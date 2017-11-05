"""
URLtool - tool for documenting http API and building API clients

This assumes using codado.kleinish.tree.enter() decorator
"""
from collections import OrderedDict
import re

import yaml

import attr

from twisted.python.reflect import namedAny

from codado.py import doc
from codado.tx import Main


class Options(Main):
    """
    Dump all urls branching from a class as OpenAPI 3 documentation

    Apply optional <filter> as a regular expression searching within urls. For
    example, to match all urls beginning with api, you might use '^/api'
    """
    synopsis = "urltool <classQname> [filter]"

    def parseArgs(self, classQname, filt=None):
        self['classQname'] = classQname
        self['filt'] = re.compile(filt or '.*')

    def _iterClass(self, cls, prefix=''):
        iterableRules = [(prefix, cls, cls.app.url_map.iter_rules())]
        for prefix, currentClass, i in iter(iterableRules):
            for rule in i:
                converted = dumpRule(currentClass, rule, prefix)
                if converted.branch:
                    continue

                if converted.subKlein:
                    clsDown = namedAny(converted.subKlein)
                    iterableRules.append((converted.rulePath, clsDown, clsDown.app.url_map.iter_rules()))

                yield converted

    def postOptions(self):
        rootCls = namedAny(self['classQname'])
        rules = list(self._iterClass(rootCls))
        arr = []
        for item in sorted(rules):
            if item.subKlein:
                continue

            if re.search(self['filt'], item.rulePath):
                arr.append(tuple(item.toOpenAPIPath()))

        openapi3 = OpenAPI()
        for pathPath, pathItem in arr:
            if pathPath in openapi3.paths:
                openapi3.paths[pathPath].merge(pathItem)
            else:
                openapi3.paths[pathPath] = pathItem
        print yaml.dump(openapi3, default_flow_style=False)


class UnsortableList(list):
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
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))


SHALLOW = {'shallow': True}


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
    responses = attr.ib(default=attr.Factory(UnsortableOrderedDict), metadata=SHALLOW)
    parameters = attr.ib(default=attr.Factory(list), metadata=SHALLOW)
    requestBody = attr.ib(default=attr.Factory(UnsortableOrderedDict), metadata=SHALLOW)
    callbacks = attr.ib(default=attr.Factory(UnsortableOrderedDict), metadata=SHALLOW)
    deprecated = attr.ib(default=False)
    security = attr.ib(default=None)
    servers = attr.ib(default=attr.Factory(list), metadata=SHALLOW)


@attr.s
class OpenAPIPathItem(object):
    """
    One path in the .paths attribute of an openapi 3 spec
    """
    summary = attr.ib(default="")
    description = attr.ib(default="")
    servers = attr.ib(default=attr.Factory(list), metadata=SHALLOW)
    parameters = attr.ib(default=attr.Factory(list), metadata=SHALLOW)
    _operations = attr.ib(default=attr.Factory(UnsortableOrderedDict), metadata=SHALLOW)

    def merge(self, other):
        """
        Gather operations from other and merge them into my operations.
        """
        for key, value in other._operations.items():
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
class OpenAPI(object):
    """
    The root openapi spec document
    """
    openapi = attr.ib(default="3.0.0")
    info = attr.ib(default=attr.Factory(OpenAPIInfo), metadata=SHALLOW)
    paths = attr.ib(default=attr.Factory(UnsortableOrderedDict), metadata=SHALLOW)


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


def representCleanOpenAPIPathItem(dumper, data):
    """
    Unpack operation key/values before representing an OpenAPIPathItem
    """
    dct = _orderedCleanDict(data)
    dct.update({k: op for (k, op) in data._operations.items()})
    del dct['_operations']

    return dumper.represent_dict(dct)


def representCleanOpenAPIObjects(dumper, data):
    """
    Produce a representation of an OpenAPI object, removing empty attributes
    """
    dct = _orderedCleanDict(data)

    return dumper.represent_dict(dct)


yaml.add_representer(OpenAPIPathItem, representCleanOpenAPIPathItem)
yaml.add_representer(OpenAPI, representCleanOpenAPIObjects)
yaml.add_representer(OpenAPIInfo, representCleanOpenAPIObjects)
yaml.add_representer(OpenAPIOperation, representCleanOpenAPIObjects)


@attr.s
class ConvertedRule(object):
    """
    An atom of structured information about one route
    """
    rulePath = attr.ib()
    operationId = attr.ib()
    summary = attr.ib(default='undocumented')
    description = attr.ib(default='')
    branch = attr.ib(default=False)
    methods = attr.ib(default=attr.Factory(list))
    subKlein = attr.ib(default=None)

    def toOpenAPIPath(self):
        """
        Produce a data structure compatible with OpenAPI

        @returns tuple of (path, pathItem)
        """
        pathItem = OpenAPIPathItem()
        methods = self.methods[:] or ['x-any-method']
        for meth in methods:
            if meth.lower() in ['head']:
                continue
            operation = OpenAPIOperation()
            operation.operationId = self.operationId
            operation.summary = self.summary
            operation.description = self.description
            pathItem.addOperation(meth.lower(), operation)

        return self.rulePath, pathItem


def dumpRule(serviceCls, rule, prefix):
    """
    Create an in-between representation of the rule, so we can eventually convert it to OpenAPIPathItem with OpenAPIOperation(s)
    """
    rulePath = prefix + rule.rule
    rulePath = re.sub('/{2,}', '/', rulePath)

    cor = ConvertedRule(
            rulePath=rulePath,
            operationId=rule.endpoint
            )

    # look for methods
    for meth in rule.methods or []:
        cor.methods.append(meth)

    # edit _branch operationId to provide the true method name
    origEP = cor.operationId
    if origEP.endswith('_branch'):
        origEP = origEP[:-7]
        cor.branch = True
    cor.operationId = '%s.%s' % (serviceCls.__name__, origEP)
    # get the actual method so we can inspect it for extension attributes
    meth = getattr(serviceCls, origEP)

    ## if hasattr(meth, "_roles"):
    ##     cor.roles = meth._roles

    ## if hasattr(meth, '_json'):
    ##     cor.json = meth._json

    if hasattr(meth, '_subKleinQname'):
        cor.subKlein = meth._subKleinQname

    _doc = doc(meth, full=True, decode=True).encode('utf-8')
    if _doc:
        cor.description = _doc
        cor.summary = cor.description.split('\n')[0]
    return cor


def literal_unicode_representer(dumper, data):
    """
    Use |- literal syntax for long strings
    """
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    else:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data)


yaml.add_representer(unicode, literal_unicode_representer)
yaml.add_representer(str, literal_unicode_representer)
yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)
