import os
import re
from typing import Any

import mysql.connector
from database_infrastructure_local.number_generator import NumberGenerator
from logger_local.MetaLogger import MetaLogger

from .connector import Connector
from .constants import DEFAULT_SQL_SELECT_LIMIT, LOGGER_CRUD_CODE_OBJECT
from .table_definition import table_definition
from .utils import (process_insert_data_json, process_update_data_json,
                    validate_none_select_table_name,
                    validate_select_table_name)


class GenericCRUD(metaclass=MetaLogger, object=LOGGER_CRUD_CODE_OBJECT):
    """A class that provides generic CRUD functionality.
    There are 4 main functions to create, read, update and delete data from the database.
    The rest of the functions are helper functions or wrappers around the main functions."""

    def __init__(self, *, default_schema_name: str,
                 default_table_name: str = None,
                 default_view_table_name: str = None,
                 default_id_column_name: str = None,
                 is_test_data: bool = None) -> None:
        """Initializes the GenericCRUD class. If a connection is not provided, a new connection will be created."""
        self.schema_name = default_schema_name
        self.connection = Connector.connect(schema_name=default_schema_name)
        self.cursor = self.connection.cursor()
        self.default_column = default_id_column_name
        self.default_table_name = default_table_name
        self.default_view_table_name = default_view_table_name or self._get_view_name(default_table_name)
        self.is_test_data = is_test_data

    def insert(self, *, schema_name: str = None, table_name: str = None, data_json: dict = None,
               ignore_duplicate: bool = False) -> int:
        """Inserts a new row into the table and returns the id of the new row or -1 if an error occurred."""

        if ignore_duplicate:
            self.logger.warning("GenericCRUD.insert using ignore_duplicate, is it really needed?")
        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.schema_name
        self._validate_args(args=locals())

        if table_name in table_definition:
            if table_definition[table_name]["is_number_column"]:
                view_name = self._get_view_name(table_name)
                number = NumberGenerator.get_random_number(schema_name=schema_name, view_name=view_name)
                data_json["number"] = number
        else:
            self.logger.warning(f"database-mysql-local-python generic_crud.py Table {table_name} not found in "
                                f"database-mysql-local.table_definition_table data structure, we might need to run sql2code")
        # TODO: later we may want to add a check for the table_definition to see if the table is a test table
        if self.is_test_data is not None:
            if self._is_test_data():
                data_json["is_test_data"] = 1
            else:
                data_json["is_test_data"] = 0

        columns, values, data_json = process_insert_data_json(data_json=data_json)
        # We removed the IGNORE from the SQL Statement as we want to return the id of the existing row
        insert_query = "INSERT " + \
                       f"INTO `{schema_name}`.`{table_name}` ({columns}) " \
                       f"VALUES ({values});"
        try:
            self.cursor.execute(insert_query, tuple(data_json.values()))
            self.connection.commit()
            inserted_id = self.cursor.lastrowid()
        except mysql.connector.errors.IntegrityError as exception:
            if ignore_duplicate:
                self.logger.warning("GenericCRUD.insert: existing record found, selecting it's id")
                inserted_id = self._get_existing_duplicate_id(table_name, exception)
            else:
                raise exception

        return inserted_id

    # TODO: test
    def insert_or_update(self, *, schema_name: str = None, table_name: str = None, data_json: dict = None) -> int:
        """Inserts a new row into the table, or updates an existing row if it already exists, and returns the id of the new row or -1 if an error occurred."""

        schema_name = schema_name or self.schema_name
        table_name = table_name or self.default_table_name
        self._validate_args(args=locals())
        columns, values, data_json = process_insert_data_json(data_json=data_json)
        set_values, data_json = process_update_data_json(data_json)
        insert_query = "INSERT " + \
                       f"INTO `{schema_name}`.`{table_name}` ({columns}) " \
                       f"VALUES ({values}) " \
                       f"ON DUPLICATE KEY UPDATE {set_values} updated_timestamp=CURRENT_TIMESTAMP();"
        self.cursor.execute(insert_query, tuple(data_json.values()) * 2)
        self.connection.commit()
        inserted_id = self.cursor.lastrowid()

        return inserted_id

    def _get_existing_duplicate_id(self, table_name: str, error: Exception) -> int:
        pattern = r'Duplicate entry \'(.+?)\' for key \'(.+?)\''
        match = re.search(pattern, str(error))
        if not match:  # a different error
            raise error
        duplicate_value = match.group(1)
        query = """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = %s AND CONSTRAINT_NAME = "PRIMARY";
        """
        self.cursor.execute(query, (table_name,))
        column_name = self.cursor.fetchone()[0]
        if column_name:
            select_query = f"SELECT {column_name} FROM `{table_name}` WHERE {column_name} = %s LIMIT 1;"
            self.cursor.execute(select_query, (duplicate_value,))
            return self.cursor.fetchone()[0]
        else:  # Column name for constraint not found
            raise error

    def update_by_id(self, *, schema_name: str = None, table_name: str = None, id_column_name: str = None,
                     id_column_value: Any = None, data_json: dict = None,
                     limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> None:
        """Updates data in the table by ID."""

        table_name = table_name or self.default_table_name
        id_column_name = id_column_name or self.default_column

        if id_column_name:
            if id_column_value is None:
                where = f"`{id_column_name}` IS NULL"
                extra_sql_params = None
            else:
                where = f"`{id_column_name}`=%s"
                extra_sql_params = (id_column_value,)
            self.update_by_where(schema_name=schema_name, table_name=table_name, where=where,
                                 data_json=data_json, params=extra_sql_params,
                                 limit=limit, order_by=order_by)
        else:
            raise Exception("Update by id requires an id_column_name")

    def update_by_where(self, *, schema_name: str = None, table_name: str = None, where: str = None,
                        params: tuple = None, data_json: dict = None,
                        limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> None:
        """Updates data in the table by WHERE.
        Example:
        "UPDATE table_name SET A=A_val, B=B_val WHERE C=C_val AND D=D_val"
        translates into:
        update_by_where(table_name="table_name",
                        data_json={"A": A_val, "B": B_val},
                        where="C=%s AND D=%s",
                        params=(C_val, D_val)"""

        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.schema_name
        self._validate_args(args=locals())

        set_values, data_json = process_update_data_json(data_json)
        if not where:
            raise Exception("update_by_where requires a 'where'")

        update_query = f"UPDATE `{schema_name}`.`{table_name}` " \
                       f"SET {set_values} updated_timestamp=CURRENT_TIMESTAMP() " \
                       f"WHERE {where} " + \
                       (f"ORDER BY {order_by} " if order_by else "") + \
                       f"LIMIT {limit};"
        params = params or tuple()
        self.cursor.execute(update_query, tuple(
            data_json.values()) + params)
        self.connection.commit()

    def delete_by_id(self, *, schema_name: str = None, table_name: str = None, id_column_name: str = None,
                     id_column_value: Any = None) -> None:
        """Deletes data from the table by id"""
        # logger, checks etc. are done inside delete_by_where
        id_column_name = id_column_name or self.default_column
        if id_column_name:  # id_column_value can be empty
            if id_column_value is None:
                where = f"`{id_column_name}` IS NULL"
                params = None
            else:
                where = f"`{id_column_name}`=%s"
                params = (id_column_value,)
            self.delete_by_where(schema_name=schema_name, table_name=table_name, where=where, params=params)
        else:
            raise Exception("Delete by id requires an id_column_name and id_column_value.")

    def delete_by_where(self, *, schema_name: str = None, table_name: str = None, where: str = None,
                        params: tuple = None) -> None:
        """Deletes data from the table by WHERE."""

        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.schema_name
        self._validate_args(args=locals())
        if not where:
            raise Exception("delete_by_where requires a 'where'")

        update_query = f"UPDATE `{schema_name}`.`{table_name}` " \
                       f"SET end_timestamp=CURRENT_TIMESTAMP() " \
                       f"WHERE {where};"
        self.cursor.execute(update_query, params)
        self.connection.commit()

    # TODO: test distinct
    def select_one_tuple_by_id(self, *, schema_name: str = None, view_table_name: str = None,
                               select_clause_value: str = "*",
                               id_column_name: str = None,
                               id_column_value: Any = None,
                               distinct: bool = False, order_by: str = "") -> tuple:
        """Selects one row from the table by ID and returns it as a tuple."""
        result = self.select_multi_tuple_by_id(schema_name=schema_name,
                                               view_table_name=view_table_name,
                                               select_clause_value=select_clause_value,
                                               id_column_name=id_column_name,
                                               id_column_value=id_column_value,
                                               distinct=distinct,
                                               limit=1,
                                               order_by=order_by)
        if result:
            return result[0]
        else:
            return tuple()

    def select_one_dict_by_id(self, *, schema_name: str = None, view_table_name: str = None,
                              select_clause_value: str = "*",
                              id_column_name: str = None,
                              id_column_value: Any = None,
                              distinct: bool = False, order_by: str = "") -> dict:
        """Selects one row from the table by ID and returns it as a dictionary (column_name: value)"""
        result = self.select_one_tuple_by_id(schema_name=schema_name,
                                             view_table_name=view_table_name,
                                             select_clause_value=select_clause_value,
                                             id_column_name=id_column_name,
                                             id_column_value=id_column_value,
                                             distinct=distinct,
                                             order_by=order_by)
        return self.convert_to_dict(result, select_clause_value)

    def select_one_tuple_by_where(self, *, schema_name: str = None, view_table_name: str = None,
                                  select_clause_value: str = "*",
                                  where: str = None, params: tuple = None,
                                  distinct: bool = False, order_by: str = "") -> tuple:
        """Selects one row from the table based on a WHERE clause and returns it as a tuple."""
        result = self.select_multi_tuple_by_where(schema_name=schema_name,
                                                  view_table_name=view_table_name,
                                                  select_clause_value=select_clause_value,
                                                  where=where,
                                                  params=params,
                                                  distinct=distinct,
                                                  limit=1,
                                                  order_by=order_by)
        if result:
            return result[0]
        else:
            return tuple()

    def select_one_dict_by_where(self, *, schema_name: str = None, view_table_name: str = None,
                                 select_clause_value: str = "*",
                                 where: str = None, params: tuple = None,
                                 distinct: bool = False, order_by: str = "") -> dict:
        """Selects one row from the table based on a WHERE clause and returns it as a dictionary."""
        result = self.select_one_tuple_by_where(schema_name=schema_name,
                                                view_table_name=view_table_name,
                                                select_clause_value=select_clause_value,
                                                where=where,
                                                params=params,
                                                distinct=distinct,
                                                order_by=order_by)
        return self.convert_to_dict(result, select_clause_value)

    def select_multi_tuple_by_id(self, *, schema_name: str = None, view_table_name: str = None,
                                 select_clause_value: str = "*",
                                 id_column_name: str = None,
                                 id_column_value: Any = None,
                                 distinct: bool = False,
                                 limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> list:
        """Selects multiple rows from the table by ID and returns them as a
        list of tuples.
        send `id_column_name=''` if you want to select all rows and ignore default column"""
        id_column_name = id_column_name or self.default_column

        if not id_column_name:
            where = None
            params = None
        else:
            if id_column_value is None:
                where = f"{id_column_name} IS NULL"
                params = None
            else:
                where = f"{id_column_name}=%s"
                params = (id_column_value,)
        return self.select_multi_tuple_by_where(schema_name=schema_name,
                                                view_table_name=view_table_name,
                                                select_clause_value=select_clause_value,
                                                where=where,
                                                params=params,
                                                distinct=distinct,
                                                limit=limit,
                                                order_by=order_by)

    def select_multi_dict_by_id(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = "*",
            id_column_name: str = None, id_column_value: Any = None, distinct: bool = False,
            limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> list:
        """Selects multiple rows from the table by ID and returns them as a list of dictionaries."""
        result = self.select_multi_tuple_by_id(schema_name=schema_name,
                                               view_table_name=view_table_name,
                                               select_clause_value=select_clause_value,
                                               id_column_name=id_column_name,
                                               id_column_value=id_column_value,
                                               distinct=distinct,
                                               limit=limit,
                                               order_by=order_by)
        return [self.convert_to_dict(row, select_clause_value) for row in result]

    # Old name: select_multi_by_where
    def select_multi_tuple_by_where(self, *, schema_name: str = None, view_table_name: str = None,
                                    select_clause_value: str = "*",
                                    where: str = None, params: tuple = None, distinct: bool = False,
                                    limit: int = DEFAULT_SQL_SELECT_LIMIT,
                                    order_by: str = "") -> list:
        """Selects multiple rows from the table based on a WHERE clause and returns them as a list of tuples."""

        schema_name = schema_name or self.schema_name
        view_table_name = view_table_name or self.default_view_table_name
        self._validate_args(args=locals())

        # TODO: add ` to column names if they are not reserved words (like COUNT, ST_X(point), etc.)
        # select_clause_value = ",".join([f"`{x.strip()}`" for x in select_clause_value.split(",") if x != "*"])

        select_query = f"SELECT {'DISTINCT' if distinct else ''} {select_clause_value} " \
                       f"FROM `{schema_name}`.`{view_table_name}` " + \
                       (f"WHERE {where} " if where else "") + \
                       (f"ORDER BY {order_by} " if order_by else "") + \
                       f"LIMIT {limit};"
        self.cursor.execute(select_query, params)
        result = self.cursor.fetchall()

        return result

    def select_multi_dict_by_where(
            self, *, schema_name: str = None, view_table_name: str, select_clause_value: str = "*",
            where: str = None, params: tuple = None, distinct: bool = False,
            limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> list:
        """Selects multiple rows from the table based on a WHERE clause and returns them as a list of dictionaries."""
        result = self.select_multi_tuple_by_where(schema_name=schema_name,
                                                  view_table_name=view_table_name,
                                                  select_clause_value=select_clause_value,
                                                  where=where,
                                                  params=params,
                                                  distinct=distinct,
                                                  limit=limit,
                                                  order_by=order_by)
        return [self.convert_to_dict(row, select_clause_value) for row in result]

    # helper functions:
    def convert_to_dict(self, row: tuple, select_clause_value: str = "*") -> dict:
        """Returns a dictionary of the column names and their values."""
        if select_clause_value == "*":
            column_names = [col[0] for col in self.cursor.description()]
        else:
            column_names = [x.strip() for x in select_clause_value.split(",")]
        return dict(zip(column_names, row or tuple()))

    def _validate_args(self, args: dict) -> None:
        # args = locals() of the calling function
        required_args = ("data_json", "table_name", "view_table_name", "schema_name", "select_clause_value")
        for arg_name, arg_value in args.items():
            message = ""
            if arg_name in ("self", "__class__"):
                continue
            elif arg_name in required_args and not arg_value:
                message = f"Invalid value for {arg_name}: {arg_value}"
            elif arg_name == "table_name":
                validate_none_select_table_name(arg_value)
            elif arg_name == "view_table_name":
                validate_select_table_name(arg_value)

            # data_json values are allowed to contain ';', as we use them with %s (TODO: unless it's ToSQLInterface)
            if (arg_name == "data_json" and any(";" in str(x) for x in arg_value.keys()) or  # check columns
                    arg_name != "data_json" and ";" in str(arg_value)):
                message = f"Invalid value for {arg_name}: {arg_value} (contains ';')"

            if message:
                raise Exception(message)

    def _is_test_data(self) -> bool:
        file_name = os.path.basename(__file__)

        if file_name.startswith('test_') or file_name.endswith('_test.py'):
            return True
        else:
            return False

    def set_schema(self, schema_name: str | None):
        """Sets the given schema to be the default schema."""
        if not schema_name:
            return

        if self.schema_name != schema_name:
            self.connection.set_schema(schema_name)
            self.schema_name = schema_name

    def close(self) -> None:
        """Closes the connection to the database."""

        self.connection.close()

    def _log_error_message(self, message: str, sql_statement: str, schema_name: str) -> str:
        return (f"{message} - SQL statement: {sql_statement}. "
                f"(user={self.connection.user}, host={self.connection.host}, schema={schema_name})")

    @staticmethod
    def _get_view_name(table_name: str | None) -> str | None:
        if table_name:
            return re.sub(r'(_table)$', '_view', table_name)

    def get_test_entity_id(self, *, entity_name: str, insert_function: callable, insert_kwargs: dict = None,
                           entity_creator: callable = None, create_kwargs: dict = None,
                           schema_name: str = None, view_name: str = None) -> int:
        """
        1. Check if there's an entity with is `is_test_data=True`.
        2. If there is, return its id.
        3. If not, create a new entity with `is_test_data=True` and return its id.
        (assuming entity_creator expects `is_test_data` as parameters,
            and returns the expected argument for insert_function)

        Example: get_test_entity_id(entity_name='person', entity_creator=Person, insert_function=PersonsLocal.insert)
        """
        view_name = view_name or self.default_view_table_name
        select_clause_value = entity_name + "_id"
        fetched_result = self.select_one_dict_by_id(schema_name=schema_name or self.schema_name,
                                                    view_table_name=view_name,
                                                    id_column_name='is_test_data',
                                                    id_column_value='1',
                                                    select_clause_value=select_clause_value)
        if fetched_result:
            test_entity_id = fetched_result[select_clause_value]
        else:
            insert_kwargs = insert_kwargs or {}
            create_kwargs = create_kwargs or {}
            if entity_creator:
                entity_result = entity_creator(is_test_data=True, **create_kwargs)
                test_entity_id = insert_function(entity_result, **insert_kwargs)
            else:
                test_entity_id = insert_function(is_test_data=True, **insert_kwargs)
        return test_entity_id
