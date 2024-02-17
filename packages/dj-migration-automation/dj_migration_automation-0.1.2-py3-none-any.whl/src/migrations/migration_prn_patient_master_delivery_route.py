from playhouse.migrate import MySQLMigrator, migrate
from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src.model.model_patient_master import PatientMaster

init_db(db, 'database_migration')


def migration_for_prn_other_rx_patient_master_delivery_route():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PatientMaster._meta.db_table,
                                PatientMaster.delivery_route_name.db_column,
                                PatientMaster.delivery_route_name)
        )
        migrate(
            migrator.add_column(PatientMaster._meta.db_table,
                                PatientMaster.delivery_route_id.db_column,
                                PatientMaster.delivery_route_id)
        )
        print("delivery_route, delivery_route_id column added in PatientMaster")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_for_prn_other_rx_patient_master_delivery_route()
