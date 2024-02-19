from enum import Enum, auto, IntEnum

from pih.consts import *
from pih.consts.names import *
from pih.consts.date_time import *
from pih.consts.password import *
from pih.collections.service import ServiceDescription

from pih.collections import (
    ActionDescription,
    ResourceDescription,
    MedicalResearchType,
    SiteResourceDescription,
    MinIntStorageVariableHolder,
    ResourceDescriptionDelegated,
    OrderedNameCaptionDescription,
    IconedOrderedNameCaptionDescription,
)
from pih.consts.service_commands import *
from pih.consts.paths import *


VERSION: str = "1.49921"

class EMAIL:
    SPLITTER: str = "@"


class ADDRESSES:
    SITE_NAME: str = "pacifichosp"
    SITE_ADDRESS: str = ".".join((SITE_NAME, "com"))
    EMAIL_SERVER_ADDRESS: str = ".".join(("mail", SITE_ADDRESS))
    RECEPTION_LOGIN: str = ".".join(("reception", SITE_NAME))

    WIKI_SITE_NAME: str = "wiki"
    WIKI_SITE_ADDRESS: str = WIKI_SITE_NAME
    OMS_SITE_NAME: str = "oms"
    OMS_SITE_ADDRESS: str = OMS_SITE_NAME
    API_SITE_ADDRESS: str = ".".join(("api", SITE_ADDRESS))
    BITRIX_SITE_URL: str = "bitrix.cmrt.ru"


class EMAIL_COLLECTION:
    MAIL_RU_NAME: str = "mail.ru"
    MAIL_RU_DAEMON: str = ".".join(("mailer-daemon@corp", MAIL_RU_NAME))
    MAIL_RU_IMAP_SERVER: str = ".".join(("imap", MAIL_RU_NAME))

    NAS: str = EMAIL.SPLITTER.join(("nas", ADDRESSES.SITE_ADDRESS))
    IT: str = EMAIL.SPLITTER.join(("it", ADDRESSES.SITE_ADDRESS))
    EXTERNAL: str = "".join(
        ("mail.", ADDRESSES.SITE_NAME, EMAIL.SPLITTER, MAIL_RU_NAME)
    )

    EXTERNAL_SERVER: str = MAIL_RU_IMAP_SERVER


ISOLATED_ARG_NAME: str = "isolated"
ARGUMENT_PREFIX: str = "--"
SPLITTER: str = ":"


class SERVICE:
    EVENT_LISTENER_NAME_PREFIX: str = "_@@EventListener@@_"
    SUPPORT_NAME_PREFIX: str = "_@@Support@@_"


class DATA:
    # deprecated
    class EXTRACTOR:
        USER_NAME_FULL: str = "user_name_full"
        USER_NAME: str = "user_name"
        AS_IS: str = "as_is"

    class FORMATTER(Enum):
        MY_DATETIME: str = "my_datetime"
        MY_DATE: str = "my_date"
        CHILLER_INDICATIONS_VALUE_INDICATORS: str = (
            "chiller_indications_value_indicators"
        )
        CHILLER_FILTER_COUNT: str = "chiller_filter_count"


class INDICATIONS:
    class CHILLER:
        ACTUAL_VALUES_TIME_DELTA_IN_MINUTES: int = 5

        INDICATOR_NAME: list[str] = [
            "Активный сигнал тревоги",
            "Работает нагреватель",
            "Замораживание включено",
            "Работает вентилятор конденсатора",
            "Работает насос/вытяжной вентилятор",
            "Работает компрессор",
        ]

        INDICATOR_EMPTY_DISPLAY: int = -1

    class MRI:
        # hours
        PERIOD: int = 2


class BARCODE:
    CODE128: str = "code128"
    I25: str = "i25"


class FONT:
    FOR_PDF: str = "DejaVuSerif"


class SessionFlags(IntEnum):
    CLI: int = 512


class URLS:
    PYPI: str = "https://pypi.python.org/pypi/pih/json"


