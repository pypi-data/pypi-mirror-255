import datetime
import functools
import operator
import os
import sys
from builtins import int
from collections import defaultdict
from typing import List

from dateutil.relativedelta import relativedelta
from peewee import InternalError, IntegrityError, DataError, DoesNotExist, JOIN_LEFT_OUTER, fn, Clause, SQL
from playhouse.shortcuts import cast

import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, fn_shorten_drugname_v2, log_args
from dosepack.validation.validate import validate
from migrations.migration_for_zone_implementation_in_canister_master import CanisterZoneMapping
from src import constants
from src.api_utility import get_filters, get_orders, apply_paginate, get_multi_search, \
    get_results
from src.cloud_storage import blob_exists, drug_master_dir, drug_dimension_dir, copy_blob, bucket_name, drug_bucket_name
from src.dao.csr_dao import db_get_locations_count_of_device
from src.service.drug_search import get_ndc_list_for_barcode, get_multi_search_with_drug_scan
from src.model.model_alternate_drug_option import AlternateDrugOption
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_history import CanisterHistory
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_disabled_location_history import DisabledLocationHistory
from src.model.model_doctor_master import DoctorMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_tracker import DrugTracker
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_missing_drug_pack import MissingDrugPack
from src.model.model_new_fill_drug import NewFillDrug
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_pack_details import PackDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_store_separate_drug import StoreSeparateDrug
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_status import DrugStatus
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_zone_master import ZoneMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_location_master import LocationMaster
from src.model.model_partially_filled_pack import PartiallyFilledPack
from src.model.model_device_master import DeviceMaster
from dosepack.error_handling.error_handler import error, create_response
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


def fetch_canister_drug_data_from_canister_ids(canister_ids: list, device_id: int, device_type_id: int):
    """

    @param device_type_id:
    @param device_id:
    @param canister_ids:
    @return:
    """
    try:
        canister_details_for_drug = "|"
        canister_list = canister_ids.split(",") if canister_ids else None
        if canister_list:
            # get all canister data for drug from list of canister
            drug_info_list = fetch_drug_info_from_canister_list(canister_ids=canister_list, device_id=device_id, device_type_id=device_type_id)
            # join all data with |
            canister_details_for_drug = canister_details_for_drug.join(drug_info_list)
            return canister_details_for_drug
        else:
            return None

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("Error in fetch_canister_drug_data_from_canister_ids {}".format(e))
        raise

    except Exception as e:
        logger.error("Error in fetch_canister_drug_data_from_canister_ids {}".format(e))
        return None


def fetch_drug_info_from_canister_list(canister_ids: list, device_id: int, device_type_id: int):
    """
    @param device_type_id:
    @param device_id:
    @param canister_ids:
    @rtype: object
    """
    CanisterAlias = CanisterMaster.alias()
    robot_device_canister_drug_info = list()
    csr_device_canister_drug_info = list()
    cart_device_canister_drug_info = list()

    robot_canister_drug_info = list()
    csr_canister_drug_info = list()
    cart_canister_drug_info = list()
    on_shelf_cart_canister_drug_info = list()

    robot_device_id_list = list()
    csr_device_id_list = list()
    cart_device_id_list = list()

    inactive_robot_device_canister_drug_info = list()
    inactive_csr_device_canister_drug_info = list()
    inactive_cart_device_canister_drug_info = list()

    inactive_robot_canister_drug_info = list()
    inactive_csr_canister_drug_info = list()
    inactive_cart_canister_drug_info = list()
    inactive_on_shelf_cart_canister_drug_info = list()

    all_canister_data = list()
    try:
        select_fields = [fn.IF(DeviceMaster.name.is_null(True), 'N.A.',
                               DeviceMaster.name).alias(
            'name'),
            fn.IF(DeviceMaster.name.is_null(True), 'null',
                  LocationMaster.display_location).alias('location_number'),
            CanisterMaster.id,
            CanisterMaster.available_quantity,
            fn.IF(CanisterMaster.active.is_null(True), '0',
                  CanisterMaster.active).alias('active'),
            fn.IF(DeviceMaster.name.is_null(True), 'null',
                  DeviceTypeMaster.id).alias(
                'device_name'),
            fn.IF(ContainerMaster.ip_address.is_null(True), 'null',
                  ContainerMaster.ip_address).alias('ip_address'),
            fn.IF(DeviceMaster.system_id.is_null(True), 'null',
                  DeviceMaster.system_id).alias('system_id'),
            fn.IF(DeviceMaster.serial_number.is_null(True), 'null',
                  DeviceMaster.serial_number).alias('device_serial_number'),
            CanisterAlias.select(
                fn.CONCAT(fn.GROUP_CONCAT(
                    Clause(
                        fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id),
                        SQL(" SEPARATOR ' & ' "))).coerce(False), ',',
                          fn.GROUP_CONCAT(
                              Clause(fn.IF(ZoneMaster.name.is_null(True), 'null',
                                           ZoneMaster.name),
                                     SQL(" SEPARATOR ' & ' "))).coerce(
                              False))).dicts()
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER,
                      on=(CanisterZoneMapping.canister_id == CanisterAlias.id))
                .join(ZoneMaster, JOIN_LEFT_OUTER,
                      ZoneMaster.id == CanisterZoneMapping.zone_id)
                .where(CanisterAlias.id == CanisterMaster.id)
                .group_by(CanisterMaster.id)
                .order_by(ZoneMaster.id, ZoneMaster.name).alias('zone_data'),

            fn.IF(ContainerMaster.drawer_name.is_null(True), 'null',
                  ContainerMaster.drawer_name).alias('drawer_name'),
            fn.IF(ContainerMaster.secondary_ip_address.is_null(True), 'null',
                  ContainerMaster.secondary_ip_address).alias('secondary_ip'),
            fn.IF(ContainerMaster.serial_number.is_null(True), 'null',
                  ContainerMaster.serial_number).alias('serial_number'),
            fn.IF(ContainerMaster.shelf.is_null(True), 'null',
                  ContainerMaster.shelf).alias('self'),
            CodeMaster.value,
            DeviceTypeMaster.id.alias('device_type_id'),
            DeviceMaster.id.alias('device_id')
        ]

        query = DrugMaster.select(*select_fields).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=(DrugMaster.id == CanisterMaster.drug_id)) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=(CodeMaster.id == CanisterMaster.canister_type)) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER,
                  on=(CanisterZoneMapping.canister_id == CanisterMaster.id)) \
            .where(CanisterMaster.id.in_(canister_ids))

        # device_type_id = int()
        # check if API call from device_id and device_id in args then sort data based on device id
        if device_id:
            # device_type_id_query = DeviceMaster.select(DeviceMaster.device_type_id).dicts().where(
            #     DeviceMaster.id == device_id)
            # # find device_type_id for device_id
            # for data in device_type_id_query:
            #     device_type_id = data['device_type_id']

            # find all device_id for device_type_id
            device_id_list_query = DeviceMaster.select(DeviceMaster.id, DeviceMaster.device_type_id).dicts() \
                .where(DeviceMaster.device_type_id == device_type_id)

            # create list of device_id from device_type_id
            for data in device_id_list_query:
                if data['device_type_id'] == settings.DEVICE_TYPES['ROBOT']:
                    robot_device_id_list.append(data['id'])
                if data['device_type_id'] == settings.DEVICE_TYPES['CSR']:
                    csr_device_id_list.append(data['id'])
                if data['device_type_id'] == settings.DEVICE_TYPES['Canister Transfer Cart']:
                    cart_device_id_list.append(data['id'])
        else:
            # not a device_id in args then sort active > ROBOT > CSR > Canister Transfer Cart > Canister Cart w/ Elevator > on_shelf
            query = query.order_by(CanisterMaster.active.desc(), SQL('device_type_id is null'),
                                   SQL('Field(device_type_id, {},{},{},{})'.format(settings.DEVICE_TYPES['ROBOT'],
                                                                                   settings.DEVICE_TYPES['CSR'],
                                                                                   settings.DEVICE_TYPES[
                                                                                       'Canister Transfer Cart'],
                                                                                   settings.DEVICE_TYPES[
                                                                                       'Canister Cart w/ Elevator'])))

        for record in query:
            drug_info = ","
            # device_id = 3(ROBOT- 02) device_type_id =2 (ROBOT)
            if device_id:
                # check if status is active or not
                if record['active'] == '1':
                    #  check device_type_id(2) is robot
                    if record['device_type_id'] == settings.DEVICE_TYPES['ROBOT']:
                        #  check device_id(3) is ROBOT- 02
                        if record['device_id'] == int(device_id):
                            # create robot_device_canister_info(ROBOT- 02) list for device_id(3)
                            del record['device_id']
                            robot_device_str_durg_info = drug_info.join(map(str, list(record.values())))
                            robot_device_canister_drug_info.append(robot_device_str_durg_info)
                        else:
                            del record['device_id']
                            # create robot_canister_info list for other device_id(2 ROBOT- 01) whose device_type_id(2 ROBOT) is same as device_id's(3 ROBOT- 02) device_type_id(2 ROBOT)
                            robot_str_durg_info = drug_info.join(map(str, list(record.values())))
                            robot_canister_drug_info.append(robot_str_durg_info)

                    #  check device_type_id(1) is CSR
                    if record['device_type_id'] == settings.DEVICE_TYPES['CSR']:
                        if record['device_id'] == int(device_id):
                            del record['device_id']
                            csr_device_str_durg_info = drug_info.join(map(str, list(record.values())))
                            csr_device_canister_drug_info.append(csr_device_str_durg_info)
                        else:
                            del record['device_id']
                            csr_str_durg_info = drug_info.join(map(str, list(record.values())))
                            csr_canister_drug_info.append(csr_str_durg_info)

                    #  check device_type_id in device_type_id(9,10) is CART
                    if record['device_type_id'] in (settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                    settings.DEVICE_TYPES['Canister Cart w/ Elevator']):
                        if record['device_id'] == int(device_id):
                            # create csr_device_canister_info(CSR - 03) list for device_id of CSR
                            del record['device_id']
                            cart_device_str_durg_info = drug_info.join(map(str, list(record.values())))
                            cart_device_canister_drug_info.append(cart_device_str_durg_info)
                        else:
                            # create CSR_canister_info list for other CSR(CSR - 1,2,Elevator) whose device_type_id(9 CSR-1,2) is same as device_id's(28 CSR -3) device_type_id(9 CSR-3)
                            del record['device_id']
                            cart_str_durg_info = drug_info.join(map(str, list(record.values())))
                            cart_canister_drug_info.append(cart_str_durg_info)

                    #  check for the on_shelf canister , device_type_id is null or N.A or None
                    if record['device_type_id'] is None:
                        del record['device_id']
                        on_shelf_str_durg_info = drug_info.join(map(str, list(record.values())))
                        on_shelf_cart_canister_drug_info.append(on_shelf_str_durg_info)

                else:
                    # logic is same as active status
                    if record['device_type_id'] == settings.DEVICE_TYPES['ROBOT']:
                        if record['device_id'] == int(device_id):
                            del record['device_id']
                            inactive_robot_device_str_durg_info = drug_info.join(map(str, list(record.values())))
                            inactive_robot_device_canister_drug_info.append(inactive_robot_device_str_durg_info)
                        else:
                            del record['device_id']
                            inactive_robot_str_durg_info = drug_info.join(map(str, list(record.values())))
                            inactive_robot_canister_drug_info.append(inactive_robot_str_durg_info)
                    if record['device_type_id'] == settings.DEVICE_TYPES['CSR']:
                        if record['device_id'] == int(device_id):
                            del record['device_id']
                            inactive_csr_device_str_durg_info = drug_info.join(map(str, list(record.values())))
                            inactive_csr_device_canister_drug_info.append(inactive_csr_device_str_durg_info)
                        else:
                            del record['device_id']
                            inactive_csr_str_durg_info = drug_info.join(map(str, list(record.values())))
                            inactive_csr_canister_drug_info.append(inactive_csr_str_durg_info)
                    if record['device_type_id'] in (settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                    settings.DEVICE_TYPES['Canister Cart w/ Elevator']):
                        if record['device_id'] == int(device_id):
                            del record['device_id']
                            inactive_cart_device_str_durg_info = drug_info.join(map(str, list(record.values())))
                            inactive_cart_device_canister_drug_info.append(inactive_cart_device_str_durg_info)
                        else:
                            del record['device_id']
                            inactive_cart_str_durg_info = drug_info.join(map(str, list(record.values())))
                            inactive_cart_canister_drug_info.append(inactive_cart_str_durg_info)

                    if record['device_type_id'] is None:
                        del record['device_id']
                        inactive_on_shelf_str_durg_info = drug_info.join(map(str, list(record.values())))
                        inactive_on_shelf_cart_canister_drug_info.append(inactive_on_shelf_str_durg_info)

            else:
                # device_id is not in args then join all data
                del record['device_type_id']
                # del record['device_id']
                str_durg_info = drug_info.join(map(str, list(record.values())))
                all_canister_data.append(str_durg_info)

        # join all the list based on device_id > device_type_id
        if device_id and int(device_id) in robot_device_id_list:
            # Active(sort based on ROBOT_03 device_id(3) > ROBOT_03 device_type_id(2) > CSR > CART > ON_Shelf ) > inactive(sort based on ROBOT_03 device_id(3) > ROBOT_03 device_type_id(2) > CSR > CART > ON_Shelf)
            all_canister_data = robot_device_canister_drug_info + robot_canister_drug_info + csr_canister_drug_info + cart_canister_drug_info + on_shelf_cart_canister_drug_info +\
                                inactive_robot_device_canister_drug_info + inactive_robot_canister_drug_info + inactive_csr_canister_drug_info + inactive_cart_canister_drug_info + inactive_on_shelf_cart_canister_drug_info
        if device_id and int(device_id) in csr_device_id_list:
            # Active(sort based on CSR device_id(1) > CSR device_type_id(1) > ROBOT > CART > ON_Shelf ) > inactive(sort based on CSR device_id(1) > CSR device_type_id(1) > ROBOT > CART > ON_Shelf)
            all_canister_data = csr_device_canister_drug_info + csr_canister_drug_info + robot_canister_drug_info + cart_canister_drug_info + on_shelf_cart_canister_drug_info +\
                                inactive_csr_device_canister_drug_info + inactive_csr_canister_drug_info + inactive_robot_canister_drug_info + inactive_cart_canister_drug_info + inactive_on_shelf_cart_canister_drug_info
        if device_id and int(device_id) in cart_device_id_list:
            # Active(sort based on cart device_id(25) > CART device_type_id(9) > ROBOT > CSR > ON_Shelf ) > inactive(sort based on CART device_id(25) > CART device_type_id(8) > ROBOT > CART > ON_Shelf)
            all_canister_data = cart_device_canister_drug_info + cart_canister_drug_info + robot_canister_drug_info + csr_canister_drug_info + on_shelf_cart_canister_drug_info +\
                                inactive_cart_device_canister_drug_info + inactive_cart_canister_drug_info + inactive_robot_canister_drug_info + inactive_csr_canister_drug_info + inactive_on_shelf_cart_canister_drug_info

        return all_canister_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in fetch_drug_info_from_canister_list".format(e))
        raise
    except Exception as e:
        logger.error("Error in fetch_drug_info_from_canister_list".format(e))
        return None


def get_drug_details_by_ndc(ndc: int) -> list:
    """
    1. Displays current drug and drug dimension related details
    @param ndc
    @return record: current drug and drug dimension related details of particular drug
    """
    drug_details = list()
    clauses = list()
    clauses.append((DrugMaster.ndc == ndc))
    try:
        query = DrugMaster.select(DrugMaster.ndc.alias('ndc'),
                                  DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                  DrugMaster.drug_name,
                                  DrugMaster.strength,
                                  DrugMaster.strength_value,
                                  DrugDimension.width,
                                  DrugDimension.length,
                                  DrugDimension.depth,
                                  DrugDimension.fillet,
                                  CustomDrugShape.name.alias('custom_shape')
                                  ).dicts() \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id) \
            .group_by(DrugMaster.concated_fndc_txr_field())
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        for record in query:
            drug_details.append(record)
        return drug_details
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_drug_details_by_ndc".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_drug_details_by_ndc".format(e))
        raise e


@log_args_and_response
def fetch_drug_info(drug_id, company_id, ndc):
    """
        @param company_id:
        @param drug_id: int
        @return:
        """
    results = list()
    inventory_data = list()
    query = DrugMaster.select(DrugMaster.id,
                              DrugMaster.drug_name,
                              DrugMaster.ndc,
                              DrugMaster.formatted_ndc,
                              DrugMaster.txr,
                              DrugMaster.strength,
                              DrugMaster.brand_flag,
                              DrugMaster.strength_value,
                              DrugMaster.imprint,
                              DrugMaster.image_name,
                              DrugMaster.color,
                              DrugMaster.shape,
                              DrugMaster.manufacturer,
                              DrugMaster.upc,
                              DrugMaster.dispense_qty,
                              DrugMaster.package_size,
                              DrugStatus.ext_status,
                              DrugStatus.ext_status_updated_date,
                              DrugStatus.last_billed_date,
                              fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr).alias('fndc_txr'),
                              DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug'),
                              # fn.CONCAT(PackHistory.new_value).alias('value'),
                              # fn.CONCAT(PackHistory.action_date_time).alias('action_date_time'),
                              # fn.CONCAT(PackHistory.action_taken_by).alias('action_taken_by'),
                              fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                    DrugStockHistory.is_in_stock).alias("is_in_stock"),
                              fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                    DrugStockHistory.created_by).alias('last_seen_with')) \
        .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
        .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                              fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                             (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
        .join(DrugStockHistory, JOIN_LEFT_OUTER,
              on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) & (DrugStockHistory.is_active == 1) &
                  (DrugStockHistory.company_id == company_id))) \
        .where(DrugMaster.id == drug_id) \
        .group_by(DrugMaster.id) \
        .order_by(DrugStatus.ext_status.desc(),
                  DrugStatus.last_billed_date.desc())

    inventory_data = get_current_inventory_data(ndc_list=[int(ndc)], qty_greater_than_zero=False)
    inventory_quantity = None
    for record in inventory_data:
        inventory_quantity = record['quantity']

    try:
        for record in query.dicts():
            record['inventory_quantity'] = inventory_quantity
            if record['inventory_quantity']:
                record['is_in_stock'] = 0 if inventory_quantity == 0 else 1
            else:
                record['is_in_stock'] = None
            results.append(record)
        return results
    except (InternalError, IntegrityError) as e:
        logger.error("Error in fetch_drug_info".format(e))
        raise e


