import functools
import json
import operator
import os
import sys
from collections import defaultdict
from datetime import datetime, date, timedelta
from copy import deepcopy
from typing import Any, Dict, List
from playhouse.shortcuts import cast, case
import settings
from com.pharmacy_software import send_data
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, log_args, get_current_date_time, get_current_date
from peewee import InternalError, IntegrityError, DataError, fn, JOIN_LEFT_OUTER, Clause, SQL, DoesNotExist
from migrations.migration_for_zone_implementation_in_canister_master import CanisterZoneMapping
from src import constants
from src.api_utility import apply_paginate, get_orders
from src.dao.canister_dao import delete_reserved_canister_for_pack_queue, delete_reserved_canister_for_skipped_canister
from src.dao.canister_transfers_dao import get_slow_movers_for_device
from src.dao.drug_dao import fetch_canister_drug_data_from_canister_ids, get_fndc_txr_wise_inventory_qty
from src.dao.drug_inventory_dao import remove_bypassed_ordering
from src.dao.pack_dao import db_get_progress_filling_left_pack_ids

from src.exceptions import PharmacySoftwareCommunicationException, PharmacySoftwareResponseException, \
    AlternateDrugUpdateException
from src.dao.misc_dao import get_company_setting_by_company_id
from src.model.model_action_master import ActionMaster
from src.model.model_alternate_drug_option import AlternateDrugOption
from src.model.model_batch_change_tracker import BatchChangeTracker
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_stick import CanisterStick
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_canister_stick_mapping import DrugCanisterStickMapping
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_status import DrugStatus
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_drug_tracker import PackDrugTracker
from src.model.model_pack_history import PackHistory
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_rx import PatientRx
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_store_separate_drug import StoreSeparateDrug
from src.model.model_unique_drug import UniqueDrug
from src.model.model_zone_master import ZoneMaster

from src.service.notifications import Notifications
from src.dao.pack_drug_dao import populate_pack_drug_tracker
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


@log_args_and_response
def get_canister_data_from_txr(company_id, txr_list, zone_id):
    canister_data = dict()
    try:
        clauses = [
            CanisterMaster.company_id == company_id,
            CanisterMaster.rfid.is_null(False),
            CanisterMaster.active == settings.is_canister_active,
            DrugMaster.txr << txr_list
        ]
        if zone_id is not None:
            clauses.append((CanisterZoneMapping.zone_id == zone_id))
        query = CanisterMaster.select(CanisterMaster,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.txr,
                                      DeviceMaster.system_id,
                                      LocationMaster.display_location,
                                      DeviceMaster.name,
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      fn.GROUP_CONCAT(
                                          Clause(
                                              fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                              SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True),
                                                                               'null', ZoneMaster.name)),
                                                             SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                          'zone_name')
                                      ) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(CanisterZoneMapping,
                  on=CanisterMaster.id == CanisterZoneMapping.canister_id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, on=ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .where(*clauses) \
            .group_by(CanisterMaster.id)
        for record in query.dicts():
            fndc_txr = (record['formatted_ndc'], record['txr'])
            if fndc_txr not in canister_data:
                canister_data[fndc_txr] = list()
            canister_data[fndc_txr].append(record)
        logger.info(" In get_canister_data_from_txr. Ended")

        return canister_data
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_canister_data_from_txr: {}".format(e))
        raise
    except Exception as e:
        logger.error("Error in get_canister_data_from_txr: {}".format(e))
        raise e


@log_args_and_response
def get_alternate_drug_verification_list(txr_list, zone_id):
    alternate_drug_dict = dict()
    canister_data = dict()
    unique_ndc = set()
    try:
        if not txr_list:
            return canister_data, alternate_drug_dict

        UniqueDrugAlias = UniqueDrug.alias()
        canister_query = CanisterMaster.select(DrugMaster,
                                               LocationMaster.device_id,
                                               LocationMaster.display_location,
                                               DeviceMaster.name.alias('device_name'),
                                               DeviceMaster.system_id,
                                               ZoneMaster.id.alias('zone_id'),
                                               ZoneMaster.name.alias('zone_name'),
                                               CanisterMaster.available_quantity,
                                               CanisterMaster.id.alias('canister_id')) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .join(CanisterZoneMapping, on=CanisterMaster.id == CanisterZoneMapping.canister_id) \
            .join(ZoneMaster, on=ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(ZoneMaster.id == zone_id,
                   CanisterMaster.rfid.is_null(False),
                   CanisterMaster.active == settings.is_canister_active,
                   UniqueDrug.txr << txr_list) \
            .group_by(CanisterMaster.id)
        logger.info("In get_alternate_drug_verification_list : Canister query".format(canister_query))
        for canister in canister_query.dicts():

            # below line is commented as we required to show them on screen
            # if not canister['alt_option_id'] or (canister['alt_option_id'] and canister['active']):
            if (canister['formatted_ndc'], canister['txr']) not in canister_data.keys():
                canister_data[(canister['formatted_ndc'], canister['txr'])] = [{
                    'canister_id': canister['canister_id'],
                    'device_id': canister['device_id'],
                    'device_name': canister['device_name'],
                    'system_id': canister['system_id'],
                    'zone_id': canister['zone_id'],
                    'zone_name': canister['zone_name'],
                    'available_quantity': canister['available_quantity']
                }]
            else:
                canister_data[(canister['formatted_ndc'], canister['txr'])].append({
                    'canister_id': canister['canister_id'],
                    'device_id': canister['device_id'],
                    'device_name': canister['device_name'],
                    'system_id': canister['system_id'],
                    'zone_id': canister['zone_id'],
                    'zone_name': canister['zone_name'],
                    'available_quantity': canister['available_quantity']
                })

        query = DrugMaster.select(DrugMaster,
                                  fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                        DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                  fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                        DrugDetails.last_seen_by, ).alias('last_seen_with'),
                                  DrugStatus.ext_status,
                                  DrugStatus.last_billed_date,
                                  fn.IF(DrugMaster.brand_flag == settings.GENERIC_FLAG, 1, 0).alias('alt_selection'),
                                  fn.GROUP_CONCAT(
                                      CanisterMaster.id,
                                  ).coerce(False).alias('canister_list')
                                  ).dicts() \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=((CanisterMaster.drug_id == DrugMaster.id) &
                                                       (CanisterMaster.active == settings.is_canister_active))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                      (DrugStockHistory.is_active == True) &
                                                      (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == CanisterMaster.company_id))) \
            .where(DrugMaster.txr << txr_list) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        for record in query:
            alternate_ndc = record['formatted_ndc'], record['txr']
            alternate_drug_brand_flag = record["brand_flag"]
            if record['txr'] not in alternate_drug_dict:
                alternate_drug_dict[record['txr']] = dict()
            if record['formatted_ndc'] not in alternate_drug_dict[record['txr']]:
                record['sort_last_billed_date'] = record["last_billed_date"] if record[
                    "last_billed_date"] else settings.min_date
                alternate_drug_dict[record['txr']][record['formatted_ndc']] = record

        return canister_data, alternate_drug_dict
    except Exception as e:
        logger.error("Error in get_alternate_drug_verification_list: {}".format(e))
        raise e


@log_args_and_response
def alternate_drug_update(dict_alternate_drug_info):
    """ Updates the alternate drug information for the packs in the
    SlotTransaction table and also sends the alternate drug information
    to the pharmacy software.

    Args:
        dict_alternate_drug_info (dict): The json dict containing
                                        batchlist, olddruglist, newdruglist, canisterlist

    Returns:
        json response of success or failure

    @param dict_alternate_drug_info:
    Examples:
        >>> alternate_drug_update()
        None

    """
    changed_after_batch = dict_alternate_drug_info.get('changed_after_batch', None)
    send_notification = dict_alternate_drug_info.get('send_notification', False)
    module_id = dict_alternate_drug_info.get('module_id', constants.PDT_ALTERNATE_UNDEFINED)
    company_id = dict_alternate_drug_info["company_id"]

    slot_details_updation: dict = dict()


    if all(item not in dict_alternate_drug_info for item in ['pack_list', 'batch_id']):
        return error(1001, "Missing Parameter(s): pack_list or batch_id.")

    if "batch_id" in dict_alternate_drug_info and module_id != constants.PDT_MVS_MANUAL_FILL:
        pack_ids = PackDetails.db_get_pack_ids_by_batch_id(batch_id=dict_alternate_drug_info['batch_id'],
                                                           company_id=company_id)
    else:
        pack_ids = dict_alternate_drug_info["pack_list"].split(',')
    logger.info("In alternate_drug_update: pack id list: {}".format(pack_ids))

    if not dict_alternate_drug_info.get('fill_manually', None):
        dict_alternate_drug_info['fill_manually'] = [0 for item in dict_alternate_drug_info['olddruglist'].split(',')
                                                     for i in range(len(pack_ids))]

    ips_drug_ids = deepcopy(dict_alternate_drug_info["olddruglist"].split(','))
    ips_alt_drug_ids = deepcopy(dict_alternate_drug_info["newdruglist"].split(','))
    original_drug_ids = deepcopy(dict_alternate_drug_info["olddruglist"].split(','))

    requestedOldDrugIds = dict_alternate_drug_info['olddruglist'].split(',')
    requestedNewDrugIds = dict_alternate_drug_info['newdruglist'].split(',')

    dict_alternate_drug_info['olddruglist'] = [
        item for item in dict_alternate_drug_info['olddruglist'].split(',') for i in range(len(pack_ids))
    ]
    dict_alternate_drug_info['newdruglist'] = [
        item for item in dict_alternate_drug_info['newdruglist'].split(',') for i in range(len(pack_ids))
    ]

    # make list which will be sent to IPS, this will be updated later by NDC.
    user_id = dict_alternate_drug_info["user_id"]
    drug_ids = dict_alternate_drug_info["olddruglist"]
    alt_drug_ids = dict_alternate_drug_info["newdruglist"]
    fill_manually = dict_alternate_drug_info["fill_manually"]

    try:  # convert to int(it gives error if we can not convert to int)
        ips_drug_ids = list(map(int, ips_drug_ids))
        ips_alt_drug_ids = list(map(int, ips_alt_drug_ids))
    except ValueError as e:
        logger.error(e, exc_info=True)
        return error(1020, "Element of olddruglist and newdruglist must be integer.")

    valid_packlist = PackDetails.db_verify_packlist(packlist=pack_ids, company_id=company_id)
    if not valid_packlist:
        return error(1014)

    company_settings = get_company_setting_by_company_id(company_id=company_id)
    required_settings = settings.ALTERNATE_DRUG_SETTINGS
    settings_present = all([key in company_settings for key in required_settings])
    logger.info("In alternate_drug_update: settings_present: {}".format(settings_present))
    if not settings_present:
        return error(6001)

    packlist_len = len(pack_ids)
    drugs_ids_len = len(drug_ids)
    alt_drug_dict: dict = dict()
    alt_drug_dict_for_drug_tracking: dict = dict()
    pack_drug_tracker_details: list = list()

    # get the number of distinct alternate drugs
    _size = int(drugs_ids_len / packlist_len)
    new_pack_ids: list = list()  # only those pack ids which really have old drugs
    try:
        with db.transaction():
            for i in range(0, _size):
                alt_drug_dict[int(drug_ids[i * packlist_len])] = (int(alt_drug_ids[i * packlist_len]),
                                                                  int(fill_manually[i * packlist_len]))

                alt_drug_dict_for_drug_tracking[int(drug_ids[i * packlist_len])] = int(alt_drug_ids[i * packlist_len])

            patient_rx_ids: dict = dict()
            marked_manual_pack_rx_ids = defaultdict(list)
            pack_rx_link_batch_scheduling_selected_drug_ids: dict = dict()
            pack_rx_link_original_drug_ids: dict = dict()
            pack_ids = list(set(pack_ids))

            # for handling daw drug update -- allowed only for daw 0
            # fetch only those patient_rx_ids where daw value is zero
            query = PackRxLink.select(PackRxLink.patient_rx_id,
                                      PackRxLink.id,
                                      PackRxLink.bs_drug_id,
                                      PackRxLink.original_drug_id,
                                      SlotDetails.drug_id,
                                      PackRxLink.pack_id
                                      ).dicts() \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .where(PackRxLink.pack_id << pack_ids, PatientRx.daw_code == 0)

            for record in query:
                try:
                    patient_rx_ids[record["patient_rx_id"]] = alt_drug_dict[record["drug_id"]][0]

                    if alt_drug_dict[record['drug_id']][1]:
                        marked_manual_pack_rx_ids[1].append(record["id"])
                    else:
                        marked_manual_pack_rx_ids[0].append(record["id"])

                    # If original_drug_id is null then store current drug id as original drug id in pack rx link
                    # this is required , so we can send the flag of ndc change while printing label
                    if record["original_drug_id"] is None:
                        pack_rx_link_original_drug_ids[record["id"]] = record["drug_id"]

                    if record["bs_drug_id"] is None:
                        pack_rx_link_batch_scheduling_selected_drug_ids[record['id']] = record["drug_id"]

                    new_pack_ids.append(record["pack_id"])
                except KeyError:
                    pass  # not really drug id for that given pack id so will throw key error

            logger.info("In alternate_drug_update: new_pack_ids: {}".format(new_pack_ids))
            if not new_pack_ids:  # if no pack has given old drug id return 0
                return create_response(0)

            slot_query = SlotDetails.select(SlotDetails.id,
                                            SlotDetails.drug_id,
                                            PackRxLink.pack_id,
                                            ).dicts() \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .where(PackRxLink.pack_id << pack_ids, PatientRx.daw_code == 0,
                       SlotDetails.drug_id << original_drug_ids)

            for record in slot_query:
                slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                       "drug_id": alt_drug_dict[record["drug_id"]][0]}

                pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                          "updated_drug_id": alt_drug_dict[record["drug_id"]][0],
                                          "module": module_id,
                                          "created_by": user_id, "created_date": get_current_date_time()}

                pack_drug_tracker_details.append(pack_drug_tracker_info)

            ips_change_response = send_alternate_drug_change_data_to_ips(new_pack_ids=new_pack_ids,
                                                                         alt_drug_ids=alt_drug_ids,
                                                                         drug_ids=drug_ids,
                                                                         ips_drug_ids=ips_drug_ids,
                                                                         ips_alt_drug_ids=ips_alt_drug_ids,
                                                                         company_settings=company_settings,
                                                                         requestedOldDrugIds=requestedOldDrugIds,
                                                                         requestedNewDrugIds=requestedNewDrugIds,
                                                                         pack_ids=pack_ids,
                                                                         send_notification=send_notification)

            if ips_change_response:
                for key, value in patient_rx_ids.items():
                    update_dict = {"drug_id": value,
                                   "modified_by": user_id,
                                   "modified_date": get_current_date_time()
                                   }
                    status1 = PatientRx.db_update_patient_rx_data(update_dict=update_dict, patient_rx_id=key)
                    logger.info("IN alternate_drug_update: Updating PatientRx in alternate drugs with values "
                                 ": " + str(key) + "," + str(value) + ":" + str(status1))

                for key, value in pack_rx_link_original_drug_ids.items():
                    update_dict = {"original_drug_id": value}
                    status2 = PackRxLink.db_update_pack_rx_link(update_dict=update_dict, pack_rx_link_id=[key])
                    logger.info("In alternate_drug_update: item of  pack_rx_link_original_drug_ids,Updating PackRxLink alternate drugs with values "
                                 ": " + str(key) + "," + str(value) + ":" + str(status2))

                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    prev_drug_id = slot_drugs["prev_drug_id"]
                    update_dict = {"drug_id": drug_id}
                    slot_details_update_status = SlotDetails.db_update_slot_details_by_slot_id(update_dict=update_dict, slot_details_id=slot_details_id)
                    logger.info(f"In alternate_drug_update: Updating SlotDetails drugs with values, id: {slot_details_id}, prev_drug_id: {prev_drug_id}, "
                        f"updated_drug_id: {drug_id} with status: {slot_details_update_status}")

                # populate pack drug tracker data in PackDrugTracker tabel
                PackDrugTracker.db_insert_pack_drug_tracker_data(pack_drug_tracker_details)

                if changed_after_batch:
                    for key, value in pack_rx_link_batch_scheduling_selected_drug_ids.items():
                        update_dict = {"bs_drug_id": value}
                        status3 = PackRxLink.db_update_pack_rx_link(update_dict=update_dict, pack_rx_link_id=[key])
                        logger.info("In alternate_drug_update: Updating PackRxLink bs drugs with values "
                                     ": " + str(key) + "," + str(value) + ":" + str(status3))

                    for key, value in marked_manual_pack_rx_ids.items():
                        update_dict = {"fill_manually": key}
                        status4 = PackRxLink.db_update_pack_rx_link(update_dict=update_dict, pack_rx_link_id=value)
                        logger.info("In alternate_drug_update: Updating PackRxLink fill_manual with values "
                                     ": " + str(key) + "," + str(value) + ":" + str(status4))
            else:
                return error(7001)

        return create_response(1)

    except (InternalError, DataError, IntegrityError) as e:
        logger.error("Error in alternate_drug_update {}".format(e))
        raise e
    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in alternate_drug_update: PharmacySoftwareCommunicationException {}".format(e))
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error("Error in alternate_drug_update: PharmacySoftwareResponseException {}".format(e))
        raise e


@log_args_and_response
def send_alternate_drug_change_data_to_ips(new_pack_ids: list, alt_drug_ids: list, drug_ids: list, ips_drug_ids: list, ips_alt_drug_ids: list,
                                           company_settings: Dict[str, Any], requestedOldDrugIds: list, requestedNewDrugIds: list, pack_ids: list,
                                           send_notification: bool = False):
    """
     send alternate drug change data to ips
      @param send_notification:
      @param pack_ids:
      @param requestedNewDrugIds:
      @param requestedOldDrugIds:
      @param company_settings:
      @param ips_alt_drug_ids:
      @param ips_drug_ids:
      @param drug_ids:
      @param alt_drug_ids:
      @param new_pack_ids:
      @return:
      """
    try:
        drug_ndc_map: dict = dict()
        drug_name_map: dict = dict()
        for record in DrugMaster.db_get_by_ids(drug_ids + alt_drug_ids):
            drug_ndc_map[record["id"]] = record["ndc"]
            drug_name_map[record["id"]] = " ".join(
                (record["drug_name"], record["strength_value"], record["strength"]))

        # Code was removed on 10th May, 2022 as we don't need to trigger multiple AlternateDrug calls to IPS.
        # Instead, handle this through updatefilledby call.
        # settings.PHARMACY_UPDATE_ALT_DRUG_URL

        # if send_notification:
        #     Notifications().drug_alter(requestedOldDrugIds, requestedNewDrugIds, drug_ndc_map, pack_ids, drug_name_map)
        return True

    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in send_alternate_drug_change_data_to_ips: PharmacySoftwareCommunicationException:{}".format(e))
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error("Error in send_alternate_drug_change_data_to_ips: PharmacySoftwareResponseException: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in send_alternate_drug_change_data_to_ips {}".format(e))
        raise e


@log_args_and_response
def get_same_drug_canister(canister_ids: list, device_id: int, alt_canisters_count: int):
    try:
        response = True
        status_list = list()
        fndc_txr_list = list()
        canister_list = list()
        drug_max_canister = None

        fndc_txr = DrugMaster.select((DrugMaster.concated_fndc_txr_field(sep="##")).alias("drug_id")).dicts() \
            .join(CanisterMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.id << canister_ids)

        for record in fndc_txr:
            fndc_txr_list.append(record["drug_id"])

        max_canister_query = (UniqueDrug.select(UniqueDrug.max_canister,
                                                UniqueDrug.concated_fndc_txr_field(sep="##").alias("drug_id")).dicts()
                              .where(UniqueDrug.concated_fndc_txr_field(sep="##") << fndc_txr_list)
                              )

        for record in max_canister_query:
            drug_max_canister = record["max_canister"]

        if int(drug_max_canister) > 2:
            canister_count_query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                                         fn.GROUP_CONCAT(
                                                             fn.DISTINCT(
                                                                 PackAnalysisDetails.status
                                                             )
                                                         ).coerce(False).alias("status")
                                                         ).dicts()\
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
                .join(PackAnalysisDetails, on=CanisterMaster.id == PackAnalysisDetails.canister_id)\
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
                .join(PackQueue, on=PackDetails.id == PackQueue.pack_id)\
                .where((DrugMaster.concated_fndc_txr_field(sep="##") << fndc_txr_list) &
                       (PackAnalysisDetails.device_id == device_id) &
                       (CanisterMaster.active == settings.is_canister_active) &
                       (PackDetails.pack_status == settings.PENDING_PACK_STATUS)
                       )\
                .group_by(CanisterMaster.id)

            for record in canister_count_query:
                if record["canister_id"] not in canister_list:
                    canister_list.append(record["canister_id"])

                status_list.extend([int(status) for status in record["status"].split(",")])

            # if len(canister_list) == 1 and alt_canisters_count == 0:
            #     response = False
            if len(canister_list) == 1:
                logger.info("In get_same_drug_canister: canister_list: {}".format(canister_list))
                response = False
        else:
            response = False

        return response
    except Exception as e:
        logger.error("Error in get_same_drug_canister_count: {}".format(e))
        raise e

# The function call was removed on 10th May, 2022 as we don't need to trigger multiple AlternateDrug calls to IPS.
# Instead, handle this through updatefilledby call.
# This function is kept here if we need to track the function call in future
# def send_alt_drug_data(batch_list, ndc_list, alt_ndc_list, company_settings):
# settings.PHARMACY_UPDATE_ALT_DRUG_URL


