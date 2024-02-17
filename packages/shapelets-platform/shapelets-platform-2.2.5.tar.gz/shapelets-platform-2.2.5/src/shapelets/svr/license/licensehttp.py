from blacksheep.server.controllers import ApiController, get
from requests import Session
from typing import Optional

from . import ILicenseService, licensehttpdocs
from ..docs import docs


class LicenseHttpServer(ApiController):
    def __init__(self, svr: ILicenseService) -> None:
        self._svr = svr
        super().__init__()

    @classmethod
    def route(cls) -> Optional[str]:
        return '/api/license'

    @get("/status")
    @docs(licensehttpdocs.license_status)
    async def license_status(self) -> str:
        return self._svr.license_status()

    @get("/version")
    @docs(licensehttpdocs.license_version)
    async def license_version(self) -> int:
        return self._svr.current_version()

    @get("/type")
    @docs(licensehttpdocs.license_type)
    async def license_type(self) -> int:
        return self._svr.license_type()


class LicenseHttpProxy(ILicenseService):
    def __init__(self, session: Session) -> None:
        self.session = session

    def license_status(self) -> str:
        response = self.session.get('/api/license/status')
        return response.content.decode("utf-8")

    def current_version(self) -> int:
        response = self.session.get('/api/license/version')
        return response.content.decode("utf-8")

    def license_type(self) -> str:
        response = self.session.get('/api/license/type')
        return response.content.decode("utf-8")

    def last_license_version(self) -> bool:
        pass

    def request_evaluation_license(self):
        pass

    def request_license(self, license_id: str = None):
        pass

    def revoke_license(self):
        pass
