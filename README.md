<p align="center">
  <h1 align="center">NEOLED</h1>
  <p align="center"><b>Hand Gesture LED Controller</b></p>
  <p align="center">Control real LEDs with your fingers using computer vision, MediaPipe, and an ESP32 microcontroller.</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-Hand_Tracking-0097A7?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-Video-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/ESP32-Arduino-E7352C?style=for-the-badge&logo=arduino&logoColor=white" />
</p>

---

## What is NEOLED?

**NEOLED** is an interactive system that bridges computer vision with physical electronics. A Python app uses your webcam to track your hand in real-time — each raised finger lights up a corresponding LED on a breadboard. Lower your finger and the LED turns off. No buttons, no keyboard — just your hand.

The interface features a futuristic neon HUD with color-coded finger tracking, glowing hand skeleton, and pulsing joints.

## How It Works

```
Webcam (30 fps)
     |
     v
[ MediaPipe ]  --  Neural network detects 21 hand landmarks
     |
     v
[ Finger Logic ]  --  Compares fingertip vs knuckle positions
     |
     v
[ USB Serial ]  --  Sends "10110" string to ESP32
     |
     v
[ ESP32 + LEDs ]  --  Sets each GPIO HIGH or LOW
```

1. **Capture** — OpenCV grabs frames from the webcam at ~30fps
2. **Detect** — MediaPipe's pre-trained neural network finds 21 joint positions on the hand
3. **Analyze** — Our code compares fingertip Y-coordinates vs knuckle Y-coordinates to determine which fingers are raised
4. **Transmit** — A 5-character string like `"10110"` is sent over USB serial (each char = one finger)
5. **Control** — The ESP32 reads the string and drives 5 GPIO pins to turn LEDs on/off

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | **Python 3.13** + **C/C++ (Arduino)** |
| Hand Tracking | **Google MediaPipe** — Hand Landmarker neural network |
| Video | **OpenCV** — webcam capture and neon UI overlay |
| Communication | **PySerial** — USB serial at 115200 baud |
| Microcontroller | **ESP32-WROVER** (Freenove) — 5 GPIO pins driving LEDs |
| Hardware | **Breadboard** — 5 LEDs + 220 ohm resistors |

## Project Structure

```
NEOLED/
├── esp32/
│   └── esp32_led_controller/
│       └── esp32_led_controller.ino    # Arduino firmware
├── pc/
│   ├── hand_tracker.py                 # Main app (MediaPipe + OpenCV + neon UI)
│   ├── serial_comm.py                  # USB serial communication
│   ├── hand_landmarker.task            # MediaPipe hand model (~7MB)
│   └── requirements.txt               # Python dependencies
└── docs/
    └── wiring_guide.md                 # Beginner-friendly wiring instructions
```

## Hardware Setup

### Components

- ESP32-WROVER (Freenove Ultimate Starter Kit)
- 5 LEDs (any color)
- 5x 220 ohm resistors (red-red-brown-gold)
- Jumper wires
- USB data cable

### GPIO Pin Mapping

| Finger | GPIO Pin |
|--------|----------|
| Thumb  | 2        |
| Index  | 4        |
| Middle | 13       |
| Ring   | 12       |
| Pinky  | 14       |

### Wiring

Each LED circuit follows the same pattern:

```
GPIO pin → jumper wire → 220 ohm resistor → LED (long leg +) → LED (short leg -) → GND rail
```

See [docs/wiring_guide.md](docs/wiring_guide.md) for a complete beginner guide with diagrams and troubleshooting.

## Software Setup

### 1. Flash the ESP32

- Open `esp32/esp32_led_controller/esp32_led_controller.ino` in **Arduino IDE**
- Install ESP32 board support (Espressif board manager)
- Select **ESP32 Wrover Module** and the correct COM port
- Click **Upload**

Test it: open Serial Monitor (115200 baud), type `11111` — all 5 LEDs turn on. Type `00000` — all off.

### 2. Install Python Dependencies

```bash
pip install -r pc/requirements.txt
```

### 3. Run

With ESP32 connected:

```bash
python pc/hand_tracker.py
```

Without ESP32 (webcam preview only):

```bash
python pc/hand_tracker.py --no-serial
```

Press `q` or close the window to quit.

## License

MIT

---
