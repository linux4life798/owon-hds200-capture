#!/usr/bin/env python3
"""
OWON Oscilloscope Interface for the HDS200 series.

Provides high-level interaction with OWON oscilloscopes including data acquisition,
visualization, and instrument control.

https://files.owon.com.cn/software/Application/HDS200_Series_SCPI_Protocol.pdf
"""
# %% Imports and Definitions

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Self

import numpy as np
import pint
import plotly.graph_objects as go

from owon_scpi_base import OwonSCPIBase
from owon_serial_scpi import OwonSerialSCPI
from owon_usb_scpi import OwonUSBSCPI


@dataclass
class DeviceIdentification:
    manufacturer: str
    model: str
    serial_number: str
    firmware_version: str

    def __str__(self) -> str:
        return (
            f"Make/Model: {self.manufacturer} {self.model}\n"
            f"Serial:     {self.serial_number}\n"
            f"Firmware:   {self.firmware_version}"
        )

    def is_hds200(self) -> bool:
        """Checks if the model indicates that it is an HDS200 series oscilloscope.

        From https://www.owon.com.hk/list_handheld_oscilloscopes :
        * HDS25 or HDS25S     (2 channel)
        * HDS242 or HDS242S   (2 channel)
        * HDS272 or HDS272S   (2 channel)
        * HDS2102 or HDS2102S (2 channel)
        * HDS2202 or HDS2202S (2 channel)
        * HDS241              (1 channel)
        * HDS271              (1 channel)

        This was only tested with an OWON HDS272S.
        """
        return self.manufacturer == "OWON" and self.model.startswith("HDS2")

    def is_hds300(self) -> bool:
        """Checks if the model indicates that it is an HDS300 series oscilloscope.

        From https://www.owon.com.hk/list_handheld_oscilloscopes :
        * HDS307S             (2 channel)
        * HDS310S             (2 channel)
        * HDS320S             (2 channel)

        This is untested.
        """
        return self.manufacturer == "OWON" and self.model.startswith("HDS3")

    def wavegen_supported(self) -> bool:
        """Checks if the model supports waveform generation.

        Models that end with "S" support waveform generation. This seems to be
        the pattern with the HDS200 and HDS300 series scopes.
        """
        if not self.is_hds200() and not self.is_hds300():
            return False
        return self.model.endswith("S")


class Channel(Enum):
    CH1 = 1
    CH2 = 2


class OwonDevice:
    """
    Interface for communicating with OWON oscilloscopes.
    This class provides oscilloscope-specific commands and functionality.
    """

    id: DeviceIdentification

    def __init__(
        self,
        transport: Literal["serial", "usb"] = "serial",
        serial_device: str = OwonSerialSCPI.DEFAULT_DEVICE,
        usb_vendor_id: int = OwonUSBSCPI.HDS272S_USB_VENDOR_ID,
        usb_product_id: int = OwonUSBSCPI.HDS272S_USB_PRODUCT_ID,
        usb_ep_out: int = 0x01,
        usb_ep_in: int = 0x81,
    ) -> None:
        """Initialize and connect to the oscilloscope."""
        transport_client: OwonSCPIBase

        if transport == "serial":
            transport_client = OwonSerialSCPI(device=serial_device)
        elif transport == "usb":
            transport_client = OwonUSBSCPI(
                usb_vendor_id=usb_vendor_id,
                usb_product_id=usb_product_id,
                usb_ep_out=usb_ep_out,
                usb_ep_in=usb_ep_in,
            )
        else:
            raise ValueError(f"Unsupported transport: {transport}")

        self.scpi: OwonSCPIBase = transport_client

        # Get device identification
        id = self.identify()
        if not id:
            raise ValueError("Failed to identify the device.")
        self.id = id
        # print(f"Connected to an {self.id.manufacturer} {self.id.model}.")
        # print(f"Serial number: {self.id.serial_number}")
        # print(f"Firmware version: {self.id.firmware_version}")

        self.oscope = OwonOscilloscope(self)

    def identify(self) -> DeviceIdentification | None:
        """Get the device identification."""
        idn = self.scpi.query("*IDN?")
        if idn:
            parts = idn.split(",")
            if len(parts) == 4:
                return DeviceIdentification(
                    manufacturer=parts[0],
                    model=parts[1],
                    serial_number=parts[2],
                    firmware_version=parts[3],
                )
            else:
                raise ValueError(f"Invalid identification string '{idn}'")
        else:
            raise ValueError(f"No identification string received")

    def close(self) -> None:
        """Close the connection to the oscilloscope."""
        if self.scpi:
            self.scpi.close()


