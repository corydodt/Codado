"""
Tests for twisted-related utilites in Codado
"""

try:
    from twisted import trial
    from twisted.trial import unittest
except ImportError:
    trial = None
    import unittest

if not trial:
    class SkipTwistedTests(unittest.TestCase):
        """
        Optional Twisted not installed
        """

else:
    from codado import tx

    class TwistedTest(unittest.TestCase):
        def test_JSON(self):
            """
            Do I encode and decode json correctly?
            """

            js = tx.JSON()
            self.assertEqual(js.toString(None), 'null')
            self.assertEqual(js.toString([]), '[]')
            self.assertEqual(js.toString({}), '{}')
            self.assertEqual(js.toString(['a', 'b']), '["a", "b"]')
            self.assertEqual(js.toString(['a', 'b']), '["a", "b"]')
            self.assertEqual(js.toString({'abc': 1, '234': 234.5, 345: '345'}), 
                    '{"234": 234.5, "345": "345", "abc": 1}')
