from typing import List, Optional, Set, Tuple

from .idataappsrepo import IDataAppsRepo
from .idataappsservice import IDataAppsService
from ..model import (
    DataAppAllFields,
    DataAppAttributes,
    DataAppField,
    DataAppFunction,
    DataAppProfile
)


class DataAppsService(IDataAppsService):
    __slots__ = ('_dataapps_repo',)

    def __init__(self, dataapp_repo: IDataAppsRepo) -> None:
        self._dataapp_repo = dataapp_repo

    def get_all(self,
                user_id: int,
                attributes: Optional[Set[DataAppField]] = DataAppAllFields,
                sort_by: Optional[List[Tuple[DataAppField, bool]]] = None,
                skip: Optional[int] = None,
                limit: Optional[int] = None) -> List[DataAppProfile]:
        return self._dataapp_repo.load_all(user_id, attributes, sort_by, skip, limit)

    def user_local_dataapp_list(self, user_id: int) -> List[DataAppProfile]:
        return self._dataapp_repo.user_local_dataapp_list(user_id)

    def user_group_dataapp_list(self, user_id: int) -> List[DataAppProfile]:
        return self._dataapp_repo.user_group_dataapp_list(user_id)

    def create(self, attributes: DataAppAttributes, data: List[str] = None,
               dataapp_functions: List[DataAppFunction] = None) -> DataAppProfile:
        return self._dataapp_repo.create(attributes, data, dataapp_functions)

    def get_dataapp(self,
                    dataapp_id: int = None,
                    dataapp_name: str = None,
                    major: int = None,
                    minor: int = None,
                    user_id: int = None) -> Optional[DataAppProfile]:
        return self._dataapp_repo.get_dataapp(dataapp_id=dataapp_id, dataapp_name=dataapp_name, major=major,
                                              minor=minor, user_id=user_id)

    def delete_dataapp(self, dataapp_id: int, user_id: int) -> bool:
        return self._dataapp_repo.delete_dataapp(dataapp_id, user_id)

    def delete_all(self) -> bool:
        self._dataapp_repo.delete_all()

    def get_dataapp_versions(self, dataapp_name: str) -> List[float]:
        return self._dataapp_repo.get_dataapp_versions(dataapp_name)

    def get_dataapp_last_version(self, dataapp_name: str) -> float:
        self._dataapp_repo.get_dataapp_last_version(dataapp_name)

    def get_dataapp_tags(self, dataapp_name: str) -> List[str]:
        self._dataapp_repo.get_dataapp_tags(dataapp_name)
