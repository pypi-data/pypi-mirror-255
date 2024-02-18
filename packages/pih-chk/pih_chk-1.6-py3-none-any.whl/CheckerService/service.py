import ipih

from pih import A
from CheckerService.const import SD
from CheckerService.api import CheckerApi as Api
from pih.tools import e, ne, n, nn, BitMask as BM, js, j

# version 1.0
SC = A.CT_SC

ISOLATED: bool = False

api: Api = Api()

from typing import Any
from datetime import datetime
from pih.const import CheckableSections
from pih.collection import (
    EventDS,
    Workstation,
    ResourceStatus,
    WSResourceStatus,
    ChillerIndicationsValueContainer,
)
from pih.rpc_collection import SubscribtionResult
from pih.tools import ParameterList

CHILLER_ALERT_COUNT_DEFAULT: int = A.S.get(A.CT_S.CHILLER_COUNT_DEFAULT)

class DH:
    current_datetime: datetime | None = None
    action_at_work: bool = False
    chiller_alert_count: int = CHILLER_ALERT_COUNT_DEFAULT
    

def check_resources_handler(force_update: bool, current_datetime: datetime) -> None:
    DH.action_at_work = True
    api.check_resources(force_update, current_datetime)
    DH.action_at_work = False

def service_call_handler(sc: SC, parameter_list: ParameterList) -> Any:
    if sc == SC.heart_beat:
        current_datetime: datetime = A.D_Ex.parameter_list(parameter_list).get()
        DH.current_datetime = current_datetime
        if not DH.action_at_work:
            check_resources_handler(False, current_datetime)
        return True
    if sc == SC.register_chiller_indications_value:
        subscribtion_result: SubscribtionResult | None = A.D_Ex.subscribtion_result(
            parameter_list
        )
        if nn(subscribtion_result):
            result: dict[str, Any] | None = subscribtion_result.result
            if ne(result):
                event_type: A.CT_E | None = None
                indications_value_container: ChillerIndicationsValueContainer = (
                    A.D.fill_data_from_source(
                        ChillerIndicationsValueContainer(), result
                    )
                )
                if (
                    indications_value_container.indicators
                    == A.CT_I.CHILLER.INDICATOR_EMPTY_DISPLAY
                ):
                    event_type = A.E_B.chiller_was_turned_off()
                    if A.C_IND.chiller_on():
                        A.E.send(
                            event_type,
                        )
                    else:
                        if DH.current_datetime.minute == 0:
                            A.E.send(
                                event_type,
                                flags=BM.remove(
                                    BM.set(A.D.get(event_type).flags),
                                    A.CT_L_ME_F.SAVE,
                                ),
                            )
                else:
                    if nn(indications_value_container.temperature):
                        event_off: EventDS | None = A.R.get_first_item(
                            A.R_E.get_last(A.E_B.chiller_was_turned_off())
                        )
                        event_type_on: A.CT_E = A.E_B.chiller_was_turned_on()
                        if nn(event_off):
                            event_on: EventDS | None = A.R.get_first_item(
                                A.R_E.get_last(event_type_on)
                            )
                            if n(event_on) or not A.C_IND.chiller_on():
                                A.E.send(event_type_on)
                        if indications_value_container.temperature > A.S.get(
                            A.CT_S.CHILLER_ALERT_TEMPERATURE
                        ):
                            DH.chiller_alert_count -= 1
                            if DH.chiller_alert_count <= 0:
                                event_type = (
                                    A.E_B.chiller_temperature_alert_was_fired()
                                )
                                if A.C_E.timeouted(event_type, None, 5 * 60):
                                    A.E.send(event_type)
                        else:
                            if DH.chiller_alert_count < 0:
                                DH.chiller_alert_count = CHILLER_ALERT_COUNT_DEFAULT
                                event_type = (
                                    A.E_B.chiller_temperature_alert_was_resolved()
                                )
                                if A.C_E.timeouted(
                                    event_type, timeout_in_seconds=5 * 60
                                ):
                                    A.E.send(event_type)
                return True
        return False
    if sc == SC.get_resource_status_list:
        section_list: list[str] | None = parameter_list.next()
        force_update: bool = parameter_list.next()
        if force_update:
            api.check_resources(True)
        result: list[ ResourceStatus] = []
        if e(section_list):
            result = A.D.to_list(api.resources_status_map)
        else:
            all: bool = parameter_list.next()
            section: str | None = None
            for section in section_list:
                section = section.upper()
                if section == CheckableSections.RESOURCES.name:
                    result += A.D.to_list(api.resources_status_map)
                if section == CheckableSections.WS.name:
                    if all:

                        def map_function(
                            workstation: Workstation,
                        ) -> WSResourceStatus:
                            return WSResourceStatus(
                                workstation.name,
                                f"Компьютер: {workstation.name} ({workstation.description})",
                                None,
                                workstation.accessable,
                                None,
                            )

                        result += A.R.map(map_function, A.R_WS.all()).data
                    else:
                        result += A.D.to_list(api.ws_status_map)
                if section == CheckableSections.SERVERS.name:
                    result += A.D.to_list(api.server_status_map)
                if section == CheckableSections.DISKS.name:
                    result += A.D.to_list(api.disk_resource_status_map)
                
        return A.R.pack(A.CT_FCA.VALUE, result)
    return True

def service_starts_handler() -> None:
    A.SRV_A.subscribe_on(SC.heart_beat)
    A.SRV_A.subscribe_on(SC.register_chiller_indications_value)


def start(as_standalone: bool = False) -> None:
    A.SRV_A.serve(SD, service_call_handler, service_starts_handler, isolate=ISOLATED, as_standalone=as_standalone)

if __name__ == "__main__":
    start()