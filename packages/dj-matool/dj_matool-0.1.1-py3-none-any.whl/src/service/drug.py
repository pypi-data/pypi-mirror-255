# other imports
import os
import sys
import json
import settings
from src import constants
from dosepack.base_model.base_model import db
from datetime import date, timedelta, datetime
from dosepack.validation.validate import validate
from dosepack.utilities.utils import last_day_of_month, SCAN_ENTITY_DICT, log_args_and_response, logger
from src.exc_thread import ExcThread
from src.service.drug_search import find_required_dict_from_entity, get_ndc_list_for_barcode, get_ndq_for_ndc_list
from dosepack.utilities.utils import get_current_date_time
from src.dao.alternate_drug_dao import get_alternate_drug_data_dao
from src.dao.canister_testing_dao import validate_canister_id_with_company_id
from src.dao.ext_change_rx_dao import db_get_pack_ids_by_pack_display_id_dao
from src.service.volumetric_analysis import get_available_drugs_for_recommended_canisters
from src.model.model_drug_master import DrugMaster
from src.service.misc import get_token
from src.service.pack import update_drug_status
from sync_drug_data.update_drug_data import get_missing_drug_images, get_missing_drug_data

from sync_drug_data.update_drug_data import get_missing_drug_images
from dosepack.error_handling.error_handler import error, create_response
from peewee import InternalError, IntegrityError, DoesNotExist, DataError
from src.exceptions import PharmacySoftwareCommunicationException, PharmacySoftwareResponseException
from dosepack.utilities.utils import SCAN_ENTITY_DICT, log_args_and_response

# import from service files
from src.service.rph_verification import get_company_user_id_from_token
from src.service.drug_tracker import get_and_insert_canister_replenish_id_in_drug_tracker_data

# import from dao files
from src.dao.batch_dao import get_batch_record
from src.dao.mfd_dao import get_manual_drugs_dao
from src.dao.analysis_dao import get_batch_drugs_dao
from src.dao.device_manager_dao import get_device_type
from src.dao.batch_dao import get_batch_id_from_pack_list
from src.dao.pack_drug_dao import populate_pack_drug_tracker
from src.dao.pack_drug_dao import create_records_in_pack_drug_tracker
from src.dao.generate_canister_dao import get_canister_info_by_canister_id
from src.dao.pack_dao import verify_pack_id_by_system_id_dao, get_no_of_drugs_dao, \
    db_update_slot_details_by_multiple_slot_id_dao, verify_pack_display_id
from src.dao.canister_dao import get_replenish_info_by_drug_usage_status_in_reverse
from src.dao.volumetric_analysis_dao import check_if_drug_dimension_measured_for_ndc, get_drug_dimension_history_dao, \
    get_drug_stock_history
from src.dao.generate_canister_dao import get_available_drug_canister, get_drug_requested_canister_count
from src.dao.drug_dao import fetch_drug_info, get_drug_info_based_on_ndc, search_drug_field_dao, \
    register_powder_pill_daw, get_drug_detail_slotwise_dao, get_drug_image_data_dao, get_lot_no_from_ndc_dao, \
    db_get_alternate_ndcs
from src.dao.mfd_dao import get_mfd_drug_list_, check_drug_dimension_required_for_drug_id, \
    check_drug_dimension_required_for_drug_id_id, db_get_filled_unfilled_slots_of_mfd_canister, \
    db_update_drug_status, db_get_canisters_status_based, db_update_canister_status
from src.dao.pack_dao import db_get_pack_wise_drug_data_dao, get_slots_to_update_pack_wise, \
    get_packs_to_update_drug_mff, get_slots_to_update_mfs, update_slot_details_by_slot_id_dao
from src.dao.canister_dao import get_canister_data_by_drug_and_company_id_dao, get_canister_details_by_canister_id, \
    update_replenish_based_on_device
from src.dao.inventory_dao import get_drug_image_and_id_from_ndc_dao, get_drug_bottle_data_by_filter, \
    get_lot_information_by_filters
from src.dao.drug_tracker_dao import get_filled_unfilled_slots_by_pack_id_and_drug_id, \
    drug_tracker_create_multiple_record, get_slot_details_pack_drug_tracker_data, db_update_drug_tracker_by_slot_id_dao, \
    db_get_drug_tracker_data_by_slot_id_dao, db_update_drug_tracker_by_drug_tracker_id_dao, \
    drug_tracker_create_multiple_record, get_slot_details_pack_drug_tracker_data, db_update_drug_tracker_by_slot_id_dao, \
    db_get_drug_tracker_data_by_slot_id_dao, db_update_drug_tracker_by_drug_tracker_id_dao, \
    update_data_in_drug_tracker_for_canister_tracker, check_case_id_present_in_drug_tracker
from src.dao.patient_dao import get_patient_rx_id_based_on_pack_id_and_drug_id, \
    db_update_patient_rx_for_manual_pack_filling, db_update_patient_rx_data_in_dao
from src.dao.drug_dao import fetch_canister_drug_data_from_canister_ids, get_drug_dao, \
    get_drug_info, get_drug_and_bottle_information_by_drug_id_dao, get_drug_id_list_for_same_configuration_by_drug_id, \
    get_drug_dosage_types_dao, change_status_by_ips_dao, \
    get_batch_drug_not_imported, get_batch_drug_imported, \
    get_drug_stock_by_status, db_get_unique_drugs, db_update_slot_details_for_manual_pack_filling, \
    db_get_txr_and_drug_id_by_ndc_dao
from src.dao.unique_drug_dao import update_unique_drug_based_on_drug_status

# imports from models
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


@log_args_and_response
def get_drug(search_filters):
    """
    Gets drugs information using search filters(and based)

    :param search_filters:
    :return: json
    """

    paginate = search_filters.pop("paginate", None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')
    sort_fields = search_filters.pop("sort_fields", None)
    logger.debug("search filters for drug {}".format(search_filters))
    company_id = search_filters.pop("company_id", None)
    filters = search_filters.pop("filters", {})
    device_id = search_filters.get('device_id')
    canister_search = int(search_filters.pop("canister_search", 0))
    alternate_drugs = list()
    drug_result = list()
    drug_list = []
    canister_lists = []
    canister_list_info_with_qty_dict = dict()
    count = 0
    ndc_list = list()
    alternate_unique_drug_list = list()
    records_from_date = search_filters.pop("records_from_date", None)
    registration_history_data = list()
    inventory_data = list()
    try:

        device_type_id = None
        if device_id:
            device_type_id_query = get_device_type(device_id)
            # find device_type_id for device_id
            for data in device_type_id_query:
                device_type_id = data['device_type_id']

        count, drug_result, ndc_list1 = get_drug_dao(paginate=paginate, sort_fields=sort_fields,
                                                            company_id=company_id, filters=filters,
                                                            canister_search=canister_search)
        change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list1)

        for record in drug_result:
            # get all canister data for drug from list of canister
            record['change_ndc_available'] = True if record['ndc'] in change_ndc_drug_list else False
            record['canister_list_with_qty'] = fetch_canister_drug_data_from_canister_ids(
                    canister_ids=record['canister_ids'], device_id=device_id, device_type_id=device_type_id)
            # fetch history and alternate drug data only if single ndc is filtered
            if filters and filters.get('ndc', None):
                ndc_list.append(record['ndc'])
                if record['alternate_drug_available']:
                    record['alternate_drugs'], alternate_drugs_count = get_alternate_drug_data_dao(drug_id=record['drug_id'],
                                                                                                   company_id=company_id,
                                                                                                   device_id=device_id,
                                                                                                   device_type_id=device_type_id,
                                                                                                   paginate=None)
                    for drug in record['alternate_drugs']:
                        ndc_list.append(drug['ndc'])
                        drug['inventory_count'] = None
                else:
                    record['alternate_drugs'] = list()
                registration_history_data = get_drug_dimension_history_dao(drug_id=record['drug_id'],
                                                                           records_from_date=records_from_date)

                record['registration_history_data'] = registration_history_data.get(record['drug_name'] + ", " + record['ndc'])
                if settings.USE_EPBM:
                    inventory_data = get_current_inventory_data(ndc_list=list(map(int, ndc_list)), qty_greater_than_zero=False)
                record['inventory_count'] = None
                for data in inventory_data:
                    if data['ndc'] == record['ndc']:
                        record['inventory_count'] = data['quantity']
                    for drug in record['alternate_drugs']:
                        if drug['ndc'] == data['ndc']:
                            drug['inventory_count'] = data['quantity']
                            break
                if record['inventory_count']:
                    record['is_in_stock'] = 0 if record["inventory_count"] == 0 else 1
                else:
                    record['is_in_stock'] = None

                drug_stock_history_data = get_drug_stock_history(unique_id_list=[record['unique_drug_id']],
                                                                 records_from_date=records_from_date, company_id=company_id)
                record['drug_stock_history_data'] = drug_stock_history_data.get(record['unique_drug_id'])

            else:
                record['canister_list_with_qty'] = list()
                record['alternate_drugs'] = list()
                record['registration_history_data'] = list()
                record['inventory_count'] = None
                record['drug_stock_history'] = list()

        response = {
            "total_records": count,
            "drugs": drug_result
        }
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_drug_information_from_ips_by_ndc(drug_args):
    try:
        logger.debug("process_rx: fetching token")
        company_id, token_user_id, token_user_name = get_company_user_id_from_token()
        get_missing_drug_images(ndc_list=drug_args["ndc_list"], company_id=drug_args["company_id"],
                                user_id=token_user_id)
        return create_response(True)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown Error while fetching Drug Info: " + str(e))


