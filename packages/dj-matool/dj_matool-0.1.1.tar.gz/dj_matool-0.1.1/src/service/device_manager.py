# -*- coding: utf-8 -*-
"""
    src.device_manager
    ~~~~~~~~~~~~~~~~
    The module defines the apis for managing the devices in the conveyor. A conveyor system
    consists of multiple devices and robots grouped together. The apis are defined to register robot ,
    devices and group them together to form a conveyor.

    Todo:

    :copyright: (c) 2015 by Dose pack LLC.

"""

import json
from collections import deque, defaultdict
from uuid import uuid1
from peewee import InternalError, DoesNotExist, IntegrityError, DataError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time, log_args_and_response, log_args
from dosepack.validation.validate import validate
from src import constants
from src.dao.canister_dao import assign_cart_location_to_canister, get_canister_data_by_rfid_dao, \
    update_canister_location_based_on_rfid, get_canister_history_latest_record_can_id_dao, \
    update_canister_history_by_id_dao, create_canister_history_record, db_get_canister_data_by_location_id_dao, \
    db_check_canister_available_dao, db_get_current_canister_based_on_location, db_get_current_canister_location, \
    update_replenish_based_on_device
from src.dao.canister_dao import get_canister_present_on_location
from src.dao.batch_dao import get_progress_batch_id
from src.dao.device_manager_dao import get_robot_data_dao, get_robots_by_systems_dao, verify_device_id_dao, \
    get_robot_dao, get_robot_serial_dao, add_robot_dao, update_device_data_dao, get_system_id_by_device_id_dao, \
    get_active_robots_count_by_system_id_dao, get_system_capacity_dao, update_system_capacity_dao, get_device_data_dao, \
    get_device_master_data_dao, add_device_data_dao, db_get_disabled_locations, validate_device_ids_with_company, \
    get_location_id_by_display_location_dao, disabled_locations_dao, set_location_enable_dao, \
    set_location_disable_dao, get_container_data_based_on_serial_numbers_dao, \
    get_device_data_by_device_id_dao, get_mfs_device_data, update_container_lock_status, get_device_drawer_info, \
    get_device_type_data_dao, get_device_shelf_info, db_get_enabled_locations, \
    get_location_id_by_display_location_list_dao, locations_to_be_disabled, get_locations_per_drawer, \
    get_disabled_drawers_by_device, get_location_canister_data_by_display_location, \
    validate_device_id_dao, get_location_info_from_location_id, get_quadrant_from_device_location_dao, \
    get_location_id_by_location_number_dao, get_location_info_from_display_location
from src.dao.guided_replenish_dao import db_get_latest_guided_canister_transfer_data, update_guided_tracker_status, \
    add_data_in_guided_transfer_cycle_history, guided_transfer_couch_db_timestamp_update
from src.dao.mfd_canister_dao import (get_canister_data_by_location_id, get_canister_data_by_rfid,
                                      update_mfd_canister_location)
from src.dao.mfd_dao import get_current_mfs_batch_data, associate_canister_with_analysis, \
    get_mfs_transfer_drawer_data, \
    mfd_update_transfer_done, \
    get_empty_location_by_drawer_level, get_empty_location_by_trolley, update_mfd_transfer_couch_db
from src.dao.couch_db_dao import get_document_from_couch_db
from src.dao.pack_analysis_dao import update_pack_analysis_details, get_pack_list_by_robot, get_manual_analysis_ids
from src.exceptions import CanisterNotExist, CanisterNotPresent, NoLocationExists, RealTimeDBException

from src.service.misc import update_document_with_revision, get_logged_in_user_from_couch_db_of_system, update_couch_db_for_drawer_status, \
    get_mfd_transfer_couch_db
from src.dao.csr_dao import get_serial_number_by_station_type_and_id
from src.service.canister_transfers import update_canister_count_in_canister_transfer_couch_db
from src.service.mfd import canister_batch_update
from src.service.mfd_canister import (update_mfd_canister_history, mfd_canister_found_update_status)

logger = settings.logger


# @validate(required_fields=["client_id", "pharmacy_id", "mfg_id", "version", "code", "name", "base_url", "ip", "port"])
# def add_device(dict_device_info):
#     """ Takes the dict_device_info and adds a new device in the database
#
#         Args:
#             dict_device_info (dict): A dict containing the fields which are required to add a device
#
#         Returns:
#            json: success or error response in json
#
#         Examples:
#             >>> add_device({})
#                 []
#     """
#     record = DeviceMaster.db_create_record(dict_device_info, DeviceMaster, get_or_create=False)
#     try:
#         return create_response(record.id)
#     except AttributeError:
#         return error(2001)

@log_args_and_response
@validate(required_fields=["system_id", "name", "serial_number",
                           "version", "user_id", "company_id"])
def add_robot(dict_robot_info):
    """ Takes the dict_robot_info and adds a new robot in the database

        Args:
            dict_robot_info (dict): A dict containing the fields
            which are required to add a robot.

        Returns:
           json: success or error response in json

        Examples:
            >>> add_robot({})
                []
    """
    logger.debug("In add_robot")
    system_id = dict_robot_info["system_id"]
    try:
        robot_data = get_robot_serial_dao(serial_number=dict_robot_info["serial_number"])
        if robot_data.system_id == system_id:
            return create_response(robot_data.id)
        else:
            return error(1021)
    except DoesNotExist:  # no robot found for serial number so proceed
        pass
    try:
        dict_robot_info["device_type_id"] = settings.DEVICE_TYPES['ROBOT']
        record = add_robot_dao(robot_info=dict_robot_info)
        return create_response(record)
    except (InternalError, IntegrityError):
        return error(2001)
    except DataError:
        return error(1020)


@log_args_and_response
def compute_system_capacity(active, no_of_active_robots, system_capacity, default_system_capacity_per_robot):
    # This method computes system_capacity based current system capacity, no of active robots
    # and whether you want to enable or disable robot
    logger.debug("In compute_system_capacity")
    try:
        if no_of_active_robots == settings.ZERO_ACTIVE_ROBOT:
            # update system capacity as DEFAULT_AUTOMATIC_PER_HOUR_PER_ROBOT
            # when no_of_active_robots is 0, we want to activate a robot
            updated_system_capacity = default_system_capacity_per_robot

        elif no_of_active_robots == settings.SINGLE_ACTIVE_ROBOT:
            #    update computed system capacity when no_of_active_robots = 1
            if active:
                # double system capacity when one active robot is there, we want to activate another robot
                updated_value = system_capacity * settings.SYSTEM_CAPACITY_MULTIPLY_BY_2
                updated_system_capacity = int(updated_value) if updated_value.is_integer() else updated_value
            else:
                # reduce capacity to 0 when only one robot is active, and we want to disable it
                updated_system_capacity = '0'

        else:
            # when multiple robots are active
            capacity_per_robot = system_capacity / float(no_of_active_robots)
            if active:
                updated_value = system_capacity + capacity_per_robot
                updated_system_capacity = int(updated_value) if updated_value.is_integer() else updated_value
            else:
                updated_value = system_capacity - capacity_per_robot
                updated_system_capacity = int(updated_value) if updated_value.is_integer() else updated_value

        return updated_system_capacity

    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=["device_id", "user_id"])
