"""
    @file: tests/run_canister_tests.py
    @createdBy: Manish Agarwal
    @createdDate: 4/7/2016
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 4/7/2016
    @type: file
    @desc: test file for canister apis
"""

from nose.tools import *
import json


from dosepack.base_model.base_model import db
db.init("autobot", user="root", password="root")


class TestPack(object):

    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""
        """ Clear all the data from the tables"""
        try:
            pass
        except Exception as ex:
            print(ex)
            raise Exception("Setup Failed")

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class after any tests are run"""
        pass

    def test_add_canister(self):
        assert_equal(1, 1)













