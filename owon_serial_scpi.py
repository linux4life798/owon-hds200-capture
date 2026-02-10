#!/usr/bin/env python3
"""
OWON Serial SCPI Interface
Provides low-level serial communication with OWON devices using the SCPI protocol.

Linux kernel support for OWON oscilloscopes was added to the usb-serial-simple
driver and was merged into mainline on April 25, 2025.
This means that you can now interface with USB OWON devices over a simple serial
interface, say /dev/ttyUSB0, rather than raw libusb.

https://github.com/torvalds/linux/commit/4cc01410e1c1dd075df10f750775c81d1cb6672b
"""

import argparse

import serial

from owon_scpi_base import OwonSCPIBase


class OwonSerialSCPI(OwonSCPIBase):
    """
    Interface for communicating with OWON devices over a serial node using SCPI.

    The default serial node is expected to be backed by a Linux USB serial driver.
    """

    DEFAULT_DEVICE = "/dev/ttyUSB0"

    def __init__(self, device: str = DEFAULT_DEVICE, timeout: int = 1000) -> None:
        """Open a serial-backed SCPI transport.

        Args:
            device: Serial node path (typically `/dev/ttyUSB0`).
            timeout: IO timeout in milliseconds.
        """
        super().__init__(timeout=timeout, max_response_size=2048)
        self._device = device
        # Baud is intentionally left at pyserial defaults. The backing device is
        # USB and does not need meaningful UART timing configuration.
        self._serial = serial.Serial(device, timeout=timeout / 1000.0)

    def _write_bytes(self, data: bytes) -> None:
        """Write a command payload to the serial device."""
        self._serial.write(data)
        self._serial.flush()

    def _read_bytes(self, size: int, timeout_ms: int) -> bytes:
        """Read up to `size` bytes with timeout behavior matching USB transport."""
        self._serial.timeout = timeout_ms / 1000.0
        data = self._serial.read(size)
        if not data:
            raise TimeoutError("Timeout")
        return data

    def close(self) -> bool:
        """Close the serial device if it is open."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            return True
        return False

    @classmethod
    def add_cli_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Register serial-specific CLI arguments."""
        parser.add_argument("--device", default=cls.DEFAULT_DEVICE)

    @classmethod
    def from_cli_args(cls, args: argparse.Namespace) -> "OwonSerialSCPI":
        """Construct a serial transport from parsed CLI arguments."""
        return cls(device=args.device)


def main() -> None:
    """Run the shared interactive SCPI CLI over serial transport."""
    OwonSerialSCPI.main()


if __name__ == "__main__":
    main()