@log_args_and_response
def db_get_drugs_volume(fndc_txr_list):
    """
    Takes list of fndc txr tuples in list and returns drug dimension data if available
    :param fndc_txr_list:
    :return:
    """
    try:
        results = dict()
        if fndc_txr_list:
            fndc_txr_list = list('{}#{}'.format(item[0], item[1] or '') for item in fndc_txr_list)
            fndc_concat_field = fn.CONCAT(UniqueDrug.formatted_ndc, '#', fn.IFNULL(UniqueDrug.txr, ''))
            query = DrugDimension.select(UniqueDrug, DrugDimension)\
                .join(UniqueDrug, on=UniqueDrug.id == DrugDimension.unique_drug_id)\
                .where(fndc_concat_field << fndc_txr_list)
            for record in query.dicts():
                results[record['formatted_ndc'], record['txr']] = record
        return results
    except (IntegrityError, InternalError) as e:
        logger.error("Error in db_get_drugs_volume".format(e))
        raise


@log_args_and_response
def get_drug_id_from_ndc(ndc: str, pharmacy_drug=False) -> List[int]:
    """
    This function fetches the drug_id for the given ndc.
    @param ndc:
    @return:
    """
    try:
        drug_id_list: list = list()
        query = DrugMaster.get_drugs_details_by_ndclist(ndc_list=[ndc])
        for record in query:
            if pharmacy_drug:
                drug_id_list.append(record["pharmacy_drug_id"])
            else:
                drug_id_list.append(record["drug_id"])
        return drug_id_list

    except DoesNotExist as e:
        logger.error("error in get_drug_id_from_ndc {}".format(e))
        return []
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_drug_id_from_ndc {}".format(e))
        raise e


@log_args_and_response
def get_drug_data_from_ndc(ndc):
    """
    This function fetches the drug_id for the given ndc.
    @param ndc:
    @return:
    """
    try:
        response = DrugMaster.get_drugs_details_by_ndclist(ndc_list=ndc)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_drug_data_from_ndc".format(e))
        raise
    except Exception as e:
        logger.error("Error in get_drug_data_from_ndc".format(e))
        raise


@log_args_and_response
def db_get_by_id(drug_id, dicts=False):
    try:
        drug = DrugMaster.select(DrugStatus.ext_status,
                                 DrugMaster)\
            .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id)\
            .where(DrugMaster.id == drug_id)
        if dicts:
            drug = drug.dicts()
        return drug.get()
    except (DoesNotExist, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_by_id".format(e))
        raise


@log_args_and_response
def db_create_new_fill_drug_dao(drug, company_id):
    try:
        NewFillDrug.db_create_new_fill_drug(drug, company_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_create_new_fill_drug_dao".format(e))
        raise


@log_args_and_response
def db_get_unique_drug_lower_level_by_drug(drug_id):
    try:
        query = DrugMaster.select(UniqueDrug.lower_level).dicts() \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (DrugMaster.txr == UniqueDrug.txr))) \
            .where(DrugMaster.id == drug_id)
        return query.get().lower_level
    except (DoesNotExist, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_unique_drug_lower_level_by_drug".format(e))
        raise


@log_args_and_response
def db_get_drug_txr_fndc_id_dao(drug_id):
    try:
        return DrugMaster.db_get_drug_txr_fndc_id(drug_id=drug_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_drug_txr_fndc_id_dao".format(e))
        raise


@log_args_and_response
def db_create_unique_drug_dao(drug_master_data):
    try:
        return UniqueDrug.db_create_unique_drug(drug_master_data)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_create_unique_drug_dao".format(e))
        raise


@log_args_and_response
def db_get_custom_drug_shape_name(req_name):
    try:
        return CustomDrugShape.db_get_by_name(req_name)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_custom_drug_shape_name".format(e))
        raise


@log_args_and_response
def db_get_drug_dimension_id_by_unique_drug(unique_drug_id):
    try:
        query = DrugDimension.db_get_drug_dimension_info(unique_drug_id)
        return query.get()
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_drug_dimension_id_by_unique_drug".format(e))
        raise


@log_args_and_response
def db_get_drug_from_unique_drug_dao(canister_data):
    try:
        return UniqueDrug.db_get_drug_from_unique_drug(canister_data=canister_data)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_drug_from_unique_drug_dao".format(e))
        raise


@log_args_and_response
def db_get_unique_drug_by_drug_id(drug_id):
    try:
        unique_drug_id = DrugMaster.select(UniqueDrug.id).dicts() \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(DrugMaster.id == drug_id)
        return unique_drug_id
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_unique_drug_by_drug_id".format(e))
        raise


@log_args_and_response
def get_drug_info(drug, unique_drugs=False, limit=None):
    """
    Returns list of drugs matching using filter
    @param unique_drugs:
    @param drug: drug name or ndc
    :param unique_drugs: bool to indicate whether to select only unique drugs
    @param limit:
    """
    drug_info = []
    if not drug:
        return None
    drug_name_field = fn.CONCAT(
        DrugMaster.drug_name, " ",
        DrugMaster.strength_value, " ",
        DrugMaster.strength, " ",
        "(", DrugMaster.ndc, ")"
    )
    select_fields = [
        DrugMaster.id.alias('drug_id'),
        DrugMaster.drug_name.alias('display_name'),
        DrugMaster.ndc,
        DrugMaster.strength_value,
        DrugMaster.strength,
        DrugMaster.image_name,
        DrugMaster.formatted_ndc,
        DrugMaster.txr,
        DrugMaster.color,
        DrugMaster.shape,
        DrugMaster.manufacturer,
        drug_name_field.alias('drug_name')
    ]
    if unique_drugs:  # if unique drugs then select unique_drug_id
        select_fields.append(UniqueDrug.id.alias('unique_drug_id'))

    candidate_ndcs, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode({"scanned_ndc": drug, "required_entity": "ndc"})

    drug = drug.translate(str.maketrans({'%': r'\%'}))  # escape % from search string
    drugsearch = "%" + drug + "%"

    # generate query
    query = DrugMaster.select(*select_fields).dicts()
    if unique_drugs:
        query = query.join(UniqueDrug, on=DrugMaster.id == UniqueDrug.drug_id)
    if candidate_ndcs:
        query = query.where((drug_name_field ** drugsearch)
                            | (DrugMaster.ndc ** drugsearch)
                            | (DrugMaster.ndc << candidate_ndcs))
    else:
        query = query.where((drug_name_field ** drugsearch) | (DrugMaster.ndc ** drugsearch))
    query = query.order_by(DrugMaster.drug_name, DrugMaster.strength_value)
    if limit:  # apply limit on records if available
        query = query.limit(limit)
    try:
        for record in query:
            if record["ndc"]:
                record["countblacklist"] = 0
                drug_info.append(record)

        return drug_info

    except DoesNotExist as ex:
        logger.error("Error in get_drug_info".format(ex))
        return error(1004)
    except InternalError as e:
        logger.error("Error in get_drug_info".format(e))
        return error(2001)


@log_args_and_response
def get_unique_drugs_by_formatted_ndc_txr(formatted_ndc, txr):
    try:
        drug_data = []
        query = DrugMaster.select(DrugMaster.id, DrugMaster.strength, DrugMaster.strength_value,
                                  UniqueDrug.id.alias('unique_drug_id'),
                                  DrugMaster.drug_name, UniqueDrug.drug_id, UniqueDrug.formatted_ndc) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(
            DrugMaster.formatted_ndc == formatted_ndc,
            DrugMaster.txr == txr
        )
        for record in query.dicts():
            drug_data.append(record)
        return drug_data
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_unique_drugs_by_formatted_ndc_txr".format(e))
        raise


def get_drawer_level_data_dao(container_id_list: list, filter_fields: dict) -> list:
    fields_dict = {"drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
                   "canister_id": CanisterMaster.id,
                   "canister_type": UniqueDrug.drug_usage,
                   "canister_size": CanisterMaster.canister_type,
                   "ndc": DrugMaster.ndc,
                   "display_locations": LocationMaster.display_location
                   }
    exact_search_list = ['canister_type', 'canister_id']
    like_search_list = ['drug_name']
    membership_search_list = ['canister_size', "display_locations"]
    try:
        if filter_fields and "ndc" in filter_fields:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'],
                 "required_entity": "ndc"})
            if ndc_list:
                filter_fields["ndc"] = ndc_list
                membership_search_list.append('ndc')
            else:
                like_search_list.append('ndc')
        clauses = [(ContainerMaster.id << container_id_list)]

        if filter_fields:
            clauses = get_filters(clauses, fields_dict, filter_fields,
                                  exact_search_fields=exact_search_list,
                                  like_search_fields=like_search_list,
                                  membership_search_fields=membership_search_list)

            if "multi_search" in filter_fields and filter_fields:
                string_search_field = [
                    DrugMaster.concated_drug_name_field(include_ndc=True),
                    DrugMaster.ndc
                ]
                multi_search_fields = filter_fields['multi_search'].split(',')
                logger.info("model_search_fields {}".format(string_search_field))

                clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_fields,
                                                          model_search_fields=string_search_field,
                                                          ndc_search_field=DrugMaster.ndc)
                logger.info("clauses {}".format(clauses))

        query = ContainerMaster.select(ContainerMaster.drawer_name,
                                       LocationMaster.id.alias("location_id"),
                                       LocationMaster.display_location,
                                       LocationMaster.is_disabled.alias("disabled_location"),
                                       CanisterMaster.id.alias("canister_id"),
                                       CanisterMaster.available_quantity.alias("quantity"),
                                       CanisterMaster.rfid.alias("electronic_id"),
                                       DrugMaster.ndc,
                                       UniqueDrug.drug_usage.alias('canister_type'),
                                       DrugMaster.concated_drug_name_field(include_ndc=False).alias("drug_name")) \
            .dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DrugMaster, JOIN_LEFT_OUTER, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                                   (DrugMaster.txr == UniqueDrug.txr)))

        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        logger.info(query)

        return list(query)
    except (IntegrityError, InternalError)as e:
        logger.error("Error in get_drawer_level_data_dao".format(e))
        raise


def get_csr_drawer_level_data_dao(device_id: int, filter_fields: dict, sort_fields: list, paginate: dict) -> list:
    fields_dict = {
        "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
        "canister_id": CanisterMaster.id,
        "shelf": ContainerMaster.shelf,
        "drawer_type": ContainerMaster.drawer_usage,
        "drawer_name": ContainerMaster.drawer_name,
        "drawer_size": ContainerMaster.drawer_type,
        "canister_type": UniqueDrug.drug_usage,
        "canister_size": CanisterMaster.canister_type,
        "ndc": DrugMaster.ndc
    }
    exact_search_list = ['drawer_type', 'canister_type', 'canister_id']
    like_search_list = ['drug_name']
    membership_search_list = ['drawer_size', 'shelf', 'canister_size', 'drawer_name']
    try:
        if filter_fields and "ndc" in filter_fields:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id,  upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'],
                 "required_entity": "ndc"})
            if ndc_list:
                filter_fields["ndc"] = ndc_list
                membership_search_list.append('ndc')
            else:
                like_search_list.append('ndc')
        clauses = [(ContainerMaster.device_id == device_id)]

        if filter_fields:
            clauses = get_filters(clauses, fields_dict, filter_fields,
                                  exact_search_fields=exact_search_list,
                                  like_search_fields=like_search_list,
                                  membership_search_fields=membership_search_list)

            if "multi_search" in filter_fields and filter_fields:
                string_search_field = [
                    DrugMaster.concated_drug_name_field(include_ndc=True),
                    DrugMaster.ndc
                ]
                multi_search_fields = filter_fields['multi_search'].split(',')
                logger.info("model_search_fields {}".format(string_search_field))

                clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_fields,
                                                          model_search_fields=string_search_field,
                                                          ndc_search_field=DrugMaster.ndc)
                logger.info("clauses {}".format(clauses))
        order_list = [ContainerMaster.shelf, ContainerMaster.drawer_level]
        if sort_fields:
            order_list = get_orders(order_list, fields_dict, sort_fields)

        query = ContainerMaster.select(ContainerMaster.id,
                                       ContainerMaster.device_id,
                                       ContainerMaster.drawer_name,
                                       ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address,
                                       ContainerMaster.mac_address,
                                       ContainerMaster.secondary_mac_address,
                                       ContainerMaster.drawer_level,
                                       ContainerMaster.drawer_usage.alias('drawer_type'),
                                       ContainerMaster.drawer_type.alias('drawer_size'),
                                       ContainerMaster.shelf,
                                       ContainerMaster.serial_number,
                                       ).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, LocationMaster.container_id == ContainerMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, LocationMaster.id == CanisterMaster.location_id) \
            .join(DrugMaster, JOIN_LEFT_OUTER, DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .group_by(ContainerMaster.id)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        logger.info(query)

        if order_list:
            query = query.order_by(*order_list)

        if paginate:
            query = apply_paginate(query, paginate)
        return list(query)
    except (DoesNotExist, DataError, IntegrityError, InternalError) as e:
        logger.error("Error in get_csr_drawer_level_data_dao".format(e))
        raise


def get_ndc_list_for_data_matrix(scanned_value: int) -> list:
    """
    returns ndc list when data matrix is scanned in multi-search

    """
    try:
        ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
            {"scanned_ndc": scanned_value, "required_entity": "ndc"})
        return ndc_list

    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in get_ndc_list_for_data_matrix".format(e))
        raise IntegrityError


