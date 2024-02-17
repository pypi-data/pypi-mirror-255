from abc import ABC, abstractmethod
from typing import List, Optional

from ..model import DataAppAttributes, DataAppFunction, DataAppProfile


class IDataAppsService(ABC):

    @abstractmethod
    def get_all(self, user_id: int) -> List[DataAppProfile]:
        """
        Retrieve all the dataApp in the system for a given user.
        """
        pass

    @abstractmethod
    def user_local_dataapp_list(self, user_id: int) -> List[DataAppProfile]:
        """
        Retrieve 'local' dataApps that are exclusively owned by the user. Local dataApps refer to those privately
        held by the user and have not been shared with any groups.
        """
        pass

    @abstractmethod
    def user_group_dataapp_list(self, user_id: int) -> List[DataAppProfile]:
        """
        Retrieve all dataApps to which the user has access through membership in any group.
        """
        pass

    @abstractmethod
    def create(self, attributes: DataAppAttributes, data: List[str] = None,
               dataapp_functions: List[DataAppFunction] = None) -> DataAppProfile:
        """
        Create a new dataApp. If a dataApp version is specified, the function will overwrite any existing dataApp in
        the system. If no version is provided and a dataApp already exists, this function will increment the minor
        version.
        """
        pass

    @abstractmethod
    def get_dataapp(self,
                    dataapp_id: int = None,
                    dataapp_name: str = None,
                    major: int = None,
                    minor: int = None,
                    user_id: int = None) -> Optional[DataAppProfile]:
        """
        Retrieve dataApp by employing various combinations of its attributes.
        """
        pass

    @abstractmethod
    def delete_dataapp(self, dataapp_id: int, user_id: int) -> bool:
        """
        Delete dataApp. User permission will be checked before deleting the dataApp.
        """
        pass

    @abstractmethod
    def delete_all(self) -> bool:
        """
        Delete ALL dataapps in the system.
        """
        pass

    @abstractmethod
    def get_dataapp_versions(self, dataapp_name: str) -> List[float]:
        """
        Giving a dataapp name, retrieve all the available versions in the system. The result is a list of versions.
        """
        pass

    @abstractmethod
    def get_dataapp_last_version(self, dataapp_name: str) -> float:
        """
        Giving a dataapp name, retrieve the LAST version in the system as a float.
        """
        pass

    @abstractmethod
    def get_dataapp_tags(self, dataapp_name: str) -> List[str]:
        pass
