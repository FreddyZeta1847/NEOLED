# Plan Zip - Active Plans Summary

## NEOLED - Hand Gesture LED Controller
**Status:** Planned - hardware verified from board photo
**Plan file:** [PLAN.md](PLAN.md)

**Summary:** PC webcam tracks hand fingers via MediaPipe + OpenCV, sends finger state (`"10110"`) over USB serial to ESP32, which controls 5 LEDs (one per finger). Latch mode: all fingers open = LEDs stay on; fist = all off. ESP32 firmware in Arduino C/C++, PC app in Python. GPIO pins: 2, 4, 13, 12, 14. GND rail already connected via screw terminal. 6-step implementation: scaffolding -> firmware -> wiring guide -> serial module -> hand tracker -> integration.
