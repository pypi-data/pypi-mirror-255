from blacksheep.server.openapi.common import EndpointDocs, ParameterInfo
from typing import Optional

from ..model import UserAttributes


# Create equivalent types here to avoid circular imports
class VerifyChallengeType:
    userName: str
    nonce: bytes
    token: bytes
    rememberMe: bool


class RegistrationType:
    userName: str
    salt: bytes
    pk: bytes
    user_details: Optional[UserAttributes] = None


class GetTokenRequestType:
    gc: bytes
    user_details: Optional[UserAttributes]


__tags = ["Auth"]

check_user_exists = EndpointDocs(
    summary="Check User Name",
    description="Verify if a given name is already associated with an existing user.",
    tags=__tags,
    parameters={"username": ParameterInfo("Name to check.", str)}
)

remove_user = EndpointDocs(
    summary="Remove User",
    description=
    """
    Delete user in the system. The user initiating the removal must possess administrator rights over the system.
    Moreover, the transfer flag can be utilized to designate a new user who will assume ownership of all dataApps
    shared with any group. This field is mandatory if the user to be deleted owns data applications within any group.
    Note: All dataApps not shared with any group will be deleted, as they solely belong to the user's local space.
    """,
    tags=__tags,
    parameters={
        "userName": ParameterInfo("Name to check.", str),
        "transfer": ParameterInfo("Transfer the dataApps of the removed user to another user.", str)
    }
)

generate_challenge = EndpointDocs(
    summary="Generate Challenge",
    description=
    """
    Returns a message with the original salt used during the registration
    process and a nonce, which the user need to sign with his private
    signature key derived from the salt and his password.
    """,
    tags=__tags,
    parameters={"username": ParameterInfo("Name of the user.", str)}
)

verify_challenge = EndpointDocs(
    summary="Verify Challenge",
    description=
    """
    Completes the authentication process by checking the signature over a nonce is verifiable using the stored public
    signature associated with a user during the registration process.
    """,
    tags=__tags,
    parameters={"details": ParameterInfo("User verify challenge.", VerifyChallengeType)}
)

new_registration = EndpointDocs(
    summary="Register New User",
    description=
    """
    Registers credentials for a new user based on user name and password.
    """,
    tags=__tags,
    parameters={"details": ParameterInfo("Registration details.", RegistrationType)}
)

is_protocol_available = EndpointDocs(
    summary="Is Protocol Available?",
    description="Checks if a particular external authentication protocol is available.",
    tags=__tags,
    parameters={"protocol": ParameterInfo("Name of the protocol to check.", str)}
)

available_providers = EndpointDocs(
    summary="Available Providers",
    description="Returns a list of valid authentication providers, including unp.",
    tags=__tags
)

addresses = EndpointDocs(
    summary="Addresses",
    description=
    """
    Returns a pair of addresses, one for a web socket where authentication results are sent, and another, for the web
    browser redirection to initiate the authentication process.
    """,
    tags=__tags,
    parameters={
        "protocol": ParameterInfo("The desired protocol.  'unp' is not a valid parameter.", str),
        "req": ParameterInfo(
            """
            The unique id for the interaction.  If none, a random uuid will be used to correlate web socket with user browser activity.
            """, str
        )
    }
)

verify_token = EndpointDocs(
    summary="Verify Token",
    description="Verifies an authentication token signed by this server",
    tags=__tags,
    parameters={
        "principal": ParameterInfo("Either a string token or a SignedPrincipalId instance Credentials to verify.", str)}
)

get_token = EndpointDocs(
    summary="Get Token",
    description="Returns an authentication token after verifying an identity obtained  through an external authn provider",
    tags=__tags,
    parameters={
        "details": ParameterInfo("Token Request with Grand Central address and user details.",
                                 GetTokenRequestType)
    }
)

redirect_provider = EndpointDocs(
    summary="Redirect Provider",
    description=
    """
    Enable seamless external login experiences by accepting login providers like Azure, Google, and more. Upon 
    receiving a provider, the system dynamically generates the connection addresses associated with that provider. 
    The responsibility of initiating the redirect browser lies with Shapelets-js, ensuring a smooth process for 
    Grand Central to retrieve the required information.
    """,
    tags=__tags
)

external_login = EndpointDocs(
    summary="External Login",
    description=
    """
    Facilitate external login by receiving a login address from Grand Central.
    Establish a connection with Grand Central to retrieve the necessary information from the chosen provider. 
    Additionally, load groups from the provider to enhance the user's experience.
    """,
    tags=__tags
)

__all__ = ['check_user_exists', 'remove_user', 'generate_challenge', 'verify_challenge', 'new_registration',
           'is_protocol_available', 'available_providers', 'addresses', 'verify_token', 'get_token',
           'redirect_provider', 'external_login']
