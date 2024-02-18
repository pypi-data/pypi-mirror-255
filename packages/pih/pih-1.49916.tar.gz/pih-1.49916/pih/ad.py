from pih.tools import j
from pih.names import USER_PROPERTIES

from enum import Enum, IntEnum, auto

class AD:
    
    SPLITTER: str = "."
    OU: str = "OU="
    SEARCH_ATTRIBUTES: list[str] = [USER_PROPERTIES.LOGIN, USER_PROPERTIES.NAME]
    SEARCH_ATTRIBUTE_DEFAULT: str = SEARCH_ATTRIBUTES[0]
    USER_HOME_FOLDER_DISK: str = "U:"
    SEARCH_ALL_PATTERN: str = "*"
    LOCATION_JOINER: str = ":"
    TEMPLATED_USER_SERACH_TEMPLATE: str = j(("_", SEARCH_ALL_PATTERN, "_"))
    

    USER_ACCOUNT_CONTROL: list[str] = [
        "SCRIPT",
        "ACCOUNTDISABLE",
        "RESERVED",
        "HOMEDIR_REQUIRED",
        "LOCKOUT",
        "PASSWD_NOTREQD",
        "PASSWD_CANT_CHANGE",
        "ENCRYPTED_TEXT_PWD_ALLOWED",
        "TEMP_DUPLICATE_ACCOUNT",
        "NORMAL_ACCOUNT",
        "RESERVED",
        "INTERDOMAIN_TRUST_ACCOUNT",
        "WORKSTATION_TRUST_ACCOUNT",
        "SERVER_TRUST_ACCOUNT",
        "RESERVED",
        "RESERVED",
        "DONT_EXPIRE_PASSWORD",
        "MNS_LOGON_ACCOUNT",
        "SMARTCARD_REQUIRED",
        "TRUSTED_FOR_DELEGATION",
        "NOT_DELEGATED",
        "USE_DES_KEY_ONLY",
        "DONT_REQ_PREAUTH",
        "PASSWORD_EXPIRED",
        "TRUSTED_TO_AUTH_FOR_DELEGATION",
        "RESERVED",
        "PARTIAL_SECRETS_ACCOUNT",
    ]
    
    DOMAIN_NAME: str = "fmv"
    DOMAIN_ALIAS: str = "pih"
    DOMAIN_SUFFIX: str = "lan"
    DOMAIN_DNS: str = j((DOMAIN_NAME, DOMAIN_SUFFIX), SPLITTER)
    DOMAIN_MAIN: str = DOMAIN_DNS
    PATH_ROOT: str = j(("//", DOMAIN_MAIN))

    ROOT_CONTAINER_DN: str = f"{OU}Unit,DC={DOMAIN_NAME},DC={DOMAIN_SUFFIX}"
    WORKSTATIONS_CONTAINER_DN: str = f"{OU}Workstations,{ROOT_CONTAINER_DN}"
    SERVERS_CONTAINER_DN: str = f"{OU}Servers,{ROOT_CONTAINER_DN}"
    USERS_CONTAINER_DN_SUFFIX: str = f"Users,{ROOT_CONTAINER_DN}"
    ACTIVE_USERS_CONTAINER_DN: str = f"{OU}{USERS_CONTAINER_DN_SUFFIX}"
    INACTIVE_USERS_CONTAINER_DN: str = f"{OU}dead{USERS_CONTAINER_DN_SUFFIX}"
    GROUP_CONTAINER_DN: str = f"{OU}Groups,{ROOT_CONTAINER_DN}"
    PROPERTY_ROOT_DN: str = f"{OU}Property,{GROUP_CONTAINER_DN}"
    PROPERTY_WS_DN: str = f"{OU}WS,{PROPERTY_ROOT_DN}"
    PROPERTY_USER_DN: str = f"{OU}User,{PROPERTY_ROOT_DN}"
    JOB_POSITION_CONTAINER_DN: str = f"{OU}Job positions,{GROUP_CONTAINER_DN}"

    WORKSTATION_PREFIX_LIST: list[str] = ["ws-", "nb-", "fmvulianna"]

    class USER:
        MARKETER_ADMINISTRATOR: str = "marketer_admin"
        CALL_CENTRE_ADMINISTRATOR: str = "callCentreAdmin"
        REGISTRATION_AND_CALL: str = "reg_and_call"
        CONTROL_SERVICE: str = "cctv"
        INDICATIONS_ALL: str = "indications_all"
        ADMINISTRATOR: str = "Administrator"

    class JobPositions(IntEnum):
        HR: int = auto()
        IT: int = auto()
        CALL_CENTRE: int = auto()
        REGISTRATOR: int = auto()
        RD: int = auto()
        MARKETER: int = auto()

    class Groups(IntEnum):
        TimeTrackingReport: int = auto()
        Inventory: int = auto()
        Polibase: int = auto()
        Admin: int = auto()
        ServiceAdmin: int = auto()
        CardRegistry: int = auto()
        PolibaseUsers: int = auto()
        RD: int = auto()
        IndicationWatcher: int = auto()
        FunctionalDiagnostics: int = auto()

    class WSProperies(IntEnum):
        Watchable: int = 1
        Shutdownable: int = 2
        Rebootable: int = 4
        DiskReportable: int = 8
        
    class UserProperies(IntEnum):
        Jokeless: int = 1
        DoctorVisitless: int = 2
        HasLunchBreak: int = 4
        TimeTrackingless: int = 8