@log_args_and_response
@validate(required_fields=["ndc", "blacklist"])
def get_drug_information_by_ndc(dict_ndc_info):
    """
    Takes the input argument for ndc search and returns
    all the information which satisfies the criteria or
    matches the ndc search string.

    Args:
        dict_ndc_info (dict): A dict containing search drug string
    Returns:
        list: List of all the drugs which satisfies the search criteria

    Examples:
        >>> get_drug_information_by_drug({"ndc": 1234})

    """
    drug_info = []
    ndc = dict_ndc_info["ndc"]
    blacklist = dict_ndc_info["blacklist"]
    # 14 Mar 16 Abner - Blacklist flag - Y/N
    new_ndc = ""
    if ndc:
        for case in range(0, 4):
            if case == 0:
                new_ndc = ndc
            elif case == 1:
                new_ndc = "0" + ndc[1:11]
            elif case == 2:
                new_ndc = ndc[1:6] + "0" + ndc[6:11]
            else:
                new_ndc = ndc[1:10] + "0" + ndc[10:11]

            cursor = get_drug_info(new_ndc)
            if cursor is None:
                return error(1012)
            drug_info += cursor

            if len(drug_info) > 0:
                break

    return create_response(drug_info, additional_info={"given_ndc": ndc, "matching_ndc": new_ndc})


@validate(required_fields=["drug_name", 'blacklist'])
def get_drug_information_by_drug(dict_info):
    """
    Takes the input argument for drug search and returns
    all the information which satisfies the criteria or
    matches the drug search string.

    Args:
        dict_info (dict): A dict containing search drug string
    Returns:
        list: Returns the list of all the drug information
              which satisfies the search criteria

    Examples:
        >>> get_drug_information_by_drug({"drug": "abc"})

    """
    drug = dict_info["drug_name"]
    unique_drugs = dict_info.get("unique_drugs", False)
    limit = dict_info.get("limit", 20)
    if limit in (0, -1):  # do not apply limit
        limit = None
    blacklist = dict_info["blacklist"]
    # 14 Mar 16 Abner - Blacklist flag - Y/N
    response = get_drug_info(drug, unique_drugs, limit=limit)
    response = create_response(response)
    return response


@validate(required_fields=["scanned_ndc"])
def check_drug_image_and_data_from_formatted_ndc(ndc_dict):
    """
    This function will be used to check if drug image is available for a drug based on its ndc.
    if available then send drug data for the same else return drug id
    :param ndc_dict: Dictionary with ndc from barcode as key
    :return: Data
    """
    scanned_ndc = ndc_dict["scanned_ndc"]

    response_dict = {"is_image_available": False, "drug_data": None, "drug_id": 0, "is_data_matrix_present": False,
                     "expiry_date": None, "lot_number": None}

    print("scanned_ndc: ", scanned_ndc, len(scanned_ndc))
    # if len(scanned_ndc) == 12:
    #     scanned_ndc = "0"+str(scanned_ndc)

    # If length of the input is less than equal to 13, but not including 9 to 11 as it is user entered, 13 is barcode value
    if len(scanned_ndc) in [i for i in range(0, 13) if i not in [9, 10, 11, 12, 13]]:
        return error(9005)

    if len(scanned_ndc) == 10:
        scan_type = SCAN_ENTITY_DICT["user_entered"]

    elif len(scanned_ndc) in [12, 13]:
        scan_type = SCAN_ENTITY_DICT["barcode"]

    else:
        scan_type = SCAN_ENTITY_DICT["data_matrix"]

    response_data = find_required_dict_from_entity(scanned_value=scanned_ndc, entity=scan_type, required_entity="ndc")

    print("Response_data: ", response_data)

    if scan_type == SCAN_ENTITY_DICT["data_matrix"]:
        response_dict["is_data_matrix_present"] = True
        if not response_data["status"]:
            return error(9011)

        try:
            temp_month = response_data["expiry_date"][2:4]
            temp_year = response_data["expiry_date"][0:2]

            complete_expiry_date = temp_month + "-20" + temp_year
        except:
            complete_expiry_date = response_data["expiry_date"]

        response_data["expiry_date"] = complete_expiry_date

        response_dict["lot_data"] = response_data

    if len(scanned_ndc == 11):
        ndc_list = list(scanned_ndc)
    else:
        ndc_list = response_data["ndc"]
    # else:
    #     ndc_list = get_ndc_list_from_scanned_ndc(response_data["ndc"])

    print("NDC list: ", ndc_list)
    for ndc in ndc_list:
        is_image_available, drug_id = get_drug_image_and_id_from_ndc_dao(ndc=ndc)

        print("Response from drug image: ", is_image_available, drug_id)
        response_dict["is_image_available"] = is_image_available

        if drug_id:
            response_dict["drug_id"] = drug_id

        if is_image_available:
            drug_data = get_drug_and_bottle_information_by_drug_id_dao(drug_id)
            response_dict["drug_data"] = drug_data

            if "lot_data" in response_dict:
                response_dict["lot_data"]["ndc"] = ndc
            return create_response(response_dict)

    return create_response(response_dict)


@validate(required_fields=["drug_id", "company_id", "require_canister_data"])
def find_drug_and_bottle_details_from_drug_id(drug_id_dict):
    """
    This function will be used to get the information for the drug and the drug bottle based on the drug id
    :param drug_id_dict: Dictionary with drug id as key
    :return: Drug data
    """

    drug_id = drug_id_dict["drug_id"]
    company_id = drug_id_dict["company_id"]
    require_canister_data = drug_id_dict["require_canister_data"]

    drug_data = get_drug_and_bottle_information_by_drug_id_dao(drug_id)

    required_dict = {"drug_id_list": [drug_id]}
    drug_id_list = get_drug_id_list_for_same_configuration_by_drug_id(required_dict)

    bottle_data = get_drug_bottle_data_by_filter(company_id=company_id, drug_id_list=drug_id_list)

    if require_canister_data:
        canister_data = get_canister_data_by_drug_and_company_id_dao(drug_id_list, company_id)

    lot_data = get_lot_information_by_filters(company_id=company_id, drug_id_list=drug_id_list)

    response_dict = {"drug_data": drug_data, "bottle_data": bottle_data, "lot_data": lot_data}

    if require_canister_data:
        response_dict["canister_data"] = canister_data

    return create_response(response_dict)


