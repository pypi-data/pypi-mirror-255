import base64
import os
import requests
import tomlkit

from nacl.encoding import Base64Encoder
from nacl.signing import VerifyKey

from typing import Tuple

home_dir = os.path.expanduser('~/.shapelets')
license_folder = os.path.join(home_dir, 'license')

shapelets_pk = b"bwlHtdRgLBvj5UUp/tBuHFE7+jW8FUtlS2pLUCbW//s="
verify_key = VerifyKey(shapelets_pk, encoder=Base64Encoder)


def _last_license_version(gc_address: str) -> Tuple[int, bytes]:
    """
    Request the last version available for the given license ID.
    param gc_address: Endpoint address from Grand Central.
    return: license version in integer format and nonce
    """
    license_version = requests.get(gc_address, verify=False)
    license_sig = verify_key.verify(Base64Encoder.decode(license_version.content), encoder=Base64Encoder)
    version_num, nonce = license_sig.decode("utf-8").split("_nonce_")
    return int(version_num), base64.b64decode(nonce)


def _last_nonce(gc_address: str) -> bytes:
    """
    Request the last nonce used by Grand Central.
    param gc_address: Endpoint address from Grand Central.
    return: last nonce.
    """
    last_nonce = requests.get(gc_address, verify=False)
    last_nonce_sig = verify_key.verify(Base64Encoder.decode(last_nonce.content), encoder=Base64Encoder)
    return last_nonce_sig


def _download_file_from_gc(gc_address: str, dst: os.path) -> None:
    """
    Download file from Grand Central
    :param gc_address: GC Request address
    :param dst: local destination for the downloaded file
    :return: None
    """
    with requests.get(gc_address, stream=True, verify=False) as r:
        r.raise_for_status()
        with open(dst, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def _verify_license(signature_file: str) -> bytes:
    """
    Verify license signature
    """
    with open(signature_file, "rb") as file:
        data = file.read()
        verify = verify_key.verify(data, encoder=Base64Encoder)
    return verify


def _request_signed_message(gc_address: str) -> bytes:
    """
    Sends a GET request to the Grand Central asking for a random signed message.
    :param gc_address (str): The address of the endpoint to send the request to.

    Returns:
        bytes: Signed message.

    """
    message = requests.get(gc_address, verify=False)
    verify_key.verify(Base64Encoder.decode(message.content), encoder=Base64Encoder)
    return message.content


def _request_evaluation_license(gc_address: str, license_id=str, product="Platform"):
    """
    Sends a GET request to Grand Central with parameters `license_id` and `product`.
    :param gc_address (str): The address of the endpoint to send the request to.
    :param license_id (str, optional): The license ID. It is used to create a license with the given ID.
    :param product (str, optional): Request license for the product name. Defaults to "Platform".

    Raises:
        Exception: If the request does not return a status code of 200.
    """
    parameters = [("product", product), ("license_id", license_id)]
    message = requests.get(gc_address, params=parameters, verify=False)
    if message.status_code != 200:
        raise Exception("Unable to generate evaluation license")


def verify_signed_message(message: str) -> bool:
    """
    Verifies the signature of the provided base64-encoded `message` using the verify_key.
    :param message (str): The base64-encoded message to verify.
    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    if verify_key.verify(Base64Encoder.decode(message), encoder=Base64Encoder):
        return True
    return False
