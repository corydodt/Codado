"""
Useful Twisted-enhancing utilities
"""
import sys
import json

from twisted.python import usage
from twisted.protocols import amp


class CLIError(Exception):
    """
    A handled error from a command-line program.

    Allows usage.Options-based programs to exit with error messages when something bad but predictable occurs
    """
    def __init__(self, program, returnCode, message):
        self.program = program
        self.message = message
        self.returnCode = returnCode

    def __str__(self):
        return "** {program} exit {returnCode}: {message}".format(**self.__dict__)


class Main(usage.Options):
    """
    Extends usage.Options to include a runnable main func
    """
    @classmethod
    def main(cls, args=None):
        """
        Fill in command-line arguments from argv
        """
        if args is None:
            args = sys.argv[1:]

        try:
            o = cls()
            o.parseOptions(args)
        except usage.UsageError, e:
            print str(o)
            print str(e)
            return 1
        except CLIError, ce:
            print str(ce)
            return ce.returnCode

        return 0


class JSON(amp.String):
    """
    Automatic marshalling through JSON (AMP type)
    """
    def toString(self, val):
        return amp.String.toString(self, json.dumps(val, sort_keys=True))

    def fromString(self, val):
        return json.loads(amp.String.fromString(self, val))

