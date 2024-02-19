import ipih

from pih import A, PIHThreadPoolExecutor
from pih.collections import (
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
from pih.consts import MessageStatuses
from DataSourceService.const import *

from shared.tools import JsonLmdb
from pih.tools import if_else, j, js, escs, ne, e, n, nn, one
from pih.consts.errors import Error
from pih.consts.names import KEYWORD_COLLECTION

from mysql.connector import pooling
from mysql.connector import ProgrammingError
from mysql.connector.pooling import PooledMySQLConnection
from typing import Any, Callable
import dataclasses
from datetime import datetime, date
from concurrent.futures import Future, as_completed

executor: PIHThreadPoolExecutor = PIHThreadPoolExecutor(max_workers=1)
executor_task_list: list[Future] = []


class DataStorageAndSourceApi:
    def __init__(self) -> None:
        self.connection_pool = pooling.MySQLConnectionPool(
            pool_name="pool",
            pool_size=DATABASE_POOL_SIZE,
            pool_reset_session=True,
            host=A.CT_H.BACKUP_WORKER.ALIAS,
            user=A.D_V_E.value(A.CT_LNK.DATABASE_ADMINISTRATOR_LOGIN),
            password=A.D_V_E.value(A.CT_LNK.DATABASE_ADMINISTRATOR_PASSWORD),
            database=DATABASE_NAME,
            port=DATABASE_PORT,
        )
        self.cached_ct_indications_value_container_list: list[
            CTIndicationsValueContainer
        ] = []
        self.cached_chiller_indications_value_container_list: list[
            ChillerIndicationsValueContainer
        ] = []
        self.storage_section_map: dict[str, JsonLmdb] = {}

    def create_connection(self) -> PooledMySQLConnection:
        return self.connection_pool.get_connection()

    def execute(
        self,
        function: Callable[[PooledMySQLConnection], Any | None],
        default_value: Any | None = None,
        use_return_of_action: bool = True,
        catch_exception: bool = False,
    ) -> Any | None:
        result: Any | None = default_value
        connection: PooledMySQLConnection | None = None
        try:
            connection = self.create_connection()
            temp_result: Any | None = function(connection)
            if use_return_of_action:
                result = temp_result
        except ProgrammingError as error:
            A.ER.global_except_hook(error)
            if catch_exception:
                raise Error(error._full_msg, None)
        finally:
            if ne(connection):
                connection.close()
        return result

    def get_settings_value(self, key: str, default_value: Any | None = None) -> Any:
        result: dict | None = self.get_storage_value(key, SETTINGS_SECTION)
        if n(result):
            self.set_settings_value(key, default_value)
        return result

    def set_settings_value(self, key: str, value: Any) -> bool:
        self.set_storage_value(key, value, SETTINGS_SECTION)
        return True

    def get_storage_container(self, section: str) -> JsonLmdb:
        if section not in self.storage_section_map:
            self.storage_section_map[section] = JsonLmdb.open(
                A.PTH.join(A.PTH_DS.DATA_FOLDER, A.PTH.add_extension(section, "db")),
                "c",
            )
        return self.storage_section_map[section]

    def set_storage_value(
        self, key: str, value: dict | None, section: str | None = None
    ) -> bool:
        section = section or STORAGE_SECTION
        db: JsonLmdb = self.get_storage_container(section)
        if e(value):
            del db[key]
        else:
            db[key] = value
        return True

    def get_storage_value(
        self, key: str | None, section: str | None = None
    ) -> dict | None:
        section = section or STORAGE_SECTION
        db: JsonLmdb = self.get_storage_container(section)
        result: dict | None = None
        if e(key):
            result = {}
            for key in db:
                result[key] = db[key]
        else:
            if key in db:
                result = db[key]
        return result

    def get_events_table_field_list(self) -> list[str]:
        return [A.CT_FNC.NAME, A.CT_FNC.PARAMETERS, A.CT_FNC.TIMESTAMP, A.CT_FNC.ID]

    def create_insert_query(
        self,
        table_name: str,
        data: Any,
        field_list: list[str] | None = None,
        replace: bool = False,
    ) -> str:
        field_list = field_list or A.D.fields(data)
        data_item_list: list[Any] = [
            getattr(data, field.name) for field in dataclasses.fields(data)
        ]
        return js(
            (
                ["insert", "replace"][replace],
                "into",
                table_name,
                A.D.list_to_string(field_list, start="(", end=")"),
                "values",
                "(",
                A.D.list_to_string(
                    list(
                        map(
                            lambda data_item: A.D_F.as_string(
                                data_item,
                                True,
                                lambda item: A.D.check_not_none(
                                    item, lambda: item, "NULL"
                                ),
                            ),
                            data_item_list,
                        )
                    )
                ),
                ")",
            )
        )

    def register_event(self, value: EventDS) -> bool:
        executor_task_list.append(
            executor.submit(
                lambda value: self.execute_event_action(ACTIONS.INSERT, value),
                value,
            )
        )
        for result_holder in as_completed(executor_task_list):
            return result_holder.result()

    def get_event(self, value: EventDS) -> list[EventDS]:
        return self.execute_event_action(ACTIONS.SELECT, value)

    def get_event_count(self, value: EventDS) -> list[EventDS]:
        return self.execute_event_action(ACTIONS.COUNT, value)

    def remove_event(self, value: EventDS) -> bool:
        return self.execute_event_action(ACTIONS.DELETE, value)

    def execute_event_action(
        self, value: ACTIONS, event: EventDS
    ) -> list[EventDS] | bool:
        event_name: str | None = event.name
        parameters: dict[str, Any] | None = event.parameters
        result: list[EventDS] | int | bool = if_else(
            value == ACTIONS.SELECT, [], if_else(value == ACTIONS.COUNT, 0, False)
        )

        def action(
            connection: PooledMySQLConnection, result: list[EventDS] | bool
        ) -> list[EventDS] | bool:
            cursor = connection.cursor(dictionary=True)
            query_string: str | None = None
            if value in [ACTIONS.DELETE, ACTIONS.SELECT, ACTIONS.COUNT]:
                parameter_list: list[Any] = A.D.filter(
                    lambda item: nn(item[1]), list((parameters or {}).items())
                )
                condition_statement_list: list[str] = []
                if ne(event_name):
                    condition_statement_list += [
                        j((A.CT_FNC.NAME, "=", escs(event_name)))
                    ]
                if ne(parameter_list):
                    is_sign_symbol: bool = False
                    is_list: bool = False
                    condition_statement_list += [
                        j(
                            (
                                "parameters->",
                                escs(j(("$.", key))),
                                (
                                    j((" ", value[0], " "))
                                    if (
                                        (is_list := isinstance(value, list))
                                        and (
                                            is_sign_symbol := value[0].lower()
                                            in (
                                                SIGN_COLLECTION
                                                + [KEYWORD_COLLECTION.LIKE]
                                            )
                                        )
                                    )
                                    else "="
                                ),
                                A.D_F.as_string(
                                    (
                                        j((ANY_SYMBOL, value[1], ANY_SYMBOL))
                                        if is_sign_symbol
                                        and value[0].lower() == KEYWORD_COLLECTION.LIKE
                                        else value[1] if is_list else value
                                    ),
                                    escaped_string=True,
                                ),
                            )
                        )
                        for key, value in parameter_list
                    ]
                timestamp: datetime | date | str | int | None = event.timestamp
                if ne(timestamp):
                    if isinstance(timestamp, str):
                        timestamp_sign: str | None = None
                        try:
                            timestamp = A.D.datetime_or_date_from_string(timestamp)
                        except ValueError as _:
                            for sign in SIGN_COLLECTION:
                                if timestamp.startswith(sign):
                                    timestamp = A.D.datetime_or_date_from_string(
                                        timestamp[len(sign) :].lstrip()
                                    )
                                    timestamp_sign = sign
                                    break
                        if n(timestamp_sign):
                            if isinstance(timestamp, datetime):
                                timestamp = j(("=", escs(timestamp)))
                            elif isinstance(timestamp, date):
                                timestamp = j(
                                    (
                                        KEYWORD_COLLECTION.LIKE,
                                        escs(j((event.timestamp, ANY_SYMBOL))),
                                    )
                                )
                        else:
                            timestamp = j((timestamp_sign, escs(timestamp)))
                        condition_statement_list.append(j(("timestamp", timestamp)))
                query_string = js(
                    (
                        if_else(
                            value in [ACTIONS.SELECT, ACTIONS.COUNT], "select", "delete"
                        ),
                        if_else(
                            value == ACTIONS.SELECT,
                            A.D.list_to_string(self.get_events_table_field_list()),
                            if_else(value == ACTIONS.COUNT, "count(*)", ""),
                        ),
                        js(
                            (
                                "from",
                                EVENTS_TABLE,
                                (
                                    ""
                                    if e(condition_statement_list)
                                    else js(
                                        ("where", j(condition_statement_list, " and "))
                                    )
                                ),
                                (
                                    js(
                                        (
                                            "order by timestamp",
                                            "asc" if timestamp > 0 else "desc",
                                            "limit",
                                            abs(timestamp),
                                        )
                                    )
                                    if isinstance(timestamp, int)
                                    else None
                                ),
                            )
                        ),
                    )
                )
            if value == ACTIONS.INSERT:
                query_string = self.create_insert_query(
                    EVENTS_TABLE, event, self.get_events_table_field_list()
                )
            cursor.execute(query_string)
            if value == ACTIONS.SELECT:
                for item in cursor:
                    result.append(
                        A.D.fill_data_from_source(
                            EventDS(), {**item}, copy_by_index=True
                        )
                    )
            if value == ACTIONS.COUNT:
                for item in cursor:
                    result = one({**item})
                    break
            if value in [ACTIONS.DELETE, ACTIONS.INSERT]:
                connection.commit()
                result = cursor.rowcount != 0
            return result

        return self.execute(lambda connection: action(connection, result), result)

    def register_polibase_person_information_quest(
        self, value: PolibasePersonInformationQuest
    ) -> bool:
        return self.execute_insert(
            f"insert into {POLIBASE_PERSON_INFORMATION_QUESTS_TABLE_NAME} ({A.CT_FNC.PIN}, {A.CT_FNC.FULL_NAME}, {A.CT_FNC.TELEPHONE_NUMBER}) value ({value.pin}, '{value.FullName}', '{value.telephoneNumber}')"
        )

    def register_ct_indication_value(
        self, value_container: CTIndicationsValueContainer, forced: bool = False
    ) -> bool:
        self.cached_ct_indications_value_container_list.append(value_container)
        if forced or (
            value_container.timestamp.minute
            % self.get_settings_value(
                A.CT_S.CT_INDICATIONS_VALUE_SAVE_PERIOD_IN_MINUTES.name
            )
            == 0
        ):
            return self.execute_insert(
                f"replace into {CT_INDICATIONS_VALUE_TABLE_NAME} ({A.CT_FNC.TIMESTAMP}, {A.CT_FNC.TEMPERATURE}, {A.CT_FNC.HUMIDITY}) value ('{value_container.timestamp}', {value_container.temperature}, {value_container.humidity})"
            )
        return False

    def register_chiller_indication_value(
        self,
        value_container: ChillerIndicationsValueContainer | None,
        forced: bool = False,
    ) -> ChillerIndicationsValueContainer | None:
        if ne(value_container):
            if A.D_C.INDICATIONS.chiller_value_valid(value_container):
                self.cached_chiller_indications_value_container_list.append(
                    value_container
                )
                if forced or (
                    value_container.timestamp.minute
                    % self.get_settings_value(
                        A.CT_S.CHILLER_INDICATIONS_VALUE_SAVE_PERIOD_IN_MINUTES.name
                    )
                    == 0
                ):
                    self.execute_insert(
                        f"replace into {CHILLER_INDICATIONS_VALUE_TABLE_NAME} ({A.CT_FNC.TIMESTAMP}, {A.CT_FNC.TEMPERATURE}, {A.CT_FNC.INDICATORS}) value ('{value_container.timestamp}', {value_container.temperature}, {value_container.indicators})"
                    )
                return value_container
            else:
                return value_container
        return None

    def update_polibase_person_information_quest(
        self,
        value: PolibasePersonInformationQuest,
        search_critery: PolibasePersonInformationQuest,
    ) -> bool:
        result: bool = False

        def action(connection: PooledMySQLConnection) -> bool:
            cursor = connection.cursor()
            set_statement_string: str | None = None
            field_value: Any = None
            field_value_string: str | None = None
            set_statement_part_list: list[str] = []
            for field_name in value.__dataclass_fields__:
                field_value = value.__getattribute__(field_name)
                if nn(field_value):
                    if isinstance(field_value, str):
                        field_value_string = escs(field_value)
                    else:
                        field_value_string = str(field_value)
                    set_statement_part_list.append(
                        f"{field_name} = {field_value_string}"
                    )
            if len(set_statement_part_list) > 0:
                set_statement_string = "set " + A.D.list_to_string(
                    set_statement_part_list, separator=", "
                )
                cursor.execute(
                    f"update {POLIBASE_PERSON_INFORMATION_QUESTS_TABLE_NAME} {set_statement_string} {self.get_condition_string(search_critery)}"
                )
                connection.commit()
                result = cursor.rowcount == 1
            return result

        return self.execute(action, result)

    def execute_query(self, value: str) -> list[dict]:
        result: list[dict] = []

        def action(connection: PooledMySQLConnection) -> list[dict]:
            # connection.autocommit = True
            cursor = connection.cursor(dictionary=True)
            cursor.execute(value)
            try:
                connection.commit()
            except Exception as _:
                pass
            for item in cursor:
                result.append({**item})
            return result

        return self.execute(action, result, catch_exception=True)

    def get_polibase_person_information_quests(
        self, search_critery: PolibasePersonInformationQuest
    ) -> list[PolibasePersonInformationQuest]:
        result: list[PolibasePersonInformationQuest] = []

        def action(
            connection: PooledMySQLConnection,
        ) -> list[PolibasePersonInformationQuest]:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                f"select * from {POLIBASE_PERSON_INFORMATION_QUESTS_TABLE_NAME} {self.get_condition_string(search_critery)}"
            )
            for item in cursor:
                result.append(
                    A.D.fill_data_from_source(
                        PolibasePersonInformationQuest(), {**item}
                    )
                )
            return result

        return self.execute(action, result)

    def get_last_ct_indications_value_container_list(
        self, cached: bool = True, count: int = 1
    ) -> list[CTIndicationsValueContainer]:
        result: list[CTIndicationsValueContainer] = []
        if cached:
            cached_result: list[CTIndicationsValueContainer] | None = (
                self.get_last_cached_indications_value_container_list(
                    self.cached_ct_indications_value_container_list, count
                )
            )
            if ne(cached_result):
                result = cached_result
        if e(result):

            def action(
                connection: PooledMySQLConnection,
            ) -> list[CTIndicationsValueContainer]:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    f"select * from {CT_INDICATIONS_VALUE_TABLE_NAME} ORDER BY {A.CT_FNC.TIMESTAMP} DESC LIMIT {count}"
                )
                for item in cursor:
                    result.append(
                        A.D.fill_data_from_source(
                            CTIndicationsValueContainer(), {**item}
                        )
                    )
                cursor.close()
                return result

            return self.execute(action, result)
        return result

    def get_last_chiller_indications_value_container_list(
        self, cached: bool = True, count: int = 1
    ) -> list[ChillerIndicationsValueContainer]:
        result: list[ChillerIndicationsValueContainer] = []
        if cached:
            cached_result: list[ChillerIndicationsValueContainer] = (
                self.get_last_cached_indications_value_container_list(
                    self.cached_chiller_indications_value_container_list, count
                )
            )
            if ne(cached_result):
                result = cached_result
        if e(result):

            def action(
                connection: PooledMySQLConnection,
            ) -> list[ChillerIndicationsValueContainer]:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    f"select * from {CHILLER_INDICATIONS_VALUE_TABLE_NAME} ORDER BY {A.CT_FNC.TIMESTAMP} DESC LIMIT {count}"
                )
                for item in cursor:
                    result.append(
                        A.D.fill_data_from_source(
                            ChillerIndicationsValueContainer(), {**item}
                        )
                    )
                cursor.close()
                return result

            return self.execute(action, result)
        return result

    def get_last_cached_indications_value_container_list(
        self,
        value_list: list[
            CTIndicationsValueContainer | ChillerIndicationsValueContainer
        ],
        count: int,
    ) -> list[CTIndicationsValueContainer | ChillerIndicationsValueContainer]:
        result_list: list[
            CTIndicationsValueContainer | ChillerIndicationsValueContainer
        ] = []
        for value_container in reversed(value_list):
            if isinstance(value_container, CTIndicationsValueContainer):
                result_list.append(value_container)
            if isinstance(value_container, ChillerIndicationsValueContainer):
                result_list.append(value_container)
            if len(result_list) == count:
                break
        return result_list

    def get_search_polibase_person_visit_notification_query(
        self, search_critery: PolibasePersonVisitNotification | None = None
    ) -> str:
        condition_statement_string: str = self.get_condition_string(search_critery)
        return f"select * from {POLIBASE_PERSON_VISITS_TABLE_NAME} inner join {POLIBASE_PERSON_VISIT_NOTIFICATIONS_TABLE_NAME} on {A.CT_FNC.VISIT_ID} = {A.CT_FNC.ID} {condition_statement_string}"

    def get_search_polibase_person_visit_query(
        self, search_critery: PolibasePersonVisitDS | None = None
    ) -> str:
        condition_statement_string: str = self.get_condition_string(search_critery)
        return f"select * from {POLIBASE_PERSON_VISITS_TABLE_NAME} {condition_statement_string}"

    def search_polibase_person_visit_notifications(
        self, search_critery: PolibasePersonVisitNotification | None = None
    ) -> list[PolibasePersonVisitNotification]:
        result: list[PolibasePersonVisitNotification] = []

        def action(
            connection: PooledMySQLConnection,
        ) -> list[PolibasePersonVisitNotification]:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                self.get_search_polibase_person_visit_notification_query(search_critery)
            )
            for item in cursor:
                result.append(
                    A.D.fill_data_from_source(
                        PolibasePersonVisitNotification(), {**item}
                    )
                )
            return result

        return self.execute(action, result)

    def search_polibase_person_visit(
        self, search_critery: PolibasePersonVisitDS
    ) -> list[PolibasePersonVisitDS]:
        class DH:
            result: list[PolibasePersonVisitNotification] = []

        def action(connection: PooledMySQLConnection) -> list[PolibasePersonVisitDS]:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(self.get_search_polibase_person_visit_query(search_critery))
            for item in cursor:
                DH.result.append(
                    A.D.fill_data_from_source(PolibasePersonVisitDS(), {**item})
                )
            return DH.result

        return self.execute(action, DH.result)

    def get_gkeep_item_list_by_any(
        self, name: str | None, title: str | None, full_equaliment: bool | None
    ) -> list[GKeepItem]:
        search_critery_name: str | None = None
        search_critery_title: str | None = None
        equaliment_value: str = "" if full_equaliment else ANY_SYMBOL
        if ne(name):
            search_critery_name = j(
                (
                    "" if full_equaliment else KEYWORD_COLLECTION.LIKE,
                    j((equaliment_value, name.lower(), equaliment_value)),
                )
            )
        if ne(title):
            search_critery_title = j(
                (
                    KEYWORD_COLLECTION.LIKE,
                    j((ANY_SYMBOL, title.lower(), ANY_SYMBOL)),
                )
            )

        class DH:
            search_critery: GKeepItem | None = (
                None
                if e(search_critery_name) and e(search_critery_title)
                else GKeepItem(search_critery_name, search_critery_title)
            )
            result: list[GKeepItem] = []

        def action(connection: PooledMySQLConnection) -> None:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                js(
                    (
                        "select",
                        "*",
                        "from",
                        GKEEP_MAP_TABLE,
                        (
                            ""
                            if e(DH.search_critery)
                            else self.get_condition_string(DH.search_critery, False)
                        ),
                    )
                )
            )
            for item in cursor:
                DH.result.append(A.D.fill_data_from_source(GKeepItem(), {**item}))

        return self.execute(action, DH.result, False)

    def add_gkeep_item(self, value: GKeepItem) -> bool:
        value.name = value.name.lower()
        return self.execute_insert(self.create_insert_query(GKEEP_MAP_TABLE, value))

    def get_condition_string(
        self, search_critery: Any | None = None, use_and: bool = True
    ) -> str:
        result: str = ""
        if nn(search_critery):
            condition_part_list: list[str] = []
            field_value: Any = None
            field_value_string: str | None = None
            compare_sign: str | None = None
            for field_name in search_critery.__dataclass_fields__:
                field_name: str = field_name
                field_value = search_critery.__getattribute__(field_name)
                if field_name.lower().find("id") != -1:
                    if nn(field_value) and field_value < 0:
                        return f"order by {field_name} desc limit {abs(field_value)}"
                if nn(field_value):
                    if isinstance(field_value, list):
                        field_value_string = A.D.list_to_string(
                            field_value, separator=", ", start="(", end=")"
                        )
                        compare_sign = "in"
                    else:
                        compare_sign = "="
                        field_value_string = str(field_value)
                        if field_name.lower().find(A.CT_FNC.DATE.lower()) != -1:
                            if e(field_value_string):
                                compare_sign = "is"
                                field_value_string = "NULL"
                            else:
                                field_value_string = escs(field_value_string)
                        else:
                            if isinstance(field_value, str):
                                for sign in SIGN_COLLECTION + [KEYWORD_COLLECTION.LIKE]:
                                    if field_value.startswith(sign):
                                        compare_sign = sign
                                        field_value = field_value[len(sign) :]
                                        field_value = field_value.lstrip()
                                        break
                                field_value_string = escs(field_value)
                    condition_part_list.append(
                        js((field_name, compare_sign, field_value_string))
                    )
            if len(condition_part_list) > 0:
                result = js(
                    ("where", j(condition_part_list, " and " if use_and else " or "))
                )
        return result

    def get_delayed_messages(
        self,
        search_critery: MessageSearchCritery | None = None,
        take_to_work: bool = False,
    ) -> list[DelayedMessageDS]:
        def action(connection: PooledMySQLConnection) -> list[DelayedMessageDS]:
            result: list[DelayedMessageDS] = []
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                js(
                    (
                        "select * from",
                        MESSAGE_BUFFER_TABLE_NAME,
                        self.get_condition_string(search_critery),
                    )
                )
            )

            for item in cursor:
                message: DelayedMessageDS = A.D.fill_data_from_source(
                    DelayedMessageDS(), {**item}
                )
                result.append(message)
            if take_to_work:
                status_at_work: int = A.D.get(MessageStatuses.AT_WORK)
                if ne(result):
                    id_list: list[int] = []

                    def every_action(item: DelayedMessageDS) -> None:
                        item.status = status_at_work
                        id_list.append(item.id)

                    A.D.every(every_action, result)
                    condition_statement_string = (
                        f"where {A.CT_FNC.ID} in "
                        + A.D.list_to_string(id_list, start="(", end=")")
                    )
                    cursor.execute(
                        js(
                            (
                                "update",
                                MESSAGE_BUFFER_TABLE_NAME,
                                "set",
                                A.CT_FNC.STATUS,
                                "=",
                                status_at_work,
                                condition_statement_string,
                            )
                        )
                    )
                    connection.commit()
            cursor.close()
            return result

        return self.execute(action, [])

    def update_delayed_message(
        self, value: DelayedMessageDS, search_critery: MessageSearchCritery
    ) -> bool:
        result: bool = False

        def action(connection: PooledMySQLConnection) -> bool:
            cursor = connection.cursor()
            set_statement_string: str | None = None
            field_value: Any = None
            field_value_string: str | None = None
            set_statement_part_list: list[str] = []
            for field_name in value.__dataclass_fields__:
                field_value = value.__getattribute__(field_name)
                if nn(field_value):
                    if isinstance(field_value, str):
                        field_value_string = escs(field_value)
                    else:
                        field_value_string = str(field_value)
                    set_statement_part_list.append(
                        f"{field_name} = {field_value_string}"
                    )
            if len(set_statement_part_list) > 0:
                set_statement_string = "set " + A.D.list_to_string(
                    set_statement_part_list, separator=", "
                )
                cursor.execute(
                    f"update {MESSAGE_BUFFER_TABLE_NAME} {set_statement_string} {self.get_condition_string(search_critery)}"
                )
                connection.commit()
                result = cursor.rowcount == 1
            return result

        return self.execute(action, result)

    def execute_insert(self, query: str) -> bool | None:
        def action(connection: PooledMySQLConnection) -> bool:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            return cursor.rowcount >= 1

        return self.execute(action, None)

    def add_polibase_person_visit(self, value: PolibasePersonVisitDS) -> bool:
        return self.execute_insert(
            f"replace into {POLIBASE_PERSON_VISITS_TABLE_NAME} ({A.CT_FNC.ID}, {A.CT_FNC.PIN}, {A.CT_FNC.FULL_NAME}, {A.CT_FNC.TELEPHONE_NUMBER}, {A.CT_FNC.REGISTRATION_DATE}, {A.CT_FNC.BEGIN_DATE}, {A.CT_FNC.COMPLETE_DATE}, {A.CT_FNC.STATUS}, {A.CT_FNC.DOCTOR_ID}, {A.CT_FNC.DOCTOR_FULL_NAME}, {A.CT_FNC.SERVICE_GROUP_ID}) value ({value.id}, {value.pin}, '{value.FullName}', '{value.telephoneNumber}', '{value.registrationDate}', '{value.beginDate}', '{value.completeDate}', {value.status}, {value.doctorID}, '{value.doctorFullName}', {value.serviceGroupID})"
        )

    def register_polibase_person_visit_notification(
        self, value: PolibasePersonVisitNotificationDS
    ) -> bool:
        return self.execute_insert(
            f"insert into {POLIBASE_PERSON_VISIT_NOTIFICATIONS_TABLE_NAME} ({A.CT_FNC.VISIT_ID}, {A.CT_FNC.MESSAGE_ID}, {A.CT_FNC.TYPE}) value ({value.visitID}, {value.messageID}, {value.type})"
        )

    def update_polibase_person_notification_confirmation(
        self, value: PolibasePersonNotificationConfirmation
    ) -> bool:
        return self.execute_insert(
            f"replace into {POLIBASE_PERSON_NOTIFICATION_CONFIRMATIONS_TABLE_NAME} ({A.CT_FNC.RECIPIENT}, {A.CT_FNC.SENDER}, {A.CT_FNC.STATUS}) value ('{value.recipient}', '{value.sender}', '{value.status}')"
        )

    def search_polibase_person_notification_confirmation(
        self, value: PolibasePersonNotificationConfirmation
    ) -> PolibasePersonNotificationConfirmation:
        result: PolibasePersonNotificationConfirmation | None = None

        def action(
            connection: PooledMySQLConnection,
        ) -> PolibasePersonNotificationConfirmation:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                js(
                    (
                        "select * from",
                        POLIBASE_PERSON_NOTIFICATION_CONFIRMATIONS_TABLE_NAME,
                        "where",
                        A.CT_FNC.RECIPIENT,
                        "=",
                        escs(value.recipient),
                        "and",
                        A.CT_FNC.SENDER,
                        "=",
                        escs(value.sender),
                    )
                )
            )
            result = A.D.fill_data_from_source(
                PolibasePersonNotificationConfirmation(), cursor.fetchone()
            )
            return result

        return self.execute(action, result)

    def register_delayed_message(self, message: DelayedMessage) -> int:
        value_statement_string: str = ""
        fields_statement_string: str = ""
        value_statement_part_list: list[str] = []
        field_part_list: list[str] = []
        for field_name in message.__dataclass_fields__:
            field_value = message.__getattribute__(field_name)
            if nn(field_value):
                if isinstance(field_value, str):
                    field_value_string = A.D_F.as_string(
                        field_value, escaped_string=True
                    )
                else:
                    field_value_string = str(field_value)
                field_part_list.append(field_name)
                value_statement_part_list.append(field_value_string)
        if len(value_statement_part_list) > 0:
            value_statement_string = "value " + A.D.list_to_string(
                value_statement_part_list, start="(", end=")"
            )
            fields_statement_string = A.D.list_to_string(
                field_part_list, start="(", end=")"
            )
        if self.execute_insert(
            f"insert into {MESSAGE_BUFFER_TABLE_NAME} {fields_statement_string} {value_statement_string}"
        ):

            def action(connection: PooledMySQLConnection) -> int:
                cursor = connection.cursor()
                cursor.execute(
                    f"select max({A.CT_FNC.ID}) from {MESSAGE_BUFFER_TABLE_NAME}"
                )
                return cursor.fetchone()[0]

            return self.execute(action, 0)
        return 0
