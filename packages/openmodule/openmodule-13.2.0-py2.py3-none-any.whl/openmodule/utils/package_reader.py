from typing import Dict, Optional, List

from openmodule.core import core
from openmodule.models.base import OpenModuleModel
from openmodule.rpc import RPCClient


class PackageData(OpenModuleModel):
    readable_name: str
    description: str
    model: Optional[str]


class BaseSetting(OpenModuleModel):
    hardware_type: Optional[List[str]]
    parent_type: Optional[List[str]]
    software_type: Optional[List[str]]
    name: str
    revision: int
    env: Dict
    yml: Dict
    package_data: Optional[PackageData]


class ServiceSetting(BaseSetting):
    parent: Optional[BaseSetting]


class ConfigGetInstalledServicesRequest(OpenModuleModel):
    """
    Request to get all installed services which start with a given predix.
    """
    compute_id: Optional[int] = None
    prefix: Optional[str] = ""


class ConfigGetServiceByNameRequest(OpenModuleModel):
    """
    Request a service by its name
    """
    name: str


class ConfigGetServiceResponse(OpenModuleModel):
    service: Optional[ServiceSetting]


class ConfigGetServicesResponse(OpenModuleModel):
    services: List[ServiceSetting]


class ConfigGetServicesByHardwareTypeRequest(OpenModuleModel):
    """
    Request to get all services with a hardware type starting with the given prefix.
    This request always returns the configurations of the services.
    """
    compute_id: Optional[int] = None
    hardware_type_prefix: Optional[str] = ""


class ConfigGetServicesByParentTypeRequest(OpenModuleModel):
    """
    Returns the configs of all services for which a parent type starts with the given prefix
    Optionally you can include the parent configs in the response.
    This request always returns the configurations of the services.
    """
    compute_id: Optional[int] = None
    parent_type_prefix: Optional[str] = ""


class ConfigGetServicesBySoftwareTypeRequest(OpenModuleModel):
    """
    Request to get all services with a software type starting with the given prefix.
    This request always returns the configurations of the services.
    """
    compute_id: Optional[int] = None
    software_type_prefix: Optional[str] = ""


class PackageReader:
    def __init__(self, rpc_client: Optional[RPCClient] = None):
        self.rpc_client = rpc_client or core().rpc_client

    def get_service_by_name(self, service: str) -> Optional[ServiceSetting]:
        """
        returns a service by its name
        """
        return self.rpc_client.rpc(
            "config", "get_service_by_name",
            ConfigGetServiceByNameRequest(name=service),
            ConfigGetServiceResponse
        ).service

    def list_all_services(self, prefix: Optional[str] = None, compute_id: Optional[int] = None) -> List[ServiceSetting]:
        """
        :param prefix: prefix of the package id, if none is passed all are returned
        """
        return self.rpc_client.rpc(
            "config", "get_services",
            ConfigGetInstalledServicesRequest(prefix=prefix, compute_id=compute_id),
            ConfigGetServicesResponse
        ).services

    def list_by_hardware_type(self, prefix: str, compute_id: Optional[int] = None) -> List[ServiceSetting]:
        """
        lists all packages with a certain hardware type (prefix). Note that these can only be hardware packages
        i.e. their name starts with "hw_"

        :param prefix: prefix of the hardware type
        """
        return self.rpc_client.rpc(
            "config", "get_services_by_hardware_type",
            ConfigGetServicesByHardwareTypeRequest(hardware_type_prefix=prefix, compute_id=compute_id),
            ConfigGetServicesResponse
        ).services

    def list_by_parent_type(self, prefix: str, compute_id: Optional[int] = None) -> List[ServiceSetting]:
        """
        lists all packages with a certain parent type (prefix). Note that these can only be software packages
        i.e. their name starts with "om_"

        :param prefix: prefix of the parent type
        """
        return self.rpc_client.rpc(
            "config", "get_services_by_parent_type",
            ConfigGetServicesByParentTypeRequest(parent_type_prefix=prefix, compute_id=compute_id),
            ConfigGetServicesResponse
        ).services

    def list_by_software_type(self, prefix: str, compute_id: Optional[int] = None) -> List[ServiceSetting]:
        """
        lists all packages with a certain software type (prefix). Note that these can only be software packages
        i.e. their name starts with "om_"

        :param prefix: prefix of the software type
        """
        return self.rpc_client.rpc(
            "config", "get_services_by_software_type",
            ConfigGetServicesBySoftwareTypeRequest(software_type_prefix=prefix, compute_id=compute_id),
            ConfigGetServicesResponse
        ).services
