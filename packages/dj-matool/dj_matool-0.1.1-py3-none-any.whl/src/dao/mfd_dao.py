import collections
import functools
import operator
import os
import sys
from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import Any, Dict, List

import couchdb
from peewee import (InternalError, IntegrityError, JOIN_LEFT_OUTER, fn, DoesNotExist, DataError)
from playhouse.shortcuts import case
from sqlalchemy.sql.elements import Case

import settings
import src
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, log_args, retry
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.api_utility import (get_filters, get_orders, apply_paginate)
from src.dao.batch_dao import db_update_mfd_status, get_progress_batch_id
from src.dao.couch_db_dao import initialize_couch_db_doc, get_document_from_couch_db, get_couch_db_database_name
from src.dao.device_manager_dao import get_robots_by_systems_dao, get_system_id_based_on_device_type
from src.dao.drug_dao import get_fndc_txr_wise_inventory_qty, dpws_paginate
from src.exceptions import (NoLocationExists, RealTimeDBException)
from src.model.model_canister_master import CanisterMaster
from src.model.model_batch_master import BatchMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_drug_dimension import DrugDimension
from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs
from src.model.model_mfd_canister_transfer_history import MfdCanisterTransferHistory
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_status import DrugStatus
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_master import FacilityMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import (MfdAnalysis)
from src.model.model_mfd_analysis_details import (MfdAnalysisDetails)
from src.model.model_mfd_canister_master import (MfdCanisterMaster)
from src.model.model_mfd_cycle_history import MfdCycleHistory
from src.model.model_mfd_history_comment import MfdCycleHistoryComment
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_drug_tracker import DrugTracker
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_template_details import TemplateDetails
from src.model.model_template_master import TemplateMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_zone_master import ZoneMaster
from src.service.misc import update_mfd_module_couch_db
from src.service.notifications import Notifications

logger = settings.logger

mfd_canister_inprogress_condition = [((MfdAnalysis.status_id == constants.MFD_CANISTER_IN_PROGRESS_STATUS) |
                                      ((MfdAnalysis.status_id << [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                  constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                                  constants.MFD_CANISTER_FILLED_STATUS,
                                                                  constants.MFD_CANISTER_VERIFIED_STATUS]) &
                                       (MfdAnalysis.mfs_device_id == LocationMaster.device_id) &
                                       (LocationMaster.location_number == MfdAnalysis.mfs_location_number) &
                                       (MfdAnalysis.mfd_canister_id.is_null(False))))]

mfd_canister_inprogress_condition_for_skip = [((MfdAnalysis.status_id == constants.MFD_CANISTER_IN_PROGRESS_STATUS) |
                                               ((MfdAnalysis.status_id << [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                           constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                                           constants.MFD_CANISTER_VERIFIED_STATUS]) &
                                                (MfdAnalysis.mfs_device_id == LocationMaster.device_id) &
                                                (LocationMaster.location_number == MfdAnalysis.mfs_location_number) &
                                                (MfdAnalysis.mfd_canister_id.is_null(False))))]

mfd_canister_pending_and_inprogress_condition = [((MfdAnalysis.status_id << [constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                                             constants.MFD_CANISTER_PENDING_STATUS]) |
                                                  ((MfdAnalysis.status_id << [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                              constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                                              constants.MFD_CANISTER_FILLED_STATUS,
                                                                              constants.MFD_CANISTER_VERIFIED_STATUS]) &
                                                   (MfdAnalysis.mfs_device_id == LocationMaster.device_id) &
                                                   (LocationMaster.location_number == MfdAnalysis.mfs_location_number) &
                                                   (MfdAnalysis.mfd_canister_id.is_null(False))))]

mfd_latest_analysis_sub_query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias('max_order_number'),
                                                   MfdAnalysis.mfd_canister_id.alias('mfd_canister_id')) \
    .group_by(MfdAnalysis.mfd_canister_id).alias('sub_query')


@log_args_and_response
def db_get_batch_ids(company_id: int, mfs_id: int) -> list:
    """
    Returns batch_ids of the system associated with the manual-filling-device based on the zone.
    @param mfs_id:
    @param company_id: int
    :param mfs_id: int
    :return: list
    """
    batch_ids = set()
    DeviceLayoutDetailsAlias = DeviceLayoutDetails.alias()
    deleted_batch_ids = get_mfd_pending_deleted_batch_ids()

    try:
        query = MfdAnalysis.select(BatchMaster.id.alias('batch_id'),
                                   fn.COUNT(fn.DISTINCT(PackDetails.id)).alias('pack_count')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(DeviceMaster, on=((DeviceMaster.system_id == BatchMaster.system_id) &
                                   (DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']))) \
            .join(DeviceLayoutDetails, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .join(ZoneMaster, on=ZoneMaster.id == DeviceLayoutDetails.zone_id) \
            .join(DeviceLayoutDetailsAlias, on=((ZoneMaster.id == DeviceLayoutDetailsAlias.zone_id) &
                                                (DeviceLayoutDetailsAlias.device_id == mfs_id))) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(PackDetails.company_id == company_id,
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED)
        if deleted_batch_ids:
            query = query.where((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)) |
                                (BatchMaster.id << deleted_batch_ids))
        else:
            query = query.where((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
        query = query.group_by(MfdAnalysis.batch_id)
        for record in query:
            batch_ids.add(record['batch_id'])
        return list(batch_ids)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfd_pending_deleted_batch_ids() -> list:
    """
    Returns batch_ids for whom batch is in deleted state but mfd filling is in progress
    :return: list
    """
    batch_ids = set()
    try:
        query = MfdAnalysis.select(BatchMaster.id.alias('batch_id'),
                                   fn.COUNT(fn.DISTINCT(PackDetails.id)).alias('pack_count')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(TempMfdFilling, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .where(BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   BatchMaster.status.in_(settings.BATCH_PROCESSING_DONE_LIST)) \
            .group_by(MfdAnalysis.batch_id)
        for record in query:
            batch_ids.add(record['batch_id'])
        return list(batch_ids)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_get_min_batch(user_id: int, company_id: int, mfs_id: int):
    """
    returns minimum batch assigned to a particular user
    @param user_id: int
    @param company_id: int
    :return: int
    @param mfs_id:
    """
    try:

        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()

        query = MfdAnalysis.select(BatchMaster.id.alias('batch_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(PackDetails, on=PackDetails.batch_id == BatchMaster.id) \
            .join(CodeMaster, on=CodeMaster.id == BatchMaster.mfd_status) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=((MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) &
                                                          (MfdCanisterMaster.location_id !=
                                                           MfdAnalysis.trolley_location_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .where(PackDetails.company_id == company_id,
                   BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   MfdAnalysis.assigned_to == user_id,
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   MfdAnalysis.mfs_device_id == mfs_id,
                   mfd_canister_pending_and_inprogress_condition
                   ) \
            .order_by(MfdAnalysis.batch_id) \
            .group_by(MfdAnalysis.batch_id) \
            .get()
        return query['batch_id']
    except DoesNotExist as e:
        logger.info(e, exc_info=True)
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def check_user_in_progress_batch(progress_batch):
    try:
        pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(progress_batch)
        if not pending_trolley_sequence:
            return False

        queue = MfdAnalysis.select(fn.COUNT(MfdAnalysis.id).alias("count")).where(
            MfdAnalysis.batch_id == progress_batch,
            MfdAnalysis.trolley_seq << pending_trolley_sequence,
            MfdAnalysis.assigned_to.is_null(True)).dicts()

        for res in queue:
            if res["count"] > 0:
                return True
        return False
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_batch_info(batch_ids=None, user_id=None, mfs_id=None, mfs_wise_data=False, company_id=None):
    """
    returns mfd batch and canister info
    :param batch_ids: list
    :param user_id: int
    :param mfs_id: int
    :param mfs_wise_data: boolean
    :return:
    """
    clauses = list()
    sub_clause1 = sub_clause2 = False
    DeviceMasterAlias = DeviceMaster.alias()
    DeviceMasterAlias2 = DeviceMaster.alias()
    LocationMasterAlias = LocationMaster.alias()
    clauses.append((BatchMaster.mfd_status << [constants.MFD_BATCH_IN_PROGRESS, constants.MFD_BATCH_PENDING,
                                               constants.MFD_BATCH_PRE_SKIPPED]))  # todo: check for Mfd_batch_pre_skipped status
    deleted_batch_ids = get_mfd_pending_deleted_batch_ids()

    if deleted_batch_ids:
        clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)) |
                       (BatchMaster.id << deleted_batch_ids))
    else:
        clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
    if user_id:
        clauses.append((MfdAnalysis.assigned_to == user_id) | (MfdAnalysis.assigned_to.is_null(True)))
    if mfs_id:
        clauses.append((MfdAnalysis.mfs_device_id == mfs_id) | (MfdAnalysis.mfs_device_id.is_null(True)))
    if batch_ids:
        clauses.append((BatchMaster.id << batch_ids))

    sub_query = MfdAnalysis.select(BatchMaster.id, BatchMaster.status).dicts() \
        .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
        .where(functools.reduce(operator.and_, clauses)) \
        .order_by(MfdAnalysis.batch_id) \
        .group_by(MfdAnalysis.batch_id)

    for status in sub_query:
        if status['status'] == settings.BATCH_IMPORTED:
            pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(status['id'])
            if pending_trolley_sequence:
                sub_clause1 = ((MfdAnalysis.trolley_seq << pending_trolley_sequence) & (BatchMaster.id == status['id']))

        else:
            pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(status['id'])
            if pending_trolley_sequence:
                sub_clause2 = ((MfdAnalysis.trolley_seq << pending_trolley_sequence) & (BatchMaster.id == status['id']))
    if sub_clause1 or sub_clause2:
        clauses.append((sub_clause1 | sub_clause2))

    else:
        return []  # if there are no pending trolleys in imported and skipped batches then no data will be shown

    try:
        query = MfdAnalysis.select(BatchMaster.id.alias('batch_id'),
                                   BatchMaster.name.alias('batch_name'),
                                   BatchMaster.imported_date,
                                   BatchMaster.scheduled_start_time,
                                   CodeMaster.id.alias('mfd_batch_status_id'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.assigned_to)).alias('assigned_user_id'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(DeviceMaster.name)).alias('assigned_trolley'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(DeviceMasterAlias.name)).alias('assigned_mfs'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(DeviceMasterAlias.id)).alias('assigned_mfs_id'),
                                   CodeMaster.value.alias('mfd_batch_status'),
                                   fn.SUM(fn.IF(MfdAnalysis.assigned_to.is_null(True), 1,
                                                fn.IF(MfdAnalysis.status_id != constants.MFD_CANISTER_SKIPPED_STATUS, 1,
                                                      fn.IF(MfdAnalysis.mfd_canister_id.is_null(True), 0,
                                                            1)
                                                      ))).alias('total_canister'),
                                   fn.SUM(fn.IF(MfdAnalysis.status_id != constants.MFD_CANISTER_SKIPPED_STATUS, 1,
                                                fn.IF(MfdAnalysis.mfd_canister_id.is_null(True), 0,
                                                      1)
                                                )).alias('assigned_canister'),
                                   fn.SUM(fn.If(MfdAnalysis.status_id << ([constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                                           constants.MFD_CANISTER_PENDING_STATUS]),
                                                0,
                                                fn.IF(MfdAnalysis.status_id << [constants.MFD_CANISTER_SKIPPED_STATUS],
                                                      fn.IF(MfdAnalysis.mfd_canister_id.is_null(True), 0, 0),
                                                      fn.IF(MfdAnalysis.status_id <<
                                                            [constants.MFD_CANISTER_FILLED_STATUS,
                                                             constants.MFD_CANISTER_VERIFIED_STATUS,
                                                             constants.MFD_CANISTER_RTS_REQUIRED_STATUS],
                                                            fn.IF(DeviceMasterAlias2.device_type_id << [
                                                                settings.DEVICE_TYPES['Manual Canister Cart'],
                                                                settings.DEVICE_TYPES['ROBOT']],
                                                                  1, fn.IF(MfdCanisterMaster.state_status ==
                                                                           constants.MFD_CANISTER_ACTIVE, 0, 1)), 1)))
                                          ).coerce(False).alias('filled_canister'),
                                   fn.SUM(fn.If(MfdAnalysis.status_id == constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                1, 0)
                                          ).coerce(False).alias('user_in_progress_count'),
                                   fn.SUM(fn.If(MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS,
                                                1, 0)
                                          ).coerce(False).alias('pending_canister')
                                   ).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(CodeMaster, on=CodeMaster.id == BatchMaster.mfd_status) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMasterAlias.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMasterAlias.device_id == DeviceMaster.id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=MfdAnalysis.mfs_device_id == DeviceMasterAlias.id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=DeviceMasterAlias2.id == LocationMaster.device_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(MfdAnalysis.batch_id) \
            .group_by(MfdAnalysis.batch_id)

        if mfs_wise_data:
            query = query.group_by(MfdAnalysis.mfs_device_id)
        logger.info("in db_get_mfd_batch_info, query : {}".format(query))
        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in db_get_mfd_batch_info: {}".format(e))
        raise e


@log_args_and_response
def populate_mfd_trolley_data(update_data, analysis_id):
    """
    @param update_data: dict
    @param analysis_id: int
    @return: status
    """
    # todo move this function to Model
    try:
        response = MfdAnalysis.update(**update_data).where(MfdAnalysis.id == analysis_id).execute()
        logger.info(response)
        return True

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise


@log_args_and_response
def populate_mfd_analysis_details_status(status, analysis_id):
    try:
        response = MfdAnalysisDetails.update(status_id=status).where(
            MfdAnalysisDetails.analysis_id == analysis_id).execute()
        logger.info(response)

        return response

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise

    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def populate_mfd_analysis_trolley(trolley_seq, order_no, analysis_id):
    try:
        response = MfdAnalysis.update(trolley_seq=trolley_seq, order_no=order_no).where(
            MfdAnalysis.id == analysis_id).execute()
        logger.info(response)

        return response

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise

    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def db_get_batch_drugs_by_trolley(batch_id: int, user_id: int, mfs_id: int, trolley_id_list: List[int]) -> \
        Dict[int, Dict[str, Any]]:

    trolley_sorted_dict: Dict[int, Dict[str, Any]] = dict()
    trolley_data: Dict[int, Dict[str, Any]] = dict()

    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()

    try:
        fields_dict = {
            "ndc": DrugMaster.ndc,
            "imprint": DrugMaster.imprint,
            "strength": DrugMaster.strength_value,
            "color": DrugMaster.color,
            "drug_fndc_txr": DrugMaster.concated_fndc_txr_field("##"),
            "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
            "stock_updated_by": DrugStockHistory.created_by
        }

        clauses = list()
        clauses.append((MfdAnalysis.assigned_to == user_id))
        clauses.append((MfdAnalysis.batch_id == batch_id))
        clauses.append((MfdAnalysis.mfs_device_id == mfs_id))
        clauses.append((BatchMaster.mfd_status != constants.MFD_BATCH_FILLED))
        clauses.append((MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS) |
                       mfd_canister_inprogress_condition)
        clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
        clauses.append((MfdAnalysisDetails.status_id.not_in([constants.MFD_DRUG_SKIPPED_STATUS])))

        if trolley_id_list:
            clauses.append((DeviceMaster.id << trolley_id_list))

        select_fields = [DeviceMaster.name.alias("trolley_name"),
                         DeviceMaster.id.alias("trolley_id"),
                         MfdAnalysis.trolley_seq,
                         DrugMaster.id.alias('drug_id'),
                         DrugMaster.strength,
                         DrugMaster.strength_value,
                         MfdAnalysisDetails.quantity,
                         fields_dict['drug_name'].alias('drug_name'),
                         DrugMaster.txr,
                         DrugMaster.ndc,
                         DrugMaster.formatted_ndc,
                         DrugMaster.color,
                         DrugMaster.imprint,
                         DrugMaster.image_name,
                         DrugMaster.brand_flag,
                         DrugMaster.manufacturer,
                         fields_dict['drug_fndc_txr'].alias('drug_fndc_txr'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                         fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by)
                             .alias('stock_updated_by'),
                         fn.IF(DrugStockHistory.created_date.is_null(True), None, DrugStockHistory.created_date)
                             .alias('stock_updated_time'),
                         fn.sum(MfdAnalysisDetails.quantity).alias("required_quantity"),
                         PatientRx.daw_code,
                         DrugDetails.last_seen_by,
                         DrugStatus.ext_status,
                         DrugStatus.ext_status_updated_date,
                         DrugStatus.last_billed_date
                         ]
        query = MfdAnalysis.select(*select_fields).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(DrugStatus, on=DrugMaster.id == DrugStatus.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id)))

        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))

        query = query.group_by(MfdAnalysis.trolley_seq, DrugMaster.formatted_ndc, DrugMaster.txr, PatientRx.daw_code) \
            .order_by(MfdAnalysis.trolley_seq, DrugMaster.drug_name)

        logger.info("Preparing Trolley Data by Trolley Sequence and Unique Drugs...")
        for record in query:
            fndc_txr = '{}{}{}'.format(record["formatted_ndc"], '##', record['txr'])

            if record["trolley_seq"] not in trolley_data:
                record["daw_list"] = dict()
                record["daw_list"][record["daw_code"]] = record["required_quantity"]

                # del record["daw_code"] # remove this key from record
                record["dawmax"] = max(record["daw_list"])

                trolley_dict = {"trolley_name": record["trolley_name"],
                                "trolley_id": record["trolley_id"],
                                "drug_list": {
                                    fndc_txr: record}
                                }
                trolley_data[record["trolley_seq"]] = trolley_dict
            else:
                if fndc_txr not in trolley_data[record["trolley_seq"]]["drug_list"]:
                    record["daw_list"] = {}
                    record["daw_list"][record["daw_code"]] = record["required_quantity"]

                    # del record["daw_code"] # remove this key from record
                    record["dawmax"] = max(record["daw_list"])
                    trolley_data[record["trolley_seq"]]["drug_list"][fndc_txr] = record
                else:
                    # updating daw wise quantity
                    previous_drug_data = trolley_data[record["trolley_seq"]]["drug_list"][fndc_txr]
                    previous_drug_data["daw_list"][record["daw_code"]] = record["required_quantity"]
                    # updating total quantity
                    previous_drug_data["quantity"] += record["quantity"]
                    previous_drug_data["dawmax"] = max(previous_drug_data["daw_list"])
                    trolley_data[record["trolley_seq"]]["drug_list"][fndc_txr] = previous_drug_data

        logger.info("Prepare the Trolley Data to store the Drugs in List format vs previously stored by fndc key...")
        for trolley_seq, trolley in trolley_data.items():
            drug_list = list(trolley["drug_list"].values())
            trolley["drug_list"] = drug_list

            trolley_sorted_dict[trolley_seq] = trolley

        logger.info("Sort the Trolley Data by Trolley Sequence...")
        trolley_sorted_dict = collections.OrderedDict(sorted(trolley_sorted_dict.items()))

        return trolley_sorted_dict

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_delivery_date_of_mfd_trolley(user_id, batch_id, mfs_id, trolley_id_list):
    """
    This function returns the delivery date of trolley >>
    delivery_date_from and delivery_date_to are maximum and minimum delivery date of packs whose mfd canister drug will be placed in trolley respectively.
    """
    try:
        logger.info("In get_delivery_date_of_mfd_trolley")
        delivery_date_dict = dict()
        clauses = list()
        clauses.append((MfdAnalysis.assigned_to == user_id))
        clauses.append((MfdAnalysis.batch_id == batch_id))
        clauses.append((MfdAnalysis.mfs_device_id == mfs_id))
        clauses.append((BatchMaster.mfd_status != constants.MFD_BATCH_FILLED))
        clauses.append((MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS) |
                       mfd_canister_inprogress_condition)
        clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
        clauses.append((MfdAnalysisDetails.status_id.not_in([constants.MFD_DRUG_SKIPPED_STATUS])))

        if trolley_id_list:
            clauses.append((DeviceMaster.id << trolley_id_list))

        time_query = MfdAnalysis.select(MfdAnalysis.trolley_seq,
                                        fn.DATE(fn.MAX(PackHeader.scheduled_delivery_date)).alias("delivery_date_to"),
                                        fn.DATE(fn.MIN(PackHeader.scheduled_delivery_date)).alias("delivery_date_from")
                                        ).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id)

        if clauses:
            time_query = time_query.where(functools.reduce(operator.and_, clauses))

        time_query = time_query.group_by(MfdAnalysis.trolley_seq)

        for data in time_query:
            delivery_date_dict[data["trolley_seq"]] = {"delivery_date_from": data["delivery_date_from"],
                                              "delivery_date_to": data["delivery_date_to"]}

        logger.info(f"In get_delivery_date_of_mfd_trolley, delivery_date_dict: {delivery_date_dict}")

        return delivery_date_dict

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e

    except Exception as e:
        logger.error(f"Error in get_delivery_date_of_mfd_trolley: {e}")


@log_args_and_response
def db_get_trolley_by_batch(batch_id, user_id, mfs_id) -> Dict[int, Dict[str, Any]]:

    trolley_sorted_dict: Dict[int, Dict[str, Any]] = dict()
    # trolley_data: List[Dict[str, Any]] = list()

    LocationMasterAlias = LocationMaster.alias()
    # DeviceMasterAlias = DeviceMaster.alias()

    try:
        clauses = list()
        clauses.append((MfdAnalysis.assigned_to == user_id))
        clauses.append((MfdAnalysis.batch_id == batch_id))
        clauses.append((MfdAnalysis.mfs_device_id == mfs_id))
        clauses.append((BatchMaster.mfd_status != constants.MFD_BATCH_FILLED))
        clauses.append((MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS) |
                       mfd_canister_inprogress_condition)
        clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
        clauses.append((MfdAnalysisDetails.status_id.not_in([constants.MFD_DRUG_SKIPPED_STATUS])))

        logger.info("Preparing Trolley Data to display in Print List for MFD Drug List...")
        trolley_data = MfdAnalysis.select(DeviceMaster.name.alias("trolley_name"),
                                          DeviceMaster.id.alias("trolley_id"),
                                          MfdAnalysis.trolley_seq).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(DeviceMaster.name, DeviceMaster.id, MfdAnalysis.trolley_seq)


        for trolley in trolley_data:
            trolley_sorted_dict[trolley["trolley_seq"]] = trolley
            delivery_date = get_delivery_date_of_mfd_trolley(user_id=user_id, batch_id=batch_id, mfs_id=mfs_id,
                                                             trolley_id_list=[trolley['trolley_id']])
            trolley_sorted_dict[trolley["trolley_seq"]]["delivery_date_from"] = delivery_date[trolley["trolley_seq"]]["delivery_date_from"]
            trolley_sorted_dict[trolley["trolley_seq"]]["delivery_date_to"] = delivery_date[trolley["trolley_seq"]]["delivery_date_to"]


        logger.info("Sort the Trolley Data by Trolley Sequence...")
        trolley_sorted_dict = collections.OrderedDict(sorted(trolley_sorted_dict.items()))
        return trolley_sorted_dict

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_batch_drugs(batch_id, user_id, mfs_id, filter_fields, sort_fields):
    """
    returns pending drugs data to be filled by particular user
    :param batch_id: int
    :param user_id: int
    :param mfs_id: int
    :param filter_fields: dict
    :param sort_fields: list
    :return:
    """
    # batch_packs_dict = dict()
    drug_data = {}
    ndc_list = []
    # response = {}
    DrugMasterAlias = DrugMaster.alias()
    txr_list = []

    like_search_list = ['ndc', 'imprint', 'color', 'shape', 'drug_name']
    exact_search_list = ['strength', 'canister_id']
    membership_search_list = []

    fields_dict = {
        "ndc": DrugMaster.ndc,
        "imprint": DrugMaster.imprint,
        "strength": DrugMaster.strength_value,
        "color": DrugMaster.color,
        "drug_fndc_txr": DrugMaster.concated_fndc_txr_field("##"),
        "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
        "stock_updated_by": DrugStockHistory.created_by
    }

    order_list = list()

    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()

    order_list = get_orders(order_list, fields_dict, sort_fields)
    order_list.append(DrugMaster.drug_name)  # To provide name sorting
    clauses = list()
    clauses.append((MfdAnalysis.assigned_to == user_id))
    clauses.append((MfdAnalysis.batch_id == batch_id))
    clauses.append((MfdAnalysis.mfs_device_id == mfs_id))
    clauses.append((BatchMaster.mfd_status != constants.MFD_BATCH_FILLED))
    clauses.append((MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS) | mfd_canister_inprogress_condition)
    clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
    clauses.append((MfdAnalysisDetails.status_id.not_in([constants.MFD_DRUG_SKIPPED_STATUS])))

    clauses = get_filters(clauses, fields_dict, filter_fields,
                          exact_search_fields=exact_search_list,
                          like_search_fields=like_search_list,
                          membership_search_fields=membership_search_list)

    patient_list = MfdAnalysis.select(PatientMaster.id,
                                      FacilityMaster.facility_name,
                                      PatientMaster.concated_patient_name_field().alias("patient_name"),
                                      fn.count(fn.distinct(PackDetails.id)).alias('total_packs')
                                      ).dicts() \
        .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
        .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
        .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
        .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
        .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id) \
        .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
        .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
        .join(UniqueDrug, on=(UniqueDrug.txr == DrugMaster.txr) &
                             (UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)) \
        .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
        .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
        .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
        .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                     (DrugStockHistory.is_active == 1) &
                                                     (PackDetails.company_id == DrugStockHistory.company_id))) \
        .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
        .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
        .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
        .where(functools.reduce(operator.and_, clauses)) \
        .group_by(PatientMaster.id) \
        .order_by(PatientMaster.id)

    select_fields = [DrugMaster.id.alias('drug_id'),
                     DrugMaster.strength,
                     DrugMaster.strength_value,
                     MfdAnalysisDetails.quantity,
                     fields_dict['drug_name'].alias('drug_name'),
                     DrugMaster.txr,
                     DrugMaster.ndc,
                     DrugMaster.formatted_ndc,
                     DrugMaster.color,
                     DrugMaster.imprint,
                     DrugMaster.image_name,
                     DrugMaster.brand_flag,
                     DrugMaster.manufacturer,
                     fields_dict['drug_fndc_txr'].alias('drug_fndc_txr'),
                     fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                           DrugStockHistory.is_in_stock).alias("is_in_stock"),
                     fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by)
                         .alias('stock_updated_by'),
                     fn.IF(DrugStockHistory.created_date.is_null(True), None, DrugStockHistory.created_date)
                         .alias('stock_updated_time'),
                     fn.sum(MfdAnalysisDetails.quantity).alias("required_quantity"),
                     PatientRx.daw_code,
                     DrugDetails.last_seen_by,
                     DrugStatus.ext_status,
                     DrugStatus.ext_status_updated_date,
                     DrugStatus.last_billed_date
                     ]

    try:
        query = MfdAnalysis.select(*select_fields).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(DrugStatus, on=DrugMaster.id == DrugStatus.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id)))

        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        query = query.group_by(DrugMaster.formatted_ndc, DrugMaster.txr, PatientRx.daw_code) \
            .order_by(DrugMaster.drug_name)
        if order_list:
            query = query.order_by(*order_list)
        count = query.count()

        logger.debug("Query: {}".format(query))
        for record in query:
            if record["daw_code"] == 0:
                alternate_drugs_in_packs = DrugMaster.select(
                    fn.IF(fn.COUNT(fn.DISTINCT(DrugMasterAlias.id)) != 0, True, False).alias(
                        'alternate_drug_available')
                ).dicts().join(DrugMasterAlias, JOIN_LEFT_OUTER, on=(DrugMasterAlias.txr == DrugMaster.txr) &
                                                                    (
                                                                            DrugMasterAlias.formatted_ndc !=
                                                                            DrugMaster.formatted_ndc) &
                                                                    (
                                                                            DrugMasterAlias.brand_flag ==
                                                                            settings.GENERIC_FLAG) &
                                                                    (
                                                                            DrugMaster.brand_flag == settings.GENERIC_FLAG)) \
                    .where(DrugMaster.formatted_ndc == record['formatted_ndc'],
                           DrugMaster.txr == record['txr']).get()
                record['alternate_drug_available'] = bool(alternate_drugs_in_packs['alternate_drug_available'])
            fndc_txr = '{}{}{}'.format(record["formatted_ndc"], '##', record['txr'])
            txr_list.append(record['txr'])
            ndc_list.append(record['ndc'])
            if fndc_txr not in drug_data:
                record["daw_list"] = {}
                record["daw_list"][record["daw_code"]] = record["required_quantity"]

                # del record["daw_code"] # remove this key from record
                record["dawmax"] = max(record["daw_list"])
                if not record.get('alternate_drug_available', False):
                    record['alternate_drug_available'] = False
                drug_data[fndc_txr] = record
            else:
                # updating daw wise quantity
                previous_drug_data = drug_data[fndc_txr]
                previous_drug_data["daw_list"][record["daw_code"]] = record["required_quantity"]
                # updating total quantity
                previous_drug_data["quantity"] += record["quantity"]
                previous_drug_data["dawmax"] = max(previous_drug_data["daw_list"])
                if not previous_drug_data.get('alternate_drug_available', False):
                    # todo check case
                    previous_drug_data['alternate_drug_available'] = record.get('alternate_drug_available', False)
                drug_data[fndc_txr] = previous_drug_data

        inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
        for record in drug_data.values():
            record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), 0)
            record['is_in_stock'] = 0 if record["inventory_qty"] == 0 else 1
        return list(drug_data.values()), count, list(patient_list), ndc_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfd_canister_batch_id_for_transfers(system_id: int, batch_id: int):
    logger.info("In get_next_mfd_batch")
    batch_device_dict = dict()
    try:
        LocationMasterAlias = LocationMaster.alias()

        mfd_canister_status = [constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        mfd_canister_transfer_pending_status = [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                constants.MFD_CANISTER_DROPPED_STATUS,
                                                constants.MFD_CANISTER_MVS_FILLING_REQUIRED]

        batch_status_list = [settings.BATCH_DELETED, settings.BATCH_PROCESSING_COMPLETE]

        query = MfdAnalysis.select(MfdAnalysis.batch_id, MfdAnalysis.dest_device_id).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .where(BatchMaster.system_id == system_id,
                   BatchMaster.id.not_in([batch_id]),
                   (((MfdAnalysis.status_id << mfd_canister_status) & (BatchMaster.status.not_in(batch_status_list))) |
                    ((MfdAnalysis.status_id << mfd_canister_transfer_pending_status) &
                     (DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'])
                     ))) \
            .group_by(MfdAnalysis.dest_device_id, MfdAnalysis.batch_id) \
            .order_by(BatchMaster.id)

        logger.info('query cdb update batch assign: {}'.format(query))
        for record in query:
            if record['batch_id'] not in batch_device_dict.keys():
                batch_device_dict[record['batch_id']] = list()
            batch_device_dict[record['batch_id']].append(record['dest_device_id'])

        return batch_device_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e)
        return batch_device_dict


@log_args_and_response
def get_required_mfd_canister_data(batch_id, manual_pre_fill, system_id):
    """
    Query to get required mfd canisters count and data from given batch_id
    @param batch_id: int
    @return: query
    """
    logger.info("In get_required_mfd_canister_data")
    try:
        clauses = []

        if not manual_pre_fill:
            clauses.append(MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS)
            clauses.append(MfdAnalysis.assigned_to.is_null(True))

        else:
            progress_batch = get_progress_batch_id(system_id)
            if progress_batch:
                pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(progress_batch)
                if pending_trolley_sequence:
                    clauses.append(MfdAnalysis.trolley_seq << pending_trolley_sequence)

            clauses.append(MfdAnalysis.assigned_to.is_null(True))

        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.batch_id,
                                   MfdAnalysis.dest_device_id,
                                   MfdAnalysis.dest_quadrant,
                                   MfdAnalysis.order_no,
                                   MfdAnalysis.status_id.alias('mfd_canister_status'),
                                   MfdAnalysisDetails.slot_id,
                                   MfdAnalysisDetails,
                                   PackDetails.id.alias("pack_id"),
                                   PatientRx.patient_id,
                                   PackDetails.order_no.alias('pack_queue_order'),
                                   PackHeader.scheduled_delivery_date.alias("delivery_date")
                                   ).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   BatchMaster.status.not_in([settings.BATCH_MFD_USER_ASSIGNED,
                                              settings.BATCH_DELETED,
                                              settings.BATCH_PROCESSING_COMPLETE]),
                   PackDetails.pack_status != settings.DELETED_PACK_STATUS) \
            .order_by(PackDetails.order_no)

        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return e
    except DoesNotExist as e:
        logger.error(e)
        return None


