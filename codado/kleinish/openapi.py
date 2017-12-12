"""
OpenAPI schema

Includes yaml representation helpers
"""
from collections import OrderedDict

import attr


class _UnsortableList(list):
    """
    List that no-ops sort(), so yaml will get unsorted items
    """
    def sort(self, *args, **kwargs):
        """
        Do not sort
        """


class UnsortableOrderedDict(OrderedDict):
    """
    Glue class to allow yaml to dump an OrderedDict
    """
    def items(self, *args, **kwargs):
        return _UnsortableList(OrderedDict.items(self, *args, **kwargs))


@attr.s
class OpenAPIMediaType(object):
    """
    TODO - an object representing a body of data with a particular media type such as text/html
    """


@attr.s
class OpenAPIResponse(object):
    """
    A response (HTTP body) returned by an operation
    """
    description = attr.ib()
    headers = attr.ib(default=attr.Factory(UnsortableOrderedDict))
    content = attr.ib(default=attr.Factory(UnsortableOrderedDict))
    links = attr.ib(default=attr.Factory(UnsortableOrderedDict))


@attr.s
class OpenAPIResponses(object):
    """
    Mapping of responses (available HTTP body return values)
    """
    default = attr.ib(default=attr.Factory(lambda: OpenAPIResponse(None)))
    codeMap = attr.ib(default=attr.Factory(UnsortableOrderedDict))


@attr.s
class OpenAPIOperation(object):
    """
    One operation (method) in an OpenAPIPathItem
    """
    tags = attr.ib(default=attr.Factory(list))
    summary = attr.ib(default="undocumented")
    description = attr.ib(default="undocumented")
    externalDocs = attr.ib(default=None)
    operationId = attr.ib(default=None)
    responses = attr.ib(default=attr.Factory(UnsortableOrderedDict))
    parameters = attr.ib(default=attr.Factory(list))
    requestBody = attr.ib(default=attr.Factory(UnsortableOrderedDict))
    callbacks = attr.ib(default=attr.Factory(UnsortableOrderedDict))
    deprecated = attr.ib(default=False)
    security = attr.ib(default=None)
    servers = attr.ib(default=attr.Factory(list))
    _extended = attr.ib(default=attr.Factory(UnsortableOrderedDict))


@attr.s
class OpenAPIPathItem(object):
    """
    One path in the .paths attribute of an openapi 3 spec
    """
    summary = attr.ib(default="")
    description = attr.ib(default="")
    servers = attr.ib(default=attr.Factory(list))
    parameters = attr.ib(default=attr.Factory(list))
    _operations = attr.ib(default=attr.Factory(UnsortableOrderedDict))

    def merge(self, other):
        """
        Gather operations from other and merge them into my operations.
        """
        for key, value in sorted(other._operations.items()):
            self.addOperation(key, value)

    def addOperation(self, key, operation):
        """
        Insert one operation to this pathItem

        Raises an exception if an operation object being merged is already in this path item.
        """
        assert key not in self._operations.keys(), "Non-unique operation %r in %r" % (key, self)
        self._operations[key] = operation


@attr.s
class OpenAPIInfo(object):
    """
    The .info attribute of an openapi 3 spec
    """
    title = attr.ib(default="TODO")
    description = attr.ib(default="")
    termsOfService = attr.ib(default="")
    contact = attr.ib(default=None)
    license = attr.ib(default=None)
    version = attr.ib(default="TODO")


@attr.s
class OpenAPIParameter(object):
    """
    The .parameters attribute of an operation
    """
    name = attr.ib()
    in_ = attr.ib()
    description = attr.ib(default="")
    required = attr.ib(default=False)
    deprecated = attr.ib(default=False)
    allowEmptyValue = attr.ib(default=False)


@attr.s
class OpenAPI(object):
    """
    The root openapi spec document
    """
    openapi = attr.ib(default="3.0.0")
    info = attr.ib(default=attr.Factory(OpenAPIInfo))
    paths = attr.ib(default=attr.Factory(UnsortableOrderedDict))


def _orderedCleanDict(attrsObj):
    """
    -> dict with false-values removed

    Also evaluates attr-instances for false-ness by looking at the values of their properties
    """
    def _filt(k, v):
        if attr.has(v):
            return not not any(attr.astuple(v))
        return not not v

    return attr.asdict(attrsObj,
        dict_factory=UnsortableOrderedDict,
        recurse=False,
        filter=_filt)


def representCleanOpenAPIOperation(dumper, data):
    """
    Unpack nonstandard attributes while representing an OpenAPIOperation
    """
    dct = _orderedCleanDict(data)
    if '_extended' in dct:
        for k, ext in data._extended.items():
            dct[k] = ext
        del dct['_extended']

    return dumper.represent_dict(dct)


def representCleanOpenAPIPathItem(dumper, data):
    """
    Unpack operation key/values before representing an OpenAPIPathItem
    """
    dct = _orderedCleanDict(data)
    if '_operations' in dct:
        items = sorted(data._operations.items())
        for k, op in items:
            dct[k] = op
        del dct['_operations']

    return dumper.represent_dict(dct)


def representCleanOpenAPIParameter(dumper, data):
    """
    Rename python reserved keyword fields before representing an OpenAPIParameter
    """
    dct = _orderedCleanDict(data)
    if 'in_' in dct:
        dct['in'] = dct['in_']
        del dct['in_']

    return dumper.represent_dict(dct)


def representCleanOpenAPIObjects(dumper, data):
    """
    Produce a representation of an OpenAPI object, removing empty attributes
    """
    dct = _orderedCleanDict(data)

    return dumper.represent_dict(dct)


def mediaTypeHelper(mediaType):
    """
    Return a function that creates a Responses object;
    """
    def _innerHelper(data=None):
        """
        Create a Responses object that contains a MediaType entry of the specified mediaType

        Convenience function for the most common cases where you need an instance of Responses
        """
        ret = OpenAPIResponses()
        if data is None:
            data = {}
        ret.default.content[mediaType] = data
        return ret
    return _innerHelper


textHTML = mediaTypeHelper('text/html')
applicationJSON = mediaTypeHelper('application/json')


def queryParameter(name, **kwargs):
    """
    Shorthand for a query parameter
    """
    return OpenAPIParameter(name=name, in_="query", **kwargs)
