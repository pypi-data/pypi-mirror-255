import ipih

from pih import A
from DataSourceService.const import SD, JOKE

# version: 0.9

SC = A.CT_SC


ISOLATED: bool = False


def start(as_standalone: bool = False) -> None:

    if A.U.for_service(SD, modules=["mysql-connector-python", "lmdbm", "dadata"]):

        from DataSourceService.api import DataStorageAndSourceApi as Api
        from pih.tools import ParameterList
        from pih.consts.errors import Error
        from pih.rpc import RPC

        from pih.collections import (
            OGRN,
            EventDS,
            GKeepItem,
            DelayedMessage,
            DelayedMessageDS,
            MessageSearchCritery,
            PolibasePersonVisitDS,
            CTIndicationsValueContainer,
            PolibasePersonInformationQuest,
            PolibasePersonVisitNotification,
            ChillerIndicationsValueContainer,
            PolibasePersonVisitNotificationDS,
            PolibasePersonNotificationConfirmation,
        )
        import grpc
        from typing import Any
        from dadata import Dadata
        import anecdotica as acalib

        api: Api = Api()

        def service_call_handler(sc: SC, pl: ParameterList, context) -> Any:
            if sc == SC.register_polibase_person_information_quest:
                return api.register_polibase_person_information_quest(
                    pl.next(PolibasePersonInformationQuest())
                )
            if sc == SC.search_polibase_person_information_quests:
                return A.R.pack(
                    None,
                    api.get_polibase_person_information_quests(
                        pl.next(PolibasePersonInformationQuest())
                    ),
                )
            if sc == SC.update_polibase_person_information_quest:
                return api.update_polibase_person_information_quest(
                    pl.next(PolibasePersonInformationQuest()),
                    pl.next(PolibasePersonInformationQuest()),
                )
            if sc == SC.get_settings_value:
                return A.R.pack(
                    A.CT_FCA.VALUE,
                    api.get_settings_value(pl.next(), pl.next()),
                )
            if sc == SC.set_settings_value:
                return api.set_settings_value(pl.next(), pl.next())
            if sc == SC.register_polibase_person_visit_notification:
                return api.register_polibase_person_visit_notification(
                    pl.next(PolibasePersonVisitNotificationDS())
                )
            if sc == SC.search_polibase_person_visit_notifications:
                return A.R.pack(
                    None,
                    api.search_polibase_person_visit_notifications(
                        pl.next(PolibasePersonVisitNotification())
                    ),
                )
            if sc == SC.update_polibase_person_visit_to_data_stogare:
                return api.add_polibase_person_visit(pl.next(PolibasePersonVisitDS()))
            if sc == SC.search_polibase_person_visits_in_data_storage:
                return A.R.pack(
                    None,
                    api.search_polibase_person_visit(pl.next(PolibasePersonVisitDS())),
                )
            if sc == SC.register_delayed_message:
                return api.register_delayed_message(pl.next(DelayedMessage()))
            if sc == SC.search_delayed_messages:
                return A.R.pack(
                    None,
                    api.get_delayed_messages(
                        pl.next(MessageSearchCritery()), pl.next()
                    ),
                )
            if sc == SC.update_delayed_message:
                return api.update_delayed_message(
                    pl.next(DelayedMessageDS()),
                    pl.next(MessageSearchCritery()),
                )
            if sc == SC.get_storage_value:
                return A.R.pack(
                    A.CT_FCA.VALUE,
                    api.get_storage_value(pl.next(), pl.next()),
                )
            if sc == SC.set_storage_value:
                return api.set_storage_value(pl.next(), pl.next(), pl.next())
            if sc == SC.update_polibase_person_notification_confirmation:
                return api.update_polibase_person_notification_confirmation(
                    pl.next(PolibasePersonNotificationConfirmation())
                )
            if sc == SC.search_polibase_person_notification_confirmation:
                return A.R.pack(
                    None,
                    api.search_polibase_person_notification_confirmation(
                        pl.next(PolibasePersonNotificationConfirmation())
                    ),
                )
            if sc == SC.register_ct_indications_value:
                return api.register_ct_indication_value(
                    pl.next(CTIndicationsValueContainer(A.D.now(second=0))),
                    pl.next(),
                )
            if sc == SC.register_chiller_indications_value:
                return api.register_chiller_indication_value(
                    pl.next(ChillerIndicationsValueContainer(A.D.now(second=0))),
                    pl.next(),
                )
            if sc == SC.execute_data_source_query:
                try:
                    return A.R.pack(A.CT_FCA.VALUE, api.execute_query(pl.next()))
                except Error as error:
                    return RPC.create_error(
                        context, error.details, grpc.StatusCode.INVALID_ARGUMENT
                    )
            if sc == SC.get_ogrn_value:
                section_name: str = "OGRN"
                ogrn: OGRN | None = None
                ogrn_code: str = str(pl.next())
                data: dict | None = api.get_storage_value(ogrn_code, section_name)
                if A.D.is_empty(data):
                    token: str = A.D_V_E.value("DADATA_TOKEN")
                    dadata: Dadata = Dadata(token)
                    result: list[dict] = dadata.find_by_id("party", ogrn_code)
                    if not A.D_C.empty(result):
                        data = result[0]
                        ogrn = OGRN(data["value"], ogrn_code, data)
                        api.set_storage_value(ogrn_code, data, section_name)
                else:
                    ogrn = OGRN(data["value"], ogrn_code, data)
                return A.R.pack(A.CT_FCA.VALUE, ogrn)
            if sc == SC.get_fms_unit_name:
                section_name: str = "FMS_UNIT"
                fms_unit_name: str | None = None
                fms_unit_code: str = str(pl.next())
                data: str | None = api.get_storage_value(fms_unit_code, section_name)
                if A.D.is_empty(data):
                    token: str = A.D_V_E.value("DADATA_TOKEN")
                    dadata: Dadata = Dadata(token)
                    result: list[dict] = dadata.find_by_id("fms_unit", fms_unit_code)
                    if not A.D_C.empty(result):
                        data = result[0]
                        fms_unit_name = data["value"]
                        api.set_storage_value(
                            fms_unit_code, fms_unit_name, section_name
                        )
                else:
                    fms_unit_name = data
                return A.R.pack(A.CT_FCA.VALUE, fms_unit_name)
            if sc == SC.get_last_ct_indications_value_container_list:
                return A.R.pack(
                    A.CT_FC.INDICATIONS.CT_VALUE_CONTAINER,
                    api.get_last_ct_indications_value_container_list(
                        pl.next(), pl.next()
                    ),
                )
            if sc == SC.get_last_сhiller_indications_value_container_list:
                return A.R.pack(
                    A.CT_FC.INDICATIONS.CHILLER_VALUE_CONTAINER,
                    api.get_last_chiller_indications_value_container_list(
                        pl.next(), pl.next()
                    ),
                )
            if sc == SC.get_gkeep_item_list_by_any:
                return A.R.pack(
                    None,
                    api.get_gkeep_item_list_by_any(pl.next(), pl.next(), pl.next()),
                )
            if sc == SC.add_gkeep_item:
                return A.R.pack(
                    A.CT_FC.VALUE,
                    api.add_gkeep_item(
                        GKeepItem(
                            pl.next(),
                            pl.next(),
                            pl.next(),
                        )
                    ),
                )
            if sc == SC.register_event:
                return api.register_event(pl.next(EventDS()))
            if sc == SC.get_event:
                return A.R.pack(A.CT_FC.VALUE, api.get_event(pl.next(EventDS())))
            if sc == SC.get_event_count:
                return A.R.pack(A.CT_FC.VALUE, api.get_event_count(pl.next(EventDS())))
            if sc == SC.remove_event:
                return api.remove_event(pl.next(EventDS()))
            if sc == SC.joke:
                reply = acalib.RandomItemApi.get_reply(
                    JOKE.USER_PROFILE, JOKE.API_SETTINGS
                )
                if reply.is_error():
                    print(
                        reply.get_result().get_error(), reply.get_result().get_err_msg()
                    )
                else:
                    return A.R.pack(A.CT_FC.VALUE, reply.get_item().get_text())

        A.SRV_A.serve(
            SD, service_call_handler, isolate=ISOLATED, as_standalone=as_standalone
        )


if __name__ == "__main__":
    start()
