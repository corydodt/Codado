"""
URLtool - tool for documenting http API and building API clients

This assumes using codado.kleinish.tree.enter() decorator
"""
import re

import attr

from twisted.python.reflect import namedAny

import yaml

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
                utr = dumpRule(currentClass, rule, prefix)
                if utr.branch:
                    continue

                if utr.subKlein:
                    clsDown = namedAny(utr.subKlein)
                    iterableRules.append((utr.rulePath, clsDown, clsDown.app.url_map.iter_rules()))

                yield utr

    def postOptions(self):
        rootCls = namedAny(self['classQname'])
        rules = list(self._iterClass(rootCls))
        for item in sorted(rules):
            if re.search(self['filt'], item.rulePath):
                print yaml.dump({item.rulePath: item})


@attr.s
class URLToolRule(object):
    """
    An atom of structured information about one route
    """
    rulePath = attr.ib()
    endpoint = attr.ib()
    branch = attr.ib(default=False)
    methods = attr.ib(default=attr.Factory(list))
    subKlein = attr.ib(default=None)

    @staticmethod
    def filterDump(atr, val):
        """
        Clean up the dict representation for yaml output
        """
        if not val:
            return False
        if atr.name == 'rulePath':
            return False
        return True

    @staticmethod
    def asYAML(dumper, data):
        """
        YAML representer, using filterDump to prune the dict
        """
        dictSelf = attr.asdict(data, filter=URLToolRule.filterDump)
        return dumper.represent_dict(dictSelf)


yaml.add_representer(URLToolRule, URLToolRule.asYAML)


def dumpRule(serviceCls, rule, prefix):
    """
    Create a dict representation of the rule
    """
    rulePath = prefix + rule.rule
    rulePath = re.sub('/{2,}', '/', rulePath)

    utr = URLToolRule(
            rulePath=rulePath,
            endpoint=rule.endpoint
            )

    # look for methods other than GET and HEAD, and note them
    for meth in rule.methods or []:
        if meth not in ['HEAD', 'GET']:
            utr.methods.append(meth)

    # edit _branch endpoints to provide the true method name
    origEP = utr.endpoint
    if origEP.endswith('_branch'):
        origEP = origEP[:-7]
        utr.branch = True
    utr.endpoint = '%s.%s' % (serviceCls.__name__, origEP)
    # get the actual method so we can inspect it for extension attributes
    meth = getattr(serviceCls, origEP)

    ## if hasattr(meth, "_roles"):
    ##     utr.roles = meth._roles

    ## if hasattr(meth, '_json'):
    ##     utr.json = meth._json

    if hasattr(meth, '_subKleinQname'):
        utr.subKlein = meth._subKleinQname

    return utr

