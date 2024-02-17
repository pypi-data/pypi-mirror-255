import os
import pyarrow as pa
import pyarrow.compute as pc
from ds_core.handlers.abstract_handlers import AbstractSourceHandler, AbstractPersistHandler
from ds_core.handlers.abstract_handlers import ConnectorContract, HandlerFactory

class DuckdbSourceHandler(AbstractSourceHandler):
    """ A DuckDB source handler"""

    def __init__(self, connector_contract: ConnectorContract):
        """ initialise the Handler passing the source_contract dictionary """
        # required module import
        self.duckdb = HandlerFactory.get_module('duckdb')
        super().__init__(connector_contract)
        # connection
        self.connection = self.duckdb.connect(':default:')
        # address
        self.address = connector_contract.address
        if self.address.endswith('duckdb:'):
            self.address = ':default:'
        # remote table
        _kwargs = self.connector_contract.query
        table = _kwargs.pop('table', 'hadron_table')
        if table.startswith('s3//'):
            region_name = _kwargs.pop('region_name', os.environ.get('AWS_DEFAULT_REGION'))
            aws_access_key_id = _kwargs.pop('aws_access_key_id', os.environ.get('AWS_ACCESS_KEY_ID'))
            aws_secret_access_key = _kwargs.pop('aws_secret_access_key', os.environ.get('AWS_SECRET_ACCESS_KEY'))
            aws_session_token = _kwargs.pop('aws_session_token', os.environ.get('AWS_SESSION_TOKEN'))
            self.connection.execute(f"""
                INSTALL httpfs;
                LOAD httpfs;
                SET s3_region='{region_name}';
                SET s3_access_key_id='{aws_access_key_id}';
                SET s3_secret_access_key='{aws_secret_access_key}';
                SET s3_session_token='{aws_session_token}';
            """)
        elif table.startswith('http//'):
            self.connection.execute(f"""
                INSTALL httpfs;
                LOAD httpfs;
             """)
        self.first_row = None
        self._changed_flag = True

    def supported_types(self) -> list:
        return ['parquet']

    def exists(self) -> bool:
        _kwargs = self.connector_contract.query
        table = _kwargs.pop('table', 'hadron_table')
        result = self.connection.execute("CALL duckdb_tables()").arrow()
        return pc.is_in(table, result.column('table_name')).as_py()

    def has_changed(self) -> bool:
        _kwargs = self.connector_contract.query
        table = _kwargs.pop('table', 'hadron_table')
        result = self.connection.execute(f"SELECT * FROM {table} LIMIT 1;").arrow()
        if self.first_row.equals(result):
            return False
        return True

    def reset_changed(self, changed: bool=None):
        """ manual reset to say the file has been seen. This is automatically called if the file is loaded"""
        changed = changed if isinstance(changed, bool) else False
        self._changed_flag = changed
        if changed:
            _kwargs = self.connector_contract.query
            table = _kwargs.pop('table', 'hadron_table')
            result = self.connection.execute(f"SELECT * FROM {table} LIMIT 1;").arrow()
            self.first_row = result

    def load_canonical(self, **kwargs) -> pa.Table:
        _kwargs = {**self.connector_contract.query, **kwargs}
        table = _kwargs.pop('table', 'hadron_table')
        if table.startswith("s3://"):
            return self.connection.execute(f"SELECT * FROM read_parquet('{table}')").arrow()
        elif table.startswith('https://'):
            return self.connection.execute(f"SELECT * FROM read_parquet('{table}')").arrow()
        query = _kwargs.pop('sql_query', f"SELECT * FROM {table};")
        query = query.replace('@', table)
        return self.connection.execute(query).arrow()


class DuckdbPersistHandler(DuckdbSourceHandler, AbstractPersistHandler):

    def persist_canonical(self, canonical: pa.Table, **kwargs) -> bool:
        """ persists the canonical dataset
        """
        if not isinstance(self.connector_contract, ConnectorContract):
            return False
        _kwargs = {**self.connector_contract.query, **kwargs}
        table = _kwargs.pop('table', 'hadron_table')
        if table.startswith("s3://"):
            self.connection.execute(f"COPY tbl TO '{table}'")
            return
        elif table.startswith('http//'):
            raise NotImplementedError("Not supported. 'https' is currently read only")
        query = _kwargs.pop('sql_query', f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM canonical;")
        self.connection.execute(query)
        # reset has changed
        self.reset_changed(True)
        return

    def remove_canonical(self, **kwargs) -> bool:
        _kwargs = {**self.connector_contract.query, **kwargs}
        table = _kwargs.pop('table', 'hadron_table')
        self.connection.execute(f"DROP TABLE IF EXISTS {table}")
        return True

    def backup_canonical(self, canonical: pa.Table, uri: str, **kwargs) -> bool:
        pass

