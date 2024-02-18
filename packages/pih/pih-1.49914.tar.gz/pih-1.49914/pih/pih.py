import ipih
import calendar
from collections import defaultdict
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from getpass import getpass
from threading import Thread
from time import sleep
from grpc import StatusCode
import dataclasses
import importlib.util
import locale
import os
import platform
import json
import pkg_resources
import re
import subprocess
from subprocess import DEVNULL, STDOUT, CompletedProcess
import sys
from typing import Any, Callable
import colorama
from colorama import Back, Style, Fore, ansi
from colorama.ansi import CSI, OSC
from prettytable import PrettyTable
import requests
from requests import ConnectTimeout, Response
import traceback
import base64
import uuid
from enum import Enum
from string import Formatter
import urllib.parse
from argparse import ArgumentParser, Namespace, ArgumentError
from io import StringIO
from contextlib import contextmanager, redirect_stdout
from urllib.parse import unquote, quote_plus
from transliterate import translit
from functools import cache

####################################
from pih.errors import *
from pih.consts.rpc import *
from pih.consts.settings import SETTINGS
from pih.consts.events import *
from pih.consts.polibase import *
from pih.rpc import *
from pih.rpc_collection import *
from pih.const import *
from pih.tools import *
from pih.collection import *
from pih.consts.addresses import EMAIL_COLLECTION
from random import randrange
from json import dumps

PIHThreadPoolExecutor = ThreadPoolExecutor

_cache: dict[str, bool] = {}


class PIHThread(Thread):
    def __init__(
        self,
        target: Callable,
        auto_start: bool = True,
        group=None,
        name=None,
        args=(),
        kwargs=None,
        *,
        daemon=None,
    ):
        def local_target(*args) -> None:
            with PIH.ERROR.detect():
                target(*args)

        super().__init__(
            group=group,
            target=local_target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
        )
        if auto_start:
            self.start()


class OutputStubAbstract:
    def b(self, value: str):
        pass

    def i(self, value: str):
        pass


class OutputStub(OutputStubAbstract):
    def b(self, value: str) -> str:
        return value

    def i(self, value: str) -> str:
        return value

    def set_to(self, value: OutputStubAbstract) -> None:
        value.b = self.b
        value.i = self.i


class IClosable:
    def close(self) -> None:
        raise NotImplemented()


class ServiceListener(IClosable):
    def __init__(self):
        self.service: IService | None = None
        self.service_command_list: list[ServiceCommands] | None = None
        self.host: str = PIH.OS.host()
        self.port: int = NetworkTool.next_free_port()

    def listen_for(
        self,
        service_command_list: list[ServiceCommands],
        handler: Callable[[ServiceCommands, ParameterList, IClosable], Any],
    ) -> None:
        self.service_command_list = service_command_list

        def service_starts_handler(service: IService) -> None:
            self.service = service
            for service_command in service_command_list:
                service.subscribe_on(service_command)

        PIH.SERVICE.ADMIN.serve(
            PIH.SERVICE.ADMIN.create_event_listener_service_description(
                self.host, self.port
            ),
            lambda command_name, pl: handler(command_name, pl, self),
            service_starts_handler,
            show_output=True,
        )

    def close(self) -> None:
        self.service.unsubscribe(self.service_command_list)
        PIH.SERVICE.ADMIN.stop(self.service.get_description(), False)


class MarkOutputAbstract:
    def by_any(self, value: str) -> None:
        raise NotImplemented()

    def result(
        self, result: Result[list[Mark]], caption: str, use_index: bool = False
    ) -> None:
        raise NotImplemented()


class OutputAbstract:
    def set_indent(self, count: int = 1) -> None:
        raise NotImplemented()

    def bold(self, value: str) -> str:
        raise NotImplemented()

    def header(self, caption: str) -> None:
        raise NotImplemented()

    def reset_indent(self) -> None:
        raise NotImplemented()

    def restore_indent(self) -> None:
        raise NotImplemented()

    def init(self) -> None:
        raise NotImplemented()

    def text_color(self, color: int, text: str) -> str:
        raise NotImplemented()

    def text_black(self, text: str) -> str:
        raise NotImplemented()

    def color_str(
        self,
        color: int,
        text: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> str:
        raise NotImplemented()

    def color(
        self,
        color: int,
        text: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> None:
        raise NotImplemented()

    def write_line(self, text: str) -> None:
        raise NotImplemented()

    def index(self, index: int, text: str, max_index: int = None) -> None:
        raise NotImplemented()

    def input(self, caption: str) -> None:
        raise NotImplemented()

    def input_str(
        self,
        caption: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> str:
        raise NotImplemented()

    def value(self, caption: str, value: str, text_before: str | None = None) -> None:
        raise NotImplemented()

    def get_action_value(
        self, caption: str, value: str, show: bool = True
    ) -> ActionValue:
        raise NotImplemented()

    def head(self, caption: str) -> None:
        raise NotImplemented()

    def head1(self, caption: str) -> None:
        raise NotImplemented()

    def head2(self, caption: str) -> None:
        raise NotImplemented()

    def new_line(self) -> None:
        raise NotImplemented()

    def separated_line(self) -> None:
        self.new_line()

    def error_str(self, caption: str) -> str:
        raise NotImplemented()

    def error(self, caption: str) -> None:
        raise NotImplemented()

    def notify_str(self, caption: str) -> str:
        raise NotImplemented()

    def notify(self, caption: str) -> None:
        raise NotImplemented()

    def good_str(self, caption: str) -> str:
        raise NotImplemented()

    def good(self, caption: str) -> None:
        raise NotImplemented()

    def green_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def green(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def yellow_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def yellow(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def black_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def black(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def white_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def white(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def draw_line(
        self, color: str = Back.LIGHTBLUE_EX, char: str = " ", width: int = 80
    ) -> None:
        raise NotImplemented()

    def line(self) -> None:
        raise NotImplemented()

    def magenta_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def magenta(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def cyan(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def cyan_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def red(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def red_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def blue(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def blue_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def bright(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        raise NotImplemented()

    def bright_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        raise NotImplemented()

    def get_number(self, value: int) -> str:
        raise NotImplemented()

    @contextmanager
    def make_separated_lines(self) -> bool:
        yield True

    def write_result(
        self,
        result: Result[T],
        use_index: bool = True,
        item_separator: str = "\n",
        empty_result_text: str = "Не найдено",
        separated_result_item: bool = True,
        label_function: Callable[[Any, int], str] = None,
        data_label_function: Callable[
            [int, FieldItem, Result[T], Any], tuple[bool, str]
        ] = None,
        title: str | None = None,
    ) -> None:
        raise NotImplemented()

    @contextmanager
    def send_to_group(self, group: CONST.MESSAGE.WHATSAPP.GROUP) -> bool:
        raise NotImplemented()


class MarkOutputBase(MarkOutputAbstract):
    def __init__(self):
        self.parent: OutputBase


class MarkOutput(MarkOutputBase):
    def by_any(self, value: str) -> None:
        try:
            self.result(PIH.RESULT.MARK.by_any(value), "Найденные карты доступа:", True)
        except NotFound as error:
            self.parent.error(error.get_details())

    def result(
        self, result: Result[list[Mark]], caption: str, use_index: bool = False
    ) -> None:
        self.parent.table_with_caption_first_title_is_centered(
            result, caption, use_index
        )


class UserOutputAbstract:
    def result(
        self,
        result: Result[list[User]],
        caption: str | None = None,
        use_index: bool = False,
        root_location: str = AD.ACTIVE_USERS_CONTAINER_DN,
    ) -> None:
        raise NotImplemented()

    def get_formatted_given_name(self, value: str | None = None) -> str:
        return value


class OutputExtendedAbstract:
    def pih_title(self) -> None:
        raise NotImplemented()

    def rpc_service_header(self, host: str, port: int, description: str) -> None:
        raise NotImplemented()

    def service_header(self, description: ServiceDescription) -> None:
        raise NotImplemented()

    def free_marks(self, show_guest_marks: bool, use_index: bool = False) -> None:
        raise NotImplemented()

    def guest_marks(self, use_index: bool = False) -> None:
        raise NotImplemented()

    def temporary_candidate_for_mark(self, mark: Mark) -> None:
        raise NotImplemented()

    def free_marks_group_statistics(
        self, use_index: bool = False, show_guest_marks: bool | None = None
    ) -> None:
        raise NotImplemented()

    def free_marks_by_group(self, group: dict, use_index: bool = False) -> None:
        raise NotImplemented()

    def free_marks_group_statistics_for_result(
        self, result: Result, use_index: bool
    ) -> None:
        raise NotImplemented()

    def free_marks_by_group_for_result(
        self, group: MarkGroup, result: Result, use_index: bool
    ) -> None:
        raise NotImplemented()

    def temporary_marks(
        self,
        use_index: bool = False,
    ) -> None:
        raise NotImplemented()

    def containers_for_result(self, result: Result, use_index: bool = False) -> None:
        raise NotImplemented()

    def table_with_caption_first_title_is_centered(
        self,
        result: Result,
        caption: str,
        use_index: bool = False,
        label_function: Callable | None = None,
    ) -> None:
        raise NotImplemented()

    def table_with_caption_last_title_is_centered(
        self,
        result: Result,
        caption: str,
        use_index: bool = False,
        label_function: Callable | None = None,
    ) -> None:
        raise NotImplemented()

    def table_with_caption(
        self,
        result: Any,
        caption: str | None = None,
        use_index: bool = False,
        modify_table_function: Callable | None = None,
        label_function: Callable | None = None,
    ) -> None:
        raise NotImplemented()

    @contextmanager
    def make_loading(self, loading_timeout: float = 1, text: str | None = None) -> None:
        raise NotImplemented()

    def template_users_for_result(self, data: dict, use_index: bool = False) -> None:
        raise NotImplemented()

    def clear_screen(self) -> None:
        raise NotImplemented()

    def write_video(self, caption: str, video_content: str) -> None:
        raise NotImplemented()

    def write_image(self, caption: str, image_content: str) -> bool:
        pass


class UserOutputBase(UserOutputAbstract):
    def __init__(self):
        self.parent: Output


class UserOutput(UserOutputBase):
    def result(
        self,
        result: Result[list[User]],
        caption: str | None = None,
        use_index: bool = False,
        root_location: str = AD.ACTIVE_USERS_CONTAINER_DN,
    ) -> None:
        data: list = DataTool.as_list(result.data)
        fields: FieldItemList = result.fields
        base_location_list: list[str] = PIH.DATA.FORMAT.location_list(
            root_location, False
        )
        root_base_location: list[str] = base_location_list[0:2]
        root_base_location.reverse()
        base_location = j(
            (
                j(root_base_location, "."),
                j(base_location_list[2:], AD.LOCATION_JOINER),
            ),
            AD.LOCATION_JOINER,
        )
        location_field = fields.get_item_by_name(FIELD_NAME_COLLECTION.DN)
        pevious_caption: str = location_field.caption
        location_field.caption = f"{location_field.caption} ({base_location})"

        def modify_data(field: FieldItem, user: User) -> str:
            if field.name == USER_PROPERTIES.DN:
                return j(
                    DataTool.filter(
                        lambda x: x not in base_location_list,
                        PIH.DATA.FORMAT.location_list(user.distinguishedName),
                    ),
                    AD.LOCATION_JOINER,
                )
            if field.name == USER_PROPERTIES.USER_ACCOUNT_CONTROL:
                return jnl(
                    PIH.DATA.FORMAT.get_user_account_control_values(
                        user.userAccountControl
                    )
                )
            if field.name == USER_PROPERTIES.DESCRIPTION:
                return user.description
            if field.name == USER_PROPERTIES.NAME:
                return jnl(user.name.split(" "))
            return None

        self.parent.table_with_caption(
            result,
            "Пользватели:" if len(data) > 1 else "Пользватель:",
            False,
            None,
            modify_data,
        )
        location_field.caption = pevious_caption


class InputAbstract:

    def input(
        self,
        caption: str | None = None,
        new_line: bool = True,
        check_function: Callable[[str], str] | None = None,
    ) -> str:
        raise NotImplemented()

    def polibase_person_card_registry_folder(
        self, value: str | None = None, title: str | None = None
    ) -> str:
        raise NotImplemented()

    def polibase_persons_by_any(
        self, value: str | None = None, title: str | None = None, use_all: bool = False
    ) -> list[PolibasePerson]:
        raise NotImplemented()

    def telephone_number(
        self, format: bool = True, telephone_prefix: str = CONST.TELEPHONE_NUMBER_PREFIX
    ) -> str:
        raise NotImplemented()

    def email(self) -> str:
        raise NotImplemented()

    def message(self, caption: str | None = None, prefix: str | None = None) -> str:
        raise NotImplemented()

    def description(self) -> str:
        raise NotImplemented()

    def login(self, check_on_exists: bool = False) -> str:
        raise NotImplemented()

    def indexed_list(
        self,
        caption: str,
        name_list: list[Any],
        caption_list: list[str],
        by_index: bool = False,
    ) -> str:
        raise NotImplemented()

    def indexed_field_list(self, caption: str, list: FieldItemList) -> str:
        raise NotImplemented()

    def index(
        self,
        caption: str,
        data: list,
        label_function: Callable[[Any, int], str] = None,
        use_zero_index: bool = False,
    ) -> int:
        raise NotImplemented()

    def item_by_index(
        self,
        caption: str,
        data: list[Any],
        label_function: Callable[[Any, int], str] = None,
        use_zero_index: bool = False,
    ) -> Any:
        raise NotImplemented()

    def tab_number(self, check: bool = True) -> str:
        raise NotImplemented()

    def password(
        self,
        secret: bool = True,
        check: bool = False,
        settings: PasswordSettings = None,
        is_new: bool = True,
    ) -> str:
        raise NotImplemented()

    def same_if_empty(self, caption: str, src_value: str) -> str:
        raise NotImplemented()

    def name(self) -> str:
        raise NotImplemented()

    def full_name(self, one_line: bool = False) -> FullName:
        raise NotImplemented()

    def yes_no(
        self,
        text: str = " ",
        enter_for_yes: bool = False,
        yes_label: str | None = None,
        no_label: str | None = None,
        yes_checker: Callable[[str], bool] = None,
    ) -> bool:
        raise NotImplemented()

    def message_for_user_by_login(self, login: str) -> str:
        raise NotImplemented()

    def polibase_person_any(self, title: str | None = None) -> str:
        raise NotImplemented()

    def datetime(self, value: str) -> datetime:
        raise NotImplemented()

    def choose_file(
        self, use_search_request: bool | None = None, force_fetch: bool | None = None
    ) -> File:
        raise NotImplemented()


class UserInputAbstract:
    def container(self) -> UserBase:
        raise NotImplemented()

    def by_name(self) -> User:
        raise NotImplemented()

    def title_any(self, title: str | None = None) -> str:
        raise NotImplemented()

    def by_any(
        self,
        value: str | None = None,
        active: bool | None = None,
        title: str | None = None,
        use_all: bool = False,
    ) -> list[User]:
        raise NotImplemented()

    def telephone_number(
        self,
        value: str | None = None,
        active: bool | None = None,
        title: str | None = None,
    ) -> User:
        raise NotImplemented()

    def template(self) -> User:
        raise NotImplemented()

    def search_attribute(self) -> str:
        raise NotImplemented()

    def search_value(self, search_attribute: str) -> str:
        raise NotImplemented()

    def generate_login(
        self,
        full_name: FullName,
        ask_for_remove_inactive_user_if_login_is_exists: bool = True,
        ask_for_use: bool = True,
    ) -> str:
        raise NotImplemented()

    def generate_password(
        self, once: bool = False, settings: PasswordSettings = PASSWORD.SETTINGS.DEFAULT
    ) -> str:
        raise NotImplemented()


class UserInputBase(UserInputAbstract):
    def __init__(self):
        self.parent: InputBase = None


class MarkInputAbstract:
    def free(self, group: MarkGroup = None) -> Mark:
        raise NotImplemented()

    def person_division(self, use_empty_division: bool = True) -> PersonDivision:
        raise NotImplemented()

    def by_name(self) -> Mark:
        raise NotImplemented()

    def by_any(self, value: str | None = None) -> Mark:
        raise NotImplemented()

    def any(self) -> str:
        raise NotImplemented()


class MarkInputBase(MarkInputAbstract):
    def __init__(self):
        self.parent: InputBase


class InputBase(InputAbstract):
    def __init__(self):
        self.output: OutputBase
        self.mark: MarkInputBase
        self.user: UserInputBase


class OutputBase(OutputAbstract, OutputExtendedAbstract):
    def __init__(
        self,
        user_output: UserOutputBase | None = None,
        mark_output: MarkOutputBase | None = None,
    ):
        self.text_before: str = ""
        self.text_after: str = ""
        self.indent_symbol: str = " "
        self.indent_value: int = 0
        self.user: UserOutputBase = user_output
        self.user.parent = self
        self.mark: MarkOutputBase = mark_output
        self.mark.parent = self
        self.personalize = False


class SessionAbstract:
    def run_forever_untill_enter_not_pressed(self) -> None:
        raise NotImplemented()

    def exit(self, timeout: int = None, message: str | None = None) -> None:
        raise NotImplemented()

    def get_login(self) -> str:
        raise NotImplemented()

    def get_user(self) -> User:
        raise NotImplemented()

    def user_given_name(self) -> str:
        raise NotImplemented()

    def start(self, login: str, notify: bool = True) -> None:
        raise NotImplemented()

    def say_hello(
        self, telephone_number: str | None = None, greeting: bool = True
    ) -> None:
        raise NotImplemented()

    @property
    def argv(self) -> list[str]:
        raise NotImplemented()

    def arg(self, index: int = None, default_value: str | None = None) -> str:
        raise NotImplemented()

    @property
    def file_path(self) -> str:
        raise NotImplemented()

    @property
    def file_name(self) -> str:
        raise NotImplemented()

    def authenticate(self, exit_on_fail: bool = True) -> bool:
        raise NotImplemented()

    def add_allowed_group(self, value: AD.Groups) -> None:
        raise NotImplemented()


class SessionBase(SessionAbstract):
    def __init__(
        self,
        input: InputBase | None = None,
        output: OutputBase | None = None,
        name: str | None = None,
        flags: int = 0,
    ):
        self.allowed_groups: list[AD.Groups] = []
        self.login: str | None = None
        self.user: User | None = None
        self.input: InputBase | None = input
        self.output: OutputBase | None = output
        self.name: str | None = name
        self.flags: int = flags

    def add_allowed_group(self, value: AD.Groups) -> None:
        self.allowed_groups.append(value)

    @property
    def is_mobile(self) -> bool:
        return self.name == "mobile"


class Session(SessionBase):
    def __init__(
        self, input: InputBase | None = None, output: OutputBase | None = None
    ):
        super().__init__(input, output)
        self.authenticated: bool = False
        self.arg_parser: ArgumentParser = ArgumentParser(description="Service help")

    def run_forever_untill_enter_not_pressed(self) -> None:
        try:
            self.output.green("Нажмите Ввод для выхода...")
            input()
        except KeyboardInterrupt:
            pass

    def exit(self, timeout: int = None, message: str | None = None) -> None:
        if message is not None:
            self.output.error(message)
        if timeout is None:
            timeout = 5
        sleep(timeout)
        exit()

    def get_login(self) -> str:
        if n(self.login):
            self.start(PIH.OS.get_login())
        return self.login

    def get_user(self) -> User:
        if n(self.user):
            self.user = PIH.RESULT.USER.by_login(self.get_login()).data
        return self.user

    @property
    def user_given_name(self) -> str:
        return FullNameTool.to_given_name(self.get_user().name)

    def start(self, login: str, notify: bool = True) -> None:
        if n(self.login):
            self.login = login
            if notify:
                PIH.EVENT.start_session()

    def say_hello(self, _: str | None = None, greeting: bool = True) -> None:
        user: User = self.get_user()
        if nn(user):
            if greeting:
                self.output.good(js(("Добро пожаловать,", user.name)))
                self.output.new_line()
            return
        self.output.error(f"Ты кто такой? Давай, до свидания...")
        self.exit()

    @property
    def argv(self) -> list[str]:
        return sys.argv[1:] if len(sys.argv) > 1 else []

    def arg(self, index: int = 0, default_value: Any | None = None) -> str | Namespace:
        return DataTool.by_index(self.argv, index, default_value)

    @property
    def arg_namespace(self) -> Namespace:
        return self.arg_parser.parse_args()

    def named_arg(self, name: str) -> str | None:
        return self.arg_parser.parse_args().__getattribute__(name)

    def isolated_arg(self) -> str | None:
        return self.named_arg(ISOLATED_ARG_NAME)

    def add_arg(self, *args, **kwargs) -> bool:
        try:
            self.arg_parser.add_argument(j((ARGUMENT_PREFIX, args[0])), **kwargs)
        except ArgumentError as _:
            return False
        return True

    def add_isolated_arg(self) -> bool:
        return self.add_arg(
            ISOLATED_ARG_NAME,
            help="Service isolated flag",
            nargs="?",
            const=1,
            type=str,
            default=None,
        )

    @property
    def file_path(self) -> str:
        return sys.argv[0]

    @property
    def is_standalone(self) -> bool:
        return self.file_path.endswith(FILE.EXTENSION.EXE)

    @property
    def file_name(self) -> str:
        return PathTool.get_file_name(self.file_path)

    def authenticate(self, exit_on_fail: bool = True, once: bool = True) -> bool:
        try:
            if once and self.authenticated:
                return True
            self.output.green("Инициализация...")
            self.output.clear_screen()
            self.output.pih_title()
            if PIH.SERVICE.check_on_accessibility(ServiceRoles.AD):
                login: str = PIH.OS.get_login()
                self.output.head1(
                    f"{FullNameTool.to_given_name(PIH.RESULT.USER.by_login(login, cached=False).data.name)}, пожалуйста, пройдите аутентификацию..."
                )
                self.output.new_line()
                if not self.input.yes_no(f"Использовать логин '{login}'", True):
                    login = PIH.input.login()
                password: str = PIH.input.password(is_new=False)
                if DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.authenticate, (login, password)
                    )
                ):
                    self.authenticated = True
                    self.start(login, False)
                    PIH.EVENT.login()
                    self.output.good(
                        self.output.text_black(
                            f"Добро пожаловать, {self.get_user().name}..."
                        )
                    )
                    return True
                else:
                    if exit_on_fail:
                        self.exit(5, "Неверный пароль или логин. До свидания...")
                    else:
                        return False
            else:
                self.output.error("Сервис аутентификации недоступен. До свидания...")
        except KeyboardInterrupt:
            self.exit(0, "Выход")


class Stdin:
    def __init__(self):
        self.data: str | None = None
        self.wait_for_data_input: bool = False
        self.interrupt_type: int = 0

    def is_empty(self) -> bool:
        return e(self.data)

    def set_default_state(self) -> None:
        self.interrupt_type = 0
        self.wait_for_data_input = False
        self.data = None


class Output(OutputBase, OutputStub):
    @contextmanager
    def make_indent(self, value: int, additional: bool = False) -> bool:
        indent: int = self.indent
        try:
            self.set_indent([0, indent][additional] + value)
            yield True
        finally:
            self.set_indent(indent)

    def set_indent(self, value: int) -> None:
        self.indent_value = value
        self.text_before = self.indent_symbol * value

    def bold(self, value: str) -> str:
        return j((CSI, "1m", value, CSI, "0m"))

    def italic(self, value: str) -> str:
        return value

    def reset_indent(self) -> None:
        self.indent_value = 0
        self.text_before = ""

    @property
    def indent(self) -> int:
        return self.indent_value

    def restore_indent(self) -> None:
        self.set_indent(self.indent_value)

    def init(self) -> None:
        colorama.init()

    def text_color(self, color: str, text: str) -> str:
        return j((color, text, Fore.RESET))

    def text_black(self, text: str) -> str:
        return self.text_color(Fore.BLACK, text)

    def text_white(self, text: str) -> str:
        return self.text_color(Fore.WHITE, text)

    def color_str(
        self,
        color: int,
        text: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> str:
        text_before = text_before or self.text_before
        text_after = text_after or self.text_after
        return j((text_before, color, " ", text, " ", Back.RESET, text_after))

    def color(
        self,
        color: int,
        text: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> None:
        self.write_line(self.color_str(color, text, text_before, text_after))

    def write_line(self, text: str) -> None:
        print(
            jnl(DataTool.map(lambda item: self.text_before + item, text.splitlines()))
        )

    @contextmanager
    def personalized(self):
        pass

    def index(self, index: int, text: str, max_index: int | None = None) -> None:
        indent: str = ""
        if max_index is not None:
            indent = " " * (len(str(max_index)) - len(str(index)))
        if index is None:
            self.write_line(j((indent, text)))
        else:
            self.write_line(j((index, ". ", indent, text)))

    def input(self, caption: str) -> None:
        self.write_line(self.input_str(caption, self.text_before, text_after=":"))

    def input_str(
        self,
        caption: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> str:
        return self.white_str(
            j((Fore.BLACK, caption, Fore.RESET)), text_before, text_after
        )

    def value(self, caption: str, value: str, text_before: str | None = None) -> None:
        text_before = text_before or self.text_before
        self.cyan(caption, text_before, j((": ", value)))

    def get_action_value(
        self, caption: str, value: str, show: bool = True
    ) -> ActionValue:
        if show:
            self.value(caption, value)
        return ActionValue(caption, value)

    def head(self, caption: str) -> None:
        self.cyan(caption)

    def head1(self, caption: str) -> None:
        self.magenta(caption)

    def head2(self, caption: str) -> None:
        self.yellow(self.text_color(Fore.BLACK, caption))

    def new_line(self) -> None:
        print()

    def separated_line(self) -> None:
        self.new_line()

    def error_str(self, caption: str) -> str:
        return self.red_str(caption)

    def error(self, caption: str) -> None:
        self.write_line(self.error_str(caption))

    def notify_str(self, caption: str) -> str:
        return self.yellow_str(caption)

    def notify(self, caption: str) -> None:
        self.write_line(self.notify_str(caption))

    def good_str(self, caption: str) -> str:
        return self.green_str(caption)

    def good(self, caption: str) -> str:
        self.write_line(self.good_str(self.text_white(caption)))

    def green_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.GREEN, text, text_before, text_after)

    def green(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.green_str(text, text_before, text_after))

    def yellow_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.YELLOW, text, text_before, text_after)

    def yellow(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        text_before = text_before or self.text_before
        text_after = text_after or self.text_after
        self.write_line(self.yellow_str(text, text_before, text_after))

    def black_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.BLACK, text, text_before, text_after)

    def black(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.black_str(text, text_before, text_after))

    def white_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.WHITE, text, text_before, text_after)

    def white(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.white_str(text, text_before, text_after))

    def draw_line(
        self, color: str = Back.LIGHTBLUE_EX, char: str = " ", width: int = 80
    ) -> None:
        self.write_line("") if color is None else self.color(color, char * width)

    def line(self) -> None:
        self.new_line()
        self.draw_line(Back.WHITE, self.text_color(Fore.BLACK, "_"), width=128)
        self.new_line()

    def magenta_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.LIGHTMAGENTA_EX, text, text_before, text_after)

    def magenta(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.magenta_str(text, text_before, text_after))

    def cyan(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.cyan_str(text, text_before, text_after))

    def cyan_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.CYAN, text, text_before, text_after)

    def red(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.red_str(text, text_before, text_after))

    def red_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.LIGHTRED_EX, text, text_before, text_after)

    def blue(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.blue_str(text, text_before, text_after))

    def blue_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Back.BLUE, text, text_before, text_after)

    def bright(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> None:
        self.write_line(self.bright_str(text, text_before, text_after))

    def bright_str(
        self, text: str, text_before: str | None = None, text_after: str | None = None
    ) -> str:
        return self.color_str(Style.BRIGHT, text, text_before, text_after)

    @staticmethod
    def get_number(value: int) -> str:
        return CONST.VISUAL.NUMBER_SYMBOLS[value]

    def header(self, caption: str) -> None:
        self.head2(caption)

    @contextmanager
    def make_separated_lines(self) -> bool:
        yield True

    @contextmanager
    def make_loading(self, loading_timeout: float = 1, text: str | None = None) -> None:
        thread: PIHThread | None = None
        try:

            def show_loading() -> None:
                sleep(loading_timeout)
                if nn(thread):
                    self.write_line(
                        js(("", A.CT_V.WAIT, j((text or "Идёт загрузка", "..."))))
                    )

            thread = PIHThread(show_loading)
            self.locked = True
            yield True
        finally:
            self.locked = False
            thread = None

    def write_result(
        self,
        result: Result[T],
        use_index: bool = True,
        item_separator: str = "\n",
        empty_result_text: str = "Не найдено",
        separated_result_item: bool = True,
        label_function: Callable[[Any, int], str | list[str]] | None = None,
        data_label_function: (
            Callable[[int, FieldItem, T, Any], tuple[bool, str]] | None
        ) = None,
        title: str | None = None,
        separated_all: bool = False,
    ) -> None:
        data: list = DataTool.as_list(result.data)
        result_string_list: list[str] | None = None
        if e(data):
            self.new_line()
            self.write_line(empty_result_text)
        else:
            if ne(title):
                self.write_line(self.bold(title))
            with self.make_indent(2, True):
                for index, data_item in enumerate(data):
                    result_string_list = []
                    if use_index and len(data) > 1:
                        result_string_list.append(j((self.text_before, index + 1, ":")))
                    if n(label_function):
                        field: FieldItem
                        for field in result.fields.list:
                            if not field.visible:
                                continue
                            item_data_value: str | None = None
                            if isinstance(data_item, dict):
                                item_data_value = data_item[field.name]
                            elif dataclasses.is_dataclass(data_item):
                                item_data_value = data_item.__getattribute__(field.name)
                            item_data_value = (
                                item_data_value
                                if e(item_data_value)
                                else PIH.DATA.FORMAT.by_formatter_name(
                                    field.data_formatter, item_data_value
                                )
                                or field.data_formatter.format(data=item_data_value)
                            )
                            if e(item_data_value):
                                if data_label_function is None:
                                    continue
                            default_value_label_function: Callable[
                                [int, FieldItem, Result[T], Any], tuple[bool, str]
                            ] = lambda _, field, __, data_value: (
                                True,
                                j((self.bold(field.caption), ": ", data_value)),
                            )
                            result_data_label_function: Callable[
                                [int, FieldItem, T, Any], tuple[bool, str]
                            ] = (data_label_function or default_value_label_function)
                            label_value_result: tuple[bool, str | None] = (
                                result_data_label_function(
                                    index, field, data_item, item_data_value
                                )
                            )
                            label_value: str | None = None
                            if nn(label_value_result[0]):
                                if label_value_result[0] == True:
                                    label_value = label_value_result[1]
                                    if n(label_value) and nn(field.default_value):
                                        label_value = field_item.default_value
                                else:
                                    label_value = default_value_label_function(
                                        None, field, None, item_data_value
                                    )[1]
                            if ne(label_value):
                                result_string_list.append(label_value)
                    else:
                        result_string_list += DataTool.as_list(
                            label_function(data_item, index)
                        )
                    if separated_result_item:
                        self.separated_line()
                    if separated_all:
                        with self.make_separated_lines():
                            for line in result_string_list:
                                self.write_line(line)
                    else:
                        self.write_line(j(result_string_list, item_separator))

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def pih_title(self) -> None:
        self.cyan(self.text_color(Fore.WHITE, "███ ███ █┼█"))
        self.cyan(self.text_color(Fore.WHITE, "█▄█ ┼█┼ █▄█"))
        self.cyan(
            j(
                (
                    self.text_color(Fore.WHITE, "█┼┼ ▄█▄ █┼█"),
                    self.text_color(Fore.BLACK, js(("", PIH.VERSION.value))),
                )
            )
        )
        self.new_line()

    def rpc_service_header(self, host: str, port: int, description: str) -> None:
        self.blue("PIH service")
        self.blue(f"Version: {PIH.VERSION.value}")
        self.green(f"Service host: {host}")
        self.green(f"Service port: {port}")
        self.green(f"Service name: {description}")

    def service_header(self, information: ServiceInformation) -> None:
        self.clear_screen()
        self.new_line()
        self.pih_title()
        self.blue("Service starting...")
        self.new_line()
        self.green(f"Service name: {information.name}")
        with self.make_indent(1):
            if information.standalone and nn(information.standalone_name):
                self.magenta("Standalone")
            if information.isolated:
                self.blue("Isolated")
            self.value("Host", PIH.DATA.FORMAT.donain(information.host))
            self.value("Port", information.port)
            self.value("PID process", information.pid)

    def free_marks(
        self,
        show_guest_marks: bool,
        use_index: bool = False,
        sort_by_tab_number: bool = True,
    ) -> None:
        def sort_function(item: Mark) -> Any:
            return item.TabNumber if sort_by_tab_number else item.GroupName

        self.table_with_caption_first_title_is_centered(
            ResultTool.sort(sort_function, PIH.RESULT.MARK.free_list(show_guest_marks)),
            "Свободные карты доступа:",
            use_index,
        )

    def guest_marks(self, use_index: bool = False) -> None:
        mark_list_result: Result[list[Mark]] = PIH.RESULT.MARK.free_list(True)
        mark_list_result.fields.visible(FIELD_NAME_COLLECTION.GROUP_NAME, False)

        def filter_function(item: Mark) -> bool:
            return EnumTool.get(MarkType, item.type) == MarkType.GUEST

        ResultTool.filter(filter_function, mark_list_result)
        self.table_with_caption_first_title_is_centered(
            mark_list_result, "Гостевые карты доступа:", use_index
        )

    def temporary_candidate_for_mark(self, mark: Mark) -> None:
        self.mark.result(
            Result(FIELD_COLLECTION.ORION.FREE_MARK, [mark]), "Временная карта"
        )

    def free_marks_group_statistics(
        self, use_index: bool = False, show_guest_marks: bool | None = None
    ) -> None:
        self.free_marks_group_statistics_for_result(
            PIH.RESULT.MARK.free_marks_group_statistics(show_guest_marks), use_index
        )

    def free_marks_by_group(self, group: dict, use_index: bool = False) -> None:
        self.free_marks_by_group_for_result(
            PIH.RESULT.MARK.free_marks_by_group_id(group), group, use_index
        )

    def free_marks_group_statistics_for_result(
        self, result: Result, use_index: bool
    ) -> None:
        self.table_with_caption_last_title_is_centered(
            result, "Свободные карты доступа:", use_index
        )

    def free_marks_by_group_for_result(
        self, group: MarkGroup, result: Result, use_index: bool
    ) -> None:
        group_name: str = group.GroupName
        self.table_with_caption_last_title_is_centered(
            result,
            js(
                (
                    "Свободные карты доступа для группы доступа",
                    j((self.b(group_name), ":")),
                )
            ),
            use_index,
        )

    def temporary_marks(
        self,
        use_index: bool = False,
    ) -> None:
        def modify_table(table: PrettyTable, caption_list: list[str]):
            table.align[caption_list[0]] = "c"
            table.align[caption_list[1]] = "c"

        self.table_with_caption(
            PIH.RESULT.MARK.temporary_list(),
            "Список временных карт:",
            use_index,
            modify_table,
        )

    def containers_for_result(self, result: Result, use_index: bool = False) -> None:
        self.table_with_caption(result, "Подразделение:", use_index)

    def table_with_caption_first_title_is_centered(
        self,
        result: Result,
        caption: str,
        use_index: bool = False,
        label_function: Callable = None,
    ) -> None:
        def modify_table(table: PrettyTable, caption_list: list[str]):
            table.align[caption_list[int(use_index)]] = "c"

        self.table_with_caption(
            result, caption, use_index, modify_table, label_function
        )

    def table_with_caption_last_title_is_centered(
        self,
        result: Result,
        caption: str,
        use_index: bool = False,
        label_function: Callable = None,
    ) -> None:
        def modify_table(table: PrettyTable, caption_list: list[str]):
            table.align[caption_list[-1]] = "c"

        self.table_with_caption(
            result, caption, use_index, modify_table, label_function
        )

    def table_with_caption(
        self,
        result: Any,
        caption: str | None = None,
        use_index: bool = False,
        modify_table_function: Callable | None = None,
        label_function: Callable | None = None,
    ) -> None:
        if caption is not None:
            self.cyan(caption)
        is_result_type: bool = isinstance(result, Result)
        field_list = (
            result.fields if is_result_type else ResultTool.unpack_fields(result)
        )
        data: Any = result.data if is_result_type else ResultTool.unpack_data(result)
        if e(data):
            self.error("Не найдено!")
        else:
            if not isinstance(data, list):
                data = [data]
            if len(data) == 1:
                use_index = False
            if use_index:
                field_list.list.insert(0, FIELD_COLLECTION.INDEX)
            caption_list: list = field_list.get_caption_list()

            def create_table(caption_list: list[str]) -> PrettyTable:
                from prettytable.colortable import ColorTable, Themes

                table: ColorTable = ColorTable(caption_list, theme=Themes.OCEAN)
                table.align = "l"
                if use_index:
                    table.align[caption_list[0]] = "c"
                return table

            table: PrettyTable = create_table(caption_list)
            if modify_table_function is not None:
                modify_table_function(table, caption_list)
            for index, item in enumerate(data):
                row_data: list = []
                for field_item_obj in field_list.get_list():
                    field_item: FieldItem = field_item_obj
                    if field_item.visible:
                        if field_item.name == FIELD_COLLECTION.INDEX.name:
                            row_data.append(str(index + 1))
                        elif not isinstance(item, dict):
                            if label_function is not None:
                                modified_item_data = label_function(field_item, item)
                                if modified_item_data is None:
                                    modified_item_data = getattr(item, field_item.name)
                                row_data.append(
                                    DataTool.check(
                                        modified_item_data,
                                        lambda: modified_item_data,
                                        "",
                                    )
                                    if modified_item_data is None
                                    else modified_item_data
                                )
                            else:
                                item_data = getattr(item, field_item.name)
                                row_data.append(
                                    DataTool.check(item_data, lambda: item_data, "")
                                )
                        elif field_item.name in item:
                            item_data = item[field_item.name]
                            if label_function is not None:
                                modified_item_data = label_function(field_item, item)
                                row_data.append(
                                    item_data
                                    if modified_item_data is None
                                    else modified_item_data
                                )
                            else:
                                row_data.append(item_data)
                table.add_row(row_data)
            print(table)
            table.clear()

    def template_users_for_result(self, data: dict, use_index: bool = False) -> None:
        def data_handler(field_item: FieldItem, item: User) -> Any:
            filed_name = field_item.name
            if filed_name == FIELD_NAME_COLLECTION.DESCRIPTION:
                return item.description
            return None

        self.table_with_caption(
            data,
            "Шаблоны для создания аккаунта пользователя:",
            use_index,
            None,
            data_handler,
        )


class Input(InputBase):
    def __init__(
        self, user_input: UserInputBase, mark_input: MarkInputBase, output: OutputBase
    ):
        self.output: OutputBase = output
        self.answer: str | None = None
        if user_input is not None:
            self.user: UserInputBase = user_input
            self.user.parent = self
        if mark_input is not None:
            self.mark: MarkInputBase = mark_input
            self.mark.parent = self

    def input(
        self,
        caption: str | None = None,
        new_line: bool = True,
        check_function: Callable[[str], str] | None = None,
    ) -> str:
        try:
            while True:
                if new_line and caption is not None:
                    self.output.input(caption)
                value: str = (
                    input(self.output.text_before)
                    if new_line
                    else input(self.output.text_before + caption)
                )
                if check_function is not None:
                    value_after: str = check_function(value)
                    if value_after is not None:
                        return value_after
                else:
                    return value
        except KeyboardInterrupt as _:
            raise KeyboardInterrupt()

    def polibase_persons_by_any(
        self, value: str | None = None, title: str | None = None, use_all: bool = False
    ) -> list[PolibasePerson]:
        result: Result[list[PolibasePerson]] = A.R_P.persons_by_any(
            value or self.polibase_person_any(title)
        )
        label_function: Callable[[Any, int], str] | None = (
            (lambda item, _: "Все" if n(item) else item.FullName)
            if len(result.data) > 1
            else None
        )
        if use_all and len(result.data) > 1:
            result.data.append(None)
        polibase_person: PolibasePerson = self.item_by_index(
            "Выберите пользователя, введя индекс", result.data, label_function
        )
        return result.data if n(polibase_person) else [polibase_person]

    def telephone_number(
        self, format: bool = True, telephone_prefix: str = CONST.TELEPHONE_NUMBER_PREFIX
    ) -> str:
        while True:
            self.output.input("Введите номер телефона")
            use_telephone_prefix: bool = telephone_prefix is not None
            telephone_number: str = self.input(telephone_prefix, False)
            if use_telephone_prefix:
                if not telephone_number.startswith(telephone_prefix):
                    telephone_number = telephone_prefix + telephone_number
            check: bool | None = None
            if format:
                telehone_number_after_fix = PIH.DATA.FORMAT.telephone_number(
                    telephone_number, telephone_prefix
                )
                check = PIH.CHECK.telephone_number(telehone_number_after_fix)
                if check and telehone_number_after_fix != telephone_number:
                    telephone_number = telehone_number_after_fix
                    self.output.value("Телефон отформатирован", telephone_number)
            if check or PIH.CHECK.telephone_number(telephone_number):
                return telephone_number
            else:
                self.output.error("Неверный формат номера телефона!")

    def email(self, title: str | None = None) -> str:
        email: str | None = None
        while True:
            email = self.input(title or "Адресс электронная почта")
            if PIH.CHECK.email(email):
                return email
            else:
                self.output.error("Неверный формат адресса электронной почты!")

    def polibase_person_card_registry_folder(
        self, value: str | None = None, title: str | None = None
    ) -> str:
        while True:
            value = value or self.input(
                title or "Введите название папки с картами пациентов"
            )
            if PIH.CHECK.POLIBASE.person_card_registry_folder(value):
                return PIH.DATA.FORMAT.polibase_person_card_registry_folder(value)
            else:
                self.output.error("Неверный формат названия папки с картами пациентов!")
                value = None

    def message(self, caption: str | None = None, prefix: str | None = None) -> str:
        caption = caption or "Введите сообщение"
        self.output.input(caption)
        return (prefix or "") + self.input(prefix, False)

    def description(self) -> str:
        self.output.input("Введите описание")
        return self.input()

    def login(self, check_on_exists: bool = False) -> str:
        login: str | None = None
        while True:
            login = self.input("Введите логин")
            if PIH.CHECK.login(login):
                if check_on_exists and PIH.CHECK.USER.exists_by_login(login):
                    self.output.error("Логин занят!")
                else:
                    return login
            else:
                self.output.error("Неверный формат логина!")

    def indexed_list(
        self,
        caption: str,
        name_list: list[Any],
        caption_list: list[str],
        by_index: bool = False,
    ) -> str:
        return self.item_by_index(
            caption,
            name_list,
            lambda item, index: caption_list[index if by_index else item],
        )

    def indexed_field_list(self, caption: str, list: FieldItemList) -> str:
        name_list = list.get_name_list()
        return self.item_by_index(
            caption, name_list, lambda item, _: list.get_item_by_name(item).caption
        )

    def index(
        self,
        caption: str,
        data: list[Any],
        label_function: Callable[[Any, int], str] | None = None,
        use_zero_index: bool = False,
        use_free_input: bool = False,
        text_after: str | None = None,
    ) -> int | str:
        value: str | None = None
        selected_index: int = -1
        length: int = len(data)
        has_error: bool = False
        zero_index_value: int = int(use_zero_index)
        min_value: int = 1 - zero_index_value
        max_value: int = length - zero_index_value
        index_caption: str = js((caption, "(от", min_value, "до", j((max_value, ")"))))
        while True:
            if not has_error and nn(label_function) and length > 1 or use_free_input:
                for index, item in enumerate(data):
                    self.output.index(
                        (
                            index + 1 - zero_index_value
                            if length > 1 or use_free_input
                            else None
                        ),
                        label_function(item, index),
                        max_value,
                    )
            if length == 1 and not use_free_input:
                return zero_index_value
            selected_index = PIH.DATA.EXTRACT.decimal(
                value := (
                    self.input(index_caption)
                    if n(text_after)
                    else self.input(j((index_caption, text_after)))
                ),
                min_value,
                max_value,
                simple=True,
            )
            if e(selected_index):
                if use_free_input:
                    return value
                selected_index = -1
            try:
                selected_index = int(selected_index) - min_value
                if selected_index >= 0 and selected_index < length:
                    return selected_index
            except ValueError:
                has_error = True
                continue

    def item_by_index(
        self,
        caption: str,
        data: list[Any],
        label_function: Callable[[Any, int], str] | None = None,
        use_zero_index: bool = False,
    ) -> Any:
        return data[self.index(caption, data, label_function, use_zero_index)]

    def tab_number(self, check: bool = True) -> str:
        tab_number: str | None = None
        while True:
            tab_number = self.input("Введите номер карты доступа")
            if check:
                if PIH.CHECK.MARK.tab_number(tab_number):
                    return tab_number
                else:
                    self.output.error("Неправильный формат номера карты доступа")
                    # return None
            else:
                return tab_number

    def password(
        self,
        secret: bool = True,
        check: bool = False,
        settings: PasswordSettings = None,
        is_new: bool = True,
    ) -> str:
        self.output.input("Введите новый пароль" if is_new else "Введите пароль")
        while True:
            value = getpass("") if secret else self.input()
            if not check or PIH.CHECK.password(value, settings):
                return value
            else:
                self.output.error("Пароль не соответствует требованием безопасности")

    def same_if_empty(self, caption: str, src_value: str) -> str:
        value = self.input(caption)
        if value == "":
            value = src_value
        return value

    def name(self) -> str:
        return self.input("Введите часть имени")

    def full_name(self, one_line: bool = False) -> FullName:
        if one_line:
            while True:
                value: str = self.input("Введите полное имя")
                if PIH.CHECK.full_name(value):
                    return FullNameTool.fullname_from_string(
                        PIH.DATA.FORMAT.name(value)
                    )
                else:
                    pass
        else:

            def full_name_part(caption: str) -> str:
                while True:
                    value: str = self.input(caption)
                    value = value.strip()
                    if PIH.CHECK.name(value):
                        return PIH.DATA.FORMAT.name(value)
                    else:
                        pass

            return FullName(
                full_name_part("Введите фамилию"),
                full_name_part("Введите имя"),
                full_name_part("Введите отчество"),
            )

    def yes_no(
        self,
        text: str = " ",
        enter_for_yes: bool = False,
        yes_label: str | None = None,
        no_label: str | None = None,
        yes_checker: Callable[[str], bool] | None = None,
    ) -> bool:
        text = self.output.blue_str(self.output.text_color(Fore.WHITE, text))
        self.output.write_line(
            f"{text}? \n{self.output.green_str(self.output.text_black('Да (1 или Ввод)'))} / {self.output.red_str(self.output.text_black('Нет (Остальное)'), '')}"
            if enter_for_yes
            else f"{text}? \n{self.output.red_str('Да (1)')} / {self.output.green_str(self.output.text_black('Нет (Остальное или Ввод)'), '')}"
        )
        answer: str = self.input()
        answer = answer.lower()
        self.answer = answer
        return (
            answer == "y"
            or answer == "yes"
            or answer == "1"
            or (answer == "" and enter_for_yes)
        )

    def message_for_user_by_login(self, login: str) -> str:
        user: User = PIH.RESULT.USER.by_login(login).data
        if user is not None:
            head_string = f"Здравствуйте, {FullNameTool.to_given_name(user.name)}, "
            self.output.green(head_string)
            message = self.input("Введите сообщениеt: ")
            return head_string + message
        else:
            pass

    def polibase_person_any(self, title: str | None = None) -> str:
        return self.input(
            title or "Введите персональный номер или часть имени пациента"
        )

    def datetime(
        self,
        use_date: bool | None = True,
        use_time: bool | None = True,
        ask_time_input: bool = True,
    ) -> datetime:
        result: datetime = DateTimeTool.now(second=0)
        temp_datetime: datetime = result
        if n(use_date):
            use_date = not self.yes_no(
                js(
                    (
                        "Использовать текущую дату",
                        self.output.bold(
                            DateTimeTool.datetime_to_string(result, CONST.DATE_FORMAT)
                        ),
                    )
                )
            )
        while use_date and True:
            date_value: str | None = self.input(
                js(("Введите дату в формате", self.output.bold("День.Месяц.Год")))
            ).lower()
            date_value = date_value.replace("ю", ".")
            dot_list: int = date_value.split(".")
            dot_count: int = len(dot_list)
            for i in range(dot_count):
                dot_list = ListTool.not_empty_items(
                    DataTool.map(
                        lambda item: str(PIH.DATA.EXTRACT.decimal(item)), dot_list
                    )
                )
            if dot_count == len(dot_list):
                date_value = j(dot_list, ".")
                temp_datetime = PIH.DATA.EXTRACT.datetime(
                    date_value,
                    [CONST.DAY_FORMAT, CONST.YEARLESS_DATE_FORMAT, CONST.DATE_FORMAT][
                        dot_count - 1
                    ],
                )
                if nn(temp_datetime):
                    if dot_count >= 1:
                        result = result.replace(day=temp_datetime.day)
                    if dot_count >= 2:
                        result = result.replace(month=temp_datetime.month)
                    if dot_count >= 3:
                        result = result.replace(year=temp_datetime.year)
                    break
        if ask_time_input and self.yes_no(js("Ввести время")):
            if n(use_time):
                use_time = not self.yes_no(
                    js(
                        (
                            "Использовать текущее время",
                            self.output.bold(
                                DateTimeTool.datetime_to_string(
                                    result, CONST.SECONDLESS_TIME_FORMAT
                                )
                            ),
                        )
                    )
                )
            while use_time and True:
                time_value: str | None = self.input(
                    js(("Введите время в формате", self.output.bold("Час:Минуты")))
                )
                dot_list: int = time_value.split(":")
                dot_count: int = len(dot_list)
                for i in range(dot_count):
                    dot_list = ListTool.not_empty_items(
                        DataTool.map(
                            lambda item: str(PIH.DATA.EXTRACT.decimal(item)), dot_list
                        )
                    )
                if dot_count == len(dot_list):
                    time_value = j(dot_list, ":")
                    temp_datetime = PIH.DATA.EXTRACT.datetime(
                        time_value,
                        [CONST.HOUR_TIME_FORMAT, CONST.SECONDLESS_TIME_FORMAT][
                            dot_count - 1
                        ],
                    )
                    if nn(temp_datetime):
                        if dot_count >= 1:
                            result = result.replace(hour=temp_datetime.hour)
                        if dot_count >= 2:
                            result = result.replace(minute=temp_datetime.minute)
                        break
        else:
            result = result.replace(minute=0, hour=0)
        return result

    def choose_file(self, use_search_request: bool | None = None) -> File:
        search_request: str | None = None
        if n(use_search_request):
            use_search_request = self.yes_no("Использвать поиск")
        file_list: list[File] | None = None
        with self.output.make_loading(1, "Идет загрузка файлов. Ожидайте"):
            file_list = PIH.RESULT.FILES.get(
                name=(
                    (search_request := self.input("Введите поисковый запрос"))
                    if use_search_request
                    else None
                )
            ).data
            if e(file_list):
                self.output.error(
                    js(
                        (
                            "Файл с именем",
                            esc(search_request),
                            "не найден",
                        )
                    )
                )
                file_list = PIH.RESULT.FILES.get().data

            def label_function(file: File, _) -> str:
                title_list: list[str] = file.title.split(SPLITTER)
                if len(title_list) == 3:
                    return j(
                        (
                            PIH.output.bold(title_list[0].upper()),
                            ": ",
                            title_list[-1],
                            " (",
                            title_list[-2],
                            ")",
                        )
                    )
                return PIH.output.bold(title_list[1])

            file: File = self.item_by_index(
                "Выберите файл",
                file_list,
                label_function,
            )
            return file


class MarkInput(MarkInputBase):
    def __init__(self, input: Input | None = None):
        self.parent = input

    def free(self, group: MarkGroup | None = None) -> Mark:
        result_mark: Mark | None = None
        mark: Mark | None = None
        free_mark_list_result: Result[list[Mark]] | None = None
        free_mark_list: list[Mark] | None = None
        length: int = 0
        while True:
            if n(group):
                if self.parent.yes_no(
                    "Выбрать группы доступа для карты доступа, введя имени пользователя из этой группы"
                ):
                    free_mark_list_result = PIH.RESULT.MARK.by_name(self.parent.name())
                    free_mark_list: list[Mark] = free_mark_list_result.data
                    length = len(free_mark_list)
                    if length > 0:
                        if length > 1:
                            self.parent.output.table_with_caption_first_title_is_centered(
                                free_mark_list_result, "Найденные пользователи:", True
                            )
                        mark = self.parent.item_by_index(
                            "Выберите группу доступа", free_mark_list
                        )
                        group = DataTool.fill_data_from_source(MarkGroup(), mark)
                    else:
                        self.parent.output.error(
                            "Персона с введенным именем не найдена"
                        )
                else:
                    free_mark_list_result = PIH.RESULT.MARK.free_marks_group_statistics(
                        False
                    )
                    free_mark_list: list[Mark] = free_mark_list_result.data
                    length = len(free_mark_list_result)
                    if length > 0:
                        if length > 1:
                            self.parent.output.free_marks_group_statistics_for_result(
                                free_mark_list_result, True
                            )
                        group = self.parent.item_by_index(
                            "Выберите группу доступа", free_mark_list_result.data
                        )
                        result_mark = Mark()
                        result_mark.GroupName = group.GroupName
                        result_mark.GroupID = group.GroupID
                    else:
                        self.parent.output.error("Свободный карт доступа нет!")
                        return None
            else:
                free_mark_list_result = PIH.RESULT.MARK.free_marks_by_group_id(
                    group.GroupID
                )
                length = len(free_mark_list_result)
                if length > 0:
                    if length > 1:
                        self.parent.output.free_marks_by_group_for_result(
                            group, free_mark_list_result, True
                        )
                    result_mark = self.parent.item_by_index(
                        "Выберите карту доступа", free_mark_list_result.data
                    )
                    if nn(mark):
                        result_mark.DivisionID = mark.DivisionID
                        result_mark.DivisionName = mark.DivisionName
                    return result_mark
                else:
                    self.parent.output.error(
                        f"Нет свободных карт для группы доступа '{group.GroupName}'!"
                    )
                    return self.free()

    def person_division(self, use_empty_division: bool = True) -> PersonDivision:
        division_list: list[PersonDivision] = PIH.RESULT.MARK.person_divisions().data
        if use_empty_division:
            division_list.insert(0, PersonDivision(0, "Без подразделения"))
        return self.parent.item_by_index(
            "Выберите подразделение для персоны, которой принадлежит карта доступа",
            division_list,
            lambda item, _: item.name,
        )

    def by_name(self) -> Mark:
        self.parent.output.head2("Введите имя персоны")
        result: Result[list[Mark]] = None
        while result is None:
            try:
                result = PIH.RESULT.MARK.by_name(self.parent.name())
            except NotFound as error:
                self.parent.output.error(error.get_details())
        self.parent.output.mark.result(result, "Карты доступа", True)
        return self.parent.item_by_index(
            "Выберите карту доступа, введя индекс", result.data
        )

    def by_any(self, value: str | None = None) -> Mark:
        result: Result[list[Mark]] = None
        while result is None:
            try:
                result = PIH.RESULT.MARK.by_any(value or self.any())
            except NotFound as error:
                self.parent.output.error(error.get_details())
        self.parent.output.mark.result(result, "Карты доступа", True)
        return self.parent.item_by_index(
            "Выберите карту доступа, введя индексу", result.data
        )

    def any(self) -> str:
        return self.parent.input(
            "Введите часть имени или табельный номер держателя карты"
        )


class UserInput(UserInputBase):
    def __init__(self, input: Input = None):
        self.parent = input

    def container(self) -> UserBase:
        result: Result[list[UserBase]] = PIH.RESULT.USER.containers()
        self.parent.output.containers_for_result(result, True)
        return self.parent.item_by_index(
            "Выберите контейнер пользователя, введя индекс", result.data
        )

    def by_name(self) -> User:
        result: Result[list[User]] = PIH.RESULT.USER.by_name(self.parent.name())
        result.fields = FIELD_COLLECTION.AD.USER_NAME
        self.parent.output.table_with_caption(result, "Список пользователей", True)
        return self.parent.item_by_index(
            "Выберите пользователя, введя индекс", result.data
        )

    def title_any(self, title: str | None = None) -> str:
        return self.parent.input(
            title or "Введите логин, часть имени или другой поисковый запрос"
        )

    def by_any(
        self,
        value: str | None = None,
        active: bool | None = None,
        title: str | None = None,
        select_all: bool = False,
    ) -> list[User]:
        result: Result[list[User]] = PIH.RESULT.USER.by_any(
            value or self.title_any(title), active
        )
        if select_all and len(result.data) > 1:
            result.data.append(None)
        result_data: User | None = self.parent.item_by_index(
            "Выберите пользователя, введя индекс",
            result.data,
            (
                (
                    lambda item, _: (
                        "Все"
                        if A.D.is_none(item)
                        else j((item.name, " (", item.samAccountName, ")"))
                    )
                )
                if len(result.data) > 1
                else None
            ),
        )
        return result.data if A.D.is_none(result_data) else [result_data]

    def telephone_number(
        self,
        value: str | None = None,
        active: bool | None = None,
        title: str | None = None,
    ) -> User | None:
        try:
            return self.by_any(value, active, title)
        except NotFound as _:
            return None

    def template(self) -> User:
        result: Result[list[User]] = PIH.RESULT.USER.template_list()
        self.parent.output.template_users_for_result(result, True)
        return self.parent.item_by_index(
            "Выберите шаблон пользователя, введя индекс", result.data
        )

    def search_attribute(self) -> str:
        return self.parent.indexed_field_list(
            "Выберите по какому критерию искать, введя индекс",
            FIELD_COLLECTION.AD.SEARCH_ATTRIBUTE,
        )

    def search_value(self, search_attribute: str) -> str:
        field_item = FIELD_COLLECTION.AD.SEARCH_ATTRIBUTE.get_item_by_name(
            search_attribute
        )
        return self.parent.input(f"Введите {field_item.caption.lower()}")

    def generate_password(
        self, once: bool = False, settings: PasswordSettings = PASSWORD.SETTINGS.DEFAULT
    ) -> str:
        def internal_generate_password(settings: PasswordSettings = None) -> str:
            return PasswordTools.generate_random_password(
                settings.length,
                settings.special_characters,
                settings.order_list,
                settings.special_characters_count,
                settings.alphabets_lowercase_count,
                settings.alphabets_uppercase_count,
                settings.digits_count,
                settings.shuffled,
            )

        while True:
            password = internal_generate_password(settings)
            if once or self.parent.yes_no(f"Использовать пароль {password}", True):
                return password
            else:
                pass

    def generate_login(
        self,
        full_name: FullName,
        ask_for_remove_inactive_user_if_login_is_exists: bool = True,
        ask_for_use: bool = True,
    ) -> str:
        login_list: list[str] = []
        inactive_user_list: list[User] = []
        login_is_exists: bool = False

        def show_user_which_login_is_exists_and_return_user_if_it_inactive(
            login_string: str,
        ) -> User:
            user: User = PIH.RESULT.USER.by_login(login_string).data
            is_active: bool = PIH.CHECK.USER.active(user)
            self.parent.output.error(
                f"Логин '{login_string}' занят {'активным' if is_active else 'неактивным'} пользователем: {user.name}"
            )
            self.parent.output.new_line()
            return user if not is_active else None

        login: FullName = NamePolicy.convert_to_login(full_name)
        login_string: str = FullNameTool.fullname_to_string(login, "")
        login_list.append(login_string)
        need_enter_login: bool = False

        def remove_inactive_user_action():
            login_string: str | None = None
            need_enter_login: bool = False
            if self.parent.yes_no(
                "Удалить неактивных пользователей, чтобы освободить логин", True
            ):
                user_for_remove: User = self.parent.item_by_index(
                    "Выберите пользователя для удаления, выбрав индекс",
                    inactive_user_list,
                    lambda user, _: f"{user.name} ({user.samAccountName})",
                )
                self.parent.output.new_line()
                self.parent.output.value(
                    "Пользователь для удаления", user_for_remove.name
                )
                if self.parent.yes_no("Удалить неактивного пользователя", True):
                    if PIH.ACTION.USER.remove(user_for_remove):
                        self.parent.output.good("Удален")
                        login_string = user_for_remove.samAccountName
                        inactive_user_list.remove(user_for_remove)
                    else:
                        self.parent.output.error("Ошибка")
                else:
                    need_enter_login = True
            else:
                need_enter_login = True
            return need_enter_login, login_string

        if PIH.CHECK.USER.exists_by_login(login_string):
            user: User = show_user_which_login_is_exists_and_return_user_if_it_inactive(
                login_string
            )
            if user is not None:
                inactive_user_list.append(user)
            login_alt: FullName = NamePolicy.convert_to_alternative_login(login)
            login_string = FullNameTool.fullname_to_string(login_alt, "")
            login_is_exists = login_string in login_list
            if not login_is_exists:
                login_list.append(login_string)
            if login_is_exists or PIH.CHECK.USER.exists_by_login(login_string):
                if not login_is_exists:
                    user = (
                        show_user_which_login_is_exists_and_return_user_if_it_inactive(
                            login_string
                        )
                    )
                    if user is not None:
                        inactive_user_list.append(user)
                login_reversed: FullName = NamePolicy.convert_to_reverse_login(login)
                login_is_exists = login_string in login_list
                login_string = FullNameTool.fullname_to_string(login_reversed, "")
                if not login_is_exists:
                    login_list.append(login_string)
                if login_is_exists or PIH.CHECK.USER.exists_by_login(login_string):
                    login_last: FullName = NamePolicy.convert_to_last_login(login)
                    login_string = FullNameTool.fullname_to_string(login_last, "")
                    if not login_is_exists:
                        user = show_user_which_login_is_exists_and_return_user_if_it_inactive(
                            login_string
                        )
                        if user is not None:
                            inactive_user_list.append(user)
                    if (
                        ask_for_remove_inactive_user_if_login_is_exists
                        and len(inactive_user_list) > 0
                    ):
                        need_enter_login, login_string = remove_inactive_user_action()
                    if need_enter_login:
                        while True:
                            login_string = self.parent.login()
                            if PIH.CHECK.USER.exists_by_login(login_string):
                                show_user_which_login_is_exists_and_return_user_if_it_inactive(
                                    login_string
                                )
                            else:
                                break
        if (
            not need_enter_login
            and ask_for_remove_inactive_user_if_login_is_exists
            and len(inactive_user_list) > 0
        ):
            need_enter_login, login_string = remove_inactive_user_action()
            if need_enter_login:
                return self.generate_login(full_name, False)
        else:
            if ask_for_use and not self.parent.yes_no(
                f"Использовать логин '{login_string}' для аккаунта пользователя", True
            ):
                login_string = self.parent.login(True)

        return login_string


class NamePolicy:
    @staticmethod
    def get_first_letter(name: str) -> str:
        letter = name[0]
        if letter.lower() == "ю":
            return "yu"
        return translit(letter, "ru", reversed=True).lower()

    @staticmethod
    def convert_to_login(full_name: FullName) -> FullName:
        return FullName(
            NamePolicy.get_first_letter(full_name.last_name),
            NamePolicy.get_first_letter(full_name.first_name),
            NamePolicy.get_first_letter(full_name.middle_name),
        )

    @staticmethod
    def convert_to_alternative_login(login_list: FullName) -> FullName:
        return FullName(
            login_list.first_name, login_list.middle_name, login_list.last_name
        )

    @staticmethod
    def convert_to_last_login(login_list: FullName) -> FullName:
        return FullName(
            login_list.first_name, login_list.last_name, login_list.middle_name
        )

    @staticmethod
    def convert_to_reverse_login(login_list: FullName) -> FullName:
        return FullName(
            login_list.middle_name, login_list.first_name, login_list.last_name
        )


class PIH:
    NAME: str = "pih"
    NAME_ALT: str = "пих"

    def __init__(
        self,
        input: InputBase | None = None,
        output: OutputBase | None = None,
        session: SessionBase | None = None,
    ):
        if n(output):
            output = Output(UserOutput(), MarkOutput())
            PIH.output: Output = output
        else:
            self.output: Output = output
        if n(input):
            input = Input(UserInput(), MarkInput(), PIH.output)
            PIH.input: Input = input
        else:
            self.input: Input = input
        if n(session):
            PIH.session: Session = Session(input, output)
        else:
            self.session: Session = session

    class VERSION:
        value: str = "1.49914"

        @staticmethod
        def need_update() -> bool:
            return False
            # return importlib.util.find_spec(PIH.NAME) is not None and PIH.VERSION.value < PIH.VERSION.remote()

    class INPUT_WAIT:
        NAME: str = "RecipientWaitingForInput"

        @staticmethod
        def _get_name(group_name: str, recipient: str) -> str:
            return j((group_name, recipient), SPLITTER)

        @staticmethod
        def add(group_name: str, recipient: str, timeout: int) -> bool:
            return PIH.ACTION.DATA_STORAGE.value(
                RecipientWaitingForInput(
                    group_name, timeout, recipient, PIH.DATA.now()
                ),
                PIH.INPUT_WAIT._get_name(group_name, recipient),
                PIH.INPUT_WAIT.NAME,
            )

        @staticmethod
        def remove(group_name: str, recipient: str) -> bool:
            return PIH.ACTION.DATA_STORAGE.value(
                None,
                PIH.INPUT_WAIT._get_name(group_name, recipient),
                PIH.INPUT_WAIT.NAME,
            )

        @staticmethod
        def has(group_name: str, recipient: str) -> bool:
            def extractor(data: Any | None) -> RecipientWaitingForInput | None:
                if n(data):
                    return None
                result: RecipientWaitingForInput = DataTool.fill_data_from_source(
                    RecipientWaitingForInput(), data
                )
                result.timestamp = DateTimeTool.datetime_from_string(result.timestamp)
                return result

            result: RecipientWaitingForInput | None = PIH.RESULT.DATA_STORAGE.value(
                PIH.INPUT_WAIT._get_name(group_name, recipient),
                extractor,
                PIH.INPUT_WAIT.NAME,
            ).data
            return nn(result) and (
                n(result.timeout)
                or (DateTimeTool.now() - result.timestamp).seconds < result.timeout
            )

    class ERROR:
        notify_about_error: bool = True

        @staticmethod
        def service_host_is_unchanachable(host: str) -> None:
            PIH.output.error(
                f"Sorry, but service can't be start, cause service host is unchangeble.\n You are trying to start service on {PIH.DATA.FORMAT.donain(PIH.OS.host())}, but service must be started on {PIH.DATA.FORMAT.donain(host)}"
            )

        @staticmethod
        def create_error_header(details: str) -> str:
            return f"\nВерсия: {PIH.VERSION.value}\nПользователь: {PIH.OS.get_login()}\nКомпьютер: {PIH.OS.host()}\n{details}"

        @staticmethod
        @contextmanager
        def detect(final_action: Callable[[None], None] | None = None):
            try:
                yield True
            except Exception as error:
                PIH.ERROR.global_except_hook(error)
            finally:
                if nn(final_action):
                    final_action()

        @staticmethod
        def wrap(action: Callable[[Any], Any]) -> Callable[[Any], Any]:
            def internal_action() -> Any:
                with PIH.ERROR.detect():
                    return action

            return internal_action()

        @staticmethod
        @contextmanager
        def detect_interruption(message: str | None = None):
            try:
                yield True
            except KeyboardInterrupt as _:
                DataTool.check_not_none(message, lambda: PIH.output.error(message))

        @staticmethod
        def rpc_error_handler(
            details: str,
            code: tuple,
            description: ServiceRoles,
            command: ServiceCommands,
            source_details: str | None = None,
        ) -> None:
            if isinstance(command, ServiceCommands):
                if code == StatusCode.UNAVAILABLE:
                    if PIH.ERROR.notify_about_error:
                        PIH.output.error("Error:")
                        PIH.output.set_indent(1)
                        for item in details.splitlines():
                            parts: list[str] = item.split(": ")
                            if len(parts) > 1:
                                PIH.output.value(
                                    parts[0], PIH.output.red_str(j(parts[1:], "; "))
                                )
                            else:
                                PIH.output.write_line(parts[0])
                        PIH.output.set_indent(0)
                    return
                elif (
                    code == StatusCode.DEADLINE_EXCEEDED
                    or details.lower().find("stream removed") != -1
                ):
                    return
                else:
                    if PIH.ERROR.notify_about_error:
                        PIH.LOG.debug(
                            PIH.ERROR.create_error_header(details),
                            LogMessageFlags.ERROR,
                        )
            raise Error(source_details, code) from None

        @staticmethod
        def global_except_hook(error: BaseException) -> None:
            exctype, value, __traceback__ = type(error), error, error.__traceback__
            details_list: list[str] = []
            for item in value.args:
                if isinstance(item, str):
                    details_list.append(item)
            details: str = jnl(traceback.format_exception(value))
            if PIH.ERROR.notify_about_error:
                PIH.LOG.debug(
                    PIH.ERROR.create_error_header(details), LogMessageFlags.ERROR
                )
            sys.__excepthook__(exctype, value, __traceback__)

        sys.excepthook = (
            lambda exception_type, exception, traceback: PIH.ERROR.global_except_hook(
                exception
            )
        )

        class POLIBASE:

            @staticmethod
            def create_not_found_error(
                title: str | None, value: str, start: str = "Пациент"
            ) -> str:
                title = title or "поисковым запросом"
                return NotFound(f'{start} с {title} "{value}" не найден', value)

        class USER:
            @staticmethod
            def get_not_found_error(title: str, active: bool, value: str) -> str:
                start: str | None = None
                if n(active):
                    start = "Пользователь"
                elif active:
                    start = "Активный пользователь"
                else:
                    start = "Неактивный пользователь"
                return NotFound(f"{start} с {title} '{value}' не найден", value)

    class UPDATE:
        @staticmethod
        def for_service(
            service_role_or_information: ServiceRoles | ServiceDescription,
            modules: list[str] | None = None,
            pih_update: bool = False,
            modules_update: bool = True,
            show_output: bool = True,
        ) -> bool:
            if PIH.session.is_standalone:
                return True
            description: ServiceDescription = ServiceRoles.description(
                service_role_or_information
            )
            result: bool = True
            if pih_update:
                remote_executor_command_list: list[str] = (
                    PIH.EXECUTOR.create_command_for_start_service(description, True)
                )
                command_list: list[str] = (
                    remote_executor_command_list
                    + PIH.UPDATE.command_for_module(PIH.NAME, None)
                )
                complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                    command_list, show_output
                )
                result = complete_process.returncode == 0
            return result and PIH.UPDATE.modules(modules, modules_update, show_output)

        @staticmethod
        def modules(
            value: list[str] | None, update: bool = True, show_output: bool = True
        ) -> bool:
            result: bool = True
            if ne(value) and update:
                installed_module_list: list[str] = {
                    pkg.key.lower() for pkg in pkg_resources.working_set
                }
                for module_name in [item.lower() for item in value]:
                    if module_name not in installed_module_list:
                        result = result and PIH.UPDATE.install_module(
                            module_name, show_output=show_output
                        )
                        if result:
                            pkg_resources.working_set.add_entry(module_name)
                        else:
                            break
            return result

        @staticmethod
        def command_for_module(
            module_name: str, version: str | None = None, local: bool = True
        ) -> list[str]:
            return [
                CONST.PYTHON.EXECUTOR if local else CONST.PYTHON.EXECUTOR_ALIAS,
                "-m",
                CONST.PYTHON.PYPI,
                CONST.PYTHON.COMMAND.INSTALL,
            ] + DataTool.check_not_none(
                version, lambda: [j((module_name, "==", version))], [module_name, "-U"]
            )

        @staticmethod
        def module_exists(module_name: str) -> bool:
            complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                [
                    CONST.PYTHON.EXECUTOR,
                    "-m",
                    CONST.PYTHON.PYPI,
                    CONST.PYTHON.COMMAND.SHOW,
                    module_name,
                ],
                True,
                True,
            )
            return complete_process.stdout.find(module_name) != -1

        @staticmethod
        def localy(version: str | None = None, show_output: bool = False) -> bool:
            return PIH.UPDATE.install_module(PIH.NAME, version, show_output)

        @staticmethod
        def install_module(
            module_name: str,
            version: str | None = None,
            show_output: bool = False,
            host: str | None = None,
            host_is_linux: bool | None = None,
        ) -> bool | None:
            name: str = jp(("module", host, module_name, version))
            if name not in _cache:
                result: bool | None = False
                is_local: bool = e(host) or PIH.OS.host_is_local(host)
                command_list: list[str] = PIH.UPDATE.command_for_module(
                    module_name, version, is_local
                )
                if not host_is_linux or n(host_is_linux):
                    complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                        (
                            command_list
                            if is_local
                            else PIH.EXECUTOR.create_command_for_psexec(
                                command_list, host, interactive=show_output
                            )
                        ),
                        show_output,
                    )
                    result = PIH.EXECUTOR.extract_returncode(
                        complete_process, check_on_success=True
                    )
                if host_is_linux or (n(host_is_linux) and n(result)):
                    command_list[0] = CONST.PYTHON.EXECUTOR3
                    result = (
                        str(PIH.RESULT.SSH.execute(js(command_list), host).data).find(
                            js(("Successfully installed", module_name))
                        )
                        != -1
                    )
                _cache[name] = result
            return _cache[name]

        @staticmethod
        def remotely(host: str, show_output: bool = False) -> bool:
            remote_executor_command_list: list[str] = (
                PIH.EXECUTOR.create_command_for_psexec(host)
            )
            command_list: list[str] = (
                remote_executor_command_list + PIH.UPDATE.command_for_module()
            )
            complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                command_list, show_output
            )
            returncode = complete_process.returncode
            return returncode == 0

    class SETTINGS:
        @staticmethod
        def to_datetime(value: SETTINGS) -> datetime:
            return PIH.DATA.CONVERT.settings_to_datetime(value)

        @staticmethod
        def to_datetime_list(value: SETTINGS) -> list[datetime]:
            return PIH.DATA.CONVERT.settings_to_datetime_list(value)

        @staticmethod
        def set(settings_item: SETTINGS | str, value: Any) -> bool:
            return PIH.ACTION.SETTINGS.set(settings_item, value)

        @staticmethod
        def set_default(settings_item: SETTINGS) -> bool:
            return PIH.ACTION.SETTINGS.set_default(settings_item)

        @staticmethod
        def get(settings_item: SETTINGS | str) -> Any:
            if isinstance(settings_item, str):
                return PIH.RESULT.SETTINGS.get_by_name(settings_item).data
            return PIH.RESULT.SETTINGS.get(settings_item).data

        @staticmethod
        def init() -> None:
            for setting_item in SETTINGS:
                if setting_item.value.auto_init:
                    PIH.SETTINGS.set_default(setting_item)

        @staticmethod
        def find(value: str | None) -> list[SETTINGS]:
            result: list[SETTINGS] = []
            for item in SETTINGS:
                if (
                    n(value)
                    or StringTool.contains(item.name, value)
                    or StringTool.contains(item.value.key_name, value)
                    or StringTool.contains(item.value.description, value)
                ):
                    result.append(item)
            return result

        class WORKSTATION:
            @staticmethod
            def shutdown_time() -> datetime:
                return PIH.DATA.CONVERT.settings_to_datetime(
                    SETTINGS.WORKSTATION_SHUTDOWN_TIME
                )

            @staticmethod
            def reboot_time() -> datetime:
                return PIH.DATA.CONVERT.settings_to_datetime(
                    SETTINGS.WORKSTATION_REBOOT_TIME
                )

        class USER:
            @staticmethod
            def use_cache() -> bool:
                return PIH.SETTINGS.get(SETTINGS.USER_USE_CACHE)

            @staticmethod
            def get_section(login: str) -> str:
                return j((login, "_settings"))

            @staticmethod
            def set(login: str, name: str, value: Any) -> bool:
                return PIH.ACTION.DATA_STORAGE.value(
                    value, name, PIH.SETTINGS.USER.get_section(login)
                )

            @staticmethod
            def get(
                login: str,
                name: str,
                class_type_holder: Any | Callable[[Any], Any] | None = None,
            ) -> Any:
                return PIH.RESULT.DATA_STORAGE.value(
                    name, class_type_holder, PIH.SETTINGS.USER.get_section(login)
                ).data

        class INDICATION:
            @staticmethod
            def ct_notification_start_time() -> list[datetime]:
                return PIH.DATA.CONVERT.settings_to_datetime(
                    SETTINGS.INDICATION_CT_NOTIFICATION_START_TIME
                )

        class RESOURCE:
            @staticmethod
            def site_check_certificate_start_time() -> datetime:
                return PIH.DATA.CONVERT.settings_to_datetime(
                    SETTINGS.RESOURCE_MANAGER_CHECK_SITE_CERTIFICATE_START_TIME
                )

            @staticmethod
            def site_check_free_space_perion_in_minutes() -> int:
                return PIH.SETTINGS.get(
                    SETTINGS.RESOURCE_MANAGER_CHECK_SITE_FREE_SPACE_PERIOD_IN_MINUTES
                )

        class POLIBASE:
            @staticmethod
            def test_recipient(sender: Any) -> str | None:
                if sender == CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.CALL_CENTRE.value:
                    return PIH.SETTINGS.get(
                        SETTINGS.POLIBASE_PERSON_VISIT_NOTIFICATION_TEST_TELEPHONE_NUMBER
                    )
                if sender == CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.MARKETER.value:
                    return PIH.SETTINGS.get(
                        SETTINGS.POLIBASE_PERSON_REVIEW_NOTIFICATION_TEST_TELEPHONE_NUMBER
                    )
                return None

            class REVIEW_NOTIFICATION:
                @staticmethod
                def start_time() -> datetime:
                    return PIH.DATA.CONVERT.settings_to_datetime(
                        SETTINGS.POLIBASE_PERSON_REVIEW_NOTIFICATION_START_TIME
                    )

                @staticmethod
                def is_on() -> bool:
                    return PIH.SETTINGS.get(
                        SETTINGS.POLIBASE_PERSON_REVIEW_NOTIFICATION_IS_ON
                    )

                @staticmethod
                def day_delta() -> int:
                    return PIH.SETTINGS.get(
                        SETTINGS.POLIBASE_PERSON_REVIEW_NOTIFICATION_DAY_DELTA
                    )

                @staticmethod
                def notification_text(
                    person: PolibasePerson, notification_confirmed: bool
                ) -> str:
                    return str(
                        PIH.SETTINGS.get(
                            SETTINGS.POLIBASE_PERSON_REVIEW_NOTIFICATION_TEXT_FOR_CONFIRMED_NOTIFICATION
                            if notification_confirmed
                            else SETTINGS.POLIBASE_PERSON_REVIEW_NOTIFICATION_TEXT
                        )
                    ).format(name=FullNameTool.to_given_name(person))

            class VISIT:
                @staticmethod
                def offer_telegram_bot_url_text(person_full_name: str) -> str:
                    return str(
                        PIH.SETTINGS.get(
                            SETTINGS.POLIBASE_PERSON_TAKE_TELEGRAM_BOT_URL_TEXT
                        )
                    ).format(name=FullNameTool.to_given_name(person_full_name))

    class EXECUTOR:
        @staticmethod
        def kill_process_by_port(value: int) -> bool | None:
            pid: str = (
                str(
                    PIH.EXECUTOR.execute(
                        j(
                            (
                                'netstat -aon | findstr /rc:"\<0.0.0.0:',
                                value,
                                '\>" | findstr "LISTENING"',
                            )
                        ),
                        show_output=True,
                        capture_output=True,
                        command_as_text=True,
                        as_shell=True,
                    ).stdout
                )
                .strip()
                .split(" ")[-1]
            )

            if e(pid):
                return None
            return PIH.EXECUTOR.kill_process(
                int(pid),
                via_standart_tools=False,
                show_output=True,
            )

        @staticmethod
        def psping(
            address_or_ip: str,
            host: str | None = None,
            count: int | None = None,
            check_all: bool = True,
        ) -> bool:
            count = count or 4
            ping_command: list[str] = [
                PIH.EXECUTOR.get_executor_path(CONST.PSTOOLS.PS_PING),
                CONST.PSTOOLS.ACCEPTEULA,
                "-4",
                "-n",
                str(count),
                address_or_ip,
            ]
            complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                DataTool.check_not_none(
                    host,
                    lambda: PIH.EXECUTOR.create_command_for_psexec(
                        ping_command,
                        host,
                        PIH.DATA.VARIABLE.ENVIRONMENT.value(LINK.ADMINISTRATOR_LOGIN),
                        PIH.DATA.VARIABLE.ENVIRONMENT.value(
                            LINK.ADMINISTRATOR_PASSWORD
                        ),
                        True,
                    ),
                    ping_command,
                ),
                True,
                True,
            )

            if complete_process.returncode == 0:
                result: str = complete_process.stdout
                lost_marker: str = "Lost = "
                index: int = result.find(lost_marker)
                if index != -1:
                    lost_count: int = int(
                        result[index + len(lost_marker) : result.find(" (", index)]
                    )
                    if check_all:
                        return lost_count == 0
                    return lost_count < count
            return False

        @staticmethod
        def python_path(host: str | None = None) -> str:
            search_pattern: str = CONST.PYTHON.SEARCH_PATTERN
            if PIH.OS.host_is_local(host):
                host = None
            variable_list: list[str] = if_else(
                n(host),
                lambda: PIH.OS.environment_variable(WINDOWS.ENVIROMENT_VARIABLES.PATH),
                lambda: PIH.EXECUTOR.execute(
                    PIH.EXECUTOR.create_command_for_psexec(
                        [
                            CONST.POWERSHELL.NAME,
                            j(
                                (
                                    WINDOWS.ENVIROMENT_COMMAND,
                                    WINDOWS.ENVIROMENT_VARIABLES.PATH,
                                ),
                                ":",
                            ),
                        ],
                        host,
                        interactive=None,
                    ),
                    True,
                    True,
                ).stdout,
            ).split(";")
            for variable_item in variable_list:
                index: int = variable_item.find(search_pattern)
                if (
                    index != -1
                    and len(variable_item) - (index + len(search_pattern)) <= 4
                ):
                    return os.path.join(
                        variable_item,
                        PathTool.add_extension(
                            CONST.PYTHON.EXECUTOR, FILE.EXTENSION.EXE
                        ),
                    )
            return None

        @staticmethod
        def python_version(
            host: str | None = None, host_is_linux: bool | None = None
        ) -> str | None:
            result: str | None = None
            if not host_is_linux or n(host_is_linux):
                command: list[str] = [
                    CONST.PYTHON.EXECUTOR_ALIAS,
                    CONST.PYTHON.COMMAND.VERSION,
                ]
                if PIH.OS.host_is_local(host):
                    host = None
                complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                    if_else(
                        n(host),
                        command,
                        lambda: PIH.EXECUTOR.create_command_for_psexec(
                            command, host, interactive=True
                        ),
                    ),
                    True,
                    True,
                )
            if host_is_linux or (
                n(host_is_linux)
                and n(
                    PIH.EXECUTOR.extract_returncode(
                        complete_process, check_on_success=True
                    )
                )
            ):
                result = PIH.RESULT.SSH.execute(
                    js((CONST.PYTHON.EXECUTOR3, CONST.PYTHON.COMMAND.VERSION)), host
                ).data
            else:
                stderr: str = complete_process.stderr
                if ne(stderr):
                    if (
                        stderr.find(
                            js(("could not start", CONST.PYTHON.EXECUTOR_ALIAS))
                        )
                        != -1
                    ):
                        return None
                result = str(complete_process.stdout)
            return j(str(result).strip().split(" ")[1:])

        @staticmethod
        def get_disk_statistics_list(host: str) -> list[DiskStatistics]:
            output: str = PIH.EXECUTOR.execute(
                js(
                    (
                        CONST.POWERSHELL.NAME,
                        "Get-WmiObject -Class win32_logicalDisk -ComputerName",
                        host,
                    )
                ),
                True,
                True,
                as_shell=True,
            ).stdout
            result: list[DiskStatistics] = []
            delimiter: str = ": "
            delimiter_length: int = len(delimiter)
            disk_statistics: DiskStatistics | None = None
            for line in ListTool.not_empty_items(output.splitlines()):
                line: str = line
                if line.startswith("DeviceID"):
                    disk_statistics = DiskStatistics(
                        line[line.find(delimiter) + delimiter_length : -1]
                    )
                    result.append(disk_statistics)
                if line.startswith("FreeSpace"):
                    disk_statistics.free_space = DataTool.if_not_empty(
                        line[line.find(delimiter) + delimiter_length :],
                        lambda item: int(item),
                        0,
                    )
                if line.startswith("Size"):
                    disk_statistics.size = DataTool.if_not_empty(
                        line[line.find(delimiter) + delimiter_length :],
                        lambda item: int(item),
                        0,
                    )
            return result

        @staticmethod
        def get_users_logged_on(host: str, active: bool | None = True) -> list[str]:
            def get_login_list(complete_process: CompletedProcess) -> set[str]:
                result: set[str] = set()
                output: str = complete_process.stdout.decode(
                    WINDOWS.CHARSETS.ALTERNATIVE
                )
                # print(host, nl(), output)
                for line in output.splitlines()[1:]:
                    line = line.lower()
                    if (
                        n(active)
                        or (
                            active
                            and (
                                line.find("active") != -1 or line.find("активно") != -1
                            )
                        )
                        or (
                            not active
                            and (line.find("disc") != -1 or line.find("диск") != -1)
                        )
                    ):
                        result.add(line.split(" ")[1])
                return result

            result: set[str] = set()
            result |= get_login_list(
                PIH.EXECUTOR.execute(
                    ["query", "user", "/server:" + host], True, True, False
                )
            )
            result |= get_login_list(
                PIH.EXECUTOR.execute(
                    PIH.EXECUTOR.create_command_for_psexec(
                        ["query", "user", "/server"],
                        host,
                        interactive=None,
                        run_from_system_account=True,
                    ),
                    True,
                    True,
                    False,
                )
            )
            return list(result)

        @staticmethod
        def stop_windows_service(name: str, workstation_name: str) -> bool:
            output: str = PIH.EXECUTOR.execute(
                PIH.EXECUTOR.create_command_for_psexec(
                    ["sc", "stop", name],
                    workstation_name,
                    interactive=True,
                    run_from_system_account=True,
                ),
                True,
                True,
            ).stdout
            return output.find("3  STOP_PENDING") != -1

        @staticmethod
        def start_windows_service(name: str, workstation_name: str) -> bool:
            output: str = PIH.EXECUTOR.execute(
                PIH.EXECUTOR.create_command_for_psexec(
                    ["sc", "start", name],
                    workstation_name,
                    interactive=True,
                    run_from_system_account=True,
                ),
                True,
                True,
            ).stdout
            return output.find("2  START_PENDING") != -1

        @staticmethod
        def check_for_windows_service_running(name: str, workstation_name: str) -> bool:
            output: str = PIH.EXECUTOR.execute(
                PIH.EXECUTOR.create_command_for_psexec(
                    ["sc", "query", name], workstation_name, interactive=True
                ),
                True,
                True,
            ).stdout
            return output.find("4  RUNNING") != -1

        @staticmethod
        def ping(
            address_or_ip: str,
            host: str | None = None,
            count: int = 1,
            timeout: int = 100,
        ):
            command_list: list[str] = [
                "ping",
                "-4",
                address_or_ip,
                "-n",
                str(count),
                "-w",
                str(timeout),
            ]
            result: CompletedProcess = PIH.EXECUTOR.execute(
                PIH.EXECUTOR.create_command_for_psexec(
                    command_list, host, interactive=True
                ),
                True,
                True,
            )
            output: str = result.stdout
            return result.returncode == 0 and output.count("(TTL)") < count

        @staticmethod
        def get_executor_path(executor_name: str) -> str:
            return PIH.PATH.adapt_for_windows(
                PIH.PATH.join(PATHS.WS.PATH, CONST.PSTOOLS.NAME, executor_name)
            )

        @staticmethod
        def create_command_for_executor(
            executor_name: str,
            command: list[str],
            login: str | None = None,
            password: str | None = None,
            use_raw_login: bool = False,
        ) -> list[str]:
            login = if_else(
                e(login),
                None,
                lambda: login if use_raw_login else PIH.DATA.FORMAT.login(login),
            )
            return (
                [
                    PIH.PATH.path(PIH.EXECUTOR.get_executor_path(executor_name)),
                    CONST.PSTOOLS.NO_BANNER,
                    CONST.PSTOOLS.ACCEPTEULA,
                ]
                + if_else(e(login), [], lambda: ["-u", login])
                + if_else(e(password), [], lambda: ["-p", password])
                + command
            )

        @staticmethod
        def create_command_for_powershell(
            command: list[str],
            host: str | None = None,
            login: str | None = None,
            password: str | None = None,
            interactive: bool | None = False,
            run_from_system_account: bool = False,
            run_with_elevetion: bool = False,
            allow_use_local_host: bool = True,
            use_raw_host_name: bool = False,
            use_raw_login: bool = False,
        ) -> list[str]:
            if command[0].lower() != CONST.POWERSHELL.NAME:
                command.insert(0, CONST.POWERSHELL.NAME)
            return PIH.EXECUTOR.create_command_for_psexec(
                command,
                host,
                login,
                password,
                interactive,
                run_from_system_account,
                run_with_elevetion,
                allow_use_local_host,
                use_raw_host_name,
                use_raw_login,
            )

        @staticmethod
        def create_command_for_psexec(
            command: list[str],
            host: str | None = None,
            login: str | None = None,
            password: str | None = None,
            interactive: bool | None = False,
            run_from_system_account: bool = False,
            run_with_elevetion: bool = False,
            allow_use_local_host: bool = True,
            use_raw_host_name: bool = False,
            use_raw_login: bool = False,
        ) -> list[str]:
            command_prefix: list[str] = DataTool.check_not_none(
                interactive, lambda: [["-d", "-i"][interactive]], []
            )
            local_host: bool = allow_use_local_host and PIH.OS.host_is_local(host)
            if not local_host:
                if ne(host):
                    command_prefix.append(
                        PIH.DATA.FORMAT.host(
                            host, use_default_domain=not use_raw_host_name
                        )
                    )
                login = login or PIH.DATA.VARIABLE.ENVIRONMENT.value(
                    LINK.ADMINISTRATOR_LOGIN
                )
                password = password or PIH.DATA.VARIABLE.ENVIRONMENT.value(
                    LINK.ADMINISTRATOR_PASSWORD
                )
            if run_from_system_account:
                command_prefix.append("-s")
            if run_with_elevetion:
                command_prefix.append("-h")
            return PIH.EXECUTOR.create_command_for_executor(
                CONST.PSTOOLS.PS_EXECUTOR,
                command_prefix + command,
                login,
                password,
                use_raw_login,
            )

        @staticmethod
        def create_command_for_start_service(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
            interactive: bool | None = False,
            host: str | None = None,
        ) -> list[str]:
            description: ServiceDescription = ServiceRoles.description(
                service_role_or_information
            )
            python_command: list[str] = (
                [description.pyton_executor_path or CONST.PYTHON.EXECUTOR_ALIAS]
                if n(description.standalone_name)
                else []
            )
            is_local: bool = PIH.OS.host_is_local(host or description.host)

            def local_action(value: Any) -> Any | None:
                return if_else(is_local, None, value)

            login: str | None = local_action(
                DataTool.check_not_none(
                    description.login,
                    lambda: PIH.DATA.FORMAT.variable(
                        description.login, from_environment=True
                    ),
                )
            )
            password: str | None = local_action(
                DataTool.check_not_none(
                    description.password,
                    lambda: PIH.DATA.FORMAT.variable(
                        description.password, from_environment=True
                    ),
                )
            )
            interactive = local_action(interactive)
            return (
                python_command
                if is_local
                else PIH.EXECUTOR.create_command_for_psexec(
                    python_command,
                    host
                    or local_action(PIH.SERVICE.get_host(service_role_or_information)),
                    login,
                    password,
                    interactive,
                    description.run_from_system_account,
                    False,
                )
            )

        @staticmethod
        def execute(
            command: list[str] | str,
            show_output: bool = False,
            capture_output: bool = False,
            command_as_text: bool = True,
            as_shell: bool = False,
        ) -> CompletedProcess:
            if show_output:
                if capture_output:
                    process_result = subprocess.run(
                        command,
                        capture_output=True,
                        text=command_as_text,
                        shell=as_shell,
                    )
                else:
                    process_result = subprocess.run(command, text=command_as_text)
            else:
                print(command)
                process_result = subprocess.run(
                    command, stdout=DEVNULL, stderr=STDOUT, text=command_as_text
                )
            return process_result

        @staticmethod
        def extract_result(value: CompletedProcess) -> str:
            return str(value.stdout).strip()

        @staticmethod
        def extract_returncode(
            value: CompletedProcess, check_on_success: bool = False
        ) -> int | bool | None:
            returncode: int = value.returncode
            return (
                True
                if returncode == 0
                else (
                    None
                    if returncode in [2, 2250, 2120]
                    else False if check_on_success else returncode
                )
            )

        @staticmethod
        def execute_for_result(
            command: list[str] | str,
            show_output: bool = False,
            capture_output: bool = True,
            command_as_text: bool = True,
            as_shell: bool = False,
        ) -> str:
            return PIH.EXECUTOR.extract_result(
                PIH.EXECUTOR.execute(
                    command, show_output, capture_output, command_as_text, as_shell
                )
            )

        @staticmethod
        def execute_python(command: list[str] | str, host: str) -> CompletedProcess:
            return PIH.EXECUTOR.execute(
                PIH.EXECUTOR.create_command_for_psexec(
                    [
                        CONST.PYTHON.EXECUTOR_ALIAS,
                        CONST.PYTHON.COMMAND.FLAG,
                        j(command, ";") if isinstance(command, list) else command,
                    ],
                    host,
                    interactive=True,
                ),
                show_output=True,
                capture_output=True,
            )

        @staticmethod
        def execute_python_localy(
            text: str,
            parameters: dict[str, Any] | None = None,
            stdout_redirect: bool = True,
            catch_exceptions: bool = False,
            use_default_stdout: bool = False,
        ) -> str | None:
            result_parameters: dict[str, Any] = globals()
            if nn(parameters):
                for key, value in parameters.items():
                    result_parameters[key] = value
            if "self" not in result_parameters:
                result_parameters["self"] = OutputStub()
            if "self" in result_parameters:
                if use_default_stdout:
                    OutputStub().set_to(result_parameters["self"])

            def action() -> None:
                try:
                    exec(
                        text,
                        globals(),
                        result_parameters,
                    )
                except Exception as exception:
                    if catch_exceptions:
                        raise exception

            if stdout_redirect:
                stdout = StringIO()
                with redirect_stdout(stdout):
                    action()
                    return stdout.getvalue()
            else:
                action()
            return None

        @staticmethod
        def execute_python_for_result(command: list[str] | str, host: str) -> str:
            return PIH.EXECUTOR.extract_result(
                PIH.EXECUTOR.execute_python(command, host)
            )

        @staticmethod
        def kill_process(
            name_or_pid: str | int,
            host: str | None = None,
            via_standart_tools: bool = True,
            show_output: bool = False,
        ) -> bool:
            local: bool = PIH.OS.host_is_local(host)
            if via_standart_tools:
                is_string: bool = isinstance(name_or_pid, str)
                command: list[str] = ["taskkill"]
                if not local:
                    command += ["/s", host]
                return (
                    PIH.EXECUTOR.execute(
                        command
                        + [
                            "/t",
                            "/f",
                            "/im" if is_string else "/pid",
                            (
                                PIH.PATH.add_extension(name_or_pid, FILE.EXTENSION.EXE)
                                if is_string
                                else str(name_or_pid)
                            ),
                        ],
                        show_output,
                    ).returncode
                    < 2
                )

            return (
                PIH.EXECUTOR.execute(
                    PIH.EXECUTOR.create_command_for_executor(
                        CONST.PSTOOLS.PS_KILL_EXECUTOR,
                        (
                            [str(name_or_pid)]
                            if local
                            else [host or PIH.OS.host(), "-t", str(name_or_pid)]
                        ),
                    ),
                    show_output,
                    capture_output=True,
                    as_shell=True,
                ).returncode
                == 0
            )

        @staticmethod
        def process_is_exists(
            pid: int,
            host: str | None = None,
            login: str | None = None,
            password: str | None = None,
        ) -> str:
            command_list: list[str] = [
                "tasklist",
                "/fi",
                f"pid eq {pid}",
                "/fo",
                "list",
            ]
            login = PIH.DATA.FORMAT.login(
                login or PIH.DATA.VARIABLE.ENVIRONMENT.value(LINK.ADMINISTRATOR_LOGIN)
            )
            password = password or PIH.DATA.VARIABLE.ENVIRONMENT.value(
                LINK.ADMINISTRATOR_PASSWORD
            )
            if ne(host):
                command_list += ["/s", host]
                command_list += ["/u", login]
                command_list += ["/p", password]
            output: str = (
                bytes(
                    PIH.EXECUTOR.execute(
                        command_list, True, True, command_as_text=False
                    ).stdout
                )
                .decode(WINDOWS.CHARSETS.ALTERNATIVE)
                .lower()
            )
            return output.find("pid") != -1

        @staticmethod
        def kill_python_process(host: str, via_standart_tools: bool) -> bool:
            return PIH.EXECUTOR.kill_process(
                CONST.PYTHON.EXECUTOR, host, via_standart_tools
            )

        @staticmethod
        def _ws_action(value: str, host: str, show_output: bool = False) -> bool:
            return (
                PIH.EXECUTOR.execute(
                    PIH.EXECUTOR.create_command_for_psexec(
                        ["shutdown", value, "/t", "0"], host
                    ),
                    show_output,
                ).returncode
                == 0
            )

        @staticmethod
        def ws_reboot(host: str, show_output: bool = False) -> bool:
            return PIH.EXECUTOR._ws_action("/r", host, show_output)

        @staticmethod
        def ws_shutdown(host: str, show_output: bool = False) -> bool:
            return PIH.EXECUTOR._ws_action("/s", host, show_output)

    class EVENT:
        @staticmethod
        def send(
            value: Events,
            parameters: tuple[Any] | Any | None = None,
            flags: int | None = None,
            ignore_send_once: bool = False,
        ) -> bool:
            if not ignore_send_once and BM.has(
                EnumTool.get(value).flags, LogMessageFlags.SEND_ONCE
            ):
                if PIH.CHECK.EVENTS.has_by_key(value, parameters):
                    return False

            def internal_send_command(
                command_name: str, parameters: dict, flags: int | None
            ) -> None:
                try:
                    PIH.SERVICE.call_command(
                        ServiceCommands.send_event, (command_name, parameters, flags)
                    )
                except Error as error:
                    PIH.output.error("Log send error")

            PIH.LOG.executor.submit(
                PIH.ERROR.wrap(internal_send_command),
                value.name,
                PIH.EVENT.BUILDER.create_parameters_map(
                    value, DataTool.as_list(parameters)
                ),
                flags,
            )
            return True

        @staticmethod
        def mri_filter_was_changed() -> None:
            PIH.EVENT.send(
                Events.MRI_CHILLER_FILTER_WAS_CHANGED,
                (
                    PIH.DATA.MATERIALIZED_RESOURCES.get_count(
                        MATERIALIZED_RESOURCES.TYPES.CHILLER_FILTER
                    ),
                ),
            )

        @staticmethod
        def computer_was_started(name: str) -> None:
            PIH.EVENT.send(Events.COMPUTER_WAS_STARTED, (name,))

        @staticmethod
        def server_was_started(name: str) -> None:
            PIH.EVENT.send(Events.SERVER_WAS_STARTED, (name,))

        @staticmethod
        def get_parameter(
            event: Events, parameters: dict[str, Any], parameter_name: str | None = None
        ) -> Any | dict[str, Any]:
            parameters_map: dict[str, Any] = PIH.EVENT.BUILDER.create_parameters_map(
                event, parameters
            )
            return DataTool.check_not_none(
                parameter_name, lambda: parameters_map[parameter_name], parameters_map
            )

        class BUILDER:
            @staticmethod
            def create_parameters_map(
                event: Events,
                parameters: tuple[Any] | None = None,
                check_for_parameters_count: bool = True,
            ) -> dict:
                event_description: EventDescription = EnumTool.get(event)
                parameter_pattern_list: list = DataTool.as_list(
                    event_description.params
                )
                parameters = parameters or ()
                if check_for_parameters_count and len(parameter_pattern_list) > len(
                    parameters
                ):
                    raise Exception(
                        "Income parameter list length is less that parameter list length of command"
                    )
                result: dict[str, Any] = {}
                for index, parameter_pattern_item in enumerate(parameter_pattern_list):
                    if index < len(parameters):
                        parameter_pattern: ParamItem = parameter_pattern_item
                        value: Any | None = parameters[index]
                        if nn(value):
                            result[parameter_pattern.name] = value
                    else:
                        break
                return result

            @staticmethod
            def create_event(
                event: Events,
                paramters: Any | None = None,
                parameters_getter: Callable[[None], tuple[Any]] | None = None,
                default_value: tuple[Any] | Any | None = None,
                check_all: bool = False,
            ) -> Events | tuple[Events, tuple[Any]]:
                return DataTool.check_not_none(
                    paramters,
                    lambda: (event, parameters_getter()),
                    event if n(default_value) else (event, default_value),
                    check_all,
                )

            @staticmethod
            def by_key(
                value: Events | None, parameters: tuple[Any] | Any
            ) -> tuple[Events, tuple[Any]]:
                event_description: EventDescription = EnumTool.get(value)
                key_len: int = len(
                    DataTool.filter(lambda item: item.key, event_description.params)
                )
                if len(parameters) != len(event_description.params):
                    if key_len == len(parameters):
                        result_parameters: list[Any] = []
                        index: int = 0
                        for item in event_description.params:
                            result_parameters.append(
                                parameters[index] if item.key else None
                            )
                            if item.key:
                                index += 1
                    parameters = result_parameters
                return (
                    value,
                    (
                        parameters
                        if key_len == 0
                        else DataTool.map(
                            lambda item: item[1] if item[0].key else None,
                            list(zip(event_description.params, parameters)),
                        )
                    ),
                )

            @staticmethod
            def polibase_person_with_inaccessable_email_was_detected(
                person: PolibasePerson | None = None,
                registrator_person: PolibasePerson | None = None,
                actual: bool = False,
            ) -> tuple[Events, tuple[Any]] | Events:
                def get_information() -> tuple[Any]:
                    workstation_name: str = "<не определён>"
                    workstation_description: str = "<не определён>"
                    if actual:
                        try:
                            user: User = PIH.RESULT.USER.by_polibase_pin(
                                registrator_person.pin
                            ).data
                            workstation: Workstation = (
                                PIH.RESULT.get_first_item(
                                    PIH.RESULT.WORKSTATION.by_login(user.samAccountName)
                                )
                                or PIH.RESULT.WORKSTATION.by_name(
                                    CONST.TEST.WORKSTATION_MAME
                                ).data
                            )
                            if nn(workstation):
                                workstation_name = workstation.name
                                workstation_description = workstation.description
                        except NotFound as _:
                            pass
                    return (
                        person.FullName,
                        person.pin,
                        person.email,
                        registrator_person.FullName,
                        workstation_name,
                        workstation_description,
                    )

                event: Events = (
                    Events.POLIBASE_PERSON_WITH_INACCESSABLE_EMAIL_WAS_DETECTED
                )
                return PIH.EVENT.BUILDER.create_event(
                    event,
                    registrator_person,
                    get_information,
                    DataTool.check_not_none(person, lambda: (None, person.pin)),
                )

            @staticmethod
            def polibase_person_duplication_was_detected(
                person: PolibasePerson | None = None,
                duplicated_person: PolibasePerson | None = None,
                registrator_person: PolibasePerson | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                event: Events = Events.POLIBASE_PERSON_DUPLICATION_WAS_DETECTED

                def get_information() -> tuple[Any]:
                    return (
                        person.FullName,
                        person.pin,
                        duplicated_person.pin,
                        duplicated_person.pin,
                        registrator_person.FullName,
                    )

                return PIH.EVENT.BUILDER.create_event(event, person, get_information)

            @staticmethod
            def polibase_person_email_was_added(
                value: PolibasePerson | None = None,
                value_for_search: PolibasePerson | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.POLIBASE_PERSON_EMAIL_WAS_ADDED,
                    value,
                    lambda: (value.FullName, value.pin, value.email),
                    DataTool.check_not_none(
                        value_for_search, lambda: (None, value_for_search.pin)
                    ),
                )

            @staticmethod
            def ask_for_polibase_person_email(
                value: PolibasePerson | None = None,
                localy: bool = True,
                secret: int | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.ASK_FOR_POLIBASE_PERSON_EMAIL,
                    value,
                    lambda: (value.FullName, value.pin, localy, randrange(100000)),
                    None if n(secret) else (None, None, None, secret),
                )

            @staticmethod
            def indication_device_was_registered(
                value: IndicationDevice | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.INDICATION_DEVICES_WAS_REGISTERED,
                    value,
                    lambda: (value.name, value.description, value.ip_address),
                )

            @staticmethod
            def service_was_started(
                information: ServiceInformation | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.SERVICE_WAS_STARTED,
                    information,
                    lambda: (
                        information.name,
                        information.host,
                        information.port,
                        information.pid,
                        information,
                    ),
                )

            @staticmethod
            def action_was_done(
                action: Actions | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.ACTION_WAS_DONE,
                    action,
                    lambda: (
                        None,
                        EnumTool.get(action).name,
                    ),
                )

            @staticmethod
            def chiller_temperature_alert_was_fired() -> Events:
                return PIH.EVENT.BUILDER.create_event(
                    Events.MRI_CHILLER_TEMPERATURE_ALERT_WAS_FIRED
                )

            @staticmethod
            def chiller_temperature_alert_was_resolved() -> Events:
                return PIH.EVENT.BUILDER.create_event(
                    Events.MRI_CHILLER_TEMPERATURE_ALERT_WAS_RESOLVED
                )

            @staticmethod
            def polibase_person_set_card_registry_folder(
                name: str | None = None,
                person: PolibasePerson | None = None,
                registrator: PolibasePerson | None = None,
                set_by_polibase: bool = True,
            ) -> Events | tuple[Events, tuple[Any]]:
                person_pin: int | None = None if n(person) else person.pin
                if set_by_polibase:
                    return PIH.EVENT.BUILDER.create_event(
                        Events.CARD_REGISTRY_FOLDER_WAS_SET_FOR_POLIBASE_PERSON,
                        (name, person, registrator),
                        lambda: (
                            person_pin,
                            (
                                None
                                if n(name)
                                else PIH.DATA.FORMAT.polibase_person_card_registry_folder(
                                    name
                                )
                            ),
                            None if n(registrator) else registrator.FullName,
                            None if n(registrator) else registrator.pin,
                        ),
                    )
                else:
                    return PIH.EVENT.BUILDER.create_event(
                        Events.CARD_REGISTRY_FOLDER_WAS_SET_NOT_FROM_POLIBASE_FOR_POLIBASE_PERSON,
                        (person_pin,),
                        lambda: (person_pin,),
                    )

            @staticmethod
            def polibase_person_set_suitable_card_registry_folder(
                name: str | None = None,
                person_or_pin: PolibasePerson | int | None = None,
                registrator: PolibasePerson | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.CARD_REGISTRY_SUITABLE_FOLDER_WAS_SET_FOR_POLIBASE_PERSON,
                    (name, person_or_pin, registrator),
                    lambda: (
                        DataTool.if_not_empty(
                            person_or_pin,
                            lambda person: PIH.RESULT.POLIBASE._person_pin(person),
                        ),
                        (
                            None
                            if n(name)
                            else PIH.DATA.FORMAT.polibase_person_card_registry_folder(
                                name
                            )
                        ),
                        None if n(registrator) else registrator.FullName,
                        None if n(registrator) else registrator.pin,
                    ),
                )

            @staticmethod
            def card_registry_folder_was_registered(
                name: str | None = None,
                place_a: int | None = None,
                place_b: int | None = None,
                place_c: int | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                if nn(name):
                    name = PIH.DATA.FORMAT.polibase_person_card_registry_folder(name)
                return PIH.EVENT.BUILDER.create_event(
                    Events.CARD_REGISTRY_FOLDER_WAS_REGISTERED,
                    name,
                    lambda: (name, place_a, place_b, place_c),
                )

            @staticmethod
            def card_registry_folder_start_card_sorting(
                name: str | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.CARD_REGISTRY_FOLDER_START_CARD_SORTING,
                    name,
                    lambda: (name,),
                )

            @staticmethod
            def card_registry_folder_complete_card_sorting(
                name: str | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.CARD_REGISTRY_FOLDER_COMPLETE_CARD_SORTING,
                    name,
                    lambda: (
                        PIH.DATA.FORMAT.polibase_person_card_registry_folder(name),
                    ),
                )

            staticmethod

            def chiller_was_turned_off() -> Events:
                return PIH.EVENT.BUILDER.create_event(Events.MRI_CHILLER_WAS_TURNED_OFF)

            @staticmethod
            def chiller_was_turned_on() -> Events:
                return PIH.EVENT.BUILDER.create_event(Events.MRI_CHILLER_WAS_TURNED_ON)

            @staticmethod
            def service_was_stopped(
                information: ServiceInformationBase | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.SERVICE_WAS_STOPPED,
                    information,
                    lambda: (information.name, information),
                )

            @staticmethod
            def polibase_persons_barcodes_old_format_were_detected(
                person_pin_list: list[int] | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.POLIBASE_PERSONS_WITH_OLD_FORMAT_BARCODE_WAS_DETECTED,
                    person_pin_list,
                    lambda: (person_pin_list,),
                )

            @staticmethod
            def polibase_person_barcodes_new_format_were_created(
                person_pin_list: list[int] | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.POLIBASE_PERSON_BARCODES_WITH_OLD_FORMAT_WERE_CREATED,
                    person_pin_list,
                    lambda: (person_pin_list,),
                )

            @staticmethod
            def polibase_person_was_created(
                value: PolibasePerson | None = None,
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.POLIBASE_PERSON_WAS_CREATED,
                    value,
                    lambda: (value.FullName, value.pin, value),
                )

            @staticmethod
            def mail_to_polibase_person_was_sent(
                id: int | None = None, person_pin: int | None = None
            ) -> Events | tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.MAIL_TO_POLIBASE_PERSON_WAS_SENT,
                    (id, person_pin),
                    lambda: (id, person_pin),
                )

            @staticmethod
            def polibase_person_was_updated(
                value: PolibasePerson | None = None,
            ) -> tuple[Events, tuple[Any]]:
                return PIH.EVENT.BUILDER.create_event(
                    Events.POLIBASE_PERSON_WAS_UPDATED,
                    value,
                    lambda: (value.FullName, value.pin, value),
                )

        @staticmethod
        def polibase_person_visit_was_registered(value: PolibasePersonVisitDS) -> None:
            PIH.EVENT.send(
                Events.POLIBASE_PERSON_VISIT_WAS_REGISTERED,
                (
                    value.FullName,
                    (
                        "Предзапись"
                        if value.pin == POLIBASE.PRERECORDING_PIN
                        else value.pin
                    ),
                    value,
                ),
            )

        @staticmethod
        def resource_accessible(resource: ResourceStatus, at_first_time: bool) -> None:
            PIH.EVENT.send(
                Events.RESOURCE_ACCESSABLE, (resource.name, resource, at_first_time)
            )

        @staticmethod
        def resource_inaccessible(
            resource: ResourceStatus,
            at_first_time: bool,
            reason: ResourceInaccessableReasons | None = None,
        ) -> None:
            reason_string: str = ""
            reason_name: str | None = None
            if ne(reason):
                reason_string = js(("Причина:", reason.value))
                reason_name = reason.name
            PIH.EVENT.send(
                Events.RESOURCE_INACCESSABLE,
                (resource.name, resource, at_first_time, reason_string, reason_name),
            )

        @staticmethod
        def polibase_person_visit_notification_was_registered(
            visit: PolibasePersonVisitDS,
            notification: PolibasePersonVisitNotificationDS,
        ) -> None:
            PIH.EVENT.send(
                Events.POLIBASE_PERSON_VISIT_NOTIFICATION_WAS_REGISTERED,
                (
                    visit.FullName,
                    (
                        "Предзапись"
                        if visit.pin == POLIBASE.PRERECORDING_PIN
                        else visit.pin
                    ),
                    notification,
                ),
            )

        @staticmethod
        def login() -> None:
            login: str = PIH.session.get_login()
            user: User = PIH.RESULT.USER.by_login(login).data
            PIH.EVENT.send(Events.LOG_IN, (user.name, login, PIH.OS.host()))

        @staticmethod
        def whatsapp_message_received(message: WhatsAppMessage) -> None:
            PIH.EVENT.send(Events.WHATSAPP_MESSAGE_RECEIVED, (message,))

        @staticmethod
        def new_file_detected(path: str) -> None:
            PIH.EVENT.send(Events.NEW_FILE_DETECTED, (PIH.PATH.path(path),))

        @staticmethod
        def new_mail_message_was_received(value: NewMailMessage) -> None:
            PIH.EVENT.send(
                Events.NEW_EMAIL_MESSAGE_WAS_RECEIVED,
                (value.mailbox_address, value.subject, value.from_, value),
            )

        @staticmethod
        def new_polibase_scanned_document_detected(
            value: PolibaseDocument,
        ) -> None:
            PIH.EVENT.send(
                Events.NEW_POLIBASE_DOCUMENT_DETECTED,
                (value.polibase_person_pin, value.file_path, value.document_type, 0),
            )

        @staticmethod
        def new_polibase_scanned_document_processed(file_path: str) -> None:
            event_ds: EventDS | None = one(
                PIH.RESULT.EVENTS.get(
                    Events.NEW_POLIBASE_DOCUMENT_DETECTED, (None, file_path)
                )
            )
            if nn(event_ds):
                parameters: dict[str, Any] = event_ds.parameters
                PIH.EVENT.send(
                    Events.NEW_POLIBASE_DOCUMENT_DETECTED,
                    (
                        parameters[PARAM_ITEMS.PERSON_PIN.name],
                        file_path,
                        parameters[PARAM_ITEMS.DOCUMENT_NAME.name],
                        1,
                    ),
                )

        @staticmethod
        def start_session() -> None:
            argv: list[str] = PIH.session.argv
            argv_str: str = ""
            if ne(argv):
                argv_str = js(argv)
                argv_str = f"({argv_str})"
            login: str = PIH.session.get_login()
            user: User = PIH.RESULT.USER.by_login(login).data
            PIH.EVENT.send(
                Events.SESSION_STARTED,
                (
                    user.name,
                    login,
                    f"{PIH.session.file_name} {argv_str}",
                    f"{PIH.VERSION.value}",
                    PIH.OS.host(),
                ),
            )

        @staticmethod
        def backup_robocopy_job_was_started(
            name: str, job_status: RobocopyJobStatus
        ) -> None:
            PIH.EVENT.send(
                Events.BACKUP_ROBOCOPY_JOB_WAS_STARTED, (name, job_status.pid)
            )

        @staticmethod
        def backup_robocopy_job_was_completed(
            name: str, job_status: RobocopyJobStatus
        ) -> None:
            status: int = job_status.last_status
            is_live: bool = job_status.pid > 0
            status_string: str = "live job" if is_live else str(status)
            pid_string: str = str(job_status.pid) if is_live else "not live job"
            if status >= ROBOCOPY.ERROR_CODE_START:
                status_string += " (есть ошибки)"
            PIH.EVENT.send(
                Events.BACKUP_ROBOCOPY_JOB_WAS_COMPLETED,
                (name, status_string, status, pid_string),
            )

        @staticmethod
        def service_is_inaccessable_and_will_be_restarted(
            information: ServiceInformationBase,
        ) -> None:
            PIH.EVENT.send(
                Events.SERVICE_IS_INACCESIBLE_AND_WILL_BE_RESTARTED,
                (information.name, information),
            )

        @staticmethod
        def service_was_not_started(
            information: ServiceInformation, error: str
        ) -> None:
            PIH.EVENT.send(
                Events.SERVICE_WAS_NOT_STARTED,
                (
                    information.name,
                    information.host,
                    information.port,
                    error,
                    information,
                ),
            )

        @staticmethod
        def hr_notify_about_new_employee(login: User) -> None:
            user: User = PIH.RESULT.USER.by_login(login, True, False).data
            hr_user: User = ResultTool.get_first_item(
                PIH.RESULT.USER.by_job_position(AD.JobPositions.HR)
            )
            PIH.EVENT.send(
                Events.HR_NOTIFY_ABOUT_NEW_EMPLOYEE,
                (FullNameTool.to_given_name(hr_user.name), user.name, user.mail),
            )

        @staticmethod
        def it_notify_about_create_user(
            login: str, password: str, additional_information: str
        ) -> None:
            it_user_list: list[User] = PIH.RESULT.USER.by_job_position(
                AD.JobPositions.IT
            ).data
            me_user_login: str = PIH.session.get_login()
            it_user_list = DataTool.filter(
                lambda user: user.samAccountName != me_user_login, it_user_list
            )
            it_user: User = it_user_list[0]
            user: User = PIH.RESULT.USER.by_login(login).data
            PIH.EVENT.send(
                Events.IT_NOTIFY_ABOUT_CREATE_USER,
                (
                    user.name,
                    user.description,
                    user.samAccountName,
                    password,
                    user.telephoneNumber,
                    user.mail,
                    additional_information,
                ),
            )
            PIH.EVENT.send(
                Events.IT_TASK_AFTER_CREATE_USER,
                (
                    FullNameTool.to_given_name(it_user.name),
                    user.name,
                    user.mail,
                    password,
                    additional_information,
                ),
            )

        @staticmethod
        def it_notify_about_create_person(
            full_name: FullName,
            email_address: str,
            password: str,
            description: str,
            telephone_number: str,
        ) -> None:
            it_user_list: list[User] = PIH.RESULT.USER.by_job_position(
                AD.JobPositions.IT
            ).data
            me_user_login: str = PIH.session.get_login()
            it_user_list = DataTool.filter(
                lambda user: user.samAccountName != me_user_login, it_user_list
            )
            it_user: User = it_user_list[0]
            PIH.EVENT.send(
                Events.IT_NOTIFY_ABOUT_CREATE_PERSON,
                (
                    FullNameTool.fullname_to_string(full_name),
                    email_address,
                    description,
                    password,
                    telephone_number,
                ),
            )
            PIH.EVENT.send(
                Events.IT_TASK_AFTER_CREATE_PERSON,
                (
                    FullNameTool.to_given_name(it_user.name),
                    FullNameTool.fullname_to_string(full_name),
                    email_address,
                    password,
                ),
            )

        @staticmethod
        def it_notify_about_create_mark(
            full_name: str | FullName,
            temporary: bool = False,
            tab_number: str | None = None,
        ) -> None:
            name: str = (
                FullNameTool.fullname_to_string(full_name)
                if isinstance(full_name, FullName)
                else full_name
            )
            mark: Mark = PIH.RESULT.MARK.by_name(name, True).data
            telephone_number: str = PIH.DATA.FORMAT.telephone_number(
                mark.telephoneNumber
            )
            if temporary:
                PIH.EVENT.send(
                    Events.IT_NOTIFY_ABOUT_CREATE_TEMPORARY_MARK,
                    (name, tab_number, telephone_number),
                )
            else:
                PIH.EVENT.send(
                    Events.IT_NOTIFY_ABOUT_CREATE_MARK,
                    (name, telephone_number, mark.TabNumber, mark.GroupName),
                )

        @staticmethod
        def it_notify_about_temporary_mark_return(
            mark: Mark, temporary_tab_number: int
        ) -> None:
            PIH.EVENT.send(
                Events.IT_NOTIFY_ABOUT_TEMPORARY_MARK_RETURN,
                (mark.FullName, temporary_tab_number),
            )

        @staticmethod
        def backup_notify_about_polibase_creation_db_dumb_start() -> None:
            PIH.EVENT.send(Events.POLIBASE_CREATION_DB_DUMP_START)

        @staticmethod
        def backup_notify_about_polibase_creation_db_dumb_complete(size: int) -> None:
            PIH.EVENT.send(Events.POLIBASE_CREATION_DB_DUMP_COMPLETE, (size,))

        @staticmethod
        def backup_notify_about_polibase_creation_archived_db_dumb_start() -> None:
            PIH.EVENT.send(Events.POLIBASE_CREATION_ARCHIVED_DB_DUMP_START)

        @staticmethod
        def backup_notify_about_polibase_creation_archived_db_dumb_complete(
            size: int,
        ) -> None:
            PIH.EVENT.send(Events.POLIBASE_CREATION_ARCHIVED_DB_DUMP_COMPLETE, size)

        @staticmethod
        def backup_notify_about_polibase_coping_archived_db_dumb_start(
            destination: str,
        ) -> None:
            PIH.EVENT.send(
                Events.POLIBASE_COPING_ARCHIVED_DB_DUMP_START, (destination,)
            )

        @staticmethod
        def backup_notify_about_polibase_coping_archived_db_dumb_complete(
            destination: str,
        ) -> None:
            PIH.EVENT.send(
                Events.POLIBASE_COPING_ARCHIVED_DB_DUMP_COMPLETE, (destination,)
            )

        @staticmethod
        def backup_notify_about_polibase_coping_db_dumb_start(destination: str) -> None:
            PIH.EVENT.send(Events.POLIBASE_COPING_DB_DUMP_START, (destination,))

        @staticmethod
        def backup_notify_about_polibase_coping_db_dumb_complete(
            destination: str,
        ) -> None:
            PIH.EVENT.send(Events.POLIBASE_COPING_DB_DUMP_COMPLETE, (destination,))

        @staticmethod
        def it_notify_about_mark_return(mark: Mark) -> None:
            PIH.EVENT.send(
                Events.IT_NOTIFY_ABOUT_MARK_RETURN, (mark.FullName, mark.TabNumber)
            )

        @staticmethod
        def it_notify_about_create_new_mark(full_name: str | FullName) -> None:
            PIH.EVENT.it_notify_about_create_mark(full_name, False)

        @staticmethod
        def it_notify_about_create_temporary_mark(
            full_name: str | FullName, tab_number: str
        ) -> None:
            PIH.EVENT.it_notify_about_create_mark(full_name, True, tab_number)

        @staticmethod
        def printer_report(name: str, location: str, report_text: str) -> None:
            PIH.EVENT.send(Events.PRINTER_REPORT, (name, location, report_text))

        @staticmethod
        def on_event(
            handler: Callable[[ParameterList, IClosable], None],
            block: bool = True,
        ) -> None:
            def thread_handler() -> None:
                ServiceListener().listen_for(
                    [ServiceCommands.send_event],
                    lambda _, pl, service_listener: handler(pl, service_listener),
                )

            if block:
                thread_handler()
            else:
                PIHThread(thread_handler)

        @staticmethod
        def wait_server_start(
            handler_or_server_name: Callable[[str, Callable[[None], None]], None] | str
        ) -> None:
            def internal_handler(pl: ParameterList, listener: IClosable) -> None:
                event, parameters = PIH.DATA.EXTRACT.EVENT.with_parameters(pl)
                if event == Events.SERVER_WAS_STARTED:
                    server_name: str = parameters[0]
                    if callable(handler_or_server_name):
                        handler_or_server_name(server_name, listener.close)
                    else:
                        if handler_or_server_name.startswith(server_name):
                            listener.close()

            PIH.EVENT.on_event(internal_handler)

        @staticmethod
        def on_service_starts(
            handler_or_service_role_or_information: (
                Callable[[str, Callable[[None], None]], None]
                | ServiceRoles
                | ServiceInformationBase
            )
        ) -> None:
            def internal_handler(pl: ParameterList, listener: ServiceListener) -> None:
                event, parameters = PIH.DATA.EXTRACT.EVENT.with_parameters(pl)
                if event == PIH.EVENT.BUILDER.service_was_started():
                    service_description_name: str = parameters[0]
                    if callable(handler_or_service_role_or_information):
                        handler_or_service_role_or_information(
                            service_description_name, listener.close
                        )
                    elif (
                        handler_or_service_role_or_information
                        == service_description_name
                    ):
                        listener.close()

            PIH.EVENT.on_event(internal_handler)

        @staticmethod
        def on_robocopy_job_complete(
            handler_or_robocopy_job_name: (
                Callable[[str, int, ServiceListener], None] | str
            )
        ) -> bool | None:
            class DH:
                result: bool | None = None

            def internal_handler(pl: ParameterList, listener: ServiceListener) -> None:
                event, parameters = PIH.DATA.EXTRACT.EVENT.with_parameters(pl)
                if event == Events.BACKUP_ROBOCOPY_JOB_WAS_COMPLETED:
                    robocopy_job_status_name: str = parameters[0]
                    robocopy_job_status: int = parameters[-1]
                    DH.result = robocopy_job_status < ROBOCOPY.ERROR_CODE_START
                    if callable(handler_or_robocopy_job_name):
                        handler_or_robocopy_job_name(
                            robocopy_job_status_name, robocopy_job_status, listener
                        )
                    else:
                        if robocopy_job_status_name.startswith(
                            handler_or_robocopy_job_name
                        ):
                            listener.close()

            PIH.EVENT.on_event(internal_handler)
            return DH.result

    class SERVICE:
        LONG_OPERATION_DURATION: int | None = None

        EVENT_LISTENER_NAME_PREFIX: str = "_@@EventListener@@_"
        SUPPORT_NAME_PREFIX: str = "_@@Support@@_"
        command_map: dict[str, ServiceDescription] | None = None

        class DH:
            long_operation_listeners: list[Callable[[None], None]] = []

        @staticmethod
        def check_on_host_chanchable(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> bool:
            description: ServiceDescription = ServiceRoles.description(
                service_role_or_information
            )
            return description.host_changeable or StringTool.contains(
                PIH.OS.host(), description.host
            )

        @staticmethod
        def call_listeners_on_long_operation() -> None:
            for listener in PIH.SERVICE.DH.long_operation_listeners:
                listener()

        @staticmethod
        def start_listen_for_long_operation(listener: Callable[[None], None]) -> None:
            PIH.SERVICE.DH.long_operation_listeners.append(listener)

        @staticmethod
        def stop_listen_for_long_operation(listener: Callable[[None], None]) -> None:
            PIH.SERVICE.DH.long_operation_listeners.remove(listener)

        @staticmethod
        def call(
            service_role_or_information: ServiceRoles | ServiceInformationBase | None,
            service_command: ServiceCommands,
            parameters: Any | None = None,
            timeout: int | None = None,
            blocked: bool = True,
        ) -> str | None:
            def action() -> str | None:
                return RPC.call_service(
                    service_role_or_information, service_command, parameters, timeout
                )

            if blocked:
                return action()
            else:
                PIHThread(action)
                return None

        @staticmethod
        def call_command(
            value: ServiceCommands,
            parameters: Any | None = None,
            timeout: int | None = None,
            blocked: bool = True,
        ) -> str | None:
            return PIH.SERVICE.call(None, value, parameters, timeout, blocked)

        @staticmethod
        def get_support_host_list(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> list[str]:
            return DataTool.filter(
                lambda item: item.name.startswith(
                    j(
                        (
                            PIH.SERVICE.SUPPORT_NAME_PREFIX,
                            ServiceRoles.description(service_role_or_information).name,
                        )
                    )
                ),
                PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP,
            )

        class ADMIN:
            SERVICE_INFORMATION_MAP: dict[
                ServiceInformationBase, ServiceInformation
            ] = {}

            @staticmethod
            def check_on_startable(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
            ) -> bool | None:
                service_description: ServiceDescription = if_else(
                    isinstance(service_role_or_information, ServiceRoles),
                    lambda: ServiceRoles.description(service_role_or_information),
                    service_role_or_information,
                )
                login_value: str | None = service_description.login
                login_variable_name_list: list[str] | None = PIH.DATA.EXTRACT.variables(
                    login_value
                )
                if ne(login_variable_name_list):
                    if e(PIH.DATA.FORMAT.variable(login_value, True)):
                        raise Exception(
                            f"Login for start service {service_description.host} ({login_variable_name_list[0]}) is not set"
                        )
                password_value: str | None = service_description.password
                password_variable_name_list: list[str] | None = (
                    PIH.DATA.EXTRACT.variables(password_value)
                )
                if ne(PIH.DATA.EXTRACT.variables(password_value)):
                    if e(PIH.DATA.FORMAT.variable(password_value, True)):
                        raise Exception(
                            f"Password for start service {service_description.host} ({password_variable_name_list[0]}) is not set"
                        )
                return True

            @staticmethod
            def change_host_on_local(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
            ) -> None:
                ServiceRoles.description(service_role_or_information).host = (
                    PIH.OS.host()
                )

            @staticmethod
            def service_information_list() -> list[ServiceInformation]:
                return DataTool.to_list(PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP)

            @staticmethod
            def kill_all(
                local: bool = True,
                via_standart_tools: bool = True,
                exclude_me: bool = False,
            ) -> bool:
                hosts: set[str] = set()
                for server_role in ServiceRoles:
                    host: str | None = ServiceRoles.description(server_role).host
                    if ne(host):
                        hosts.add(host)

                def kill(host: str, local: bool, via_standart_tools: bool) -> None:
                    if local:
                        PIH.EXECUTOR.kill_python_process(host, via_standart_tools)
                    else:
                        PIH.ACTION.WORKSTATION.kill_python_process(
                            host, via_standart_tools
                        )

                for host in hosts:
                    if host != PIH.OS.host():
                        kill(host, local, via_standart_tools)
                if not exclude_me:
                    for host in hosts:
                        if host == PIH.OS.host():
                            kill(host, local, via_standart_tools)

            @staticmethod
            def subscribe_on(
                service_command: ServiceCommands,
                type: int = SubscribtionTypes.ON_RESULT,
                name: str | None = None,
            ) -> bool:
                return RPC.service.subscribe_on(service_command, type, name)

            @staticmethod
            def unsubscribe(service_command: ServiceCommands, type: int) -> bool:
                return RPC.service.unsubscribe(service_command, type)

            @staticmethod
            def create_developer_service_description(
                port: int = None,
            ) -> ServiceDescription:
                if n(port) or port == ServiceRoles.DEVELOPER.value.port:
                    return ServiceRoles.DEVELOPER.value
                return ServiceDescription(
                    f"Developer_{port}",
                    host=CONST.HOST.DEVELOPER.NAME,
                    port=CONST.RPC.PORT(port),
                )

            @staticmethod
            def create_support_service_or_master_service_description(
                master_service_desctiption: ServiceDescription, host: str | None = None
            ) -> ServiceDescription:
                if PIH.SERVICE.check_on_accessibility(master_service_desctiption):
                    host = host or PIH.OS.host()
                    if master_service_desctiption.host != host:
                        port: int = PIH.SERVICE.create_port(master_service_desctiption)
                        return ServiceDescription(
                            name=j(
                                (
                                    j(
                                        (
                                            PIH.SERVICE.SUPPORT_NAME_PREFIX,
                                            master_service_desctiption.name,
                                        )
                                    ),
                                    host,
                                ),
                                ":",
                            ),
                            description=js(
                                (
                                    "Support service for",
                                    master_service_desctiption.name,
                                    "on",
                                    host,
                                )
                            ),
                            host=host,
                            port=port,
                            auto_restart=False,
                        )
                return master_service_desctiption

            @staticmethod
            def create_event_listener_service_description(
                host: str, port: int
            ) -> ServiceDescription:
                return ServiceDescription(
                    name=j(
                        (PIH.SERVICE.EVENT_LISTENER_NAME_PREFIX, host, str(port)), ":"
                    ),
                    description="Subscriber",
                    host=host,
                    port=port,
                    auto_start=False,
                    auto_restart=False,
                )

            @staticmethod
            def as_developer(
                service_role: ServiceRoles, port: int = None
            ) -> ServiceDescription:
                developer_service_description: ServiceDescription = (
                    PIH.SERVICE.ADMIN.create_developer_service_description(port)
                )
                description: ServiceDescription = ServiceRoles.description(service_role)
                description.isolated = True
                description.host = developer_service_description.host
                description.port = developer_service_description.port
                return description

            @staticmethod
            def isolate(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
            ) -> ServiceDescription:
                description: ServiceDescription = ServiceRoles.description(
                    service_role_or_information
                )
                description.isolated = True
                description.auto_restart = False
                return description

            @staticmethod
            def restart(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
                show_output: bool = True,
            ) -> bool | None:
                if PIH.SERVICE.ADMIN.check_on_startable(service_role_or_information):
                    PIH.SERVICE.ADMIN.stop(service_role_or_information, False)
                    return PIH.SERVICE.ADMIN.start(
                        service_role_or_information, False, show_output
                    )
                return None

            @staticmethod
            def start_certainly(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
                host: str | None = None,
                as_standalone: bool = True,
            ) -> bool | None:
                return PIH.SERVICE.ADMIN.start(
                    service_role_or_information,
                    False,
                    True,
                    host=host,
                    host_is_linux=None,
                    ipih_install=True,
                    pih_install=True,
                    as_standalone=as_standalone,
                )

            @staticmethod
            def start(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
                check_if_started: bool = True,
                show_output: bool = True,
                parameters: Any | None = None,
                host: str | None = None,
                host_is_linux: bool | None = None,
                ipih_install: bool = True,
                pih_install: bool | None = None,
                as_standalone: bool = False,
            ) -> bool | None:
                description: ServiceInformationBase = ServiceRoles.description(
                    service_role_or_information, True
                )
                as_standalone = as_standalone and nn(description.standalone_name)
                host = host or description.host
                if ipih_install:
                    PIH.UPDATE.install_module(
                        ipih.NAME,
                        ipih.VERSION,
                        show_output=show_output,
                        host=host,
                        host_is_linux=host_is_linux,
                    )
                if pih_install:
                    PIH.UPDATE.install_module(
                        PIH.NAME,
                        PIH.VERSION.value,
                        show_output=show_output,
                        host=host,
                        host_is_linux=host_is_linux,
                    )

                if as_standalone:
                    PIH.UPDATE.install_module(
                        j((A.NAME, description.standalone_name), "-"),
                        description.version,
                        show_output=show_output,
                        host=host,
                        host_is_linux=host_is_linux,
                    )
                if n(host_is_linux) and (host_is_linux := PIH.OS.is_linux(host)):
                    PIH.ACTION.SSH.mount_facade_for_linux_host(host)
                try:
                    PIH.SERVICE.ADMIN.check_on_startable(service_role_or_information)
                    if check_if_started:
                        if PIH.SERVICE.check_on_accessibility(description):
                            return None
                    command_list: list[str] = []
                    file_path: str | None = None
                    if as_standalone and nn(description.standalone_name):
                        file_path = j((PIH.NAME, description.standalone_name), "-")
                    else:
                        service_file: str = PathTool.add_extension(
                            CONST.SERVICE.NAME, FILE.EXTENSION.PYTHON
                        )
                        if e(description.service_path):
                            file_path = PIH.PATH.adapt_for_linux(
                                PIH.PATH.join(
                                    PATH_FACADE.VALUE,
                                    j(
                                        (
                                            description.name,
                                            FACADE.SERVICE_FOLDER_SUFFIX,
                                        )
                                    ),
                                    service_file,
                                ),
                                host=host,
                                host_is_linux=host_is_linux,
                            )
                        else:
                            file_path = PIH.PATH.join(
                                description.service_path, service_file
                            )
                    command_list.append(file_path)
                    command_list.append(j((ARGUMENT_PREFIX, ISOLATED_ARG_NAME)))
                    command_list.append("0")
                    if ne(parameters):
                        if isinstance(parameters, list) or isinstance(
                            parameters, tuple
                        ):
                            for parameter_item in parameters:
                                command_list.append(parameter_item)
                        else:
                            command_list.append(parameters)
                    if not host_is_linux or n(host_is_linux):
                        command_list = (
                            PIH.EXECUTOR.create_command_for_start_service(
                                description,
                                host=host,
                            )
                            + command_list
                        )
                        complete_process: CompletedProcess = PIH.EXECUTOR.execute(
                            command_list, show_output
                        )
                    if host_is_linux or (
                        n(host_is_linux)
                        and n(PIH.EXECUTOR.extract_returncode(complete_process, True))
                    ):
                        return PIH.RESULT.SSH.execute_python_file(
                            js(command_list), host, in_background=True
                        )
                    return True
                except Exception as error:
                    A.O.error(error.args[0])
                    return None

            @staticmethod
            def kill(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
                local: bool = True,
                via_standart_tools: bool = True,
            ) -> bool | None:
                information: ServiceInformation | None = PIH.SERVICE.get_information(
                    service_role_or_information
                )
                if e(information):
                    return None
                pid: int = information.pid
                host: str = PIH.SERVICE.get_host(information)
                if local:
                    return PIH.EXECUTOR.kill_process(pid, host, via_standart_tools)
                return PIH.ACTION.WORKSTATION.kill_process(
                    pid, host, via_standart_tools
                )

            @staticmethod
            def serve(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
                call_handler: (
                    Callable[[ServiceCommands, ParameterList], Any | None] | None
                ) = None,
                starts_handler: Callable[[IService | None], None] | None = None,
                max_workers: int | None = None,
                stop_before: bool = True,
                depends_on_list: list[ServiceDescription | ServiceRoles] | None = None,
                isolate: bool = False,
                as_standalone: bool = False,
                show_output: bool = True,
            ) -> None:
                service_description: ServiceDescription = A.D.get(
                    service_role_or_information
                )
                service_description.standalone = not isolate and (
                    as_standalone
                    and nn(service_description.standalone_name)
                    if n(service_description.standalone)
                    else service_description.standalone
                )
                host: str = PIH.OS.host()
                service_description = ServiceRoles.description(
                    service_role_or_information
                )
                if PIH.SERVICE.check_on_host_chanchable(service_description):
                    if isolate:
                        PIH.SERVICE.ADMIN.isolate(service_description)
                    else:
                        if not PIH.DATA.contains(host, service_description.host):
                            PIH.SERVICE.ADMIN.change_host_on_local(service_description)
                        if stop_before:
                            if PIH.SERVICE.check_on_accessibility(service_description):
                                PIH.SERVICE.ADMIN.stop(service_description)

                    def internal_start_handler(service: IService) -> None:
                        if PIH.OS.is_linux():
                            A.A_SSH.mount_facade_for_linux_host(host)
                        if nn(starts_handler):
                            if starts_handler.__code__.co_argcount == 1:
                                starts_handler(service)
                            else:
                                starts_handler()

                    service: IService = RPC.create_service()
                    from inspect import signature, Signature

                    def internal_call_handler(
                        command_name: str, pl: ParameterList, context
                    ) -> Any | None:
                        with PIH.ERROR.detect():
                            if ne(call_handler):
                                sig: Signature = signature(call_handler)
                                arg_count: int = len(sig.parameters) - (
                                    "self" in sig.parameters
                                )
                                if arg_count == 3:
                                    if DataTool.is_in(sig.parameters, "context"):
                                        return call_handler(
                                            EnumTool.get(ServiceCommands, command_name),
                                            pl,
                                            context,
                                        )
                                    if DataTool.is_in(
                                        sig.parameters, "subscribtion_result"
                                    ):
                                        return call_handler(
                                            EnumTool.get(ServiceCommands, command_name),
                                            pl,
                                            PIH.DATA.EXTRACT.subscribtion_result(pl),
                                        )
                                return call_handler(
                                    EnumTool.get(ServiceCommands, command_name),
                                    pl,
                                )
                        return None

                    service.serve(
                        service_description,
                        internal_call_handler,
                        internal_start_handler,
                        max_workers,
                        depends_on_list,
                        show_output,
                    )
                else:
                    PIH.ERROR.service_host_is_unchanachable(service_description.host)

            @staticmethod
            def stop(
                service_role_or_information: ServiceRoles | ServiceInformationBase,
                check_if_started: bool = True,
                direct_call: bool = False,
            ) -> bool:
                description: ServiceDescription | None = ServiceRoles.description(
                    service_role_or_information
                )
                if not check_if_started or PIH.SERVICE.check_on_accessibility(
                    description
                ):
                    if PIH.SERVICE.is_service_as_listener(description) or direct_call:
                        PIH.SERVICE.call(description, ServiceCommands.stop_service)
                        return True
                    service_information: ServiceInformationBase | None = (
                        DataTool.fill_data_from_source(
                            ServiceInformationBase(),
                            PIH.SERVICE.get_information(description),
                        )
                    )
                    if n(service_information):
                        return False
                    PIH.SERVICE.call(service_information, ServiceCommands.stop_service)
                    return True
                return False

            @staticmethod
            def update_service_information(
                list: list[ServiceInformation],
                add: bool = True,
                overwrite: bool = False,
            ) -> None:
                if overwrite:
                    PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP = {}
                for item in list:
                    if add:
                        PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP[item] = item
                    else:
                        if item in PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP:
                            del PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP[item]

            @staticmethod
            def validate(
                cached: bool = False, include_isolated: bool = False
            ) -> tuple[list, list]:
                if not cached:
                    PIH.SERVICE.ADMIN.request_for_service_information_list()
                service_information_list: list[ServiceInformation] = (
                    PIH.SERVICE.ADMIN.service_information_list()
                )
                if not include_isolated:
                    service_information_list = DataTool.filter(
                        lambda item: not item.isolated, service_information_list
                    )
                if ne(service_information_list):
                    length: int = len(service_information_list)
                    with ThreadPoolExecutor(max_workers=length) as executor:
                        future_to_bool = {
                            executor.submit(
                                PIH.ERROR.wrap(PIH.SERVICE.check_on_accessibility),
                                service_descroption,
                            ): service_descroption
                            for service_descroption in service_information_list
                        }
                        offline_service_list: list[ServiceInformation] = []
                        for value in futures.as_completed(future_to_bool):
                            if not value.result():
                                service_information: ServiceInformation = (
                                    future_to_bool[value]
                                )
                                offline_service_list.append(service_information)
                                service_information_list.remove(service_information)
                                del PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP[
                                    service_information
                                ]
                        service_description_list: list[ServiceDescription] = (
                            DataTool.filter(
                                lambda item: item.visible_for_admin,
                                DataTool.map(
                                    lambda item: ServiceRoles.description(item),
                                    ServiceRoles,
                                ),
                            )
                        )
                        for service_description_item in service_description_list:
                            if (
                                service_description_item not in service_information_list
                                and service_description_item not in offline_service_list
                            ):
                                offline_service_list.append(service_description_item)
                        return offline_service_list, service_information_list
                return [], []

            @staticmethod
            def request_for_service_information_list() -> None:
                PIH.SERVICE.ADMIN.update_service_information(
                    list(
                        map(
                            PIH.DATA.EXTRACT.service_information,
                            DataTool.rpc_unrepresent(
                                PIH.SERVICE.call_command(
                                    ServiceCommands.get_service_information_table,
                                    (
                                        (
                                            RPC.service_information or ServiceRoles.STUB
                                        ).name
                                    ),
                                )
                            )
                            or [],
                        )
                    ),
                    True,
                    True,
                )

        @staticmethod
        def check_on_accessibility(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
            cached: bool = False,
        ) -> bool:
            return ne(PIH.SERVICE.get_information(service_role_or_information, cached))

        @staticmethod
        def is_service_as_listener(information: ServiceInformationBase) -> bool:
            return information.name.find(PIH.SERVICE.EVENT_LISTENER_NAME_PREFIX) == 0

        @staticmethod
        def is_service_as_support(information: ServiceInformationBase) -> bool:
            return information.name.find(PIH.SERVICE.SUPPORT_NAME_PREFIX) == 0

        @staticmethod
        def get_information(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
            cached: bool = True,
        ) -> ServiceInformation | None:
            service_information: ServiceInformationBase | None = (
                ServiceRoles.description(service_role_or_information)
            )
            # if PIH.SERVICE.is_service_as_listener(service_information):
            #    return RPC.ping(service_information)
            if e(PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP):
                PIH.SERVICE.ADMIN.request_for_service_information_list()
            service_information = PIH.SERVICE.get_information_from_cache(
                service_information
            )
            if cached:
                return service_information
            if e(service_information):
                return None
            return RPC.ping(service_information)

        @staticmethod
        def get_information_or_description(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> ServiceInformation | ServiceDescription:
            return PIH.SERVICE.get_information(
                service_role_or_information
            ) or ServiceRoles.description(service_role_or_information)

        @staticmethod
        def get_information_from_cache(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> ServiceInformation | None:
            description: ServiceDescription = ServiceRoles.description(
                service_role_or_information
            )
            return (
                PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP[description]
                if description in PIH.SERVICE.ADMIN.SERVICE_INFORMATION_MAP
                else None
            )

        @staticmethod
        def description_by_command(value: ServiceCommands) -> ServiceDescription | None:
            if e(PIH.SERVICE.command_map):
                PIH.SERVICE.command_map = {}
                for service_role_item in ServiceRoles:
                    description: ServiceDescription = ServiceRoles.description(
                        service_role_item
                    )
                    service_command_item: ServiceCommands
                    for service_command_item in description.commands:
                        PIH.SERVICE.command_map[service_command_item.name] = description
            return (
                PIH.SERVICE.command_map[value.name]
                if value.name in PIH.SERVICE.command_map
                else None
            )

        @staticmethod
        def get_host(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> str:
            information: ServiceInformationBase | None = ServiceRoles.description(
                service_role_or_information
            )
            if isinstance(information, ServiceDescription):
                if ne(information.port):
                    return PIH.DATA.FORMAT.donain(information.host)
            return PIH.DATA.FORMAT.donain(
                (
                    PIH.SERVICE.get_information(service_role_or_information)
                    or ServiceInformationBase()
                ).host
                or information.host
            )

        @staticmethod
        def get_port(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> int | None:
            information: ServiceInformationBase | None = ServiceRoles.description(
                service_role_or_information
            )
            if isinstance(information, ServiceDescription):
                if ne(information.port):
                    return information.port
            return (
                PIH.SERVICE.get_information(service_role_or_information)
                or ServiceInformationBase()
            ).port or information.port

        @staticmethod
        def create_port(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> int:
            return (
                ServiceRoles.description(service_role_or_information).port
                or NetworkTool.next_free_port()
            )

        @staticmethod
        def create_host(
            service_role_or_information: ServiceRoles | ServiceInformationBase,
        ) -> int:
            description: ServiceDescription = ServiceRoles.description(
                service_role_or_information
            )
            return (
                PIH.OS.host()
                if description.isolated or e(description.host)
                else description.host
            )

    class PATH(PATHS, PathTool):
        DIRECTORY_INFO_SECTION: str = "directory_info"

        @staticmethod
        def get_file_directory(path: str) -> str:
            return PIH.PATH.path(PathTool.get_file_directory(path))

        @staticmethod
        def join(path: str, *paths) -> str:
            return PIH.PATH.path(os.path.join(path, *paths))

        @staticmethod
        def get_modification_time(path: str) -> str:
            return os.path.getmtime(PIH.PATH.adapt_for_linux(path))

        @staticmethod
        def get_creation_time(path: str) -> str:
            return os.path.getctime(PIH.PATH.adapt_for_linux(path))

        @staticmethod
        def adapt_for_linux(
            path: str, host: str | None = None, host_is_linux: bool | None = None
        ) -> str:
            path = PIH.PATH.path(path)
            if host_is_linux or PIH.OS.is_linux(host):
                alias: str = PATH_FACADE.VALUE
                if path.find(alias) == 0:
                    path = path[len(alias) :]
                    path = PATHS.FACADE.LINUX_MOUNT_POINT_PATH + path
            return path

        @staticmethod
        def get_file_list_by_directory_info(path: str) -> list[str] | None:
            return PIH.PATH.get_file_list(
                path,
                DataTool.if_not_empty(
                    PIH.RESULT.DATA_STORAGE.value(
                        PIH.PATH.get_directory_info_name(None, PIH.PATH.path(path)),
                        DirectoryInfo(),
                        PIH.PATH.DIRECTORY_INFO_SECTION,
                    ).data,
                    lambda info: info.last_created_file_timestamp,
                ),
            )

        @staticmethod
        def get_directory_info_name(
            file_path: str | None, directory_path: str | None = None
        ) -> str:
            return j(
                (
                    PIH.PATH.DIRECTORY_INFO_SECTION,
                    (directory_path or PIH.PATH.get_file_directory(file_path)),
                ),
                "_",
            )

        @staticmethod
        def save_timestamp_for_directory_info(path: str) -> None:
            path = PIH.PATH.path(path)
            PIH.ACTION.DATA_STORAGE.value(
                DirectoryInfo(path, int(DateTimeTool.now().timestamp())),
                PIH.PATH.get_directory_info_name(path),
                PIH.PATH.DIRECTORY_INFO_SECTION,
            )

        @staticmethod
        def get_directory_info(path: str) -> DirectoryInfo | None:
            return PIH.RESULT.DATA_STORAGE.value(
                PIH.PATH.get_directory_info_name(None, PIH.PATH.path(path)),
                DirectoryInfo(),
                PIH.PATH.DIRECTORY_INFO_SECTION,
            ).data

        @staticmethod
        def get_host(value: str) -> str:
            return PIH.DATA.FORMAT.host(value, reverse=True)

        @staticmethod
        def resolve(value: str) -> str:
            if value[0] == "{" and value[-1] == "}":
                value = value[1:-1]
            return PathTool.resolve(value, PIH.OS.host())

        class QR_CODE:
            @staticmethod
            def polibase_person_card_registry_folder(name: str) -> str:
                name = name.upper()
                return PIH.PATH.join(
                    PATHS.POLIBASE_APP_DATA.PERSON_CARD_REGISTRY_FOLDER,
                    PathTool.replace_prohibited_symbols_from_path_with_symbol(
                        PathTool.add_extension(name, FILE.EXTENSION.PNG)
                    ),
                )

            @staticmethod
            def mobile_helper_command(name: str) -> str:
                name = PIH.DATA.FORMAT.mobile_helper_command(name)
                return PIH.PATH.join(
                    PATHS.MOBILE_HELPER.QR_CODE_FOLDER,
                    PathTool.replace_prohibited_symbols_from_path_with_symbol(
                        PathTool.add_extension(name, FILE.EXTENSION.PNG)
                    ),
                )

    class DATA(DataTool, StringTool, ListTool, DateTimeTool, EnumTool, FullNameTool):
        class JOURNAL:
            @staticmethod
            def type_by_any(
                value: str | int | None, full_equaliment: bool = True
            ) -> list[JournalType] | None:
                result: list[JournalType] = []
                if n(value):
                    return None
                try:
                    value = int(value)
                    data: OrderedNameCaptionDescription | None = one(
                        DataTool.filter(
                            lambda item: item[0] == value, DataTool.to_list(JournalType)
                        )
                    )
                    return None if n(data) else [JournalType(data)]
                except ValueError as _:
                    pass
                value = value.lower()
                for item in JournalType:
                    item_data: OrderedNameCaptionDescription = EnumTool.get(item)
                    item_data_param: ParamItem = item_data[1]
                    a: bool = (
                        item_data_param.name.lower() == value
                        if full_equaliment
                        else StringTool.contains(item_data_param.name, value)
                    )
                    b: bool = StringTool.contains(item_data_param.caption, value)
                    if a or b:
                        result.append(item)
                        if not b and full_equaliment:
                            break
                return None if e(result) else result

            @staticmethod
            def tag_by_id(value: int) -> Tags | None:
                data: IconedOrderedNameCaptionDescription | None = one(
                    DataTool.filter(
                        lambda item: item[0] == value, DataTool.to_list(Tags)
                    )
                )
                return None if n(data) else Tags(data)

        @staticmethod
        def translit(value, language_code=None, reversed=False, strict=False):
            return translit(value, language_code, reversed, strict)

        class VARIABLE:
            SECTION_DELIMITER: str = "__"
            SECTION_DELIMITER_ALT: str = "."

            @staticmethod
            def _get_as_name(value: str | StorageVariableHolder) -> str:
                if isinstance(value, StorageVariableHolder):
                    return value.key_name
                return value

            class TIMESTAMP:
                @staticmethod
                def value(name: str | StorageVariableHolder) -> datetime | None:
                    return DateTimeTool.datetime_from_string(
                        PIH.DATA.VARIABLE.value(
                            PIH.DATA.VARIABLE._get_as_name(name),
                            from_environment_only=False,
                            section=PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP,
                        )
                    )

                @staticmethod
                def find(name: str | None = None) -> list[StorageVariableHolder] | None:
                    return (
                        PIH.DATA.VARIABLE.TIMESTAMP.get(name)
                        if n(name)
                        else PIH.DATA.VARIABLE.find(
                            name, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP
                        )
                    )

                @staticmethod
                def get(
                    name: str | None = None,
                ) -> StorageVariableHolder | list[StorageVariableHolder] | None:
                    return PIH.DATA.VARIABLE.get(
                        name, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP
                    )

                @staticmethod
                def set(
                    name: str | StorageVariableHolder,
                    value: datetime | None,
                    description: str,
                ) -> str:
                    return PIH.DATA.VARIABLE.set(
                        PIH.DATA.VARIABLE._get_as_name(name),
                        DateTimeTool.datetime_to_string(value or DateTime.now()),
                        description,
                        PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP,
                    )

                @staticmethod
                def update(
                    name: str | StorageVariableHolder, value: datetime | None = None
                ) -> bool:
                    holder: StorageVariableHolder | None = (
                        PIH.DATA.VARIABLE.TIMESTAMP.get(name)
                    )
                    if nn(holder):
                        PIH.DATA.VARIABLE.TIMESTAMP.set(
                            PIH.DATA.VARIABLE._get_as_name(name),
                            value,
                            holder.description,
                        )
                        return True
                    return False

                @staticmethod
                def remove(name: str) -> None:
                    PIH.DATA.VARIABLE.remove(
                        PIH.DATA.VARIABLE._get_as_name(name),
                        PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP,
                    )
                    item: ExpiredTimestampVariableHolder | None = None
                    for item in PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder():
                        if item.timestamp == name:
                            PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.remove(name)

                class EXPIRED:
                    @staticmethod
                    def remove(name: str) -> None:
                        PIH.DATA.VARIABLE.remove(
                            PIH.DATA.VARIABLE._get_as_name(name),
                            PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED,
                        )

                    @staticmethod
                    def set(
                        name: str,
                        description: str,
                        timestamp_variable_name: str,
                        life_time_variable_name: str,
                        note_name_resolver: str,
                    ) -> None:
                        timestamp_value: datetime | None = (
                            PIH.DATA.VARIABLE.TIMESTAMP.value(timestamp_variable_name)
                        )
                        if nn(timestamp_value):
                            life_time_variable: int | None = int(
                                PIH.DATA.VARIABLE.value(life_time_variable_name)
                            )
                            PIH.DATA.VARIABLE.set(
                                name,
                                ExpiredTimestampVariableHolder(
                                    timestamp_variable_name,
                                    life_time_variable_name,
                                    note_name_resolver,
                                ),
                                description,
                                PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED,
                            )

                    @staticmethod
                    def get(
                        name: str | None = None,
                    ) -> StorageVariableHolder | list[StorageVariableHolder] | None:
                        return PIH.DATA.VARIABLE.get(
                            name, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED
                        )

                    @staticmethod
                    def holder(
                        name: str | StorageVariableHolder | None = None,
                    ) -> (
                        ExpiredTimestampVariableHolder
                        | list[ExpiredTimestampVariableHolder]
                        | None
                    ):
                        result: list[ExpiredTimestampVariableHolder] = (
                            DataTool.fill_data_from_list_source(
                                ExpiredTimestampVariableHolder,
                                DataTool.map(
                                    lambda item: item.default_value,
                                    PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.get(name),
                                ),
                            )
                        )
                        if nn(name):
                            if e(result):
                                return None
                        return result if n(name) else DataTool.get_first_item(result)

                    @staticmethod
                    def value(
                        name_or_holder: (
                            str | ExpiredTimestampVariableHolder | StorageVariableHolder
                        ),
                    ) -> datetime | None:
                        if isinstance(name_or_holder, str):
                            name_or_holder = PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(
                                name_or_holder
                            )
                        if isinstance(name_or_holder, StorageVariableHolder):
                            name_or_holder = DataTool.fill_data_from_source(
                                ExpiredTimestampVariableHolder(),
                                name_or_holder.defaul_value,
                            )
                        life_time: int | None = None
                        try:
                            life_time = int(name_or_holder.life_time)
                        except ValueError as _:
                            life_time = int(
                                PIH.DATA.VARIABLE.value(name_or_holder.life_time)
                            )
                        return (
                            None
                            if e(name_or_holder)
                            else DateTimeTool.add_months(
                                PIH.DATA.VARIABLE.TIMESTAMP.value(
                                    name_or_holder.timestamp
                                ),
                                life_time,
                            )
                        )

                    @staticmethod
                    def timestamp(
                        name_or_variable_holder: str | ExpiredTimestampVariableHolder,
                    ) -> datetime | None:
                        variable_holder: ExpiredTimestampVariableHolder | None = (
                            PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(
                                name_or_variable_holder
                            )
                            if isinstance(name_or_variable_holder, str)
                            else name_or_variable_holder
                        )
                        return (
                            None
                            if e(variable_holder)
                            else PIH.DATA.VARIABLE.TIMESTAMP.value(
                                variable_holder.timestamp
                            )
                        )

                    @staticmethod
                    def life_time(
                        name_or_variable_holder: str | ExpiredTimestampVariableHolder,
                    ) -> int | None:
                        variable_holder: ExpiredTimestampVariableHolder | None = (
                            PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(
                                name_or_variable_holder
                            )
                            if isinstance(name_or_variable_holder, str)
                            else name_or_variable_holder
                        )
                        return (
                            None
                            if e(variable_holder)
                            else DateTimeTool.day_count(
                                PIH.DATA.VARIABLE.TIMESTAMP.value(
                                    variable_holder.timestamp
                                ),
                                int(PIH.DATA.VARIABLE.value(variable_holder.life_time)),
                            )
                        )

                    @staticmethod
                    def left_life_time(
                        name_or_variable_holder: str | ExpiredTimestampVariableHolder,
                    ) -> int | None:
                        variable_holder: ExpiredTimestampVariableHolder | None = (
                            PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(
                                name_or_variable_holder
                            )
                            if isinstance(name_or_variable_holder, str)
                            else name_or_variable_holder
                        )
                        return (
                            None
                            if e(variable_holder)
                            else (
                                PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.value(
                                    variable_holder
                                )
                                - DateTimeTool.now()
                            ).days
                            + 1
                        )

            class ENVIRONMENT:
                @staticmethod
                def value(name: str, raise_exception_if_not_exist: bool = True) -> Any:
                    result = PIH.DATA.VARIABLE.value(name, True)
                    if raise_exception_if_not_exist and n(result):
                        raise NotFound(
                            js(("Переменная окружения", esc(name), "не найдена!"))
                        )
                    return result

            class SECTIONS(Enum):
                VARIABLE: str = "variable"
                TIMESTAMP: str = "timestamp"
                TIMESTAMP_EXPIRED: str = "timestamp_expired"

            @staticmethod
            def remove(
                name: str | StorageVariableHolder, section: SECTIONS | None = None
            ) -> None:
                if isinstance(name, StorageVariableHolder):
                    name = name.key_name
                index: int = name.find(PIH.DATA.VARIABLE.SECTION_DELIMITER)
                if index != -1:
                    return PIH.DATA.VARIABLE.remove(
                        name[index + len(PIH.DATA.VARIABLE.SECTION_DELIMITER) :],
                        name[0:index],
                    )
                PIH.ACTION.DATA_STORAGE.value(
                    None,
                    name,
                    section,
                )

            @staticmethod
            def set(
                name: str,
                value: Any,
                description: str | None = None,
                section: SECTIONS | str | None = None,
            ) -> Any:
                section = section or PIH.DATA.VARIABLE.SECTIONS.VARIABLE
                index: int = name.find(PIH.DATA.VARIABLE.SECTION_DELIMITER)
                if index != -1:
                    return PIH.DATA.VARIABLE.set(
                        name[index + len(PIH.DATA.VARIABLE.SECTION_DELIMITER) :],
                        value,
                        description,
                        name[0:index],
                    )
                PIH.ACTION.DATA_STORAGE.value(
                    StorageVariableHolder(name, value, description),
                    name,
                    EnumTool.get(section),
                )
                return value

            @staticmethod
            def get(
                name: str | None = None, section: SECTIONS | None = None
            ) -> StorageVariableHolder | list[StorageVariableHolder] | None:
                section = section or PIH.DATA.VARIABLE.SECTIONS.VARIABLE
                section_name: str | None = EnumTool.get(section)
                data: dict[str, Any] | list[dict[str, Any]] | None = (
                    PIH.RESULT.DATA_STORAGE.value(
                        name,
                        None if n(name) else StorageVariableHolder,
                        section_name,
                    ).data
                )

                def convert(
                    value_holder: StorageVariableHolder | None,
                ) -> StorageVariableHolder | None:
                    if e(value_holder):
                        return value_holder
                    if value_holder.section == EnumTool.get(
                        PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED
                    ):
                        value_holder.default_value = DataTool.fill_data_from_source(
                            ExpiredTimestampVariableHolder(), value_holder.default_value
                        )
                    return value_holder

                if n(name):
                    result: list[StorageVariableHolder] = []
                    for item in data:
                        value_holder: StorageVariableHolder = (
                            DataTool.fill_data_from_source(
                                StorageVariableHolder(section=section_name),
                                data[item],
                                skip_not_none=True,
                            )
                        )
                        result.append(convert(value_holder))
                    return result
                if nn(data):
                    data.section = section_name
                return convert(data)

            @staticmethod
            def find(
                name: str | Enum | None = None,
                sections: list[str] | str | list[SECTIONS] | SECTIONS | None = None,
            ) -> list[MATERIALIZED_RESOURCES.TYPES | SETTINGS | StorageVariableHolder]:
                if isinstance(name, Enum):
                    name = name.name
                result: list[StorageVariableHolder] = []
                section_name_list = (
                    None
                    if e(sections)
                    else list(
                        map(
                            lambda item: (
                                EnumTool.get(item)
                                if isinstance(item, PIH.DATA.VARIABLE.SECTIONS)
                                else item
                            ),
                            sections if isinstance(sections, list) else [sections],
                        )
                    )
                ) or list(
                    map(lambda item: EnumTool.get(item), PIH.DATA.VARIABLE.SECTIONS)
                )
                for section_name_item in section_name_list:
                    for item in PIH.DATA.VARIABLE.get(section=section_name_item):
                        item: StorageVariableHolder = item
                        if (
                            e(name)
                            or StringTool.contains(item.key_name, name)
                            or StringTool.contains(item.description, name)
                        ):
                            """if len(section_name_list) > 1:
                            item.key_name = j(
                                (section_name_item, item.key_name), PIH.DATA.VARIABLE.SECTION_DELIMITER_ALT)
                            """
                            item.section = section_name_item
                            result.append(item)
                return (
                    (
                        PIH.DATA.MATERIALIZED_RESOURCES.find(name)
                        + PIH.SETTINGS.find(name)
                    )
                    if e(sections)
                    else []
                ) + result

            @staticmethod
            def link(name: str) -> Any:
                return PIH.DATA.FORMAT.variable(
                    name
                    if name.startswith("{") and name.endswith("}")
                    else j(("{", name, "}"))
                )

            @staticmethod
            def value(
                variable_name: str,
                from_environment_only: bool = False,
                section: str | SECTIONS | None = None,
            ) -> Any | None:
                result: Any = PIH.DATA.VARIABLE.value_with_section(
                    variable_name, from_environment_only, section
                )
                return result if from_environment_only else result[0]

            @staticmethod
            def value_with_section(
                variable_name: str,
                from_environment_only: bool = False,
                section: str | SECTIONS | None = None,
            ) -> tuple[Any | None, SECTIONS]:
                section = EnumTool.get(section)
                variable_name = variable_name.replace(
                    PIH.DATA.VARIABLE.SECTION_DELIMITER_ALT,
                    PIH.DATA.VARIABLE.SECTION_DELIMITER,
                )
                index: int = variable_name.find(PIH.DATA.VARIABLE.SECTION_DELIMITER)
                if index != -1:
                    return PIH.DATA.VARIABLE.value_with_section(
                        variable_name[
                            index + len(PIH.DATA.VARIABLE.SECTION_DELIMITER) :
                        ],
                        from_environment_only,
                        variable_name[0:index],
                    )
                environment_variable_handler: Callable[[str], Any] = (
                    PIH.OS.environment_variable
                )
                if from_environment_only:
                    return environment_variable_handler(variable_name)

                def get_value(
                    variable_name: str, section: PIH.DATA.VARIABLE.SECTIONS | str
                ) -> Any | None:
                    if section == PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED:
                        return PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(variable_name)
                    return DataTool.if_not_empty(
                        PIH.DATA.VARIABLE.get(variable_name, section),
                        lambda item: item.default_value,
                    )

                def is_in_section(
                    value: str | None, section: PIH.DATA.VARIABLE.SECTIONS
                ) -> bool:
                    return value == EnumTool.get(section) or e(value)

                for value in (
                    environment_variable_handler(variable_name),
                    (
                        get_value(variable_name, PIH.DATA.VARIABLE.SECTIONS.VARIABLE)
                        if is_in_section(section, PIH.DATA.VARIABLE.SECTIONS.VARIABLE)
                        else None
                    ),
                    (
                        get_value(variable_name, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP)
                        if is_in_section(section, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP)
                        else None
                    ),
                    (
                        get_value(
                            variable_name, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED
                        )
                        if is_in_section(
                            section, PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED
                        )
                        else None
                    ),
                    PIH.DATA.MATERIALIZED_RESOURCES.get_count(variable_name),
                    PIH.SETTINGS.get(variable_name),
                ):
                    if nn(value):
                        break
                if section not in DataTool.to_list(PIH.DATA.VARIABLE.SECTIONS):
                    value = get_value(variable_name, section)
                return (
                    value,
                    EnumTool.get_by_value(PIH.DATA.VARIABLE.SECTIONS, section),
                )

        class ACTIONS:
            @staticmethod
            def get(action_or_name: str | Actions) -> Actions | None:
                action: Actions | None = (
                    None if isinstance(action_or_name, str) else action_or_name
                )
                if n(action):
                    action_or_name = action_or_name.lower()
                    for item in Actions:
                        if (
                            item.name.lower() == action_or_name
                            or item.value.name.lower() == action_or_name
                            or action_or_name
                            in DataTool.map(lambda item: item.lower(), item.value.alias)
                        ):
                            action = item
                            break
                return action

        class MATERIALIZED_RESOURCES:
            @staticmethod
            def find(value: str | None) -> list[MATERIALIZED_RESOURCES.TYPES]:
                result: list[MATERIALIZED_RESOURCES.TYPES] = []
                for item in MATERIALIZED_RESOURCES.TYPES:
                    if (
                        n(value)
                        or StringTool.contains(item.name, value)
                        or StringTool.contains(item.value.key_name, value)
                        or StringTool.contains(item.value.description, value)
                    ):
                        result.append(item)
                return result

            @staticmethod
            def get_count(type_value: MATERIALIZED_RESOURCES.TYPES | str) -> int:
                return PIH.RESULT.DATA_STORAGE.value(
                    if_else(
                        isinstance(type_value, str), type_value, lambda: type_value.name
                    ),
                    None,
                    MATERIALIZED_RESOURCES.NAME,
                ).data

            @staticmethod
            def set_count(type_value: MATERIALIZED_RESOURCES.TYPES, value: int) -> bool:
                return PIH.ACTION.DATA_STORAGE.value(
                    value, type_value.name, MATERIALIZED_RESOURCES.NAME
                )

            @staticmethod
            def add_count(type_value: MATERIALIZED_RESOURCES.TYPES, value: int) -> bool:
                return PIH.ACTION.DATA_STORAGE.value(
                    PIH.DATA.MATERIALIZED_RESOURCES.get_count(type_value) + value,
                    type_value.name,
                    MATERIALIZED_RESOURCES.NAME,
                )

        @staticmethod
        def save_base64_as_image(path: str, content: str) -> bool:
            with open(path, "wb") as file:
                file.write(base64.decodebytes(bytes(content, "utf-8")))
                return True
            return False

        @staticmethod
        def uuid() -> str:
            return str(uuid.uuid4().hex)

        class USER:
            @staticmethod
            def by_login(
                value: str, active: bool | None = None, cached: bool | None = None
            ) -> User:
                return PIH.RESULT.USER.by_login(value, active, cached).data

            @staticmethod
            def by_name(value: str) -> list[User]:
                return PIH.RESULT.USER.by_name(value).data

        class MARK:
            @staticmethod
            def by_tab_number(value: str | int) -> User:
                return PIH.RESULT.MARK.by_tab_number(value).data

        class SETTINGS:
            @staticmethod
            def get(value: SETTINGS) -> Any:
                return PIH.RESULT.SETTINGS.get(value).data

        class FILTER:
            @staticmethod
            def symbols_only_in(value: str, check_value: str) -> str:
                return "".join(c for c in value if c in check_value)

            @staticmethod
            def users_by_dn(value: list[User], dn: str) -> list:
                return DataTool.filter(
                    lambda item: item.distinguishedName.find(dn) != -1, value
                )

            @staticmethod
            def computers_with_property(
                list: list[ComputerDescription], value: AD.WSProperies
            ) -> list[ComputerDescription]:
                def filter_function(computer: ComputerDescription) -> bool:
                    return BM.has(computer.properties, EnumTool.get(value))

                return DataTool.filter(filter_function, list)

        class EXTRACT:
            @staticmethod
            def command_type(value: str | File) -> CommandTypes:
                if isinstance(value, File):
                    return PIH.DATA.EXTRACT.command_type(value.title)
                value = value.split(SPLITTER)[0]
                for item in CommandTypes:
                    if value.lower() in DataTool.map(
                        lambda item: item.lower(), EnumTool.get(item)[1:]
                    ):
                        return item
                return None

            @staticmethod
            def new_mail_message(value: dict) -> NewMailMessage:
                return DataTool.fill_data_from_source(NewMailMessage(), value)

            @staticmethod
            def mailbox_info(value: dict | None) -> MailboxInfo | None:
                if n(value):
                    return None
                result: MailboxInfo = DataTool.fill_data_from_source(
                    MailboxInfo(), value
                )
                result.timestamp = DateTimeTool.datetime_from_string(result.timestamp)
                return result

            @staticmethod
            def polibase_person(value: dict | None) -> PolibasePerson | None:
                if n(value):
                    return None
                polibase_person: PolibasePerson = DataTool.fill_data_from_source(
                    PolibasePerson(), value
                )
                polibase_person.Birth = DateTimeTool.datetime_from_string(
                    polibase_person.Birth
                )
                polibase_person.registrationDate = DateTimeTool.datetime_from_string(
                    polibase_person.registrationDate
                )
                return polibase_person

            @staticmethod
            def datetime(value: str | None, format: str) -> datetime | None:
                if e(value):
                    return None
                result: datetime | None = None
                try:
                    result = DateTimeTool.datetime_from_string(value, format)
                except ValueError as error:
                    date_extract_pattern: str = "[0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}"
                    date_list: list[str] = re.findall(date_extract_pattern, value)
                    if ne(date_list):
                        result = PIH.DATA.EXTRACT.datetime(date_list[0], format)
                return result

            @staticmethod
            def boolean(value: int | str | None) -> bool | None:
                if e(value):
                    return False
                if isinstance(value, str):
                    value = value.lower()
                    if value in ["1", "yes", "да"]:
                        return True
                    if value in ["0", "no", "нет"]:
                        return True
                if isinstance(value, int):
                    if value == 1:
                        return True
                    if value == 0:
                        return False
                return None

            @staticmethod
            def service_information(
                value: dict | ServiceInformation,
            ) -> ServiceInformation:
                service_information: ServiceInformation = (
                    DataTool.fill_data_from_source(ServiceInformation(), value)
                    if isinstance(value, dict)
                    else value
                )
                if ne(service_information.subscribtions):
                    service_information.subscribtions = (
                        DataTool.fill_data_from_list_source(
                            Subscribtion, service_information.subscribtions
                        )
                    )
                return service_information

            @staticmethod
            def wappi_telephone_number(value: Any) -> str:
                if isinstance(value, str):
                    return PIH.DATA.FORMAT.telephone_number(
                        value.split(CONST.MESSAGE.WHATSAPP.WAPPI.CONTACT_SUFFIX)[0]
                    )
                if isinstance(value, dict):
                    return PIH.DATA.FORMAT.telephone_number(value["user"])

            class EVENT:
                @staticmethod
                def parameter(
                    event_ds: EventDS | None, param_item: ParamItem
                ) -> Any | None:
                    if n(event_ds):
                        return None
                    event: Events = EnumTool.get(Events, event_ds.name)
                    event_description: EventDescription = EnumTool.get(event)
                    param_index: int = event_description.params.index(param_item)
                    if param_index == -1 or param_index >= len(event_ds.parameters):
                        return None
                    for index, name in enumerate(event_ds.parameters):
                        if index == param_index:
                            return event_ds.parameters[name]

                @staticmethod
                def whatsapp_message(
                    value: ParameterList,
                ) -> WhatsAppMessage | None:
                    allow: bool = PIH.DATA.EXTRACT.subscribtion_result(value).result
                    message: WhatsAppMessage | None = None
                    if allow:
                        event, parameters = PIH.DATA.EXTRACT.EVENT.with_parameters(
                            value
                        )
                        if event == Events.WHATSAPP_MESSAGE_RECEIVED:
                            message = DataTool.fill_data_from_source(
                                WhatsAppMessage(), parameters[0]
                            )
                            if ne(message.message):
                                message.message = unquote(message.message)
                    return message

                @staticmethod
                def action(value: dict[str, Any]) -> ActionWasDone:
                    action: ActionWasDone = DataTool.fill_data_from_source(
                        ActionWasDone(),
                        PIH.EVENT.get_parameter(Events.ACTION_WAS_DONE, value),
                        copy_by_index=True,
                    )
                    action.action = EnumTool.get(Actions, action.action)
                    return action

                @staticmethod
                def get(value: ParameterList) -> Events:
                    event_content: Any | list[Any] = (
                        value.list[0]
                        if PIH.DATA.CHECK.has_subscribtion_result(value)
                        else value.list
                    )
                    return EnumTool.get(Events, event_content[0])

                @staticmethod
                def with_parameters(
                    value: ParameterList,
                ) -> tuple[Events, list[Any]]:
                    event_data: Any | list[Any] = (
                        value.list[0]
                        if PIH.DATA.CHECK.has_subscribtion_result(value)
                        else value.list
                    )
                    event: Events = EnumTool.get(Events, event_data[0])
                    parameters: dict[str, Any] = event_data[1]
                    result_parameters: list[Any] = []
                    if ne(event.value.params):
                        for event_parameters_description in event.value.params:
                            event_parameters_description: ParamItem = (
                                event_parameters_description
                            )
                            if event_parameters_description.optional:
                                if DataTool.is_in(
                                    parameters, event_parameters_description.name
                                ):
                                    result_parameters.append(
                                        parameters[event_parameters_description.name]
                                    )
                                else:
                                    result_parameters.append(None)
                            else:
                                result_parameters.append(
                                    parameters[event_parameters_description.name]
                                )
                    return event, result_parameters

                @staticmethod
                def parameters(
                    value: ParameterList,
                ) -> list[Any]:
                    return PIH.DATA.EXTRACT.EVENT.with_parameters(value)[1]

            @staticmethod
            def subscribtion_result(
                pl: ParameterList,
            ) -> SubscribtionResult | None:
                def extract() -> SubscriberInformation:
                    result: SubscribtionResult = DataTool.fill_data_from_source(
                        SubscribtionResult(), pl.list[-1]
                    )
                    if isinstance(result.result, str):
                        try:
                            result.result = DataTool.rpc_unrepresent(result.result)
                        except Exception as _:
                            pass
                    return result

                return (
                    None
                    if e(pl.list) or not PIH.DATA.CHECK.has_subscribtion_result(pl)
                    else extract()
                )

            @staticmethod
            def parameter_list(value: ParameterList) -> ParameterList:
                return (
                    ParameterList(value.get())
                    if PIH.DATA.CHECK.has_subscribtion_result(value)
                    else value
                )

            @staticmethod
            def email(value: str) -> str | None:
                email_list: list[str] = re.findall(
                    r"[A-Za-z0-9_%+-.]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,5}", value
                )
                if len(email_list) > 0:
                    return email_list[0]
                return None

            @staticmethod
            def float(value: str) -> float:
                if ne(value):
                    floats: list[str] = re.findall(r"\d+[\.\,]*\d+", value)
                    if len(floats) > 0:
                        return float(floats[0].replace(",", "."))
                return None

            @staticmethod
            def decimal(
                value: str,
                min: int | None = None,
                max: int | None = None,
                simple: bool = False,
            ) -> int | None:
                value = value.strip()
                result: int | None = None
                if simple:
                    try:
                        result = int(value)
                    except ValueError as _:
                        return None
                else:
                    numbers: list[str] = re.findall(r"\d+", value)
                    if ne(numbers):
                        result = int(numbers[0])
                if nn(min) and nn(max) and (result < min or result > max):
                    result = None
                return result

            @staticmethod
            def variables(value: str | None) -> list[str] | None:
                if n(value):
                    return None
                fields: list[str] | None = [
                    name for _, name, _, _ in Formatter().parse(value) if name
                ]
                if e(fields):
                    return None
                return fields

            @staticmethod
            def parameter(object: dict, name: str) -> str:
                return object[name] if name in object else ""

            @staticmethod
            def tab_number(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.TAB_NUMBER
                )

            @staticmethod
            def telephone(user_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    user_object, FIELD_NAME_COLLECTION.TELEPHONE_NUMBER
                )

            @staticmethod
            def login(user_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    user_object, FIELD_NAME_COLLECTION.LOGIN
                )

            @staticmethod
            def name(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.NAME
                )

            @staticmethod
            def dn(user_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(user_object, FIELD_NAME_COLLECTION.DN)

            @staticmethod
            def group_name(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.GROUP_NAME
                )

            @staticmethod
            def group_id(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.GROUP_ID
                )

            @staticmethod
            def as_full_name(mark_object: dict) -> FullName:
                return FullNameTool.fullname_from_string(
                    PIH.DATA.EXTRACT.full_name(mark_object)
                )

            @staticmethod
            def full_name(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.FULL_NAME
                )

            @staticmethod
            def person_id(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.PERSON_ID
                )

            @staticmethod
            def mark_id(mark_object: dict) -> str:
                return PIH.DATA.EXTRACT.parameter(
                    mark_object, FIELD_NAME_COLLECTION.MARK_ID
                )

            @staticmethod
            def description(object: dict) -> str:
                result = PIH.DATA.EXTRACT.parameter(
                    object, FIELD_NAME_COLLECTION.DESCRIPTION
                )
                if isinstance(result, tuple) or isinstance(result, list):
                    return result[0]

            @staticmethod
            def container_dn(user_object: dict) -> str:
                return PIH.DATA.EXTRACT.container_dn_from_dn(
                    PIH.DATA.EXTRACT.dn(user_object)
                )

            @staticmethod
            def container_dn_from_dn(dn: str) -> str:
                return j(dn.split(",")[1:], ",")

        class CONVERT:
            @staticmethod
            def settings_to_datetime(
                item: SETTINGS, format: str = CONST.SECONDLESS_TIME_FORMAT
            ) -> datetime | list[datetime]:
                settings_value: str | list[str] = PIH.SETTINGS.get(item)
                return (
                    PIH.DATA.CONVERT.settings_to_datetime_list(item, format)
                    if isinstance(settings_value, list)
                    else DateTimeTool.datetime_from_string(settings_value, format)
                )

            @staticmethod
            def settings_to_datetime_list(
                item: SETTINGS, format: str = CONST.SECONDLESS_TIME_FORMAT
            ) -> list[datetime]:
                return list(
                    map(
                        lambda item: DateTimeTool.datetime_from_string(item, format),
                        PIH.SETTINGS.get(item),
                    )
                )

            @staticmethod
            def file_to_base64(path: str) -> str | None:
                path = PIH.PATH.adapt_for_linux(path)
                while True:
                    try:
                        with open(path, "rb") as file:
                            return PIH.DATA.CONVERT.bytes_to_base64(file.read())
                    except Exception:
                        pass
                return None

            @staticmethod
            def bytes_to_base64(value: bytes) -> str:
                return PIH.DATA.CONVERT.bytes_to_string(
                    PIH.DATA.CONVERT.to_base64(value)
                )

            @staticmethod
            def to_base64(value: Any) -> str:
                return base64.b64encode(value)

            @staticmethod
            def bytes_to_string(value: bytes) -> str:
                return value.decode("utf-8")

        class STATISTICS:
            NAME: str = "statistics"

            @staticmethod
            def by_name(value: str) -> TimeSeriesStatistics | None:
                def is_equal(value: MATERIALIZED_RESOURCES.TYPES, name: str) -> bool:
                    return EnumTool.get(value).key_name == name or value.name == name

                if is_equal(MATERIALIZED_RESOURCES.TYPES.CHILLER_FILTER, value):
                    return PIH.DATA.STATISTICS.for_chiller_filter()
                return None

            @staticmethod
            def for_chiller_filter() -> TimeSeriesStatistics | None:
                events_result: Result[list[EventDS]] = PIH.RESULT.EVENTS.get(
                    *PIH.EVENT.BUILDER.action_was_done(Actions.CHILLER_FILTER_CHANGING)
                )
                if e(events_result):
                    return None
                datetime_list: list[datetime] = ResultTool.map(
                    lambda event: event.timestamp, events_result
                ).data
                distance: list[timedelta] = []
                for index, _ in enumerate(datetime_list):
                    if index == len(datetime_list) - 1:
                        break
                    value: timedelta = datetime_list[index + 1] - datetime_list[index]
                    distance.append(int(value.total_seconds()))
                return TimeSeriesStatistics(
                    len(events_result),
                    datetime_list,
                    distance,
                    min(distance),
                    max(distance),
                    int(sum(distance) / len(distance)),
                )

        class CHECK:
            class VARIABLE:
                class TIMESTAMP:
                    class EXPIRED:
                        @staticmethod
                        def exists(name: str) -> bool:
                            return ne(PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(name))

                        @staticmethod
                        def exists_by_timestamp(name: str) -> bool:
                            return ne(
                                DataTool.filter(
                                    lambda item: item.timestamp == name,
                                    PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.holder(),
                                )
                            )

            @staticmethod
            def polibase_person_has_new_barcode_format(
                polibase_person: PolibasePerson,
            ) -> bool:
                return not (
                    e(polibase_person.barcode)
                    or polibase_person.barcode.find(POLIBASE.BARCODE.NEW_PREFIX) == -1
                )

            @staticmethod
            def polibase_person_barcode(value: BarcodeInformation) -> bool:
                data: int | None = None
                try:
                    data = int(value.data)
                except ValueError:
                    return False
                return (
                    value.type in POLIBASE.BARCODE.SUPPORT_FORMATS
                    and PIH.CHECK.POLIBASE.person_pin(data)
                )

            @staticmethod
            def has_subscribtion_result(pl: ParameterList) -> bool:
                return (
                    len(pl.list) == 2
                    and DataTool.fill_data_from_source(
                        SubscribtionResult(), pl.list[-1]
                    ).checker
                )

            @staticmethod
            def by_secondless_time(
                value_datetime: datetime, value_str: str | None
            ) -> bool:
                return (
                    False
                    if e(value_str)
                    else DateTimeTool.is_equal_by_time(
                        value_datetime,
                        DateTimeTool.datetime_from_string(
                            value_str, CONST.SECONDLESS_TIME_FORMAT
                        ),
                    )
                )

            @staticmethod
            def empty(value: list | str | dict | tuple | Any | None) -> bool:
                result: bool = e(value)
                if not result:
                    if isinstance(value, str):
                        return e(value.strip())
                return result

            @staticmethod
            def decimal(value: int | str | None) -> bool:
                return nn(value) and (
                    isinstance(value, int)
                    or (isinstance(value, str) and value.isdecimal())
                )

            @staticmethod
            def floated(value: float | int | str | None) -> bool:
                return nn(value) and (
                    (isinstance(value, float) or isinstance(value, int))
                    or (
                        isinstance(value, str)
                        and PIH.DATA.CHECK.decimal(value.replace(".", ""))
                    )
                )

            class INDICATIONS:
                @staticmethod
                def chiller_value_actual(
                    value_container: ChillerIndicationsValueContainer,
                ) -> bool:
                    return (
                        DateTimeTool.now()
                        - DateTimeTool.datetime_from_string(
                            value_container.timestamp, CONST.ISO_DATETIME_FORMAT
                        )
                    ).total_seconds() // 60 <= INDICATIONS.CHILLER.ACTUAL_VALUES_TIME_DELTA_IN_MINUTES

                @staticmethod
                def chiller_value_valid(value: ChillerIndicationsValue) -> bool:
                    return ne(value.temperature)

        class FORMAT:
            @staticmethod
            def to_mysql(value: str) -> str:
                return json.dumps(value, ensure_ascii=False)[1:-1].replace("'", "<%>")

            @staticmethod
            def from_mysql(value: str) -> str:
                return value.replace("<%>", "'")

            @staticmethod
            def full_name(value: str) -> str:
                return js(
                    (
                        DataTool.map(
                            StringTool.capitalize,
                            ListTool.not_empty_items(
                                DataTool.map(
                                    lambda item: str(item).strip(),
                                    value.split(FullNameTool.SPLIT_SYMBOL),
                                )
                            ),
                        )
                    )
                )

            class BACKUP:
                SPLITTER: str = "::"

                @staticmethod
                def job_full_name(name: str, source: str, destination: str) -> str:
                    return j(
                        (source, destination, name), PIH.DATA.FORMAT.BACKUP.SPLITTER
                    )

                @staticmethod
                def job_status_name(name: str, source: str, destination: str) -> str:
                    return j(
                        (
                            "robocopy_job_status",
                            PIH.DATA.FORMAT.BACKUP.job_full_name(
                                name, source, destination
                            ),
                        ),
                        PIH.DATA.FORMAT.BACKUP.SPLITTER,
                    )

            @staticmethod
            def donain(value: str) -> str:
                return if_else(
                    value.endswith(AD.DOMAIN_DNS),
                    value,
                    lambda: j((value, AD.DOMAIN_DNS), "."),
                )

            @staticmethod
            def login(value: str) -> str:
                return j((AD.DOMAIN_NAME, value), "\\")

            @staticmethod
            def variable(
                value: str | None, from_environment: bool = False
            ) -> str | None:
                if n(value):
                    return value
                variable_name_list: list[str] | None = PIH.DATA.EXTRACT.variables(value)
                if e(variable_name_list):
                    return None
                variable_name: str = variable_name_list[0]
                return (
                    PIH.DATA.VARIABLE.ENVIRONMENT.value(variable_name)
                    if from_environment
                    else PIH.DATA.VARIABLE.value(variable_name)
                )

            @staticmethod
            def variable_name(value: str) -> str:
                value = value.lower()
                return re.sub("[\\\\.\\-@:]", "_", value)

            @staticmethod
            def statistics(value: MATERIALIZED_RESOURCES.TYPES) -> str | None:
                statistics: TimeSeriesStatistics | None = PIH.DATA.STATISTICS.by_name(
                    value.name
                )
                if n(statistics):
                    return None
                count: int = PIH.DATA.MATERIALIZED_RESOURCES.get_count(value)

                def to_days(value: int) -> int:
                    return int(DateTimeTool.seconds_to_days(value))

                return j(
                    (
                        "Остаток по времени (дней):",
                        f" {CONST.VISUAL.BULLET} Максимально: {count * to_days(statistics.max)}",
                        f" {CONST.VISUAL.BULLET} Минимально: {count * to_days(statistics.min)}",
                        f" {CONST.VISUAL.BULLET} В среднем: {count * to_days(statistics.avg)}",
                    ),
                    "\n",
                )

            @staticmethod
            def yes_no(value: bool, symbolic: bool = False) -> str:
                c: Callable[
                    [
                        bool,
                        Callable[[None], Any | None] | Any,
                        Callable[[None], Any | None] | Any,
                    ],
                    Any,
                ] = DataTool.check
                return c(
                    value,
                    c(symbolic, CONST.VISUAL.YES, "Да"),
                    c(symbolic, CONST.VISUAL.NO, "Нет"),
                )

            @staticmethod
            def size(
                value: int | float, round_value: int = 0, use_megabites: bool = False
            ) -> str:
                value = value / 1024 / 1024 / (1 if use_megabites else 1024)
                return js(
                    (
                        str(
                            round(value, round_value)
                            if round_value == 0
                            else int(value)
                        ),
                        "Мб" if use_megabites else "Гб",
                    )
                )

            @staticmethod
            def format(
                value: str,
                parameters: dict[str, Any] | None = None,
                use_python: bool = False,
            ) -> str:
                result_parameters: dict[str, Any] = globals()
                # result_parameters["print"] = print
                if nn(parameters):
                    for lkey, lvalue in parameters.items():
                        result_parameters[lkey] = lvalue
                io: StringIO = StringIO()
                part: str
                for part in re.findall(
                    r"(\{['\"\,.*?\w\n\[\]\(\)\/:=+\-\!\\ а-яА-Я#]*\})", value
                ):
                    try:
                        if use_python or ne(re.findall(r"print\(.*?\)", part)):
                            io.truncate(0)
                            io.seek(0)
                            with redirect_stdout(io):
                                exec(part[1:-1], globals(), result_parameters)
                            value = value.replace(part, io.getvalue().strip())
                            continue
                    except Exception as error:
                        pass
                    if part.find(PIH.DATA.VARIABLE.SECTION_DELIMITER_ALT) != -1:
                        value = value.replace(
                            part,
                            part.replace(
                                PIH.DATA.VARIABLE.SECTION_DELIMITER_ALT,
                                PIH.DATA.VARIABLE.SECTION_DELIMITER,
                            ),
                        )
                field_list: list[str] = [
                    name for _, name, _, _ in Formatter().parse(value) if name
                ]
                formatter: dict[str, str] = {}
                for field_item in field_list:
                    formatter[field_item] = PIH.DATA.FORMAT.by_formatter_name(
                        field_item, None
                    )
                if e(formatter):
                    return value
                return value.format(**formatter)

            @staticmethod
            def index(value: int) -> str:
                return str(value + 1) if value > 0 else ""

            @staticmethod
            def user_principal_name(login: str) -> str:
                return j((login, AD.DOMAIN_MAIN), EMAIL.SPLITTER)

            @staticmethod
            def as_string(
                value: Any,
                escaped_string: bool = False,
                mapper: Callable[[Any], str] | None = None,
            ) -> str | None:
                result: str | None = None
                if isinstance(value, Enum):
                    result = value.name
                else:
                    result = str(value)
                if escaped_string:
                    if isinstance(value, (str, datetime, Enum)):
                        result = escs(result)
                    if isinstance(value, dict):
                        result = escs(DataTool.rpc_represent(value, False))
                return DataTool.check_not_none(mapper, lambda: mapper(result), result)

            @staticmethod
            def host(
                value: str, reverse: bool = False, use_default_domain: bool = True
            ) -> str:
                value = value.lower()
                host_start: str = r"\\"
                if reverse:
                    return ListTool.not_empty_items(
                        j(j(value.replace("\\", ":")).replace("/", ":")).split(":")
                    )[0]
                if use_default_domain and not value.endswith(AD.DOMAIN_MAIN):
                    value = j((value, AD.DOMAIN_MAIN), AD.SPLITTER)
                return ("" if value.startswith(host_start) else host_start) + value

            @staticmethod
            def host_name(value: str) -> str:
                return value.split(".")[0]

            @staticmethod
            def get_chiller_indications_value_image_name(
                datetime: datetime | str,
            ) -> str:
                if isinstance(datetime, str):
                    datetime = PIH.DATA.datetime_from_string(
                        datetime, CONST.ISO_DATETIME_FORMAT
                    )
                return PIH.PATH.replace_prohibited_symbols_from_path_with_symbol(
                    PIH.DATA.datetime_to_string(
                        datetime, CONST.DATETIME_SECOND_ZEROS_FORMAT
                    )
                )

            @staticmethod
            def by_formatter_name(value: Enum | str, data: Any | None) -> str | None:
                if isinstance(value, str):
                    value = EnumTool.get_by_value(DATA.FORMATTER, value) or value
                if isinstance(value, str):
                    name: str = j((PIH.DATA.STATISTICS.NAME, "_"))
                    index: int = value.lower().find(name)
                    if index != -1:
                        index += len(name)
                        value: MATERIALIZED_RESOURCES.TYPES | None = (
                            EnumTool.get_by_value_or_key(
                                MATERIALIZED_RESOURCES.TYPES, value[index:].upper()
                            )
                        )
                        if n(value):
                            return None
                        return PIH.DATA.FORMAT.statistics(value)
                if isinstance(value, str):
                    result: Any | None = None
                    section: PIH.DATA.VARIABLE.SECTIONS | None = None
                    result, section = PIH.DATA.VARIABLE.value_with_section(value)
                    if section == PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP_EXPIRED:
                        result: ExpiredTimestampVariableHolder = result
                        return js(
                            (
                                PIH.DATA.FORMAT.datetime(
                                    PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.value(result),
                                    CONST.DATE_FORMAT,
                                ),
                                "(ещё",
                                PIH.DATA.VARIABLE.TIMESTAMP.EXPIRED.left_life_time(
                                    result
                                ),
                                "дней)",
                            )
                        )
                    if section == PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP:
                        return PIH.DATA.FORMAT.datetime(result, CONST.DATE_FORMAT)
                    return result
                if value == DATA.FORMATTER.MY_DATETIME:
                    return PIH.DATA.FORMAT.datetime(data)
                if value == DATA.FORMATTER.MY_DATE:
                    return PIH.DATA.FORMAT.date(data)
                if value == DATA.FORMATTER.CHILLER_FILTER_COUNT:
                    return str(
                        PIH.DATA.MATERIALIZED_RESOURCES.get_count(
                            MATERIALIZED_RESOURCES.TYPES.CHILLER_FILTER
                        )
                    )
                if value == DATA.FORMATTER.CHILLER_INDICATIONS_VALUE_INDICATORS:
                    result_list: list[str] = []
                    for index in range(len(INDICATIONS.CHILLER.INDICATOR_NAME)):
                        if BM.has_index(data, index):
                            result_list.append(
                                js(
                                    (
                                        CONST.VISUAL.BULLET,
                                        INDICATIONS.CHILLER.INDICATOR_NAME[index],
                                    )
                                )
                            )
                    return jnl((nl(), jnl(result_list), ""))
                return None

            @staticmethod
            def polibase_person_card_registry_folder(value: str) -> str:
                return value.upper()

            @staticmethod
            def mobile_helper_command(value: str) -> str:
                return value.lower()

            @staticmethod
            def mobile_helper_qr_code_text(value: str) -> str:
                return PIH.DATA.FORMAT.whatsapp_send_message_to(
                    PIH.DATA.FORMAT.telephone_number_international(
                        PIH.DATA.TELEPHONE_NUMBER.it_administrator()
                    ),
                    quote_plus(js((PIH.NAME, value))),
                )

            @staticmethod
            def whatsapp_send_message_to(telephone_number: str, message: str) -> str:
                return CONST.MESSAGE.WHATSAPP.SEND_MESSAGE_TO_TEMPLATE.format(
                    telephone_number, message.replace(" ", "+")
                )

            @staticmethod
            def whatsapp_send_message_to_it(message: str) -> str:
                keyword_found: bool = False
                for item in [PIH.NAME, PIH.NAME_ALT]:
                    keyword_found = message.lower().startswith(item)
                    if keyword_found:
                        break
                if not keyword_found:
                    message = js((PIH.NAME, message))
                return PIH.DATA.FORMAT.whatsapp_send_message_to(
                    PIH.DATA.FORMAT.telephone_number_international(
                        PIH.DATA.TELEPHONE_NUMBER.it_administrator()
                    ),
                    message,
                )

            @staticmethod
            def string(value: str | None) -> str:
                return ("" or value).lower().replace('"', "")

            @staticmethod
            def telephone_number(
                value: str | None, prefix: str = CONST.TELEPHONE_NUMBER_PREFIX
            ) -> str | None:
                if e(value) or value.endswith(CONST.MESSAGE.WHATSAPP.GROUP_SUFFIX):
                    return value
                if prefix != CONST.TELEPHONE_NUMBER_PREFIX:
                    value = value[value.find(prefix) :]
                src_value: str = value
                if ne(value):
                    value = re.sub("[\\-\\(\\) ]", "", value)
                    if value.startswith(prefix):
                        value = value[len(prefix) :]
                    if len(value) == 0:
                        return src_value
                    value = prefix + (
                        value[1:]
                        if (
                            value[0] == "8"
                            or value[0] == CONST.INTERNATIONAL_TELEPHONE_NUMBER_PREFIX
                        )
                        else value
                    )
                    pattern: str = (
                        ("^\\" if prefix[0] == "+" else "^") + prefix + "[0-9]{10}"
                    )
                    matcher: re.Match = re.match(pattern, value)
                    if matcher is not None:
                        return matcher.group(0)
                    else:
                        return src_value
                else:
                    return src_value

            @staticmethod
            def telephone_number_international(value: str) -> str:
                return PIH.DATA.FORMAT.telephone_number(
                    value, CONST.INTERNATIONAL_TELEPHONE_NUMBER_PREFIX
                )

            @staticmethod
            def email(
                value: str,
                use_default_domain: bool = False,
                email_correction: bool = False,
            ) -> str:
                if use_default_domain and value.find(EMAIL.SPLITTER) == -1:
                    value = PIH.DATA.FORMAT.email(
                        j((value, ADDRESSES.SITE_ADDRESS), EMAIL.SPLITTER)
                    )
                if email_correction:
                    for char in '"(),:;<>[\\] ':
                        value = value.replace(char, "")
                    value = value.replace("/", ".")
                    print("email", value)
                    email_name, email_domain = value.split(EMAIL.SPLITTER)
                    PIH.RESULT.FILES.execute_file("@email_correction")
                    for email_correction_item in EMAIL_CORRECTION:
                        if email_domain in email_correction_item[0]:
                            email_domain = email_correction_item[1]
                            break
                    value = j((email_name, email_domain), EMAIL.SPLITTER)
                return value.lower()

            @staticmethod
            def name(
                value: str,
                remove_non_alpha: bool = False,
                name_part_minimal_length: int | None = None,
            ) -> str:
                name_part_list: list[str] = DataTool.filter(
                    lambda item: len(item)
                    > (
                        0
                        if name_part_minimal_length is None
                        else name_part_minimal_length - 1
                    ),
                    value.split(" "),
                )
                if len(name_part_list) == 1:
                    value = value.lower()
                    value = re.sub("[^а-я]+", "", value) if remove_non_alpha else value
                    if len(value) > 1:
                        value = StringTool.capitalize(value)
                    return value
                return js(
                    list(
                        map(
                            lambda item: PIH.DATA.FORMAT.name(item, remove_non_alpha),
                            name_part_list,
                        )
                    )
                )

            @staticmethod
            def location_list(
                value: str, remove_first: bool = True, reversed: bool = True
            ) -> list[str]:
                location_list: list[str] = value.split(",")[int(remove_first) :]
                if reversed:
                    location_list.reverse()
                return DataTool.map(lambda item: item.split("=")[-1], location_list)

            @staticmethod
            def get_user_account_control_values(uac: int) -> list[str]:
                result: list[str] = []
                for count, item in enumerate(AD.USER_ACCOUNT_CONTROL):
                    if (pow(2, count) & uac) != 0:
                        result.append(item)
                return result

            @staticmethod
            def description(value: str) -> str:
                return PIH.DATA.FORMAT.description_list(value)[0]

            @staticmethod
            def description_list(value: str) -> list[str]:
                return DataTool.map(lambda item: item.strip(), value.split("|"))

            @staticmethod
            def to_date(value: str) -> str:
                value = value.strip()
                value = value.replace("/", CONST.DATE_PART_DELIMITER)
                value = value.replace(",", CONST.DATE_PART_DELIMITER)
                value = value.replace(" ", CONST.DATE_PART_DELIMITER)
                return value

            @staticmethod
            def date(iso_datetime_value: str | datetime) -> str:
                return DateTimeTool.datetime_to_string(
                    (
                        datetime.fromisoformat(iso_datetime_value)
                        if isinstance(iso_datetime_value, str)
                        else iso_datetime_value
                    ),
                    CONST.DATE_FORMAT,
                )

            @staticmethod
            def datetime(iso_value: str | datetime, format: str | None = None) -> str:
                return DateTimeTool.datetime_to_string(
                    (
                        iso_value
                        if isinstance(iso_value, datetime)
                        else datetime.fromisoformat(iso_value)
                    ),
                    format or CONST.DATETIME_SECOND_ZEROS_FORMAT,
                )

        class TELEPHONE_NUMBER:
            wappi_profile_to_telephone_number_map: dict | None = None
            cache: dict[str, str] = {}

            @staticmethod
            def all(active: bool = True) -> list[str]:
                def filter_function(user: User) -> str:
                    return user.telephoneNumber is not None

                def map_function(user: User) -> str:
                    return PIH.DATA.FORMAT.telephone_number(user.telephoneNumber)

                return ResultTool.map(
                    map_function,
                    ResultTool.filter(
                        filter_function,
                        PIH.RESULT.USER.by_name(AD.SEARCH_ALL_PATTERN, active=active),
                    ),
                ).data

            @staticmethod
            def it_administrator() -> str:
                return PIH.DATA.TELEPHONE_NUMBER.by_login(
                    PIH.DATA.VARIABLE.ENVIRONMENT.value(LINK.ADMINISTRATOR_LOGIN)
                )

            @staticmethod
            def call_centre_administrator() -> str:
                return PIH.DATA.TELEPHONE_NUMBER.by_login(
                    AD.USER.CALL_CENTRE_ADMINISTRATOR
                )

            @staticmethod
            def marketer_administrator() -> str:
                return PIH.DATA.TELEPHONE_NUMBER.by_login(
                    AD.USER.MARKETER_ADMINISTRATOR
                )

            @staticmethod
            def for_wappi(value: Any) -> str | None:
                WP = CONST.MESSAGE.WHATSAPP.WAPPI.Profiles
                value = EnumTool.get_by_value_or_key(WP, value)
                map: dict = (
                    PIH.DATA.TELEPHONE_NUMBER.wappi_profile_to_telephone_number_map
                )
                if n(map):
                    map = {
                        WP.CALL_CENTRE: PIH.DATA.TELEPHONE_NUMBER.call_centre_administrator(),
                        WP.IT: PIH.DATA.TELEPHONE_NUMBER.it_administrator(),
                        WP.MARKETER: PIH.DATA.TELEPHONE_NUMBER.marketer_administrator(),
                    }
                    PIH.DATA.TELEPHONE_NUMBER.wappi_profile_to_telephone_number_map = (
                        map
                    )
                return DataTool.if_is_in(map, value)

            @staticmethod
            def by_login(
                value: str,
                format: bool = True,
                active: bool = True,
                cached: bool = True,
            ) -> str:
                if cached and value in PIH.DATA.TELEPHONE_NUMBER.cache:
                    return PIH.DATA.TELEPHONE_NUMBER.cache[value]

                result: str = PIH.DATA.USER.by_login(
                    value, active, True
                ).telephoneNumber
                result = PIH.DATA.FORMAT.telephone_number(result) if format else result
                PIH.DATA.TELEPHONE_NUMBER.cache[value] = result
                return result

            @staticmethod
            def by_workstation_name(value: str) -> str:
                workstation: Workstation = PIH.RESULT.WORKSTATION.by_name(value).data
                return PIH.DATA.TELEPHONE_NUMBER.by_login(workstation.samAccountName)

            @staticmethod
            def by_mark_tab_number(value: str, format: bool = True) -> str:
                result: str = PIH.DATA.MARK.by_tab_number(value).telephoneNumber
                return PIH.DATA.FORMAT.telephone_number(result) if format else result

            @staticmethod
            def by_polibase_person_pin(value: int, format: bool = True) -> bool:
                result: str = PIH.DATA.POLIBASE.person_by_pin(value).telephoneNumber
                return PIH.DATA.FORMAT.telephone_number(result) if format else result

            @staticmethod
            def by_full_name(value: Any, format: bool = True) -> str:
                value_string: str | None = None
                if isinstance(value, str):
                    value_string = value
                    value = FullNameTool.fullname_from_string(value)
                else:
                    value_string = FullNameTool.fullname_to_string(value)
                telephone_number: str = PIH.RESULT.MARK.by_full_name(
                    value_string, True
                ).data.telephoneNumber
                if PIH.CHECK.telephone_number(telephone_number):
                    return (
                        PIH.DATA.FORMAT.telephone_number(telephone_number)
                        if format
                        else telephone_number
                    )
                telephone_number = PIH.RESULT.USER.by_full_name(
                    value_string, True
                ).data.telephoneNumber
                if PIH.CHECK.telephone_number(telephone_number):
                    return (
                        PIH.DATA.FORMAT.telephone_number(telephone_number)
                        if format
                        else telephone_number
                    )
                details: str = f"Телефон для {value_string} не найден"
                raise NotFound(details)

        class POLIBASE:
            @staticmethod
            def note_title(id: int) -> str:
                field_name: str = "note_title"
                return A.R.get_first_item(
                    PIH.RESULT.POLIBASE.execute(
                        js(
                            (
                                "select",
                                field_name,
                                esc(field_name),
                                "from notes where note_no =",
                                id,
                            )
                        )
                    )
                )[field_name]

            @staticmethod
            def person_by_pin(value: int, test: bool | None = None) -> PolibasePerson:
                return PIH.RESULT.POLIBASE.person_by_pin(value, test).data

            @staticmethod
            def duplicate_persons_by_person(
                person: PolibasePerson, check_for_birth: bool = True
            ) -> list[PolibasePerson]:
                def check_function(check_person: PolibasePerson) -> bool:
                    return check_person.pin != person.pin and (
                        not check_for_birth or check_person.Birth == person.Birth
                    )

                return ResultTool.get_first_item(
                    ResultTool.filter(
                        lambda item: check_function(item),
                        PIH.RESULT.POLIBASE.persons_by_name(person.FullName),
                    )
                )

            @staticmethod
            def unique_by_telephone(value: str) -> PolibasePerson:
                value = PIH.DATA.FORMAT.telephone_number(value)

                def check_function(check_person: PolibasePerson) -> bool:
                    return (
                        PIH.DATA.FORMAT.telephone_number(check_person.telephoneNumber)
                        == value
                    )

                return ResultTool.get_first_item(
                    ResultTool.filter(
                        lambda item: check_function(item),
                        PIH.RESULT.POLIBASE.person_by_telephone_number(value),
                    )
                )

            @staticmethod
            def duplicate_persons_by_person_pin(
                value: int, check_birth: bool = True
            ) -> list[PolibasePerson] | None:
                try:
                    return PIH.DATA.POLIBASE.duplicate_persons_by_person(
                        PIH.RESULT.POLIBASE.person_by_pin(value).data, check_birth
                    )
                except NotFound as _:
                    return None

            @staticmethod
            def sort_person_list_by_pin(
                value: list[PolibasePerson] | PolibasePerson | None = None,
            ) -> list[PolibasePerson] | int | Callable[[PolibasePerson], int]:
                def sort_function(person: PolibasePerson) -> int:
                    return person.pin

                if isinstance(value, PolibasePerson):
                    return sort_function(value)
                if e(value):
                    return sort_function
                value.sort(key=sort_function)
                return value

    class OS:

        @staticmethod
        def stop_windows_service(name: str, workstation_name: str) -> bool | None:
            accessable: bool | None = PIH.CHECK.WORKSTATION.accessibility(
                workstation_name
            )
            if n(accessable):
                return None
            return PIH.EXECUTOR.stop_windows_service(name, workstation_name)

        @staticmethod
        def start_windows_service(name: str, workstation_name: str) -> bool | None:
            accessable: bool | None = PIH.CHECK.WORKSTATION.accessibility(
                workstation_name
            )
            if n(accessable):
                return None
            return PIH.EXECUTOR.start_windows_service(name, workstation_name)

        @staticmethod
        def start_windows_service_if_stopped(
            name: str, workstation_name: str
        ) -> bool | None:
            windows_service_information = name, workstation_name
            if not PIH.CHECK.COMPUTER.windows_service_running(
                *windows_service_information
            ):
                return PIH.OS.start_windows_service(*windows_service_information)
            return None

        @staticmethod
        def host_is_local(value: str | None) -> bool:
            return e(value) or socket.gethostbyname(
                socket.gethostname()
            ) == socket.gethostbyname(value)

        @staticmethod
        def make_sudo(command: str, password: str) -> str:
            return js(("echo -e", password, "| sudo -S", command))

        @staticmethod
        def python_path(host: str | None = None) -> str | None:
            return PIH.EXECUTOR.python_path(host)

        @staticmethod
        def python_version(
            host: str | None = None, host_is_linux: bool | None = None
        ) -> str | None:
            return PIH.EXECUTOR.python_version(host, host_is_linux)

        @staticmethod
        def python_exists(
            host: str | None = None, host_is_linux: bool | None = None
        ) -> bool:
            return ne(PIH.OS.python_version(host, host_is_linux))

        @staticmethod
        def name(host: str | None = None) -> str:
            if n(host):
                return platform.system()
            result: str | None = None
            command: str = "import platform;print(platform.system())"
            if PIH.OS.host_is_local(host):
                host = None
            complete_process: CompletedProcess = PIH.EXECUTOR.execute_python(
                command, host
            )
            if n(
                PIH.EXECUTOR.extract_returncode(complete_process, check_on_success=True)
            ):
                result = PIH.RESULT.SSH.execute_python(command, host).data[0]
            else:
                result = str(complete_process.stdout)
            return result.strip()

        @staticmethod
        @cache
        def is_linux(host: str | None = None) -> bool:
            return PIH.OS.name(host) == "Linux"

        @staticmethod
        def get_login() -> str:
            return os.getlogin()

        @staticmethod
        def host() -> str:
            return platform.node()

        @staticmethod
        def pid() -> int:
            return os.getppid()

        @staticmethod
        def environment_variable(name: str) -> str:
            return os.getenv(name)

        @staticmethod
        def os_name() -> str:
            return PIH.OS.environment_variable("OS")

        @staticmethod
        def domain_dns() -> str:
            return PIH.OS.environment_variable("USERDNSDOMAIN")

        @staticmethod
        def domain() -> str:
            return PIH.OS.environment_variable("USERDOMAIN")

        @staticmethod
        def kill_process(
            name_or_pid: str | int,
            via_standart_tools: bool = True,
            show_output: bool = False,
        ) -> bool:
            return PIH.EXECUTOR.kill_process(
                name_or_pid, None, via_standart_tools, show_output
            )

        @staticmethod
        def kill_process_by_port(
            value: int,
        ) -> bool | None:
            return PIH.EXECUTOR.kill_process_by_port(value)

    class RESULT(ResultTool):
        class JOURNALS:
            @staticmethod
            def get(
                value: JournalType | None = None, tag: Tags | None = None
            ) -> Result[list[JournalRecord]]:
                parameters: tuple = ()
                parameters += (EnumTool.get(tag)[0] if nn(tag) else None,)
                parameters += (EnumTool.get(value)[0] if nn(value) else None,)
                user_cache: dict[str, User] = {}

                def convert(event: EventDS) -> JournalRecord:
                    user: User | None = None
                    login: str = event.parameters[PARAM_ITEMS.LOGIN.name]
                    if login in user_cache:
                        user = user_cache[login]
                    else:
                        user = PIH.DATA.USER.by_login(login)
                        user_cache[login] = user
                    event.parameters[PARAM_ITEMS.TAG.name] = PIH.DATA.JOURNAL.tag_by_id(
                        event.parameters[PARAM_ITEMS.TAG.name]
                    )
                    event.parameters[PARAM_ITEMS.TYPE.name] = (
                        PIH.DATA.JOURNAL.type_by_any(
                            event.parameters[PARAM_ITEMS.TYPE.name]
                        )
                    )
                    title: str | None = event.parameters["title"]
                    try:
                        title: str = PIH.DATA.FORMAT.format(title)
                    except Exception as _:
                        pass
                    text: str | None = event.parameters["text"]
                    try:
                        text: str = PIH.DATA.FORMAT.format(text)
                    except Exception as _:
                        pass
                    return DataTool.fill_data_from_source(
                        JournalRecord(
                            event.timestamp,
                            applicant_user=user,
                            title=title,
                            text=text,
                        ),
                        event.parameters,
                        skip_not_none=True,
                    )

                return ResultTool.map(
                    convert,
                    PIH.RESULT.EVENTS.get(Events.ADD_JOURNAL_RECORD, parameters),
                )

        class EMAIL:
            @staticmethod
            def information(value: str) -> Result[dict[str, Any]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_email_information,
                        (value, EmailVerificationMethods.ABSTRACT_API),
                    )
                )

            """@staticmethod
            def corrected(value: str) -> Result[str | None]:
                result: str = PIH.RESULT.EMAIL.information(value).data["autocorrect"]
                return Result(None, None if e(result) else result)
            """

        class EVENTS:
            @staticmethod
            def get_by_key(
                event_type: Events | None,
                parameters: tuple[Any] | Any | None = None,
                timestamp: datetime | date | str | int | None = None,
                count_as_result: bool = False,
            ) -> Result[list[EventDS] | int]:
                if not isinstance(parameters, (Tuple, List)):
                    parameters = (parameters,)
                return PIH.RESULT.EVENTS.get(
                    *PIH.EVENT.BUILDER.by_key(event_type, parameters),
                    timestamp,
                    count_as_result,
                )

            @staticmethod
            def get(
                event_type: Events | None = None,
                parameters: tuple[Any] | None = None,
                timestamp: datetime | date | str | int | None = None,
                count_as_result: bool = False,
            ) -> Result[list[EventDS] | int]:
                def extract_function(data: Any, count_as_result: bool) -> EventDS | int:
                    if count_as_result:
                        return data
                    result: EventDS = DataTool.fill_data_from_source(EventDS(), data)
                    # from json string to python object
                    result.parameters = DataTool.rpc_unrepresent(result.parameters)
                    if isinstance(result.timestamp, str):
                        result.timestamp = DateTimeTool.datetime_from_string(
                            result.timestamp
                        )
                    return result

                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        (
                            ServiceCommands.get_event_count
                            if count_as_result
                            else ServiceCommands.get_event
                        ),
                        (
                            EventDS(timestamp=timestamp)
                            if n(event_type)
                            else EventDS(
                                event_type.name,
                                PIH.EVENT.BUILDER.create_parameters_map(
                                    event_type,
                                    parameters,
                                    check_for_parameters_count=False,
                                ),
                                timestamp=timestamp,
                            )
                        ),
                    ),
                    lambda data: extract_function(data, count_as_result),
                )

            @staticmethod
            def get_last(
                event_type: Events | None = None,
                parameters: tuple[Any] | None = None,
                count: int = 1,
            ) -> Result[list[EventDS]]:
                return PIH.RESULT.EVENTS.get(event_type, parameters, -abs(count))

            @staticmethod
            def get_last_by_key(
                event_type: Events | None = None,
                parameters: tuple[Any] | None = None,
                count: int = 1,
            ) -> Result[list[EventDS]]:
                return PIH.RESULT.EVENTS.get_by_key(event_type, parameters, -abs(count))

            @staticmethod
            def get_first(
                event_type: Events | None = None,
                parameters: tuple[Any] | None = None,
                count: int = 1,
            ) -> Result[list[EventDS]]:
                return PIH.RESULT.EVENTS.get(event_type, parameters, abs(count))

            @staticmethod
            def get_first_by_key(
                event_type: Events | None = None,
                parameters: tuple[Any] | None = None,
                count: int = 1,
            ) -> Result[list[EventDS]]:
                return PIH.RESULT.EVENTS.get_by_key(event_type, parameters, abs(count))

            @staticmethod
            def get_count(
                event_type: Events | None = None,
                parameters: tuple[Any] | None = None,
            ) -> Result[int]:
                return PIH.RESULT.EVENTS.get(
                    event_type, parameters, count_as_result=True
                )

        class NOTES:
            @staticmethod
            def find_gkeep_item(
                name: str | None = None,
                title: str | None = None,
                full_equaliment: bool = False,
            ) -> Result[list[GKeepItem]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_gkeep_item_list_by_any,
                        (name, title, full_equaliment),
                    ),
                    GKeepItem,
                )

            @staticmethod
            def get(id: str, force_fetch: bool = False) -> Result[Note]:
                event: Events = Events.SAVE_NOTE_FROM_KNOWLEDGE_BASE
                note: Note | None = None
                if force_fetch:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_note, (id, force_fetch)
                        ),
                        Note,
                    )
                else:
                    event_ds: EventDS | None = one(
                        PIH.RESULT.EVENTS.get_by_key(event, id)
                    )
                    if nn(event_ds):
                        parameters: dict[str, Any] = event_ds.parameters
                        note = Note(
                            PIH.DATA.FORMAT.from_mysql(
                                parameters[PARAM_ITEMS.TITLE.name]
                            ),
                            PIH.DATA.FORMAT.from_mysql(
                                parameters[PARAM_ITEMS.TEXT.name]
                            ),
                            parameters[PARAM_ITEMS.ID.name],
                            parameters[PARAM_ITEMS.IMAGES.name],
                        )
                        return Result(data=note)

        class FILES:
            cache: Result[list[File]] | None = None
            last_file_id: int | None = None

            @staticmethod
            def get(
                name: str | None = None,
                command_type: CommandTypes | None = None,
                exclude_private_files: bool = False,
            ) -> Result[list[File]]:
                name = lw(name)
                search_function: Callable[[File], bool] = (
                    lambda item: lw(item.title).find(name) != -1
                )
                event: Events = Events.SAVE_FILE_FROM_KNOWLEDGE_BASE
                if n(PIH.RESULT.FILES.last_file_id):
                    PIH.RESULT.FILES.last_file_id = PIH.DATA.VARIABLE.value(
                        FIELD_NAME_COLLECTION.LAST_ID, False
                    )
                last_file_id: int = one(PIH.RESULT.EVENTS.get_last(event), EventDS()).id
                need_update: bool = last_file_id != PIH.RESULT.FILES.last_file_id
                if need_update:
                    PIH.RESULT.FILES.last_file_id = last_file_id
                    PIH.DATA.VARIABLE.set(FIELD_NAME_COLLECTION.LAST_ID, last_file_id)
                if need_update or n(PIH.RESULT.FILES.cache):
                    PIH.RESULT.FILES.cache = ResultTool.map(
                        lambda item: File(
                            PIH.DATA.FORMAT.from_mysql(item[PARAM_ITEMS.TITLE.name]),
                            PIH.DATA.FORMAT.from_mysql(item[PARAM_ITEMS.TEXT.name]),
                        ),
                        ResultTool.map(
                            lambda item: item.parameters,
                            PIH.RESULT.EVENTS.get(event),
                        ),
                    )
                result: Result[list[File]] = (
                    PIH.RESULT.FILES.cache
                    if n(name)
                    else ResultTool.filter(
                        search_function, PIH.RESULT.FILES.cache, True
                    )
                )
                result = (
                    result
                    if n(command_type)
                    else ResultTool.filter(
                        lambda item: PIH.DATA.EXTRACT.command_type(item)
                        == command_type,
                        result,
                    )
                )
                result = (
                    ResultTool.filter(
                        lambda item: item.title.find(j((SPLITTER, "@"))) == -1, result
                    )
                    if exclude_private_files
                    else result
                )

                def sort_function(value: File) -> str:
                    title_list: list[str] = lw(value.title).split(SPLITTER)
                    return j(
                        [title_list[0]] + [title_list[-1]] + title_list[1:-1], SPLITTER
                    )

                return ResultTool.sort(sort_function, result)

            @staticmethod
            def execute(
                file_search_request: str,
                parameters: dict[str, Any] | None = None,
                stdout_redirect: bool = True,
                catch_exceptions: bool = False,
                use_default_stdout: bool = False,
            ) -> str | None:
                file: File = one(PIH.RESULT.FILES.get(file_search_request))
                if n(file):
                    return None
                return PIH.EXECUTOR.execute_python_localy(
                    file.text,
                    parameters,
                    stdout_redirect,
                    catch_exceptions,
                    use_default_stdout,
                )

            @staticmethod
            def execute_some(
                file_search_request: str,
                parameters: dict[str, Any] | None = None,
                stdout_redirect: bool = True,
                catch_exceptions: bool = False,
                use_default_stdout: bool = False,
            ) -> list[str] | None:
                file: File | None = None
                result: list[str] = []
                file_list: list[File] = PIH.RESULT.FILES.get(file_search_request).data
                if e(file_list):
                    return None
                for file in file_list:
                    result.append(
                        PIH.EXECUTOR.execute_python_localy(
                            file.text,
                            parameters,
                            stdout_redirect,
                            catch_exceptions,
                            use_default_stdout,
                        )
                    )
                return result

        class SSH:
            @staticmethod
            def execute(
                command: str,
                host: str,
                username: str | None = None,
                password: str | None = None,
                use_sudo: bool = False,
                in_background: bool = False,
            ) -> Result[list[str]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.execute_ssh_command,
                        (command, host, username, password, use_sudo, in_background),
                    )
                )

            @staticmethod
            def execute_python(
                command: list[str] | str, host: str, in_background: bool = False
            ) -> Result[list[str]]:
                return PIH.RESULT.SSH.execute(
                    js(
                        (
                            CONST.PYTHON.EXECUTOR3,
                            CONST.PYTHON.COMMAND.FLAG,
                            escs(
                                j(command, ";")
                                if isinstance(command, list)
                                else command
                            ),
                        )
                    ),
                    host,
                    in_background,
                )

            @staticmethod
            def execute_python_file(
                value: str, host: str, in_background: bool = False
            ) -> Result[list[str]]:
                return PIH.RESULT.SSH.execute(
                    js(
                        (
                            CONST.PYTHON.EXECUTOR3,
                            value,
                        )
                    ),
                    host,
                    in_background=in_background,
                )

            @staticmethod
            def get_certificate_information(
                host: str, username: str | None = None, password: str | None = None
            ) -> Result[str | None]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_certificate_information,
                        (host, username, password),
                    )
                )

            @staticmethod
            def get_unix_free_space_information_by_drive_name(
                drive_name: str,
                host: str,
                username: str | None = None,
                password: str | None = None,
            ) -> Result[str | None]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_unix_free_space_information_by_drive_name,
                        (drive_name, host, username, password),
                    )
                )

        class DATA_STORAGE:
            @staticmethod
            def joke() -> Result[str]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.joke,
                    ),
                )

            @staticmethod
            def value(
                name: str | None,
                class_type_holder: T | Callable[[Any], T] | None,
                section: str | None = None,
            ) -> Result[T]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_storage_value, (name, section)
                    ),
                    class_type_holder,
                )

            @staticmethod
            def ogrn(code: str) -> Result[OGRN]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_ogrn_value, (code,)),
                    OGRN,
                )

            @staticmethod
            def fms_unit_name(code: str) -> Result[str]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_fms_unit_name, (code,))
                )

            @staticmethod
            def execute(query: str) -> Result[list[dict[str, Any]]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.execute_data_source_query, (query,)
                    )
                )

        class MESSAGE:
            class DELAYED:
                @staticmethod
                def get(
                    search_condition: MessageSearchCritery | None = None,
                    take_to_work: bool = False,
                ) -> Result[list[DelayedMessageDS]]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.search_delayed_messages,
                            (search_condition, take_to_work),
                        ),
                        DelayedMessageDS,
                    )

        class RECOGNIZE:
            @staticmethod
            def document(
                file_path: str,
                document_type: DocumentTypes,
                class_type: R,
                log_level: int = 0,
            ) -> Result[R]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.recognize_document,
                        (file_path, EnumTool.get(document_type), False, log_level),
                    ),
                    class_type,
                )

            @staticmethod
            def polibase_document(
                file_path: str, log_level: int = 0
            ) -> Result[PolibaseDocument]:
                return PIH.RESULT.RECOGNIZE.document(
                    file_path, DocumentTypes.POLIBASE, PolibaseDocument, log_level
                )

            @staticmethod
            def medical_direction_document(
                file_path: str, log_level: int = 0
            ) -> Result[MedicalDirectionDocument]:
                def action(value: MedicalDirectionDocument) -> None:
                    value.person_birthday = DateTimeTool.date_from_string(
                        value.person_birthday
                    )
                    value.date = DateTimeTool.date_from_string(value.date)

                return ResultTool.every(
                    action,
                    PIH.RESULT.RECOGNIZE.document(
                        file_path,
                        DocumentTypes.MEDICAL_DIRECTION,
                        MedicalDirectionDocument,
                        log_level,
                    ),
                )

            @staticmethod
            def barcodes_information(
                file_path: str, get_only_first_barcode: bool = False, log_level: int = 0
            ) -> Result[list[list[BarcodeInformation]]]:
                def extractor(data: list[dict[str, Any]]) -> list[BarcodeInformation]:
                    return list(
                        map(
                            lambda item: DataTool.fill_data_from_source(
                                BarcodeInformation(), item
                            ),
                            data,
                        )
                    )

                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_barcode_list_information,
                        (file_path, get_only_first_barcode, log_level),
                    ),
                    extractor,
                )

        class RESOURCES:
            @staticmethod
            def get_status_list(
                checkable_section_list: list[CheckableSections] | None = None,
                force_update: bool = False,
                all: bool = False,
            ) -> Result[list[IResourceStatus]]:
                def fill_data(data: dict) -> IResourceStatus:
                    result: IResourceStatus | None = None
                    if "disk_list" in data:
                        result = DisksResourceStatus()
                    elif "check_certificate_status" in data:
                        result = SiteResourceStatus()
                    else:
                        result = ResourceStatus()
                    result = DataTool.fill_data_from_source(
                        result,
                        data,
                    )
                    if isinstance(result, DisksResourceStatus):
                        result.disk_list = DataTool.fill_data_from_list_source(
                            DiskStatistics, result.disk_list
                        )
                    return result

                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_resource_status_list,
                        (
                            (
                                None
                                if e(checkable_section_list)
                                else DataTool.map(
                                    lambda item: item.name, checkable_section_list
                                )
                            ),
                            force_update,
                            all,
                        ),
                    ),
                    fill_data,
                )

            @staticmethod
            def get_resource_status_list(
                force_update: bool = False, all: bool = False
            ) -> Result[list[ResourceStatus]]:
                return PIH.RESULT.RESOURCES.get_status_list(
                    [CheckableSections.RESOURCES], force_update, all
                )

            @staticmethod
            def get_status(
                checkable_section_list: list[CheckableSections],
                resource_desription_or_address: Any,
                force: bool = False,
            ) -> ResourceStatus:
                address: str | None = None
                if isinstance(resource_desription_or_address, ResourceDescription):
                    address = resource_desription_or_address.address
                elif isinstance(resource_desription_or_address, str):
                    address = resource_desription_or_address
                if ne(address):
                    resource_list: list[ResourceStatus] = (
                        PIH.RESULT.RESOURCES.get_status_list(
                            checkable_section_list, force
                        ).data
                    )
                    for item in resource_list:
                        if item.address == address:
                            return item
                return None

            @staticmethod
            def get_resource_status(
                resource_desription_or_address: Any, force: bool = False
            ) -> ResourceStatus:
                return PIH.RESULT.RESOURCES.get_status(
                    [CheckableSections.RESOURCES], resource_desription_or_address, force
                )

        class INDICATIONS:
            class DEVICE:
                @staticmethod
                def get(
                    name: str | None = None,
                ) -> Result[list[IndicationDevice] | IndicationDevice | None]:
                    getter: Callable = (
                        PIH.EVENT.BUILDER.indication_device_was_registered
                    )
                    result: Result[list[IndicationDevice]] = ResultTool.map(
                        lambda event: DataTool.fill_data_from_source(
                            IndicationDevice(), event.parameters
                        ),
                        PIH.RESULT.EVENTS.get(
                            *(
                                (getter(None), None)
                                if n(name)
                                else getter(IndicationDevice(name))
                            )
                        ),
                    )
                    return result if n(name) else ResultTool.with_first_item(result)

            @staticmethod
            def last_ct_value_containers(
                cached: bool, count: int = 1
            ) -> Result[list[CTIndicationsValueContainer]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_last_ct_indications_value_container_list,
                        (cached, count),
                    ),
                    CTIndicationsValueContainer,
                )

            @staticmethod
            def last_chiller_value_containers(
                cached: bool, count: int = 1, valid_values: bool = True
            ) -> Result[list[ChillerIndicationsValueContainer]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_last_сhiller_indications_value_container_list,
                        (cached, count, valid_values),
                    ),
                    ChillerIndicationsValueContainer,
                )

        class BACKUP:
            @staticmethod
            def robocopy_job_status_list() -> Result[list[RobocopyJobStatus]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.robocopy_get_job_status_list
                    ),
                    RobocopyJobStatus,
                )

        class SETTINGS:
            @staticmethod
            def key(key: str, default_value: Any | None = None) -> Result[Any]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_settings_value, (key, default_value)
                    )
                )

            @staticmethod
            def get(settings_item: SETTINGS) -> Result[Any]:
                settings_value: StorageVariableHolder = EnumTool.get(settings_item)
                return PIH.RESULT.SETTINGS.get_by_name(
                    settings_value.key_name or settings_item.name,
                    settings_value.default_value,
                )

            @staticmethod
            def get_by_name(
                value: str, default_value: Any | None = None
            ) -> Result[Any]:
                return PIH.RESULT.SETTINGS.key(value, default_value)

        class SERVER:
            CONTAINER_DN: str = AD.SERVERS_CONTAINER_DN

            @staticmethod
            def all_description() -> Result[list[ComputerDescription]]:
                return PIH.RESULT.COMPUTER.all_description_by_container_dn(
                    PIH.RESULT.SERVER.CONTAINER_DN
                )

            @staticmethod
            def all() -> Result[list[Server]]:
                return PIH.RESULT.COMPUTER.by_container_dn(
                    PIH.RESULT.SERVER.CONTAINER_DN, Server
                )

            @staticmethod
            def by_name(value: str) -> Result[Server]:
                try:
                    return PIH.RESULT.COMPUTER.by_name(
                        value, PIH.RESULT.SERVER.CONTAINER_DN, Server
                    )
                except NotFound as _:
                    raise NotFound(f"Сервер с именем {value} не найден")

        class COMPUTER:
            @staticmethod
            def by_container_dn(
                value: str | None = None, class_type: Any = Computer
            ) -> Result[list[Computer]]:
                def every_action(computer: Computer) -> None:
                    computer.name = computer.name.lower()

                return ResultTool.every(
                    every_action,
                    DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_computer_list,
                            (value,),
                        ),
                        class_type,
                    ),
                )

            @staticmethod
            def all_description_by_container_dn(
                value: str,
            ) -> Result[list[ComputerDescription]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_computer_description_list,
                        (value,),
                    ),
                    ComputerDescription,
                )

            @staticmethod
            def by_name(
                value: str, container_dn: str | None = None, class_type: Any = Computer
            ) -> Result[Computer]:
                value = PIH.DATA.FORMAT.string(value).lower().split(".")[0]
                result: Result[Workstation] = ResultTool.with_first_item(
                    ResultTool.filter(
                        lambda item: item.name.lower() == value,
                        PIH.RESULT.COMPUTER.by_container_dn(container_dn, class_type),
                    )
                )
                if e(result):
                    raise NotFound(f"Компьютер с именем {value} не найден")
                return result

        class WORKSTATION:
            CONTAINER_DN: str = AD.WORKSTATIONS_CONTAINER_DN

            @staticmethod
            def all_description() -> Result[list[ComputerDescription]]:
                return PIH.RESULT.COMPUTER.all_description_by_container_dn(
                    PIH.RESULT.WORKSTATION.CONTAINER_DN
                )

            @staticmethod
            def by_login(value: str) -> Result[list[Workstation]]:
                value = PIH.DATA.FORMAT.string(value)
                if PIH.CHECK.USER.exists_by_login(value):
                    workstation_list_result: Result[list[Workstation]] = (
                        DataTool.to_result(
                            PIH.SERVICE.call_command(
                                ServiceCommands.get_workstation_list_by_user_login,
                                value,
                            ),
                            Workstation,
                        )
                    )
                    workstation_name_collection: list[str] = []

                    def filter_function(worksatation: Workstation) -> bool:
                        worksatation_name: str = worksatation.name.lower()
                        if worksatation_name not in workstation_name_collection:
                            workstation_name_collection.append(worksatation_name)
                            return True
                        return False

                    workstation_list_result += (
                        PIH.RESULT.POLIBASE.workstations_by_login(value)
                    )
                    return ResultTool.filter(filter_function, workstation_list_result)
                else:
                    raise NotFound(f"Пользователь с логином {value} не найден")

            @staticmethod
            def by_internal_telephone_number(value: int) -> Result[Workstation]:
                result: Result[list[Workstation]] = PIH.RESULT.WORKSTATION.all()
                workstation_list: list[Workstation] = result.data
                result_worksation: Workstation | None = None
                for workstation in workstation_list:
                    if ne(workstation.description):
                        index: int = workstation.description.find(
                            CONST.INTERNAL_TELEPHONE_NUMBER_PREFIX
                        )
                        if index != -1:
                            internal_telephone_number_text: str = (
                                workstation.description[index:]
                            )
                            internal_telephone_number: int = PIH.DATA.EXTRACT.decimal(
                                internal_telephone_number_text
                            )
                            if internal_telephone_number == value:
                                result_worksation = workstation
                                break
                if result_worksation is not None:
                    return Result(result.fields, workstation)
                else:
                    raise PIH.ERROR.USER.get_not_found_error(
                        "внутренним номером телефона", True, str(value)
                    )

            @staticmethod
            def by_any(value: int | str | User) -> Result[list[Workstation]]:
                value_is_user: bool = isinstance(value, User)
                if not value_is_user:
                    if PIH.DATA.CHECK.decimal(value):
                        try:
                            return ResultTool.as_list(
                                PIH.RESULT.WORKSTATION.by_internal_telephone_number(
                                    int(value)
                                )
                            )
                        except NotFound as _:
                            return PIH.RESULT.WORKSTATION.by_login(
                                PIH.RESULT.USER.by_tab_number(value).data.samAccountName
                            )
                    if PIH.CHECK.WORKSTATION.name(value):
                        return ResultTool.as_list(PIH.RESULT.WORKSTATION.by_name(value))
                try:
                    if value_is_user:
                        value = value.samAccountName
                    return PIH.RESULT.WORKSTATION.by_login(value)
                except NotFound as _:
                    raise NotFound(f"Компьютер с параметром поиска {value} не найден")

            @staticmethod
            def by_name(value: str) -> Result[Workstation]:
                try:
                    return PIH.RESULT.COMPUTER.by_name(
                        value, PIH.RESULT.WORKSTATION.CONTAINER_DN, Workstation
                    )
                except NotFound as _:
                    raise NotFound(f"Рабочая станция с именем {value} не найден")

            @staticmethod
            def all() -> Result[list[Workstation]]:
                return PIH.RESULT.COMPUTER.by_container_dn(
                    PIH.RESULT.WORKSTATION.CONTAINER_DN, Workstation
                )

        class INVENTORY:
            @staticmethod
            def report(
                report_file_path: str, open_for_edit: bool = False
            ) -> Result[list[InventoryReportItem]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_inventory_report,
                        (report_file_path, open_for_edit),
                    ),
                    InventoryReportItem,
                )

        class TIME_TRACKING:
            @staticmethod
            def today(
                tab_number_list: list[str] | None = None,
            ) -> Result[list[TimeTrackingResultByPerson]]:
                return PIH.RESULT.TIME_TRACKING.create(tab_number_list=tab_number_list)

            def yesterday(
                tab_number_list: list[str] | None = None,
            ) -> Result[list[TimeTrackingResultByPerson]]:
                yesterday: datetime = DateTimeTool.yesterday()
                return PIH.RESULT.TIME_TRACKING.create(
                    DateTimeTool.begin_date(yesterday),
                    DateTimeTool.begin_date(yesterday),
                    tab_number_list,
                )

            @staticmethod
            def in_period(
                day_start: int = 1,
                day_end: int | None = None,
                month: int | None = None,
                tab_number: list[str] | None = None,
            ) -> Result[list[TimeTrackingResultByPerson]]:
                now: datetime = datetime.now()
                if nn(month):
                    now = now.replace(month=month)
                start_date: datetime = DateTimeTool.begin_date(now)
                end_date: datetime = DateTimeTool.end_date(now)
                if day_start < 0:
                    start_date -= timedelta(days=abs(day_start))
                else:
                    start_date = start_date.replace(day=day_start)
                if nn(day_end):
                    if day_end < 0:
                        day_end -= timedelta(days=abs(day_start))
                    else:
                        day_end = start_date.replace(day=day_start)
                return PIH.RESULT.TIME_TRACKING.create(start_date, end_date, tab_number)

            @staticmethod
            def create(
                start_date: datetime | None = None,
                end_date: datetime | None = None,
                tab_number_list: list[str] | None = None,
            ) -> Result[list[TimeTrackingResultByPerson]]:
                now: datetime | None = DataTool.check(
                    e(start_date) or e(end_date),
                    datetime.now(),
                )
                start_date = DateTimeTool.begin_date(start_date or now)
                end_date = DateTimeTool.end_date(end_date or now)

                def get_date_or_time(entity: TimeTrackingEntity, date: bool) -> str:
                    return DataTool.check_not_none(
                        entity,
                        lambda: entity.TimeVal.split(DATE_TIME.SPLITTER)[not date],
                    )

                result_data: dict = {}
                full_name_by_tab_number_map: dict = {}
                result_data = defaultdict(
                    lambda: defaultdict(lambda: defaultdict(list))
                )
                data: list[TimeTrackingEntity] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_time_tracking,
                        (start_date, end_date, tab_number_list),
                    ),
                    TimeTrackingEntity,
                ).data
                for time_tracking_entity in data:
                    tab_number: str = time_tracking_entity.TabNumber
                    full_name_by_tab_number_map[tab_number] = (
                        time_tracking_entity.FullName
                    )
                    result_data[time_tracking_entity.DivisionName][tab_number][
                        get_date_or_time(time_tracking_entity, True)
                    ].append(time_tracking_entity)
                result: list[TimeTrackingResultByDivision] = []
                has_lunch_break: list[str] = []
                ResultTool.every(
                    lambda user: has_lunch_break.append(user.name),
                    PIH.RESULT.USER.by_property(AD.UserProperies.HasLunchBreak),
                )
                for division_name in result_data:
                    if n(division_name):
                        continue
                    result_division_item: TimeTrackingResultByDivision = (
                        TimeTrackingResultByDivision(division_name)
                    )
                    result.append(result_division_item)
                    for tab_number in result_data[division_name]:
                        full_name: str = full_name_by_tab_number_map[tab_number]
                        result_person_item: TimeTrackingResultByPerson = (
                            TimeTrackingResultByPerson(
                                tab_number, full_name_by_tab_number_map[tab_number]
                            )
                        )
                        result_division_item.list.append(result_person_item)
                        for date in result_data[division_name][tab_number]:
                            time_tracking_entity_list: list[TimeTrackingEntity] = (
                                result_data[division_name][tab_number][date]
                            )
                            time_tracking_enter_entity: TimeTrackingEntity = None
                            time_tracking_exit_entity: TimeTrackingEntity = None
                            for (
                                time_tracking_entity_list_item
                            ) in time_tracking_entity_list:
                                if time_tracking_entity_list_item.Mode == 1:
                                    time_tracking_enter_entity = (
                                        time_tracking_entity_list_item
                                    )
                                if time_tracking_entity_list_item.Mode == 2:
                                    time_tracking_exit_entity = (
                                        time_tracking_entity_list_item
                                    )
                            duration: int = 0
                            if time_tracking_enter_entity is not None:
                                if time_tracking_exit_entity is not None:
                                    enter_time: datetime = datetime.fromisoformat(
                                        time_tracking_enter_entity.TimeVal
                                    ).timestamp()
                                    exit_time: datetime = datetime.fromisoformat(
                                        time_tracking_exit_entity.TimeVal
                                    ).timestamp()
                                    if enter_time < exit_time:
                                        #    enter_time, exit_time = exit_time, enter_time
                                        #    time_tracking_enter_entity, time_tracking_exit_entity = time_tracking_exit_entity, time_tracking_enter_entity
                                        duration = int(exit_time - enter_time) - (
                                            60 * 60
                                            if (full_name in has_lunch_break)
                                            else 0
                                        )
                                    result_person_item.duration += duration
                            result_person_item.list.append(
                                TimeTrackingResultByDate(
                                    date,
                                    get_date_or_time(time_tracking_enter_entity, False),
                                    get_date_or_time(time_tracking_exit_entity, False),
                                    duration,
                                )
                            )
                #
                #
                # print(has_lunch_break)
                for division in result:
                    for person in division.list:
                        index: int = 0
                        length: int = len(person.list)
                        for _ in range(length):
                            item: TimeTrackingResultByDate = person.list[index]
                            if item.duration == 0:
                                # if item.enter_time is None and item.exit_time is not None:
                                if index < length - 1:
                                    item_next: TimeTrackingResultByDate = person.list[
                                        index + 1
                                    ]
                                    if nn(item.exit_time):
                                        if nn(item_next.enter_time):
                                            duration = int(
                                                datetime.fromisoformat(
                                                    item.date
                                                    + DATE_TIME.SPLITTER
                                                    + item.exit_time
                                                ).timestamp()
                                                - datetime.fromisoformat(
                                                    item_next.date
                                                    + DATE_TIME.SPLITTER
                                                    + item_next.enter_time
                                                ).timestamp()
                                            )
                                            # print(full_name, full_name in has_lunch_break)
                                            # duration -= 60*60 if (full_name in has_lunch_break) else 0
                                            item.duration = duration
                                            person.duration += duration
                                            if n(item_next.exit_time):
                                                index += 1
                            index += 1
                            if index >= length - 1:
                                break

                return Result(FIELD_COLLECTION.ORION.TIME_TRACKING_RESULT, result)

        class PRINTER:
            @staticmethod
            def call(printer_name: str, oid: str) -> Result[Any]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.printer_snmp_call, (printer_name, oid)
                    )
                )

            @staticmethod
            def all() -> Result[list[PrinterADInformation]]:
                def filter_by_server_name(
                    printer_list: list[PrinterADInformation],
                ) -> list[PrinterADInformation]:
                    return DataTool.filter(
                        lambda item: item.serverName.find(
                            CONST.HOST.PRINTER_SERVER.NAME
                        )
                        == 0,
                        printer_list,
                    )

                result: Result[list[PrinterADInformation]] = DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_printer_list),
                    PrinterADInformation,
                )
                return Result(result.fields, filter_by_server_name(result.data))

            @staticmethod
            def report() -> Result[list[PrinterReport]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.printers_report),
                    PrinterReport,
                )

        class MARK:
            @staticmethod
            def by_tab_number(value: str) -> Result[Mark]:
                result: Result[Mark] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_mark_by_tab_number, value
                    ),
                    Mark,
                )
                if e(result):
                    raise NotFound(f"Карта доступа с номером '{value}' не найдена")
                return result

            @staticmethod
            def by_division(division_or_id: PersonDivision | int) -> Result[list[Mark]]:
                division_id: int = DataTool.check(
                    isinstance(division_or_id, PersonDivision),
                    lambda: division_or_id.id,
                    division_or_id,
                )
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_mark_list_by_division_id, division_id
                    ),
                    Mark,
                )

            @staticmethod
            def person_divisions() -> Result[list[PersonDivision]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_mark_person_division_list
                    ),
                    PersonDivision,
                )

            @staticmethod
            def by_name(value: str, first_item: bool = False) -> Result[list[Mark]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_mark_by_person_name, value
                    ),
                    Mark,
                    first_item,
                )

            @staticmethod
            def by_full_name(
                value: FullName | str, first_item: bool = False
            ) -> Result[list[Mark]]:
                return PIH.RESULT.MARK.by_name(
                    (
                        FullNameTool.fullname_to_string(value)
                        if isinstance(value, FullName)
                        else value
                    ),
                    first_item,
                )

            @staticmethod
            def temporary_list() -> Result[list[TemporaryMark]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_temporary_mark_list),
                    TemporaryMark,
                )

            @staticmethod
            def by_any(value: str) -> Result[list[Mark]]:
                if PIH.CHECK.MARK.tab_number(value):
                    return ResultTool.as_list(PIH.RESULT.MARK.by_tab_number(value))
                elif PIH.CHECK.name(value, True):
                    return PIH.RESULT.MARK.by_name(value)
                return Result()

            @staticmethod
            def free_list(show_with_guest_marks: bool = False) -> Result[list[Mark]]:
                result: Result[list[Mark]] = DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_free_mark_list), Mark
                )

                def filter_function(item: Mark) -> bool:
                    return EnumTool.get(MarkType, item.type) != MarkType.GUEST

                return (
                    result
                    if show_with_guest_marks
                    else ResultTool.filter(filter_function, result)
                )

            @staticmethod
            def free_marks_by_group_id(value: int) -> Result[list[Mark]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_free_mark_list_by_group_id, value
                    ),
                    Mark,
                )

            @staticmethod
            def free_marks_group_statistics(
                show_guest_marks: bool | None = None,
            ) -> Result[list[MarkGroupStatistics]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_free_mark_group_statistics_list,
                        show_guest_marks,
                    ),
                    MarkGroupStatistics,
                )

            @staticmethod
            def all() -> Result[list[Mark]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_mark_list), Mark
                )

            @staticmethod
            def temporary_mark_owner(mark: Mark) -> Result[Mark]:
                return DataTool.check(
                    mark is not None
                    and EnumTool.get(MarkType, mark.type) == MarkType.TEMPORARY,
                    lambda: DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_owner_mark_for_temporary_mark,
                            mark.TabNumber,
                        ),
                        Mark,
                    ),
                    None,
                )

            @staticmethod
            def temporary_mark_owner_by_tab_number(value: str) -> Result[Mark]:
                return PIH.RESULT.MARK.temporary_mark_owner(
                    PIH.RESULT.MARK.by_tab_number(value).data
                )

        class POLIBASE:
            @staticmethod
            def _person_pin(person_or_pin: PolibasePerson | int) -> int:
                return (
                    person_or_pin.pin
                    if isinstance(person_or_pin, PolibasePerson)
                    else person_or_pin
                )

            @staticmethod
            def bonus_information(
                person_or_person_pin: PolibasePerson | int, test: bool | None = None
            ) -> Result[BonusInformation]:
                result: BonusInformation = BonusInformation()

                class DH:
                    last_item: dict[str, int | float] | None = None

                def action(item: dict[str, int | float]) -> None:
                    item["bonus_plus"] = item["bonus_plus"] or 0
                    item["bonus_minus"] = item["bonus_minus"] or 0
                    item["money"] = item["money"] or 0
                    result.all += item["bonus_plus"]
                    result.spent += item["bonus_minus"]
                    if n(DH.last_item):
                        DH.last_item = item

                ResultTool.every(
                    action,
                    DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_bonus_list,
                            (
                                PIH.RESULT.POLIBASE._person_pin(person_or_person_pin),
                                test,
                            ),
                        )
                    ),
                )
                if nn(DH.last_item):
                    result.last_spent = DH.last_item["bonus_minus"]
                    result.last = (
                        DH.last_item["bonus_plus"] - DH.last_item["bonus_minus"]
                    )
                    result.last_money_spent = DH.last_item["money"]
                    result.active = result.all - result.spent
                return Result(None, result)

            @staticmethod
            def workstations_by_login(
                value: str, test: bool | None = None
            ) -> Result[list[Workstation]] | None:
                if PIH.CHECK.POLIBASE.person_exists_by_login(value):
                    return ResultTool.map(
                        lambda item: PIH.RESULT.WORKSTATION.by_name(item).data,
                        ResultTool.map(
                            lambda item: item[1],
                            ResultTool.filter(
                                lambda item: StringTool.equal(item[0], value),
                                DataTool.to_result(
                                    PIH.SERVICE.call_command(
                                        ServiceCommands.get_polibase_person_user_login_and_worstation_name_pair_list,
                                        test,
                                    )
                                ),
                            ),
                        ),
                    )
                return None

            @staticmethod
            def person_by_login(
                value: str, test: bool | None = None
            ) -> Result[PolibasePerson]:
                result: Result[int | None] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_person_pin_by_login, (value, test)
                    )
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error(
                        "логином", value, "Пользователь"
                    )
                return PIH.RESULT.POLIBASE.person_by_pin(result.data)

            class NOTIFICATION:
                @staticmethod
                def by(
                    value: PolibasePersonVisitNotification,
                ) -> Result[list[PolibasePersonVisitNotification]]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.search_polibase_person_visit_notifications,
                            value,
                        ),
                        PolibasePersonVisitNotification,
                    )

                @staticmethod
                def by_message_id(
                    value: int,
                ) -> Result[PolibasePersonVisitNotification]:
                    return ResultTool.with_first_item(
                        PIH.RESULT.POLIBASE.NOTIFICATION.by(
                            PolibasePersonVisitNotification(messageID=value)
                        )
                    )

                class CONFIRMATION:
                    @staticmethod
                    def by(
                        recipient: str, sender: str
                    ) -> Result[PolibasePersonNotificationConfirmation]:
                        return DataTool.to_result(
                            PIH.SERVICE.call_command(
                                ServiceCommands.search_polibase_person_notification_confirmation,
                                PolibasePersonNotificationConfirmation(
                                    recipient, sender
                                ),
                            ),
                            PolibasePersonNotificationConfirmation,
                        )

            class INFORMATION_QUEST:
                @staticmethod
                def get(
                    search_critery: PolibasePersonInformationQuest,
                ) -> Result[list[PolibasePersonInformationQuest]]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.search_polibase_person_information_quests,
                            search_critery,
                        ),
                        PolibasePersonInformationQuest,
                    )

            class VISIT:
                @staticmethod
                def after_id(
                    value: int, test: bool | None = None
                ) -> Result[list[PolibasePersonVisitDS]]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.search_polibase_person_visits,
                            (
                                PolibasePersonVisitSearchCritery(
                                    vis_no=j((">", value))
                                ),
                                test,
                            ),
                        ),
                        PolibasePersonVisitDS,
                    )

                @staticmethod
                def by_id(
                    value: int, test: bool | None = None
                ) -> Result[PolibasePersonVisitDS]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.search_polibase_person_visits,
                            (PolibasePersonVisitSearchCritery(vis_no=value), test),
                        ),
                        PolibasePersonVisitDS,
                        True,
                    )

                @staticmethod
                def last_id(test: bool | None = None) -> Result[int]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_polibase_person_visits_last_id, test
                        )
                    )

                @staticmethod
                def today(
                    test: bool | None = None,
                ) -> Result[list[PolibasePersonVisitDS]]:
                    return PIH.RESULT.POLIBASE.VISIT.by_registration_date(
                        DateTimeTool.today(as_datetime=True), test
                    )

                @staticmethod
                def prerecording_today(
                    test: bool | None = None,
                ) -> Result[list[PolibasePersonVisitDS]]:
                    return PIH.RESULT.POLIBASE.VISIT.prerecording_by_registration_date(
                        DateTimeTool.today(as_datetime=True), test
                    )

                @staticmethod
                def by_registration_date(
                    value: datetime, test: bool | None = None
                ) -> Result[list[PolibasePersonVisitDS]]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.search_polibase_person_visits,
                            (
                                PolibasePersonVisitSearchCritery(
                                    vis_reg_date=DateTimeTool.date_to_string(
                                        value, POLIBASE.DATE_FORMAT
                                    )
                                ),
                                test,
                            ),
                        ),
                        PolibasePersonVisitDS,
                    )

                @staticmethod
                def prerecording_by_registration_date(
                    value: datetime = None, test: bool | None = None
                ) -> Result[list[PolibasePersonVisitDS]]:
                    def filter_function(value: PolibasePersonVisitDS) -> bool:
                        return value.pin == POLIBASE.PRERECORDING_PIN

                    return ResultTool.filter(
                        filter_function,
                        PIH.RESULT.POLIBASE.VISIT.by_registration_date(value, test),
                    )

                class DATA_STORAGE:
                    @staticmethod
                    def search(
                        value: PolibasePersonVisitDS,
                    ) -> Result[PolibasePersonVisitDS]:
                        return DataTool.to_result(
                            PIH.SERVICE.call_command(
                                ServiceCommands.search_polibase_person_visits_in_data_storage,
                                (value,),
                            ),
                            PolibasePersonVisitDS,
                            True,
                        )

                    @staticmethod
                    def last() -> Result[PolibasePersonVisitDS]:
                        return PIH.RESULT.POLIBASE.VISIT.DATA_STORAGE.search(
                            PolibasePersonVisitDS(id=-1)
                        )

            @staticmethod
            def person_by_telephone_number(
                value: str, test: bool | None = None
            ) -> Result[list[PolibasePerson]]:
                value = PIH.DATA.FORMAT.telephone_number_international(value)
                result: Result[PolibasePerson] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_persons_by_telephone_number,
                        (value, test),
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error(
                        "идентификационным номером", value
                    )
                return result

            @staticmethod
            def person_by_pin(
                value: int, test: bool | None = None
            ) -> Result[PolibasePerson]:
                result: Result[PolibasePerson] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_person_by_pin, (value, test)
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error(
                        "идентификационным номером", value
                    )
                return result

            @staticmethod
            def execute(
                query: str, test: bool | None = None
            ) -> Result[list[dict[str, Any]]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.execute_polibase_query, (query, test)
                    ),
                )

            @staticmethod
            def person_by_email(
                value: str, test: bool | None = None
            ) -> Result[PolibasePerson]:
                result: Result[PolibasePerson] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_person_by_email, (value, test)
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error(
                        "адресом электронной почты", value
                    )
                return result

            @staticmethod
            def persons_pin_by_visit_date(
                date: datetime | date,
                inpatient: bool = False,
                test: bool | None = None,
            ) -> Result[list[int]]:
                if test:
                    return Result(None, [CONST.TEST.PIN])
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_persons_pin_by_visit_date,
                        (
                            date.strftime(CONST.DATE_FORMAT),
                            inpatient,
                            test,
                        ),
                    )
                )

            @staticmethod
            def person_registrator_by_pin(
                value: int, test: bool | None = None
            ) -> Result[PolibasePerson]:
                result: Result[list[PolibasePerson]] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_person_registrator_by_pin,
                        (value, test),
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error(
                        "идентификационным номером", value
                    )
                return result

            @staticmethod
            def person_operator_by_pin(
                value: int, test: bool | None = None
            ) -> Result[PolibasePerson]:
                result: Result[list[PolibasePerson]] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_person_operator_by_pin,
                        (value, test),
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error(
                        "идентификационным номером", value
                    )
                return result

            @staticmethod
            def persons_by_name(
                value: str, test: bool | None = None
            ) -> Result[list[PolibasePerson]]:
                # value = FullNameTool.format(value)
                result: Result[list[PolibasePerson]] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_persons_by_name, (value, test)
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )
                if e(result):
                    raise PIH.ERROR.POLIBASE.create_not_found_error("именем", value)
                return result

            @staticmethod
            def persons_by_pin(
                value: list[int], test: bool | None = None
            ) -> Result[list[PolibasePerson]] | None:
                result: Result[list[PolibasePerson]] | None = None
                if ne(value):
                    result = DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_polibase_persons_by_pin, (value, test)
                        ),
                        PIH.DATA.EXTRACT.polibase_person,
                    )
                    if e(result):
                        raise PIH.ERROR.POLIBASE.create_not_found_error(
                            "идентификационным номером", value
                        )
                return result

            @staticmethod
            def persons_by_card_registry_folder(
                name: str, test: bool | None = None
            ) -> Result[list[PolibasePerson]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_persons_by_card_registry_folder_name,
                        (name, test),
                    ),
                    PIH.DATA.EXTRACT.polibase_person,
                )

            @staticmethod
            def person_pin_list_with_old_format_barcode(
                test: bool | None = None,
            ) -> Result[list[int]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_polibase_person_pin_list_with_old_format_barcode,
                        (test,),
                    )
                )

            @staticmethod
            def persons_by_any(
                value: str | int, test: bool | None = None
            ) -> Result[list[PolibasePerson]]:
                try:
                    if value == POLIBASE.BARCODE.NOT_FOUND:
                        raise BarcodeNotFound()
                    if PIH.CHECK.telephone_number(
                        value
                    ) or PIH.CHECK.telephone_number_international(value):
                        return ResultTool.as_list(
                            PIH.RESULT.POLIBASE.person_by_telephone_number(value, test)
                        )
                    if PIH.CHECK.POLIBASE.person_pin(value):
                        return ResultTool.as_list(
                            PIH.RESULT.POLIBASE.person_by_pin(int(value), test)
                        )
                    if PIH.CHECK.POLIBASE.person_card_registry_folder(value):
                        return PIH.RESULT.POLIBASE.persons_by_card_registry_folder(
                            value, test
                        )
                    if PIH.DATA.CHECK.decimal(value):
                        raise PIH.ERROR.POLIBASE.create_not_found_error(
                            "идентификационным номером", value
                        )
                    return ResultTool.as_list(
                        PIH.RESULT.POLIBASE.persons_by_name(value)
                    )
                except NotFound as _:
                    try:
                        return ResultTool.as_list(
                            PIH.RESULT.POLIBASE.person_by_login(value)
                        )
                    except NotFound as _:
                        raise PIH.ERROR.POLIBASE.create_not_found_error(None, value)

        class USER:
            @staticmethod
            def by_property(value: AD.UserProperies) -> Result[list[User]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_user_list_by_property, (value.name,)
                    ),
                    User,
                )

            @staticmethod
            def by_login(
                value: str, active: bool | None = None, cached: bool | None = None
            ) -> Result[User]:
                try:
                    return ResultTool.with_first_item(
                        PIH.RESULT.USER.by_login_pattern(value, active, cached)
                    )
                except NotFound as _:
                    raise PIH.ERROR.USER.get_not_found_error("логином", active, value)

            @staticmethod
            def by_login_pattern(
                value: str, active: bool | None = None, cached: bool | None = None
            ) -> Result[list[User]]:
                result: Result[list[User]] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_user_by_login, (value, active, cached)
                    ),
                    User,
                )
                if e(result):
                    raise PIH.ERROR.USER.get_not_found_error(
                        "шаблоном логина", active, value
                    )
                return result

            @staticmethod
            def by_telephone_number(
                value: str, active: bool | None = None
            ) -> Result[User]:
                result: Result[User] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_user_by_telephone_number, (value, active)
                    ),
                    User,
                    True,
                )
                if e(result):
                    raise PIH.ERROR.USER.get_not_found_error(
                        "номером телефона", active, value
                    )
                return result

            @staticmethod
            def by_internal_telephone_number(value: int) -> Result[User]:
                workstation_list: list[Workstation] = PIH.RESULT.WORKSTATION.all().data
                result_worksation: Workstation = None
                for workstation in workstation_list:
                    if ne(workstation.description):
                        index: int = workstation.description.find(
                            CONST.INTERNAL_TELEPHONE_NUMBER_PREFIX
                        )
                        if index != -1:
                            internal_telephone_number_text: str = (
                                workstation.description[index:]
                            )
                            internal_telephone_number: int = PIH.DATA.EXTRACT.decimal(
                                internal_telephone_number_text
                            )
                            if internal_telephone_number == value:
                                result_worksation = workstation
                                break
                if (
                    result_worksation is not None
                    and result_worksation.accessable
                    and ne(result_worksation.samAccountName)
                ):
                    return PIH.RESULT.USER.by_login(workstation.samAccountName)
                else:
                    raise PIH.ERROR.USER.get_not_found_error(
                        "внутренним номером телефона", True, str(value)
                    )

            @staticmethod
            def by_polibase_pin(value: int) -> Result[User]:
                return ResultTool.with_first_item(
                    PIH.RESULT.USER.by_name(
                        PIH.RESULT.POLIBASE.person_by_pin(value).data.FullName
                    )
                )

            @staticmethod
            def by_workstation_name(value: str) -> Result[User]:
                value = value.lower()
                user_workstation: Workstation = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_user_by_workstation, value
                    ),
                    Workstation,
                    True,
                ).data
                if e(user_workstation):
                    details: str = f"Компьютер с именем '{value}' не найден!"
                    raise NotFound(details)
                if e(user_workstation.samAccountName):
                    raise NotFound(
                        f"За компьютером {value} нет залогиненного пользователя", value
                    )
                return PIH.RESULT.USER.by_login(user_workstation.samAccountName)

            @staticmethod
            def by_any(value: Any, active: bool | None = None) -> Result[list[User]]:
                def by_number(value: int) -> Result[list[User]]:
                    try:
                        return ResultTool.as_list(PIH.RESULT.USER.by_tab_number(value))
                    except NotFound as _:
                        try:
                            return ResultTool.as_list(
                                PIH.RESULT.USER.by_login(
                                    PIH.RESULT.WORKSTATION.by_internal_telephone_number(
                                        value
                                    ).data.samAccountName
                                )
                            )
                        except:
                            return ResultTool.as_list(
                                PIH.RESULT.USER.by_polibase_pin(value)
                            )

                if isinstance(value, Mark):
                    return PIH.RESULT.USER.by_name(value.FullName)
                elif isinstance(value, FullName):
                    return PIH.RESULT.USER.by_full_name(value, False, active)
                elif isinstance(value, (ComputerDescription, Workstation)):
                    return PIH.RESULT.USER.by_any(value.name, active)
                elif isinstance(value, str):

                    class DH:
                        result: Result[list[User]] | None = None

                    def init_or_add(
                        value_getter: Callable[[None], Result[list[User]]]
                    ) -> None:
                        try:
                            value: Result[list[User]] = value_getter()
                            if nn(value):
                                if n(DH.result):
                                    DH.result = value
                                else:
                                    DH.result += value
                        except NotFound as _:
                            pass

                    try:
                        value_as_telephone_number: str = (
                            PIH.DATA.FORMAT.telephone_number(value)
                        )
                        if PIH.CHECK.telephone_number(value_as_telephone_number):
                            init_or_add(
                                lambda: ResultTool.as_list(
                                    PIH.RESULT.USER.by_telephone_number(
                                        value_as_telephone_number, active
                                    )
                                )
                            )
                    except Exception as _:
                        pass
                    if PIH.DATA.CHECK.decimal(value):
                        init_or_add(lambda: by_number(int(value)))
                    if PIH.CHECK.WORKSTATION.name(value):
                        init_or_add(
                            lambda: ResultTool.as_list(
                                PIH.RESULT.USER.by_workstation_name(value)
                            )
                        )
                    if PIH.CHECK.login(value):
                        init_or_add(
                            lambda: ResultTool.as_list(
                                PIH.RESULT.USER.by_login(value, active)
                            )
                        )
                    init_or_add(lambda: PIH.RESULT.USER.by_login_pattern(value, active))
                    init_or_add(lambda: PIH.RESULT.USER.by_name(value, active))
                    if ne(DH.result):
                        return DH.result
                elif isinstance(value, int):
                    return by_number(value)
                raise PIH.ERROR.USER.get_not_found_error(
                    "поисковым значением", active, value
                )

            @staticmethod
            def by_job_position(value: AD.JobPositions) -> Result[list[User]]:
                UCH = PIH.CHECK.USER
                return ResultTool.filter(
                    lambda user: not UCH.template(user) and UCH.active(user),
                    DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_user_list_by_job_position, value.name
                        ),
                        User,
                    ),
                )

            @staticmethod
            def by_group(value: AD.Groups) -> Result[list[User]]:
                return PIH.RESULT.USER.by_group_name(value.name)

            @staticmethod
            def by_group_name(value: str) -> Result[list[User]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_user_list_by_group, value
                    ),
                    User,
                )

            @staticmethod
            def template_list() -> Result[list[User]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_template_users), User
                )

            @staticmethod
            def containers() -> Result[list[UserBase]]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(ServiceCommands.get_containers), UserBase
                )

            @staticmethod
            def by_full_name(
                value: FullName, get_first: bool = False, active: bool | None = None
            ) -> Result[list[User] | User]:
                return DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_user_by_full_name, (value, active)
                    ),
                    User,
                    get_first,
                )

            @staticmethod
            def by_name(
                value: str, active: bool | None = None, cached: bool | None = None
            ) -> Result[list[User]]:
                result: Result[list[User]] = DataTool.to_result(
                    PIH.SERVICE.call_command(
                        ServiceCommands.get_users_by_name, (value, active, cached)
                    ),
                    User,
                )
                if e(result):
                    raise PIH.ERROR.USER.get_not_found_error("именем", active, value)
                return result

            @staticmethod
            def all(active: bool | None = None) -> Result[list[User]]:
                return PIH.RESULT.USER.by_name(AD.SEARCH_ALL_PATTERN, active)

            @staticmethod
            def list_with_telephone_number(
                active: bool | None = None,
            ) -> Result[list[User]]:
                def user_with_telephone_number(user: User) -> bool:
                    return PIH.CHECK.telephone_number(user.telephoneNumber)

                return ResultTool.filter(
                    lambda user: user_with_telephone_number(user),
                    PIH.RESULT.USER.all(active),
                )

            @staticmethod
            def by_tab_number(value: str) -> Result[User]:
                result: Result[Mark] = PIH.RESULT.MARK.by_tab_number(value)
                if e(result):
                    details: str = f"Карта доступа с номером {value} не найдена"
                    raise NotFound(details)
                return PIH.RESULT.USER.by_mark(result.data)

            @staticmethod
            def by_mark(value: Mark) -> Result[User]:
                return Result(
                    FIELD_COLLECTION.AD.USER,
                    DataTool.check(
                        value,
                        lambda: DataTool.get_first_item(
                            PIH.RESULT.USER.by_full_name(
                                FullNameTool.fullname_from_string(value.FullName)
                            ).data
                        ),
                    ),
                )

    class CHECK:
        class EVENTS:
            @staticmethod
            def has(value: Events | None, parameters: tuple[Any] | None = None) -> bool:
                return ne(PIH.RESULT.EVENTS.get(value, parameters))

            @staticmethod
            def has_by_key(
                value: Events | None, parameters: tuple[Any] | None = None
            ) -> bool | None:
                return PIH.CHECK.EVENTS.has(
                    *PIH.EVENT.BUILDER.by_key(value, parameters)
                )

            @staticmethod
            def timeouted(
                event: Events,
                parameters: dict | None = None,
                timeout_in_seconds: int | None = None,
            ) -> bool:
                event_ds: EventDS | None = PIH.RESULT.get_first_item(
                    PIH.RESULT.sort(
                        PIH.RESULT.EVENTS.get(event, parameters),
                        lambda item: item.timestamp,
                        reserve=True,
                    )
                )
                return (
                    n(event_ds)
                    or (DateTimeTool.now() - event_ds.timestamp).total_seconds()
                    > timeout_in_seconds
                )

            @staticmethod
            def compare_by_timestamp(event_type: Events, event_type2: Events) -> bool:
                get_event_timestamp: Callable[[Events], datetime] = (
                    lambda event: ResultTool.get_first_item(
                        PIH.RESULT.EVENTS.get_last(event)
                    ).timestamp
                )
                return get_event_timestamp(event_type) > get_event_timestamp(
                    event_type2
                )

        class SETTINGS:
            @staticmethod
            def by_time(current: datetime, settings: SETTINGS) -> bool:
                return DateTimeTool.is_equal_by_time(
                    current, PIH.SETTINGS.to_datetime(settings)
                )

        class INDICATION:
            class DEVICE:
                @staticmethod
                def accessibility(name: str) -> bool | None:
                    device: IndicationDevice | None = PIH.RESULT.INDICATIONS.DEVICE.get(
                        name
                    ).data
                    if n(device):
                        return None
                    return PIH.CHECK.RESOURCE.accessibility_by_ping(device.ip_address)

            @staticmethod
            def ct_notification_start_time(current: datetime) -> bool:
                start_time_list: list[datetime] = (
                    PIH.SETTINGS.INDICATION.ct_notification_start_time()
                )
                for start_time in start_time_list:
                    if DateTimeTool.is_equal_by_time(current, start_time):
                        return True
                return False

            @staticmethod
            def chiller_on() -> bool:
                return PIH.CHECK.EVENTS.compare_by_timestamp(
                    PIH.EVENT.BUILDER.chiller_was_turned_on(),
                    PIH.EVENT.BUILDER.chiller_was_turned_off(),
                )

            @staticmethod
            def chiller_temperature_good() -> bool:
                return PIH.CHECK.EVENTS.compare_by_timestamp(
                    PIH.EVENT.BUILDER.chiller_temperature_alert_was_resolved(),
                    PIH.EVENT.BUILDER.chiller_temperature_alert_was_fired(),
                )

        class RECOGNIZE:
            @staticmethod
            def document_type_exists(
                file_path: str, value: DocumentTypes, log_level: int | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.document_type_exists,
                        (file_path, EnumTool.get(value), log_level),
                    )
                )

            @staticmethod
            def polibase_document(file_path: str, log_level: int | None = 0) -> bool:
                return PIH.CHECK.RECOGNIZE.document_type_exists(
                    file_path, DocumentTypes.POLIBASE, log_level
                )

            @staticmethod
            def medical_direction(file_path: str, log_level: int | None = 0) -> bool:
                return PIH.CHECK.RECOGNIZE.document_type_exists(
                    file_path, DocumentTypes.MEDICAL_DIRECTION, log_level
                )

        class NOTES:
            @staticmethod
            def exists(
                name: str | None, title: str | None = None, full_equaliment: bool = True
            ) -> bool:
                return ne(
                    PIH.RESULT.NOTES.find_gkeep_item(name, title, full_equaliment)
                )

        class JOURNALS:
            @staticmethod
            def exists(name: str | None, caption: str | None = None) -> bool:
                return nn(
                    PIH.DATA.JOURNAL.type_by_any(name)
                    or PIH.DATA.JOURNAL.type_by_any(caption)
                )

        class RESOURCE:
            @staticmethod
            def accessibility_by_ping_with_port(
                address_or_ip: str,
                port: int,
                host: str | None = None,
                count: int | None = None,
                check_all: bool = True,
            ) -> bool:
                return PIH.CHECK.RESOURCE.accessibility_by_ping(
                    j((address_or_ip, port), ":"), host, count, check_all
                )

            @staticmethod
            def accessibility_by_smb_port(
                address_or_ip: str,
                host: str | None = None,
                count: int | None = None,
                check_all: bool = True,
            ) -> bool:
                return PIH.CHECK.RESOURCE.accessibility_by_ping_with_port(
                    address_or_ip, WINDOWS.PORT.SMB, host, count, check_all
                )

            @staticmethod
            def accessibility_by_ping(
                address_or_ip: str,
                host: str | None = None,
                count: int | None = None,
                check_all: bool = True,
            ) -> bool:
                return PIH.EXECUTOR.psping(address_or_ip, host, count, check_all)

            @staticmethod
            def accessibility(resource_status_or_address: Any) -> bool | None:
                resource_status: ResourceStatus | None = None
                if isinstance(resource_status_or_address, ResourceDescription):
                    resource_status = resource_status_or_address
                else:
                    resource_status = PIH.RESULT.RESOURCES.get_resource_status(
                        resource_status_or_address
                    )
                return (
                    None
                    if n(resource_status)
                    else resource_status.inaccessibility_counter
                    < resource_status.inaccessibility_check_values[0]
                )

            @staticmethod
            def vpn_pacs_accessibility(count: int = 2) -> bool:
                return PIH.EXECUTOR.ping(
                    RESOURCES.DESCRIPTIONS.VPN_PACS_SPB.address,
                    RESOURCES.DESCRIPTIONS.VPN_PACS_SPB.delegator,
                    count,
                )

            @staticmethod
            def pacs_accessibility(count: int = 2) -> bool:
                return PIH.CHECK.RESOURCE.accessibility_by_ping(
                    RESOURCES.DESCRIPTIONS.PACS_SPB.address,
                    RESOURCES.DESCRIPTIONS.PACS_SPB.delegator,
                    count,
                )

            @staticmethod
            def wappi_profile_accessibility(
                value: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | str, cached: bool = False
            ) -> bool:
                return (
                    PIH.CHECK.RESOURCE.accessibility(
                        PIH.RESULT.RESOURCES.get_resource_status(
                            EnumTool.get_value(
                                value,
                                EnumTool.get(
                                    CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT
                                ),
                            )
                        )
                    )
                    if cached
                    else PIH.CHECK.MESSAGE.WHATSAPP.WAPPI.accessibility(value, False)
                )

            @staticmethod
            def ws_accessibility(name: str) -> bool:
                result: Result[Workstation] = PIH.RESULT.WORKSTATION.by_name(name)
                return ne(result) and result.data.accessable

            @staticmethod
            def polibase_accessibility(
                cached: bool = False, test: bool | None = None
            ) -> bool:
                try:
                    if cached:
                        return PIH.RESULT.RESOURCES.get_resource_status(
                            RESOURCES.DESCRIPTIONS.POLIBASE2
                            if test
                            else RESOURCES.DESCRIPTIONS.POLIBASE1
                        ).accessable
                    result_by_ping: bool = PIH.SERVICE.check_on_accessibility(
                        ServiceRoles.POLIBASE
                    )
                    if result_by_ping:
                        return PIH.CHECK.POLIBASE.person_exists_by_pin(
                            POLIBASE.PRERECORDING_PIN, test
                        )
                    return False
                except NotFound as _:
                    pass
                return False

        class EMAIL:
            @staticmethod
            def accessability(value: str) -> bool:
                def internal_accessability(
                    value: str, verification_method: EmailVerificationMethods.DEFAULT
                ) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.check_email_accessibility,
                            (value, verification_method),
                        )
                    )

                if not internal_accessability(value, EmailVerificationMethods.DEFAULT):
                    return internal_accessability(
                        value, EmailVerificationMethods.ABSTRACT_API
                    )
                return True

        class FILE:
            @staticmethod
            def excel_file(path: str) -> bool:
                return os.path.isfile(path) and PathTool.get_extension(path) in [
                    FILE.EXTENSION.EXCEL_OLD,
                    FILE.EXTENSION.EXCEL_NEW,
                ]

        class ACCESS:
            @staticmethod
            def by_group(
                group: AD.Groups,
                exit_on_access_denied: bool = False,
                session: SessionBase = None,
                notify_on_fail: bool = True,
                notify_on_success: bool = True,
            ) -> bool:
                session = session or PIH.session
                user: User = session.get_user()
                result: bool = False
                notify: bool = notify_on_success or notify_on_fail
                if group in session.allowed_groups:
                    result = True
                    notify = False
                else:
                    result = PIH.CHECK.USER.by_group(user, group)
                    if result:
                        session.add_allowed_group(group)
                if notify:
                    PIH.LOG.it_bot(
                        f"Запрос на доступа к группе: {group.name} от пользователя {user.name} ({user.samAccountName}). Доступ {'разрешен' if result else 'отклонен'}.",
                        LogMessageFlags.NORMAL if result else LogMessageFlags.ERROR,
                    )
                if not result and exit_on_access_denied:
                    session.exit(5, "Функционал недоступен...")
                return result

            @staticmethod
            def admin(
                exit_on_access_denied: bool = False,
                session: SessionBase = None,
                notify_on_fail: bool = True,
                notify_on_success: bool = True,
            ) -> bool:
                return PIH.CHECK.ACCESS.by_group(
                    AD.Groups.Admin,
                    exit_on_access_denied,
                    session,
                    notify_on_fail,
                    notify_on_success,
                )

            @staticmethod
            def service_admin(
                session: SessionBase = None,
                notify_on_fail: bool = True,
                notify_on_success: bool = True,
            ) -> bool:
                return PIH.CHECK.ACCESS.by_group(
                    AD.Groups.ServiceAdmin,
                    False,
                    session,
                    notify_on_fail,
                    notify_on_success,
                )

            @staticmethod
            def inventory(
                session: SessionBase = None,
                notify_on_fail: bool = True,
                notify_on_success: bool = True,
            ) -> bool:
                return PIH.CHECK.ACCESS.by_group(
                    AD.Groups.Inventory,
                    False,
                    session,
                    notify_on_fail,
                    notify_on_success,
                )

            @staticmethod
            def polibase(
                session: SessionBase = None,
                notify_on_fail: bool = True,
                notify_on_success: bool = True,
            ) -> bool:
                return PIH.CHECK.ACCESS.by_group(
                    AD.Groups.Polibase,
                    False,
                    session,
                    notify_on_fail,
                    notify_on_success,
                )

            @staticmethod
            def card_registry(
                session: SessionBase = None,
                notify_on_fail: bool = True,
                notify_on_success: bool = True,
            ) -> bool:
                return PIH.CHECK.ACCESS.by_group(
                    AD.Groups.CardRegistry,
                    False,
                    session,
                    notify_on_fail,
                    notify_on_success,
                )

        class USER:
            @staticmethod
            def doctor(user: User) -> bool:
                distinguishedName: str = user.distinguishedName
                return not (
                    distinguishedName.find("Доктор") == -1
                    and distinguishedName.find("Оператор") == -1
                )

            @staticmethod
            def by_group(user: User, value: AD.Groups) -> bool:
                return ne(
                    ResultTool.filter(
                        lambda check_user: check_user.samAccountName
                        == user.samAccountName,
                        PIH.RESULT.USER.by_group(value),
                    )
                )

            @staticmethod
            def has_property(user: User, value: AD.UserProperies) -> bool:
                return ne(
                    ResultTool.filter(
                        lambda check_user: check_user.samAccountName
                        == user.samAccountName,
                        PIH.RESULT.USER.by_property(value),
                    )
                )

            @staticmethod
            def exists_by_login(value: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.check_user_exists_by_login, value
                    )
                )

            @staticmethod
            def user(value: User) -> bool:
                return PIH.CHECK.full_name(value.name)

            @staticmethod
            def active(value: User) -> bool:
                return value.distinguishedName.find(AD.ACTIVE_USERS_CONTAINER_DN) != -1

            @staticmethod
            def template(value: User) -> bool:
                name: str = value.samAccountName
                return name[0] == "_" and name[-1] == "_"

            @staticmethod
            def exists_by_full_name(value: FullName) -> bool:
                return ne(PIH.RESULT.USER.by_full_name(value))

            @staticmethod
            def search_attribute(value: str) -> bool:
                return value in AD.SEARCH_ATTRIBUTES

            @staticmethod
            def property(
                value: str | None, default_value: str = USER_PROPERTIES.PASSWORD
            ) -> str:
                return value or default_value

            @staticmethod
            def accessibility() -> bool:
                return PIH.SERVICE.check_on_accessibility(ServiceRoles.AD)

        class MESSAGE:
            class WHATSAPP:
                class WAPPI:
                    @staticmethod
                    def from_me(value: str) -> bool:
                        value = PIH.DATA.FORMAT.telephone_number(value)
                        return value in [
                            PIH.DATA.TELEPHONE_NUMBER.it_administrator(),
                            PIH.DATA.TELEPHONE_NUMBER.call_centre_administrator(),
                            PIH.DATA.TELEPHONE_NUMBER.marketer_administrator(),
                        ]

                    @staticmethod
                    def accessibility(
                        profile: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | str | None,
                        cached: bool = True,
                    ) -> bool:
                        def internal_accessibility(
                            profile: (
                                CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | str | None
                            ) = None,
                        ) -> bool:
                            profile = EnumTool.get_by_value(
                                CONST.MESSAGE.WHATSAPP.WAPPI.Profiles,
                                profile
                                or CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT,
                            )
                            profile_value: str = EnumTool.get_value(
                                profile,
                                EnumTool.get(profile),
                            )
                            url: str = (
                                f"{CONST.MESSAGE.WHATSAPP.WAPPI.URL_GET_STATUS}{profile_value}"
                            )
                            headers: dict = {
                                "Authorization": CONST.MESSAGE.WHATSAPP.WAPPI.AUTHORIZATION[
                                    profile
                                ],
                                "Content-Type": "application/json",
                            }
                            response_result: dict = None
                            try:
                                response: Response = requests.get(url, headers=headers)
                                response_result = json.loads(response.text)
                            except Exception:
                                return False
                            if "status" in response_result:
                                if response_result["status"] == "error":
                                    return False
                            return response_result["app_status"] == "open"

                        return (
                            PIH.CHECK.RESOURCE.wappi_profile_accessibility(
                                profile, True
                            )
                            if cached
                            else internal_accessibility(profile)
                        )

        class MARK:
            @staticmethod
            def free(tab_number: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.check_mark_free, tab_number
                    )
                )

            @staticmethod
            def exists_by_full_name(full_name: FullName) -> bool:
                result: Result[list[Mark]] = PIH.RESULT.MARK.by_name(
                    FullNameTool.fullname_to_string(full_name)
                )
                return e(result)

            @staticmethod
            def accessibility() -> bool:
                return PIH.SERVICE.check_on_accessibility(ServiceRoles.MARK)

            @staticmethod
            def tab_number(value: str) -> bool:
                return value.isdecimal()

        class TIME_TRACKING:
            @staticmethod
            def accessibility() -> bool:
                return PIH.CHECK.ACCESS.by_group(AD.Groups.TimeTrackingReport)

        class INVENTORY:
            @staticmethod
            def is_report_file(file_path: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.check_inventory_report, file_path
                    )
                )

            @staticmethod
            def accessibility() -> bool:
                return (
                    PIH.SERVICE.check_on_accessibility(ServiceRoles.DOCS)
                    and PIH.CHECK.ACCESS.inventory()
                )

        class POLIBASE:
            @staticmethod
            def accessibility() -> bool:
                return (
                    PIH.SERVICE.check_on_accessibility(ServiceRoles.POLIBASE)
                    and PIH.CHECK.ACCESS.polibase()
                )

            @staticmethod
            def person_card_registry_folder(value: str) -> bool:
                return (
                    value in CONST.CARD_REGISTRY.SUITABLE_FOLDER_NAME_SYMBOL
                ) or DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.check_polibase_person_card_registry_folder_name,
                        value,
                    )
                )

            @staticmethod
            def person_exists_by_pin(value: int, test: bool | None = None) -> bool:
                try:
                    return ne(PIH.RESULT.POLIBASE.person_by_pin(value, test))
                except NotFound as _:
                    return False

            @staticmethod
            def visit_exists_by_id(value: int) -> bool:
                pass

            @staticmethod
            def person_exists_by_login(value: str) -> bool:
                try:
                    return ne(PIH.RESULT.POLIBASE.person_by_login(value))
                except NotFound as _:
                    return False

            @staticmethod
            def person_pin(value: str | int) -> bool:
                is_numeric: bool = (
                    value.isnumeric()
                    if isinstance(value, str)
                    else True if isinstance(value, int) else False
                )
                return is_numeric and int(value) > POLIBASE.PERSON_MINIMAL_PIN

            class NOTIFICATION:
                @staticmethod
                def exists(value: PolibasePersonVisitNotification) -> bool:
                    return ne(PIH.RESULT.POLIBASE.NOTIFICATION.by(value))

                class CONFIRMATION:
                    @staticmethod
                    def exists(recipient: str, sender: str, state: int = None) -> bool:
                        result: Result[PolibasePersonNotificationConfirmation] = (
                            PIH.RESULT.POLIBASE.NOTIFICATION.CONFIRMATION.by(
                                recipient, sender
                            )
                        )
                        return ne(result) and (
                            True if state is None else result.data.status == state
                        )

            class DATABASE:
                def creation_start_time(value: datetime) -> bool:
                    return DateTimeTool.is_equal_by_time(
                        value,
                        PIH.SETTINGS.to_datetime(
                            SETTINGS.POLIBASE_CREATION_DB_DUMP_START_TIME
                        ),
                    )

        @staticmethod
        def login(value: str) -> bool:
            pattern: str = (
                r"^[a-z]+[a-z_0-9]{"
                + str(CONST.NAME_POLICY.PART_ITEM_MIN_LENGTH - 1)
                + ",}"
            )
            return re.fullmatch(pattern, value, re.IGNORECASE) is not None

        class COMPUTER:
            @staticmethod
            def windows_service_running(
                name: str, host: str, host_check_for_accessibility: bool = True
            ) -> bool | None:
                accessable: bool | None = None
                if host_check_for_accessibility:
                    accessable = PIH.CHECK.COMPUTER.accessibility(host)
                    if n(accessable):
                        return None
                return PIH.EXECUTOR.check_for_windows_service_running(name, host)

            @staticmethod
            def accessibility(name: str) -> bool | None:
                try:
                    return PIH.RESULT.COMPUTER.by_name(name).data.accessable
                except NotFound as _:
                    return None

        class WORKSTATION:
            @staticmethod
            def accessibility(name: str) -> bool | None:
                try:
                    return PIH.RESULT.WORKSTATION.by_name(name).data.accessable
                except NotFound as _:
                    return None

            @staticmethod
            def name(value: str) -> bool:
                value = PIH.DATA.FORMAT.string(value)
                for prefix in AD.WORKSTATION_PREFIX_LIST:
                    if value.startswith(prefix):
                        return True
                return False

            @staticmethod
            def exists(name: str) -> bool:
                name = name.lower()
                return ne(
                    ResultTool.filter(
                        lambda workstation: name == workstation.name.lower(),
                        PIH.RESULT.WORKSTATION.all_description(),
                    )
                )

            @staticmethod
            def has_property(
                workstation: ComputerDescription, property: AD.WSProperies
            ) -> bool:
                return BM.has(workstation.properties, property)

            @staticmethod
            def watchable(workstation: ComputerDescription) -> bool:
                return PIH.CHECK.WORKSTATION.has_property(
                    workstation, AD.WSProperies.Watchable
                )

            @staticmethod
            def shutdownable(workstation: ComputerDescription) -> bool:
                return PIH.CHECK.WORKSTATION.has_property(
                    workstation, AD.WSProperies.Shutdownable
                )

            @staticmethod
            def rebootable(workstation: ComputerDescription) -> bool:
                return PIH.CHECK.WORKSTATION.has_property(
                    workstation, AD.WSProperies.Rebootable
                )

        @staticmethod
        def telephone_number(value: str | int, international: bool = False) -> bool:
            return (
                ne(value)
                and re.fullmatch(
                    ("" if international else r"^\+") + "[0-9]{11,13}$", str(value)
                )
                is not None
            )

        @staticmethod
        def telephone_number_international(value: str) -> bool:
            return PIH.CHECK.telephone_number(value, True)

        @staticmethod
        def email(value: str, check_accesability: bool = False) -> bool:
            return ne(
                re.fullmatch(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", value
                )
            ) and (not check_accesability or PIH.CHECK.EMAIL.accessability(value))

        @staticmethod
        def name(value: str, use_space: bool = False) -> bool:
            pattern = (
                r"[а-яА-ЯёЁ"
                + (" " if use_space else "")
                + "]{"
                + str(CONST.NAME_POLICY.PART_ITEM_MIN_LENGTH)
                + ",}$"
            )
            return re.fullmatch(pattern, value) is not None

        @staticmethod
        def full_name(value: str) -> bool:
            pattern = (
                r"[а-яА-ЯёЁ]{"
                + str(CONST.NAME_POLICY.PART_ITEM_MIN_LENGTH)
                + ",} [а-яА-ЯёЁ]{"
                + str(CONST.NAME_POLICY.PART_ITEM_MIN_LENGTH)
                + ",} [а-яА-ЯёЁ]{"
                + str(CONST.NAME_POLICY.PART_ITEM_MIN_LENGTH)
                + ",}$"
            )
            return re.fullmatch(pattern, value) is not None

        @staticmethod
        def password(value: str, settings: PasswordSettings | None = None) -> bool:
            settings = settings or PASSWORD.SETTINGS.DEFAULT
            return PasswordTools.check_password(
                value, settings.length, settings.special_characters
            )

    class LOG:
        executor = ThreadPoolExecutor(max_workers=1)

        @staticmethod
        def send(
            value: str,
            channel: LogMessageChannels = LogMessageChannels.DEFAULT,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
            image_path: str | None = None,
        ) -> str:
            level = level or LogMessageFlags.DEFAULT

            def internal_send_message(
                message: str,
                channel_name: str,
                level_value: int,
                image_path: str | None = None,
            ) -> None:
                with PIH.ERROR.detect():
                    try:
                        PIH.SERVICE.call_command(
                            ServiceCommands.send_log_message,
                            (message, channel_name, level_value, image_path),
                            blocked=False,
                        )
                    except Error as error:
                        PIH.output.error("Log send error")

            PIH.LOG.executor.submit(
                PIH.ERROR.wrap(internal_send_message),
                value,
                channel.name,
                DataTool.as_bitmask_value(level),
                image_path,
            )
            return value

        @staticmethod
        def debug_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.DEBUG_BOT, level)

        @staticmethod
        def debug(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.DEBUG, level)

        @staticmethod
        def journal(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.JOURNAL, level)

        @staticmethod
        def journal_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.JOURNAL_BOT, level)

        @staticmethod
        def new_email_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.NEW_EMAIL_BOT, level)

        @staticmethod
        def new_email(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.NEW_EMAIL, level)

        @staticmethod
        def services(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.SERVICES, level)

        @staticmethod
        def time_tracking(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.TIME_TRACKING, level)

        @staticmethod
        def resources(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.RESOURCES, level)

        @staticmethod
        def printers(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.PRINTER, level)

        @staticmethod
        def services_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.SERVICES_BOT, level)

        @staticmethod
        def backup(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.BACKUP, level)

        @staticmethod
        def polibase_document(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
            image_path: str | None = None,
        ) -> str:
            return PIH.LOG.send(
                message, LogMessageChannels.POLIBASE_DOCUMENT, level, image_path
            )

        @staticmethod
        def polibase_document_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(
                message, LogMessageChannels.POLIBASE_DOCUMENT_BOT, level
            )

        @staticmethod
        def polibase(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.POLIBASE, level)

        @staticmethod
        def polibase_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.POLIBASE_BOT, level)

        @staticmethod
        def card_registry(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.CARD_REGISTRY, level)

        @staticmethod
        def card_registry_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.CARD_REGISTRY_BOT, level)

        @staticmethod
        def polibase_error(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.POLIBASE_ERROR, level)

        @staticmethod
        def polibase_error_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.POLIBASE_ERROR_BOT, level)

        @staticmethod
        def it(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.IT, level)

        @staticmethod
        def it_bot(
            message: str,
            level: int | tuple[Enum] | Enum | list[Enum] | list[int] | None = None,
        ) -> str:
            return PIH.LOG.send(message, LogMessageChannels.IT_BOT, level)

    class MESSAGE:
        class POLIBASE:
            @staticmethod
            def notify(message: str, test: bool = True) -> None:
                PIH.MESSAGE.WORKSTATION.to_all_workstations(
                    message,
                    AD.Groups.PolibaseUsers,
                    [CONST.HOST.WS255.NAME],
                    None,
                    test,
                    180,
                )

            @staticmethod
            def notify_about_polibase_closing(
                message: str | None = None, test: bool = True
            ) -> None:
                PIH.MESSAGE.POLIBASE.notify(
                    message
                    or PIH.SETTINGS.get(
                        SETTINGS.POLIBASE_WAS_EMERGENCY_CLOSED_NOTIFICATION_TEXT
                    ),
                    test,
                )

            @staticmethod
            def notify_about_polibase_restarted(test: bool = True) -> None:
                PIH.MESSAGE.POLIBASE.notify(
                    PIH.SETTINGS.get(SETTINGS.POLIBASE_WAS_RESTARTED_NOTIFICATION_TEXT),
                    test,
                )

        class WORKSTATION:
            executor = ThreadPoolExecutor(max_workers=10)

            @staticmethod
            def to_all_workstations(
                message: str,
                filter_group: AD.Groups | None = None,
                to_all_user_workstation_name_list: list[str] | None = None,
                session: Session | None = None,
                test: bool = True,
                timeout: int = 60,
            ) -> None:
                session = session or PIH.session
                filter_user_login_list: list[str] = (
                    None
                    if filter_group is None
                    else ResultTool.map(
                        lambda item: item.samAccountName.lower(),
                        PIH.RESULT.USER.by_group(filter_group),
                    ).data
                )
                filter_user_login_list_is_empty: bool = e(filter_user_login_list)
                to_all_user_workstation_name_list_is_empty: bool = e(
                    to_all_user_workstation_name_list
                )

                def filter_function(workstation: Workstation) -> bool:
                    workstation_name: str = workstation.name.lower()
                    if test:
                        return workstation_name == CONST.TEST.WORKSTATION_MAME
                    return workstation.accessable and (
                        (
                            filter_user_login_list_is_empty
                            or workstation.samAccountName in filter_user_login_list
                        )
                        or (
                            to_all_user_workstation_name_list_is_empty
                            or workstation_name in to_all_user_workstation_name_list
                        )
                    )

                def every_action(workstation: Workstation) -> None:
                    def internal_send_message(
                        user_login: str | None, workstation_name: str, message: str
                    ) -> None:
                        if (
                            ne(to_all_user_workstation_name_list)
                            and workstation_name in to_all_user_workstation_name_list
                        ):
                            if not test:
                                PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                                    None, workstation_name, message, timeout
                                )
                        else:
                            if e(user_login):
                                if test:
                                    PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                                        user_login, workstation_name, message, timeout
                                    )
                                else:
                                    pass
                                # dont send message - cause workstation is on but no one user is logged
                            else:
                                if test:
                                    if workstation_name == CONST.TEST.WORKSTATION_MAME:
                                        PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                                            user_login,
                                            workstation_name,
                                            message,
                                            timeout,
                                        )
                                else:
                                    PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                                        user_login, workstation_name, message, timeout
                                    )

                    result_message: str = (
                        f"Сообщение от {session.user_given_name} ({PIH.DATA.FORMAT.description(session.get_user().description)}):"
                    )
                    result_message += f" День добрый, "
                    user: User | None = (
                        None
                        if e(workstation.samAccountName)
                        else PIH.RESULT.USER.by_login(
                            workstation.samAccountName, True, True
                        ).data
                    )
                    result_message += DataTool.if_not_empty(
                        user, lambda user: f"{FullNameTool.to_given_name(user)}, ", ""
                    )
                    result_message += message
                    PIH.MESSAGE.WORKSTATION.executor.submit(
                        PIH.ERROR.wrap(internal_send_message),
                        workstation.samAccountName,
                        workstation.name.lower(),
                        result_message,
                    )

                ResultTool.every(
                    every_action,
                    ResultTool.filter(filter_function, PIH.RESULT.WORKSTATION.all()),
                )

            @staticmethod
            def to_user(
                value: User | str,
                message: str,
                timeout: int = 60,
                method_type: WorkstationMessageMethodTypes = WorkstationMessageMethodTypes.REMOTE,
            ) -> bool:
                return PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                    value.samAccountName if isinstance(value, User) else value,
                    None,
                    message,
                    timeout,
                    method_type,
                )

            @staticmethod
            def to_workstation(
                value: ComputerDescription | str,
                message: str,
                timeout: int = 60,
                method_type: WorkstationMessageMethodTypes = WorkstationMessageMethodTypes.REMOTE,
            ) -> bool:
                return PIH.MESSAGE.WORKSTATION.by_workstation_name(
                    value.name if isinstance(value, ComputerDescription) else value,
                    message,
                    timeout,
                    method_type,
                )

            @staticmethod
            def by_workstation_name(
                value: str,
                message: str,
                timeout: int = 60,
                method_type: WorkstationMessageMethodTypes = WorkstationMessageMethodTypes.REMOTE,
            ) -> bool:
                user: User | None = None
                try:
                    user = PIH.RESULT.USER.by_workstation_name(value).data
                except NotFound as _:
                    pass
                return PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                    None if n(user) else user.samAccountName,
                    value,
                    message,
                    timeout,
                    method_type,
                )

            @staticmethod
            def to_user_or_workstation(
                user_login: str,
                workstation_name: str,
                message: str,
                timeout: int = 60,
                method_type: WorkstationMessageMethodTypes = WorkstationMessageMethodTypes.REMOTE,
            ) -> bool:
                if method_type == WorkstationMessageMethodTypes.REMOTE:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.send_message_to_user_or_workstation,
                            (user_login, workstation_name, message, timeout),
                        )
                    )

                def internal_send_by_login_and_workstation_name(
                    login: str, workstation_name: str
                ) -> None:
                    if method_type == WorkstationMessageMethodTypes.LOCAL_PSTOOL_MSG:
                        PIH.EXECUTOR.execute(
                            PIH.EXECUTOR.create_command_for_psexec(
                                [
                                    CONST.MSG.EXECUTOR,
                                    j(("/time:", timeout)),
                                    login,
                                    message,
                                ],
                                workstation_name,
                            ),
                            False,
                        )
                    if method_type == WorkstationMessageMethodTypes.LOCAL_MSG:
                        PIH.EXECUTOR.execute(
                            [
                                CONST.MSG.EXECUTOR,
                                j(("/time:", timeout)),
                                login,
                                j(("/server:", workstation_name)),
                                message,
                            ],
                            False,
                        )

                if n(workstation_name):
                    result: Result[list[Workstation]] = PIH.RESULT.WORKSTATION.by_login(
                        user_login
                    )
                    ResultTool.every(
                        lambda workstation: internal_send_by_login_and_workstation_name(
                            user_login, workstation.name
                        ),
                        result,
                    )
                else:
                    if n(user_login):
                        internal_send_by_login_and_workstation_name(
                            "*", workstation_name
                        )
                    else:
                        internal_send_by_login_and_workstation_name(
                            user_login, workstation_name
                        )
                return True

            @staticmethod
            def by_login(
                value: str,
                message: str,
                timeout: int = 60,
                method_type: WorkstationMessageMethodTypes = WorkstationMessageMethodTypes.REMOTE,
            ) -> bool:
                return PIH.MESSAGE.WORKSTATION.to_user_or_workstation(
                    value, None, message, timeout, method_type
                )

        class WHATSAPP:
            class WAPPI:
                class QUEUE:
                    @staticmethod
                    def add(
                        message: Message,
                        recipient: str,
                        sender: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles,
                        high_priority: bool = False,
                    ) -> bool:
                        return PIH.MESSAGE.WHATSAPP.WAPPI.QUEUE.add_message(
                            Message(message, recipient, sender.value), high_priority
                        )

                    @staticmethod
                    def add_message(
                        message: Message, high_priority: bool = False
                    ) -> bool:
                        return DataTool.rpc_unrepresent(
                            PIH.SERVICE.call_command(
                                ServiceCommands.add_message_to_queue,
                                (message, high_priority),
                            )
                        )

                WAPPI_PROFILE_MAP: dict | None = None

                @staticmethod
                def get_wappi_collection() -> dict:
                    WP = CONST.MESSAGE.WHATSAPP.WAPPI
                    result: dict = PIH.MESSAGE.WHATSAPP.WAPPI.WAPPI_PROFILE_MAP or {
                        WP.Profiles.IT: PIH.DATA.TELEPHONE_NUMBER.it_administrator(),
                        WP.Profiles.CALL_CENTRE: PIH.DATA.TELEPHONE_NUMBER.call_centre_administrator(),
                        WP.Profiles.MARKETER: PIH.DATA.TELEPHONE_NUMBER.marketer_administrator(),
                    }
                    if PIH.MESSAGE.WHATSAPP.WAPPI.WAPPI_PROFILE_MAP is None:
                        PIH.MESSAGE.WHATSAPP.WAPPI.WAPPI_PROFILE_MAP = result
                    return result

                @staticmethod
                def send_to_group(
                    group: CONST.MESSAGE.WHATSAPP.GROUP,
                    message: str,
                    profile: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles = CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.IT,
                ) -> bool:
                    return PIH.MESSAGE.WHATSAPP.WAPPI.send(
                        group.value, message, profile
                    )

                @staticmethod
                def get_profile_id(
                    telephone_number: str,
                ) -> CONST.MESSAGE.WHATSAPP.WAPPI.Profiles:
                    if PIH.CHECK.telephone_number_international(telephone_number):
                        telephone_number = PIH.DATA.FORMAT.telephone_number(
                            telephone_number
                        )
                    profile_id_collection = (
                        PIH.MESSAGE.WHATSAPP.WAPPI.get_wappi_collection()
                    )
                    for item in profile_id_collection:
                        if profile_id_collection[item] == telephone_number:
                            return item
                    return None

                @staticmethod
                def get_message_list(
                    telephone_number: str,
                    profile: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | None = None,
                ) -> list[WhatsAppMessage]:
                    profile = EnumTool.get_by_value(
                        CONST.MESSAGE.WHATSAPP.WAPPI.Profiles,
                        profile or CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT,
                    )
                    profile_value: str = EnumTool.get_value(
                        profile,
                        EnumTool.get(profile),
                    )
                    url: str = (
                        f"{CONST.MESSAGE.WHATSAPP.WAPPI.URL_GET_MESSAGES}{profile_value}&chat_id={telephone_number}{CONST.MESSAGE.WHATSAPP.WAPPI.CONTACT_SUFFIX}"
                    )
                    headers: dict = {
                        "Authorization": CONST.MESSAGE.WHATSAPP.WAPPI.AUTHORIZATION[
                            profile
                        ],
                        "Content-Type": "application/json",
                    }
                    result: list[WhatsAppMessage] = []
                    try:
                        response: Response = requests.get(url, headers=headers)
                    except Exception:
                        return result
                    response_result: dict = json.loads(response.text)
                    has_error: bool = response_result["status"] == "error" or (
                        "detail" in response_result
                        and response_result["detail"] == "Messages not found"
                    )
                    key: str = "message"
                    if not has_error:
                        if A.D.is_in(response_result, key):
                            for message_item in response_result[key]:
                                if message_item["type"] == "chat":
                                    result.append(
                                        WhatsAppMessage(
                                            message_item["body"],
                                            message_item["fromMe"],
                                            str(message_item["from"]).split(
                                                EMAIL.SPLITTER
                                            )[0],
                                            str(message_item["to"]).split(
                                                EMAIL.SPLITTER
                                            )[0],
                                            profile,
                                            message_item["time"],
                                        )
                                    )
                    return result

                @staticmethod
                def send(
                    telephone_number: str,
                    message: Any,
                    profile: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | str | None = None,
                ) -> bool:
                    profile = EnumTool.get_by_value(
                        CONST.MESSAGE.WHATSAPP.WAPPI.Profiles,
                        profile or CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT,
                    )
                    profile_value: str = EnumTool.get_value(
                        profile,
                        EnumTool.get(profile),
                    )
                    url: str | None = None
                    payload: dict = {"recipient": telephone_number}
                    if isinstance(message, str):
                        payload["body"] = message
                        url = CONST.MESSAGE.WHATSAPP.WAPPI.URL_SEND_MESSAGE
                    elif isinstance(
                        message,
                        (WhatsAppMessageListPayload, WhatsAppMessageButtonsPayload),
                    ):
                        for item_name in message.__dataclass_fields__:
                            item_value: Any = message.__getattribute__(item_name)
                            if ne(item_value):
                                if item_name == "buttons":
                                    payload[item_name] = list(
                                        map(lambda button: button.__dict__, item_value)
                                    )
                                else:
                                    payload[item_name] = item_value
                        if isinstance(message, WhatsAppMessageListPayload):
                            url = CONST.MESSAGE.WHATSAPP.WAPPI.URL_SEND_LIST_MESSAGE
                        else:
                            url = CONST.MESSAGE.WHATSAPP.WAPPI.URL_SEND_BUTTONS_MESSAGE
                    url += profile_value
                    headers: dict = {
                        "accept": "application/json",
                        "Authorization": CONST.MESSAGE.WHATSAPP.WAPPI.AUTHORIZATION[
                            profile
                        ],
                        "Content-Type": "application/json",
                    }
                    try:
                        response: Response = requests.post(
                            url, data=dumps(payload), headers=headers
                        )
                    except ConnectTimeout:
                        return False
                    if response.status_code == CONST.ERROR.WAPPI.PROFILE_NOT_PAID:
                        PIH.LOG.resources(
                            "Аккаунт Wappi (сервис для отправики сообщений через WhatsApp) не оплачен",
                            LogMessageFlags.ERROR,
                        )
                    return response.status_code == 200

                @staticmethod
                def send_base64_file(
                    url: str,
                    telephone_number: str,
                    caption: str,
                    file_name: str | None,
                    base64_content: str,
                    profile: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | str | None = None,
                ) -> bool:
                    profile = EnumTool.get_by_value(
                        CONST.MESSAGE.WHATSAPP.WAPPI.Profiles,
                        profile or CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT,
                    )
                    profile_value: str = EnumTool.get_value(
                        profile,
                        EnumTool.get(profile),
                    )
                    payload: dict = {
                        "recipient": telephone_number,
                        "caption": caption,
                        "b64_file": base64_content,
                    }
                    if ne(file_name):
                        payload["file_name"] = file_name
                    headers: dict = {
                        "accept": "application/json",
                        "Authorization": CONST.MESSAGE.WHATSAPP.WAPPI.AUTHORIZATION[
                            profile
                        ],
                        "Content-Type": "application/json",
                    }
                    url = url + profile_value
                    try:
                        response: Response = requests.post(
                            url, data=dumps(payload), headers=headers
                        )
                    except ConnectTimeout:
                        return False
                    if response.status_code == CONST.ERROR.WAPPI.PROFILE_NOT_PAID:
                        PIH.LOG.resources(
                            "Аккаунт Wappi (сервис для отправики сообщений через WhatsApp) не оплачен",
                            LogMessageFlags.ERROR,
                        )
                    return response.status_code == 200

                @staticmethod
                def send_video(
                    telephone_number: str,
                    caption: str,
                    base64_content: str,
                    profile: Any | None = None,
                ) -> bool:
                    return PIH.MESSAGE.WHATSAPP.WAPPI.send_base64_file(
                        CONST.MESSAGE.WHATSAPP.WAPPI.URL_SEND_VIDEO,
                        telephone_number,
                        caption,
                        None,
                        base64_content,
                        profile,
                    )

                @staticmethod
                def send_image(
                    telephone_number: str,
                    caption: str,
                    base64_content: str,
                    profile: Any | None = None,
                ) -> bool:
                    return PIH.MESSAGE.WHATSAPP.WAPPI.send_base64_file(
                        CONST.MESSAGE.WHATSAPP.WAPPI.URL_SEND_IMAGE,
                        telephone_number,
                        caption,
                        None,
                        base64_content,
                        profile,
                    )

                @staticmethod
                def send_document(
                    telephone_number: str,
                    caption: str,
                    file_name: str,
                    base64_content: str,
                    profile: Any | None = None,
                ) -> bool:
                    return PIH.MESSAGE.WHATSAPP.WAPPI.send_base64_file(
                        CONST.MESSAGE.WHATSAPP.WAPPI.URL_SEND_DOCUMENT,
                        telephone_number,
                        caption,
                        file_name,
                        base64_content,
                        profile,
                    )

            @staticmethod
            def send_via_browser(telephone_number: str, message: str) -> bool:
                pywhatkit_is_exists: bool = (
                    importlib.util.find_spec("pywhatkit") is not None
                )
                if not pywhatkit_is_exists:
                    PIH.output.green(
                        "Установка библиотеки для отправки сообщения. Ожидайте..."
                    )
                    if not PIH.UPDATE.install_module("pywhatkit"):
                        PIH.output.error(
                            "Ошибка при установке библиотеки для отправки сообщений!"
                        )
                try:
                    import pywhatkit as pwk

                    pwk.sendwhatmsg_instantly(telephone_number, message)
                except Exception as уrror:
                    PIH.output.error("Ошибка при отправке сообщения!")

            @staticmethod
            def send(
                telephone_number: str,
                message: Any,
                via_wappi: bool = True,
                use_alternative: bool = True,
                wappi_profile: Any | None = None,
            ) -> bool:
                wappi_profile = EnumTool.get_value(
                    wappi_profile,
                    EnumTool.get(CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT),
                )
                result: bool = False
                telephone_number = PIH.DATA.FORMAT.telephone_number(telephone_number)
                if via_wappi:
                    result = PIH.MESSAGE.WHATSAPP.WAPPI.send(
                        telephone_number, message, wappi_profile
                    )
                if result:
                    return result
                if use_alternative or not via_wappi:
                    return PIH.MESSAGE.WHATSAPP.send_via_browser(
                        telephone_number, message
                    )
                return False

            @staticmethod
            def send_video(
                telephone_number: str,
                caption: str,
                base64_value: str,
                wappi_profile: Any | None = None,
            ) -> bool:
                wappi_profile = EnumTool.get_value(
                    wappi_profile,
                    EnumTool.get(CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT),
                )
                telephone_number = PIH.DATA.FORMAT.telephone_number(telephone_number)
                return PIH.MESSAGE.WHATSAPP.WAPPI.send_video(
                    telephone_number, caption, base64_value, wappi_profile
                )

            @staticmethod
            def send_image(
                telephone_number: str,
                caption: str,
                base64_value: str,
                wappi_profile: Any | None = None,
            ) -> bool:
                wappi_profile = EnumTool.get_value(
                    wappi_profile,
                    EnumTool.get(CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT),
                )
                telephone_number = PIH.DATA.FORMAT.telephone_number(telephone_number)
                return PIH.MESSAGE.WHATSAPP.WAPPI.send_image(
                    telephone_number, caption, base64_value, wappi_profile
                )

            @staticmethod
            def send_document(
                telephone_number: str,
                caption: str,
                base64_value: str,
                wappi_profile: Any | None = None,
            ) -> bool:
                wappi_profile = EnumTool.get_value(
                    wappi_profile,
                    EnumTool.get(CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT),
                )
                telephone_number = PIH.DATA.FORMAT.telephone_number(telephone_number)
                return PIH.MESSAGE.WHATSAPP.WAPPI.send_document(
                    telephone_number, caption, base64_value, wappi_profile
                )

            @staticmethod
            def send_to_user(
                user: User,
                message: Any,
                via_wappi: bool = True,
                use_alternative: bool = True,
                wappi_profile: Any | None = None,
            ) -> bool:
                return PIH.MESSAGE.WHATSAPP.send(
                    user.telephoneNumber,
                    message,
                    via_wappi,
                    use_alternative,
                    EnumTool.get_value(
                        wappi_profile,
                        EnumTool.get(CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.DEFAULT),
                    ),
                )

        class DELAYED:
            @staticmethod
            def register(message: DelayedMessage) -> int:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.register_delayed_message,
                        PIH.ACTION.MESSAGE.DELAYED._prepeare_message(message),
                    )
                )

            @staticmethod
            def send(message: DelayedMessage, high_priority: bool = True) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.send_delayed_message,
                        (
                            PIH.ACTION.MESSAGE.DELAYED._prepeare_message(message),
                            high_priority,
                        ),
                    )
                )

    class CARD_REGISTRY:
        @staticmethod
        def is_folder_registered(name: str) -> bool:
            return not A.R.is_empty(
                A.R_E.get(*A.E_B.card_registry_folder_was_registered(name))
            )

        @staticmethod
        def get_statistics() -> list[CardRegistryFolderStatistics]:
            query: str = (
                f"SELECT parameters->'$.{FIELD_NAME_COLLECTION.CARD_REGISTRY_FOLDER}' as name, count(*) as count FROM events where name = '{Events.CARD_REGISTRY_FOLDER_WAS_SET_FOR_POLIBASE_PERSON.name}' group by parameters->'$.{FIELD_NAME_COLLECTION.CARD_REGISTRY_FOLDER}' order by count desc;"
            )

            def map_function(value: dict) -> CardRegistryFolderStatistics:
                result: CardRegistryFolderStatistics = DataTool.fill_data_from_source(
                    CardRegistryFolderStatistics(), value
                )
                result.name = json.loads(result.name)
                return result

            return PIH.RESULT.map(map_function, A.R_DS.execute(query)).data

        @staticmethod
        def get_suitable_folder_name_for_person(
            value: PolibasePerson, forced: bool = False
        ) -> str:
            if not forced and (
                value.ChartFolder not in CONST.CARD_REGISTRY.SUITABLE_FOLDER_NAME_SYMBOL
            ):
                return None
            person_full_name_first_letter: str = value.FullName[0]
            folder_field_name: str = FIELD_NAME_COLLECTION.CARD_REGISTRY_FOLDER
            person_full_name_first_letter = person_full_name_first_letter.upper()
            place_letter: str = ""
            for holder_item in list(
                CONST.CARD_REGISTRY.PLACE_CARD_HOLDER_MAPPER.items()
            ):
                holder_letter_list: list[str] = holder_item[1].split("-")
                if (
                    person_full_name_first_letter >= holder_letter_list[0]
                    and person_full_name_first_letter <= holder_letter_list[1]
                ):
                    place_letter = holder_item[0]
                    break
            query: str = j(
                (
                    "SELECT parameters->",
                    escs(j(("$.", folder_field_name))),
                    " as name, count(*) as count FROM events where name = ",
                    escs(Events.CARD_REGISTRY_FOLDER_WAS_SET_FOR_POLIBASE_PERSON.name),
                    " and parameters->",
                    escs(j(("$.", folder_field_name))),
                    " like ",
                    escs(
                        j(("%", place_letter, "%", person_full_name_first_letter, "%"))
                    ),
                    " group by parameters->",
                    escs(j(("$.", folder_field_name))),
                    " order by count;",
                )
            )

            def map_function(value: dict[str, Any]) -> CardRegistryFolderStatistics:
                result: CardRegistryFolderStatistics = DataTool.fill_data_from_source(
                    CardRegistryFolderStatistics(), value
                )
                result.name = json.loads(result.name)
                return result

            return DataTool.get_first_item(
                PIH.RESULT.map(map_function, A.R_DS.execute(query)).data
            ).name

        @staticmethod
        def is_person_card_registry_folder(value: str) -> bool:
            return PIH.CHECK.POLIBASE.person_card_registry_folder(value)

        @staticmethod
        def set_folder_for_person(
            value: str | None,
            person: PolibasePerson,
            registrator_person: PolibasePerson,
            set_by_polibase: bool,
            already_set_by_polibase: bool = False,
        ) -> bool:
            event_builder = PIH.EVENT.BUILDER.polibase_person_set_card_registry_folder
            if set_by_polibase:
                if e(value):
                    PIH.ACTION.EVENTS.remove(*event_builder(None, person))
                    return True
                else:
                    event_ds: EventDS | None = ResultTool.get_first_item(
                        PIH.RESULT.EVENTS.get(*event_builder(None, person))
                    )
                    allow_add: bool = n(event_ds)
                    if not allow_add:
                        card_registry_folder: str = event_ds.parameters[
                            FIELD_NAME_COLLECTION.CARD_REGISTRY_FOLDER
                        ]
                        allow_add = card_registry_folder != value
                    if allow_add:
                        PIH.EVENT.send(
                            *event_builder(value, person, registrator_person)
                        )
                        return True
                    return False
            else:
                PIH.ACTION.POLIBASE.update_person_change_date(
                    person, registrator_person
                )
                PIH.EVENT.send(*event_builder(person=person, set_by_polibase=False))
                if already_set_by_polibase:
                    PIH.EVENT.send(*event_builder(value, person, registrator_person))
                else:
                    PIH.ACTION.POLIBASE.set_card_registry_folder(value, person)
                return True

        @staticmethod
        def start_card_sorting_for(folder_name: str) -> None:
            event_builder_function: Callable[
                [None], Events | tuple[Events, tuple[Any]]
            ] = PIH.EVENT.BUILDER.card_registry_folder_start_card_sorting
            PIH.ACTION.EVENTS.remove(*event_builder_function(folder_name))
            PIH.ACTION.EVENTS.remove(
                *PIH.EVENT.BUILDER.card_registry_folder_complete_card_sorting(
                    folder_name
                )
            )
            PIH.EVENT.send(*event_builder_function(folder_name))

        @staticmethod
        def complete_card_sorting_for(folder_name: str) -> None:
            event_builder_function: Callable[
                [None], Events | tuple[Events, tuple[Any]]
            ] = PIH.EVENT.BUILDER.card_registry_folder_complete_card_sorting
            PIH.ACTION.EVENTS.remove(*event_builder_function(folder_name))
            PIH.EVENT.send(*event_builder_function(folder_name))

        @staticmethod
        def folder_is_sorted(folder_name: str | None) -> bool:
            if e(folder_name):
                return False
            return ne(
                PIH.RESULT.EVENTS.get(
                    *PIH.EVENT.BUILDER.card_registry_folder_complete_card_sorting(
                        folder_name
                    )
                )
            )

        @staticmethod
        def persons_by_folder(
            folder_name: str,
            polibase_person_list_result: Result[list[PolibasePerson]] | None = None,
        ) -> Result[list[PolibasePerson]]:
            folder_is_sorted: bool = PIH.CARD_REGISTRY.folder_is_sorted(folder_name)
            polibase_person_list_result = (
                polibase_person_list_result
                or PIH.RESULT.POLIBASE.persons_by_card_registry_folder(folder_name)
            )
            if folder_is_sorted:
                ResultTool.sort(
                    PIH.DATA.POLIBASE.sort_person_list_by_pin,
                    polibase_person_list_result,
                )
            else:
                polibase_person_list_map: dict[int, PolibasePerson] = {
                    person.pin: person for person in polibase_person_list_result.data
                }
                polibase_person_list: list[PolibasePerson] = []
                polibase_person_pin_list: list[int] = (
                    PIH.CARD_REGISTRY.persons_pin_by_folder(folder_name)
                )
                for pin in polibase_person_pin_list:
                    if DataTool.is_in(polibase_person_list_map, pin):
                        polibase_person_list.append(polibase_person_list_map[pin])
                polibase_person_list_result.data = polibase_person_list
            return polibase_person_list_result

        @staticmethod
        def persons_pin_by_folder(folder_name: str) -> list[int]:
            def map_function(value: EventDS | PolibasePerson) -> int:
                if isinstance(value, PolibasePerson):
                    return value.pin
                return value.parameters[FIELD_NAME_COLLECTION.PERSON_PIN]

            folder_is_sorted: bool = PIH.CARD_REGISTRY.folder_is_sorted(folder_name)
            if folder_is_sorted:
                return list(
                    map(
                        map_function,
                        PIH.DATA.POLIBASE.sort_person_list_by_pin(
                            PIH.RESULT.POLIBASE.persons_by_card_registry_folder(
                                folder_name
                            ).data
                        ),
                    )
                )

            def sort_function(event: EventDS) -> datetime:
                return event.timestamp

            return ResultTool.map(
                map_function,
                ResultTool.sort(
                    sort_function,
                    PIH.RESULT.EVENTS.get(
                        *PIH.EVENT.BUILDER.polibase_person_set_card_registry_folder(
                            folder_name
                        )
                    ),
                ),
            ).data

    class ACTION:

        class FILES:

            @staticmethod
            def sync() -> None:
                def get() -> Result[list[File]]:
                    return DataTool.to_result(
                        PIH.SERVICE.call_command(
                            ServiceCommands.get_note_list_by_label,
                            (CONST.FILES.SECTION, True),
                        ),
                        File,
                    )

                PIH.RESULT.FILES.cache = get()

        class RECOGNIZE:
            @staticmethod
            def recognize_document(
                file_path: str, document_type: DocumentTypes | None = None
            ) -> bool:
                document_type = document_type or DocumentTypes.POLIBASE
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.recognize_document,
                        (file_path, EnumTool.get(document_type)),
                    )
                )

        class SSH:
            @staticmethod
            def mount_facade_for_linux_host(value: str | None) -> bool | None:
                if n(value) and not PIH.OS.is_linux():
                    return None
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.mount_facade_for_linux_host,
                        (value or PIH.OS.host(),),
                    )
                )

        class JOURNAL:
            @staticmethod
            def add(
                applicant_user: User,
                journal_type: JournalType,
                tag: Tags,
                title: str,
                text: str,
                parameters: dict[str, Any] | None = None,
            ) -> bool:
                def escape_string(value: str) -> str:
                    value = value.replace('"', "''")
                    value = value.replace("\\", "\\\\")
                    return value

                journal_type_value: tuple[int, OrderedNameCaptionDescription] = (
                    EnumTool.get(journal_type)
                )
                tag_value: tuple[int, IconedOrderedNameCaptionDescription] = (
                    EnumTool.get(tag)
                )
                PIH.EVENT.send(
                    Events.ADD_JOURNAL_RECORD,
                    (
                        tag_value[0],
                        journal_type_value[0],
                        applicant_user.samAccountName,
                        escape_string(title),
                        escape_string(text),
                        js((tag_value[1].icon, tag_value[1].caption)),
                        journal_type_value[1].caption,
                        parameters,
                    ),
                )

        class EMAIL:
            @staticmethod
            def send(recipient: str, subject: str, message: str) -> bool | None:
                if not PIH.CHECK.email(recipient):
                    recipient = PIH.DATA.FORMAT.email(
                        recipient, use_default_domain=True
                    )
                if PIH.CHECK.email(recipient, check_accesability=True):
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.send_email,
                            (recipient, j(("Subject:", nl(subject, count=2), message))),
                        )
                    )
                return None

        class PATH:
            @staticmethod
            def listen(value: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.listen_for_new_files, (value,)
                    )
                )

        class ACTIONS:
            @staticmethod
            def was_done(
                action: Actions | str,
                user_login_or_user: str | User | None = None,
                parameters: list[Any] | Any = [],
                forced: bool = False,
            ) -> bool | None:
                if not isinstance(parameters, list):
                    parameters = [parameters]
                user: User | None = None
                if isinstance(user_login_or_user, User):
                    user = user_login_or_user
                if e(user_login_or_user) or isinstance(user_login_or_user, str):
                    user = PIH.RESULT.USER.by_login(
                        user_login_or_user or AD.USER.ADMINISTRATOR, True, True
                    ).data
                _action: Actions | None = PIH.DATA.ACTIONS.get(action)
                if n(_action):
                    return None
                PIH.EVENT.send(
                    Events.ACTION_WAS_DONE,
                    (
                        EnumTool.get(_action).description,
                        _action.name,
                        user.name,
                        user.samAccountName,
                        parameters,
                        forced,
                    ),
                )
                return True

            @staticmethod
            def have_to_be_done(action: Actions | str) -> bool | None:
                _action: Actions | None = PIH.DATA.ACTIONS.get(action)
                if n(_action):
                    return None
                PIH.EVENT.send(
                    Events.ACTION_HAVE_TO_BE_DONE,
                    (_action.name, EnumTool.get(_action).description),
                )
                return True

        class EVENTS:
            @staticmethod
            def register(
                value: Events,
                parameters: dict[str, Any] | tuple[Any] | None = None,
                remove_before: bool = False,
            ) -> bool:
                if isinstance(parameters, Tuple):
                    parameters = PIH.EVENT.BUILDER.create_parameters_map(
                        value, parameters
                    )
                event_description: EventDescription = EnumTool.get(value)
                if remove_before:
                    parameters_for_removing: dict[str, Any] | None = parameters
                    key_name_list: tuple[str] | None = DataTool.map(
                        lambda item: item.name,
                        DataTool.filter(
                            lambda item: item.key, event_description.params
                        ),
                    )
                    if nn(key_name_list):
                        parameters_for_removing = {}
                        for key_name_item in key_name_list:
                            parameters_for_removing[key_name_item] = parameters[
                                key_name_item
                            ]
                    PIH.ACTION.EVENTS.remove(value, parameters_for_removing)
                visible_parameters: dict[str, Any] = {}
                for index, parameter_key in enumerate(parameters):
                    if event_description.params[index].saved:
                        visible_parameters[parameter_key] = parameters[parameter_key]
                parameters = visible_parameters
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.register_event,
                        (
                            EventDS(
                                value.name,
                                parameters,
                                DateTimeTool.now(use_microsecond=True),
                            ),
                        ),
                    )
                )

            @staticmethod
            def update(
                value: Events,
                parameter_for_search: tuple[Any],
                parameters_for_set: tuple[Any],
            ) -> bool:
                return PIH.ACTION.EVENTS.remove(
                    value, parameter_for_search
                ) and PIH.ACTION.EVENTS.register(
                    value,
                    PIH.EVENT.BUILDER.create_parameters_map(value, parameters_for_set),
                )

            @staticmethod
            def remove_by_key(
                event_type: Events | None, parameters: tuple[Any] | None = None
            ) -> Result[list[EventDS] | int]:
                return PIH.ACTION.EVENTS.remove(
                    *PIH.EVENT.BUILDER.by_key(event_type, parameters)
                )

            @staticmethod
            def remove(
                value: Events, parameters: tuple[Any] | dict[str, Any] | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.remove_event,
                        EventDS(
                            value.name,
                            DataTool.check(
                                isinstance(parameters, dict),
                                parameters,
                                lambda: PIH.EVENT.BUILDER.create_parameters_map(
                                    value, parameters, check_for_parameters_count=False
                                ),
                            ),
                        ),
                    )
                )

        class NOTES:
            @staticmethod
            def create(
                name: str,
                title: str,
                note: Note,
                label_list: list[str] | None = None,
                color: str | None = None,
                raw: bool = False,
            ) -> bool:
                id: str | None = DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_note, (note, label_list, color, raw)
                    )
                )
                if raw:
                    return True
                if e(id):
                    return False
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.add_gkeep_item, (name, title, id)
                    )
                )

            @staticmethod
            def create_raw(
                note: Note,
                label_list: list[str] | None = None,
                color: str | None = None,
            ) -> bool:
                return PIH.ACTION.NOTES.create(
                    None, None, note, label_list, color, True
                )

            @staticmethod
            def drop_cache(local: bool = False) -> bool:
                if not local:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(ServiceCommands.drop_note_cache)
                    )
                return True

        class QR_CODE:
            @staticmethod
            def titled(
                data: str, title, path: str, font_size: int | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_qr_code, (data, title, path, font_size)
                    )
                )

            @staticmethod
            def print(path: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(ServiceCommands.print_image, (path,))
                )

            @staticmethod
            def for_mobile_helper_command(
                value: str, title: str, path: str, font_size: int | None = None
            ) -> bool:
                return PIH.ACTION.QR_CODE.titled(
                    PIH.DATA.FORMAT.mobile_helper_qr_code_text(
                        PIH.DATA.FORMAT.mobile_helper_command(value)
                    ),
                    title,
                    path,
                    font_size,
                )

            @staticmethod
            def for_polibase_person_card_registry_folder(name: str) -> bool:
                name = PIH.DATA.FORMAT.polibase_person_card_registry_folder(name)
                return PIH.ACTION.QR_CODE.for_mobile_helper_command(
                    js(("card", "registry", urllib.parse.quote(name))),
                    name,
                    PIH.PATH.QR_CODE.polibase_person_card_registry_folder(name),
                    80,
                )

        class INDICATION:
            class CT:
                @staticmethod
                def register(value: CTIndicationsValue, forced: bool = False) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.register_ct_indications_value,
                            (value, forced),
                        )
                    )

            class CHILLER:
                @staticmethod
                def register(
                    value: ChillerIndicationsValue, forced: bool = False
                ) -> bool:
                    data: dict = PIH.SERVICE.call_command(
                        ServiceCommands.register_chiller_indications_value,
                        (value, forced),
                    )
                    return ne(data)

        class MOBILE_INPUT_OUTPUT:
            @staticmethod
            def send_command_to(
                value: str,
                recipient: str | Enum,
                chat_id: str | Enum | None = None,
                flags: int | None = None,
                return_result_key: str | None = None,
                args: tuple[Any] | None = None,
            ) -> None:
                recipient = EnumTool.get(recipient)
                if not value.startswith(PIH.NAME):
                    value = js((PIH.NAME, value))
                PIH.EVENT.whatsapp_message_received(
                    WhatsAppMessage(
                        value,
                        False,
                        recipient,
                        recipient,
                        EnumTool.get(CONST.MESSAGE.WHATSAPP.WAPPI.Profiles.IT),
                        int(A.D.now().timestamp()),
                        EnumTool.get(chat_id),
                        flags,
                        return_result_key,
                        args,
                    )
                )

            @staticmethod
            def write(
                telephone_number: str,
                message: Any,
                profile: CONST.MESSAGE.WHATSAPP.WAPPI.Profiles | str | None = None,
            ) -> bool:
                return PIH.MESSAGE.WHATSAPP.WAPPI.send(
                    telephone_number, message, profile
                )

        class BACKUP:
            @staticmethod
            def start_robocopy_job(
                name: str | None = None,
                source: str | None = None,
                destination: str | None = None,
                force: bool = False,
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.robocopy_start_job,
                        (name, source, destination, force),
                    )
                )

            @staticmethod
            def start_robocopy_job_by_name(value: str, force: bool = False) -> bool:
                return PIH.ACTION.BACKUP.start_robocopy_job(value, force=force)

        class DATA_STORAGE:
            @staticmethod
            def value(
                value: Any, name: str | None = None, section: str | None = None
            ) -> bool:
                try:
                    name = name or value.__getattribute__("name")
                except AttributeError as error:
                    pass
                else:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.set_storage_value, (name, value, section)
                        )
                    )

        class MESSAGE:
            class DELAYED:
                @staticmethod
                def update(
                    value: DelayedMessageDS, search_critery: MessageSearchCritery
                ) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.update_delayed_message,
                            (value, search_critery),
                        )
                    )

                @staticmethod
                def update_status(
                    value: DelayedMessageDS, status: MessageStatuses
                ) -> bool:
                    return PIH.ACTION.MESSAGE.DELAYED.update(
                        DelayedMessageDS(status=status.value),
                        MessageSearchCritery(id=value.id),
                    )

                @staticmethod
                def complete(value: DelayedMessageDS) -> bool:
                    return PIH.ACTION.MESSAGE.DELAYED.update_status(
                        value, MessageStatuses.COMPLETE
                    )

                @staticmethod
                def abort(value: DelayedMessageDS) -> bool:
                    return PIH.ACTION.MESSAGE.DELAYED.update_status(
                        value, MessageStatuses.ABORT
                    )

                @staticmethod
                def _prepeare_message(message: DelayedMessage) -> DelayedMessage:
                    if n(message.type):
                        message.type = MessageTypes.WHATSAPP.value
                    if nn(message.date):
                        if isinstance(message.date, datetime):
                            message.date = DateTimeTool.datetime_to_string(
                                message.date, CONST.ISO_DATETIME_FORMAT
                            )
                    if nn(message.sender):
                        message.sender = EnumTool.get_value(message.sender)
                    if message.type == MessageTypes.WHATSAPP.value and ne(
                        message.recipient
                    ):
                        if PIH.CHECK.telephone_number(message.recipient):
                            # +7 -> 7
                            message.recipient = PIH.DATA.FORMAT.telephone_number(
                                message.recipient,
                                CONST.INTERNATIONAL_TELEPHONE_NUMBER_PREFIX,
                            )
                    return message

        class SETTINGS:
            @staticmethod
            def key(key: str, value: Any) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_settings_value, (key, value)
                    )
                )

            @staticmethod
            def set(settings_item: SETTINGS | str, value: Any) -> bool:
                return PIH.ACTION.SETTINGS.key(
                    if_else(
                        isinstance(settings_item, str),
                        settings_item,
                        lambda: settings_item.value.key_name or settings_item.name,
                    ),
                    value,
                )

            @staticmethod
            def set_default(settings_item: SETTINGS) -> bool:
                return PIH.ACTION.SETTINGS.set(
                    settings_item, settings_item.value.default_value
                )

        class USER:
            @staticmethod
            def drop_user_cache() -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(ServiceCommands.drop_user_cache)
                )

            @staticmethod
            def create_from_template(
                container_dn: str,
                full_name: FullName,
                login: str,
                password: str,
                description: str,
                telephone: str,
                email: str,
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_user_by_template,
                        (
                            container_dn,
                            full_name,
                            login,
                            password,
                            description,
                            telephone,
                            email,
                        ),
                    )
                )

            @staticmethod
            def set_telephone_number(user: User, telephone: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_user_telephone_number,
                        (user.distinguishedName, telephone),
                    )
                )

            @staticmethod
            def set_password(user: User, password: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_user_password,
                        (user.distinguishedName, password),
                    )
                )

            @staticmethod
            def set_status(user: User, status: str, container: UserBase) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_user_status,
                        (
                            user.distinguishedName,
                            status,
                            DataTool.check(
                                container, lambda: container.distinguishedName
                            ),
                        ),
                    )
                )

            @staticmethod
            def remove(user: User) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.remove_user, user.distinguishedName
                    )
                )

        class TIME_TRACKING:
            @staticmethod
            def save_report(
                path: str,
                start_date: datetime,
                end_date: datetime,
                tab_number_list: list[str] | None = None,
                plain_format: bool = False,
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.save_time_tracking_report,
                        (
                            path,
                            DateTimeTool.begin_date(start_date),
                            DateTimeTool.end_date(end_date),
                            tab_number_list,
                            plain_format,
                        ),
                    )
                )

        class INVENTORY:
            @staticmethod
            def create_barcodes(report_file_path: str, result_directory: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_barcodes_for_inventory,
                        (report_file_path, result_directory),
                    )
                )

            @staticmethod
            def save_report_item(
                report_file_path: str, item: InventoryReportItem
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.save_inventory_report_item,
                        (report_file_path, item),
                    )
                )

            @staticmethod
            def close_report(report_file_path: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.close_inventory_report, report_file_path
                    )
                )

        class PRINTER:
            @staticmethod
            def report() -> bool:
                return ne(PIH.RESULT.PRINTER.report())

            @staticmethod
            def status() -> bool:
                return ne(PIH.RESULT.PRINTER.status())

        class POLIBASE:
            executor: PIHThreadPoolExecutor = PIHThreadPoolExecutor(max_workers=10)

            def update_person_change_date(
                polibase_person: PolibasePerson,
                registrator_polibase_person: PolibasePerson,
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.update_person_change_date,
                        (polibase_person.pin, registrator_polibase_person.pin),
                    )
                )

            @staticmethod
            def client_program_close_for_all(
                notify: bool = True,
                notification_message: str | None = None,
                test: bool = True,
            ) -> None:
                def close_action(workstation: Workstation) -> None:
                    PIH.ACTION.POLIBASE.client_program_close_for_workstation(
                        workstation
                    )

                def filter_function(workstation: Workstation) -> bool:
                    return (
                        workstation.name == CONST.TEST.WORKSTATION_MAME
                        if test
                        else workstation.accessable
                    )

                def every_action(workstation: Workstation) -> None:
                    PIH.ACTION.POLIBASE.executor.submit(
                        PIH.ERROR.wrap(close_action), workstation
                    )

                if notify:
                    PIH.MESSAGE.POLIBASE.notify_about_polibase_closing(
                        notification_message, test
                    )
                ResultTool.every(
                    every_action,
                    ResultTool.filter(filter_function, PIH.RESULT.WORKSTATION.all()),
                )

            @staticmethod
            def client_program_close_for_workstation(workstation: Workstation) -> bool:
                return PIH.ACTION.WORKSTATION.kill_process(
                    POLIBASE.PROCESS_NAME, workstation.name
                )

            def restart(test: bool = True) -> None:
                PIH.EXECUTOR.ws_reboot(
                    HOSTS.POLIBASE_TEST.NAME if test else HOSTS.POLIBASE.NAME
                )

            class NOTIFICATION:
                @staticmethod
                def register(value: PolibasePersonVisitNotificationDS) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.register_polibase_person_visit_notification,
                            value,
                        )
                    )

                class CONFIRMATION:
                    @staticmethod
                    def update(recepient: str, sender: str, status: int) -> bool:
                        return DataTool.rpc_unrepresent(
                            PIH.SERVICE.call_command(
                                ServiceCommands.update_polibase_person_notification_confirmation,
                                PolibasePersonNotificationConfirmation(
                                    recepient, sender, status
                                ),
                            )
                        )

            class INFORMATION_QUEST:
                @staticmethod
                def register(person: PolibasePerson) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.register_polibase_person_information_quest,
                            PolibasePersonInformationQuest(
                                person.pin, person.FullName, person.telephoneNumber
                            ),
                        )
                    )

                @staticmethod
                def start(person_or_pin: PolibasePerson | int) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.start_polibase_person_information_quest,
                            (
                                (
                                    person_or_pin
                                    if isinstance(person_or_pin, int)
                                    else person_or_pin.pin
                                ),
                            ),
                        )
                    )

                @staticmethod
                def update(
                    value: PolibasePersonInformationQuest,
                    search_critery: PolibasePersonInformationQuest,
                ) -> bool:
                    return DataTool.rpc_unrepresent(
                        PIH.SERVICE.call_command(
                            ServiceCommands.update_polibase_person_information_quest,
                            (value, search_critery),
                        )
                    )

            @staticmethod
            def create_barcode_for_person(
                person_or_pin: PolibasePerson | int, test: bool | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_barcode_for_polibase_person,
                        (PIH.RESULT.POLIBASE._person_pin(person_or_pin), test),
                    )
                )

            @staticmethod
            def set_card_registry_folder(
                value: str | None,
                person: PolibasePerson,
                test: bool | None = None,
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_polibase_person_card_folder_name,
                        (value, PIH.RESULT.POLIBASE._person_pin(person), test),
                    )
                )

            @staticmethod
            def email(
                value: str, person: PolibasePerson, test: bool | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_polibase_person_email,
                        (value, person.pin, test),
                    )
                )

            @staticmethod
            def set_telephone_number(
                index: int, value: str, person: PolibasePerson, test: bool | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_polibase_person_telephone_number,
                        (index, value, person.pin, test),
                    )
                )

            @staticmethod
            def set_barcode(
                value: str, person: PolibasePerson, test: bool | None = None
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_barcode_for_polibase_person,
                        (value, person.pin, test),
                    )
                )

            class DB:
                @staticmethod
                def backup(
                    dump_file_name: str | None = None, test: bool | None = None
                ) -> bool:
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_polibase_database_backup,
                        (dump_file_name, test),
                    )
                    return True

            class VISIT:
                class DATA_STORAGE:
                    @staticmethod
                    def update(value: PolibasePersonVisitDS) -> bool:
                        return DataTool.rpc_unrepresent(
                            PIH.SERVICE.call_command(
                                ServiceCommands.update_polibase_person_visit_to_data_stogare,
                                value,
                            )
                        )

        class MARK:
            @staticmethod
            def door_operation(door_name: str, operation_name: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.door_operation,
                        (door_name, operation_name),
                    )
                )

            @staticmethod
            def create(
                full_name: FullName,
                person_division_id: int,
                tab_number: str,
                telephone: str | None = None,
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_mark,
                        (full_name, person_division_id, tab_number, telephone),
                    )
                )

            @staticmethod
            def set_full_name_by_tab_number(
                full_name: FullName, tab_number: str
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_full_name_by_tab_number,
                        (full_name, tab_number),
                    )
                )

            @staticmethod
            def set_telephone_by_tab_number(telephone: str, tab_number: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.set_telephone_by_tab_number,
                        (telephone, tab_number),
                    )
                )

            @staticmethod
            def make_as_free_by_tab_number(tab_number: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.make_mark_as_free_by_tab_number, tab_number
                    )
                )

            @staticmethod
            def make_as_temporary(temporary_mark: Mark, owner_mark: Mark) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.make_mark_as_temporary,
                        (temporary_mark.TabNumber, owner_mark.TabNumber),
                    )
                )

            @staticmethod
            def remove(mark: Mark) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.remove_mark_by_tab_number, mark.TabNumber
                    )
                )

        class DOCUMENTS:
            @staticmethod
            def create_statistics_chart(type: STATISTICS.Types) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_statistics_chart, (type.name,)
                    )
                )

            @staticmethod
            def save_xlsx(
                title: str, result: Result[list[dict[str, Any]]], path: str
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.save_xlsx,
                        (title, result.fields.list, result.data, path),
                    )
                )

            @staticmethod
            def save_base64_as_image(path: str, content: str) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.save_base64_as_image, (path, content)
                    )
                )

            @staticmethod
            def create_for_user(
                path: str,
                full_name: FullName,
                tab_number: str,
                pc: LoginPasswordPair | None,
                polibase: LoginPasswordPair | None,
                email: LoginPasswordPair,
            ) -> bool:
                locale.setlocale(locale.LC_ALL, "ru_RU")
                date_now = datetime.now().date()
                date_now_string = f"{date_now.day} {calendar.month_name[date_now.month]} {date_now.year}"
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.create_user_document,
                        (
                            path,
                            date_now_string,
                            ADDRESSES.SITE_ADDRESS,
                            CONST.SITE_PROTOCOL + ADDRESSES.SITE_ADDRESS,
                            ADDRESSES.EMAIL_SERVER_ADDRESS,
                            full_name,
                            tab_number,
                            pc,
                            polibase,
                            email,
                        ),
                    )
                )

        class WORKSTATION:
            @staticmethod
            def reboot(host: str | None = None, force: bool = False) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(ServiceCommands.reboot, (host, force))
                )

            @staticmethod
            def shutdown(host: str | None = None, force: bool = False) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(ServiceCommands.shutdown, (host, force))
                )

            @staticmethod
            def kill_process(
                name_or_pid: str | int, host: str, via_standart_tools: bool = True
            ) -> bool:
                return DataTool.rpc_unrepresent(
                    PIH.SERVICE.call_command(
                        ServiceCommands.kill_process,
                        (name_or_pid, host, via_standart_tools),
                    )
                )

            @staticmethod
            def kill_python_process(
                host: str, via_standart_tools: bool = False
            ) -> bool:
                return PIH.ACTION.WORKSTATION.kill_process(
                    CONST.PYTHON.EXECUTOR, host, via_standart_tools
                )


class ActionStack(list):
    def __init__(
        self,
        caption: str = "",
        *argv: Callable[[], ActionValue | None],
        input: InputBase = None,
        output: OutputBase = None,
    ):
        self.input = input or PIH.input
        self.output = output or PIH.output
        self.acion_value_list: list[ActionValue] = []
        self.caption = caption
        for arg in argv:
            self.append(arg)
        self.start()

    def call_actions_by_index(self, index: int = 0, change: bool = False):
        previous_change: bool = False
        while True:
            try:
                action_value: ActionValue = self[index]()
                if action_value:
                    if change or previous_change:
                        previous_change = False
                        if index < len(self.acion_value_list):
                            self.acion_value_list[index] = action_value
                        else:
                            self.acion_value_list.append(action_value)
                    else:
                        self.acion_value_list.append(action_value)
                index = index + 1
                if index == len(self) or change:
                    break
            except KeyboardInterrupt:
                self.output.new_line()
                self.output.error("Повтор предыдущих действия")
                self.output.new_line()
                if index > 0:
                    previous_change = True
                    # self.show_action_values()
                    # index = index - 1
                else:
                    continue

    def show_action_values(self) -> None:
        def label(item: ActionValue, _):
            return item.caption

        self.call_actions_by_index(
            self.input.index(
                "Выберите свойство для изменения, введя индекс",
                self.acion_value_list,
                label,
            ),
            True,
        )

    def start(self):
        self.call_actions_by_index()
        while True:
            self.output.new_line()
            self.output.head2(self.caption)
            for action_value in self.acion_value_list:
                self.output.value(action_value.caption, action_value.value)
            if self.input.yes_no("Данные верны", True):
                break
            else:
                self.show_action_values()


class PathPolibaseExtended(PATH_POLIBASE):
    @staticmethod
    def person_folder(pin: int, test: bool = False) -> str:
        return PIH.PATH.path(PATH_POLIBASE.person_folder(pin, test))

    @staticmethod
    def person_barcode(person_pin: int) -> str:
        return PIH.PATH.join(
            PATH_POLIBASE.person_folder(person_pin),
            POLIBASE.BARCODE.get_file_name(person_pin, with_extension=True),
        )


class A:
    root = PIH()

    NAME = PIH.NAME

    IW = root.INPUT_WAIT

    R = root.RESULT
    D = root.DATA
    D_V = D.VARIABLE
    D_V_T = D_V.TIMESTAMP
    D_V_T_E = D_V_T.EXPIRED
    D_V_E = D_V.ENVIRONMENT
    D_TN = D.TELEPHONE_NUMBER
    D_MR = D.MATERIALIZED_RESOURCES
    D_FL = D.FILTER
    D_Ex = D.EXTRACT
    D_Ex_E = D_Ex.EVENT
    D_M = D.MARK
    D_C = D.CHECK
    D_STAT = D.STATISTICS
    D_U = D.USER
    D_J = D.JOURNAL
    A = root.ACTION
    A_F = A.FILES

    A_D = A.DOCUMENTS
    A_SSH = A.SSH
    A_QR = A.QR_CODE
    A_IND = A.INDICATION
    A_IND_CT = A_IND.CT
    A_IND_CH = A_IND.CHILLER
    ME = root.MESSAGE
    ME_P = ME.POLIBASE
    A_WS = A.WORKSTATION
    R_ME = R.MESSAGE
    R_R = R.RESOURCES
    R_RCG = R.RECOGNIZE
    R_SSH = R.SSH
    R_IND = R.INDICATIONS
    R_N = R.NOTES
    R_E = R.EVENTS
    R_INV = R.INVENTORY
    #
    A_ME = A.MESSAGE
    A_J = A.JOURNAL
    A_ACT = A.ACTIONS
    A_TT = A.TIME_TRACKING
    A_MIO = A.MOBILE_INPUT_OUTPUT
    R_ME_D = R_ME.DELAYED
    A_ME_D = A_ME.DELAYED
    A_N = A.NOTES
    A_E = A.EVENTS
    A_EM = A.EMAIL
    A_RCG = A.RECOGNIZE

    #
    ME_WS = ME.WORKSTATION
    ME_P = ME.POLIBASE
    ME_WH = ME.WHATSAPP
    ME_D = ME.DELAYED
    ME_WH_W = ME_WH.WAPPI
    ME_WH_W_Q = ME_WH_W.QUEUE
    A_ME_WH_W_Q = ME_WH_W.QUEUE
    #
    S = root.SETTINGS
    S_U = S.USER
    S_P = S.POLIBASE
    S_R = S.RESOURCE
    S_WS = S.WORKSTATION
    S_P_V = S_P.VISIT
    S_P_RN = S_P.REVIEW_NOTIFICATION
    #
    C = root.CHECK
    C_COMP = C.COMPUTER
    D_ACT = D.ACTIONS
    C_R = C.RESOURCE
    C_IND = C.INDICATION
    C_IND_D = C_IND.DEVICE
    C_INV = C.INVENTORY
    C_M = C.MARK
    C_TT = C.TIME_TRACKING
    C_A = C.ACCESS
    C_S = C.SETTINGS
    C_WS = C.WORKSTATION
    C_ME = C.MESSAGE
    C_ME_WH = C_ME.WHATSAPP
    C_ME_WH_W = C_ME_WH.WAPPI
    C_N = C.NOTES
    C_J = C.JOURNALS
    C_EML = C.EMAIL
    C_RCG = C.RECOGNIZE
    #
    A_M = A.MARK
    R_M = R.MARK
    R_U = R.USER
    R_F = R.FILES
    R_TT = R.TIME_TRACKING
    A_U = A.USER
    C_U = C.USER
    D_F = D.FORMAT
    D_F_B = D_F.BACKUP
    D_CO = D.CONVERT
    A_P = A.POLIBASE
    A_INV = A.INVENTORY
    C_E = C.EVENTS
    C_P = C.POLIBASE
    C_P_DB = C_P.DATABASE
    D_P = D.POLIBASE
    R_P = R.POLIBASE
    R_PR = R.PRINTER
    R_SRVS = R.SERVER
    R_EM = R.EMAIL
    R_IND_D = R_IND.DEVICE
    #
    A_PTH = A.PATH
    A_P_V = A_P.VISIT
    A_P_V_DS = A_P_V.DATA_STORAGE
    R_P_V = R_P.VISIT
    R_P_V_DS = R_P_V.DATA_STORAGE
    A_P_N = A_P.NOTIFICATION
    A_P_N_C = A_P_N.CONFIRMATION
    R_P_N = R_P.NOTIFICATION
    R_P_N_C = R_P_N.CONFIRMATION
    C_P_N = C_P.NOTIFICATION
    C_P_N_С = C_P_N.CONFIRMATION
    R_WS = R.WORKSTATION
    R_COMP = R.COMPUTER
    C_WS = C.WORKSTATION
    C_COMP = C.COMPUTER
    A_P_IQ = A_P.INFORMATION_QUEST
    R_P_IQ = R_P.INFORMATION_QUEST
    SRV = root.SERVICE
    SRV_A = SRV.ADMIN
    I = root.input
    I_U = I.user
    A_B = A.BACKUP
    R_B = R.BACKUP
    O = root.output
    SE = root.session
    A_DS = A.DATA_STORAGE
    R_DS = R.DATA_STORAGE
    V = root.VERSION
    OS = root.OS
    U = root.UPDATE
    EXC = root.EXECUTOR
    ER = root.ERROR
    E = root.EVENT
    E_B = E.BUILDER
    PTH = root.PATH
    PTH_STAT = PTH.STATISTICS
    PTH_DS = PTH.DATA_STORAGE
    PTH_U = PTH.USER
    PTH_P = PathPolibaseExtended
    PTH_QR = PTH.QR_CODE
    PTH_FNT = PTH.FONTS
    PTH_IND = PTH.INDICATIONS
    PTH_MIO = PTH.MOBILE_HELPER
    PTH_FACADE = PTH.FACADE
    L = root.LOG
    R_J = R.JOURNALS

    CT = CONST
    CT_FACADE = FACADE
    CT_PY = CONST.PYTHON
    CT_PORT = CONST.PORT
    CT_CMDT = CommandTypes
    CT_LNK = LINK
    CT_MR = MATERIALIZED_RESOURCES
    CT_WINDOWS = WINDOWS
    CT_SCN = SCAN
    CT_EVM = EmailVerificationMethods
    CT_D = DATA
    CT_DT = DocumentTypes
    CT_RBK = ROBOCOPY
    CT_H = HOSTS
    CT_FNT = FONT
    CT_SR = ServiceRoles
    CT_SC = ServiceCommands
    CT_SubT = SubscribtionTypes
    CT_F = FILE
    CT_EML = EMAIL_COLLECTION
    CT_R = RESOURCES
    CT_R_D = CT_R.DESCRIPTIONS
    CT_ADDR = ADDRESSES
    CT_R_IR = ResourceInaccessableReasons
    CT_STAT = STATISTICS
    CT_F_E = CT_F.EXTENSION
    CT_P = POLIBASE
    CT_P_DT = PolibaseDocumentTypes
    CT_P_VS = PolibasePersonVisitStatus
    CT_FC = FIELD_COLLECTION
    CT_S = SETTINGS
    CT_ME = CT.MESSAGE
    CT_ME_WH = CT_ME.WHATSAPP
    CT_ME_WH_G = CT_ME.WHATSAPP.GROUP
    CT_ME_WH_W = CT_ME_WH.WAPPI
    CT_L_ME_F = LogMessageFlags
    CT_L_ME_CH = LogMessageChannels
    CT_V = CT.VISUAL
    CT_E = Events
    CT_J = JournalType
    CT_Tag = Tags
    CT_ACT = Actions
    CT_MRT = MedicalResearchTypes
    CT_FNC = FIELD_NAME_COLLECTION
    CT_FCA = FieldCollectionAliases
    CT_UP = USER_PROPERTIES
    CT_AD = AD
    CT_AD_U = AD.USER
    CT_AD_UP = AD.UserProperies
    CT_I = INDICATIONS
    CT_T = Tags
    CT_CR = CT.CARD_REGISTRY
    C_P_DB = C_P.DATABASE
    CT_PI = PARAM_ITEMS

    D_P = D.POLIBASE
    R_P = R.POLIBASE

    CR = root.CARD_REGISTRY
    #

    C_V_T_E = D_C.VARIABLE.TIMESTAMP.EXPIRED


def delay(
    action: Callable[[None], None], value: float = 1, block: bool = False
) -> None:
    def action_support() -> None:
        sleep(value)
        action()

    if block:
        action_support
    else:
        PIHThread(action_support)
