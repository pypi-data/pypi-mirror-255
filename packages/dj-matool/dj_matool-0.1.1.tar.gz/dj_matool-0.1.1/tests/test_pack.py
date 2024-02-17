"""
    @file: tests/run_pack_tests.py
    @createdBy: Manish Agarwal
    @createdDate: 3/22/2016
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 3/22/2016
    @type: file
    @desc: test file for pack apis
"""

import settings
import src.service.verification
from model.model_template import *
from dosepack.base_model.base_model import db
from nose.tools import *
import time

# Include settings,pack,process_pharmacy_file and model tables required for models
from src import generate_packs


from dosepack.utilities.utils import get_all_startup_parameters
from src.parameters import populate_parameters

import json

# create instance of the Pack and ProcessPharmacyFile
pack_instance = _old.Pack("test")
process_file = process_file_template.ProcessPharmacyFile("test")

import dosepack.utilities.utils

db.init("dosepacker", user="root", password="root")

data = get_all_startup_parameters()
data = json.loads(data)
populate_parameters(data["data"])


class TestPack(object):

    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""
        """ Clear all the data from the tables"""
        try:
            slot_details_instance = slot_details.delete()
            template_tracker_instance = template_tracker.delete()
            pack_status_tracker_instance = pack_status_tracker.delete()
            pack_verification_instance = pack_verification.delete()
            pack_header_instance = pack_header.delete()
            file_header_instance = file_header.delete()

            slot_details_instance.execute()
            template_tracker_instance.execute()
            pack_status_tracker_instance.execute()
            pack_verification_instance.execute()
            pack_header_instance.execute()
            file_header_instance.execute()
        except Exception as ex:
            print(ex)
            raise Exception("Setup Failed")

        filename1 = 'test1.dat'
        filename2 = 'test2.dat'

        args1 = {"filename": filename1, "robot_id": settings.DEFAULT_ROBOT_ID, "username": "admin"}
        args2 = {"filename": filename2, "robot_id": settings.DEFAULT_ROBOT_ID, "username": "admin"}

        process_pharmacy_file_instance = process_file_template.ProcessPharmacyFile(
            "test")

        process_pharmacy_file_instance.process_file(args1)
        file_id = get_max_file_id()
        print(file_id)

        process_pharmacy_file_instance.generate_packs_from_file(str(file_id), settings.DEFAULT_ROBOT_ID, "admin")

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class after any tests are run"""
        pass

    def test_get_packlist_info(self):

        # true input
        test_args1 = {"date_from": dosepack.utilities.utils.get_current_date(), "date_to": dosepack.utilities.utils.get_current_date(), "robot_id": 6,
                     "pack_status": "pending", "print_status":"0,1"}

        output = pack_instance.get_packlist_info(test_args1)
        output = json.loads(output)
        count = len(output["data"])
        actual_count = 4
        assert_equal(count, actual_count)

        test_args2 = {"date_from":dosepack.utilities.utils.get_current_date(), "date_to":dosepack.utilities.utils.get_current_date(), "robot_id":6,
                     "pack_status":"done", "print_status":"0,1"}

        output = pack_instance.get_packlist_info(test_args2)
        output = json.loads(output)
        count = len(output["data"])
        actual_count = 0
        assert_equal(count, actual_count)

        # false input
        test_args3 = {"date_from":dosepack.utilities.utils.get_current_date(), "date_to":dosepack.utilities.utils.get_current_date(), "robot_id":0,
                     "pack_status":"done", "print_status":"0,1"}

        output = pack_instance.get_packlist_info(test_args3)
        output = json.loads(output)
        status = output["status"]
        actual_status = 0
        assert_equal(status, actual_status)

        # time test
        start_time = time.time()
        output = pack_instance.get_packlist_info(test_args1)
        end_time = time.time()
        assert(end_time-start_time < 1)

        # input validation test
        output = pack_instance.get_packlist_info("invalid argument")
        output = json.loads(output)
        status = output["status"]
        actual_status = 0
        assert_equal(status, actual_status)

        # null input test
        output = pack_instance.get_packlist_info({})
        output = json.loads(output)
        status = output["status"]
        actual_status = 0
        assert_equal(status, actual_status)

    def test_get_pack_status(self):

        # true input
        valid_pack_id = pack_utilities_old.get_max_pack_id()
        output = pack_instance.get_pack_status({"packid": valid_pack_id})
        output = json.loads(output)["data"]
        actual_output = "pending"
        assert_equal(output,actual_output)

        # false input
        output = pack_instance.get_pack_status({"packid": 99999})
        output = json.loads(output)["status"]
        actual_output = 0
        assert_equal(output,actual_output)

        # time test
        start_time = time.time()
        output = pack_instance.get_pack_status({"packid": valid_pack_id})
        end_time = time.time()
        assert(end_time-start_time < 0.1)

        # null input test
        output = pack_instance.get_pack_status()
        output = json.loads(output)["status"]
        actual_output = 0
        assert_equal(output,actual_output)

    def test_set_pack_status(self):

        # true input
        valid_pack_id = pack_utilities_old.get_max_pack_id()
        output = pack_instance.set_pack_status({"packid": str(valid_pack_id), "status": "done", "username": "admin"})
        output = json.loads(output)["status"]
        actual_output = 1
        assert_equal(output, actual_output)

        output = pack_instance.get_pack_status({"packid": valid_pack_id})
        output = json.loads(output)["data"]
        actual_output = "done"
        assert_equal(output,actual_output)

        # false input
        output = pack_instance.set_pack_status({"packid": str(99999), "status": "done", "username": "admin"})
        output = json.loads(output)["status"]
        actual_output = 1
        assert_equal(output,actual_output)

        # time test
        start_time = time.time()
        output = pack_instance.set_pack_status({"packid": str(valid_pack_id), "status": "done", "username": "admin"})
        end_time = time.time()
        assert(end_time-start_time < 0.1)

        # missing key test
        output = pack_instance.set_pack_status({"packid": str(99999), "username": "admin"})
        output = json.loads(output)["status"]
        actual_output = 0
        assert_equal(output,actual_output)

        # wrong input type test
        output = pack_instance.set_pack_status(str({"packid": str(99999), "username": "admin"}))
        output = json.loads(output)["status"]
        actual_output = 0
        assert_equal(output,actual_output)

    def test_delete_pack(self):

        # true input
        valid_pack_id = pack_utilities_old.get_max_pack_id()
        output = pack_instance.delete_pack({"packid": str(valid_pack_id), "username": "admin"})
        output = json.loads(output)["status"]
        actual_output = 1
        assert_equal(output, actual_output)

        output = pack_instance.get_pack_status({"packid": valid_pack_id})
        output = json.loads(output)["data"]
        actual_output = "deleted"
        assert_equal(output, actual_output)

        output = pack_instance.set_pack_status({"packid": str(valid_pack_id), "status": "pending", "username": "admin"})
        output = json.loads(output)["status"]
        actual_output = 1
        assert_equal(output, actual_output)

        # false input
        output = pack_instance.delete_pack({"packid": str(99999), "username": "admin"})
        output = json.loads(output)["status"]
        actual_output = 0
        assert_equal(output, actual_output)

    def test_get_pack_info(self):

        # time input
        start_time = time.time()
        valid_pack_id = pack_utilities_old.get_max_pack_id()
        output = pack_instance.get_pack_info({"packid": str(valid_pack_id)})
        end_time = time.time()
        assert(end_time-start_time < 1)

        slot_status = json.loads(output)["status"]
        actual_status = 1
        assert_equal(slot_status,actual_status)

        # false input
        output = pack_instance.get_pack_info({"packid": str(99999)})
        slot_status = json.loads(output)["status"]
        actual_status = 0
        assert_equal(slot_status,actual_status)

    def test_get_pack_list_done(self):

        # true input
        test_args1 = {"date_from":dosepack.utilities.utils.get_current_date(), "date_to":dosepack.utilities.utils.get_current_date(), "robot_id":6}

        output = pack_instance.get_pack_list_done(test_args1)
        output = json.loads(output)
        count = len(output["data"])
        actual_count = 0
        assert_equal(count,actual_count)

        valid_pack_id = pack_utilities_old.get_max_pack_id()
        pack_instance.set_pack_status({"packid": str(valid_pack_id), "status": "done", "username": "admin"})

        output = pack_instance.get_pack_list_done(test_args1)
        output = json.loads(output)
        count = len(output["data"])
        actual_count = 1
        assert_equal(count, actual_count)

        valid_pack_id = pack_utilities_old.get_max_pack_id()
        pack_instance.set_pack_status({"packid": str(valid_pack_id), "status": "pending", "username": "admin"})

        # false input
        test_args1 = {"date_from":dosepack.utilities.utils.get_current_date(), "date_to":dosepack.utilities.utils.get_current_date(), "robot_id":0}

        output = pack_instance.get_pack_list_done(test_args1)
        output = json.loads(output)
        output = output["status"]
        actual_output = 1
        assert_equal(output, actual_output)

    def test_add_verified_pack(self):

        # true input
        valid_pack_id = pack_utilities_old.get_max_pack_id()
        input_args_1 = {"packid": valid_pack_id, "image_path": "/", "note1": "", "note2": "",
        "note3": "", "note4": "", "note5": "", "pack_fill_status": 1, "username":"admin"}
        output = src.service.verification.add_verified_pack(input_args_1)
        output = json.loads(output)
        status = output["status"]
        actual_status = 1
        assert_equal(status, actual_status)

    def test_associate_rfid_with_packid(self):
        """
        @createdBy: Amisha Patel
        @createdDate: 04/25/2016
        @purpose - Tests assoiate_rfid_with_packid routine.
        """
        valid_pack_id = pack_utilities_old.get_max_pack_id()
        # true input
        test_args_valid =  {
             "rfid": "A123BC456",
             "packid": valid_pack_id,
             "username": "admin",
             "user_id": 1
         }

        output = pack_instance.associate_rfid_with_packid(test_args_valid)
        output = json.loads(output)["data"]["association"]
        expected_output = 1
        assert_equal(output, expected_output)

        # false input
        #####################################
        # case 1. Duplicate rfid
        # case 2. Empty rfid.
        # case 3. Invalid packid.
        #####################################

        # case 1. Duplicate rfid
        test_args2_invalid_case2 =  {
             "rfid": "A123BC456",
             "packid": (valid_pack_id - 1),
             "username": "admin",
             "user_id": 1
         }
        output = pack_instance.associate_rfid_with_packid(test_args2_invalid_case2)
        output = json.loads(output)["data"]["association"]
        expected_output = 0
        assert_equal(output, expected_output)

        # case 2. Empty rfid.
        test_args2_invalid_case2 =  {
             "rfid": "",
             "packid": valid_pack_id,
             "username": "admin",
             "user_id": 1
         }
        output = pack_instance.associate_rfid_with_packid(test_args2_invalid_case2)
        output = json.loads(output)["data"]["association"]
        expected_output = 0
        assert_equal(output, expected_output)

        # case 3. Invalid packid.
        test_args2_invalid_case3 =  {
             "rfid": "A123BC456",
             "packid": 10000000,
             "username": "admin",
             "user_id": 1
         }
        output = pack_instance.associate_rfid_with_packid(test_args2_invalid_case3)
        output = json.loads(output)["status"]
        expected_output = 0
        assert_equal(output, expected_output)

        # time test
        start_time = time.time()
        output = pack_instance.associate_rfid_with_packid(test_args_valid)
        end_time = time.time()
        assert(end_time-start_time < 0.1)

        # null input test
        output = pack_instance.associate_rfid_with_packid()
        output = json.loads(output)["status"]
        expected_output = 0
        assert_equal(output,expected_output)

    def test_get_required_quantity_by_batch_list(self):
        """
        @createdBy: Manish Agarwal
        @createdDate: 05/23/2016
        @purpose - Tests the analysis window
        """
















