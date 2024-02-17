import settings
from dosepack.base_model.base_model import BaseModel
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, InternalError, IntegrityError, DoesNotExist, DataError
from src.model.model_consumable_type_master import ConsumableTypeMaster

logger = settings.logger


class ConsumableTracker(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    consumable_id = ForeignKeyField(ConsumableTypeMaster)
    quantity = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "consumable_tracker"

    @classmethod
    def db_update_or_create(cls, company_id, consumable_id, defaults_data_dict=None):
        try:
            record, created = ConsumableTracker.get_or_create(company_id=company_id, consumable_id=consumable_id,
                                                              defaults=defaults_data_dict)
            if not created:
                ConsumableTracker.update(**{'quantity': record.quantity + defaults_data_dict["quantity"]})\
                    .where(ConsumableTracker.id == record.id).execute()
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_remove_consumed_items(cls, consumed_data, company_id):
        try:
            new_data = {}
            for item in consumed_data:
                try:
                    record = ConsumableTracker.get(consumable_id=item, company_id=company_id)
                    new_data[record.id] = record.quantity - consumed_data[item]
                except DoesNotExist:
                    pass
            for item in new_data:
                ConsumableTracker.update(quantity=new_data[item]) \
                    .where(ConsumableTracker.id == item).execute()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
