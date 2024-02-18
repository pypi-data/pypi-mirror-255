import io
import os
import threading
from typing import Optional
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq
from .cortex_helpers import load_token, load_api_endpoint
from ds_core.handlers.abstract_handlers import AbstractSourceHandler, ConnectorContract, AbstractPersistHandler, HandlerFactory


class McSourceHandler(AbstractSourceHandler):
    """ A Managed Content Source handler"""

    def __init__(self, connector_contract: ConnectorContract):
        """ Initialise the handler passing the source_contract dictionary """
        super().__init__(connector_contract)
        self.cortex = HandlerFactory.get_module('cortex')
        self.token = self._load_token()
        self.api_endpoint = self._load_api_endpoint()
        self.project = self._load_project_name()
        self.cortex_client = self.cortex.Cortex.client(project=self.project)
        # _ = self.cortex_client.content.exists
        self._etag = 0
        self._changed_flag = True

    def mc_key(self, connector_contract: Optional[ConnectorContract]=None):
        _cc = connector_contract if connector_contract is not None else self.connector_contract
        schema, bucket, path = _cc.parse_address_elements(_cc.uri)
        if not path:
            return bucket
        return os.path.join(bucket, path.strip('/'))

    def _load_token(self):
        return load_token(token=self.connector_contract.kwargs.get("token", os.environ["TOKEN"]))

    def _load_api_endpoint(self):
        return load_api_endpoint(endpoint=self.connector_contract.kwargs.get("api_endpoint", os.environ["API_ENDPOINT"]))
    
    def _load_project_name(self):
        return self.connector_contract.kwargs.get("project", os.environ["PROJECT"])

    def supported_types(self) -> list:
        """ The source types supported with this module"""
        return ["csv", "parquet"]

    def _download_key_from_mc(self, key):
        return self.cortex_client.content.download(key, retries=2)

    def _load_df_from_csv_in_mc(self, mc_key: str, **options) -> pa.Table:
        content = self._download_key_from_mc(mc_key).read()
        return csv.read_csv(io.BytesIO(content), **options)

    def _load_df_from_parquet_in_mc(self, mc_key: str, **options) -> pa.Table:
        content = self._download_key_from_mc(mc_key).read()
        return pq.read_table(io.BytesIO(content), **options)

    def load_canonical(self) -> pa.Table:
        """ returns the canonical dataset based on the connector contract. This method utilises the pandas
        'pd.read_' methods and directly passes the kwargs to these methods.
        Extra Parameters in the ConnectorContract kwargs:
            - file_type: (optional) the type of the source file. if not set, inferred from the file extension
        """
        if not isinstance(self.connector_contract, ConnectorContract):
            raise ValueError("The Managed Content Connector Contract has not been set")
        _cc = self.connector_contract
        if not isinstance(_cc, ConnectorContract):
            raise ValueError("The Python Source Connector Contract has not been set correctly")
        load_params = _cc.kwargs
        load_params.update(_cc.query)  # Update kwargs with those in the uri query
        load_params.pop('token', None)
        load_params.pop('api_endpoint', None)
        load_params.pop('project', None)
        _, _, _ext = _cc.address.rpartition('.')
        file_type = load_params.get('file_type', _ext if len(_ext) > 0 else 'csv')
        if file_type.lower() not in self.supported_types():
            raise ValueError("The file type {} is not recognised. "
                             "Set file_type parameter to a recognised source type".format(file_type))

        # session
        if _cc.schema not in ['mc']:
            raise ValueError("The Connector Contract Schema has not been set correctly.")
        with threading.Lock():
            if file_type.lower() in ['csv', 'gz']:
                rtn_data = self._load_df_from_csv_in_mc(mc_key=self.mc_key(), **load_params)
            elif file_type.lower() in ['parquet']:
                rtn_data = self._load_df_from_parquet_in_mc(mc_key=self.mc_key(),
                **load_params)
            else:
                raise LookupError('The source format {} is not currently supported'.format(file_type))
        self.reset_changed()
        return rtn_data

    def exists(self) -> bool:
        """ returns True if the file in mc exists """
        _cc = self.connector_contract
        mc_key = self.mc_key()
        return self.cortex_client.content.exists(key=mc_key)

    def reset_changed(self, changed: bool = False):
        """ manual reset to say the file has been seen. This is automatically called if the file is loaded"""
        changed = changed if isinstance(changed, bool) else False
        self._changed_flag = changed
    
    def has_changed(self) -> bool:
        """ 
            returns if the file has been modified
            uses etag
        """
        if not isinstance(self.connector_contract, ConnectorContract):
            raise ValueError("The Managed Content Connector Contract has not been set")
        _cc = self.connector_contract
        if not isinstance(_cc, ConnectorContract):
            raise ValueError("The Python Source Connector Contract has not been set correctly")
        load_params = _cc.kwargs
        load_params.update(_cc.query)  # Update kwargs with those in the uri query
        load_params.pop('token', None)
        load_params.pop('api_endpoint', None)
        load_params.pop('project', None)
        res = self._download_key_from_mc(self.mc_key())  
        _etag = res.headers['etag']
        if _etag != self._etag:
            self._changed_flag = True
            self._etag = _etag
        else:
            self._changed_flag = False
        return self._changed_flag

