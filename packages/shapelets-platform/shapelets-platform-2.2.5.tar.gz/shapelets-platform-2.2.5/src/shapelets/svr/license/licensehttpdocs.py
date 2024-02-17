from blacksheep.server.openapi.common import EndpointDocs

__tags = ["License"]

license_version = EndpointDocs(summary="Curren version of the version")

license_status = EndpointDocs(summary="Status of the license")

license_type = EndpointDocs(summary="Returns the type of the license (Free/Commercial).")

__all__ = ['license_version', 'license_status']
