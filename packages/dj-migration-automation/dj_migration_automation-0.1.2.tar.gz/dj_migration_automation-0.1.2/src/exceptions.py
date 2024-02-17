# -*- coding: utf-8 -*-
"""
    src.exceptions
    ~~~~~~~~~~~~~~~~
    This module defines all the self declared exceptions.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""


class PreconditionFailedException(Exception):
    """Base class for precondition failed Exception"""
    pass


class FileParsingException(Exception):
    """Base class for other exceptions"""
    pass


class AutoProcessTemplateException(Exception):
    """Base class for AutoProcess Template exceptions"""
    pass


class PackGenerationException(Exception):
    """Base class for other exceptions"""
    pass


class ThreadException(Exception):
    """Base class for other exceptions"""
    pass


class PharmacyFillIDException(Exception):
    """Base class for other exceptions"""
    pass


class PharmacySoftwareCommunicationException(Exception):
    """Base class for other exceptions"""
    pass


class PharmacySoftwareResponseException(Exception):
    """Base class for other exceptions"""
    pass


class PharmacySlotFileGenerationException(Exception):
    """Base class for other exceptions"""
    pass


class PharmacyRxFileGenerationException(Exception):
    """Base class for other exceptions"""
    pass


class CanisterQuantityAdjustmentException(Exception):
    """Base class for other exceptions"""
    pass


class DBUpdateFailedException(Exception):
    """Base class for database update failed exceptions"""
    pass


class RealTimeDBException(Exception):
    """Base class for real time database update failed exceptions"""
    pass


class DrugFetchFailedException(Exception):
    """Base class for drug data fetch failed exceptions"""
    pass


class DuplicateFileException(Exception):
    """ Exception Class for Duplicate File Error """
    pass


class AlternateDrugUpdateException(Exception): pass


class UnsplittableTemplateException(Exception):
    """ Exception class for template that can't be split """

    def __init__(self, msg, taper_error=False):
        super().__init__(msg)
        self.message = msg
        self.taper_error = taper_error

    def __str__(self):
        return "UnsplittableTemplateException(taper_error={}, message={})" \
            .format(self.taper_error, self.message)


class CarError(Exception):
    """Basic exception for errors raised by cars"""

    def __init__(self, car, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An error occurred with car %s" % car
        super(CarError, self).__init__(msg)
        self.car = car


class CarCrashError(CarError):
    """When you drive too fast"""

    def __init__(self, car, other_car, speed):
        super(CarCrashError, self).__init__(
            car, msg="Car crashed into %s at speed %d" % (other_car, speed))
        self.speed = speed
        self.other_car = other_car


class InvalidTechnicianID(Exception):
    """Invalid technician ID"""
    pass


class DuplicateSerialNumber(Exception):
    """duplicate serial number"""
    pass


class ArgumentMissingException(Exception):
    """Argument missing in url"""
    pass


class DuplicateCanisterParameterRuleException(Exception):
    """ Exception for duplicate entry in canister parameter rule """
    pass


class NoLocationExists(Exception):
    """Invalid device_id and location_number"""
    pass


class NoDeviceExists(Exception):
    """Exception having no device for given system id"""
    pass


class CanisterStickException(Exception):
    """added as superclass for canister stick exceptions"""
    """
        This exception is added to handle canister stick exception while adding canister data. 
        By adding this we can manage transaction easily and use the existing method.
    """

    def __init__(self, error_code):
        super().__init__()
        self.error_code = error_code


class TemplateAlreadyProcessed(Exception):
    """Template processed before rollback of file event"""
    pass


class RedisConnectionException(Exception):
    """Redis connection error"""
    pass


class RedisKeyException(Exception):
    """Specified key not available in Redis """
    pass


class TemplateException(Exception):
    """"""
    pass


class InventoryBadRequestException(Exception):
    """
        When Inventory API call fails due bad request
    """
    pass


class InventoryDataNotFoundException(Exception):
    """
        When data not found in Inventory API call
    """
    pass


class InventoryConnectionException(Exception):
    """
        Unable to connect to inventory-db
    """
    pass


class InventoryBadStatusCode(Exception):
    """
        When found unexpected status code from Inventory
    """
    pass


class InvalidResponseFromInventory(Exception):
    """
        When found unexpected response from Inventory
    """
    pass


class CanisterNotExist(Exception):
    """ Canister not exist in canister master"""
    pass


class CanisterNotPresent(Exception):
    """ Canister not present at given location"""
    pass


class RemoveASRSPacksException(Exception):
    """ Exception raise while removing canister from ASRS"""
    pass


class APIFailureException(Exception):
    """ Exception raise when any internal api call fails"""
    pass


class DataDoesNotExistException(Exception):
    """Exception when there is no data for the given criteria"""
    pass


class TokenMissingException(Exception):
    """Exception when the token is missing in the request headers"""
    pass


class InvalidUserTokenException(Exception):
    """Exception when the token mapping with user is missing"""
    pass


class DrugInventoryValidationException(Exception):
    """Exception class for any sort of Drug Inventory Validation Error or Exception"""
    pass


class DrugInventoryInternalException(Exception):
    """Exception class for any sort of Drug Inventory Internal Error or Exception"""
    pass


class TokenFetchException(Exception):
    """Exception class in case when there is an issue fetching the token"""
    pass


class MissingParameterException(Exception):
    """Exception class in case when there is a missing parameter"""
    pass


class InvalidUserTokenException(Exception):
    """Exception when the no user is found for the received token in the request headers"""
    pass


class OtherDrugParsingException(Exception):

    pass