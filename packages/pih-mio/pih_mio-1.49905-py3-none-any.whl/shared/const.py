import importlib.util
import sys

pih_is_exists = importlib.util.find_spec("pih") is not None
if not pih_is_exists:
    sys.path.append("//pih/facade")
from shared.hosts import HOSTS
from pih.rpc_collection import ServiceDescription
from enum import Enum

POLIBASE_BASE: ServiceDescription = ServiceDescription(
    host=HOSTS.POLIBASE.NAME,
    pyton_executor_path=r"C:\Users\adm\AppData\Local\Programs\Python\Python310\python.exe",
    run_from_system_account=True,
)


class MESSAGE:
    class WHATSAPP:
        SITE_NAME: str = "https://wa.me/"
        SEND_MESSAGE_TO_TEMPLATE: str = SITE_NAME + "{}?text={}"

        GROUP_SUFFIX: str = "@g.us"

        class GROUP(Enum):
            IT: str = "120363163438805316@g.us"
            RD: str = "79146947050-1595848245@g.us"
            MAIN: str = "79644300470-1447044803@g.us"
            EMAIL_CONTROL: str = "120363159605715569@g.us"
            CT_INDICATIONS: str = "120363084280723039@g.us"
            DOCUMENTS_WORK_STACK: str = "120363115241877592@g.us"
            REGISTRATION_AND_CALL: str = "79242332784-1447983812@g.us"
            DOCUMENTS_WORK_STACK_TEST: str = "120363128816931482@g.us"
            CONTROL_SERVICE_INDICATIONS: str = "120363159210756301@g.us"

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
                CALL_CENTRE: str = "81b820f8-cd6e"
                MARKETER: str = "c31db01c-b6d6"
                DEFAULT: str = CALL_CENTRE

            AUTHORIZATION: str = "6b356d3f53124af3078707163fdaebca3580dc38"
