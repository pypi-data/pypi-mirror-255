__author__ = 'amishap'
"""
    @createdBy: Amisha Patel
    @createdDate: 10/17/2016
    @desc: test file for manual station APIs.
"""

from nose.tools import *
import json
from src.manual_station import *
from dosepack.base_model.base_model import db
db.init("dosepack_new", user="root".encode("utf-8"), password="root".encode("utf-8"))

class TestManualStation(object):
    SUCCESS = "success"
    FAILURE = "failure"
    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""
        """ Clear all the data from the tables"""
        pass

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class after any tests are run"""
        pass

    def test_fetch_manual_details(self):
        # required fields not passed.
        arg = {
            "id": "rfid1",
        }
        output = fetch_manual_details(arg)
        actual_output = json.loads(output)["status"]
        expected_output = self.FAILURE
        assert_equal(expected_output, actual_output)

        # type is incorrect.
        arg = {
            "id": "rfid1",
            "type": "Y"
        }
        output = fetch_manual_details(arg)
        actual_output = json.loads(output)["status"]
        expected_output = self.FAILURE
        assert_equal(expected_output, actual_output)

        # non existing rfid.
        arg = {
            "id": "arbitraryrfid",
            "type": "R"
        }
        output = fetch_manual_details(arg)
        actual_output = json.loads(output)["data"]
        expected_output = {} # when there is no rfid it should send empty object
        assert_equal(expected_output, actual_output)

        # non existing pack id.
        arg = {
            "id": 2222,
            "type": "P"
        }
        output = fetch_manual_details(arg)
        actual_output = json.loads(output)["status"]
        expected_output = self.FAILURE # when there is no rfid it should send empty object
        assert_equal(expected_output, actual_output)

        # valid data
        arg = {
            "id": "12345",
            "type": "R"
        }
        output = fetch_manual_details(arg)
        actual_output = json.loads(output)["status"]
        expected_output = self.SUCCESS
        assert_equal(expected_output, actual_output)

        #todo implement once decorator is completed by Backend team.
        arg = {
            "id": 3,
            "type": "P"
        }
        output = fetch_manual_details(arg)
        actual_output = json.loads(output)["status"]
        expected_output = self.SUCCESS
        assert_equal(expected_output, actual_output)
