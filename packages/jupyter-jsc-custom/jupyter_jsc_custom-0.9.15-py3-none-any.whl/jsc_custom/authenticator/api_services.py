from jupyterhub.apihandlers.base import APIHandler
from jupyterhub.handlers import default_handlers
from jupyterhub.utils import token_authenticated
from tornado import web


class ServiceAPIHandler(APIHandler):
    """
    Allows us to support more services than just JupyterLab.
    One can switch with a frontend button press or via
    REST API
    """

    @web.authenticated
    async def post(self, service):
        user = self.current_user
        state = await user.get_auth_state()
        if service in state.get("services_available", []):
            state["service_active"] = service
            await user.save_auth_state(state)
            await self.refresh_auth(user, force=True)
        else:
            self.log.debug(
                "{} not part of list {}".format(
                    service, state.get("services_available", [])
                )
            )
            self.set_status(403)
            return
        self.set_status(204)
        return


class ServiceTokenAPIHandler(APIHandler):
    @token_authenticated
    async def post(self, service):
        user = self.get_current_user_token()
        state = await user.get_auth_state()
        if service in state.get("services_available", []):
            state["service_active"] = service
            await user.save_auth_state(state)
            await self.refresh_auth(user, force=True)
        else:
            self.log.debug(
                "{} not part of list {}".format(
                    service, state.get("services_available", [])
                )
            )
            self.set_status(403)
            return
        self.set_status(204)
        return


default_handlers.append((r"/api/service/([^/]+)", ServiceAPIHandler))
default_handlers.append((r"/api/servicetoken/([^/]+)", ServiceTokenAPIHandler))
