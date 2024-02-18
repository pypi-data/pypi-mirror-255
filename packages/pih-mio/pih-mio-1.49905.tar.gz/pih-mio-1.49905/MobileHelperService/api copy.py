from io import BytesIO
import requests
from MobileHelperContent.content import MEDIA_CONTENT
import json
from string import Formatter
from pih.collection import (
    User,
    Result,
    Workstation,
    RobocopyJobStatus,
    Mark,
    MarkGroup,
    FieldItem,
    FieldItemList,
    PolibasePerson,
    Note,
    ActionDescription,
    StorageValue,
    IntStorageValue,
    TimeStorageValue,
    BoolStorageValue,
    EventDS,
    CardRegistryFolderPosition,
    ResourceStatus,
    CardRegistryFolderStatistics,
)
from pih.console_api import ConsoleAppsApi
from pih.tools import BitMask as BM, i, b, nl, j, if_else, js, e, ne
from pih.const import CheckableSections, Actions
from pih.errors import BarcodeNotFound, NotFound
from pih import (
    PIH,
    A,
    Stdin,
    Session,
    Output,
    Input,
    while_not_do,
    MarkInput,
    UserInput,
    UserOutput,
    MarkOutput,
    SessionBase,
)
from requests import Response
from enum import Enum, auto
from dataclasses import dataclass
from time import sleep
from threading import Thread
from typing import Any, Callable
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime

import importlib.util
import sys

pih_is_exists = importlib.util.find_spec("pih") is not None
if not pih_is_exists:
    sys.path.append("//pih/facade")


class MIO:
    NAME: str = "mio"
    VERSION: str = "1.48059"


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


class MobileSession(SessionBase):
    def __init__(self, recipient: str, flags: int = 0):
        super().__init__(name="mobile")
        self.recipient: str = recipient
        self.user: User | None = None
        self.arg_list: list[str] | None = None
        self.flags: int = flags

    def say_hello(
        self, telephone_number: str | None = None, greeting: bool = True
    ) -> None:
        try:
            self.get_user(telephone_number)
            if greeting and not BM.has(self.flags, Flags.ONLY_RESULT):
                self.output.write_line(
                    f"Добро пожаловать, {self.output.user.get_formatted_given_name(self.user_given_name)}!\n {A.CT_V.WAIT} {i('Ожидайте...')}"
                )
        except NotFound as error:
            self.output.error(
                f"к сожалению, не могу идентифицировать Вас. ИТ отдел добавит Вас после окончания процедуры идентификации."
            )
            raise NotFound(error.get_details())

    def get_login(self, telephone_number: str | None = None) -> str:
        if A.D.is_none(self.user):
            self.start(
                A.R_U.by_telephone_number(
                    telephone_number or self.recipient).data
            )
            self.login = self.user.samAccountName
        return self.login

    def get_user(self, telephone_number: str | None = None) -> User:
        if A.D.is_none(self.user):
            user = A.R_U.by_login(self.get_login(
                telephone_number), True, True).data
        else:
            user = self.user
        return user

    @property
    def user_given_name(self) -> str:
        return A.D.to_given_name(self.user.name)

    def start(self, user: User, notify: bool = True) -> None:
        if A.D.is_none(self.user):
            self.user = user

    def exit(self, timeout: int | None = None, message: str | None = None) -> None:
        raise InternalInterrupt(A.CT.MOBILE_HELPER.InteraptionTypes.EXIT)

    @property
    def argv(self) -> list[str] | None:
        return self.arg_list

    def arg(self, index: int = 0, default_value: Any | None = None) -> str | Any | None:
        return A.D.by_index(self.argv, index, default_value)


class MessageType(Enum):
    SEPARATE_ONCE: int = auto()
    SEPARATED: int = auto()


class MobileUserOutput(UserOutput):
    def result(
        self,
        result: Result[list[User]],
        caption: str | None = None,
        use_index: bool = False,
        root_location: str = A.CT_AD.ACTIVE_USERS_CONTAINER_DN,
    ) -> None:
        if not A.D_C.empty(caption):
            self.parent.write_line(b(caption))
        self.parent.write_result(result, use_index=use_index)

    def get_formatted_given_name(self, value: str | None = None) -> str:
        return b(value)


class MobileMarkOutput(MarkOutput):
    def result(
        self,
        result: Result[list[Mark]],
        caption: str | None = None,
        use_index: bool = False,
    ) -> None:
        if not A.D_C.empty(caption):
            self.parent.write_line(b(caption))
        self.parent.write_result(result, use_index=use_index)


@dataclass
class MessageHolder:
    body: str | None = None
    text_before: str = ""

    def to_string(self) -> str:
        return self.text_before + self.body


class OutputFlags(Enum):
    EXITLESS: int = 1


def get_value(function_or_value: Callable[[None], str] | str | None) -> str:
    return (
        function_or_value() if callable(function_or_value) else function_or_value
    ) or ""


class MobileOutput(Output):
    MAX_MESSAGE_LINE_LENGTH: int = 12

    def __init__(self, session: MobileSession):
        super().__init__(MobileUserOutput(), MobileMarkOutput())
        self.message_buffer: list[MessageHolder] = []
        self.thread_started: bool = False
        self.session = session
        self.session.output = self
        self.type: int = 0
        self.instant_mode: bool = False
        self.recipient: str | None = None
        self.profile: int = A.CT.MESSAGE.WHATSAPP.WAPPI.Profiles.IT
        self.flags: int = 0
        self.locked: bool = False
        self.show_exit_message: bool = True

    @contextmanager
    def set_show_exit_message(self, value: bool) -> None:
        value_before: bool = self.show_exit_message
        try:
            self.show_exit_message = value
            yield True
        finally:
            self.show_exit_message = value_before

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
    def send_to_group(self, group: A.CT.MESSAGE.WHATSAPP.GROUP) -> bool:
        try:
            while_not_do(lambda: A.D_C.empty(self.message_buffer))
            self.recipient = A.D.get(group)
            yield True
        finally:
            self.recipient = None

    @contextmanager
    def make_separated_lines(self) -> bool:
        try:
            self.type = BM.add(self.type, MessageType.SEPARATED)
            yield True
        finally:
            self.type = BM.remove(self.type, MessageType.SEPARATED)

    @contextmanager
    def personalized(self, enter: bool = True) -> bool:
        if enter:
            try:
                while_not_do(lambda: A.D_C.empty(self.message_buffer))
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
    def make_loading(self, loading_timeout: int = 1, text: str | None = None) -> bool:
        while_not_do(lambda: A.D_C.empty(self.message_buffer))
        thread: Thread | None = None
        try:

            def show_loading() -> None:
                sleep(loading_timeout)
                if A.D.is_not_none(thread):
                    self.whatsapp_send(
                        js(("", A.CT_V.WAIT, text or "Идёт загрузка..."))
                    )

            thread = Thread(target=show_loading)
            thread.start()
            self.locked = True
            yield True
        finally:
            self.locked = False
            thread = None

    def internal_write_line(self) -> None:
        while self.locked:
            pass
        if not self.instant_mode:
            sleep(0.2)
        message_list: list[MessageHolder] | None = None

        def get_next_part_messages() -> list[MessageHolder]:
            max_lines: int = MobileOutput.MAX_MESSAGE_LINE_LENGTH
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
                    j(list(map(self.add_text_before, message_list)), A.CT.NEW_LINE)
                )
            )
            message_list = get_next_part_messages()
        self.thread_started = False

    def add_text_before(self, message_holder: MessageHolder) -> str:
        return j(
            list(
                map(
                    lambda message_body: MessageHolder(
                        message_body, message_holder.text_before
                    ).to_string(),
                    message_holder.body.split(A.CT.NEW_LINE),
                )
            ),
            A.CT.NEW_LINE,
        )

    def get_recipient(self) -> str:
        return self.recipient or self.session.recipient

    def write_line(self, text: str) -> None:
        if self.personalize:
            user_name: str | None = self.user.get_formatted_given_name()
            if ne(user_name):
                text = j((user_name, ", ", A.D.decapitalize(text)))
        if not A.D_C.empty(text):
            if not self.locked and BM.has(
                self.type, [MessageType.SEPARATE_ONCE, MessageType.SEPARATED]
            ):
                message_holder: MessageHolder = MessageHolder(
                    text, self.text_before)
                self.type = BM.remove(self.type, MessageType.SEPARATE_ONCE)
                while self.thread_started:
                    pass
                self.whatsapp_send(self.add_text_before(message_holder))
            else:
                self.message_buffer.append(
                    MessageHolder(text, self.text_before))
                if not self.thread_started:
                    self.thread_started = True
                    Thread(target=self.internal_write_line).start()

    def write_video(self, caption: str, video_content: str) -> None:
        return A.ME_WH_W.send_video(
            self.session.recipient, caption, video_content, self.profile
        )

    def write_image(self, caption: str, image_content: str) -> None:
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

    def exit_line(self, title: str | None = None) -> str:
        title = title or "Для выхода, отправьте: "
        return j(
            (
                nl(),
                i(
                    j(
                        (
                            title,
                            j(
                                list(
                                    map(
                                        lambda item: b(A.D.capitalize(item)),
                                        EXIT_KEYWORDS,
                                    )
                                ),
                                " или ",
                            ),
                        )
                    )
                ),
            )
        )

    def input(self, caption: str) -> None:
        with self.make_indent(4):
            self.write_line(j((caption, ":")))
            if self.show_exit_message:
                with self.make_indent(2):
                    with self.personalized(False):
                        self.write_line(
                            A.D.check(
                                BM.has(self.flags, Flags.EXITLESS),
                                "",
                                self.exit_line(),
                            )
                        )

    def value(self, caption: str, value: str, text_before: str | None = None) -> None:
        self.separated_line()
        self.write_line(f"{b(caption)}: {value}")

    def good(self, caption: str) -> str:
        self.write_line(caption)

    def error(self, caption: str) -> str:
        self.write_line(nl(js((A.CT_V.WARNING, i(caption), A.CT_V.WARNING))))

    def head(self, caption: str) -> None:
        if caption[0] == "*":
            caption = caption[1:]
        if caption[-1] == "*":
            caption = caption[:-1]
        self.write_line(b(caption.upper()) + A.CT.NEW_LINE)

    def head1(self, caption: str) -> None:
        self.write_line(b(caption) + A.CT.NEW_LINE)

    def head2(self, caption: str) -> None:
        self.write_line(b(caption))

    def new_line(self) -> None:
        return

    def separated_line(self) -> None:
        self.type = BM.add(self.type, MessageType.SEPARATE_ONCE)

    def header(self, caption: str) -> None:
        self.head1(caption)

    def bold(self, value: str) -> str:
        return b(value)

    def italic(self, value: str) -> str:
        return i(value)

    def free_marks_by_group_for_result(
        self, group: MarkGroup, result: Result, use_index: bool
    ) -> None:
        group_name: str = group.GroupName
        self.write_line(
            f"Свободные карты доступа для группы доступа '{group_name}':")
        self.write_result(
            result,
            use_index=False,
            data_label_function=lambda index, caption, result_data_item, data_value: f"{index+1}. "
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
            self.write_line(b(caption) + A.CT.NEW_LINE)
        is_result_type: bool = isinstance(result, Result)
        field_list = result.fields if is_result_type else result.fields
        data: Any = result.data if is_result_type else result.data
        if A.D_C.empty(data):
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
                                f"{b(str(index + 1))}*."
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
                                modified_item_data = label_function(
                                    field_item, item)
                                if modified_item_data is None:
                                    modified_item_data = getattr(
                                        item, field_item.name)
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
                                modified_item_data = label_function(
                                    field_item, item)
                                row_data.append(
                                    item_data
                                    if modified_item_data is None
                                    else modified_item_data
                                )
                            else:
                                row_data.append(item_data)
                row_data = list(map(lambda item: str(item), row_data))
                result_text_list.append(row_data)
            self.write_line(
                (
                    " " * (2 + (1 if len(str(length)) >
                           1 else 0) + len(str(length)))
                    if use_index
                    else ""
                )
                + A.D.list_to_string(
                    list(
                        map(
                            lambda item: i(item.caption),
                            list(
                                filter(
                                    lambda item: item.visible,
                                    field_list.get_list()[1:]
                                    if use_index
                                    else field_list.get_list(),
                                )
                            ),
                        )
                    ),
                    separator=" |",
                )
                + nl(ConsoleAppsApi.LINE, reversed=True)
            )
            for item in result_text_list:
                self.write_line(
                    item[0] + j(A.D.check(use_index, item[1:], item), " | ")
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
            title
            or js(
                (
                    self.parent.output.user.get_formatted_given_name(),
                    "введите логин, часть имени или другой поисковый запрос",
                )
            )
        )

    def template(self) -> dict:
        return self.parent.item_by_index(
            f"Выберите шаблон пользователя, введя индекс",
            A.R_U.template_list().data,
            lambda item, _: item.description,
        )


YES_VARIANTS: str = ["1", "yes", "ok", "да"]
YES_LABEL: str = (
    f" {A.CT.VISUAL.BULLET} *Да* - отправьте *{A.CT.VISUAL.NUMBER_SYMBOLS[1]}*"
)
NO_LABEL: str = (
    f" {A.CT.VISUAL.BULLET} *Нет* - отправьте *{A.CT.VISUAL.NUMBER_SYMBOLS[0]}*"
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
            else (
                data_input_timeout
                or A.S.get(A.CT_S.MOBILE_HELPER_USER_DATA_INPUT_TIMEOUT)
            )
        )

    @contextmanager
    def input_timeout(self, value: int | None) -> bool:
        data_input_timeout: int | None = self.data_input_timeout
        try:
            self.data_input_timeout = value
            yield True
        finally:
            self.data_input_timeout = data_input_timeout

    def input(
        self,
        caption: str | None = None,
        new_line: bool = True,
        check_function: Callable[[str], Any | None] | None = None,
    ) -> str:
        input_data: str | None = None
        while True:
            if new_line and caption is not None:
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
                        not A.D_C.empty(self.data_input_timeout)
                        and start_time > self.data_input_timeout
                    ):
                        self.stdin.interrupt_type = (
                            A.CT.MOBILE_HELPER.InteraptionTypes.TIMEOUT
                        )
                        return

            action_thread = Thread(target=internal_input)
            action_thread.start()
            action_thread.join()
            self.stdin.wait_for_data_input = False
            input_data = self.stdin.data
            if self.stdin.interrupt_type > 0:
                interrupt_type: int = self.stdin.interrupt_type
                self.stdin.set_default_state()
                raise InternalInterrupt(interrupt_type)
            self.stdin.set_default_state()
            if A.D.is_none(check_function):
                return input_data
            else:
                checked_input_data: str | None = check_function(input_data)
                if A.D.is_not_none(checked_input_data):
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
            yes_label = f" {A.CT.VISUAL.BULLET} {yes_label}"
        if no_label != NO_LABEL:
            no_label = f" {A.CT.VISUAL.BULLET} {no_label}"
        text = j(
            (
                nl(f"{text}?"),
                nl(ConsoleAppsApi.LINE),
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
            f"{caption}, отправив число", data, label_function, use_zero_index
        )

    def index(
        self,
        caption: str,
        data: list,
        label_function: Callable[[Any, int], str] | None = None,
        use_zero_index: bool = False,
    ) -> int:
        return super().index(
            j((ConsoleAppsApi.LINE, caption), nl()),
            data,
            label_function,
            use_zero_index,
        )

    def interrupt_for_new_command(self) -> None:
        self.stdin.interrupt_type = A.CT.MOBILE_HELPER.InteraptionTypes.NEW_COMMAND

    def polibase_person_by_any(
        self, value: str | None = None, title: str | None = None, use_all: bool = False
    ) -> list[PolibasePerson]:
        result: Result[list[PolibasePerson]] = A.R_P.persons_by_any(
            value or self.polibase_person_any(title)
        )
        label_function: Callable[[Any, int], str] | None = (
            (lambda item, _: "Все" if item is None else item.FullName)
            if len(result.data) > 1
            else None
        )
        if use_all and len(result.data) > 1:
            result.data.append(None)
        polibase_person: PolibasePerson = self.item_by_index(
            "Выберите пользователя, введя индекс", result.data, label_function
        )
        return result.data if polibase_person is None else [polibase_person]

    def wait_for_polibase_person_pin_input(self, action: Callable[[None], str]) -> str:
        return self.wait_for_input(A.CT.MOBILE_HELPER.POLIBASE_PERSON_PIN, action)

    def wait_for_polibase_person_card_registry_folder_input(
        self, action: Callable[[None], str]
    ) -> str:
        return self.wait_for_input(
            A.CT.MOBILE_HELPER.POLIBASE_PERSON_CARD_REGISTRY_FOLDER, action
        )

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
                f"Введите:\n {A.CT_V.BULLET} название папки с картами пациентов\n или\n {A.CT_V.BULLET} отсканируйте QR-код на папке реестра карт пациентов",
            )
        )

    def polibase_person_any(self, title: str | None = None) -> str:
        return self.wait_for_polibase_person_pin_input(
            lambda: self.input(
                title
                or f"Введите:\n {A.CT_V.BULLET} персональный номер\n {A.CT_V.BULLET} часть имени пациента\nили\n  отсканируйте штрих-код на карте пациента"
            )
        )


