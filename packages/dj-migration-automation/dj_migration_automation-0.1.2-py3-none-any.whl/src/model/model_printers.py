from peewee import PrimaryKeyField, CharField, ForeignKeyField, IntegerField, DateField, TimeField, DoesNotExist
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date, get_current_time
from src.model.model_code_master import CodeMaster


class Printers(BaseModel):
    """
        @class:
        @createdBy: Jitendra Saxena
        @createdDate: 01/08/2018
        @lastModifiedBy:
        @lastModifiedDate:
        @type: file
        @desc: stores the printers associated with a given system.
    """
    id = PrimaryKeyField()
    printer_name = CharField(max_length=50)
    printer_type_id = ForeignKeyField(CodeMaster)
    unique_code = CharField(max_length=55, unique=True)
    ip_address = CharField()
    system_id = IntegerField()
    added_date = DateField(default=get_current_date)
    added_time = TimeField(default=get_current_time)
    print_count = IntegerField(default=0)

    @classmethod
    def get_associated_printers(cls, system_id):
        printers = list()
        for record in Printers.select(
                Printers.id,
                Printers.printer_name,
                Printers.ip_address,
                Printers.unique_code
        ).dicts().where(Printers.system_id == system_id):
            printers.append(record)

        return printers

    @classmethod
    def check_ip_exists_for_given_system(cls, ip_address, system_id):
        try:
            # check if ip exists
            ip_exists = Printers.get(ip_address=ip_address, system_id=system_id)
            return True
        except DoesNotExist as ex:
            return False

    @classmethod
    def check_unique_code_exists(cls, unique_code):
        try:
            # check if unique_code exists
            printer = Printers.get(unique_code=unique_code)
        except DoesNotExist as ex:
            return None
        return printer
