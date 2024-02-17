import re
from typing import Optional, Dict, Any

import numpy as np
from pandas_schema import Schema, Column
from pandas_schema.validation import CanConvertValidation, CustomSeriesValidation, MatchesPatternValidation, \
    DateFormatValidation, InListValidation, InRangeValidation
from peewee import InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from src.dao.file_dao import get_file_validation_error_dao

from src.model.model_file_validation_error import FileValidationError


logger = settings.logger

ndc_pattern = re.compile('^(\d{11})$')   # matches 11 digits

# Matches pattern quantity(1,3, .5, 1.5) multiplied by 100 i.e 100,300,50,150
individual_quantity = re.compile('^((\d{1})*00|0|(\d{1})*50)$')


quantity_validations = [
    InRangeValidation(0, 10000)  # will be divided by 100. Allowing Max. Qty 100
]

date_format = '%Y%m%d'
time_format = '%H%M'

date_validation_message = "Does not contain YYYYMMDD format"
null_validation_message = "Cannot be empty"
time_validation_message = "Does not contain HHMM format"
quantity_validation_message = "Incorrect format"
numeric_validation_message = "Should be numeric"


def daw_range_validation(y):
    """
    Checks if the value is in range 0 to 9, both inclusive
    :param y: pandas series
    :return:
    """
    def validate(val):
        try:
            if 0 <= int(val) < 10:
                return True
            else:
                return False
        except (TypeError, ValueError) as e:
            logger.error(e, exc_info=True)
            return False
    return y.apply(validate)


def null_validation(y):
    """
    Checks weather the column contains null or not
    :param y: pandas series
    :return:
    """
    def validate(val):
        try:
            if isinstance(val, (int, float)):
                if val > 0:
                    return True
                else:
                    return False
            else:
                if len(val) > 0:
                    return True
                else:
                    return False
        except Exception as e:
            logger.error(e, exc_info=True)
            return False
    return y.apply(validate)


def remaining_refill_null_validation(y):
    """
    Checks weather the column contains null or not
    :param y: pandas series
    :return:
    """
    def validate(val):
        try:
            if isinstance(val, (int, float)):
                if val >= 0:
                    return True
                else:
                    return False
            else:
                if len(val) > 0:
                    return True
                else:
                    return False
        except Exception as e:
            logger.error(e, exc_info=True)
            return False
    return y.apply(validate)


