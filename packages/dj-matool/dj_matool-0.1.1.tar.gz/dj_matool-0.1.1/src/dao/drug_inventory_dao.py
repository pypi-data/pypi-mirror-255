from typing import List, Dict, Any, Optional, Tuple

from celery.utils import threads
from peewee import *
from peewee import InternalError, IntegrityError, DoesNotExist, DataError
from playhouse.shortcuts import case

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, log_args, get_current_datetime_by_timezone
from model import model_init
from src.dao.canister_dao import db_get_total_canister_quantity_by_drug_id
from src.dao.drug_dao import get_all_same_drug_by_drug_id, get_drug_list_from_case_id_ndc
from src.dao.pack_dao import get_filled_drug_count_slot_transaction, get_mfd_filled_drug_count, \
    get_manual_partially_filled_packs_drug_count
from src.exc_thread import ExcThread
from src.exceptions import APIFailureException, TokenFetchException, DrugInventoryInternalException, \
    DrugInventoryValidationException
from src.model.model_inventroy_transaction_history import InventoryTransactionHistory
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_user_map import PackUserMap
from src.model.model_alternate_drug_option import AlternateDrugOption
from dosepack.utilities.utils import get_current_date_time
from src.constants import DRUG_INVENTORY_MANAGEMENT_ADDED_ID, DRUG_INVENTORY_MANAGEMENT_UPDATED_ID
from src.model.model_adhoc_drug_request import AdhocDrugRequest
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_batch_drug_order_data import BatchDrugOrderData
from src.model.model_batch_drug_request_mapping import BatchDrugRequestMapping
from src.model.model_batch_pack_data import BatchPackData
from src.model.model_canister_master import CanisterMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_current_inventory_mapping import CurrentInventoryMapping
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_patient_rx import PatientRx
from src.model.model_pre_order_missing_ndc import PreOrderMissingNdc
from src.model.model_slot_details import SlotDetails
from src.model.model_system_setting import SystemSetting
from src.model.model_unique_drug import UniqueDrug
from utils.drug_inventory_webservices import post_adjustment_data_to_drug_inventory

logger = settings.logger


