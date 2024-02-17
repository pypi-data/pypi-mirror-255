import datetime
import json
import sys

from google.cloud import storage
import google
import os
import functools
import settings
from dosepack.utilities.utils import log_args_and_response
from src.exceptions import PreconditionFailedException

logger = settings.logger

os.environ["PROJECT_ID"] = "dosepack-197416"
if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join('../secret_keys', 'dosepack-b325905c30d0.json')
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join('secret_keys', 'dosepack-b325905c30d0.json')

storage_client = storage.Client()
bucket_name = os.environ.get('BUCKET_NAME', 'dosepack-dev')
label_blob_dir = os.environ.get('PACK_LABEL_PATH', 'pack_labels')
canister_label_dir = os.environ.get('CANISTER_LABEL_PATH', 'canister_labels')
drug_bottle_label_dir = os.environ.get('BOTTLE_LABEL_PATH', 'drug_bottle_labels')
drug_blob_dir = os.environ.get('DRUG_IMAGE_PATH', 'drug_images')
pack_error_blob_dir = os.environ.get('PACK_ERROR_LABEL_PATH', 'pack_error_labels')
rx_file_blob_dir = os.environ.get('RX_FILE_PATH', 'pharmacy_rx_files')
pack_stencil_label_dir = os.environ.get('PACK_STENCIL_LABEL_PATH', 'pst_labels')
mfd_canister_label_dir = os.environ.get('MFD_CANISTER_LABEL_PATH', 'mfd_canister_labels')
drug_master_dir = os.environ.get('DRUG_MASTER_DIR', 'drug_images')
drug_dimension_dir = os.environ.get('PILL_DIMENSION_DIR', 'pill_dimension_drug_images')
vial_label_dir = os.environ.get('VIAL_LABEL_PATH', 'vial_labels')
drug_bucket_name = os.environ.get("DRUG_BUCKET_NAME", 'dosepack-dev')



def bucket_init():
    try:  # check if bucket is present or not
        storage_client.get_bucket(bucket_name)
    except google.api_core.exceptions.NotFound:
        try:
            bucket = storage.Bucket(client=storage_client, name=bucket_name)
            bucket.location = os.environ.get('BUCKET_LOCATION', 'us-central1')
            bucket.create()
        except google.api_core.exceptions.Conflict:
            logger.info("Storage Bucket already exists")
        except Exception as e:
            logger.fatal("Couldn't Create Storage Bucket")
            logger.fatal(e, type(e))
            raise PreconditionFailedException("Couldn't Create Storage Bucket")


def create_blob(src_file, dest_file, blob_dir_path, drug_image=False):
    dest_file = blob_dir_path + '/' + dest_file
    if drug_image:
        logger.info('Trying to get the bucket: {}'.format(drug_bucket_name))
        bucket = storage_client.get_bucket(drug_bucket_name)
    else:
        logger.info('Trying to get the bucket: {}'.format(bucket_name))
        bucket = storage_client.get_bucket(bucket_name)
    logger.info('Trying to create blob for: {}'.format(dest_file))
    blob = bucket.blob(dest_file)
    logger.info('Blob created for {}'.format(dest_file))
    blob.upload_from_filename(src_file)


def download_blob(blob_name, dest_file, blob_dir_path, drug_image=False):
    blob_name = blob_dir_path + '/' + blob_name
    if drug_image:
        logger.debug('Trying to get the bucket: {}'.format(drug_bucket_name))
        bucket = storage_client.get_bucket(drug_bucket_name)
    else:
        logger.debug('Trying to get the bucket: {}'.format(bucket_name))
        bucket = storage_client.get_bucket(bucket_name)
    logger.debug('Trying to create blob for: {}'.format(dest_file))
    blob = bucket.blob(blob_name)
    logger.debug('Blob created for {}'.format(dest_file))
    blob.download_to_file(dest_file)


# @functools.lru_cache(maxsize=500)
def blob_as_string(blob_name, blob_dir_path, drug_image=False):
    """
    Returns string for given file using download_as_string of bucket.blob

    :param blob_name: str - file name
    :param blob_dir_path: str - full path of directory of blob in bucket
    :return: str
    """
    try:
        if blob_dir_path:
            blob_name = blob_dir_path + '/' + blob_name
        if drug_image:
            bucket = storage_client.get_bucket(drug_bucket_name)
            logger.info("In blob_as_string, bucket_name: {}".format(drug_bucket_name))
        else:
            bucket = storage_client.get_bucket(bucket_name)
            logger.info("In blob_as_string, bucket_name: {}".format(bucket_name))
        blob = bucket.blob(blob_name)
        return blob.download_as_string()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in blob_as_string: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        raise e


def blob_exists(file_name, blob_dir_path, drug_image=False):
    """
    Returns True if file present in given dir.

    :param file_name:
    :param blob_dir_path:
    :return: bool
    """
    blob_name = blob_dir_path + '/' + file_name
    if drug_image:
        bucket = storage_client.get_bucket(drug_bucket_name)
        logger.info("In blob_exists, bucket_name {}".format(drug_bucket_name))
    else:
        bucket = storage_client.get_bucket(bucket_name)
        logger.info("In blob_exists, bucket_name {}".format(bucket_name))
    blob = bucket.blob(blob_name)
    return blob.exists()


@log_args_and_response
def save_and_upload_file_to_cloud(file_data: dict):
    """
    Method to upload file to cloud
    @param file_data:
    @return:
    """
    try:
        file = file_data["file_name"]
        company_id = file_data["company_id"]
        file_name: str = file + ".json"
        logger.debug("save_and_upload_file_to_cloud: uploading file - {}".format(file_name))

        # check if the pharmacy_files directory exists or not in local
        file_dir = os.path.join(settings.PENDING_FILE_PATH, str(company_id))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        # append the file_name to the directory
        file_path = os.path.join(file_dir, file_name)

        # create json from the args
        rx_file = open(file_path, "w")
        json.dump(file_data, rx_file)

        # close the file after populating record
        rx_file.close()

        # upload file to cloud
        start_time = datetime.datetime.now()
        create_blob(file_path, file_name, '{}/{}'.format(rx_file_blob_dir, company_id))
        end_time = datetime.datetime.now()
        logger.info('Uploading time for file {}: {}s'.format(file_name, (end_time - start_time).total_seconds()))

        os.remove(file_path)
        logger.debug("save_and_upload_file_to_cloud: uploaded file - {}".format(file_name))

    except Exception as e:
        raise e


def copy_blob(bucket_name, blob_name, destination_blob_name, drug_image=False):
    """ Copies file from one directory to another directory"""
    # storage_client = storage.Client()
    if drug_image:
        bucket = storage_client.bucket(drug_bucket_name)
        logger.info("In copy_blob, bucket_name: {}".format(drug_bucket_name))
    else:
        bucket = storage_client.bucket(bucket_name)
        logger.info("In copy_blob, bucket_name: {}".format(bucket_name))
    source_blob = bucket.blob(blob_name)

    bucket.copy_blob(source_blob, bucket, destination_blob_name)


def delete_blob(blob_name, drug_image=False):
    if drug_image:
        bucket = storage_client.bucket(drug_bucket_name)
        logger.info("In delete_blob, bucket_name: {}".format(drug_bucket_name))
    else:
        bucket = storage_client.bucket(bucket_name)
        logger.info("In delete_blob, bucket_name: {}".format(bucket_name))
    blob = bucket.blob(blob_name)
    blob.delete()
