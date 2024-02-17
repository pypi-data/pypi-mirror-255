import unittest
import os
import pyarrow as pa
from cortex.utils import generate_token
from pprint import pprint

from ds_capability.components.commons import Commons

from ds_capability.handlers.mc_handlers import McSourceHandler, McPersistHandler
from ds_core.handlers.abstract_handlers import ConnectorContract, HandlerFactory


class ManagedContentHandlerTest(unittest.TestCase):

    def setUp(self):
        PAT = {"jwk": {"crv": "Ed25519", "d": "chtqzYc7igE62XMI9U0y_NbOjjDGoO2k6AnNCvasK_4",
                       "x": "oJa4EVeM0rhJGZUs_DH-MuKOsmrWS0Kj3E_TDPY_k-Q", "kty": "OKP",
                       "kid": "5x0yfsfU57eL_BLr9pnaj1fyLyufFJYpza_N8A8JSH8", "alg": "EdDSA"}, "issuer": "tecnotree.com",
               "audience": "sensa", "username": "1652d24e-7974-4a83-896d-0eac230a1c62",
               "url": "https://api.dci-dev.dev-eks.insights.ai"}
        os.environ["TOKEN"] = generate_token(PAT)
        os.environ["API_ENDPOINT"] = "https://api.dci-dev.dev-eks.insights.ai"
        os.environ['PROJECT'] = "bptest"

    def tearDown(self):
        del os.environ["TOKEN"]
        del os.environ["API_ENDPOINT"]
        del os.environ['PROJECT']

    def test_mc_handler(self):
        """
        required params: 
            - uri : used as the key for managed content
            - api_endpoint: cortex api endpoint
            - token: cortex token
            - project: cortex project
        """
        cc = ConnectorContract(uri='mc://test/test.parquet', module_name='', handler='')
        handler = McPersistHandler(cc)
        tbl = pa.table([pa.array([1,2,3,4,5])], names=['a'])
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        self.assertTrue(handler.has_changed())
        self.assertFalse(handler.has_changed())
        self.assertEqual((5,1),result.shape)
        self.assertTrue(handler.remove_canonical())
        #
        cc = ConnectorContract(uri='mc://test/test.csv', module_name='', handler='')
        handler = McPersistHandler(cc)
        tbl = pa.table([pa.array([1,2,3,4,5])], names=['a'])
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        self.assertTrue(handler.has_changed())
        self.assertFalse(handler.has_changed())
        self.assertEqual((5,1),result.shape)
        self.assertTrue(handler.remove_canonical())


if __name__ == '__main__':
    unittest.main()