import json
import os
from decimal import Decimal
from collections import Counter

from blacksheep import FromJSON, Request, WebSocket
from blacksheep.server.controllers import ApiController, delete, file, get, post, ws
from requests import Session
from typing import List, Optional, Union

from .dataapps_ws import DataAppChangeListeners
from . import dataappshttpdocs, IDataAppsService

from ..docs import docs
from ..groups import InvalidGroupName
from ..model import DataAppAttributes, DataAppFunction, DataAppProfile
from ..telemetry import ITelemetryService
from ..users import check_user_identity, IUsersService, UserDoesNotBelong, WritePermission


def _tel_extract_types(data: Union[dict, List]):
    """
    Extract widget types. This function is recursive when a Layout is found, and we need to go 'deeper'.
    """
    types = []

    if isinstance(data, dict):
        if "type" in data:
            types.append(data["type"])

        for key, value in data.items():
            types.extend(_tel_extract_types(value))

    elif isinstance(data, list):
        for item in data:
            types.extend(_tel_extract_types(item))

    return types


def _tel_count_widgets(spec: str) -> Union[dict, List]:
    """
    For telemetry purposes, determine the usage of widgets in a dataApp. This function will count the number of widgets
    per type.
    Return example: {'Button': 1, 'LineChart': 3, 'Sequence': 3, 'Table': 1}
    """
    try:
        widgets = json.loads(spec)["mainPanel"]["properties"]["widgets"]
        widget_types = _tel_extract_types(widgets)
        return dict(Counter(widget_types))
    except Exception:
        return []


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


