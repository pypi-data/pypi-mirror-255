# Copyright (c) 2022 Shapelets.io
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..model import GroupAttributes, GroupField, GroupProfile, UserProfile


class InvalidGroupName(Exception):
    def __init__(self, groupName: str, *args: object) -> None:
        self._groupName = groupName
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Invalid group name {self._groupName}"


class IGroupsService(ABC):
    @abstractmethod
    def create(self, attributes: GroupAttributes) -> GroupProfile:
        """
        Creates a new group

        Parameters
        ----------
        attributes: Group Attributes with the group details.

        Returns
        -------
        Group just created
        """
        pass

    @abstractmethod
    def get_all(self,
                sort_by: Optional[List[Tuple[GroupField, bool]]] = None,
                limit: Optional[int] = None
                ) -> List[GroupProfile]:
        """
        Returns all the groups in the system.

        Parameters
        ----------
        sort_by: sort by any group attribute.
        limit: max number of groups to return.

        Returns
        -------
        List of groups
        """
        pass

    @abstractmethod
    def get_one(self, group_id: int = None, group_name=None) -> Optional[GroupProfile]:
        """
        Retrieve group details using either its group id or name.

        Parameters
        ----------
        group_id (optional)
        group_name (optional)

        Returns
        -------
        Group
        """
        pass

    @abstractmethod
    def get_all_by_user(self, user_id: int) -> List[GroupProfile]:
        """
        Returns all the groups in the system for a given user.

        Parameters
        ----------
        user_id: id of the user requesting groups.

        Returns
        -------
        List of groups
        """
        pass

    @abstractmethod
    def update_group(self, update_group: GroupProfile) -> bool:
        """
        Update group details and permissions.

        Parameters
        ----------
        update_group: group with the updated details.

        Returns
        -------
        Pass
        """
        pass

    @abstractmethod
    def group_name_exists(self, group_name: str) -> bool:
        """
        Check if a group name already exists in the system

        Parameters
        ----------
        group_name

        Returns
        -------
        A boolean flag; when True, the group name exists.  False otherwise.
        """
        pass

    @abstractmethod
    def delete_group(self, group_name: str) -> str:
        """
        Delete group from the system

        Parameters
        ----------
        group_name
        """
        pass

    @abstractmethod
    def delete_all(self):
        """
        Delete ALL groups from the system
        """
        pass

    @abstractmethod
    def all_users_in_group(self, group_id: int) -> List[UserProfile]:
        """
        Returns all users belonging to the group. In the case of cloud groups, returns all users, those that already
        logged in in the system, and those that are not logged in. This allows the user to modify group permission
        even to user that are not logged in yet.

        The return list will have the following structure:
        {"uid": 1, "nickName": user, "picture": None, "read_write": 1}
            uid: could be None, representing those users that are not logged in yet
            read_write could be either 0 or 1

        Parameters
        ----------
        group_id
        """
        pass

    @abstractmethod
    def admin_group(self) -> GroupProfile:
        """
        Retrieve a group with all the superAdmin users.
        """
        pass


