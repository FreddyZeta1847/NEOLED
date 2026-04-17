# NEOLED Wiring Guide - Complete Beginner Edition

## What You Need From Your Kit

Grab these from your Freenove kit box:

| Component | Qty | How to Identify |
|-----------|-----|-----------------|
| LED | 5 | Small colored bulbs with 2 metal legs |
| 220 ohm resistor | 5 | Tiny cylinder with stripes: RED - RED - BROWN - GOLD |
| Jumper wires (M-M) | 5 | Colored wires with metal pins on both ends |
| USB cable | 1 | To connect ESP32 to your PC |

---

## Glossary (Read This First!)

**LED** — A tiny light. It has TWO legs:
- **Long leg** = positive (+) side, called "anode". Power goes IN here.
- **Short leg** = negative (-) side, called "cathode". Also: the FLAT side of the LED's bottom rim.
- If you plug it backwards it won't light up (but won't break).

**Resistor** — Slows down electricity so the LED doesn't burn out. ALWAYS put one between the ESP32 pin and the LED. It has no direction — plug it either way.

**GPIO** — The pins on your ESP32 you control with code. When code says "turn GPIO 2 ON", that pin sends electricity out.

**GND** — Ground. The return path for electricity, like the minus (-) terminal of a battery. Every circuit needs it.

**Breadboard** — The white board with holes. Components plug in to connect WITHOUT soldering.

---

## How Your Breadboard Works

```
    YOUR BREADBOARD (top view)
    
    LEFT RAILS          CENTER AREA           RIGHT RAILS
    -  +          a  b  c  d  e | f  g  h  i  j          +  -
    -  +    row1  .  .  .  .  . | .  .  .  .  .    row1  +  -
    -  +    row2  .  .  .  .  . | .  .  .  .  .    row2  +  -
    -  +    row3  .  .  .  .  . | .  .  .  .  .    row3  +  -
    -  +    ...                                     ...   +  -
    -  +    row30 .  .  .  .  . | .  .  .  .  .   row30  +  -
    -  +                                                  +  -
    
    GND  5V                                          EXT-3.3V  GND
```

### Connection rules:

**Side rails (+ and -):** All holes in the same column are connected top-to-bottom.
- Left `-` rail = all connected = your GND (already wired via screw terminal)
- Left `+` rail = all connected = 5V

**Center area:** Holes in the same ROW on the same SIDE of the gap are connected.
- `a1, b1, c1, d1, e1` = all connected together
- `f1, g1, h1, i1, j1` = all connected together
- But `e1` is NOT connected to `f1` — the center gap separates them

**Your ESP32** sits across the center gap, with pins going into both sides.

---

## Your ESP32 Pin Map (from your board photo)

```
              USB PORT (top)
              
    LEFT SIDE                RIGHT SIDE
    ─────────                ──────────
    3.3V                     GND
    EN                       23
    36/VP                    22
    39/VN                    1/TX
    34                       3/RX
    35                       21
    32                       GND
    33                       19
    25                       18
    26                       5
    27                       17
    14  ← PINKY              16
    12  ← RING               GND
    GND                      4   ← INDEX
    13  ← MIDDLE             0
    3.3V*                    2   ← THUMB
    3.3V*                    15
    3.3V*                    *GND
    5V                       *GND
    5V                       GND
```

The 5 GPIO pins we use are marked with arrows above.

---

## Wiring: Step by Step

### How one LED circuit works

```
ESP32 GPIO pin ──→ jumper wire ──→ RESISTOR ──→ LED (long leg +) → LED (short leg -) ──→ GND rail
```

Electricity flows: GPIO → wire → resistor → LED → ground. Done.

---

### LED #1 — THUMB (GPIO 2, right side of ESP32)

GPIO 2 is on the **right side**, near the bottom of the ESP32. Look at your board and find which breadboard row it sits in.

**Step 1:** Find GPIO 2's row on the right side (columns f-j). Let's call it row R.

**Step 2:** Place a jumper wire from **row R, column j** to a free area on the left side of the breadboard. Pick **row 1, column a**.

**Step 3:** Place a 220 ohm resistor from **row 1, column b** to **row 2, column b**. (Bridges two rows. Direction doesn't matter.)

**Step 4:** Place the LED:
- **Long leg (+)** into **row 2, column c** (same row as resistor's other end)
- **Short leg (-)** into the **left minus (-) rail**

```
    - rail     a      b      c      d      e
      |        |      |      |
      |   [wire from GPIO2]  |      
      |     row1 ────[RESISTOR]──── row2
      |                      |
      ●←── LED short leg     LED long leg (row2, col c)
    (flat side)
```

**That's it! One LED done.** The circuit is: GPIO 2 → wire → resistor → LED → GND rail.

---

### LED #2 — INDEX (GPIO 4, right side of ESP32)

GPIO 4 is also on the **right side**, just above GPIO 2.

Repeat the same pattern using **rows 4-5**:

1. Jumper wire from GPIO 4's row (column j) → **row 4, column a**
2. Resistor from **row 4, column b** → **row 5, column b**
3. LED long leg → **row 5, column c** / LED short leg → **minus (-) rail**

---

### LED #3 — MIDDLE (GPIO 13, left side of ESP32)

GPIO 13 is on the **left side**. Its pin already connects to a row on the left half (columns a-e).

This one is easier — no long jumper wire needed:

1. Find GPIO 13's row. The pin is already in column e (or d). Let's call it row M.
2. Resistor from **row M, column a** → **row M+1, column a** (next row down)
3. LED long leg → **row M+1, column b** / LED short leg → **minus (-) rail**

The GPIO pin and resistor are in the same row, so they're already connected!

---

### LED #4 — RING (GPIO 12, left side)

Same pattern as LED #3. GPIO 12 is on the left side, two pins above GPIO 13.

1. Find GPIO 12's row (column e or d)
2. Resistor from that row (column a) → next row (column a)
3. LED long leg in resistor's second row (column b) / short leg → minus (-) rail

---

### LED #5 — PINKY (GPIO 14, left side)

Same pattern. GPIO 14 is on the left side, two pins above GPIO 12.

1. Find GPIO 14's row
2. Resistor from that row (column a) → next row (column a)
3. LED long leg in next row (column b) / short leg → minus (-) rail

---

## Final Check

After wiring all 5 LEDs, you should have:

- [x] 5 LEDs with short legs all in the **minus (-) rail**
- [x] 5 resistors, each connecting an LED to a GPIO pin's row
- [x] 2 jumper wires for the right-side GPIOs (2 and 4) crossing to the left half
- [x] USB cable plugged in from ESP32 to PC (for power + communication)
- [x] Nothing in GPIO 1/TX, 3/RX, or GPIO 0

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| LED doesn't light up | LED is backwards | Swap the two legs (rotate 180) |
| LED doesn't light up | Wrong row | Check resistor + LED share a row |
| LED doesn't light up | Resistor not seated | Push it firmly into the holes |
| LED is very dim | Wrong resistor value | Use 220 ohm (red-red-brown-gold) |
| Nothing works at all | No power | Check USB cable connected to PC |
| Wrong LED lights up | Wrong GPIO row | Double-check pin labels on board |
