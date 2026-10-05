# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'smartlight.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QSlider, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1020, 751)
        MainWindow.setMinimumSize(QSize(1020, 680))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_4 = QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.video_label = QLabel(self.centralwidget)
        self.video_label.setObjectName(u"video_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.video_label.sizePolicy().hasHeightForWidth())
        self.video_label.setSizePolicy(sizePolicy)
        self.video_label.setMaximumSize(QSize(8000000, 16777215))
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.video_label, 0, 0, 1, 1)

        self.right_v = QVBoxLayout()
        self.right_v.setSpacing(8)
        self.right_v.setObjectName(u"right_v")
        self.conn_grp = QGroupBox(self.centralwidget)
        self.conn_grp.setObjectName(u"conn_grp")
        self.conn_v = QVBoxLayout(self.conn_grp)
        self.conn_v.setObjectName(u"conn_v")
        self.port_h = QHBoxLayout()
        self.port_h.setObjectName(u"port_h")
        self.port_label = QLabel(self.conn_grp)
        self.port_label.setObjectName(u"port_label")

        self.port_h.addWidget(self.port_label)

        self.port_combo = QComboBox(self.conn_grp)
        self.port_combo.setObjectName(u"port_combo")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.port_combo.sizePolicy().hasHeightForWidth())
        self.port_combo.setSizePolicy(sizePolicy1)

        self.port_h.addWidget(self.port_combo)

        self.btn_refresh = QPushButton(self.conn_grp)
        self.btn_refresh.setObjectName(u"btn_refresh")

        self.port_h.addWidget(self.btn_refresh)


        self.conn_v.addLayout(self.port_h)

        self.btn_connect = QPushButton(self.conn_grp)
        self.btn_connect.setObjectName(u"btn_connect")

        self.conn_v.addWidget(self.btn_connect)

        self.conn_status = QLabel(self.conn_grp)
        self.conn_status.setObjectName(u"conn_status")

        self.conn_v.addWidget(self.conn_status)


        self.right_v.addWidget(self.conn_grp)

        self.cam_grp = QGroupBox(self.centralwidget)
        self.cam_grp.setObjectName(u"cam_grp")
        self.cam_v = QVBoxLayout(self.cam_grp)
        self.cam_v.setObjectName(u"cam_v")
        self.cam_h = QHBoxLayout()
        self.cam_h.setObjectName(u"cam_h")
        self.cam_combo = QComboBox(self.cam_grp)
        self.cam_combo.addItem("")
        self.cam_combo.addItem("")
        self.cam_combo.addItem("")
        self.cam_combo.addItem("")
        self.cam_combo.setObjectName(u"cam_combo")
        sizePolicy1.setHeightForWidth(self.cam_combo.sizePolicy().hasHeightForWidth())
        self.cam_combo.setSizePolicy(sizePolicy1)

        self.cam_h.addWidget(self.cam_combo)

        self.btn_cam = QPushButton(self.cam_grp)
        self.btn_cam.setObjectName(u"btn_cam")

        self.cam_h.addWidget(self.btn_cam)


        self.cam_v.addLayout(self.cam_h)


        self.right_v.addWidget(self.cam_grp)

        self.led_grp = QGroupBox(self.centralwidget)
        self.led_grp.setObjectName(u"led_grp")
        self.led_h = QHBoxLayout(self.led_grp)
        self.led_h.setSpacing(6)
        self.led_h.setObjectName(u"led_h")
        self.ind_left = QLabel(self.led_grp)
        self.ind_left.setObjectName(u"ind_left")
        self.ind_left.setMinimumSize(QSize(100, 50))
        self.ind_left.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.led_h.addWidget(self.ind_left)

        self.ind_mid = QLabel(self.led_grp)
        self.ind_mid.setObjectName(u"ind_mid")
        self.ind_mid.setMinimumSize(QSize(100, 50))
        self.ind_mid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.led_h.addWidget(self.ind_mid)

        self.ind_right = QLabel(self.led_grp)
        self.ind_right.setObjectName(u"ind_right")
        self.ind_right.setMinimumSize(QSize(100, 50))
        self.ind_right.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.led_h.addWidget(self.ind_right)


        self.right_v.addWidget(self.led_grp)

        self.manual_grp = QGroupBox(self.centralwidget)
        self.manual_grp.setObjectName(u"manual_grp")
        self.manual_g = QGridLayout(self.manual_grp)
        self.manual_g.setSpacing(5)
        self.manual_g.setObjectName(u"manual_g")
        self.btn_left_on = QPushButton(self.manual_grp)
        self.btn_left_on.setObjectName(u"btn_left_on")
        self.btn_left_on.setEnabled(False)

        self.manual_g.addWidget(self.btn_left_on, 0, 0, 1, 1)

        self.btn_left_off = QPushButton(self.manual_grp)
        self.btn_left_off.setObjectName(u"btn_left_off")
        self.btn_left_off.setEnabled(False)

        self.manual_g.addWidget(self.btn_left_off, 0, 1, 1, 1)

        self.btn_mid_on = QPushButton(self.manual_grp)
        self.btn_mid_on.setObjectName(u"btn_mid_on")
        self.btn_mid_on.setEnabled(False)

        self.manual_g.addWidget(self.btn_mid_on, 1, 0, 1, 1)

        self.btn_mid_off = QPushButton(self.manual_grp)
        self.btn_mid_off.setObjectName(u"btn_mid_off")
        self.btn_mid_off.setEnabled(False)

        self.manual_g.addWidget(self.btn_mid_off, 1, 1, 1, 1)

        self.btn_right_on = QPushButton(self.manual_grp)
        self.btn_right_on.setObjectName(u"btn_right_on")
        self.btn_right_on.setEnabled(False)

        self.manual_g.addWidget(self.btn_right_on, 2, 0, 1, 1)

        self.btn_right_off = QPushButton(self.manual_grp)
        self.btn_right_off.setObjectName(u"btn_right_off")
        self.btn_right_off.setEnabled(False)

        self.manual_g.addWidget(self.btn_right_off, 2, 1, 1, 1)

        self.btn_all_on = QPushButton(self.manual_grp)
        self.btn_all_on.setObjectName(u"btn_all_on")
        self.btn_all_on.setEnabled(False)

        self.manual_g.addWidget(self.btn_all_on, 3, 0, 1, 1)

        self.btn_all_off = QPushButton(self.manual_grp)
        self.btn_all_off.setObjectName(u"btn_all_off")
        self.btn_all_off.setEnabled(False)

        self.manual_g.addWidget(self.btn_all_off, 3, 1, 1, 1)


        self.right_v.addWidget(self.manual_grp)

        self.auto_grp = QGroupBox(self.centralwidget)
        self.auto_grp.setObjectName(u"auto_grp")
        self.auto_v = QVBoxLayout(self.auto_grp)
        self.auto_v.setObjectName(u"auto_v")
        self.thr_h = QHBoxLayout()
        self.thr_h.setObjectName(u"thr_h")
        self.thr_label = QLabel(self.auto_grp)
        self.thr_label.setObjectName(u"thr_label")

        self.thr_h.addWidget(self.thr_label)

        self.thr_slider = QSlider(self.auto_grp)
        self.thr_slider.setObjectName(u"thr_slider")
        sizePolicy1.setHeightForWidth(self.thr_slider.sizePolicy().hasHeightForWidth())
        self.thr_slider.setSizePolicy(sizePolicy1)
        self.thr_slider.setMinimum(5)
        self.thr_slider.setMaximum(60)
        self.thr_slider.setValue(15)
        self.thr_slider.setOrientation(Qt.Orientation.Horizontal)

        self.thr_h.addWidget(self.thr_slider)

        self.thr_val_lbl = QLabel(self.auto_grp)
        self.thr_val_lbl.setObjectName(u"thr_val_lbl")

        self.thr_h.addWidget(self.thr_val_lbl)


        self.auto_v.addLayout(self.thr_h)

        self.btn_auto = QPushButton(self.auto_grp)
        self.btn_auto.setObjectName(u"btn_auto")
        self.btn_auto.setEnabled(False)
        self.btn_auto.setCheckable(True)

        self.auto_v.addWidget(self.btn_auto)

        self.dec_h = QHBoxLayout()
        self.dec_h.setObjectName(u"dec_h")
        self.dec_left = QLabel(self.auto_grp)
        self.dec_left.setObjectName(u"dec_left")
        self.dec_left.setMinimumSize(QSize(80, 44))
        self.dec_left.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dec_h.addWidget(self.dec_left)

        self.dec_mid = QLabel(self.auto_grp)
        self.dec_mid.setObjectName(u"dec_mid")
        self.dec_mid.setMinimumSize(QSize(80, 44))
        self.dec_mid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dec_h.addWidget(self.dec_mid)

        self.dec_right = QLabel(self.auto_grp)
        self.dec_right.setObjectName(u"dec_right")
        self.dec_right.setMinimumSize(QSize(80, 44))
        self.dec_right.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dec_h.addWidget(self.dec_right)


        self.auto_v.addLayout(self.dec_h)


        self.right_v.addWidget(self.auto_grp)

        self.log_grp = QGroupBox(self.centralwidget)
        self.log_grp.setObjectName(u"log_grp")
        self.log_v = QVBoxLayout(self.log_grp)
        self.log_v.setObjectName(u"log_v")
        self.log_label = QLabel(self.log_grp)
        self.log_label.setObjectName(u"log_label")
        self.log_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.log_label.setWordWrap(True)

        self.log_v.addWidget(self.log_label)


        self.right_v.addWidget(self.log_grp)


        self.gridLayout_3.addLayout(self.right_v, 0, 1, 2, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy2)
        self.groupBox.setMinimumSize(QSize(391, 115))
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)

        self.horizontalSlider_2 = QSlider(self.groupBox)
        self.horizontalSlider_2.setObjectName(u"horizontalSlider_2")
        self.horizontalSlider_2.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.horizontalSlider_2, 1, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 2)

        self.horizontalSlider_3 = QSlider(self.groupBox)
        self.horizontalSlider_3.setObjectName(u"horizontalSlider_3")
        self.horizontalSlider_3.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.horizontalSlider_3, 2, 2, 1, 1)

        self.horizontalSlider = QSlider(self.groupBox)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.horizontalSlider, 0, 2, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.bright_grp = QGroupBox(self.centralwidget)
        self.bright_grp.setObjectName(u"bright_grp")
        self.bright_grid = QGridLayout(self.bright_grp)
        self.bright_grid.setSpacing(4)
        self.bright_grid.setObjectName(u"bright_grid")
        self.bright_name_left = QLabel(self.bright_grp)
        self.bright_name_left.setObjectName(u"bright_name_left")

        self.bright_grid.addWidget(self.bright_name_left, 0, 0, 1, 1)

        self.bright_bar_left = QLabel(self.bright_grp)
        self.bright_bar_left.setObjectName(u"bright_bar_left")
        self.bright_bar_left.setProperty(u"fixedHeight", 14)

        self.bright_grid.addWidget(self.bright_bar_left, 0, 1, 1, 1)

        self.bright_val_left = QLabel(self.bright_grp)
        self.bright_val_left.setObjectName(u"bright_val_left")
        self.bright_val_left.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.bright_grid.addWidget(self.bright_val_left, 0, 2, 1, 1)

        self.bright_name_mid = QLabel(self.bright_grp)
        self.bright_name_mid.setObjectName(u"bright_name_mid")

        self.bright_grid.addWidget(self.bright_name_mid, 1, 0, 1, 1)

        self.bright_bar_mid = QLabel(self.bright_grp)
        self.bright_bar_mid.setObjectName(u"bright_bar_mid")
        self.bright_bar_mid.setProperty(u"fixedHeight", 14)

        self.bright_grid.addWidget(self.bright_bar_mid, 1, 1, 1, 1)

        self.bright_val_mid = QLabel(self.bright_grp)
        self.bright_val_mid.setObjectName(u"bright_val_mid")
        self.bright_val_mid.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.bright_grid.addWidget(self.bright_val_mid, 1, 2, 1, 1)

        self.bright_name_right = QLabel(self.bright_grp)
        self.bright_name_right.setObjectName(u"bright_name_right")

        self.bright_grid.addWidget(self.bright_name_right, 2, 0, 1, 1)

        self.bright_bar_right = QLabel(self.bright_grp)
        self.bright_bar_right.setObjectName(u"bright_bar_right")
        self.bright_bar_right.setProperty(u"fixedHeight", 14)

        self.bright_grid.addWidget(self.bright_bar_right, 2, 1, 1, 1)

        self.bright_val_right = QLabel(self.bright_grp)
        self.bright_val_right.setObjectName(u"bright_val_right")
        self.bright_val_right.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.bright_grid.addWidget(self.bright_val_right, 2, 2, 1, 1)


        self.verticalLayout.addWidget(self.bright_grp)


        self.gridLayout_3.addLayout(self.verticalLayout, 1, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"SmartLight V2 \u2014 \u81ea\u9002\u5e94\u9632\u9634\u5f71\u7167\u660e", None))
        self.video_label.setText(QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934\u672a\u5f00\u542f", None))
        self.conn_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u4e32\u53e3\u8fde\u63a5", None))
        self.port_label.setText(QCoreApplication.translate("MainWindow", u"\u4e32\u53e3:", None))
        self.btn_refresh.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.btn_connect.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5", None))
        self.conn_status.setText(QCoreApplication.translate("MainWindow", u"\u25cf \u672a\u8fde\u63a5", None))
        self.cam_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934", None))
        self.cam_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934 0", None))
        self.cam_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934 1", None))
        self.cam_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934 2", None))
        self.cam_combo.setItemText(3, QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934 3", None))

        self.btn_cam.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u542f", None))
        self.led_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u706f\u5e26\u72b6\u6001", None))
        self.ind_left.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">LEFT</span></p><p><span style=\" font-size:10pt;\">\u25cb OFF</span></p></body></html>", None))
        self.ind_mid.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">MID</span></p><p><span style=\" font-size:10pt;\">\u25cb OFF</span></p></body></html>", None))
        self.ind_right.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">RIGHT</span></p><p><span style=\" font-size:10pt;\">\u25cb OFF</span></p></body></html>", None))
        self.manual_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
        self.btn_left_on.setText(QCoreApplication.translate("MainWindow", u"LEFT  ON", None))
        self.btn_left_off.setText(QCoreApplication.translate("MainWindow", u"LEFT  OFF", None))
        self.btn_mid_on.setText(QCoreApplication.translate("MainWindow", u"MID   ON", None))
        self.btn_mid_off.setText(QCoreApplication.translate("MainWindow", u"MID   OFF", None))
        self.btn_right_on.setText(QCoreApplication.translate("MainWindow", u"RIGHT ON", None))
        self.btn_right_off.setText(QCoreApplication.translate("MainWindow", u"RIGHT OFF", None))
        self.btn_all_on.setText(QCoreApplication.translate("MainWindow", u"ALL   ON", None))
        self.btn_all_off.setText(QCoreApplication.translate("MainWindow", u"ALL   OFF", None))
        self.auto_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u89c6\u89c9\u81ea\u52a8\u6a21\u5f0f", None))
        self.thr_label.setText(QCoreApplication.translate("MainWindow", u"\u9608\u503c:", None))
        self.thr_val_lbl.setText(QCoreApplication.translate("MainWindow", u"15", None))
        self.btn_auto.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8\u81ea\u52a8\u8865\u5149", None))
        self.dec_left.setText(QCoreApplication.translate("MainWindow", u"LEFT\n"
"\u2014", None))
        self.dec_mid.setText(QCoreApplication.translate("MainWindow", u"MID\n"
"\u2014", None))
        self.dec_right.setText(QCoreApplication.translate("MainWindow", u"RIGHT\n"
"\u2014", None))
        self.log_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u4e32\u53e3\u65e5\u5fd7", None))
        self.log_label.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u6444\u50cf\u5934", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u6c34\u5e73\u504f\u79fb", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u5782\u76f4\u504f\u79fb", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">\u7f29\u653e</p></body></html>", None))
        self.bright_grp.setTitle(QCoreApplication.translate("MainWindow", u"\u5404\u533a\u4eae\u5ea6", None))
        self.bright_name_left.setText(QCoreApplication.translate("MainWindow", u"LEFT", None))
        self.bright_bar_left.setText("")
        self.bright_val_left.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.bright_name_mid.setText(QCoreApplication.translate("MainWindow", u"MID", None))
        self.bright_bar_mid.setText("")
        self.bright_val_mid.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.bright_name_right.setText(QCoreApplication.translate("MainWindow", u"RIGHT", None))
        self.bright_bar_right.setText("")
        self.bright_val_right.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
    # retranslateUi