def db_get_drug_analysis_query(batch_id, user_id, old_ndc_record):
    """
    returns query to get the analysis info for the specified ndc
    :param batch_id: int
    :param user_id: int
    :param old_ndc_record: str
    :return: query
    """
    try:
        analysis_id_query = MfdAnalysis.select(MfdAnalysis.id,
                                               MfdAnalysisDetails.slot_id,
                                               PackRxLink.pack_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(DrugMaster.formatted_ndc == old_ndc_record.formatted_ndc,
                   DrugMaster.txr == old_ndc_record.txr,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysisDetails.status_id == constants.MFD_DRUG_PENDING_STATUS,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_PENDING_STATUS,
                                             constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                             constants.MFD_CANISTER_SKIPPED_STATUS],
                   SlotTransaction.id.is_null(True),
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
        return analysis_id_query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_skip_drug(analysis_details_ids):
    """
    marks the drug as skipped
    :param analysis_details_ids: list
    :return: int
    """
    # batch_packs_dict = dict()
    logger.info("In db_skip_drug")
    try:
        status = MfdAnalysisDetails.db_update_drug_status(analysis_details_ids, constants.MFD_DRUG_SKIPPED_STATUS)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_drug_status(analysis_details_ids, status_id):
    """
    updates status of drug for given analysis_details id
    :param analysis_details_ids: list
    :param status_id: int
    :return:
    """
    try:
        status = MfdAnalysisDetails.db_update_drug_status(analysis_details_ids, status_id)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_drug_tracker_from_mfd_analysis_details_ids(mfd_analysis_details_ids):
    try:
        status = None
        if mfd_analysis_details_ids:
            query = MfdAnalysisDetails.select(MfdAnalysisDetails.slot_id).dicts().where(MfdAnalysisDetails.id.in_(mfd_analysis_details_ids))
            slot_ids = [data["slot_id"] for data in query]

            if slot_ids:
                # status = DrugTracker.update(is_overwrite=2).where(DrugTracker.slot_id.in_(slot_ids)).execute()
                update_dict: dict = dict()
                update_dict["is_overwrite"] = 2
                update_dict["modified_date"] = get_current_date_time()

                status = DrugTracker.db_update_drug_tracker_by_slot_id(update_dict=update_dict,
                                                                       slot_ids=slot_ids)

        return status
    except Exception as e:
        logger.error(f"Error in update_drug_tracker_from_mfd_analysis_details_ids: {e}")


def get_suggested_empty_location(mfs_ids: list) -> list:
    """
    returns already suggested locations for skipped canisters
    :param mfs_ids:
    :return:
    """
    try:
        suggested_locations = list()
        query = MfdAnalysis.select(MfdAnalysis).dicts() \
            .where(MfdAnalysis.mfs_device_id << mfs_ids,
                   MfdAnalysis.mfd_canister_id.is_null(False),
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_SKIPPED_STATUS])
        for record in query:
            suggested_locations.append(record['trolley_location_id'])
        return suggested_locations
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def current_mfs_placed_canisters(analysis_ids: list) -> dict:
    """
    returns data of canisters currently placed on mfs
    :param analysis_ids:
    :return:
    """
    try:
        logger.info("In current_mfs_placed_canisters")
        home_cart_analysis_dict = defaultdict(list)
        home_cart_mfs_dict = defaultdict(set)
        skip_location_info = dict()
        LocationMasterAlias = LocationMaster.alias()
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdCanisterMaster.home_cart_id,
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(mfd_canister_inprogress_condition,
                   MfdAnalysis.id << analysis_ids)
        for record in query:
            home_cart_analysis_dict[record['home_cart_id']].append(record['mfd_analysis_id'])
            home_cart_mfs_dict[record['home_cart_id']].add(record['mfs_device_id'])

        for home_cart_id, analysis_id_data in home_cart_analysis_dict.items():
            suggested_empty_location = get_suggested_empty_location(list(home_cart_mfs_dict[home_cart_id]))
            skip_location_info[home_cart_id] = {'mfs_ids': list(home_cart_mfs_dict[home_cart_id]),
                                                'skip_locations': suggested_empty_location,
                                                'skip_analysis_ids': home_cart_analysis_dict[home_cart_id]}
        return skip_location_info
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_empty_locations(drawer_type, count, trolley_id, exclude_locations=None):
    """

    :param drawer_type:
    :param count:
    :param trolley_id:
    :param exclude_locations:
    :return:
    """
    logger.info(f'In get_empty_locations, getting empty_location_count: {count} for trolly: {trolley_id}')
    try:
        empty_locations = defaultdict(list)
        clauses = [LocationMaster.device_id == trolley_id, MfdCanisterMaster.id.is_null(True)]
        if drawer_type == constants.MFD_TROLLEY_EMPTY_DRAWER_TYPE:
            clauses.append((ContainerMaster.drawer_level << constants.MFD_TROLLEY_EMPTY_DRAWER_LEVEL))
        elif drawer_type == constants.MFD_TROLLEY_RTS_DRAWER_TYPE:
            # TODO: update for rts
            pass
        if exclude_locations:
            clauses.append((LocationMaster.id.not_in(exclude_locations)))
        empty_location = LocationMaster.select(LocationMaster.container_id,
                                               LocationMaster.id.alias('loc_id')).dicts() \
            .join(ContainerMaster, on=(ContainerMaster.id == LocationMaster.container_id)) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .where(functools.reduce(operator.and_, clauses))
        for record in empty_location:
            empty_locations[record['container_id']].append(record['loc_id'])
        empty_location_drawer_wise = empty_locations.values()

        sorted_empty_location_drawer_wise = sorted(empty_location_drawer_wise, key=len, reverse=True)
        logger.info(f"In get_empty_locations, sorted_empty_location_drawer_wise: {sorted_empty_location_drawer_wise}")
        final_empty_locations = list()
        for sorted_empty_loc in sorted_empty_location_drawer_wise:
            if len(sorted_empty_loc) + len(final_empty_locations) <= count:
                final_empty_locations.extend(sorted_empty_loc)
            else:
                require_loc_count = count - (len(final_empty_locations))
                final_empty_locations.extend(sorted_empty_loc[:require_loc_count])
            if len(final_empty_locations) == count:
                return final_empty_locations

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_dest_location_for_current_mfd_canister(analysis_ids, current_suggested_dest_location_ids, trolley_id):
    """
    gets the empty location and updates mfs_analysis
    :param analysis_ids:
    :param current_suggested_dest_location_ids:
    :param trolley_id:
    :return:
    """
    try:
        logger.info("In update_dest_location_for_current_mfd_canister")
        empty_location = get_empty_locations(constants.MFD_TROLLEY_EMPTY_DRAWER_TYPE, len(analysis_ids), trolley_id,
                                             current_suggested_dest_location_ids)
        logger.info(f"update_dest_location_for_current_mfd_canister, empty_location:{empty_location}")
        loc_status = MfdAnalysis.db_update_dest_location(analysis_ids, empty_location)
        return loc_status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_current_skipped_analysis_ids(mfs_id: int) -> tuple:
    """
    returns list of current mfd_analysis_ids and list of analysis_ids that are skipped and canister is not present on
    mfs
    :param mfs_id:
    :return: tuple of lists
    """
    try:
        current_mfd_analysis = list()
        currently_skipped_without_canister = list()
        current_mfs_data = TempMfdFilling.select(TempMfdFilling.mfd_analysis_id,
                                                 MfdAnalysis.status_id,
                                                 MfdAnalysis.mfd_canister_id
                                                 ).dicts() \
            .join(MfdAnalysis, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .where(MfdAnalysis.mfs_device_id == mfs_id)
        for record in current_mfs_data:
            current_mfd_analysis.append(record['mfd_analysis_id'])
            if record['status_id'] == constants.MFD_CANISTER_SKIPPED_STATUS and record['mfd_canister_id'] is None:
                currently_skipped_without_canister.append(record['mfd_analysis_id'])

        logger.info('current_mfd_analysis: {} and currently_skipped_without_canister_mfd_analysis_ids: {} for mfs_id: '
                     '{}'.format(current_mfd_analysis, currently_skipped_without_canister, mfs_id))
        return current_mfd_analysis, currently_skipped_without_canister
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_temp_mfs_data(mfs_ids: list) -> bool:
    """
    if all the mfd_analysis_ids that are currently on mfs are skipped and do not have canisters placed on any location
    or have any error present on them then deletes data from temp_mfd_filling
    :param mfs_ids:
    :return:
    """
    try:
        for mfs_id in mfs_ids:
            current_mfd_analysis_ids, currently_skipped_analysis_ids = get_current_skipped_analysis_ids(mfs_id)
            if current_mfd_analysis_ids == currently_skipped_analysis_ids:
                logger.info("same_analysis_found_for_mfs_id: {}".format(mfs_id))
                mfd_remove_current_canister_data(mfs_id)
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfd_history_data(analysis_ids: list, updated_status: int, user_id: int, action_id: int = None) -> list:
    """
    gets current status of analysis_ids
    @param analysis_ids:
    @param updated_status:
    @param user_id:
    @return:
    @param action_id:
    """
    try:
        logger.info("In get_mfd_history_data")
        analysis_status_dict = dict()
        current_data = MfdAnalysis.db_get_analysis_data_from_analysis_ids(analysis_ids)
        for record in current_data:
            analysis_status_dict[record['id']] = {'previous_status_id': record['status_id'],
                                                  'current_status_id': updated_status,
                                                  'analysis_id': record['id'],
                                                  'action_id': action_id if action_id else
                                                  constants.MFD_ACTION_STATUS_MAP[updated_status],
                                                  'action_taken_by': user_id}
        return list(analysis_status_dict.values())
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_latest_mfd_cycle_history_data(analysis_ids: list, comment: str) -> list:
    """
    gets current status of analysis_ids
    :param comment:
    :param analysis_ids:
    :return:
    """
    try:
        history_comment_dict = dict()
        current_history_data = MfdCycleHistory.db_get_max_history_id(analysis_ids)
        for record in current_history_data:
            history_comment_dict[record['analysis_id']] = {'cycle_history_id': record['max_history_id'],
                                                           'comment': comment}
        return list(history_comment_dict.values())
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_canister_status(analysis_ids, status_id, user_id, comment=None, action_id=None):
    """
    updates mfd canister status
    :param analysis_ids:
    :param status_id:
    :param user_id:
    :param comment:
    :param action_id:
    :return:
    """
    try:
        analysis_current_status_list = get_mfd_history_data(analysis_ids, status_id, user_id, action_id=action_id)
        logger.info('analysis_current_status_list: {}'.format(analysis_current_status_list))

        status = MfdAnalysis.db_update_canister_status(analysis_ids, status_id)
        logger.info(f"In db_update_canister_status, status of update mfd analysis: {status}")

        if analysis_current_status_list:
            cycle_status = MfdCycleHistory.db_add_history_data(analysis_current_status_list)
            logger.info('In db_update_canister_status: cycle_status: {}'.format(cycle_status))

        if comment:
            latest_history_data = get_latest_mfd_cycle_history_data(analysis_ids, comment)
            logger.info('latest_history_data: {}'.format(latest_history_data))
            if latest_history_data:
                comment_add_status = MfdCycleHistoryComment.db_add_comment_history_data(latest_history_data)
                logger.info('In db_update_canister_status: comment_add_status: {}'.format(comment_add_status))
        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_analysis_ids_drug(company_id, user_id, drug_id, batch_id, status, mfs_id, skip_for_batch=False):
    """
    returns analysis_ids(canister) and analysis_details_ids(drug) in which the particular drug is used
    @param user_id:
    @param company_id:
    @param skip_for_batch:
    @param mfs_id:
    @param batch_id:
    @param drug_id:
    @param user_id:
    @param company_id:
    @param status:
    """
    analysis_details_ids = set()
    analysis_ids = set()
    LocationMasterAlias = LocationMaster.alias()

    logger.info(f"In db_get_analysis_ids_drug, drug_id: {drug_id}, mfs_id:{mfs_id}")

    try:
        # getting all the drug_ids of same fndc_txr of the given drug(same drug)
        try:
            current_drug = get_drug_status_by_drug_id(drug_id, dicts=True)
        except DoesNotExist as e:
            return analysis_ids, analysis_details_ids

        drug_ids = [item.id for item in DrugMaster.get_drugs_by_formatted_ndc_txr(
            current_drug['formatted_ndc'],
            current_drug['txr']
        )]

        logger.info(f"In db_get_analysis_ids_drug drug_ids:{drug_ids}")
        # remove the filled drug status at line 1229 to resolve the bug of mfd_canister_skip

        if not drug_ids:
            return analysis_ids, analysis_details_ids
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysis.batch_id == batch_id,
                   PackDetails.company_id == company_id,
                   MfdAnalysis.mfs_device_id == mfs_id,
                   SlotDetails.drug_id << drug_ids,
                   MfdAnalysis.status_id << status,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_PENDING_STATUS])
        if not skip_for_batch:
            query = query.where(mfd_canister_inprogress_condition_for_skip)

        for record in query:
            analysis_details_ids.add(record['analysis_details_id'])
            analysis_ids.add(record['analysis_id'])
        return analysis_ids, analysis_details_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_filled_drug_analysis_ids(company_id, user_id, current_analysis_ids, batch_id, mfs_id, action):
    """
    gets valid analysis ids for canister update
    @param company_id:
    @param user_id:
    @param current_analysis_ids:
    @param batch_id:
    @param mfs_id:
    @return:
    @param action:
    """
    analysis_details_ids = set()
    analysis_ids = set()
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysis.mfs_device_id == mfs_id,
                   MfdAnalysis.batch_id == batch_id,
                   PackDetails.company_id == company_id,
                   MfdAnalysis.id << current_analysis_ids,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_FILLED_STATUS,
                                                    constants.MFD_DRUG_SKIPPED_STATUS])

        if action == 'verification':
            query = query.where(MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS])
        for record in query:
            analysis_details_ids.add(record['analysis_details_id'])
            analysis_ids.add(record['analysis_id'])
        return analysis_ids, analysis_details_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_get_not_skipped_analysis_ids(analysis_ids):
    """
    returns the analysis_ids which has filled or pending drug
    :param analysis_ids:
    :return:
    """
    # todo: remove this as not in use
    not_skipped_analysis_ids = set()
    analysis_ids_list = list(analysis_ids)
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.status_id.alias('canister_status'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << analysis_ids_list,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_PENDING_STATUS,
                                                    constants.MFD_DRUG_RTS_REQUIRED_STATUS,
                                                    constants.MFD_DRUG_DROPPED_STATUS,
                                                    constants.MFD_DRUG_FILLED_STATUS])
        logger.info('canister_skip_query_mfd: {}'.format(query))
        for record in query:
            not_skipped_analysis_ids.add(record['analysis_id'])
        return not_skipped_analysis_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_skipped_analysis_ids(analysis_ids: list) -> list:
    """
    returns the analysis_ids which needs to be skipped
    :param analysis_ids:
    :return:
    """

    skipped_analysis_ids = set()
    analysis_ids_list = list(analysis_ids)
    try:
        logger.info("In db_get_skipped_analysis_ids")

        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id)).alias('canister_status'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.status_id)).alias('drug_status'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << analysis_ids_list) \
            .group_by(MfdAnalysis.id)
        logger.info('In db_get_skipped_analysis_ids, canister_skip_query_mfd: {}'.format(query))
        for record in query:
            drug_status = map(int, record['drug_status'].split(","))
            if set(drug_status).difference({constants.MFD_DRUG_SKIPPED_STATUS}):
                continue
            skipped_analysis_ids.add(record['analysis_id'])
        return list(skipped_analysis_ids)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_rts_analysis_ids(analysis_ids: list) -> list:
    """
    returns the analysis_ids which needs to be marked RTS
    :param analysis_ids:
    :return:
    """
    rts_analysis_ids = set()
    analysis_ids_list = list(analysis_ids)
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id)).alias('canister_status'),
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.status_id)).alias('drug_status'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << analysis_ids_list) \
            .group_by(MfdAnalysis.id)
        logger.info('canister_skip_query_mfd: {}'.format(query))
        for record in query:
            drug_status = map(int, record['drug_status'].split(","))
            if constants.MFD_DRUG_RTS_REQUIRED_STATUS in drug_status:
                if set(drug_status).intersection({constants.MFD_DRUG_PENDING_STATUS, constants.MFD_DRUG_FILLED_STATUS}):
                    continue
                rts_analysis_ids.add(record['analysis_id'])
        return list(rts_analysis_ids)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_filling_pending_analysis_ids(analysis_ids):
    """
    returns the analysis_ids which has pending or rts_required drug
    :param analysis_ids:
    :return:
    """
    not_skipped_analysis_ids = set()
    analysis_ids_list = list(analysis_ids)
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << analysis_ids_list,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_PENDING_STATUS,
                                                    constants.MFD_DRUG_RTS_REQUIRED_STATUS])
        for record in query:
            not_skipped_analysis_ids.add(record['analysis_id'])
        return not_skipped_analysis_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_get_canisters_status_based(analysis_ids, status_ids):
    """
    returns the analysis_ids which has filled or pending drug
    :param analysis_ids: list
    :param status_ids: list
    :return:
    """
    pending_canister_analysis = set()
    analysis_ids_list = list(analysis_ids)
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << analysis_ids_list,
                   MfdAnalysis.status_id != constants.MFD_CANISTER_SKIPPED_STATUS,
                   MfdAnalysisDetails.status_id << status_ids)
        for record in query:
            pending_canister_analysis.add(record['analysis_id'])
        return pending_canister_analysis
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_add_current_filling_data(analysis_ids: list, batch_id: int, mfs_device_id: int) -> int:
    """
    adds in-progress mfd data
    :param analysis_ids: list
    :param batch_id: int
    :param mfs_device_id: int
    :return:
    """
    logger.info("adding_data_in_temp_mfd_filling for mfd_analysis_ids: {} batch_id: {}  mfs_device_id: {}"
                .format(analysis_ids, batch_id, mfs_device_id))
    try:
        for analysis_id in analysis_ids:
            mfs_loc_data = {'batch_id': batch_id,
                            'mfs_device_id': mfs_device_id}

            status = TempMfdFilling.get_or_create(mfd_analysis_id=analysis_id,
                                                  defaults=mfs_loc_data)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_canister_data(record, inventory_data):
    """
    returns required drug data for canister
    :param record: dict
    :return: dict
    """
    record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), 0)
    record['is_in_stock'] = 0 if record["inventory_qty"] == 0 else 1

    return {
        'canister_slot_number': record['mfd_can_slot_no'],
        'quantity': record['quantity'],
        'drug_status': record['drug_status'],
        'drug_status_id': record['drug_status_id'],
        'drop_number': record['drop_number'],
        'drug_name': record['drug_name'],
        'ndc': record['ndc'],
        'strength': record['strength'],
        'strength_value': record['strength_value'],
        'manufacturer': record['manufacturer'],
        'txr': record['txr'],
        'imprint': record['imprint'],
        'color': record['color'],
        'shape': record['shape'],
        'image_name': record['image_name'],
        'drug_id': record['drug_id'],
        'sig': record['sig'],
        'hoa_date': record['hoa_date'],
        'hoa_time': record['hoa_time'],
        'formatted_ndc': record['formatted_ndc'],
        'is_in_stock': record['is_in_stock'],
        'stock_updated_by': record['stock_updated_by'],
        'stock_updated_time': record['stock_updated_time'],
        'last_seen_with': record["last_seen_with"],
        'original_drug_ndc': record['original_drug_ndc']
    }


