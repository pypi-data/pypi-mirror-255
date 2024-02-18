from datetime import datetime, timedelta
from contextlib import contextmanager
from collections import defaultdict
from typing import Any, Callable
from time import sleep
from dataclasses import dataclass
from enum import Enum
from requests import Response
from string import Formatter
import json
import requests
from io import BytesIO
import calendar

from MobileHelperContent.content import MEDIA_CONTENT

from pih.collection import (
    User,
    Mark,
    Note,
    File,
    Result,
    EventDS,
    MarkGroup,
    GKeepItem,
    FieldItem,
    Workstation,
    FieldItemList,
    PolibasePerson,
    ResourceStatus,
    ActionDescription,
    RobocopyJobStatus,
    StorageVariableHolder,
    IntStorageVariableHolder,
    TimeStorageVariableHolder,
    BoolStorageVariableHolder,
    CardRegistryFolderPosition,
    CardRegistryFolderStatistics,
    IconedOrderedNameCaptionDescription,
    InaccesableEmailInformation,
    PolibaseDocument,
)

from pih.console_api import ConsoleAppsApi
from pih.tools import (
    BitMask as BM,
    i,
    b,
    n,
    e,
    j,
    nl,
    js,
    nn,
    ne,
    one,
    esc,
    escs,
    jnl,
    if_else,
    while_not_do,
)
from pih.const import CheckableSections, Actions, JournalType, Tags, SPLITTER
from pih.consts.polibase import PolibaseDocumentTypes
from pih.consts.ssh_hosts import SSHHosts
from MobileHelperService.const import *
from MobileHelperService.collection import MobileHelperUserSettings

from pih.errors import BarcodeNotFound, NotFound, Error
from pih import (
    A,
    PIH,
    PIHThread,
    Input,
    Stdin,
    Output,
    Session,
    MarkInput,
    UserInput,
    UserOutput,
    MarkOutput,
    SessionBase,
    OutputStub,
)
from pih.console_api import LINE
import re
from re import Match
import traceback
from subprocess import CompletedProcess


class MobileHelperUserSettiongsHolder:
    @staticmethod
    def get(login: str) -> MobileHelperUserSettings:
        value: MobileHelperUserSettings = MobileHelperUserSettings()
        result: MobileHelperUserSettings | None = A.S_U.get(
            login, MOBILE_HELPER_USER_SETTINGS_NAME, value
        )
        if n(result):
            MobileHelperUserSettiongsHolder.set(login, value)
            result = value
        return result

    @staticmethod
    def set(login: str, value: MobileHelperUserSettings) -> bool:
        return A.S_U.set(login, MOBILE_HELPER_USER_SETTINGS_NAME, value)


class UserSettings:
    def __init__(self, login: str):
        self.login: str = login

    def get(self) -> MobileHelperUserSettings:
        return MobileHelperUserSettiongsHolder.get(self.login)

    def set(self, value: int) -> bool:
        return MobileHelperUserSettiongsHolder.set(
            self.login, MobileHelperUserSettings(value)
        )

    def has(self, value: int) -> bool:
        return BM.has(self.get().flags, value)

    def remove(self, value: int) -> bool:
        return self.set(BM.remove(self.get().flags, value))

    def add(self, value: int) -> bool:
        return self.set(BM.add(self.get().flags, value))


def command_name_base(value: str) -> str:
    return value.split(COMMAND_NAME_BASE_DELEMITER)[0]


def mio_command(value: list[str] | str) -> str:
    if isinstance(value, str):
        return command_name_base(value)
    return mio_command(one(value))


def flag_name_list(value: Flags, all: bool = False) -> list[str]:
    result: list[str] = [
        item[0]
        for item in A.D.filter(lambda item: item[1] == value, list(FLAG_MAP.items()))
    ]
    return result if all else [result[0]]


def flag_string_represent(value: Flags, all: bool = True) -> str:
    return js(
        (
            "[",
            j(
                A.D.map(lambda item: b(item), flag_name_list(value, all)),
                j((" ", i("или"), " ")),
            ),
            "]",
        )
    )


def format_given_name(
    session: Session, _: Output | None, name: str | None = None
) -> str | None:
    if e(session.login):
        return None
    return b(name or session.user_given_name)


class InternalInterrupt(Exception):
    @property
    def type(self) -> int:
        return self.args[0]


class AddressedInterruption(Exception):
    @property
    def sender_user(self) -> User:
        return self.args[0]

    @property
    def recipient_user_list(self) -> list[User]:
        return self.args[1]

    @property
    def command_name(self) -> str:
        return self.args[2]

    @property
    def flags(self) -> int:
        return self.args[3]


class MobileUserOutput(UserOutput):
    def result(
        self,
        result: Result[list[User]],
        caption: str | None = None,
        use_index: bool = False,
        root_location: str = A.CT_AD.ACTIVE_USERS_CONTAINER_DN,
    ) -> None:
        if ne(caption):
            self.parent.write_line(b(caption))
        self.parent.write_result(result, use_index=use_index)

    def get_formatted_given_name(self, value: str | None = None) -> str:
        return b(value)


class MobileSession(SessionBase):
    def __init__(self, recipient: str, flags: int | None = 0):
        super().__init__(name="mobile", flags=flags)
        self.recipient: str = recipient
        self.user: User | None = None
        self.arg_list: list[str] | None = None

    def say_hello(self, telephone_number: str | None = None) -> None:
        self.get_user(telephone_number)

    def get_login(self, telephone_number: str | None = None) -> str:
        if n(self.user):
            self.start(
                A.R_U.by_telephone_number(telephone_number or self.recipient).data
            )
            self.login = self.user.samAccountName
        return self.login

    def get_user(self, telephone_number: str | None = None) -> User:
        if n(self.user):
            user = A.R_U.by_login(self.get_login(telephone_number), True, True).data
        else:
            user = self.user
        return user

    @property
    def user_given_name(self) -> str:
        return A.D.to_given_name(self.user.name)

    def start(self, user: User, _1: bool = True) -> None:
        if n(self.user):
            self.user = user

    def exit(self, _1: int | None = None, _2: str | None = None) -> None:
        raise InternalInterrupt(InterruptionTypes.EXIT)

    @property
    def argv(self) -> list[str] | None:
        return self.arg_list

    def arg(self, index: int = 0, default_value: Any | None = None) -> str | Any | None:
        return A.D.by_index(self.argv, index, default_value)


class MobileMarkOutput(MarkOutput):
    def result(
        self,
        result: Result[list[Mark]],
        caption: str | None = None,
        use_index: bool = False,
    ) -> None:
        if ne(caption):
            self.parent.write_line(b(caption))
        self.parent.write_result(result, use_index=use_index)


@dataclass
class MessageHolder:
    body: str | None = None
    text_before: str = ""

    def to_string(self) -> str:
        return self.text_before + self.body


