#!/usr/bin/env python3
"""
OWON USB SCPI Interface
Provides low-level USB communication with OWON devices using the SCPI protocol.

https://github.com/pyusb/pyusb/blob/master/docs/faq.rst
https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
"""

import usb.core
import usb.util
import time
import json


class OwonUSBSCPI:
    """
    Interface for communicating with OWON devices over USB using SCPI protocol.
    This class handles the low-level USB communication and basic SCPI command formatting.
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
        timeout: int = 2000,
    ) -> None:
        """Initialize the USB-SCPI interface.

        Args:
            vendor_id: USB vendor ID
            product_id: USB product ID
            usb_ep_out: Endpoint for sending commands
            usb_ep_in: Endpoint for receiving data
            timeout: Command timeout in milliseconds
        """
        self.usb_vendor_id = usb_vendor_id
        self.usb_product_id = usb_product_id
        self.usb_ep_out = usb_ep_out
        self.usb_ep_in = usb_ep_in
        self.timeout = timeout
        self.device = None
        self._connect()

    def _connect(self) -> bool:
        """Connect to the USB device."""
        # Find the first device with correct vendor/product ID.
        self.device = usb.core.find(
            idVendor=self.usb_vendor_id, idProduct=self.usb_product_id
        )

        if self.device is None:
            raise ValueError(
                f"Device with vendor ID {self.usb_vendor_id:04x} and product ID {self.usb_product_id:04x} not found."
            )

        print("# Reset")
        self.device.reset()
        print("# Reset - finished")

        # Detach kernel driver if active.
        print("# Check kernel")
        if self.device.is_kernel_driver_active(0):
            print("# Remove kernel")
            self.device.detach_kernel_driver(0)

        # Set first and only configuration.
        print("# Set configuration")
        self.device.set_configuration()
        print("# Set configuration - finished")
        inf = self.device.get_active_configuration()
        inf0 = inf[(0,0)]

        print("# Claim interface")
        usb.util.claim_interface(self.device, inf0)
        print("# Claim interface - finished")

        # self.device.reset()

    def send_command(self, command: str) -> bool:
        """Send a SCPI command to the device.

        Args:
            command: The SCPI command to send

        Returns:
            True if command was sent successfully, False otherwise.
        """
        try:
            # Ensure command ends with newline
            if not command.endswith("\n"):
                command += "\n"

            # Convert to bytes and send to EP_OUT
            data = command.encode("ascii")
            self.device.write(self.usb_ep_out, data, self.timeout)
            return True

        except usb.core.USBError as e:
            print(f"Error sending command: {e}")
            return False

    def read_response(self, length: int = 4096) -> bytes | None:
        """Read a response from the device.

        Args:
            length: Maximum number of bytes to read

        Returns:
            Response from the device, or None if error.
        """
        try:
            data = self.device.read(self.usb_ep_in, length, self.timeout)
            # print(f"Received {len(data)} bytes.")
            return bytes(data)

        except usb.core.USBError as e:
            if e.args[0] == 110:  # Operation timed out
                return ""
            print(f"Error reading response: {e}")
            return None

    def read_response_chunked(self, length: int = 4096) -> bytes | None:
        """Read a response from the device in chunks of 64 bytes.

        Args:
            length: Maximum number of bytes to read

        Returns:
            Response from the device, or None if error.
        """
        try:
            data = bytearray()
            bytes_read = 0
            while bytes_read < length:
                chunk = self.device.read(self.usb_ep_in, min(64, length - bytes_read), self.timeout)
                data.extend(chunk)
                bytes_read += len(chunk)
                print(f"Received {len(chunk)} bytes, total {bytes_read} bytes.")
                if len(chunk) < 64:
                    break
            return bytes(data)

        except usb.core.USBError as e:
            if e.args[0] == 110:  # Operation timed out
                return b""
            print(f"Error reading response: {e}")
            return None

    def query_binary(self, command: str, length: int = 4096) -> bytes | None:
        """Send a command and return the response.

        Args:
            command: The SCPI command to send
            length: Maximum number of bytes to read

        Returns:
            Response from the device, or None if error.
        """
        if self.send_command(command):
            return self.read_response(length)
            # return self.read_response_chunked(length)
        return None

    def query(self, command: str, length: int = 4096) -> str | None:
        """Send a command and return the response.

        Args:
            command: The SCPI command to send
            length: Maximum number of bytes to read

        Returns:
            Response from the device, or None if error.
        """

        resp = self.query_binary(command=command, length=length)
        if resp:
            return resp.decode("ascii", errors="backslashreplace").strip()
        return None

    def close(self) -> bool:
        """Close the connection to the device.

        Returns:
            True if the connection was closed successfully, False otherwise.
        """
        if self.device:
            usb.util.dispose_resources(self.device)
            self.device = None
            return True
        return False


if __name__ == "__main__":
    import sys

    owon = OwonUSBSCPI()

    if not owon.device:
        print("Failed to connect to the device.")
        sys.exit(1)

    # Example usage
    try:
        print("Connected to OWON device.")
        response = owon.query("*IDN?")
        print(f"Device ID: {response}")

        print_modes = ["str", "json", "bin", "int"]
        print_mode = "str"
        while True:
            cmd = input("> ")
            if cmd in print_modes:
                print_mode = cmd
                print(f"# Print mode changed to {print_mode}.")
                continue

            if cmd == "read":
                print(owon.read_response())

            if print_mode == "str":
                print(owon.query(cmd, 40960))
            elif print_mode == "json":
                try:
                    response = owon.query(cmd)
                    json_data = json.loads(response)
                    print(json.dumps(json_data, indent=4))
                except json.JSONDecodeError:
                    print("Failed to decode JSON response.")
                    print(f"Raw Response:\n{response}")
            elif print_mode == "bin":
                bdata = owon.query_binary(cmd)
                print(" ".join(f"{byte:02x}" for byte in bdata))
            elif print_mode == "int":
                bdata = owon.query_binary(cmd)
                print(" ".join(str(int.from_bytes([byte], byteorder='big', signed=True)) for byte in bdata))

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        owon.close()