class DataAppsHttpServer(ApiController):
    def __init__(self, svr: IDataAppsService, telemetry: ITelemetryService, users: IUsersService) -> None:
        self._svr = svr
        self._telemetry = telemetry
        self._users = users
        super().__init__()
        self.dataapp_change_listeners = DataAppChangeListeners()

    @classmethod
    def route(cls) -> Optional[str]:
        return '/api/dataapps'

    @ws("/ws")
    async def ws(self, websocket: WebSocket):
        await websocket.accept()
        try:
            msg = await websocket.receive_text()
            self.dataapp_change_listeners.add(msg, websocket)
            while True:
                msg = await websocket.receive_text()
        except Exception as e:
            print(e)
        finally:
            self.dataapp_change_listeners.remove(websocket)

    @get("/")
    @docs(dataappshttpdocs.dataapp_list)
    async def dataapp_list(self, request: Request) -> List[DataAppProfile]:
        """
        Retrieve all the dataApp in the system for the requesting user.
        """
        try:
            user_id = check_user_identity(request)
            self._svr.get_all(user_id)
            return self.ok()
        except Exception as e:
            return self.status_code(500, str(e))

    @get("/user")
    @docs(dataappshttpdocs.local_dataapp_list)
    async def user_local_dataapp_list(self, request: Request) -> List[DataAppAttributes]:
        """
        Retrieve 'local' dataApps that are exclusively owned by the user. Local dataApps refer to those privately
        held by the user and have not been shared with any groups.
        """
        try:
            user_id = check_user_identity(request)
            self._svr.get_all(user_id)
            return self._svr.user_local_dataapp_list(user_id)
        except Exception as e:
            return self.status_code(500, str(e))

    @get("/groups")
    @docs(dataappshttpdocs.group_dataapp_list)
    async def user_group_dataapp_list(self, request: Request) -> List[DataAppAttributes]:
        """
        Retrieve all dataApps to which the user has access through membership in any group.
        """
        try:
            user_id = check_user_identity(request)
            return self._svr.user_group_dataapp_list(str(user_id))
        except Exception as e:
            return self.status_code(500, str(e))

    @post("/")
    @docs(dataappshttpdocs.create_dataapp)
    async def create(self, request: Request, attributes: FromJSON[DataAppAttributes], data) -> DataAppProfile:
        """
        Endpoint to create a dataApp. If a dataApp version is specified, the function will overwrite any existing
        dataApp in the system. If no version is provided and a dataApp already exists, this function will increment
        the minor version.

        param request: info from the request. It is used to check the identity of the user trying to register the dataApp.
                       First, the user must be logged in in order to register a dataApp. Once the user is logged in,
                       the user permission are checked to make sure the user can register or update the desired dataApp.
        param attributes: contains the main information from the dataApp.
        param data: contains additional information of the files (uid) that the dataApp uses,
                    so we can keep track of the files used by the dataApp and update/delete when needed.
        """
        try:
            user_id = check_user_identity(request)
            dataapp_attributes = DataAppAttributes(name=attributes.value.name,
                                                   major=attributes.value.major,
                                                   minor=attributes.value.minor,
                                                   description=attributes.value.description,
                                                   specId=attributes.value.specId,
                                                   tags=attributes.value.tags,
                                                   groups=attributes.value.groups,
                                                   userId=user_id)
            dataapp_functions = []
            for fn in attributes.value.functions:
                dataapp_functions.append(DataAppFunction(uid=fn["uid"], ser_body=fn["ser_body"]))

            dataapp = self._svr.create(dataapp_attributes, data, dataapp_functions)
            tel_info = {
                "dataapp_id": dataapp.uid,
                "dataapp_version": f"{dataapp.major}.{dataapp.minor}",
                "dataapp_creation_date": dataapp.creationDate,
                "dataapp_update_date": dataapp.updateDate,
                "user_id": user_id,
                "dataapp_groups": dataapp.groups,
                "amount_custom_fn": len(dataapp_functions),
                "widgets": _tel_count_widgets(attributes.value.specId)
            }
            self._telemetry.send_telemetry(event="DataAppCreated", info=tel_info)
            await self.dataapp_change_listeners.notify(dataapp.name, dataapp.uid, user_id, False)
            return dataapp
        except UserDoesNotBelong as e:
            return self.bad_request(str(e))
        except InvalidGroupName as e:
            return self.bad_request(str(e))
        except WritePermission as e:
            return self.bad_request(str(e))
        except Exception as e:
            return self.status_code(500, str(e))

    @get("/name/{dataAppName}")
    @docs(dataappshttpdocs.dataapp_by_name)
    async def get_dataapp_by_name(self, request: Request, dataAppName: str) -> DataAppAttributes:
        """
        UI Home section access dataApp through here
        """
        user_id = check_user_identity(request)
        dataapp = self._svr.get_dataapp(dataapp_name=dataAppName)
        # check if user can visualize the dataapp
        user_groups = self._users.get_user_details(user_id).groupIds
        if user_id != dataapp.userId and not bool(set(dataapp.groups).intersection((user_groups))):
            return self.unauthorized("User has not permission to visualize dataapp")
        tel_info = {
            "dataapp_id": dataapp.uid,
            "from": "Home",
            "user_id": user_id
        }
        self._telemetry.send_telemetry(event="DataAppVisualization", info=tel_info)
        return dataapp

    @get("/{id}")
    @docs(dataappshttpdocs.dataapp_by_id)
    async def get_dataapp_by_id(self, id: str) -> DataAppAttributes:
        return self._svr.get_dataapp(dataapp_id=id)

    @delete("/")
    @docs(dataappshttpdocs.delete_all_dataapps)
    async def delete_all(self, request: Request) -> bool:
        try:
            user_id = check_user_identity(request)
            user_details = self._users.get_user_details(user_id)
            if hasattr(user_details, "superAdmin") and user_details.superAdmin == 1:
                response = self._svr.delete_all()
                self._telemetry.send_telemetry(event="DataAppDeleteAll", info={"user_id": user_details.nickName})
                return response
            return self.unauthorized(f"User {user_details.nickName} has no permission to delete all dataApps.")
        except Exception as e:
            return self.status_code(500, str(e))

    @delete("/{id}")
    @docs(dataappshttpdocs.delete_dataapp)
    async def delete(self, uid: int, request: Request) -> bool:
        try:
            user_id = check_user_identity(request)
            dataapp = self._svr.get_dataapp(dataapp_id=uid)
            if self._svr.delete_dataapp(uid, user_id):
                await self.dataapp_change_listeners.notify(dataapp.name, dataapp.uid, user_id, True, dataapp.major,
                                                           dataapp.minor)
                tel_info = {
                    "dataapp_id": dataapp.uid,
                    'user_id': user_id,
                }
                self._telemetry.send_telemetry(event="DataAppDelete", info=tel_info)
                return self.ok("DataApp removed successfully.")
            return self.bad_request()
        except Exception as e:
            return self.status_code(500, str(e))

    @get("/{id}/versions")
    @docs(dataappshttpdocs.dataapp_versions)
    async def get_dataapp_versions(self, dataAppName: str) -> List[float]:
        """
        Giving a dataapp name, retrieve all the available versions in the system. The result is a list of versions.
        """
        return json.dumps(self._svr.get_dataapp_versions(dataAppName), cls=DecimalEncoder)

    @get("spec/{specId}")
    @docs(dataappshttpdocs.dataapp_spec)
    async def get_dataapp_spec(self, specId: str) -> file:
        """
        Retrieve the file containing the dataApp Spec. The UI request this file to 'paint' the dataApp.
        """
        shapelets_dir = os.path.expanduser('~/.shapelets')
        data_apps_store = os.path.join(shapelets_dir, 'dataAppsStore')
        spec_path = os.path.join(data_apps_store, f"{specId}.json")
        return file(spec_path, "multipart/form-data")

    @get("/{id}/{major}/{minor}")
    @docs(dataappshttpdocs.dataapp_by_version)
    async def get_dataapp_by_version(self, request: Request, dataAppName: str,
                                     major: int, minor: int) -> DataAppProfile:
        """
        Giving the name, major and minor version of a dataApp, return all its details.
        """
        user_id = check_user_identity(request)
        dataapp = self._svr.get_dataapp(dataapp_name=dataAppName, major=major, minor=minor)
        # check if user can visualize the dataapp
        user_groups = self._users.get_user_details(user_id).groupIds
        if user_id != dataapp.userId and not bool(set(dataapp.groups).intersection((user_groups))):
            return self.unauthorized("User has not permission to visualize dataapp")
        tel_info = {
            "dataapp_id": dataapp.uid,
            "from": "dataAppSection",
            "user_id": user_id
        }
        self._telemetry.send_telemetry(event="DataAppVisualization", info=tel_info)
        return dataapp

    @get("/{id}/lastVersion")
    @docs(dataappshttpdocs.dataapp_last_version)
    async def get_dataapp_last_version(self, dataAppName: str) -> float:
        """
        Giving a dataapp name, retrieve the LAST version in the system as a float.
        """
        return self._svr.get_dataapp_last_version(dataAppName)

    @get("/{id}/tags")
    @docs(dataappshttpdocs.dataapp_tags)
    async def get_dataapp_tags(self, dataAppName: str) -> List[str]:
        """
        Not Used yet. Will return dataApp tags.
        """
        return self._svr.get_dataapp_tags(dataAppName)


