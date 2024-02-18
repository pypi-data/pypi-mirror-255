from enum import Enum
from pih.collection import EventDescription, ParamItem
from pih.const import LogMessageChannels, LogMessageFlags
from pih.names import PARAM_ITEMS, FIELD_NAME_COLLECTION


class Events(Enum):
    DEBUG: EventDescription = EventDescription(
        "It is a debug event", LogMessageChannels.POLIBASE, LogMessageFlags.DEBUG.value
    )

    PRINTER_REPORT: EventDescription = EventDescription(
        "Принтер {printer_name} ({location}):\n {printer_report}",
        LogMessageChannels.PRINTER,
        LogMessageFlags.NORMAL,
        (
            ParamItem("printer_name", "Name of printer"),
            ParamItem("location", "Location"),
            ParamItem("printer_report", "Printer report"),
        ),
    )
    #
    ADD_JOURNAL_RECORD: EventDescription = EventDescription(
        "{tag_string}. {type_string}. {samAccountName} сделал запись в журнале. {title}: {text}.",
        LogMessageChannels.JOURNAL,
        (LogMessageFlags.NORMAL, LogMessageFlags.SAVE),
        (
            PARAM_ITEMS.TAG,
            PARAM_ITEMS.TYPE,
            PARAM_ITEMS.LOGIN,
            PARAM_ITEMS.TITLE,
            PARAM_ITEMS.TEXT,
            ParamItem("tag_string", "Tags string").configurate(saved=False),
            ParamItem("type_string", "Type string").configurate(saved=False),
            PARAM_ITEMS.PARAMETERS,
        ),
    )
    #
    LOG_IN: EventDescription = EventDescription(
        "Пользователь {} ({}) вошел с компьютера {}",
        LogMessageChannels.IT_BOT,
        LogMessageFlags.NORMAL,
        (
            PARAM_ITEMS.FULL_NAME,
            PARAM_ITEMS.LOGIN,
            ParamItem("computer_name", "Name of computer"),
        ),
    )

    SESSION_STARTED: EventDescription = EventDescription(
        "Пользователь {} ({}) начал пользоваться программой {}.\nВерсия: {}.\nНазвание компьютера: {}",
        LogMessageChannels.IT_BOT,
        LogMessageFlags.NORMAL,
        (
            PARAM_ITEMS.FULL_NAME,
            PARAM_ITEMS.LOGIN,
            ParamItem("app_name", "Name of user"),
            ParamItem("version", "Version"),
            ParamItem("computer_name", "Name of computer"),
        ),
    )

    SERVICE_WAS_STARTED: EventDescription = EventDescription(
        "Сервис {service_name} запущен!\nИмя хоста: {host_name}\nПорт: {port}\nИдентификатор процесса: {pid}\n",
        LogMessageChannels.SERVICES,
        LogMessageFlags.NORMAL,
        (
            PARAM_ITEMS.SERVICE_NAME,
            ParamItem("host_name", "Name of host"),
            ParamItem("port", "Port"),
            ParamItem("pid", "PID"),
            ParamItem("service_information", "Service information"),
        ),
    )

    SERVICE_WAS_STOPPED: EventDescription = EventDescription(
        "Сервис {service_name} остановлен!",
        LogMessageChannels.SERVICES,
        LogMessageFlags.NORMAL,
        (
            PARAM_ITEMS.SERVICE_NAME,
            ParamItem("service_information", "Service information"),
        ),
    )

    SERVICE_WAS_NOT_STARTED: EventDescription = EventDescription(
        "Сервис {service_name} не запущен!\nИмя хоста: {host_name}\nПорт: {port}\nОшибка:{error}",
        LogMessageChannels.SERVICES,
        LogMessageFlags.ERROR,
        (
            PARAM_ITEMS.SERVICE_NAME,
            ParamItem("host_name", "Name of host"),
            ParamItem("port", "Port"),
            ParamItem("error", "Error"),
            ParamItem("service_information", "Service information"),
        ),
    )

    SERVICE_IS_INACCESIBLE_AND_WILL_BE_RESTARTED: EventDescription = EventDescription(
        "Сервис {service_name} недоступен и будет перезапущен!",
        LogMessageChannels.SERVICES,
        LogMessageFlags.ERROR,
        (
            PARAM_ITEMS.SERVICE_NAME,
            ParamItem("service_information", "Service  information"),
        ),
    )

    WHATSAPP_MESSAGE_RECEIVED: EventDescription = EventDescription(
        "Получено сообщение",
        LogMessageChannels.POLIBASE,
        LogMessageFlags.SILENCE,
        (ParamItem("message", "Сообщение"),),
    )

    NEW_FILE_DETECTED: EventDescription = EventDescription(
        "Новый файл: {path}",
        LogMessageChannels.IT_BOT,
        LogMessageFlags.NORMAL,
        (PARAM_ITEMS.PATH,),
    )

    NEW_POLIBASE_DOCUMENT_DETECTED: EventDescription = EventDescription(
        lambda args: [
            "Новый документ Полибейс: {path}",
            "Обработанный документ Полибейс: {path}",
        ][args[PARAM_ITEMS.STATUS.name]],
        LogMessageChannels.POLIBASE_DOCUMENT,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE_ONCE),
        (
            PARAM_ITEMS.PERSON_PIN,
            PARAM_ITEMS.PATH.configurate(key=True),
            PARAM_ITEMS.DOCUMENT_NAME,
            PARAM_ITEMS.STATUS,
        ),
    )

    COMPUTER_WAS_STARTED: EventDescription = EventDescription(
        "Компьютер {name} загрузился",
        LogMessageChannels.IT,
        LogMessageFlags.NORMAL,
        (ParamItem("name", "Название компьютера"),),
    )

    SERVER_WAS_STARTED: EventDescription = EventDescription(
        "Сервер {name} загрузился",
        LogMessageChannels.IT,
        LogMessageFlags.NORMAL,
        (ParamItem("name", "Название сервера"),),
    )

    RESOURCE_INACCESSABLE: EventDescription = EventDescription(
        "Ресурс {resource_name} недоступен. {reason_string}",
        LogMessageChannels.RESOURCES,
        LogMessageFlags.ERROR,
        (
            ParamItem("resource_name", "Название ресурса"),
            ParamItem("resource", "Ресурс"),
            ParamItem("at_first_time", "Признак первого раза"),
            ParamItem("reason_string", "Строка причины"),
            ParamItem("reason", "Причины", optional=True),
        ),
    )

    RESOURCE_ACCESSABLE: EventDescription = EventDescription(
        "Ресурс {resource_name} доступен",
        LogMessageChannels.RESOURCES,
        LogMessageFlags.NORMAL,
        (
            ParamItem("resource_name", "Название ресурса"),
            ParamItem("resource", "Ресурс"),
            ParamItem("at_first_time", "Признак первого раза"),
        ),
    )

    #
    BACKUP_ROBOCOPY_JOB_WAS_STARTED: EventDescription = EventDescription(
        "Robocopy: Начато выполнение задания: {name}. PID процесса: {pid}",
        LogMessageChannels.BACKUP,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE_ONCE),
        (PARAM_ITEMS.NAME.configurate(key=True), PARAM_ITEMS.PID),
    )

    BACKUP_ROBOCOPY_JOB_WAS_COMPLETED: EventDescription = EventDescription(
        "Robocopy: Завершено выполнение задания: {name}. Статус: {status_string}",
        LogMessageChannels.BACKUP,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE),
        (PARAM_ITEMS.NAME, ParamItem("status_string", ""), PARAM_ITEMS.STATUS),
    )
    #
    POLIBASE_CREATION_DB_DUMP_START: EventDescription = EventDescription(
        "Базы данных Polibase: Начато создание дампа",
        LogMessageChannels.BACKUP,
        (LogMessageFlags.NORMAL, LogMessageFlags.SAVE),
    )

    POLIBASE_CREATION_DB_DUMP_COMPLETE: EventDescription = EventDescription(
        "Базы данных Polibase: Завершено создание дампа. Размер: {size}",
        LogMessageChannels.BACKUP,
        (LogMessageFlags.NORMAL, LogMessageFlags.SAVE),
        (ParamItem("size", ""),),
    )

    POLIBASE_CREATION_ARCHIVED_DB_DUMP_START: EventDescription = EventDescription(
        "Базы данных Polibase: Начато архивирование дампа",
        LogMessageChannels.BACKUP,
        LogMessageFlags.NORMAL,
    )

    POLIBASE_CREATION_ARCHIVED_DB_DUMP_COMPLETE: EventDescription = EventDescription(
        "Базы данных Polibase: Завершено архивирование дампа. Размер: {size}",
        LogMessageChannels.BACKUP,
        (LogMessageFlags.NORMAL, LogMessageFlags.SAVE),
        (ParamItem("size", ""),),
    )

    POLIBASE_COPING_ARCHIVED_DB_DUMP_START: EventDescription = EventDescription(
        "Базы данных Polibase: Начато копирование архивированного дампа на {}",
        LogMessageChannels.BACKUP,
        LogMessageFlags.NORMAL,
        (PARAM_ITEMS.DESTINATION,),
    )

    POLIBASE_COPING_ARCHIVED_DB_DUMP_COMPLETE: EventDescription = EventDescription(
        "Базы данных Polibase: Завершено копирование архивированного дампа на {}",
        LogMessageChannels.BACKUP,
        LogMessageFlags.NORMAL,
        (PARAM_ITEMS.DESTINATION,),
    )

    POLIBASE_COPING_DB_DUMP_START: EventDescription = EventDescription(
        "Базы данных Polibase: Начато копирование дампа на {}",
        LogMessageChannels.BACKUP,
        LogMessageFlags.NORMAL,
        (PARAM_ITEMS.DESTINATION,),
    )

    POLIBASE_COPING_DB_DUMP_COMPLETE: EventDescription = EventDescription(
        "Базы данных Polibase: Завершено копирование дампа на {}",
        LogMessageChannels.BACKUP,
        LogMessageFlags.NORMAL,
        (PARAM_ITEMS.DESTINATION,),
    )
    #
    HR_NOTIFY_ABOUT_NEW_EMPLOYEE: EventDescription = EventDescription(
        "День добрый, {hr_given_name}.\nДокументы для нового сотрудника: {employee_full_name} готовы!\nЕго корпоративная почта: {employee_email}.",
        LogMessageChannels.HR,
        LogMessageFlags.NOTIFICATION.value,
        (
            ParamItem("hr_given_name", "Имя руководителя отдела HR"),
            ParamItem("employee_full_name", "ФИО нового сотрудника"),
            ParamItem("employee_email", "Корпаротивная почта нового сотрудника"),
        ),
    )
    #
    IT_NOTIFY_ABOUT_CREATE_USER: EventDescription = EventDescription(
        "Добрый день, отдел Информационных технологий.\nДокументы для нового пользователя: {} готовы!\nОписание: {}\nЛогин: {}\nПароль: {}\nТелефон: {}\nЭлектронная почта: {}\nДополнительная информация: {}",
        LogMessageChannels.IT,
        LogMessageFlags.NOTIFICATION.value,
        (
            PARAM_ITEMS.NAME,
            PARAM_ITEMS.DESCRIPTION,
            PARAM_ITEMS.LOGIN,
            PARAM_ITEMS.PASSWORD,
            PARAM_ITEMS.TELEPHONE_NUMBER,
            PARAM_ITEMS.EMAIL,
            ParamItem("information", ""),
        ),
    )

    IT_NOTIFY_ABOUT_CREATE_PERSON: EventDescription = EventDescription(
        "Добрый день, отдел Информационных технологий.\nДокументы для новой персоны: {name} готовы!\nОписание: {description}\nЭлектронная почта: {email}\nПароль: {password}\nТелефон: {telephoneNumber}",
        LogMessageChannels.IT,
        LogMessageFlags.NOTIFICATION.value,
        (
            PARAM_ITEMS.NAME,
            PARAM_ITEMS.DESCRIPTION,
            PARAM_ITEMS.EMAIL,
            PARAM_ITEMS.PASSWORD,
            PARAM_ITEMS.TELEPHONE_NUMBER,
        ),
    )

    IT_NOTIFY_ABOUT_CREATE_MARK: EventDescription = EventDescription(
        "Добрый день, отдел Информационных технологий.\nКарта доступа для новой персоны: {name} готова!\nТелефон: {telephoneNumber}\nНомер карты доступа: {TabNumber}\nГруппа доступа: {group_name}",
        LogMessageChannels.IT,
        LogMessageFlags.NOTIFICATION.value,
        (
            PARAM_ITEMS.NAME,
            PARAM_ITEMS.TELEPHONE_NUMBER,
            PARAM_ITEMS.TAB_NUMBER,
            ParamItem("group_name", ""),
        ),
    )

    IT_NOTIFY_ABOUT_CREATE_TEMPORARY_MARK: EventDescription = EventDescription(
        "Добрый день, отдел Информационных технологий.\nВременная карта доступа для персоны: {name} готова!\nНомер карты: {TabNumber}\nТелефон: {telephoneNumber}",
        LogMessageChannels.IT,
        LogMessageFlags.NOTIFICATION.value,
        (PARAM_ITEMS.NAME, PARAM_ITEMS.TAB_NUMBER, PARAM_ITEMS.TELEPHONE_NUMBER),
    )

    IT_NOTIFY_ABOUT_TEMPORARY_MARK_RETURN: EventDescription = EventDescription(
        "Добрый день, отдел Информационных технологий.\nВременная карта доступа для персоны: {name} возвращена!\nНомер карты: {TabNumber}",
        LogMessageChannels.IT,
        LogMessageFlags.NOTIFICATION.value,
        (PARAM_ITEMS.NAME, PARAM_ITEMS.TAB_NUMBER),
    )

    IT_NOTIFY_ABOUT_MARK_RETURN: EventDescription = EventDescription(
        "Добрый день, отдел Информационных технологий.\nКарта доступа для персоны: {name} возвращена!\nНомер карты: {TabNumber}",
        LogMessageChannels.IT,
        LogMessageFlags.NOTIFICATION.value,
        (PARAM_ITEMS.NAME, PARAM_ITEMS.TAB_NUMBER),
    )

    IT_TASK_AFTER_CREATE_USER: EventDescription = EventDescription(
        "Добрый день, {it_user_name}.\nНеобходимо создать ящик электронной почту для пользователя: {name}\nАдресс электронной почты: {mail}\nПароль: {password}",
        LogMessageChannels.IT,
        LogMessageFlags.TASK.value,
        (
            ParamItem("it_user_name", ""),
            PARAM_ITEMS.NAME,
            ParamItem("mail", ""),
            PARAM_ITEMS.PASSWORD,
        ),
    )

    IT_TASK_AFTER_CREATE_PERSON: EventDescription = EventDescription(
        "Добрый день, {it_user_name}.\nНеобходимо создать ящик электронной почты почту для персоны: {name}\nАдресс электронной почты: {mail}\nПароль: {password}",
        LogMessageChannels.IT,
        LogMessageFlags.TASK.value,
        (
            ParamItem("it_user_name", ""),
            PARAM_ITEMS.NAME,
            ParamItem("mail", ""),
            PARAM_ITEMS.PASSWORD,
        ),
    )

    WATCHABLE_WORKSTATION_IS_NOT_ACCESSABLE: EventDescription = EventDescription(
        "Компьютер {} вне сети",
        LogMessageChannels.RESOURCES,
        LogMessageFlags.ERROR,
        (PARAM_ITEMS.NAME,),
    )

    WATCHABLE_WORKSTATION_IS_ACCESSABLE: EventDescription = EventDescription(
        "Компьютер {} в сети",
        LogMessageChannels.RESOURCES,
        LogMessageFlags.NORMAL,
        (PARAM_ITEMS.NAME,),
    )

    SERVER_IS_NOT_ACCESSABLE: EventDescription = EventDescription(
        "Сервер {} вне сети",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.ERROR, LogMessageFlags.SAVE_ONCE),
        (PARAM_ITEMS.NAME,),
    )

    SERVER_IS_ACCESSABLE: EventDescription = EventDescription(
        "Сервер {} в сети",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.NORMAL, LogMessageFlags.SAVE_ONCE),
        (PARAM_ITEMS.NAME,),
    )

    # INDICATION_DEVICES

    INDICATION_DEVICES_WAS_REGISTERED: EventDescription = EventDescription(
        "Устройство индикации: {} ({}) зарегистрировано. Адресс: {}",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE_ONCE),
        (
            PARAM_ITEMS.NAME.configurate(key=True),
            PARAM_ITEMS.DESCRIPTION,
            PARAM_ITEMS.IP_ADDRESS,
        ),
    )

    # MRI

    MRI_CHILLER_FILTER_WAS_CHANGED: EventDescription = EventDescription(
        "Фильтр водяного охлаждения МРТ был заменён. Количество оставшихся фильтров: {}",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE),
        (PARAM_ITEMS.COUNT,),
    )

    MRI_CHILLER_TEMPERATURE_ALERT_WAS_FIRED: EventDescription = EventDescription(
        "Превышена температура чиллера",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.ERROR, LogMessageFlags.SAVE),
    )

    MRI_CHILLER_TEMPERATURE_ALERT_WAS_RESOLVED: EventDescription = EventDescription(
        "Проблема повышенной температуры чиллера была решена",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE),
    )

    MRI_CHILLER_WAS_TURNED_OFF: EventDescription = EventDescription(
        "Чиллер был выключен",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE),
    )

    MRI_CHILLER_WAS_TURNED_ON: EventDescription = EventDescription(
        "Чиллер был включен",
        LogMessageChannels.RESOURCES,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SAVE),
    )

    # POLIBASE

    POLIBASE_PERSON_DUPLICATION_WAS_DETECTED: EventDescription(
        "Регистратор {registrator_person_name} создал персону {person_name} ({person_pin}), которая дублирует {duplicated_person_name} ({duplicated_person_pin})",
        LogMessageChannels.POLIBASE_ERROR,
        LogMessageFlags.SAVE,
        (
            ParamItem("person_name", ""),
            PARAM_ITEMS.PERSON_PIN,
            ParamItem("duplicated_person_name", ""),
            ParamItem("duplicated_person_pin", ""),
            ParamItem("registrator_person_name", ""),
        ),
    )

    POLIBASE_PERSON_VISIT_WAS_REGISTERED: EventDescription = EventDescription(
        "Зарегистрировано новое посещение: {name} ({type_string})",
        LogMessageChannels.POLIBASE,
        LogMessageFlags.NOTIFICATION,
        (PARAM_ITEMS.NAME, ParamItem("type_string", ""), ParamItem("visit", "")),
    )

    POLIBASE_PERSON_WAS_CREATED: EventDescription = EventDescription(
        "Создана полибейс персона: {name} ({pin})",
        LogMessageChannels.POLIBASE,
        LogMessageFlags.NOTIFICATION,
        (PARAM_ITEMS.NAME, PARAM_ITEMS.PIN, PARAM_ITEMS.VALUE),
    )

    MAIL_TO_POLIBASE_PERSON_WAS_SENT: EventDescription = EventDescription(
        "Почта с медицинской записью {id} была отправлена пациенту: {pin}",
        LogMessageChannels.POLIBASE,
        LogMessageFlags.NOTIFICATION,
        (PARAM_ITEMS.ID, PARAM_ITEMS.PIN),
    )

    POLIBASE_PERSON_WAS_UPDATED: EventDescription = EventDescription(
        "Обновлена полибейс персона: {name} ({pin})",
        LogMessageChannels.POLIBASE,
        LogMessageFlags.SILENCE,
        (PARAM_ITEMS.NAME, PARAM_ITEMS.PIN, PARAM_ITEMS.VALUE),
    )

    POLIBASE_PERSON_VISIT_NOTIFICATION_WAS_REGISTERED: EventDescription = (
        EventDescription(
            "Зарегистрировано новое уведомление о посещении: {name} ({type_string})",
            LogMessageChannels.POLIBASE,
            LogMessageFlags.SILENCE,
            (
                PARAM_ITEMS.NAME,
                ParamItem("type_string", ""),
                ParamItem("notification", ""),
            ),
        )
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_WAS_REGISTERED: EventDescription = (
        EventDescription(
            None,
            LogMessageChannels.POLIBASE,
            (LogMessageFlags.SAVE_ONCE, LogMessageFlags.SILENCE),
            (PARAM_ITEMS.PERSON_PIN.configurate(key=True), PARAM_ITEMS.INPATIENT),
        )
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION_WAS_ANSWERED: EventDescription = (
        EventDescription(
            "Пациент ({}) ответил на уведомление об отзыве: {}",
            LogMessageChannels.POLIBASE,
            LogMessageFlags.SAVE_ONCE,
            (PARAM_ITEMS.PERSON_PIN.configurate(key=True), PARAM_ITEMS.STATUS),
        )
    )

    POLIBASE_PERSONS_WITH_OLD_FORMAT_BARCODE_WAS_DETECTED: EventDescription = EventDescription(
        "Полибейс: обнаружены пациенты со старым форматом или отсутствующим штрих-кодом",
        LogMessageChannels.POLIBASE,
        LogMessageFlags.SILENCE,
        (PARAM_ITEMS.PERSON_PIN,),
    )

    POLIBASE_PERSON_BARCODES_WITH_OLD_FORMAT_WERE_CREATED: EventDescription = (
        EventDescription(
            "Полибейс: все новые штрих-коды созданы",
            LogMessageChannels.POLIBASE,
            LogMessageFlags.SILENCE,
            (PARAM_ITEMS.PERSON_PIN,),
        )
    )

    POLIBASE_PERSON_WITH_INACCESSABLE_EMAIL_WAS_DETECTED: EventDescription = EventDescription(
        "Пациент {} ({}) имеет недоступную электронную почту: {}. Регистратор: {}, компьютер: {} ({})",
        LogMessageChannels.POLIBASE_ERROR,
        LogMessageFlags.SAVE,
        (
            PARAM_ITEMS.PERSON_NAME,
            PARAM_ITEMS.PERSON_PIN,
            PARAM_ITEMS.EMAIL,
            PARAM_ITEMS.REGISTRATOR_PERSON_NAME,
            ParamItem(FIELD_NAME_COLLECTION.WORKSTATION_NAME, ""),
            ParamItem(FIELD_NAME_COLLECTION.WORKSTATION_DESCRIPTION, ""),
        ),
    )

    POLIBASE_PERSON_EMAIL_WAS_ADDED: EventDescription = EventDescription(
        "Электронная почта пациента {} ({}): {} была добавлена",
        LogMessageChannels.POLIBASE,
        (LogMessageFlags.RESULT, LogMessageFlags.SAVE),
        (
            PARAM_ITEMS.PERSON_NAME,
            PARAM_ITEMS.PERSON_PIN,
            PARAM_ITEMS.EMAIL,
        ),
    )

    ASK_FOR_POLIBASE_PERSON_EMAIL: EventDescription = EventDescription(
        "Запрос электронной почта у пациента {} ({}). Локально: {}",
        LogMessageChannels.POLIBASE,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SEND_ONCE),
        (
            PARAM_ITEMS.PERSON_NAME.configurate(saved=False),
            PARAM_ITEMS.PERSON_PIN.configurate(key=True),
            PARAM_ITEMS.LOCALY,
            PARAM_ITEMS.SECRET.configurate(visible=False),
        ),
    )

    POLIBASE_PERSON_BONUSES_WAS_UPDATED: EventDescription = EventDescription(
        "Бонусы пациента {} обновились",
        LogMessageChannels.POLIBASE,
        (LogMessageFlags.NOTIFICATION, LogMessageFlags.SILENCE),
        (PARAM_ITEMS.PERSON_PIN,),
    )

    ACTION_WAS_DONE: EventDescription = EventDescription(
        'Совершено действие "{}"➜{}.\nДействие совершил: {} ({}).\nПараметры действия: {}.\nПринудительное действие: {}.',
        LogMessageChannels.IT_BOT,
        LogMessageFlags.SAVE,
        (
            ParamItem(FIELD_NAME_COLLECTION.ACTION_DESCRIPTION, ""),
            ParamItem(FIELD_NAME_COLLECTION.ACTION_NAME, ""),
            PARAM_ITEMS.NAME,
            PARAM_ITEMS.LOGIN,
            PARAM_ITEMS.PARAMETERS,
            ParamItem(FIELD_NAME_COLLECTION.FORCED, ""),
        ),
    )

    ACTION_HAVE_TO_BE_DONE: EventDescription = EventDescription(
        "Необходимо совершить действие {}: {}",
        LogMessageChannels.DEBUG,
        LogMessageFlags.SAVE,
        (
            ParamItem(FIELD_NAME_COLLECTION.ACTION_NAME, ""),
            ParamItem(FIELD_NAME_COLLECTION.ACTION_DESCRIPTION, ""),
        ),
    )

    NEW_EMAIL_MESSAGE_WAS_RECEIVED: EventDescription = EventDescription(
        "Почтовый ящик: {mailbox}\nНовое письмо было получено от {from}: {title}.",
        LogMessageChannels.NEW_EMAIL,
        LogMessageFlags.NOTIFICATION,
        (
            ParamItem("mailbox", ""),
            PARAM_ITEMS.TITLE,
            ParamItem("from", ""),
            PARAM_ITEMS.VALUE,
        ),
    )

    CARD_REGISTRY_FOLDER_WAS_SET_FOR_POLIBASE_PERSON: EventDescription = (
        EventDescription(
            'Карта пациента: {} добавлена в папку "{}".\nДействие совершил: {} ({})',
            LogMessageChannels.CARD_REGISTRY,
            LogMessageFlags.SAVE_ONCE,
            (
                PARAM_ITEMS.PERSON_PIN.configurate(key=True),
                PARAM_ITEMS.CARD_REGISTRY_FOLDER,
                PARAM_ITEMS.REGISTRATOR_PERSON_NAME,
                PARAM_ITEMS.REGISTRATOR_PERSON_PIN,
            ),
        )
    )

    CARD_REGISTRY_FOLDER_WAS_SET_NOT_FROM_POLIBASE_FOR_POLIBASE_PERSON: EventDescription = EventDescription(
        "Карта пациента: {} добавлена не с помощью Полибейс",
        LogMessageChannels.CARD_REGISTRY,
        LogMessageFlags.SAVE_ONCE,
        (PARAM_ITEMS.PERSON_PIN,),
    )

    CARD_REGISTRY_SUITABLE_FOLDER_WAS_SET_FOR_POLIBASE_PERSON: EventDescription = EventDescription(
        'Карта пациента: {} добавлена в подходящую папку "{}".\nДействие совершил: {} ({})',
        LogMessageChannels.CARD_REGISTRY,
        LogMessageFlags.NOTIFICATION,
        (
            PARAM_ITEMS.PERSON_PIN,
            PARAM_ITEMS.CARD_REGISTRY_FOLDER,
            PARAM_ITEMS.REGISTRATOR_PERSON_NAME,
            PARAM_ITEMS.REGISTRATOR_PERSON_PIN,
        ),
    )

    CARD_REGISTRY_FOLDER_WAS_REGISTERED: EventDescription = EventDescription(
        "Папка с картами пациентов: {} добавлена в реестр карт пациентов. Положение: шкаф: {}; полка: {}; место на полке: {}",
        LogMessageChannels.CARD_REGISTRY,
        LogMessageFlags.SAVE_ONCE,
        (
            PARAM_ITEMS.CARD_REGISTRY_FOLDER.configurate(key=True),
            ParamItem("p_a", ""),
            ParamItem("p_b", ""),
            ParamItem("p_c", ""),
        ),
    )

    CARD_REGISTRY_FOLDER_START_CARD_SORTING: EventDescription = EventDescription(
        'Начат процесс сортировки карта пациентов в папке реестра карт "{}"',
        LogMessageChannels.CARD_REGISTRY,
        LogMessageFlags.SAVE,
        (PARAM_ITEMS.CARD_REGISTRY_FOLDER,),
    )

    CARD_REGISTRY_FOLDER_COMPLETE_CARD_SORTING: EventDescription = EventDescription(
        'Закончен процесс сортировки карта пациентов в папке реестра карт "{}"',
        LogMessageChannels.CARD_REGISTRY,
        LogMessageFlags.SAVE,
        (PARAM_ITEMS.CARD_REGISTRY_FOLDER,),
    )

    EMPLOYEE_CHECKED_IN: EventDescription = EventDescription(
        "Сотрудник {} отметился на приход",
        LogMessageChannels.TIME_TRACKING,
        LogMessageFlags.NOTIFICATION,
        (PARAM_ITEMS.NAME,),
    )

    EMPLOYEE_CHECKED_OUT: EventDescription = EventDescription(
        "Сотрудник {} отметился на выход",
        LogMessageChannels.TIME_TRACKING,
        LogMessageFlags.NOTIFICATION,
        (PARAM_ITEMS.NAME,),
    )

    RESULT_WAS_RETURNED: EventDescription = EventDescription(
        "Возврат результата из мобильного помощника",
        LogMessageChannels.IT_BOT,
        LogMessageFlags.SILENCE,
        (
            ParamItem("key", "Ключ"),
            PARAM_ITEMS.VALUE,
            ParamItem("interaption_type", "Занчение прерывания", optional=True),
        ),
    )

    SAVE_FILE_FROM_KNOWLEDGE_BASE: EventDescription = EventDescription(
        "Сохранение файла из базы знаний (Мобильные файл)",
        LogMessageChannels.IT_BOT,
        LogMessageFlags.SILENCE,
        (
            PARAM_ITEMS.ID.configurate(key=True),
            PARAM_ITEMS.TITLE,
            PARAM_ITEMS.TEXT,
        ),
    )

    SAVE_NOTE_FROM_KNOWLEDGE_BASE: EventDescription = EventDescription(
        "Сохранение заметки из базы знаний (Мобильные заметки)",
        LogMessageChannels.IT_BOT,
        LogMessageFlags.SILENCE,
        (
            PARAM_ITEMS.ID.configurate(key=True),
            PARAM_ITEMS.TITLE,
            PARAM_ITEMS.TEXT,
            PARAM_ITEMS.IMAGES,
        ),
    )
