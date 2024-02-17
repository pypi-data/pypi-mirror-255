import unittest
import os
from pathlib import Path
import shutil
import ast
from datetime import datetime

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from ds_core.properties.property_manager import PropertyManager
from ds_capability import *
from ds_capability.components.commons import Commons
from ds_capability.handlers.duckdb_handlers import DuckdbSourceHandler, DuckdbPersistHandler

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class DuckdbTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # clean out any old environments
        for key in os.environ.keys():
            if key.startswith('HADRON'):
                del os.environ[key]
        # Local Domain Contract
        os.environ['HADRON_PM_PATH'] = os.path.join('working', 'contracts')
        os.environ['HADRON_PM_TYPE'] = 'parquet'
        # Local Connectivity
        os.environ['HADRON_DEFAULT_PATH'] = Path('working/data').as_posix()
        # Specialist Component
        try:
            os.makedirs(os.environ['HADRON_PM_PATH'])
        except OSError:
            pass
        try:
            os.makedirs(os.environ['HADRON_DEFAULT_PATH'])
        except OSError:
            pass
        try:
            shutil.copytree('../_test_data', os.path.join(os.environ['PWD'], 'working/source'))
        except OSError:
            pass
        PropertyManager._remove_all()

    def tearDown(self):
        try:
            shutil.rmtree('working')
        except OSError:
            pass

    def test_default(self):
        fe = FeatureEngineer.from_memory()
        tbl = fe.tools.get_synthetic_data_types(10, seed=1)
        source_uri = f"duckdb://"
        persist_uri = f"duckdb://"
        fe.set_source_uri(source_uri)
        # persist
        fe.set_persist_uri(persist_uri)
        fe.save_persist_canonical(tbl)
        # source
        result = fe.load_source_canonical()
        self.assertEqual((10,6), result.shape)
        # distinct
        distinct_sql = "SELECT num, int FROM @"
        distinct_uri = f"duckdb://?sql_query={distinct_sql}"
        fe.add_connector_uri('distinct', distinct_uri)
        result = fe.load_canonical('distinct')
        self.assertEqual((10,2), result.shape)

    def test_table(self):
        fe = FeatureEngineer.from_memory()
        tbl = fe.tools.get_synthetic_data_types(10, seed=1)
        source_uri = f"duckdb://?table=my_test"
        persist_uri = f"duckdb://?table=my_test"
        fe.set_source_uri(source_uri)
        # persist
        fe.set_persist_uri(persist_uri)
        fe.save_persist_canonical(tbl)
        # source
        result = fe.load_source_canonical()
        self.assertEqual((10, 6), result.shape)

    def test_s3(self):
        fe = FeatureEngineer.from_memory()
        tbl = fe.tools.get_synthetic_data_types(100)
        s3_uri = 's3://project-hadron-cs-repo/domain/synthetic/source/duckdb_tbl_100.parquet'
        persist_uri = f"duckdb://{s3_uri}"
        # persist_uri = f"duckdb://?table={s3_uri}&sql={persist_sql}"
        fe.set_persist_uri(persist_uri)
        fe.save_persist_canonical(tbl)
        s3_uri = 's3://project-hadron-cs-repo/domain/synthetic/source/synthetic_sample.parquet'
        source_uri = f"duckdb:///?table={s3_uri}"
        fe.set_source_uri(source_uri)
        result = fe.load_source_canonical()
        print(result.shape)

    def test_s3_direct(self):
        fe = FeatureEngineer.from_memory()
        tbl = fe.tools.get_synthetic_data_types(100)
        s3_uri = 's3://project-hadron-cs-repo/domain/synthetic/source/duckdb_tbl_100.parquet'
        conn = duckdb.connect(':default:')
        conn.execute(f"""
            INSTALL httpfs;
            LOAD httpfs;
            SET s3_region='{os.environ.get('AWS_DEFAULT_REGION')}';
            SET s3_access_key_id='{os.environ.get('AWS_ACCESS_KEY_ID')}';
            SET s3_secret_access_key='{os.environ.get('AWS_SECRET_ACCESS_KEY')}';
        """)
        conn.execute(f"COPY tbl TO '{s3_uri}'")
        # export
        result = conn.execute(f"SELECT * FROM read_parquet('{s3_uri}')").arrow()
        print(result.shape)

    def test_local_direct(self):
        fe = FeatureEngineer.from_memory()
        tbl = fe.tools.get_synthetic_data_types(100)
        conn = duckdb.connect(':default:')
        conn.execute("CREATE OR REPLACE TABLE my_arrow AS SELECT * FROM tbl;")
        conn.execute("CREATE OR REPLACE TABLE dup AS SELECT * FROM tbl;")
        result = conn.execute("SELECT * FROM my_arrow;").arrow()
        print(result.shape)
        result = conn.execute("CALL duckdb_tables()").arrow()
        print(result.column('table_name'))
        print(pc.is_in('my_arrow', result.column('table_name')).as_py())


    def test_raise(self):
        startTime = datetime.now()
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))
        print(f"Duration - {str(datetime.now() - startTime)}")


def tprint(t: pa.table, headers: [str, list] = None, d_type: [str, list] = None, regex: [str, list] = None):
    _ = Commons.filter_columns(t.slice(0, 10), headers=headers, d_types=d_type, regex=regex)
    print(Commons.table_report(_).to_string())


if __name__ == '__main__':
    unittest.main()