class DataAppsHttpProxy(IDataAppsService):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self) -> List[DataAppProfile]:
        return self.session.get('/api/dataapps/')

    def user_local_dataapp_list(self) -> List[DataAppProfile]:
        return self.session.get('/api/dataapps/user')

    def user_group_dataapp_list(self) -> List[DataAppProfile]:
        return self.session.get('/api/dataapps/groups')

    def create(self, dataapp, host:str = None) -> DataAppProfile:
        params = []
        if dataapp.functions is not None:
            dataapp_functions = []
            for key, item in dataapp.functions.items():
                dataapp_functions.append(DataAppFunction(uid=key, ser_body=item["ser_body"]))

        payload = DataAppAttributes(name=dataapp.name,
                                    major=dataapp.version[0] if dataapp.version else None,
                                    minor=dataapp.version[1] if dataapp.version else None,
                                    description=dataapp.description,
                                    specId=dataapp.to_json(host),
                                    tags=dataapp.tags,
                                    groups=dataapp.groups,
                                    functions=dataapp_functions)

        if dataapp._data:
            params.append(("data", dataapp._data))
        response = self.session.post('/api/dataapps/', json=json.loads(payload.json()), params=params)
        if response.status_code != 200:
            raise RuntimeError(response.content)
        return response

    def get_dataapp(self):
        pass

    def delete_dataapp(self, uid: int):
        self.session.delete('/api/dataapps/{id}', params=[("uid", uid)])

    def delete_all(self) -> bool:
        self.session.delete('/api/dataapps/')
        return True

    def get_dataapp_versions(self, dataAppName: str) -> List[float]:
        return self.session.get('/api/{id}/versions', params=[("dataAppName", dataAppName)])

    def get_dataapp_last_version(self, dataAppName: str) -> float:
        return self.session.get('/api/{id}/lastVersion', params=[("dataAppName", dataAppName)])

    def get_dataapp_tags(self, dataAppName: str) -> List[str]:
        return self.session.get('/api/{id}/tags', params=[("dataAppName", dataAppName)])