@log_args_and_response
def db_get_alternate_drug_canisters(canister_id: int,
                                    company_id: int, reserved_canister_query: List[Any] = None,
                                    same_drug_canisters: bool = None) -> List[Any]:
    """
     Returns canisters of alternate drugs of drug present in given canister id
    :param canister_id: int
    :param company_id: int
    :param reserved_canister_query: peewee.SelectQuery
    :return: list
    """
    try:
        CanisterMasterAlias = CanisterMaster.alias()
        LocationMasterAlias = LocationMaster.alias()

        DrugMasterAlias = DrugMaster.alias()
        sub_q = CanisterMasterAlias.select(CanisterMasterAlias.id.alias('canister_id'),
                                           LocationMasterAlias.device_id.alias('device_id'),
                                            CanisterMasterAlias.available_quantity,
                                           fn.IF(CanisterMasterAlias.available_quantity < 0, 0,
                                                CanisterMasterAlias.available_quantity).alias('display_quantity'),
                                           CanisterMasterAlias.rfid.alias('rfid'),
                                           fn.IF(
                                               CanisterMasterAlias.expiry_date <= date.today() + timedelta(
                                                   settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                               constants.EXPIRED_CANISTER,
                                               fn.IF(
                                                   CanisterMasterAlias.expiry_date <= date.today() + timedelta(
                                                       settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                   constants.EXPIRES_SOON_CANISTER,
                                                   constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                           DrugMasterAlias.formatted_ndc,
                                           DrugMasterAlias.txr,
                                           DrugMasterAlias.brand_flag,
                                           DrugMasterAlias.ndc,
                                           DrugMasterAlias.drug_name,
                                           DrugMasterAlias.strength,
                                           DrugMasterAlias.strength_value,
                                           DrugMasterAlias.imprint,
                                           DrugMasterAlias.color,
                                           UniqueDrug.is_powder_pill,
                                           DrugMasterAlias.shape,
                                           DrugMasterAlias.image_name,
                                           DrugMasterAlias.id.alias('drug_id'),
                                           LocationMasterAlias.location_number,
                                           LocationMasterAlias.is_disabled,
                                           ContainerMaster.drawer_name.alias('drawer_number'),
                                           LocationMasterAlias.container_id.alias('container_id'),
                                           LocationMasterAlias.display_location,
                                           ZoneMaster.id.alias('zone_id'),
                                           ZoneMaster.name.alias('zone_name'),
                                           DeviceLayoutDetails.id.alias('device_layout_id'),
                                           DeviceMaster.name.alias('device_name'),
                                           DeviceTypeMaster.device_type_name,
                                           DeviceTypeMaster.id.alias('device_type_id'),
                                           ContainerMaster.ip_address,
                                           ContainerMaster.secondary_ip_address,
                                           ContainerMaster.id.alias('drawer_id'),
                                           ContainerMaster.serial_number,
                                           ContainerMaster.mac_address,
                                           ContainerMaster.secondary_mac_address,
                                           DrugStatus,
                                           UniqueDrug.is_delicate
                                           ) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == CanisterMasterAlias.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMasterAlias.formatted_ndc)
                                                  & (UniqueDrug.txr == DrugMasterAlias.txr))\
            .join(DrugStatus, on=DrugMasterAlias.id == DrugStatus.drug_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, CanisterMasterAlias.location_id == LocationMasterAlias.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, DeviceLayoutDetails.zone_id == ZoneMaster.id) \
            .where(CanisterMasterAlias.company_id == company_id,
                   CanisterMasterAlias.active == settings.is_canister_active,
                   DrugStatus.ext_status == settings.VALID_EXT_STATUS,
                   DrugMasterAlias.brand_flag == settings.GENERIC_FLAG,
                   CanisterMasterAlias.id.not_in(reserved_canister_query)
                   ).alias('alt_drug_canisters')

        # removed generic flog as these will be disabled from FE.
        query = CanisterMaster.select(sub_q.c.canister_id.alias('alt_canister_id'),
                                      sub_q.c.device_id.alias('alt_device_id'),
                                      sub_q.c.device_name.alias('alt_device_name'),
                                      sub_q.c.device_type_id.alias('alt_device_type_id'),
                                      sub_q.c.location_number.alias('alt_location_number'),
                                      sub_q.c.is_disabled.alias('is_alt_location_disabled'),
                                      sub_q.c.drug_id.alias('alt_drug_id'),
                                      sub_q.c.drug_name.alias('alt_drug_name'),
                                      sub_q.c.ndc.alias('alt_ndc'),
                                      sub_q.c.brand_flag.alias('alt_brand_flag'),
                                      sub_q.c.strength.alias('alt_strength'),
                                      sub_q.c.strength_value.alias('alt_strength_value'),
                                      sub_q.c.shape.alias('alt_shape'),
                                      sub_q.c.color.alias('alt_color'),
                                      sub_q.c.formatted_ndc.alias('alt_formatted_ndc'),
                                      sub_q.c.is_powder_pill.alias('alt_is_powder_pill'),
                                      sub_q.c.txr.alias('alt_txr'),
                                      sub_q.c.imprint.alias('alt_imprint'),
                                      sub_q.c.available_quantity.alias('alt_available_quantity'),
                                      sub_q.c.rfid.alias('alt_rfid'),
                                      sub_q.c.image_name.alias('image_name'),  # TODO add prefix 'alt_'
                                      sub_q.c.drawer_number.alias('alt_drawer_number'),
                                      sub_q.c.display_location.alias('alt_display_location'),
                                      sub_q.c.location_number.alias('alt_location_number'),
                                      sub_q.c.container_id.alias('alt_drawer_id'),
                                      sub_q.c.ip_address.alias('alt_ip_address'),
                                      sub_q.c.zone_id.alias('alt_zone_id'),
                                      sub_q.c.zone_name.alias('alt_zone_name'),
                                      sub_q.c.ext_status.alias('alt_ext_status'),
                                      sub_q.c.ext_status_updated_date.alias('alt_ext_status_updated_date'),
                                      sub_q.c.last_billed_date.alias('alt_last_billed_date'),
                                      sub_q.c.drawer_id.alias('alt_drawer_id'),
                                      sub_q.c.serial_number.alias('alt_serial_number'),
                                      sub_q.c.mac_address.alias('alt_mac_address'),
                                      sub_q.c.secondary_mac_address.alias('alt_secondary_mac_address'),
                                      sub_q.c.expiry_status.alias('alt_expiry_status'),
                                      sub_q.c.is_delicate.alias('alt_is_delicate'),
                                      DrugMaster.id.alias('drug_id'),
                                      DrugMaster.ndc,
                                      DrugMaster.drug_name,
                                      DrugMaster.strength,
                                      UniqueDrug.is_powder_pill,
                                      DrugMaster.strength_value,
                                      CanisterMaster.id.alias('canister_id'),
                                      LocationMaster.device_id,
                                      LocationMaster.location_number,
                                      LocationMaster.display_location,
                                      LocationMaster.quadrant,
                                      DeviceMaster.name.alias('device_name'),
                                      DeviceMaster.device_type_id.alias('device_type_id'),
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      ContainerMaster.id.alias('drawer_id'),
                                      ContainerMaster.serial_number,
                                      ContainerMaster.mac_address,
                                      ContainerMaster.secondary_mac_address,
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      UniqueDrug.is_delicate.alias('is_delicate')
                                      ) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                  & (UniqueDrug.txr == DrugMaster.txr)) \
            .join(DrugStatus, on=DrugMaster.id == DrugStatus.drug_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(sub_q, on=((sub_q.c.formatted_ndc != DrugMaster.formatted_ndc) & (sub_q.c.txr == DrugMaster.txr)))\
            .where(CanisterMaster.active == settings.is_canister_active,
                          CanisterMaster.id == canister_id,
                          CanisterMaster.company_id == company_id)\
            .order_by(
            SQL('FIELD(alt_expiry_status, {},{},{})'.format(constants.EXPIRES_SOON_CANISTER, constants.EXPIRED_CANISTER,
                                                            constants.NORMAL_EXPIRY_CANISTER)),
            DrugStatus.ext_status.desc(),
            SQL('FIELD(alt_brand_flag, "1")').desc(),
            DrugStatus.last_billed_date.desc())
        response_list = []
        ndc_list = []
        for record in query.dicts():
            ndc_list.append(int(record['alt_ndc']))
            if record['alt_is_delicate']:
                slow_movers, canister_id = get_slow_movers_for_device(record["device_id"], record["quadrant"])
                if canister_id:
                    record['slow_movers'] = slow_movers
                    record['slow_movers'][canister_id] = record["slow_movers"][canister_id][0]

            if same_drug_canisters:
                record["same_canister_available"] = True
            else:
                record["same_canister_available"] = False
            response_list.append(record)
        inventory_data = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        inventory_data_dict = {}
        for item in inventory_data:
            inventory_data_dict[item['ndc']] = item['quantity']

        for record in response_list:
            record['inventory_qty'] = inventory_data_dict.get(record['alt_ndc'], 0)
            record['is_in_stock'] = 0 if record["inventory_qty"] <= 0 else 1
        return response_list

    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_alternate_drug_canisters {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_alternate_drug_canisters {}".format(e))
        raise e


@log_args_and_response
def db_get_alternate_drugs(canister_id: int, company_id: int, same_drug_canisters: bool = None) -> list:
    """
    Returns alternate drugs for given canister id
    :param canister_id: int
    :param company_id: int
    :return: list
    """
    results: list = list()
    try:
        current_canister = CanisterMaster.select(DrugMaster,
                                                 LocationMaster.device_id,
                                                 LocationMaster.location_number,
                                                 LocationMaster.display_location,
                                                 DeviceMaster.device_type_id,
                                                 DeviceMaster.id,
                                                 ContainerMaster.id.alias('drawer_id'),
                                                 ContainerMaster.drawer_name.alias('drawer_number'),
                                                 ContainerMaster.serial_number,
                                                 ContainerMaster.ip_address,
                                                 ContainerMaster.mac_address,
                                                 ContainerMaster.secondary_mac_address,
                                                 ContainerMaster.secondary_ip_address,
                                                 DeviceMaster.name.alias('device_nae')).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id, ) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.company_id == company_id,
                   CanisterMaster.id == canister_id,
                   CanisterMaster.active == settings.is_canister_active,
                   DrugMaster.brand_flag == settings.GENERIC_FLAG).get()
    except DoesNotExist:
        # current canister invalid or not generic drug, so return empty list
        return results

    try:
        # removed generic flog as these will be disabled from FE.
        query = DrugMaster.select(DrugMaster.id.alias('alt_drug_id'),
                                  DrugMaster.drug_name.alias('alt_drug_name'),
                                  DrugMaster.formatted_ndc.alias('alt_formatted_ndc'),
                                  DrugMaster.txr.alias('alt_txr'),
                                  DrugMaster.ndc.alias('alt_ndc'),
                                  DrugMaster.strength.alias('alt_strength'),
                                  DrugMaster.strength_value.alias('alt_strength_value'),
                                  DrugMaster.imprint.alias('alt_imprint'),
                                  UniqueDrug.is_powder_pill.alias('alt_is_powder_pill'),
                                  DrugMaster.brand_flag.alias('alt_brand_flag'),
                                  DrugMaster.image_name.alias('alt_image_name'),
                                  DrugMaster.color.alias('alt_color'),
                                  DrugMaster.shape.alias('alt_shape'),
                                  DrugMaster.id.alias('drug_id'),
                                  DrugStatus.ext_status.alias('alt_ext_status'),
                                  DrugStatus.ext_status_updated_date.alias('alt_ext_status_updated_date'),
                                  DrugStatus.last_billed_date.alias('alt_last_billed_date'),
                                  DrugMaster.concated_drug_name_field(include_ndc=True).alias('alt_drug')) \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(DrugMaster.formatted_ndc != current_canister['formatted_ndc'],
                   DrugMaster.txr == current_canister['txr'],
                   DrugMaster.brand_flag == settings.GENERIC_FLAG) \
            .order_by(DrugStatus.ext_status.desc(), SQL('FIELD(alt_brand_flag, "1")').desc(),
                      DrugStatus.last_billed_date)

        for record in query.dicts():
            if same_drug_canisters:
                record["same_canister_available"] = True
            else:
                record["same_canister_available"] = False
            record.update(current_canister)  # add current canister's drug data
            results.append(record)
        logger.info("In db_get_alternate_drugs: result: {}".format(results))

        return results

    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_alternate_drugs {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_alternate_drugs {}".format(e))
        raise e


@log_args_and_response
def update_alternate_drug_canister_for_batch_data(canister_id: int, alt_canister_id: int, device_id: int,
                                                  user_id: int, company_id: int, current_pack_id: int = None, batch_id: int = None):
    """
    Returns alternate drugs for given canister id
    update patient_rx, IPS and canister id in pack analysis
    update IPS about alt drug in packs
    if success in IPS update, end transaction
        @param batch_id:
        @param canister_id:
        @param alt_canister_id:
        @param device_id:
        @param user_id:
        @param company_id:
        @param current_pack_id:
        @return:
    """
    try:
        current_canister = get_canister_by_id_dao(canister_id=canister_id)
        alternate_canister = get_canister_by_id_dao(canister_id=alt_canister_id)

        valid_alternate_drug_canister = current_canister and alternate_canister \
                                        and current_canister['formatted_ndc'] != alternate_canister['formatted_ndc'] \
                                        and current_canister['txr'] == alternate_canister['txr'] \
                                        and str(current_canister['brand_flag']) == str(alternate_canister['brand_flag']) \
                                        == settings.GENERIC_FLAG
        # and alternate_canister['ext_status'] == settings.VALID_EXT_STATUS

        logger.info("In update_alternate_drug_canister_for_batch_data: valid_alternate_drug_canister: {}".format(valid_alternate_drug_canister))
        if not valid_alternate_drug_canister:
            raise ValueError(' canister_id and alt_canister_id does not have alternate drugs')

        old_drug_ids = [item.id for item in DrugMaster.get_drugs_by_formatted_ndc_txr(formatted_ndc=current_canister['formatted_ndc'],
                                                                                      txr=current_canister['txr'])]
        logger.info("In update_alternate_drug_canister_for_batch_data: old_drug_ids: {}".format(old_drug_ids))
        # current_canister_list = [
        #     item['id'] for item in CanisterMaster.db_get_canisters_by_fndc_txr(
        #         current_canister['formatted_ndc'] + '#' + current_canister['txr'],
        #         company_id, device_id
        #     )
        # ]
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in update_alternate_drug_canister_for_batch_data: {}".format(e))
        raise e

    try:
        # drug_id = current_canister['drug_id']
        alt_drug_id = alternate_canister['drug_id']
        if batch_id:
            mfd_pack_ids = get_mfd_drug_packs(batch_id=batch_id, old_drug_ids=old_drug_ids)
        else:
            mfd_pack_ids = get_mfd_drug_packs_pack_queue(old_drug_ids)
        # todo : Change the above function after rewriting mds flow
        logger.info("In update_alternate_drug_canister_for_batch_data: mfd_pack_ids: {}".format(mfd_pack_ids))

        clauses = [PatientRx.daw_code == 0]

        if mfd_pack_ids:
            clauses.append((PackDetails.id.not_in(mfd_pack_ids)))

        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info("In update_alternate_drug_canister_for_batch_data: filling_pending_pack_ids: {}, current_pack_id: {}".format(filling_pending_pack_ids, current_pack_id))

        if current_pack_id:
            filling_pending_pack_ids.append(current_pack_id)
        if filling_pending_pack_ids:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                           | (PackDetails.id << filling_pending_pack_ids))
        else:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        # get pending packs query
        pending_packs = PackDetails.select(PackDetails.id).distinct() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(*clauses)

        packs_to_update = PackAnalysis.select(PackAnalysis.pack_id,
                                              PatientRx.daw_code,
                                              SlotDetails.id.alias('slot_id'),
                                              PackAnalysis.id.alias('analysis_id')) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(SlotDetails.drug_id << old_drug_ids,
                   PackAnalysis.pack_id << pending_packs,
                   PackAnalysisDetails.device_id == device_id)

        daw_zero_analysis_ids_set: set = set()
        null_canister_analysis_ids_set: set = set()
        robot_packs: set = set()
        robot_analysis_id: set = set()
        pack_ids: list = list()
        drug_list: list = list()
        alt_drug_list: list = list()
        slot_ids: list = list()
        null_canister_pack_ids: set = set()

        for record in packs_to_update.dicts():
            pack_ids.append(record['pack_id'])
            if record['daw_code'] == 0:
                daw_zero_analysis_ids_set.add(record['analysis_id'])
            else:
                null_canister_pack_ids.add(record['pack_id'])
                null_canister_analysis_ids_set.add(record['analysis_id'])
            slot_ids.append(record['slot_id'])
        daw_zero_analysis_ids = list(daw_zero_analysis_ids_set)
        null_canister_analysis_ids = list(null_canister_analysis_ids_set)
        logger.info("In  update_alternate_drug_canister_for_batch_data: daw_zero_analysis_ids: {}, null_canister_analysis_ids: {}, slot_ids: {}, null_canister_pack_ids: {}"
                    .format(daw_zero_analysis_ids, null_canister_analysis_ids, slot_ids, null_canister_pack_ids))

        # as no packs needs update, so returning True as no action required
        if not pack_ids:
            logger.info(
                'In update_alternate_drug_canister_for_batch_data: For No packs were updated for action alt_drug_canister. Other params '
                'canister_id: {}, alt_canister_id: {}, robot_id: {}, current_pack_id: {}'
                .format(canister_id, alt_canister_id, device_id, current_pack_id))
            return True, []

        query = PackRxLink.select(PackRxLink.pack_id,
                                  SlotDetails.drug_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .where(PackRxLink.pack_id << pack_ids,
                    SlotDetails.drug_id << old_drug_ids)

        pack_list: list = list()
        for record in query.dicts():
            pack_list.append(record['pack_id'])
            if record['drug_id'] not in drug_list:
                drug_list.append(record['drug_id'])
                alt_drug_list.append(alt_drug_id)

        logger.info("In update_alternate_drug_canister_for_batch_data: pack_list: {}, drug_list: {}, alt_drug_list: {}".format(
                pack_list, drug_list, alt_drug_list))

        if null_canister_analysis_ids:
            remaining_analysis_ids = PackAnalysis.select(PackAnalysis.id,
                                                         fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.location_number)).coerce(False).alias('location_number'),
                                                         fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.canister_id)).coerce(False).alias('canister_id')) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .where(SlotDetails.drug_id.not_in(old_drug_ids),
                       PackAnalysis.pack_id << list(null_canister_pack_ids),
                       PackAnalysisDetails.device_id == device_id)\
                .group_by(PackAnalysis.pack_id)

            for record in remaining_analysis_ids.dicts():
                if record['canister_id'] and record['location_number']:
                    canister_ids = list(record['canister_id'].split(","))
                    location_number = list(record['location_number'].split(","))

                    analysis_ids = list(record['analysis_id'].split(","))

                    if not any(canister_ids) is False and not any(location_number) is False:
                        robot_packs.add(record['pack_id'])
                        robot_analysis_id.update(analysis_ids)

            manual_pack_list = list(null_canister_pack_ids - robot_packs)
            logger.info("In update_alternate_drug_canister_for_batch_data: robot_packs: {}, robot_analysis_id: {}, manual_pack_list: {}".format(
                    robot_packs, robot_analysis_id, manual_pack_list))

            if manual_pack_list:
                for current_in_progress_pack in filling_pending_pack_ids:
                    if current_in_progress_pack in manual_pack_list:
                        manual_pack_list.remove(current_in_progress_pack)

                if manual_pack_list:
                    return False, manual_pack_list

        daw_zero_analysis_ids = list(daw_zero_analysis_ids)

        # keeping canister ids in the analysis details id where daw code is not zero as we are not changing drug so
        # drug and canister drug won't create conflict
        logger.info(
            'In update_alternate_drug_canister_for_batch_data : Alternate drug canister data for: canister_id: {} and alt_canister_id:  {} :: '
            'daw_zero_analysis_ids {}, null_canister_analysis_ids {} and robot_packs {}'.format(
                canister_id, alt_canister_id, daw_zero_analysis_ids, null_canister_analysis_ids, robot_packs))

        with db.transaction():
            # removing canister related data as in packs having non-zero daw code drug can't be changed
            if old_drug_ids and null_canister_analysis_ids:
                update_dict = {'location_number': None,
                               'quadrant': None,
                               'drop_number': None,
                               'config_id': None,
                               'device_id': None,
                               'canister_id': None
                               }
                pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(update_dict=update_dict,
                                                                                   analysis_id=null_canister_analysis_ids,
                                                                                   slot_id=slot_ids,
                                                                                   device_id=device_id)
                logger.info("In update_alternate_drug_canister_for_batch_data: pack_analysis_status: {}".format(
                        pack_analysis_status))

            if old_drug_ids and daw_zero_analysis_ids:
                update_dict = {'canister_id': alt_canister_id}
                pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(update_dict=update_dict,
                                                                                                          analysis_id=daw_zero_analysis_ids,
                                                                                                         slot_id=slot_ids,
                                                                                                         device_id=device_id)
                logger.info("In update_alternate_drug_canister_for_batch_data: pack_analysis_status for daw_zero_analysis_ids: {}".format(pack_analysis_status))


                response = alternate_drug_update({'pack_list': ','.join(map(str, pack_list)),
                                                  'olddruglist': ','.join(map(str, drug_list)),
                                                  'newdruglist': ','.join(map(str, alt_drug_list)),
                                                  'user_id': user_id,
                                                  'company_id': company_id,
                                                  'module_id': constants.PDT_REPLENISH_ALTERNATES
                                                  })
                response = json.loads(response)
                if response['status'] != 'success':
                    # throwing exception to rollback changes as we could not update IPS
                    raise AlternateDrugUpdateException(response['code'])

                status = ReservedCanister.db_replace_canister(canister_id=None,
                                                              alt_canister_id=alt_canister_id,
                                                              canister_ids=[canister_id])
                logger.info(
                    "In update_alternate_drug_canister_for_batch_data: update status for reserved canister: {}".format(
                        status))
                BatchChangeTracker.db_save(batch_id=batch_id,
                                           user_id=user_id,
                                           action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.UPDATE_ALT_DRUG_CANISTER],
                                           params={"canister_id": canister_id,
                                                   "alt_canister_id": alt_canister_id,
                                                   "current_canister_list": [canister_id],
                                                   "batch_id": batch_id,
                                                   "current_pack_id": current_pack_id,
                                                   },
                                           packs_affected=pack_list
                                           )
                return True, pack_list
            else:
                return False, []

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_alternate_drug_canister_for_batch_data {}".format(e))
        raise
    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in update_alternate_drug_canister_for_batch_data: PharmacySoftwareCommunicationException {}".format(e))
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error("Error in update_alternate_drug_canister_for_batch_data: PharmacySoftwareResponseException {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_alternate_drug_canister_for_batch_data {}".format(e))
        raise e


