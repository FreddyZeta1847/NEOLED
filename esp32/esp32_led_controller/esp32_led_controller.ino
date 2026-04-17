// ============================================================
// NEOLED - ESP32 LED Controller
// ============================================================
// This sketch listens for 5-character messages over USB serial.
// Each character controls one LED: '1' = ON, '0' = OFF.
// Example: "10110" turns on Thumb, Middle, Ring LEDs.
// ============================================================

// --- PIN SETUP ---

// We create an array (a list) of 5 GPIO pin numbers.
// Each position in the array matches a finger:
//   Position 0 = Thumb  = GPIO 2
//   Position 1 = Index  = GPIO 4
//   Position 2 = Middle = GPIO 13
//   Position 3 = Ring   = GPIO 12
//   Position 4 = Pinky  = GPIO 14
int ledPins[5] = {2, 4, 13, 12, 14};

// How many LEDs we have. We use this instead of writing "5"
// everywhere, so if we ever change the number, we only change
// it in one place.
int numLeds = 5;

// --- SETUP ---
// This function runs ONCE when the ESP32 starts up (or resets).
void setup() {

  // Start serial communication at 115200 "baud" (speed).
  // Baud = how many bits per second travel over the USB cable.
  // Both the ESP32 and the Python script must use the same speed,
  // otherwise they can't understand each other.
  Serial.begin(115200);

  // Configure each GPIO pin as an OUTPUT.
  // OUTPUT means the pin will SEND electricity out (to power the LED).
  // The opposite would be INPUT (reading a sensor or button).
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
  }

  // Turn all LEDs OFF at startup, so we start from a clean state.
  // LOW = no electricity on the pin = LED off.
  for (int i = 0; i < numLeds; i++) {
    digitalWrite(ledPins[i], LOW);
  }

  // Blink the built-in LED (GPIO 2, which is also our Thumb LED)
  // 3 times to show that the ESP32 has started successfully.
  // This is a visual confirmation that the firmware is running.
  for (int j = 0; j < 3; j++) {
    digitalWrite(2, HIGH);   // HIGH = send electricity = LED ON
    delay(200);              // Wait 200 milliseconds (0.2 seconds)
    digitalWrite(2, LOW);    // LOW = no electricity = LED OFF
    delay(200);              // Wait again before next blink
  }

  // Send a message over serial to tell the PC we're ready.
  // You can see this message in the Arduino Serial Monitor.
  Serial.println("NEOLED ready");
}

// --- LOOP ---
// This function runs OVER AND OVER, forever, after setup() finishes.
// It checks if there's a message from the PC, and if so, acts on it.
void loop() {

  // Serial.available() returns how many bytes (characters) are
  // waiting in the serial buffer (the inbox). If it's >= 5,
  // that means a complete message has arrived.
  if (Serial.available() >= 5) {

    // Read exactly 5 characters into a char array (a small text box).
    // Each character will be either '0' or '1'.
    char buffer[6];  // 6 because C strings need an extra spot for '\0' (end marker)

    // Serial.readBytes reads exactly 5 characters from the serial
    // buffer and stores them in our array.
    Serial.readBytes(buffer, 5);

    // Add the end-of-string marker so we can treat it as text.
    buffer[5] = '\0';

    // Now process each character in the message.
    // buffer[0] = Thumb, buffer[1] = Index, buffer[2] = Middle, etc.
    for (int i = 0; i < numLeds; i++) {

      // If the character is '1', turn the LED ON (HIGH).
      // If it's anything else ('0'), turn the LED OFF (LOW).
      if (buffer[i] == '1') {
        digitalWrite(ledPins[i], HIGH);
      } else {
        digitalWrite(ledPins[i], LOW);
      }
    }

    // Send back "OK" so the Python script knows we received
    // and processed the message successfully.
    Serial.println("OK");

    // Clear any leftover bytes in the serial buffer.
    // This prevents old partial messages from piling up
    // if the PC sends data faster than we process it.
    while (Serial.available()) {
      Serial.read();
    }
  }
}
