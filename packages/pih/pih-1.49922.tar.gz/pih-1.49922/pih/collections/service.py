import ipih
from dataclasses import dataclass, field
from pih.consts.service_commands import ServiceCommands
from typing import Any


@dataclass
class ServiceDescriptionBase:
    name: str | None = None
    host: str | None = None
    port: int | None = None
    service_path: str | None = None
    isolated: bool | None = None
    host_changeable: bool = True
    visible_for_admin: bool = True
    auto_start: bool = True
    auto_restart: bool = True
    run_from_system_account: bool = False
    pyton_executor_path: str | None = None
    version: str | None = None
    pih_version: str | None = None
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, another):
        return False if another is None else self.name == another.name if isinstance(another, ServiceDescriptionBase) else self.name == another
  
    
@dataclass
class SubscribtionDescription:
    service_command: ServiceCommands | None = None
    type: int | None = None
    name: str | None = None
   
@dataclass
class Subscribtion(SubscribtionDescription):
    available: bool = False
    enabled: bool = False

@dataclass
class SubscribtionInformation(SubscribtionDescription):
    pass

@dataclass
class ServiceInformation(ServiceDescriptionBase):
    subscribtions: list[Subscribtion] = field(default_factory=list)
    pid: int = -1
    standalone: bool | None = None

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, another):
        return False if another is None else self.name == another.name if isinstance(another, ServiceDescriptionBase) else self.name == another

@dataclass
class ServiceDescription(ServiceDescriptionBase):
    description: str | None = None
    login: str | None = None
    password: str | None = None
    commands: list[ServiceCommands | str] = field(default_factory=list)
    use_standalone: bool | None = None
    standalone_name: str | None = None
    support_servers: tuple[str] | None = None

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, another):
        return False if another is None else self.name == another.name if isinstance(another, ServiceDescriptionBase) else self.name == another

@dataclass
class SubscriberInformation:
    type: int | None = None
    name: str | None = None
    available: bool = True
    enabled: bool = True
    service_information: ServiceDescriptionBase | None = None

@dataclass
class SubscribtionResult:
    result: Any | None = None
    type: int = 0
    checker: bool = False