@log_args_and_response
def db_get_canister_data(progress_batch_id, user_id, mfs_id, analysis_ids=None, ignore_progress_condition=False):
    """
    Returns canister data which are currently on MFS or supposed to be put on MFS of a particular user
    @param progress_batch_id:
    @param user_id:
    @param mfs_id:
    @param analysis_ids:
    @param ignore_progress_condition:
    @return:
    """
    canister_filling_data = dict()
    CodeMasterAlias = CodeMaster.alias()
    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    ContainerMasterAlias = ContainerMaster.alias()
    DrugMasterAlias = DrugMaster.alias()
    inventory_data = {}

    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.mfs_location_number,
                                   DrugMaster,
                                   PatientRx.sig,
                                   SlotHeader.hoa_date,
                                   SlotHeader.hoa_time,
                                   PatientMaster.id.alias('patient_id'),
                                   PatientMaster.concated_patient_name_field().alias('patient_name'),
                                   DeviceMaster.name.alias('dest_trolley_name'),
                                   DeviceMaster.id.alias('dest_trolley_id'),
                                   LocationMasterAlias.container_id.alias('dest_trolley_drawer_id'),
                                   LocationMasterAlias.display_location.alias('dest_trolley_display_location'),
                                   ContainerMaster.serial_number.alias('dest_trolley_drawer_serial_number'),
                                   ContainerMaster.drawer_name.alias('dest_trolley_drawer_name'),
                                   DeviceMasterAlias.name.alias('current_device_name'),
                                   DeviceMasterAlias.id.alias('current_device_id'),
                                   LocationMaster.container_id.alias('current_drawer_id'),
                                   LocationMaster.display_location.alias('current_display_location'),
                                   ContainerMasterAlias.drawer_name.alias('current_drawer_name'),
                                   CodeMaster.value.alias('can_status'),
                                   DrugMasterAlias.ndc.alias('original_drug_ndc'),
                                   CodeMasterAlias.value.alias('drug_status'),
                                   DrugMaster.id.alias('drug_id'),
                                   DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                   MfdAnalysisDetails,
                                   MfdAnalysisDetails.status_id.alias('drug_status_id'),
                                   MfdAnalysisDetails.mfd_can_slot_no,
                                   fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                         DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                   fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by)
                                   .alias('stock_updated_by'),
                                   fn.IF(DrugStockHistory.created_date.is_null(True), None,
                                         DrugStockHistory.created_date)
                                   .alias('stock_updated_time'),
                                   fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                         DrugDetails.last_seen_by).alias('last_seen_with'),
                                   fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                         DrugDetails.last_seen_date).alias('last_seen_on'),
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(TempMfdFilling, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(DrugMasterAlias, on=SlotDetails.original_drug_id == DrugMasterAlias.id)\
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientRx.patient_id == PatientMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(CodeMasterAlias, on=MfdAnalysisDetails.status_id == CodeMasterAlias.id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER, on=ContainerMasterAlias.id == LocationMaster.container_id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == MfdCanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == MfdCanisterMaster.company_id))) \
            .where(BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   BatchMaster.id == progress_batch_id,
                   MfdAnalysis.mfs_device_id == mfs_id,
                   MfdAnalysis.assigned_to == user_id)
        if not ignore_progress_condition:
            query = query.where(mfd_canister_inprogress_condition)
            # query = query.where((LocationMaster.id.is_null(True)) |(MfdAnalysis.trolley_location_id != LocationMaster.id))
        if analysis_ids:
            query = query.where(MfdAnalysis.id << analysis_ids)
        print(query)
        txr_list = []
        ndc_list = []
        for record in query:
            txr_list.append(record['txr'])
            ndc_list.append(record['ndc'])
        if txr_list:
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
        for record in query:
            if record['mfd_analysis_id'] not in canister_filling_data:
                canister_filling_data[record['mfd_analysis_id']] = {
                    'mfs_device_id': record['mfs_device_id'],
                    'mfd_analysis_id': record['mfd_analysis_id'],
                    'mfs_location_number': record['mfs_location_number'],
                    'dest_trolley_name': record['dest_trolley_name'],
                    'dest_trolley_id': record['dest_trolley_id'],
                    'patient_name': record['patient_name'],
                    'patient_id': record['patient_id'],
                    'dest_trolley_drawer_id': record['dest_trolley_drawer_id'],
                    'dest_trolley_display_location': record['dest_trolley_display_location'],
                    'dest_trolley_drawer_name': record['dest_trolley_drawer_name'],
                    'dest_trolley_drawer_serial_number': record['dest_trolley_drawer_serial_number'],
                    'mfd_canister_id': record['mfd_canister_id'],
                    'current_device_name': record['current_device_name'],
                    'current_device_id': record['current_device_id'],
                    'current_drawer_id': record['current_drawer_id'],
                    'current_display_location': record['current_display_location'],
                    'current_drawer_name': record['current_drawer_name'],
                    'batch_id': record['batch_id'],
                    'order_no': record['order_no'],
                    'dest_device_id': record['dest_device_id'],
                    'dest_quadrant': record['dest_quadrant'],
                    'canister_status_id': record['status_id'],
                    'canister_status': record['can_status'],
                    'hoa_time': record['hoa_time'],
                    'can_slot_data': dict()
                }
                can_data = get_canister_data(record, inventory_data)
                if record["drug_status_id"] == constants.MFD_DRUG_FILLED_STATUS:
                    can_data["is_filled"] = 1
                else:
                    can_data["is_filled"] = 0
                canister_filling_data[record['mfd_analysis_id']]['can_slot_data'][record['mfd_can_slot_no']] = \
                    [can_data]
            else:
                if record['mfd_can_slot_no'] not in canister_filling_data[record['mfd_analysis_id']]['can_slot_data']:
                    can_data = get_canister_data(record, inventory_data)
                    if record["drug_status_id"] == constants.MFD_DRUG_FILLED_STATUS:
                        can_data["is_filled"] = 1
                    else:
                        can_data["is_filled"] = 0
                    canister_filling_data[record['mfd_analysis_id']]['can_slot_data'][record['mfd_can_slot_no']] = \
                        [can_data]
                else:
                    can_data = get_canister_data(record, inventory_data)
                    if record["drug_status_id"] == constants.MFD_DRUG_FILLED_STATUS:
                        can_data["is_filled"] = 1
                    else:
                        can_data["is_filled"] = 0
                    canister_filling_data[record['mfd_analysis_id']]['can_slot_data'][record['mfd_can_slot_no']] \
                        .append(can_data)

        return canister_filling_data, list(set(ndc_list))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_similar_canister_analysis_ids(company_id, user_id, analysis_id, batch_id, mfs_id, analysis_ids=None):
    """
    returns canister which has same drugged and same quantity of drug in every slot of canister
    :param company_id: int
    :param user_id: int
    :param analysis_id: int
    :param batch_id: int
    :param mfs_id: int
    :return:
    """
    CodeMasterAlias = CodeMaster.alias()
    canister_slot_data = defaultdict(lambda: defaultdict(list))
    similar_canister_set = set()
    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   DrugMaster,
                                   CodeMaster.value.alias('can_status'),
                                   CodeMasterAlias.value.alias('drug_status'),
                                   DrugMaster.id.alias('drug_id'),
                                   MfdAnalysisDetails,
                                   MfdAnalysisDetails.mfd_can_slot_no, MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(CodeMasterAlias, on=MfdAnalysisDetails.status_id == CodeMasterAlias.id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   MfdAnalysis.mfs_device_id == mfs_id,
                   PackDetails.company_id == company_id,
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysis.batch_id == batch_id)
        if not analysis_ids:
            query = query.where(mfd_canister_inprogress_condition)
        else:
            query = query.where(MfdAnalysis.id << analysis_ids)
        query = query.group_by(MfdAnalysis.id,
                               MfdAnalysisDetails.mfd_can_slot_no,
                               DrugMaster.formatted_ndc, DrugMaster.txr)

        for record in query:
            canister_slot_data[record['mfd_analysis_id']][record['mfd_can_slot_no']] \
                .append('{}#{}#{}'.format(record['formatted_ndc'], record['txr'], record['quantity']))

        logger.info('canister_slot_data {}'.format(canister_slot_data))
        base_analysis_data = canister_slot_data[int(analysis_id)]
        logger.info('base_analysis_data' + str(base_analysis_data))

        for analysis_id, canister_slot_details in canister_slot_data.items():
            print(analysis_id, canister_slot_details)
            if base_analysis_data == canister_slot_details:
                print('in: ', analysis_id)
                similar_canister_set.add(analysis_id)
        logger.info('similar_canister_set {}'.format(similar_canister_set))
        return similar_canister_set
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_trolley_first_pack(user_id, analysis_ids, batch_id):
    """
    returns first pack in which the mfd canister is required and the device from which it is to be filled
    :param user_id: int
    :param analysis_ids: list
    :param batch_id: int
    :return: tuple
    """
    order_no = None
    dest_robot_id = None
    try:
        query = MfdAnalysis.select(PackRxLink.pack_id, PackDetails.order_no, MfdAnalysis.dest_device_id).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.id << analysis_ids,
                   MfdAnalysis.assigned_to == user_id,
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)) \
            .group_by(MfdAnalysis.batch_id).having(fn.MIN(PackDetails.order_no))
        for record in query:
            order_no = record['order_no']
            dest_robot_id = record['dest_device_id']
        return order_no, dest_robot_id
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_similar_drawer_analysis_ids(company_id, user_id, drawer_ids, batch_id, mfs_id, mfd_analysis_ids,
                                    mfs_location_number):
    """
    returns analysis_ids having same drawer id
    @param company_id:
    @param user_id:
    @param drawer_ids:
    @param batch_id:
    @param mfs_id:
    @param mfd_analysis_ids:
    @param mfs_location_number:
    @return:
    """
    canister_filling_data = dict()
    CodeMasterAlias = CodeMaster.alias()
    canister_slot_data = defaultdict(lambda: defaultdict(list))
    similar_drawer_set = set()
    LocationMasterAlias = LocationMaster.alias()
    if not mfd_analysis_ids:
        return similar_drawer_set
    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   DrugMaster,
                                   CodeMaster.value.alias('can_status'),
                                   CodeMasterAlias.value.alias('drug_status'),
                                   DrugMaster.id.alias('drug_id'),
                                   MfdAnalysisDetails,
                                   MfdAnalysisDetails.mfd_can_slot_no, MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(CodeMasterAlias, on=MfdAnalysisDetails.status_id == CodeMasterAlias.id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   MfdAnalysis.mfs_device_id == mfs_id,
                   LocationMasterAlias.container_id << drawer_ids,
                   PackDetails.company_id == company_id,
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.id << mfd_analysis_ids,
                   MfdAnalysis.mfs_location_number << mfs_location_number)
        for record in query:
            similar_drawer_set.add(record['analysis_id'])
        logger.info(similar_drawer_set)
        return similar_drawer_set
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_get_mfd_slot_info(pack_id, device_id, company_id, original_drop_data, missing_canisters):
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
                        'location_disabled': record['location_disabled']
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
        print(drop_data)
        missing_canisters.update(missing_mfd_canister)
        logger.info("Response mfd_slot_data {}, mfd_dop_data {}, missing_canisters {}".format(mfd_slot_data,
                                                                                              drop_data,
                                                                                              missing_canisters))
        return {'mfd_slot_data': mfd_slot_data, 'mfd_dop_data': drop_data, 'missing_canisters': missing_canisters}
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_first_trolley_id(progress_batch_id, user_id, device_id, trolley_seq = None):
    """
    returns trolley data which to be currently filled by user
    :param progress_batch_id:
    :param user_id:
    :param device_id:
    :return:
    """
    DeviceMasterAlias = DeviceMaster.alias()

    clauses = list()
    clauses.append((BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST)))
    clauses.append((BatchMaster.mfd_status != constants.MFD_BATCH_FILLED))
    clauses.append((MfdAnalysis.assigned_to == user_id))
    clauses.append((MfdAnalysis.mfs_device_id == device_id))
    clauses.append((MfdAnalysis.batch_id == progress_batch_id))
    clauses.append((MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS))

    if trolley_seq:
        clauses.append((MfdAnalysis.trolley_seq == trolley_seq))
    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.trolley_seq,
                                   DeviceMaster.id.alias('trolley_id'),
                                   DeviceMaster.serial_number.alias('trolley_serial_number'),
                                   DeviceMaster.name.alias('trolley_name'),
                                   DeviceMasterAlias.name.alias('mfs_device_name'),
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == MfdAnalysis.mfs_device_id) \
            .where(*clauses) \
            .order_by(MfdAnalysis.order_no) \
            .get()
        trolley_data = {
            'trolley_id': query['trolley_id'],
            'trolley_seq': query['trolley_seq'],
            'name': query['trolley_name'],
            'mfs_device_name': query['mfs_device_name'],
            'trolley_serial_number': query['trolley_serial_number']
        }
        delivery_date = get_delivery_date_of_mfd_trolley(user_id=user_id, batch_id=progress_batch_id, mfs_id=device_id,
                                                         trolley_id_list=[trolley_data['trolley_id']])
        # couchdb will allow only str data type >> need to convert "delivery_date_from" and "delivery_date_to" to str.
        trolley_data["delivery_date_from"] = str(delivery_date[trolley_data["trolley_seq"]]["delivery_date_from"])
        trolley_data["delivery_date_to"] = str(delivery_date[trolley_data["trolley_seq"]]["delivery_date_to"])

        return trolley_data
    except DoesNotExist as e:
        logger.info("No trolley found for user.")
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_check_mfd_exists_for_batch_and_template(batch_id: int, template_id: int):
    try:
        query = TemplateMaster.select(MfdAnalysisDetails).dicts()\
            .join(TemplateDetails, on=TemplateMaster.patient_id == TemplateDetails.patient_id)\
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id)))\
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
            .join(PackRxLink, on=((PackDetails.id == PackRxLink.pack_id) &
                                  (TemplateDetails.patient_rx_id == PackRxLink.patient_rx_id)))\
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(MfdAnalysisDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .where(TemplateMaster.id == template_id)

        if query.count() > 0:
            return True

        return False
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_check_mfd_analysis_by_batch_dao(batch_id: int, old_template_id: int, new_template_id: int) -> bool:
    mfd_recommendation_check: bool = False
    try:
        mfd_recommendation_check = MfdAnalysis.db_check_mfd_analysis_by_batch(batch_id)

        if mfd_recommendation_check:
            logger.debug("MFD Recommendation has been executed for Batch ID: {}".format(batch_id))

            logger.debug("Check the template split between Old and New Templates for MFD drugs...")

            # logger.debug("Check MFD Analysis status to determine if MFD action is already taken...")
            # mfd_analysis_fill_status = db_check_mfd_analysis_status(batch_id, old_template_id)
            # if mfd_analysis_fill_status:
            #     mfd_recommendation_check = True

        return mfd_recommendation_check
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def concatenate_fndc_txr_dao(fndc, txr):
    return fndc + settings.SEPARATOR + txr


@log_args_and_response
def db_prepare_mfd_drug_template_column_unique_data(column_number, hoa_time, quantity, fndc, txr):
    return str(column_number) + \
           settings.SEPARATOR + str(hoa_time) + \
           settings.SEPARATOR + str(round(quantity, 1)) + \
           settings.SEPARATOR + concatenate_fndc_txr_dao(fndc, txr)


@log_args_and_response
def db_get_mfd_drugs_template_combination(patient_id: int, file_id: int):
    # mfd_drug_dict: Dict[Any, Any] = defaultdict(set)
    mfd_drug_dict: Dict[Any, Any] = {}
    data_set = set()
    final_data_set = set()
    mfd_in_progress_list = [constants.MFD_CANISTER_IN_PROGRESS_STATUS, constants.MFD_CANISTER_FILLED_STATUS]
    try:
        query = TemplateMaster.select(TemplateDetails.patient_id, TemplateDetails.column_number,
                                      TemplateDetails.hoa_time, TemplateDetails.quantity, TemplateDetails.patient_rx_id,
                                      DrugMaster.id.alias("drug_id"),
                                      DrugMaster.formatted_ndc.alias("fndc"), DrugMaster.txr,
                                      fn.SUM(fn.IF(MfdAnalysis.status_id.in_(mfd_in_progress_list), 1, 0))
                                      .alias("mfd_fill_status")).dicts()\
            .join(TemplateDetails, on=TemplateMaster.patient_id == TemplateDetails.patient_id)\
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id)))\
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
            .join(PackRxLink, on=((PackDetails.id == PackRxLink.pack_id) &
                                  (TemplateDetails.patient_rx_id == PackRxLink.patient_rx_id)))\
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(MfdAnalysisDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .where(TemplateMaster.patient_id == patient_id, TemplateMaster.file_id == file_id)\
            .group_by(TemplateDetails.patient_id, TemplateDetails.patient_rx_id, TemplateDetails.column_number,
                      TemplateDetails.hoa_time, TemplateDetails.quantity)\
            .order_by(TemplateDetails.column_number, TemplateDetails.hoa_time, TemplateDetails.patient_rx_id)

        logger.debug("db_get_mfd_drugs_template_combination -- Query: {}".format(query))
        for record in query:
            data_set.clear()
            if record["fndc"] and record["txr"]:
                if record["drug_id"] in mfd_drug_dict.keys():
                    data_set = mfd_drug_dict[record["drug_id"]]["data"]
                    data_set.add(db_prepare_mfd_drug_template_column_unique_data(record["column_number"],
                                                                                 record["hoa_time"],
                                                                                 record["quantity"], record["fndc"],
                                                                                 record["txr"]))
                    final_data_set = deepcopy(data_set)
                    mfd_drug_dict[record["drug_id"]]["data"] = final_data_set
                else:
                    data_set.add(db_prepare_mfd_drug_template_column_unique_data(record["column_number"],
                                                                                 record["hoa_time"],
                                                                                 record["quantity"], record["fndc"],
                                                                                 record["txr"]))
                    final_data_set = deepcopy(data_set)
                    fndc_dict = {
                        "fndc_txr": concatenate_fndc_txr_dao(record["fndc"], record["txr"]),
                        "data": final_data_set,
                        "mfd_fill_status": True if record["mfd_fill_status"] > 0 else False
                    }
                    mfd_drug_dict[record["drug_id"]] = fndc_dict

        return mfd_drug_dict
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_trolley_pending_analysis_ids(batch_id, trolley_id, user_id=None):
    """
    returns analysis_ids for user's upcoming trolley
    :param batch_id: int
    :param trolley_id: int
    :param user_id: int
    :return: list
    """
    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   DeviceMaster.id.alias('trolley_id'),
                                   DeviceMaster.name.alias('trolley_name'),
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   MfdAnalysis.batch_id == batch_id,
                   DeviceMaster.id == trolley_id,
                   MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS) \
            .order_by(MfdAnalysis.order_no) \
            .limit(160)
        analysis_id_list = list()

        if user_id:
            query = query.where(MfdAnalysis.assigned_to == user_id)
        for record in query:
            print(record)
            if trolley_id == record['trolley_id']:
                analysis_id_list.append(record['mfd_analysis_id'])
            else:
                break
        return analysis_id_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_patient_info(analysis_ids):
    """
    returns patient's canister data based on hoa and order number of patient
    :param analysis_ids: list
    :return: tuple
    """
    patient_hoa_dict = defaultdict(lambda: defaultdict(list))
    patient_order_no = defaultdict(list)
    min_order_no = dict()
    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis,
                                   MfdAnalysis.order_no,
                                   SlotHeader.hoa_date,
                                   SlotHeader.hoa_time,
                                   PatientRx.patient_id).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(MfdAnalysis.id << analysis_ids) \
            .group_by(MfdAnalysis.id) \
            .order_by(MfdAnalysis.order_no)

        for record in query:
            patient_hoa_dict[record['patient_id']][record['hoa_time']].append(record['mfd_analysis_id'])
            patient_order_no[record['patient_id']].append(record['order_no'])

        logger.info("Inside db_get_patient_info patient_hoa_dict {}, patient_order_no {}."
                    .format(patient_hoa_dict, patient_order_no))
        for patient, order_no_list in patient_order_no.items():
            min_order_no[patient] = min(order_no_list)
        return patient_hoa_dict, min_order_no
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_get_location_info(mfs_id, device_max_location):
    """
    returns pairs in which same patient's hoa canister is to be placed
    :param mfs_id: int
    :param device_max_location: max active location
    :return:
    """
    return settings.standard_mfs_location
    try:
        query = LocationMaster.select(LocationMaster.location_number).dicts() \
            .join(DisabledCanisterLocation, JOIN_LEFT_OUTER, on=DisabledCanisterLocation.loc_id == LocationMaster.id) \
            .where(LocationMaster.device_id == mfs_id,
                   DisabledCanisterLocation.id.is_null(True))

        active_location = [record['location_number'] for record in query]

        if len(active_location) == device_max_location:
            return settings.standard_mfs_location
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_analysis_sorted_list(company_id, user_id, batch_id, mfs_id, analysis_ids):
    """
    returns pairs in which same patient's hoa canister is to be placed
    @param company_id:
    @param user_id:
    @param batch_id:
    @param mfs_id:
    @param analysis_ids:
    @return:
    """
    sorted_analysis_id_list = list()
    try:
        for analysis_id in analysis_ids:
            if analysis_id not in sorted_analysis_id_list:
                sorted_analysis_ids = get_similar_canister_analysis_ids(company_id, user_id, analysis_id, batch_id,
                                                                        mfs_id, analysis_ids)
                sorted_analysis_id_list.extend(sorted_analysis_ids)
            if len(sorted_analysis_id_list) == len(analysis_ids):
                return sorted_analysis_id_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def map_mfs_location(patient_hoa_dict, patient_order_no, location_mapping, company_id, user_id, batch_id, mfs_id):
    """
    maps mfs location to mfs_analysis_id
    @param patient_hoa_dict:
    @param patient_order_no:
    @param location_mapping:
    @param company_id:
    @param user_id:
    @param batch_id:
    @param mfs_id:
    @return:
    """
    """
    based on available pattern in which patient's same hoa canister are to be placed and patient's canister having same 
    hoa time canister is mapped with mfs's particular location
    """
    analysis_id_list = list()
    location_number_list = list()
    current_location_mapping = deepcopy(location_mapping)
    try:
        for patient_id, order_no in sorted(patient_order_no.items(), key=lambda item: item[1]):
            patient_hoa_info = patient_hoa_dict[patient_id]
            for hoa_time, analysis_ids in patient_hoa_info.items():
                print(analysis_ids)
                print(current_location_mapping)
                if not len(analysis_ids) <= len(current_location_mapping) * 2:
                    analysis_ids = analysis_ids[: int(len(current_location_mapping) * 2)]

                if current_location_mapping:
                    if len(analysis_ids) % 2 == 0:
                        location_required = int(len(analysis_ids) / 2)
                        locations = current_location_mapping[:location_required]
                        current_location_mapping = current_location_mapping[location_required:]
                        for location in locations:
                            location_number_list.extend(location)
                        analysis_ids = db_get_analysis_sorted_list(company_id, user_id, batch_id, mfs_id,
                                                                   analysis_ids)
                        analysis_id_list.extend(analysis_ids)
                    else:
                        location_required = int((len(analysis_ids) + 1) / 2)
                        locations = current_location_mapping[:location_required]
                        current_location_mapping = current_location_mapping[location_required:]
                        if int(len(locations)) == 1:
                            location_number_list.append(locations[len(locations) - 1][0])
                        else:
                            for i in range(0, len(locations) - 1):
                                location_number_list.extend(locations[i])
                            location_number_list.append(locations[len(locations) - 1][0])
                        analysis_ids = db_get_analysis_sorted_list(company_id, user_id, batch_id, mfs_id,
                                                                   analysis_ids)
                        analysis_id_list.extend(analysis_ids)

        return analysis_id_list, location_number_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def update_in_progress_canister(analysis_id_list, location_number_list, user_id):
    """
    updates canister's status to in progress and updates mfs_location_number in mfd_analysis table
    :param analysis_id_list: list
    :param location_number_list: list
    :param user_id: int
    :return:
    """
    try:
        db_update_canister_status(analysis_id_list, constants.MFD_CANISTER_IN_PROGRESS_STATUS, user_id)
        MfdAnalysis.db_update_mfs_location(analysis_id_list, location_number_list)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_current_mfs_batch_data(mfs_id: int) -> tuple:
    """
    returns current placement information of particular mfs
    :param mfs_id:
    :return:
    """
    logger.info('in_get_current_mfs_batch_data_for_mfs_id: {}'.format(mfs_id))
    location_analysis_dict = dict()
    LocationMasterAlias = LocationMaster.alias()
    LocationMasterAlias2 = LocationMaster.alias()

    required_canister_location_dict = dict()
    ContainerMasterAlias = ContainerMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    DeviceMasterAlias2 = DeviceMaster.alias()

    try:
        batch_id = None
        query = MfdAnalysis.select(LocationMasterAlias.container_id.alias('drawer_id'),
                                   MfdAnalysis,
                                   ContainerMaster.drawer_name,
                                   ContainerMasterAlias.drawer_name.alias('trolley_drawer_name'),
                                   DeviceMasterAlias.name.alias('trolley_name'),
                                   LocationMasterAlias2.display_location.alias('mfs_display_location'),
                                   LocationMaster.id.alias('current_location_id'),
                                   fn.GROUP_CONCAT(MfdAnalysisDetails.status_id).coerce(False).alias('drug_status'),
                                   TempMfdFilling.transfer_done,
                                   MfdAnalysis.id.alias('mfd_analysis_id'),
                                   LocationMasterAlias.device_id.alias('trolley_id'),
                                   BatchMaster.system_id).dicts() \
            .join(TempMfdFilling, on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(LocationMasterAlias, on=MfdAnalysis.trolley_location_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == ContainerMasterAlias.device_id) \
            .join(LocationMasterAlias2, on=((MfdAnalysis.mfs_device_id == LocationMasterAlias2.device_id) &
                                            (MfdAnalysis.mfs_location_number == LocationMasterAlias2.location_number))) \
            .join(DeviceMasterAlias2, on=DeviceMasterAlias2.id == LocationMasterAlias2.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias2.container_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=((MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) &
                                                          (MfdCanisterMaster.location_id !=
                                                           MfdAnalysis.trolley_location_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(MfdAnalysis.mfs_device_id == mfs_id) \
            .group_by(MfdAnalysisDetails.analysis_id)

        logger.info('callback_current_data_query: {}'.format(query))
        for record in query:
            if not batch_id:
                batch_id = record['batch_id']
                user_id = record['assigned_to']
            drawer_initial = record['drawer_name'].split('-')
            loc_number = record['mfs_display_location'].split('-')
            if record['transfer_done']:
                display_location = record['trolley_drawer_name']
                dest_device = record['trolley_name']
            else:
                display_location = '{}{}'.format(drawer_initial[0], loc_number[1])
            required_canister_location_dict[record['mfd_canister_id']] = {
                'display_location': display_location
            }
            location_analysis_dict[str(record['mfs_location_number'])] = {
                'analysis_id': record['mfd_analysis_id'],
                'canister_id': record['mfd_canister_id'],
                'status': record['status_id'],
                'trolley_location_id': record['trolley_location_id'],
                'canister_current_location': record['current_location_id'],
                'drawer_id': record['drawer_id'],
                'batch_id': record['batch_id'],
                'drug_status': record['drug_status'],
                'dest_quadrant': record['dest_quadrant'],
                'transfer_done': record['transfer_done'],
                'system_id': record['system_id'],
                'trolley_id': record['trolley_id'],
                'dest_device_id': record['dest_device_id'],
                'mfs_location': '{}{}'.format(drawer_initial[0], loc_number[1])
            }
        logger.info('returning_data_for_callback_current_data for batch_id: {} location_data: {} '
                     'display_location_info: {}'.format(batch_id, location_analysis_dict,
                                                        required_canister_location_dict))
        return batch_id, location_analysis_dict, required_canister_location_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def associate_canister_with_analysis(analysis_canister_dict):
    """
    updates canister_id in mfd_analysis based on callback
    :param analysis_canister_dict:
    :return:
    """
    analysis_ids = list(analysis_canister_dict.keys())
    canister_ids = list(analysis_canister_dict.values())

    try:
        status = MfdAnalysis.db_update_canister_id(analysis_ids, canister_ids)
        return status
    except (InternalError, IntegrityError) as e:
        raise e


@log_args_and_response
def db_get_pending_canister_count(batch_id, user_id=None, trolley_id=None):
    """
    returns count of canisters on which actions are required weather filling pending or if filled/skipped needs to be put
    in trolley
    :param batch_id: int
    :param user_id: int
    :param trolley_id: int
    :return: int
    """
    LocationMasterAlias = LocationMaster.alias()
    try:
        pending_count = MfdAnalysis.select().dicts() \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMasterAlias.id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(MfdAnalysis.batch_id == batch_id)
        if user_id:
            pending_count = pending_count.where(MfdAnalysis.assigned_to == user_id)
        if trolley_id:
            pending_count = pending_count.where(LocationMasterAlias.device_id == trolley_id)
        pending_count = pending_count.where(mfd_canister_pending_and_inprogress_condition).count()
        return pending_count
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_user_pending_canister_count(batch_id, user_id, mfs_id):
    """
    returns count of canisters currently placed on mfs
    in trolley
    @param batch_id:
    @param user_id:
    @param mfs_id:
    @return:
    """
    try:
        in_progress_canister_query = MfdAnalysis.select().dicts() \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=((MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) &
                                                          (MfdCanisterMaster.location_id !=
                                                           MfdAnalysis.trolley_location_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysis.mfs_device_id == mfs_id)
        in_progress_canister_query = in_progress_canister_query.where(mfd_canister_inprogress_condition)
        in_progress_count = in_progress_canister_query.count()
        return in_progress_count
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_batch_data(batch_id):
    """
    returns batch data for a particular batch_id
    :param batch_id: int
    :return: object
    """
    try:
        batch_data = BatchMaster.db_get(batch_id)
        return batch_data
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


def get_pack_id_query(min_order_no, batch_id):
    """
    returns packs of batch having order no greater than min_order_no
    :param min_order_no: int
    :param batch_id: int
    :return: object
    """
    try:
        query = PackDetails.select(PackDetails.id).dicts() \
            .where(PackDetails.order_no > min_order_no,
                   PackDetails.batch_id == batch_id)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def location_mfd_can_info(device_id, display_locations):
    """
    disables particular location
    :param device_id: int
    :param display_locations: list
    :return: tuple
    """
    try:
        loc_info = LocationMaster.select(LocationMaster.id.alias('loc_id'),
                                         MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         LocationMaster,
                                         MfdAnalysis.dest_quadrant,
                                         MfdAnalysis.dest_device_id,
                                         MfdCanisterMaster).dicts() \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .where(LocationMaster.device_id == device_id,
                   LocationMaster.display_location << display_locations)

        return loc_info
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_nearest_location(location_list, disable_location_id):
    """
    returns nearest location from disable_location_id
    :param location_list: list
    :param disable_location_id: int
    :return: int
    """
    location_difference_list = list(map(lambda x: abs(x - disable_location_id), location_list))
    return location_difference_list.index(min(location_difference_list))


def get_empty_location(device_id, quadrant, disabled_location_id, exclude_locations):
    """
    returns mfd drawer's empty location for given device and quadrant
    @param device_id:
    @param quadrant:
    @param disabled_location_id:
    @param exclude_locations:
    @return:
    """
    location_info = dict()
    location_id_list = list()
    try:
        query = LocationMaster.select(LocationMaster).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(ContainerMaster.drawer_type == settings.SIZE_OR_TYPE['MFD'],
                   LocationMaster.device_id == device_id,
                   LocationMaster.quadrant == quadrant,
                   LocationMaster.is_disabled == settings.is_location_active,
                   MfdCanisterMaster.id.is_null(True))
        if exclude_locations:
            query = query.where(LocationMaster.display_location.not_in(exclude_locations))
        for record in query:
            location_info[record['id']] = {
                'display_location': record['display_location'],
                'location_id': record['id']
            }
            location_id_list.append(record['id'])
        if not location_id_list:
            logger.info('No empty location found while disabling:' + str(disabled_location_id))
            return None
        nearest_loc = get_nearest_location(location_id_list, disabled_location_id)
        print(query)
        # query = query.get()
        return location_info[location_id_list[nearest_loc]]
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_empty_canister(device_id, quadrant, disabled_location_id, exclude_locations):
    """
    returns empty mfd canister data which is currently placed in a particular quadrant of a device
    :param device_id: int
    :param quadrant: int
    :param disabled_location_id: int
    :return: dict
    """
    location_info = dict()
    location_id_list = list()
    try:
        MfdAnalysisAlias = MfdAnalysis.alias()

        query = MfdCanisterMaster.select(MfdAnalysisAlias.mfd_canister_id,
                                         LocationMaster.id,
                                         LocationMaster.display_location).dicts() \
            .join(LocationMaster, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysisAlias, on=MfdAnalysisAlias.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .where(LocationMaster.device_id == device_id,
                   LocationMaster.is_disabled == settings.is_location_active,
                   MfdAnalysisAlias.status_id << [constants.MFD_CANISTER_DROPPED_STATUS,
                                                  constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                  constants.MFD_CANISTER_SKIPPED_STATUS],
                   LocationMaster.quadrant == quadrant)
        if exclude_locations:
            query = query.where(LocationMaster.display_location.not_in(exclude_locations))
        for record in query:
            location_info[record['id']] = {'display_location': record['display_location'],
                                           'canister_id': record['mfd_canister_id'],
                                           'location_id': record['id']}
            location_id_list.append(record['id'])
        if not location_id_list:
            logger.info('No empty canister found while disabling:' + str(disabled_location_id))
            return None
        nearest_loc = get_nearest_location(location_id_list, disabled_location_id)
        return location_info[location_id_list[nearest_loc]]
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_last_canister(device_id, quadrant, disabled_location_id, exclude_locations):
    """
    returns canister data which is last in queue for dropping
    :param device_id: int
    :param quadrant: int
    :param disabled_location_id: int
    :return: dict
    """
    location_info = dict()
    # location_id_list = list()
    try:
        MfdAnalysisAlias = MfdAnalysis.alias()
        query = LocationMaster.select(MfdAnalysisAlias.mfd_canister_id,
                                      LocationMaster.display_location,
                                      LocationMaster.id,
                                      fn.MAX(MfdAnalysisDetails.mfd_can_slot_no).alias('max_slot_number')).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysisAlias, on=MfdAnalysisAlias.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysisAlias.id) \
            .where(ContainerMaster.drawer_type == settings.SIZE_OR_TYPE['MFD'],
                   LocationMaster.device_id == device_id,
                   LocationMaster.quadrant == quadrant,
                   MfdAnalysisAlias.status_id << constants.MFD_CANISTER_DONE_LIST,
                   LocationMaster.is_disabled == settings.is_location_active)
        if exclude_locations:
            query = query.where(LocationMaster.id.not_in(exclude_locations))
        query = query.group_by(MfdAnalysisAlias.id) \
            .order_by(MfdAnalysisAlias.order_no.desc()).limit(1)
        for record in query:
            location_info = {'location_id': record['id'],
                             'display_location': record['display_location'],
                             'canister_id': record['mfd_canister_id'],
                             'max_slot_number': record['max_slot_number']}
        if not location_info:
            logger.info('No pending canister found while disabling:' + str(disabled_location_id))
            return None
        return location_info
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_transfer_data(device_id, display_location, canister_data, disabled_location_id, exclude_locations):
    """
    returns transfer data for a particular canister
    @param device_id:
    @param display_location:
    @param canister_data:
    @param disabled_location_id:
    @param exclude_locations:
    @return:
    """
    """
    Returns transfer data for given canister based on three criteria:
    1. If empty mfd location is found then returns transfer data to that location
    2. If not empty mfd location then checks if any mfd canister is currently empty(dropping done)
    3. If not any above mentioned scenario then ask user to skip the canister and use the same at mvs

    """
    try:
        if canister_data:
            # get the quadrant of a particular location
            quadrant = canister_data['dest_quadrant']
            logger.info('quadrant_found: ' + str(quadrant))
            # check if any empty location is empty
            empty_location = get_empty_location(device_id, quadrant, disabled_location_id, exclude_locations)
            if empty_location:
                transfer_data = {
                    'current_canister_id': canister_data['mfd_canister_id'],
                    'current_canister_rfid': canister_data['rfid'],
                    'current_display_location': display_location,
                    'device_id': device_id,
                    'new_canister_id': None,
                    'new_display_location': empty_location['display_location'],
                    'new_loc_id': empty_location['location_id'],
                    'skip_required': False,
                }
                return transfer_data
            # get empty canister
            empty_canister_data = get_empty_canister(device_id, quadrant, disabled_location_id, exclude_locations)
            if empty_canister_data:
                transfer_data = {
                    'current_canister_id': canister_data['mfd_canister_id'],
                    'current_canister_rfid': canister_data['rfid'],
                    'current_display_location': display_location,
                    'device_id': device_id,
                    'new_canister_id': empty_canister_data['canister_id'],
                    'new_display_location': empty_canister_data['display_location'],
                    'new_loc_id': empty_canister_data['location_id'],
                    'skip_required': False,
                }
                return transfer_data
            # get the canister data which is to be used in last
            # last_use_canister_data = get_last_canister(device_id, quadrant, disabled_location_id, exclude_locations)
            # if last_use_canister_data:
            #     transfer_data = {
            #         'current_canister_id': canister_data.id,
            #         'current_canister_rfid': canister_data.rfid,
            #         'current_display_location': display_location,
            #         'device_id': device_id,
            #         'new_canister_id': last_use_canister_data['canister_id'],
            #         'new_display_location': last_use_canister_data['display_location'],
            #         'new_loc_id': last_use_canister_data['location_id'],
            #         'reswap_required': True,
            #         'current_canister_max_slot': last_use_canister_data['max_slot_number']
            #     }
            #     return transfer_data
            return {'skip_required': True}
    except NoLocationExists as e:
        logger.info("In get_transfer_data: {}".format(e))
        raise ValueError('Invalid location.')
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_unique_mfd_drop(clauses):
    """
    returns unique drops per pack for counting the time required by robot to fill the packs.
    @param clauses: list
    :return: object
    """
    logger.info("")
    query = MfdAnalysis.select(fn.CONCAT(SlotHeader.pack_id, '#', MfdAnalysisDetails.drop_number)
                               .coerce(False).alias('pack_drop'),
                               SlotHeader.pack_id).dicts() \
        .join(MfdAnalysisDetails, on=(MfdAnalysisDetails.analysis_id == MfdAnalysis.id)) \
        .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
        .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
        .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
        .where(functools.reduce(operator.and_, clauses))
    query = query.group_by(SlotHeader.pack_id, MfdAnalysisDetails.drop_number)
    return query


@log_args_and_response
def db_get_batch_mfd_packs(batch_id):
    """
    Function to get list mfd packs for given batch
    @param batch_id:
    @return: list
        Sample Output = ['mfd_pack':1, 'mfd_pack':2]
    """
    try:
        mfd_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        query = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id)).alias('mfd_pack'),
                                   BatchMaster.system_id,
                                   fn.DATE(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   MfdAnalysis.status_id << mfd_canister_status) \
            .group_by(PackRxLink.pack_id) \
            .order_by(fn.MIN(MfdAnalysis.order_no), fn.MIN(MfdAnalysisDetails.mfd_can_slot_no))

        return list(query)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return None


@log_args_and_response
def db_get_mfd_packs_from_packlist(pack_list):
    """
    Function to get list mfd packs for given batch
    @param pack_list:
    @return: list
        Sample Output = ['mfd_pack':1, 'mfd_pack':2]
    """
    try:
        mfd_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        if pack_list:
            query = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id)).alias('mfd_pack')).dicts() \
                .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                .where(PackDetails.id << pack_list,
                       PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                       MfdAnalysis.status_id << mfd_canister_status) \
                .group_by(PackRxLink.pack_id) \
                .order_by(PackDetails.order_no)

            return list(query)

        else:
            return None

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return None


