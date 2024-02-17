import logging
from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_zone_master import ZoneMaster
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class DeviceLayoutDetails(BaseModel):
    """
    Class to store the inventory layout related details of various devices.
    """
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, null=True, unique=True, related_name='device_layout_device_id')
    zone_id = ForeignKeyField(ZoneMaster, null=True, related_name='device_zone_id')
    x_coordinate = DecimalField(decimal_places=2, null=True)
    y_coordinate = DecimalField(decimal_places=2, null=True)
    marked_for_transfer = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_layout_details"

    @classmethod
    def add_device_in_zone(cls, device_data):
        """
        Adds newly added device layout related data in the table.
        :param device_data:
        :return:
        """
        logger.debug("In add_device_in_zone")
        try:
            query = BaseModel.db_create_record(device_data, DeviceLayoutDetails, get_or_create=False)
            return query.id
        except (IntegrityError, InternalError, DataError) as e:
            raise e

    @classmethod
    def transfer_device_from_zone(cls, zone_id, device_id_list, transfer_to_zone):
        """
        Function to transfer a device from one zone to another. In the case when device is being transferred outside all
        of the zones or being transferred from outside the zones then that corresponding zone id will come as null.
        @param zone_id: Source zone_id
        @param device_id_list: Device layout ids to be transferred.
        @param transfer_to_zone: Destination zone id.
        @return:
        """
        try:
            for device_id in device_id_list:
                # StackedDevices.update_stacked_devices_after_device_transfer(device_layout_id=device_id)
                marked_for_transfer = True
                if transfer_to_zone is not None:
                    marked_for_transfer = False
                DeviceLayoutDetails.update(marked_for_transfer=marked_for_transfer, zone_id=transfer_to_zone).where(
                    DeviceLayoutDetails.id == device_id,
                    DeviceLayoutDetails.zone_id ==
                    zone_id).execute()
            return True


        except (IntegrityError, InternalError, DataError) as e:
            raise e

    @classmethod
    def remove_device_from_zone(cls, device_id_list):
        """
        To remove the device data from all the related tables.
        @param device_id_list:
        @return:
        """
        # todo: Have to delete the data from CSR Master, CSR Drawers and location master if any present and
        # if we had to delete the CSR data from CSR Master table.
        try:
            for device in device_id_list:
                # StackedDevices.delete_device_stacking_data(device_id=device)
                device_to_delete = DeviceLayoutDetails.select().where(DeviceLayoutDetails.id == device).get()
                device_to_delete.delete_instance()
            return True

        except (IntegrityError, InternalError, DataError) as e:
            raise e


    @classmethod
    def update_zone_configuration(cls, zone_id, device_list):
        """
        To update the x_coordinate and y_coordinate of devices present in the given zone.
        @param zone_id:
        @param device_list:
        @return:
        """
        logger.debug("In update_zone_configuration")
        try:
            for device in device_list:
                query = DeviceLayoutDetails.update(x_coordinate=device['x_coordinate'],
                                                   y_coordinate=device['y_coordinate']) \
                    .where(DeviceLayoutDetails.id == device['id']).execute()

            return True

        except (IntegrityError, InternalError, DataError) as e:
            raise e

    @classmethod
    def get_device_id_list_for_a_zone(cls, zone_id):

        """
        To get the list of device_layout_ids of a zone.
        @param zone_id:
        @return:
        """
        logger.debug("In get_device_id_list_for_a_zone")

        db_result = []
        try:
            query = DeviceLayoutDetails.select(DeviceLayoutDetails.id).dicts().where(
                DeviceLayoutDetails.zone_id == zone_id)

            for device in query:
                db_result.append(device['id'])
            return db_result
        except (IntegrityError, InternalError, DataError) as e:
            raise e
