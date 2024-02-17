import operator
import os
import sys
import threading
import time

import settings
from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *
from dosepack.utilities.utils import convert_date_to_sql_date

from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_header import SlotHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_batch_master import BatchMaster
from src.model.model_pack_details import PackDetails


class SlotDetails(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotHeader, related_name="migration_slot_id_id")
    pack_rx_id = ForeignKeyField(PackRxLink, related_name="migration_pack_rx_id_id")
    quantity = DecimalField(decimal_places=2, max_digits=4)
    is_manual = BooleanField()
    drug_id = ForeignKeyField(DrugMaster, related_name="migration_drug_id_id", null=True)
    original_drug_id = ForeignKeyField(DrugMaster, related_name="migration_slot_details_original_drug_id_id", null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_details"


def update_table_slot_details():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)
        threads_list = []
        count = 0
        st = time.time()

        slot_details_update = dict()
        pack_ids = set()
        batch_ids = set()
        slot_ids = list()

        slot_details_update_list = []
        pack_status_list = [settings.PENDING_PACK_STATUS, settings.MANUAL_PACK_STATUS]

        # for record in SlotDetails.select(SlotDetails.id, PatientRx.drug_id, PackDetails.id.alias("pack_id"), PackDetails.batch_id).dicts() \
        #         .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
        #         .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        #         .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
        #         .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
        #         .where(BatchMaster.status.in_(settings.CURRENT_AND_UPCOMING_BATCH_STATUS_LIST) | ((
        #             PackDetails.pack_status.in_(pack_status_list)) & PackDetails.batch_id.is_null(True)),
        #                SlotDetails.drug_id.is_null(True)):
        #
        #     pack_ids.add(record["pack_id"])
        #     batch_ids.add(record["batch_id"])
        #     slot_ids.append(record["id"])
        #
        # print(len(slot_ids))
        # print(len(pack_ids))
        # print((batch_ids))
        #
        # print(len(batch_ids))
        #
        # a = input()

        from_date = '01-20-22'
        to_date = '02-24-22'

        date_from, date_to = convert_date_to_sql_date(from_date, to_date)

        print(date_from, date_to)

        clauses = list()
        clauses.append((PackDetails.created_date.between(date_from, date_to)))
        clauses.append((SlotDetails.drug_id.is_null(True)))

        for record in SlotDetails.select(SlotDetails.id, PatientRx.drug_id, PackDetails.id.alias("pack_id"),
                                         PackDetails.batch_id).dicts() \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
                .where(functools.reduce(operator.and_, clauses)):
            slot_details_update[record["id"]] = {"drug_id": record["drug_id"]}
            slot_details_update_list.append((record["id"], record["drug_id"]))

            SlotDetails.update(drug_id=record["drug_id"], original_drug_id=record["drug_id"]).where(
                SlotDetails.id == record["id"]).execute()

            pack_ids.add(record["pack_id"])
        # for record in SlotDetails.select(SlotDetails.id, PatientRx.drug_id, PackDetails.id.alias("pack_id"), PackDetails.batch_id).dicts() \
        #         .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
        #         .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        #         .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
        #         .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
        #         .where(BatchMaster.status.in_(settings.CURRENT_AND_UPCOMING_BATCH_STATUS_LIST) | ((
        #             PackDetails.pack_status.in_(pack_status_list)) & PackDetails.batch_id.is_null(True)),
        #                SlotDetails.drug_id.is_null(True)):
        #
        #     slot_details_update[record["id"]] = {"drug_id": record["drug_id"]}
        #     slot_details_update_list.append((record["id"], record["drug_id"]))
        #
        #     SlotDetails.update(drug_id=record["drug_id"], original_drug_id=record["drug_id"]).where(
        #         SlotDetails.id == record["id"]).execute()

            # update_table(record["drug_id"], record["id"])
            # count += 1
            # if count == 10000:
            #     break

        #     t = threading.Thread(target=update_table, args=[record["drug_id"], record["id"]])
        #     threads_list.append(t)
        #     t.start()
        #     # if len(threads_list) == 10000:
        #     #     break
        #
        # [th.join() for th in threads_list]  # wait for all thread to close

        # print("count: ", len(threads_list))
        et = time.time()

        print("pack count: ", len(pack_ids))

        print("total time : ", et - st)  # 1000 > time: 48.3166983127594 ,  36.00  10000 > 434.9414155483246
        print("no of packs updated: ", len(pack_ids))

        # print("slot_details {}".format(slot_details_update_list))
        # case_sequence = case(SlotDetails.id, slot_details_update_list)
        # print("case_sequence: ", case_sequence)
        # query = SlotDetails.update(drug_id=case_sequence, original_drug_id=case_sequence)
        # query.execute()
        # print("update columns: drug_id and original_drug_id of the table slot_details.")

        # migrate(migrator.add_not_null("slot_details", "drug_id"))
        # migrate(migrator.add_not_null("slot_details", "original_drug_id"))
        #
        # print("Not null constraint added to the columns: drug_id and original_drug_id of the table slot_details.")

    except Exception as e:
        print("Error in update_table_slot_details: ", str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_table_slot_details: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        return e


def update_table(drug_id, slot_id):
    SlotDetails.update(drug_id=drug_id, original_drug_id=drug_id).where(
        SlotDetails.id == slot_id).execute()


if __name__ == "__main__":
    update_table_slot_details()
