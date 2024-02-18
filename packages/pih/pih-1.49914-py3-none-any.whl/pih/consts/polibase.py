from enum import Enum, auto

from pih.tools import j
from pih.consts.file import FILE
from pih.const import BARCODE
from pih.collection import PolibaseDocumentDescription


class POLIBASE:
    NAME: str = "Polibase"
    SERVICE_NAME: str = "OracleServiceORCL"
    PROCESS_NAME: str = "Polibase ODAC"

    DBMS_OUTPUT: str = "dbms_output"

    DOCTEMPLETS_LAST_OPERATED_ID: str = "doctemplete_last_operated_id"

    PRERECORDING_PIN: int = 10
    PERSON_MINIMAL_PIN: int = 100
    RESERVED_TIME_A_PIN: int = 5
    RESERVED_TIME_B_PIN: int = 6
    RESERVED_TIME_C_PIN: int = 7
    EMPTY_VALUE: str = "xxxxx"
    EMPTY_EMAIL_VARIANTS: list[str] = ["нет", "-", "no"]
    ASK_EMAIL_LOCALY_VARIANTS: list[str] = ["!"]
    # ASK_EMAIL_REMOTELY_VARIANTS: list[str] = ["!!"]
    TELEPHONE_NUMBER_COUNT: int = 4

    CARD_REGISTRY_FOLDER_QR_CODE_COUNT: int = 2

    CARD_REGISTRY_FOLDER_NAME_CHECK_PATTERN: list[str] = ["п", "т"]

    # 145 - Средний Медицинский Персонал
    # 300 - Реанимация
    # 361 - Операционная блок
    # 421 - СМП
    # 221 -
    # 229 -
    CABINET_NUMBER_EXCLUDED_FROM_VISIT_RESULT: list[int] = [
        145,
        221,
        229,
        300,
        361,
        421,
    ]

    # 147 - УЗИ
    # 201 - ЭНДОСКОПИЯ
    # 202 - МРТ
    # 203 - КТ

    class AppointmentServiceGroupId(Enum):
        ULTRASOUND: int = 147
        ENDOSCOPY: int = 201
        MRI: int = 202
        CT: int = 203

    APPOINTMENT_SERVICE_GROUP_NAME: dict[Enum, str] = {
        AppointmentServiceGroupId.ULTRASOUND: "ультразвуковое исследование",
        AppointmentServiceGroupId.ENDOSCOPY: "эндоспопичекое исследование",
        AppointmentServiceGroupId.MRI: "МРТ исследование",
        AppointmentServiceGroupId.CT: "рентген исследование",
    }

    STATUS_EXCLUDE_FROM_VISIT_RESULT: list[int] = [63]

    ###

    TELEGRAM_BOT_URL: str = "https://t.me/pacifichospital_bot"

    REVIEW_ACTION_URL: str = "https://forms.gle/qriwujnAknYXga4eA"
    REVIEW_ACTION_URL_FOR_INPATIENT: str = "https://forms.gle/ULRFv4aujQQsrvFG7"

    PERSON_VISIT_NOTIFICATION_TEXT_CANCEL_OR_REPLACE_RECEPTION: str = "\nВ случае отмены или переноса записи обязательно свяжитесь с нами по номеру +7(423)2790790.\n С уважением, больница Пасифик Интернешнл Хоспитал."

    PERSON_VISIT_NOTIFICATION_HEADER: str = "_Здравствуйте, это *автоматическая* рассылка от Пасифик Интернешнл Хоспитал (Falck)._\n\n"

    SEND_TELEGRAM_BOT_TEXT: str = (
        "\n\nОтправляем ссылку на наш telegram-бот с *важной информацией* (подготовка к исследованиям, врачи, услуги, схема проезда и др.):\n"
        + TELEGRAM_BOT_URL
    )

    ASK_TO_SEND_TELEGRAM_BOT_URL_TEXT: str = "\n\nОтправьте в ответ любое сообщение и мы пришлём Вам ссылку на наш telegram-бот с *важной информацией* (подготовка к исследованиям, врачи, услуги, схема проезда и др.)"

    PERSON_VISIT_NOTIFICATION_APPOINTMENT_INFORMATION: str = "*{name}*, Вы записаны в Пасифик Интернешнл Хоспитал на {appointment_information}."

    HAVE_A_GOOD_DAY: str = "\n\nХорошего дня!"

    PERSON_VISIT_GREETING_NOTIFICATION_TEXT_BASE: str = (
        PERSON_VISIT_NOTIFICATION_HEADER
        + PERSON_VISIT_NOTIFICATION_APPOINTMENT_INFORMATION
    )

    PERSON_VISIT_GREETING_NOTIFICATION_TEXT_WITHOUT_TEXT: str = (
        PERSON_VISIT_GREETING_NOTIFICATION_TEXT_BASE + ASK_TO_SEND_TELEGRAM_BOT_URL_TEXT
    )

    PERSON_VISIT_GREETING_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION: str = (
        PERSON_VISIT_GREETING_NOTIFICATION_TEXT_BASE
    )

    PERSON_VISIT_NOTIFICATION_WITH_TIME_TEXT: str = (
        "\n\nВаш приём запланирован на {day_string} {month_string} в {hour_string}{minute_string}."
        + PERSON_VISIT_NOTIFICATION_TEXT_CANCEL_OR_REPLACE_RECEPTION
    )

    ###

    PERSON_REVIEW_NOTIFICATION_TEXT_BASE: str = "Добрый день, *{name}*!\n\nМеня зовут Анна, я директор отдела качества *Pacific International Hospital* (ранее Falck).\n\nВы недавно обращались в нашу больницу. Будем очень признательны, если в целях улучшения качества обслуживания вы ответите на несколько вопросов"

    SEND_REVIEW_ACTION_URL_TEXT: str = ", перейдя по ссылке ниже:\n" + REVIEW_ACTION_URL

    PERSON_REVIEW_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION: str = (
        PERSON_REVIEW_NOTIFICATION_TEXT_BASE + SEND_REVIEW_ACTION_URL_TEXT
    )

    ASK_TO_SEND_REVIEW_ACTION_TEXT: str = ". Согласны ли Вы пройти опрос?"

    PERSON_REVIEW_NOTIFICATION_TEXT: str = (
        PERSON_REVIEW_NOTIFICATION_TEXT_BASE + ASK_TO_SEND_REVIEW_ACTION_TEXT
    )

    YES_ANSWER: list[str] = [
        "да",
        "согласен",
        "согласна",
        "ok",
        "ок",
        "yes",
        "хорошо",
        "ага",
    ]

    NO_ANSWER: list[str] = ["нет", "не согласен", "не согласна", "no", "занят"]

    TAKE_TELEGRAM_BOT_URL_TEXT: str = "*{name}*, отправляем Вам ссылку:\n"

    PERSONLESS_TAKE_TELEGRAM_BOT_URL_TEXT: str = "Отправляем Вам ссылку:\n"

    TAKE_REVIEW_ACTION_URL_TEXT: str = (
        "*{name}*, отправляем Вам ссылку для прохождения опроса:"
    )

    DATE_FORMAT: str = "%d.%m.%Y"
    DATE_IS_NOT_SET_YEAR: int = 1899
    DATETIME_FORMAT: str = "dd.mm.yyyy hh24:mi:ss"

    DB_DATETIME_FORMAT: str = "%d-%m-%Y-%H-%M-00"

    class BARCODE:
        NOT_FOUND: str = "_@barcode_not_found@_"

        class PERSON:
            IMAGE_FORMAT: str = FILE.EXTENSION.JPEG

        class PERSON_CARD_REGISTRY_FOLDER:
            IMAGE_FORMAT: str = FILE.EXTENSION.PNG

        ACTUAL_FORMAT: str = BARCODE.CODE128
        OLD_FORMAT: str = BARCODE.I25

        SUPPORT_FORMATS: list[str] = [ACTUAL_FORMAT, OLD_FORMAT]

        NEW_PREFIX: str = "new_"

        @staticmethod
        def get_file_name(pin: int, with_extension: bool = False) -> str:
            extension: str = (
                j((".", POLIBASE.BARCODE.PERSON.IMAGE_FORMAT)) if with_extension else ""
            )
            return j((POLIBASE.BARCODE.NEW_PREFIX, str(pin), extension))

    POLIBASE_PERSON_REVIEW_NOTIFICATION_DOCTOR_PERSON_PIN_LIST: list[int] = [
        51087,
        24727,
        8846,
        104498,
        97967,
        12411,
        40903,
        1121,
        100669,
        2455,
        99537,
        1226,
        67558,
        12097,
        43476,
        12146,
        22142,
        4497,
        9207,
        102114,
        34388,
        5960,
        111110,
        118252,
        120547,
        120508,
        122658,
    ]

    BONUS_DOCTOR_PERSON_PIN_LIST: list[int] = [
        51087,
        24727,
        8846,
        104498,
        97967,
        12411,
        40903,
        1121,
        1226,
        67558,
        12097,
        43476,
        12146,
        22142,
        4497,
        102114,
        34388,
        5960,
        111110,
        118252,
        120508,
    ]

