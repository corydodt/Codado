"""
Publish docker events
"""
import time

from twisted.internet import reactor

import attr

from docker import Client


SOCKET = 'unix://var/run/docker.sock'


@attr.s
class EventActor(object):
    image = attr.ib()
    name = attr.ib()
    signal = attr.ib()
    id = attr.ib()

    @classmethod
    def fromLowLevelActor(cls, dct):
        a = dct['Attributes']
        id = dct['ID']
        return cls(
                image=a.get('image', None),
                name=a.get('name', None),
                signal=a.get('signal', None), 
                id=id)


@attr.s
class Event(object):
    status = attr.ib()
    id = attr.ib()
    time = attr.ib()
    timeNano = attr.ib()
    actor = attr.ib(convert=EventActor.fromLowLevelActor)
    action = attr.ib()
    eventFrom = attr.ib()
    eventType = attr.ib()

    @property
    def name(self):
        return ".".join([self.eventType, self.action])

    @classmethod
    def fromLowLevelEvent(cls, dct):
        actor = dct.pop('Actor')
        action = dct.pop('Action')
        eventType = dct.pop('Type')
        eventFrom = dct.pop('from', None)
        id = dct.pop('id', None)
        status = dct.pop('status', None)
        return Event(actor=actor, eventFrom=eventFrom, eventType=eventType,
                action=action, id=id, status=status, **dct)


PEEK_INTERVAL_SECONDS = 0.5


@attr.s
class DockerEngine(object):
    base_url = attr.ib(default=SOCKET)
    handlers = attr.ib(default=attr.Factory(dict))
    _stopping = False

    def __get__(self, instance, cls):
        if instance is None:
            return self

        self.owner = instance
        return self

    def run(self):
        client = Client(base_url=self.base_url)
        reactor.callLater(PEEK_INTERVAL_SECONDS, self._genEvents, client, time.time())

    def _genEvents(self, client, since):
        until = time.time()
        for llEvent in client.events(
                decode=True,
                since=since,
                until=until):
            ev = Event.fromLowLevelEvent(llEvent)
            for func_name in self.handlers.get(ev.name, ()):
                getattr(self.owner, func_name)(ev)
        reactor.callLater(PEEK_INTERVAL_SECONDS, self._genEvents, client, until)

    def handler(self, eventName):
        """
        Register a method or function as a handler for an event
        """
        def _deco(fn):
            print "Making %r a handler for %r" % (fn.__name__, eventName)
            self.handlers.setdefault(eventName, []).append(fn.__name__)
            return fn
        return _deco