class EmailVerificationMethods(IntEnum):
    NORMAL: int = auto()
    ABSTRACT_API: int = auto()
    DEFAULT: int = NORMAL


class ROBOCOPY:
    ERROR_CODE_START: int = 8

    STATUS_CODE: dict[int, str] = {
        0: "No errors occurred, and no copying was done. The source and destination directory trees are completely synchronized.",
        1: "One or more files were copied successfully (that is, new files have arrived).",
        2: "Some Extra files or directories were detected. No files were copied Examine the output log for details.",
        4: "Some Mismatched files or directories were detected. Examine the output log. Housekeeping might be required.",
        8: "Some files or directories could not be copied (copy errors occurred and the retry limit was exceeded). Check these errors further.",
        16: "Serious error. Robocopy did not copy any files. Either a usage error or an error due to insufficient access privileges on the source or destination directories.",
        3: "Some files were copied. Additional files were present. No failure was encountered.",
        5: "Some files were copied. Some files were mismatched. No failure was encountered.",
        6: "Additional files and mismatched files exist. No files were copied and no failures were encountered. This means that the files already exist in the destination directory",
        7: "Files were copied, a file mismatch was present, and additional files were present.",
    }


class WINDOWS:
    class ENVIROMENT_VARIABLES:
        PATH: str = "PATH"

    ENVIROMENT_COMMAND: str = "$Env"

    class CHARSETS:
        ALTERNATIVE: str = "CP866"

    class SERVICES:
        WIA: str = "stisvc"  # Обеспечивает службы получения изображений со сканеров и цифровых камер
        TASK_SCHEDULER: str = "schtasks"

    class PROCESSES:
        POWER_SHELL_REMOTE_SESSION: str = "wsmprovhost.exe"

    class PORT:
        SMB: int = 445


class LINK:
    ADMINISTRATOR_PASSWORD: str = "ADMINISTRATOR_PASSWORD"
    ADMINISTRATOR_LOGIN: str = "ADMINISTRATOR_LOGIN"

    DEVELOPER_LOGIN: str = "DEVELOPER_LOGIN"
    DEVELOPER_PASSWORD: str = "DEVELOPER_PASSWORD"

    USER_LOGIN: str = "USER_LOGIN"
    USER_PASSWORD: str = "USER_PASSWORD"

    SERVICES_USER_LOGIN: str = "SERVICES_LOGIN"
    SERVICES_USER_PASSWORD: str = "SERVICES_PASSWORD"

    DATABASE_ADMINISTRATOR_LOGIN: str = "DATABASE_ADMINISTRATOR_LOGIN"
    DATABASE_ADMINISTRATOR_PASSWORD: str = "DATABASE_ADMINISTRATOR_PASSWORD"


