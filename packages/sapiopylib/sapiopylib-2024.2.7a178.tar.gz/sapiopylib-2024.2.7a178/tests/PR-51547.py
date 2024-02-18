import unittest

from data_type_models import SampleModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel

from sapiopylib.rest.utils.FoundationAccessioning import FoundationAccessionManager

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
data_record_manager = DataMgmtServer.get_data_record_manager(user)
eln_manager = DataMgmtServer.get_eln_manager(user)
rec_man = RecordModelManager(user)
inst_man = rec_man.instance_manager

class TestPR51547(unittest.TestCase):
    def test_record_cache(self):
        sample: SampleModel = inst_man.add_new_record_of_type(SampleModel)
        field_changes = sample.fields.copy_changes_to_dict()
        self.assertFalse(field_changes, "There shouldn't have been any field changes initially")
        sample.set_OtherSampleId_field("Blah")
        field_changes = sample.fields.copy_changes_to_dict()
        self.assertTrue(field_changes['OtherSampleId'] and len(field_changes) == 1,
                        "The sample name should have been filled and this becomes length 1")
        rec_man.store_and_commit()
        field_changes = sample.fields.copy_changes_to_dict()
        self.assertFalse(field_changes, "After store and commit the field changes should be returned to empty.")