def get_drug_dosage_types_and_coating_types():
    """ Returns list of dosage types and coating types"""
    try:
        dosage_types_list = get_drug_dosage_types_dao()
        results = {
            'dosage_types': dosage_types_list,
            'coating_types': constants.COATING_TYPE
        }
        return create_response(results)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_valid_ndc(info_dict):
    """
    returns list of valid ndc from barcode scan data
    :return:
    """
    try:
        company_id = info_dict.get('company_id')
        is_mvc = info_dict.get('is_mvs', False)  # is_mvs = True if user scan canister from MVC screen otherwise it is false
        ndc_allowed = info_dict.get('ndc_allowed', True)
        ndq_required = info_dict.get('ndq_required', False)
        module_id = info_dict.get("module_id")
        ndc_ndq_dict = dict()
        if isinstance(ndc_allowed, str):
            ndc_allowed = json.loads(ndc_allowed)

        ndc_dict = {
            "scanned_ndc": info_dict['ndc'],
            "required_entity": "ndc",
            "user_id": info_dict.get("user_id"),
            "bottle_qty_req": info_dict.get("bottle_qty_req", False),
            "company_id": company_id,
            "ndc_allowed": ndc_allowed,
            "module_id": module_id
        }
        logger.info("In get_valid_ndc: {}".format(ndc_dict))
        ndc_list, drug_scan_type, lot_no, expiration_date, inventory_quantity, case_id, upc, bottle_qty = get_ndc_list_for_barcode(ndc_dict)
        if ndc_list and ndq_required:
            ndc_ndq_dict = get_ndq_for_ndc_list(ndc_list, drug_scan_type)
        response_data = {"ndc_list": ndc_list, "drug_scan_type": drug_scan_type, "lot_number": lot_no,
                         "expiration_date": expiration_date, "inventory_quantity": inventory_quantity, "unique_drug_id": None,
                         "available_canister_count": 0, "requested_canister_count": 0, "required_canister_count": 0,
                         "generate_new_canister": False, "canister_scan": False, "case_id": case_id, "upc": upc,
                         "bottle_qty": bottle_qty, "ndc_ndq_dict": ndc_ndq_dict}
        # if ndc_list and lot_no:
        #     print("lot insertion started")
        #     for item in ndc_list:
        #         txr, drug_id = DrugMaster.db_get_txr_and_drug_id_by_ndc(item)
        #         drug_lot_data = {"lot_number": lot_no,
        #                          "drug_id": drug_id,
        #                          "expiry_date": expiration_date,
        #                          "total_packages": 0,
        #                          "total_quantity": 0,
        #                          "available_quantity": 0,
        #                          "company_id": 3,
        #                          "created_by": info_dict.get("user_id"),
        #                          "modified_by": info_dict.get("user_id")
        #                          }
        #
        #         try:
        #             status = DrugLotMaster.get_or_create(lot_number=lot_no,
        #                                                  drug_id=drug_id,
        #                                                  expiry_date=expiration_date,
        #                                                  defaults=drug_lot_data
        #                                                  )
        #             print(status, "lot inserted")
        #         except Exception as e:
        #             print(e)

        if not ndc_list and (str(info_dict['ndc']).isnumeric() or
                             info_dict['ndc'].startswith(constants.CANISTER_LABEL_PREFIX)):

            canister_id, company_id = parser_scan_canister_qr(info_dict['ndc'], company_id)

            if not canister_id:
                create_response(response_data)

            canister_data = get_canister_details_by_canister_id(canister_id=canister_id, company_id=company_id)
            if canister_data:
                if canister_data["ndc"] and ndq_required:
                    ndc_ndq_dict = get_ndq_for_ndc_list([canister_data["ndc"]])
                response_data['canister_id'] = canister_id
                response_data["ndc_list"] = [canister_data["ndc"]]
                response_data["canister_scan"] = True  # True when canister is scan from MVS Screen
                response_data["expiry_status"] = canister_data["expiry_status"]
                response_data["lot_number"] = canister_data["lot_number"]
                response_data["expiry_date"] = canister_data["expiry_date"]
                response_data["available_quantity"] = canister_data["available_quantity"]
                response_data["drug_scan_type"] = constants.CANISTER_SCAN
                response_data['case_id'] = canister_data['case_id']
                response_data['upc'] = canister_data['upc']
                response_data['canister_id'] = canister_data['id']
                response_data["ndc_ndq_dict"] = ndc_ndq_dict
                return create_response(response_data)

        if ndc_list:
            # check if drug dimension is measured for given ndc
            dimension_exists, drug_data = check_if_drug_dimension_measured_for_ndc(ndc_list=ndc_list, drug_scan_type=drug_scan_type)
            logger.info("In get_valid_ndc Drug dimension is measured or not for ndc:{} unique_drug_data: {}".format(
                dimension_exists, drug_data))

            # if drug dimension not measure for given ndc then pass unique drug id in response data
            if not dimension_exists:
                response_data['unique_drug_id'] = drug_data['unique_drug_id']
                return create_response(response_data)

            # if dimension is measured, it is verified and canister is required then generate request for canister
            if dimension_exists and drug_data['verification_status_id'] == settings.VERIFICATION_DONE_FOR_DRUG:
                # get count of available canister for drug
                available_canister = get_available_drug_canister(company_id=company_id,
                                                                 fndc=drug_data['formatted_ndc'],
                                                                 txr=drug_data['txr'])

                # get requested canister count from generate canister table (requested status in [approved,
                # in progress, pending, Done])
                requested_canister_count = get_drug_requested_canister_count(company_id=company_id,
                                                                             fndc=drug_data['formatted_ndc'],
                                                                             txr=drug_data['txr'])

                response_data['available_canister_count'] = len(available_canister)
                response_data['requested_canister_count'] = requested_canister_count
                response_data['required_canister_count'] = settings.REQUIRED_CANISTER_COUNT
                logger.info("In get_valid_ndc : available_canister_count: {} and requested_canister_count: {},"
                            "required_canister_count: {} for formatted_ndc: {}, txr: {} "
                            .format(len(available_canister), requested_canister_count, settings.REQUIRED_CANISTER_COUNT,
                                    drug_data['formatted_ndc'],
                                    drug_data['txr']))

                if len(available_canister) + requested_canister_count < settings.REQUIRED_CANISTER_COUNT:
                    response_data['generate_new_canister'] = True
                    response_data['unique_drug_id'] = drug_data['unique_drug_id']
            return create_response(response_data)

        return create_response(response_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("An error occurred while fetching ndc list of scanned drug bottle - " + str(e))
        return error(1000, "Unknown error- " + str(e))


@log_args_and_response
@validate(required_fields=['ndc_status_data'])
def change_status_by_ips(drug_data):
    """
    changes the status of drug for given ndcs
    :param drug_data: dict of ndc_list, status
    :return: json
    """
    try:
        with db.transaction():
            ndc_status_dict = drug_data['ndc_status_data']
            change_status_by_ips_dao(ndc_status_dict)

        return create_response({'status': True})
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    finally:
        try:
            update_unique_drug_based_on_drug_status()
        except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
            logger.error(e, exc_info=True)
            return error(2001)


@validate(required_fields=["system_id", "batch_id"])
def get_manual_drugs(search_filters):
    """
    Gives manual drug data based on canister availability and fractional drugs for given pack list

    :param search_filters:
    :return: json
    """
    system_id = search_filters["system_id"]
    batch_id = search_filters["batch_id"]
    try:
        response = get_manual_drugs_dao(batch_id, system_id)
        if response:
            return create_response(response)
    except (IntegrityError, InternalError) as e:
        print(e)
        logger.error(e, exc_info=True)
        return error(2001)


def batch_drugs(company_id, batch_id, system_id, number_of_packs, type_of_drug,
                replenish_required, extra_canister_data=0):
    try:
        if extra_canister_data is not None:
            extra_canister_data = int(extra_canister_data)
        if replenish_required:
            replenish_required = int(replenish_required)
        if type_of_drug:
            type_of_drug = int(type_of_drug)
        logger.info("inside batch_drugs: {} {} {} {} {} {} {} ".format(company_id, batch_id, system_id, number_of_packs, type_of_drug,
                replenish_required, extra_canister_data))
        pack_ids, list_final = get_batch_drugs_dao(company_id, batch_id, system_id, number_of_packs, type_of_drug,
                replenish_required, extra_canister_data)
        response = {
            'pack_ids': pack_ids,
            'drug_data': list_final
        }
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)


@validate(required_fields=["system_id", "company_id"])
def get_batch_drug_details(dict_batch_info):
    logger.info("In get_batch_drug_details")

    try:

        system_id = dict_batch_info['system_id']
        company_id = dict_batch_info['company_id']
        pack_queue = dict_batch_info['pack_queue']
        upcoming_batches = dict_batch_info.get('upcoming_batches', False)
        if dict_batch_info['batch_id']:
            batch_id = json.loads(dict_batch_info['batch_id'])
            if type(batch_id) == int or type(batch_id) == str:
                batch_id = [batch_id]

            batch_data = get_batch_record(batch_id[0])
            batch_status = batch_data.status.id

        logger.info("Input args of get_batch_drug_details {}".format(dict_batch_info))

        if len(dict_batch_info['filter_fields']) > 0:
            filter_fields = json.loads(dict_batch_info['filter_fields'])
        else:
            filter_fields = dict_batch_info['filter_fields']

        if len(dict_batch_info['paginate']) > 0:
            paginate = json.loads(dict_batch_info['paginate'])
        else:
            paginate = dict_batch_info['paginate']

        if len(dict_batch_info['sort_fields']) > 0:
            sort_fields = json.loads(dict_batch_info['sort_fields'])
        else:
            sort_fields = dict_batch_info['sort_fields']

        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        if pack_queue:
            return get_batch_drug_imported(system_id=system_id,
                                           filter_fields=filter_fields, paginate=paginate,
                                           sort_fields=sort_fields)
        else:
            logger.info("get_batch_drug_details {}".format(upcoming_batches))
            return get_batch_drug_not_imported(batch_id=batch_id, filter_fields=filter_fields,
                                               sort_fields=sort_fields, paginate=paginate,
                                               company_id=company_id)

    except ValueError as e:
        logger.error("Error in get_batch_drug_details {}".format(e))
        return error(0)

    except Exception as e:
        logger.error("Error in get_batch_drug_details {}".format(e))
        return error(0)


@log_args_and_response
def get_drug_stock_status(company_id, filter_fields):
    """

    @param args:
    @return:
    """
    results, count, non_paginate_result = get_drug_stock_by_status(company_id, filter_fields)
    response = {"drug_data": results, "total_drugs": count, "drug_id_list": non_paginate_result}
    return create_response(response)


@validate(required_fields=["pack_id"])
def get_unique_drugs(pack_obj):
    """ Takes the pack id  and returns all unique drug present in pack and quantity of those drug.

        Args:
            pack_obj (dict): pack_id(int)

        Returns:
           json

        Examples:
            >>> get_unique_drugs({})
    """
    try:
        data = db_get_unique_drugs(pack_obj["pack_id"])
        return create_response(data)
    except IntegrityError:
        return error(2001)
    except InternalError:
        return error(2001)


@log_args_and_response
def get_no_of_drug_by_pack_id(dict_info):
    """
    Takes the pack_id and returns total no of unique drugs available.

    Args:
    pack_id : dictionary containing pack_id of the pack and system_id
    Returns:
    total no of unique drugs available for the given pack_id.

    Examples:
    >>> get_no_of_drug_by_pack_id(dict_info)

    """
    # todo use system_id to verify pack and then process the request
    pack_id = dict_info["pack_id"]
    system_id = dict_info["system_id"]

    valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
    if not valid_pack:
        return error(1014)
    try:
        response = get_no_of_drugs_dao(pack_id)
        if response is None:
            return error(1004)
        return create_response(response)
    except InternalError:
        return error(2001)