class OwonOscilloscope:
    """
    Interface for communicating with the oscilloscope portion of an OWON
    multifunctional oscilloscope.
    """

    _device: OwonDevice

    def __init__(self, device: OwonDevice):
        self._device = device

    def screen_values(self, channel: Channel) -> list[int]:
        """Fetch all the raw data points for a given channel.

        Note that these values are in some unknown screen related units.
        For the HDS200 series oscopes, there are 600 signed 8bit values per
        channel. This differs from the 4K or 8K (depending on mem depth mode)
        values that are produced when saving the waveform on the actual device
        and retrieving via Mass Storage Mode.
        """

        data = self._device.scpi.query(
            f":DATa:WAVe:SCReen:ch{channel.value}?",
            data_type="int8",
            length_header=True,
        )
        if not data:
            raise ValueError(f"No data received for channel {channel.value}")
        return data

    def screen_header(self) -> dict[str, str | dict[str, Any] | list[dict[str, Any]]]:
        """Fetch the header for the screen data.

        Returns:
            A dictionary containing the header information.
        """
        data = self._device.scpi.query(
            f":DATa:WAVe:SCReen:HEAD?",
            data_type="json",
            length_header=True,
        )
        if not data:
            raise ValueError(f"No data received for screen header")
        return data

    class HorizontalScale(Enum):
        """Horizontal scale values for the oscilloscope."""

        Time_2ns = "2.0ns"
        Time_5ns = "5.0ns"
        Time_10ns = "10ns"
        Time_20ns = "20ns"
        Time_50ns = "50ns"
        Time_100ns = "100ns"
        Time_200ns = "200ns"
        Time_500ns = "500ns"
        Time_1us = "1.0us"
        Time_2us = "2.0us"
        Time_5us = "5.0us"
        Time_10us = "10us"
        Time_20us = "20us"
        Time_50us = "50us"
        Time_100us = "100us"
        Time_200us = "200us"
        Time_500us = "500us"
        Time_1ms = "1.0ms"
        Time_2ms = "2.0ms"
        Time_5ms = "5.0ms"
        Time_10ms = "10ms"
        Time_20ms = "20ms"
        Time_50ms = "50ms"
        Time_100ms = "100ms"
        Time_200ms = "200ms"
        Time_500ms = "500ms"
        Time_1s = "1.0s"
        Time_2s = "2.0s"
        Time_5s = "5.0s"
        Time_10s = "10s"
        Time_20s = "20s"
        Time_50s = "50s"
        Time_100s = "100s"
        Time_200s = "200s"
        Time_500s = "500s"
        Time_1000s = "1000s"

        @classmethod
        def all(cls) -> list[Self]:
            return list(cls)

        def quantity(self) -> pint.Quantity:
            return pint.Quantity(self.value)

    def horizontal_div_scale_get(self) -> HorizontalScale:
        """Fetch the horizontal division scale."""
        data = self._device.scpi.query(":HORIzontal:SCALe?")
        if not data:
            raise ValueError(f"No data received for horizontal scale")
        return self.HorizontalScale(data)

    def horizontal_div_scale_set(self, scale: HorizontalScale) -> None:
        """Set the horizontal division scale."""
        self._device.scpi.set(f":HORIzontal:SCALe {scale.value}")

    def horizontal_div_offset_get(self) -> float:
        """Fetch the horizontal division offset."""
        data = self._device.scpi.query(":HORIzontal:OFFSet?")
        if not data:
            raise ValueError(f"No data received for horizontal offset")
        return float(data)

    def horizontal_div_offset_set(self, offset: float) -> None:
        """Set the horizontal division offset."""
        self._device.scpi.set(f":HORIzontal:OFFSet {offset}")

    class ChannelCoupling(Enum):
        """Channel input signal coupling mode."""

        AC = "AC"
        DC = "DC"
        GND = "GND"

    def channel_coupling_get(self, channel: Channel) -> ChannelCoupling:
        """Fetch the channel input signal coupling mode."""
        data = self._device.scpi.query(f":CH{channel.value}:COUPling?")
        if not data:
            raise ValueError(f"No data received for channel {channel.value} coupling")
        return self.ChannelCoupling(data)

    def channel_coupling_set(self, channel: Channel, coupling: ChannelCoupling) -> None:
        """Set the channel input signal coupling mode."""
        self._device.scpi.set(f":CH{channel.value}:COUPling {coupling.value}")

    class ChannelProbeAttenuation(Enum):
        """Probe attenuation values."""

        Atten_1X = 1
        Atten_10X = 10
        Atten_100X = 100
        Atten_1000X = 1000
        Atten_10000X = 10000

        def __repr__(self) -> str:
            return f"{self.value}X"

        def order(self) -> int:
            if not hasattr(self, "_all"):
                self._all = list(self.__class__)
            return self._all.index(self)

    class ChannelVerticalScale(Enum):
        # X1
        Volt_10mv = "10.0mV"
        Volt_20mv = "20.0mV"
        Volt_50mv = "50.0mV"
        # X10
        Volt_100mv = "100mV"
        Volt_200mv = "200mV"
        Volt_500mv = "500mV"
        # X100
        Volt_1V = "1.0V"
        Volt_2V = "2.0V"
        Volt_5V = "5.0V"
        # X1000
        Volt_10V = "10V"
        Volt_20V = "20V"
        Volt_50V = "50V"
        # X10000
        Volt_100V = "100V"
        Volt_200V = "200V"
        Volt_500V = "500V"
        Volt_1kV = "1.00kV"
        Volt_2kV = "2.00kV"
        Volt_5kV = "5.00kV"
        Volt_10kV = "10.0kV"
        Volt_20kV = "20.0kV"
        Volt_50kV = "50.0kV"
        Volt_100kV = "100kV"

        @classmethod
        def all(cls) -> list[Self]:
            return list(cls)

        @classmethod
        def scales_by_attenuation(
            cls, atten: "OwonOscilloscope.ChannelProbeAttenuation"
        ) -> list[Self]:
            """Return available vertical scales for a given probe attenuation."""
            atten_ord_mag = atten.order()
            return cls.all()[atten_ord_mag * 3 : 10 + (atten_ord_mag * 3)]

        def quantity(self) -> pint.Quantity:
            return pint.Quantity(self.value)

    def channel_vertical_scale_get(self, channel: Channel) -> str:
        """Fetch the vertical scale for a given channel."""
        data = self._device.scpi.query(f":CH{channel.value}:SCALe?")
        if not data:
            raise ValueError(
                f"No data received for channel {channel.value} vertical scale"
            )
        return data

    def channel_vertical_scale_set(
        self, channel: Channel, scale: ChannelVerticalScale
    ) -> None:
        """Set the vertical scale for a given channel."""
        self._device.scpi.set(f":CH{channel.value}:SCALe {scale.value}")

    def channel_probe_attenuation_get(
        self, channel: Channel
    ) -> ChannelProbeAttenuation:
        """Fetch the probe attenuation for a given channel."""
        data = self._device.scpi.query(f":CH{channel.value}:PROB?")
        if not data:
            raise ValueError(
                f"No data received for channel {channel.value} probe attenuation"
            )
        order = int(data[:-1])
        return self.ChannelProbeAttenuation(order)

    def channel_probe_attenuation_set(
        self, channel: Channel, atten: ChannelProbeAttenuation
    ) -> None:
        """Set the probe attenuation for a given channel."""
        self._device.scpi.set(f":CH{channel.value}:PROBe {atten.value}X")

    def channel_display_get(self, channel: Channel) -> bool:
        """Fetch the display state for a given channel."""
        data = self._device.scpi.query(f":CH{channel.value}:DISPlay?")
        if not data:
            raise ValueError(f"No data received for channel {channel.value} display")
        return data == "ON"

    def channel_display_set(self, channel: Channel, display: bool) -> None:
        """Set the display state for a given channel."""
        display_str = "ON" if display else "OFF"
        self._device.scpi.set(f":CH{channel.value}:DISPlay {display_str}")


