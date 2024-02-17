from blacksheep.server.openapi.common import EndpointDocs, ParameterInfo

from ..model import DataAppAttributes

__tags = ["DataApps"]

dataapp_list = EndpointDocs(
    summary="DataApp List",
    description="""Retrieve all the dataApp in the system for the requesting user""",
    tags=__tags
)

local_dataapp_list = EndpointDocs(
    summary="Local DataApps",
    description=
    """
    Retrieve 'local' dataApps that are exclusively owned by the user. Local dataApps refer to those privately
    held by the user and have not been shared with any groups.
    """,
    tags=__tags
)

group_dataapp_list = EndpointDocs(
    summary="Group DataApps",
    description=
    """
    Retrieve all dataApps to which the user has access through membership in any group.
    """,
    tags=__tags
)

create_dataapp = EndpointDocs(
    summary="Create/Update DataApp",
    description=
    """
    Endpoint to create a dataApp. If a dataApp version is specified, the function will overwrite any existing
    dataApp in the system. If no version is provided and a dataApp already exists, this function will increment
    the minor version. The request is used to check the identity of the user trying to register the dataApp.
    """,
    tags=__tags,
    parameters={
        "attributes": ParameterInfo("contains the main information from the dataApp", DataAppAttributes),
        "data": ParameterInfo(
            """
            contains additional information of the files (uid) that the dataApp uses,
            so we can keep track of the files used by the dataApp and update/delete when needed.
            """
        )
    }
)

dataapp_by_name = EndpointDocs(
    summary="DataApp By Name",
    description=
    """
    Fetch details of a dataApp using its name. UI Home section access dataApps through here.
    """,
    tags=__tags
)

dataapp_by_id = EndpointDocs(
    summary="DataApp By ID",
    description=
    """
    Fetch details of a dataApp using its ID.
    """,
    tags=__tags
)

delete_all_dataapps = EndpointDocs(
    summary="Delete ALL DataApps",
    description=
    """
    Delete all dataApps from the system. This action is exclusive to users with super administrative permissions over 
    the system.
    """,
    tags=__tags
)

delete_dataapp = EndpointDocs(
    summary="Delete DataApp",
    description=
    """
    Delete a dataApp using its ID. Users must have write permissions over the dataApp, either by being 
    the owner of the dataApp or by belonging to the dataApp group.
    """,
    tags=__tags
)

dataapp_versions = EndpointDocs(
    summary="DataApp Versions",
    description=
    """
    Giving a dataapp name, retrieve all the available versions in the system. The result is a list of  (float).
    """,
    tags=__tags,
    parameters={"dataAppName": ParameterInfo("DataApp Name", str)}
)

dataapp_spec = EndpointDocs(
    summary="Get DataApp Spec",
    description=
    """
    Retrieve the file containing the dataApp specification. The UI requests this file to visually represent
    the dataApp.
    """,
    tags=__tags,
    parameters={"specId": ParameterInfo("UID of the spec", str)}
)

dataapp_by_version = EndpointDocs(
    summary="Get DataApp By Version",
    description=
    """
    Given the name, major, and minor version of a data application, retrieve all its details.
    """,
    tags=__tags,
    parameters={
        "dataAppName": ParameterInfo("DataApp Name", str),
        "major": ParameterInfo("Major version", int),
        "minor": ParameterInfo("Minor version", int)
    }
)

dataapp_last_version = EndpointDocs(
    summary="Get DataApp Last Version",
    description=
    """
    Giving a dataapp name, retrieve the latest version in the system as a floating-point number.
    """,
    tags=__tags,
    parameters={"dataAppName": ParameterInfo("DataApp Name", str)}
)

dataapp_tags = EndpointDocs(
    summary="Get DataApp Tags",
    description=
    """
    Get dataApp Tags.
    """,
    tags=__tags,
    parameters={"dataAppName": ParameterInfo("DataApp Name", str)}
)

__all__ = ['dataapp_list', 'local_dataapp_list', 'group_dataapp_list', 'create_dataapp', 'dataapp_by_id',
           'delete_all_dataapps', 'dataapp_by_name', 'delete_dataapp', 'dataapp_versions', 'dataapp_spec',
           'dataapp_by_version', 'dataapp_last_version', 'dataapp_tags']
