import logging
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.migrations.drug_refrence_image_dict import old_drug_image_data
from src.model.model_drug_master import DrugMaster

from src.cloud_storage import blob_exists, bucket_name, copy_blob, delete_blob
import settings

logger = logging.getLogger("root")

drug_fndc, drug_img = list(old_drug_image_data.keys()), list(old_drug_image_data.values())


def delete_drug_master_images():
    null_image_fndc_txr = []
    query = DrugMaster.select(DrugMaster.id).dicts().where(
        DrugMaster.concated_fndc_txr_field('_') << drug_fndc , DrugMaster.image_name << drug_img)

    drug_ids = [record['id'] for record in query]
    if drug_ids:
        query = DrugMaster.update(image_name=None).where(DrugMaster.id << drug_ids)
        print("Images deleted for drug_ids {}".format(drug_ids))
        query.execute()


def remove_wrong_named_images_from_bucket_and_db(drug_dimension_dir, drug_master_dir):
    init_db(db, 'database_migration')
    delete_drug_master_images()

    final_dict = {}
    for image_name in drug_img:

        if blob_exists(image_name, drug_master_dir, True):
            try:
                delete_blob(drug_master_dir+ "/"+ image_name, True)
                print("Deleted Image {}  from {}".format(image_name, drug_master_dir))
            except Exception as e:
                print("Cannot delete image {} in bucket {}".format(image_name, drug_master_dir))


        if blob_exists(image_name, drug_dimension_dir, True):
            try:
                delete_blob(drug_dimension_dir+ "/"+ image_name, True)
                print("Deleted Image {}  from {}".format(image_name, drug_dimension_dir))
            except Exception as e:
                print("Cannot delete image {} in bucket {}".format(image_name, drug_dimension_dir))
    print("Migration Remove Image run successfully")

if __name__ == "__main__":
    init_db(db, 'database_migration')
    drug_master_dir = 'drug_images'
    drug_dimension_dir = 'pill_dimension_drug_images'
    remove_wrong_named_images_from_bucket_and_db(drug_dimension_dir, drug_master_dir)