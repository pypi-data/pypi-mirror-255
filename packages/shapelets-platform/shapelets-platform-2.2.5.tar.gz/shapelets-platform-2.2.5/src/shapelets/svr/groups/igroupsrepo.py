from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..model import GroupAttributes, GroupField, GroupProfile, UserInGroup, UserProfile


class IGroupsRepo(ABC):

    @abstractmethod
    def create(self, details: GroupAttributes) -> Optional[GroupProfile]:
        """
        Creates a new group
        param details: Group Attributes with the group details.
        """
        pass

    @abstractmethod
    def get_group_by_remote_id(self, group_id: int) -> Optional[GroupProfile]:
        """
        Return group details for the giving ID
        param group_id: Group ID.
        """
        pass

    @abstractmethod
    def update_group_info(self, new_attributes: GroupProfile):
        """
        Updates group details for the giving ID
        param new_attributes: Group Attributes with the new group details.
        """
        pass

    @abstractmethod
    def get_all(self,
                sort_by: Optional[List[Tuple[GroupField, bool]]] = None,
                limit: Optional[int] = None
                ) -> List[GroupProfile]:
        """
        Returns all the groups in the system.
        param sort_by: sort by any group attribute.
        param limit: max number of groups to return.
        """
        pass

    @abstractmethod
    def get_one(self, group_id: int = None, group_name=None) -> Optional[GroupProfile]:
        """
        Returns all the groups in the system.
        param group_id
        """
        pass

    @abstractmethod
    def get_all_by_user(self, user_id: int) -> List[GroupProfile]:
        """
        Returns all the groups in the system.
        param user_id: id of the user requesting groups.
        """
        pass

    @abstractmethod
    def update_group_user_permission(self, users: List[UserInGroup], group_id: int) -> bool:
        """
        Update user permission for the given group
        """
        pass

    @abstractmethod
    def group_name_exists(self, group_name: str) -> bool:
        """
        Check if a group name already exists in the system
        param group_name
        """
        pass

    @abstractmethod
    def delete_by_id(self, uid: int):
        """
        Delete group providing its id.
        param uid
        """
        pass

    @abstractmethod
    def delete_by_name(self, group_name: str) -> str:
        """
        Delete group providing its name.
        param group_name
        """
        pass

    @abstractmethod
    def delete_all(self):
        """
        Delete all groups in the system
        """
        pass

    @abstractmethod
    def all_users_in_group(self, group_id: int) -> List[UserProfile]:
        """
        Returns all users belonging to the group.
        param group_id
        """
        pass

    @abstractmethod
    def admin_group(self) -> GroupProfile:
        """
        Retrieve a group with all the superAdmin users.
        """
        pass
