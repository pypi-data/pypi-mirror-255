from dosepack.base_model.base_model import db
from model.model_pack import BatchMaster, PackRxLink, PackHeader, PackVerification,\
    SlotDetails, SlotHeader, SlotTransaction, TempSlotInfo, PatientRx, PackStatusTracker, SlotHeaderTransaction
from src.model.model_pack_details import PackDetails
from src.model.model_doctor_master import DoctorMaster
from src.model.model_note_master import NoteMaster
from src.model.model_pack_header import PackHeader
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_verification import PackVerification
from src.model.model_patient_master import PatientMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_pharmacy_master import PharmacyMaster
from model.model_drug import NdcBlacklist, NdcBlacklistAudit
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_drug_sync_log import DrugSyncLog
from src.model.model_drug_sync_history import DrugSyncHistory
from src.model.model_drug_master import DrugMaster
from model.model_canister import CanisterDrawerMaster, CanisterMaster
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_history import CanisterHistory
from model.model_misc import FileDownloadTracker, SystemSetting
from src.model.model_print_queue import PrintQueue
from src.model.model_printers import Printers
from model.model_template import TemplateMaster, TemplateDetails
from src.model.model_file_header import FileHeader
from src.model.model_slot_header import SlotHeader
from src.model.model_batch_master import BatchMaster
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from model.model_device_manager import RobotMaster
from src.model.model_vision_drug_count import VisionCountPrediction
from src.model.model_vision_drug_prediction import VisionDrugPrediction
from dosepack.base_model.base_model import db
from src.model.model_consumable_tracker import ConsumableTracker
from src.model.model_consumable_type_master import ConsumableTypeMaster
from src.model.model_consumable_used import ConsumableUsed
from src.model.model_courier_master import CourierMaster
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from src.model.model_order_details import OrderDetails
from src.model.model_order_document import OrderDocument
from src.model.model_order_status_tracker import OrderStatusTracker
from src.model.model_orders import Orders
from src.model.model_shipment_tracker import ShipmentTracker
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_temp_slot_info import TempSlotInfo


