import datetime
import functools
import json
import operator
import settings
import os
import sys
from collections import OrderedDict
from copy import deepcopy
from typing import Optional, List
from dosepack.base_model.base_model import db
from dosepack.validation.validate import validate
from src import constants
from peewee import (InternalError, IntegrityError, DoesNotExist, DataError)
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, convert_dob_date_to_sql_date, \
    is_date, log_args, get_current_datetime_by_timezone, get_next_date_by_timezone, get_utc_time_offset_by_time_zone, \
    get_current_date_time
from src.constants import MVS_OTHER, MVS_DRUGS_OUT_OF_STOCK, MVS_MISSING_PILLS
from src.dao.batch_dao import get_batch_status, get_progress_batch_id, get_pack_ids_for_batch, db_update_mfd_status, \
    db_update_batch_id_after_merged
from src.dao.crm_dao import get_packs_count_for_all_batches, get_all_batch_pack_queue_data, \
    get_drug_info_from_canister_list_pack_queue, get_manual_drug_info_from_drug_list_pack_queue, \
    get_total_packs_of_batch, get_mfd_pack_data, get_automatic_pack_record, \
    get_pending_facility_data, get_pending_packs_per_robot, get_number_of_drugs_in_pack, \
    get_pack_details_by_pack_id, get_mfd_devices, get_pack_count_by_device_id, check_notification_sent_or_not, \
    get_done_pack_count, \
    get_pending_pack_data_by_batch, \
    get_pending_packs_data_by_batch, get_manual_packs_by_batch_id, get_pack_data_for_change_pack_status, \
    get_pack_queue_by_conveyor_id_pagination_data, get_facility_data_by_batch, \
    get_facility_data_by_packs, get_device_id_for_pack_by_batch, get_pending_pack_count_of_working_day, \
    db_check_pack_with_ext_pack_details, get_count_of_done_pack_after_system_start_time, \
    get_done_pack_count_by_time_filter, get_pack_count_by_device_id_retail, db_get_trolley_wise_pack, \
    db_get_trolley_wise_pack_patient_data, get_mfs_filling_progress_trolley
from src.dao.drug_dao import get_drug_data_from_ndc
from src.dao.device_manager_dao import get_robots_by_systems_dao, get_device_name_from_device, \
    db_get_device_data_by_type, db_get_in_robot_mfd_trolley
from src.dao.ext_change_rx_dao import db_check_pack_marked_for_delete_dao, get_new_template_from_old_packs, \
    db_get_new_pack_details_for_template, logger
from src.dao.mfd_dao import db_get_mfd_packs_from_packlist, db_get_batch_mfd_packs, get_next_mfd_transfer_batch, \
    get_batch_data, get_mfd_analysis_data_by_batch, update_trolley_seq_and_merge, db_get_all_mfd_packs_from_packlist, \
    db_get_pack_queue_mfd_packs, skip_mfd_for_packs, change_mfd_trolley_sequence, \
    populate_data_in_frequent_mfd_drugs_table, remove_trolley_location, remove_notifications_for_skipped_mfs_filling
from src.dao.mfd_canister_dao import db_get_next_trolley, get_trolley_analysis_ids, db_get_last_mfd_sequence_for_batch, \
    db_check_mfd_filling_for_batch
from src.dao.misc_dao import get_packs_count_for_latest_batch, update_sequence_no_for_pre_processing_wizard, \
    get_packs_count_for_system, get_company_setting_by_company_id
from src.dao.pack_dao import get_batch_id_from_packs, get_packs_by_facility, get_filled_packs_count_for_latest_batch, \
    get_total_packs_count_for_batch, verify_pack_list_by_company_id, verify_pack_list_by_system_id, update_pack_details, \
    update_dict_pack_details, get_pack_id_list_by_status, get_order_pack_id_list, \
    get_pack_status_by_pack_list, update_batch_id_null, get_pack_order_no, \
    get_pending_order_pack_by_batch, change_pack_sequence, get_deleted_packs_by_batch, get_batch_status_wise_pack_count, \
    check_transfer_filling_pending, get_system_status_wise_pack_count, \
    get_pack_id_list_by_status_and_system, get_filled_packs_count_for_system, get_pack_order_no_by_pack_list, \
    get_pending_pack_queue_order_pack, get_patient_data_for_packs, get_db_data_for_batch_merge, merge_batch_dao, \
    get_mfd_trolley_for_pack, get_trolley_analysis_ids_by_trolley_seq, insert_record_in_reuse_pack_drug
from src.dao.pack_ext_dao import db_update_ext_packs_delivery_status_dao
from src.dao.pack_queue_dao import insert_packs_to_pack_queue, remove_pack_from_pack_queue, remove_packs_from_queue
from src.exceptions import AutoProcessTemplateException
from src.service import patient
from src.service.generate_packs import set_unit_pack_for_multi_dosage

from src.service.misc import update_timestamp_couch_db_pre_processing_wizard, get_mfd_wizard_couch_db, \
    update_mfd_transfer_wizard_couch_db, get_token, update_mfd_error_notification
from src.service.notifications import Notifications
from src.service.batch import create_batch
from src.service.pack import set_status, map_user_pack_dao
from src.service.mfd import get_mfd_notification_info, update_trolley_seq_couchdb, update_pending_mfd_assignment
from src.dao.canister_dao import update_replenish_based_on_device
from src.dao.pack_drug_dao import delete_slot_transaction
from src.service.refill_device import update_replenish_based_on_system

logger = settings.logger