class CONST(DATE_TIME):
    class PORT:
        HTTP: int = 80
        SMTP: int = 587
        IMAP: int = 993

    class FILES:
        SECTION: str = "Мобильные файлы"

    class NOTES:
        FILE_SECTION: str = "Мобильные файлы"
        JOURNAL_SECTION: str = "Журналы"

    # in seconds
    HEART_BEAT_PERIOD: int = 60

    NEW_LINE: str = "\n"

    class TEST:
        WORKSTATION_MAME: str = HOSTS.DEVELOPER.NAME
        USER: str | None = "nak"
        EMAIL_ADDRESS: str | None = "nak@pacifichosp.com"
        PIN: int = 117276
        NAME: str = "test"

    GROUP_PREFIX: str = "group:"

    SITE_PROTOCOL: str = "https://"
    UNTRUST_SITE_PROTOCOL: str = "http://"

    INTERNATIONAL_TELEPHONE_NUMBER_PREFIX: str = "7"
    TELEPHONE_NUMBER_PREFIX: str = f"+{INTERNATIONAL_TELEPHONE_NUMBER_PREFIX}"
    INTERNAL_TELEPHONE_NUMBER_PREFIX: str = "тел."

    class CACHE:
        class TTL:
            # in seconds
            WORKSTATIONS: int = 60
            USERS: int = 300

    class ERROR:
        class WAPPI:
            PROFILE_NOT_PAID: int = 402

    class TIME_TRACKING:
        REPORT_DAY_PERIOD_DEFAULT: int = 15

    class MESSAGE:
        class WHATSAPP:
            SITE_NAME: str = "https://wa.me/"
            SEND_MESSAGE_TO_TEMPLATE: str = SITE_NAME + "{}?text={}"
            GROUP_SUFFIX: str = "@g.us"

            class GROUP(Enum):
                # IT: str = "120363163438805316@g.us"
                PIH_CLI: str = "120363163438805316@g.us"
                REGISTRATOR_CLI: str = "120363212130686795@g.us"
                RD: str = "79146947050-1595848245@g.us"
                MAIN: str = "79644300470-1447044803@g.us"
                EMAIL_CONTROL: str = "120363159605715569@g.us"
                CT_INDICATIONS: str = "120363084280723039@g.us"
                DOCUMENTS_WORK_STACK: str = "120363115241877592@g.us"
                REGISTRATION_AND_CALL: str = "79242332784-1447983812@g.us"
                DOCUMENTS_WORK_STACK_TEST: str = "120363128816931482@g.us"
                CONTROL_SERVICE_INDICATIONS: str = "120363159210756301@g.us"
                SCANNED_DOCUMENT_HELPER_CLI: str = "120363220286578760@g.us"

            class WAPPI:
                PROFILE_SUFFIX: str = "profile_id="
                URL_API: str = "https://wappi.pro/api"
                URL_API_SYNC: str = f"{URL_API}/sync"
                URL_MESSAGE: str = f"{URL_API_SYNC}/message"
                URL_SEND_MESSAGE: str = f"{URL_MESSAGE}/send?{PROFILE_SUFFIX}"
                URL_SEND_VIDEO: str = f"{URL_MESSAGE}/video/send?{PROFILE_SUFFIX}"
                URL_SEND_IMAGE: str = f"{URL_MESSAGE}/img/send?{PROFILE_SUFFIX}"
                URL_SEND_DOCUMENT: str = f"{URL_MESSAGE}/document/send?{PROFILE_SUFFIX}"
                URL_SEND_LIST_MESSAGE: str = f"{URL_MESSAGE}/list/send?{PROFILE_SUFFIX}"
                URL_SEND_BUTTONS_MESSAGE: str = (
                    f"{URL_MESSAGE}/buttons/send?{PROFILE_SUFFIX}"
                )
                URL_GET_MESSAGES: str = f"{URL_MESSAGE}s/get?{PROFILE_SUFFIX}"
                URL_GET_STATUS: str = f"{URL_API_SYNC}/get/status?{PROFILE_SUFFIX}"
                CONTACT_SUFFIX: str = "@c.us"

                class Profiles(Enum):
                    IT: str = "e6706eaf-ae17"
                    CALL_CENTRE: str = "285c71a4-05f7"
                    MARKETER: str = "c31db01c-b6d6"
                    DEFAULT: str = CALL_CENTRE

                AUTHORIZATION: dict[Profiles, str] = {
                    Profiles.IT: "6b356d3f53124af3078707163fdaebca3580dc38",
                    Profiles.MARKETER: "6b356d3f53124af3078707163fdaebca3580dc38",
                    Profiles.CALL_CENTRE: "7d453de6fc17d3e6816b0abc46f2b192822130f5",
                }

    class PYTHON:
        EXECUTOR_ALIAS: str = "py"
        EXECUTOR: str = "python"
        EXECUTOR3: str = "python3"
        PYPI: str = "pip"
        SEARCH_PATTERN: str = "\\Python\\Python"

        class COMMAND:
            VERSION: str = "--version"
            INSTALL: str = "install"
            SHOW: str = "show"
            FLAG: str = "-c"

    class SERVICE:
        NAME: str = "service"

    class VALENTA:
        PROCESS_NAME: str = "Vlwin"

    class POWERSHELL:
        NAME: str = "powershell"

    class PSTOOLS:
        NAME: str = "pstools"
        PS_EXECUTOR: str = "psexec"
        PS_KILL_EXECUTOR: str = "pskill"
        PS_PING: str = "psping"

        COMMAND_LIST: list[str] = [
            PS_KILL_EXECUTOR,
            "psfile",
            "psgetsid",
            "psinfo",
            "pslist",
            "psloggedon",
            "psloglist",
            "pspasswd",
            PS_PING,
            "psservice",
            "psshutdown",
            "pssuspend",
        ]

        NO_BANNER: str = "-nobanner"
        ACCEPTEULA: str = "-accepteula"

    class MSG:
        NAME: str = "msg"
        EXECUTOR: str = NAME

    class BARCODE_READER:
        PREFIX: str = "("
        SUFFIX: str = ")"

    class NAME_POLICY:
        PARTS_LIST_MIN_LENGTH: int = 3
        PART_ITEM_MIN_LENGTH: int = 3


    HOST = HOSTS()

    class CARD_REGISTRY:
        PLACE_NAME: dict[str, str] = {"Т": "Приёмное отделение", "П": "Поликлиника"}
        PLACE_CARD_HOLDER_MAPPER: dict[str, str] = {"Т": "М-Я", "П": "А-Л"}
        MAX_CARD_PER_FOLDER: int = 60
        SUITABLE_FOLDER_NAME_SYMBOL: tuple[str] = ("!", " ")

    class VISUAL:
        YES: str = "✅"
        NO: str = "❌"
        WARNING: str = "⚠️"
        WAIT: str = "⏳"
        NOTIFICATION: str = "🔔"
        ROBOT: str = "🤖"
        GOOD: str = YES
        ERROR: str = NO
        ORANGE_ROMB: str = "🔸"
        TASK: str = "✳️"
        EYE: str = "👁️"
        HAND_INDICATE: str = "👉"
        HAND_DOWN: str = "👇"
        HAND_UP: str = "☝️"
        INFORMATION: str = "ℹ️"
        QUESTION: str = "❔"

        NUMBER_SYMBOLS: list[str] = [
            "0️⃣",
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟",
        ]

        TEMPERATURE_SYMBOL: str = "°C"

        ARROW: str = "➜"

        BULLET: str = "•"