def create_tables(database):
    db.init(database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    with db.transaction():
        db.create_tables([PharmacyMaster, GroupMaster, CodeMaster])
        db.create_tables([FacilityMaster, PatientMaster, DoctorMaster])
        db.create_tables([DrugMaster, DrugSyncHistory, DrugSyncLog])
        db.create_tables([PatientRx, TemplateDetails])
        db.create_tables([RobotMaster])
        db.create_tables([FileHeader, TemplateMaster])
        db.create_tables([CanisterDrawerMaster, CanisterMaster, CanisterHistory, CanisterTracker])
        db.create_tables([NdcBlacklist, NdcBlacklistAudit])
        db.create_tables([TempSlotInfo, BatchMaster, PackHeader, PackDetails, PackRxLink, PrintQueue, Printers])
        db.create_tables([SlotHeader, SlotDetails, SlotTransaction])
        db.create_tables([FileDownloadTracker, SystemSetting])
        db.create_tables([NoteMaster, PackStatusTracker, PackVerification])
        db.create_tables([VisionDrugPrediction, VisionCountPrediction])
        db.create_tables(
            [ConsumableTypeMaster, ConsumableTracker, Orders, OrderDetails, OrderStatusTracker, OrderDocument,
             ShipmentTracker, CourierMaster, ConsumableUsed], safe=True)

        db.register_fields({'primary_key': 'INT AUTOINCREMENT'})

        GroupMaster.create(**{'id': 1, 'name': 'PackStatus'})
        GroupMaster.create(**{'id': 2, 'name': 'FileStatus'})
        GroupMaster.create(**{'id': 3, 'name': 'TemplateStatus'})
        order_group = GroupMaster.create(**{'id': 4, 'name': 'OrderStatus'})
        document_group = GroupMaster.create(**{'id': 5, 'name': 'DocumentType'})

        CodeMaster.create(**{'id': 1, 'key': 1, 'value': 'ALL', 'group_id': 1})
        CodeMaster.create(**{'id': 2, 'key': 2, 'value': 'Pending', 'group_id': 1})
        CodeMaster.create(**{'id': 3, 'key': 3, 'value': 'Progress', 'group_id': 1})
        CodeMaster.create(**{'id': 4, 'key': 4, 'value': 'Processed', 'group_id': 1})
        CodeMaster.create(**{'id': 5, 'key': 5, 'value': 'Done', 'group_id': 1})
        CodeMaster.create(**{'id': 6, 'key': 6, 'value': 'Verified', 'group_id': 1})
        CodeMaster.create(**{'id': 7, 'key': 7, 'value': 'Deleted', 'group_id': 1})
        CodeMaster.create(**{'id': 8, 'key': 8, 'value': 'Manual', 'group_id': 1})
        CodeMaster.create(**{'id': 9, 'key': 9, 'value': 'Rolled Back', 'group_id': 1})
        CodeMaster.create(**{'id': 10, 'key': 10, 'value': 'ALL', 'group_id': 2})
        CodeMaster.create(**{'id': 11, 'key': 11, 'value': 'Pending', 'group_id': 2})
        CodeMaster.create(**{'id': 12, 'key': 12, 'value': 'Processed', 'group_id': 2})
        CodeMaster.create(**{'id': 13, 'key': 13, 'value': 'Error', 'group_id': 2})
        CodeMaster.create(**{'id': 14, 'key': 14, 'value': 'Rolled Back', 'group_id': 2})
        CodeMaster.create(**{'id': 15, 'key': 15, 'value': 'ALL', 'group_id': 3})
        CodeMaster.create(**{'id': 16, 'key': 16, 'value': 'Pending', 'group_id': 3})
        CodeMaster.create(**{'id': 17, 'key': 17, 'value': 'Done', 'group_id': 3})
        CodeMaster.create(**{'id': 18, 'key': 18, 'value': 'Rolled Back', 'group_id': 3})
        CodeMaster.create(**{'id': 19, 'key': 19, 'value': 'Verified With Success', 'group_id': 1})
        CodeMaster.create(**{'id': 20, 'key': 20, 'value': 'Verified With Failure', 'group_id': 1})
        CodeMaster.create(**{'id': 21, 'key': 21, 'value': 'Cancelled', 'group_id': 1})
        CodeMaster.create(**{'id': 22, 'key': 22, 'value': 'InQueue', 'group_id': 1})
        CodeMaster.create(**{'id': 23, 'key': 23, 'value': 'DispensePending', 'group_id': 1})
        CodeMaster.create(**{'id': 24, 'key': 24, 'value': 'Dropped', 'group_id': 1})
        CodeMaster.create(**{'id': 25, 'key': 25, 'value': 'Confirmation Pending', 'group_id': order_group.id})
        CodeMaster.create(**{'id': 26, 'key': 26, 'value': 'Confirmed', 'group_id': order_group.id})
        CodeMaster.create(**{'id': 27, 'key': 27, 'value': 'Processing', 'group_id': order_group.id})
        CodeMaster.create(**{'id': 28, 'key': 28, 'value': 'In Transit', 'group_id': order_group.id})
        CodeMaster.create(**{'id': 29, 'key': 29, 'value': 'Delivered', 'group_id': order_group.id})
        CodeMaster.create(**{'id': 30, 'key': 30, 'value': 'Cancelled', 'group_id': order_group.id})
        CodeMaster.create(**{'id': 31, 'key': 31, 'value': 'proforma_invoice', 'group_id': document_group.id})
        CodeMaster.create(**{'id': 32, 'key': 32, 'value': 'commercial_invoice', 'group_id': document_group.id})
        CodeMaster.create(**{'id': 33, 'key': 33, 'value': 'Discarded', 'group_id': 1})

        ConsumableTypeMaster.create(**{'id': 1, 'name': 'Blister Pack'})
        ConsumableTypeMaster.create(**{'id': 2, 'name': 'Label'})
        ConsumableTypeMaster.create(**{'id': 3, 'name': 'Vial'})

        CourierMaster.create(**{'id': 1, 'name': 'FedEx', 'website': 'www.fedex.com'})
        CourierMaster.create(**{'id': 2, 'name': 'DHL', 'website': 'www.dhl.com'})
        CourierMaster.create(**{'id': 3, 'name': 'USPS', 'website': 'www.usps.com'})
        CourierMaster.create(**{'id': 4, 'name': 'UPS', 'website': 'www.ups.com'})

        BatchMaster.create(**{"id": 1, "created_by": 1})
        pharmacy_record = PharmacyMaster.create(**{'system_id': 1, 'store_name': 'VIBRANT CARE PHARMACY INC', 'store_address': '7400 MACARTHUR BLVD, OAKLAND, CA 94605', 'store_phone': '(510) 638-9851',
                                 'store_fax': '9852', 'store_website': 'www.rxnsend.com', 'created_by': 1, 'modified_by': 1})


        # pack_plate_record = PackPlateMaster.create(**{'pack_plate_type': 1, 'reverse': True, 'rfid_based': True, 'created_by': 1, 'modified_by': 1})

        # robot_record = RobotMaster.create(**{'id': 1, 'system_id': 1, 'version': 1, 'name': 'Aaragon', 'max_canisters': 256,
        #                       'serial_number': 'RBT01', 'active': True, 'created_by': 1, 'modified_by': 1})
        # RobotMaster.create(
        #     **{'id': 4, 'system_id': 1, 'version': 1, 'name': 'Aaragon', 'max_canisters': 256,
        #        'serial_number': 'RBT04', 'active': True, 'created_by': 1, 'modified_by': 1})
        # RobotMaster.create(
        #     **{'id': 6, 'system_id': 1, 'version': 1, 'name': 'Aaragon', 'max_canisters': 256,
        #        'serial_number': 'RBT06', 'active': True, 'created_by': 1, 'modified_by': 1})
        # RobotMaster.create(
        #     **{'id': 8, 'system_id': 1, 'version': 1, 'name': 'Aaragon', 'max_canisters': 256,
        #        'serial_number': 'RBT08', 'active': True, 'created_by': 1, 'modified_by': 1})

        # CanisterDrawerMaster.create(**{'robot_id': robot_record.id, 'canister_drawer_number': 1, 'created_by': 1, 'modified_by': 1})

