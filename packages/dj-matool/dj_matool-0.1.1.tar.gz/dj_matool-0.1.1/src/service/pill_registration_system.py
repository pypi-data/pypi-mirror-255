from peewee import *

import settings
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, image_convert
from dosepack.validation.validate import validate
from src import constants
from src.dao.pill_registration_system_dao import db_get_prs_drug_data, \
    db_get_pvs_drug_crop_images, get_prs_data_dao, add_data_in_prs_drug_data, \
    db_get_next_unique_drug_id_based_on_status, get_count_from_company_setting, get_filters_for_prs, \
    get_prs_images_from_unique_drug_id, update_prs_images_for_unique_drug, \
    get_remote_tech_slot_id_from_prs_unique_drug_and_images
from src.dao.remote_tech_dao import get_remote_tech_slot_id_dao, update_status_in_remote_tech_slot_dao, \
    update_status_in_remote_tech_slot_details_dao

logger = settings.logger


@log_args_and_response
def update_prs_data(data_dict: dict) -> dict:
    """
        @input: args:{
                        "face1": str(list of images),
                        "face2": str(list of images),
                        "side face": str(list of images),
                        "user_id":id}
                    }
        @return:
    """
    try:
        logger.debug("In save prs drug images")
        data_dict["unique_drug_id"] = data_dict.pop("drug_id")
        prs_status = data_dict["status"]
        if prs_status == constants.PRS_DRUG_STATUS_DONE:
            if "done_by" not in data_dict:
                return error(1001, "Missing Parameter(s): done_by.")

        if prs_status == constants.PRS_DRUG_STATUS_REGISTERED:
            if "registered_by" not in data_dict:
                return error(1001, "Missing Parameter(s): rejected_by.")

        if prs_status == constants.PRS_DRUG_STATUS_VERIFIED:
            if "verified_by" not in data_dict:
                return error(1001, "Missing Parameter(s): verified_by.")

        drug_images = ["face1", "face2", "side_face"]

        if any(drug_images) in data_dict:
            if type(data_dict["unique_drug_id"]) == list:
                return error(1001, "Images for one drug can be updated at a time.")

        if "face1" in data_dict:
            face1 = len(data_dict["face1"].split(","))
            if face1 < constants.PRS_IMAGE_COUNT:
                return error(1001, "Incorrect image count for face1.")

        if "face2" in data_dict:
            face2 = len(data_dict["face2"].split(","))
            if face2 < constants.PRS_IMAGE_COUNT:
                return error(1001, "Incorrect image count for face2.")

        # if "sideface" in data_dict:
        #     sideface = len(data_dict["sideface"].split(","))
        #     if sideface < constants.PRS_IMAGE_COUNT:
        #         return error(1001, "Incorrect image count for sideface")

        if prs_status == constants.PRS_DRUG_STATUS_REJECTED:
            if "comments" not in data_dict:
                return error(1001, "Missing Parameter(s): comments.")

        response = add_data_in_prs_drug_data(data_dict=data_dict)
        return create_response(response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_prs_data {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in update_prs_data {}".format(e))
        return error(1000, "Error in update_prs_data: " + str(e))


@log_args_and_response
def get_prs_drug_images(args):
    """
    Method to get drug data and slot images based on prs mode
    @param args:
    @return:
    """
    unique_drug_ids = args.get("unique_drug_ids")
    paginate = args.get("paginate")

    if not args.get("prs_mode"):
        prs_mode = "non_rts"
    else:
        prs_mode = args.get("prs_mode")

    results = dict()

    if unique_drug_ids:
        unique_drug_ids = unique_drug_ids.split(",")
    else:
        if args.get("drug_status") is None:
            return error(1001, "Missing Parameter(s): drug_status.")
        drug_status = int(args.get("drug_status"))
        try:
            logger.info("get_prs_drug_images: No unique_drug_id found so fetching next pending unique_drug_id")
            # This function will fetch next pending unique_drug_id from prs_details table
            unique_drug_ids = [db_get_next_unique_drug_id_based_on_status(drug_status=drug_status)]
            logger.info("get_prs_drug_images: Found unique_drug_id: " + str(unique_drug_ids))
        except DoesNotExist:
            return error(12001)

    # method to get drug data based on unique_drug_id
    try:
        logger.info("get_prs_drug_images: fetching prs_drug_data for unique_drug_id:" + str(unique_drug_ids))
        drug_data = db_get_prs_drug_data(unique_drug_ids=unique_drug_ids)
        logger.info("get_prs_drug_images: fetched prs_drug_data for unique_drug_id:" + str(unique_drug_ids))
        for record in drug_data:
            if not record["unique_drug_id"] in results:
                if record["face_1_selected_images"] is not None:
                    record["face_1_selected_images"] = list(map(lambda x: image_convert(str(x)), record["face_1_selected_images"].split(",")))
                else:
                    record["face_1_selected_images"] = []
                if record["face_2_selected_images"] is not None:
                    record["face_2_selected_images"] = list(map(lambda x: image_convert(str(x)), record["face_2_selected_images"].split(",")))
                else:
                    record["face_2_selected_images"] = []
                if record["side_face_selected_images"] is not None:
                    record["side_face_selected_images"] = list(map(lambda x: image_convert(str(x)), record["side_face_selected_images"].split(",")))
                else:
                    record["side_face_selected_images"] = []
                logger.info(
                    "get_prs_drug_images: fetching slot_images for unique_drug_id: " + str(record["unique_drug_id"]))
                available_crop_images_count, crop_images = \
                    db_get_pvs_drug_crop_images(prs_mode=prs_mode,
                                                unique_drug_id=record["unique_drug_id"],
                                                paginate=paginate)

                record["available_crop_images_count"] = available_crop_images_count
                record["crop_images"] = crop_images
                logger.info("get_prs_drug_images: fetched slot_images for unique_drug_id: {}, "
                             "available_crop_images_count: {}".format(str(record["unique_drug_id"]),
                                                                      str(record["available_crop_images_count"])))
                results[record["unique_drug_id"]] = record
        logger.info("get_prs_drug_images: prs_drug_data and slot_images: " + str(results))
    except DoesNotExist:
        return error(1004, ": unique_drug_id - {}.".format(unique_drug_ids))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_prs_drug_images {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_prs_drug_images {}".format(e))
        return error(1000, "Error in get_prs_drug_images: " + str(e))

    return create_response(results)


@log_args_and_response
@validate(required_fields=["company_id"])
def get_prs_data(dict_prs_info):
    """
    Get PRSDrugData for the given mode and company_id

    @args:
        dict_prs_info (dict): The key containing the filter_fields

    @return:
       json: success or the failure response along details of the PrsDrugData for the given mode and company_id
   """

    company_id = dict_prs_info.get("company_id")
    filter_fields = dict_prs_info.get("filter_fields", None)
    sort_fields = dict_prs_info.get("sort_fields", None)
    paginate = dict_prs_info.get("paginate", None)
    mode = dict_prs_info.get("mode", constants.NON_RTS_MODE)

    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, "Missing key(s) in paginate.")
    try:
        # get the value of the MINIMUM_IMAGE_COUNT_FOR_PRS from the company_setting table.
        required_count = get_count_from_company_setting(company_id=company_id)

        logger.debug("In GetPRSData")
        response = get_prs_data_dao(
            sort_fields=sort_fields,
            filter_fields=filter_fields,
            paginate=paginate,
            mode=mode,
            required_count=required_count
        )

        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_prs_data {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_prs_data {}".format(e))
        return error(1000, "Error in get_prs_data: " + str(e))


@log_args_and_response
def unlink_mapped_crops(unlink_info):
    try:
        remote_tech_slot_details_ids = unlink_info.get('remote_tech_slot_details_id', None)
        unique_drug_id = unlink_info.get('unique_drug_id', None)
        images_to_unlink = unlink_info.get('images_to_unlink', None)
        face_1_list = list()
        face_2_list = list()
        side_face_list = list()
        if remote_tech_slot_details_ids:
            remote_tech_slot_ids = get_remote_tech_slot_id_dao(remote_tech_slot_details_ids=remote_tech_slot_details_ids)
            logger.info("In unlink_mapped_crops remote_tech_slot_details_ids: {}".format(remote_tech_slot_ids))
        else:
            remote_tech_slot_ids, remote_tech_slot_details_ids = \
                get_remote_tech_slot_id_from_prs_unique_drug_and_images(unique_drug_id, images_to_unlink)

        status = update_status_in_remote_tech_slot_dao(remote_tech_ids=remote_tech_slot_ids)

        if status:
            update_status = update_status_in_remote_tech_slot_details_dao(remote_tech_slot_details_ids=remote_tech_slot_details_ids)

        if images_to_unlink and unique_drug_id:
            query = get_prs_images_from_unique_drug_id(unique_drug_id=unique_drug_id)
            if query['face1'] is not None:
                face_1_list = list(map(lambda x: image_convert(str(x)), query['face1'].split(',')))
            if query['face2'] is not None:
                face_2_list = list(map(lambda x: image_convert(str(x)), query['face2'].split(',')))
            if query['side_face'] is not None:
                side_face_list = list(map(lambda x: image_convert(str(x)), query['side_face'].split(',')))

            for image in images_to_unlink:
                if image in face_1_list:
                    face_1_list.remove(image)
                elif image in face_2_list:
                    face_2_list.remove(image)
                elif image in side_face_list:
                    side_face_list.remove(image)

            face_1 = ','.join(face_1_list) if face_1_list else None
            face_2 = ','.join(face_2_list) if face_2_list else None
            side_face = ','.join(side_face_list) if side_face_list else None
            logger.info("In unlink_mapped_crops: face_1: {}, face2: {}, side_face:{}".format(face_1, face_2, side_face))

            updated_status = update_prs_images_for_unique_drug(face_1, face_2, side_face, unique_drug_id)

        return create_response(True)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error while fetching unlink_mapped_crops: " + str(e))
        raise


@log_args_and_response
def get_filters_prs():
    try:
        drug_list, color_list, status_list, faces_list = get_filters_for_prs()
        response = {
            "drug_list": drug_list,
            "color_list": color_list,
            "status_list": status_list,
            "faces_list": faces_list
        }

        return create_response(response)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error while fetching unlink_mapped_crops: " + str(e))
        raise