class MATERIALIZED_RESOURCES:
    NAME: str = "MATERIALIZED_RESOURCES"
    ALIAS: str = "MR"

    class TYPES(Enum):
        CHILLER_FILTER: MinIntStorageVariableHolder = MinIntStorageVariableHolder(
            "CHF", description="Фильтры для чиллера", min_value=2
        )

        OPTICAL_DISK_IN_STOCK: MinIntStorageVariableHolder = (
            MinIntStorageVariableHolder(
                "ODS",
                description="Оптические диски для записи исследований на складе",
                min_value=50,
            )
        )

        OPTICAL_DISK_IN_USE: MinIntStorageVariableHolder = MinIntStorageVariableHolder(
            "ODU",
            description="Оптические диски для записи исследований в пользовании",
            min_value=10,
        )


class MedicalResearchTypes(Enum):
    MRI: MedicalResearchType = MedicalResearchType(
        ("Магнитно-резонансная томография",), "МРТ"
    )
    CT: MedicalResearchType = MedicalResearchType(("Компьютерная томография",), "КТ")
    ULTRASOUND: MedicalResearchType = MedicalResearchType(
        ("ультразвуковая допплерография",), "УЗИ"
    )


class RESOURCES:
    class DESCRIPTIONS:
        INTERNET: ResourceDescription = ResourceDescription(
            "77.88.55.242", "Интернет соединение"
        )

        VPN_PACS_SPB: ResourceDescriptionDelegated = ResourceDescriptionDelegated(
            "192.168.5.3", "VPN соединение для PACS SPB", (2, 100, 5), HOSTS.WS255.NAME
        )

        PACS_SPB: ResourceDescriptionDelegated = ResourceDescriptionDelegated(
            "10.76.12.124:4242", "Соединение PACS SPB", (2, 100, 5), HOSTS.WS255.NAME
        )

        POLIBASE1: ResourceDescription = ResourceDescription(
            HOSTS.POLIBASE1.NAME,
            "Polibase",
            inaccessibility_check_values=(2, 10000, 15),
        )

        POLIBASE2: ResourceDescription = ResourceDescription(
            HOSTS.POLIBASE2.NAME,
            "Polibase reserved",
            inaccessibility_check_values=(2, 10000, 15),
        )
        
        POLIBASE: ResourceDescription = ResourceDescription(
            HOSTS.POLIBASE.ALIAS,
            "Polibase",
            inaccessibility_check_values=(2, 10000, 15),
        )

        SITE_LIST: list[SiteResourceDescription] = [
            SiteResourceDescription(
                ADDRESSES.SITE_ADDRESS,
                f"Сайт компании: {ADDRESSES.SITE_ADDRESS}",
                inaccessibility_check_values=(3, 20, 15),
                check_certificate_status=True,
                check_free_space_status=True,
                driver_name="/dev/mapper/centos-root",
            ),
            SiteResourceDescription(
                ADDRESSES.EMAIL_SERVER_ADDRESS,
                f"Сайт корпоративной почты: {ADDRESSES.EMAIL_SERVER_ADDRESS}",
                check_certificate_status=True,
                check_free_space_status=True,
                driver_name="/dev/mapper/centos_tenant26--02-var",
            ),
            SiteResourceDescription(
                ADDRESSES.API_SITE_ADDRESS,
                f"Api сайта {ADDRESSES.SITE_ADDRESS}: {ADDRESSES.API_SITE_ADDRESS}",
                check_certificate_status=True,
                check_free_space_status=False,
            ),
            SiteResourceDescription(
                ADDRESSES.BITRIX_SITE_URL, f"Сайт ЦМРТ24: {ADDRESSES.BITRIX_SITE_URL}"
            ),
            SiteResourceDescription(
                ADDRESSES.OMS_SITE_ADDRESS,
                f"Внутренний сайт омс: {ADDRESSES.OMS_SITE_ADDRESS}",
                internal=True,
            ),
            SiteResourceDescription(
                ADDRESSES.WIKI_SITE_ADDRESS,
                f"Внутренний сайт Вики: {ADDRESSES.WIKI_SITE_ADDRESS}",
                internal=True,
            ),
        ]

    class InaccessableReasons(Enum):
        CERTIFICATE_ERROR: str = "Ошибка проверки сертификата"
        SERVICE_UNAVAILABLE: str = "Ошибка 503: Сервис недоступен"


