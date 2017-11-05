"""
URLtool - tool for documenting http API and building API clients

This assumes using codado.kleinish.tree.enter() decorator
"""
import re

import yaml

import attr

from twisted.python.reflect import namedAny

from codado.py import doc
from codado.tx import Main


class Options(Main):
    """
    Dump all urls branching from a class

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
                oar = dumpRule(currentClass, rule, prefix)
                if oar.branch:
                    continue

                if oar.subKlein:
                    clsDown = namedAny(oar.subKlein)
                    iterableRules.append((oar.rulePath, clsDown, clsDown.app.url_map.iter_rules()))

                yield oar

    def postOptions(self):
        rootCls = namedAny(self['classQname'])
        rules = list(self._iterClass(rootCls))
        arr = []
        for item in sorted(rules):
            if item.subKlein:
                continue

            if re.search(self['filt'], item.rulePath):
                arr.append(item.toOpenAPIData())

        print yaml.dump_all(arr, default_flow_style=False)


@attr.s
class OpenAPIRule(object):
    """
    An atom of structured information about one route
    """
    rulePath = attr.ib()
    endpoint = attr.ib()
    summary = attr.ib(default='undocumented')
    description = attr.ib(default='')
    branch = attr.ib(default=False)
    methods = attr.ib(default=attr.Factory(list))
    subKlein = attr.ib(default=None)

    def toOpenAPIData(self):
        """
        Produce a data structure compatible with OpenAPI
        """
        dct = {self.rulePath: {}}
        methods = self.methods[:] or ['*']
        for meth in methods:
            if meth.lower() in ['head']:
                continue
            dct[self.rulePath].setdefault(meth.lower(), dict(
                description=self.description,
                summary=self.summary,
                responses=[],
                requestBody={},
            ))

        return decruftDict(dct)


def decruftDict(dct, matcher=lambda node: not not node):
    """
    Remove any key from a dict if its value is a false-value (by default)
    or any function you want to provide to matcher. Function should return False to skip a key.
    """
    ret = {}
    for k, v in dct.items():
        if isinstance(v, dict):
            v = decruftDict(v)

        if matcher(v):
            ret[k] = v

    return ret


def dumpRule(serviceCls, rule, prefix):
    """
    Create an OpenAPI 3.0 representation of the rule
    """
    rulePath = prefix + rule.rule
    rulePath = re.sub('/{2,}', '/', rulePath)

    oar = OpenAPIRule(
            rulePath=rulePath,
            endpoint=rule.endpoint
            )

    # look for methods
    for meth in rule.methods or []:
        oar.methods.append(meth)

    # edit _branch endpoints to provide the true method name
    origEP = oar.endpoint
    if origEP.endswith('_branch'):
        origEP = origEP[:-7]
        oar.branch = True
    oar.endpoint = '%s.%s' % (serviceCls.__name__, origEP)
    # get the actual method so we can inspect it for extension attributes
    meth = getattr(serviceCls, origEP)

    ## if hasattr(meth, "_roles"):
    ##     oar.roles = meth._roles

    ## if hasattr(meth, '_json'):
    ##     oar.json = meth._json

    if hasattr(meth, '_subKleinQname'):
        oar.subKlein = meth._subKleinQname

    _doc = doc(meth, full=True, decode=True).encode('utf-8')
    if _doc:
        oar.description = _doc
        oar.summary = oar.description.split('\n')[0]
    return oar


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
