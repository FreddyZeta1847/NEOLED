# Plan Zip - Active Plans Summary

## NEOLED - Hand Gesture LED Controller
**Status:** Planned - awaiting approval
**Plan file:** [PLAN.md](PLAN.md)

**Summary:** PC webcam tracks hand fingers via MediaPipe + OpenCV, sends finger state (`"10110"`) over USB serial to ESP32, which controls 5 LEDs (one per finger). Latch mode: all fingers open = LEDs stay on; fist = all off. ESP32 firmware in Arduino C/C++, PC app in Python. 6-step implementation: scaffolding → firmware → wiring guide → serial module → hand tracker → integration.
