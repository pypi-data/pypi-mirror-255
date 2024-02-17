#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    @file: label_config.py
    @createdBy: Manish Agarwal
    @createdDate: 06/14/2016
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 06/14/2016
    @type: file
    @desc: Contains global constants for label printing
"""
import os

# value for default, null and absent
DEFAULT = 1
NULL = 0
ABSENT = -1
SUCCESS = 1
FAILURE = 0
INVALID = 3
QUEUED = 'queued'

# number of rows in pack
PACK_ROW = 7
# number of cols in pack
PACK_COL = 4

ROBOT6PRINTER = "SC-P800 Series(Network)"
# ROBOT4PRINTER = "EPSONFCB628 (SC-P800 Series)"

DEFAULT_ROBOT_ID = 6

DOSEPACK_ROBOT = 6
MTS_ROBOT = 4

UNIT_TEST_DATABASE = None


IPS_CONN_SCHEME = bool(int(os.environ.get("IPS_ON_SSL", "1")))
if IPS_CONN_SCHEME:
    IPS_CONN_SCHEME = 'https://'
else:
    IPS_CONN_SCHEME = 'http://'

# Base url for auth server
BASE_URL_AUTH = os.environ.get("BASE_URL_AUTH", "d-auth.dosepack.com")

MEDITAB_ID = "0050023"


PATIENT_PIC_WEBSERVICE = "/robotv1/getpatientpicture"
DEFAULT_PDF_DIRECTORY = os.path.join(os.getcwd(), 'pack_labels', 'generated')
DRUG_PATH = 'drug_images'
BUCKET_DRUG_IMAGE_PATH = 'drug_images'
# COUCH DB REALTED CONSTANTS
CONST_PRINT_JOB_DOC_ID = 'printjobs'
CONST_PRINT_JOB_DOC_TYPE = 'printjobs-v1'

PRINTJOB_DOCUMENT_OBJ = None
PRINTJOB_DOC = None  # stores the document retrieved from couch_db
PRINT_JOB_QUEUE = list()

# CERTIFICATE RELATED CONSTANTS
CUSTOM_CA_BUNDLE_PATH = os.path.join("ca_bundle")
CUSTOM_CA_BUNDLE_FILE = "gd_bundle-g2-g1.crt"

DRUG_IMAGE_MODIFICATION_ALLOWED = 168  # in hours



