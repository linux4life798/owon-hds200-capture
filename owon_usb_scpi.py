#!/usr/bin/env python3
"""
OWON USB SCPI Interface
Provides low-level USB communication with OWON devices using the SCPI protocol.

https://github.com/pyusb/pyusb/blob/master/docs/faq.rst
https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
"""

from typing import Any
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

        # print("# Reset")
        self.device.reset()
        # print("# Reset - finished")

        # Detach kernel driver if active.
        if self.device.is_kernel_driver_active(0):
            self.device.detach_kernel_driver(0)

        # Set first and only configuration.
        self.device.set_configuration()
        # inf = self.device.get_active_configuration()
        # inf0 = inf[(0,0)]

        # print("# Claim interface")
        # usb.util.claim_interface(self.device, inf0)
        # print("# Claim interface - finished")

        # self.device.reset()
        # time.sleep(2)

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
                chunk = self.device.read(
                    self.usb_ep_in, min(64, length - bytes_read), self.timeout
                )
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


def parse_head_json(response: bytes) -> Any:
    # Decode first 4 bytes as LSB packet length (unsigned).
    length = int.from_bytes(response[:4], byteorder="little", signed=False)
    print(f"Declared length is {length}.")
    json_str = response[4 : 4 + length].decode("ascii")
    json_data = json.loads(json_str)
    return json_data


def parse_channel_data(response: bytes) -> list[int]:
    # Decode first 4 bytes as LSB packet length (unsigned).
    length = int.from_bytes(response[:4], byteorder="little", signed=False)
    print(f"Declared length is {length}.")
    # json_str = response[4:4+length].decode("ascii")
    bdata = response[4:]
    return [int.from_bytes([byte], byteorder="big", signed=True) for byte in bdata]


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
            elif cmd == "values":
                query_head = ":DATa:WAVe:SCReen:head?"
                query_data_ch1 = ":DATa:WAVe:SCReen:ch1?"

                response_head = owon.query_binary(query_head)
                response_data_ch1 = owon.query_binary(query_data_ch1)

                head = parse_head_json(response_head)
                values = parse_channel_data(response_data_ch1)
                # 10X
                ch1_probe_atten = head["CHANNEL"][0]["PROBE"]
                # 200mV
                ch1_probe_scale = head["CHANNEL"][0]["SCALE"]

                atten = int(ch1_probe_atten[:-1])
                if ch1_probe_scale.endswith("mV"):
                    scale = float(ch1_probe_scale[:-2]) / 1000
                elif ch1_probe_scale.endswith("uV"):
                    scale = float(ch1_probe_scale[:-2]) / 1000000
                else:
                    scale = float(ch1_probe_scale[:-1])
                conversion = float(atten) * scale * 4.0
                print(" ".join(f"{float(v) * conversion / 100 : .3f}V" for v in values))
                continue

            if print_mode == "str":
                print(owon.query(cmd, 40960))
            elif print_mode == "json":
                try:
                    response = owon.query_binary(cmd)
                    # Decode first 4 bytes as LSB packet length (unsigned).
                    length = int.from_bytes(
                        response[:4], byteorder="little", signed=False
                    )
                    print(f"Declared length is {length}.")
                    json_str = response[4 : 4 + length].decode("ascii")
                    json_data = json.loads(json_str)
                    print(json.dumps(json_data, indent=4))
                except json.JSONDecodeError:
                    print("Failed to decode JSON response.")
                    print(f"Raw Response:\n{response}")
            elif print_mode == "bin":
                bdata = owon.query_binary(cmd)
                print(" ".join(f"{byte:02x}" for byte in bdata))
            elif print_mode == "int":
                response = owon.query_binary(cmd)
                # Decode first 4 bytes as LSB packet length (unsigned).
                length = int.from_bytes(response[:4], byteorder="little", signed=False)
                print(f"Declared length is {length}.")
                # json_str = response[4:4+length].decode("ascii")
                bdata = response[4:]
                print(
                    " ".join(
                        str(int.from_bytes([byte], byteorder="big", signed=True))
                        for byte in bdata
                    )
                )

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        owon.close()
