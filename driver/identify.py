#!/usr/bin/env python3

"""
Ask the OWON device to identify itself using the USB serial driver.

This simple script issues the *IDN? SCPI command to the serial device and
reads the response. It uses the python serial library.
"""

import sys
import serial

def main(argv: list[str]):
    if len(argv) != 2:
        print("Usage: identify.py <device>")
        sys.exit(1)

    device = sys.argv[1]

    # You should use a serial library, since it will automatically do the
    # termios configuration, including disabling echo and line ending
    # modification.
    with serial.Serial(device, timeout=1) as ser:
        ser.write(b"*IDN?\n")
        ser.flush()
        response = ser.read(1024)
        print(f"Identity: {response.decode()}")

if __name__ == "__main__":
    main(sys.argv)
