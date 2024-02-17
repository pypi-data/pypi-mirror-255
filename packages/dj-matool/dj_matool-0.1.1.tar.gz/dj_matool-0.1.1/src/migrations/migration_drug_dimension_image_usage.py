import logging
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response
from model.model_init import init_db
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_dimention_history import DrugDimensionHistory
from src.cloud_storage import blob_exists, bucket_name, copy_blob, drug_bucket_name
import settings
logger = logging.getLogger("root")


@log_args_and_response
def drug_dimension_image_usage(drug_master_dir, drug_dimension_dir):
    init_db(db, "database_migration")
    try:
        drug_image_dict = dict()  # Stores drug_id as key and image_name from DrugDimensionHistory as value
        # query for finding drugs from DrugMaster which have image_name in DrugDimensionHistory
        query = DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                  DrugMaster.image_name.alias('drug_master_image'),
                                  DrugDimensionHistory.image_name.alias('drug_dimension_image')) \
                                .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                                                      (DrugMaster.txr == UniqueDrug.txr))) \
                                .join(DrugDimension, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                                .join(DrugDimensionHistory, on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                                .where(DrugDimensionHistory.image_name.is_null(False)) \
                                .order_by(DrugMaster.id, DrugDimensionHistory.created_date)

        for drugs in query.dicts():
            if drugs['drug_master_image'] is None:   # drugs which don't have image_name in DrugMaster
                drug_image_dict[drugs['drug_id']] = drugs['drug_dimension_image']
            else:
                # if image_name of DrugMaster exists in cloud, do nothing
                if blob_exists(drugs['drug_master_image'], drug_master_dir, True):
                    continue
                else:  # drugs which have image_name in DrugMaster but image does not exist in cloud
                    drug_image_dict[drugs['drug_id']] = drugs['drug_dimension_image']

        update_image(drug_image_dict, drug_master_dir, drug_dimension_dir)
        logger.info("Images updated in DrugMaster from DrugDimension")
    except Exception as e:
        logger.error("Error in drug dimension image usage: ", str(e))


def update_image(drug_image_dict, drug_master_dir, drug_dimension_dir):
    try:
        for drug_id, image_name in drug_image_dict.items():
            if blob_exists(image_name, drug_dimension_dir, True):
                if blob_exists(image_name, drug_master_dir, True):
                    logger.info("Image already exists in drug_images for drug_id", drug_id)
                else:
                    # updating image in cloud
                    source_blob = drug_dimension_dir + '/' + image_name
                    destination_blob = drug_master_dir + '/' + image_name
                    copy_blob(drug_bucket_name, source_blob, destination_blob, True)
                # update drug image in DrugMaster table
                update_query = DrugMaster.update({DrugMaster.image_name: image_name}).where(
                    DrugMaster.id == drug_id)
                update_query.execute()
        logger.info("Images added in cloud and image_name updated in DrugMaster table")
    except Exception as e:
        logger.error("Error while updating image_name in cloud: ", str(e))


if __name__ == "__main__":
    drug_dimension_image_usage(drug_master_dir=None, drug_dimension_dir=None)