def update_robot(dict_robot_info):
    """
    Updates robot fields given device_id
    and update system capacity in system_settings if active key is there in args
    :param dict_robot_info: dict containing update info.
    :return: json
    """
    logger.debug("In update_robot")
    device_id = dict_robot_info.pop("device_id")
    active = dict_robot_info.get("active", None)
    system_id = dict_robot_info.pop("system_id", None)
    dict_robot_info["modified_by"] = dict_robot_info.pop("user_id")
    dict_robot_info["modified_date"] = get_current_date_time()
    try:
        if active is None:
            status = update_device_data_dao(robot_info=dict_robot_info, device_id=device_id)
        else:
            # when active is not None means we have to enable (if active=1) or disable(if active=0) robot
            # so for that first we will update system capacity in system setting then update device master
            with db.transaction():
                if system_id is None:
                    system_id = get_system_id_by_device_id_dao(device_id=device_id)

                no_of_active_robots = get_active_robots_count_by_system_id_dao(system_id=system_id)
                system_capacity, default_system_capacity_per_robot = get_system_capacity_dao(system_id=system_id)
                update_system_dict = dict()
                update_system_dict["value"] = compute_system_capacity(active, no_of_active_robots, system_capacity,
                                                                      default_system_capacity_per_robot)
                update_system_dict['modified_by'] = dict_robot_info["modified_by"]
                update_system_dict['modified_date'] = get_current_date_time()
                system_status = update_system_capacity_dao(update_system_dict=update_system_dict,
                                                           system_id=update_system_dict)

                if system_status:
                    status = update_device_data_dao(dict_robot_info, device_id)
        return create_response(status)
    except (IntegrityError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args
@validate(required_fields=["system_id"])
def get_robot_info(dict_robot_info):
    """ Get all the robot units  for the given pharmacy_id and client_id and system_id

        Args:
            dict_robot_info (dict): A dict containing the pharmacy_id and client_id and system_id
        Returns:
           json: success or error response in json

        Examples:
            >>> get_robot_info({})
                []
                @param dict_robot_info:
    """
    logger.debug("In get_robot_info")
    serial_number = None
    system_id = dict_robot_info["system_id"]
    if "serial_number" in dict_robot_info:
        serial_number = dict_robot_info["serial_number"]
    if "device_id" in dict_robot_info and serial_number is None:
        device_id = dict_robot_info["device_id"]
        valid_device = verify_device_id_dao(device_id=device_id, system_id=system_id)
        if not valid_device:
            return error(1015)
    else:
        device_id = None

    try:
        if serial_number is None:
            robot_data = get_robot_dao(system_id, device_id=device_id)
        else:
            robot_data = get_robot_dao(system_id, serial_number=serial_number)
        return create_response(robot_data)
    except (IntegrityError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_robots_by_system_list(system_id_list):
    """
    Returns list of all robots given for system id list
    :param system_id_list: list
    :return: str
    """
    logger.debug("In get_robots_by_system_list")
    try:
        robot_data = get_robots_by_systems_dao(system_id_list=system_id_list)
        return create_response(robot_data)
    except (IntegrityError, InternalError):
        return error(2001)


@log_args_and_response
def get_robots_by_company_id(company_id):
    """
    Returns list of all robots given for company_id
    :param company_id: int
    :return: str
    """
    logger.debug("In get_robots_by_company_id")
    try:
        robot_data = get_robot_data_dao(company_id=company_id)
        return create_response(robot_data)
    except (IntegrityError, InternalError):
        return error(2001)


# def get_robot_data(system_id):
#     """ Get all the robot units  for the given pharmacy_id and client_id
#
#         Args:
#             system_id (int): The system id
#         Returns:
#            json: success or error response in json
#
#         Examples:
#             >>> get_robot_data(1)
#                 []
#     """
#     robot_data = {}
#     try:
#         for record in DeviceMaster.db_get(system_id):
#             robot_data[record["id"]] = record["name"]
#     except IntegrityError as e:
#         logger.error(e, exc_info=True)
#         return error(2001)
#     except InternalError as e:
#         logger.error(e, exc_info=True)
#         return error(2001)
#
#     return robot_data


@log_args
def get_device_type_data(data_dict):
    """
    To obtain unique device types
    @param data_dict: dict
    @return: json
    """
    logger.debug("In get_device_type_data")
    try:
        device_type_info = {"device_types": list()}
        device_type_query = get_device_type_data_dao(data_dict=data_dict)

        for record in device_type_query:
            device_type_info['device_types'].append(record)

        logger.info(device_type_info)
        return create_response(device_type_info)

    except IntegrityError as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args
def get_device_data(data_dict):
    """
    To obtain device data
    @param data_dict:
    @return:
    """
    logger.debug("In get_device_data")
    try:
        trolley_data = get_device_data_dao(data_dict=data_dict)
        logger.info(trolley_data)
        return create_response(trolley_data)

    except IntegrityError as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except KeyError as e:
        logger.error(e, exc_info=True)
        return error(1001, e)


@log_args_and_response
@validate(required_fields=["device_id", "user_id"])
def update_device(args):
    """
    Function to update data in device master.
    @param args:
    @return:
    """
    logger.debug("In update_device")
    device_id = args.pop('device_id', None)
    system_id = args.pop('system_id', None)
    associated_device = args.get("associated_device", None)
    logger.info(args)

    try:

        if associated_device:
            """Checks if associated_device is already associated with other trolley"""
            try:
                device_data = get_device_master_data_dao(associated_device=associated_device)
                if device_data.id and device_data.id != device_id:
                    return error(1000, "Device already associated.")
            except DoesNotExist:
                pass

        if not system_id:
            args['system_id'] = get_system_id_by_device_id_dao(device_id=device_id)
        args['modified_by'] = args.pop('user_id')
        args['modified_date'] = get_current_date_time()
        response = update_device_data_dao(robot_info=args, device_id=device_id)
        logger.info(response)
        return create_response(response)

    except Exception as e:
        logger.info(e)
        return error(1001)


@validate(required_fields=["device_id", "user_id", "ip_address"])
@log_args_and_response
def update_id_address(args):
    """
        :param: list
        :return: str
        """
    logger.debug("In update_id_address")
    try:
        device_id = args['device_id']
        ip_address = args['ip_address']
        user_id = args['user_id']
        update_dict = {"ip_address": ip_address, "modified_by": user_id, "modified_date": get_current_date_time()}
        response = update_device_data_dao(robot_info=update_dict, device_id=device_id)
        logger.info(response)
        return create_response(response)
    except (IntegrityError, InternalError):
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id", "name", "serial_number",
                           "version", "user_id", "device_type"])
def add_device_data(dict_robot_info):
    logger.debug("In add_device_data")
    """ Takes the dict_robot_info and adds a new device in the database

        Returns:
           json: success or error response in json

        Examples:
            >>> add_device_data({})
                []
    """
    system_id = dict_robot_info.pop('system_id', None)
    device_type = dict_robot_info["device_type"]

    try:
        robot_data = get_device_master_data_dao(serial_number=dict_robot_info["serial_number"])
        if robot_data.system_id == system_id:
            return create_response(
                "Device with serial number {} already added".format(dict_robot_info["serial_number"]))
        else:
            return error(1021)
    except DoesNotExist:  # no robot found for serial number so proceed
        pass

    try:
        dict_robot_info["system_id"] = system_id
        dict_robot_info["device_type_id"] = settings.DEVICE_TYPES[device_type]
        dict_robot_info["active"] = settings.is_device_active
        record = add_device_data_dao(device_info=dict_robot_info)
        logger.info(str(record))
        return create_response(record)

    except (InternalError, IntegrityError):
        return error(2001)
    except DataError:
        return error(1020)


@log_args_and_response
def get_disabled_locations(device_ids=None, company_id=None, container_numbers=None):
    """
    Gets all records of disabled location for given device ids, company_id or container_numbers

    @param device_ids: Device IDs
    @param company_id: Company ID
    @param container_numbers: container_numbers
    :return: json
    """
    logger.debug("In get_disabled_locations")
    # disabled_locations = list()
    if device_ids:  # check for device ids
        device_ids = list(map(lambda x: int(x), device_ids.split(",")))
    else:
        device_ids = None
    if container_numbers:  # check for device ids
        container_numbers = container_numbers.split(",")

    #     validate device_ids and company_id
    logger.debug("validating device_ids {} and company_id {}".format(device_ids, company_id))
    if device_ids and company_id:
        valid_devices = validate_device_ids_with_company(device_ids=device_ids, company_id=company_id)
        if not valid_devices:
            logger.error("Invalid device ID(s) {} or company_id {}".format(device_ids, company_id))
            return error(9059)
    logger.debug(
        "validated device_ids {} and company_id {} and fetching disabled locations".format(device_ids, company_id))
    try:
        disabled_locations = db_get_disabled_locations(device_ids=device_ids, company_id=company_id,
                                                       drawer_numbers=container_numbers)
        return create_response(disabled_locations)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["location", "device_id", "user_id"])
def disable_canister_location(location_info):
    """
    Disables location of device if no canister is present at that location

    @param location_info: dict
    :return: json
    input args:
    {'company_id': 3, 'user_id': 13, 'device_id': 3, 'location': ['M7-8']}
    {'company_id': 3, 'user_id': 13, 'device_id': 3, 'location': ['M5-1', 'M5-2', 'M5-3', 'M5-4', 'M5-5', 'M5-6', 'M5-7', 'M5-8']}
    """
    logger.debug("In disable_canister_location")
    logger.debug("disable_canister_location: location_info - {}".format(location_info))
    location_info["created_by"] = location_info.pop("user_id")
    location_list = location_info["location"]
    location_list = location_list if isinstance(location_list, list) else [location_list]
    device_id = location_info["device_id"]
    analysis_ids = location_info.get("analysis_ids", None)
    if not "comment" in location_info:
        location_info["comment"] = "N.A."
    try:
        # display location sent in get api so changing to display location
        try:
            location_id_list = get_location_id_by_display_location_list_dao(device_id,  location_list)
        except DoesNotExist:
            return error(3009)

        try:  # If canister present, throw error
            canister_info = get_canister_present_on_location(location_id_list=location_id_list)
            if canister_info:
                return error(3004)
        except DoesNotExist:
            pass  # No canister present, can disable location

        disabled_locations_dict = disabled_locations_dao(location_id_list)

        for location in disabled_locations_dict.keys():
            location_id_list.remove(location)

        if not location_id_list:
            return error(3005)


        location_info.pop('location')

        location_info_list: list = list()
        disable_loc_dict: dict = dict()
        for location in location_id_list:
            disable_loc_dict['loc_id'] = location
            disable_loc_dict['start_time'] = get_current_date_time()
            disable_loc_dict['comment'] = location_info['comment']
            disable_loc_dict['created_by'] = location_info['created_by']
            disable_loc_dict['created_date'] = disable_loc_dict['start_time']

            location_info_list.append(disable_loc_dict.copy())

        logger.debug("Adding record in disable_location_history and updating ")
        with db.transaction():
            disabled_location_id = locations_to_be_disabled(disable_info_dict_list=location_info_list,
                                                            locations_to_disable=location_id_list)
            logger.debug("Record added in disable_location_history with id - {}".format(disabled_location_id))
            if analysis_ids is not None:
                update_status = update_pack_analysis_details(analysis_ids)
                logger.info("In disable_canister_location: pack analysis details updated: {}".format(update_status))
        response = {"already_disabled_locations": list(disabled_locations_dict.values()),
                    "locations_disabled": disabled_location_id}
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(1020)


