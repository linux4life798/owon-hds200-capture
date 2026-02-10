#!/usr/bin/env python3
"""
Shared SCPI transport abstractions and utilities for OWON devices.
"""

import argparse
import json
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Literal, Protocol, Self, overload

import utils


class OwonSCPI(Protocol):
    """Minimal SCPI interface used by higher-level device logic."""

    def set(self, command: str) -> bool: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["bin"],
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | None: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["str"] = "str",
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> str | None: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["int8"],
        length_header: Literal[True],
        bypass_length_checks: bool = False,
    ) -> list[int] | None: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["json"],
        length_header: Literal[True],
        bypass_length_checks: bool = False,
    ) -> Any | None: ...

    def query(
        self,
        command: str,
        data_type: Literal["str", "bin", "int8", "json"] = "str",
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | str | list[int] | Any | None: ...

    def close(self) -> bool: ...


class OwonSCPIBase(ABC):
    """Shared SCPI command/query behavior and common CLI."""

    def __init__(self, timeout: int = 1000, max_response_size: int = 2048) -> None:
        """Initialize shared SCPI transport settings.

        Args:
            timeout: Default IO timeout in milliseconds.
            max_response_size: Upper bound for one transport read operation.
        """
        self._timeout = timeout
        self.max_response_size = max_response_size

    @abstractmethod
    def _write_bytes(self, data: bytes) -> None:
        """Write bytes to the underlying transport."""

    @abstractmethod
    def _read_bytes(self, size: int, timeout_ms: int) -> bytes:
        """Read up to `size` bytes from the underlying transport."""

    @abstractmethod
    def close(self) -> bool:
        """Close the transport."""

    def _send_command(self, command: str) -> bool:
        """Send a SCPI command to the device."""
        try:
            if not command.endswith("\n"):
                command += "\n"
            self._write_bytes(command.encode("ascii"))
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    @overload
    def _read_response(
        self,
        binary: Literal[True],
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
        """Read, frame-parse, and decode a response packet from the transport.

        Args:
            binary: Return bytes directly when True; ASCII text when False.
            length_header: Expect little-endian 4-byte length prefix.
            bypass_length_checks: Skip framing validation (debug use).

        Notes:
            We assume that all large reads will succeed.
        """
        # It is still faster to read the largest block of data in one shot,
        # so we do not read the 4 byte header separately.
        try:
            data = self._read_bytes(self.max_response_size, self._timeout)
            if not data:
                raise TimeoutError("Timeout")
            if not bypass_length_checks:
                data = parse_and_validate_packet(data, length_header)
            if length_header and bypass_length_checks:
                data = data[4:]
        except TimeoutError:
            print("Timeout")
            return None

        if binary:
            return data
        return data.decode("ascii")

    def set(self, command: str) -> bool:
        """Send a command to the device.

        TODO: Add the ability to wait/poll until the setting takes effect.
        """
        return self._send_command(command)

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["bin"],
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | None: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["str"] = "str",
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> str | None: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["int8"],
        length_header: Literal[True],
        bypass_length_checks: bool = False,
    ) -> list[int] | None: ...

    @overload
    def query(
        self,
        command: str,
        data_type: Literal["json"],
        length_header: Literal[True],
        bypass_length_checks: bool = False,
    ) -> Any | None: ...

    def query(
        self,
        command: str,
        data_type: Literal["str", "bin", "int8", "json"] = "str",
        length_header: bool = False,
        bypass_length_checks: bool = False,
    ) -> bytes | str | list[int] | Any | None:
        """Send a command and return the response.

        TODO: Add ability to handle concatenated commands with multiple responses.
        """
        if data_type == "int8" and not length_header:
            raise ValueError("int8 data type requires length_header=True")

        if not self._send_command(command):
            return None
        # The time between sending the command and receiving the response is
        # somewhat delicate. Adding any delays will cause the response to be
        # missing some initial data. Starting the receive after sending the
        # command does create a race condition, but luckily the oscope device
        # is slow and takes more than 10ms to start responding.

        if data_type in ["str", "json"]:
            resp = self._read_response(
                binary=False,
                length_header=length_header,
                bypass_length_checks=bypass_length_checks,
            )
            if not resp:
                return None
            if data_type == "str":
                return resp
            return json.loads(resp)

        if data_type in ["bin", "int8"]:
            resp = self._read_response(
                binary=True,
                length_header=length_header,
                bypass_length_checks=bypass_length_checks,
            )
            if not resp:
                return None
            if data_type == "bin":
                return resp
            return [
                int.from_bytes([byte], byteorder="big", signed=True) for byte in resp
            ]

        raise ValueError(f"Unsupported data_type: {data_type}")

    @classmethod
    def add_cli_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Allow transport implementations to register CLI args."""
        del parser

    @classmethod
    @abstractmethod
    def from_cli_args(cls, args: argparse.Namespace) -> Self:
        """Create a transport instance from parsed CLI args."""

    @classmethod
    def main(cls) -> None:
        """Common interactive CLI entry point."""
        parser = argparse.ArgumentParser(description=f"{cls.__name__} interactive CLI")
        cls.add_cli_arguments(parser)
        args = parser.parse_args()
        owon = cls.from_cli_args(args)
        owon.run_cli_loop()

    def run_cli_loop(self) -> None:
        """Run the shared interactive debug CLI for any transport backend."""
        print("Connected to OWON device.")
        resp = self.query("*IDN?")
        print(f"Device ID: {resp}")

        print_modes: list[str] = ["str", "json", "bin", "int"]
        print_mode: str = "str"

        try:
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
                if cmd == "read":
                    print(self._read_response())
                    continue
                if cmd == "values":
                    query_head = ":DATa:WAVe:SCReen:head?"
                    query_data_ch1 = ":DATa:WAVe:SCReen:ch1?"
                    query_data_ch2 = ":DATa:WAVe:SCReen:ch2?"

                    head = self.query(query_head, data_type="json", length_header=True)
                    response_data_ch1 = self.query(
                        query_data_ch1, data_type="int8", length_header=True
                    )
                    response_data_ch2 = self.query(
                        query_data_ch2, data_type="int8", length_header=True
                    )
                    if not head or not response_data_ch1 or not response_data_ch2:
                        print("Failed to read data from the device.")
                        continue

                    values: list[list[int]] = [response_data_ch1, response_data_ch2]
                    print(f"Received {len(values[0])} values for ch1.")
                    print(f"Received {len(values[1])} values for ch2.")

                    ch_probe_attenuation = list[float]([0.0, 0.0])
                    ch_probe_scale = list[float]([0.0, 0.0])
                    ch_offset = list[int]([0, 0])
                    ch_display = list[bool]([False, False])

                    for ch in head["CHANNEL"]:
                        if ch["NAME"] == "CH1":
                            index = 0
                        elif ch["NAME"] == "CH2":
                            index = 1
                        else:
                            raise ValueError(f"Unknown channel: {ch['NAME']}")

                        probe = ch["PROBE"]
                        scale = ch["SCALE"]
                        offset = ch["OFFSET"]
                        display = ch["DISPLAY"]
                        print(
                            f"{ch['NAME']} Probe: {probe}, Scale: {scale}, "
                            f"Offset: {offset}, Display: {display}"
                        )

                        ch_probe_attenuation[index], units = utils.split_float_units(
                            probe
                        )
                        assert units == "X"
                        ch_probe_scale[index], units = utils.split_float_units(scale)
                        if units == "kV":
                            ch_probe_scale[index] *= 1000
                        elif units == "V":
                            ch_probe_scale[index] *= 1
                        elif units == "mV":
                            ch_probe_scale[index] /= 1000
                        elif units == "uV":
                            ch_probe_scale[index] /= 1000000
                        else:
                            raise ValueError(f"Unknown unit: {units}")
                        ch_offset[index] = int(offset)
                        ch_display[index] = display == "ON"
                        print(
                            f"{ch['NAME']} calculated scale is {ch_probe_scale[index]}V"
                        )

                    ch1_voltage = data_screen_values_to_voltage(
                        values[0],
                        ch_probe_attenuation[0],
                        ch_probe_scale[0],
                        ch_offset[0],
                    )
                    ch2_voltage = data_screen_values_to_voltage(
                        values[1],
                        ch_probe_attenuation[1],
                        ch_probe_scale[1],
                        ch_offset[1],
                    )

                    if ch_display[0]:
                        print("Channel 1:")
                        for row in list_reshape(ch1_voltage, 20):
                            print(" ".join(f"{v : .3f}V" for v in row))
                    else:
                        print("Channel 1 is off.")
                    if ch_display[1]:
                        print("Channel 2:")
                        for row in list_reshape(ch2_voltage, 20):
                            print(" ".join(f"{v : .3f}V" for v in row))
                    else:
                        print("Channel 2 is off.")
                    continue
                if cmd == "benchmark":
                    print("Benchmark downloading one screen of data.")
                    # Benchmark how long it takes to transfer one screen of data
                    # for a single channel.
                    query = ":DATa:WAVe:SCReen:CH1?"
                    start = time.time()
                    for _ in range(100):
                        self.query(query, data_type="bin", length_header=True)
                    end = time.time()
                    print(
                        f"It takes {((end - start) / 100) * 1000 : .3f} ms per screen."
                    )
                    continue

                if print_mode == "str":
                    print(
                        self.query(
                            cmd,
                            data_type="str",
                            length_header=False,
                            bypass_length_checks=True,
                        )
                    )
                elif print_mode == "json":
                    try:
                        # The query will consume the first 4 bytes as data length.
                        resp = self.query(cmd, data_type="json", length_header=True)
                        print(json.dumps(resp, indent=4))
                    except json.JSONDecodeError:
                        print("Failed to decode JSON response.")
                elif print_mode == "bin":
                    # This is purely for debugging, so do not remove the 4 byte
                    # length header. This will cause a warning, given that it can't
                    # find a newline.
                    resp = self.query(
                        cmd,
                        data_type="bin",
                        length_header=False,
                        bypass_length_checks=True,
                    )
                    if not resp:
                        print("Failed to read data from the device.")
                        continue
                    print(f"Received {len(resp)} bytes.")
                    if len(resp) >= 4:
                        attempted_length = int.from_bytes(
                            resp[:4], byteorder="little", signed=False
                        )
                        print(f"First 4 bytes is value {attempted_length}.")
                    # Print hex values with 32 bytes on one line. Add extra space
                    # between each set of 4 bytes.
                    for row in list_reshape(resp, 32):
                        for word in list_reshape(row, 4):
                            print(" ".join(f"{byte:02x}" for byte in word), end="  ")
                        print()
                elif print_mode == "int":
                    # The query will consume the first 4 bytes as data length.
                    resp = self.query(cmd, data_type="int8", length_header=True)
                    if not resp:
                        print("Failed to read data from the device.")
                        continue
                    print(f"Received {len(resp)} 8-bit ints.")
                    print(" ".join(str(v) for v in resp))
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.close()


def parse_and_validate_packet(data: bytes, length_header: bool = False) -> bytes:
    """Parse a response packet and validate its data length.

    The primary function is to strip the 4 byte packet length header, which is
    used by select commands, and remove the final newline character from other
    ascii-only commands. The additional validation is to ensure program
    correctness and to detect device issues.

    Args:
        data: The packet to parse and validate.
        length_header: When True, expect and use a 4-byte length header.
            Otherwise, expect and use a newline character to denote the packet
            end.

    Returns:
        The stripped data from the packet.
    """
    UNREASONABLE_PACKET_HEADER_LENGTH = 4096

    if length_header:
        # The first 4 bytes of the packet are the unsigned integer length of
        # the remaining packet data, excluding the header itself.
        if len(data) < 4:
            raise ValueError("Received insufficient data to parse length header.")
        hdr_length = int.from_bytes(data[:4], byteorder="little", signed=False)

        if hdr_length == 0:
            raise ValueError("Received packet header of 0.")
        if hdr_length > UNREASONABLE_PACKET_HEADER_LENGTH:
            raise ValueError(
                f"Received packet header length, {hdr_length}, is unreasonably large."
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
                f"packet header specified ({hdr_length}). This may be a program bug."
            )
        data = data[4 : 4 + hdr_length]
        assert len(data) > 0
    else:
        newline = data.find(b"\n")
        if newline == -1:
            raise ValueError("No final newline found in response packet.")
        if newline != len(data) - 1:
            print(
                f"Received {len(data) - newline} extra bytes past the first response "
                f"newline (index {newline}). This may be a program bug."
            )
        data = data[:newline]
        assert data.find(b"\n") == -1
    return data


def list_reshape[T](data: list[T], width: int) -> list[list[T]]:
    """Reshape a list into a list of lists, each with a fixed width."""
    return [data[i : i + width] for i in range(0, len(data), width)]


@overload
def data_screen_values_to_voltage(
    values: int,
    probe_attenuation_factor: int,
    channel_scale: float,
    channel_offset: int,
) -> float: ...


@overload
def data_screen_values_to_voltage(
    values: list[int],
    probe_attenuation_factor: int,
    channel_scale: float,
    channel_offset: int,
) -> list[float]: ...


def data_screen_values_to_voltage(
    values: int | list[int],
    probe_attenuation_factor: int,
    channel_scale: float,
    channel_offset: int,
) -> float | list[float]:
    """Convert screen values to voltages.

    Args:
        values: The screen values to convert.
        probe_attenuation_factor: The probe attenuation factor.
        channel_scale: The channel scale in volts (units already applied).
        channel_offset: The channel offset.
    """
    real_scale = probe_attenuation_factor * channel_scale
    convert: Callable[[int], float] = (
        lambda value: (value - channel_offset) * real_scale * 4 / 100
    )
    if isinstance(values, int):
        return convert(values)
    return [convert(value) for value in values]
