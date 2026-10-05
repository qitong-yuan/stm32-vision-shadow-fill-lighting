import sys
import time
import cv2
import numpy as np
import serial
import serial.tools.list_ports

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore    import Qt, QTimer, QThread, Signal
from PySide6.QtGui     import QImage, QPixmap, QFont

from Ui_smartlight import Ui_MainWindow


MIN_BLOB_AREA    = 120    # 物体/阴影连通块最小像素，小于此视为噪点
# ── 渐变闭环调
# 光参数 ──
# 每帧亮度变化步长（百分比/帧，约 30ms/帧）：
RAMP_UP   = 3.0    # 变亮速度（检测到阴影时，平滑升到压住阴影）
# 熄灭要慢，否则一闪一闪伤眼。0.6%/帧 → 从100%降到0约需5秒，柔和淡出。
RAMP_DOWN = 0.6
# 连续多少帧"阴影已消除"才开始调暗。约 30ms/帧，40帧≈1.2s。
# 压住阴影后先稳一段，避免刚补好就回降造成的拉锯/呼吸。
CLEAR_FRAMES = 40
# 发给下位机的百分比量化步长：只有跨过整步才发命令，避免每帧刷串口。
LEVEL_STEP = 5
# 目标亮度上限（防止补到刺眼/过曝）。需要时可调高。
LEVEL_MAX = 100
# 启动后拍"全灭基准"前的稳定等待（秒）。
SETTLE_SECONDS = 0.8

# ROI 缩放滑条(0~99) → ROI 占整幅画面的比例。
ROI_MAX_RATIO  = 1.0
ROI_MIN_RATIO  = 0.30


#串口读取
class SerialReadThread(QThread):
    ack_received = Signal(str) #收到应答就发信号给主线程

    def __init__(self, ser: serial.Serial):
        super().__init__()
        self._ser     = ser
        self._running = True

    def run(self):
        buf = b""
        while self._running:
            try:
                if self._ser and self._ser.is_open and self._ser.in_waiting:
                    buf += self._ser.read(self._ser.in_waiting)
                    while b"\n" in buf:#按行切分
                        line, buf = buf.split(b"\n", 1)
                        text = line.decode("ascii", errors="ignore").strip()
                        if text:
                            self.ack_received.emit(text)
                self.msleep(10)
            except Exception:
                self.msleep(50)

    def stop(self):
        self._running = False
        self.wait()


