from blacksheep import FromJSON
from blacksheep.server.controllers import ApiController, get, post, Request, put, delete
from requests import Session
from typing import List, Optional

from . import groupshttpdocs, IGroupsService, InvalidGroupName

from ..docs import docs
from ..model import GroupProfile, GroupAttributes, UserInGroup
from ..telemetry import ITelemetryService
from ..users import IUsersService, check_user_identity, super_admin


class GroupsHttpServer(ApiController):
    def __init__(self, svr: IGroupsService, telemetry: ITelemetryService, users: IUsersService) -> None:
        self._svr = svr
        self._telemetry = telemetry
        self._users = users
        super().__init__()

    @classmethod
    def route(cls) -> Optional[str]:
        return '/api/groups'

    @get("all")
    @docs(groupshttpdocs.get_all)
    async def get_all(self, request: Request) -> List[GroupProfile]:
        """
        Retrieve the list of all groups to which a user belongs. If superAdmin, no user filter is applied.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            if super_admin(user_details):
                return self.json(self._svr.get_all())
            return self.json(self._svr.get_all_by_user(user_id))
        except Exception as e:
            return self.status_code(500, str(e))

    @post("/")
    @docs(groupshttpdocs.create_group)
    async def create(self, request: Request, group: FromJSON[GroupAttributes]) -> Optional[GroupProfile]:
        """
        Create group. Expect name and description of the group.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            # group.value.usersInGroup = [user_details.nickName]
            new_group = self._svr.create(group.value)
            # Once created, add user to group
            self._users.add_to_group(user_details.nickName, new_group.name, True, True)
            self._telemetry.send_telemetry(event="GroupCreated", info={"group_name": new_group.name})
            return self.json(new_group)
        except Exception as e:
            return self.status_code(500, str(e))

    @get("{groupId}")
    @docs(groupshttpdocs.get_one_group)
    async def get_one(self, request: Request, groupId: int) -> Optional[GroupProfile]:
        """
        Returns details of the given group.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            group = self._svr.get_one(group_id=groupId)
            if super_admin(user_details) or user_details.nickName in [user.nickName for user in group.usersInGroup]:
                return self.json(group)
            return self.unauthorized("Current user cannot view details.")
        except Exception as e:
            return self.status_code(500, str(e))

    @put("{groupId}")
    @docs(groupshttpdocs.update_group)
    async def update_group(self, request: Request, data: FromJSON[GroupProfile]) -> bool:
        """
        Update info of the group, add users and update user permission of the given group.
        Only local groups are allowed to change name and description. Cloud groups only change user permissions.
        In addition, only users with administrative permissions for the group are authorized to perform this action.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            # superAdmin, can update group
            if super_admin(user_details):
                update_details = GroupProfile(uid=data.value.uid, name=data.value.name,
                                              description=data.value.description,
                                              provider=data.value.provider,
                                              providerGroupId=data.value.providerGroupId,
                                              usersInGroup=[UserInGroup(**user) for user in data.value.usersInGroup])
                response = self._svr.update_group(update_details)
                return self.ok(response)
            else:
                # Regular user, check if the user has admin permission over the group.
                users_in_group = self._svr.all_users_in_group(data.value.uid)
                for user in users_in_group:
                    if user.uid == user_id and user.admin == 1:
                        update_details = GroupProfile(uid=data.value.uid, name=data.value.name,
                                                      description=data.value.description,
                                                      provider=data.value.provider,
                                                      providerGroupId=data.value.providerGroupId,
                                                      usersInGroup=[UserInGroup(**user) for user in
                                                                    data.value.usersInGroup])
                        response = self._svr.update_group(update_details)
                        self._telemetry.send_telemetry(event="GroupUpdated", info={"group_name": update_details.name})
                        return self.ok(response)
            return self.unauthorized("Current user cannot delete this group.")
        except Exception as e:
            return self.status_code(500, str(e))

    @get("/{groupId}/users")
    @docs(groupshttpdocs.users_in_group)
    async def all_users_in_group(self, groupId: int) -> []:
        """
        Retrieve all users belonging to the specified groupId. The function returns a list containing user information,
        including uid, nickName, picture (if available), read-write and admin permissions. Users without uid are those
        present in the system but have not logged in yet.
        Return example: {uid: 1, nickName: "admin", picture: null, read_write: 1, admin: 0}
        """
        try:
            return self.json(self._svr.all_users_in_group(groupId))
        except Exception as e:
            return self.status_code(500, str(e))

    @delete("/{id}")
    @docs(groupshttpdocs.delete_group)
    async def delete_group_id(self, request: Request, id: str) -> str:
        """
        Remove the designated group. This action is exclusive to users with administrative permissions for the group.
        Only local groups are eligible for deletion.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            if super_admin(user_details):
                group = self._svr.get_one(group_id=id)
                response = self._svr.delete_group(group.name)
                self._telemetry.send_telemetry(event="GroupDelete", info={"group_name": group.name})
                return self.ok(response)
            else:
                users_in_group = self._svr.all_users_in_group(id)
                for user in users_in_group:
                    if user.uid == user_id and user.admin == 1:
                        group = self._svr.get_one(group_id=id)
                        response = self._svr.delete_group(group.name)
                        self._telemetry.send_telemetry(event="GroupDelete", info={"group_name": group.name})
                        return self.ok(response)
            return self.unauthorized("Current user cannot delete this group.")
        except InvalidGroupName as e:
            return self.bad_request(str(e))

    @get('/unp/check')
    @docs(groupshttpdocs.group_name_doc)
    async def group_name_exists(self, groupName: str) -> bool:
        try:
            return self.json(self._svr.group_name_exists(groupName))
        except Exception as e:
            return self.status_code(500, str(e))

    @delete()
    @docs(groupshttpdocs.delete_all)
    async def delete_all(self, request: Request):
        """
        Delete all groups. Only local groups are eligible for deletion. This action is exclusive to users with
        super administrative permissions over the system.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            if super_admin(user_details):
                response = self.json(self._svr.delete_all())
                self._telemetry.send_telemetry(event="GroupDeleteAll")
                return response
            return self.unauthorized("User has no permission.")
        except Exception as e:
            return self.status_code(500, str(e))

    @get("admin")
    @docs(groupshttpdocs.admin)
    async def get_admin_group(self, request: Request) -> GroupProfile:
        """
        Retrieve a group with all the superAdmin users.
        """
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            if super_admin(user_details):
                return self.json(self._svr.admin_group())
            return self.unauthorized("User has no permission.")
        except Exception as e:
            return self.status_code(500, str(e))