def get_device_quadrant_from_location_id(location_id: int) -> tuple:
    """
    Function to get device_id and quadrant from location_id
    @param location_id:
    @return:
    """
    try:
        logger.info("Location {}".format(location_id))
        query = LocationMaster.select(LocationMaster.device_id,
                                      LocationMaster.quadrant).dicts() \
            .where(LocationMaster.id == location_id)

        for record in query:
            return record['device_id'], record['quadrant']

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist:
        return None, None


@log_args_and_response
def get_empty_location_by_drawer(container_id, exclude_location):
    """
    Function to get empty location by drawer
    @param container_id: int
    @param exclude_location:
    @return:
    """
    try:
        logger.info("input get_empty_location_by_drawer {}".format(container_id))
        query = LocationMaster.select(LocationMaster.id).dicts() \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(MfdCanisterMaster.id.is_null(True), LocationMaster.container_id == container_id,
                   LocationMaster.is_disabled == False)
        if exclude_location:
            query = query.where(LocationMaster.id.not_in(exclude_location))

        for record in query:
            return record['id']

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist:
        return None


@log_args_and_response
def get_empty_location_by_trolley(trolley_id, exclude_location):
    """
    Function to get empty location by drawer
    @param trolley_id: int
    @param exclude_location:
    @return:
    """
    try:
        logger.info("input get_empty_location_by_trolley {}".format(trolley_id))
        query = LocationMaster.select(LocationMaster.id).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(MfdCanisterMaster.id.is_null(True),
                   ContainerMaster.device_id == trolley_id,
                   LocationMaster.is_disabled == False,
                   ContainerMaster.drawer_level << constants.MFD_TROLLEY_EMPTY_DRAWER_LEVEL)
        if exclude_location:
            query = query.where(LocationMaster.id.not_in(exclude_location))

        for record in query:
            return record['id']

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist:
        return None


@log_args_and_response
def get_filled_drug(mfd_analysis_details_ids, status_list):
    """
    function to get filtered mfd_analysis_details_ids based on status
    :param mfd_analysis_details_ids: list
    :param status_list: list
    :return:
    """
    try:
        filled_drugs = MfdAnalysisDetails.db_get_status_based_drug(mfd_analysis_details_ids, status_list)
        return filled_drugs
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def db_get_non_rts_analysis_ids(analysis_ids):
    """
    returns the analysis_ids which has filled or pending drug
    :param analysis_ids:
    :return:
    """
    # todo: remove this as not in use
    not_skipped_analysis_ids = set()
    analysis_ids_list = list(analysis_ids)
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << analysis_ids_list,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_PENDING_STATUS,
                                                    constants.MFD_DRUG_FILLED_STATUS])
        for record in query:
            not_skipped_analysis_ids.add(record['analysis_id'])
        return not_skipped_analysis_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def current_mfs_canisters(analysis_ids: list) -> dict:
    """

    :param analysis_ids:
    :return:
    """
    try:
        system_analysis_loc_dict = dict()
        DeviceMasterAlias = DeviceMaster.alias()
        current_mfs_canisters = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                                   MfdAnalysis.mfs_device_id,
                                                   MfdAnalysis.mfs_location_number,
                                                   DeviceMasterAlias.system_id).dicts() \
            .join(DeviceMasterAlias, on=MfdAnalysis.mfs_device_id == DeviceMasterAlias.id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .where(MfdAnalysis.id << analysis_ids,
                   MfdCanisterMaster.id.is_null(True),
                   mfd_canister_inprogress_condition)
        for record in current_mfs_canisters:
            system_analysis_loc_dict[record['mfd_analysis_id']] = {
                'system_id': record['system_id'],
                'mfs_location_number': record['mfs_location_number'],
                'mfs_device_id': record['mfs_device_id']
            }
        logger.info(f"In current_mfs_canisters, system_analysis_loc_dict:{system_analysis_loc_dict}")
        return system_analysis_loc_dict
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


def mfd_transfer_notification_for_batch(batch_id: int = None, device_id: int = None) -> dict:
    """
    To notify when there are pending transfers for a particular batch
    @param batch_id:
    @param device_id:
    @return:
    """
    try:

            # trolley_id = None
        trolley_analysis_id_list = []
        analysis_id = MfdAnalysis.select(MfdAnalysis.id.alias("analysis_id"),
                                         LocationMaster.device_id.alias("trolley_device_id")).dicts() \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(MfdAnalysis.dest_device_id == device_id,
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS) \
            .order_by(MfdAnalysis.order_no)
        logger.info("analysis_id_query: {}".format(analysis_id))
        for record in analysis_id:
            trolley_id = record["trolley_device_id"]
            trolley_analysis_id_list.append(record["analysis_id"])
            if trolley_id != record["trolley_device_id"]:
                break
        logger.info("trolley_analysis_id_list:{}".format(trolley_analysis_id_list))
        DeviceMasterAlias = DeviceMaster.alias()
        query = MfdAnalysis.select(MfdAnalysis.status_id,
                                   MfdAnalysis.trolley_location_id,
                                   MfdAnalysis.dest_device_id,
                                   LocationMaster.device_id,
                                   MfdAnalysis.dest_quadrant,
                                   LocationMaster.quadrant,
                                   DeviceMaster.device_type_id,
                                   MfdAnalysis.mfs_device_id,
                                   DeviceMasterAlias.system_id.alias('mfs_system_id'),
                                   LocationMaster.device_id.alias('current_device_id'),
                                   MfdCanisterMaster.location_id.alias('current_location_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == MfdAnalysis.mfs_device_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(MfdAnalysis.id << trolley_analysis_id_list,
                   MfdAnalysis.dest_device_id == device_id) \
            .group_by(MfdAnalysis.id)
        logger.info("validate_query_for_batch:{}".format(query))
        return query

        # if pack_id:
        #
        #     validate_query_for_pack = MfdAnalysis.select(MfdAnalysis.id.alias('analysis_id')).dicts()\
        #                                 .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)\
        #                                 .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)\
        #                                 .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id)\
        #                                 .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id)\
        #                                 .join(MfdCanisterMaster, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
        #                                 .join(LocationMaster, on=MfdCanisterMaster.location_id == LocationMaster.id)\
        #                                 .where(PackDetails.id == pack_id)
        #     logger.info(validate_query_for_pack)
        #     return validate_query_for_pack

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_current_mfs_transfer_count(mfs_id: int) -> list:
    """
    returns drawer wise pending transfer count.
    @param mfs_id: int
    :return:
    """
    drawer_list = list()

    pending_drawer_query = TempMfdFilling.select(LocationMaster.container_id).dicts() \
        .join(MfdAnalysis, on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id) \
        .join(LocationMaster, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
        .where(TempMfdFilling.mfs_device_id == mfs_id,
               TempMfdFilling.transfer_done == False) \
        .group_by(LocationMaster.container_id)
    pending_drawers = list()
    for drawer in pending_drawer_query:
        pending_drawers.append(drawer['container_id'])

    if not pending_drawers:
        return drawer_list

    LocationMasterAlias = LocationMaster.alias()
    try:
        query = MfdAnalysis.select(LocationMasterAlias.container_id,
                                   LocationMaster.id.alias('current_location_id'),
                                   MfdAnalysis.id.alias('mfd_analysis_id')).dicts() \
            .join(TempMfdFilling, on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id) \
            .join(LocationMasterAlias, on=MfdAnalysis.trolley_location_id == LocationMasterAlias.id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id)
        query = query.where(MfdAnalysis.mfs_device_id == mfs_id,
                            LocationMasterAlias.container_id << pending_drawers,
                            ((MfdCanisterMaster.location_id != MfdAnalysis.trolley_location_id) |
                             (MfdCanisterMaster.location_id.is_null(True))),
                            MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_SKIPPED_STATUS])) \
            .group_by(LocationMasterAlias.container_id)

        for record in query:
            if record['container_id'] not in drawer_list:
                drawer_list.append(record['container_id'])

        return drawer_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfs_transfer_drawer_data(mfs_id: int) -> list:
    try:
        drawer_list = get_current_mfs_transfer_count(mfs_id)
        return drawer_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_check_entire_mfd_trolley_skipped(batch_id, trolley_id, trolley_seq, device_id_list, mfd_canister_status=None):
    try:
        skip_for_devices_dict = dict()
        skip_for_all_devices = False
        for device_id in device_id_list:
            query = MfdAnalysis.select().dicts()\
                .join(LocationMaster, on=MfdAnalysis.trolley_location_id == LocationMaster.id)\
                .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                .where(MfdAnalysis.batch_id == batch_id, DeviceMaster.id == trolley_id,
                       MfdAnalysis.trolley_seq == trolley_seq, MfdAnalysis.dest_device_id == device_id)
            mfd_record_count_by_trolley = query.count()
            logger.debug("MFD Analysis Total Count: {}, Trolley ID: {}, Trolley Sequence: {}"
                         .format(mfd_record_count_by_trolley, trolley_id, trolley_seq))
            if mfd_canister_status:
                query = query.where(MfdAnalysis.status_id << mfd_canister_status)
            mfd_record_count_by_trolley_empty_canister = query.count()
            logger.debug("MFD Analysis Total Skipped Count: {}, Trolley ID: {}, Trolley Sequence: {}"
                         .format(mfd_record_count_by_trolley_empty_canister, trolley_id, trolley_seq))

            if mfd_record_count_by_trolley == mfd_record_count_by_trolley_empty_canister:
                logger.debug("Entire Trolley Skipped for Trolley ID: {} and Trolley Sequence: {}".format(trolley_id,
                                                                                                         trolley_seq))
                skip_for_devices_dict[device_id] = True
            else:
                skip_for_devices_dict[device_id] = False

        skip_for_all_devices = all(status for status in skip_for_devices_dict.values())
        return skip_for_all_devices, skip_for_devices_dict

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_analysis_details_ids(mfd_analysis_ids: list, canister_status: list = None,
                                drug_status: list = None) -> tuple:
    """
    gets valid analysis details ids for canister update
    @param mfd_analysis_ids:
    @param canister_status:
    @param drug_status:
    @return:
    """
    analysis_details_ids = set()
    analysis_ids = set()
    try:
        query = MfdAnalysis.select(MfdAnalysisDetails.id.alias('analysis_details_id'),
                                   MfdAnalysis.id.alias('analysis_id')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.id << mfd_analysis_ids)
        if canister_status:
            query = query.where(MfdAnalysis.status_id << canister_status)
        if drug_status:
            query = query.where(MfdAnalysisDetails.status_id << drug_status)

        for record in query:
            analysis_details_ids.add(record['analysis_details_id'])
            analysis_ids.add(record['analysis_id'])
        return analysis_ids, analysis_details_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfd_pack_with_status(batch_id: int) -> tuple:
    """
    Function to get mfd packs with status by batch id
    @param batch_id:
    @return:
    """
    pack_mfd_can_status = dict()
    mfd_pack_skipped_status = dict()
    try:
        query = MfdAnalysis.select(PackDetails.id.alias('pack_id'),
                                   MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.status_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) \
            .order_by(PackDetails.order_no)

        for record in query:
            if record['pack_id'] not in pack_mfd_can_status.keys():
                pack_mfd_can_status[record['pack_id']] = dict()
                mfd_pack_skipped_status[record['pack_id']] = False
            if record['mfd_analysis_id'] not in pack_mfd_can_status[record['pack_id']].keys():
                pack_mfd_can_status[record['pack_id']][record['mfd_analysis_id']] = list()
            pack_mfd_can_status[record['pack_id']][record['mfd_analysis_id']].append(record['status_id'])
            if record['status_id'] in [constants.MFD_CANISTER_SKIPPED_STATUS]:
                mfd_pack_skipped_status[record['pack_id']] = True

        return pack_mfd_can_status, mfd_pack_skipped_status

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return pack_mfd_can_status, mfd_pack_skipped_status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(e)


@log_args_and_response
def get_pack_slot_quantity_details(slot_id_list: str) -> dict:
    """
    Function to get slot info from pack_id
    @param slot_id_list:
    @return:
    """

    try:
        if slot_id_list:
            slot_id_list = [int(id) for id in slot_id_list.strip(",").split(",")]
            select_fields = [fn.GROUP_CONCAT(fn.DISTINCT(SlotDetails.quantity)).alias(
                'quantities'),
                fn.GROUP_CONCAT(SlotDetails.quantity).alias(
                    'total_quantities').coerce(False),
                fn.GROUP_CONCAT(SlotDetails.id).alias(
                    'slot_ids').coerce(False),
                fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('drug_qty'),
                fn.SUM(SlotDetails.quantity).alias('total_qty')]

            query = PackDetails.select(*select_fields).dicts() \
                .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .where(SlotDetails.id << slot_id_list)

            for record in query:
                return record
        else:
            return {}

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return {}


@log_args_and_response
def get_batch_manual_drug_list(system_id, list_type, pack_ids=None, pack_queue=True):
    """
    Returns list of manual drugs based on drug_type `i.e` mfd drugs
    @param batch_id:
    @param list_type: drug | patient | facility
    @param pack_ids:
    @param pack_queue:
    @return:
    """
    if system_id:
        try:
            DeviceMasterAlias = DeviceMaster.alias()
            select_fields = [PackRxLink.pack_id,
                             fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id)).alias(
                                 'pack_ids_group'),
                             fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_display_id)).alias(
                                 'pack_display_ids_group'),
                             PackDetails.pack_status,
                             fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.mfd_canister_id)).alias(
                                 'canister_id'),
                             fn.GROUP_CONCAT(SlotDetails.id).alias(
                                 'slot_ids').coerce(False),
                             SlotDetails.drug_id,
                             MfdAnalysisDetails.id,
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
                             DrugMaster.concated_fndc_txr_field().alias("fndc_txr"),
                             MfdAnalysis.dest_device_id.alias('device_id'),
                             MfdAnalysis.mfs_location_number.alias('location_number'),
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
                             PackHeader.delivery_datetime]

            query = PackDetails.select(*select_fields) \
                .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
                .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
                .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == MfdAnalysis.dest_device_id) \
                .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientSchedule.patient_id == PatientMaster.id) &
                                                            (PatientSchedule.facility_id == FacilityMaster.id))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
                .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
                .join(PackAnalysis, JOIN_LEFT_OUTER, on=((PackAnalysis.id == PackAnalysisDetails.analysis_id) &
                                                         (PackAnalysis.batch_id == PackDetails.batch_id))) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == PackAnalysisDetails.device_id) \

            if pack_ids:
                query = query.where(PackDetails.system_id == system_id,
                                    PackRxLink.pack_id << pack_ids)
            else:
                query = query.where(PackDetails.system_id == system_id)

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
                    query = query.group_by(PackRxLink.pack_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                        .order_by(PackDetails.order_no)

            else:
                query = query.group_by(PackRxLink.pack_id, SlotDetails.drug_id, MfdAnalysis.mfd_canister_id) \
                    .order_by(PackDetails.order_no)

            for record in query.dicts():
                record["patient_name"] = record["last_name"] + ", " + record["first_name"]
                slot_info = get_pack_slot_quantity_details(record['slot_ids'])
                if slot_info:
                    record["quantities"] = slot_info["quantities"]
                    record["total_quantities"] = slot_info["total_quantities"]
                    record["slot_ids"] = slot_info["slot_ids"]
                    record["drug_qty"] = float(slot_info["drug_qty"])
                    record["total_qty"] = float(slot_info["total_qty"])
                record['delivery_datetime'] = str(record['delivery_datetime']) if record[
                    'delivery_datetime'] else None

                yield record

        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

        except Exception as e:
            logger.error(e)


def db_get_current_user_assignment(system_ids: list) -> dict:
    """
    returns user associated with system and pending mfd-analysis
    :param system_ids:
    :return:
    """
    system_user_data = dict()
    if not system_ids:
        raise ValueError('Missing system_ids')
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()
        system_query = DeviceMasterAlias2.select(DeviceMaster.id.alias('mfs_device_id'),
                                                 MfdAnalysis.batch_id,
                                                 MfdAnalysis.id.alias('mfd_analysis_id'),
                                                 MfdAnalysis.status_id,
                                                 DeviceMasterAlias2.system_id,
                                                 MfdAnalysis.assigned_to).dicts() \
            .join(MfdAnalysis, on=MfdAnalysis.mfs_device_id == DeviceMasterAlias2.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=((MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) &
                                                          (MfdCanisterMaster.location_id !=
                                                           MfdAnalysis.trolley_location_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .where(DeviceMasterAlias2.system_id << system_ids)
        system_query = system_query.where(mfd_canister_pending_and_inprogress_condition)
        for record in system_query:
            if record['system_id'] not in system_user_data:
                system_user_data[record['system_id']] = {
                    'associated_user': record['assigned_to'] if record['assigned_to'] else None,
                    'mfd_analysis_ids': list(),
                    'update_couch_db': False,
                    'mfs_id': record['mfs_device_id']
                }
            if record['mfd_analysis_id']:
                system_user_data[record['system_id']]['mfd_analysis_ids'].append(record['mfd_analysis_id'])
            if record['status_id'] and record['status_id'] != constants.MFD_CANISTER_PENDING_STATUS:
                system_user_data[record['system_id']]['update_couch_db'] = True
                system_user_data[record['system_id']]['batch_id'] = record['batch_id']

        return system_user_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_recommendation_pending_data(trolley_count: int, system_id: int) -> dict:
    """
    returns analysis_ids for user's upcoming trolley
    :param trolley_count: int
    :param system_id: int
    :return: list
    """
    trolley_list = list()
    trolley_user_quadrant = dict()

    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   MfdAnalysis.trolley_seq.is_null(False),
                   BatchMaster.system_id == system_id,
                   BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   MfdAnalysis.trolley_location_id.is_null(True),
                   MfdAnalysis.status_id != constants.MFD_CANISTER_SKIPPED_STATUS) \
            .order_by(MfdAnalysis.batch_id,
                      MfdAnalysis.trolley_seq)
        for record in query:
            unique_trolley_seq = "{}#{}".format(record["batch_id"], record["trolley_seq"])
            if unique_trolley_seq not in trolley_list and len(trolley_list) == trolley_count:
                break
            if unique_trolley_seq in trolley_list:
                if record['dest_device_id'] in trolley_user_quadrant[unique_trolley_seq]:
                    if record['dest_quadrant'] in trolley_user_quadrant[unique_trolley_seq][
                            record['dest_device_id']]:
                        pass
                    else:
                        trolley_user_quadrant[unique_trolley_seq][record['dest_device_id']][
                            record['dest_quadrant']] = \
                            list()
                else:
                    trolley_user_quadrant[unique_trolley_seq][record['dest_device_id']] = {
                        record['dest_quadrant']: list()}
            else:
                trolley_list.append(unique_trolley_seq)
                trolley_user_quadrant[unique_trolley_seq] = {
                    record['dest_device_id']: {record['dest_quadrant']: list()}}
            trolley_user_quadrant[unique_trolley_seq][record['dest_device_id']][record['dest_quadrant']] \
                .append(record['mfd_analysis_id'])
        return trolley_user_quadrant
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_update_current_user_assignment(assignment_data: dict) -> bool:
    """
    updates user associated with pending device of a system
    :param assignment_data: dict
    :return:
    """
    try:
        for new_user, mfd_analysis_ids in assignment_data.items():
            status = MfdAnalysis.db_update_assigned_to(analysis_ids=mfd_analysis_ids, assigned_to=new_user)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_trolley_location(analysis_ids: list, trolley_location_ids: list) -> int:
    """
    updates trolley location for given analysis_ids
    :param analysis_ids:
    :param trolley_location_ids:
    :return:
    """
    try:
        loc_status = MfdAnalysis.db_update_dest_location(analysis_ids, trolley_location_ids)
        return loc_status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_rts_canisters_in_robot(batch_id: int, device_id: int) -> bool:
    """
    This function checks the location for the RTS Canisters of the batch
    """
    logger.info("In get_rts_canisters_in_robot")
    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster.id).dicts() \
            .join(MfdAnalysis, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
            .join(LocationMaster, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where((LocationMaster.device_id == device_id), (MfdAnalysis.batch_id == batch_id),
                   (MfdAnalysis.status_id << [constants.MFD_CANISTER_RTS_REQUIRED_STATUS]))
        logger.info(query)
        if query.count() > 0:
            return True
        else:
            return False

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_next_mfd_transfer_batch(device_id: int) -> tuple:
    """
    This function will fetch the next_batch if transfers are not pending
    """
    logger.info("In_get_next_mfd_transfer_batch for device_id: {}".format(device_id))
    try:
        # LocationMasterAlias = LocationMaster.alias()
        pending_batch_ids = 0
        in_robot_batch_ids = 0
        in_robot_can_status = []

        mfd_canister_status = [constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        mfd_canister_transfer_pending_status = [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                constants.MFD_CANISTER_DROPPED_STATUS]

        batch_status_list = [settings.BATCH_DELETED, settings.BATCH_PROCESSING_COMPLETE]
        transfer_batch_status_list = [settings.BATCH_DELETED]

        # query to get batch ids for which MFD transfer is pending
        query1 = MfdAnalysis.select(MfdAnalysis.batch_id,
                                    fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.id)).alias('mfd_analysis_ids')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(BatchMaster.status.not_in(batch_status_list),
                   MfdAnalysis.dest_device_id == device_id,
                   MfdAnalysis.trolley_seq.is_null(False),
                   MfdAnalysis.status_id << mfd_canister_status) \
            .group_by(MfdAnalysis.batch_id) \
            .order_by(BatchMaster.id)
        # return if the current batch or any new batch has pending transfers
        for record in query1:
            logger.info('get_next_mfd_transfer_batch for device_id: {} pending_batch_id: {} and mfd_analysis_ids {}'.
                         format(device_id, record["batch_id"],  record['mfd_analysis_ids']))
            pending_batch_ids = record["batch_id"]
            break
        logger.info("batch_id_in_get_next_mfd_transfer_batch pending_batch_ids: {}".format(pending_batch_ids))

        # query to get batch_ids for which canisters are present in device (robot)
        query2 = MfdCanisterMaster.select(MfdAnalysis.mfd_canister_id,
                                          MfdAnalysis.batch_id,
                                          LocationMaster.id,
                                          fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id)).alias(
                                              'mfd_can_status_id'),
                                          fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.id)).alias('mfd_analysis_ids'),
                                          fn.GROUP_CONCAT(fn.DISTINCT(MfdCanisterMaster.id)).alias('mfd_can_ids'),
                                          LocationMaster.display_location).dicts() \
            .join(LocationMaster, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(BatchMaster, on=MfdAnalysis.batch_id == BatchMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(BatchMaster.status.not_in(transfer_batch_status_list),
                   MfdAnalysis.dest_device_id == device_id,
                   MfdAnalysis.trolley_seq.is_null(False),
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'],
                   MfdAnalysis.status_id << mfd_canister_transfer_pending_status) \
            .group_by(MfdAnalysis.batch_id) \
            .order_by(BatchMaster.id)

        for record in query2:
            logger.info('get_next_mfd_transfer_batch for device_id: {} transfer_pending_batch_id: {} analysis_ids {} '
                         'and can_ids {}'.format(device_id, record["batch_id"], record['mfd_analysis_ids'],
                          record['mfd_can_ids']))
            in_robot_batch_ids = record["batch_id"]
            mfd_can_status = record["mfd_can_status_id"]
            in_robot_can_status = map(int, mfd_can_status.split(","))
            break
        logger.info("batch_id_in_get_next_mfd_transfer_batch in_robot_batch_ids: {}".format(in_robot_batch_ids))

        if in_robot_batch_ids or pending_batch_ids:
            return in_robot_batch_ids, pending_batch_ids, True, in_robot_can_status
        else:
            return 0, 0, False, []

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_empty_drawer_device(device_id):
    """
    This function checks the location for the RTS Canisters of the batch
    """
    logger.info("In get_rts_canisters_in_robot")
    try:
        query = ContainerMaster.select(ContainerMaster.id.alias('container_id'),
                                       ContainerMaster.drawer_name,
                                       ContainerMaster.serial_number).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(DeviceMaster.id == device_id,
                   ContainerMaster.drawer_level << constants.MFD_TROLLEY_EMPTY_DRAWER_LEVEL)
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def check_trolley_reuse_required(progress_batch_id: int, user_id: int, device_id: int) -> dict or None:
    """
    returns trolley seq for which recommendation is required
    :param progress_batch_id:
    :param user_id:
    :param device_id:
    :return:
    """
    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.trolley_seq,
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   BatchMaster.mfd_status != constants.MFD_BATCH_FILLED,
                   MfdAnalysis.trolley_location_id.is_null(True),
                   MfdAnalysis.trolley_seq.is_null(False),
                   MfdAnalysis.assigned_to == user_id,
                   MfdAnalysis.mfs_device_id == device_id,
                   MfdAnalysis.batch_id == progress_batch_id,
                   MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS) \
            .order_by(MfdAnalysis.order_no) \
            .get()
        seq_data = {
            'seq': query['trolley_seq'],
        }
        return seq_data
    except DoesNotExist as e:
        logger.info("Trolley reuse not required.")
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_get_mfs_info(mfd_analysis_ids):
    """

    @param mfd_analysis_ids:
    :return:
    """
    mfs_data = dict()
    try:
        query = MfdAnalysis.select(MfdAnalysis.mfs_device_id,
                                   MfdAnalysis.batch_id,
                                   DeviceMaster.company_id,
                                   DeviceMaster.system_id).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .where(MfdAnalysis.id << mfd_analysis_ids) \
            .group_by(MfdAnalysis.mfs_device_id)
        for record in query:
            mfs_data[record['system_id']] = {
                'mfs_device_id': record['mfs_device_id'],
                'batch_id': record['batch_id'],
                'company_id': record['company_id']
            }
        return mfs_data
    except DoesNotExist as e:
        logger.info("Trolley reuse not required: {}".format(e))
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def update_transferred_location(analysis_transfer_loc_dict):
    """
    updates canister_id in mfd_analysis based on callback
    :param analysis_transfer_loc_dict:
    :return:
    """
    analysis_ids = list(analysis_transfer_loc_dict.keys())
    transfer_loc_ids = list(analysis_transfer_loc_dict.values())

    try:
        status = MfdAnalysis.db_update_transferred_location(analysis_ids, transfer_loc_ids)
        return status
    except (InternalError, IntegrityError) as e:
        raise e


def update_batch_data(batch_id: int, update_dict: dict) -> int:
    """
    updates batch_master details of a batch
    @param batch_id:
    @return:
    @param update_dict:
    """
    try:
        status = BatchMaster.db_update(update_dict, id=batch_id)
        return status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_max_order_number(analysis_ids: list) -> dict:
    """
    returns last transaction history for given mfd_canister
    :param analysis_ids: list
    :return: record
    """
    try:
        record = MfdAnalysis.db_get_order_number_from_analysis_id(analysis_ids=analysis_ids)
        return record
    except (IntegrityError, InternalError) as e:
        raise e


def mfd_data_by_order_no(order_no: int) -> dict:
    """
    returns  mfd data by order no
    :param order_no: list
    :return: record
    """
    try:
        mfd_query = MfdAnalysis.select(LocationMaster.device_id, MfdAnalysis.trolley_seq,
                                       DeviceMaster.name).dicts() \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
            .where(MfdAnalysis.order_no == order_no)
        return mfd_query
    except (IntegrityError, InternalError) as e:
        raise e

@log_args_and_response
def mfd_remove_current_canister_data(mfs_id: int) -> int:
    """
    removes current canister's data from TempMfdFilling as the filling is done
    :param mfs_id: int
    :return: status
    """
    try:
        logger.info("in_deleting_mfs_for {}".format(mfs_id))
        status = TempMfdFilling.db_delete_current_filling(mfs_id)
        logger.info("returning_from_deleting_mfs_for {} with count {}".format(mfs_id, status))
        return status
    except (IntegrityError, InternalError) as e:
        raise e


def mfd_update_transfer_done(analysis_ids: list) -> int:
    """
    updates transfer done status for mfd canister
    :param analysis_ids: list
    :return: status
    """
    try:
        status = TempMfdFilling.db_update_canister_transfer_status(analysis_ids, True)
        return status
    except (IntegrityError, InternalError) as e:
        raise e


def db_get_batch_mfd_drugs(batch_id: int) -> dict:
    """
    function to get mfd drug info pack wise
    @param batch_id:
    @return: list
    """
    try:

        query = MfdAnalysis.select(PackRxLink.pack_id,
                                   DrugMaster.ndc,
                                   DrugMaster.formatted_ndc,
                                   DrugMaster.txr,
                                   DrugMaster.strength,
                                   DrugMaster.strength_value,
                                   DrugMaster.drug_name,
                                   PackDetails.pack_display_id,
                                   PatientMaster.last_name,
                                   PatientMaster.first_name,
                                   PatientMaster.patient_no,
                                   PackHeader.patient_id,
                                   SlotDetails.drug_id,
                                   MfdAnalysis.dest_device_id.alias('device_id'),
                                   PatientMaster.facility_id,
                                   fn.GROUP_CONCAT(fn.DISTINCT(SlotDetails.quantity)).alias(
                                       'quantities'),
                                   fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('drug_qty'),
                                   fn.SUM(SlotDetails.quantity).alias('total_qty'),
                                   ).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(MfdAnalysis.batch_id == batch_id) \
            .group_by(PackRxLink.pack_id,
                      DrugMaster.formatted_ndc,
                      DrugMaster.txr) \
            .order_by(PackDetails.order_no)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def update_couch_db_mfd_canister_master(mfd_analysis_ids=None, company_ids=None):
    """
    updates couch db document with pending rts count.
    @param mfd_analysis_ids: list
    @param company_ids: list
    :return:
    """
    if mfd_analysis_ids is None and company_ids is None:
        raise ValueError
    try:
        mfs_ids = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.company_id)).alias('company_id')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(MfdAnalysis.id << list(mfd_analysis_ids)) \
            .group_by(MfdAnalysis.batch_id).get()
        company_ids = set(mfs_ids['company_id'].split(','))
        for company_id in company_ids:
            count = db_get_rts_required_canister_count(company_id)
            logger.info('pending_rts_count: {} for company_id: {}'.format(count, company_id))
            couch_db_data = {'count': count, 'update_timestamp': get_current_date_time()}
            update_mfd_rts_count_in_couch_db(constants.CONST_MFD_RTS_DOC_ID, company_id, couch_db_data)
    except RealTimeDBException as e:
        raise e
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def update_couch_db_mfd_canister_transfer(mfd_analysis_ids=None):
    """
    updates couch db document with pending rts count.
    @param mfd_analysis_ids: list
    :return:
    """
    if mfd_analysis_ids is None:
        raise ValueError
    DeviceMasterAlias = DeviceMaster.alias()
    try:
        query = MfdAnalysis.select(DeviceMaster.id.alias('trolley_id'),
                                   DeviceMasterAlias.system_id,
                                   MfdAnalysis.batch_id,
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.dest_device_id)).alias(
                                       'dest_device')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == MfdAnalysis.dest_device_id) \
            .where(MfdAnalysis.id << list(mfd_analysis_ids),
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_RTS_REQUIRED_STATUS],
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_SKIPPED_STATUS,
                                                    constants.MFD_DRUG_RTS_REQUIRED_STATUS],
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['Manual Canister Cart']) \
            .group_by(DeviceMaster.id)

        for record in query:
            device_ids = set(record['dest_device'].split(','))
            system_id = record['system_id']
            # batch_id = record['batch_id']
            # trolley_id = record['trolley_id']
            for device in device_ids:
                rts_data = {"rts_changes": True}
                update_mfd_transfer_couch_db(device, system_id, rts_data)
    except RealTimeDBException as e:
        raise e
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_couch_db_current_mfs(mfd_analysis_ids, skip_system):
    """
    updates couch db document to inform user about canister/drug status update if canister is currently on mfs.
    @param skip_system:
    @param mfd_analysis_ids: list
    :return:
    """
    try:
        DeviceMasterAlias = DeviceMaster.alias()
        clauses = [MfdAnalysis.id << list(mfd_analysis_ids),
                   DeviceMasterAlias.device_type_id == settings.DEVICE_TYPES["Manual Filling Device"]]
        if skip_system:
            clauses.append((DeviceMaster.system_id.not_in(skip_system)))
        logger.info('in update mfs doc')
        mfs_ids = MfdAnalysis.select(MfdAnalysis.mfs_device_id,
                                     DeviceMaster.system_id).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(MfdAnalysis.mfs_device_id)
        for record in mfs_ids:
            system_id = record['system_id']
            mfs_id = record['mfs_device_id']
            mfs_data = {'pack_manual_delete': True}
            status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                          system_id=system_id)
            couch_db_doc = document.get_document()
            couch_db_data = couch_db_doc.get("data", {})
            # couch_db_canister_data = couch_db_data.get('canister_data', {})
            batch_id = couch_db_data.get('batch_id', None)
            user_id = couch_db_data.get('user_id', None)
            if batch_id:
                query_2 = db_get_mfd_batch_info(batch_ids=[batch_id], user_id=user_id, mfs_id=mfs_id)
                filled_canisters = None
                total_canisters = None
                for record in query_2:
                    filled_canisters = int(record['filled_canister'])
                    total_canisters = int(record['total_canister'])
                mfs_data['total_canisters'] = total_canisters
                mfs_data['filled_canisters'] = filled_canisters
            skip_system.append(system_id)
            update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                        system_id, mfs_data)
        return skip_system
    except RealTimeDBException as e:
        raise e
    except DoesNotExist as e:
        logger.info("No_canister_currently_present_on_mfs for analysis_ids:" + str(mfd_analysis_ids))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_rts_required_canister_count(company_id):
    """
    to return the count of canisters that require rts
    :param company_id:
    :return: int
    """
    clauses = list()
    clauses.append(MfdCanisterMaster.company_id == company_id)
    clauses.append((MfdCanisterMaster.rfid.is_null(False)))

    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id')) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, on=((MfdAnalysisDetails.analysis_id == MfdAnalysis.id) &
                                          (MfdAnalysisDetails.status_id == constants.MFD_DRUG_RTS_REQUIRED_STATUS))) \
            .where(*clauses) \
            .group_by(MfdCanisterMaster.id)

        return query.count()

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_robot_system_info(mfd_analysis_ids):
    try:
        system_id = MfdAnalysis.select(MfdAnalysis,
                                       DeviceMaster.company_id,
                                       DeviceMaster.system_id.alias('dest_system_id')).dicts() \
            .join(DeviceMaster, on=MfdAnalysis.dest_device_id == DeviceMaster.id) \
            .where(MfdAnalysis.id << mfd_analysis_ids) \
            .group_by(MfdAnalysis.dest_device_id)
        return system_id

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return e


