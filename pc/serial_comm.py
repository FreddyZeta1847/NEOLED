"""
serial_comm.py — Handles USB serial communication with the ESP32.

This module finds the ESP32 on a COM port, opens the connection,
and provides a function to send finger states like "10110".
"""

# 'serial' is the pyserial library. It lets Python talk to devices
# connected via USB serial (like our ESP32).
import serial

# serial.tools.list_ports gives us a function to scan all available
# COM ports on the computer, so we can find the ESP32 automatically.
import serial.tools.list_ports

# 'time' lets us use sleep() to pause the program — needed to wait
# for the ESP32 to reboot after we open the serial connection.
import time


def find_esp32_port():
    """
    Scans all COM ports on the computer and returns the first one
    that looks like an ESP32 (based on the USB chip name).

    Returns the port name (e.g. "COM3") or None if not found.
    """

    # list_ports.comports() returns a list of all serial ports
    # currently connected to the computer. Each port has attributes
    # like .device (the name, e.g. "COM3"), .description (human
    # readable name), and .hwid (hardware ID).
    ports = serial.tools.list_ports.comports()

    for port in ports:
        desc = port.description.lower()

        # The ESP32 board uses a USB-to-serial chip. Common ones are:
        # - CH340 / CH341 (used by most Freenove boards)
        # - CP210x (used by some other ESP32 boards)
        # - FTDI (less common for ESP32)

        if "ch340" in desc or "cp210" in desc or "ftdi" in desc or "serial" in desc:
            return port.device

    return None


def connect(port=None, baud=115200):
    """
    Opens a serial connection to the ESP32.

    Parameters:
    - port: The COM port name (e.g. "COM3"). If None, we auto-detect.
    - baud: Communication speed. Must match the ESP32 firmware (115200).

    Returns a serial.Serial object (the open connection), or None if failed.
    """

    # If no port was given, try to find the ESP32 automatically.
    if port is None:
        port = find_esp32_port()
        if port is None:
            print("ERROR: Could not find ESP32. Is it plugged in?")
            return None

    print(f"Connecting to ESP32 on {port}...")

    # serial.Serial() opens the connection. Parameters:
    # - port: which COM port to use
    # - baudrate: speed (must match ESP32's Serial.begin(115200))
    # - timeout: how long to wait (in seconds) for data before giving up.
    #   1 second is enough — if the ESP32 doesn't reply in 1s, something's wrong.
    connection = serial.Serial(port=port, baudrate=baud, timeout=1)

    # When we open a serial connection to the ESP32, it reboots automatically.
    # We wait 2 seconds for it to finish booting and run setup().
    time.sleep(2)

    # After rebooting, the ESP32 sends "NEOLED ready" via Serial.println().

    startup_msg = connection.read_all().decode("utf-8").strip()

    if "ready" in startup_msg.lower():
        print(f"ESP32 connected! Message: {startup_msg}")
    else:
        print(f"ESP32 connected on {port} (no ready message received)")

    return connection


def send_finger_state(connection, state):
    """
    Sends a 5-character finger state string to the ESP32.

    Parameters:
    - connection: the serial.Serial object from connect()
    - state: a string like "10110" (1=finger up, 0=finger down)
             Order: Thumb, Index, Middle, Ring, Pinky

    The ESP32 will set each LED on/off based on this string.
    """

    # encode("utf-8") converts the Python string to raw bytes,
    # because serial communication works with bytes, not text.
    connection.write(state.encode("utf-8"))

    # flush() forces all buffered data to be sent immediately,
    # rather than waiting for the buffer to fill up. This ensures
    # the ESP32 gets our message right away with no delay.
    connection.flush()


def disconnect(connection):
    """
    Closes the serial connection cleanly.

    Parameters:
    - connection: the serial.Serial object to close
    """

    if connection and connection.is_open:

        send_finger_state(connection, "00000")

        connection.close()
        print("ESP32 disconnected.")
