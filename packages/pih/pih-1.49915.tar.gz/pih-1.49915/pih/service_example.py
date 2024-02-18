import ipih

from pih import A

SR = A.CT_SR
SC = A.CT_SC

#version 1.0

ROLE: SR = SR.DEVELOPER
if A.U.for_service(ROLE):

    from typing import Any
    from pih.tools import ParameterList

    def service_call_handler(sc: SC, parameter_list: ParameterList) -> Any:     
        return None
    
    def service_starts_handler() -> None:
        A.SRV_A.subscribe_on(SC.print_image)
       
    A.SRV_A.serve(ROLE, service_call_handler, service_starts_handler)
