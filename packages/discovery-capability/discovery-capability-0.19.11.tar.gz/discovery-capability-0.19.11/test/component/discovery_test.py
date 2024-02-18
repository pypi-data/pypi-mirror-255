import unittest
import os
from datetime import datetime
from pathlib import Path
import shutil
from pprint import pprint
import pyarrow as pa
import pyarrow.compute as pc
import pandas as pd
from ds_capability.components.commons import Commons

from ds_capability.intent.feature_engineer_intent import FeatureEngineerIntent

from ds_capability import FeatureEngineer, FeatureEngineer
from ds_core.properties.property_manager import PropertyManager

from ds_capability.components.discovery import DataDiscovery

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class DiscoveryTest(unittest.TestCase):

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

    def test_interquartile_outliers(self):
        sb = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = sb.tools
        arr = pa.array([1,2,1,34,1,2,3])
        result = DataDiscovery.outliers_iqr(arr)
        self.assertEqual(([],[34]), result)

    def test_empirical_outliers(self):
        sb = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = sb.tools
        arr = pa.array([1,2,1,1,2,3]*100 +[34])
        result = DataDiscovery.outliers_empirical(arr)
        self.assertEqual(([],[34]), result)

    def test_data_dictionary(self):
        sb = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = sb.tools
        tbl = tools.get_synthetic_data_types(1_000, extend=True)
        result = DataDiscovery.data_dictionary(tbl, stylise=True)
        pprint(result.to_string())

    def test_data_quality(self):
        sb = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = sb.tools
        tbl = tools.get_synthetic_data_types(100_000, extend=True)
        result = DataDiscovery.data_quality(tbl, stylise=True)
        pprint(result.to_string())

    def test_data_quality_ref(self):
        sb = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = sb.tools
        tbl = tools.get_synthetic_data_types(100_000, extend=True)
        result = DataDiscovery.data_quality(tbl, stylise=False)
        pprint(result.schema)

    def test_data_schema(self):
        sb = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = sb.tools
        tbl = tools.get_synthetic_data_types(1_000, extend=True)
        result = DataDiscovery.data_schema(tbl, stylise=True)
        pprint(result.to_string())

    def test_raise(self):
        startTime = datetime.now()
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))
        print(f"Duration - {str(datetime.now() - startTime)}")


if __name__ == '__main__':
    unittest.main()
