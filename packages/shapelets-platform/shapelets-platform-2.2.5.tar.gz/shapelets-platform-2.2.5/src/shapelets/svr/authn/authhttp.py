import json

from blacksheep import FromJSON, Response, Request
from blacksheep.server.controllers import ApiController, get, post
from pydantic import BaseModel
from requests import Session
from typing import Dict, Optional, Union

from . import authhttpdocs

from .iauthservice import (
    Addresses,
    Challenge,
    IAuthService,
    InvalidUserName,
    UnknownUser,
    VerificationError
)
from .gc_client import gc_flow
from ..docs import docs
from ..groups import IGroupsService
from ..license import ILicenseService
from ..model import GCPrincipalId, GroupAttributes, SignedPrincipalId, UserAttributes
from ..settings import add_user_to_client, Settings
from ..users import check_user_identity, IUsersRepo
from ..utils import FlexBytes
from ..telemetry import ITelemetryService


def _verify_server_domain(domain: str, email: str) -> bool:
    """
    When there is an external login, it is essential to verify that the login credentials belong to the domain of the
    server. For instance, if the server owner has set a domain of my-company.io, any login attempt outside of that
    domain should be denied.
    """
    email_split = email.split('@')
    if len(email_split) == 2:
        email_domain = email_split[1]
    else:
        raise "Invalid email format"
    return domain == email_domain


class VerifyChallenge(BaseModel):
    userName: str
    nonce: Optional[FlexBytes]
    token: FlexBytes
    rememberMe: bool

    class Config:
        json_encoders = {
            FlexBytes: lambda v: str(v)
        }


class Registration(BaseModel):
    userName: str
    salt: FlexBytes
    pk: FlexBytes

    user_details: Optional[UserAttributes] = None

    class Config:
        json_encoders = {
            FlexBytes: lambda v: str(v)
        }


class GetTokenRequest(BaseModel):
    gc: GCPrincipalId
    user_details: Optional[UserAttributes]

    class Config:
        json_encoders = {
            FlexBytes: lambda v: str(v)
        }


