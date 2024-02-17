from abc import ABC, abstractmethod


class ILicenseService(ABC):
    @abstractmethod
    def license_status(self) -> str:
        """
        Returns license status: Active or Revoked
        """
        pass

    @abstractmethod
    def current_version(self) -> int:
        """
        Returns the current license version of the server.
        """
        pass

    @abstractmethod
    def license_type(self) -> str:
        """
        Returns the type of the license (Free/Commercial).
        """
        pass

    @abstractmethod
    def last_license_version(self) -> bool:
        """
        Verify with Grand Central that the current server license version aligns with the latest version available.
        If not, initiate a request for the most recent version.
        """
        pass

    @abstractmethod
    def request_evaluation_license(self):
        """
        Request an evaluation license for Platform.
        """
        pass

    @abstractmethod
    def request_license(self, license_id: str = None):
        """
        Giving a license ID, request the latest license file available on Grand Central.
        """
        pass

    @abstractmethod
    def revoke_license(self):
        """
        Checks if license is revoked on the server.
        """
        pass
