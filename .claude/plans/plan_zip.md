# Plan Zip - Active Plans Summary

## NEOLED - Hand Gesture LED Controller
**Status:** Implemented
**Plan file:** [PLAN.md](PLAN.md)

**Summary:** PC webcam tracks hand fingers via MediaPipe + OpenCV, sends finger state (`"10110"`) over USB serial to ESP32, which controls 5 LEDs (one per finger). Rotation-invariant finger detection using Pythagorean distance from wrist (thumb uses index base as reference). ESP32 firmware in Arduino C/C++, PC app in Python with neon HUD. GPIO pins: 2, 4, 13, 12, 14.