schema = Schema([
    Column('pharmacy_facility_id', [
        CanConvertValidation(int, message=numeric_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('pharmacy_patient_id', [
        CustomSeriesValidation(null_validation, null_validation_message),
        CanConvertValidation(int, message=numeric_validation_message)
    ]),
    Column('pharmacy_doctor_id', [
        CanConvertValidation(int, message=numeric_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('facility_name', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('patient_name', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('doctor_name', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('patient_picture', [
        CanConvertValidation(str, allow_null=True)
    ]),
    Column('address1', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('city', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('state', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('zip_code', [
        MatchesPatternValidation('^\d{5}(?:\d{4})?$', message='Does not match with 5 or 9 digit format'),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),  # matches either 5 digits or 9 digits
    Column('workphone', [
        MatchesPatternValidation('^(\w{10})$', message='Does not contain 10 digits'),
    ], allow_empty=True),  # matches exactly 10 digits or empty string
    Column('dob', [
        DateFormatValidation(date_format, message=date_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),   # matches date pattern YYYYMMDD or empty srring
    Column('patient_allergy', [
        CanConvertValidation(str),
        # CustomSeriesValidation(null_validation, null_validation_message)  # empty string found in production
    ]),
    Column('doctor_phone', [
        MatchesPatternValidation('^(\d{10})$', message='Does not contain 10 digits')
    ], allow_empty=True),  # matches exactly 10 digits or empty string
    Column('pharmacy_drug_id', allow_empty=False),
    Column('pharmacy_rx_no', [CustomSeriesValidation(null_validation, null_validation_message)]),
    Column('fill_note', allow_empty=True),
    Column('to_fill', allow_empty=True),
    Column('actual_qty', allow_empty=True),
    Column('quantity', [
        MatchesPatternValidation('^((\d{1})*000|(\d{1})*500)$', message=quantity_validation_message)
    ]),  # Matches pattern quantity(1,3, .5, 1.5) multiplied by 1000 i.e 1000,3000,500,1500
    Column('hoa_date', [
        DateFormatValidation(date_format,  message=date_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),  # matches date pattern YYYYMMDD
    Column('hoa_time', [
        DateFormatValidation(time_format,  message=time_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),  # matches pattern HHMM
    Column('sig', [CanConvertValidation(str)]),
    Column('morning', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
    Column('noon', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
    Column('evening', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
    Column('bed', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
    Column('caution1', [CanConvertValidation(str)], allow_empty=True),
    Column('caution2', [CanConvertValidation(str)], allow_empty=True),
    Column('remaining_refill', [CanConvertValidation(float, message=numeric_validation_message),
                                CustomSeriesValidation(remaining_refill_null_validation, null_validation_message)]),
    Column('is_tapered', [
        InListValidation(['N', 'Y'], message="Should only contain 'Y' or 'N'"),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),  # to represent yes or no select y or n
    Column('pharmacy_fill_id', [CustomSeriesValidation(null_validation, null_validation_message)]),
    Column('delivery_schedule', [
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('filled_by', allow_empty=True),
    Column('fill_start_date', [
        DateFormatValidation(date_format,  message=date_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),  # matches date pattern YYYYMMDD
    Column('fill_end_date', [
        DateFormatValidation(date_format,  message=date_validation_message),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),  # matches date pattern YYYYMMDD
    Column('drug_name', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('ndc', [
        MatchesPatternValidation(ndc_pattern, message='Does not match the required 11 digit format'),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('patient_no', [
        CanConvertValidation(str),
        CustomSeriesValidation(null_validation, null_validation_message)
    ]),
    Column('daw_code', [
        CanConvertValidation(int, message=numeric_validation_message),
        CustomSeriesValidation(daw_range_validation, 'Should be in range 0 to 9')
        #InRangeValidation throws exception for string so CustomSeriesValidation used
    ]),  # value in range 0 to 9
    Column('delivery_date', [
        DateFormatValidation(date_format,  message=date_validation_message),
    ], allow_empty=True),  # matches date pattern YYYYMMDD
    Column('delivery_time', [
        DateFormatValidation(time_format,  message=time_validation_message),
    ], allow_empty=True)   # matches pattern HHMM
])


@log_args_and_response
def file_validation(df, file_id, change_rx: Optional[bool] = False):
    """
    Validates file against the given format
    :param df: data frame of file
    :param file_id: file_id
    :param change_rx
    :return:
    """
    error_set = set()
    error_list = list()
    validation_data: Dict[int, Any]
    with db.transaction():
        df_obj = df.select_dtypes('object')
        df[df_obj.columns] = df_obj.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.replace(np.nan, '', regex=True)

        count = 0
        error_details = dict()

        if change_rx:
            change_rx_schema = Schema([
                Column('pharmacy_patient_id', [
                    CustomSeriesValidation(null_validation, null_validation_message),
                    CanConvertValidation(int, message=numeric_validation_message)
                ]),
                Column('pharmacy_doctor_id', [
                    CanConvertValidation(int, message=numeric_validation_message),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('patient_name', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('doctor_name', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('doctor_phone', [
                    MatchesPatternValidation('^(\d{10})$', message='Does not contain 10 digits')
                ], allow_empty=True),  # matches exactly 10 digits or empty string
                Column('pharmacy_drug_id', allow_empty=False),
                Column('fill_note', allow_empty=True),
                Column('to_fill', allow_empty=True),
                Column('actual_qty', allow_empty=True),
                Column('pharmacy_rx_no', [CustomSeriesValidation(null_validation, null_validation_message)]),
                Column('quantity', [
                    MatchesPatternValidation('^((\d{1})*000|(\d{1})*500)$', message=quantity_validation_message)
                ]),  # Matches pattern quantity(1,3, .5, 1.5) multiplied by 1000 i.e 1000,3000,500,1500
                Column('hoa_date', [
                    DateFormatValidation(date_format, message=date_validation_message),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),  # matches date pattern YYYYMMDD
                Column('hoa_time', [
                    DateFormatValidation(time_format, message=time_validation_message),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),  # matches pattern HHMM
                Column('sig', [CanConvertValidation(str)]),
                Column('morning', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
                Column('noon', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
                Column('evening', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
                Column('bed', [MatchesPatternValidation(individual_quantity, message=quantity_validation_message)]),
                Column('caution1', [CanConvertValidation(str)], allow_empty=True),
                Column('caution2', [CanConvertValidation(str)], allow_empty=True),
                Column('remaining_refill', [CanConvertValidation(float, message=numeric_validation_message),
                                            CustomSeriesValidation(remaining_refill_null_validation,
                                                                   null_validation_message)]),
                Column('is_tapered', [
                    InListValidation(['N', 'Y'], message="Should only contain 'Y' or 'N'"),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('pharmacy_fill_id', [CustomSeriesValidation(null_validation, null_validation_message)]),
                Column('delivery_schedule', [
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('filled_by', allow_empty=True),
                Column('fill_start_date', [
                    DateFormatValidation(date_format, message=date_validation_message),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),  # matches date pattern YYYYMMDD
                Column('fill_end_date', [
                    DateFormatValidation(date_format, message=date_validation_message),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),  # matches date pattern YYYYMMDD
                Column('drug_name', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('ndc', [
                    MatchesPatternValidation(ndc_pattern, message='Does not match the required 11 digit format'),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('patient_no', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('daw_code', [
                    CanConvertValidation(int, message=numeric_validation_message),
                    CustomSeriesValidation(daw_range_validation, 'Should be in range 0 to 9')
                    # InRangeValidation throws exception for string so CustomSeriesValidation used
                ]),  # value in range 0 to 9
                Column('delivery_date', [
                    DateFormatValidation(date_format, message=date_validation_message),
                ], allow_empty=True),  # matches date pattern YYYYMMDD
                Column('delivery_time', [
                    DateFormatValidation(time_format, message=time_validation_message),
                ], allow_empty=True),  # matches pattern HHMM
                Column('status', [
                    CanConvertValidation(int, message=numeric_validation_message),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('rx_change_comment', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('rx_change_datetime', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('rx_change_user_name', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('pack_type', [
                    CanConvertValidation(str),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('seperate_pack_per_dose', [
                    InListValidation(['N', 'Y'], message="Should only contain 'Y' or 'N'"),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('true_unit', [
                    InListValidation(['N', 'Y'], message="Should only contain 'Y' or 'N'"),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ]),
                Column('customization', [
                    InListValidation(['N', 'Y'], message="Should only contain 'Y' or 'N'"),
                    CustomSeriesValidation(null_validation, null_validation_message)
                ])
            ])

        #TODO  commented temporary, until IPS adds mandatory keys
        # if change_rx:
        #     errors = change_rx_schema.validate(df)
        # else:
        #     errors = schema.validate(df)
        errors = list()
        for error_detail in errors:

            count += 1
            column = error_detail.column
            value = str(error_detail.value)
            message = error_detail.message
            patient_name = df.loc[error_detail.row, 'patient_name']
            patient_no = str(df.loc[error_detail.row, 'patient_no'])

            tuple_data = (file_id, patient_no, column, value, message,)
            if tuple_data not in error_set:
                error_set.add(tuple_data)

                if not change_rx:
                    error_list.append((file_id, patient_name, patient_no, column, value, message,))
                else:
                    clauses = list()

                    clauses.append(clauses.append(FileValidationError.file_id == file_id))
                    clauses.append(clauses.append(FileValidationError.patient_name == patient_name))
                    clauses.append(clauses.append(FileValidationError.patient_no == patient_no))
                    clauses.append(clauses.append(FileValidationError.column == column))
                    clauses.append(clauses.append(FileValidationError.message == message))
                    validation_data = FileValidationError.db_get_file_validation(clauses)
                    if validation_data:
                        continue
                    else:
                        error_list.append((file_id, patient_name, patient_no, column, value, message,))
                error_details.setdefault(patient_name, set())
                formatted_message = column + " : " + value + " " + message
                error_details[patient_name].add(formatted_message)

        if error_list:
            fields = [name for name in FileValidationError._meta.sorted_field_names if name != 'id']
            rows = [dict(zip(fields, record)) for record in error_list]
            try:
                FileValidationError.insert_many(rows).execute()
                logger.info("file validation error_detail" + str(error_details))
                return error_details
            except (InternalError, IntegrityError) as e:
                logger.error(e, exc_info=True)
                return error(2001)


@log_args_and_response
def get_file_validation_error(file_id):
    """
    returns error occurred during file processing
    :param file_id: id of file
    :return:
    """
    file_validation_error_list = list()
    try:
        # query = FileValidationError.select(FileValidationError.file_id,
        #                                    FileValidationError.patient_name,
        #                                    FileValidationError.patient_no,
        #                                    FileValidationError.column,
        #                                    FileValidationError.value,
        #                                    fn.trim(fn.GROUP_CONCAT(' ', FileValidationError.message))
        #                                    .alias('message')).dicts()\
        #     .group_by(FileValidationError.file_id,
        #               FileValidationError.patient_no,
        #               FileValidationError.column,
        #               FileValidationError.value).where(FileValidationError.file_id == file_id)
        # for record in query:
        #     file_validation_error_list.append(record)
        file_validation_error_list = get_file_validation_error_dao(file_id=file_id)
        return create_response(file_validation_error_list)
    except InternalError:
        return error(2001)
