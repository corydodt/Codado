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
        print '*' * 5, 'died:', event.container
        self.count = self.count + 1
        if self.count == 3:
            reactor.stop()

    @engine.handler("container.start")
    def onStart(self, event):
        """
        Display the environment of a started container
        """
        c = event.container
        print '+' * 5, 'started:', c
        kv = lambda s: s.split('=', 1)
        env = {k: v for (k, v) in (kv(s) for s in c.attrs['Config']['Env'])}
        print env

    @engine.defaultHandler
    def onWhatever(self, event):
        if event.name in ['container.die']:
            return
        obj = getattr(event, event.eventType)
        print ' '*5, 'other:', event.name, obj


mourner = AppMourner()
reactor.callWhenRunning(mourner.engine.run)
reactor.run()

)
"""
ok here's what noms needs to do

- change nginx-letsencrypt-s3 to nginx-proximation
- this does the same thing it does now, except you DON'T HAVE TO TELL IT WHAT
  THE PROXIES ARE
  
1. build a docker container with environment variable `virtual_host`
2. optionally add `certbot_flags` in that container for --staging
3. just start that shit up.

1. nginx-proximation starts up with just a cron job to run certbot renew
   periodically
2. It also starts up proximationd which tries to read docker events and crashes
   us if it can't (so you must expose the docker engine socket as a volume)
3. it also attempts to acquire or load the letsencrypt cert every time a
   container with virtual_host appears and there is no cert (respecting
   certbot_flags if present)
4. if cert acquisition succeeds, proximationd rebuilds the nginx config file
5. ps. proximationd will also check containers that are already running to see
   if they have virtual_host

"""
