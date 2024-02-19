from pih.consts.hosts import HOSTS
from pih.consts.addresses import ADDRESSES
from enum import Enum

class SSHHosts(Enum):
    EMAIL_SERVER: str = ADDRESSES.EMAIL_SERVER_ADDRESS
    SITE_API: str = ADDRESSES.API_SITE_ADDRESS
    SITE: str = ADDRESSES.SITE_ADDRESS
    SERVICES: str = HOSTS.SERVICES.NAME