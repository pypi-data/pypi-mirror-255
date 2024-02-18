import mysql.connector
from logger_local.LoggerLocal import Logger
from logger_local.MetaLogger import MetaLogger
from python_sdk_remote.utilities import get_sql_hostname, get_sql_username, get_sql_password

from .constants import LOGGER_CONNECTOR_CODE_OBJECT
from .cursor import Cursor

logger = Logger.create_logger(object=LOGGER_CONNECTOR_CODE_OBJECT)
connections_pool = {}


# TODO Can we add hostname, IPv4, IPv6, sql statement? Can we have the same message format in all cases?
class Connector(metaclass=MetaLogger, object=LOGGER_CONNECTOR_CODE_OBJECT):
    @staticmethod
    def connect(schema_name: str) -> 'Connector':
        if (schema_name in connections_pool and
                connections_pool[schema_name] and
                connections_pool[schema_name].connection):
            if connections_pool[schema_name].connection.is_connected():

                return connections_pool[schema_name]
            else:
                # reconnect
                connections_pool[schema_name].connection.reconnect()
                # TODO We should develop retry mechanism to support password rotation and small network issues.
                if connections_pool[schema_name].connection.is_connected():

                    return connections_pool[schema_name]
                else:
                    connector = Connector(schema_name)
                    logger.warning("Reconnect failed, returning a new connection",
                                   object={'connections_pool': str(connections_pool[schema_name])})

                    return connector
        else:
            connector = Connector(schema_name)

            return connector

    def __init__(self, schema_name: str,
                 host: str = get_sql_hostname(),
                 user: str = get_sql_username(),
                 password: str = get_sql_password()) -> None:
        self.host = host
        self.schema = schema_name
        self.user = user
        self.password = password

        # Checking host suffix
        # TODO: move to sdk.get_sql_hostname
        if not (self.host.endswith("circ.zone") or self.host.endswith("circlez.ai")):
            logger.warning(
                f"Your RDS_HOSTNAME={self.host} which is not what is expected")
        self.connection: mysql.connector = None
        self._cursor: Cursor | None = None
        self._connect_to_db()
        connections_pool[schema_name] = self

    def reconnect(self) -> None:
        self.connection.reconnect()
        self._cursor = self.cursor()
        self.set_schema(self.schema)

    def _connect_to_db(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.schema
        )
        self._cursor = self.cursor()
        self.set_schema(self.schema)

    def database_info(self):
        return f"host={self.host}, user={self.user}, schema={self.schema}"

    def close(self) -> None:

        try:
            if self._cursor:
                self._cursor.close()
                logger.info("Cursor closed successfully.")
        except Exception as exception:
            logger.error(f"connection.py close() {self.database_info()}", object={"exception": exception})

        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Connection closed successfully.")

    def cursor(self, dictionary=False, buffered=False) -> Cursor:

        cursor_instance = Cursor(self.connection.cursor(
            dictionary=dictionary, buffered=buffered))

        return cursor_instance

    def commit(self) -> None:

        self.connection.commit()

    def set_schema(self, new_schema: str | None) -> None:
        if not new_schema:
            return
        if self.schema == new_schema:
            return
        self.schema = new_schema
        if self.connection and self.connection.is_connected():
            use_query = f"USE `{new_schema}`;"
            self._cursor.execute(use_query)
            logger.info(f"Switched to schema: {new_schema}")
        else:
            raise Exception(
                "Connection is not established. The database will be used on the next connect.")

    def rollback(self):

        self.connection.rollback()

    def start_tranaction(self):

        self.connection.start_transaction()
