import calendar
from datetime import datetime
import datetime
import functools
import json
import math
import operator
import os
import sys
import threading
import pytz
# from _ast import operator
from collections import defaultdict, OrderedDict
from decimal import Decimal
from itertools import cycle
from typing import List, Dict, Any, Optional

from dateutil.relativedelta import relativedelta
from peewee import InternalError, IntegrityError, DataError, DoesNotExist, fn, JOIN_LEFT_OUTER, Clause, SQL, logger
from playhouse.shortcuts import case, cast

import settings
from com.pharmacy_software import send_data
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import convert_date_from_sql_to_display_date, log_args_and_response, \
    convert_dob_date_to_sql_date, is_date, get_current_date_time, get_current_date, retry, log_args_and_response_dict, \
    get_current_date_time_as_per_time_zone, last_day_of_month, convert_utc_timezone_into_local_time_zone
from dosepack.validation.validate import validate
from migrations.migration_for_zone_implementation_in_canister_master import CanisterZoneMapping
from model import model_init
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from src import constants
from src.api_utility import get_filters, get_multi_search, apply_paginate, get_orders, get_expected_delivery_date, \
    get_pack_module, get_results
from src.constants import MFD_CANISTER_MVS_FILLING_REQUIRED, MFD_CANISTER_RTS_REQUIRED_STATUS, REUSE_REQUIRED, RESEALED
from src.dao.batch_dao import get_batch_id_from_pack_list, get_pack_count_by_batch, get_next_pending_batches, \
    get_batch_scheduled_start_date
from src.dao.canister_transfers_dao import update_canister_tx_meta_by_batch_id
from src.dao.company_setting_dao import get_ips_communication_settings_dao
from src.dao.dashboard_dao import db_get_pharmacy_master_data_dao
from src.dao.drug_dao import get_expiry_date_of_filled_pack, get_ordered_list, dpws_paginate
from src.dao.ext_change_rx_dao import db_get_new_pack_details_for_template, db_get_pack_ids_by_pack_display_id_dao
from src.dao.mfd_dao import db_update_canister_status, concatenate_fndc_txr_dao
from src.dao.pack_analysis_dao import db_get_pack_analysis
from src.dao.pack_distribution_dao import transfer_canister_recommendation, save_transfers, save_analysis, \
    PackDistributorV3, PackDistributor
from src.dao.pack_ext_dao import update_ext_pack_data, update_ext_pack_usage_status, db_get_storage_by_pack_display_id
from src.dao.misc_dao import get_system_setting_by_system_id
from src.exceptions import PharmacySoftwareResponseException, PharmacySoftwareCommunicationException
from src.model.model_batch_manual_packs import BatchManualPacks
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_tx_meta import CanisterTxMeta
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_code_master import CodeMaster

from src.model.model_company_setting import CompanySetting
from src.model.model_consumable_tracker import ConsumableTracker
from src.model.model_consumable_used import ConsumableUsed
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_doctor_master import DoctorMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_status import DrugStatus
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_tracker import DrugTracker
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_facility_schedule import FacilitySchedule
from src.model.model_file_header import FileHeader
from src.model.model_fill_error_details import FillErrorDetails
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_mfd_canister_transfer_history import MfdCanisterTransferHistory
from src.model.model_missing_drug_pack import MissingDrugPack
from src.model.model_overloaded_pack_timings import OverLoadedPackTiming
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_drug_tracker import PackDrugTracker
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_pack_history import PackHistory
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_user_map import PackUserMap
from src.model.model_pack_verification import PackVerification
from src.model.model_pack_verification_details import PackVerificationDetails
from src.model.model_partially_filled_pack import PartiallyFilledPack
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_pharmacy_master import PharmacyMaster
from src.model.model_pill_fill_error import PillJumpError
from src.model.model_print_queue import PrintQueue
from src.model.model_pvs_dimension import PVSDimension
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_reuse_pack_drug import ReusePackDrug
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_template_master import TemplateMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_vision_drug_count import VisionCountPrediction
from src.model.model_vision_drug_prediction import VisionDrugPrediction
from src.model.model_zone_master import ZoneMaster
from dosepack.base_model.base_model import BaseModel
from src.service.misc import update_canister_transfer_wizard_data_in_couch_db, get_token, get_current_user, \
    update_notifications_couch_db_status, get_users_by_ids
from src.service.notifications import Notifications
from utils.drug_inventory_webservices import get_current_inventory_data, \
    create_item_vial_generation_for_rts_reuse_pack

logger = settings.logger


@log_args_and_response
def get_pack_details_dao(pack_id, device_id, company_id, non_fractional=False, module_id=None):
    """
    Fetches pack data and slot data for robot(optionally).

    :param pack_id:
    :param device_id:
    :param company_id:
    :param non_fractional:
    :return:
    """
    logger.debug("Inside get_pack_details_dao")
    pack_details_data = None
    linked_packs_list: List[int] = []
    asrs_dict: Dict[str, Any] = {}
    try:
        filled_flow_tuple = [(0, 'Auto'),
                             (1, 'Marked manual during Batch Distribution'),
                             (2, 'Marked manual from Pack Queue'),
                             (3, 'Marked manual from Manual Verification Station'),
                             (4, 'Marked manual during Pack Pre-Processing'),
                             (11, 'Processed by Drug Dispenser')
                             ]
        sub_query = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                          ExtPackDetails.pack_id.alias('pack_id')) \
            .group_by(ExtPackDetails.pack_id).alias('sub_query')

        fields_dict = {"filled_flow": fn.IF(
                           PackUserMap.id.is_null(True),
                           case(PackDetails.filled_at, filled_flow_tuple, default='DosePacker'),
                           "Processed by Manual Pack Filling"
                       )}
        query = PackDetails.select(
                PackDetails.id,
                PackDetails.pack_display_id,
                PackDetails.pack_no,
                PackDetails.created_date,
                PackDetails.pack_status,
                PackDetails.pack_header_id,
                PackDetails.rfid,
                fn.CONCAT(PackDetails.consumption_start_date, ' to ', PackDetails.consumption_end_date).alias(
                    'admin_period'),
                PackHeader.patient_id,
                fields_dict['filled_flow'].alias('filled_flow'),
                PackDetails.filled_at,
                PackHeader.delivery_datetime,
                PatientMaster.last_name,
                PatientMaster.first_name,
                PatientMaster.dob,
                PatientMaster.allergy,
                PatientMaster.patient_no,
                FacilityMaster.facility_name,
                PatientMaster.facility_id,
                PatientMaster.pharmacy_patient_id,
                PackDetails.order_no,
                PackDetails.container_id,
                ContainerMaster.drawer_name.alias('storage_container_name'),
                PackDetails.pack_plate_location,
                PackDetails.batch_id,
                PackUserMap.id.alias("pack_user_id"),
                PackDetails.facility_dis_id,
                BatchMaster.status.alias('batch_status'),
                CodeMaster.value,
                CodeMaster.id.alias('pack_status_id'),
                # PackVerification.pack_fill_status,
                PackUserMap.assigned_to,
                PackDetails.fill_time,
                ExtPackDetails.ext_status_id.alias('ext_pack_status_id'),
                ExtPackDetails.pack_usage_status_id.alias("ext_pack_usage_status_id"),
                ExtPackDetails.pharmacy_pack_status_id.alias('pharmacy_pack_status_id'),
                PackHeader.change_rx_flag,
                PackDetails.consumption_start_date.alias("consumption_start_date"),
                PackDetails.consumption_end_date.alias("consumption_end_date"),
                FillErrorDetails.assigned_to.alias("fill_error_assigned_to"),
                FillErrorDetails.reported_by,
                FillErrorDetails.fill_error_note,
                PackDetails.filled_by,
                PackDetails.packaging_type,
                PackDetails.store_type,
                PackDetails.filled_date,
                FillErrorDetails.modified_date.alias("reported_date"),
                PackDetails.verification_status,
                PackDetails.pack_checked_by
        ).order_by(
            PackDetails.created_date
        ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == PackDetails.container_id) \
                .join(PackUserMap, JOIN_LEFT_OUTER, on=PackDetails.id == PackUserMap.pack_id) \
                .join(sub_query, JOIN_LEFT_OUTER, on=(sub_query.c.pack_id == PackDetails.id)) \
                .join(ExtPackDetails, JOIN_LEFT_OUTER, on=ExtPackDetails.id == sub_query.c.max_ext_pack_details_id) \
                .join(FillErrorDetails, JOIN_LEFT_OUTER, on=FillErrorDetails.pack_id == PackDetails.id) \
                .join(PackRxLink, JOIN_LEFT_OUTER, on=PackRxLink.pack_id == PackDetails.id) \
                .join(PatientRx, JOIN_LEFT_OUTER, on=PackRxLink.patient_rx_id == PatientRx.id)  \
            .where(PackDetails.id == pack_id, PackDetails.company_id == company_id)
        for record in query:

            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])

            if device_id:
                slot_list, max_location, missing_canisters, batch_id = \
                    db_slot_details(pack_id, device_id, company_id, non_fractional)
                record["SlotList"] = slot_list
                record["max_location"] = max_location
                record["missing_canisters"] = missing_canisters
                record["batch_id"] = batch_id

            record["pack_status"] = record["value"]
            record["patient_name"] = record["patient_name"]
            record["facility_name"] = record["facility_name"]
            record["pack_id"] = record["id"]
            record["cyclic_pack"] = 1 if record["store_type"] == constants.STORE_TYPE_CYCLIC else 0
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            record['module'] = get_pack_module(pack_status=record['pack_status_id'], batch_id=record['batch_id'],
                                               batch_status=record['batch_status'],
                                               facility_dist_id=record['facility_dis_id'],
                                               user_id=record['pack_user_id'])

            linked_packs_list = []
            asrs_dict = {}
            linked_pack_status = {}
            if record["change_rx_flag"]:
                logger.debug("Fetch the Old Packs List as current Pack falls in the category of Change Rx...")
                # query to get last ChangeRx received for any Template.
                # sub_q_ext_change_rx = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
                #                                             fn.max(ExtChangeRx.id).alias("ext_change_rx_id")) \
                #     .join(ExtChangeRx, on=ExtChangeRx.new_template == TemplateMaster.id) \
                #     .where(TemplateMaster.patient_id == record["patient_id"],
                #            TemplateMaster.file_id == record["file_id"]) \
                #     .group_by(TemplateMaster.id).alias("sub_q_ext_change_rx")

                # Link last ChangeRx with affected Packs for providing reference to user
                sub_q_ext_change_rx_pack = \
                    ExtPackDetails.select(ExtPackDetails.ext_pack_display_id,
                                          fn.IF(ExtPackDetails.pharmacy_pack_status_id.is_null(True), None,
                                                CodeMaster.value).alias("pharmacy_pack_status"),
                                          ExtPackDetails.pharmacy_pack_status_id) \
                    .join(PackDetails, on=ExtPackDetails.pack_id == PackDetails.id) \
                    .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                    .join(CodeMaster, JOIN_LEFT_OUTER, on=ExtPackDetails.pharmacy_pack_status_id == CodeMaster.id) \
                    .join(TemplateMaster, on=((PackHeader.patient_id == TemplateMaster.patient_id) &
                                              (PackHeader.file_id == TemplateMaster.file_id))) \
                    .where(PackHeader.patient_id == record["patient_id"],
                           ExtPackDetails.pack_usage_status_id == constants.EXT_PACK_USAGE_STATUS_PENDING_ID,
                           ExtPackDetails.status_id << settings.PACK_PROGRESS_DONE_STATUS_LIST,
                           TemplateMaster.fill_start_date <= PackDetails.consumption_start_date,
                           TemplateMaster.fill_end_date >= PackDetails.consumption_end_date)

                for ext_pack_data in sub_q_ext_change_rx_pack.dicts():
                    if ext_pack_data['ext_pack_display_id'] not in linked_packs_list:
                        linked_packs_list.append(ext_pack_data['ext_pack_display_id'])
                    if ext_pack_data['ext_pack_display_id'] not in linked_pack_status:
                        linked_pack_status[ext_pack_data['ext_pack_display_id']] = ext_pack_data['pharmacy_pack_status']
                if linked_packs_list:
                    asrs_dict = db_get_storage_by_pack_display_id(pack_display_ids=linked_packs_list,
                                                                      company_id=company_id)
            record["linked_packs"] = linked_packs_list
            record["linked_pack_status"] = linked_pack_status

            if asrs_dict:
                record["asrs_info"] = asrs_dict
            pack_details_data = record

        logger.debug("In get_pack_details_dao, pack_details_data fetched.")

        return pack_details_data

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def check_packs_in_pack_queue_for_system(system_id):
    try:
        available_pack_queue = False
        query = PackQueue.select().dicts() \
                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                .where(PackDetails.system_id == system_id)
        for data in query:
            return True

        return available_pack_queue

    except Exception as e:
        logger.error(f"Error in check_packs_in_pack_queue_for_system, e: {e}")

@log_args_and_response
def db_get_pack_wise_drug_data_dao(pack_list):
    """
    Return drug_data for given pack list
    @param pack_list:
    @return:
    """

    try:
        DrugMasterAlias1 = DrugMaster.alias()
        drug_list = set()
        query = DrugMaster.select(fn.IF(DrugMasterAlias1.id.is_null(True), DrugMaster.id,
                                        DrugMasterAlias1.id).alias("id"),
                                  fn.IF(DrugMasterAlias1.ndc.is_null(True), DrugMaster.ndc,
                                        DrugMasterAlias1.ndc).alias("ndc"),
                                  fn.IF(DrugMasterAlias1.formatted_ndc.is_null(True), DrugMaster.formatted_ndc,
                                        DrugMasterAlias1.formatted_ndc).alias("formatted_ndc"),
                                  fn.IF(DrugMasterAlias1.txr.is_null(True), DrugMaster.txr,
                                        DrugMasterAlias1.txr).alias("txr"),
                                  fn.IF(DrugMasterAlias1.brand_flag.is_null(True), DrugMaster.brand_flag,
                                        DrugMasterAlias1.brand_flag).alias("brand_flag"),
                                  PatientRx.daw_code).dicts()\
            .join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id)\
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)\
            .join(DrugTracker, JOIN_LEFT_OUTER, on=SlotDetails.id == DrugTracker.slot_id) \
            .join(DrugMasterAlias1, JOIN_LEFT_OUTER, on=DrugMasterAlias1.id == DrugTracker.drug_id) \
            .where(PackRxLink.pack_id << pack_list).group_by(
            fn.IF(DrugTracker.drug_id.is_null(False), DrugTracker.drug_id, SlotDetails.drug_id))

        for data in query:
            drug_list.add(data["ndc"])

        return query, drug_list

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return None
    except InternalError as e:
        logger.error(e, exc_info=True)
        return None


@log_args_and_response
def slot_details_for_vision_system_dao(pack_id, device_id, system_id):
    pack_details = {}
    slot_list = defaultdict(lambda: defaultdict(float))

    try:
        pack_data = get_pack_details_dao(pack_id, device_id, system_id)
        if "status" in pack_details:  # status will be thrown in case of error otherwise it will have pack_details_data
            return None
        pack_details["pack_data"] = pack_data

        for record in SlotHeader.select(PackGrid.slot_row, PackGrid.slot_column, SlotDetails.quantity,
                                        SlotDetails.is_manual,
                                        DrugMaster.id.alias("drug_id"), DrugMaster.drug_name,
                                        DrugMaster.ndc).dicts() \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
                .where(SlotHeader.pack_id == pack_id).distinct():
            record["quantity"] = float(record["quantity"])

            location = map_pack_location_dao(record["slot_row"], record["slot_column"])
            slot_list[location][record["drug_id"]] += record["quantity"]

        pack_details["slot_data"] = slot_list
        return pack_details

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return None
    except InternalError as e:
        logger.error(e, exc_info=True)
        return None


@log_args_and_response
def get_deleted_packs(pack_ids: list, company_id: int) -> tuple:
    """
    Return deleted packs out of pack_ids
    @param company_id:
    @param pack_ids:
    @return:
    """
    logger.debug("Inside get_deleted_packs")
    try:
        deleted_packs = list()
        deleted_pack_display_ids = list()
        query = PackDetails.select(PackDetails.id, PackDetails.pack_display_id).dicts() \
            .where(PackDetails.id << pack_ids,
                   PackDetails.pack_status == settings.DELETED_PACK_STATUS,
                   PackDetails.company_id == company_id)

        logger.info("In get_deleted_packs, query: {}".format(list(query)))

        for record in query:
            deleted_packs.append(record['id'])
            deleted_pack_display_ids.append(record['pack_display_id'])

        return deleted_packs, deleted_pack_display_ids
    except InternalError as e:
        raise e
    except Exception as e:
        logger.error("Error in get_deleted_packs: {}".format(e))
        raise e


@log_args_and_response
def add_missing_drug_record_dao(missing_drug_list_dict: List[Dict[str, Any]]):
    missing_drug_list_insert_dict: List[Dict[str, Any]] = list()
    drug_list = []

    try:
        for item in missing_drug_list_dict:
            query = (PackRxLink.select(PackRxLink.id,
                                      SlotDetails.drug_id).dicts() \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)\
                .where(PackRxLink.pack_id << item["pack_ids"],
                       PatientRx.pharmacy_rx_no << item["rx_no_list"])
                     .group_by(PackRxLink.id))

            for record in query:
                # For marking out of stock drug list is added.
                drug_list.append(record['drug_id'])
                missing_drug_list_insert_dict.append({"pack_rx_id": record["id"], "created_by": item["created_by"],
                                                      "created_date": item["created_date"]})

        return MissingDrugPack.add_missing_drug_record(missing_drug_list_insert_dict), drug_list
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_filling_pending_pack_ids(company_id=None) -> list:
    """
    Return filling pending  pack ids
    @param batch_id:
    @return:
    """
    try:
        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids(company_id=company_id)

        return filling_pending_pack_ids
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_filling_pending_pack_ids {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_filling_pending_pack_ids: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_batch_id_from_packs(all_pack_list: list) -> int:
    """
    Return batch id from pack ids
    @param all_pack_list:
    @return:
    """
    try:
        batch_id = PackDetails.db_get_batch_id_from_packs(pack_list=all_pack_list)
        return batch_id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_batch_id_from_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_batch_id_from_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_packs_by_facility(pack_list: list) -> defaultdict:
    """
        Return dict of packs  by facility(facility id as key and packs as value)
        @param pack_list:
        @return:
    """
    logger.debug("Inside get_packs_by_facility")
    try:
        query = PackDetails.select(FacilityMaster.id.alias('f_id'),
                                   PackDetails.id.alias('packs')) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.id << pack_list) \
            .group_by(PackDetails.id)
        facility_packs = defaultdict(set)

        for record in query.dicts():
            facility_packs[record['f_id']].add(record['packs'])
        return facility_packs

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in db_get_packs_by_facility {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in db_get_packs_by_facility: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_filled_packs_count_for_latest_batch(latest_batch_id: int):
    """
    get filled pack count for latest batch
    :return: bool
    """
    try:
        filled_pack_count = PackDetails.db_get_filled_pack_count(latest_batch_id)
        return filled_pack_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_filled_packs_count_for_latest_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_filled_packs_count_for_latest_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_filled_packs_count_for_latest_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_filled_packs_count_for_latest_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_total_packs_count_for_batch(latest_batch_id: int):
    """
    get total pack count for batch
    :return: bool
    """
    try:
        total_pack_count = PackDetails.db_get_total_packs_count_for_batch(latest_batch_id)
        return total_pack_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_total_packs_count_for_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_total_packs_count_for_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_total_packs_count_for_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_total_packs_count_for_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def verify_pack_list_by_company_id(pack_list: list, company_id: int) -> bool:
    """
    verify pack list by company id
    :return: bool
    """
    try:
        verification_status = PackDetails.db_verify_packlist(packlist=pack_list, company_id=company_id)
        return verification_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in verify_pack_list_by_company_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in verify_pack_list_by_company_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def verify_pack_list_by_system_id(pack_list: list, system_id: int) -> bool:
    """
    verify pack list by system id
    :return: bool
    """
    try:
        verification_status = PackDetails.db_verify_packlist_by_system_id(packlist=pack_list, system_id=system_id)
        return verification_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in verify_pack_list_by_system_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in verify_pack_list_by_system_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_pack_details(update_dict: dict, pack_id: int) -> bool:
    """
    Update pack details table for given pack_id
    """
    try:
        update_status = PackDetails.db_update_pack_details(update_dict=update_dict, pack_id=pack_id)
        return update_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_pack_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pack_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_dict_pack_details(update_dict, pack_id, system_id) -> bool:
    """
    Update dict in pack details table for given pack_id
    """
    try:
        update_status = PackDetails.db_update_dict_pack_details(update_dict, pack_id, system_id)
        return update_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_uploading_time_pack_details {}".format(e))
        raise e


@log_args_and_response
def get_pack_id_list_by_status(status: list, batch_id: int, pack_id_list: Optional[list] = None) -> list:
    """
    get pack id list for given status
    """
    try:

        pack_list = PackDetails.db_get_pack_id_list_by_status(status=status, batch_id=batch_id, pack_id_list=pack_id_list)
        return pack_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_id_list_by_status {}".format(e))
        raise e


@log_args_and_response
def get_order_pack_id_list(pack_id_list: list, system_id: int) -> list:
    """
        This function will be used to get order pack ids
        :return: List of pack ids
        @param pack_id_list:
        @param system_id:
    """
    try:
        pack_list = PackDetails.db_get_order_pack_id_list(pack_id_list=pack_id_list, system_id=system_id)
        return pack_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_order_pack_id_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_order_pack_id_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pack_status_by_pack_list(pack_list: list) -> dict:
    """
    function to get pack status by pack list
    :return: dict
    """
    try:
        status_pack_count = db_get_pack_status_by_pack_list(pack_list)
        return status_pack_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_status_by_pack_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_status_by_pack_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_batch_id_null(pending_manual_packs: list, system_id: int) -> bool:
    """
    function to update batch_id null for pending manual pack
    :return: dict
    """
    try:
        update_status = PackDetails.db_update_batch_id_null(pending_manual_packs, system_id)
        return update_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_batch_id_null {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_batch_id_null: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pack_order_no(batch_id: int) -> List[Any]:
    """
        This function will be used to get order pack ids
        @param batch_id:
    """
    try:
        query = PackDetails.db_get_pack_order_no(batch_id=batch_id)
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_order_no {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_order_no: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pack_order_no_by_pack_list(pack_list) :
    """
        This function will be used to get order pack ids
        @param pack_list:
    """
    try:
        query = PackDetails.select(PackDetails.id, PackDetails.order_no).dicts() \
                .where(PackDetails.id << pack_list) \
                .order_by(PackDetails.order_no)
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_order_no {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_order_no: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pending_order_pack_by_batch(batch_id: int, priority: Optional[int] = None) -> List[Any]:
    """
        This function will be used to get pending order pack ids by batch
        :return: List
        @param priority:
        @param batch_id:
    """
    try:
        query = PackDetails.db_get_pending_order_pack_by_batch(batch_id=batch_id, priority=priority)
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_order_pack_id_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_order_pack_id_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def change_pack_sequence(pack_list: list, order_number_list: list = None, new_seq_tuple: list = None) -> bool:
    """
    Function to updated pack sequence
    @param pack_list: list
    @param order_number_list: list
    @return: status
    """
    try:
        if not new_seq_tuple:
            logger.info("In change_pack_sequence: pack list and order list {}, {}".format(pack_list, order_number_list))
            new_seq_tuple = list(tuple(zip(map(str, pack_list), map(str, order_number_list))))
        logger.info("In change_pack_sequence: new_case_tuple: {}".format(new_seq_tuple))
        case_sequence = case(PackDetails.id, new_seq_tuple)
        logger.info("In change_pack_sequence: case_sequence: {}".format(case_sequence))

        # update order number in table
        order_no_status = PackDetails.db_change_pack_sequence(case_sequence=case_sequence, pack_list=pack_list)
        logger.info("In change_pack_sequence: order_no is updated in pack details table: {}".format(order_no_status))
        return order_no_status

    except (InternalError, IntegrityError, DoesNotExist, ValueError) as e:
        logger.error("error in change_pack_sequence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in change_pack_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in change_pack_sequence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in change_pack_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_deleted_packs_by_batch(batch_id: int, company_id: int) -> list:
    """
    function to get deleted pack list by batch id and company_id
    :return: dict
    """
    try:
        pack_list = PackDetails.db_get_deleted_packs_by_batch(batch_id=batch_id,
                                                              company_id=company_id)
        return pack_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_deleted_packs_by_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in db_get_deleted_packs_by_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_batch_status_wise_pack_count(status: list, latest_batch_id: int):
    """
    get pack_status wise total pack count for batch
    :return: bool
    """

    try:
        query = PackDetails.db_get_batch_status_wise_pack_count(batch_id=latest_batch_id, status_list=status)
        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_batch_status_wise_pack_count {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_batch_status_wise_pack_count: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_batch_status_wise_pack_count {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_batch_status_wise_pack_count: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_system_status_wise_pack_count(status: list, system_id: int):
    """
    get pack_status wise total pack count for batch
    :return: bool
    """

    try:
        query = PackDetails.select(fn.COUNT(PackDetails.id).alias("id"), PackDetails.pack_status) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(
            PackDetails.pack_status << status, PackDetails.system_id == system_id) \
            .group_by(PackDetails.pack_status)
        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_system_status_wise_pack_count {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_system_status_wise_pack_count: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_system_status_wise_pack_count {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_system_status_wise_pack_count: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_filled_pack_count_by_date(company_id: int, from_date, to_date, offset):
    """
        get filled pack count by date
    """
    try:
        return PackDetails.db_get_filled_pack_count_by_date(company_id=company_id, from_date=from_date, to_date=to_date, offset=offset)
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_filled_pack_count_by_date:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_filled_pack_count_by_date {}".format(e))
        raise e


@log_args_and_response
def overload_pack_timing_update_or_create_record(data_dict: dict, update_dict: dict):
    """
    create or update record in overloaded pack timing table
    """
    try:

        response = OverLoadedPackTiming.db_update_or_create_record(create_dict=data_dict, update_dict=update_dict)
        return response

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in overload_pack_timing_update_or_create_record {}".format(e))
        raise e


@log_args_and_response
def get_extra_hours_dao(date_list: list, system_id: int):
    """
    get extra hours from overloaded pack timing table in given range of date
    """
    try:

        response = OverLoadedPackTiming.get_extra_hours(date_range=date_list, system_id=system_id)
        return response

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_extra_hours_dao {}".format(e))
        raise e



@log_args_and_response
def db_add_overloaded_pack_timing_data_dao(insert_dict: list):
    """
    adds overloaded pack timing data in overloaded pack table
    """
    try:

        status = OverLoadedPackTiming.db_add_overloaded_pack_timing_data(insert_dict=insert_dict)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_add_overloaded_pack_timing_data_dao {}".format(e))
        raise e


@log_args_and_response
def map_pack_location_dao(slot_row, slot_column):
    """
    Map the slot row and slot col from
    matrix index i,j to a pack location
    """
    try:

        query = PackGrid.select(PackGrid.slot_number).where(
            (PackGrid.slot_row == slot_row) & (PackGrid.slot_column == slot_column)).get()
        slot_number = query.slot_number
        return slot_number

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in map_pack_location_dao {}".format(e))
        raise e


@log_args_and_response
def get_pack_grid_id_dao(slot_row, slot_column):
    """
    get pack grid id from pack grid table
    """
    try:
        pack_grid_id = PackGrid.db_get_pack_grid_id(slot_row, slot_column)
        return pack_grid_id

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in map_pack_location_dao {}".format(e))
        raise e


@log_args_and_response
def verify_pack_id_by_system_id_dao(pack_id, system_id) -> bool:
    """
    verify pack id by system id
    """
    try:
        status = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in verify_pack_id_by_system_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_pack_grid_id_by_slot_number(slot_number):
    """
    get pack grid id by slot number from pack grid table
    """
    try:
        status = PackGrid.db_get_pack_grid_id_by_slot_number(slot_number=slot_number)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_grid_id_by_slot_number {}".format(e))
        raise e


@log_args_and_response
def update_unit_dosage_flag(slot_volume_threshold, pack_list):
    """
    Unit dosage = 1 ndc and qty depends on slot volume with threshold.
    """
    try:
        if pack_list:
            sub_q = PackDetails.select(PackDetails.id.alias('pack_id'),
                                       SlotHeader.id.alias('slot_header_id'),
                                       fn.SUM(SlotDetails.quantity),
                                       fn.IF(fn.SUM(SlotDetails.quantity) == 1, 1, fn.IF(fn.COUNT(
                                           fn.DISTINCT(
                                               fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr))) == 1,
                                                                                         fn.IF(fn.ROUND(
                                                                                             DrugDimension.width * DrugDimension.depth * DrugDimension.length).is_null(
                                                                                             False), fn.IF(
                                                                                             fn.ROUND(
                                                                                                 DrugDimension.width * DrugDimension.depth * DrugDimension.length) * fn.SUM(
                                                                                                 SlotDetails.quantity) <= settings.UNIT_DOSAGE_SLOT_VOLUME * slot_volume_threshold,
                                                                                             1, 0), fn.IF(
                                                                                             settings.DEFAULT_PILL_VOLUME * fn.SUM(
                                                                                                 SlotDetails.quantity) <= settings.UNIT_DOSAGE_SLOT_VOLUME,
                                                                                             1, 0)), 0)).alias(
                                           'unit_dosage_slot')) \
                .join(SlotHeader, on=SlotHeader.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(UniqueDrug,
                      on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (
                              UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .where(PackDetails.id << pack_list) \
                .group_by(SlotHeader.id) \
                .order_by(PackDetails.id).alias('sub_q')

            query = PackDetails.select(sub_q.c.pack_id,
                                       fn.IF(fn.COUNT(sub_q.c.slot_header_id) == fn.SUM(sub_q.c.unit_dosage_slot),
                                             settings.DOSAGE_TYPE_UNIT, settings.DOSAGE_TYPE_MULTI).alias(
                                           'dosage_type')) \
                .join(sub_q, on=sub_q.c.pack_id == PackDetails.id) \
                .group_by(sub_q.c.pack_id)

            pack_ids = []
            seq_tuples = []
            for record in query.dicts():
                logger.info(f"In update_unit_dosage_flag, record: {record}")
                pack_ids.append(str(record['pack_id']))
                if settings.USE_UNIT_DOSAGE:
                    logger.info(f"In update_unit_dosage_flag, USE_UNIT_DOSAGE: {settings.USE_UNIT_DOSAGE}")
                    seq_tuples.append((str(record['pack_id']), record['dosage_type']))
                else:
                    logger.info(f"In update_unit_dosage_flag, else, USE_UNIT_DOSAGE: {settings.USE_UNIT_DOSAGE}")
                    seq_tuples.append((str(record['pack_id']), settings.DOSAGE_TYPE_MULTI))

            logger.info(f"In update_unit_dosage_flag, seq_tuples: {seq_tuples}")
            case_sequence = case(PackDetails.id, seq_tuples)

            status = PackDetails.update(dosage_type=case_sequence).where(PackDetails.id << pack_ids).execute()
            return status

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return e


@log_args_and_response
def update_unit_pack_for_multi_dosage_flag(slot_volume_threshold, pack_list):
    """
    slot qty based on slot volume with threshold.
    """
    try:
        if pack_list:
            sub_q = PackDetails.select(PackDetails.id.alias('pack_id'),
                                       SlotHeader.id.alias('slot_header_id'),
                                       fn.SUM(SlotDetails.quantity).alias("quantity"),
                                       fn.IF(
                                           fn.ROUND(
                                               DrugDimension.width * DrugDimension.depth * DrugDimension.length).is_null(
                                               False),
                                           fn.IF(fn.ROUND(
                                               DrugDimension.width * DrugDimension.depth * DrugDimension.length) * fn.SUM(
                                               SlotDetails.quantity) <= settings.UNIT_DOSAGE_SLOT_VOLUME * slot_volume_threshold,
                                                 fn.IF(fn.SUM(SlotDetails.quantity) <= settings.MAX_SLOT_COUNT_UNIT_PACK, 1, 0), 0),
                                           fn.IF(settings.DEFAULT_PILL_VOLUME * fn.SUM(
                                               SlotDetails.quantity) <= settings.UNIT_DOSAGE_SLOT_VOLUME,
                                                 fn.IF(fn.SUM(SlotDetails.quantity) <= settings.MAX_SLOT_COUNT_UNIT_PACK, 1, 0), 0),
                                       )\
                                       .alias('unit_dosage_slot')) \
                .join(SlotHeader, on=SlotHeader.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(UniqueDrug,
                      on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (
                              UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .where(PackDetails.id << pack_list, PackDetails.dosage_type != settings.DOSAGE_TYPE_UNIT) \
                .group_by(SlotHeader.id) \
                .order_by(PackDetails.id).alias('sub_q')

            query = PackDetails.select(sub_q.c.pack_id,
                                       fn.IF(fn.COUNT(sub_q.c.slot_header_id) == fn.SUM(sub_q.c.unit_dosage_slot),
                                             settings.DOSAGE_TYPE_UNIT, settings.DOSAGE_TYPE_MULTI).alias(
                                           'dosage_type')) \
                .join(sub_q, on=sub_q.c.pack_id == PackDetails.id) \
                .group_by(sub_q.c.pack_id)

            pack_ids = []
            seq_tuples = []
            for record in query.dicts():
                logger.info(f"In update_unit_dosage_flag, record: {record}")
                pack_ids.append(str(record['pack_id']))
                if record["dosage_type"] == settings.DOSAGE_TYPE_UNIT:
                    logger.info(f"In update_unit_pack_for_multi_dosage_flag setting True")
                    seq_tuples.append((str(record['pack_id']), constants.WEEKLY_UNITDOSE_PACK))
                else:
                    logger.info(f"In update_unit_pack_for_multi_dosage_flag setting False")
                    seq_tuples.append((str(record['pack_id']), constants.WEEKLY_MULTIDOSE_PACK))

            if seq_tuples:
                logger.info(f"In update_unit_dosage_flag, seq_tuples: {seq_tuples}")
                case_sequence = case(PackDetails.id, seq_tuples)

                status = PackDetails.update(pack_type=case_sequence).where(PackDetails.id << pack_ids).execute()
                logger.info(f"In update_unit_dosage_flag, status : {status}")
                return status
            else:
                return None

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return e


@log_args_and_response
def get_drug_wise_pack_count(time_period, company_id):
    """
    Function to get drug wise count of packs (packs in which that drug is used)
        for given time period
    @param time_period: To get start date (n(time_period) months back) from current date
    @param company_id:
    @return: drug_canister_pack_count_dict: {fndc_txr: (pack_count, [canister_list]}
    """
    logger.debug("In get_drug_wise_pack_count")
    try:
        current_date = datetime.datetime.now().date()
        days_before = int(time_period) * settings.days_in_month
        month_back_date = current_date - datetime.timedelta(days=days_before)
        drug_canister_pack_count_dict = dict()
        start_date = datetime.date.today() + relativedelta(months=+time_period)

        DrugMasterAlias = DrugMaster.alias()
        CanisterMasterAlias = CanisterMaster.alias()

        sub_query = CanisterMaster.select(DrugMasterAlias.concated_fndc_txr_field()) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == CanisterMaster.drug_id) \
            .join(CanisterZoneMapping, on=((CanisterZoneMapping.canister_id == CanisterMaster.id) &
                                           (CanisterMaster.active == settings.is_canister_active) &
                                           (CanisterZoneMapping.zone_id << settings.canister_zone_id))) \
            .where(CanisterMaster.company_id == company_id) \
            .group_by(DrugMasterAlias.concated_fndc_txr_field())

        query = PackDetails.select(DrugMaster.concated_fndc_txr_field().alias('drug_id'),
                                   fn.COUNT(fn.DISTINCT(PackDetails.id)).alias('pack_count'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(CanisterMasterAlias.id)).coerce(False).alias(
                                       'canister_list')) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .join(CanisterMasterAlias, on=CanisterMasterAlias.drug_id == DrugMaster.id) \
            .where(PackDetails.filled_date >= str(month_back_date),
                   DrugMaster.concated_fndc_txr_field() << sub_query,
                   CanisterMasterAlias.company_id == company_id) \
            .group_by(DrugMaster.concated_fndc_txr_field()) \
            .order_by(fn.COUNT(fn.DISTINCT(PackDetails.id)).desc())

        for record in query.dicts():
            drug_canister_pack_count_dict[record['drug_id']] = (record['pack_count'],
                                                                list(record['canister_list'].split(",")))

        return drug_canister_pack_count_dict

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def db_get_packs(start_date, end_date, _pack_status, filter_fields=None, company_id=None, system_id=None,
                 all_flag=False):
    pending_packs = []
    pack_list = []
    unique_batch_ids = set()
    schedule_facility_ids = set()
    schedule_ids = set()
    patient_schedule_ids = set()
    pack_cycle_dict = {}
    facility_min_delivery_date = dict()
    location = cycle(settings.PACK_PLATE_LOCATION)
    clauses = list()
    clauses.append((PackDetails.created_date.between(start_date, end_date)))
    clauses.append((PackDetails.pack_status << _pack_status))
    # clauses.append((BatchManualPacks.id.is_null(True)))
    clauses.append((
            BatchMaster.id.is_null(True)
            | BatchMaster.status.not_in([settings.BATCH_IMPORTED])
    ))
    if company_id:
        clauses.append((PackDetails.company_id == company_id))
        clauses.append(PackDetails.batch_id.is_null(True))
        if not system_id:
            clauses.append((PackDetails.system_id.is_null(True)))
    if system_id and not all_flag:
        clauses.append((PackDetails.system_id == system_id))

    non_exact_search_list = ['facility_name']
    fields_dict = {
        "facility_name": FacilityMaster.facility_name,
    }
    clauses = get_filters(clauses, fields_dict, filter_fields,
                          like_search_fields=non_exact_search_list,
                          )
    logger.debug("Inside db_get_packs")
    try:
        query = PackDetails.select(
            PackDetails.filled_days,
            PackDetails.fill_start_date,
            PackDetails.id,
            PackDetails.pack_display_id,
            PackDetails.pack_no,
            FileHeader.created_date,
            FileHeader.created_time,
            PackDetails.pack_status,
            PackDetails.system_id,
            PackDetails.facility_dis_id.alias('facility_distribution_id'),
            PackDetails.consumption_start_date,
            PackDetails.consumption_end_date,
            PackHeader.patient_id,
            PackHeader.delivery_datetime,
            PackHeader.scheduled_delivery_date,
            PatientMaster.last_name,
            PatientMaster.first_name,
            PatientMaster.patient_no,
            FacilityMaster.facility_name,
            PatientMaster.facility_id,
            PackDetails.order_no,
            PackDetails.pack_plate_location,
            CodeMaster.value,
            CodeMaster.id.alias('pack_status_id'),
            PackDetails.batch_id,
            BatchMaster.status.alias('batch_status'),
            BatchMaster.name.alias('batch_name'),
            PatientSchedule.schedule_id,
            PatientSchedule.id.alias("patient_schedule_id")
        ).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(FileHeader, on=FileHeader.id == PackHeader.file_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
            .join(PatientSchedule, JOIN_LEFT_OUTER,
                  on=((PatientSchedule.patient_id == PatientMaster.id)
                      & (PatientSchedule.facility_id == PatientMaster.facility_id))) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(FileHeader.created_date, PatientMaster.facility_id,
                      PackHeader.patient_id, PackDetails.id)

        logger.info("In db_get_packs, query: {}".format(query))

        for record in query:

            logger.info("In pack_cycle_dict, record: {}".format(record))

            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["created_date"] = datetime.datetime.combine(record["created_date"], record["created_time"])
            # record['slotDetails'] = '/slots?pack_id=' + str(record["id"]) + '&system_id=' + str(record["system_id"])
            record["pack_status"] = record["value"]
            record["patient_name"] = record["patient_name"].strip()
            record["facility_name"] = record["facility_name"].strip()
            record["consumption_start_date"] = convert_date_from_sql_to_display_date(
                record["consumption_start_date"])
            record["consumption_end_date"] = convert_date_from_sql_to_display_date(record["consumption_end_date"])
            record["admin_period"] = record["consumption_start_date"] + "  to  " + record["consumption_end_date"]
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            record['scheduled_delivery_date'] = str(record['scheduled_delivery_date']) if record[
                'scheduled_delivery_date'] else None

            pack_list.append(record['id'])

            if not record["pack_plate_location"]:
                pack_plate_location = next(location)
                record["pack_plate_location"] = pack_plate_location
                pack_cycle_dict[str(record["id"])] = pack_plate_location

            pending_packs.append(record)
            unique_batch_ids.add(record['batch_id'])
            schedule_facility_ids.add('{}:{}'.format(record['schedule_id'],
                                                     record['facility_id']))

            if record['schedule_id']:
                schedule_ids.add(record['schedule_id'])

            if record['patient_schedule_id']:
                patient_schedule_ids.add(record['patient_schedule_id'])

            if record['batch_status'] not in [settings.BATCH_PROCESSING_COMPLETE, settings.BATCH_IMPORTED] \
                    and record['pack_status_id'] == settings.PENDING_PACK_STATUS:

                if record['facility_id'] in facility_min_delivery_date and \
                        facility_min_delivery_date[record['facility_id']]:

                    if record['scheduled_delivery_date']:

                        if record['scheduled_delivery_date'] <= facility_min_delivery_date[record['facility_id']]:
                            facility_min_delivery_date[record['facility_id']] = record['scheduled_delivery_date']

                    else:
                        facility_min_delivery_date[record['facility_id']] = record['scheduled_delivery_date']

                else:
                    facility_min_delivery_date[record['facility_id']] = record['scheduled_delivery_date']

        logger.info("In db_get_packs, pack_cycle_dict: {}".format(pack_cycle_dict))

        if pack_cycle_dict:
            t = threading.Thread(target=PackDetails.update_pack_plate_location, kwargs=(pack_cycle_dict))
            t.start()

        return {
            'packs': pending_packs,
            'batches': unique_batch_ids,
            'schedule_ids': schedule_ids,
            'schedule_facility_ids': schedule_facility_ids,
            'facility_min_delivery_date': facility_min_delivery_date,
            'patient_schedule_ids': patient_schedule_ids
        }

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_packs {}".format(e))
        raise


@log_args_and_response
def db_get_packs_by_facility_id(start_date, end_date, _pack_status, facility_id, filter_fields=None,
                                company_id=None, system_id=None, all_flag=False):
    """

    @param start_date:
    @param end_date:
    @param _pack_status:
    @param facility_id:
    @param filter_fields:
    @param company_id:
    @param system_id:
    @param all_flag:
    @return:
    """
    logger.debug("Inside db_get_packs_by_facility_id")
    pack_list = []
    header_pack_list = {}
    pack_cycle_dict = {}
    location = cycle(settings.PACK_PLATE_LOCATION)
    clauses = list()
    having_clauses = list()
    clauses.append((PackDetails.created_date.between(start_date, end_date)))
    clauses.append((PackDetails.pack_status << _pack_status))
    clauses.append((FacilityMaster.id == facility_id))
    clauses.append((PackDetails.batch_id.is_null(True)))
    if company_id:
        clauses.append((PackDetails.company_id == company_id))
        if not system_id:
            clauses.append((PackDetails.system_id.is_null(True)))
    if system_id and not all_flag:
        clauses.append((PackDetails.system_id == system_id))

    if filter_fields and filter_fields.get('multi_search', None) is not None:
        string_search_fields = [
            FacilityMaster.facility_name,
            PatientMaster.id,
            PatientMaster.concated_patient_name_field(),
            PackDetails.pack_display_id,
            PackDetails.id,
        ]

        multi_search_fields = filter_fields.get('multi_search').split(',')
        for index, search_field in enumerate(multi_search_fields):
            if not search_field.isdigit() and is_date(search_field):
                delivery_date = convert_dob_date_to_sql_date(search_field)
                if delivery_date is not None:
                    multi_search_fields.pop(index)
        if multi_search_fields:
            clauses = get_multi_search(clauses, multi_search_fields, string_search_fields)

    try:
        query = PackDetails.select(PackDetails.id.alias('pack_id'),
                                   PackDetails.pack_display_id,
                                   PackDetails.pack_no,
                                   PackDetails.pack_status,
                                   PackDetails.system_id,
                                   PackDetails.facility_dis_id.alias('facility_distribution_id'),
                                   PackDetails.consumption_start_date,
                                   PackDetails.consumption_end_date,
                                   PackDetails.pack_header_id,
                                   PackDetails.pack_plate_location,
                                   PackHeader.scheduled_delivery_date,
                                   PackHeader.patient_id,
                                   PackUserMap.assigned_to,
                                   PatientMaster.last_name,
                                   PatientMaster.first_name,
                                   PatientMaster.patient_no,
                                   PatientMaster.dob,
                                   FacilityMaster.id.alias('facility_id'),
                                   FacilityMaster.facility_name,
                                   PackDetails.batch_id,
                                   BatchMaster.status.alias('batch_status'),
                                   BatchMaster.name.alias('batch_name'),
                                   ).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
            .join(BatchManualPacks, JOIN_LEFT_OUTER, on=PackDetails.id == BatchManualPacks.pack_id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackDetails.id == PackUserMap.pack_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(PackDetails.pack_display_id)

        logger.debug("In db_get_packs_by_facility_id, pack query: " + str(query))
        all_manual_header = {}
        for record in query:
            if not all_manual_header.get(record['pack_header_id']):
                all_manual_header[record['pack_header_id']] = [record['pack_status']]
            else:
                all_manual_header[record['pack_header_id']].append(record['pack_status'])

            record["patient_name"] = str(record["last_name"] + ", " + record["first_name"]).strip()

            if not record["pack_plate_location"]:

                pack_plate_location = next(location)
                record["pack_plate_location"] = pack_plate_location
                pack_cycle_dict[str(record["pack_id"])] = pack_plate_location

            # pack_list.append(record)
            if not header_pack_list.get(record['pack_header_id']):
                header_pack_list[record['pack_header_id']] =[record]
            else:
                header_pack_list[record['pack_header_id']].append(record)
        for header, status_set in all_manual_header.items():
            if settings.PENDING_PACK_STATUS not in status_set:
                del header_pack_list[header]
        for k,v in header_pack_list.items():
            pack_list.extend(v)
        # pack_list = sum(header_pack_list.values(), [])
        logger.info("In db_get_packs_by_facility_id, pack_list fetched; pack_list: {}".format(
            pack_list))

        logger.info("In db_get_packs_by_facility_id, pack_cycle_dict: {}".format(pack_cycle_dict))
        if pack_cycle_dict:
            logger.debug("In db_get_packs_by_facility_id, updating pack plate location")
            t = threading.Thread(target=PackDetails.update_pack_plate_location, kwargs=(pack_cycle_dict))
            t.start()

        logger.debug("In db_get_packs_by_facility_id, pack plate location updated")

        result = {'pack_list': pack_list}
        return result

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_packs_by_facility_id {}".format(e))
        raise


@log_args_and_response
def db_get_facility_data_v3(start_date, end_date, _pack_status, filter_fields=None, company_id=None,
                            system_ids=None, all_flag=False, active=True):
        logger.debug("In db_get_facility_data")
        facility_ids = list()
        facility_data_dict = dict()
        having_clauses = list()
        clauses = list()
        clauses.append((PackDetails.created_date.between(start_date, end_date)))
        clauses.append((PackDetails.pack_status << _pack_status))
        clauses.append((PackDetails.batch_id.is_null(True)))
        if company_id:
            clauses.append((PackDetails.company_id == company_id))
            if not system_ids:
                clauses.append((PackDetails.system_id.is_null(True)))
        if system_ids and not all_flag:
            clauses.append((PackDetails.system_id == system_ids))
        if active:
            clauses.append((PatientSchedule.active == 1))

        PatientMasterAlias = PatientMaster.alias()
        non_exact_search_list = ['facility_name']
        membership_search_list = ['facility_ids']
        fields_dict = {
            "facility_name": FacilityMaster.facility_name,
            "facility_ids": FacilityMaster.id,
        }
        clauses = get_filters(clauses, fields_dict, filter_fields,
                              like_search_fields=non_exact_search_list,
                              membership_search_fields=membership_search_list)

        if filter_fields and filter_fields.get('multi_search', None) is not None:
            string_search_fields = [
                FacilityMaster.facility_name,
                PatientMaster.id,
                PatientMaster.concated_patient_name_field(),
                PackDetails.pack_display_id,
                PackDetails.id,
            ]

            multi_search_fields = filter_fields.get('multi_search').split(',')
            for index, search_field in enumerate(multi_search_fields):
                if not search_field.isdigit() and is_date(search_field):
                    delivery_date = convert_dob_date_to_sql_date(search_field)
                    if delivery_date is not None:
                        having_clauses.append(fn.MIN(PackHeader.scheduled_delivery_date) == delivery_date)
                        multi_search_fields.pop(index)
            if multi_search_fields:
                clauses = get_multi_search(clauses, multi_search_fields, string_search_fields)

        logger.debug("db_get_facility_data: filters added")
        try:
            exclude_header = []
            header_query = PackDetails.select(fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_status)).coerce(False)
                                            .alias("all_pack_status"), PackHeader.id
            ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientSchedule.patient_id == PatientMaster.id) & (
                    PatientSchedule.facility_id == PatientMaster.facility_id))) \
                .join(FacilitySchedule, JOIN_LEFT_OUTER, on=FacilitySchedule.id == PatientSchedule.schedule_id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(PackHeader.id)
            for record in header_query:
                if str(settings.PENDING_PACK_STATUS) not in record['all_pack_status']:
                    exclude_header.append(record['id'])
            if exclude_header:
                clauses.append((PackHeader.id.not_in(exclude_header)))
            query = PackDetails.select(
                PatientSchedule.schedule_id,
                FacilityMaster.id.alias('facility_id'),
                FacilityMaster.facility_name,
                fn.MAX(FileHeader.created_date).alias('file_upload_date'),
                PackDetails.facility_dis_id.alias('facility_distribution_id'),
                fn.MIN(PackDetails.consumption_start_date).coerce(False).alias('admin_start_date'),
                FacilitySchedule.fill_cycle.alias('fill_cycle'),
                FacilitySchedule.days,
                FacilitySchedule.start_date,
                PatientSchedule.delivery_date_offset,
                fn.GROUP_CONCAT(fn.DISTINCT(PackHeader.id)).coerce(False)
                .alias("pack_header"),
                fn.MAX(PatientSchedule.last_import_date).alias('last_import_date'),
                fn.MIN(PackHeader.scheduled_delivery_date).coerce(False).alias('delivery_date'),

            ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(FileHeader, on=FileHeader.id == PackHeader.file_id) \
                .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientSchedule.patient_id == PatientMaster.id) & (
                    PatientSchedule.facility_id == PatientMaster.facility_id))) \
                .join(FacilitySchedule, JOIN_LEFT_OUTER, on=FacilitySchedule.id == PatientSchedule.schedule_id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(FacilityMaster.id)
            if having_clauses:
                query = query.having(functools.reduce(operator.and_, having_clauses))
            query = query.order_by(FacilityMaster.facility_name)
            logger.debug("db_get_facility_data: facility_query: " + str(query))

            for record in query:
                facility_ids.append(record["facility_id"])
                record["pack_ids"] = set()
                record['bubble_pack_ids'] = set()
                record["pack_display_ids"] = set()
                record["pack_status_ids"] = set()
                record["scheduled_patient_ids"] = set()
                record["current_patient_ids"] = set()
                record["delivery_date_null_set"] = set()
                record["total_patient_ids"] = set()
                record["admin_start_date"] = datetime.datetime.combine(record["admin_start_date"], datetime.datetime.min.time())
                facility_data_dict[record["facility_id"]] = record

            logger.debug("db_get_facility_data: fetching pack level data based on facility_ids")
            if len(facility_ids):
                clauses.append((FacilityMaster.id << facility_ids))
                pack_query = PackDetails.select(
                    FacilityMaster.id.alias('facility_id'),
                    PackDetails.id.alias('pack_id'),
                    PackDetails.pack_display_id.alias('pack_display_id'),
                    PackDetails.pack_status.alias('pack_status_id'),
                    PackDetails.consumption_start_date,
                    PatientSchedule.id.alias('scheduled_patient_id'),
                    PatientMaster.id.alias('current_patient_id'),
                    fn.IF(PackHeader.scheduled_delivery_date.is_null(True), True, False).alias('delivery_date_null'),
                    PackHeader.id.alias('pack_header_id'),
                    PackHeader.scheduled_delivery_date,
                    TemplateMaster.is_bubble,
                ).dicts() \
                    .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                    .join(TemplateMaster, on=((TemplateMaster.patient_id == PackHeader.patient_id) & (
                            TemplateMaster.file_id == PackHeader.file_id))) \
                    .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                    .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                    .join(FileHeader, on=FileHeader.id == PackHeader.file_id) \
                    .join(PatientSchedule, on=((PatientSchedule.patient_id == PatientMaster.id) & (
                        PatientSchedule.facility_id == PatientMaster.facility_id))) \
                    .join(FacilitySchedule, JOIN_LEFT_OUTER, on=FacilitySchedule.id == PatientSchedule.schedule_id) \
                    .where(functools.reduce(operator.and_, clauses))

                logger.debug("db_get_facility_data: packs_query: " + str(pack_query))

                for pack in pack_query:
                    facility_data_dict[pack["facility_id"]]["pack_ids"].add(pack["pack_id"])
                    facility_data_dict[pack["facility_id"]]["pack_display_ids"].add(pack["pack_display_id"])
                    facility_data_dict[pack["facility_id"]]["pack_status_ids"].add(pack["pack_status_id"])
                    facility_data_dict[pack["facility_id"]]["scheduled_patient_ids"].add(pack["scheduled_patient_id"])
                    facility_data_dict[pack["facility_id"]]["current_patient_ids"].add(int(pack["current_patient_id"]))
                    facility_data_dict[pack["facility_id"]]["delivery_date_null_set"].add(pack["delivery_date_null"])
                    if pack["is_bubble"]:
                        facility_data_dict[pack["facility_id"]]["bubble_pack_ids"].add(pack["pack_id"])

                # fetching patient data, added new query to fetch all active patients of the facility
                logger.debug("db_get_facility_data: fetching patient data")
                patient_query = PatientMaster.select(fn.DISTINCT(PatientMaster.id),
                                                     PatientMaster.facility_id).dicts() \
                    .join(PatientSchedule, on=(PatientSchedule.patient_id == PatientMaster.id) & (
                        PatientSchedule.facility_id == PatientMaster.facility_id)) \
                    .where(PatientMaster.facility_id << facility_ids, PatientSchedule.active == True)
                logger.debug("db_get_facility_data: patient_query: " + str(patient_query))

                for patient in patient_query:
                    facility_data_dict[patient["facility_id"]]["total_patient_ids"].add(patient["id"])
                logger.debug("db_get_facility_data: total_patient_ids added")

            logger.debug("db_get_facility_data: Adding facility level data")
            for facility_id, facility_record in facility_data_dict.items():
                facility_record["pending_patient_ids"] = facility_record["total_patient_ids"] \
                    .difference(facility_record["current_patient_ids"])
                facility_record["total_patient_count"] = len(facility_record["total_patient_ids"])
                facility_record["current_patient_count"] = len(facility_record["current_patient_ids"])
                facility_record["pending_patient_count"] = len(facility_record["pending_patient_ids"])

                facility_record['schedule_facility_id'] = '{}:{}'.format(facility_record['schedule_id'],
                                                                         facility_record['facility_id'])
                facility_record["total_packs_count"] = len(facility_record["pack_ids"])

                # check if any scheduled delivery date is null then set delivery date as null
                if any(facility_record["delivery_date_null_set"]):
                    facility_record["delivery_date"] = None

                if facility_record["delivery_date"] is not None and facility_record["delivery_date_offset"] is not None:
                    facility_record["schedule_date"] = (
                            facility_record['delivery_date'] - datetime.timedelta(
                        days=facility_record['delivery_date_offset'])).date()
                else:
                    facility_record["schedule_date"] = None

                facility_record["delivery_date"] = str(facility_record["delivery_date"]) \
                    if facility_record["delivery_date"] else None
                facility_record["schedule_date"] = str(facility_record["schedule_date"]) \
                    if facility_record["schedule_date"] else None

            logger.debug("db_get_facility_data: Facility data retrieved")

            return list(facility_data_dict.values()), facility_ids
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise


@log_args_and_response
def db_get_half_pill_drug_drop_by_pack_id(pack_list):
    try:
        query = PackDetails.select(
            PackDetails.id,
            DrugMaster.formatted_ndc,
            DrugMaster.txr,
            fn.Count(PackDetails.id).alias("drug_drops")
        ).join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id)\
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id)\
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)\
            .where(PackDetails.id << pack_list, SlotDetails.quantity << [0.5, 1.5, 2.5, 3.5]).group_by(PackDetails.id)

        pack_half_pill_drop_count = {}
        for record in query.dicts():
            pack_half_pill_drop_count[record["id"]] = record["drug_drops"]
        return pack_half_pill_drop_count
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


@log_args_and_response
def db_get_pack_details_batch_scheduling(pack_id, delivery_date, system_id=None,
                                         non_fractional=False):
    """
    Fetches pack data and slot data for robot(optionally).

    :param pack_id:
    :param system_id:
    :param non_fractional:
    :return:
    """
    pack_details_data = None
    try:

        for record in PackDetails.select(
                PackDetails.id,
                PackDetails.pack_display_id,
                PackDetails.pack_no,
                PackDetails.created_date,
                PackDetails.pack_status,
                PackDetails.rfid,
                PackHeader.patient_id,
                PackHeader.delivery_datetime,
                PatientMaster.last_name,
                PatientMaster.first_name,
                PatientMaster.dob,
                PatientMaster.allergy,
                PatientMaster.patient_no,
                FacilityMaster.facility_name,
                PatientMaster.facility_id,
                PackDetails.order_no,
                PackDetails.pack_plate_location,
                CodeMaster.value,
                CodeMaster.id.alias('pack_status_id'),
                # PackVerification.pack_fill_status,
                PackDetails.consumption_start_date,
                PackDetails.consumption_end_date
        ).order_by(
            PackDetails.created_date
        ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .where(PackDetails.id == pack_id):
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])
            record["consumption_start_date"] = convert_date_from_sql_to_display_date(
                record["consumption_start_date"])
            record["consumption_end_date"] = convert_date_from_sql_to_display_date(record["consumption_end_date"])
            record["admin_period"] = record["consumption_start_date"] + "  to  " + record["consumption_end_date"]
            record["delivery_date"] = delivery_date
            # record["schedule_date"] = schedule_date
            record["pack_status"] = record["value"]
            record["patient_name"] = record["patient_name"]
            record["facility_name"] = record["facility_name"]
            record["pack_id"] = record["id"]
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            pack_details_data = record

        return pack_details_data

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.error("Error in db_get_pack_details_batch_scheduling {}".format(e))
        raise


@log_args_and_response
def db_get_packs_by_batch(batch_ids, filter_fields, sort_fields, paginate):
    """
    Fetches pack data and slot data for robot(optionally).
    @param batch_ids:
    @param filter_fields:
    @param sort_fields:
    @param paginate:
    @return:
    """
    clauses = list()
    if filter_fields is not None:

        if filter_fields.get('multi_search', None) is not None:
            multi_search_fields = filter_fields.get('multi_search').split(',')
            string_search_fields = [
                FacilityMaster.facility_name,
                PatientMaster.concated_patient_name_field(),
                PackDetails.pack_display_id
            ]
            clauses = get_multi_search(clauses, multi_search_fields, string_search_fields)

    try:
        query = PackDetails.select(PackDetails.id.alias("pack_id")).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where((PackDetails.batch_id << batch_ids) & (PackDetails.pack_status == settings.PENDING_PACK_STATUS))
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        if paginate:
            query = apply_paginate(query, paginate)
        pack_ids = [data['pack_id'] for data in query]
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError

    pack_details_dict = {}

    try:
        if pack_ids:
            query = PackDetails.select(PackDetails.id,
                                       PackDetails.pack_display_id,
                                       PackDetails.pack_no,
                                       PackDetails.created_date,
                                       PackDetails.pack_status,
                                       PackDetails.rfid,
                                       PackHeader.patient_id,
                                       PackHeader.delivery_datetime.alias('ips_delivery_date'),
                                       PackHeader.scheduled_delivery_date,
                                       PatientMaster.last_name,
                                       PatientMaster.first_name,
                                       PatientMaster.dob,
                                       PatientMaster.allergy,
                                       PatientMaster.patient_no,
                                       FacilityMaster.facility_name,
                                       PatientMaster.facility_id,
                                       PackDetails.order_no,
                                       PackDetails.pack_plate_location,
                                       CodeMaster.value,
                                       CodeMaster.id.alias('pack_status_id'),
                                       # PackVerification.pack_fill_status,
                                       PackDetails.consumption_start_date,
                                       PackDetails.consumption_end_date,
                                       BatchMaster.status,
                                       BatchMaster.id.alias('batch_id'),
                                       BatchMaster.name,
                                       BatchMaster.scheduled_start_time,
                                       BatchMaster.estimated_processing_time) \
                .order_by(BatchMaster.id, PackDetails.created_date).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
                .where(PackDetails.id << pack_ids)

            for record in query:
                record["patient_name"] = record["last_name"] + ", " + record["first_name"]
                record["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])
                record["consumption_start_date"] = convert_date_from_sql_to_display_date(
                    record["consumption_start_date"])
                record["consumption_end_date"] = convert_date_from_sql_to_display_date(
                    record["consumption_end_date"])
                record["admin_period"] = record["consumption_start_date"] + "  to  " + record[
                    "consumption_end_date"]
                record["delivery_date"] = record["scheduled_delivery_date"]
                record["pack_status"] = record["value"]
                record["patient_name"] = record["patient_name"]
                record["facility_name"] = record["facility_name"]
                record["pack_id"] = record["id"]
                record["status"] = record["status"]
                record["delivery_date"] = convert_date_from_sql_to_display_date(record["scheduled_delivery_date"])
                # record['delivery_date'] = str(record['scheduled_delivery_date']).split(' ')[0]

                if record['name'] not in pack_details_dict.keys():
                    pack_details_dict[record['name']] = list()
                pack_details_dict[record['name']].append(record)

        return pack_details_dict

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.error("Error in db_get_packs_by_batch {}".format(e))
        raise


@log_args_and_response
def get_manual_packs_data(company_id, date_from, date_to, date_type, assigned_to, user_stats,
                          pack_status_list):
    clauses = list()
    try:
        clauses.append((PackDetails.company_id == company_id))
        if date_type == "admin_start_date":
            clauses.append((PackDetails.consumption_start_date.between(date_from, date_to)))
        elif date_type == "delivery_date":
            clauses.append((PackHeader.scheduled_delivery_date.between(date_from, date_to)))
        elif date_type == "created_date":
            clauses.append((PackDetails.created_date.between(date_from, date_to)))

        if user_stats:
            clauses.append((PackUserMap.assigned_to == assigned_to))

        if pack_status_list:
            clauses.append(PackDetails.pack_status << pack_status_list)

        status_pack_count_dict = {}
        value_status_id_dict = {}
        assigned_user_pack_count = {'user_total_packs': 0, 'user_done_packs': 0}
        total_packs = 0
        query = PackDetails.select(PackDetails.id,
                                   # PackDetails.pack_status,
                                   fn.IF((PackHeader.change_rx_flag.is_null(True) |
                                          (PackHeader.change_rx_flag == False) | PackDetails.pack_status << [
                                              settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS]),
                                         PackDetails.pack_status, settings.PACK_STATUS_CHANGE_RX).alias("pack_status"),
                                   PackHeader.scheduled_delivery_date,
                                   PackUserMap.assigned_to,
                                   # CodeMaster.value,

                                   fn.IF((PackHeader.change_rx_flag.is_null(True) |
                                          (PackHeader.change_rx_flag == False) | (
                                                  PackDetails.pack_status << [settings.DONE_PACK_STATUS,
                                                                              settings.DELETED_PACK_STATUS])),
                                         CodeMaster.value, constants.EXT_CHANGE_RX_PACKS_DESC).alias("value"),
                                   PackHeader.change_rx_flag).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .where(functools.reduce(operator.and_, clauses))

        logger.info(f"In get_manual_packs_data, query: {list(query)}")

        for record in query:
            if record['value'] not in status_pack_count_dict:
                status_pack_count_dict[record['value']] = 0
                value_status_id_dict[record['value']] = record['pack_status']

            if record['assigned_to'] is None:
                if 'Not assigned' not in status_pack_count_dict:
                    status_pack_count_dict['Not assigned'] = 0
                    # We statically giving status id 0 for Not assigned packs.
                    value_status_id_dict['Not assigned'] = 0
                status_pack_count_dict['Not assigned'] += 1

            if record['assigned_to'] == assigned_to:
                assigned_user_pack_count['user_total_packs'] += 1
                if record['pack_status'] in [settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS]:
                    assigned_user_pack_count['user_done_packs'] += 1

            status_pack_count_dict[record['value']] += 1
            total_packs += 1
        # status_pack_count_dict['total_packs'] = total_packs
        return status_pack_count_dict, value_status_id_dict, total_packs, assigned_user_pack_count
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in get_manual_packs_data {}".format(e))
        raise


@log_args_and_response
def get_patient_manual_packs(patient_id, company_id, date_from, date_to, date_type, user_id, assigned_user_id, pack_header_id, pack_master):
    logger.debug("Inside get_patient_manual_packs")
    try:
        clauses = []
        status_set = set()
        if date_type == "admin_start_date":
            clauses.append((PackDetails.consumption_start_date.between(date_from, date_to)))
        elif date_type == "delivery_date":
            clauses.append((PackHeader.scheduled_delivery_date.between(date_from, date_to)))
        elif date_type == "created_date":
            clauses.append((PackDetails.created_date.between(date_from, date_to)))
        # clauses.append()

        if pack_header_id:
            clauses.append((PackDetails.pack_header_id << pack_header_id))
            if not pack_master:
                if user_id:
                    clauses.append((PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                                   settings.FILLED_PARTIALLY_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT]))
                elif assigned_user_id:
                    clauses.append(
                        (PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS]))
        elif patient_id:
            clauses.append((PatientMaster.id << patient_id))
            clauses.append((PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS]))


        patient_packs_data_dict = {}

        query = PackDetails.select(PackDetails.id.alias('pack_id'),
                                   PackDetails.pack_status,
                                   # fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                                   #       fn.IF((PackHeader.change_rx_flag.is_null(True) | (
                                   #                   PackHeader.change_rx_flag == False)),
                                   #             PackDetails.pack_status, settings.PACK_STATUS_CHANGE_RX),
                                   #       PackDetails.pack_status).alias('pack_status'),
                                   PatientMaster.id.alias('patient_id'),
                                   PatientMaster.first_name,
                                   PatientMaster.last_name,
                                   PackDetails.pack_display_id,
                                   PackDetails.consumption_start_date,
                                   PackDetails.consumption_end_date,
                                   PackHeader.change_rx_flag,

                                   PackUserMap.assigned_to).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .where(PackDetails.company_id == company_id)

        if user_id and not pack_master:
            query = query.where((PackUserMap.assigned_to.not_in([user_id]))|(PackUserMap.assigned_to.is_null(True)))

        if assigned_user_id and not pack_master:
            query = query.where(PackUserMap.assigned_to == assigned_user_id)

        logger.info("In get_patient_manual_packs, clauses: {}".format(clauses))

        if len(clauses) > 0:
            query = query.where(functools.reduce(operator.and_, clauses))

        pack_data_dict = {"pack_data": [], "pack_count": 0}
        i = 1

        logger.info("In get_patient_manual_packs, query: {}".format(list(query)))

        for record in query:
            status_set.add(record["pack_status"])
            patient_packs_data_dict[i] = {"patient_id": record['patient_id'], "pack_id": record['pack_id'],
                                          "pack_display_id": record['pack_display_id'],
                                          "first_name": record['first_name'], "last_name": record['last_name'],
                                          "assigned_user_id": record["assigned_to"],
                                          "pack_status": record["pack_status"],
                                          "admin_start_date": record['consumption_start_date'],
                                          "admin_end_date": record['consumption_end_date'],
                                          "change_rx_flag": record['change_rx_flag']}
            pack_data_dict['pack_data'].append(patient_packs_data_dict[i])
            i += 1
        pack_data_dict['pack_count'] = len(patient_packs_data_dict)

        logger.info("In get_patient_manual_packs, pack_data_dict: {}".format(pack_data_dict))

        if status_set and settings.PROGRESS_PACK_STATUS in status_set:
            pack_data_dict['progress_packs'] = True
        else:
            pack_data_dict['progress_packs'] = False

        return pack_data_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in get_patient_manual_packs {}".format(e))
        raise


@log_args_and_response
def get_patient_packs(patient_id, company_id, pack_header_id):
    logger.debug("Inside get_patient_manual_packs")
    try:
        clauses = []
        status_set = set()

        patient_packs_data_dict = {}

        query = PackDetails.select(PackDetails.id.alias('pack_id'),
                                   PackDetails.pack_status,
                                   PatientMaster.id.alias('patient_id'),
                                   PatientMaster.first_name,
                                   PatientMaster.last_name,
                                   PackDetails.pack_status,
                                   PackDetails.pack_display_id,
                                   PackDetails.consumption_start_date,
                                   PackDetails.consumption_end_date,
                                   PackUserMap.assigned_to).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .where(PackHeader.id == pack_header_id,
                   PackDetails.company_id == company_id)


        logger.info("In get_patient_manual_packs, clauses: {}".format(clauses))

        if len(clauses) > 0:
            query = query.where(functools.reduce(operator.and_, clauses))

        pack_data_dict = {"pack_data": [], "pack_count": 0}
        i = 1

        logger.info("In get_patient_manual_packs, query: {}".format(list(query)))

        for record in query:
            status_set.add(record["pack_status"])
            patient_packs_data_dict[i] = {"patient_id": record['patient_id'], "pack_id": record['pack_id'],
                                          "pack_display_id": record['pack_display_id'],
                                          "first_name": record['first_name'], "last_name": record['last_name'],
                                          "assigned_user_id": record["assigned_to"],
                                          "pack_status": record["pack_status"],
                                          "admin_start_date": record['consumption_start_date'],
                                          "admin_end_date": record['consumption_end_date']}
            pack_data_dict['pack_data'].append(patient_packs_data_dict[i])
            i += 1
        pack_data_dict['pack_count'] = len(patient_packs_data_dict)

        logger.info("In get_patient_manual_packs, pack_data_dict: {}".format(pack_data_dict))

        if status_set and settings.PROGRESS_PACK_STATUS in status_set:
            pack_data_dict['progress_packs'] = True
        else:
            pack_data_dict['progress_packs'] = False

        return pack_data_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in get_patient_manual_packs {}".format(e))
        raise


@log_args_and_response
def db_get_pack_details_v2(pack_id, device_id, company_id, non_fractional=False, exclude_pack_ids=None):
    """
    Fetches pack data and slot data for robot(optionally).

    :param pack_id:
    :param device_id:
    :param company_id:
    :param non_fractional:
    :return:
    """
    logger.debug("Inside db_get_pack_details_v2")
    pack_details_data = None
    try:

        for record in PackDetails.select(PackDetails.id,
                                        PackDetails.pack_display_id,
                                        PackDetails.pack_no,
                                        PackDetails.created_date,
                                        PackDetails.pack_status,
                                        PackDetails.rfid,
                                        PackHeader.patient_id,
                                        PackHeader.delivery_datetime,
                                        PatientMaster.last_name,
                                        PatientMaster.first_name,
                                        PatientMaster.dob,
                                        PatientMaster.allergy,
                                        PatientMaster.patient_no,
                                        FacilityMaster.facility_name,
                                        PatientMaster.facility_id,
                                        PackDetails.order_no,
                                        PackDetails.pack_plate_location,
                                        CodeMaster.value,
                                        CodeMaster.id.alias('pack_status_id')
                                        # PackVerification.pack_fill_status
                                        ).order_by(
                                            PackDetails.created_date
                                        ).dicts() \
                                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                                .where(PackDetails.id == pack_id,
                                        PackDetails.company_id == company_id):

            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])

            if device_id:
                slot_list, max_location, missing_canisters, batch_id, drop_data, expired_canister = \
                    db_slot_details_v2(pack_id, device_id, company_id, non_fractional,
                                                   exclude_pack_ids=exclude_pack_ids)
                error_canisters = dict()
                error_canisters.update(missing_canisters)
                error_canisters.update(expired_canister)
                record["SlotList"] = slot_list
                record["max_location"] = max_location
                record["error_canisters"] = error_canisters
                record["batch_id"] = batch_id
                record["drop_data"] = drop_data
            record["pack_status"] = record["value"]
            record["patient_name"] = record["patient_name"]
            record["facility_name"] = record["facility_name"]
            record["pack_id"] = record["id"]
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            pack_details_data = record

        logger.debug("In db_get_pack_details_v2, pack_details_data fetched")

        return pack_details_data

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.error("Error in db_get_pack_details_v2 {}".format(e))
        raise


@log_args_and_response
def db_get_unassociated_packs(start_date, end_date, system_id):
    """

    @param start_date:
    @param end_date:
    @param system_id:
    @return:
    """
    list_all_unassociated_packs = []
    try:
        for record in PackDetails.select(PackDetails.id.alias('pack_id'),
                                         PackDetails.pack_display_id,
                                         PackDetails.pack_no,
                                         PackDetails.created_date,
                                         PackDetails.pack_status,
                                         PackHeader.patient_id,
                                         PatientMaster.last_name,
                                         PatientMaster.first_name,
                                         FacilityMaster.facility_name,
                                         PatientMaster.facility_id,
                                         CodeMaster.value,
                                         CodeMaster.id.alias('pack_status_id')
                                         ).order_by(
            PackDetails.created_date
        ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .where(PackDetails.system_id == system_id,
                       PackDetails.created_date.between(start_date, end_date),
                       PackDetails.rfid >> None):
            record["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])
            record["pack_status"] = record["value"]
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["facility_name"] = record["facility_name"].strip()
            list_all_unassociated_packs.append(record)

        return list_all_unassociated_packs
    except IntegrityError as e:
        logger.error(e, exc_info=True)
        raise IntegrityError
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError

    except Exception as e:
        logger.error("Error in db_get_unassociated_packs {}".format(e))
        raise


@log_args_and_response
def db_get_status_numeric(pack_id):
    """

    @param pack_id:
    @return:
    """
    status = None
    try:
        query = PackDetails.select(
            CodeMaster.value,
            CodeMaster.id.alias('pack_status_id')
        ).dicts() \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .where(PackDetails.id == pack_id).get()

        status = query["pack_status_id"]
        return status
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except Exception as e:
        logger.error("Error in db_get_status_numeric {}".format(e))
        raise


@log_args_and_response
def db_slot_details(pack_id, device_id, company_id, non_fractional=False, mft_slots_required=False):
    """
    Returns drug data to drop in slot for given pack and robot based on analysis of pack

    :param pack_id:
    :param device_id:
    :param company_id:
    :param non_fractional: whether to floor drug quantity or not (filters out floored 0)
    :return:
    """
    slot_list = defaultdict(list)
    device_id = int(device_id)
    fndc_txr_canister = dict()
    all_location = {-1}
    missing_canisters = dict()
    batch_id = None
    try:

        for record in DeviceMaster.select(LocationMaster.device_id,
                                          LocationMaster.device_id,
                                          CanisterMaster.id.alias('canister_id'),
                                          CanisterMaster.drug_id,
                                          LocationMaster.location_number,
                                          LocationMaster.display_location,
                                          LocationMaster.is_disabled.alias('is_location_disabled'),
                                          ContainerMaster.drawer_name.alias('drawer_number'),
                                          CanisterMaster.available_quantity,
                                          fn.IF(CanisterMaster.available_quantity < 0, 0,
                                                CanisterMaster.available_quantity).alias('display_quantity'),
                                          CanisterMaster.rfid,
                                          DrugMaster.formatted_ndc,
                                          DrugMaster.txr,
                                          DrugMaster.ndc).dicts() \
                .join(LocationMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(CanisterMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .where(DeviceMaster.id == device_id,
                       DeviceMaster.company_id == company_id) \
                .order_by(CanisterMaster.available_quantity.desc()):
            # use canister with max available qty
            # TODO make efficient query
            fndc_txr = (record["formatted_ndc"], record["txr"])
            if fndc_txr in fndc_txr_canister \
                    and fndc_txr_canister[fndc_txr]['available_quantity'] >= record['available_quantity']:
                continue
            fndc_txr_canister[fndc_txr] = {
                "canister_id": record["canister_id"],
                "location_number": record["location_number"],
                "available_quantity": record["available_quantity"],
                "device_id": record["device_id"],
                "drug_id": record["drug_id"],
                "rfid": record["rfid"],
                "display_location": record["display_location"],
                "drawer_number": record["drawer_number"]
            }

        batch_id = db_get_max_batch_id(pack_id)

        batch_id = batch_id.id

        pack_analysis, drop_data, canister_batch_quantity_dict = db_get_pack_analysis(pack_id, batch_id, device_id)
        # default data for missing drug # no canister assigned, will be marked manual
        default_pack_analysis = {
            'rfid': None,
            'device_id': None,
            'canister_id': None,
            'location_number': None,
            'display_location': None,
        }

        # join_condition = ((PackAnalysisDetails.analysis_id == PackAnalysis.id)
        #                   & (PackAnalysisDetails.drug_id == PatientRx.drug_id))
        #  Using analysis data to provide which drugs to be filled by a robot
        query = SlotHeader.select(
            SlotHeader.hoa_date, SlotHeader.hoa_time,
            PackGrid.slot_row, PackGrid.slot_column,
            SlotDetails.quantity,
            SlotDetails.is_manual,
            SlotDetails.id.alias("slot_id"),
            SlotHeader.id.alias('slot_header_id'),
            PatientRx.pharmacy_rx_no,
            SlotDetails.drug_id,
            DrugMaster.drug_name,
            DrugMaster.ndc, DrugMaster.txr,
            DrugMaster.strength_value,
            DrugMaster.strength,
            DrugMaster.color,
            DrugMaster.formatted_ndc, DrugMaster.shape,
            DrugMaster.image_name,
            DrugMaster.imprint
        ) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .where(SlotHeader.pack_id == pack_id)
        for record in query.dicts():
            fndc_txr = (record["formatted_ndc"], record["txr"] or '')
            slot_fndc_txr = (record["formatted_ndc"], record["txr"] or '', record['slot_id'])
            try:
                record.update(pack_analysis[slot_fndc_txr])  # add data of analysis
            except KeyError as e:
                # pack analysis does not have required drug data
                # OR pack rx has updated ndc (most likely)
                logger.warning('Missing fndc_txr {} in pack_analysis for pack_id {}'
                               .format(e, pack_id))
                record.update(default_pack_analysis)
            location = map_pack_location_dao(record["slot_row"], record["slot_column"])
            if record["device_id"] == device_id or record["device_id"] is None or record["quantity"] % 1 != 0:
                all_location.add(location)
            if record["device_id"] != device_id:
                continue  # not to be filled by robot

            # If non fractional flag floor drug qty and do not consider if qty 0
            record["quantity"] = float(record["quantity"])
            if non_fractional:
                record["quantity"] = math.floor(record["quantity"])
                if record["quantity"] <= 0:
                    continue

            record["hoa_date"] = record["hoa_date"].strftime('%Y-%m-%d')
            record["hoa_time"] = record["hoa_time"].strftime('%H:%M:%S')
            # record["device_id"] = device_id
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
            try:
                fndc_txr = (record["formatted_ndc"], record["txr"])
                if fndc_txr in fndc_txr_canister:  # canister present in robot
                    record.update(fndc_txr_canister[fndc_txr])
                    rem_list = ['previous_device_name', 'previous_location_id',
                                'previous_display_location', 'last_seen_time']
                    [record.pop(key) for key in rem_list]
                    # record.pop()
                    slot_list[location].append(record)
                elif record["location_number"]:  # canister found while analysis and not present in robot
                    missing_canisters[record["location_number"]] = {
                        "canister_id": record["canister_id"],
                        "rfid": record["rfid"],
                        "drug_name": record["drug_name"],
                        "ndc": record["ndc"],
                        "color": record["color"],
                        "shape": record["shape"],
                        "imprint": record["imprint"],
                        "image_name": record["image_name"],
                        "formatted_ndc": record["formatted_ndc"],
                        "txr": record["txr"],
                        'previous_device_name': record['previous_device_name'],
                        'previous_location_id': record['previous_location_id'],
                        'previous_display_location': record['previous_display_location'],
                        'last_seen_time': record['last_seen_time']
                    }
            except KeyError as e:
                logger.error(e, exc_info=True)
        return slot_list, max(all_location), missing_canisters, batch_id
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return dict(), max(all_location), missing_canisters, batch_id
    except InternalError as e:
        logger.error(e, exc_info=True)
        return None, max(all_location), missing_canisters, batch_id


@log_args_and_response
def db_slot_details_v2(pack_id, device_id, company_id, non_fractional=False, mft_slots_required=False,
                       exclude_pack_ids=None):
    """
    Returns drug data to drop in slot for given pack and robot based on analysis of pack

    :param pack_id:
    :param device_id:
    :param company_id:
    :param non_fractional: whether to floor drug quantity or not (filters out floored 0)
    :return:
    """
    # logger.debug("Inside db_slot_details_v2")

    slot_list = defaultdict(dict)
    device_id = int(device_id)
    fndc_txr_canister = dict()
    all_location = {-1}
    missing_canisters = dict()
    missing_canister_list = list()
    batch_id = None
    drop_dict = dict()
    exclude_location = list()
    updated_missing_canister = dict()
    expired_canister = dict()
    expired_canister_list = list()
    try:

        # for record in DeviceMaster.select(LocationMaster.device_id,
        #                                   CanisterMaster.id.alias('canister_id'),
        #                                   CanisterMaster.drug_id,
        #                                   LocationMaster.quadrant,
        #                                   LocationMaster.location_number,
        #                                   LocationMaster.display_location,
        #                                   LocationMaster.is_disabled.alias('is_location_disabled'),
        #                                   ContainerMaster.drawer_name.alias('drawer_number'),
        #                                   CanisterMaster.available_quantity,
        #                                   fn.IF(CanisterMaster.available_quantity < 0, 0,
        #                                         CanisterMaster.available_quantity).alias('display_quantity'),
        #                                   CanisterMaster.rfid,
        #                                   DrugMaster.formatted_ndc,
        #                                   DrugMaster.txr,
        #                                   DrugMaster.ndc).dicts() \
        #         .join(ContainerMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
        #         .join(LocationMaster, on=ContainerMaster.id == LocationMaster.container_id) \
        #         .join(CanisterMaster, on=CanisterMaster.location_id == LocationMaster.id) \
        #         .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
        #         .where(DeviceMaster.id == device_id,
        #                LocationMaster.is_disabled == False,
        #                DeviceMaster.company_id == company_id) \
        #         .order_by(CanisterMaster.available_quantity.desc()):
        #     # use canister with max available qty
        #     # TODO make efficient query
        #     fndc_txr = (record["formatted_ndc"], record["txr"] or '', record["quadrant"])
        #     if fndc_txr in fndc_txr_canister \
        #             and fndc_txr_canister[fndc_txr]['available_quantity'] >= record['available_quantity']:
        #         continue
        #     fndc_txr_canister[fndc_txr] = {
        #         "canister_id": record["canister_id"],
        #         "location_number": record["location_number"],
        #         "available_quantity": record["available_quantity"],
        #         "device_id": record["device_id"],
        #         "drug_id": record["drug_id"],
        #         "rfid": record["rfid"],
        #         "display_location": record["display_location"],
        #         "drawer_number": record["drawer_number"]
        #     }
        #     logger.debug(fndc_txr_canister)

        batch_id = db_get_max_batch_id(pack_id)

        # batch_id = batch_id.id

        pack_analysis, drop_data, canister_batch_quantity = db_get_pack_analysis(pack_id,
                                                                                 batch_id,
                                                                                 device_id,
                                                                                 exclude_pack_ids)

        logger.debug("In db_slot_details_v2, pack_analysis:{}".format(pack_analysis))
        logger.debug("In db_slot_details_v2, drop_data:{}".format(drop_data))
        logger.debug("In db_slot_details_v2, canister_batch_quantity:{}".format(canister_batch_quantity))

        # default data for missing drug # no canister assigned, will be marked manual
        default_pack_analysis = {
            'rfid': None,
            'canister_type': None,
            'device_id': None,
            'canister_id': None,
            'location_number': None,
            'display_location': None,
            'quadrant': None,
            'drop_number': None,
            'config_id': None,
            'dest_device_name': None,
            'is_location_empty': None,
            'is_location_disabled': None,
        }

        used_canister_ids = set()
        # join_condition = ((PackAnalysisDetails.analysis_id == PackAnalysis.id)
        #                   & (PackAnalysisDetails.drug_id == PatientRx.drug_id))
        #  Using analysis data to provide which drugs to be filled by a robot
        query = SlotHeader.select(
            SlotHeader.hoa_date,
            SlotHeader.hoa_time,
            PackGrid.slot_row,
            PackGrid.slot_column,
            SlotDetails.quantity,
            SlotDetails.is_manual,
            SlotDetails.id.alias("slot_id"),
            SlotHeader.id.alias('slot_header_id'),
            PatientRx.pharmacy_rx_no,
            PatientRx.daw_code,
            SlotDetails.drug_id,
            DrugMaster.drug_name,
            DrugMaster.ndc, DrugMaster.txr,
            DrugMaster.strength_value,
            DrugMaster.strength,
            DrugMaster.color,
            DrugMaster.formatted_ndc,
            DrugMaster.shape,
            UniqueDrug.is_powder_pill,
            DrugMaster.image_name,
            DrugMaster.imprint,
            DrugMaster.brand_flag,
            DrugDimension.length.alias("dd_length"),
            DrugDimension.width.alias("dd_width"),
            DrugDimension.depth.alias("dd_depth"),
            DrugDimension.fillet.alias("dd_fillet"),
            CustomDrugShape.name.alias("dd_shape"),
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None,
                  DrugStockHistory.created_by).alias("stock_updated_by"),
            fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                  DrugDetails.last_seen_by).alias('last_seen_with'),
            fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                  DrugDetails.last_seen_date).alias('last_seen_on'),
            UniqueDrug.is_delicate
        ) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                      (DrugStockHistory.is_active == True) &
                                                      (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
            .where(SlotHeader.pack_id == pack_id).dicts()

        logger.debug("In db_slot_details_v2, slot_query :{}".format(query))
        ndc_list = []
        for record in query:
            ndc_list.append(int(record['ndc']))
        inventory_data = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        inventory_data_dict = {}
        for item in inventory_data:
            inventory_data_dict[item['ndc']] = item['quantity']

        for record in query:
            record['inventory_qty'] = inventory_data_dict.get(record['ndc'], 0)
            record['is_in_stock'] = 0 if record["inventory_qty"] <= 0 else 1
            fndc_txr = (record["formatted_ndc"], record["txr"] or '')
            slot_fndc_txr = (record["formatted_ndc"], record["txr"] or '', record['slot_id'])
            try:
                used_canister_ids.add(pack_analysis[slot_fndc_txr]['canister_id'])
                # updating batch_required_quantity for given canister
                pack_analysis[slot_fndc_txr]['batch_required_quantity'] = canister_batch_quantity\
                    .get(pack_analysis[slot_fndc_txr]['canister_id'], 0)
                record.update(pack_analysis[slot_fndc_txr])  # add data of analysis
            except KeyError as e:
                # pack analysis does not have required drug data
                # OR pack rx has updated ndc (most likely)
                logger.warning('Missing fndc_txr {} in pack_analysis for pack_id {}'
                               .format(e, pack_id))
                record.update(default_pack_analysis)

            location = map_pack_location_dao(record["slot_row"], record["slot_column"])

            if record["device_id"] == device_id or record["device_id"] is None or record["quantity"] % 1 != 0:
                all_location.add(location)

            if record["device_id"] != device_id or record['location_number'] is None:
                continue  # not to be filled by robot

            # If non fractional flag floor drug qty and do not consider if qty 0
            record["quantity"] = float(record["quantity"])

            if non_fractional:
                record["quantity"] = math.floor(record["quantity"])
                if record["quantity"] <= 0:
                    continue
            record["quantity"] = record["quantity"] - (record["quantity"] % 1)
            record["hoa_date"] = record["hoa_date"].strftime('%Y-%m-%d')
            record["hoa_time"] = record["hoa_time"].strftime('%H:%M:%S')
            # record["device_id"] = device_id
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
            try:
                fndc_txr = (record["formatted_ndc"], record["txr"] or '', record['quadrant'])
                fndc_txr_key = '{}{}{}'.format(record["formatted_ndc"], settings.FNDC_TXR_SEPARATOR,
                                               record['txr'] or '')
                if record['current_device_id'] == device_id and \
                        record['current_quadrant'] == record['quadrant']:  # canister present in robot
                    # record.update(fndc_txr_canister[fndc_txr])
                    record.update({"location_number": record["current_location_number"],
                                   "device_id": record["current_device_id"],
                                   "display_location": record["current_display_location"],
                                   "drawer_number": record["drawer_number"]})

                    rem_list = ['previous_device_name', 'previous_location_id',
                                'previous_display_location', 'last_seen_time']
                    [record.pop(key) for key in rem_list]

                    slot_list[location][fndc_txr_key] = record

                    # logger.info("In db_slot_details_v2, slot_list: {}".format(slot_list))

                elif record["location_number"] and record[
                    'canister_id'] not in missing_canister_list:  # canister found while analysis and not present in robot
                    missing_canister_list.append(record['canister_id'])
                    device_zone_data = get_zone_by_device_id(device_id, company_id)
                    csr_canister_data = dict()
                    if device_zone_data:
                        csr_canister_data = get_csr_canister_by_fndc_txr(company_id,
                                                                         record['formatted_ndc'],
                                                                         record['txr'],
                                                                         device_zone_data['zone_id'])
                    canister_location_dict = db_get_current_location_details_by_canisters(
                        list(used_canister_ids))
                    missing_display_location = record['display_location']
                    exclude_location.append(record['missing_location_id'])
                    missing_canisters[missing_display_location] = {
                        "canister_id": record["canister_id"],
                        "canister_type": record["canister_type"],
                        "rfid": record["rfid"],
                        "is_location_disabled": record["is_location_disabled"],
                        "is_location_empty": record["is_location_empty"],
                        "quadrant": record["quadrant"],
                        "drug_name": record["drug_name"],
                        "ndc": record["ndc"],
                        "color": record["color"],
                        "shape": record["shape"],
                        "imprint": record["imprint"],
                        "brand_flag": record["brand_flag"],
                        "daw_code": record["daw_code"],
                        "is_powder_pill": record["is_powder_pill"],
                        "image_name": record["image_name"],
                        "formatted_ndc": record["formatted_ndc"],
                        "txr": record["txr"],
                        "dest_device_name": record["dest_device_name"],
                        "dest_display_location": missing_display_location,
                        "is_active": canister_location_dict[record["canister_id"]]["active"],
                        "current_display_location": canister_location_dict[record["canister_id"]][
                            'display_location'],
                        "current_device_id": canister_location_dict[record["canister_id"]][
                            'device_id'],
                        "current_location_number": canister_location_dict[record["canister_id"]][
                            'location_number'],
                        "is_current_location_disabled": canister_location_dict[record["canister_id"]][
                            "is_location_disabled"],
                        "current_quadrant": canister_location_dict[record["canister_id"]][
                            'quadrant'],
                        "current_device_name": canister_location_dict[record["canister_id"]][
                            'device_name'],
                        "current_device_type_id": canister_location_dict[record["canister_id"]]['device_type_id'],
                        "current_serial_number": canister_location_dict[record["canister_id"]]['serial_number'],
                        "current_shelf": canister_location_dict[record["canister_id"]]['shelf'],
                        "current_device_ip_address": canister_location_dict[record["canister_id"]]['device_ip_address'],
                        "current_ip_address": canister_location_dict[record["canister_id"]]['ip_address'],
                        "current_secondary_ip_address": canister_location_dict[record["canister_id"]]['secondary_ip_address'],
                        "current_drawer_number": canister_location_dict[record["canister_id"]]['drawer_name'],
                        'previous_device_name': record['previous_device_name'],
                        'previous_location_id': record['previous_location_id'],
                        'previous_display_location': record['previous_display_location'],
                        'last_seen_time': record['last_seen_time'],
                        'batch_required_quantity': record['batch_required_quantity'],
                        'canister_capacity': record['canister_capacity'],
                        'expiry_status': record["expiry_status"],
                        'missing_canister': True,
                        "canister_drug_id": record["drug_id"],
                        "available_quantity": record["available_quantity"],
                        "is_in_stock": record.get("is_in_stock", None),
                        "is_delicate":record["is_delicate"]
                    }
                    if csr_canister_data:
                        missing_canisters[missing_display_location].update({
                            'csr_name': csr_canister_data['name'],
                            'csr_display_location': csr_canister_data['display_location'],
                            'is_csr_location_disabled': csr_canister_data['is_location_disabled'],
                            'csr_drawer': csr_canister_data['drawer_number'],
                            'csr_canister_id': csr_canister_data['canister_id'],
                            'csr_zone': csr_canister_data['zone_name']
                        })

                if record["canister_id"] not in expired_canister_list and record["canister_id"] not in missing_canister_list and record.get("expiry_status") == 0:
                    expired_canister_list.append(record['canister_id'])
                    device_zone_data = get_zone_by_device_id(device_id, company_id)
                    csr_canister_data = dict()
                    if device_zone_data:
                        csr_canister_data = get_csr_canister_by_fndc_txr(company_id,
                                                                         record['formatted_ndc'],
                                                                         record['txr'],
                                                                         device_zone_data['zone_id'])
                    canister_location_dict = db_get_current_location_details_by_canisters(
                        list(used_canister_ids))
                    expired_display_location = record['display_location']
                    expired_canister[expired_display_location] = {
                        "canister_id": record["canister_id"],
                        "canister_type": record["canister_type"],
                        "rfid": record["rfid"],
                        "is_location_disabled": record["is_location_disabled"],
                        "is_location_empty": record["is_location_empty"],
                        "quadrant": record["quadrant"],
                        "drug_name": record["drug_name"],
                        "ndc": record["ndc"],
                        "color": record["color"],
                        "shape": record["shape"],
                        "imprint": record["imprint"],
                        "brand_flag": record["brand_flag"],
                        "daw_code": record["daw_code"],
                        "is_powder_pill": record["is_powder_pill"],
                        "image_name": record["image_name"],
                        "formatted_ndc": record["formatted_ndc"],
                        "txr": record["txr"],
                        "dest_device_name": record["dest_device_name"],
                        "dest_display_location": expired_display_location,
                        "is_active": canister_location_dict[record["canister_id"]]["active"],
                        "current_display_location": canister_location_dict[record["canister_id"]][
                            'display_location'],
                        "current_device_id": canister_location_dict[record["canister_id"]][
                            'device_id'],
                        "current_location_number": canister_location_dict[record["canister_id"]][
                            'location_number'],
                        "is_current_location_disabled": canister_location_dict[record["canister_id"]][
                            "is_location_disabled"],
                        "current_quadrant": canister_location_dict[record["canister_id"]][
                            'quadrant'],
                        "current_device_name": canister_location_dict[record["canister_id"]][
                            'device_name'],
                        "current_device_type_id": canister_location_dict[record["canister_id"]]['device_type_id'],
                        "current_serial_number": canister_location_dict[record["canister_id"]]['serial_number'],
                        "current_shelf": canister_location_dict[record["canister_id"]]['shelf'],
                        "current_device_ip_address": canister_location_dict[record["canister_id"]][
                            'device_ip_address'],
                        "current_ip_address": canister_location_dict[record["canister_id"]]['ip_address'],
                        "current_secondary_ip_address": canister_location_dict[record["canister_id"]][
                            'secondary_ip_address'],
                        "current_drawer_number": canister_location_dict[record["canister_id"]]['drawer_name'],

                        'batch_required_quantity': record['batch_required_quantity'],
                        'canister_capacity': record['canister_capacity'],
                        'expiry_status': record['expiry_status'],
                        'missing_canister': False,
                        "canister_drug_id": record["drug_id"],
                        "available_quantity": record["available_quantity"],
                        "is_in_stock": record.get("is_in_stock", None),
                        "is_delicate": record["is_delicate"]
                    }
                    if csr_canister_data:
                        expired_canister[expired_display_location].update({
                            'csr_name': csr_canister_data['name'],
                            'csr_display_location': csr_canister_data['display_location'],
                            'is_csr_location_disabled': csr_canister_data['is_location_disabled'],
                            'csr_drawer': csr_canister_data['drawer_number'],
                            'csr_canister_id': csr_canister_data['canister_id'],
                            'csr_zone': csr_canister_data['zone_name']
                        })

            except KeyError as e:
                logger.error(e, exc_info=True)

        for missing_canister_display_location, missing_can_data in missing_canisters.items():
            missing_display_location = missing_canister_display_location
            logger.debug('missing_canister_id: {} is_location_empty: {} is_location_disable: {}'
                         .format(missing_can_data['canister_id'], missing_can_data['is_location_empty'],
                                 missing_can_data['is_location_disabled']))
            if not missing_can_data['is_location_empty'] or missing_can_data['is_location_disabled']:
                logger.debug('fetching_empty_location_for_canister: {}'.format(missing_can_data['canister_id']))
                logger.debug(exclude_location)
                drawer_type = []
                if missing_can_data['canister_type']:
                    drawer_type = [missing_can_data['canister_type']]
                empty_location_data = get_empty_location_by_quadrant(
                    device_id, missing_can_data["quadrant"], company_id,
                    drawer_type=drawer_type, exclude_location=exclude_location)
                logger.debug('empty_location_data for canister_id: {}: {}'.format(missing_can_data['canister_id'],
                                                                                  empty_location_data))
                if empty_location_data:
                    missing_display_location = empty_location_data["display_location"]
                    missing_can_data['dest_display_location'] = empty_location_data["display_location"]
                    exclude_location.append(empty_location_data["location_id"])
            updated_missing_canister[missing_display_location] = missing_can_data

        return slot_list, max(all_location), updated_missing_canister, batch_id, drop_data, expired_canister

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return dict(), max(all_location), updated_missing_canister, batch_id, dict()
    except InternalError as e:
        logger.error(e, exc_info=True)
        return None, max(all_location), updated_missing_canister, batch_id, None
    except Exception as e:
        logger.error(e)
        logger.error("error in db_slot_details_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in db_slot_details_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")

@log_args_and_response
def db_slots_for_user_station(pack_id):
    """

    @param pack_id:
    @return:
    """
    latest_created_date_time = datetime.datetime.now()
    slot_data = []
    try:
        # in case of deferred pack, to consider the latest record.
        for rec in SlotTransaction.select(fn.MAX(SlotTransaction.created_date_time).alias(
                "latest_created_date_time")).dicts().where(SlotTransaction.pack_id == pack_id):
            latest_created_date_time = rec["latest_created_date_time"]

        for record in SlotTransaction.select(SlotTransaction.drug_id,
                                             SlotDetails.quantity.alias("required_qty"),
                                             fn.sum(SlotTransaction.dropped_qty).alias("robot_qty"),
                                             SlotHeader.hoa_date,
                                             SlotHeader.hoa_time,
                                             PackGrid.slot_row,
                                             PackGrid.slot_column,
                                             DrugMaster.drug_name,
                                             DrugMaster.ndc,
                                             DrugMaster.strength,
                                             DrugMaster.imprint,
                                             DrugMaster.strength_value,
                                             DrugMaster.color, DrugMaster.shape,
                                             PatientRx.pharmacy_rx_no,
                                             PatientRx.sig).dicts() \
                .join(SlotDetails, on=SlotTransaction.slot_id == SlotDetails.id) \
                .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(DrugMaster, on=SlotTransaction.drug_id == DrugMaster.id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .where((SlotHeader.pack_id == pack_id) & (SlotTransaction.created_date_time >=
                                                          latest_created_date_time)) \
                .group_by(SlotTransaction.slot_id):
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
            slot_data.append(record)
        return slot_data
    except InternalError as e:
        logger.error(e, exc_info=True)
        return None
    except Exception as e:
        logger.error("Error in db_slots_for_user_station {}".format(e))
        raise


@log_args_and_response
def db_get_label_info(pack_id):
    """

    @param pack_id:
    @return:
    """
    try:
        logger.info("Inside prepare_label_data db_get_label_info")
        OtherPackDetails = PackDetails.alias()

        for record in PackDetails.select(PackDetails.consumption_end_date.alias('filled_end_date'),
                                         # removing slot_header join as pack start date and pack end date available in pack_details
                                         PackDetails.consumption_start_date.alias('filled_start_date'),
                                         PackDetails.pack_display_id,
                                         PackDetails.pack_no,
                                         PackDetails.filled_by,
                                         PackDetails.filled_days,
                                         PackDetails.created_date,
                                         PackDetails.delivery_schedule,
                                         PackDetails.car_id,
                                         PackDetails.pack_status,
                                         PackDetails.packaging_type,
                                         fn.DATE(PackDetails.filled_date).alias('filled_date'),
                                         PackHeader.patient_id,
                                         PackHeader.delivery_datetime,
                                         PackHeader.scheduled_delivery_date,
                                         fn.IF(PackUserMap.id.is_null(True), PackDetails.filled_at,
                                               settings.FILLED_AT_PACK_FILL_WORKFLOW).alias('filled_at'),
                                         fn.Max(OtherPackDetails.pack_no).alias('max_pack_no'),
                                         fn.IF(ExtPackDetails.id.is_null(True), False, True).alias("change_rx")
                                         ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(OtherPackDetails, JOIN_LEFT_OUTER, on=PackHeader.id == OtherPackDetails.pack_header_id) \
                .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
                .join(ExtPackDetails, JOIN_LEFT_OUTER, on=PackDetails.id == ExtPackDetails.pack_id) \
                .where(PackDetails.id == pack_id) \
                .group_by(PackDetails.id):
            # below code commented as discussed with Raj that filled date should be the date when pack is filled
            # and not the created date
            if not record["filled_date"]:
                # to handle case when getlabelinfo is called for label count
                record["filled_date"] = record["created_date"]

            if record["change_rx"]:
                record["change_rx"] = True
            else:
                record["change_rx"] = False

            expiry_date = get_expiry_date_of_filled_pack(pack_id)
            try:
                expiry_date = expiry_date.replace("-", "/")
            except Exception as e:
                logger.error(f"Error in db_get_label_info, date format is not correct. e: {e} ")

            record["exp_date"] = expiry_date if expiry_date else (
                        record["filled_date"] + datetime.timedelta(days=settings.PACK_EXP_OFFSET)).strftime(
                '%m/%y')

            record["scheduled_delivery_date"] = record['scheduled_delivery_date'].strftime('%Y-%m-%d') if record[
                'scheduled_delivery_date'] else None
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            yield record
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        yield None
    except InternalError as e:
        logger.error(e)
        yield None
    except Exception as e:
        logger.error(e)
        yield None


@log_args_and_response
def db_max_assign_order_no_manual_packs(company_id, pack_ids):
    """

    @param company_id:
    @param pack_ids:
    @return:
    """
    try:
        order_no = PackDetails.select(fn.MAX(PackDetails.order_no).alias('order_no')) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id).dicts() \
            .where(PackDetails.company_id == company_id).get()
        length = len(pack_ids)
        order_no = order_no['order_no']
        if order_no is None:
            order_no = 1
        elif (order_no == 0) | (order_no + length >= settings.DB_MAX_INT_VALUE):
            order_no = 1
        else:
            order_no += 1

        # assigning orders to packs
        order_no_list = list(range(order_no, order_no + length))

        updated_pack_query = PackDetails.select(PackDetails.id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.id << pack_ids) \
            .order_by(PackHeader.scheduled_delivery_date, FacilityMaster.facility_name, PackDetails.id)
        updated_list = list(updated_pack_query.dicts())
        for index, item in enumerate(order_no_list):
            update_info = PackDetails.update(order_no=order_no_list[index]).where(
                PackDetails.id == int(updated_list[index]['id'])).execute()

    except Exception as e:
        logger.error("Error in db_max_assign_order_no_manual_packs {}".format(e))
        raise


@log_args_and_response
def db_get_pack_drugs_by_pack(company_id, pack_list):
    try:
        pack_drugs = defaultdict(list)
        query = PackDetails.select(
            PackDetails.id,
            DrugMaster.formatted_ndc,
            DrugMaster.txr
        ).join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list,
                   PackDetails.company_id == company_id)

        for record in query.dicts():
            if record["id"] not in pack_drugs:
                pack_drugs[record["id"]] = []
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"]
            )
            pack_drugs[record["id"]].append(fndc_txr)
        return pack_drugs
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def db_get_pack_and_drug_by_patient(company_id, pack_list):
    """
    Returns patient_packs, patient_drugs for given pack_list and company_id.
    - patient_packs is dict with patient_id as key and `set` of packs as value
    - patient_drugs is dict with patient_id as key and `set` of fndc_txr as value
    :param company_id: int Company ID
    :param pack_list: list List of Pack IDs
    :return: tuple
    """
    logger.debug("Inside db_get_pack_and_drug_by_patient")
    try:
        patient_packs = defaultdict(set)
        patient_drugs = defaultdict(set)

        query = PackDetails.select(
                            PackHeader.patient_id,
                            fn.GROUP_CONCAT(
                                fn.DISTINCT(fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')))
                            ).alias('drugs'),
                            # fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).alias('packs')
                            PackDetails.id.alias('pack_id')) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list,
                   PackDetails.company_id == company_id, PackHeader.scheduled_delivery_date.is_null(False)) \
            .group_by(PackDetails.id)

        for record in query.dicts():
            if record['patient_id'] not in patient_packs:
                patient_packs[record['patient_id']] = set()
                patient_drugs[record['patient_id']] = set()

            patient_drugs[record['patient_id']].update(record['drugs'].split(','))
            patient_packs[record['patient_id']].add(str(record['pack_id']))

        logger.info("In db_get_pack_and_drug_by_patient, patient_packs: {}, patient_drugs: {}".format(patient_packs,
                                                                                                      patient_drugs))

        return patient_packs, patient_drugs

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_pack_and_drug_by_patient: {}".format(e))
        raise


@log_args_and_response
def get_patient_data_for_packs(pack_list):
    """

    @param pack_list:
    @return:
    """
    logger.debug("Inside get_patient_data_for_packs")
    try:
        patient_data = PackDetails.select(PatientMaster.id,
                                          FacilityMaster.facility_name,
                                          PatientMaster.concated_patient_name_field().alias('patient_name'),
                                          fn.count(PackDetails.id).alias('total_packs')).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=PatientMaster.facility_id == FacilityMaster.id) \
            .where(PackDetails.id << pack_list) \
            .group_by(PatientMaster.id)
        return list(patient_data)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def db_get_slot_wise_drug_data_for_packs(pack_list):
    """
    fetch slot wise drug data for all given packs
    @param pack_list: list of pack ids
    @return:
    """
    logger.debug("Inside db_get_slot_wise_drug_data_for_packs")
    try:

        logger.info(f"In db_get_slot_wise_drug_data_for_packs, pack_list: {pack_list}")

        pack_drug_data = PackDetails.select(
            fn.SUM(SlotDetails.quantity).alias('quantity'),
            DrugMaster,
            DrugMaster.concated_drug_name_field().alias('full_drug_name'),
            DrugMaster.concated_fndc_txr_field().alias('con_fndc_txr'),
            DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_full_name'),
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                'stock_updated_by'),
            fn.IF(DrugStockHistory.created_date.is_null(True), None, DrugStockHistory.created_date)
                .alias('stock_updated_on'),
            DrugDetails.last_seen_by.alias("last_seen_with"),
            DrugDetails.last_seen_date.alias("last_seen_on"),
            PartiallyFilledPack.missing_qty,
            PatientRx.daw_code,
            SlotDetails.is_manual,
            fn.sum(SlotTransaction.dropped_qty).alias('dropped_qty'),
            PartiallyFilledPack.note,
            DrugStatus.ext_status,
            DrugStatus.last_billed_date,
            DrugStatus.ext_status_updated_date,
        ).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (PackDetails.company_id == DrugDetails.company_id)) \
            .join(PartiallyFilledPack, JOIN_LEFT_OUTER, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .where(PackDetails.id << pack_list) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr, PatientRx.daw_code, SlotDetails.id) \
            .order_by(DrugMaster.concated_drug_name_field())

        logger.info("In db_get_slot_wise_drug_data_for_packs, pack_drug_data fetched.")

        return list(pack_drug_data)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in db_get_slot_wise_drug_data_for_packs: {e}")
        raise


@log_args_and_response
def db_get_pack_status_by_pack_list(pack_list):
    try:
        status_pack_count = {}
        query = PackDetails.select(CodeMaster.value, fn.COUNT(PackDetails.id).alias('status_count')) \
            .join(CodeMaster, on=CodeMaster.id == PackDetails.pack_status) \
            .where(PackDetails.id << pack_list) \
            .group_by(PackDetails.pack_status) \
            .dicts()
        for record in query.dicts():
            status_pack_count[record['value']] = record['status_count']
        return status_pack_count
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def db_get_batch_canister_manual_drugs(system_id, list_type, pack_ids=None, pack_queue=True):
    """
    Returns list of canister drugs or manual drugs based on drug_type
    @param batch_id:
    @param list_type: drug | patient | facility
    @param pack_ids:
    @param pack_queue:
    @return:
    """
    drug_type = "canister"
    if system_id:
        try:
            query = PackAnalysisDetails.select(PackAnalysis.pack_id,
                                               fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysis.pack_id)).alias(
                                                   'pack_ids_group'),
                                               fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_display_id)).alias(
                                                   'pack_display_ids_group'),
                                               PackDetails.pack_status,
                                               fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.canister_id)).alias(
                                                   'canister_id'),
                                               SlotDetails.drug_id,
                                               PackAnalysis.manual_fill_required, PackAnalysisDetails.id,
                                               fn.GROUP_CONCAT(fn.DISTINCT(SlotDetails.quantity)).alias(
                                                   'quantities'),
                                               fn.GROUP_CONCAT(SlotDetails.quantity).alias(
                                                   'total_quantities').coerce(False),
                                               fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('drug_qty'),
                                               fn.SUM(SlotDetails.quantity).alias('total_qty'),
                                               DrugMaster.drug_name,
                                               DrugMaster.strength,
                                               DrugMaster.strength_value,
                                               DrugMaster.imprint,
                                               DrugMaster.image_name,
                                               DrugMaster.shape,
                                               DrugMaster.color,
                                               DrugMaster.formatted_ndc,
                                               DrugMaster.manufacturer,
                                               DrugMaster.ndc,
                                               DrugMaster.txr,
                                               PackAnalysisDetails.device_id,
                                               PackAnalysisDetails.location_number,
                                               DeviceMaster.name.alias('device_name'),
                                               FacilityMaster.facility_name,
                                               PackDetails.pack_display_id,
                                               PackDetails.order_no,
                                               PackDetails.created_date.alias('uploaded_date'),
                                               PatientMaster.last_name,
                                               PatientMaster.first_name,
                                               PatientMaster.patient_no,
                                               PatientMaster.facility_id,
                                               PackHeader.patient_id,
                                               LocationMaster.display_location,
                                               ContainerMaster.drawer_name.alias('drawer_number'),
                                               CanisterMaster.available_quantity,
                                               fn.IF(CanisterMaster.available_quantity < 0, 0,
                                                     CanisterMaster.available_quantity).alias('display_quantity'),
                                               PatientMaster.facility_id,
                                               PackDetails.consumption_start_date,
                                               PackDetails.consumption_end_date,
                                               PackHeader.delivery_datetime) \
                .dicts() \
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(PackQueue, on=PackQueue.pack_id == PackAnalysis.pack_id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(PackDetails, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == PackAnalysisDetails.device_id) \
                .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientSchedule.patient_id == PatientMaster.id) &
                                                            (PatientSchedule.facility_id == FacilityMaster.id))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id)

            if pack_ids:
                query = query.where(PackDetails.system_id == system_id,
                                    PackAnalysis.pack_id << pack_ids)
            else:
                query = query.where(PackDetails.system_id == system_id)

            if drug_type == "canister":
                query = query.where(PackAnalysisDetails.canister_id.is_null(False),
                                    PackAnalysisDetails.device_id.is_null(False))

            elif drug_type == "manual":
                query = query.where((PackAnalysisDetails.canister_id.is_null(True) |
                                     PackAnalysisDetails.device_id.is_null(True) |
                                     SlotDetails.quantity << settings.DECIMAL_QTY_LIST))

            if pack_queue:
                query = query.where(
                    PackDetails.pack_status << ([settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]))
                if list_type == "drug":
                    query = query.group_by(SlotDetails.drug_id).order_by(DrugMaster.drug_name)
                elif list_type == "patient":
                    query = query.group_by(PatientMaster.id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                        .order_by(DrugMaster.drug_name)
                elif list_type == "facility":
                    query = query.group_by(PatientMaster.facility_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                        .order_by(DrugMaster.drug_name)
                else:
                    query = query.group_by(PackAnalysis.pack_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                        .order_by(PackDetails.order_no)

            else:
                query = query.group_by(PackAnalysis.pack_id, SlotDetails.drug_id, PackAnalysisDetails.canister_id) \
                    .order_by(PackDetails.order_no)

            for record in query.dicts():
                record["patient_name"] = record["last_name"] + ", " + record["first_name"]
                record["drug_qty"] = float(record["drug_qty"])
                record["total_qty"] = float(record["total_qty"])
                record['delivery_datetime'] = str(record['delivery_datetime']) if record[
                    'delivery_datetime'] else None

                yield record
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise


def get_delivery_date_list_of_pending_packs(patient_schedule_ids):
    """
    Method to get min delivery date based on patient schedule ids
    @return:
    """
    try:
        delivery_date_set = set()
        query = PatientSchedule.select(PackHeader.scheduled_delivery_date).dicts() \
            .join(PatientMaster, on=PatientSchedule.patient_id == PatientMaster.id) \
            .join(PackHeader, on=PackHeader.patient_id == PatientMaster.id) \
            .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
            .where(PatientSchedule.id.in_(patient_schedule_ids),
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                   PackDetails.batch_id.is_null(True)) \
            .group_by(PackHeader.id)
        for record in query:
            delivery_date_set.add(record["scheduled_delivery_date"])
        return list(delivery_date_set)

    except (InternalError, IntegrityError) as e:
        raise e


@log_args_and_response
def get_unscheduled_packs_dao(pack_id):

    logger.debug("Inside get_unscheduled_packs_dao")
    try:

        query = PackHeader.select(PackDetails.id,
                                  PackDetails.pack_display_id,
                                  PackDetails.pack_no,
                                  PackDetails.created_date,
                                  PackDetails.pack_status,
                                  PackDetails.rfid,
                                  PackHeader.patient_id,
                                  PatientMaster.last_name,
                                  PatientMaster.first_name,
                                  PatientMaster.dob,
                                  PatientMaster.allergy,
                                  PatientMaster.patient_no,
                                  FacilityMaster.facility_name,
                                  PatientMaster.facility_id,
                                  PackDetails.order_no,
                                  PackDetails.pack_plate_location,
                                  PackHeader.scheduled_delivery_date.alias('delivery_date'),
                                  # CodeMaster.value,
                                  # CodeMaster.id.alias('pack_status_id'),
                                  # PackVerification.pack_fill_status,
                                  PackDetails.consumption_start_date,
                                  PackDetails.consumption_end_date) \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.id == pack_id)
        print(query)
        pack_details_data = {}
        count = 0
        for record in query.dicts():

            logger.info("In get_unscheduled_packs_dao, record: {}".format(record))

            if record['delivery_date'] is not None:
                count += 1
                continue
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])
            record["consumption_start_date"] = convert_date_from_sql_to_display_date(
                record["consumption_start_date"])
            record["consumption_end_date"] = convert_date_from_sql_to_display_date(record["consumption_end_date"])
            record["admin_period"] = record["consumption_start_date"] + "  to  " + record["consumption_end_date"]
            # record["pack_status"] = record["value"]
            record["patient_name"] = record["patient_name"]
            record["facility_name"] = record["facility_name"]
            record["pack_id"] = record["id"]
            record["delivery_date"] = record["delivery_date"]
            pack_details_data = record
        return pack_details_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_unscheduled_packs_dao {}".format(e))
        raise e


@log_args_and_response
def get_each_pack_delivery_date(pack_list):
    """
    Function to get delivery date pack wise for all scheduled and unscheduled packs
    :param pack_list:
    :return:
    """
    pack_dd_dict = {}
    try:
        query = PackDetails.select(
            PackDetails.id,
            PackHeader.patient_id,
            PackHeader.scheduled_delivery_date.alias('scheduled_delivery_date')
        ).join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id).where(PackDetails.id << pack_list)

        for record in query.dicts():
            if record['id'] not in pack_dd_dict:
                pack_dd_dict[record['id']] = record["scheduled_delivery_date"]
        return pack_dd_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_pack_ids_dao(batch_id: int, system_id: int) -> List[int]:
    try:
        return PackDetails.db_get_pack_ids(batch_id=batch_id, system_id=system_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_pack_wise_delivery_date(pack_list):
    patient_dd_dict = {}

    logger.debug("Inside get_pack_wise_delivery_date")

    try:
        query = PackDetails.select(PackDetails.id,
                                   PackHeader.patient_id,
                                   PackHeader.scheduled_delivery_date.alias('scheduled_delivery_date')) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(PackDetails.id << pack_list, PackHeader.scheduled_delivery_date.is_null(False))
        # PackHeader.scheduled_delivery_date.is_null(True)

        for record in query.dicts():

            logger.info("In get_pack_wise_delivery_date, record: {}".format(record))

            if record['patient_id'] not in patient_dd_dict:
                patient_dd_dict[record['patient_id']] = record["scheduled_delivery_date"]

        return patient_dd_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_pack_history_by_pack_id(pack_id):
    """
    Get pack History Details for given pack_id
    @param pack_id: int
    @return: query record
    """
    logger.debug("Inside get_pack_history_by_pack_id")
    try:
        verification_status = None
        DrugMasterAlias = DrugMaster.alias()
        pack_history_data = []
        drug_master_join = ((PackHistory.action_id << [settings.PACK_HISTORY_NDC_CHANGE]) &
                            (DrugMaster.id == PackHistory.old_value))
        drug_master_alias_join = ((PackHistory.action_id << [settings.PACK_HISTORY_NDC_CHANGE]) &
                                  (DrugMasterAlias.id == PackHistory.new_value))
        query = PackHistory.select(PackHistory.id.alias('pack_history_id'),
                                   PackHistory.pack_id,
                                   PackHistory.action_date_time,
                                   PackHistory.action_taken_by,
                                   PackHistory.action_id,
                                   PackHistory.old_value,
                                   PackHistory.new_value,
                                   DrugMaster.id.alias('old_drug_id'),
                                   DrugMaster.ndc.alias('old_drug_ndc'),
                                   DrugMaster.concated_drug_name_field().alias('old_drug_name'),
                                   DrugMasterAlias.id.alias('new_drug_id'),
                                   DrugMasterAlias.ndc.alias('new_drug_ndc'),
                                   DrugMasterAlias.concated_drug_name_field().alias('new_drug_name'),
                                   PackHistory.from_ips, PackDetails.verification_status
                                   ) \
            .join(DrugMaster, JOIN_LEFT_OUTER, on=drug_master_join) \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=drug_master_alias_join) \
            .join(PackDetails, on=PackDetails.id == PackHistory.pack_id)    \
            .where(PackHistory.pack_id == pack_id).order_by(
            PackHistory.action_date_time.desc(),
            PackHistory.id.desc())

        for record in query.dicts():
            pack_history_data.append(record)
        if pack_history_data:
            verification_status = pack_history_data[0]["verification_status"]
        response = {"history": pack_history_data,
                    "verification_status": verification_status}
        return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def delete_partially_filled_pack(pack_details):
    pack_ids = pack_details['pack_ids']
    try:
        query = PartiallyFilledPack.select(PartiallyFilledPack.id).dicts() \
            .join(PackRxLink, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id).where(PackDetails.id << pack_ids)
        partially_filled_ids = [item['id'] for item in list(query)]
        status = 0
        if partially_filled_ids:
            status = PartiallyFilledPack.delete().where(PartiallyFilledPack.id << partially_filled_ids).execute()
        return status
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def set_status_pack_details(pack_ids, pack_status, user_id, reason_dict=None,
                  use_company_id=False, system_id=None, filled_at=None, fill_time=None, filled_by=None,
                  transfer_to_manual_fill_system=False, change_rx_token=None):

    logger.debug("Inside set_status_pack_details")

    pack_status_list = []
    update_pack_usage_ids: List[int] = []
    current_date_time = get_current_date_time()
    notification_found: bool = False
    ext_pack_ids: List[int] = []
    ext_pack_display_ids: List[int] = []
    ext_data: Dict[str, Any] = {}
    pack_display_id_status_dict: Dict[int, Dict[str, Any]] = {}
    try:
        # throw error if use_company_id and status is manual as we have to set system_id for such packs
        if use_company_id and pack_status == settings.PACK_FILLING_DONE_STATUS_LIST and not system_id:
            return error(1020, "The parameter system_id is required when use_company_id is "
                               "true and pack_status is Manual({}).".format(settings.MANUAL_PACK_STATUS))

        if pack_status in settings.PACK_FILLING_DONE_STATUS_LIST and pack_ids:
            query = PackDetails.select(PackDetails.id) \
                .where(PackDetails.id << pack_ids,
                       PackDetails.system_id.is_null(True))

            if not system_id and not use_company_id and query.count() > 0:
                return error(1020, "Cannot set status to one of these {} without allocating pack to system. "
                                   "Use flag use_company_id true and send system_id to "
                                   "allocate pack to a system.".format(settings.PACK_FILLING_DONE_STATUS_LIST))

        if pack_status == settings.DELETED_PACK_STATUS:
            logger.debug("Fetch the details of Pack Status at the time of Pack Deletion to make decision on "
                         "Notifications.")
            query = PackDetails.select(PackDetails.id, PackDetails.pack_display_id, PackDetails.pack_status).dicts() \
                .where(PackDetails.id << pack_ids)
            for pack in query:
                pack_display_id_status_dict[pack["pack_display_id"]] = {"pack_id": pack["id"],
                                                                        "pack_status": pack["pack_status"]
                                                                        }

        with db.transaction():
            if not pack_status == settings.DISCARDED_PACK_STATUS:
                update_dict = {
                    "pack_status": pack_status,
                    "modified_by": user_id,
                    "modified_date": current_date_time,
                    "fill_time": fill_time
                }
                if filled_at:
                    update_dict.update({"filled_at": filled_at})
                if use_company_id and system_id \
                        and pack_status in settings.PACK_FILLING_DONE_STATUS_LIST:
                    update_dict['system_id'] = system_id
                    logger.debug('Setting system_id {} for pack_ids {}'.format(system_id, pack_ids))
                if pack_status in settings.PACK_FILLING_DONE_STATUS_LIST_MOD:
                    update_dict['filled_date'] = current_date_time
                    if transfer_to_manual_fill_system:
                        update_dict['filled_date'] = None
                    # else:
                    #     if not transfer_to_manual_fill_system:
                    #         update_dict['filled_date'] = current_date_time

                    # if filled_at != settings.FILLED_AT_PRI_PROCESSING:
                    if filled_by:
                        update_dict['filled_by'] = filled_by
                pack_instance = PackDetails.update(**update_dict) \
                    .where(PackDetails.id << pack_ids)
                status = pack_instance.execute()
                logger.info("In set_status_pack_details; pack_details_pack_status_change_pack_ids: " + str(
                    pack_ids) + ' updated info : ' +
                            str(update_dict) + ' updated pack count' + str(status))

            else:
                status = 1  # to handle discarded pack scenario
            for item in pack_ids:
                # modified the method to bring reason description because now we have created dictionary that maps
                # individual pack with its respective reason
                pack_status_list.append({"pack_id": item, "status": pack_status,
                                         'created_by': user_id,
                                         'reason': reason_dict[item].get("reason", None) if reason_dict else None})

            # create record for pack status tracker
            logger.info("In set_status_pack_details, pack_status_list: {}".format(pack_status_list))

            PackStatusTracker.db_track_status(pack_status_list)

            if pack_status == settings.DELETED_PACK_STATUS:
                ext_pack_ids, ext_pack_display_ids, ext_data = ExtPackDetails.db_get_ext_packs_on_hold(pack_ids=
                                                                                                       pack_ids)
                if ext_pack_ids:
                    logger.debug("Update ExtPackDetails pack_usage_status_id if ext_status is Hold.")
                    update_status = update_ext_pack_data(hold_to_delete_pack_ids=ext_pack_ids,
                                                         pack_display_id_status_dict=pack_display_id_status_dict)
                    logger.debug("Update Status: {}".format(update_status))

                    logger.debug("Add the packs in Couch DB if the notification/message already exists or create"
                                 "new notification.")
                    logger.debug("Old Template ID: {}, New Template ID: {}".format(ext_data["old_template_id"],
                                                                                   ext_data["new_template_id"]))
                    if ext_data["old_template_id"]:
                        logger.debug("Find the CouchDB Notifications to update the new Template Details...")
                        couchdb_status, notification_found = \
                            update_notifications_couch_db_status(old_pharmacy_fill_id=[],
                                                                 company_id=ext_data["company_id"],
                                                                 file_id=0, old_template_id=ext_data["old_template_id"],
                                                                 new_template_id=ext_data["new_template_id"],
                                                                 autoprocess_template_flag=True,
                                                                 new_pack_ids=ext_pack_display_ids, remove_action=False)
                        logger.info("update_notifications_couch_db_status --> CouchDB Status: {}, "
                                    "Notification Found: {}".format(couchdb_status, notification_found))
                        if not notification_found:
                            for pack_display_id, pack_status_from_dict in pack_display_id_status_dict.items():
                                if pack_status_from_dict["pack_status"] in settings.PACK_PROGRESS_DONE_STATUS_LIST + \
                                        [settings.MANUAL_PACK_STATUS]:
                                    logger.debug("Pack Display ID: {}, with Pack Status: {} should be deleted".
                                                 format(pack_display_id, pack_status_from_dict["pack_status"]))
                                else:
                                    logger.debug("Remove the Pack Display ID from ext_pack_display_ids..")
                                    ext_pack_display_ids = list(set(ext_pack_display_ids) - set([pack_display_id]))

                            if ext_pack_display_ids:
                                message = constants.NOTIFICATION_EXT_CHANGE_RX_GENERAL

                                update_couch_db_notifications_change_rx_delete(pack_display_ids=ext_pack_display_ids,
                                                                               ext_data=ext_data, user_id=user_id,
                                                                               message=message, flow_document="dp",
                                                                               change_rx_token=change_rx_token)

            if pack_status in settings.FILLED_PACK_STATUS:
                logger.debug("Update ExtPackDetails pack_usage_status_id to Done if any entry exists with Pack Usage "
                             "Status as Pending.")

                for pack in pack_ids:
                    ext_pack_ids = ExtPackDetails.db_get_ext_packs_with_pack_usage_pending(pack=pack)
                    if ext_pack_ids:
                        update_pack_usage_ids = update_pack_usage_ids + ext_pack_ids

                if update_pack_usage_ids:
                    update_status = update_ext_pack_usage_status(pack_ids=update_pack_usage_ids, new_pack_ids=pack_ids)
                    logger.debug("Update Status: {}".format(update_status))

            # check if this is last pending pack, if yes mark whole batch done
            # PackDetails.db_handle_batch_end(pack_ids)
        return create_response(status)
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return error(1004)
    except InternalError as ex:
        logger.error(ex, exc_info=True)
        return error(1004)
    except PharmacySoftwareResponseException as e:
        logger.error(e, exc_info=True)
        return error(7001)


@retry(3)
def update_couch_db_notifications_change_rx_delete(pack_display_ids, ext_data, user_id, message, flow_document,
                                                   change_rx_token):
    user_lastname_firstname: str = ""
    args_info: Dict[str, Any] = {}
    try:
        logger.info("pack_display_ids: {}, ext_data: {}, user_id: {}, message: {}, flow_document: {}, "
                    "change_rx_token: {}".format(pack_display_ids, ext_data, user_id, message, flow_document,
                                                 change_rx_token))
        args_info = {"token": change_rx_token}
        user_info = get_users_by_ids(str(user_id), args_info)
        if user_info and "id" in user_info:
            user_lastname_firstname = user_info["last_name"] + ", " + user_info["first_name"]

        more_info = {"pack_ids": pack_display_ids, "ips_username": "",
                     "change_rx": True, "old_template_id": ext_data["old_template_id"],
                     "mvs_only": True, "user_full_name": user_lastname_firstname}
        if ext_data["new_template_id"]:
            more_info.update({"new_template_id": ext_data["new_template_id"],
                              "autoprocess_template": ext_data["autoprocess_template"]})

        Notifications(user_id=user_id, token=change_rx_token, call_from_client=True).\
            send_with_username(user_id=0, message=message, flow=flow_document, more_info=more_info,
                               add_current_user=False)
        return True, True
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("update_couch_db_notifications_change_rx_delete: Issue with CouchDB Document update.")
        logger.error(e, exc_info=True)
        return False, False


@log_args_and_response
def db_get_drug_info_old_template_packs(pack_ids: List[int]):
    slot_fndc_drug_dict: Dict[str, int] = {}
    try:
        drug_query = PackDetails.select(SlotDetails.drug_id, DrugMaster.formatted_ndc.alias("fndc"),
                                        DrugMaster.txr).dicts()\
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)\
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id)\
            .where(PackDetails.id << pack_ids)\
            .group_by(SlotDetails.drug_id)

        logger.debug("Old Template Drug Query: {}".format(drug_query))
        for drug in drug_query:
            if drug["fndc"] and drug["txr"]:
                slot_fndc_drug_dict[concatenate_fndc_txr_dao(drug["fndc"], drug["txr"])] = drug["drug_id"]

        return slot_fndc_drug_dict

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_drug_info_new_template(patient_id: int, file_id: int):
    slot_fndc_drug_dict: Dict[str, int] = {}
    try:
        drug_query = TempSlotInfo.select(DrugMaster.formatted_ndc.alias("fndc"), DrugMaster.txr.alias("txr"),
                                         PatientRx.drug_id.alias("drug_id")).dicts() \
            .join(PatientRx, on=TempSlotInfo.patient_rx_id == PatientRx.id)\
            .join(DrugMaster, on=PatientRx.drug_id == DrugMaster.id)\
            .where(TempSlotInfo.patient_id == patient_id, TempSlotInfo.file_id == file_id)\
            .group_by(DrugMaster.id)

        logger.debug("New Template Drug Query: {}".format(drug_query))
        for drug in drug_query:
            if drug["fndc"] and drug["txr"]:
                slot_fndc_drug_dict[concatenate_fndc_txr_dao(drug["fndc"], drug["txr"])] = drug["drug_id"]

        return slot_fndc_drug_dict
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_slot_details_drug_with_old_packs(update_drug_dict: Dict[int, int], ext_change_rx_data, user_id):
    update_slot_drug_status: int = 0
    daw_check_dict: Dict[int, int] = {}
    daw_no_check_dict: Dict[int, int] = {}
    new_pack_list: List[int] = []
    new_drug_list: List[int] = []
    pack_drug_tracker_details: List[Dict[str, Any]] = []

    try:
        if update_drug_dict:
            logger.debug("Update Drug in Slot Details. Drug Mapping shows New Drug in key and Old Drug in value for "
                         "dictionary. Update the Slot Details with Old Drug: {}".format(update_drug_dict))

            for new_drug_id, old_drug_dict in update_drug_dict.items():
                if old_drug_dict[constants.CHECK_DAW_KEY]:
                    daw_check_dict[new_drug_id] = old_drug_dict[constants.DRUG_ID_KEY]
                else:
                    daw_no_check_dict[new_drug_id] = old_drug_dict[constants.DRUG_ID_KEY]

            logger.debug("Update Drug Dict with DAW Check = True. Final Dict: {}".format(daw_check_dict))
            logger.debug("Update Drug Dict with DAW Check = False. Final Dict: {}".format(daw_no_check_dict))

            logger.debug("Find the packs for new Template to adjust the drugs..")
            new_pack_query = db_get_new_pack_details_for_template(template_id=ext_change_rx_data["new_template"])
            new_pack_list = [pack["id"] for pack in new_pack_query]
            new_drug_list = list(daw_check_dict.keys())

            logger.debug("New Packs List: {}".format(new_pack_list))
            logger.debug("New Drugs List: {}".format(new_drug_list))

            if daw_no_check_dict:
                logger.debug("Update Drugs where DAW check is not required...")
                update_slot_drug_status = \
                    db_update_drug_based_on_slot_info(daw_dict=daw_no_check_dict, new_pack_list=new_pack_list,
                                                      new_drug_list=new_drug_list, daw_check=False)
            if daw_check_dict:
                logger.debug("Update Drugs where DAW check is required...")
                update_slot_drug_status = \
                    db_update_drug_based_on_slot_info(daw_dict=daw_check_dict, new_pack_list=new_pack_list,
                                                      new_drug_list=new_drug_list, daw_check=True)

            logger.debug("Get Slot Information for the packs where Drugs mismatch is found between Original and "
                         "New Drugs.")
            new_pack_list = []
            pack_query = db_get_new_pack_details_for_template(template_id=ext_change_rx_data["new_template"])
            new_pack_list = [pack["id"] for pack in pack_query]

            slot_query = SlotDetails.select(SlotDetails.id, SlotDetails.drug_id,
                                            SlotDetails.original_drug_id, PackRxLink.pack_id).dicts()\
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .where(PackRxLink.pack_id << new_pack_list, PatientRx.daw_code == 0,
                       SlotDetails.drug_id != SlotDetails.original_drug_id)

            for record in slot_query:
                pack_drug_tracker_info = {"slot_details_id": record["id"],
                                          "previous_drug_id": record["original_drug_id"],
                                          "updated_drug_id": record["drug_id"],
                                          "module": constants.PDT_CHANGE_RX_FLOW,
                                          "created_by": user_id,
                                          "created_date": get_current_date_time()}

                pack_drug_tracker_details.append(pack_drug_tracker_info)

            if pack_drug_tracker_details:
                logger.debug("Pack Drug Tracker Details: {}".format(pack_drug_tracker_details))
                insert_status = PackDrugTracker.db_insert_pack_drug_tracker_data(pack_drug_tracker_details)
                logger.debug("Pack Drug Tracker Details Insert Status: {}".format(insert_status))

        return update_slot_drug_status
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_drug_based_on_slot_info(daw_dict, new_pack_list, new_drug_list, daw_check):
    final_slot_id_list: List[int] = []
    clauses = list()
    old_drug_ids: List[int] = []
    new_drug_ids: List[int] = []
    slot_id_list: List[int] = []
    update_slot_drug_status: int = 0
    try:
        if daw_check:
            logger.debug("Find the slots where DAW=0 and new drug is used.")
            query = SlotDetails.select(SlotDetails.drug_id,
                                       fn.GROUP_CONCAT(Clause(fn.DISTINCT(SlotDetails.id))).coerce(False)
                                       .alias("slot_id_list")).dicts() \
                .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .where(PatientRx.daw_code == 0, PackRxLink.pack_id << new_pack_list,
                       SlotDetails.drug_id << new_drug_list) \
                .group_by(SlotDetails.drug_id)
        else:
            query = SlotDetails.select(SlotDetails.drug_id,
                                       fn.GROUP_CONCAT(Clause(fn.DISTINCT(SlotDetails.id))).coerce(False)
                                       .alias("slot_id_list")).dicts() \
                .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .where(PackRxLink.pack_id << new_pack_list, SlotDetails.drug_id << new_drug_list) \
                .group_by(SlotDetails.drug_id)

        for drug_slot in query:
            if drug_slot["slot_id_list"] is not None:
                slot_id_list = list(map(lambda x: int(x), drug_slot["slot_id_list"].split(',')))
                final_slot_id_list = final_slot_id_list + slot_id_list

        if final_slot_id_list:
            for new_drug_id, old_drug_id in daw_dict.items():
                old_drug_ids.append(old_drug_id)
                new_drug_ids.append(new_drug_id)

            clauses.append(SlotDetails.drug_id << new_drug_ids)
            clauses.append(SlotDetails.id << final_slot_id_list)

            new_seq_tuple = list(tuple(zip(map(str, new_drug_ids), old_drug_ids)))
            drug_case_sequence = case(SlotDetails.drug_id, new_seq_tuple)
            update_slot_drug_status = \
                SlotDetails.db_update_drug_details_by_old_drug(drug_case_sequence, clauses)

        return update_slot_drug_status
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_pack_ids_by_batch_id(batch_id: int, company_id: int) -> list:
    """
    This function get packs ids by batch id
    @param company_id:
    @param batch_id:
    @return:
    """
    try:
        pack_ids = PackDetails.db_get_pack_ids_by_batch_id(batch_id=batch_id, company_id=company_id)
        return pack_ids

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_pack_ids_by_batch_id {}".format(e))
        logger.error(e, exc_info=True)
        raise e


def db_verify_packlist_by_company(company_id, pack_list):
    """
    Function to validate pack list for given company_id and system_id
    @param company_id: int
    @param pack_list: list
    @return: status
    """
    try:
        valid_pack_list = PackDetails.db_verify_packlist(pack_list, company_id)
        if not valid_pack_list:
            return False

        return True
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pack_ids_by_batch_id {}".format(e))
        raise e


def db_max_order_no_dao(system_id):
    try:
        _max_order_no = PackDetails.db_max_order_no(system_id)
        return _max_order_no

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pack_ids_by_batch_id {}".format(e))
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def update_facility_distribution_id(company_id, pack_list):
    """
    Function to get list of facility distribution id's from the given pack list
    and update status of respective id in db
    """

    try:
        if len(pack_list) > 0:
            facility_ids = PackDetails.db_get_facility_distribution_ids(pack_list)
            if len(facility_ids) > 1:
                return False, "update_facility_distribution_id: Multiple facility ids found", None
            response = FacilityDistributionMaster.db_update_facility_distribution_status(company_id, list(facility_ids))
            return True, response, facility_ids.pop()
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return False, str(e), None
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def get_ordered_pack_list(pack_list):
    """
    This function returns ordered pack list for assigning order_no.
    Sorting logic is based on scheduled_delivery_date
    @param pack_list:list
    @return:sorted_pack_list
    """
    try:
        sorted_pack_list = []
        query = PackDetails.select(PackDetails.id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .where(PackDetails.id.in_(pack_list)) \
            .order_by(PackHeader.scheduled_delivery_date, PatientMaster.id)

        for record in query.dicts():
            sorted_pack_list.append(record["id"])
        return sorted_pack_list
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def update_schedule_id_null_dao(pack_list, facility_distribution_id, update=False):
    try:
        status = PackDetails.update_schedule_id_null(pack_list, facility_distribution_id, update)
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pack_ids_by_batch_id {}".format(e))
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def update_schedule_id_dao(pack_list, facility_dis_id):
    try:
        status = PackDetails.update_schedule_id(pack_list=pack_list, facility_distribution_id=facility_dis_id)
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pack_ids_by_batch_id {}".format(e))
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def db_set_pack_status_dao(pack_ids):
    try:

        PackDetails.update(pack_status=settings.MANUAL_PACK_STATUS, system_id=5).where(
            PackDetails.id << pack_ids['pack_list']).execute()

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def get_no_of_drugs_dao(pack_id):
    try:
        response = PackRxLink.get_no_of_drugs(pack_id)
        if response is None:
            return error(1004)
        return response
    except InternalError:
        return error(2001)


@log_args_and_response
def get_slots_to_update_pack_wise(pack_ids, old_drug):
    try:
        query = SlotDetails.select(
            SlotDetails.id,
            SlotDetails.drug_id,
            PackRxLink.pack_id).dicts() \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .where((PackRxLink.pack_id << pack_ids),
                   (SlotDetails.drug_id == old_drug))

        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_packs_to_update_drug_mff(user_id):
    pack_id_list: list = list()
    try:
        query = PackDetails.select(PackDetails.id).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .where(
            (PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                         settings.FILLED_PARTIALLY_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT]), (
                    PackUserMap.assigned_to == user_id))

        for record in query:
            pack_id_list.append(record['id'])
        return pack_id_list
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_slots_to_update_mfs(batch_id, user_id, old_drug, mfs_device_id):
    """
        returns query to get the slot info for the specified ndc to update drug for that use
        @param batch_id:
        @param user_id:
        @param mfs_device_id:
        @param old_drug:
        """
    try:
        analysis_id_query = MfdAnalysis.select(SlotDetails.id, SlotDetails.drug_id,
                                               PackRxLink.pack_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(SlotDetails.drug_id == old_drug,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.assigned_to == user_id,
                   # MfdAnalysisDetails.status_id == constants.MFD_DRUG_PENDING_STATUS,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_PENDING_STATUS,
                                             constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                             constants.MFD_CANISTER_SKIPPED_STATUS],
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   SlotTransaction.id.is_null(True),
                   MfdAnalysis.mfs_device_id == mfs_device_id)
        return analysis_id_query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_slot_details_by_slot_id_dao(update_dict: dict, slot_details_id: int) -> bool:
    """
    This function to update slot details by slot id
    @param update_dict:
    @param slot_details_id:
    @return:

    """
    try:
        status = SlotDetails.db_update_slot_details_by_slot_id(update_dict=update_dict,
                                                               slot_details_id=slot_details_id)
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_slot_details_by_slot_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_manual_pack_ids(assigned_user_id: int, company_id: int, pack_ids: int) -> list:
    """
       This function used to get manual pack ids
       @param assigned_user_id:
       @param company_id:
       @param pack_ids:
       @return:

    """
    try:
        clauses: list = list()
        clauses.append((PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                                    settings.FILLED_PARTIALLY_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT]))
        clauses.append((PackDetails.company_id == company_id))

        if assigned_user_id:
            clauses.append((PackUserMap.assigned_to == assigned_user_id))
        if pack_ids:
            clauses.append((PackUserMap.pack_id << pack_ids))

        pack_id_list = PackDetails.select(PackDetails.id).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .where(functools.reduce(operator.and_, clauses))

        pack_ids = list(item['id'] for item in list(pack_id_list))
        return pack_ids
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_manual_pack_ids {}".format(e))
        raise e


@log_args_and_response
def get_slot_data_by_pack_ids_drug_ids(original_drug_ids: list, pack_ids: list):
    """
          This function used to slot data by pack ids and drug ids
          @param pack_ids:
          @param original_drug_ids:
          @return:

    """
    try:

        slot_query = SlotDetails.select(SlotDetails.id,
                                        SlotDetails.drug_id,
                                        PackRxLink.pack_id,
                                        ).dicts() \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(PackRxLink.pack_id << pack_ids,
                   PatientRx.daw_code == 0,
                   SlotDetails.drug_id << original_drug_ids)
        return slot_query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_slot_data_by_pack_ids_drug_ids {}".format(e))
        raise e


@log_args_and_response
def get_pending_progress_pack_count(system_id: int, status_list: list, device_id: int, batch_id: int = None):
    """

    @param system_id:
    @param batch_id:
    @param status_list:
    @param device_id:
    @return:
    """
    logger.debug("Inside get_pending_progress_pack_count")
    try:
        if batch_id:
            pack_id_query = PackDetails.select(PackDetails,
                                               PackDetails.id.alias('pack_id')).dicts() \
                .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(PackDetails.batch_id == batch_id,
                       PackDetails.pack_status << status_list,
                       PackAnalysisDetails.device_id == device_id) \
                .group_by(PackDetails.id)
        else:
            pack_id_query = PackDetails.select(PackDetails,
                                               PackDetails.id.alias('pack_id')).dicts() \
                .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(PackQueue, on=PackQueue.pack_id==PackDetails.id)\
                      .where(PackDetails.pack_status << status_list,
                             PackAnalysisDetails.device_id == device_id) \
                      .group_by(PackDetails.id)
        pack_ids = [record['pack_id'] for record in pack_id_query]
        return pack_ids

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_incomplete_packs_for_given_time_and_status(start_date, end_date, _pack_status, system_id):
    all_incomplete_packs = []
    logger.debug("Inside get_incomplete_packs_for_given_time_and_status")
    try:
        for record in PackDetails.select(PackDetails.id).dicts().where(
                PackDetails.system_id == system_id,
                PackDetails.created_date.between(start_date, end_date),
                PackDetails.pack_status == _pack_status):
            all_incomplete_packs.append(record["id"])

        return all_incomplete_packs

    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError


@log_args_and_response
def verify_pack_id(pack_id, company_id):
    """ Returns True if pack id is generated for given company_id, False otherwise

    :param pack_id:
    :param company_id:
    :return: Boolean
    """
    logger.debug("Inside verify_pack_id")
    pack_id = int(pack_id)
    company_id = int(company_id)

    try:
        pack = PackDetails.get(id=pack_id)
        if company_id == pack.company_id:
            return True
        return False

    except DoesNotExist:
        return False
    except InternalError as e:
        logger.error("Error in verify_pack_id: {}").format(e)
        return False


def is_print_requested(pack_id):
    """
    Returns True if print request present in print_queue table, False otherwise.
    :param int pack_id: Pack ID
    :return: bool
    """
    logger.debug("Inside is_print_requested")
    try:
        PrintQueue.get(pack_id=pack_id)
        return True
    except DoesNotExist:
        return False
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_max_batch_id(pack_id):
    logger.debug("Inside db_get_max_batch_id")
    try:
        record = PackAnalysis.select() \
            .where(PackAnalysis.pack_id == pack_id) \
            .order_by(PackAnalysis.batch_id.desc()).get()

        return record.batch_id_id

    except DoesNotExist:
        raise
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_zone_by_device_id(device_id, company_id):
    """
    To get the device details from device_id (Foreign Key of DeviceMaster).
    @param device_id:
    @param company_id:
    :return:
    """
    logger.debug("Inside get_zone_by_device_id")

    try:
        query = DeviceLayoutDetails.select(DeviceLayoutDetails,
                                           DeviceLayoutDetails.zone_id,
                                           DeviceMaster.device_type_id,
                                           DeviceMaster.serial_number,
                                           DeviceMaster.name,
                                           DeviceMaster.company_id).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(DeviceLayoutDetails.device_id == device_id,
                   DeviceMaster.company_id == company_id).get()
        property_name_value = 'drawer_initials_pattern'
        query[property_name_value] = None

        return query

    except (IntegrityError, InternalError, DataError) as e:
        raise e
    except Exception as e :
        logger.error("Error in get_zone_by_device_id: {}".format(e))


@log_args_and_response
def get_csr_canister_by_fndc_txr(company_id, fndc, txr, zone_id):

    # logger.debug("Inside get_csr_canister_by_fndc_txr")

    try:
        query = CanisterMaster.select(CanisterMaster.rfid,
                                      CanisterMaster.id.alias('canister_id'),
                                      fn.GROUP_CONCAT(Clause(
                                          fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                          fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                          'zone_name'),
                                      DeviceMaster.system_id,
                                      DeviceMaster.name,
                                      LocationMaster.display_location,
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      LocationMaster.device_id.alias('device_id'),
                                      LocationMaster.location_number,
                                      LocationMaster.is_disabled.alias('is_location_disabled')
                                      ).dicts() \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .where(DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR'],
                   DrugMaster.formatted_ndc == fndc,
                   DrugMaster.txr == txr,
                   DeviceLayoutDetails.zone_id == zone_id,
                   CanisterMaster.company_id == company_id,
                   DeviceMaster.company_id == company_id) \
            .group_by(CanisterMaster.id).order_by(CanisterMaster.available_quantity.desc()).get()

        return query
    except (InternalError, InternalError) as e:
        logger.info(e)
        return None
    except DoesNotExist as e:
        logger.info(e)
        return None


@log_args_and_response
def get_empty_location_by_quadrant(device_id: int, quadrant: int, company_id: int, drawer_type: list,
                                   exclude_location: list) -> dict:
    """
    :param device_id:
    :param quadrant:
    :param company_id:
    :param exclude_location:
    :param drawer_type:
    :return:
    """
    logger.debug("In function get_empty_location_by_quadrant")
    data = {}
    try:
        query = LocationMaster.select(ContainerMaster.device_id,
                                      ContainerMaster.id.alias("container_id"),
                                      LocationMaster.id.alias("location_id"),
                                      LocationMaster.location_number,
                                      LocationMaster.display_location,
                                      LocationMaster.quadrant).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.quadrant == quadrant,
                   ContainerMaster.device_id == device_id,
                   LocationMaster.is_disabled == False,
                   CanisterMaster.id.is_null(True),
                   DeviceMaster.company_id == company_id)\
            .order_by(ContainerMaster.drawer_level)
        if exclude_location:
            query = query.where(LocationMaster.id.not_in(exclude_location))
        if drawer_type:
            query = query.where(ContainerMaster.drawer_type << drawer_type)

        query = query.limit(1)
        for record in query:
            data = {
                'location_id': record['location_id'],
                'display_location': record['display_location'],
                'location_number': record['location_number']
            }
        return data
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_empty_location_by_quadrant: {}".format(e))
        raise e


@log_args_and_response
def get_mfd_trolley_for_pack(pack_id: int) -> dict:
    """
    returns trolley seq and batch_id of a pack
    :param pack_id: int
    :return: dict
    """
    logger.debug("Inside get_mfd_trolley_for_pack")
    try:
        query = MfdAnalysis.select(MfdAnalysis.trolley_seq,
                                   MfdAnalysis.batch_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .where(PackRxLink.pack_id == pack_id,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                             constants.MFD_CANISTER_VERIFIED_STATUS,
                                             constants.MFD_CANISTER_PENDING_STATUS,
                                             constants.MFD_CANISTER_IN_PROGRESS_STATUS],
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_FILLED_STATUS,
                                                    constants.MFD_DRUG_PENDING_STATUS]) \
            .group_by(MfdAnalysis.trolley_seq)

        trolley_data = dict()
        for record in query:
            trolley_data = {'trolley_seq': record['trolley_seq'],
                            'batch_id': record['batch_id']}
        return trolley_data

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in get_mfd_trolley_for_pack: {}".format(e))


@log_args_and_response
def get_trolley_analysis_ids_by_trolley_seq(batch_id: int, trolley_seq: int) -> tuple:
    """
    returns analysis_ids for given trolley seq
    :param batch_id: int
    :param trolley_seq: int
    :return: list
    """
    mfs_system_mapping = dict()
    dest_devices = set()
    DeviceMasterAlias = DeviceMaster.alias()
    batch_system = None
    logger.debug("Inside get_trolley_analysis_ids_by_trolley_seq")

    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   DeviceMaster.id.alias('trolley_id'),
                                   DeviceMaster.name.alias('trolley_name'),
                                   DeviceMasterAlias.system_id.alias('mfs_system_id'),
                                   BatchMaster.system_id,
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == MfdAnalysis.mfs_device_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.trolley_seq == trolley_seq,
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_DROPPED_STATUS,
                                                 constants.MFD_CANISTER_SKIPPED_STATUS,
                                                 constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                 constants.MFD_CANISTER_RTS_DONE_STATUS])) \
            .order_by(MfdAnalysis.order_no)

        logger.debug("In get_trolley_analysis_ids_by_trolley_seq, query: {}".format(list(query)))

        analysis_id_list = list()

        for record in query:
            mfs_system_mapping[record['mfs_device_id']] = record['mfs_system_id']
            dest_devices.add(record['dest_device_id'])
            analysis_id_list.append(record['mfd_analysis_id'])
            batch_system = record['system_id']

        return analysis_id_list, mfs_system_mapping, list(dest_devices), batch_system

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_trolley_analysis_ids_by_trolley_seq: {}".format(e))


@log_args_and_response
def check_transfer_filling_pending(mfd_analysis_ids=None, pack_id=None, device_id=None):
    """
    gets valid analysis details ids for canister update
    :param mfd_analysis_ids: list
    :param pack_id: int
    :param device_id: int
    :return: tuple
    """
    logger.debug("Inside check_transfer_filling_pending")

    filling_done = True
    transfer_done = True
    trolley_data = dict()
    clauses = list()

    if mfd_analysis_ids:
        clauses.append((MfdAnalysis.id << mfd_analysis_ids))

    if pack_id:
        clauses.append((PackDetails.id == pack_id))

    clauses.append((MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_SKIPPED_STATUS,
                                                  constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                  constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                  constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                  constants.MFD_CANISTER_MVS_FILLING_REQUIRED])))
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        query = MfdAnalysis.select(MfdAnalysis.status_id,
                                   MfdAnalysis.transferred_location_id,
                                   MfdAnalysis.trolley_location_id,
                                   MfdAnalysis.assigned_to,
                                   MfdAnalysis.dest_device_id,
                                   LocationMaster.device_id,
                                   MfdAnalysis.mfd_canister_id,
                                   MfdAnalysis.dest_quadrant,
                                   MfdAnalysis.trolley_seq,
                                   LocationMaster.quadrant,
                                   DeviceMaster.device_type_id,
                                   PackRxLink.pack_id,
                                   DeviceMasterAlias.id.alias('cart_id'),
                                   DeviceMasterAlias.name.alias('cart_name'),
                                   LocationMaster.id.alias('current_location'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(MfdAnalysis.id) \
            .order_by(MfdAnalysis.status_id)
        for record in query:
            if not trolley_data:
                trolley_data = {
                    'cart_id': record['cart_id'],
                    'cart_name': record['cart_name'],
                    'to_be_filled_by': record['assigned_to'],
                    'trolley_seq': record['trolley_seq']
                }
            logger.debug('checking_mfd_canister_status_for_pack_id: {} canister_id {} can_status: {}'
                         ' transferred_loc_id: {} and current_location: {}'.format(record['pack_id'],
                                                                                   record['mfd_canister_id'],
                                                                                   record['status_id'],
                                                                                   record['transferred_location_id'],
                                                                                   record['current_location']))
            if record['status_id'] in [constants.MFD_CANISTER_PENDING_STATUS, constants.MFD_CANISTER_IN_PROGRESS_STATUS] \
                    or record['device_type_id'] == settings.DEVICE_TYPES['Manual Filling Device']:
                filling_done = False
                transfer_done = False
                break
            if record['transferred_location_id'] is None:
                if device_id:
                    if record['dest_device_id'] == device_id:
                        transfer_done = False
                else:
                    transfer_done = False

        logger.info(
            'In check_transfer_filling_pending, mfd_status_returned_values: filling_done: {} transfer_done: {}'.format(
                filling_done, transfer_done))

        return filling_done, transfer_done, trolley_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("error in check_transfer_filling_pending: {}".format(e))


@log_args_and_response
def db_get_mfd_slot_info(pack_id, device_id, company_id, original_drop_data, error_canisters):
    """
    returns drop data, mfd_slot data and missing canister data for a given pack
    :param pack_id:
    :param device_id:
    :param company_id:
    :param original_drop_data:
    :param missing_canisters:
    :return:
    """
    logger.debug("In db_get_mfd_slot_info")
    mfd_slot_data = dict()
    mfd_drop_data = dict()
    CodeMasterAlias = CodeMaster.alias()
    drop_data = dict(original_drop_data)
    slot_header_set = set()
    location_id_set = set()

    missing_mfd_canister = dict()

    LocationMasterAlias = LocationMaster.alias()
    LocationMasterAlias2 = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    DeviceMasterAlias2 = DeviceMaster.alias()
    MfdCanisterTransferHistoryAlias = MfdCanisterTransferHistory.alias()

    sub_query = MfdCanisterTransferHistory.select(fn.MAX(MfdCanisterTransferHistory.id)
                                                  .alias('max_canister_history_id'),
                                                  MfdCanisterTransferHistory.mfd_canister_id
                                                  .alias('mfd_canister_id')) \
        .where(MfdCanisterTransferHistory.previous_location_id.is_null(False)) \
        .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query')

    # locations = LocationMaster.select(LocationMaster.id.alias('loc_id')).dicts()\
    #     .where(LocationMaster.device_id == device_id)
    # robot_locations = list()
    # for record in locations:
    #     robot_locations.append(record['loc_id'])
    # sub_query_2 = MfdCanisterTransferHistoryAlias.select(fn.MAX(MfdCanisterTransferHistoryAlias.id)
    #                                                      .alias('max_canister_history_id'),
    #                                                      MfdCanisterTransferHistoryAlias.mfd_canister_id
    #                                                      .alias('mfd_canister_id')) \
    #     .where(MfdCanisterTransferHistoryAlias.current_location_id << robot_locations) \
    #     .group_by(MfdCanisterTransferHistoryAlias.mfd_canister_id).alias('sub_query_2')

    mfd_drop_data = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))

    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   DeviceMasterAlias2.name.alias('dest_device_name'),
                                   MfdAnalysis,
                                   SlotDetails.id.alias('slot_id'),
                                   SlotHeader.id.alias('slot_header_id'),
                                   DrugMaster,
                                   SlotHeader.hoa_date, SlotHeader.hoa_time,
                                   ContainerMaster.drawer_name.alias("drawer_number"),
                                   LocationMaster.location_number,
                                   LocationMaster.display_location,
                                   LocationMaster.device_id,
                                   LocationMaster.quadrant,
                                   DeviceMaster.name.alias('current_device_name'),
                                   DeviceMaster.device_type_id,
                                   PackGrid.slot_row,
                                   PackGrid.slot_column,
                                   PatientRx.pharmacy_rx_no,
                                   MfdCanisterMaster,
                                   MfdCanisterMaster.id.alias('canister_id'),
                                   CodeMaster.value.alias('can_status'),
                                   CodeMasterAlias.value.alias('drug_status'),
                                   DrugMaster.id.alias('drug_id'),
                                   DrugDimension.length.alias("dd_length"),
                                   DrugDimension.width.alias("dd_width"),
                                   DrugDimension.depth.alias("dd_depth"),
                                   DrugDimension.fillet.alias("dd_fillet"),
                                   CustomDrugShape.name.alias("dd_shape"),
                                   MfdAnalysisDetails,
                                   LocationMasterAlias2.id.alias('missing_location_id'),
                                   LocationMasterAlias2.display_location.alias('missing_display_location'),
                                   LocationMaster.is_disabled.alias('location_disabled'),
                                   MfdAnalysisDetails.id.alias('mfd_analysis_details_id'),
                                   MfdCanisterTransferHistory.created_date.alias('last_seen_time'),
                                   DeviceMasterAlias.name.alias('previous_device_name'),
                                   LocationMasterAlias.id.alias('previous_location_id'),
                                   LocationMasterAlias.display_location.alias('previous_display_location'),
                                   MfdAnalysisDetails.mfd_can_slot_no,
                                   fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr).alias('txr'),
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(DeviceMasterAlias2, on=MfdAnalysis.dest_device_id == DeviceMasterAlias2.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(CodeMasterAlias, on=MfdAnalysisDetails.status_id == CodeMasterAlias.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(sub_query, JOIN_LEFT_OUTER, on=sub_query.c.mfd_canister_id == MfdCanisterMaster.id) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias.id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias.device_id == DeviceMasterAlias.id)) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=(MfdAnalysis.transferred_location_id == LocationMasterAlias2.id)) \
            .where(PackDetails.id == pack_id,
                   MfdAnalysisDetails.status_id == constants.MFD_DRUG_FILLED_STATUS,
                   MfdAnalysis.status_id << constants.MFD_CANISTER_DONE_LIST,
                   MfdAnalysis.dest_device_id == device_id,
                   PackDetails.company_id == company_id) \
            .order_by(MfdAnalysisDetails.mfd_can_slot_no)

        for record in query:

            logger.info("In db_get_mfd_slot_info, record: {}".format(record))

            slot_header_set.add(record['slot_header_id'])
            # todo: check location_number condition
            if record.get('drop_number', None) \
                    and record.get('canister_id', None):
                if record['dest_device_id'] != record['device_id'] or \
                        record['dest_quadrant'] != record['quadrant'] or \
                        record['location_disabled']:
                    logger.debug('adding_mfd_missing_data {}'.format(record))
                    missing_mfd_canister[record["missing_display_location"]] = {
                        "analysis_id": record['mfd_analysis_id'],
                        "canister_id": record["canister_id"],
                        "missing_location_id": record["missing_location_id"],
                        "rfid": record["rfid"],
                        "dest_device_name": record["dest_device_name"],
                        "dest_display_location": record["missing_display_location"],
                        "new_display_location": record["missing_display_location"],
                        "current_display_location": record["display_location"],
                        "current_device_id": record["device_id"],
                        "current_location_number": record["location_number"],
                        "current_quadrant": record["quadrant"],
                        "current_device_name": record["current_device_name"],
                        "current_device_type_id": record["device_type_id"],
                        'previous_device_name': record['previous_device_name'],
                        'previous_location_id': record['previous_location_id'],
                        'previous_display_location': record['previous_display_location'],
                        'last_seen_time': record['last_seen_time'],
                        'can_status': record.get('can_status', None),
                        'location_disabled': record['location_disabled'],
                        'missing_canister': True
                    }
                location = map_pack_location_dao(slot_row=record["slot_row"], slot_column=record["slot_column"])

                location_id_set.add(location)

                if not record['canister_id'] in mfd_slot_data:
                    mfd_slot_data[record['canister_id']] = {"canister_id": record["canister_id"],
                                                            "rfid": record["rfid"],
                                                            "quadrant": record["dest_quadrant"],
                                                            "location_number": record["location_number"],
                                                            "device_id": record["dest_device_id"],
                                                            "display_location": record["display_location"],
                                                            "drawer_number": record["drawer_number"],
                                                            "mfd_analysis_id": record["mfd_analysis_id"],
                                                            "mfd_slot_details": {}}

                fndc_txr = {
                    '{}{}{}'.format(record["formatted_ndc"], settings.FNDC_TXR_SEPARATOR, record['txr']): {
                        "hoa_date": record['hoa_date'],
                        "hoa_time": record['hoa_time'],
                        "slot_row": record['slot_row'],
                        "slot_column": record['slot_column'],
                        "quantity": record['quantity'],
                        "is_manual": 1,
                        "slot_id": record['slot_id'],
                        "slot_header_id": record['slot_header_id'],
                        "pharmacy_rx_no": record["pharmacy_rx_no"],
                        "drug_id": record['drug_id'],
                        "drug_name": record['drug_name'],
                        "ndc": record['ndc'],
                        "txr": record['txr'],
                        "strength_value": record['strength_value'],
                        "strength": record['strength'],
                        "color": record['color'],
                        "formatted_ndc": record["formatted_ndc"],
                        "shape": record["shape"],
                        "image_name": record["image_name"],
                        "imprint": record["imprint"],
                        "dd_length": record["dd_length"],
                        "dd_width": record["dd_width"],
                        "dd_depth": record["dd_depth"],
                        "dd_fillet": record["dd_fillet"],
                        "dd_shape": record["dd_shape"],
                        "mfd_analysis_details_id": record["mfd_analysis_details_id"]
                    }
                }
                if record['mfd_can_slot_no'] not in mfd_slot_data[record['canister_id']]['mfd_slot_details']:
                    mfd_slot_data[record['canister_id']]['mfd_slot_details'][record['mfd_can_slot_no']] = fndc_txr

                else:
                    mfd_slot_data[record['canister_id']]['mfd_slot_details'][record['mfd_can_slot_no']].update(
                        fndc_txr)

                if drop_data.get(record['drop_number'], None):
                    if record['config_id'] in drop_data[record['drop_number']]:
                        if location in drop_data[record['drop_number']][record['config_id']]:
                            if 'mfd_canister_data' in drop_data[record['drop_number']][record['config_id']][location]:
                                if record['canister_id'] in \
                                        drop_data[record['drop_number']][record['config_id']][location][
                                            'mfd_canister_data']:
                                    # this is added in the end for not writing repetitive code
                                    pass
                                else:
                                    drop_data[record['drop_number']][record['config_id']][location][
                                        'mfd_canister_data'][record['canister_id']] = list()
                            else:
                                drop_data[record['drop_number']][record['config_id']][location]['mfd_canister_data'] = {
                                    record['canister_id']: list()}
                        else:
                            drop_data[record['drop_number']][record['config_id']][location] = {
                                'mfd_canister_data': {record['canister_id']: list()}}
                    else:
                        drop_data[record['drop_number']][record['config_id']] = {
                            location: {'mfd_canister_data': {record['canister_id']: list()}}}
                else:
                    drop_data[record['drop_number']] = {
                        record['config_id']: {location: {'mfd_canister_data': {record['canister_id']: list()}}}}
                if str(record['mfd_can_slot_no']) not in drop_data[record['drop_number']][record['config_id']][location] \
                        ['mfd_canister_data'][record['canister_id']]:
                    drop_data[record['drop_number']][record['config_id']][location]['mfd_canister_data'][
                        record['canister_id']].append(str(record['mfd_can_slot_no']))

        # removing transfer from disable location as we won't detect canister placed at empty location
        # if missing_mfd_canister:
        #     exclude_location = list()
        #     for display_location, record in missing_mfd_canister.items():
        #         if record['location_disabled']:
        #             transfer_data = get_transfer_data(record['current_device_id'],
        #                                               record['current_display_location'],
        #                                               record['canister_id'],
        #                                               record['missing_location_id'],
        #                                               exclude_location)
        #             if transfer_data:
        #                 exclude_location.append(transfer_data['new_loc_id'])
        #                 missing_mfd_canister[display_location].update(transfer_data)
        error_canisters.update(missing_mfd_canister)
        logger.info("In db_get_mfd_slot_info, Response mfd_slot_data {}, mfd_dop_data {}, error_canisters {}".format(
            mfd_slot_data,
            drop_data,
            error_canisters))

        return {'mfd_slot_data': mfd_slot_data, 'mfd_dop_data': drop_data, 'error_canisters': error_canisters}

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in db_get_mfd_slot_info: {}".format(e))
        raise e


@log_args_and_response
def db_get_mfd_analysis_info_old_packs(pack_ids):
    mfd_analysis_ids: List[int] = []
    mfd_analysis_detail_ids: List[int] = []
    try:
        mfd_query = MfdAnalysisDetails.select(MfdAnalysis.id.alias("mfd_analysis_id"),
                                              MfdAnalysisDetails.id.alias("mfd_analysis_details_id")).dicts()\
            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)\
            .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id)\
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id)\
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id)\
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
            .where(PackRxLink.pack_id << pack_ids)\
            .group_by(MfdAnalysis.id, MfdAnalysisDetails.id)

        for mfd_info in mfd_query:
            if mfd_info["mfd_analysis_id"] not in mfd_analysis_ids:
                mfd_analysis_ids.append(mfd_info["mfd_analysis_id"])
            if mfd_info["mfd_analysis_details_id"] not in mfd_analysis_detail_ids:
                mfd_analysis_detail_ids.append(mfd_info["mfd_analysis_details_id"])

        return mfd_analysis_ids, mfd_analysis_detail_ids
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        logger.error("Function: db_get_mfd_analysis_info_old_packs -- {}".format(e))
        return [], []
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        logger.error("Function: db_get_mfd_analysis_info_old_packs -- {}".format(e))
        raise e


@log_args_and_response
def get_sharing_packs(pack_ids, forced_pack_manual=False, status_changed_from_ips=False):
    """
    returns extra pending packs that shares the same canister with given packs and requires rts
    :param pack_ids: list
    :param forced_pack_manual: bool
    :param status_changed_from_ips: bool
    :return:
    """
    logger.debug("Inside get_sharing_packs")

    affected_mfd_analysis_ids = set()
    affected_mfd_analysis_details_ids = set()
    affected_canister = set()
    pack_canister_dict = dict()
    canister_status = set()
    canister_filled = False
    input_pack = list()
    affected_packs = set()

    pack_clause = PackDetails.pack_status << [settings.PENDING_PACK_STATUS]

    if forced_pack_manual or status_changed_from_ips:
        pack_clause = ((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) | (PackDetails.id << pack_ids))
    try:
        # Fetches patient-wise mfd information for given packs
        base_canister_query = MfdAnalysis.select(PatientRx.patient_id,
                                                 fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id))
                                                 .alias('patient_packs').coerce(False),
                                                 PackHeader.id.alias("pack_header_id"),
                                                 fn.MIN(PackDetails.order_no).alias('min_order_no')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .where(PackRxLink.pack_id << pack_ids,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                             constants.MFD_CANISTER_PENDING_STATUS,
                                             constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                             constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                             constants.MFD_CANISTER_VERIFIED_STATUS],
                   pack_clause) \
            .group_by(PatientRx.patient_id)

        logger.info(
            f"In get_sharing_packs, base_canister_query: {list(base_canister_query)}"
        )

        for base_record in base_canister_query:
            patient_header_id = [base_record['pack_header_id']]

            """ finds the other pending mfd packs of the patient for given batch and whose dropping is after the given 
                packs.
            """
            query = PackHeader.select(MfdAnalysis.id.alias("mfd_analysis_ids"),
                                      MfdAnalysis.status_id.alias("canister_status"),
                                      fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.id)).alias(
                                          "mfd_analysis_details_ids"),
                                      fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).alias("pack_list")).dicts() \
                .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
                .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
                .where(PackHeader.id << patient_header_id,
                       PackDetails.order_no >= base_record['min_order_no'],
                       MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                                 constants.MFD_CANISTER_PENDING_STATUS,
                                                 constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                 constants.MFD_CANISTER_VERIFIED_STATUS],
                       pack_clause) \
                .group_by(MfdAnalysis.id)
            logger.info(f"In get_sharing_packs, query: {list(query)}")

            for record in query:
                mfd_analysis_ids = {record['mfd_analysis_ids']}
                pack_list = list(map(lambda x: int(x), record['pack_list'].split(',')))
                mfd_analysis_details_ids = set(map(lambda x: int(x), record['mfd_analysis_details_ids'].split(',')))
                canister_status.add(record['canister_status'])
                for packs in pack_list:
                    if packs in pack_ids:
                        affected_packs.update([packs])
                        affected_mfd_analysis_ids.update(mfd_analysis_ids)
                        affected_mfd_analysis_details_ids.update(mfd_analysis_details_ids)
                    if packs in pack_canister_dict:
                        pack_canister_dict[packs]["mfd_analysis_ids"].update(mfd_analysis_ids)
                        pack_canister_dict[packs]["mfd_analysis_details_ids"].update(mfd_analysis_details_ids)
                        pack_canister_dict[packs]["canister_status"].update(canister_status)
                    else:
                        pack_canister_dict.update({keys: {"mfd_analysis_ids": mfd_analysis_ids,
                                                          "mfd_analysis_details_ids": mfd_analysis_details_ids,
                                                          "canister_status": canister_status}
                                                   for keys in (pack_list)})

                if len(pack_list) > 1:
                    input_pack.append(tuple(pack_list))

            response_linked_packs = get_shared_canister(pack_ids, input_pack)
            affected_packs.update(response_linked_packs)
            for pack_id in affected_packs:
                affected_mfd_analysis_ids.update(pack_canister_dict[pack_id]['mfd_analysis_ids'])
                affected_mfd_analysis_details_ids.update(pack_canister_dict[pack_id]["mfd_analysis_details_ids"])
                affected_canister.update(pack_canister_dict[pack_id]["canister_status"])

        if affected_canister.intersection(
                (
                        constants.MFD_CANISTER_FILLED_STATUS,
                        constants.MFD_CANISTER_VERIFIED_STATUS,
                        constants.MFD_CANISTER_MVS_FILLING_REQUIRED
                        # constants.MFD_CANISTER_IN_PROGRESS_STATUS
                )
        ):
            canister_filled = True

        return affected_packs, affected_mfd_analysis_ids, affected_mfd_analysis_details_ids, canister_filled
    except (InternalError, IntegrityError) as e:
        raise e


@log_args_and_response
def get_shared_canister(delete_pack, pack_list):
    provided_pack = {*delete_pack}
    linked_packs = set()
    for canister_packs in pack_list:  # list of tuple of packs sharing same canister.
        for pack in canister_packs:  # Each pack in tuple
            if pack in provided_pack:  # if any of the pack in tuple is in provided_pack then add all the
                # packs to provided_packs and linked_packs as they need to be deleted
                provided_pack.update(set(canister_packs))
                linked_packs.update(set(canister_packs))
                break

    return get_shared_canister(list(linked_packs), pack_list) if len(delete_pack) != len(linked_packs) else linked_packs



# @log_args_and_response
# def get_sharing_packs(pack_ids, forced_pack_manual=False, status_changed_from_ips=False):
#     """
#     returns extra pending packs that shares the same canister with given packs and requires rts
#     :param pack_ids: list
#     :param forced_pack_manual: bool
#     :param status_changed_from_ips: bool
#     :return:
#     """
#     logger.debug("Inside get_sharing_packs")
#
#     PatientRxAlias = PatientRx.alias()
#     PackRxLinkAlias = PackRxLink.alias()
#     SlotDetailsAlias = SlotDetails.alias()
#     MfdAnalysisAlias = MfdAnalysis.alias()
#     MfdAnalysisDetailsAlias = MfdAnalysisDetails.alias()
#
#     pack_canister_dict = dict()
#     affected_mfd_analysis_ids = set()
#     affected_mfd_analysis_details_ids = set()
#     affected_pack_ids = list()
#     canister_filled = False
#     pack_clause = PackDetails.pack_status << [settings.PENDING_PACK_STATUS]
#
#     if forced_pack_manual or status_changed_from_ips:
#         pack_clause = ((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) | (PackDetails.id << pack_ids))
#
#     try:
#         # Fetches patient-wise mfd information for given packs
#         base_canister_query = MfdAnalysis.select(PatientRx.patient_id,
#                                                  fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id))
#                                                  .alias('patient_packs').coerce(False),
#                                                  fn.MIN(PackDetails.order_no).alias('min_order_no')).dicts() \
#             .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
#             .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
#             .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
#             .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
#             .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
#             .where(PackRxLink.pack_id << pack_ids,
#                    MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
#                                              constants.MFD_CANISTER_PENDING_STATUS,
#                                              constants.MFD_CANISTER_IN_PROGRESS_STATUS,
#                                              constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
#                                              constants.MFD_CANISTER_VERIFIED_STATUS],
#                    pack_clause) \
#             .group_by(PatientRx.patient_id)
#
#         logger.info("In get_sharing_packs, base_canister_query: {}".format(list(base_canister_query)))
#
#         for base_record in base_canister_query:
#             patient_affected_mfd_analysis_ids = list()
#             patient_affected_mfd_analysis_details_ids = list()
#             patient_affected_pack_ids = list()
#             patient_packs = list(map(lambda x: int(x), base_record['patient_packs'].split(',')))
#
#             """ finds the other pending mfd packs of the patient for given batch and whose dropping is after the given
#                 packs.
#             """
#             query = MfdAnalysis.select(PackRxLinkAlias.pack_id,
#                                        fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisAlias.status_id))
#                                        .alias('canister_status').coerce(False),
#                                        fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisAlias.id)).alias('mfd_analysis_ids'),
#                                        fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetailsAlias.id))
#                                        .alias('mfd_analysis_details_ids')).dicts() \
#                 .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
#                 .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
#                 .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
#                 .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
#                 .join(PatientRxAlias, on=PatientRxAlias.patient_id == PatientRx.patient_id) \
#                 .join(PackRxLinkAlias, on=PatientRxAlias.id == PackRxLinkAlias.patient_rx_id) \
#                 .join(PackDetails, on=PackDetails.id == PackRxLinkAlias.pack_id) \
#                 .join(SlotDetailsAlias, on=SlotDetailsAlias.pack_rx_id == PackRxLinkAlias.id) \
#                 .join(MfdAnalysisDetailsAlias, on=SlotDetailsAlias.id == MfdAnalysisDetailsAlias.slot_id) \
#                 .join(MfdAnalysisAlias, on=((MfdAnalysisAlias.id == MfdAnalysisDetailsAlias.analysis_id) &
#                                             (MfdAnalysis.batch_id == MfdAnalysisAlias.batch_id))) \
#                 .where(PackRxLink.pack_id << patient_packs,
#                        PatientRx.patient_id == base_record['patient_id'],
#                        PackDetails.order_no >= base_record['min_order_no'],
#                        MfdAnalysisAlias.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
#                                                       constants.MFD_CANISTER_PENDING_STATUS,
#                                                       constants.MFD_CANISTER_IN_PROGRESS_STATUS,
#                                                       constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
#                                                       constants.MFD_CANISTER_VERIFIED_STATUS],
#                        MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
#                                                  constants.MFD_CANISTER_PENDING_STATUS,
#                                                  constants.MFD_CANISTER_IN_PROGRESS_STATUS,
#                                                  constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
#                                                  constants.MFD_CANISTER_VERIFIED_STATUS],
#                        pack_clause) \
#                 .group_by(PackRxLinkAlias.pack_id)
#
#             logger.info("In get_sharing_packs, query: {}".format(list(query)))
#
#             for record in query:
#                 mfd_analysis_ids = list(map(lambda x: int(x), record['mfd_analysis_ids'].split(',')))
#                 mfd_analysis_details_ids = list(map(lambda x: int(x), record['mfd_analysis_details_ids'].split(',')))
#                 canister_status = set(map(lambda x: int(x), record['canister_status'].split(',')))
#                 pack_canister_dict[record['pack_id']] = {'mfd_analysis_ids': mfd_analysis_ids,
#                                                          'mfd_analysis_details_ids': mfd_analysis_details_ids,
#                                                          'canister_status': canister_status}
#                 if record['pack_id'] in pack_ids:
#                     patient_affected_mfd_analysis_ids.extend(mfd_analysis_ids)
#                     patient_affected_mfd_analysis_details_ids.extend(mfd_analysis_details_ids)
#                     patient_affected_pack_ids.append(record['pack_id'])
#                     if not canister_filled and canister_status.intersection((constants.MFD_CANISTER_FILLED_STATUS,
#                                                                              constants.MFD_CANISTER_VERIFIED_STATUS,
#                                                                              constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
#                                                                              constants.MFD_CANISTER_IN_PROGRESS_STATUS)):
#                         canister_filled = True
#
#                 print('base_canister_ids:', affected_mfd_analysis_ids)
#
#                 patient_affected_pack_ids, patient_affected_mfd_analysis_ids, patient_affected_mfd_analysis_details_ids, \
#                 canister_filled = find_packs_sharing_mfd_canisters(pack_canister_dict,
#                                                                    patient_affected_pack_ids,
#                                                                    patient_affected_mfd_analysis_ids,
#                                                                    patient_affected_mfd_analysis_details_ids,
#                                                                    canister_filled,
#                                                                    forced_pack_manual)
#                 affected_pack_ids.extend(patient_affected_pack_ids)
#                 affected_mfd_analysis_ids.update(patient_affected_mfd_analysis_ids)
#                 affected_mfd_analysis_details_ids.update(patient_affected_mfd_analysis_details_ids)
#         return affected_pack_ids, affected_mfd_analysis_ids, affected_mfd_analysis_details_ids, canister_filled
#     except (InternalError, IntegrityError) as e:
#         raise e


@log_args_and_response
def find_filled_partially_packs(pack_ids, fill_time, user_id):
    """
    This function finds is used to find that given packs are filled partially or not
    If any packs are filled partially then we return it as response
    @param pack_ids:
    @return: filled_partially_packs
    """

    try:
        filled_partially_packs: list = list()

        # query to check whether the given packs are partially filled or not
        select_fields = [DrugTracker.is_overwrite,
                         DrugTracker.drug_id,
                         SlotDetails.drug_id,
                         PackGrid.slot_number,
                         PackDetails.id.alias("pack_id"),
                         PackDetails.pack_status
                         ]

        query = SlotDetails.select(*select_fields).dicts() \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id)\
            .where((PackDetails.id << pack_ids) &
                   ((DrugTracker.is_overwrite.is_null(True)) | (DrugTracker.is_overwrite == 0)))\
            .order_by(PackDetails.id, PackGrid.slot_number)

        for record in query:
            if record["is_overwrite"] == 0:
                if record["pack_id"] not in filled_partially_packs:
                    filled_partially_packs.append(record["pack_id"])

        logger.info("In find_filled_partially_packs: filled_partially_packs: {}".format(filled_partially_packs))

        # if we find the packs which are partially filled then update the status of those packs
        if filled_partially_packs:
            update_dict = {"pack_status": settings.FILLED_PARTIALLY_STATUS,
                           "modified_date": get_current_date_time(),
                           "fill_time": fill_time
                           }
            pack_details_status = PackDetails.update(**update_dict) \
                .where(PackDetails.id << filled_partially_packs)\
                .execute()

            logger.info("In find_filled_partially_packs: pack_details_status: {}".format(pack_details_status))

            if pack_details_status:

                pack_status_tracker_list: list = list()

                for pack_id in filled_partially_packs:

                    pack_status_tracker_list.append({"pack_id": pack_id,
                                                     "status": settings.FILLED_PARTIALLY_STATUS,
                                                     "created_by": user_id
                                                     }
                                                    )

                pack_status_tracker = PackStatusTracker.db_track_status(pack_status_tracker_list)

                logger.info("In find_filled_partially_packs: pack_status_tracker: {}".format(pack_status_tracker))

        return filled_partially_packs

    except Exception as e:
        logger.error("Error in find_filled_partially_packs: {}".format(e))
        raise e


@log_args_and_response
def check_mfd_canister_on_mfs_station_or_not(pack_ids):
    """
    this function returns the pack_ids for those mfd_canister are still present on the MFS station
    """
    try:
        pack_data: dict = dict()
        new_pack_ids: dict = dict()
        mfd_analysis_ids: list = list()
        mfd_analysis_details_ids: list = list()

        select_fields = [MfdAnalysis.id.alias("mfd_analysis_id"),
                         fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.id)).alias("mfd_analysis_details_id").coerce(False),
                         MfdAnalysis.status_id.alias("mfd_canister_status"),
                         TempMfdFilling.transfer_done,
                         PackDetails.pack_display_id,
                         PackDetails.id.alias("pack_id")
                         ]

        # query to check whether the data is available in temp_mfd_filling model
        query = MfdAnalysis.select(*select_fields).dicts()\
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id)\
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)\
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(TempMfdFilling, JOIN_LEFT_OUTER, on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id) \
            .where(PackDetails.id << pack_ids)\
            .group_by(MfdAnalysis.id)\
            .order_by(PackDetails.id)

        for record in query:
            if record["pack_id"] not in pack_data:
                pack_data[record["pack_id"]] = dict()
                pack_data[record["pack_id"]]["pack_display_id"] = record["pack_display_id"]
                pack_data[record["pack_id"]]["mfd_analysis_id"] = list()
                pack_data[record["pack_id"]]["mfd_analysis_details_id"] = list()
                pack_data[record["pack_id"]]["transfer_done_with_none"] = list()
                pack_data[record["pack_id"]]["transfer_done_with_zero"] = list()
                pack_data[record["pack_id"]]["transfer_done_with_one"] = list()

            print(record["transfer_done"])
            pack_data[record["pack_id"]]["mfd_analysis_id"].append(record["mfd_analysis_id"])
            pack_data[record["pack_id"]]["mfd_analysis_details_id"].extend(list(map(int, record["mfd_analysis_details_id"].split(','))))

            if record["transfer_done"] is None:
                pack_data[record["pack_id"]]["transfer_done_with_none"].append(record["mfd_canister_status"])

            if record["transfer_done"] == 1:
                pack_data[record["pack_id"]]["transfer_done_with_one"].append(record["mfd_canister_status"])

            if record["transfer_done"] == 0:
                pack_data[record["pack_id"]]["transfer_done_with_zero"].append(record["mfd_canister_status"])

        for pack_id, pack_info in pack_data.items():

            if not pack_info["transfer_done_with_zero"]:
                if pack_info["transfer_done_with_one"] and constants.MFD_CANISTER_IN_PROGRESS_STATUS not in pack_info["transfer_done_with_one"]:
                    if constants.MFD_CANISTER_IN_PROGRESS_STATUS in pack_info["transfer_done_with_none"]:
                        new_pack_ids[pack_id] = pack_info["pack_display_id"]
                        mfd_analysis_ids.extend(pack_info["mfd_analysis_id"])
                        mfd_analysis_details_ids.extend(pack_info["mfd_analysis_details_id"])
            else:
                new_pack_ids[pack_id] = pack_info["pack_display_id"]
                mfd_analysis_ids.extend(pack_info["mfd_analysis_id"])
                mfd_analysis_details_ids.extend(pack_info["mfd_analysis_details_id"])

        return new_pack_ids, mfd_analysis_ids, mfd_analysis_details_ids

    except Exception as e:
        logger.error("Error in check_mfd_canister_on_mfs_station_or_not: {}".format(e))
        raise e


@log_args_and_response
def find_packs_sharing_mfd_canisters(pack_canister_dict, affected_pack_ids, affected_mfd_analysis_ids,
                                     affected_mfd_analysis_details_ids, canister_filled, forced_pack_manual):
    """
    if any new pack is added that shares the mfd then this function is called in recursion to find packs that shares mfd
    :param pack_canister_dict: dict
    :param affected_pack_ids: list
    :param affected_mfd_analysis_ids: list
    :param affected_mfd_analysis_details_ids: list
    :param canister_filled: boolean
    :return:
    """
    logger.debug("Inside find_packs_sharing_mfd_canisters")

    recursion_required = False
    for pack_id, mfd_data in pack_canister_dict.items():
        if pack_id not in affected_pack_ids:
            print(pack_id, set(mfd_data['mfd_analysis_ids']).intersection(set(affected_mfd_analysis_ids)))
            if set(mfd_data['mfd_analysis_ids']).intersection(set(affected_mfd_analysis_ids)):
                recursion_required = True
                affected_pack_ids.append(pack_id)
                affected_mfd_analysis_ids.extend(mfd_data['mfd_analysis_ids'])
                affected_mfd_analysis_details_ids.extend(mfd_data['mfd_analysis_details_ids'])
                canister_status = mfd_data['canister_status']
                if not canister_filled and canister_status.intersection((constants.MFD_CANISTER_FILLED_STATUS,
                                                                         constants.MFD_CANISTER_VERIFIED_STATUS,
                                                                         constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                                         constants.MFD_CANISTER_IN_PROGRESS_STATUS)):
                    canister_filled = True

    if not recursion_required:
        return affected_pack_ids, affected_mfd_analysis_ids, affected_mfd_analysis_details_ids, canister_filled
    else:
        affected_pack_ids, affected_mfd_analysis_ids, affected_mfd_analysis_details_ids, canister_filled = \
            find_packs_sharing_mfd_canisters(pack_canister_dict, affected_pack_ids, affected_mfd_analysis_ids,
                                             affected_mfd_analysis_details_ids, canister_filled, forced_pack_manual)
        return affected_pack_ids, affected_mfd_analysis_ids, affected_mfd_analysis_details_ids, canister_filled


@log_args_and_response
def track_consumed_packs(pack_ids, company_id):
    """ Reduces consumed pack quantity from consumable tracker and updates consumable used
    """
    logger.info("in_track_consumed_packs : pack ids: " + str(pack_ids) + " company_id " + str(company_id))
    consumed_data = dict()
    try:
        consumed_data[settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE] = len(set(pack_ids))
        ConsumableTracker.db_remove_consumed_items(consumed_data, company_id)
        current_date = get_current_date()
        used_data = dict()
        used_data["used_quantity"] = len(set(pack_ids))
        ConsumableUsed.db_update_or_create(company_id, settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE, current_date,
                                           used_data)
    except Exception as e:
        logger.error("Error in track_consumed_packs: {}".format(e))


@log_args_and_response
def db_get_pack_display_ids(pack_ids):
    pack_display_ids = []
    logger.debug("Inside db_get_pack_display_ids")
    try:
        for record in PackDetails.select(
                PackDetails.pack_display_id).dicts().where(PackDetails.id << pack_ids):
            pack_display_ids.append(str(record["pack_display_id"]))
        return pack_display_ids
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist(ex)
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError(e)
    except Exception as e:
        logger.error("Error in db_get_pack_display_ids: {}".format(e))
        raise e


@log_args_and_response
def db_update_pack_details_by_template_dao(update_pack_dict, pack_list, update_pack_order_dict):
    update_other_packs: bool = False
    update_pack_list: List[int] = []
    pack_difference: int = 0
    success_count: int = 0
    failure_count: int = 0
    try:
        if pack_list:
            update_flag = PackDetails.db_update_pack_details_by_pack_list(update_pack_dict=update_pack_dict,
                                                                          pack_ids=pack_list)
            if update_pack_order_dict:
                update_status_response = PackDetails.\
                    db_update_pack_order_no(
                    {'pack_ids': ','.join(list(map(str, pack_list))),
                     'order_nos': ','.join(list(map(str, update_pack_order_dict["pack_orders"]))),
                     'system_id': update_pack_order_dict["system_id"]})
                logger.debug("Update Status Response: {}".format(update_status_response))

                update_other_packs = update_pack_order_dict.get("update_other_packs_order_no", False)
                update_pack_list = update_pack_order_dict.get("update_pack_list", [])
                pack_difference = update_pack_order_dict.get("pack_difference", 0)
                if update_other_packs:
                    if update_pack_list and pack_difference > 0:
                        pack_data = PackDetails.db_get_pack_data(update_pack_list)
                        logger.debug("Pack Data Query: {}".format(pack_data))

                        for pack in pack_data:
                            final_order_no = pack["order_no"] + pack_difference
                            update_other_packs_status = PackDetails.update(order_no=final_order_no)\
                                .where(PackDetails.id == pack["id"]).execute()

                            logger.debug("Pack ID: {}, Update Status: {}".format(pack["id"], update_other_packs_status))
                            if update_other_packs_status:
                                success_count += 1
                            else:
                                failure_count += 1

                        logger.debug("Final Count -- Success = {} and Failure = {}"
                                     .format(success_count, failure_count))
            return update_flag
        else:
            return 0
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_pack_list_by_order_number(order_no: int, batch_id: int):
    pack_list: List[int] = []
    try:
        pack_query = PackDetails.select(PackDetails.id.alias("pack_id")).dicts()\
            .where(PackDetails.order_no > order_no, PackDetails.batch_id == batch_id)

        for pack in pack_query:
            pack_list.append(pack["pack_id"])

        return pack_list
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def delete_pack_in_ips(pack_display_ids: List[str], filled_by: str, reason_list: List[str], company_id: int,
                       change_rx: bool = False):
    """
    Call an API from IPS-procedure-services to communicate data

    :param pack_display_ids: List of Pack Display IDs (will be used to delete appropriate packs in IPS)
    :param filled_by: IPS Username (will be used to update the user in IPS who deleted the packs)
    :param reason_list: The record dict where mapping is set among pack display ID and delete reason
    :param company_id: Details of company to fetch Company level constants.
    :param change_rx: Notification to IPS regarding delete pack call due to ChangeRx
    """
    try:
        ips_comm_settings = CompanySetting.db_get_ips_communication_settings(company_id)
        pack_display_ids = ','.join(pack_display_ids)
        reason_list = ','.join(reason_list)
        logger.info(pack_display_ids)

        # This will help to identify at IPS that delete call is due to ChangeRx flow
        status: str = "0"
        if change_rx:
            status = "1"

        response_data = send_data(
            ips_comm_settings['BASE_URL_IPS'],
            settings.PHARMACY_DELETE_PACK_SYNC,
            {
                "batchlist": pack_display_ids,
                "username": filled_by,
                "note": reason_list,
                'token': ips_comm_settings["IPS_COMM_TOKEN"],
                "status": status
            },
            0,
            token=ips_comm_settings["IPS_COMM_TOKEN"]
        )

        # During the flow of ChangeRx, we will get new pharmacy fill ID from IPS
        return response_data
    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def db_get_pack_and_display_ids(pack_ids: List[int]) -> Dict[int, int]:
    """

    """
    logger.debug("Inside db_get_pack_and_display_ids")
    try:
        pack_and_display_ids = dict()
        for record in PackDetails.select(PackDetails.id,
                                         PackDetails.pack_display_id).dicts().where(PackDetails.id << pack_ids):
            pack_and_display_ids[record["id"]] = record["pack_display_id"]
        return pack_and_display_ids

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist(ex)
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError(e)
    except Exception as e:
        logger.error("Error in db_get_pack_and_display_ids: {}".format(e))


@log_args_and_response
def get_pending_pack_details_and_patient_name_with_past_delivery_date(company_id, current_date):
    logger.debug("Inside get_pending_pack_details_and_patient_name_with_past_delivery_date")
    try:
        query = PackDetails.select(PackDetails.pack_display_id,
                                    PackDetails.consumption_start_date,
                                    PackDetails.consumption_end_date,
                                    PackHeader.scheduled_delivery_date,
                                    fn.Concat(PatientMaster.last_name, ', ',
                                              PatientMaster.first_name).alias("patient_name"),
                                    FacilityMaster.facility_name).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.company_id == company_id, PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                   PackHeader.scheduled_delivery_date < current_date) \
            .order_by(PackHeader.scheduled_delivery_date)

        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_pending_pack_details_and_patient_name_with_past_delivery_date: {}".format(e))
        raise e


@log_args_and_response
def get_manual_pack_details_and_patient_name_with_past_delivery_date(company_id, current_date):
    logger.debug("Inside get_manual_pack_details_and_patient_name_with_past_delivery_date")
    try:
        query = PackDetails.select(PackDetails.pack_display_id,
                                   PackDetails.consumption_start_date,
                                   PackDetails.consumption_end_date,
                                   PackHeader.scheduled_delivery_date,
                                   fn.IF(PackUserMap.assigned_to.is_null(True), 0, PackUserMap.assigned_to).alias(
                                       "assigned_to"),
                                   fn.Concat(PatientMaster.last_name, ', ',
                                             PatientMaster.first_name).alias("patient_name"),
                                   FacilityMaster.facility_name).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.company_id == company_id, PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                   PackHeader.scheduled_delivery_date < current_date) \
            .order_by(PackHeader.scheduled_delivery_date)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_manual_pack_details_and_patient_name_with_past_delivery_date: {}".format(e))
        raise e


@log_args_and_response
def get_packs_with_status_partially_filled_by_robot_for_given_pack_display_ids(user_id, pack_display_ids, company_id):
    logger.debug("Inside get_packs_with_status_partially_filled_by_robot_for_given_pack_display_ids")
    try:
        query = PackUserMap.select().dicts() \
            .join(PackDetails, on=PackDetails.id == PackUserMap.pack_id) \
            .where(PackUserMap.assigned_to == user_id,
                   PackDetails.pack_display_id << pack_display_ids,
                   PackDetails.pack_status == settings.PARTIALLY_FILLED_BY_ROBOT,
                   PackDetails.company_id == company_id)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(
            "Error in get_packs_with_status_partially_filled_by_robot_for_given_pack_display_ids: {}".format(e))
        raise e


@log_args_and_response
def get_pack_analysis_details_for_given_batch(batch_id):
    logger.debug("Inside get_pack_analysis_details_for_given_batch")

    try:

        # query = PackAnalysisDetails.select(PackDetails.id.alias("pack_id"),
        #                                    PackDetails.car_id,
        #                                    PackDetails.pack_status,
        #                                    (fn.COUNT(Clause(SQL('DISTINCT'),
        #                                                     fn.IF((PackAnalysisDetails.device_id.is_null(
        #                                                         True) | PackAnalysisDetails.canister_id.is_null(True)
        #                                                            | PackAnalysisDetails.location_number.is_null(True)),
        #                                                           True,
        #                                                           None)))).alias("is_manual"),
        #                                    ).dicts() \
        #     .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        #     .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
        #     .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
        #     .where((BatchMaster.id == batch_id),
        #            (PackDetails.pack_status << [settings.PACK_STATUS['Pending'], settings.PACK_STATUS['Progress']])) \
        #     .group_by(PackDetails.id)

        # Todo: need to check if condition
        query = PackAnalysisDetails.select(PackDetails.id.alias("pack_id"),
                                           PackDetails.car_id,
                                           PackDetails.pack_status,
                                           (fn.COUNT(Clause(SQL('DISTINCT'),
                                                            fn.IF((PackAnalysisDetails.status != constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED),
                                                                  True,
                                                                  None)))).alias("is_manual"),
                                           ).dicts() \
            .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .where((BatchMaster.id == batch_id),
                   (PackDetails.pack_status << [settings.PACK_STATUS['Pending'], settings.PACK_STATUS['Progress']])) \
            .group_by(PackDetails.id)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        return e
    except Exception as e:
        logger.error(f"Error in get_pack_analysis_details_for_given_batch: {e}")


@log_args_and_response
def get_mfd_automatic_packs(batch_id: int) -> list:
    """
    This function checks for the mfd packs which can be filled automatically
    """
    try:
        logger.debug("In get_mfd_automatic_packs")
        LocationMasterAlias = LocationMaster.alias()
        # Query to fetch the current as well as the dest location of the canisters
        mfd_canisters_in_robot = MfdAnalysis.select(MfdAnalysis.id,
                                                    MfdAnalysis.dest_quadrant,
                                                    MfdAnalysis.dest_device_id,
                                                    LocationMasterAlias.quadrant,
                                                    LocationMasterAlias.device_id,
                                                    PackDetails.id.alias("pack_id")).dicts() \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMasterAlias, on=MfdCanisterMaster.location_id == LocationMasterAlias.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where((MfdAnalysis.batch_id == batch_id),
                   (MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                              constants.MFD_CANISTER_DROPPED_STATUS]),
                   (PackDetails.pack_status == settings.PACK_STATUS["Pending"]))
        packs_list = []
        # get the pack_ids whose canisters are not in the robot
        for record in mfd_canisters_in_robot:
            if record["dest_quadrant"] != record["quadrant"] and record["dest_device_id"] != record["device_id"]:
                if record["pack_id"] not in packs_list:
                    packs_list.append(record["pack_id"])

        return packs_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_batch_packs(company_id, batch_id, status=None):
    """

    :param company_id:
    :param batch_id:
    :param status:
    :return:
    """
    logger.debug("Inside get_batch_packs")
    try:
        clauses = list()
        clauses.append((PackDetails.company_id == company_id))
        clauses.append((PackDetails.batch_id == batch_id))
        if status:
            clauses.append((PackDetails.pack_status << status))

        logger.info(f"In get_batch_packs, clauses: {clauses}")

        query = PackDetails.select().dicts().where(functools.reduce(operator.and_, clauses))

        pack_ids = [item['id'] for item in list(query)]

        return pack_ids

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def create_info_notification(msg, car_id=0, pack_id=0):
    return json.dumps({"status": "info", "msg": msg, "car_id": car_id, "pack_id": pack_id})


def create_crm_notification(pack_id, car_id, station_id, order, start_point, end_point, time_arrived, status, msg):
    return json.dumps(
        {"msg": msg, "pack_id": pack_id, "car_id": car_id, "id": station_id, "order": order, "start_point": start_point,
         "end_point": end_point, "time_arrived": time_arrived, "status": status})


def create_dashboard_notification(id, data, car_id=0, pack_id=0, printer_id=0):
    if printer_id > 0:
        data = json.dumps({"status": "dashboard", "data": data, "id": id, "car_id": car_id, "pack_id": pack_id,
                           "printer_id": printer_id})
    else:
        data = json.dumps({"status": "dashboard", "data": data, "id": id, "car_id": car_id, "pack_id": pack_id})
    return data


@log_args_and_response
def get_drug_data_for_unique_fndc_txr_for_non_manual_packs(pack_list):
    """
    get unique fndc,txr for non-manual packs of given pack list
    @param pack_list: list of pack_ids
    @return: list
    """
    try:
        canister_drug_query = PackAnalysis.select(fn.DISTINCT(fn.CONCAT(DrugMaster.formatted_ndc, ',',
                                                                        fn.IF(DrugMaster.txr.is_null(True), '',
                                                                              DrugMaster.txr)
                                                                        )).alias('canister_fndc_txr'),
                                                  DrugMaster
                                                  ) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(CanisterMaster, on=PackAnalysisDetails.canister_id == CanisterMaster.id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id).dicts() \
            .where(PackAnalysis.batch_id == PackDetails.batch_id,
                   PackAnalysis.pack_id << pack_list,
                   PackDetails.pack_status != settings.MANUAL_PACK_STATUS)

        logger.info(
            f"In get_drug_data_for_unique_fndc_txr_for_non_manual_packs, canister_drug_query: {list(canister_drug_query)}")

        return [item["canister_fndc_txr"] for item in list(canister_drug_query)]

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def add_variable_alternate_drug_available_in_drug_data(con_fndc_txr_list):
    try:
        alternate_drug_flag = {}
        DrugMasterAlias = DrugMaster.alias()

        alternate_drugs_count_query = DrugMaster.select(fn.COUNT(fn.DISTINCT(DrugMasterAlias.id))
                                                        .alias('alternate_drug_count'),
                                                        DrugMaster.concated_fndc_txr_field().alias('fndc_txr')).dicts() \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=(DrugMasterAlias.txr == DrugMaster.txr) &
                                                       (
                                                                   DrugMasterAlias.formatted_ndc != DrugMaster.formatted_ndc) &
                                                       (DrugMasterAlias.brand_flag == settings.GENERIC_FLAG) &
                                                       (DrugMaster.brand_flag == settings.GENERIC_FLAG)) \
            .where(DrugMaster.concated_fndc_txr_field() << con_fndc_txr_list)

        for record in alternate_drugs_count_query:
            alternate_drug_flag[record['fndc_txr']] = True if record['alternate_drug_count'] > 0 else False

        return alternate_drug_flag
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_packs_in_pack_user_map(user_list):
    try:
        logger.info(f"In update_packs_in_pack_user_map, user_list: {user_list}")

        if user_list:

            packs = PackUserMap.select(PackUserMap.pack_id).dicts() \
                .join(PackDetails, on=PackUserMap.pack_id == PackDetails.id) \
                .where(PackUserMap.assigned_to << user_list,
                       PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.FILLED_PARTIALLY_STATUS])

            pack_ids = [pack['pack_id'] for pack in packs]

            logger.info("In unassign_packs, unassign_packs" + str(pack_ids))

            if pack_ids:
                update_packs = PackUserMap.update(assigned_to=None, modified_date=get_current_date_time()) \
                    .where(PackUserMap.pack_id << pack_ids).execute()
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    return True


@log_args_and_response
def get_similar_packs_manual_assign_dao(pack_id, date_type, date_from, date_to, batch_distribution):
    similar_pack_ids = dict()
    pack_data = defaultdict(dict)
    pack_ids = list()
    pack_header_list = list()
    company_id = None
    select_field_dict = dict()
    manual_pack_detail_dict = dict()
    sub_q_pack_id = list()
    logger.debug("Inside get_similar_packs_manual_assign_dao")
    record_qty_map = {}
    given_pack_qty_map = {}
    try:

        try:
            pack_detail = PackDetails.select(PackUserMap.assigned_to, PackDetails) \
                    .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id)\
                .where(PackDetails.id << pack_id).dicts()

        except DoesNotExist as e:
            logger.debug(e, exc_info=True)
            return error(1014)

        logger.debug("In get_similar_packs_manual_assign_dao: pack_details: {}".format(pack_detail))

        for pack in pack_detail:
            if company_id is None:
                company_id = pack['company_id']
            if pack['pack_header_id'] not in pack_header_list:
                pack_header_list.append(pack['pack_header_id'])
            if not batch_distribution:
                manual_pack_detail_dict = {
                    'pack_id': pack['id'],
                    'pack_display_id': pack['pack_display_id'],
                    'assigned_to': pack['assigned_to'],
                    'pack_status': pack['pack_status']
                }

        pack_status_list = list()
        logger.debug("In get_similar_packs_manual_assign_dao: manual_pack_detail_dict: {}".format(manual_pack_detail_dict))

        if batch_distribution:
            pack_status_list.append(settings.PENDING_PACK_STATUS)
        else:
            # if manual_pack_detail_dict['pack_status'] == settings.FILLED_PARTIALLY_STATUS:
            #     pack_status_list.append(settings.FILLED_PARTIALLY_STATUS)
            # else:
            #     pack_status_list = [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS]
            pack_status_list = [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS, settings.FILLED_PARTIALLY_STATUS]

        if pack_detail:
            # logger.info(pack_detail.assigned_to)
            clauses = [PackDetails.pack_header_id << pack_header_list,
                       PackDetails.company_id == company_id,
                       PackDetails.pack_status << pack_status_list]

            if batch_distribution:
                clauses.append(PackDetails.batch_id.is_null(True))
            else:
                clauses.extend([PackUserMap.assigned_to == manual_pack_detail_dict['assigned_to'], PackUserMap.id.is_null(False)])

            if date_type == "admin_start_date":
                clauses.append((PackDetails.consumption_start_date.between(date_from, date_to)))
            elif date_type == "delivery_date":
                clauses.append((PackHeader.scheduled_delivery_date.between(date_from, date_to)))
            elif date_type == "created_date":
                clauses.append((PackDetails.created_date.between(date_from, date_to)))

            sub_q = PackDetails.select(PackDetails.id, PackDetails.pack_display_id, PatientMaster.id.alias('patient_id'),
                                       fn.Concat(PatientMaster.last_name, ', ', PatientMaster.first_name).alias('patient_name'),
                                       FacilityMaster.id.alias('facility_id'), FacilityMaster.facility_name,
                                       PackDetails.consumption_start_date, PackDetails.consumption_end_date,
                                       PackHeader.scheduled_delivery_date, PackHeader.id.alias('pack_header_id')).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
                .join(PatientMaster, JOIN_LEFT_OUTER, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, JOIN_LEFT_OUTER, on=FacilityMaster.id == PatientMaster.facility_id) \
                .where(*clauses)
            logger.debug("In get_similar_packs_manual_assign_dao: sub_q: {}".format(sub_q))

            if not batch_distribution:
                given_pack_qty_map = list(SlotHeader.select(SlotHeader.pack_grid_id, fn.GROUP_CONCAT(
                    fn.CONCAT(SlotDetails.drug_id, " ", SlotDetails.quantity))).dicts() \
                                          .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                                          .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
                                          .where(PackDetails.id << pack_id) \
                                          .group_by(SlotHeader.pack_grid_id, PackDetails.id))
            for pack in list(sub_q):
                if not batch_distribution:
                    record_qty_map = list(SlotHeader.select(SlotHeader.pack_grid_id, fn.GROUP_CONCAT(
                        fn.CONCAT(SlotDetails.drug_id, " ", SlotDetails.quantity))).dicts() \
                                          .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                                          .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
                                          .where(PackDetails.id == pack['id']) \
                                          .group_by(SlotHeader.pack_grid_id, PackDetails.id))
                if record_qty_map == given_pack_qty_map or batch_distribution:
                    formatted_consumption_start_date = datetime.datetime.strftime(pack['consumption_start_date'],
                                                                                  "%Y-%m-%d %H:%M:%S") + " +0000"
                    formatted_consumption_start_date = datetime.datetime.strptime(formatted_consumption_start_date,
                                                                                  "%Y-%m-%d %H:%M:%S %z")
                    formatted_consumption_start_date = formatted_consumption_start_date.astimezone(pytz.timezone('UTC'))
                    formatted_consumption_end_date = datetime.datetime.strftime(pack['consumption_end_date'],
                                                                                  "%Y-%m-%d %H:%M:%S") + " +0000"
                    formatted_consumption_end_date = datetime.datetime.strptime(formatted_consumption_end_date,
                                                                                  "%Y-%m-%d %H:%M:%S %z")
                    formatted_consumption_end_date = formatted_consumption_end_date.astimezone(pytz.timezone('UTC'))
                    select_field_dict[pack['id']] = {
                        'facility_id': pack['facility_id'],
                        'patient_id': pack['patient_id'],
                        'facility_name': pack['facility_name'],
                        'pack_id': pack['id'],
                        'pack_display_id': pack['pack_display_id'],
                        'patient_name': pack['patient_name'],
                        'consumption_start_date': pack['consumption_start_date'],
                        'consumption_end_date': pack['consumption_end_date'],
                        'formatted_consumption_start_date': formatted_consumption_start_date,
                        'formatted_consumption_end_date': formatted_consumption_end_date,
                        'scheduled_delivery_date': pack['scheduled_delivery_date'],
                        'pack_header_id': pack['pack_header_id'],
                        'partial_fill': []
                    }

                    if batch_distribution:
                        similar_pack_ids[pack['id']] = select_field_dict[pack['id']]
                    else:
                        sub_q_pack_id.append(pack['id'])
            if batch_distribution:
                return similar_pack_ids
            logger.debug("In get_similar_packs_manual_assign_dao: sub_q_pack_id: {}".format(sub_q_pack_id))

            if not sub_q_pack_id:
                response = list(similar_pack_ids.values())
                return response
            for record in PackRxLink.select(PackRxLink.pack_id,
                                            SlotDetails.drug_id,
                                            PackDetails.pack_display_id,
                                            fn.GROUP_CONCAT(SlotHeader.pack_grid_id).coerce(False).alias(
                                                'pack_grid_id')).dicts() \
                    .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                    .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                    .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
                    .where(PackRxLink.pack_id << sub_q_pack_id) \
                    .group_by(PackRxLink.id, SlotDetails.drug_id):
                pack_grid_ids = record['pack_grid_id'].split(',')
                pack_data[(record["pack_id"], record['pack_display_id'])] \
                    .update({record["drug_id"]: set(pack_grid_ids)})

            logger.debug("In get_similar_packs_manual_assign_dao: pack_data: {}".format(pack_data))

            from pprint import pprint
            pprint(pack_data)
            # changed to give same pack in list
            # If needed to remove same pack from the list of similar packs pop the data from the line below.
            reference_drug_ids = pack_data[(int(manual_pack_detail_dict['pack_id']), manual_pack_detail_dict['pack_display_id'])]
            for pack, drug_ids in pack_data.items():
                if drug_ids == reference_drug_ids:
                    similar_pack_ids[pack[0]] = select_field_dict[pack[0]]
                    pack_ids.append(pack[0])
            if pack_ids:
                logger.debug("In get_similar_packs_manual_assign_dao: pack_ids: {}".format(pack_ids))

                query = PackRxLink.select(PackRxLink.id.alias('pack_rx_id'),
                                          PartiallyFilledPack.missing_qty,
                                          PackRxLink.pack_id, SlotDetails.drug_id,
                                          PartiallyFilledPack.note).dicts() \
                    .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                    .join(PartiallyFilledPack, JOIN_LEFT_OUTER, on=PackRxLink.id == PartiallyFilledPack.pack_rx_id) \
                    .where(PackRxLink.pack_id << pack_ids) \
                    .group_by(PackRxLink.pack_id)
                for record in query:
                    similar_pack_ids[record['pack_id']]['partial_fill'].append({
                        'pack_rx_id': record['pack_rx_id'],
                        'missing_qty': record['missing_qty'],
                        'note': record['note'],
                        'drug_id': record['drug_id']
                    })

        return similar_pack_ids

    except(InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_similar_packs_manual_assign_dao: {e}")
        raise e


@log_args_and_response
def set_fill_time_dao(fill_time, pack_ids):
    update_count = 0
    logger.debug("Inside set_fill_time_dao")
    try:
        for index in range(0, len(pack_ids)):
            update_pack_details = PackDetails.update(fill_time=fill_time[index]) \
                .where(PackDetails.id == pack_ids[index]).execute()

            update_count += update_pack_details

        return update_count

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("Error in set_fill_time_dao: {e}")
        return e


@log_args_and_response
def partially_filled_pack_dao(userpacks):
    logger.debug("Inside partially_filled_pack_dao")

    with db.transaction():
        try:
            for userpack in userpacks:
                pack_id = userpack['pack_id']
                company_id = userpack['company_id']
                user_id = userpack['user_id']
                fill_time = int(userpack['fill_time'])
                valid_pack = verify_pack_id(pack_id, company_id)
                if not valid_pack:
                    return error(1026)
                drug_info = userpack['drug_info']
                for item in drug_info:
                    missing_qty = item['missing_qty']
                    pack_rx_id = item['pack_rx_id']
                    note = item.get('note', None)
                    modified_by = created_by = user_id
                    update_dict = {
                        'created_by': created_by,
                        'modified_by': modified_by,
                        'modified_date': get_current_date_time(),
                        'note': note,
                        'missing_qty': missing_qty
                    }
                    create_dict = {
                        'pack_rx_id': pack_rx_id
                    }

                    logger.info(f"In partially_filled_pack_dao; update_dict:{update_dict}, create_dict: {create_dict}")

                    PartiallyFilledPack.db_update_or_create(create_dict, update_dict)

                query = PackDetails.update(pack_status=settings.FILLED_PARTIALLY_STATUS,
                                           modified_date=get_current_date_time(),
                                           fill_time=fill_time) \
                    .where(PackDetails.id == pack_id).execute()

                Notifications().fill_partially(userpacks)

            return True
        except KeyError as e:
            logger.error(e, exc_info=True)
            return error(1020)
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            return error(2001)


@log_args_and_response
def max_order_no(system_id):

    order_no = 0
    logger.debug("Inside max_order_no")

    try:
        order_no = PackDetails.select(PackDetails.order_no) \
            .where(PackDetails.system_id == system_id) \
            .order_by(PackDetails.order_no.desc()) \
            .get().order_no

        return order_no

    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return order_no
    except InternalError as e:
        logger.error(e)
        return order_no
    except Exception as e:
        logger.error(f"Error in max_order_no: {e}")
        return e


@log_args_and_response
def generate_test_packs_dao(pack_quantity, child_packs_count, all_dates, date_count, user_id, company_id,
                            test_pack_data, times):
    pack_id_list = []
    slot_details_list = []
    pack_admin_date_dict = dict()
    try:
        with db.transaction():
            for pack in range(pack_quantity):
                pack_header_id = PackHeader.get().id
                day = 0
                for cpack in range(child_packs_count):
                    if cpack + 1 != child_packs_count:
                        consumption_end_date = all_dates[day + (settings.ONE_WEEK - 1)]
                    else:
                        consumption_end_date = all_dates[int(date_count - 1)]

                    pack_admin_date_dict = {"consumption_start_date": all_dates[day],
                                            "consumption_end_date": consumption_end_date,
                                            "dates": all_dates[day:day + settings.ONE_WEEK]}
                    day += settings.ONE_WEEK

                    pack_data = {"pack_header_id": pack_header_id,
                                 "batch_id": None, "pack_display_id": 1000, "pack_no": 1, "pack_status_id": 2,
                                 "filled_by": "test", "filled_days": 7, "fill_start_date": "2016-01-01",
                                 "delivery_schedule": "test",
                                 "order_no": 100, "created_by": user_id, "modified_by": user_id,
                                 "created_date": get_current_date(),
                                 "system_id": None, "company_id": company_id,
                                 "consumption_start_date": pack_admin_date_dict["consumption_start_date"],
                                 "consumption_end_date": pack_admin_date_dict["consumption_end_date"]}

                    status = BaseModel.db_create_record(pack_data, PackDetails, get_or_create=False)
                    pack_id = status.id

                    for i in range(len(pack_admin_date_dict["dates"])):
                        columns = sorted([int(i) for i in test_pack_data.keys()])
                        for column in columns:
                            slot = test_pack_data[str(column)]
                            pack_grid_id = get_pack_grid_id_dao(slot_row=i, slot_column=column)
                            slot_record = BaseModel.db_create_record(
                                {"pack_id": pack_id, "hoa_date": pack_admin_date_dict["dates"][i],
                                 "hoa_time": times[column],
                                 "pack_grid_id": pack_grid_id}, SlotHeader, get_or_create=False)

                            for rx in slot:
                                rx_record, created = BaseModel.db_create_record(
                                    {"patient_rx_id": rx["rx_id"], "pack_id": pack_id},
                                    PackRxLink, get_or_create=True)

                                slot_id = slot_record.id
                                slot_details_list.append(
                                    {"slot_id": slot_id, "pack_rx_id": rx_record.id, "quantity": rx["qty"],
                                     "is_manual": 0})
                    logger.debug("Dummy Pack ID: " + str(pack_id))
                    pack_id_list.append(pack_id)
            SlotDetails.db_create_multi_record(slot_details_list, SlotDetails)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    return pack_id_list


def get_pack_assigned_to(pack_list):
    try:

        query = PackDetails.select(PackDetails.id, PackUserMap.assigned_to.alias('assigned_from')).dicts() \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .where(PackDetails.id << pack_list)

        return query
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_pack_assigned_to: {e}")
        return e

def db_update_assigned_to_pack_details(create_dict, update_dict):
    try:
        PackUserMap.db_update_or_create(create_dict, update_dict)
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(f"Error in db_update_assigned_to_pack_details: {e}")
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in db_update_assigned_to_pack_details: {e}")
        return e

def db_get_notification_packs_to_update(update_notification_packs):
    try:
        updated_rx_change_templates = PackDetails.select(TemplateMaster.id).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(TemplateMaster, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                      (TemplateMaster.file_id == PackHeader.file_id))) \
            .where(PackDetails.id << update_notification_packs)
        notify_change_rx_templates = [record['id'] for record in updated_rx_change_templates]

        return notify_change_rx_templates

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(f"Error in db_update_assigned_to_pack_details: {e}")
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in db_update_assigned_to_pack_details: {e}")
        return e


@log_args_and_response
def get_pack_user_map_dao(company_id, filter_fields, sort_fields, paginate):

    logger.debug("Inside get_pack_user_map_dao")
    try:
        clauses = list()
        clauses.append((PackDetails.batch_id.is_null(True)))
        clauses.append((PackDetails.company_id == company_id))

        exact_search_list = ['system_id', 'print_requested']
        non_exact_search_list = ['patient_name', 'facility_name', 'pack_id', 'pack_display_id']
        membership_search_list = ['user_id', 'status', 'facility_id', 'system_id', 'patient_id']
        between_search_list = ['created_date', 'delivery_date', 'admin_start_date']

        if 'user_id' in filter_fields and filter_fields['user_id'] == -1:
            clauses.append((PackUserMap.assigned_to.is_null(True)))
            filter_fields.pop('user_id')

        fields_dict = {
            "pack_display_id": cast(PackDetails.pack_display_id, 'CHAR'),
            "status": PackDetails.pack_status,
            "user_id": PackUserMap.assigned_to,
            "pack_id": PackDetails.pack_display_id,
            "facility_name": FacilityMaster.facility_name,
            "patient_name": fn.Concat(PatientMaster.last_name, ', ', PatientMaster.first_name),
            "system_id": PackDetails.system_id,
            # "filled_date": fn.DATE(fn.CONVERT_TZ(PackDetails.created_date, settings.TZ_UTC, time_zone)),
            "created_date": fn.DATE(PackDetails.created_date),
            "facility_id": FacilityMaster.id,
            "patient_id": PatientMaster.id,
            "delivery_date": fn.DATE(PackHeader.delivery_datetime),
            "admin_start_date": PackDetails.id,
            "print_requested": fn.IF(PrintQueue.id.is_null(True), 'No', 'Yes')
        }
        order_list = list()
        try:
            clauses = get_filters(clauses, fields_dict, filter_fields,
                                  exact_search_fields=exact_search_list,
                                  like_search_fields=non_exact_search_list,
                                  membership_search_fields=membership_search_list,
                                  between_search_fields=between_search_list)
            logger.info(f"In get_pack_user_map_dao, clauses: {clauses}")

            order_list = get_orders(order_list, fields_dict, sort_fields)
            order_list.append(PackDetails.id)  # To provide same order for grouped data

            pack_data = dict()
            query = PackDetails.select(PackDetails.filled_days,
                                       PackDetails.fill_start_date,
                                       PackDetails.id,
                                       PackDetails.pack_display_id,
                                       PackDetails.pack_no,
                                       FileHeader.created_date,
                                       FileHeader.created_time,
                                       PackDetails.pack_status,
                                       PackDetails.system_id,
                                       PackDetails.consumption_start_date,
                                       PackDetails.consumption_end_date,
                                       PackHeader.patient_id,
                                       PackHeader.delivery_datetime,
                                       PatientMaster.last_name,
                                       PatientMaster.first_name,
                                       PatientMaster.patient_no,
                                       FacilityMaster.facility_name,
                                       PatientMaster.facility_id,
                                       PackDetails.order_no,
                                       PackDetails.pack_plate_location,
                                       CodeMaster.value,
                                       PackDetails.batch_id,
                                       BatchMaster.status.alias('batch_status'),
                                       BatchMaster.name.alias('batch_name'),
                                       fields_dict['patient_name'].alias('patient_name'),
                                       PackUserMap.assigned_to,
                                       PackRxLink.id.alias('pack_rx_link_id'),
                                       fields_dict['delivery_date'].alias('delivery_date'),
                                       fields_dict['print_requested'].alias('print_requested'),
                                       fn.IF((PackDetails.pack_status == settings.FILLED_PARTIALLY_STATUS), True,
                                             False).alias('filled_partially'),
                                       PackUserMap.modified_by.alias('pack_assigned_by')).dicts() \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
                .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
                .join(PrintQueue, JOIN_LEFT_OUTER, on=PrintQueue.pack_id == PackDetails.id) \
                .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(PackDetails.id)
            if clauses:
                query = query.where(functools.reduce(operator.and_, clauses))
            print('query_clause', query)
            if order_list:
                query = query.order_by(*order_list)
            count = query.count()
            if paginate:
                query = apply_paginate(query, paginate)

            pack_data = list(query)

            return pack_data, count

        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    except Exception as e:
        logger.error(f"Error in get_pack_user_map_dao: {e}")
        raise e


@log_args_and_response
def get_user_pack_stats_dao(company_id, date_from, date_to):
    logger.debug("Inside get_user_pack_stats_dao")
    try:
        clauses = list()
        clauses.append((PackDetails.batch_id.is_null(True)))
        clauses.append((PackDetails.company_id == company_id))
        clauses.append((PackDetails.created_date.between(date_from, date_to)))

        query = PackDetails.select(PackDetails.filled_days,
                                   PackDetails.fill_start_date,
                                   PackDetails.id,
                                   PackDetails.pack_display_id,
                                   PackDetails.pack_no,
                                   PackDetails.pack_status,
                                   PackDetails.system_id,
                                   PackDetails.consumption_start_date,
                                   PackDetails.consumption_end_date,
                                   PackDetails.order_no,
                                   PackDetails.pack_plate_location,
                                   PackDetails.batch_id,
                                   PackUserMap.assigned_to,
                                   fn.IF(PackUserMap.assigned_to.is_null(True), False, True).alias('assigned_to_user'),
                                   PackUserMap.modified_by.alias('pack_assigned_by')).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .where(*clauses) \
            .group_by(PackDetails.id)

        return query

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_user_pack_stats_dao: {e}")
        raise e


@log_args_and_response
def db_vision_slots_for_user_station(pack_id):
    slot_data = []
    try:
        for record in VisionDrugPrediction.select(PackGrid.slot_row,
                                                  PackGrid.slot_column,
                                                  VisionCountPrediction.predicted_drug_id,
                                                  fn.sum(VisionCountPrediction.predicted_pill_count).alias(
                                                      "predicted_qty"),
                                                  VisionCountPrediction.is_unknown).dicts() \
                .join(SlotHeader, on=SlotHeader.id == VisionDrugPrediction.slot_header_id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(VisionCountPrediction,
                      on=VisionDrugPrediction.id == VisionCountPrediction.vision_drug_prediction_id) \
                .where(VisionDrugPrediction.pack_id == pack_id) \
                .group_by(SlotHeader.id, VisionCountPrediction.predicted_drug_id):
            slot_data.append(record)

        return slot_data
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError


@log_args_and_response
def get_mfd_canister_drugs(pack_id: int) -> tuple:
    """
    Function to get pack mfd drugs
    @param pack_id:
    @return:
    """
    mfd_data = dict()
    is_mfd_pack = False
    try:
        query = MfdAnalysis.select(DrugMaster.formatted_ndc,
                                   DrugMaster.txr,
                                   MfdAnalysis.mfd_canister_id,
                                   MfdAnalysisDetails.status_id.alias('mfd_analysis_details_status'),
                                   CodeMaster.value.alias('mfd_analysis_details_status_value'),
                                   SlotDetails.id.alias('slot_details_id'),
                                   MfdAnalysisDetails.quantity,
                                   DrugMaster.concated_fndc_txr_field().alias('drug_full_name')
                                   ) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(CodeMaster, on=CodeMaster.id == MfdAnalysisDetails.status_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id).dicts() \
            .where(PackRxLink.pack_id == pack_id) \
            .group_by(MfdAnalysisDetails.id)

        for record in query:
            fndc_txr = (record['formatted_ndc'], record['txr'])
            dropped_quantity = record['quantity'] if record['mfd_analysis_details_status'] == \
                                                     constants.MFD_DRUG_DROPPED_STATUS else 0
            if dropped_quantity:
                is_mfd_pack = True
            skipped_quantity = record['quantity'] if record['mfd_analysis_details_status'] in \
                                                     [constants.MFD_DRUG_RTS_REQUIRED_STATUS,
                                                      constants.MFD_DRUG_RTS_DONE,
                                                      constants.MFD_DRUG_SKIPPED_STATUS,
                                                      constants.MFD_DRUG_PENDING_STATUS] else 0
            mfd_manual_filled = record['quantity'] if record['mfd_analysis_details_status'] in \
                                                      [constants.MFD_DRUG_MVS_FILLED] else 0
            if record['slot_details_id'] not in mfd_data:
                mfd_data[record['slot_details_id']] = {fndc_txr: {
                    'mfd_dropped_quantity': dropped_quantity,
                    'mfd_skipped_quantity': skipped_quantity,
                    'mfd_manual_filled_quantity': mfd_manual_filled,
                    'mfd_canister_id': record['mfd_canister_id']
                }}
            else:
                mfd_data[record['slot_details_id']][fndc_txr] = {
                    'mfd_dropped_quantity': mfd_data[record['slot_details_id']][fndc_txr][
                                                'mfd_dropped_quantity'] + dropped_quantity,
                    'mfd_manual_filled_quantity': mfd_data[record['slot_details_id']][fndc_txr][
                                                      'mfd_manual_filled_quantity'] + mfd_manual_filled,
                    'mfd_skipped_quantity': mfd_data[record['slot_details_id']][fndc_txr][
                                                'mfd_skipped_quantity'] + skipped_quantity,
                    'mfd_canister_id': record['mfd_canister_id']
                }
        return mfd_data, is_mfd_pack

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def get_pharmacy_data_for_system_id(system_id):
    try:
        for record in PharmacyMaster.select().dicts().where(PharmacyMaster.system_id == system_id):
            yield record
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        yield None
    except InternalError as e:
        logger.error(e)
        yield None
    except Exception as e:
        logger.error(e)



@log_args_and_response
def get_patient_details_for_patient_id(patient_id):
    # initialize empty dictionary to store pharmacy details
    # return True if query executes successfully along with the dict of pharmacy details
    logger.debug("Inside get_patient_details_for_patient_id")
    try:
        for record in PatientMaster.select(PatientMaster.last_name, PatientMaster.first_name,
                                           # PatientMaster.pharmacy_patient_id added for Print Utility
                                           PatientMaster.patient_no, PatientMaster.pharmacy_patient_id,
                                           PatientMaster.patient_picture, PatientMaster.address1,
                                           PatientMaster.dob, PatientMaster.workphone,
                                           PatientMaster.allergy, PatientMaster.city, PatientMaster.state,
                                           PatientMaster.zip_code, FacilityMaster.facility_name
                                           ).join(FacilityMaster).dicts().where(PatientMaster.id == patient_id):
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["state"] = record["state"]
            if not record["state"]:
                record["state"] = "CA"
            record["address1"] = record["address1"].strip().upper()[0:12] + "," + record["city"].upper() + "," + \
                                 record["state"] + "," + record["zip_code"]
            if not record["workphone"]:
                record["workphone"] = None
            else:
                record["workphone"] = "(" + record["workphone"][0:3] + ") " + record["workphone"][3:6] + "-" + \
                                      record["workphone"][6:10]
            if not record["allergy"]:
                record["allergy"] = 'NKA'
            yield record
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        yield None
    except InternalError as e:
        logger.error(e)
        yield None


@log_args_and_response
def db_get_pack_info(pack_id):
    try:
        data = PackDetails.select().dicts() \
            .where(PackDetails.id == pack_id) \
            .get()
        return data
    except DoesNotExist as ex:
        return 0
    except InternalError as ex:
        logger.error(ex, exc_info=True)
        return 0


@log_args_and_response
def db_get_pack_slot_transaction(pack_id):
    try:
        pack_transaction_data = False
        query = SlotTransaction.select(SlotTransaction.id, SlotTransaction.pack_id).dicts() \
            .where(SlotTransaction.pack_id == pack_id) \

        for record in query:
            logger.info("Data already added for given pack {}".format(record))
            pack_transaction_data = True
            break
        return pack_transaction_data
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return 0
    except (InternalError, IntegrityError) as ex:
        logger.error(ex, exc_info=True)
        return 0


@log_args_and_response
def get_location_id_from_display_location(device_id, display_location) -> tuple:
    """
        formatted location is the location used for the communication with csr hardware
        :return:
    """
    try:
        query = LocationMaster.select(LocationMaster.id, LocationMaster.is_disabled).where(
            LocationMaster.device_id == device_id,
            LocationMaster.display_location == display_location).get()
        return query.id, query.is_disabled
    except DoesNotExist as e:
        raise e

@log_args_and_response
def db_create_multi_record_in_slot_transaction(slot_transaction_list):
    try:
        BaseModel.db_create_multi_record(
            slot_transaction_list, SlotTransaction
        )
    except Exception as e:
        logger.error(f"Error in db_create_multi_record_in_slot_transaction: {e}")
        raise


@log_args_and_response
def db_update_canister_data(analysis_dict, pack_id, user_id):
    """
    updates drug status to dropped and updates dropped_location for all the canisters
    :param analysis_dict: dict
    :param pack_id: int
    :return: int
    """
    try:
        logger.debug("In db_update_canister_data")
        analysis_ids = list(analysis_dict.keys())
        logger.debug(
            "In slot_transaction_for_pack_id {}, analysis_ids: {}".format(pack_id, analysis_ids))

        pending_canister = MfdAnalysisDetails.select(MfdAnalysisDetails.analysis_id).dicts() \
            .where(MfdAnalysisDetails.analysis_id << analysis_ids,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_PENDING_STATUS,
                                                    constants.MFD_DRUG_RTS_REQUIRED_STATUS,
                                                    constants.MFD_DRUG_FILLED_STATUS])

        non_rts_canisters = MfdAnalysisDetails.select(MfdAnalysisDetails.analysis_id).dicts() \
            .where(MfdAnalysisDetails.analysis_id << analysis_ids,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_PENDING_STATUS,
                                                    constants.MFD_DRUG_FILLED_STATUS])

        non_rts_analysis_ids = list()
        for record in non_rts_canisters:
            non_rts_analysis_ids.append(record['analysis_id'])

        pending_analysis_ids = list()
        for record in pending_canister:
            pending_analysis_ids.append(record['analysis_id'])
        logger.debug(
            "In slot_transaction_for_pack_id {}, pending_analysis_ids: {}".format(pack_id, pending_analysis_ids))

        rts_canister_analysis_ids = list(set(pending_analysis_ids) - set(non_rts_analysis_ids))
        logger.debug(
            "In slot_transaction_for_pack_id {}, rts_canister_analysis_ids: {}".format(pack_id,
                                                                                       rts_canister_analysis_ids))

        if rts_canister_analysis_ids:
            can_status = db_update_canister_status(rts_canister_analysis_ids,
                                                   constants.MFD_CANISTER_RTS_REQUIRED_STATUS, user_id)

        dropped_canister_list = list(set(analysis_ids) - set(pending_analysis_ids))
        logger.debug(
            "In slot_transaction_for_pack_id {}, dropped_canister_list: {}".format(dropped_canister_list, pack_id))

        if dropped_canister_list:
            can_status = db_update_canister_status(dropped_canister_list,
                                                   constants.MFD_CANISTER_DROPPED_STATUS, user_id)
            logger.info("mfd_can_status_changed_to: " + str(constants.MFD_CANISTER_DROPPED_STATUS) +
                        ' for_analysis_ids' + str(dropped_canister_list) + ' with record_update: ' + str(can_status))

        for analysis_id, dropped_location in analysis_dict.items():
            update_dict = {'dropped_location_id': dropped_location}
            status = MfdAnalysis.db_update(update_dict, id=analysis_id)
            logger.info("mfd_can_updated_dropped_location_updated_to " + str(dropped_location) + ' for_analysis ' +
                        str(analysis_id) + ' with: ' + str(status))

        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_pack_display_ids_for_given_packs(company_id, pack_ids, status):
    try:
        pack_list = list()
        query = PackDetails.select(PackDetails.pack_display_id).dicts() \
            .where(PackDetails.company_id == company_id,
                   PackDetails.pack_display_id << pack_ids,
                   PackDetails.pack_status != status)
        for record in query:
            pack_list.append(record['pack_display_id'])
        return pack_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_pending_packs_by_template_and_user(template_id, company_id, assigned_to):
    pack_dict: List[Dict[str, int]] = []
    pack_ids: List[int] = []
    try:
        pack_query = TemplateMaster.select(PackDetails.id, PackDetails.pack_display_id).dicts()\
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id)))\
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
            .join(PackUserMap, on=PackDetails.id == PackUserMap.pack_id)\
            .where(TemplateMaster.id == template_id, TemplateMaster.company_id == company_id,
                   PackUserMap.assigned_to == assigned_to, PackDetails.pack_status == settings.MANUAL_PACK_STATUS)\
            .order_by(PackDetails.id)

        for pack in pack_query:
            pack_dict.append({"pack_id": pack["id"],
                              "pack_display_id": pack["pack_display_id"]})

        return pack_dict
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return {}
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_manual_pack_dao(company_id, filter_fields, sort_fields):

    try:
        clauses = [PackDetails.company_id == company_id]

        if filter_fields and filter_fields.get('patient_name', None) is not None:
            if (filter_fields['patient_name']).isdigit():
                patient_id = int(filter_fields['patient_name'])
                filter_fields['patient_id'] = patient_id
                filter_fields.pop('patient_name')

            elif is_date(filter_fields['patient_name']) and filter_fields['patient_name'][0].isdigit():
                patient_dob = convert_dob_date_to_sql_date(filter_fields['patient_name'])
                filter_fields['patient_dob'] = patient_dob
                filter_fields.pop('patient_name')


        order_list = list()
        defined_orders = list()

        if sort_fields:
            # adding pack status predefined order
            for index, item in enumerate(sort_fields):
                if item[0] == "pack_status":
                    logger.debug("getmanualpacks: got pack_status in sort_fields- before pop: " + str(sort_fields))
                    pack_status_order = sort_fields.pop(index)
                    if pack_status_order[1] == 1:
                        defined_orders.append(SQL('FIELD(pack_status, {},{},{},{},{},{})'
                                                  .format(settings.PARTIALLY_FILLED_BY_ROBOT,
                                                          settings.PROGRESS_PACK_STATUS, settings.MANUAL_PACK_STATUS,
                                                          settings.FILLED_PARTIALLY_STATUS, settings.DONE_PACK_STATUS,
                                                          settings.DELETED_PACK_STATUS)))
                    else:
                        defined_orders.append(SQL('FIELD(pack_status, {},{},{},{},{},{})'
                                                  .format(settings.DELETED_PACK_STATUS, settings.DONE_PACK_STATUS,
                                                          settings.FILLED_PARTIALLY_STATUS,
                                                          settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                                          settings.PARTIALLY_FILLED_BY_ROBOT)))
                    logger.debug("getmanualpacks: got pack_status in sort_fields- after pop: " + str(sort_fields))
                    break

        # again checking for sort fields as we popped pack_status order
        if sort_fields:
            order_list.extend(sort_fields)

        fields_dict = {
            "facility_name": FacilityMaster.facility_name,
            "facility_id": PatientMaster.facility_id,
            "patient_id": PatientMaster.patient_no,
            "patient_dob": PatientMaster.dob,
            "uploaded_by": FileHeader.created_by,
            "uploaded_date": fn.DATE(FileHeader.created_date),
            "created_date": fn.DATE(PackDetails.created_date),
            "admin_start_date": fn.DATE(PackDetails.consumption_start_date),
            "admin_end_date": fn.DATE(PackDetails.consumption_end_date),
            "delivery_date": fn.DATE(PackHeader.scheduled_delivery_date),
            "delivery_date_exact": fn.DATE(PackHeader.scheduled_delivery_date),
            # "pack_status": fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
            #                      fn.IF((PackHeader.change_rx_flag.is_null(True) |
            #                             (PackHeader.change_rx_flag == False)),
            #                            PackDetails.pack_status, settings.PACK_STATUS_CHANGE_RX),
            #                      PackDetails.pack_status),
            "pack_status": PackDetails.pack_status,
            "patient_name": PatientMaster.concated_patient_name_field(),
            "user_id": PackUserMap.assigned_to,
            "pack_display_id": PackDetails.pack_display_id,
            # "status_name": fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
            #                      fn.IF((PackHeader.change_rx_flag.is_null(True) |
            #                             (PackHeader.change_rx_flag == False)),
            #                            CodeMaster.value, constants.EXT_CHANGE_RX_PACKS_DESC),
            #                      CodeMaster.value),
            "status_name": CodeMaster.value,
            "change_rx_flag": PackHeader.change_rx_flag,

            "fill_start_date": PackDetails.fill_start_date,
            "order_no": PackDetails.order_no,
            "company_id": PackDetails.company_id,
            "all_flag": fn.IF(PackUserMap.assigned_to.is_null(True), '0', '1'),
            "assigned_to": fn.IF(PackUserMap.assigned_to.is_null(True), -1, PackUserMap.assigned_to),
            "system_id": PackDetails.system_id,
            "pack_id": PackDetails.id,
            "print_requested": fn.IF(PrintQueue.id.is_null(True), 'No',
                                     fn.IF(PackStatusTracker.status == settings.PARTIALLY_FILLED_BY_ROBOT, 'No',
                                           'Yes')),            "filled_date": PackDetails.filled_date,
        }

        global_search = [
            fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name),
            FacilityMaster.facility_name,
            PackDetails.pack_display_id,
            PackDetails.pack_status,
            fields_dict['delivery_date'],
            fields_dict['admin_start_date'],
            fields_dict['admin_end_date']
        ]
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            multi_search_string.remove('') if '' in multi_search_string else multi_search_string
            clauses = get_multi_search(clauses, multi_search_string, global_search)

        try:
            PackDetailsAlias = PackDetails.alias()
            select_fields = [
                PackDetails.filled_days,
                PackDetails.fill_start_date,
                fields_dict['uploaded_by'].alias('uploaded_by'),
                fields_dict['pack_id'].alias('pack_id'),
                fields_dict['pack_display_id'],
                PackDetails.pack_no,
                FileHeader.created_date.alias('uploaded_date'),
                PackDetails.created_date,
                FileHeader.created_time,
                # fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                #       fn.IF((PackHeader.change_rx_flag.is_null(True) | (PackHeader.change_rx_flag == False)),
                #             PackDetails.pack_status, settings.PACK_STATUS_CHANGE_RX),
                #       PackDetails.pack_status).alias('pack_status'),
                PackDetails.pack_status.alias('pack_status'),
                PackHeader.change_rx_flag,
                PackDetails.system_id,
                fields_dict['admin_start_date'].alias('admin_start_date'),
                fields_dict['admin_end_date'].alias('admin_end_date'),
                PackHeader.patient_id,
                PackHeader.id.alias('pack_header_id'),
                PatientMaster.last_name,
                PatientMaster.first_name,
                fields_dict["patient_id"],
                FacilityMaster.facility_name,
                PatientMaster.facility_id,
                PackDetails.order_no,
                PackDetails.pack_plate_location,
                PackDetails.packaging_type,
                fn.DATE(PackHeader.scheduled_delivery_date).alias('delivery_date'),
                PackDetails.filled_date,
                PatientMaster.dob,
                # fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                #       fn.IF((PackHeader.change_rx_flag.is_null(True) | (PackHeader.change_rx_flag == False)),
                #             CodeMaster.value, constants.EXT_CHANGE_RX_PACKS_DESC),
                #       CodeMaster.value).alias("value"),
                CodeMaster.value,
                PackDetails.batch_id,
                BatchMaster.status.alias('batch_status'),
                BatchMaster.name.alias('batch_name'),
                fields_dict['patient_name'].alias('patient_name'),
                PackDetails.fill_time,
                fields_dict['delivery_date_exact'].alias('delivery_date_exact'),
                fields_dict['assigned_to'].alias('assigned_to'),
                fn.IF(PartiallyFilledPack.id.is_null(True), False, True).alias(
                    'filled_partially'),
                fields_dict['print_requested'].alias('print_requested'),
                PackUserMap.modified_by.alias('pack_assigned_by'),
                ExtPackDetails.ext_status_id.alias('ext_pack_status_id'),
                PackStatusTracker.reason.alias('reason'),
                FileHeader.id.alias('file_id'),
                PatientSchedule.last_import_date,
                PatientSchedule.delivery_date_offset,
                FacilitySchedule.fill_cycle,
                FacilitySchedule.days,
                PatientSchedule.id.alias("patient_schedule_id"),
                (fn.MIN(PackDetailsAlias.consumption_start_date)).alias('min_consumption_start_date')
            ]

            sub_query = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                              ExtPackDetails.pack_id.alias('pack_id')) \
                .group_by(ExtPackDetails.pack_id).alias('sub_query')

            sub_query_reason = PackStatusTracker.select(fn.MAX(PackStatusTracker.id).alias('max_pack_status_id'),
                                                        PackStatusTracker.pack_id.alias('pack_id')) \
                .group_by(PackStatusTracker.pack_id).alias('sub_query_reason')

            query = PackDetails.select(*select_fields).dicts() \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(PatientSchedule, on=((PatientMaster.id == PatientSchedule.patient_id) &
                                           (PatientMaster.facility_id == PatientSchedule.facility_id))) \
                .join(FacilitySchedule, on=PatientSchedule.schedule_id == FacilitySchedule.id)  \
                .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
                .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
                .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
                .join(PrintQueue, JOIN_LEFT_OUTER, PrintQueue.pack_id == PackDetails.id) \
                .join(sub_query, JOIN_LEFT_OUTER, on=(sub_query.c.pack_id == PackDetails.id)) \
                .join(ExtPackDetails, JOIN_LEFT_OUTER, on=ExtPackDetails.id == sub_query.c.max_ext_pack_details_id) \
                .join(sub_query_reason, JOIN_LEFT_OUTER, on=(sub_query_reason.c.pack_id == PackDetails.id)) \
                .join(PackStatusTracker, JOIN_LEFT_OUTER,
                      on=PackStatusTracker.id == sub_query_reason.c.max_pack_status_id) \
                .join(PackDetailsAlias, JOIN_LEFT_OUTER, on=PackDetailsAlias.pack_header_id == PackHeader.id) \
                .group_by(PackDetails.id).order_by(PackDetails.order_no)

            return query, fields_dict, filter_fields, clauses, order_list, defined_orders

        except IntegrityError as ex:
            logger.error(ex, exc_info=True)
            raise IntegrityError

        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

        except Exception as e:
            return e

    except Exception as e:
        return e

@log_args_and_response
def check_for_reuse_pack(pack_display_id, company_id):
    try:
        logger.info("In check_for_reuse_pack")

        query = ExtPackDetails.select(ExtPackDetails.ext_pack_display_id, PackDetails.pack_status, PackDetails.filled_at).dicts() \
                .join(PackDetails, on=ExtPackDetails.pack_id == PackDetails.id) \
                .where(ExtPackDetails.ext_pack_display_id == pack_display_id,
                        PackDetails.company_id == company_id,
                       ExtPackDetails.pack_usage_status_id == constants.EXT_PACK_USAGE_STATUS_PENDING_ID)

        return query
    except Exception as e:
        print(e)


@log_args_and_response
def get_drugs_of_reuse_pack_dao(pack_display_id, company_id, similar_pack_ids):
    try:
        response_dict = {}
        logger.info("In get_drugs_of_reuse_pack_dao")
        total_drugs = set()

        status = None
        status_query = PackDetails.select(PackDetails.pack_status).dicts() \
                    .where(PackDetails.pack_display_id == pack_display_id)
        for data in status_query:
            status = int(data["pack_status"])

        logger.info(f"In get_drugs_of_reuse_pack_dao, pack status of {pack_display_id}: {status}")

        query = PackDetails.select(DrugMaster.id,
                                   UniqueDrug.id.alias("unique_drug_id"),
                                   DrugMaster.formatted_ndc,
                                   DrugMaster.txr,
                                   DrugMaster.ndc,
                                   fn.SUM(SlotDetails.quantity).alias("quantity")).dicts() \
                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.slot_id == SlotDetails.id) \
                .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .where(PackDetails.pack_display_id == pack_display_id,
                       PackDetails.company_id == company_id,
                       ((SlotTransaction.id.is_null(False) & MfdAnalysisDetails.id.is_null(True) |
                         SlotTransaction.id.is_null(True) & MfdAnalysisDetails.status_id << [constants.MFD_DRUG_DROPPED_STATUS]))) \
                .group_by(DrugMaster.id)

        for data in query:
            total_drugs.add(data["id"])
            response_dict[data["id"]] = {"drug_id": data["id"],
                                         "unique_drug_id": data["unique_drug_id"],
                                         "formatted_ndc": data["formatted_ndc"],
                                         "txr": data["txr"],
                                         "ndc": data["ndc"],
                                         "quantity": data["quantity"]}
        if status in [settings.FILLED_PARTIALLY_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT]:
            # remove_drugs = []
            query1 = PackDetails.select(DrugMaster.id,
                                       UniqueDrug.id.alias("unique_drug_id"),
                                       DrugMaster.formatted_ndc,
                                       DrugMaster.txr,
                                       DrugMaster.ndc,
                                       fn.SUM(SlotDetails.quantity).alias("quantity")).dicts() \
                    .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                    .join(PartiallyFilledPack, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
                    .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                    .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                    .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                    .where(PackDetails.pack_display_id == pack_display_id,
                           PartiallyFilledPack.missing_qty == 0) \
                    .group_by(DrugMaster.id)

            for data in query1:
                # remove_drugs.append(data["id"])
                if response_dict.get(data["id"], None):
                    response_dict[data["id"]]["quantity"] += data["quantity"]
                else:
                    response_dict[data["id"]] = {"drug_id": data["id"],
                                                 "unique_drug_id": data["unique_drug_id"],
                                                 "formatted_ndc": data["formatted_ndc"],
                                                 "txr": data["txr"],
                                                 "ndc": data["ndc"],
                                                 "quantity": data["quantity"]}

        elif status in [settings.PROCESSED_MANUALLY_PACK_STATUS, settings.DONE_PACK_STATUS,
                        settings.DELETED_PACK_STATUS]:
            response_dict = dict()
            query = PackDetails.select(DrugMaster.id,
                                   UniqueDrug.id.alias("unique_drug_id"),
                                   DrugMaster.formatted_ndc,
                                   DrugMaster.txr,
                                   DrugMaster.ndc,
                                   fn.SUM(SlotDetails.quantity).alias("quantity")).dicts() \
                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .where(PackDetails.pack_display_id == pack_display_id) \
                .group_by(DrugMaster.id)

            for data in query:
                response_dict[data["id"]] = {"drug_id": data["id"],
                                             "unique_drug_id": data["unique_drug_id"],
                                             "formatted_ndc": data["formatted_ndc"],
                                             "txr": data["txr"],
                                             "ndc": data["ndc"],
                                             "quantity": data["quantity"]}

        else:
            return error(21010)
        response_list = response_dict.values()
        response = list(response_list)
        # ---------------------------------------------------
        # reuse pack
        if similar_pack_ids and response:
            available_txr = [data["txr"] for data in response]
            total_available_txr = len(available_txr)
            required_reuse_pack = True
            get_drug_tracker_data = DrugTracker.select(DrugMaster.txr).dicts() \
                                    .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id) \
                                    .where(DrugTracker.pack_id.in_(similar_pack_ids)) \
                                    .group_by(DrugTracker.pack_id, DrugMaster.txr)
            count = 0
            already_filled_txr = list()
            for data in get_drug_tracker_data:
                if data["txr"] in available_txr and data["txr"] not in already_filled_txr:
                    # required_reuse_pack = False
                    count += 1
                    already_filled_txr.append(data["txr"])

            if count == total_available_txr:
                required_reuse_pack = False

            logger.info("In get_drugs_of_reuse_pack_dao: required_reuse_pack: {}".format(required_reuse_pack))
            if required_reuse_pack:
                pack_ids: list = list()

                pack_data = PackDetails.db_get_pack_details_by_display_ids(pack_display_ids=[pack_display_id])

                for key, value in pack_data.items():
                    if key not in pack_ids:
                        pack_ids.append(key)

                old_pack_txr = (SlotDetails.select(SlotDetails.drug_id, DrugMaster.txr)
                                .dicts()
                                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                                .where(PackDetails.id << pack_ids)
                                .group_by(SlotDetails.drug_id)
                                )

                old_pack_txr_set = set()
                for record in old_pack_txr:
                    old_pack_txr_set.add(record["txr"])

                similar_packs_txr = (SlotDetails.select(SlotDetails.drug_id, DrugMaster.txr)
                                     .dicts()
                                     .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                                     .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                                     .where(PackDetails.id << similar_pack_ids)
                                     .group_by(SlotDetails.drug_id)
                                     )

                is_pack_reusable = False
                for record in similar_packs_txr:
                    if record["txr"] in old_pack_txr_set:
                        is_pack_reusable = True
                        break

                if is_pack_reusable:
                    daw_code_brand_flag_query = (PackDetails.select(PackDetails.id.alias("pack_id"),
                                                                    PatientRx.daw_code,
                                                                    DrugMaster.id.alias("drug_id"),
                                                                    DrugMaster.txr,
                                                                    DrugMaster.brand_flag,
                                                                    PatientRx.patient_id,
                                                                    DrugMaster.formatted_ndc
                                                                    )
                                                 .dicts()
                                                 .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)
                                                 .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                                 .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                                 .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                                                 .where(PackDetails.id << similar_pack_ids)
                                                 )

                    pack_wise_patient_daw_code_brand_flag_of_drug = dict()
                    for record in daw_code_brand_flag_query:
                        if record["pack_id"] not in pack_wise_patient_daw_code_brand_flag_of_drug:
                            pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]] = dict()
                            pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]]["patient"] = record["patient_id"]

                        if record["txr"] not in pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]]:
                            pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]] = dict()

                        pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]]["daw"] =\
                            record["daw_code"]
                        pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]]["brand"] = (
                            record)["brand_flag"]
                        pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]]["fndc"] = (
                            record)["formatted_ndc"]

                    old_pack_patient_query = (PackDetails.select(PatientRx.patient_id)
                                              .dicts()
                                              .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)
                                              .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                              .where(PackDetails.id << pack_ids)
                                              .group_by(PatientRx.patient_id)
                                              )

                    old_pack_patient = None
                    for record in old_pack_patient_query:
                        old_pack_patient = record["patient_id"]

                    count_dict: dict = dict()
                    old_pack_info_dict: dict = dict()
                    old_pack_brand_flag_fndc_dict: dict = dict()
                    # get the data of old_pack from drug_tracker
                    old_pack_query = SlotHeader.select(DrugTracker,
                                                       PackGrid.slot_number,
                                                       SlotDetails.drug_id,
                                                       DrugMaster.formatted_ndc,
                                                       DrugMaster.txr,
                                                       DrugMaster.brand_flag
                                                       ).dicts() \
                            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
                            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                            .join(DrugTracker, on=DrugTracker.slot_id == SlotDetails.id) \
                            .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id) \
                            .where(PackDetails.id << pack_ids,
                                   DrugTracker.is_overwrite != True) \
                            .group_by(PackGrid.slot_number, DrugTracker.drug_id)

                    for record in old_pack_query:
                        drug_tracker_data = dict()
                        drug_tracker_data["drug_tracker_id"] = record["id"]
                        drug_tracker_data["canister_id"] = record["canister_id"]
                        drug_tracker_data["drug_id"] = record["drug_id"]
                        drug_tracker_data["drug_quantity"] = record["drug_quantity"]
                        drug_tracker_data["canister_tracker_id"] = record["canister_tracker_id"]
                        drug_tracker_data["comp_canister_tracker_id"] = record["comp_canister_tracker_id"]
                        drug_tracker_data["drug_lot_master_id"] = record["drug_lot_master_id"]
                        drug_tracker_data["filled_at"] = record["filled_at"]
                        drug_tracker_data["created_by"] = record["created_by"]
                        drug_tracker_data["pack_id"] = record["pack_id"]
                        drug_tracker_data["is_overwrite"] = record["is_overwrite"]
                        drug_tracker_data["scan_type"] = record["scan_type"]
                        drug_tracker_data["case_id"] = record["case_id"]

                        # if record["slot_number"] not in old_pack_info_dict:
                        #     old_pack_info_dict[record["slot_number"]] = dict()
                        #     old_pack_info_dict[record["slot_number"]][record["txr"]] = drug_tracker_data
                        # else:
                        #     old_pack_info_dict[record["slot_number"]][record["txr"]] = drug_tracker_data

                        if record["pack_id"] not in old_pack_brand_flag_fndc_dict:
                            old_pack_brand_flag_fndc_dict[record["pack_id"]] = dict()

                        if record["txr"] not in old_pack_brand_flag_fndc_dict[record["pack_id"]]:
                            old_pack_brand_flag_fndc_dict[record["pack_id"]][record["txr"]] = dict()
                            old_pack_brand_flag_fndc_dict[record["pack_id"]][record["txr"]]["brand"] = (
                                record)["brand_flag"]
                            old_pack_brand_flag_fndc_dict[record["pack_id"]][record["txr"]]["fndc"] = (
                                record)["formatted_ndc"]

                        if record["pack_id"] not in old_pack_info_dict:
                            old_pack_info_dict[record["pack_id"]] = dict()

                        if record["txr"] not in old_pack_info_dict[record["pack_id"]]:
                            old_pack_info_dict[record["pack_id"]][record["txr"]] = list()
                            old_pack_info_dict[record["pack_id"]][record["txr"]].append(drug_tracker_data)
                        else:
                            old_pack_info_dict[record["pack_id"]][record["txr"]].append(drug_tracker_data)

                        if record["txr"] not in count_dict:
                            count_dict[record["txr"]] = 0

                    logger.info("In get_drugs_of_reuse_pack_dao: old_pack_info_dict: {}".format(old_pack_info_dict))

                    # get the data for all similar pack_ids from slot_details
                    new_pack_query = SlotHeader.select(PackGrid.slot_number,
                                                       DrugMaster.id.alias("drug_id"),
                                                       DrugMaster.formatted_ndc,
                                                       DrugMaster.txr,
                                                       fn.SUM(SlotDetails.quantity).alias("quantity"),
                                                       PackDetails.id.alias("pack_id"),
                                                       SlotDetails.id.alias("slot_details_id")).dicts()\
                        .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
                        .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                        .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                        .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                        .where(PackDetails.id << similar_pack_ids) \
                        .group_by(PackGrid.slot_number, SlotDetails.id, PackDetails.id)\
                        .order_by(PackDetails.id, PackGrid.slot_number)

                    first_pack = similar_pack_ids[0]
                    drug_tracker_id_list: list = list()
                    drug_tracker_update_list: list = list()
                    drug_tracker_insert_data: list = list()
                    for record in new_pack_query:
                        # if record["slot_number"] in old_pack_info_dict:
                        #     if record["txr"] in old_pack_info_dict[record["slot_number"]]:
                        #         data = old_pack_info_dict[record["slot_number"]][record["txr"]]
                        allowed_alt_drug = False
                        if record["txr"] in old_pack_info_dict[pack_ids[0]] and record["txr"] not in already_filled_txr:
                            if old_pack_patient == pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]]["patient"]:
                                allowed_alt_drug = True
                            elif old_pack_patient != pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]]["patient"]:
                                if pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]]["daw"] == 0:
                                    if pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]]["brand"] == settings.BRAND_FLAG:
                                        if (old_pack_brand_flag_fndc_dict[pack_ids[0]][record["txr"]][
                                            "brand"] == settings.BRAND_FLAG
                                                and pack_wise_patient_daw_code_brand_flag_of_drug[record[
                                                    "pack_id"]][record["txr"]]["fndc"]
                                                == old_pack_brand_flag_fndc_dict[pack_ids[0]][record["txr"]]["fndc"]):
                                            allowed_alt_drug = True

                                    elif pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record[
                                        "txr"]]["brand"] == settings.GENERIC_FLAG:
                                        if old_pack_brand_flag_fndc_dict[pack_ids[0]][record["txr"]]["brand"] == settings.GENERIC_FLAG:
                                            allowed_alt_drug = True

                                elif pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]]["daw"] == 1:
                                    if (pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][record["txr"]][
                                        "fndc"] == old_pack_brand_flag_fndc_dict[pack_ids[0]][record["txr"]]["fndc"]
                                            and pack_wise_patient_daw_code_brand_flag_of_drug[record["pack_id"]][
                                                record["txr"]]["brand"] == old_pack_brand_flag_fndc_dict[pack_ids[0]][
                                                record["txr"]]["brand"]):
                                        allowed_alt_drug = True

                            if allowed_alt_drug:
                                data = old_pack_info_dict[pack_ids[0]][record["txr"]][count_dict[record["txr"]]]
                                drug_tracker_info_data = dict()
                                drug_tracker_info_data["canister_id"] = data["canister_id"]
                                drug_tracker_info_data["drug_id"] = data["drug_id"]
                                drug_tracker_info_data["canister_tracker_id"] = data["canister_tracker_id"]
                                drug_tracker_info_data["comp_canister_tracker_id"] = data["comp_canister_tracker_id"]
                                drug_tracker_info_data["drug_lot_master_id"] = data["drug_lot_master_id"]
                                drug_tracker_info_data["filled_at"] = settings.FILLED_AT_PACK_FILL_WORKFLOW
                                drug_tracker_info_data["created_by"] = data["created_by"]
                                drug_tracker_info_data["is_overwrite"] = data["is_overwrite"]
                                drug_tracker_info_data["pack_id"] = record["pack_id"]
                                drug_tracker_info_data["drug_quantity"] = record["quantity"]
                                drug_tracker_info_data["slot_id"] = record["slot_details_id"]
                                drug_tracker_info_data["scan_type"] = data["scan_type"]
                                drug_tracker_info_data["case_id"] = data["case_id"]
                                drug_tracker_info_data["reuse_pack"] = data["pack_id"]
                                drug_tracker_insert_data.append(drug_tracker_info_data)

                                if data["drug_tracker_id"] not in drug_tracker_update_list:
                                    # drug_tracker_id_list.append(data["drug_tracker_id"])
                                    reuse_quantity = None
                                    if data["drug_quantity"] > record["quantity"]:
                                        reuse_quantity = record["quantity"]
                                    elif data["drug_quantity"] <= record["quantity"]:
                                        reuse_quantity = data["drug_quantity"]

                                    update_dict = {"is_overwrite": 3,
                                                   "reuse_quantity": reuse_quantity,
                                                   "modified_date": get_current_date_time()
                                                   }

                                    drug_tracker_update_list.append({data["drug_tracker_id"]: update_dict})

                                if count_dict[record["txr"]] == len(old_pack_info_dict[pack_ids[0]][record["txr"]]) - 1:
                                    count_dict[record["txr"]] = 0
                                else:
                                    count_dict[record["txr"]] = count_dict[record["txr"]] + 1

                    if not drug_tracker_insert_data:
                        return error(21011)

                    logger.info("In get_drugs_of_reuse_pack_dao: drug_tracker_insert_data: {}"
                                .format(drug_tracker_insert_data))

                    logger.info("In get_drugs_of_reuse_pack_dao: drug_tracker_update_list: {}"
                                .format(drug_tracker_update_list))

                    if drug_tracker_insert_data:
                        drug_tracker_status = BaseModel.db_create_multi_record(drug_tracker_insert_data, DrugTracker)
                        logger.info("In get_drugs_of_reuse_pack_dao: drug_tracker_status: {}".format(drug_tracker_status))

                    if drug_tracker_update_list:
                        # update_dict: dict = dict()
                        # update_dict["is_overwrite"] = 3
                        # update_dict["modified_date"] = get_current_date_time()
                        for drug_tracker_record in drug_tracker_update_list:
                            for drug_tracker_id, update_dict in drug_tracker_record.items():
                                drug_tracker_update_status = DrugTracker.db_update_drug_tracker_by_drug_tracker_id(update_dict=update_dict,
                                                                                                                   drug_tracker_ids=[drug_tracker_id])
                                logger.info("In get_drugs_of_reuse_pack_dao: drug_tracker_update_status: {}".format(drug_tracker_update_status))

                    if pack_ids:
                        ext_pack_details_status = ExtPackDetails.db_update_ext_pack_usage_status(pack_ids=pack_ids)
                        logger.info("In get_drugs_of_reuse_pack_dao: ext_pack_details_status: {}"
                                        .format(ext_pack_details_status))
                else:
                    return error(21011)
        else:
            return error(21011)
        return create_response(response)

    except Exception as e:
        logger.error(f"Error in get_drugs_of_reuse_pack_dao, e: {e}")
        raise e


@log_args_and_response
def db_check_change_rx_flag_for_pack(pack_id: int):
    change_rx_flag: bool = False
    try:
        query = PackDetails.select(PackHeader.change_rx_flag).dicts()\
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
            .where(PackDetails.id == pack_id)

        for pack in query:
            if pack["change_rx_flag"]:
                change_rx_flag = True
        return change_rx_flag
    except (IntegrityError, InternalError, Exception) as ex:
        logger.error(ex, exc_info=True)
        raise ex


@log_args_and_response
def get_user_assigned_packs_dao(company_id, filter_fields, sort_fields):

    try:
        clauses = list()
        clauses.append((PackDetails.company_id == company_id))
        clauses.append((PackDetails.batch_id.is_null(True)))

        exact_search_list = ['system_id', 'print_requested']
        non_exact_search_list = ['patient_name', 'facility_name', 'pack_id', 'pack_display_id']
        membership_search_list = ['user_id', 'status', 'facility_id', 'system_id', 'patient_id']
        between_search_list = ['created_date', 'delivery_date', 'admin_start_date', 'admin_end_date']

        fields_dict = {
            "pack_display_id": cast(PackDetails.pack_display_id, 'CHAR'),
            "status": PackDetails.pack_status,
            "user_id": PackUserMap.assigned_to,
            "pack_id": PackDetails.pack_display_id,
            "facility_name": FacilityMaster.facility_name,
            "patient_name": fn.Concat(PatientMaster.last_name, ', ', PatientMaster.first_name),
            "system_id": PackDetails.system_id,
            # "filled_date": fn.DATE(fn.CONVERT_TZ(PackDetails.created_date, settings.TZ_UTC, time_zone)),
            "created_date": fn.DATE(PackDetails.created_date),
            "facility_id": FacilityMaster.id,
            "patient_id": PatientMaster.id,
            "delivery_date": fn.DATE(PackHeader.delivery_datetime),
            "admin_start_date": PackDetails.consumption_start_date,
            "admin_end_date": PackDetails.consumption_end_date,
            "print_requested": fn.IF(PrintQueue.id.is_null(True), 'No', 'Yes')
        }
        order_list = list()
        if 'user_id' in filter_fields and filter_fields['user_id'] == -1:
            clauses.append((PackUserMap.assigned_to.is_null(True)))
            filter_fields.pop('user_id')

        try:
            clauses = get_filters(clauses, fields_dict, filter_fields,
                                  exact_search_fields=exact_search_list,
                                  like_search_fields=non_exact_search_list,
                                  membership_search_fields=membership_search_list,
                                  between_search_fields=between_search_list)

            logger.info(f"In get_user_assigned_packs_dao, clauses: {clauses}")

            order_list = get_orders(order_list, fields_dict, sort_fields)
            order_list.append(PackDetails.id)  # To provide same order for grouped data

            query = PackDetails.select(PackDetails.filled_days,
                                       PackDetails.fill_start_date,
                                       PackDetails.id,
                                       PackDetails.pack_display_id,
                                       PackDetails.pack_no,
                                       FileHeader.created_date,
                                       FileHeader.created_time,
                                       PackDetails.pack_status,
                                       PackDetails.system_id,
                                       PackDetails.consumption_start_date,
                                       PackDetails.consumption_end_date,
                                       PackHeader.patient_id,
                                       PackHeader.delivery_datetime,
                                       PatientMaster.last_name,
                                       PatientMaster.first_name,
                                       PatientMaster.patient_no,
                                       FacilityMaster.facility_name,
                                       PatientMaster.facility_id,
                                       PackDetails.order_no,
                                       PackDetails.pack_plate_location,
                                       CodeMaster.value,
                                       PackDetails.batch_id,
                                       BatchMaster.status.alias('batch_status'),
                                       BatchMaster.name.alias('batch_name'),
                                       fields_dict['patient_name'].alias('patient_name'),
                                       PackUserMap.assigned_to,
                                       PackRxLink.id.alias('pack_rx_link_id'),
                                       fields_dict['delivery_date'].alias('delivery_date'),
                                       fields_dict['print_requested'].alias('print_requested'),
                                       fn.IF((PackDetails.pack_status == settings.FILLED_PARTIALLY_STATUS), True, False)
                                       .alias('filled_partially'),
                                       PackUserMap.modified_by.alias('pack_assigned_by')).dicts() \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
                .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
                .join(PrintQueue, JOIN_LEFT_OUTER, on=PrintQueue.pack_id == PackDetails.id) \
                .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(PackDetails.id)
            if clauses:
                query = query.where(functools.reduce(operator.and_, clauses))
            print('query_clause', query)
            if order_list:
                query = query.order_by(*order_list)
            count = query.count()
            # if paginate:
            #     query = apply_paginate(query, paginate)

            return query, count

        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            return error(2001)
    except Exception as e:
        logger.error(f"Error in get_user_assigned_packs_dao: {e}")
        return e


@log_args_and_response
def get_user_assigned_pack_count_dao(company_id, users):
    try:
        clauses = list()
        clauses.append((PackDetails.company_id == company_id))
        if users:
            users = json.loads(users)
        if users:
            clauses.append((PackUserMap.assigned_to << users))

        query = PackDetails.select(PackUserMap.assigned_to,
                                   fn.COUNT(PackUserMap.pack_id).alias('pack_count')).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(PackUserMap.assigned_to)

        return list(query)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_user_assigned_pack_count_dao: {e}")
        return e


@log_args_and_response
def get_user_wise_pack_count_dao(company_id):
    try:
        query = PackUserMap.select(PackUserMap.assigned_to, fn.COUNT(PackUserMap.assigned_to).alias('count')).dicts() \
            .join(PackDetails, on=PackDetails.id == PackUserMap.pack_id) \
            .where(PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.FILLED_PARTIALLY_STATUS],
                   PackDetails.company_id == company_id, PackDetails.consumption_start_date >= datetime.datetime.now()) \
            .group_by(PackUserMap.assigned_to)

        return query

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_user_wise_pack_count_dao: {e}")
        return e

def get_pack_id_for_given_status_from_given_packs(pack_ids):
    try:
        packs = PackDetails.select(PackDetails.id).dicts() \
            .where(PackDetails.id << pack_ids, PackDetails.pack_status == settings.FILLED_PARTIALLY_STATUS)
        return packs
    except Exception as e:
        return e


def get_order_no_for_given_company_id(company_id):
    try:
        order_no = PackDetails.select(fn.MAX(PackDetails.order_no).alias('order_no')) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id).dicts() \
            .where(PackDetails.company_id == company_id).get()

        return order_no
    except Exception as e:
        return e


def update_pack_details_for_pack_ids(pack_ids, order_no_list):
    try:
        updated_pack_query = PackDetails.select(PackDetails.id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.id << pack_ids) \
            .order_by(PackHeader.scheduled_delivery_date, FacilityMaster.facility_name, PackDetails.id)
        updated_list = list(updated_pack_query.dicts())

        for index, item in enumerate(order_no_list):
            update_info = PackDetails.update(order_no=order_no_list[index]).where(
                PackDetails.id == int(updated_list[index]['id'])).execute()
    except Exception as e:
        return e


@log_args_and_response
def get_batch_status_from_batch_id(batch_id):
    try:
        query = BatchMaster.select(BatchMaster.status).where(BatchMaster.id == batch_id).dicts().get()
        return query['status']
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return 0
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def update_scheduled_start_date_for_next_batches(pack_ids):
    try:
        with db.transaction():
            batch_id, system_id = get_batch_id_from_pack_list(pack_ids)
            pack_count = get_pack_count_by_batch(batch_id)
            batch_schedule_date_dict = {}
            previous_start_date = 0
            if pack_count == 0:
                batch_start_date_dict = get_next_pending_batches(system_id, batch_id)
                if len(batch_start_date_dict) > 1:
                    count = 1
                    for batch, start_date in batch_start_date_dict.items():
                        if batch == batch_id:
                            # batch_schedule_date_dict[batch] = start_date
                            previous_start_date = start_date
                            count += 1
                            continue
                        if count == 2:
                            batch_schedule_date_dict[batch] = previous_start_date
                            total_packs = get_pack_count_by_batch(batch)
                            count += 1
                            continue
                        # total_packs = get_pack_count_by_batch(batch)
                        system_timings = get_system_setting_by_system_id(system_id=system_id)
                        previous_start_date = get_batch_scheduled_start_date(system_timings, total_packs,
                                                                             previous_start_date,
                                                                             batch)
                        batch_schedule_date_dict[batch] = previous_start_date
                        date_status = BatchMaster.update(scheduled_start_time=previous_start_date).where(
                            BatchMaster.id == batch).execute()
                        if count == len(batch_start_date_dict):
                            break
                        count += 1
                        total_packs = get_pack_count_by_batch(batch)
                update_status = BatchMaster.update(status=settings.BATCH_DELETED).where(
                    BatchMaster.id == batch_id).execute()
                # this function call deletes the data from guided tracker when the batch is marked as deleted
                # todo- uncomment this when we change join of guided_transfer_cycle_history table
                # delete_from_guided_tracker(batch_id=batch_id)
                return update_status
            return 1
    except Exception as e:
        logger.error(e, exc_info=True)


@log_args_and_response
def get_latest_print_data(pack_id):
    """

    :param pack_id:
    :return:
    """
    try:
        pending_print_data = PrintQueue.select().dicts() \
            .where(PrintQueue.printing_status << (settings.PRINT_STATUS['Pending'],
                                                  settings.PRINT_STATUS['In queue'],
                                                  settings.PRINT_STATUS['Done'],
                                                  settings.PRINT_STATUS['Printing']),
                   PrintQueue.pack_id == pack_id).order_by(PrintQueue.id.desc()).get()
        return {'print_job_id': pending_print_data['id'],
                'print_status': pending_print_data['printing_status'],
                'page_count': pending_print_data['page_count']}
    except DoesNotExist:
        return {}
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pvs_dimension():
    """
    Returns the slot image crop dimensions to remove black hopper area for MVS
    :return: list
    """
    data = list()
    try:
        for record in PVSDimension.select().dicts():
            data.append({
                "company_id": record["company_id"],
                "device_id": record["device_id"],
                "quadrant": record["quadrant"],
                "left_value": record["left_value"],
                "right_value": record["right_value"],
                "top_value": record["top_value"],
                "bottom_value": record["bottom_value"]
            })
        return data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise

def get_skipped_canister_drug_qty(pack_id):
    try:
        query = PackAnalysis.select(PackGrid.slot_number,
                                    fn.sum(SlotDetails.quantity).alias('canister_skipped_drug_qty')).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(SlotDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id).dicts() \
            .join(SlotTransaction, JOIN_LEFT_OUTER, SlotTransaction.slot_id == SlotDetails.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .where(PackAnalysis.batch_id == PackDetails.batch_id,
                   PackAnalysis.pack_id == pack_id,
                   PackAnalysisDetails.status != constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED,
                   MfdAnalysisDetails.id.is_null(True),
                   SlotTransaction.id.is_null(True)) \
            .group_by(PackGrid.slot_number)

        return query
    except Exception as e:
        return e
@log_args_and_response
def save_distributed_packs_by_batch(batch_info):
    """
    This function is special handling of function save_distributed_packs
    It handles scenario when there is only one system in pharmacy
    We want to provide functionality in which they can replenish
    and transfer for idle robots.
    :param batch_info: dict
    :return: str
    """
    batch_id = batch_info['batch_id']
    system_id = batch_info['system_id']
    user_id = batch_info['user_id']
    split_function_id = batch_info.get('split_function_id', None)
    logger.info('----------------------------------------Starting of API--------------------------------------------')
    logger.info('split_function_id in args:{}'.format(split_function_id))

    try:
        # This validation should fix bug #121778,
        # bug replicates when two algorithm runs and saves pack analysis data under same batch_id
        # we will prevent this by checking status of batch is pending before running algorithm
        with db.transaction():

            batch = BatchMaster.get(id=batch_id)
            if batch.status.id != settings.BATCH_PENDING:
                return error(1020, 'Batch is not in pending state. '
                                   'It is more likely that recommendation algorithm being executed.')
            else:
                BatchMaster.db_set_status(batch.id, settings.BATCH_CANISTER_TRANSFER_RECOMMENDED, user_id)
                split_function_id = BatchMaster.db_get_split_function_id(batch.id, split_function_id)

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return error(1020, 'Batch does not exist with given batch_id.')
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    try:
        logger.info('split_function_id from db:{}'.format(split_function_id))
        query = PackDetails.select(PackDetails.id)
        query = query.where(
            PackDetails.batch_id == batch_id
        )
        pack_ids = [record.id for record in query]
        distribution_info = {
            # create structured data for _save_distributed_packs
            'batch_present': True,
            'company_id': batch_info['company_id'],
            'user_id': user_id,
            'split_function_id': split_function_id,
            'pack_distribution': {
                system_id: {
                    'batch_name': batch.name,
                    'batch_id': batch_id,
                    'pack_list': pack_ids
                }
            },
        }
        with db.transaction():
            _save_distributed_packs(distribution_info)
            status = settings.BATCH_CANISTER_TRANSFER_RECOMMENDED
        return create_response({'batch_status': status, })
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        BatchMaster.db_set_status(batch.id, settings.BATCH_PENDING, user_id)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        print(e)
        BatchMaster.db_set_status(batch.id, settings.BATCH_PENDING, user_id)
        return error(2001)


# @validate(required_fields=['user_id', 'system_id', 'batch_id', 'company_id'])
@log_args_and_response
def save_distributed_packs_by_batch_v3(batch_info):
    batch_id = batch_info['batch_id']
    company_id = batch_info['company_id']
    system_id = batch_info['system_id']
    user_id = batch_info['user_id']
    split_function_id = batch_info.get('split_function_id', None)

    try:

        # check for pending normal canister transfer flow
        logger.info("save_distributed_packs_by_batch_v3: Checking for pending canister transfers")
        pending_can_transfers = check_pending_canister_transfers(system_id=system_id)
        pending_batch_id, pending_device_system_id, pending_cycle_id = None, None, None

        if pending_can_transfers:
            logger.info("save_distributed_packs_by_batch_v3: Incomplete canister transfer flow {}".
                        format(pending_can_transfers))
            for record in pending_can_transfers:
                if not pending_batch_id or not pending_device_system_id:
                    pending_batch_id = record["batch_id"]
                    pending_device_system_id = record["pending_device_system_id"]
                    pending_cycle_id = record["cycle_id"]
        logger.info("save_distributed_packs_by_batch_v3: No pending cycle of canister transfer flow {}, {}".
                    format(pending_batch_id, pending_device_system_id))
        # Removing code block from here and writing it down

        with db.transaction():

            batch = BatchMaster.get(id=batch_id)
            if batch.status.id != settings.BATCH_PENDING:
                return error(1020, 'Batch is not in pending state. '
                                   'It is more likely that recommendation algorithm being executed.')
            else:
                # BatchMaster.db_set_status(batch.id, settings.BATCH_CANISTER_TRANSFER_RECOMMENDED, user_id)
                split_function_id = BatchMaster.db_get_split_function_id(batch.id, split_function_id)

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return error(1020, 'Batch does not exist with given batch_id.')
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error()

    try:
        query = PackDetails.select(PackDetails.id)
        query = query.where(PackDetails.batch_id == batch_id,
                            PackDetails.pack_status == settings.PENDING_PACK_STATUS)
        pack_ids = [record.id for record in query]
        distribution_info = {
            # create structured data for _save_distributed_packs
            'batch_present': True,
            'company_id': batch_info['company_id'],
            'user_id': user_id,
            'system_id': system_id,
            'split_function_id': split_function_id,
            'pack_distribution': {
                system_id: {
                    'batch_name': batch.name,
                    'batch_id': batch_id,
                    'pack_list': pack_ids
                    # [71133,71134,71135,71136,71137,71138,71139,71140,71141,71142,71143,71144,71145,71146,71147,71148,71149,71150,71151,71152,71153,71154,71155,71156,71157,71158,71159,71160,71161,71162,71163,71164,74894,74895,74896,74897,74898,74899,74900,74901,74902,74903,74904,74905,74906,74907,74908,74909,74910,74911,74912,74913,74914,74915,74916,74917,74918,74919,74920,74921,74922,74923,74924,74925,74926,74927,74928,74929,74930,74931,74932,74933,74934,74935,74936,74937,74938,74939,74940,74941,74942,74943,74944,74945,74946,74947,74948,74949,74950,74951,74952,74953,74954,74955,74956,74957,74958,74959,74960,74961,74962,74963,74964,74965,74966,74967,74968,74969,74970,74971,74972,74973,74974,74975,74976,74977,74978,74979,74980,74981,74982,74983,72737,72738,72739,72740,72741,72742,72743,72744,72745,72746,72747,72748,72749,72750,72751,72752,72753,72754,72755,72756,72757,72758,72759,72760]
                }
            },
        }

        with db.transaction():
            _save_distributed_packs_v3(distribution_info)
            status = settings.BATCH_CANISTER_TRANSFER_RECOMMENDED

        # set order number of packs in this temporary for production as we are creating batch from backend
        logger.info("update order number for packs")
        _max_order_no = PackDetails.db_max_order_no(system_id)
        pack_list = get_ordered_pack_list(pack_ids)
        pack_orders = [_max_order_no + index + 1 for index, item in enumerate(pack_list)]

        update_query = PackDetails.db_update_pack_order_no({
            'pack_ids': ','.join(list(map(str, pack_list))),
            'order_nos': ','.join(list(map(str, pack_orders))),
            'system_id': system_id
        })
        logger.info("order number updated in pack details {}".format(update_query))

        # Previously this below code block was written at top... This created a bug where
        # canister-transfers-wizard was updated
        # before any data gets populated in CanisterTransfers table... Result of this, couchdb get re-set..
        # Now we will update couchdb after recommendation executes...
        if not pending_batch_id:
            update_couch_db_status, couch_db_response = update_canister_transfer_wizard_data_in_couch_db(
                {"company_id": company_id, "batch_id": batch_id,
                 "timestamp": get_current_date_time(), "robot_system_id": system_id})
            logger.debug("canister transfer: couch db updated with status: " + str(update_couch_db_status))
            logger.info("couch db update status {} , {}".format(update_couch_db_status, couch_db_response))

            if not update_couch_db_status:
                return couch_db_response
        else:
            cart_canisters = check_canisters_present_in_cart(system_id=system_id)
            if cart_canisters:
                update_couch_db_status, couch_db_response = update_canister_transfer_wizard_data_in_couch_db(
                    {"company_id": company_id, "batch_id": pending_batch_id,
                     "timestamp": get_current_date_time(), "robot_system_id": system_id, "module_id": 2,
                     "transfer_cycle_id": pending_cycle_id})
            else:
                update_dict = {"status_id": constants.CANISTER_TRANSFER_TO_CSR_DONE,
                               "modified_date": get_current_date_time()}

                canister_tx_status = update_canister_tx_meta_by_batch_id(update_dict=update_dict,
                                                                         batch_id=pending_batch_id)

                update_couch_db_status, couch_db_response = update_canister_transfer_wizard_data_in_couch_db(
                    {"company_id": company_id, "batch_id": batch_id,
                     "timestamp": get_current_date_time(), "robot_system_id": system_id})
                logger.debug("canister transfer: couch db updated with status after to csr done: " + str(update_couch_db_status))
                logger.info("couch db update status {} , {}".format(update_couch_db_status, couch_db_response))
                if not update_couch_db_status:
                    return couch_db_response
        # commenting as mfd recommendation will be executed after alternate drug screen
        # with db.transaction():
        #     mfd_status = save_mfd_recommendation(batch_info=batch_info)

        return create_response({'batch_status': status})

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        BatchMaster.db_set_status(batch.id, settings.BATCH_PENDING, user_id)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        BatchMaster.db_set_status(batch.id, settings.BATCH_PENDING, user_id)
        return error(2001)

@log_args_and_response
def check_canisters_present_in_cart(system_id: int) -> list:
    """
    Function to check if canisters are present in canister transfer cart or Canister Cart w/ Elevator
    @param system_id: int
    @return: list
    """
    logger.info("Inside check_canisters_present_in_cart")
    canister_list = list()
    try:
        device_types = [settings.DEVICE_TYPES['Canister Transfer Cart'],
                        settings.DEVICE_TYPES['Canister Cart w/ Elevator']]

        query = CanisterMaster.select(CanisterMaster.id).dicts() \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(DeviceMaster.system_id == system_id,
                   DeviceMaster.device_type_id << device_types)

        for record in query:
            canister_list.append(record['id'])

        logger.info("check_canisters_present_in_cart response {}".format(canister_list))
        return canister_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in check_canisters_present_in_cart {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("Error in check_canisters_present_in_cart {}".format(e))
        return canister_list



@log_args_and_response
def get_packs_by_facility_distribution_id(facility_distribution_id: int, company_id: int):
    try:
        return PackDetails.get_packs_by_facility_distribution_id(facility_distribution_id, company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def check_canisters_present_in_cart(system_id: int) -> list:
    """
    Function to check if canisters are present in canister transfer cart or Canister Cart w/ Elevator
    @param system_id: int
    @return: list
    """
    logger.info("Inside check_canisters_present_in_cart")
    canister_list = list()
    try:
        device_types = [settings.DEVICE_TYPES['Canister Transfer Cart'],
                        settings.DEVICE_TYPES['Canister Cart w/ Elevator']]

        query = CanisterMaster.select(CanisterMaster.id).dicts() \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(DeviceMaster.system_id == system_id,
                   DeviceMaster.device_type_id << device_types)

        for record in query:
            canister_list.append(record['id'])

        logger.info("check_canisters_present_in_cart response {}".format(canister_list))
        return canister_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in check_canisters_present_in_cart {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("Error in check_canisters_present_in_cart {}".format(e))
        return canister_list


@log_args_and_response
def get_patient_drug_alternate_flag_data(pack_list):
    """
    This function will give you patient wise drug and alternate use flag means if that drug can be replaced with
    alternate drug or not
    :param pack_list:
    :return:
    """
    try:
        patient_drug_alternate_flag_dict = {}

        for record in PackRxLink.select(
                PackRxLink.patient_rx_id,
                PackRxLink.id,
                PackRxLink.original_drug_id,
                SlotDetails.drug_id,
                PatientRx.patient_id,
                PatientRx.daw_code,
                PackRxLink.pack_id,
                fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')).alias('drug')
        ).dicts() \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .join(SlotDetails, on=  SlotDetails.pack_rx_id == PackRxLink.id)\
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .where(PackRxLink.pack_id << pack_list):
            if record['patient_id'] not in patient_drug_alternate_flag_dict:
                patient_drug_alternate_flag_dict[record['patient_id']] = {}
            patient_drug_alternate_flag_dict[record['patient_id']][record['drug']] = True if record['daw_code'] == 0 \
                else False

        return patient_drug_alternate_flag_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        print(e)
        raise


@log_args_and_response
def get_original_drug_id(drug_ids, patient_packs, patient_id):
    try:
        packs = list(map(int, patient_packs[patient_id]))
        query = SlotDetails.select(SlotDetails.drug_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id).where(PackRxLink.pack_id << packs)

        for record in query.dicts():
            if record['drug_id'] in drug_ids:
                return record['drug_id']
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        print(e)
        raise


@log_args_and_response
def get_pack_slot_drug_data(pack_list):
    try:
        pack_slot_drug_dict = dict()
        pack_slot_detail_drug_dict = dict()

        query = PackDetails.select(PackDetails.id,
                                   fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug_id'),
                                   PackGrid.slot_number, SlotDetails.id.alias('slot_id')) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list)

        for record in query.dicts():
            if record['id'] not in pack_slot_drug_dict.keys():
                pack_slot_drug_dict[record['id']] = {}
                pack_slot_detail_drug_dict[record['id']] = {}
            if record['slot_number'] not in pack_slot_drug_dict[record['id']].keys():
                pack_slot_drug_dict[record['id']][record['slot_number']] = set()
                pack_slot_detail_drug_dict[record['id']][record['slot_number']] = record['slot_id']
            if record['drug_id'] is not None:
                pack_slot_drug_dict[record['id']][record['slot_number']].add(record['drug_id'])

        logger.info(pack_slot_drug_dict, pack_slot_detail_drug_dict)
        return pack_slot_drug_dict

    except Exception as e:
        logger.info(e)
        return e


@log_args_and_response
def get_batch_scheduled_start_date_and_packs(batch_id):
    try:
        query = PackDetails.select(fn.COUNT(PackDetails.id).alias('total_packs'),
                                   fn.DATE(BatchMaster.scheduled_start_time).alias('scheduled_start_date')) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id).where(BatchMaster.id == batch_id).group_by(
            BatchMaster.id)
        for record in query.dicts():
            total_packs = record['total_packs']
            scheduled_start_date = record['scheduled_start_date']
            return total_packs, scheduled_start_date
    except DoesNotExist as e:
        return 0, None
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        print(e)
        raise


@log_args_and_response
def get_ordered_pack_list(pack_list):
    """
    This function returns ordered pack list for assigning order_no.
    Sorting logic is based on scheduled_delivery_date
    @param pack_list:list
    @return:sorted_pack_list
    """
    sorted_pack_list = []
    query = PackDetails.select(PackDetails.id) \
        .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
        .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
        .where(PackDetails.id.in_(pack_list)) \
        .order_by(PackHeader.scheduled_delivery_date, PatientMaster.id)

    for record in query.dicts():
        sorted_pack_list.append(record["id"])
    return sorted_pack_list


@log_args_and_response
@validate(required_fields=['pack_distribution', 'company_id', 'user_id'])
def _save_distributed_packs_v3(distribution_info):
    """
    Internal function to distribute packs.
    This will be used to return python data types
    instead of json so multiple apis can be written on this function.
    :param distribution_info: dict
    :return:
    """
    batch_present = distribution_info.get('batch_present', False)
    # batch_present: do not create batch record as already present.
    # If False, new batch will be created and assigned to these packs
    pack_distribution = distribution_info["pack_distribution"]
    company_id = distribution_info["company_id"]
    system_id = distribution_info["system_id"]
    user_id = distribution_info['user_id']
    split_function_id = distribution_info.get('split_function_id', None)
    re_run = False
    pack_distributorV3 = PackDistributorV3(company_id=company_id, batch_packs=pack_distribution,
                                           split_function_id=split_function_id, dry_run=False, system_id=system_id)
    recommendations = pack_distributorV3.get_recommendation()
    print("done till jere")
    # pass
    # return
    # re use of intermediate artifacts of pack distribution
    robots_data = pack_distributorV3.robots_data
    pack_manual = pack_distributorV3.pack_manual
    canister_data = pack_distributorV3.canister_data
    cache_drug_data = pack_distributorV3.cache_drug_data
    fully_manual_pack_drug = pack_distributorV3.fully_manual_pack_drug
    batch_names = pack_distributorV3.batch_names
    batch_ids = pack_distributorV3.batch_ids
    system_packs = pack_distributorV3.system_packs
    robot_dict = pack_distributorV3.robot_dict
    print("her i m")

    with db.transaction():

        reserved_batch_canisters = dict()
        for system, data in recommendations.items():
            _max_order_no = PackDetails.db_max_order_no(system)
            pack_orders = list(range(_max_order_no + 1, _max_order_no + len(system_packs[system]) + 1))
            if not batch_ids[system]:
                batch = BaseModel.db_create_record({
                    'name': batch_names[system],
                    'system_id': system,
                    'status': settings.BATCH_PENDING,
                    'created_by': user_id
                }, BatchMaster, get_or_create=False)
                batch_id = batch.id
            else:
                batch_id = batch_ids[system]
            print("last")
            transfers, analysis = data['canister_transfer_info_dict'], data['analysis']
            batch_id, _ = save_analysis(analysis, pack_manual, canister_data, cache_drug_data, batch_id,
                                        system_packs[system], re_run, user_id, fully_manual_pack_drug)
            if system_packs[system]:
                PackDetails.update(batch_id=batch_id, system_id=system) \
                    .where(PackDetails.id << system_packs[system]).execute()
                if not batch_present:
                    PackDetails.db_update_pack_order_no({
                        'pack_ids': ','.join(list(map(str, system_packs[system]))),
                        'order_nos': ','.join(list(map(str, pack_orders))),
                        'system_id': system
                    })
            transfers, remove_locations, canister_transfers, reserved_canisters = transfer_canister_recommendation(
                transfers, canister_data, robot_dict)
            save_transfers(transfers, batch_id)
            reserved_batch_canisters[batch_id] = reserved_canisters
        ReservedCanister.db_save(reserved_batch_canisters)
    logger.info("recommendations: {}".format(recommendations))


@log_args_and_response
@validate(required_fields=['pack_distribution', 'company_id', 'user_id'])
def _save_distributed_packs(distribution_info):
    """
    Internal function to distribute packs.
    This will be used to return python data types
    instead of json so multiple apis can be written on this function.
    :param distribution_info: dict
    :return:
    """
    batch_present = distribution_info.get('batch_present', False)
    # batch_present: do not create batch record as already present.
    # If False, new batch will be created and assigned to these packs
    pack_distribution = distribution_info["pack_distribution"]
    company_id = distribution_info["company_id"]
    user_id = distribution_info['user_id']
    split_function_id = distribution_info.get('split_function_id', None)
    re_run = False
    pack_distributor = PackDistributor(company_id=company_id, batch_packs=pack_distribution,
                                       split_function_id=split_function_id, dry_run=False)
    recommendations = pack_distributor.get_recommendation()

    # re use of intermediate artifacts of pack distribution
    robots_data = pack_distributor.robots_data
    pack_manual = pack_distributor.pack_manual
    canister_data = pack_distributor.canister_data
    cache_drug_data = pack_distributor.cache_drug_data
    fully_manual_pack_drug = pack_distributor.fully_manual_pack_drug
    batch_names = pack_distributor.batch_names
    batch_ids = pack_distributor.batch_ids
    system_packs = pack_distributor.system_packs
    robot_dict = pack_distributor.robot_dict
    logger.info("recommendation {}".format(recommendations))

    with db.transaction():

        reserved_batch_canisters = dict()
        for system, data in recommendations.items():
            _max_order_no = PackDetails.db_max_order_no(system)
            pack_orders = list(range(_max_order_no + 1, _max_order_no + len(system_packs[system]) + 1))
            if not batch_ids[system]:
                batch = BaseModel.db_create_record({
                    'name': batch_names[system],
                    'system_id': system,
                    'status': settings.BATCH_PENDING,
                    'created_by': user_id
                }, BatchMaster, get_or_create=False)
                batch_id = batch.id
            else:
                batch_id = batch_ids[system]
            transfers, analysis = data['canister_transfer_info_dict'], data['analysis']
            logger.info('transfers_before_save_to_db:{}'.format(transfers))
            logger.info('analysis_before_save_to_db:{}'.format(analysis))
            robot_ids = list(robot_dict.keys())
            logger.info("analysis {}".format(analysis))
            batch_id, _ = save_analysis(analysis, pack_manual, canister_data, cache_drug_data, batch_id,
                                        system_packs[system], re_run, user_id, fully_manual_pack_drug)
            if system_packs[system]:
                PackDetails.update(batch_id=batch_id, system_id=system) \
                    .where(PackDetails.id << system_packs[system]).execute()
                if not batch_present:
                    PackDetails.db_update_pack_order_no({
                        'pack_ids': ','.join(list(map(str, system_packs[system]))),
                        'order_nos': ','.join(list(map(str, pack_orders))),
                        'system_id': system
                    })
            transfers, remove_locations, canister_transfers, reserved_canisters = transfer_canister_recommendation(
                transfers, canister_data, robot_dict)
            save_transfers(transfers, batch_id)
            reserved_batch_canisters[batch_id] = reserved_canisters
        ReservedCanister.db_save(reserved_batch_canisters)
    logger.info("recommendations: {}".format(recommendations))


@log_args_and_response
def check_pending_canister_transfers(system_id: int) -> list:
    """
    Function to check if canister tx is pending for any batch or not
    @return: list
    """
    try:
        query = CanisterTxMeta.select(CanisterTxMeta, DeviceMaster.system_id.alias("pending_device_system_id")).dicts() \
            .join(BatchMaster, on=BatchMaster.id == CanisterTxMeta.batch_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
            .where(CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE,
                   BatchMaster.system_id == system_id)

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_delivery_date_dao(update_dict):
    delivery_date_set = set()
    clauses = list()
    start_date = update_dict.get('start_date', None)

    try:
        PackDetailsAlias = PackDetails.alias()

        # used in case of pack generation when delivery date is to be assigned to new packs only
        update_existing_delivery_date = update_dict.get('update_existing', False)
        current_date = get_current_date_time_as_per_time_zone()
        formatted_current_date = datetime.datetime.combine(current_date.date(), datetime.time())
        clauses.append((PackDetailsAlias.pack_status << [settings.PENDING_PACK_STATUS, settings.MANUAL_PACK_STATUS]))

        clauses.append(
            (PackDetailsAlias.batch_id.is_null(True)) |
            ((PackUserMap.id.is_null(True)) &
             (PackDetailsAlias.pack_status == settings.MANUAL_PACK_STATUS))
        )
        if 'facility_id_list' in update_dict:
            clauses.append((PatientMaster.facility_id << update_dict['facility_id_list']))
        if 'patient_ids' in update_dict:
            clauses.append((PatientMaster.id << update_dict['patient_ids']))
        if 'patient_schedule_ids' in update_dict:
            logger.info(update_dict['patient_schedule_ids'])
            clauses.append((PatientSchedule.id << update_dict['patient_schedule_ids']))
        if not update_existing_delivery_date:
            clauses.append((PackHeader.scheduled_delivery_date.is_null(True)))

        clauses.append(PackDetails.pack_status.not_in(
            [settings.DELETED_PACK_STATUS, settings.DONE_PACK_STATUS, settings.FILL_ERROR_STATUS,
             settings.FIXED_ERROR_STATUS, constants.PRN_DONE_STATUS]))

        query = PackDetails.select(PatientSchedule,
                                   FacilitySchedule,
                                   PackDetails,
                                   fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.consumption_start_date)).alias('min_consumption_start_date'),
                                   PackDetails.id.alias('pack_id'),
                                   PackHeader.id.alias('pack_header_id'),
                                   fn.CONCAT(PackDetails.id).alias('pack_ids')).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PatientSchedule, on=((PatientSchedule.patient_id == PatientMaster.id) & (
                PatientSchedule.facility_id == PatientMaster.facility_id))) \
            .join(PackDetailsAlias, on=PackDetailsAlias.pack_header_id == PackHeader.id) \
            .join(FacilitySchedule, JOIN_LEFT_OUTER, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetailsAlias.batch_id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetailsAlias.id) \
            .where(*clauses) \
            .group_by(PackHeader.id)
        logger.info(f"In update_delivery_date_dao, query: {query}")
        count = 0
        for record in query:
            delivery_data = dict()
            date_list = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in record["min_consumption_start_date"].split(',')]
            new_date_list = [date for date in date_list if date >= formatted_current_date]
            if not new_date_list:
                delivery_data['next_delivery_date'] = None
            else:
                record["min_consumption_start_date"] = min(new_date_list)
                if record["min_consumption_start_date"] >= formatted_current_date:
                    if record['start_date'] > record['min_consumption_start_date']:
                        record['start_date'] = datetime.datetime.strptime(get_current_date(), '%Y-%m-%d')
                    delivery_data = get_expected_delivery_date(record['min_consumption_start_date'],
                                                               record['start_date'],
                                                               record['delivery_date_offset'], record['fill_cycle'],
                                                               record['days'])
                else:
                    delivery_data['next_delivery_date'] = None
            if (not delivery_data['next_delivery_date'] and start_date) or update_dict.get("current_schedule"):
                delivery_data['next_delivery_date'] = start_date
            PackHeader.update(scheduled_delivery_date=delivery_data['next_delivery_date']) \
                .where(PackHeader.id == record['pack_header_id']).execute()
            if delivery_data['next_delivery_date']:
                status = sync_delivery_dates_with_ips(pack_header_id=record['pack_header_id'], delivery_date=delivery_data['next_delivery_date'])
            logger.info('updated_delivery_date {} for {} '.format(delivery_data['next_delivery_date'], record))
            count = count + 1
            delivery_date_set.add(delivery_data["next_delivery_date"])
        logger.info("delivery_date_set: " + str(delivery_date_set))

        return delivery_date_set
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_delivery_without_schedule_dao(update_dict):
    """
    # Get all patient schedules with no delivery dates of delivery dates of past.
    # Change it with current or given date.

    :param update_dict:
    :return:
        >>> update_delivery_date_dao()
    """
    delivery_date_set = set()
    clauses = list()
    start_date = update_dict.get('start_date')

    try:
        PackDetailsAlias = PackDetails.alias()

        # used in case of pack generation when delivery date is to be assigned to new packs only
        update_existing_delivery_date = update_dict.get('update_existing', False)
        current_date = get_current_date_time_as_per_time_zone()
        formatted_current_date = datetime.datetime.combine(current_date.date(), datetime.time())
        clauses.append((PackDetailsAlias.pack_status << [settings.PENDING_PACK_STATUS, settings.MANUAL_PACK_STATUS]))

        clauses.append(
            (PackDetailsAlias.batch_id.is_null(True)) |
            ((PackUserMap.id.is_null(True)) &
             (PackDetailsAlias.pack_status == settings.MANUAL_PACK_STATUS))
        )
        if 'facility_id_list' in update_dict:
            clauses.append((PatientMaster.facility_id << update_dict['facility_id_list']))
        if 'patient_ids' in update_dict:
            clauses.append((PatientMaster.id << update_dict['patient_ids']))
        if 'patient_schedule_ids' in update_dict:
            logger.info(update_dict['patient_schedule_ids'])
            clauses.append((PatientSchedule.id << update_dict['patient_schedule_ids']))

        clauses.append((PackHeader.scheduled_delivery_date.is_null(True)) | (
                PackHeader.scheduled_delivery_date < formatted_current_date))

        clauses.append(PackDetails.pack_status.not_in(
            [settings.DELETED_PACK_STATUS, settings.DONE_PACK_STATUS]))

        query = PackDetails.select(PatientSchedule,
                                   FacilitySchedule,
                                   PackDetails,
                                   fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.consumption_start_date)).alias('min_consumption_start_date'),
                                   PackDetails.id.alias('pack_id'),
                                   PackHeader.id.alias('pack_header_id'),
                                   fn.CONCAT(PackDetails.id).alias('pack_ids')).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PatientSchedule, on=((PatientSchedule.patient_id == PatientMaster.id) & (
                PatientSchedule.facility_id == PatientMaster.facility_id))) \
            .join(PackDetailsAlias, on=PackDetailsAlias.pack_header_id == PackHeader.id) \
            .join(FacilitySchedule, JOIN_LEFT_OUTER, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetailsAlias.batch_id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetailsAlias.id) \
            .where(*clauses) \
            .group_by(PackHeader.id)
        logger.info(f"In update_delivery_without_schedule_dao, query: {query}")
        for record in query:

            PackHeader.update(scheduled_delivery_date=start_date) \
                .where(PackHeader.id == record['pack_header_id']).execute()
            logger.info('update_delivery_without_schedule_dao {} for {} '.format(start_date, record))
            delivery_date_set.add(start_date)
        logger.info("delivery_date_set: " + str(delivery_date_set))

        return delivery_date_set
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(f"Error in update_delivery_without_schedule_dao {e}", exc_info=True)
        raise e


@log_args_and_response
def get_pack_id_list_by_status_and_system(status: list, system_id: int, pack_id_list: Optional[list] = None) -> list:
    """
    get pack id list for given status
    """
    pack_ids_list: list = list()
    try:

        if pack_id_list is None:
            query = PackDetails.select(PackDetails.id).join(PackQueue, on=PackQueue.pack_id==PackDetails.id).where(
                PackDetails.pack_status << status, PackDetails.system_id == system_id) \
                .group_by(PackDetails.id)
        else:
            query = PackDetails.select(PackDetails.id).join(PackQueue, on=PackQueue.pack_id==PackDetails.id).where(
                (PackDetails.id << pack_id_list) & (PackDetails.pack_status << status)) \
                .group_by(PackDetails.id)
        for record in query.dicts():
            pack_ids_list.append(record['id'])

        return pack_ids_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_id_list_by_status {}".format(e))
        raise e


@log_args_and_response
def get_filled_packs_count_for_system(system_id: int):
    """
    get filled pack count for latest batch
    :return: bool
    """
    try:
        query = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.system_id == system_id,
                                                                   PackDetails.pack_status << (
                                                                       [settings.DONE_PACK_STATUS,
                                                                        settings.PROCESSED_MANUALLY_PACK_STATUS]),
                                                                   PackDetails.filled_at.not_in(
                                                                       [settings.FILLED_AT_POST_PROCESSING]))
        filled_pack_count = query.scalar()
        return filled_pack_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_filled_packs_count_for_system {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_filled_packs_count_for_system: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_filled_packs_count_for_system {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_filled_packs_count_for_system: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def db_get_current_location_details_by_canisters(canister_ids):
    try:
        canister_location_dict = {}
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                      CanisterMaster.active,
                                      LocationMaster.id,
                                      LocationMaster.display_location,
                                      LocationMaster.location_number,
                                      LocationMaster.is_disabled.alias('is_location_disabled'),
                                      LocationMaster.device_id,
                                      LocationMaster.quadrant,
                                      LocationMaster.container_id.alias('drawer_id'),
                                      DeviceMaster.name.alias('device_name'),
                                      DeviceMaster.serial_number.alias('device_serial_number'),
                                      DeviceMaster.device_type_id,
                                      DeviceMaster.ip_address.alias('device_ip_address'),
                                      ContainerMaster.serial_number,
                                      ContainerMaster.shelf,
                                      ContainerMaster.drawer_level,
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      ContainerMaster.drawer_name) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.id << canister_ids)
        for record in query.dicts():
            canister_location_dict[record['canister_id']] = {'display_location': record['display_location'],
                                                             'location_number': record['location_number'],
                                                             'is_location_disabled': record['is_location_disabled'],
                                                             'quadrant': record['quadrant'],
                                                             'device_name': record['device_name'],
                                                             'device_type_id': record['device_type_id'],
                                                             'device_id': record['device_id'],
                                                             'location_id': record['id'],
                                                             'active': record['active'],
                                                             "serial_number": record['serial_number'],
                                                             "device_serial_number": record['device_serial_number'],
                                                             "shelf": record['shelf'],
                                                             "ip_address": record['ip_address'],
                                                             "secondary_ip_address": record[
                                                                 'secondary_ip_address'],
                                                             "drawer_name": record['drawer_name'],
                                                             "drawer_id": record['drawer_id'],
                                                             "drawer_level": record['drawer_level'],
                                                             "device_ip_address": record["device_ip_address"]
                                                             }
        return canister_location_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise e


@log_args_and_response
def get_packs_from_pack_queue_for_system(system_id):
    try:
        query = PackQueue.select(PackQueue.pack_id).dicts() \
                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                .where(PackDetails.system_id == system_id)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_packs_from_pack_queue_for_system {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_packs_from_pack_queue_for_system {}".format(e))
        raise e


@log_args_and_response
def get_system_id_from_pack_queue(company_id):
    try:
        system_ids = []

        query = PackQueue.select(PackDetails.system_id).dicts() \
                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                .where(PackDetails.company_id == company_id) \
                .group_by(PackDetails.system_id)

        for data in query:
            system_ids.append(data["system_id"])

        return system_ids

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_packs_from_pack_queue_for_system {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_packs_from_pack_queue_for_system {}".format(e))
        raise e


@log_args_and_response
def db_get_progress_filling_left_pack_ids(company_id=None):
    """
    Replace progress filling left pack ids by batch id
    @param batch_id:
    @return:
    """
    try:
        pack_id_query = PackDetails.select(PackDetails,
                                           PackDetails.id.alias('pack_id')).dicts()\
            .join(PackQueue, on=PackQueue.pack_id==PackDetails.id)\
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(PackDetails.pack_status == settings.PROGRESS_PACK_STATUS,
                   SlotTransaction.id.is_null(True))
        if company_id:
            pack_id_query = pack_id_query.where(PackDetails.company_id == company_id)

        pack_ids = [record['pack_id'] for record in pack_id_query]
        logger.info("In db_get_progress_filling_left_pack_ids, pack_id_query {}".format(pack_id_query))
        return pack_ids
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_progress_filling_left_pack_ids {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_progress_filling_left_pack_ids {}".format(e))
        raise e



@log_args_and_response
def add_pharmacy_data_dao(pharmacy_info):
    """
    Function to add pharmacy data in pharmacy master table
    @param pharmacy_info:
    @return:
    """
    try:
        return PharmacyMaster.db_create_record(pharmacy_info,
                                               PharmacyMaster,
                                               get_or_create=False )
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_pharmacy_data_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in add_pharmacy_data_dao {}".format(e))
        raise e


@log_args_and_response
@validate(required_fields=["dropped_qty"])
def update_inventory_v2(inventory_info):
    """
    Updates canister quantity using dropped quantity information.

    :param inventory_info: dict {"dropped_qty": {canister_id: pills dropped from canister}}
    :return: str
    """
    try:
        dropped_qty = inventory_info["dropped_qty"]
        canister_id_list = list(dropped_qty.keys())
        if canister_id_list:
            query = CanisterMaster.select(
                CanisterMaster.id,
                CanisterMaster.available_quantity
            ).where(CanisterMaster.id << canister_id_list)
            with db.transaction():
                for record in query:
                    updated_quantity = record.available_quantity - int(dropped_qty[str(record.id)])
                    available_qty = updated_quantity if updated_quantity > 0 else 0
                    update_dict = {"available_quantity": available_qty}
                    if not available_qty:
                        update_dict["expiry_date"] = None
                    status = CanisterMaster.update(**update_dict).where(CanisterMaster.id == record.id).execute()
                    logger.info(f"In update_inventory_v2, status: {status}")

        return create_response(True)
    except (IntegrityError, InternalError, KeyError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(1020)


def update_set_last_seen(pack_ids):
    try:
        token = get_token()
        user_details = get_current_user(token)
        query = PackDetails.select(
            UniqueDrug.id, DrugDetails.id.alias('details_id'), PackDetails.company_id
        ).distinct().dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc),
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .where(PackDetails.id << pack_ids)
        for row in query:
            now = datetime.datetime.now()
            DrugDetails.db_update_or_create({"unique_drug_id": row["id"], "company_id": row["company_id"]},
                                            {"last_seen_by": user_details["id"],
                                             "last_seen_date": now})
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return False
    return True


@log_args_and_response
def get_rx_wise_ndc_fill(pack_id: int, pack_and_display_ids: Dict[int, int]):
    rx_dict: Dict[str, Dict[str, Any]] = defaultdict(dict)
    temp_dict: Dict[str, Dict[str, Any]] = dict()
    ndc_dict: Dict[str, Any] = dict()
    pack_id_from_display: int = 0
    clauses = list()
    rx_clauses = list()
    rx_key_label: str = "rxid"
    ndc_list_key_label: str = "ndcs"
    ndc_key_label: str = "ndc"
    qty_key_label: str = "qty"
    case_label: str = 'case_id'
    rx_dict_list: List[Dict[str, Any]] = list()

    try:
        DrugMasterAlias = DrugMaster.alias()
        DrugMasterAlias2 = DrugMaster.alias()

        for key, value in pack_and_display_ids.items():
            if int(pack_id) == value:
                pack_id_from_display = key

        clauses.append((PackDetails.pack_display_id == pack_id))
        clauses.append(DrugTracker.drug_quantity > 0)
        if pack_id_from_display > 0:
            clauses.append(PackDetails.id == pack_id_from_display)

        # TODO : uncomment below code if IPS req. start date and end date for rx_no
        # rx_sd_ed = dict()
        # query = SlotHeader.select(PatientRx.pharmacy_rx_no,
        #                           SlotHeader.hoa_time,
        #                           fn.MIN(SlotHeader.hoa_date).alias("start_date"),
        #                           fn.MAX(SlotHeader.hoa_date).alias("end_date")).dicts() \
        #     .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
        #     .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
        #     .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        #     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
        #     .where(functools.reduce(operator.and_, clauses)) \
        #     .group_by(PatientRx.pharmacy_rx_no, SlotHeader.hoa_time)
        #
        # for data in query:
        #     if not rx_sd_ed.get(data["pharmacy_rx_no"]):
        #         rx_sd_ed[data["pharmacy_rx_no"]] = {}
        #     if not rx_sd_ed[data["pharmacy_rx_no"]].get(str(data["hoa_time"])):
        #         rx_sd_ed[data["pharmacy_rx_no"]][str(data["hoa_time"])] = {"start_date": str(data["start_date"]),
        #                                                                    "end_date": str(data["end_date"])}
        # logger.info(f"In get_rx_wise_ndc_fill, rx_sd_ed: {rx_sd_ed}")

        logger.debug("Prepare the list of Rxs for the selected pack along with total required qty per Rx...")
        pack_rx_qty_query = PackDetails.select(PackDetails.id.alias("pack_id"),
                                               PatientRx.id.alias("patient_rx_id"),
                                               DrugMaster.ndc.alias("ndc"),
                                               fn.sum(SlotDetails.quantity).alias("total_slot_quantity")).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugTracker, on=DrugTracker.slot_id == SlotDetails.id)    \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(PackDetails.id, PatientRx.id)

        for rx_record in pack_rx_qty_query:
            rx_clauses = clauses + [PatientRx.id == rx_record["patient_rx_id"]]

            # TODO -- Handle the scenario for DrugTracker --> is_deleted field when it is ready with changes related
            #  to deferring any pack

            logger.debug("Get the details of NDC wise qty from Drug Tracker and Slot Details...")
            query = PackDetails.select(PackDetails.id, PatientRx.pharmacy_rx_no,
                                       fn.IF(DrugTracker.drug_id, DrugMasterAlias.ndc,
                                             DrugMaster.ndc).coerce(False).alias("ndc"),
                                       fn.SUM(fn.IF(DrugTracker.drug_id, DrugTracker.drug_quantity,
                                                    SlotDetails.quantity)).alias('total_ndc_qty'),
                                       fn.IF(CanisterTracker.id.is_null(True), DrugTracker.case_id,
                                             CanisterTracker.case_id).alias("case_id"),
                                       CanisterTracker.id.alias("canister_tracker_id"),
                                       DrugMasterAlias2.ndc.alias("original_ndc"),
                                       PackDetails.store_type
                                       ).dicts() \
                .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
                .join(DrugTracker, JOIN_LEFT_OUTER,
                      on=((SlotDetails.id == DrugTracker.slot_id) & (DrugTracker.is_overwrite == 0))) \
                .join(CanisterTracker, JOIN_LEFT_OUTER, on=DrugTracker.canister_tracker_id == CanisterTracker.id) \
                .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=DrugTracker.drug_id == DrugMasterAlias.id) \
                .join(DrugMasterAlias2, JOIN_LEFT_OUTER, on=DrugMasterAlias2.id == SlotDetails.original_drug_id)   \
                .where(functools.reduce(operator.and_, rx_clauses)) \
                .group_by(fn.IF(DrugTracker.drug_id, DrugTracker.drug_id, SlotDetails.drug_id),
                          fn.IF(CanisterTracker.id.is_null(True), DrugTracker.case_id, CanisterTracker.case_id))

            total_slot_quantity = rx_record["total_slot_quantity"]

            logger.debug("Following block will get the data of NDCs and its quantity for selected Rx from "
                         "Drug Tracker and Slot Details...")
            for record in query:
                canister_fill = False
                case_id = record['case_id']
                if record["canister_tracker_id"]:
                    canister_fill = True
                if record["total_ndc_qty"] > total_slot_quantity:
                    logger.debug("Situation: When total quantity from Drug Tracker is more than the total required as "
                                 "per Slot information...")

                    ndc_dict = {ndc_key_label: record["ndc"],
                                "case_id": record['case_id'],
                                "case_qty": str(total_slot_quantity),
                                "canister_filled": canister_fill,
                                "original_ndc": str(record["original_ndc"]),
                                "store_type": 1 if record["store_type"] in [constants.STORE_TYPE_RETAIL] else 0
                                }
                    # case_data = {
                    #     "case_id": case_id,
                    #     "case_quantity": str(total_slot_quantity)
                    # }
                    # ndc_dict['case_data'] = [case_data]
                else:
                    ndc_dict = {ndc_key_label: record["ndc"],
                                "case_id": case_id,
                                "case_qty": str(record["total_ndc_qty"]),
                                "canister_filled": canister_fill,
                                "original_ndc": str(record["original_ndc"]),
                                "store_type": 1 if record["store_type"] in [constants.STORE_TYPE_RETAIL] else 0
                                }
                    # case_data = {
                    #     "case_id": case_id,
                    #     "case_quantity": str(record["total_ndc_qty"])
                    # }
                    # ndc_dict['case_data'] = [case_data]

                if record["pharmacy_rx_no"] not in rx_dict:
                    rx_dict[record["pharmacy_rx_no"]].update(
                        {rx_key_label: record["pharmacy_rx_no"],
                         ndc_list_key_label: [ndc_dict]},)

                    # TODO : uncomment below code if IPS req. start date and end date for rx_no
                    # rx_dict[record["pharmacy_rx_no"]].update(
                    #     {rx_key_label: record["pharmacy_rx_no"],
                    #      ndc_list_key_label: [ndc_dict],
                    #      "hoa_time_date": rx_sd_ed.get(record["pharmacy_rx_no"], {})})
                else:
                    temp_dict = rx_dict[record["pharmacy_rx_no"]]
                    temp_dict[ndc_list_key_label].append(ndc_dict)
                    # for index, item in enumerate(temp_dict['ndcs']):
                    #     if item['ndc'] == record['ndc']:
                    #         temp_dict[ndc_list_key_label][index]['case_data'].append(ndc_dict['case_data'][0])
                    # rx_dict[record["pharmacy_rx_no"]].update(temp_dict)

                total_slot_quantity = total_slot_quantity - record["total_ndc_qty"]
                if total_slot_quantity <= 0:
                    break

            if total_slot_quantity > 0:
                logger.debug("Situation: When total quantity from Drug Tracker is less than the total required as "
                             "per Slot information with following reason...")
                logger.debug("** If any Slot is partially filled with Robot then remaining qty needs to be taken from "
                             "Drug associated with Slot Details.")

                temp_dict = rx_dict[record["pharmacy_rx_no"]]
                ndc_qty_list = temp_dict["ndcs"]
                for ndc_details in ndc_qty_list:
                    if ndc_details["ndc"] == rx_record["ndc"]:
                        logger.debug("-- If drug from Drug Tracker already matches with Slot information then just "
                                     "add up the quantity...")
                        ndc_details["qty"] = str(Decimal(ndc_details["case_qty"]) + total_slot_quantity)
                        total_slot_quantity = 0
                        break

                if total_slot_quantity > 0:
                    logger.debug("-- If drug from Drug Tracker does not match with Slot information and we still have "
                                 "remaining qty to match with total required as per Slot information, then apply the "
                                 "remaining qty based on Drug from Slot Details...")
                    ndc_dict = {ndc_key_label: rx_record["ndc"],
                                qty_key_label: str(total_slot_quantity),
                                case_label: None
                                }
                    temp_dict[ndc_list_key_label].append(ndc_dict)
                    rx_dict[record["pharmacy_rx_no"]].update(temp_dict)

            logger.debug("Rx List with NDC: {}".format(rx_dict))
            # if rx_dict:
            #     rx_dict_list.append(rx_dict[record["pharmacy_rx_no"]])

        return list(rx_dict.values())
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_pack_slotwise_drugs(pack_list):
    try:

        pack_slot_drug_dict = dict()
        pack_slot_detail_drug_dict = dict()
        pack_drug_half_pill_slots_dict = dict()

        query = PackDetails.select(PackDetails.id,
                                   fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug_id'),
                                   PackGrid.slot_number, SlotDetails.id.alias('slot_id'), SlotDetails.quantity) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list)

        for record in query.dicts():
            if record['id'] not in pack_slot_drug_dict.keys():
                pack_slot_drug_dict[record['id']] = {}
                pack_slot_detail_drug_dict[record['id']] = {}
                pack_drug_half_pill_slots_dict[record['id']] = {}
            if record['slot_number'] not in pack_slot_drug_dict[record['id']].keys():
                pack_slot_drug_dict[record['id']][record['slot_number']] = set()
                pack_slot_detail_drug_dict[record['id']][record['slot_number']] = record['slot_id']
            if record['drug_id'] is not None:
                pack_slot_drug_dict[record['id']][record['slot_number']].add(record['drug_id'])
            if record['drug_id'] not in pack_drug_half_pill_slots_dict[record['id']].keys():
                pack_drug_half_pill_slots_dict[record['id']][record['drug_id']] = list()
            if record['slot_number'] not in pack_drug_half_pill_slots_dict[record['id']][record['drug_id']] \
                    and record['quantity'] == 0.5:
                    # and not float(record['quantity']).is_integer():
                pack_drug_half_pill_slots_dict[record['id']][record['drug_id']].append(record['slot_number'])

        return pack_slot_drug_dict, pack_slot_detail_drug_dict, pack_drug_half_pill_slots_dict
    except Exception as e:
        logger.info(e)
        return e


@log_args_and_response
def get_canister_skipped_drug_qty_per_slot(pack_id: int):
    """
    to get the skipped drug qty for given pack slot wise.
    note : if same drug skipped for canister and mfd canister then that drug is not consider in this function.
    :param pack_id:
    :return:
    """

    canister_skipped_qty_dicts = {}

    try:

        query = PackAnalysis.select(PackGrid.slot_number,
                                    fn.sum(SlotDetails.quantity).alias('canister_skipped_drug_qty')).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(SlotDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id).dicts() \
            .join(SlotTransaction, JOIN_LEFT_OUTER, SlotTransaction.slot_id == SlotDetails.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .where(PackAnalysis.batch_id == PackDetails.batch_id,
                   PackAnalysis.pack_id == pack_id,
                   ((PackAnalysisDetails.status != constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)|(PackAnalysisDetails.location_number.is_null(True))),
                   MfdAnalysisDetails.id.is_null(True),
                   SlotTransaction.id.is_null(True)) \
            .group_by(PackGrid.slot_number)

        for record in query:
            canister_skipped_qty_dicts[record['slot_number']] = record['canister_skipped_drug_qty']
        logger.info(f"canister skipped drug qty in slot of given pack_id: {canister_skipped_qty_dicts}")

        return canister_skipped_qty_dicts
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error(e)


@log_args_and_response
def get_dropped_quadrant_data_slot_wise(pack_id):
    """
    to get the quadrants from drug dropped for given pack slot wise
    """
    quadrant_dict = {}
    try:
        query = SlotHeader.select(PackGrid.slot_number,
                                  fn.GROUP_CONCAT((fn.DISTINCT(PackAnalysisDetails.quadrant))).coerce(
                                      False).alias(
                                      "canister_quadrant"),
                                  fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.dest_quadrant)).coerce(False).alias(
                                      "mfd_canister_quadrant")).dicts() \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.slot_id == PackAnalysisDetails.slot_id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(PackGrid, JOIN_LEFT_OUTER, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .where(SlotHeader.pack_id == pack_id,
                   (((MfdAnalysis.status_id == constants.MFD_CANISTER_DROPPED_STATUS) |
                     (MfdAnalysis.id.is_null(True))) |
                    SlotTransaction.id.is_null(False))) \
            .group_by(PackGrid.slot_number)

        for data in query:
            quadrants = []
            mfd_quadrants = []

            logger.info(f"quadrant_data: {data}")

            if data["canister_quadrant"]:
                quadrants = list(map(int, (data["canister_quadrant"]).split(",")))
            if data["mfd_canister_quadrant"]:
                mfd_quadrants = list(map(int, (data["mfd_canister_quadrant"]).split(",")))
            quadrants.extend(mfd_quadrants)

            quadrant_dict[data["slot_number"]] = list(set(quadrants))

        logger.info(f"quadrant_dict: {quadrant_dict}")
        return quadrant_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error(e)


def insert_data_in_pack_verification_and_pack_verification_details(pack_id, dict_slot_info, compare_qty_dict,
                                                                   dropped_qty_dict,
                                                                   predicted_qty_dict, pack_verified_status, user_id):
    """
    This function is insert data in pack verification and pack verification details
    """

    insert_list = []
    status = None

    try:
        need_to_insert = True
        query = PackVerification.select(PackVerification.id).dicts().where(PackVerification.pack_id == pack_id)
        for data in query:
            logger.info(
                f"In insert_data_in_pack_verification_and_pack_verification_details, data already inserted for this pack: {pack_id}")
            return None

        if need_to_insert:

            with db.transaction():

                # insert data in pack_verification table for given pack_id
                pack_dict = {"pack_id": pack_id,
                             "pack_verified_status": pack_verified_status,
                             "created_by": user_id if user_id else 1,
                             "created_date": get_current_date_time()}

                status = PackVerification.insert(**pack_dict).execute()

                logger.info(
                    "In insert_data_in_pack_verification_and_pack_verification_details, PackVerification insert status: {}".format(
                        status))

                # get pack_verification_id to insert data in pack_verification_details
                pack_verification_id = \
                PackVerification.select(PackVerification.id).dicts().where(PackVerification.pack_id == pack_id).get()['id']

                logger.info(
                    "In insert_data_in_pack_verification_and_pack_verification_details, pack_verification_id: {}".format(
                        pack_verification_id))

                for k in dict_slot_info.keys():
                    slot_data_dict = {}
                    slot_data_dict['pack_verification_id'] = pack_verification_id
                    slot_data_dict['slot_header_id'] = dict_slot_info[k]['slot_header_id']
                    slot_data_dict['colour_status'] = dict_slot_info[k]['slot_colour_status']
                    slot_data_dict['compare_quantity'] = compare_qty_dict[k]
                    slot_data_dict['dropped_quantity'] = dropped_qty_dict[k]
                    slot_data_dict['predicted_quantity'] = predicted_qty_dict[k]
                    if user_id:
                        slot_data_dict['created_by'] = user_id
                    slot_data_dict['created_date'] = get_current_date_time()

                    insert_list.append(slot_data_dict)

                logger.info(
                    "In insert_data_in_pack_verification_and_pack_verification_details, PackVerificationDetails insert data list: {}".format(
                        insert_list))

                # insert data in pack_verification_details
                if insert_list:
                    status = PackVerificationDetails.insert_many(insert_list).execute()

            return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        # logger.error(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in insert_data_in_pack_verification_and_pack_verification_details: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")


@log_args_and_response
def get_patient_pack_data_by_batch_id(batch_id: int or None = None, pack_list: list or None = None, patient_id_list: list or None = None):
    """
        This function to get patient packs ids by batch id and pack ids
        @param patient_id_list:
        @param pack_list:
        @param batch_id:
        @return:
    """
    try:
        PackDetailsAlias = PackDetails.alias()
        query = PackDetails.select(PackDetails.id.alias('pack_id'),
                                   PackDetails.pack_status,
                                   PatientMaster.id.alias('patient_id')).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id)
        if pack_list:
            query = query.join(PackDetailsAlias, on=PackDetailsAlias.pack_header_id == PackHeader.id) \
                        .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                    .where(PackDetailsAlias.id.in_(pack_list))

        if patient_id_list:
            query = query.where(PatientMaster.id.in_(patient_id_list), PackDetails.batch_id == batch_id)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_patient_pack_data_by_pack_list_batch_id {}".format(e))
        raise e


@log_args_and_response
def get_mfd_analysis_status(pack_list: list):
    """
        Function to get packs having mfd canisters or rts required status
    """
    mfd_status_dict = dict()
    query = MfdAnalysisDetails.select(PackDetails.id.alias("pack_id"), MfdAnalysis.status_id.alias("status")).dicts()\
        .join(MfdAnalysis, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id)\
        .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)\
        .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
        .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
        .where(PackDetails.id << pack_list,
               ((MfdAnalysis.status_id == MFD_CANISTER_RTS_REQUIRED_STATUS) |
                (MfdAnalysis.status_id == MFD_CANISTER_MVS_FILLING_REQUIRED)))\
        .group_by(PackDetails.id).dicts()

    logger.info('query = {}'.format(query))
    for response in query:
        mfd_status_dict[response["pack_id"]] = response["status"]
    return mfd_status_dict


@log_args_and_response
def get_manual_packs_patient_data(pack_list: list):
    """
        This function to get manual packs patient data to revert batch from manual fill flow
        @param pack_list:
        @return:
    """
    try:
        PackDetailsAlias = PackDetails.alias()
        query = PackDetails.select(PackDetails.id.alias('pack_id'),
                                   PackDetails.pack_status,
                                   PatientMaster.id.alias('patient_id')).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackDetailsAlias, on=PackDetailsAlias.pack_header_id == PackHeader.id)
        if pack_list:
            query = query.where(PackDetailsAlias.id.in_(pack_list))
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_manual_pending_patient_ids {}".format(e))
        raise e


@log_args_and_response
def create_pack_status_tracker_dao(pack_status_tracker_list: list):
    """
        This function to create record in pack status tracker
        @param pack_status_tracker_list:
        @return:
    """
    try:
        # create record for pack status tracker
        status = PackStatusTracker.db_track_status(pack_status_tracker_list)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("Error in create_pack_status_tracker_dao {}".format(e))
        raise e


def get_slot_details_data(pack_id):
    try:
        for record in SlotHeader.select(PackDetails.pack_display_id, SlotHeader.hoa_date, SlotHeader.hoa_time,
                                        PackGrid.slot_row,
                                        PackGrid.slot_column, PatientRx.pharmacy_rx_no, SlotDetails.quantity) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(PackDetails, on=SlotHeader.pack_id == PackDetails.id) \
                .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .dicts().where(SlotHeader.pack_id == pack_id):
            record["hoa_date"] = record["hoa_date"].strftime('%Y-%m-%d')
            record["hoa_time"] = record["hoa_time"].strftime('%H:%M:%S')
            record["pharmacy_rx_no"] = record["pharmacy_rx_no"].strip()
            record["quantity"] = float(record["quantity"])
            yield record
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_slot_details_data {}".format(e))
        raise e


def insert_slot_data_dao(slot_details_list: list):
    """
    This function to insert slot data
    @param slot_details_list:
    @return:
    """
    try:
        status = SlotDetails.insert_many(slot_details_list).execute()
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("Error in insert_slot_data_dao {}".format(e))
        raise e


@log_args_and_response
def insert_pack_user_map_data_dao(pack_id, user_id, date, created_by=None):
    try:
        status = PackUserMap.db_insert_pack_user_map_data(pack_id=pack_id, user_id=user_id, date=date, created_by=created_by)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("Error in insert_pack_user_map_data_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_pack_user_map_old_template(ext_change_rx_data):
    old_packs_assigned_user_id: int = 0
    try:
        pack_user_query = ExtChangeRx.select(PackUserMap.assigned_to).dicts()\
            .join(ExtPackDetails, on=ExtChangeRx.id == ExtPackDetails.ext_change_rx_id)\
            .join(PackUserMap, on=ExtPackDetails.pack_id == PackUserMap.pack_id)\
            .where(ExtChangeRx.current_template << ext_change_rx_data["current_template"])\
            .order_by(PackUserMap.id.desc()).get()

        logger.debug("Pack User Query: {}".format(pack_user_query))
        old_packs_assigned_user_id = pack_user_query.get("assigned_to", 0)

        return old_packs_assigned_user_id
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        logger.error("Data does not exists Exception for Function: db_get_pack_user_map_old_template. {}".format(e))
        return 0
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in fetching information from Pack User Map for Old Template: {}".format(e))
        raise e


def create_record_pack_rx_link_dao(data):
    try:
        pack_rx_link_record = BaseModel.db_create_record(data, PackRxLink, get_or_create=False)
        return pack_rx_link_record
    except (InternalError, IntegrityError) as e:
        logger.error("Error in create_record_pack_rx_link_dao {}".format(e))
        raise e


def create_record_slot_dao(data):
    try:
        slot_data = BaseModel.db_create_record(data, SlotHeader, get_or_create=False)
        return slot_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in create_record_pack_rx_link_dao {}".format(e))
        raise e


@log_args_and_response
def get_pack_grid_data_dao(grid_type) -> tuple:
    """
        This function to pack grid data from pack grid table
        @return:
    """
    try:
        pack_grid_row: int = 0
        pack_grid_column: int = 0
        slot_row_column_dict: dict = dict()

        # get pack grid data
        pack_grid_data_query = PackGrid.db_get_pack_grid_data(grid_type)

        for data in pack_grid_data_query:
            # find max number of column and row from pack grid data
            pack_grid_row = data["slot_row"] if pack_grid_row < data["slot_row"] else pack_grid_row
            pack_grid_column = data["slot_column"] if pack_grid_column < data["slot_column"] else pack_grid_column

            slot_row_column_dict[data["slot_number"]] = str(data["slot_row"]) + str(data["slot_column"])

        return slot_row_column_dict, pack_grid_row, pack_grid_column
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_pack_grid_data_dao {}".format(e))
        raise e


@log_args_and_response
def get_max_ext_data(pack_ids):
    try:
        ext_data = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                          ExtPackDetails.pack_id.alias('pack_id'), ExtPackDetails.ext_status_id, PackDetails.pack_status).dicts()\
            .join(PackDetails, on = (PackDetails.id == ExtPackDetails.pack_id)) \
            .where(ExtPackDetails.pack_id << pack_ids) \
            .group_by(ExtPackDetails.pack_id)
        return ext_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_max_ext_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_max_ext_data {}".format(e))
        raise e

@log_args_and_response
def get_pack_slotwise_canister_drugs_(pack_list:list, company_id: int, mfd_drug_id=None):
    try:
        pack_all_slot_drug_dict = dict()
        pack_canister_slot_drug_dict = dict()
        canister_drugs = list()
        mfd_drug_set = set()
        drugs_set = set()
        pack_manual_drugs_set = dict()

        if mfd_drug_id:

            mfd_drugs_query = (MfdAnalysisDetails.select(DrugMaster.concated_fndc_txr_field(sep='##').alias('drug_id'))
                               .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)
                               .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)
                               .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                               .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                               .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                               .where(PackDetails.id.in_(pack_list),
                                      SlotDetails.drug_id.not_in([mfd_drug_id])))
            for record in mfd_drugs_query.dicts():
                mfd_drug_set.add(record['drug_id'])

        canister_drugs_query = CanisterMaster.select(DrugMaster.concated_fndc_txr_field(sep="##").alias('drug_id')).dicts()\
                        .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
                        .where(CanisterMaster.company_id == company_id,
                               CanisterMaster.active == settings.is_canister_active)\
                        .group_by(DrugMaster.concated_fndc_txr_field())

        for record in canister_drugs_query.dicts():
            canister_drugs.append(record['drug_id'])

        query = PackDetails.select(PackDetails.id,
                                   DrugMaster.concated_fndc_txr_field(sep='##').alias('drug_id'),
                                   PackGrid.slot_number, SlotDetails.id.alias('slot_id'), SlotDetails.quantity) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list) \
            .group_by(SlotDetails.id)

        for record in query.dicts():
            if mfd_drug_set and record['drug_id'] in mfd_drug_set:
                continue
            if record['id'] not in pack_manual_drugs_set.keys():
                pack_manual_drugs_set[record['id']] = set()
            if record['id'] not in pack_all_slot_drug_dict.keys():
                pack_all_slot_drug_dict[record['id']] = {}
            if record['slot_number'] not in pack_all_slot_drug_dict[record['id']].keys():
                pack_all_slot_drug_dict[record['id']][record['slot_number']] = set()
            if record['drug_id'] is not None:
                pack_all_slot_drug_dict[record['id']][record['slot_number']].add(record['drug_id'])

            if float(record['quantity']) in settings.DECIMAL_QTY_LIST:
                pack_manual_drugs_set[record['id']].add(record['drug_id'])

        for record in query.dicts():
            if mfd_drug_set and record['drug_id'] in mfd_drug_set:
                continue
            if record['drug_id'] in canister_drugs and record['drug_id'] not in pack_manual_drugs_set[record['id']]:
                if record['id'] not in pack_canister_slot_drug_dict.keys():
                    pack_canister_slot_drug_dict[record['id']] = {}
                if record['slot_number'] not in pack_canister_slot_drug_dict[record['id']].keys():
                    pack_canister_slot_drug_dict[record['id']][record['slot_number']] = set()
                if record['drug_id'] is not None:
                    pack_canister_slot_drug_dict[record['id']][record['slot_number']].add(record['drug_id'])

                drugs_set.add(record['drug_id'])

        return pack_all_slot_drug_dict, pack_canister_slot_drug_dict, drugs_set, pack_manual_drugs_set

    except Exception as e:
        logger.error("Exception in get_pack_slotwise_canister_drugs_ {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in get_pack_slotwise_canister_drugs_: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def insert_unassigned_pack_user_map_data_dao(pack_id, user_id, date, created_by=None):
    try:
        if user_id:
            created_by = user_id
        status = PackUserMap.insert(pack_id=pack_id, assigned_to=None,
                                    created_by=created_by, modified_by=created_by,
                                    created_date=date,
                                    modified_date=date).execute()
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in insert_pack_user_map_data_dao {}".format(e))
        raise e




@log_args_and_response
def get_data_of_slot_with_fill_volume(pack_id):
    try:
        logger.info("In get_data_of_slot_with_fill_volume")
        slot_vol_dict = {}
        query = PackGrid.select(PackGrid.slot_number).dicts()
        for data in query:
            slot_vol_dict[data["slot_number"]] = 0
        # slot_vol_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0}

        query = SlotHeader.select(PackGrid.slot_number,
                                  SlotDetails.drug_id,
                                  fn.SUM(SlotDetails.quantity).alias('qty'),
                                  DrugDimension.approx_volume).dicts() \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .where(SlotHeader.pack_id == pack_id) \
                .group_by(PackGrid.slot_number, SlotDetails.drug_id)

        logger.info(f"In get_data_of_slot_with_fill_volume, query: {query}")

        for data in query:
            vol = float(data["qty"]) * (float(data["approx_volume"]) if data["approx_volume"] is not None else 532.57)
            slot_vol_dict[data["slot_number"]] += vol

        return slot_vol_dict

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_data_of_slot_with_fill_volume {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_data_of_slot_with_fill_volume {}".format(e))
        raise e


@log_args_and_response
def get_pill_jump_error_slot_for_given_pack(pack_id):
    try:
        logger.info("Inside get_pill_jump_error_slot_for_given_pack")
        jump_error_slot_set: set = set()

        query = PillJumpError.select(PillJumpError.slot_number).dicts() \
                .where(PillJumpError.pack_id == pack_id) \
                .group_by(PillJumpError.slot_number)

        for data in query:
            jump_error_slot_set.add(data["slot_number"])

        logger.info(f"In get_pill_jump_error_slot_for_given_pack, jump_error_slot_dict: {jump_error_slot_set}")

        return jump_error_slot_set

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pill_jump_error_slot_for_given_pack {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_pill_jump_error_slot_for_given_pack {}".format(e))
        raise e

# This Function is for analysis of canister recommnedation
def get_total_drop_count(batch_id):
    drug_wise_count_dict = {}
    total_count = PackDetails.select(fn.COUNT(fn.DISTINCT(SlotDetails.slot_id))) \
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
        .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
        .where(PackDetails.batch_id == batch_id).scalar()

    drug_wise_count = PackDetails.select(UniqueDrug.id, fn.COUNT(SlotDetails.slot_id).alias('slot_count')).dicts() \
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
        .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
        .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
        .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                              (UniqueDrug.txr == DrugMaster.txr))) \
        .where(PackDetails.batch_id == batch_id).group_by(UniqueDrug.id)

    for record in drug_wise_count:
        drug_wise_count_dict[record['id']] = record['slot_count']

    sorted_dict = {k: v for k, v in sorted(drug_wise_count_dict.items(), key=lambda item: item[1], reverse = True)}
    return total_count, sorted_dict


@log_args_and_response
def update_pack_details_and_insert_in_pack_user_map(pack_list):
    try:
        logger.info(f"Inside update_pack_details_and_insert_in_pack_user_map, pack_list: {pack_list}")

        status = PackDetails.update(pack_status=settings.MANUAL_PACK_STATUS).where(PackDetails.id << pack_list).execute()

        logger.info(f"In update_pack_details_and_insert_in_pack_user_map, pack_details status: {status}")

        if status:
            insert_list = []

            for pack in pack_list:
                insert_list.append({"pack_id": pack,
                                    "assigned_to": None,
                                    "created_by": 1,
                                    "modified_by": 1,
                                    "created_date": get_current_date_time(),
                                    "modified_date": get_current_date_time()})

            logger.info(f"In update_pack_details_and_insert_in_pack_user_map, insert_list: {insert_list}")

            if insert_list:
                status = PackUserMap.insert_many(insert_list).execute()
                logger.info(f"In update_pack_details_and_insert_in_pack_user_map, pack_user_map status: {status}")

        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_pack_details_and_insert_in_pack_user_map {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in update_pack_details_and_insert_in_pack_user_map {}".format(e))
        raise e


@log_args_and_response
def get_pending_pack_queue_order_pack(system_id: int, priority: Optional[int] = None) -> List[Any]:
    """

    """
    try:
        if priority == 1:
            query = PackDetails.select(PackDetails.id, PackDetails.order_no).dicts() \
                .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
                .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                       PackDetails.system_id == system_id,
                       PackDetails.order_no.is_null(False)) \
                .order_by(PackDetails.order_no)
            return query
        else:
            query = PackDetails.select(PackDetails.id, PackDetails.order_no).dicts() \
                .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
                .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                       PackDetails.system_id == system_id,
                       PackDetails.order_no.is_null(False)) \
                .order_by(PackDetails.order_no.desc())
            return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_order_pack_id_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_order_pack_id_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response_dict
def get_db_data_for_batch_merge(system_id: int, merge_batch_id, imported_batch_id):

    # pack queue packs with MA and PA

    # New batch Packs with MA and PA

    # device_pack_list[device]=[packs] ------------

    # device_trolley_packs[device][trolley]=[packs] -------

    # pack_order_dict[pack]=order_no ----------

    # new_batch_device_trolley_packs[device][trolley]=[packs] -------

    # delivery_wise_auto_packs[delivery_date]= [packs] ------

    # trolley_seq_min_max_delivery_date[trolley]=[min_date, max_date] ------

    # new_trolley_seq_min_max_delivery_date[trolley]=[min_date, max_date] -------

    # device_wise_order_no[device]=[order_no]  # All
    '''
    :param system_id:
    :param merge_batch_id:
    :param imported_batch_id:

    here throughout the code block, refer o as old, n as new, d as device p as pack, ord as order_no, ma as mfd_analysis_id, ts as trolley_seq
    '''
    # variables with o will referd as old batch data or imported batch data
    # variables with n will referd as new batch data or to be imported batch data
    o_d_p_dict = OrderedDict()
    o_d_p_ord_dict = OrderedDict()
    n_d_p_dict = OrderedDict()
    n_d_p_ord_dict = OrderedDict()
    all_p_ord_dict = OrderedDict()
    o_d_ts_p_dict = OrderedDict()
    n_d_ts_p_dict = OrderedDict()
    auto_p_del_dict = OrderedDict()
    d_auto_p_del_dict = OrderedDict()
    o_ts_del_min_max = OrderedDict()
    n_ts_del_min_max = OrderedDict()
    d_p_ord_dict = OrderedDict()
    d_ma_ord_dict = OrderedDict()
    o_ts_ma_dict = OrderedDict()
    n_ts_ma_dict = OrderedDict()
    o_del_date_trolley_seq = {}
    n_del_date_trolley_seq = {}
    del_date_list = []
    device_set = set()
    response_dict = {}
    skip_consider_trolley = []
    progress_trolley = {}
    last_transferred = 0
    last_progress_cart = 0
    manual_packs = []
    trolley_travelled = []
    empty_trolley_device_id = []
    max_trolley_old_batch = 0
    try:

        try:
            last_transferred = MfdAnalysis.select(fn.MAX(MfdAnalysis.trolley_seq)).where(
                MfdAnalysis.batch_id == imported_batch_id, MfdAnalysis.transferred_location_id.is_null(False)).scalar()
            last_transferred = 0 if not last_transferred else last_transferred

        except DoesNotExist as e:
            pass
        logger.info("In get_db_data_for_batch_merge: last_transferred: {}".format(last_transferred))
        try:
            max_trolley_query = MfdAnalysis.select(fn.MAX(MfdAnalysis.trolley_seq)).where(
                MfdAnalysis.batch_id == imported_batch_id).scalar()
            max_trolley_old_batch = 0 if not max_trolley_query else max_trolley_query

        except DoesNotExist as e:
            pass
        logger.info("In get_db_data_for_batch_merge: max_trolley_old_batch: {}".format(max_trolley_old_batch))
        try:
            last_progress_cart = MfdAnalysis.select(fn.MAX(MfdAnalysis.trolley_seq)) \
                    .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
                    .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                    .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                    .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                    .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                    .where(PackDetails.pack_status == settings.PROGRESS_PACK_STATUS).scalar()
            last_progress_cart = 0 if not last_progress_cart else last_progress_cart

        except DoesNotExist as e:
            pass
        logger.info("In get_db_data_for_batch_merge: last_progress_cart: {}".format(last_progress_cart))

        trolley_query: object = MfdAnalysis.select(MfdAnalysis.trolley_seq,
                                                fn.GROUP_CONCAT(MfdAnalysis.status_id).coerce(False).alias("status")).dicts().where(
            MfdAnalysis.batch_id == imported_batch_id, MfdAnalysis.trolley_seq > last_transferred).group_by(MfdAnalysis.trolley_seq)

        for record in trolley_query:
            status_list = list(map(int, record['status'].split(',')))
            status_list = set(status_list)
            pending_status = {constants.MFD_CANISTER_IN_PROGRESS_STATUS, constants.MFD_CANISTER_PENDING_STATUS, constants.MFD_CANISTER_FILLED_STATUS}
            if not pending_status.intersection(status_list):
                skip_consider_trolley.append(record['trolley_seq'])
                # if [constants.MFD_CANISTER_IN_PROGRESS_STATUS] in status_list:
            #     progress_trolley.append(record['trolley_seq'])
        logger.info("In get_db_data_for_batch_merge: skip_consider_trolley: {}".format(skip_consider_trolley))

        not_to_consider_trolley = last_transferred if last_transferred > last_progress_cart else last_progress_cart
        logger.info("In get_db_data_for_batch_merge: not_to_consider_trolley: {}".format(not_to_consider_trolley))

        manual_pack_query = PackQueue.select(PackQueue.pack_id).dicts() \
            .join(PackRxLink, on=PackQueue.pack_id == PackRxLink.pack_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id)

        manual_packs = [record['pack_id'] for record in manual_pack_query]
        logger.info("In get_db_data_for_batch_merge: manual_packs: {}".format(manual_packs))

        query = PackDetails.select(PackDetails.id.alias('pack_id'),
                                   PackDetails.order_no,
                                   PackDetails.batch_id,
                                   PackHeader.scheduled_delivery_date,
                                   fn.IF(PackAnalysisDetails.id.is_null(False), PackAnalysisDetails.device_id,
                                         MfdAnalysis.dest_device_id).alias('device_id'),
                                   MfdAnalysisDetails.analysis_id.alias('mfd_analysis_id'),
                                   MfdAnalysis.trolley_seq,
                                   MfdAnalysis.dest_device_id,
                                   MfdAnalysis.transferred_location_id,
                                   MfdAnalysis.order_no.alias("mfd_order_no"),
                                   MfdAnalysis.assigned_to,
                                   MfdAnalysis.mfs_device_id,
                                   DeviceMaster.system_id.alias('mfs_system_id'),
                                   MfdAnalysis.status_id.alias('mfd_status'),
                                   PackDetails.pack_status,
                                   LocationMaster.device_id.alias('trolley_cart_id')
                                   ).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=(
                (MfdAnalysis.id == MfdAnalysisDetails.analysis_id) & ((
                (MfdAnalysis.batch_id == imported_batch_id)) | (MfdAnalysis.batch_id == merge_batch_id)))) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .where(PackDetails.system_id == system_id, PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   PackDetails.batch_id << [imported_batch_id, merge_batch_id]) \
            .order_by(PackDetails.order_no)
        logger.info("In get_db_data_for_batch_merge: query: {}".format((query)))

        for row in query:
            device_id = row['device_id']
            batch_id = row['batch_id']
            pack_id = row['pack_id']
            trolley_seq = row['trolley_seq']
            order_no = row['order_no']
            del_date = row['scheduled_delivery_date']
            mfd_analysis_id = row['mfd_analysis_id']
            dest_device_id = row['dest_device_id']
            transferred_location_id = row['transferred_location_id']
            assigned_to = row['assigned_to']
            mfs_system_id = row['mfs_system_id']
            pack_status = row['pack_status']
            mfd_status = row['mfd_status']
            mfd_order_no = row['mfd_order_no']
            trolley_cart_id = row['trolley_cart_id']
            if device_id:
                device_set.add(device_id)
            # If Old Batch
            if batch_id == imported_batch_id:

                # If any canister in skipped
                if trolley_seq and trolley_seq in skip_consider_trolley:
                    continue
                # to check empty canister list
                if trolley_cart_id and trolley_cart_id not in trolley_travelled:
                    trolley_travelled.append(trolley_cart_id)
                # to get all old device pack ids and their previous order no
                if device_id not in o_d_p_dict:
                    o_d_p_dict[device_id] = [pack_id]
                    o_d_p_ord_dict[device_id] = [order_no]
                else:
                    if pack_id not in o_d_p_dict[device_id] :
                        o_d_p_dict[device_id].append(pack_id)
                        o_d_p_ord_dict[device_id].append(order_no)

                # for mfd packs
                if trolley_seq and trolley_seq not in skip_consider_trolley and trolley_seq > not_to_consider_trolley:
                    # to check trolley seq if is in progress
                    if mfd_status == constants.MFD_CANISTER_IN_PROGRESS_STATUS:
                        progress_trolley[trolley_seq]= mfs_system_id

                    # device wise trolley packs..
                    if device_id not in o_d_ts_p_dict:
                        o_d_ts_p_dict[device_id] = {trolley_seq: [pack_id]}
                    else:
                        if trolley_seq not in o_d_ts_p_dict[device_id]:
                            o_d_ts_p_dict[device_id][trolley_seq] = [pack_id]
                        else:
                            if pack_id not in o_d_ts_p_dict[device_id][trolley_seq]:
                                o_d_ts_p_dict[device_id][trolley_seq].append(pack_id)

                    # Trolley min max delivery date
                    if trolley_seq not in o_ts_del_min_max:
                        o_ts_del_min_max[trolley_seq] = [del_date, del_date]
                    else:
                        min = o_ts_del_min_max[trolley_seq][0]
                        max = o_ts_del_min_max[trolley_seq][1]
                        if del_date <= min:
                            o_ts_del_min_max[trolley_seq][0] = del_date
                        elif del_date >= max:
                            o_ts_del_min_max[trolley_seq][1] = del_date
                    if device_id not in d_p_ord_dict:
                        d_p_ord_dict[device_id] = [order_no]
                    else:
                        if order_no not in d_p_ord_dict[device_id]:
                            d_p_ord_dict[device_id].append(order_no)

                    # Trolley seq wise analysis ids
                    if trolley_seq not in o_ts_ma_dict:
                        o_ts_ma_dict[trolley_seq] = [mfd_analysis_id]
                    else:
                        if mfd_analysis_id not in o_ts_ma_dict[trolley_seq]:
                            o_ts_ma_dict[trolley_seq].append(mfd_analysis_id)
                    if device_id not in d_ma_ord_dict:
                        d_ma_ord_dict[device_id] = [mfd_order_no]
                    else:
                        if mfd_order_no not in d_ma_ord_dict[device_id]:
                            d_ma_ord_dict[device_id].append(mfd_order_no)

                    # del date wise trolleys
                    if del_date not in o_del_date_trolley_seq:
                        o_del_date_trolley_seq[del_date] =[trolley_seq]
                    else:
                        if trolley_seq not in o_del_date_trolley_seq[del_date]:
                            o_del_date_trolley_seq[del_date].append(trolley_seq)
            # if new batch
            else:
                # all packs data
                if device_id not in n_d_p_dict:
                    n_d_p_dict[device_id] = [pack_id]
                    n_d_p_ord_dict[device_id] = [order_no]
                else:
                    if pack_id not in n_d_p_dict[device_id] :
                        n_d_p_dict[device_id].append(pack_id)
                        n_d_p_ord_dict[device_id].append(order_no)

                # Mfd
                if trolley_seq:
                    #device wise trolley packs
                    if device_id not in n_d_ts_p_dict:
                        n_d_ts_p_dict[device_id] = {trolley_seq: [pack_id]}
                    else:
                        if trolley_seq not in n_d_ts_p_dict[device_id]:
                            n_d_ts_p_dict[device_id][trolley_seq] = [pack_id]
                        else:
                            if pack_id not in n_d_ts_p_dict[device_id][trolley_seq]:
                                n_d_ts_p_dict[device_id][trolley_seq].append(pack_id)
                    # trolley wise min max dates
                    if trolley_seq not in n_ts_del_min_max:
                        n_ts_del_min_max[trolley_seq] = [del_date, del_date]
                    else:
                        min = n_ts_del_min_max[trolley_seq][0]
                        max = n_ts_del_min_max[trolley_seq][1]
                        if del_date <= min:
                            n_ts_del_min_max[trolley_seq][0] = del_date
                        elif del_date >= max:
                            n_ts_del_min_max[trolley_seq][1] = del_date

                    # Trolley wise analysis ids
                    if trolley_seq not in n_ts_ma_dict:
                        n_ts_ma_dict[trolley_seq] = [mfd_analysis_id]
                    else:
                        if mfd_analysis_id not in n_ts_ma_dict[trolley_seq]:
                            n_ts_ma_dict[trolley_seq].append(mfd_analysis_id)
                    if device_id not in d_ma_ord_dict:
                        d_ma_ord_dict[device_id] = [mfd_order_no]
                    else:
                        if mfd_order_no not in d_ma_ord_dict[device_id]:
                            d_ma_ord_dict[device_id].append(mfd_order_no)

                    # delivery date wise trolleys
                    if del_date not in n_del_date_trolley_seq:
                        n_del_date_trolley_seq[del_date] =[trolley_seq]
                    else:
                        if trolley_seq not in n_del_date_trolley_seq[del_date]:
                            n_del_date_trolley_seq[del_date].append(trolley_seq)

                    if device_id not in d_p_ord_dict:
                        d_p_ord_dict[device_id] = [order_no]
                    else:
                        if order_no not in d_p_ord_dict[device_id]:
                            d_p_ord_dict[device_id].append(order_no)
            # ===========================================================
            # auto packs
            if pack_id not in manual_packs or (trolley_seq and batch_id == imported_batch_id and (trolley_seq in skip_consider_trolley)):
                # del date wise packs
                if del_date not in auto_p_del_dict:
                    auto_p_del_dict[del_date] = [pack_id]
                else:
                    if pack_id not in auto_p_del_dict[del_date] :
                        auto_p_del_dict[del_date].append(pack_id)
                # device wise del data and packs
                if device_id not in d_auto_p_del_dict:
                    d_auto_p_del_dict[device_id] = {del_date : [pack_id]}
                else:
                    if del_date not in d_auto_p_del_dict[device_id]:
                        d_auto_p_del_dict[device_id][del_date] = [pack_id]
                    else:
                        if pack_id not in d_auto_p_del_dict[device_id][del_date]:
                            d_auto_p_del_dict[device_id][del_date].append(pack_id)
                if device_id not in d_p_ord_dict:
                    d_p_ord_dict[device_id] = [order_no]
                else:
                    if order_no not in d_p_ord_dict[device_id]:
                        d_p_ord_dict[device_id].append(order_no)

            # ===============================================================

            all_p_ord_dict[pack_id] = order_no
            if del_date not in del_date_list:
                del_date_list.append(del_date)

        response_dict["o_d_p_dict"] = o_d_p_dict
        response_dict["o_d_p_ord_dict"] = o_d_p_ord_dict
        response_dict["n_d_p_dict"] = n_d_p_dict
        response_dict["n_d_p_ord_dict"] = n_d_p_ord_dict
        response_dict["all_p_ord_dict"] = all_p_ord_dict
        response_dict["o_d_ts_p_dict"] = o_d_ts_p_dict
        response_dict["n_d_ts_p_dict"] = n_d_ts_p_dict
        response_dict["auto_p_del_dict"] = auto_p_del_dict
        response_dict["o_ts_del_min_max"] = o_ts_del_min_max
        response_dict["n_ts_del_min_max"] = n_ts_del_min_max
        response_dict["d_p_ord_dict"] = d_p_ord_dict
        response_dict["d_ma_ord_dict"] = d_ma_ord_dict
        response_dict["o_ts_ma_dict"] = o_ts_ma_dict
        response_dict["n_ts_ma_dict"] = n_ts_ma_dict
        response_dict["n_del_date_trolley_seq"] = n_del_date_trolley_seq
        response_dict["o_del_date_trolley_seq"] = o_del_date_trolley_seq
        response_dict["del_date_list"] = del_date_list
        response_dict["device_set"] = device_set
        response_dict["progress_trolley"] = progress_trolley
        response_dict["d_auto_p_del_dict"] = d_auto_p_del_dict
        response_dict["trolley_travelled"] = trolley_travelled
        response_dict["max_trolley_old_batch"] = max_trolley_old_batch

        return response_dict
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_db_data_for_batch_merge {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_db_data_for_batch_merge: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def merge_batch_dao(pack_seq_tuple, pack_ids, analysis_ids, mfd_order_seq_tuple, mfd_trolley_seq_tuple,
                    imported_batch_id, merge_batch_id, user_id):
    try:
        if mfd_order_seq_tuple:
            case_sequence = case(MfdAnalysis.id, mfd_order_seq_tuple)
            logger.info("In AUTO_BATCH_MERGE: analysis_ids: {}".format(mfd_order_seq_tuple))
            order_no_status = MfdAnalysis.db_change_mfd_order_no(case_sequence=case_sequence,
                                                                 mfd_analysis_ids=analysis_ids,
                                                                 user_id=user_id)
        if mfd_trolley_seq_tuple:
            case_sequence = case(MfdAnalysis.id, mfd_trolley_seq_tuple)
            logger.info("In AUTO_BATCH_MERGE: mfd_trolley_seq_tuple: {}".format(mfd_trolley_seq_tuple))
            order_no_status = MfdAnalysis.db_change_trolley_seq(case_sequence=case_sequence,
                                                                mfd_analysis_ids=analysis_ids,
                                                                user_id=user_id)

        if pack_seq_tuple:
            case_sequence = case(PackDetails.id, pack_seq_tuple)
            logger.info("In AUTO_BATCH_MERGE: pack_seq_tuple: {}".format(pack_seq_tuple))
            order_no_status = PackDetails.db_change_pack_sequence(case_sequence=case_sequence,
                                                                  pack_list=pack_ids)

        # Update batch id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in merge_batch_dao {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in merge_batch_dao: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_all_same_drug_by_drug_id(drug_ids):
    try:
        DrugMasterAlias = DrugMaster.alias()
        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugMaster.formatted_ndc, DrugMaster.txr).dicts() \
            .join(DrugMasterAlias, on=(
                (DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) & (DrugMaster.txr == DrugMasterAlias.txr))) \
            .where(DrugMasterAlias.id << drug_ids)
        response = {}
        for record in query:
            response[record["id"]] = {
                'id': record["id"],
                'ndc': record["ndc"],
                'formatted_ndc': record["formatted_ndc"],
                'txr': record["txr"],
            }
        return response
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_all_same_drug_by_drug_id".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in get_all_same_drug_by_drug_id:{e}")
        raise e


@log_args_and_response
def get_all_same_ndc_by_drug_id(drug_id):
    try:
        DrugMasterAlias = DrugMaster.alias()

        ndc_concatenated = DrugMaster.select(fn.GROUP_CONCAT(DrugMaster.ndc).alias('ndc_concatenated')) \
            .join(DrugMasterAlias, on=(
                (DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) & (DrugMaster.txr == DrugMasterAlias.txr))) \
            .where(DrugMasterAlias.id == drug_id).scalar()

        return ndc_concatenated

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_all_same_drug_by_drug_id".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in get_all_same_drug_by_drug_id:{e}")
        raise e


@log_args_and_response
def get_filled_drug_count_slot_transaction(drug_list):
    mfd_qty_dict = {}
    drug_qty_dict = {}
    return_dict = {}
    canister_filled_list = []
    mfd_filled_list = []
    try:
        canister_filled = PackDetails.select(DrugTracker.drug_id, DrugTracker.case_id,fn.SUM(DrugTracker.drug_quantity).alias(
            'dropped_qty'), fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id),).coerce(False).alias('pack_ids')).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id) \
            .where(PackDetails.pack_status << [settings.PROGRESS_PACK_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT],
                   DrugTracker.drug_id << drug_list) \
            .group_by(DrugTracker.case_id, DrugTracker.drug_id)

        mfd_filled = PackDetails.select(SlotDetails.drug_id, fn.SUM(MfdAnalysisDetails.quantity).alias(
            'dropped_qty'), DrugTracker.case_id, fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).coerce(False).alias(
            'pack_ids')).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(MfdAnalysisDetails, on=((MfdAnalysisDetails.slot_id == SlotDetails.id) & (
                MfdAnalysisDetails.status_id << [constants.MFD_DRUG_DROPPED_STATUS, constants.MFD_DRUG_MVS_FILLED,
                                                 constants.MFD_DRUG_FILLED_STATUS, constants.MFD_DRUG_RTS_REQUIRED_STATUS])))\
            .join(DrugTracker, JOIN_LEFT_OUTER ,on=DrugTracker.slot_id == SlotDetails.slot_id) \
            .where(PackDetails.pack_status << [settings.PROGRESS_PACK_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT],
                   SlotDetails.drug_id << drug_list) \
            .group_by(DrugTracker.case_id, DrugTracker.drug_id)

        canister_filled_list = list(canister_filled)
        mfd_filled_list = list(mfd_filled)
        logger.info("In get_filled_drug_count_slot_transaction: caniter_drug_count: {}".format(canister_filled_list))
        logger.info("In get_filled_drug_count_slot_transaction: mfd_drug_count: {}".format(mfd_filled_list))

        for record in canister_filled_list:
            if record['dropped_qty']:
                drug_qty_dict.setdefault(record['drug_id'],dict())
                drug_qty_dict[record['drug_id']][record['case_id']] = drug_qty_dict[record['drug_id']].get(record['case_id'], 0) + int(
                math.ceil(record['dropped_qty']))
        for record in mfd_filled_list:
            if record['dropped_qty']:
                mfd_qty_dict.setdefault(record['drug_id'], dict())
                mfd_qty_dict[record['drug_id']][record['case_id']] = mfd_qty_dict[record['drug_id']].get(
                    record['case_id'], 0) + int(
                    math.ceil(record['dropped_qty']))

        # return_dict = {
        #     key: int(mfd_qty_dict.get(key, 0)) + int(drug_qty_dict.get(key, 0)) for key in
        #     set(mfd_qty_dict) | set(drug_qty_dict)
        #     }
        return_dict = drug_qty_dict.copy()
        for drug_id,drug_data in mfd_qty_dict.items():
            for case_id, quantity in drug_data.items():
                return_dict.setdefault(drug_id,dict())
                return_dict[drug_id][case_id] = int(return_dict[drug_id].get(case_id, 0)) + quantity

        return return_dict
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in adjust_drug_based_on_current_filled_qty: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in adjust_drug_based_on_current_filled_qty: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_mfd_filled_drug_count(drug_list):
    drug_qty_dict = {}
    try:
        query = MfdAnalysis.select(SlotDetails.drug_id,DrugTracker.case_id ,fn.SUM(SlotDetails.quantity).alias('mfd_quantity')) \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id==SlotDetails.id) \
            .where(SlotDetails.drug_id << drug_list, MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                                                               constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                                               constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                                               constants.MFD_CANISTER_VERIFIED_STATUS],
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS) \
            .group_by(DrugTracker.case_id, DrugTracker.drug_id)

        for record in query.dicts():
            drug_qty_dict.setdefault(record['drug_id'], dict())
            drug_qty_dict[record['drug_id']][record['case_id']] = int(math.ceil(record['mfd_quantity']))

        return drug_qty_dict
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in adjust_drug_based_on_current_filled_qty: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in adjust_drug_based_on_current_filled_qty: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_manual_partially_filled_packs_drug_count(drug_list):
    drug_qty_dict = {}
    try:
        query = PackDetails.select(SlotDetails.drug_id, fn.SUM(SlotDetails.quantity).alias('total_qty'),
                                   PartiallyFilledPack.missing_qty,
                                   DrugTracker.case_id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PartiallyFilledPack, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id)\
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id) \
            .where(PackDetails.pack_status == settings.FILLED_PARTIALLY_STATUS, SlotDetails.drug_id << drug_list) \
            .group_by(PackRxLink.id)

        for record in query.dicts():
            missing_qty = record['missing_qty']
            total_qty = record['total_qty']
            if record['drug_id'] not in drug_qty_dict:
                drug_qty_dict[record['drug_id']] = {}
                if record['case_id'] not in drug_qty_dict[record['drug_id']]:
                    drug_qty_dict[record['drug_id']][record['case_id']] = int(math.ceil(total_qty if not missing_qty else total_qty - missing_qty))
            else:
                drug_qty_dict[record['drug_id']][record['case_id']] += int(math.ceil(total_qty if not missing_qty else total_qty - missing_qty))

        return drug_qty_dict
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in adjust_drug_based_on_current_filled_qty: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in adjust_drug_based_on_current_filled_qty: {}".format(e), exc_info=True)
        raise e

@log_args_and_response
def get_manual_pack_ids_for_manual_pack_filling(assign_user, txr):

    try:
        select_fields = [PackDetails.id.alias("pack_id")]
        pack_ids = list()

        query = PackDetails.select(*select_fields).dicts()\
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id)\
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)\
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)\
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id)\
            .where((PackUserMap.assigned_to == assign_user) &
                   (PackDetails.pack_status == settings.MANUAL_PACK_STATUS) &
                   (DrugMaster.txr == txr) &
                   (PatientRx.daw_code == 0)
                   )\
            .group_by(PackDetails.id)

        for record in query:
            if record["pack_id"] not in pack_ids:
                pack_ids.append(record["pack_id"])

        return pack_ids
    except Exception as e:
        logger.error("Error in get_manual_pack_ids: {}".format(e))
        raise e


@log_args_and_response
def db_update_slot_details_by_multiple_slot_id_dao(update_dict: dict, slot_details_ids: list) -> bool:
    """
    This function to update slot details by slot id
    @param update_dict:
    @param slot_details_ids:
    @return:

    """
    try:
        status = SlotDetails.db_update_slot_details_by_multiple_slot_id(update_dict=update_dict,
                                                                        slot_details_ids=slot_details_ids)
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_slot_details_by_slot_id_dao {}".format(e))
        raise e


@log_args_and_response
def verify_pack_id_by_system_id(pack_id):
    try:
        valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id)
        return valid_pack
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in verify_pack_id_by_system_id: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in verify_pack_id_by_system_id: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def db_fetch_nearest_exp_date_drug(pack_id, max_pack_consumption_end_date):
    exp_date_fndc_txr_dict = {}
    try:
        if max_pack_consumption_end_date is not None:
            max_pack_consumption_end_date = datetime.datetime.strptime(max_pack_consumption_end_date,
                                                                       "%Y-%m-%d").date()
        else:
            max_pack_consumption_end_date = PackDetails.select(fn.MAX(PackDetails.consumption_end_date)) \
                .where(PackDetails.id << [pack_id]).scalar()

        query = PackDetails.select(DrugMaster, fn.IF(CanisterTracker.expiration_date, CanisterTracker.expiration_date, DrugTracker.expiry_date).alias("exp_date")).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(DrugTracker, on=DrugTracker.slot_id == SlotDetails.id) \
            .join(CanisterTracker, JOIN_LEFT_OUTER, on=DrugTracker.canister_tracker_id == CanisterTracker.id) \
            .where(PackDetails.id == pack_id, DrugTracker.is_overwrite == 0)

        for record in query:
            if record['exp_date']:
                if not exp_date_fndc_txr_dict.get(record['exp_date']):
                    exp_date_fndc_txr_dict[record['exp_date']] = set()
                exp_date_fndc_txr_dict[record['exp_date']].add((record['formatted_ndc'], record['txr']))
        if exp_date_fndc_txr_dict:
            def sort_by_month(date_string):
                return datetime.datetime.strptime(date_string, "%m-%Y")

            nearest_exp = sorted(exp_date_fndc_txr_dict.keys(), key=sort_by_month)[0]
            date_obj = datetime.datetime.strptime(nearest_exp + "-01", "%m-%Y-%d").date()

            # today = datetime.datetime.now().date()
            last_day_of_month = date_obj.replace(day=28) + datetime.timedelta(days=4)
            last_day_of_month = last_day_of_month - datetime.timedelta(days=last_day_of_month.day)
            if (last_day_of_month - max_pack_consumption_end_date).days < settings.EXPIRY_SOON_DAYS:
                return exp_date_fndc_txr_dict[nearest_exp]

        return []
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in db_fetch_nearest_exp_date_drug: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in db_fetch_nearest_exp_date_drug: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def db_get_expiry_soon_drug(pack_id, max_pack_consumption_end_date):

    try:
        expiry_soon_drugs: dict = dict()
        if max_pack_consumption_end_date is not None:
            max_pack_consumption_end_date = datetime.datetime.strptime(max_pack_consumption_end_date,
                                                                       "%Y-%m-%d").date()
        else:
            max_pack_consumption_end_date = PackDetails.select(fn.MAX(PackDetails.consumption_end_date)) \
                .where(PackDetails.id << [pack_id]).scalar()

        select_fields = [DrugTracker.pack_id,
                         DrugTracker.slot_id,
                         DrugTracker.drug_id,
                         fn.IF(DrugTracker.canister_tracker_id.is_null(False),
                               CanisterTracker.expiration_date,
                               DrugTracker.expiry_date).alias("drug_expiry_date"),
                         PackGrid.slot_number
                         ]

        query = SlotDetails.select(*select_fields).dicts()\
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id)\
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
            .join(DrugTracker, on=SlotDetails.id == DrugTracker.slot_id)\
            .join(CanisterTracker, JOIN_LEFT_OUTER, on=CanisterTracker.id == DrugTracker.canister_tracker_id) \
            .where((PackDetails.id << [pack_id]), (DrugTracker.is_overwrite == 0))\
            .order_by(PackGrid.slot_number)

        logger.info("query for expiry_soon_drug: {}".format(query))

        for record in query:
            if "drug_list" not in expiry_soon_drugs:
                expiry_soon_drugs["drug_list"] = dict()

            if record["slot_number"] not in expiry_soon_drugs:
                expiry_soon_drugs[record["slot_number"]] = dict()

            if record["drug_id"] not in expiry_soon_drugs[record["slot_number"]]:
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]] = dict()

            if record["drug_id"] not in expiry_soon_drugs["drug_list"]:
                expiry_soon_drugs["drug_list"][record["drug_id"]] = dict()
                expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] = None
                expiry_soon_drugs["drug_list"][record["drug_id"]]["expire_soon_drug"] = None

            if not record["drug_expiry_date"]:
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]]["expire_soon_drug"] = None
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]]["expiry_date"] = record["drug_expiry_date"]
                continue

            drug_expiry_date = datetime.datetime.strptime(record["drug_expiry_date"], "%m-%Y").date()
            expiry_month = drug_expiry_date.month
            expiry_year = drug_expiry_date.year
            days = calendar.monthrange(expiry_year, expiry_month)[1]

            if days == 31:
                drug_expiry_date = drug_expiry_date + datetime.timedelta(days=30)
            elif days == 30:
                drug_expiry_date = drug_expiry_date + datetime.timedelta(days=29)
            elif days == 29:
                drug_expiry_date = drug_expiry_date + datetime.timedelta(days=28)
            elif days == 28:
                drug_expiry_date = drug_expiry_date + datetime.timedelta(days=27)

            if (drug_expiry_date - max_pack_consumption_end_date).days < settings.EXPIRY_SOON_DAYS:
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]]["expire_soon_drug"] = True
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]]["expiry_date"] = drug_expiry_date

                if expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] is None:
                    expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] = drug_expiry_date
                    expiry_soon_drugs["drug_list"][record["drug_id"]]["expire_soon_drug"] = True
                else:
                    if drug_expiry_date < expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"]:
                        expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] = drug_expiry_date
                        expiry_soon_drugs["drug_list"][record["drug_id"]]["expire_soon_drug"] = True
            else:
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]]["expire_soon_drug"] = False
                expiry_soon_drugs[record["slot_number"]][record["drug_id"]]["expiry_date"] = drug_expiry_date

                if expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] is None:
                    expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] = drug_expiry_date
                    expiry_soon_drugs["drug_list"][record["drug_id"]]["expire_soon_drug"] = False
                else:
                    if drug_expiry_date < expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"]:
                        expiry_soon_drugs["drug_list"][record["drug_id"]]["expiry_date"] = drug_expiry_date
                        expiry_soon_drugs["drug_list"][record["drug_id"]]["expire_soon_drug"] = False

        return expiry_soon_drugs
    except Exception as e:
        logger.error("Error in db_get_expiry_soon_drug: {}".format(e))
        raise e



@log_args_and_response
def verify_pack_display_id(pack_display_id):
    try:
        status = PackDetails.db_verify_pack_display_id(pack_display_id=pack_display_id)
        return status
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in verify_pack_display_id: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in verify_pack_display_id: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_packs_info_dao(company_id, filter_fields, paginate, time_zone):
    try:
        clauses = list()
        module = str()
        filled_at_tuples = PackDetails.FILLED_AT_MAP.items()
        limit_records = False

        like_search_list = ['pack_display_id', 'facility_name', 'patient_name', 'pack_id']
        between_search_list = ['delivery_date']
        exact_search_list = ['pack_status']
        membership_search_list = ['filled_by', 'modified_by']

        fields_dict = {"pack_display_id": PackDetails.pack_display_id,
                       "facility_name": FacilityMaster.facility_name,
                       "filled_datetime": fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, time_zone),
                       "patient_name": fn.CONCAT(PatientMaster.last_name, ', ', PatientMaster.first_name),
                       "pack_status": CodeMaster.id,
                       "filled_at_value": fn.IF(
                           PackDetails.filled_at.is_null(False),
                           cast(case(PackDetails.filled_at, filled_at_tuples), 'CHAR'), 'N.A.'
                       ),
                       "pack_id": PackDetails.id,
                       "delivery_date": fn.DATE(PackHeader.scheduled_delivery_date),
                       "filled_by": PackDetails.filled_by,
                       "modified_by": PackDetails.modified_by
                       }
        CHAR = 'CHAR'
        select_fields = [fields_dict['pack_id'].alias('pack_id'),
                         fields_dict['pack_display_id'].alias('pack_display_id'),
                         cast(fields_dict["filled_datetime"], CHAR).alias("filled_datetime"),
                         fields_dict['delivery_date'].alias('delivery_date'),
                         fields_dict["patient_name"].alias('patient_name'),
                         FacilityMaster.facility_name,
                         PackDetails.facility_dis_id,
                         fn.DATE(PackDetails.consumption_start_date).alias('admin_start_date'),
                         fn.DATE(PackDetails.consumption_end_date).alias('admin_end_date'),
                         fields_dict['filled_at_value'].alias('filled_at_value'),
                         fields_dict['filled_by'].alias('filled_by'),
                         ContainerMaster.id.alias("storage_container_id"),
                         ContainerMaster.drawer_name.alias("storage_container_name"),
                         DeviceMaster.id.alias("storage_device_id"),
                         DeviceMaster.name.alias("storage_device_name"),
                         PackDetails.batch_id,
                         BatchMaster.status.alias('batch_status'),
                         fields_dict['pack_status'].alias('pack_status'),
                         PatientMaster.id.alias('patient_id'),
                         PackUserMap.id.alias("pack_user_id")
                         ]
        clauses = [(PackDetails.company_id == company_id)]
        if 'modified_by' in filter_fields:
            clauses.append((PackDetails.pack_status << [settings.DONE_PACK_STATUS,
                                                        settings.PROCESSED_MANUALLY_PACK_STATUS]))

        # search by pack_id instead of pack_display_id as it reduces time.
        if 'pack_display_id' in filter_fields:
            pack_data = db_get_pack_ids_by_pack_display_id_dao(pack_display_ids=[filter_fields['pack_display_id']], company_id=company_id)
            if pack_data:
                pack_display_id = filter_fields.pop('pack_display_id')
                filter_fields['pack_id'] = pack_data[int(pack_display_id)]

        query = PackDetails.select(*select_fields) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == PackDetails.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .group_by(PackDetails.id) \
            .order_by(PackDetails.id.desc())

        # limit total records if filter is on pack_master module or filter is on pack_status deleted or
        # done as it takes more time.
        if (filter_fields
            and
            (((set(filter_fields.keys()) == {"pack_status"} or set(filter_fields.keys()) == {"module"})
              and (("pack_status" in filter_fields and filter_fields["pack_status"] in
                    [settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS])
                   or ("module" in filter_fields and filter_fields["module"] == settings.PACK_MODULE_PACK_MASTER)))
             or
             ((set(filter_fields.keys()) == {"pack_status", "module"}) and (
                     ("pack_status" in filter_fields and filter_fields["pack_status"] in
                      [settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS])
                     and ("module" in filter_fields and filter_fields["module"] == settings.PACK_MODULE_PACK_MASTER))))) \
                and (
                paginate and paginate["page_number"] * paginate["number_of_rows"] <= settings.NUMBER_OF_RECORDS_LIMIT):
            query = query.limit(settings.NUMBER_OF_RECORDS_LIMIT)
            limit_records = True
        if filter_fields and 'module' in filter_fields.keys():
            module = filter_fields['module']
            filter_fields.pop('module')
        if module == settings.PACK_MODULE_BATCH_DISTRIBUTION:
            clauses.extend((PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                           PackDetails.batch_id.is_null(True), PackUserMap.id.is_null(True)))
        if module == settings.PACK_MODULE_MANUAL_FILLING:
            clauses.extend((PackDetails.pack_status << settings.MANUAL_FILLING_STATUS,
                           PackUserMap.id.is_null(False)))
        if module == settings.PACK_MODULE_PACK_PRE:
            clauses.extend((BatchMaster.status << settings.PACK_PRE_BATCH_STATUS, PackDetails.batch_id.is_null(False),
                           PackUserMap.id.is_null(True)))
        if module == settings.PACK_MODULE_PACK_QUEUE:
            clauses.extend((BatchMaster.status == settings.BATCH_IMPORTED, PackUserMap.id.is_null(True),
                            PackDetails.pack_status << [
                                settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]))
        if module == settings.PACK_MODULE_PACK_MASTER:
            clauses.append((PackDetails.pack_status << [settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS,
                                                        settings.PROCESSED_MANUALLY_PACK_STATUS]))

        results, count = get_results(query.dicts(), fields_dict, clauses=clauses,
                                     filter_fields=filter_fields,
                                     exact_search_list=exact_search_list,
                                     paginate=paginate,
                                     like_search_list=like_search_list,
                                     between_search_list=between_search_list,
                                     membership_search_list=membership_search_list,
                                     limit_records=limit_records)
        for data in results:
            data['module'] = get_pack_module(pack_status=data['pack_status'], batch_id=data['batch_id'],
                                             batch_status=data['batch_status'],
                                             facility_dist_id=data['facility_dis_id'], user_id=data['pack_user_id'])

            if filter_fields.get('pack_display_id') or filter_fields.get('pack_id'):
                data['drug_info'] = get_required_and_filled_qty_of_pack(pack_id=data['pack_id'], company_id=company_id)
                try:
                    print_queue_requested = PrintQueue.select().where(PrintQueue.pack_id == data['pack_id']).get()
                    if print_queue_requested:
                        data['print_requested'] = "Yes"
                except DoesNotExist as e:
                    logger.info("No print queue requested for pack_id: {}".format(data['pack_id']))
                    data['print_requested'] = "No"
            else:
                data['drug_info'] = list()
                data['print_requested'] = None

        return count, results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_info_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_pack_info_dao {}".format(e))
        raise e


@log_args_and_response
def get_required_and_filled_qty_of_pack(pack_id, company_id):
    try:
        query = SlotDetails.select(DrugMaster.drug_name, fn.SUM(SlotDetails.quantity).alias('required_qty'),
                                   fn.IF(fn.SUM(DrugTracker.drug_quantity).is_null(True), 0,
                                         fn.SUM(DrugTracker.drug_quantity)).alias('filled_qty'), PatientRx.sig,
                                   DrugMaster.color, DrugMaster.ndc, DrugMaster.shape, DrugMaster.imprint,
                                   DrugMaster.image_name,
                                   fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                         DrugDetails.last_seen_by).alias('last_seen_with'),
                                   fn.IF(DrugStockHistory.is_in_stock.is_null(True), None,
                                         DrugStockHistory.is_in_stock).alias(
                                       "is_in_stock"),
                                   ).dicts() \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=((DrugMaster.formatted_ndc==UniqueDrug.formatted_ndc) & (DrugMaster.txr==UniqueDrug.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                        (DrugStockHistory.is_active == True) &
                                                        (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .where(PackRxLink.pack_id == pack_id) \
            .group_by(DrugMaster.id)

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_required_and_filled_qty_of_pack {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_required_and_filled_qty_of_pack {}".format(e))
        raise e


@log_args_and_response
def db_get_packs_with_status(pack_ids, status_list):
    status_pack_dict = {}
    try:
        query = PackDetails.select(PackDetails.id, PackDetails.pack_status).dicts() \
            .where(PackDetails.id << pack_ids, PackDetails.pack_status << status_list)

        for r in query:
            if status_pack_dict.get(r['pack_status'], []):
                status_pack_dict[r['pack_status']].append(r['id'])
            else:
                status_pack_dict[r['pack_status']] = [r['id']]

        return status_pack_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_required_and_filled_qty_of_pack {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_required_and_filled_qty_of_pack {}".format(e))
        raise e


@log_args_and_response
def db_get_prn_fill_details_dao(rx_id, pack_ids, pack_send_data, is_ltc, bill_id, queue_id, is_partial):
    try:
        is_ndc_change = False
        response = []
        query = PackDetails.select(PackDetails, PatientMaster.pharmacy_patient_id, FacilityMaster.pharmacy_facility_id,
                                   fn.SUM(SlotDetails.quantity).alias("qty"), DrugMaster.ndc,
                                   DrugMaster.pharmacy_drug_id.alias("initial_fill_drug_id"), PatientRx.to_fill_qty,
                                   DrugTracker.case_id, PackDetails.packaging_type, PatientRx.initial_fill_qty,
                                   PackDetails.queue_no).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientRx.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugTracker, JOIN_LEFT_OUTER,
                  on=((SlotDetails.id == DrugTracker.slot_id) & (DrugTracker.is_overwrite == 0))) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .where(PackRxLink.pack_id.in_(pack_ids)) \
            .group_by(PackDetails.id)   \
            .order_by(PackDetails.id)
        total_quantity = float((PackRxLink.select(fn.SUM(SlotDetails.quantity))
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id)
            .where(PackRxLink.pack_id.in_(pack_ids))).scalar())
        master_pack_id = None
        if query.exists():
            master_pack_id = list(query)[0]['pack_display_id']
        suggested_packaging = None

        for record in query:
            if len(pack_send_data.keys()) == 1:
                if pack_send_data[list(pack_send_data.keys())[0]][2] != record['ndc']:
                    is_ndc_change = True
            for packaging_type, value in constants.PACKAGING_TYPES.items():
                if value == record["packaging_type"]:
                    suggested_packaging = packaging_type
                    break
            response.append({
                "pack_id": record['pack_display_id'],
                "filled_by": record['filled_by'],
                "filled_days": record['filled_days'],
                "patient_id": record['pharmacy_patient_id'],
                "facility_id": record['pharmacy_facility_id'],
                "filled_time": get_current_date_time(),
                "filled_start": str(record['consumption_start_date']),
                "filled_end": str(record['consumption_end_date']),
                "rx_id": str(rx_id),
                "pack_total_qty": float(record['qty']),
                "orig_fill_check_id": master_pack_id,
                "fill_ndc": record['ndc'],
                "actual_fill_drug_id": int(pack_send_data[record["id"]][0]),
                "initial_fill_drug_id": int(record['initial_fill_drug_id']) if record.get('initial_fill_drug_id') else None,
                "original_qty": float(record["to_fill_qty"]),
                "filled_qty": total_quantity,
                "initial_qty": float(record["initial_fill_qty"]),
                "separate_pack_per_dose": False,
                "packing_type": "Unit",
                "true_unit": False,
                "customization": False,
                "case_id": record.get("case_id", None),
                "packaging_type": suggested_packaging,
                "drug_expiry": pack_send_data[record["id"]][1],
                "queue_no": str(record["queue_no"]),
                "is_ltc": is_ltc,
                "bill_id": bill_id,
                "queue_id": queue_id,
                "is_partial": is_partial,
                "filled_ndc": pack_send_data[record["id"]][2],
                "is_ndc_change": is_ndc_change
            })
        return response

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_prn_fill_details_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_prn_fill_details_dao {}".format(e))
        raise e


@log_args_and_response
def get_pack_grid_type(pack_ids):
    try:
        response = []
        query = PackDetails.select(PackDetails.id, PackDetails.pack_display_id,
                                   PackDetails.packaging_type).dicts()   \
            .where(PackDetails.id.in_(pack_ids))

        for data in query:
            response.append(data)

        return response

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_grid_type {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_pack_grid_type {}".format(e))
        raise e


@log_args_and_response
def call_to_ips_for_label(pack_display_ids, company_id):
    try:
        token = get_token()
        ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
        for pack_id in pack_display_ids:
            parameters = {
                "pack_id": pack_id
            }
            send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1],
                      webservice_url=settings.IPS_PRINT_LABEL,
                      parameters=parameters, counter=0, request_type="POST", token=token, ips_api=True)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_grid_type {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_pack_grid_type {}".format(e))
        raise e


@log_args_and_response
def db_get_slot_wise_hoa_for_pack(pack_id):
    try:
        query = SlotHeader.select(SlotHeader.hoa_time).dicts() \
            .where(SlotHeader.pack_id == pack_id)
        index = 1
        response = {}
        for record in query:
            response[str(index)] = {"hoa_time": record["hoa_time"]}
            index += 1
        return response
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_slot_wise_hoa_for_pack {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_slot_wise_hoa_for_pack {}".format(e))
        raise e


@log_args_and_response
def get_quadrant_and_device_from_location_number_dao(location_number):
    try:
        quadrant, device_id = LocationMaster.db_get_quadrant_and_device_from_location_number(location_number)
        return quadrant, device_id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_quadrant_and_device_from_location_number_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_quadrant_and_device_from_location_number_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_pack_status_dict(pack_ids):
    try:
        pack_status_dict = dict()
        query = (PackDetails.select(PackDetails.id, PackDetails.pack_status)
                 .dicts()
                 .where(PackDetails.id << pack_ids)
                 )

        for record in query:
            pack_status_dict[record["id"]] = record["pack_status"]

        return pack_status_dict
    except Exception as e:
        logger.error("Error in db_get_pack_status_dict: {}".format(e))
        raise e


@log_args_and_response
def insert_record_in_reuse_pack_drug(pack_ids, company_id, return_from_the_delivery_packs_status=False,
                                     return_from_the_delivery_packs=None):
    try:
        insert_list = list()
        insert_status = None
        ext_update_dict = dict()
        reuse_pack_drug_data = dict()
        reuse_pack_quantity_data = dict()
        reuse_pack_drug_insert_data = dict()
        create_data_for_elite = {"created": list()}

        PackDetailsAlias = PackDetails.alias()
        DrugTrackerAlias = DrugTracker.alias()

        pack_status_dict = db_get_pack_status_dict(pack_ids)

        if not return_from_the_delivery_packs_status:
            quantity_query = (DrugTracker.select(DrugTracker.pack_id,
                                                 DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr"),
                                                 fn.SUM(DrugTracker.drug_quantity).alias("quantity"),
                                                 fn.SUM(MfdAnalysisDetails.quantity).alias("mfd_quantity"),
                                                 fn.GROUP_CONCAT(
                                                     fn.DISTINCT(
                                                         MfdAnalysisDetails.status_id
                                                     )
                                                 ).alias("mfd_status")
                                                 )
                              .dicts()
                              .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id)
                              .join(MfdAnalysisDetails, JOIN_LEFT_OUTER,
                                    on=((MfdAnalysisDetails.slot_id == DrugTracker.slot_id) &
                                        (MfdAnalysisDetails.status_id << [constants.MFD_DRUG_DROPPED_STATUS,
                                                                          constants.MFD_DRUG_MVS_FILLED])))
                              .where((DrugTracker.pack_id << pack_ids) & (DrugTracker.is_overwrite == 0))
                              .group_by(DrugMaster.concated_fndc_txr_field(sep="##"), DrugTracker.pack_id)
                              )

            for record in quantity_query:
                if record["pack_id"] not in reuse_pack_quantity_data:
                    reuse_pack_quantity_data[record["pack_id"]] = dict()

                if record["fndc_txr"] not in reuse_pack_quantity_data[record["pack_id"]]:
                    if record["mfd_status"]:
                        mfd_status_list = record["mfd_status"].split(",")
                        if (str(constants.MFD_DRUG_DROPPED_STATUS)
                                in mfd_status_list or str(constants.MFD_DRUG_MVS_FILLED) in mfd_status_list):
                            reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] = record["mfd_quantity"]
                        else:
                            reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] = record["quantity"]
                    else:
                        reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] = record["quantity"]
        else:
            for pack_display_id, pack_data in return_from_the_delivery_packs.items():
                quantity_query = (SlotDetails.select(fn.SUM(DrugTracker.drug_quantity).alias("quantity"),
                                                     DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr"),
                                                     PatientRx.pharmacy_rx_no,
                                                     PackDetails.id.alias("pack_id"),
                                                     fn.SUM(MfdAnalysisDetails.quantity).alias("mfd_quantity"),
                                                     fn.GROUP_CONCAT(
                                                         fn.DISTINCT(
                                                             MfdAnalysisDetails.status_id
                                                         )
                                                     ).alias("mfd_status")
                                                     )
                                  .dicts()
                                  .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                  .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                  .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id)
                                  .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                                  .join(DrugTracker, on=SlotDetails.id == DrugTracker.slot_id)
                                  .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id)
                                  .join(MfdAnalysisDetails, JOIN_LEFT_OUTER,
                                        on=((MfdAnalysisDetails.slot_id == DrugTracker.slot_id) &
                                            (MfdAnalysisDetails.status_id << [constants.MFD_DRUG_DROPPED_STATUS,
                                                                              constants.MFD_DRUG_MVS_FILLED])))
                                  .where((PackDetails.pack_display_id == pack_display_id) &
                                         (DrugTracker.is_overwrite == 0))
                                  .group_by(SlotHeader.id, DrugMaster.concated_fndc_txr_field(sep="##"))
                                  .order_by(SlotHeader.hoa_date.desc())
                                  )

                for record in quantity_query:
                    if record["pack_id"] not in reuse_pack_quantity_data:
                        reuse_pack_quantity_data[record["pack_id"]] = dict()

                    if record["pharmacy_rx_no"] in pack_data:
                        if record["fndc_txr"] not in reuse_pack_quantity_data[record["pack_id"]]:
                            reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] = 0.0

                        if record["mfd_status"]:
                            mfd_status_list = record["mfd_status"].split(",")
                            if (str(constants.MFD_DRUG_DROPPED_STATUS)
                                    in mfd_status_list or str(constants.MFD_DRUG_MVS_FILLED) in mfd_status_list):
                                if pack_data[record["pharmacy_rx_no"]]["available_quantity"] > record["mfd_quantity"]:
                                    reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] += float(
                                        record["mfd_quantity"])

                                    pack_data[record["pharmacy_rx_no"]]["available_quantity"] -= float(
                                        record["mfd_quantity"])

                                elif pack_data[record["pharmacy_rx_no"]]["available_quantity"] > 0:
                                    reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] += (float(
                                        pack_data[record["pharmacy_rx_no"]]["available_quantity"]))

                                    pack_data[record["pharmacy_rx_no"]]["available_quantity"] -= float(
                                        pack_data[record["pharmacy_rx_no"]]["available_quantity"])

                            else:
                                reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] += float(
                                    record["quantity"])

                                pack_data[record["pharmacy_rx_no"]]["available_quantity"] -= float(record["quantity"])

                        else:
                            if pack_data[record["pharmacy_rx_no"]]["available_quantity"] > record["quantity"]:
                                reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] += float(
                                    record["quantity"])

                                pack_data[record["pharmacy_rx_no"]]["available_quantity"] -= float(record["quantity"])

                            elif pack_data[record["pharmacy_rx_no"]]["available_quantity"] > 0:
                                reuse_pack_quantity_data[record["pack_id"]][record["fndc_txr"]] += (float(
                                    pack_data[record["pharmacy_rx_no"]]["available_quantity"]))

                                pack_data[record["pharmacy_rx_no"]]["available_quantity"] -= float(
                                    pack_data[record["pharmacy_rx_no"]]["available_quantity"])

        logger.info("In insert_record_in_reuse_pack_drug: reuse_pack_quantity_data: {}".format(reuse_pack_quantity_data)
                    )
        # print(reuse_pack_quantity_data)

        select_fields = [DrugTracker.pack_id,
                         PackDetails.pack_display_id,
                         DrugTracker.drug_id,
                         DrugMaster.ndc,
                         DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr"),
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(
                                 fn.CONCAT(CanisterTracker.lot_number, "_",
                                           CanisterTracker.expiration_date, "_",
                                           fn.IF(CanisterTracker.case_id.is_null(True),
                                                 "",
                                                 CanisterTracker.case_id
                                                 )
                                           )
                             )).alias("canister_tracker_lot_expiry_case_id"),
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(fn.IF(DrugTracker.canister_id.is_null(True),
                                               fn.CONCAT(DrugTracker.lot_number, "_",
                                                         DrugTracker.expiry_date, "_",
                                                         fn.IF(DrugTracker.case_id.is_null(True),
                                                               "",
                                                               DrugTracker.case_id)),
                                               None
                                               )
                                         )).alias("drug_lot_expiry_case_id"),
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(
                                 MfdAnalysisDetails.status_id
                             )).alias("mfd_status"),
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(
                                 DrugTracker.id
                             )).alias("drug_tracker_ids"),
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(
                                 DrugTrackerAlias.item_id
                             )).alias("item_ids"),
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(
                                 DrugTrackerAlias.pack_id
                             )).alias("reuse_pack")
                         ]

        query = (PackDetails.select(*select_fields)
                 .dicts()
                 .join(DrugTracker, on=PackDetails.id == DrugTracker.pack_id)
                 .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id)
                 .join(PackDetailsAlias, JOIN_LEFT_OUTER, on=PackDetailsAlias.id == DrugTracker.reuse_pack)
                 .join(DrugTrackerAlias, JOIN_LEFT_OUTER, on=((PackDetailsAlias.id == DrugTrackerAlias.pack_id) &
                                                              (DrugMaster.id == DrugTrackerAlias.drug_id)))
                 .join(CanisterTracker, JOIN_LEFT_OUTER, on=CanisterTracker.id == DrugTracker.canister_tracker_id)
                 .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == DrugTracker.slot_id)
                 .where(DrugTracker.pack_id << pack_ids)
                 .group_by(DrugTracker.pack_id, DrugMaster.concated_fndc_txr_field(sep="##"))
                 .order_by(DrugTracker.pack_id)
                 )

        for record in query:

            if record["pack_id"] not in reuse_pack_drug_data:
                reuse_pack_drug_data[record["pack_id"]] = dict()
                reuse_pack_drug_data[record["pack_id"]]["pack_display_id"] = record["pack_display_id"]

            if record["fndc_txr"] not in reuse_pack_quantity_data[record["pack_id"]]:
                continue

            if record["fndc_txr"] not in reuse_pack_drug_data[record["pack_id"]]:
                drug_reuse_allowed = False
                if record["mfd_status"]:
                    mfd_status_list = record["mfd_status"].split(",")
                    if (str(constants.MFD_DRUG_DROPPED_STATUS)
                            in mfd_status_list or str(constants.MFD_DRUG_MVS_FILLED) in mfd_status_list):
                        drug_reuse_allowed = True
                else:
                    drug_reuse_allowed = True

                if drug_reuse_allowed:
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]] = dict()
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["drug_id"] = record["drug_id"]
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["ndc"] = record["ndc"]
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["expiry_date"] = None
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["quantity"] = reuse_pack_quantity_data[
                        record["pack_id"]][record["fndc_txr"]]
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["drug_tracker_ids"] = record[
                        "drug_tracker_ids"].split(",")

                    if pack_status_dict[record["pack_id"]] in settings.PROGRESS_PACK_STATUS_LIST:
                        reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["packInProgress"] = True
                    else:
                        reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["packInProgress"] = False

                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["source_items"] = []

                    if record["item_ids"]:
                        item_ids = record["item_ids"].split(",")
                        for item in item_ids:
                            temp_query = (DrugTracker.select(DrugTracker.drug_quantity, DrugTracker.scan_type,
                                                             DrugTrackerAlias.item_id, DrugTrackerAlias.lot_number,
                                                             DrugTrackerAlias.expiry_date
                                                             )
                                          .dicts()
                                          .join(DrugTrackerAlias, on=DrugTracker.reuse_pack == DrugTrackerAlias.pack_id)
                                          .where(DrugTracker.pack_id == record["pack_id"],
                                                 DrugTrackerAlias.item_id == item)
                                          .group_by(DrugTracker.id))

                            temp_lot_info = {"lotNo": None,
                                             "expirationDate": None,
                                             "caseId": None,
                                             "quantity": 0,
                                             "filledByCanister": False}

                            for lot_info in temp_query:
                                if lot_info["item_id"] != temp_lot_info["caseId"]:
                                    temp_lot_info = {"lotNo": lot_info["lot_number"],
                                                     "expirationDate": lot_info["expiry_date"],
                                                     "caseId": lot_info["item_id"],
                                                     "quantity": 0,
                                                     "filledByCanister": False}

                                temp_lot_info["quantity"] += float(lot_info["drug_quantity"])

                            reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["source_items"].append(temp_lot_info)

                    if record["reuse_pack"]:
                        reuse_packs = record["reuse_pack"].split(",")

                        ext_query = (ExtPackDetails.select(ExtPackDetails.packs_delivery_status,
                                                           ExtPackDetails.pack_id)
                                     .dicts()
                                     .where(ExtPackDetails.pack_id << reuse_packs))

                        for ext_record in ext_query:
                            if ext_record["packs_delivery_status"] == constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID:
                                ext_update_dict = {record["pack_id"]: constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID}
                                return_from_the_delivery_packs_status = True
                                break

                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                        "canister_tracker_lot_expiry_case_id"] = list()
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["drug_lot_expiry_case_id"] = list()
                else:
                    continue

            if record["canister_tracker_lot_expiry_case_id"]:
                canister_tracker_lot_expiry_case_id = record["canister_tracker_lot_expiry_case_id"].split(",")
                for item_1 in canister_tracker_lot_expiry_case_id:
                    canister_tracker_lot_data = item_1.split("_")

                    canister_tracker_lot_data_dict = {"lotNo": canister_tracker_lot_data[0],
                                                      "expirationDate": canister_tracker_lot_data[1],
                                                      "caseId": canister_tracker_lot_data[2] if canister_tracker_lot_data[2] else None
                                                      }
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                        "canister_tracker_lot_expiry_case_id"].append(canister_tracker_lot_data_dict)

                    canister_tracker_lot_data_query = (DrugTracker.select(DrugTracker.case_id,
                                                                          DrugTracker.lot_number,
                                                                          fn.SUM(
                                                                              DrugTracker.drug_quantity
                                                                          ).alias("quantity"),
                                                                          DrugTracker.expiry_date)
                                                       .dicts()
                                                       .where(DrugTracker.lot_number == canister_tracker_lot_data[0],
                                                              DrugTracker.pack_id == record["pack_id"]
                                                              ))

                    if canister_tracker_lot_data[2]:
                        canister_tracker_lot_data_query = (canister_tracker_lot_data_query
                                                           .where(DrugTracker.case_id == canister_tracker_lot_data[2]))
                        canister_tracker_lot_data_query = (canister_tracker_lot_data_query
                                                           .group_by(DrugTracker.case_id))

                    canister_tracker_lot_data_query = (canister_tracker_lot_data_query
                                                       .group_by(DrugTracker.lot_number))

                    add_source_item = True
                    temp_lot_info = {"lotNo": None,
                                     "expirationDate": None,
                                     "caseId": None,
                                     "quantity": 0,
                                     "filledByCanister": False}

                    for data in canister_tracker_lot_data_query:
                        temp_lot_info = {"lotNo": data["lot_number"],
                                         "expirationDate": data["expiry_date"],
                                         "caseId": data["case_id"],
                                         "quantity": float(data["quantity"]),
                                         "filledByCanister": True}

                        for source_item in reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["source_items"]:
                            if data["case_id"] == source_item["caseId"]:
                                add_source_item = False
                                break

                    if add_source_item:
                        reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["source_items"].append(temp_lot_info)

                    if reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["expiry_date"] is None:
                        reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["expiry_date"] = (
                            canister_tracker_lot_data)[1]
                    else:
                        date_1 = datetime.datetime.strptime(reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                                                                "expiry_date"], "%m-%Y").date()
                        date_1 = last_day_of_month(date_1)

                        date_2 = datetime.datetime.strptime(canister_tracker_lot_data[1], "%m-%Y").date()
                        date_2 = last_day_of_month(date_2)

                        if date_2 < date_1:
                            reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                                "expiry_date"] = date_2.strftime("%m-%Y")

            if record["drug_lot_expiry_case_id"]:
                drug_lot_expiry_case_id = record["drug_lot_expiry_case_id"].split(",")
                for item_2 in drug_lot_expiry_case_id:
                    drug_lot_data = item_2.split("_")

                    drug_lot_data_dict = {"lotNo": drug_lot_data[0],
                                          "expirationDate": drug_lot_data[1],
                                          "caseId": drug_lot_data[2] if drug_lot_data[2] else None
                                          }
                    reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                        "drug_lot_expiry_case_id"].append(drug_lot_data_dict)

                    drug_lot_data_dict_query = (DrugTracker.select(DrugTracker.case_id,
                                                                   DrugTracker.lot_number,
                                                                   fn.SUM(
                                                                       DrugTracker.drug_quantity
                                                                   ).alias("quantity"),
                                                                   DrugTracker.expiry_date)
                                                .dicts()
                                                .where(DrugTracker.lot_number == drug_lot_data[0],
                                                       DrugTracker.pack_id == record["pack_id"]
                                                       ))

                    if drug_lot_data[2]:
                        drug_lot_data_dict_query = (drug_lot_data_dict_query
                                                    .where(DrugTracker.case_id == drug_lot_data[2]))
                        drug_lot_data_dict_query = (drug_lot_data_dict_query.group_by(DrugTracker.case_id))

                    drug_lot_data_dict_query = (drug_lot_data_dict_query.group_by(DrugTracker.lot_number))

                    add_source_item = True
                    temp_lot_info = {"lotNo": None,
                                     "expirationDate": None,
                                     "caseId": None,
                                     "quantity": 0,
                                     "filledByCanister": False}

                    for data in drug_lot_data_dict_query:
                        temp_lot_info = {"lotNo": data["lot_number"],
                                         "expirationDate": data["expiry_date"],
                                         "caseId": data["case_id"],
                                         "quantity": float(data["quantity"]),
                                         "filledByCanister": False}

                        for source_item in reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["source_items"]:
                            if data["case_id"] == source_item["caseId"]:
                                add_source_item = False
                                break

                    if add_source_item:
                        reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["source_items"].append(
                            temp_lot_info)

                    if reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["expiry_date"] is None:
                        reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]]["expiry_date"] = (
                            drug_lot_data)[1]
                    else:
                        date_1 = datetime.datetime.strptime(reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                                                                "expiry_date"], "%m-%Y").date()
                        date_1 = last_day_of_month(date_1)

                        date_2 = datetime.datetime.strptime(drug_lot_data[1], "%m-%Y").date()
                        date_2 = last_day_of_month(date_2)

                        if date_2 < date_1:
                            reuse_pack_drug_data[record["pack_id"]][record["fndc_txr"]][
                                "expiry_date"] = date_2.strftime("%m-%Y")

        logger.info(
            "In insert_record_in_reuse_pack_drug: reuse_pack_drug_data: {}".format(reuse_pack_drug_data))
        # print(reuse_pack_drug_data)

        for pack_id, pack_data in reuse_pack_drug_data.items():
            pack_display_id = None
            ndc_count = 1
            for fndc_txr, fndc_txr_data in pack_data.items():
                if fndc_txr == "pack_display_id":
                    pack_display_id = fndc_txr_data
                    continue

                lot_details = list()

                if fndc_txr_data["canister_tracker_lot_expiry_case_id"]:
                    for lot_detail in fndc_txr_data["canister_tracker_lot_expiry_case_id"]:
                        lot_details.append(lot_detail)

                if fndc_txr_data["drug_lot_expiry_case_id"]:
                    for lot_detail in fndc_txr_data["drug_lot_expiry_case_id"]:
                        lot_details.append(lot_detail)

                if len(lot_details) > 1:
                    lot = "P" + str(pack_display_id) + "N" + str(ndc_count)
                    ndc_count += 1
                else:
                    lot = lot_details[0]["lotNo"]

                create_record_for_elite = {"department": "dosepack",
                                           "ndc": fndc_txr_data["ndc"],
                                           "lot": lot,
                                           "exp": fndc_txr_data["expiry_date"],
                                           "qty": float(fndc_txr_data["quantity"]),
                                           "create": settings.ITEM,
                                           "sourceItems": fndc_txr_data["source_items"],
                                           "packId": pack_display_id,
                                           "adjustmentDate": convert_utc_timezone_into_local_time_zone(),
                                           "packType": settings.REUSE_PACK if return_from_the_delivery_packs_status else settings.ITEM,
                                           "lotDetails": lot_details,
                                           "packInProgress": fndc_txr_data["packInProgress"]
                                           }

                create_data_for_elite["created"].append(create_record_for_elite)

                if pack_id not in reuse_pack_drug_insert_data:
                    reuse_pack_drug_insert_data[pack_id] = dict()

                if fndc_txr_data["ndc"] not in reuse_pack_drug_insert_data[pack_id]:
                    reuse_pack_drug_insert_data[pack_id][fndc_txr_data["ndc"]] = list()

                create_record = {"item_id": None,
                                 "pack_id": pack_id,
                                 "drug_id": fndc_txr_data["drug_id"],
                                 "lot_number": lot,
                                 "total_quantity": fndc_txr_data["quantity"],
                                 "available_quantity": fndc_txr_data["quantity"],
                                 "status_id": constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_ID,
                                 "expiry_date": fndc_txr_data["expiry_date"],
                                 "company_id": company_id,
                                 "drug_tracker_ids": fndc_txr_data["drug_tracker_ids"]
                                 }

                reuse_pack_drug_insert_data[pack_id][fndc_txr_data["ndc"]].append(create_record)

        logger.info("In insert_record_in_reuse_pack_drug: reuse_pack_drug_insert_data: {}"
                    .format(reuse_pack_drug_insert_data))

        # print(reuse_pack_drug_insert_data)

        logger.info("In insert_record_in_reuse_pack_drug: create_data_for_elite: {}"
                    .format(create_data_for_elite))

        # print(create_data_for_elite)
        logger.info("In insert_record_in_reuse_pack_drug: sending call to elite for item generation***")
        inventory_resp = create_item_vial_generation_for_rts_reuse_pack(create_data_for_elite)
        if inventory_resp:
            for record in inventory_resp["created"]:
                pack_id = PackDetails.select(PackDetails.id).dicts().where(
                    PackDetails.pack_display_id == record["PackId"]).get()
                pack_id = pack_id["id"]
                reuse_pack_drug_insert_data[pack_id][str(record["Ndc"])][0]["item_id"] = record["ItemId"]
                drug_tracker_ids = reuse_pack_drug_insert_data[pack_id][str(record["Ndc"])][0].pop("drug_tracker_ids")

                query = (DrugTracker.update(item_id=record["ItemId"],
                                            modified_date=get_current_date_time()
                                            )
                         .where(DrugTracker.pack_id == pack_id,
                                DrugTracker.id << drug_tracker_ids
                                )
                         ).execute()

                insert_list.append(reuse_pack_drug_insert_data[pack_id][str(record["Ndc"])][0])

        logger.info("In insert_record_in_reuse_pack_drug: insert_list: {}".format(insert_list))
        # print(insert_list)

        if insert_list:
            insert_status = ReusePackDrug.insert_multiple_record_in_reuse_pack_drug(insert_list)
            logger.info("In insert_record_in_reuse_pack_drug: insert_status: {}".format(insert_status))

        return insert_status, ext_update_dict

    except Exception as e:
        logger.error("Error in insert_record_in_reuse_pack_drug: {}".format(e))
        raise e


@log_args_and_response
def get_reusable_pack_dao(company_id, filter_fields, sort_fields, paginate):
    try:
        debug_mode_flag = False
        sort_by_drug_name = None

        if filter_fields and filter_fields.get('pack_display_id') and filter_fields.get('pack_id'):
            debug_mode_flag = True

        fields_dict = {"pack_id": PackDetails.id,
                       "pack_display_id": PackDetails.pack_display_id,
                       "facility_name": FacilityMaster.facility_name,
                       "patient_name": fn.CONCAT(PatientMaster.first_name, ", ", PatientMaster.last_name),
                       "admin_start_date": fn.DATE(PackDetails.consumption_start_date),
                       "admin_end_date": fn.DATE(PackDetails.consumption_end_date),
                       "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
                       "pack_delivery_status": ExtPackDetails.packs_delivery_status
                       }

        """
        below logic created because we have to perform the sorting of more than one drug of one pack
        """
        if sort_fields:
            index = None
            for sort_data in sort_fields:
                if sort_data[0] == "drug_name":
                    index = sort_fields.index(sort_data)
                    if sort_data[1] == -1:
                        sort_by_drug_name = -1
                        # query = query.order_by(SQL("drug_name").desc())
                    else:
                        sort_by_drug_name = 1
                        # query = query.order_by(SQL("drug_name"))
                    break

            if index or index == 0:
                sort_fields.pop(index)

        sub_q = fields_dict["drug_name"]
        if sort_by_drug_name == -1:
            sub_q = fn.GROUP_CONCAT(Clause(SQL('DISTINCT'), fields_dict["drug_name"], SQL('ORDER BY'),
                                           fields_dict["drug_name"], SQL('DESC'))).alias("drug_name")
        elif sort_by_drug_name == 1:
            sub_q = fn.GROUP_CONCAT(Clause(SQL('DISTINCT'), fields_dict["drug_name"], SQL('ORDER BY'),
                                           fields_dict["drug_name"])).alias("drug_name")

        select_fields = [PackDetails.id.alias("pack_id"),
                         fields_dict["pack_display_id"],
                         fn.GROUP_CONCAT(
                             fn.DISTINCT(
                                 fn.CONCAT(ReusePackDrug.drug_id, "_",
                                           ReusePackDrug.total_quantity, "_",
                                           ReusePackDrug.available_quantity, "_",
                                           ReusePackDrug.expiry_date, "_",
                                           ReusePackDrug.lot_number, "_",
                                           ReusePackDrug.item_id
                                           )
                             )
                         ).alias("reuse_drug_data"),
                         fields_dict["patient_name"].alias("patient_name"),
                         fields_dict["facility_name"],
                         fields_dict["admin_start_date"].alias("admin_start_date"),
                         fields_dict["admin_end_date"].alias("admin_end_date"),
                         PatientMaster.id.alias("patient_id"),
                         sub_q,
                         # fields_dict["drug_name"],
                         PatientMaster.dob,
                         fields_dict["pack_delivery_status"],
                         fn.MIN(fn.STR_TO_DATE(ReusePackDrug.expiry_date, "%m-%Y")).alias("pack_expiry")
                         ]

        clauses = [ExtPackDetails.pack_usage_status_id << [constants.EXT_PACK_USAGE_STATUS_PENDING_ID,
                                                           constants.EXT_PACK_USAGE_STATUS_PACK_RESEALED_ID],
                   ReusePackDrug.status_id << [constants.REUSE_DRUG_STATUS_DRUG_RESEALED_ID,
                                               constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_ID],
                   ReusePackDrug.company_id == company_id
                   ]

        if debug_mode_flag:
            like_search_list = ['facility_name', 'patient_name', 'drug_name']
            string_search_field = [fields_dict['pack_display_id'], fields_dict['pack_id']]
            multi_search_fields = [filter_fields['pack_display_id']]
            clauses = get_multi_search(clauses=clauses,
                                       multi_search_values=multi_search_fields,
                                       model_search_fields=string_search_field
                                       )
            filter_fields.pop('pack_id')
            filter_fields.pop('pack_display_id')

        else:
            like_search_list = ['pack_display_id', 'facility_name', 'patient_name', 'drug_name']

        exact_search_list = ['pack_delivery_status']

        query = (ReusePackDrug.select(*select_fields)
                 .join(PackDetails, on=PackDetails.id == ReusePackDrug.pack_id)
                 .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                 .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id)
                 .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)
                 .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                 .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id)
                 .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id)
                 )

        query = query.group_by(PackDetails.id)

        order_list = list()

        if sort_fields:
            order_list.extend(sort_fields)
        else:
            if sort_by_drug_name == -1:
                query = query.order_by(SQL("drug_name").desc())
            elif sort_by_drug_name == 1:
                query = query.order_by(SQL("drug_name"))
            else:
                query = query.order_by(SQL("pack_expiry"))

        results, count = get_results(query.dicts(), fields_dict, clauses=clauses,
                                     filter_fields=filter_fields,
                                     sort_fields=order_list,
                                     paginate=paginate,
                                     like_search_list=like_search_list,
                                     exact_search_list=exact_search_list
                                     )

        logger.info("In get_reusable_pack_dao: results: {}, count: {}".format(results, count))

        total_patient_query = (ReusePackDrug.select(PatientMaster.id).dicts()
                               .join(PackDetails, on=PackDetails.id == ReusePackDrug.pack_id)
                               .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                               .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id)
                               .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)
                               .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                               .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id)
                               .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id)
                               .where(*clauses)
                               .group_by(PatientMaster.id)
                               )

        logger.info("In get_reusable_pack_dao: total_patient_query: {}".format(total_patient_query))

        total_patient = total_patient_query.count()

        logger.info("In get_reusable_pack_dao: total_patient: {}".format(total_patient))

        total_facility_query = (ReusePackDrug.select(FacilityMaster.id).dicts()
                                .join(PackDetails, on=PackDetails.id == ReusePackDrug.pack_id)
                                .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                                .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id)
                                .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)
                                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id)
                                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id)
                                .where(*clauses)
                                .group_by(FacilityMaster.id)
                                )

        logger.info("In get_reusable_pack_dao: total_facility_query: {}".format(total_facility_query))

        total_facility = total_facility_query.count()

        logger.info("In get_reusable_pack_dao: total_facility: {}".format(total_facility))

        reuse_pack_drug_data = {"total_packs": count,
                                "total_patient": total_patient,
                                "total_facility": total_facility,
                                "expiry_flag": settings.DISCARDED_REUSE_PACK,
                                "pack_list": list()
                                }

        for record in results:
            ndc_list = list()
            temp_pack_dict = {"pack_id": record["pack_id"],
                              "pack_display_id": record["pack_display_id"],
                              "patient_name": record["patient_name"],
                              "patient_id": record["patient_id"],
                              "patient_dob": record["dob"],
                              "facility_name": record["facility_name"],
                              "admin_start_date": record["admin_start_date"],
                              "admin_end_date": record["admin_end_date"],
                              "pack_delivery_status": record["packs_delivery_status"],
                              "drug_list": list(),
                              "is_pack_expired": 0,
                              "pack_expiry_date": None
                              }

            reuse_drug_data = record["reuse_drug_data"].split(",")
            for drug_data in reuse_drug_data:
                data = drug_data.split("_")
                if float(data[2]) > 0:
                    drug_master_select_fields = [DrugMaster,
                                                 DrugMaster.concated_drug_name_field(include_ndc=True).alias(
                                                     "drug_image_name"),
                                                 DrugDetails.last_seen_by]
                    drug_master_data = (DrugMaster.select(*drug_master_select_fields).dicts()
                                        .join(UniqueDrug, on=((fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                                              fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                                              (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)))
                                        .join(DrugDetails, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDetails.unique_drug_id)
                                        .where(DrugMaster.id == data[0])
                                        .group_by(DrugMaster.ndc)
                                        )
                    temp_drug_dict = dict()
                    for drug_info in drug_master_data:
                        ndc_list.append(int(drug_info["ndc"]))
                        temp_drug_dict = {"ndc": drug_info["ndc"],
                                          "drug_id": drug_info["id"],
                                          "imprint": drug_info["imprint"],
                                          "image_name": drug_info["image_name"],
                                          "shape": drug_info["shape"],
                                          "color": drug_info["color"],
                                          "drug_name": drug_info["drug_image_name"],
                                          "strength": drug_info["strength"],
                                          "strength_value": drug_info["strength_value"],
                                          "expiry_date": data[3],
                                          "total_quantity": data[1],
                                          "is_expired": 0,
                                          "available_quantity": data[2],
                                          "lot_number": data[4],
                                          "item_id": data[5],
                                          "last_seen_with": drug_info.get("last_seen_by", None),
                                          "is_in_stock": None
                                          }

                    date_1 = datetime.datetime.strptime(data[3], "%m-%Y").date()
                    date_1 = last_day_of_month(date_1)

                    if date_1 < datetime.datetime.today().date():
                        temp_drug_dict["is_expired"] = 1
                        if settings.DISCARDED_REUSE_PACK:
                            temp_pack_dict["is_pack_expired"] = 1

                    if temp_pack_dict["pack_expiry_date"] is None:
                        temp_pack_dict["pack_expiry_date"] = date_1.strftime("%m-%Y")
                    else:
                        date_2 = datetime.datetime.strptime(temp_pack_dict["pack_expiry_date"], "%m-%Y").date()
                        date_2 = last_day_of_month(date_2)

                        if date_1 < date_2:
                            temp_pack_dict["pack_expiry_date"] = date_1.strftime("%m-%Y")

                    if temp_drug_dict:
                        temp_pack_dict["drug_list"].append(temp_drug_dict)

            if sort_by_drug_name == -1:
                temp_pack_dict["drug_list"].sort(key=lambda x: x['drug_name'], reverse=True)
            elif sort_by_drug_name == 1:
                temp_pack_dict["drug_list"].sort(key=lambda x: x['drug_name'])

            if ndc_list:
                inventory_data = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
                logger.info("get_reusable_pack_dao: inventory_data: {}".format(inventory_data))
                if inventory_data:
                    for ndc_record in inventory_data:
                        for d_data in temp_pack_dict["drug_list"]:
                            if ndc_record["ndc"] == d_data["ndc"]:
                                d_data["is_in_stock"] = 1 if ndc_record["quantity"] > 0 else 0

            reuse_pack_drug_data["pack_list"].append(temp_pack_dict)

        # reuse_pack_drug_data["pack_list"].sort(key=lambda x: datetime.datetime.strptime(x['pack_expiry_date'], '%m-%Y'))

        return create_response(reuse_pack_drug_data)

    except Exception as e:
        logger.error(f"Error in get_reusable_pack_dao: {e}")
        raise e


@log_args_and_response
def db_fetch_reuse_pack_data(reuse_pack_id, similar_pack_ids):
    try:
        drug_ids_list = list()
        reuse_pack_data = dict()
        reuse_pack_patient = None
        pack_delivery_status = None
        similar_packs_patient = None

        reuse_pack_patient_query = (PackDetails.select(PackHeader.patient_id, ExtPackDetails.packs_delivery_status)
                                    .dicts()
                                    .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id)
                                    .join(ExtPackDetails, JOIN_LEFT_OUTER, on=PackDetails.id == ExtPackDetails.pack_id)
                                    .where(PackDetails.id == reuse_pack_id)
                                    .group_by(PackHeader.id))

        for record in reuse_pack_patient_query:
            reuse_pack_patient = record["patient_id"]
            pack_delivery_status = record["packs_delivery_status"]

        similar_packs_patient_query = (PackDetails.select(PackHeader.patient_id)
                                       .dicts()
                                       .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id)
                                       .where(PackDetails.id << similar_pack_ids)
                                       .group_by(PackHeader.id))

        for record in similar_packs_patient_query:
            similar_packs_patient = record["patient_id"]

        if similar_packs_patient != reuse_pack_patient:
            if pack_delivery_status is None or pack_delivery_status == constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID:
                return 21016

        query = ReusePackDrug.db_get_reuse_pack_drug_data_by_pack_id([reuse_pack_id])

        for record in query:
            if record["status_id"] in (constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_ID,
                                       constants.REUSE_DRUG_STATUS_DRUG_RESEALED_ID):
                drug_ids_list.append(record["drug_id"])

        if drug_ids_list:
            reuse_pack_data_query = (ReusePackDrug.select(DrugMaster.txr,
                                                          fn.GROUP_CONCAT(
                                                              fn.DISTINCT(
                                                                  fn.CONCAT(DrugMaster.formatted_ndc, "_",
                                                                            DrugMaster.id, "_",
                                                                            ReusePackDrug.item_id, "_",
                                                                            ReusePackDrug.available_quantity, "_",
                                                                            DrugMaster.brand_flag, "_",
                                                                            ReusePackDrug.expiry_date, "_",
                                                                            ReusePackDrug.lot_number
                                                                            )
                                                              )
                                                          ).alias("item_id_quantity"),
                                                          ReusePackDrug.pack_id,
                                                          PatientRx.patient_id
                                                          )
                                     .dicts()
                                     .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                                     .join(PackDetails, on=PackDetails.id == ReusePackDrug.pack_id)
                                     .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)
                                     .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                     .where(ReusePackDrug.pack_id == reuse_pack_id,
                                            ReusePackDrug.status_id << [constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_ID,
                                                                        constants.REUSE_DRUG_STATUS_DRUG_RESEALED_ID]
                                            )
                                     .group_by(DrugMaster.txr, ReusePackDrug.pack_id)
                                     )

            logger.info("In db_fetch_reuse_pack_data: reuse_pack_data_query: {}".format(reuse_pack_data_query))

            max_pack_consumption_end_date = (PackDetails.select(fn.MAX(PackDetails.consumption_end_date))
                                             .where(PackDetails.id << similar_pack_ids).scalar())

            for record in reuse_pack_data_query:
                if record["pack_id"] not in reuse_pack_data:
                    reuse_pack_data[record["pack_id"]] = dict()
                    reuse_pack_data[record["pack_id"]]["patient_id"] = record["patient_id"]

                if record["txr"] not in reuse_pack_data[record["pack_id"]]:
                    reuse_pack_data[record["pack_id"]][record["txr"]] = dict()
                    fndc_item_quantity = record["item_id_quantity"].split(",")
                    for item in fndc_item_quantity:
                        fndc_item_quantity_data = item.split("_")
                        expiry = datetime.datetime.strptime(fndc_item_quantity_data[5], "%m-%Y").date()
                        expiry = last_day_of_month(expiry)
                        if expiry > max_pack_consumption_end_date + datetime.timedelta(settings.EXPIRED_DRUG_DAYS):
                            if fndc_item_quantity_data[0] not in reuse_pack_data[record["pack_id"]][record["txr"]]:
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]] = dict()
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "drug_id"] = (
                                    fndc_item_quantity_data)[1]
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "item_id"] = (
                                    fndc_item_quantity_data)[2]
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "total_quantity"] = float(fndc_item_quantity_data[3])
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "available_quantity"] = float(fndc_item_quantity_data[3])
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "brand_flag"] = (
                                    fndc_item_quantity_data)[4]
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "expiry_date"] = (
                                    fndc_item_quantity_data)[5]
                                reuse_pack_data[record["pack_id"]][record["txr"]][fndc_item_quantity_data[0]][
                                    "lot_number"] = (
                                    fndc_item_quantity_data)[6]
                        else:
                            return None
        else:
            return 21016
        return reuse_pack_data
    except Exception as e:
        logger.error("Error in db_fetch_reuse_pack_data: {}".format(e))
        raise e


@log_args_and_response
def db_fetch_similar_pack_data(similar_pack_ids):
    try:
        select_fields = [DrugMaster.txr,
                         PatientRx.daw_code,
                         PackGrid.slot_number,
                         PatientRx.patient_id,
                         DrugMaster.brand_flag,
                         DrugMaster.formatted_ndc,
                         DrugMaster.id.alias("drug_id"),
                         PackDetails.id.alias("pack_id"),
                         SlotDetails.id.alias("slot_details_id"),
                         fn.SUM(fn.DISTINCT(SlotDetails.quantity)).alias("required_quantity"),
                         fn.SUM(DrugTracker.drug_quantity).alias("filled_quantity")
                         ]

        similar_pack_data_query = (SlotDetails.select(*select_fields)
                                   .dicts()
                                   .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                   .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id)
                                   .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                                   .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)
                                   .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                                   .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                   .join(DrugTracker, JOIN_LEFT_OUTER, on=SlotDetails.id == DrugTracker.slot_id)
                                   .where(PackDetails.id << similar_pack_ids)
                                   .group_by(PackGrid.slot_number, SlotDetails.id, PackDetails.id)
                                   .order_by(PackDetails.id, PackGrid.slot_number)
                                   )

        return similar_pack_data_query
    except Exception as e:
        logger.error("Error in db_fetch_similar_pack_data: {}".format(e))
        raise e


@log_args_and_response
def db_check_packs_are_change_rx_or_not(pack_ids):
    try:
        is_change_rx = None
        patient_id = None
        query = (PackDetails.select(PackHeader.change_rx_flag,
                                    PackHeader.patient_id
                                    )
                 .dicts()
                 .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id)
                 .where(PackDetails.id << pack_ids)
                 .group_by(PackHeader.id)
                 )

        for record in query:
            is_change_rx = record["change_rx_flag"]
            patient_id = record["patient_id"]

        return is_change_rx, patient_id

    except Exception as e:
        logger.error("Error in db_check_packs_are_change_rx_or_not: {}".format(e))
        raise e


@log_args_and_response
def db_get_required_txr_for_packs(pack_ids):
    try:
        pack_id_txr = dict()
        pack_patient_data = dict()
        required_quantity_dict = dict()
        DrugMasterAlias = DrugMaster.alias()

        required_quantity_query = (SlotDetails.select(fn.SUM(SlotDetails.quantity).alias("required_quantity"),
                                                      DrugMaster.txr)
                                   .dicts()
                                   .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                   .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                                   .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                                   .where(PackDetails.id << pack_ids)
                                   .group_by(DrugMaster.txr))

        for record in required_quantity_query:
            required_quantity_dict[record["txr"]] = record["required_quantity"]

        logger.info("In db_get_required_txr_for_packs: required_quantity_dict: {}".format(required_quantity_dict))

        query = (SlotDetails.select(PackDetails.id.alias("pack_id"),
                                    PackDetails.consumption_end_date,
                                    PackDetails.consumption_start_date,
                                    DrugMaster.txr,
                                    # fn.SUM(SlotDetails.quantity).alias("required_quantity"),
                                    DrugMasterAlias.txr.alias("filled_txr"),
                                    fn.SUM(DrugTracker.drug_quantity).alias("filled_quantity")
                                    )
                 .dicts()
                 .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                 .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                 .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                 .join(DrugTracker, JOIN_LEFT_OUTER, on=SlotDetails.id == DrugTracker.slot_id)
                 .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=DrugMasterAlias.id == DrugTracker.drug_id)
                 .where(PackDetails.id << pack_ids)
                 .group_by(DrugMaster.txr, PackDetails.id)
                 )

        logger.info("In db_get_required_txr_for_packs: query: {}".format(query))

        for record in query:
            if record["pack_id"] not in pack_id_txr:
                pack_id_txr[record["pack_id"]] = dict()
                pack_id_txr[record["pack_id"]]["remaining_required_txr"] = list()
                pack_id_txr[record["pack_id"]]["consumption_start_date"] = record["consumption_start_date"]
                pack_id_txr[record["pack_id"]]["consumption_end_date"] = record["consumption_end_date"]

            if record["filled_quantity"] is None:
                record["filled_quantity"] = 0

            if required_quantity_dict[record["txr"]] > record["filled_quantity"]:
                pack_id_txr[record["pack_id"]]["remaining_required_txr"].append(record["txr"])

        logger.info("In db_get_required_txr_for_packs: pack_id_txr: {}".format(pack_id_txr))

        daw_code_brand_flag_query = (SlotDetails.select(PackDetails.id.alias("pack_id"),
                                                        PatientRx.patient_id,
                                                        DrugMaster.formatted_ndc,
                                                        DrugMaster.txr,
                                                        DrugMaster.brand_flag,
                                                        PatientRx.daw_code
                                                        )
                                     .dicts()
                                     .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                                     .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                                     .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                                     .where(PackDetails.id << pack_ids)
                                     .group_by(PackDetails.id, SlotDetails.drug_id)
                                     )

        logger.info("In db_get_required_txr_for_packs: daw_code_brand_flag_query: {}".format(daw_code_brand_flag_query))

        for record in daw_code_brand_flag_query:
            if record["pack_id"] not in pack_patient_data:
                pack_patient_data[record["pack_id"]] = dict()
                # pack_patient_data[record["pack_id"]]["daw_code"] = record["daw_code"]
                pack_patient_data[record["pack_id"]]["patient_id"] = record["patient_id"]
                pack_patient_data[record["pack_id"]]["consumption_start_date"] = (
                    pack_id_txr)[record["pack_id"]]["consumption_start_date"]
                pack_patient_data[record["pack_id"]]["consumption_end_date"] = (
                    pack_id_txr)[record["pack_id"]]["consumption_end_date"]
                pack_patient_data[record["pack_id"]]["remaining_required_txr_count"] = 0

            if (record["txr"] in pack_id_txr[record["pack_id"]]["remaining_required_txr"]
                    and record["txr"] not in pack_patient_data[record["pack_id"]]):
                pack_patient_data[record["pack_id"]][record["txr"]] = dict()
                pack_patient_data[record["pack_id"]]["remaining_required_txr_count"] += 1
                pack_patient_data[record["pack_id"]][record["txr"]][record["formatted_ndc"]] = dict()
                pack_patient_data[record["pack_id"]][record["txr"]][record["formatted_ndc"]]["brand_flag"] = record[
                    "brand_flag"]
                pack_patient_data[record["pack_id"]][record["txr"]][record["formatted_ndc"]]["daw_code"] = record[
                    "daw_code"]

        return pack_patient_data

    except Exception as e:
        logger.error("Error in db_get_current_pack_drug_tracker_data: {}".format(e))
        raise e


@log_args_and_response
def db_fetch_reusable_packs(pack_ids, patient_id, company_id, is_change_rx):
    try:
        asrs_dict = dict()
        pack_display_ids = list()
        reusable_packs_dict = dict()
        deleted_pack_id_list = list()
        pack_wise_found_pack_txr_dict = dict()

        reusable_packs_query = (ReusePackDrug.select(ExtPackDetails.ext_pack_display_id,
                                                     ReusePackDrug.pack_id,
                                                     ReusePackDrug.expiry_date,
                                                     ReusePackDrug.available_quantity,
                                                     DrugMaster.formatted_ndc,
                                                     DrugMaster.txr,
                                                     DrugMaster.brand_flag,
                                                     PackHeader.patient_id,
                                                     fn.IF(
                                                         ExtPackDetails.pharmacy_pack_status_id.is_null(True),
                                                         None,
                                                         CodeMaster.value
                                                     ).alias("pharmacy_pack_status"),
                                                     ExtPackDetails.pharmacy_pack_status_id,
                                                     ExtPackDetails.packs_delivery_status
                                                     )
                                .dicts()
                                .join(PackDetails, on=PackDetails.id == ReusePackDrug.pack_id)
                                .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id)
                                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id)
                                .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                                .join(CodeMaster, JOIN_LEFT_OUTER,
                                      on=CodeMaster.id == ExtPackDetails.pharmacy_pack_status_id)
                                .join(TemplateMaster,
                                      on=((PackHeader.patient_id == TemplateMaster.patient_id) &
                                          (PackHeader.file_id == TemplateMaster.file_id)
                                          )
                                      )
                                .where(ExtPackDetails.pack_usage_status_id << [constants.EXT_PACK_USAGE_STATUS_PENDING_ID, constants.EXT_PACK_USAGE_STATUS_PACK_RESEALED_ID],
                                       ExtPackDetails.status_id << settings.PACK_PROGRESS_DONE_STATUS_LIST
                                       ))

        # if is_change_rx:
        #     reusable_packs_query = reusable_packs_query.where(PackHeader.patient_id == patient_id)

        pack_patient_data = db_get_required_txr_for_packs(pack_ids)
        max_pack_consumption_end_date = (PackDetails.select(fn.MAX(PackDetails.consumption_end_date))
                                         .where(PackDetails.id << pack_ids).scalar())
        # max_pack_consumption_end_date = datetime.datetime.strptime(max_pack_consumption_end_date, "%Y-%m-%d").date()

        for pack in pack_ids:
            temp_reusable_packs_query = reusable_packs_query.clone()
            # if is_change_rx:
            #     temp_reusable_packs_query = temp_reusable_packs_query.where(
            #         TemplateMaster.fill_start_date <= pack_patient_data[pack]["consumption_start_date"],
            #         TemplateMaster.fill_end_date >= pack_patient_data[pack]["consumption_end_date"]
            #     )

            logger.info("In db_fetch_reusable_packs: temp_reusable_packs_query: {}".format(temp_reusable_packs_query))
            discarded_pack_list = list()
            for record in temp_reusable_packs_query:
                if record["ext_pack_display_id"] in discarded_pack_list:
                    continue

                if pack not in reusable_packs_dict:
                    reusable_packs_dict[pack] = dict()
                    pack_wise_found_pack_txr_dict[pack] = dict()

                if record["ext_pack_display_id"] not in reusable_packs_dict[pack]:
                    reusable_packs_dict[pack][record["ext_pack_display_id"]] = dict()
                    reusable_packs_dict[pack][record["ext_pack_display_id"]]["count"] = 0
                    reusable_packs_dict[pack][record["ext_pack_display_id"]]["pharmacy_pack_status"] = (
                        record)["pharmacy_pack_status"]
                    reusable_packs_dict[pack][record["ext_pack_display_id"]]["same_patient"] = False

                if record["ext_pack_display_id"] not in pack_wise_found_pack_txr_dict[pack]:
                    pack_wise_found_pack_txr_dict[pack][record["ext_pack_display_id"]] = set()

                if pack in pack_patient_data:
                    if (record["txr"] in pack_patient_data[pack] and record["txr"]
                            not in pack_wise_found_pack_txr_dict[pack][record["ext_pack_display_id"]]):
                        expiry = datetime.datetime.strptime(record["expiry_date"], "%m-%Y").date()
                        expiry = last_day_of_month(expiry)
                        if expiry > max_pack_consumption_end_date + datetime.timedelta(
                                settings.EXPIRED_DRUG_DAYS):
                            if (record["patient_id"] == pack_patient_data[pack]["patient_id"]
                                    and record["available_quantity"] > 0):
                                reusable_packs_dict[pack][record["ext_pack_display_id"]]["count"] += 1
                                reusable_packs_dict[pack][record["ext_pack_display_id"]]["same_patient"] = True
                                pack_wise_found_pack_txr_dict[pack][record["ext_pack_display_id"]].add(record["txr"])
                            else:
                                if record["packs_delivery_status"] == constants.PACK_DELIVERY_STATUS_INSIDE_PHARMACY_ID:
                                    if (record["formatted_ndc"] in pack_patient_data[pack][record["txr"]]
                                            and record["available_quantity"] > 0):
                                        reusable_packs_dict[pack][record["ext_pack_display_id"]]["count"] += 1
                                        pack_wise_found_pack_txr_dict[pack][record["ext_pack_display_id"]].add(
                                            record["txr"])

                                    elif record["brand_flag"] == settings.GENERIC_FLAG:
                                        for fndc in pack_patient_data[pack][record["txr"]].keys():
                                            if pack_patient_data[pack][record["txr"]][fndc]["daw_code"] == 0:
                                                if (pack_patient_data[pack][record["txr"]][fndc]["brand_flag"] == settings.GENERIC_FLAG
                                                        and record["available_quantity"] > 0):
                                                    reusable_packs_dict[pack][record["ext_pack_display_id"]]["count"] += 1
                                                    pack_wise_found_pack_txr_dict[pack][
                                                        record["ext_pack_display_id"]].add(record["txr"])
                                                    break
                                else:
                                    reusable_packs_dict[pack].pop(record["ext_pack_display_id"])
                                    discarded_pack_list.append(record["ext_pack_display_id"])
                        else:
                            if settings.DISCARDED_REUSE_PACK:
                                reusable_packs_dict[pack].pop(record["ext_pack_display_id"])
                                discarded_pack_list.append(record["ext_pack_display_id"])

        logger.info("In db_fetch_reusable_packs: reusable_packs_dict: {}".format(reusable_packs_dict))

        if reusable_packs_dict:
            for pack, recommend_packs in reusable_packs_dict.items():
                deleted_pack_id_list = list()
                found_reusable_packs = 0
                recommend_packs = dict(sorted(recommend_packs.items(), key=lambda x: x[1]['count'], reverse=True))
                for recommend_pack, recommend_pack_data in recommend_packs.items():
                    if recommend_pack_data["count"] > 0 and found_reusable_packs != settings.MAX_REUSABLE_PACKS:
                        found_reusable_packs += 1
                        pass
                        # if ((recommend_pack_data["count"] * 100) / pack_patient_data[pack]["remaining_required_txr_count"]) < 50.00:
                        #    deleted_pack_id_list.append(recommend_pack)
                        #
                        # if recommend_pack not in deleted_pack_id_list:
                        #     pack_display_ids.append(recommend_pack)
                    else:
                        deleted_pack_id_list.append(recommend_pack)

                for deleted_pack in deleted_pack_id_list:
                    recommend_packs.pop(deleted_pack)

                reusable_packs_dict[pack] = recommend_packs

        if pack_display_ids:
            asrs_dict = db_get_storage_by_pack_display_id(pack_display_ids=pack_display_ids, company_id=company_id)

        return reusable_packs_dict, asrs_dict

    except Exception as e:
        logger.error("Error in db_fetch_reusable_packs: {}".format(e))
        raise e


@log_args_and_response
def db_discard_pack_in_ext_pack_details_and_reuse_pack_drug(pack_id):
    try:
        update_status = (
            ExtPackDetails.db_update_ext_pack_details_by_pack_id([pack_id],
                                                                {
                                                                    "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_PACK_DISCARDED_ID,
                                                                    "ext_modified_date": get_current_date_time()}))

        logger.info("In db_discard_pack_in_ext_pack_details_and_reuse_pack_drug: update_status: {}"
                    .format(update_status))

        update_drug_status = (
            ReusePackDrug.db_update_drugs_status_by_pack_id([pack_id],
                                                            constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_ID)
        )

        logger.info("In db_discard_pack_in_ext_pack_details_and_reuse_pack_drug: update_drug_status: {}"
                    .format(update_drug_status))

        return update_status
    except Exception as e:
        logger.error("Error in db_discard_pack_in_ext_pack_details_and_reuse_pack_drug: {}".format(e))
        raise e


@log_args_and_response
def db_discard_reuse_drug_in_reuse_pack_drug(pack_id, drug_id):
    try:
        update_drug_status = (
            ReusePackDrug.db_update_status_by_pack_id_drug_ids(pack_id, [drug_id],
                                                               constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_ID))
        logger.info("In db_discard_reuse_drug_in_reuse_pack_drug: update_drug_status: {}".format(update_drug_status))

        update_pack_status = True
        query = ReusePackDrug.db_get_reuse_pack_drug_data_by_pack_id([pack_id])
        for record in query:
            if record["status_id"] not in [constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_ID,
                                           constants.REUSE_DRUG_STATUS_DRUG_REUSE_DONE_ID]:
                update_pack_status = False
                break

        if update_pack_status:
            update_pack_status = (
                ExtPackDetails.db_update_ext_pack_details_by_pack_id([pack_id],
                                                                     {"pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_PACK_DISCARDED_ID,
                                                                      "ext_modified_date": get_current_date_time()}))
            logger.info(
                "In db_discard_reuse_drug_in_reuse_pack_drug: update_pack_status: {}".format(update_pack_status))

        return update_drug_status
    except Exception as e:
        logger.error("Error in db_discard_reuse_drug_in_reuse_pack_drug: {}".format(e))
        raise e


@log_args_and_response
def db_update_reuse_pack_drug_by_pack_id_drug_id_dao(pack_id, drug_id, update_dict):
    try:
        return ReusePackDrug.db_update_reuse_pack_drug_by_pack_id_drug_id(pack_id, drug_id, update_dict)
    except Exception as e:
        logger.error("Error in db_update_reuse_pack_drug_by_pack_id_drug_id_dao: {}".format(e))
        raise e


@log_args_and_response
def db_get_reuse_pack_drug_data_by_pack_id_dao(pack_ids):
    try:
        return ReusePackDrug.db_get_reuse_pack_drug_data_by_pack_id(pack_ids)
    except Exception as e:
        logger.error("Error in db_get_reuse_pack_drug_data_by_pack_id_dao: {}".format(e))
        raise e


@log_args_and_response
def db_update_drugs_status_by_pack_id_dao(pack_ids, status_id):
    try:
        return ReusePackDrug.db_update_drugs_status_by_pack_id(pack_ids, status_id)
    except Exception as e:
        logger.error("Error in db_update_drugs_status_by_pack_id_dao: {}".format(e))
        raise e


@log_args_and_response
def db_get_drug_master_data_by_drug_id_dao(drug_id):
    try:
        return DrugMaster.db_get_drug_master_data_by_drug_id(drug_id)
    except Exception as e:
        logger.error("Error in db_get_drug_master_data_by_drug_id_dao: {}".format(e))
        raise e


@log_args_and_response
def get_reuse_in_progress_pack_dao(pack_ids):
    try:
        query = (DrugTracker.select(DrugTracker.reuse_pack,
                                    PackDetails.pack_display_id,
                                    ExtPackDetails.packs_delivery_status
                                    )
                 .dicts()
                 .join(PackDetails, on=PackDetails.id == DrugTracker.reuse_pack)
                 .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id)
                 .where(DrugTracker.pack_id << pack_ids,
                        ExtPackDetails.pack_usage_status_id == constants.EXT_PACK_USAGE_STATUS_PROGRESS_ID
                        )
                 .group_by(PackDetails.id)
                 )

        return query
    except Exception as e:
        logger.error("Error in get_reuse_in_progress_pack_from_drug_tracker: {}".format(e))
        raise e


@log_args_and_response
def get_reuse_pack_drug_data_dao(pack_ids):
    try:
        select_fields = [ReusePackDrug.drug_id,
                         ReusePackDrug.lot_number,
                         ReusePackDrug.item_id,
                         PackDetails.id.alias("pack_id"),
                         ReusePackDrug.expiry_date,
                         ReusePackDrug.total_quantity,
                         ReusePackDrug.available_quantity,
                         PackDetails.pack_display_id,
                         DrugMaster.ndc,
                         DrugMaster.color,
                         DrugMaster.shape,
                         DrugMaster.strength,
                         DrugMaster.drug_name,
                         DrugMaster.imprint,
                         DrugMaster.strength_value,
                         DrugMaster.image_name,
                         DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr"),
                         DrugMaster.manufacturer,
                         DrugDetails.last_seen_by
                         ]

        query = (ReusePackDrug.select(*select_fields)
                 .dicts()
                 .join(PackDetails, on=PackDetails.id == ReusePackDrug.pack_id)
                 .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                 .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                       fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                      (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc))
                 .join(DrugDetails, on=UniqueDrug.id == DrugDetails.unique_drug_id)
                 .where(PackDetails.id << pack_ids,
                        ReusePackDrug.status_id.not_in([constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_ID])
                        )
                 .group_by(DrugMaster.concated_fndc_txr_field(sep="##"), PackDetails.id)
                 )

        return query
    except Exception as e:
        logger.error("Error in get_reuse_pack_drug_data_dao: {}".format(e))
        raise e


@log_args_and_response
def db_get_pack_details_by_display_ids_dao(reuse_pack_ids):
    try:
        return PackDetails.db_get_pack_details_by_display_ids(reuse_pack_ids)
    except Exception as e:
        logger.error("Error in db_get_pack_details_by_display_ids_dao: {}".format(e))
        raise e


@log_args_and_response
def db_get_pack_drug_adjusted_quantity(pack_id, drug_id):
    try:
        query = (DrugTracker.select(fn.SUM(DrugTracker.drug_quantity).alias("drug_quantity"),
                                    fn.SUM(MfdAnalysisDetails.quantity).alias("mfd_quantity"),
                                    fn.GROUP_CONCAT(
                                        fn.DISTINCT(
                                            MfdAnalysisDetails.status_id
                                        )
                                    ).alias("mfd_status")
                                    )
                 .dicts()
                 .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id)
                 .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=((DrugTracker.slot_id == MfdAnalysisDetails.slot_id) &
                                                                (MfdAnalysisDetails.status_id << [constants.MFD_DRUG_MVS_FILLED, constants.MFD_DRUG_DROPPED_STATUS])
                                                                )
                       )
                 .where(DrugTracker.pack_id == pack_id,
                        DrugMaster.concated_fndc_txr_field(sep="##") == drug_id
                        )
                 .group_by(DrugMaster.concated_fndc_txr_field(sep="##"), DrugTracker.slot_id)
                 )

        return query
    except Exception as e:
        logger.error("Error in db_get_pack_drug_adjusted_quantity: {}".format(e))
        raise e


@log_args_and_response
def generate_vial_label(vial_data, filename):
    try:
        c = canvas.Canvas(filename, pagesize=(4.3 * inch, 2.36 * inch))
        pharmacy_data = next(db_get_pharmacy_master_data_dao())
        for vial_details in vial_data:

            # Add a margin around the border of the label
            border_margin = 0.1 * inch
            c.rect(border_margin, border_margin, 4.1 * inch, 2.16 * inch)

            # Draw horizontal lines to separate partitions
            line_height = 1.55 * inch  # Adjust this value to position the lines as needed
            c.line(border_margin, line_height, 4.3 * inch - border_margin, line_height)  # First line
            c.line(border_margin, line_height - 0.60 * inch, 4.3 * inch - border_margin,
                   line_height - 0.60 * inch)  # Second line

            # Set font and decrease the font size
            font_size = 9
            c.setFont("Helvetica", font_size)

            # Partition 1
            c.drawString(border_margin + 0.1 * inch, 2.05 * inch, f"Vial ID: {vial_details['vial_id']}")
            c.setFont("Helvetica-Bold", font_size + 2)
            c.drawString(border_margin + 0.1 * inch, 1.85 * inch, vial_details['drug_name'])
            c.setFont("Helvetica", font_size)
            c.drawString(border_margin + 0.1 * inch, 1.67 * inch,
                         f"Quantity: {vial_details['quantity']} | Drug Expiry: {vial_details['expiry_date']}")

            # Partition 2
            font_size = 8
            c.setFont("Helvetica", font_size)
            text = f"{vial_details['color']} | {vial_details['imprint']} | NDC: {vial_details['ndc']} | Pack ID: {vial_details['pack_display_id']}"
            text_width = c.stringWidth(text, "Helvetica", font_size)
            center_x = (4.3 * inch - text_width) / 2.5 + border_margin
            c.drawString(center_x, 1.32 * inch, text)

            text = f"Manufacturer: {vial_details['manufacturer']} | Lot Number: {vial_details['lot_number']}"
            text_width = c.stringWidth(text, "Helvetica", font_size)
            center_x = (4.0 * inch - text_width) / 2 + border_margin
            c.drawString(center_x, 1.10 * inch, text)

            font_size = 9
            c.setFont("Helvetica", font_size)
            # Partition 3 - DosePacker Logo and Vibrant Care Pharmacy Inc
            logo_path = "src/dosepack_logo.png"  # Replace with the path to your logo
            c.drawImage(logo_path, border_margin + 0.045 * inch, 0.59 * inch, width=1.0 * inch, height=0.2 * inch)
            text = pharmacy_data["store_name"]
            c.stringWidth(text, "Helvetica-Bold", font_size - 2)
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(border_margin + 0.1 * inch, 0.45 * inch, text)
            c.setFont("Helvetica", font_size - 2)
            text = pharmacy_data["store_address"] + " |"
            c.drawString(border_margin + 0.1 * inch, 0.32 * inch, text)
            text = pharmacy_data["store_phone"] + " | " + pharmacy_data["store_fax"]
            c.drawString(border_margin + 0.1 * inch, 0.20 * inch, text)

            qr_data = vial_details["item_id"]
            qr = QrCodeWidget(qr_data)
            b = qr.getBounds()
            w = b[2] - b[0]
            h = b[3] - b[1]

            d = Drawing(55, 55, transform=[55. / w, 0, 0, 55. / h, 0, 0])
            d.add(qr)
            d.hAlign = 'RIGHT'

            renderPDF.draw(d, c, ((4.3 * inch) - 10) / 1.23, y=11)
            c.showPage()

        c.save()

    except Exception as e:
        logger.error("Error in generate_vial_label: {}".format(e))
        raise e


@log_args_and_response
def db_get_updated_quantity_data_for_label(pack_ids):
    try:
        response = dict()
        query = (ReusePackDrug.select(DrugMaster.formatted_ndc,
                                      ReusePackDrug.available_quantity
                                      )
                 .dicts()
                 .join(DrugMaster, on=DrugMaster.id == ReusePackDrug.drug_id)
                 .where(ReusePackDrug.pack_id << pack_ids,
                        ReusePackDrug.status_id == constants.REUSE_DRUG_STATUS_DRUG_RESEALED_ID)
                 )

        for record in query:
            response[record["formatted_ndc"]] = record["available_quantity"]

        return response

    except Exception as e:
        logger.error("Error in db_get_updated_quantity_data_for_label: {}".format(e))
        raise e


@log_args_and_response
def get_ndc_list_for_vial_list_for_filling_screen(ndc_data):
    try:
        final_ndc_dict = dict()
        final_ndc_list = list()
        DrugMasterAlias = DrugMaster.alias()

        for patient, ndc_list in ndc_data.items():
            for ndc in ndc_list:
                query = (SlotDetails.select(PatientRx.patient_id,
                                            PatientRx.daw_code,
                                            DrugMaster.ndc.alias("original_ndc"),
                                            DrugMasterAlias.ndc.alias("other_ndc"),
                                            DrugMaster.formatted_ndc.alias("original_formatted_ndc"),
                                            DrugMasterAlias.formatted_ndc.alias("other_formatted_ndc"),
                                            DrugMaster.txr,
                                            DrugMaster.brand_flag,
                                            DrugMaster.brand_flag.alias("other_brand_flag")
                                            )
                         .dicts()
                         .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                         .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                         .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)
                         .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id)
                         .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                         .join(DrugMasterAlias, on=DrugMaster.txr == DrugMasterAlias.txr)
                         .where(DrugMaster.ndc == ndc,
                                DrugMasterAlias.ndc != ndc,
                                PatientMaster.id == patient
                                )
                         .group_by(DrugMasterAlias.id)
                         )

                if ndc not in final_ndc_list:
                    final_ndc_list.append(int(ndc))
                    final_ndc_dict[int(ndc)] = int(ndc)

                for record in query:
                    if record["daw_code"] == 0:
                        if (record["brand_flag"] == settings.GENERIC_FLAG
                                and record["other_brand_flag"] == settings.GENERIC_FLAG):
                            final_ndc_list.append(int(record["other_ndc"]))
                            final_ndc_dict[int(record["other_ndc"])] = int(record["original_ndc"])

                    if record["daw_code"] == 1:
                        if record["original_formatted_ndc"] == record["other_formatted_ndc"]:
                            final_ndc_list.append(int(record["other_ndc"]))
                            final_ndc_dict[int(record["other_ndc"])] = int(record["original_ndc"])

        return final_ndc_dict, final_ndc_list

    except Exception as e:
        logger.error("Error in get_ndc_list_for_vial_list: {}".format(e))
        raise e


@log_args_and_response
def get_ndc_list_for_vial_list_for_prn_screen(ndc_data):
    try:
        final_ndc_dict = dict()
        final_ndc_list = list()
        DrugMasterAlias = DrugMaster.alias()

        for patient, ndc_dict in ndc_data.items():
            for ndc, daw_code in ndc_dict.items():
                query = (DrugMaster.select(DrugMaster.ndc.alias("original_ndc"),
                                           DrugMasterAlias.ndc.alias("other_ndc"),
                                           DrugMaster.formatted_ndc.alias("original_formatted_ndc"),
                                           DrugMasterAlias.formatted_ndc.alias("other_formatted_ndc"),
                                           DrugMaster.brand_flag,
                                           DrugMaster.brand_flag.alias("other_brand_flag")
                                           )
                         .dicts()
                         .join(DrugMasterAlias, on=DrugMaster.txr == DrugMasterAlias.txr)
                         .where(DrugMaster.ndc == ndc,
                                DrugMasterAlias.ndc != ndc
                                )
                         .group_by(DrugMasterAlias.id)
                         )

                if ndc not in final_ndc_list:
                    final_ndc_list.append(int(ndc))
                    final_ndc_dict[int(ndc)] = int(ndc)

                for record in query:
                    if record["original_formatted_ndc"] == record["other_formatted_ndc"]:
                        final_ndc_list.append(int(record["other_ndc"]))
                        final_ndc_dict[int(record["other_ndc"])] = int(record["original_ndc"])

        return final_ndc_dict, final_ndc_list

    except Exception as e:
        logger.error("Error in get_ndc_list_for_vial_list: {}".format(e))
        raise e


@log_args_and_response
def sync_delivery_dates_with_ips(pack_header_id=None, delivery_date=None, ips_user_name=None, pack_display_ids=None,
                                 company_id=None, queue_id=0, bill_id=0):
    try:
        store_type = 0
        token = get_token()
        if not token:
            logger.debug("sync_delivery_dates_with_ips: token not found")
            return error(5018)
        company_id = company_id
        if not ips_user_name:
            user_details = get_current_user(token=token)
            ips_user_name = user_details["ips_user_name"]
            company_id = user_details["company_id"]
        ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
        if pack_display_ids:
            store_type = PackDetails.select(PackDetails.store_type).where(
                PackDetails.pack_display_id == pack_display_ids[0]).scalar()
        if not pack_display_ids:
            pack_display_ids = PackDetails.select(PackDetails.pack_display_id).dicts().where(
                PackDetails.pack_header_id == pack_header_id)
        parameters = []
        for pack in pack_display_ids:
            parameters.append({
                "pack_id": pack["pack_display_id"],
                "rx_id": None,
                "delivery_datetime": str(delivery_date),
                "username": ips_user_name,
                "store_type": store_type,
                "bill_id": bill_id,
                "queue_id": queue_id
            })
        logger.info(f"In sync_delivery_dates_with_ips, parameters are {parameters}")
        send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1], webservice_url=settings.IPS_SYNC_DELIVERY_SCHEDULE,
                  parameters=parameters, counter=0, request_type="POST", token=token, ips_api=True)
        # store type 0 suggests LTC pack and 1 suggests Retail pack
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        pass


@log_args_and_response
def db_update_delivery_date_of_pack(pack_ids, user_id, delivery_date):
    try:
        current_time = get_current_date_time()
        pack_header_ids = PackHeader.select(fn.GROUP_CONCAT(PackHeader.id)).dicts() \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(PackDetails.id.in_(pack_ids)).scalar().split(',')
        for pack_header in pack_header_ids:
            status = PackHeader.update(scheduled_delivery_date=delivery_date, delivery_datetime=delivery_date,
                                       modified_date=current_time, modified_by=user_id).where(PackHeader.id == pack_header).execute()
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        pass


@log_args_and_response
def db_update_delivery_date_and_delivery_status(pack_display_id, delivery_status, delivery_date, user_id):
    try:
        current_date_time = get_current_date_time()
        pack_header_id = PackDetails.select(PackDetails.pack_header_id).where(
            PackDetails.pack_display_id == pack_display_id).scalar()
        update = PackHeader.update(scheduled_delivery_date=delivery_date, delivery_datetime=delivery_date,
                                   modified_date=current_date_time, modified_by=user_id).where(
            PackHeader.id == pack_header_id).execute()
        if delivery_status == 5:
            status = PackDetails.update(delivery_status=None, modified_date=current_date_time,
                                        modified_by=user_id, delivered_date=current_date_time).where(
                PackDetails.pack_display_id == pack_display_id).execute()
            return True
        delivery_status = constants.DELIVERY_STATUS_MAP[delivery_status]
        if delivery_status == constants.DELIVERY_STATUS_DELIVERED:
            status = PackDetails.update(delivery_status=delivery_status, modified_date=current_date_time,
                                        modified_by=user_id, delivered_date=current_date_time).where(
                PackDetails.pack_display_id == pack_display_id).execute()
            return True
        status = PackDetails.update(delivery_status=delivery_status, modified_date=current_date_time,
                                    modified_by=user_id).where(PackDetails.pack_display_id == pack_display_id).execute()
        return True
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        pass


@log_args_and_response
def db_fetch_store_type_of_pack(pack_id):
    try:
        store_type = PackDetails.select(PackDetails.store_type).where(PackDetails.id == pack_id).scalar()
        # sending store type 1 for retail and 0 for LTC or On Demand
        if store_type == constants.STORE_TYPE_RETAIL:
            return 1
        else:
            return 0
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        pass



@log_args_and_response
def db_master_search_dao(company_id, filters, sort_fields, paginate):
    """
    function to get global search for patient his doctor and associated facility.
    """
    clauses: list = list()
    order_list = list()

    if sort_fields:
        order_list = sort_fields

    like_search_fields = ['patient_name', 'facility_name', 'doctor_name', 'doctor_phone', "patient_phone"]
    global_search = [PatientMaster.concated_patient_name_field(),
                     FacilityMaster.facility_name,
                     PatientRx.pharmacy_rx_no,
                     PatientMaster.workphone,
                     DoctorMaster.workphone,
                     DoctorMaster.concated_doctor_name_field()]

    if filters and filters.get('global_search', None) is not None:
        multi_search_string = filters['global_search'].split(',')
        clauses = get_multi_search(clauses, multi_search_string, global_search)

    fields_dict = {"patient_name": fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name),
                   "facility_name": FacilityMaster.facility_name,
                   "patient_id": PatientMaster.pharmacy_patient_id,
                   "facility_id": FacilityMaster.pharmacy_facility_id,
                   "doctor_name": DoctorMaster.concated_doctor_name_field(),
                   "doctor_workphone": DoctorMaster.workphone,
                   "patient_workphone": PatientMaster.workphone
                   }

    try:
        clauses.append(FacilityMaster.company_id == company_id)

        query = PatientMaster.select(FacilityMaster.id.alias("facility_id"),
                                     fields_dict["facility_name"],
                                     FacilityMaster.pharmacy_facility_id,
                                     PatientMaster.pharmacy_patient_id,
                                     DoctorMaster.pharmacy_doctor_id,
                                     fields_dict["patient_name"].alias("patient_name"),
                                     PatientMaster.id.alias("patient_id"),
                                     fields_dict["patient_workphone"].alias("patient_phone"),
                                     PatientMaster.dob.alias("dob"),
                                     fields_dict["doctor_name"].alias("doctor_name"),
                                     fields_dict["doctor_workphone"].alias("doctor_phone")
                                     ).dicts() \
            .join(PatientRx, on=(PatientMaster.id == PatientRx.patient_id)) \
            .join(FacilityMaster, on=(FacilityMaster.id == PatientMaster.facility_id)) \
            .join(DoctorMaster, on=(DoctorMaster.id == PatientRx.doctor_id)) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(PatientMaster.workphone) \
            .order_by(PatientMaster.id.desc())

        logger.info(query)

        results, count = get_results(query, fields_dict,
                                     filter_fields=filters,
                                     like_search_list=like_search_fields)

        for order in order_list:
            order[1] = -1 if order[1] == 1 else 1
        final_results = get_ordered_list(results, order_list)

        if final_results is not None:
            paginated_results = dpws_paginate(final_results, paginate) if paginate else final_results

            patient_data = {}

            for patient in paginated_results:
                patient_data[patient["patient_phone"]] = {
                    "patient_name": patient["patient_name"],
                    "patient_id": patient["patient_id"],
                    "patient_dob": patient["dob"],
                    "facility_name": patient["facility_name"],
                    "facility_id": patient["facility_id"],
                    "doctor_name": patient["doctor_name"],
                    "doctor_phone_no": patient["doctor_phone"]
                }

            return patient_data, count

        logger.debug("sorted_fields returning null in db_master_search_dao")
        return None, None

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_master_search_dao {}".format(e))
        return None, None
    except Exception as e:
        logger.error("Unexpected error occurred in db_master_search_dao {}".format(e))
        return None, None


@log_args_and_response
def db_person_master_search_dao(company_id, filters, sort_fields, paginate):
    """
    function to get global search
    """
    patient_clauses: list = list()
    facility_clauses: list = list()
    doctor_clauses: list = list()
    order_list = list()
    results = []

    if sort_fields:
        order_list = sort_fields

    like_search_fields = ['patient_name', 'facility_name', 'doctor_name', 'doctor_phone', "patient_phone"]

    doctor_search = [DoctorMaster.workphone, DoctorMaster.concated_doctor_name_field()]

    patient_search = [PatientMaster.concated_patient_name_field(), PatientMaster.workphone]

    facility_search = [FacilityMaster.facility_name, FacilityMaster.workphone]

    if filters and filters.get('global_search', None) is not None:
        multi_search_string = filters['global_search'].split(',')
        doctor_clauses = get_multi_search(doctor_clauses, multi_search_string, doctor_search)
        patient_clauses = get_multi_search(patient_clauses, multi_search_string, patient_search)
        facility_clauses = get_multi_search(facility_clauses, multi_search_string, facility_search)

    fields_dict = {"patient_name": fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name),
                   # "facility_name": FacilityMaster.facility_name,
                   "doctor_name": DoctorMaster.concated_doctor_name_field(),
                   "doctor_workphone": DoctorMaster.workphone,
                   "patient_workphone": PatientMaster.workphone,
                   # "facility_workphone": FacilityMaster.workphone
                   }
    try:
        patient_clauses.append(PatientMaster.company_id == company_id)
        facility_clauses.append(FacilityMaster.company_id == company_id)
        doctor_clauses.append(DoctorMaster.company_id == company_id)

        patient_data, patient_count = search_patient(patient_clauses, fields_dict, like_search_fields, filters)
        # facility_data, facility_count = search_facility(facility_clauses, fields_dict, like_search_fields, filters)
        doctor_data, doctor_count = search_doctor(doctor_clauses, fields_dict, like_search_fields, filters)

        if patient_data:
            results.extend(patient_data)
        # if facility_data:
        #     results.extend(facility_data)
        if doctor_data:
            results.extend(doctor_data)

        final_count = patient_count + doctor_count  # + facility_count TODO: if facility needs to be searched

        for order in order_list:
            order[1] = -1 if order[1] == 1 else 1
        final_results = get_ordered_list(results, order_list)

        if final_results is not None:
            paginated_results = dpws_paginate(final_results, paginate) if paginate else final_results

            return paginated_results, final_count

        logger.debug("sorted_fields returning null in db_master_search_dao")
        return None, None

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_master_search_dao {}".format(e))
        return None, None
    except Exception as e:
        logger.error("Unexpected error occurred in db_master_search_dao {}".format(e))
        return None, None


def search_facility(facility_clauses, fields_dict, like_search_fields, filters):
    try:
        facility_data = []
        facility_query = FacilityMaster.select(fields_dict["facility_name"].alias("name"),
                                               fn.COALESCE(FacilityMaster.workphone, "00000").alias(
                                                   "workphone")).dicts() \
            .where(functools.reduce(operator.and_, facility_clauses)) \
            .order_by(FacilityMaster.id)

        logger.info(facility_query)

        facility_results, count = get_results(facility_query, fields_dict,
                                              filter_fields=filters,
                                              like_search_list=like_search_fields)
        for facility in facility_results:
            facility_dict = {"name": facility["name"],
                             "type": "Facility",
                             "phone": facility["workphone"],
                             "org": facility["name"]}
            facility_data.append(facility_dict)

        return facility_data, count

    except Exception as e:
        print(e)
        return None, None


def search_doctor(doctor_clauses, fields_dict, like_search_fields, filters):
    try:
        doctor_data = []
        doctor_query = DoctorMaster.select(DoctorMaster.first_name.alias("first_name"),
                                           DoctorMaster.last_name.alias("last_name"),
                                           fn.COALESCE(fields_dict["doctor_workphone"], "00000").alias(
                                               "workphone")).dicts() \
            .where(functools.reduce(operator.and_, doctor_clauses)) \
            .order_by(DoctorMaster.id)

        logger.info(doctor_query)

        doctor_results, count = get_results(doctor_query, fields_dict,
                                            filter_fields=filters,
                                            like_search_list=like_search_fields)

        for doctor in doctor_results:
            doctor_dict = {"first_name": doctor["first_name"],
                           "last_name": doctor["last_name"],
                           "type": "Doctor",
                           "phone_number": doctor["workphone"],
                           "organization": None}
            doctor_data.append(doctor_dict)

        return doctor_data, count
    except Exception as e:
        print(e)
        return None, 0


def search_patient(patient_clauses, fields_dict, like_search_fields, filters):
    try:
        patient_data = []
        patient_query = PatientMaster.select(PatientMaster.first_name.alias("first_name"),
                                             PatientMaster.last_name.alias("last_name"),
                                             fn.COALESCE(PatientMaster.workphone, "00000").alias("workphone"),
                                             FacilityMaster.facility_name.alias("facility_name")).dicts() \
            .join(FacilityMaster, on=(FacilityMaster.id == PatientMaster.facility_id)) \
            .where(functools.reduce(operator.and_, patient_clauses)) \
            .order_by(PatientMaster.id.desc())

        logger.info(patient_query)

        patient_results, count = get_results(patient_query, fields_dict,
                                             filter_fields=filters,
                                             like_search_list=like_search_fields)

        for patient in patient_results:
            patient_dict = {"first_name": patient["first_name"],
                            "last_name": patient["last_name"],
                            "type": "Patient",
                            "phone_number": patient["workphone"],
                            "organization": patient["facility_name"]}
            patient_data.append(patient_dict)

        return patient_data, count

    except Exception as e:
        print(e)
        return None, None
