from blacksheep import Request, Response
from blacksheep.server.controllers import ApiController, delete, get, post, put
from requests import Session
from typing import List, Optional, Union

from . import IUsersService, usershttpdocs
from .user_identity import check_user_identity
from ..docs import docs
from ..model import PrincipalId, ResolvedPrincipalId, UserProfile


class InvalidGroupName(Exception):
    def __init__(self, groupName: str, *args: object) -> None:
        self._groupName = groupName
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Invalid group name {self._groupName}"


class UsersHttpServer(ApiController):
    def __init__(self, svr: IUsersService) -> None:
        self._svr = svr
        super().__init__()

    @classmethod
    def route(cls) -> Optional[str]:
        return '/api/users'

    @get("/")
    @docs(usershttpdocs.user_list)
    async def user_list(self, request: Request) -> List[UserProfile]:
        user_id = check_user_identity(request)
        user_details = self._svr.get_user_details(user_id)
        if hasattr(user_details, "superAdmin") and user_details.superAdmin == 1:
            return self.json(self._svr.get_all())
        return self.unauthorized(f"User {user_details.nickName} cannot perform this action.")

    @delete("/")
    @docs(usershttpdocs.delete_all_users)
    async def delete_all_users(self, request: Request) -> bool:
        user_id = check_user_identity(request)
        user_details = self._svr.get_user_details(user_id)
        if hasattr(user_details, "superAdmin") and user_details.superAdmin == 1:
            return self._svr.delete_all()
        return self.unauthorized(f"User {user_details.nickName} cannot perform this action.")

    @post("/checkNickName")
    @docs(usershttpdocs.nickname_doc)
    async def check_nickname(self, nickName: str) -> bool:
        return self._svr.nickname_exists(nickName)

    @get("/me")
    @docs(usershttpdocs.me_doc)
    async def my_details(self, request: Request) -> UserProfile:
        user_id = check_user_identity(request)
        if user_id:
            return self._svr.get_user_details(user_id)
        return False

    @get("/{id}")
    @docs(usershttpdocs.get_user_details)
    async def get_user_details(self, id: int) -> Optional[UserProfile]:
        return self._svr.get_user_details(id)

    @put("/{id}")
    @docs(usershttpdocs.update_user_details)
    async def update_user_details(self, id: int, details: UserProfile) -> Optional[UserProfile]:
        self._svr.update_user_details(id, details)

    @delete("/{id}")
    @docs(usershttpdocs.delete_user)
    async def delete_user(self, request: Request, id: int) -> Response:
        user_id = check_user_identity(request)
        user_details = self._svr.get_user_details(user_id)
        if hasattr(user_details, "superAdmin") and user_details.superAdmin == 1:
            self._svr.delete_user(id)
            return self.ok("User removed successfully.")
        return self.unauthorized(f"User {user_details.nickName} cannot perform this action.")

    @put("/{userName}/groups")
    @docs(usershttpdocs.add_to_group)
    async def add_to_group(self, userName: str, groups: list, write: bool, admin: bool):
        try:
            if self.json(self._svr.add_to_group(userName, groups, write, admin)):
                return self.ok(f"User {userName} added successfully to group/s {groups}")
            return self.bad_request()
        except InvalidGroupName as e:
            return self.bad_request(str(e))
        except Exception as e:
            return self.status_code(500, str(e))

    @delete("/{userName}/groups")
    @docs(usershttpdocs.remove_from_group)
    async def remove_from_group(self, userName: str, groups: list):
        try:
            if self._svr.remove_from_group(userName, groups):
                return self.ok(f"User {userName} removed successfully from group/s {groups}")
            return self.bad_request()
        except InvalidGroupName as e:
            return self.bad_request(str(e))
        except Exception as e:
            return self.status_code(500, str(e))


class UsersHttpProxy(IUsersService):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self) -> List[UserProfile]:
        response = self.session.get('/api/users/')
        return response.json()

    def delete_user(self, id: int):
        self.session.delete('/api/users/{id}', params=[("id", id)])

    def delete_all(self) -> bool:
        self.session.delete('/api/users/')
        return True

    def get_user_details(self, id: int) -> Optional[UserProfile]:
        return self.session.get('/api/users/{id}', params=[("id", id)])

    def update_user_details(self, id: int, details: UserProfile) -> Optional[UserProfile]:
        self.session.put('/api/users/{id}', params=[("id", id), ("details", details)])
        pass

    @docs(usershttpdocs.nickname_doc)
    def nickname_exists(self, nickName: str) -> bool:
        return self.session.get('/api/users/checkNickName', params=[("nickName", nickName)])

    def get_principals(self, id: int) -> List[PrincipalId]:
        return self.session.get('/api/users/{id}/principals', params=[("id", id)])

    def dissociate_principal(self, principal: PrincipalId):
        pass

    def verify_principal(self, resolved_principal: ResolvedPrincipalId) -> bool:
        pass

    def resolve_principal(self, scope: str, pid: str) -> Optional[ResolvedPrincipalId]:
        pass

    def add_to_group(self, user_name: str, groups: Union[List[str], str], write: bool = False, admin: bool = False):
        response = self.session.put(f'/api/users/{user_name}/groups',
                                    params=[("userName", user_name), ("groups", groups), ("write", write),
                                            ("admin", admin)])
        if response.status_code != 200:
            raise Exception(response.content)
        print(response.content)

    def remove_from_group(self, user_name: str, groups: Union[List[str], str]):
        response = self.session.delete(f'/api/users/{user_name}/groups',
                                       params=[("userName", user_name), ("groups", groups)])
        if response.status_code != 200:
            raise Exception(response.content)
        print(response.content)

    def get_user_groups(self, id: int):
        response = self.session.get('/api/users/{id}/groups', params=[("id", id)])
        pass

    @docs(usershttpdocs.me_doc)
    def my_details(self) -> UserProfile:
        return self.session.get('/api/users/me')

    def add_remote_groups(self, user_id: int, groups: List[str], write: bool = False) -> bool:
        pass

    def find_remote_temp_user(self, user_name: str) -> int:
        pass

    def delete_remote_temp_user(self, user_name: str) -> bool:
        pass

    def update_remote_user_id(self, old_id: int, new_id: int):
        pass
