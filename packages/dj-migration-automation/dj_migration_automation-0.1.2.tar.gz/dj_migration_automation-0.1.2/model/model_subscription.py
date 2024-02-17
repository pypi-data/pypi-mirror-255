"""
    @file: model/model_subscription.py
    @createdBy: Dushyant Parmar
    @createdDate: 03/09/2018
    @lastModifiedBy: Dushyant Parmar
    @lastModifiedDate: 03/09/2018
    @type: file
    @desc: model classes for database tables
"""


from multiprocessing import Lock
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import convert_date_from_sql_to_display_date, get_current_date_time, get_current_date
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateField, CharField, BooleanField, DateTimeField,\
    SmallIntegerField, InternalError, IntegrityError, DoesNotExist, JOIN_LEFT_OUTER, DataError, fn
from src.model.model_code_master import CodeMaster

import settings

logger = settings.logger
lock = Lock()

