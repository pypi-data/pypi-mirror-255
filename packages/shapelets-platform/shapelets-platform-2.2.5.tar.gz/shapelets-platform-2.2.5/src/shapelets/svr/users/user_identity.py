from blacksheep.server.controllers import Request, unauthorized

from ..model import SignedPrincipalId, GroupProfile


def check_user_identity(request: Request) -> int:
    """
    When initiating a request within the system, verify the user identity  and, when possible,
    provide the corresponding user ID in response.
    """
    if request.identity:
        return request.identity.claims["userId"]
    elif request.get_first_header(b"authorization"):
        header_value = request.get_first_header(b"authorization")
        token = header_value.decode('ascii').split("Bearer ", 1)[1]
        principal = SignedPrincipalId.from_token(token)
        if principal is None:
            raise RuntimeError(f"Invalid bearer token: {header_value}")
        return principal.userId
    else:
        message = "Unable to find user for dataApp registration. Please, login."
        print(message)
        return unauthorized(message)

def super_admin(user_details: GroupProfile) -> bool:
    return hasattr(user_details, "superAdmin") and user_details.superAdmin == 1
