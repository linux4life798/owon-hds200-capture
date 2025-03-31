#!/usr/bin/env python3

import json
import unittest

import owon_usb_scpi


class TestParseAndValidatePacket(unittest.TestCase):
    def test_packet_smaller_than_header(self):
        """Test that a packet with insufficient bytes to hold a length header is handled correctly."""
        with self.assertRaises(
            ValueError, msg="Received insufficient data to parse length header."
        ):
            owon_usb_scpi._parse_and_validate_packet(
                data=b"\x00\x00\x00",
                length_header=True,
            )
        with self.assertRaises(
            ValueError, msg="Received insufficient data to parse length header."
        ):
            owon_usb_scpi._parse_and_validate_packet(
                data=b"",
                length_header=True,
            )

    def test_invalid_packet_header_length(self):
        """Test that packet header lengths that are too small are handled correctly."""

        # Header length indicates no data.
        with self.assertRaises(ValueError, msg="Received packet header of 0."):
            owon_usb_scpi._parse_and_validate_packet(
                data=b"\x00\x00\x00\x00",
                length_header=True,
            )

    def test_packet_header_length_too_large(self):
        """Test that a packet header length that is too large is handled correctly."""
        with self.assertRaises(ValueError):
            owon_usb_scpi._parse_and_validate_packet(
                data=b"\x05\x00\x00\x00",
                length_header=True,
            )


class TestOwonUSBSCPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        try:
            self.owon = owon_usb_scpi.OwonUSBSCPI()
        except ValueError as e:
            self.skipTest(f"Device not connected: {e}")

    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, "owon"):
            self.owon.close()

    def test_device_connection(self):
        """Test basic device connection and identification."""
        response = self.owon.query("*IDN?")
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 0)

    def test_packet_parse_missing_newline(self):
        """Test that a missing newline is handled correctly."""

        err_msg = "No final newline found in response packet."
        with self.assertRaises(ValueError, msg=err_msg):
            # This command uses a 4 byte length header, but no newline.
            self.owon.query(":DATa:WAVe:SCReen:HEAD?")
        with self.assertRaises(ValueError, msg=err_msg):
            # This command uses a 4 byte length header, but no newline.
            self.owon.query(":DATa:WAVe:SCReen:CH1?")
        with self.assertRaises(ValueError, msg=err_msg):
            # This command uses a 4 byte length header, but no newline.
            self.owon.query(":DATa:WAVe:SCReen:CH2?")

    def test_head_data(self):
        """Test waveform header data."""
        # Get waveform header
        head_data = self.owon.query(
            ":DATa:WAVe:SCReen:HEAD?", data_type="str", length_header=True
        )
        self.assertIsNotNone(head_data)
        json_data = json.loads(head_data)
        self.assertIsInstance(json_data, dict)
        self.assertIn("CHANNEL", json_data)

    def test_channel_data(self):
        """Test waveform channel data."""
        ch1_data = self.owon.query(
            ":DATa:WAVe:SCReen:CH1?", data_type="bin", length_header=True
        )
        self.assertIsNotNone(ch1_data)
        self.assertEqual(len(ch1_data), 600)

    def test_int8_data(self):
        """Test int8 data type."""
        ch1_int_data = self.owon.query(
            ":DATa:WAVe:SCReen:CH1?", data_type="int8", length_header=True
        )
        self.assertIsNotNone(ch1_int_data)
        self.assertEqual(len(ch1_int_data), 600)
        self.assertIsInstance(ch1_int_data, list)
        for value in ch1_int_data:
            self.assertIsInstance(value, int)
            self.assertTrue(-128 <= value <= 127)  # 8-bit signed integers range

    def test_json_data(self):
        """Test JSON data type."""
        head_data = self.owon.query(
            ":DATa:WAVe:SCReen:HEAD?", data_type="json", length_header=True
        )
        self.assertIsNotNone(head_data)
        self.assertIsInstance(head_data, dict)
        # Check for expected keys in the JSON structure
        self.assertIn("CHANNEL", head_data)


if __name__ == "__main__":
    unittest.main()
