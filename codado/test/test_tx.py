"""
Tests for twisted-related utilites in Codado - unless Twisted is not installed
"""
try:
    from twisted import trial
    (trial,) # for pyflakes
    from codado.test._test_tx import *
except ImportError: # pragma: no cover
    import unittest
    class SkipTwistedTests(unittest.TestCase):
        """
        Optional Twisted not installed
        """
