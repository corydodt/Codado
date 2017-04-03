"""
Tests for twisted-related utilites in Codado
"""
import shlex
import re
import sys
from contextlib import contextmanager
from cStringIO import StringIO

from mock import patch

try:
    from twisted.trial import unittest
    from codado import tx
    needTwisted = lambda c: c
except ImportError: # pragma: nocover
    import unittest
    needTwisted = unittest.skip("Twisted not installed")


@needTwisted
class TwistedTest(unittest.TestCase):
    def test_JSONtoString(self):
        """
        Do I encode json correctly?
        """
        js = tx.JSON()
        self.assertEqual(js.toString(None), 'null')
        self.assertEqual(js.toString([]), '[]')
        self.assertEqual(js.toString({}), '{}')
        self.assertEqual(js.toString(['a', 'b']), '["a", "b"]')
        self.assertEqual(js.toString(['a', 'b']), '["a", "b"]')
        # Minor assymmetry: json key names MUST be strings, so int(345) as a
        # key becomes string "345".
        # However, since int(345) sorts BEFORE str("234"), the keys arrive in
        # this order. :shrug_emoji:
        self.assertEqual(js.toString({'abc': 1, '234': 234.5, 345: '345'}), 
                '{"345": "345", "234": 234.5, "abc": 1}')

    def test_JSONfromString(self):
        """
        Do I decode json correctly?
        """
        js = tx.JSON()
        self.assertEqual(js.fromString('null'), None)
        self.assertEqual(js.fromString('[]'), [])
        self.assertEqual(js.fromString('{}'), {})
        self.assertEqual(js.fromString('["a", "b"]'), ["a", "b"])
        # minor assymmetry: json key names MUST be strings, so int(345) is no longer allowed as a key
        self.assertEqual(js.fromString('{"234": 234.5, "345": "345", "abc": 1}'), {'abc': 1, '234': 234.5, '345': '345'})


@needTwisted
class MainTest(unittest.TestCase):
    """
    Test Main.run usage-enhancer
    """
    def options(self, name='Options'):
        """
        Return a new instance of an Options for testing
        """
        class O(tx.Main):
            """
            I am the longdesc
            """
            optParameters = [['flag', 'f', None, None]]
            optFlags = [['hello', None, 'Say hello']]
            def parseArgs(self, *a):
                self['ret'] = ' '.join(a)

            def postOptions(self):
                if 'error' in self['ret']:
                    raise tx.CLIError('o', 1, 'This is an error!')

                print self['ret']

        O.__name__ = name
        return O

    @contextmanager
    def patchIO(self):
        """
        Replace stdio streams with a single StringIO
        """
        io = StringIO()
        pStdout = patch.object(sys, 'stdout', io)
        pStderr = patch.object(sys, 'stderr', io)
        with pStdout, pStderr:
            yield io

    def test_main(self):
        """
        The factory function main() does command-line shit
        """
        main = self.options('O')().main

        pArgv = patch.object(sys, 'argv', ('o',))
        # manual args, remove first arg and succeed
        with self.patchIO() as io, pArgv:
            argv = shlex.split("this is a sandwich")
            exitCode = main(argv)
            self.assertEqual(exitCode, 0)
            ret = io.getvalue().strip()
            self.assertEqual(ret, 'this is a sandwich')

        # remove first arg and error
        with self.patchIO() as io, pArgv:
            argv = shlex.split("this is an error")
            exitCode = main(argv)
            self.assertEqual(exitCode, 1)
            ret = io.getvalue().strip()
            rx = re.compile(r'\*\* o exit 1: This is an error!', re.DOTALL)
            self.assertRegexpMatches(ret, rx)

        # handle UsageError with incorrect --flag parameter
        with self.patchIO() as io, pArgv:
            argv = ['--flag']
            exitCode = main(argv)
            self.assertEqual(exitCode, 1)
            ret = io.getvalue().strip()
            rx = re.compile(r'Usage: o.*Say hello.*flag requires argument', re.DOTALL)
            self.assertRegexpMatches(ret, rx)

        # use sys.argv and succeed
        with self.patchIO() as io, pArgv:
            exitCode = main()
            self.assertEqual(exitCode, 0)
            ret = io.getvalue().strip()
            self.assertEqual(ret, '')

    def test_subCommands(self):
        """
        When a subcommand is involved, we get the right help
        """
        pExit = patch.object(sys, 'exit', autospec=True)
        pArgv = patch.object(sys, 'argv', ('o',))

        class Sub(tx.Main):
            "I am sub longdesc"
            synopsis = "i am sub synopsis"

        cls = self.options("O")
        class HasSub(cls):
            subCommands = [['sub', None, Sub, None]]
            def postOptions(self):
                pass

        with self.patchIO() as io, pArgv:
            exit = HasSub().main(["sub", "dsfasdfadf"])
            val = io.getvalue().strip()
            self.assertRegexpMatches(val, r'Usage: o i am sub synopsis')
            self.assertEqual(exit, 1)

        with self.patchIO() as io, pArgv, pExit as mExit:
            opt = HasSub()
            exit = opt.main(["sub", "--help"])
            val = io.getvalue().strip()
            self.assertRegexpMatches(val, r'Usage: o i am sub synopsis')
            self.assertRegexpMatches(val, r'I am sub longdesc')
            self.assertEqual(exit, 0)
            mExit.assert_called_once_with(0)

__all__ = ['MainTest', 'TwistedTest']