def horizontal_offset_real(
    div_scale: OwonOscilloscope.HorizontalScale,
    div_offset: float,
) -> pint.Quantity:
    """Convert the horizontal division offset to the real time offset."""
    return div_offset * div_scale.quantity()


# %%
def main() -> None:
    device = OwonDevice()
    print(device.identify())


if __name__ == "__main__":
    main()

# %%
if "device" in locals():
    device.close()
device = OwonDevice()
device.oscope.horizontal_div_scale_get()
device.oscope.horizontal_div_offset_get()
horizontal_offset_real(
    device.oscope.horizontal_div_scale_get(),
    device.oscope.horizontal_div_offset_get(),
)

# %%
OwonOscilloscope.ChannelVerticalScale.scales_by_attenuation(
    OwonOscilloscope.ChannelProbeAttenuation.Atten_1X
)

# %%
OwonOscilloscope.ChannelVerticalScale.scales_by_attenuation(
    OwonOscilloscope.ChannelProbeAttenuation.Atten_10X
)

# device.oscope.channel_vertical_scale_get(Channel.CH1)

# %%
device.oscope.channel_probe_attenuation_set(
    Channel.CH1, OwonOscilloscope.ChannelProbeAttenuation.Atten_1X
)
print(device.oscope.channel_probe_attenuation_get(Channel.CH1))
device.oscope.channel_probe_attenuation_set(
    Channel.CH1, OwonOscilloscope.ChannelProbeAttenuation.Atten_10X
)
print(device.oscope.channel_probe_attenuation_get(Channel.CH1))
device.oscope.channel_probe_attenuation_set(
    Channel.CH1, OwonOscilloscope.ChannelProbeAttenuation.Atten_100X
)
print(device.oscope.channel_probe_attenuation_get(Channel.CH1))
device.oscope.channel_probe_attenuation_set(
    Channel.CH1, OwonOscilloscope.ChannelProbeAttenuation.Atten_1000X
)
print(device.oscope.channel_probe_attenuation_get(Channel.CH1))
device.oscope.channel_probe_attenuation_set(
    Channel.CH1, OwonOscilloscope.ChannelProbeAttenuation.Atten_10000X
)
print(device.oscope.channel_probe_attenuation_get(Channel.CH1))

# %% Test Probe Coupling
device.oscope.channel_coupling_set(Channel.CH1, OwonOscilloscope.ChannelCoupling.GND)
print(device.oscope.channel_coupling_get(Channel.CH1))
device.oscope.channel_coupling_set(Channel.CH1, OwonOscilloscope.ChannelCoupling.AC)
print(device.oscope.channel_coupling_get(Channel.CH1))
device.oscope.channel_coupling_set(Channel.CH1, OwonOscilloscope.ChannelCoupling.DC)
print(device.oscope.channel_coupling_get(Channel.CH1))

# %% Test Channel Display
device.oscope.channel_display_set(Channel.CH1, True)
print(device.oscope.channel_display_get(Channel.CH1))
time.sleep(1)
device.oscope.channel_display_set(Channel.CH1, False)
print(device.oscope.channel_display_get(Channel.CH1))
time.sleep(1)
device.oscope.channel_display_set(Channel.CH1, True)
print(device.oscope.channel_display_get(Channel.CH1))


# %%
device.close()

# %%
