from pydantic import BaseModel
from typing import Optional, List, Set, Union
from typing_extensions import Literal

GroupField = Literal['uid', 'name', 'description', 'provider']
GroupAllFields: Set[GroupField] = set(['uid', 'name', 'description', 'provider'])
GroupId = Union[int, str]


class UserInGroup(BaseModel):
    uid: Optional[int] = None
    nickName: str
    picture: Optional[str] = None
    read_write: Optional[int] = None
    admin: Optional[int] = None


class GroupAttributes(BaseModel):
    """
    Group Info
        name: group name.
        description: group description.
        provider: is the group coming from an enterprise login like azure or google?
        providerGroupId: if applied, save the original group ID from the provider.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = "local"
    providerGroupId: Optional[str] = None
    usersInGroup: Optional[List]
    usersNotInGroup: Optional[List]


class GroupProfile(GroupAttributes):
    uid: int
