"""
    @file: model/model_pack.py
    @createdBy: Manish Agarwal
    @createdDate: 7/22/2015
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 7/2/2015
    @type: file
    @desc: model class for database tables
"""
import logging

logger = logging.getLogger("root")
schedule_logger = logging.getLogger("schedule")



# class ExtPackDetails(BaseModel):
#     id = PrimaryKeyField()
#     pack_id = ForeignKeyField(PackDetails, unique=True)
#     pack_display_id = IntegerField()
#
#     # This can have values like Checked, Error, Fixed Error, Not Checked
#     rph_verification_status = ForeignKeyField(CodeMaster, related_name="ext_pack_details_rph_verification_status",
#                                               null=True)
#     rph_reason_code = CharField(null=True)
#     rph_comment = CharField(null=True)
#     rph_ext_user_name = FixedCharField(max_length=64, null=True)
#     rph_user_id = IntegerField(null=True)
#     rph_status_datetime = DateTimeField(null=True)
#
#     # This can have values like Filled, Deleted, Reuse
#     technician_fill_status = ForeignKeyField(CodeMaster, related_name="ext_pack_details_technician_fill_status",
#                                              null=True)
#     technician_status_datetime = DateTimeField(null=True)
#     technician_ext_user_name = FixedCharField(max_length=64, null=True)
#     technician_user_id = IntegerField(null=True)
#
#     # This fields will store delivery information
#     delivery_status = ForeignKeyField(CodeMaster, related_name="ext_pack_details_delivery_status", null=True)
#     delivery_status_datetime = DateTimeField(null=True)
#     delivery_change_ext_user_name = FixedCharField(max_length=64, null=True)
#     delivery_change_user_id = IntegerField(null=True)
#
#     api_call_created_datetime = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "ext_pack_details"
#
#     # @classmethod
#     # def db_get_pack_grid_id(cls, row, col):
#     #     try:
#     #         data = cls.select(cls.id).dicts().where((cls.slot_row == row), (cls.slot_column == col)).get()
#     #         return data['id']
#     #     except (InternalError, IntegrityError) as e:
#     #         logger.error(e, exc_info=True)
#     #         raise


# class ExtRxChangeTracker(BaseModel):
#     id = PrimaryKeyField()
#     pack_display_id = IntegerField()
#     pack_id = ForeignKeyField(PackDetails, null=True)
#     pharmacy_rx_no= FixedCharField(max_length=20)
#     patient_rx_id = ForeignKeyField(PatientRx, null=True)
#     ndc = CharField(max_length=14)
#     rx_status = ForeignKeyField(CodeMaster, related_name="ext_rx_change_status")
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "ext_rx_change_tracker"


