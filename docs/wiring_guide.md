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

All 5 LEDs will be lined up neatly at the bottom of the breadboard (left side), with anodes in **column A**. A jumper wire connects each GPIO pin to the LED area.

### How one LED circuit works

```
GPIO pin row ──→ JUMPER WIRE ──→ row N, col D ──→ RESISTOR ──→ row N+1 ──→ LED anode (col A) ──→ LED cathode ──→ minus (-) rail
```

### The layout

| LED # | Finger | GPIO | Wire goes to row | Resistor rows | LED anode row, col A |
|-------|--------|------|-----------------|---------------|---------------------|
| 1     | Thumb  | 2    | row 40          | 40 → 41       | row 41              |
| 2     | Index  | 4    | row 43          | 43 → 44       | row 44              |
| 3     | Middle | 13   | row 46          | 46 → 47       | row 47              |
| 4     | Ring   | 12   | row 49          | 49 → 50       | row 50              |
| 5     | Pinky  | 14   | row 52          | 52 → 53       | row 53              |

---

### LED #1 — THUMB (GPIO 2)

GPIO 2 is on the **right side** of the ESP32, near the bottom. Find which breadboard row it sits in.

**Step 1 — Jumper wire:** Plug one end into **GPIO 2's row** (right side, any free column like col j). Plug the other end into **row 40, column d** (left side).

**Step 2 — Resistor:** Plug one end into **row 40, column c**. Plug the other end into **row 41, column c**. (Same column, spans two rows. Direction doesn't matter.)

**Step 3 — LED:**
- **Long leg (+, anode)** into **row 41, column a**
- **Short leg (-, cathode, flat side)** into the **LEFT minus (-) rail**

```
    - rail     a       b       c       d       e
      |        |               |       |
      |        |               |    [WIRE from GPIO 2]     row 40
      |        |            [RESISTOR]                       
      |     [LED +]         [RESISTOR]                     row 41
      ●──[LED -]            
      |  (short leg,
      |   flat side)
```

The circuit: GPIO 2 → wire → row 40 → resistor → row 41 → LED → GND. Done!

---

### LED #2 — INDEX (GPIO 4)

GPIO 4 is on the **right side**, just above GPIO 2. Same pattern:

1. **Wire:** GPIO 4's row (right side, col j) → **row 43, col d**
2. **Resistor:** **row 43, col c** → **row 44, col c**
3. **LED:** long leg (+) → **row 44, col a** / short leg (-) → **minus (-) rail**

---

### LED #3 — MIDDLE (GPIO 13)

GPIO 13 is on the **left side**. Same pattern:

1. **Wire:** GPIO 13's row (left side, col a) → **row 46, col d**
2. **Resistor:** **row 46, col c** → **row 47, col c**
3. **LED:** long leg (+) → **row 47, col a** / short leg (-) → **minus (-) rail**

---

### LED #4 — RING (GPIO 12)

GPIO 12 is on the **left side**, two pins above GPIO 13. Same pattern:

1. **Wire:** GPIO 12's row (left side, col a) → **row 49, col d**
2. **Resistor:** **row 49, col c** → **row 50, col c**
3. **LED:** long leg (+) → **row 50, col a** / short leg (-) → **minus (-) rail**

---

### LED #5 — PINKY (GPIO 14)

GPIO 14 is on the **left side**, above GPIO 12. Same pattern:

1. **Wire:** GPIO 14's row (left side, col a) → **row 52, col d**
2. **Resistor:** **row 52, col c** → **row 53, col c**
3. **LED:** long leg (+) → **row 53, col a** / short leg (-) → **minus (-) rail**

---

## Final Check

After wiring all 5 LEDs, you should have:

- [x] 5 jumper wires — each connecting a GPIO pin row to rows 40, 43, 46, 49, 52
- [x] 5 resistors — each bridging two rows (e.g. 40→41, 43→44, etc.)
- [x] 5 LEDs — all with long legs (+) in **column A**, all short legs (-) in the **LEFT minus (-) rail**
- [x] USB cable plugged in from ESP32 to PC
- [x] Nothing plugged into GPIO 1/TX, 3/RX, or GPIO 0

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
