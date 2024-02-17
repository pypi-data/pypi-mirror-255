from playhouse.migrate import *
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_patient_schedule import PatientSchedule


def migration_add_column_patient_overwrite_in_patient_schedule():
    init_db(db, "database_migration")
    # migrator = SchemaMigrator(db)
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            migrate(
                migrator.add_column(PatientSchedule._meta.db_table,
                                    PatientSchedule.patient_overwrite.db_column,
                                    PatientSchedule.patient_overwrite)
            )
    except Exception as e:
        print("error", e)


if __name__ == "__main__":
    migration_add_column_patient_overwrite_in_patient_schedule()
    print("column patient_overwrite is added in patient_schedule")