@log_args_and_response
@validate(required_fields=["device_id", "location", "user_id"])
def save_disabled_location_transfers(dict_info):
    """

    @param dict_info:dict
    @return: json
    """
    logger.debug("In save_disabled_location_transfers")
    device_id = dict_info["device_id"]
    location = dict_info["location"]
    user_id = dict_info["user_id"]
    drug = dict_info.get("drug", None)
    disable = dict_info.get("disable", 0)
    enable = dict_info.get("enable", 0)
    comment = dict_info.get("reason_disabled_loc", "motor not working")

    if enable:
        try:
            set_location_enable = None
            for display_location in location.split(','):
                set_location_enable = set_location_enable_dao(device_id=device_id, display_location=display_location)
                logger.info(set_location_enable)
            if "failure" in str(set_location_enable):
                return set_location_enable
            else:
                return create_response(settings.SUCCESS_RESPONSE)
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001, e)

    if disable:
        canister_present_location_dict = dict()
        location_info_list = list()
        already_disabled_loc = list()
        set_location_disable = None
        valid_display_location = list()
        try:
            display_locations = location.split(',')
            canister_loc_info = get_location_canister_data_by_display_location(device_id, display_locations)
            for record in canister_loc_info:
                valid_display_location.append(record['display_location'])
                if record['is_disabled']:
                    already_disabled_loc.append(record['display_location'])
                    continue
                if record['canister_id']:
                    canister_present_location_dict[record['display_location']] = {
                        'canister_id': record['loc_id'],
                        'canister_rfid': record['rfid']}
                else:
                    location_info = {"comment": comment,
                                     "created_by": user_id,
                                     "loc_id": record['loc_id'],
                                     "start_time": get_current_date_time()}
                    location_info["created_date"] = location_info['start_time']
                    location_info_list.append(location_info)

            if location_info_list:
                set_location_disable = set_location_disable_dao(disable_info_list=location_info_list)
            return create_response({'disable_location': set_location_disable,
                                    'already_disabled_loc': already_disabled_loc,
                                    'canister_present_location': canister_present_location_dict,
                                    'invalid_display_location': list(set(display_locations) - set(valid_display_location))})

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001, e)

    # This is not in use
    if drug is not None:
        try:
            all_manual_analysis_ids = []
            drug_list = deque(drug.split(','))
            location_list = location.split(',')
            system_id = get_system_id_by_device_id_dao(device_id=device_id)
            batch_id = get_progress_batch_id(system_id=system_id)
            pack_list = get_pack_list_by_robot(batch_id, device_id)
            logger.debug(pack_list)
            if len(pack_list) != 0:
                for location in location_list:
                    quad = get_quadrant_from_device_location_dao(device_id=device_id, location=location)
                    drug = drug_list.popleft()
                    manual_analysis_ids = get_manual_analysis_ids(quad, drug, pack_list)
                    all_manual_analysis_ids.extend(manual_analysis_ids)
                if all_manual_analysis_ids:
                    # if manual_analysis_ids:
                    print(all_manual_analysis_ids)
                    status = update_pack_analysis_details(analysis_ids=all_manual_analysis_ids)
                    logger.info("In save_disabled_location_transfers: pack analysis details updated: {}".format(status))
            update_replenish_based_on_device(device_id)
            return create_response(1)
        except DoesNotExist as e:
            logger.error(e)
            logger.info('Not valid device')
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001, e)
        except ValueError as e:
            return error(2005, str(e))


@log_args_and_response
@validate(required_fields=["station_type", "station_id"])
def api_callback_v3(args):
    """
    Function to differentiate rfid callback coming from different stations
    @param args: dict
    @return: json
    """
    try:
        station_type = int(args["station_type"])

        if station_type == constants.CSR_SERIAL_NUMBER and "eeprom_dict" in args:
            # when call is to update canister location placed or moved from csr
            response = update_csr_canister(args)
        elif station_type == constants.CSR_SERIAL_NUMBER and "status" in args:
            # when call is to update status(open-1 or close-0) of drawer of csr
            response = csr_emlock_status_callback_v3(args)
        elif station_type == constants.MFS_SERIAL_NUMBER:
            # when call is to update mfd canister location when placed or moved from mfs
            response = mfs_rfid_callback(args)
        else:
            return error(1001, "Invalid Input parameters {}.".format(args))

        return response
    except Exception as e:
        logger.info(e)
        return error(1001, "Error in updating location.")


@log_args_and_response
@validate(required_fields=["station_type", "station_id", "status"])
def csr_emlock_status_callback_v3(request_args):
    """
    Function called when there is status update call for station
    @param request_args: dict
    @return: json
    """
    try:
        emlock_status = bool(int(request_args['status']))
        station_type = int(request_args['station_type'])
        station_id = int(request_args['station_id'])

        if station_id >= 1:
            # find actual station id based on even and odd station id concept i.e, for station id 1,2
            # actual station id should be 1 in case of csr like wise for 3,4 actual station id should be 2 and so on
            if station_id % 2 == 0:
                # Got call from secondary pcb with status 1 only in case of power up so ignore the call as
                # emlock is connected only with primary pcb, so we have to consider calls from primary pcb only
                logger.info("csr_emlock_status_callback_v3: ignoring emlock status call from secondary pcb")
                return create_response(data="Ignored emlock status call as it was from secondary PCB of CSR drawer.")
            else:
                actual_station_id = int((station_id + 1) / 2)
        else:
            return error(1000, "Invalid station_id.")

        # fetch container_id based on station_type and station_id
        logger.debug("fetching container_id based on station_type and station_id")
        # container_id = None
        try:
            # get container serial number based on station_type and station_id
            container_serial_number = get_serial_number_by_station_type_and_id(station_type=int(station_type),
                                                                               station_id=str(actual_station_id),
                                                                               container_serial_number=True,
                                                                               device_serial_number=False)
        except ValueError as e:
            logger.error(e)
            return error(9062)
        # fetch container_data based on container serial number
        container_data = get_container_data_based_on_serial_numbers_dao(serial_numbers=[container_serial_number])
        if not container_data:
            return error(9063)

        container_id = None
        device_id = None
        # container_name = None

        for container in container_data:
            if container["serial_number"] == container_serial_number:
                container_id = container["id"]
                device_id = container["device_id"]
                # container_name = container["drawer_name"]
                break

        if not container_id or not device_id:
            return error(9063)

        logger.debug("fetched container_id {} and now fetching company_id of device".format(container_id))
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        company_id = device_data.company_id
        logger.debug("updating em_lock_status of container in database for container_id- " + str(container_id))
        with db.transaction():
            # update lock_status based on container_id
            response = update_container_lock_status(container_id=container_id, emlock_status=emlock_status)
            logger.debug("response of em_lock_status update in container_master for container {} is {}: "
                         .format(container_id, response))
            if response:
                # update couch db for drawer open and close status- add drawer_name when open and remove when close
                couch_db_update_status = update_couch_db_for_drawer_status(company_id=company_id,
                                                                           device_id=device_id,
                                                                           container_id=container_id,
                                                                           lock_status=emlock_status)
                logger.info("In csr_emlock_status_callback_v3: couch db updated for drawer: {}".format(couch_db_update_status))
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DoesNotExist as e:
        logger.error("Error in csr_emlock_status_callback_v3:{}".format(e))
        return error(9063)
    except DataError as e:
        logger.error("Error in csr_emlock_status_callback_v3:{}".format(e))
        return error(1020)
    except RealTimeDBException:
        return error(11002)


@log_args_and_response
def callback_couch_db_data_update(batch_id, user_id, mfs_id, couch_db_canister_data,
                                  system_id, couch_db_drawer_data, trolley_id,
                                  company_id, mfd_data, original_doc, system_device_trolley_dict):
    try:
        reset_couch_db_data = False
        mfd_data['data']['update_rfid_timestamp'] = get_current_date_time()
        if not batch_id:
            logger.debug('batch_not_found')
        mfd_data['data']['canister_data'] = couch_db_canister_data
        pending_error = False
        for can_data in couch_db_canister_data.values():
            pending_error = pending_error or can_data['is_in_error']
        mfd_data['data']['drawer_data'] = couch_db_drawer_data
        scanned_drawer = mfd_data['data'].get('scanned_drawer', None)
        drawer_serial_number = couch_db_drawer_data[0] if couch_db_drawer_data else None
        if drawer_serial_number and scanned_drawer and scanned_drawer != drawer_serial_number:
            mfd_data["data"]["previously_scanned_drawer"] = scanned_drawer
        if batch_id:
            mfd_data, reset_couch_db_data = canister_batch_update(mfd_data, batch_id, user_id, mfs_id, pending_error, system_id,
                                                                  company_id, trolley_id)
        else:
            if not pending_error:
                mfd_data['data']['canister_data'] = {}

        logger.info('couch_db_data' + str(mfd_data))
        status, doc = update_document_with_revision(original_doc, mfd_data, reset_couch_db_data)
        if not status:
            raise ValueError(error(11002))
        if system_device_trolley_dict:
            logger.info('system_device_trolley_dict: {}'.format(system_device_trolley_dict))
            for canister_system_id, device_trolley_dict in system_device_trolley_dict.items():
                for dest_device_id, trolley_list in device_trolley_dict.items():
                    if canister_system_id and dest_device_id and trolley_list:
                        update_timestamp_mfd_transfer_doc(canister_system_id, dest_device_id, trolley_list)
    except RealTimeDBException as e:
        raise RealTimeDBException
    except (InternalError, IntegrityError) as e:
        raise e