def get_csr_location_level_data_dao(device_id: int, filter_fields: dict, sort_fields: dict, paginate: dict) -> dict:

    fields_dict = {
        "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
        "ndc": DrugMaster.ndc,
        "canister_id": CanisterMaster.id,
        "shelf": ContainerMaster.shelf,
        "drawer_level": ContainerMaster.drawer_level,
        "drawer_type": ContainerMaster.drawer_usage,
        "drawer_name": ContainerMaster.drawer_name,
        "drawer_size": ContainerMaster.drawer_type,
        "canister_type": UniqueDrug.drug_usage,
        "canister_size": CanisterMaster.canister_type,
        "location_number": cast(fn.Substr(LocationMaster.display_location,
                                          fn.instr(LocationMaster.display_location, '-') + 1), 'SIGNED'),
        "quantity": CanisterMaster.available_quantity,
        "drawer_initial": cast(
            fn.Substr(ContainerMaster.drawer_name, 1, fn.instr(ContainerMaster.drawer_name, '-') - 1), 'CHAR'),
        "drawer_number": cast(
            fn.Substr(ContainerMaster.drawer_name, fn.instr(ContainerMaster.drawer_name, '-') + 1), 'SIGNED'),
        "disabled": LocationMaster.is_disabled,
        "empty_location": CanisterMaster.id.is_null(True)  # This field is for sorting on empty location i.e.,
        # null canister_id data should be at end for this default order should be - sort_fields = [["empty_location",1]]
    }

    clauses = [(ContainerMaster.device_id == device_id)]
    exact_search_list = ['drawer_type', 'canister_type']
    like_search_list = ['canister_id', 'location_number', 'drug_name', 'ndc']
    membership_search_list = ['drawer_size', 'shelf', 'drawer_name', 'canister_size']

    try:
        if filter_fields and "ndc" in filter_fields:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'],
                 "required_entity": "ndc"})
            if ndc_list:
                filter_fields["ndc"] = ndc_list
                membership_search_list.append('ndc')
            else:
                like_search_list.append('ndc')

        if filter_fields is not None and "location_type" in filter_fields:
            if filter_fields["location_type"] == constants.LOCATION_TYPE["ACTIVE"]:
                clauses.append((LocationMaster.is_disabled == False))
            elif filter_fields["location_type"] == constants.LOCATION_TYPE["DISABLED"]:
                clauses.append((LocationMaster.is_disabled == True))
            if filter_fields["location_type"] == constants.LOCATION_TYPE["EMPTY"]:
                clauses.append((CanisterMaster.id.is_null(True)))

        if filter_fields:
            clauses = get_filters(clauses, fields_dict, filter_fields,
                                  exact_search_fields=exact_search_list,
                                  like_search_fields=like_search_list,
                                  membership_search_fields=membership_search_list)

            if "multi_search" in filter_fields is not None:
                string_search_field = [
                    DrugMaster.ndc,
                    CanisterMaster.id,
                    DrugMaster.concated_drug_name_field()
                ]
                multi_search_fields = filter_fields['multi_search'].split(',')
                logger.info("string_search_field".format(string_search_field))

                clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_fields,
                                                          model_search_fields=string_search_field,
                                                          ndc_search_field=DrugMaster.ndc)
        order_list = list()
        if sort_fields:
            order_list = get_orders(order_list, fields_dict, sort_fields)

        sub_query_reason = DisabledLocationHistory.select(
            fn.MAX(DisabledLocationHistory.id).alias('max_disable_loc_id'),
            DisabledLocationHistory.loc_id.alias('loc_id')).group_by(DisabledLocationHistory.loc_id).alias(
            'sub_query_reason')

        query = ContainerMaster.select(ContainerMaster.id.alias('drawer_id'),
                                       ContainerMaster.shelf,
                                       ContainerMaster.drawer_level,
                                       ContainerMaster.drawer_type.alias('drawer_size'),
                                       ContainerMaster.drawer_usage.alias('drawer_type'),
                                       ContainerMaster.drawer_name,
                                       ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address,
                                       ContainerMaster.mac_address,
                                       ContainerMaster.secondary_mac_address,
                                       ContainerMaster.serial_number,
                                       LocationMaster.id.alias('location_id'),
                                       LocationMaster.location_number,
                                       LocationMaster.display_location,
                                       LocationMaster.is_disabled,
                                       CanisterMaster.id.alias('canister_id'),
                                       UniqueDrug.drug_usage.alias('canister_type'),
                                       CanisterMaster.canister_type.alias('canister_size'),
                                       fn.IF(CanisterMaster.available_quantity < 0, 0,
                                             CanisterMaster.available_quantity).alias('display_quantity'),
                                       DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                       DrugMaster.image_name,
                                       DrugMaster.ndc,
                                       DrugMaster.color,
                                       DrugMaster.imprint,
                                       CustomDrugShape.name.alias('shape'),
                                       DrugDetails.last_seen_date,
                                       fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                             DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                       fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                             DrugDetails.last_seen_by).alias('last_seen_with'),
                                       fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                             DrugDetails.last_seen_date).alias('last_seen_on'),
                                       fn.IF(LocationMaster.is_disabled == settings.is_location_active, None,
                                             DisabledLocationHistory.comment
                                             ).alias('reason_disable_loc')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, LocationMaster.container_id == ContainerMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, LocationMaster.id == CanisterMaster.location_id) \
            .join(DrugMaster, JOIN_LEFT_OUTER, DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, ((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                 (DrugDetails.company_id == CanisterMaster.company_id))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, DrugDimension.shape == CustomDrugShape.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                      (DrugStockHistory.is_active == True) &
                                                      (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(sub_query_reason, JOIN_LEFT_OUTER, on=(sub_query_reason.c.loc_id == LocationMaster.id)) \
            .join(DisabledLocationHistory, JOIN_LEFT_OUTER,
                  on=DisabledLocationHistory.id == sub_query_reason.c.max_disable_loc_id) \

        logger.info(query)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))

        if order_list:
            query = query.order_by(*order_list)
        response = {}
        # to count total,empty and disabled locations
        location_id_list = []
        for record in query:
            location_id_list.append(record["location_id"])
        if location_id_list:
            locations_count_dict = db_get_locations_count_of_device(location_id_list=location_id_list,
                                                                    disabled_locations=True, empty_locations=True,
                                                                    active_locations=False)
            response["total_locations_count"] = len(location_id_list)
            response["empty_locations_count"] = locations_count_dict.get("empty_locations_count")
            response["disabled_locations_count"] = locations_count_dict.get("disabled_locations_count")
        else:
            response["total_locations_count"] = 0
            response["empty_locations_count"] = 0
            response["disabled_locations_count"] = 0
        if paginate:
            query = apply_paginate(query, paginate)
        logger.info(list(query))
        response["drawers_data"] = list(query)
        return response
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_csr_location_level_data_dao".format(e))
        raise e


@log_args_and_response
def db_get_canisters_v2(company_id, filter_fields, sort_fields, paginate, replenish_canister_flag):
    """
    returns canister data for given company_id
    :param company_id: int
    :param filter_fields: dict  Examples: filters= {"robot_id":null}
    :param sort_fields: list  Examples: sort_fields= [["available_quantity",1],["canister_number",1]]
    :param paginate: int
    :param replenish_canister_flag: int
    :return:
    """
    fields_dict = {
        "imprint": fn.replace(fn.replace(DrugMaster.imprint, ' ', ''), '<>', ''),
        "location_number": CanisterMaster.location_id,
        "drug_name": DrugMaster.concated_drug_name_field(),
        "ndc": DrugMaster.formatted_ndc,
        "rfid": CanisterMaster.rfid,
        "available_quantity": CanisterMaster.available_quantity,
        "formatted_ndc": DrugMaster.formatted_ndc,
        "txr": DrugMaster.txr,
        "canister_id": CanisterMaster.id,
        "canister_type": CanisterMaster.canister_type,
        "canister_type_name": CodeMaster.value,
        "is_label_printed": fn.IF(CanisterMaster.label_print_time.is_null(True), False, True),
        'formatted_location': fn.IF(LocationMaster.display_location.is_null(False),
                                    LocationMaster.get_formatted_location(), None),
        'drawer_number': cast(
            fn.Substr(ContainerMaster.drawer_name, fn.instr(ContainerMaster.drawer_name, '-') + 1), 'SIGNED'),
        'device_id': fn.IF(DeviceMaster.id.is_null(True), -1, DeviceMaster.id),
        'device_name': DeviceMaster.name,
        'canister_location': fn.IF(CanisterMaster.location_id.is_null(True), -1,
                                   LocationMaster.get_device_location()),
        'drawer_initial': cast(
            fn.Substr(ContainerMaster.drawer_name, 1, fn.instr(ContainerMaster.drawer_name, '-') - 1), 'CHAR'),
        'device_type': DeviceMaster.device_type_id,
        'display_location': fn.IF(LocationMaster.display_location.is_null(False), LocationMaster.display_location,
                                  None),
        'zone_id': fn.IF(ZoneMaster.id.is_null(True), None, ZoneMaster.id),
        'zone_name': fn.IF(ZoneMaster.name.is_null(True), None, ZoneMaster.name),
        'system_id': DeviceMaster.system_id,
        'drawer_id': LocationMaster.display_location,
        'location_id': LocationMaster.display_location,
        'display_quantity': fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity),
        'canister_active': CanisterMaster.active

    }
    exact_search_list = ['canister_location', 'formatted_ndc', 'txr', 'is_label_printed', 'canister_active',
                         'location_number']
    like_search_list = ['rfid', 'drug_name', 'display_location', 'zone_name', 'canister_id', 'drawer_id',
                        "canister_type_name", "imprint"]
    membership_search_list = ['device_id', 'zone_id', 'system_id']
    left_like_search_fields = ['container_id']
    right_like_search_fields = ['location_id']

    clauses = list()
    clauses.append((CanisterMaster.company_id == company_id))
    clauses.append((CanisterMaster.rfid.is_null(False)))
    if filter_fields.get("expiry_status") == 0:
        clauses.append((CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(settings.TIME_DELTA_FOR_EXPIRED_CANISTER)))
    # clauses.append((CanisterMaster.active == settings.is_canister_active))
    if filter_fields and 'available_quantity' in filter_fields and filter_fields['available_quantity'] is not None:

        if not filter_fields['available_quantity'].isdigit() or int(filter_fields['available_quantity']) < 0:
            result = []
            return result, 0
        elif int(filter_fields['available_quantity']) == 0:
            clauses.append((CanisterMaster.available_quantity <= int(filter_fields['available_quantity'])))
        else:
            exact_search_list.append('available_quantity')

    order_list = list()
    # not passing robot_id and csr_id in search as we require or operation on them
    if filter_fields and filter_fields.get('display_location', None):
        if filter_fields['display_location'] == '-':
            filter_fields['display_location'] = ' '

    if replenish_canister_flag:
        if filter_fields and 'canister_id' in filter_fields and filter_fields['canister_id'] is not None:
            clauses.append(CanisterMaster.id == filter_fields['canister_id'])

    if "ndc" in filter_fields and filter_fields["ndc"]:
        ndcs = []
        fielter_ndc = filter_fields["ndc"].split(",")
        for ndc in fielter_ndc:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": ndc,
                 "required_entity": "ndc"})
            if ndc_list:
                formatted_ndc_list = list(map(lambda x: x[:9], ndc_list))
                # filter_fields["ndc"] = formatted_ndc_list
                ndcs.extend(formatted_ndc_list)
                if "ndc" not in membership_search_list:
                    membership_search_list.append('ndc')
            else:
                ndcs.append(ndc)
                # filter_fields["ndc"] = filter_fields["ndc"][:9]
                if "ndc" not in like_search_list:
                    like_search_list.append('ndc')
                    filter_fields["ndc"] = ndc
        if "ndc" in membership_search_list:
            filter_fields["ndc"] = list(set(ndcs))

    if "imprint" in filter_fields and filter_fields["imprint"]:
        imprint = filter_fields["imprint"]
        if imprint != '<>':
            filter_fields['imprint'] = "".join([x for x in imprint.split() if x != '<>'])

    clauses = get_filters(clauses, fields_dict, filter_fields,
                          exact_search_fields=exact_search_list,
                          like_search_fields=like_search_list,
                          membership_search_fields=membership_search_list,
                          left_like_search_fields=left_like_search_fields,
                          right_like_search_fields=right_like_search_fields)

    # In model_search_fields, all field must be CharField
    string_search_field = [
        DrugMaster.concated_drug_name_field(),
        DrugMaster.strength,
        DrugMaster.strength_value,
        DrugMaster.color,
        DrugMaster.shape,
        DrugMaster.ndc,
        DrugMaster.formatted_ndc,
        DrugMaster.txr,
        CanisterMaster.id,
        CodeMaster.value,
    ]
    if filter_fields and filter_fields.get('multi_search', None) is not None:
        multi_search_fields = filter_fields['multi_search'].split(',')

        clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_fields,
                                                  model_search_fields=string_search_field,
                                                  ndc_search_field=DrugMaster.ndc)

    if filter_fields and filter_fields.get('id_or_rfid_search') is not None:
        canister_multi_search = [CanisterMaster.id, CanisterMaster.rfid]
        id_rfid_search_fields = filter_fields['id_or_rfid_search'].split(',')
        clauses = get_multi_search(clauses=clauses,
                                   multi_search_values=id_rfid_search_fields,
                                   model_search_fields=canister_multi_search)

    order_list = get_orders(order_list, fields_dict, sort_fields)

    # Apart from the regular sorting requested from the FrontEnd,
    # we need to consider the sort with Active status followed by Canister ID
    order_list.insert(0, CanisterMaster.active.desc())  # To provide active canister always on top
    order_list.append(CanisterMaster.id)  # To provide same order for grouped data

    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    CanisterHistoryAlias = CanisterHistory.alias()

    sub_query = CanisterHistoryAlias.select(fn.MAX(CanisterHistoryAlias.id).alias('max_canister_history_id'),
                                            CanisterHistoryAlias.canister_id.alias('canister_id')) \
        .group_by(CanisterHistoryAlias.canister_id).alias('sub_query')

    try:
        query = CanisterMaster.select(
            fields_dict['canister_id'].alias('canister_id'),
            fn.IF(
                CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                constants.EXPIRED_CANISTER,
                fn.IF(
                    CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                    constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            CanisterMaster.company_id,
            CanisterMaster.expiry_date,
            CanisterMaster.canister_type,
            CodeMaster.value.alias('canister_type_name'),
            CanisterMaster.rfid,
            CanisterMaster.label_print_time,
            fn.IF(CanisterMaster.label_print_time.is_null(True), False, True).alias('is_label_printed'),
            CanisterMaster.available_quantity,
            fields_dict['display_quantity'].alias('display_quantity'),
            LocationMaster.location_number,
            CanisterMaster.drug_id,
            DrugMaster.strength, DrugMaster.image_name,
            UniqueDrug.is_powder_pill,
            DrugMaster.strength_value,
            DrugMaster.ndc, DrugMaster.imprint,
            DrugMaster.color, DrugMaster.shape,
            DrugMaster.formatted_ndc, DrugMaster.txr,
            DrugStatus.ext_status,
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                'stock_updated_by'),
            DrugDetails.last_seen_by.alias('last_seen_with'),
            DrugDetails.last_seen_date.alias('last_seen_date'),
            CanisterMaster.reorder_quantity,
            CanisterMaster.barcode,
            fields_dict['canister_active'].alias('canister_active'),
            # CanisterMaster.active.alias('canister_Active'),
            fields_dict['drug_name'].alias("drug_name"),
            ContainerMaster.drawer_name.alias('drawer_number'),
            LocationMaster.display_location,
            LocationMaster.is_disabled.alias('is_location_disabled'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True),
                                                     'null', ZoneMaster.id)),
                                   SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True),
                                                     'null', ZoneMaster.name)), SQL(" SEPARATOR ' & ' "))).coerce(
                False).alias('zone_name'),
            DeviceLayoutDetails.id.alias('device_layout_id'),
            DeviceMaster.name.alias('device_name'),
            DeviceMaster.id.alias('device_id'),
            DeviceMaster.serial_number,
            DeviceTypeMaster.device_type_name,
            DeviceTypeMaster.id.alias('device_type_id'),
            ContainerMaster.ip_address,
            ContainerMaster.secondary_ip_address,
            DeviceMaster.system_id,
            fn.IF(CanisterHistory.previous_location_id.is_null(True), None, CanisterHistory.created_date).alias(
                'last_seen_time'),
            DeviceMasterAlias.name.alias('previous_device_name'),
            LocationMasterAlias.id.alias('previous_location_id'),
            LocationMasterAlias.display_location.alias('previous_display_location'),
            fields_dict['formatted_location'].coerce(False).alias('formatted_location'),
            fields_dict['canister_location'].alias('canister_location'),
            ContainerMaster.id.alias('container_id'),
            ContainerMaster.serial_number.alias("drawer_serial_number"),
            ContainerMaster.shelf
        ).dicts() \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStatus, JOIN_LEFT_OUTER, on=DrugStatus.drug_id == DrugMaster.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == CanisterMaster.company_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(CodeMaster, on=CodeMaster.id == CanisterMaster.canister_type) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.canister_id == CanisterMaster.id)) \
            .join(CanisterHistory, JOIN_LEFT_OUTER, on=(CanisterHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=(CanisterHistory.previous_location_id == LocationMasterAlias.id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=(LocationMasterAlias.device_id == DeviceMasterAlias.id))
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        query = query.group_by(CanisterMaster.id) \
            .order_by(CanisterHistory.created_date.desc())
        if order_list:
            query = query.order_by(*order_list)

        results, count, non_paginate_records = get_results(query,
                                                           fields_dict,
                                                           paginate=paginate,
                                                           non_paginate_result_field_list=["canister_type"])
        ndc_list = []
        for data in results:
            ndc_list.append(int(data['ndc']))
            if data["expiry_date"]:
                data["expiry_date"] = data["expiry_date"].strftime("%Y-%m")

        return results, count, non_paginate_records, ndc_list
    except InternalError as e:
        logger.error("Error in db_get_canisters_v2".format(e))
        raise InternalError


@log_args_and_response
def db_get_expired_drug_history(company_id, filter_fields, sort_fields, paginate):
    try:
        logger.info(f'In db_get_expired_drug_history')

        clauses = []
        clauses.append((CanisterTracker.usage_consideration == constants.USAGE_CONSIDERATION_DISCARD))
        clauses.append((CanisterTracker.qty_update_type_id == constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD))

        fields_dict = {
            "imprint": fn.replace(fn.replace(DrugMaster.imprint, ' ', ''), '<>', ''),
            "drug_name": DrugMaster.concated_drug_name_field(),
            "ndc": DrugMaster.formatted_ndc,
            "formatted_ndc": DrugMaster.formatted_ndc,
            "txr": DrugMaster.txr,
            "canister_id": CanisterMaster.id,
            'created_date': fn.DATE(CanisterTracker.created_date),
            'discard_qty': CanisterTracker.quantity_adjusted
        }
        like_search_fields = ['drug_name', 'txr', 'ndc', 'formatted_ndc']
        query = CanisterTracker.select(CanisterTracker.canister_id,
                                       (fn.FLOOR(CanisterTracker.quantity_adjusted) * (-1)).alias("trashed_qty"),
                                       CanisterTracker.expiration_date,
                                       fn.DATE(CanisterTracker.created_date).alias("discarded_date"),
                                       CanisterTracker.lot_number,
                                       DrugMaster.concated_drug_name_field(include_ndc=True).alias("drug_name"),
                                       DrugMaster.manufacturer).dicts() \
                .join(CanisterMaster, on=CanisterMaster.id == CanisterTracker.canister_id) \
                .join(DrugMaster, on=DrugMaster.id == CanisterTracker.drug_id) \


        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        # query = query.group_by(CanisterMaster.id) \
        #     .order_by(CanisterHistory.created_date.desc())

        order_list = []
        order_list = get_orders(order_list, fields_dict, sort_fields)
        if order_list:
            query = query.order_by(*order_list)

        string_search_field = [
            DrugMaster.concated_drug_name_field(),
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.formatted_ndc,
            DrugMaster.txr,
            CanisterMaster.id
        ]

        between_search_fields = ['created_date']

        if filter_fields and filter_fields.get('multi_search', None) is not None:
            multi_search_fields = filter_fields['multi_search'].split(',')

            clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_fields,
                                                      model_search_fields=string_search_field,ndc_search_field=None)

        results, count = get_results(query.dicts(), fields_dict,
                                     filter_fields=filter_fields,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     clauses=clauses,
                                     between_search_list=between_search_fields,
                                     identified_order=order_list,
                                     like_search_list = like_search_fields)
        return results, count
    except Exception as e:
        logger.info(f'Error in db_get_expired_drug_history, e: {e}')
        raise e

@log_args_and_response
def get_custome_drug_shape_by_id(id: int):
    """
    get custome drug shape name by id
    """
    try:
        return CustomDrugShape.db_get_by_id(id=id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_custome_drug_shape_by_id:  {}".format(e))
        raise e


@log_args_and_response
def get_fndc_txr_by_unique_id_dao(unique_ids: list) -> list or None:
    """
    get fndc txr by unique drug id
    """
    try:
        return UniqueDrug.db_get_fndc_txr_by_unique_id(unique_ids=unique_ids)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_fndc_txr_by_unique_id_dao:  {}".format(e))
        raise e


@log_args_and_response
def get_drug_stock_by_status(company_id: int, filter_fields: dict) -> tuple:
    """
    Function to obtain drug list with status
    @return: dict
    """
    try:
        clauses = [PackDetails.company_id == company_id]

        like_search_list = ['drug_name', 'drug_name_ndc']
        exact_search_list = []
        between_search_list = []
        membership_search_list = ['is_in_stock', 'last_updated_by']
        order_list = [["drug_name", 1]]

        fields_dict = {
            'drug_name': DrugMaster.drug_name,
            'drug_name_ndc': DrugMaster.concated_drug_name_field(include_ndc=True),
            'ndc': DrugMaster.ndc,
            'is_in_stock': DrugStockHistory.is_in_stock,
            'last_seen_by': DrugDetails.last_seen_by,
            'last_updated_by': DrugStockHistory.created_by
        }

        # logic to add when a data matrix is scanned
        if "drug_name_ndc" in filter_fields and filter_fields["drug_name_ndc"]:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['drug_name_ndc'], "required_entity": "ndc"})
            if ndc_list:
                membership_search_list.append('ndc')
                filter_fields["ndc"] = ndc_list

        query = PackDetails.select(DrugMaster.id,
                                   DrugMaster.ndc,
                                   DrugMaster.drug_name,
                                   DrugMaster.strength_value,
                                   DrugMaster.strength,
                                   DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name_ndc'),
                                   fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                         DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                   DrugStockHistory.created_by.alias('last_updated_by'),
                                   DrugStockHistory.created_date.alias('last_updated_on'),
                                   DrugDetails.last_seen_date.alias('last_seen_on'),
                                   DrugDetails.last_seen_by,
                                   ).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) & (DrugStockHistory.is_active == True)
                      & (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .join(PartiallyFilledPack, JOIN_LEFT_OUTER, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                          clauses=clauses,
                                                          sort_fields=order_list,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          membership_search_list=membership_search_list,
                                                          non_paginate_result_field_list=['id'],
                                                          between_search_list=between_search_list,
                                                          )

        return results, count, non_paginate_result

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_drug_stock_by_status".format(e))
        raise
    except Exception as e:
        logger.error("Error in get_drug_stock_by_status".format(e))
        raise


@log_args_and_response
def db_get_unique_drugs(pack_id):
    """

    @param pack_id:
    @return:
    """
    slot_data = []
    try:
        for record in PackDetails.select(
                fn.SUM(SlotDetails.quantity).alias('total_qty'),
                DrugMaster.drug_name,
                DrugMaster.strength_value,
                DrugMaster.strength,
                DrugMaster.ndc,
                DrugMaster.image_name) \
                .order_by(DrugMaster.drug_name).dicts() \
                .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
                .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
                .where(PackDetails.id == pack_id) \
                .group_by(DrugMaster.id):
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
            record["total_qty"] = float(record["total_qty"])
            slot_data.append(record)
        return slot_data

    except IntegrityError as ex:
        logger.error("Error in db_get_unique_drugs".format(ex))
        raise IntegrityError
    except InternalError as e:
        logger.error("Error in db_get_unique_drugs".format(e))
        raise InternalError
    except Exception as e:
        logger.error("Error in db_get_unique_drugs".format(e))
        raise


@log_args_and_response
def get_label_drugs(pack_id, pack_status=None, **kwargs):
    label_drug_info_dict = dict()
    # label_drug_info = []
    txr_occurance_dict = {}
    total_quantity_dict, missing_drug_set = get_total_rx_quantity(pack_id, pack_status)
    try:
        DrugMasterAlias = DrugMaster.alias()
        DrugMasterAlias1 = DrugMaster.alias()
        query = PackRxLink.select(PatientRx.pharmacy_rx_no,
                                  PatientRx.sig,
                                  PatientRx.morning,
                                  PatientRx.noon,
                                  PatientRx.evening,
                                  PatientRx.bed,
                                  PatientRx.caution1,
                                  PatientRx.caution2,
                                  PatientRx.remaining_refill,
                                  PatientRx.is_tapered,
                                  fn.IF(DrugMasterAlias1.drug_name.is_null(True), DrugMaster.drug_name,
                                        DrugMasterAlias1.drug_name).alias("drug_name"),
                                  fn.IF(DrugMasterAlias1.ndc.is_null(True), DrugMaster.ndc,
                                        DrugMasterAlias1.ndc).alias("ndc"),
                                  fn.IF(DrugMasterAlias1.strength.is_null(True), DrugMaster.strength,
                                        DrugMasterAlias1.strength).alias("strength"),
                                  fn.IF(DrugMasterAlias1.strength_value.is_null(True), DrugMaster.strength_value,
                                        DrugMasterAlias1.strength_value).alias("strength_value"),
                                  fn.IF(DrugMasterAlias1.imprint.is_null(True), DrugMaster.imprint,
                                        DrugMasterAlias1.imprint).alias("imprint"),
                                  fn.IF(DrugMasterAlias1.color.is_null(True), DrugMaster.color,
                                        DrugMasterAlias1.color).alias("color"),
                                  fn.IF(DrugMasterAlias1.shape.is_null(True), DrugMaster.shape,
                                        DrugMasterAlias1.shape).alias("shape"),
                                  fn.IF(DrugMasterAlias1.manufacturer.is_null(True), DrugMaster.manufacturer,
                                        DrugMasterAlias1.manufacturer).alias("manufacturer"),
                                  fn.IF(DrugMasterAlias1.image_name.is_null(True), DrugMaster.image_name,
                                        DrugMasterAlias1.image_name).alias("image_name"),
                                  fn.IF(DrugMasterAlias1.brand_flag.is_null(True), DrugMaster.brand_flag,
                                        DrugMasterAlias1.brand_flag).alias("brand_flag"),
                                  fn.IF(DrugMasterAlias1.brand_drug.is_null(True), DrugMaster.brand_drug,
                                        DrugMasterAlias1.brand_drug).alias("brand_drug"),
                                  fn.IF(DrugMasterAlias1.generic_drug.is_null(True), DrugMaster.generic_drug,
                                        DrugMasterAlias1.generic_drug).alias("generic_drug"),
                                  fn.IF(DrugMasterAlias1.id.is_null(True), DrugMaster.formatted_ndc,
                                        DrugMasterAlias1.formatted_ndc).alias("formatted_ndc"),
                                  fn.IF(DrugMasterAlias1.id.is_null(True), DrugMaster.txr,
                                        DrugMasterAlias1.txr).alias("txr"),
                                  PackRxLink.id,
                                  DoctorMaster.last_name,
                                  DoctorMaster.first_name,
                                  DoctorMaster.workphone.alias('cellphone'),
                                  SlotDetails.drug_id,
                                  SlotDetails.original_drug_id,
                                  DrugMasterAlias.ndc.alias('original_drug_ndc'),
                                  PartiallyFilledPack.pack_rx_id,
                                  PartiallyFilledPack.missing_qty,
                                  fn.IF(PartiallyFilledPack.missing_qty, 1, 0).alias(
                                      'missing_flag'),
                                  DrugMasterAlias.formatted_ndc.alias("sd_fndc"),
                                  DrugMasterAlias.txr.alias("sd_txr")).dicts() \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(DrugMasterAlias, on=SlotDetails.original_drug_id == DrugMasterAlias.id) \
            .join(DoctorMaster, JOIN_LEFT_OUTER, on=DoctorMaster.id == PatientRx.doctor_id) \
            .join(PartiallyFilledPack, JOIN_LEFT_OUTER, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id) \
            .join(DrugMasterAlias1, JOIN_LEFT_OUTER, on=DrugMasterAlias1.id == DrugTracker.drug_id) \
            .where(PackRxLink.pack_id == pack_id).order_by(DrugMaster.drug_name, PatientRx.id).group_by(
            fn.IF(DrugMasterAlias1.id, DrugMasterAlias1.formatted_ndc, DrugMaster.formatted_ndc),
            fn.IF(DrugMasterAlias1.id, DrugMasterAlias1.txr, DrugMaster.txr), SlotDetails.pack_rx_id)

        for record in query:
            print(record)
            record["doctor_name"] = record["last_name"] + ", " + record["first_name"]
            record["remaining_refill"] = round(float(record["remaining_refill"]), 0)
            record["morning"] = float(record["morning"])
            record["noon"] = float(record["noon"])
            record["evening"] = float(record["evening"])
            record["bed"] = float(record["bed"])
            # record["print_qty"] = total_quantity_dict[record["pharmacy_rx_no"]]
            record["drug_type"] = ''
            record["sig"] = record["sig"].strip()
            record["caution1"] = record["caution1"].strip()
            record["caution2"] = record["caution2"].strip()

            drug_indication = settings.MISSING_DRUG_SYMBOL if record["missing_flag"] else ''
            record["drug_name"] = drug_indication + record["drug_name"] if record["drug_name"] else ''
            record["short_drug_name_v2"] = fn_shorten_drugname_v2(record["drug_name"], record["strength"],
                                                                  record["strength_value"], **kwargs)

            if record["caution1"] == settings.INVALID:
                record["caution1"] = None
            if record["caution2"] == settings.INVALID:
                record["caution2"] = None
            if not record['imprint']:
                record['imprint'] = ''
            if not record['image_name']:
                record['image_name'] = ''
            if not record['color']:
                record['color'] = ''
            if not record['shape']:
                record['shape'] = ''
            if not record['cellphone']:
                record['cellphone'] = ''
            else:
                record['cellphone'] = record["cellphone"] = "(" + record["cellphone"][0:3] + ") " \
                                                            + record["cellphone"][3:6] + "-" + record["cellphone"][
                                                                                               6:10]
            record["ndc_changed"] = 0
            for key, value in total_quantity_dict[record["pharmacy_rx_no"]].items():
                if record["formatted_ndc"] == key[0] and record["txr"] != key[1]:
                    record["ndc_changed"] = 1  # same drug with different ndc
                elif record["formatted_ndc"] != key[0]:
                    record["ndc_changed"] = 2   # alternate drug change flag
                    break
            #above condition will not execute if d1 required and user filled d2 completely -> now we are not updating slot_details.
            if record["ndc_changed"] == 0:
                print("************************")
                if record["ndc"] != record["original_drug_ndc"]:
                    if record["formatted_ndc"] != record["sd_fndc"]:
                        record["ndc_changed"] = 1
                    else:
                        record["ndc_changed"] = 2
            if not label_drug_info_dict.get((record["formatted_ndc"], record["txr"])):
                txr_occurance_dict[record["txr"]] = txr_occurance_dict.get(record["txr"], 0) + 1
                rx = record.pop("pharmacy_rx_no", None)
                record["rx_info"] = [
                    {"pharmacy_rx_no": rx, "print_qty": total_quantity_dict[rx].get((record["formatted_ndc"], record["txr"]), 0)}]
                label_drug_info_dict[(record["formatted_ndc"], record["txr"])] = record
                is_in_stock = True
                if pack_status == settings.PARTIALLY_FILLED_BY_ROBOT:
                    if (record["formatted_ndc"], record["txr"]) in missing_drug_set:
                        is_in_stock = False
                label_drug_info_dict[(record["formatted_ndc"], record["txr"])][
                    "is_in_stock"] = is_in_stock
            else:
                label_drug_info_dict[(record["formatted_ndc"], record["txr"])]["rx_info"].append({"pharmacy_rx_no": record["pharmacy_rx_no"], "print_qty": total_quantity_dict[record["pharmacy_rx_no"]].get((record["formatted_ndc"], record["txr"]), 0)})
                label_drug_info_dict[(record["formatted_ndc"], record["txr"])]["remaining_refill"] = record["remaining_refill"]
            # label_drug_info.append(record)
        srt_txr_occurance = sorted(txr_occurance_dict.keys(), key=lambda x: txr_occurance_dict[x], reverse=True)
        response = list(label_drug_info_dict.values())

        def custom_sort(item):
            return srt_txr_occurance.index(item["txr"])

        sorted_response = sorted(response, key=custom_sort)

        return sorted_response

    except DoesNotExist as e:
        logger.error("Error in get_label_drugs".format(e))
        return list(label_drug_info_dict.values())
    except InternalError as e:
        logger.error("Error in get_label_drugs".format(e))
        return list(label_drug_info_dict.values())
    except Exception as e:
        logger.error("Error in get_label_drugs".format(e))
        return list(label_drug_info_dict.values())


@log_args_and_response
def get_total_rx_quantity(pack_id, pack_status=None):
    total_quantity_info_drug_tracker = {}
    total_quantity_info_slot_details = {}
    qty_drug_dict = {}
    missing_drug_set = set()
    DrugMasterAlias = DrugMaster.alias()
    try:
        query1 = SlotDetails.select(PatientRx.pharmacy_rx_no,
                                    fn.IF(DrugMaster.id.is_null(True), DrugMasterAlias.id,
                                          DrugMaster.id).alias("drug_id"),
                                    fn.sum(fn.IF(SlotDetails.quantity, SlotDetails.quantity, 0)).alias('total_quantity'),
                                    fn.sum(fn.IF(DrugTracker.drug_quantity, DrugTracker.drug_quantity, 0)).alias(
                                        'total_filled_quantity'),
                                    fn.IF(DrugMaster.id.is_null(True), DrugMasterAlias.formatted_ndc,
                                          DrugMaster.formatted_ndc).alias("formatted_ndc"),
                                    fn.IF(DrugMaster.id.is_null(True), DrugMasterAlias.txr,
                                          DrugMaster.txr).alias("txr"),
                                    fn.IF(MissingDrugPack.id.is_null(True), False, True).alias('missing_drug')).dicts() \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugTracker, JOIN_LEFT_OUTER,
                  on=((DrugTracker.slot_id == SlotDetails.id) & (DrugTracker.is_overwrite == 0))) \
            .join(DrugMaster, JOIN_LEFT_OUTER, on=DrugMaster.id == DrugTracker.drug_id) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == SlotDetails.drug_id)    \
            .join(MissingDrugPack, JOIN_LEFT_OUTER, on=(PackRxLink.id == MissingDrugPack.pack_rx_id)) \
            .where(PackRxLink.pack_id == pack_id) \
            .group_by(fn.IF(DrugMaster.id, DrugMaster.formatted_ndc, DrugMasterAlias.formatted_ndc), fn.IF(DrugMaster.id, DrugMaster.txr, DrugMasterAlias.txr), SlotDetails.pack_rx_id)

        query2 = SlotDetails.select(PatientRx.pharmacy_rx_no,
                                    SlotDetails.drug_id,
                                    fn.sum(SlotDetails.quantity).alias('total_quantity'),
                                    # fn.sum(fn.IF(DrugTracker.drug_quantity, DrugTracker.drug_quantity, 0)).alias(
                                    #     'total_filled_quantity'),
                                    DrugMaster.formatted_ndc,
                                    DrugMaster.txr,
                                    fn.IF(MissingDrugPack.id.is_null(True), False, True).alias('missing_drug')).dicts() \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(MissingDrugPack, JOIN_LEFT_OUTER, on=(PackRxLink.id == MissingDrugPack.pack_rx_id)) \
            .where(PackRxLink.pack_id == pack_id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr, SlotDetails.pack_rx_id)

        for record in query1:
            if not qty_drug_dict.get(record['txr']):
                qty_drug_dict[(record['formatted_ndc'], record['txr'])] = {
                    "total_req_quantity": record["total_quantity"],
                    "total_filled_quantity": record["total_filled_quantity"]}
            else:
                qty_drug_dict[(record['formatted_ndc'], record['txr'])]["total_req_quantity"] += record[
                    "total_quantity"]
                qty_drug_dict[(record['formatted_ndc'], record['txr'])]["total_filled_quantity"] += record[
                    "total_filled_quantity"]
            if not total_quantity_info_drug_tracker.get(record["pharmacy_rx_no"]):

                total_quantity_info_drug_tracker[record["pharmacy_rx_no"]] = {(record["formatted_ndc"], record["txr"]):float(record["total_filled_quantity"])}
            else:
                total_quantity_info_drug_tracker[record["pharmacy_rx_no"]][(record["formatted_ndc"], record["txr"])] = float(record["total_filled_quantity"])
            #
            if record["missing_drug"]:
                missing_drug_set.add((record["formatted_ndc"], record["txr"]))
        for record2 in query2:
            if not total_quantity_info_slot_details.get(record2["pharmacy_rx_no"]):

                total_quantity_info_slot_details[record2["pharmacy_rx_no"]] = {(record2["formatted_ndc"], record2["txr"]):float(record2["total_quantity"])}
            else:
                total_quantity_info_slot_details[record2["pharmacy_rx_no"]][
                    (record2["formatted_ndc"], record2["txr"])] = float(record2["total_quantity"])

        pharmacy_rx_no_list = total_quantity_info_drug_tracker.keys()
        for pharmacy_rx in pharmacy_rx_no_list:
            if list(total_quantity_info_slot_details[pharmacy_rx].values())[0] > sum(
                    value for value in total_quantity_info_drug_tracker[pharmacy_rx].values()):
                if total_quantity_info_drug_tracker[pharmacy_rx].get(
                        list(total_quantity_info_slot_details[pharmacy_rx].keys())[0]):
                    total_quantity_info_drug_tracker[pharmacy_rx][
                        list(total_quantity_info_slot_details[pharmacy_rx].keys())[0]] += \
                        list(total_quantity_info_slot_details[pharmacy_rx].values())[0] - sum(
                            value for value in total_quantity_info_drug_tracker[pharmacy_rx].values())
                else:
                    total_quantity_info_drug_tracker[pharmacy_rx][
                        list(total_quantity_info_slot_details[pharmacy_rx].keys())[0]] = \
                        list(total_quantity_info_slot_details[pharmacy_rx].values())[0] - sum(
                            value for value in total_quantity_info_drug_tracker[pharmacy_rx].values())
            if list(total_quantity_info_slot_details[pharmacy_rx].values())[0] < sum(
                    value for value in total_quantity_info_drug_tracker[pharmacy_rx].values()):
                total_quantity_info_drug_tracker[pharmacy_rx][
                    list(total_quantity_info_slot_details[pharmacy_rx].keys())[0]] = \
                list(total_quantity_info_slot_details[pharmacy_rx].values())[0]

        logger.info(f"In get_total_rx_quantity, qty_drug_dict: {qty_drug_dict}")
        logger.info(f"In get_total_rx_quantity, missing_drug_set: {missing_drug_set}")
        if pack_status == settings.PARTIALLY_FILLED_BY_ROBOT:
            for drug, qty_dict in qty_drug_dict.items():
                if qty_dict["total_req_quantity"] != qty_dict["total_filled_quantity"]:
                    missing_drug_set.add(drug)

        return total_quantity_info_drug_tracker, missing_drug_set

    except DoesNotExist as e:
        logger.error("Error in get_total_rx_quantity".format(e))
        return total_quantity_info_drug_tracker, missing_drug_set
    except InternalError as e:
        logger.error("Error in get_total_rx_quantity".format(e))
        return total_quantity_info_drug_tracker, missing_drug_set


