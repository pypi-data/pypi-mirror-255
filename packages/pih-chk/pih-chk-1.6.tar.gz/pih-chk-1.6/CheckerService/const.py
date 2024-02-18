import ipih

from pih import A
from pih.rpc_collection import ServiceDescription
from pih.consts.hosts import HOSTS
from pih.collection import ResourceStatus, ComputerDescription, SiteResourceStatus

NAME: str = "Checker"

HOST = HOSTS.BACKUP_WORKER.NAME

SD: ServiceDescription = ServiceDescription(
    name=NAME,
    description="Checker service",
    host=HOST,
    commands=["get_resource_status_list"],
    standalone_name="chk",
    version="1.6"
)


class RESOURCE_LIST:

    INTERNET: ResourceStatus = A.D.fill_data_from_source(
        ResourceStatus(), A.CT_R_D.INTERNET
    )

    VPN_PACS_SPB: ResourceStatus = A.D.fill_data_from_source(
        ResourceStatus(), A.CT_R_D.VPN_PACS_SPB
    )

    PACS_SPB: ResourceStatus = A.D.fill_data_from_source(
        ResourceStatus(), A.CT_R_D.PACS_SPB
    )

    SITE: list[SiteResourceStatus] = []

    WAPPI: list[ResourceStatus] = []

    WS: list[ResourceStatus] = []

    SERVER: list[ResourceStatus] = []

    DISK_STATISTICS_COMPUTER_DESCRIPTION: list[ComputerDescription] = []

    POLIBASE1: ResourceStatus = A.D.fill_data_from_source(
        ResourceStatus(), A.CT_R_D.POLIBASE1
    )

    POLIBASE2: ResourceStatus = A.D.fill_data_from_source(
        ResourceStatus(), A.CT_R_D.POLIBASE2
    )

    DISK_STATISTICS_COMPUTER_DESCRIPTION: list[ComputerDescription] = []