@log_args_and_response
def update_mfs_data(rfid_dict: dict, mfs_id: int, user_id: int, couch_db_canister_data: dict, scanned_drawer: int,
                    trolley_id: int, trolley_name: str, system_device_trolley_dict: dict) -> tuple:
    """
    updates current location of mfd-canister, updates history data, updates transfer done status in temp_mfd_filling table
    and formats couch-db data for error in placement
    @param rfid_dict: callback info
    @param mfs_id: device id
    @param user_id: user by whom the actions are being performed
    @param couch_db_canister_data: display info for user
    @param scanned_drawer: drawer scanned by user
    @param trolley_id: trolley whose canisters are being filled
    @param trolley_name: name of the trolley
    :return:
    @param system_device_trolley_dict:
    """
    try:
        canister_mfs_association_dict = dict()
        mfd_canister_master_dict = dict()
        canister_history_update = list()
        temp_filling_transfer_done = list()
        acitvate_mfd_can_dict = defaultdict(list)

        # location and canister info for current placement of data
        batch_id, current_mfs_batch, canister_location_mapping = get_current_mfs_batch_data(mfs_id)
        logger.info('current_mfs_data: ' + str(current_mfs_batch))
        logger.info('iterating_over_dict')
        exclude_location = list()
        for loc, rfid in rfid_dict.items():
            loc = str(int(loc) + 1)
            try:
                # get location id from location number and device id(manual fill station)
                location_id = get_location_id_by_location_number_dao(device_id=mfs_id, location_number=loc)
            except NoLocationExists as e:
                logger.error(e)
                return error(1020, 'Invalid location.')
            if rfid == settings.NULL_RFID_CSR:
                rfid = None

            logger.debug("{} - RFID: {}".format(constants.TEMP_MFD_LOGS, rfid))
            # if canister is removed from a location
            if not rfid:
                # canister that is placed on the location from which canister is removed(null rfid call received)
                current_canister_data = get_canister_data_by_location_id(location_id)
                logger.debug("{} - current_canister_data: {}".format(constants.TEMP_MFD_LOGS, current_canister_data))
                if not current_canister_data:
                    # if no canister is present then skipping the calculation
                    continue
                # checks if for current mini batch given location required canister filling
                if current_mfs_batch.get(loc, None):
                    # checks if any canister is associated with location
                    associated_canister_id = current_mfs_batch[loc]['canister_id']
                    if associated_canister_id == current_canister_data['id']:
                        # if filling is done for given canister then below blocks get executed
                        if current_mfs_batch[loc]['status'] in [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                                constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                constants.MFD_CANISTER_FILLED_STATUS,
                                                                constants.MFD_CANISTER_VERIFIED_STATUS]:
                            # if correct drawer is scanned for putting canister back to trolley or once the canister
                            # transfer is done successfully then canister's placed in trolley else
                            if ((scanned_drawer and (int(scanned_drawer) == int(current_mfs_batch[loc]['drawer_id']))) or
                                (current_mfs_batch[loc]['status'] == constants.MFD_CANISTER_SKIPPED_STATUS)) or \
                                    (current_mfs_batch[loc]['transfer_done']):
                                if current_mfs_batch[loc]['status'] == constants.MFD_CANISTER_SKIPPED_STATUS:
                                    analysis_id = current_mfs_batch[loc]['analysis_id']
                                    canister_mfs_association_dict[analysis_id] = None
                                mfd_canister_master_dict[current_mfs_batch[loc]['canister_id']] = \
                                    current_mfs_batch[loc]['trolley_location_id']
                                logger.debug("IF Regular {} - mfd_canister_master_dict: {}, scanned_drawer: {}, "
                                             "current MFS Batch Status: {} "
                                             .format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict, scanned_drawer,
                                                     current_mfs_batch[loc]['status']))
                                history_dict = {
                                    'mfd_canister_id': current_mfs_batch[loc]['canister_id'],
                                    'current_location_id': current_mfs_batch[loc]['trolley_location_id'],
                                    'user_id': user_id
                                }
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': None,
                                    'error_message': None,
                                    'is_in_error': False,
                                    'transfer_done': True,
                                    'message_location': None,
                                    'required_canister_id': current_mfs_batch[loc]['canister_id']})
                                temp_filling_transfer_done.append(current_mfs_batch[loc]['analysis_id'])
                            # based on weather drawer is scanned or not error messages are formed and canister is
                            # considered to be on shelf
                            else:
                                # message_location = None
                                if scanned_drawer:
                                    error_message = constants.MFD_ERROR_MESSAGES['WRONG_DRAWER_SCANNED'] \
                                        .format(associated_canister_id)

                                else:
                                    error_message = constants.MFD_ERROR_MESSAGES['DRAWER_SCAN_REQ'] \
                                        .format(associated_canister_id)

                                logger.debug("{} - Process location update for MFD canister: {}, State Status: {}, "
                                             "Temp Filling ID: {},  Status ID: {}".
                                             format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict,
                                                    current_canister_data['state_status'],
                                                    current_canister_data['temp_filling_id'],
                                                    current_canister_data['status_id']))
                                updated_location = None
                                if current_canister_data['state_status'] != constants.MFD_CANISTER_INACTIVE:
                                    if current_canister_data['temp_filling_id'] and current_canister_data['transfer_done']:
                                        updated_location = current_canister_data['trolley_location_id']
                                    elif current_canister_data['temp_filling_id'] is None and current_canister_data[
                                        'status_id'] \
                                            in [constants.MFD_CANISTER_FILLED_STATUS,
                                                constants.MFD_CANISTER_VERIFIED_STATUS,
                                                constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                constants.MFD_CANISTER_DROPPED_STATUS,
                                                constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                        if current_canister_data['status_id'] \
                                                in [constants.MFD_CANISTER_FILLED_STATUS,
                                                    constants.MFD_CANISTER_VERIFIED_STATUS]:
                                            updated_location = current_canister_data['trolley_location_id']
                                            exclude_location.append(updated_location)
                                        elif current_canister_data['status_id'] \
                                                in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                    constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                            # check if location is empty
                                            if current_canister_data['is_loc_empty']:
                                                updated_location = current_canister_data['trolley_location_id']
                                                exclude_location.append(updated_location)
                                            else:
                                                updated_location = get_empty_location_by_drawer_level(
                                                    current_canister_data['home_cart_id'],
                                                    settings.MFD_TROLLEY_FILLED_DRAWER_LEVEL,
                                                    exclude_location)
                                                exclude_location.append(updated_location)
                                        elif current_canister_data['status_id'] in \
                                                [constants.MFD_CANISTER_MVS_FILLED_STATUS, constants.MFD_CANISTER_DROPPED_STATUS]:
                                            updated_location = get_empty_location_by_trolley(
                                                current_canister_data['home_cart_id'], exclude_location)

                                            exclude_location.append(updated_location)
                                else:
                                    updated_location = None
                                mfd_canister_master_dict[current_mfs_batch[loc]['canister_id']] = updated_location
                                # mfd_canister_master_dict[current_mfs_batch[loc]['canister_id']] = None

                                logger.debug("IF scanned_drawer {} - mfd_canister_master_dict: {}, scanned_drawer: {}, "
                                             "error_message: {}".format(constants.TEMP_MFD_LOGS,
                                                                        mfd_canister_master_dict, scanned_drawer,
                                                                        error_message))
                                history_dict = {
                                    'mfd_canister_id': current_mfs_batch[loc]['canister_id'],
                                    'current_location_id': updated_location,
                                    'user_id': user_id,
                                }
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': None,
                                    'error_message': error_message,
                                    'is_in_error': True,
                                    'message_location':
                                        canister_location_mapping[current_mfs_batch[loc]['canister_id']][
                                            'display_location'],
                                    'required_canister_id': current_mfs_batch[loc]['canister_id']})
                            canister_history_update.append(history_dict)
                        # if canister is removed before filling then it's drug status is checked. If any drug is filled
                        # then association in mfdanalysis is kept and error is updated in couch-db else the association
                        # is removed
                        else:
                            analysis_id = current_mfs_batch[loc]['analysis_id']
                            drug_status = list(map(lambda x: int(x), current_mfs_batch[loc]['drug_status'].split(",")))
                            if constants.MFD_DRUG_FILLED_STATUS not in drug_status:
                                canister_mfs_association_dict[analysis_id] = None
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': None,
                                    'error_message': None,
                                    'is_in_error': False,
                                    'message_location': None,
                                    'required_canister_id': None})
                            else:
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': None,
                                    'error_message': constants.MFD_ERROR_MESSAGES['MISSING_CAN']
                                        .format(current_mfs_batch[loc]['canister_id']),
                                    'is_in_error': True,
                                    'message_location':
                                        canister_location_mapping[current_mfs_batch[loc]['canister_id']][
                                            'display_location'],
                                    'required_canister_id': current_mfs_batch[loc]['canister_id']})

                            logger.debug("{} - Process location update for MFD canister: {}, State Status: {}, "
                                         "Temp Filling ID: {},  Status ID: {}".
                                         format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict,
                                                current_canister_data['state_status'],
                                                current_canister_data['temp_filling_id'],
                                                current_canister_data['status_id']))
                            updated_location = None
                            if current_canister_data['state_status'] != constants.MFD_CANISTER_INACTIVE:
                                if current_canister_data['temp_filling_id'] and current_canister_data['transfer_done']:
                                    updated_location = current_canister_data['trolley_location_id']
                                elif current_canister_data['temp_filling_id'] is None and current_canister_data[
                                    'status_id'] \
                                        in [constants.MFD_CANISTER_FILLED_STATUS,
                                            constants.MFD_CANISTER_VERIFIED_STATUS,
                                            constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                            constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                            constants.MFD_CANISTER_DROPPED_STATUS,
                                            constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                    if current_canister_data['status_id'] \
                                            in [constants.MFD_CANISTER_FILLED_STATUS,
                                                constants.MFD_CANISTER_VERIFIED_STATUS]:
                                        updated_location = current_canister_data['trolley_location_id']
                                        exclude_location.append(updated_location)
                                    elif current_canister_data['status_id'] \
                                            in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                        # check if location is empty
                                        if current_canister_data['is_loc_empty']:
                                            updated_location = current_canister_data['trolley_location_id']
                                            exclude_location.append(updated_location)
                                        else:
                                            updated_location = get_empty_location_by_drawer_level(
                                                current_canister_data['home_cart_id'],
                                                settings.MFD_TROLLEY_FILLED_DRAWER_LEVEL,
                                                exclude_location)
                                            exclude_location.append(updated_location)
                                    elif current_canister_data['status_id'] in [constants.MFD_CANISTER_MVS_FILLED_STATUS, constants.MFD_CANISTER_DROPPED_STATUS]:
                                        updated_location = get_empty_location_by_trolley(
                                            current_canister_data['home_cart_id'], exclude_location)

                                        exclude_location.append(updated_location)
                            else:
                                updated_location = None
                            mfd_canister_master_dict[current_mfs_batch[loc]['canister_id']] = updated_location
                            # mfd_canister_master_dict[current_mfs_batch[loc]['canister_id']] = None

                            logger.debug("IF drug_status {} - mfd_canister_master_dict: {}, couch_db_canister_data: {}".
                                         format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict,
                                                couch_db_canister_data))
                            history_dict = {
                                'mfd_canister_id': current_mfs_batch[loc]['canister_id'],
                                'current_location_id': updated_location,
                                'user_id': user_id
                            }
                            canister_history_update.append(history_dict)
                    # If associated canister is different from the current canister then below block gets executed
                    else:
                        system_device_trolley_dict[current_canister_data['system_id']][current_canister_data['dest_device_id']]\
                            .append(current_canister_data['trolley_id'])
                        current_canister_id = current_canister_data['id']
                        updated_location = None
                        # if canister is one of the canister being used in current 16 placement then it's transfer done
                        # status is checked and if transfer is done then
                        if current_canister_data['state_status'] != constants.MFD_CANISTER_INACTIVE:
                            if current_canister_data['temp_filling_id'] and current_canister_data['transfer_done']:
                                updated_location = current_canister_data['trolley_location_id']
                            elif current_canister_data['temp_filling_id'] is None and current_canister_data['status_id'] \
                                    in [constants.MFD_CANISTER_FILLED_STATUS,
                                        constants.MFD_CANISTER_VERIFIED_STATUS,
                                        constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                        constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                        constants.MFD_CANISTER_DROPPED_STATUS,
                                        constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                if current_canister_data['status_id'] \
                                    in [constants.MFD_CANISTER_FILLED_STATUS,
                                        constants.MFD_CANISTER_VERIFIED_STATUS]:
                                    updated_location = current_canister_data['trolley_location_id']
                                    exclude_location.append(updated_location)
                                elif current_canister_data['status_id'] \
                                    in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                        constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                    # check if location is empty
                                    if current_canister_data['is_loc_empty']:
                                        updated_location = current_canister_data['trolley_location_id']
                                        exclude_location.append(updated_location)
                                    else:
                                        updated_location = get_empty_location_by_drawer_level(
                                            current_canister_data['home_cart_id'],
                                            settings.MFD_TROLLEY_FILLED_DRAWER_LEVEL,
                                            exclude_location)
                                        exclude_location.append(updated_location)
                                elif current_canister_data['status_id'] in [constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                        constants.MFD_CANISTER_DROPPED_STATUS]:
                                    updated_location = get_empty_location_by_trolley(current_canister_data['home_cart_id'], exclude_location)

                                    exclude_location.append(updated_location)
                        mfd_canister_master_dict[current_canister_id] = updated_location
                        logger.debug("{} - mfd_canister_master_dict: {} Updated Location: {}".
                                     format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict, updated_location))

                        history_dict = {
                            'mfd_canister_id': current_canister_id,
                            'current_location_id': updated_location,
                            'user_id': user_id
                        }
                        canister_history_update.append(history_dict)
                        if couch_db_canister_data.get(loc, None):
                            transfer_done = couch_db_canister_data[loc]['transfer_done']
                            if transfer_done:
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': None,
                                    'error_message': None,
                                    'message_location': None,
                                    'is_in_error': False})
                            else:
                                if associated_canister_id:
                                    couch_db_canister_data[loc].update({
                                        'current_canister_id': None,
                                        'error_message': constants.MFD_ERROR_MESSAGES['MISSING_CAN']
                                            .format(current_mfs_batch[loc]['canister_id']),
                                        'is_in_error': True,
                                        'message_location':
                                            canister_location_mapping[current_mfs_batch[loc]['canister_id']][
                                                'display_location'],
                                        'required_canister_id': current_mfs_batch[loc]['canister_id']})
                                else:
                                    couch_db_canister_data[loc].update({
                                        'current_canister_id': None,
                                        'error_message': None,
                                        'message_location': None,
                                        'is_in_error': False,
                                        'required_canister_id': None})
                        else:
                            couch_db_canister_data[loc] = {
                                'current_canister_id': None,
                                'error_message': None,
                                'message_location': None,
                                'is_in_error': False,
                                'required_canister_id': None}
                else:
                    current_canister_id = current_canister_data['id']
                    updated_location = None
                    system_device_trolley_dict[current_canister_data['system_id']][current_canister_data['dest_device_id']] \
                        .append(current_canister_data['trolley_id'])
                    if not current_canister_data['state_status'] == constants.MFD_CANISTER_INACTIVE:
                        if current_canister_data['temp_filling_id'] and current_canister_data['transfer_done']:
                            updated_location = current_canister_data['trolley_location_id']
                        elif current_canister_data['temp_filling_id'] is None and current_canister_data['status_id'] \
                                 in [constants.MFD_CANISTER_FILLED_STATUS,
                                     constants.MFD_CANISTER_VERIFIED_STATUS,
                                     constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                     constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                     constants.MFD_CANISTER_DROPPED_STATUS,
                                     constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                            if current_canister_data['status_id'] \
                                    in [constants.MFD_CANISTER_FILLED_STATUS,
                                        constants.MFD_CANISTER_VERIFIED_STATUS]:
                                updated_location = current_canister_data['trolley_location_id']
                                exclude_location.append(updated_location)
                            elif current_canister_data['status_id'] \
                                    in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                        constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                                # check if location is empty
                                if current_canister_data['is_loc_empty']:
                                    updated_location = current_canister_data['trolley_location_id']
                                    exclude_location.append(updated_location)
                                else:
                                    updated_location = get_empty_location_by_drawer_level(
                                        current_canister_data['home_cart_id'],
                                        settings.MFD_TROLLEY_FILLED_DRAWER_LEVEL,
                                        exclude_location)
                                    exclude_location.append(updated_location)
                            elif current_canister_data['status_id'] in [constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                                        constants.MFD_CANISTER_DROPPED_STATUS, ]:
                                updated_location = get_empty_location_by_trolley(current_canister_data['home_cart_id'],
                                                                                 exclude_location)

                                exclude_location.append(updated_location)
                    mfd_canister_master_dict[current_canister_id] = updated_location
                    logger.debug("{} - mfd_canister_master_dict: {} Updated Location: {}".
                                 format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict, updated_location))

                    history_dict = {
                        'mfd_canister_id': current_canister_id,
                        'current_location_id': updated_location,
                        'user_id': user_id
                    }
                    canister_history_update.append(history_dict)
                    if couch_db_canister_data.get(loc, None):
                        couch_db_canister_data[loc].update({
                            'current_canister_id': None,
                            'error_message': None,
                            'message_location': None,
                            'is_in_error': False})
                    else:
                        couch_db_canister_data[loc] = {
                            'canister_required': False,
                            'current_canister_id': None,
                            'error_message': None,
                            'message_location': None,
                            'is_in_error': False,
                            'required_canister_id': None}
            # if canister is placed on any location
            else:
                current_canister_data = get_canister_data_by_rfid(rfid)
                if not current_canister_data:
                    continue
                current_canister_id = current_canister_data['id']
                home_cart = current_canister_data['home_cart_id']
                current_can_state_status = current_canister_data['state_status']
                mfd_canister_master_dict[current_canister_id] = location_id
                logger.debug("{} - mfd_canister_master_dict: {} Updated Location: {}".
                             format(constants.TEMP_MFD_LOGS, mfd_canister_master_dict, location_id))

                history_dict = {
                    'mfd_canister_id': current_canister_id,
                    'current_location_id': location_id,
                    'user_id': user_id
                }
                canister_history_update.append(history_dict)
                if current_mfs_batch.get(loc, None):
                    analysis_id = current_mfs_batch[loc]['analysis_id']
                    associated_canister_id = current_mfs_batch[loc]['canister_id']
                    canister_status = current_mfs_batch[loc]['status']
                    # check if canister is bind with particular location or not. If bounded then give error messages
                    # for invalid canister at that location. If not then check validity of currently
                    if associated_canister_id:
                        if associated_canister_id != current_canister_id:
                            system_device_trolley_dict[current_canister_data['system_id']][
                                current_canister_data['dest_device_id']] \
                                .append(current_canister_data['batch_id'])
                            # message_location = None
                            if current_canister_data['status_id'] in [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                      constants.MFD_CANISTER_DROPPED_STATUS,
                                                                      constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                                      constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                                      constants.MFD_CANISTER_PENDING_STATUS]:
                                error_message = constants.MFD_ERROR_MESSAGES['WRONG_CAN_DETECTED'] \
                                    .format(associated_canister_id)
                                message_location = current_mfs_batch[loc]['mfs_location']
                            else:
                                if current_canister_data['status_id'] != constants.MFD_CANISTER_IN_PROGRESS_STATUS:
                                    if current_canister_data['transfer_done'] or \
                                            current_canister_id not in canister_location_mapping:
                                        error_message = constants.MFD_ERROR_MESSAGES['TROLLEY_PLACEMENT_REQUIRED'] \
                                            .format(current_canister_data['id'],
                                                    current_canister_data['trolley_drawer_name'],
                                                    current_canister_data['trolley_name'])
                                        message_location = current_canister_data['trolley_drawer_name']
                                    else:
                                        error_message = constants.MFD_ERROR_MESSAGES['WRONG_PLACEMENT'] \
                                            .format(current_canister_id,
                                                    canister_location_mapping[current_canister_id]['display_location'])
                                        message_location = canister_location_mapping[current_canister_id][
                                            'display_location']

                                else:
                                    error_message = constants.MFD_ERROR_MESSAGES['WRONG_CAN_DETECTED'] \
                                        .format(associated_canister_id)
                                    message_location = current_mfs_batch[loc]['mfs_location']
                            couch_db_canister_data[loc].update({
                                'current_canister_id': current_canister_id,
                                'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                                'error_message': error_message,
                                'is_in_error': True,
                                'message_location': message_location,
                                'required_canister_id': associated_canister_id})
                        else:
                            if current_canister_data['transfer_done']:
                                error_message = constants.MFD_ERROR_MESSAGES['TROLLEY_PLACEMENT_REQUIRED'] \
                                    .format(current_canister_data['id'],
                                            current_canister_data['trolley_drawer_name'],
                                            current_canister_data['trolley_name'])
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': current_canister_id,
                                    'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                                    'error_message': error_message,
                                    'is_in_error': True,
                                    'transfer_done': True,
                                    'message_location': current_canister_data['trolley_drawer_name'],
                                    'required_canister_id': current_canister_id})
                            else:
                                couch_db_canister_data[loc].update({
                                    'current_canister_id': current_canister_id,
                                    'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                                    'error_message': None,
                                    'is_in_error': False,
                                    'transfer_done': False,
                                    'message_location': None,
                                    'required_canister_id': current_canister_id})
                    else:
                        system_device_trolley_dict[current_canister_data['system_id']][current_canister_data['dest_device_id']] \
                            .append(current_canister_data['trolley_id'])
                        # check if canister is required on a particular location or not. If required then validate else
                        # return no can required error message
                        if canister_status != constants.MFD_CANISTER_SKIPPED_STATUS:
                            # checking validity of canister
                            error_message = None
                            is_in_error = False
                            message_location = None
                            if current_can_state_status == constants.MFD_CANISTER_INACTIVE:
                                error_message = constants.MFD_ERROR_MESSAGES['DEACTIVATE_CANISTER']
                                is_in_error = True
                            elif home_cart != trolley_id:
                                error_message = constants.MFD_ERROR_MESSAGES['WRONG_HOME_CART'].format(trolley_name)
                                logger.debug("{} - error_message: {}".format(constants.TEMP_MFD_LOGS, error_message))

                                is_in_error = True
                            elif home_cart == trolley_id and not current_canister_data['status_id'] or \
                                    current_canister_data['status_id'] in [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                           constants.MFD_CANISTER_DROPPED_STATUS,
                                                                           constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                                           constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                                           constants.MFD_CANISTER_PENDING_STATUS]:
                                canister_mfs_association_dict[analysis_id] = current_canister_id
                                system_device_trolley_dict[current_mfs_batch[loc]['system_id']][
                                    current_mfs_batch[loc]['dest_device_id']] \
                                    .append(current_mfs_batch[loc]['trolley_id'])
                                if current_can_state_status == constants.MFD_CANISTER_MISPLACED:
                                    acitvate_mfd_can_dict[home_cart].append(current_canister_id)
                            else:
                                if canister_location_mapping.get(current_canister_id, None):
                                    error_message = constants.MFD_ERROR_MESSAGES['WRONG_PLACEMENT'] \
                                        .format(current_canister_id,
                                                canister_location_mapping[current_canister_id]['display_location'])
                                    is_in_error = True
                                    message_location = canister_location_mapping[current_canister_id][
                                        'display_location']
                                else:
                                    if home_cart != trolley_id:
                                        error_message = constants.MFD_ERROR_MESSAGES['WRONG_HOME_CART'].format(
                                            trolley_name)
                                        logger.debug(
                                            "{} - error_message: {}".format(constants.TEMP_MFD_LOGS, error_message))

                                        is_in_error = True
                                    else:
                                        error_message = constants.MFD_ERROR_MESSAGES['TROLLEY_PLACEMENT_REQUIRED'] \
                                            .format(current_canister_data['id'],
                                                    current_canister_data['trolley_drawer_name'],
                                                    current_canister_data['trolley_name'])
                                        is_in_error = True
                                        message_location = current_canister_data['trolley_drawer_name']
                            couch_db_canister_data[loc].update({
                                'current_canister_id': current_canister_id,
                                'transfer_done': False,
                                'error_message': error_message,
                                'is_in_error': is_in_error,
                                'message_location': message_location,
                                'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                                'required_canister_id': current_canister_id})
                        else:
                            couch_db_canister_data[loc].update({
                                'current_canister_id': current_canister_id,
                                'error_message': constants.MFD_ERROR_MESSAGES['NO_CAN_REQ'],
                                'message_location': None,
                                'is_in_error': True,
                                'required_canister_id': None})
                else:
                    system_device_trolley_dict[current_canister_data['system_id']][current_canister_data['dest_device_id']] \
                        .append(current_canister_data['trolley_id'])
                    # The data will not be available if no placement was required at that location
                    couch_db_canister_data[loc] = {
                        'canister_required': False,
                        'is_in_error': True,
                        'current_canister_id': current_canister_id,
                        'required_canister_id': None,
                        'message_location': None,
                        'error_message': constants.MFD_ERROR_MESSAGES['NO_CAN_REQ']
                    }

        if mfd_canister_master_dict:
            status = update_mfd_canister_location(mfd_canister_master_dict)
            logger.info(status)

        if canister_mfs_association_dict:
            status = associate_canister_with_analysis(canister_mfs_association_dict)
            logger.info(status)

        if canister_history_update:
            print(canister_history_update)
            status = update_mfd_canister_history(canister_history_update)
            logger.info(status)

        if temp_filling_transfer_done:
            status = mfd_update_transfer_done(temp_filling_transfer_done)
            logger.info("In update_mfs_data: mfd canister transfer status updated: {}".format(status))

        if acitvate_mfd_can_dict:
            update_status = mfd_canister_found_update_status(acitvate_mfd_can_dict, user_id)
            logger.info("In update_mfs_data: mfd_canister_found_update_status: {}".format(update_status))

        return batch_id, couch_db_canister_data, system_device_trolley_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def fetch_and_update_data(mfs_id: int, update_dict: dict, rfid_dict: dict, mfs_data: object, count: int = 1) -> int:
    """
    fetches current couch-db data and updates accordingly
    :param mfs_id:
    :param update_dict:
    :param rfid_dict:
    :param mfs_data:
    :param count:
    :return:
    """
    if not rfid_dict:
        return error(1001, "Missing Parameter(s): eeprom_dict.")

    try:
        with db.transaction():
            status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                          system_id=mfs_data.system_id)
            couch_db_doc = document.get_document()
            logger.info('current_couch_db_data' + str(couch_db_doc))
            couch_db_canister_data = couch_db_doc["data"].get('canister_data', {})
            trolley_id = couch_db_doc["data"].get('trolley_id', None)
            trolley_name = couch_db_doc["data"].get('name', None)
            user_id = couch_db_doc["data"].get('user_id', 1)
            scanned_drawer = couch_db_doc["data"].get('scanned_drawer', None)
            system_device_trolley_dict = defaultdict(lambda: defaultdict(list))
            if update_dict:
                batch_id, couch_db_canister_data, system_device_trolley_dict = update_mfs_data(update_dict, mfs_id, user_id,
                                                                   couch_db_canister_data, scanned_drawer,
                                                                   trolley_id, trolley_name, system_device_trolley_dict)

            batch_id, couch_db_canister_data, system_device_trolley_dict = update_mfs_data(rfid_dict, mfs_id, user_id,
                                                               couch_db_canister_data, scanned_drawer,
                                                               trolley_id, trolley_name, system_device_trolley_dict)

            if not batch_id:
                batch_id = couch_db_doc["data"].get('batch_id', None)
            couch_db_drawer_data = get_mfs_transfer_drawer_data(mfs_id)
            callback_couch_db_data_update(batch_id, user_id, mfs_id,
                                          couch_db_canister_data=couch_db_canister_data,
                                          system_id=mfs_data.system_id,
                                          couch_db_drawer_data=couch_db_drawer_data,
                                          trolley_id=trolley_id,
                                          company_id=mfs_data.company_id,
                                          mfd_data=couch_db_doc,
                                          original_doc=document, system_device_trolley_dict=system_device_trolley_dict)
            return status
    except RealTimeDBException as e:
        logger.error(e)
        if count >= 3:
            raise RealTimeDBException
        else:
            count += 1
            fetch_and_update_data(mfs_id, update_dict, rfid_dict, mfs_data, count=count)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
@validate(required_fields=["station_type", "station_id", "eeprom_dict"])
def mfs_rfid_callback(request_args):
    """
    updates current location of mfd-canister and updates history data.
    updates couch-db document for pending canister count, valid canister placement and quadrant data for LED blink
    :param request_args: dict
    :return: json
    """

    rfid_dict = request_args.get("eeprom_dict", None)
    station_type = int(request_args["station_type"])
    station_id = str(request_args["station_id"])

    if not rfid_dict:
        return error(1001, "Missing Parameter(s): eeprom_dict.")

    try:
        with db.transaction():
            serial_number = get_serial_number_by_station_type_and_id(station_type=station_type,
                                                                     station_id=station_id,
                                                                     container_serial_number=False,
                                                                     device_serial_number=True)

            try:
                mfs_data = get_mfs_device_data(serial_number)
                print('mfs_data ', mfs_data.system_id)
                logger.info('mfs_data system_id: ' + str(mfs_data.system_id) + ' mfs_id: ' + str(mfs_data.id))
            except DoesNotExist as e:
                logger.error(e)
                return error(1020, 'No such device.')
            mfs_id = mfs_data.id

            update_dict = dict()
            # builds extra dictionary in case any callback is missing
            # i.e. canister located on location 2 is having canister_id: 1234 but location 2 has canister having: 2134
            # and/or canister_id: 1234 was previously on location 1 of mfs and rfid callback for removal is not received

            logger.debug('{} - rfid_dict: {}'.format(constants.TEMP_MFD_LOGS, rfid_dict))
            for loc, rfid in rfid_dict.items():
                if rfid == settings.NULL_RFID_CSR:
                    rfid = None
                if rfid:
                    loc = str(int(loc) + 1)
                    try:
                        location_id = get_location_id_by_location_number_dao(device_id=mfs_id, location_number=loc)
                    except NoLocationExists as e:
                        logger.error(e)
                        return error(1020, 'Invalid location.')
                    # checks the current location of canister. If it is on mfs then null rfid callback is added on that
                    # location
                    current_canister_data = get_canister_data_by_rfid(rfid)
                    logger.debug('{} - current_canister_data: {}'.format(constants.TEMP_MFD_LOGS, current_canister_data))

                    if current_canister_data and current_canister_data['current_device_type_id'] == \
                            settings.DEVICE_TYPES['Manual Filling Device']:
                        if serial_number == current_canister_data['current_serial_number']:
                            update_dict[current_canister_data['current_loc_number'] - 1] = settings.NULL_RFID_CSR

                    # checks if the location has canister present on it then removed previous canister callback is
                    # added.
                    current_location_data = get_canister_data_by_location_id(location_id)
                    if current_location_data:
                        if rfid != current_location_data['rfid']:
                            update_dict[int(loc) - 1] = settings.NULL_RFID_CSR

            logger.debug('update_dict_extra_data: {}'.format(update_dict))
            status = fetch_and_update_data(mfs_id, update_dict, rfid_dict, mfs_data)
            return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["station_type", "station_id", "eeprom_dict"])
