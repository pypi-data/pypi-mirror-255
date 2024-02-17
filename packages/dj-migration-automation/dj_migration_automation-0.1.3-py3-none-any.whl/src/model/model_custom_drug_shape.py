from peewee import PrimaryKeyField, CharField, BooleanField, InternalError, IntegrityError, DoesNotExist, fn

import settings
from dosepack.base_model.base_model import BaseModel

logger = settings.logger


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True)
    image_name = CharField(max_length=55, null=True)
    help_video_name = CharField(max_length=55, null=True)
    is_deleted = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'custom_drug_shape'

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, name="Capsule"),
            dict(id=2, name="Elliptical"),
            dict(id=3, name="Oblong"),
            dict(id=4, name="Oval"),
            dict(id=5, name="Round Curved"),
            dict(id=6, name="Round Flat")
        ]

    @classmethod
    def db_get(cls):
        try:
            query = cls.select().where(CustomDrugShape.is_deleted == False)
            results = list()
            for record in query.dicts():
                results.append(record)
            return results
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_by_id(cls, id):
        try:
            data = CustomDrugShape.get(CustomDrugShape.id == id).name
            return data
        except DoesNotExist:
            return None
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_by_name(cls, req_name):
        try:
            data = CustomDrugShape.get(fn.LOWER(CustomDrugShape.name) == req_name.lower()).id
            return data
        except DoesNotExist:
            return None
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
