#!/usr/bin/env python3
"""
OWON USB SCPI Interface
Provides low-level USB communication with OWON devices using the SCPI protocol.

This library also provides a simple CLI for interacting with the device.

https://github.com/pyusb/pyusb/blob/master/docs/faq.rst
https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
"""

import argparse

import usb.core
import usb.util

from owon_scpi_base import OwonSCPIBase


class OwonUSBSCPI(OwonSCPIBase):
    """
    Interface for communicating with OWON devices over USB using SCPI protocol.
    This class handles low-level USB communication and common SCPI semantics.
    """

    # OWON HDS272S
    HDS272S_USB_VENDOR_ID = 0x5345
    HDS272S_USB_PRODUCT_ID = 0x1234

    def __init__(
        self,
        usb_vendor_id: int = HDS272S_USB_VENDOR_ID,
        usb_product_id: int = HDS272S_USB_PRODUCT_ID,
        usb_ep_out: int = 0x01,
        usb_ep_in: int = 0x81,
        timeout: int = 1000,
    ) -> None:
        """Initialize USB transport and claim the configured interface/endpoints.

        Args:
            usb_vendor_id: USB vendor ID.
            usb_product_id: USB product ID.
            usb_ep_out: Bulk OUT endpoint address used for SCPI commands.
            usb_ep_in: Bulk IN endpoint address used for responses.
            timeout: IO timeout in milliseconds.

        Notes:
            max_response_size:
                The device will claim that the maximum USB packet size is 64
                bytes, but it will happily transfer 600+ bytes in one IN
                transaction. Considering this, we use one large size to reduce
                transaction overhead.
        """
        super().__init__(timeout=timeout, max_response_size=2048)

        # Find the first device with the correct vendor/product ID.
        self._device = usb.core.find(idVendor=usb_vendor_id, idProduct=usb_product_id)

        if self._device is None:
            raise ValueError(
                f"No device with vendor ID {usb_vendor_id:04x} and "
                f"product ID {usb_product_id:04x} found."
            )

        self._device.reset()

        # Detach kernel driver if active.
        if self._device.is_kernel_driver_active(0):
            self._device.detach_kernel_driver(0)

        # Set first and only configuration.
        self._device.set_configuration()
        inf = self._device.get_active_configuration()
        inf0 = inf[(0, 0)]
        self._usb_in = usb.util.find_descriptor(inf0, bEndpointAddress=usb_ep_in)
        self._usb_out = usb.util.find_descriptor(inf0, bEndpointAddress=usb_ep_out)

        if self._usb_in is None or self._usb_out is None:
            raise ValueError("Failed to find expected USB IN/OUT endpoints.")

    def _write_bytes(self, data: bytes) -> None:
        """Write bytes to the USB OUT endpoint."""
        self._usb_out.write(data)

    def _read_bytes(self, size: int, timeout_ms: int) -> bytes:
        """Read bytes from the USB IN endpoint."""
        try:
            return bytes(self._usb_in.read(size, timeout_ms))
        except usb.core.USBTimeoutError as e:
            raise TimeoutError("Timeout") from e

    def close(self) -> bool:
        """Close the connection to the device."""
        if self._device:
            usb.util.dispose_resources(self._device)
            self._device = None
            return True
        return False

    @classmethod
    def add_cli_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Register USB-specific CLI arguments."""
        parser.add_argument(
            "--vendor-id", type=lambda v: int(v, 0), default=cls.HDS272S_USB_VENDOR_ID
        )
        parser.add_argument(
            "--product-id", type=lambda v: int(v, 0), default=cls.HDS272S_USB_PRODUCT_ID
        )
        parser.add_argument("--ep-out", type=lambda v: int(v, 0), default=0x01)
        parser.add_argument("--ep-in", type=lambda v: int(v, 0), default=0x81)

    @classmethod
    def from_cli_args(cls, args: argparse.Namespace) -> "OwonUSBSCPI":
        """Construct a USB transport from parsed CLI arguments."""
        return cls(
            usb_vendor_id=args.vendor_id,
            usb_product_id=args.product_id,
            usb_ep_out=args.ep_out,
            usb_ep_in=args.ep_in,
        )


def main() -> None:
    """Run the shared interactive SCPI CLI over USB transport."""
    OwonUSBSCPI.main()


if __name__ == "__main__":
    main()