def update_csr_canister(request_args):
    """
    Function to update canister data when placed or moved from csr
    @param request_args: dict
    @return: json
    """
    try:
        loc_rfid_dict = request_args.get("eeprom_dict", None)
        station_type = int(request_args["station_type"])
        station_id = int(request_args["station_id"])
        canister_location_dict = dict()

        if not loc_rfid_dict:
            return error(1001, "Missing Parameter(s): eeprom_dict")

        if station_id >= 1:
            # find actual station id based on even and odd station id concept i.e, for station id 1,2
            # actual station id should be 1 in case of csr like wise for 3,4 actual station id should be 2 and so on
            if station_id % 2 == 0:
                actual_station_id = int(station_id / 2)
            else:
                actual_station_id = int((station_id + 1) / 2)
        else:
            return error(1000, "Invalid station_id.")

        # if station id is even then its secondary pcb else primary pcb
        pcb_id = constants.SECONDARY_PCB_ID if station_id % 2 == 0 else constants.PRIMARY_PCB_ID
        try:
            logger.debug("generating serial number based on station type and station id")
            # get container serial number based on station_type and station_id
            container_serial_number = get_serial_number_by_station_type_and_id(station_type=int(station_type),
                                                                               station_id=str(actual_station_id),
                                                                               container_serial_number=True,
                                                                               device_serial_number=False)
            logger.debug("Serial number generated: " + str(container_serial_number))
        except KeyError as e:
            logger.error(e)
            return error(9062)

        logger.debug("fetching container data based on serial number: " + str(container_serial_number))
        # fetch container_data based on container serial number
        container_data = get_container_data_based_on_serial_numbers_dao(serial_numbers=[container_serial_number])
        if not container_data:
            return error(9062)
        logger.debug("container_data fetched: " + str(container_data))
        container_name = None
        device_id = None
        container_id = None
        for container in container_data:
            if container["serial_number"] == container_serial_number:
                container_name = container["drawer_name"]
                device_id = container["device_id"]
                container_id = container["id"]
                break
        if not container_name or not device_id:
            return error(9063)

        for key, value in loc_rfid_dict.items():
            # get display_location_number based on location in loc_rfid dict
            display_location_number = int(key)
            if int(pcb_id) == constants.SECONDARY_PCB_ID:
                display_location_number = constants.LOCATIONS_PER_PCB_IN_CSR + int(key)

            # generate display_location based on drawer_name and display_location_number
            display_location = ''.join(str(container_name).split('-')) + '-' + str(display_location_number)
            logger.debug("display_location for location: {} of container {}".format(str(display_location),
                                                                                    str(container_name)))

            # fetch location_id based on display_location and container_id
            location_id = get_location_id_by_display_location_dao(device_id=device_id, location=display_location)
            logger.debug("fetched location_id {} for display_location {}".format(str(location_id), display_location))
            # fetching device data
            logger.debug("fetching device_data based on device_id: " + str(device_id))
            device_data = get_device_data_by_device_id_dao(device_id=device_id)
            system_id = device_data.system_id
            company_id = device_data.company_id
            logger.debug(
                "fetched device_data and now fetching current logged_in user_id from couch db for system: " + str(
                    system_id))
            # fetch user_id of user logged in in current system
            user_id = get_logged_in_user_from_couch_db_of_system(company_id=company_id, system_id=system_id)
            logger.debug("current logged_in user_id {} fetched for system: ".format(user_id, system_id))
            # for guided flow get canister location info

            # update location in canister master
            canister_location_update_status = csr_location_canister_rfid_update(rfid_location_dict={value: location_id},
                                                                                user_id=user_id, device_id=device_id,
                                                                                system_id=system_id,
                                                                                status_to_update=None)
            logger.info(canister_location_update_status)
            logger.debug("canister master updated for rfid: {} with location: {}".format(value, str(location_id)))

            # update couch db is call is during guided transfer flow
            couch_db_update_status, new_loc_id = verify_csr_canister_location_and_update_couch_db(canister_location_dict, system_id,
                                                                                      device_id, user_id)
            logger.info("couch_db_update_status {}".format(couch_db_update_status))

            # update couch db for canister location update(placement or removal from drawer)
            couch_db_update_status = update_couch_db_for_drawer_status(company_id=company_id,
                                                                       device_id=device_id,
                                                                       container_id=container_id,
                                                                       lock_status=False,
                                                                       canister_status=True)
            logger.info("In update_csr_canister: update_couch_db_for_drawer_status {}".format(couch_db_update_status))

        return create_response(True)
    except (IntegrityError, InternalError) as e:
        logger.error(e)
        return error(2001)
    except DoesNotExist as e:
        logger.error(e)
        return error(9063)
    except DataError as e:
        logger.error(e)
        return error(1020)
    except CanisterNotExist:
        return error(1032)
    except CanisterNotPresent:
        return error(3010)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error while updating canister location in csr- " + str(e))