#主窗口
class SmartLightApp(QMainWindow):

    DEFAULT_THRESHOLD = 15

    # 命令发送最小间隔（ms）。下位机处理一条命令需 ~10ms(Delay) + 发ACK，
    # 留足余量取 80ms，保证连发时每条都被完整处理，不会相互覆盖。
    SEND_INTERVAL_MS = 80

    ACK_MAP = {
        "ACK:LEFT_ON":  (0, True),  "ACK:LEFT_OFF":  (0, False),
        "ACK:MID_ON":   (1, True),  "ACK:MID_OFF":   (1, False),
        "ACK:RIGHT_ON": (2, True),  "ACK:RIGHT_OFF": (2, False),
    }

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ── 串口 / 摄像头 ────────────────────────────────────────
        self._ser:         serial.Serial | None    = None
        self._read_thread: SerialReadThread | None = None
        self._cap:         cv2.VideoCapture | None = None

        # ── 基础状态 ─────────────────────────────────────────────
        self._threshold  = self.DEFAULT_THRESHOLD
        self._auto_mode  = False
        self._zone_state = [False, False, False]
        self._zone_pct   = [0, 0, 0]   # 各区当前亮度百分比（指示灯显示用）
        self._log_lines: list[str] = []

        # ── 局部阴影检测 + 渐变调光 ────────────────────────────
        # 基准灰度图（全灭时拍的整张 ROI 灰度图），逐像素比对找阴影
        self._baseline_gray = None
        self._last_gray     = None   # 主循环最新灰度，供拍基准避免抢帧
        self._baseline_ready: bool = False
        self._state_since   = 0.0    # 自动启动时刻（用于等待拍基准）
        # 每个区当前亮度百分比（0~100，浮点，逐帧渐变）
        self._level:      list[float] = [0.0, 0.0, 0.0]
        # 已发给下位机的量化百分比（去重用，-1=未发过）
        self._sent_level: list[int]   = [-1, -1, -1]
        # 各区"连续看不到阴影"的帧数（达到 CLEAR_FRAMES 才开始调暗）
        self._clear_cnt:  list[int]   = [0, 0, 0]

        # ── ROI 状态（缩放/水平/垂直，均为 0~99 的滑条值）────────
        self._roi_zoom = 0    # 0=最大框
        self._roi_dx   = 50   # 50=水平居中
        self._roi_dy   = 50   # 50=垂直居中

        # 画面水平镜像（摄像头左右与灯带物理位置相反，故默认开启）
        self._mirror = True

        # ── 命令发送队列（关键：防止连发命令在下位机被覆盖丢失）──
        # 下位机串口中断每收完一条命令置 uart_cmd_ready=1，主循环要
        # 调用 Process_Command（内含 Delay_ms + 发 ACK）才处理完。
        # 若上位机在它处理完前连发下一条，下位机 buffer 会被新命令的
        # '#' 清零覆盖，中间那条（最常是 MID）就丢了。
        # 解法：所有命令进队列，定时器每 SEND_INTERVAL_MS 只发一条。
        self._cmd_queue: list[str] = []
        self._send_timer = QTimer()
        self._send_timer.setInterval(self.SEND_INTERVAL_MS)
        self._send_timer.timeout.connect(self._flush_one_cmd)
        self._send_timer.start()

        # ── 指示块字体 ───────────────────────────────────────────
        ind_font = QFont("Consolas", 11, QFont.Weight.Bold)
        for w in (self.ui.ind_left, self.ui.ind_mid, self.ui.ind_right):
            w.setFont(ind_font)

        # ── ROI 滑条初始化（UI 里没设范围，这里用代码设好）──────
        self._init_roi_sliders()

        # ── 摄像头定时器 ─────────────────────────────────────────
        self._cam_timer = QTimer()
        self._cam_timer.timeout.connect(self._update_frame)

        self._bind_signals()
        self._refresh_ports()
        self._refresh_zone_indicators()


    #ROI 滑条初始化
    def _init_roi_sliders(self):
        # 缩放：0~99，初值 0（整幅）
        self.ui.horizontalSlider.setMinimum(0)
        self.ui.horizontalSlider.setMaximum(99)
        self.ui.horizontalSlider.setValue(0)
        # 水平偏移：0~99，初值 50（居中）
        self.ui.horizontalSlider_2.setMinimum(0)
        self.ui.horizontalSlider_2.setMaximum(99)
        self.ui.horizontalSlider_2.setValue(50)
        # 垂直偏移：0~99，初值 50（居中）
        self.ui.horizontalSlider_3.setMinimum(0)
        self.ui.horizontalSlider_3.setMaximum(99)
        self.ui.horizontalSlider_3.setValue(50)

    #信号绑定
    def _bind_signals(self):
        u = self.ui
        u.btn_refresh.clicked.connect(self._refresh_ports)
        u.btn_connect.clicked.connect(self._toggle_connect)
        u.btn_cam.clicked.connect(self._toggle_camera)
        u.btn_left_on.clicked.connect(lambda: self._send_zone("LEFT",  True))
        u.btn_left_off.clicked.connect(lambda: self._send_zone("LEFT",  False))
        u.btn_mid_on.clicked.connect(lambda: self._send_zone("MID",   True))
        u.btn_mid_off.clicked.connect(lambda: self._send_zone("MID",   False))
        u.btn_right_on.clicked.connect(lambda: self._send_zone("RIGHT", True))
        u.btn_right_off.clicked.connect(lambda: self._send_zone("RIGHT", False))
        u.btn_all_on.clicked.connect(self._send_all_on)
        u.btn_all_off.clicked.connect(self._send_all_off)
        u.btn_auto.clicked.connect(self._toggle_auto)
        u.thr_slider.valueChanged.connect(self._on_threshold_change)

        # ROI 三滑条
        u.horizontalSlider.valueChanged.connect(self._on_roi_zoom)
        u.horizontalSlider_2.valueChanged.connect(self._on_roi_dx)
        u.horizontalSlider_3.valueChanged.connect(self._on_roi_dy)

    #ROI 滑条回调
    def _on_roi_zoom(self, val: int):
        self._roi_zoom = val
        # ROI 改变后，已采集的基准失效，需要在自动模式下重新采集
        self._invalidate_baseline_if_auto()

    def _on_roi_dx(self, val: int):
        self._roi_dx = val
        self._invalidate_baseline_if_auto()

    def _on_roi_dy(self, val: int):
        self._roi_dy = val
        self._invalidate_baseline_if_auto()

    def _invalidate_baseline_if_auto(self):
        #ROI 变了，基准按旧框拍的已失效，就全部归零、重新拍基准。
        if self._auto_mode:
            self._send_raw("#OFF*")
            self._level          = [0.0, 0.0, 0.0]
            self._sent_level     = [-1, -1, -1]
            self._state_since    = time.monotonic()
            self._baseline_ready = False

    #把滑条值换算成像素矩形 (x, y, w, h)
    def _compute_roi(self, frame_w: int, frame_h: int):
        # 缩放：滑条 0→最大框，99→最小框
        t = self._roi_zoom / 99.0
        ratio = ROI_MAX_RATIO + (ROI_MIN_RATIO - ROI_MAX_RATIO) * t

        roi_w = int(frame_w * ratio)
        roi_h = int(frame_h * ratio)
        roi_w = max(roi_w, 40)  
        roi_h = max(roi_h, 40)

        # 偏移：滑条 50=居中，可移动的范围是框外剩余空间
        free_x = frame_w - roi_w
        free_y = frame_h - roi_h
        x = int(free_x * (self._roi_dx / 99.0))
        y = int(free_y * (self._roi_dy / 99.0))

        # 夹紧到画面内
        x = max(0, min(x, frame_w - roi_w))
        y = max(0, min(y, frame_h - roi_h))
        return x, y, roi_w, roi_h

    #串口
    def _refresh_ports(self):
        self.ui.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.ui.port_combo.addItem(p.device, p.device)
        if not ports:
            self.ui.port_combo.addItem("（无可用串口）")

    def _toggle_connect(self):
        if self._ser and self._ser.is_open:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port = self.ui.port_combo.currentData()
        if not port:
            self._log("串口未选择")
            return
        try:
            self._ser = serial.Serial(port, 115200, timeout=0)
            self._read_thread = SerialReadThread(self._ser)
            self._read_thread.ack_received.connect(self._on_ack)
            self._read_thread.start()
            self.ui.conn_status.setText(f"● 已连接 {port}")
            self.ui.btn_connect.setText("断开")
            self._set_manual_btns_enabled(True)
            self._update_auto_btn_state()
            self._log(f"已连接 {port} @ 115200")
        except Exception as e:
            self._log(f"连接失败: {e}")

    def _disconnect(self):
        if self._read_thread:
            self._read_thread.stop()
            self._read_thread = None
        if self._ser:
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None
        self._cmd_queue.clear()
        self.ui.conn_status.setText("● 未连接")
        self.ui.btn_connect.setText("连接")
        self._set_manual_btns_enabled(False)
        self.ui.btn_auto.setEnabled(False)
        self.ui.btn_auto.setChecked(False)
        self._auto_mode = False
        self._log("已断开串口")

    def _send_raw(self, cmd: str):
        """
        不直接写串口，而是进入发送队列。由定时器每一段时间取一条发送
        避免连发命令在下位机被覆盖。
        类似于抖动修正，判断尾巴，如果一样就不要。
        """
        if not self._ser or not self._ser.is_open:
            return
        if self._cmd_queue and self._cmd_queue[-1] == cmd:
            return
        self._cmd_queue.append(cmd)

    def _flush_one_cmd(self):
        """定时发送"""
        if not self._cmd_queue:
            return
        if not self._ser or not self._ser.is_open:
            self._cmd_queue.clear()
            return
        cmd = self._cmd_queue.pop(0)
        try:
            self._ser.write(cmd.encode("ascii"))
            self._log(f"发送 → {cmd.strip()}")
        except Exception as e:
            self._log(f"发送失败: {e}")

    def _on_ack(self, line: str):
        self._log(f"收到 ← {line}")
        # 新格式：ACK:L075 / ACK:M050 / ACK:R100（百分比调光）
        if (len(line) == 8 and line.startswith("ACK:")
                and line[4] in "LMR" and line[5:8].isdigit()):
            idx = {"L": 0, "M": 1, "R": 2}[line[4]]
            pct = int(line[5:8])
            self._zone_state[idx] = pct > 0
            self._zone_pct[idx]   = pct
            self._refresh_zone_indicators() #刷新区域指示器
            return
        # 旧格式：兼容手动按钮
        if line in self.ACK_MAP:
            idx, state = self.ACK_MAP[line]
            self._zone_state[idx] = state
            self._zone_pct[idx]   = 100 if state else 0
            self._refresh_zone_indicators()
        elif line == "ACK:ALL_ON":
            self._zone_state = [True, True, True]
            self._zone_pct   = [100, 100, 100]
            self._refresh_zone_indicators()
        elif line == "ACK:ALL_OFF":
            self._zone_state = [False, False, False]
            self._zone_pct   = [0, 0, 0]
            self._refresh_zone_indicators()

    def _send_zone(self, zone: str, on: bool):
        #左中右区域
        self._send_raw(f"#{zone}{'ON' if on else 'OFF'}*")

    def _send_all_on(self):
        self._send_raw("#ALL*")

    def _send_all_off(self):
        self._send_raw("#OFF*")

    #摄像头
    def _toggle_camera(self):
        if self._cap and self._cap.isOpened():
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        idx = self.ui.cam_combo.currentIndex()
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            self._log(f"摄像头 {idx} 打开失败")
            return
        self._cap = cap
        self._cam_timer.start(30)
        self.ui.btn_cam.setText("关闭")
        self._update_auto_btn_state()
        self._log(f"摄像头 {idx} 已开启")

    def _stop_camera(self):
        self._cam_timer.stop()
        if self._cap:
            self._cap.release()
            self._cap = None
        self.ui.video_label.setText("摄像头未开启")
        self.ui.btn_cam.setText("开启")
        self.ui.btn_auto.setEnabled(False)
        self.ui.btn_auto.setChecked(False)
        self._auto_mode = False
        self._log("摄像头已关闭")

    #视觉主循环
    def _update_frame(self):
        if not self._cap or not self._cap.isOpened():
            return
        ret, frame = self._cap.read()
        if not ret:
            return

        """
        水平镜像翻转
        因为摄像头倒着放，视角与灯带物理左右相反
        水平翻转后，画面左 = 实际左
        若以后摄像头摆正了，把self._mirror设为False即可。
        """
        if self._mirror:
            frame = cv2.flip(frame, 1)   # 1 = 水平翻转

        H, W = frame.shape[:2]

        rx, ry, rw, rh = self._compute_roi(W, H)    #计算 ROI 矩形
        roi = frame[ry:ry+rh, rx:rx+rw]    #只分析ROI区域

        gray    = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)    #灰度
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)    #去噪
        self._last_gray = blurred   #作为基准快照

        w3 = rw // 3

        #物体 + 阴影方向检测
        result = self._detect_shadow(blurred, rw, rh, w3)

        # 信息显示
        self._update_shadow_bars(result)

        #按阴影方向调光
        if self._auto_mode:
            want_on = self._auto_step(result)
        else:
            want_on = self._preview_decision(result)

        self._update_decision_labels(want_on)

        # 可视化叠加
        frame = self._draw_overlay(frame, W, H, rx, ry, rw, rh, result, want_on)

        #显示
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rh2, rw2, ch = rgb.shape
        qt_img = QImage(rgb.data, rw2, rh2, ch * rw2, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(
            self.ui.video_label.width(),
            self.ui.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.ui.video_label.setPixmap(pix)

    #物体 + 阴影分离检测
    def _detect_shadow(self, gray, rw, rh, w3):
        empty = dict(has_obj=False, has_shadow=False, side=None,
                     depth=0.0, obj_mask=None, shadow_mask=None)
        if (not self._baseline_ready or self._baseline_gray is None
                or self._baseline_gray.shape != gray.shape):
            return empty

        shadow_dark = self._threshold     #阈值：比基准暗多少才算“暗”

        #基准值-当前值
        diff = self._baseline_gray.astype(np.int16) - gray.astype(np.int16)#防止溢出
        diff = np.clip(diff, 0, 255).astype(np.uint8)

        # 第一步：超过阈值的判为"变暗区"（物体+阴影都在里面）
        _, all_dark = cv2.threshold(diff, shadow_dark, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        all_dark = cv2.morphologyEx(all_dark, cv2.MORPH_OPEN, kernel)   #去噪点

        dark_vals = diff[all_dark > 0]
        if dark_vals.size < MIN_BLOB_AREA: ##变暗太少就当作没有物体
            return empty

        # 第二步：自适应分层（物体优先）。
        # 在"变暗区"用Otsu自动找一个暗度分界split
        split, _ = cv2.threshold(dark_vals, 0, 255,
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        split = max(split, shadow_dark + 12)# 保护：split 至少比 shadow_dark 高一截


        # 暗度 ≥ split就是物体本体，反之阴影
        _, obj_mask = cv2.threshold(diff, split, 255, cv2.THRESH_BINARY)
        obj_mask    = cv2.morphologyEx(obj_mask, cv2.MORPH_OPEN, kernel)
        shadow_mask = cv2.subtract(all_dark, obj_mask)
        shadow_mask = cv2.morphologyEx(shadow_mask, cv2.MORPH_OPEN, kernel)

        obj_cx, obj_cy, obj_area, obj_w, obj_h = self._largest_blob_cx(obj_mask)
        shadow_cx, shadow_cy, shadow_area, _, _ = self._largest_blob_cx(shadow_mask)

        has_obj    = obj_area    >= MIN_BLOB_AREA
        has_shadow = shadow_area >= MIN_BLOB_AREA

        sides = set()      # 需要补光的分区L/M/R
        depth = 0.0
        if has_shadow:
            depth = float(np.mean(diff[shadow_mask > 0]))
        if has_obj and has_shadow:
            cx = int(round(obj_cx))
            cy = int(round(obj_cy))
            ys, xs = np.nonzero(shadow_mask)
            total = len(xs)
            if total > 0:
                left_r  = np.count_nonzero(xs < cx) / total #阴影像素中，左侧占比
                right_r = np.count_nonzero(xs > cx) / total #阴影像素中，右侧占比
                up_r    = np.count_nonzero(ys < cy) / total #阴影像素中，上方占比
                if up_r >= 0.55:
                    sides.add('M')  # 上方→中区横灯
                if up_r < 0.70:     #过于靠下的阴影不算环绕，才按左右分区。过于靠上的阴影不算环绕，才按左右分区。
                    if left_r  >= 0.45: sides.add('L')
                    if right_r >= 0.45: sides.add('R')
                if not sides:
                    sides.add('R' if right_r >= left_r else 'L')
        elif has_shadow and not has_obj:# 没识别到物体：用阴影相对画面中心定方向
            if shadow_cx < rw * 0.4: sides.add('L')
            elif shadow_cx > rw * 0.6: sides.add('R')
            else: sides.add('M')

        return dict(has_obj=has_obj, has_shadow=has_shadow, sides=sides,
                    depth=depth, obj_mask=obj_mask, shadow_mask=shadow_mask)

    def _largest_blob_cx(self, mask):
        #返回最大连通块的 (质心x, 质心y, 面积, 宽, 高)。无则全0。
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.0, 0.0, 0, 0, 0
        c = max(contours, key=cv2.contourArea)  #找最大连通块
        area = cv2.contourArea(c)
        if area < 1:
            return 0.0, 0.0, 0, 0, 0
        x, y, w, h = cv2.boundingRect(c)
        M = cv2.moments(c)  #计算矩，求质心
        cx = M["m10"] / M["m00"] if M["m00"] else x + w / 2
        cy = M["m01"] / M["m00"] if M["m00"] else y + h / 2
        return cx, cy, area, w, h

    #渐变方向调光（按阴影相对物体的方向）
    def _preview_decision(self, result) -> list[bool]:
        #非自动 / 基准未就绪：纯展示，标出需要补光的方向。
        return self._zones_to_fill(result)

    def _zones_to_fill(self, result):    #看看左中右要不要补光
        need = [False, False, False]
        if not result["has_shadow"]:
            return need
        sides = result["sides"]
        if 'L' in sides: need[0] = True
        if 'M' in sides: need[1] = True
        if 'R' in sides: need[2] = True
        return need

    def _auto_step(self, result):   #每帧调用
        now = time.monotonic()
        # 先判断基准好了没，好了就过几秒，等稳定了再执行动作
        if not self._baseline_ready:
            if now - self._state_since >= SETTLE_SECONDS and self._last_gray is not None:
                self._baseline_gray  = self._last_gray.copy()   #全灭基准
                self._baseline_ready = True
                self._log("基准已采集，开始调光")
            return [lv > 0 for lv in self._level]

        need = self._zones_to_fill(result)
        for i in range(3):
            if need[i]: #要就快快亮
                self._level[i] = min(float(LEVEL_MAX), self._level[i] + RAMP_UP)
                self._clear_cnt[i] = 0
            else:   #不要了就慢慢暗
                self._clear_cnt[i] += 1
                if self._clear_cnt[i] >= CLEAR_FRAMES:
                    self._level[i] = max(0.0, self._level[i] - RAMP_DOWN)
            self._push_level(i) #把第 i 区的目标亮度发给下位机

        return [lv > 0 for lv in self._level]

    def _push_level(self, i: int):
        # 量化到 LEVEL_STEP 的整数倍，避免每帧都发微小变化的命令。
        q = int(round(self._level[i] / LEVEL_STEP) * LEVEL_STEP)
        q = max(0, min(100, q))
        if q != self._sent_level[i]:    #只有跨过量化步长才发命令
            self._sent_level[i] = q
            zone_ch = ["L", "M", "R"][i]
            self._send_raw(f"#{zone_ch}{q:03d}*")

    def _reset_algo_state(self):
        self._state_since    = time.monotonic()
        self._level          = [0.0, 0.0, 0.0]
        self._sent_level     = [-1, -1, -1]
        self._clear_cnt      = [0, 0, 0]
        self._baseline_ready = False
        self._baseline_gray  = None

    #UI 更新
    def _update_shadow_bars(self, result):
        sides = result.get("sides", set())
        txt = "".join(s for s in ("L", "M", "R") if s in sides) or "-"
        self.ui.bright_val_left.setText(txt)
        self.ui.bright_val_mid.setText(f"{result['depth']:.0f}")
        self.ui.bright_val_right.setText(
            "物体✓" if result["has_obj"] else "无物体")

    def _update_decision_labels(self, want_on: list[bool]):
        labels     = [self.ui.dec_left, self.ui.dec_mid, self.ui.dec_right]
        zone_names = ["LEFT", "MID", "RIGHT"]
        for i, lbl in enumerate(labels):
            lbl.setText(f"{zone_names[i]}\n{'补光' if want_on[i] else '正常'}")

    def _refresh_zone_indicators(self):
        widgets = [self.ui.ind_left, self.ui.ind_mid, self.ui.ind_right]
        names   = ["LEFT", "MID", "RIGHT"]
        for i, (w, name) in enumerate(zip(widgets, names)):
            if self._zone_state[i]:
                w.setText(f"{name}\n● {self._zone_pct[i]}%")
            else:
                w.setText(f"{name}\n○ OFF")

    def _draw_overlay(self, frame, W, H, rx, ry, rw, rh, result, want_on):
        # ROI 框外压暗
        dark = frame.copy()
        dark[:] = (dark * 0.35).astype(np.uint8)
        dark[ry:ry+rh, rx:rx+rw] = frame[ry:ry+rh, rx:rx+rw]
        frame = dark
        off = np.array([[rx, ry]])

        # ROI 边框
        cv2.rectangle(frame, (rx, ry), (rx+rw, ry+rh), (0, 200, 255), 2)

        # 阴影：黄色半透明高亮
        sm = result.get("shadow_mask")
        if sm is not None:
            cnts, _ = cv2.findContours(sm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = [c for c in cnts if cv2.contourArea(c) >= MIN_BLOB_AREA]
            shifted = [c + off for c in cnts]
            if shifted:
                fill = frame.copy()
                cv2.drawContours(fill, shifted, -1, (0, 200, 255), cv2.FILLED)
                frame = cv2.addWeighted(fill, 0.35, frame, 0.65, 0)
                cv2.drawContours(frame, shifted, -1, (0, 220, 255), 2)

        # 物体：蓝色实框
        om = result.get("obj_mask")
        if om is not None:
            cnts, _ = cv2.findContours(om, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = [c for c in cnts if cv2.contourArea(c) >= MIN_BLOB_AREA]
            if cnts:
                c = max(cnts, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (rx+x, ry+y), (rx+x+w, ry+y+h), (255, 120, 0), 2)
                cv2.putText(frame, "OBJ", (rx+x, ry+y-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 120, 0), 1)

        # 方向 + 各灯亮度文字
        font = cv2.FONT_HERSHEY_SIMPLEX
        sides = result.get("sides", set())
        names = {"L": "LEFT", "M": "MID", "R": "RIGHT"}
        if sides:
            lit = "+".join(names[s] for s in ("L", "M", "R") if s in sides)
            side_txt = f"SHADOW -> {lit} LED"
        else:
            side_txt = "NO SHADOW"
        cv2.putText(frame, side_txt, (rx+6, ry+22), font, 0.55, (0, 220, 255), 2)

        # 诊断提示：识别到物体却没识别到阴影 → 多半是阈值太高把浅阴影滤掉了
        if result["has_obj"] and not result["has_shadow"]:
            cv2.putText(frame, "obj ok, no shadow - try lower THR",
                        (rx+6, ry+42), font, 0.45, (0, 180, 255), 1)

        lv = self._level
        cv2.putText(frame, f"L:{lv[0]:.0f}% M:{lv[1]:.0f}% R:{lv[2]:.0f}%",
                    (rx+6, ry+rh-12), font, 0.55, (120, 255, 120), 2)

        mode_txt   = "AUTO" if self._auto_mode else "MANUAL"
        mode_color = (40, 200, 255) if self._auto_mode else (160, 160, 160)
        cv2.putText(frame, f"MODE:{mode_txt}  THR:{self._threshold}",
                    (8, H - 10), font, 0.5, mode_color, 1)
        return frame

    
    #自动模式
    
    def _toggle_auto(self, checked: bool):
        self._auto_mode = checked
        self.ui.btn_auto.setText("停止自动补光" if checked else "启动自动补光")
        if checked:
            self._cmd_queue.clear()   # 清掉残留命令，让 OFF 优先
            self._send_raw("#OFF*")
            self._reset_algo_state()  # 等画面稳定后自动拍基准，再开始调光
            self._log("自动模式启动，正在采集基准...")
        else:
            self._send_raw("#OFF*")
            self._reset_algo_state()
            self._log("自动模式已关闭")

    def _update_auto_btn_state(self):
        cam_ok = self._cap is not None and self._cap.isOpened()
        ser_ok = self._ser is not None and self._ser.is_open
        self.ui.btn_auto.setEnabled(cam_ok and ser_ok)

    #阈值滑条
    def _on_threshold_change(self, val: int):
        self._threshold = val
        self.ui.thr_val_lbl.setText(str(val))

    #手动按钮
    def _set_manual_btns_enabled(self, enabled: bool):
        for btn in (
            self.ui.btn_left_on,  self.ui.btn_left_off,
            self.ui.btn_mid_on,   self.ui.btn_mid_off,
            self.ui.btn_right_on, self.ui.btn_right_off,
            self.ui.btn_all_on,   self.ui.btn_all_off,
        ):
            btn.setEnabled(enabled)

    #日志
    def _log(self, msg: str):
        self._log_lines.append(msg)
        if len(self._log_lines) > 4:
            self._log_lines.pop(0)
        self.ui.log_label.setText("\n".join(self._log_lines))

    #关闭
    def closeEvent(self, event):
        self._cam_timer.stop()
        self._send_timer.stop()
        if self._cap:
            self._cap.release()
        if self._read_thread:
            self._read_thread.stop()
        if self._ser and self._ser.is_open:
            self._ser.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SmartLightApp()
    win.show()
    sys.exit(app.exec())