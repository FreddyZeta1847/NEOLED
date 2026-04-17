# NEOLED - Hand Gesture LED Controller

## Context
Build an interactive system where a PC webcam tracks hand/finger movements using Python (MediaPipe + OpenCV), and controls 5 LEDs on an ESP32 via USB serial. Each raised finger lights up one LED. Special gestures: open all fingers instantly = LEDs stay on (latched); close fist = all LEDs off.

---

## Architecture Overview

```
┌──────────────────┐    USB Serial     ┌──────────────────────┐
│   PC (Python)    │ ───────────────>  │   ESP32-WROVER       │
│                  │   sends: "01011"  │                      │
│  - OpenCV        │   (5 chars,       │  - Arduino C/C++     │
│  - MediaPipe     │   one per finger) │  - Reads serial      │
│  - PySerial      │                   │  - Controls 5 GPIOs  │
└──────────────────┘                   └──────────┬───────────┘
                                                  │ GPIO pins
                                          ┌───────┴────────┐
                                          │  Breadboard     │
                                          │  5 LEDs + 220Ω  │
                                          └─────────────────┘
```

---

## Part 1: Hardware Setup (Wiring Guide)

### Board confirmed
Freenove ESP32 GPIO Extension Board (photo: `esp32/esp32 pins.jpeg`)
- Left power rail: GND (-) and 5V (+) — already connected via screw terminals
- Right power rail: GND (-) and EXT-3.3V (+) — already connected

### Components needed
- 5 LEDs (any color from kit)
- 5x 220 ohm resistors (red-red-brown-gold stripes)
- 5 jumper wires (male-to-male)
- USB cable (ESP32 to PC)

### Pin assignments (verified from board photo)

| Finger | GPIO | Board side | Approx breadboard row |
|--------|------|-----------|----------------------|
| Thumb  | 2    | RIGHT, near bottom | ~row 29 |
| Index  | 4    | RIGHT, near bottom | ~row 28 |
| Middle | 13   | LEFT, near bottom  | ~row 28 |
| Ring   | 12   | LEFT                | ~row 26 |
| Pinky  | 14   | LEFT                | ~row 25 |

GND: Use the LEFT minus (-) rail — already connected to GND via screw terminal.

### Wiring per LED
```
GPIO pin row → jumper wire → resistor (220 ohm) → LED long leg (+) → LED short leg (-) → GND rail (-)
```

### Key beginner notes
- LED long leg = positive (anode), short leg = negative (cathode, flat side of rim)
- Resistor has no direction — either way works
- LED short leg always goes into the minus (-) rail on the left side
- Avoid GPIO 1/TX, 3/RX (serial), GPIO 0 (boot), GPIO 34/35/36/39 (input-only)

---

## Part 2: ESP32 Firmware (Arduino C/C++)

**File:** `esp32/esp32_led_controller.ino`

### GPIO pin mapping in firmware
```cpp
int ledPins[5] = {2, 4, 13, 12, 14};
//                 ^  ^   ^   ^   ^
//              Thumb Index Middle Ring Pinky
```

### Logic
- Opens serial at 115200 baud
- Waits for 5-character strings like `"10110"` (1=on, 0=off, one per finger)
- Character 0 → GPIO 2 (Thumb), char 1 → GPIO 4 (Index), char 2 → GPIO 13 (Middle), char 3 → GPIO 12 (Ring), char 4 → GPIO 14 (Pinky)
- Sets each pin HIGH (LED on) or LOW (LED off)
- Sends acknowledgment back over serial

### Key features
- Simple serial protocol: receives exactly 5 bytes per message
- No WiFi needed - just USB connection
- Built-in LED blink on startup to confirm firmware is running

---

## Part 3: Python Application (PC Side)

### Dependencies
- `opencv-python` — webcam capture and display
- `mediapipe` — hand landmark detection (21 hand landmarks)
- `pyserial` — USB serial communication with ESP32

**File:** `pc/hand_tracker.py`

### Hand Detection Logic (MediaPipe)

MediaPipe detects 21 landmarks per hand. To determine if a finger is "open":
- **Thumb**: Compare tip (landmark 4) x-position vs. joint (landmark 3) — thumb opens sideways
- **Index**: Compare tip (landmark 8) y-position vs. PIP joint (landmark 6) — tip above joint = open
- **Middle**: Compare tip (landmark 12) y-position vs. PIP joint (landmark 10)
- **Ring**: Compare tip (landmark 16) y-position vs. PIP joint (landmark 14)
- **Pinky**: Compare tip (landmark 20) y-position vs. PIP joint (landmark 18)

### Gesture Logic
- Each frame: detect which fingers are up → build string like `"10110"`
- Send string over serial to ESP32
- **Latch mode**: If all 5 fingers open simultaneously → LEDs stay ON (latched), stop sending updates
- **Unlatch**: If fist detected (all closed) → send `"00000"`, resume normal tracking
- Visual feedback: draw hand skeleton + finger status on webcam preview window

### Serial Communication
- Auto-detect ESP32 COM port (scan available ports)
- 115200 baud, 8N1
- Send finger state string every ~100ms (throttled to avoid flooding)

---

## Part 4: Project File Structure

```
NEOLED/
├── .claude/
│   ├── agents/
│   ├── plans/
│   │   ├── PLAN.md
│   │   └── plan_zip.md
│   ├── skills/
│   └── tree.md
├── esp32/
│   └── esp32_led_controller.ino    # Arduino sketch for ESP32
├── pc/
│   ├── hand_tracker.py             # Main Python app (MediaPipe + OpenCV)
│   ├── serial_comm.py              # Serial communication module
│   └── requirements.txt            # Python dependencies
├── docs/
│   └── wiring_guide.md             # Detailed wiring instructions with ASCII diagrams
├── CLAUDE.md                       # Project-level instructions
└── README.md
```

---

## Implementation Order

### Step 1: Project scaffolding
- Create directory structure
- Create `CLAUDE.md` with project conventions
- Create `requirements.txt`

### Step 2: ESP32 firmware
- Write Arduino sketch with serial LED control
- Include instructions for flashing via Arduino IDE

### Step 3: Wiring guide
- Detailed step-by-step wiring doc with ASCII diagrams
- Pin mapping reference

### Step 4: Python serial module
- Auto-detect COM port
- Send/receive functions
- Connection status handling

### Step 5: Python hand tracker
- MediaPipe hand detection
- Finger state detection logic
- Latch/unlatch gesture logic
- OpenCV preview window with overlay

### Step 6: Integration & testing
- End-to-end test procedure
- Troubleshooting guide in README

---

## Verification / Testing Plan

1. **ESP32 firmware test**: Flash the sketch, open Arduino Serial Monitor, manually type `"11111"` → all 5 LEDs should light up. Type `"00000"` → all off.
2. **Python hand tracker test** (no ESP32): Run with `--no-serial` flag, verify webcam shows hand skeleton and finger count overlay.
3. **Serial comms test**: Run Python with ESP32 connected, verify COM port auto-detected and data flows.
4. **Full integration**: Open hand in front of camera → LEDs follow fingers. Open all fingers fast → LEDs latch on. Close fist → all LEDs off.

---

## Prerequisites the user needs to install

1. **Arduino IDE** — with ESP32 board support added (Espressif board manager URL)
2. **Python 3.10+** — with pip
3. **USB driver** — CP2102 or CH340 driver for ESP32 USB (usually auto-installed on Windows 11)