def db_get_mfd_dropped_pills_v2(pack_id: int) -> dict:
    """
    Returns mfd dropped pill count for given pack_id
    :param pack_id:
    :return: list
    """
    try:

        results = dict()
        query = SlotHeader.select(PackGrid.slot_row,
                                  PackGrid.slot_column,
                                  fn.SUM(MfdAnalysisDetails.quantity).alias('dropped_quantity'),
                                  SlotHeader.id.alias('slot_header_id'),
                                  UniqueDrug.id.alias('unique_drug_id')).dicts() \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.txr == DrugMaster.txr) &
                                 (UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .where(PackRxLink.pack_id == pack_id,
                   MfdAnalysisDetails.status_id << [constants.MFD_DRUG_DROPPED_STATUS]) \
            .group_by(SlotDetails.id)
        for item in query:
            loc = PackGrid.map_pack_location(item["slot_row"], item["slot_column"])
            results.setdefault(item["unique_drug_id"], {})
            results[item["unique_drug_id"]].setdefault(loc, {})
            results[item["unique_drug_id"]][loc] = {
                "dropped_qty": item["dropped_quantity"]
            }
        return results
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def get_pack_mfd_canisters(pack_id: int, company_id: int, status_ids: list = None) -> list:
    """
    returns mfd canisters' data of a pack
    :param pack_id:
    :param company_id:
    :param status_ids:
    :return:
    """
    logger.info("In db_get_mfd_slot_info")

    # CodeMasterAlias = CodeMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()

    # mfd_canister_data = list()

    clauses = list()
    clauses.append((PackDetails.id == pack_id))
    clauses.append((PackDetails.company_id == company_id))
    clauses.append((MfdAnalysisDetails.status_id == constants.MFD_DRUG_FILLED_STATUS))

    if status_ids:
        clauses.append((MfdAnalysis.status_id << status_ids))

    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.batch_id,
                                   MfdAnalysis.status_id.alias('mfd_canister_status'),
                                   MfdAnalysis.mfd_canister_id,
                                   DeviceMasterAlias.name.alias('home_cart_name'),
                                   SlotDetails.id.alias('slot_id'),
                                   ContainerMaster.drawer_name.alias("drawer_number"),
                                   LocationMaster.location_number,
                                   LocationMaster.display_location,
                                   LocationMaster.device_id,
                                   LocationMaster.quadrant,
                                   PackRxLink.pack_id,
                                   DeviceMaster.name.alias('current_device_name'),
                                   MfdCanisterMaster.rfid,
                                   MfdCanisterMaster.state_status,
                                   CodeMaster.value.alias('can_status'),
                                   LocationMaster.is_disabled.alias('location_disabled')).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=MfdCanisterMaster.home_cart_id == DeviceMasterAlias.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .where(*clauses) \
            .group_by(MfdCanisterMaster.id) \
            .order_by(ContainerMaster.id)

        return list(query)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def check_mfd_recommendation_executed(batch_id: int) -> bool:
    """
    Function to check mfd if mfd recommendation is already executed
    @param batch_id:
    @return:
    """
    try:
        query = MfdAnalysis.select(MfdAnalysis.id, MfdAnalysis.status_id, MfdAnalysisDetails.status_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .where(MfdAnalysis.batch_id == batch_id, MfdAnalysis.status_id != constants.MFD_CANISTER_SKIPPED_STATUS)

        for record in query:
            logger.info("MFD already executed {}".format(record))
            return True

        return False
    except DoesNotExist as e:
        logger.error("Function: check_mfd_recommendation_executed -- {}".format(e), exc_info=True)
        return False
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Function: check_mfd_recommendation_executed -- {}".format(e), exc_info=True)
        raise


@log_args_and_response
def get_mfd_analysis_ids_for_skip(batch_id=None, trolley_seq=None) -> tuple:
    """
    Function to check mfd if mfd recommendation is already executed
    @param batch_id:
    @param mfs_id:
    @param trolley_id:
    @return:
    """
    try:
        mfd_analysis_ids = set()
        mfd_analysis_details_ids = set()
        trolley_seq_info = dict()
        DeviceMasterAlias = DeviceMaster.alias()

        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis,
                                   MfdAnalysisDetails.id.alias('mfd_analysis_details_id'),
                                   TempMfdFilling.id.alias('temp_mfd_filling_id'),
                                   DeviceMaster.id.alias('trolley_id'),
                                   DeviceMasterAlias.system_id.alias('system_id')).dicts() \
            .join(DeviceMasterAlias, on=MfdAnalysis.mfs_device_id == DeviceMasterAlias.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id)         \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(TempMfdFilling, JOIN_LEFT_OUTER, on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_PENDING_STATUS,
                                             constants.MFD_CANISTER_IN_PROGRESS_STATUS])

        if trolley_seq:
            query = query.where(MfdAnalysis.trolley_seq == trolley_seq)

        for record in query:
            if not record['trolley_seq'] in trolley_seq_info:
                trolley_seq_info[record['trolley_seq']] = dict()
                trolley_seq_info[record['trolley_seq']]['trolley_id'] = record['trolley_id']
                trolley_seq_info[record['trolley_seq']]['mfs_device_id'] = record['mfs_device_id']
                trolley_seq_info[record['trolley_seq']]['system_id'] = record['system_id']
                trolley_seq_info[record['trolley_seq']]['skip_analysis_ids'] = set()
                trolley_seq_info[record['trolley_seq']]['skip_analysis_details_ids'] = set()
                trolley_seq_info[record['trolley_seq']]['is_canister_present'] = False
                trolley_seq_info[record['trolley_seq']]['locations_to_be_skipped'] = set()
            if record['mfd_canister_id']:
                trolley_seq_info[record['trolley_seq']]['is_canister_present'] = True
            else:
                mfd_analysis_ids.add(record['mfd_analysis_id'])
                mfd_analysis_details_ids.add(record['mfd_analysis_details_id'])
                trolley_seq_info[record['trolley_seq']]['skip_analysis_ids'].add(record['mfd_analysis_id'])
                trolley_seq_info[record['trolley_seq']]['skip_analysis_details_ids'].add(record['mfd_analysis_details_id'])
            if not record['mfd_canister_id'] and record['mfs_location_number']:
                trolley_seq_info[record['trolley_seq']]['locations_to_be_skipped'].add(record['mfs_location_number'])

        return list(mfd_analysis_ids), list(mfd_analysis_details_ids), trolley_seq_info

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def get_empty_location_by_drawer_level(device_id, container_level, exclude_location):
    """
    Function to get empty location by drawer
    @param exclude_location:
    @param device_id:
    @param container_level:
    @return:
    """
    try:
        logger.info(
            "input get_empty_location_by_drawer_level  device: {}, drawer_level: {}".format(device_id, container_level))
        query = LocationMaster.select(LocationMaster.id).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(MfdCanisterMaster.id.is_null(True),
                   LocationMaster.device_id == device_id,
                   ContainerMaster.drawer_level << container_level,
                   LocationMaster.is_disabled == False)
        if exclude_location:
            query = query.where(LocationMaster.id.not_in(exclude_location))

        for record in query:
            return record['id']

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist:
        return None


@log_args_and_response
def get_half_pill_drug_pack_data(batch_id, device_ordered_packs_dict):
    query = PackDetails.select(PackDetails.id, fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
                               SlotDetails.quantity) \
        .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
        .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
        .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
        .where(PackDetails.batch_id == batch_id)

    robot_half_pill_drug_pack_dict = defaultdict(dict)
    for record in query.dicts():
        for device in device_ordered_packs_dict:
            if record['id'] in device_ordered_packs_dict[device]:
                if not float(record['quantity']).is_integer():
                    if record['drug'] not in robot_half_pill_drug_pack_dict[device]:
                        robot_half_pill_drug_pack_dict[device][record['drug']] = set()
                    robot_half_pill_drug_pack_dict[device][record['drug']].add(record['id'])
                break
        # if not record['quantity'].is_integer():
        #     half_pill_drug_pack_dict[record['drug']].append(record['id'])
        # if record['drug'] not in half_pill_drug_pack_dict:
        #     half_pill_drug_pack_dict[record['drug']] = []
    return robot_half_pill_drug_pack_dict


@log_args_and_response
def get_pack_slotwise_canister_drugs(pack_id_list, zone_id):
    """
    This Function makes dictionaries related to pack_slot data.
    1) Creating pack_slot_drug_dict with considering only canister drug.This dict will be used in drop algorithm.
    2) Creating pack_drug_slot_number_slot_id_dict for storing slot_id in mfd_analysis_details table.
    3) Creating pack_slot_drug_dict_global for keeping all drug data slot wise.
    @param zone_id:
    @param pack_id_list:
    :return:
    """
    try:
        '''
        1. Creating Pack_slot_drug_dict(Only Canister Drug)
        '''
        pack_slot_drug_dict = dict()
        pack_drug_slot_number_slot_id_dict = {}
        pack_slot_drug_dict_global = {}
        drug_list = list()

        if len(pack_id_list):
            sub_q = CanisterMaster.select(DrugMaster.concated_fndc_txr_field().alias('drug_fndc_txr')) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.canister_id == CanisterMaster.id) \
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(CanisterZoneMapping, on=((CanisterZoneMapping.canister_id == CanisterMaster.id) & (
                    CanisterMaster.active == settings.is_canister_active) & (
                                                       CanisterZoneMapping.zone_id == zone_id))) \
                .where(PackAnalysis.pack_id << pack_id_list) \
                .group_by(DrugMaster.concated_fndc_txr_field())

            for record in sub_q.dicts():
                drug_list.append(record['drug_fndc_txr'])

            if drug_list:
                query = PackDetails.select(PackDetails.id,
                                           DrugMaster.concated_fndc_txr_field(sep='##').alias('drug_id'),
                                           PackGrid.slot_number, SlotDetails.id.alias('slot_id')) \
                    .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                    .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                    .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                    .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                    .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                    .where(PackDetails.id << pack_id_list, DrugMaster.concated_fndc_txr_field() << drug_list,
                           SlotDetails.quantity.not_in(settings.DECIMAL_QTY_LIST))

                for record in query.dicts():
                    if record['id'] not in pack_slot_drug_dict.keys():
                        pack_slot_drug_dict[record['id']] = {}
                    if record['slot_number'] not in pack_slot_drug_dict[record['id']].keys():
                        pack_slot_drug_dict[record['id']][record['slot_number']] = set()
                    if record['drug_id'] is not None:
                        pack_slot_drug_dict[record['id']][record['slot_number']].add(record['drug_id'])

            '''
            2. Creating pack_drug_slot_number_slot_id_dict
            '''
            query1 = SlotDetails.select(PackDetails.id.alias('pack_id'),
                                        DrugMaster.concated_fndc_txr_field(sep='##').alias('drug'),
                                        SlotDetails.id.alias('slot_id'), PackGrid.slot_number) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .where(PackDetails.id << pack_id_list)

            for record in query1.dicts():
                if record['pack_id'] not in pack_drug_slot_number_slot_id_dict:
                    pack_drug_slot_number_slot_id_dict[record['pack_id']] = {}
                if record['drug'] not in pack_drug_slot_number_slot_id_dict[record['pack_id']]:
                    pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']] = {}
                if record['slot_number'] not in pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']]:
                    pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']][record['slot_number']] = 0
                pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']][record['slot_number']] = record[
                    'slot_id']

            '''
            3. Creating pack_slot_drug_dict_global(All Drugs)
            '''

            query = PackDetails.select(PackDetails.id,
                                       DrugMaster.concated_fndc_txr_field(sep='##').alias('drug_id'),
                                       PackGrid.slot_number, SlotDetails.id.alias('slot_id')) \
                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .where(PackDetails.id << pack_id_list)

            for record in query.dicts():
                if record['id'] not in pack_slot_drug_dict_global.keys():
                    pack_slot_drug_dict_global[record['id']] = {}
                if record['slot_number'] not in pack_slot_drug_dict_global[record['id']].keys():
                    pack_slot_drug_dict_global[record['id']][record['slot_number']] = set()
                if record['drug_id'] is not None:
                    pack_slot_drug_dict_global[record['id']][record['slot_number']].add(record['drug_id'])

        return pack_slot_drug_dict, pack_drug_slot_number_slot_id_dict, pack_slot_drug_dict_global
    except (InternalError, IntegrityError, DataError, ValueError) as e:
        logger.error("Error in MFD recommendation {}".format(e))
        raise


@log_args_and_response
def get_quadrant_drugs(batch_id, device_id_list= None):
    """
    To get quadrant drugs from canister destination location.
    Makes the dictionaries related to canister recommendation that which quadrant has which canisters and drugs. It helps in drop algorithm for fully manual slots with automatic slots.
    @param device_id_list:
    @param batch_id:
    @return:
    """
    try:
        robot_quadrant_drug_data = {}
        robot_quadrant_drug_canister_dict = {}
        robot_drugs_dict = {}
        query = CanisterTransfers.select(DrugMaster.concated_fndc_txr_field(sep='##').alias("drug"), CanisterMaster.id,
                                         CanisterTransfers.dest_quadrant, CanisterTransfers.dest_device_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterTransfers.batch_id == batch_id)

        if device_id_list:
            query = query.where(CanisterTransfers.dest_device_id == device_id_list)

        for record in query.dicts():
            if record['dest_device_id'] not in robot_quadrant_drug_data:
                robot_quadrant_drug_data[record['dest_device_id']] = {}
                robot_quadrant_drug_canister_dict[record['dest_device_id']] = {}
                robot_drugs_dict[record['dest_device_id']] = set()
            if record['dest_quadrant'] not in robot_quadrant_drug_data[record['dest_device_id']]:
                robot_quadrant_drug_data[record['dest_device_id']][record['dest_quadrant']] = {}
                robot_quadrant_drug_canister_dict[record['dest_device_id']][record['dest_quadrant']] = {}
            if record['drug'] not in robot_quadrant_drug_canister_dict[record['dest_device_id']][
                    record['dest_quadrant']]:
                robot_quadrant_drug_canister_dict[record['dest_device_id']][record['dest_quadrant']][
                    record['drug']] = set()
            if 'drugs' not in robot_quadrant_drug_data[record['dest_device_id']][record['dest_quadrant']]:
                robot_quadrant_drug_data[record['dest_device_id']][record['dest_quadrant']]['drugs'] = set()
            robot_quadrant_drug_data[record['dest_device_id']][record['dest_quadrant']]['drugs'].add(record['drug'])
            robot_drugs_dict[record['dest_device_id']].add(record['drug'])
            robot_quadrant_drug_canister_dict[record['dest_device_id']][record['dest_quadrant']][record['drug']].add(
                record['id'])
            # drug_set.add(record['drug'])
        return robot_quadrant_drug_data, robot_quadrant_drug_canister_dict, robot_drugs_dict

    except (InternalError, IntegrityError, DataError, DoesNotExist, ValueError) as e:
        logger.error("Error in MFD recommendation get_quadrant_drugs {}".format(e))
        raise


