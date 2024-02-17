from blacksheep.server.openapi.common import EndpointDocs, ParameterInfo

from ..model import GroupProfile

__tags = ["Groups"]

create_group = EndpointDocs(
    summary="Create Group",
    description="Create group. Expect name and description of the group.",
    tags=__tags,
    parameters={"group": ParameterInfo("Name and Description of the new group.")}
)

get_all = EndpointDocs(
    summary="All Groups",
    description="Returns all groups in the system. No user filter is applied.",
    tags=__tags
)

get_one_group = EndpointDocs(
    summary="Get Details",
    description="Returns details of the given group.",
    tags=__tags,
    parameters={"groupId": ParameterInfo("Group ID.", int)}
)

update_group = EndpointDocs(
    summary="Update Group",
    description=
    """
    Update the information for the specified group, including adding users and modifying user permissions within the 
    group. Changing the name and description is restricted to local groups, while cloud groups are limited to updating 
    user permissions. Furthermore, only users possessing administrative permissions for the group are authorized to 
    execute this action.
    """,
    tags=__tags,
    parameters={"data": ParameterInfo("Group new information.", GroupProfile)}
)

users_in_group = EndpointDocs(
    summary="Users In Group",
    description=
    """
    Retrieve all users belonging to the specified groupId. The function returns a list containing user information,
    including uid, nickName, picture (if available), read-write and admin permissions. Users without uid are those
    present in the system but have not logged in yet.
    Return example: {uid: 1, nickName: "admin", picture: null, read_write: 1, admin: 0}
    """,
    tags=__tags,
    parameters={"groupId": ParameterInfo("Group ID.", int)}
)

delete_group = EndpointDocs(
    summary="Delete Group",
    description=
    """
    Remove the designated group. This action is exclusive to users with administrative permissions for the group.
    Only local groups are eligible for deletion.
    """,
    tags=__tags,
    parameters={"groupId": ParameterInfo("Group ID.", int)}
)

group_name_doc = EndpointDocs(
    summary="Checks if a group name exists in the groups database",
    description="Returns a boolean flag indicating if a group name is already present in the system.",
    tags=__tags
)

delete_all = EndpointDocs(
    summary="Delete All Groups",
    description=
    """
    Delete all groups. Only local groups are eligible for deletion. This action is exclusive to users with
    super administrative permissions over the system.
    """,
    tags=__tags
)

get_users_not_in_group = EndpointDocs(
    summary="Users Not In Group",
    description="Obtain the list of users not associated with the provided group ID.",
    tags=__tags
)

admin = EndpointDocs(
    summary="Super Admin Users",
    description="""
    Retrieve a list with all the superAdmin users. This action is exclusive to users with super administrative 
    permissions over the system.
    """,
    tags=__tags,
)

__all__ = ['create_group', 'get_all', 'get_one_group', 'update_group', 'users_in_group',
           'delete_group', 'group_name_doc', 'delete_all', 'admin']
