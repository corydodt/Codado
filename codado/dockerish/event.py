"""
Publish docker events
"""
import time

import attr

from twisted.internet import reactor

import docker


ALL_EVENTS = '__all_events__'

VALID_EVENTS = (
    ALL_EVENTS,
    'container.attach',
    'container.commit',
    'container.copy',
    'container.create',
    'container.destroy',
    'container.detach',
    'container.die',
    'container.exec_create',
    'container.exec_detach',
    'container.exec_start',
    'container.export',
    'container.health_status',
    'container.kill',
    'container.oom',
    'container.pause',
    'container.rename',
    'container.resize',
    'container.restart',
    'container.start',
    'container.stop',
    'container.top',
    'container.unpause',
    'container.update',

    'image.delete',
    'image.import',
    'image.load',
    'image.pull',
    'image.push',
    'image.save',
    'image.tag',
    'image.untag',

    'plugin.install',
    'plugin.enable',
    'plugin.disable',
    'plugin.remove',

    'volume.create',
    'volume.mount',
    'volume.unmount',
    'volume.destroy',

    'network.create',
    'network.connect',
    'network.disconnect',
    'network.destroy',

    'daemon.reload',

    # special event specific to the dockerish framework itself
    'dockerish.init',
)


@attr.s
class EventActor(object):
    """
    The source of the event, e.g. the container for a start event or the image
    for a pull event.
    """
    image = attr.ib()
    name = attr.ib()
    signal = attr.ib()
    id = attr.ib()

    @classmethod
    def fromLowLevelActor(cls, dct):
        """
        Build an instance of this class from the dict coming from the
        docker-py event
        """
        # this method is called automatically by convert= when instantiating
        # an event, but we can skip it if we this is already an actual EventActor
        if isinstance(dct, EventActor):
            return dct

        a = dct['Attributes']
        id = dct['ID']
        return cls(
                image=a.get('image', None),
                name=a.get('name', None),
                signal=a.get('signal', None),
                id=id)


@attr.s
class Event(object):
    """
    A generic docker event, constructed from the dict returned by docker-py
    """
    status = attr.ib()
    id = attr.ib()
    time = attr.ib()
    timeNano = attr.ib()
    actor = attr.ib(convert=EventActor.fromLowLevelActor)
    action = attr.ib()
    eventFrom = attr.ib()
    eventType = attr.ib()
    engine = attr.ib()

    @property
    def container(self):
        try:
            return self.engine.client.containers.get(self.actor.id)
        except docker.errors.NotFound:
            # This mainly happens when a container dies or is destroyed
            return None

    @property
    def image(self):
        return self.engine.client.images.get(self.actor.name)

    @property
    def plugin(self):
        return self.engine.client.plugins.get(self.actor.name)

    @property
    def volume(self):
        return self.engine.client.volumes.get(self.actor.id)

    @property
    def network(self):
        try:
            return self.engine.client.networks.get(self.actor.id)
        except docker.errors.NotFound:
            # This mainly happens when a network is destroyed
            return None

    @property
    def daemon(self):
        return self.engine.client

    @property
    def name(self):
        """
        The dotted event name, e.g. `container.die`
        """
        return ".".join([self.eventType, self.action])

    @classmethod
    def fromLowLevelEvent(cls, engine, dct):
        """
        Use the raw event dict from docker-py to build an Event
        """
        return Event(
                engine=engine,
                actor=dct.pop('Actor'),
                eventFrom=dct.pop('from', None),
                eventType=dct.pop('Type'),
                action=dct.pop('Action'),
                id=dct.pop('id', None),
                status=dct.pop('status', None),
                time=dct.pop('time'),
                timeNano=dct.pop('timeNano'),
                **dct)


PEEK_INTERVAL_SECONDS = 0.5


@attr.s
class DockerEngine(object):
    """
    Connection to and interface with a docker engine. Listens for events
    from docker by sampling every 0.5s, then reports these events to bound
    listeners, which are created using the @handler decorator.
    """
    handlers = attr.ib(default=attr.Factory(dict))

    callLater = reactor.callLater

    def __get__(self, instance, cls):
        """
        Set the 'owner' on the DockerEngine instance, as a side effect of
        accessing the attribute from the owner

        FIXME: is there a cleaner way to do this than relying on the side
        effect of accessing the descriptor?
        """
        if instance is None:
            return self

        self.owner = instance
        return self

    def run(self):
        """
        Connect to the docker engine and begin listening for docker events
        """
        self.client = docker.from_env()

        now = time.time()
        nowNano = now * 1000000000
        startEvent = Event(status='init',
                id=None,
                time=int(now),
                timeNano=int(nowNano),
                actor=EventActor(image=None, name=None, signal=None, id=None),
                action='init',
                eventFrom=None,
                eventType='dockerish',
                engine=self,
                )
        self.callLater(0, self._callHandlers, 'dockerish.init', startEvent)
        self.callLater(PEEK_INTERVAL_SECONDS, self._genEvents, time.time())

    def _callHandlers(self, eventName, event):
        """
        Fire all handlers that are listening for this event
        """
        for func_name in self.handlers.get(ALL_EVENTS, ()):
            getattr(self.owner, func_name)(event)

        for func_name in self.handlers.get(eventName, ()):
            getattr(self.owner, func_name)(event)

    def _genEvents(self, since):
        """
        Gather docker events, beginning from the timestamp `since`.
        """
        until = time.time()
        for llEvent in self.client.events(
                decode=True,
                since=since,
                until=until):
            ev = Event.fromLowLevelEvent(self, llEvent)

            self._callHandlers(ev.name, ev)

        self.callLater(PEEK_INTERVAL_SECONDS, self._genEvents, until)

    def handler(self, eventName):
        """
        Register a method or function as a handler for an event

        `eventName` must be specified as a dotted notation which categorizes
        each event, such as `container.die` or `image.pull`.

        The category determines what property is available on the event
        object, for example ".container" for container events.
        """
        def _deco(fn):
            print "Making %r a handler for %r" % (fn.__name__, eventName)
            assert eventName in VALID_EVENTS, "%r is not a docker event" % eventName
            self.handlers.setdefault(eventName, []).append(fn.__name__)
            return fn
        return _deco

    def defaultHandler(self, fn):
        """
        Register a method or function as a handler for ALL events

        You may register multiple methods or functions as defaultHandlers
        """
        return self.handler(ALL_EVENTS)(fn)
