from blacksheep.server.openapi.common import EndpointDocs, ParameterInfo

from ..model import UserProfile

__tags = ["Users"]

user_list = EndpointDocs(
    summary="List of Users",
    description=
    """
    Retrieve a list of all the users in the system. This action is exclusive to users with
    super administrative permissions over the system.
    """,
    tags=__tags
)

delete_all_users = EndpointDocs(
    summary="Delete All of Users",
    description=
    """
    Delete all the users in the system. This action is exclusive to users with
    super administrative permissions over the system.
    """,
    tags=__tags
)

nickname_doc = EndpointDocs(
    summary="Checks if a user name exists in the user database",
    description="Returns a boolean flag indicating if a user name is already present in the system.",
    tags=__tags
)

me_doc = EndpointDocs(
    summary="Current User Profile",
    description="Returns details of the current logged user",
    tags=__tags
)

get_user_details = EndpointDocs(
    summary="Get User Profile",
    description="Returns details of the requested user",
    tags=__tags,
    parameters={"id": ParameterInfo("User ID.", int)}
)

update_user_details = EndpointDocs(
    summary="Update User Profile",
    description="Update user details",
    tags=__tags,
    parameters={"id": ParameterInfo("User ID.", int),
                "details": ParameterInfo("User details to update.", UserProfile)}
)

delete_user = EndpointDocs(
    summary="Delete User",
    description=
    """
    Delete user in the system. The user initiating the removal must possess administrator rights over the system.
    """,
    tags=__tags,
    parameters={"id": ParameterInfo("User ID.", int)}
)

add_to_group = EndpointDocs(
    summary="Add User to Group/s",
    description="Add user to group/s.",
    tags=__tags,
    parameters={
        "userName": ParameterInfo("Username.", str),
        "groups": ParameterInfo("Group/s where the user will be added.", list),
        "write": ParameterInfo("Grant the user write permissions for the specified group.", bool),
        "admin": ParameterInfo("Grant the user administrator permissions for the specified group.", bool)
    }
)

remove_from_group = EndpointDocs(
    summary="Remove User from Group",
    description=
    """
    Remove the specified user from the group. The user initiating the removal must possess administrator rights over 
    the group.
    """,
    tags=__tags,
    parameters={
        "userName": ParameterInfo("Username.", str),
        "groups": ParameterInfo("Group/s where the user will be added.", list)
    }
)

__all__ = ['user_list', 'delete_all_users', 'nickname_doc', 'me_doc', 'get_user_details', 'update_user_details',
           'delete_user', 'add_to_group', 'remove_from_group']
