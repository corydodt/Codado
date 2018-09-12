"""
Tests for twisted-related utilites in Codado
"""
from __future__ import print_function

import shlex
import re
import sys

from future import standard_library
standard_library.install_aliases()

from mock import patch

from codado import tx


def test_JSONtoString():
    """
    Do I encode json correctly?
    """
    js = tx.JSON()
    assert js.toString(None) == 'null'
    assert js.toString([]) == '[]'
    assert js.toString({}) == '{}'
    assert js.toString(['a', 'b']) == '["a", "b"]'
    assert js.toString(['a', 'b']) == '["a", "b"]'
    assert js.toString({'abc': 1, '234': 234.5}) == '{"234": 234.5, "abc": 1}'


def test_JSONfromString():
    """
    Do I decode json correctly?
    """
    js = tx.JSON()
    assert js.fromString('null') == None
    assert js.fromString('[]') == []
    assert js.fromString('{}') == {}
    assert js.fromString('["a", "b"]') == ["a", "b"]
    # minor assymmetry: json key names MUST be strings, so int(345) is no longer allowed as a key
    assert js.fromString('{"234": 234.5, "345": "345", "abc": 1}') == {'abc': 1, '234': 234.5, '345': '345'}


def options(name='Options'):
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

            print(self['ret'])

    O.__name__ = name
    return O


def test_main(capsys):
    """
    The factory function main() does command-line shit
    """
    main = options('O')().main

    pArgv = patch.object(sys, 'argv', ('o',))
    # manual args, remove first arg and succeed
    with pArgv:
        argv = shlex.split("this is a sandwich")
        exitCode = main(argv)
        assert exitCode == 0
        out, err = [f.strip() for f in capsys.readouterr()]
        assert out, err == ('this is a sandwich', "")

    # remove first arg and error
    with pArgv:
        argv = shlex.split("this is an error")
        exitCode = main(argv)
        assert exitCode == 1
        out, err = [f.strip() for f in capsys.readouterr()]
        rx = re.compile(r'\*\* o exit 1: This is an error!', re.DOTALL)
        assert re.match(rx, out)
        assert err == ''

    # handle UsageError with incorrect --flag parameter
    with pArgv:
        argv = ['--flag']
        exitCode = main(argv)
        assert exitCode == 1
        out, err = [f.strip() for f in capsys.readouterr()]
        rx = re.compile(r'Usage: o.*Say hello.*flag requires argument', re.DOTALL)
        assert re.match(rx, out)
        assert err == ''

    # use sys.argv and succeed
    with pArgv:
        exitCode = main()
        assert exitCode == 0
        out, err = [f.strip() for f in capsys.readouterr()]
        assert (out, err) == ('', '')


def test_subCommands(capsys):
    """
    When a subcommand is involved, we get the right help
    """
    pExit = patch.object(sys, 'exit', autospec=True)
    pArgv = patch.object(sys, 'argv', ('o',))

    class Sub(tx.Main):
        "I am sub longdesc"
        synopsis = "i am sub synopsis"

    cls = options("O")

    class HasSub(cls):
        subCommands = [['sub', None, Sub, None]]
        def postOptions(self):
            pass

    with pArgv:
        exit = HasSub().main(["sub", "dsfasdfadf"])
        out, err = [f.strip() for f in capsys.readouterr()]
        assert re.match(r'Usage: o i am sub synopsis', out)
        assert err == ''
        assert exit == 1

    with pArgv, pExit as mExit:
        opt = HasSub()
        exit = opt.main(["sub", "--help"])
        out, err = [f.strip() for f in capsys.readouterr()]
        assert re.search(r'Usage: o i am sub synopsis', out)
        assert re.search(r'I am sub longdesc', out)
        assert err == ''
        assert exit == 0
        mExit.assert_called_once_with(0)