class AuthHttpServer(ApiController):
    def __init__(self,
                 settings: Settings,
                 svr: IAuthService,
                 telemetry: ITelemetryService,
                 groups: IGroupsService,
                 users: IUsersRepo,
                 license: ILicenseService
                 ) -> None:
        self._svr = svr
        self._telemetry = telemetry
        self._groups = groups
        self._users = users
        self._settings = settings
        self._license = license
        super().__init__()

    @classmethod
    def route(cls) -> Optional[str]:
        return '/api/login'

    @get('/unp/check')
    @docs(authhttpdocs.check_user_exists)
    async def check_user_exists(self, username: str) -> bool:
        try:
            return self.json(self._svr.user_name_exists(username))
        except InvalidUserName as e:
            return self.bad_request(str(e))
        except Exception as e:
            return self.status_code(500, str(e))

    @get('/unp/remove')
    @docs(authhttpdocs.remove_user)
    async def remove_user(self, request: Request, userName: str, transfer: str = None) -> bool:
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            if hasattr(user_details, "superAdmin") and user_details.superAdmin == 1:
                self._svr.remove_user(userName, transfer)
                self._telemetry.send_telemetry(event="UserRemove", info={"remove_by": user_details.nickName,
                                                                         "user_remove": userName})
                return self.ok(True)
            return self.unauthorized(f"User {user_details.nickName} cannot perform this action.")
        except InvalidUserName as e:
            return self.bad_request(str(e))
        except Exception as e:
            return self.status_code(500, str(e))

    @get('/unp/challenge')
    @docs(authhttpdocs.generate_challenge)
    async def generate_challenge(self, userName: str) -> Challenge:
        try:
            return self.json(json.loads(self._svr.generate_challenge(userName).json()))
        except InvalidUserName as e:
            return self.bad_request(str(e))
        except UnknownUser as e:
            return self.not_found(str(e))
        except Exception as e:
            return self.status_code(500, str(e))

    @post('/unp/authenticate')
    @docs(authhttpdocs.verify_challenge)
    async def verify_challenge(self, details: FromJSON[VerifyChallenge]) -> Response:
        data = details.value
        try:
            principal = self._svr.verify_challenge(data.userName, data.nonce, data.token)
            return self.ok(principal.to_token())
        except InvalidUserName as e:
            return self.bad_request(str(e))
        except VerificationError as e:
            return self.unauthorized(str(e))
        except Exception as e:
            return self.status_code(500, str(e))

    @post('/unp/register')
    @docs(authhttpdocs.new_registration)
    async def new_registration(self, details: FromJSON[Registration]) -> Response:
        data: Registration = details.value
        user_details = data.user_details or UserAttributes(nickName=data.userName)
        user_id = self._svr.register(data.userName, data.salt, data.pk, user_details)
        if user_id is not None:
            self._telemetry.send_telemetry(event="UserCreated", info={"user_id": user_id})
            return self.ok(user_id is not None)
        return self.not_found("Unable to create user")

    @get('/available/{protocol}')
    @docs(authhttpdocs.is_protocol_available)
    async def available(self, protocol: str):
        return self.ok(self._svr.available(protocol))

    @get('/available')
    @docs(authhttpdocs.available_providers)
    async def providers(self):
        return self.ok(self._svr.providers())

    @get('/addresses')
    @docs(authhttpdocs.addresses)
    async def addresses(self, protocol: str, req: Optional[str] = None):
        return self._svr.compute_addresses(protocol, req)

    @get('/verify')
    @docs(authhttpdocs.verify_token)
    async def verify(self, token: str):
        return self.ok(self._svr.verify(token))

    @post('/token')
    @docs(authhttpdocs.get_token)
    async def get_token(self, details: FromJSON[GetTokenRequest]):
        principal = self._svr.auth_token(details.value.gc, details.value.user_details)
        return self.ok(principal.to_token())

    @get('/redirectProvider')
    @docs(authhttpdocs.redirect_provider)
    async def redirect_provider(self, request: Request):
        provider = request.query["provider"][0]
        if not self._svr.available(provider):
            raise RuntimeError(f"Authentication flow for {provider} is not available at the moment.")
        tel_id = self._telemetry._id
        addresses = self._svr.compute_addresses(provider, tel_id)
        return self.ok(addresses)

    @post('/externalLogin')
    @docs(authhttpdocs.external_login)
    async def login_external(self, request: Request):
        # First, let's check if user has license for this request
        if self._license.license_type() != "Commercial":
            raise RuntimeError("Enterprise logins are exclusively permitted with a valid Commercial License.")
        addresses = Addresses(**json.loads(request.query["address"][0]))
        remember_me = True
        try:
            gc_principal_id, user_details = gc_flow(addresses)
        except Exception:
            return self.forbidden("Unable to login externally")
        # Ensure that the individual logging in is a member of the server domain.
        if self._settings.server.domain:
            if not _verify_server_domain(self._settings.server.domain, user_details.email):
                return self.bad_request("External logins are not allowed for the given domain.")
        signed_principal = self._svr.auth_token(gc_principal_id, user_details)
        user_name = user_details.nickName if user_details.nickName is not None else user_details.email

        # Save Remote Groups
        if user_details.remoteGroups:
            group_ids = []
            for group in user_details.remoteGroups:
                group_attributes = GroupAttributes(
                    name=group.groupName,
                    description=group.groupDescription,
                    provider=user_details.provider,
                    providerGroupId=group.groupId,
                    usersInGroup=group.usersInGroup)
                # Create group and save its uid
                group_ids.append(self._groups.create(group_attributes).uid)

            # Verify whether the user is already registered on the platform, or this login marks their initial access.
            remote_temp_users = self._users.find_remote_temp_user(user_name)
            if remote_temp_users is not None:
                self._users.update_remote_user_id(remote_temp_users, signed_principal.userId)
                self._users.delete_remote_temp_user(user_name)
            # Assign groups to user
            self._users.add_remote_groups(signed_principal.userId, group_ids)

        if remember_me:
            # add user to current settings
            host = self._settings.server.host
            current_client = None
            for client, info in self._settings.client.clients.items():
                if host == info.host:
                    current_client = client
                    break
            if current_client:
                # add settings to settings.toml
                add_user_to_client(str(host), user_name, signed_principal, False)

        return self.ok(signed_principal.to_token())


