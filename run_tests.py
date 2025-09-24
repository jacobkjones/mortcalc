import sys
import os
parent = os.path.dirname(os.getcwd())
sys.path.insert(0, parent)
import unittest
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
