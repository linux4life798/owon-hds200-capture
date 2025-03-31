#!/usr/bin/env python3
"""
Tests for the OWON oscilloscope interface.
"""

import unittest

from owon_oscilloscope_hds200 import *


class TestDeviceIdentification(unittest.TestCase):
    """Test suite for DeviceIdentification class without hardware dependencies."""

    def test_is_hds200_valid(self):
        """Test the is_hds200() method with various device configurations."""
        # Test valid HDS200 series devices
        valid_models = [
            "HDS25",
            "HDS25S",
            "HDS242",
            "HDS242S",
            "HDS272",
            "HDS272S",
            "HDS2102",
            "HDS2102S",
            "HDS2202",
            "HDS2202S",
        ]
        for model in valid_models:
            device = DeviceIdentification(
                manufacturer="OWON",
                model=model,
                serial_number="123456",
                firmware_version="1.0.0",
            )
            self.assertTrue(
                device.is_hds200(), f"Model {model} should be recognized as HDS200"
            )

    def test_is_hds200_invalid(self):
        """Test the is_hds200() method with invalid device configurations."""
        # Test non-HDS200 models
        invalid_models = ["HDS100", "HDS150", "HDS300", "HDS400"]
        for model in invalid_models:
            device = DeviceIdentification(
                manufacturer="OWON",
                model=model,
                serial_number="123456",
                firmware_version="1.0.0",
            )
            self.assertFalse(
                device.is_hds200(), f"Model {model} should not be recognized as HDS200"
            )

        # Test non-OWON manufacturers
        non_owon = DeviceIdentification(
            manufacturer="OTHER",
            model="HDS272S",
            serial_number="123456",
            firmware_version="1.0.0",
        )
        self.assertFalse(
            non_owon.is_hds200(),
            "Non-OWON manufacturer should not be recognized as HDS200",
        )


class TestOwonOscilloscope(unittest.TestCase):
    """Test suite for the OWON oscilloscope interface."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.device = OwonDevice()
        # Verify device is HDS200 series before running tests
        id_info = self.device.identify()
        if not id_info.is_hds200():
            self.device.close()
            self.skipTest("Device is not an HDS200 series oscilloscope")

    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, "device"):
            self.device.close()

    def test_device_identification(self):
        """Test device identification retrieval."""
        id_info = self.device.identify()
        self.assertIsInstance(id_info, DeviceIdentification)
        self.assertIsInstance(id_info.manufacturer, str)
        self.assertIsInstance(id_info.model, str)
        self.assertIsInstance(id_info.serial_number, str)
        self.assertIsInstance(id_info.firmware_version, str)

    def test_horizontal_scale(self):
        """Test horizontal scale operations."""
        # Test getting current scale
        scale = self.device.oscope.horizontal_div_scale_get()
        self.assertIsInstance(scale, OwonOscilloscope.HorizontalScale)

        # Test setting and getting a new scale
        test_scale = OwonOscilloscope.HorizontalScale.Time_1s
        self.device.oscope.horizontal_div_scale_set(test_scale)
        time.sleep(0.2)
        self.assertEqual(self.device.oscope.horizontal_div_scale_get(), test_scale)

    def test_horizontal_offset(self):
        """Test horizontal offset operations."""
        # Test getting current offset
        offset = self.device.oscope.horizontal_div_offset_get()
        self.assertIsInstance(offset, float)

        # Test setting and getting a new offset
        test_offset = 1.0
        self.device.oscope.horizontal_div_offset_set(test_offset)
        time.sleep(0.1)
        self.assertEqual(self.device.oscope.horizontal_div_offset_get(), test_offset)

    def test_channel_probe_attenuation(self):
        """Test channel probe attenuation operations."""
        channel = Channel.CH1
        test_attenuations = [
            OwonOscilloscope.ChannelProbeAttenuation.Atten_1X,
            OwonOscilloscope.ChannelProbeAttenuation.Atten_10X,
            OwonOscilloscope.ChannelProbeAttenuation.Atten_100X,
            OwonOscilloscope.ChannelProbeAttenuation.Atten_1000X,
            OwonOscilloscope.ChannelProbeAttenuation.Atten_10000X,
            OwonOscilloscope.ChannelProbeAttenuation.Atten_1X,
        ]

        for atten in test_attenuations:
            self.device.oscope.channel_probe_attenuation_set(channel, atten)
            self.assertEqual(
                self.device.oscope.channel_probe_attenuation_get(channel), atten
            )

    def test_channel_coupling(self):
        """Test channel coupling operations."""
        channel = Channel.CH1
        test_couplings = [
            OwonOscilloscope.ChannelCoupling.DC,
            OwonOscilloscope.ChannelCoupling.GND,
            OwonOscilloscope.ChannelCoupling.AC,
            OwonOscilloscope.ChannelCoupling.DC,
        ]

        for coupling in test_couplings:
            print(f"Setting channel {channel} to {coupling}")
            self.device.oscope.channel_coupling_set(channel, coupling)
            time.sleep(1)
            self.assertEqual(self.device.oscope.channel_coupling_get(channel), coupling)

    def test_channel_display(self):
        """Test channel display operations."""
        for channel in [Channel.CH1, Channel.CH2]:
            # Test turning display on
            self.device.oscope.channel_display_set(channel, True)
            self.assertTrue(self.device.oscope.channel_display_get(channel))
            # Test turning display off
            self.device.oscope.channel_display_set(channel, False)
            self.assertFalse(self.device.oscope.channel_display_get(channel))
            # Test turning display back on
            self.device.oscope.channel_display_set(channel, True)
            self.assertTrue(self.device.oscope.channel_display_get(channel))

    def test_vertical_scale_by_attenuation(self):
        """Test vertical scale availability by attenuation."""
        # Test scales for 1X attenuation
        scales_1x = OwonOscilloscope.ChannelVerticalScale.scales_by_attenuation(
            OwonOscilloscope.ChannelProbeAttenuation.Atten_1X
        )
        self.assertIsInstance(scales_1x, list)
        self.assertTrue(len(scales_1x) > 0)

        # Test scales for 10X attenuation
        scales_10x = OwonOscilloscope.ChannelVerticalScale.scales_by_attenuation(
            OwonOscilloscope.ChannelProbeAttenuation.Atten_10X
        )
        self.assertIsInstance(scales_10x, list)
        self.assertTrue(len(scales_10x) > 0)

    def test_screen_data(self):
        """Test screen data retrieval."""
        channel = Channel.CH1

        # Test getting screen values
        values = self.device.oscope.screen_values(channel)
        self.assertIsInstance(values, list)
        self.assertTrue(len(values) > 0)
        self.assertTrue(all(isinstance(v, int) for v in values))

        # Test getting screen header
        header = self.device.oscope.screen_header()
        self.assertIsInstance(header, dict)
        self.assertTrue(len(header) > 0)


if __name__ == "__main__":
    unittest.main()
