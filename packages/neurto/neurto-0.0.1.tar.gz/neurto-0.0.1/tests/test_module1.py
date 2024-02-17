import unittest

from neurto.lfp import LFP


# Add a silly test just for testing
class TestSimple(unittest.TestCase):

    def lfp_fs(self):
        lfp = LFP([1, 2, 3, 4, 4, 3, 2, 1], fs=1000)
        self.assertEqual(lfp.fs, 1000)


if __name__ == '__main__':
    unittest.main()