@log_args_and_response
def verify_csr_canister_location_and_update_couch_db(canister_info, system_id, device_id, user_id, manual_transfer=False):
    """
    Function to verify if canister update is during guided transfer flow and update couch db
    accordingly
    @param user_id:
    @param manual_transfer:
    @param canister_info: dict
    @param system_id: int
    @param device_id: int
    @return: status
    """
    try:
        guided_history_list = list()
        system_device_dict = dict()
        new_loc_id = None

        for canister, canister_location_info in canister_info.items():
            canister_removed = canister_location_info['canister_removed']
            canister_data = db_get_latest_guided_canister_transfer_data(canister)
            if canister_data:
                if not canister_removed:
                    # case when canister is placed in csr
                    if canister_location_info['device_to_update'] == canister_data['dest_device'] and \
                            not (canister_location_info["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                 canister_location_info["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):
                        if canister_data["transfer_status"] == constants.GUIDED_TRACKER_SKIPPED_AND_REPLACED:
                            done_transfer_status = constants.GUIDED_TRACKER_SKIPPED_AND_DONE
                        else:
                            done_transfer_status = constants.GUIDED_TRACKER_DONE
                        update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
                                                                     done_transfer_status)
                        logger.info("In verify_csr_canister_location_and_update_couch_db : guided tracker status updated{}".format(update_status))
                        # add data in guided transfer cycle history tables
                        insert_data = {'guided_tracker_id': canister_data['guided_tracker_id'],
                                       'canister_id': canister,
                                       'action_id': constants.GUIDED_TRACKER_TRANSFER_ACTION,
                                       'current_status_id': done_transfer_status,
                                       'previous_status_id': canister_data['transfer_status'],
                                       'action_taken_by': user_id,
                                       'action_datetime': get_current_date_time()
                                       }

                        guided_history_list.append(insert_data)

                elif canister_removed:
                    # args = {"device_id": device_id, "system_id": system_id}
                    # currently_scanned_drawer_id = fetch_scanned_drawer_in_guided_tx_flow(args=args)
                    # if currently_scanned_drawer_id:
                    #     empty_locations_of_scanned_drawer = get_empty_locations_of_drawer(
                    #         drawer_id=currently_scanned_drawer_id)
                    #     if empty_locations_of_scanned_drawer:
                    #         new_loc_id = empty_locations_of_scanned_drawer.pop(0)
                    logger.debug("guided_replenish - removed source or alternate canister from csr or on shelf to trolley- {}".format(canister))
                    new_loc_id = canister_data["cart_location_id"]
                    status = assign_cart_location_to_canister(canister, new_loc_id)
                    logger.info("assign_cart_location_to_canister {}".format(status))
                    if canister_data["guided_meta_status"] == constants.GUIDED_META_DRUG_BOTTLE_FETCHED:
                        update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
                                                                     constants.GUIDED_TRACKER_TO_TROLLEY_DONE)
                        logger.info("update_guided_tracker_status status {}".format(update_status))


                # update couch db according to current wizard
                system_device_dict[system_id] = device_id
                if canister_data['dest_device'] != device_id:
                    system_device_dict[canister_data["dest_system_id"]] = canister_data['dest_device']
                logger.info(
                    "verify_canister_location_and_update_couch_db system_device_dict {}".format(system_device_dict))

                if not manual_transfer:
                    for cdb_system_id, cdb_device_id in system_device_dict.items():
                        couch_db_update = guided_transfer_couch_db_timestamp_update(cdb_system_id, cdb_device_id)
                        logger.info("couch_db_update {}".format(couch_db_update))

                else:
                    logger.info("No need to update couch_db")

        #  add guided transfer history data in transfer history tables
        if len(guided_history_list):
            response = add_data_in_guided_transfer_cycle_history(insert_data=guided_history_list)
            logger.info("add_data_in_guided_transfer_cycle_history response {}".format(response))

        return True, new_loc_id

    except Exception as e:
        logger.error("Error in verify_csr_canister_location_and_update_couch_db {}".format(e))
        return False, None


