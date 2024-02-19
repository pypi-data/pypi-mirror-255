import ipih

from pih.collections.service import ServiceDescription
from pih.consts.hosts import HOSTS
from enum import Enum, auto

NAME: str = "DataSource"

DATABASE_NAME: str = "pih_db"
DATABASE_PORT: int = 3306
DATABASE_POOL_SIZE: int = 5

HOST = HOSTS.BACKUP_WORKER

VERSION: str = "1.1"

SD: ServiceDescription = ServiceDescription(
    name=NAME,
    description="Data storage and source service",
    host=HOST.NAME,
    commands=[
        "register_polibase_person_information_quest",
        "search_polibase_person_information_quests",
        "update_polibase_person_information_quest",
        #
        "update_polibase_person_visit_to_data_stogare",
        "search_polibase_person_visits_in_data_storage",
        #
        "register_polibase_person_visit_notification",
        "search_polibase_person_visit_notifications",
        #
        "register_delayed_message",
        "search_delayed_messages",
        "update_delayed_message",
        #
        "get_settings_value",
        "set_settings_value",
        #
        "search_polibase_person_notification_confirmation",
        "update_polibase_person_notification_confirmation",
        #
        "get_storage_value",
        "set_storage_value",
        #
        "get_ogrn_value",
        "get_fms_unit_name",
        #
        "register_chiller_indications_value",
        "register_ct_indications_value",
        "get_last_ct_indications_value_container_list",
        "get_last_chiller_indications_value_container_list",
        #
        "get_gkeep_item_id",
        "add_gkeep_map_item",
        #
        "register_event",
        "get_event",
        "remove_event",
        #
        "execute_data_source_query"
        #
        "joke",
        "get_event_count",
    ],
    standalone_name="ds",
    version=VERSION,
)


class ACTIONS(Enum):
    SELECT: int = auto()
    DELETE: int = auto()
    INSERT: int = auto()
    COUNT: int = auto()


ANY_SYMBOL: str = "%"
SIGN_COLLECTION: list[str] = ["!=", ">=", "<=", "<>", ">", "<"]

POLIBASE_PERSON_INFORMATION_QUESTS_TABLE_NAME: str = (
    "polibase_person_information_quests"
)
POLIBASE_PERSON_VISITS_TABLE_NAME: str = "polibase_person_visits"
POLIBASE_PERSON_VISIT_NOTIFICATIONS_TABLE_NAME: str = (
    "polibase_person_visit_notifications"
)
POLIBASE_PERSON_NOTIFICATION_CONFIRMATIONS_TABLE_NAME: str = (
    "polibase_person_notification_confirmations"
)
#
CT_INDICATIONS_VALUE_TABLE_NAME: str = "ct_indications_value"
CHILLER_INDICATIONS_VALUE_TABLE_NAME: str = "chiller_indications_value"
#
GKEEP_MAP_TABLE: str = "gkeep_map"
EVENTS_TABLE: str = "events"
MESSAGE_BUFFER_TABLE_NAME: str = "message_buffer"
#
SETTINGS_SECTION: str = "pih_settings"
STORAGE_SECTION: str = "pih_storage"


class JOKE:
    
    USER_PROFILE: dict[str, str] = {
        "http_method": "POST",
        "pid": "e1u5962439l73iwnci9v",
        "key": "0ba083328cd4ba19272437f2293665163c9acc47c864311a0ed1441dfd61fc48",
    }
    
    API_SETTINGS: dict[str, int] = {
        # "category": 2,
        "lang": 1,
        "wlist": 1,
        "markup": 0,
    }