@log_args_and_response
def get_pending_facility_drug_data(unique_drug_ids: list) -> tuple:
    """
    Fetches all alt_option_ids for which batch id is not present and is in pending state (If batch ids are present
    then they are no longer on batch-scheduling screen and no need to update them)
    :param unique_drug_ids: list
    :return:
    """
    try:
        alternate_drug_option_list = list()
        company_ids = set()
        if unique_drug_ids:
            for unique_drug in unique_drug_ids:
                # getting only those ids for which source drug and alternate option both are the deactivated drug as
                # we do not want to deselect other options
                query = AlternateDrugOption.select(AlternateDrugOption.id.alias('alt_drug_opt_id'),
                                                   PackDetails.company_id).dicts() \
                    .join(PackDetails, on=PackDetails.facility_dis_id == AlternateDrugOption.facility_dis_id) \
                    .where(PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                           PackDetails.batch_id.is_null(True),
                           AlternateDrugOption.alternate_unique_drug_id == unique_drug,
                           AlternateDrugOption.unique_drug_id == unique_drug) \
                    .group_by(AlternateDrugOption.facility_dis_id)
                for record in query:
                    alternate_drug_option_list.append(record['alt_drug_opt_id'])
                    company_ids.add(record['company_id'])
            logger.info("pending_alternate_drug_option_ids {} and company_ids: {} for unique_drug_ids: {}".
                        format(alternate_drug_option_list, company_ids, unique_drug_ids))
            return alternate_drug_option_list, list(company_ids)
        else:
            logger.info("no_pending_alternate_drug_option_ids for unique_drug_ids: {}".format(unique_drug_ids))
            return [], []
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pending_facility_drug_data".format(e))
        raise e


