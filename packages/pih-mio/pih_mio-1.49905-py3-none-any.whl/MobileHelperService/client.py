import ipih

from enum import Enum
from collections import defaultdict
from typing import Callable, Any

from pih import A, IClosable
from pih.const import ARGUMENT_PREFIX
from MobileHelperService.api import (
    MobileOutput,
    MobileSession,
    Flags,
    format_given_name,
    mio_command,
    MobileHelperUserSettiongsHolder,
)
from MobileHelperService.const import (
    MODULE_NAME,
    VERSION,
    ADMIN_ALIAS,
    COMMAND_KEYWORDS,
    InterruptionTypes,
)
from pih.tools import ne, e, n, j, js, nn, ParameterList
from pih.collection import WhatsAppMessage
from pih.errors import OperationCanceled, OperationExit

ANSWER: dict[str, list[str]] = defaultdict(list)


class Client:
    class CT:
        S_UF = A.CT_AD.UserProperies

    @staticmethod
    def start(
        host: str,
        host_is_linux: bool | None = None,
        as_admin: bool = False,
        as_standalone: bool = False,
        ipih_install: bool = False,
        pih_install: bool = False,
        show_output: bool = True,
    ) -> bool:
        if A.OS.python_exists(host, host_is_linux=host_is_linux):
            if as_standalone:
                A.U.install_module(
                    MODULE_NAME,
                    VERSION,
                    show_output=show_output,
                    host=host,
                    host_is_linux=host_is_linux
                )
                returncode_result: bool | None = A.EXC.extract_returncode(
                    A.EXC.execute(
                        A.EXC.create_command_for_psexec(
                            [
                                MODULE_NAME,
                                j((ARGUMENT_PREFIX, ADMIN_ALIAS)) if as_admin else None,
                            ],
                            host,
                        ),
                        show_output=show_output,
                    ),
                    check_on_success=True,
                )
                if n(returncode_result):
                    result: str = str(
                        A.R_SSH.execute(
                            js(
                                (
                                    MODULE_NAME,
                                    j((ARGUMENT_PREFIX, ADMIN_ALIAS))
                                    if as_admin
                                    else "",
                                )
                            ),
                            host,
                        ).data
                    )
                    return result
                return returncode_result
            else:
                return A.SRV_A.start(
                    A.CT_SR.MOBILE_HELPER,
                    check_if_started=False,
                    show_output=show_output,
                    parameters=j((ARGUMENT_PREFIX, ADMIN_ALIAS)) if as_admin else None,
                    host=host,
                    host_is_linux=host_is_linux,
                    ipih_install=ipih_install,
                    pih_install=pih_install
                )
        else:
            raise Exception("Python is not exists on host")

    @staticmethod
    def create_output(recipient: str | Enum) -> MobileOutput:
        recipient = A.D.get(recipient)
        session: MobileSession = MobileSession(recipient, A.D.get(Flags.SILENCE))
        recipient_as_whatsapp_group: bool = recipient.endswith(A.CT_ME_WH.GROUP_SUFFIX)
        output: MobileOutput = MobileOutput(session)
        session.output = output
        if not recipient_as_whatsapp_group:
            output.user.get_formatted_given_name = lambda: format_given_name(
                session, output
            )
            session.say_hello(recipient)
        return output

    @staticmethod
    def waiting_for_result(
        command: str,
        recipient: str | Enum,
        chat_id: str | Enum | None = None,
        flags: int | None = None,
        args: tuple[Any] | None = None,
    ) -> Any | None:
        recipient = A.D.get(recipient)
        chat_id = A.D.get(chat_id)
        return_result_key: str = A.D.uuid()
        A.A_MIO.send_command_to(
            command, recipient, chat_id, flags, return_result_key, args
        )

        class DH:
            exception: BaseException | None = None

        def internal_handler(pl: ParameterList, listener: IClosable) -> None:
            event, parameters = A.D_Ex_E.with_parameters(pl)
            if event == A.CT_E.RESULT_WAS_RETURNED:
                if parameters[0] == return_result_key:
                    if parameters[2] == A.D.get(InterruptionTypes.CANCEL):
                        DH.exception = OperationCanceled()
                    if parameters[2] == A.D.get(InterruptionTypes.EXIT):
                        DH.exception = OperationExit()
                    ANSWER[j((recipient, chat_id), "-")].append(parameters[1])
                    listener.close()

        A.E.on_event(internal_handler)
        if nn(DH.exception):
            raise DH.exception
        return ANSWER[j((recipient, chat_id), "-")][-1]

    @staticmethod
    def ask(
        title: str,
        recipient: str | Enum,
        chat_id: str | Enum | None = None,
        flags: int | None = None,
    ) -> Any | None:
        return Client.waiting_for_result(
            mio_command(COMMAND_KEYWORDS.ASK), recipient, chat_id, flags, (title,)
        )

    @staticmethod
    def ask_yes_no(
        title: str,
        recipient: str | Enum,
        chat_id: str | Enum | None = None,
        flags: int | None = None,
    ) -> bool | None:
        return Client.waiting_for_result(
            mio_command(COMMAND_KEYWORDS.ASK_YES_NO),
            recipient,
            chat_id,
            flags,
            (title,),
        )

    @staticmethod
    def waiting_for_answer_from(
        recipient: str,
        handler: Callable[[str, Callable[[None], None]], None] | None = None,
    ) -> str | None:
        def internal_handler(
            message: str, close_handler: Callable[[None], None]
        ) -> None:
            ANSWER[recipient].append(message)
            if n(handler):
                close_handler()
            else:
                handler(message, close_handler)

        Client.waiting_for_input_from(recipient, internal_handler)
        return ANSWER[recipient][-1]

    @staticmethod
    def waiting_for_input_from(
        recipient: str,
        handler: Callable[[str, Callable[[None], None]], None] | None = None,
    ) -> None:
        def internal_handler(pl: ParameterList, listener: IClosable) -> None:
            message: WhatsAppMessage | None = A.D_Ex_E.whatsapp_message(pl)
            if ne(message) and A.D_F.telephone_number(
                message.sender
            ) == A.D_F.telephone_number(recipient):
                if n(handler):
                    listener.close()
                else:
                    handler(message.message, listener.close)

        A.E.on_event(internal_handler)

    class SETTINGS:
        class USER(MobileHelperUserSettiongsHolder):
            pass
