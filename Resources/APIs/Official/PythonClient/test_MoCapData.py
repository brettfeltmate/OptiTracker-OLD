import numpy as np
import unittest
import MoCapData

class TestFramePrefix(unittest.TestCase):
    def setUp(self):
        self.motive_version = 2
        self.frame_prefix = MoCapData.FramePrefix(self.motive_version)

    def test_bytesize(self):
        expected_bytesize = self.frame_prefix.dtype.itemsize
        self.assertEqual(self.frame_prefix.bytesize(), expected_bytesize)

    def test_parse(self):
        data = b'\x00\x00\x00\x00'  # 4 bytes representing frame number 0
        self.frame_prefix.parse(data)
        self.assertEqual(self.frame_prefix.frame()['frame_number'], 0)

    def test_parse_invalid_data(self):
        invalid_data = b'\x00\x00\x00\x00\x00'  # 5 bytes instead of 4
        with self.assertRaises(ValueError):
            self.frame_prefix.parse(invalid_data)

    def test_frame_no_data_recorded(self):
        self.frame_prefix.parse(b'\x00\x00\x00\x00')  # Parse valid data
        self.frame_prefix.parse(b'\x00\x00\x00\x00')  # Parse another valid data
        self.frame_prefix.parse(b'\x00\x00\x00\x00')  # Parse one more valid data
        self.assertEqual(self.frame_prefix.frame()['frame_number'], 0)

if __name__ == '__main__':
    unittest.main()