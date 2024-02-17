from typing import List, Optional, Tuple

from .igroupsrepo import IGroupsRepo
from .igroupsservice import IGroupsService

from ..model import GroupAttributes, GroupField, GroupProfile, UserInGroup, UserProfile


class GroupsService(IGroupsService):
    __slots__ = ('_groups_repo',)

    def __init__(self, groups_repo: IGroupsRepo) -> None:
        self._groups_repo = groups_repo

    def create(self, attributes: GroupAttributes) -> GroupProfile:
        if all([attributes.provider, attributes.providerGroupId]):
            # Remote group
            group = self._groups_repo.get_group_by_remote_id(attributes.providerGroupId)
            if group is None or not group:
                # Is name taken?
                if self._groups_repo.group_name_exists(attributes.name):
                    raise Exception(
                        f"Group Name {attributes.name} already in the system. Please, pick a different name.")
                profile = self._groups_repo.create(attributes)
                # self._groups_repo.add_users_to_group()
            elif (attributes.name != group.name
                  or attributes.description != group.description
                  or attributes.usersInGroup != [user.nickName for user in group.usersInGroup]):
                # Update name or description?
                new_info = GroupProfile(uid=group.uid, **dict(attributes))
                self._groups_repo.update_group_info(new_info)
                # Transform users to UserInGroup and Update permissions
                user_in_group = []
                for user in attributes.usersInGroup:
                    existed_user = [user_in for user_in in group.usersInGroup if user_in.nickName == user]
                    if existed_user:
                        user_in_group.append(existed_user[0])
                    else:
                        user_in_group.append(UserInGroup(nickName=user))
                self._groups_repo.update_group_user_permission(user_in_group, group.uid)
                profile = self._groups_repo.get_group_by_remote_id(attributes.providerGroupId)
            else:
                # Group already in db, find it and return it
                profile = self._groups_repo.get_group_by_remote_id(attributes.providerGroupId)
        else:
            # Local group
            profile = self._groups_repo.create(attributes)
        return profile

    def get_all(self,
                sort_by: Optional[List[Tuple[GroupField, bool]]] = None,
                limit: Optional[int] = None
                ) -> List[GroupProfile]:
        return self._groups_repo.get_all(sort_by, limit)

    def get_one(self, group_id: int = None, group_name=None) -> Optional[GroupProfile]:
        return self._groups_repo.get_one(group_id=group_id, group_name=group_name)

    def get_all_by_user(self, user_id: int) -> List[GroupProfile]:
        return self._groups_repo.get_all_by_user(user_id)

    def update_group(self, update_group: GroupProfile) -> bool:
        if update_group.provider == "local":
            # Allow to update name or description
            self._groups_repo.update_group_info(update_group)
        if update_group.usersInGroup is not None:
            # Update permissions
            self._groups_repo.update_group_user_permission(update_group.usersInGroup, update_group.uid)
        return True

    def group_name_exists(self, group_name: str) -> bool:
        return self._groups_repo.group_name_exists(group_name)

    def delete_group(self, group_name: str) -> str:
        return self._groups_repo.delete_by_name(group_name)

    def delete_all(self):
        self._groups_repo.delete_all()

    def all_users_in_group(self, group_id: int) -> List[UserProfile]:
        return self._groups_repo.all_users_in_group(group_id)

    def admin_group(self) -> GroupProfile:
        return self._groups_repo.admin_group()
