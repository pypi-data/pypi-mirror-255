from pih.consts import SPLITTER, ISOLATED_ARG_NAME
from pih.consts.service_roles import ServiceRoles
from pih.consts.service import EVENT_LISTENER_NAME_PREFIX, SUPPORT_NAME_PREFIX
from pih.collections.service import ServiceDescriptionBase, ServiceInformation, ServiceDescription
from pih.tools import NetworkTool, OSTool, j, e

from enum import Enum


class ServiceTool:

    @staticmethod
    def is_service_as_listener(description: ServiceDescriptionBase) -> bool:
        return description.name.find(EVENT_LISTENER_NAME_PREFIX) == 0

    @staticmethod
    def is_service_as_support(description: ServiceDescriptionBase) -> bool:
        return description.name.find(SUPPORT_NAME_PREFIX) == 0


class ServiceAdminTool:
    
    SERVICE_INFORMATION_MAP: dict[
                ServiceDescriptionBase, ServiceInformation
            ] = {}
    
    @staticmethod
    def update_service_information(
        list: list[ServiceInformation],
        add: bool = True,
        overwrite: bool = False,
    ) -> None:
        if overwrite:
            ServiceAdminTool.SERVICE_INFORMATION_MAP = {}
        for item in list:
            if add:
                ServiceAdminTool.SERVICE_INFORMATION_MAP[item] = item
            else:
                if item in ServiceAdminTool.SERVICE_INFORMATION_MAP:
                    del ServiceAdminTool.SERVICE_INFORMATION_MAP[item]
                    
    @staticmethod
    def create_port(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> int:
        return (
            ServiceRoleTool.service_description(service_role_or_description).port
            or NetworkTool.next_free_port()
        )

    @staticmethod
    def create_host(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> str:
        description: ServiceDescription = ServiceRoleTool.service_description(
            service_role_or_description
        )
        return (
            OSTool.host()
            if description.isolated or e(description.host)
            else description.host
        )


class ServiceRoleTool:
    
   

    @staticmethod
    def service_description(
        value: Enum | str | ServiceDescriptionBase, get_source_description: bool = False
    ) -> ServiceDescriptionBase | None:
        def isolated_name(
            value: ServiceDescriptionBase | None,
        ) -> ServiceDescriptionBase | None:
            if value is None:
                return None
            value.name = (
                j((ISOLATED_ARG_NAME, value.name), SPLITTER)
                if value.isolated and value.name.find(ISOLATED_ARG_NAME) == -1
                else value.name
            )
            return value

        if isinstance(value, str):
            for service_role in ServiceRoles:
                if ServiceRoleTool.service_description(service_role).name == value:
                    return isolated_name(service_role.value)
            return None
        if isinstance(value, ServiceDescriptionBase):
            return isolated_name(
                ServiceRoleTool.service_description(value.name)
                if get_source_description
                else value
            )
        return isolated_name(value.value)