@log_args_and_response
def get_active_alternate_drug_data(facility_distribution_id, company_id):
    try:
        alternate_drug_data = {}
        alternate_drug_ids = set()
        drug_alternate_drug_dict = {}
        sub_query_1 = AlternateDrugOption.select(AlternateDrugOption.unique_drug_id.alias('uid'),
                                                 fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias(
                                                     'original_fndc'),
                                                 DrugMaster.id.alias('original_drug_ids'),
                                                 AlternateDrugOption.alternate_unique_drug_id.alias('alternate_uid')
                                                 ) \
            .join(UniqueDrug, on=UniqueDrug.id == AlternateDrugOption.unique_drug_id) \
            .join(DrugMaster,
                  on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) & (DrugMaster.txr == UniqueDrug.txr))) \
            .where(AlternateDrugOption.facility_dis_id == facility_distribution_id,
                   AlternateDrugOption.active == 1,
                   AlternateDrugOption.unique_drug_id != AlternateDrugOption.alternate_unique_drug_id).alias('sub_q_1')

        sub_query_2 = CanisterMaster.select(CanisterMaster.id,
                                            DrugMaster.id.alias('drug_id'),
                                            DrugMaster.formatted_ndc.alias('formatted_ndc'),
                                            DrugMaster.txr.alias('txr')) \
            .join(DrugMaster, on=((DrugMaster.id == CanisterMaster.drug_id) & (CanisterMaster.active == 1) & (
                CanisterMaster.company_id == company_id))).alias('sub_q_2')

        query = UniqueDrug.select(sub_query_1.c.uid,
                                  sub_query_1.c.original_fndc,
                                  sub_query_1.c.original_drug_ids,
                                  sub_query_1.c.alternate_uid,
                                  fn.CONCAT(UniqueDrug.formatted_ndc, '##', UniqueDrug.txr).alias('alternate_fndc'),
                                  sub_query_2.c.drug_id.alias('alternate_drug_id')) \
            .join(sub_query_1, on=UniqueDrug.id == sub_query_1.c.alternate_uid) \
            .join(sub_query_2, on=((sub_query_2.c.formatted_ndc == UniqueDrug.formatted_ndc) & (
                sub_query_2.c.txr == UniqueDrug.txr))) \
            .group_by(sub_query_1.c.original_drug_ids, sub_query_2.c.drug_id)

        for record in query.dicts():
            if record['original_fndc'] not in drug_alternate_drug_dict:
                drug_alternate_drug_dict[record['original_fndc']] = set()
            drug_alternate_drug_dict[record['original_fndc']].add(record['alternate_fndc'])

            if record['uid'] not in alternate_drug_data:
                alternate_drug_data[record['uid']] = {}
            if 'drug_ids' not in alternate_drug_data[record['uid']]:
                alternate_drug_data[record['uid']]['drug_ids'] = set()
            alternate_drug_data[record['uid']]['fndc_txr'] = record['original_fndc']
            alternate_drug_data[record['uid']]['drug_ids'].add(record['original_drug_ids'])

            if 'alternate_drug_data' not in alternate_drug_data[record['uid']]:
                alternate_drug_data[record['uid']]['alternate_drug_data'] = {}
            if record['alternate_uid'] not in alternate_drug_data[record['uid']]['alternate_drug_data']:
                alternate_drug_data[record['uid']]['alternate_drug_data'][record['alternate_uid']] = {}
            if 'drug_ids' not in alternate_drug_data[record['uid']]['alternate_drug_data'][record['alternate_uid']]:
                alternate_drug_data[record['uid']]['alternate_drug_data'][record['alternate_uid']][
                    'drug_ids'] = set()
            alternate_drug_data[record['uid']]['alternate_drug_data'][record['alternate_uid']]['fndc_txr'] = record[
                'alternate_fndc']
            alternate_drug_data[record['uid']]['alternate_drug_data'][record['alternate_uid']]['drug_ids'].add(
                record['alternate_drug_id'])
            alternate_drug_ids.add(record['alternate_drug_id'])
        return alternate_drug_data, alternate_drug_ids, drug_alternate_drug_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_active_alternate_drug_data".format(e))
        raise e


@log_args
def remove_alternate_drug_by_id(info_dict):
    try:
        if not info_dict['alternate_drug_option_ids']:
            raise ValueError('alternate_drug_option_ids not found')
        status = AlternateDrugOption.update(active=False, modified_date=get_current_date_time(), modified_by=info_dict['user_id']) \
            .where(AlternateDrugOption.id << info_dict['alternate_drug_option_ids']).execute()
        logger.info("Alt_drug_option_ids {} deselected with status: {}".format(
            info_dict["alternate_drug_option_ids"], status))
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("Error in remove_alternate_drug_by_id".format(e))
        raise e


@log_args
def remove_redundant_alternate_drug_distribution_id(info_dict):
    try:
        status = AlternateDrugOption.update(active=False,
                            modified_date=get_current_date_time(),
                            modified_by=info_dict['user_id']) \
            .where(AlternateDrugOption.unique_drug_id.not_in(info_dict['unique_drug_ids']),
                   AlternateDrugOption.facility_dis_id == info_dict['facility_distribution_id']).execute()
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("Error in remove_redundant_alternate_drug_distribution_id".format(e))
        raise e


@log_args_and_response
def update_drug_status_dao(drug_id, is_in_stock, user_details, reason=None):
    """
    Update Drug status
    @param drug_id:
    @param is_in_stock:
    @param user_details:
    @param reason:
    @return: status

    Examples:
            >>> update_drug_status({"drug_id": 106940, "is_in_stock": 0, "user_id":10})
            "is_in_stock": 0 - to mark drug as out of stock
            "is_in_stock": 1 - to mark drug as  in stock
            "is_in_stock": 2 -  to mark drug as discontinue
    """
    update_inventory = True
    try:
        if reason == "":
            reason = None
        unique_drug_id = None
        with db.atomic():
            query = UniqueDrug.select(UniqueDrug.id).dicts() \
                .join(DrugMaster, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                      (UniqueDrug.txr == DrugMaster.txr))) \
                .where(DrugMaster.id == drug_id)

            for record in query:
                unique_drug_id = record["id"]
                break

            if not unique_drug_id:
                return error(1017), False
            # only check in out of stock case
            check_current_status = DrugStockHistory.select().dicts().where(
                DrugStockHistory.unique_drug_id == unique_drug_id,
                DrugStockHistory.company_id == user_details["company_id"], DrugStockHistory.is_active == True, DrugStockHistory.is_in_stock == is_in_stock)
            for record in check_current_status:
                update_inventory = False

            status = DrugStockHistory.update(is_active=False).where(
                DrugStockHistory.unique_drug_id == unique_drug_id,
                DrugStockHistory.company_id == user_details["company_id"]).execute()
            logger.info("Drug Stock History Update Result = {} for Unique Drug ID: {}.".format(status, unique_drug_id))

            DrugStockHistory.insert(**{"unique_drug_id": unique_drug_id, "is_in_stock": is_in_stock, "is_active": True,
                                       "created_by": user_details["id"], "company_id": user_details["company_id"],
                                       "created_date": datetime.datetime.now(), "reason": reason}).execute()

        drug = db_get_by_id(drug_id=drug_id, dicts=True)

        # update the unique drug last_seen_by and last_seen_time for DrugDetails
        formatted_ndc_txr_list = list()
        formatted_ndc_txr = str(drug["formatted_ndc"] + '_' + drug["txr"])
        formatted_ndc_txr_list.append(formatted_ndc_txr)
        # get the unique_drug_id for the provided fndc_txr
        unique_drug_id_dict = UniqueDrug.db_get_unique_drug_id(formatted_ndc_txr_list=formatted_ndc_txr_list)
        create_dict = {"unique_drug_id": unique_drug_id_dict[formatted_ndc_txr],
                       "company_id": user_details["company_id"]}
        update_dict = {"last_seen_by": user_details["id"],
                       "last_seen_date": get_current_date_time()}
        # update or creates new record in DrugDetails table
        logger.info("updating drug details with input {} and {}".format(create_dict, update_dict))
        DrugDetails.db_update_or_create(create_dict=create_dict, update_dict=update_dict)

        drug_name = " ".join((drug["drug_name"], drug["strength_value"], drug["strength"]))
        # if is_in_stock == 2:
        #     Notifications().send_with_username(0, settings.NOTIFICATION_MESSAGE_CODE_DICT["DRUG_DISCONTINUE"].format(
        #         drug_name, drug["ndc"]), flow='pfw,dp')
        # else:
        #     Notifications().send_with_username(0, settings.NOTIFICATION_MESSAGE_CODE_DICT["DRUG_STOCK_CHANGE"].format(
        #         drug_name, drug["ndc"], "in stock" if is_in_stock else "out of stock"), flow='pfw,dp')

        return status, update_inventory
    except Exception as e:
        logger.error("Error in update_drug_status_dao".format(e))
        raise e


@log_args_and_response
def get_drug_dao(company_id, canister_search, filters=None, paginate=None, sort_fields=None):
    """

    @param paginate:
    @param sort_fields:
    @param company_id:
    @param filters:
    @param canister_search:
    @return:
    """
    drug_result = []
    count = 0
    try:
        ndc_list = []
        clauses = list()
        DrugMasterAlias = DrugMaster.alias()
        CodeMasterAlias = CodeMaster.alias()
        fields_dict = {
            "imprint": fn.replace(fn.replace(DrugMaster.imprint, ' ', ''), '<>', ''),
            "drug_name": DrugMaster.drug_name,
            "drug_id": DrugMaster.id,
            "ndc": DrugMaster.ndc,
            "strength": DrugMaster.strength,
            "strength_value": DrugMaster.strength_value,
            "strength_strength_value": fn.CONCAT(DrugMaster.strength_value, ' ', DrugMaster.strength),
            "drug_fullname": fn.CONCAT(DrugMaster.drug_name, ' ', DrugMaster.strength_value,
                                       ' ', DrugMaster.strength),
            "manufacturer": DrugMaster.manufacturer,
            "canister_type_name": CodeMaster.value,
            "color": DrugMaster.color,
            "shape": DrugMaster.shape,
            "canister_id": CanisterMaster.id,
            "dosage_type_ids": DosageType.id,
            'drawer_initial': cast(
                fn.Substr(ContainerMaster.drawer_name, 1, fn.instr(ContainerMaster.drawer_name, '-') - 1), 'CHAR'),
            'device_type': DeviceMaster.device_type_id,
            'display_location': fn.IF(LocationMaster.display_location.is_null(False), LocationMaster.display_location,
                                      None),
            'drawer_number': cast(
                fn.Substr(ContainerMaster.drawer_name, fn.instr(ContainerMaster.drawer_name, '-') + 1),
                'SIGNED'),
            'device_name': DeviceMaster.name,
            'qty': CanisterMaster.available_quantity,
            'zone_id': fn.IF(ZoneMaster.id.is_null(True), None, ZoneMaster.id),
            'zone_name': fn.IF(ZoneMaster.name.is_null(True), None, ZoneMaster.name),
        }

        non_exact_search_list = ['imprint', 'drug_name', 'strength', 'strength_value', 'strength_strength_value',
                                 'drug_fullname', 'manufacturer', "canister_type_name", 'ndc', 'color', 'shape', 'canister_id']
        membership_search_list = ['dosage_type_ids']
        if "canister_id" in filters and filters["canister_id"]:
            canister_id = filters["canister_id"]
            if not canister_id.isnumeric():
                return error(1000, "The parameter canister_id search value should be numeric.")
        if "imprint" in filters and filters["imprint"]:
            imprint = filters["imprint"]
            if imprint != '<>':
                filters['imprint'] = "".join([x for x in imprint.split() if x != '<>'])

        clauses = get_filters(clauses, fields_dict, filter_dict=filters,
                              like_search_fields=non_exact_search_list,
                              membership_search_fields=membership_search_list)
        order_list = list()

        order_list = get_orders(order_list, fields_dict, sort_fields)
        order_list.append(DrugMaster.id)  # To provide same order for grouped data

        if canister_search:
            clauses.append((CanisterMaster.company_id == company_id))
            clauses.append((CanisterMaster.location_id.is_null(False)))
            clauses.append((DeviceMaster.id == settings.DEVICE_TYPES['ROBOT']))

        query = DrugMaster.select(
            DrugMaster.id.alias('drug_id'),
            UniqueDrug.id.alias('unique_drug_id'),
            UniqueDrug.unit_weight,
            DrugMaster.drug_name,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.imprint,
            DrugMaster.formatted_ndc,
            DrugMaster.txr,
            DrugMaster.manufacturer,
            DrugMaster.image_name,
            DrugMaster.color, DrugMaster.shape,
            DrugMaster.ndc, DrugMaster.brand_flag,
            DrugStatus,
            DosageType.id.alias('dosage_type_id'),
            DosageType.name.alias('dosage_type_name'),
            DosageType.code.alias('dosage_type_code'),
            fn.IF(DrugDimension.id.is_null(True), 'Registration Pending',
                  fn.IF(DrugDimension.verification_status_id == settings.VERIFICATION_PENDING_FOR_DRUG,
                        'Verification Pending', CodeMasterAlias.value)).alias('registration_status'),
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
            fn.GROUP_CONCAT(Clause(SQL('DISTINCT'), Clause(
                fn.CONCAT(fn.IF(DeviceMaster.name.is_null(True), 'N.A.', DeviceMaster.name), '-',
                          fn.IF(DeviceMaster.name.is_null(True), 'null', LocationMaster.display_location), ),
                SQL(" SEPARATOR ', ' ")))).coerce(False).alias('canister_list'),
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), None, DrugStockHistory.is_in_stock).alias(
                "is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                'stock_updated_by'),
            fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                  DrugDetails.last_seen_by).alias('last_seen_with'),
            fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                  DrugDetails.last_seen_date).alias('last_seen_on')).dicts() \
            .join(
            CanisterMaster,
            JOIN_LEFT_OUTER,
            on=(
                    (CanisterMaster.drug_id == DrugMaster.id) &
                    (CanisterMaster.company_id == company_id) &
                    (CanisterMaster.rfid.is_null(False))
            )
        ) \
            .join(DrugStatus, JOIN_LEFT_OUTER, on=DrugStatus.drug_id == DrugMaster.id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == CanisterMaster.canister_type) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                                  & (DrugMaster.txr == UniqueDrug.txr)) \
            .join(StoreSeparateDrug, JOIN_LEFT_OUTER, on=UniqueDrug.id == StoreSeparateDrug.unique_drug_id) \
            .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                      (DrugStockHistory.is_active == True) &
                                                      (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=(UniqueDrug.id == DrugDimension.unique_drug_id)) \
            .join(CodeMasterAlias, JOIN_LEFT_OUTER, on=DrugDimension.verification_status_id == CodeMasterAlias.id)

        if clauses:
            query = query.where(*clauses)
        query = query.group_by(DrugMaster.id) \
            .order_by(SQL('canister_ids').desc())

        if order_list:
            query = query.order_by(*order_list)
        count = query.count()

        if paginate:
            query = apply_paginate(query, paginate)
        drug_result = list(query)
        for record in drug_result:
            ndc_list.append(record['ndc'])

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

        return count, drug_result, ndc_list

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_drug_dao".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_drug_dao".format(e))
        return error(1036)


@log_args_and_response
def search_drug_field_dao(field, field_value, all_flag):
    try:
        results = list()
        clauses = list()
        try:
            if all_flag:
                clauses.append((DrugMaster._meta.fields[field] ** '%%'))
            else:  # for search using input
                for item in field_value.split():
                    item = escape_wildcard(item)
                    item = '%' + item + '%'
                    clauses.append((DrugMaster._meta.fields[field] ** item))
                    # builds peewee expression to filter using like
        except KeyError as e:
            logger.error("Wrong field name found. Field Name: {}".format(field))
            return error(1020)

        if clauses:
            for record in DrugMaster.select(
                    fn.DISTINCT(DrugMaster._meta.fields[field])
            ).dicts().where(functools.reduce(operator.and_, clauses)):
                results.append(record[field])
        if all_flag:
            results = sorted(results)
        return results

    except (IntegrityError, InternalError) as e:
        logger.error("Error in search_drug_field_dao".format(e))
        raise e
    except Exception as e:
        logger.error("Error in search_drug_field_dao".format(e))
        raise e