@log_args_and_response
def get_mfd_drug_packs(batch_id: int, old_drug_ids: list) -> List:
    """
    returns query to get the analysis info for the specified ndc
    :param batch_id: int
    :param old_drug_ids: list
    :return: query
    """
    pack_ids: list = list()
    try:
        mfd_status = [constants.MFD_CANISTER_SKIPPED_STATUS,
                      constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                      constants.MFD_CANISTER_RTS_DONE_STATUS]

        query = MfdAnalysis.select(PackRxLink.pack_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .where(SlotDetails.drug_id << old_drug_ids,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.status_id.not_in(mfd_status),
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])
        for record in query.dicts():
            pack_ids.append(record['pack_id'])

        return pack_ids
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_mfd_drug_packs {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_mfd_drug_packs {}".format(e))
        raise e


@log_args_and_response
def update_alternate_drug_for_batch_data(canister_id: int, alt_drug_id: int, batch_id: int,
                                         current_pack_id: int, device_id: int, user_id: int, company_id: int) -> tuple:
    """
        update alternate drug for batch
        :return: query
        @param canister_id:
        @param alt_drug_id:
        @param batch_id:
        @param current_pack_id:
        @param device_id:
        @param user_id:
        @param company_id:
        @return:
        """

    try:
        current_drug = get_canister_by_id_dao(canister_id)
        alternate_drug = db_get_drug_status_by_id(drug_id=alt_drug_id, dicts=True)
        valid_alternate_drug = current_drug and alternate_drug \
                               and current_drug['formatted_ndc'] != alternate_drug['formatted_ndc'] \
                               and current_drug['txr'] == alternate_drug['txr'] \
                               and str(current_drug['brand_flag']) == \
                               str(alternate_drug['brand_flag']) == settings.GENERIC_FLAG
        # and alternate_drug['ext_status'] == settings.VALID_EXT_STATUS

        logger.info("In update_alternate_drug_for_batch_data: valid_alternate_drug: {}".format(valid_alternate_drug))
        if not valid_alternate_drug:
            raise ValueError(' drug_id and alt_drug_id are not alternate drugs')

        old_drug_ids = [item.id for item in DrugMaster.get_drugs_by_formatted_ndc_txr(formatted_ndc=current_drug['formatted_ndc'],
                                                                                      txr=current_drug['txr'])]
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e

    try:
        # drug_id = current_drug['drug_id']
        alt_drug_id = alternate_drug['id']
        mfd_pack_ids = get_mfd_drug_packs(batch_id, old_drug_ids)
        logger.info("In update_alternate_drug_for_batch_data: mfd_pack_ids: {}".format(mfd_pack_ids))

        clauses = [PackDetails.batch_id == batch_id]

        if mfd_pack_ids:
            clauses.append(PackDetails.id.not_in(mfd_pack_ids))

        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info("In update_alternate_drug_for_batch_data: current_pack_id: {}, filling_pending_pack_ids: {}".format(current_pack_id, filling_pending_pack_ids))

        if current_pack_id:
            filling_pending_pack_ids.append(current_pack_id)
        if filling_pending_pack_ids:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                           | (PackDetails.id << filling_pending_pack_ids))
        else:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        # query to get pending packs
        pending_packs = PackDetails.select(PackDetails.id).distinct() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(*clauses)

        # update data of pending packs
        packs_to_update = PackAnalysis.select(PackAnalysis.pack_id,
                                              PackAnalysisDetails.slot_id,
                                              PatientRx.daw_code,
                                              PackAnalysis.id.alias('analysis_id')) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(SlotDetails.drug_id << old_drug_ids,
                   PackAnalysis.pack_id << pending_packs,
                   PackAnalysisDetails.device_id == device_id)

        daw_zero_analysis_ids_set: set = set()
        non_zero_daw_analysis_ids_set: set = set()
        pack_ids: list = list()
        drug_list: list = list()
        # pack_analysis_id_dict = dict()
        alt_drug_list: list = list()
        slot_ids: list = list()

        for record in packs_to_update.dicts():
            pack_ids.append(record['pack_id'])
            if record['daw_code'] == 0:
                daw_zero_analysis_ids_set.add(record['analysis_id'])
            else:
                non_zero_daw_analysis_ids_set.add(record['analysis_id'])
            slot_ids.append(record['slot_id'])

        logger.info("In update_alternate_drug_for_batch_data: pack_ids: {}, old_drug_ids: {}, daw_zero_analysis_ids: {}, non_zero_daw_analysis_ids: {}, slot_ids: {}"
                    .format(pack_ids, old_drug_ids, daw_zero_analysis_ids_set, non_zero_daw_analysis_ids_set, slot_ids))
        if not pack_ids or not old_drug_ids:
            # as no packs needs update, so returning True as no action required
            return True, []

        daw_zero_analysis_ids = list(daw_zero_analysis_ids_set)
        non_zero_daw_analysis_ids = list(non_zero_daw_analysis_ids_set)

        query = PackRxLink.select(PackRxLink.pack_id,
                                  SlotDetails.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(PackRxLink.pack_id << pack_ids,
                   SlotDetails.drug_id << old_drug_ids)

        pack_list: list = list()

        for record in query.dicts():
            pack_list.append(record['pack_id'])
            if record['drug_id'] not in drug_list:
                drug_list.append(record['drug_id'])
                alt_drug_list.append(alt_drug_id)

        logger.info("In update_alternate_drug_for_batch_data: pack_list: {}, drug_list: {}, alt_drug_list: {}"
            .format(pack_list, drug_list, alt_drug_list))

        remaining_analysis_ids = PackAnalysis.select(PackAnalysis.id.alias('analysis_id'),
                                                     PackAnalysis.pack_id,
                                                     fn.GROUP_CONCAT(
                                                         fn.DISTINCT(PackAnalysisDetails.location_number)).coerce(
                                                         False).alias('location_number'),
                                                     fn.GROUP_CONCAT(
                                                         fn.DISTINCT(PackAnalysisDetails.canister_id)).coerce(
                                                         False).alias('canister_id')) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(SlotDetails.drug_id.not_in(old_drug_ids),
                   PackAnalysis.pack_id << pack_list,
                   PackAnalysisDetails.device_id == device_id) \
            .group_by(PackAnalysis.pack_id)

        robot_packs: set = set()
        # robot_analysis_ids = set()
        for record in remaining_analysis_ids.dicts():
            if record['canister_id'] and record['location_number']:
                canister_ids = list(record['canister_id'].split(","))
                location_number = list(record['location_number'].split(","))

                if not any(canister_ids) is False and not any(location_number) is False:
                    robot_packs.add(record['pack_id'])

        manual_pack_list = list(set(pack_list) - robot_packs)

        logger.info("In update_alternate_drug_for_batch_data: robot_packs: {}, manual_pack_list: {}"
                    .format(robot_packs, manual_pack_list))

        if manual_pack_list:
            for current_in_progress_pack in filling_pending_pack_ids:
                if current_in_progress_pack in manual_pack_list:
                    manual_pack_list.remove(current_in_progress_pack)
            if manual_pack_list:
                logger.info(
                    'In update_alternate_drug_for_batch_data: Alternate drug data for: canister_id: {} and alt_drug:  {} :: daw_zero_analysis_ids {},'
                    ' non_zero_daw_analysis_ids {} and manual_pack_list {}'.format(
                        canister_id, alt_drug_id, daw_zero_analysis_ids, non_zero_daw_analysis_ids, manual_pack_list))
                return False, manual_pack_list

        pack_analysis_id_list = daw_zero_analysis_ids

        # keeping canister ids in the analysis details id where daw code is not zero as we are not changing drug so
        # drug and canister drug won't create conflict
        canister_analysis_ids = list(non_zero_daw_analysis_ids)
        logger.info(
            'In update_alternate_drug_for_batch_data: Alternate drug data for: canister_id: {} and alt_drug:  {} :: pack_analysis_id_list {},'
            ' canister_analysis_ids {}'.format(
                canister_id, alt_drug_id, pack_analysis_id_list, canister_analysis_ids))

        with db.transaction():
            if len(pack_analysis_id_list):
                update_dict = {'location_number': None,
                               'quadrant': None,
                               'canister_id': None,
                               'drop_number': None,
                               'config_id': None
                               }
                pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(update_dict=update_dict,
                    analysis_id=pack_analysis_id_list,
                    slot_id=slot_ids,
                    device_id=device_id)
                logger.info("In update_alternate_drug_for_batch_data: pack_analysis_status: {} for pack_analysis_id_list: {}".format(
                    pack_analysis_status, pack_analysis_id_list))

            if canister_analysis_ids:
                update_dict = {'location_number': None,
                               'quadrant': None,
                               'drop_number': None,
                               'config_id': None
                               }
                pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(
                    update_dict=update_dict,
                    analysis_id=canister_analysis_ids,
                    slot_id=slot_ids,
                    device_id=device_id)
                logger.info("In update_alternate_drug_for_batch_data: pack_analysis_status: {} for canister_analysis_ids :{}".format(
                    pack_analysis_status, canister_analysis_ids))

            if daw_zero_analysis_ids and old_drug_ids:
                # delete reserved canister data
                status = ReservedCanister.db_remove_reserved_canister(canister_ids=[canister_id])
                logger.info("In update_alternate_drug_for_batch_data: reserved canister: {} deleted:{}".format(
                        canister_id, status))
                response = alternate_drug_update({'pack_list': ','.join(map(str, pack_list)),
                                                  'olddruglist': ','.join(map(str, drug_list)),
                                                  'newdruglist': ','.join(map(str, alt_drug_list)),
                                                  'user_id': user_id,
                                                  'company_id': company_id,
                                                  'module_id': constants.PDT_REPLENISH_ALTERNATES
                                                  })
                response = json.loads(response)
                if response['status'] != 'success':
                    # throwing exception to rollback changes as we could not update IPS
                    raise AlternateDrugUpdateException(response['code'])

                BatchChangeTracker.db_save(batch_id=batch_id,
                                           user_id=user_id,
                                           action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.UPDATE_ALT_DRUG],
                                           params={"canister_id": canister_id,
                                                   "alt_drug_id": alt_drug_id,
                                                   "batch_id": batch_id,
                                                   "current_pack_id": current_pack_id,
                                                   "user_id": user_id},
                                           packs_affected=pack_list)
                return True, pack_list
            else:
                return False, []

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e
    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in update_alternate_drug_for_batch_data: PharmacySoftwareCommunicationException {}".format(e))
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error("Error in update_alternate_drug_for_batch_data: PharmacySoftwareResponseException {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e


@log_args_and_response
def get_canister_by_id_dao(canister_id: int) -> dict:
    """
        Returns dict of canister data
        @param canister_id:
        @return:
    """
    canister_data: dict = dict()

    try:
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                      CanisterMaster.drug_id,
                                      CanisterMaster.active,
                                      UniqueDrug.lower_level,
                                      LocationMaster.location_number,
                                      LocationMaster.is_disabled.alias('is_location_disabled'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                                 SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
                                      DeviceMaster.system_id,
                                      CanisterMaster.available_quantity,
                                      fn.IF(CanisterMaster.available_quantity < 0, 0,
                                            CanisterMaster.available_quantity).alias('display_quantity'),
                                      CanisterMaster.rfid,
                                      DrugMaster.drug_name,
                                      DrugMaster.ndc,
                                      DrugMaster.txr,
                                      DrugMaster.strength,
                                      DrugMaster.strength_value,
                                      DrugMaster.imprint,
                                      DrugMaster.image_name,
                                      DrugMaster.shape,
                                      DrugMaster.color,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.manufacturer,
                                      DrugMaster.brand_flag,
                                      DrugMaster.drug_form,
                                      DrugStatus.ext_status,
                                      CanisterMaster.canister_type,
                                      CanisterMaster.product_id,
                                      CanisterMaster.company_id,
                                      CanisterStick.big_canister_stick_id,
                                      CanisterStick.small_canister_stick_id,
                                      CustomDrugShape.name.alias("drug_shape_name")).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(DrugStatus, on=DrugMaster.id == DrugStatus.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                  & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(DrugCanisterStickMapping, JOIN_LEFT_OUTER,
                  on=DrugCanisterStickMapping.drug_dimension_id == DrugDimension.id) \
            .join(CanisterStick, JOIN_LEFT_OUTER,
                  CanisterStick.id == DrugCanisterStickMapping.canister_stick_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .where(CanisterMaster.id == canister_id).group_by(CanisterMaster.id)
        for record in query:
            canister_data = record

        return canister_data

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_by_id_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_by_id_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_drug_status_by_id(drug_id: int, dicts=False):
    try:
        drug = DrugMaster.select(DrugStatus.ext_status,
                                 DrugMaster)\
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id)\
            .where(DrugMaster.id == drug_id)
        if dicts:
            drug = drug.dicts()
        return drug.get()
    except (DoesNotExist, IntegrityError, InternalError) as e:
        logger.error("error in db_get_drug_status_by_id {}".format(e))
        raise


@log_args_and_response
def db_skip_for_batch(batch_id: int, canister_list: list, user_id: int, current_pack: int = None) -> tuple:
    """
    Canister will be not be considered for pending packs
    :param batch_id: int
    :param canister_list: List<int>
    :param user_id: int
    :param current_pack: int pack id whose pack_status is not pending and being filled by robot right now
    :return: bool
    """
    try:
        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info("In db_skip_for_batch: filling_pending_pack_ids: {}, current_pack: {},canister_list: {}"
                    .format(filling_pending_pack_ids, current_pack, canister_list))
        if current_pack:
            filling_pending_pack_ids.append(current_pack)
        if not canister_list:
            return False, None

        clauses = [PackAnalysis.batch_id == batch_id]

        if filling_pending_pack_ids:
            clauses.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                            | (PackDetails.id << filling_pending_pack_ids)))
        else:
            clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS])

        affected_packs: set = set()
        pack_analysis_id_set: set = set()
        pack_analysis_id_dict: dict = dict()
        pack_canister_dict = dict()
        canister_location_dict = dict()
        delete_reserved_canister_analysis_id = list()

        pack_analysis_list = PackAnalysis.select(PackAnalysis.id, PackAnalysis.pack_id, PackAnalysisDetails.canister_id,
                                                 PackAnalysisDetails.location_number,
                                                 PackAnalysisDetails.device_id,
                                                 PackAnalysisDetails.quadrant).dicts() \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(*clauses, PackAnalysisDetails.canister_id << canister_list)

        for record in pack_analysis_list:
            affected_packs.add(record['pack_id'])
            pack_analysis_id_set.add(record['id'])
            canister_location_dict[record["canister_id"]] = {'device_id': record["device_id"],
                                                             'quadrant': record["quadrant"],
                                                             'location_number': record["location_number"]}

            if record['pack_id'] not in pack_analysis_id_dict.keys():
                pack_analysis_id_dict[record['pack_id']] = set()
                pack_canister_dict[record['pack_id']] = set()
            pack_analysis_id_dict[record['pack_id']].add(record['id'])
            pack_canister_dict[record['pack_id']].add(record['canister_id'])

        logger.info("In db_skip_for_batch: pack_analysis_ids:{}, pack_analysis_id_dict: {},affected_packs: {} "
                    .format(pack_analysis_id_set, pack_analysis_id_dict, affected_packs))

        if not affected_packs:
            logger.info('No_packs_found_while_skipping_for_batch_for_canister: ' + str(canister_list))
            return True, None

        robot_analysis_ids: set = set()
        # robot_pack_canister_list: list = list()
        robot_pack_canister_dict = dict()

        non_robot_analysis_ids: set = set()
        # non_robot_pack_canister_list = list()
        non_robot_pack_canister_dict = dict()

        robot_packs: set = set()
        logger.info("In db_skip_for_batch : affected packs {}".format(affected_packs))
        if len(affected_packs):
            remaining_analysis_ids = PackAnalysis.select(fn.GROUP_CONCAT(
                                                             PackAnalysis.id).coerce(
                                                             False).alias('analysis_id'),
                                                         PackAnalysis.pack_id,
                                                         fn.GROUP_CONCAT(
                                                             PackAnalysisDetails.location_number).coerce(
                                                             False).alias('location_number'),
                                                         fn.GROUP_CONCAT(PackAnalysisDetails.canister_id).coerce(
                                                             False).alias('canister_id'),
                                                         fn.GROUP_CONCAT(fn.DISTINCT(fn.CONCAT(PackAnalysisDetails.canister_id, "-", PackAnalysisDetails.device_id, "-", PackAnalysisDetails.quadrant, "-", PackAnalysisDetails.location_number))).alias('can_destination')) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(*clauses, PackAnalysis.pack_id << list(affected_packs),
                       PackAnalysisDetails.canister_id.not_in(canister_list),
                       PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED) \
                .group_by(PackAnalysis.pack_id)

            for record in remaining_analysis_ids.dicts():
                if record['canister_id'] and record['location_number']:
                    canister_id = list(record['canister_id'].split(","))
                    location_number = list(record['location_number'].split(","))
                    analysis_ids = list(record['analysis_id'].split(","))
                    can_destination_list = list(record["can_destination"].split(","))
                    d = {}
                    d = {i.split("-", 1)[0]: {"device_id": i.split("-")[1], "quadrant": i.split("-")[2],
                                              "location_number": i.split("-")[3]} for i in can_destination_list}
                    canister_location_dict.update(d)

                    if not any(canister_id) is False and not any(location_number) is False:
                        robot_packs.add(record['pack_id'])
                        if record['pack_id'] in filling_pending_pack_ids:
                            non_robot_analysis_ids.update(analysis_ids)
                            if not non_robot_pack_canister_dict.get(record["pack_id"]):
                                non_robot_pack_canister_dict[record["pack_id"]] = set()
                            non_robot_pack_canister_dict[record["pack_id"]].update(canister_id)
                            # non_robot_pack_canister_list.extend(
                            #     [{"pack_id": record['pack_id'], "canister_id": canister} for canister in canister_id])
                        else:
                            robot_analysis_ids.update(analysis_ids)
                            if not robot_pack_canister_dict.get(record["pack_id"]):
                                robot_pack_canister_dict[record["pack_id"]] = set()
                            robot_pack_canister_dict[record["pack_id"]].update(canister_id)
                            # robot_pack_canister_list.extend(
                            #     [{"pack_id": record['pack_id'], "canister_id": canister} for canister in canister_id])
        manual_pack_list = list(affected_packs - robot_packs)
        logger.info("In db_skip_for_batch manual pack list: robot_packs: {},non_robot_analysis_ids: {}, robot_analysis_ids: {}"
                    .format(robot_packs, non_robot_analysis_ids, robot_analysis_ids))

        if len(manual_pack_list):
            for current_in_progress_pack in filling_pending_pack_ids:
                if current_in_progress_pack in manual_pack_list:
                    if current_in_progress_pack in pack_analysis_id_dict.keys():
                        non_robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        if not non_robot_pack_canister_dict.get(current_in_progress_pack):
                            non_robot_pack_canister_dict[current_in_progress_pack] = set()
                        non_robot_pack_canister_dict[current_in_progress_pack].update(
                            pack_canister_dict[current_in_progress_pack])
                        # non_robot_pack_canister_list.extend(
                        #     [{"pack_id": current_in_progress_pack, "canister_id": canister} for canister in
                        #      pack_canister_dict[current_in_progress_pack]])
                    else:
                        robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        robot_pack_canister_dict[current_in_progress_pack].update(pack_canister_dict[current_in_progress_pack])

                    manual_pack_list.remove(current_in_progress_pack)

            logger.info("In db_skip_for_batch: non_robot_analysis_ids: {},robot_analysis_ids: {},manual_pack_list: {} "
                        .format(non_robot_analysis_ids, robot_analysis_ids, manual_pack_list))

            if manual_pack_list:
                mfd_pack_list = get_mfd_packs_from_given_pack_list(batch_id=batch_id,
                                                                   pack_list=manual_pack_list)
                logger.info("In db_skip_for_batch :mfd pack list {}".format(mfd_pack_list))

                if len(mfd_pack_list):
                    for pack in mfd_pack_list:
                        non_robot_analysis_ids.update(pack_analysis_id_dict[pack])
                        if not non_robot_pack_canister_dict.get(pack):
                            non_robot_pack_canister_dict[pack] = set()
                        non_robot_pack_canister_dict[pack].update(pack_canister_dict[pack])
                        # non_robot_pack_canister_list.extend(
                        #     [{"pack_id": pack, "canister_id": canister} for canister in
                        #      pack_canister_dict[pack]])
                    manual_pack_list = list(set(manual_pack_list) - set(mfd_pack_list))

                if len(manual_pack_list):
                    return False, manual_pack_list

        insert_list = []
        if non_robot_analysis_ids or robot_analysis_ids:
            analysis_ids = list(non_robot_analysis_ids) + list(robot_analysis_ids)
            insert_list = get_insert_list_of_replenish_skipped_canister(analysis_ids, canister_list)
            logger.info(f"In db_skip_for_batch, insert_list: {insert_list}")

        with db.transaction():
            if len(non_robot_analysis_ids):
                logger.info("In db_skip_for_batch: non_robot_analysis_ids {}".format(non_robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None}
                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in non_robot_pack_canister_dict.items() for can in canisters]
                # logger.info(f"In db_skip_for_batch non_robot_analysis_ids insert_list: {insert_list}")
                #
                # insert_status = ReplenishSkippedCanister.insert_many(insert_list).execute()
                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(non_robot_analysis_ids))
                logger.info("In db_skip_for_batch: pack_analysis_status: {} for non_robot_analysis_ids: {}".format(
                    status, non_robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(non_robot_analysis_ids)


            if len(robot_analysis_ids):
                logger.info("db_skip_for_batch robot_analysis_ids {}".format(robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'canister_id': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None
                #                }
                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}

                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in robot_pack_canister_dict.items() for can in canisters]
                # logger.info(f"In db_skip_for_batch robot_analysis_ids insert_list: {insert_list}")
                #
                # insert_status = ReplenishSkippedCanister.insert_many(insert_list).execute()
                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(robot_analysis_ids))
                logger.info("In db_skip_for_batch: pack_analysis_status: {} for robot_analysis_ids: {}".format(
                    status, robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(robot_analysis_ids)

            if insert_list:
                status = ReplenishSkippedCanister.insert_many(insert_list).execute()
                logger.info(f"In db_skip_for_batch, insert status: {status}")

            if delete_reserved_canister_analysis_id:
                status = delete_reserved_canister_for_skipped_canister(canister_list=canister_list, analysis_id=delete_reserved_canister_analysis_id)
                logger.info("In db_skip_for_batch: reserved canister: {} deleted:{}".format(canister_list, status))
            BatchChangeTracker.db_save(batch_id=batch_id,
                                       user_id=user_id,
                                       action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.SKIP_FOR_BATCH],
                                       params={"canister_list": canister_list,
                                               "batch_id": batch_id,
                                               "user_id": user_id},
                                       packs_affected=list(affected_packs)
                                       )
            return True, list(affected_packs)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in db_skip_for_batch: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in db_skip_for_batch: {}".format(e))
        raise e


@log_args_and_response
def get_mfd_packs_from_given_pack_list(batch_id: int, pack_list: list) -> list:
    """
    Function to get mfd packs from given pack list and batch
    @param pack_list: list
    @param batch_id: int
    @return:
    """
    mfd_pack_list = list()
    try:
        mfd_status = [constants.MFD_CANISTER_SKIPPED_STATUS,
                      constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                      constants.MFD_CANISTER_RTS_DONE_STATUS]

        query = MfdAnalysis.select(PackDetails.id.alias('pack_id')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.batch_id == batch_id,
                   PackDetails.id << pack_list,
                   MfdAnalysis.status_id.not_in(mfd_status)) \
            .group_by(PackDetails.id)

        for record in query:
            mfd_pack_list.append(record['pack_id'])

        return mfd_pack_list

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_mfd_packs_from_given_pack_list: {}".format(e))
        raise e


@log_args_and_response
def db_skip_canister_for_packs(batch_id: int, canister_list: list, user_id: int, current_pack: int = None,
                               device_id: int = None, pack_count: int = None, manual_pack_count: int = None) -> tuple:
    """
    Canister will be not be considered for pending packs
    @param batch_id:
    @param canister_list:
    @param user_id:
    @param current_pack: int pack id whose pack_status is not pending and being filled by robot right now
    @param device_id:
    @param pack_count: number of packs till which this canister should be skipped
    @param manual_pack_count: if some packs moved to manual then manual pack count to decrement from original pack count
    @return:
    """
    try:
        if manual_pack_count:
            pack_count = pack_count - manual_pack_count

        logger.info("In db_skip_canister_for_packs: pack_count: {}".format(pack_count))
        if not pack_count or pack_count <= 0:
            return True, []

        affected_packs: set = set()
        pack_analysis_id_set: set = set()
        pack_analysis_id_dict: dict = dict()
        pack_canister_dict = dict()
        packs_to_skip: list = list()
        delete_reserved_canister_analysis_id = list()
        canister_location_dict = dict()

        # check data for filling pending packs, i.e packs are in progress but not filled
        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids_device_wise(batch_id=batch_id, device_id=device_id)
        logger.info("In db_skip_canister_for_packs: filling_pending_pack_ids: {}, current_pack: {}"
                    .format(filling_pending_pack_ids, current_pack))

        if current_pack and current_pack not in filling_pending_pack_ids:
            filling_pending_pack_ids.append(current_pack)
        if not canister_list:
            return False, None

        logger.info("db_skip_canister_for_packs filling pending pack id {}".format(filling_pending_pack_ids))

        clauses = [PackAnalysis.batch_id == batch_id,
                   PackAnalysisDetails.device_id == device_id]

        if filling_pending_pack_ids:
            packs_to_skip.extend(filling_pending_pack_ids)
            clauses.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                            | (PackDetails.id << filling_pending_pack_ids)))
        else:
            clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS])

        # query to get ordered pack' device wise
        if pack_count:
            pack_list_to_skip_query = PackAnalysis.select(PackDetails.order_no, PackAnalysis.pack_id).dicts() \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(*clauses) \
                .group_by(PackDetails.id) \
                .order_by(PackDetails.order_no)

            for record in pack_list_to_skip_query:
                logger.info("packs to consider db_skip_canister_for_packs {}".format(record))
                if len(packs_to_skip) < int(pack_count):
                    if record['pack_id'] not in packs_to_skip:
                        packs_to_skip.append(record['pack_id'])
                else:
                    break

        logger.info("In db_skip_canister_for_packs packs to skip {}".format(packs_to_skip))
        if packs_to_skip:
            clauses.append(PackDetails.id << packs_to_skip)

        pack_analysis_list = PackAnalysis.select(PackAnalysis.id, PackAnalysis.pack_id, PackAnalysisDetails.canister_id,
                                                 PackAnalysisDetails.device_id,
                                                 PackAnalysisDetails.quadrant,
                                                 PackAnalysisDetails.location_number).dicts() \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(*clauses, PackAnalysisDetails.canister_id << canister_list,
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)

        for record in pack_analysis_list:
            affected_packs.add(record['pack_id'])
            pack_analysis_id_set.add(record['id'])
            canister_location_dict[record["canister_id"]] = {'device_id': record["device_id"],
                                                             'quadrant': record["quadrant"],
                                                             'location_number': record["location_number"]}

            if record['pack_id'] not in pack_analysis_id_dict.keys():
                pack_analysis_id_dict[record['pack_id']] = set()
                pack_canister_dict[record['pack_id']] = set()
            pack_analysis_id_dict[record['pack_id']].add(record['id'])
            pack_canister_dict[record['pack_id']].add(record["canister_id"])

        logger.info("In db_skip_canister_for_packs: pack_analysis_ids: {}, affected_packs: {}, pack_analysis_id_dict: {}"
                    .format(pack_analysis_id_set, affected_packs, pack_analysis_id_dict))

        if not affected_packs:
            logger.info('In db_skip_canister_for_packs No_packs_found_while_skipping_for_batch_for_canister: ' + str(canister_list))
            return True, None

        robot_analysis_ids: set = set()
        robot_pack_canister_dict = dict()
        non_robot_analysis_ids: set = set()
        non_robot_pack_canister_dict = dict()
        robot_packs: set = set()
        if len(affected_packs):
            remaining_analysis_ids = PackAnalysis.select(fn.GROUP_CONCAT(
                                                             PackAnalysis.id).coerce(
                                                             False).alias('analysis_id'),
                                                         PackAnalysis.pack_id,
                                                         fn.GROUP_CONCAT(
                                                             PackAnalysisDetails.location_number).coerce(
                                                             False).alias('location_number'),
                                                         fn.GROUP_CONCAT(PackAnalysisDetails.canister_id).coerce(
                                                             False).alias('canister_id'),
                                                         fn.GROUP_CONCAT(fn.DISTINCT(fn.CONCAT(PackAnalysisDetails.canister_id, "-", PackAnalysisDetails.device_id, "-", PackAnalysisDetails.quadrant, "-", PackAnalysisDetails.location_number))).alias('can_destination')) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(*clauses, PackAnalysis.pack_id << list(affected_packs),
                       PackAnalysisDetails.canister_id.not_in(canister_list),
                       PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED) \
                .group_by(PackAnalysis.pack_id)

            for record in remaining_analysis_ids.dicts():
                if record['canister_id'] and record['location_number']:
                    canister_id = list(record['canister_id'].split(","))
                    location_number = list(record['location_number'].split(","))
                    analysis_ids = list(record['analysis_id'].split(","))
                    can_destination_list = list(record["can_destination"].split(","))
                    d = {}
                    d = {i.split("-", 1)[0]: {"device_id": i.split("-")[1], "quadrant": i.split("-")[2],
                                              "location_number": i.split("-")[3]} for i in can_destination_list}
                    canister_location_dict.update(d)

                    if not any(canister_id) is False and not any(location_number) is False:
                        robot_packs.add(record['pack_id'])
                        if record['pack_id'] in filling_pending_pack_ids:
                            non_robot_analysis_ids.update(analysis_ids)
                            if not non_robot_pack_canister_dict.get(record['pack_id']):
                                non_robot_pack_canister_dict[record["pack_id"]] = set()
                            non_robot_pack_canister_dict[record["pack_id"]].update(canister_id)
                        else:
                            robot_analysis_ids.update(analysis_ids)
                            if not robot_pack_canister_dict.get(record['pack_id']):
                                robot_pack_canister_dict[record["pack_id"]] = set()
                            robot_pack_canister_dict[record["pack_id"]].update(canister_id)


        manual_pack_list = list(affected_packs - robot_packs)
        logger.info("In db_skip_canister_for_packs: manual pack list {}, robot_packs: {},non_robot_analysis_ids: {}, robot_analysis_ids: {}".
                    format(manual_pack_list, robot_packs, non_robot_analysis_ids, robot_analysis_ids))

        if len(manual_pack_list):
            for current_in_progress_pack in filling_pending_pack_ids:
                if current_in_progress_pack in manual_pack_list:
                    if current_in_progress_pack in pack_analysis_id_dict.keys():
                        logger.info("db_skip_canister_for_packs current progress pack {}".format(current_in_progress_pack))
                        non_robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        if not non_robot_pack_canister_dict.get(current_in_progress_pack):
                            non_robot_pack_canister_dict[current_in_progress_pack] = set()
                        non_robot_pack_canister_dict[current_in_progress_pack].update(pack_canister_dict[current_in_progress_pack])
                    else:
                        robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        if not robot_pack_canister_dict.get(current_in_progress_pack):
                            robot_pack_canister_dict[current_in_progress_pack] = set()
                        robot_pack_canister_dict[current_in_progress_pack].update(pack_canister_dict[current_in_progress_pack])
                    manual_pack_list.remove(current_in_progress_pack)


            logger.info("In db_skip_canister_for_packs: for manual_pack_list: manual pack list {}, robot_packs: {},non_robot_analysis_ids: {}, robot_analysis_ids: {}".
                format(manual_pack_list, robot_packs, non_robot_analysis_ids, robot_analysis_ids))

            if manual_pack_list:
                mfd_pack_list = get_mfd_packs_from_given_pack_list(batch_id=batch_id,
                                                                   pack_list=manual_pack_list)
                logger.info("In db_skip_canister_for_packs mfd pack list {}".format(mfd_pack_list))

                if len(mfd_pack_list):
                    for pack in mfd_pack_list:
                        non_robot_analysis_ids.update(pack_analysis_id_dict[pack])
                        if not non_robot_pack_canister_dict.get(pack):
                            non_robot_pack_canister_dict[pack] = set()
                        non_robot_pack_canister_dict[pack].update(pack_canister_dict[pack])
                    manual_pack_list = list(set(manual_pack_list) - set(mfd_pack_list))
                logger.info("In db_skip_canister_for_packs manual_pack_list {}".format(manual_pack_list))

                if len(manual_pack_list):
                    return False, manual_pack_list

        insert_list = []
        if non_robot_analysis_ids or robot_analysis_ids:
            analysis_ids = list(non_robot_analysis_ids) + list(robot_analysis_ids)
            insert_list = get_insert_list_of_replenish_skipped_canister(analysis_ids, canister_list)
            logger.info(f"In db_skip_canister_for_packs, insert_list: {insert_list}")

        with db.transaction():
            if len(non_robot_analysis_ids):
                logger.info("In db_skip_canister_for_packs non_robot_analysis_ids {}".format(non_robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None
                #                }
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in non_robot_pack_canister_dict.items() for can in canisters]
                # logger.info(f"In db_skip_canister_for_packs non_robot_analysis_ids insert_list: {insert_list}")
                # insert_status = ReplenishSkippedCanister.insert_many(insert_list).execute()

                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}
                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(non_robot_analysis_ids))
                logger.info("In db_skip_canister_for_packs: pack_analysis_status: {} for non_robot_analysis_ids: {}".format(
                    status, non_robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(non_robot_analysis_ids)

            if len(robot_analysis_ids):
                logger.info("In db_skip_canister_for_packs robot_analysis_ids {}".format(robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'canister_id': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None
                #                }
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in robot_pack_canister_dict.items() for can in canisters]
                # logger.info(f"In db_skip_canister_for_packs robot_analysis_ids insert_list: {insert_list}")
                #
                # insert_status = ReplenishSkippedCanister.insert_many(insert_list).execute()

                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}
                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(robot_analysis_ids))
                logger.info("In db_skip_canister_for_packs: pack_analysis_status: {} for robot_analysis_ids: {}".format(
                    status, robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(robot_analysis_ids)

            if insert_list:
                status = ReplenishSkippedCanister.insert_many(insert_list).execute()
                logger.info(f"In db_skip_canister_for_packs, insert status: {status}")

            if delete_reserved_canister_analysis_id:
                status = delete_reserved_canister_for_skipped_canister(canister_list, delete_reserved_canister_analysis_id)
                logger.info("In db_skip_canister_for_packs: reserved canister: {} deleted:{}".format(canister_list, status))

            BatchChangeTracker.db_save(batch_id=batch_id,
                                       user_id=user_id,
                                       action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.SKIP_FOR_PACKS],
                                       params={"canister_list": canister_list,
                                           "batch_id": batch_id,
                                           "pack_count": pack_count,
                                           "device_id": device_id,
                                           "user_id": user_id,
                                           "packs_to_skip": packs_to_skip},
                                       packs_affected=list(affected_packs)
                                       )
            return True, list(affected_packs)

    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_skip_canister_for_packs: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in db_skip_canister_for_packs: {}".format(e))
        raise e


@log_args
def get_drug_info_dao(company_id, drug_id):
    """
           @param company_id:
           @param drug_id:
           @return:  function to get drug information
    """
    try:

        drug = DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                 DrugMaster.drug_name,
                                 DrugMaster.strength,
                                 DrugMaster.strength_value,
                                 DrugMaster.imprint,
                                 DrugMaster.formatted_ndc,
                                 DrugMaster.txr,
                                 DrugMaster.manufacturer,
                                 DrugMaster.image_name,
                                 DrugMaster.color, DrugMaster.shape,
                                 DrugMaster.ndc,
                                 DosageType.id.alias('dosage_type_id'),
                                 DosageType.name.alias('dosage_type_name'),
                                 DosageType.code.alias('dosage_type_code'),
                                 fn.GROUP_CONCAT(
                                     DeviceMaster.name, '-', LocationMaster.display_location
                                 ).coerce(False).alias('canister_list'),
                                 fn.SUM(CanisterMaster.available_quantity).alias('available_quantity'),
                                 fn.IF((fn.SUM(CanisterMaster.available_quantity)) < 0, 0,
                                       fn.SUM(CanisterMaster.available_quantity)).alias(
                                     'display_quantity'),
                                 LocationMaster.location_number,
                                 LocationMaster.is_disabled.alias('is_location_disabled'),
                                 ContainerMaster.drawer_name.alias('drawer_number'),
                                 LocationMaster.display_location,
                                 DeviceLayoutDetails.id.alias('device_layout_id'),
                                 DeviceMaster.name.alias('device_name'),
                                 DeviceMaster.id.alias('device_id'),
                                 DeviceTypeMaster.device_type_name,
                                 DeviceTypeMaster.id.alias('device_type_id'),
                                 ContainerMaster.ip_address,
                                 ContainerMaster.secondary_ip_address,
                                 fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).alias('canister_ids'),
                                 # fn.GROUP_CONCAT(Clause(fn.CONCAT(fn.IF(DeviceMaster.name.is_null(True), 'On Shelf', DeviceMaster.name),
                                 fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                       DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                 fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                                     'stock_updated_by')).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=(
                (CanisterMaster.drug_id == DrugMaster.id) &
                (CanisterMaster.company_id == company_id) &
                CanisterMaster.rfid.is_null(False))) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == CanisterMaster.canister_type) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                                  & (DrugMaster.txr == UniqueDrug.txr)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                      (DrugStockHistory.is_active == True) &
                                                      (DrugStockHistory.company_id == company_id))) \
            .join(StoreSeparateDrug, JOIN_LEFT_OUTER, on=UniqueDrug.id == StoreSeparateDrug.unique_drug_id) \
            .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .where(DrugMaster.id == drug_id) \
            .group_by(DrugMaster.id) \
            .order_by(SQL('canister_list').desc()) \
            .get()
        return drug

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_info_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_drug_info_dao {}".format(e))
        raise e