@validate(required_fields=["company_id", "user_id", "ndc", "module"])
@log_args_and_response
def validate_scanned_drug(scanned_data):
    """
    Validated scanned drug bottle to update drugs in packs
    @param scanned_data:
    @return:
    """
    company_id = scanned_data['company_id']
    user_id = scanned_data['user_id']
    batch_id = scanned_data.get('batch_id', None)
    scanned_ndc = (scanned_data['ndc'])
    pack_ids = scanned_data.get('pack_ids', None)
    confirmation = scanned_data.get('confirmation', False)
    module = scanned_data['module']
    mfs_device_id = scanned_data.get('mfs_device_id', None)
    # filled_ndc_list = scanned_data.get('filled_ndc', None)
    mfs_filled_drug = scanned_data.get('mfs_filled_drug', None)
    slot_fill_data = scanned_data.get('slot_fill_data', None)
    daw_flag = scanned_data.get('daw', None)
    to_fill_ndc = scanned_data.get('to_fill_ndc', None)
    # mfs_filled_drug_list: list = list()

    response_data: dict = dict()
    new_ndc: str = str()
    old_ndc: str = str()
    ndc_updated: bool = False
    drug_type: int = int()
    new_drug_info: dict = dict()
    additional_info: dict = dict()
    pack_drugs: dict = dict()
    db_update: dict = dict()
    scanned_fndc: str = str()
    scanned_txr: str = str()
    scanned_drug_id: str = str()
    scanned_drug_brand: str = str()
    drug_dimension_required = False

    try:
        if slot_fill_data:
            slot_fill_data["company_id"] = company_id
            logger.info("slot_fill_data as input for drug_filled: {}".format(slot_fill_data))
            drug_filled(slot_fill_data)
    except Exception as e:
        logger.error("error in slot_fill_data {}".format(e))
        raise e

    scanned_drug = get_drug_info_based_on_ndc(scanned_ndc)
    if not scanned_drug:
        return error(9021)
    for data in scanned_drug:
        # if data['ext_status'] == settings.INVALID_EXT_STATUS:
        #     return error(9024)
        scanned_fndc = data['formatted_ndc']
        scanned_txr = data['txr']
        scanned_drug_id = data['id']
        scanned_drug_brand = data['brand_flag']

    if module == constants.MODULE_PRN_OTHER_RX:
        drug_type, ndc_updated, error_code = validate_drug_for_prn_retail(ndc=scanned_ndc, daw=daw_flag, to_fill_ndc=to_fill_ndc,
                                                              scanned_fndc=scanned_fndc, scanned_txr=scanned_txr)
        if not drug_type:
            return error(error_code)
        new_drug_info = fetch_drug_info(scanned_drug_id, company_id, scanned_ndc)[0]
        response_data = {'drug_type': drug_type,
                         'old_ndc': to_fill_ndc,
                         'new_ndc': scanned_ndc,
                         'ndc_updated': ndc_updated,
                         'new_drug_info': new_drug_info,
                         'additional_info': {}
                         }
        return create_response(response_data)
    if not pack_ids:
        if not mfs_device_id:
            return error(9018)

    # if filled_ndc_list:
    #     if scanned_ndc in filled_ndc_list:
    #         return error(9025)

    if mfs_filled_drug:
        for i in mfs_filled_drug:
            temp = get_drug_info_based_on_ndc(i)
            logger.info(temp)
            for record in temp:
                if scanned_ndc == record['ndc'] or (
                        scanned_fndc == record['formatted_ndc'] and scanned_txr == record['txr']) or scanned_txr == record['txr']:
                    return error(9025)

    if not batch_id:
        batch_id, system_id = get_batch_id_from_pack_list(pack_ids)

    #  create 3 list: list1 will contain all ndc that are in packs (drug type 1)
    #  list2 will contain all the alternate NDC fetched from db for given NDC present in packs (drug type 2)
    #  list 3 will contain all the alternate drug NDC fetched from db for given NDC present in packs (drug type 3)
    #  then check the ndc in input with all the list and find drug type

    logger.info("In validate_scanned_drug: Scanned Drug Data {}".format(scanned_drug))
    if pack_ids:
        pack_drugs, drug_list = db_get_pack_wise_drug_data_dao(pack_ids)
    if mfs_device_id:
        pack_drugs, drug_list = get_mfd_drug_list_(batch_id, mfs_device_id)
        drug_dimension_required, no_of_canister = check_drug_dimension_required_for_drug_id_id(batch_id=batch_id,
                                                                            fndc=scanned_fndc,
                                                                            txr=scanned_txr)
    try:
        alternate_drug_info = dict()
        if pack_drugs:
            if scanned_ndc in drug_list:
                drug_type = constants.SAME_NDC
                new_ndc = scanned_ndc
                old_ndc = scanned_ndc
                new_drug = scanned_drug_id
                ndc_updated = False
                new_drug_info = fetch_drug_info(new_drug, company_id, new_ndc)[0]

            else:
                for data in pack_drugs:
                    logger.info("In validate_scanned_drug: Pack Drug consideration {}".format(data))
                    if scanned_fndc == data['formatted_ndc'] and scanned_txr == data['txr']:
                        logger.info("In validate_scanned_drug: Different packaging code found {}".format(data))

                        new_ndc = scanned_ndc
                        old_ndc = data['ndc']
                        new_drug = scanned_drug_id
                        old_drug = data['id']
                        drug_type = constants.SAME_DRUG

                        # if db_update:
                        ndc_updated = True
                        new_drug_info = fetch_drug_info(new_drug, company_id, new_ndc)[0]
                        additional_info = {"updated_pack_display_ids": db_update}
                        break

                    elif scanned_txr and data['txr']:
                        if str(scanned_txr) == data['txr']:
                            logger.info("Alternate drug scan found")
                            if scanned_drug_brand == settings.BRAND_FLAG:
                                return error(9023)
                            if data['brand_flag'] == settings.BRAND_FLAG:
                                return error(9026)

                            if data['brand_flag'] != settings.GENERIC_FLAG or scanned_drug_brand != settings.GENERIC_FLAG:
                                return error(9023)
                            if data['daw_code'] == 1:
                                return error(9022)
                            drug_type = constants.ALTERNATE_DRUG
                            new_drug = scanned_drug_id

                            old_drug = data['id']
                            old_ndc = data['ndc']
                            new_ndc = scanned_ndc
                            new_drug_info = fetch_drug_info(new_drug, company_id, new_ndc)[0]

                            alternate_drug_info["drug_type"] = drug_type
                            alternate_drug_info["old_ndc"] = old_ndc
                            alternate_drug_info["new_ndc"] = new_ndc
                            alternate_drug_info["new_drug_info"] = new_drug_info

                            if confirmation:
                                # Todo: For the current changes we comment the below code
                                # if pack_ids:
                                #     db_update = update_alternate_drug_by_module(company_id=company_id, user_id=user_id,
                                #                                                 batch_id=batch_id, new_drug=new_drug,
                                #                                                 old_drug=old_drug,
                                #                                                 module=module, pack_ids=pack_ids)
                                # if mfs_device_id:
                                #     db_update = update_alternate_drug_by_module(company_id=company_id, user_id=user_id,
                                #                                                 batch_id=batch_id, new_drug=new_drug,
                                #                                                 old_drug=old_drug,
                                #                                                 module=module)
                                # if db_update:
                                ndc_updated = True
                                additional_info = db_update
                                alternate_drug_info["ndc_updated"] = ndc_updated
                                alternate_drug_info["additional_info"] = additional_info

                                break

        if drug_type == constants.SAME_NDC:
            response_data = {'drug_type': drug_type,
                             'old_ndc': old_ndc,
                             'new_ndc': new_ndc,
                             'ndc_updated': ndc_updated,
                             'new_drug_info': new_drug_info,
                             'additional_info': additional_info
                             }
        elif drug_type == constants.SAME_DRUG:
            response_data = {'drug_type': drug_type,
                             'old_ndc': old_ndc,
                             'new_ndc': new_ndc,
                             'ndc_updated': ndc_updated,
                             'new_drug_info': new_drug_info,
                             'additional_info': additional_info
                             }
        elif drug_type == constants.ALTERNATE_DRUG:
            if not confirmation:
                # response_data = {'drug_type': drug_type,
                #                  'old_ndc': old_ndc,
                #                  'new_ndc': new_ndc,
                #                  'ndc_updated': ndc_updated,
                #                  'new_drug_info': new_drug_info,
                #                  'additional_info': additional_info
                #                  }
                response_data = {'drug_type': alternate_drug_info["drug_type"],
                                 'old_ndc': alternate_drug_info["old_ndc"],
                                 'new_ndc': alternate_drug_info["new_ndc"],
                                 'ndc_updated': ndc_updated,
                                 'new_drug_info': alternate_drug_info["new_drug_info"],
                                 'additional_info': additional_info
                                 }
            if confirmation:
                # response_data = {'drug_type': drug_type,
                #                  'old_ndc': old_ndc,
                #                  'new_ndc': new_ndc,
                #                  'ndc_updated': ndc_updated,
                #                  'new_drug_info': new_drug_info,
                #                  'additional_info': additional_info
                #                  }
                response_data = {'drug_type': alternate_drug_info["drug_type"],
                                 'old_ndc': alternate_drug_info["old_ndc"],
                                 'new_ndc': alternate_drug_info["new_ndc"],
                                 'ndc_updated': alternate_drug_info["ndc_updated"],
                                 'new_drug_info': alternate_drug_info["new_drug_info"],
                                 'additional_info': alternate_drug_info["additional_info"]
                                 }
                if mfs_device_id:
                    drug_dimension_required, no_of_canister = check_drug_dimension_required_for_drug_id_id(
                        batch_id=batch_id,
                        fndc=scanned_fndc,
                        txr=scanned_txr,
                        confirmation=confirmation)
        else:
            return error(9021)

        if mfs_device_id:
            response_data["drug_dimension_required"] = drug_dimension_required
            if drug_dimension_required:
                # response_data["count"] = count
                response_data["no_of_canister"] = no_of_canister

        return create_response(response_data)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in validate_scanned_drug: {}".format(e))
        return error(2001)
    except PharmacySoftwareCommunicationException as e:
        logger.error("error in validate_scanned_drug: {}".format(e))
        return error(7001)
    except PharmacySoftwareResponseException as e:
        logger.error("error in validate_scanned_drug: {}".format(e))
        return error(7001)
    except Exception as e:
        logger.error("error in validate_scanned_drug: {}".format(e))
        return error(2001)


