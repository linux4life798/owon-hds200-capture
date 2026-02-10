#!/usr/bin/env python3

import unittest

from owon_scpi_base import parse_and_validate_packet


class TestParseAndValidatePacket(unittest.TestCase):
    def test_packet_smaller_than_header(self):
        """Test that a packet with insufficient bytes to hold a length header is handled correctly."""
        with self.assertRaises(
            ValueError, msg="Received insufficient data to parse length header."
        ):
            parse_and_validate_packet(
                data=b"\x00\x00\x00",
                length_header=True,
            )
        with self.assertRaises(
            ValueError, msg="Received insufficient data to parse length header."
        ):
            parse_and_validate_packet(
                data=b"",
                length_header=True,
            )

    def test_invalid_packet_header_length(self):
        """Test that packet header lengths that are too small are handled correctly."""
        # Header length indicates no data.
        with self.assertRaises(ValueError, msg="Received packet header of 0."):
            parse_and_validate_packet(
                data=b"\x00\x00\x00\x00",
                length_header=True,
            )

    def test_packet_header_length_too_large(self):
        """Test that a packet header length that is too large is handled correctly."""
        with self.assertRaises(ValueError):
            parse_and_validate_packet(
                data=b"\x05\x00\x00\x00",
                length_header=True,
            )


if __name__ == "__main__":
    unittest.main()