class MobileOutput(Output):
    def __init__(self, session: MobileSession):
        super().__init__(MobileUserOutput(), MobileMarkOutput())
        self.message_buffer: list[MessageHolder] = []
        self.thread_started: bool = False
        self.session: MobileSession = session
        self.type: int = 0
        self.instant_mode: bool = False
        self.write_line_delay: float = 0.2
        self.recipient: str | None = None
        self.profile: A.CT.MESSAGE.WHATSAPP.WAPPI.Profiles = (
            A.CT.MESSAGE.WHATSAPP.WAPPI.Profiles.IT
        )
        self.flags: int = 0
        self.locked: bool = False
        self.show_exit_message: bool = True
        self.exit_line: str | None = None
        self.show_error: bool = True

    @contextmanager
    def set_show_exit_message(self, value: bool):
        value_before: bool = self.show_exit_message
        try:
            self.show_exit_message = value
            yield True
        finally:
            self.show_exit_message = value_before

    @contextmanager
    def set_write_line_delay(self, value: float):
        value_before: float = self.write_line_delay
        try:
            self.write_line_delay = value
            yield True
        finally:
            self.write_line_delay = value_before

    @contextmanager
    def make_instant_mode(self):
        try:
            self.instant_mode = True
            yield True
        finally:
            self.instant_mode = False

    def color_str(
        self,
        color: int,
        text: str,
        text_before: str | None = None,
        text_after: str | None = None,
    ) -> str:
        return text

    def whatsapp_send(self, text: str) -> bool:
        return A.ME_WH_W.send(self.get_recipient(), text, self.profile)

    @contextmanager
    def send_to_group(self, group: A.CT.MESSAGE.WHATSAPP.GROUP):
        try:
            while_not_do(lambda: e(self.message_buffer))
            self.recipient = A.D.get(group)
            yield True
        finally:
            self.recipient = None

    def b(self, value: str) -> str:
        return b(value)

    @contextmanager
    def make_separated_lines(self):
        try:
            self.type = BM.add(self.type, MessageType.SEPARATED)
            yield True
        finally:
            self.type = BM.remove(self.type, MessageType.SEPARATED)

    @contextmanager
    def make_exit_line(self, value: str | None = None):
        if nn(value):
            value = self.create_exit_line(
                j((value, ": ")),
                self.keywords.command.BACK,
            )
        try:
            self.exit_line = (
                j((nl(self.create_exit_line())))
                if n(value)
                else j(
                    (
                        nl("Отправьте:"),
                        " ",
                        A.CT_V.BULLET,
                        " ",
                        self.create_exit_line("для выхода"),
                        nl("или", reversed=None),
                        " ",
                        A.CT_V.BULLET,
                        " ",
                        value,
                    )
                )
            )
            yield True
        finally:
            self.exit_line = None

    @contextmanager
    def make_personalized(self, enter: bool = True):
        if enter:
            try:
                while_not_do(lambda: e(self.message_buffer))
                self.personalize = True
                yield True
            finally:
                self.personalize = False
        else:
            value: bool = self.personalize
            try:
                self.personalize = False
                yield True
            finally:
                self.personalize = value

    @contextmanager
    def make_allow_show_error(self, value: bool):
        value_before: bool = self.show_error
        try:
            self.show_error = value
            yield True
        finally:
            self.show_error = value_before

    @contextmanager
    def make_loading(
        self,
        loading_timeout: float = 1,
        text: str | None = None,
    ):
        while_not_do(lambda: e(self.message_buffer))
        thread: PIHThread | None = None

        try:

            def show_loading() -> None:
                sleep(loading_timeout)
                if nn(thread):
                    self.whatsapp_send(
                        js(("", A.CT_V.WAIT, i(j((text or "Идёт загрузка", "...")))))
                    )

            thread = PIHThread(show_loading)
            self.locked = True
            yield True
        finally:
            self.locked = False
            thread = None

    def internal_write_line(self) -> None:
        while self.locked:
            pass
        if not self.instant_mode:
            sleep(self.write_line_delay)
        message_list: list[MessageHolder] | None = None

        def get_next_part_messages() -> list[MessageHolder]:
            max_lines: int = MAX_MESSAGE_LINE_LENGTH
            return (
                self.message_buffer
                if len(self.message_buffer) < max_lines
                else self.message_buffer[0:max_lines]
            )

        message_list = get_next_part_messages()
        while len(self.message_buffer) > 0:
            self.message_buffer = [
                item for item in self.message_buffer if item not in message_list
            ]
            while_not_do(
                lambda: self.whatsapp_send(
                    jnl(A.D.map(self.add_text_before, message_list))
                )
            )
            message_list = get_next_part_messages()
        self.thread_started = False

    def add_text_before(self, message_holder: MessageHolder) -> str:
        return jnl(
            A.D.map(
                lambda message_body: MessageHolder(
                    message_body, message_holder.text_before
                ).to_string(),
                message_holder.body.splitlines(),
            )
        )

    def get_recipient(self) -> str:
        return self.recipient or self.session.recipient

    def write_line(self, text: str) -> None:
        if self.personalize:
            user_name: str | None = self.user.get_formatted_given_name()
            if ne(user_name):
                text = j((user_name, ", ", A.D.decapitalize(text)))
        if ne(text):
            if not self.locked and BM.has(
                self.type, [MessageType.SEPARATE_ONCE, MessageType.SEPARATED]
            ):
                message_holder: MessageHolder = MessageHolder(text, self.text_before)
                self.type = BM.remove(self.type, MessageType.SEPARATE_ONCE)
                while self.thread_started:
                    pass
                self.whatsapp_send(self.add_text_before(message_holder))
            else:
                self.message_buffer.append(MessageHolder(text, self.text_before))
                if not self.thread_started:
                    self.thread_started = True
                    PIHThread(self.internal_write_line)

    def write_video(self, caption: str, video_content: str) -> None:
        return A.ME_WH_W.send_video(
            self.session.recipient, caption, video_content, self.profile
        )

    def write_image(self, caption: str, image_content: str) -> bool:
        return A.ME_WH_W.send_image(
            self.session.recipient,
            j((self.text_before, caption)),
            image_content,
            self.profile,
        )

    def write_document(
        self, caption: str, file_name: str, document_content: str
    ) -> None:
        return A.ME_WH_W.send_document(
            self.session.recipient, caption, file_name, document_content, self.profile
        )

    def create_exit_line(
        self,
        title: str = "Для выхода, отправьте:",
        keywords: list[str] = COMMAND_KEYWORDS.EXIT,
    ) -> str:
        return i(
            js(
                (
                    title,
                    j(
                        A.D.map(
                            lambda item: b(A.D.capitalize(item)),
                            keywords,
                        ),
                        " или ",
                    ),
                )
            )
        )

    def input(self, value: str) -> None:
        self.separated_line()
        with self.make_personalized(True):
            with self.make_indent(2, True):
                self.write_line(j((value, SPLITTER)))
                if self.show_exit_message:
                    with self.make_indent(2):
                        with self.make_personalized(False):
                            self.write_line(self.exit_line or self.create_exit_line())

    def value(self, caption: str, value: Any, text_before: str | None = None) -> None:
        self.separated_line()
        self.write_line(j((b(caption), ": ", value)))

    def good(self, value: str) -> None:
        self.write_line(nl(js((A.CT_V.GOOD, value))))

    def error(self, value: str | Any) -> None:
        if self.show_error:
            self.separated_line()
            self.write_line(
                nl(
                    js(
                        (
                            A.CT_V.ERROR,
                            (value if isinstance(value, str) else value.get_details()),
                        )
                    )
                )
            )

    def head(self, value: str) -> None:
        self.write_line(nl(b(value.upper())))

    def head1(self, value: str) -> None:
        self.write_line(nl(b(value)))

    def head2(self, value: str) -> None:
        self.write_line(b(value))

    def new_line(self) -> None:
        return

    def separated_line(self) -> None:
        self.type = BM.add(self.type, MessageType.SEPARATE_ONCE)

    def header(self, value: str) -> None:
        self.write_line(js(("", A.CT_V.BULLET, nl(b(value)))))

    def bold(self, value: str) -> str:
        return b(value)

    def italic(self, value: str) -> str:
        return i(value)

    def free_marks_by_group_for_result(
        self, group: MarkGroup, result: Result, use_index: bool
    ) -> None:
        group_name: str = group.GroupName
        self.write_line(
            js(
                (
                    "Свободные карты доступа для группы доступа",
                    j((esc(group_name), ":")),
                )
            )
        )
        self.write_result(
            result,
            use_index=False,
            data_label_function=lambda index, _, __, data_value: j((index + 1, ". "))
            + b(data_value),
        )

    def table_with_caption(
        self,
        result: Result,
        caption: str | None = None,
        use_index: bool = False,
        modify_table_function: Callable | None = None,
        label_function: Callable | None = None,
    ) -> None:
        if caption is not None:
            self.write_line(nl(caption))
        is_result_type: bool = isinstance(result, Result)
        field_list = result.fields if is_result_type else result.fields
        data: Any = result.data if is_result_type else result.data
        if e(data):
            self.error("Не найдено!")
        else:
            if not isinstance(data, list):
                data = [data]
            length: int = len(data)
            if length == 1:
                use_index = False
            if use_index:
                field_list.list.insert(0, A.CT_FC.INDEX)
            item_data: Any | None = None
            result_text_list: list[list[str]] = []
            for index, item in enumerate(data):
                row_data: list = []
                for field_item_obj in field_list.get_list():
                    field_item: FieldItem = field_item_obj
                    if field_item.visible:
                        if field_item == A.CT_FC.INDEX:
                            row_data.append(
                                j((b(index + 1), "."))
                                + " "
                                * (
                                    len(str(length))
                                    - len(str(index + 1))
                                    + 1
                                    + (1 if index < 9 and len(str(length)) > 1 else 0)
                                )
                            )
                        elif not isinstance(item, dict):
                            if label_function is not None:
                                modified_item_data = label_function(field_item, item)
                                if modified_item_data is None:
                                    modified_item_data = getattr(item, field_item.name)
                                row_data.append(
                                    A.D.check(
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
                                    A.D.check(item_data, lambda: item_data, "")
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
                row_data = A.D.map(lambda item: str(item), row_data)
                result_text_list.append(row_data)
            self.write_line(
                j(
                    (
                        (
                            " "
                            * (
                                2
                                + (1 if len(str(length)) > 1 else 0)
                                + len(str(length))
                            )
                            if use_index
                            else ""
                        ),
                        A.D.list_to_string(
                            A.D.map(
                                lambda item: i(item.caption),
                                A.D.filter(
                                    lambda item: item.visible,
                                    field_list.get_list()[1:]
                                    if use_index
                                    else field_list.get_list(),
                                ),
                            ),
                            separator=js(("", A.CT_V.ARROW)),
                        ),
                        nl(LINE, reversed=True),
                    )
                )
            )
            for item in result_text_list:
                self.write_line(
                    item[0]
                    + j(
                        A.D.check(use_index, item[1:], item),
                        j((" ", A.CT_V.ARROW, " ")),
                    )
                )

    def free_marks_by_group_for_result(
        self, group: MarkGroup, result: Result, use_index: bool
    ) -> None:
        self.table_with_caption_last_title_is_centered(
            result,
            f"Свободные карты доступа для группы доступа '{group.GroupName}':",
            use_index,
        )


class MobileMarkInput(MarkInput):
    pass


class MobileUserInput(UserInput):
    def title_any(self, title: str | None = None) -> str:
        return self.parent.input(
            title or "введите логин, часть имени или другой поисковый запрос",
        )

    def template(self) -> dict:
        return self.parent.item_by_index(
            "Выберите шаблон пользователя, введя индекс",
            A.R_U.template_list().data,
            lambda item, _: item.description,
        )


class MobileInput(Input):
    def __init__(
        self,
        stdin: Stdin,
        user_input: MobileUserInput,
        mark_input: MobileMarkInput,
        output: MobileOutput,
        session: MobileSession,
        data_input_timeout: int | None = None,
    ):
        super().__init__(user_input, mark_input, output)
        self.stdin: Stdin = stdin
        self.session = session
        self.data_input_timeout: int | None = (
            None
            if data_input_timeout == -1
            else (data_input_timeout or A.S.get(MOBILE_HELPER_USER_DATA_INPUT_TIMEOUT))
        )

    @contextmanager
    def input_timeout(self, value: int | None):
        data_input_timeout: int | None = self.data_input_timeout
        try:
            self.data_input_timeout = value
            yield True
        finally:
            self.data_input_timeout = data_input_timeout

    def telephone_number(
        self, format: bool = True, telephone_prefix: str = A.CT.TELEPHONE_NUMBER_PREFIX
    ) -> str:
        while True:
            use_telephone_prefix: bool = nn(telephone_prefix)
            telephone_number: str = self.input("Введите номер телефона", False)
            if use_telephone_prefix:
                if not telephone_number.startswith(telephone_prefix):
                    telephone_number = telephone_prefix + telephone_number
            check: bool | None = None
            if format:
                telehone_number_after_fix = A.D_F.telephone_number(
                    telephone_number, telephone_prefix
                )
                check = A.C.telephone_number(telehone_number_after_fix)
                if check and telehone_number_after_fix != telephone_number:
                    telephone_number = telehone_number_after_fix
                    self.output.value("Телефон отформатирован", telephone_number)
            if check or A.C.telephone_number(telephone_number):
                return telephone_number
            else:
                self.output.error("Неверный формат номера телефона!")

    def input(
        self,
        caption: str | None = None,
        _: bool = True,
        check_function: Callable[[str], Any | None] | None = None,
    ) -> str:
        input_data: str | None = None
        while True:
            if ne(caption):
                self.output.input(caption)
            self.stdin.wait_for_data_input = True

            def internal_input() -> None:
                start_time: int = 0
                sleep_time: int = 1
                while True:
                    if not self.stdin.is_empty() or self.stdin.interrupt_type > 0:
                        return
                    sleep(sleep_time)
                    start_time += sleep_time
                    if (
                        ne(self.data_input_timeout)
                        and start_time > self.data_input_timeout
                    ):
                        self.stdin.interrupt_type = InterruptionTypes.TIMEOUT
                        return

            action_thread = PIHThread(internal_input)
            action_thread.join()
            self.stdin.wait_for_data_input = False
            input_data = self.stdin.data
            if self.stdin.interrupt_type > 0:
                interrupt_type: int = self.stdin.interrupt_type
                self.stdin.set_default_state()
                raise InternalInterrupt(interrupt_type)
            self.stdin.set_default_state()
            if n(check_function):
                return input_data
            else:
                checked_input_data: str | None = check_function(input_data)
                if nn(checked_input_data):
                    return checked_input_data

    def yes_no(
        self,
        text: str,
        _: bool = False,
        yes_label: str = YES_LABEL,
        no_label: str = NO_LABEL,
        yes_checker: Callable[[str], bool] | None = None,
    ) -> bool:
        default_yes_label: bool = yes_label == YES_LABEL
        if not default_yes_label:
            yes_label = j((" ", A.CT.VISUAL.BULLET, " ", yes_label))
        if no_label != NO_LABEL:
            no_label = j((" ", A.CT.VISUAL.BULLET, " ", no_label))
        text = j(
            (
                nl(j((text, A.CT_V.QUESTION))),
                nl(LINE),
                nl(yes_label),
                nl("или"),
                no_label,
            )
        )
        self.answer = self.input(text).lower().strip()
        return (
            (
                self.answer in YES_VARIANTS
                if default_yes_label
                else self.answer not in ["0", "no", "нет"]
            )
            if yes_checker is None
            else yes_checker(self.answer)
        )

    def item_by_index(
        self,
        caption: str,
        data: list[Any],
        label_function: Callable[[Any, int], str] | None = None,
        use_zero_index: bool = False,
    ) -> Any:
        return super().item_by_index(
            j((caption, ", отправив число")), data, label_function, use_zero_index
        )

    def interrupt_for_new_command(self) -> None:
        self.stdin.interrupt_type = InterruptionTypes.NEW_COMMAND

    def interrupt(self) -> None:
        self.stdin.interrupt_type = InterruptionTypes.EXIT

    def wait_for_polibase_person_pin_input(self, action: Callable[[None], str]) -> str:
        return self.wait_for_input(POLIBASE_PERSON_PIN, action)

    def wait_for_polibase_person_card_registry_folder_input(
        self, action: Callable[[None], str]
    ) -> str:
        return self.wait_for_input(POLIBASE_PERSON_CARD_REGISTRY_FOLDER, action)

    def wait_for_input(self, name: str, action: Callable[[None], str]) -> str:
        A.IW.add(name, self.session.recipient, self.data_input_timeout)
        try:
            result: str = action()
        except InternalInterrupt as interruption:
            raise interruption
        finally:
            A.IW.remove(name, self.session.recipient)
        return result

    def polibase_person_card_registry_folder(
        self, value: str | None = None, title: str | None = None
    ) -> str:
        return self.wait_for_polibase_person_card_registry_folder_input(
            lambda: super(MobileInput, self).polibase_person_card_registry_folder(
                value,
                f"Введите:\n  {A.CT_V.BULLET} название папки с картами пациентов\n  {A.CT_V.BULLET} символ {b('!')} для автоматического выбора папки\n или\n  {A.CT_V.BULLET} отсканируйте QR-код на папке реестра карт пациентов",
            )
        )

    def polibase_person_any(self, title: str | None = None) -> str:
        return self.wait_for_polibase_person_pin_input(
            lambda: self.input(
                title
                or f"Введите:\n  {A.CT_V.BULLET} персональный номер\n  {A.CT_V.BULLET} часть имени пациента\nили\n  отсканируйте штрих-код на карте пациента"
            )
        )


@dataclass
class CommandNode:
    name_list: list[str] | None = None
    title_and_label: list[str] | Callable[[None], list[str]] | None = None
    handler: Callable[[None], None] | None = None
    allowed_groups: list[Groups] | None = None
    wait_for_input: bool = True
    show_in_main_menu: bool = False
    parent: Any | None = None
    text: str | Callable[[None], str] | None = None
    visible: bool = True
    show_always: bool = False
    description: str | Callable[[None], str] | None = None
    order: int | None = None
    filter_function: Callable[[None], bool] | None = None
    help_text: Callable[[None], str] | None = None
    text_decoration_before: str | Callable[[None], str] | None = None
    text_decoration_after: str | Callable[[None], str] | None = None
    settings_handler: Callable[[None], None] | None = None

    def __hash__(self) -> int:
        return hash(j(self.name_list, "|"))

    def set_visible(self, value: bool):
        self.visible = value
        return self

    def clone_as(
        self,
        name: str | None = None,
        title_and_label: str | Callable[[None], list[str] | None] | None = None,
        handler: Callable[[None], None] | None = None,
        clone_title_and_label: bool = False,
        filter_function: Callable[[None], bool] | None = None,
    ):
        return CommandNode(
            name or self.name_list,
            title_and_label
            or (self.title_and_label if clone_title_and_label else None),
            handler or self.handler,
            self.allowed_groups,
            self.wait_for_input,
            self.show_in_main_menu,
            filter_function=filter_function or self.filter_function,
            help_text=self.help_text,
        )


@dataclass
class IndexedLink:
    object: Any
    attribute: str


@dataclass
class HelpContent:
    content: Callable[[None], str] | IndexedLink | None = None
    text: str | None = None
    title: str | None = None
    show_loading: bool = True
    show_next: bool = True


def extract_command_menu(value: str) -> tuple[str, list[list[CommandNode]]]:
    result: list[CommandNode] = []
    fields: list[str] = [name for _, name, _, _ in Formatter().parse(value) if name]
    for field_item in fields:
        index_start: int = field_item.find('"menu"')
        if index_start != -1:
            index_start = value.find('"menu":')
            index_end: int = value.find("]}") + 2
            index_start -= 1
            manu_text: str = value[index_start:index_end]
            value = value[0:index_start] + value[index_end : len(value) - 1]
            menu_json = json.loads(manu_text)
            for menu_json_item in menu_json["menu"]:
                result.append(
                    [
                        CommandNode(
                            [menu_json_item["command"]], [None, menu_json_item["label"]]
                        )
                    ]
                )
    return value, result


@dataclass
class HelpVideoContent(HelpContent):
    pass


@dataclass
class HelpImageContent(HelpContent):
    pass


@dataclass
class HelpContentHolder:
    name: str | None = None
    title_and_label: list[str] | str | None = None
    content: list[HelpVideoContent | HelpImageContent] | None = None


class MENU:
    backup: list[CommandNode] | None = None
    card_registry: list[CommandNode] | None = None
    polibase: list[CommandNode] | None = None
    polibase_person: list[CommandNode] | None = None
    it: list[CommandNode] | None = None
    it_help: list[CommandNode] | None = None
    unit: list[CommandNode] | None = None
    workstation: list[CommandNode] | None = None
    notes: list[CommandNode] | None = None
    hr_unit: list[CommandNode] | None = None
    call_centre: list[CommandNode] | None = None
    check: list[CommandNode] | None = None
    run_command: list[CommandNode] | None = None
    polibase_doctor: list[CommandNode] | None = None
    user: list[CommandNode] | None = None
    journals: list[CommandNode] | None = None
    marketer_unit: list[CommandNode] | None = None


@dataclass
class KEYWORDS:
    flag: FLAG_KEYWORDS = FLAG_KEYWORDS
    command: COMMAND_KEYWORDS = COMMAND_KEYWORDS
    FROM_FILE_REDIRECT: str = FROM_FILE_REDIRECT_SYMBOL


def get_file_pattern_index(value: str | None) -> int | None:
    if e(value):
        return None
    for file_pattern_index, pattern in enumerate(FILE_PATTERN_LIST):
        if value.find(pattern) == 0:
            return file_pattern_index
    return None


def check_for_arg_is_file(self, value: str) -> bool:
    return nn(get_file_pattern_index(value))


class MobileHelper(OutputStub):
    command_node_name_list: list[str] | None = None
    allowed_group_list: list[Groups] | None = None

    def create_study_course_item(
        self,
        index: int,
        item: HelpContentHolder,
        item_list: dict[CommandNode, None],
        content_list: list[HelpContentHolder],
        wiki_location: Callable[[None], str] | None = None,
    ) -> CommandNode:
        return CommandNode(
            [item.name],
            [item.title_and_label]
            if isinstance(item.title_and_label, str)
            else item.title_and_label,
            lambda: self.study_course_handler(
                index, item_list, content_list, wiki_location=wiki_location
            ),
            wait_for_input=False,
        )

    def get_journal_add_record_title(self) -> list[str]:
        journal_type_list: list[JournalType] | None = A.D_J.type_by_any(self.arg())
        journal_type: JournalType | None = (
            one(journal_type_list)
            if ne(journal_type_list) and len(journal_type_list) == 1
            else None
        )
        result: str = (
            "" if n(journal_type) else js(("", esc(A.D.get(journal_type)[1].caption)))
        )
        return [
            j(("Добавление записи в журнал", result)),
            j(("Добавить запись в журнал", result)),
        ]

    def get_journal_title(self) -> list[str]:
        journal_type_list: list[JournalType] | None = A.D_J.type_by_any(self.arg())
        journal_type: JournalType | None = (
            one(journal_type_list)
            if ne(journal_type_list) and len(journal_type_list) == 1
            else None
        )
        return [
            j(
                (
                    "Журнал",
                    "ы"
                    if n(journal_type)
                    else j((" ", esc(A.D.get(journal_type)[1].caption))),
                )
            )
        ]

    def get_it_telephone_number_text(self) -> str:
        return j(
            (
                "Общий телефон: ",
                nl(b("709")),
                "Сотовый телефон: ",
                b(A.D_TN.by_login("Administrator")),
            )
        )

    def long_operation_handler(self) -> None:
        self.write_line(i("Ожидайте получения результата..."))

    @staticmethod
    def polibase_status() -> str:
        resource: ResourceStatus | None = A.R_R.get_resource_status(A.CT_R_D.POLIBASE)
        return A.D.check_not_none(
            resource, lambda: A.D_F.yes_no(resource.accessable, True), ""
        )

    @property
    def is_person_card_registry_folder(self) -> bool:
        name: str | None = self.arg()
        if n(name):
            return True
        return A.CR.is_person_card_registry_folder(name)

    @property
    def is_person_card_registry_folder_registered(self) -> bool:
        name: str | None = self.arg()
        if n(name):
            return True
        return A.CR.is_folder_registered(name)

    @property
    def arg_len(self) -> int:
        return 0 if n(self.arg_list) else len(self.arg_list)

    @property
    def none_command(self) -> bool:
        return n(self.current_command)

    def ws_ping_handler(self) -> None:
        with self.output.make_loading(loading_timeout=0.5):
            self.write_line(
                js(
                    (
                        "Результат:",
                        A.D_F.yes_no(
                            A.C_R.accessibility_by_ping(
                                self.arg() or self.input.input("Введите название хоста")
                            ),
                            True,
                        ),
                    )
                )
            )

    @property
    def am_i_admin(self) -> bool:
        return Groups.Admin in self.session.allowed_groups

    @property
    def am_i_doctor(self) -> bool:
        return self.is_doctor(self.session.user) or self.am_i_admin

    def is_doctor(self, value: User) -> bool:
        distinguishedName: str | None = value.distinguishedName
        return ne(distinguishedName) and not (
            distinguishedName.find("Доктор") == -1
            and distinguishedName.find("Оператор") == -1
        )

    def yes_no_adapted(
        self,
        text: str,
        _: bool = False,
        yes_label: str = YES_LABEL,
        no_label: str = NO_LABEL,
        yes_checker: Callable[[str], bool] | None = None,
    ) -> bool:
        return self.yes_no(
            text,
            yes_label,
            no_label,
            yes_checker,
        )

    def get_run_title_and_label(self, command_type: A.CT_CMDT) -> Callable[[None], str]:
        return lambda: [
            js(
                (
                    "Запустить" if self.is_all else None,
                    A.D.decapitalize(A.D.get(command_type)[0]),
                )
            )
        ]

    def __init__(self, pih: PIH, stdin: Stdin):
        self.pih: PIH = pih
        self.console_apps_api: ConsoleAppsApi = ConsoleAppsApi(pih)
        self.console_apps_api.yes_no = self.yes_no_adapted
        self.stdin: Stdin = stdin
        self.flags: int = 0
        self.external_flags: int | None = 0
        self.line_part_list: list[str] | None = None
        self.arg_list: list[str] | None = None
        self.flag_information: list[tuple(int, str, Flags)] | None = None
        self.command_node_tree: dict | None = None
        self.command_node_cache: list = []
        self.command_node_tail_list: dict[CommandNode, list[CommandNode]] = {}
        self.current_command: list[CommandNode] | None = None
        self.command_list: list[list[CommandNode]] = []
        self.command_history: list[list[CommandNode]] = []
        self.recipient_user_list: list[User] | None = None
        self.line: str | None = None
        self.show_good_bye: bool | None = None
        self.language_index: int | None = None
        self.comandless_line_part_list: list[str] | None
        self.menu = MENU()
        self.keywords = KEYWORDS()
        self.return_result_key: str | None = None
        self.user_settings: UserSettings = UserSettings(self.session.login)
        # output stub rewrite
        self.b = b
        self.i = i

        def get_formatted_given_name(name: str | None = None) -> str | None:
            return format_given_name(self.session, None, name)

        self.output.user.get_formatted_given_name = get_formatted_given_name
        #######################
        self.study_node: CommandNode = self.create_command_link(
            A.D.map(lambda item: j((COMMAND_LINK_SYMBOL, item)), ["study", "обучение"]),
            "study",
            ["Обучение"],
            None,
            False,
            "🎓 ",
        )
        #######################
        INFINITY_STUDY_COURCE_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "telephone_collection",
                ["Список внутренних телефонов колл-центра"],
                [
                    HelpContent(
                        None,
                        f"Вам нужно знать ваш внутренний телефон для входа в программу *инфинити*.\nПомещение *колл-центра*:\n{A.CT.VISUAL.BULLET} Дальний слева: *303*\n{A.CT.VISUAL.BULLET} Дальний справа: *305*\n{A.CT.VISUAL.BULLET} Ближний справа: *306*\n\n*Регистратура поликлиники*:\n{A.CT.VISUAL.BULLET} левый: *121*\n{A.CT.VISUAL.BULLET} правый: *120*\n\n*Регистратура больницы*:\n*240*",
                    )
                ],
            ),
            HelpContentHolder(
                "setup",
                ["Настройка при первом входе"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.INFINITY_A.CT_S,
                        '*Важно*: в поле "Имя" нужно внести внутренний номер телефона, на которым Вы принимаете звонки',
                    )
                ],
            ),
            HelpContentHolder(
                "missed_calls",
                ["Просмотр пропущенных звонков"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.INFINITY_OPEN_MISSED_CALLS
                    )
                ],
            ),
            HelpContentHolder(
                "infinity_status",
                ["Установка статуса"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.INFINITY_ABOUT_STATUSES,
                        "Чтобы начать принимать звонки, ставим статус *'На месте'*. Уходя с рабочего места, ставим статус *'Перерыв'* (не *'Отошел'*!)",
                    )
                ],
            ),
        ]
        INFINITY_STUDY_COURSE_COLLECTION: dict[CommandNode, None] = {}
        for index, item in enumerate(INFINITY_STUDY_COURCE_CONTENT_LIST):
            INFINITY_STUDY_COURSE_COLLECTION[
                self.create_study_course_item(
                    index,
                    item,
                    INFINITY_STUDY_COURSE_COLLECTION,
                    INFINITY_STUDY_COURCE_CONTENT_LIST,
                )
            ] = None
        ######################
        CALLCENTRE_BROWSER_STUDY_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "_ccbli",
                ["Как войти в общий аккаунт в браузере Google Chrome"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.CALL_CENTRE_BROWSER_LOG_IN,
                        f"Если коротко: включить синхронизацию при входе в общий аккаунт:\n {A.CT.VISUAL.BULLET} Логин: *{A.CT_ADDR.RECEPTION_LOGIN}*\n {A.CT.VISUAL.BULLET} Пароль: *QmF1ZA8n*",
                    )
                ],
            ),
            HelpContentHolder(
                "_ccbp",
                ["О панели вкладок"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.CALL_CENTRE_BROWSER_BOOKMARKS
                    )
                ],
            ),
        ]
        CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION: dict[CommandNode, None] = {}
        for index, item in enumerate(CALLCENTRE_BROWSER_STUDY_CONTENT_LIST):
            CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION[
                self.create_study_course_item(
                    index,
                    item,
                    CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION,
                    CALLCENTRE_BROWSER_STUDY_CONTENT_LIST,
                )
            ] = None
        #######################
        CARD_REGISTRY_STUDY_COURCE_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "introduction",
                ["О курсе"],
                [
                    HelpImageContent(
                        None,
                        f"Любые данные любят порядок. Особенно, если их много. В нашей больнице очень много карт пациентов. В данном курсе Вы, {self.user_given_name}, узнаете и научитесь:\n {A.CT.VISUAL.BULLET} о штрих-кодах на картах пациентов\n {A.CT.VISUAL.BULLET} научитесь добавлять новые штрих-коды в документ карты пациента и распечатывать этот документ\n {A.CT.VISUAL.BULLET} добавлять карту пациента в папку\n {A.CT.VISUAL.BULLET} искать карту пациента с помощью инструментов и программ",
                        None,
                        False,
                    ),
                ],
            ),
            HelpContentHolder(
                "about_card",
                ["О картах пациентов"],
                [
                    HelpImageContent(
                        None,
                        f'Все карты хранятся в папках. Папки с активными картами хранятся на полках шкафов:\n {A.CT.VISUAL.BULLET} *регистратуры Поликлиники*\n {A.CT.VISUAL.BULLET} *регистратуры Приемного отделения*\n {A.CT.VISUAL.BULLET} у *Анны Генадьевны Комиссаровой*\n\nУ каждой папки есть название. Если папка хранится:\n {A.CT.VISUAL.BULLET} на регистратуре Поликлиники, то название папки начинается на *"П"*\n {A.CT.VISUAL.BULLET} на регистратуре Приемного отделения, то название папки начинается на *"Т"*\n {A.CT.VISUAL.BULLET} у Анны Генадьевны Комиссаровой - одна папка и называется она *"Б"*.',
                        None,
                        False,
                    ),
                ],
            ),
            HelpContentHolder(
                "folder_name",
                ["Наклейка с именем папки"],
                [
                    HelpContent(
                        lambda: MEDIA_CONTENT.IMAGE.CARD_FOLDER_LABEL_LOCATION,
                        "Название папки нанесена на наклейку, которая располагается в двух местах:",
                        "На корешковой части",
                        False,
                    ),
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.CARD_FOLDER_LABEL_LOCATION2,
                        None,
                        "На лицевой части",
                        False,
                    ),
                ],
            ),
            HelpContentHolder(
                "barcode",
                ["Штрих-код на карте пациента"],
                [
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.CARD_BARCODE_LOCATION,
                        None,
                        "На самой карте пациента располагается штрих-код в левой верхней части. В нем закодирован _персональный номер пациента_. Он необходим для быстрого выполнения операций с картой пациента: добаления в папку и поиска.\n*Обратите внимание*: не на всех картах пациента есть штрих-коды или эти штрих-код старого формата.\n\n_*Давайте научимся отличать штрих-кода нового и старого форматов*_",
                        False,
                    ),
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.POLIBASE_PERSON_NEW_BAR_CODE,
                        None,
                        "Новый – более четкий, широкий",
                        False,
                    ),
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.POLIBASE_PERSON_OLD_BAR_CODE,
                        None,
                        "Старый – менее четкий, высокий",
                        False,
                    ),
                ],
            ),
            HelpContentHolder(
                "tools",
                ["Инструментарий"],
                [
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.CARD_FOLDER_NAME_POLIBASE_LOCATION,
                        None,
                        f'Для того, чтобы узнать в какой папке находится карта пациента, нам необходимо, чтобы название папки было внесено в электронную карту пациента с помощью программы: *Полибейс* в поле *"Таб. номер"*.\n\n {A.CT.VISUAL.BULLET} Для добавления этого значения в электронную карту пациента, было нужно использовать программу: *"Polibase. Добавление карты пациента в папку"*\n\n {A.CT.VISUAL.BULLET} Для поиска карты пациента производится с помощью программы *"Polibase. Поиск пациента по штрих-коду"*',
                        False,
                    ),
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.BARCODE_READER,
                        None,
                        f"Для этих операций нужен инстумент: *сканер штрих и QR-кодов* для быстрого считывания значения названия папки и _персональный номера пациента_ со штрихкода на карте пациента.\n*_Сканирование происходит при нажатиий на желтую кнопку, при удачном сканировании издается звуковой сигнал._*\nСканер должен быть соединен с компьютером, с помощью провода, который вставляется в *разъем USB* компьютера",
                        False,
                    ),
                ],
            ),
            HelpContentHolder(
                "add_bar_code",
                ["Добавление штрих-кода нового формата"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.POLIBASE_ADD_PERSON_NEW_BARCODE,
                        None,
                        "Процесс добавления штрих-кода нового формата на первый лист документа *МЕД КАРТА v3 (025У)*, если штрих-код отсутствует или старого формата. После добавоения штрих-кода необходимо распечатать этот документ.",
                        False,
                    ),
                ],
            ),
            HelpContentHolder(
                "add_person",
                ["Добавление карты пациента в папку"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.POLIBASE_ADD_PERSON_CARD_TO_FOLDER,
                        None,
                        None,
                        False,
                    ),
                ],
            ),
        ]
        CARD_REGISTRY_STUDY_COURSE_COLLECTION: dict[CommandNode, None] = {}
        for index, item in enumerate(CARD_REGISTRY_STUDY_COURCE_CONTENT_LIST):
            CARD_REGISTRY_STUDY_COURSE_COLLECTION[
                self.create_study_course_item(
                    index,
                    item,
                    CARD_REGISTRY_STUDY_COURSE_COLLECTION,
                    CARD_REGISTRY_STUDY_COURCE_CONTENT_LIST,
                    lambda: MEDIA_CONTENT.IMAGE.CARD_REGISTRY_WIKI_LOCATION,
                )
            ] = None
        #######################
        POLIBASE_HELP_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "reboot",
                ["перезагрузить сервер Полибейс"],
                [HelpVideoContent(lambda: MEDIA_CONTENT.VIDEO.POLIBASE_RESTART)],
            )
        ]
        POLIBASE_HELP_COLLECTION: dict[CommandNode, None] = {}
        for index, item in enumerate(POLIBASE_HELP_CONTENT_LIST):
            POLIBASE_HELP_COLLECTION[
                self.create_study_course_item(
                    index, item, POLIBASE_HELP_COLLECTION, POLIBASE_HELP_CONTENT_LIST
                )
            ] = None
        #######################
        holter_study_course_help_content_image_list: list[HelpImageContent] = []
        HOLTER_STUDY_COURSE_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "introduce",
                ["Вступительное видео"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_INTRODUCTION, title=""
                    )
                ],
            ),
            HelpContentHolder(
                "nn1",
                ["Внесение данных пациента"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_ADD_PATIENT_TO_VALENTA,
                        title="",
                    )
                ],
            ),
            HelpContentHolder(
                "nn2",
                ["Распечатывание дневника пациента"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_PRINT_PATIENT_JOURNAL,
                        title="",
                    )
                ],
            ),
            HelpContentHolder(
                "nn3",
                ["Установка аппарата Холтера"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_CLEAR_BEFORE_SET,
                        title="Подготовка перед установкой датчиков",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_SETUP_DETECTORS,
                        title="Установка датчиков на тело пациента",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_CONNECT_DETECTORS,
                        title="Подсоединение датчиков к аппарату",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_SETUP_MEMORY,
                        title="Установка карты памяти",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_SETUP_BATTERY,
                        title="Установка аккумулятора",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_TURN_ON,
                        title="Начало обследования Холтера",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_FIX_ON_BODY,
                        title="Закрепление аппарата на теле пациента",
                    ),
                ],
            ),
            HelpContentHolder(
                "nn4",
                [i("Памятка: Установка датчиков, карты и аккумулятора")],
                holter_study_course_help_content_image_list,
            ),
            HelpContentHolder(
                "nn5",
                [i("Памятка: Расположение датчиков на теле пациента")],
                [
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.HOLTER_DETECTORS_MAP, title=""
                    )
                ],
            ),
            HelpContentHolder(
                "nn6",
                ["Снятие аппарата холтера"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_GET_OUT_SD_CARD,
                        title="Снятие карты после окончания обследования",
                    ),
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_BATTERY_CHARGE,
                        title="Зарядка аккумулятора",
                    ),
                ],
            ),
            HelpContentHolder(
                "nn7",
                ["Выгрузка исследования на компьютер"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_LOAD_OUT_DATA, title=""
                    )
                ],
            ),
        ]
        HOLTER_STUDY_COURSE_COLLECTION: dict[CommandNode, None] = {}
        holter_study_course_node: CommandNode = CommandNode(
            ["?holter"],
            ['Обучающий курс "Аппарат Холтера"'],
            lambda: self.study_course_handler(
                None,
                HOLTER_STUDY_COURSE_COLLECTION,
                HOLTER_STUDY_COURSE_CONTENT_LIST,
                lambda: MEDIA_CONTENT.IMAGE.HOLTER_WIKI_LOCATION,
            ),
            text=lambda: f"В данном курсе, {self.user_given_name}, Вы научитесь тому, как работать с аппаратом Холтера:\n\n{A.CT.VISUAL.BULLET} Вносить данные пациента в программу;\n{A.CT.VISUAL.BULLET} Распечатывать журнал пациента;\n{A.CT.VISUAL.BULLET} Надевать датчики на тело пациента;\n{A.CT.VISUAL.BULLET} Снимать датчики;\n{A.CT.VISUAL.BULLET} Выгружать данные исследования на компьютер",
        )
        for index in range(10):
            holter_study_course_help_content_image_list.append(
                HelpImageContent(
                    IndexedLink(MEDIA_CONTENT.IMAGE, "HOLTER_IMAGE_"), title=""
                )
            )
        for index, item in enumerate(HOLTER_STUDY_COURSE_CONTENT_LIST):
            HOLTER_STUDY_COURSE_COLLECTION[
                self.create_study_course_item(
                    index,
                    item,
                    HOLTER_STUDY_COURSE_COLLECTION,
                    HOLTER_STUDY_COURSE_CONTENT_LIST,
                )
            ] = None
        #######################
        reboot_workstation_node: CommandNode = CommandNode(
            ["reboot", "перезагруз^ить"],
            lambda: [
                "перезагрузить компьютер",
                "перезагрузить" + (" компьютер" if self.in_choose_command else ""),
            ],
            self.reboot_workstation_handler,
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        reboot_all_workstations_node: CommandNode = CommandNode(
            reboot_workstation_node.name_list,
            lambda: [
                "перезагрузка всех компьютеров",
                "перезагрузить все" + (" компьютеры" if self.in_choose_command else ""),
            ],
            lambda: self.reboot_workstation_handler(True),
            ADMIN_GROUP,
            filter_function=lambda: self.is_all or self.in_main_menu,
            help_text=lambda: flag_string_represent(Flags.ALL),
        )
        shutdown_workstation_node: CommandNode = CommandNode(
            ["shutdown", "выключ^ить"],
            lambda: [
                "выключение компьютера",
                "выключить" + (" компьютер" if self.is_all else ""),
            ],
            self.shutdown_workstation_handler,
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        shutdown_all_workstations_node: CommandNode = CommandNode(
            shutdown_workstation_node.name_list,
            lambda: [
                "выключение всех компьютеров",
                "выключить все" + (" компьютеры" if self.is_all else ""),
            ],
            lambda: self.shutdown_workstation_handler(True),
            ADMIN_GROUP,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_string_represent(Flags.ALL),
        )
        find_workstation_node: CommandNode = CommandNode(
            self.keywords.command.FIND,
            lambda: [
                "Поиск компьютера",
                "Найти" + (" компьютер" if self.in_choose_command else ""),
            ],
            self.find_workstation_handler,
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        find_all_workstations_node: CommandNode = CommandNode(
            self.keywords.command.FIND,
            lambda: [
                "Весь список компьютеров",
                "Показать весь список компьютеров"
                if self.in_choose_command
                else "Весь список",
            ],
            lambda: self.find_workstation_handler(True),
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_string_represent(Flags.ALL),
        )
        msg_to_node: CommandNode = CommandNode(
            ["msg", "сообщение", "message"],
            lambda: [
                "Отправка сообщения пользователю",
                "Отправить сообщение"
                + (" пользователю" if self.in_choose_command else ""),
            ],
            lambda: self.workstation_message_send_handler(False),
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all,
        )
        msg_to_all_node: CommandNode = CommandNode(
            msg_to_node.name_list,
            [
                "Отправка сообщения всем пользователям",
                "Отправить сообщение всем пользователям",
            ],
            lambda: self.workstation_message_send_handler(True),
            ADMIN_GROUP,
            filter_function=lambda: self.is_all and not self.in_main_menu,
        )
        check_ws_node: CommandNode = CommandNode(
            self.keywords.command.CHECK,
            lambda: [
                "Список отслеживаемых компьютеров",
                ("Проверить " if self.in_choose_command else "")
                + "отслеживаемые компьютеры на доступность",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.WS], False
            ),
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        check_ws_all_node: CommandNode = CommandNode(
            self.keywords.command.CHECK,
            lambda: [
                "Проверить все компьютеры на доступность",
                "все компьютеры на доступность",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.WS], True
            ),
            ADMIN_GROUP,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_string_represent(Flags.ALL),
        )
        process_kill_node: CommandNode = CommandNode(
            ["kill", "завершить"],
            ["Завершение процесса", "Завершить процесс"],
            lambda: self.console_apps_api.process_kill(self.arg(), self.arg(1)),
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        disks_report_node: CommandNode = CommandNode(
            ["disk^s", "диски"],
            ["Показать информацию о дисках"],
            lambda: self.console_apps_api.disks_report(self.arg()),
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        self.menu.workstation = [
            reboot_workstation_node,
            reboot_all_workstations_node,
            shutdown_workstation_node,
            shutdown_all_workstations_node,
            process_kill_node,
            find_workstation_node,
            find_all_workstations_node,
            msg_to_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщения компьютеру",
                    "Отправить сообщение"
                    + (" компьютеру" if self.in_choose_command else ""),
                ],
                filter_function=lambda: self.is_not_all or self.in_main_menu,
            ),
            msg_to_all_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщения всем компьютерам",
                    "Отправить сообщение всем"
                    + (" компьютерам" if self.in_choose_command else ""),
                ],
                filter_function=lambda: self.is_all,
            ),
            disks_report_node,
            check_ws_node.clone_as(
                None,
                lambda: [
                    "Проверка отслеживаемых компьютеров на доступность",
                    "Проверить отслеживаемыe компьютеры на доступность"
                    if self.in_choose_command
                    else "Проверить отслеживаемыe на доступность",
                ],
            ),
            check_ws_all_node.clone_as(
                None,
                lambda: [
                    "Проверка всех компьютеров на доступность ",
                    "Проверить все "
                    + ("компьютеры " if self.in_choose_command else "")
                    + "на доступность",
                ],
            ),
        ]

        #
        create_note_node: CommandNode = CommandNode(
            self.keywords.command.CREATE,
            lambda: [
                "Создание заметки",
                "Создать" + (" заметку" if self.in_choose_command else ""),
            ],
            self.create_note_handler,
            filter_function=lambda: self.is_not_all or self.in_choose_command,
        )
        add_journal_record_node: CommandNode = CommandNode(
            self.keywords.command.CREATE,
            self.get_journal_add_record_title,
            self.add_journal_record_handler,
            filter_function=lambda: self.is_not_all or self.in_choose_command,
        )
        show_journal_node: CommandNode = CommandNode(
            self.keywords.command.FIND,
            lambda: [
                "Записи в журнале",
                "Показать журнал",
            ],
            self.show_journal_handler,
            filter_function=lambda: self.is_not_all or self.in_choose_command,
        )
        self.show_note_node: CommandNode = CommandNode(
            self.keywords.command.FIND,
            lambda: [
                "Поиск заметки",
                "Найти" + (" заметку" if self.in_choose_command else ""),
            ],
            lambda: self.find_note_handler(False, False),
            filter_function=lambda: self.is_not_all or self.in_choose_command,
            help_text=lambda: js((" (", i("Название заметки"), ")")),
        )
        self.show_all_note_node: CommandNode = CommandNode(
            ["show", "показать"],
            lambda: [
                "",
                "Показать все" + (" заметки" if self.in_choose_command else ""),
            ],
            lambda: self.find_note_handler(False, True),
            help_text=lambda: flag_string_represent(Flags.ALL),
        )
        self.menu.notes = [
            create_note_node,
            self.show_note_node,
            self.show_all_note_node,
        ]
        self.menu.journals = [add_journal_record_node, show_journal_node]
        #######################
        call_centre_unit_node: CommandNode = CommandNode(
            ["callcentre", "колл-центр"],
            ["Колл-центр"],
            lambda: self.menu_handler(self.menu.call_centre),
            text=f"Алло, алло... С этих слов начинается общение наших клиентов c колцентром. Работники коллцентра принимают звонки и работают с запросами от клиентов и в этом им помогает:\n\n{A.CT.VISUAL.BULLET} программа *Инфинити*, отвечающая за звонки\n{A.CT.VISUAL.BULLET} программа *Полибейс*, в которой заноситься информация о клиенте\n{A.CT.VISUAL.BULLET} браузер *Google Chrome*, с набором ресурсов\n\nНиже представлены курсы по всем трем программам.",
        )
        it_unit_node: CommandNode = CommandNode(
            ["it", "ит"],
            ["ИТ отдел"],
            lambda: self.menu_handler(self.menu.it),
            text=self.get_it_telephone_number_text,
        )
        time_tracking_report_node: CommandNode = CommandNode(
            ["tt", "урв"], ["учёт рабочего времени"], self.time_tracking_report_handler
        )
        my_time_tracking_report_node: CommandNode = CommandNode(
            ["my_tt", "мой_урв"],
            ["Мои отметки ухода и прихода"],
            lambda: self.time_tracking_report_handler(True),
        )
        marketer_statistics: CommandNode = CommandNode(
            ["statistics", "статистика"],
            ["Статистика по отзывам"],
            self.marketer_statistics_handler,
        )
        self.menu.hr_unit = [my_time_tracking_report_node]
        self.menu.marketer_unit = [marketer_statistics]
        hr_unit_node: CommandNode = CommandNode(
            ["hr", "кадр^ов"],
            ["Отдел кадров"],
            lambda: self.menu_handler(self.menu.hr_unit),
            text=lambda: j(
                (
                    "Руководитель: ",
                    b(
                        one(
                            A.R.filter(
                                lambda item: not item.samAccountName.startswith(
                                    A.CT_AD.TEMPLATED_USER_SERACH_TEMPLATE[0]
                                )
                                and not item.samAccountName.endswith(
                                    A.CT_AD.TEMPLATED_USER_SERACH_TEMPLATE[-1]
                                ),
                                A.R_U.by_job_position(A.CT_AD.JobPositions.HR),
                            )
                        ).name
                    ),
                    nl("."),
                    "Телефон: ",
                    b("706"),
                    ".",
                )
            ),
        )
        marketer_unit_node: CommandNode = CommandNode(
            ["marketing", "маркет^олог", "marketer"],
            ["Отдел маркетинга"],
            lambda: self.menu_handler(self.menu.marketer_unit),
            text=lambda: j(
                (
                    "Руководитель: ",
                    b(one(A.R_U.by_job_position(A.CT_AD.JobPositions.MARKETER)).name),
                    ".",
                )
            ),
        )
        self.menu.unit = [
            it_unit_node,
            call_centre_unit_node,
            hr_unit_node,
            marketer_unit_node,
        ]
        #######################
        robocopy_node: CommandNode = CommandNode(
            ["rb^k", "robocopy"],
            ["Запуск Robocopy-задания"],
            self.robocopy_job_run_handler,
        )
        polibase_backup_node: CommandNode = CommandNode(
            ["pb^k"],
            [
                "Создание бекапа базы данных Polibase",
                "Создать бекап базы данных Polibase",
            ],
            self.create_polibase_db_backup_handler,
        )
        self.menu.backup = [robocopy_node, polibase_backup_node]

        #######################
        polibase_person_information_node: CommandNode = CommandNode(
            ["info^rmation", "инфо^рмация"],
            lambda: [
                "Информация о пациенте",
                "Информация" + (" о пациенте" if self.in_choose_command else ""),
            ],
            self.polibase_person_show_information_handler,
        )
        polibase_doctor_visits_node: CommandNode = CommandNode(
            ["visit^s", "приём^ы", "визит^ы", "прием^ы"],
            lambda: ["Список моих приёмов", "Показать список моих приёмов"],
            self.polibase_visit_handler,
            filter_function=lambda: self.am_i_doctor,
        )
        polibase_person_find_card_registry_or_folder_node: CommandNode = CommandNode(
            self.keywords.command.FIND,
            lambda: [
                "Поиск карты пациента или папки",
                "Найти карту"
                + (" пациента" if self.in_choose_command else "")
                + " или папку",
            ],
            self.polibase_person_card_registry_folder_find_handler,
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )

        check_email_node: CommandNode = CommandNode(
            ["email", "почт^ы", "mail"],
            lambda: [
                "Проверка адресса электронной почты",
                "Проверить адресс электронной почты"
                if self.in_choose_command
                else "Адресса электронной почты",
            ],
            lambda: self.check_email_address_handler(),
        )

        check_valenta_node: CommandNode = CommandNode(
            ["valenta", "валент^у"],
            lambda: [
                "Проверка наличия новых исследований в Валенте",
                j(
                    (
                        "Проверить наличие новых исследований в Валенте"
                        if self.in_choose_command
                        else "",
                        "наличия новых исследований в Валенте",
                    )
                ),
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.VALENTA]
            ),
        )

        check_printers_node: CommandNode = CommandNode(
            ["printer^s", "принтер^ы"],
            lambda: [
                "Проверка принтеров",
                "Проверить принтеры" if self.in_choose_command else "Принтеров",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.PRINTERS]
            ),
        )

        check_material_resources_node: CommandNode = CommandNode(
            ["material^ resources", "материал^ьные ресурсы"],
            lambda: [
                "Проверка материальных ресурсов",
                "Проверить материальные ресурсы"
                if self.in_choose_command
                else "Материальных ресурсов",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.MATERIALIZED_RESOURCES]
            ),
        )

        check_timestamp_node: CommandNode = CommandNode(
            ["timestamp"],
            lambda: [
                "Проверка временных меток",
                "Проверить временные метки"
                if self.in_choose_command
                else "Временных меток",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.TIMESTAMPS]
            ),
        )

        check_email_node_polibase_person_node: CommandNode = check_email_node.clone_as(
            None,
            [
                "Проверка адресса электронной почты пациента",
                "Проверить адресс электронной почты пациента",
            ],
            lambda: self.check_email_address_handler(only_for_polibase_person=True),
        )

        joke_node: CommandNode = CommandNode(
            COMMAND_KEYWORDS.JOKE,
            ["Анекдот"],
            lambda: self.get_joke_handler(),
            wait_for_input=False,
            settings_handler=lambda: self.get_joke_handler(True),
        )

        self.menu.polibase_person = [
            polibase_person_information_node,
            polibase_person_find_card_registry_or_folder_node.clone_as(
                title_and_label=lambda: [
                    "Поиск карты пациента",
                    "Найти карту" + (" пациента" if self.in_choose_command else ""),
                ],
            ),
            check_email_node_polibase_person_node,
        ]
        #######################
        self.menu.polibase_doctor = [
            polibase_doctor_visits_node,
        ]
        #######################
        create_user_node: CommandNode = CommandNode(
            self.keywords.command.CREATE,
            lambda: [
                "Создание",
                j(("Создать", (" пользователя" if self.in_choose_command else ""))),
            ],
            self.create_user_handler,
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all,
        )
        find_user_node: CommandNode = CommandNode(
            self.keywords.command.FIND,
            lambda: [
                "Поиск пользователя",
                j(("Найти", (" пользователя" if self.in_choose_command else ""))),
            ],
            self.user_find_handler,
            filter_function=lambda: self.is_not_all or self.in_choose_command,
        )
        change_user_telephone_number_node: CommandNode = CommandNode(
            ["phone", "телефон^е"],
            lambda: [
                "Изменение телефонного номера пользователя",
                j(
                    (
                        "Изменить телефонный номер",
                        (" пользователя" if self.in_main_menu else ""),
                    )
                ),
            ],
            lambda: self.user_property_set_handler(0),
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all or self.in_choose_command,
        )
        change_all_user_telephone_number_node: CommandNode = CommandNode(
            ["phone", "телефон^е"],
            lambda: [
                "Редактирование всех телефонных номеров",
                j(
                    (
                        "Изменить все телефонные номера",
                        (" пользователей" if self.in_choose_command else ""),
                    )
                ),
            ],
            lambda: self.user_property_set_handler(0),
            ADMIN_GROUP,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_string_represent(Flags.ALL),
        )
        change_user_password_node: CommandNode = CommandNode(
            self.keywords.command.PASSWORD,
            lambda: [
                "Изменение пароля пользователя",
                j(
                    (
                        "Изменить пароль",
                        (" пользователя" if self.in_choose_command else ""),
                    )
                ),
            ],
            lambda: self.user_property_set_handler(1),
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all or self.in_all_commands,
        )
        change_user_status_node: CommandNode = CommandNode(
            ["status", "статус"],
            lambda: [
                "Изменение статуса пользователя",
                "Изменить статус" + (" пользователя" if self.in_choose_command else ""),
            ],
            lambda: self.user_property_set_handler(2),
            ADMIN_GROUP,
            filter_function=lambda: self.is_not_all,
        )
        self.menu.user = [
            create_user_node,
            find_user_node,
            change_user_telephone_number_node,
            change_all_user_telephone_number_node,
            change_user_password_node,
            change_user_status_node,
            msg_to_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщение пользователю",
                    "Отправить сообщение" + (" пользователю" if self.is_all else ""),
                ],
                filter_function=lambda: self.is_not_all or self.in_main_menu,
            ),
            msg_to_all_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщения всем",
                    "Отправить сообщение всем"
                    + (" пользователям" if self.is_all else ""),
                ],
                filter_function=lambda: self.is_all,
            ),
        ]
        #######################

        self.run_command_node: CommandNode = CommandNode(
            self.keywords.command.RUN,
            ["Запуск", "Запуск скрипта"],
            lambda: self.run_command_handler()
            if self.check_for_arg_list_include_file
            else self.menu_handler(self.menu.run_command),
        )
        self.menu.run_command = [
            CommandNode(
                A.D.get(A.CT_CMDT.CMD)[1:],
                self.get_run_title_and_label(A.CT_CMDT.CMD),
                lambda: self.run_command_handler(A.CT_CMDT.CMD),
            ),
            CommandNode(
                A.D.get(A.CT_CMDT.POLIBASE)[1:],
                self.get_run_title_and_label(A.CT_CMDT.POLIBASE),
                lambda: self.run_command_handler(A.CT_CMDT.POLIBASE),
            ),
            CommandNode(
                A.D.get(A.CT_CMDT.DATA_SOURCE)[1:],
                self.get_run_title_and_label(A.CT_CMDT.DATA_SOURCE),
                lambda: self.run_command_handler(A.CT_CMDT.DATA_SOURCE),
            ),
            CommandNode(
                A.D.get(A.CT_CMDT.PYTHON)[1:],
                self.get_run_title_and_label(A.CT_CMDT.PYTHON),
                lambda: self.run_command_handler(A.CT_CMDT.PYTHON),
            ),
            CommandNode(
                A.D.get(A.CT_CMDT.SSH)[1:],
                self.get_run_title_and_label(A.CT_CMDT.SSH),
                lambda: self.run_command_handler(A.CT_CMDT.SSH),
            ),
        ]
        #######################
        check_resources_node: CommandNode = CommandNode(
            ["resource^s", "ресурс^ы"],
            lambda: [
                "Проверка основных ресурсов",
                "Проверить основные ресурсы"
                if self.in_choose_command
                else "основных ресурсов",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.RESOURCES]
            ),
            ADMIN_GROUP + [Groups.RD, Groups.IndicationWatcher],
        )
        check_indications_node: CommandNode = CommandNode(
            ["indication^s", "показан^ия"],
            lambda: [
                "Проверка показаний отделения лучевой диагностики",
                "Проверить показания отделения лучевой диагностики"
                if self.in_choose_command
                else "Показаний отделения лучевой диагностики",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.INDICATIONS]
            ),
            ADMIN_GROUP + [Groups.RD, Groups.IndicationWatcher],
        )
        check_backups_node: CommandNode = CommandNode(
            ["backup^s", "бекап^ы", "rbk"],
            lambda: [
                "Список Robocopy-заданий",
                "Проверить Robocopy-задания"
                if self.in_choose_command
                else "Robocopy-заданий",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.BACKUPS]
            ),
            ADMIN_GROUP,
        )
        check_polibase_database_dump_node: CommandNode = CommandNode(
            ["polibase"],
            lambda: [
                "Проверка дампа базы данных Polibase",
                "Проверить дамп базы данных Polibase"
                if self.in_choose_command
                else "Дампа базы данных Polibase",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.POLIBASE]
            ),
            ADMIN_GROUP,
        )
        check_scanned_document_node: CommandNode = CommandNode(
            COMMAND_KEYWORDS.SCAN,
            lambda: [
                "Проверка отсканированого документа",
                "Проверить отсканированный документ"
                if self.in_choose_command
                else "Отсканированого документа",
            ],
            self.check_scanned_document_handler,
            # filter_function=lambda: not self.argless,
        )
        check_disks_node: CommandNode = CommandNode(
            ["disk^s", "диск^и"],
            lambda: [
                "Проверка свободного места на всех наблюдаемых дисках",
                "Проверить свободное места на всех наблюдаемых дисках"
                if self.in_choose_command
                else "свободного места на всех наблюдаемых дисках",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.DISKS]
            ),
            ADMIN_GROUP,
        )
        check_all_node: CommandNode = self.create_command_link(
            [""],
            js((self.keywords.command.CHECK[0], FLAG_KEYWORDS.ALL_SYMBOL)),
            lambda: [
                None,
                "Проверить все компоненты"
                if self.in_choose_command
                else "Всех компонентов",
            ],
            None,
            True,
        )
        check_all_node.help_text = lambda: flag_string_represent(Flags.ALL)
        #######################
        polibase_restart_node: CommandNode = CommandNode(
            ["restart", "перезагруз^ить"],
            A.D.map(
                lambda item: js((item, "Polibase")), ["Перезагрузка сервера", "Перезагрузить сервер"]
            ),
            self.console_apps_api.polibase_restart,
            ADMIN_GROUP,
        )
        polibase_show_password_node: CommandNode = CommandNode(
            self.keywords.command.PASSWORD,
            lambda: [
                "Пароль пользователя Полибейс",
                j(
                    (
                        "Показать пароль пользователя",
                        " Полибейс"
                        if self.none_command or self.in_all_commands
                        else "",
                    )
                ),
            ]
            if self.am_i_admin
            else [
                "Мой пароль Полибейс",
                j(("Показать мой пароль", " Полибейс" if self.none_command else "")),
            ],
            self.show_polibase_password_handler,
        )
        polibase_close_node: CommandNode = CommandNode(
            ["close", "закрыть"],
            lambda: [
                "Закрытие клиентской программы Polibase",
                js(
                    (
                        "Закрыть клиентскую программу",
                        "Polibase" if self.in_main_menu else None,
                    )
                ),
            ],
            lambda: self.console_apps_api.polibase_client_program_close(self.arg()),
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )
        all_polibase_close_node: CommandNode = CommandNode(
            ["close", "закрыть"],
            lambda: [
                "Закрытие всех клиентских программ",
                js(
                    (
                        "Закрыть все клиентские программы",
                        "Polibase" if self.in_choose_command else None,
                    )
                ),
            ],
            lambda: self.console_apps_api.polibase_client_program_close(
                self.arg(), True
            ),
            filter_function=lambda: self.is_all or self.in_main_menu,
        )
        self.menu.polibase = [
            polibase_restart_node,
            polibase_close_node,
            all_polibase_close_node,
            polibase_show_password_node,
        ]

        def get_polibase_person_card_registry_folder_name() -> str:
            arg: str = self.arg(default_value="")
            return (
                ""
                if e(arg) or not A.C_P.person_card_registry_folder(arg)
                else j((" ", esc(A.D_F.polibase_person_card_registry_folder(arg))))
            )

        #######################
        infinity_study_course_node: CommandNode = CommandNode(
            ["?infinity", "?инфинити"],
            ['Обучающий курс "Регистартор и Оператор колл-центра: инфинити"'],
            lambda: self.study_course_handler(
                None,
                INFINITY_STUDY_COURSE_COLLECTION,
                INFINITY_STUDY_COURCE_CONTENT_LIST,
                lambda: MEDIA_CONTENT.IMAGE.INFINITY_WIKI_LOCATION,
            ),
        )
        basic_polibase_study_course_node: CommandNode = CommandNode(
            ["?polibase"],
            ['Обучающий курс "Полибейс - базовый уровень"'],
            self.under_construction_handler,
        )
        callcentre_browser_study_course_node: CommandNode = CommandNode(
            ["?callcentre"],
            [
                'Обучающий курс "Регистратор и Оператор колл-центра: браузер Google Chrome"'
            ],
            lambda: self.study_course_handler(
                None,
                CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION,
                CALLCENTRE_BROWSER_STUDY_CONTENT_LIST,
            ),
            text="Браузер *Google Chrome* - это инструмент для работы регистратора и оператора колл-центра. При входе в общий аккаунт будут доступны все нужные ресурсы!",
        )
        #######################
        polibase_person_card_registry_folder_qr_code_create_node: CommandNode = (
            CommandNode(
                ["qr"],
                lambda: [
                    j(
                        (
                            "Создание QR-кода для папки карт пациентов",
                            get_polibase_person_card_registry_folder_name(),
                        )
                    ),
                    j(
                        (
                            "Создать QR-код для папки карт пациентов",
                            get_polibase_person_card_registry_folder_name(),
                        )
                    ),
                ],
                self.create_qr_code_for_card_registry_folder_handler,
                ADMIN_GROUP + [Groups.CardRegistry],
                filter_function=lambda: (
                    self.argless and (self.is_not_all or self.in_main_menu)
                )
                or (
                    not self.argless
                    and self.is_not_all
                    and self.is_person_card_registry_folder
                ),
            )
        )

        polibase_persons_by_card_registry_folder_name_node: CommandNode = CommandNode(
            flag_name_list(Flags.ALL, True),
            lambda: [
                j(
                    (
                        "Список карт пациентов в папке",
                        get_polibase_person_card_registry_folder_name(),
                    )
                )
            ],
            self.polibase_persons_by_card_registry_folder_handler,
            filter_function=lambda: self.argless or self.is_person_card_registry_folder,
        )

        def polibase_person_add_to_card_registry_folder_title_and_label() -> list[str]:
            value: str = j(
                ("пациента в папку", get_polibase_person_card_registry_folder_name())
            )
            return [js(("Добавление карты", value)), js(("Добавить карту", value))]

        self.polibase_person_card_add_to_card_registry_folder_node: CommandNode = CommandNode(
            self.keywords.command.ADD,
            polibase_person_add_to_card_registry_folder_title_and_label,
            self.add_polibase_person_to_card_registry_folder_handler,
            ADMIN_GROUP + [Groups.CardRegistry],
            text="Добавляет карту пациента в папку реестра",
            help_text=lambda: f" {i('название папки')} {i('запрос для поиска пациента')}.\nНапример, {self.current_pih_keyword} + п1к {A.CT.TEST.PIN}",
            filter_function=lambda: self.is_not_all or self.in_main_menu,
        )

        def polibase_person_card_registry_folder_register_title_and_label() -> (
            list[str]
        ):
            value: str = get_polibase_person_card_registry_folder_name()
            return [
                j(("Регистрация папки", value, " в реестре карт")),
                j(
                    (
                        "Зарегистрировать папку",
                        value,
                        " в реестре карт" if self.in_choose_command else "",
                    )
                ),
            ]

        polibase_person_card_registry_folder_register_node: CommandNode = CommandNode(
            ["register"],
            polibase_person_card_registry_folder_register_title_and_label,
            self.register_card_registry_folder_handler,
            ADMIN_GROUP,
            filter_function=lambda: (
                self.argless and (self.is_not_all or self.in_main_menu)
            )
            or (
                self.is_not_all
                and not self.argless
                and self.is_person_card_registry_folder
                and (
                    self.is_forced or not self.is_person_card_registry_folder_registered
                )
            ),
        )

        polibase_person_card_registry_folder_statistics_node: CommandNode = CommandNode(
            ["statistics", "статистика"],
            lambda: [
                "Статистика реестра карт",
                "Статистика" + (" реестра карт" if self.in_choose_command else ""),
            ],
            self.get_card_registry_statistics_handler,
            ADMIN_GROUP,
            filter_function=lambda: self.argless
            and (self.is_not_all or self.in_main_menu),
        )

        self.menu.card_registry = [
            polibase_persons_by_card_registry_folder_name_node,
            self.polibase_person_card_add_to_card_registry_folder_node,
            polibase_person_find_card_registry_or_folder_node,
            polibase_person_card_registry_folder_qr_code_create_node,
            polibase_person_card_registry_folder_register_node,
            polibase_person_card_registry_folder_statistics_node,
        ]
        #######################
        WIKI_BASE_CONTENT_LIST: list[HelpImageContent] = [
            HelpImageContent(
                lambda: MEDIA_CONTENT.IMAGE.WIKI_ICON,
                f"Пройти обучение можно на нашем внутреннем сайте: *Wiki*. Ниже покажем Вам, {self.user_given_name}, как зайти на этот сайт.\n\n_*Обратите внимание*, что доступ к данному сайту возможен только с *компьютера* рабочего места пользователя!_",
                "Найдите на *Рабочем столе* иконку с названием *Wiki* и откройте ее",
                False,
            ),
            HelpImageContent(
                lambda: MEDIA_CONTENT.IMAGE.WIKI_GET_ACCESS,
                None,
                f'Если видите это, нажмите на кнопку *"Перейти на сайт"*',
                False,
            ),
        ]
        #######################
        STUDY_WIKI_CONTENT_HOLDER_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "study_wiki_location", ["Обучение в Вики"], WIKI_BASE_CONTENT_LIST
            )
        ]
        STUDY_WIKI_LOCATION_COLLECTION: dict[CommandNode, None] = {}
        self.study_wiki_location_node = self.create_study_course_item(
            -1,
            STUDY_WIKI_CONTENT_HOLDER_LIST[0],
            STUDY_WIKI_LOCATION_COLLECTION,
            STUDY_WIKI_CONTENT_HOLDER_LIST,
        )
        STUDY_WIKI_LOCATION_COLLECTION[self.study_wiki_location_node] = None
        #######################
        WIKI_CONTENT_HOLDER: HelpContentHolder = HelpContentHolder(
            "wiki",
            ["Наша Вики", "Наша Вики - источник знаний!"],
            WIKI_BASE_CONTENT_LIST
            + [
                HelpImageContent(
                    lambda: MEDIA_CONTENT.IMAGE.WIKI_PAGE,
                    None,
                    f"Откроется браузер и отобразится страница.\n\n_{b('Важное дополнение')}: получить доступ к сайту можно, введя в адресной строке браузера текст: "
                    + b(A.CT_ADDR.WIKI_SITE_ADDRESS)
                    + "_",
                    False,
                )
            ],
        )
        IT_HELP_CONTENT_HOLDER_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "request_help",
                ["Как создать запрос на помощь"],
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.IT_CREATE_HELP_REQUEST,
                        'Для создания задачи, вам понадобится программа "Полибейс". А как создать задачу - посмотрите видео ниже:',
                    )
                ],
            ),
            WIKI_CONTENT_HOLDER,
        ]
        print_node: CommandNode = CommandNode(
            ["print", "печать"], ["Распечатать картинку"], self.print_handler
        )
        ####
        self.about_it_node: CommandNode = CommandNode(
            ["about"], ["О ИТ отделе"], self.about_it_handler
        )
        IT_HELP_COLLECTION: dict[CommandNode, None] = {}
        self.menu.it_help = []
        for index, item in enumerate(IT_HELP_CONTENT_HOLDER_LIST):
            self.menu.it_help.append(
                self.create_study_course_item(
                    -1, item, IT_HELP_COLLECTION, IT_HELP_CONTENT_HOLDER_LIST
                )
            )
            IT_HELP_COLLECTION[self.menu.it_help[index]] = None
        self.menu.it = [
            self.about_it_node,
            self.create_command_link(
                [""],
                js(
                    (
                        self.keywords.command.POLIBASE[0],
                        self.keywords.command.PASSWORD[0],
                    )
                ),
                ["Мой пароль Полибейс", "Показать мой пароль Полибейс"],
            ),
            self.study_node.clone_as(title_and_label=["Обучение"]),
        ]
        self.menu.it += self.menu.it_help
        self.wiki_node = self.menu.it_help[-1]
        self.wiki_node.show_always = True
        #######################
        self.menu.call_centre = [
            infinity_study_course_node,
            callcentre_browser_study_course_node,
            self.wiki_node,
        ]

        self.main_menu_node: CommandNode = CommandNode(
            ["menu", "меню"],
            ["Меню"],
            self.main_menu_handler,
            text=lambda: nl(
                b("Все команды:") if self.is_all else b("Список разделов:")
            ),
        )
        #######################
        self.address_node: CommandNode = self.create_command_link(
            j(("to", FLAG_KEYWORDS.ADDRESS_SYMBOL), "|"),
            FLAG_KEYWORDS.ADDRESS_SYMBOL,
            i("Адресовать команду"),
            ADMIN_GROUP,
            True,
        )
        self.address_node.order = 2
        #######################
        self.address_as_link_node: CommandNode = self.create_command_link(
            j(("link", FLAG_KEYWORDS.LINK_SYMBOL), "|"),
            FLAG_KEYWORDS.LINK_SYMBOL,
            i("Адресовать ссылку на команду"),
            ADMIN_GROUP,
            True,
        )
        self.address_as_link_node.order = 3
        #######################
        self.all_commands_node: CommandNode = self.create_command_link(
            j((COMMAND_LINK_SYMBOL, j((flag_string_represent(Flags.ALL, True))))),
            FLAG_KEYWORDS.ALL_SYMBOL,
            [i("Все команды")],
            None,
            True,
        )
        self.all_commands_node.order = 1
        self.all_commands_node.filter_function = lambda: not self.in_choose_command

        about_pih_node: CommandNode = CommandNode(
            ["about", "o"],
            [i("О PIH")],
            text_decoration_after=lambda: ""
            if not self.in_main_menu or self.has_help
            else nl("...", reversed=True),
            text=lambda: j(
                (
                    nl(
                        "Я бот-помощник для решения Ваших задач. Моё имя составлено из первых букв нашей организации:"
                    ),
                    "   ",
                    A.CT_V.BULLET,
                    " ",
                    b("P"),
                    " acific ",
                    b("I"),
                    " nternational ",
                    b("H"),
                    nl(" ospital "),
                    nl("или"),
                    "   ",
                    A.CT_V.BULLET,
                    " ",
                    b("П"),
                    " асифик ",
                    b("И"),
                    " нтернейшнл ",
                    b("Х"),
                    nl(" оспитал.", count=2),
                    b("Автор: "),
                    nl("Караченцев Никита Александрович"),
                    b("Версия: "),
                    nl(b(VERSION)),
                    b("Сервер: "),
                    A.OS.host(),
                )
            ),
            show_in_main_menu=True,
            wait_for_input=False,
            show_always=True,
            order=4,
        )
        self.exit_node: CommandNode = CommandNode(
            self.keywords.command.EXIT,
            [None, i(A.D.capitalize(self.keywords.command.EXIT[1]))],
            self.session.exit,
            text_decoration_after=lambda: ""
            if self.in_main_menu and not self.has_help
            else nl("...", reversed=True),
            wait_for_input=False,
            filter_function=lambda: not self.in_all_commands,
        )
        self.exit_node.order = 0
        self.exit_node_for_menu: CommandNode = CommandNode(
            self.exit_node.name_list,
            self.exit_node.title_and_label,
            self.exit_node.handler,
            wait_for_input=False,
        )
        #######################
        self.ws_node: CommandNode = CommandNode(
            ["ws", "комп^ьютер"],
            ["Компьютер"],
            lambda: self.menu_handler(self.menu.workstation),
            text_decoration_before="🖥️ ",
            show_in_main_menu=True,
            help_text=lambda: flag_string_represent(Flags.ALL) if self.is_all else "",
            text="Наши компьютеры",
        )
        self.menu.check = [
            check_all_node,
            check_resources_node,
            check_ws_node.clone_as(
                self.ws_node.name_list,
                lambda: [
                    "Проверка отслеживаемых компьютеров на доступность",
                    "Проверить отслеживаемые компьютеры на доступность"
                    if self.in_choose_command
                    else "отслеживаемых компьютеров на доступность",
                ],
            ),
            check_disks_node,
            check_indications_node,
            check_backups_node,
            check_polibase_database_dump_node,
            check_scanned_document_node,
            check_email_node,
            check_valenta_node,
            check_printers_node,
            check_material_resources_node,
            check_timestamp_node,
        ]
        self.user_node: CommandNode = CommandNode(
            COMMAND_KEYWORDS.USER,
            ["Пользователь"],
            lambda: self.menu_handler(self.menu.user),
            text_decoration_before="👤 ",
            show_in_main_menu=True,
            text="Наши пользователи",
        )
        patient_node: CommandNode = CommandNode(
            COMMAND_KEYWORDS.PATIENT,
            ["Пациент"],
            lambda: self.menu_handler(self.menu.polibase_person),
            text_decoration_before="🤒 ",
            show_in_main_menu=True,
            text="Наши пациенты",
        )
        doctor_node: CommandNode = CommandNode(
            COMMAND_KEYWORDS.DOCTOR,
            ["Доктор"],
            lambda: self.menu_handler(self.menu.polibase_doctor),
            text_decoration_before="🧑🏼‍⚕️ ",
            show_in_main_menu=True,
            text="Наши доктора",
            filter_function=lambda: self.am_i_doctor and self.argless,
        )
        check_node: CommandNode = CommandNode(
            self.keywords.command.CHECK,
            lambda: ["Проверка всех компонентов системы"]
            if self.is_all
            else ["Проверка", "Проверить"],
            lambda: self.check_resources_and_indications_handler(None, self.is_all)
            if self.is_all
            else self.menu_handler(self.menu.check),
            ADMIN_GROUP + [Groups.RD, Groups.IndicationWatcher],
            text_decoration_before="☑️ ",
            show_in_main_menu=True,
        )
        polibase_node: CommandNode = CommandNode(
            self.keywords.command.POLIBASE,
            lambda: [js(("Полибейс", MobileHelper.polibase_status())), "Полибейс"],
            lambda: self.menu_handler(self.menu.polibase),
            text_decoration_before=lambda: js((MobileHelper.polibase_status())),
            show_in_main_menu=True,
            text=j(
                (
                    nl("Медицинская информационая система"),
                    "Разработчик: ",
                    b("Жданов Олег Николаевич"),
                )
            ),
        )
        help_node: CommandNode = CommandNode(
            ["help", "помощь"], [js(("Помощь", A.CT.VISUAL.ARROW))]
        )

        def get_note_title() -> list[str]:
            value: str | None = self.arg()
            if e(value):
                return ["Все заметки" if self.is_all else "Заметки"]
            gkeep_item: GKeepItem | None = one(
                A.R_N.find_gkeep_item(value, value, self.is_not_all)
            )
            if e(gkeep_item):
                return [j(("Поиск заметки", ' "', value, '"'))]
            else:
                return [j(("Заметка", ' "', gkeep_item.title, '"'))]

        self.note_node: CommandNode = CommandNode(
            self.keywords.command.NOTES,
            get_note_title,
            lambda: self.find_note_handler(True)
            if self.arg_len == 1
            else self.menu_handler(self.menu.notes),
            text_decoration_before="📝 ",
            show_in_main_menu=True,
            filter_function=lambda: self.argless
            or A.C_N.exists(self.arg(), self.arg(), False),
            help_text=lambda: js((" (", i("Название заметки"), ")")),
        )

        self.journal_node: CommandNode = CommandNode(
            self.keywords.command.JOURNALS,
            self.get_journal_title,
            lambda: self.show_journal_handler()
            if self.arg_len == 1
            else self.menu_handler(self.menu.journals),
            text_decoration_before="📖 ",
            show_in_main_menu=True,
            filter_function=lambda: self.argless
            or A.C_J.exists(self.arg(), self.arg()),
        )

        all_passwords_node: CommandNode = self.create_command_link(
            change_user_password_node.name_list,
            js(
                (
                    command_name_base(self.note_node.name_list[0]),
                    flag_name_list(Flags.SILENCE)[0],
                    esc("password"),
                )
            ),
            ["Список всех паролей"],
            ADMIN_GROUP,
        )
        all_passwords_node.help_text = lambda: flag_string_represent(Flags.ALL)
        self.execute_file_silence("@on_before_command_node_tree_creation")

        #######################
        self.command_node_tree = {
            CommandNode(
                ["where", "где"],
                lambda: [
                    "Где? 🫴",
                ],
                self.where_handler,
                filter_function=lambda: self.is_not_all or self.in_main_menu,
            ): None,
            CommandNode(
                ["who", "кто"],
                lambda: [
                    "Кто? ☝️",
                ],
                self.who_handler,
                filter_function=lambda: self.is_not_all or self.in_main_menu,
            ): None,
            joke_node: None,
            CommandNode(["test"], handler=self.test_handler): None,
            CommandNode(["mri_log"], ["МРТ лог"], self.add_mri_log_handler): None,
            print_node: None,
            msg_to_node: None,
            self.exit_node: None,
            msg_to_all_node: None,
            self.all_commands_node: None,
            about_pih_node: None,
            self.study_node: None,
            self.main_menu_node: None,
            self.user_node: None,
            self.run_command_node: None,
            CommandNode(self.run_command_node.name_list, [""]): A.D.to_dict(
                self.menu.run_command
            ),
            CommandNode(self.user_node.name_list, [""]): A.D.to_dict(self.menu.user),
            self.ws_node: None,
            CommandNode(["ws", "комп^ьютер"], [""]): A.D.to_dict(self.menu.workstation),
            CommandNode(["study", "обучение"], [""]): {
                self.wiki_node: None,
                infinity_study_course_node: None,
                basic_polibase_study_course_node: None,
                holter_study_course_node: None,
                callcentre_browser_study_course_node: None,
            },
            CommandNode(
                COMMAND_KEYWORDS.REGISTRY,
                ["Реестр"],
                ADMIN_GROUP + [Groups.CardRegistry],
                text_decoration_before="📂 ",
                show_in_main_menu=True,
            ): CommandNode(
                COMMAND_KEYWORDS.CARD + [""],
                ["карт пациентов"],
                lambda: self.menu_handler(self.menu.card_registry),
                text=lambda: self.get_polibase_person_card_place_label(self.arg()),
            ),
            CommandNode(
                COMMAND_KEYWORDS.REGISTRY,
                [""],
                allowed_groups=ADMIN_GROUP + [Groups.CardRegistry],
            ): {
                CommandNode(COMMAND_KEYWORDS.CARD + [""], [""]): A.D.to_dict(
                    self.menu.card_registry
                )
            },
            self.journal_node: None,
            CommandNode(self.journal_node.name_list, [""]): A.D.to_dict(
                self.menu.journals
            ),
            self.note_node: None,
            CommandNode(self.note_node.name_list, [""]): A.D.to_dict(self.menu.notes),
            CommandNode(it_unit_node.name_list, [""]): A.D.to_dict(self.menu.it),
            self.create_command_link(
                A.D.map(
                    lambda item: j((COMMAND_LINK_SYMBOL, item)), help_node.name_list
                ),
                help_node.name_list[0],
                ["Помощь"],
                None,
                False,
                text_decoration_before="❔ ",
            ): None,
            help_node: {
                CommandNode(
                    ["infinity", "инфинити"],
                    [
                        js(("Инфинити", A.CT.VISUAL.ARROW)),
                    ],
                ): INFINITY_STUDY_COURSE_COLLECTION,
                CommandNode(
                    ["?polibase", "полибейс"],
                    js(("Полибейс", A.CT.VISUAL.ARROW)),
                ): POLIBASE_HELP_COLLECTION,
                CommandNode(
                    ["holter", "холтер"],
                    [
                        js(("Аппарат Холтера", A.CT.VISUAL.ARROW)),
                    ],
                ): HOLTER_STUDY_COURSE_COLLECTION,
                CommandNode(
                    [
                        j(
                            (
                                mio_command(COMMAND_KEYWORDS.CARD),
                                mio_command(COMMAND_KEYWORDS.REGISTRY),
                            ),
                            "_",
                        )
                    ],
                    [
                        js(("Реестр карт пациентов", A.CT.VISUAL.ARROW)),
                    ],
                ): CARD_REGISTRY_STUDY_COURSE_COLLECTION,
                CommandNode(
                    ["hccb", "Браузер регистратора и оператора колл-центра"],
                    [
                        js(
                            (
                                "Браузер для регистратора и оператора колл-центра",
                                A.CT.VISUAL.ARROW,
                            )
                        ),
                    ],
                ): CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION,
                self.wiki_node: None,
            },
            time_tracking_report_node: None,
            my_time_tracking_report_node: None,
            print_node: None,
            patient_node: None,
            CommandNode(patient_node.name_list, [""]): A.D.to_dict(
                self.menu.polibase_person
            ),
            doctor_node: None,
            CommandNode(doctor_node.name_list, [""]): A.D.to_dict(
                self.menu.polibase_doctor
            ),
            CommandNode(
                ["ping"],
                [
                    "Проверка компьютера на доступность",
                    "Проверить компьютер на доступность",
                ],
                self.ws_ping_handler,
            ): None,
            check_node: None,
            CommandNode(
                [COMMAND_KEYWORDS.ASK[0]],
                lambda: [js(("Спросить", None if self.argless else self.arg()))],
                lambda: self.return_result(self.input.input("Ответ")),
            ): None,
            CommandNode(
                [COMMAND_KEYWORDS.ASK_YES_NO[0]],
                lambda: [js(("Спросить", None if self.argless else self.arg()))],
                lambda: self.return_result(self.input.yes_no("Ответ")),
            ): None,
            CommandNode(check_node.name_list, [""]): A.D.to_dict(self.menu.check),
            polibase_node: None,
            CommandNode(polibase_node.name_list, [""]): A.D.to_dict(self.menu.polibase),
            CommandNode(marketer_unit_node.name_list, [""]): A.D.to_dict(
                self.menu.marketer_unit
            ),
            CommandNode(
                ["action", "действие"],
                lambda: A.D.map(
                    lambda item: j(
                        (item, "" if self.argless else " " + esc(self.arg()))
                    ),
                    ["Выполнение действия", "Действие"],
                ),
                self.create_action_handler,
                ADMIN_GROUP,
                show_in_main_menu=True,
                text_decoration_before="🎯 ",
                help_text=lambda: js((" (", i("Название действия"), ")")),
                # filter_function=lambda: self.argless or ne(A.D_ACT.get(self.arg())),
            ): None,
            CommandNode(
                ["unit", "отдел"],
                ["Отделы"],
                lambda: self.menu_handler(self.menu.unit),
                text_decoration_before="🏥 ",
                show_in_main_menu=True,
            ): None,
            it_unit_node: None,
            hr_unit_node: None,
            call_centre_unit_node: None,
            marketer_unit_node: None,
            CommandNode(
                ["indication^s", "показания"],
                ["Показания"],
                lambda: self.check_resources_and_indications_handler(
                    [CheckableSections.INDICATIONS]
                ),
                ADMIN_GROUP + [Groups.RD, Groups.IndicationWatcher],
                text_decoration_before="📈 ",
                show_in_main_menu=True,
                filter_function=lambda: self.argless,
            ): None,
            CommandNode(
                ["backup", "бекап"],
                ["Бекап"],
                lambda: self.menu_handler(self.menu.backup),
                ADMIN_GROUP,
                text_decoration_before="📦 ",
                show_in_main_menu=True,
            ): None,
            robocopy_node: None,
            polibase_backup_node: None,
            # self.create_command_link(
            #    "cr",
            #    "card registry",
            #    [""],
            #    ADM + [Groups.CardRegistry],
            #    show_in_main_menu=False,
            # ): None,
            CommandNode(
                self.keywords.command.CREATE,
                ["Создание", "Создать"],
                filter_function=lambda: self.argless,
            ): {
                CommandNode(
                    change_user_password_node.name_list,
                    ["пароля", "пароль"],
                    self.create_password_handler,
                    filter_function=lambda: self.is_not_all or self.in_all_commands,
                ): None,
                CommandNode(
                    ["timestamp"],
                    ["временной метки", "временную метку"],
                    self.create_timestamp_handler,
                    ADMIN_GROUP,
                ): None,
            },
            CommandNode([""], [""]): all_passwords_node,
            CommandNode(
                ["set"],
                ["Установить значение переменной"],
                self.get_or_set_variable_handler,
            ): None,
            CommandNode(
                ["open"],
                ["Открытие дверей холодного прохода"],
                lambda: self.door_open_handler("cold_pass"),
            ): None,
            CommandNode(
                ["close"],
                ["Закрытие дверей холодного прохода"],
                lambda: self.door_close_handler("cold_pass"),
            ): None,
            CommandNode(
                ["get"],
                ["Показать значение переменной"],
                lambda: self.get_or_set_variable_handler(True),
            ): None,
            CommandNode(["qr"], [""]): {
                CommandNode(["code", "код"], ["Создание QR-кода", "Создать QR-код"]): {
                    CommandNode(
                        ["command", "команды"],
                        ["для команды мобильного помощника"],
                        self.create_qr_code_for_mobile_helper_command_handler,
                    ): None
                }
            },
        }
        self.create_command_list()

    @property
    def current_pih_keyword(self) -> str:
        return self.keywords.command.PIH[self.language_index]

    def say_good_bye(self) -> None:
        if not self.is_only_result:
            with self.output.make_indent(2):
                keyword: str = self.current_pih_keyword
                self.output.separated_line()
                link_text: str = A.D_F.whatsapp_send_message_to_it(keyword)
                if self.is_cli:
                    with self.output.make_indent(0):
                        self.write_line(
                            j(
                                (
                                    " ",
                                    A.CT_V.ROBOT,
                                    " ",
                                    nl("Команда выполнена."),
                                    "       Ожидаю новой команды...",
                                )
                            )
                        )
                else:
                    self.write_line(
                        j(
                            (
                                b(keyword.upper()),
                                ": до свидания, ",
                                self.get_user_given_name(),
                                ".",
                            )
                        )
                    )
                    with self.output.make_indent(2, True):
                        self.write_line(
                            js(
                                (
                                    nl("Всегда буду рад видеть Вас вновь:"),
                                    " ",
                                    A.CT_V.BULLET,
                                    "повторить",
                                    esc(b(self.get_command_title())),
                                    A.CT_V.ARROW,
                                    "отправьте",
                                    b(keyword),
                                    b(self.get_command_name(use_language_index=True)),
                                    nl(),
                                    "     ",
                                    A.CT_V.HAND_INDICATE,
                                    nl(
                                        b(
                                            A.D_F.whatsapp_send_message_to_it(
                                                js((keyword, self.get_command_name()))
                                            )
                                        )
                                    ),
                                    "или",
                                    nl(),
                                    " ",
                                    A.CT_V.BULLET,
                                    "отправьте",
                                    b(keyword),
                                    nl(),
                                    "     ",
                                    A.CT_V.HAND_INDICATE,
                                    b(link_text),
                                )
                            )
                        )

    def choose_file(
        self,
        search_request: str | None = None,
        filter_function: Callable[[str], bool] | None = None,
        command_type: A.CT_CMDT | None = None,
    ) -> File:
        search_request_source: str | None = search_request
        file_pattern_index: int | None = get_file_pattern_index(search_request)
        if ne(search_request):
            search_request = search_request[
                len(FILE_PATTERN_LIST[file_pattern_index]) :
            ]
            if n(command_type):
                splitter_index: int = search_request.find(SPLITTER)
                command_type = A.D_Ex.command_type(
                    search_request
                    if splitter_index == -1
                    else search_request[0:splitter_index]
                )

        def label_function(file: File, _) -> str:
            title_list: list[str] = file.title.split(SPLITTER)
            if len(title_list) == 3:
                return j(
                    ([b(title_list[0].upper()), ": "] if n(filter_function) else [])
                    + [
                        b(title_list[-1]),
                        " (",
                        title_list[-2],
                        ")",
                    ]
                )
            return b(title_list[1])

        with self.output.make_loading(1, "Идет загрузка файлов. Ожидайте"):
            file_list: list[File] = A.R_F.get(
                search_request,
                command_type=command_type,
                exclude_private_files=True,
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
            file_list = A.R_F.get(
                command_type=command_type,
                exclude_private_files=True,
            ).data
        file: File = self.input.item_by_index(
            "Выберите файл",
            A.D.filter(filter_function or (lambda _: True), file_list),
            label_function,
        )
        title_list: list[str] = file.title.split(SPLITTER)
        self.output.separated_line()
        if nn(search_request_source) and search_request_source in self.arg_list:
            self.arg_list.remove(search_request_source)
        command_type = command_type or A.D_Ex.command_type(file)
        self.output.head1(
            js(
                (
                    None if n(command_type) else j((b(A.D.get(command_type)[0]), ": ")),
                    title_list[-1] if n(command_type) else esc(title_list[-1]),
                )
            )
        )
        return file

    def create_command_link(
        self,
        name: str | list[str],
        link: str,
        title_and_label: list[str] | None,
        allowed_groups: list[Groups] | None = None,
        show_always: bool = False,
        text_decoration_before: str | None = None,
        show_in_main_menu: bool = True,
    ) -> CommandNode:
        return CommandNode(
            [name] if isinstance(name, str) else name,
            title_and_label,
            lambda: self.do_pih(
                js(
                    (
                        self.current_pih_keyword,
                        js((js(self.comandless_line_part_list), link)),
                    )
                )
            ),
            allowed_groups=allowed_groups,
            wait_for_input=True,
            show_in_main_menu=show_in_main_menu,
            text_decoration_before=text_decoration_before,
            show_always=show_always,
        )

    def get_user_given_name(self, value: str | None = None) -> str:
        return self.output.user.get_formatted_given_name(
            value or self.session.user_given_name
        )

    @property
    def user_given_name(self) -> str:
        return self.get_user_given_name()

    @property
    def session(self) -> MobileSession:
        return self.pih.session

    @property
    def output(self) -> MobileOutput:
        return self.pih.output

    @property
    def input(self) -> MobileInput:
        return self.pih.input

    def bold(self, value: str) -> str:
        return b(value)

    @property
    def arg_list_exclude_file(self) -> list[str]:
        return A.D.filter(
            lambda item: not item.startswith(FILE_PATTERN_LIST), self.arg_list
        )

    @property
    def check_for_arg_list_include_file(self) -> bool:
        return (self.arg_len - len(self.arg_list_exclude_file)) != 0

    def arg(
        self,
        index: int = 0,
        default_value: Any | None = None,
        as_file: bool = False,
        filter_function: Callable[[str], bool] | None = None,
    ) -> Any | None:
        result: str | None = (
            A.D.by_index(
                self.arg_list
                if n(filter_function)
                else A.D.filter(filter_function, self.arg_list),
                index,
                default_value,
            )
            if e(self.session.arg_list or [])
            else self.session.arg(index, default_value)
        )
        if as_file and ne(result):
            return self.choose_file(result, filter_function)
        return result

    @property
    def in_main_menu(self) -> bool:
        return (
            not self.none_command
            and len(self.current_command) == 1
            and self.current_command[0] == self.main_menu_node
        )

    @property
    def in_choose_command(self) -> bool:
        return self.in_all_commands or self.none_command

    @property
    def in_all_commands(self) -> bool:
        return self.in_main_menu and self.is_all

    @property
    def argless(self) -> bool:
        return self.arg_len == 0

    def drop_args(self) -> None:
        self.session.arg_list = []
        self.arg_list = []

    def get_joke_handler(self, set_settings: bool = False) -> None:
        if set_settings:
            if A.C_U.has_property(
                self.session.user,
                A.CT_AD_UP.Jokeless,
            ):
                self.output.error(
                    j(
                        (
                            "Отправка анегдота при входе или выходе отключена Администратором.",
                            nl(),
                            "Вы не можете изменить настройки",
                        )
                    )
                )
            else:
                state: bool = not self.user_settings.has(A.CT_AD_UP.Jokeless)
                self.write_line(
                    j(
                        (
                            "Отправка анегдота при входе или выходе ",
                            b(["выключена", "включена"][state]),
                            ".",
                        )
                    )
                )
                if self.yes_no(
                    js(
                        (
                            ["выключить", "включить"][not state],
                            "отправку анегдота при выходе и входе",
                        )
                    )
                ):
                    state = not state
                    if [self.user_settings.add, self.user_settings.remove][state](
                        A.CT_AD_UP.Jokeless
                    ):
                        self.write_line(
                            j(
                                (
                                    "Отправка анегдота при входе или выходе ",
                                    b(["выключена", "включена"][state]),
                                    ".",
                                )
                            )
                        )
        else:
            self.write_line(A.R_DS.joke().data)

    def check_email_address_handler(
        self,
        value: str | None = None,
        polibase_person: PolibasePerson | None = None,
        only_for_polibase_person: bool = False,
    ) -> bool | None:
        result: bool | None = None
        try:
            if only_for_polibase_person:
                polibase_person = A.D.get_first_item(
                    self.input.polibase_persons_by_any(value or self.arg())
                )
            else:
                value = self.input.wait_for_polibase_person_pin_input(
                    lambda: value
                    or self.arg()
                    or self.input.input(
                        f"Введите:\n  {A.CT_V.BULLET} Адресс электронной почты\nили\n  {A.CT_V.BULLET} Поисковый запрос для поиска пациента"
                    )
                )
            polibase_person_string: str = ""
            if ne(polibase_person):
                polibase_person_string = j(
                    ("клиента ", b(polibase_person.FullName), SPLITTER)
                )
            if not only_for_polibase_person:
                if ne(value):
                    if A.C.email(value):
                        result = A.C.EMAIL.accessability(value)
                        self.output.separated_line()
                        text: str = js(
                            (
                                "Адресс электронной почты",
                                polibase_person_string,
                                b(value),
                                j(("" if result else "не", "доступен")),
                            )
                        )
                        if result:
                            self.output.good(text)
                        else:
                            self.output.error(text)
                        return result
                    elif ne(polibase_person):
                        self.output.error(
                            js(
                                (
                                    "Адресс электронной почты:",
                                    b(value),
                                    "имеет неверный формат",
                                )
                            )
                        )
                        return None
                else:
                    self.output.error("Адресс электронной почты отстутствует")
                    return None
            polibase_person = polibase_person or A.D.get_first_item(
                self.input.polibase_persons_by_any(value)
            )
            self.drop_args()
            result = self.check_email_address_handler(
                polibase_person.email, polibase_person
            )
            if not result:
                if self.yes_no(
                    f"Начать информационный квест для клиента {b(polibase_person.FullName)}"
                ):
                    A.A_P_IQ.start(polibase_person)
        except NotFound as error:
            self.output.error(error)
        return result

    def check_scanned_document_handler(self) -> None:
        path: str | None = self.arg()
        if nn(path) and A.PTH.exists(path):
            self.write_line("Помогите распознать документ")
            self.output.write_image(
                "Помогите распознать документ", A.D_CO.file_to_base64(path)
            )
            if self.yes_no("Это Полибейс документ"):
                self.return_result(
                    PolibaseDocument(
                        path,
                        self.input.polibase_person_any(
                            "Найдите штрих-код и введите персональный номер пациента"
                        ),
                        self.input.item_by_index(
                            "Выберите тип документа",
                            [
                                PolibaseDocumentTypes.ABPM_JOURNAL,
                                PolibaseDocumentTypes.HOLTER_JOURNAL,
                            ],
                            label_function=lambda item, _: A.D.get(item).title,
                        ).name,
                    )
                )
            else:
                self.return_result(interrupt_type=InterruptionTypes.CANCEL)
            self.output.good("Спасибо за помощь")

    def check_resources_and_indications_handler(
        self, section_list: list[CheckableSections] | None = None, all: bool = False
    ) -> None:
        section_list = section_list or CheckableSections.all()
        with self.output.make_instant_mode():
            self.console_apps_api.resources_and_indications_check(
                section_list, False, self.is_forced, all
            )

    def register_ct_indications_handler(self) -> None:
        self.console_apps_api.register_ct_indications()

    def create_polibase_db_backup_handler(self) -> None:
        name: str = A.D.now_to_string(A.CT_P.DB_DATETIME_FORMAT)
        answer: bool | None = None
        if not self.is_forced:
            answer = self.yes_no(
                "Изменить имя файла дампа базы данных",
                b("Отправьте имя"),
                js(("Использовать имя:", b(name), "- отправьте", A.O.get_number(0))),
            )
        # A.SRV_A.isolate(A.CT_SR.POLIBASE_DATABASE)
        self.write_line(
            i(
                j(
                    (
                        self.user_given_name,
                        ", ожидайте уведовление об процессе создания бекапа база данных Polibase в telegram-группе: ",
                        b("Backup Console"),
                    )
                )
            )
        )
        A.A_P.DB.backup(self.input.answer if answer else name, self.is_forced)

    def show_polibase_password_handler(self) -> None:
        LOGIN: str = "login"
        PASSWORD: str = "password"
        result: dict | None = None

        def execute_query_for_password(condition: str) -> dict:
            return one(
                A.R_P.execute(
                    js(
                        (
                            "select use_password",
                            esc(PASSWORD),
                            ", use_name",
                            esc(LOGIN),
                            "from users where",
                            condition,
                        )
                    )
                )
            )

        def get_by_login(value: str) -> dict:
            return execute_query_for_password(
                j(("lower(use_name)=", escs(value.lower())))
            )

        if self.am_i_admin:
            value: str = (
                self.arg()
                or self.input.polibase_person_any(
                    f"Введите:\n {A.CT_V.BULLET} персональный номер пользователя\n {A.CT_V.BULLET} часть имени пользователя\n {A.CT_V.BULLET} логин пользователя"
                )
            ).lower()
            result = execute_query_for_password(
                j(
                    (
                        j(("use_per_no=", value)) if A.D_C.decimal(value) else None,
                        j(("lower(use_name)=", escs(value))),
                        js(("lower(use_cliname) like", escs(j(("%", value, "%"))))),
                    ),
                    " or ",
                )
            )
        else:
            result = get_by_login(self.session.login)
        if e(result):
            self.output.error("Пользователь Полибейс не найден")
        else:
            self.write_line(
                j(
                    (
                        b("Логин"),
                        ": ",
                        result[LOGIN],
                        nl(),
                        b("Пароль"),
                        ": ",
                        result[PASSWORD],
                    )
                )
            )

    def robocopy_job_run_handler(self) -> None:
        forced: bool = self.is_forced
        source_job_name: str | None = self.arg()
        if ne(source_job_name):
            source_job_name = source_job_name.lower()
        job_name_set: set = set()
        job_status_map_by_name: dict[str, list[RobocopyJobStatus]] = defaultdict(list)
        job_status_list: list[RobocopyJobStatus] = A.R_B.robocopy_job_status_list().data
        job_status_map: dict[str, RobocopyJobStatus] = {}
        for job_status in job_status_list:
            job_name: str = job_status.name
            job_name_set.add(job_name)
            job_status_map_by_name[job_name].append(job_status)
            job_status_map[
                A.D_F_B.job_full_name(
                    job_status.name, job_status.source, job_status.destination
                )
            ] = job_status
        job_name_list: list[str] = list(job_name_set)
        job_name_list.sort()
        if ne(source_job_name) and source_job_name not in job_name_list:
            source_job_name = None

        def is_active(job_name: str) -> bool:
            inacitve_count: int = 0
            for job_status in job_status_list:
                if job_status.name == job_name:
                    inacitve_count += 1
                    if job_status.active:
                        inacitve_count -= 1
            return inacitve_count == 0

        if ne(source_job_name) and is_active(source_job_name) and not forced:
            self.output.error(f"Robocopy-задание '{source_job_name}' уже выполняется")
        else:
            if source_job_name not in job_name_list:
                self.write_line(f"{b('Список Robocopy-заданий:')}\n")

            def job_status_list_label_function(name: str) -> str:
                job_list: list[RobocopyJobStatus] = job_status_map_by_name[name]

                def job_status_item_label_function(
                    job_status: RobocopyJobStatus,
                ) -> str:
                    source: str = job_status.source
                    destination: str = job_status.destination
                    job_status = job_status_map[
                        A.D_F_B.job_full_name(name, source, destination)
                    ]
                    status: int | None = None
                    date: str | None = None
                    if job_status.active:
                        date = "выполняется"
                    else:
                        if job_status.last_created is not None:
                            date = A.D_F.datetime(job_status.last_created)
                        status = job_status.last_status
                    return (
                        f"   {A.CT.VISUAL.BULLET} {source}{A.CT.VISUAL.ARROW}{destination}"
                        + ("" if status is None else f" [ {b(status)} ]")
                        + ("" if date is None else f"\n     {date}")
                    )

                return nl(
                    jnl(A.D.map(job_status_item_label_function, job_list)),
                    reversed=True,
                )

            def job_label_function(name: str) -> str:
                return j((b(name), SPLITTER, job_status_list_label_function(name)))

            job_name: str = source_job_name or self.input.item_by_index(
                "Пожалуйста, выберите Robocopy-задание, которое необходимо запустить",
                job_name_list,
                lambda name, _: job_label_function(name),
            )
            job_list: list[RobocopyJobStatus] = job_status_map_by_name[job_name]
            job_list = (
                job_list
                if forced
                else A.D.filter(lambda item: not item.active or item.live, job_list)
            )
            if len(job_list) > 0:
                self.write_line(nl(j((b("Robocopy-задание"), ": ", job_name))))
                job_item: RobocopyJobStatus = self.input.item_by_index(
                    "Пожалуйста, выберите направление",
                    job_list
                    + ([] if len(job_list) < 2 else [RobocopyJobStatus("Все")]),
                    lambda item, _: b(item.name)
                    if n(item.destination)
                    else b(j((item.source, A.CT.VISUAL.ARROW, item.destination))),
                )
                if A.A_B.start_robocopy_job(
                    job_name, job_item.source, job_item.destination, forced
                ):
                    self.write_line(
                        i(
                            j(
                                (
                                    self.user_given_name,
                                    ", ожидайте уведовление об процессе выполнения Robocopy-задания в telegram-группе ",
                                    b("Backup Console"),
                                )
                            )
                        )
                    )
                else:
                    self.output.error(
                        j(
                            (
                                self.user_given_name,
                                ", Robocopy-задание не может быть выполнено",
                            )
                        )
                    )
            else:
                self.output.error(
                    j(
                        (
                            self.user_given_name,
                            ", все направления для Robocopy-задания в процессе выполнения",
                        )
                    )
                )

    def yes_no(
        self,
        text: str,
        yes_label: str = YES_LABEL,
        no_label: str = NO_LABEL,
        yes_checker: Callable[[str], bool] | None = None,
    ) -> bool:
        if self.is_silence or self.is_silence_yes:
            return True
        if self.is_silence_no:
            return False
        return self.input.yes_no(
            text, yes_label=yes_label, no_label=no_label, yes_checker=yes_checker
        )

    def save_media_efilm(self) -> None:
        self.write_line(i("Идёт загрузка..."))
        self.output.write_video(
            "Как экспортировать исследование пациента из eFilm. Данные находятся в папке: *C:\Program Files (x86)\Merge Healthcare\eFilm\CD*",
            MEDIA_CONTENT.VIDEO.EXPORT_FROM_EFILM,
        )

    def under_construction_handler(self) -> None:
        self.output.error(f"Извините, {self.user_given_name}, раздел в разработке 😞")

    def user_property_set_handler(self, index: int | None = None) -> None:
        action_list: FieldItemList = A.CT_FC.AD.USER_ACTION
        if index is not None:
            if index < 0 or index >= action_list.length():
                index = None
        if index == 0 and self.is_all:
            self.console_apps_api.start_user_telephone_number_editor()
        else:
            self.console_apps_api.start_user_property_setter(
                self.input.indexed_field_list("Выберите действие", action_list)
                if index is None
                else action_list.get_name_list()[index],
                self.arg(),
                True,
            )

    @property
    def is_all(self) -> bool:
        return self.all()

    @property
    def is_not_all(self) -> bool:
        return self.not_all()

    def not_all(self) -> bool:
        return not self.all()

    def all(self) -> bool:
        flag = Flags.ALL
        return self.has_flag(flag) or BM.has(self.external_flags, flag)

    @property
    def is_only_result(self) -> bool:
        return self.has_flag(Flags.ONLY_RESULT) or BM.has(
            self.external_flags, Flags.ONLY_RESULT
        )

    @property
    def is_cli(self) -> bool:
        return self.has_flag(Flags.CLI) or BM.has(self.external_flags, Flags.CLI)

    @property
    def is_silence(self) -> bool:
        return self.has_flag(Flags.SILENCE) or BM.has(
            self.external_flags, Flags.SILENCE
        )

    @property
    def is_silence_no(self) -> bool:
        return self.has_flag(Flags.SILENCE_NO) or BM.has(
            self.external_flags, Flags.SILENCE_NO
        )

    @property
    def is_silence_yes(self) -> bool:
        return self.has_flag(Flags.SILENCE_YES) or BM.has(
            self.external_flags, Flags.SILENCE_YES
        )

    @property
    def is_forced(self) -> bool:
        return self.has_flag(Flags.FORCED) or BM.has(self.external_flags, Flags.FORCED)

    @property
    def is_test(self) -> bool:
        return self.has_flag(Flags.TEST) or BM.has(self.external_flags, Flags.TEST)

    def get_formatted_given_name(self, value: str | None = None) -> str:
        return self.output.user.get_formatted_given_name(value or self.user_given_name)

    def workstation_action_handler(
        self,
        value: str | User | None = None,
        action_index: int | None = None,
        all: bool = False,
        raise_exception: bool = False,
    ) -> None:
        if n(action_index):
            action_index = self.command_by_index(
                "Выберите действие",
                ["Перезагрузить", "Выключить", "Найти"],
                lambda item, _: item,
            )

        non_search_action: bool = action_index < 2
        if not all:
            value = value or self.input.input(
                "введите название компьютера или запрос для поиска пользователя"
            )
            if value in FLAG_MAP:
                all = FLAG_MAP[value] == Flags.ALL
        if non_search_action:
            if all:
                if not self.yes_no(
                    j(
                        (
                            ("Перезагрузить" if action_index == 0 else "Выключить"),
                            " все компьютеры, которые помечены как разрешенные",
                            b("Да"),
                            " (Введите слово ",
                            esc(WORKSTATION_CHECK_WORD),
                            ")",
                        )
                    ),
                    yes_checker=(lambda item: item == WORKSTATION_CHECK_WORD),
                ):
                    return
        try:
            workstations_result: Result[list[Workstation]] | None = None
            if non_search_action:
                workstations_result = (
                    A.D_FL.computers_with_property(
                        A.R_WS.all(),
                        [
                            A.CT_AD.WSProperies.Rebootable,
                            A.CT_AD.WSProperies.Shutdownable,
                        ][action_index],
                    )
                    if non_search_action
                    else A.R_WS.all()
                    if all
                    else A.R_WS.by_any(value)
                )
                if e(workstations_result):
                    if A.C_R.accessibility_by_ping(value, None, 2):
                        if self.is_forced:
                            if action_index == 0:
                                A.A_WS.reboot(value, True)
                                self.write_line(
                                    b(
                                        j(
                                            (
                                                "Идет перезагрузка компьютера ",
                                                value,
                                                "...",
                                            )
                                        )
                                    )
                                )
                            else:
                                A.A_WS.shutdown(value, True)
                                self.write_line(
                                    b(j(("Идет выключение компьютера ", value, "...")))
                                )
                        else:
                            self.output.error(
                                js(("Компьютер", value, "нельзя перезагрузить"))
                            )
                    else:
                        self.output.error(js(("Компьютер", value, "не найден")))
                else:

                    def every_action(workstation: Workstation):
                        user_string: str = ""
                        has_user: bool = ne(workstation.samAccountName)
                        if has_user:
                            user_string = f" (им пользуется {A.R_U.by_login(workstation.samAccountName).data.name})"
                        if action_index == 0:
                            if all or (
                                A.C_WS.rebootable(workstation)
                                or (
                                    self.yes_no(
                                        js(
                                            (
                                                "Компьютер",
                                                b(workstation.name),
                                                "не отмечен как разрешенный для перезагрузки, Вы уверены, что хотите его перезагрузить",
                                            )
                                        )
                                    )
                                )
                                and (
                                    not has_user
                                    or self.yes_no(
                                        j(
                                            (
                                                "Перезагрузить компьютер ",
                                                workstation.name,
                                                user_string,
                                            )
                                        )
                                    )
                                )
                            ):
                                if A.A_WS.reboot(workstation.name, True):
                                    self.write_line(
                                        b(
                                            f"Идет перезагрузка компьютера {workstation.name}..."
                                        )
                                    )
                        else:
                            if all or (
                                A.C_WS.shutdownable(workstation)
                                or (
                                    self.yes_no(
                                        f"Компьютер {b('не отмечен')} как разрешенный для выключения, Вы уверены, что хотите его выключить"
                                    )
                                )
                                and (
                                    not has_user
                                    or self.yes_no(
                                        f"Выключить компьютер {workstation.name}{user_string}"
                                    )
                                )
                            ):
                                if A.A_WS.shutdown(workstation.name, True):
                                    self.write_line(
                                        b(
                                            f"Идет выключение компьютер {workstation.name}..."
                                        )
                                    )

                    A.R.every(every_action, workstations_result)
            else:
                try:
                    if not A.C_WS.name(value):
                        value = A.D.get_first_item(self.input.user.by_any(value))
                except NotFound as error:
                    if raise_exception:
                        raise error
                    else:
                        self.output.error(error)
                workstations_result = A.R_WS.all() if all else A.R_WS.by_any(value)

                try:

                    def data_label_function(
                        index: int, field: FieldItem, data: Any, item_data: Any
                    ) -> tuple[bool, str]:
                        if field.name == A.CT_FNC.ACCESSABLE:
                            accessable: bool = item_data
                            return True, f"{b(field.caption)}: " + (
                                "Да" if accessable else "Нет"
                            )
                        if field.name == A.CT_FNC.LOGIN:
                            login: str | None = item_data
                            return (
                                True,
                                None
                                if e(item_data)
                                else f"{b('Пользователь')}: {A.R_U.by_login(login).data.name} ({login})",
                            )
                        return False, None

                    self.output.write_result(
                        workstations_result,
                        False,
                        separated_result_item=True,
                        data_label_function=data_label_function,
                        title="Найденные компьютеры:",
                    )
                except NotFound as error:
                    if raise_exception:
                        raise error
                    else:
                        self.output.error(error)
        except NotFound as error:
            if raise_exception:
                raise error
            else:
                self.output.error(error)

    def return_result(
        self, value: Any | None = None, interrupt_type: InterruptionTypes | None = None
    ) -> None:
        if nn(self.return_result_key):
            A.E.send(
                A.CT_E.RESULT_WAS_RETURNED,
                (
                    self.return_result_key,
                    value if n(interrupt_type) else "",
                    A.D.get(interrupt_type),
                ),
            )
            self.return_result_key = None

    def reboot_workstation_handler(self, all: bool = False) -> None:
        self.workstation_action_handler(None, 0, all)

    def shutdown_workstation_handler(
        self, all: bool = False, raise_exception: bool = False
    ) -> None:
        self.workstation_action_handler(None, 1, all, raise_exception)

    def find_workstation_handler(self, all: bool = False) -> None:
        self.workstation_action_handler(None, 2, all)

    def where_handler(self) -> None:
        was_found: bool = False
        with self.output.make_allow_show_error(False):
            value: str = self.arg() or self.input.input("Введите поисковый запрос")
            try:
                self.workstation_action_handler(value, 2, False, raise_exception=True)
                was_found = True
            except NotFound as _:
                pass
            try:
                if A.C_P.person_pin(value) and A.C_P.person_exists_by_pin(int(value)):
                    polibase_person: PolibasePerson = A.D_P.person_by_pin(value)
                    result: str | None = None
                    polibase_person_card_registry_folder: str = (
                        polibase_person.ChartFolder
                    )
                    if ne(polibase_person_card_registry_folder):
                        result = j(
                            (
                                j(
                                    (
                                        b(
                                            A.CT_FC.POLIBASE.CARD_REGISTRY_FOLDER.caption
                                        ),
                                        ": ",
                                        polibase_person_card_registry_folder,
                                    )
                                ),
                                self.get_polibase_person_card_place_label(
                                    polibase_person,
                                    A.CR.persons_pin_by_folder(
                                        polibase_person_card_registry_folder
                                    ),
                                ),
                            )
                        )
                    if e(result):
                        with self.output.make_allow_show_error(True):
                            self.write_line(
                                js(
                                    (
                                        "Найдена карта пациента:",
                                        b(polibase_person.FullName),
                                    )
                                )
                            )
                            with self.output.make_indent(2, True):
                                self.output.error(
                                    j(
                                        (
                                            "Карта пациента: ",
                                            b(value),
                                            " ",
                                            A.CT_FC.POLIBASE.CARD_REGISTRY_FOLDER.default_value.lower(),
                                        )
                                    )
                                )
                        was_found = True
                    else:
                        self.write_line(
                            js(("Найдена карта пациента:", b(polibase_person.FullName)))
                        )
                        with self.output.make_indent(2, True):
                            self.write_line(result)
                        was_found = True
                else:
                    pass
            except NotFound as _:
                pass
        if not was_found:
            self.output.error("Ничего не найдено")

    def who_handler(self) -> None:
        was_found: bool = False
        with self.output.make_allow_show_error(False):
            value: str = self.arg() or self.input.input("Введите поисковый запрос")
            try:
                self.user_find_handler(value)
                was_found = True
            except NotFound as _:
                pass
            if A.C_P.person_pin(value):
                try:
                    self.polibase_person_show_information_handler(
                        value, show_title=True
                    )
                    was_found = True
                except NotFound as _:
                    pass
        if not was_found:
            self.output.error("Ничего не найдена")

    def run_command_handler(self, command_type: A.CT_CMDT | None = None) -> None:
        def filter_function(item: Note) -> bool:
            title_list: list[str] = item.title.split(SPLITTER)
            if len(title_list) > 1:
                return title_list[0].lower() in A.D.get(command_type)[1:]
            return True

        arg: Any | None = None
        if n(command_type):
            for i in range(max(1, self.arg_len)):
                arg = self.arg(
                    i,
                    as_file=True,
                    filter_function=None if n(command_type) else filter_function,
                )
                if isinstance(arg, File):
                    self.run_command(
                        A.D_Ex.command_type(arg), arg.text, arg.title, test=self.is_test
                    )
                    break
        else:
            if isinstance(arg, File):
                self.run_command(
                    A.D_Ex.command_type(arg), arg.text, arg.title, test=self.is_test
                )
            else:
                self.run_command(command_type, arg, test=self.is_test)

    def run_command(
        self,
        command_type: A.CT_CMDT | None = None,
        text: str | None = None,
        title: str | None = None,
        test: bool | None = None,
    ) -> None:
        def extract_parameters(value: str) -> str:
            class DH:
                parameters_map: dict[str, list[str | None]] = {}

            def get_name_and_title(value: Match[str]) -> tuple[str, str | None]:
                name_and_title: str = value.group()[1:]
                name_and_title_list: list[str] = name_and_title.split(SPLITTER)
                return (
                    name_and_title_list[0],
                    name_and_title_list[1] if len(name_and_title_list) > 1 else None,
                )

            def create_parameters_map(value: Match[str]) -> str:
                name: str | None = None
                title: str | None = None
                name, title = get_name_and_title(value)
                if name not in DH.parameters_map:
                    DH.parameters_map[name] = [None, title]
                return value.group()

            re.sub(PARAMETER_PATTERN, create_parameters_map, value)
            fileless_arg_list: list[str] = self.arg_list_exclude_file
            for index, parameter in enumerate(DH.parameters_map):
                DH.parameters_map[parameter][0] = A.D.if_is_in(
                    fileless_arg_list, index
                ) or self.input.input(
                    js(
                        (
                            "Введите параметр",
                            b(DH.parameters_map[parameter][1] or parameter),
                        )
                    )
                )

            def put_parameters(value: Match[str]) -> str:
                return DH.parameters_map[get_name_and_title(value)[0]][0]

            return re.sub(PARAMETER_PATTERN, put_parameters, value)

        if e(text):
            search_request: str = self.arg()
            file_pattern_index: int | None = get_file_pattern_index(search_request)
            if nn(file_pattern_index) or self.yes_no("Выбрать файл"):
                text = self.choose_file(
                    search_request,
                    command_type=command_type,
                ).text

        if command_type == A.CT_CMDT.SSH:
            host: str = self.arg() or A.D.get(
                self.input.item_by_index(
                    "Выберите хост",
                    A.D.to_list(SSHHosts),
                    lambda item, _: A.D.get(item),
                )
            )
            if ne(text):
                text = extract_parameters(text)
            with self.output.make_loading(
                1, j(("Выполнение запроса на ", b(host), ". Ожидайте"))
            ):
                self.write_line(
                    jnl(
                        A.R_SSH.execute(
                            text
                            or self.input.input(js(("Введите команду для", b(host)))),
                            host,
                        ).data
                    )
                )
        if command_type == A.CT_CMDT.CMD:
            default_host: str = A.OS.host()
            host: str | None = None

            def get_command(value: str | None = None) -> list[str]:
                result: tuple[list[str], list[str]] = A.D.dequotes(
                    value or self.pih.input.input("Введите команду")
                )
                return A.D.filter(lambda item: ne(item), result[0] + result[1])

            use_psexec_executor: bool | None = None
            host_is_local: bool | None = None
            if ne(text):
                text = extract_parameters(text)
            command_text_list: list[str] = A.D.filter(
                lambda item: not item.startswith("::"),
                ([None] if e(text) else text.splitlines()),
            )
            for text in command_text_list:
                text = get_command(text if ne(text) else None)
                if n(use_psexec_executor):
                    use_psexec_executor = e(
                        [
                            value
                            for value in A.D.map(lambda item: item.lower(), text)
                            if value in A.CT.PSTOOLS.COMMAND_LIST
                        ]
                    )
                process_result: CompletedProcess | None = None
                if use_psexec_executor:
                    if e(host):
                        if self.yes_no(
                            j(
                                (
                                    "Использовать хост ",
                                    b(default_host),
                                    ", для выполнения команды",
                                )
                            ),
                            no_label=b("Или введите название хоста"),
                        ):
                            host = default_host
                        else:
                            host = self.input.answer
                    while True:
                        host = host.lower()
                        if A.C_R.accessibility_by_ping(host, count=1):
                            self.write_line(
                                nl(
                                    js(
                                        (
                                            "Команда будет запущена на хосте",
                                            b(host),
                                        )
                                    )
                                )
                            )
                            break
                        else:
                            self.output.error(js(("Хост", b(host), "не доступен")))
                            host = self.input.input(
                                "Введите имя хоста, на котором будет выполнена команда"
                            )
                if n(host_is_local):
                    host_is_local = A.OS.host_is_local(host)
                self.write_line(
                    j(
                        (
                            self.get_formatted_given_name(),
                            "ожидайте окончания выполнения команды...",
                        )
                    )
                )
                if use_psexec_executor:
                    with self.output.make_loading(0.5, "Выролнение команды. Ожидайте"):
                        process_result = A.EXC.execute(
                            text
                            if host_is_local
                            else A.EXC.create_command_for_powershell(
                                text,
                                host,
                                interactive=None,
                                run_from_system_account=True,
                            ),
                            True,
                            True,
                            False,
                        )
                else:
                    with self.output.make_loading(0.5, "Выполнение команды. Ожидайте"):
                        process_result = A.EXC.execute(
                            A.EXC.create_command_for_executor(text[0], text[1:]),
                            True,
                            True,
                            False,
                        )

                def decode(value: bytes | None) -> str | None:
                    if e(value):
                        return None
                    return value.decode(A.CT_WINDOWS.CHARSETS.ALTERNATIVE)

                output: str | None = decode(process_result.stdout)
                error: str | None = decode(process_result.stderr)
                if ne(output):
                    self.write_line(output)
                if ne(error):
                    self.output.error(error)
        elif command_type == A.CT_CMDT.PYTHON:
            if self.session.is_mobile:
                while True:
                    command_line_list: list[str] = []
                    line_count: int = 0
                    while e(text):
                        if line_count == 0 or self.yes_no(
                            "Ввести следующую строку код",
                            no_label=j(
                                (
                                    b("Завершить ввод кода"),
                                    " - ",
                                    A.CT_V.NUMBER_SYMBOLS[0],
                                )
                            ),
                        ):
                            command_line_list.append(
                                self.input.input("Введите строку кода")
                            )
                        else:
                            break
                        line_count += 1
                    command_part_item: str = extract_parameters(
                        text or jnl(command_line_list)
                    )
                    command_result: str | None = None
                    try:
                        command_result = A.EXC.execute_python_localy(
                            command_part_item, {"self": self}
                        )
                    except Exception as exception:
                        if isinstance(exception, InternalInterrupt):
                            raise exception
                        self.output.error(jnl(traceback.format_exception(exception)))
                        with self.output.make_separated_lines():
                            self.write_line(text)
                        if self.yes_no("Попробовать еще раз"):
                            continue
                        else:
                            break
                    if ne(command_result):
                        self.write_line(command_result)
                    break
        elif command_type in (A.CT_CMDT.POLIBASE, A.CT_CMDT.DATA_SOURCE):
            if True:  # self.session.is_mobile :
                command_line_list: list[str] = []
                line_count: int = 0
                while e(text):
                    if line_count == 0 or self.yes_no(
                        "Ввести следующую строку запроса",
                        no_label=j(
                            (
                                b("Завершить ввод текста запроса"),
                                " - ",
                                A.CT_V.NUMBER_SYMBOLS[0],
                            )
                        ),
                    ):
                        command_line_list.append(
                            self.input.input("Введите текст запрос")
                        )
                    else:
                        break
                    line_count += 1
                text = text or jnl(command_line_list)
                command_part_list: list[str] = text.split("$\\n")
                command_part_list_is_single: bool = len(command_part_list) == 1
                if not command_part_list_is_single:
                    self.write_line(
                        js(
                            (
                                "Команда состоит из",
                                b(len(command_part_list)),
                                "запросов",
                            )
                        )
                    )
                for command_part_index, command_part_item in enumerate(
                    command_part_list
                ):
                    command_part_item_source: str = command_part_item
                    error_catched: bool | None = None
                    while True:
                        try:
                            command_part_item = extract_parameters(command_part_item)
                            result: Result[list[dict[str, Any]]] | None = None
                            with self.output.make_loading(
                                0.5, "Выполнение запроса. Ожидайте"
                            ):
                                result = (
                                    A.R_P.execute(command_part_item, test)
                                    if command_type == A.CT_CMDT.POLIBASE
                                    else A.R_DS.execute(command_part_item)
                                )
                            if e(result.data):
                                self.output.good(
                                    "Запрос выполнен"
                                    if command_part_list_is_single
                                    else js(
                                        ("Запрос", command_part_index + 1, "выполнен")
                                    )
                                )
                            else:
                                result.fields = FieldItemList(
                                    A.D.map(
                                        lambda item: FieldItem(item, item),
                                        list(one(result).keys()),
                                    )
                                )
                                need_show_result: bool = True  # self.session.is_mobile
                                if len(result) > 1 and (
                                    result.fields.length() * len(result) > 50
                                ):
                                    need_show_result = (
                                        not need_show_result
                                        or not self.yes_no(
                                            j(
                                                (
                                                    "Результат состоит из ",
                                                    len(result),
                                                    nl(" элементов."),
                                                    b("Выгрузить в виде EXCEL файла"),
                                                )
                                            ),
                                            no_label=j(
                                                (
                                                    b("Показать результат"),
                                                    " - ",
                                                    A.CT_V.NUMBER_SYMBOLS[0],
                                                )
                                            ),
                                        )
                                    )

                                def show_result() -> None:
                                    self.output.write_result(
                                        result,
                                        False,
                                        data_label_function=lambda _, field, __, data_value: (
                                            True,
                                            data_value
                                            if field.name == A.CT_P.DBMS_OUTPUT
                                            else j(
                                                (
                                                    " ",
                                                    A.CT_V.BULLET,
                                                    " ",
                                                    field.name,
                                                    ": ",
                                                    b((data_value or "").strip()),
                                                )
                                            ),
                                        ),
                                        separated_result_item=True,
                                    )

                                if need_show_result:
                                    if result.fields.length() > 1:
                                        show_result()
                                    else:
                                        first_field: FieldItem = result.fields.list[0]
                                        if first_field.name == A.CT_P.DBMS_OUTPUT:
                                            show_result()
                                        else:
                                            self.write_line(
                                                j((b(first_field.caption), ":"))
                                            )
                                            A.R.every(
                                                lambda data: self.write_line(
                                                    js(
                                                        (
                                                            "",
                                                            A.CT_V.BULLET,
                                                            A.D.get_first_item(data),
                                                        )
                                                    )
                                                ),
                                                result,
                                            )
                                else:
                                    result_title: str = (
                                        title
                                        or self.input.input("Введите название файла")
                                    ).split(SPLITTER)[-1]
                                    result_file_path: str = A.PTH.add_extension(
                                        A.PTH.join(A.PTH_MIO.FILES_FOLDER, A.D.uuid()),
                                        A.CT_F_E.EXCEL_NEW,
                                    )
                                    with self.output.make_loading(
                                        0.5, "Идёт создание файла"
                                    ):
                                        if A.A_D.save_xlsx(
                                            result_title, result, result_file_path
                                        ):
                                            self.output.write_document(
                                                result_title,
                                                result_title,
                                                A.D_CO.file_to_base64(result_file_path),
                                            )
                                        else:
                                            self.output.error(
                                                "Ошибка при создании файла"
                                            )
                            break
                        except Error as error:
                            details: str = error.details
                            error_catched = True
                            if command_type == A.CT_CMDT.POLIBASE:
                                for error in ["ORA-00027"]:
                                    if A.D.contains(details, error):
                                        error_catched = False
                                        break
                            if error_catched:
                                self.output.error(details)
                                with self.output.make_separated_lines():
                                    self.write_line(command_part_item_source)
                                if self.yes_no("Попробовать еще раз"):
                                    error_catched = None
                                else:
                                    break
                        if nn(error_catched):
                            break

    def show_free_marks(self) -> None:
        def label_function(data_item: Mark, _: int) -> str:
            return f" {A.CT.VISUAL.BULLET} {b(data_item.TabNumber)} - {data_item.GroupName}"

        self.output.write_result(
            A.R_M.free_list(),
            False,
            separated_result_item=False,
            label_function=label_function,
        )

    def make_mark_as_free(self) -> None:
        self.console_apps_api.make_mark_as_free(self.arg(), self.is_silence)

    def find_note_handler(self, root: bool, show_all: bool = False) -> None:
        note_name: str | None = self.arg()

        has_argument: bool = ne(note_name)
        if not (self.is_all or show_all):
            note_name = note_name or self.input.input(
                "Введите название или заголовок заметки"
            )

        full_equaliment: bool = self.is_not_all and (
            not has_argument or A.C_N.exists(note_name, note_name, self.is_not_all)
        )
        if full_equaliment or A.C_N.exists(note_name, note_name, False):

            def label_function(gkeep_item: GKeepItem, note: Note) -> list[str]:
                text: str = A.D_F.format(note.text, {"self": self})
                text_list: list[str] = text.split("___")
                text_list_result: list[str] = []
                for text_item in text_list:
                    if text_item.strip() != "_" * len(text_item.strip()):
                        text_list_result.append(text_item)
                if ne(note.title) and not A.D.equal(gkeep_item.title, note.title):
                    if len(text_list_result) > 1:
                        return [
                            j((b(note.title), nl(count=2), text_list_result[0]))
                        ] + text_list_result[1:]
                    return A.D.as_list(j((b(note.title), nl(count=2), text)))
                return text_list_result

            def label_function_for_command_menu(
                item: list[CommandNode], _
            ) -> list[str]:
                if item == [self.exit_node]:
                    return self.exit_node.title_and_label[1] + A.D.as_value(
                        self.exit_node.text_decoration_after
                    )
                return item[0].title_and_label[1]

            gkeep_item_list_result: Result[list[GKeepItem]] = A.R.sort(
                lambda item: item.title,
                A.R_N.find_gkeep_item(note_name, note_name, self.is_not_all),
            )
            if e(gkeep_item_list_result):
                self.output.error("Заметка не найдена")
            else:
                gkeep_item_list: list[GKeepItem] = (
                    [
                        self.input.item_by_index(
                            "Выберите заметку",
                            gkeep_item_list_result.data,
                            lambda item, _: j((b(item.title), ": ", item.name)),
                        )
                    ]
                    if self.is_not_all or show_all or has_argument
                    else gkeep_item_list_result.data
                )
                for gkeep_item in gkeep_item_list:
                    with self.output.make_loading(1, "Идет загрузка заметки. Ожидайте"):
                        note_result: Result[None] = A.R_N.get(gkeep_item.id)
                        note: Note = note_result.data
                        command_menu: list[CommandNode] | None = None
                        note.text, command_menu = extract_command_menu(note.text)
                        if not self.is_silence:
                            self.output.write_result(
                                note_result,
                                label_function=lambda note, _: label_function(
                                    gkeep_item, note
                                ),
                                title=None
                                if len(gkeep_item_list) == 1
                                else gkeep_item.title.upper(),
                                separated_all=True,
                            )
                            if ne(note.images):
                                self.write_line(
                                    i(
                                        js(
                                            (
                                                "Ожидайте загрузку изображений:",
                                                len(note.images),
                                            )
                                        )
                                    )
                                )
                                for index, image in enumerate(note.images):
                                    response: Response = requests.get(image)
                                    self.output.write_image(
                                        js(("Изображение", index + 1)),
                                        A.D_CO.bytes_to_base64(
                                            BytesIO(response.content).getvalue()
                                        ),
                                    )
                        if len(gkeep_item_list) == 1 and ne(command_menu):
                            self.write_line(nl(b("Доступные команды:"), count=2))
                            with self.output.make_indent(2, True):
                                self.do_pih(
                                    js(
                                        (
                                            self.current_pih_keyword,
                                            self.get_command_name(
                                                self.command_by_index(
                                                    "Выберите пункт меню",
                                                    command_menu,
                                                    label_function_for_command_menu,
                                                    use_zero_index=True,
                                                    auto_select=False,
                                                )
                                            ),
                                        )
                                    )
                                )
        else:
            self.output.error("Заметка не найдена")

    def create_action_handler(self, use_choice_of_action: bool = False) -> None:
        forced: bool = self.is_forced
        action: Actions | None = None
        if not self.argless:
            for arg_name in self.arg_list:
                action = A.D_ACT.get(arg_name)
                if ne(action):
                    self.arg_list.remove(arg_name)
                    break
        if e(action):
            if self.argless:
                action_name: str = self.input.input("Введите название действия")
                action = A.D_ACT.get(action_name)
                if e(action):
                    action = A.CT_ACT.ACTION
                    self.arg_list.append(action_name)
            else:
                action = A.CT_ACT.ACTION

        parameters: list[str] = []
        parameters_are_present: bool = not self.argless
        action_description: ActionDescription = A.D.get(action)
        if parameters_are_present:
            parameters = self.arg_list[0:]
        else:
            if ne(action_description.parameters_description):
                if self.yes_no(
                    j(
                        (
                            "Ввести параметры для действия",
                            ""
                            if e(action_description.parameters_description)
                            else j(
                                (": ", i(action_description.parameters_description))
                            ),
                        )
                    )
                ):
                    parameters = [self.input.input("Введите параметры для действия")]
        if not action_description.confirm or self.yes_no(
            js(("Запустить действие", action_description.description))
            if e(action_description.question)
            else action_description.question
        ):
            if (
                action_description.forcable
                and not forced
                and self.yes_no(
                    action_description.forced_description
                    or "Запустить действие принудительно"
                )
            ):
                forced = True
            if A.A_ACT.was_done(action, self.session.login, parameters, forced):
                if not action_description.silence:
                    self.output.good(
                        js(
                            (
                                "Действие",
                                b(action_description.description),
                                "зарегистрировано.",
                            )
                        )
                    )

    def choice_journal(self, name: str | None) -> JournalType:
        def choice_journal_internal(value: list[JournalType]) -> int:
            index: int = self.input.index(
                "Выберите журнал",
                value,
                lambda item, _: js((b(item[1].caption), j(("(", item[1].name, ")")))),
            )
            return A.D.get(value[index])[0]

        journal_list: list[JournalType] = A.D.filter(
            lambda item: item[0] >= 0, A.D.to_list(A.CT_J)
        )
        return one(
            A.D_J.type_by_any(
                (
                    choice_journal_internal(journal_list)
                    if n(name)
                    else choice_journal_internal(
                        A.D_J.type_by_any(name, self.is_not_all) or journal_list
                    )
                )
            )
        )

    def add_journal_record_handler(self) -> None:
        journal_type: JournalType | None = self.choice_journal(self.arg())

        def get(item: Enum) -> IconedOrderedNameCaptionDescription:
            return A.D.get(item)[1]

        tag: Tags = A.D_J.tag_by_id(
            A.D.get(
                self.input.item_by_index(
                    "Выберите тэг записи журнал",
                    sorted(
                        A.D.to_list(A.CT_Tag),
                        key=lambda item: get(item).order,
                    ),
                    lambda item, _: js((get(item).icon, get(item).caption)),
                )
            )[0]
        )

        variants: list[str] = A.R.map(
            lambda item: item["title"].strip('"'),
            A.R_DS.execute(
                js(
                    (
                        'SELECT parameters->"$.title" title FROM pih_db.events where name =',
                        esc(A.CT_E.ADD_JOURNAL_RECORD.name),
                        'and parameters->"$.type"=',
                        A.D.get(journal_type)[0],
                        'and parameters->"$.tag"=',
                        A.D.get(tag)[0],
                        'group by parameters->"$.title"',
                    )
                )
            ),
        ).data
        title: str | None = None
        if ne(variants):
            title_index: int | str | None = None
            title_index = self.input.index(
                js(
                    (
                        nl(),
                        "",
                        A.CT_V.BULLET,
                        "выберите заголовок журнальной записи из списка",
                    )
                ),
                variants,
                lambda item, _: item,
                False,
                True,
                js((nl(), nl("или"), "", A.CT_V.BULLET, "введите его самостоятельно")),
            )
            try:
                title_index = int(title_index)
                title = variants[title_index]
            except ValueError as _:
                title = title_index
        else:
            title = self.input.input("Введите заголовок")
        A.A_J.add(
            self.session.user,
            journal_type,
            tag,
            title,
            self.input.input("Введите текст"),
        )

    def show_journal_handler(self) -> None:
        self.execute_file("show_journal_records", redirect_to_mobile_output=True)

    def create_note_handler(
        self, name: str | None = None, title: str | None = None, text: str | None = None
    ) -> str | None:
        name = self.arg() or name
        title = self.arg(1) or title
        text = self.arg(2) or text
        self.drop_args()
        while True:
            if e(name):
                name = self.input.input(
                    js(("Введите название заметки:", b("оно должно быть уникальным")))
                )
            if A.C_N.exists(name, None, True):
                self.output.error(
                    js(
                        (
                            "Заметка с названием",
                            esc(name),
                            "уже существует",
                        )
                    )
                )
                name = None
            else:
                break
        title = title or self.input.input("Введите заголовок заметки")
        text = text or self.input.input("Введите текст заметки")
        if A.A_N.create(
            name,
            title,
            Note(title, text),
        ):
            self.output.good("Заметка создана")
            with self.output.make_indent(2):
                self.output.head("Создание QR-кода")
                qr_code_image_path: str | None = (
                    self.console_apps_api.create_qr_code_for_mobile_helper_command(
                        js((self.get_command_node_name(self.note_node), esc(name))),
                        self.input.input("Введите заголовок QR-кода"),
                        False,
                    )
                )
                if ne(qr_code_image_path):
                    if self.yes_no(
                        "Распечатать QR-код",
                        js((b("Да"), "- укажите количество копий")),
                        yes_checker=lambda value: A.D_Ex.decimal(value) > 0,
                    ):
                        self.output.good("QR-код заметки отправлен на печать")
                        for _ in range(
                            if_else(
                                self.is_silence,
                                1,
                                lambda: A.D_Ex.decimal(self.input.answer),
                            )
                        ):
                            A.A_QR.print(qr_code_image_path)
            return name
        return None

    def workstation_message_send_handler(self, to_all: bool) -> None:
        if to_all:
            self.console_apps_api.send_workstation_message_to_all()
        else:
            self.console_apps_api.send_workstation_message(
                self.arg(), self.arg(1), not self.is_silence
            )

    def who_lost_the_mark_handler(self) -> None:
        self.console_apps_api.who_lost_the_mark(self.arg())

    def marketer_statistics_handler(self) -> None:
        self.execute_file(
            "marketer_statistics_create",
            redirect_to_mobile_output=True,
            loading_text="Создание статистики. Ожидайте",
        )
        self.output.write_image(
            "Статистика по отзывам",
            A.D_CO.file_to_base64(
                A.PTH_STAT.get_file_path(
                    A.CT_STAT.Types.POLIBASE_PERSON_REVIEW_NOTIFICATION
                )
            ),
        )

    def time_tracking_report_handler(self, for_me_report_only: bool = False) -> None:
        def get_date_format(value: str) -> str:
            return (
                A.CT.YEARLESS_DATE_FORMAT
                if value.count(A.CT.DATE_PART_DELIMITER) == 1
                else A.CT.DATE_FORMAT
            )

        if for_me_report_only:
            if self.argless and self.yes_no(
                "Получить отчет в период с начала месяца до сегодняшнего дня"
            ):
                now: datetime = A.D.now()
                self.arg_list.append(j((1, now.month), "."))
                self.arg_list.append(j((now.day, now.month), "."))
        value: str | None = self.arg()
        format: str | None = None if e(value) else get_date_format(value)
        start_date: datetime | None = A.D_Ex.datetime(value, format)
        if ne(start_date):
            if format == A.CT.YEARLESS_DATE_FORMAT:
                start_date = start_date.replace(A.D.today().year)
        value = self.arg(1)
        format = None if e(value) else get_date_format(value)
        end_date: datetime | None = A.D_Ex.datetime(value, format)
        if ne(end_date):
            if format == A.CT.YEARLESS_DATE_FORMAT:
                end_date = end_date.replace(A.D.today().year)
        while True:
            if e(start_date):
                value = self.input.input(
                    j(
                        (
                            "Введите начало периода, в формате ",
                            b("ДЕНЬ.МЕСЯЦ"),
                            ", например ",
                            A.D.today_string(A.CT.YEARLESS_DATE_FORMAT),
                        )
                    )
                )
                value = A.D_F.to_date(value)
                format = get_date_format(value)
                start_date = A.D_Ex.datetime(value, format)
                if e(start_date) or start_date.date() > A.D.today():
                    continue
                if format == A.CT.YEARLESS_DATE_FORMAT:
                    start_date = start_date.replace(A.D.today().year)
            if e(end_date) or start_date > end_date:
                if not self.yes_no(
                    "Использовать сегодняшнюю дату",
                    no_label=j(
                        (
                            "Введите окончание периода, в формате ",
                            b("ДЕНЬ.МЕСЯЦ"),
                            ", например ",
                            A.D.today_string(A.CT.YEARLESS_DATE_FORMAT),
                        )
                    ),
                ):
                    value = A.D_F.to_date(self.input.answer)
                    format = get_date_format(value)
                    end_date = A.D_Ex.datetime(value, format)
                    if e(end_date):
                        continue
                    if format == A.CT.YEARLESS_DATE_FORMAT:
                        end_date = end_date.replace(A.D.today().year)
                else:
                    end_date = A.D.today(as_datetime=True)
            if not (e(start_date) or e(end_date)):
                break
        start_date_string: str = A.D.date_to_string(
            start_date, A.CT.YEARLESS_DATE_FORMAT
        )
        end_date_string: str = A.D.date_to_string(end_date, A.CT.YEARLESS_DATE_FORMAT)
        report_file_name: str = A.PTH.add_extension(
            j([self.session.login, start_date_string, end_date_string], "_"),
            A.CT_F_E.EXCEL_NEW,
        )
        report_file_path: str = A.PTH.join(
            A.PTH.MOBILE_HELPER.TIME_TRACKING_REPORT_FOLDER, report_file_name
        )
        allowed_report_for_all_persons: bool = (
            not for_me_report_only
            and not self.is_forced
            and A.C_A.by_group(
                Groups.TimeTrackingReport, False, self.session, True, False
            )
        )
        if A.A_TT.save_report(
            report_file_path,
            start_date,
            end_date,
            None
            if allowed_report_for_all_persons
            else A.R.map(
                lambda item: item.TabNumber, A.R_M.by_name(self.session.user.name)
            ).data,
            self.session.login in A.S.get(A.CT_S.PLAIN_FORMAT_AS_DEFAULT_LOGIN_LIST),
        ):
            name: str = js(
                ("Отчет рабочего времени с", start_date_string, "по", end_date_string)
            )
            self.output.write_document(
                name,
                A.PTH.add_extension(name, A.CT_F_E.EXCEL_NEW),
                A.D_CO.file_to_base64(report_file_path),
            )

    def menu_handler(self, menu_command_node_list: list[CommandNode]) -> None:
        def label_function(command_node: CommandNode) -> str:
            return j(
                (
                    A.D.as_value(command_node.text_decoration_before),
                    b(A.D.capitalize(self.get_command_node_label(command_node))),
                    j(
                        (
                            nl(),
                            " ",
                            A.CT_V.BULLET,
                            " ",
                            self.get_command_node_help_label(command_node),
                            A.D.as_value(command_node.help_text),
                            nl(),
                        )
                    )
                    if self.has_help
                    and command_node.name_list != self.exit_node.name_list
                    else "",
                    A.D.as_value(command_node.text_decoration_after),
                )
            )

        self.execute_command(
            self.command_by_index(
                "Пожалуйста, выберите пункт меню",
                A.D.filter(
                    self.command_list_filter_function,
                    A.D.map(lambda item: [item], menu_command_node_list),
                ),
                label_function=lambda item, _: label_function(item[0]),
            )
        )

    def create_qr_code_for_card_registry_folder_handler(self) -> None:
        qr_image_path_list: list[
            str
        ] = self.console_apps_api.create_qr_code_for_card_registry_folder(
            self.arg(), not self.is_silence
        )
        if e(qr_image_path_list):
            return
        count: int = A.CT_P.CARD_REGISTRY_FOLDER_QR_CODE_COUNT
        for qr_image_path_item in qr_image_path_list:
            if (
                self.is_silence
                or len(qr_image_path_list) > 1
                or self.yes_no(
                    js(("Распечатать QR-код (будут распечатаны", count, "копии)"))
                )
            ):
                for _ in range(
                    count
                    if self.is_silence
                    else max(
                        count,
                        A.D.check_not_none(
                            self.input.answer,
                            lambda: A.D_Ex.decimal(self.input.answer),
                            0,
                        ),
                    )
                ):
                    A.A_QR.print(qr_image_path_item)
        self.output.good(" QR-код отправлен на печать")

    def create_qr_code_for_mobile_helper_command_handler(self) -> None:
        image_path: str | None = (
            self.console_apps_api.create_qr_code_for_mobile_helper_command(
                self.arg(), self.arg(1), not self.is_silence
            )
        )
        if e(image_path):
            pass
        elif self.yes_no("Показать результат"):
            self.output.write_image("Результат", A.D_CO.file_to_base64(image_path))
        if self.yes_no(
            "Распечатать",
            js((b("Да"), "- укажите количество копий")),
            yes_checker=lambda value: A.D_Ex.decimal(value) > 0,
        ):
            self.output.good(" QR код отправлен на печать")
            for _ in range(1 if self.is_silence else A.D_Ex.decimal(self.input.answer)):
                A.A_QR.print(image_path)

    def study_course_handler(
        self,
        index: int | None = None,
        node_list: dict[CommandNode, None] | None = None,
        help_content_holder_list: list[HelpContentHolder] | None = None,
        wiki_location: Callable[[None], str] | None = None,
    ) -> None:
        if e(index):
            action_index: int = self.input.index(
                "Пожалуйста, выберите пункт меню",
                [
                    j(
                        (
                            b(A.D.capitalize(self.keywords.command.EXIT[1])),
                            nl("...", reversed=True),
                        )
                    ),
                    "Пройти обучающий курс",
                    "Выбрать раздел обучающего курса",
                ]
                + (
                    []
                    if n(wiki_location)
                    else ["Как открыть курс на компьютере с рабочего места?"]
                ),
                lambda item, index: [lambda _: _, b][index != 0](item),
                use_zero_index=True,
            )
            if action_index == 0:
                self.exit_node.handler()
            if action_index == 1:
                length: int = len(node_list)
                self.write_line(
                    nl(
                        j(
                            (
                                self.user_given_name,
                                ", Вы начали обучающий курс. Он состоит из ",
                                length,
                                " разделов.",
                            )
                        )
                    )
                )
                index = 0
                for index, _ in enumerate(node_list):
                    self.study_course_handler(
                        index, node_list, help_content_holder_list, True
                    )
                    if index < length - 1:
                        if not self.yes_no(
                            j(
                                (
                                    self.user_given_name,
                                    ", перейти к следующему разделу (",
                                    index + 2,
                                    " из ",
                                    length,
                                    ")",
                                )
                            )
                        ):
                            self.write_line(
                                j(
                                    (
                                        self.user_given_name,
                                        ", вы не полность прошли обучайющий курс.",
                                    )
                                )
                            )
                            break
                if index == len(node_list) - 1:
                    self.write_line(
                        j(
                            (
                                self.user_given_name,
                                ", спасибо, что прошли обучайющий курс!",
                            )
                        )
                    )
            elif action_index == 2:
                if node_list is not None:
                    main_title: str | None = self.get_command_title(
                        self.current_command
                    )
                    if ne(main_title):
                        self.output.head(main_title) is not None
                    self.study_course_handler(
                        self.input.index(
                            "Пожалуйста, выберите раздел обучения",
                            A.D.to_list(node_list, True),
                            lambda item, _: b(self.get_command_node_title(item)),
                        ),
                        node_list,
                        help_content_holder_list,
                    )
            else:
                title: str = b(self.get_command_title())
                self.execute_command([self.study_wiki_location_node])
                self.output.write_image(
                    js(
                        (
                            "На странице найдите раздел",
                            b("Обучение"),
                            "и выберите пункт меню:",
                            title,
                        )
                    ),
                    wiki_location(),
                )
        else:
            with self.output.make_instant_mode():
                help_content_holder: HelpContentHolder = help_content_holder_list[index]
                main_title: str | None = self.get_command_node_title(
                    help_content_holder.title_and_label or help_content_holder.name
                )
                if ne(main_title) and index >= 0:
                    self.output.head(j(("Раздел ", index + 1, ": ", main_title)))
                content: list[Callable[[None], str]] = help_content_holder.content
                len_content: int = len(content)
                for index, content_item in enumerate(content):
                    content_item: HelpContent = content_item
                    text: str | None = content_item.text
                    title: str | None = content_item.title or main_title
                    if text is not None:
                        self.write_line(nl(text))
                    self.output.separated_line()
                    content_link: Callable[
                        [None], str
                    ] | IndexedLink = content_item.content
                    if content_link is not None:
                        content_body: str | None = None
                        if callable(content_link):
                            content_body = content_link()
                        else:
                            content_body = getattr(
                                content_link.object,
                                f"{content_link.attribute}{index + 1}",
                            )
                        is_video: bool = isinstance(content_item, HelpVideoContent)
                        if content_item.show_loading:
                            loading_text: str = "Пожалуйста ожидайте, идет загрузка "
                            if is_video:
                                loading_text += "видео"
                            else:
                                loading_text += "изображения"
                            if len_content > 1:
                                loading_text += f" [{index + 1} из {len_content}]"
                            loading_text += "..."
                            self.write_line(i(loading_text))
                        if is_video:
                            self.output.write_video(title, content_body)
                        else:
                            self.output.write_image(title, content_body)

    def create_temporary_mark_handler(self) -> None:
        arg: str | None = self.arg()
        owner_mark: Mark | None = None
        if ne(arg):
            try:
                owner_mark = one(A.R_M.by_any(arg))
            except NotFound:
                pass
        self.console_apps_api.create_temporary_mark(owner_mark)

    def create_mark_handler(self) -> None:
        self.console_apps_api.create_new_mark()

    def create_user_handler(self) -> None:
        self.console_apps_api.create_new_user()

    def polibase_persons_by_card_registry_folder_handler(self) -> None:
        def data_label_function(
            index: int, field: FieldItem, person: PolibasePerson, data: Any, length: int
        ) -> tuple[bool, str | None]:
            def represent_data() -> str | None:
                if field.name == A.CT_FNC.FULL_NAME:
                    index_string: str = nl(index + 1)
                    return (
                        field.default_value
                        if e(data)
                        else j(
                            (index_string, " " * (len(str(length)) + 3), b(person.pin))
                        )
                    )
                if field.name in [
                    A.CT_FNC.PIN,
                    A.CT_FNC.CARD_REGISTRY_FOLDER,
                    A.CT_FNC.EMAIL,
                ]:
                    return ""

            return True, represent_data()

        polibase_person_card_registry_folder: str = (
            self.input.polibase_person_card_registry_folder(self.arg())
        )
        person_list_result: Result[
            list[PolibasePerson]
        ] = A.R_P.persons_by_card_registry_folder(
            self.arg() or polibase_person_card_registry_folder
        )
        person: PolibasePerson | None = one(person_list_result)
        if ne(person):
            if A.CR.folder_is_sorted(polibase_person_card_registry_folder):
                A.R.sort(A.D_P.sort_person_list_by_pin, person_list_result)
            else:
                person_list_result = A.CR.persons_by_folder(
                    polibase_person_card_registry_folder, person_list_result
                )
        self.output.write_result(
            person_list_result,
            separated_result_item=False,
            data_label_function=lambda *parameters: data_label_function(
                *parameters, len(person_list_result.data)
            ),
            empty_result_text=i("Папка с картами пациентов пуста"),
            use_index=False,
            title=js(
                (
                    "Список карт пациентов в папке ",
                    polibase_person_card_registry_folder,
                    nl(),
                )
            )
            if self.argless
            else None,
        )

    def sort_polibase_person_card_registry_folder_handler(self) -> None:
        with self.input.input_timeout(None):
            polibase_person_card_registry_folder: str = (
                self.input.polibase_person_card_registry_folder(self.arg())
            )
            if e(
                A.R_E.get(
                    *A.E_B.card_registry_folder_complete_card_sorting(
                        polibase_person_card_registry_folder
                    )
                )
            ):
                base: int = 10
                polibase_person_pin_list: list[int] = A.CR.persons_pin_by_folder(
                    polibase_person_card_registry_folder
                )
                length: int = len(polibase_person_pin_list)
                if length == 0:
                    self.output.error(
                        js(
                            (
                                "Папка реестра карт",
                                polibase_person_card_registry_folder,
                                "пустая",
                            )
                        )
                    )
                else:
                    stack_count: int = int(length / base)
                    polibase_person_card_registry_map = {
                        i: polibase_person_pin_list[i * base : (1 + i) * base]
                        for i in range(stack_count)
                    }
                    remainder_length: int = length - stack_count * base
                    if remainder_length > 0:
                        polibase_person_card_registry_map[
                            stack_count
                        ] = polibase_person_pin_list[stack_count * base :]
                    length = len(polibase_person_card_registry_map)
                    text: str = f"Разложите все карты пациентов, находящиеся в папке на {b(length)} стопок по {base} в каждой стопке."
                    if remainder_length > 0:
                        text += f"В последней стопке будет {b(remainder_length)} карт пациентов."
                    self.write_line(text)
                    names: list[str] = [
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "10",
                    ]

                    def sort_action(step_limit: int = 1) -> None:
                        step: int = 0
                        index: int = 0
                        while True:
                            min_pin_value: int = min(polibase_person_pin_list)
                            count: int = length
                            for index in range(length):
                                if len(polibase_person_card_registry_map[index]) == 0:
                                    count -= 1
                                    if count == 0:
                                        return
                                else:
                                    break
                            for index in range(length):
                                if len(polibase_person_card_registry_map[index]) > 0:
                                    min_pin_value = max(
                                        min_pin_value,
                                        max(polibase_person_card_registry_map[index]),
                                    )
                            position: int = -1
                            for index in range(length):
                                if (
                                    min_pin_value
                                    in polibase_person_card_registry_map[index]
                                ):
                                    position = polibase_person_card_registry_map[
                                        index
                                    ].index(min_pin_value)
                                    polibase_person_card_registry_map[index].pop(
                                        position
                                    )
                                    break
                            step += 1
                            with self.output.make_personalized(False):
                                if step_limit > 1 and step % step_limit == 1:
                                    self.write_line(
                                        nl("Возьмите карту пациента c номером:")
                                    )
                                self.write_line(
                                    js(
                                        (
                                            A.CT_V.BULLET,
                                            "Возьмите карту пациента c номером "
                                            if step_limit == 1
                                            else "",
                                            j((b(min_pin_value), ": ")),
                                            b(names[index]),
                                            "стопка",
                                            js(
                                                (
                                                    names[
                                                        A.D.check(
                                                            position > 4,
                                                            len(
                                                                polibase_person_card_registry_map[
                                                                    index
                                                                ]
                                                            )
                                                            - position,
                                                            position,
                                                        )
                                                    ],
                                                    "карта",
                                                    b(
                                                        A.D.check(
                                                            position + 1
                                                            > int(
                                                                len(
                                                                    polibase_person_card_registry_map[
                                                                        index
                                                                    ]
                                                                )
                                                                / 2
                                                            ),
                                                            "снизу",
                                                            "сверху",
                                                        )
                                                    ),
                                                )
                                                if len(
                                                    polibase_person_card_registry_map[
                                                        index
                                                    ]
                                                )
                                                > 0
                                                else ("последняя оставшаяся",)
                                            ),
                                        )
                                    )
                                )
                                if step_limit > 0 and (step % step_limit) == 0:
                                    self.output.separated_line()
                                    self.input.input(
                                        "Отправьте любое сообщение для продолжения..."
                                    )

                    sort_action(
                        A.D_Ex.decimal(
                            self.input.input(
                                "Введите какое количество операций сортировки выводить за раз. Введя 0: появяться все операции для сортировки карт в папке"
                            )
                        )
                    )
            else:
                self.output.error(
                    f"Папка реестра карт {polibase_person_card_registry_folder} уже отсортирована"
                )

    def get_card_registry_statistics_handler(self) -> None:
        places: dict[str, str] = A.CT_CR.PLACE_NAME

        statistics: list[CardRegistryFolderStatistics] = A.CR.get_statistics()
        statistics_by_place: dict[str, list[CardRegistryFolderStatistics]] = {}
        for place_item in places:
            statistics_by_place[place_item] = A.D.filter(
                lambda item: item.name.startswith(place_item), statistics
            )

        def count(statistics: list[CardRegistryFolderStatistics]) -> str:
            total: int = 0
            for item in statistics:
                total += item.count
            return str(total)

        self.write_line(nl(j(("Всего зарегистрированных карт: ", count(statistics)))))
        for place_item in places:
            self.write_line(
                j(
                    (
                        " ",
                        A.CT_V.BULLET,
                        " ",
                        places[place_item],
                        ": ",
                        count(statistics_by_place[place_item]),
                    )
                )
            )
        self.write_line(
            nl(j(("Всего папок: ", len(statistics))), reversed=True),
        )
        for place_item in places:
            with self.output.make_loading():
                titled: bool = False
                folder_name_list: list[str] = A.D.map(
                    lambda item: item.name,
                    statistics_by_place[place_item],
                )
                folder_list: list[CardRegistryFolderStatistics] = statistics_by_place[
                    place_item
                ]
                self.write_line(
                    j(
                        (
                            nl(),
                            " ",
                            A.CT_V.BULLET,
                            " ",
                            places[place_item],
                            ": ",
                            len(statistics_by_place[place_item]),
                            nl(),
                            " " * 4,
                            A.CT_V.BULLET,
                            " ",
                            "Зарегистрированных: ",
                            len(
                                A.D.filter(
                                    A.CR.is_folder_registered,
                                    folder_name_list,
                                ),
                            ),
                            # Проблемных (количество карт в папке больше {A.CT.CARD_REGISTRY.MAX_CARD_PER_FOLDER}
                            nl(),
                            " " * 4,
                            A.CT_V.BULLET,
                            " ",
                            "Незарегистрированных: ",
                            j(
                                A.D.filter(
                                    lambda item: not A.CR.is_folder_registered(item),
                                    folder_name_list,
                                ),
                                ", ",
                            ),
                            nl(),
                            " " * 4,
                            A.CT_V.BULLET,
                            " ",
                            "Количество карт пациентов в папках: ",
                            nl(),
                            A.D.list_to_string(
                                A.D.map(
                                    lambda item: j(
                                        (
                                            " " * 8,
                                            A.CT_V.BULLET,
                                            " ",
                                            b(item.name),
                                            " (",
                                            item.count,
                                            ")",
                                        )
                                    ),
                                    folder_list,
                                ),
                                separator=nl(),
                            ),
                            nl(),
                        )
                    )
                )
                for folder_name in folder_name_list:
                    person_pin_list_from_data_source = A.CR.persons_pin_by_folder(
                        folder_name
                    )
                    person_pin_list_from_polibase = A.R.map(
                        lambda item: item.pin,
                        A.R_P.persons_by_card_registry_folder(folder_name),
                    ).data
                    diff_list: list[int] = A.D.diff(
                        person_pin_list_from_polibase,
                        person_pin_list_from_data_source,
                    )
                    if ne(diff_list):
                        self.write_line(
                            j(
                                (
                                    j(
                                        (
                                            " ",
                                            A.CT_V.BULLET,
                                            " ",
                                            nl("Незарегистрованные карты в папке:"),
                                        )
                                    )
                                    if not titled
                                    else "",
                                    " " * 4,
                                    A.CT_V.BULLET,
                                    " ",
                                    b(folder_name),
                                    ": ",
                                    A.D.list_to_string(diff_list),
                                )
                            )
                        )
                        titled = True

    def register_card_registry_folder_handler(self) -> None:
        def check(value: str) -> int | None:
            return A.D_Ex.decimal(value)

        polibase_person_card_registry_folder: str = (
            A.D_F.polibase_person_card_registry_folder(
                self.arg() or self.input.polibase_person_card_registry_folder()
            )
        )
        if A.CR.is_folder_registered(polibase_person_card_registry_folder):
            if not self.yes_no(
                j((nl("Папка реестра карт уже добавлена в реестр."), "Продолжить"))
            ):
                return
        A.E.send(
            *A.E_B.card_registry_folder_was_registered(
                polibase_person_card_registry_folder,
                self.input.input("Введите номер шкафа", check_function=check),
                self.input.input("Введите номер полки", check_function=check),
                self.input.input(
                    "Введите позицию на полке (0 - без позиции)",
                    check_function=check,
                ),
            )
        )

    def add_polibase_person_to_card_registry_folder_handler(
        self,
        once: bool = False,
        polibase_person_card_registry_folder_query: str | None = None,
        polibase_person_query: str | None = None,
    ) -> None:
        if not self.argless:
            args: list[str | None] = [self.arg(0), self.arg(1)]
            for arg in A.D.not_empty_items(args):
                if A.C_P.person_card_registry_folder(arg) or (
                    arg in A.CT_CR.SUITABLE_FOLDER_NAME_SYMBOL
                ):
                    polibase_person_card_registry_folder_query = arg
                else:
                    polibase_person_query = arg
            self.drop_args()
        if self.is_forced:
            polibase_person_card_registry_folder_query = "!"
        interruption: InternalInterrupt | None = None
        polibase_person_card_registry_folder: str = (
            A.D_F.polibase_person_card_registry_folder(
                polibase_person_card_registry_folder_query
                or self.input.polibase_person_card_registry_folder()
            )
        )
        try:
            with self.input.input_timeout(None):
                polibase_person_list_in_folder_result: Result[
                    list[PolibasePerson]
                ] = A.CR.persons_by_folder(polibase_person_card_registry_folder)
                polibase_person_pin_list: list[int] = A.D.map(
                    lambda item: item.pin, polibase_person_list_in_folder_result.data
                )
                added_polibase_person_list: list[PolibasePerson] = []
                while True:
                    while True:
                        try:
                            for polibase_person in self.input.polibase_persons_by_any(
                                polibase_person_query
                            ):
                                if (
                                    polibase_person_card_registry_folder
                                    in A.CT.CARD_REGISTRY.SUITABLE_FOLDER_NAME_SYMBOL
                                ):
                                    polibase_person_card_registry_folder = (
                                        A.CR.get_suitable_folder_name_for_person(
                                            polibase_person, True
                                        )
                                    )
                                polibase_person_query = None
                                if polibase_person.pin not in polibase_person_pin_list:
                                    added_polibase_person_list.append(polibase_person)
                                    registrator_person: PolibasePerson = ()
                                    if A.CR.set_folder_for_person(
                                        polibase_person_card_registry_folder,
                                        polibase_person,
                                        A.R_P.person_by_login(
                                            self.session.user.samAccountName
                                        ).data,
                                        set_by_polibase=False,
                                    ):
                                        self.drop_args()
                                        self.output.separated_line()
                                        self.write_line(
                                            js(
                                                (
                                                    "Карта пациента с персональным номером",
                                                    b(polibase_person.pin),
                                                    "добавлена в папку",
                                                    b(
                                                        polibase_person_card_registry_folder
                                                    ),
                                                )
                                            )
                                        )
                                    else:
                                        pass
                                else:
                                    self.drop_args()
                                    self.output.separated_line()
                                    self.write_line(
                                        js(
                                            (
                                                "Карта пациента с персональным номером",
                                                b(polibase_person.pin),
                                                "уже находится в папке",
                                                b(polibase_person_card_registry_folder),
                                            )
                                        )
                                    )
                                    A.CR.set_folder_for_person(
                                        polibase_person_card_registry_folder,
                                        polibase_person,
                                        A.R_P.person_by_login(
                                            self.session.user.samAccountName
                                        ).data,
                                        set_by_polibase=False,
                                        already_set_by_polibase=True,
                                    )
                            break
                        except NotFound as error:
                            self.output.error(error)
                        except BarcodeNotFound as error:
                            self.output.error(error)
                    if once:
                        break
                    with self.output.make_personalized(False):
                        self.output.separated_line()
                        self.write_line(
                            j(
                                (
                                    nl("  Добавьте следующую карту пациента в папку"),
                                    nl("или"),
                                    "  ",
                                    self.output.create_exit_line("отправьте"),
                                    " ",
                                    i("для завершения"),
                                )
                            )
                        )
        except InternalInterrupt as _interruption:
            interruption = _interruption
        if (
            ne(added_polibase_person_list)
            and A.CR.folder_is_sorted(polibase_person_card_registry_folder)
            and self.yes_no("Показать результат")
        ):
            polibase_person_list_result: list[PolibasePerson] = (
                polibase_person_list_in_folder_result.data + added_polibase_person_list
            )
            polibase_person_list_in_folder_result.data = polibase_person_list_result
            folder_is_sorted: bool = A.CR.folder_is_sorted(
                polibase_person_card_registry_folder
            )
            if folder_is_sorted:
                A.D_P.sort_person_list_by_pin(polibase_person_list_result)

            def label_function(polibase_person: PolibasePerson, index: int) -> str:
                is_new: bool = (
                    e(polibase_person_pin_list)
                    or polibase_person.pin not in polibase_person_pin_list
                )
                result: str = f"{index + 1}. {'Добавлена ' if is_new else ''}{polibase_person.pin}: {polibase_person.FullName}"
                return result if is_new else b(result)

            self.output.write_result(
                Result(A.CT_FC.POLIBASE.PERSON, polibase_person_list_result),
                False,
                label_function=label_function,
                title=js(
                    (
                        "Список карт пациентов в папке",
                        b(polibase_person_card_registry_folder),
                    )
                ),
            )
            if ne(interruption):
                raise interruption

    def create_password_handler(self) -> None:
        self.console_apps_api.create_password()

    def create_timestamp_handler(self) -> None:
        timestamp_name: str | None = self.arg()
        timestamp_description: str | None = self.arg(1)
        timestamp_holder: StorageVariableHolder | None = None
        while True:
            variable_storage_list: list[StorageVariableHolder] = A.D_V_T.find(
                timestamp_name := A.D_F.variable_name(
                    timestamp_name
                    or self.input.input("Введите названия временной метки")
                )
            )
            self.drop_args()
            variable_is_exists: bool = ne(variable_storage_list)
            if variable_is_exists:

                def label_function(
                    item: StorageVariableHolder, _: int | None = None
                ) -> str:
                    return j(
                        [b(item.key_name)]
                        + [
                            "" if e(item.description) else " (",
                            item.description,
                            ")",
                        ]
                    )

                timestamp_holder = self.input.item_by_index(
                    "Выберите временную метку",
                    variable_storage_list,
                    label_function,
                )
                if self.yes_no(
                    js(("Обновить временную метку:", label_function(timestamp_holder)))
                ):
                    if self.yes_no(
                        "Использовать текущую дату",
                        no_label=js(
                            (
                                b("Ввести дату самостоятельно"),
                                "- отправьте",
                                A.O.get_number(0),
                            )
                        ),
                    ):
                        A.D_V_T.update(timestamp_holder)
                        if A.C_V_T_E.exists_by_timestamp(timestamp_holder.key_name):
                            return
            else:
                timestamp_description = timestamp_description or self.input.input(
                    "Введите описание временной метки"
                )
                A.D_V_T.set(
                    timestamp_name,
                    None
                    if self.yes_no(
                        "Использовать текущую дату",
                        no_label=js(
                            (
                                b("Ввести дату самостоятельно"),
                                "- отправьте",
                                A.O.get_number(0),
                            )
                        ),
                    )
                    else self.input.datetime(use_time=None, ask_time_input=False),
                    timestamp_description,
                )
                self.output.good("Временная метка создана")
                break
        note_name: str | None = None
        if self.yes_no("Создать заметку для временной метки"):
            self.output.header("Создание заметки для временной метки")
            note_name: str | None = None
            if self.yes_no(
                js(("Использовать название", b(timestamp_name), "для заметки"))
            ):
                note_name = timestamp_name
            else:
                while True:
                    if A.C_N.exists(
                        note_name := self.input.input("Введите название заметки")
                    ):
                        self.output.error(
                            js(("Заметка с названием", b(note_name), "уже существует"))
                        )
                    else:
                        break

            with self.output.make_indent(2):
                note_name = self.create_note_handler(
                    note_name,
                    "",
                    j(
                        (
                            timestamp_description,
                            ": ",
                            "{",
                            A.D.get(A.D_V.SECTIONS.TIMESTAMP),
                            ".",
                            timestamp_name,
                            "}",
                        )
                    ),
                )
            if n(note_name):
                self.output.error("Заметка не создана")
            else:
                self.output.good("Заметка создана")
        if self.yes_no("Сделать временную метку истекающей"):
            self.output.header("Создание истекающей временной метки")
            life_time_holder: StorageVariableHolder | None = None
            expired_timestamp_name: str | None = None
            with self.output.make_indent(2):
                life_time_holder = self.input.item_by_index(
                    "Выберите продолжительность (в месяцах)",
                    A.D_V.find("life_time") + A.D_V.find("duration"),
                    lambda item, _: j(
                        (
                            b(item.description),
                            ": ",
                            item.default_value,
                            " месяцев",
                        )
                    ),
                )
                if self.yes_no(
                    js(
                        (
                            "Использовать название",
                            b(timestamp_name),
                            "для истекающей временной метки",
                        )
                    )
                ):
                    expired_timestamp_name = timestamp_name
                else:
                    while True:
                        if A.C_V_T_E.exists(
                            expired_timestamp_name := self.input.input(
                                "Введите название истекающей временной метки"
                            )
                        ):
                            self.output.error(
                                js(
                                    (
                                        "Истекающая временная метка с названием",
                                        b(expired_timestamp_name),
                                        "уже существет",
                                    )
                                )
                            )
                        else:
                            break
            A.D_V_T_E.set(
                expired_timestamp_name,
                timestamp_description,
                timestamp_name,
                life_time_holder.key_name,
                note_name,
            )
            self.output.good("Истекающая заметка создана")

    def print_handler(self) -> None:
        image_path: str = self.arg() or self.input.input("Отправьте изображение")
        if self.yes_no(
            "Распечатать",
            f"{b('Да')} - укажите количество копий",
            yes_checker=lambda value: A.D_Ex.decimal(value) > 0,
        ):
            self.output.good("Изображение отправлено на печать")
            image_path_list: tuple = A.D.dequotes(image_path)
            image_path = j(
                A.D.not_empty_items([js(image_path_list[0])] + image_path_list[1])
            )
            for _ in range(1 if self.is_silence else A.D_Ex.decimal(self.input.answer)):
                A.A_QR.print(image_path)

    def about_it_handler(self) -> None:
        it_user_list: Result[list[User]] = A.R_U.by_job_position(
            A.CT_AD.JobPositions.IT
        )

        def label_function(user: User, index: int) -> str:
            result: str = nl(js(("", A.CT.VISUAL.BULLET, b(user.name))))
            if ne(user.description):
                user_description_list: list[str] = A.D_F.description_list(
                    user.description
                )
                workstation_name: str = user_description_list[1]
                workstation: Workstation = A.R_WS.by_name(workstation_name).data
                result += nl(j(("   ", user_description_list[0])))
                if nn(workstation):
                    if ne(workstation.description):
                        internal_telephone_number: str = str(
                            A.D_Ex.decimal(workstation.description.split("(")[-1])
                        )
                        result += nl(
                            js(
                                (
                                    "   Внутренний номер телефона:",
                                    b(internal_telephone_number),
                                )
                            )
                        )
            return result

        self.output.write_result(
            it_user_list,
            False,
            label_function=label_function,
            title=nl("ИТ отдел это:"),
            separated_result_item=True,
        )
        self.write_line(self.get_it_telephone_number_text())

    def user_find_handler(self, value: str | None = None) -> None:
        self.console_apps_api.find_user(value or self.arg())

    def find_mark_handler(self) -> None:
        self.console_apps_api.mark_find(self.arg())

    def find_free_mark_handler(self) -> None:
        value: str | None = self.arg()
        try:
            result_mark: Mark = one(A.R_M.by_any(value or self.input.mark.any()))

            def label_function(data_item: Mark, _: int) -> str:
                return j((A.CT.VISUAL.BULLET, b(data_item.TabNumber)))

            def filter_function(mark: Mark) -> bool:
                return mark.GroupID == result_mark.GroupID

            self.write_line(
                nl(
                    j(
                        (
                            "Свободные карты доступа для группы доступа ",
                            b(result_mark.GroupName),
                            ":",
                        )
                    )
                )
            )
            self.output.write_result(
                A.R.filter(A.R_M.free_list(), filter_function),
                False,
                separated_result_item=False,
                label_function=label_function,
                empty_result_text="Нет свободных карт доступа",
            )
        except NotFound as error:
            self.output.error(error)

    def show_all_free_marks_handler(self) -> None:
        sort_by_tab_number: bool = self.yes_no(
            "Как отсортировать",
            js((b("по табельному номеру"), "- отправьте", A.O.get_number(1))),
            js(
                (
                    b("по названию группы доступа"),
                    "- отправьте",
                    A.O.get_number(0),
                )
            ),
        )

        def sort_function(item: Mark) -> str:
            return item.TabNumber if sort_by_tab_number else item.GroupName

        self.output.write_result(
            A.R.sort(sort_function, A.R_M.free_list(False)),
            False,
            title="Свободные карты доступа:",
        )

    def door_close_handler(self, name: str) -> None:
        A.A_M.door_operation(name, "close")

    def door_open_handler(self, name: str) -> None:
        A.A_M.door_operation(name, "open")

    def get_or_set_variable_handler(self, get_action: bool = False) -> None:
        variable_name: str | None = (
            None
            if self.is_all and (not get_action or self.argless)
            else (
                self.arg()
                or self.input.input("Введите название или часть названия переменной")
            )
        )
        variable_value_holder_list: list[
            A.CT_S | A.CT_MR.TYPES | StorageVariableHolder
        ] = A.D_V.find(variable_name)

        def sort_function(
            item: A.CT_S | A.CT_MR.TYPES | StorageVariableHolder,
        ) -> int:
            if isinstance(item, A.CT_S):
                return 0
            return 1

        variable_value_holder_list = sorted(
            variable_value_holder_list, key=sort_function
        )

        def label_function(
            variable_value_holder: A.CT_S | A.CT_MR.TYPES | StorageVariableHolder,
            _=None,
        ) -> str:
            variable_name: str = (
                variable_value_holder.key_name
                if isinstance(variable_value_holder, StorageVariableHolder)
                else variable_value_holder.name
            )
            variable_holder: StorageVariableHolder = A.D.get(variable_value_holder)
            alias: str | None = variable_holder.key_name
            if e(alias) or A.D.equal(variable_name, alias):
                alias = None
            return j(
                A.D.filter(
                    lambda item: ne(item),
                    [
                        ""
                        if e(variable_holder.description)
                        else j((b(variable_holder.description), ": ")),
                        None
                        if n(variable_holder.section)
                        else j((variable_holder.section, A.D_V.SECTION_DELIMITER_ALT)),
                        variable_name,
                        "" if e(alias) else f" [{alias}]",
                    ],
                )
            )

        if e(variable_value_holder_list):
            self.output.error(f"Значение с именем '{variable_name}' не найдено")
            return
        variable_value_holder: A.CT_S | A.CT_MR.TYPES | None = None
        value: Any | None = None

        def get_value(
            variable_holder: A.CT_S | A.CT_MR.TYPES | StorageVariableHolder,
        ) -> Any:
            if isinstance(variable_holder, StorageVariableHolder):
                return variable_holder.default_value
            if isinstance(variable_holder, A.CT_S):
                return A.S.get(variable_holder)
            if isinstance(variable_holder, A.CT_MR.TYPES):
                return A.D_MR.get_count(variable_holder)

        def show_variable(
            variable_holder: A.CT_S | A.CT_MR.TYPES | StorageVariableHolder,
        ) -> None:
            value: Any = get_value(variable_holder)
            if not self.is_silence:
                with self.output.make_separated_lines():
                    group_name: str = ""
                    if isinstance(variable_holder, StorageVariableHolder):
                        if variable_holder.section == A.D.get(
                            PIH.DATA.VARIABLE.SECTIONS.TIMESTAMP
                        ):
                            group_name = "Временная метка"
                            value = A.D_F.datetime(value)
                        else:
                            group_name = "Переменная"
                    if isinstance(variable_holder, A.CT_S):
                        group_name = "Настройка"
                    if isinstance(variable_holder, A.CT_MR.TYPES):
                        group_name = "Материальный ресурс"
                    self.write_line(j((A.CT_V.BULLET, " ", group_name, SPLITTER)))
                    with self.output.make_indent(3, True):
                        self.write_line(f"{label_function(variable_holder)}:")
                        self.write_line(js(("Значение: ", b(value))))

        if self.is_all:
            with self.output.make_personalized(False):
                for variable_value_holder in variable_value_holder_list:
                    show_variable(variable_value_holder)
        else:
            with self.output.make_personalized(False):
                variable_value_holder = self.input.item_by_index(
                    "Выберите переменную",
                    variable_value_holder_list,
                    label_function,
                )
                show_variable(variable_value_holder)
        if not get_action:
            type: StorageVariableHolder = variable_value_holder.value
            if isinstance(type, IntStorageVariableHolder):

                def check_function(value: str) -> int | None:
                    return A.D_Ex.decimal(value)

                value = self.input.input("Введите число", check_function=check_function)
            elif isinstance(type, TimeStorageVariableHolder):
                format: str = A.CT.SECONDLESS_TIME_FORMAT

                def check_function(value: str) -> datetime | None:
                    return A.D_Ex.datetime(value, format)

                value = self.input.input(
                    "Введите время в формате 12:00", check_function=check_function
                )
                value = A.D.datetime_to_string(value, format)
            elif isinstance(type, BoolStorageVariableHolder):

                def check_function(value: str) -> bool | None:
                    return A.D_Ex.boolean(value)

                value = self.input.input(
                    "Введите булево значение (0 или 1)",
                    check_function=check_function,
                )
            elif isinstance(type, StorageVariableHolder):
                value = self.input.input("Введите строку")
            if ne(value):
                if isinstance(variable_value_holder, A.CT_S):
                    A.S.set(variable_value_holder, value)
                if isinstance(variable_value_holder, A.CT_MR.TYPES):
                    A.D_MR.set_count(variable_value_holder, value)
            self.output.good(
                js(
                    (
                        "Переменная",
                        label_function(variable_value_holder, None),
                        "установлена",
                    )
                )
            )

    def polibase_person_card_registry_folder_find_handler(self) -> None:
        value: str | None = self.arg()
        while True:
            try:
                value = value or self.input.polibase_person_any(
                    j(
                        (
                            nl("Введите:"),
                            "   ",
                            A.CT_V.BULLET,
                            " ",
                            nl("персональный номер"),
                            " ",
                            A.CT_V.BULLET,
                            " ",
                            nl("часть имени пациента"),
                            "   ",
                            A.CT_V.BULLET,
                            "   ",
                            nl("название папки с картами пациентов"),
                            " ",
                            nl("или"),
                            " ",
                            "   отсканируйте штрих-код на карте пациента",
                        )
                    )
                )
                if A.C_P.person_card_registry_folder(value):
                    self.write_line(self.get_polibase_person_card_place_label(value))
                    break
                else:
                    person_list_result: Result[
                        list[PolibasePerson]
                    ] = A.R_P.persons_by_any(value)
                    person: PolibasePerson | None = None
                    person_not_in_list: bool = False
                    if (
                        len(person_list_result) == 1
                        and (
                            e((person := person_list_result.data[0]).ChartFolder)
                            or (
                                person_not_in_list := person.pin
                                not in A.CR.persons_pin_by_folder(person.ChartFolder)
                            )
                        )
                        and self.yes_no(
                            j(
                                (
                                    nl("Карта не зарегистрирована в реестре карт."),
                                    "Зарегистировать",
                                )
                            )
                        )
                    ):
                        self.drop_args()
                        action = (
                            self.add_polibase_person_to_card_registry_folder_handler
                        )
                        if person_not_in_list:
                            action(True, person.ChartFolder, person.pin)
                        else:
                            self.arg_list.append(value)
                            action(True)
                        break
                    else:

                        def data_label_function(
                            _, field: FieldItem, person: PolibasePerson, data: Any
                        ) -> tuple[bool, str]:
                            result: list[bool, str] = [True, ""]
                            if field.name in [
                                A.CT_FNC.CARD_REGISTRY_FOLDER,
                                A.CT_FNC.FULL_NAME,
                            ]:
                                is_full_name_field: bool = (
                                    field.name == A.CT_FNC.FULL_NAME
                                )
                                result[1] = j(
                                    (
                                        b(field.caption),
                                        ": ",
                                        (field.default_value if e(data) else data),
                                        j((" (", person.pin, ")"))
                                        if is_full_name_field
                                        else "",
                                    )
                                )
                                if not is_full_name_field and ne(data):
                                    if ne(data):
                                        person_pin_list: list[
                                            int
                                        ] = A.CR.persons_pin_by_folder(data)
                                    result[1] += A.D.check(
                                        person.pin in person_pin_list,
                                        lambda: self.get_polibase_person_card_place_label(
                                            person, person_pin_list
                                        ),
                                        A.CT_FC.POSITION.default_value,
                                    )
                            return tuple(result)

                        self.output.write_result(
                            person_list_result,
                            False,
                            data_label_function=data_label_function,
                            separated_result_item=False,
                        )
                        break
            except NotFound as error:
                self.output.error(error)
                value = None
            except BarcodeNotFound as error:
                self.output.error(error)

    def exitable(self, interruption: InternalInterrupt) -> bool:
        return interruption.type in (
            InterruptionTypes.EXIT,
            InterruptionTypes.NEW_COMMAND,
        )

    def add_mri_log_handler(self, timestamp: datetime | None = None) -> None:
        PERIOD: int = A.CT_I.MRI.PERIOD
        YEAR: int | None = 2022
        use_preset: bool = False
        timestamp_from_db: datetime = A.D.datetime_from_string(
            one(
                A.R_DS.execute(
                    "select timestamp from mri_log order by timestamp desc limit 1;"
                )
            )["timestamp"]
        )
        timestamp_from_db += timedelta(hours=PERIOD)
        if self.yes_no(
            js(
                (
                    "Использовать дату и время для дальнейшего заполения информации:",
                    b(
                        A.D_F.datetime(
                            timestamp_from_db, A.CT.DATETIME_ONLY_HOUR_FORMAT
                        )
                    ),
                )
            )
        ):
            timestamp = timestamp_from_db
            use_preset = True

        def log(timestamp: datetime) -> None:
            self.write_line(
                js(
                    (
                        "Показания для дата и время:",
                        b(A.D_F.datetime(timestamp, A.CT.DATETIME_ONLY_HOUR_FORMAT)),
                    )
                )
            )
            preasure_list: list[str] = []
            helium_level: str = self.input.input(
                "Введите уровень гелия",
                check_function=lambda item: item
                if len(A.D.filter(lambda value: A.D_C.floated(value), item.split(" ")))
                == len(item.split(" "))
                else None,
            )
            value_list: list[str] = helium_level.split(" ")
            helium_level = value_list[0]
            preasure: str | None = None
            if len(value_list) == 2:
                preasure = value_list[1]
                preasure_list.append(preasure)
            elif len(value_list) == 1:
                preasure = self.input.input(
                    "Введите давление",
                    check_function=lambda item: item if A.D_C.floated(item) else None,
                )
                preasure_list.append(preasure)
            else:
                preasure_list = value_list[1:]
            for preasure_item in preasure_list:
                A.R_DS.execute(
                    j(
                        (
                            "insert into mri_log values (",
                            j(
                                (
                                    esc(A.D.datetime_to_string(timestamp)),
                                    preasure_item,
                                    helium_level,
                                ),
                                ", ",
                            ),
                            ");",
                        )
                    )
                )
                timestamp = timestamp + timedelta(hours=PERIOD)
            return timestamp

        if n(timestamp) or use_preset:
            with self.output.make_exit_line():
                while True:
                    try:
                        if not use_preset:
                            timestamp = datetime(
                                YEAR or A.D.now().year,
                                int(
                                    self.input.input(
                                        "Введите месяц",
                                        check_function=lambda item: A.D_Ex.decimal(
                                            item, 1, 12
                                        ),
                                    )
                                ),
                                1,
                            )
                        with self.output.make_exit_line("для выбора месяца"):
                            while True:
                                try:
                                    with self.output.make_exit_line("для выбора дня"):
                                        if not use_preset:
                                            timestamp = timestamp.replace(
                                                day=int(
                                                    self.input.input(
                                                        "Введите число",
                                                        check_function=lambda item: A.D_Ex.decimal(
                                                            item,
                                                            1,
                                                            calendar.monthrange(
                                                                timestamp.year,
                                                                timestamp.month,
                                                            )[1],
                                                        ),
                                                    )
                                                )
                                            )
                                        while True:
                                            try:
                                                if not use_preset:
                                                    timestamp = timestamp.replace(
                                                        hour=int(
                                                            self.input.input(
                                                                "Введите час",
                                                                check_function=lambda item: A.D_Ex.decimal(
                                                                    item, 0, 23
                                                                ),
                                                            )
                                                        )
                                                    )
                                                timestamp = log(timestamp)
                                                if int(timestamp.hour) == 24:
                                                    self.write_line(
                                                        js(
                                                            (
                                                                "Переход на следующий день:",
                                                                b(
                                                                    A.D_F.date(
                                                                        timestamp
                                                                    )
                                                                ),
                                                            )
                                                        )
                                                    )
                                            except InternalInterrupt as interruption:
                                                if (
                                                    interruption.type
                                                    == InterruptionTypes.BACK
                                                ):
                                                    break
                                                if self.exitable(interruption):
                                                    raise interruption

                                except InternalInterrupt as interruption:
                                    if interruption.type == InterruptionTypes.BACK:
                                        break
                                    if self.exitable(interruption):
                                        raise interruption
                    except InternalInterrupt as interruption:
                        if (
                            interruption.type == InterruptionTypes.BACK
                            or self.exitable(interruption)
                        ):
                            raise interruption
        else:
            log(timestamp)

    def untill_exit(self, action: Callable[[None], None]) -> None:
        while True:
            try:
                action()
            except InternalInterrupt as interruption:
                if interruption.type in (
                    InterruptionTypes.BACK,
                    InterruptionTypes.EXIT,
                ):
                    raise interruption

    def get_polibase_person_card_place_label(
        self,
        person_or_folder_name: PolibasePerson | str | None,
        polibase_person_pin_list: list[int] | None = None,
    ) -> str:
        if e(person_or_folder_name):
            return ""
        result_label_list: list[str] = []
        display_only_card_folder_label: bool = isinstance(person_or_folder_name, str)
        folder: str | None = (
            person_or_folder_name
            if display_only_card_folder_label
            else person_or_folder_name.ChartFolder
        )
        if ne(folder) and A.CR.is_person_card_registry_folder(folder):
            folder = A.D_F.polibase_person_card_registry_folder(folder)
            result_label_list.append(
                j(
                    (
                        b(A.CT_FC.POSITION.caption),
                        if_else(
                            display_only_card_folder_label,
                            lambda: js(("", b("папки"), b(folder))),
                            "",
                        ),
                        SPLITTER,
                    )
                )
            )
            card_folder_first_letter: str | None = folder[0]
            if card_folder_first_letter in A.CT_CR.PLACE_NAME:
                result_label_list.append(
                    f" {A.CT_V.BULLET} Место: {b(A.CT_CR.PLACE_NAME[card_folder_first_letter])}"
                )
            card_registry_folder_was_registered_event: EventDS | None = one(
                A.R_E.get(*A.E_B.card_registry_folder_was_registered(folder))
            )
            if nn(polibase_person_pin_list):
                card_index_source: int = polibase_person_pin_list.index(
                    person_or_folder_name.pin
                )
                card_index_correction: int = 0
                if card_index_source == 0:
                    card_index_correction = 1
                if card_index_source == len(polibase_person_pin_list) - 1:
                    card_index_correction = -1
                card_index: int = card_index_source
                card_index += card_index_correction
                result_label_list.append(
                    if_else(
                        e(polibase_person_pin_list),
                        js(
                            (
                                "",
                                A.CT_V.WARNING,
                                b(i(A.CT_FC.POSITION.default_value)),
                            )
                        ),
                        lambda: j(
                            (
                                nl(
                                    js(
                                        (
                                            "",
                                            A.CT_V.BULLET,
                                            "Карта в папке:",
                                            b(card_index_source + 1),
                                            "из",
                                            b(len(polibase_person_pin_list)),
                                        )
                                    )
                                ),
                                j(
                                    [nl("    -------------")]
                                    + [
                                        js(
                                            (
                                                "   ",
                                                A.CT_V.ARROW
                                                if item == person_or_folder_name.pin
                                                else A.CT_V.BULLET,
                                                nl(
                                                    b(item)
                                                    if item == person_or_folder_name.pin
                                                    else item
                                                ),
                                            )
                                        )
                                        for item in [
                                            polibase_person_pin_list[card_index - 1],
                                            polibase_person_pin_list[card_index],
                                            polibase_person_pin_list[card_index + 1],
                                        ]
                                    ]
                                    + ["    --------------"]
                                ),
                            )
                        ),
                    )
                )

            if ne(card_registry_folder_was_registered_event):
                position: CardRegistryFolderPosition = A.D.fill_data_from_source(
                    CardRegistryFolderPosition(),
                    card_registry_folder_was_registered_event.parameters,
                )
                if display_only_card_folder_label:
                    result_label_list.append(
                        j(
                            (
                                f" {A.CT_V.BULLET} Шкаф: {b(position.p_a)}\n {A.CT_V.BULLET} Полка: {b(position.p_b)}",
                                if_else(
                                    position.p_c > 0,
                                    nl(
                                        js(
                                            (
                                                "",
                                                A.CT_V.BULLET,
                                                "Позиция на полке:",
                                                b(position.p_c),
                                            )
                                        )
                                    ),
                                    "",
                                ),
                            )
                        )
                    )
                    return jnl(result_label_list)
                result_label_list.append(
                    j(
                        (
                            js(
                                (
                                    "",
                                    A.CT_V.BULLET,
                                    b("Папка:"),
                                    nl(),
                                    "     шкаф:",
                                    nl(b(position.p_a)),
                                    "     полка:",
                                    b(position.p_b),
                                )
                            ),
                            if_else(
                                lambda: position.p_c > 0,
                                f"\n     позиция на полке: {b(position.p_c)}",
                                "",
                            ),
                        )
                    )
                )

            return nl(jnl(result_label_list), reversed=True)
        return ""

    def polibase_visit_handler(self) -> None:
        self.execute_file("doctor_visits", {"test": self.is_test})

    def test_handler(self) -> None:
        def every_action(event_ds: EventDS) -> None:
            person_pin: int = A.D.fill_data_from_source(
                InaccesableEmailInformation(), event_ds.parameters
            ).person_pin
            try:
                polibase_person: PolibasePerson = A.R_P.person_by_pin(person_pin).data
                (
                    event,
                    parameters,
                ) = A.E_B.polibase_person_with_inaccessable_email_was_detected(
                    polibase_person
                )
                with self.output.make_separated_lines():
                    if e(polibase_person.email):
                        self.output.write_line(
                            j(
                                (
                                    A.CT_V.WARNING,
                                    "Пациент ",
                                    polibase_person.FullName,
                                    " (",
                                    polibase_person.pin,
                                    ") ",
                                    "имеет пустую почту",
                                )
                            )
                        )
                        A.A_E.remove(event, parameters)
                    else:
                        if A.C.email(polibase_person.email):
                            if A.C.email(polibase_person.email, True):
                                A.A_E.remove(event, parameters)
                                A.E.send(
                                    *A.E_B.polibase_person_email_was_added(
                                        polibase_person
                                    )
                                )
                                self.output.write_line(
                                    j(
                                        (
                                            " ",
                                            A.CT_V.GOOD,
                                            " ",
                                            "Пациент ",
                                            polibase_person.FullName,
                                            " (",
                                            polibase_person.pin,
                                            ") ",
                                            "имеет правильную почту: ",
                                            polibase_person.email,
                                        )
                                    )
                                )
                            else:
                                self.output.write_line(
                                    j(
                                        (
                                            " ",
                                            A.CT_V.ERROR,
                                            " ",
                                            "Пациент ",
                                            polibase_person.FullName,
                                            " (",
                                            polibase_person.pin,
                                            ") ",
                                            "имеет недоступную почту: ",
                                            polibase_person.email,
                                        )
                                    )
                                )
                        else:
                            if polibase_person.email in A.CT_P.EMPTY_EMAIL_VARIANTS:
                                A.A_E.remove(event, parameters)
                            else:
                                self.output.write_line(
                                    j(
                                        (
                                            " ",
                                            A.CT_V.WARNING,
                                            " ",
                                            "Пациент ",
                                            polibase_person.FullName,
                                            " (",
                                            polibase_person.pin,
                                            ") ",
                                            "имеет неправильную почту: ",
                                            polibase_person.email,
                                        )
                                    )
                                )
            except NotFound as _:
                pass

        result: Result[list[EventDS]] | None = None
        event_builder: Callable = (
            A.E_B.polibase_person_with_inaccessable_email_was_detected
        )
        count: int = len(A.R_E.get(event_builder()))
        if n(self.arg()) and self.yes_no(js(("Проверить все события:", b(count)))):
            result = A.R_E.get(event_builder())
        else:
            while True:
                try:
                    polibase_person: PolibasePerson = one(
                        self.input.polibase_persons_by_any(self.arg())
                    )
                    result = A.R_E.get(*event_builder(polibase_person))
                    break
                except NotFound as _:
                    self.output.error("Пациент не найден")
        if A.R.is_empty(result):
            self.output.error(
                js(
                    (
                        "Событие о добавление недоступной почты для пациента:",
                        b(polibase_person.FullName),
                        j(("(", polibase_person.pin, ")")),
                        "отсутствует.",
                    )
                )
            )
        else:
            A.R.every(every_action, result)

    def execute_file_silence(
        self,
        file_search_request: str,
        parameters: dict[str, Any] | list[tuple[str, Any]] | None = None,
    ) -> None:
        self.execute_file(file_search_request, parameters, False, False, False, None)

    def execute_file(
        self,
        file_search_request: str,
        parameters: dict[str, Any] | list[tuple[str, Any]] | None = None,
        stdout_redirect: bool = True,
        catch_exceptions: bool = True,
        redirect_to_mobile_output: bool = False,
        loading_text: str | None = None,
    ) -> str | None:
        def internal_execute_file(
            file_search_request: str,
            parameters: dict[str, Any] | list[tuple[str, Any]] | None = None,
            stdout_redirect: bool = True,
            catch_exceptions: bool = True,
            redirect_to_mobile_output: bool = False,
        ) -> str | None:
            result_parameters: dict[str, Any] = {}
            if isinstance(parameters, list):
                for parameter_item in parameters:
                    result_parameters[parameter_item[0]] = parameter_item[1]
            else:
                result_parameters = parameters or {}
            result_parameters["self"] = self
            if stdout_redirect:
                if redirect_to_mobile_output:
                    result_parameters["print"] = self.write_line
                else:
                    result_parameters["print"] = print
            try:
                return A.R_F.execute(
                    file_search_request,
                    result_parameters,
                    stdout_redirect=stdout_redirect,
                    catch_exceptions=catch_exceptions,
                )
            except Exception as exception:
                if isinstance(exception, InternalInterrupt):
                    raise exception

        if n(loading_text):
            return internal_execute_file(
                file_search_request,
                parameters,
                stdout_redirect,
                catch_exceptions,
                redirect_to_mobile_output,
            )
        else:
            with self.output.make_loading(text=loading_text):
                return internal_execute_file(
                    file_search_request,
                    parameters,
                    stdout_redirect,
                    catch_exceptions,
                    redirect_to_mobile_output,
                )

    def polibase_person_show_information_handler(
        self, value: str | None = None, show_title: bool = False
    ) -> None:
        value = value or self.arg()
        while True:
            try:

                def data_label_function(
                    _, field: FieldItem, person: PolibasePerson, data: Any
                ) -> tuple[bool, str | None]:
                    if field.name == A.CT_FNC.CARD_REGISTRY_FOLDER:
                        if e(data):
                            return (True, None)
                        # if ne(person.ChartFolder):
                        person_pin_list: list[int] = A.CR.persons_pin_by_folder(
                            person.ChartFolder
                        )
                        return (
                            True,
                            j(
                                (
                                    b(A.CT_FC.POLIBASE.CARD_REGISTRY_FOLDER.caption),
                                    ": ",
                                    data,
                                    self.get_polibase_person_card_place_label(
                                        person, person_pin_list
                                    )
                                    if person.pin in person_pin_list
                                    else "",
                                ),
                            ),
                        )
                    return (False, None)

                self.output.write_result(
                    A.R_P.persons_by_any(value or self.input.polibase_person_any()),
                    data_label_function=data_label_function,
                    title="Найденные пациенты:" if show_title else None,
                )
                break
            except NotFound as error:
                self.output.error(error)
                self.drop_args()
            except BarcodeNotFound as error:
                self.output.error(error)

    def create_command_list(self) -> list[list[CommandNode]]:
        def init_command_node_tree(
            tail: CommandNode | dict | set, parent: CommandNode | None = None
        ):
            if isinstance(tail, dict):
                for node in tail:
                    node.parent = parent
                    self.command_node_cache.append(node)
                    init_command_node_tree(tail[node], node)
            elif isinstance(tail, set):
                for node in tail:
                    self.command_node_tail_list[node] = self.command_node_cache + [node]
                    self.command_node_cache = []
            else:
                head: CommandNode | None = None
                if not tail:
                    tail = self.command_node_cache[-1]
                    head = None
                    parent = tail.parent
                else:
                    head = tail
                    parent = self.command_node_cache[-1].parent
                self.command_node_tail_list[tail] = []
                if parent and parent.name_list not in A.D.map(
                    lambda item: item.name_list, self.command_node_cache
                ):
                    self.command_node_tail_list[tail] += [parent]
                self.command_node_tail_list[tail] += self.command_node_cache
                if head:
                    self.command_node_tail_list[tail] += [tail]
                self.command_node_cache = []

        init_command_node_tree(self.command_node_tree)
        for command_node in self.command_node_tail_list:
            result: list[CommandNode] = self.command_node_tail_list[command_node]
            parent: CommandNode = result[0].parent
            while nn(parent):
                result.insert(0, parent)
                parent = parent.parent
            self.command_list.append(result)
        self.command_list.sort(key=self.command_sort_function)
        if MobileHelper.command_node_name_list is None:
            command_node_name_set: set[str] = set()
            allowed_group_set: set = set()
            for command_item in self.command_list:
                for command_node in command_item:
                    if ne(command_node.allowed_groups):
                        for group in command_node.allowed_groups:
                            allowed_group_set.add(group)
                    name_list: list[str] = A.D.map(
                        lambda item: command_name_base(item),
                        command_node.name_list or [],
                    )
                    for name_item in name_list:
                        command_node_name_set.add(name_item)
            MobileHelper.command_node_name_list = (
                A.D.filter(ne, list(command_node_name_set)) + self.keywords.command.EXIT
            )
            MobileHelper.allowed_group_list = list(allowed_group_set)
        self.fill_allowed_group_list()

    def fill_allowed_group_list(self, session: Session | None = None) -> None:
        session = session or self.session
        for group in MobileHelper.allowed_group_list:
            A.C_A.by_group(group, False, session, False, False)

    def command_sort_function(self, value: list[CommandNode]) -> str:
        name_list: list[str] = []
        for item in value:
            name_list.append(
                self.get_command_node_label(item)
                if item.order is None
                else chr(item.order)
            )
        return j(name_list).lower()

    def command_list_filter_function(
        self,
        value: list[CommandNode] | CommandNode,
        session_holder: SessionBase | None = None,
        in_root: bool = False,
        in_search: bool = False,
    ) -> bool:
        session_holder = session_holder or self.session
        allow_to_add: bool = True
        if not isinstance(value, list):
            value = [value]
        for command_node in value:
            if command_node.allowed_groups is not None:
                if e(command_node.allowed_groups):
                    allow_to_add = True
                else:
                    allow_to_add = False
                    for group in command_node.allowed_groups:
                        allow_to_add = (
                            allow_to_add or group in session_holder.allowed_groups
                        )
        if allow_to_add:
            for command_node in value:
                if ne(command_node.filter_function):
                    allow_to_add = in_root or (
                        (command_node.visible or not in_search)
                        and command_node.filter_function()
                    )
                    if not allow_to_add:
                        break
        return allow_to_add

    @staticmethod
    def check_for_starts_with_pih_keyword(value: str | None) -> bool:
        if e(value):
            return False
        value = value.lower()
        return value.startswith(COMMAND_KEYWORDS.PIH)

    def get_language_index(self, value: str) -> bool:
        value = value.lower()
        for index, item in enumerate(self.keywords.command.PIH):
            if value.find(item) == 0:
                self.language_index = index
                return True
        return False

    def do_pih(
        self,
        line: str = PIH.NAME,
        sender_user: User | None = None,
        external_flags: int | None = None,
        return_result_key: str | None = None,
        args: tuple[Any] | None = None,
    ) -> bool:
        if n(self.return_result_key):
            self.return_result_key = return_result_key
        result: bool = True
        self.line = line
        if self.get_language_index(line):
            if self.wait_for_input():
                self.input.interrupt_for_new_command()
            else:
                self.current_command = None
                command_list: list[list[CommandNode]] = []
                line = line[len(PIH.NAME) :]
                action_line_part_list: list[str] | None = None
                action_line_part_list, self.arg_list = A.D.dequotes(line)
                self.comandless_line_part_list = list(action_line_part_list)
                self.line_part_list = A.D.not_empty_items(line.split(" "))
                action_line_part_list = A.D.filter(
                    lambda item: item.lower() not in (PIH.NAME, PIH.NAME_ALT),
                    action_line_part_list,
                )

                ################################
                self.flags = 0
                if nn(external_flags):
                    self.external_flags = external_flags
                self.flag_information = []
                for index, arg_item in enumerate(action_line_part_list):
                    if arg_item in FLAG_MAP:
                        flag: Flags = FLAG_MAP[arg_item]
                        self.flags = BM.add(self.flags, flag)
                        self.flag_information.append((index, arg_item, flag))
                action_line_part_list = [
                    item
                    for item in action_line_part_list
                    if item
                    not in A.D.map(
                        lambda flag_information_item: flag_information_item[1],
                        self.flag_information,
                    )
                ]
                non_reserved_keyword_list: list[str] = []
                for arg_item in action_line_part_list:
                    reserved_keyword_founded: bool = False
                    for system_keyword in MobileHelper.command_node_name_list:
                        reserved_keyword_founded = (
                            reserved_keyword_founded
                            or arg_item.lower().startswith(system_keyword)
                        )
                        if reserved_keyword_founded:
                            self.comandless_line_part_list.remove(arg_item)
                            break
                    if not reserved_keyword_founded:
                        non_reserved_keyword_list.append(arg_item)
                for arg_item in non_reserved_keyword_list:
                    action_line_part_list.remove(arg_item)
                    self.arg_list.append(arg_item)
                self.session.arg_list = self.arg_list
                if nn(args):
                    self.session.arg_list.extend(args)
                self.session.flags = BM.add(self.session.flags, self.flags)
                source_line_part_list: list[str] = A.D.map(
                    str.lower, list(action_line_part_list)
                )
                action_line_part_list_length: int = len(action_line_part_list)

                if action_line_part_list_length > 0:
                    filtered_command_list: list[list[CommandNode]] = A.D.filter(
                        self.command_list_filter_function, self.command_list
                    )
                    for command_item in filtered_command_list:
                        command_item: list[CommandNode] = command_item
                        command_len: int = len(command_item)
                        if action_line_part_list_length > command_len:
                            continue
                        command_node_name_list: list[str] = []
                        for command_node in command_item:
                            command_node_name_list += A.D.map(
                                lambda item: command_name_base(item),
                                command_node.name_list,
                            )
                        work_arg_list: list[str] = list(source_line_part_list)
                        for arg_item in source_line_part_list:
                            has_result: bool = False
                            for command_node_name in command_node_name_list:
                                has_result = ne(
                                    command_node_name
                                ) and arg_item.startswith(command_node_name)
                                if has_result:
                                    break
                            if has_result:
                                work_arg_list.remove(arg_item)
                                if arg_item in action_line_part_list:
                                    action_line_part_list.remove(arg_item)
                                command_len -= 1
                            if command_len == 0:
                                self.current_command = list(command_item)
                        if not self.current_command:
                            if command_len > 0:
                                if len(work_arg_list) == 0:
                                    command_list.append(command_item)
                else:
                    self.current_command = [self.main_menu_node]
                is_addressed: bool = self.has_flag(Flags.ADDRESS)
                is_addressed_as_link: bool = self.has_flag(Flags.ADDRESS_AS_LINK)
                if is_addressed or is_addressed_as_link:
                    with self.output.make_indent(2):
                        self.write_line(
                            nl(
                                A.D.check(
                                    is_addressed,
                                    i(
                                        j(
                                            (
                                                self.user_given_name,
                                                ", вы выбрали режим адресации команды пользователю.",
                                            )
                                        )
                                    ),
                                    i(
                                        j(
                                            (
                                                self.user_given_name,
                                                ", вы выбрали режим адресации ссылки на команду пользователю.",
                                            )
                                        )
                                    ),
                                )
                            )
                        )
                    flag_information_item_index: int | None = None
                    for flag_information_item in self.flag_information:
                        if flag_information_item[2] == A.D.check(
                            is_addressed, Flags.ADDRESS, Flags.ADDRESS_AS_LINK
                        ):
                            flag_information_item_index = flag_information_item[0] + 1
                            break
                    recipient: str | None = A.D.check(
                        nn(self.line_part_list)
                        and nn(flag_information_item_index)
                        and len(self.line_part_list) > flag_information_item_index,
                        lambda: self.line_part_list[flag_information_item_index],
                    )
                    while True:
                        try:
                            self.recipient_user_list = self.input.user.by_any(
                                recipient, True, b("Выберите получателя команды"), True
                            )
                        except NotFound as error:
                            recipient = None
                            self.output.error(error)
                        else:
                            if len(self.recipient_user_list) == 1:
                                if (
                                    self.recipient_user_list[0].samAccountName
                                    == self.session.get_login()
                                ):
                                    self.output.error("Нельзя адресовать самому себе!")
                                    recipient = None
                                else:
                                    break
                            else:
                                self.recipient_user_list = A.D.filter(
                                    lambda item: item.samAccountName
                                    != self.session.get_login()
                                    and A.C.telephone_number(item.telephoneNumber),
                                    self.recipient_user_list,
                                )
                                if len(self.recipient_user_list) == 0:
                                    self.output.error("Нельзя адресовать самому себе!")
                                    recipient = None
                                else:
                                    break
                if nn(sender_user):
                    if ne(external_flags):
                        self.session.flags = BM.add(self.session.flags, external_flags)
                    if not BM.has(external_flags, Flags.SILENCE):
                        self.write_line(
                            i(
                                f"{self.get_user_given_name(A.D.to_given_name(sender_user))}, отправил Вам команду:"
                            )
                        )
                command_list_len: int = 0
                if self.none_command:
                    command_list = A.D.filter(
                        lambda value: self.command_list_filter_function(
                            value, in_search=True
                        ),
                        command_list,
                    )
                    command_list_len = len(command_list)
                    if command_list_len > 0:
                        if command_list_len > 1:
                            self.output.separated_line()
                            with self.output.make_indent(2):
                                self.write_line(
                                    nl(
                                        js(
                                            (
                                                b(self.current_pih_keyword.upper()),
                                                "нашёл следующие разделы:",
                                            )
                                        )
                                    )
                                )
                        with self.output.make_indent(4):

                            def label_function(
                                command: list[CommandNode], _: int
                            ) -> str | None:
                                command_node: CommandNode = command[-1]
                                return (
                                    j(
                                        (
                                            A.D.as_value(
                                                command_node.text_decoration_before
                                            ),
                                            b(self.get_command_label(command)),
                                            A.D.as_value(
                                                command_node.text_decoration_after
                                            ),
                                        )
                                    )
                                    if len(command_list) > 1
                                    else None
                                )

                            self.current_command = list(
                                self.command_by_index(
                                    "Пожалуйста, выберите пункт меню",
                                    command_list,
                                    label_function,
                                )
                            )
                    else:
                        self.output.error(f"Команда{line} не найдена")
                        self.execute_command([self.main_menu_node])
                if not self.none_command:
                    self.execute_command(self.current_command)
        else:
            if self.wait_for_input():
                self.do_input(line)
            else:
                result = False
        return result

    def get_current_command_node(self) -> CommandNode:
        return self.current_command[-1]

    def set_current_command(self, value: list[CommandNode]) -> None:
        self.current_command = value
        if nn(value):
            self.command_history.append(value)

    def get_wait_for_input(self, value: list[CommandNode]) -> bool:
        wait_for_input: bool = False
        for node in value:
            node: CommandNode = node
            wait_for_input = node.wait_for_input
            if not wait_for_input:
                break
        return wait_for_input

    def write_line(self, text: str) -> None:
        self.output.write_line(text)

    def get_command_node_title_or_label(self, value: str | CommandNode) -> list[str]:
        result: list[str] | None = None
        if isinstance(value, CommandNode):
            if ne(value.title_and_label):
                if callable(value.title_and_label):
                    temp_string_list: list[str] = value.title_and_label()
                    if temp_string_list is not None:
                        result = temp_string_list
                else:
                    result = value.title_and_label
            else:
                value_string_list: list[str] = value.name_list
                result = (
                    value_string_list[0]
                    if len(value_string_list) == 1
                    else value_string_list[1]
                )
        else:
            result = value
        return A.D.map(
            lambda item: (item or "").replace(COMMAND_NAME_BASE_DELEMITER, ""),
            result,
        )

    def get_command_node_text(self, value: str | CommandNode) -> str:
        result: str | None = None
        if isinstance(value, CommandNode):
            if nn(value.text):
                if callable(value.text):
                    temp_value_string: str | None = value.text()
                    if nn(temp_value_string):
                        result = temp_value_string
                else:
                    result = value.text
        else:
            result = value
        return result

    def get_command_node_help_label(self, value: CommandNode) -> str:
        name_list: list[str] = A.D.not_empty_items(
            A.D.map(
                lambda item: item[item.startswith(COMMAND_LINK_SYMBOL) :],
                value.name_list,
            )
        )

        def name(value: str) -> str:
            index: int = value.find(COMMAND_NAME_BASE_DELEMITER)
            if index != -1:
                return j((value[:index], "(", value[index + 1 :], ")"))
            return value

        name_list = A.D.map(name, name_list)
        return j(
            (
                A.D.check(
                    len(name_list) > 1,
                    lambda: j(
                        (
                            "[ ",
                            j(
                                A.D.map(lambda item: b(item), name_list),
                                j((" ", i("или"), " ")),
                            ),
                            " ]",
                        )
                    ),
                    A.D.check(
                        len(name_list) > 0
                        and value.name_list != self.exit_node.name_list,
                        lambda: b(name_list[0]),
                        "",
                    ),
                )
            )
        )

    def get_command_node_name(
        self, value: CommandNode, use_language_index: bool = False
    ) -> str:
        return command_name_base(
            A.D.by_index(
                A.D.not_empty_items(
                    A.D.map(
                        lambda item: item[item.startswith(COMMAND_LINK_SYMBOL) :],
                        value.name_list,
                    )
                ),
                [0, self.language_index][use_language_index],
            )
        )

    def has_flag(self, flag: Flags) -> bool:
        return BM.has(self.flags, flag)

    @property
    def has_help(self) -> bool:
        return self.has_flag(Flags.HELP)

    @property
    def has_settings(self) -> bool:
        flag = Flags.SETTINGS
        return self.has_flag(flag) or BM.has(self.external_flags, flag)

    def command_by_index(
        self,
        caption: str,
        data: list[CommandNode | list[CommandNode]],
        label_function: Callable[[CommandNode, int], str] | None = None,
        use_zero_index: bool = True,
        auto_select: bool = True,
    ) -> CommandNode | list[CommandNode]:
        if auto_select and len(data) == 1:
            return data[0]
        data.insert(0, [self.exit_node])
        with self.output.set_show_exit_message(False):
            return self.input.item_by_index(
                caption, data, label_function, use_zero_index
            )

    def main_menu_handler(self) -> None:
        is_all: bool = self.is_all

        def filter_function(command: list[CommandNode]) -> bool:
            command_node: CommandNode | None = None
            command_node = command[0]
            return command_node != self.main_menu_node and (
                not command_node.show_in_main_menu
                # and visible
                or command_node.show_always
                if is_all
                else command_node.show_in_main_menu
            )

        command_list: list[list[CommandNode]] = A.D.filter(
            filter_function, self.command_list
        )
        command_list.sort(key=self.command_sort_function)
        session: Session | None = None
        if ne(self.recipient_user_list):
            session = Session()
            session.login = self.recipient_user_list[0].samAccountName
            self.fill_allowed_group_list(session)

        def label_function(command: list[CommandNode], _: int) -> str:
            command_node: CommandNode = command[0]
            return j(
                (
                    A.D.as_value(command_node.text_decoration_before),
                    b(self.get_command_label(command)),
                    A.D.as_value(command_node.description),
                    A.D.as_value(command_node.text_decoration_after),
                )
            )

        command: list[CommandNode] = self.command_by_index(
            "Пожалуйста, выберите пункт меню",
            A.D.filter(
                lambda item: self.command_list_filter_function(item, session),
                command_list,
            ),
            label_function,
            True,
        )
        if is_all:
            self.flags = BM.remove(self.flags, Flags.ALL)
        self.execute_command(command)

    def execute_command(self, value: list[CommandNode]) -> None:
        in_root: bool = self.in_main_menu
        if self.command_list_filter_function(value, in_root=in_root):
            self.set_current_command(value)
            handler: Callable[[None], None] = value[-1].handler
            has_settings: bool = self.has_settings
            if self.has_settings:
                settings_handler: Callable[[None], None] | None = value[
                    -1
                ].settings_handler
                has_settings = nn(settings_handler)
                if has_settings:
                    handler = settings_handler
                else:
                    self.output.error("Клманда не поддерживает режим настройки")
            is_cyclic: bool = self.has_flag(Flags.CYCLIC)
            is_addressed: bool = self.has_flag(Flags.ADDRESS)
            is_addressed_as_link: bool = self.has_flag(Flags.ADDRESS_AS_LINK)

            # title
            with self.output.make_indent(2):
                if (
                    not self.is_silence
                    and not self.is_only_result
                    and value[0] != self.all_commands_node
                ):
                    title: str = (
                        js(("Настройка", esc(self.get_command_title(value))))
                        if has_settings
                        else self.get_command_title(value)
                    )
                    title_list: list[str] = title.splitlines()
                    title = "" if e(title_list) else title_list[0]
                    if ne(title):
                        self.output.separated_line()
                        self.output.head(title)
                    if len(title_list) > 1:
                        self.write_line(jnl(title_list[1:]))
                # text
                text: str | None = self.get_command_node_text(
                    self.get_current_command_node()
                )
                if ne(text):
                    with self.output.make_indent(2, True):
                        self.output.separated_line()
                        self.write_line(text)
                while True:
                    if is_cyclic:
                        for command_node in value:
                            if not command_node.wait_for_input:
                                is_cyclic = False
                                break
                    if is_cyclic:
                        self.output.separated_line()
                        self.write_line(
                            i(
                                js(
                                    (
                                        b(PIH.NAME.upper()),
                                        "будет выполнять команду в зацикленном режиме.",
                                    )
                                )
                            )
                        )
                    if nn(handler):
                        with self.output.make_indent(2, True):
                            handler()
                    if is_cyclic:
                        self.output.separated_line()
                    else:
                        break
            self.show_good_bye = True
        else:
            self.output.error(
                j((self.user_given_name, ", данная команда Вам недоступна."))
            )
            self.do_pih()

    def get_command_node_title(self, value: str | CommandNode) -> str:
        return self.get_command_node_title_or_label(value or self.current_command)[0]

    def get_command_title(self, value: list[CommandNode] | None = None) -> str:
        value = value or self.current_command
        return self.get_command_title_or_label(value, self.get_command_node_title)

    def get_command_label(self, value: list[CommandNode] | None = None) -> str:
        value = value or self.current_command
        return self.get_command_title_or_label(value, self.get_command_node_label)

    def get_command_title_or_label(
        self,
        value: list[CommandNode] | None = None,
        function: Callable[[str], str] | None = None,
    ) -> str:
        value = value or self.current_command
        filtered: list[str] = A.D.filter(lambda item: str(item).startswith("|"), value)
        if len(filtered) > 0:
            value = filtered
        return j(
            (
                A.D.capitalize(
                    A.D.list_to_string(
                        A.D.map(function, value),
                        separator=" ",
                        filter_empty=True,
                    )
                ),
                j(
                    (
                        nl(),
                        " ",
                        A.CT_V.BULLET,
                        " ",
                        "[ ",
                        j(
                            A.D.map(b, self.keywords.command.PIH),
                            j((" ", i("или"), " ")),
                        ),
                        " ]",
                        " ",
                        js(
                            A.D.map(
                                self.get_command_node_help_label,
                                A.D.filter(
                                    lambda item: ne(item.name_list[0]),
                                    value,
                                ),
                            ),
                        ),
                        A.D.check_not_none(
                            value[-1].help_text, lambda: value[-1].help_text(), ""
                        ),
                        A.D.check_not_none(value[-1].description, "", nl()),
                    )
                )
                if self.has_help and value[-1].name_list != self.exit_node.name_list
                else "",
            )
        )

    def get_command_node_label(self, value: str | CommandNode | None = None) -> str:
        title_or_label: list[str] = self.get_command_node_title_or_label(value)
        return title_or_label[1] if len(title_or_label) > 1 else title_or_label[0]

    def get_command_name(
        self, value: list[CommandNode] | None = None, use_language_index: bool = False
    ) -> str:
        value = value or self.current_command
        return A.D.list_to_string(
            A.D.map(
                lambda item: self.get_command_node_name(item, use_language_index), value
            ),
            separator=" ",
            filter_empty=True,
        )

    def wait_for_input(self) -> bool:
        return self.stdin.wait_for_data_input

    def do_input(self, line: str):
        if self.stdin.wait_for_data_input:
            self.stdin.interrupt_type = 0
            lower_line: str = line.lower()
            if lower_line in self.keywords.command.EXIT:
                interrupt_type = InterruptionTypes.EXIT
                self.stdin.interrupt_type = interrupt_type
                self.return_result(interrupt_type=interrupt_type)
            if lower_line in self.keywords.command.BACK:
                self.stdin.interrupt_type = InterruptionTypes.BACK
            self.stdin.data = line
