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

### Components needed
- ESP32-WROVER (already on breadboard)
- 5 LEDs (any color)
- 5x 220Ω resistors (red-red-brown band)
- 6 jumper wires (male-to-male or male-to-female depending on breadboard)
- USB cable (to connect ESP32 to PC)

### Wiring diagram (per LED)

```
ESP32 GPIO pin ──── 220Ω Resistor ──── LED (long leg/anode) ──── LED (short leg/cathode) ──── GND
```

### Pin assignments

| Finger | GPIO Pin | LED Color (suggestion) |
|--------|----------|----------------------|
| Thumb  | GPIO 2   | Red                  |
| Index  | GPIO 4   | Yellow               |
| Middle | GPIO 5   | Green                |
| Ring   | GPIO 18  | Blue                 |
| Pinky  | GPIO 19  | White                |

All LED cathodes (short legs) connect to a shared **GND** rail on the breadboard, which connects to an ESP32 **GND** pin.

### Step-by-step wiring instructions
1. Place 5 LEDs on the breadboard, spaced apart
2. Connect a 220Ω resistor from each LED's **anode** (long leg) to a free row
3. Use jumper wires to connect each resistor's other end to the corresponding ESP32 GPIO pin
4. Connect all LED **cathodes** (short legs) to the breadboard's ground rail
5. Connect the breadboard ground rail to the ESP32's **GND** pin

---

## Part 2: ESP32 Firmware (Arduino C/C++)

**File:** `esp32/esp32_led_controller.ino`

### Logic
- Opens serial at 115200 baud
- Waits for 5-character strings like `"10110"` (1=on, 0=off, one per finger)
- Maps each character to a GPIO pin and sets HIGH/LOW
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