@log_args_and_response
def get_packs_count_by_system(system_id: Optional[int] = None):
    """
    @return: get pack_count of the latest batch
    """
    try:
        count = get_packs_count_for_system(system_id=system_id)
        response = {"pack_count": count, "system_id": system_id}
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_count_by_system {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_for_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_count_by_system: " + str(e))



@log_args_and_response
def get_packs_count_for_batch(batch_id: Optional[int] = None, system_id: Optional[int] = None):
    """
    @return: get pack_count of the latest batch
    """
    try:
        latest_batch_id = get_progress_batch_id(system_id) if batch_id is None else batch_id
        response = get_packs_count_for_latest_batch(batch_id=latest_batch_id)
        return response

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_count_for_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_for_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_count_for_batch: " + str(e))


@validate(required_fields=["status", "system_id"])
@log_args_and_response
def get_packs_count_by_status(args):
    """
    @param args: status
    @return: dict of pack_count as key and count of packs with given status as value, batch_id, status as key and pack_count of status(key) as value
    """

    status = args['status']
    system_id = args['system_id']
    pack_count = args.get('pack_count', False)
    status_pack_count: dict = dict()
    status_new_pack_count: dict = dict()
    try:
        if type(status) == int or type(status) == str:
            status = [status]
        elif type(status) == list:
            status = status
        else:
            status = json.loads(status)
        latest_batch_id = args['batch_id'] if 'batch_id' in args and args[
            'batch_id'] is not None else get_progress_batch_id(system_id)

        if latest_batch_id is None:
            return create_response({'pack_count': 0, 'batch_id': latest_batch_id})

        logger.info("In get_packs_count_by_status: status: {}".format(status))
        logger.info("In get_packs_count_by_status: latest_batch_id: {}".format(latest_batch_id))

        if settings.DONE_PACK_STATUS in status:
            status.remove(settings.DONE_PACK_STATUS)
            done_pack_count = get_filled_packs_count_for_latest_batch(latest_batch_id=latest_batch_id)
            status_pack_count[settings.DONE_PACK_STATUS] = done_pack_count

        if len(status) == 0:
            total_pack_count = get_total_packs_count_for_batch(latest_batch_id=latest_batch_id)
            status_pack_count['batch_id'] = latest_batch_id
            status_pack_count['pack_count'] = total_pack_count
        else:
            total_pack_count = get_total_packs_count_for_batch(latest_batch_id=latest_batch_id)
            query = get_batch_status_wise_pack_count(status=status, latest_batch_id=latest_batch_id)
            for record in query.dicts():
                logger.info("In get_packs_count_by_status: record:{}".format(record))
                status_new_pack_count[record['pack_status']] = record['id']
                # status_pack_count['pack_count'] = query1.scalar()
            status_pack_count.update(status_new_pack_count)

            for each_status in status:
                if each_status not in status_pack_count:
                    status_pack_count[each_status] = 0
            status_pack_count['batch_id'] = latest_batch_id
            status_pack_count['pack_count'] = total_pack_count

        if pack_count:
            return status_pack_count

        logger.info("In get_packs_count_by_status : pack count by status {}".format(status_pack_count))
        return create_response(status_pack_count)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_packs_count_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_count_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_count_by_status: " + str(e))


@validate(required_fields=["status", "system_id"])
@log_args_and_response
def get_packs_count_by_status_by_batch(args):
    """
    @param args: status
    @return: dict of pack_count as key and count of packs with given status as value, batch_id, status as key and pack_count of status(key) as value
    """

    status = args['status']
    system_id = args['system_id']
    pack_count = args.get('pack_count', False)
    status_pack_count: dict = dict()
    status_new_pack_count: dict = dict()
    try:
        if type(status) == int or type(status) == str:
            status = [status]
        elif type(status) == list:
            status = status
        else:
            status = json.loads(status)
        latest_batch_id = args['batch_id'] if 'batch_id' in args and args[
            'batch_id'] is not None else get_progress_batch_id(system_id)

        if latest_batch_id is None:
            return create_response({'pack_count': 0, 'batch_id': latest_batch_id})

        logger.info("In get_packs_count_by_status: status: {}".format(status))
        logger.info("In get_packs_count_by_status: latest_batch_id: {}".format(latest_batch_id))

        if settings.DONE_PACK_STATUS in status:
            status.remove(settings.DONE_PACK_STATUS)
            done_pack_count = get_filled_packs_count_for_latest_batch(latest_batch_id=latest_batch_id)
            status_pack_count[settings.DONE_PACK_STATUS] = done_pack_count

        if len(status) == 0:
            total_pack_count = get_total_packs_count_for_batch(latest_batch_id=latest_batch_id)
            status_pack_count['batch_id'] = latest_batch_id
            status_pack_count['pack_count'] = total_pack_count
        else:
            total_pack_count = get_total_packs_count_for_batch(latest_batch_id=latest_batch_id)
            query = get_batch_status_wise_pack_count(status=status, latest_batch_id=latest_batch_id)
            for record in query.dicts():
                logger.info("In get_packs_count_by_status: record:{}".format(record))
                status_new_pack_count[record['pack_status']] = record['id']
                # status_pack_count['pack_count'] = query1.scalar()
            status_pack_count.update(status_new_pack_count)

            for each_status in status:
                if each_status not in status_pack_count:
                    status_pack_count[each_status] = 0
            status_pack_count['batch_id'] = latest_batch_id
            status_pack_count['pack_count'] = total_pack_count

        if pack_count:
            return status_pack_count

        logger.info("In get_packs_count_by_status : pack count by status {}".format(status_pack_count))
        return create_response(status_pack_count)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_packs_count_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_count_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_count_by_status: " + str(e))


@validate(required_fields=["system_id"])
@log_args_and_response
def get_system_packs_count_by_status(args):
    """
    @param args: status
    @return: dict of pack_count as key and count of packs with given status as value, batch_id, status as key and pack_count of status(key) as value
    """

    status = args.get('status', [2,3])
    system_id = args['system_id']
    time_zone = args.get("time_zone", None)
    system_start_time = args.get("system_start_time", None)

    status_pack_count: dict = dict()
    status_new_pack_count: dict = dict()
    try:
        if type(status) == int or type(status) == str:
            status = [status]
        elif type(status) == list:
            status = status
        else:
            status = json.loads(status)

        logger.info("In get_system_packs_count_by_status: status: {}".format(status))


        total_pack_count = get_packs_count_for_system(system_id=system_id)
        query = get_system_status_wise_pack_count(status=status, system_id=system_id)
        if 2 in status:
            status_pack_count["pending_pack_count"] = 0
        if 3 in status:
            status_pack_count["progress_pack_count"] = 0
        for record in query.dicts():
            logger.info("In get_system_packs_count_by_status: record:{}".format(record))
            if record['pack_status'] == 2:
                status_new_pack_count["pending_pack_count"] = record['id']
            if record['pack_status'] == 3:
                status_new_pack_count["progress_pack_count"] = record['id']
            status_new_pack_count[record['pack_status']] = record['id']
            # status_pack_count['pack_count'] = query1.scalar()
        status_pack_count.update(status_new_pack_count)
        for each_status in status:
            if each_status not in status_pack_count:
                status_pack_count[each_status] = 0
        status_pack_count['system_id'] = system_id
        status_pack_count['pack_count'] = total_pack_count

        day_pack_count = []


        if time_zone:
            time_zone = args.get('time_zone', 'UTC')
            time_zone = settings.TIME_ZONE_MAP[time_zone]

            system_start_time = args.get('system_start_time')
            if system_start_time:
                total_done_packs = get_count_of_done_pack_after_system_start_time(system_start_time, time_zone)
                total_done_packs = {"label": "Filled", "count": total_done_packs}
            else:
                total_done_packs = {"label": "Filled", "count": 0}

            utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
            day_pack_count = get_pending_pack_count_of_working_day(time_zone, utc_time_zone_offset)
            day_pack_count.insert(0, total_done_packs)
            status_pack_count['day_pack_count'] = day_pack_count

            logger.info(f"In get_system_packs_count_by_status, day_pack_count: {day_pack_count}")

        logger.info("In get_system_packs_count_by_status : pack count by status {}".format(status_pack_count))
        return create_response(status_pack_count)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_system_packs_count_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_system_packs_count_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(2001)

    except Exception as e:
        logger.error("Error in get_system_packs_count_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_system_packs_count_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(1000, "Error in get_system_packs_count_by_status: " + str(e))


@validate(required_fields=["status", "system_id"])
@log_args_and_response
def find_pack_id_by_status(args):
    """
    Reduce to pack count
    @param args: status
    @return: list of pack_ids having given status
    """
    system_id = args['system_id']
    device_id = args.get("device_id", None)
    pack_ids: list = list()
    batch_total_packs_list: list = list()
    automatic_packs: list = list()
    unfilled_mfd_packs: list = list()
    change_pending_pack_ids: List[int] = []
    error_code = args.get("error_code", None)

    try:
        if type(args['status']) == int or type(args['status']) == str:
            status = [args['status']]
        elif type(args['status']) == list:
            status = args['status']
        else:
            status = json.loads(args['status'])

        pack_count = get_packs_count_for_system(system_id)
        logger.info("In find_pack_id_by_status: Device Id {}".format(device_id))

        if not pack_count:
            if 'data' in args:
                return create_response({"pack_count": 0})
            else:
                return False, 0

        if device_id is not None:
            batch_total_packs_list = get_total_packs_of_batch(pack_status=status, system_id=system_id)
            pack_mfd_filled, trolley_seq, pack_trolley_seq = get_mfd_pack_data(system_id=system_id, device_id=device_id)
            query = get_automatic_pack_record(pack_status=status, system_id=system_id, device_id=device_id)

        else:
            pack_mfd_filled, trolley_seq, pack_trolley_seq = get_mfd_pack_data(system_id=system_id)
            query = get_automatic_pack_record(pack_status=status, system_id=system_id, device_id=device_id)

        for record in query:
            automatic_packs.append(record['id'])

        if automatic_packs:
            change_pending_pack_ids = db_check_pack_with_ext_pack_details(pack_list=automatic_packs)

        for each_pack in batch_total_packs_list:
            if each_pack in pack_mfd_filled.keys():
                mfd_can_info = pack_mfd_filled[each_pack]
                if pack_trolley_seq[each_pack] == trolley_seq and all([loc for loc, seq in mfd_can_info.values()]):
                    pack_ids.append(each_pack)
                else:
                    unfilled_mfd_packs.append(each_pack)
            elif each_pack in automatic_packs:
                pack_ids.append(each_pack)

        logger.info("In find_pack_id_by_status: automatic and unfilled mfd packs {} and {}".format(automatic_packs,
                                                                                                   unfilled_mfd_packs))

        """
            Dev: 16 DEC 2022
            Currently we stop mfd packs if not filled or transferred after all auto packs get filled. 
            This error is handled from robot and showed on utility.  
            We need to move this logic before dispatching packs. Packs wont be sent in progress until error is resolved. 
            If new batch is imported and auto-packs are there, this error will be converted into notification.
            
            Points to cover:
                1. All auto packs dispatched. Now if only mfd packs remains, return error to CRM.
                2. Update notification in this case as error
                3. If new batch arrives, need to check that if there is any exception like this so we will turn 
                notification error into normal error
                4. CRM will send flag once it receives error it identify that last time it was error.
            
                
        """
        if error_code and len(pack_ids):
            # remove notification
            args = {
                "system_id": system_id,
                "device_id": device_id,
                "modified_time": get_current_date_time(),
                "error_data": dict()
            }

            update_mfd_error_notification(args)
        if not len(pack_ids) and len(unfilled_mfd_packs):
            nearest_mfd_pack = unfilled_mfd_packs[0]
            # check which mfd trolley is required by the pack

            trolley_data = get_mfd_trolley_for_pack(nearest_mfd_pack)

            logger.debug('In find_pack_id_by_status; Trolley_data_for_pack_id: {} is {}'.format(nearest_mfd_pack, trolley_data))

            mfd_analysis_ids = []

            if trolley_data:
                mfd_analysis_ids, mfs_system_mapping, dest_devices, batch_system = get_trolley_analysis_ids_by_trolley_seq(
                    trolley_data['batch_id'], trolley_data['trolley_seq'])

            logger.debug(
                'In find_pack_id_by_status, mfd_analysis_ids_for_pack_id: {} are: {}'.format(nearest_mfd_pack, mfd_analysis_ids))

            if mfd_analysis_ids:
                filling_done_status, transfer_done_status, trolley_data = check_transfer_filling_pending(
                    mfd_analysis_ids=mfd_analysis_ids, device_id=device_id)

                logger.debug('find_pack_id_by_status: pack_id: {}, filling_done_status: {} and transfer_done: {}'.format(
                    nearest_mfd_pack, filling_done_status, transfer_done_status))

                if not filling_done_status or not transfer_done_status:
                    pack_status = 2  # transfer pending
                    message = 'Kindly complete the manual canister transfer flow for the {} and then retry to resume the flow.'.format(
                        trolley_data['cart_name'])
                    if not filling_done_status:
                        pack_status = 1  # filling pending
                        message = 'Kindly complete the manual canister filling flow for the {} and then retry to resume the flow.'.format(
                            trolley_data['cart_name'])

                    filling_transfer_pending = {
                        'mfd_filling_status': pack_status,
                        'cart_data': trolley_data,
                        "message": message,
                        'cart_name': trolley_data['cart_name'],
                        'cart_id': trolley_data['cart_id'],
                        'pack_id': nearest_mfd_pack,
                        'to_be_filled_by': trolley_data['to_be_filled_by']
                    }

                    args = {
                        "system_id": system_id,
                        "device_id": device_id,
                        "modified_time": get_current_date_time(),
                        "error_data": filling_transfer_pending
                    }
                    if not error_code:
                        update_mfd_error_notification(args)
                    return 2, None

        if len(unfilled_mfd_packs):
            pack_ids.extend(unfilled_mfd_packs)

        logger.debug("Remove the Change Pending Pack IDs from the regular sequence of dispatch and "
                     "move them to the end of pack sequence.")
        for change_pack in change_pending_pack_ids:
            if change_pack in pack_ids:
                pack_ids.remove(change_pack)

        if change_pending_pack_ids:
            pack_ids.extend(change_pending_pack_ids)

        logger.info("In find_pack_id_by_status: Pack list {}".format(pack_ids))

        if not automatic_packs and not pack_mfd_filled and unfilled_mfd_packs:
            pass
            # todo : BatchRemoval define this while modifying mfd floe
            # mfd_notification_info = get_mfd_notification_info(system_id=system_id,
            #                                                   device_id=device_id)

        status = True if len(pack_ids) > 0 else False
        if 'data' in args:
            return create_response(pack_ids)
        else:
            return status, pack_ids

    except (InternalError, IntegrityError) as e:
        logger.error("error in find_pack_id_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in find_pack_id_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in find_pack_id_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in find_pack_id_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in find_pack_id_by_status: " + str(e))


@log_args_and_response
def get_pending_facility_list(system_id: int, batch_list: Optional[list] = None):
    """
    @return: list of facility name that are pending
    """
    facility_names: list = list()
    try:
        if not batch_list:
            batch_id = get_progress_batch_id(system_id=system_id)
            if batch_id is None:
                return facility_names
            batch_list = [batch_id]
        logger.info(" In get_pending_facility_list: batch_list: {}".format(batch_list))
        facility_names = get_pending_facility_data(batch_list=batch_list)
        logger.info("In get_pending_facility_list: facility names {}".format(facility_names))
        return facility_names

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pending_facility_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pending_facility_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pending_facility_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pending_facility_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pending_facility_list: " + str(e))


@validate(required_fields=["status", "system_id"])
@log_args_and_response
def get_packs_per_robot_by_status(args):
    """
    @param args: status
    @return: dict having robot_id and pack_list as key , robot id and packs as value
    """
    status = args['status']
    system_id = args['system_id']
    device_id = args.get("device_id", None)

    try:
        batch_id = get_progress_batch_id(system_id) if 'batch_id' not in args else args['batch_id']
        logger.info("IN get_packs_per_robot_by_status: batch_id:{}".format(batch_id))
        logger.info("IN get_packs_per_robot_by_status: device_id:{}".format(device_id))
        if batch_id is None:
            if 'data' in args:
                return create_response({'batch_id': batch_id, "pack_count": 0})
            else:
                return False, 0

        if status == settings.PENDING_PACK_STATUS or status is None:
            status = settings.PENDING_PACK_STATUS

        if type(status) == int or type(status) == str:
            pack_status = [status]
        elif type(status) == list:
            pack_status = status
        else:
            pack_status = json.loads(status)

        logger.info("In get_packs_per_robot_by_status: pack_status".format(pack_status))
        pending_pack_per_robot = get_pending_packs_per_robot(pack_status=pack_status, batch_id=batch_id, device_id=device_id)

        if 'data' in args:
            return create_response(pending_pack_per_robot)
        else:
            return True, pending_pack_per_robot

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_packs_per_robot_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_per_robot_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_per_robot_by_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_per_robot_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_per_robot_by_status: " + str(e))


@validate(required_fields=["pack_id", "car_id", "user_id", "system_id"])
@log_args_and_response
def assign_car_id_for_pack(args):
    """
    @param args: pack_id, car_id, user_id, system_id
    @return: updates car id for given pack id
    """
    pack_id = args['pack_id']
    car_id = args['car_id']
    pack_rfid = args['rfid'] if 'rfid' in args else None
    company_id = args['company_id']
    system_id = args['system_id']
    user_id = args['user_id']
    update_dict = {}
    update_dict['car_id'] = car_id
    batch_id = get_progress_batch_id(system_id)
    dry_run = bool(int(args.get("dry_run", 0)))

    if dry_run:
        logger.info("dry run")
        dummy_response = {"no_of_drugs": 1}
        return create_response(dummy_response)

    if company_id:
        valid_pack_list = verify_pack_list_by_company_id(pack_list=[pack_id], company_id=company_id)
        if not valid_pack_list:
            return error(1026)
    if system_id:
        valid_pack_list = verify_pack_list_by_system_id(pack_list=[pack_id], system_id=system_id)
        if not valid_pack_list:
            return error(1014)

    # commented for now because pack rfid will be a garbage value
    # if pack_rfid is not None:
    #     update_dict['rfid'] = pack_rfid
    try:
        with db.transaction():
            status = update_pack_details(update_dict=update_dict, pack_id=pack_id)
            logger.info("In assign_car_id_for_pack: update pack details: {}".format(status))

            no_of_drugs = get_number_of_drugs_in_pack(pack_id=pack_id, system_id=system_id)
            response = {"no_of_drugs": no_of_drugs}

            return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in assign_car_id_for_pack: {},Duplicate RFID {} for pack_id {}".format(e, pack_rfid, pack_id))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in assign_car_id_for_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in assign_car_id_for_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in assign_car_id_for_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in assign_car_id_for_pack: " + str(e))


@validate(required_fields=["user_id", "company_id", "system_id", "status", "system_id"])
@log_args_and_response
def change_pack_status(args):
    """
    @param args: pack id, status
    @return: updates the status as given for given pack_id
    """
    logger.debug("In change_pack_status")

    pack_id_list = args['pack_id_list'] if 'pack_id_list' in args else []
    system_id = args['system_id']
    # batch_id = get_progress_batch_id(system_id=system_id)
    # args['batch_id'] = batch_id
    args["call_from_client"] = True
    dry_run = bool(int(args.get("dry_run", 0)))
    filled_at = args.get('filled_at', None)
    forced_pack_manual = args.get('forced_pack_manual', False)
    pack_status_list = args['filter_by_status'] if 'filter_by_status' in args else []

    logger.info("In change_pack_status: pack_list {}".format(pack_id_list))

    if dry_run:
        return create_response({'system_id': system_id, "pack_count": 0, "robot_pack_data": []})

    if dry_run :
        args1 = {"system_id": system_id}
        dry_run_count = json.loads(get_packs_count_by_system(system_id))
        dummy_response = {'system_id': system_id, 'robot_pack_data': [],
                          'pack_count': dry_run_count['data']['pack_count']}
        dummy_response['robot_pack_data'].extend(get_packs_count_by_robot_id(args1))
        logger.info("response of change_pack_status {}".format(dummy_response))
        return create_response(dummy_response)

    # if batch_id is None:
    #     logger.info("In change_pack_status: response of change_pack_status batch_id is none")
    #     return create_response({'batch_id': batch_id, "pack_count": 0, "robot_pack_data": []})

    if args['status'] in [settings.DONE_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS] \
            and filled_at is None:
        logger.error("error in change_pack_status missing param filled at")
        return error(1001, "Missing Parameter(s): filled_at")

    try:
        pack_id_list_to_update = get_pack_data_for_change_pack_status(pack_id_list, system_id, pack_status_list)
        args['pack_id'] = pack_id_list_to_update
        response = json.loads(set_status(args))

        if 'require_robot_data' in args:
            if args['require_robot_data']:
                args1 = {"system_id": system_id}
                response['robot_pack_data'] = []
                response['robot_pack_data'].extend(get_packs_count_by_robot_id(args1))

        if 'delete_slot' in args:
            if args['delete_slot']:
                for each_pack in args['pack_id']:
                    delete_slot_transaction({'pack_id': each_pack, 'system_id': args['system_id']})

        logger.info("In change_pack_status: response of change_pack_status {}".format(response))
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in change_pack_status {}".format(e))
        return error(2001)


@validate(required_fields=["status", "system_id"])
@log_args_and_response
def get_pack_id_list_from_packs_by_status(args):
    """
    @param args: pack status
    @return: list of pack ids for given status
    """
    system_id = args['system_id']
    update_status = args['update_status'] if 'update_status' in args else None
    pack_id_list = json.loads(args['pack_id_list']) if args['pack_id_list'] is not None else None
    logger.info("In get_pack_id_list_from_packs_by_status: pack_id_list: {}".format(pack_id_list))

    try:
        if type(args['status']) == int or type(args['status']) == str:
            status = [args['status']]
        elif type(args['status']) == list:
            status = args['status']
        else:
            status = json.loads(args['status'])

        # batch_id = get_progress_batch_id(system_id=system_id)
        logger.info("In get_pack_id_list_from_packs_by_status_retail: update_status: {}".format(update_status))

        # if batch_id is None:
        #     return create_response({'batch_id': batch_id, "pack_count": 0})

        if system_id and pack_id_list is not None:
            valid_pack_list = verify_pack_list_by_system_id(pack_list=pack_id_list, system_id=system_id)
            if not valid_pack_list:
                return error(1014)

        pack_ids = get_pack_id_list_by_status_and_system(status=status, pack_id_list=pack_id_list, system_id = system_id)

        if update_status:
            update_args = {'pack_id_list': pack_ids, 'status': update_status, 'system_id': system_id}
            change_pack_status(update_args)

        return create_response(pack_ids)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_id_list_from_packs_by_status_retail: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_id_list_from_packs_by_status_retail: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_id_list_from_packs_by_status_retail {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_id_list_from_packs_by_status_retail: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pack_id_list_from_packs_by_status_retail: " + str(e))


@validate(required_fields=["pack_id", "unloading_time", "user_id", "status", "ips_username", "filled_at"])
@log_args_and_response
def update_unloading_time(args):
    """
    @param args: status, pack_id
    @return: if status than updates unloading time and status else unloading time
    """

    # FUTURE SCOPE: We need to handle the reason code by synchronizing it with reason master table, instead of Frontend
    # team handling it with static values.
    # This is for the Reasons that we show in MVS when marking pack status to Fill Manually.

    status = args['status']
    pack_id = args['pack_id']
    company_id = args['company_id']
    system_id = args['system_id']
    unloading_time = args['unloading_time']
    user_id = args['user_id']
    filled_at = args.get("filled_at", None)
    batch_id = get_progress_batch_id(system_id=system_id)
    dry_run = bool(int(args.get("dry_run", 0)))
    update_dict: dict = dict()
    update_notification_dp_all = False
    new_pack_assign_to = args.get('assigned_to', None)
    update_dict['unloading_time'] = unloading_time[0:19].encode("utf-8")   # remove IST+0530

    # Verify if the reason field is received from CRM before processing the reason dict any further
    # Because reason field will not be received everytime
    reason_crm = args.get("reason", None)
    if reason_crm:
        if isinstance(args["reason"], str):
            reason = json.loads(args["reason"])
        else:
            reason = args["reason"]

    reason_desc: str
    reason_action: int

    if dry_run:
        dummy_response = "time updated"
        return create_response(dummy_response)

    try:
        if company_id:
            valid_pack_list = verify_pack_list_by_company_id(pack_list=[pack_id], company_id=company_id)
            if not valid_pack_list:
                return error(1026)
        if system_id:
            valid_pack_list = verify_pack_list_by_system_id(pack_list=[pack_id], system_id=system_id)
            if not valid_pack_list:
                return error(1014)

        if status in [settings.DONE_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS] \
                and filled_at is None:
            logger.error("error in update_unloading_time missing param filled at")
            return error(1001, "Missing Parameter(s): filled_at")

        if reason_crm:
            # When on MVS screen, user selects an appropriate reason for moving packs from Robot to Pack Fill Workflow
            # With new changes, we will get the reason in dictionary format instead of string
            logger.info("In update_unloading_time: Parse the dictionary containing reason details from MVS before "
                        "updating Pack Status.")
            logger.info("In update_unloading_time: Reason Dictionary = {}".format(reason))
            reason_desc = reason.get("desc", "Other")

            args["reason_action"] = reason.get("action", MVS_OTHER)
            args["reason_rx_no_list"] = reason.get("rx_no_list", None)
            args["drug_list"] = reason.get("drug_list", None)
            args["reason"] = reason_desc

            # We need to make that we receive the Pharmacy Rx No list when selected reasons are
            # Drugs out of Stock OR Missing Pills
            if args["reason_action"] == MVS_DRUGS_OUT_OF_STOCK and args["drug_list"] is None:
                return error(1001, "Action: Drugs Out of Stock. Missing drug list for MVS action {}"
                             .format(args["reason_action"]))

            if args["reason_action"] == MVS_MISSING_PILLS and args["reason_rx_no_list"] is None:
                return error(1001, "Action: Missing Pills. Missing Pharmacy Rx No list for MVS action {}"
                             .format(args["reason_action"]))

        if status == settings.DELETED_PACK_STATUS:
            logger.debug("Check if the Pack exists in Ext Pack Details")
            args["reason"] = constants.DELETE_PACK_DESC_FOR_OLD_PACKS_MVS_CHANGE_RX
            ext_flag = db_check_pack_marked_for_delete_dao(pack_id=pack_id)
            if ext_flag:
                args["change_rx"] = True
                args["change_rx_token"] = get_token()
                update_notification_dp_all = True

        with db.transaction():
            status = update_dict_pack_details(update_dict=update_dict, pack_id=pack_id, system_id=system_id)
            logger.info("IN update_unloading_time: update uploading time in pack details table: {}".format(status))
            rts_flag = bool(int(get_company_setting_by_company_id(company_id).get("USE_RTS_FLOW", 0)))
            if rts_flag:
                reuse_pack_drug_insert_response, ext_update_dict = insert_record_in_reuse_pack_drug([pack_id],
                                                                                                    company_id)
                logger.info(
                    "In update_unloading_time: response of insert_record_in_reuse_pack_drug: {}, ext_update_dict: {}"
                    .format(reuse_pack_drug_insert_response, ext_update_dict))

                if ext_update_dict:
                    ext_update_status = db_update_ext_packs_delivery_status_dao(ext_update_dict)
                    logger.debug(
                        "In update_unloading_time:: ext_update_status - {}".format(ext_update_status))
            response = json.loads(set_status(args))
            logger.info("In update_unloading_time: response {}".format(response))
            response = "time updated"

            if update_notification_dp_all and new_pack_assign_to:
                # Assigne user to new packs for this packs.
                status = assign_user_for_change_rx_packs_from_mvs(pack_id, new_pack_assign_to, company_id, user_id)

            return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_unloading_time: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_unloading_time: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_unloading_time {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_unloading_time: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_unloading_time: " + str(e))


@validate(required_fields=["pack_id", "system_id"])
@log_args_and_response
def get_pack_details_from_pack_id(args):
    """
    @param args: pack_id
    @return: dict of pack_display_id and patient_name as key and display id and patient name for the given pack id as value
    """
    company_id = args['company_id']
    system_id = args['system_id']
    response: list = list()

    if isinstance(args['pack_id'], str):
        pack_id = args['pack_id'].split(',')  # use if multiple packs are needed
    elif isinstance(args['pack_id'], int):
        pack_id = [args['pack_id']]
    elif isinstance(args['pack_id'], list):
        pack_id = args['pack_id']
    else:
        pack_id = None

    try:
        if company_id:
            valid_pack_list = verify_pack_list_by_company_id(pack_list=pack_id, company_id=company_id)
            if not valid_pack_list:
                return error(1026)
        if system_id:
            valid_pack_list = verify_pack_list_by_system_id(pack_list=pack_id, system_id=system_id)
            if not valid_pack_list:
                return error(1014)
        if settings.UTILIZATION_OF_UNIT_DOSE_PACK:
            status = set_unit_pack_for_multi_dosage(company_id, pack_id)
        query = get_pack_details_by_pack_id(pack_id=pack_id, system_id=system_id)

        mfd_pack_device_dict = get_mfd_devices(pack_id=pack_id)

        for record in query:
            if record['id'] in mfd_pack_device_dict.keys() and len(mfd_pack_device_dict[record['id']]):
                if record['robot_id_list']:
                    device_list = record['robot_id_list'] + "," + mfd_pack_device_dict[record['id']]
                else:
                    device_list = mfd_pack_device_dict[record['id']]
                record['robot_id_list'] = ','.join(set(device_list.split(',')))
            response.append(record)

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_details_from_pack_id: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_details_from_pack_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_details_from_pack_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_details_from_pack_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pack_details_from_pack_id: " + str(e))


@validate(required_fields=["system_id"])
@log_args_and_response
def get_packs_count_by_robot_id(args):
    """
    @param args: robot id
    @return: pack count which are in progress by given robot id
    """

    system_id = args['system_id']
    device_id = list(args['device_id']) if 'device_id' in args and args['device_id'] is not None else None
    robot_wise_pack_count: dict = dict()
    response: list = list()
    device_pack_dict: dict = dict()
    try:
        # batch_id = args['batch_id'] if 'batch_id' in args and args['batch_id'] is not None else \
        #     get_progress_batch_id(system_id)
        #
        # logger.info("In get_packs_count_by_robot_id: batch_id: {}".format(batch_id))
        # if batch_id is None:
        #     return {'batch_id': batch_id, "pack_count": 0}

        query = get_pack_count_by_device_id(system_id=system_id, device_id=device_id)

        for record in query:
            if record['device_id']:
                if record['device_id'] not in robot_wise_pack_count.keys():
                    device_pack_dict[record['device_id']] = list()
                    robot_wise_pack_count[record['device_id']] = {"device_id": record['device_id'],
                                                                  "progress_pack_count": 0, "pack_count": 0}

                if record['id'] not in device_pack_dict[record['device_id']]:
                    device_pack_dict[record['device_id']].append(record['id'])
                    if record['pack_status'] == settings.PROGRESS_PACK_STATUS:
                        robot_wise_pack_count[record['device_id']]["progress_pack_count"] += 1

                    if record['pack_status'] not in [settings.MANUAL_PACK_STATUS] and \
                            record['filled_at'] != settings.FILLED_AT_POST_PROCESSING:
                        robot_wise_pack_count[record['device_id']]['pack_count'] += 1

        for key, value in robot_wise_pack_count.items():
            response.append(value)
        logger.info("In get_packs_count_by_robot_id: response : {}".format(response))
        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_packs_count_by_robot_id: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_packs_count_by_robot_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_count_by_robot_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_packs_count_by_robot_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_count_by_robot_id: " + str(e))


@log_args_and_response
def get_pack_queue_by_conveyor_id_pagination(only_manual, paginate, filter_fields=None, sort_fields=None,
                                             system_id=None, drug_list=None):
    """
        @param drug_list:
        @param system_id:
        @param sort_fields:
        @param filter_fields:
        @param paginate:
        @param only_manual: robot id
        @return: get pack queue data by conveyor id
        """
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')
    pack_list: list = list()
    pack_list_raw: list = list()
    robot_dict: dict = dict()
    pack_seq_dict: dict = dict()
    null_order_no: list = list()

    try:
        results, count, non_paginate_result, selected_drug_details = get_pack_queue_by_conveyor_id_pagination_data(
            filter_fields=filter_fields,
            sort_fields=sort_fields,
            paginate=paginate,
            system_id=system_id,
            drug_list=drug_list,
            only_manual=only_manual)

        logger.info("In get_pack_queue_by_conveyor_id_pagination: results: {}".format(results))
        logger.info("In get_pack_queue_by_conveyor_id_pagination: counts: {}".format(count))

        for record in results:
            pack_list_raw.append(record['pack_id'])

        if len(results) == 0:
            response_dict = {"pack_list": pack_list,
                             "robot_dict": robot_dict,
                             "selected_drug_details": selected_drug_details}
            return False, response_dict

        query1 = get_pack_order_no_by_pack_list(pack_list_raw)
        for record in query1:
            if record['order_no'] is None:
                null_order_no.append(record['id'])
            else:
                pack_list.append(record['id'])

        logger.info("In get_pack_queue_by_conveyor_id_pagination: null order number: {}".format(null_order_no))
        logger.info("In get_pack_queue_by_conveyor_id_pagination: pack_list: {}".format(pack_list))
        if len(null_order_no) > 0:
            for null_pack in null_order_no:
                pack_list.append(null_pack)

        logger.info("In get_pack_queue_by_conveyor_id_pagination: pack_list: {}".format(pack_list))
        for index, pack in enumerate(pack_list):
            pack_seq_dict[pack] = index + 1

        logger.info("In get_pack_queue_by_conveyor_id_pagination: pack_seq_dict: {}".format(pack_seq_dict))
        # looping over records
        for record in results:

            record['canister_drug_details'] = get_canister_drug_data_from_canister_ids(
                                                                                       canister_ids=record[
                                                                                           'canister_ids'],
                                                                                       pack_id=record['pack_id'])

            record['manual_drug_details'] = get_manual_drug_data_from_drug_ids(drug_ids=record[
                                                                                   'manual_drug_ids'],
                                                                               pack_id=record['pack_id'])

            if record['admin_period'] is not None:
                admin_period = str(record['admin_period']).split(' to ')
                logger.info(admin_period)
                start_date = datetime.datetime.strptime(admin_period[0], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(admin_period[1], "%Y-%m-%d")
                record['admin_period'] = start_date.strftime("%m-%d-%Y") + ' to ' + end_date.strftime("%m-%d-%Y")

            record['delivery_date'] = record['delivery_date'].strftime("%m-%d-%Y %H:%M:%S") if record[
                                                                                                   'delivery_date'] \
                                                                                               is not None else None
            record['helper_tray_dropped_time'] = None
            record['helper_tray_status'] = None
            record['helper_tray_srno'] = None
            record['manual_tray_robot_id'] = None
            record['manual_tray_location'] = None
            record['conveyor_id'] = 1
            record['helper_tray_name'] = None
            record['crm_description'] = None
            record['manual_tray_status_id'] = None
            record['helper_tray_status_id'] = None
            record['helper_tray_rfid'] = None
            record['pack_sequence'] = pack_seq_dict[record['pack_id']]
            mfd_status: set = set()
            # check if pack requires mfd to be filled i.e is_mfd_pack and set mfd_filled flag for it
            if record['mfd_status']:
                mfd_status = set(map(lambda x: int(x), record['mfd_status'].split(',')))
            print('mfd_status', mfd_status)
            logger.info("In get_pack_queue_by_conveyor_id_pagination: mfd_status: {}".format(mfd_status))
            if mfd_status.intersection(set(constants.PACK_MFD_REQUIRED_LIST)):
                record['mfd_required'] = True
                if mfd_status.intersection(set(constants.MFD_CANISTER_DONE_LIST_PQ)):
                    record['mfd_filled'] = True
                else:
                    record['mfd_filled'] = False
            else:
                record['mfd_required'] = False
                record['mfd_filled'] = False

        # get dict format from given non paginate results
        non_paginate_result = modify_non_paginate_result(non_paginate_result)
        if non_paginate_result['device_id_list']:
            robot_dict = get_device_name_from_device(device_id_list=non_paginate_result['device_id_list'])
        else:
            logger.error("In get_pack_queue_by_conveyor_id_pagination: robot_list is empty.")
        logger.info("In get_pack_queue_by_conveyor_id_pagination: non paginate result {}".format(non_paginate_result))
        response_dict = {"pack_list": results, "number_of_records": count, "all_packs_data": non_paginate_result,
                         "robot_dict": robot_dict, "selected_drug_details": selected_drug_details}

        return True, response_dict

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pack_queue_by_conveyor_id_pagination {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_queue_by_conveyor_id_pagination: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_queue_by_conveyor_id_pagination {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_queue_by_conveyor_id_pagination: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pack_queue_by_conveyor_id_pagination: " + str(e))


@ validate(required_fields=["pack_priority", "pack_id_list", "sequence_as_sent", "system_id"])
@log_args_and_response
def update_pack_priority_by_pack_list(args):
    """
        This function will be used to update the priority of pack filling for any pack id list.
        To achieve that we first get the last reference of pack priority based on priority requirement
        And then update the priority of the packs provided in the list
        :param priority : Priority requirement
        1: To Top.... -1: To Bottom
        :param pack_id_list: List of pack ids we need to update
        :param sequence_as_sent: if sequence of pack_id_list needs to be maintained or to not consider
                                existing pack_sequence
        :return: Count of rows updated
        @param args:
    """

    priority = args['pack_priority']
    pack_id_list = args['pack_id_list']
    sequence_as_sent = args['sequence_as_sent']
    system_id = args['system_id']
    user_id = args.get('user_id', 0)
    order_number_list = args.get('order_no_list', None)
    call_from_client = args.get('call_from_client', False)
    user_confirmation = args.get('user_confirmation', False)
    user_confirmation_mfd = args.get('user_confirmation_mfd', False)

    try:
        with db.transaction():
            if priority not in [-1, 1]:
                return False
            if not sequence_as_sent:
                pack_id_list = get_order_pack_id_list(pack_id_list=pack_id_list, system_id=system_id)
            patient_data = get_patient_data_for_packs(pack_id_list)

            patient_id_list = [record['id'] for record in patient_data]
            """To get mfd packs from given pack list"""
            mfd_pack_sequence, extra_pack, pack_id_list, cannot_change_pack, pack_data = db_get_all_mfd_packs_from_packlist(pack_id_list, patient_id_list)
            pack_id_list = get_order_pack_id_list(pack_id_list=pack_id_list, system_id=system_id)
            if mfd_pack_sequence:
                mfd_pack_sequence = get_order_pack_id_list(pack_id_list=mfd_pack_sequence, system_id=system_id)
            logger.info(
                ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: PACK: pack_id_list {}".format(pack_id_list)))
            logger.info(
                ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: PACK: mfd_pack_sequence {}".format(mfd_pack_sequence)))

            pack_list, order_no_list, batch_id, sorted_list = get_previous_pack_priority_for_reference(
                priority=priority,
                pack_id_list=pack_id_list,
                system_id=system_id,
                mfd_pack_sequence=[])

            '''
            This code block is for when user wants any pack/patient to move to top then confirmation will be given to user for 
            today and tomorrow delivery date facility.
            '''
            if not user_confirmation:
                if not pack_id_list:
                    return 1
                facility_data = get_today_tomorrow_delivery_dates_facilities(input_pack_list=pack_id_list,
                                                                             all_pack_list=pack_list, priority=priority)

                if facility_data:
                    if mfd_pack_sequence:
                        facility_data['mfd_pack_sequence'] = mfd_pack_sequence
                        facility_data['extra_pack'] = extra_pack
                        facility_data['cannot_change_pack'] = cannot_change_pack
                        facility_data['pack_data'] = pack_data

                    return facility_data

            if mfd_pack_sequence and not user_confirmation_mfd:
                return {'mfd_pack_sequence': mfd_pack_sequence,
                        'cannot_change_pack':cannot_change_pack,
                        'extra_pack': extra_pack,
                        'pack_data': pack_data,

                        }

            if priority == 1:
                if not sorted_list:
                    sorted_list = pack_id_list + pack_list

                if len(sorted_list) != len(order_no_list):
                    return error(1000, "In update_pack_priority_by_pack_list: Error in changing priority of packs")

            else:
                if not sorted_list:
                    sorted_list = pack_list + pack_id_list

                if len(sorted_list) != len(order_no_list):
                    return error(1000, "In update_pack_priority_by_pack_list: Error in changing priority of packs")

            if mfd_pack_sequence:
                status = skip_mfd_for_packs(mfd_pack_sequence, user_id)
            logger.info(
                ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: PACK: sorted_list {}".format(sorted_list)))
            update_status = change_pack_sequence(pack_list=sorted_list, order_number_list=order_no_list)
            logger.info("IN update_pack_priority_by_pack_list: update_status: {}".format(update_status))

            if len(pack_id_list) > 0:
            #     if user_id > 0:
            #         logger.info("In update_pack_priority_by_pack_list: pack queue sequence changed by {}".format(user_id))
            #
            #     logger.info("In update_pack_priority_by_pack_list: Before notification sent in update_pack_priority_by_pack_list")
                # message = "Pack queue sequence changed"
                # Notifications(user_id=user_id, call_from_client=call_from_client) \
                #     .send_with_username(user_id=settings.ALL_USER_NOTIFICATION, message=message, flow='dp')
                # logger.info("In update_pack_priority_by_pack_list: After notification sent in update_pack_priority_by_pack_list")

                try:
                    update_replenish_based_on_system(system_id)
                except (InternalError, IntegrityError) as e:
                    logger.error(e, exc_info=True)
                    return error(2001, e)
                except ValueError as e:
                    return error(2005, str(e))

                return 1
            else:
                return 0

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_pack_priority_by_pack_list: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pack_priority_by_pack_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        return json.dumps({"code": 2001, "description": str(e), "status": settings.FAILURE_RESPONSE})


@validate(required_fields=["status", "system_id", "user_id", "company_id"])
@log_args_and_response
def update_pack_count_couch_db(args):
    """
    Function used to update the pack count.
    @param args:
    @return:
    """
    try:
        # response = {}
        time_zone = args.get('time_zone', 'UTC')
        time_zone = settings.TIME_ZONE_MAP[time_zone]

        system_start_time = args.get('system_start_time')
        if system_start_time:
            total_done_packs = get_count_of_done_pack_after_system_start_time(system_start_time, time_zone)
            total_done_packs = {"label": "Today", "count": total_done_packs}
        else:
            total_done_packs = {"label": "Today", "count": 0}

        company_id = args['company_id']
        system_id = args['system_id']
        # batch_id = args['batch_id'] if 'batch_id' in args else get_progress_batch_id(system_id)
        # logger.info("In update_pack_count_couch_db: batch_id : {}".format(batch_id))

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        # if batch_id is None:
        #     response = {"batch_id": batch_id, "pack_count": 0, "day_pack_count": [total_done_packs]}
        #     return create_response(response)

        response_data = json.loads(get_packs_count_by_status(args))
        response = response_data["data"]
        robot_pack_data_list = get_packs_count_by_robot_id(
            {"status": None, "system_id": system_id})
        # response1 = response1_data['data']
        logger.info("IN update_pack_count_couch_db: robot_pack_data_list: {}".format(robot_pack_data_list))
        response['robot_pack_data'] = robot_pack_data_list

        total_pack_count = get_packs_count_for_system(system_id=system_id)
        filled_pack_count = get_filled_packs_count_for_system(system_id=system_id)
        # query = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.batch_id == batch_id)
        # query1 = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.batch_id == batch_id,
        #                                                             PackDetails.pack_status.not_in(
        #                                                                 [settings.PENDING_PACK_STATUS,
        #                                                                  settings.PROGRESS_PACK_STATUS]))
        pending_packs_count = abs(total_pack_count - filled_pack_count)
        if total_pack_count == filled_pack_count:
            response['batch_update_flag'] = True
            batch_info = {"user_id": args['user_id'],
                          "status": settings.BATCH_PROCESSING_COMPLETE,
                          "system_id": args['system_id'],
                          "crm": True}
            response['pack_batch'] = json.loads( create_batch(batch_info))
            notification_message = "No packs left for processing in system {}".format(system_id)
            notification_sent_status = check_notification_sent_or_not(notification_message=notification_message)
            if not notification_sent_status:
                Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
                                                                                 notification_message, flow='dp')
        else:
            response['batch_update_flag'] = False
            if pending_packs_count == settings.PACKS_LEFT_FOR_PROCESSING_100:
                notification_message = "100 packs remains to be processed in system {}".format(system_id)
                notification_sent_status = check_notification_sent_or_not(notification_message=notification_message)
                if not notification_sent_status:
                    Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
                                                                                     notification_message, flow='dp')

            elif pending_packs_count == settings.PACKS_LEFT_FOR_PROCESSING_30:
                notification_message = "30 packs remains to be processed in system {}".format(system_id)
                notification_sent_status = check_notification_sent_or_not(notification_message=notification_message)
                if not notification_sent_status:
                    Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
                                                                                     notification_message, flow='dp')

        today, last_one_hour = get_done_pack_count(time_zone, utc_time_zone_offset)
        day_pack_count = get_pending_pack_count_of_working_day(time_zone, utc_time_zone_offset)
        day_pack_count.insert(0, total_done_packs)
        # day_pack_count.append({"label": "total_packs", "count": total_pack_count})
        # response['done_pack_count'] = done_pack_count
        response['today'] = today
        response['last_one_hour'] = last_one_hour
        response['day_pack_count'] = day_pack_count

        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_pack_count_couch_db: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pack_count_couch_db: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_pack_count_couch_db {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pack_count_couch_db: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_pack_count_couch_db: " + str(e))


@log_args_and_response
def dispatch_new_pack(args):
    """
        Function is used to dispatch new packs
        @param args:
    """
    try:
        batch_start = args.get("batch_start", False)
        version_type = args.get("version_type", "C")
        status, pack_list = get_pack_to_dispatch(args)
        logger.info("In dispatch_new_pack: status: {}, pack_list".format(status, pack_list))
        if status == 2:
            return True, error(7005)
        if status:
            dict_info = {'pack_id': pack_list, 'company_id': args['company_id'], "device_id": args['device_id'],
                         "system_id": args['system_id']}
            if batch_start:
                update_replenish_based_on_device(args["device_id"])
            pack_detail_resp = get_pack_details_from_pack_id(dict_info)

            if version_type == "C":
                response = {"pfm_response": pack_detail_resp[0]}
            else:
                response = {"pfm_response": pack_detail_resp}

            logger.info("In dispatch_new_pack: response: {}".format(response))
            return True, create_response(response)
        else:
            return True, create_response({"description": pack_list})

    except (InternalError, IntegrityError) as e:
        logger.error("error in dispatch_new_pack: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in dispatch_new_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in dispatch_new_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in dispatch_new_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in dispatch_new_pack: " + str(e))


@log_args_and_response
def get_pack_queue(only_manual, filter_fields, paginate, sort_fields, system_id, drug_list):
    """
    @param only_manual:
    @param filter_fields:
    @param paginate:
    @param sort_fields:
    @param system_id:
    @param drug_list
    @return:
    """
    try:
        logger.info("{},{},{},{},{}".format(only_manual, filter_fields, paginate, sort_fields, drug_list))
        pack_count = get_packs_count_for_system(system_id)

        # get pack count by status id
        args = {
            'system_id': system_id,
            'status': [settings.PROGRESS_PACK_STATUS]
        }
        packs_count = json.loads(get_system_packs_count_by_status(args))
        progress_packs = packs_count['data'][str(settings.PROGRESS_PACK_STATUS)]

        filter_fields = None if len(filter_fields) == 0 else filter_fields
        sort_fields = None if len(sort_fields) == 0 else sort_fields
        logger.info('In get_pack_queue: filter_fields' + str(filter_fields) + 'sort_fields' + str(sort_fields))

        status_pagination, response = get_pack_queue_by_conveyor_id_pagination(only_manual=only_manual,
                                                                               filter_fields=filter_fields,
                                                                               paginate=paginate,
                                                                               sort_fields=sort_fields,
                                                                               system_id=system_id,
                                                                               drug_list=drug_list)
        if status_pagination:
            data = response["pack_list"]
            pack_list = response['all_packs_data']['pack_id']

            for record in data:
                robot_string = record["device_id_list"]
                try:
                    # Handling the case where a pack was not assigned to any of the robot
                    robot_list = robot_string.split(",")
                except AttributeError:
                    robot_list = []

                robot_name_list = []
                for item in robot_list:
                    try:
                        r_name = settings.ACTIVE_ROBOT_NAME[str(item)]
                    except KeyError:
                        r_name = item

                    robot_name_list.append(r_name)

                robot_name = ",".join(robot_name_list)
                record["device_id_list"] = robot_name
                response['pack_status_dict'] = get_pack_status_by_pack_list(pack_list=pack_list)
        else:
            response['pack_status_dict'] = dict()
            response['all_packs_data'] = []
            response['robot_dict'] = {}
        response["all_packs_data"] = response['all_packs_data']
        response["total_packs"] = pack_count
        response['pack_status_dict']['progress_packs'] = progress_packs
        response["facility_list"] = get_pending_facility_list(system_id)
        response['robot_dict'] = response['robot_dict']

        return True, response

    except Exception as e:
        logger.error("Error in get_pack_queue {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return False, e


@log_args_and_response
def get_pack_queue_all_batch(only_manual, filter_fields, paginate, sort_fields, system_id, drug_list):
    """
    @param only_manual:
    @param filter_fields:
    @param paginate:
    @param sort_fields:
    @param system_id:
    @param drug_list
    @return:
    """
    system_id = int(system_id)
    try:
        # get batch list and total packc count from system id
        response_data = get_packs_count_for_all_batches(system_id=system_id)
        batch_list = response_data['batch_list']
        logger.info("In get_pack_queue_all_batch: batch_list: {}".format(batch_list))
        if not len(batch_list):
            return True, {"batch_list": batch_list, "pack_count": 0}

        #  get done and progress pack count for given batch id
        # packs_count = get_pack_count(system_id, imported_batch, [settings.DONE_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
        # processed_packs = packs_count[settings.DONE_PACK_STATUS]
        # progress_packs = packs_count[settings.PROGRESS_PACK_STATUS]

        filter_fields = None if len(filter_fields) == 0 else filter_fields
        sort_fields = None if len(sort_fields) == 0 else sort_fields

        status_pagination, response = get_all_batch_pack_queue_by_pagination(only_manual=only_manual,
                                                                             filter_fields=filter_fields,
                                                                             paginate=paginate,
                                                                             sort_fields=sort_fields,
                                                                             system_id=system_id,
                                                                             drug_list=drug_list,
                                                                             batch_list=batch_list)
        if status_pagination:
            data = response["pack_list"]
            pack_list = response['all_packs_data']['pack_id']
            response['pack_status_dict'] = get_pack_status_by_pack_list(pack_list=pack_list)

            for record in data:
                robot_string = record["device_id_list"]
                try:
                    # Handling the case where a pack was not assigned to any of the robot
                    robot_list = robot_string.split(",")
                except AttributeError:
                    robot_list = []

                robot_name_list = []
                for item in robot_list:
                    try:
                        r_name = settings.ACTIVE_ROBOT_NAME[str(item)]
                    except KeyError:
                        r_name = item

                    robot_name_list.append(r_name)

                robot_name = ",".join(robot_name_list)
                record["device_id_list"] = robot_name

        else:
            response['pack_status_dict'] = dict()
            response['all_packs_data'] = []
            response['robot_dict'] = {}
        response["all_packs_data"] = response['all_packs_data']
        response["total_packs"] = response_data['pack_count']
        response["batch_id"] = batch_list[0] if len(batch_list) else None
        response["batch_list"] = batch_list
        response['pack_status_dict']["processed_packs"] = None
        response['pack_status_dict']['progress_packs'] = None
        response["facility_list"] = get_pending_facility_list(system_id, batch_list=batch_list)
        response['robot_dict'] = response['robot_dict']

        return True, response

    except Exception as e:
        logger.error("Error in get_pack_queue_all_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_queue_all_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return False, e


@log_args_and_response
def update_pack_sequence(args):
    """
    Used for non tech mode in pack queue screen.
    If criteria is delivery date it sorts the packs by delivery date.
    If criteria is auto it sets priority of packs for night mode.
    @param args:
    @return:
    """
    try:
        criteria = args["criteria"]
        company_id = int(args['company_id'])
        system_id = args['system_id']
        user_id = args['user_id']
        time_zone = args.get('time_zone', 'UTC')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        resp = False

        batch_id = get_progress_batch_id(system_id)

        if criteria == "delivery_date":
            logger.info("In update_pack_sequence: Tech mode")
            resp = update_pack_queue_seq_by_delivery_date(company_id, system_id, user_id)

        elif criteria == "auto":
            logger.info("In update_pack_sequence: Non tech mode")
            resp = get_packs_to_process_in_non_tech_mode(system_id=system_id,
                                                         batch_id=batch_id,
                                                         user_id=user_id,
                                                         time_zone="UTC")

        logger.info("In update_pack_sequence: Response of update_pack_sequence {}".format(resp))
        return create_response(resp)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_pack_sequence: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pack_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_pack_sequence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pack_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_pack_sequence: " + str(e))


@validate(required_fields=["batch_id", "batch_name", "system_id", "user_id", "company_id"])
@log_args_and_response
def pack_analysis_v2(args):
    """
    Function is called when new batch is ready to import.
    Two sub functions update_analysis_data and create_batch are called.
    1) get_packs_count_for_latest_batch : to get the pack count for latest batch
    2) create_batch : sets status of batch to Batch Imported.

    @param args:
    @return: pack_count, batch_id and robot wise pack data
    """
    status_pack_queue = None
    try:
        user_id = args["user_id"]
        company_id = args["company_id"]
        system_id = args['system_id']
        batch_id = args['batch_id']
        merge_mfd = False
        notification_status = None

        if 'batch_id' in args:
            batch_id = args['batch_id']
            batch_status = get_batch_status(batch_id=batch_id)
            if batch_status not in [settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                                    settings.BATCH_CANISTER_TRANSFER_DONE,
                                    settings.BATCH_MFD_USER_ASSIGNED,
                                    settings.BATCH_ALTERNATE_DRUG_SAVED]:
                return error(1020)

        batch_packs = get_pack_ids_for_batch(batch_id)
        try:
            status_pack_queue = insert_packs_to_pack_queue(batch_packs)
        except IntegrityError as e:
            logger.error("error in inserting packs to pack_queue, packs already inserted in Pack Queue.")
            return error(2001, "Error in pack_analysis_v2: Packs already inserted in Pack Queue.")

        args['batch_packs'] = batch_packs

        if not status_pack_queue:
            return error(1020, "Error in pack_analysis_v2 : Cannot populate PackQueue")

        # Update batch id null for manual packs
        pending_manual_packs = get_manual_packs_by_batch_id(batch_id=batch_id)

        deleted_packs = get_deleted_packs_by_batch(batch_id=batch_id, company_id=company_id)
        pending_manual_packs.extend(deleted_packs)
        logger.info("In pack_analysis_v2: total batch id null packs while batch import {}".format(pending_manual_packs))

        update_pack_manual_response = update_batch_id_null(pending_manual_packs=pending_manual_packs, system_id=system_id)
        logger.info("In pack_analysis_v2: Pending manual packs done null {}, {}".format(pending_manual_packs, update_pack_manual_response))

        if batch_id is None:
            return create_response({'batch_id': batch_id, "pack_count": 0})

        update_mfd_pack_sequence = update_sequence_for_mfd_packs(batch_id)
        logger.info("In pack_analysis_v2: update_mfd_pack_sequence {}".format(update_mfd_pack_sequence))

        response_data = json.loads(get_packs_count_for_latest_batch(batch_id))
        response = response_data['data']
        logger.info("In pack_analysis_v2: get_packs_count_for_latest_batch in pack analysis {}".format(response))

        progress_batch = get_progress_batch_id(system_id)

        if progress_batch:
            args['progress_batch_id'] = progress_batch
            args['status'] = settings.BATCH_MERGED
        else:
            args['progress_batch_id'] = None
            args['status'] = settings.BATCH_IMPORTED
        with db.transaction():
            if batch_id and progress_batch:
                if settings.USE_BATCH_SMART_MERGE:
                    merge_mfd = auto_merge_batch_packs(system_id, batch_id, progress_batch, user_id, company_id)
                else:
                    merge_mfd = merge_mfd_flow(batch_id, progress_batch)
                # update mfd status of progress batch if it is pending or if it's null but merged batch have mfd_status.
                progress_batch_data = get_batch_data(progress_batch)
                batch_data = get_batch_data(batch_id)
                if batch_data.mfd_status:
                    if progress_batch_data.mfd_status:
                        logger.info(f"In pack_analysis_v2, progress_batch: {progress_batch} with mfd_status: {progress_batch_data.mfd_status.id}")
                        logger.info(
                            f"In pack_analysis_v2, batch: {batch_id} with mfd_status: {batch_data.mfd_status.id}")
                        if progress_batch_data.mfd_status.id == constants.MFD_BATCH_FILLED:
                            db_update_mfd_status(progress_batch, mfd_status=constants.MFD_BATCH_PENDING, user_id=user_id)
                    else:
                        db_update_mfd_status(progress_batch, mfd_status=constants.MFD_BATCH_PENDING, user_id=user_id)

                    db_update_mfd_status(batch_data, mfd_status=constants.MFD_BATCH_FILLED, user_id=user_id)

            pack_batch_response = json.loads(create_batch(args))
            logger.info("In pack_analysis_v2: create batch response in pack analysis {}".format(pack_batch_response))
            # Update trolley sequence

            if pack_batch_response['status'] == settings.SUCCESS_RESPONSE:


                robot_wise_response = get_packs_count_by_robot_id({'batch_id': batch_id, 'system_id': system_id})
                # update sequence_no to PPP_SEQUENCE_DONE(it means pre_processing wizard run successfully)
                seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=constants.PPP_SEQUENCE_DONE,
                                                                          batch_id=batch_id)
                logger.info("In pack_analysis_v2: pack_analysis_v2 run successfully: {} , changed sequence to {} for batch_Id: {}"
                             .format(seq_status, constants.PPP_SEQUENCE_DONE, batch_id))
                if seq_status:
                    # update couch db timestamp for pack_pre processing wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=args)
                    logger.info("In pack_analysis_v2: In couch_db time stamp is updated for pre processing wizard: {} for batch_id: {}".format(
                            couch_db_status, batch_id))
            else:
                return json.dumps(pack_batch_response)

            if not progress_batch:
                notification_status = send_notification_and_get_mfd_packs_for_trolley(
                    batch_id=batch_id,
                    user_id=user_id,
                    system_id=system_id,
                    company_id=company_id)


            response['pack_batch_response'] = pack_batch_response
            response['robot_pack_data'] = robot_wise_response
            response['notification_status'] = notification_status
            response['merge_mfd'] = merge_mfd
            logger.info("final response in pack analysis {}".format(response))
            update_replenish_based_on_system(system_id)

            logger.info(f"In pack_analysis_v2, update data in frequent_mfd_drugs")
            populate_data_in_frequent_mfd_drugs_table()

        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in pack_analysis_v2: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in pack_analysis_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        remove_packs_from_queue(batch_packs)
        return error(2001)

    except ValueError as e:
        logger.error("error in pack_analysis_v2: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in pack_analysis_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        remove_packs_from_queue(batch_packs)
        return error(2005, str(e))

    except Exception as e:
        logger.error("Error in pack_analysis_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in pack_analysis_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        remove_packs_from_queue(batch_packs)
        return error(1000, "Error in pack_analysis_v2: " + str(e))


@log_args_and_response
def merge_mfd_flow(batch_id, progress_batch):

    analysis_update_dict = {}
    try:
        # progress_batch = get_progress_batch_id(system_id)
        if progress_batch:
            last_sequence = db_get_last_mfd_sequence_for_batch(progress_batch)
            mfd_filling_started = db_check_mfd_filling_for_batch(batch_id)

            #commeting because now we are merging the batch in any case
            #if last_sequence and not mfd_filling_started:

            mfd_analysis_data = get_mfd_analysis_data_by_batch(batch_id)

            for data in mfd_analysis_data:
                analysis_update_dict.update({
                    data['id']: {"batch_id": progress_batch,
                                 "trolley_seq": int(data['trolley_seq'] + last_sequence)
                                 }})

            if analysis_update_dict:
                status = update_trolley_seq_and_merge(analysis_update_dict)

                if status:
                    return True

        return False

    except (InternalError, IntegrityError) as e:
        logger.error("error in merge_mfd_flow: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in merge_mfd_flow: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except ValueError as e:
        return error(2005, str(e))

    except Exception as e:
        logger.error("Error in merge_mfd_flow {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in merge_mfd_flow: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in merge_mfd_flow: " + str(e))

@log_args_and_response
def get_all_batch_pack_queue_by_pagination(only_manual, paginate, filter_fields=None, sort_fields=None,
                                           system_id=None, drug_list=None, batch_list=None):
    """
    Function to get packs from batch list
    @param only_manual:
    @param paginate:
    @param filter_fields:
    @param sort_fields:
    @param system_id:
    @param drug_list:
    @param batch_list:
    @return:
    """
    try:
        logger.debug("Inside get_all_batch_pack_queue_by_pagination")
        pack_list = list()
        robot_dict = dict()
        debug_mode_flag = False

        if filter_fields and filter_fields.get('patient_name', None) is not None:
            if (filter_fields['patient_name']).isdigit():
                patient_id = int(filter_fields['patient_name'])
                filter_fields['patient_id'] = patient_id
                filter_fields.pop('patient_name')

            elif is_date(filter_fields['patient_name']) and filter_fields['patient_name'][0].isdigit():
                patient_dob = convert_dob_date_to_sql_date(filter_fields['patient_name'])
                filter_fields['patient_dob'] = patient_dob
                filter_fields.pop('patient_name')

        if filter_fields is not None and len(filter_fields) > 0:
            if 'delivery_date' in filter_fields.keys():
                delivery_date_list: list = list()
                for date in filter_fields['delivery_date']:
                    d_date = datetime.datetime.strptime(date, "%m-%d-%Y")
                    delivery_date_list.append(d_date.strftime("%Y-%m-%d"))
                filter_fields['delivery_date'] = delivery_date_list

        if filter_fields and filter_fields.get('pack_display_id') and filter_fields.get('pack_id'):
            debug_mode_flag = True
        elif filter_fields and filter_fields.get('pack_display_id') and not filter_fields.get('pack_id'):
            debug_mode_flag = False

        selected_drug_details = get_drug_data_from_ndc(ndc=drug_list)

        results, count, non_paginate_result = get_all_batch_pack_queue_data(filter_fields=filter_fields,
                                                                            paginate=paginate,
                                                                            debug_mode_flag=debug_mode_flag,
                                                                            drug_list=drug_list, sort_fields=sort_fields,
                                                                            only_manual=only_manual, batch_list=batch_list,
                                                                            system_id=system_id)

        logger.info("get_all_batch_pack_queue_by_pagination query results {}, {}, {}".format(results,
                                                                                             count,
                                                                                             non_paginate_result))

        if len(results) == 0:
            response_dict = {"pack_list": pack_list,
                             "robot_dict": robot_dict,
                             "selected_drug_details": selected_drug_details}
            return False, response_dict

        # looping over records
        for record in results:

            record['canister_drug_details'] = get_canister_drug_data_from_canister_ids(batch_id=record['batch_id'],
                                                                                       canister_ids=record[
                                                                                           'canister_ids'],
                                                                                       pack_id=record['pack_id'])

            record['manual_drug_details'] = get_manual_drug_data_from_drug_ids(drug_ids=record[
                                                                                   'manual_drug_ids'],
                                                                               pack_id=record['pack_id'])

            if record['admin_period'] is not None:
                admin_period = str(record['admin_period']).split(' to ')
                logger.info(admin_period)
                start_date = datetime.datetime.strptime(admin_period[0], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(admin_period[1], "%Y-%m-%d")
                record['admin_period'] = start_date.strftime("%m-%d-%Y") + ' to ' + end_date.strftime("%m-%d-%Y")

            record['delivery_date'] = record['delivery_date'].strftime("%m-%d-%Y %H:%M:%S") if record[
                                                                                                   'delivery_date'] \
                                                                                               is not None else None
            record['helper_tray_dropped_time'] = None
            record['helper_tray_status'] = None
            record['helper_tray_srno'] = None
            record['manual_tray_robot_id'] = None
            record['manual_tray_location'] = None
            record['conveyor_id'] = 1
            record['helper_tray_name'] = None
            record['crm_description'] = None
            record['manual_tray_status_id'] = None
            record['helper_tray_status_id'] = None
            record['helper_tray_rfid'] = None

            # check if pack requires mfd to be filled i.e is_mfd_pack and set mfd_filled flag for it
            mfd_status = set()
            if record['mfd_status']:
                mfd_status = set(map(lambda x: int(x), record['mfd_status'].split(',')))
            print('mfd_status', mfd_status)
            if mfd_status.intersection(set(constants.PACK_MFD_REQUIRED_LIST)):
                record['mfd_required'] = True
                if mfd_status.intersection(set(constants.MFD_CANISTER_DONE_LIST_PQ)):
                    record['mfd_filled'] = True
                else:
                    record['mfd_filled'] = False
            else:
                record['mfd_required'] = False
                record['mfd_filled'] = False

        # get dict format from given non paginate results
        non_paginate_result = modify_non_paginate_result(non_paginate_result)
        if non_paginate_result['device_id_list']:
            robot_dict = get_device_name_from_device(device_id_list=non_paginate_result['device_id_list'])
        else:
            logger.error("get_all_batch_pack_queue_by_pagination robot_list is empty.")

        response_dict = {"pack_list": results, "number_of_records": count, "all_packs_data": non_paginate_result,
                         "robot_dict": robot_dict, "selected_drug_details": selected_drug_details}

        return True, response_dict

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args
def get_canister_drug_data_from_canister_ids(canister_ids: str, pack_id: int):
    """
    Function is used to get drug info from given canister id's
    @param pack_id:
    @param batch_id:
    @param canister_ids:
    @return:
    """
    try:
        canister_drug_details = "|"
        canister_list = canister_ids.split(",") if canister_ids else None
        if canister_list:
            drug_info_list = get_drug_info_from_canister_list_pack_queue(
                                                                         canister_list=canister_list,
                                                                         pack_id=pack_id
                                                                         )
            canister_drug_details = canister_drug_details.join(drug_info_list)
            return canister_drug_details
        else:
            return None

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error(e)
        raise

    except Exception as e:
        logger.error(e)
        return None


@log_args
def get_manual_drug_data_from_drug_ids(drug_ids: str, pack_id: int):
    """
    Fnction to get drug info for given manual drugs
    @param pack_id:
    @param batch_id:
    @param drug_ids:
    @return:
    """
    try:
        manual_drug_details = "|"
        manual_drugs = [x.split(',') for x in drug_ids.split('|')] if drug_ids else None
        if manual_drugs:
            drug_info_list = get_manual_drug_info_from_drug_list_pack_queue(drug_list=manual_drugs,
                                                                            pack_id=pack_id
                                                                            )
            manual_drug_details = manual_drug_details.join(drug_info_list)
            return manual_drug_details
        else:
            return None

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error(e)
        raise

    except Exception as e:
        logger.error(e)
        return None


def modify_non_paginate_result(non_paginate_result):
    for field, value in non_paginate_result.items():
        if field == 'pack_id':
            continue
        if field == 'manual_drug_count':
            non_paginate_result[field] = sum(value)
        if field == 'device_id_list':
            device_ids_set = set()
            for i in non_paginate_result[field]:
                if i is not None:
                    for j in i.split(","):
                        device_ids_set.add(j)
            non_paginate_result[field] = list(device_ids_set)
    return non_paginate_result


def add_having_clauses(clauses_having, fields_dict, filter_fields):
    if filter_fields and "canister_drug_count" in filter_fields:
        key = fields_dict["canister_drug_count"]
        value = [int(val) for val in filter_fields["canister_drug_count"].split(',')]
        subclauses = list()
        for v in value:
            if v in range(0, 4):
                subclauses.append((key == v))
            else:
                subclauses.append((key >= v))
        clauses_having.append((functools.reduce(operator.or_, subclauses)))
    if filter_fields and "manual_drug_count" in filter_fields:
        key = fields_dict["manual_drug_count"]
        value = [int(val) for val in filter_fields["manual_drug_count"].split(',')]
        subclauses = list()
        for v in value:
            if v in range(0, 4):
                subclauses.append((key == v))
            else:
                subclauses.append((key >= v))
        clauses_having.append((functools.reduce(operator.or_, subclauses)))
    return clauses_having


@log_args_and_response
def get_today_tomorrow_delivery_dates_facilities(input_pack_list, all_pack_list, priority):
    """
    This function will check that if any facilities will hamper because of changing pack orders on both cases:Move to Top and to Bottom.
    """
    output_facility_date: list = list()
    other_pack_list: list = list()

    batch_id = get_batch_id_from_packs(all_pack_list=all_pack_list)
    facility_delivery_date, _ = get_facility_data_by_batch(batch_id=batch_id)
    remaining_facility_delivery_date, _ = get_facility_data_by_packs(pack_list=all_pack_list)
    input_facility_delivery_date, facility_name_id_dict = get_facility_data_by_packs(pack_list=input_pack_list)
    facility_packs = get_packs_by_facility(pack_list=input_pack_list)
    current_date = datetime.date.today()
    next_date = current_date + datetime.timedelta(days=1)
    dates_to_check = {str(current_date), str(next_date)}

    for facility, delivery_date in facility_delivery_date.items():
        if facility in remaining_facility_delivery_date:
            remaining_facility_delivery_date[facility] = delivery_date
        if facility in input_facility_delivery_date:
            input_facility_delivery_date[facility] = delivery_date

    logger.info("In get_today_tomorrow_delivery_dates_facilities: batch_id: {},facility_delivery_date: {}, remaining_facility_delivery_date: {}, input_facility_delivery_date: {},"
                "facility_packs: {}, dates_to_check: {}".format(batch_id, facility_delivery_date, remaining_facility_delivery_date, input_facility_delivery_date, facility_packs, dates_to_check))
    if priority == 1:
        '''
        On Move to top, this will check if any packs with today and tomorrow's delivery date in top of queue,
         if there then this will return those facilities with delivery date otherwise not.
         {str(current_date)}
        '''
        if dates_to_check & set(map(str, remaining_facility_delivery_date.values())):
            for facility, delivery_date in remaining_facility_delivery_date.items():
                if str(delivery_date) in dates_to_check and facility not in input_facility_delivery_date:
                    output_facility_date.append({'facility_name': facility, 'delivery_date': delivery_date})
            if len((set(map(str,
                            remaining_facility_delivery_date.values())) - dates_to_check) & dates_to_check) == 0 and len(
                    output_facility_date) == 0 and set(map(str, input_facility_delivery_date.values())).issubset(dates_to_check) == False:
                for facility, delivery_date in remaining_facility_delivery_date.items():
                    if str(delivery_date) in dates_to_check:
                        output_facility_date.append({'facility_name': facility, 'delivery_date': delivery_date})
        if output_facility_date:
            return {"facility_details": output_facility_date}
        return {}
    else:
        '''
        In Move to bottom, if any packs are there in input packs(packs to be shifted to bottom) with today and tomorrow's delivery date,
        then those facilities will return and also the packs will return of other facilities with future delivery date for frontend to send on next api call(if user clicks on "No"). 
        '''
        if dates_to_check & set(map(str, input_facility_delivery_date.values())):
            for facility, delivery_date in input_facility_delivery_date.items():
                if str(delivery_date) in dates_to_check:
                    output_facility_date.append({'facility_name': facility, 'delivery_date': delivery_date})
                else:
                    other_pack_list.extend(facility_packs[facility_name_id_dict[facility]])
        if output_facility_date:
            return {"facility_details": output_facility_date, "other_pack_list": other_pack_list}
        return {}


@log_args_and_response
def get_previous_pack_priority_for_reference(pack_id_list, priority=1, system_id=None,
                                             mfd_pack_sequence=None, batch_id=None):
    """
    @param mfd_pack_sequence: list
    @param pack_id_list: list
    @param priority: int
    @param system_id: int
        This function will be used to find the last pack for reference in case we want to change priority
        :param priority: Priority direction
        1: Top, -1: Bottom
        :return:  Last reference priority
    """
    try:


        if mfd_pack_sequence:
            """Code block to handle case when sequence of mfd packs is to be updated"""

            if len(mfd_pack_sequence) == len(pack_id_list):
                """when all packs for which sequence is to be changed are mfd packs"""
                status, pack_list, order_no_list, sorted_list = get_mfd_pack_priority(system_id=system_id,
                                                                                      mfd_pack_sequence=mfd_pack_sequence,
                                                                                      priority=priority)

            else:
                """when there are automatic and mfd packs"""
                automatic_packs = list(set(pack_id_list) - set(mfd_pack_sequence))
                status, pack_list, order_no_list, sorted_list = get_mfd_and_automatic_pack_priority(system_id,
                                                                                                    automatic_packs,
                                                                                                    priority,
                                                                                                    mfd_pack_sequence)

            if status:
                return pack_list, order_no_list, system_id, sorted_list

            else:
                raise ValueError("In get_previous_pack_priority_for_reference: Unable to update priority")

        pack_tuple = []
        pack_list = []
        order_no_list = []
        temp_pack_list = deepcopy(pack_id_list)

        if priority == 1:
            query = get_pending_pack_queue_order_pack(system_id=system_id, priority=priority)
            for record in query:
                order_no_list.append(record['order_no'])
                if record['id'] in pack_id_list:
                    temp_pack_list.remove(record['id'])
                    if len(temp_pack_list) == 0:
                        break
                    else:
                        continue
                pack_list.append(record['id'])
            sorted_list = pack_id_list + pack_list
            logger.info(
                "In get_previous_pack_priority_for_reference: sorted_list: {}, pack_list: {}, pack_id_list: {}, order_no_list: {}"
                .format(sorted_list, pack_list, pack_id_list, order_no_list))
        else:
            query = get_pending_pack_queue_order_pack(system_id=system_id, priority=priority)
            for record in query:
                order_no_list.append(record['order_no'])
                if int(record['id']) in pack_id_list:
                    temp_pack_list.remove(record['id'])
                    if len(temp_pack_list) == 0:
                        break
                    else:
                        continue
                pack_list.append(record['id'])
            pack_list.reverse()
            order_no_list.reverse()
            sorted_list = pack_list + pack_id_list
            logger.info(
                "In get_previous_pack_priority_for_reference: sorted_list: {}, pack_list: {}, pack_id_list: {}, order_no_list: {}"
                .format(sorted_list, pack_list, pack_id_list, order_no_list))
        return pack_id_list, order_no_list, system_id, sorted_list

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_previous_pack_priority_for_reference {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_previous_pack_priority_for_reference: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        logger.error("Error in get_previous_pack_priority_for_reference {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_previous_pack_priority_for_reference: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_previous_pack_priority_for_reference: " + str(e))


@log_args_and_response
def get_mfd_pack_priority(system_id, priority, mfd_pack_sequence):
    """
    Function called when packs for which priority is to be changed includes mfd packs.
    Change priority of packs such that mfd sequence is maintained

    @param batch_id: int
    @param priority: int
    @param mfd_pack_sequence: list
    @return: status, pending_pack_list, order_no_list, sorted_list
    """

    try:
        order_no_list = list()
        pending_pack_list = list()
        total_packs = deepcopy(mfd_pack_sequence)
        automatic_packs = list()
        mfd_pack_updated = list()
        pack_sequence = list()
        batch_mfd_pack_dict = db_get_pack_queue_mfd_packs(system_id)
        batch_mfd_packs = [int(item['mfd_pack']) for item in batch_mfd_pack_dict]
        logger.info("In get_mfd_pack_priority: batch_mfd_packs: {}".format(batch_mfd_packs))

        if priority == 1:
            first_pack = False
            first_mfd_pack_index = batch_mfd_packs.index(mfd_pack_sequence[0])
            if first_mfd_pack_index != 0:
                batch_first_mfd_pack = batch_mfd_packs[first_mfd_pack_index - 1]
            else:
                batch_first_mfd_pack = mfd_pack_sequence[0]
                first_pack = True

            logger.info("In get_mfd_pack_priority: batch_first_mfd_pack: {}".format(batch_first_mfd_pack))
            query = get_pending_pack_queue_order_pack(system_id=system_id, priority=priority)
            for record in query:
                if len(total_packs):
                    order_no_list.append(record['order_no'])
                    pack_sequence.append(record['id'])
                    if record['id'] in batch_mfd_packs:
                        mfd_pack_updated.append(record['id'])
                    else:
                        automatic_packs.append(record['id'])

                    if record['id'] in total_packs:
                        total_packs.remove(record['id'])
                else:
                    break

            if len(mfd_pack_sequence) == 1 and mfd_pack_sequence[0] == batch_first_mfd_pack:
                remove_pack = pack_sequence.remove(batch_first_mfd_pack)
                pack_sequence.insert(0, batch_first_mfd_pack)

            elif batch_mfd_packs[0] in mfd_pack_sequence:
                index = 0
                for pack in mfd_pack_sequence:
                    pack_sequence.remove(pack)
                    pack_sequence.insert(index, pack)
                    index += 1
            else:
                if batch_first_mfd_pack not in mfd_pack_sequence:
                    first_index = pack_sequence.index(batch_first_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

                else:
                    first_index = pack_sequence.index(batch_first_mfd_pack)
                    mfd_pack_sequence.remove(batch_first_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

            sorted_list = pack_sequence
            logger.info(
                "In get_mfd_pack_priority: sorted_list: {}, mfd_pack_updated: {}, total_packs: {}, pack_sequence: {}, order_no_list: {}"
                .format(sorted_list, mfd_pack_updated, total_packs, pack_sequence, order_no_list))
        else:
            last_pack = False
            last_mfd_pack_index = batch_mfd_packs.index(mfd_pack_sequence[-1])
            if last_mfd_pack_index == (len(batch_mfd_packs) - 1):
                batch_last_mfd_pack = mfd_pack_sequence[-1]
                last_pack = True
            else:
                batch_last_mfd_pack = batch_mfd_packs[last_mfd_pack_index + 1]

            mfd_pack_sequence.reverse()
            query = get_pending_pack_queue_order_pack(system_id=system_id, priority=priority)

            for record in query:
                if len(total_packs):
                    order_no_list.append(record['order_no'])
                    pack_sequence.append(record['id'])
                    if record['id'] in batch_mfd_packs:
                        mfd_pack_updated.append(record['id'])
                    else:
                        automatic_packs.append(record['id'])

                    if record['id'] in total_packs:
                        total_packs.remove(record['id'])

                else:
                    break

            if len(mfd_pack_sequence) == 1 and mfd_pack_sequence[0] == batch_last_mfd_pack:
                remove_pack = pack_sequence.remove(batch_last_mfd_pack)
                pack_sequence.insert(0, batch_last_mfd_pack)

            elif batch_mfd_packs[-1] in mfd_pack_sequence:
                index = 0
                for pack in mfd_pack_sequence:
                    pack_sequence.remove(pack)
                    pack_sequence.insert(index, pack)
                    index += 1

            else:
                if batch_last_mfd_pack not in mfd_pack_sequence:
                    first_index = pack_sequence.index(batch_last_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

                else:
                    first_index = pack_sequence.index(batch_last_mfd_pack)
                    mfd_pack_sequence.remove(batch_last_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

            # pack_sequence.reverse()
            sorted_list = pack_sequence
            logger.info("In get_mfd_pack_priority: sorted_list: {}, mfd_pack_updated: {}, total_packs: {}, pack_sequence: {}, order_no_list: {}"
                        .format(sorted_list, mfd_pack_updated, total_packs, pack_sequence, order_no_list))

        return True, pack_sequence, order_no_list, sorted_list

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in get_mfd_pack_priority {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_pack_priority: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise

    except Exception as e:
        logger.error("Error in get_mfd_pack_priority {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_pack_priority: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return False


@log_args_and_response
def get_mfd_and_automatic_pack_priority(system_id, automatic_packs, priority, mfd_pack_sequence):
    """
    Function called when packs for which priority is to be changed includes mfd packs.
    Change priority of packs such that mfd sequence is maintained

    @param system_id: int
    @param automatic_packs: list
    @param priority: int
    @param mfd_pack_sequence: list
    @return: status, pending_pack_list, order_no_list, sorted_list
    """

    try:
        order_no_list = list()
        pending_pack_list = list()
        total_packs = automatic_packs + mfd_pack_sequence
        pending_automatic_packs = list()
        pack_sequence = list()
        mfd_pack_updated = list()
        batch_first_mfd_pack = 0
        batch_mfd_pack_dict = db_get_pack_queue_mfd_packs(system_id)
        batch_mfd_packs = [int(item['mfd_pack']) for item in batch_mfd_pack_dict]
        if priority == 1:
            first_mfd_pack_index = batch_mfd_packs.index(mfd_pack_sequence[0])
            if first_mfd_pack_index != 0:
                batch_first_mfd_pack = batch_mfd_packs[first_mfd_pack_index - 1]
            else:
                batch_first_mfd_pack = mfd_pack_sequence[0]

            query = get_pending_pack_queue_order_pack(system_id=system_id, priority=priority)

            for record in query:
                if len(total_packs):
                    order_no_list.append(record['order_no'])
                    pack_sequence.append(record['id'])
                    if record['id'] in batch_mfd_packs:
                        mfd_pack_updated.append(record['id'])
                    else:
                        pending_automatic_packs.append(record['id'])

                    if record['id'] in total_packs:
                        total_packs.remove(record['id'])

                else:
                    break

            if len(mfd_pack_sequence) == 1 and mfd_pack_sequence[0] == batch_first_mfd_pack:
                remove_pack = pack_sequence.remove(batch_first_mfd_pack)
                pack_sequence.insert(0, batch_first_mfd_pack)

            elif batch_mfd_packs[0] in mfd_pack_sequence:
                index = 0
                for pack in mfd_pack_sequence:
                    pack_sequence.remove(pack)
                    pack_sequence.insert(index, pack)
                    index += 1

            else:
                if batch_first_mfd_pack not in mfd_pack_sequence:
                    first_index = pack_sequence.index(batch_first_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

                else:
                    first_index = pack_sequence.index(batch_first_mfd_pack)
                    mfd_pack_sequence.remove(batch_first_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

            automatic_packs.reverse()
            for pack in automatic_packs:
                remove_pack = pack_sequence.remove(pack)
                pack_sequence.insert(0, pack)

            sorted_list = pack_sequence
            logger.info("In get_mfd_and_automatic_pack_priority: sorted_list: {}, mfd_pack_updated: {}, total_packs: {}, pack_sequence: {}, order_no_list: {}"
                .format(sorted_list, mfd_pack_updated, total_packs, pack_sequence, order_no_list))
        else:
            last_mfd_pack_index = batch_mfd_packs.index(mfd_pack_sequence[-1])
            if last_mfd_pack_index == (len(batch_mfd_packs) - 1):
                batch_last_mfd_pack = mfd_pack_sequence[-1]
            else:
                batch_last_mfd_pack = batch_mfd_packs[last_mfd_pack_index + 1]

            mfd_pack_sequence.reverse()
            query = get_pending_pack_queue_order_pack(system_id=system_id, priority=priority)

            for record in query:
                if len(total_packs):
                    order_no_list.append(record['order_no'])
                    pack_sequence.append(record['id'])
                    if record['id'] in batch_mfd_packs:
                        mfd_pack_updated.append(record['id'])
                    else:
                        pending_automatic_packs.append(record['id'])

                    if record['id'] in total_packs:
                        total_packs.remove(record['id'])
                else:
                    break

            if len(mfd_pack_sequence) == 1 and mfd_pack_sequence[0] == batch_last_mfd_pack:
                remove_pack = pack_sequence.remove(batch_last_mfd_pack)
                pack_sequence.insert(0, batch_last_mfd_pack)

            elif batch_mfd_packs[-1] in mfd_pack_sequence:
                index = 0
                for pack in mfd_pack_sequence:
                    pack_sequence.remove(pack)
                    pack_sequence.insert(index, pack)
                    index += 1

            else:
                if batch_last_mfd_pack not in mfd_pack_sequence:
                    first_index = pack_sequence.index(batch_last_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1
                else:
                    first_index = pack_sequence.index(batch_last_mfd_pack)
                    mfd_pack_sequence.remove(batch_last_mfd_pack)
                    for pack in mfd_pack_sequence:
                        pack_sequence.remove(pack)
                        pack_sequence.insert(first_index + 1, pack)
                        first_index += 1

            # automatic_packs.reverse()
            for pack in automatic_packs:
                remove_pack = pack_sequence.remove(pack)
                pack_sequence.insert(0, pack)

            # pack_sequence.reverse()
            sorted_list = pack_sequence
            logger.info(
                "In get_mfd_and_automatic_pack_priority: sorted_list: {}, mfd_pack_updated: {}, total_packs: {}, pack_sequence: {}, order_no_list: {}"
                .format(sorted_list, mfd_pack_updated, total_packs, pack_sequence, order_no_list))
        return True, pack_sequence, order_no_list, sorted_list

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in get_mfd_and_automatic_pack_priority {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_and_automatic_pack_priority: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise

    except Exception as e:
        logger.error("Error in get_mfd_and_automatic_pack_priority {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_and_automatic_pack_priority: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return False


def get_pack_count(system_id, batch_id, status):
    args = {"system_id": system_id, "batch_id": batch_id, "status": status, "pack_count": True}
    response = get_packs_count_by_status(args)
    return response


@log_args_and_response
def get_pack_to_dispatch(args):
    """
        Function is used to get list of packs ids
        @param args:
        !:return: 1, data if success | 2, msg if mfd not transfers | 0, other error
    """
    # here we will get pending packs for robot id
    system_id = args['system_id']
    pack_count = args.get('pack_count', 1)
    pack_count = 1
    error_code = args.get("error_code")
    list_of_packs = list()
    pack_list_status, pack_list = find_pack_id_by_status(
        {'device_id': int(args['device_id']), 'status': settings.PENDING_PACK_STATUS, "system_id": system_id,
         "error_code": error_code})

    if pack_list_status == 2:
        return 2, "Pending mfd transfers"
    elif pack_list_status:
        count = pack_count if (len(pack_list) >= pack_count) else len(pack_list)
        for pack_no in range(0, count):
            list_of_packs.append(pack_list[pack_no])
        args['pack_id'] = list_of_packs
        args['status'] = settings.PROGRESS_PACK_STATUS
        response = json.loads(set_status(args))

        if response['status']:
            # TODO: Code commented because we are not deleting the packs while they go to In Progress.
            #  Instead when they reach MVS, CRM will send the delete call.
            # logger.debug("Verify if there are any packs on Hold in Ext Pack Details table. If yes, then delete those "
            #              "packs once they are dispatched.")
            # for pack in pack_list:
            #     hold_pack_status = db_check_ext_pack_status_on_hold_by_pack_id_dao(pack_ids=[pack])
            #     if hold_pack_status:
            #         delete_pack_ids.append(pack)
            #
            # args = {"company_id": args["company_id"], "user_id": args["user_id"],
            #         "status": settings.DELETED_PACK_STATUS, "pack_id": delete_pack_ids, "status_changed_from_ips": True,
            #         "reason": constants.DELETE_PACK_DESC_FOR_OLD_PACKS_DISPATCH_CHANGE_RX, "change_rx": True}
            # response = json.loads(set_status(args))
            # logger.debug("set_status response: {}".format(response))

            logger.info('response_dict {}'.format(response['status']))
            return 1, list_of_packs
        else:
            return 0, "error: Unable to set the pack as dispatched."
            # else:
            #
            #     if settings.MODE == settings.MODES['autopilot']:
            #         status, response = cls.dispatch_new_pack_for_autopilot(robot_id, conveyor_id)
            #         # print ("Response from Autopilot: ", status, response)
            #         return status, response
            #     return False, {"status": "success",
            #                    "description": "error: No
            #                    available for robot " + str(robot_id)}

    else:
        return 0, "error: Not able to get pending pack list for the given robot."


@log_args_and_response
def update_pack_queue_seq_by_delivery_date(batch_id, system_id, user_id):
    try:
        update_status = update_sequence_for_mfd_packs(batch_id=batch_id)

        if update_status:
            # if user_id > 0:
            #     logger.info("pack queue sequence changed by {}".format(user_id))
            # message = "Pack queue sequence changed"
            # Notifications(user_id=user_id, call_from_client=True) \
            #     .send_with_username(user_id=settings.ALL_USER_NOTIFICATION, message=message, flow='dp')
            try:
                update_replenish_based_on_system(system_id)
            except (InternalError, IntegrityError) as e:
                logger.error(e, exc_info=True)
                return error(2001, e)
            except ValueError as e:
                return error(2005, str(e))

            return update_status

        else:
            return 0

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.exception("Exception in update_pack_queue_seq_by_delivery_date: ")
        return error(1001, e)


@log_args_and_response
def get_packs_to_process_in_non_tech_mode(system_id, batch_id, user_id, time_zone="UTC"):
    """
    Function to get pack list to process in non tech mode
    @param batch_id:
    @param system_id:
    @param user_id:
    @param time_zone:
    @return:
    """
    try:
        pack_info = get_pending_packs_data_by_batch(batch_id=batch_id)
        mfd_pack_info = db_get_batch_mfd_packs(batch_id=batch_id)
        mfd_pack_date_dict = {int(item['mfd_pack']): item['scheduled_delivery_date'] for item in mfd_pack_info}
        logger.info("In get_packs_to_process_in_non_tech_mode: mfd_pack_date_dict: {}".format(mfd_pack_date_dict))
        current_date = get_current_datetime_by_timezone(time_zone, return_format="date")
        next_date = get_next_date_by_timezone(time_zone, type="date")

        current_date_packs_manual_drug_count = dict()
        next_date_packs_manual_drug_count = dict()
        remaining_packs_manual_drug_count = dict()
        current_date_mfd_pack = None
        next_date_mfd_pack = None
        current_date_mfd_pack_list = list()
        next_date_mfd_pack_list = list()
        pack_list_sequence = list()
        order_number_list = list()

        for pack, pack_data in pack_info.items():
            order_number_list.append(pack_data['order_no'])
            if pack in mfd_pack_date_dict.keys():
                continue
            if pack_data['scheduled_delivery_date'].strftime('%Y-%m-%d') == current_date:
                current_date_packs_manual_drug_count[pack] = pack_data['manual_drug_count']
            elif pack_data['scheduled_delivery_date'].strftime('%Y-%m-%d') == next_date:
                next_date_packs_manual_drug_count[pack] = pack_data['manual_drug_count']
            else:
                remaining_packs_manual_drug_count[pack] = pack_data['manual_drug_count']

        # sort mfd packs according to delivery date such that its sequence is not affected
        mfd_pack_list = deepcopy(list(mfd_pack_date_dict.keys()))
        mfd_pack_list.reverse()
        for pack in mfd_pack_list:
            if current_date_mfd_pack and next_date_mfd_pack:
                break
            if mfd_pack_date_dict[pack].strftime('%Y-%m-%d') == current_date and not current_date_mfd_pack:
                current_date_mfd_pack = pack
            if mfd_pack_date_dict[pack].strftime('%Y-%m-%d') == next_date and not next_date_mfd_pack:
                next_date_mfd_pack = pack

        if current_date_mfd_pack:
            current_mfd_pack_index = list(mfd_pack_date_dict.keys()).index(current_date_mfd_pack)
            current_date_mfd_pack_list = list(mfd_pack_date_dict.keys())[:current_mfd_pack_index + 1]

        if next_date_mfd_pack and next_date_mfd_pack in mfd_pack_date_dict.keys():
            next_mfd_pack_index = list(mfd_pack_date_dict.keys()).index(next_date_mfd_pack)
            next_date_mfd_pack_list = list(mfd_pack_date_dict.keys())[:next_mfd_pack_index + 1]

        if len(current_date_packs_manual_drug_count):
            current_date_packs_manual_drug_count = OrderedDict(
                sorted(current_date_packs_manual_drug_count.items(), key=lambda x: x[1]))
            pack_list_sequence.extend(current_date_packs_manual_drug_count.keys())

        if len(current_date_mfd_pack_list):
            pack_list_sequence.extend(current_date_mfd_pack_list)

        if len(next_date_packs_manual_drug_count):
            next_date_packs_manual_drug_count = OrderedDict(
                sorted(next_date_packs_manual_drug_count.items(), key=lambda x: x[1]))
            pack_list_sequence.extend(next_date_packs_manual_drug_count.keys())

        if len(next_date_mfd_pack_list):
            pack_list_sequence.extend(next_date_mfd_pack_list)

        if len(remaining_packs_manual_drug_count):
            remaining_packs_manual_drug_count = OrderedDict(
                sorted(remaining_packs_manual_drug_count.items(), key=lambda x: x[1]))
            pack_list_sequence.extend(remaining_packs_manual_drug_count.keys())

        if len(mfd_pack_date_dict):
            pack_list_sequence.extend(list(mfd_pack_date_dict.keys()))

        logger.info("In get_packs_to_process_in_non_tech_mode : pack list sequence {}".format(pack_list_sequence))
        if len(pack_list_sequence) > 0:
            status = True
        else:
            status = False

        if status and len(pack_list_sequence):
            logger.info(pack_list_sequence)
            if len(order_number_list) != len(pack_list_sequence):
                logger.error("Error in get_packs_to_process_in_non_tech_mode length not same {}, {}".format(order_number_list, pack_list_sequence))
                return False

            update_status = change_pack_sequence(pack_list=pack_list_sequence, order_number_list=order_number_list)
            logger.info("IN get_packs_to_process_in_non_tech_mode: update_status: {}".format(update_status))

            # if user_id > 0:
            #     logger.info("In get_packs_to_process_in_non_tech_mode: pack queue sequence changed by {}".format(user_id))
            # message = "Pack queue sequence changed"
            # Notifications(user_id=user_id, call_from_client=True) \
            #     .send_with_username(user_id=settings.ALL_USER_NOTIFICATION, message=message, flow='dp')
            try:
                update_replenish_based_on_system(system_id)
            except (InternalError, IntegrityError) as e:
                logger.error(e, exc_info=True)
                raise
            except ValueError as e:
                raise
        else:
            logger.error("In get_packs_to_process_in_non_tech_mode No packs to change status")
            return False

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return False
    except ValueError as e:
        logger.error(e, exc_info=True)
        return False


@log_args_and_response
def update_sequence_for_mfd_packs(batch_id: int) -> bool:
    """
    Function to update sequence for mfd packs
    @param batch_id:
    @return:
    """
    try:
        mfd_pack_dict = db_get_batch_mfd_packs(batch_id)
        mfd_packs = [int(item['mfd_pack']) for item in mfd_pack_dict]

        if len(mfd_packs):
            logger.info("In update_sequence_for_mfd_packs: MFD packs while import {}".format(mfd_packs))
            pack_order_update_status = update_pack_sequence_of_mfd_packs(batch_id, mfd_packs)
            logger.info("In update_sequence_for_mfd_packs: pack_order_update_status {}".format(pack_order_update_status))
            if not pack_order_update_status:
                return False
        else:
            return True

    except ValueError as e:
        return error(2005, str(e))
    except Exception as e:
        logger.exception("Exception in updating pack sequence: ")
        return error(1001, e)


@log_args_and_response
def update_pack_sequence_of_mfd_packs(batch_id: int, mfd_packs: list) -> bool:
    """
    Function to get updated pack sequence of packs considering MFD packs to be moved
    on top
    @param batch_id: int
    @param mfd_packs: list
    @return: status
    """
    automatic_delivery_date_pack_dict = dict()
    mfd_pack_delivery_date_dict = dict()
    delivery_dates = list()
    sorted_mfd_packs_delivery_date = dict()
    updated_mfd_pack_sequence = deepcopy(mfd_packs)
    updated_pack_list = list()
    order_number_list = list()
    try:

        pack_device_dict = get_device_id_for_pack_by_batch(batch_id=batch_id)

        query = get_pending_pack_data_by_batch(batch_id=batch_id)
        for record in query:
            device_id = pack_device_dict[record['id']]
            if device_id not in automatic_delivery_date_pack_dict.keys():
                automatic_delivery_date_pack_dict[device_id] = dict()
            if device_id not in sorted_mfd_packs_delivery_date.keys():
                sorted_mfd_packs_delivery_date[device_id] = dict()

            if not record['order_no']:
                continue
            order_number_list.append(record['order_no'])
            record['scheduled_delivery_date'] = record['scheduled_delivery_date'].strftime("%Y-%m-%d")
            if record['scheduled_delivery_date'] not in delivery_dates:
                delivery_dates.append(record['scheduled_delivery_date'])

            if record['id'] in mfd_packs:
                if device_id not in mfd_pack_delivery_date_dict.keys():
                    mfd_pack_delivery_date_dict[device_id] = dict()

                mfd_pack_delivery_date_dict[device_id][record['id']] = record['scheduled_delivery_date']

            else:
                if record['scheduled_delivery_date'] not in automatic_delivery_date_pack_dict[device_id].keys():
                    automatic_delivery_date_pack_dict[device_id][record['scheduled_delivery_date']] = list()

                automatic_delivery_date_pack_dict[device_id][record['scheduled_delivery_date']].append(record['id'])

        logger.info("In update_pack_sequence_of_mfd_packs: automatic_delivery_date_pack_dict {}".format(automatic_delivery_date_pack_dict))
        logger.info("In update_pack_sequence_of_mfd_packs: mfd_pack_delivery_date_dict {}".format(mfd_pack_delivery_date_dict))

        for pack in mfd_packs:
            pack_device = pack_device_dict[pack]
            sorted_mfd_packs_delivery_date[pack_device][pack] = mfd_pack_delivery_date_dict[pack_device][pack]

        delivery_dates.sort()

        for each_delivery_date in delivery_dates:
            if len(updated_mfd_pack_sequence):
                for device, pack_date_dict in sorted_mfd_packs_delivery_date.items():
                    for pack, date in pack_date_dict.items():
                        if pack in updated_mfd_pack_sequence:
                            if date <= each_delivery_date:
                                updated_pack_list.append(pack)
                                updated_mfd_pack_sequence.remove(pack)
                            else:
                                break

            for device, date_packs in automatic_delivery_date_pack_dict.items():
                if each_delivery_date in date_packs.keys():
                    for each_pack in date_packs[each_delivery_date]:
                        updated_pack_list.append(each_pack)

        if len(updated_mfd_pack_sequence):
            for pack_ in updated_mfd_pack_sequence:
                updated_pack_list.append(pack_)

        if len(updated_pack_list) != len(order_number_list):
            logger.error("Pack list and order list does not match")
            return False

        update_status = change_pack_sequence(pack_list=updated_pack_list, order_number_list=order_number_list)
        logger.info("IN update_pack_sequence_of_mfd_packs: update_status: {}".format(update_status))

        return True

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise
    except ValueError as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e)
        raise



@log_args_and_response
def send_notification_and_get_mfd_packs_for_trolley(batch_id: int, user_id: int,
                                                    system_id: int, company_id: int) -> bool:
    """
    Function to get mfd_pack list and send notification to get trolley
    @param company_id: int
    @param system_id: int
    @param batch_id: int
    @param user_id: int
    @return: status, list
    """
    trolley_notification_sent: list = list()
    try:
        system_device_dict = get_robots_by_systems_dao(system_id_list=[system_id])
        device_ids = system_device_dict[system_id]
        logger.info("In send_notification_and_get_mfd_packs_for_trolley: device_ids: {}".format(device_ids))

        for record in device_ids:
            device_id = record['id']
            trolley_id, system_id, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id, device_id)

            if trolley_id not in trolley_notification_sent:
                trolley_notification_sent.append(trolley_id)
                mfd_analysis_ids, mfs_system_mapping, dest_devices, batch_system = get_trolley_analysis_ids(batch_id,
                                                                                                            trolley_id)
                if mfd_analysis_ids:
                    for device_id in dest_devices:
                        filling_done, transfer_done, trolley_data = check_transfer_filling_pending(
                            mfd_analysis_ids=mfd_analysis_ids, device_id=device_id)

                        if not filling_done or not transfer_done:
                            device_message = dict()
                            logger.info("In send_notification_and_get_mfd_packs_for_trolley: mfd notifications {},  {},  {}".format(
                                    batch_id, dest_devices, user_id))
                            robot_data = get_device_name_from_device([device_id])
                            if trolley_data['cart_id'] and trolley_data['trolley_seq']:
                                device_message[device_id] = constants.REQUIRED_MFD_CART_MESSAGE.format(
                                    trolley_data['cart_name'], robot_data[device_id])
                                unique_id = int(str(trolley_data['cart_id']) + str(trolley_data['trolley_seq']) + str(device_id))
                                logger.info("In send_notification_and_get_mfd_packs_for_trolley message {} and unique_id {}"
                                            .format(device_message, unique_id))
                                Notifications(user_id=user_id, call_from_client=True) \
                                    .send_transfer_notification(user_id=user_id, system_id=batch_system,
                                                                device_message=device_message, batch_id=batch_id, unique_id=unique_id,
                                                                flow='mfd')
                        if filling_done and not transfer_done:
                            # update wizard
                            logger.info('In send_notification_and_get_mfd_packs_for_trolley: getting transfer_wizard_data')
                            status, transfer_wizard_data = get_mfd_wizard_couch_db(company_id=company_id,
                                                                                   device_id=device_id)
                            logger.info('getting_transfer_wizard data {}'.format(transfer_wizard_data))
                            wizard_couch_db_data = transfer_wizard_data.get("data", {})
                            if wizard_couch_db_data:
                                current_module = wizard_couch_db_data.get('module_id', None)
                                transfer_status = wizard_couch_db_data.get('mfd_transfer_to_device', True)
                                in_robot_batch_id, pending_batch_id, status, in_robot_can_status = get_next_mfd_transfer_batch(
                                    device_id=device_id)
                                logger.debug("get_next_mfd_transfer_batch response: {}, {}, {}, {}"
                                             .format(in_robot_batch_id, pending_batch_id, status, in_robot_can_status))
                                # update module after checking if empty canister are left to remove
                                if not in_robot_batch_id and pending_batch_id == batch_id and transfer_status \
                                        and current_module == constants.MFD_TRANSFER_WIZARD_MODULES["TRANSFER_TO_ROBOT_WIZARD"]:
                                    wizard_data = {
                                        'mfd_transfer_to_device': False,
                                        'batch_id': batch_id,
                                        'module_id': constants.MFD_TRANSFER_WIZARD_MODULES[
                                            "TRANSFER_TO_ROBOT_WIZARD"]}
                                    logger.info('updating_transfer_wizard_data: {}'.format(wizard_data))
                                    update_mfd_transfer_wizard_couch_db(device_id, company_id,
                                                                        wizard_data)

        return True

    except Exception as e:
        logger.error(e)
        return False


@log_args_and_response
def assign_user_for_change_rx_packs_from_mvs(pack_id, assigned_to, company_id, user_id):
    pack_id_list = []
    try:
        old_to_new_template = get_new_template_from_old_packs([pack_id])
        if old_to_new_template:
            for old, new in old_to_new_template.items():
                new_packs_details = db_get_new_pack_details_for_template(int(new))

        if new_packs_details:
            pack_id_list = [record['id'] for record in new_packs_details]

        userpacks = {
            'pack_id_list': pack_id_list,
            'assigned_to': assigned_to,
            'company_id': company_id,
            'user_id': user_id,
            'rx_change_pack_ids': pack_id_list
        }
        status = map_user_pack_dao(userpacks=[userpacks])
        return status
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def get_processed_pack_count_by_filled_time(args):
    """
    Function is called when new batch is ready to import.
    Two sub functions update_analysis_data and create_batch are called.
    1) get_packs_count_for_latest_batch : to get the pack count for latest batch
    2) create_batch : sets status of batch to Batch Imported.

    @param args:
    @return: pack_count, batch_id and robot wise pack data
    """
    try:
        start_time = args['start_time']
        end_time = args['end_time']
        system_id = args['system_id']

        pack_count = get_done_pack_count_by_time_filter(start_time, end_time, system_id)
        response = {"processed_pack_count" : pack_count}
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in pack_analysis_v2: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in pack_analysis_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except ValueError as e:
        return error(2005, str(e))

    except Exception as e:
        logger.error("Error in pack_analysis_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in pack_analysis_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in pack_analysis_v2: " + str(e))


@validate(required_fields=["system_id"])
@log_args_and_response
def get_packs_count_by_robot_id_retail(args):
    """
    @param args: robot id
    @return: pack count which are in progress by given robot id
    """

    system_id = args['system_id']
    device_id = list(args['device_id']) if 'device_id' in args and args['device_id'] is not None else None
    robot_wise_pack_count: dict = dict()
    response: list = list()
    device_pack_dict: dict = dict()
    try:

        query = get_pack_count_by_device_id_retail(system_id=system_id, device_id=device_id)

        for record in query:
            if record['device_id']:
                if record['device_id'] not in robot_wise_pack_count.keys():
                    device_pack_dict[record['device_id']] = list()
                    robot_wise_pack_count[record['device_id']] = {"device_id": record['device_id'],
                                                                  "progress_pack_count": 0, "pack_count": 0}

                if record['id'] not in device_pack_dict[record['device_id']]:
                    device_pack_dict[record['device_id']].append(record['id'])
                    if record['pack_status'] == settings.PROGRESS_PACK_STATUS:
                        robot_wise_pack_count[record['device_id']]["progress_pack_count"] += 1

                    if record['pack_status'] not in [settings.MANUAL_PACK_STATUS] and\
                            record['filled_at'] != settings.FILLED_AT_POST_PROCESSING:
                        robot_wise_pack_count[record['device_id']]['pack_count'] += 1

        for key, value in robot_wise_pack_count.items():
            response.append(value)
        logger.info("In get_packs_count_by_robot_id_retail: response : {}".format(response))
        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_packs_count_by_robot_id_retail: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_by_robot_id_retail: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs_count_by_robot_id_retail {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_packs_count_by_robot_id_retail: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_packs_count_by_robot_id_retail: " + str(e))


@log_args_and_response
def get_trolley_seq_data(system_id, pack_list, paginate, filter_fields, internal_call=False):
    trolley_pack_data = OrderedDict()
    delivery_date_dict = {}
    patient_trolley_dict = {}
    pack_trolley_dict = {}
    selected_pack_trolley = []
    ordered_trolley_seq = []
    trolley_patient_data = OrderedDict()
    trolley_travelled = []
    empty_trolley_device_id = []
    trolley_status_dict = {}
    try:
        trolley_data = db_get_trolley_wise_pack_patient_data(system_id, pack_list, paginate, filter_fields)
        progress_trolley = get_mfs_filling_progress_trolley()

        for record in trolley_data:
            trolley_seq = record['trolley_seq']
            transferred_location = record["transferred_location_id"]
            pack_id = record['pack_id']
            mfd_status = record['status_id']
            delivery_date= record['delivery_date']
            patient_name = record["patient_name"]
            patient_id = record["patient_id"]
            pack_status = record["pack_status"]
            in_robot = record["in_robot"]
            if record['device_id'] not in trolley_travelled:
                trolley_travelled.append(record['device_id'])
            if trolley_seq not in delivery_date_dict:
                delivery_date_dict[trolley_seq] = [delivery_date]
            else:
                delivery_date_dict[trolley_seq].append(delivery_date)
            #  Pack Wise Data ....
            if trolley_seq not in trolley_pack_data:
                trolley_pack_data[trolley_seq] = {
                    "trolley_name": record['device_name'],
                    "trolley_pack_count" : 1,
                    "mfd_canister_count": 1,
                    "device_id": record['device_id'],

                    "in_robot": True if in_robot else False,
                    "mfd_status": mfd_status,
                    "pack_dict": {pack_id: {
                        "pack_id": pack_id,
                        "order_no": record["pack_sequence"],
                        "patient_name": record["patient_name"],
                        "admin_period": record["admin_period"],
                        "pack_display_id": record["pack_display_id"],
                    }},
                    "patient_dict": {patient_id: {
                        "patient_name": record["patient_name"],
                        "patient_id": patient_id,
                        "packs": [pack_id],
                        "mfd_canister_count": 1,
                        "delivery_date": delivery_date
                    }
                    }

                }

                trolley_status_dict[trolley_seq] = {mfd_status}
            else:
                if pack_id not in trolley_pack_data[trolley_seq]["pack_dict"]:
                    trolley_pack_data[trolley_seq]["pack_dict"][pack_id] = {
                        "pack_id": pack_id,
                        "order_no": record["pack_sequence"],
                        "patient_name": record["patient_name"],
                        "admin_period": record["admin_period"],
                        "pack_display_id": record["pack_display_id"],
                    }
                    trolley_pack_data[trolley_seq]["trolley_pack_count"] +=1
                if patient_id not in trolley_pack_data[trolley_seq]["patient_dict"]:
                    trolley_pack_data[trolley_seq]["patient_dict"][patient_id] = {
                        "patient_name": record["patient_name"],
                        "patient_id": patient_id,
                        "packs": [pack_id],
                        "mfd_canister_count": 1,
                        "delivery_date": delivery_date
                    }
                else:
                    trolley_pack_data[trolley_seq]["patient_dict"][patient_id]["mfd_canister_count"] += 1
                    if pack_id not in trolley_pack_data[trolley_seq]["patient_dict"][patient_id]["packs"]:
                        trolley_pack_data[trolley_seq]["patient_dict"][patient_id]["packs"].append(pack_id)

                trolley_status_dict[trolley_seq].add(mfd_status)

                # if mfd_status == constants.MFD_CANISTER_IN_PROGRESS_STATUS:
                #     trolley_pack_data[trolley_seq]["mfd_status"] = mfd_status
                # elif mfd_status == constants.MFD_CANISTER_PENDING_STATUS and trolley_pack_data[trolley_seq]["mfd_status"] != constants.MFD_CANISTER_IN_PROGRESS_STATUS:
                #     trolley_pack_data[trolley_seq]["mfd_status"] = mfd_status
                # elif trolley_pack_data[trolley_seq]["mfd_status"] == constants.MFD_CANISTER_SKIPPED_STATUS and mfd_status in [constants.MFD_CANISTER_FILLED_STATUS, constants.MFD_CANISTER_PENDING_STATUS, constants.MFD_CANISTER_IN_PROGRESS_STATUS]:
                #     trolley_pack_data[trolley_seq]["mfd_status"] = mfd_status
                # elif mfd_status == constants.MFD_CANISTER_SKIPPED_STATUS and trolley_pack_data[trolley_seq]["mfd_status"] in [constants.MFD_CANISTER_FILLED_STATUS, constants.MFD_CANISTER_PENDING_STATUS, constants.MFD_CANISTER_IN_PROGRESS_STATUS]:
                #     trolley_pack_data[trolley_seq]["mfd_status"] = mfd_status
                # elif mfd_status == constants.MFD_CANISTER_DROPPED_STATUS:
                #     trolley_pack_data[trolley_seq]["mfd_status"] = constants.MFD_CANISTER_FILLED_STATUS # as it is fillef and droped

                if not trolley_pack_data[trolley_seq]["in_robot"] and in_robot:
                    trolley_pack_data[trolley_seq]["in_robot"] = True
                if pack_status == settings.PROGRESS_PACK_STATUS and  trolley_pack_data[trolley_seq]["mfd_status"] != constants.MFD_CANISTER_SKIPPED_STATUS:
                    trolley_pack_data[trolley_seq]["in_robot"] = True
                trolley_pack_data[trolley_seq]["mfd_canister_count"] += 1

            if record["patient_name"] not in patient_trolley_dict:
                patient_trolley_dict[record["patient_name"]] = [trolley_seq]
            else:
                if trolley_seq not in patient_trolley_dict[record["patient_name"]]:
                    patient_trolley_dict[record["patient_name"]].append(trolley_seq)

            if record["pack_id"] not in pack_trolley_dict:
                pack_trolley_dict[record["pack_id"]] = trolley_seq
        logger.info("In get_trolley_seq_data: trolley_status_dict {}".format(trolley_status_dict))
        for trolley, status in trolley_status_dict.items():
            if constants.MFD_CANISTER_IN_PROGRESS_STATUS in status:
                trolley_pack_data[trolley]["mfd_status"] = constants.MFD_CANISTER_IN_PROGRESS_STATUS
                trolley_pack_data[trolley]["skip_cart"] = True if constants.MFD_CANISTER_PENDING_STATUS in status else False
            elif {constants.MFD_CANISTER_SKIPPED_STATUS} == status:
                trolley_pack_data[trolley]["mfd_status"] = constants.MFD_CANISTER_SKIPPED_STATUS
                trolley_pack_data[trolley]["skip_cart"] = False
            elif (constants.MFD_CANISTER_FILLED_STATUS in status) and (
                    constants.MFD_CANISTER_IN_PROGRESS_STATUS not in status) and (
                    constants.MFD_CANISTER_PENDING_STATUS not in status):
                trolley_pack_data[trolley]["mfd_status"] = constants.MFD_CANISTER_FILLED_STATUS
                trolley_pack_data[trolley]["skip_cart"] = False
            elif constants.MFD_CANISTER_PENDING_STATUS in status:
                trolley_pack_data[trolley]["mfd_status"] = constants.MFD_CANISTER_PENDING_STATUS
                trolley_pack_data[trolley]["skip_cart"] = True
            if trolley in progress_trolley:
                trolley_pack_data[trolley]["mfd_status"] = constants.MFD_CANISTER_IN_PROGRESS_STATUS

        for trolley, date_list in delivery_date_dict.items():
            trolley_pack_data[trolley]["min_trolley_data"] = min(date_list)
            trolley_pack_data[trolley]["max_trolley_data"] = max(date_list)

        if internal_call:
            return trolley_pack_data

        if pack_list:
            for pack in pack_list:
                trolley = pack_trolley_dict.get(pack)
                if trolley and trolley not in selected_pack_trolley:
                    selected_pack_trolley.append(trolley)

        mfd_trolleys = db_get_device_data_by_type(constants.MFD_TROLLEY_DEVICE_TYPE, system_id)

        for trolleys in mfd_trolleys:
            if trolleys['id'] not in trolley_travelled:
                empty_trolley_device_id.append(trolleys['id'])
        if trolley_pack_data:
            ordered_trolley_seq = list(trolley_pack_data.keys())

        response = {
            "trolley_pack_data": trolley_pack_data,
            "patient_trolley_dict": patient_trolley_dict,
            "pack_trolley_dict":pack_trolley_dict,
            "selected_pack_trolley": selected_pack_trolley,
            "ordered_trolley_seq": ordered_trolley_seq,
            "empty_trolley_device_id": empty_trolley_device_id
        }

        return create_response(response)
    except (InternalError, IntegrityError, KeyError, ValueError) as e:
        logger.error("error in get_trolley_seq_data: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_trolley_seq_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_trolley_seq_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_trolley_seq_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_trolley_seq_data: " + str(e))


@log_args_and_response
def update_trolley_seq_pack_queue(args):
    order_no_list = []
    mfd_order_list = []
    analysis_list = []
    old_pack_list = []
    trolley_pack_dict = {}
    trolley_mfd_dict = {}
    sorted_mdf_list = []
    original_trolley_seq = args.get("old_trolley_sequence", [])
    to_be_updated_seq: list = args.get("new_trolley_sequence", [])
    system_id = args['system_id']
    user_id = args['user_id']
    company_id = args.get('company_id', None)
    sorted_pack_list = []
    mfd_location_dict = {}
    old_pack_order_dict = OrderedDict()
    old_mfd_order_dict = OrderedDict()
    update_mfs_data = {}
    device_trolley_pack_dict = OrderedDict()
    device_trolley_mfd_dict = OrderedDict()
    device_trolley_pack_order_no = OrderedDict()
    device_trolley_mfd_order_no = OrderedDict()
    device_pack_order_no = OrderedDict()
    mfd_order_list = []
    device_set = set()
    sorted_pack_order_dict = OrderedDict()
    sorted_mfd_order_dict = OrderedDict()
    updated_trolley_seq = []
    try:
        with db.transaction():
            logger.info(
                ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: original_trolley_seq {}".format(original_trolley_seq)))
            logger.info(
                ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: updated_trolley_seq {}".format(to_be_updated_seq)))

            for old in original_trolley_seq:
                index = to_be_updated_seq.index(old)
                updated_trolley_seq.append(original_trolley_seq[to_be_updated_seq.index(old)])
            updated_seq = list(tuple(zip(original_trolley_seq, updated_trolley_seq)))
            progress_trolley = get_mfs_filling_progress_trolley()
            trolley_data = db_get_trolley_wise_pack(system_id, to_be_updated_seq)

            for data in trolley_data:
                assigned_to = data['assigned_to']
                device_id = data['dest_device_id']
                sys_id = data['system_id']
                trolley_seq = data['trolley_seq']
                pack_status = data['pack_status']
                pack = data['id']
                mfd_order_no = data['mfd_order_no']
                mfd_status = data['status_id']
                order_no = data['order_no']
                analysis_id = data['analysis_id']

                device_set.add(device_id)

                # Further Check
                if pack_status != settings.PENDING_PACK_STATUS and mfd_status != constants.MFD_CANISTER_SKIPPED_STATUS:
                    for old_trolley, new_trolley in updated_seq:
                        if old_trolley == trolley_seq and old_trolley != new_trolley:
                            return error(13014)
                if trolley_seq in progress_trolley:
                    if sys_id not in update_mfs_data:
                        for old, new in updated_seq:
                            if old == trolley_seq and old != new:
                                update_mfs_data[sys_id] = new

                mfd_order_list.append(mfd_order_no)

                # Creating device_trolley_pack_dict
                if device_id not in device_trolley_pack_dict:
                    device_trolley_pack_dict[device_id] = {trolley_seq: [pack]}
                    device_trolley_pack_order_no[device_id] = {trolley_seq: [order_no]}
                    device_pack_order_no[device_id] = [order_no]
                else:
                    if trolley_seq not in device_trolley_pack_dict[device_id]:
                        device_trolley_pack_dict[device_id][trolley_seq] = [pack]
                        device_trolley_pack_order_no[device_id][trolley_seq] = [order_no]
                        device_pack_order_no[device_id].append(order_no)
                    else:
                        if pack not in device_trolley_pack_dict[device_id][trolley_seq]:
                            device_trolley_pack_dict[device_id][trolley_seq].append(pack)
                            device_trolley_pack_order_no[device_id][trolley_seq].append(order_no)
                            device_pack_order_no[device_id].append(order_no)

                # Creating device_trolley_mfd_dict
                if device_id not in device_trolley_mfd_dict:
                    device_trolley_mfd_dict[device_id] = {trolley_seq: [analysis_id]}
                    device_trolley_mfd_order_no[device_id] = {trolley_seq: [mfd_order_no]}
                else:
                    if trolley_seq not in device_trolley_mfd_dict[device_id]:
                        device_trolley_mfd_dict[device_id][trolley_seq] = [analysis_id]
                        device_trolley_mfd_order_no[device_id][trolley_seq] = [mfd_order_no]
                    else:
                        if analysis_id not in device_trolley_mfd_dict[device_id][trolley_seq]:
                            device_trolley_mfd_dict[device_id][trolley_seq].append(analysis_id)
                            device_trolley_mfd_order_no[device_id][trolley_seq].append(mfd_order_no)

                if trolley_seq not in trolley_mfd_dict:
                    trolley_mfd_dict[trolley_seq] = [analysis_id]
                else:
                    trolley_mfd_dict[trolley_seq].append(analysis_id)

            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: device_trolley_mfd_dict {}".format(
                dict(device_trolley_mfd_dict))))
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: device_trolley_mfd_order_no {}".format(
                dict(device_trolley_mfd_order_no))))
            logger.info(
                ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: trolley_mfd_dict {}".format(dict(trolley_mfd_dict))))
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: device_pack_order_no {}".format(
                dict(device_pack_order_no))))
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: device_trolley_pack_order_no {}".format(
                dict(device_trolley_pack_order_no))))
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: device_trolley_pack_dict {}".format(
                dict(device_trolley_pack_dict))))

            mfd_order_list = sorted(mfd_order_list)

            for device_id in device_set:
                sorted_orders = sorted(device_pack_order_no[device_id])
                for trolley_seq in to_be_updated_seq:
                    if trolley_seq in device_trolley_pack_dict[device_id]:
                        for pack in device_trolley_pack_dict[device_id][trolley_seq]:
                            sorted_pack_order_dict[pack] = sorted_orders.pop(0)

            for trolley_seq in to_be_updated_seq:
                for device_id in device_trolley_mfd_dict.keys():
                    if trolley_seq in device_trolley_mfd_dict[device_id]:
                        for analysis_id in device_trolley_mfd_dict[device_id][trolley_seq]:
                            sorted_mfd_order_dict[analysis_id] = mfd_order_list.pop(0)

            # creating pack_id case tuple
            pack_tuple_list = list(
                tuple(zip(map(str, sorted_pack_order_dict.keys()), map(str, sorted_pack_order_dict.values()))))
            pack_list = list(sorted_pack_order_dict.keys())
            mfd_tuple_list = list(
                tuple(zip(map(str, sorted_mfd_order_dict.keys()), map(str, sorted_mfd_order_dict.values()))))
            mfd_list = list(sorted_mfd_order_dict.keys())
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: pack_tuple_list {}".format(pack_tuple_list)))
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: mfd_tuple_list {}".format(mfd_tuple_list)))
            logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: mfd_tuple_list {}".format(mfd_tuple_list)))

            pack_seq = change_pack_sequence(pack_list=pack_list, new_seq_tuple=pack_tuple_list)

            mfd_seq = change_mfd_trolley_sequence(analysis_ids=mfd_list, new_seq_tuple=mfd_tuple_list,
                                                  trolley_mfd_dict=trolley_mfd_dict, updated_seq=updated_seq,
                                                  user_id=user_id)
            if update_mfs_data:
                status = update_trolley_seq_couchdb(update_mfs_data)
                if not status:
                    return error(13011)
            if not pack_seq:
                return error(13010)

            # raise InternalError
        if settings.UPDATE_MFD_CART_RECOMMENDATION and pack_seq:
            assign_trolley_to_sequence_move_to_top(system_id, company_id)

        batch_id = get_progress_batch_id(system_id=system_id)
        logger.info("In update_trolley_seq_pack_queue: batch_id: {}".format(batch_id))
        robot_data = get_robots_by_systems_dao(system_id_list=[system_id])

        for system, device_data in robot_data.items():
            for data in device_data:
                device_id = data['id']
                device_message: dict = dict()
                next_trolley, system_id, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id, device_id)
                if next_trolley and next_trolley_seq and device_id:
                    unique_id = int(str(next_trolley) + str(next_trolley_seq) + str(device_id))
                    # check if notification is already there for next trolley and trolley seq
                    notification_present = Notifications(user_id=user_id, call_from_client=True) \
                            .check_if_notification_is_present(unique_id, device_id, system_id, batch_id)
                    logger.info("In update_trolley_seq_pack_queue: notification already there for next trolley: {}".format(notification_present))
                    if not notification_present:
                        # update action_taken_by for all the messages
                        remove_notifications_for_skipped_mfs_filling(system_id=system_id, device_id=device_id, user_id=user_id, update_all=True)
                        device_id_name_dict = get_device_name_from_device([device_id])
                        logger.info("In update_trolley_seq_pack_queue: device_id_name_dict: {}".format(device_id_name_dict))
                        message = constants.REQUIRED_MFD_CART_MESSAGE.format(next_trolley_name, device_id_name_dict[device_id])
                        device_message[device_id] = message
                        logger.info("In update_trolley_seq_pack_queue: device_message: {}, unique_id: {}".format(device_message, unique_id))
                        # add new notification for next trolley
                        Notifications(user_id=user_id, call_from_client=True) \
                            .send_transfer_notification(user_id=user_id, system_id=system_id,
                                                        device_message=device_message, unique_id=unique_id,
                                                        batch_id=batch_id, flow='mfd')
                    else:
                        remove_notifications_for_skipped_mfs_filling(system_id=system_id, device_id=device_id, remove_action_taken_by=True)
        return create_response(True)

    except (InternalError, IntegrityError, IndexError, ValueError) as e:
        logger.error("error in update_trolley_seq_pack_queue: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_trolley_seq_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_trolley_seq_pack_queue {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_trolley_seq_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_trolley_seq_pack_queue: " + str(e))


#
# @log_args_and_response
# def org_update_trolley_seq_pack_queue(args):
#     order_no_list = []
#     mfd_order_list = []
#     analysis_list = []
#     old_pack_list = []
#     trolley_pack_dict = {}
#     trolley_mfd_dict = {}
#     sorted_mdf_list = []
#     original_trolley_seq = args.get("old_trolley_sequence", [])
#     updated_trolley_seq = args.get("new_trolley_sequence", [])
#     system_id = args['system_id']
#     user_id = args['user_id']
#     sorted_pack_list = []
#     mfd_location_dict = {}
#     old_pack_order_dict = OrderedDict()
#     old_mfd_order_dict = OrderedDict()
#     update_mfs_data = {}
#     try:
#         with db.transaction():
#             logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: original_trolley_seq {}".format(original_trolley_seq)))
#             logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: updated_trolley_seq {}".format(updated_trolley_seq)))
#             updated_seq = list(tuple(zip(original_trolley_seq, updated_trolley_seq)))
#             trolley_data = db_get_trolley_wise_pack(system_id, updated_trolley_seq)
#
#             for data in trolley_data:
#                 assigned_to = data['assigned_to']
#                 device_id = data['mfs_device_id']
#                 system_id = data['system_id']
#                 trolley_seq_id = data['trolley_seq']
#                 if data["status_id"] == constants.MFD_CANISTER_IN_PROGRESS_STATUS:
#                     if system_id not in update_mfs_data:
#                         for old, new in updated_seq:
#                             if old == trolley_seq_id and old != new:
#                                 update_mfs_data[system_id] = new
#                 pack = data['id']
#                 order_no = data['order_no']
#                 analysis_id = data['analysis_id']
#                 mfd_order_no = data['mfd_order_no']
#                 if trolley_seq_id not in trolley_pack_dict:
#                     trolley_pack_dict[trolley_seq_id] = [pack]
#                     order_no_list.append(order_no)
#                     old_pack_list.append(pack)
#                 else:
#                     if pack not in trolley_pack_dict[trolley_seq_id]:
#                         trolley_pack_dict[trolley_seq_id].append(pack)
#                         order_no_list.append(order_no)
#                         old_pack_list.append(pack)
#
#                 old_pack_order_dict[pack] = order_no
#
#                 if trolley_seq_id not in trolley_mfd_dict:
#                     trolley_mfd_dict[trolley_seq_id] = [analysis_id]
#                 else:
#                     trolley_mfd_dict[trolley_seq_id].append(analysis_id)
#
#
#                 analysis_list.append(analysis_id)
#                 mfd_order_list.append(mfd_order_no)
#                 old_mfd_order_dict[analysis_id] = mfd_order_no
#
#             # Sort packs by trolley.
#             for trolley in updated_trolley_seq:
#                 sorted_pack_list += trolley_pack_dict[trolley]
#                 sorted_mdf_list += trolley_mfd_dict[trolley]
#             logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: pack-orderno {}".format(old_pack_order_dict)))
#             logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: mfd-orderno {}".format(old_mfd_order_dict)))
#             logger.info(("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: trolley_pack_dict {}".format(trolley_pack_dict)))
#
#             logger.info(
#                 ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: old_pacK_seq {}".format(old_pack_list)))
#             logger.info(
#                 ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: new_pacK_seq {}".format(sorted_pack_list)))
#             logger.info(
#                 ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: order_no_list {}".format(order_no_list)))
#
#             pack_seq = change_pack_sequence(sorted_pack_list, order_no_list)
#             logger.info(
#                 ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: sorted_mdf_list {}".format(sorted_mdf_list)))
#             logger.info(
#                 ("PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: trolley_mfd_dict {}".format(trolley_mfd_dict)))
#             if len(sorted_mdf_list) != len(mfd_order_list):
#                 logger.error(
#                     "PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: Length of analysis_ids and mfd_order no does not match mfd_order_list {}".format(
#                         mfd_order_list))
#                 return error(13012)
#             if len(mfd_order_list) != len(set(mfd_order_list)):
#                 logger.error(
#                     "PACK_QUEUE_PACK_SEQUENCE_CHANGE: TROLLEY: Error in order no list mfd_order_list {}".format(
#                         mfd_order_list))
#                 return error(13013)
#             mfd_seq = change_mfd_trolley_sequence(sorted_mdf_list, mfd_order_list, updated_trolley_seq, trolley_mfd_dict, updated_seq, user_id)
#             if update_mfs_data:
#                 status = update_trolley_seq_couchdb(update_mfs_data)
#                 if not status:
#                     return error(13011)
#             if not pack_seq:
#                 return error(13010)
#         return True
#
#     except (InternalError, IntegrityError) as e:
#         logger.error("error in update_trolley_seq_pack_queue: {}".format(e))
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(f"Error in update_trolley_seq_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
#         return error(2001)
#
#     except Exception as e:
#         logger.error("Error in update_trolley_seq_pack_queue {}".format(e))
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(f"Error in update_trolley_seq_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
#         return error(1000, "Error in update_trolley_seq_pack_queue: " + str(e))


@log_args_and_response
def auto_merge_batch_packs(system_id, batch_id, progress_batch_id, user_id, company_id):
    final_pack_list = []
    final_pack_order_dict = {}
    old_identifier = 'o'
    new_identifier = 'n'
    update_mfs_data = {}
    empty_trolley_device_id = []
    try:

        response_dict = get_db_data_for_batch_merge(system_id=system_id, merge_batch_id=batch_id,
                                                    imported_batch_id=progress_batch_id)

        o_d_p_dict = response_dict["o_d_p_dict"]
        o_d_p_ord_dict = response_dict["o_d_p_ord_dict"]
        n_d_p_dict = response_dict["n_d_p_dict"]
        n_d_p_ord_dict = response_dict["n_d_p_ord_dict"]
        all_p_ord_dict = response_dict["all_p_ord_dict"]
        o_d_ts_p_dict = response_dict["o_d_ts_p_dict"]
        n_d_ts_p_dict = response_dict["n_d_ts_p_dict"]
        auto_p_del_dict = response_dict["auto_p_del_dict"]
        o_ts_del_min_max = response_dict["o_ts_del_min_max"]
        n_ts_del_min_max = response_dict["n_ts_del_min_max"]
        d_p_ord_dict = response_dict["d_p_ord_dict"]
        d_ma_ord_dict = response_dict["d_ma_ord_dict"]
        o_ts_ma_dict = response_dict["o_ts_ma_dict"]
        n_ts_ma_dict = response_dict["n_ts_ma_dict"]
        n_del_date_trolley_seq = response_dict["n_del_date_trolley_seq"]
        o_del_date_trolley_seq = response_dict["o_del_date_trolley_seq"]
        del_date_list = response_dict["del_date_list"]
        device_set = response_dict["device_set"]
        progress_trolley = response_dict["progress_trolley"]
        d_auto_p_del_dict = response_dict["d_auto_p_del_dict"]
        trolley_travelled = response_dict["trolley_travelled"]
        max_trolley_old_batch = response_dict["max_trolley_old_batch"]
        freeze_trolley = 2   # if required convert this to variable
        mfd_trolleys = db_get_device_data_by_type(constants.MFD_TROLLEY_DEVICE_TYPE, system_id)
        in_robot_trolleys = db_get_in_robot_mfd_trolley(system_id)

        for trolleys in mfd_trolleys:
            if trolleys['id'] not in trolley_travelled or trolleys['id']  not in in_robot_trolleys:
                empty_trolley_device_id.append(trolleys['id'])

        # logic begins

        # 1. if needed freeze 1st trolley from old_trolley. use dict o_ts_del_min_max.keys() for list of trolleys

        # 2. sort del_date_list
        del_date_list.sort()
        # old_trolley_list = o_ts_del_min_max.keys()
        # new_trolley_list = n_ts_del_min_max.keys()
        # no_of_trolley_seq = len(old_trolley_list) + len(new_trolley_list)
        # final_trolley_list = [0 for _ in range(len(old_trolley_list) + len(new_trolley_list))]
        final_trolley_list = []
        temp_del_date_list = deepcopy(del_date_list)
        del_date_end_trolley = {}  # for now, we are assuming that we are putting new trolley after old
        # 3. for date in del_date_list
        temp_o_del_date_trolley_seq = deepcopy(o_del_date_trolley_seq)
        temp_n_del_date_trolley_seq = deepcopy(n_del_date_trolley_seq)
        '''
        Write freeze logic here
        
        '''
        logger.info("In auto_merge_batch_packs: empty_trolley_device_id: {}".format(empty_trolley_device_id))
        if not len(empty_trolley_device_id) and len(o_ts_del_min_max.keys()):
            for i in range(min(freeze_trolley, len(list(o_ts_del_min_max.keys())))):
                t = list(o_ts_del_min_max.keys())[i]
                # need more definition to this
                trolley = old_identifier + str(t)
                final_trolley_list.append(trolley)
            logger.info("In auto_merge_batch_packs: final_trolley_list after Freeze: {}".format(final_trolley_list))

        while len(temp_del_date_list):
            date = temp_del_date_list.pop(0)
            old_trollies = temp_o_del_date_trolley_seq.pop(date, [])
            new_trollies = temp_n_del_date_trolley_seq.pop(date, [])
            old_trollies = [old_identifier + str(x) for x in old_trollies]
            new_trollies = [new_identifier + str(x) for x in new_trollies]

            if new_trollies:
                del_date_end_trolley[date] = max(new_trollies)
            elif old_trollies:
                del_date_end_trolley[date] = max(old_trollies)

            for trolley in old_trollies:
                if trolley not in final_trolley_list:
                    final_trolley_list.append(trolley)
            for trolley in new_trollies:
                if trolley not in final_trolley_list:
                    final_trolley_list.append(trolley)

        # trolley is sorted.. no create pack-list by adding all
        logger.info("In auto_merge_batch_packs: final_trolley_list: {}".format(final_trolley_list))

        # total packs check:
        all_packs = {}
        for device in device_set:
            if device:
                all_packs[device] = list()
                if device in o_d_ts_p_dict:
                    for t, pack_list in o_d_ts_p_dict[device].items():
                        err = set(all_packs[device]).intersection(pack_list)
                        if err:
                            raise InternalError("Pack already in list in | auto packs {}".format(
                                err))
                        all_packs[device] += pack_list
                if device in n_d_ts_p_dict:
                    for t, pack_list in n_d_ts_p_dict[device].items():
                        err = set(all_packs[device]).intersection(pack_list)
                        if err:
                            raise InternalError("Pack already in list in | auto packs {}".format(
                                err))
                        all_packs[device] += pack_list
                if device in d_auto_p_del_dict:
                    for d_date, pack_list in d_auto_p_del_dict[device].items():
                        err = set(all_packs[device]).intersection(pack_list)
                        if err:
                            raise InternalError("Pack already in list in | auto packs {}".format(
                                err))
                        all_packs[device] += pack_list
                # check length
                if len(all_packs[device]) != len(d_p_ord_dict[device]):
                    logger.error("In auto_merge_batch_packs: all_packs {}".format(all_packs))
                    raise InternalError("Pack List length and order list length do not match")

        # Appending packs date wise -> device_wise -> trolley_wise
        d_p_ord_dict = {k: sorted(v) for k, v in d_p_ord_dict.items()}
        for date in del_date_list:
            for device_id in device_set:
                order_list = d_p_ord_dict[device_id]
                max_trolley = del_date_end_trolley.get(date, None)
                for trolley in final_trolley_list:
                    identifier, trolley_id = trolley[0], int(trolley[1:])

                    if identifier == old_identifier:
                        # min_del, max_dal = o_ts_del_min_max[trolley_id][0], o_ts_del_min_max[trolley_id][1]
                        if device_id in o_d_ts_p_dict:
                            if date in o_del_date_trolley_seq and trolley_id in o_del_date_trolley_seq[
                                    date] and trolley_id in o_d_ts_p_dict[device_id]:
                                # add packs for this trolley
                                pack_list = o_d_ts_p_dict[device_id][trolley_id]
                                add_packs(pack_ids=pack_list, pack_list=final_pack_list, order_list=order_list,
                                          pack_order_dict=final_pack_order_dict, device_id=device_id, del_date=date,
                                          pack_type="Old_Trolley", trolley_id=trolley_id)
                                del o_d_ts_p_dict[device_id][trolley_id]

                    if identifier == new_identifier:
                        # min_del, max_dal = o_ts_del_min_max[trolley_id][0], o_ts_del_min_max[trolley_id][1]
                        if device_id in n_d_ts_p_dict:
                            if date in n_del_date_trolley_seq and trolley_id in n_del_date_trolley_seq[
                                    date] and trolley_id in n_d_ts_p_dict[device_id]:
                                # add packs for this trolley
                                pack_list = n_d_ts_p_dict[device_id][trolley_id]
                                add_packs(pack_ids=pack_list, pack_list=final_pack_list, order_list=order_list,
                                          pack_order_dict=final_pack_order_dict, device_id=device_id, del_date=date,
                                          pack_type="New_Trolley", trolley_id=trolley_id)
                                del n_d_ts_p_dict[device_id][trolley_id]

                    if trolley == max_trolley:
                        # add this del date auto packs packs and remove del date
                        if device_id in d_auto_p_del_dict:
                            if date in d_auto_p_del_dict[device_id]:
                                pack_list = d_auto_p_del_dict[device_id][date]
                                add_packs(pack_ids=pack_list, pack_list=final_pack_list, order_list=order_list,
                                          pack_order_dict=final_pack_order_dict, device_id=device_id, del_date=date,
                                          pack_type="Auto_After_Trolley")
                                del d_auto_p_del_dict[device_id][date]

                if device_id in d_auto_p_del_dict:
                    if date in d_auto_p_del_dict[device_id]:
                        # check if del date is not removed for auto packs
                        pack_list = d_auto_p_del_dict[device_id][date]
                        add_packs(pack_ids=pack_list, pack_list=final_pack_list, order_list=order_list,
                                  pack_order_dict=final_pack_order_dict, device_id=device_id, del_date=date,
                                  pack_type="No_Trolley_Auto_Packs")
                        del d_auto_p_del_dict[device_id][date]


        # Managing trolley sequence
        all_trolley_ids = list(o_ts_del_min_max.keys())
        new_trolley_len = len(n_ts_del_min_max.keys())
        if all_trolley_ids:
            max_old_trolley = max(all_trolley_ids)
            for i in range(max_old_trolley + 1, max_old_trolley + new_trolley_len +1):
                all_trolley_ids.append(i)
            if len(final_trolley_list) != len(all_trolley_ids):
                logger.error("In auto_merge_batch_packs: all_trolley_ids {}".format(all_trolley_ids))
                raise InternalError("Trolley Lenght Does Not Match")
        else:
            temp_trolley_ids = list(n_ts_del_min_max.keys())
            all_trolley_ids = [x + max_trolley_old_batch for x in temp_trolley_ids]
            if len(final_trolley_list) != len(all_trolley_ids):
                logger.error("In auto_merge_batch_packs: all_trolley_ids {}".format(all_trolley_ids))
                raise InternalError("Trolley Lenght Does Not Match")

        update_to_trolley_seq = list(tuple(zip(final_trolley_list, all_trolley_ids)))
        logger.info("In auto_merge_batch_packs: update_to_trolley_seq: {}".format(update_to_trolley_seq))

        all_ma_order_list = []
        for device in d_ma_ord_dict.keys():
            all_ma_order_list = all_ma_order_list + d_ma_ord_dict[device]

        all_ma_order_list.sort()
        change_in_old_trolley_seq = {}
        change_in_new_trolley_seq = {}
        final_ma_dict_in_order = []
        trolley_seq_ma_change_dict = {}
        ma_trolley_change_dict = {}
        for trolley, new in update_to_trolley_seq:
            identifier, trolley_id = trolley[0], int(trolley[1:])

            if identifier == old_identifier:
                change_in_old_trolley_seq[trolley_id] = new
                final_ma_dict_in_order += o_ts_ma_dict[trolley_id]
                trolley_seq_ma_change_dict[new] = o_ts_ma_dict[trolley_id]
                for ma in o_ts_ma_dict[trolley_id]:
                    ma_trolley_change_dict[ma] = new

                if trolley_id in progress_trolley:
                    sys_id = progress_trolley[trolley_id]
                    if sys_id not in update_mfs_data:
                        update_mfs_data[sys_id] = new

            elif identifier == new_identifier:
                change_in_new_trolley_seq[trolley_id] = new
                final_ma_dict_in_order += n_ts_ma_dict[trolley_id]
                trolley_seq_ma_change_dict[new] = n_ts_ma_dict[trolley_id]
                for ma in n_ts_ma_dict[trolley_id]:
                    ma_trolley_change_dict[ma] = new

        ma_trolley_tuple_list = list(
            tuple(zip(map(str, ma_trolley_change_dict.keys()), map(str, ma_trolley_change_dict.values()))))
        logger.info("In auto_merge_batch_packs: ma_trolley_tuple_list: {}".format(ma_trolley_tuple_list))

        pack_order_tuple_list = list(
            tuple(zip(map(str, final_pack_order_dict.keys()), map(str, final_pack_order_dict.values()))))
        logger.info("In auto_merge_batch_packs: pack_order_tuple_list: {}".format(pack_order_tuple_list))

        ma_order_tuple_list = list(tuple(zip(map(str, final_ma_dict_in_order), map(str, all_ma_order_list))))
        logger.info("In auto_merge_batch_packs: ma_order_tuple_list: {}".format(ma_order_tuple_list))

        merge_batch_dao(pack_seq_tuple=pack_order_tuple_list, mfd_order_seq_tuple=ma_order_tuple_list,
                        mfd_trolley_seq_tuple=ma_trolley_tuple_list,
                        imported_batch_id=progress_batch_id, merge_batch_id=batch_id,
                        pack_ids=list(final_pack_order_dict.keys()), analysis_ids=list(ma_trolley_change_dict.keys()),
                        user_id=user_id)

        new_batch_pack_ids = []
        new_batch_pack_ids = [pack for device in n_d_p_dict.keys() for pack in n_d_p_dict[device]]
        db_update_batch_id_after_merged(batch_id=batch_id, progress_batch_id=progress_batch_id,
                                        batch_packs=new_batch_pack_ids)

        if update_mfs_data:
            status = update_trolley_seq_couchdb(update_mfs_data)
            if not status:
                return error(13011)

        if settings.UPDATE_MFD_CART_RECOMMENDATION:
            assign_trolley_to_sequence_move_to_top(system_id, company_id)

        return True
    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("error in auto_merge_batch_packs: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in auto_merge_batch_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("Error in auto_merge_batch_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in auto_merge_batch_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def add_packs(pack_ids, pack_list, order_list, pack_order_dict, del_date, device_id, pack_type, trolley_id = None):
    try:
        for pack in pack_ids:
            pack_list.append(pack)
            pack_order_dict[pack] = order_list.pop(0)

    except (InternalError, IntegrityError) as e:
        logger.error("error in auto_merge_batch_packs | add_packs: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in auto_merge_batch_packs | add_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("Error in auto_merge_batch_packs | add_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in auto_merge_batch_packs | add_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


def change_trolley_seq(trolley_change_dict, trolley_mfd_analysis_dict):
    try:
        pass

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_trolley_seq_pack_queue: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_trolley_seq_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_trolley_seq_pack_queue {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_trolley_seq_pack_queue: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_trolley_seq_pack_queue: " + str(e))



@log_args_and_response
def assign_trolley_to_sequence_move_to_top(system_id, company_id):
    unassigned_trolley_seq = []
    to_trigger = False
    replaceable = []
    trolley_status_dict = OrderedDict()
    rm_assigned_trolley = []
    last_trolley = None
    try:
        if not company_id or not system_id:
            raise InternalError("Parameter missing. company_id or system_id")
        # 1. fetch all trolley
        trolley_data = get_trolley_seq_data(system_id=system_id, internal_call=True, pack_list=[], paginate=None,
                                            filter_fields=None)

        # 2. for trolley in trolleys:
        # if trolley not assigned cart, add to pending_trolley else pass
        # if len of pending trolley: if cart is assigned..  trigger change = true
        if trolley_data:
            trolley_data = OrderedDict(sorted(trolley_data.items()))
        all_trolley = list(trolley_data.keys())
        for trolley in all_trolley[::-1]:
            if trolley_data[trolley]['device_id']:
                last_trolley = trolley
                break
        for trolley_seq, data in trolley_data.items():
            status = data['mfd_status']
            device_id = data['device_id']
            if last_trolley and trolley_seq > last_trolley:
                break
            trolley_status_dict[trolley_seq] = status
            # if to_trigger and not device_id:
            #     break
            if not device_id:
                unassigned_trolley_seq.append(trolley_seq)
            if len(unassigned_trolley_seq) and device_id:
                to_trigger = True

        logger.info("In assign_trolley_to_sequence_move_to_top unassigned_trolley_seq :{}".format(unassigned_trolley_seq))
        logger.info("In assign_trolley_to_sequence_move_to_top trolley_status_dict :{}".format(trolley_status_dict))
        # all_trolley = list(trolley_data.keys())
        if to_trigger:
            for _ in unassigned_trolley_seq:
                for replaceable in all_trolley[::-1]:
                    # replaceable = all_trolley.pop()
                    if not trolley_data[replaceable]['device_id']:
                        continue
                    if trolley_data[replaceable]['mfd_status'] == constants.MFD_CANISTER_PENDING_STATUS:
                        rm_assigned_trolley.append(replaceable)
                        break
                    else:
                        break
                if replaceable in rm_assigned_trolley:
                    all_trolley.remove(replaceable)

        logger.info("In assign_trolley_to_sequence_move_to_top rm_assigned_trolley :{}".format(rm_assigned_trolley))

        if rm_assigned_trolley:
            batch_id = remove_trolley_location(rm_assigned_trolley)

            if batch_id:
                args = {'batch_id': batch_id, 'company_id': company_id}
                update_pending_mfd_assignment(args)

    except (InternalError, IntegrityError, IndexError, ValueError) as e:
        logger.error("error in assign_trolley_to_sequence_move_to_top: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in assign_trolley_to_sequence_move_to_top: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in assign_trolley_to_sequence_move_to_top {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in assign_trolley_to_sequence_move_to_top: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in assign_trolley_to_sequence_move_to_top: " + str(e))
