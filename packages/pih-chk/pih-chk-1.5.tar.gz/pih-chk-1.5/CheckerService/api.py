from ssl import SSLCertVerificationError
import time
from urllib.error import URLError, HTTPError
import urllib.request
from typing import Callable
from datetime import datetime

import ipih
from pih import A, PIHThreadPoolExecutor
from CheckerService.const import *
from pih.rpc import RPC
from pih.tools import n, nn, ne, e, j, js, lw
from pih.collection import (
    User,
    Result,
    ResourceStatus,
    DiskStatistics,
    WSResourceStatus,
    SiteResourceStatus,
    DisksResourceStatus,
    ComputerDescription,
    ServerResourceStatus,
)


class CheckerApi:

    def __init__(self) -> None:

        self.resources_status_map: dict[str, ResourceStatus] = {}
        self.ws_status_map: dict[str, WSResourceStatus] = {}
        self.server_status_map: dict[str, ServerResourceStatus] = {}
        self.disk_resource_status_map: dict[str, DisksResourceStatus] = {}
        self.resources_accessable_map: dict[str, bool] = {}
        self.check_counter: int = 0

        for wappi_profile in A.CT_ME_WH_W.Profiles:
            RESOURCE_LIST.WAPPI.append(
                ResourceStatus(
                    wappi_profile.value,
                    js(("Профиль Wappi:", wappi_profile.name)),
                    (2, 50, 24 * 60),
                )
            )

        for site_resource_description in A.CT_R_D.SITE_LIST:
            RESOURCE_LIST.SITE.append(
                A.D.fill_data_from_source(
                    SiteResourceStatus(), site_resource_description
                )
            )

        def filter_function(workstation: ComputerDescription) -> bool:
            return A.C_WS.watchable(workstation)

        def ws_every_action(workstation: ComputerDescription) -> None:
            RESOURCE_LIST.WS.append(
                WSResourceStatus(
                    workstation.name,
                    j(
                        (
                            "Компьютер: ",
                            workstation.name,
                            " (",
                            workstation.description,
                            ")",
                        )
                    ),
                )
            )

        ws_description_result_list: Result[list[ComputerDescription]] = (
            A.R_WS.all_description()
        )
        A.R.every(
            ws_every_action, A.R.filter(filter_function, ws_description_result_list)
        )

        def server_every_action(server: ComputerDescription) -> None:
            RESOURCE_LIST.SERVER.append(
                ServerResourceStatus(
                    server.name, f"Сервер: {server.name} ({server.description})"
                )
            )

        server_description_result_list: Result[list[ComputerDescription]] = (
            A.R_SRVS.all_description()
        )
        A.R.every(server_every_action, server_description_result_list)

        RESOURCE_LIST.DISK_STATISTICS_COMPUTER_DESCRIPTION = (
            A.D_FL.computers_with_property(
                (ws_description_result_list + server_description_result_list).data,
                A.CT_AD.WSProperies.DiskReportable,
            )
        )

    def send_message_to_it_users(self, message: str) -> None:
        def every_action(user: User) -> None:
            A.ME_WS.to_user(user, message)

        A.R.every(every_action, A.R_U.by_job_position(A.CT_AD.JobPositions.IT))

    def update_resource_status_and_notify(
        self,
        value: ResourceStatus,
        accessable: bool,
        on_init_handler: Callable[[ResourceStatus, bool], None] | None = None,
        on_access_handler: Callable[[ResourceStatus, bool], None] | None = None,
        on_inaccess_handler: Callable[[ResourceStatus, bool], None] | None = None,
    ) -> None:
        self.resources_accessable_map[value.address] = value.accessable
        if (
            accessable
            and isinstance(value, SiteResourceStatus)
            and value.check_certificate_status
            and ne(value.certificate_status)
        ):
            accessable = lw(value.certificate_status).find("invalid") == -1
            if accessable:
                pass
        if accessable:
            value.inaccessibility_counter = 0
        else:
            value.inaccessibility_counter += 1
        accessable = A.C_R.accessibility(value)
        value.accessable = accessable
        if isinstance(value, WSResourceStatus):
            self.ws_status_map[value.address] = value
        elif isinstance(value, ServerResourceStatus):
            self.server_status_map[value.address] = value
        else:
            self.resources_status_map[value.address] = value

        if self.check_counter == value.inaccessibility_check_values[0]:
            if nn(on_init_handler):
                on_init_handler(value, accessable)
        else:
            if accessable:
                if self.resources_accessable_map[value.address] == False and nn(
                    on_access_handler
                ):
                    on_access_handler(value, value.inaccessibility_counter == 0)
            else:
                if (
                    value.inaccessibility_counter
                    <= value.inaccessibility_check_values[0]
                    + value.inaccessibility_check_values[1]
                ) or (
                    value.inaccessibility_counter
                    % value.inaccessibility_check_values[2]
                    == 0
                ):
                    if nn(on_inaccess_handler):
                        on_inaccess_handler(value, self.at_first_time(value))
        return accessable

    def on_inaccess_handler(
        self, resource_status: ResourceStatus, at_first_time: bool
    ) -> None:
        A.E.resource_inaccessible(resource_status, at_first_time)

    def on_access_handler(
        self, resource_status: ResourceStatus, at_first_time: bool
    ) -> None:
        #if at_first_time:
        A.E.resource_accessible(resource_status, at_first_time)

    def on_init_handler(
        self, resource_status: ResourceStatus, accessable: bool
    ) -> None:
        (
            A.E.resource_accessible(resource_status, True)
            if accessable
            else A.E.resource_inaccessible(resource_status, True)
        )

    def at_first_time(self, resource_status: ResourceStatus) -> bool:
        return (
            resource_status.inaccessibility_counter
            == resource_status.inaccessibility_check_values[0],
        )

    def set_disk_resource_status(self, value: ComputerDescription) -> None:
        def set_disk_resource_status_for_host(
            host: str, disk_statistics: DiskStatistics
        ) -> None:
            if disk_statistics.size != 0:
                if host not in self.disk_resource_status_map:
                    self.disk_resource_status_map[host] = DisksResourceStatus(host)
                self.disk_resource_status_map[host].disk_list.append(disk_statistics)

        self.disk_resource_status_map = {}
        A.D.every(
            lambda item: set_disk_resource_status_for_host(value.name, item),
            A.EXC.get_disk_statistics_list(value.name),
        )

    def ws_or_server_check(
        self,
        resource_status: ResourceStatus,
        check_function: Callable[[ResourceStatus], bool],
        events: tuple[A.CT_E],
    ) -> None:
        def on_access_handler(
            resource_status: ResourceStatus, at_first_time: bool
        ) -> None:
            if at_first_time:
                A.E.send(events[0], (resource_status.address,))

        def on_inaccess_handler(
            resource_status: ResourceStatus, at_first_time: bool
        ) -> None:
            if at_first_time:
                A.E.send(events[1], (resource_status.address,))

        self.update_resource_status_and_notify(
            resource_status,
            check_function(resource_status),
            lambda _, accessable: (
                on_access_handler(resource_status, True)
                if accessable
                else on_inaccess_handler(resource_status, True)
            ),
            on_access_handler,
            on_inaccess_handler,
        )

    def check_resources(
        self, force_update: bool = False, current_datetime: datetime | None = None
    ) -> None:
        start: float = time.perf_counter()
        self.check_counter += 1
        self.action_at_work = True
        #
        self.update_resource_status_and_notify(
            RESOURCE_LIST.INTERNET,
            A.C_R.accessibility_by_ping(RESOURCE_LIST.INTERNET.address, None, 2, False),
        )
        site_check_free_space_perion_in_minutes: int = (
            A.S_R.site_check_free_space_perion_in_minutes()
        )
        site_check_certificate_start_time: datetime = (
            A.S_R.site_check_certificate_start_time()
        )
        if not RESOURCE_LIST.INTERNET.accessable:
            self.send_message_to_it_users("Вероятно, интернет отсутствует")
        else:

            def check_site(site_resource_status: SiteResourceStatus) -> None:
                site_address: str = site_resource_status.address
                try:
                    if force_update or ne(current_datetime):
                        if site_resource_status.check_free_space_status:
                            if (
                                e(site_resource_status.free_space_status)
                                or force_update
                                or (
                                    (
                                        (RPC.SESSION.life_time.total_seconds() // 60)
                                        % site_check_free_space_perion_in_minutes
                                    )
                                    == 0
                                )
                            ):
                                site_resource_status.free_space_status = A.R_SSH.get_unix_free_space_information_by_drive_name(
                                    site_resource_status.driver_name, site_address
                                ).data
                        if site_resource_status.check_certificate_status:
                            if (
                                e(site_resource_status.certificate_status)
                                or force_update
                                or (
                                    ne(current_datetime)
                                    and A.D.is_equal_by_time(
                                        current_datetime,
                                        site_check_certificate_start_time,
                                    )
                                )
                            ):
                                site_resource_status.certificate_status = (
                                    A.R_SSH.get_certificate_information(
                                        site_address
                                    ).data
                                )
                    url: str = j(
                        (
                            A.D.check(
                                site_resource_status.internal,
                                A.CT.UNTRUST_SITE_PROTOCOL,
                                A.CT.SITE_PROTOCOL,
                            ),
                            site_address,
                        )
                    )
                    self.update_resource_status_and_notify(
                        site_resource_status,
                        urllib.request.urlopen(url).getcode() == 200,
                        self.on_init_handler,
                        self.on_access_handler,
                        self.on_inaccess_handler,
                    )
                except URLError as error:
                    if isinstance(error.reason, SSLCertVerificationError):
                        self.update_resource_status_and_notify(
                            site_resource_status, False
                        )
                        A.E.resource_inaccessible(
                            site_resource_status,
                            self.at_first_time(site_resource_status),
                            A.CT_R_IR.CERTIFICATE_ERROR,
                        )
                        
                    if isinstance(error, HTTPError) and error.code == 503:
                        self.update_resource_status_and_notify(
                            site_resource_status, False
                        )
                        A.E.resource_inaccessible(
                            site_resource_status,
                            self.at_first_time(site_resource_status),
                            A.CT_R_IR.SERVICE_UNAVAILABLE,
                        )

            #
            with PIHThreadPoolExecutor(max_workers=len(RESOURCE_LIST.SITE)) as executor:
                future_to_site_resources_status = {
                    executor.submit(
                        A.ER.wrap(check_site), site_resource_status
                    ): site_resource_status
                    for site_resource_status in RESOURCE_LIST.SITE
                }
            #
            for wappi_resource in RESOURCE_LIST.WAPPI:
                self.update_resource_status_and_notify(
                    wappi_resource,
                    A.C_R.wappi_profile_accessibility(wappi_resource.address),
                    self.on_init_handler,
                    self.on_access_handler,
                    self.on_inaccess_handler,
                )
            #
            if self.update_resource_status_and_notify(
                RESOURCE_LIST.VPN_PACS_SPB,
                A.C_R.vpn_pacs_accessibility(),
                self.on_init_handler,
                self.on_access_handler,
                self.on_inaccess_handler,
            ):
                #
                self.update_resource_status_and_notify(
                    RESOURCE_LIST.PACS_SPB,
                    A.C_R.pacs_accessibility(),
                    self.on_init_handler,
                    self.on_access_handler,
                    self.on_inaccess_handler,
                )
            else:
                self.update_resource_status_and_notify(RESOURCE_LIST.PACS_SPB, False)
        #
        self.update_resource_status_and_notify(
            RESOURCE_LIST.POLIBASE1,
            A.C_R.polibase_accessibility(),
            self.on_init_handler,
            self.on_access_handler,
            self.on_inaccess_handler,
        )
        self.update_resource_status_and_notify(
            RESOURCE_LIST.POLIBASE2,
            A.C_R.polibase_accessibility(test=True),
            self.on_init_handler,
            self.on_access_handler,
            self.on_inaccess_handler,
        )
        if not RESOURCE_LIST.POLIBASE1.accessable:
            self.send_message_to_it_users("Полибейс недоступен")
        #
        with PIHThreadPoolExecutor(max_workers=len(RESOURCE_LIST.WS)) as executor:
            future_to_ws_resources_status = {
                executor.submit(
                    A.ER.wrap(self.ws_or_server_check),
                    ws_resource_status,
                    lambda resource_status: A.C_R.accessibility_by_smb_port(
                        resource_status.address, count=2, check_all=False
                    ),
                    (
                        A.CT_E.WATCHABLE_WORKSTATION_IS_ACCESSABLE,
                        A.CT_E.WATCHABLE_WORKSTATION_IS_NOT_ACCESSABLE,
                    ),
                ): ws_resource_status
                for ws_resource_status in RESOURCE_LIST.WS
            }
        #
        with PIHThreadPoolExecutor(max_workers=len(RESOURCE_LIST.SERVER)) as executor:
            future_to_server_resources_status = {
                executor.submit(
                    A.ER.wrap(self.ws_or_server_check),
                    server_resource_status,
                    lambda resource_status: A.C_R.accessibility_by_ping(
                        resource_status.address, count=2, check_all=False
                    ),
                    (A.CT_E.SERVER_IS_ACCESSABLE, A.CT_E.SERVER_IS_NOT_ACCESSABLE),
                ): server_resource_status
                for server_resource_status in RESOURCE_LIST.SERVER
            }
        #
        with PIHThreadPoolExecutor(
            max_workers=len(RESOURCE_LIST.DISK_STATISTICS_COMPUTER_DESCRIPTION)
        ) as executor:
            future_to_disk_statistics = {
                executor.submit(
                    A.ER.wrap(self.set_disk_resource_status),
                    disk_statistics_computer_description,
                ): disk_statistics_computer_description
                for disk_statistics_computer_description in RESOURCE_LIST.DISK_STATISTICS_COMPUTER_DESCRIPTION
            }
        #
        print("Время:", str(time.perf_counter() - start))
        print("Resources", self.resources_status_map)
        print("Disk statistics", self.disk_resource_status_map)