@log_args_and_response
def drug_filled(drug_filled_data):
    """
    insert the data into drug_tracker
    """
    logger.info("Inside the drug_filled")

    try:
        token = get_token()
        ndc = drug_filled_data["ndc"]
        user_id = drug_filled_data["user_id"]
        system_id = drug_filled_data["system_id"]
        # drug_type = drug_filled_data["drug_type"]
        module_id = drug_filled_data["module_id"]
        lot_number = drug_filled_data["lot_number"]
        company_id = drug_filled_data["company_id"]
        expiry_date = drug_filled_data.get("expiry", None)
        case_id = drug_filled_data.get("case_id", None)
        """
        commented the below function as it is not used in the current changes
        as because of this api taking too much time
        """
        # case_id_present = check_case_id_present_in_drug_tracker(case_id) if case_id else None

        if expiry_date is not None:
            if isinstance(expiry_date, str):
                if "-" not in expiry_date or expiry_date == "0":
                    return error(1020, 'Invalid expiry_date')
            else:
                return error(1020, 'Invalid expiry_date, not str')

        if module_id == constants.PDT_MVS_MANUAL_FILL or module_id == constants.PDT_PACK_FILL_WORKFLOW or module_id == constants.PDT_PRN_FILL_WORKFLOW or module_id == constants.PDT_FILL_ERROR_WORKFLOW:

            fill_data = drug_filled_data.get("fill_data", None)
            canister_id = drug_filled_data.get("canister_id", None)
            scan_type = drug_filled_data.get("drug_scan_type", None)

            pack_info = dict()
            patient_rx_status = None
            slot_details_status = None
            drug_tracker_status = None

            """
            commented the below code block because to handle the expiry_date case proper development has been done 
            """
            # if expiry_date is not None:
            #     expiry_month = int(expiry[0])
            #     expiry_year = int(expiry[1])
            #     expiry_date_for_testing = last_day_of_month(date(expiry_year, expiry_month, 1))
            #
            #     if expiry_date_for_testing <= date.today() + timedelta(settings.TIME_DELTA_FOR_EXPIRED_CANISTER):
            #         return error(21003)

            # to get the correct format of expiry_date
            # if '-' not in expiry_date:
            #     return error(21003)

            if expiry_date is not None:
                format = "%m-%Y"
                try:
                    res = bool(datetime.strptime(expiry_date, format))
                except ValueError:
                    return error(21003)

            if fill_data:
                # fetch txr, drug_id of scanned_drug
                txr, drug_id = db_get_txr_and_drug_id_by_ndc_dao(ndc)
                logger.info("value of txr {}, drug_id {}".format(txr, drug_id))

                input_args = {"txr": txr,
                              "pack_info": fill_data,
                              "scanned_drug": drug_id,
                              "scan_type": scan_type,
                              "case_id": case_id,
                              "canister_id": canister_id,
                              "module_id": module_id
                              }
                drug_lot_master_args = {
                    "drug_id": drug_id,
                    "created_by": user_id,
                    "modified_by": user_id,
                    "lot_number": lot_number,
                    "company_id": company_id,
                    "expiry_date": expiry_date,
                    "case_id": case_id,
                    # "case_id_present": case_id_present
                }
                drug_lot_master_id = None
                with db.transaction():
                    # fetch slot_detail whether slots are filled or not for given pack_ids
                    slot_details_data = get_filled_unfilled_slots_by_pack_id_and_drug_id(input_args, drug_lot_master_args)
                    logger.info("slot_details_data {}".format(slot_details_data))

                    # create the records for drug_tracker table
                    for pack_id, pack_data in slot_details_data.items():
                        old_drug_list = list()
                        patient_rx_info = dict()
                        required_quantity = int()
                        slot_id_list: list = list()
                        drug_tracker: list = list()
                        drug_tracker_info_list = list()
                        pack_drug_tracker_details = list()
                        for slot_number, slot_data in pack_data.items():
                            if not slot_data["same_drug"]:
                                slot_id_list.append(slot_data["slot_id"])

                                pack_drug_tracker_info = {
                                    "module": module_id,
                                    "created_by": user_id,
                                    "updated_drug_id": drug_id,
                                    "slot_details_id": slot_data["slot_id"],
                                    "created_date": get_current_date_time(),
                                    "previous_drug_id": slot_data["old_drug_id"]
                                }

                                pack_drug_tracker_details.append(pack_drug_tracker_info)

                                if slot_data["old_drug_id"] not in old_drug_list:
                                    old_drug_list.append(slot_data["old_drug_id"])


                            required_quantity += slot_data["filled_quantity"]

                            drug_tracker_data = {"drug_tracker_id": slot_data["drug_tracker_id"],
                                                 "drug_quantity": slot_data["filled_quantity"],
                                                 "canister_tracker_id": None
                                                 }
                            drug_tracker_info_list.append(drug_tracker_data)

                        if canister_id:
                            canister_id = int(canister_id)
                            input_args = {
                                "canister_id": canister_id,
                                "required_quantity": required_quantity,
                                "drug_tracker_info_list": drug_tracker_info_list
                            }
                            drug_tracker = get_and_insert_canister_replenish_id_in_drug_tracker_data(input_args)

                        if old_drug_list:
                            patient_rx_info[pack_id] = old_drug_list

                        # insert record in pack_drug_tracker
                        if pack_drug_tracker_details and slot_details_status:
                            logger.info("In drug_filled: pack_drug_tracker_details {}".format(pack_drug_tracker_details))
                            pack_drug_tracker_status = populate_pack_drug_tracker(pack_drug_tracker_details)

                        if drug_tracker_info_list:
                            status = update_data_in_drug_tracker_for_canister_tracker(drug_tracker_info_list)

                        # update drug_id in patient_rx table
                        if patient_rx_info:
                            logger.info("In drug_filled: patient_rx_info {}".format(patient_rx_info))
                            patient_rx_data = get_patient_rx_id_based_on_pack_id_and_drug_id(patient_rx_info)
                            patient_rx_ids = patient_rx_data[pack_id]
                            for patient_rx_id in patient_rx_ids:
                                if patient_rx_id:
                                    update_dict = {"drug_id": drug_id}
                                    patient_rx_status = db_update_patient_rx_data_in_dao(update_dict=update_dict,
                                                                                         patient_rx_id=patient_rx_id
                                                                                         )
                    if required_quantity:
                        param = {
                            "drug_id": drug_id,
                            "is_in_stock": 1,
                            "token": token,
                            "user_id": user_id

                        }
                        exception_list = []
                        threads = []
                        if settings.USE_EPBM:
                            t = ExcThread(exception_list, target=update_drug_status,
                                          args=[param])
                            threads.append(t)
                            t.start()

                    return create_response(True)
            else:
                return error(21004)
        elif module_id == constants.PDT_MFD_ALTERNATE:
            action = drug_filled_data["action"]
            valid_actions = ['filled', 'pending']

            if action not in valid_actions:
                return error(1020, 'Action is not valid. Valid Actions: {}.'.format(valid_actions))

            if action == "filled":
                fill_data = drug_filled_data.get("fill_data", None)
                canister_id = drug_filled_data.get("canister_id", None)
                scan_type = drug_filled_data.get("drug_scan_type", None)

                slot_details_status = None
                drug_tracker_status = None

                """
                commented the below code block because to handle the expiry_date case proper development has been done 
                """
                # if expiry_date is not None:
                #     expiry = expiry_date.split("-")
                #     expiry_month = int(expiry[0])
                #     expiry_year = int(expiry[1])
                #     expiry_date_for_testing = last_day_of_month(date(expiry_year, expiry_month, 1))
                #
                #     if expiry_date_for_testing <= date.today() + timedelta(settings.TIME_DELTA_FOR_EXPIRED_CANISTER):
                #         return error(21003)

                if fill_data:
                    mfd_analysis_info = dict()

                    # fetch txr, drug_id of scanned_drug
                    txr, drug_id = db_get_txr_and_drug_id_by_ndc_dao(ndc)
                    logger.info("In drug_filled: for mfd filled action value of txr {}, drug_id {}".format(txr, drug_id)
                                )

                    for mfd_analysis_id, mfd_analysis_slot_data in fill_data.items():
                        mfd_analysis_info[mfd_analysis_id] = {
                            "slots_to_filled": mfd_analysis_slot_data["slots_to_filled"],
                            "overwrite_slots": mfd_analysis_slot_data["overwrite_slots"]
                        }

                    input_args = dict()
                    input_args["txr"] = txr
                    input_args["scanned_drug"] = drug_id
                    input_args["mfd_analysis_info"] = mfd_analysis_info

                    mfd_analysis_data = db_get_filled_unfilled_slots_of_mfd_canister(input_args)
                    logger.info("In drug_filled: mfd_analysis_data: {}".format(mfd_analysis_data))

                    analysis_ids: set = set()
                    analysis_details_ids: set = set()

                    with db.transaction():

                        for mfd_analysis_id, mfd_analysis_slot_data in mfd_analysis_data.items():
                            slot_id_list: list = list()
                            drug_tracker: list = list()
                            old_drug_list: list = list()
                            patient_rx_info: dict = dict()
                            required_quantity: int = int()
                            drug_tracker_info_list: list = list()
                            pack_drug_tracker_details: list = list()
                            slot_id_list_for_is_overwrite: list = list()

                            analysis_ids.add(int(mfd_analysis_id))

                            for mfd_slot_number, mfd_slot_data in mfd_analysis_slot_data.items():
                                drug_tracker_data: dict = dict()

                                analysis_details_ids.add(int(mfd_slot_data["mfd_analysis_details_id"]))

                                if not mfd_slot_data["same_drug"]:
                                    # update_dicts = {"drug_id": drug_id}
                                    # slot_details_status = update_slot_details_by_slot_id_dao(update_dicts,
                                    #                                                          mfd_slot_data["slot_id"]
                                    #                                                          )

                                    slot_id_list.append(mfd_slot_data["slot_id"])

                                    # if slot_details_status:
                                    pack_drug_tracker_info: dict = dict()
                                    pack_drug_tracker_info["module"] = module_id
                                    pack_drug_tracker_info["created_by"] = user_id
                                    pack_drug_tracker_info["updated_drug_id"] = drug_id
                                    pack_drug_tracker_info["created_date"] = get_current_date_time()
                                    pack_drug_tracker_info["slot_details_id"] = mfd_slot_data["slot_id"]
                                    pack_drug_tracker_info["previous_drug_id"] = mfd_slot_data["old_drug_id"]

                                    pack_drug_tracker_details.append(pack_drug_tracker_info)

                                    if mfd_slot_data["old_drug_id"] not in old_drug_list:
                                        old_drug_list.append(mfd_slot_data["old_drug_id"])
                                        patient_rx_info[mfd_slot_data["pack_id"]] = old_drug_list

                                drug_tracker_data["drug_id"] = drug_id
                                drug_tracker_data["created_by"] = user_id
                                drug_tracker_data["canister_id"] = canister_id
                                drug_tracker_data["canister_tracker_id"] = None
                                drug_tracker_data["comp_canister_tracker_id"] = None
                                drug_tracker_data["pack_id"] = mfd_slot_data["pack_id"]
                                drug_tracker_data["slot_id"] = mfd_slot_data["slot_id"]
                                drug_tracker_data["filled_at"] = settings.FILLED_AT_DICT[module_id]
                                drug_tracker_data["drug_quantity"] = mfd_slot_data["required_quantity"]
                                drug_tracker_data["expiry_date"] = expiry_date
                                drug_tracker_data["lot_number"] = lot_number

                                required_quantity += mfd_slot_data["required_quantity"]

                                if mfd_slot_number in fill_data[mfd_analysis_id]["overwrite_slots"]:
                                    # update_dict = {"is_overwrite": 1}
                                    # status = db_update_drug_tracker_by_slot_id_dao(update_dict,
                                    #                                                mfd_slot_data["slot_id"]
                                    #                                                )
                                    slot_id_list_for_is_overwrite.append(mfd_slot_data["slot_id"])

                                drug_tracker_data["is_overwrite"] = 0
                                drug_tracker_data["scan_type"] = scan_type

                                if not canister_id:
                                    # Now we are going to use bottle level inventory .That's why if canister_id is
                                    # not available then it inserts bottle_id(case_id) instead if drug_lot_master
                                    drug_tracker_data["case_id"] = case_id
                                    #
                                    # drug_lot_master_id = crud_process_for_drug_lot_master(drug_lot_master_args)
                                    #
                                    # drug_tracker_data["drug_lot_master_id"] = drug_lot_master_id

                                drug_tracker_info_list.append(drug_tracker_data)

                            if canister_id:
                                canister_id = int(canister_id)
                                input_args: dict = dict()
                                input_args["canister_id"] = canister_id
                                input_args["required_quantity"] = required_quantity
                                input_args["drug_tracker_info_list"] = drug_tracker_info_list
                                drug_tracker = get_and_insert_canister_replenish_id_in_drug_tracker_data(input_args)

                                logger.info("In drug_filled drug_tracker_info_list {}".format(drug_tracker))

                            # update the is_overwrite column in drug_tracker
                            if slot_id_list_for_is_overwrite:
                                logger.info(
                                    "In drug_filled: slot_id_list_for_is_overwrite to update is_overwrite status {}"
                                    .format(slot_id_list_for_is_overwrite))
                                update_dict: dict = dict()
                                update_dict["is_overwrite"] = 1
                                update_dict["modified_date"] = get_current_date_time()
                                drug_tacker_update_status = db_update_drug_tracker_by_slot_id_dao(update_dict,
                                                                                                  slot_id_list_for_is_overwrite
                                                                                                  )

                            # update the drug_id column in slot_details
                            if slot_id_list:
                                logger.info("In drug_filled: slot_id_list to update drug_ids during MFD filling{}"
                                            .format(slot_id_list))
                                update_dict: dict = dict()
                                update_dict["drug_id"] = drug_id
                                slot_details_status = db_update_slot_details_by_multiple_slot_id_dao(update_dict,
                                                                                                     slot_id_list)

                            # insert record in pack_drug_tracker
                            if pack_drug_tracker_details and slot_details_status:
                                logger.info(
                                    "In drug_filled: pack_drug_tracker_details at MFD filling {}"
                                    .format(pack_drug_tracker_details))
                                pack_drug_tracker_status = populate_pack_drug_tracker(pack_drug_tracker_details)

                            # insert records in drug_tracker
                            if drug_tracker_info_list:
                                logger.info(
                                    "In drug_filled: drug_tracker_info_list at MFD filling {}"
                                    .format(drug_tracker_info_list))
                                drug_tracker_status = drug_tracker_create_multiple_record(insert_dict=drug_tracker_info_list
                                                                                          )
                            # elif drug_tracker:
                            #     logger.info(
                            #         "In drug_filled: drug_tracker {}".format(drug_tracker))
                            #     drug_tracker_status = drug_tracker_create_multiple_record(insert_dict=drug_tracker)

                            # update drug_id in patient_rx table
                            if patient_rx_info:
                                logger.info("In drug_filled: patient_rx_info at MFD filling{}".format(patient_rx_info))
                                patient_rx_data = get_patient_rx_id_based_on_pack_id_and_drug_id(patient_rx_info)
                                for pack_id, patient_rx_ids in patient_rx_data.items():
                                    for patient_rx_id in patient_rx_ids:
                                        if patient_rx_id:
                                            update_dict = {"drug_id": drug_id}
                                            patient_rx_status = db_update_patient_rx_data_in_dao(update_dict=update_dict,
                                                                                                 patient_rx_id=patient_rx_id
                                                                                                 )

                        # update the mfd_canister and mfd_drug status in mfd_analysis and mfd_analysis_details
                        if drug_tracker_status:
                            logger.info("In drug_filled: action: filled: analysis_ids: {}".format(analysis_ids))
                            logger.info("In drug_filled: action: filled: analysis_details_ids: {}".format(
                                analysis_details_ids))
                            status_id = constants.MFD_DRUG_FILLED_STATUS
                            status = db_update_drug_status(list(analysis_details_ids), status_id)

                            pending_canisters_analysis = db_get_canisters_status_based(list(analysis_ids),
                                                                                       [constants.MFD_DRUG_PENDING_STATUS])

                            logger.info("In drug_filled: pending_canisters_analysis: {}".format(pending_canisters_analysis))

                            filled_canisters_analysis = analysis_ids - pending_canisters_analysis
                            # status_id = constants.MFD_DRUG_FILLED_STATUS
                            logger.info("In drug_filled: filled_canisters_analysis: {}".format(filled_canisters_analysis))
                            if filled_canisters_analysis:
                                update_canister_status = db_update_canister_status(list(filled_canisters_analysis),
                                                                                   constants.MFD_CANISTER_FILLED_STATUS,
                                                                                   user_id)
                                logger.info(
                                    "In drug_filled: update_canister_status: {}".format(update_canister_status))

                        if settings.USE_EPBM:
                            param = {
                                "drug_id": drug_id,
                                "is_in_stock": 1,
                                "token": token,
                                "user_id": user_id
                            }
                            exception_list = []
                            threads = []
                            t = ExcThread(exception_list, target=update_drug_status,
                                          args=[param])
                            threads.append(t)
                            t.start()

                        return create_response(True)
                else:
                    return error(21004)
            elif action == "pending":
                # user_id = drug_filled_data["user_id"]
                # system_id = drug_filled_data["system_id"]
                # drug_type = drug_filled_data["drug_type"]
                fill_data = drug_filled_data.get("fill_data", None)

                if fill_data:
                    analysis_ids: set = set()
                    analysis_details_ids: set = set()

                    for ndc, mfd_data in fill_data.items():
                        txr, drug_id = db_get_txr_and_drug_id_by_ndc_dao(ndc)
                        logger.info(
                            "In drug_filled: for mfd pending action value of txr {}, drug_id {}".format(txr, drug_id))

                        mfd_analysis_info: dict = dict()
                        for mfd_analysis_id, mfd_analysis_slot_data in mfd_data.items():
                            mfd_analysis_info[mfd_analysis_id] = {
                                "slots_to_unfilled": mfd_analysis_slot_data["slots_to_unfilled"]
                            }

                        input_args = dict()
                        input_args["txr"] = txr
                        input_args["scanned_drug"] = drug_id
                        input_args["mfd_analysis_info"] = mfd_analysis_info

                        mfd_analysis_data = db_get_filled_unfilled_slots_of_mfd_canister(input_args)
                        logger.info("In drug_filled: mfd_analysis_data: {}".format(mfd_analysis_data))

                        for mfd_analysis_id, mfd_analysis_slot_data in mfd_analysis_data.items():

                            analysis_ids.add(int(mfd_analysis_id))

                            for mfd_slot_number, mfd_slot_data in mfd_analysis_slot_data.items():

                                analysis_details_ids.add(int(mfd_slot_data["mfd_analysis_details_id"]))

                                slot_id = mfd_slot_data["slot_id"]

                                drug_tracker_data = db_get_drug_tracker_data_by_slot_id_dao(slot_id)

                                for record in drug_tracker_data:
                                    drug_tracker_id = record["id"]
                                    drug_lot_master_id = record["drug_lot_master_id"]
                                    drug_tracker_quantity = record["drug_quantity"]

                                    drug_tracker_update_dict = dict()
                                    drug_tracker_update_dict["is_overwrite"] = 2
                                    drug_tracker_update_dict["modified_date"] = get_current_date_time()
                                    status = db_update_drug_tracker_by_drug_tracker_id_dao(drug_tracker_update_dict,
                                                                                           [drug_tracker_id]
                                                                                           )

                    logger.info("In drug_filled: action: pending: analysis_ids: {}".format(analysis_ids))
                    logger.info("In drug_filled: action: pending: analysis_details_ids: {}".format(
                        analysis_details_ids))
                    if analysis_ids and analysis_details_ids:
                        status_id = constants.MFD_DRUG_PENDING_STATUS
                        status = db_update_drug_status(list(analysis_details_ids), status_id)

                        update_canister_status = db_update_canister_status(list(analysis_ids),
                                                                           constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                                           user_id)
                        logger.info("In drug_filled:action = pending, update_canister_status: {}".format(
                            update_canister_status))

                    return create_response(True)
                else:
                    return error(21004)
    except Exception as e:
        logger.error("error in drug_filled {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in drug_filled: exc_type - {exc_type}, filename - {filename}, line - "
            f"{exc_tb.tb_lineno}")
        return error(2001)


