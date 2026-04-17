# Issue #1: ESP32 COM Port Not Detected + OpenOCD Upload Error

## Date: 2026-04-17

## Problem
After plugging the ESP32 via USB, Device Manager showed no "Ports (COM & LPT)" section. The ESP32 appeared as "Camera DFU Device" under "Universal Serial Bus devices" instead of a serial port.

Additionally, when trying to upload from Arduino IDE, the following error appeared:
```
Error: unable to open ftdi device with description '*', serial '*' at bus location '*'
```

## Root Causes

### 1. COM Port not appearing
The ESP32 was booting into Camera DFU mode instead of serial mode.

**Solution:** Hold the **IO0 button** while plugging in the USB cable, then release after 2 seconds. This forces the ESP32 into serial/download mode. After that, "Ports (COM & LPT)" appeared in Device Manager with COM3.

### 2. OpenOCD upload error
The **Debug button** was being clicked instead of the **Upload button** in Arduino IDE. The debug button launches OpenOCD (a JTAG debugger), which tries to connect via FTDI — not applicable to our USB serial setup.

**Solution:** Use the **Upload button (→ arrow)** in Arduino IDE, not the debug button (play icon with a bug).

## Correct Arduino IDE Settings
- Board: ESP32 Wrover Module (or ESP32 Dev Module)
- Port: COM3
- Upload Speed: 115200
- Programmer: Esptool

## Lesson Learned
- IO0 button = BOOT mode selector on this board
- Debug button != Upload button in Arduino IDE
- The CH340 driver was already pre-installed, no manual driver install needed
