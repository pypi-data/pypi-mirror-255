import unittest
import os
from pathlib import Path
import shutil
from datetime import datetime
import pandas as pd
import pyarrow as pa

import pyarrow.compute as pc
from ds_capability.components.commons import Commons

from ds_capability.handlers.pyarrow_handlers import PyarrowSourceHandler, PyarrowPersistHandler
from ds_core.handlers.abstract_handlers import ConnectorContract
from ds_core.properties.property_manager import PropertyManager

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class FeatureBuilderTest(unittest.TestCase):

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
        os.environ['HADRON_PM_TYPE'] = 'json'
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

    def test_parquet(self):
        tbl = get_table()
        uri = os.path.join(os.environ['HADRON_DEFAULT_PATH'], 'test.parquet')
        cc = ConnectorContract(uri, 'module_name', 'handler')
        handler = PyarrowPersistHandler(cc)
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        self.assertEqual(tbl.column_names, result.column_names)
        self.assertEqual(tbl.shape, result.shape)
        self.assertEqual(tbl.schema, result.schema)

    def test_csv(self):
        tbl = get_table()
        uri = os.path.join(os.environ['HADRON_DEFAULT_PATH'], 'test.csv')
        cc = ConnectorContract(uri, 'module_name', 'handler')
        handler = PyarrowPersistHandler(cc)
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        self.assertEqual(tbl.column_names, result.column_names)
        self.assertEqual(tbl.shape, result.shape)

    def test_csv_https(self):
        tbl = get_table()
        uri = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
        cc = ConnectorContract(uri, 'module_name', 'handler')
        handler = PyarrowPersistHandler(cc)
        result = handler.load_canonical()
        self.assertEqual((891, 15), result.shape)

    def test_json(self):
        tbl = get_table()
        uri = os.path.join(os.environ['HADRON_DEFAULT_PATH'], 'test.json')
        cc = ConnectorContract(uri, 'module_name', 'handler')
        handler = PyarrowPersistHandler(cc)
        # tbl
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        print(result.shape)
        # properties
        cfg = {'feature_build': {'data_profiling': {'description': '', 'version': '0.0.1', 'status': 'discovery', 'connectors': {'pm_feature_build_data_profiling': {'raw_uri': 'working/contracts/hadron_pm_feature_build_data_profiling.json', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'template_source': {'raw_uri': 'working/data', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowSourceHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'template_persist': {'raw_uri': 'working/data', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'primary_source': {'raw_uri': '${HADRON_PROFILING_SOURCE_URI}', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'primary_persist': {'raw_uri': 'event://profiling', 'raw_module_name': 'ds_core.handlers.event_handlers', 'raw_handler': 'EventPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'quality': {'raw_uri': '${HADRON_DATA_QUALITY_URI}', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'dictionary': {'raw_uri': '${HADRON_DATA_DICTIONARY_URI}', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}, 'schema': {'raw_uri': '${HADRON_DATA_SCHEMA_URI}', 'raw_module_name': 'ds_capability.handlers.pyarrow_handlers', 'raw_handler': 'PyarrowPersistHandler', 'raw_version': '0.0.1', 'raw_kwargs': {}, 'aligned': False}}, 'intent': {'primary': {'0': {'build_profiling': {'profiling': 'quality', 'connector_name': 'quality', 'save_intent': False}}, '1': {'build_profiling': {'profiling': 'dictionary', 'connector_name': 'dictionary', 'save_intent': False}}, '2': {'build_profiling': {'profiling': 'schema', 'connector_name': 'schema', 'save_intent': False}}}}, 'snapshot': {}, 'run_book': {}, 'meta': {'module': ['ds_capability', 'managers', 'feature_build_property_manager'], 'class': 'FeatureBuildPropertyManager'}, 'knowledge': {'describe': {}, 'intent': {}, 'schema': {}}}}, 'config_meta': {'uid': 'c18ffafd-f28d-4835-81f8-bd5d580fb54a', 'create': '2023-10-14 13:33:59.006304', 'modify': '2023-10-14 13:33:59.151534', 'release': '0.8.8'}}
        tbl = pa.Table.from_pylist([cfg])
        tbl = Commons.table_flatten(tbl)
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        print(result.shape)
        # swagger
        cfg = {'columnProfile': [{'customMetricsProfile': [{'name': 'string', 'value': 0}], 'distinctCount': 0, 'distinctProportion': 0, 'duplicateCount': 0, 'firstQuartile': 0, 'histogram': {'boundaries': [{}], 'frequencies': [{}]}, 'interQuartileRange': 0, 'max': {}, 'maxLength': 0, 'mean': 0, 'median': 0, 'min': {}, 'minLength': 0, 'missingCount': 0, 'missingPercentage': 0, 'name': 'string', 'nonParametricSkew': 0, 'nullCount': 0, 'nullProportion': 0, 'stddev': 0, 'sum': 0, 'thirdQuartile': 0, 'timestamp': 0, 'uniqueCount': 0, 'uniqueProportion': 0, 'validCount': 0, 'valuesCount': 0, 'valuesPercentage': 0, 'variance': 0}], 'systemProfile': [{'operation': 'UPDATE', 'rowsAffected': 0, 'timestamp': 0}], 'tableProfile': {'columnCount': 0, 'createDateTime': '2019-08-24T14:15:22Z', 'profileSample': 0, 'profileSampleType': 'PERCENTAGE', 'rowCount': 0, 'sizeInByte': 0, 'timestamp': 0}}
        tbl = pa.Table.from_pylist([cfg])
        tbl = Commons.table_flatten(tbl)
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        print(result.shape)

    def test_txt(self):
        tbl = get_table()
        uri = os.path.join(os.environ['HADRON_DEFAULT_PATH'], 'test.txt')
        cc = ConnectorContract(uri, 'module_name', 'handler')
        handler = PyarrowPersistHandler(cc)
        handler.persist_canonical(tbl)
        result = handler.load_canonical()
        self.assertEqual(tbl.column_names, result.column_names)
        self.assertEqual(tbl.shape, result.shape)

    def test_raise(self):
        startTime = datetime.now()
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))
        print(f"Duration - {str(datetime.now() - startTime)}")



def get_table():
    num = pa.array([1.0, None, 5.0, -0.46421, 3.5, 7.233, -2], pa.float64())
    val = pa.array([1, 2, 3, 4, 5, 6, 7], pa.int64())
    date = pc.strptime(["2023-01-02 04:49:06", "2023-01-02 04:57:12", None, None, "2023-01-02 05:23:50", None, None],
                       format='%Y-%m-%d %H:%M:%S', unit='us')
    text = pa.array(["Blue", "Green", None, 'Red', 'Orange', 'Yellow', 'Pink'], pa.string())
    binary = pa.array([True, True, None, False, False, True, False], pa.bool_())
    cat = pa.array([None, 'M', 'F', 'M', 'F', 'M', 'M'], pa.string()).dictionary_encode()
    return pa.table([num, val, date, text, binary, cat], names=['num', 'int', 'date', 'text', 'bool', 'cat'])


if __name__ == '__main__':
    unittest.main()