class CheckableSections(IntEnum):
    RESOURCES: int = auto()
    WS: int = auto()
    PRINTERS: int = auto()
    INDICATIONS: int = auto()
    BACKUPS: int = auto()
    VALENTA: int = auto()
    SERVERS: int = auto()
    MATERIALIZED_RESOURCES: int = auto()
    TIMESTAMPS: int = auto()
    DISKS: int = auto()
    POLIBASE: int = auto()

    @staticmethod
    def all():
        return [item for item in CheckableSections]


class MarkType(IntEnum):
    NORMAL: int = auto()
    FREE: int = auto()
    GUEST: int = auto()
    TEMPORARY: int = auto()


class PolibasePersonInformationQuestStatus(IntEnum):
    UNKNOWN: int = -1
    GOOD: int = 0
    EMAIL_IS_EMPTY: int = 1
    EMAIL_IS_WRONG: int = 2
    EMAIL_IS_NOT_ACCESSABLE: int = 4


class ResourceInaccessableReasons(Enum):
    CERTIFICATE_ERROR: str = "Ошибка проверки сертификата"
    SERVICE_UNAVAILABLE: str = "Ошибка 503: Сервис недоступен"


class PolibasePersonReviewQuestStep(IntEnum):
    BEGIN: int = auto()
    #
    ASK_GRADE: int = auto()
    ASK_FEEDBACK_CALL: int = auto()
    ASK_INFORMATION_WAY: int = auto()
    #
    COMPLETE: int = auto()


