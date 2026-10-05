# Vision-Based Adaptive Desk Fill Light (STM32 + OpenCV)

A desk lighting prototype that detects the shadow cast by an object on the desk and fills it in from the matching side. A PySide6 + OpenCV desktop app watches the desk through a webcam, separates the object from its shadow, and decides which side the shadow falls on; an STM32F103 then drives three WS2812B LED zones (left / middle / right) over a small UART protocol with acknowledgements.

Course project, Shenzhen Technology University, spring semester 2026. It is the follow-up to my first project, [stm32-smart-ambient-lighting](https://github.com/qitong-yuan/stm32-smart-ambient-lighting), and reuses its WS2812 SPI + DMA driver.


https://github.com/user-attachments/assets/657d0d1f-4763-43b1-9b48-b070712fc74d


## Features

- **Automatic shadow fill.** With the camera and serial port open, auto mode switches all LEDs off, waits 0.8 s, stores a baseline frame, and then lights the zone(s) on the side where a shadow appears.
- **Object / shadow separation.** Pixels darker than the baseline are split into "object" and "shadow" with an Otsu threshold computed on the darkened pixels only, so no fixed darkness value has to be tuned per object.
- **Direction-based zone choice.** The zone is chosen from where the shadow pixels lie relative to the object's centroid (left, right, above), and more than one zone can be lit at once.
- **Smooth brightness ramp.** Brightness rises 3 % per frame while a shadow is present, holds for 40 shadow-free frames, then fades at 0.6 % per frame. Levels are quantised to 5 % steps before being sent.
- **Manual control.** On / off buttons for each zone, plus all on / all off.
- **Adjustable region of interest.** Three sliders set the size and position of the analysed part of the image (30 – 100 % of the frame).
- **Acknowledged protocol.** The firmware answers every command; the zone indicators in the GUI are updated from these replies, not from what the app assumes it sent.
- **Live overlay.** The preview shows the ROI, the object box, the shadow area, the chosen zones and the current levels. An OLED on the board shows each zone as ON / OFF.

## System overview

```
Webcam ──► PySide6 + OpenCV app ──UART 115200──► STM32F103C8 ──► WS2812B  LEFT | MID | RIGHT
           (detection, decision)  ◄──── ACK ────  (execution)  ──► OLED
```

### Detection pipeline (`host/main.py`)

The camera timer fires every 30 ms. For each frame:

1. Mirror the frame horizontally (the camera faces the opposite way to the LED layout), crop the ROI, convert to grey, apply a 5×5 Gaussian blur.
2. Subtract the current frame from the baseline and clip negatives to zero, so only *darkening* counts. Pixels brightened by the fill light are ignored.
3. Threshold the difference (slider, 5 – 60, default 15) and apply a 5×5 morphological opening. If fewer than 120 pixels remain, nothing is detected.
4. Run Otsu on the darkened pixels to find a split value, kept at least 12 above the slider threshold. Darker than the split = object, the rest = shadow.
5. Take the largest contour of each mask (minimum area 120 px) and its centroid.
6. Compute the share of shadow pixels to the left of, to the right of, and above the object centroid:
   - above ≥ 0.55 → middle zone
   - above < 0.70 and left ≥ 0.45 → left zone; right ≥ 0.45 → right zone
   - if nothing was selected, the larger of left / right
   - if a shadow is found but no object, fall back to the shadow centroid's position in the ROI (< 40 % left, > 60 % right, otherwise middle)

### Serial protocol

ASCII frames, `#` = start, `*` = end, no separators. Replies end with `\r\n`.

| Command | Meaning | Reply |
|---|---|---|
| `#LEFTON*` / `#LEFTOFF*` | Left zone on / off | `ACK:LEFT_ON` / `ACK:LEFT_OFF` |
| `#MIDON*` / `#MIDOFF*` | Middle zone on / off | `ACK:MID_ON` / `ACK:MID_OFF` |
| `#RIGHTON*` / `#RIGHTOFF*` | Right zone on / off | `ACK:RIGHT_ON` / `ACK:RIGHT_OFF` |
| `#ALL*` | All zones on | `ACK:ALL_ON` |
| `#OFF*` | All zones off | `ACK:ALL_OFF` |
| `#Lnnn*` / `#Mnnn*` / `#Rnnn*` | Set one zone to `nnn` % (three digits, `000` – `100`) | `ACK:Lnnn` etc. |
| `#LEFT*` / `#MID*` / `#RIGHT*` | Zone on (older form, not used by the app) | `ACK:LEFT_ON` etc. |
| anything else | – | `ERR:UNKNOWN_CMD` |

The firmware sends `READY` once after start-up. Frames are received byte by byte in the USART1 interrupt and parsed in the main loop. The app queues outgoing commands and sends one every 80 ms.

## Hardware

| Component | Interface | Pins |
|---|---|---|
| USB–TTL adapter (PC link) | USART1, 115200 8N1 | PA9 (TX), PA10 (RX) |
| 3 × WS2812B strip in series (15 LEDs, 5 per zone) | SPI1 MOSI + DMA1 channel 3 | PA7 |
| OLED | Software I²C | PB8 (SCL), PB9 (SDA) |
| USB webcam | – | connected to the PC |

LED indices 0 – 4 are the left zone, 5 – 9 the middle zone, 10 – 14 the right zone. Each WS2812 bit is encoded as one SPI byte (`0xF8` = 1, `0xE0` = 0) and DMA streams the whole 15 × 24 byte frame. The fill colour is white at (200, 200, 200), scaled by the requested percentage (`LIGHT_R/G/B` in `firmware/Hardware/WS2812.h`).

## Repository layout

```
firmware/        Keil uVision5 project (STM32F10x Standard Peripheral Library V3.5)
  User/          main.c – initialisation, main loop, command parser
  Hardware/      Drivers: WS2812 (zones, percentage dimming), Serial, OLED
  System/        Delay; timer and MPU6050 filter (left from the first project, not called)
  Library/ Start/  ST peripheral library and startup code
host/            PySide6 + OpenCV desktop application
  main.py        Serial link, detection pipeline, ramp control
  smartlight.ui  Qt Designer layout (Ui_smartlight.py is generated from it)
```

## Getting started

**Firmware:** open `firmware/project.uvprojx` in Keil uVision5, build, and flash to an STM32F103C8.

**Desktop app** (developed with Python 3.13 on Windows):

```bash
cd host
pip install -r requirements.txt
python main.py
```

1. Select the serial port and click connect. The manual buttons now work without a camera.
2. Select the camera index and open the camera. Adjust the three ROI sliders so the frame covers the desk area.
3. Clear the desk, then start auto mode. The baseline is captured 0.8 s later, with the LEDs off.
4. Place an object in the ROI. If the overlay shows the object but no shadow, lower the threshold slider.

The UI labels are in Chinese. Detection results appear only while auto mode is running, because the baseline exists only then.

## Engineering notes

- **From column statistics to shadow direction.** The first version split the image into three vertical strips and lit the darkest one. That cannot express which way a shadow is thrown from an object, so it was replaced by the object / shadow split and the centroid-relative direction test.
- **Middle zone never lit.** With strip statistics the centre strip almost never won. The middle zone now has its own rule (share of shadow pixels above the object).
- **Flicker from on / off control.** Switching a zone fully on and off made the system oscillate: the fill light removed the shadow, the light went off, the shadow came back. The fix is the asymmetric ramp (fast up, 40-frame hold, slow down). The ramp turned out to be required for stability, not only for appearance.
- **Lost commands.** The firmware has a single receive buffer, so a command arriving while the previous one was still being processed overwrote it (most often the middle-zone command). The app now puts every command in a queue, sends one per 80 ms, and skips a command equal to the last one queued.
- **Unfocused detection.** Analysing the full frame picked up unrelated dark areas at the edges. The adjustable ROI limits analysis to the desk; changing it in auto mode switches the LEDs off and recaptures the baseline.
- **Fill light casting new shadows.** A lit zone is itself a light source and can create a shadow on the other side. This is reduced, not solved: only darkening relative to the LEDs-off baseline is counted, and the slow fade prevents fast back-and-forth switching.

## Limitations

- Bench prototype: a cardboard box as the "desk", 15 LEDs and a top-down webcam. There are no accuracy or timing measurements.
- The method assumes the object is darker than its shadow. Light-coloured objects and faint shadows are split incorrectly or missed.
- The baseline is a single frame taken when auto mode starts. Objects already on the desk at that moment are not detected, and a change in ambient light or camera position requires restarting auto mode.
- Only the largest object blob and the largest shadow blob are used for detection, so the design targets one object. Hand occlusion, the original goal, is not implemented.
- The camera looks straight down, so the detected shadow side does not always match what a person sitting at the desk sees.
- Commands are sent at most every 80 ms, but a ramp can produce a new 5 % step faster than that. With several zones ramping, the queue grows and the LEDs lag behind the level shown in the overlay.
- The firmware uses blocking delays (10 ms per zone update, 150 ms for all-off) and has no command queue of its own.
- The horizontal mirror is fixed in code (`self._mirror`), and the app was only run on Windows.

## Author

Qitong Yuan – [github.com/qitong-yuan](https://github.com/qitong-yuan)