@log_args_and_response
def get_manual_drug_pack_info(batch_id):
    """
    This function makes dicts related to manual drug slots which required in mfd rec. algorithm.
    1) Create pack_slot_drug_qty dict
    2) Create Device Ordered Patients and packs dict
    3) - creating patient_pack_column_drop_slot_quad_dict . If any slot can be filled from multiple quadrant then quad list with more than 1 entry.(There are 4 columns in each pack(morning,noon,evening,bed))
       - patient_pack_column_manual_slots_dict. This dict indicates fully manual slots of patient packs' column wise.
    4) Creating patient_pack_slot_quad_config_dict . This dict is for keeping config id of automatic slots.
    :param batch_id:
    :return:All created dictionaries
    """
    try:
        patient_pack_column_drop_slot_quad_dict = OrderedDict()
        patient_pack_column_manual_slots_dict = OrderedDict()
        pack_slot_drug_qty_dict = {}
        device_ordered_packs_dict = {}
        device_ordered_patients_dict = {}
        pack_travelled_list = list()
        pack_device_dict = dict()
        # pack_slot_quad_config_dict = {}
        patient_pack_slot_quad_config_dict = {}
        manual_column_pack_list = []
        pack_list = []
        with db.transaction():

            device_query = PackAnalysis.select(
                fn.GROUP_CONCAT(
                    fn.DISTINCT(PackAnalysisDetails.device_id)).alias(
                    'device_id'),
                PackAnalysis.pack_id,
                PatientRx.patient_id,
            ).dicts() \
                .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .where(PackAnalysis.batch_id == batch_id).group_by(PackAnalysis.pack_id)

            for record in device_query:
                if record['device_id']:
                    device_list = str(record['device_id']).split(",")
                    device_list = list(filter(None, device_list))
                    pack_device_dict[record['pack_id']] = int(device_list[0])

            sub_q = PackAnalysis.select(
                SlotHeader.id.alias('id'),
                fn.GROUP_CONCAT(
                    fn.DISTINCT(fn.CONCAT(PackAnalysisDetails.quadrant, '_', PackAnalysisDetails.config_id))).alias(
                    'drop_config'),
                PackAnalysisDetails.drop_number.alias('drop_number'),
                PackGrid.slot_number.alias('slot_number'),
                PackAnalysisDetails.device_id.alias('device_id')
            ) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .where(PackAnalysisDetails.canister_id.is_null(False), PackAnalysis.batch_id == batch_id).group_by(
                SlotHeader.id).alias('sub_q')

            query = PackDetails.select(
                PackDetails.id.alias("pack_id"),
                PackDetails.order_no,
                PackAnalysisDetails.slot_id,
                PackGrid.slot_number,
                sub_q.c.drop_number,
                sub_q.c.device_id,
                sub_q.c.drop_config.alias('quad_config'),
                DrugMaster.concated_fndc_txr_field(sep='##').alias('drug'),
                SlotDetails.quantity,
                PatientRx.patient_id
            ).join(PackAnalysis, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(sub_q, JOIN_LEFT_OUTER, on=sub_q.c.id == SlotHeader.id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .where(PackAnalysis.batch_id == batch_id, PackAnalysisDetails.canister_id.is_null(True),
                       PackDetails.pack_status != settings.DELETED_PACK_STATUS) \
                .order_by(PackDetails.order_no)

            for record in query.dicts():
                if record['pack_id'] not in pack_list:
                    pack_list.append(int(record['pack_id']))
                '''
                1. creating pack_slot_drug_qty_dict
                '''
                if record['pack_id'] not in pack_slot_drug_qty_dict:
                    pack_slot_drug_qty_dict[record['pack_id']] = {}
                if record['slot_number'] not in pack_slot_drug_qty_dict[record['pack_id']]:
                    pack_slot_drug_qty_dict[record['pack_id']][record['slot_number']] = OrderedDict()
                pack_slot_drug_qty_dict[record['pack_id']][record['slot_number']][record['drug']] = float(
                    record['quantity'])

                '''
                2. creating device_ordered_packs_dict
                '''
                if record['device_id'] is not None:
                    if record['device_id'] not in device_ordered_patients_dict:
                        device_ordered_patients_dict[record['device_id']] = []
                        device_ordered_packs_dict[record['device_id']] = []
                    if record['patient_id'] not in device_ordered_patients_dict[record['device_id']]:
                        device_ordered_patients_dict[record['device_id']].append(record['patient_id'])
                    if record['pack_id'] not in device_ordered_packs_dict[record['device_id']]:
                        device_ordered_packs_dict[record['device_id']].append(record['pack_id'])
                        pack_travelled_list.append(record['pack_id'])

                # '''
                # creating pack_slot_quad_config_dict
                # '''
                # if record['pack_id'] not in pack_slot_quad_config_dict:
                #     pack_slot_quad_config_dict[record['pack_id']] = {}
                # if record['slot_number'] not in pack_slot_quad_config_dict[record['pack_id']]:
                #     pack_slot_quad_config_dict[record['pack_id']][record['slot_number']] = {}
                # pack_slot_quad_config_dict[record['pack_id']][record['slot_number']] = quad_config_dict

                '''
                3. creating patient_pack_column_drop_slot_quad_dict and patient_pack_column_manual_slots_dict
                '''
                if record['drop_number'] == None:
                    # TODO: ADD logic here.
                    if record['patient_id'] not in patient_pack_column_manual_slots_dict:
                        patient_pack_column_manual_slots_dict[record['patient_id']] = {}
                    if record['pack_id'] not in patient_pack_column_manual_slots_dict[record['patient_id']]:
                        manual_column_pack_list.append(record['pack_id'])
                        patient_pack_column_manual_slots_dict[record['patient_id']][record['pack_id']] = {}
                    column_id = settings.SLOT_COLUMN_ID[record['slot_number']]
                    if column_id not in patient_pack_column_manual_slots_dict[record['patient_id']][
                            record['pack_id']]:
                        patient_pack_column_manual_slots_dict[record['patient_id']][record['pack_id']][
                            column_id] = set()
                    patient_pack_column_manual_slots_dict[record['patient_id']][record['pack_id']][column_id].add(
                        record['slot_number'])

                    if record['pack_id'] not in pack_travelled_list and record['pack_id'] in pack_device_dict:
                        device_id = pack_device_dict[record['pack_id']]
                        if device_id not in device_ordered_patients_dict:
                            device_ordered_patients_dict[device_id] = []
                            device_ordered_packs_dict[device_id] = []
                        if record['patient_id'] not in device_ordered_patients_dict[device_id]:
                            device_ordered_patients_dict[device_id].append(record['patient_id'])
                        if record['pack_id'] not in device_ordered_packs_dict[device_id]:
                            device_ordered_packs_dict[device_id].append(record['pack_id'])
                            pack_travelled_list.append(record['pack_id'])

                    continue

                quad_list = []
                quad_config_dict = {}
                for quad_config in record['quad_config'].split(','):
                    quad = quad_config.split('_')[0]
                    config = quad_config.split('_')[1]
                    quad_config_dict[int(quad)] = int(config)
                    quad_list.append(quad)

                if record['patient_id'] not in patient_pack_column_drop_slot_quad_dict:
                    patient_pack_column_drop_slot_quad_dict[record['patient_id']] = OrderedDict()
                if record['pack_id'] not in patient_pack_column_drop_slot_quad_dict[record['patient_id']]:
                    patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']] = {}
                column_id = settings.SLOT_COLUMN_ID[record['slot_number']]
                if column_id not in patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']]:
                    patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']][column_id] = {}
                if record['drop_number'] not in \
                        patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']][column_id]:
                    patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']][column_id][
                        record['drop_number']] = {}
                if record['slot_number'] not in \
                        patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']][column_id][
                            record['drop_number']]:
                    patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']][column_id][
                        record['drop_number']][record['slot_number']] = set()
                patient_pack_column_drop_slot_quad_dict[record['patient_id']][record['pack_id']][column_id][
                    record['drop_number']][record['slot_number']] = tuple(quad_list) if len(quad_list) > 1 else int(
                    quad_list[0])

                '''
                4) creating patient_pack_slot_quad_config_dict
                '''
                if record['patient_id'] not in patient_pack_slot_quad_config_dict:
                    patient_pack_slot_quad_config_dict[record['patient_id']] = {}
                if record['pack_id'] not in patient_pack_slot_quad_config_dict[record['patient_id']]:
                    patient_pack_slot_quad_config_dict[record['patient_id']][record['pack_id']] = {}
                if record['slot_number'] not in patient_pack_slot_quad_config_dict[record['patient_id']][
                        record['pack_id']]:
                    patient_pack_slot_quad_config_dict[record['patient_id']][record['pack_id']][
                        record['slot_number']] = {}
                patient_pack_slot_quad_config_dict[record['patient_id']][record['pack_id']][
                    record['slot_number']] = quad_config_dict

            for pack, slot_data in pack_slot_drug_qty_dict.items():
                for slot, drug_data in slot_data.items():
                    pack_slot_drug_qty_dict[pack][slot] = OrderedDict(
                        sorted(pack_slot_drug_qty_dict[pack][slot].items(), key=lambda k: k[0]))

            return patient_pack_column_drop_slot_quad_dict, device_ordered_patients_dict, pack_slot_drug_qty_dict, patient_pack_slot_quad_config_dict, patient_pack_column_manual_slots_dict, pack_list, device_ordered_packs_dict

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        print(e)
        raise e


@log_args_and_response
def add_mfd_analysis_data(data_dict: dict) -> object:
    try:
        return BaseModel.db_create_record(data_dict, MfdAnalysis, get_or_create=False)
    except (DataError, IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def add_mfd_analysis_details_data(data_dict: list) -> object:
    try:
        return BaseModel.db_create_multi_record(data_dict, MfdAnalysisDetails)

    except (DataError, IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@retry(3)
def update_mfs_data_in_couch_db(document_name, system_id, mfs_data, reset_data=False):
    """
    updates couch-db doc for manual fill station of a particular system

    @param document_name:
    @param system_id:
    @param mfs_data:
    @return:
    @param reset_data:
    """
    try:
        logger.info("Inside update_mfs_data_in_couch_db -- document_name: {}, system_id: {}, mfs_data: {}, "
                    "reset_data: {}".format(document_name, system_id, mfs_data, reset_data))
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=None)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", constants.CONST_MANUAL_FILL_STATION_TYPE)
        couchdb_doc.setdefault("data", {})
        for key, value in mfs_data.items():
            couchdb_doc["data"][key] = value
        if reset_data:
            couchdb_doc["data"] = {}
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@log_args_and_response
def update_mfd_rts_count_in_couch_db(document_name, company_id, mfs_data):
    """
    updates couch-db doc for manual fill station of a particular system
    :param document_name: str
    :param company_id: int
    :param mfs_data: dict
    :return: tuple
    """
    try:
        document = initialize_couch_db_doc(document_name,
                                           system_id=None,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", constants.CONST_MFD_RTS_TYPE)
        couchdb_doc.setdefault("data", {})
        for key, value in mfs_data.items():
            couchdb_doc["data"][key] = value
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("conflict_while_saving_document")
    except Exception as e:
        logger.error(e, exc_info=True)
        raise RealTimeDBException("Couldn't update rts count in couch-db")


@retry(3)
def update_mfd_transfer_couch_db(device_id, system_id, mfd_data, reset_data=False):
    """
    updates wizard doc for manual fill station of a particular system
    @param device_id:
    @param system_id:
    @param mfd_data:
    @param reset_data:
    @return:
    """
    try:
        document_name = '{}_{}'.format(constants.MFD_TRANSFER_COUCH_DB, device_id)
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=None)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", constants.MFD_TRANSFER_DOC_TYPE)
        couchdb_doc.setdefault("data", {})
        for key, value in mfd_data.items():
            couchdb_doc["data"][key] = value
        if reset_data:
            couchdb_doc["data"] = {}
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@log_args_and_response
def get_drug_status_by_drug_id(drug_id, dicts=False):
    """
       get drug status by drug id
    """
    try:
        drug = DrugMaster.select(DrugStatus.ext_status,
                                 DrugMaster) \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .where(DrugMaster.id == drug_id)
        if dicts:
            drug = drug.dicts()
        return drug.get()
    except (DoesNotExist, IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("Error in get_drug_status_by_drug_id {}".format(e))
        raise e


@log_args_and_response
def get_manual_drugs_dao(batch_id, system_id):
    try:
        manual_drug_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        drug_ids = set()
        facility_ids = set()
        facility_seq_no = dict()
        response = list()
        for record in CanisterMaster.select(
                DrugMaster.formatted_ndc,
                DrugMaster.txr,
                CanisterMaster.drug_id
        ).dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
                .where(DeviceMaster.system_id == system_id,
                       CanisterMaster.location_id.is_null(False),
                       LocationMaster.is_disabled == False):
            drug_ids.add((record["formatted_ndc"], record["txr"]), )

        if batch_id:
            try:
                mfd_data_query = db_get_batch_mfd_drugs(batch_id)
                for record in mfd_data_query:
                    fndc_txr = (record["formatted_ndc"], record["txr"])
                    manual_drug_data[record["pack_id"]][fndc_txr] = record

                # # sub query to select pack drugs
                # sub_q = PackRxLink.select(PackRxLink.id.alias('pack_rx_id'),
                #                           PatientRx.drug_id,
                #                           PackRxLink.pack_id,
                #                           DrugMaster.formatted_ndc,
                #                           DrugMaster.txr) \
                #     .join(PatientRx,
                #           on=(PatientRx.id == PackRxLink.patient_rx_id)) \
                #     .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
                #     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                #     .where(PackDetails.batch_id == batch_id).alias('pack_drugs')
                query = PackAnalysisDetails.select(PackAnalysis.pack_id,
                                                   PackAnalysisDetails.canister_id,
                                                   LocationMaster.device_id,
                                                   LocationMaster.is_disabled.alias('is_location_disabled'),
                                                   fn.GROUP_CONCAT(fn.DISTINCT(SlotDetails.quantity)).alias(
                                                       'quantities'),
                                                   fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('drug_qty'),
                                                   fn.SUM(SlotDetails.quantity).alias('total_qty'),
                                                   DrugMaster.ndc,
                                                   DrugMaster.formatted_ndc,
                                                   DrugMaster.txr,
                                                   DrugMaster.strength,
                                                   DrugMaster.strength_value,
                                                   DrugMaster.drug_name,
                                                   FacilityMaster.facility_name,
                                                   PackDetails.pack_display_id,
                                                   PatientMaster.last_name,
                                                   PatientMaster.first_name,
                                                   PatientMaster.patient_no,
                                                   PackHeader.patient_id,
                                                   SlotDetails.drug_id,
                                                   PatientMaster.facility_id).dicts() \
                    .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                    .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                    .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                    .join(PackDetails, on=PackAnalysis.pack_id == PackDetails.id) \
                    .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                    .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
                    .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                    .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                    .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                    .where(PackAnalysis.batch_id == batch_id,
                           PackDetails.batch_id == batch_id) \
                    .group_by(PackAnalysis.pack_id,
                              DrugMaster.formatted_ndc,
                              DrugMaster.txr) \
                    .order_by(PackDetails.order_no)
                for record in query:
                    fndc_txr = (record["formatted_ndc"], record["txr"])
                    if manual_drug_data.get(record['pack_id'], None) and manual_drug_data[record['pack_id']].get(
                            fndc_txr):
                        logger.info(
                            'drug: {} already found in mfd for pack: {}'.format(record['drug_id'], record['pack_id']))
                        continue
                    record["drug_qty"] = float(record["drug_qty"])
                    record["total_qty"] = float(record["total_qty"])

                    quantities = list(map(float, record["quantities"].split(',')))
                    fractional_quantities = [i % 1 != 0 for i in quantities]  # list of bool
                    half_pill = any(fractional_quantities)
                    if not record["canister_id"] or record["device_id"] is None or half_pill or record[
                            'is_location_disabled']:
                        if record['facility_id'] not in facility_ids:
                            facility_seq_no[record['facility_id']] = len(facility_ids) + 1
                            facility_ids.add(record['facility_id'])
                        record['facility_seq_no'] = facility_seq_no[record['facility_id']]
                        if half_pill and record["canister_id"] and record["device_id"] is not None and not record[
                                'is_location_disabled']:
                            # manual due to half pills, so consider only half pills
                            record['quantity'] = record['total_qty'] - record["drug_qty"]
                        else:
                            # manual because canister not present, all qty will be manual
                            record['quantity'] = record["total_qty"]
                        # manual drug if no canister found during analysis or fractional pill
                        manual_drug_data[record["pack_id"]][fndc_txr] = record

                response = [i for item in manual_drug_data.values() for i in item.values()]
                response = sorted(response, key=lambda each_drug: each_drug['drug_name'])
                logger.info("Manual Drugs: {} for batch_id: {}".format(response, batch_id))
            except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
                logger.error(e)
                raise
            except Exception as e:
                logger.error(e)
                raise

        return response
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def get_mfd_drug_list_(batch_id, mfs_device_id):
    try:
        drug_list = set()
        analysis_ids: list = list()
        query1 = TempMfdFilling.select(TempMfdFilling.mfd_analysis_id).dicts().where(
            TempMfdFilling.batch_id == batch_id, TempMfdFilling.mfs_device_id == mfs_device_id)
        for record in query1:
            if record['mfd_analysis_id']:
                analysis_ids.append(record['mfd_analysis_id'])
        logger.info("In get_mfd_drug_list_ {} ".format(analysis_ids))
        logger.info("In get_mfd_drug_list_ {} ".format(query1))

        # skipped_drug can not be selected for that apply the one more where clause added
        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugMaster.formatted_ndc, DrugMaster.txr,
                                  DrugMaster.brand_flag, PatientRx.daw_code).dicts() \
            .join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)\
            .where((MfdAnalysis.id << analysis_ids) &
                   (MfdAnalysisDetails.status_id != constants.MFD_DRUG_SKIPPED_STATUS))\
            .group_by(DrugMaster.id)

        for data in query:
            drug_list.add(data["ndc"])

        return query, drug_list
    except DataError as e:
        logger.error(e)
        return e


@log_args_and_response
def map_pack_location_dao(slot_row, slot_column):
    """
    Map the slot row and slot col from
    matrix index i,j to a pack location
    """
    try:

        slot_number = PackGrid.map_pack_location(row=slot_row, col=slot_column)
        return slot_number

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in map_pack_location_dao {}".format(e))
        raise e


@log_args_and_response
def check_drug_dimension_required_for_drug_id(batch_id, fndc, txr, confirmation=None):

    try:
        logger.info("Inside check_drug_dimension_required_for_drug_id")

        drug_dimension_required = False
        # count=0
        no_of_canister = 0

        logger.info(f"check_drug_dimension_required_for_drug_id, confirmation: {confirmation}")
        if not confirmation:
            query = FrequentMfdDrugs.select(FrequentMfdDrugs.status,
                                            UniqueDrug.formatted_ndc,
                                            UniqueDrug.txr,
                                            FrequentMfdDrugs.required_canister).dicts() \
                .join(UniqueDrug, on=FrequentMfdDrugs.unique_drug_id == UniqueDrug.id) \
                .where(FrequentMfdDrugs.batch_id == batch_id,
                       UniqueDrug.formatted_ndc == fndc,
                       UniqueDrug.txr == txr,
                       FrequentMfdDrugs.status == constants.PENDING_MFD_DRUD_DIMENSION_FLOW)

            logger.info(f"In check_drug_dimension_required_for_drug_id, query: {list(query)}")

            # for data in query:
            #     count += 1
            #     if data["formatted_ndc"] == fndc and data["txr"] == txr and data["status"] == constants.PENDING_MFD_DRUD_DIMENSION_FLOW:
            #         drug_dimension_required = True
            #         no_of_canister = data["required_canister"]
            #         return drug_dimension_required, count, no_of_canister
            for data in query:
                if data["formatted_ndc"] == fndc and data["txr"] == txr and data["status"] == constants.PENDING_MFD_DRUD_DIMENSION_FLOW:
                    drug_dimension_required = True
                    no_of_canister = data["required_canister"]

            return drug_dimension_required, no_of_canister

        else:
            # means confirmation = True
            # This case happen when user scan alternate drug and confirm to further process with alternate drug.
            # In this case we have to check weather alternate of scan drug are in top 5 mfd drug or not
            # top 5 mfd drug --> frequent_mfd_drugs table

            query = FrequentMfdDrugs.select(FrequentMfdDrugs).dicts() \
                    .join(UniqueDrug, on=UniqueDrug.id == FrequentMfdDrugs.unique_drug_id) \
                    .where(FrequentMfdDrugs.batch_id == batch_id,
                           UniqueDrug.txr == txr,
                           UniqueDrug.formatted_ndc != fndc)

            logger.info(
                f"In check_drug_dimension_required_for_drug_id, query to check weather alternate of scan drug are in top 5 mfd drug or not: {list(query)}")

            if query:

                # If alternate of scan drug present in frequent_mfd_drugs >> we have to insert data of this drug also
                # scanned drug shouldn't have dimensions

                count_query = MfdAnalysis.select(UniqueDrug.id.alias("unique_drug_id"), MfdAnalysis.id,
                                           fn.SUM(SlotDetails.quantity).alias("total_qty")).dicts() \
                                    .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                                    .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                                    .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                                    .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (
                                            UniqueDrug.txr == DrugMaster.txr))) \
                                    .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                                    .where(MfdAnalysis.batch_id == batch_id,
                                           DrugDimension.id.is_null(True),
                                           DrugMaster.txr == txr,
                                           DrugMaster.formatted_ndc == fndc) \
                                    .group_by(UniqueDrug.id, MfdAnalysis.id)

                logger.info(f"In check_drug_dimension_required_for_drug_id, count_query: {list(count_query)}")

                response = dict()
                for data in count_query:
                    if data["unique_drug_id"] not in response:
                        response[data["unique_drug_id"]] = data
                        response[data["unique_drug_id"]]["canister_qty"] = 1
                    else:
                        response[data["unique_drug_id"]]["total_qty"] += data["total_qty"]
                        response[data["unique_drug_id"]]["canister_qty"] += 1

                insert_dict = dict()
                for data in response.values():
                    # only one unique_drug_id data will be in response
                    insert_dict = {"unique_drug_id": data["unique_drug_id"],
                                   "quantity": data["total_qty"],
                                   "required_canister": data["canister_qty"],
                                   "batch_id": batch_id,
                                   "status": constants.PENDING_MFD_DRUD_DIMENSION_FLOW,
                                   "created_date": get_current_date_time()}

                logger.info(f"In check_drug_dimension_required_for_drug_id, insert_dict: {insert_dict}")

                if insert_dict:
                    with db.transaction():
                        status = FrequentMfdDrugs.insert(insert_dict).execute()

                        logger.info(
                            f"In check_drug_dimension_required_for_drug_id, alternate data inserted in frequent_mfd_drugs table: {status} ")

                    drug_dimension_required = True
                    no_of_canister = insert_dict["required_canister"]

                return drug_dimension_required, no_of_canister

            return drug_dimension_required, no_of_canister

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_drug_dimension_required_for_drug_id {}".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in check_drug_dimension_required_for_drug_id: {e}")
        raise e


@log_args_and_response
def check_drug_dimension_required_for_drug_id_id(batch_id, fndc, txr, confirmation=None):
    try:
        drug_dimension_required = False
        # count=0
        no_of_canister = 0

        drug_query = FrequentMfdDrugs.select(FrequentMfdDrugs.status,
                                        UniqueDrug.formatted_ndc,
                                        UniqueDrug.txr,
                                        FrequentMfdDrugs.required_canister).dicts() \
            .join(UniqueDrug, on=FrequentMfdDrugs.unique_drug_id == UniqueDrug.id) \
            .where(FrequentMfdDrugs.batch_id.is_null(True),
                   FrequentMfdDrugs.current_pack_queue == 1,
            # FrequentMfdDrugs.batch_id == batch_id,
                   UniqueDrug.formatted_ndc == fndc,
                   UniqueDrug.txr == txr)

        logger.info(f"In check_drug_dimension_required_for_drug_id_id, drug_query:{list(drug_query)}")

        # This for loop will run only one time
        for data in drug_query:
            # Means that drug is in the table but if status is other than the pending and
            # comes as alternate drug scan at that time no need to check alternate flow >> confirmation = False
            confirmation = False
            if data["formatted_ndc"] == fndc and data["txr"] == txr and data["status"] == constants.PENDING_MFD_DRUD_DIMENSION_FLOW:
                drug_dimension_required = True
                no_of_canister = data["required_canister"]

                logger.info(f"In check_drug_dimension_required_for_drug_id_id, scanned drug present in frequent_mfd_drugs with pending status")

                return drug_dimension_required, no_of_canister

        if confirmation:
            logger.info(f"In check_drug_dimension_required_for_drug_id_id, confirmation: {confirmation}")

            alternate_query = FrequentMfdDrugs.select(FrequentMfdDrugs).dicts() \
                                .join(UniqueDrug, on=UniqueDrug.id == FrequentMfdDrugs.unique_drug_id) \
                                .where(FrequentMfdDrugs.batch_id.is_null(True),
                                       # FrequentMfdDrugs.batch_id == batch_id,
                                       FrequentMfdDrugs.current_pack_queue == 1,
                                       UniqueDrug.txr == txr,
                                       UniqueDrug.formatted_ndc != fndc)

            logger.info(f"In check_drug_dimension_required_for_drug_id_id, alternate_query:{list(alternate_query)}")

            if alternate_query:

                # If alternate of scan drug present in frequent_mfd_drugs >> we have to insert data of this drug also
                # scanned drug shouldn't have dimensions

                count_query = MfdAnalysis.select(UniqueDrug.id.alias("unique_drug_id"), MfdAnalysis.id,
                                           fn.SUM(SlotDetails.quantity).alias("total_qty")).dicts() \
                                    .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                                    .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                                    .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                                    .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (
                                            UniqueDrug.txr == DrugMaster.txr))) \
                                    .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                                    .where(MfdAnalysis.batch_id == batch_id,
                                           DrugDimension.id.is_null(True),
                                           DrugMaster.txr == txr,
                                           DrugMaster.formatted_ndc == fndc) \
                                    .group_by(UniqueDrug.id, MfdAnalysis.id)

                logger.info(f"In check_drug_dimension_required_for_drug_id_id, count_query: {list(count_query)}")

                response = dict()
                for data in count_query:
                    if data["unique_drug_id"] not in response:
                        response[data["unique_drug_id"]] = data
                        response[data["unique_drug_id"]]["canister_qty"] = 1
                    else:
                        response[data["unique_drug_id"]]["total_qty"] += data["total_qty"]
                        response[data["unique_drug_id"]]["canister_qty"] += 1

                insert_dict = dict()
                for data in response.values():
                    # only one unique_drug_id data will be in response
                    insert_dict = {"unique_drug_id": data["unique_drug_id"],
                                   "quantity": data["total_qty"],
                                   "required_canister": data["canister_qty"],
                                   "batch_id": None,
                                   "status": constants.PENDING_MFD_DRUD_DIMENSION_FLOW,
                                   "created_date": get_current_date_time(),
                                   "modified_date": get_current_date_time(),
                                   "current_pack_queue": 1}

                logger.info(f"In check_drug_dimension_required_for_drug_id_id, insert_dict: {insert_dict}")

                if insert_dict:
                    with db.transaction():
                        status = FrequentMfdDrugs.insert(insert_dict).execute()

                        logger.info(
                            f"In check_drug_dimension_required_for_drug_id, alternate data inserted in frequent_mfd_drugs table: {status} ")

                    drug_dimension_required = True
                    no_of_canister = insert_dict["required_canister"]

        return drug_dimension_required, no_of_canister

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_status_in_frequent_mfd_drugs {}".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in update_status_in_frequent_mfd_drugs: {e}")
        raise e


@log_args_and_response
def update_status_in_frequent_mfd_drugs(drug_id):
    try:
        logger.info("Inside update_status_in_frequent_mfd_drugs")
        status = FrequentMfdDrugs.update(status=constants.SKIPPED_MFD_DRUG_DIMENSION_FLOW,
                                         modified_date=get_current_date_time()) \
                        .where(FrequentMfdDrugs.batch_id.is_null(True),
                               FrequentMfdDrugs.unique_drug_id == drug_id,
                               FrequentMfdDrugs.current_pack_queue == 1).execute()
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_status_in_frequent_mfd_drugs {}".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in update_status_in_frequent_mfd_drugs: {e}")
        raise e


