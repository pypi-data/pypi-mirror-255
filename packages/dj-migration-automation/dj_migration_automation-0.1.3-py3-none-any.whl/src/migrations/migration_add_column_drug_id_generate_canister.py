import os
import sys

from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *
from dosepack.utilities.utils import get_current_date_time
import settings
from src.model.model_code_master import CodeMaster
from model.model_init import init_db
from src.model.model_drug_master import DrugMaster
from model.model_volumetric_analysis import CanisterStick


class GenerateCanister(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField()
    ndc = CharField(max_length=14)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drug_id = ForeignKeyField(DrugMaster, null=True, related_name='drug_master_drug_id')
    requested_canister_count = IntegerField(default=0)
    created_by = IntegerField(default=13)
    odoo_request_id = IntegerField(default=1)
    status = ForeignKeyField(CodeMaster, related_name="requested_canister_status", default=204)
    canister_stick_id = ForeignKeyField(CanisterStick, related_name="stick_id", default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "generate_canister"


def migration_add_column_drug_id_in_generate_canister():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if GenerateCanister.table_exists():
            # Add column drug_id and requested_canister_count and created_by

            migrate(
                    migrator.add_column(GenerateCanister._meta.db_table,
                                        GenerateCanister.drug_id.db_column,
                                        GenerateCanister.drug_id))

            migrate(
                migrator.add_column(GenerateCanister._meta.db_table,
                                    GenerateCanister.requested_canister_count.db_column,
                                    GenerateCanister.requested_canister_count))

            migrate(
                migrator.add_column(GenerateCanister._meta.db_table,
                                    GenerateCanister.created_by.db_column,
                                    GenerateCanister.created_by))

            migrate(
                migrator.add_column(GenerateCanister._meta.db_table,
                                    GenerateCanister.odoo_request_id.db_column,
                                    GenerateCanister.odoo_request_id))

            migrate(
                migrator.add_column(GenerateCanister._meta.db_table,
                                    GenerateCanister.status.db_column,
                                    GenerateCanister.status))

            migrate(
                migrator.add_column(GenerateCanister._meta.db_table,
                                    GenerateCanister.canister_stick_id.db_column,
                                    GenerateCanister.canister_stick_id))

            # # sync generate canister table with drug master table
            add_drug_data()
            print("data inserted in generate canister")

            migrate(migrator.drop_column(GenerateCanister._meta.db_table,
                                         GenerateCanister.ndc.db_column))
            print("dropped column ndc from table generate canister")

            migrate(migrator.add_not_null(GenerateCanister._meta.db_table,
                                          GenerateCanister.drug_id.db_column))
            print("Add not null constraint for drug_id column in generate canister")

            migrate(migrator.add_not_null(GenerateCanister._meta.db_table,
                                          GenerateCanister.created_by.db_column))
            print("Add not null constraint for created_by column in generate canister")

            migrate(migrator.add_not_null(GenerateCanister._meta.db_table,
                                          GenerateCanister.odoo_request_id.db_column))
            print("Add not null constraint for odoo_request_id column in generate canister")

            migrate(migrator.add_not_null(GenerateCanister._meta.db_table,
                                          GenerateCanister.status.db_column))
            print("Add not null constraint for status column in generate canister")

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in executing migration: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")

        raise


def add_drug_data():
    try:
        """
            Fetch drug id based on ndc from drug master table
        """
        query = DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                  DrugMaster.ndc) \
            .join(GenerateCanister, on=GenerateCanister.ndc == DrugMaster.ndc)
        """
            Update drug_id for generate canister table
        """
        for record in query.dicts():
            GenerateCanister.update(drug_id=record["drug_id"]).where(
                GenerateCanister.ndc == record["ndc"]).execute()
    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    migration_add_column_drug_id_in_generate_canister()