Groups = A.CT_AD.Groups


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
    # as_link: bool = False
    show_always: bool = False
    description: str | Callable[[None], str] | None = None
    order: int | None = None
    filter_function: Callable[[None], bool] | None = None
    help_text: Callable[[None], str] | None = None
    text_decoration_before: str | Callable[[None], str] | None = None
    text_decoration_after: str | Callable[[None], str] | None = None

    def __hash__(self) -> int:
        return hash(j(self.name_list, "|"))

    def set_visible(self, value: bool):
        self.visible = value
        return self

    def clone_as(
        self,
        name: str | None = None,
        title_and_label: str | Callable[[None],
                                        list[str] | None] | None = None,
        handler: Callable | None = None,
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


class Flags(Enum):
    CYCLIC: int = 1
    ADDRESS: int = 2
    ALL: int = 4
    ADDRESS_AS_LINK: int = 8
    FORCED: int = 16
    SILENCE: int = 32
    HELP: int = 64
    ONLY_RESULT: int = 128
    SILENCE_NO: int = 256
    SILENCE_YES: int = 512
    CLI: int = 1024


ALL_SYMBOL: str = "*"
ADDRESS_SYMBOL: str = ">"
LINK_SYMBOL: str = ">>"

FLAG_KEYWORDS: dict[str, Flags] = {
    "цикл": Flags.CYCLIC,
    "-c": Flags.CYCLIC,
    "-o": Flags.CYCLIC,
    "-о": Flags.CYCLIC,
    "to": Flags.ADDRESS,
    ADDRESS_SYMBOL: Flags.ADDRESS,
    "!": Flags.FORCED,
    "_": Flags.SILENCE,
    "_0": Flags.SILENCE_NO,
    "_1": Flags.SILENCE_YES,
    ALL_SYMBOL: Flags.ALL,
    "all": Flags.ALL,
    "все": Flags.ALL,
    "link": Flags.ADDRESS_AS_LINK,
    LINK_SYMBOL: Flags.ADDRESS_AS_LINK,
    "?": Flags.HELP,
}


def flag_name_list(value: Flags, all: bool = False) -> list[str]:
    result: list[str] = [
        item[0]
        for item in list(filter(lambda item: item[1] == value, FLAG_KEYWORDS.items()))
    ]
    return result if all else [result[0]]


def flag_name_string(value: Flags, all: bool = True) -> str:
    return js(("[", j(list(map(lambda item: b(item), flag_name_list(value, all))), j((" ", i("или"), " "))), "]"))


# "отмена", "стоп",
EXIT_KEYWORDS: list[str] = ["выход", "exit"]
FIND_KEYWORDS: list[str] = ["find", "поиск", "search", "найти"]
CREATE_KEYWORDS: list[str] = ["create", "создать", "+"]
CHECK_KEYWORDS: list[str] = ["check", "проверить"]
ADD_KEYWORDS: list[str] = ["add", "добавить", "+"]

ADM: list[Groups] = [Groups.Admin]


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


def format_given_name(
    session: Session, _: Output, name: str | None = None
) -> str | None:
    if A.D_C.empty(session.login):
        return None
    return b(name or session.user_given_name)


class MobileHelper:
    PIH_KEYWORDS: tuple[str] = (PIH.NAME, PIH.NAME_ALT)
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
            [item.title_and_label] if isinstance(
                item.title_and_label, str) else item.title_and_label,
            lambda: self.study_course_handler(
                index, item_list, content_list, wiki_location=wiki_location
            ),
            wait_for_input=False,
        )

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
        resource: ResourceStatus | None = A.R_R.get_resource_status(
            A.CT_R_D.POLIBASE)
        return A.D.check_not_none(
            resource, lambda: A.D_F.yes_no(resource.accessable, True), ""
        )

    @property
    def is_person_card_registry_folder(self) -> bool:
        name: str | None = self.arg()
        if A.D.is_none(name):
            return True
        return A.CR.is_person_card_registry_folder(name)

    @property
    def arg_len(self) -> int:
        return 0 if A.D.is_none(self.arg_list) else len(self.arg_list)

    @property
    def none_command(self) -> bool:
        return A.D.is_none(self.current_command)

    def ws_ping_handler(self) -> None:
        with self.output.make_loading():
            self.write_line(
                js(
                    (
                        "Доступен:",
                        A.D_F.yes_no(
                            A.C_R.accessibility_by_ping(
                                self.arg()
                                or self.input.input("Введите название хоста")
                            ),
                        ),
                    )
                )
            )

    def __init__(self, pih: PIH, stdin: Stdin):
        self.pih: PIH = pih
        self.console_apps_api: ConsoleAppsApi = ConsoleAppsApi(pih)
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

        def get_formatted_given_name(name: str | None = None) -> str:
            return format_given_name(self.session, self.output, name)

        self.output.user.get_formatted_given_name = get_formatted_given_name
        #
        #additional_nodes: list[CommandNode] = []
        self.study_node: CommandNode = self.create_command_link(
            "@study", "study", ["Обучение"], None, False, "🎓 "
        )

        #######################
        INFINITY_STUDY_COURCE_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "telephone_collection",
                "Список внутренних телефонов колл-центра",
                [
                    HelpContent(
                        None,
                        f"Вам нужно знать ваш внутренний телефон для входа в программу *инфинити*.\nПомещение *колл-центра*:\n{A.CT.VISUAL.BULLET} Дальний слева: *303*\n{A.CT.VISUAL.BULLET} Дальний справа: *305*\n{A.CT.VISUAL.BULLET} Ближний справа: *306*\n\n*Регистратура поликлиники*:\n{A.CT.VISUAL.BULLET} левый: *121*\n{A.CT.VISUAL.BULLET} правый: *120*\n\n*Регистратура больницы*:\n*240*",
                    )
                ],
            ),
            HelpContentHolder(
                "setup",
                "Настройка при первом входе",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.INFINITY_A.CT_S,
                        '*Важно*: в поле "Имя" нужно внести внутренний номер телефона, на которым Вы принимаете звонки',
                    )
                ],
            ),
            HelpContentHolder(
                "missed_calls",
                "Просмотр пропущенных звонков",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.INFINITY_OPEN_MISSED_CALLS
                    )
                ],
            ),
            HelpContentHolder(
                "infinity_status",
                "Установка статуса",
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
                "Как войти в общий аккаунт в браузере Google Chrome",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.CALL_CENTRE_BROWSER_LOG_IN,
                        f"Если коротко: включить синхронизацию при входе в общий аккаунт:\n {A.CT.VISUAL.BULLET} Логин: *{A.CT.RECEPTION_EMAIL_LOGIN}*\n {A.CT.VISUAL.BULLET} Пароль: *QmF1ZA8n*",
                    )
                ],
            ),
            HelpContentHolder(
                "_ccbp",
                "О панели вкладок",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.CALL_CENTRE_BROWSER_BOOKMARKS
                    )
                ],
            ),
        ]
        CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION: dict[CommandNode, None] = {
        }
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
                "card_registry_introduction",
                "О курсе",
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
                "card_registry_about_card",
                "О картах пациентов",
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
                "card_registry_folder_name",
                "Наклейка с именем папки",
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
                "card_registry_barcode",
                "Штрих-код на карте пациента",
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
                "card_registry_tools",
                "Инструментарий",
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
                "card_registry_add_bar_code",
                "Добавление штрих-кода нового формата",
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
                "card_registry_add_person",
                "Добавление карты пациента в папку",
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
                "polibase reboot",
                "перезапустить Полибейс",
                [HelpVideoContent(
                    lambda: MEDIA_CONTENT.VIDEO.POLIBASE_RESTART)],
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
        holter_study_course_help_content_image_list: list[HelpImageContent] = [
        ]
        HOLTER_STUDY_COURSE_CONTENT_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "introduce",
                "Вступительное видео",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_INTRODUCTION, title=""
                    )
                ],
            ),
            HelpContentHolder(
                "nn1",
                "Внесение данных пациента",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_ADD_PATIENT_TO_VALENTA,
                        title="",
                    )
                ],
            ),
            HelpContentHolder(
                "nn2",
                "Распечатывание дневника пациента",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_PRINT_PATIENT_JOURNAL,
                        title="",
                    )
                ],
            ),
            HelpContentHolder(
                "nn3",
                "Установка аппарата Холтера",
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
                i("Памятка: Установка датчиков, карты и аккумулятора"),
                holter_study_course_help_content_image_list,
            ),
            HelpContentHolder(
                "nn5",
                i("Памятка: Расположение датчиков на теле пациента"),
                [
                    HelpImageContent(
                        lambda: MEDIA_CONTENT.IMAGE.HOLTER_DETECTORS_MAP, title=""
                    )
                ],
            ),
            HelpContentHolder(
                "nn6",
                "Снятие аппарата холтера",
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
                "Выгрузка исследования на компьютер",
                [
                    HelpVideoContent(
                        lambda: MEDIA_CONTENT.VIDEO.HOLTER_LOAD_OUT_DATA, title=""
                    )
                ],
            ),
        ]
        HOLTER_STUDY_COURSE_COLLECTION: dict[CommandNode, None] = {}
        holter_study_course_node: CommandNode = CommandNode(
            ["holter"],
            ['Обучающий курс "Аппарат Холтера"'],
            lambda: self.study_course_handler(
                None,
                HOLTER_STUDY_COURSE_COLLECTION,
                HOLTER_STUDY_COURSE_CONTENT_LIST,
                lambda: MEDIA_CONTENT.IMAGE.HOLTER_WIKI_LOCATION,
            ),
            text=lambda: f"В данном курсе, {self.user_given_name}, Вы научитесь тому, как работать с аппаратом Холтера:\n\n{A.CT.VISUAL.BULLET} Вносить данные пациента в программу;\n {A.CT.VISUAL.BULLET} Распечатывать журнал пациента;\n{A.CT.VISUAL.BULLET} Надевать датчики на тело пациента;\n{A.CT.VISUAL.BULLET} Снимать датчики;\n{A.CT.VISUAL.BULLET} Выгружать данные исследования на компьютер",
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
                "перезагрузить" +
                (" компьютер" if self.in_choice_command else ""),
            ],
            self.reboot_workstation_handler,
            ADM,
            filter_function=lambda: not self.is_all or self.in_main_menu,
        )
        reboot_all_workstations_node: CommandNode = CommandNode(
            reboot_workstation_node.name_list,
            lambda: [
                "перезагрузка всех компьютеров",
                "перезагрузить все" +
                (" компьютеры" if self.in_choice_command else ""),
            ],
            self.reboot_workstation_handler,
            ADM,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_name_string(Flags.ALL),
        )
        shutdown_workstation_node: CommandNode = CommandNode(
            ["shutdown", "выключ^ить"],
            lambda: [
                "выключение компьютера",
                "выключить" + (" компьютер" if self.is_all else ""),
            ],
            self.shutdown_workstation_handler,
            ADM,
            filter_function=lambda: not self.is_all or self.in_main_menu,
        )
        shutdown_all_workstations_node: CommandNode = CommandNode(
            shutdown_workstation_node.name_list,
            lambda: [
                "выключение всех компьютеров",
                "выключить все" + (" компьютеры" if self.is_all else ""),
            ],
            self.shutdown_workstation_handler,
            ADM,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_name_string(Flags.ALL),
        )
        find_workstation_node: CommandNode = CommandNode(
            FIND_KEYWORDS,
            lambda: [
                "Поиск компьютера",
                "Найти" + (" компьютер" if self.in_choice_command else ""),
            ],
            self.find_workstation_handler,
            filter_function=lambda: not self.is_all or self.in_main_menu,
        )
        find_all_workstations_node: CommandNode = CommandNode(
            FIND_KEYWORDS,
            lambda: [
                "Весь список компьютеров",
                "Весь список" +
                (" компьютеров" if self.in_choice_command else ""),
            ],
            self.find_workstation_handler,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_name_string(Flags.ALL),
        )
        msg_to_node: CommandNode = CommandNode(
            ["msg", "сообщение", "message"],
            lambda: [
                "Отправка сообщения пользователю",
                "Отправить сообщение"
                + (" пользователю" if self.in_choice_command else ""),
            ],
            lambda: self.send_workstation_message_handler(False),
            ADM,
            filter_function=lambda: not self.is_all,
        )
        msg_to_all_node: CommandNode = CommandNode(
            msg_to_node.name_list,
            [
                "Отправка сообщения всем пользователям",
                "Отправить сообщение всем пользователям",
            ],
            lambda: self.send_workstation_message_handler(True),
            ADM,
            help_text=lambda: flag_name_string(Flags.ALL),
            filter_function=lambda: self.is_all,
        )
        check_ws_node: CommandNode = CommandNode(
            CHECK_KEYWORDS,
            lambda: [
                "Список отслеживаемых компьютеров",
                ("Проверить " if self.in_choice_command else "") +
                "отслеживаемые компьютеры на доступность",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.WS], False
            ),
            ADM,
            filter_function=lambda: not self.is_all or self.in_main_menu,
        )
        check_ws_all_node: CommandNode = CommandNode(
            CHECK_KEYWORDS,
            lambda: [
                "Проверить все компьютеры на доступность",
                "все компьютеры на доступность",
            ],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.WS], True
            ),
            ADM,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_name_string(Flags.ALL),
        )
        process_kill_node: CommandNode = CommandNode(
            ["kill", "завершить"],
            ["Завершение процесса", "Завершить процесс"],
            lambda: self.console_apps_api.process_kill(
                self.arg(), self.arg(1)),
            filter_function=lambda: not self.is_all,
        )
        disks_information_node: CommandNode = CommandNode(
            ["disk^s", "диски"],
            ["Получение информации о дисках", "Получить информацию о дисках"],
            lambda: self.console_apps_api.disks_information(self.arg()),
            filter_function=lambda: not self.is_all,
        )
        WORKSTATION_MENU: list[CommandNode] = [
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
                    + (" компьютеру" if self.in_choice_command else ""),
                ]
            ),
            msg_to_all_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщения всем компьютерам",
                    "Отправить сообщение всем"
                    + (" компьютерам" if self.in_choice_command else ""),
                ],
            ),
            disks_information_node,
            check_ws_node.clone_as(
                None,
                lambda: [
                    "Проверка отслеживаемых компьютеров на доступность",
                    "Проверить отслеживаемыe компьютеры на доступность"
                    if self.in_choice_command
                    else "Проверить отслеживаемыe на доступность",
                ],
            ),
            check_ws_all_node.clone_as(
                None,
                lambda: [
                    "Проверка всех компьютеров на доступность ",
                    "Проверить все "
                    + (" компьютеры " if self.in_choice_command else "")
                    + "на доступность",
                ],
            ),
        ]

        #
        create_note_node: CommandNode = CommandNode(
            CREATE_KEYWORDS,
            lambda: [
                "Создание заметки",
                "Создать" + (" заметку" if self.in_choice_command else ""),
            ],
            self.create_note_handler,
        )
        self.show_note_node: CommandNode = CommandNode(
            ["show", "показать"],
            lambda: [
                "Показать заметку",
                "Показать" + (" заметку" if self.in_choice_command else ""),
            ],
            lambda: self.show_note_handler(False),
            help_text=lambda: j((" ( ", "Название заметки", " )"))
        )
        NOTES_MENU: list[CommandNode] = [create_note_node, self.show_note_node]
        #
        # additional_nodes.append(msg_to_node)
        # additional_nodes.append(msg_to_all_node)
        #######################
        # ct_indication_value_node: CommandNode = CommandNode(
        #    "ict", "Отправка показаний КТ", self.register_ct_indications_handler, allowed_groups=ADM + [Groups.RD, Groups.IndicationWatcher])
        # mri_indication_value_node: CommandNode = CommandNode(
        #    "imri", "Отправка показаний МРТ", self.under_construction_handler, allowed_groups=ADM + [Groups.RD, Groups.IndicationWatcher])
        INDICATION_MENU: list[CommandNode] = [
            # ct_indication_value_node,
            # mri_indication_value_node
        ]
        #######################
        callcentre_unit_node: CommandNode = CommandNode(
            ["callcentre", "колл-центр"],
            ["Колл-центр"],
            lambda: self.menu_handler(CALL_CENTRE_MENU),
            text=f"Алло, алло... С этих слов начинается общение наших клиентов c колцентром. Работники коллцентра принимают звонки и работают с запросами от клиентов и в этом им помогает:\n\n{A.CT.VISUAL.BULLET} программа *Инфинити*, отвечающая за звонки\n{A.CT.VISUAL.BULLET} программа *Полибейс*, в которой заноситься информация о клиенте\n{A.CT.VISUAL.BULLET} браузер *Google Chrome*, с набором ресурсов\n\nНиже представлены курсы по всем трем программам.",
        )
        it_unit_node: CommandNode = CommandNode(
            ["it", "ит"],
            ["ИТ отдел"],
            lambda: self.menu_handler(IT_MENU),
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
        HR_UNIT_MENU: list[CommandNode] = [my_time_tracking_report_node]
        # additional_nodes.append(my_time_tracking_report_node)
        hr_unit_node: CommandNode = CommandNode(
            ["hr", "кадр^ов"],
            ["Отдел кадров"],
            lambda: self.menu_handler(HR_UNIT_MENU),
            text=lambda: f"Руководитель: {b(A.R.get_first_item(A.R.filter(A.R_U.by_job_position(A.CT_AD.JobPisitions.HR), lambda item: not item.samAccountName.startswith(A.CT_AD.TEMPLATED_USER_SERACH_TEMPLATE[0]) and not item.samAccountName.endswith(A.CT_AD.TEMPLATED_USER_SERACH_TEMPLATE[-1]))).name)}.\nТелефон: {b('706')}.",
        )
        UNIT_MENU: list[CommandNode] = [
            it_unit_node,
            callcentre_unit_node,
            hr_unit_node,
        ]
        #additional_nodes += UNIT_MENU
        #######################
        robocopy_node: CommandNode = CommandNode(
            ["rb^k", "robocopy"], [
                "Запуск Robocopy-задания"], self.robocopy_job_run_handler
        )
        polibase_backup_node: CommandNode = CommandNode(
            ["pb^k"],
            ["Создание бекапа базы данных Polibase",
                "Создать бекап базы данных Polibase"],
            self.create_polibase_db_backup_handler,
        )
        BACKUP_MENU: list[CommandNode] = [robocopy_node, polibase_backup_node]
        run_command_node: CommandNode = CommandNode(
            "run|выполнить",
            "Выполнение команды|Выполнить команду",
            self.run_commnad_handler,
            ADM,
        )
        #######################
        polibase_person_information_node: CommandNode = CommandNode(
            ["info^rmation", "инфо^рмация"],
            ["Информация о пациенте", "Информация" +
                (" о пациенте" if self.in_choice_command else ""), ],
            self.polibase_person_information_handler,
        )
        polibase_person_find_card_registry_folder_node: CommandNode = CommandNode(
            FIND_KEYWORDS,
            [
                "Поиск карты пациента",
                "Найти карту" +
                (" пациента" if self.in_choice_command else ""),
            ],
            self.polibase_person_card_registry_folder_find_handler,
            filter_function=lambda: (not self.is_all or self.in_main_menu)
            and A.D_C.empty(get_polibase_person_card_registry_folder_name()),
        )

        check_email_node: CommandNode = CommandNode(
            ["email", "почт^ы", "mail"],
            ["Проверка адресса электронной почты",
                "Проверить адресс электронной почты" if self.in_choice_command else "Адресс электронной почты"],
            lambda: self.check_email_address_handler(),
        )

        check_valenta_node: CommandNode = CommandNode(
            ["valenta", "валент^у"],
            ["Проверка наличия новых исследований в Валенте",
                "Проверить наличие новых исследований" if self.in_choice_command else "Наличие новых исследований в Валенте"],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.VALENTA]
            ),
        )

        check_printers_node: CommandNode = CommandNode(
            ["printer^s", "принтер^ы"],
            ["Проверка принтеров",
                "Проверить принтеры" if self.in_choice_command else "Принтеры"],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.PRINTERS]
            ),
        )

        check_email_node_polibase_person: CommandNode = check_email_node.clone_as(
            None,
            [
                "Проверка адресса электронной почты пациента",
                "Проверить адресс электронной почты пациента",
            ],
            lambda: self.check_email_address_handler(
                only_for_polibase_person=True),
        )

        POLIBASE_PERSON_MENU: list[CommandNode] = [
            polibase_person_information_node,
            polibase_person_find_card_registry_folder_node,
            check_email_node_polibase_person,
        ]
        #######################
        create_user_node: CommandNode = CommandNode(
            CREATE_KEYWORDS,
            lambda: [
                "Создание пользователя",
                "Создать" +
                (" пользователя" if self.in_choice_command else ""),
            ],
            self.create_user_handler,
            ADM,
            filter_function=lambda: not self.is_all
            # visible=False,
        )
        find_user_node: CommandNode = CommandNode(
            FIND_KEYWORDS,
            lambda: [
                "Поиск пользователя",
                "Найти" + (" пользователя" if self.in_choice_command else ""),
            ],
            self.find_user_handler,
            filter_function=lambda: not A.D_C.decimal(self.arg())
            and (not self.is_all or self.in_choice_command),
        )
        change_user_telephone_number_node: CommandNode = CommandNode(
            ["phone", "телефоне"],
            lambda: [
                "Изменение телефонного номера пользователя",
                "Изменить телефонный номер"
                + (" пользователя" if self.in_main_menu else ""),
            ],
            lambda: self.user_property_set_handler(0),
            ADM,
            filter_function=lambda: not self.is_all or self.in_choice_command,
        )
        change_all_user_telephone_number_node: CommandNode = CommandNode(
            ["phone", "телефоне"],
            [
                "Редактирование всех телефонных номеров",
                "Редактировать все телефонные номера"
                + (" пользователей" if self.in_choice_command else ""),
            ],
            lambda: self.user_property_set_handler(0),
            ADM,
            filter_function=lambda: self.is_all,
            help_text=lambda: flag_name_string(Flags.ALL),
        )
        change_user_password_node: CommandNode = CommandNode(
            ["password", "пароль"],
            [
                "Изменение пароля пользователя",
                "Изменить пароль" +
                (" пользователя" if self.in_choice_command else ""),
            ],
            lambda: self.user_property_set_handler(1),
            ADM,
            filter_function=lambda: not self.is_all,
        )
        change_user_status_node: CommandNode = CommandNode(
            ["status", "статус"],
            [
                "Изменение статуса пользователя",
                "Изменить статус" +
                (" пользователя" if self.in_choice_command else ""),
            ],
            lambda: self.user_property_set_handler(2),
            ADM,
            filter_function=lambda: not self.is_all,
        )
        USER_MENU: list[CommandNode] = [
            create_user_node,
            find_user_node,
            change_user_telephone_number_node,
            change_all_user_telephone_number_node,
            change_user_password_node,
            change_user_status_node,
            msg_to_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщение пользователю",
                    "Отправить сообщение" +
                    (" пользователю" if self.is_all else ""),
                ],
            ),
            msg_to_all_node.clone_as(
                title_and_label=lambda: [
                    "Отправка сообщения всем",
                    "Отправить сообщение всем"
                    + (" пользователям" if self.is_all else ""),
                ],
            ),
        ]
        #######################
        check_resources_node: CommandNode = CommandNode(
            ["resource^s", "ресурс^ы"],
            ["Проверка основных ресурсов", "Основные ресурсы"],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.RESOURCES]
            ),
            ADM + [Groups.RD, Groups.IndicationWatcher],
        )
        check_indications_node: CommandNode = CommandNode(
            ["indication^s", "показан^ия"],
            ["Показания отделения лучевой диагностики",
                "Показания отделения лучевой диагностики"],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.INDICATIONS]
            ),
            ADM + [Groups.RD, Groups.IndicationWatcher],
        )
        check_backups_node: CommandNode = CommandNode(
            ["backup^s", "бекап^ы", "rbk"],
            ["Список Robocopy-заданий", "Robocopy-задания"],
            lambda: self.check_resources_and_indications_handler(
                [CheckableSections.BACKUPS]
            ),
            ADM,
        )
        check_all_node: CommandNode = self.create_command_link(
            #list(map(lambda item: j(("@", item)), CHECK_KEYWORDS)),
            [""],
            js((CHECK_KEYWORDS[0], ALL_SYMBOL)),
            lambda: [
                None, "Проверить все компоненты" if self.in_choice_command else "Все компоненты"],
            None,
            True,
        )
        check_all_node.help_text = lambda: flag_name_string(Flags.ALL)
        CHECK_MENU: list[CommandNode] = [
            check_all_node,
            check_resources_node,
            check_ws_node,
            check_indications_node,
            check_backups_node,
            check_email_node,
            check_valenta_node,
            check_printers_node,
        ]
        # additional_nodes += CHECK_MENU
        # check_chiller_indications_node: CommandNode = CommandNode(
        #    "indication^s|показан^ия", "Проверка показаний отделения лучевой диагностики|Показания отделения лучевой диагностики", lambda: self.check_resources_and_indications_handler([CheckableSections.INDICATIONS]), ADM + [Groups.RD, Groups.IndicationWatcher])

        show_all_indications_node = check_indications_node.clone_as(
            "indication^s|показан^ия",
            "Актуальные значения|Актуальные значения показаний",
        )
        # INDICATION_MENU.append(show_all_indications_node)
        #######################
        polibase_restart_node: CommandNode = CommandNode(
            ["restart", "перезапустить"],
            ["Перезапуск Polibase", "Перезапустить Polibase"],
            self.console_apps_api.polibase_restart,
        )
        polibase_close_node: CommandNode = CommandNode(
            ["close", "закрыть"],
            lambda: ["Закрытие всех клиентских программ",
                     "Закрыть все клиентские программы"]
            if self.is_all
            else ["Закрытие клиентской программы Polibase", "Закрыть клиентскую программу Polibase"],
            lambda: self.console_apps_api.polibase_client_program_close(
                self.arg(), True
            )
            if self.is_all
            else self.console_apps_api.polibase_client_program_close(self.arg()),
        )
        POLIBASE_MENU: list[CommandNode] = [
            polibase_restart_node, polibase_close_node]

        def get_polibase_person_card_registry_folder_name() -> str:
            arg: str = self.arg(default_value="")
            return (
                ""
                if A.D_C.empty(arg) or not A.C_P.person_card_registry_folder(arg)
                else f' "{A.D_F.polibase_person_card_registry_folder(arg)}"'
            )

        #######################
        infinity_study_course_node: CommandNode = CommandNode(
            ["infinity", "инфинити"],
            ['Обучающий курс "Регистартор и Оператор колл-центра: инфинити"'],
            lambda: self.study_course_handler(
                None,
                INFINITY_STUDY_COURSE_COLLECTION,
                INFINITY_STUDY_COURCE_CONTENT_LIST,
                lambda: MEDIA_CONTENT.IMAGE.INFINITY_WIKI_LOCATION,
            ),
        )
        card_registry_study_course_node: CommandNode = CommandNode(
            "card",
            'Обучающий курс "Реестр карт пациентов"',
            lambda: self.study_course_handler(
                None,
                CARD_REGISTRY_STUDY_COURSE_COLLECTION,
                CARD_REGISTRY_STUDY_COURCE_CONTENT_LIST,
                lambda: MEDIA_CONTENT.IMAGE.CARD_REGISTRY_WIKI_LOCATION,
            ),
            filter_function=lambda: A.D_C.empty(
                get_polibase_person_card_registry_folder_name()
            ),
        )
        basic_polibase_study_course_node: CommandNode = CommandNode(
            ["polibase"],
            ['Обучающий курс "Полибейс - базовый уровень"'],
            self.under_construction_handler,
        )  # lambda: self.study_course_handler(None, POLIBASE_HELP_COLLECTION, POLIBASE_HELP_CONTENT_LIST))
        callcentre_browser_study_course_node: CommandNode = CommandNode(
            ["cc_browser"],
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
                [
                    "Создание QR кода для папки карт пациентов",
                    "Создать QR код для папки карт пациентов",
                ],
                self.create_qr_code_for_card_registry_folder_handler,
                ADM + [Groups.CardRegistry],
                filter_function=lambda: (not self.is_all or self.in_main_menu)
                and self.is_person_card_registry_folder,
            )
        )
        polibase_persons_by_card_registry_folder_name_node: CommandNode = CommandNode(
            ["list"] + flag_name_list(Flags.ALL, True),
            lambda: [
                f"Список карт пациентов в папке{get_polibase_person_card_registry_folder_name()}"
            ],
            self.polibase_persons_by_card_registry_folder_handler,
            filter_function=lambda: self.is_person_card_registry_folder,
        )

        def polibase_person_add_to_card_registry_folder_title_and_label() -> list[str]:
            value: str = (
                f"пациента в папку{get_polibase_person_card_registry_folder_name()}"
            )
            return [j(("Добавление карты", value)), js(("Добавить карту", value))]

        def polibase_person_sort_card_registry_folder_title_and_label() -> str:
            value: str = get_polibase_person_card_registry_folder_name()
            if not A.D_C.empty(value):
                value = f" {value}"
            return f"Сортировка карт папки{value}|Сортировать карты в папке{value}"

        polibase_person_card_add_to_card_registry_folder_node: CommandNode = CommandNode(
            ADD_KEYWORDS,
            polibase_person_add_to_card_registry_folder_title_and_label,
            self.add_polibase_person_to_card_registry_folder_handler,
            ADM + [Groups.CardRegistry],
            text="Добавляет карту пациента в папку реестра",
            help_text=lambda: f" {i('название папки')} {i('запрос для поиска пациента')}.\nНапример, {self.current_pih_keyword} + п1к {A.CT.TEST.PIN}",
            filter_function=lambda: not self.is_all or self.in_main_menu,
        )

        def polibase_person_card_registry_folder_register_title_and_label() -> (
            list[str]
        ):
            value: str = get_polibase_person_card_registry_folder_name()
            return [
                j(("Регистрация папки", value, " в реестре карт")),
                j(("Зарегистрировать папку", value, " в реестре карт" if self.in_choice_command else "")),
            ]

        polibase_person_card_registry_folder_register_node: CommandNode = CommandNode(
            ["register"],
            polibase_person_card_registry_folder_register_title_and_label,
            self.register_card_registry_folder_handler,
            ADM,
            filter_function=lambda: (not self.is_all or self.in_main_menu)
            and self.is_person_card_registry_folder,
        )

        polibase_person_card_registry_folder_statistics_node: CommandNode = CommandNode(
            ["statistics"],
            lambda: [
                "Статистика реестра карт",
                "Статистика" +
                (" реестра карт" if self.in_choice_command else ""),
            ],
            self.get_card_registry_statistics_handler,
            ADM,
            filter_function=lambda: (not self.is_all or self.in_main_menu),
        )

        # sort_card_registry_folder_node: CommandNode = CommandNode(
        # "sort|сортиров^ать", polibase_person_sort_card_registry_folder_title_and_label, self.sort_card_registry_folder_handler, ADM + [Groups.CardRegistry])
        CARD_REGISTRY_MENU: list[CommandNode] = [
            # card_registry_study_course_node.clone_as(
            # None, "Обучающий курс \"Реестр карт пациентов\""),
            polibase_persons_by_card_registry_folder_name_node,
            polibase_person_card_add_to_card_registry_folder_node,
            polibase_person_find_card_registry_folder_node,
            polibase_person_card_registry_folder_qr_code_create_node,
            polibase_person_card_registry_folder_register_node,
            polibase_person_card_registry_folder_statistics_node
            # sort_card_registry_folder_node
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
                "study_wiki_location", "Обучение в Вики", WIKI_BASE_CONTENT_LIST
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
                    + b(A.CT.WIKI_SITE_ADDRESS)
                    + "_",
                    False,
                )
            ],
        )
        IT_HELP_CONTENT_HOLDER_LIST: list[HelpContentHolder] = [
            HelpContentHolder(
                "request_help",
                "Как создать запрос на помощь",
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
        # additional_nodes.append(print_node)
        ####
        self.about_it_node: CommandNode = CommandNode(
            ["about_it"], ["О ИТ отделе"], self.about_it_handler
        )
        IT_HELP_COLLECTION: dict[CommandNode, None] = {}
        IT_HELP_MENU: list[CommandNode] = []
        for index, item in enumerate(IT_HELP_CONTENT_HOLDER_LIST):
            IT_HELP_MENU.append(
                self.create_study_course_item(
                    -1, item, IT_HELP_COLLECTION, IT_HELP_CONTENT_HOLDER_LIST
                )
            )
            IT_HELP_COLLECTION[IT_HELP_MENU[index]] = None
        IT_MENU: list[CommandNode] = [
            self.about_it_node,
            self.study_node.clone_as(title_and_label=["Обучение"]),
        ]
        IT_MENU += IT_HELP_MENU
        self.wiki_node = IT_HELP_MENU[-1]
        self.wiki_node.show_always = True
        #additional_nodes += IT_HELP_MENU
        #additional_nodes += [self.about_it_node]
        #######################
        CALL_CENTRE_MENU: list[CommandNode] = [
            infinity_study_course_node,
            callcentre_browser_study_course_node,
            self.wiki_node,
        ]

        self.main_menu_node: CommandNode = CommandNode(
            ["menu", "меню"],
            ["Меню"],
            self.main_menu_handler,
            text=lambda: b("Все команды:") if self.is_all else b(
                "Список разделов:"),
        )
        #######################

        # additional_nodes.append(self.all_commands_node)
        #######################
        self.address_node: CommandNode = self.create_command_link(
            f"to|{ADDRESS_SYMBOL}",
            ADDRESS_SYMBOL,
            i("Адресовать команду"),
            ADM,
            True,
        )
        self.address_node.order = 2
        # additional_nodes.append(self.address_node)
        #######################
        self.address_as_link_node: CommandNode = self.create_command_link(
            f"link|{LINK_SYMBOL}",
            LINK_SYMBOL,
            i("Адресовать ссылку на команду"),
            ADM,
            True,
        )
        self.address_as_link_node.order = 3
        # additional_nodes.append(self.address_as_link_node)
        #######################
        # additional_nodes.append(about_pih_node)
        #######NEW_VERSION##########
        self.all_commands_node: CommandNode = self.create_command_link(
            j(("@", ALL_SYMBOL)), ALL_SYMBOL, [i("Все команды")], None, True
        )
        self.all_commands_node.order = 1
        self.all_commands_node.filter_function = lambda: not self.in_choice_command

        about_pih_node: CommandNode = CommandNode(
            ["about", "o"],
            [i("О PIH")],
            text_decoration_after=lambda: ""
            if self.helped
            else nl("...", reversed=True),
            text=lambda: f"Я бот-помощник для решения Ваших задач. Моё имя составлено из первых букв нашей организации:\n   {A.CT_V.BULLET} {b('P')} acific {b('I')} nternational {b('H')} ospital\nили\n   {A.CT_V.BULLET} {b('П')} асифик {b('И')} нтернейшнл {b('Х')} оспитал.\n\n{i('Автор')}: {i(b('Караченцев Никита Александрович'))} \n{i('Версия')}: {b(MIO.VERSION)}",
            show_in_main_menu=True,
            wait_for_input=False,
            show_always=True,
            order=4,
        )
        self.exit_node: CommandNode = CommandNode(
            EXIT_KEYWORDS,
            [None, i("Выход")],
            self.session.exit,
            text_decoration_after=lambda: ""
            if self.in_main_menu and not self.helped
            else nl("...", reversed=True),
            show_in_main_menu=True,
            wait_for_input=False,
            show_always=True,
            # as_link=True,
        )
        self.exit_node.order = 0
        # additional_nodes.append(self.exit_node)
        #######################
        self.ws_node: CommandNode = CommandNode(
            ["ws", "комп^ьютер"],
            ["Компьютер"],
            lambda: self.menu_handler(WORKSTATION_MENU),
            text_decoration_before="🖥️ ",
            show_in_main_menu=True,
            help_text=lambda: flag_name_string(
                Flags.ALL) if self.is_all else "",
            text="Наши компьютеры",
        )
        self.user_node: CommandNode = CommandNode(
            ["user^s", "пользовател^ь"],
            ["Пользователь"],
            lambda: self.menu_handler(USER_MENU),
            text_decoration_before="👤 ",
            show_in_main_menu=True,
            text="Наши пользователи",
        )
        patient_node: CommandNode = CommandNode(
            ["patient", "пациент"],
            ["Пациент"],
            lambda: self.menu_handler(POLIBASE_PERSON_MENU),
            text_decoration_before="🤒 ",
            show_in_main_menu=True,
            text="Наши пациенты",
        )
        check_node: CommandNode = CommandNode(
            CHECK_KEYWORDS,
            lambda: ["Проверка всех компонентов системы"]
            if self.is_all
            else ["Проверка", "Проверить"],
            lambda: self.check_resources_and_indications_handler(
                None, self.is_all)
            if self.is_all
            else self.menu_handler(CHECK_MENU),
            ADM + [Groups.RD, Groups.IndicationWatcher],
            text_decoration_before="☑️ ",
            show_in_main_menu=True,
        )
        polibase_node: CommandNode = CommandNode(
            ["polibase", "полибейс"],
            lambda: [
                js(("Полибейс", MobileHelper.polibase_status())), "Полибейс"],
            lambda: self.menu_handler(POLIBASE_MENU),
            text_decoration_before=lambda: j(
                (MobileHelper.polibase_status(), " ")),
            show_in_main_menu=True,
        )
        #######################
        self.command_node_tree = {
            msg_to_node: None,
            msg_to_all_node: None,
            self.all_commands_node: None,
            about_pih_node: None,
            self.study_node: None,
            self.main_menu_node: None,
            self.user_node: None,
            CommandNode(["user", "пользователь"], [""]): A.D.to_dict(USER_MENU),
            self.ws_node: None,
            CommandNode(["ws", "комп^ьютер"], [""]): A.D.to_dict(WORKSTATION_MENU),
            CommandNode(["study", "обучение"], [""]): {
                self.wiki_node: None,
                infinity_study_course_node: None,
                basic_polibase_study_course_node: None,
                holter_study_course_node: None,
                # card_registry_study_course_node: None,
                callcentre_browser_study_course_node: None,
            },
            CommandNode(
                ["registry", "реестр"],
                ["Реестр"],
                ADM + [Groups.CardRegistry],
                text_decoration_before="📂 ",
                show_in_main_menu=True,
            ): CommandNode(
                ["card", "карт", ""],
                ["карт пациентов"],
                lambda: self.menu_handler(CARD_REGISTRY_MENU),
                text=lambda: self.get_polibase_person_card_place_label(
                    self.arg(), display_only_card_folder=True
                ),
            ),
            CommandNode(
                ["registry", "реестр"],
                [""],
                allowed_groups=ADM + [Groups.CardRegistry],
            ): {CommandNode(["card", "карт", ""], [""]): A.D.to_dict(CARD_REGISTRY_MENU)},
            # CommandNode(FIND_KEYWORDS, [""]): {
            #    polibase_person_find_card_registry_folder_node.clone_as(
            #        ["patient", "пациент^а"],
            #        ["Поиск карты пациента", "Найти карту пациента"],
            #        filter_function=lambda: not self.none_command
            #    ): None,
            # },
            CommandNode(
                ["note^s", "заметк^и"],
                lambda: [js(("Заметка", "\"", self.arg(), "\"")), "Заметки"]
                if self.arg_len == 1
                else ["Заметки"],
                lambda: self.show_note_handler(True)
                if self.arg_len == 1
                else self.menu_handler(NOTES_MENU),
                text_decoration_before="📝 ",
                show_in_main_menu=True,
                help_text=lambda: j((" ( ", "Название заметки", " )"))
            ): None,
            CommandNode(["note^s", "заметк^и"], [""]): A.D.to_dict(NOTES_MENU),
            self.create_command_link(
                "@help", "help", ["Помощь"], None, False, text_decoration_before="❔ "
            ): None,
            CommandNode(
                ["help", "помощь"], [js(("Помощь", A.CT.VISUAL.ARROW))]
            ): {
                CommandNode(
                    ["infinity", "инфинити"],
                    [
                        js(("Инфинити", A.CT.VISUAL.ARROW)),
                    ],
                ): INFINITY_STUDY_COURSE_COLLECTION,
                CommandNode(
                    ["polibase", "полибейс"],
                    js(("Полибейс", A.CT.VISUAL.ARROW)),
                ): POLIBASE_HELP_COLLECTION,
                CommandNode(
                    ["holter", "холтер"],
                    [
                        js(("Аппарат Холтера", A.CT.VISUAL.ARROW)),
                    ],
                ): HOLTER_STUDY_COURSE_COLLECTION,
                CommandNode(
                    ["card_registry", "реестр карт"],
                    [
                        js(("Реестр карт пациентов", A.CT.VISUAL.ARROW)),
                    ],
                ): CARD_REGISTRY_STUDY_COURSE_COLLECTION,
                CommandNode(
                    ["hccb", "Браузер регистратора и оператора колл-центра"],
                    [
                        js(("Браузер для регистратора и оператора колл-центра",
                           A.CT.VISUAL.ARROW)),
                    ],
                ): CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION,
                self.wiki_node: None,
            },
            patient_node: None,
            time_tracking_report_node: None,
            my_time_tracking_report_node: None,
            print_node: None,
            CommandNode(patient_node.name_list, [""]): A.D.to_dict(POLIBASE_PERSON_MENU),
            CommandNode(
                ["ping"],
                ["Проверка компьютера на доступность",
                    "Проверить компьютер на доступность"],
                self.ws_ping_handler
            ): None,
            check_node: None,
            CommandNode(check_node.name_list, [""]): A.D.to_dict(CHECK_MENU),
            polibase_node: None,
            CommandNode(polibase_node.name_list, [""]): A.D.to_dict(POLIBASE_MENU),
            CommandNode(
                ["action", "действие^ \"название действия\""],
                lambda: [
                    j(("Действие", "" if self.argless else " " + esc(self.arg())))],
                self.create_action_handler,
                ADM,
                show_in_main_menu=True,
                text_decoration_before="🎯 ",
                filter_function=lambda: self.argless or A.D_ACT.get(self.arg()),
            ): None,
            CommandNode(
                ["unit", "отдел"],
                ["Отделы"],
                lambda: self.menu_handler(UNIT_MENU),
                text_decoration_before="🏥 ",
                show_in_main_menu=True,
            ): None,
            it_unit_node: None,
            hr_unit_node: None,
            callcentre_unit_node: None,
            CommandNode(
                ["indication^s", "показания"],
                ["Показания"],
                lambda: self.check_resources_and_indications_handler(
                    [CheckableSections.INDICATIONS]
                ),
                # if self.is_all
                # else self.menu_handler(INDICATION_MENU)
                ADM + [Groups.RD, Groups.IndicationWatcher],
                text_decoration_before="📈 ",
                show_in_main_menu=True,
            ): None,
            CommandNode(
                ["backup", "бекап"],
                ["Бекап"],
                lambda: self.menu_handler(BACKUP_MENU),
                ADM,
                text_decoration_before="📦 ",
                show_in_main_menu=True,
            ): None,
            robocopy_node: None,
            polibase_backup_node: None,
            self.create_command_link(
                "cr",
                "card registry",
                [""],
                ADM + [Groups.CardRegistry],
                show_in_main_menu=False,
            ): None,
        }
        self.create_command_list()
        return
        self.command_node_tree = {
            self.study_node: None,
            self.main_menu_node: None,
            self.create_command_link(
                "@help", "help", "Помощь", None, False, text_decoration_before="❔ "
            ): None,
            CommandNode(
                "help|помощь", f"Помощь {A.CT.VISUAL.ARROW} |помощь {A.CT.VISUAL.ARROW}"
            ): {
                CommandNode(
                    "infinity|инфинити", f"инфинити|инфинити {A.CT.VISUAL.ARROW}"
                ): INFINITY_STUDY_COURSE_COLLECTION,
                CommandNode(
                    "polibase|полибейс", f"полибейс|полибейс {A.CT.VISUAL.ARROW}"
                ): POLIBASE_HELP_COLLECTION,
                CommandNode(
                    "holter|холтер",
                    f"аппарат Холтера|аппарат Холтера {A.CT.VISUAL.ARROW}",
                ): HOLTER_STUDY_COURSE_COLLECTION,
                CommandNode(
                    "cr|реестр карт",
                    f"реестр карт пациентов|реестр карт пациентов {A.CT.VISUAL.ARROW}",
                ): CARD_REGISTRY_STUDY_COURSE_COLLECTION,
                CommandNode(
                    "hccb|Браузер регистратора и оператора колл-центра",
                    f"Браузер для регистратора и оператора колл-центра|браузер для регистратора и оператора колл-центра {A.CT.VISUAL.ARROW}",
                ): CALLCENTRE_BROWSER_STUDY_COURSE_COLLECTION,
                self.wiki_node: None,
            },
            CommandNode(
                "polibase|полибейс",
                lambda: j(
                    (js(("Полибейс", MobileHelper.polibase_status())), "|", "Полибейс")
                ),
                lambda: self.menu_handler(POLIBASE_MENU),
                text_decoration_before=lambda: j(
                    (MobileHelper.polibase_status(), " ")),
                show_in_main_menu=True,
            ): None,
            CommandNode("polibase", "|"): {
                polibase_restart_node: None,
                polibase_close_node: None,
                check_email_node_polibase_person: None,
            },
            CommandNode("study|обучение", "|"): {
                self.wiki_node: None,
                infinity_study_course_node: None,
                basic_polibase_study_course_node: None,
                holter_study_course_node: None,
                # card_registry_study_course_node: None,
                callcentre_browser_study_course_node: None,
            },
            CommandNode(
                "ping",
                "Проверка на доступность компьютера|Проверить на доступность компьютера",
                lambda: self.write_line(
                    js(
                        (
                            "Доступен:",
                            A.D_F.yes_no(
                                A.C_R.accessibility_by_ping(
                                    self.arg()
                                    or self.input.input("Введите название хоста")
                                ),
                            ),
                        )
                    )
                ),
            ): None,
            CommandNode(
                "ws|комп^ьютер",
                "Компьютер",
                lambda: self.menu_handler(WORKSTATION_MENU),
                text_decoration_before="🖥️ ",
                show_in_main_menu=True,
            ): None,
            CommandNode("ws|комп^ьютер", "|"): {
                reboot_workstation_node: None,
                shutdown_workstation_node: None,
                process_kill_node: None,
                find_workstation_node: None,
                disks_information_node: None,
                check_ws_node.clone_as(
                    "check|провер^ить",
                    "Проверить все компьютеры"
                    if self.is_all
                    else "Проверка отслеживаемых компьютеров|Проверить отслеживаемые компьютеры",
                ): None,
            },
            CommandNode(
                "note^s|заметк^и",
                lambda: f'Заметка "{self.arg()}"|Заметки'
                if not self.argless and len(self.arg_list) == 1
                else "Заметки",
                lambda: self.show_note_handler(True)
                if len(self.arg_list) == 1
                else self.menu_handler(NOTES_MENU),
                text_decoration_before="📝 ",
                show_in_main_menu=True,
            ): None,
            CommandNode("note^s|заметк^и", "|"): {
                # create_note_node: None,
                self.show_note_node: None,
            },
            CommandNode(
                'action|действие^"название действия"',
                lambda: j(
                    ("Действие", "" if self.argless else " " + esc(self.arg()))),
                self.create_action_handler,
                show_in_main_menu=True,
                filter_function=lambda: not self.argless,
            ): None,
            CommandNode(
                "unit|отдел",
                "Отделы",
                lambda: self.menu_handler(UNIT_MENU),
                text_decoration_before="🏥 ",
                show_in_main_menu=True,
            ): None,
            CommandNode(
                "indication^s|показания",
                "Показания",
                lambda: self.check_resources_and_indications_handler(
                    [CheckableSections.INDICATIONS]
                ),
                # if self.is_all
                # else self.menu_handler(INDICATION_MENU)
                ADM + [Groups.RD, Groups.IndicationWatcher],
                text_decoration_before="📈 ",
                show_in_main_menu=True,
            ): None,
            # CommandNode("indication^s|показания", "|"): {
            #    show_all_indications_node: None
            # },
            # ct_indication_value_node: None,
            # mri_indication_value_node: None,
            # callcentre_unit_node: None,
            # it_unit_node: None,
            # hr_unit_node: None,
            CommandNode(
                "patient|пациент",
                "Пациент",
                lambda: self.menu_handler(POLIBASE_PERSON_MENU),
                text_decoration_before="🤒 ",
                show_in_main_menu=True,
                text="Наши клиенты",
            ): None,
            #
            CommandNode(
                "user|пользователь",
                "Пользователи",
                lambda: self.menu_handler(USER_MENU),
                text_decoration_before="👤 ",
                show_in_main_menu=True,
                text="Наши пользователи",
            ): None,
            CommandNode("user|пользователь", "|", show_always=True): A.D.to_dict(
                USER_MENU
            ),
            #
            CommandNode(
                "check|провер^ка",
                lambda: "Проверка всех компонентов системы"
                if self.is_all
                else "Проверить|Проверка",
                lambda: self.check_resources_and_indications_handler(
                    None, self.is_all)
                if self.is_all
                else self.menu_handler(CHECK_MENU),
                ADM + [Groups.RD, Groups.IndicationWatcher],
                text_decoration_before="☑️ ",
                show_in_main_menu=True,
            ): None,
            CommandNode("check|провер^ка", "|"): A.D.to_dict(CHECK_MENU),
            #
            CommandNode(
                "registry|реестр",
                "Реестр",
                ADM + [Groups.CardRegistry],
                text_decoration_before="📂 ",
                show_in_main_menu=True,
            ): CommandNode(
                "card|карт",
                "карт пациентов",
                lambda: self.menu_handler(CARD_REGISTRY_MENU),
                text=lambda: self.get_polibase_person_card_place_label(
                    self.arg(), display_only_card_folder=True
                ),
            ),
            CommandNode(
                "registry|реестр",
                "|",
                allowed_groups=ADM + [Groups.CardRegistry],
            ): {CommandNode("card|карт", "|"): A.D.to_dict(CARD_REGISTRY_MENU)},
            CommandNode(
                "backup|бекап",
                "Бекап",
                lambda: self.menu_handler(BACKUP_MENU),
                ADM,
                text_decoration_before="📦 ",
                show_in_main_menu=True,
            ): None,
            robocopy_node: None,
            polibase_backup_node: None,
            CommandNode("find|поиск|search|найти", "|"): {
                find_user_node.clone_as(
                    "user|пользовател^я", "Найти пользователя|Поиск пользователя"
                ): None,
                find_workstation_node.clone_as(
                    "ws|компьютер^а", "Найти компьютер|Поиск компьютер"
                ): None,
                # polibase_person_information_node.clone_as(
                #    "client|пациент^а|клиент^а|patient"
                # ): None,
                CommandNode("card|карт^ы", "|"): {
                    polibase_person_find_card_registry_folder_node.clone_as(
                        "patient|пациент^а", "Найти карту пациента|Поиск карты пациента"
                    ): None,
                },
                CommandNode("mark|карт^ы"): {
                    CommandNode("|доступ^а", None, self.find_mark_handler): None
                },
                CommandNode("free|свободн^ой"): {
                    CommandNode("mark|карт^ы"): {
                        CommandNode(
                            "|доступ^а",
                            None,
                            self.find_free_mark_handler,
                            filter_function=lambda: not self.is_all
                            or A.D_C.decimal(self.arg()),
                        ): None
                    }
                },
            },
            CommandNode("list|список"): {
                CommandNode("free|свободн^ых"): {
                    CommandNode("mark^s|карт"): {
                        CommandNode(
                            "|доступ^а",
                            None,
                            self.show_all_free_marks_handler,
                            filter_function=lambda: self.is_all,
                        ): None
                    }
                },
            },
            CommandNode(
                "set",
                "Установить значение переменной",
                lambda: self.get_or_set_variable_handler(),
            ): None,
            CommandNode(
                "get",
                "Получить значение переменной",
                lambda: self.get_or_set_variable_handler(True),
            ): None,
            CommandNode("create|создать|+", "Создать|Создание"): {
                CommandNode("временную", allowed_groups=ADM): {
                    CommandNode(
                        "карт^у",
                    ): {
                        CommandNode(
                            "доступ^а", None, self.create_temporary_mark_handler
                        ): None
                    }
                },
                CommandNode("mark|карт^у", allowed_groups=ADM): {
                    CommandNode("доступ^а", None, self.create_mark_handler): None
                },
                CommandNode("qr", "QR "): {
                    CommandNode("code|код", "кода|код"): {
                        CommandNode(
                            "command|команды",
                            "для команды мобильного помощника",
                            self.create_qr_code_for_mobile_helper_command_handler,
                        ): None
                    }
                },
                create_note_node.clone_as("note|заметку", "заметку"): None,
                create_user_node.clone_as(
                    "user|пользовател^я", "пользователя|пользователя"
                ): None,
                CommandNode(
                    "password|пароль",
                    "пароля|пароль",
                    lambda: self.create_password_handler(),
                    [],
                ): None,
                time_tracking_report_node: None,
                my_time_tracking_report_node: None,
            },
            CommandNode("make|сделать|вернуть", allowed_groups=ADM): {
                CommandNode("mark|карт^у"): {
                    CommandNode("доступ^а"): {
                        CommandNode(
                            "free|свободной",
                            None,
                            self.make_mark_as_free,
                            filter_function=lambda: not self.is_all,
                        ): None
                    }
                }
            },
            CommandNode("|кто"): {
                CommandNode("|потерял"): {
                    CommandNode("mark|карт^у"): {
                        CommandNode(
                            "wlm|доступ^а?",
                            None,
                            self.who_lost_the_mark_handler,
                        ): None
                    }
                }
            },
            run_command_node: None,
        }
        # for node in additional_nodes:
        #    self.command_node_tree[node] = None

        self.create_command_list()

    @property
    def current_pih_keyword(self) -> str:
        return MobileHelper.PIH_KEYWORDS[self.language_index]

    """
    self.create_command_link(
        "cr",
        "card registry",
        "Реестр карт пациентов",
        ADM + [Groups.CardRegistry],
        show_in_main_menu=False,
    ): None,
    CommandNode(
        "cr",
        "|",
        filter_function=lambda: not self.in_root,
        allowed_groups=ADM + [Groups.CardRegistry],
    ): A.D.to_dict(
        CARD_REGISTRY_MENU,
        lambda item: item.clone_as(clone_title_and_label=True),
    ),
    """

    def say_good_bye(self) -> None:
        if not self.is_only_result:
            with self.output.make_indent(2):
                keyword: str = self.current_pih_keyword
                self.output.separated_line()
                link_text: str = A.CT.MESSAGE.WHATSAPP.SEND_MESSAGE_TO_TEMPLATE.format(
                    A.D_F.telephone_number_international(
                        A.D_TN.it_administrator()),
                    keyword,
                )
                if self.is_cli:
                    with self.output.make_indent(0):
                        self.write_line(
                            j(
                                (
                                    A.CT_V.ROBOT,
                                    " ",
                                    nl("Команда выполнена."),
                                    "      Ожидаю новой команды...",
                                )
                            )
                        )
                else:
                    self.write_line(
                        f"{b(keyword.upper())}: до свидания, {self.get_user_given_name()}."
                    )
                    with self.output.make_indent(2, True):
                        self.write_line(
                            f"Всегда буду рад видеть Вас снова, для этого:\n {A.CT_V.BULLET} отправьте {b(keyword)}\nили\n {A.CT_V.BULLET} нажмите на ссылку: {link_text}"
                        )

    def create_command_link(
        self,
        name: str | list[str],
        link: str,
        title_and_label: list[str] | None,
        allowed_groups: list[Groups] | None = None,
        show_always: bool = False,
        text_decoration_before: str | None = None,
        show_in_main_menu: bool = True
    ) -> CommandNode:
        return CommandNode(
            [name] if isinstance(name, str) else name,
            title_and_label,
            lambda: self.do_pih(
                js(
                    (
                        self.current_pih_keyword,
                        js((link, js(self.comandless_line_part_list))),
                    )
                )
            ),
            allowed_groups=allowed_groups,
            wait_for_input=True,
            show_in_main_menu=show_in_main_menu,
            # as_link=True,
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

    # def first_arg(self, default_value: Any | None = None) -> Any | None:
    #    return self.arg(default_value=default_value)

    def arg(self, index: int = 0, default_value: Any | None = None) -> Any | None:
        return self.session.arg(index, default_value)

    @property
    def in_main_menu(self) -> bool:
        return (
            not self.none_command
            and len(self.current_command) == 1
            and self.current_command[0] == self.main_menu_node
        )

    @property
    def in_choice_command(self) -> bool:
        return self.in_all_commands or self.none_command

    @property
    def in_all_commands(self) -> bool:
        return self.in_main_menu and self.is_all

    @property
    def argless(self) -> bool:
        return self.arg_len == 0

    def drop_args(self) -> None:
        self.session.arg_list = None

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
                    self.input.polibase_person_by_any(value or self.arg())
                )
            else:
                value = self.input.wait_for_polibase_person_pin_input(
                    lambda: value
                    or self.arg()
                    or self.input.input(
                        f"Введите:\n {A.CT_V.BULLET} Адресс электронной почты\nили\n {A.CT_V.BULLET} Поисковый запрос для поиска пациента/клиента"
                    )
                )
            polibase_person_string: str = " "
            if not A.D_C.empty(polibase_person):
                polibase_person_string = f" клиента {b(polibase_person.FullName)}: "
            if not only_for_polibase_person:
                if not A.D_C.empty(value):
                    if A.C.email(value):
                        result: bool = A.C.EMAIL.accessability(value)
                        self.output.separated_line()
                        self.output.good(
                            f"Адресс электронной почты{polibase_person_string}{b(value)} {'' if result else 'не' }доступен"
                        )
                        return result
                else:
                    self.show_error(f"Нет адресса электронной почты")
                    return None
            polibase_person = polibase_person or A.D.get_first_item(
                self.input.polibase_person_by_any(value)
            )
            self.drop_args()
            result = self.check_email_address_handler(
                polibase_person.email, polibase_person
            )
            if not result:
                if self.input.yes_no(
                    f"Начать информационный квест для клиента {b(polibase_person.FullName)}"
                ):
                    A.A_P_IQ.start(polibase_person)
        except NotFound as error:
            self.show_error(error)
        return result

    def check_resources_and_indications_handler(
        self, section_list: list[CheckableSections] | None = None, all: bool = False
    ) -> None:
        section_list = section_list or CheckableSections.all()
        self.console_apps_api.resources_and_indications_check(
            section_list, False, self.is_forced, all
        )

    def register_ct_indications_handler(self) -> None:
        self.console_apps_api.register_ct_indications()

    def create_polibase_db_backup_handler(self) -> None:
        name: str = A.D.now_to_string(A.CT_P.DATABASE_DATETIME_FORMAT)
        answer: bool = self.input.yes_no(
            f"Изменить имя файла дампа базы данных",
            False,
            b("Отправьте имя"),
            f"Использовать имя: {b(name)} - отправьте {A.CT.VISUAL.NUMBER_SYMBOLS[0]}",
        )
        if A.A_P.DB.backup(self.input.answer if answer else name):
            self.write_line(
                i(
                    f"{self.user_given_name}, ожидайте уведовление об процессе создания бекапа база данных Polibase в telegram-группе {b('Backup Console')}"
                )
            )

    def robocopy_job_run_handler(self) -> None:
        forced: bool = self.is_forced
        source_job_name: str | None = self.arg()
        if not A.D_C.empty(source_job_name):
            source_job_name = source_job_name.lower()
        job_name_set: set = set()
        job_status_map_by_name: dict[str,
                                     list[RobocopyJobStatus]] = defaultdict(list)
        job_status_list: list[RobocopyJobStatus] = A.R_B.robocopy_job_status_list(
        ).data
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
        if not A.D_C.empty(source_job_name) and source_job_name not in job_name_list:
            source_job_name = None

        def is_active(job_name: str) -> bool:
            inacitve_count: int = 0
            for job_status in job_status_list:
                if job_status.name == job_name:
                    inacitve_count += 1
                    if job_status.active:
                        inacitve_count -= 1
            return inacitve_count == 0

        if (
            not A.D_C.empty(source_job_name)
            and is_active(source_job_name)
            and not forced
        ):
            self.show_error(
                f"Robocopy-задание '{source_job_name}' уже выполняется")
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
                            date = f"{A.D_F.datetime(job_status.last_created)}"
                        status = job_status.last_status
                    return (
                        f"   {A.CT.VISUAL.BULLET} {source}{A.CT.VISUAL.ARROW}{destination}"
                        + ("" if status is None else f" [ {b(str(status))} ]")
                        + ("" if date is None else f"\n     {date}")
                    )

                return A.CT.NEW_LINE + j(
                    list(map(job_status_item_label_function, job_list)), A.CT.NEW_LINE
                )

            def job_label_function(name: str) -> str:
                return f"{b(name)}:" + job_status_list_label_function(name)

            job_name: str = source_job_name or self.input.item_by_index(
                f"Пожалуйста, выберите Robocopy-задание, которое необходимо выполнить",
                job_name_list,
                lambda name, _: job_label_function(name),
            )
            job_list: list[RobocopyJobStatus] = job_status_map_by_name[job_name]
            job_list = (
                job_list
                if forced
                else list(filter(lambda item: not item.active or item.live, job_list))
            )
            if len(job_list) > 0:
                self.write_line(nl(j((b("Robocopy-задание"), ": ", job_name))))
                job_item: RobocopyJobStatus = self.input.item_by_index(
                    "Пожалуйста, выберите направление",
                    job_list
                    + ([] if len(job_list) < 2 else [RobocopyJobStatus("Все")]),
                    lambda item, _: b(item.name)
                    if A.D.is_none(item.destination)
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
                    self.show_error(
                        j(
                            (
                                self.user_given_name,
                                ", Robocopy-задание не может быть выполнено",
                            )
                        )
                    )
            else:
                self.show_error(
                    j(
                        (
                            self.user_given_name,
                            ", все направления для Robocopy-задания в процессе выполнения",
                        )
                    )
                )

    def save_media_efilm(self) -> None:
        self.write_line(i("Идёт загрузка..."))
        self.output.write_video(
            "Как экспортировать исследование пациента из eFilm. Данные находятся в папке: *C:\Program Files (x86)\Merge Healthcare\eFilm\CD*",
            MEDIA_CONTENT.VIDEO.EXPORT_FROM_EFILM,
        )

    def under_construction_handler(self) -> None:
        self.show_error(
            f"Извините, {self.user_given_name}, раздел в разработке 😞")

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
        return self.has_flag(Flags.ALL) or BM.has(self.external_flags, Flags.ALL)

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
        return (
            self.has_flag(Flags.SILENCE)
            or BM.has(self.external_flags, Flags.SILENCE)
            or self.is_silence_no
            or self.is_silence_yes
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

    def workstation_action_handler(self, action_index: int | None = None) -> None:
        if action_index is None:
            action_index = self.command_by_index(
                "Выберите действие",
                ["Перезагрузить", "Выключить", "Найти"],
                lambda item, _: item,
            )
        search_value: str | None = None
        is_all: bool = self.is_all
        non_search_action: bool = action_index < 2
        if not is_all:
            search_value = A.D.get_first_item(self.arg_list) or self.input.input(
                f"{self.user_given_name}, введите название компьютера или запрос для поиска пользователя"
            )
            if search_value in FLAG_KEYWORDS:
                is_all = FLAG_KEYWORDS[search_value] == Flags.ALL
        if non_search_action:
            if is_all:
                if not self.input.yes_no(
                    ("Перезагрузить" if action_index == 0 else "Выключить")
                    + " все компьютеры, которые помечены как разрешенные",
                    False,
                    b("Да") + ' (Введите слово "Workstation")',
                    yes_checker=(lambda item: item == "Workstation"),
                ):
                    return
        try:
            workstations_result: Result[list[Workstation]] | None = None
            if non_search_action:
                workstations_result = (
                    A.R_WS.all_with_prooperty(
                        A.CT_AD.WSProperies.Shutdownable
                        if action_index == 1
                        else A.CT_AD.WSProperies.Rebootable
                    )
                    if non_search_action
                    else A.R_WS.all()
                    if is_all
                    else A.R_WS.by_any(search_value)
                )
                if A.R.is_empty(workstations_result):
                    if A.C_R.accessibility_by_ping(search_value, None, 2):
                        if self.is_forced:
                            if action_index == 0:
                                A.A_WS.reboot(search_value, True)
                                self.write_line(
                                    b(f"Идет перезагрузка компьютера {search_value}...")
                                )
                            else:
                                A.A_WS.shutdown(search_value, True)
                                self.write_line(
                                    b(f"Идет выключение компьютера {search_value}...")
                                )
                        else:
                            self.show_error(
                                f"Компьютер {search_value} нельзя перезагрузить"
                            )
                    else:
                        self.show_error(f"Компьютер {search_value} не найден")
                else:

                    def every_function(workstation: Workstation):
                        user_string: str = ""
                        has_user: bool = not A.D_C.empty(
                            workstation.samAccountName)
                        if has_user:
                            user_string = f" (им пользуется {A.R_U.by_login(workstation.samAccountName).data.name})"
                        if action_index == 0:
                            if is_all or (
                                A.C_WS.rebootable(workstation)
                                or (
                                    self.input.yes_no(
                                        f"Компьютер {b(workstation.name)} не отмечен как разрешенный для перезагрузки, Вы уверены, что хотите его перезагрузить"
                                    )
                                )
                                and (
                                    not has_user
                                    or self.input.yes_no(
                                        f"Перезагрузить компьютер {workstation.name}{user_string}"
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
                            if is_all or (
                                A.C_WS.shutdownable(workstation)
                                or (
                                    self.input.yes_no(
                                        f"Компьютер {b('не отмечен')} как разрешенный для выключения, Вы уверены, что хотите его выключить"
                                    )
                                )
                                and (
                                    not has_user
                                    or self.input.yes_no(
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

                    A.R.every(every_function, workstations_result)
            else:
                workstations_result = (
                    A.R_WS.all() if is_all else A.R_WS.by_any(search_value)
                )
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
                                if A.D_C.empty(item_data)
                                else f"{b('Пользователь')}: {A.R_U.by_login(login).data.name} ({login})",
                            )
                        return False, None

                    self.output.write_result(
                        workstations_result,
                        False,
                        separated_result_item=True,
                        title="Найденные компьютеры:",
                        data_label_function=data_label_function,
                    )
                except NotFound as error:
                    self.show_error(error)
        except NotFound as error:
            self.show_error(error)

    def reboot_workstation_handler(self) -> None:
        self.workstation_action_handler(0)

    def shutdown_workstation_handler(self) -> None:
        self.workstation_action_handler(1)

    def find_workstation_handler(self) -> None:
        self.workstation_action_handler(2)

    def run_commnad_handler(self) -> None:
        self.console_apps_api.run_command(self.arg_list)

    def show_free_marks(self) -> None:
        def label_function(data_item: Mark, index: int) -> str:
            return (
                f"{A.CT.VISUAL.BULLET} {b(data_item.TabNumber)} - {data_item.GroupName}"
            )

        self.output.write_result(
            A.R_M.free_list(),
            False,
            separated_result_item=False,
            label_function=label_function,
        )

    def make_mark_as_free(self) -> None:
        self.console_apps_api.make_mark_as_free(self.arg(), self.is_silence)

    def extract_command_menu(self, value: str) -> tuple[str, list[list[CommandNode]]]:
        result: list[CommandNode] = []
        fields: list[str] = [name for _, name, _,
                             _ in Formatter().parse(value) if name]
        for field_item in fields:
            index_start: int = field_item.find('"menu"')
            if index_start != -1:
                index_start = value.find('"menu":')
                index_end: int = value.find("]}") + 2
                index_start -= 1
                manu_text: str = value[index_start:index_end]
                value = value[0:index_start] + value[index_end: len(value) - 1]
                menu_json = json.loads(manu_text)
                for menu_json_item in menu_json["menu"]:
                    result.append(
                        [
                            CommandNode(
                                menu_json_item["command"], menu_json_item["label"]
                            )
                        ]
                    )
        return value, result

    def show_note_handler(self, root: bool) -> None:
        name: str | None = None
        input_name: str | None = self.arg()
        with self.output.personalized():
            name = input_name or self.input.input("Ввведите название заметки")
        if A.C_N.exists(name):

            def label_function(note: Note, _) -> str:
                text: str = A.D_F.format(note.text)
                return f"{b(note.title)}\n\n{text}"

            note_result: Result[Note | None] = A.R_N.by_name(name)
            if A.R.is_empty(note_result):
                with self.output.personalized():
                    self.show_error("Заметка не найдена")
            else:
                note: Note = note_result.data
                command_menu: list[CommandNode] | None = None
                note.text, command_menu = self.extract_command_menu(note.text)
                self.output.write_result(
                    note_result,
                    label_function=label_function,
                    title=None if root else f"Заметка {name}",
                )
                if not A.D_C.empty(note.images):
                    self.write_line(
                        i(f"Ожидайте загрузку изображений: {len(note.images)}")
                    )
                    for image in note.images:
                        response: Response = requests.get(image)
                        self.output.write_image(
                            "Изображение",
                            A.D_CO.bytes_to_base64(
                                BytesIO(response.content).getvalue()
                            ),
                        )
                if not A.D_C.empty(command_menu):
                    # if self.input.yes_no("Показать доступные операции"):

                    def label_function(item: list[CommandNode], _) -> str:
                        return item[0].title_and_label

                    self.write_line(nl(b("Доступные операции:")))
                    with self.output.make_indent(2, True):
                        self.do_pih(
                            js(
                                (
                                    self.current_pih_keyword,
                                    self.get_command_name(
                                        self.command_by_index(
                                            "Выберите пункт меню",
                                            command_menu,
                                            label_function,
                                            use_zero_index=True,
                                            auto_select=False,
                                        )
                                    ),
                                )
                            )
                        )
        else:
            with self.output.personalized():
                self.show_error("Заметка не найдена")

    def create_action_handler(self) -> None:
        with self.output.personalized():
            action_name: str | None = self.arg() or self.input.input("Введите название действия")
            if A.D_C.empty(action_name):
                self.show_error("Действие для выполнения не выбрано")
            action: Actions | None = A.D_ACT.get(action_name)
            if A.D_C.empty(action):
                self.show_error("Действие не найдено")
            else:
                parameters: list[str] | None = None
                parameters_are_present: bool = self.arg_len > 1
                action_description: ActionDescription = A.D.get(action)
                if not parameters_are_present:
                    if ne(action_description.parameters):
                        parameters = [self.input.input("Введите параметры действия")] if self.input.yes_no(
                            "Ввести параметры для действия") else action_description.parameters
                else:
                    parameters = self.arg_list[1:]
                if not action_description.confirm or self.input.yes_no(
                    js(("Выполнить действие", action_description.description))
                    if A.D_C.empty(action_description.question)
                    else action_description.question
                ):
                    if A.A_ACT.was_done(
                        action,
                        self.session.login,
                        parameters or []
                    ):
                        if not action_description.silence:
                            self.output.good(
                                f"Действие {b(A.D.get(action).description)} зарегистрировано."
                            )

    def create_note_handler(self) -> None:
        with self.output.personalized():
            input_name: str | None = self.arg()
            name: str | None = None
            while True:
                name = input_name or self.input.input(
                    "Введите название заметки: оно должно быть уникальным"
                )
                if A.C_N.exists(name):
                    self.show_error(
                        'Заметка с названием "{name}" уже существует')
                    input_name = None
                else:
                    break
            title: str = self.arg(1) or self.input.input("Введите заголовок")
            if A.A_N.create(
                name, Note(title, self.arg(
                    2) or self.input.input("Введите текст"))
            ):
                self.output.good("Заметка создана")
                image_path: str | None = (
                    self.console_apps_api.create_qr_code_for_mobile_helper_command(
                        j(
                            (
                                self.get_command_node_name(
                                    self.show_note_node.name_list
                                ),
                                e(name),
                                not self.is_silence,
                            )
                        ),
                        title,
                        False,
                    )
                )
                if not A.D_C.empty(image_path):
                    if self.is_silence or self.input.yes_no(
                        "Распечатать",
                        False,
                        f"{b('Да')} - укажите количество копий",
                        yes_checker=lambda value: A.D_Ex.decimal(value) > 0,
                    ):
                        self.output.good(" QR-код заметки отправлен на печать")
                        for _ in range(
                            if_else(
                                self.is_silence,
                                1,
                                lambda: A.D_Ex.decimal(self.input.answer),
                            )
                        ):
                            A.A_QR.print(image_path)
                else:
                    pass

    def send_workstation_message_handler(self, to_all: bool) -> None:
        if to_all:
            self.console_apps_api.send_workstation_message_to_all()
        else:
            self.console_apps_api.send_workstation_message(
                self.arg(), self.arg(1), not self.is_silence
            )

    def who_lost_the_mark_handler(self) -> None:
        self.console_apps_api.who_lost_the_mark(self.arg())

    def time_tracking_report_handler(self, for_me_report_only: bool = False) -> None:
        def get_date_format(value: str) -> str:
            return (
                A.CT.YEARLESS_DATE_FORMAT
                if value.count(A.CT.DATE_PART_DELIMITER) == 1
                else A.CT.DATE_FORMAT
            )
        with self.output.personalized():
            if for_me_report_only:
                if self.argless and self.input.yes_no("Получить отчет в период с начала месяца до сегодняшнего дня"):
                    now: datetime = A.D.now()
                    self.arg_list.append(j((1, now.month), "."))
                    self.arg_list.append(j((now.day, now.month), "."))
            value: str | None = self.arg()
            format: str | None = None if A.D_C.empty(
                value) else get_date_format(value)
            start_date: datetime | None = A.D_Ex.datetime(value, format)
            if not A.D_C.empty(start_date):
                if format == A.CT.YEARLESS_DATE_FORMAT:
                    start_date = start_date.replace(A.D.today().year)
            value = self.arg(1)
            format = None if A.D_C.empty(value) else get_date_format(value)
            end_date: datetime | None = A.D_Ex.datetime(value, format)
            if not A.D_C.empty(end_date):
                if format == A.CT.YEARLESS_DATE_FORMAT:
                    end_date = end_date.replace(A.D.today().year)
            while True:
                if A.D_C.empty(start_date):
                    value = self.input.input(
                        f"Введите начало периода, в формате {b('ДЕНЬ.МЕСЯЦ')}, например {A.D.today_string(A.CT.YEARLESS_DATE_FORMAT)}"
                    )
                    value = A.D_F.to_date(value)
                    format = get_date_format(value)
                    start_date = A.D_Ex.datetime(value, format)
                    if A.D_C.empty(start_date) or start_date.date() > A.D.today():
                        continue
                    if format == A.CT.YEARLESS_DATE_FORMAT:
                        start_date = start_date.replace(A.D.today().year)
                if A.D_C.empty(end_date) or start_date > end_date:
                    if not self.input.yes_no(
                        "Использовать сегодняшнюю дату",
                        no_label=f"Введите окончание периода, в формате {b('ДЕНЬ.МЕСЯЦ')}, например {A.D.today_string(A.CT.YEARLESS_DATE_FORMAT)}",
                    ):
                        value = A.D_F.to_date(self.input.answer)
                        format = get_date_format(value)
                        end_date = A.D_Ex.datetime(value, format)
                        if A.D_C.empty(end_date):
                            continue
                        if format == A.CT.YEARLESS_DATE_FORMAT:
                            end_date = end_date.replace(A.D.today().year)
                    else:
                        end_date = A.D.today(as_datetime=True)
                if not (A.D_C.empty(start_date) or A.D_C.empty(end_date)):
                    break
            start_date_string: str = A.D.date_to_string(
                start_date, A.CT.YEARLESS_DATE_FORMAT
            )
            end_date_string: str = A.D.date_to_string(
                end_date, A.CT.YEARLESS_DATE_FORMAT)
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
                    A.R_M.by_name(
                        self.session.user.name), lambda item: item.TabNumber
                ).data,
                self.session.login in A.CT.TIME_TRACKING.PLAIN_FORMAT_AS_DEFAULT_LOGIN_LIST,
            ):
                name: str = (
                    f"Отчет рабочего времени с {start_date_string} по {end_date_string}"
                )
                self.output.write_document(
                    name,
                    A.PTH.add_extension(name, A.CT_F_E.EXCEL_NEW),
                    A.D_CO.file_to_base64(report_file_path),
                )

    def menu_handler(self, menu_command_list: list[CommandNode]) -> None:
        def label_function(command_node: CommandNode) -> str:
            return j(
                (
                    get_value(command_node.text_decoration_before),
                    b(A.D.capitalize(self.get_command_node_label(command_node))),
                    j(
                        (
                            nl(),
                            f" {A.CT_V.BULLET} ",
                            self.get_command_node_help_label(command_node),
                            get_value(command_node.help_text),
                            nl(),
                        )
                    )
                    if self.helped
                    and command_node.name_list != self.exit_node.name_list
                    else "",
                    get_value(command_node.text_decoration_after),
                )
            )

        self.execute_command(
            self.command_by_index(
                f"Пожалуйста, выберите пункт меню",
                list(
                    filter(
                        self.command_list_filter_function,
                        list(map(lambda item: [item], menu_command_list)),
                    )
                ),
                label_function=lambda item, _: label_function(item[0]),
            )
        )

    def create_qr_code_for_card_registry_folder_handler(self) -> None:
        with self.output.personalized():
            qr_image_path_list: list[
                str
            ] = self.console_apps_api.create_qr_code_for_card_registry_folder(
                self.arg(), not self.is_silence
            )
            if A.D_C.empty(qr_image_path_list):
                return
            count: int = A.CT_P.CARD_REGISTRY_FOLDER_QR_CODE_COUNT
            for qr_image_path_item in qr_image_path_list:
                if (
                    self.is_silence
                    or len(qr_image_path_list) > 1
                    or self.input.yes_no(
                        f"Распечатать QR-код (будут распечатаны {count} копии)"
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
        with self.output.personalized():
            image_path: str | None = (
                self.console_apps_api.create_qr_code_for_mobile_helper_command(
                    self.arg(), self.arg(1), not self.is_silence
                )
            )
            if A.D_C.empty(image_path):
                pass
            elif self.is_silence or self.input.yes_no("Показать результат"):
                if self.is_silence_yes:
                    self.output.write_image(
                        "Результат", A.D_CO.file_to_base64(image_path)
                    )
            if self.is_silence or self.input.yes_no(
                "Распечатать",
                False,
                f"{b('Да')} - укажите количество копий",
                yes_checker=lambda value: A.D_Ex.decimal(value) > 0,
            ):
                self.output.good(" QR код отправлен на печать")
                for _ in range(
                    1 if self.is_silence else A.D_Ex.decimal(self.input.answer)
                ):
                    A.A_QR.print(image_path)

    def study_course_handler(
        self,
        index: int | None = None,
        node_list: dict[CommandNode, None] | None = None,
        help_content_holder_list: list[HelpContentHolder] | None = None,
        wiki_location: Callable[[None], str] | None = None,
    ) -> None:
        if A.D_C.empty(index):
            action_index: int = self.input.index(
                "Пожалуйста, выберите пункт меню",
                ["Пройти обучающий курс", "Выбрать раздел обучающего курса"]
                + (
                    []
                    if wiki_location is None
                    else ["Как открыть курс на компьютере с рабочего места?"]
                ),
                lambda item, _: b(item),
            )
            if action_index == 0:
                length: int = len(node_list)
                self.write_line(
                    nl(f"{self.user_given_name}, Вы начали обучающий курс. Он состоит из {length} разделов.")
                )
                index = 0
                for index, _ in enumerate(node_list):
                    self.study_course_handler(
                        index, node_list, help_content_holder_list, True
                    )
                    if index < length - 1:
                        if not self.input.yes_no(
                            f"{self.user_given_name}, перейти к следующему разделу ({index + 2} из {length})"
                        ):
                            self.write_line(
                                f"{self.user_given_name}, вы не полность прошли обучайющий курс."
                            )
                            break
                if index == len(node_list) - 1:
                    self.write_line(
                        f"{self.user_given_name}, спасибо, что прошли обучайющий курс!"
                    )
            elif action_index == 1:
                if node_list is not None:
                    main_title: str | None = self.get_command_title(
                        self.current_command
                    )
                    if not A.D_C.empty(main_title):
                        self.output.head(f"{main_title}") is not None
                    self.study_course_handler(
                        self.input.index(
                            f"Пожалуйста, выберите раздел обучения",
                            A.D.to_list(node_list, True),
                            lambda item, _: b(
                                self.get_command_node_title(item)),
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
            self.output.instant_mode = True
            help_content_holder: HelpContentHolder = help_content_holder_list[index]
            main_title: str | None = f"{self.get_command_node_title(help_content_holder.title_and_label or help_content_holder.name)}"
            if not A.D_C.empty(main_title) and index >= 0:
                self.output.head(j(("Раздел ", index + 1, ": ", main_title)))
            content: list[Callable[[None], str]] = help_content_holder.content
            len_content: int = len(content)
            for index, content_item in enumerate(content):
                content_item: HelpContent = content_item
                text: str = content_item.text
                title: str | None = None
                title = content_item.title or main_title
                if text is not None:
                    self.write_line(text)
                self.output.separated_line()
                content_link: Callable[[None],
                                       str] | IndexedLink = content_item.content
                if content_link is not None:
                    content_body: str | None = None
                    if callable(content_link):
                        content_body = content_link()
                    else:
                        content_body = getattr(
                            content_link.object, f"{content_link.attribute}{index + 1}"
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
            self.output.instant_mode = False

    def create_temporary_mark_handler(self) -> None:
        arg: str | None = self.arg()
        owner_mark: Mark | None = None
        if not A.D_C.empty(arg):
            try:
                owner_mark = A.R.get_first_item(A.R_M.by_any(arg))
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
            def data_to_string() -> str | None:
                if field.name == A.CT_FNC.FULL_NAME:
                    index_string: str = f"{index + 1}/{length}"
                    return (
                        field.default_value
                        if A.D_C.empty(data)
                        else f"{index_string}: {b(A.D_F.name(data))} ({person.pin})"
                    )
                if field.name in [
                    A.CT_FNC.PIN,
                    A.CT_FNC.CARD_REGISTRY_FOLDER,
                    A.CT_FNC.EMAIL,
                ]:
                    return ""

            return True, data_to_string()

        polibase_person_card_registry_folder: str = (
            self.input.polibase_person_card_registry_folder(self.arg())
        )
        person_list_result: Result[
            list[PolibasePerson]
        ] = A.R_P.persons_by_card_registry_folder(
            self.arg() or polibase_person_card_registry_folder
        )
        person: PolibasePerson | None = A.R.get_first_item(person_list_result)
        if not A.D_C.empty(person):
            if A.CR.folder_is_sorted(polibase_person_card_registry_folder):
                A.R.sort(person_list_result, A.D_P.sort_person_list_by_pin)
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
            title=f'Список карт пациентов в папке "{polibase_person_card_registry_folder}"{A.CT.NEW_LINE}'
            if self.argless
            else None,
        )

    def sort_card_registry_folder_handler(self) -> None:
        with self.input.input_timeout(None):
            with self.output.personalized():
                card_registry_folder: str = (
                    self.input.polibase_person_card_registry_folder(self.arg())
                )
                if A.R.is_empty(
                    A.R_E.get(
                        *A.E_B.card_registry_folder_complete_card_sorting(
                            card_registry_folder
                        )
                    )
                ):
                    base: int = 10
                    polibase_person_pin_list: list[int] = A.CR.persons_pin_by_folder(
                        card_registry_folder
                    )
                    length: int = len(polibase_person_pin_list)
                    if length == 0:
                        self.show_error(
                            f"Папка реестра карт {card_registry_folder} пустая"
                        )
                    else:
                        stack_count: int = int(length / base)
                        polibase_person_card_map = {
                            i: polibase_person_pin_list[i *
                                                        base: (1 + i) * base]
                            for i in range(stack_count)
                        }
                        remainder_length: int = length - stack_count * base
                        if remainder_length > 0:
                            polibase_person_card_map[
                                stack_count
                            ] = polibase_person_pin_list[stack_count * base:]
                        length = len(polibase_person_card_map)
                        text: str = f"Разложите все карты пациентов, находящиеся в папке на {b(str(length))} стопок по {base} в каждой стопке."
                        if remainder_length > 0:
                            text += f"В последней стопке будет {b(str(remainder_length))} карт пациентов."
                        self.write_line(text)
                        # names: list[str] = ["первая", "вторая", "третья", "четвёртая", "пятая", "шестая", "седьмая", "восьмая", "девятая", "десятая"]
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
                                min_pin_value: int = min(
                                    polibase_person_pin_list)
                                count: int = length
                                for index in range(length):
                                    if len(polibase_person_card_map[index]) == 0:
                                        count -= 1
                                        if count == 0:
                                            return
                                    else:
                                        break
                                for index in range(length):
                                    if len(polibase_person_card_map[index]) > 0:
                                        min_pin_value = max(
                                            min_pin_value,
                                            max(polibase_person_card_map[index]),
                                        )
                                position: int = -1
                                for index in range(length):
                                    if min_pin_value in polibase_person_card_map[index]:
                                        position = polibase_person_card_map[
                                            index
                                        ].index(min_pin_value)
                                        polibase_person_card_map[index].pop(
                                            position)
                                        break
                                step += 1
                                with self.output.personalized(False):
                                    if step_limit > 1 and step % step_limit == 1:
                                        self.write_line(
                                            "Возьмите карту пациента c номером:\n"
                                        )
                                    self.write_line(
                                        js(
                                            (
                                                A.CT_V.BULLET,
                                                f"Возьмите карту пациента c номером "
                                                if step_limit == 1
                                                else "",
                                                f"{b(str(min_pin_value))}: ",
                                                b(names[index]),
                                                "стопка",
                                                js(
                                                    (
                                                        names[
                                                            A.D.check(
                                                                position > 4,
                                                                len(
                                                                    polibase_person_card_map[
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
                                                                        polibase_person_card_map[
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
                                                        polibase_person_card_map[index]
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
                    self.show_error(
                        f"Папка реестра карт {card_registry_folder} уже отсортирована"
                    )

    def get_card_registry_statistics_handler(self) -> None:
        places: dict[str, str] = A.CT_CR.PLACE_NAME
        full_statistics: bool = self.input.yes_no("Показать полную статистику")

        statistics: list[CardRegistryFolderStatistics] = A.CR.get_statistics()
        statistics_by_place: dict[str, list[CardRegistryFolderStatistics]] = {}
        for place_item in places:
            statistics_by_place[place_item] = list(
                filter(lambda item: item.name.startswith(
                    place_item), statistics)
            )

        def count(statistics: list[CardRegistryFolderStatistics]) -> str:
            total: int = 0
            for item in statistics:
                total += item.count
            return str(total)

        self.write_line(
            nl(j(("Всего зарегистрированных карт: ", count(statistics)))))
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
                folder_name_list: list[str] = list(
                    map(
                        lambda item: item.name,
                        statistics_by_place[place_item],
                    )
                )
                folder_list: list[CardRegistryFolderStatistics] = statistics_by_place[place_item]
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
                                list(
                                    filter(
                                        A.CR.is_folder_registered,
                                        folder_name_list,
                                    )
                                ),
                            ),
                            #Проблемных (количество карт в папке больше {A.CT.CARD_REGISTRY.MAX_CARD_PER_FOLDER}
                            nl(),
                            " " * 4,
                            A.CT_V.BULLET,
                            " ",
                            f"Количество карт пацментов в папках: ",
                            nl(),
                            A.D.list_to_string(
                                list(
                                    map(
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
                                    )
                                ),
                                separator=nl(),
                            )
                            if full_statistics
                            else "",
                            nl(),
                        )
                    )
                )
                if full_statistics:
                    for folder_name in folder_name_list:
                        person_pin_list_from_data_source = A.CR.persons_pin_by_folder(
                            folder_name
                        )
                        person_pin_list_from_polibase = A.R.map(
                            A.R_P.persons_by_card_registry_folder(folder_name),
                            lambda item: item.pin,
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
                                                "Незарегистрованные карты в папке:\n",
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
        with self.output.personalized():

            def check(value: str) -> int | None:
                return A.D_Ex.decimal(value)

            polibase_person_card_registry_folder: str = (
                A.D_F.polibase_person_card_registry_folder(
                    self.arg() or self.input.polibase_person_card_registry_folder()
                )
            )
            if A.CR.is_folder_registered(
                polibase_person_card_registry_folder
            ):
                if not self.input.yes_no(
                    "Папка реестра карт уже добавлена в реестр.\nПродолжить"
                ):
                    return
            A.E.send(
                *A.E_B.card_registry_folder_was_registered(
                    polibase_person_card_registry_folder,
                    self.input.input("Введите номер шкафа",
                                     check_function=check),
                    self.input.input("Введите номер полки",
                                     check_function=check),
                    self.input.input(
                        "Введите позицию на полке (0 - без позиции)",
                        check_function=check,
                    ),
                )
            )

    def add_polibase_person_to_card_registry_folder_handler(self) -> None:
        with self.output.personalized():
            interruption: InternalInterrupt | None = None
            polibase_person_card_registry_folder: str = (
                A.D_F.polibase_person_card_registry_folder(
                    self.arg() or self.input.polibase_person_card_registry_folder()
                )
            )
            try:
                with self.input.input_timeout(None):
                    result_polibase_person_list: Result[
                        list[PolibasePerson]
                    ] = A.CR.persons_by_folder(polibase_person_card_registry_folder)
                    polibase_person_pin_list: list[int] = list(
                        map(lambda item: item.pin,
                            result_polibase_person_list.data)
                    )
                    added_polibase_person_list: list[PolibasePerson] = []
                    while True:
                        while True:
                            try:
                                for (
                                    polibase_person
                                ) in self.input.polibase_person_by_any(self.arg(1)):
                                    if (
                                        polibase_person.pin
                                        not in polibase_person_pin_list
                                    ):
                                        added_polibase_person_list.append(
                                            polibase_person
                                        )
                                        if A.A_P.set_card_registry_folder(
                                            polibase_person_card_registry_folder,
                                            polibase_person,
                                        ):
                                            self.drop_args()
                                            self.output.separated_line()
                                            self.write_line(
                                                f"Карта пациента с персональным номером {b(str(polibase_person.pin))} добавлена в папку {b(polibase_person_card_registry_folder)}"
                                            )
                                        else:
                                            pass
                                    else:
                                        self.drop_args()
                                        self.output.separated_line()
                                        self.write_line(
                                            f"Карта пациента с персональным номером {b(str(polibase_person.pin))} уже находится в папке {b(polibase_person_card_registry_folder)}"
                                        )
                                break
                            except NotFound as error:
                                self.show_error(error)
                            except BarcodeNotFound as error:
                                self.show_error(error)
                        with self.output.personalized(False):
                            self.output.separated_line()
                            self.write_line(
                                f" {A.CT_V.BULLET} Добавьте следующую карту пациента в папку\nили\n {A.CT_V.BULLET} {self.output.exit_line('отправьте: ')} для завершения"
                            )
            except InternalInterrupt as _interruption:
                interruption = _interruption
        if (
            not A.D_C.empty(added_polibase_person_list)
            and A.CR.folder_is_sorted(polibase_person_card_registry_folder)
            and self.input.yes_no("Показать результат")
        ):
            polibase_person_list: list[PolibasePerson] = (
                result_polibase_person_list.data + added_polibase_person_list
            )
            result_polibase_person_list.data = polibase_person_list
            folder_is_sorted: bool = A.CR.folder_is_sorted(
                polibase_person_card_registry_folder
            )
            if folder_is_sorted:
                A.D_P.sort_person_list_by_pin(polibase_person_list)

            def label_function(polibase_person: PolibasePerson, index: int) -> str:
                is_new: bool = (
                    A.D_C.empty(polibase_person_pin_list)
                    or polibase_person.pin not in polibase_person_pin_list
                )
                result: str = f"{index + 1}. {'Добавлена ' if is_new else ''}{polibase_person.pin}: {polibase_person.FullName}"
                return result if is_new else b(result)

            self.output.write_result(
                Result(A.CT_FC.POLIBASE.PERSON, polibase_person_list),
                False,
                label_function=label_function,
                title=f"Список карт пациентов в папке {b(polibase_person_card_registry_folder)}",
            )
            if not A.D_C.empty(interruption):
                raise interruption

    def create_password_handler(self) -> None:
        self.console_apps_api.create_password()

    def print_handler(self) -> None:
        with self.output.personalized():
            image_path: str = self.arg() or self.input.input("Отправьте изображение")
            if self.is_silence or self.input.yes_no(
                "Распечатать",
                False,
                f"{b('Да')} - укажите количество копий",
                yes_checker=lambda value: A.D_Ex.decimal(value) > 0,
            ):
                self.output.good("Изображение отправлено на печать")
                image_path_list: tuple = A.D.dequotes(image_path)
                image_path = j(
                    A.D.not_empty_items(
                        [js(image_path_list[0])] + image_path_list[1])
                )
                for _ in range(
                    1 if self.is_silence else A.D_Ex.decimal(self.input.answer)
                ):
                    A.A_QR.print(image_path)

    def about_it_handler(self) -> None:
        it_user_list: Result[list[User]] = A.R_U.by_job_position(
            A.CT_AD.JobPisitions.IT
        )

        def label_function(user: User, index: int) -> str:
            workstation: Workstation | None = None
            result: str = f" {b(A.CT.VISUAL.BULLET)} {b(user.name)}"
            if not A.D_C.empty(user.description):
                user_description_list: list[str] = user.description.split("|")
                workstation_name: str = user_description_list[1].strip()
                workstation = A.R_WS.by_name(workstation_name).data
                result += f" ({user_description_list[0].strip()})"
            if workstation is not None:
                internal_telephone_number: str = str(
                    A.D_Ex.decimal(workstation.description.split("(")[-1])
                )
                result += f"\n  Внутренний телефон: " + \
                    b(internal_telephone_number)
            return result

        self.output.write_result(
            it_user_list,
            False,
            label_function=label_function,
            title=j((nl("ИТ отдел это:"), ConsoleAppsApi.LINE)),
            separated_result_item=False,
        )
        self.write_line(
            j((nl(ConsoleAppsApi.LINE), self.get_it_telephone_number_text()))
        )

    def find_user_handler(self) -> None:
        self.console_apps_api.find_user(self.arg())

    def find_mark_handler(self) -> None:
        self.console_apps_api.mark_find(self.arg())

    def find_free_mark_handler(self) -> None:
        value: str | None = self.arg()
        try:
            result_mark: Mark = A.R.get_first_item(
                A.R_M.by_any(value or self.input.mark.any())
            )

            def label_function(data_item: Mark, _: int) -> str:
                return f"{A.CT.VISUAL.BULLET} {b(data_item.TabNumber)}"

            def filter_function(mark: Mark) -> bool:
                return mark.GroupID == result_mark.GroupID

            self.write_line(
                f"Свободные карты доступа для группы доступа {b(result_mark.GroupName)}:\n"
            )
            self.output.write_result(
                A.R.filter(A.R_M.free_list(), filter_function),
                False,
                separated_result_item=False,
                label_function=label_function,
                empty_result_text="Нет свободных карт доступа",
            )
        except NotFound as error:
            self.show_error(error)

    def show_all_free_marks_handler(self) -> None:
        sort_by_tab_number: bool = self.input.yes_no(
            "Как отсортировать",
            False,
            f"{b('по табельному номеру')} - отправьте {A.CT_V.NUMBER_SYMBOLS[1]}",
            f"{b('по названию группы доступа')} - отправьте {A.CT_V.NUMBER_SYMBOLS[0]}",
        )

        def sort_function(item: Mark) -> str:
            return item.TabNumber if sort_by_tab_number else item.GroupName

        self.output.write_result(
            A.R.sort(A.R_M.free_list(False), sort_function),
            False,
            title="Свободные карты доступа:",
        )

    def get_or_set_variable_handler(self, get_action: bool = False) -> None:
        with self.output.personalized():
            storage_value_name: str | None = (
                None
                if self.is_all and (not get_action or self.argless)
                else (self.arg() or self.input.input("Введите название переменной"))
            )
            storage_value_holder_list: list[
                A.CT_S | A.CT_MR.TYPES | StorageValue
            ] = A.D_V.find(storage_value_name)

            def sort_function(item: A.CT_S | A.CT_MR.TYPES | StorageValue) -> int:
                if isinstance(item, A.CT_S):
                    return 0
                return 1

            storage_value_holder_list = sorted(
                storage_value_holder_list, key=sort_function
            )

            def label_function(
                variable_value_holder: A.CT_S | A.CT_MR.TYPES | StorageValue, _
            ) -> str:
                variable_name: str = (
                    variable_value_holder.key_name
                    if isinstance(variable_value_holder, StorageValue)
                    else variable_value_holder.name
                )
                variable_value: StorageValue = A.D.get(variable_value_holder)
                alias: str | None = variable_value.key_name
                if A.D_C.empty(alias) or variable_name.lower() == alias.lower():
                    alias = None
                return js(
                    list(
                        filter(
                            lambda item: not A.D_C.empty(item),
                            [
                                ""
                                if A.D_C.empty(variable_value.description)
                                else j((b(variable_value.description), ":")),
                                variable_name,
                                "" if A.D_C.empty(alias) else f"[{alias}]",
                            ],
                        )
                    )
                )

            if A.D_C.empty(storage_value_holder_list):
                self.show_error(
                    f"Значение с именем '{storage_value_name}' не найдено")
                return
            variable_value_holder: A.CT_S | A.CT_MR.TYPES | None = None
            value: Any | None = None

            def get_value(
                variable_holder: A.CT_S | A.CT_MR.TYPES | StorageValue,
            ) -> Any:
                if isinstance(variable_holder, StorageValue):
                    return variable_holder.default_value
                if isinstance(variable_holder, A.CT_S):
                    return A.S.get(variable_holder)
                if isinstance(variable_holder, A.CT_MR.TYPES):
                    return A.D_MR.get_count(variable_holder)

            def show_variable(
                variable_holder: A.CT_S | A.CT_MR.TYPES | StorageValue,
            ) -> None:
                value: Any = get_value(variable_holder)
                if not self.is_silence:
                    with self.output.make_separated_lines():
                        type: str = ""
                        if isinstance(variable_holder, StorageValue):
                            type = "Переменная"
                        if isinstance(variable_holder, A.CT_S):
                            type = "Настройка"
                        if isinstance(variable_holder, A.CT_MR.TYPES):
                            type = "Материальный ресурс"
                        self.write_line(f"{A.CT_V.BULLET} {type}:")
                        with self.output.make_indent(3, True):
                            self.write_line(
                                f"{label_function(variable_holder, None)}:")
                            self.write_line(b(str(value)))

            if self.is_all:
                with self.output.personalized(False):
                    for variable_value_holder in storage_value_holder_list:
                        show_variable(variable_value_holder)
            else:
                with self.output.personalized(False):
                    variable_value_holder = self.input.item_by_index(
                        "Выберите переменную",
                        storage_value_holder_list,
                        label_function,
                    )
                    show_variable(variable_value_holder)
            if not get_action:
                type: StorageValue = variable_value_holder.value
                if isinstance(type, IntStorageValue):

                    def check_function(value: str) -> int | None:
                        return A.D_Ex.decimal(value)

                    value = self.input.input(
                        "Введите число", check_function=check_function
                    )
                elif isinstance(type, TimeStorageValue):
                    format: str = A.CT.SECONDLESS_TIME_FORMAT

                    def check_function(value: str) -> datetime | None:
                        return A.D_Ex.datetime(value, format)

                    value = self.input.input(
                        "Введите время в формате 12:00", check_function=check_function
                    )
                    value = A.D.datetime_to_string(value, format)
                elif isinstance(type, BoolStorageValue):

                    def check_function(value: str) -> bool | None:
                        return A.D_Ex.boolean(value)

                    value = self.input.input(
                        "Введите булево значение (0 или 1)",
                        check_function=check_function,
                    )
                elif isinstance(type, StorageValue):
                    value = self.input.input("Введите строку")
                if not A.D_C.empty(value):
                    if isinstance(variable_value_holder, A.CT_S):
                        A.S.set(variable_value_holder, value)
                    if isinstance(variable_value_holder, A.CT_MR.TYPES):
                        A.D_MR.set_count(variable_value_holder, value)
                self.output.good(
                    f"Переменная {label_function(variable_value_holder, None)} установлена"
                )

    def show_error(self, value: str | Any) -> None:
        self.output.separated_line()
        self.write_line(
            js(
                (
                    A.CT_V.WARNING,
                    value if isinstance(value, str) else value.get_details(),
                )
            )
        )

    def polibase_person_card_registry_folder_find_handler(self) -> None:
        value: str | None = self.arg()
        while True:
            try:
                position_map: dict[int, tuple[int, int]] = {}
                person_list_result: Result[list[PolibasePerson]] = A.R_P.persons_by_any(
                    value or self.input.polibase_person_any()
                )

                def prepeare_polibase_person_function(person: PolibasePerson) -> None:
                    if not A.D_C.empty(person.ChartFolder):
                        person_pin_list: list[int] = A.CR.persons_pin_by_folder(
                            person.ChartFolder
                        )
                        position_map[person.pin] = (
                            person_pin_list.index(person.pin) + 1,
                            len(person_pin_list),
                        )

                A.R.every(prepeare_polibase_person_function,
                person_list_result,
                          )

                def data_label_function(
                    _, field: FieldItem, person: PolibasePerson, data: Any
                ) -> tuple[bool, str]:
                    result: list[bool, Any] = [True, ""]
                    if field.name in [
                        A.CT_FNC.CARD_REGISTRY_FOLDER,
                        A.CT_FNC.FULL_NAME,
                    ]:
                        result[
                            1
                        ] = f"{b(field.caption)}: {(field.default_value if A.D_C.empty(data) else data)}"
                        if (
                            field.name == A.CT_FNC.CARD_REGISTRY_FOLDER
                            and not A.D_C.empty(data)
                        ):
                            result[1] += if_else(
                                person.pin in position_map,
                                lambda: self.get_polibase_person_card_place_label(
                                    person.ChartFolder,
                                    position_map[person.pin][0],
                                    position_map[person.pin][1],
                                ),
                                A.CT_FC.POSITION.default_value,
                            )
                            # f" {A.CT_V.BULLET} Карта: {str(position_map[person.pin][0])} из {position_map[person.pin][1]}" if person.pin in position_map else A.CT_FC.POSITION.default_value
                    return tuple(result)

                self.output.write_result(
                    person_list_result,
                    False,
                    data_label_function=data_label_function,
                    separated_result_item=False,
                )
                break
            except NotFound as error:
                self.show_error(error)
                value = None
            except BarcodeNotFound as error:
                self.show_error(error)

    def get_polibase_person_card_place_label(
        self,
        card_folder_name: str | None,
        card_position: int | None = None,
        folder_length: int | None = None,
        display_only_card_folder: bool = False,
    ) -> str:
        result_label_list: list[str] = []
        if not A.D_C.empty(card_folder_name) and A.CR.is_person_card_registry_folder(
            card_folder_name
        ):
            card_folder_name = A.D_F.polibase_person_card_registry_folder(
                card_folder_name
            )
            result_label_list.append(
                j(
                    (
                        nl(),
                        b(A.CT_FC.POSITION.caption),
                        if_else(
                            display_only_card_folder,
                            lambda: js(("", b("папки"), b(card_folder_name))),
                            "",
                        ),
                        ":",
                    )
                )
            )
            card_folder_first_letter: str | None = card_folder_name[0]
            if card_folder_first_letter in A.CT_CR.PLACE_NAME:
                result_label_list.append(
                    f" {A.CT_V.BULLET} Место: {b(A.CT_CR.PLACE_NAME[card_folder_first_letter])}"
                )
            card_registry_folder_was_registered_event: EventDS | None = (
                A.R.get_first_item(
                    A.R_E.get(
                        *A.E_B.card_registry_folder_was_registered(card_folder_name)
                    )
                )
            )
            if not A.D_C.empty(card_registry_folder_was_registered_event):
                position: CardRegistryFolderPosition = A.D.fill_data_from_source(
                    CardRegistryFolderPosition(),
                    card_registry_folder_was_registered_event.parameters,
                )
                if display_only_card_folder:
                    result_label_list.append(
                        j(
                            (
                                f" {A.CT_V.BULLET} Шкаф: {b(position.p_a)}\n {A.CT_V.BULLET} Полка: {b(position.p_b)}",
                                if_else(
                                    position.p_c > 0,
                                    f"\n {A.CT_V.BULLET} Позиция на полке: {b(position.p_c)}",
                                    "",
                                ),
                            )
                        )
                    )
                    return j(result_label_list, nl())
                result_label_list.append(
                    j(
                        (
                            f" {A.CT_V.BULLET} Папка:\n     шкаф: {b(position.p_a)}\n     полка: {b(position.p_b)}",
                            if_else(
                                lambda: position.p_c > 0,
                                f"\n     позиция на полке: {b(position.p_c)}",
                                "",
                            ),
                        )
                    )
                )
            result_label_list.append(
                if_else(
                    A.D_C.empty(card_position),
                    js(
                        (
                            A.CT_V.WARNING,
                            b(i(A.CT_FC.POSITION.default_value)),
                            A.CT_V.WARNING,
                        )
                    ),
                    lambda: f" {A.CT_V.BULLET} Карта в папке: {b(card_position)} из {b(folder_length)}",
                )
            )
            return j(result_label_list, nl())
        return ""

    def polibase_person_information_handler(self) -> None:
        while True:
            try:

                def action_function(person: PolibasePerson) -> tuple[int | None, int]:
                    if not A.D_C.empty(person.ChartFolder):
                        result: Result[list[PolibasePerson]] = A.CR.persons_by_folder(
                            person.ChartFolder
                        )
                        if not A.D_C.empty(result):
                            person_list: list[PolibasePerson] = result.data
                            for index, person_item in enumerate(person_list):
                                if person_item.pin == person.pin:
                                    return (index + 1, len(person_list))
                            return (None, len(person_list))
                    return (None, 0)

                def data_label_function(
                    _, field: FieldItem, person: PolibasePerson, data: Any
                ) -> tuple[bool, str | None]:
                    if field.name == A.CT_FNC.CARD_REGISTRY_FOLDER:
                        if A.D_C.empty(data):
                            return (True, None)
                        position_map: tuple[int | None,
                                            int] = action_function(person)
                        return (
                            True,
                            j(
                                (
                                    b(A.CT_FC.POLIBASE.CARD_REGISTRY_FOLDER.caption),
                                    ": ",
                                    data,
                                )
                            )
                            + if_else(
                                A.D_C.empty(position_map[0]),
                                "",
                                lambda: self.get_polibase_person_card_place_label(
                                    person.ChartFolder, position_map[0], position_map[1]
                                ),
                            ),
                        )
                    return (False, None)

                self.output.write_result(
                    A.R_P.persons_by_any(
                        self.arg() or self.input.polibase_person_any()
                    ),
                    data_label_function=data_label_function,
                )
                break
            except NotFound as error:
                self.show_error(error)
                self.drop_args()
            except BarcodeNotFound as error:
                self.show_error(error)

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
                if parent and parent.name_list not in list(
                    map(lambda item: item.name_list, self.command_node_cache)
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
            while parent is not None:
                result.insert(0, parent)
                parent = parent.parent
            self.command_list.append(result)
        self.command_list.sort(key=self.command_sort_function)
        if MobileHelper.command_node_name_list is None:
            command_node_name_set: set[str] = set()
            allowed_group_set: set = set()
            for command_item in self.command_list:
                for command_node in command_item:
                    if not A.D_C.empty(command_node.allowed_groups):
                        for group in command_node.allowed_groups:
                            allowed_group_set.add(group)
                    name_list: list[str] = list(
                        map(
                            lambda item: item.split("^")[0],
                            command_node.name_list or [],
                        )
                    )
                    for name_item in name_list:
                        command_node_name_set.add(name_item)
            MobileHelper.command_node_name_list = (
                list(
                    filter(
                        lambda item: not A.D_C.empty(
                            item), list(command_node_name_set)
                    )
                )
                + EXIT_KEYWORDS
            )
            MobileHelper.allowed_group_list = list(allowed_group_set)
        self.fill_allowed_group_list()

    def fill_allowed_group_list(self, session: Session | None = None) -> None:
        session = session or self.session
        for group in MobileHelper.allowed_group_list:
            A.C_A.by_group(group, False, session, False, False)

    def command_sort_function(self, value: list[CommandNode]) -> str:
        name_list: list[str] = []
        for parent in value:
            name_list.append(
                self.get_command_node_title(parent)
                if parent.order is None
                else chr(parent.order)
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
                if A.D_C.empty(command_node.allowed_groups):
                    allow_to_add = True
                else:
                    allow_to_add = False
                    for group in command_node.allowed_groups:
                        allow_to_add = (
                            allow_to_add or group in session_holder.allowed_groups
                        )
        if allow_to_add:
            for command_node in value:
                if not A.D_C.empty(command_node.filter_function):
                    allow_to_add = in_root or (
                        (command_node.visible or not in_search)
                        and command_node.filter_function()
                    )
                    if not allow_to_add:
                        break
        return allow_to_add

    @staticmethod
    def check_for_starts_with_pih_keyword(value: str | None) -> bool:
        if A.D.is_empty(value):
            return False
        value = value.lower()
        return value.startswith(MobileHelper.PIH_KEYWORDS)

    def get_language_index(self, value: str) -> bool:
        value = value.lower()
        for index, item in enumerate(MobileHelper.PIH_KEYWORDS):
            if value.find(item) == 0:
                self.language_index = index
                return True
        return False

    def do_pih(
        self,
        line: str = PIH.NAME,
        sender_user: User | None = None,
        external_flags: int | None = None,
    ) -> bool:
        result: bool = True
        self.line = line
        if self.get_language_index(line):
            if self.wait_for_input():
                self.input.interrupt_for_new_command()
            else:
                self.current_command = None
                command_list: list[list[CommandNode]] = []
                line = line[len(PIH.NAME):]
                action_line_part_list: list[str] | None = None
                action_line_part_list, self.arg_list = A.D.dequotes(line)
                self.comandless_line_part_list = list(action_line_part_list)
                self.line_part_list = A.D.not_empty_items(line.split(" "))
                action_line_part_list = list(
                    filter(
                        lambda item: item.lower() not in (PIH.NAME, PIH.NAME_ALT),
                        action_line_part_list,
                    )
                )
                ################################
                self.flags = 0
                if A.D.is_not_none(external_flags):
                    self.external_flags = external_flags
                self.flag_information = []
                for index, arg_item in enumerate(action_line_part_list):
                    if arg_item in FLAG_KEYWORDS:
                        flag: Flags = FLAG_KEYWORDS[arg_item]
                        self.flags = BM.add(self.flags, flag)
                        self.flag_information.append((index, arg_item, flag))
                action_line_part_list = [
                    item
                    for item in action_line_part_list
                    if item
                    not in list(
                        map(
                            lambda flag_information_item: flag_information_item[1],
                            self.flag_information,
                        )
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
                self.session.flags = self.flags
                source_line_part_list: list[str] = list(
                    map(lambda item: item.lower(), list(action_line_part_list))
                )
                action_line_part_list_length: int = len(action_line_part_list)

                if action_line_part_list_length > 0:
                    filtered_command_list: list[list[CommandNode]] = list(
                        filter(self.command_list_filter_function,
                               self.command_list)
                    )
                    for command_item in filtered_command_list:
                        command_item: list[CommandNode] = command_item
                        command_len: int = len(command_item)
                        if action_line_part_list_length > command_len:
                            continue
                        command_node_name_list: list[str] = []
                        for command_node in command_item:
                            command_node_name_list += list(
                                map(
                                    lambda item: item.split("^")[0],
                                    command_node.name_list,
                                )
                            )
                        work_arg_list: list[str] = list(source_line_part_list)
                        for arg_item in source_line_part_list:
                            has_result: bool = False
                            for command_node_name in command_node_name_list:
                                has_result = not A.D_C.empty(
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
                    # if len(self.arg_list) > 0:
                    #    self.flags = BM.add(self.flags, Flags.ALL)
                #
                is_addressed: bool = self.has_flag(Flags.ADDRESS)
                is_addressed_as_link: bool = self.has_flag(
                    Flags.ADDRESS_AS_LINK)
                if is_addressed or is_addressed_as_link:
                    with self.output.make_indent(2):
                        self.write_line(
                            nl(
                                A.D.check(
                                    is_addressed,
                                    i(
                                        f"{self.user_given_name}, вы выбрали режим адресации команды пользователю."
                                    ),
                                    i(
                                        f"{self.user_given_name}, вы выбрали режим адресации ссылки на команду пользователю."
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
                        A.D.is_not_none(self.line_part_list)
                        and A.D.is_not_none(flag_information_item_index)
                        and len(self.line_part_list) > flag_information_item_index,
                        lambda: self.line_part_list[flag_information_item_index],
                    )
                    while True:
                        try:
                            self.recipient_user_list = self.input.user.by_any(
                                recipient, True, b(
                                    "Выберите получателя команды"), True
                            )
                        except NotFound as error:
                            recipient = None
                            self.show_error(error)
                        else:
                            if len(self.recipient_user_list) == 1:
                                if (
                                    self.recipient_user_list[0].samAccountName
                                    == self.session.get_login()
                                ):
                                    self.show_error(
                                        "Нельзя адресовать самому себе!")
                                    recipient = None
                                else:
                                    break
                            else:
                                self.recipient_user_list = list(
                                    filter(
                                        lambda item: item.samAccountName
                                        != self.session.get_login()
                                        and A.C.telephone_number(item.telephoneNumber),
                                        self.recipient_user_list,
                                    )
                                )
                                if len(self.recipient_user_list) == 0:
                                    self.show_error(
                                        "Нельзя адресовать самому себе!")
                                    recipient = None
                                else:
                                    break
                if A.D.is_not_none(sender_user):
                    if not A.D_C.empty(external_flags):
                        self.session.flags = BM.add(
                            self.session.flags, external_flags)
                    if not BM.has(external_flags, Flags.SILENCE):
                        self.write_line(
                            i(
                                f"{self.get_user_given_name(A.D.to_given_name(sender_user))}, отправил Вам команду:"
                            )
                        )
                command_list_len: int = 0
                # or ((is_addressed or is_addressed_as_link) and self.in_root)
                if self.none_command:
                    command_list = list(
                        filter(
                            lambda value: self.command_list_filter_function(
                                value, in_search=True
                            ),
                            command_list,
                        )
                    )
                    command_list_len = len(command_list)
                    if command_list_len > 0:
                        if command_list_len > 1:
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
                                            get_value(
                                                command_node.text_decoration_before
                                            ),
                                            b(self.get_command_label(command)),
                                            get_value(
                                                command_node.text_decoration_after
                                            ),
                                        )
                                    )
                                    if len(command_list) > 1
                                    else None
                                )

                            self.current_command = list(
                                self.command_by_index(
                                    f"Пожалуйста, выберите пункт меню",
                                    command_list,
                                    label_function,
                                )
                            )
                    else:
                        self.show_error(f"Команда{line} не найдена")
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
        if A.D.is_not_none(value):
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

    # name|title or title|label
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
        return list(map(lambda item: (item or "").replace("^", ""), result))

    def get_command_node_text(self, value: str | CommandNode) -> str:
        result: str | None = None
        if isinstance(value, CommandNode):
            if A.D.is_not_none(value.text):
                # self.argless and
                if callable(value.text):
                    temp_value_string: str | None = value.text()
                    if A.D.is_not_none(temp_value_string):
                        result = temp_value_string
                else:
                    result = value.text
        else:
            result = value
        return result

    def get_command_node_help_label(self, value: CommandNode) -> str:
        name_list: list[str] = A.D.not_empty_items(
            list(
                map(lambda item: item[item.startswith("@"):], value.name_list))
        )

        def name(value: str) -> str:
            index: int = value.find("^")
            if index != -1:
                return j((value[:index], "(", value[index + 1:], ")"))
            return value

        name_list = list(map(name, name_list))
        return j(
            (
                A.D.check(
                    len(name_list) > 1,
                    lambda: j(
                        (
                            "[ ",
                            j(
                                list(map(lambda item: b(item), name_list)),
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

    def get_command_node_name(self, value: CommandNode) -> str:
        return A.D.not_empty_items(
            list(
                map(lambda item: item[item.startswith("@"):], value.name_list))
        )[0].replace("^", "")

    def has_flag(self, flag: Flags) -> bool:
        return BM.has(self.flags, flag)

    @property
    def helped(self) -> bool:
        return self.has_flag(Flags.HELP)

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
            # visible: bool = True
            # for command_node in command:
            #    if not command_node.visible:
            #        visible = False
            #        break
            command_node = command[0]
            return command_node != self.main_menu_node and (
                not command_node.show_in_main_menu
                # and visible
                or command_node.show_always
                if is_all
                else command_node.show_in_main_menu
            )

        command_list: list[list[CommandNode]] = list(
            filter(filter_function, self.command_list)
        )
        command_list.sort(key=self.command_sort_function)
        session: Session | None = None
        if not A.D_C.empty(self.recipient_user_list):
            session = Session()
            session.login = self.recipient_user_list[0].samAccountName
            self.fill_allowed_group_list(session)

        def label_function(command: list[CommandNode], _: int) -> str:
            command_node: CommandNode = command[0]
            return j(
                (
                    get_value(command_node.text_decoration_before),
                    b(self.get_command_label(command)),
                    get_value(command_node.description),
                    get_value(command_node.text_decoration_after),
                    #A.D.check(
                    #    self.helped and A.D.is_not_none(
                    #        command_node.help_text),
                    #    lambda: command_node.help_text(),
                    #    "",
                    #),
                )
            )

        command: list[CommandNode] = self.command_by_index(
            f"Пожалуйста, выберите пункт меню",
            list(
                filter(
                    lambda item: self.command_list_filter_function(
                        item, session),
                    command_list,
                )
            ),
            label_function,
            True,
        )
        self.execute_command(command)

    def execute_command(self, value: list[CommandNode]) -> None:
        in_root: bool = self.in_main_menu
        self.set_current_command(value)
        if self.command_list_filter_function(value, in_root=in_root):
            handler: Callable[[None], None] = value[-1].handler
            is_cyclic: bool = self.has_flag(Flags.CYCLIC)
            is_addressed: bool = self.has_flag(Flags.ADDRESS)
            is_addressed_as_link: bool = self.has_flag(Flags.ADDRESS_AS_LINK)

            # title
            with self.output.make_indent(2):
                if (
                    not self.is_silence
                    and value[0] != self.all_commands_node
                    # and not value[0].as_link
                ):
                    title: str = self.get_command_title(value)
                    title_list: list[str] = title.split(nl())
                    title = title_list[0]
                    if ne(title):
                        self.output.head(title)
                    if len(title_list) > 1:
                        self.write_line(j(title_list[1:], nl()))
                # text
                text: str | None = self.get_command_node_text(
                    self.get_current_command_node()
                )
                if not A.D_C.empty(text):
                    with self.output.make_indent(2, True):
                        self.write_line(nl(text))
                # if self.helped and A.D.is_not_none(value[-1].help_text):
                # self.output.separated_line()
                """with self.output.make_indent(2, True):
                    self.write_line(
                        js(
                            (
                                b("Помощь"),
                                nl(),
                                js(
                                    (
                                        j(
                                            list(map(b, MobileHelper.PIH_KEYWORDS)),
                                            j((" ", i("или"), " ")),
                                        ),
                                        self.get_command_name(value),
                                        value[-1].help_text(),
                                    ),
                                ),
                            )
                        )
                    ) 
                """
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
                                f"{b(PIH.NAME.upper())} будет выполнять команду в зациклическом режиме."
                            )
                        )
                    if A.D.is_not_none(handler):
                        with self.output.make_indent(2, True):
                            handler()
                    if is_cyclic:
                        self.output.separated_line()
                    else:
                        break
            self.show_good_bye = True
        else:
            self.show_error(
                f"{self.user_given_name}, данная команда Вам недоступна.")
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
        filtered: list[str] = list(
            filter(lambda item: str(item).startswith("|"), value)
        )
        if len(filtered) > 0:
            value = filtered
        return j(
            (
                A.D.capitalize(
                    A.D.list_to_string(
                        list(map(lambda item: function(item), value)),
                        separator=" ",
                        filter_empty=True,
                    )
                ),
                j(
                    (
                        nl(),
                        f" {A.CT_V.BULLET} ",
                        "[ ",
                        j(
                            list(map(b, MobileHelper.PIH_KEYWORDS)),
                            j((" ", i("или"), " ")),
                        ),
                        " ]",
                        " ",
                        js(
                            list(
                                map(
                                    lambda item: self.get_command_node_help_label(
                                        item),
                                    value,
                                )
                            )
                        ),
                        A.D.check_not_none(
                            value[-1].help_text, lambda: value[-1].help_text(), ""
                        ),
                        A.D.check_not_none(value[-1].description, "", nl()),
                    )
                )
                if self.helped and value[-1].name_list != self.exit_node.name_list
                else "",
            )
        )

    def get_command_node_label(self, value: str | CommandNode | None = None) -> str:
        title_or_label: list[str] = self.get_command_node_title_or_label(value)
        return title_or_label[1] if len(title_or_label) > 1 else title_or_label[0]

    def get_command_name(self, value: list[CommandNode] | None = None) -> str:
        value = value or self.current_command
        return A.D.list_to_string(
            list(map(lambda item: self.get_command_node_name(item), value)),
            separator=" ",
            filter_empty=True,
        )

    def wait_for_input(self) -> bool:
        return self.stdin.wait_for_data_input

    def do_input(self, line: str):
        if self.stdin.wait_for_data_input:
            self.stdin.interrupt_type = (
                A.CT.MOBILE_HELPER.InteraptionTypes.EXIT
                if line.lower() in EXIT_KEYWORDS
                else 0
            )
            self.stdin.data = line