class PolibasePersonVisitStatus:
    CONFIRMED: int = 107
    CANCELED: int = 102
    
class PolibasePersonVisitNotificationType(Enum):
    GREETING: int = auto()
    REMINDER: int = auto()
    DEFAULT: int = auto()


"""
102 - отмена		
99 прошу перенести
101 - пришел			
102 - отказался	
103 - на приеме
104 - окончен
105 - не пришел	
106 - предварительно
107 - подверждено
108 - оказано
109 к оплате
"""



class PolibaseDocumentTypes(Enum):
    ABPM_JOURNAL: PolibaseDocumentDescription = PolibaseDocumentDescription(
        "Дневник суточного мониторинга АД", 70, 70, 80
    )
    HOLTER_JOURNAL: PolibaseDocumentDescription = PolibaseDocumentDescription(
        "Дневник суточного мониторинга ЭКГ", 70, 70, 80
    )
    PATIENT_CARD_AMBULATORY: PolibaseDocumentDescription = PolibaseDocumentDescription(
        "Медицинская карта\nпациента, получившего медицинскую помощь\nв амбулаторных условиях",
        70,
        120,
        120,
    )
    PROCESSING_PRESONAL_DATA_CONSENT: PolibaseDocumentDescription = (
        PolibaseDocumentDescription(
            "согласие\nпациента на обработку персональных данных",
            70,
            70,
            120,
            1,
        )
    )
    INFORMED_VOLUNTARY_MEDICAL_INVENTION_CONSENT: PolibaseDocumentDescription = (
        PolibaseDocumentDescription(
            "информированное добровольное согласие\nна медицинское вмешательство",
            70,
            70,
            120,
            1,
        )
    )
    INFORMED_VOLUNTARY_MEDICAL_INVENTION_CONSENT_SPECIFIC: PolibaseDocumentDescription = PolibaseDocumentDescription(
        "информированное добровольное согласие на виды медицинских\nвмешательств, включенные в перечень определенных видов\nмедицинских вмешательств, на которые граждане дают\nинформированное добровольное согласие при выборе врача и\nмедицинской организации для получения первичной медико-\nсанитарной помощи",
        70,
        70,
        280,
        2,
    )

    @staticmethod
    def sorted() -> list:
        return sorted(
            PolibaseDocumentTypes,
            key=lambda item: item.value.title_height,
            reverse=True,
        )