@log_args
def get_device_drawer_data(company_id, system_id=None, device_id=None, station_type=None, station_id=None,
                           serial_number=None):
    try:
        device_data, drawer_data = get_device_drawer_info(company_id,
                                                          system_id=system_id,
                                                          device_id=device_id,
                                                          station_type=station_type,
                                                          station_id=station_id,
                                                          serial_number=serial_number)
        response = {
            'device_data': device_data,
            'drawer_data': drawer_data
        }

        return create_response(response)
    except IntegrityError as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_device_shelf_data(device_id):
    """
    Function to get list of shelf from device_id
    @param device_id: int
    @return: list of shelf's
    """
    try:
        logger.debug("In get_device_shelf_data")
        shelf_list = list()
        data_dict = get_device_shelf_info(device_id)
        if len(data_dict):
            shelf_list = [int(item['shelf']) for item in data_dict]

        return shelf_list

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args
def get_enabled_locations(device_ids: str = None, company_id: int = None, container_numbers: str = None) -> dict:
    """
    Gets all records of enabled location for given device ids, company_id or container_numbers

    @param device_ids: Device IDs
    @param company_id: Company ID
    @param container_numbers: container_numbers
    :return: json
    """
    logger.debug("In get_enabled_locations")
    if device_ids:  # check for device ids
        device_ids: list = eval(device_ids)
    if container_numbers:  # check for container numbers
        container_numbers = container_numbers.split(",")

    # validate device_ids and company_id
    logger.debug("validating device_ids {} and company_id {}".format(device_ids, company_id))
    if device_ids and company_id:
        valid_devices = validate_device_ids_with_company(device_ids=device_ids, company_id=company_id)
        if not valid_devices:
            logger.error("Invalid device ID(s) {} or company_id {}".format(device_ids, company_id))
            return error(9059)
    logger.debug(
        "validated device_ids {} and company_id {} and fetching enabled locations".format(device_ids, company_id))
    try:
        enabled_locations: list = db_get_enabled_locations(device_ids=device_ids, company_id=company_id,
                                                           drawer_numbers=container_numbers)
        return create_response(enabled_locations)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args
