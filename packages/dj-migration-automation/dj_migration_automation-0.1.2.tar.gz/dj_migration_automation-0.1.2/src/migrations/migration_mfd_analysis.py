from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class MfdAnalysis(BaseModel):
    id = PrimaryKeyField()
    # batch_id = ForeignKeyField(BatchMaster, related_name='batch_id')
    # mfd_canister_id = ForeignKeyField(MfdCanisterMaster, null=True, related_name='mfd_can_id')
    order_no = IntegerField()
    assigned_to = IntegerField(null=True)
    # status_id = ForeignKeyField(CodeMaster, related_name='can_status')
    # dest_device_id = ForeignKeyField(DeviceMaster, related_name='robot_id')
    # mfs_device_id = ForeignKeyField(DeviceMaster, null=True, related_name='manual_fill_station')
    mfs_location_number = IntegerField(null=True)
    dest_quadrant = IntegerField()
    # trolley_location_id = ForeignKeyField(LocationMaster, related_name='trolley_loc_id', null=True)
    # dropped_location_id = ForeignKeyField(LocationMaster, null=True, related_name='dropped_loc_id')
    trolley_seq = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis"


def migrate_mfd_analysis_trolley():
    init_db(db, "database_migration")

    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(MfdAnalysis._meta.db_table,
                            MfdAnalysis.trolley_seq.db_column,
                            MfdAnalysis.trolley_seq
                            )
    )

    print('Column added in: MfdAnalysis')


if __name__ == "__main__":
    migrate_mfd_analysis_trolley()
