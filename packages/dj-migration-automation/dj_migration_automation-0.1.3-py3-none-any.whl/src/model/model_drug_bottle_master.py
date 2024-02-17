from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import *
import settings
from src.model.model_drug_lot_master import DrugLotMaster

logger = settings.logger


class DrugBottleMaster(BaseModel):
    """
    Class to maintain inventory of all the bottles of the drugs registered
    """
    id = PrimaryKeyField()
    drug_lot_master_id = ForeignKeyField(DrugLotMaster, related_name="drug_lot_master_id")
    available_quantity = IntegerField()
    total_quantity = IntegerField()
    serial_number = CharField(null=True)
    rfid = CharField(max_length=12, null=True)
    data_matrix_type = SmallIntegerField()  # 0: Drug bottle, 1: Dose Packer
    label_printed = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    bottle_location = CharField(null=True)
    company_id = IntegerField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_bottle_master"

    @classmethod
    def db_insert_drug_bottle_data(cls, drug_bottle_data):
        """
        This method will be used to insert the data about a drug bottle into our database
        :param drug_bottle_data:
        :return:
        """
        try:
            query = BaseModel.db_create_record(drug_bottle_data, DrugBottleMaster, get_or_create=False)
            return query.id

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_drug_bottle_information(cls, drug_bottle_update_dict, drug_bottle_id):
        """
        This function will be used to update the information for drug bottle based on the id of the database
        @param drug_bottle_update_dict: Drug bottle information we need to update in key
        @param drug_bottle_id:
        :return:
        """
        try:
            status = DrugBottleMaster.update(**drug_bottle_update_dict).where(DrugBottleMaster.id == drug_bottle_id).execute()
            print("Status: ", status)
            return status

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_drug_bottle_quantity_by_bottle_id(cls, bottle_id, quantity_to_update, action=1):
        """
        :param bottle_id:
        :param quantity_to_update:
        :param action:
        :return:
        """
        try:
            query = DrugBottleMaster.select(DrugBottleMaster.id).where(DrugBottleMaster.id == bottle_id)

            if not query.exists():
                return False, 9006

            if action == 1:
                query = DrugBottleMaster.select(DrugBottleMaster.id).where((DrugBottleMaster.id == bottle_id) & (
                        (DrugBottleMaster.available_quantity - quantity_to_update) < 0))

                if query.exists():
                    return False, 9008

                status = DrugBottleMaster.update(
                    available_quantity=DrugBottleMaster.available_quantity - quantity_to_update).where(
                    DrugBottleMaster.id == bottle_id).execute()

            else:
                query = DrugBottleMaster.select(DrugBottleMaster.id).where((DrugBottleMaster.id == bottle_id) & (
                    (DrugBottleMaster.available_quantity + quantity_to_update) > DrugBottleMaster.total_quantity))

                if query.exists():
                    return False, 9007

                status = DrugBottleMaster.update(
                    available_quantity=DrugBottleMaster.available_quantity + quantity_to_update).where(
                    DrugBottleMaster.id == bottle_id).execute()

            return status, ""

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_drug_bottle_quantity_by_lot_id(cls, lot_id):
        """
        :param lot_id:
        :return:
        """
        try:
            bottle_quantity = DrugBottleMaster.get((DrugBottleMaster.drug_lot_master_id == lot_id)).total_quantity
            return bottle_quantity

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return -1

    @classmethod
    def db_get_drug_bottle_count_by_drug_and_company_id(cls, company_id, drug_lot_master_id_list):
        """
        @param company_id:
        @param drug_lot_master_id_list:
        :return:
        """
        try:
            bottle_count = DrugBottleMaster.select(DrugBottleMaster.id)\
                .where((DrugBottleMaster.company_id == company_id) & (DrugBottleMaster.drug_lot_master_id.in_(drug_lot_master_id_list)) &
                       (DrugBottleMaster.available_quantity > 0) & (DrugBottleMaster.is_deleted == False)).count()
            return bottle_count
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_recall_status_for_bottle_by_lot_id(cls, lot_id):
        """
        :param lot_id:
        :return:
        """
        try:
            status = DrugBottleMaster.update(is_deleted=True).where((DrugBottleMaster.drug_lot_master_id == lot_id) &
                                                                    (DrugBottleMaster.available_quantity > 0)).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def check_if_lot_has_unprinted_bottle_label(cls, lot_id):
        """
        This function will check if given lot id has bottles which have unprinted data matrix
        :param lot_id: Lot id for which we need to find the data
        :return: Count of bottles
        """
        try:
            bottle_count = DrugBottleMaster.select(DrugBottleMaster.id).where(
                (DrugBottleMaster.drug_lot_master_id == lot_id) & (DrugBottleMaster.data_matrix_type == 1) & (
                            DrugBottleMaster.label_printed == False)).count()
            return bottle_count
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_bottle_id_for_unprinted_label_by_lot_id(cls, lot_id):
        """
        This function will be used to get list of id of bottles whose label is not printed for the given lot id
        :param lot_id: Lot id for which we need find the data
        :return: List of bottle ids
        """
        db_result: list = list()
        try:
            query = DrugBottleMaster.select(DrugBottleMaster.id).dicts().where((DrugBottleMaster.drug_lot_master_id == lot_id) & (DrugBottleMaster.data_matrix_type == 1) & (
                                DrugBottleMaster.label_printed == False))
            for record in query:
                db_result.append(record["id"])
            return db_result

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def delete_drug_bottle(cls, bottle_id_list):
        """
        This function will be used to delete drug bottle because it is of no use
        :param bottle_id_list: Bottle ID which we need to delete
        :return: True/False
        """
        try:
            status = DrugBottleMaster.update(is_deleted=True).where(DrugBottleMaster.id.in_(bottle_id_list)).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_bottle_print_status(cls, bottle_id_list):
        """
        @param bottle_id_list:
        :return:
        """
        try:
            status = DrugBottleMaster.update(label_printed=True).where(DrugBottleMaster.id.in_(bottle_id_list)).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def check_if_serial_number_exists(cls, serial_number):
        """
        :param serial_number:
        :return:
        """
        try:
            existence = DrugBottleMaster.select(DrugBottleMaster.id).where(
                DrugBottleMaster.serial_number == serial_number).exists()
            return existence

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