LINK_EXT = "lnk"


class PrinterCommands(Enum):
    REPORT: str = "report"
    STATUS: str = "status"


class CommandTypes(Enum):
    POLIBASE: tuple[str] = (
        "Запрос к базе данный Polibase (Oracle)",
        "polibase",
        "полибейс",
        "oracle",
    )
    DATA_SOURCE: tuple[str] = ("Запрос к базе данных DataSource (DS)", "ds")
    CMD: tuple[str] = ("Консольную команду", "cmd")
    PYTHON: tuple[str] = ("Скрипт Python", "py", "python")
    SSH: tuple[str] = ("Команда SSH", "ssh")


class LogMessageChannels(IntEnum):
    BACKUP: int = auto()
    POLIBASE: int = auto()
    POLIBASE_BOT: int = auto()
    DEBUG: int = auto()
    DEBUG_BOT: int = auto()
    SERVICES: int = auto()
    SERVICES_BOT: int = auto()
    HR: int = auto()
    HR_BOT: int = auto()
    IT: int = auto()
    IT_BOT: int = auto()
    RESOURCES: int = auto()
    RESOURCES_BOT: int = auto()
    PRINTER: int = auto()
    POLIBASE_ERROR: int = auto()
    POLIBASE_ERROR_BOT: int = auto()
    CARD_REGISTRY: int = auto()
    CARD_REGISTRY_BOT: int = auto()
    NEW_EMAIL: int = auto()
    NEW_EMAIL_BOT: int = auto()
    TIME_TRACKING: int = auto()
    JOURNAL: int = auto()
    JOURNAL_BOT: int = auto()
    POLIBASE_DOCUMENT: int = auto()
    POLIBASE_DOCUMENT_BOT: int = auto()
    DEFAULT: int = DEBUG


class LogMessageFlags(IntEnum):
    NORMAL: int = 1
    ERROR: int = 2
    NOTIFICATION: str = 4
    DEBUG: str = 8
    SAVE: int = 16
    SILENCE: str = 32
    RESULT: int = 64
    WHATSAPP: int = 128
    ALERT: int = 256
    TASK: int = 512
    SAVE_ONCE: int = 1024
    SEND_ONCE: int = SAVE_ONCE | 2048
    DEFAULT: str = NORMAL


class SUBSCRIBTION_TYPE:
    ON_PARAMETERS: int = 1
    ON_RESULT: int = 2
    ON_RESULT_SEQUENTIALLY: int = 4


class WorkstationMessageMethodTypes(IntEnum):
    REMOTE: int = auto()
    LOCAL_MSG: int = auto()
    LOCAL_PSTOOL_MSG: int = auto()


class MessageTypes(IntEnum):
    WHATSAPP: int = auto()
    TELEGRAM: int = auto()
    WORKSTATION: int = auto()


class MessageStatuses(IntEnum):
    REGISTERED: int = 0
    COMPLETE: int = 1
    AT_WORK: int = 2
    ERROR: int = 3
    ABORT: int = 4


class SCAN:
    SPLITTER_DATA: str = "1"

    class Sources(Enum):
        POLICLINIC: tuple[str, str, str] = ("poly", "Поликлиника", PATH_SCAN.VALUE)
        DIAGNOSTICS: tuple[str, str, str] = (
            "diag",
            "Приёмное отделение",
            PATH_SCAN.VALUE,
        )
        TEST: tuple[str, str, str] = ("test", "Тестовый", PATH_SCAN_TEST.VALUE)
        WS_816: tuple[str, str, str] = (
            "рисунок",
            "Дневной стационар",
            PATH_WS_816_SCAN.VALUE,
        )


