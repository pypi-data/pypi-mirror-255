from typing import Any

from ds_core.handlers.abstract_handlers import AbstractSourceHandler, AbstractPersistHandler
from ds_core.handlers.abstract_handlers import ConnectorContract, HandlerFactory
import pyarrow as pa

class PostgresSourceHandler(AbstractSourceHandler):
    """ A Postgres Source Handler"""

    def __init__(self, connector_contract: ConnectorContract):
        """ initialise the Hander passing the source_contract dictionary """
        # required module import
        self.psycopg2 = HandlerFactory.get_module('psycopg2')
        super().__init__(connector_contract)
        connector_type = self.connector_contract.schema
        if connector_type.lower() not in self.supported_types():
            raise ValueError("The source type '{}' is not supported. see supported_types()".format(connector_type))
        self._file_state = 0
        self._changed_flag = True

    def supported_types(self) -> list:
        """ The source types supported with this module"""
        return ['postgresql', 'postgres']

    def exists(self) -> bool:
        return True

    def has_changed(self) -> bool:
        """ returns if the file has been modified"""
        # TODO: Add in change logic here
        state = None
        if state != self._file_state:
            self._changed_flag = True
            self._file_state = state
        return self._changed_flag

    def reset_changed(self, changed: bool = False):
        """ manual reset to say the file has been seen. This is automatically called if the file is loaded"""
        changed = changed if isinstance(changed, bool) else False
        self._changed_flag = changed

    def load_canonical(self, **kwargs) -> dict:
        """ returns the canonical dataset based on the source contract
            The canonical in this instance is a dictionary that has the headers as the key and then
            the ordered list of values for that header
        """
        conn = None
        cur = self.get_cursor()
        _kwargs = {**self.connector_contract.query, **kwargs}
        table = _kwargs.pop('table', 'hadron_table')
        sql_query = _kwargs.pop('sql_query', f"SELECT * FROM {table};")
        try:
            cur.execute(sql_query)
            col_names = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return pa.table([rows], names=[col_names])
        except (Exception, self.psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def get_cursor(self):
        if not isinstance(self.connector_contract, ConnectorContract):
            raise ValueError("The Connector Contract is not valid")
        _kwargs = self.connector_contract.query
        config_name = _kwargs.pop('config_name', None)
        section = _kwargs.pop('config_section', 'postgresql')
        try:
            config = self.connector_contract.parse_ini(config_name=config_name, section=section)
        except ValueError:
            config = {}
        database = config.pop('database', self.connector_contract.path[1:])
        host = config.pop('host', self.connector_contract.hostname)
        port = config.pop('post', self.connector_contract.port)
        user = config.pop('user', self.connector_contract.username)
        password = config.pop('password', self.connector_contract.password)
        try:
            conn = self.psycopg2.connect(database=database, host=host, port=port, user=user, password=password)
            return conn.cursor()
        except (Exception, self.psycopg2.DatabaseError) as error:
            raise ConnectionError(error)


class PostgresPersistHandler(PostgresSourceHandler, AbstractPersistHandler):
    def persist_canonical(self, canonical: pa.Table, **kwargs) -> bool:
        if not isinstance(self.connector_contract, ConnectorContract):
            return False
        return self.backup_canonical(canonical=canonical, uri=self.connector_contract.uri, **kwargs)

    def backup_canonical(self, canonical: Any, uri: str, **kwargs) -> bool:
        conn = None
        cur = self.get_cursor()
        _kwargs = {**self.connector_contract.query, **kwargs}
        table = _kwargs.pop('table', 'hadron_table')
        sql_query = _kwargs.pop('sql_query', f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM canonical;")
        try:
            cur.execute(sql_query)
            return
        except (Exception, self.psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def remove_canonical(self, **kwargs) -> bool:
        pass
