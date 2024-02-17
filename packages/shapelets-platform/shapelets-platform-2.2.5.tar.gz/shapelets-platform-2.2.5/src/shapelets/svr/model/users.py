from pydantic import AnyUrl, BaseModel, EmailStr
from typing import List, Optional, Set, Union
from typing_extensions import Literal

UserField = Literal[
    'uid', 'nickName', 'email', 'firstName', 'familyName', 'locale', 'picture', 'bio', 'location', 'url']
UserAllFields: Set[UserField] = set(
    ['uid', 'nickName', 'email', 'firstName', 'familyName', 'locale', 'picture', 'bio', 'location', 'url'])
UserId = Union[int, str]


class RemoteGroup(BaseModel):
    """
    Details of a remote group coming from Azure, Google or any other provider
    """
    groupId: str
    groupName: str
    groupDescription: Optional[str] = None
    usersInGroup: Optional[List[str]] = None


class UserAttributes(BaseModel):
    nickName: Optional[str] = None
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    familyName: Optional[str] = None
    locale: Optional[str] = None
    picture: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    url: Optional[AnyUrl] = None
    groupIds: Optional[List[int]] = None
    provider: Optional[str] = "local"
    providerId: Optional[str] = None
    remoteGroups: Optional[List[RemoteGroup]] = None


class UserProfile(UserAttributes):
    uid: int

class SuperUserProfile(UserProfile):
    superAdmin: int