class Actions(Enum):
    CHILLER_FILTER_CHANGING: ActionDescription = ActionDescription(
        "CHILLER_FILTER_CHANGING",
        ("filter",),
        "Замена фильтра очистки воды",
        "Заменить фильтр очистки воды",
    )

    SWITCH_TO_EXTERNAL_WATER_SOURCE: ActionDescription = ActionDescription(
        "SWITCH_TO_EXTERNAL_WATER_SOURCE",
        ("external_ws",),
        "Переход на внешнее (городское) водоснабжение",
        "Перейти на внешнее (городское) водоснабжение",
    )

    SWITCH_TO_INTERNAL_WATER_SOURCE: ActionDescription = ActionDescription(
        "SWITCH_TO_INTERNAL_WATER_SOURCE",
        ("internal_ws",),
        "Переход на внутреннее водоснабжение",
        "Перейти на внутреннее водоснабжение",
    )

    VALENTA_SYNCHRONIZATION: ActionDescription = ActionDescription(
        "VALENTA_SYNCHRONIZATION",
        ("valenta", "валента"),
        "Синхронизация Валенты",
        "Совершить синхронизацию для Валенты",
        False,
        True,
        forcable=True,
    )

    TIME_TRACKING_REPORT: ActionDescription = ActionDescription(
        "TIME_TRACKING_REPORT",
        ("tt", "урв"),
        "Отчеты по учёту рабочего времени",
        "Создать",
        False,
        False,
    )

    DOOR_OPEN: ActionDescription = ActionDescription(
        "DOOR_OPEN",
        ("door_open",),
        "Открытие дверей",
        "Открыть",
        False,
        False,
    )

    DOOR_CLOSE: ActionDescription = ActionDescription(
        "DOOR_CLOSE",
        ("door_close",),
        "Закрытие дверей",
        "Закрыть",
        False,
        False,
    )

    ATTACH_SHARED_DISKS: ActionDescription = ActionDescription(
        "ATTACH_SHARED_DISKS",
        ("attach",),
        "Присоединить сетевые диски",
        "Присоединить",
        False,
        True,
    )

    ACTION: ActionDescription = ActionDescription(
        "ACTION",
        ("action",),
        "Неспециализированное действие",
        None,
        False,
        True,
        forcable=False,
    )


class STATISTICS:
    class Types(Enum):
        CT: str = "CT"
        CT_DAY: str = "CT_DAY"
        CT_WEEK: str = "CT_WEEK"
        CT_MONTH: str = "CT_MONTH"
        CHILLER_FILTER: str = MATERIALIZED_RESOURCES.TYPES.CHILLER_FILTER.name
        MRI_COLDHEAD: str = "MRI_COLDHEAD"
        POLIBASE_DATABASE_DUMP: str = "POLIBASE_DATABASE_DUMP"
        POLIBASE_PERSON_REVIEW_NOTIFICATION: str = "POLIBASE_PERSON_REVIEW_NOTIFICATION"