class McPersistHandler(McSourceHandler, AbstractPersistHandler):
    # A Managed Content persist handler

    def _persist_df_as_csv(self, canonical: pa.Table, mc_key: str, **kwargs):
        file_name = os.path.basename(mc_key)
        byte_obj = io.BytesIO()
        csv.write_csv(canonical, byte_obj)
        res = self.cortex_client.content.upload(key=mc_key, stream_name=file_name, stream=byte_obj, content_type="application/octet-stream", retries=2)
        return res
    
    def _persist_df_as_parquet(self, canonical: pa.Table, mc_key: str, **kwargs):
        file_name = os.path.basename(mc_key)
        pq.write_table(canonical, file_name)
        with open(file_name, mode="rb") as f_obj:
            res = self.cortex_client.content.upload(key=mc_key, stream_name=file_name, stream=f_obj, content_type="application/octet-stream", retries=2)
        return res

    def persist_canonical(self, canonical: pa.Table, **kwargs) -> bool:
        """ persists the canonical dataset
        Extra Parameters in the ConnectorContract kwargs:
            - file_type: (optional) the type of the source file. if not set, inferred from the file extension
        """
        if not isinstance(self.connector_contract, ConnectorContract):
            return False
        _uri = self.connector_contract.uri
        return self.backup_canonical(uri=_uri, canonical=canonical)

    def backup_canonical(self, canonical: pa.Table, uri: str, ignore_kwargs: bool = False) -> bool:
        """ creates a backup of the canonical to an alternative URI  """
        if not isinstance(self.connector_contract, ConnectorContract):
            return False
        _cc = self.connector_contract
        if not isinstance(_cc, ConnectorContract):
            raise ValueError("The Python Source Connector Contract has not been set correctly")
        schema, bucket, path = _cc.parse_address_elements(uri=uri)
        _, _, _ext = path.rpartition('.')
        load_params = _cc.kwargs
        load_params.update(_cc.query)  # Update kwargs with those in the uri query
        load_params.pop('token', None)
        load_params.pop('api_endpoint', None)
        load_params.pop('project', None)
        mc_key = self.mc_key()
        file_type = load_params.get('file_type', _ext if len(_ext) > 0 else 'parquet')
        with threading.Lock():
            if file_type.lower() in ['csv']:
                self._persist_df_as_csv(canonical, mc_key=mc_key, **load_params)
            elif file_type.lower() in ['parquet']:
                self._persist_df_as_parquet(canonical=canonical, mc_key=mc_key)
            else:
                raise LookupError('The source format {} is not currently supported'.format(file_type))

        return True

    def remove_canonical(self) -> bool:
        if not isinstance(self.connector_contract, ConnectorContract):
            raise ValueError("The Managed Content Connector Contract has not been set")
        _cc = self.connector_contract
        if not isinstance(_cc, ConnectorContract):
            raise ValueError("The Python Source Connector Contract has not been set correctly")
        load_params = _cc.kwargs
        load_params.update(_cc.query)  # Update kwargs with those in the uri query
        load_params.pop('token', None)
        load_params.pop('api_endpoint', None)
        load_params.pop('project', None)
        self.cortex_client.content.delete(self.mc_key())
        if not self.exists():
            return True
        return False
