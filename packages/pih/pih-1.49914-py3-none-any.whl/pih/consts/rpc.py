from enum import Enum, auto


class ServiceCommands(Enum):
    ping: int = auto()
    subscribe: int = auto()
    unsubscribe: int = auto()
    create_subscribtions: int = auto()
    stop_service: int = auto()
    send_event: int = auto()
    # Service admin
    on_service_starts: int = auto()
    on_service_stops: int = auto()
    update_service_information: int = auto()
    get_service_information_table: int = auto()

    # Log
    send_log_message: int = auto()
    #
    send_message_to_user_or_workstation: int = auto()
    add_message_to_queue: int = auto()
    send_delayed_message: int = auto()
    # Documents
    create_user_document: int = auto()
    save_time_tracking_report: int = auto()
    save_xlsx: int = auto()
    create_barcodes_for_inventory: int = auto()
    create_barcode_for_polibase_person: int = auto()
    create_qr_code: int = auto()
    check_inventory_report: int = auto()
    get_inventory_report: int = auto()
    save_inventory_report_item: int = auto()
    close_inventory_report: int = auto()
    # Polibase
    get_polibase_person_by_pin: int = auto()
    get_polibase_persons_by_pin: int = auto()
    get_polibase_persons_by_card_registry_folder_name: int = auto()
    get_polibase_persons_by_name: int = auto()
    get_polibase_person_pin_list_with_old_format_barcode: int = auto()
    get_polibase_person_registrator_by_pin: int = auto()
    get_polibase_persons_pin_by_visit_date: int = auto()
    get_polibase_persons_by_telephone_number: int = auto()
    get_polibase_person_pin_by_login: int = auto()
    get_polibase_person_user_login_and_worstation_name_pair_list: int = auto()
    #
    get_polibase_person_visits_last_id: int = auto()
    search_polibase_person_visits: int = auto()
    #
    set_polibase_person_card_folder_name: int = auto()
    set_polibase_person_email: int = auto()
    set_barcode_for_polibase_person: int = auto()
    check_polibase_person_card_registry_folder_name: int = auto()

    # ActiveDirectory
    check_user_exists_by_login: int = auto()
    drop_user_cache: int = auto()
    drop_workstaion_cache: int = auto()
    get_user_by_full_name: int = auto()
    get_users_by_name: int = auto()
    # get_active_users_by_name: int = auto()
    get_user_by_login: int = auto()
    get_user_by_telephone_number: int = auto()
    get_template_users: int = auto()
    get_containers: int = auto()
    get_user_list_by_job_position: int = auto()
    get_user_list_by_group: int = auto()
    create_user_by_template: int = auto()
    set_user_telephone_number: int = auto()
    authenticate: int = auto()
    set_user_password: int = auto()
    set_user_status: int = auto()
    get_printer_list: int = auto()
    remove_user: int = auto()
    get_computer_description_list: int = auto()
    get_computer_list: int = auto()
    get_workstation_list_by_user_login: int = auto()
    get_user_by_workstation: int = auto()
    # Printer
    printers_report: int = auto()
    # Orion
    get_free_mark_list: int = auto()
    get_temporary_mark_list: int = auto()
    get_mark_person_division_list: int = auto()
    get_time_tracking: int = auto()
    get_mark_list: int = auto()
    get_owner_mark_for_temporary_mark: int = auto()
    get_mark_by_tab_number: int = auto()
    get_mark_by_person_name: int = auto()
    get_free_mark_group_statistics_list: int = auto()
    get_free_mark_list_by_group_id: int = auto()
    get_mark_list_by_division_id: int = auto()
    set_full_name_by_tab_number: int = auto()
    set_telephone_by_tab_number: int = auto()
    check_mark_free: int = auto()
    create_mark: int = auto()
    remove_mark_by_tab_number: int = auto()
    make_mark_as_free_by_tab_number: int = auto()
    make_mark_as_temporary: int = auto()
    # PolibaseDatabaseBackup
    create_polibase_database_backup: int = auto()
    # DataStorage::Settings
    set_settings_value: int = auto()
    get_settings_value: int = auto()
    # HeatBeat
    heart_beat: int = auto()
    # Notifier
    register_polibase_person_information_quest: int = auto()
    search_polibase_person_information_quests: int = auto()
    update_polibase_person_information_quest: int = auto()
    # Visit Cached
    update_polibase_person_visit_to_data_stogare: int = auto()
    search_polibase_person_visits_in_data_storage: int = auto()
    # Visit notification
    register_polibase_person_visit_notification: int = auto()
    search_polibase_person_visit_notifications: int = auto()
    # Notification confirmation
    search_polibase_person_notification_confirmation: int = auto()
    update_polibase_person_notification_confirmation: int = auto()
    #
    check_email_accessibility: int = auto()
    get_email_information: int = auto()
    #
    register_delayed_message: int = auto()
    search_delayed_messages: int = auto()
    update_delayed_message: int = auto()
    #
    execute_data_source_query: int = auto()
    # WORKSTATION
    reboot: int = auto()
    shutdown: int = auto()
    log_out: int = auto()
    # Robocopy::Job
    robocopy_start_job: int = auto()
    robocopy_get_job_status_list: int = auto()
    # DataStorage::Storage value
    set_storage_value: int = auto()
    get_storage_value: int = auto()
    # Resource Manager
    get_resource_status_list: int = auto()
    send_mobile_helper_message: int = auto()

    register_ct_indications_value: int = auto()
    get_last_ct_indications_value_container_list: int = auto()
    get_last_сhiller_indications_value_container_list: int = auto()
    #
    test: int = auto()
    #
    execute_ssh_command: int = auto()
    get_certificate_information: int = auto()
    get_unix_free_space_information_by_drive_name: int = auto()
    print_image: int = auto()
    #
    get_ogrn_value: int = auto()
    get_fms_unit_name: int = auto()
    #
    start_polibase_person_information_quest: int = auto()
    register_chiller_indications_value: int = auto()
    #
    add_gkeep_item: int = auto()
    get_gkeep_item_list_by_any: int = auto()
    # get_gkeep_item_list_by_name: int = auto()
    #
    create_note: int = auto()
    get_note: int = auto()
    get_note_list_by_label: int = auto()
    set_polibase_person_telephone_number: int = auto()
    kill_process: int = auto()
    #
    register_event: int = auto()
    get_event: int = auto()
    remove_event: int = auto()
    #
    get_polibase_person_operator_by_pin: int = auto()
    #
    get_barcode_list_information: int = auto()
    document_type_exists: int = auto()
    #
    listen_for_new_files: int = auto()
    #
    recognize_document: int = auto()
    #
    get_polibase_person_by_email: int = auto()
    #
    create_statistics_chart: int = auto()
    #
    execute_polibase_query: int = auto()
    #
    send_email: int = auto()
    #
    joke: int = auto()
    #
    printer_snmp_call: int = auto()
    #
    update_person_change_date: int = auto()
    #
    drop_note_cache: int = auto()
    #
    get_bonus_list: int = auto()
    #
    door_operation: int = auto()
    #
    mount_facade_for_linux_host: int = auto()
    #
    get_event_count: int = auto()
    #
    get_user_list_by_property: int = auto()

