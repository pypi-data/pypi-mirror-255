import ast
import unittest
import os
from pathlib import Path
import shutil
from datetime import datetime
from pprint import pprint

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from ds_core.handlers.event_handlers import EventManager
from ds_core.properties.property_manager import PropertyManager
from ds_capability import FeatureEngineer, Controller, FeatureSelect
from ds_capability.components.pipeline_scripts import run_repo_pipeline

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

    def test_controller(self):
        # setup
        os.environ['HADRON_CLEAN_SOURCE_URI'] = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'
        os.environ['HADRON_CLEAN_PERSIST_URI'] = 'event://demo/'

        fs = FeatureSelect.from_env('auto_clean', has_contract=False)
        fs.set_source_uri('${HADRON_CLEAN_SOURCE_URI}')
        fs.set_persist_uri('${HADRON_CLEAN_PERSIST_URI}')

        tbl = fs.load_source_canonical()
        tbl = fs.tools.auto_clean_header(tbl)
        tbl = fs.tools.auto_drop_noise(tbl)
        tbl = fs.tools.auto_drop_correlated(tbl)
        tbl = fs.tools.auto_drop_duplicates(tbl)
        tbl = fs.tools.auto_cast_types(tbl, include_category=False, include_bool=False)

        ctr = Controller.from_env(has_contract=False)
        ctr.register.feature_select('auto_clean')

        # reuse
        os.environ['HADRON_CLEAN_SOURCE_URI'] = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv'
        os.environ['HADRON_CLEAN_PERSIST_URI'] = 'event://demo/'
        os.environ['HADRON_PM_REPO'] = './working/contracts/'

        ctr = Controller.from_env()
        ctr.run_controller()

        # review
        ctr.set_persist_uri('event://demo/')
        print(ctr.table_report(ctr.load_persist_canonical()).to_string())

    def test_controller_scripts(self):
        repo_path = "https://github.com/project-hadron/hadron-asset-bank/blob/master/contracts/pyarrow/data_profiling"
        tbl = FeatureEngineer.from_memory().tools.get_synthetic_data_types(100)
        # pass the environ variables
        result = run_repo_pipeline(tbl, repo_path=repo_path,
                                   hadron_profiing_source_uri='s3://project-hadron-cs-repo/domain/synthetic/source/synthetic_type_10_000.parquet',
                                   hadron_profiing_persist_uri='s3://project-hadron-cs-repo/domain/synthetic/persist/synthetic_type_10_000_processed.parquet',
                                   hadron_data_profile_uri='s3://project-hadron-cs-repo/domain/synthetic/persist/quality.parquet',
                                   hadron_data_dictionary_uri='s3://project-hadron-cs-repo/domain/synthetic/persist/dictionary.parquet',
                                   hadron_data_schema_uri='s3://project-hadron-cs-repo/domain/synthetic/persist/schema.parquet')
        print(result.shape)

    def test_raise(self):
        startTime = datetime.now()
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))
        print(f"Duration - {str(datetime.now() - startTime)}")


def get_table(size: int=10, inc_null: bool=None):
    return FeatureEngineer.from_memory().tools.get_synthetic_data_types(size=size, extend=inc_null)

def set_service():
    EventManager().set('sample', get_table())
    fb1 = FeatureEngineer.from_env('task1', has_contract=False)
    # fb1.set_source_uri('./working/source/hadron_synth_origin.pq')
    fb1.set_persist()
    tbl = fb1.tools.get_synthetic_data_types(size=10)
    _ = fb1.tools.get_noise(size=10, num_columns=2, canonical=tbl)
    fb1.run_component_pipeline()
    pprint(pm_view('feature_build', 'task1'))
    fb2 = FeatureEngineer.from_env('task2', has_contract=False)
    fb2.set_source_uri(fb1.get_persist_contract().raw_uri)
    fb2.set_persist()
    source_tbl = fb2.load_source_canonical()
    _ = fb2.tools.correlate_number(canonical=source_tbl, header='num', column_name='corr')
    fb2.run_component_pipeline()
    controller = Controller.from_env(has_contract=False)
    controller.intent_model.feature_build(canonical=None, task_name='task1', intent_level='task1_tr')
    controller.intent_model.wrangle(canonical=None, task_name='task2', intent_level='task2_wr')

def pm_view(capability: str, task: str, section: str=None):
    uri = os.path.join(os.environ['HADRON_PM_PATH'], f"hadron_pm_{capability}_{task}.parquet")
    tbl = pq.read_table(uri)
    tbl = tbl.column(0).combine_chunks()
    result = ast.literal_eval(tbl.to_pylist()[0]).get(capability,{}).get(task,{})
    return result.get(section, {}) if isinstance(section, str) and section in result.keys() else result



if __name__ == '__main__':
    unittest.main()