class AuthHttpProxy(IAuthService):
    def __init__(self, session: Session) -> None:
        self.session = session

    def user_name_exists(self, userName: str) -> bool:
        response = self.session.get('/api/login/unp/check', params=[("username", userName)])

        if response.status_code == 400:
            raise InvalidUserName(userName)

        return response.ok and bool(response.json() == True)

    def remove_user(self, userName: str, transfer: str = None) -> int:
        response = self.session.get('/api/login/unp/remove', params=[("userName", userName), ("transfer", transfer)])
        if response.status_code != 200:
            raise Exception(response.content)

        return response.ok and bool(response.json() == True)

    def generate_challenge(self, userName: str) -> Challenge:
        response = self.session.get('/api/login/unp/challenge', params=[("userName", userName)])
        if response.status_code == 400:
            raise InvalidUserName(userName)
        elif response.status_code == 404:
            raise UnknownUser(userName)
        elif response.status_code != 200:
            raise RuntimeError(response.text)

        return Challenge.parse_obj(response.json())

    def verify_challenge(self, userName: str, nonce: Optional[bytes], token: bytes) -> SignedPrincipalId:
        payload = VerifyChallenge(userName=userName,
                                  nonce=nonce,
                                  token=token,
                                  rememberMe=False)

        response = self.session.post('/api/login/unp/authenticate', json=json.loads(payload.json()))
        if response.status_code == 400:
            raise InvalidUserName(userName)
        elif response.status_code == 401:
            raise VerificationError(response.text)
        elif response.status_code != 200:
            raise RuntimeError(response.text)

        token = response.text
        principal = SignedPrincipalId.from_token(token)
        if principal is None:
            raise RuntimeError(f"Unable to decode token [{token}]")

        return principal

    def register(self, userName: str, salt: bytes, verify_key: bytes, user_details: UserAttributes) -> Response:
        payload = Registration(userName=userName, salt=salt, pk=verify_key, user_details=user_details)
        response = self.session.post('/api/login/unp/register', json=json.loads(payload.json()))
        return response

    def available(self, protocol: str) -> bool:
        response = self.session.get(f'/api/login/available/{protocol}')
        return response.ok and bool(response.json() == True)

    def providers(self) -> Dict[str, bool]:
        response = self.session.get('/api/login/available')
        response.raise_for_status()
        return response.json()

    def compute_addresses(self, protocol: str, req: Optional[str] = None) -> Optional[Addresses]:
        params = [('protocol', protocol)]
        if req is not None:
            params.append(('req', req))

        response = self.session.get('/api/login/addresses', params=params)
        response.raise_for_status()
        data = response.json()
        if len(data) == 0:
            return None
        return Addresses.parse_obj(data)

    def verify(self, principal: Union[SignedPrincipalId, str]) -> bool:
        token = principal.to_token() if isinstance(principal, SignedPrincipalId) else str(principal)
        response = self.session.get('/api/login/verify', params=[('token', token)])
        return response.ok and bool(response.json() == True)

    def auth_token(self, principal: GCPrincipalId, user_details: Optional[UserAttributes] = None) -> SignedPrincipalId:
        token_request = GetTokenRequest(gc=principal, user_details=user_details)
        response = self.session.post('/api/login/token', json=json.loads(token_request.json()))
        response.raise_for_status()
        return SignedPrincipalId.from_token(response.text)

    def associate_unp(self, principal: SignedPrincipalId, new_user_name: str, new_salt: bytes, new_verify_key: bytes):
        """
        Associates (or updates) a user-name/password combination to the current logged user.
        """
        raise RuntimeError("TODO")

    def associate(self, principal: SignedPrincipalId, new_principal: GCPrincipalId):
        """
        Associate an external credential to the current logged user
        """
        raise RuntimeError("TODO")

    def disassociate(self, principal: SignedPrincipalId, scope: str):
        """
        Disassociates a particular authentication protocol 
        """
        raise RuntimeError("TODO")
