from rodi import Container

from .ilicenseservice import ILicenseService
from .licenseservice import LicenseService
from .licensehttp import LicenseHttpProxy, LicenseHttpServer


def setup_remote_client(container: Container):
    container.add_singleton(ILicenseService, LicenseHttpProxy)


def setup_services(container: Container):
    container.add_singleton(ILicenseService, LicenseService)


__all__ = [
    'setup_remote_client', 'setup_services',
    'ILicenseService', 'LicenseHttpServer', 'LicenseService'
]