@log_args_and_response
def last_scanned_ndc_manual_pack_filling(manual_fill_data):

    try:
        assign_user = manual_fill_data["assign_to"]
        drug_data = manual_fill_data["drug_data"]
        module_id = manual_fill_data["module_id"]

        pack_drug_tracker_status = None
        slot_details_update_status = None
        patient_rx_update_status = None

        # pack_list = get_manual_pack_ids(assign_user)
        # logger.info("In manual_pack_filling: pack_list {}".format(pack_list))

        slot_details_data, pack_drug_tracker_data, patient_rx_update_data = get_slot_details_pack_drug_tracker_data(
            drug_data=drug_data,
            module_id=module_id,
            assign_user=assign_user
        )

        logger.info("In manual_pack_filling: slot_details_data: {}".format(slot_details_data))
        logger.info("In manual_pack_filling: pack_drug_tracker_details: {}".format(pack_drug_tracker_data))
        logger.info("In manual_pack_filling: patient_rx_update_data: {}".format(patient_rx_update_data))

        if slot_details_data:
            slot_details_update_status = db_update_slot_details_for_manual_pack_filling(drug_data=drug_data,
                                                                                        slot_details_data=slot_details_data
                                                                                        )

        if pack_drug_tracker_data and slot_details_update_status:
            pack_drug_tracker_status = populate_pack_drug_tracker(pack_drug_tracker_data)

        if patient_rx_update_data:
            patient_rx_update_status = db_update_patient_rx_for_manual_pack_filling(drug_data,
                                                                                    patient_rx_update_data
                                                                                    )

        return create_response(True)
    except Exception as e:
        logger.error("Error in manual_pack_filling: {}".format(e))
        raise e