@log_args_and_response
def get_canister_details_by_id_dao(canister_id: int, company_id: int) -> dict:
    """
    Method to get canister details based on canister_id
    @param canister_id:
    @param company_id:
    @return:
    """
    try:
        return CanisterMaster.select().dicts().where(CanisterMaster.id == canister_id,
                                                     CanisterMaster.company_id == company_id).get()

    except DoesNotExist as e:
        logger.error("Invalid canister_id - {} or company_id - {}".format(canister_id, company_id))
        raise e

    except InternalError as e:
        logger.error("error in get_canister_details_by_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_info_based_on_ndc_dao(ndc_list: List[str]) -> dict:
    """
    Method to get drug_info based on ndc
    """
    try:
        return DrugMaster.db_get_drug_data_based_on_ndc(ndc_list=ndc_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_drug_info_based_on_ndc_dao".format(e))
        raise e


@log_args_and_response
def get_batch_drug_data(facility_dist_id: Optional[int] = None, pack_id_list: Optional[List[int]] = None) -> List[Any]:
    """
    Gets a list of unique drugs in the packs of the given facility_dist_id along with the qty, brand flag & daw flag.
    """
    clauses: List[Any] = list()

    if facility_dist_id:
        clauses.extend([PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                        PackDetails.facility_dis_id == facility_dist_id])
    if pack_id_list:
        clauses.append(PackDetails.id.in_(pack_id_list))
    try:
        query = SlotDetails.select(fn.sum(SlotDetails.quantity).alias("req_qty"),
                                   PatientRx.daw_code.alias("daw"),
                                   FacilityDistributionMaster.company_id,
                                   fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).alias("pack_id"),
                                   PackDetails.facility_dis_id.alias("facility_dist_id"),
                                   DrugMaster.txr,
                                   DrugMaster.formatted_ndc,
                                   DrugMaster.manufacturer,
                                   DrugMaster.ndc,
                                   DrugMaster.drug_name,
                                   DrugMaster.strength,
                                   DrugMaster.strength_value,
                                   DrugMaster.id.alias("drug_id"),
                                   DrugMaster.brand_flag,
                                   DrugMaster.image_name,
                                   DrugMaster.shape,
                                   DrugMaster.imprint,
                                   UniqueDrug.id.alias("unique_drug_id"),
                                   UniqueDrug.drug_usage).dicts() \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(FacilityDistributionMaster, JOIN_LEFT_OUTER, on=FacilityDistributionMaster.id == PackDetails.facility_dis_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .where(*clauses) \
            .group_by(UniqueDrug.formatted_ndc, UniqueDrug.txr, PatientRx.daw_code) \
            .having(fn.sum(SlotDetails.quantity) > 0)

        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_batch_drug_data".format(e))
        raise e


@log_args
def get_records_by_facility_dist_id_and_dept(facility_dist_id: int, department: Optional[str] = None) -> List[Any]:
    """
    Gets the list of records from the BatchDrugData & the unique_id for the record's ndc for the given facility_dist_id.
    """
    clauses: List[Any] = [BatchDrugData.facility_dist_id == facility_dist_id]
    if department:
        clauses.append(BatchDrugData.department == department)
    try:
        query = BatchDrugData.select(BatchDrugData.id.alias("batch_drug_data_id"),
                                     BatchDrugData.facility_dist_id,
                                     BatchDrugData.formatted_ndc,
                                     BatchDrugData.txr,
                                     BatchDrugData.daw,
                                     BatchDrugData.req_qty,
                                     BatchDrugData.order_qty,
                                     BatchDrugData.ndc,
                                     BatchDrugData.status_id,
                                     BatchDrugData.department,
                                     UniqueDrug.id.alias("unique_drug_id")).dicts() \
            .join(DrugMaster, on=DrugMaster.ndc == BatchDrugData.ndc) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .where(*clauses)
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_records_by_facility_dist_id_and_dept".format(e))
        raise e


@log_args_and_response
def get_batch_drug_data_by_facility_dist_id_and_dept(facility_dist_id: int, department: str) -> List[Any]:
    """
    Fetches all the data from BatchDrugData for the given facility_dist_id
    """
    try:
        return BatchDrugData.get_drug_data_by_facility_dist_id_and_dept(facility_dist_id=facility_dist_id,
                                                                        department=department)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_batch_drug_data_by_facility_dist_id_and_dept".format(e))
        raise e


@log_args_and_response
def populate_batch_drug_data(batch_drug_data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the BatchDrugData.
    """
    try:
        return BatchDrugData.insert_data(data_list=batch_drug_data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_batch_drug_data".format(e))
        raise e


@log_args_and_response
def delete_batch_drug_data(delete_list: List[str], facility_dist_id: int, user_id: int) -> bool:
    """
    Updates the status as deleted of the given list of drug_ids and the given facility_dist_id.
    """
    try:
        return BatchDrugData.delete_data(delete_list=delete_list, facility_dist_id=facility_dist_id, user_id=user_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in delete_batch_drug_data".format(e))
        raise e


@log_args_and_response
def update_batch_drug_data_by_fndc_txr_daw_and_dept(data: Dict[str, Any], facility_dist_id: int, fndc_txr_daw: str,
                                                    department: str) -> bool:
    """
    Updates the record for the given drug_id and the facility_dist_id.
    """
    try:
        return BatchDrugData.update_batch_drug_data_by_fndc_txr_daw_and_dept(
            data=data, facility_dist_id=facility_dist_id, fndc_txr_daw=fndc_txr_daw, department=department)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_batch_drug_data_by_fndc_txr_daw_and_dept".format(e))
        raise e


@log_args_and_response
def update_batch_drug_data_by_ndc(data: Dict[str, Any], facility_dist_id: int, ndc: str) -> bool:
    """
    Updates the record for the given drug_id and the facility_dist_id.
    """
    try:
        return BatchDrugData.update_batch_drug_data_by_ndc(data=data, facility_dist_id=facility_dist_id, ndc=ndc)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_batch_drug_data_by_ndc".format(e))
        raise e


@log_args_and_response
def get_drug_data_from_ndc_list(ndc_list: List[str]) -> Dict[str, Any]:
    """
    This function fetches the drug_ids corresponding to the list of NDCs.
    """
    try:
        query = DrugMaster.select(DrugMaster.ndc,
                                  DrugMaster.formatted_ndc,
                                  DrugMaster.txr,
                                  DrugMaster.id.alias("drug_id"),
                                  UniqueDrug.id.alias("unique_drug_id")).dicts() \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (
                          fn.COALESCE(UniqueDrug.txr, "") == fn.COALESCE(DrugMaster.txr, "")))) \
            .where(DrugMaster.ndc << ndc_list).dicts()

        return {record["ndc"]: record for record in query}

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_drug_data_from_ndc_list".format(e))
        raise


@log_args_and_response
def get_inventory_order_data_by_facility_dist_id(facility_dist_id: int) -> List[Any]:
    """
    Get the records from BatchDrugOrderData for the given facility_dist_id
    """
    try:
        query = BatchDrugOrderData.select(BatchDrugOrderData.batch_drug_data_id).dicts() \
            .join(BatchDrugData, on=BatchDrugData.id == BatchDrugOrderData.batch_drug_data_id) \
            .where(BatchDrugData.facility_dist_id == facility_dist_id)
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_inventory_order_data_by_facility_dist_id".format(e))
        raise e


@log_args_and_response
def populate_alternate_drug_option_by_order_data(alternate_drug_option_data: List[Dict[str, Any]]) -> bool:
    """
    Inserts the data in the AlternateDrugOption table.
    """
    try:
        AlternateDrugOption.add_alternate_drug(info_list=alternate_drug_option_data)
        return True
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_alternate_drug_option_by_order_data".format(e))
        raise e


@log_args_and_response
def update_alternate_drug_option_by_order_data(facility_dist_id: int, unique_alt_drug_id_list: List[str],
                                               unique_drug_id_list: List[int], user_id: int) -> bool:
    """
    Updates the record for the given list of unique_alt_drug_ids and the facility_dist_id.
    """
    try:
        info_dict = {"facility_distribution_id": facility_dist_id,
                     "unique_drug_ids": unique_drug_id_list,
                     "user_id": user_id}
        AlternateDrugOption.remove_alternate_drug_distribution_id(info_dict=info_dict)

        update_based_on_order(facility_dist_id=facility_dist_id, user_id=user_id,
                                                  unique_alt_drug_id_list=unique_alt_drug_id_list)
        return True
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_alternate_drug_option_by_order_data".format(e))
        raise e


@log_args_and_response
def populate_batch_order_data(batch_order_data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the BatchDrugOrderData.
    """
    try:
        return BatchDrugOrderData.insert_data(data_list=batch_order_data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_batch_order_data".format(e))
        raise e


@log_args_and_response
def update_batch_drug_order_data_by_batch_drug_data_id(update_dict: Dict[str, Any], batch_drug_data_id: int) -> bool:
    """
    Updates the record in BatchDrugOrderData by batch_drug_data_id.
    """
    try:
        return BatchDrugOrderData.update_data_by_id(data=update_dict, batch_drug_data_id=batch_drug_data_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_batch_drug_order_data_by_batch_drug_data_id".format(e))
        raise e


@log_args_and_response
def validate_facility_dist_id_by_company_id(company_id: int, facility_dist_id: int) -> bool:
    """
    Checks if the given facility_dist_id and company_id combination is valid.
    """
    try:
        return FacilityDistributionMaster.db_validate_company_bach_distribution_id(company_id=company_id,
                                                                                   facility_dist_id=facility_dist_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in validate_facility_dist_id_by_company_id".format(e))
        raise e


@log_args_and_response
def populate_batch_drug_request_mapping_data(batch_drug_req_map_data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the BatchDrugRequestMapping.
    """
    try:
        return BatchDrugRequestMapping.insert_data(data_list=batch_drug_req_map_data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_batch_drug_request_mapping_data".format(e))
        raise e


@log_args
def get_mapping_data_by_facility_dist_id(facility_dist_id: int) -> Dict[str, Dict[str, Any]]:
    """
    Fetches the data grouped by requested_unique_drug_id and daw for the given facility_dist_id.
    """
    try:
        return BatchDrugRequestMapping.get_mapping_data_by_facility_dist_id(facility_dist_id=facility_dist_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_mapping_data_by_facility_dist_id".format(e))
        raise e


@log_args_and_response
def update_txr_in_drug_master_and_unique_drug(txr: str, ndc: str) -> bool:
    """
    Updates the txr for the given NDC in DrugMaster & corresponding changes in the UniqueDrug & PRS table.
    """
    try:
        status = DrugMaster.update_txr_by_ndc(txr=txr, ndc=ndc)
        return status

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_txr_in_drug_master_and_unique_drug".format(e))
        raise e


@log_args_and_response
def get_batch_drug_data_id_from_ndc(ndc_list: List[str], facility_dist_id: int) -> Dict[str, int]:
    """
    get the batch_drug_data_id from BatchDrugOrderData or CurrentInventoryMapping based on pre_order_ndc or
    reserve_ndc respectively.
    """
    response_data: Dict[str, int] = dict()
    try:
        query = BatchDrugData.select(BatchDrugData.id,
                                     fn.IF(BatchDrugOrderData.pre_ordered_ndc.is_null(True), None,
                                           BatchDrugOrderData.pre_ordered_ndc).alias("pre_ordered_ndc"),
                                     fn.IF(CurrentInventoryMapping.reserve_ndc.is_null(True), None,
                                           CurrentInventoryMapping.reserve_ndc).alias("reserve_ndc")).dicts() \
            .join(BatchDrugOrderData, JOIN_LEFT_OUTER, on=BatchDrugData.id == BatchDrugOrderData.batch_drug_data_id) \
            .join(CurrentInventoryMapping, JOIN_LEFT_OUTER,
                  on=BatchDrugData.id == CurrentInventoryMapping.batch_drug_id) \
            .where((BatchDrugData.facility_dist_id == facility_dist_id) &
                   ((BatchDrugOrderData.pre_ordered_ndc.in_(ndc_list)) |
                    (CurrentInventoryMapping.reserve_ndc.in_(ndc_list))))

        for data in query:
            if data["pre_ordered_ndc"]:
                response_data[data["pre_ordered_ndc"]] = data["id"]
            if data["reserve_ndc"]:
                response_data[data["reserve_ndc"]] = data["id"]
        return response_data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_batch_drug_data_id_from_ndc".format(e))
        raise e


@log_args_and_response
def populate_pre_order_missing_ndc(pre_order_missing_ndc_data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the PreOrderMissingNdc.
    """
    try:
        return PreOrderMissingNdc.insert_data(data_list=pre_order_missing_ndc_data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_pre_order_missing_ndc".format(e))
        raise e


@log_args_and_response
def get_data_for_modified_drug_list(facility_dist_id: int, req_drug_search: str,
                                    avl_pre_order_drug_search: str) -> List[Any]:
    """
    Fetch the requested data and the corresponding pre-order data & inventory mapped data for the given facility_dist_id
    """

    drug_master_pre_order: BaseModel = DrugMaster.alias()
    unique_drug_pre_order: BaseModel = UniqueDrug.alias()
    drug_master_available: BaseModel = DrugMaster.alias()
    unique_drug_available: BaseModel = UniqueDrug.alias()
    clauses: List[Any] = [BatchDrugData.facility_dist_id == facility_dist_id,
                          BatchDrugData.status_id.in_([DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                                       DRUG_INVENTORY_MANAGEMENT_UPDATED_ID])]
    if req_drug_search:
        ndc = req_drug_search.split(",")
        if len(ndc[0]) == 11:
            if ndc[0].isnumeric():
                clauses.append(drug_master_pre_order.ndc << ndc | drug_master_available.ndc << ndc)
        else:
            data: str = "%" + str(req_drug_search) + "%"
            clauses.append(
                fn.CONCAT("", DrugMaster.concated_drug_name_field(include_ndc=True) ** data))

    if avl_pre_order_drug_search:
        ndc = avl_pre_order_drug_search.split(",")
        if len(ndc[0]) == 11:
            if ndc[0].isnumeric():
                clauses.append(drug_master_pre_order.ndc << ndc | drug_master_available.ndc << ndc)
        else:
            data: str = "%" + str(avl_pre_order_drug_search) + "%"
            clauses.append(
                (fn.CONCAT("",
                           fn.CONCAT(drug_master_pre_order.drug_name, ' ', drug_master_pre_order.strength_value, ' ',
                                     drug_master_pre_order.strength, ' (', drug_master_pre_order.ndc, ')') ** data)) |
                (fn.CONCAT("",
                           fn.CONCAT(drug_master_available.drug_name, ' ', drug_master_available.strength_value, ' ',
                                     drug_master_available.strength, ' (', drug_master_available.ndc, ')') ** data)))
    try:
        query = BatchDrugData.select(BatchDrugData.id.alias("batch_drug_data_id"),
                                     BatchDrugData.ndc.alias("requested_ndc"),
                                     BatchDrugData.daw.alias("requested_daw"),
                                     BatchDrugData.req_qty.alias("required_qty"),
                                     BatchDrugData.order_qty.alias("requested_qty"),
                                     BatchDrugData.ext_is_success.alias("request_success"),
                                     BatchDrugData.ext_note.alias("request_note"),
                                     DrugMaster.concated_drug_name_field().alias("requested_drug_name"),
                                     UniqueDrug.id.alias("requested_unique_drug_id"),
                                     BatchDrugOrderData.id.alias("batch_drug_order_data_id"),
                                     BatchDrugOrderData.pre_ordered_ndc,
                                     BatchDrugOrderData.pre_ordered_qty,
                                     BatchDrugOrderData.is_sub.alias("is_substituted"),
                                     BatchDrugOrderData.sub_reason.alias("substitution_reason"),
                                     fn.CONCAT(drug_master_pre_order.drug_name, ' ',
                                               drug_master_pre_order.strength_value, ' ',
                                               drug_master_pre_order.strength).alias("pre_order_drug_name"),
                                     unique_drug_pre_order.id.alias("pre_ordered_unique_drug_id"),
                                     CurrentInventoryMapping.id.alias("current_inventory_mapped_id"),
                                     CurrentInventoryMapping.reserve_ndc.alias("available_ndc"),
                                     CurrentInventoryMapping.reserve_qty.alias("available_qty"),
                                     CurrentInventoryMapping.is_active.alias("available_is_active"),
                                     fn.CONCAT(drug_master_available.drug_name, ' ',
                                               drug_master_available.strength_value, ' ',
                                               drug_master_available.strength).alias("available_drug_name"),
                                     unique_drug_available.id.alias("available_unique_drug_id")).dicts() \
            .join(DrugMaster, on=(BatchDrugData.ndc == DrugMaster.ndc)) \
            .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                  (DrugMaster.txr == UniqueDrug.txr))) \
            .join(BatchDrugOrderData, JOIN_LEFT_OUTER, on=BatchDrugData.id == BatchDrugOrderData.batch_drug_data_id) \
            .join(drug_master_pre_order, JOIN_LEFT_OUTER,
                  on=BatchDrugOrderData.pre_ordered_ndc == drug_master_pre_order.ndc) \
            .join(unique_drug_pre_order, JOIN_LEFT_OUTER,
                  on=((drug_master_pre_order.formatted_ndc == unique_drug_pre_order.formatted_ndc) &
                      (drug_master_pre_order.txr == unique_drug_pre_order.txr))) \
            .join(CurrentInventoryMapping, JOIN_LEFT_OUTER,
                  on=BatchDrugData.id == CurrentInventoryMapping.batch_drug_id) \
            .join(drug_master_available, JOIN_LEFT_OUTER,
                  on=CurrentInventoryMapping.reserve_ndc == drug_master_available.ndc) \
            .join(unique_drug_available, JOIN_LEFT_OUTER,
                  on=((drug_master_available.formatted_ndc == unique_drug_available.formatted_ndc) &
                      (drug_master_available.txr == unique_drug_available.txr))) \
            .where(*clauses).order_by(DrugMaster.concated_drug_name_field())
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_data_for_modified_drug_list".format(e))
        raise e


@log_args_and_response
def get_drug_data_by_ndc_list(ndc_list: List[str], company_id: int) -> Dict[str, Dict[str, Any]]:
    """
    This function returns the drug data with its stock information and last seen with data.
    """
    try:
        query = DrugMaster.select(DrugMaster.ndc,
                                  DrugMaster.concated_drug_name_field(include_ndc=True).alias("drug_name"),
                                  DrugMaster.formatted_ndc,
                                  DrugMaster.txr,
                                  DrugMaster.image_name,
                                  DrugMaster.shape,
                                  DrugMaster.color,
                                  DrugMaster.imprint,
                                  UniqueDrug.id.alias("unique_drug_id"),
                                  fn.IF(DrugStockHistory.is_in_stock.is_null(True), None,
                                        DrugStockHistory.is_in_stock).alias('is_in_stock'),
                                  fn.IF(DrugDetails.last_seen_by.is_null(True), None,
                                        DrugDetails.last_seen_by).alias('last_seen_with')).dicts() \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                 (UniqueDrug.txr == DrugMaster.txr)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .where(DrugMaster.ndc.in_(ndc_list))

        return {data["ndc"]: data for data in query}

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_drug_data_by_ndc_list".format(e))
        raise e


@log_args_and_response
def get_canister_data_by_unique_drug_id_list(id_list: List[int], company_id: int) -> Dict[int, List[Dict[str, Any]]]:
    """
    This function returns the canister data for the given list of unique_drug_ids
    """
    result_dict: Dict[int, List[Dict[str, Any]]] = dict()
    try:
        query = CanisterMaster.select(UniqueDrug.id.alias("unique_drug_id"),
                                      CanisterMaster.id.alias("canister_id"),
                                      CanisterMaster.available_quantity,
                                      CanisterMaster.location_id,
                                      LocationMaster.display_location,
                                      ContainerMaster.id.alias("container_id"),
                                      ContainerMaster.drawer_name,
                                      DeviceMaster.id.alias("device_id"),
                                      DeviceMaster.name.alias("device_name")).dicts() \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                  (fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                   fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(UniqueDrug.id.in_(id_list), CanisterMaster.company_id == company_id, CanisterMaster.active == 1)

        for data in query:
            if data["unique_drug_id"] in result_dict:
                result_dict[data["unique_drug_id"]].append(data)
            else:
                result_dict[data["unique_drug_id"]] = [data]

        return result_dict

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_canister_data_by_unique_drug_id_list".format(e))
        raise e


@log_args_and_response
def get_cur_inventory_mapping_data(facility_dist_id: int, local_di: bool,
                                   only_active: Optional[bool] = True) -> List[Any]:
    """
    Fetches the data from the CurrentInventoryMapping for the given facility_dist_id.
    """
    try:
        return CurrentInventoryMapping.get_data_by_facility_dist_id(facility_dist_id=facility_dist_id,
                                                                    only_active=only_active, local_di=local_di)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_cur_inventory_mapping_data".format(e))
        raise e


@log_args_and_response
def insert_current_inventory_mapping_data(data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the BatchDrugData.
    """
    try:
        return CurrentInventoryMapping.insert_data(data_list=data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in insert_current_inventory_mapping_data".format(e))
        raise e


@log_args_and_response
def delete_current_inventory_mapping(facility_dist_id: int) -> bool:
    """
    Updates the is_active flag false in the CurrentInventoryMapping table.
    """
    try:
        return CurrentInventoryMapping.delete_data(facility_dist_id=facility_dist_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in delete_current_inventory_mapping".format(e))
        raise e


@log_args_and_response
def update_current_inventory_mapping_by_id(update_dict: Dict[str, Any], update_id: int) -> bool:
    """
    Updates the record in BatchDrugOrderData by batch_drug_data_id.
    """
    try:
        return CurrentInventoryMapping.update_data_by_id(data=update_dict, update_id=update_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_current_inventory_mapping_by_id".format(e))
        raise e


@log_args_and_response
def get_reserve_ndc_by_facility_dist_id(facility_dist_id: int) -> List[Any]:
    """
    Fetches the reserve ndc from the CurrentInventoryMapping for the given facility_dist_id.
    """
    try:
        return CurrentInventoryMapping.select(CurrentInventoryMapping.batch_drug_id,
                                              fn.GROUP_CONCAT(CurrentInventoryMapping.reserve_ndc).coerce(False).alias(
                                                  "reserve_ndc_list"),
                                              BatchDrugData.daw,
                                              BatchDrugData.ndc).dicts() \
            .join(BatchDrugData, on=BatchDrugData.id == CurrentInventoryMapping.batch_drug_id) \
            .where(BatchDrugData.facility_dist_id == facility_dist_id, CurrentInventoryMapping.is_active == 1) \
            .group_by(CurrentInventoryMapping.batch_drug_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_reserve_ndc_by_facility_dist_id".format(e))
        raise e


@log_args_and_response
def get_facility_dist_id_status(company_id: int, facility_dist_id: int) -> int:
    """
    Fetch the status of the facility_dist_id for the given company_id.
    """
    try:
        return FacilityDistributionMaster.db_get_facility_distribution_status(company_id=company_id,
                                                                              facility_dist_id=facility_dist_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_facility_dist_id_status".format(e))
        raise e


@log_args_and_response
def get_system_setting_by_system_ids(system_id_list: List[int]) -> List[Any]:
    """
    Fetches the data from the SystemSetting for the given list of system_ids.
    """
    try:
        return SystemSetting.db_get_by_system_id_list(system_id_list=system_id_list)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_system_setting_by_system_ids".format(e))
        raise e


@log_args_and_response
def get_manual_pack_ids_for_upcoming_days(company_id: int, current_date: str, end_date: Optional[str] = None,
                                          manual_capacity: Optional[int] = None) -> List[Any]:
    """
    Get the manual pack_ids for the upcoming days based on the capacity
    """
    clauses: List[Any] = [PackDetails.company_id == company_id,
                          PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                          PackHeader.scheduled_delivery_date >= current_date]
    order_list: List[Any] = [PackHeader.scheduled_delivery_date]
    if end_date:
        clauses.append(PackHeader.scheduled_delivery_date <= end_date)
    try:
        query = PackDetails.select(PackDetails.id.alias("pack_id")).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .where(*clauses).order_by(*order_list)

        if manual_capacity:
            query = query.limit(manual_capacity)

        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_manual_pack_ids_for_upcoming_days".format(e))
        raise e


@log_args_and_response
def get_auto_pack_ids_for_upcoming_days(company_id: int, current_date: str, auto_capacity: Optional[int] = None,
                                        end_date: Optional[str] = None) -> List[Any]:
    """
    Get the manual pack_ids for the upcoming days based on the capacity
    """
    clauses: List[Any] = [PackDetails.company_id == company_id,
                          PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                          PackHeader.scheduled_delivery_date >= current_date]
    order_list: List[Any] = [PackHeader.scheduled_delivery_date, PackDetails.pack_sequence]
    if end_date:
        clauses.append(PackHeader.scheduled_delivery_date <= end_date)
    try:
        query = PackDetails.select(PackDetails.id.alias("pack_id")).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(*clauses).order_by(*order_list)

        if auto_capacity:
            query = query.limit(auto_capacity)

        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_auto_pack_ids_for_upcoming_days".format(e))
        raise e


@log_args_and_response
def get_records_by_unique_id_and_dept(unique_id: str, department: str) -> List[Any]:
    """
    Gets the list of records from the BatchDrugData & the unique_id for the record's ndc for the given facility_dist_id.
    """
    try:
        query = AdhocDrugRequest.select(AdhocDrugRequest.id.alias("batch_drug_data_id"),
                                        AdhocDrugRequest.unique_id,
                                        AdhocDrugRequest.formatted_ndc,
                                        AdhocDrugRequest.txr,
                                        AdhocDrugRequest.daw,
                                        AdhocDrugRequest.req_qty,
                                        AdhocDrugRequest.order_qty,
                                        AdhocDrugRequest.ndc,
                                        AdhocDrugRequest.status_id,
                                        AdhocDrugRequest.department,
                                        UniqueDrug.id.alias("unique_drug_id")).dicts() \
            .join(DrugMaster, on=DrugMaster.ndc == AdhocDrugRequest.ndc) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .where(AdhocDrugRequest.unique_id == unique_id, AdhocDrugRequest.department == department)
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_records_by_unique_id_and_dept".format(e))
        raise e


@log_args_and_response
def populate_adhoc_drug_request(adhoc_drug_request_data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the AdhocDrugRequest.
    """
    try:
        return AdhocDrugRequest.insert_data(data_list=adhoc_drug_request_data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_adhoc_drug_request".format(e))
        raise e


@log_args_and_response
def update_adhoc_drug_request_by_fndc_txr_daw(data: Dict[str, Any], unique_id: str, fndc_txr_daw: str) -> bool:
    """
    Updates the record for the given drug_id and the unique_id.
    """
    try:
        return AdhocDrugRequest.update_adhoc_drug_request_by_fndc_txr_daw(data=data, unique_id=unique_id,
                                                                          fndc_txr_daw=fndc_txr_daw)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_adhoc_drug_request_by_fndc_txr_daw".format(e))
        raise e


@log_args_and_response
def update_adhoc_drug_request_by_fndc_txr_daw_case(data, unique_id):
    """
    Updates the record for the given drug_id and the unique_id.
    """
    ext_is_success_tuple_list = []
    ext_note_list = []
    fndc_txr_daws = []
    try:
        for key, value in data.items():
            ext_is_success_tuple_list.append((key, value['ext_is_success']))
            ext_note_list.append((key, value['ext_note']))
            fndc_txr_daws.append(key)
        ext_success_case = case(fn.CONCAT(AdhocDrugRequest.formatted_ndc, "##", AdhocDrugRequest.txr, "##",
                                          AdhocDrugRequest.daw), ext_is_success_tuple_list)
        ext_note_case = case(fn.CONCAT(AdhocDrugRequest.formatted_ndc, "##", AdhocDrugRequest.txr, "##",
                                       AdhocDrugRequest.daw), ext_note_list)
        return AdhocDrugRequest.update_adhoc_drug_request_by_fndc_txr_daw_case(ext_success_case=ext_success_case,
                                                                               ext_note_case=ext_note_case,
                                                                               unique_id=unique_id,
                                                                               fndc_txr_daws=fndc_txr_daws)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_adhoc_drug_request_by_fndc_txr_daw".format(e))
        raise e

@log_args_and_response
def delete_adhoc_drug_request_data(delete_list: List[str], unique_id: str) -> bool:
    """
    Updates the status as deleted of the given list of drug_ids and the given unique_id.
    """
    try:
        return AdhocDrugRequest.delete_data(delete_list=delete_list, unique_id=unique_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in delete_adhoc_drug_request_data".format(e))
        raise e


@log_args_and_response
def update_adhoc_drug_request_by_ndc(data: Dict[str, Any], unique_id: str, ndc: str) -> bool:
    """
    Updates the record for the given drug_id and the facility_dist_id.
    """
    try:
        return AdhocDrugRequest.update_adhoc_drug_request_by_ndc(data=data, unique_id=unique_id, ndc=ndc)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_adhoc_drug_request_by_ndc".format(e))
        raise e


@log_args_and_response
def populate_batch_pack_data(batch_pack_data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts data in the BatchPackData table.
    """
    try:
        BatchPackData.insert_data(data_list=batch_pack_data_list)
        return True
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_batch_pack_data".format(e))
        raise e


@log_args_and_response
def get_fndc_txr_with_canister(fndc_txr_list: List[str]) -> List[str]:
    """
    Returns the list of fndc_txr with canisters, out of the given list of fndc_txr.
    """
    result_list: List[str] = list()
    try:
        query = DrugMaster.select(fn.CONCAT(DrugMaster.formatted_ndc, "##", DrugMaster.txr).alias("fndc_txr"),
                                  fn.GROUP_CONCAT(CanisterMaster.id).coerce(False).alias("canister_id_list"),
                                  fn.GROUP_CONCAT(CanisterMaster.active).coerce(False).alias("active_list"),
                                  fn.GROUP_CONCAT(CanisterMaster.drug_id).coerce(False).alias("drug_id_list")).dicts() \
            .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .where(fn.CONCAT(DrugMaster.formatted_ndc, "##", DrugMaster.txr).in_(fndc_txr_list),
                   CanisterMaster.active == 1) \
            .group_by(fn.CONCAT(DrugMaster.formatted_ndc, "##", DrugMaster.txr))

        for data in query:
            result_list.append(data["fndc_txr"])
        return result_list

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_fndc_txr_with_canister".format(e))
        raise e


@log_args_and_response
def get_facility_dist_data_by_id(facility_dist_id: int) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    """
    Get the data from FacilityDistributionMaster for the given id
    """
    try:
        return FacilityDistributionMaster.db_get_dept_data_by_id(facility_dist_id=facility_dist_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_facility_dist_data_by_id".format(e))
        raise e


@log_args_and_response
def update_facility_dist_data_by_id(update_data: Dict[str, Any], facility_dist_id: int) -> bool:
    """
    Update FacilityDistributionMaster by id
    """
    try:
        return FacilityDistributionMaster.db_update_by_id(update_dict=update_data, facility_dist_id=facility_dist_id)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in update_facility_dist_data_by_id".format(e))
        raise e


def update_based_on_order(facility_dist_id: int, unique_alt_drug_id_list: List[str], user_id: int) -> bool:
    """
    Update the Table with active for ordered and inactive for others.
    @param facility_dist_id:
    @param unique_alt_drug_id_list:
    @param user_id:
    @return:
    """

    update_dict_for_ordered: Dict[str, Any] = {"active": True,
                                               "modified_by": user_id,
                                               "modified_date": get_current_date_time()}
    try:
        AlternateDrugOption.update(**update_dict_for_ordered) \
            .where(AlternateDrugOption.facility_dis_id == facility_dist_id,
                   fn.CONCAT(AlternateDrugOption.unique_drug_id, "##", AlternateDrugOption.alternate_unique_drug_id).in_(unique_alt_drug_id_list)) \
            .execute()
        return True
    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_based_on_order".format(e))
        raise e


@log_args_and_response
def get_last_order_data_ny_ndc(ndc_list):
    """

    """
    ndc_alternate_ndc_dict = {}
    all_ndc_list = []
    ordering_data = {}

    try:
        query = BatchDrugData.select(
        BatchDrugData.formatted_ndc,
        BatchDrugData.txr,
        BatchDrugData.daw,
        BatchDrugData.ndc,
        BatchDrugData.req_qty,
        BatchDrugData.order_qty,
        BatchDrugData.department,
        BatchDrugData.status_id,
        BatchDrugData.ext_is_success,
        BatchDrugData.ext_note,
        BatchDrugOrderData.ndc.alias("b_ndc"),
        BatchDrugOrderData.original_qty,
        BatchDrugOrderData.daw.alias('b_daw'),
        BatchDrugOrderData.pack_size,
        BatchDrugOrderData.pack_unit,
        BatchDrugOrderData.cfi,
        BatchDrugOrderData.is_ndc_active,
        BatchDrugOrderData.is_sub,
        BatchDrugOrderData.sub_reason,
        BatchDrugOrderData.pre_ordered_ndc,
        BatchDrugOrderData.pre_ordered_qty,
        BatchDrugOrderData.pre_ordered_pack_size,
        BatchDrugOrderData.pre_ordered_pack_unit,
        BatchDrugOrderData.is_processed,
        BatchDrugOrderData.message
        # BatchDrugOrderData.created_by,
        # BatchDrugOrderData.created_date,
        # BatchDrugOrderData.modified_by,
        # BatchDrugOrderData.modified_date,
                                     ).dicts() \
            .join(BatchDrugOrderData, on=BatchDrugData.id == BatchDrugOrderData.batch_drug_data_id) \
            .where(BatchDrugData.ndc << ndc_list).order_by(BatchDrugData.created_date.desc())

        for record in query:
            req_ndc = record['ndc']
            req_fndc = record['formatted_ndc']

            order_ndc = record['pre_ordered_ndc']
            txr = record['txr']
            cfi = record['cfi']
            # if req_ndc != order_ndc:
            #     if txr != cfi:
            if req_ndc not in ordering_data:
                ordering_data[req_ndc] = record
            if req_ndc not in ndc_alternate_ndc_dict:
                ndc_alternate_ndc_dict[req_ndc] = order_ndc
                all_ndc_list.append(req_ndc)
                all_ndc_list.append(order_ndc)
        return ndc_alternate_ndc_dict, all_ndc_list, ordering_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_based_on_order".format(e))
        raise e




def get_current_batch_drug_data_by_department(facility_dist_id: int) -> Any:
    """
    Update the Table with active for ordered and inactive for others.
    @param facility_dist_id:
    @param unique_alt_drug_id_list:
    @param user_id:
    @return:
    """

    batch_drug_data = {}
    try:
        query = BatchDrugData.select().dicts().where(BatchDrugData.facility_dist_id == facility_dist_id)
        for record in query:
            if record['ndc'] not in batch_drug_data:
                batch_drug_data[record['ndc']] = record
        return batch_drug_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_based_on_order".format(e))
        raise e


@log_args_and_response
def populate_batch_drug_and_order_data(ordering_data, facility_dist_id, user_id, actual_order):
    batch_drug_order_data_insert_dict = []
    try:

        batch_order_data = get_current_batch_drug_data_by_department(facility_dist_id)

        for ndc, record in ordering_data.items():
            batch_drug_id = batch_order_data[ndc]['id']
            order_qty = batch_order_data[ndc]['order_qty']
            update_batch_drug_data_dict = {"ext_is_success": True,
                                           "ext_note": "From Past Ordering",
                                           "modified_by": user_id,
                                           "modified_date": get_current_date_time()}
            update_batch_drug_data_by_ndc(data=update_batch_drug_data_dict, facility_dist_id=facility_dist_id,
                                          ndc=ndc)
            

            batch_drug_order_data = {
            "batch_drug_data_id": batch_drug_id,
            "ndc" : record["b_ndc"],
            "original_qty" : record["original_qty"],
            "daw" : record["b_daw"],
            "pack_size" : record["pack_size"],
            "pack_unit" : record["pack_unit"],
            "cfi" : record["cfi"],
            "is_ndc_active" : record["is_ndc_active"],
            "is_sub" : record["is_sub"],
            "sub_reason" :  "From Past Orders" if record["is_sub"] else None,
            "pre_ordered_ndc" : record["pre_ordered_ndc"],
            "pre_ordered_qty" : order_qty,
            "pre_ordered_pack_size" : record["pre_ordered_pack_size"],
            "pre_ordered_pack_unit" : record["pre_ordered_pack_unit"],
            "is_processed" : True,
            "message" : "From Past Ordering",
            "created_by" : user_id,
            "modified_by" : user_id
            }
            batch_drug_order_data_insert_dict.append(batch_drug_order_data)
        if batch_drug_order_data_insert_dict:
            status = BatchDrugOrderData.insert_many(batch_drug_order_data_insert_dict).execute()

    except (InternalError, IntegrityError, DatabaseError) as e:
        logger.error("Error in populate_batch_drug_and_order_data".format(e))
        raise e


@log_args_and_response
def remove_bypassed_ordering(facility_distribution_id: int):
    """
    get alternate drug option data
    @param facility_distribution_id:
    @param type:
    @return:

    """
    batch_drug_order_id = []
    try:

        status = FacilityDistributionMaster.select(FacilityDistributionMaster.ordering_bypass).where(
            FacilityDistributionMaster.id == facility_distribution_id).scalar()

        if status:
            batch_drug_order_query = BatchDrugOrderData.select(BatchDrugOrderData.id).dicts()\
                .join(BatchDrugData, on=BatchDrugData.id == BatchDrugOrderData.batch_drug_data_id) \
                .where(BatchDrugData.facility_dist_id == facility_distribution_id)

            batch_drug_order_id = [record["id"] for record in batch_drug_order_query]
            if batch_drug_order_id:
                with db.transaction():
                    try:
                        BatchDrugOrderData.delete().where(BatchDrugOrderData.id << batch_drug_order_id).execute()
                        BatchDrugData.delete().where(BatchDrugData.facility_dist_id == facility_distribution_id).execute()
                        AlternateDrugOption.delete().where(AlternateDrugOption.facility_dis_id == facility_distribution_id).execute()

                        # update facilility with null
                        update_dict = {"ordering_bypass": None}
                        update_facility_dist_data_by_id(update_data=update_dict, facility_dist_id=facility_distribution_id)
                    except DoesNotExist as e:
                        pass

        return True
    except (InternalError, IntegrityError) as e:
        logger.error("Error in remove_bypassed_ordering {}".format(e))
        raise e


@log_args_and_response
def populate_inventory_transaction_history_data(transaction_dict) -> bool:
    """
    Inserts data in the BatchPackData table.
    """
    try:
        InventoryTransactionHistory.insert_data(data_list=transaction_dict)
        return True
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in populate_inventory_transaction_history_data".format(e))
        raise e


@log_args_and_response
def drug_inventory_adjustment(args):
    """
    When user mark drug as out of stock or exipred or count drugs while reconciliation, Notify ELite

    """
    canister_dict = args.get('canister_dict')
    on_shelf_dict = args.get('on_shelf_dict')
    transaction_type = args.get('transaction_type')
    user_details = args.get('user_details')
    case_id = args.get("case_id")
    created_list = []
    deleted_list = []
    updated_list = []
    inventory_response = []
    case_quantity_dict = args.get("case_quantity_dict", {})
    ndc_list = args.get("ndc_list", [])

    try:
        current_date = get_current_datetime_by_timezone(settings.DEFAULT_TIME_ZONE, "datetime")
        # current_date = get_current_date_time()
        if case_quantity_dict:
            for case_id, quantity in case_quantity_dict.items():
                note = args.get('note', "")
                ndc = ndc_list[0]
                create_dict = {
                    # "uid": unique_id,
                    "ndc": int(ndc),
                    "quantity": float(quantity),
                    "adjustmentDate": current_date,
                    "typeOfTransaction": transaction_type,
                    "note": "by {}".format(user_details['name']) if not note else "{} , by {}".format(note,
                                                                                                      user_details[
                                                                                                          'name']),
                    # "lotNumber": None,
                    "expirationDate": None,
                    "caseId": case_id
                }
                if args.get("is_replenish"):
                    create_dict['isCanisterAdjustment'] = True
                created_list.append(create_dict)
        elif transaction_type in [settings.EPBM_QTY_ADJUSTMENT_KEY,
                                settings.EPBM_DRUG_ADJUSTMENT_DECREMENT,
                                settings.EPBM_DRUG_ADJUSTMENT_INCREMENT]:
            note = args.get('note', "")

            if 'drug_data' in args:
                drug_data = args.get('drug_data')
                final_drug_count = args.get('final_drug_count')

                for drug_id, record in drug_data.items():
                    final_drug_count.setdefault(drug_id, {})
                    create_dict = {
                        # "uid": unique_id,
                        "ndc": int(record['ndc']),
                        "quantity": float(final_drug_count[drug_id].get('quantity', 0)),
                        "adjustmentDate": current_date,
                        "typeOfTransaction": transaction_type,
                        "note": "by {}".format(user_details['name']) if not note else "{} , by {}".format(note,user_details['name']),
                        # "lotNumber": None,
                        "expirationDate": None,
                        "caseId": case_id
                    }
                    if args.get("is_replenish"):
                        create_dict['isCanisterAdjustment'] = True
                    created_list.append(create_dict)

        elif transaction_type == settings.EPBM_EXPIRY:

            expiry_list = args.get('expiry_list')
            if expiry_list:
                for record in expiry_list:
                    ndc = int(record['ndc'])
                    trash_qty = float(record['trash_qty'])
                    lot_number = record['lot_number']
                    expiry_date = record['expiry_date']
                    case_id = record["case_id"]
                    note = record.get('note', "")
                    create_dict = {
                        # "uid": unique_id,
                        "ndc": ndc,
                        "quantity": trash_qty,
                        "adjustmentDate": current_date,
                        "typeOfTransaction": transaction_type,
                        "note": "{}, by {}".format(note, user_details['name']),
                        "lotNumber": lot_number,
                        "expirationDate": str(expiry_date),
                        "caseId": case_id
                    }
                    if args.get("is_replenish"):
                        create_dict['isCanisterAdjustment'] = True
                    created_list.append(create_dict)

        if created_list:
            inventory_response = post_adjustment_data_to_drug_inventory(created_list=created_list,
                                                                        updated_list=updated_list,
                                                                        deleted_list=deleted_list)
            if inventory_response:

                #  Insert data into inventory_transaction_history
                status = populate_inventory_transaction_history_data(created_list)

        return inventory_response

    except APIFailureException as e:
        logger.error(e)
        raise e
    except TokenFetchException as e:
        logger.error(e)
        raise e
    except DrugInventoryInternalException as e:
        logger.error(e)
        raise e
    except DrugInventoryValidationException as e:
        logger.error(e)
        raise e

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in drug_inventory_adjustment: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in drug_inventory_adjustment: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def check_drug_inventory(ndc_list, case_list=None):
    try:
        response_list = []
        ndc_list: List[str] = list(ndc_list.split(','))
        if case_list:
            case_list: List[str] = list(case_list.split(','))
        logger.info("inside function check_drug_inventory")

        drug_ids, ndc_data = get_drug_list_from_case_id_ndc(ndc_list, case_list)

        # in this case ndc is available in elite but not available in dosepack
        if not drug_ids:
            for item in ndc_list:
                response = {"ndc": item,
                            "ndc_present": False,
                            "case_data": [
                                {
                                    "case_id": None,
                                    "case_quantity": 0
                                }
                            ],
                            "quantity": 0}
                response_list.append(response)
        if response_list:
            final_response_dict = {"ndc_data": response_list}
            return create_response(final_response_dict)

        # # 1 get progress & partially filled packs
        robot_packs_qty = get_filled_drug_count_slot_transaction(drug_ids)

        # 2 get mfd filled drug count
        mfd_drugs = get_mfd_filled_drug_count(drug_ids)

        # 3 get partially filled packs
        partial_packs_qty = get_manual_partially_filled_packs_drug_count(drug_ids)

        # 4 get canister filled quantity
        canister_qty = db_get_total_canister_quantity_by_drug_id(drug_ids)

        # final_drug_count = {
        #     key: int(robot_packs_qty.get(key, 0)) + int(mfd_drugs.get(key, 0)) + int(partial_packs_qty.get(key, 0))
        #          + int(canister_qty.get(key, 0))
        #     for key in set(robot_packs_qty) | set(mfd_drugs) | set(partial_packs_qty) | set(canister_qty)
        # }
        final_drug_count = {}

        data_dicts = [robot_packs_qty, mfd_drugs, partial_packs_qty, canister_qty]
        for data_dict in data_dicts:
            for drug_id, drug_data in data_dict.items():
                for case_id, quantity in drug_data.items():
                    final_drug_count.setdefault(drug_id, dict())
                    final_drug_count[drug_id][case_id] = int(final_drug_count[drug_id].get(case_id, 0)) + quantity

        final_drug_count_ndc_wise = {}
        for drug_id, drug_data in final_drug_count.items():
            if drug_id in ndc_data.keys():
                final_drug_count_ndc_wise.setdefault(ndc_data[drug_id], dict())
                for key, value in drug_data.items():
                    final_drug_count_ndc_wise[ndc_data[drug_id]].setdefault(ndc_data[drug_id],dict())
                    final_drug_count_ndc_wise[ndc_data[drug_id]][ndc_data[drug_id]]['case_id'] = key
                    final_drug_count_ndc_wise[ndc_data[drug_id]][ndc_data[drug_id]]['case_quantity'] = value
                final_drug_count_ndc_wise[ndc_data[drug_id]].setdefault('quantity', 0)
                for value in drug_data.values():
                    final_drug_count_ndc_wise[ndc_data[drug_id]]['quantity'] += value
        response_dict = {}

        for ndc, ndc_data in final_drug_count_ndc_wise.items():
            response_dict['ndc'] = ndc
            response_dict['case_data'] = []
            response_dict['quantity'] = ndc_data['quantity']
            for ndc1, case_data in ndc_data.items():
                if 'quantity' not in ndc1:
                    response_dict['case_data'].append(case_data)

            response_list.append(response_dict)

        if not len(response_list):
            for item in ndc_list:
                response = {"ndc": item,
                            "case_data": [
                                {
                                    "case_id": None,
                                    "case_quantity": 0
                                }
                            ],
                            "quantity": 0}
                response_list.append(response)

        final_response_dict = {"ndc_data": response_list}
        # final_drug_count_ndc_wise_list = list(final_drug_count_ndc_wise.values())

        return create_response(final_response_dict)

    except Exception as e:
        logger.error("error occured in check_drug_inventory {}".format(e))
        return e


@log_args_and_response
def db_create_record_in_adhoc_drug_request(insert_dict):
    try:
        AdhocDrugRequest.insert_many(insert_dict).execute()
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in db_create_record_in_adhoc_drug_request: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in db_create_record_in_adhoc_drug_request: {}".format(e), exc_info=True)
        raise e