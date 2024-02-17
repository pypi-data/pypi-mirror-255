import unittest
import os
from pathlib import Path
import shutil
import ast
from datetime import datetime
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from ds_core.properties.property_manager import PropertyManager
from ds_capability import *
from ds_capability.components.commons import Commons
from ds_capability.components.visualization import Visualisation as viz

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class VisualisationTest(unittest.TestCase):

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

    def test_for_smoke(self):
        fe = FeatureEngineer.from_memory()
        tbl = fe.tools.get_synthetic_data_types(100000)
        result = viz.show_chi_square(tbl, target='bool', capped_at=100*tbl.num_columns)
        print(result)


    def test_show_distribution(self):
        fs = FeatureSelect.from_memory()
        _ = fs.add_connector_uri('orders', uri='s3://project-hadron-cs-repo/downloads/data/STOCK_ORDERS.csv')
        orders = fs.load_canonical('orders', delimiter=u"\u0009")
        orders = fs.tools.auto_reinstate_nulls(orders, nulls_list=['?'])
        orders = fs.tools.auto_cast_types(orders, include_category=False, tm_format="%m/%d/%Y %H:%M:%S.000000")
        result = viz.show_distributions(orders)
        print(result)

    def test_show_category_frequency(self):
        fs = FeatureSelect.from_memory()
        _ = fs.add_connector_uri('orders', uri='s3://project-hadron-cs-repo/downloads/data/STOCK_ORDERS.csv')
        orders = fs.load_canonical('orders', delimiter=u"\u0009")
        orders = fs.tools.auto_reinstate_nulls(orders, nulls_list=['?'])
        orders = fs.tools.auto_cast_types(orders, include_category=False, tm_format="%m/%d/%Y %H:%M:%S.000000")
        result = viz.show_category_frequency(orders, target_dt='ORD_DTS')
        print(result)

    def test_show_num_density(self):
        fs = FeatureSelect.from_memory()
        _ = fs.add_connector_uri('orders', uri='s3://project-hadron-cs-repo/downloads/data/STOCK_ORDERS.csv')
        orders = fs.load_canonical('orders', delimiter=u"\u0009")
        orders = fs.tools.auto_reinstate_nulls(orders, nulls_list=['?'])
        orders = fs.tools.auto_cast_types(orders, include_category=False, tm_format="%m/%d/%Y %H:%M:%S.000000")
        result = viz.show_numeric_density(orders)
        print(result)

    def test_show_categories(self):
        fs = FeatureSelect.from_memory()
        _ = fs.add_connector_uri('titanic', uri='s3://project-hadron-cs-repo/downloads/data/titanic_kaggle_train.csv')
        titanic = fs.load_canonical('titanic')
        titanic = fs.tools.auto_drop_columns(titanic, headers=['PassengerId', 'Name'])
        titanic = fs.tools.auto_reinstate_nulls(titanic)
        titanic = fs.tools.auto_cast_types(titanic, include_category=False)
        result = viz.show_categories(titanic, headers=['Ticket', 'Cabin'], drop=True)
        print(result)


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
