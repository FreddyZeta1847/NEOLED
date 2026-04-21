"""
hand_tracker.py — Main application for NEOLED.

Uses the webcam to detect hand gestures with MediaPipe,
counts which fingers are raised, and sends the state to
the ESP32 to control LEDs.

Run with:
  python hand_tracker.py              (with ESP32 connected)
  python hand_tracker.py --no-serial  (webcam only, no ESP32)
"""

import cv2
import mediapipe as mp
import os
import sys
import time
import random
import math

import serial_comm

# Each finger gets a unique neon color (BGR format — OpenCV uses Blue,Green,Red).
FINGER_COLORS = [
    (0, 100, 255),   # Thumb  — orange
    (0, 255, 255),   # Index  — yellow
    (0, 255, 100),   # Middle — green
    (255, 200, 0),   # Ring   — cyan
    (255, 50, 150),  # Pinky  — magenta
]

# MediaPipe landmark IDs for each fingertip.
FINGERTIP_IDS = [4, 8, 12, 16, 20]

# A "landmark" is a point on the hand. MediaPipe always returns 21 of them as
# an ordered list. Each landmark has .x and .y coordinates (0.0-1.0), but its
# position in the list IS its ID: landmarks[0] = wrist, landmarks[8] = index tip, etc.
# We use the IDs to know WHICH joint we're looking at, and the coordinates to
# know WHERE it is on screen. IDs are fixed by Google, coordinates change every frame.


def dist_sq(p1, p2):
    """
    Returns the SQUARED distance between two landmarks (no sqrt needed).
    We skip sqrt because we only compare distances — if a² > b² then a > b.
    Uses Pythagoras: dist² = (x2-x1)² + (y2-y1)²
    """
    return (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2


def detect_fingers(landmarks):
    """
    Determines which fingers are raised based on landmark positions.
    Returns a list of 5 booleans: [Thumb, Index, Middle, Ring, Pinky].

    Rotation-invariant approach: instead of comparing raw Y coordinates
    (which only works when the hand points up), we use the WRIST as the
    origin and compare distances:
      - dist(wrist, fingertip) vs dist(wrist, PIP joint)
      - If the tip is FARTHER from the wrist than the PIP → finger is extended
      - If the tip is CLOSER to the wrist than the PIP → finger is curled
    This works regardless of hand orientation (up, down, left, right, tilted).

    MediaPipe hand landmark IDs:
        0  = Wrist (our origin point)
        4  = Thumb tip         3  = Thumb IP joint
        8  = Index tip         6  = Index PIP joint
        12 = Middle tip        10 = Middle PIP joint
        16 = Ring tip          14 = Ring PIP joint
        20 = Pinky tip         18 = Pinky PIP joint
    """

    wrist = landmarks[0]

    # --- THUMB (x-coordinate approach) ---
    # The thumb moves sideways, so we compare x-coordinates of tip vs joint.
    # We check wrist vs pinky base to determine left/right hand.
    thumb_tip_x = landmarks[4].x
    thumb_joint_x = landmarks[3].x
    pinky_mcp_x = landmarks[17].x

    if wrist.x < pinky_mcp_x:
        thumb_extended = thumb_tip_x < thumb_joint_x
    else:
        thumb_extended = thumb_tip_x > thumb_joint_x

    # --- OTHER FINGERS ---
    # For each finger, compare:
    #   dist²(wrist, tip) vs dist²(wrist, pip_joint)
    # Works in any hand orientation because distances don't depend on direction.
    finger_pairs = [
        (8, 6),    # Index:  tip=8,  PIP joint=6
        (12, 10),  # Middle: tip=12, PIP joint=10
        (16, 14),  # Ring:   tip=16, PIP joint=14
        (20, 18),  # Pinky:  tip=20, PIP joint=18
    ]

    fingers = [thumb_extended]
    for tip_id, joint_id in finger_pairs:
        tip_farther = dist_sq(wrist, landmarks[tip_id]) > dist_sq(wrist, landmarks[joint_id])
        fingers.append(tip_farther)

    return fingers


def fingers_to_string(fingers):
    """Converts [True, False, True, True, False] → '10110'."""
    return "".join("1" if f else "0" for f in fingers)


def draw_hand_skeleton(frame, landmarks, width, height, fingers):
    """Draws a futuristic neon hand skeleton with glowing bones and color-coded fingertips."""

    # Which landmark pairs to connect with lines (the "bones").
    hand_connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),        # Index
        (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
        (5, 9), (9, 13), (13, 17),              # Palm cross-connections
    ]

    # Groups of landmark IDs belonging to each finger.
    # Used to color each finger's bones with its own neon color.
    finger_bone_groups = [
        {1, 2, 3, 4},       # Thumb landmarks (excluding wrist 0)
        {5, 6, 7, 8},       # Index
        {9, 10, 11, 12},    # Middle
        {13, 14, 15, 16},   # Ring
        {17, 18, 19, 20},   # Pinky
    ]

    # Convert normalized coordinates (0.0-1.0) to pixel positions.
    points = []
    for lm in landmarks:
        px = int(lm.x * width)
        py = int(lm.y * height)
        points.append((px, py))

    # Pulse effect: sin() oscillates between -1 and +1.
    pulse = (math.sin(time.time() * 4) + 1) / 2

    # --- DRAW BONES ---
    for start, end in hand_connections:
        # Find which finger this bone belongs to, for coloring.
        bone_color = (60, 60, 60) 
        for fi, group in enumerate(finger_bone_groups):
            if start in group and end in group:
                bone_color = FINGER_COLORS[fi] if fingers[fi] else (40, 40, 40)
                break

        # Glow trick: draw a thick dim line BEHIND a thin bright line.
        glow = tuple(int(c * 0.3) for c in bone_color)
        cv2.line(frame, points[start], points[end], glow, 6)    # outer glow
        cv2.line(frame, points[start], points[end], bone_color, 2)  # inner line

    # --- DRAW JOINTS ---
    # enumerate() gives us both the index (i) and the point.
    # i = the landmark ID (0-20), point = its pixel position.
    for i, point in enumerate(points):
        # We loop through all 5 finger groups and check:
        #   1. Is this landmark ID (i) in this finger's group?
        #   2. Is that finger currently raised (fingers[fi] == True)?
        is_active = False
        for fi, group in enumerate(finger_bone_groups):
            if i in group and fingers[fi]:
                is_active = True
                break

        if is_active:
            r = int(4 + pulse * 2)  # pulsation
            cv2.circle(frame, point, r + 4, (255, 255, 255), 1)   # outer ring
            cv2.circle(frame, point, r, (255, 255, 255), -1)       # filled center
        else:
            cv2.circle(frame, point, 3, (80, 80, 80), -1)

    # --- DRAW FINGERTIPS ---
    for fi, tip_id in enumerate(FINGERTIP_IDS):
        color = FINGER_COLORS[fi]
        pt = points[tip_id]

        if fingers[fi]:
            # Active fingertip: 4 layered circles from big/dim to small/bright.
            glow_r = int(18 + pulse * 6)  # outer radius pulses between 18-24px
            cv2.circle(frame, pt, glow_r, tuple(int(c * 0.2) for c in color), -1)  # faint outer
            cv2.circle(frame, pt, 12, tuple(int(c * 0.5) for c in color), -1)       # mid glow
            cv2.circle(frame, pt, 6, color, -1)                                     # bright core
            cv2.circle(frame, pt, 3, (255, 255, 255), -1)                           # white hot center
        else:
            # Inactive: dim circle with outline.
            cv2.circle(frame, pt, 5, (40, 40, 40), -1)
            cv2.circle(frame, pt, 5, (80, 80, 80), 1)


