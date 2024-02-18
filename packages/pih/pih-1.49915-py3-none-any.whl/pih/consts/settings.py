from enum import Enum
from pih.consts.polibase import POLIBASE
from pih.collection import (
    StorageVariableHolder,
    IntStorageVariableHolder,
    BoolStorageVariableHolder,
    TimeStorageVariableHolder,
    DateListStorageVariableHolder,
    FloatStorageVariableHolder,
    IntListStorageVariableHolder,
)


class SETTINGS(Enum):
    REVIEW_ACTION_URL: StorageVariableHolder = StorageVariableHolder(
        "REVIEW_ACTION_URL",
        POLIBASE.REVIEW_ACTION_URL,
    )

    REVIEW_ACTION_URL_FOR_INPATIENT: StorageVariableHolder = StorageVariableHolder(
        "REVIEW_ACTION_URL_FOR_INPATIENT",
        POLIBASE.REVIEW_ACTION_URL_FOR_INPATIENT,
    )

    USER_RESPONSIBLE_FOR_PATIENT_MARK: StorageVariableHolder = StorageVariableHolder(
        "USER_RESPONSIBLE_FOR_PATIENT_MARK",
        "baa",
    )

    WIFI_VIP_PASSWORD: StorageVariableHolder = StorageVariableHolder(
        "WIFI_VIP_PASSWORD", "ilovepacific"
    )

    PLAIN_FORMAT_AS_DEFAULT_LOGIN_LIST: StorageVariableHolder = StorageVariableHolder(
        "PLAIN_FORMAT_AS_DEFAULT_LOGIN_LIST", ["bar", "rob", "ptyu"]
    )

    CHILLER_RECOGNIZE_LOG_LEVEL: IntStorageVariableHolder = IntStorageVariableHolder(
        "CHILLER_RECOGNIZE_LOG_LEVEL", 0
    )

    HEART_BEAT_IS_ON: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "HEART_BEAT_IS_ON", True
    )

    CT_INDICATIONS_VALUE_TEMPERATURE_CORRECTION: IntStorageVariableHolder = (
        IntStorageVariableHolder("CT_INDICATIONS_VALUE_TEMPERATURE_CORRECTION", 0.7)
    )
    CT_INDICATIONS_VALUE_SAVE_PERIOD_IN_MINUTES: IntStorageVariableHolder = (
        IntStorageVariableHolder("CT_INDICATIONS_VALUE_SAVE_PERIOD_IN_MINUTES", 60)
    )

    CHILLER_INDICATIONS_VALUE_SAVE_PERIOD_IN_MINUTES: IntStorageVariableHolder = (
        IntStorageVariableHolder("CHILLER_INDICATIONS_VALUE_SAVE_PERIOD_IN_MINUTES", 60)
    )

    HOSPITAL_WORK_DAY_START_TIME: TimeStorageVariableHolder = TimeStorageVariableHolder(
        "HOSPITAL_WORK_DAY_START_TIME", "8:00"
    )
    HOSPITAL_WORK_DAY_END_TIME: TimeStorageVariableHolder = TimeStorageVariableHolder(
        "HOSPITAL_WORK_DAY_END_TIME", "20:00"
    )
    OFFICE_WORK_DAY_START_TIME: TimeStorageVariableHolder = TimeStorageVariableHolder(
        "OFFICE_WORK_DAY_START_TIME", "8:30"
    )
    OFFICE_WORK_DAY_END_TIME: TimeStorageVariableHolder = TimeStorageVariableHolder(
        "OFFICE_WORK_DAY_END_TIME", "17:00"
    )

    INDICATION_CT_NOTIFICATION_START_TIME: DateListStorageVariableHolder = (
        DateListStorageVariableHolder(
            "INDICATION_CT_NOTIFICATION_START_TIME", ["8:00", "12:00", "15:00", "17:00"]
        )
    )

    USER_USE_CACHE: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "USER_USE_CACHE", True
    )

    POLIBASE_PERSON_INFORMATION_QUEST_IS_ON: BoolStorageVariableHolder = (
        BoolStorageVariableHolder("POLIBASE_PERSON_INFORMATION_QUEST_IS_ON", False)
    )
    #
    POLIBASE_PERSON_REVIEW_NOTIFICATION_IS_ON: BoolStorageVariableHolder = (
        BoolStorageVariableHolder("POLIBASE_PERSON_REVIEW_NOTIFICATION_IS_ON", True)
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_ASK_WITHOUT_CHECK_FOR_CONFIRMATION: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "POLIBASE_PERSON_REVIEW_NOTIFICATION_ASK_WITHOUT_CHECK_FOR_CONFIRMATION", True
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_DAY_DELTA: StorageVariableHolder = (
        StorageVariableHolder("POLIBASE_PERSON_REVIEW_NOTIFICATION_DAY_DELTA", 0)
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_REVIEW_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION",
        POLIBASE.PERSON_REVIEW_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION,
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_TEXT: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_REVIEW_NOTIFICATION_TEXT",
            POLIBASE.PERSON_REVIEW_NOTIFICATION_TEXT,
        )
    )

    TIME_TRACKING_FOR_POLYCLINIC: StorageVariableHolder = StorageVariableHolder(
        "TIME_TRACKING_FOR_POLYCLINIC",
        [
            "190",
            "035",
            "058",
            "064",
            "101-0-",
            "125",
            "131",
            "134",
            "139",
            "156",
            "177",
            "199",
            "124",
            "183",
        ],
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_START_TIME: TimeStorageVariableHolder = (
        TimeStorageVariableHolder(
            "POLIBASE_PERSON_REVIEW_NOTIFICATION_START_TIME", "23:00"
        )
    )
    #
    RESOURCE_MANAGER_CHECK_SITE_CERTIFICATE_START_TIME: TimeStorageVariableHolder = (
        TimeStorageVariableHolder(
            "RESOURCE_MANAGER_CHECK_SITE_CERTIFICATE_START_TIME", "8:00"
        )
    )
    #
    POLIBASE_CREATION_DB_DUMP_START_TIME: TimeStorageVariableHolder = (
        TimeStorageVariableHolder("POLIBASE_CREATION_DB_DUMP_START_TIME", "20:30")
    )
    #
    RESOURCE_MANAGER_CHECK_SITE_FREE_SPACE_PERIOD_IN_MINUTES: IntStorageVariableHolder = IntStorageVariableHolder(
        "RESOURCE_MANAGER_CHECK_SITE_FREE_SPACE_PERIOD_IN_MINUTES", 15
    )
    #
    PRINTER_REPORT_PERIOD_IN_MINUTES: IntStorageVariableHolder = (
        IntStorageVariableHolder("PRINTER_REPORT_PERIOD_IN_MINUTES", 5)
    )
    #
    POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT_WITHOUT_DATE_FOR_CONFIRMED_NOTIFICATION: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT_WITHOUT_DATE_FOR_CONFIRMED_NOTIFICATION",
        POLIBASE.PERSON_VISIT_GREETING_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION
        + POLIBASE.SEND_TELEGRAM_BOT_TEXT,
    )

    POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT_WITHOUT_DATE: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT_WITHOUT_DATE",
        POLIBASE.PERSON_VISIT_GREETING_NOTIFICATION_TEXT_WITHOUT_TEXT,
    )

    POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION",
        POLIBASE.PERSON_VISIT_GREETING_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION
        + POLIBASE.PERSON_VISIT_NOTIFICATION_WITH_TIME_TEXT
        + POLIBASE.SEND_TELEGRAM_BOT_TEXT
        + POLIBASE.HAVE_A_GOOD_DAY,
    )

    POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_VISIT_GREETING_NOTIFICATION_TEXT",
            POLIBASE.PERSON_VISIT_GREETING_NOTIFICATION_TEXT_BASE
            + POLIBASE.PERSON_VISIT_NOTIFICATION_WITH_TIME_TEXT
            + POLIBASE.ASK_TO_SEND_TELEGRAM_BOT_URL_TEXT
            + POLIBASE.HAVE_A_GOOD_DAY,
        )
    )

    PERSON_VISIT_NOTIFICATION_HEADER: StorageVariableHolder = StorageVariableHolder(
        "PERSON_VISIT_NOTIFICATION_HEADER",
        POLIBASE.PERSON_VISIT_NOTIFICATION_HEADER,
    )

    POLIBASE_PERSON_VISIT_NOTIFICATION_TEXT: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_VISIT_NOTIFICATION_TEXT",
            POLIBASE.PERSON_VISIT_NOTIFICATION_HEADER
            + POLIBASE.PERSON_VISIT_NOTIFICATION_APPOINTMENT_INFORMATION
            + POLIBASE.PERSON_VISIT_NOTIFICATION_WITH_TIME_TEXT
            + POLIBASE.HAVE_A_GOOD_DAY,
        )
    )

    POLIBASE_PERSON_VISIT_REMINDER_TEXT: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_VISIT_REMINDER_TEXT",
        POLIBASE.PERSON_VISIT_NOTIFICATION_HEADER
        + "*{name}*, напоминаем Вам о записи сегодня {visit_time}. Вы записаны на {appointment_information}."
        + POLIBASE.PERSON_VISIT_NOTIFICATION_TEXT_CANCEL_OR_REPLACE_RECEPTION
        + POLIBASE.HAVE_A_GOOD_DAY,
    )

    POLIBASE_PERSON_TAKE_TELEGRAM_BOT_URL_TEXT: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_TAKE_TELEGRAM_BOT_URL_TEXT",
            POLIBASE.TAKE_TELEGRAM_BOT_URL_TEXT,
        )
    )

    POLIBASE_PERSON_TAKE_REVIEW_ACTION_URL_TEXT: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_TAKE_REVIEW_ACTION_URL_TEXT",
            POLIBASE.TAKE_REVIEW_ACTION_URL_TEXT,
        )
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_DOCTOR_PERSON_PIN_LIST: IntListStorageVariableHolder = IntListStorageVariableHolder(
        "POLIBASE_PERSON_REVIEW_NOTIFICATION_DOCTOR_PERSON_PIN_LIST",
        POLIBASE.POLIBASE_PERSON_REVIEW_NOTIFICATION_DOCTOR_PERSON_PIN_LIST,
    )

    BONUS_DOCTOR_PERSON_PIN_LIST: IntListStorageVariableHolder = (
        IntListStorageVariableHolder(
            "BONUS_DOCTOR_PERSON_PIN_LIST",
            POLIBASE.BONUS_DOCTOR_PERSON_PIN_LIST,
        )
    )

    POLIBASE_DOCTEMPLATE_THRESHOLD: IntStorageVariableHolder = IntStorageVariableHolder(
        "POLIBASE_DOCTEMPLATE_THRESHOLD", 100
    )

    POLIBASE_PERSON_YES_ANSWER_VARIANTS: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_YES_ANSWER_VARIANTS", POLIBASE.YES_ANSWER
    )

    POLIBASE_PERSON_NO_ANSWER_VARIANTS: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_NO_ANSWER_VARIANTS", POLIBASE.NO_ANSWER
    )

    POLIBASE_PERSON_NO_ANSWER_ON_NOTIFICATION_CONFIRMATION_TEXT: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_PERSON_NO_ANSWER_ON_NOTIFICATION_CONFIRMATION_TEXT",
        "Хорошего дня",
    )

    POLIBASE_PERSON_REVIEW_QUEST_WAIT_TIME: IntStorageVariableHolder = (
        IntStorageVariableHolder("POLIBASE_PERSON_REVIEW_QUEST_WAIT_TIME", 15)
    )

    POLIBASE_PERSON_VISIT_NEED_REGISTER_GREETING_NOTIFICATION: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "POLIBASE_PERSON_VISIT_NEED_REGISTER_GREETING_NOTIFICATION", True
    )

    POLIBASE_PERSON_VISIT_NEED_REGISTER_REMINDER_NOTIFICATION: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "POLIBASE_PERSON_VISIT_NEED_REGISTER_REMINDER_NOTIFICATION", True
    )

    POLIBASE_PERSON_VISIT_TIME_BEFORE_REMINDER_NOTIFICATION_IN_MINUTES: IntStorageVariableHolder = IntStorageVariableHolder(
        "POLIBASE_PERSON_VISIT_TIME_BEFORE_REMINDER_NOTIFICATION_IN_MINUTES", 120
    )

    POLIBASE_PERSON_VISIT_NOTIFICATION_TEST_TELEPHONE_NUMBER: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_VISIT_NOTIFICATION_TEST_TELEPHONE_NUMBER", None
        )
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_TEST_TELEPHONE_NUMBER: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_PERSON_REVIEW_NOTIFICATION_TEST_TELEPHONE_NUMBER", None
        )
    )

    WHATSAPP_SENDING_MESSAGES_VIA_WAPPI_IS_ON: BoolStorageVariableHolder = (
        BoolStorageVariableHolder("WHATSAPP_SENDING_MESSAGES_VIA_WAPPI_IS_ON", True)
    )

    WHATSAPP_BUFFERED_MESSAGE_MIN_DELAY_IN_MILLISECONDS: IntStorageVariableHolder = (
        IntStorageVariableHolder(
            "WHATSAPP_BUFFERED_MESSAGE_MIN_DELAY_IN_MILLISECONDS", 6000
        )
    )

    WHATSAPP_BUFFERED_MESSAGE_MAX_DELAY_IN_MILLISECONDS: IntStorageVariableHolder = (
        IntStorageVariableHolder(
            "WHATSAPP_BUFFERED_MESSAGE_MAX_DELAY_IN_MILLISECONDS", 12000
        )
    )

    WHATSAPP_MESSAGE_SENDER_USER_LOGIN: StorageVariableHolder = StorageVariableHolder(
        "WHATSAPP_MESSAGE_SENDER_USER_LOGIN", "Administrator"
    )

    POLIBASE_WAS_EMERGENCY_CLOSED_NOTIFICATION_TEXT: StorageVariableHolder = StorageVariableHolder(
        "POLIBASE_WAS_EMERGENCY_CLOSED_NOTIFICATION_TEXT",
        "к сожалениию наш Полибейс поломался и был аварийно закрыт, ожидайте сообщение о просьбе переоткрыть его!",
    )

    POLIBASE_WAS_RESTARTED_NOTIFICATION_TEXT: StorageVariableHolder = (
        StorageVariableHolder(
            "POLIBASE_WAS_RESTARTED_NOTIFICATION_TEXT",
            "Полибейс перезагружен, можете переоткрыть его.",
        )
    )

    WORKSTATION_SHUTDOWN_TIME: TimeStorageVariableHolder = TimeStorageVariableHolder(
        "WORKSTATION_SHUTDOWN_TIME", "21:00"
    )

    WORKSTATION_REBOOT_TIME: TimeStorageVariableHolder = TimeStorageVariableHolder(
        "WORKSTATION_REBOOT_TIME", "21:00"
    )

    EMAIL_VALIDATION_IS_ON: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "EMAIL_VALIDATION_IS_ON", True
    )
    EMAIL_VALIDATION_TEST: BoolStorageVariableHolder = BoolStorageVariableHolder(
        "EMAIL_VALIDATION_TEST", False
    )

    CHILLER_ALERT_TEMPERATURE: FloatStorageVariableHolder = FloatStorageVariableHolder(
        "CHILLER_ALERT_TEMPERATURE", 17.0
    )

    CHILLER_COUNT_DEFAULT: FloatStorageVariableHolder = FloatStorageVariableHolder(
        "CHILLER_COUNT_DEFAULT", 3
    )

    CHILLER_MAX_TEMPERATURE: IntStorageVariableHolder = IntStorageVariableHolder(
        "CHILLER_MAX_TEMPERATURE", 17
    )

    CHILLER_MIN_TEMPERATURE: IntStorageVariableHolder = IntStorageVariableHolder(
        "CHILLER_MIN_TEMPERATURE", 10
    )

    CHILLER_ACTION_MAX_TEMPERATURE: IntStorageVariableHolder = IntStorageVariableHolder(
        "CHILLER_ACTION_MAX_TEMPERATURE", 15
    )

    CHILLER_ACTION_MIN_TEMPERATURE: IntStorageVariableHolder = IntStorageVariableHolder(
        "CHILLER_ACTION_MIN_TEMPERATURE", 12
    )

    CT_ROOM_MAX_TEMPERATURE: IntStorageVariableHolder = IntStorageVariableHolder(
        "CT_ROOM_MAX_TEMPERATURE", 24
    )

    CT_ROOM_MIN_TEMPERATURE: IntStorageVariableHolder = IntStorageVariableHolder(
        "CT_ROOM_MIN_TEMPERATURE", 20
    )

    CT_ROOM_MAX_HUMIDITY: IntStorageVariableHolder = IntStorageVariableHolder(
        "CT_ROOM_MAX_HUMIDITY", 60
    )

    CT_ROOM_MIN_HUMIDITY: IntStorageVariableHolder = IntStorageVariableHolder(
        "CT_ROOM_MIN_HUMIDITY", 30
    )
    
    CHECK_ALL_RECIPIENT_USER_LOGIN: StorageVariableHolder = StorageVariableHolder(
        "CHECK_ALL_RECIPIENT_USER_LOGIN", "nak"
    )

