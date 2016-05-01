"""
Missing batteries from Python
"""
import inspect
import types

def eachMethod(decorator, methodFilter=lambda fName: True):
    """
    Class decorator that wraps every single method in its own method decorator

    methodFilter: a function which accepts a function name and should return
    True if the method is one which we want to decorate, False if we want to
    leave this method alone.

    methodFilter can also be simply a string prefix. If it is a string, it is
    assumed to be the prefix we're looking for.
    """
    if isinstance(methodFilter, basestring):
        # Is it a string? If it is, change it into a function that takes a string.
        prefix = methodFilter
        methodFilter = lambda fName: fName.startswith(prefix)

    def innerDeco(cls):
        for fName, fn in inspect.getmembers(cls):
            if type(fn) is types.MethodType and methodFilter(fName):
                if fn.im_self is None:
                    # this is an unbound instance method
                    setattr(cls, fName, decorator(fn))
                else:
                    assert fn.im_class is type, "This should be a classmethod but it doesn't look like one: %r" % fName
                    setattr(cls, fName, classmethod(decorator(fn)))

        return cls
    return innerDeco


class enum(dict):
    """
    Create a simple attribute list from keys
    """
    @classmethod
    def fromkeys(cls, keys):
        ret = cls()
        dd = []
        for k in keys:
            dd.append((k, k))
        ret.update(dict(dd))
        return ret
 
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