def escape_wildcard(_input):
    """
    Escapes % from string
    :param _input:
    :return: str
    """
    return _input.translate(str.maketrans({'%': r'\%'}))


def escape_wrap_wildcard(x):
    """
    Wraps wildcard(%) around given string after escaping wildcard

    :param x:
    :return: str
    """
    x = escape_wildcard(x)
    return '%' + x + '%'


def get_drug_and_bottle_information_by_drug_id_dao(drug_id):
    try:
        drug_data = DrugMaster.get_drug_and_bottle_information_by_drug_id(drug_id=drug_id)
        return drug_data
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_drug_and_bottle_information_by_drug_id_dao".format(e))
        return error(2001)


@validate(required_fields=["drug_id_list"])
def get_drug_id_list_for_same_configuration_by_drug_id(drug_id_dict):
    """

    :param drug_id_dict:
    :return:
    """
    try:
        drug_id_list = drug_id_dict["drug_id_list"]

        drug_id_list_resp = list()

        sub_query = DrugMaster.select(fn.CONCAT(DrugMaster.formatted_ndc, DrugMaster.txr).alias("fndc_txr")).where(
            DrugMaster.id.in_(drug_id_list))

        query = DrugMaster.select(DrugMaster.id).where(fn.CONCAT(DrugMaster.formatted_ndc, DrugMaster.txr) << sub_query)

        for drug_data in query.dicts():
            drug_id_list_resp.append(drug_data["id"])

        return drug_id_list_resp
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_drug_id_list_for_same_configuration_by_drug_id".format(e))
        return error(2001)


def get_drug_dosage_types_dao():
    try:
        results = DosageType.db_get()
        return results

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_drug_dosage_types_dao".format(e))
        return error(2001)


def change_status_by_ips_dao(ndc_status_dict):
    try:
        activate_unique_drug_ids = set()
        inactive_unique_drug_data = dict()

        for ndc_data in ndc_status_dict:
            status = int(ndc_data['drug_status'])
            ndc = ndc_data['ndc']
            update_date = ndc_data['drug_status_updated_date']
            try:
                query = DrugMaster.select(DrugMaster.id,
                                          DrugMaster.formatted_ndc,
                                          DrugMaster.txr,
                                          DrugMaster.concated_fndc_txr_field(sep='#').alias('fndc_txr'),
                                          UniqueDrug.id.alias('unique_drug_id')).dicts() \
                    .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                          (DrugMaster.txr == UniqueDrug.txr))) \
                    .where(DrugMaster.ndc == ndc).get()

            except DoesNotExist as e:
                logger.info('ndc not found in db so skipping:' + str(ndc))
                continue
            drug_id = query['id']
            if status:
                activate_unique_drug_ids.add(query['unique_drug_id'])
            else:
                inactive_unique_drug_data[query['unique_drug_id']] = {'fndc_txr': "{}#{}".format(
                    query['formatted_ndc'], query['txr'])}
            update_status = DrugStatus.db_update_status(drug_id, status, update_date)
            logger.info("In change_status_by_ips_dao: drug status updated: {}".format(update_status))
        if inactive_unique_drug_data:
            # active_unique_drug_single_fndc_txr_based: unique drug for which anyone drugs is active
            active_unique_drug_single_fndc_txr_based = set()
            for unique_drug_id, fndc_txr in inactive_unique_drug_data.items():
                query = DrugMaster.select(UniqueDrug.id.alias('unique_drug_id')) \
                    .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
                    .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                          (DrugMaster.txr == UniqueDrug.txr))) \
                    .where(DrugMaster.concated_fndc_txr_field(sep='#') == fndc_txr['fndc_txr'],
                           DrugStatus.ext_status == settings.VALID_EXT_STATUS) \
                    .group_by(DrugMaster.formatted_ndc,
                              DrugMaster.txr)
                for record in query.dicts():
                    active_unique_drug_single_fndc_txr_based.add(record['unique_drug_id'])

            # inactive_unique_drug_ips_ndc_based: unique drugs to mark inactive due to deactivating ndc from ips.
            inactive_unique_drug_ips_ndc_based = set(inactive_unique_drug_data.keys())
            logger.info('inactive_unique_drug_ips_ndc_based: {}'.format(inactive_unique_drug_ips_ndc_based))
            logger.info('active_unique_drug_single_fndc_txr_based: {}'.
                        format(active_unique_drug_single_fndc_txr_based))

            # inactivate_unique_drug_ids: unique drugs for which all the drugs are inactive
            inactivate_unique_drug_ids = inactive_unique_drug_ips_ndc_based - \
                                         active_unique_drug_single_fndc_txr_based
            logger.info('inactivate_unique_drug_ids: {}'.format(inactivate_unique_drug_ids))
            if inactivate_unique_drug_ids:
                # if drugs are deactivated then get all the alt_drug_option_ids for which we need to deselect the
                # particular drug
                alt_drug_option_ids, company_ids = get_pending_facility_drug_data(
                    list(inactivate_unique_drug_ids))

                logger.info('alt_drug_option_ids: {}'.format(alt_drug_option_ids))
                if alt_drug_option_ids:
                    # marking them deselected
                    status = remove_alternate_drug_by_id({'alternate_drug_option_ids': alt_drug_option_ids,
                                                          'user_id': 1
                                                          })
                    logger.info("In change_status_by_ips_dao: remove_alternate_drug_by_id status: {}".format(status))
    except (IntegrityError, InternalError) as e:
        logger.error("Error in change_status_by_ips_dao".format(e))
        return error(2001)


@log_args
def get_batch_drug_not_imported(batch_id, filter_fields, sort_fields, paginate, company_id):

    try:
        response = dict()
        like_search_list = ["drug_name"]
        membership_search_list = []
        order_list = list()
        txr_list=[]

        if sort_fields:
            order_list.extend(sort_fields)
        else:
            order_list = [["drug_name", 1]]

        fields_dict = {"ndc": DrugMaster.ndc,
                       "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
                       "available_quantity": CanisterMaster.available_quantity,
                       "updated_by": DrugStockHistory.created_by
                       }
        if "ndc" in filter_fields and filter_fields["ndc"]:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'], "required_entity": "ndc"})
            if ndc_list:
                membership_search_list.append("ndc")
                filter_fields[
                    "ndc"], drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                    {"scanned_ndc": filter_fields['ndc'],
                     "required_entity": "ndc"})
            else:
                response = {"drug_data": [], "total_drug_count": 0}
                return create_response(response)

        unique_drugs = PackDetails.select(fn.DISTINCT(DrugMaster.id).alias('drug_id'),
                                          DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                          fn.SUM(SlotDetails.quantity).alias('required_qty')).dicts() \
            .join(BatchMaster, on=PackDetails.batch_id == BatchMaster.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(BatchMaster.id << batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) \
            .group_by(DrugMaster.concated_fndc_txr_field())
        logger.info(unique_drugs)

        unique_drug_dict = {}
        for record in unique_drugs:
            unique_drug_dict[record['fndc_txr']] = int(record['required_qty'])
        print(unique_drug_dict)

        if len(unique_drug_dict):
            query = DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                      DrugMaster.strength,
                                      DrugMaster.strength_value,
                                      DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                      DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                      DrugMaster.ndc,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.txr,
                                      DrugMaster.image_name,
                                      DrugMaster.shape,
                                      DrugMaster.imprint,
                                      fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                            DrugDetails.last_seen_by, ).alias('last_seen_with'),
                                      fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                            DrugDetails.last_seen_date).alias('last_seen_on'),
                                      fn.SUM(CanisterMaster.available_quantity).alias('available_qty'),
                                      fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                            DrugStockHistory.is_in_stock).alias(
                                          "is_in_stock"),
                                      fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                            DrugStockHistory.created_by).alias('stock_updated_by')).dicts() \
                .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                      & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == company_id))) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .where(DrugMaster.concated_fndc_txr_field() << list(unique_drug_dict.keys())) \
                .group_by(DrugMaster.concated_fndc_txr_field())

            results, count, non_paginate_result = get_results(query.dicts(), fields_dict=fields_dict,
                                                              filter_fields=filter_fields,
                                                              like_search_list=like_search_list,
                                                              sort_fields=order_list,
                                                              paginate=paginate,
                                                              membership_search_list=membership_search_list,
                                                              non_paginate_result_field_list=['fndc_txr'])

            for data in results:
                txr_list.append(data['txr'])
                logger.info(data['drug_id'])
                if data['fndc_txr'] in unique_drug_dict.keys():
                    data['required_qty'] = unique_drug_dict[data['fndc_txr']]
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
            for record in results:
                record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), 0)
                record['is_in_stock'] = 0 if record["inventory_qty"] <= 0 else 1

            response['drug_data'] = results

            response['total_drug_count'] = count
            response['drug_fndc_txr'] = non_paginate_result

        return create_response(response)

    except IntegrityError as ex:
        logger.error("Error in get_batch_drug_not_imported".format(ex))
        raise IntegrityError
    except InternalError as e:
        logger.error("Error in get_batch_drug_not_imported".format(e))
        raise InternalError


def get_canister_info_from_canister_list(canister_list):
    """
    Function to get canister location info from canister list after batch import
    # @param batch_id:
    @param canister_list:
    @return:
    """
    try:
        canister_info_list = list()
        device_info = list()
        clauses = list()
        # clauses.append((PackDetails.batch_id == batch_id))
        clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
        if len(canister_list):
            canister_list = [int(can) for can in canister_list]
            clauses.append(PackAnalysisDetails.canister_id << canister_list)

            select_fields = [fn.IF(CanisterMaster.id.is_null(True), 'null',
                                   CanisterMaster.id).alias('canister_id'),
                             fn.IF(CanisterMaster.available_quantity.is_null(True), 'null',
                                   CanisterMaster.available_quantity).alias('available_quantity'),
                             fn.IF(CanisterMaster.drug_id.is_null(True), 'null',
                                   CanisterMaster.drug_id).alias('drug_id'),

                             fn.IF(CanisterMaster.rfid.is_null(True), 'null',
                                   CanisterMaster.rfid).alias('rfid'),
                             fn.IF(CanisterMaster.active.is_null(True), 'null',
                                   CanisterMaster.active).alias('active'),
                             fn.IF(CanisterMaster.canister_type.is_null(True), 'null',
                                   CanisterMaster.canister_type).alias('canister_type'),
                             fn.IF(LocationMaster.display_location.is_null(True), 'null',
                                   LocationMaster.display_location).alias('display_location'),
                             fn.IF(LocationMaster.location_number.is_null(True), 'null',
                                   LocationMaster.location_number).alias('location_number'),
                             fn.IF(PackAnalysisDetails.device_id.is_null(True), 'null',
                                   PackAnalysisDetails.device_id).alias('device_id'),
                             fn.IF(DeviceMaster.name.is_null(True), 'N.A.', DeviceMaster.name).alias('name'),
                             fn.GROUP_CONCAT(
                                 DeviceMaster.name, '-', LocationMaster.display_location
                             ).alias('canister_list'),
                             ]

            query = PackDetails.select(*select_fields) \
                .join(PackAnalysis, JOIN_LEFT_OUTER,
                      on=((PackAnalysis.pack_id == PackDetails.id) &
                          (PackDetails.batch_id == PackAnalysis.batch_id))) \
                .join(PackAnalysisDetails, JOIN_LEFT_OUTER,
                      on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .group_by(CanisterMaster.id) \
                .where(*clauses)

            for record in query.dicts():
                can_info = [record['canister_id'],
                            record['available_quantity'],
                            record['drug_id'],
                            record['rfid'],
                            record['active'],
                            record['canister_type'],
                            record['display_location'],
                            record['location_number'],
                            record['device_id'],
                            record['name']]

                if record['canister_list']:
                    device_name_loc = list(record['canister_list'].split(","))

                    for device_name_loc_data in device_name_loc:
                        if device_name_loc_data not in device_info:
                            device_info.append(device_name_loc_data)

                else:
                    device_info = None

                canister_info_list.append(','.join(can_info))

        return canister_info_list, device_info

    except IntegrityError as ex:
        logger.error("Error in get_canister_info_from_canister_list".format(ex))
        raise IntegrityError
    except InternalError as e:
        logger.error("Error in get_canister_info_from_canister_list".format(e))
        raise InternalError
    except Exception as e:
        logger.error("Error in get_canister_info_from_canister_list".format(e))
        return None, None


@log_args
def get_batch_drug_imported(filter_fields, sort_fields, paginate, system_id, batch_id = None):
    """
    @desc: get_batch_drug_imported
    @param batch_id:
    @return:
    """
    # batch_status = BatchMaster.db_get_batch_status(batch_id)
    # logger.info("batch status for batch unique drugs {}".format(batch_status))
    drug_data = []
    response = {}
    txr_list = []
    clauses = list()
    clauses.append((PackDetails.system_id == system_id))
    # clauses.append((PackDetails.batch_id == batch_id))
    clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
    # clauses.append(CanisterMaster.active == settings.is_canister_active)
    # clauses.append(CanisterMaster.company_id == company_id)

    like_search_list = ['imprint', 'color', 'shape', 'drug_name']
    exact_search_list = ['strength', 'canister_id']
    membership_search_list = ['ndc']
    having_search_list = []
    order_list = [["drug_name", 1]]

    if sort_fields:
        order_list.extend(sort_fields)

    fields_dict = {
        # do not give alias here, instead give it in select_fields,
        # as this can be reused in where clause
        "canister_master_id": CanisterMaster.id,
        "ndc": DrugMaster.ndc,
        "imprint": DrugMaster.imprint,
        "strength": DrugMaster.strength_value,
        "color": DrugMaster.color,
        "shape": CustomDrugShape.name,
        "drug_fndc_txr": DrugMaster.concated_fndc_txr_field("##"),
        "location_number": PackAnalysisDetails.location_number,
        "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
        "display_location": LocationMaster.display_location,
        "canister_id": PackAnalysisDetails.canister_id,
        "available_quantity": CanisterMaster.available_quantity

    }

    try:
        select_fields = [fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).alias('canister_id'),
                         DrugMaster.id.alias('drug_master_id'),
                         DrugMaster.strength,
                         DrugMaster.strength_value,
                         DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                         DrugMaster.txr,
                         DrugMaster.ndc,
                         DrugMaster.formatted_ndc,
                         DrugMaster.color,
                         DrugMaster.imprint,
                         DrugMaster.image_name,
                         DrugMaster.shape.alias("shape_name"),
                         fields_dict['drug_fndc_txr'].alias('drug_fndc_txr'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                         fn.IF(DrugStockHistory.created_by.is_null(True), None,
                               DrugStockHistory.created_by).alias('stock_updated_by'),
                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                               DrugDetails.last_seen_by, ).alias('last_seen_with'),
                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                               DrugDetails.last_seen_date).alias('last_seen_on'),
                         fn.sum(SlotDetails.quantity).alias("required_quantity"),
                         fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).alias('pack_id_list'),
                         DrugDimension.id.alias('drug_dimension_id'),
                         DrugDimension.shape,
                         DrugDimension.depth, DrugDimension.width, DrugDimension.length, DrugDimension.fillet,
                         DrugDimension.unique_drug_id,
                         CustomDrugShape.id.alias('custom_shape_id')
                         # fn.GROUP_CONCAT(
                         #     Clause(fn.CONCAT(fn.IF(SlotDetails.quantity.is_null(True), 'null',
                         #                            SlotDetails.quantity), ',',
                         #                      fn.IF(SlotDetails.is_manual.is_null(True), 'null',
                         #                            SlotDetails.is_manual)),
                         #            SQL(" SEPARATOR ' | ' "))).coerce(False).alias('slot_details'),
                         ]
        if "ndc" in filter_fields and filter_fields["ndc"]:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'], "required_entity": "ndc"})
            if ndc_list:
                filter_fields[
                    "ndc"], drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                    {"scanned_ndc": filter_fields['ndc'],
                     "required_entity": "ndc"})
            else:
                response = {"records": [], "total_drugs": 0, "drug_fndc_txr": {}}
                return create_response(response)

        query = PackDetails.select(*select_fields).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER,
                  on=((PackAnalysis.pack_id == PackDetails.id) &
                      (PackDetails.batch_id == PackAnalysis.batch_id))) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER,
                  on=((PackAnalysisDetails.analysis_id == PackAnalysis.id)
                      & (PackAnalysisDetails.slot_id == SlotDetails.id))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        logger.info(query)

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                          clauses=clauses,
                                                          sort_fields=order_list,
                                                          paginate=paginate,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          membership_search_list=membership_search_list,
                                                          having_search_list=having_search_list,
                                                          non_paginate_result_field_list=['drug_fndc_txr']
                                                          )

        for record in results:
            if record["txr"] is not None:
                drug_id = record['formatted_ndc'] + "##" + record['txr']
                txr_list.append(record['txr'])
            else:
                drug_id = record['formatted_ndc'] + "##"
            if drug_id not in drug_data:
                response_dict = {
                    'formatted_ndc_txr': drug_id,
                    'drug_name': record["drug_name"]
                }

                if record['canister_id'] is not None:
                    record['canister_id_list'], device_info = get_canister_info_from_canister_list(list(record[
                                                                                                       'canister_id'].split(
                                                                                                       ',')))
                    record['canister_list'] = device_info
                else:
                    record['canister_id_list'] = list()
                    record['canister_list'] = set()

                response_dict.update(record)
                drug_data.append(response_dict)
        inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
        for record in drug_data:
            record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), 0)
            record['is_in_stock'] = 0 if record["inventory_qty"] <= 0 else 1
        response['records'] = drug_data
        response['total_drugs'] = count
        response['drug_fndc_txr'] = non_paginate_result

        logger.info(response)
        return create_response(response)

    except IntegrityError as ex:
        logger.error("Error in get_batch_drug_imported".format(ex))
        raise IntegrityError
    except InternalError as e:
        logger.error("Error in get_batch_drug_imported".format(e))
        raise InternalError
    except Exception as e:
        logger.error("Error in get_batch_drug_imported".format(e))
        return error(0)


