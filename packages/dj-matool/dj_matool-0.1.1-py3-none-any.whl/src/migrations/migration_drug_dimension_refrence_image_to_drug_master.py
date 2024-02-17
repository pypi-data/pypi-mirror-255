import logging
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response
from model.model_init import init_db
from src.migrations.drug_refrence_image_dict import new_drug_image_dit, drug_image_dict_23_03_2023
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_dimention_history import DrugDimensionHistory
from src.cloud_storage import blob_exists, bucket_name, copy_blob, drug_bucket_name
import settings
logger = logging.getLogger("root")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# add the handler to the logger
logger.addHandler(console_handler)


def drug_master_fndc_txr():
    
    null_image_fndc_txr = []
    query = DrugMaster.select(DrugMaster.concated_fndc_txr_field('_').alias('fndc_txr')).dicts().where(DrugMaster.image_name.is_null(True))
    null_image_fndc_txr = [record['fndc_txr'] for record in query]

    return null_image_fndc_txr


def add_drug_dimension_ref_image_to_drug_master(refernce_image_fndc_txr=drug_image_dict_23_03_2023, drug_dimension_dir="pill_dimension_drug_images",
                                                drug_master_dir="drug_images"):
    init_db(db, 'database_migration')
    null_image_fndc_txr = drug_master_fndc_txr()
    count = 0
    count1 = 0
    count3 = 0
    missing = []
    missing_list_in_dg = []
    not_available_in_pill_dimension = []
    available = []
    for fndc_txr in null_image_fndc_txr:
        missing_list_in_dg.append(fndc_txr)
        count1 += 1
        if fndc_txr in refernce_image_fndc_txr:
            available.append(fndc_txr)
            image_name = refernce_image_fndc_txr[fndc_txr]
            if blob_exists(image_name, drug_dimension_dir, True):
                count += 1
                if blob_exists(image_name, drug_master_dir, True):
                    print("Image already exists in drug_images for fndc_txr: {}".format(fndc_txr))
                else:
                    # updating image in cloud
                    source_blob = drug_dimension_dir + '/' + image_name
                    destination_blob = drug_master_dir + '/' + image_name
                    copy_blob(drug_bucket_name, source_blob, destination_blob, True)
                    print("Image updated in drug_images for fndc_txr : {} image {}".format(fndc_txr, image_name))
                count3 += 1
                missing.append(fndc_txr)
                # update drug image in DrugMaster table
                update_query = DrugMaster.update({DrugMaster.image_name: image_name}).where(
                    DrugMaster.concated_fndc_txr_field("_") == fndc_txr)
                update_check = update_query.execute()
                if update_check:
                    print("Image updated for {}: image name = {}".format(fndc_txr, image_name))
    available = list(set(available))
    count2 = len(available)
    print("null_image_in drug_master in `dpws_stage_v3_live` are: ", count1, "which are", missing_list_in_dg)
    print(f"out of those {count1} missing images reference in folder available are: ", count2, available)
    print("and not available are:", not_available_in_pill_dimension)
    print("out of these missing images, in cloud drug_dimension_dir available are: ", count)
    print("missing in cloud are: ", count3, missing)


if __name__ == "__main__":

    drug_master_dir = 'drug_images'
    drug_dimension_dir = 'pill_dimension_drug_images'
    add_drug_dimension_ref_image_to_drug_master(drug_image_dict_23_03_2023, drug_dimension_dir, drug_master_dir)