def get_alternate_drug_data_dao(company_id: int, device_type_id: int, device_id: int, drug_id: int, paginate: [dict, None], sort_fields=None) -> tuple:
    """
        function to get alternate drug data
    @param sort_fields:
    @param company_id:
    @param device_id:
    @param device_type_id:
    @param drug_id:
    @param paginate:
    @return:
    """
    DrugAlias = DrugMaster.alias()
    alternate_drugs: list = list()
    try:
        fields_dict = {"drug_name": DrugAlias.drug_name,
                       "ndc": DrugAlias.ndc,
                       "canister_id": CanisterMaster.id,
                       'drawer_initial': cast(fn.Substr(ContainerMaster.drawer_name, 1, fn.instr(ContainerMaster.drawer_name, '-') - 1),
                           'CHAR'),
                       'device_type': DeviceMaster.device_type_id,
                       'display_location': fn.IF(LocationMaster.display_location.is_null(False),
                                                 LocationMaster.display_location,
                                                 None),
                       'drawer_number': cast(fn.Substr(ContainerMaster.drawer_name, fn.instr(ContainerMaster.drawer_name, '-') + 1),
                           'SIGNED'),
                       'device_name': DeviceMaster.name,
                       'qty': CanisterMaster.available_quantity,
                       'zone_id': fn.IF(ZoneMaster.id.is_null(True), None, ZoneMaster.id),
                       'zone_name': fn.IF(ZoneMaster.name.is_null(True), None, ZoneMaster.name),
                       }
        order_list: list = list()
        order_list = get_orders(order_list, fields_dict, sort_fields)
        order_list.extend([DeviceTypeMaster.id.desc(), DeviceMaster.id.desc(), DrugMaster.id])

        query = DrugAlias.select(DrugAlias.id.alias('drug_id'),
                                 DrugAlias.drug_name,
                                 DrugAlias.strength,
                                 DrugMaster.strength_value,
                                 DrugAlias.imprint,
                                 DrugAlias.formatted_ndc,
                                 DrugAlias.txr,
                                 DrugAlias.manufacturer,
                                 DrugAlias.image_name,
                                 DrugAlias.color,
                                 DrugAlias.shape,
                                 DrugAlias.ndc,
                                 DrugAlias.brand_flag,
                                 DrugAlias.brand_flag.alias('alt_brand_flag'),
                                 DrugStatus.ext_status,
                                 DrugStatus.ext_status_updated_date,
                                 DrugStatus.last_billed_date,
                                 DosageType.id.alias('dosage_type_id'),
                                 DosageType.name.alias('dosage_type_name'),
                                 DosageType.code.alias('dosage_type_code'),
                                 fn.SUM(CanisterMaster.available_quantity).alias('available_quantity'),
                                 fn.IF((fn.SUM(CanisterMaster.available_quantity)) < 0, 0,
                                       fn.SUM(CanisterMaster.available_quantity)).alias(
                                     'display_quantity'),
                                 LocationMaster.location_number,
                                 LocationMaster.is_disabled.alias('is_location_disabled'),
                                 ContainerMaster.drawer_name.alias('drawer_number'),
                                 LocationMaster.display_location,
                                 DeviceLayoutDetails.id.alias('device_layout_id'),
                                 DeviceMaster.name.alias('device_name'),
                                 DeviceMaster.id.alias('device_id'),
                                 DeviceTypeMaster.device_type_name,
                                 DeviceTypeMaster.id.alias('device_type_id'),
                                 ContainerMaster.ip_address,
                                 ContainerMaster.secondary_ip_address,
                                 fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).alias('canister_ids'),
                                 fn.COUNT(fn.DISTINCT(CanisterMaster.id)).alias('canister_count'),
                                 fn.GROUP_CONCAT(Clause(fn.CONCAT(DeviceMaster.name,
                                                                  '- Drawer ',
                                                                  ContainerMaster.drawer_name,
                                                                  '(',
                                                                  LocationMaster.get_device_location(),
                                                                  ')'
                                                                  ),
                                                        SQL(" SEPARATOR ', ' "))).coerce(False).alias('canister_list'),
                                 fn.IF(DrugStockHistory.is_in_stock.is_null(True), None,
                                       DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                 fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                       DrugStockHistory.created_by).alias(
                                     'stock_updated_by')).dicts() \
                    .join(DrugMaster, on=((DrugMaster.txr == DrugAlias.txr) &
                                          (DrugMaster.formatted_ndc != DrugAlias.formatted_ndc))) \
                    .join(DrugStatus, on=DrugStatus.drug_id == DrugAlias.id) \
                    .join(CanisterMaster, JOIN_LEFT_OUTER,
                          on=((CanisterMaster.drug_id == DrugAlias.id) &
                              (CanisterMaster.company_id == company_id) &
                              (CanisterMaster.rfid.is_null(False)))) \
                    .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == CanisterMaster.canister_type) \
                    .join(UniqueDrug, JOIN_LEFT_OUTER, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                                           & (DrugMaster.txr == UniqueDrug.txr))) \
                    .join(StoreSeparateDrug, JOIN_LEFT_OUTER, on=UniqueDrug.id == StoreSeparateDrug.unique_drug_id) \
                    .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                    .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                    .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                    .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                    .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
                    .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                              (DrugStockHistory.is_active == True) &
                                                              (DrugStockHistory.company_id == company_id))) \
                    .where(DrugMaster.id == drug_id) \
                    .group_by(DrugAlias.id) \
                    .order_by(SQL('canister_ids').desc(), *order_list)

        count = query.count()
        if paginate:
            query = apply_paginate(query, paginate)
        for record in query:
            record['available_quantity'] = float(record['available_quantity'] if record['available_quantity'] else 0)
            record['canister_list_with_qty'] = fetch_canister_drug_data_from_canister_ids(canister_ids=record['canister_ids'],
                                                                                          device_id=device_id,
                                                                                          device_type_id=device_type_id)
            alternate_drugs.append(record)

        return alternate_drugs, count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_alternate_drug_data_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_drug_data_dao {}".format(e))
        raise e