@log_args_and_response
def get_pack_drugs_by_pack_id_dao(old_drug_ids, current_pack_id):
    """
    function to get pack drug data by pack ids and drug ids
    @param pack_ids:
    @param drug_ids:
    @return:
    """
    try:
        query = PackRxLink.select(PackRxLink.pack_id,
                                  SlotDetails.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(PackRxLink.pack_id == current_pack_id,
                   SlotDetails.drug_id << old_drug_ids)
        return query
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_pack_drugs_by_pack_id_dao".format(e))
        raise e


@log_args_and_response
def get_drug_info_based_on_ndc(ndc):
    try:
        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugMaster.formatted_ndc, DrugMaster.txr,
                                  DrugMaster.brand_flag, DrugStatus.ext_status, DrugMaster.drug_name).dicts().join(
            DrugStatus, JOIN_LEFT_OUTER, on=DrugMaster.id == DrugStatus.drug_id) \
            .where(DrugMaster.ndc == ndc)
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_drug_info_based_on_ndc".format(e))
        return False
    except Exception as e:
        logger.error("Error in get_drug_info_based_on_ndc".format(e))
        return False


@log_args_and_response
def get_drug_and_bottle_information_by_drug_id_dao(drug_id: int):
    """
    This function to drug data by drug id
    @param drug_id:
    @return:
    @return:

    """
    try:
        drug_data = DrugMaster.get_drug_and_bottle_information_by_drug_id(drug_id=drug_id)
        return drug_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_drug_and_bottle_information_by_drug_id_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_drug_info_by_canister(canister_id):
    """
    get drug info by canister
    @param canister_id:
    @return:
    """
    try:
        query = CanisterMaster.select(CanisterMaster.canister_stick_id, CanisterMaster.rfid, DrugMaster.id.alias(
            "drug_id"), DrugMaster.concated_fndc_txr_field().alias("fndc_txr")).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.id == canister_id)

        for record in query:
            return record

    except DoesNotExist as e:
        logger.error("Error in db_get_drug_info_by_canister {}".format(e))
        return None
    except InternalError as e:
        logger.error("Error in db_get_drug_info_by_canister {}".format(e))
        raise e


@log_args_and_response
def get_custome_drug_shape_dao():
    """
    This function to custome drug shape data
    @return:
    @return:
    """
    try:
        drug_data = CustomDrugShape.db_get()
        return drug_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_custome_drug_shape_dao {}".format(e))
        raise e



@log_args_and_response
def db_get_drug_data_by_ndc_parser_dao(ndc_list):
    try:
        return DrugMaster.db_get_drug_data_by_ndc_parser(ndc_list)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_drug_data_by_ndc_dao(ndc: int):
    """
    This function to drug data by ndc
    @param ndc:
    @return:

    """
    try:
        drug_data = DrugMaster.get(ndc=ndc)
        return drug_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_drug_data_by_ndc_dao {}".format(e))
        raise e


@log_args_and_response
def get_drugs_by_formatted_ndc_txr_dao(formatted_ndc, txr):
    """
    This function to get drug data by fndc and txr
    @param formatted_ndc:
    @param txr:
    @return:

    """
    try:
        drug_data = DrugMaster.get_drugs_by_formatted_ndc_txr(formatted_ndc, txr)
        return drug_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_drugs_by_formatted_ndc_txr_dao {}".format(e))
        raise e


@log_args_and_response
def get_drugs_for_batch_pre_processing(company_id, batch_id, filter_fields):
    """
    return drugs in the batch having other alternate drugs to let user change drugs in pack_pre_processing
    :param company_id:
    :param batch_id:
    :param filter_fields:
    :return: non_paginated_dict, count, txr_list, changed_bs_count
    """
    count: int = 0
    changed_bs_count: int = 0
    drug_dict = defaultdict(dict)
    non_paginated_dict = defaultdict(dict)
    fndc_txr_list: list = []
    txr_list: list = []
    ndc_list = []
    fields_dict = {
        'required_qty': fn.SUM(fn.FLOOR(SlotDetails.quantity)),
        "drug_name": DrugMaster.drug_name,
        "ndc": DrugMaster.ndc,
        "formatted_ndc": DrugMaster.formatted_ndc,
        "txr": DrugMaster.txr,
        'manufacturer': DrugMaster.manufacturer,
        }
    exact_search_list = ['formatted_ndc', 'txr', 'ndc']
    like_search_list = ['drug_name', 'formatted_ndc', 'txr']
    string_search_field = [
        DrugMaster.concated_drug_name_field(),
        DrugMaster.strength,
        DrugMaster.strength_value,
        DrugMaster.color,
        DrugMaster.shape,
        DrugMaster.ndc,
        DrugMaster.formatted_ndc,
        DrugMaster.txr,
        DrugMaster.manufacturer
    ]

    try:
        logger.info("Inside get_drugs_for_batch_pre_processing")
        clauses = [(PackDetails.company_id == company_id),
                   (PackDetails.batch_id == batch_id),
                   (PackDetails.pack_status << [settings.PENDING_PACK_STATUS]),
                   (DrugMaster.brand_flag == settings.GENERIC_FLAG),
                   (PatientRx.daw_code == 0)
                   ]

        if filter_fields and filter_fields.get('multi_search', None) is not None:
            multi_search_fields = filter_fields['multi_search'].split(',')
            clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_fields,
                                                  model_search_fields=string_search_field,
                                                  ndc_search_field=DrugMaster.ndc)

        clauses = get_filters(clauses, fields_dict, filter_fields,
                              exact_search_fields=exact_search_list,
                              like_search_fields=like_search_list)
        countquery = PackDetails.select() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(PackRxLink.bs_drug_id.is_null(False), PackRxLink.bs_drug_id != SlotDetails.drug_id
                   , PackDetails.company_id == company_id,
                   PackDetails.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) \
            .group_by(SlotDetails.drug_id)
        changed_bs_count = countquery.count()

        logger.info("Inside get_drugs_for_batch_pre_processing: Main Query Started")
        query = PackDetails.select(DrugMaster,
                                   DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                   fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                         DrugDetails.last_seen_by, ).alias('last_seen_with'),
                                   cast(DrugStatus.ext_status, 'SIGNED').alias('ext_status'),
                                   DrugStatus.ext_status_updated_date,
                                   DrugStatus.last_billed_date,
                                   PackRxLink.bs_drug_id,
                                   PackRxLink.fill_manually,
                                   SlotDetails.drug_id.alias('pack_drug_id'),
                                   fn.SUM(SlotDetails.quantity).alias('required_qty'))\
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(DrugStatus, on=DrugMaster.id == DrugStatus.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .where(functools.reduce(operator.and_, clauses))\
            .group_by(SlotDetails.drug_id)

        # DrugStockHistory join removed because is_in_stock is shown by inventory quantity

        logger.debug(query)
        logger.debug("Inside get_drugs_for_batch_pre_processing: Query count started")
        for record in query.dicts():
            fndc_txr = (record['formatted_ndc'], record['txr'])
            if fndc_txr not in drug_dict.keys():
                drug_dict[fndc_txr]['drug_id'] = record['id']
                drug_dict[fndc_txr]['drug_name'] = record['drug_name']
                drug_dict[fndc_txr]['ndc'] = record['ndc']
                drug_dict[fndc_txr]['formatted_ndc'] = record['formatted_ndc']
                drug_dict[fndc_txr]['strength'] = record['strength']
                drug_dict[fndc_txr]['id'] = record['id']
                drug_dict[fndc_txr]['strength_value'] = record['strength_value']
                drug_dict[fndc_txr]['manufacturer'] = record['manufacturer']
                drug_dict[fndc_txr]['txr'] = record['txr']
                drug_dict[fndc_txr]['imprint'] = record['imprint']
                drug_dict[fndc_txr]['color'] = record['color']
                drug_dict[fndc_txr]['shape'] = record['shape']
                drug_dict[fndc_txr]['image_name'] = record['image_name']
                drug_dict[fndc_txr]['brand_flag'] = record['brand_flag']
                drug_dict[fndc_txr]['brand_drug'] = record['brand_drug']
                drug_dict[fndc_txr]['drug_form'] = record['drug_form']
                drug_dict[fndc_txr]['upc'] = record['upc']
                drug_dict[fndc_txr]['generic_drug'] = record['generic_drug']
                drug_dict[fndc_txr]['last_seen_with'] = record['last_seen_with']
                drug_dict[fndc_txr]['ext_status'] = record['ext_status']
                drug_dict[fndc_txr]['ext_status_updated_date'] = record['ext_status_updated_date']
                drug_dict[fndc_txr]['last_billed_date'] = record['last_billed_date']
                drug_dict[fndc_txr]['bs_drug_id'] = record['bs_drug_id']
                drug_dict[fndc_txr]['fill_manually'] = record['fill_manually']
                drug_dict[fndc_txr]['pack_drug_id'] = record['pack_drug_id']
                fndc_txr_list.append(record['fndc_txr'])
                alternate_drug_list = list()
                drug_dict[fndc_txr]['alternate_drug_list'] = alternate_drug_list
                txr_list.append(record['txr'])
                ndc_list.append(int(record['ndc']))
                if record['bs_drug_id'] and record['id'] != record['bs_drug_id']:
                    drug_dict[fndc_txr]['bs_selected_drug'] = False
                else:
                    drug_dict[fndc_txr]['bs_selected_drug'] = True

                drug_dict[fndc_txr]['required_qty'] = record['required_qty']
            else:
                drug_dict[fndc_txr]['required_qty'] += record['required_qty']
                logger.debug("Inside get_drugs_for_batch_pre_processing: Different ndc with same fndc_txr found- fndc_txr {}".format(fndc_txr))

        if drug_dict:

            txr_with_alt_drug = get_list_of_drug_having_alternate_drugs(txr_list)
            logger.info("Inside get_drugs_for_batch_pre_processing: Removed drugs not having alternate drugs")

            logger.info("main_query_ends")
            count = len(drug_dict.keys())
            for key in drug_dict.keys():
                if drug_dict[key]['txr'] in txr_with_alt_drug:
                    non_paginated_dict[key] = drug_dict[key]

        else:
            logger.info("Inside get_drugs_for_batch_pre_processing: No drugs found for given parameter")
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in get_drugs_for_batch_pre_processing: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        logger.info(e)
        raise e
    finally:
        return non_paginated_dict, count, txr_list, changed_bs_count, ndc_list


@log_args_and_response
def get_ordered_list(list_of_dict, sort_fields):
    """
    accept list of dictionaries and returns sorted list of dictionaries.
    :param list_of_dict:
    :param sort_fields: [['required_qty', -1],['drug_name', 1]]
    :return: sorted list of dictionary
    """
    try:
        for item in sort_fields:
            if item[1] == 1:
                list_of_dict = sorted(list_of_dict, key=operator.itemgetter(str(item[0])), reverse=True)
            else:
                list_of_dict = sorted(list_of_dict, key=operator.itemgetter(str(item[0])), reverse=False)
        return list_of_dict
    except Exception as e:
        logger.error(e)


@log_args_and_response
def get_list_of_drug_having_alternate_drugs(txr_list):
    """
    return txr's having alternate drugs
    :param txr_list:
    :return:
    """
    txr_with_alt_drug = []
    try:
        query = DrugMaster.select(DrugMaster.txr,
                                  fn.COUNT(fn.DISTINCT(DrugMaster.formatted_ndc)).alias('alt_count')).dicts()\
            .where(DrugMaster.txr << txr_list).group_by(DrugMaster.txr)

        for record in query:
            if record['alt_count'] > 1:
                txr_with_alt_drug.append(record['txr'])
        return txr_with_alt_drug
    except Exception as e:
        logger.error(e)


@log_args_and_response
def dpws_paginate(non_paginated_dict, paginate):
    """
    paginate list of dictionaries just like apply_paginate
    :param non_paginated_dict:
    :param paginate:
    :return:
    """
    if paginate:
        lower = (paginate['page_number'] - 1) * paginate['number_of_rows']
        upper = paginate['page_number'] * paginate['number_of_rows']
        results = non_paginated_dict[lower:upper]
    return results


@log_args_and_response
def create_store_separate_drug_dao(company_id, unique_drug_id, dosage_type_id, user_id):
    try:
        return StoreSeparateDrug.db_create_store_separate_drug(company_id=company_id,
                                                               unique_drug_id=unique_drug_id,
                                                               dosage_type_id=dosage_type_id,
                                                               user_id=user_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in create_store_separate_drug_dao {}".format(e))
        raise e

@log_args_and_response
def delete_separate_drug_dao(drug_id_list):
    try:
        return StoreSeparateDrug.db_delete_separate_drug_dao(drug_id_list=drug_id_list)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in create_store_separate_drug_dao {}".format(e))
        raise e


@log_args_and_response
def get_unique_drug_id_from_ndc(ndc):

    try:
        logger.info("Inside get_unique_drug_id_from_ndc")
        drug_data = []
        formatted_ndc_txr_query = DrugMaster.select(DrugMaster.formatted_ndc, DrugMaster.txr).dicts() \
                                    .where(DrugMaster.ndc == ndc).get()
        formatted_ndc = formatted_ndc_txr_query["formatted_ndc"]
        txr = formatted_ndc_txr_query["txr"]

        query = DrugMaster.select(UniqueDrug.id.alias('unique_drug_id')).dicts() \
                    .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                        fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                        (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                    .where(DrugMaster.formatted_ndc == formatted_ndc,
                            DrugMaster.txr == txr)

        query = UniqueDrug.select(UniqueDrug.id).dicts().where(UniqueDrug.formatted_ndc == formatted_ndc,
                                                               UniqueDrug.txr == txr).get()

        # for record in query:
        #     drug_data.append(record)
        return query["id"]
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_unique_drug_id_from_ndc".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in get_unique_drug_id_from_ndc:{e}")


@log_args_and_response
def get_drug_stocks_and_dimension_details(fndc_txr_list):

    try:
        drug_data = {}
        drug_query = UniqueDrug.select(UniqueDrug.concated_fndc_txr_field().alias('fndc_txr'),fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                        DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                  DrugDetails.last_seen_by.alias("last_seen_with"), DrugDimension.approx_volume
                                  ).dicts() \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) ))\
            .where(UniqueDrug.concated_fndc_txr_field() << fndc_txr_list)

        for record in drug_query:
            drug_data[record['fndc_txr']] = {
                'is_in_stock': record['is_in_stock'],
                'last_seen_with': record['last_seen_with'],
                'approx_volume': record['approx_volume']
            }
        return drug_data
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_drug_stocks_and_dimension_details".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in get_drug_stocks_and_dimension_details:{e}")




@log_args_and_response
def register_powder_pill_daw(fndc, txr, is_powder_pill):
    try:
        response = UniqueDrug.db_update_powder_pill_data(fndc=fndc, txr=txr, is_powder_pill=is_powder_pill)
        return response
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in register_powder_pill_daw".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in register_powder_pill_daw:{e}")


@log_args_and_response
def save_drug_dimension_image_to_drug_master(unique_drug, image_url):
    drug_list = []
    drug_image = ""
    update_image = False
    drug_image_exists = False
    try:
        # check drug images exist for this unique drug
        query = DrugMaster.select(DrugMaster.id, DrugMaster.image_name).dicts() \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))).where(UniqueDrug.id == unique_drug)

        for record in query:
            drug_image = record['image_name']
            if drug_image:
                if not blob_exists(drug_image, drug_master_dir, True):
                    update_image = True
                    drug_list.append(record['id'])
                else:
                    image_url = drug_image
                    drug_image_exists = True
            else:
                update_image = True
                drug_list.append(record['id'])

        if update_image:
            logger.info(
                "In save_drug_dimension_image_to_drug_master: Updating Image name for drug {} and image_name {}".format(
                    drug_list, image_url))

            if drug_image_exists:
                DrugMaster.db_update_image_name_in_drug_master(image_url, drug_list)
            else:
                if blob_exists(image_url, drug_dimension_dir, True):
                    source_blob = drug_dimension_dir + '/' + image_url
                    destination_blob = drug_master_dir + '/' + image_url
                    copy_blob(drug_bucket_name, source_blob, destination_blob, True)
                    DrugMaster.db_update_image_name_in_drug_master(image_url, drug_list)

    except (IntegrityError, InternalError) as e:
        logger.error("Error in save_drug_dimension_image_to_drug_master".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in save_drug_dimension_image_to_drug_master:{e}")


@log_args_and_response
def get_all_same_drug_by_drug_id(drug_id):

    try:
        DrugMasterAlias = DrugMaster.alias()
        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugMaster.formatted_ndc, DrugMaster.txr).dicts() \
            .join(DrugMasterAlias, on=(
                   ( DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) & (DrugMaster.txr == DrugMasterAlias.txr))) \
            .where(DrugMasterAlias.id == drug_id)

        return [record for record in query]

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_all_same_drug_by_drug_id".format(e))
        raise e
    except Exception as e:
        logger.error(f"Error in get_all_same_drug_by_drug_id:{e}")
        raise e


