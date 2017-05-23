"""
Sample: A DockerEngine monitor that reacts to `die` events by quitting.

This sample prints out information about the container that died, whenever it
receives the event.
"""

from twisted.internet import reactor

from codado.dockerish import DockerEngine


class AppMourner(object):
    """
    When I receive 3 die events from any container in the local engine, quit.
    """
    engine = DockerEngine()
    count = 0

    @engine.handler("container.die")
    def onDie(self, event):
        print event
        print event.container
        self.count = self.count + 1
        if self.count == 3:
            reactor.stop()


mourner = NomsMourner()
reactor.callWhenRunning(mourner.engine.run)
reactor.run()