def draw_ui(frame, finger_state, connection, no_serial, width, height):
    """Draws the futuristic HUD overlay with semi-transparent bars."""

    finger_count = finger_state.count("1")

    # --- TOP BAR ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 65), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # Cyan accent line under the top bar (1px thin neon separator).
    cv2.line(frame, (0, 65), (width, 65), (0, 255, 255), 1)

    # Title with glow: draw the same text twice — first in dark color (shadow),
    # then in bright color on top. The thick dark text bleeds around the thin
    # bright text, creating a glow/halo effect.
    cv2.putText(frame, "NEOLED", (15, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 80, 80), 2)   # dark glow layer
    cv2.putText(frame, "NEOLED", (15, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1)  # bright top layer

    cv2.putText(frame, "HAND GESTURE CONTROLLER", (15, 52),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

    # Active LED count in the top right.
    count_color = (0, 255, 255) if finger_count > 0 else (80, 80, 80)
    cv2.putText(frame, f"{finger_count}/5", (width - 80, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 50, 50), 3)   # dark glow
    cv2.putText(frame, f"{finger_count}/5", (width - 80, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, count_color, 2)    # bright text
    cv2.putText(frame, "LEDs", (width - 75, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

    # Connection status dot + label.
    if connection:
        cv2.circle(frame, (width // 2, 35), 5, (0, 255, 0), -1)
        cv2.putText(frame, "LINKED", (width // 2 + 12, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 0), 1)
    elif not no_serial:
        cv2.circle(frame, (width // 2, 35), 5, (0, 0, 200), -1)
        cv2.putText(frame, "NO LINK", (width // 2 + 12, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 200), 1)

    # --- BOTTOM BAR (same semi-transparent technique) ---
    bar_h = 80
    bar_y = height - bar_h
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, bar_y), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay2, 0.7, frame, 0.3, 0, frame)
    cv2.line(frame, (0, bar_y), (width, bar_y), (0, 255, 255), 1)

    # Finger indicators: one per finger, evenly spaced.
    labels = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]
    spacing = width // 5

    for i, label in enumerate(labels):
        x_center = spacing // 2 + i * spacing
        color = FINGER_COLORS[i]
        is_on = finger_state[i] == "1"

        # Small vertical line connecting the accent bar to the circle.
        cv2.line(frame, (x_center, bar_y), (x_center, bar_y + 10),
                 color if is_on else (40, 40, 40), 2)

        # Status circle: layered glow when ON, dim outline when OFF.
        cy = bar_y + 28
        if is_on:
            # 3-layer glow: faint outer (16px) → colored mid (12px) → white center (6px).
            cv2.circle(frame, (x_center, cy), 16,
                       tuple(int(c * 0.3) for c in color), -1)
            cv2.circle(frame, (x_center, cy), 12, color, -1)
            cv2.circle(frame, (x_center, cy), 6, (255, 255, 255), -1)
            cv2.putText(frame, "ON", (x_center - 8, cy + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
        else:
            cv2.circle(frame, (x_center, cy), 12, (40, 40, 40), -1)
            cv2.circle(frame, (x_center, cy), 12, (60, 60, 60), 1)

        # Finger name label, centered under the circle.
        # getTextSize() returns (width, height) of the rendered text
        # so we can offset by half to center it horizontally.
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)[0]
        text_x = x_center - text_size[0] // 2
        cv2.putText(frame, label, (text_x, bar_y + 62),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38,
                    color if is_on else (80, 80, 80), 1)

    # Raw state code in bottom-right corner (e.g. "10110").
    cv2.putText(frame, finger_state, (width - 80, height - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)


def main():
    """
    Main loop: captures webcam frames, detects hand gestures,
    sends finger states to ESP32, and shows the video preview.
    """

    # Check if --no-serial flag was passed (skip ESP32 connection).
    no_serial = "--no-serial" in sys.argv

    # --- CONNECT TO ESP32 ---
    connection = None
    if not no_serial:
        connection = serial_comm.connect()
        if connection is None:
            print("Starting without ESP32 (webcam preview only)")

    # --- SETUP MEDIAPIPE ---
    # Load the hand landmarker model from the .task file.
    model_path = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
    base_options = mp.tasks.BaseOptions(model_asset_path=model_path)

    # Configure the detector: VIDEO mode, 1 hand, 70% detection confidence.
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
    )

    # Load the model into memory — this is the object we call detect_for_video() on.
    landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

    # --- OPEN WEBCAM ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        landmarker.close()
        return

    print("NEOLED running. Press 'q' to quit.")

    # --- STATE ---
    last_send_time = 0
    send_interval = 0.1  # send to ESP32 at most every 100ms
    prev_state = ""       # track previous state to avoid duplicate sends
    frame_timestamp_ms = 0  # MediaPipe requires increasing timestamps

    # --- MAIN LOOP ---
    while True:
        # Grab one frame from the webcam.
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror the image so it feels like a mirror.
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # Convert BGR → RGB and wrap in a MediaPipe Image for the model.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run the hand detection model on this frame.
        # This one call does both palm detection + landmark detection internally.
        result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33  # advance timestamp by ~33ms (30fps)

        finger_state = "00000"
        fingers = [False] * 5

        # result.hand_landmarks is a list of detected hands (each = 21 landmarks).
        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]  # first hand only

            fingers = detect_fingers(landmarks)
            finger_state = fingers_to_string(fingers)

            draw_hand_skeleton(frame, landmarks, width, height, fingers)


        # --- SEND TO ESP32 ---
        current_time = time.time()
        if (current_time - last_send_time >= send_interval and finger_state != prev_state and connection):
            serial_comm.send_finger_state(connection, finger_state)
            last_send_time = current_time
            prev_state = finger_state


        draw_ui(frame, finger_state, connection, no_serial, width, height)

        cv2.imshow("NEOLED", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.getWindowProperty("NEOLED", cv2.WND_PROP_VISIBLE) < 1:
            break

    # --- CLEANUP ---
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    if connection:
        serial_comm.disconnect(connection)
    print("NEOLED stopped.")


if __name__ == "__main__":
    main()