@log_args_and_response
def save_alternate_drug_option(pack_data):
    """
    - Business logic
        automatically saves alternate drug in AlternateDrugOption
        In case user has changed the choices i.e. deselected alternate drug than those are preserved
    - Data format
        {
            'pack_ids': pack_ids,
            'company_id': company_id
            'save_alternate_drug_option': True
        }
    @param pack_data:
    @return:
    """
    try:
        facility_distribution_id = pack_data['facility_distribution_id']
        #remove entry from batch drug & order and alternate drugs'
        remove_bypassed_ordering(facility_distribution_id)
        pack_ids = PackDetails.get_packs_by_facility_distribution_id(facility_distribution_id=facility_distribution_id,
                                                                     company_id=pack_data['company_id'])
        logger.info("In save_alternate_drug_option: pack ids: {}".format(pack_ids))

        pack_data['pack_ids'] = pack_ids
        if not pack_ids:
            return error(1020)

        saved_alternate_drug = get_alternate_drug_dao(facility_distribution_id=facility_distribution_id, type='dict')
        alternate_drug_dict = get_alternate_drug_list(pack_list_info=pack_data)
        logger.info("In save_alternate_drug_option: alternate_drug_dict: {}".format(alternate_drug_dict))

        if not alternate_drug_dict:
            status = AlternateDrugOption.remove_alternate_drug_distribution_id({'facility_distribution_id': facility_distribution_id,
                                                                                'user_id': pack_data['user_id']})
            logger.info("In save_alternate_drug_option: AlternateDrugOption remove status: {}".format(status))
            return create_response(True)

        if not saved_alternate_drug:
            alternate_drug_option_list: list = list()
            for original_drug, alternate_drug_list in alternate_drug_dict.items():
                for alternate_drug in alternate_drug_list:
                    alternate_drug_option_data = {'created_by': pack_data['user_id'],
                                                  'modified_by': pack_data['user_id'],
                                                  'active': alternate_drug[1],
                                                  'created_date': get_current_date(),
                                                  'modified_date': get_current_date(),
                                                  'facility_dis_id': facility_distribution_id,
                                                  'unique_drug_id': original_drug,
                                                  'alternate_unique_drug_id': alternate_drug[0]
                                                  }
                    alternate_drug_option_list.append(alternate_drug_option_data)

            # add data in alternate drug option table
            status = AlternateDrugOption.add_alternate_drug(alternate_drug_option_list)
            logger.info("In save_alternate_drug_option: if not saved_alternate_drug: AlternateDrugOption data added status: {}".format(status))

        else:
            alternate_drug_option_list: list = list()
            alternate_drugs: list = list()
            for original_drug, alternate_drug_list in alternate_drug_dict.items():
                if original_drug not in saved_alternate_drug.keys():
                    for alternate_drug in alternate_drug_list:
                        alternate_drug_option_data = {'created_by': pack_data['user_id'],
                                                      'modified_by': pack_data['user_id'],
                                                      'active': alternate_drug[1],
                                                      'modified_date': get_current_date(),
                                                      'facility_dis_id': facility_distribution_id,
                                                      'unique_drug_id': original_drug,
                                                      'alternate_unique_drug_id': alternate_drug[0]
                                                      }
                        alternate_drug_option_list.append(alternate_drug_option_data)
                alternate_drugs.append(original_drug)
            if alternate_drug_option_list:
                status = AlternateDrugOption.add_alternate_drug(alternate_drug_option_list)
                logger.info("In save_alternate_drug_option: if alternate_drug_option_list: AlternateDrugOption data added status: {}".format(status))
            # removed as same facility removed and added scenario keeps drug deselected.
            # if alternate_drugs:
            #     AlternateDrugOption.remove_redundant_alternate_drug_distribution_id({
            #         'facility_distribution_id': facility_distribution_id,
            #         'unique_drug_ids': alternate_drugs,
            #         'user_id': pack_data['user_id']})

        return create_response(True)

    except DoesNotExist as e:
        logger.error("Error in save_alternate_drug_option {}".format(e))
        raise e
    except (IntegrityError, InternalError) as e:
        logger.error("Error in save_alternate_drug_option {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in save_alternate_drug_option {}".format(e))
        raise e


@log_args_and_response
def get_alternate_drug_dao(facility_distribution_id: int, type='list') -> list or dict:
    """
    get alternate drug option data
    @param facility_distribution_id:
    @param type:
    @return:

    """
    try:
        data = AlternateDrugOption.select().dicts() \
            .join(UniqueDrug, on=UniqueDrug.id == AlternateDrugOption.unique_drug_id) \
            .where(AlternateDrugOption.facility_dis_id == facility_distribution_id)

        if type == 'dict':
            alternate_drug_dict = defaultdict(list)
            for record in data:
                alternate_drug_dict[record['unique_drug_id']].append(record['alternate_unique_drug_id'])
            return alternate_drug_dict
        else:
            return list(data)

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_alternate_drug_dao {}".format(e))
        raise e


@log_args
def get_alternate_drug_list(pack_list_info):
    """ Gets alternate drug list for given pack ids.
    Args:
        pack_list_info (dict): The dict containing pack list and system id as key.

    Returns:
        {}

    Examples:
        >>> get_alternate_drug_list()
        None
        @param pack_list_info:
        @return:
    """
    # get the value pack_list form the input dict
    pack_list = pack_list_info["pack_ids"]
    try:
        logger.info("In get_alternate_drug_list: pack_list: {}".format(pack_list))
        facility_distribution_id = list(PackDetails.db_get_facility_distribution_ids(pack_list=[pack_list[0]]))[0]
        logger.info("In get_alternate_drug_list: facility_distribution_id: {}".format(facility_distribution_id))

    except DoesNotExist as e:
        logger.error("Error in get_alternate_drug_list {}".format(e))
        return error(1020, 'Unable to find facility_dist_id.')
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_alternate_drug_list {}".format(e))
        return error(2001)

    company_id = pack_list_info["company_id"]
    alternate_drug_option = pack_list_info.get('save_alternate_drug_option', False)


    analysis_data: list = list()
    canister_data: dict = dict()
    drug_data: dict = dict()
    formatted_ndc_canister_data: set = set()
    selected_alternate_drug_dict = defaultdict(set)
    pack_txr: set = set()

    UniqueDrugAlias = UniqueDrug.alias()

    if not pack_list:
        return create_response(analysis_data)
    try:
        # is_imported = BatchMaster.db_is_imported(batch_id)
        # if is_imported is None or is_imported:
        #     return error(1020)
        # reserved canister query
        reserved_canister = ReservedCanister.select(ReservedCanister.canister_id) \
            .join(BatchMaster, on=BatchMaster.id == ReservedCanister.batch_id) \
            .join(CanisterMaster, on=CanisterMaster.id == ReservedCanister.canister_id) \
            .where(CanisterMaster.company_id == company_id)

        # alternate option query
        query = AlternateDrugOption.select(UniqueDrug.formatted_ndc.alias('alternate_fndc'),
                                           UniqueDrug.txr.alias('alternate_txr'),
                                           UniqueDrugAlias.formatted_ndc.alias('original_fndc'),
                                           UniqueDrugAlias.txr.alias('original_txr')) \
            .join(UniqueDrug, on=UniqueDrug.id == AlternateDrugOption.alternate_unique_drug_id) \
            .join(UniqueDrugAlias, on=UniqueDrugAlias.id == AlternateDrugOption.unique_drug_id) \
            .where(AlternateDrugOption.facility_dis_id == facility_distribution_id,
                   AlternateDrugOption.active == True)
        print(query)

        for record in query.dicts():
            selected_alternate_drug_dict[(record['original_fndc'], record['original_txr'])] \
                .add((record['alternate_fndc'], record['alternate_txr']))

        logger.info("In get_alternate_drug_list: selected_alternate_drug_dict: {}".format(selected_alternate_drug_dict))

        # drug_based_ext_status_query
        ext_status_alt_query = DrugMaster.select(DrugMaster.formatted_ndc.alias('formatted_ndc'),
                                                 DrugMaster.txr.alias('txr'),
                                                 fn.MAX(DrugStatus.ext_status).alias('ext_status'),
                                                 fn.MAX(DrugStatus.last_billed_date).alias('last_billed_date')).dicts() \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr).alias('ext_status_alt_query')

        query = SlotDetails.select(ext_status_alt_query.c.ext_status.alias('ext_status'),
                                   ext_status_alt_query.c.last_billed_date.alias('last_billed_date'),
                                   fn.sum(fn.floor(SlotDetails.quantity)).alias("required_quantity"),
                                   DrugMaster.txr,
                                   DrugMaster.formatted_ndc,
                                   DrugMaster.manufacturer,
                                   DrugMaster.ndc,
                                   PackDetails.facility_dis_id,
                                   DrugMaster.drug_name,
                                   DrugMaster.strength,
                                   DrugMaster.strength_value,
                                   DrugMaster.id.alias('drug_id'),
                                   DrugMaster.brand_flag,
                                   DrugMaster.image_name,
                                   DrugMaster.shape,
                                   DrugMaster.imprint,
                                   fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                         DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                   fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                         DrugDetails.last_seen_by, ).alias('last_seen_with'),
                                   fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                         DrugDetails.last_seen_date).alias('last_seen_on'),
                                   UniqueDrug.id.alias('unique_drug_id'),
                                   PatientRx.daw_code,
                                   fn.IF(DrugMaster.brand_flag == settings.GENERIC_FLAG, 1, 0).alias('alt_selection'),
                                   ) \
                .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
                .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                      (UniqueDrug.txr == DrugMaster.txr))) \
                .join(ext_status_alt_query, on=((ext_status_alt_query.c.formatted_ndc == DrugMaster.formatted_ndc) &
                                                (ext_status_alt_query.c.txr == DrugMaster.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == 1) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == company_id))) \
                .where(PackDetails.id << pack_list,
                       PackDetails.company_id == company_id) \
                .group_by(DrugMaster.formatted_ndc, DrugMaster.txr, PatientRx.daw_code) \
                .having(fn.sum(fn.floor(SlotDetails.quantity)) > 0)


        for record in query.dicts():
            # we are considering only non-fractional drug quantity
            # that is why we are doing floor of slot_details.quantity
            if record['txr']:
                pack_txr.add(record['txr'])

            fndc_txr = record["formatted_ndc"], record['txr']
            record["required_quantity"] = float(record["required_quantity"])
            record["ext_status"] = bool(record["ext_status"])
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]

            if fndc_txr not in drug_data:
                record["daw_list"] = {}
                record["daw_list"][record["daw_code"]] = record["required_quantity"]
                # del record["daw_code"] # remove this key from record
                drug_data[fndc_txr] = record

            else:
                # updating daw wise quantity
                previous_drug_data = drug_data[fndc_txr]
                previous_drug_data["daw_list"][record["daw_code"]] = record["required_quantity"]
                # updating total quantity
                previous_drug_data["required_quantity"] += record["required_quantity"]
                drug_data[fndc_txr] = previous_drug_data

        logger.info("In get_alternate_drug_list: drug_data: {}".format(drug_data))

        if not pack_txr:
            logger.info('In get_alternate_drug_list: pack_txr: {}'.format(pack_txr))
            return []

        query = CanisterMaster.select(ext_status_alt_query.c.ext_status.alias('ext_status'),
                                      ext_status_alt_query.c.last_billed_date.alias('last_billed_date'),
                                      CanisterMaster.id.alias('canister_id'),
                                      LocationMaster.device_id,
                                      CanisterMaster.rfid,
                                      fn.SUM(CanisterMaster.available_quantity).alias('available_quantity'),
                                      fn.IF(CanisterMaster.available_quantity < 0, 0,
                                            CanisterMaster.available_quantity).alias('display_quantity'),
                                      LocationMaster.location_number,
                                      LocationMaster.is_disabled.alias('is_location_disabled'),
                                      CanisterMaster.drug_id,
                                      DrugMaster.drug_name,
                                      DrugMaster.image_name,
                                      DrugMaster.strength,
                                      DrugMaster.strength_value,
                                      DrugMaster.ndc,
                                      DrugMaster.txr,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.manufacturer,
                                      DrugMaster.shape,
                                      DrugMaster.imprint,
                                      fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                            DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                      fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                            DrugDetails.last_seen_by, ).alias('last_seen_with'),
                                      CanisterMaster.reorder_quantity,
                                      CanisterMaster.barcode,
                                      DeviceMaster.name.alias('device_name'),
                                      LocationMaster.location_number,
                                      UniqueDrug.id.alias('unique_drug_id'),
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      LocationMaster.display_location,
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True),
                                                                               'null', ZoneMaster.id)),
                                                             SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                          'zone_id'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True),
                                                                               'null', ZoneMaster.name)),
                                                             SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                          'zone_name'),
                                      DeviceLayoutDetails.id.alias('device_layout_id'),
                                      DeviceMaster.name.alias('device_name'),
                                      DeviceMaster.id.alias('device_id'),
                                      DeviceTypeMaster.device_type_name,
                                      DeviceTypeMaster.id.alias('device_type_id'),
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      DeviceMaster.system_id,
                                      LocationMaster.get_device_location().alias('device_location'),
                                      DrugMaster.brand_flag,
                                      fn.IF(DrugMaster.brand_flag == settings.GENERIC_FLAG, 1, 0).alias(
                                          'alt_selection'),
                                      ).dicts() \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(ext_status_alt_query, on=((ext_status_alt_query.c.formatted_ndc == DrugMaster.formatted_ndc) &
                                            (ext_status_alt_query.c.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .where(CanisterMaster.company_id == company_id,
                   CanisterMaster.active == settings.is_canister_active,
                   CanisterMaster.id.not_in(reserved_canister),
                   ((DrugMaster.txr << list(pack_txr)) | (DrugMaster.txr.is_null(True)))) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)

        logger.info('In get_alternate_drug_list: pack_txr: {}'.format(pack_txr))

        for record in query:
            # we are checking for duplicated formatted ndc available and increasing the quantity only
            # by summing up
            # if record["location_number"] > 0: # placing into query
            fndc_txr = record["formatted_ndc"], record['txr']

            if fndc_txr not in formatted_ndc_canister_data:
                record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
                record["available_quantity"] = float(record["available_quantity"])
                record["ext_status"] = bool(record["ext_status"])
                record['selected_alternate'] = True if fndc_txr in selected_alternate_drug_dict[fndc_txr] else False \
                    if fndc_txr in selected_alternate_drug_dict else False
                canister_data[fndc_txr] = record
                formatted_ndc_canister_data.add(fndc_txr)
            else:
                prev_record = canister_data[fndc_txr]
                prev_record["available_quantity"] += record["available_quantity"]
                canister_data[fndc_txr] = prev_record

        logger.info("In get_alternate_drug_list: formatted_ndc_canister_data: {}".format(formatted_ndc_canister_data))

        # In drug_data we get all the drugs which are required to fill the pack.
        # Now create a list of filtered drugs.
        alt_drug_data: dict = dict()
        alt_generic_fndc_txr_set = defaultdict(set)

        query = DrugMaster.select(DrugMaster,
                                  DrugStatus.ext_status,
                                  DrugStatus.last_billed_date).dicts() \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .where(((DrugMaster.txr << list(pack_txr)) | (DrugMaster.txr.is_null(True))))

        for record in query:
            # if the drug is generic then add it in alt_generic_fndc_txr_set. If there are generic drugs available then
            # only we will show list of alternate but according to new alt-drug list format we show all the drug
            # having same txr with disable selection for non-generic drug
            if record['brand_flag'] == settings.GENERIC_FLAG:
                alt_generic_fndc_txr_set[record['txr']].add(record['formatted_ndc'])
            if record['txr'] not in alt_drug_data:
                alt_drug_data[record['txr']] = dict()
            if record['formatted_ndc'] not in alt_drug_data[record['txr']]:
                alt_drug_data[record['txr']][record['formatted_ndc']] = {'formatted_ndc': record['formatted_ndc'],
                                                                         'txr': record['txr'],
                                                                         'brand_flag': record['brand_flag'],
                                                                         'manufacturer': record['manufacturer'],
                                                                         'id': record['id'],
                                                                         'ext_status': bool(record['ext_status']),
                                                                         'last_billed_date': record['last_billed_date'],
                                                                         }
        count: int = 0
        for record in drug_data.values():
            count += 1
            drug_id = record["drug_id"]
            fndc_txr = record["formatted_ndc"], record['txr']
            if fndc_txr not in formatted_ndc_canister_data:
                # check for DAW and if equals to zero -- go for alternate drug
                if 0 in record["daw_list"].keys() and record["brand_flag"] == settings.GENERIC_FLAG:
                    alternate_drug_list = get_alternate_drug(formatted_ndc=record["formatted_ndc"],
                                                             txr_no=record["txr"],
                                                             canister_data=canister_data,
                                                             alt_drug_data=alt_drug_data,
                                                             alt_generic_fndc_txr_set=alt_generic_fndc_txr_set,
                                                             selected_alternate_drug_list=selected_alternate_drug_dict[
                                                                 fndc_txr] if fndc_txr in selected_alternate_drug_dict else [],
                                                             )
                    # change the above get_alternate_drug function by below commented code when you need out_of_stock_key in alternate_drug_list
                    # alternate_drug_list = get_alternate_drug(
                    #     record["formatted_ndc"], record["txr"],
                    #     canister_data,
                    #     record["brand_flag"], required_quantity=record["required_quantity"],
                    # )
                    logger.info("In get_alternate_drug_list: alternate_drug_list: {}".format(alternate_drug_list))
                    if alternate_drug_list:
                        alternate_drug_list.append(get_data_dict(record))
                        record["available_quantity"] = 0
                        record["is_canister_available"] = False
                        record["location_number"] = 0
                        record["alternate_drug_list"] = sorted(alternate_drug_list,
                                                               key=lambda i: (i['ext_status'],
                                                                              i['alt_selection'],
                                                                              i['sort_last_billed_date'],
                                                                              i['available_quantity']),
                                                               reverse=True)
                        # adding dawmax field
                        record["dawmax"] = max(record["daw_list"].keys())
                        analysis_data.append(record)
            else:
                _data = canister_data[fndc_txr]
                record.update(_data)
                record["drug_id"] = drug_id
                daw_list = record["daw_list"].keys()
                missing_quantity = record["required_quantity"] - record["available_quantity"]

                if 0 in daw_list:
                    if (missing_quantity > 0 or record['ext_status'] != settings.VALID_EXT_STATUS or fndc_txr in
                        selected_alternate_drug_dict) and \
                            record["brand_flag"] == settings.GENERIC_FLAG:
                        record["dawmax"] = max(daw_list)  # adding dawmax field
                        record['ext_status'] = bool(record['ext_status'])
                        record["is_canister_available"] = True

                        alternate_drug_list = get_alternate_drug(formatted_ndc=record["formatted_ndc"],
                                                                 txr_no=record["txr"],
                                                                 canister_data=canister_data,
                                                                 alt_drug_data=alt_drug_data,
                                                                 alt_generic_fndc_txr_set=alt_generic_fndc_txr_set,
                                                                 selected_alternate_drug_list=selected_alternate_drug_dict[
                                                                     fndc_txr] if fndc_txr in selected_alternate_drug_dict else []
                                                                 )
                        # change the above get_alternate_drug function by below commented code when you need out_of_stock_key in alternate_drug_list
                        # alternate_drug_list = get_alternate_drug(
                        #     record["formatted_ndc"], record["txr"],
                        #     canister_data,
                        #     record["brand_flag"], required_quantity=record["required_quantity"],
                        # )
                        if alternate_drug_list:
                            alternate_drug_list.append(get_data_dict(record))
                            record["alternate_drug_list"] = sorted(alternate_drug_list,
                                                                   key=lambda i: (i['ext_status'],
                                                                                  i['alt_selection'],
                                                                                  i['sort_last_billed_date'],
                                                                                  i['available_quantity']),
                                                                   reverse=True)
                            record["location_number"] = 0
                            # append the drug to analysis_data for daw values other than 0
                            analysis_data.append(record)

        logger.info("In get_alternate_drug_list: count: {}".format(count))

        alternate_drug_dict = defaultdict(list)
        analysis_data = sorted(analysis_data, key=lambda x: (x["ext_status"], x["location_number"]))

        if alternate_drug_option:
            for data in analysis_data:
                for alternate in data['alternate_drug_list']:
                    if alternate['ext_status'] == settings.VALID_EXT_STATUS and alternate['brand_flag'] == settings.GENERIC_FLAG:
                        if data['unique_drug_id'] == alternate['unique_drug_id']:
                            if data['is_canister_available']:
                                alternate_drug_dict[data['unique_drug_id']].append((alternate['unique_drug_id'], 1))
                            else:
                                alternate_drug_dict[data['unique_drug_id']].append((alternate['unique_drug_id'], 0))
                        else:
                            alternate_drug_dict[data['unique_drug_id']].append((alternate['unique_drug_id'], 1))
                    else:
                        alternate_drug_dict[data['unique_drug_id']].append((alternate['unique_drug_id'], 0))
            return alternate_drug_dict
        else:
            return create_response(analysis_data)

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_alternate_drug_list:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_alternate_drug_list {}".format(e))
        raise e


@log_args
def get_alternate_drug(formatted_ndc: str, txr_no: str, canister_data: dict, alt_drug_data: dict, alt_generic_fndc_txr_set: defaultdict,
                       missing_quantity: int = None, selected_alternate_drug_list: list = List) -> list:
    # change the above get_alternate_drug function signature by below commented line when you need
    # out_of_stock_key in alternate_drug_list
    # def get_alternate_drug(formatted_ndc, txr_no, canister_data, brand_flag,**kwargs):
    """ Get the alternate drug information for the given ndc and txr number

    Args:
        formatted_ndc (str): The formatted ndc of the drug
        txr_no (int): The txr number for the given ndc
        canister_data (dict): The list of canisters to get alternate drug canisters
        brand_flag (str): The brand flag for the ndc

    Returns:
        {}

    Examples:
        >>> get_alternate_drug()
        None
        @param formatted_ndc:
        @param txr_no:
        @param canister_data:
        @param alt_drug_data:
        @param alt_generic_fndc_txr_set:
        @param selected_alternate_drug_list:
        @return:
        @param missing_quantity:
    """
    alternate_drug_list: list = list()
    unique_ndc: set = set()
    # uncomment below commented lines when you need out_of_stock_key in alternate_drug_list
    # required_quantity=None
    # missing_quantity=None
    # for key, value in kwargs.items():
    #     if key=='required_quantity':
    #         required_quantity=value
    #     elif key=='missing_quantity':
    #         missing_quantity=value

    try:
        logger.info("In get_alternate_drug: txr_no: {},alt_generic_fndc_txr_set: {}".format(txr_no, alt_generic_fndc_txr_set))
        if not txr_no:
            return alternate_drug_list

        alt_drug_txr_data = alt_drug_data[txr_no]
        generic_fndc = alt_generic_fndc_txr_set[txr_no]
        if len(generic_fndc) <= 1:
            return alternate_drug_list

        for alt_fndc, record in alt_drug_txr_data.items():
            if formatted_ndc != alt_fndc:
                alternate_ndc = record['formatted_ndc'], record['txr']
                manufacturer = record["manufacturer"]
                # Get the brand flag for the alternate drug
                alternate_drug_brand_flag = record["brand_flag"]
                # Check if the brand flag for the required flag for the brand and alternate drug matches
                try:
                    canister_record = canister_data[alternate_ndc]
                except KeyError:
                    canister_record = {}

                if len(canister_record) > 0 and alternate_ndc not in unique_ndc:
                    canister_record["manufacturer"] = manufacturer
                    canister_record["brand_flag"] = alternate_drug_brand_flag
                    # BugFix Adding drug_id in alternate drug list
                    canister_record["drug_id"] = record["id"]
                    canister_record['sort_last_billed_date'] = record['last_billed_date'] if \
                        record['last_billed_date'] else settings.min_date

                    canister_record["selected_alternate"] = True if alternate_ndc in selected_alternate_drug_list else False
                    # uncomment below two commented lines when you need out_of_stock_key in alternate_drug_list
                    # if required_quantity is not None:
                    #     canister_record["out_of_stock"] =True if required_quantity > canister_record["available_quantity"] else False
                    if missing_quantity:
                        if canister_record["available_quantity"] > missing_quantity:
                            alternate_drug_list.append(canister_record)
                    else:
                        alternate_drug_list.append(canister_record)

                unique_ndc.add(alternate_ndc)
        return alternate_drug_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_alternate_drug {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_drug {}".format(e))
        raise e


def get_data_dict(data):
    data_dict = {
        "rfid": data.get("rfid", None),
        "zone_name": data.get("zone_name"),
        "location_number": data.get("location_number", None),
        "strength_value": data.get("strength_value", None),
        "device_location": data.get("device_location", None),
        "drug_name": data.get("drug_name", None),
        "device_name": data.get("device_name", None),
        "system_id": data.get("system_id", None),
        "available_quantity": data.get("available_quantity", 0),
        "strength": data.get("strength", None),
        "device_type_id": data.get("device_type_id", None),
        "reorder_quantity": data.get("reorder_quantity", None),
        "drug_id": data.get("drug_id", None),
        "display_location": data.get("display_location", None),
        "canister_id": data.get("canister_id", None),
        "brand_flag": data.get("brand_flag", None),
        "ip_address": data.get("ip_address", None),
        "drawer_number": data.get("drawer_number", None),
        "zone_id": data.get("zone_id", None),
        "drawers_initial_pattern": data.get("drawers_initial_pattern", None),
        "container_id": data.get("container_id", None),
        "device_layout_id": data.get("device_layout_id", None),
        "txr": data.get("txr", None),
        "ndc": data.get("ndc", None),
        "device_id": data.get("device_id", None),
        "manufacturer": data.get("manufacturer", None),
        "barcode": data.get("barcode", None),
        "display_quantity": data.get("display_quantity", None),
        "formatted_ndc": data.get("formatted_ndc", None),
        "device_type_name": data.get("device_type_name", None),
        "selected_alternate": data.get("selected_alternate", False),
        "unique_drug_id": data.get("unique_drug_id", None),
        "is_canister_available": data.get("is_canister_available", False),
        "is_source_drug": True,
        "ext_status": data["ext_status"],
        "last_billed_date": data["last_billed_date"],
        "sort_last_billed_date": data["last_billed_date"] if data["last_billed_date"] else settings.min_date,
        "alt_selection": data["alt_selection"],
    }
    return data_dict


def get_old_drug_new_drug_data(i: int, new_drug_ids: list, old_drug_ids: list):
    """
       Get the old drug data and new drug data
    """
    try:
        join_condition = ((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                          (DrugMaster.txr == UniqueDrug.txr))
        old_drug_record = DrugMaster.select(DrugMaster.formatted_ndc,
                                            DrugMaster.txr,
                                            DrugMaster.brand_flag,
                                            UniqueDrug.id.alias('unique_drug_id')).dicts() \
            .join(UniqueDrug, on=join_condition) \
            .where(DrugMaster.id == old_drug_ids[i]).get()
        new_drug_record = DrugMaster.select(DrugMaster.formatted_ndc,
                                            DrugMaster.txr,
                                            DrugMaster.brand_flag,
                                            DrugStatus.ext_status,
                                            UniqueDrug.id.alias('unique_drug_id')).dicts() \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=join_condition) \
            .where(DrugMaster.id == new_drug_ids[i]).get()
        return new_drug_record, old_drug_record

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_old_drug_new_drug_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_old_drug_new_drug_data {}".format(e))
        raise e


@log_args_and_response
def create_update_alternate_option_dao(create_dict: dict, update_dict: dict):
    """
       create or update record in alternate drug option table
    """
    try:
        return AlternateDrugOption.db_update_or_create(create_dict=create_dict, update_dict=update_dict)
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in create_update_alternate_option_dao:  {}".format(e))
        raise e


@log_args_and_response
def update_alternate_drug_option_dao(update_dict: dict, alt_drug_list: list) -> bool:
    """
    update alternate drug option table
    @param alt_drug_list:
    @param update_dict:
    """
    try:
        return AlternateDrugOption.db_update_alternate_drug_option(update_dict=update_dict, alt_drug_list=alt_drug_list)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_alternate_drug_option_dao:  {}".format(e))
        raise e


@log_args_and_response
def get_alternate_drug_option_dao(facility_dist_id: int) -> list:
    """
    get alternate drug option data
    @param facility_dist_id:
    """
    try:
        UniqueDrugAlias = UniqueDrug.alias()
        DrugMasterAlias = DrugMaster.alias()
        data = AlternateDrugOption.select(DrugMaster,
                                          AlternateDrugOption.id.alias('alternate_drug_option_id'),
                                          DrugMaster.id.alias('drug_id'),
                                          DrugMasterAlias.drug_name.alias('alternate_drug_name'),
                                          DrugMasterAlias.ndc.alias('alternate_ndc'),
                                          DrugMasterAlias.formatted_ndc.alias('alternate_formatted_ndc'),
                                          DrugMasterAlias.strength.alias('alternate_strength'),
                                          DrugMasterAlias.strength_value.alias('alternate_strength_value'),
                                          DrugMasterAlias.txr.alias('alternate_txr'),
                                          DrugMasterAlias.id.alias('alternate_drug_id')).dicts() \
            .join(UniqueDrug, on=AlternateDrugOption.unique_drug_id == UniqueDrug.id) \
            .join(DrugMaster, on=UniqueDrug.drug_id == DrugMaster.id) \
            .join(UniqueDrugAlias, on=AlternateDrugOption.alternate_unique_drug_id == UniqueDrugAlias.id) \
            .join(DrugMasterAlias, on=UniqueDrugAlias.drug_id == DrugMasterAlias.id) \
            .where(AlternateDrugOption.facility_dis_id == facility_dist_id)

        return list(data)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_alternate_drug_option_dao:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_drug_option_dao {}".format(e))
        raise e


@log_args_and_response
def remove_alternate_drug_option_dao(drug_ids_list: list, facility_distribution_id: int, user_id: int) -> bool:
    """
    remove alternate drug option data dao
    @param facility_distribution_id:
    @param user_id:
    @param drug_ids_list:
    @return:
    """
    try:
        status: bool = False
        drug_id_list = drug_ids_list.split(',')
        unique_drug_ids = UniqueDrug.select(UniqueDrug.id).dicts() \
            .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(DrugMaster.id << drug_id_list)

        unique_drug_ids_list = [item['id'] for item in unique_drug_ids]

        if unique_drug_ids_list:
            args_dict = {'unique_drug_ids': unique_drug_ids_list,
                         'facility_distribution_id': facility_distribution_id,
                         'user_id': user_id}
            status = AlternateDrugOption.remove_alternate_drug_distribution_id(info_dict=args_dict)

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in remove_alternate_drug_option_dao:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in remove_alternate_drug_option_dao {}".format(e))
        raise e


@log_args
def get_altered_drugs_dao(pack_id: int):
    """
       To get all altered drugs of a pack
       @param pack_id:
       @return:
       @return:
    """
    altered_drugs: list = list()
    txr_list = []

    try:
        query = DrugMaster.select(DrugMaster.id,
                                  DrugMaster.drug_name,
                                  DrugMaster.ndc,
                                  DrugMaster.formatted_ndc,
                                  DrugMaster.strength,
                                  DrugMaster.strength_value,
                                  DrugMaster.manufacturer,
                                  DrugMaster.txr,
                                  DrugMaster.imprint,
                                  DrugMaster.color,
                                  DrugMaster.shape,
                                  DrugMaster.image_name,
                                  DrugMaster.brand_flag,
                                  DrugMaster.brand_drug,
                                  DrugMaster.drug_form,
                                  PackRxLink.id.alias('pack_rx_id')).dicts() \
            .join(PackRxLink, on=PackRxLink.original_drug_id == DrugMaster.id) \
            .where(PackRxLink.pack_id == pack_id)

        for record in query:
            txr_list.append(record['txr'])
            altered_drugs.append(record)
        if altered_drugs:
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
            for record in altered_drugs:
                record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), 0)
        return altered_drugs

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_altered_drugs_dao:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_altered_drugs_dao {}".format(e))
        raise e


@log_args_and_response
def remove_alternate_drug_by_id(update_dict: dict, alt_drug_option_ids: list):
    """
        update alternate drug option by alternate drug option id
        @param update_dict:
        @param alt_drug_option_ids:
        @return:
    """
    try:
        status = AlternateDrugOption.db_remove_alternate_drug_by_id(update_dict=update_dict, alt_drug_option_id=alt_drug_option_ids)
        logger.info("In remove_alternate_drug_by_id: Alt_drug_option_ids {} deselected with status: {}".format(alt_drug_option_ids, status))
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("error in remove_alternate_drug_by_id {}".format(e))
        raise e


@log_args_and_response
def get_packs_to_update_dao(old_drug_ids, current_pack_id) :
    """
        function to get query for packs data to update
        @param batch_id:
        @param current_drug:
        @param current_pack_id:
        @return:

    """
    packs_clauses: list = list()
    try:
        packs_clauses.append((SlotDetails.drug_id << old_drug_ids))

        packs_clauses.append((PackAnalysis.pack_id == current_pack_id))
        analysis_to_update = PackAnalysis.select(PackAnalysis.pack_id,
                                                 SlotDetails.id.alias('slot_id'),
                                                 PackAnalysis.id.alias('analysis_id')).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .where(functools.reduce(operator.and_, packs_clauses))
        logger.info("In _update_alternate_drug_for_batch_manual_canister:  Pack_analysis data to update : {}".format(
            analysis_to_update))

        return analysis_to_update

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_packs_to_update_dao:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_packs_to_update_dao {}".format(e))
        raise e


def get_manual_drug_manual_pack_dao(drug_id: int):
    """
        function to get manual alternate drug of pack drug by drug id
        @param drug_id:

    """
    try:
        DrugMasterAlias = DrugMaster.alias()
        query = DrugMaster.select(DrugMaster.id.alias('alt_drug_id'),
                                  DrugMaster.drug_name.alias('alt_drug_name'),
                                  DrugMaster.ndc.alias('alt_ndc'),
                                  DrugMaster.strength.alias('alt_strength'),
                                  DrugMaster.brand_flag.alias('alt_brand_flag'),
                                  DrugMaster.strength_value.alias('alt_strength_value'),
                                  DrugMaster.imprint.alias('alt_imprint'),
                                  DrugMaster.image_name.alias('alt_image_name'),
                                  DrugMasterAlias.id.alias('drug_id'),
                                  DrugStatus.ext_status.alias('alt_ext_status'),
                                  DrugStatus.ext_status_updated_date.alias('alt_ext_status_updated_date'),
                                  DrugStatus.last_billed_date.alias('alt_last_billed_date'),
                                  fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr).alias('alt_fndc_txr'),
                                  fn.CONCAT(DrugMasterAlias.formatted_ndc, '#', DrugMasterAlias.txr).alias(
                                      'current_fndc_txr'),
                                  DrugMaster.concated_drug_name_field(include_ndc=True).alias('alt_drug'),
                                  fn.CONCAT(PackHistory.new_value).alias('value'),
                                  fn.CONCAT(PackHistory.action_date_time).alias('action_date_time'),
                                  fn.CONCAT(PackHistory.action_taken_by).alias('action_taken_by')) \
            .join(PackHistory, JOIN_LEFT_OUTER, on=(DrugMaster.id == PackHistory.new_value) &
                                                   (PackHistory.action_id << [settings.PACK_HISTORY_NDC_CHANGE])) \
            .join(DrugMasterAlias, on=(DrugMasterAlias.txr == DrugMaster.txr) &
                                      (DrugMasterAlias.formatted_ndc != DrugMaster.formatted_ndc)) \
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
            .where(DrugMaster.formatted_ndc != DrugMasterAlias.formatted_ndc,
                   DrugMasterAlias.brand_flag == settings.GENERIC_FLAG,
                   DrugMasterAlias.id == drug_id) \
            .group_by(DrugMaster.id) \
            .order_by(DrugStatus.ext_status.desc(),
                      SQL('FIELD(alt_brand_flag, "1")').desc(),
                      DrugStatus.last_billed_date.desc(),
                      PackHistory.action_date_time.desc())
        return query

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_drug_manual_pack_dao:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_manual_drug_manual_pack_dao {}".format(e))
        raise e


