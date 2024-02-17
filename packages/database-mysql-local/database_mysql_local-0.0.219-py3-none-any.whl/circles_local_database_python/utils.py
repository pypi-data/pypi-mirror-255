from python_sdk_remote.utilities import get_environment_name
from url_remote.environment_name_enum import EnvironmentName

from .to_sql_interface import ToSQLInterface


def validate_select_table_name(database_object_name: str) -> None:
    if (get_environment_name() not in (EnvironmentName.DVLP1.value, EnvironmentName.PROD1.value)
            and not database_object_name.endswith("_view")):
        raise Exception(
            f"View name must end with '_view' in this environment (got {database_object_name})")


def validate_none_select_table_name(database_object_name: str) -> None:
    if (get_environment_name() not in (EnvironmentName.DVLP1.value, EnvironmentName.PROD1.value)
            and not database_object_name.endswith("_table")):
        raise Exception(
            f"Table name must end with '_table' in this environment  (got {database_object_name})")


def process_insert_data_json(data_json: dict | None) -> tuple[str, str, dict]:
    if not data_json:
        return '', '', {}

    columns = []
    values = []

    for key, value in data_json.items():
        columns.append(f"`{key}`")
        if isinstance(value, ToSQLInterface):
            values.append(value.to_sql())
        else:
            values.append('%s')

    filtered_data_json = {key: value for key, value in data_json.items() if
                          not isinstance(value, ToSQLInterface)}
    return ','.join(columns), ','.join(values), filtered_data_json


# Please add typing and example of input-output as docstring if possible.
def process_update_data_json(data_json: dict | None) -> tuple[str, dict]:
    if not data_json:
        return '', {}

    set_values = []
    for key, value in data_json.items():
        if isinstance(value, ToSQLInterface):
            set_values.append(f"`{key}`={value.to_sql()}")
        else:
            set_values.append(f"`{key}`=%s")

    filtered_data_json = {key: value for key, value in data_json.items() if
                          not isinstance(value, ToSQLInterface)}
    # + "," because we add updated_timestamp in the update query
    return ', '.join(set_values) + ",", filtered_data_json
