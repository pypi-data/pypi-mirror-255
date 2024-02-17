import os
import tomlkit

from typing import Optional

from .ilicenseservice import ILicenseService
from .license_utils import (
    verify_signed_message,
    _download_file_from_gc,
    _last_license_version,
    _last_nonce,
    _request_evaluation_license,
    _request_signed_message,
    _verify_license
)

from ..settings import Settings

home_dir = os.path.expanduser('~/.shapelets')
license_folder = os.path.join(home_dir, 'license')


def _update_license_id(license_id: str):
    """
    Update license id in settings.toml. Following the creation of an evaluation license, it is crucial to store the
    corresponding ID in the 'settings.toml' file. This ensures that upon subsequent server runs, there is no
    unnecessary request for another evaluation license.
    """
    settings_file = os.path.join(home_dir, 'settings.toml')
    # load the data
    with open(settings_file, "rt", encoding="utf-8") as handle:
        data = tomlkit.load(handle)

    data.get("server").update(license=license_id)

    with open(settings_file, "wt", encoding="utf-8") as handle:
        tomlkit.dump(data, handle)


class LicenseService(ILicenseService):
    """
    License Service.
        The license ID can be conveniently stored either in the environment variable 'SHAPELETS_AGREEMENT' or in the
        'settings.toml' file. In the event that the license ID is not found in either location, the system will
        initiate a request for an evaluation license to ensure seamless functionality.
        The signed license will be store in .shapelets/license.
        If there is a commercial license, the attribute commercial will be filled with a signed message from Grand Central.
    """
    __slots__ = ('_gc_url',)

    def __init__(self, settings: Settings) -> None:
        self._server_settings = settings
        self._gc_url = settings.grand_central
        self.license_id = os.getenv('SHAPELETS_AGREEMENT') if os.getenv(
            'SHAPELETS_AGREEMENT') else settings.server.license
        self.last_version = 1
        self.license_revoked = False  # True: Revoked / False: Active
        self.last_nonce: bytes = self._last_nonce()
        self._create_license_folder()
        self.commercial = None
        self.request_license()

    @staticmethod
    def _create_license_folder():
        """
        Makes sure .shapelets and license folder are created
        """
        os.makedirs(home_dir, exist_ok=True)
        os.makedirs(license_folder, exist_ok=True)

    def license_status(self) -> str:
        return "Revoked" if self.license_revoked else "Active"

    def current_version(self) -> int:
        return self.last_version

    def license_type(self) -> str:
        if self.commercial is not None and verify_signed_message(self.commercial):
            return "Commercial"
        return "Free"

    def _last_nonce(self) -> bytes:
        """
        Retrieve last nonce used from Grand Central
        return: last nonce
        """
        gc_address = f"https://{self._gc_url}/license/nonce"
        last_nonce = _last_nonce(gc_address)
        return last_nonce

    def _check_nonce(self, nonce: bytes) -> bool:
        """
        Check that the received nonce is bigger than the stored nonce. If so, save the new nonce.
        param: nonce
        return: True or raise exception
        """
        if nonce > self.last_nonce:
            self.last_nonce = nonce
            return True
        raise Exception("Unable to match nonce")

    def last_license_version(self):
        """
        Check if latest license is presented in the local machine. If not, download the latest available version.
        """
        if self.license_id is None:
            raise Exception("Shapelets Agreement Not Found")
        address = f"https://{self._gc_url}/license/version/{self.license_id}"
        gc_license_version, nonce = _last_license_version(address)
        if self._check_nonce(nonce):
            if gc_license_version != self.last_version:
                self.request_license()

    def request_evaluation_license(self):
        address = f"https://{self._gc_url}/license/evaluation/"
        _request_evaluation_license(address, self.license_id)

    def request_license(self):
        """
        Download license file and signature file from Grand Central. If no license ID is found, request an evaluation
        license.
        """
        if self.license_id is None:
            # Request evaluation license
            self.license_id = str(self._server_settings.telemetry.id)
            self._server_settings.server.license = self.license_id
            # Add to the actual settings.toml
            _update_license_id(self.license_id)
            self.request_evaluation_license()

        # Download License
        signature_path = os.path.join(license_folder, f"{self.license_id}_signature")
        _download_file_from_gc(f"https://{self._gc_url}/license/signature/{self.license_id}", signature_path)
        try:
            # Verify Signature
            data = _verify_license(signature_path)
        except Exception:
            raise RuntimeError(f"Unable to verify license")
        license = tomlkit.loads(data.decode("utf-8-sig"))
        # Apply last version
        self.last_version = license.get("License").get("version")
        self.apply_license(license.get("Product").get("Platform"))

    def revoke_license(self) -> bool:
        """
        Check if a license is revoked.
        """
        return self.license_revoked

    def apply_license(self, platform: tomlkit.items.Table) -> Optional[bytes]:
        status = platform.get("Status")
        if status != "Active":
            self.license_revoked = True
            # raise RuntimeError("License status: Revoked.")
        licensing = platform.get("Licensing")
        if licensing == "Free":
            # Free license, return nothing.
            return None
        elif licensing == "Commercial":
            # 1. Let´s request a singed message.
            # 2. Incorporate the obtained signed message into the commercial attribute.
            # 3. For external logins, access is restricted unless the presented message is both valid and signed,
            # ensuring an enhanced layer of security.
            gc_address = f"https://{self._gc_url}/license/signedMessage"
            sig_message = _request_signed_message(gc_address)
            self.commercial = sig_message
        else:
            raise RuntimeError("License type not found.")
