"""
Missing batteries from Python
"""

def eachMethod(decorator, methodFilter=lambda fName: True):
    """
    Class decorator that wraps every single method in its own method decorator

    methodFilter: a function which accepts a function name and should return
    True if the method is one which we want to decorate, False if we want to
    leave this method alone.

    methodFilter can also be simply a string prefix. If it is a string, it is
    assumed to be the prefix we're looking for.
    """
    raise NotImplementedError("We can't figure out how to use this! :(")

    if isinstance(methodFilter, basestring):
        # Is it a string? If it is, change it into a function that takes a string.
        prefix = methodFilter
        methodFilter = lambda fName: fName.startswith(prefix)

    def innerDeco(cls):
        for fName, fn in inspect.getmembers(cls):
            if type(fn) is types.UnboundMethodType and methodFilter(fName):
                setattr(cls, fName, decorator(fn))

        return cls
    return innerDeco


class enum(dict):
    """
    Create a simple attribute list from keys
    """
    def __getattr__(self, attr):
        v = self[attr]
        if v is None:
            return attr
        return v