@log_args_and_response
def update_same_fndc_drug_by_module(user_id, batch_id, new_drug, old_drug, module, pack_ids=None,
                                    mfs_device_id=None):
    """
    Update Drug ids in slot details for same fndc_txr
    @param user_id:
    @param batch_id:
    @param new_drug:
    @param old_drug:
    @param module:
    @param pack_ids:
    @param mfs_device_id:
    @return: True or packs affected
    """

    slot_details_updation: dict = dict()
    pack_drug_tracker_details: list = list()
    pack_id_list: list = list()

    try:
        if module == constants.PDT_MVS_MANUAL_FILL:
            with db.transaction():

                slot_data = get_slots_to_update_pack_wise(pack_ids, old_drug)
                for record in slot_data:
                    slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                           "drug_id": new_drug}

                    pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                              "updated_drug_id": new_drug,
                                              "module": constants.PDT_MVS_MANUAL_FILL,
                                              "created_by": user_id, "created_date": get_current_date_time()}

                    pack_drug_tracker_details.append(pack_drug_tracker_info)
                logger.info("In update_same_fndc_drug_by_module - MVS - slots data going to update {}".format(
                    pack_drug_tracker_info))
                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    # prev_drug_id = slot_drugs["prev_drug_id"]
                    logger.info("In update_same_fndc_drug_by_module -- updating Drug id in slot details {}".format(
                        slot_details_id))

                    update_dict = {"drug_id": drug_id}
                    slot_details_update_status = update_slot_details_by_slot_id_dao(update_dict=update_dict,
                                                                  slot_details_id=slot_details_id)

                    logger.info("In update_same_fndc_drug_by_module: slot details updated: {}, for slot id: {}"
                                .format(slot_details_update_status, slot_details_id))

                create_records_in_pack_drug_tracker(pack_drug_tracker_details=pack_drug_tracker_details)
                logger.info("In update_same_fndc_drug_by_module: Drug Id updated successfully for PDT_MVS_MANUAL_FILL module")
                pack_ids = list(set(pack_ids))
                return pack_ids

        elif module == constants.PDT_PACK_FILL_WORKFLOW:

            pack_id_list = get_packs_to_update_drug_mff(user_id)
            slot_data = get_slots_to_update_pack_wise(pack_id_list, old_drug)
            with db.transaction():
                for record in slot_data:
                    slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                           "drug_id": new_drug}

                    pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                              "updated_drug_id": new_drug,
                                              "module": constants.PDT_PACK_FILL_WORKFLOW,
                                              "created_by": user_id, "created_date": get_current_date_time()}

                    pack_drug_tracker_details.append(pack_drug_tracker_info)
                    logger.info("In update_same_fndc_drug_by_module - MFF - slots data going to update {}".format(
                        pack_drug_tracker_info))

                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    # prev_drug_id = slot_drugs["prev_drug_id"]
                    logger.info("In update_same_fndc_drug_by_module -- updating Drug id in slot details {}".format(
                        slot_details_id))

                    update_dict = {"drug_id": drug_id}
                    slot_details_update_status = update_slot_details_by_slot_id_dao(update_dict=update_dict,
                                                                                    slot_details_id=slot_details_id)

                    logger.info("In update_same_fndc_drug_by_module: slot details updated: {}, for slot id: {}"
                                .format(slot_details_update_status, slot_details_id))

                create_records_in_pack_drug_tracker(pack_drug_tracker_details=pack_drug_tracker_details)
                logger.info("In update_same_fndc_drug_by_module: Drug Id updated successfully for PDT_PACK_FILL_WORKFLOW module")
                pack_id_list = list(set(pack_id_list))
                return pack_id_list

        elif module == constants.PDT_MFD_ALTERNATE:
            slot_data = get_slots_to_update_mfs(batch_id, user_id, old_drug, mfs_device_id)
            with db.transaction():
                for record in slot_data:
                    logger.info(record)
                    pack_id_list.append(record['pack_id'])

                    slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                           "drug_id": new_drug}

                    pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                              "updated_drug_id": new_drug,
                                              "module": constants.PDT_MFD_ALTERNATE,
                                              "created_by": user_id, "created_date": get_current_date_time()}

                    pack_drug_tracker_details.append(pack_drug_tracker_info)
                    logger.info("In update_same_fndc_drug_by_module - MFD - slots data going to update {}".format(
                        pack_drug_tracker_info))

                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    # prev_drug_id = slot_drugs["prev_drug_id"]
                    logger.info("In update_same_fndc_drug_by_module -- updating Drug id in slot details {}".format(
                        slot_details_id))

                    update_dict = {"drug_id": drug_id}
                    slot_details_update_status = update_slot_details_by_slot_id_dao(update_dict=update_dict,
                                                                                    slot_details_id=slot_details_id)

                    logger.info("In update_same_fndc_drug_by_module: slot details updated: {}, for slot id: {}"
                                .format(slot_details_update_status, slot_details_id))

                create_records_in_pack_drug_tracker(pack_drug_tracker_details=pack_drug_tracker_details)
                logger.info("In update_same_fndc_drug_by_module: Drug Id updated successfully for PDT_MFD_ALTERNATE module")
                pack_id_list = list(set(pack_id_list))
                return pack_id_list
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def search_drug_fields(field, field_value=None, all_flag=None):
    """
    Searches on drug fields with given field value
    - splits input with whitespaces and every item is used to search using like

    :param field:
    :param field_value:
    :param all_flag:
    :return: json
    """
    if not field_value and not all_flag:
        return create_response([])
    if all_flag:
        all_flag = int(all_flag)
    try:
        results = search_drug_field_dao(field, field_value, all_flag)
        return create_response(results)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def register_powder_pill(args):
    try:
        fndc = args.get('fndc')
        txr = args.get('txr')
        company_id = args.get('company_id')
        is_powder_pill = int(args.get('is_powder_pill'))
        is_robot = args.get('is_robot', False)
        device_id = args.get('device_id', 0)
        if not fndc or not txr or not is_powder_pill:
            return error(1002, "Required args missing -> fndc or txr or is_powder_pill")

        update_data = register_powder_pill_daw(fndc, txr, is_powder_pill)
        # if is_robot and device_id and update_data:
        #     update_replenish_based_on_device(device_id)
        return create_response(1)
        
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in register_powder_pill. {}".format(e)))
        return error(2001)
    except Exception as e:
        logger.error(e)
        logger.error(("Error in register_powder_pill. {}".format(e)))
        return error(2001)


