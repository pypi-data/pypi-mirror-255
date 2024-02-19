from enum import Enum
from pih.consts import LINK
from pih.consts.rpc import RPC
from pih.consts.hosts import HOSTS
from pih.consts.service_commands import ServiceCommands
from pih.collections.service import ServiceDescription


POLIBASE_BASE: ServiceDescription = ServiceDescription(
    host=HOSTS.POLIBASE.NAME,
    pyton_executor_path=r"C:\Users\adm\AppData\Local\Programs\Python\Python310\python.exe",
    run_from_system_account=True,
)

class ServiceRoles(Enum):

    SERVICE_ADMIN: ServiceDescription = ServiceDescription(
        name="ServiceAdmin",
        description="Service admin",
        host=HOSTS.DC1.NAME,
        port=RPC.PORT(20),
        host_changeable=False,
        commands=[
            ServiceCommands.on_service_starts,
            ServiceCommands.on_service_stops,
            ServiceCommands.get_service_information_table,
            ServiceCommands.heart_beat,
        ],
    )

    EVENT_AND_LOG: ServiceDescription = ServiceDescription(
        name="EventAndLog",
        description="Log and Event service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[ServiceCommands.send_log_message, ServiceCommands.send_event],
    )

    DS: ServiceDescription = ServiceDescription(
        name="DataSource",
        description="Data storage and source service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[
            ServiceCommands.register_polibase_person_information_quest,
            ServiceCommands.search_polibase_person_information_quests,
            ServiceCommands.update_polibase_person_information_quest,
            #
            ServiceCommands.update_polibase_person_visit_to_data_stogare,
            ServiceCommands.search_polibase_person_visits_in_data_storage,
            #
            ServiceCommands.register_polibase_person_visit_notification,
            ServiceCommands.search_polibase_person_visit_notifications,
            #
            ServiceCommands.register_delayed_message,
            ServiceCommands.search_delayed_messages,
            ServiceCommands.update_delayed_message,
            #
            ServiceCommands.get_settings_value,
            ServiceCommands.set_settings_value,
            #
            ServiceCommands.search_polibase_person_notification_confirmation,
            ServiceCommands.update_polibase_person_notification_confirmation,
            #
            ServiceCommands.get_storage_value,
            ServiceCommands.set_storage_value,
            #
            ServiceCommands.get_ogrn_value,
            ServiceCommands.get_fms_unit_name,
            #
            ServiceCommands.register_chiller_indications_value,
            ServiceCommands.register_ct_indications_value,
            ServiceCommands.get_last_ct_indications_value_container_list,
            ServiceCommands.get_last_сhiller_indications_value_container_list,
            #
            ServiceCommands.get_gkeep_item_list_by_any,
            ServiceCommands.add_gkeep_item,
            #
            ServiceCommands.register_event,
            ServiceCommands.get_event,
            ServiceCommands.remove_event,
            #
            ServiceCommands.execute_data_source_query,
            ServiceCommands.joke,
            ServiceCommands.get_event_count,
        ],
        standalone_name="ds",
        version="1.1"
    )

    AD: ServiceDescription = ServiceDescription(
        name="ActiveDirectory",
        description="Active directory service",
        host=HOSTS.DC2.NAME,
        commands=[
            ServiceCommands.authenticate,
            ServiceCommands.check_user_exists_by_login,
            ServiceCommands.get_user_by_full_name,
            ServiceCommands.get_users_by_name,
            ServiceCommands.get_user_by_login,
            ServiceCommands.get_user_by_telephone_number,
            ServiceCommands.get_template_users,
            ServiceCommands.get_containers,
            ServiceCommands.get_user_list_by_job_position,
            ServiceCommands.get_user_list_by_group,
            ServiceCommands.get_printer_list,
            ServiceCommands.get_computer_list,
            ServiceCommands.get_computer_description_list,
            ServiceCommands.get_workstation_list_by_user_login,
            ServiceCommands.get_user_by_workstation,
            ServiceCommands.create_user_by_template,
            ServiceCommands.set_user_telephone_number,
            ServiceCommands.set_user_password,
            ServiceCommands.set_user_status,
            ServiceCommands.remove_user,
            ServiceCommands.drop_user_cache,
            ServiceCommands.drop_workstaion_cache,
            ServiceCommands.get_user_list_by_property,
        ],
        version="1.1",
        standalone_name="ad"
    )

    RECOGNIZE: ServiceDescription = ServiceDescription(
        name="Recognize",
        description="Recognize service",
        host=HOSTS.WS255.NAME,
        host_changeable=False,
        commands=[
            ServiceCommands.get_barcode_list_information,
            ServiceCommands.document_type_exists,
            ServiceCommands.recognize_document,
        ],
    )

    FILE_WATCHDOG: ServiceDescription = ServiceDescription(
        name="FileWatchdog",
        description="FileWatchdog service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[ServiceCommands.listen_for_new_files],
    )

    """
    FILE_ORGANIZER: ServiceDescription = ServiceDescription(
        name="FileOrganizer",
        description="File organizer service",
        host=HOSTS.WS255.NAME,
    )
    """

    MAIL: ServiceDescription = ServiceDescription(
        name="Mail",
        description="Mail service",
        host=HOSTS.WS255.NAME,
        commands=[
            ServiceCommands.check_email_accessibility,
            ServiceCommands.send_email,
            ServiceCommands.get_email_information,
        ],
    )

    DOCS: ServiceDescription = ServiceDescription(
        name="Docs",
        description="Documents service",
        host=HOSTS.DC2.NAME,
        commands=[
            ServiceCommands.get_inventory_report,
            ServiceCommands.create_user_document,
            ServiceCommands.save_time_tracking_report,
            ServiceCommands.create_barcodes_for_inventory,
            ServiceCommands.create_barcode_for_polibase_person,
            ServiceCommands.create_qr_code,
            ServiceCommands.check_inventory_report,
            ServiceCommands.save_inventory_report_item,
            ServiceCommands.close_inventory_report,
            ServiceCommands.create_note,
            ServiceCommands.get_note,
            ServiceCommands.get_note_list_by_label,
            ServiceCommands.create_statistics_chart,
            ServiceCommands.save_xlsx,
            ServiceCommands.drop_note_cache,
        ],
    )

    MARK: ServiceDescription = ServiceDescription(
        name="Mark",
        description="Mark service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[
            ServiceCommands.get_free_mark_list,
            ServiceCommands.get_temporary_mark_list,
            ServiceCommands.get_mark_person_division_list,
            ServiceCommands.get_time_tracking,
            ServiceCommands.get_mark_list,
            ServiceCommands.get_mark_by_tab_number,
            ServiceCommands.get_mark_by_person_name,
            ServiceCommands.get_free_mark_group_statistics_list,
            ServiceCommands.get_free_mark_list_by_group_id,
            ServiceCommands.get_owner_mark_for_temporary_mark,
            ServiceCommands.get_mark_list_by_division_id,
            ServiceCommands.set_full_name_by_tab_number,
            ServiceCommands.set_telephone_by_tab_number,
            ServiceCommands.check_mark_free,
            ServiceCommands.create_mark,
            ServiceCommands.make_mark_as_free_by_tab_number,
            ServiceCommands.make_mark_as_temporary,
            ServiceCommands.remove_mark_by_tab_number,
            ServiceCommands.door_operation,
        ],
    )

    POLIBASE: ServiceDescription = ServiceDescription(
        name="Polibase",
        description="Polibase service",
        host=POLIBASE_BASE.host,
        pyton_executor_path=POLIBASE_BASE.pyton_executor_path,
        run_from_system_account=POLIBASE_BASE.run_from_system_account,
        commands=[
            ServiceCommands.get_polibase_person_by_pin,
            ServiceCommands.get_polibase_persons_by_pin,
            ServiceCommands.get_polibase_persons_by_telephone_number,
            ServiceCommands.get_polibase_persons_by_name,
            ServiceCommands.get_polibase_persons_by_card_registry_folder_name,
            ServiceCommands.get_polibase_person_registrator_by_pin,
            ServiceCommands.get_polibase_person_pin_list_with_old_format_barcode,
            #
            ServiceCommands.get_polibase_persons_pin_by_visit_date,
            #
            ServiceCommands.search_polibase_person_visits,
            ServiceCommands.get_polibase_person_visits_last_id,
            #
            ServiceCommands.set_polibase_person_card_folder_name,
            ServiceCommands.set_polibase_person_email,
            ServiceCommands.set_barcode_for_polibase_person,
            ServiceCommands.check_polibase_person_card_registry_folder_name,
            ServiceCommands.set_polibase_person_telephone_number,
            ServiceCommands.get_polibase_person_operator_by_pin,
            ServiceCommands.get_polibase_person_by_email,
            #
            ServiceCommands.execute_polibase_query,
            ServiceCommands.update_person_change_date,
            ServiceCommands.get_polibase_person_pin_by_login,
            ServiceCommands.get_polibase_person_user_login_and_worstation_name_pair_list,
            ServiceCommands.get_bonus_list,
        ],
    )

    MESSAGE_RECEIVER: ServiceDescription = ServiceDescription(
        name="MessageReceiver",
        description="Message service",
        host=HOSTS.BACKUP_WORKER.NAME,
        host_changeable=False,
    )

    POLIBASE_APP: ServiceDescription = ServiceDescription(
        name="PolibaseApp",
        description="Polibase Application service",
        host=POLIBASE_BASE.host,
        pyton_executor_path=POLIBASE_BASE.pyton_executor_path,
        run_from_system_account=POLIBASE_BASE.run_from_system_account,
    )

    MESSAGE_QUEUE: ServiceDescription = ServiceDescription(
        name="MessageQueue",
        description="Message queue service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[ServiceCommands.add_message_to_queue],
    )

    POLIBASE_PERSON_NOTIFICATION: ServiceDescription = ServiceDescription(
        name="PolibasePersonNotification",
        description="Polibase Person Notification service",
        host=HOSTS.BACKUP_WORKER.NAME,
    )

    POLIBASE_PERSON_INFORMATION_QUEST: ServiceDescription = ServiceDescription(
        name="PolibasePersonInformationQuest",
        description="Polibase Person Information Quest service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[ServiceCommands.start_polibase_person_information_quest],
    )

    POLIBASE_PERSON_REVIEW_NOTIFICATION: ServiceDescription = ServiceDescription(
        name="PolibasePersonReviewNotification",
        description="Polibase Person Review Notification service",
        host=HOSTS.BACKUP_WORKER.NAME,
    )

    WS: ServiceDescription = ServiceDescription(
        name="WS",
        description="Workstation service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[
            ServiceCommands.reboot,
            ServiceCommands.shutdown,
            ServiceCommands.send_message_to_user_or_workstation,
            ServiceCommands.kill_process,
        ],
    )

    BACKUP: ServiceDescription = ServiceDescription(
        name="Backup",
        description="Backup service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[
            ServiceCommands.robocopy_start_job,
            ServiceCommands.robocopy_get_job_status_list,
        ],
    )

    PRINTER: ServiceDescription = ServiceDescription(
        name="Printer",
        description="Printer service",
        host=HOSTS.DC2.NAME,
        commands=[ServiceCommands.printers_report, ServiceCommands.printer_snmp_call],
    )

    POLIBASE_DATABASE: ServiceDescription = ServiceDescription(
        name="PolibaseDatabase",
        description="Polibase database service",
        host=POLIBASE_BASE.host,
        pyton_executor_path=POLIBASE_BASE.pyton_executor_path,
        run_from_system_account=POLIBASE_BASE.run_from_system_account,
        commands=[ServiceCommands.create_polibase_database_backup],
    )

    SSH: ServiceDescription = ServiceDescription(
        name="SSH",
        description="SSH service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[
            ServiceCommands.execute_ssh_command,
            ServiceCommands.get_certificate_information,
            ServiceCommands.get_unix_free_space_information_by_drive_name,
            ServiceCommands.mount_facade_for_linux_host,
        ],
        version = "1.0"
    )

    WS735: ServiceDescription = ServiceDescription(
        name="ws735",
        description="ws-735 service",
        host=HOSTS.WS735.NAME,
        login="{" + LINK.DEVELOPER_LOGIN + "}",
        password="{" + LINK.DEVELOPER_PASSWORD + "}",
        commands=[ServiceCommands.print_image],
        host_changeable=False,
    )

    RECOGNIZE_TEST: ServiceDescription = ServiceDescription(
        name="RecognizeTest",
        description="Recognize test service",
        host=HOSTS.WS255.NAME,
        auto_start=False,
        auto_restart=False,
        visible_for_admin=False,
    )

    """INDICATIONS: ServiceDescription = ServiceDescription(
        name="Indications",
        description="Indications service",
        host=HOSTS.WS255.NAME,
    )"""

    WEB_SERVER: ServiceDescription = ServiceDescription(
        name="WebServer",
        description="Web server service",
        host=HOSTS.WS255.NAME,
    )

    CHECKER: ServiceDescription = ServiceDescription(
        name="Checker",
        description="Checker service",
        host=HOSTS.BACKUP_WORKER.NAME,
        commands=[ServiceCommands.get_resource_status_list],
        standalone_name="chk",
        version="1.7"
    )

    AUTOMATION: ServiceDescription = ServiceDescription(
        name="Automation",
        description="Automation service",
        host=HOSTS.BACKUP_WORKER.NAME,
    )

    MEDICAL_AUTOMATION: ServiceDescription = ServiceDescription(
        name="MedicalAutomation",
        description="Medical Automation service",
        host=HOSTS.BACKUP_WORKER.NAME,
    )

    REGISTRATOR_HELPER: ServiceDescription = ServiceDescription(
        name="RegistratorHelper",
        description="Registrator mobile helper service",
        host=HOSTS.BACKUP_WORKER.NAME,
        version="1.0",
        standalone_name="reg_help"
    )

    DEVELOPER: ServiceDescription = ServiceDescription(
        name="Developer",
        description="Developer service",
        host=HOSTS.DEVELOPER.NAME,
        port=RPC.PORT(1),
        visible_for_admin=False,
        auto_start=False,
        auto_restart=False,
        commands=[ServiceCommands.test],
    )
    
    
    #done
    MOBILE_HELPER: ServiceDescription = ServiceDescription(
        name="MobileHelper",
        description="Mobile helper service",
        host=HOSTS.WS255.NAME,
        commands=[ServiceCommands.send_mobile_helper_message],
        auto_restart=True,
        support_servers=(HOSTS.DEVELOPER.NAME,),
        standalone_name="mio",
        version="1.49910"
    )