class GroupsHttpProxy(IGroupsService):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, group_name: str, group_description: str) -> Optional[GroupProfile]:
        response = self.session.post(
            '/api/groups/', params=[("groupName", group_name), ("groupDescription", group_description)])
        if response.status_code == 400 or response.status_code == 500:
            raise Exception(response.content)
        return response.json()

    def get_all(self) -> List[GroupProfile]:
        response = self.session.get('/api/groups/unp/all')
        return response.json()

    def get_one(self, group_id: int = None, group_name: str = None) -> Optional[GroupProfile]:
        pass

    def get_all_by_user(self) -> List[GroupProfile]:
        response = self.session.get('/api/groups/')
        return response.json()

    def update_group(self) -> List[GroupProfile]:
        pass

    def group_name_exists(self, group_name: str) -> bool:
        response = self.session.get('/api/groups/unp/check', params=[("groupName", group_name)])
        if response.status_code == 400:
            raise InvalidGroupName(group_name)
        return response.ok and bool(response.json() == True)

    def delete_group(self, group_id: str) -> str:
        response = self.session.delete('/api/groups/{id}', params=[("id", group_id)])
        if response.status_code == 400:
            raise InvalidGroupName(group_id)
        return response.json()

    def delete_all(self) -> bool:
        response = self.session.get('/api/groups/unp/removeAll')
        return response.ok and bool(response.json() == True)

    def all_users_in_group(self, group_name: str):
        raise RuntimeError("TODO")

    def admin_group(self):
        raise RuntimeError("TODO")