@log_args_and_response
def get_save_alternate_drug(batch_id: int, company_id: int) -> dict:
    """
        function to save alternate drug
        @param batch_id:
        @param company_id:
    """
    try:
        DrugMasterAlias = DrugMaster.alias()

        query = PackRxLink.select(DrugMasterAlias.formatted_ndc,
                                  DrugMasterAlias.txr,
                                  DrugMaster.formatted_ndc.alias('alt_formatted_ndc'),
                                  DrugMaster.txr.alias('alt_txr')).dicts() \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == PackRxLink.bs_drug_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.company_id == company_id,
                   PackDetails.batch_id == batch_id,
                   PackRxLink.bs_drug_id.is_null(False),
                   DrugMasterAlias.formatted_ndc != DrugMaster.formatted_ndc) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        return query

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_save_alternate_drug:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_save_alternate_drug {}".format(e))
        raise e


@log_args_and_response
def update_pack_analysis(alt_fndc_txr_dict: dict, batch_id: int, zone_id: int, company_id: int) -> bool:
    """
        function to update pack analysis data
        @param alt_fndc_txr_dict:
        @param zone_id:
        @return:
        @param batch_id:
        @param company_id:

    """
    original_drug_can_data = defaultdict(list)
    alt_drug_can_data = defaultdict(list)
    manual_canisters: list = list()
    base_fndc_txr: list = list()
    alternate_fndc_txr: list = list()
    alt_can_data: list = list()
    original_can_data: list = list()
    analysis_details_ids: list = list()
    analysis_ids: set = set()
    try:
        for key, value in alt_fndc_txr_dict.items():
            base_fndc_txr.append(key)
            alternate_fndc_txr.append(value)

        logger.info('In update_pack_analysis: base_fndc_txr: ' + str(base_fndc_txr))
        logger.info('In update_pack_analysis: alternate_fndc_txr: ' + str(alternate_fndc_txr))

        query = PackAnalysis.select(fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('required_qty'),
                                    PackAnalysisDetails.canister_id,
                                    PackRxLink.fill_manually,
                                    DrugMaster.formatted_ndc,
                                    DrugMaster.txr).dicts() \
            .join(PackAnalysisDetails, on=(PackAnalysis.id == PackAnalysisDetails.analysis_id)) \
            .join(PackDetails, on=((PackAnalysis.pack_id == PackDetails.id) &
                                   (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PackRxLink.bs_drug_id) \
            .where(PackDetails.company_id == company_id,
                   PackDetails.batch_id == batch_id,
                   PackAnalysisDetails.canister_id.is_null(False),
                   fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr) << base_fndc_txr,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   PatientRx.daw_code == 0,
                   PackRxLink.original_drug_id.is_null(False)) \
            .group_by(PackAnalysisDetails.canister_id) \
            .order_by(fn.SUM(fn.FLOOR(SlotDetails.quantity)).desc())

        for record in query:
            if record['canister_id']:
                if record['fill_manually']:
                    manual_canisters.append(record['canister_id'])
                else:
                    original_drug_can_data['{}#{}'.format(record['formatted_ndc'], record['txr'])] \
                        .append(int(record['canister_id']))

        logger.info("In update_pack_analysis: manual_canisters:" + str(manual_canisters))
        logger.info("In update_pack_analysis: original_drug_can_data:" + str(original_drug_can_data))

        canister_query = CanisterMaster.select(CanisterMaster.available_quantity,
                                               DrugMaster,
                                               LocationMaster.device_id,
                                               LocationMaster.display_location,
                                               DeviceMaster.name.alias('device_name'),
                                               DeviceMaster.system_id,
                                               CanisterMaster.id.alias('canister_id')).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .join(CanisterZoneMapping, on=CanisterMaster.id == CanisterZoneMapping.canister_id) \
            .join(ZoneMaster, on=ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(ReservedCanister, JOIN_LEFT_OUTER, on=ReservedCanister.canister_id == CanisterMaster.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(ZoneMaster.id == zone_id,
                   CanisterMaster.active == settings.is_canister_active,
                   fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr) << alternate_fndc_txr,
                   ReservedCanister.id.is_null(True)) \
            .group_by(CanisterMaster.id) \
            .order_by(CanisterMaster.available_quantity.desc())

        for record in canister_query:
            alt_drug_can_data['{}#{}'.format(record['formatted_ndc'], record['txr'])] \
                .append(int(record['canister_id']))

        for original_fndc_txr, alt_fndc_txr in alt_fndc_txr_dict.items():
            if original_drug_can_data.get(original_fndc_txr, None):
                original_can_data.append(original_drug_can_data[original_fndc_txr])
                alt_can_data.append(alt_drug_can_data.get(alt_fndc_txr, None))
            else:
                logger.info('In update_pack_analysis: No original canister found for {}'.format(original_fndc_txr))

        logger.info('In update_pack_analysis: alt_can_data: ' + str(alt_can_data))
        logger.info('In update_pack_analysis: original_drug_can_data: ' + str(original_drug_can_data))

        if alt_can_data:
            response = update_canister_data(original_can_data=original_can_data,
                                            alt_can_data=alt_can_data,
                                            batch_id=batch_id,
                                            manual_canisters=manual_canisters)
            return response

        else:
            analysis_data = PackAnalysisDetails.select(PackAnalysisDetails.id,
                                                       PackAnalysis.pack_id,
                                                       PackAnalysisDetails.canister_id,
                                                       PackAnalysisDetails.analysis_id).dicts() \
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .join(DrugMaster, on=DrugMaster.id == PackRxLink.bs_drug_id) \
                .join(PackDetails, on=((PackAnalysis.pack_id == PackDetails.id) &
                                       (PackAnalysis.batch_id == PackDetails.batch_id))) \
                .where(fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr) << base_fndc_txr,
                       PackAnalysis.batch_id == batch_id)

            for record in analysis_data:
                analysis_details_ids.append(record['id'])
                analysis_ids.add(record['pack_id'])
                manual_canisters.append(record['canister_id'])

            logger.info("In update_pack_analysis: manual_canisters: {}, analysis_ids: {}, analysis_details_ids: {}"
                        .format(manual_canisters, analysis_ids, analysis_details_ids))

            if manual_canisters:
                transfer_status = CanisterTransfers.db_remove_canister(batch_id=batch_id, canister_ids=manual_canisters)

                reserved_status = ReservedCanister.db_remove_reserved_canister(canister_ids=manual_canisters, batch_id=batch_id)
                logger.info("In update_pack_analysis: reserved_status: {}, transfer_status: {}".format(reserved_status, transfer_status))
                logger.info('In update_pack_analysis:marking_packs_manual_fill_in_analysis_ids: {}'.format(analysis_ids))

            PackAnalysis.db_update_manual_packs(analysis_ids=list(analysis_ids), manual=True)
            status = PackAnalysisDetails.update_manual_canister_location_v2(analysis_details_ids=analysis_details_ids)
            return status

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_pack_analysis {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in update_pack_analysis {}".format(e))
        raise e


@log_args_and_response
def update_canister_data(original_can_data: list, alt_can_data: list, batch_id: int, manual_canisters: list) -> bool:
    """
        function to update canister data
        @param batch_id:
        @param original_can_data:
        @param alt_can_data:
        @param manual_canisters:
        @return:

    """
    update_original_can_list: list = list()
    update_alt_can_list: list = list()

    try:
        for i in range(0, len(original_can_data)):
            if not alt_can_data[i]:
                manual_canisters.extend(original_can_data[i])
            else:
                if len(original_can_data[i]) > len(alt_can_data[i]):
                    manual_canisters.extend(original_can_data[i])
                else:
                    required_alternate_canisters = alt_can_data[i][0: len(original_can_data[i])]
                    update_original_can_list.extend(original_can_data[i])
                    update_alt_can_list.extend(required_alternate_canisters)

        logger.info(f"In update_canister_data: update_original_can_list: {update_original_can_list}")

        if update_original_can_list:
            new_seq_tuple = list(tuple(zip(update_original_can_list, update_alt_can_list)))
            logger.info('In update_canister_data: new_seq_tuple_alt: ' + str(new_seq_tuple))
            case_sequence = case(PackAnalysisDetails.canister_id, new_seq_tuple)
            reserved_can_case_seq = case(ReservedCanister.canister_id, new_seq_tuple)
            canister_transfer_case_seq = case(CanisterTransfers.canister_id, new_seq_tuple)

            updated_reserved_can = ReservedCanister.db_replace_canister_list(batch_id=batch_id,
                                                                             case_sequence=reserved_can_case_seq,
                                                                             canister_list=update_original_can_list)
            logger.info('In update_canister_data: updated_reserved_can:{}'.format(updated_reserved_can))

            updated_canister_transfers = CanisterTransfers.db_replace_canister_list(batch_id=batch_id,
                                                                                    canister_list=update_original_can_list,
                                                                                    case_sequence=canister_transfer_case_seq)
            logger.info('In update_canister_data: updated_canister_transfers:{}'.format(updated_canister_transfers))

            analysis_data = PackAnalysisDetails.select(PackAnalysisDetails.id,
                                                       PackAnalysis.pack_id).dicts() \
                        .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                        .join(PackDetails, on=((PackAnalysis.pack_id == PackDetails.id) &
                                               (PackAnalysis.batch_id == PackDetails.batch_id))) \
                        .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                        .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                        .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                        .where(PackAnalysis.batch_id == batch_id,
                               PackAnalysisDetails.canister_id << update_original_can_list,
                               PatientRx.daw_code == 0)

            analysis_details_ids: list = list()
            for record in analysis_data:
                analysis_details_ids.append(record['id'])
            logger.info("In update_canister_data: updating_pack_analysis_details_for_ids: {} and canister_seq {}".format(analysis_details_ids,
                                                                                                new_seq_tuple))
            resp = PackAnalysisDetails.update(canister_id=case_sequence).where(
                PackAnalysisDetails.id.in_(analysis_details_ids)).execute()
            logger.info("In update_canister_data: updating_pack_analysis_details: {}".format(resp))

        logger.info(f"In update_canister_data:manual_canisters: {manual_canisters}")

        if manual_canisters:
            analysis_data = PackAnalysisDetails.select(PackAnalysisDetails.id,
                                                       PackAnalysisDetails.analysis_id).dicts() \
                    .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                    .join(PackDetails, on=((PackAnalysis.pack_id == PackDetails.id) &
                                           (PackAnalysis.batch_id == PackDetails.batch_id))) \
                    .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                    .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                    .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                    .join(DrugMaster, on=DrugMaster.id == PackRxLink.bs_drug_id) \
                    .where(PackAnalysisDetails.canister_id << manual_canisters,
                           PackAnalysis.batch_id == batch_id)

            analysis_details_ids: list = list()
            analysis_ids: set = set()
            for record in analysis_data:
                analysis_details_ids.append(record['id'])
                analysis_ids.add(record['analysis_id'])
            if manual_canisters:
                transfer_status = CanisterTransfers.db_remove_canister(batch_id=batch_id,
                                                                       canister_ids=manual_canisters)
                reserved_status = ReservedCanister.db_remove_reserved_canister(canister_ids=manual_canisters,
                                                                               batch_id=batch_id)
                logger.info("In update_pack_analysis: reserved_status: {}, transfer_status: {}".format(reserved_status,
                                                                                                       transfer_status))

            logger.info('In update_pack_analysis: analysis_ids: {}, analysis_details_ids: {}'.format(analysis_ids, analysis_details_ids))
            pack_analysis_status = PackAnalysis.db_update_manual_packs(analysis_ids=list(analysis_ids),
                                                                       manual=True)
            pack_analysis_details_status = PackAnalysisDetails.update_manual_canister_location_v2(analysis_details_ids=analysis_details_ids)
            logger.info("In update_pack_analysis: pack_analysis_status: {}, pack_analysis_details_status: {}".format(pack_analysis_status,
                                                                                                   pack_analysis_details_status))
        return True

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_canister_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in update_canister_data {}".format(e))
        raise e


@log_args_and_response
def db_get_progress_filling_left_pack_ids_device_wise(device_id: int) -> list:
    """
    Replace canister_id with alt_canister_id.
    @param batch_id:
    :return:
    @param device_id:
    """
    try:
        pack_id_query = PackDetails.select(PackDetails,
                                           PackDetails.id.alias('pack_id')).dicts() \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(PackDetails.pack_status == settings.PROGRESS_PACK_STATUS,
                   PackAnalysisDetails.device_id == device_id,
                   SlotTransaction.id.is_null(True)) \
            .group_by(PackDetails.id)
        pack_ids = [record['pack_id'] for record in pack_id_query]
        return pack_ids

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_progress_filling_left_pack_ids_device_wise {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_get_progress_filling_left_pack_ids_device_wise {}".format(e))
        raise


@log_args_and_response
def alternate_drug_update_facility(dict_alternate_drug_info):
    """ Updates the alternate drug information for the packs in the
    SlotTransaction table and also sends the alternate drug information
    to the pharmacy software.

    Args:
        dict_alternate_drug_info (dict): The json dict containing
                                        batchlist, olddruglist, newdruglist, canisterlist

    Returns:
        json response of success or failure

    Examples:
        >>> alternate_drug_update()
        None

    """

    slot_details_updation = {}
    pack_drug_tracker_details = []

    company_id = dict_alternate_drug_info["company_id"]
    if len(dict_alternate_drug_info["olddruglist"]) == 0:
        return create_response(1)
    # if all(item not in dict_alternate_drug_info for item in ['pack_list', 'facility_distribution_id']):
    #     return error(1001, "Missing Parameter(s): pack_list or facility_distribution_id.")

    # if "facility_distribution_id" in dict_alternate_drug_info:
    #     pack_ids = PackDetails.db_get_pack_ids_by_batch_id(
    #         dict_alternate_drug_info['facility_distribution_id'],
    #         company_id
    #     )
    # else:
    pack_ids = dict_alternate_drug_info["pack_list"]
    ips_drug_ids = deepcopy(dict_alternate_drug_info["olddruglist"])
    ips_alt_drug_ids = deepcopy(dict_alternate_drug_info["newdruglist"])

    original_drug_ids = deepcopy(dict_alternate_drug_info["olddruglist"])

    logger.info('fetched_ips_drug_ids: {} and ips_alt_drug_ids: {}'.format(ips_drug_ids, ips_alt_drug_ids))
    dict_alternate_drug_info['olddruglist'] = [
        item for item in dict_alternate_drug_info['olddruglist'] for i in range(len(pack_ids))
    ]
    dict_alternate_drug_info['newdruglist'] = [
        item for item in dict_alternate_drug_info['newdruglist'] for i in range(len(pack_ids))
    ]
    # make list which will be sent to IPS, this will be updated later by NDC.
    user_id = dict_alternate_drug_info["user_id"]
    drug_ids = dict_alternate_drug_info["olddruglist"]
    alt_drug_ids = dict_alternate_drug_info["newdruglist"]
    try:  # convert to int, throw error if can not convert to int
        ips_drug_ids = list(map(int, ips_drug_ids))
        ips_alt_drug_ids = list(map(int, ips_alt_drug_ids))
        logger.info('final_ips_drug_ids: {} and ips_alt_drug_ids: {}'.format(ips_drug_ids, ips_alt_drug_ids))
    except ValueError as e:
        logger.error(e, exc_info=True)
        return error(1020, "Element of olddruglist and newdruglist must be integer.")

    valid_packlist = PackDetails.db_verify_packlist(pack_ids, company_id)
    if not valid_packlist:
        return error(1014)

    company_settings = get_company_setting_by_company_id(company_id=company_id)
    required_settings = settings.ALTERNATE_DRUG_SETTINGS
    settings_present = all([key in company_settings for key in required_settings])
    if not settings_present:
        return error(6001)

    packlist_len = len(pack_ids)
    drugs_ids_len = len(drug_ids)
    alt_drug_dict = {}

    # get the number of distinct alternate drugs
    _size = int(drugs_ids_len / packlist_len)
    new_pack_ids = []  # only those pack ids which really have old drugs
    try:
        with db.transaction():
            for i in range(0, _size):
                alt_drug_dict[int(drug_ids[i * packlist_len])] = int(alt_drug_ids[i * packlist_len])

            patient_rx_ids = {}
            pack_rx_link_original_drug_ids = {}
            pack_ids = list(set(pack_ids))
            # Changed by: Jitendra Kumar Saxena 13/12/2017
            # for handling daw drug updation -- allowed for daw 0 only
            # fetch only those patient_rx_ids where daw value is zero
            for record in PackRxLink.select(
                    PackRxLink.patient_rx_id,
                    PackRxLink.id,
                    PackRxLink.original_drug_id,
                    SlotDetails.drug_id,
                    PackRxLink.pack_id
            ).dicts() \
                    .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                    .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                    .where(PackRxLink.pack_id << pack_ids, PatientRx.daw_code == 0):
                try:
                    patient_rx_ids[record["patient_rx_id"]] = alt_drug_dict[record["drug_id"]]

                    # If original_drug_id is null then store current drug id as original drug id in pack rx link
                    # this is required so we can send the flag of ndc change while printing label
                    if record["original_drug_id"] is None:
                        pack_rx_link_original_drug_ids[record["id"]] = record["drug_id"]

                    new_pack_ids.append(record["pack_id"])
                except KeyError:
                    pass  # not really drug id for that given pack id so will throw key error

            if not new_pack_ids:  # if no pack has given old drug id return 0
                return create_response(0)

            for record in SlotDetails.select(
                    SlotDetails.id,
                    SlotDetails.drug_id,
                    PackRxLink.pack_id,
            ).dicts() \
                    .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                    .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                    .where(PackRxLink.pack_id << pack_ids, PatientRx.daw_code == 0,
                           SlotDetails.drug_id << original_drug_ids):

                # pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                #                           "updated_drug_id": alt_drug_dict[record["drug_id"]],
                #                           "module": constants.PDT_BATCH_GENERATION,
                #                           "modified_by": 11, "modified_date": get_current_date_time()}
                #
                # pack_drug_tracker_details.append(pack_drug_tracker_info)

                slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                       "drug_id": alt_drug_dict[record["drug_id"]]}

                pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                          "updated_drug_id": alt_drug_dict[record["drug_id"]],
                                          "module": constants.PDT_BATCH_GENERATION,
                                          "created_by": user_id, "created_date": get_current_date_time()}

                pack_drug_tracker_details.append(pack_drug_tracker_info)

            for key, value in patient_rx_ids.items():
                status1 = PatientRx.update(
                    drug_id=value,
                    modified_by=user_id,
                    modified_date=get_current_date_time()
                ).where(PatientRx.id == key).execute()
                logger.info("Updating PatientRx in alternate drugs with values "
                             ": " + str(key) + "," + str(value) + ":" + str(status1))

            for key, value in pack_rx_link_original_drug_ids.items():
                status2 = PackRxLink.update(
                    original_drug_id=value
                ).where(PackRxLink.id == key).execute()
                logger.info("Updating PackRxLink alternate drugs with values "
                             ": " + str(key) + "," + str(value) + ":" + str(status2))

            for slot_details_id, slot_drugs in slot_details_updation.items():
                drug_id = slot_drugs["drug_id"]
                prev_drug_id = slot_drugs["prev_drug_id"]

                slot_details_update_status = SlotDetails.update(
                    drug_id=drug_id
                ).where(SlotDetails.id == slot_details_id).execute()

                logger.info(
                    f"Updating SlotDetails drugs with values, id: {slot_details_id}, prev_drug_id: {prev_drug_id}, "
                    f"updated_drug_id: {drug_id} with status: {slot_details_update_status}")

            populate_pack_drug_tracker(pack_drug_tracker_details)

            # Code was removed on 10th May, 2022 as we don't need to trigger multiple AlternateDrug calls to IPS.
            # Instead, handle this through updatefilledby call.
            # settings.PHARMACY_UPDATE_ALT_DRUG_URL

        return create_response(1)
    except (InternalError, DataError, IntegrityError) as e:
        logger.error("error in alternate_drug_update_facility {}".format(e))
        raise e
    except PharmacySoftwareCommunicationException as e:
        logger.error("error in alternate_drug_update_facility {}".format(e))
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error("error in alternate_drug_update_facility {}".format(e))
        raise e

@log_args_and_response
def update_alternate_drug_for_batch_data_pack_queue(canister_id: int, alt_drug_id: int,
                                         current_pack_id: int, device_id: int, user_id: int, company_id: int, batch_id: int = None) -> tuple:
    """
        update alternate drug for batch
        :return: query
        @param canister_id:
        @param alt_drug_id:
        @param batch_id:
        @param current_pack_id:
        @param device_id:
        @param user_id:
        @param company_id:
        @return:
        """

    try:
        current_drug = get_canister_by_id_dao(canister_id)
        alternate_drug = db_get_drug_status_by_id(drug_id=alt_drug_id, dicts=True)
        valid_alternate_drug = current_drug and alternate_drug \
                               and current_drug['formatted_ndc'] != alternate_drug['formatted_ndc'] \
                               and current_drug['txr'] == alternate_drug['txr'] \
                               and str(current_drug['brand_flag']) == \
                               str(alternate_drug['brand_flag']) == settings.GENERIC_FLAG
        # and alternate_drug['ext_status'] == settings.VALID_EXT_STATUS

        logger.info("In update_alternate_drug_for_batch_data: valid_alternate_drug: {}".format(valid_alternate_drug))
        if not valid_alternate_drug:
            raise ValueError(' drug_id and alt_drug_id are not alternate drugs')

        old_drug_ids = [item.id for item in DrugMaster.get_drugs_by_formatted_ndc_txr(formatted_ndc=current_drug['formatted_ndc'],
                                                                                      txr=current_drug['txr'])]
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e

    try:
        # drug_id = current_drug['drug_id']
        alt_drug_id = alternate_drug['id']
        mfd_pack_ids = get_mfd_drug_packs_pack_queue(old_drug_ids)
        logger.info("In update_alternate_drug_for_batch_data: mfd_pack_ids: {}".format(mfd_pack_ids))

        clauses = []

        if mfd_pack_ids:
            clauses.append(PackDetails.id.not_in(mfd_pack_ids))

        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info("In update_alternate_drug_for_batch_data: current_pack_id: {}, filling_pending_pack_ids: {}".format(current_pack_id, filling_pending_pack_ids))

        if current_pack_id:
            filling_pending_pack_ids.append(current_pack_id)
        if filling_pending_pack_ids:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                           | (PackDetails.id << filling_pending_pack_ids))
        else:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        # query to get pending packs
        pending_packs = PackDetails.select(PackDetails.id).distinct()\
            .join(PackQueue, on=PackDetails.id==PackQueue.pack_id)\
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(*clauses)

        # update data of pending packs
        packs_to_update = PackAnalysis.select(PackAnalysis.pack_id,
                                              PackAnalysisDetails.slot_id,
                                              PatientRx.daw_code,
                                              PackAnalysis.id.alias('analysis_id')) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(SlotDetails.drug_id << old_drug_ids,
                   PackAnalysis.pack_id << pending_packs,
                   PackAnalysisDetails.device_id == device_id)

        daw_zero_analysis_ids_set: set = set()
        non_zero_daw_analysis_ids_set: set = set()
        pack_ids: list = list()
        drug_list: list = list()
        # pack_analysis_id_dict = dict()
        alt_drug_list: list = list()
        slot_ids: list = list()

        for record in packs_to_update.dicts():
            pack_ids.append(record['pack_id'])
            if record['daw_code'] == 0:
                daw_zero_analysis_ids_set.add(record['analysis_id'])
            else:
                non_zero_daw_analysis_ids_set.add(record['analysis_id'])
            slot_ids.append(record['slot_id'])

        logger.info("In update_alternate_drug_for_batch_data: pack_ids: {}, old_drug_ids: {}, daw_zero_analysis_ids: {}, non_zero_daw_analysis_ids: {}, slot_ids: {}"
                    .format(pack_ids, old_drug_ids, daw_zero_analysis_ids_set, non_zero_daw_analysis_ids_set, slot_ids))
        if not pack_ids or not old_drug_ids:
            # as no packs needs update, so returning True as no action required
            return True, []

        daw_zero_analysis_ids = list(daw_zero_analysis_ids_set)
        non_zero_daw_analysis_ids = list(non_zero_daw_analysis_ids_set)

        query = PackRxLink.select(PackRxLink.pack_id,
                                  SlotDetails.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(PackRxLink.pack_id << pack_ids,
                   SlotDetails.drug_id << old_drug_ids)

        pack_list: list = list()

        for record in query.dicts():
            pack_list.append(record['pack_id'])
            if record['drug_id'] not in drug_list:
                drug_list.append(record['drug_id'])
                alt_drug_list.append(alt_drug_id)

        logger.info("In update_alternate_drug_for_batch_data: pack_list: {}, drug_list: {}, alt_drug_list: {}"
            .format(pack_list, drug_list, alt_drug_list))

        remaining_analysis_ids = PackAnalysis.select(PackAnalysis.id.alias('analysis_id'),
                                                     PackAnalysis.pack_id,
                                                     fn.GROUP_CONCAT(
                                                         fn.DISTINCT(PackAnalysisDetails.location_number)).coerce(
                                                         False).alias('location_number'),
                                                     fn.GROUP_CONCAT(
                                                         fn.DISTINCT(PackAnalysisDetails.canister_id)).coerce(
                                                         False).alias('canister_id')) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(SlotDetails.drug_id.not_in(old_drug_ids),
                   PackAnalysis.pack_id << pack_list,
                   PackAnalysisDetails.device_id == device_id) \
            .group_by(PackAnalysis.pack_id)

        robot_packs: set = set()
        # robot_analysis_ids = set()
        for record in remaining_analysis_ids.dicts():
            if record['canister_id'] and record['location_number']:
                canister_ids = list(record['canister_id'].split(","))
                location_number = list(record['location_number'].split(","))

                if not any(canister_ids) is False and not any(location_number) is False:
                    robot_packs.add(record['pack_id'])

        manual_pack_list = list(set(pack_list) - robot_packs)

        logger.info("In update_alternate_drug_for_batch_data: robot_packs: {}, manual_pack_list: {}"
                    .format(robot_packs, manual_pack_list))

        if manual_pack_list:
            for current_in_progress_pack in filling_pending_pack_ids:
                if current_in_progress_pack in manual_pack_list:
                    manual_pack_list.remove(current_in_progress_pack)
            if manual_pack_list:
                logger.info(
                    'In update_alternate_drug_for_batch_data: Alternate drug data for: canister_id: {} and alt_drug:  {} :: daw_zero_analysis_ids {},'
                    ' non_zero_daw_analysis_ids {} and manual_pack_list {}'.format(
                        canister_id, alt_drug_id, daw_zero_analysis_ids, non_zero_daw_analysis_ids, manual_pack_list))
                return False, manual_pack_list

        pack_analysis_id_list = daw_zero_analysis_ids

        # keeping canister ids in the analysis details id where daw code is not zero as we are not changing drug so
        # drug and canister drug won't create conflict
        canister_analysis_ids = list(non_zero_daw_analysis_ids)
        logger.info(
            'In update_alternate_drug_for_batch_data: Alternate drug data for: canister_id: {} and alt_drug:  {} :: pack_analysis_id_list {},'
            ' canister_analysis_ids {}'.format(
                canister_id, alt_drug_id, pack_analysis_id_list, canister_analysis_ids))

        with db.transaction():
            if len(pack_analysis_id_list):
                update_dict = {'location_number': None,
                               'quadrant': None,
                               'canister_id': None,
                               'drop_number': None,
                               'config_id': None
                               }
                pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(update_dict=update_dict,
                    analysis_id=pack_analysis_id_list,
                    slot_id=slot_ids,
                    device_id=device_id)
                logger.info("In update_alternate_drug_for_batch_data: pack_analysis_status: {} for pack_analysis_id_list: {}".format(
                    pack_analysis_status, pack_analysis_id_list))

            if canister_analysis_ids:
                update_dict = {'location_number': None,
                               'quadrant': None,
                               'drop_number': None,
                               'config_id': None
                               }
                pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(
                    update_dict=update_dict,
                    analysis_id=canister_analysis_ids,
                    slot_id=slot_ids,
                    device_id=device_id)
                logger.info("In update_alternate_drug_for_batch_data: pack_analysis_status: {} for canister_analysis_ids :{}".format(
                    pack_analysis_status, canister_analysis_ids))

            if daw_zero_analysis_ids and old_drug_ids:
                # delete reserved canister data
                status = ReservedCanister.db_remove_reserved_canister(canister_ids=[canister_id])
                logger.info("In update_alternate_drug_for_batch_data: reserved canister: {} deleted:{}".format(
                        canister_id, status))
                response = alternate_drug_update({'pack_list': ','.join(map(str, pack_list)),
                                                  'olddruglist': ','.join(map(str, drug_list)),
                                                  'newdruglist': ','.join(map(str, alt_drug_list)),
                                                  'user_id': user_id,
                                                  'company_id': company_id,
                                                  'module_id': constants.PDT_REPLENISH_ALTERNATES
                                                  })
                response = json.loads(response)
                if response['status'] != 'success':
                    # throwing exception to rollback changes as we could not update IPS
                    raise AlternateDrugUpdateException(response['code'])
                BatchChangeTracker.db_save(batch_id=batch_id,
                                               user_id=user_id,
                                               action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.UPDATE_ALT_DRUG],
                                               params={"canister_id": canister_id,
                                                       "alt_drug_id": alt_drug_id,
                                                       "batch_id": batch_id,
                                                       "current_pack_id": current_pack_id,
                                                       "user_id": user_id},
                                               packs_affected=pack_list)
                return True, pack_list
            else:
                return False, []

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e
    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in update_alternate_drug_for_batch_data: PharmacySoftwareCommunicationException {}".format(e))
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error("Error in update_alternate_drug_for_batch_data: PharmacySoftwareResponseException {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in update_alternate_drug_for_batch_data: {}".format(e))
        raise e