@log_args_and_response
def populate_data_in_frequent_mfd_drugs_table(batch_id=None):
    logger.info(f"Inside populate_data_in_frequent_mfd_drugs_table, batch_id: {batch_id}")
    try:
        current_pack_queue = None
        query = MfdAnalysis.select(UniqueDrug.id.alias("unique_drug_id"), MfdAnalysis.id,
                                   fn.SUM(SlotDetails.quantity).alias("total_qty")).dicts() \
                    .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                    .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                    .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                    .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
                    .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id)

        if batch_id:
            query = query.where(MfdAnalysis.batch_id == batch_id, DrugDimension.id.is_null(True)) \
                    .group_by(UniqueDrug.id,MfdAnalysis.id)
        if not batch_id:
            current_pack_queue = 1
            #first update the previous data for pack queue from frequent mfd drug.
            status = FrequentMfdDrugs.update(current_pack_queue=0).where(FrequentMfdDrugs.batch_id.is_null(True),
                                                                         FrequentMfdDrugs.current_pack_queue == 1).execute()
            logger.info(f"In populate_data_in_frequent_mfd_drugs_table, previous data updated from frequent mfd drug. {status}")

            query = query.join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                        .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                        .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                        .where(DrugDimension.id.is_null(True)) \
                        .group_by(UniqueDrug.id, MfdAnalysis.id)

        logger.info(f"In populate_data_in_frequent_mfd_drugs_table, query: {list(query)}")
        response = dict()
        for data in query:
            if data["unique_drug_id"] not in response:
                response[data["unique_drug_id"]] = data
                response[data["unique_drug_id"]]["canister_qty"] = 1
            else:
                response[data["unique_drug_id"]]["total_qty"] += data["total_qty"]
                response[data["unique_drug_id"]]["canister_qty"] += 1

        response = sorted(response.values(), key=lambda x: x["total_qty"], reverse=True)
        insert_list = []
        # dic = {}
        logger.info(f"In populate_data_in_frequent_mfd_drugs_table, response by qty:{response}")

        for data in response[:5]:
            update_dict = {"unique_drug_id": data["unique_drug_id"],
                           "quantity": data["total_qty"],
                           "required_canister": data["canister_qty"],
                           "batch_id": batch_id,
                           "status": constants.PENDING_MFD_DRUD_DIMENSION_FLOW,
                           "created_date": get_current_date_time(),
                           "modified_date": get_current_date_time(),
                           "current_pack_queue": current_pack_queue
                           }
            # update_dict["total_canister"] = data["canister_qty"] + dic[data["id"]]
            insert_list.append(update_dict)

        logger.info(f"In populate_data_in_frequent_mfd_drugs_table,insert data in FrequentMfdDrugs --> insert_list: {insert_list}")
        if insert_list:
            with db.transaction():
                FrequentMfdDrugs.insert_many(insert_list).execute()
                logger.info(f"In populate_data_in_frequent_mfd_drugs_table, data inserted in FrequentMfdDrugs")

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in populate_data_in_frequent_mfd_drugs_table {}".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in populate_data_in_frequent_mfd_drugs_table: {e}")
        raise e



@log_args_and_response
def db_check_mfd_analysis_status(batch_id, old_template_id) -> bool:
    total_mfd_count: int = 0
    total_mfd_pending_count: int = 0
    mfd_analysis_fill_status: bool = False
    try:
        mfd_query = TemplateMaster.select(MfdAnalysis).dicts()\
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id)))\
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)\
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(MfdAnalysisDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)\
            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)\
            .where(TemplateMaster.id == old_template_id, PackDetails.batch_id == batch_id)\
            .group_by(MfdAnalysis.id)

        total_mfd_count = mfd_query.count()
        if total_mfd_count > 0:
            mfd_query = mfd_query.where(MfdAnalysis.status_id == constants.MFD_CANISTER_PENDING_STATUS)
            total_mfd_pending_count = mfd_query.count()
            if total_mfd_pending_count == total_mfd_count:
                logger.debug("MFD filling pending...")
            else:
                logger.debug("MFD filling in Progress or done...")
                mfd_analysis_fill_status = True

        return mfd_analysis_fill_status
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_mfd_drop_number(pack_list: list) -> tuple:
    """

    @param pack_list:
    @return:
    """
    pack_drop_analysis_id: dict = OrderedDict()
    pack_drop_no_dict: dict = OrderedDict()

    try:
        mfd_query = PackDetails.select(MfdAnalysisDetails.id, MfdAnalysisDetails.drop_number,
                                       PackDetails.id.alias('pack_id')).dicts()\
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)\
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(MfdAnalysisDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)\
            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)\
            .where(PackDetails.id << pack_list)\
            .order_by(MfdAnalysis.order_no, MfdAnalysisDetails.mfd_can_slot_no)

        for record in mfd_query:

            if record['pack_id'] not in pack_drop_no_dict.keys():
                pack_drop_no_dict[record['pack_id']] = list()
                pack_drop_analysis_id[record['pack_id']] = dict()

            if record['drop_number'] not in pack_drop_no_dict[record['pack_id']]:
                pack_drop_analysis_id[record['pack_id']][record['drop_number']] = list()
                pack_drop_no_dict[record['pack_id']].append(record['drop_number'])

            pack_drop_analysis_id[record['pack_id']][record['drop_number']].append(record['id'])

        return pack_drop_analysis_id, pack_drop_no_dict

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_mfd_drop_number {}".format(e))
        raise


@log_args_and_response
def update_drop_number_in_mfd_analysis_details(analysis_id_drop_dict: dict):
    """

    @param analysis_id_drop_dict:
    @return:
    """
    try:
        for analysis_id, drop_no in analysis_id_drop_dict.items():
            update_query = MfdAnalysisDetails.update(drop_number=drop_no)\
                            .where(MfdAnalysisDetails.id == analysis_id).execute()

        return True

    except (InternalError, IntegrityError, DoesNotExist, ValueError) as e:
        logger.error("error in update_drop_number_in_mfd_analysis_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drop_number_in_mfd_analysis_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in update_drop_number_in_mfd_analysis_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drop_number_in_mfd_analysis_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def db_update_mfd_analysis_details_by_status(mfd_analysis_details_pending_status_ids1,
                                         mfd_analysis_details_complete_status_ids1,
                                             mfd_analysis_details_pending_status_ids2,
                                         mfd_analysis_details_complete_status_ids2, batch_id):
    try:
        subquery = ""

        mfd_analysis_details_updated_status = list()
        mfd_analysis_id_list = list()

        if batch_id:
            subquery = MfdAnalysis.select(MfdAnalysis.id.alias("MFD_analysis_id")).where(MfdAnalysis.batch_id << batch_id)

        subquery1 = MfdAnalysis.select(MfdAnalysis.id.alias("mfd_analysis_id"),
                                       MfdAnalysisDetails.id.alias("mfd_analysis_details_id"),
                                       MfdAnalysisDetails.status_id.alias("mfd_analysis_details_old_status")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .where((MfdAnalysisDetails.status_id.in_(mfd_analysis_details_pending_status_ids1)) |
                   (MfdAnalysisDetails.status_id.in_(mfd_analysis_details_pending_status_ids2)),
                   MfdAnalysis.batch_id.not_in(batch_id)
                   ).order_by(MfdAnalysis.id)

        for record in subquery1:
            mfd_analysis_details_updated_status.append(record)
            mfd_analysis_id_list.append(record["mfd_analysis_details_id"])

        new_seq_tuple1 = list(
                tuple(zip(map(str, mfd_analysis_details_pending_status_ids1), map(str, mfd_analysis_details_complete_status_ids1))))
        case_sequence1 = case(MfdAnalysisDetails.status_id, new_seq_tuple1)

        new_seq_tuple2 = list(
            tuple(zip(map(str, mfd_analysis_details_pending_status_ids2),
                      map(str, mfd_analysis_details_complete_status_ids2))))
        case_sequence2 = case(MfdAnalysisDetails.status_id, new_seq_tuple2)

        subquery2 = MfdAnalysis.select(MfdAnalysis.id.alias("mfd_analysis_ids")).where(
            MfdAnalysis.status_id == src.constants.MFD_CANISTER_MVS_FILLED_STATUS)

        query1 = MfdAnalysisDetails.update(status_id=case_sequence1) \
            .where(
                MfdAnalysisDetails.status_id.in_(mfd_analysis_details_pending_status_ids1) &
                (MfdAnalysisDetails.analysis_id.not_in(subquery2) & MfdAnalysisDetails.status_id !=
                 src.constants.MFD_DRUG_RTS_REQUIRED_STATUS))

        if subquery:
            query1 = query1.where(MfdAnalysisDetails.analysis_id.not_in(subquery))

        status1 = query1.execute()

        query2 = MfdAnalysisDetails.update(status_id=case_sequence2) \
            .where(
            MfdAnalysisDetails.status_id.in_(mfd_analysis_details_pending_status_ids2) &
            MfdAnalysisDetails.analysis_id << subquery2 & MfdAnalysisDetails.status_id ==
                 src.constants.MFD_DRUG_RTS_REQUIRED_STATUS)

        if subquery:
            query2 = query2.where(MfdAnalysisDetails.analysis_id.not_in(subquery))

        status2 = query2.execute()

        status = status1 + status2

        if subquery1:
            select_query = MfdAnalysisDetails.select(MfdAnalysisDetails.analysis_id.alias("mfd_analysis_id"),
                                                 MfdAnalysisDetails.status_id.alias("mfd_analysis_details_new_status")).dicts() \
            .where(MfdAnalysisDetails.id.in_(mfd_analysis_id_list)).order_by(MfdAnalysisDetails.analysis_id)

            if select_query:
                for record, i in zip(select_query, mfd_analysis_details_updated_status):
                    i["mfd_analysis_details_new_status"] = record["mfd_analysis_details_new_status"]

        return status, mfd_analysis_details_updated_status
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_temp_mfd_filling_details():
    """

    @param
    @return:
    """
    try:
        DestLocationMaster = LocationMaster.alias()
        DestDeviceMaster = DeviceMaster.alias()
        source_device_id = 0
        mfd_query = TempMfdFilling.select(DeviceMaster.system_id.alias("source_system_id"),
                                          DeviceMaster.device_type_id.alias("source_device_type_id"),
                                          DeviceMaster.id.alias('source_device_id'),
                                          LocationMaster.id.alias("source_location_id"),
                                          LocationMaster.container_id.alias("source_drawer_id"),
                                          DestDeviceMaster.system_id.alias("dest_system_id"),
                                          DestDeviceMaster.device_type_id.alias("dest_device_type_id"),
                                          DestDeviceMaster.id.alias("dest_device_id"),
                                          DestLocationMaster.container_id.alias("dest_drawer_id"),
                                          DestLocationMaster.display_location.alias("dest_display_location"),
                                          DestLocationMaster.id.alias("dest_location_id"),
                                          ContainerMaster.serial_number.alias("drawer_serial_number")
                                          ).dicts()\
            .join(MfdAnalysis, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id)\
            .join(LocationMaster, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id)\
            .join(DestDeviceMaster, on=DestDeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .join(DestLocationMaster, on=(DestLocationMaster.location_number == MfdAnalysis.mfs_location_number) &
                                         (MfdAnalysis.mfs_device_id == DestLocationMaster.device_id))\
            .where(MfdAnalysis.mfd_canister_id.is_null(True))

        temp_mfd_data = list()
        for record in mfd_query.dicts():
            source_device_id = record["source_device_id"]
            temp_mfd_data.append(record)

        return temp_mfd_data, source_device_id

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_mfd_drop_number {}".format(e))
        raise


def db_get_mfd_analysis_filled_canister_details(trolley_seq_number, dest_device_id):
    """

    @param
    @return:
    """
    try:
        DestLocationMaster = LocationMaster.alias()
        DestDeviceMaster = DeviceMaster.alias()
        source_device_id = 0
        mfd_query = MfdAnalysis.select(MfdAnalysis.batch_id.alias("batch_id"),
                                          MfdAnalysis.mfd_canister_id.alias('source_canister_rfid'),
                                          MfdAnalysis.mfd_canister_id.alias('source_canister_id'),
                                          MfdCanisterMaster.rfid.alias("source_canister_rfid"),
                                          DeviceMaster.system_id.alias("source_system_id"),
                                          DeviceMaster.device_type_id.alias("source_device_type_id"),
                                          DeviceMaster.id.alias('source_device_id'),
                                          LocationMaster.id.alias("source_location_id"),
                                          LocationMaster.container_id.alias("source_drawer_id"),
                                          DestDeviceMaster.system_id.alias("dest_system_id"),
                                          DestDeviceMaster.device_type_id.alias("dest_device_type_id"),
                                          DestDeviceMaster.id.alias("dest_device_id"),
                                          MfdAnalysis.dest_quadrant.alias("dest_quadrant"),
                                          MfdAnalysis.trolley_seq.alias("trolley_sequence"),
                                          DeviceMaster.serial_number.alias("trolley_serial_number"),
                                          ContainerMaster.serial_number.alias("drawer_serial_number")
                                          ).dicts() \
            .join(MfdCanisterMaster, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
            .join(LocationMaster, on=MfdAnalysis.trolley_location_id == LocationMaster.id)\
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id)\
            .join(DestDeviceMaster, on=DestDeviceMaster.id == MfdAnalysis.dest_device_id) \
            .where(MfdAnalysis.status_id == 66, MfdAnalysis.trolley_seq == trolley_seq_number,
                   DestDeviceMaster.id == dest_device_id)

        temp_mfd_data = list()
        for record in mfd_query.dicts():
            source_device_id = record["source_device_id"]
            temp_mfd_data.append(record)

        return temp_mfd_data, source_device_id

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_mfd_drop_number {}".format(e))
        raise


@log_args_and_response
def db_update_mfd_analysis_by_status_by_mfd_cart_device_id(mfd_analysis_pending_status_ids,
                                                                           mfd_analysis_complete_status_ids,
                                                               mfd_cart_device_id):
    try:
        new_seq_tuple = list(tuple(zip(map(str, mfd_analysis_pending_status_ids), map(str, mfd_analysis_complete_status_ids))))
        case_sequence = case(MfdAnalysis.status_id, new_seq_tuple)

        mfd_analysis_updated_status = list()
        mfd_analysis_id_list = list()

        subquery = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id')) \
            .where(MfdCanisterMaster.home_cart_id == mfd_cart_device_id)

        query1 = MfdAnalysis.select(MfdAnalysis.id.alias("mfd_analysis_id"),
                                    MfdAnalysis.status_id.alias("mfd_analysis_old_status")).dicts() \
            .where(MfdAnalysis.status_id.in_(mfd_analysis_pending_status_ids),
                   MfdAnalysis.mfd_canister_id << subquery).order_by(MfdAnalysis.id)

        for record in query1:
            mfd_analysis_updated_status.append(record)
            mfd_analysis_id_list.append(record["mfd_analysis_id"])

        query = MfdAnalysis.update(status_id=case_sequence) \
            .where(MfdAnalysis.status_id.in_(mfd_analysis_pending_status_ids), MfdAnalysis.mfd_canister_id << subquery)

        status = query.execute()

        if len(query1) != 0:
            select_query = MfdAnalysis.select(MfdAnalysis.id.alias("mfd_analysis_id"),
                                      MfdAnalysis.status_id.alias("mfd_analysis_new_status")).dicts() \
                .where(MfdAnalysis.id.in_(mfd_analysis_id_list)).order_by(MfdAnalysis.id)

            if select_query:
                for record, i in zip(select_query, mfd_analysis_updated_status):
                    i["mfd_analysis_new_status"] = record["mfd_analysis_new_status"]

        return status, mfd_analysis_updated_status
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_mfd_analysis_details_by_status_by_mfd_cart_device_id(mfd_analysis_details_pending_status_ids,
                                         mfd_analysis_details_complete_status_ids, mfd_cart_device_id):
    try:
        mfd_analysis_details_updated_status = list()
        mfd_analysis_id_list = list()

        new_seq_tuple = list(
                tuple(zip(map(str, mfd_analysis_details_pending_status_ids), map(str, mfd_analysis_details_complete_status_ids))))
        case_sequence = case(MfdAnalysisDetails.status_id, new_seq_tuple)

        subquery = MfdAnalysis.select(MfdAnalysis.id.alias("mfd_analysis_id"))\
            .join(MfdCanisterMaster, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
            .where(MfdCanisterMaster.home_cart_id == mfd_cart_device_id)

        subquery1 = MfdAnalysis.select(MfdAnalysis.id.alias("mfd_analysis_id"),
                                       MfdAnalysisDetails.status_id.alias("mfd_analysis_details_old_status")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .where(MfdAnalysisDetails.status_id.in_(mfd_analysis_details_pending_status_ids),
                   MfdAnalysis.id << subquery
                   ).order_by(MfdAnalysis.id)

        for record in subquery1:
            mfd_analysis_details_updated_status.append(record)
            mfd_analysis_id_list.append(record["mfd_analysis_id"])

        query = MfdAnalysisDetails.update(status_id=case_sequence) \
               .where(MfdAnalysisDetails.status_id.in_(mfd_analysis_details_pending_status_ids),
                      MfdAnalysisDetails.analysis_id << subquery)
        status = query.execute()

        if subquery1:
            select_query = MfdAnalysisDetails.select(MfdAnalysisDetails.analysis_id.alias("mfd_analysis_id"),
                                                     MfdAnalysisDetails.status_id.alias(
                                                         "mfd_analysis_details_new_status")).dicts() \
                .where(MfdAnalysisDetails.analysis_id.in_(mfd_analysis_id_list)).order_by(
                MfdAnalysisDetails.analysis_id)

            if select_query:
                for record, i in zip(select_query, mfd_analysis_details_updated_status):
                    i["mfd_analysis_details_new_status"] = record["mfd_analysis_details_new_status"]

        return status, mfd_analysis_details_updated_status
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_temp_mfd_filling_details_for_mfs_to_cart():
    """

    @param
    @return:
    """
    try:
        SourceLocationMaster = LocationMaster.alias()
        SourceDeviceMaster = DeviceMaster.alias()
        source_device_id = 0
        mfd_query = TempMfdFilling.select(SourceDeviceMaster.system_id.alias("source_system_id"),
                                          SourceDeviceMaster.device_type_id.alias("source_device_type_id"),
                                          SourceDeviceMaster.id.alias("source_device_id"),
                                          SourceLocationMaster.container_id.alias("source_drawer_id"),
                                          SourceLocationMaster.id.alias("source_location_id"),
                                          DeviceMaster.system_id.alias("destination_system_id"),
                                          DeviceMaster.id.alias("trolley_device_id"),
                                          LocationMaster.id.alias("trolley_location_id"),
                                          DeviceMaster.serial_number.alias("trolley_serial_number"),
                                          MfdCanisterMaster.rfid.alias("source_canister_rfid"),
                                          MfdCanisterMaster.id.alias("mfd_canister_id"),
                                          MfdAnalysis.batch_id,
                                          ContainerMaster.serial_number.alias("drawer_id")
                                          ).dicts() \
            .join(MfdAnalysis, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(LocationMaster, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(SourceDeviceMaster, on=SourceDeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .join(SourceLocationMaster, on=(SourceLocationMaster.location_number == MfdAnalysis.mfs_location_number) &
                                         (MfdAnalysis.mfs_device_id == SourceLocationMaster.device_id)) \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id)\
            .where(TempMfdFilling.transfer_done == 0)

        temp_mfd_data = list()
        for record in mfd_query.dicts():
            source_device_id = record["source_device_id"]
            temp_mfd_data.append(record)

        return temp_mfd_data, source_device_id

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_mfd_drop_number {}".format(e))
        raise


@log_args_and_response
def check_and_update_mfd_module_for_all_batch_mfd_skipped_couch_db(batch_id, system_id):
    try:
        reset_couch_db = False

        pending_canisters = check_pending_mfd_canister_count(batch_id)
        logger.info("canister_pending_count for batch_id {} is: {}"
                    .format(batch_id, pending_canisters))
        if not pending_canisters:
            reset_couch_db = True
            logger.info('No pending canister found for current batch: marking batch done: ' + str(batch_id))
            batch_status = db_update_mfd_status(batch=batch_id, mfd_status=constants.MFD_BATCH_FILLED, user_id=1)
            logger.info('updated_mfd_batch_status: {}'.format(batch_status))

            module_data = {
                'batch_id': 0,
                'trolley_scanned': False,
                'current_module': constants.MFD_MODULES["SCHEDULED_BATCH"]
            }
            logger.info('couch_db_module_reset: {}'.format(module_data))
            status, doc = update_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID, system_id,
                                                     module_data)

        return reset_couch_db

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in check_and_udpate_mfd_module_for_all_batch_mfd_skipped_couch_db {}".format(e))
        raise


@log_args_and_response
def check_pending_mfd_canister_count(batch_id):
    """
    returns count of canisters on which actions are required weather filling pending or if filled/skipped needs to be put
    in trolley
    :param batch_id: int
    :param user_id: int
    :param trolley_id: int
    :return: int
    """
    LocationMasterAlias = LocationMaster.alias()
    try:
        pending_count = MfdAnalysis.select().dicts() \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMasterAlias.id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .where(MfdAnalysis.batch_id == batch_id)

        pending_count = pending_count.where((MfdAnalysis.status_id << [constants.MFD_CANISTER_PENDING_STATUS])).count()
        return pending_count
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_temp_mfd_filling_drug_details():
    """

    @param
    @return:
    """
    try:
        mfd_query = TempMfdFilling.select(fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.id)).alias("analysis_ids_updated"),
            DrugMaster.ndc, DrugMaster.id.alias("drug_id"),
                                          MfdAnalysis.batch_id,
                                          MfdAnalysis.mfs_device_id,
                                          DeviceMaster.system_id
                                          ).dicts()\
            .join(MfdAnalysis, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(DeviceMaster, on=DeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .where(MfdAnalysisDetails.status_id != 61) \
            .group_by(DrugMaster.ndc)

        temp_mfd_data = list()
        temp_mfd_dict = mfd_query.dicts()
        for record in mfd_query.dicts():
            temp_mfd_data.append(record)

        return temp_mfd_data

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_mfd_drop_number {}".format(e))
        raise


@log_args_and_response
def db_get_temp_mfd_filled_drug_details():
    """

    @param
    @return:
    """
    try:
        mfd_query = TempMfdFilling.select(fn.GROUP_CONCAT(fn.DISTINCT(DrugMaster.ndc)).alias("mfs_filled_drug")).dicts() \
            .join(MfdAnalysis, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id).dicts() \
            .where(MfdAnalysisDetails.status_id == 61)

        mfs_filled_drug = list()
        for record in mfd_query:
            mfs_filled_drug.append(record["mfs_filled_drug"])

        return mfs_filled_drug

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return dict(), dict()
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_mfd_drop_number {}".format(e))
        raise


@log_args_and_response
def get_mfd_analysis_data_by_batch(batch_id):
    record = list
    try:
        query = MfdAnalysis.select().dicts().where(MfdAnalysis.batch_id == batch_id).order_by(MfdAnalysis.trolley_seq)
        record = [data for data in query]
        return record
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_mfd_analysis_data_by_batch {}".format(e))
        raise e


@log_args_and_response
def update_trolley_seq_and_merge(analysis_update_dict):
    try:

        with db.transaction():
            for analysis_id, update_dict in analysis_update_dict.items():
                query = MfdAnalysis.update(**update_dict).where(MfdAnalysis.id == analysis_id).execute()

        return True
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in update_trolley_seq_and_merge {}".format(e))
        raise e


@log_args_and_response
def db_get_all_mfd_packs_from_packlist(pack_list, patient_id_list):
    """
    Function to get list mfd packs for given batch
    @param pack_list:
    @return: list
        Sample Output = ['mfd_pack':1, 'mfd_pack':2]
    """
    all_mfd_packs = []
    extra_packs = []
    analysis_pack_dict =  {}
    cannot_change_pack = []
    pack_mfd_status_dict = {}
    pack_data = {}
    try:
        mfd_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        all_patient_mfd_packs = MfdAnalysis.select(MfdAnalysisDetails.analysis_id, PackDetails.id,
                                                   MfdAnalysis.transferred_location_id, MfdAnalysis.status_id,
                                                   PackDetails.pack_display_id,
                                                   fn.CONCAT(PackDetails.consumption_start_date, ' to ',
                                                             PackDetails.consumption_end_date).alias(
                                                       "admin_period"),
                                                   PackHeader.scheduled_delivery_date.alias("delivery_date"),
                                                   PatientMaster.concated_patient_name_field().alias("patient_name")
                                                   ).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id) \
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
            .where(PatientRx.patient_id << patient_id_list,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   MfdAnalysis.status_id << mfd_canister_status) \
            .group_by(MfdAnalysis.id) \
            .order_by(PackDetails.order_no)

        for record in all_patient_mfd_packs:
            analysis_id = record['analysis_id']
            transferred_location_id = record['transferred_location_id']
            pack_id = record['id']
            status_id = record['status_id']
            if transferred_location_id:
                cannot_change_pack.append(pack_id)
                # continue
            if analysis_id not in analysis_pack_dict:
                analysis_pack_dict[analysis_id] = [pack_id]
            else:
                analysis_pack_dict[analysis_id].append(pack_id)

            mfd_status = record["status_id"]
            # get_pack_data
            if pack_id not in pack_data:
                pack_data[pack_id] = {
                    "patient_name": record['patient_name'],
                    "delivery_date": record['delivery_date'],
                    "admin_period": record['admin_period'],
                    "canister_count": 1,
                    "pack_display_id": record['pack_display_id'],
                    "pack_id": pack_id,
                    "mfd_status": record['status_id']
                }
            else:
                pack_data[pack_id]["canister_count"] += 1
                if mfd_status == constants.MFD_CANISTER_PENDING_STATUS:
                    if pack_data[pack_id]["mfd_status"] != constants.MFD_CANISTER_PENDING_STATUS:
                        pack_data[pack_id]["mfd_status"] = mfd_status
                elif pack_data[pack_id]["mfd_status"]  == constants.MFD_CANISTER_SKIPPED_STATUS and mfd_status == constants.MFD_CANISTER_FILLED_STATUS:
                    pack_data[pack_id]["mfd_status"] = mfd_status


        for analysis_id, packs in analysis_pack_dict.items():
            if len(packs) > 1:
                for pack in packs:
                    all_mfd_packs.append(pack)
                    if not pack in pack_list:
                        extra_packs.append(pack)

            elif packs[0] in pack_list:
                all_mfd_packs.append(packs[0])

        all_mfd_packs = list(set(all_mfd_packs))
        extra_packs = list(set(extra_packs))
        pack_list += extra_packs
        copy_pack_data = deepcopy(pack_data)
        for pack in copy_pack_data:
            if pack not in all_mfd_packs:
                del pack_data[pack]

        return all_mfd_packs, extra_packs, pack_list, list(set(cannot_change_pack)),pack_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_queue_mfd_packs(system_id):
    """
    Function to get list mfd packs for given batch
    @return: list
        Sample Output = ['mfd_pack':1, 'mfd_pack':2]
    """
    try:
        mfd_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        query = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id)).alias('mfd_pack'),
                                   BatchMaster.system_id,
                                   fn.DATE(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   PackDetails.system_id == system_id,
                   MfdAnalysis.status_id << mfd_canister_status) \
            .group_by(PackRxLink.pack_id) \
            .order_by(fn.MIN(MfdAnalysis.order_no), fn.MIN(MfdAnalysisDetails.mfd_can_slot_no))

        return list(query)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return None



@log_args_and_response
def skip_mfd_for_packs(mfd_pack_sequence, user_id):

    skip_id_list = []
    skip_details_id_list = []
    manual_filling_id = []
    manual_details_filling_id = []
    try:
        mfd_analysis = MfdAnalysis.select(MfdAnalysisDetails.analysis_id,  MfdAnalysis.status_id.alias("analysis_status"), MfdAnalysisDetails.id).dicts() \
                .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .where(PackRxLink.pack_id << mfd_pack_sequence)

        for record in mfd_analysis:
            if record['analysis_status'] == constants.MFD_CANISTER_PENDING_STATUS:
                skip_id_list.append(record['analysis_id'])
                skip_details_id_list.append(record['id'])
            if record['analysis_status'] in [constants.MFD_CANISTER_FILLED_STATUS, constants.MFD_CANISTER_VERIFIED_STATUS]:
                manual_filling_id.append(record['analysis_id'])
                manual_details_filling_id.append(record['id'])
        if skip_id_list:
            status = db_update_canister_status(skip_id_list, constants.MFD_CANISTER_SKIPPED_STATUS, user_id)
            status = db_update_drug_status(list(skip_details_id_list), constants.MFD_DRUG_SKIPPED_STATUS)

            if status:
                update_mfd_couch_db_notification(analysis_id=skip_id_list, user_id=user_id)
        if manual_filling_id:
            status = db_update_canister_status(manual_filling_id, constants.MFD_CANISTER_MVS_FILLING_REQUIRED, user_id)

            if status:
                update_mfd_couch_db_notification(analysis_id=manual_filling_id, user_id=user_id)

        # status = db_update_drug_status(list(manual_details_filling_id), constants.MFD_DRUG_RTS_REQUIRED_STATUS)

        return True

    except (InternalError, IntegrityError, DoesNotExist, ValueError) as e:
        logger.error("error in skip_mfd_for_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in skip_mfd_for_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in skip_mfd_for_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in skip_mfd_for_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def change_mfd_trolley_sequence(analysis_ids, new_seq_tuple, trolley_mfd_dict, updated_seq, user_id):
    """
    Function to updated pack sequence
    @param analysis_ids: list
    @param order_number_list: list
    @return: status
    """
    try:
        case_sequence = case(MfdAnalysis.id, new_seq_tuple)
        logger.info("In PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: new_seq_tuple: {}".format(new_seq_tuple))
        logger.info("In PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: case_sequence: {}".format(case_sequence))

        # update order number in table
        order_no_status = MfdAnalysis.db_change_mfd_order_no(case_sequence=case_sequence, mfd_analysis_ids=analysis_ids,
                                                             user_id=user_id)
        logger.info("In PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: order_no is updated in pack details table: {}".format(
            order_no_status))
        # return order_no_status

        for old, new in updated_seq:
            analysis_ids = trolley_mfd_dict[old]
            logger.info(
                "In PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: updating analysis_ids {} with trolley_seq: {}".format(
                    analysis_ids, new))
            seq_update = MfdAnalysis.update_trolley_seq_by_analysis_id(analysis_ids, new)

        return True
    except (InternalError, IntegrityError, DoesNotExist, ValueError) as e:
        logger.error("error in change_mfd_trolley_sequence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in change_mfd_trolley_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in change_mfd_trolley_sequence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in change_pack_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def db_get_last_order_no_trolley_seq_no_of_given_batch(batch_id: int):
    """
    get query to get last order no., trolley_seq of imported batch
    @param batch_id:
    """
    try:
        mfd_analysis_data = list()
        query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias("last_order_no"),
                                   fn.MAX(MfdAnalysis.trolley_seq).alias("last_trolley_seq")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.batch_id == batch_id, PackDetails.previous_batch_id.is_null(True))

        for record in query:
            mfd_analysis_data.append(record)
        return mfd_analysis_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_first_order_no_trolley_seq_no_of_given_batches(batch_ids: list):
    """
    get query to get first order no., first trolley seq and merged (previous) batch_id of given batch
    @param batch_ids:
    """
    try:
        mfd_analysis_data = list()
        query = MfdAnalysis.select(fn.MIN(MfdAnalysis.order_no).alias("first_order_no"),
                                   fn.MIN(MfdAnalysis.trolley_seq).alias("first_trolley_seq"),
                                   PackDetails.previous_batch_id.alias("merged_batch_id")
                                   ).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.previous_batch_id << batch_ids).group_by(PackDetails.previous_batch_id)

        for record in query:
            mfd_analysis_data.append(record)
        return mfd_analysis_data
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_last_order_no_trolley_seq_no_of_given_batches(batch_id: int):
    """
    get query to get last order no. of imported batch
    @param batch_id:
    """
    try:
        mfd_analysis_data = list()
        query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias("last_order_no"),
                                   fn.MAX(MfdAnalysis.trolley_seq).alias("last_trolley_seq"),
                                   PackDetails.previous_batch_id.alias("merged_batch_id")
                                   ).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.previous_batch_id << batch_id).group_by(PackDetails.previous_batch_id)

        for record in query:
            mfd_analysis_data.append(record)
        return mfd_analysis_data
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def db_get_merged_pack_mfd_canister_status(merged_pack_ids):
    """
    @param merged_pack_ids:
    """
    try:
        merged_pack_mfd_canister_details = list()
        query = MfdAnalysis.select(MfdAnalysis.status.alias("mfd_canister_status"),
                                   PackDetails.id.alias("pack_id"), MfdAnalysis.id.alias("mfd_analysis_id")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.pack_status == 2, PackDetails.order_no != 0, PackDetails.id.not_in(merged_pack_ids),
                   MfdAnalysis.status.not_in(src.constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                             src.constants.MFD_CANISTER_MVS_FILLING_REQUIRED))
        for record in query:
            merged_pack_mfd_canister_details.append(record)
        return merged_pack_mfd_canister_details
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def db_get_min_pack_sequence_of_given_batch_id(batch_id):
    """
    get query to get last merged pending pack order no., pack id and pack status
    @param batch_id:
    """
    try:
        pack_sequence_details = list()
        query = MfdAnalysis.select(fn.MIN(PackDetails.pack_sequence).alias("min_pack_sequence"),
                                   MfdAnalysis.trolley_seq.alias("trolley_seq")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.order_no != 0, PackDetails.batch_id == batch_id).group_by(MfdAnalysis.trolley_seq)
        for record in query:
            pack_sequence_details.append(record)
        return pack_sequence_details
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_trolley_seq_fill_status(trolley_seq, batch_id):

    pending = False
    try:
        query = MfdAnalysis.select(fn.COUNT(MfdAnalysis.id)).where(MfdAnalysis.batch_id == batch_id,
                                                         MfdAnalysis.trolley_seq == trolley_seq,
                                                         MfdAnalysis.status_id << [
                                                             constants.MFD_CANISTER_PENDING_STATUS]).scalar()
        if query:
            pending = True
        return pending
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return pending
    except Exception as e:
        logger.error(e, exc_info=True)
        return pending


