import re
from typing import Any

from language_remote.lang_code import LangCode
from logger_local.MetaLogger import MetaLogger
from user_context_remote.user_context import UserContext

from .constants import DEFAULT_SQL_SELECT_LIMIT, LOGGER_CRUD_ML_CODE_OBJECT
from .generic_crud import GenericCRUD
from .utils import validate_select_table_name

TEST_TABLE_NAME = 'test_mysql_table'
TEST_ML_TABLE_NAME = 'test_mysql_ml_table'


class GenericCRUDML(GenericCRUD, metaclass=MetaLogger, object=LOGGER_CRUD_ML_CODE_OBJECT):
    """A class that provides generic CRUD functionality for tables with multi-language support."""

    def __init__(self, default_schema_name: str, default_table_name: str = None,
                 default_id_column_name: str = None,
                 is_test_data: bool = False) -> None:
        """Initializes the GenericCRUDML class. If connection is not provided,
        a new connection will be created."""
        if default_table_name is not None:
            self.default_ml_table_name = self._create_ml_table_name(default_table_name)
            self.default_view_table_name = self._get_ml_view_name(default_table_name)
        else:
            self.default_ml_table_name = None
            self.default_view_table_name = None
        #     self.default_ml_table_name = default_ml_table_name or re.sub(r'(_table)$', '_ml\\1', default_table_name)
        self.logger.info("GenericCRUDML.__init__", object={"default_ml_table_name": self.default_ml_table_name,
                                                           "default_view_table_name": self.default_view_table_name})
        super().__init__(default_schema_name=default_schema_name,
                         default_table_name=default_table_name,
                         default_view_table_name=self.default_view_table_name,
                         default_id_column_name=default_id_column_name,
                         is_test_data=is_test_data)
        self.user_context = UserContext()

    def sql_in_list_by_entity_list_id(self, schema_name: str, entity_name: str, entity_list_id: int) -> str:
        """Example: select group_id from group.group_list_member_table WHERE group_list_id=1"""

        old_schema_name = self.schema_name
        self.set_schema(schema_name=schema_name)
        ids = self.select_multi_dict_by_id(view_table_name=f"{entity_name}_list_member_view",
                                           select_clause_value=f"{entity_name}_id",
                                           id_column_name=f"{entity_name}_list_id",
                                           id_column_value=entity_list_id)
        if ids:
            result = f" IN ({','.join([str(_id[f'{entity_name}_id']) for _id in ids])})"
        else:
            result = " = TRUE"
        self.set_schema(schema_name=old_schema_name)

        return result

    def add_value(self, table_id: int = None, lang_code: LangCode = None,
                  is_main: int = 0, data_json: dict = None, data_ml_json: dict = None,
                  table_name: str = None, ml_table_name: str = None) -> tuple[int, int | None] | None:

        lang_code_str = self._get_lang_code_str(lang_code)
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name

        # if this is the first insert of this data, is_main should be 1
        if table_id is None:
            is_main = 1
        elif is_main == 1:
            self._update_old_main_value_to_zero(table_id, table_name)

        # id is the id value of the row in the table_name table
        table_id = table_id or self.insert(data_json=data_json, ignore_duplicate=True)
        if table_id is None:  # TODO: delete
            self.logger.error("Error inserting data_json", object={"data_json": str(data_json)})

            return None

        if data_ml_json is None or data_ml_json == {}:
            return table_id, None

        id_column_name = re.sub(r'(_table)$', '_id', table_name)
        data_ml_json[id_column_name] = table_id
        data_ml_json["lang_code"] = lang_code_str
        data_ml_json["is_main"] = is_main

        # ml_id is the id value of the row in the ml_table_name table
        ml_table_id = self.insert(data_json=data_ml_json, table_name=ml_table_name, ignore_duplicate=True)

        return table_id, ml_table_id

    def get_values_tuple(self, table_id: int, lang_code: LangCode = None,
                         id_column_name: str = None, select_clause_value: str = "*") -> tuple:

        lang_code_str = self._get_lang_code_str(lang_code)
        id_column_name = self._generate_id_column_name(id_column_name, self.default_table_name)
        result = self.select_one_tuple_by_where(where=f"{id_column_name}=%s AND lang_code=%s",
                                                params=(table_id, lang_code_str),
                                                select_clause_value=select_clause_value,
                                                order_by=f"{id_column_name} DESC")

        return result

    def get_values_dict(self, table_id: int, lang_code: LangCode = None,
                        id_column_name: str = None) -> dict:

        lang_code_str = self._get_lang_code_str(lang_code)
        id_column_name = self._generate_id_column_name(id_column_name, self.default_table_name)
        result = self.select_one_dict_by_where(where=f"{id_column_name}=%s AND lang_code=%s",
                                               params=(table_id, lang_code_str),
                                               order_by=f"{id_column_name} DESC")

        return result

    def get_main_values_tuple(self, table_id: int, id_column_name: str = None, select_clause_value: str = "*") -> tuple:

        id_column_name = self._generate_id_column_name(id_column_name, self.default_table_name)
        result = self.select_one_tuple_by_where(where=f"{id_column_name}=%s AND is_main=1",
                                                params=(table_id,),
                                                select_clause_value=select_clause_value,
                                                order_by=f"{id_column_name} DESC")

        return result

    def get_main_values_dict(self, table_id: int, id_column_name: str = None, select_clause_value: str = "*") -> dict:

        id_column_name = self._generate_id_column_name(id_column_name, self.default_table_name)
        result = self.select_one_dict_by_where(where=f"{id_column_name}=%s AND is_main=1",
                                               params=(table_id,),
                                               select_clause_value=select_clause_value,
                                               order_by=f"{id_column_name} DESC")

        return result

    def get_id_by_name(self, name: str, lang_code: LangCode = None,
                       id_column_name: str = None, order_by: str = None) -> int | None:

        lang_code_str = self._get_lang_code_str(lang_code)
        id_column_name = self._generate_id_column_name(id_column_name, self.default_table_name)
        if not order_by:
            order_by = f"{id_column_name} DESC"
        try:
            # TODO: check if the table has a `title` column or a `name` column
            result = self.select_one_tuple_by_where(select_clause_value=id_column_name,
                                                    where="title=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)
        except Exception as exception:
            self.logger.warning("select_one_tuple_by_where was not successful for name and lang_code. "
                                "Error: " + str(exception), object={"title": name, "lang_code": lang_code})
            # this call is not tested because test_mysql_ml_table does not have a `name` column
            result = self.select_one_tuple_by_where(select_clause_value=id_column_name,
                                                    where="`name`=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)

        if result:
            return result[0]
        else:
            return None

    def get_ml_id_by_name(self, name: str, lang_code: LangCode = None,
                          id_column_name: str = None, order_by: str = None) -> int:

        lang_code_str = self._get_lang_code_str(lang_code)
        ml_id_column_name = self._generate_id_column_name(id_column_name, self.default_ml_table_name)
        if not order_by:
            order_by = f"{ml_id_column_name} DESC"
        result = None
        try:
            result = self.select_one_tuple_by_where(select_clause_value=ml_id_column_name,
                                                    where="title=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)
        except Exception as exception:
            self.logger.warning("select_one_tuple_by_where was not successful for name and lang_code. "
                                "Error: " + str(exception), object={"title": name, "lang_code": lang_code})
            # this call is not tested because test_mysql_ml_view does not have a `name` column
            result = self.select_one_tuple_by_where(select_clause_value=ml_id_column_name,
                                                    where="`name`=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)

        return result[0]

    def delete_by_name(self, name: str,
                       lang_code: LangCode = None) -> None:

        lang_code_str = self._get_lang_code_str(lang_code)
        try:
            self.delete_by_where(table_name=TEST_ML_TABLE_NAME, where="title=%s AND lang_code=%s",
                                 params=(name, lang_code_str))
        except Exception as exception:
            self.logger.warning("delete_by_where was not successful for name and lang_code Error: " + str(exception),
                                object={"title": name, "lang_code": lang_code})
            # this call is not tested because test_mysql_ml_table does not have a `name` column
            self.delete_by_where(table_name=TEST_ML_TABLE_NAME,
                                 where="`name`=%s AND lang_code=%s", params=(name, lang_code_str))

    @staticmethod
    def _create_ml_table_name(table_name: str) -> str:
        ml_table_name = re.sub(r'(_table)$', '_ml_table', table_name)
        return ml_table_name

    @staticmethod
    def _get_ml_view_name(table_name: str) -> str:
        view_name = re.sub(r'(_table)$', '_ml_view', table_name)
        return view_name

    def _generate_id_column_name(self, id_column_name: str | None, table_name: str) -> str:
        return id_column_name or re.sub(r'(_table)$', '_id', table_name)

    # Change the old row with is_main=1 to is_main=0
    def _update_old_main_value_to_zero(self, table_id: int, table_name: str) -> None:

        data_ml_json = {"is_main": 0}
        id_column_name = self._generate_id_column_name(None, table_name)
        self.update_by_where(table_name=self.default_ml_table_name,
                             data_json=data_ml_json,
                             where=f"{id_column_name}=%s AND is_main=1",
                             params=(table_id,))

    def _get_lang_code_str(self, lang_code: LangCode) -> str:
        if lang_code is None:
            lang_code_str = self.user_context.get_effective_profile_preferred_lang_code().value
        else:
            lang_code_str = lang_code.value
        return lang_code_str

    # The follwing methods may be irrelevant since GenericCRUD has equivalent methods
    # TODO: We may want to remove these following methods

    # This method returns the value in a selected column by a condition, the condition can be none or a value
    # for a specific column
    def select_one_by_value_with_none_option(
            self, condition_column_name, condition_column_value,
            view_table_name: str = None,
            select_column_name: str = None) -> Any:
        view_table_name = view_table_name or self.default_view_table_name
        # Returns the row id if select_column_name is None
        select_column_name = select_column_name or self.default_column
        """Selects a column from the table based on a WHERE clause and returns it as a list of dictionaries."""

        self.logger.warning("this method is deprecated, use select_one_tuple_by_id instead")
        validate_select_table_name(view_table_name)
        select_query = f"SELECT {select_column_name} " f"FROM {self.schema_name}.{view_table_name} " + (
            f"WHERE `{condition_column_name}` = \"{condition_column_value}\" " if (condition_column_name and
                                                                                   condition_column_value)
            else f"WHERE `{condition_column_name}` IS NULL ")

        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        # Extract the first element from the first tuple in the result
        result = result[0][0] if result else None

        return result

    def select_multi_tuple_by_value_with_none_option(self,
                                                     condition_column_name,
                                                     condition_column_value,
                                                     view_table_name: str = None, select_clause_value: str = "*",

                                                     limit: int = DEFAULT_SQL_SELECT_LIMIT,
                                                     order_by: str = "") -> list:
        view_table_name = view_table_name or self.default_view_table_name
        # Returns the row id if select_column_name is None
        select_column_name = f"`{select_clause_value}`" if select_clause_value != "*" else "*"
        """Selects a column from the table based on a WHERE clause and returns it as a list of dictionaries."""

        self.logger.warning("this method is deprecated, use select_multi_tuple_by_id instead")
        validate_select_table_name(view_table_name)
        select_query = f"SELECT {select_column_name} " f"FROM {self.schema_name}.{view_table_name} " + (
            f"WHERE `{condition_column_name}` = \"{condition_column_value}\" " if (condition_column_name and
                                                                                   condition_column_value)
            else f"WHERE {condition_column_name} IS NULL ") + (
                           f"ORDER BY {order_by} " if order_by else "") + f"LIMIT {limit}"
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        return result

    def select_multi_dict_by_value_with_none_option(self,
                                                    condition_column_name,
                                                    condition_column_value,
                                                    view_table_name: str = None, select_clause_value: str = "*",

                                                    limit: int = DEFAULT_SQL_SELECT_LIMIT,
                                                    order_by: str = "") -> list:
        self.logger.warning("this method is deprecated, use select_multi_tuple_by_id instead")
        """Selects a column from the table based on a WHERE clause and returns it as a list of dictionaries."""
        result = self.select_multi_tuple_by_value_with_none_option(condition_column_name, condition_column_value,

                                                                   view_table_name=view_table_name,
                                                                   select_clause_value=select_clause_value,
                                                                   limit=limit, order_by=order_by)
        return [self.convert_to_dict(row, select_clause_value) for row in result]
