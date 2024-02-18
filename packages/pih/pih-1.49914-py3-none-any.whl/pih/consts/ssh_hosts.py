from pih.consts.hosts import HOSTS as H
from pih.consts.addresses import ADDRESSES as ADDR
from enum import Enum

class SSHHosts(Enum):
    EMAIL_SERVER: str = ADDR.EMAIL_SERVER_ADDRESS
    SITE_API: str = ADDR.API_SITE_ADDRESS
    SITE: str = ADDR.SITE_ADDRESS
    SERVICES: str = H.SERVICES.NAME