@log_args_and_response
def separate_pack_canister_drug_from_scanned_value(args):
    try:
        scanned_value = args.get('scanned_value', None)
        company_id = args.get('company_id', None)
        user_id = args.get('user_id', None)
        system_id = args.get('system_id', None)
        canister_data = dict()
        pack_data = dict()
        drug_data = dict()
        pack_dict = dict()

        if len(scanned_value) >= 9:
            input_args = {"ndc": scanned_value, "user_id": user_id,
                          "company_id": company_id}
            data = json.loads(get_valid_ndc(input_args))
            drug_data = data.get("data")

        elif len(scanned_value) <= 5:
            canister_status = validate_canister_id_with_company_id(canister_id=scanned_value, company_id=company_id)
            if canister_status:
                canister_data['canister_id'] = scanned_value

        if len(scanned_value) < 9 and not canister_data:
            pack_status = verify_pack_display_id(pack_display_id=scanned_value)
            if pack_status:
                pack_dict = db_get_pack_ids_by_pack_display_id_dao(pack_display_ids=[scanned_value], company_id=company_id)
                pack_data['display_pack_id'] = scanned_value
                pack_data['pack_id'] = pack_dict[int(scanned_value)]

        response = {
            "drug_data": drug_data,
            "canister_data": canister_data,
            "pack_data": pack_data
        }
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in separate_pack_canister_drug_from_scanned_value. {}".format(e)))
        return error(2001)
    except Exception as e:
        logger.error(e)
        logger.error(("Error in separate_pack_canister_drug_from_scanned_value. {}".format(e)))
        return error(2001)


@validate(required_fields=["company_id", "pack_id"])
@log_args_and_response
def get_drug_detail_slotwise(args):
    ''' This function returns list of drugs slotwise of a given pack '''

    try:
        pack_id = args['pack_id']
        slot_drug_dict = {
            pack_id: dict()
        }
        logger.info("Inside get_drug_detail_slotwise, getting drug info for pack_id {}".format(pack_id))

        for record in get_drug_detail_slotwise_dao(args):
            if record['slot_number'] not in slot_drug_dict[pack_id]:
                slot_drug_dict[pack_id][record['slot_number']] = list()

            slot_drug_dict[pack_id][record['slot_number']].append({
                'fndc_txr': record['fndc_txr'],
                'qty': record['quantity'],
                'name_strength_ndc': record['name_strength_ndc']
            })

        return create_response(slot_drug_dict)

    except Exception as e:
        logger.error("In get_drug_detail_slotwise. Error: {}".format(e))
        return error(1000, "Error in get_drug_detail_slotwise: " + str(e))


@log_args_and_response
def fetch_drug_data(company_id, user_id, file_id, token, upc=None, ndc=None):
    """ check if ndc received is missing and fetch data for that ndc from IPS"""
    try:
        if ndc:
            drug_id = DrugMaster.select(DrugMaster.id).where(DrugMaster.ndc == ndc).scalar()
            if drug_id:
                return drug_id
            get_missing_drug_data([ndc], company_id, user_id, file_id)
            drug_id = DrugMaster.select(DrugMaster.id).where(DrugMaster.ndc == ndc).scalar()
            if drug_id:
                return drug_id
            return error(1001)
        if upc:
            drug_id = DrugMaster.select(DrugMaster.id).where(DrugMaster.upc == upc).scalar()
            if drug_id:
                return drug_id
            get_missing_drug_data([upc], company_id, user_id, file_id, upc_flag=True, token=token)
            drug_id = DrugMaster.select(DrugMaster.id).where(DrugMaster.upc == upc).scalar()
            if drug_id:
                return drug_id
            return error(1001)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in separate_pack_canister_drug_from_scanned_value. {}".format(e)))
        return error(2001)
    except Exception as e:
        logger.error(e)
        logger.error(("Error in separate_pack_canister_drug_from_scanned_value. {}".format(e)))
        return error(2001)


@log_args_and_response
def get_drug_image_data(ndc_list, company_id):
    """ check if ndc received is missing and fetch data for that ndc from IPS"""
    try:
        ndc_qty_map = get_inventory_quantity_from_elite(ndc_list=ndc_list, back_end_fetch=True)
        return create_response(get_drug_image_data_dao(ndc_list, ndc_qty_map, company_id))

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in get_drug_image_data. {}".format(e)))
        return error(2001)
    except Exception as e:
        logger.error(e)
        logger.error(("Error in get_drug_image_data. {}".format(e)))
        return error(2001)


@log_args_and_response
def get_inventory_quantity_from_elite(ndc_list, back_end_fetch=None):
    """ fetch ndc's quantity from elite """
    try:
        ndc_qty_map = {}
        new = []
        ndc_list_copy = ndc_list.copy()
        inventory_data = []
        inventory_data_2 = []
        for ndc in ndc_list_copy:
            new.append(int(ndc))
        alternate_ndc_map, alternate_ndcs = db_get_alternate_ndcs(new)
        if settings.USE_EPBM:
            inventory_data = get_current_inventory_data(ndc_list=new, qty_greater_than_zero=False)
            inventory_data_2 = get_current_inventory_data(ndc_list=alternate_ndcs, qty_greater_than_zero=False)
            pass
        ndc_alternate_qty_map = {}
        for record in inventory_data:
            alternate_qty_sum = 0
            for alternate_record in inventory_data_2:
                if int(alternate_record["ndc"]) in alternate_ndc_map[int(record["ndc"])]:
                    alternate_qty_sum += alternate_record["quantity"]
            ndc_alternate_qty_map.setdefault(record["ndc"], {}).setdefault("qty", record["quantity"])
            ndc_alternate_qty_map.setdefault(record["ndc"], {}).setdefault("alternate_qty_sum", alternate_qty_sum)
            if record['ndc'] in ndc_list_copy:
                ndc_list_copy.remove(record['ndc'])
            ndc_qty_map[record['ndc']] = record['quantity']
        for ndc in ndc_list_copy:
            ndc_qty_map[ndc] = None
        if back_end_fetch:
            return ndc_qty_map
        return create_response(ndc_alternate_qty_map)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in get_inventory_quantity_from_elite. {}".format(e)))
        return error(2001)
    except Exception as e:
        logger.error(e)
        logger.error(("Error in get_inventory_quantity_from_elite. {}".format(e)))
        return error(2001)


@log_args_and_response
def get_lot_no_from_ndc(ndc, no_of_records):
    '''Function to get latest lot no for ndc'''
    try:

        no_of_records = int(no_of_records)
        recent_lot_info = get_lot_no_from_ndc_dao(ndc, no_of_records)

        return create_response(recent_lot_info)

    except Exception as e:
        logger.error("In get_lot_no_from_ndc. Error: {}".format(e))
        return error(1000, "Error in get_lot_no_from_ndc: " + str(e))


@log_args_and_response
def parser_scan_canister_qr(scanned_canister, company_id):
    '''
    The Scanned Canister id is like CAN-6754-3
    In this canister_id -> 6754
            company_id -> 3
    '''
    try:
        if scanned_canister.startswith(constants.CANISTER_LABEL_PREFIX):

            first_dash_position = scanned_canister.find('-')
            second_dash_position = scanned_canister.find('-', first_dash_position + 1)
            third_dash_position = scanned_canister.find('-', second_dash_position + 1)

            if first_dash_position != -1 and second_dash_position != -1 and third_dash_position == -1:
                try:
                    company_id = int(scanned_canister[second_dash_position + 1:])
                    canister_id = int(scanned_canister[first_dash_position + 1: second_dash_position])

                except ValueError as e:
                    return False, False
            else:
                return False, False

            return int(canister_id), int(company_id)
        else:
            return scanned_canister, company_id
    except Exception as e:
        logger.error("In get_valid_canister_id. Error: {}".format(e))
        return error(1000, "Error in get_valid_canister_id: " + str(e))


@log_args_and_response
def validate_drug_for_prn_retail(ndc, daw, to_fill_ndc, scanned_fndc, scanned_txr):
    try:
        if ndc == to_fill_ndc:
            return constants.SAME_NDC, False, None
        to_fill_brand_flag = int(DrugMaster.select(DrugMaster.brand_flag).where(DrugMaster.ndc == to_fill_ndc).scalar())
        scanned_brand_flag = int(DrugMaster.select(DrugMaster.brand_flag).where(DrugMaster.ndc == ndc).scalar())
        if scanned_brand_flag == 2:
            return None, None, 9023
        if to_fill_brand_flag == 2:
            return None, None, 9026
        to_fill_fndc = DrugMaster.select(DrugMaster.formatted_ndc).where(DrugMaster.ndc == to_fill_ndc).scalar()
        to_fill_fndc = ndc[:9] if not to_fill_fndc else to_fill_fndc
        if to_fill_fndc == scanned_fndc:
            return constants.SAME_DRUG, True, None
        if daw == 1:
            return None, None, 9022
        to_fill_txr = list(DrugMaster.select(DrugMaster.txr).dicts().where(DrugMaster.formatted_ndc == to_fill_fndc))[0]["txr"]
        if to_fill_txr == scanned_txr:
            return constants.ALTERNATE_DRUG, True, None
        return None, None, 9021

    except Exception as e:
        logger.error("In validate_drug_for_prn_retail. Error: {}".format(e))
        return error(1000, "Error in validate_drug_for_prn_retail: " + str(e))
