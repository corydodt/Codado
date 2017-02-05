"""
URLtool - tool for documenting http API and building API clients
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
                rtop = dumpRule(currentClass, rule, prefix)
                urlKey = rtop.keys()[0]
                if rtop[urlKey].branch:
                    continue

                if rtop[urlKey].subKlein:
                    clsDown = namedAny(rtop[urlKey].subKlein)
                    iterableRules.append((urlKey, clsDown, clsDown.app.url_map.iter_rules()))

                yield rtop

    def postOptions(self):
        rootCls = namedAny(self['classQname'])
        rules = list(self._iterClass(rootCls))
        for item in sorted(rules):
            if re.search(self['filt'], item.keys()[0]):
                print yaml.dump(item)


@attr.s
class URLToolRule(object):
    rulePath = attr.ib()
    endpoint = attr.ib()
    branch = attr.ib(default=False)
    methods = attr.ib(default=attr.Factory(list))
    subKlein = attr.ib(default=None)

    @staticmethod
    def filterDump(atr, val):
        if not val:
            return False
        if atr.name == 'rulePath':
            return False
        return True

    @staticmethod
    def asYAML(dumper, data):
        return dumper.represent_dict(
                attr.asdict(data, filter=URLToolRule.filterDump)
                )


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

    # edit _branch endpoints to provide the true method name
    origEP = utr.endpoint
    if origEP.endswith('_branch'):
        origEP = origEP[:-7]
        utr.branch = True
    utr.endpoint = '%s.%s' % (serviceCls.__name__, origEP)
    meth = getattr(serviceCls, origEP)

    # look for methods other than GET and HEAD, and note them
    interestingMethods = []
    if rule.methods:
        interestingMethods = list(rule.methods)
        if 'HEAD' in interestingMethods:
            interestingMethods.remove('HEAD')
    if interestingMethods and interestingMethods != ['GET']:
        utr.methods = interestingMethods

    ## if hasattr(meth, "_roles"):
    ##     utr.roles = meth._roles
    ## if hasattr(meth, '_json'):
    ##     utr.json = meth._json
    if hasattr(meth, '_subKleinQname'):
        utr.subKlein = meth._subKleinQname

    return {rulePath: utr}