@log_args_and_response
def get_same_or_alternate_canister_by_pack(company_id, ndc, pack_id=None, mfd_analysis_ids=None):
    try:

        canister_list = []
        clauses = []
        order_list = []
        mfd_daw = 1
        DrugMasterAlias = DrugMaster.alias()
        logger.info(f"In get_same_or_alternate_canister_by_pack")
        select_fields = [DrugMasterAlias.txr.alias("txr_alias"),
                         DrugMasterAlias.formatted_ndc.alias("formatted_ndc_alias"),
                         DrugMaster.formatted_ndc,
                         DrugMaster.txr,
                         DrugMaster.ndc,
                         DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                         DrugMaster.image_name,
                         DrugMaster.imprint,
                         DrugMaster.color,
                         DrugMaster.shape,
                         CanisterMaster.id.alias("canister_id"),
                         CanisterMaster.available_quantity,
                         CanisterMaster.active,
                         fn.IF(
                             CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                             constants.EXPIRED_CANISTER,
                             fn.IF(
                                 CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                 constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias(
                             "expiry_status"),
                         DeviceMaster.name.alias("device_name"),
                         DeviceMaster.device_type_id,
                         LocationMaster.display_location,
                         LocationMaster.location_number,
                         ContainerMaster.ip_address,
                         ContainerMaster.secondary_ip_address,
                         ContainerMaster.secondary_mac_address,
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                               DrugStockHistory.is_in_stock).alias(
                             "is_in_stock"),
                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                               DrugDetails.last_seen_by).alias('last_seen_with'),
                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                               DrugDetails.last_seen_date).alias('last_seen_on'),
                         ContainerMaster.shelf,
                         DeviceMaster.ip_address.alias("device_ip_address"),
                         DeviceMaster.serial_number,
                         DeviceMaster.id.alias("device_id"),
                         ContainerMaster.drawer_name.alias('drawer_number')]

        if pack_id:
            select_fields.append(PatientRx.daw_code)
            select_fields.append(DrugMasterAlias.brand_flag)

        query = CanisterMaster.select(*select_fields).dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(DrugMasterAlias, on=((DrugMaster.txr == DrugMasterAlias.txr) & (DrugMaster.brand_flag == DrugMasterAlias.brand_flag))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                                                          & (DrugMaster.txr == UniqueDrug.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                          (DrugStockHistory.is_active == True) &
                                                          (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                                    (DrugDetails.company_id == company_id))) \

        if pack_id:
            query = query \
                .join(SlotDetails, on=SlotDetails.drug_id == DrugMasterAlias.id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \

        clauses.append((DrugMasterAlias.ndc == ndc))
        clauses.append((CanisterMaster.available_quantity != 0))
        clauses.append((CanisterMaster.company_id == company_id))
        if pack_id:
            clauses.append((PackRxLink.pack_id == pack_id))

        query = query.where(functools.reduce(operator.and_, clauses))

        order_list.append(
            SQL('FIELD(expiry_status, {},{})'.format(constants.EXPIRES_SOON_CANISTER,
                                                     constants.NORMAL_EXPIRY_CANISTER)))
        order_list.append(CanisterMaster.available_quantity.desc())

        if order_list:
            query = query.order_by(*order_list)

        query = query.group_by(CanisterMaster.id)

        query = query.having(SQL('expiry_status != 0'))

        logger.info(f"In get_same_or_alternate_canister_by_pack, query:{query}")

        if mfd_analysis_ids:
            #this block execute when api called from mfs station.
            #check daw code for given mfd analysis ids and ndc and if daw 1 available, we will return only same canister drug list.
            mfd_daw = get_daw_from_analysis_ids(ndc, mfd_analysis_ids)
            logger.info(f"In get_same_or_alternate_canister_by_pack, mfd_daw: {mfd_daw}")

        for data in query:

            daw_code = data.pop("daw_code", None)
            brand_flag = data.pop("brand_flag", None)
            original_txr = data.pop("txr_alias", None)
            original_formatted_ndc = data.pop("formatted_ndc_alias", None)

            if (data["formatted_ndc"] == original_formatted_ndc) and (data["txr"] == original_txr):
                alternate_drug_canister = False
            else:
                alternate_drug_canister = True

            data["alternate_drug_canister"] = alternate_drug_canister

            if pack_id:
                logger.info(
                    f"In get_same_or_alternate_canister_by_pack, pack:{pack_id}, ndc:{ndc}, daw: {daw_code}, brand_flag: {brand_flag}")

                if daw_code == 1 or brand_flag == settings.BRAND_FLAG:

                    if (data["formatted_ndc"] == original_formatted_ndc) and (data["txr"] == original_txr):
                        canister_list.append(data)
                else:
                    canister_list.append(data)
            else:
                if mfd_daw:
                    if (data["formatted_ndc"] == original_formatted_ndc) and (data["txr"] == original_txr):
                        canister_list.append(data)
                else:
                    canister_list.append(data)

        return canister_list
    except Exception as e:
        logger.error("error in get_same_or_alternate_canister_by_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in get_same_or_alternate_canister_by_pack: exc_type - {exc_type}, filename - {filename}, line - "
            f"{exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def db_update_drug_id_by_slot_id(slot_details_data: list):
    """
    update the drug_id column by slot_details id
    """
    try:
        logger.info("Inside db_update_drug_id_by_slot_id")
        logger.debug("slot_details_data: {}".format(slot_details_data))
        user_id = 1
        pack_drug_tracker_details = list()
        for record in slot_details_data:
            slot_id = record["slot_id"]
            drug_id = record["drug_id"]
            previous_drug_id = SlotDetails.db_get_drug_id_based_on_slot_id(slot_id)
            txr_of_drug_id = DrugMaster.db_get_txr_by_drug_id(drug_id)
            txr_of_previous_drug_id = DrugMaster.db_get_txr_by_drug_id(previous_drug_id)

            if txr_of_drug_id == txr_of_previous_drug_id:
                if previous_drug_id != drug_id:
                    update_dicts = {"drug_id": drug_id}
                    slot_details_status = SlotDetails.db_update_slot_details_by_slot_id(update_dicts, slot_id)

                    if slot_details_status:
                        pack_drug_tracker_info = {"slot_details_id": slot_id,
                                                  "previous_drug_id": previous_drug_id,
                                                  "updated_drug_id": drug_id,
                                                  "module": constants.PDT_SLOT_TRANSACTION,
                                                  "created_by": user_id,
                                                  "created_date": get_current_date_time()
                                                  }

                        pack_drug_tracker_details.append(pack_drug_tracker_info)
            else:
                logger.error("In db_update_drug_id_by_slot_id txr of slot_details_drug_id {} and filled_drug_id {} are different".format(previous_drug_id, drug_id))
        return pack_drug_tracker_details
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_slot_details_for_manual_pack_filling(drug_data, slot_details_data):

    try:
        slot_details_status = None
        with db.transaction():
            for txr, ndc in drug_data.items():
                if ndc in slot_details_data:
                    update_dict = slot_details_data[ndc]["update_dicts"]
                    slot_ids = slot_details_data[ndc]["slot_ids"]

                    slot_details_status = SlotDetails.db_update_slot_details_by_multiple_slot_id(update_dict,
                                                                                                 slot_ids
                                                                                                 )

                    logger.info("In db_update_slot_details_for_manual_pack_filling: slot_details_status: {}".format(
                        slot_details_status))

        return slot_details_status
    except Exception as e:
        logger.error("Error in db_update_slot_details_for_manual_pack_filling: {}".format(e))
        raise e

@log_args_and_response
def get_daw_from_analysis_ids(ndc, mfd_analysis_ids):
    try:
        logger.info(f"In get_daw_from_analysis_ids")

        query = MfdAnalysis.select(PatientRx.daw_code).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(MfdAnalysis.id.in_(mfd_analysis_ids),
                   DrugMaster.ndc == ndc) \
            .group_by(PatientRx.id)

        logger.info(f"In get_daw_from_analysis_ids, query: {query}")

        for data in query:
            if data["daw_code"] == 1:
                return 1

        return 0
    except Exception as e:
        logger.error(f"In get_daw_from_analysis_ids, e: {e}")
        raise e


@log_args_and_response
def db_get_txr_and_drug_id_by_ndc_dao(ndc):
    try:
        return DrugMaster.db_get_txr_and_drug_id_by_ndc(ndc=ndc)
    except Exception as e:
        logger.error("Error in db_get_txr_and_drug_id_by_ndc_dao: {}".format(e))
        raise e

@log_args_and_response
def db_get_drug_id_by_ndc_dao(ndc_item:list):
    try:
        ndc_list = [item[0] for item in ndc_item]
        return DrugMaster.db_get_drug_id_dict_by_ndc_list(ndc=ndc_list)
    except Exception as e:
        logger.error("Error in db_get_txr_and_drug_id_by_ndc_dao: {}".format(e))
        raise e


@log_args_and_response
def get_expiry_date_of_filled_pack(pack_id):
    try:
        expiry_date = None
        query = DrugTracker.select(
            fn.MIN(fn.DATE_FORMAT(fn.STR_TO_DATE(CanisterTracker.expiration_date, '%m-%Y'), '%Y-%m-%d')).alias(
                "canister_exp_date"),
            fn.MIN(fn.DATE_FORMAT(fn.STR_TO_DATE(DrugTracker.expiry_date, '%m-%Y'), '%Y-%m-%d')).alias(
                "drug_bottle_expiry_date")
        ).dicts() \
            .join(CanisterTracker, JOIN_LEFT_OUTER, on=CanisterTracker.id == DrugTracker.canister_tracker_id) \
            .where(
            DrugTracker.pack_id == pack_id,
            DrugTracker.is_overwrite == 0
        )

        for data in query:
            logger.info(f"In get_expiry_date_of_filled_pack, data: {data}")
            l=[]
            if data["canister_exp_date"]:
                l.append(data["canister_exp_date"])
            if data["drug_bottle_expiry_date"]:
                l.append(data["drug_bottle_expiry_date"])
            if l:
                # if minimum exp_date is within 6 months we will set pack's expiry as that date
                # else we will take date 6 months from now as expiry date
                min_date = datetime.datetime.strptime(min(l)[:-2] + "01", '%Y-%m-%d')
                six_months_from_now = datetime.datetime.today() + relativedelta(months=+6)
                if min_date > six_months_from_now:
                    return six_months_from_now.strftime('%m-%Y')
                else:
                    return min_date.strftime('%m-%Y')

            # if data["canister_exp_date"] and data["drug_bottle_expiry_date"] and data["drug_bottle_lot_expiry_date"]:
            #     return min(data["canister_exp_date"], data["drug_bottle_expiry_date"], data["drug_bottle_lot_expiry_date"])
            # elif data["canister_exp_date"] and not data["drug_bottle_expiry_date"]:
            #     return data["canister_exp_date"]
            # elif not data["canister_exp_date"] and data["drug_bottle_expiry_date"]:
            #     return data["drug_bottle_expiry_date"]
            else:
                logger.info(f"In get_expiry_date_of_filled_pack, no records found in drug tracker")
                return None
    except Exception as e:
        logger.error(f"Error in get_expiry_date_of_filled_pack, e: {e}")
        raise e


@log_args_and_response
def get_fndc_txr_wise_inventory_qty(txr_list=None):
    fndc_txr_wise_inventory = {}
    try:
        if not txr_list:
            return fndc_txr_wise_inventory
        ndc_list, fndc_ndc_group = fetch_ndc_from_txr(txr_list)
        inventory_data = {int(data["ndc"]): data for data in get_current_inventory_data(
            ndc_list=ndc_list, qty_greater_than_zero=False)}
        for fndc_txr, ndc_list in fndc_ndc_group.items():
            for ndc in ndc_list:
                data = inventory_data.get(ndc, {'quantity': 0})

                fndc_txr_wise_inventory[fndc_txr] = fndc_txr_wise_inventory.get(fndc_txr, 0) + data['quantity']

        return fndc_txr_wise_inventory

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def fetch_ndc_from_txr(txr_list):
    fndc_ndc_group = {}
    ndc_list = []
    try:

        query = DrugMaster.select().dicts().where(DrugMaster.txr << txr_list, DrugMaster.ndc != None).group_by(DrugMaster.ndc)
        for record in query:
            ndc_list.append(int(record['ndc']))
            if not fndc_ndc_group.get((record['formatted_ndc'], record['txr'])):
                fndc_ndc_group[(record['formatted_ndc'], record['txr'])] = [int(record['ndc'])]
            else:
                fndc_ndc_group[(record['formatted_ndc'], record['txr'])].append(int(record['ndc']))

        return ndc_list, fndc_ndc_group
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e



@log_args_and_response
def get_drug_detail_slotwise_dao(args):

    ''' fetches drugs slot wise of a given pack. '''

    try:
        logger.info("Inside get_drug_detail_slotwise_dao")
        pack_id = args['pack_id']
        query = PackDetails.select(PackGrid.slot_number,
                                   DrugMaster.concated_drug_name_field(include_ndc=True).alias('name_strength_ndc'),
                                   DrugMaster.concated_fndc_txr_field(sep='_').alias('fndc_txr'),
                                   SlotDetails.quantity).dicts() \
                          .join(SlotHeader, on=SlotHeader.pack_id == PackDetails.id) \
                          .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                          .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id)  \
                          .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id) \
                          .where(PackDetails.id == pack_id) \
                          .group_by(DrugMaster.drug_name, PackGrid.slot_number) \
                          .order_by(PackGrid.slot_number)

        for record in query:
            yield record

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_drug_detail_slotwise_dao {}".format(e))
        raise error(2001)
    except Exception as e:
        logger.error("Error in get_drug_detail_slotwise_dao {}".format(e))
        raise error(1000, "Error in get_drug_detail_slotwise_dao: " + str(e))


@log_args_and_response
def get_drug_image_data_dao(ndc_list, ndc_qty_map, company_id):

    ''' fetches drugs image from ndc. '''

    try:
        drug_data = {}
        logger.info("Inside get_drug_image_dao")
        query = (DrugMaster.select(DrugMaster, DrugDetails.last_seen_by)
                 .join(UniqueDrug,
                       on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr)))
                 .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                         (DrugDetails.company_id == company_id)))
                 .where(DrugMaster.ndc << ndc_list).dicts())
        for record in query:
            check_qty = ndc_qty_map.get(record["ndc"], None)
            if check_qty:
                is_in_stock = 1 if check_qty > 0 else 0
            else:
                is_in_stock = None
            drug_data[record["ndc"]] = {"image_name": record.get("image_name", None),
                                        "color": record.get("color", None),
                                        "shape": record.get("shape", None),
                                        "is_in_stock": is_in_stock,
                                        "last_seen_with": record.get("last_seen_by", None),
                                        "imprint": record.get("imprint", None)
                                        }

        return drug_data

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_drug_image_dao {}".format(e))
        raise error(2001)
    except Exception as e:
        logger.error("Error in get_drug_image_dao {}".format(e))
        raise error(1000, "Error in get_drug_image_dao: " + str(e))



@log_args_and_response
def get_lot_no_from_ndc_dao(ndc, no_of_records):
    try:
        response_list = []
        lot_no_list = []
        lot_no_alias = fn.IF(DrugTracker.lot_number.is_null(False), DrugTracker.lot_number,
                             CanisterTracker.lot_number)

        query = DrugMaster.select(DrugTracker.id,
                                  DrugMaster.ndc,
                                  fn.IF(DrugTracker.lot_number.is_null(False), DrugTracker.lot_number,
                                        CanisterTracker.lot_number).alias('lot_number'),
                                  fn.IF(DrugTracker.expiry_date.is_null(False), DrugTracker.expiry_date,
                                        CanisterTracker.expiration_date).alias('expiration_date')) \
            .join(DrugTracker, on=DrugMaster.id == DrugTracker.drug_id) \
            .join(CanisterTracker, JOIN_LEFT_OUTER, on=CanisterTracker.id == DrugTracker.canister_id) \
            .where(DrugMaster.ndc == ndc).group_by(lot_no_alias).order_by(DrugTracker.id.desc()).dicts()

        for record in query:
            if record['lot_number']:
                response_dict = dict()
                response_dict['lot_number'] = record['lot_number']
                response_dict['expiration_date'] = record['expiration_date']
                response_list.append(response_dict)
                lot_no_list.append(record['lot_number'])

        response_data = response_list[:no_of_records]

        return response_data
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_lot_no_from_ndc_dao {}".format(e))
        raise error(2001)
    except Exception as e:
        logger.error("Error in get_lot_no_from_ndc_dao {}".format(e))
        raise error(1000, "Error in get_lot_no_from_ndc_dao: " + str(e))
#
# if __name__ == '__main__':
#     init_db(db, 'database_migration')
#     print(db_get_drug_id_by_ndc_dao(['00002143611','00002150680','00002202402','00002203502','00002237711','00002311509','00002318280','00002322930','00002323560','00002324030']))
#     print(get_fndc_txr_wise_inventory_qty(txr_list = [77]))


@log_args_and_response
def get_drug_list_from_case_id_ndc(ndc, case_id=None):
    try:
        logger.info("In get_drug_list_from_case_id_ndc")
        clauses = []
        drug_ids = []
        ndc_data = {}
        if case_id:
            clauses.append(DrugTracker.case_id << case_id)
        if ndc:
            clauses.append(DrugMaster.ndc << ndc)
        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugTracker.expiry_date, DrugTracker.case_id) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.drug_id == DrugMaster.id)\
            .where(*clauses).order_by(DrugTracker.id.desc()).dicts()
        for record in query:
            drug_ids.append(record['id'])
            ndc_data[record['id']] = record['ndc']
        return list(set(drug_ids)), ndc_data

    except Exception as e:
        logger.error("error in get_drug_list_from_case_id_ndc {}".format(e))
        return e


@log_args_and_response
def db_get_alternate_ndcs(ndc_list):
    try:
        ndc_alternate_map = {}
        alternate_ndcs = []
        DrugMasterAlias = DrugMaster.alias()
        query = DrugMaster.select(DrugMasterAlias.ndc.alias("alternate"), DrugMaster.ndc).dicts() \
            .join(DrugMasterAlias, on=((DrugMaster.formatted_ndc != DrugMasterAlias.formatted_ndc) & (
                    DrugMaster.txr == DrugMasterAlias.txr))) \
            .where(DrugMaster.ndc.in_(ndc_list))
        for record in query:
            if int(record["ndc"]) not in ndc_alternate_map:
                ndc_alternate_map[int(record["ndc"])] = [int(record["alternate"])]
            else:
                ndc_alternate_map[int(record["ndc"])].append(int(record["alternate"]))
            if record["alternate"] not in alternate_ndcs:
                alternate_ndcs.append(int(record["alternate"]))
        for ndc in ndc_list:
            if ndc not in ndc_alternate_map:
                ndc_alternate_map[ndc] = []
        return ndc_alternate_map, alternate_ndcs
    except Exception as e:
        logger.error("error in get_drug_list_from_case_id_ndc {}".format(e))
        return e