@log_args_and_response
def get_mfd_drug_packs_pack_queue(old_drug_ids: list) -> List:
    """
    returns query to get the analysis info for the specified ndc
    :param batch_id: int
    :param old_drug_ids: list
    :return: query
    """
    pack_ids: list = list()
    try:
        mfd_status = [constants.MFD_CANISTER_SKIPPED_STATUS,
                      constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                      constants.MFD_CANISTER_RTS_DONE_STATUS]

        query = MfdAnalysis.select(PackRxLink.pack_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id)\
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id)\
            .where(SlotDetails.drug_id << old_drug_ids,
                   MfdAnalysis.status_id.not_in(mfd_status),
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])
        for record in query.dicts():
            pack_ids.append(record['pack_id'])

        return pack_ids
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_mfd_drug_packs {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_mfd_drug_packs {}".format(e))
        raise e


@log_args_and_response
def db_skip_for_batch_pack_queue(canister_list: list, user_id: int, device_id: int, current_pack: int = None,
                                 batch_id: int = None) -> tuple:
    """
    Canister will be not be considered for pending packs
    :param batch_id: int
    :param canister_list: List<int>
    :param user_id: int
    :param current_pack: int pack id whose pack_status is not pending and being filled by robot right now
    :return: bool
    """
    try:
        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info("In db_skip_for_batch: filling_pending_pack_ids: {}, current_pack: {},canister_list: {}"
                    .format(filling_pending_pack_ids, current_pack, canister_list))
        if current_pack:
            filling_pending_pack_ids.append(current_pack)
        if not canister_list:
            return False, None

        clauses = []

        if filling_pending_pack_ids:
            clauses.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                            | (PackDetails.id << filling_pending_pack_ids)))
        else:
            clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS])

        affected_packs: set = set()
        pack_analysis_id_set: set = set()
        pack_analysis_id_dict: dict = dict()
        pack_canister_dict = dict()
        delete_reserved_canister_analysis_id = list()
        canister_location_dict = dict()

        pack_analysis_list = PackAnalysis.select(PackAnalysis.id, PackAnalysis.pack_id, PackAnalysisDetails.canister_id,
                                                 PackAnalysisDetails.quadrant,
                                                 PackAnalysisDetails.device_id,
                                                 PackAnalysisDetails.location_number).dicts() \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
            .join(PackQueue, on=PackQueue.pack_id==PackDetails.id)\
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(*clauses, PackAnalysisDetails.canister_id << canister_list,
                   PackAnalysisDetails.device_id == device_id
                   )

        for record in pack_analysis_list:
            affected_packs.add(record['pack_id'])
            pack_analysis_id_set.add(record['id'])
            canister_location_dict[record["canister_id"]] = {'device_id': record["device_id"], 'quadrant': record["quadrant"], 'location_number': record["location_number"]}

            if record['pack_id'] not in pack_analysis_id_dict.keys():
                pack_analysis_id_dict[record['pack_id']] = set()
                pack_canister_dict[record['pack_id']] = set()
            pack_analysis_id_dict[record['pack_id']].add(record['id'])
            pack_canister_dict[record['pack_id']].add(record['canister_id'])

        logger.info("In db_skip_for_batch: pack_analysis_ids:{}, pack_analysis_id_dict: {},affected_packs: {} "
                    .format(pack_analysis_id_set, pack_analysis_id_dict, affected_packs))

        if not affected_packs:
            logger.info('No_packs_found_while_skipping_for_batch_for_canister: ' + str(canister_list))
            return True, None

        robot_analysis_ids: set = set()
        robot_pack_canister_dict = dict()
        non_robot_analysis_ids: set = set()
        non_robot_pack_canister_dict = dict()
        robot_packs: set = set()
        logger.info("In db_skip_for_batch : affected packs {}".format(affected_packs))
        if len(affected_packs):
            remaining_analysis_ids = PackAnalysis.select(fn.GROUP_CONCAT(
                                                             PackAnalysis.id).coerce(
                                                             False).alias('analysis_id'),
                                                         PackAnalysis.pack_id,
                                                         fn.GROUP_CONCAT(
                                                             PackAnalysisDetails.location_number).coerce(
                                                             False).alias('location_number'),
                                                         fn.GROUP_CONCAT(PackAnalysisDetails.canister_id).coerce(
                                                             False).alias("canister_id"),
                                                         fn.GROUP_CONCAT(fn.DISTINCT(fn.CONCAT(PackAnalysisDetails.canister_id, "-", PackAnalysisDetails.device_id, "-", PackAnalysisDetails.quadrant, "-", PackAnalysisDetails.location_number))).alias('can_destination')) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(*clauses, PackAnalysis.pack_id << list(affected_packs),
                       PackAnalysisDetails.canister_id.not_in(canister_list),
                       PackAnalysisDetails.location_number.is_null(False),
                       PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED) \
                .group_by(PackAnalysis.pack_id)

            for record in remaining_analysis_ids.dicts():
                if record['canister_id'] and record['location_number']:
                    canister_id = list(record['canister_id'].split(","))
                    location_number = list(record['location_number'].split(","))
                    analysis_ids = list(record['analysis_id'].split(","))
                    can_destination_list = list(record["can_destination"].split(","))
                    d = {}
                    d = {i.split("-", 1)[0]: {"device_id":i.split("-")[1], "quadrant": i.split("-")[2], "location_number": i.split("-")[3]} for i in can_destination_list}
                    canister_location_dict.update(d)
                    if not any(canister_id) is False and not any(location_number) is False:
                        robot_packs.add(record['pack_id'])
                        if record['pack_id'] in filling_pending_pack_ids:
                            non_robot_analysis_ids.update(analysis_ids)
                            if not non_robot_pack_canister_dict.get(record["pack_id"]):
                                non_robot_pack_canister_dict[record["pack_id"]] = set()
                            non_robot_pack_canister_dict[record["pack_id"]].update(canister_id)
                        else:
                            robot_analysis_ids.update(analysis_ids)
                            if not robot_pack_canister_dict.get(record["pack_id"]):
                                robot_pack_canister_dict[record["pack_id"]] = set()
                            robot_pack_canister_dict[record["pack_id"]].update(canister_id)

        manual_pack_list = list(affected_packs - robot_packs)
        logger.info("In db_skip_for_batch manual pack list: robot_packs: {},non_robot_analysis_ids: {}, robot_analysis_ids: {}"
                    .format(robot_packs, non_robot_analysis_ids, robot_analysis_ids))

        if len(manual_pack_list):
            for current_in_progress_pack in filling_pending_pack_ids:
                if current_in_progress_pack in manual_pack_list:
                    if current_in_progress_pack in pack_analysis_id_dict.keys():
                        non_robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        if not non_robot_pack_canister_dict.get(current_in_progress_pack):
                            non_robot_pack_canister_dict[current_in_progress_pack] = set()
                        non_robot_pack_canister_dict[current_in_progress_pack].update(
                            pack_canister_dict[current_in_progress_pack])
                    else:
                        robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        robot_pack_canister_dict[current_in_progress_pack].update(pack_canister_dict[current_in_progress_pack])
                    manual_pack_list.remove(current_in_progress_pack)

            logger.info("In db_skip_for_batch: non_robot_analysis_ids: {},robot_analysis_ids: {},manual_pack_list: {} "
                        .format(non_robot_analysis_ids, robot_analysis_ids, manual_pack_list))

            if manual_pack_list:
                mfd_pack_list = get_mfd_packs_from_given_pack_list_pack_queue(pack_list=manual_pack_list)
                logger.info("In db_skip_for_batch :mfd pack list {}".format(mfd_pack_list))

                if len(mfd_pack_list):
                    for pack in mfd_pack_list:
                        non_robot_analysis_ids.update(pack_analysis_id_dict[pack])
                        if not non_robot_pack_canister_dict.get(pack):
                            non_robot_pack_canister_dict[pack] = set()
                        non_robot_pack_canister_dict[pack].update(pack_canister_dict[pack])
                    manual_pack_list = list(set(manual_pack_list) - set(mfd_pack_list))

                if len(manual_pack_list):
                    return False, manual_pack_list

        insert_list = []
        if non_robot_analysis_ids or robot_analysis_ids:
            analysis_ids = list(non_robot_analysis_ids) + list(robot_analysis_ids)
            insert_list = get_insert_list_of_replenish_skipped_canister(analysis_ids, canister_list)
            logger.info(f"In db_skip_for_batch, insert_list: {insert_list}")

        with db.transaction():
            if len(non_robot_analysis_ids):
                logger.info("In db_skip_for_batch: non_robot_analysis_ids {}".format(non_robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None}
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in non_robot_pack_canister_dict.items() for can in canisters]
                #
                # logger.info(f"In db_skip_for_batch, non_robot_analysis_ids insert_list : {insert_list}")
                # inster_status = ReplenishSkippedCanister.insert_many(insert_list).execute()

                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}

                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(non_robot_analysis_ids))
                logger.info("In db_skip_for_batch: pack_analysis_status: {} for non_robot_analysis_ids: {}".format(
                    status, non_robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(non_robot_analysis_ids)

            if len(robot_analysis_ids):
                logger.info("db_skip_for_batch robot_analysis_ids {}".format(robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'canister_id': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None
                #                }
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in robot_pack_canister_dict.items() for can in canisters]
                # logger.info(f"In db_skip_for_batch, robot_analysis_ids insert_list : {insert_list}")
                # inster_status = ReplenishSkippedCanister.insert_many(insert_list).execute()

                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}

                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(robot_analysis_ids))
                logger.info("In db_skip_for_batch: pack_analysis_status: {} for robot_analysis_ids: {}".format(
                    status, robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(robot_analysis_ids)

            if insert_list:
                status = ReplenishSkippedCanister.insert_many(insert_list).execute()
                logger.info(f"In db_skip_for_batch, insert status: {status}")

            # if delete_reserved_canister_analysis_id:
            #     status = delete_reserved_canister_for_skipped_canister(canister_list=canister_list, analysis_id=delete_reserved_canister_analysis_id)
            #     logger.info("In db_skip_for_batch: reserved canister: {} deleted:{}".format(canister_list, status))
            BatchChangeTracker.db_save(batch_id=batch_id,
                                       user_id=user_id,
                                       action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.SKIP_FOR_BATCH],
                                       params={"canister_list": canister_list,
                                               "batch_id": batch_id,
                                               "user_id": user_id},
                                       packs_affected=list(affected_packs)
                                       )
            return True, list(affected_packs)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in db_skip_for_batch: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in db_skip_for_batch: {}".format(e))
        raise e


@log_args_and_response
def get_mfd_packs_from_given_pack_list_pack_queue(pack_list: list) -> list:
    """
    Function to get mfd packs from given pack list and batch
    @param pack_list: list
    @param batch_id: int
    @return:
    """
    mfd_pack_list = list()
    try:
        mfd_status = [constants.MFD_CANISTER_SKIPPED_STATUS,
                      constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                      constants.MFD_CANISTER_RTS_DONE_STATUS]

        query = MfdAnalysis.select(PackDetails.id.alias('pack_id')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
            .join(PackQueue, on=PackQueue.pack_id==PackDetails.id)\
            .where(PackDetails.id << pack_list,
                   MfdAnalysis.status_id.not_in(mfd_status)) \
            .group_by(PackDetails.id)

        for record in query:
            mfd_pack_list.append(record['pack_id'])

        return mfd_pack_list

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_mfd_packs_from_given_pack_list: {}".format(e))
        raise e


@log_args_and_response
def db_skip_canister_for_packs_pack_queue(canister_list: list, user_id: int, current_pack: int = None,
                               device_id: int = None, pack_count: int = None, manual_pack_count: int = None, batch_id: int = None) -> tuple:
    """
    Canister will be not be considered for pending packs
    @param batch_id:
    @param canister_list:
    @param user_id:
    @param current_pack: int pack id whose pack_status is not pending and being filled by robot right now
    @param device_id:
    @param pack_count: number of packs till which this canister should be skipped
    @param manual_pack_count: if some packs moved to manual then manual pack count to decrement from original pack count
    @return:
    """
    try:
        if manual_pack_count:
            pack_count = pack_count - manual_pack_count

        logger.info("In db_skip_canister_for_packs: pack_count: {}".format(pack_count))
        if not pack_count or pack_count <= 0:
            return True, []

        affected_packs: set = set()
        pack_analysis_id_set: set = set()
        pack_analysis_id_dict: dict = dict()
        pack_canister_dict = dict()
        packs_to_skip: list = list()
        delete_reserved_canister_analysis_id = list()
        canister_location_dict = dict()

        # check data for filling pending packs, i.e packs are in progress but not filled
        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids_device_wise(device_id=device_id)
        logger.info("In db_skip_canister_for_packs: filling_pending_pack_ids: {}, current_pack: {}"
                    .format(filling_pending_pack_ids, current_pack))

        if current_pack and current_pack not in filling_pending_pack_ids:
            filling_pending_pack_ids.append(current_pack)
        if not canister_list:
            return False, None

        logger.info("db_skip_canister_for_packs filling pending pack id {}".format(filling_pending_pack_ids))

        clauses = [PackAnalysisDetails.device_id == device_id]

        if filling_pending_pack_ids:
            packs_to_skip.extend(filling_pending_pack_ids)
            clauses.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                            | (PackDetails.id << filling_pending_pack_ids)))
        else:
            clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS])

        # query to get ordered pack' device wise
        if pack_count:
            pack_list_to_skip_query = PackAnalysis.select(PackDetails.order_no, PackAnalysis.pack_id).dicts() \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
                .join(PackQueue, on =PackQueue.pack_id==PackDetails.id)\
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(*clauses) \
                .group_by(PackDetails.id) \
                .order_by(PackDetails.order_no)

            for record in pack_list_to_skip_query:
                logger.info("packs to consider db_skip_canister_for_packs {}".format(record))
                if len(packs_to_skip) < int(pack_count):
                    if record['pack_id'] not in packs_to_skip:
                        packs_to_skip.append(record['pack_id'])
                else:
                    break

        logger.info("In db_skip_canister_for_packs packs to skip {}".format(packs_to_skip))
        if packs_to_skip:
            clauses.append(PackDetails.id << packs_to_skip)

        pack_analysis_list = PackAnalysis.select(PackAnalysis.id, PackAnalysis.pack_id, PackAnalysisDetails.canister_id,
                                                 PackAnalysisDetails.device_id,
                                                 PackAnalysisDetails.quadrant,
                                                 PackAnalysisDetails.location_number).dicts() \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(*clauses, PackAnalysisDetails.canister_id << canister_list,
                   PackAnalysisDetails.location_number.is_null(False),
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)

        for record in pack_analysis_list:
            affected_packs.add(record['pack_id'])
            pack_analysis_id_set.add(record['id'])
            canister_location_dict[record["canister_id"]] = {'device_id': record["device_id"],
                                                             'quadrant': record["quadrant"],
                                                             'location_number': record["location_number"]}

            if record['pack_id'] not in pack_analysis_id_dict.keys():
                pack_analysis_id_dict[record['pack_id']] = set()
                pack_canister_dict[record['pack_id']] = set()
            pack_analysis_id_dict[record['pack_id']].add(record['id'])
            pack_canister_dict[record['pack_id']].add(record['canister_id'])

        logger.info("In db_skip_canister_for_packs: pack_analysis_ids: {}, affected_packs: {}, pack_analysis_id_dict: {}"
                    .format(pack_analysis_id_set, affected_packs, pack_analysis_id_dict))

        if not affected_packs:
            logger.info('In db_skip_canister_for_packs No_packs_found_while_skipping_for_batch_for_canister: ' + str(canister_list))
            return True, None

        robot_analysis_ids: set = set()
        robot_pack_canister_dict = dict()
        non_robot_analysis_ids: set = set()
        non_robot_pack_canister_dict = dict()
        robot_packs: set = set()
        if len(affected_packs):
            remaining_analysis_ids = PackAnalysis.select(fn.GROUP_CONCAT(
                                                             PackAnalysis.id).coerce(
                                                             False).alias('analysis_id'),
                                                         PackAnalysis.pack_id,
                                                         fn.GROUP_CONCAT(
                                                             PackAnalysisDetails.location_number).coerce(
                                                             False).alias('location_number'),
                                                         fn.GROUP_CONCAT(PackAnalysisDetails.canister_id).coerce(
                                                             False).alias('canister_id'),
                                                         fn.GROUP_CONCAT(fn.DISTINCT(fn.CONCAT(PackAnalysisDetails.canister_id, "-", PackAnalysisDetails.device_id, "-", PackAnalysisDetails.quadrant, "-", PackAnalysisDetails.location_number))).alias('can_destination')) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(*clauses, PackAnalysis.pack_id << list(affected_packs),
                       PackAnalysisDetails.canister_id.not_in(canister_list),
                       PackAnalysisDetails.location_number.is_null(False),
                       PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED) \
                .group_by(PackAnalysis.pack_id)

            for record in remaining_analysis_ids.dicts():
                if record['canister_id'] and record['location_number']:
                    canister_id = list(record['canister_id'].split(","))
                    location_number = list(record['location_number'].split(","))
                    analysis_ids = list(record['analysis_id'].split(","))
                    can_destination_list = list(record["can_destination"].split(","))
                    d = {}
                    d = {i.split("-", 1)[0]: {"device_id": i.split("-")[1], "quadrant": i.split("-")[2],
                                              "location_number": i.split("-")[3]} for i in can_destination_list}
                    canister_location_dict.update(d)

                    if not any(canister_id) is False and not any(location_number) is False:
                        robot_packs.add(record['pack_id'])
                        if record['pack_id'] in filling_pending_pack_ids:
                            non_robot_analysis_ids.update(analysis_ids)
                            if not non_robot_pack_canister_dict.get(record["pack_id"]):
                                non_robot_pack_canister_dict[record["pack_id"]] = set()
                            non_robot_pack_canister_dict[record["pack_id"]].update(canister_id)
                        else:
                            robot_analysis_ids.update(analysis_ids)
                            if not robot_pack_canister_dict.get(record["pack_id"]):
                                robot_pack_canister_dict[record["pack_id"]] = set()
                            robot_pack_canister_dict[record["pack_id"]].update(canister_id)

        manual_pack_list = list(affected_packs - robot_packs)
        logger.info("In db_skip_canister_for_packs: manual pack list {}, robot_packs: {},non_robot_analysis_ids: {}, robot_analysis_ids: {}".
                    format(manual_pack_list, robot_packs, non_robot_analysis_ids, robot_analysis_ids))

        if len(manual_pack_list):
            for current_in_progress_pack in filling_pending_pack_ids:
                if current_in_progress_pack in manual_pack_list:
                    if current_in_progress_pack in pack_analysis_id_dict.keys():
                        logger.info("db_skip_canister_for_packs current progress pack {}".format(current_in_progress_pack))
                        non_robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        if not non_robot_pack_canister_dict.get(current_in_progress_pack):
                            non_robot_pack_canister_dict[current_in_progress_pack] = set()
                        non_robot_pack_canister_dict[current_in_progress_pack].update(
                            pack_canister_dict[current_in_progress_pack])
                    else:
                        robot_analysis_ids.update(pack_analysis_id_dict[current_in_progress_pack])
                        if not robot_pack_canister_dict.get(current_in_progress_pack):
                            robot_pack_canister_dict[current_in_progress_pack] = set()
                        robot_pack_canister_dict[current_in_progress_pack].update(
                            pack_canister_dict[current_in_progress_pack])
                    manual_pack_list.remove(current_in_progress_pack)


            logger.info("In db_skip_canister_for_packs: for manual_pack_list: manual pack list {}, robot_packs: {},non_robot_analysis_ids: {}, robot_analysis_ids: {}".
                format(manual_pack_list, robot_packs, non_robot_analysis_ids, robot_analysis_ids))

            if manual_pack_list:
                mfd_pack_list = get_mfd_packs_from_given_pack_list_pack_queue(pack_list=manual_pack_list)
                logger.info("In db_skip_canister_for_packs mfd pack list {}".format(mfd_pack_list))

                if len(mfd_pack_list):
                    for pack in mfd_pack_list:
                        non_robot_analysis_ids.update(pack_analysis_id_dict[pack])
                        if not non_robot_pack_canister_dict.get(pack):
                            non_robot_pack_canister_dict[pack] = set()
                        non_robot_pack_canister_dict[pack].update(pack_canister_dict[pack])
                    manual_pack_list = list(set(manual_pack_list) - set(mfd_pack_list))
                logger.info("In db_skip_canister_for_packs manual_pack_list {}".format(manual_pack_list))

                if len(manual_pack_list):
                    return False, manual_pack_list

        insert_list = []
        if non_robot_analysis_ids or robot_analysis_ids:
            analysis_ids = list(non_robot_analysis_ids) + list(robot_analysis_ids)
            insert_list = get_insert_list_of_replenish_skipped_canister(analysis_ids, canister_list)
            logger.info(f"In db_skip_canister_for_packs, insert_list: {insert_list}")

        with db.transaction():
            if len(non_robot_analysis_ids):
                logger.info("In db_skip_canister_for_packs non_robot_analysis_ids {}".format(non_robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None
                #                }
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in non_robot_pack_canister_dict.items() for can in canisters]
                # insert_status = ReplenishSkippedCanister.insert_many(insert_list).execute()

                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}

                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(non_robot_analysis_ids))
                logger.info("In db_skip_canister_for_packs: pack_analysis_status: {} for non_robot_analysis_ids: {}".format(
                    status, non_robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(non_robot_analysis_ids)

            if len(robot_analysis_ids):
                logger.info("In db_skip_canister_for_packs robot_analysis_ids {}".format(robot_analysis_ids))
                # update_dict = {'location_number': None,
                #                'canister_id': None,
                #                'quadrant': None,
                #                'drop_number': None,
                #                'config_id': None
                #                }
                # insert_list = [{"pack_id": pack, "canister_id": can,
                #                 "location_number": canister_location_dict.get(can, {}).get("location_number"),
                #                 "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                #                 "device_id": canister_location_dict.get(can, {}).get("device_id")}
                #                for pack, canisters
                #                in robot_pack_canister_dict.items() for can in canisters]
                # insert_status = ReplenishSkippedCanister.insert_many(insert_list).execute()

                update_dict = {'status': constants.REPLENISH_CANISTER_TRANSFER_SKIPPED}

                status = PackAnalysisDetails.db_update_analysis_by_canister_ids(update_dict=update_dict,
                                                                                canister_ids=canister_list,
                                                                                analysis_ids=list(robot_analysis_ids))
                logger.info("In db_skip_canister_for_packs: pack_analysis_status: {} for robot_analysis_ids: {}".format(
                    status, robot_analysis_ids))
                delete_reserved_canister_analysis_id.extend(robot_analysis_ids)

            if insert_list:
                status = ReplenishSkippedCanister.insert_many(insert_list).execute()
                logger.info(f"In db_skip_canister_for_packs, insert status: {status}")

            if delete_reserved_canister_analysis_id:
                status = delete_reserved_canister_for_skipped_canister(canister_list=canister_list, analysis_id=delete_reserved_canister_analysis_id)
                logger.info("In db_skip_canister_for_packs: reserved canister: {} deleted:{}".format(canister_list, status))

            BatchChangeTracker.db_save(batch_id=batch_id,
                                       user_id=user_id,
                                       action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.SKIP_FOR_PACKS],
                                       params={"canister_list": canister_list,
                                               "batch_id": batch_id,
                                               "pack_count": pack_count,
                                               "device_id": device_id,
                                               "user_id": user_id,
                                               "packs_to_skip": packs_to_skip},
                                       packs_affected=list(affected_packs)
                                       )

            return True, list(affected_packs)

    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_skip_canister_for_packs: {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in db_skip_canister_for_packs: {}".format(e))
        raise e


@log_args_and_response
def insert_data_in_replenish_skipped_canister(canister_location_dict, pack_canister_dict):
    try:
        status = None
        insert_list = [{"pack_id": pack, "canister_id": can,
                        "location_number": canister_location_dict.get(can, {}).get("location_number"),
                        "quadrant": canister_location_dict.get(can, {}).get("quadrant"),
                        "device_id": canister_location_dict.get(can, {}).get("device_id")}
                       for pack, canisters
                       in pack_canister_dict.items() for can in canisters]
        if insert_list:
            status = ReplenishSkippedCanister.insert_many(insert_list).execute()

        return status
    except Exception as e:
        logger.info(f'Error in insert_data_in_replenish_skipped_canister, e: {e}')
        raise e

@log_args_and_response
def get_insert_list_of_replenish_skipped_canister(analysis_ids, canister_list):
    try:
        insert_list = []
        if analysis_ids and canister_list:
            query = PackAnalysisDetails.select(PackAnalysis.pack_id, PackAnalysisDetails.canister_id,
                                               PackAnalysisDetails.location_number,
                                               PackAnalysisDetails.quadrant,
                                               PackAnalysisDetails.device_id).dicts() \
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .where(PackAnalysis.id.in_(analysis_ids),
                       PackAnalysisDetails.canister_id.in_(canister_list)) \
                .group_by(PackAnalysis.pack_id, PackAnalysisDetails.canister_id)

            insert_list = list(query)

        return insert_list
    except Exception as e:
        logger.info(f"Error in get_insert_list_of_replenish_skipped_canister, e: {e}")