def get_disabled_drawers(device_id: int, company_id: int) -> dict:
    """
    This method fetches the disabled drawers if all the locations of a drawer are disabled.
    @param device_id:
    @param company_id:
    @return:
    """
    logger.debug("Inside get_disabled_drawers")
    locations_per_drawer: int
    response_dict: dict
    try:
        # validate if the given device_id belongs to the given company_id
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

        # get the number of locations per drawer
        locations_per_drawer = get_locations_per_drawer(device_id)

        # get the list of disabled drawers
        disabled_drawers = get_disabled_drawers_by_device(device_id=device_id,
                                                          locations_per_drawer=locations_per_drawer)

        response_dict = {"disabled_drawers": disabled_drawers}

        return create_response(response_dict)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def csr_location_canister_rfid_update(rfid_location_dict: dict, user_id: int, device_id: int, system_id: int,
                                      status_to_update: [int, None]) -> int:
    try:
        # check if call is to place a canister at a location where another canister is already present,
        # if so then remove the existing canister first
        canister_remove_dict = dict()
        canister_location_dict = dict()
        for rfid, location_id in rfid_location_dict.items():
            if rfid != constants.NULL_RFID_CSR:
                logger.debug("rfid is not null so checking if any canister present at current location")
                # call is to place the canister so check if any canister present at loc location_id
                try:
                    canister_data = db_get_canister_data_by_location_id_dao(location_id=location_id)
                    if canister_data:
                        logger.debug("canister found at location - {}: {}".format(location_id, canister_data))
                        #  add data in canister_remove_dict
                        canister_remove_dict[constants.NULL_RFID_CSR] = location_id
                except CanisterNotPresent:
                    logger.debug("No canister present at given location")
                    continue

        if canister_remove_dict:
            updated_rfid_location_dict = canister_remove_dict
            updated_rfid_location_dict.update(rfid_location_dict)
        else:
            updated_rfid_location_dict = rfid_location_dict

        for rfid, location_id in updated_rfid_location_dict.items():

            # fetching location info initially as we are updating location_id value later on
            location_info = get_location_info_from_location_id(location_id=location_id)
            if location_info:
                canister_location_dict = get_canister_location_from_display_location(
                                                                {location_info["display_location"]: rfid}, device_id)

            # if rfid is not 0000 or null
            if rfid != constants.NULL_RFID_CSR:
                # placing canister
                # fetch canister data based on rfid
                try:
                    canister_data = get_canister_data_by_rfid_dao(rfid=rfid)
                except CanisterNotExist:
                    raise
                # update location id in canister master based on rfid
                update_status = update_canister_location_based_on_rfid(location_id=location_id, rfid=rfid)
                # update current location id in canister history if current loc id is null in the latest entry else add new record
                if update_status:
                    # To update current location in canister history
                    latest_canister_history_record = get_canister_history_latest_record_can_id_dao(
                        canister_id=canister_data["id"])
                    if latest_canister_history_record is not None:
                        # record available in canister history
                        if latest_canister_history_record.current_location_id is None \
                                and latest_canister_history_record.previous_location_id is not None:
                            # update current location id in the latest record
                            update_history_dict = {"current_location_id": location_id,
                                                   "modified_by": user_id,
                                                   "modified_date": get_current_date_time()
                                                   }
                            can_history_update_status = update_canister_history_by_id_dao(update_history_dict,
                                                                                          latest_canister_history_record.id)
                            logger.info("In csr_location_canister_rfid_update: canister history is updated by id: {}".format(can_history_update_status))
                        else:
                            # add new record
                            canister_history_dict = {
                                "canister_id": canister_data["id"],
                                "current_location_id": location_id,
                                "previous_location_id": latest_canister_history_record.current_location_id,
                                "created_by": user_id,
                                "modified_by": user_id,
                                "modified_date": get_current_date_time()
                            }
                            create_canister_history_record(data=canister_history_dict, get_or_create=False)
                    else:
                        canister_history_dict = {
                            "canister_id": canister_data["id"],
                            "current_location_id": location_id,
                            "previous_location_id": canister_data["location_id"],
                            "created_by": user_id,
                            "modified_by": user_id,
                            "modified_date": get_current_date_time()
                        }
                        create_canister_history_record(data=canister_history_dict, get_or_create=False)
            else:
                # removing canister
                # fetch canister data based on location id
                try:
                    canister_data = db_get_canister_data_by_location_id_dao(location_id=location_id)
                except CanisterNotPresent:
                    raise
                # update location_id = None as we are removing canister from given location
                update_status = update_canister_location_based_on_rfid(location_id=None,
                                                                       rfid=canister_data["rfid"])
                # add record in canister history with prev loc id as location id and current loc id as none
                if update_status:
                    canister_history_dict = {
                        "canister_id": canister_data["id"],
                        "current_location_id": None,
                        "previous_location_id": location_id,
                        "created_by": user_id,
                        "modified_by": user_id,
                        "modified_date": get_current_date_time()
                    }
                    create_canister_history_record(data=canister_history_dict, get_or_create=False)
                    location_id = None  # as current canister is removed from given location id

            if update_status:
                # update timestamp for canister transfer flow
                couchdb_update_status = update_canister_count_in_canister_transfer_couch_db(system_id=system_id,
                                                                                            canister_id=canister_data["id"],
                                                                                            source_device=device_id,
                                                                                            dest_loc_id=location_id,
                                                                                            user_id=user_id,
                                                                                            dest_device_type_id=settings.DEVICE_TYPES["CSR"],
                                                                                            previous_location=None,
                                                                                            status_to_update=status_to_update)
                logger.info("csr_location_canister_rfid_update: update canister count in canister transfer couchdb {}".format(couchdb_update_status))
                # update timestamp for guided transfer flow
                if canister_location_dict:
                    logger.debug("csr: updating timestamp in guided flow")
                    couch_db_update_status, new_loc_id = verify_csr_canister_location_and_update_couch_db(
                                                                    canister_location_dict, system_id, device_id, user_id)
                    logger.info("couch_db_update_status {}".format(couch_db_update_status))
        return True
    except (IntegrityError, InternalError, Exception) as e:
        raise e


def update_timestamp_mfd_transfer_doc(system_id, device_id, trolley_list):
    """

    :return:
    """
    try:
        status, couch_db_doc = get_mfd_transfer_couch_db(device_id, system_id)
        couch_db_data = couch_db_doc.get("data", {})
        trolley_id = couch_db_data.get("scanned_trolley", None)
        misplaced_count = couch_db_data.get("misplaced_count", None)
        if trolley_id in trolley_list:
            mfd_data = {'timestamp': get_current_date_time(),
            'uuid': uuid1().int,
            'misplaced_count': misplaced_count+1}
            update_mfd_transfer_couch_db(device_id, system_id, mfd_data)
    except (IntegrityError, InternalError, Exception) as e:
        raise e


@validate(required_fields=['company_id', 'device_id', 'display_location'])
def enable_location(request_args):
    """
    enables location
    """
    company_id = request_args['company_id']
    device_id = request_args['device_id']
    display_location = request_args['display_location']

    try:
        with db.transaction():
            # validate the device_id for the given company
            valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
            if not valid_device:
                return error(1033)

            # mark location as enable in location master
            for each_location in display_location:
                set_location_enable = set_location_enable_dao(device_id=device_id, display_location=each_location)
                logger.info("set_location_enable_dao response {}".format(set_location_enable))

            return create_response(settings.SUCCESS_RESPONSE)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)


@log_args_and_response
def get_canister_location_from_display_location(location_rfid_dict, device_id):
    """

    @param location_rfid_dict:
    @param device_id:
    @return:
    """
    # todo reduce the loop
    try:
        logger.info("get_location_no_from_display_location {}".format(location_rfid_dict))
        canister_location_dict = dict()

        for display_location, rfid in location_rfid_dict.items():
            location_info_updated = get_location_info_from_display_location(device_id=device_id,
                                                                            display_location=display_location)

            logger.info("Location info {}".format(location_info_updated))

            if location_info_updated['drawer_type'] == settings.SIZE_OR_TYPE["MFD"]:
                continue

            if not rfid or rfid == settings.NULL_RFID_CSR:
                canister_info = db_get_canister_data_by_location_id_dao(location_id=location_info_updated['id'])
                canister_id = canister_info['id']
                location_info = location_info_updated
                location_info['canister_removed'] = True

            else:
                # canister_id = CanisterMaster.get_canister_id_by_rfid(rfid=rfid)
                canister_id = db_check_canister_available_dao(rfid=rfid)

                location_info = db_get_current_canister_based_on_location(location_info_updated['id'])

                if not canister_id:
                    logger.debug("get_canister_location_from_display_location: Found wrong rfid")
                    if location_info:
                        logger.debug("get_canister_location_from_display_location: "
                                     "Garbage value found while removing canister.")
                        canister_id = location_info["canister_id"]
                        location_info = location_info_updated
                        location_info['canister_removed'] = True
                    else:
                        return {}
                else:
                    logger.debug("get_canister_location_from_display_location: placing canister in robot")
                    location_info = db_get_current_canister_location(canister_id)
                    location_info['location_to_update'] = location_info_updated['id']
                    location_info['canister_removed'] = False
                    location_info['quadrant_to_update'] = location_info_updated['quadrant']
                    location_info['device_to_update'] = location_info_updated['device_id']
                    location_info["drawer_type"] = location_info_updated["drawer_type"]

            canister_location_dict[canister_id] = location_info

        logger.info("canister_location_dict {}".format(canister_location_dict))
        return canister_location_dict

    except Exception as e:
        logger.error("Error in get_canister_location_from_display_location: {}".format(e))
        return {}