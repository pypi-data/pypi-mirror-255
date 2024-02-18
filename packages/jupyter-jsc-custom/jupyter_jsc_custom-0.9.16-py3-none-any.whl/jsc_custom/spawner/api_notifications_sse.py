import asyncio

from jupyterhub.apihandlers import default_handlers
from jupyterhub.apihandlers.users import SpawnProgressAPIHandler
from jupyterhub.scopes import needs_scope
from tornado import web

from .utils import get_general_spawn_event
from .utils import get_user_spawner_events


class GeneralSpawnNotificationAPIHandler(SpawnProgressAPIHandler):
    """EventStream handler alerting new spawns with no specific information"""

    async def get(self):
        self.set_header("Cache-Control", "no-cache")
        asyncio.ensure_future(self.keepalive())
        event = get_general_spawn_event()
        await event.wait()
        # No need to send any data since we just want to notify a new spawn has occured
        await self.send_event({})
        event.clear()
        return
    

class UserSpawnNotificationAPIHandler(SpawnProgressAPIHandler):
    """EventStream handler for active spawns for a specific user"""

    @needs_scope("read:servers")
    async def get(self, user_name):
        self.set_header("Cache-Control", "no-cache")
        user = self.find_user(user_name)
        if user is None:
            # no such user
            raise web.HTTPError(404)

        # start sending keepalive to avoid proxies closing the connection
        asyncio.ensure_future(self.keepalive())

        events = get_user_spawner_events(user.id)
        await events["start"].wait()
        spawners = user.spawners.values()
        # Set active spawners as event data
        event_data = {s.name: s.pending for s in spawners if s.pending}
        await self.send_event(event_data)
        # Clear event after sending in case stream has been closed
        events["start"].clear()
        return
    

default_handlers.append(
    (r"/api/notifications/spawners", GeneralSpawnNotificationAPIHandler)
)
default_handlers.append(
    (r"/api/users/([^/]+)/notifications/spawners", UserSpawnNotificationAPIHandler)
)