@log_args_and_response
def remove_trolley_location(trolley_seqs: list) -> int:
    """

    """
    past_data = []
    analysis_ids = []
    batch_id = None
    try:
        #get_past_data_for_logs
        past_data_query = MfdAnalysis.select(MfdAnalysis.id, MfdAnalysis.trolley_seq, MfdAnalysis.trolley_location_id, MfdAnalysis.batch_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(MfdAnalysis.trolley_seq << trolley_seqs)

        for data in past_data_query:
            past_data.append(data)
            analysis_ids.append(data['id'])
            batch_id = data['batch_id']

        logger.info("In remove_trolley_location: past_data = {}".format(past_data))

        loc_status = MfdAnalysis.update(trolley_location_id=None).where(
            MfdAnalysis.id << analysis_ids).execute()

        if loc_status:
            return batch_id
        else:
            return loc_status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_pack_status(template):
    """
    @param merged_pack_ids:
    """
    mfd_status_list = []
    try:

        query = MfdAnalysis.select(MfdAnalysis.status_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(TemplateMaster, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id))) \
            .where(TemplateMaster.id == template).group_by(MfdAnalysis.status_id)
        for record in query:
            mfd_status_list.append(record['status_id'])
        return mfd_status_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_trolley_data(analysis_id):
    try:
        logger.info("In get_trolley_data")
        trolley_data_dict = dict()
        batch_id = None
        query = MfdAnalysis.select(MfdAnalysis.trolley_seq, DeviceMaster.id.alias('trolley_id'), MfdAnalysis.batch_id).dicts() \
                            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
                            .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                            .where(MfdAnalysis.id << analysis_id) \
                            .group_by(MfdAnalysis.trolley_seq)

        for record in query:
            batch_id = record['batch_id']
            trolley_data_dict[record['trolley_seq']] = record['trolley_id']

        return trolley_data_dict, batch_id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_device_id_list_from_trolley_data(trolley_id, trolley_seq, batch_id):
    try:
        logger.info("In get_device_id_list_from_trolley_data")
        query = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.dest_device_id)).alias('device_id')).dicts() \
                            .where(MfdAnalysis.trolley_seq==trolley_seq, MfdAnalysis.batch_id==batch_id) \
                            .group_by(MfdAnalysis.trolley_seq)

        for record in query:
            return list(map(int, record['device_id'].split(',')))

        return None

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_device_name_from_device(device_id_list: list):
    try:
        robot_data = DeviceMaster.db_get_device_name_from_device(device_id_list=device_id_list)
        return robot_data
    except(IntegrityError, InternalError) as e:
        logger.error("Error in get_device_name_from_device".format(e))
        raise


@log_args_and_response
def get_system_id_by_device_id_dao(device_id):
    try:
        system_id = DeviceMaster.db_get_system_id_by_device_id(device_id)
        return system_id
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_system_id_by_device_id_dao".format(e))
        raise


@log_args_and_response
def db_get_next_trolley(batch_id, device_id=None):
    """
    returns count of canisters currently placed on mfs
    in trolley
    :param batch_id: int
    :param device_id: int
    :return: int
    """
    # same as function in mfd_canister_dao
    try:
        query = MfdAnalysis.select(LocationMaster.device_id,
                                   DeviceMaster.name,
                                   BatchMaster.system_id,
                                   MfdAnalysis.trolley_seq).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_SKIPPED_STATUS,
                                                 constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                 constants.MFD_CANISTER_DROPPED_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                 constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                 constants.MFD_CANISTER_RTS_REQUIRED_STATUS]),
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])
        if device_id:
            query = query.where(MfdAnalysis.dest_device_id == device_id)

        query = query.order_by(MfdAnalysis.order_no).group_by(LocationMaster.device_id).get()

        next_trolley = query['device_id']
        next_trolley_name = query['name']
        system_id = query['system_id']
        next_trolley_seq = query['trolley_seq']
        logger.info("db_get_next_trolley Input {} {} and output {} {} {}".format(batch_id, device_id, next_trolley,
                                                                                  system_id, next_trolley_name))
        return next_trolley, system_id, next_trolley_name, next_trolley_seq

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None, None, None, None

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def remove_notifications_for_skipped_mfs_filling(system_id, device_id, unique_id=None, user_id=None, update_all=False,
                                                 remove_action_taken_by=False):
    # same function in mfd.py
    try:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'mfd_notifications_{}'.format(device_id)
        logger.info("notification_document_name: " + str(id))
        table = cdb.get(_id=id)
        if table is not None:
            data = table.get("data", {})
            if data:
                notification_data = table["data"].get("notification_data")
                if notification_data:
                    notifications_list = list()
                    if not update_all:
                        for record in notification_data:
                            if 'unique_id' in record:
                                if unique_id == record['unique_id']:
                                    if not remove_action_taken_by:
                                        record['action_taken_by'] = user_id
                                    else:
                                        record['action_taken_by'] = None
                            notifications_list.append(record)
                    else:
                        for data in notification_data:
                            data['action_taken_by'] = user_id
                            notifications_list.append(data)
                    table['data']['notification_data'] = notifications_list
                    logger.info("In remove_notifications_for_skipped_mfs_filling: notification_data {}".format(notifications_list))
                    cdb.save(table)
    except Exception as e:
        logger.error(e)
        logger.error("Error in remove_notifications_for_skipped_mfs_filling: {}".format(e))
        raise e


@log_args_and_response
def update_mfd_couch_db_notification(user_id, analysis_id=None, batch_id=None):
    """
        removes notification for current mfd trolley and adds new notifications for next trolley in couchdb
    """

    try:
        logger.info("In update_mfd_couch_db_notification")
        skip_for_all_devices = False
        trolley_data_dict, batch_id = get_trolley_data(analysis_id=analysis_id)
        mfd_canister_status = [constants.MFD_CANISTER_SKIPPED_STATUS,
                               constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                               constants.MFD_CANISTER_RTS_REQUIRED_STATUS]
        next_trolley_devices = set()
        for trolley_seq, trolley_id in trolley_data_dict.items():
            device_id_list = get_device_id_list_from_trolley_data(trolley_id, trolley_seq, batch_id)
            skip_for_all_devices, skip_for_devices_dict = db_check_entire_mfd_trolley_skipped(batch_id,
                                                                                              trolley_id,
                                                                                              trolley_seq,
                                                                                              device_id_list=device_id_list,
                                                                                              mfd_canister_status=mfd_canister_status)
            if skip_for_devices_dict:
                dest_device_system_id = get_system_id_by_device_id_dao(device_id_list[0])
                for device_id in device_id_list:
                    if skip_for_devices_dict[device_id]:
                        next_trolley_devices.add(device_id)
                        if trolley_id:
                            unique_id = int(str(trolley_id) + str(trolley_seq) + str(device_id))
                            remove_notifications_for_skipped_mfs_filling(system_id=dest_device_system_id,
                                                                         unique_id=unique_id,
                                                                         device_id=device_id,
                                                                         user_id=user_id)

        if skip_for_all_devices:
            device_list = list()
            system_device_dict = get_robots_by_systems_dao([dest_device_system_id])
            for system, robot_data in system_device_dict.items():
                for device_data in robot_data:
                    device_list.append(device_data['id'])
            next_trolley_devices.update(set(device_list))

        logger.info("In update_mfd_couch_db_notification: next_trolley_devices: {}".format(next_trolley_devices))

        for device_id in list(next_trolley_devices):
            device_message = dict()
            next_trolley, system_id, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id,
                                                                                               device_id)
            if next_trolley and next_trolley_seq and device_id:
                unique_id = int(str(next_trolley) + str(next_trolley_seq) + str(device_id))
                notification_present = Notifications().check_if_notification_is_present(unique_id,
                                                                                        device_id,
                                                                                        dest_device_system_id,
                                                                                        batch_id)
                logger.info("In update_mfd_couch_db_notification notification_present: {}".format(notification_present))
                # update only if notification is not present.
                if not notification_present:
                    robot_data = get_device_name_from_device([device_id])
                    message = constants.REQUIRED_MFD_CART_MESSAGE.format(next_trolley_name, robot_data[device_id])
                    device_message[device_id] = message
                    logger.info("In update_mfd_couch_db_notification, device_message {}, unique_id {}".format(device_message, unique_id))
                    Notifications(user_id=user_id, call_from_client=True) \
                        .send_transfer_notification(user_id=user_id, system_id=system_id,
                                                    device_message=device_message, unique_id=unique_id,
                                                    batch_id=batch_id, flow='mfd')

        return skip_for_all_devices
    except Exception as e:
        logger.error(e)
        logger.error("Error in remove_notifications_for_skipped_mfs_filling: {}".format(e))
        raise e


@log_args_and_response
def db_get_filled_unfilled_slots_of_mfd_canister(args):
    """
    this function return the information of mfd_slots and slots of packs
    """
    logger.info("In db_get_filled_unfilled_slots_of_mfd_canister")
    try:
        response: dict = dict()

        txr = args["txr"]
        scanned_drug = args["scanned_drug"]
        mfd_analysis_info = args["mfd_analysis_info"]

        select_fields = [DrugMaster.txr.alias("txr"),
                         MfdAnalysis.id.alias("mfd_analysis_id"),
                         SlotDetails.id.alias("slot_details_id"),
                         PackDetails.id.alias("pack_details_id"),
                         SlotDetails.drug_id.alias("slot_details_drug"),
                         MfdAnalysisDetails.status_id.alias("mfd_drug_status"),
                         MfdAnalysisDetails.id.alias("mfd_analysis_details_id"),
                         MfdAnalysisDetails.quantity.alias("required_quantity"),
                         MfdAnalysisDetails.mfd_can_slot_no.alias("slot_number"),
                         ]

        for mfd_analysis_id, mfd_analysis_slot_data in mfd_analysis_info.items():

            mfd_slot_info = dict()
            diff_slot_number = list()
            slots_to_filled = mfd_analysis_slot_data.get("slots_to_filled", None)
            overwrite_slots = mfd_analysis_slot_data.get("overwrite_slots", None)
            slots_to_unfilled = mfd_analysis_slot_data.get("slots_to_unfilled", None)

            query = MfdAnalysis.select(*select_fields).dicts() \
                .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)\
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
                .where((MfdAnalysis.id == mfd_analysis_id) & (DrugMaster.txr == txr))

            for record in query:
                if slots_to_unfilled:
                    if record["slot_number"] in slots_to_unfilled:
                        if record["txr"] == txr:
                            if record["slot_details_drug"] == scanned_drug:
                                mfd_slot_info[record["slot_number"]] = {"same_drug": True,
                                                                        "pack_id": record["pack_details_id"],
                                                                        "slot_id": record["slot_details_id"],
                                                                        "old_drug_id": record["slot_details_drug"],
                                                                        "required_quantity":
                                                                            record["required_quantity"],
                                                                        "mfd_analysis_details_id":
                                                                            record["mfd_analysis_details_id"]
                                                                        }
                            else:
                                mfd_slot_info[record["slot_number"]] = {"same_drug": False,
                                                                        "pack_id": record["pack_details_id"],
                                                                        "slot_id": record["slot_details_id"],
                                                                        "old_drug_id": record["slot_details_drug"],
                                                                        "required_quantity":
                                                                            record["required_quantity"],
                                                                        "mfd_analysis_details_id":
                                                                            record["mfd_analysis_details_id"]
                                                                        }
                elif slots_to_filled or overwrite_slots:
                    if record["slot_number"] in slots_to_filled:
                        if record["txr"] == txr:
                            if record["slot_details_drug"] == scanned_drug:
                                mfd_slot_info[record["slot_number"]] = {"same_drug": True,
                                                                        "pack_id": record["pack_details_id"],
                                                                        "slot_id": record["slot_details_id"],
                                                                        "old_drug_id": record["slot_details_drug"],
                                                                        "required_quantity":
                                                                            record["required_quantity"],
                                                                        "mfd_analysis_details_id":
                                                                            record["mfd_analysis_details_id"]
                                                                        }
                            else:
                                mfd_slot_info[record["slot_number"]] = {"same_drug": False,
                                                                        "pack_id": record["pack_details_id"],
                                                                        "slot_id": record["slot_details_id"],
                                                                        "old_drug_id": record["slot_details_drug"],
                                                                        "required_quantity":
                                                                            record["required_quantity"],
                                                                        "mfd_analysis_details_id":
                                                                            record["mfd_analysis_details_id"]
                                                                        }
                    elif record["slot_number"] in overwrite_slots:
                        if record["txr"] == txr:
                            if record["slot_details_drug"] == scanned_drug:
                                mfd_slot_info[record["slot_number"]] = {"same_drug": True,
                                                                        "pack_id": record["pack_details_id"],
                                                                        "slot_id": record["slot_details_id"],
                                                                        "old_drug_id": record["slot_details_drug"],
                                                                        "required_quantity":
                                                                            record["required_quantity"],
                                                                        "mfd_analysis_details_id":
                                                                            record["mfd_analysis_details_id"]
                                                                        }
                            else:
                                mfd_slot_info[record["slot_number"]] = {"same_drug": False,
                                                                        "pack_id": record["pack_details_id"],
                                                                        "slot_id": record["slot_details_id"],
                                                                        "old_drug_id": record["slot_details_drug"],
                                                                        "required_quantity":
                                                                            record["required_quantity"],
                                                                        "mfd_analysis_details_id":
                                                                            record["mfd_analysis_details_id"]
                                                                        }
                    else:
                        diff_slot_number.append(record["slot_number"])

            if diff_slot_number:
                logger.debug("Wrong unfilled slot_number {}".format(diff_slot_number))
            response[mfd_analysis_id] = mfd_slot_info

        return response
    except Exception as e:
        logger.error("Error in db_get_filled_unfilled_slots_of_mfd_canister: {}".format(e))
        raise e


@log_args_and_response
def db_get_mfd_pending_sequence_for_batch(batch_id):
    pending_trolley = []
    try:


        trolley_seq = MfdAnalysis.select(MfdAnalysis.trolley_seq,
                                         fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_status)).alias(
                                             "pack_status"),
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id))
                                         .alias("mfd_canister_status_ids")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(MfdAnalysis.batch_id == batch_id) \
            .group_by(MfdAnalysis.trolley_seq)

        for pending_trolleys in trolley_seq:
            pack_status = pending_trolleys["pack_status"]
            pack_status_list = [int(x) for x in pack_status.split(',')]
            mfd_status = pending_trolleys["mfd_canister_status_ids"]
            mfd_status_list = [int(x) for x in mfd_status.split(',')]
            if all(t_seq in [settings.PENDING_PACK_STATUS, settings.DELETED_PACK_STATUS] for t_seq in
                   pack_status_list) and \
                    all(t_seq in [constants.MFD_CANISTER_PENDING_STATUS, constants.MFD_CANISTER_SKIPPED_STATUS] for t_seq in mfd_status_list):
                pending_trolley.append(pending_trolleys["trolley_seq"])
        return pending_trolley

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return pending_trolley


@log_args_and_response
def get_mfd_batch_drugs_dao(paginate, filter_fields):
    try:
        drug_id_list = []
        response_drug_list = []
        data_list = []
        # in_progress_batch = (BatchMaster.select(BatchMaster.id).where(BatchMaster.status << [settings.BATCH_IMPORTED])
        #                      .scalar())
        drug_list = []
        fields_dict = {
            "mfd_drug_name": DrugMaster.concated_drug_name_field(include_ndc=True)
        }
        clauses = [SlotDetails.quantity == fn.FLOOR(SlotDetails.quantity),
                   BatchMaster.status == settings.BATCH_IMPORTED,
                   DrugDimension.verification_status_id == settings.DRUG_VERIFICATION_STATUS['verified'],
                   PackDetails.pack_status.not_in(settings.PACK_FILLING_DONE_STATUS_LIST)
                   # (CanisterMaster.id.is_null(True) | (fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.active)) == 0))
                   ]

        batch_query = BatchMaster.select().where(BatchMaster.status == settings.BATCH_IMPORTED).get()
        pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(batch_query.id)
        if pending_trolley_sequence:
            clauses.append((MfdAnalysis.trolley_seq << pending_trolley_sequence) |
                           (MfdAnalysis.trolley_seq.is_null(True)))
        else:
            return [], 0, []
        exact_search_fields = ['canister_id']
        like_search_fields = ['mfd_drug_name']
        query = (MfdAnalysis.select(SlotDetails.drug_id,
                                    DrugMaster.ndc,
                                    DrugMaster.imprint,
                                    DrugMaster.color,
                                    CustomDrugShape.name.alias("shape"),
                                    DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                    fn.SUM(SlotDetails.quantity).alias('quantity'),
                                    DrugMaster.image_name,

                                    )
                 .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id)
                 .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)
                 .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                 .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                 .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                 .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                       (UniqueDrug.txr == DrugMaster.txr)))
                 .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                 .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id)
                 .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id)
                 .group_by(SlotDetails.drug_id)
                 .order_by(fn.SUM(SlotDetails.quantity).desc())
                 )
        query = query.where(functools.reduce(operator.and_, clauses))
        for record in query.dicts():
            drug_id_list.append(record['drug_id'])

        if drug_id_list:
            sub_query = (DrugMaster.select(fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.active)).alias("is_active"),
                                           DrugMaster.id.alias('drug_id')
                                           )
                         .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMaster.id)
                         .where(DrugMaster.id.in_(drug_id_list)).group_by(DrugMaster.id))
            for record in sub_query.dicts():
                if record['is_active'] and '1' in record['is_active']:
                    continue
                response_drug_list.append(record['drug_id'])
        clauses = get_filters(clauses, fields_dict, filter_dict=filter_fields, exact_search_fields=exact_search_fields,
                              like_search_fields=like_search_fields)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        for record in query.dicts():
            if record['drug_id'] in response_drug_list:
                drug_list.append(record['drug_name'])
                data_list.append(record)
        count = len(data_list)
        paginated_result = dpws_paginate(data_list, paginate)
        return paginated_result, count, drug_list
    except DoesNotExist as e:
        return [], 0, []
    except Exception as e:
        return e


@log_args_and_response
def get_pending_mfd_pack_list_dao(canister_list):
    """
    Function to get pending packs for the drugs which are present in canisters
    """
    try:
        batch_query = BatchMaster.select().where(BatchMaster.status == settings.BATCH_IMPORTED).get()
        pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(batch_query.id)
        clauses = [BatchMaster.status == settings.BATCH_IMPORTED,
                   CanisterMaster.id << canister_list,
                   CanisterMaster.active == settings.is_canister_active,
                   SlotDetails.quantity == fn.FLOOR(SlotDetails.quantity)]
        if pending_trolley_sequence:
            clauses.append(MfdAnalysis.trolley_seq << pending_trolley_sequence)
        else:
            return None, None, None, None, None, None

        # if batch_query.mfd_status_id == constants.MFD_BATCH_PRE_SKIPPED:
        #     clauses.append(MfdAnalysisDetails.status_id == constants.MFD_DRUG_SKIPPED_STATUS)
        # else:
        #     clauses.append(MfdAnalysisDetails.status_id == constants.MFD_DRUG_PENDING_STATUS)
        #     clauses.append(MfdAnalysis.status_id != constants.MFD_CANISTER_IN_PROGRESS_STATUS)
        query = (MfdAnalysis.select(PackRxLink.pack_id,
                                    MfdAnalysisDetails.id,
                                    MfdAnalysis.id.alias('analysis_id'),
                                    MfdAnalysis.batch_id,
                                    DrugMaster.id.alias('drug_id'),
                                    MfdAnalysis.dest_device_id
                                    )
                 .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id)
                 .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id)
                 .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)
                 .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id)
                 .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id)
                 .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMaster.id)
                 .where(functools.reduce(operator.and_, clauses)))
        device_wise_packs = {}
        device_wise_analysis_dict = {}
        affected_packs = set()
        mfd_analysis_dict = {}
        batch_id = None
        drug_id = None
        device_id = None
        analysis_ids = []
        for record in query.dicts():
            if not batch_id:
                batch_id = record['batch_id']
            if not drug_id:
                drug_id = record['drug_id']
            device_wise_packs.setdefault(record['dest_device_id'], set())
            device_wise_packs[record['dest_device_id']].add(record['pack_id'])
            if record['dest_device_id'] not in device_wise_analysis_dict:
                device_wise_analysis_dict[record['dest_device_id']] = {}
            if record['analysis_id'] not in device_wise_analysis_dict[record['dest_device_id']]:
                device_wise_analysis_dict[record['dest_device_id']][record['analysis_id']] = []
            device_wise_analysis_dict[record['dest_device_id']][record['analysis_id']].append(record['id'])
            device_wise_analysis_dict[record['dest_device_id']][record['analysis_id']] = list(set(device_wise_analysis_dict[record['dest_device_id']][record['analysis_id']]))

        for dest_device_id, packs in device_wise_packs.items():
            if len(packs) > len(affected_packs):
                affected_packs = packs
                device_id = dest_device_id
        # if len(device_wise_packs[2]) > len(device_wise_packs[3]):
        #     affected_packs = set(device_wise_packs[2])
        #     device_id = 2
        # else:
        #     affected_packs = set(device_wise_packs[3])
        #     device_id = 3
        if device_id:
            mfd_analysis_dict = device_wise_analysis_dict[device_id]
        if mfd_analysis_dict:
            sub_query = (MfdAnalysis.select(MfdAnalysis.id.alias('analysis_id'),
                                            MfdAnalysisDetails.id)
                         .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)
                         .where(MfdAnalysis.id << list(mfd_analysis_dict.keys())))

            mfd_analysis_dict_all = {}
            for record in sub_query.dicts():
                if record['analysis_id'] not in mfd_analysis_dict_all:
                    mfd_analysis_dict_all[record['analysis_id']] = []
                mfd_analysis_dict_all[record['analysis_id']].append(record['id'])
                mfd_analysis_dict_all[record['analysis_id']] = list(set(mfd_analysis_dict_all[record['analysis_id']]))

            for analysis_id, analysis_list in mfd_analysis_dict.items():
                diff = set(mfd_analysis_dict_all[analysis_id]) - set(mfd_analysis_dict[analysis_id])
                if not diff:
                    analysis_ids.append(analysis_id)

        return list(affected_packs), mfd_analysis_dict, analysis_ids, batch_id, drug_id, device_id

    except Exception as e:
        return e


@log_args_and_response
def check_batch_drug_dao(ndc):
    """
    This function is used for given ndc used in mfd drugs or not.
    """
    try:
        clauses = list()
        clauses.append(BatchMaster.status == settings.BATCH_IMPORTED)
        clauses.append(DrugMaster.ndc == ndc)
        clauses.append(SlotDetails.quantity == fn.FLOOR(SlotDetails.quantity))
        batch_query = BatchMaster.select().where(BatchMaster.status == settings.BATCH_IMPORTED).get()
        pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(batch_query.id)
        if pending_trolley_sequence:
            clauses.append((MfdAnalysis.trolley_seq << pending_trolley_sequence) |
                           (MfdAnalysis.trolley_seq.is_null(True)))
        else:
            return False
        # if batch_query.mfd_status_id == constants.MFD_BATCH_PRE_SKIPPED:
        #     clauses.append(MfdAnalysisDetails.status_id == constants.MFD_DRUG_SKIPPED_STATUS)
        # else:
        #     clauses.append(MfdAnalysisDetails.status_id == constants.MFD_DRUG_PENDING_STATUS)
        #     clauses.append(MfdAnalysis.status_id != constants.MFD_CANISTER_IN_PROGRESS_STATUS)
        query = (MfdAnalysis.select()
                 .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)
                 .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)
                 .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                 .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id)
                 .where(functools.reduce(operator.and_, clauses)))
        return query.get()
    except DoesNotExist as e:
        return False