class JournalType(tuple[int, OrderedNameCaptionDescription], Enum):
    TEST: tuple[int, OrderedNameCaptionDescription] = (
        0,
        OrderedNameCaptionDescription("test", "Тест"),
    )
    COMPUTER: tuple[int, OrderedNameCaptionDescription] = (
        1,
        OrderedNameCaptionDescription("computer", "Компьютер"),
    )
    MRI_CHILLER: tuple[int, OrderedNameCaptionDescription] = (
        2,
        OrderedNameCaptionDescription("mri_chiller", "Чиллер МРТ"),
    )
    MRI_GRADIENT_CHILLER: tuple[int, OrderedNameCaptionDescription] = (
        3,
        OrderedNameCaptionDescription("mri_gradient_chiller", "Чиллер градиентов МРТ"),
    )
    MRI_CLOSET_CHILLER: tuple[int, OrderedNameCaptionDescription] = (
        4,
        OrderedNameCaptionDescription("mri_closet_chiller", "Чиллер кабинета МРТ"),
    )
    CHILLER: tuple[int, OrderedNameCaptionDescription] = (
        5,
        OrderedNameCaptionDescription("chiller", "Чиллер"),
    )
    COMMUNICATION_ROOM: tuple[int, OrderedNameCaptionDescription] = (
        6,
        OrderedNameCaptionDescription("communication_room", "Коммутационная комната"),
    )
    SERVER_ROOM: tuple[int, OrderedNameCaptionDescription] = (
        7,
        OrderedNameCaptionDescription("server_room", "Серверная комната"),
    )
    MRI_TECHNICAL_ROOM: tuple[int, OrderedNameCaptionDescription] = (
        8,
        OrderedNameCaptionDescription("mri_technical_room", "Техническая комната МРТ"),
    )
    MRI_PROCEDURAL_ROOM: tuple[int, OrderedNameCaptionDescription] = (
        9,
        OrderedNameCaptionDescription("mri_procedural_room", "Процедурная комната МРТ"),
    )
    PRINTER: tuple[int, OrderedNameCaptionDescription] = (
        10,
        OrderedNameCaptionDescription("printer", "Принтер"),
    )
    SERVER: tuple[int, OrderedNameCaptionDescription] = (
        11,
        OrderedNameCaptionDescription("server", "Сервер"),
    )
    OUTSIDE_SERVER: tuple[int, OrderedNameCaptionDescription] = (
        12,
        OrderedNameCaptionDescription("outside_server", "Внешний сервер"),
    )
    AGREEMENT: tuple[int, OrderedNameCaptionDescription] = (
        13,
        OrderedNameCaptionDescription("agreement", "Договор и счет"),
    )
    XRAY: tuple[int, OrderedNameCaptionDescription] = (
        14,
        OrderedNameCaptionDescription("xray", "Рентген"),
    )
    CASH_REGISTER: tuple[int, OrderedNameCaptionDescription] = (
        15,
        OrderedNameCaptionDescription("cash_register", "Касса"),
    )


class Tags(tuple[int, IconedOrderedNameCaptionDescription], Enum):
    SERVICE: tuple[int, IconedOrderedNameCaptionDescription] = (
        1,
        IconedOrderedNameCaptionDescription(
            None, "Обслуживание", None, 4, CONST.VISUAL.GOOD
        ),
    )
    ERROR: tuple[int, IconedOrderedNameCaptionDescription] = (
        2,
        IconedOrderedNameCaptionDescription(
            None, "Ошибка", None, 2, CONST.VISUAL.ERROR
        ),
    )
    WARNING: tuple[int, IconedOrderedNameCaptionDescription] = (
        3,
        IconedOrderedNameCaptionDescription(
            None, "Внимание", None, 3, CONST.VISUAL.WARNING
        ),
    )
    NOTIFICATION: tuple[int, IconedOrderedNameCaptionDescription] = (
        4,
        IconedOrderedNameCaptionDescription(
            None, "Уведомление", None, 1, CONST.VISUAL.NOTIFICATION
        ),
    )
    TASK: tuple[int, IconedOrderedNameCaptionDescription] = (
        5,
        IconedOrderedNameCaptionDescription(
            None,
            "Задача",
            None,
            6,
            CONST.VISUAL.TASK,
        ),
    )
    INSPECTION: tuple[int, IconedOrderedNameCaptionDescription] = (
        6,
        IconedOrderedNameCaptionDescription(
            None,
            "Осмотр",
            None,
            5,
            CONST.VISUAL.EYE,
        ),
    )
    INFORMATION: tuple[int, IconedOrderedNameCaptionDescription] = (
        7,
        IconedOrderedNameCaptionDescription(
            None,
            "Информация",
            None,
            0,
            CONST.VISUAL.INFORMATION,
        ),
    )
