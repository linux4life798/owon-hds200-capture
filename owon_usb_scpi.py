#!/usr/bin/env python3
"""
OWON USB SCPI Interface
Provides low-level USB communication with OWON devices using the SCPI protocol.

This library also provides a simple CLI for interacting with the device.

https://github.com/pyusb/pyusb/blob/master/docs/faq.rst
https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
"""

from typing import Literal, overload
import usb.core
import usb.util


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
        timeout: int = 1000,
    ) -> None:
        """Initialize the USB-SCPI interface and connect to the device.

        Args:
            usb_vendor_id: USB vendor ID
            usb_product_id: USB product ID
            usb_ep_out: Endpoint for sending commands
            usb_ep_in: Endpoint for receiving data
            timeout: Command timeout in milliseconds
        """

        self._timeout = timeout
        self._device = None
        self.max_response_size = 2048
        """The device will claim that the maximum USB packet size is 64 bytes,
        but it will happily transfer 600+ bytes in one IN transaction.
        Considering this, we use one large size to reduce transaction overhead.
        """

        # Find the first device with correct vendor/product ID.
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

    def _send_command(self, command: str) -> bool:
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
            self._usb_out.write(data)
            return True

        except usb.core.USBError as e:
            print(f"Error sending command: {e}")
            return False

    @overload
    def _read_response(
        self,
        binary: Literal[True] = True,
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | None: ...

    @overload
    def _read_response(
        self,
        binary: Literal[False] = False,
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> str | None: ...

    def _read_response(
        self,
        binary: bool = False,
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | str | None:
        """Read a response from the device.

        Args:
            binary: Whether the response is binary.
                    If `True`, the response is returned as a bytes object.
                    If `False`, the response is returned as an str.
            length_header: Whether to expect and use the 4-byte length header
            bypass_length_checks: If enabled, all data length checks are
                disabled and the full packet is returned.

        Returns:
            Response from the device, or None if error.

        Notes:
            We assume that all large read will succeed.
        """

        # It is still faster to read the largest block of data in one shot,
        # so we do not read the 4 byte header separately.
        try:
            # data = bytes(self._usb_in.read(self.max_response_size, self._timeout))
            data = bytes(self._usb_in.read(604, self._timeout))
            # print(f"Received {len(data)} bytes.")
            if not bypass_length_checks:
                data = _parse_and_validate_packet(data, length_header)

        except usb.core.USBTimeoutError:
            print("Timeout")
            return None
        # Allow usb.core.USBError (include IOError) to be raised.

        if binary:
            return data
        return data.decode("ascii")

    def set(self, command: str) -> bool:
        """Send a command to the device.

        Args:
            command: The SCPI command to send

        Returns:
            True if command was sent successfully, False otherwise.
        """
        return self._send_command(command)

    @overload
    def query(
        self,
        command: str,
        binary: Literal[True] = True,
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | None: ...

    @overload
    def query(
        self,
        command: str,
        binary: Literal[False] = False,
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> str | None: ...

    def query(
        self,
        command: str,
        binary: bool = False,
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | str | None:
        """Send a command and return the response.

        Args:
            command: The SCPI command to send
            length: Maximum number of bytes to read
            bypass_length_checks: If enabled, all data length checks are
                disabled and the full packet is returned.

        Returns:
            Response from the device, or None if error.
        """

        if not self._send_command(command):
            return None
        # The time between sending the command and receiving the response is
        # somewhat delicate. Adding any delays will cause the response to be
        # missing some initial data. Starting the receive after sending the
        # command does create a race condition, but luckily the oscope device
        # is slow and takes more than 10ms to start responding.
        return self._read_response(
            binary=binary,
            length_header=length_header,
            bypass_length_checks=bypass_length_checks,
        )

    def close(self) -> bool:
        """Close the connection to the device.

        Returns:
            True if the connection was closed successfully, False otherwise.
        """
        if self._device:
            usb.util.dispose_resources(self._device)
            self._device = None
            return True
        return False


def main() -> None:
    import sys
    import json
    import time

    owon = OwonUSBSCPI()

    if not owon._device:
        print("Failed to connect to the device.")
        sys.exit(1)

    try:
        print("Connected to OWON device.")
        resp = owon.query("*IDN?")
        print(f"Device ID: {resp}")

        print_modes: list[str] = ["str", "json", "bin", "int"]
        print_mode: str = "str"
        while True:
            cmd = input("> ")

            # Check for special commands.
            if cmd in print_modes:
                print_mode = cmd
                print(f"# Print mode changed to {print_mode}.")
                continue

            if cmd == "help":
                print("help - show this help")
                print("read - force a read of the response")
                print("values - dump oscope voltage values for ch1")
                print(
                    ",".join(print_modes),
                    " - set the print mode for subsequent command",
                )
                print("CTRL-C - exit")
                continue
            elif cmd == "read":
                print(owon._read_response())
                continue
            elif cmd == "values":
                query_head = ":DATa:WAVe:SCReen:head?"
                query_data_ch1 = ":DATa:WAVe:SCReen:ch1?"
                query_data_ch2 = ":DATa:WAVe:SCReen:ch2?"

                response_head = owon.query(query_head, binary=False, length_header=True)
                response_data_ch1 = owon.query(
                    query_data_ch1, binary=True, length_header=True
                )
                response_data_ch2 = owon.query(
                    query_data_ch2, binary=True, length_header=True
                )

                values = list[list[int]]()
                values.append(_parse_channel_data(response_data_ch1))
                values.append(_parse_channel_data(response_data_ch2))
                print(f"Received {len(values[0])} values for ch1.")
                print(f"Received {len(values[1])} values for ch2.")

                head = json.loads(response_head)
                probe_attenuation = list[float]([0.0, 0.0])
                probe_scale = list[float]([0.0, 0.0])

                for ch in head["CHANNEL"]:
                    if ch["NAME"] == "CH1":
                        index = 0
                    elif ch["NAME"] == "CH2":
                        index = 1
                    else:
                        raise ValueError(f"Unknown channel: {ch['NAME']}")

                    probe = ch["PROBE"]
                    scale = ch["SCALE"]
                    print(f"{ch['NAME']} Probe: {probe}, Scale: {scale}")

                    # Examples: 1X, 10X, 100X, 1000X, 10000X
                    probe_attenuation[index], units = _split_float_units(probe)
                    assert units == "X"
                    # Examples: 10mV, 200mV, 2V, 100V, 500V, 1kV, 10kV
                    probe_scale[index], units = _split_float_units(scale)
                    if units == "kV":
                        probe_scale[index] *= 1000
                    elif units == "V":
                        probe_scale[index] *= 1
                    elif units == "mV":
                        probe_scale[index] /= 1000
                    elif units == "uV":
                        probe_scale[index] /= 1000000
                    else:
                        raise ValueError(f"Unknown unit: {units}")
                    print(f"Calculated scale is {probe_scale[index]}")

                # probe_attenuation = list[float]()
                # probe_attenuation[0] = _split_float_units(head["CHANNEL"][0]["PROBE"])
                # probe_attenuation[1] = _split_float_units(head["CHANNEL"][1]["PROBE"])

                # ch1_probe_scale = head["CHANNEL"][0]["SCALE"]
                # ch2_probe_scale = head["CHANNEL"][1]["SCALE"]
                # atten = int(ch1_probe_atten[:-1])
                # if ch1_probe_scale.endswith("mV"):
                #     scale = float(ch1_probe_scale[:-2]) / 1000
                # elif ch1_probe_scale.endswith("uV"):
                #     scale = float(ch1_probe_scale[:-2]) / 1000000
                # else:
                #     scale = float(ch1_probe_scale[:-1])

                conversion = list[float]()
                conversion.append(float(probe_attenuation[0]) * probe_scale[0] * 4.0)
                conversion.append(float(probe_attenuation[1]) * probe_scale[1] * 4.0)
                print("Channel 1:")
                for row in _list_reshape(values[0], 20):
                    print(
                        " ".join(
                            f"{float(v) * conversion[0] / 100 : .3f}V" for v in row
                        )
                    )
                # print("Channel 2:")
                # for row in _list_reshape(values[1], 20):
                #     print(
                #         " ".join(
                #             f"{float(v) * conversion[1] / 100 : .3f}V" for v in row
                #         )
                #     )
                continue
            elif cmd == "benchmark":
                # Benchmark how long it takes to transfer one screen of data
                # for a single channel.
                query = ":DATa:WAVe:SCReen:CH1?"
                start = time.time()
                for i in range(100):
                    resp = owon.query(query, binary=True, length_header=True)
                end = time.time()
                print(f"It takes {((end - start) / 100) * 1000 : .3f} ms per screen.")
                continue

            # Interpret as an SCPI command with the given print mode.
            if print_mode == "str":
                print(owon.query(cmd))
            elif print_mode == "json":
                try:
                    # The query will consume the first 4 bytes as data length.
                    resp = owon.query(cmd, binary=False, length_header=True)
                    json_data = json.loads(resp)
                    print(json.dumps(json_data, indent=4))
                except json.JSONDecodeError:
                    print("Failed to decode JSON response.")
                    print(f"Raw Response:\n{resp}")
            elif print_mode == "bin":
                # This is purely for debugging, so do not remove the 4 byte
                # length header. This will cause a warning, given that it can't
                # find a newline.
                resp = owon.query(
                    cmd,
                    binary=True,
                    length_header=False,
                    bypass_length_checks=True,
                )
                print(f"Received {len(resp)} bytes.")
                if len(resp) >= 4:
                    attempted_length = int.from_bytes(
                        resp[:4], byteorder="little", signed=False
                    )
                    print(f"First 4 bytes is value {attempted_length}.")
                # Print hex values with 32 bytes on one line. Add extra space
                # between each set of 4 bytes.
                for row in _list_reshape(resp, 32):
                    for word in _list_reshape(row, 4):
                        print(" ".join(f"{byte:02x}" for byte in word), end="  ")
                    print()
            elif print_mode == "int":
                # The query will consume the first 4 bytes as data length.
                resp = owon.query(cmd, binary=True, length_header=True)
                print(f"Received {len(resp)} 8-bit ints.")
                print(
                    " ".join(
                        str(int.from_bytes([byte], byteorder="big", signed=True))
                        for byte in resp
                    )
                )

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        owon.close()


def _split_int_units(value: str) -> tuple[int, str]:
    """Parse a number with units from string as an int."""

    for i, c in enumerate(value):
        if not c.isdigit():
            return int(value[:i]), value[i:]
    return int(value), ""


def _split_float_units(value: str) -> tuple[float, str]:
    """Parse a number with units from string as a float."""

    for i, c in enumerate(value):
        if not c.isdigit() and c != ".":
            return float(value[:i]), value[i:]
    return float(value), ""


def _list_reshape(data: list[int], width: int) -> list[list[int]]:
    """Reshape a list of ints into a list of lists of ints, each with a width."""
    return [data[i : i + width] for i in range(0, len(data), width)]


def _parse_channel_data(response: bytes) -> list[int]:
    return [int.from_bytes([byte], byteorder="big", signed=True) for byte in response]


def _parse_and_validate_packet(data: bytes, length_header: bool = False) -> bytes:
    """Parse a response packet and validate its data length.

    The primary function is to strip the 4 byte packet length header, which is
    used by select commands, and remove the final newline character from other
    ascii only commands. The additional validation is to ensure program
    correctness and to detect device issues.

    Args:
        data: The packet to parse and validate
        length_header: When True, we expect and use a 4-byte length header.
            Otherwise, we expect and use a newline character to denote the
            packet end.

    Returns:
        The stripped data from the packet.
    """

    UNREASONABLE_PACKET_HEADER_LENGTH = 4096

    if length_header:
        # The first 4 bytes of the packet are the unsigned integer length of
        # the remaining packet data, excluding the header itself.
        if len(data) < 4:
            raise ValueError("Received insufficient data to parse length header.")
        hdr_length = int.from_bytes(
            data[:4],
            byteorder="little",
            signed=False,
        )
        print(f"Declared length of data is {hdr_length}.")

        if hdr_length == 0:
            raise ValueError("Received packet header of 0.")
        if hdr_length > UNREASONABLE_PACKET_HEADER_LENGTH:
            raise ValueError(
                f"Received packet header length, {hdr_length}, is unreasonably "
                "large."
            )
        # Received too little data compared to expected data.
        # This may require chunking smaller data reads.
        if len(data) - 4 < hdr_length:
            raise ValueError(
                f"Received {len(data)} bytes, but packet header "
                f"specified {hdr_length + 4} expected bytes. This may be a "
                "USB compatibility issue between device and program."
            )
        # Received too much data compared to expected data.
        if len(data) - 4 > hdr_length:
            print(
                f"Received {len(data) - 4 - hdr_length} extra bytes than the "
                f"packet header specified ({hdr_length}). This may be a "
                "program bug."
            )
        data = data[4 : 4 + hdr_length]
        assert len(data) > 0
    else:
        newline = data.find(b"\n")
        if newline == -1:
            raise ValueError("No final newline found in response packet.")
        if newline != len(data) - 1:
            print(
                f"Received {len(data) - newline} extra bytes past the "
                "first response newline (index {newline}). This may be "
                "a program bug."
            )
        data = data[:newline]
        assert data.find(b"\n") == -1
    return data


if __name__ == "__main__":
    main()
