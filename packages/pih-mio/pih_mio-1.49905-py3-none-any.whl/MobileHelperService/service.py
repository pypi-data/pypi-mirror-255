
import ipih
from pih.tools import nn, ne
from pih import A

from MobileHelperService.service_api import MobileHelperService

def checker(telephone_number: str) -> bool:
    if ne(A.SRV.get_support_host_list(A.CT_SR.MOBILE_HELPER)):
        am_i_admin: bool = telephone_number == A.D.get(A.CT_ME_WH.GROUP.PIH_CLI) or (
            nn(A.CT.TEST.USER) and telephone_number == A.D_TN.by_login(A.CT.TEST.USER)
        )
        if MobileHelperService.as_admin():
            return am_i_admin
        return not am_i_admin
    return True


MobileHelperService(None, checker).start()