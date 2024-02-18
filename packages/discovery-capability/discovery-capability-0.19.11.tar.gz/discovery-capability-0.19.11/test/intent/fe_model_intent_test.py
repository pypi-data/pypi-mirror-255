import unittest
import os
from pathlib import Path
import shutil
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from ds_capability import *
from ds_capability.components.commons import Commons
from ds_capability.intent.feature_engineer_intent import FeatureEngineerIntent
from ds_core.properties.property_manager import PropertyManager
from ds_capability.components.visualization import Visualisation as viz

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class FeatureEngineerModelTest(unittest.TestCase):

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
        PropertyManager._remove_all()

    def tearDown(self):
        try:
            shutil.rmtree('working')
        except OSError:
            pass

    def test_for_smoke(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        tbl = FeatureEngineer.from_memory().tools.get_synthetic_data_types(100)
        self.assertEqual(100, tbl.num_rows)
        
    def test_model_cat_cast(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        tbl = FeatureEngineer.from_memory().tools.get_synthetic_data_types(100)
        result = tools.model_cat_cast(tbl)
        schema = pa.schema([
            ("cat", pa.string()),
            ("num", pa.string()),
            ("int", pa.string()),
            ("bool", pa.string()),
            ("date", pa.string()),
            ("string", pa.string()),
        ])
        self.assertEqual(result.schema, schema)
        tbl = FeatureEngineer.from_memory().tools.get_synthetic_data_types(100)
        result = tools.model_cat_cast(tbl, cat_type=True)
        schema = pa.schema([
            ("cat", pa.dictionary(pa.int32(), pa.utf8())),
            ("num", pa.dictionary(pa.int32(), pa.utf8())),
            ("int", pa.dictionary(pa.int32(), pa.utf8())),
            ("bool", pa.dictionary(pa.int32(), pa.utf8())),
            ("date", pa.dictionary(pa.int32(), pa.utf8())),
            ("string", pa.dictionary(pa.int32(), pa.utf8())),
        ])
        self.assertEqual(result.schema, schema)

    def test_model_num_cast(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        tbl = FeatureEngineer.from_memory().tools.get_synthetic_data_types(100, category_encode=False)
        tbl = tools.model_cat_cast(tbl)
        result = tools.model_num_cast(tbl)
        schema = pa.schema([
            ("cat", pa.string()),
            ("num", pa.float64()),
            ("int", pa.int64()),
            ("bool", pa.int64()),
            ("date", pa.timestamp('ns')),
            ("string", pa.string()),
        ])
        self.assertEqual(result.schema, schema)
        tbl = pa.table([pa.array(['$1,000.00', '$56.34', '$0.45'])], names=['currency'])
        result = tools.model_num_cast(tbl, remove=['$', ','])
        self.assertEqual('double', result.column('currency').type)
        self.assertEqual([1000.0, 56.34, 0.45], result.column('currency').to_pylist())

    def test_model_sample_link(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        canonical = FeatureEngineer.from_memory().tools.get_synthetic_data_types(10, category_encode=False)
        other = FeatureEngineer.from_memory().tools.get_synthetic_data_types(5, category_encode=False)
        result = tools.model_concat_remote(canonical=canonical, other=other, headers=['int'], rename_map=['key'])
        self.assertCountEqual(result.column_names, canonical.column_names+['key'])
        result = tools.model_concat_remote(canonical=canonical, other=other, headers=['int', 'num'], rename_map={'int': 'key', 'num': 'prob'})
        self.assertCountEqual(result.column_names, canonical.column_names + ['key', 'prob'])
        result = tools.model_concat_remote(canonical=canonical, other=other, headers=['int'], rename_map=['key1'], multi_map={'key2': 'key1'})
        self.assertCountEqual(result.column_names, canonical.column_names + ['key1', 'key2'])
        self.assertTrue(result.column('key1').equals(result.column('key2')))


    def test_raise(self):
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))

    def get_party_table(self):
        document = [
            {"_id": "PI1832341", "interactionDate": {"startDateTime": "2023-01-02 04:49:06.955000", "endDateTime": "2023-01-02 04:50:35.130000"}, "status": "failed", "relatedParty": [{"_id": "C5089669", "role": "Customer", "engagedParty": {"_id": "I249908", "referredType": "Individual"}}, {"_id": "dclmappuser1", "role": "CSRAgent"}], "interactionItem": [{"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR716796"], "type": "DeLinkProductUserRequest"},
            {"_id": "PI1832345", "interactionDate": {"startDateTime": "2023-01-02 04:52:47.834000", "endDateTime": "2023-01-02 04:52:53.122000"}, "status": "failed", "relatedParty": [{"_id": "C5089669", "role": "Customer", "engagedParty": {"_id": "I249908", "referredType": "Individual"}}, {"_id": "dclmappuser1", "role": "CSRAgent"}], "interactionItem": [{"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721074"], "type": "DeLinkProductUserRequest"},
            {"_id": "PI1832352", "interactionDate": {"startDateTime": "2023-01-02 04:58:06.792000", "endDateTime": "2023-01-02 04:59:42.650000"}, "status": "failed", "relatedParty": [{"_id": "dclmappuser1", "role": "CSRAgent"}, {"_id": "C5091676", "role": "Customer", "engagedParty": {"_id": "I253956", "referredType": "Individual"}}], "interactionItem": [{"item": {"requestedStartDate": "2023-01-02 04:59:38.298000"}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721185"], "type": "RegistrationRequest"},
            {"_id": "PI1832357", "interactionDate": {"startDateTime": "2023-01-02 05:06:12.877000", "endDateTime": "2023-01-02 05:07:49.597000"}, "status": "completed", "relatedParty": [{"_id": "dclmappuser1", "role": "CSRAgent"}, {"_id": "C5091679", "role": "Customer", "engagedParty": {"_id": "I253962", "referredType": "Individual"}}], "interactionItem": [{"item": {"requestedStartDate": "2023-01-02 05:07:44.329000"}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721189"], "type": "RegistrationRequest"},
            {"_id": "PI1832365", "interactionDate": {"startDateTime": "2023-01-02 05:13:52.453000", "endDateTime": "2023-01-02 05:15:12.898000"}, "status": "completed", "relatedParty": [{"_id": "dclmappuser1", "role": "CSRAgent"}, {"_id": "C5091686", "role": "Customer", "engagedParty": {"_id": "I253969", "referredType": "Individual"}}], "interactionItem": [{"item": {"requestedStartDate": "2023-01-02 05:15:08.082000"}}, {"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721193"], "type": "RegistrationRequest"},
            {"_id": "PI1832363", "interactionDate": {"startDateTime": "2023-01-02 05:13:50.672000", "endDateTime": "2023-01-02 05:16:20.100000"}, "status": "completed", "relatedParty": [{"_id": "dclmappuser1", "role": "CSRAgent"}, {"_id": "C5091684", "role": "Customer", "engagedParty": {"_id": "I253967", "referredType": "Individual"}}], "interactionItem": [{"item": {"requestedStartDate": "2023-01-02 05:16:14.449000"}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721199"], "type": "RegistrationRequest"},
            {"_id": "PI1832370", "interactionDate": {"startDateTime": "2023-01-02 05:16:10.685000", "endDateTime": "2023-01-02 05:17:44.885000"}, "status": "completed", "relatedParty": [{"_id": "dclmappuser1", "role": "CSRAgent"}, {"_id": "C5091690", "role": "Customer", "engagedParty": {"_id": "I253974", "referredType": "Individual"}}], "interactionItem": [{"item": {"requestedStartDate": "2023-01-02 05:17:39.901000"}}, {"item": {}}, {"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721203"], "type": "RegistrationRequest"},
            {"_id": "PI1832376", "interactionDate": {"startDateTime": "2023-01-02 05:28:06.660000", "endDateTime": "2023-01-02 05:28:14.543000"}, "status": "failed", "relatedParty": [{"_id": "C5089669", "role": "Customer", "engagedParty": {"_id": "I249908", "referredType": "Individual"}}, {"_id": "dclmappuser1", "role": "CSRAgent"}], "interactionItem": [{"item": {}}, {"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721074"], "type": "DeLinkProductUserRequest"},
            {"_id": "PI1832385", "interactionDate": {"startDateTime": "2023-01-02 05:35:44.427000"}, "status": "draft", "relatedParty": [{"_id": "C5091684", "role": "Customer", "engagedParty": {"_id": "I253967", "referredType": "Individual"}}, {"_id": "dclmappuser1", "role": "CSRAgent"}], "interactionItem": [{"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721199"], "type": "ModifyPlanProductRequest"},
            {"_id": "PI1832388", "interactionDate": {"startDateTime": "2023-01-02 05:35:59.615000"}, "status": "draft", "relatedParty": [{"_id": "C5091684", "role": "Customer", "engagedParty": {"_id": "I253967", "referredType": "Individual"}}, {"_id": "dclmappuser1", "role": "CSRAgent"}], "interactionItem": [{"item": {}}, {"item": {}}], "channel": [{"name": "DCLM", "role": "interaction creation", "referredType": "Channel"}], "productId": ["PR721199"], "type": "AddVasProductRequest"},
        ]
        return Commons.table_flatten(pa.Table.from_pylist(document))
    def get_indivdual_table(self):
        document = [
            {"_id": "I35138", "contactMedium": [{"medium": {"number": "50070028", "type": "mobile"}, "preferred": True}, {"medium": {"emailAddress": "mail@stc.com.kw", "type": "emailAddress"}, "preferred": True}], "gender": "M", "familyName": "Fouad", "givenName": "Fouad", "middleName": "Fouad"},
            {"_id": "I35145", "contactMedium": [{"medium": {"emailAddress": "panneer.rajadurai.c@solutions.com.kw", "type": "EmailAddress"}, "preferred": True}, {"medium": {"number": "51658317", "type": "mobile"}, "preferred": True}, {"medium": {"number": "51658317", "type": "whatsapp"}, "preferred": False}, {"medium": {"number": "51658317", "type": "telegram"}, "preferred": False}, {"medium": {"type": "telephone"}, "role": "AlternateNumber"}], "gender": "M", "familyName": "Jay", "givenName": "Bhuvana", "middleName": ""},
            {"_id": "I35146", "contactMedium": [{"medium": {"emailAddress": "bhuvana.stc21@gmail.com", "type": "EmailAddress"}, "preferred": True}, {"medium": {"type": "mobile"}, "preferred": False}, {"medium": {"type": "whatsapp"}, "preferred": False}, {"medium": {"type": "telegram"}, "preferred": False}], "gender": "F", "familyName": "CORP", "givenName": "TECNOTREE", "middleName": "LTD"},
            {"_id": "I35178", "contactMedium": [{"medium": {"emailAddress": "m.m.alkhoduri@outlook.com", "type": "emailAddress"}, "preferred": True}, {"medium": {"number": "55850055", "type": "mobile"}, "preferred": True}, {"medium": {"number": "55850055", "type": "whatsapp"}, "preferred": False}, {"medium": {"number": "55850055", "type": "telegram"}, "preferred": False}], "gender": "M", "familyName": "", "givenName": "MohammadalKoduri", "middleName": ""},
            {"_id": "I35179", "contactMedium": [{"medium": {"emailAddress": "ahb@bremenintl.com", "type": "emailAddress"}, "preferred": True}, {"medium": {"number": "51500014", "type": "mobile"}, "preferred": True}, {"medium": {"number": "51500014", "type": "whatsapp"}, "preferred": False}, {"medium": {"number": "51500014", "type": "telegram"}, "preferred": False}], "gender": "M", "familyName": "", "givenName": "AhmedBakhiet", "middleName": ""},
            {"_id": "I35180", "contactMedium": [{"medium": {"emailAddress": "test@gmail.com", "type": "emailAddress"}, "preferred": True}], "gender": "M", "familyName": "Admin", "givenName": "FakhrTest", "middleName": ""},
            {"_id": "I35181", "contactMedium": [], "gender": "M", "familyName": "test", "givenName": "test", "nationality": "", "middleName": ""}
        ]
        return Commons.table_flatten(pa.Table.from_pylist(document))

def tprint(t: pa.table, headers: [str, list]=None, d_type: [str, list]=None, regex: [str, list]=None):
    _ = Commons.filter_columns(t.slice(0,10), headers=headers, d_types=d_type, regex=regex)
    print(Commons.table_report(_).to_string())


if __name__ == '__main__':
    unittest.main()
