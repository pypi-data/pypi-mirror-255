import json
import ssl
import webbrowser
import websocket

from typing import Any, Optional, List, Tuple, Union
from typing_extensions import Annotated, Literal

from pydantic import AnyUrl, BaseModel, EmailStr, Field, parse_obj_as

from .iauthservice import Addresses
from ..utils import FlexBytes
from ..model import GCPrincipalId, UserAttributes

AuthenticationOutcome = Literal['Success', 'Error']


class RemoteGroup(BaseModel):
    """
    Details of a remote group coming from Azure, Google or any other provider
    """
    groupId: str
    groupName: str
    groupDescription: Optional[str] = None
    usersInGroup: Optional[List[str]] = None


class AuthenticationSuccess(BaseModel):
    """
    Details of a user after running a successful auth flow
    """

    outcome: Literal['Success'] = 'Success'
    """
    Identifies the message
    """

    id: str
    """
    Unique identifier of a user
    """

    signature: FlexBytes
    """
    Crypto signature
    """

    provider: str
    """
    Provider internal code (unique)
    """

    nickName: Optional[str] = None
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    familyName: Optional[str] = None
    locale: Optional[str] = None
    picture: Optional[bytes] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    url: Optional[AnyUrl] = None
    remoteGroups: Optional[List[RemoteGroup]] = None

    class Config:
        json_encoders = {
            FlexBytes: lambda v: str(v)
        }


class AuthenticationError(BaseModel):
    """
    Error details after running a failed auth flow
    """
    outcome: Literal['Error'] = 'Error'
    """
    Identifies the message
    """

    provider: str
    """
    Should indicate the Authn protocol (ej: azure).
    """

    provider_text: Optional[str] = None
    """
    friendly description of the authn provider (ej: Azure AD)
    """

    error_code: Optional[int] = None
    """
    An HTML error code associated with the exception.
    """

    error_type: Optional[str] = None
    """
    An optional, textual error code associated with the exception.
    """

    description: Optional[str] = None
    """
    A textual description of the issue 
    """

    more_info: Optional[AnyUrl] = None
    """
    An optional html url where the user may find more information about the error 
    """


class AuthenticationException(Exception):
    def __init__(self,
                 provider: str,
                 provider_text: Optional[str],
                 error_code: Optional[int],
                 error_type: Optional[str],
                 description: Optional[str],
                 more_info: Optional[AnyUrl],
                 *args: object) -> None:
        self.provider = provider
        self.provider_text = provider_text
        self.error_code = error_code
        self.error_type = error_type
        self.description = description
        self.more_info = more_info
        super().__init__(*args)


AuthenticationResponse = Annotated[Union[AuthenticationSuccess, AuthenticationError], Field(discriminator="outcome")]
"""
Discriminated Union of Authentication Responses
"""


def gc_parse(data: Any) -> Tuple[GCPrincipalId, UserAttributes]:
    """
    Parses a response from GC web socket.
    
    Parameters
    ----------
    data: object, required
        JSON contents of the response from GC
    
    Returns
    -------
    A tuple, where the first element is an instance of GCPrincipalId (which can 
    be used to complete the logging process) and, the second element, are 
    the user attributes as provided by the authentication system.
    
    Exceptions
    ----------
    AuthenticationException, if the authn process was not successful.
    
    """

    outcome = parse_obj_as(AuthenticationResponse, data)

    if isinstance(outcome, AuthenticationError):
        raise AuthenticationException(outcome.provider,
                                      outcome.provider_text,
                                      outcome.error_code,
                                      outcome.error_type,
                                      outcome.description,
                                      outcome.more_info)

    principal = GCPrincipalId(scope=outcome.provider, id=outcome.id, signature=outcome.signature)
    user_details = UserAttributes(**outcome.dict(), providerId=outcome.id)
    return principal, user_details


def gc_flow(addresses: Addresses, browser: bool = None, relax_ssl: bool = True) -> Tuple[GCPrincipalId, UserAttributes]:
    """
    Runs a full authentication flow through GC
    
    Parameters
    ----------
    addresses: Addresses, required
        The addresses for the web socket and the browser redirection

    browser: bool, defaults to None
        Flag to check if the funtion should open the browser. When log in from api, browser must be opened.
        
    relax_ssl: boolean, defaults to True
        Avoids issues with local development and SSL connections.
    
    Returns
    -------
    A tuple, where the first element is an instance of GCPrincipalId (which can 
    be used to complete the logging process) and, the second element, are 
    the user attributes as provided by the authentication system.
    
    Exceptions
    ----------
    AuthenticationException, if the authn process was not successful.
        
    """
    # relaxed ssl options for the client
    options = {}
    if relax_ssl:
        options['sslopt'] = {
            "cert_reqs": ssl.CERT_NONE,
            "check_hostname": False
        }

    # websockets doesn't do 'with'
    ws = websocket.create_connection(addresses.ws, **options)
    try:
        # run web browser to kick off the interaction through a browser
        # Note: this does not work in remote servers. From now on, shapelets-js will open the web browser, unless the
        # login is made from the python api.
        if browser:
            webbrowser.open(addresses.redirect)
        # just wait for the process to finish
        return gc_parse(json.loads(ws.recv()))
    finally:
        ws.close()
