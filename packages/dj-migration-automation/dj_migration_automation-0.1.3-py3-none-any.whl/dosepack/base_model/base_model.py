"""
    @file: model/base_model.py
    @createdBy: Manish Agarwal
    @createdDate: 4/22/2016
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 4/22/2016
    @type: file
    @desc: model class for database tables
"""

import functools
import logging
import operator
import os

from peewee import Model, MySQLDatabase, InternalError, IntegrityError, DataError, DoesNotExist
from playhouse.pool import PooledMySQLDatabase

# initialize the database connection
pool_connections = int(os.environ.get('USE_CONNECTION_POOL', 0))
if pool_connections:
    db = PooledMySQLDatabase(
        None,
        max_connections=int(os.environ.get('MAX_POOL_CONNECTIONS', 132)),
        stale_timeout=int(os.environ.get('POOL_CONNECTION_STALE_TIMEOUT', 10800))
    )
    # invalidate connection after 3 hours of first activity
    # It does not invalidate when connection is being used.
else:

    db = MySQLDatabase(None)

# get the logger for the pack from global configuration file logging.json
logger = logging.getLogger("root")


def between_expression(field, from_val, to_val):
    """builds peewee expression using between"""
    return field.between(from_val, to_val)


# parent class for all model tables
class BaseModel(Model):
    class Meta:
        database = db

    @staticmethod
    def db_create_record(data, table_name, add_fields=None, remove_fields=None, fn_transform=None,
                         fn_validate=None, default_data_dict=None, get_or_create=True):

        """ Takes a file and creates a data frame from it form the input arguments

                Args:
                    data (dict): The record dict to be inserted in table.
                    table_name (Model): The model instance of the table in which the record is to be inserted
                    add_fields (optional argument) (dict): The additional data to be added to record dict.
                    remove_fields (optional argument) (dict): The data to be removed from record dict.
                    fn_transform (optional argument) (dict): The transformation rules if any for the record.
                    fn_validate (optional argument) (dict): The validation rules if any for the record dict.
                    default_data_dict (optional argument) (boolean): The default data to be added along the record.
                    get_or_create (optional argument) (boolean): If set to True gets the record if already exists
                    otherwise creates it. If set to False creates a new record.

                Returns:
                    Model.tuple : The tuple has two records. First record is the id of the record inserted. Second
                                  record is boolean indicating whether the record is already present or it
                                  is inserted now. True indicates the record is inserted now.

                Raises:
                    IntegrityError: If the record with the provided primary key already exists
                    InternalError: If the record to be inserted does not have have valid fields.

                Examples:
                    >>> create_record([], [])
                    [0, 1, 2, 3]

        """
        # If default data dict is True update the insert record dict with default data dict.
        if default_data_dict:
            data.update(default_data_dict)

        # List of fields to be removed from data dictionary
        if remove_fields:
            for item in remove_fields:
                data.pop(item, 0)

        # List of additional fields to be added to data dictionary
        if add_fields:
            data.update(add_fields)

        # Transformation rule or function to be applied to data dictionary
        if fn_transform:
            fn_transform(data)

        # Validation rule to be applied to data dictionary
        if fn_validate:
            fn_validate(data)

        try:
            if get_or_create:
                record = table_name.get_or_create(**data)
            else:
                record = table_name.create(**data)
        except DataError as e:
            raise
        except IntegrityError as e:
            raise
        except InternalError as e:
            raise
        return record

    @staticmethod
    def db_create_multi_record(data, table_name):

        """ Takes a data and creates multiple records for it in db.

                Args:
                    data (list): The record dict to be inserted in table.
                    table_name (Model): The model instance of the table in which the record is to be inserted

                Returns:
                    Model.tuple : The tuple has two records. First record is the id of the record inserted. Second
                                  record is boolean indicating whether the record is already present or it
                                  is inserted now. True indicates the record is inserted now.

                Raises:
                    IntegrityError: If the record with the provided primary key already exists
                    InternalError: If the record to be inserted does not have have valid fields.

                Examples:
                    >>> db_create_multi_record([], [])
                    [0, 1, 2, 3]

        """

        try:
            with db.atomic():
                record = table_name.insert_many(data).execute()
        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)
        return record

    @classmethod
    def db_update_or_create(cls, create_dict, update_dict):
        """
        If record exists then updates it or creates new record
        :param create_dict: dict: default data for creating record
        :param update_dict: dict containing data to be updated
        :return: record
        """
        try:
            record, created = cls.get_or_create(defaults=update_dict, **create_dict)
            if not created:
                created_by = update_dict.pop("created_by", None)
                created_date = update_dict.pop("created_date", None)
                update_record = cls.update(**update_dict).where(cls.id == record.id).execute()
            return record
        except InternalError as e:
            raise InternalError(e)

    @classmethod
    def db_update(cls, update_dict, **kwargs):
        """
        Method to update data in model
        @param update_dict: dict to be updated
        @param kwargs: key, value pairs needed for where condition
        @return: query status
        """
        try:
            clauses = list()
            for field, value in kwargs.items():
                clauses.append((getattr(cls, field) == value))
            if clauses:
                query = cls.update(**update_dict).where(functools.reduce(operator.and_, clauses)).execute()
                return query
            else:
                raise ValueError("There must be atleast one value in kwargs")
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise
        except ValueError as e:
            logger.error(e)
            raise

    @classmethod
    def db_get_data(cls, **kwargs):
        """
        Method to get records
        @param kwargs: key, value pairs needed for where condition
        @return: query status
        """
        try:
            clauses = list()
            for field, value in kwargs.items():
                clauses.append((getattr(cls, field) == value))
            query = cls.select().dicts()
            if clauses:
                query = query.where(functools.reduce(operator.and_, clauses))
            return list(query)
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise
        except DoesNotExist as e:
            logger.error(e)
            raise
