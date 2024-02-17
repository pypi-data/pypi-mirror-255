from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class DrugMaster(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50)
    strength_value = CharField(max_length=16)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    # drug_id = ForeignKeyField(DrugMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class DosageType(BaseModel):
    id = PrimaryKeyField()
    code = FixedCharField(unique=True, max_length=10)
    name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "dosage_type"


class StoreSeparateDrug(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    dosage_type_id = ForeignKeyField(DosageType, null=True)
    # note = CharField(null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('company_id', 'unique_drug_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "store_separate_drug"


class CompanySetting(BaseModel):
    """ stores setting for a company """
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    # Constant for template_settings
    SLOT_VOLUME_THRESHOLD_MARK = 'SLOT_VOLUME_THRESHOLD_MARK'
    SPLIT_STORE_SEPARATE = 'SPLIT_STORE_SEPARATE'
    VOLUME_BASED_TEMPLATE_SPLIT = 'VOLUME_BASED_TEMPLATE_SPLIT'
    COUNT_BASED_TEMPLATE_SPLIT = 'COUNT_BASED_TEMPLATE_SPLIT'
    TEMPLATE_SPLIT_COUNT_THRESHOLD = 'TEMPLATE_SPLIT_COUNT_THRESHOLD'
    template_setting_converter_and_default = {
        # dict to maintain type and default of template settings
        SLOT_VOLUME_THRESHOLD_MARK: (float, 0.53),
        SPLIT_STORE_SEPARATE: (int, 1),
        VOLUME_BASED_TEMPLATE_SPLIT: (int, 1),
        COUNT_BASED_TEMPLATE_SPLIT: (int, 0),
        TEMPLATE_SPLIT_COUNT_THRESHOLD: (int, 6),
    }

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )


def migrate_46():
    init_db(db, "database_migration")
    company_id = 3
    user_id = 1
    odt_ndcs = ['00093541901', '00093541701', '00093308684', '00093308784', '60505327803', '60505327603', '60505327703', '33342008507', '60505327503', '33342008607', '33342008307', '33342008407', '55111026379', '68462015811', '59746005022', '49884031591', '59746004022', '59746003022', '59746002022', '00781531106']
    chewable_ndcs = ["12843013231"]
    softgel_ndcs = ['54629089309', '79854000893', '54629001893', '47469004040', '33674015903', '00536718601', '00536718706']

    db.create_tables([StoreSeparateDrug, DosageType], safe=True)
    print('Table Created: StoreSeparateDrug, DosageType')

    ctb, _ = DosageType.get_or_create(code='CTB', **{'name': 'Chewable Tablet'})
    odt, _ = DosageType.get_or_create(code='ODT', **{'name': 'Orally Disintegrating Tablet'})
    sgl, _ = DosageType.get_or_create(code='SGL', **{'name': 'Softgel'})
    print('Table Updated: DosageType')
    for name, value in CompanySetting.template_setting_converter_and_default.items():
        # insert if not present, do not override it
        CompanySetting.get_or_create(
            company_id=company_id,
            name=name,
            defaults={
                'value': str(value[1]),
                'created_by': user_id,
                'modified_by': user_id,
            })
    with db.transaction():
        store_separate_list = list()
        base_query = DrugMaster.select(UniqueDrug.id.alias('unique_drug_id')).join(
            UniqueDrug,
            on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
               & (UniqueDrug.txr == DrugMaster.txr)
        )
        odt_query = base_query.where(DrugMaster.ndc << odt_ndcs)
        for record in odt_query.dicts():
            store_separate_list.append({
                'unique_drug_id': record['unique_drug_id'],
                'dosage_type_id': odt.id,
                'created_by': user_id,
                'modified_by': user_id,
                'company_id': company_id
            })
        chewable_query = base_query.where(DrugMaster.ndc << chewable_ndcs)
        for record in chewable_query.dicts():
            store_separate_list.append({
                'unique_drug_id': record['unique_drug_id'],
                'dosage_type_id': ctb.id,
                'created_by': user_id,
                'modified_by': user_id,
                'company_id': company_id
            })
        sgl_query = base_query.where(DrugMaster.ndc << softgel_ndcs)
        for record in sgl_query.dicts():
            store_separate_list.append({
                'unique_drug_id': record['unique_drug_id'],
                'dosage_type_id': sgl.id,
                'created_by': user_id,
                'modified_by': user_id,
                'company_id': company_id
            })
        status = StoreSeparateDrug.insert_many(store_separate_list).execute()
        print("Initial StoreSeparateDrug(s) inserted. status: {}".format(status))


if __name__ == '__main__':
    migrate_46()
