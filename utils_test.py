#!/usr/bin/env python3

import unittest

import utils


class TestHelperFunctions(unittest.TestCase):
    def test_split_int_units(self):
        """Test the split_int_units function."""
        test_cases = [
            ("100mV", (100, "mV")),
            ("10X", (10, "X")),
            ("1234", (1234, "")),
            ("0dB", (0, "dB")),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                result = utils.split_int_units(input_str)
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
