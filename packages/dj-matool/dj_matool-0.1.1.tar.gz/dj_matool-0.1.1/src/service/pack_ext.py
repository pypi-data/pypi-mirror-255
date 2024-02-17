import json
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict, Any

from peewee import IntegrityError, InternalError, DoesNotExist, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, ips_response
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from dosepack.validation.validate import validate
from src import constants
from src.dao.device_manager_dao import get_system_id_based_on_device_type
from src.dao.ext_change_rx_couchdb_dao import update_couch_db_batch_distribution_status
from src.dao.ext_change_rx_dao import db_check_ext_pack_status_on_hold_dao, db_get_pack_display_ids_on_hold_dao
from src.dao.misc_dao import get_company_setting_by_company_id
from src.dao.pack_dao import insert_record_in_reuse_pack_drug, get_reusable_pack_dao
from src.dao.pack_errors_dao import save_pack_error_from_ips
from src.dao.pack_ext_dao import db_get_templates_by_pharmacy_fill_ids, save_ext_pack_data, \
    db_get_pack_data_by_pack_display_id, get_packs_based_on_flow, \
    update_ext_pack_data, db_get_template_info_by_pack_display_id, db_check_pack_user_map_data_dao, \
    check_other_packs_of_that_patients, get_ext_pack_data_by_pack_display_id, db_update_ext_pharmacy_pack_status, \
    db_insert_many_records_in_ext_pack_details_dao, db_update_ext_packs_delivery_status_dao
from src.exc_thread import ExcThread
from src.exceptions import RealTimeDBException
from src.service.notifications import Notifications
from src.pack_ext import logger
from src.service.generate_templates import rollback_templates
from src.service.misc import get_userid_by_ext_username, real_time_db_timestamp_trigger, get_users_by_ids, \
    update_timestamp_couch_db_pre_processing_wizard
from src.service.pack import set_status
from src.service.prn_vial_filling import delete_pack


@log_args_and_response
def db_get_ext_status_by_pack_status(pack_data, delivered_packs=None):
    pack_user_map_data_exists: bool = False
    try:
        done_pack_status: List[int] = list(set(settings.PACK_PROGRESS_DONE_STATUS_LIST) -
                                           set([settings.PROGRESS_PACK_STATUS]))
        logger.debug("Pack ID: {}, Pack Status: {}, Batch ID: {}".format(pack_data["id"], pack_data["pack_status"],
                                                                         pack_data["batch_id"]))

        if pack_data["pack_status"] == settings.DELETED_PACK_STATUS:
            return constants.EXT_PACK_STATUS_CODE_DELETED

        pack_user_map_data_exists = db_check_pack_user_map_data_dao(pack_id=pack_data["id"])
        if pack_data["pack_status"] in done_pack_status or \
                (pack_data["pack_status"] in [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                              settings.PARTIALLY_FILLED_BY_ROBOT] and pack_user_map_data_exists):
            technician_fill_status = constants.EXT_PACK_STATUS_CODE_DELETED
        else:
            logger.info("For all remaining cases, we need to put Ext Pack Details record on Hold...")
            technician_fill_status = constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD
            # if pack_data["batch_id"]:
            #     technician_fill_status = constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD
            # else:
            #     technician_fill_status = constants.EXT_PACK_STATUS_CODE_DELETED
        # Overwriting technician_fill_status it there is any old delivered packs as currently in that
        # case we are only putting old packs on hold
        if delivered_packs:
            logger.info(
                "# Overwriting technician_fill_status it there is any old delivered packs as currently "
                "in that case we are only putting old packs on hold.. pack_data = {}".format(pack_data))
            technician_fill_status = constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD

        return technician_fill_status
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_ext_packs_delete_status(pack_ids, hold_pack_ids, batch_pack_ids, ext_hold_pack_list, ext_pack_list):
    try:
        logger.debug("Move the packs from Hold to Delete when they needs to be deleted as they are neither Change Rx "
                     "nor their packs are earlier marked as Hold..")
        pack_ids = list(set(pack_ids) | set(batch_pack_ids))
        hold_pack_ids = list(set(hold_pack_ids) - set(batch_pack_ids))

        for ext_pack in ext_hold_pack_list:
            if ext_pack["pack_id"] in batch_pack_ids:
                ext_pack["ext_status_id"] = constants.EXT_PACK_STATUS_CODE_DELETED
                ext_pack["ext_comment"] = constants.DELETE_REASON_EXT_CHANGE_RX
            ext_pack_list.append(ext_pack)

        return pack_ids, hold_pack_ids, ext_hold_pack_list, ext_pack_list
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@validate(required_fields=["pack_display_ids", "technician_fill_status",
                           "technician_user_name", "company_id"])
@log_args_and_response
def update_ext_pack_status(request_args):
    """
    Performs template rollback for given pack_display_ids
    :param request_args: dict
    :return: str
    i.e., request_args:
                {'pack_display_ids': [1705923, 1706046, 1706047, 1706048],
                'technician_fill_status': 161,
                'technician_user_name': 'nancyr',
                'technician_fill_comment': 'Deleted from Pharmacy Software due to Change Rx workflow.',
                'user_id': 13,
                'company_id': 3,
                'change_rx': True,
                'ext_change_rx_id': 23,
                'delivered_packs': []}
    """
    all_pack_display_ids = list(set(request_args['pack_display_ids']))
    ips_username = request_args['technician_user_name']
    company_id = request_args["company_id"]
    is_retail = request_args.get("is_retail")
    if is_retail:
        all_pack_display_ids = ', '.join(map(str, all_pack_display_ids))
        status = delete_pack({"pack_id": str(all_pack_display_ids)})
        return ips_response(200, 'ok')
    technician_fill_status = int(request_args["technician_fill_status"])
    technician_fill_error_comment = str(request_args.get("technician_fill_error_comment", None))
    pharmacy_pack_status = request_args.get("pack_status", None)
    reason = request_args.get('technician_fill_comment')
    template_dict = dict()
    template_ids = list()
    ext_pack_list = list()
    ext_hold_pack_list = list()
    pack_display_ids_with_error = list()
    pack_dict = dict()
    pack_ids = list()
    deleted_pack_ids = list()
    template_ext_pack_list = list()
    deleted_pack_display_ids = list()
    change_rx: bool = request_args.get("change_rx", False)
    ext_change_rx_id: int = request_args.get("ext_change_rx_id", None)
    force_delete: bool = request_args.get("force_delete", False)
    delivered_packs_display_ids: list = request_args.get("delivered_packs", list())
    delivered_packs: list = list()
    all_rxs_on_hold: bool = request_args.get("all_rxs_on_hold", False)
    return_from_the_delivery_packs = request_args.get("return_from_the_delivery_packs", None)
    update_couch_db = False
    cdb_batch_distribution = None
    if all_rxs_on_hold:
        update_couch_db = True
    patient_id: int = 0
    ext_update_dict = None
    asrs_data: Dict[str, Any] = dict()
    hold_pack_ids: List[int] = []
    hold_pack_display_ids: List[int] = []
    ext_pack_display_ids: List[int] = []
    ext_hold_flag_exists: bool = False
    distinct_ext_pack_status: List[int] = []
    batch_dict: Dict[int, List[int]] = defaultdict(list)
    hold_to_delete_pack_ids: List[int] = []
    ext_dict: Dict[str, Any] = {}
    change_rx_hold_pack_ids: List[int] = []
    user_lastname_firstname: str = ""
    not_partially_filled_status_packs = {}
    partially_filled_packs = {}

    pharmacy_pack_status_id = constants.PHARMACY_PACK_STATUS_DICT[pharmacy_pack_status] if pharmacy_pack_status else None

    try:
        if technician_fill_status == constants.EXT_PACK_STATUS_CODE_DELETED:
            if not reason:
                reason = 'Deleted from Pharmacy Software'

            if not all_pack_display_ids:
                logger.error("empty pack_display_ids")
                return error(5008)
            if delivered_packs_display_ids:
                # to save in database, convert pack_display_id to pack_id
                pack_dict = db_get_pack_data_by_pack_display_id(pack_display_ids=delivered_packs_display_ids,
                                                                company_id=company_id)
                for pack, pack_data in pack_dict.items():
                    delivered_packs.append(pack_data['id'])

            # Bellow is a patch where in case of all Rx get on hold, IPS will send this key so we will delete all packs
            if not all_rxs_on_hold:
                # Bypassing delete call from IPS in case when they send ips_username as 'system' .
                # The deletion of these packs will be done after new packs arrive
                if ips_username == 'system':
                    #  PATCH ALERT
                    ext_update_pharmacy_pack_status(all_pack_display_ids, pharmacy_pack_status_id)

                    logger.info("In update_ext_pack_status, bypassing delete call when ips_username is 'system'.")
                    return ips_response(200, 'ok')

                # fetch userid based on ips_username
                user_info = get_userid_by_ext_username(ips_username, company_id)

                logger.info(
                    "In update_ext_pack_status: User Id fetched ={}".format(user_info)) if user_info else logger.info(
                    "In update_ext_pack_status: No user found for ips_user_name")

                if not change_rx:
                    if user_info and "id" in user_info:
                        user_id = user_info["id"]
                        user_lastname_firstname = user_info["last_name"] + ", " + user_info["first_name"]
                    else:
                        logger.error("Error while fetching user_info for technician_user_name {}".format(ips_username))
                        return error(5006)
                    logger.info("userinfo: {} for ips_username: {}".format(user_info, ips_username))
                    logger.debug("User LastName, Firstname: {}".format(user_lastname_firstname))
                else:
                    logger.info("change_rx_logger_debug_string: in UpdateExtPackFillStatus")
                    user_id = request_args.get("user_id", None)
                    if user_id:
                        if user_info and "id" in user_info:
                            user_lastname_firstname = user_info["last_name"] + ", " + user_info["first_name"]
                    logger.debug("User LastName, Firstname: {}".format(user_lastname_firstname))
            else:
                logger.info("In update_ext_pack_status: All Rx are  on hold for packs :{}".format(all_pack_display_ids))
                user_id = 1
                force_delete = True

            remaining_pack_display_ids = deepcopy(all_pack_display_ids)
            logger.debug(
                "change_rx_logger_debug_string: update_ext_pack_status: checking for pending/progress templates for "
                "remaining_pack_display_ids - {}".format(remaining_pack_display_ids))
            template_dict = db_get_templates_by_pharmacy_fill_ids(pharmacy_fill_ids=remaining_pack_display_ids,
                                                                  status_list=settings.PENDING_PROGRESS_TEMPLATE_LIST,
                                                                  company_id=company_id)
            if template_dict:
                for display_id, template_data in template_dict.items():
                    ext_dict = {"pack_id": None,
                                "template_id": template_data["id"],
                                "status_id": template_data["status"],
                                "ext_pack_display_id": display_id,
                                "ext_status_id": constants.EXT_PACK_STATUS_CODE_DELETED,
                                "ext_comment": reason,
                                "ext_company_id": company_id,
                                "ext_user_id": user_id,
                                "ext_created_date": get_current_date_time()}
                    template_ext_pack_list.append(ext_dict)
                    template_ids.append(template_data["id"])

                logger.debug(
                    "change_rx_logger_debug_string: update_ext_pack_status: template_dict data added in template_ext_pack_list")

                logger.debug("change_rx_logger_debug_string: update_ext_pack_status: rolling back template_ids {} ".format(template_ids))
                update_template_dict = {"company_id": company_id, "reason": reason,
                                        "user_id": user_id, "template_ids": template_ids}
                response = json.loads(rollback_templates(update_template_dict))
                logger.debug("update_ext_pack_status: response of rollback_templates: " + str(response))

                if response["status"] == settings.SUCCESS_RESPONSE:

                    # save data in ext_pack_details
                    logger.debug("update_ext_pack_status: saving data in ext_pack_details")
                    ext_data_update_flag = save_ext_pack_data(data_list=template_ext_pack_list)
                    logger.debug("update_ext_pack_status: data saved in ext_pack_details with status - {}"
                                 .format(ext_data_update_flag))

                    # send notification for rolled back template in portal wide notification (company level)
                    # message = 'Templates ID(s) {} has been deleted in Pharmacy Software'\
                    #                                         .format(','.join(str(temp) for temp in template_ids))
                    more_info = {"template_ids": template_ids, "ips_username": ips_username}
                    exception_list = []
                    # send_notification_in_thread(user_id, message, 'general', more_info, False)
                    # t = ExcThread(exception_list, name="send_notification_for_change_rx",
                    #               target=send_notification_in_thread,
                    #               args=[user_id, message, 'general', more_info, False])
                    # t.start()
                    # Notifications(user_id=user_id, call_from_client=True).send_with_username(user_id=0, message=message,
                    #                                                                          flow='general',
                    #                                                                          more_info=more_info,
                    #                                                                          add_current_user=False)

                    logger.debug("update_ext_pack_status: updating couch-db for rolled back templates from ips")
                    real_time_db_timestamp_trigger(settings.CONST_TEMPLATE_MASTER_DOC_ID, company_id=company_id)
                    logger.debug("update_ext_pack_status: couch-db updated for rolled back templates from ips")

                else:
                    # todo- handle the scenario if error code is 5005, this can happen only
                    #  if template is rolled back or processed after this api call triggered.
                    logger.error("update_ext_pack_status: Templates {} are not in pending or progress state"
                                 .format(str(template_dict["template_ids"])))
                    pack_display_ids_with_error.extend(template_dict.keys())

                # remaining_pack_display_ids = list(set(remaining_pack_display_ids)
                #                                   .difference(set(template_dict.keys())))
                logger.debug("update_ext_pack_status: template_dict found so modified remaining_pack_display_ids: {}"
                             .format(remaining_pack_display_ids))

            # fetching pack data if not pending/progress template found for some display_ids
            if remaining_pack_display_ids:
                logger.debug("update_ext_pack_status: fetching pack_dict for remaining_pack_display_ids - {}"
                             .format(remaining_pack_display_ids))
                pack_dict = db_get_pack_data_by_pack_display_id(pack_display_ids=remaining_pack_display_ids,
                                                                company_id=company_id)
                if pack_dict:
                    """Below code is to handle case where some packs are on BD and some are manual and changeRx is called. Here we will delete all the packs even on BD"""
                    manual_delete_all_check = {}
                    technician_fill_status_dict = {}


                    for display_id, pack_data in pack_dict.items():
                        pack_user_map_data_exists = db_check_pack_user_map_data_dao(pack_id=pack_data["id"])
                        technician_fill = db_get_ext_status_by_pack_status(pack_data)
                        if technician_fill != constants.EXT_PACK_STATUS_CODE_DELETED:
                            technician_fill = check_other_packs_of_that_patients(pack_header_id = pack_data["pack_header_id"],
                                                                                 technician_fill=technician_fill)

                        technician_fill_status_dict[display_id] = technician_fill

                        if technician_fill == constants.EXT_PACK_STATUS_CODE_DELETED and (
                                pack_data["pack_status"] in [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                                             settings.PARTIALLY_FILLED_BY_ROBOT] and pack_user_map_data_exists):
                            manual_delete_all_check[display_id] = "M"
                        if technician_fill == constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD and pack_data[
                            'batch_id'] == None and not pack_user_map_data_exists:
                            logger.info("Deleting all packs: manual_delete_all_check {}".format(manual_delete_all_check))
                            manual_delete_all_check[display_id] = "B"
                    if manual_delete_all_check.values() and "M" in manual_delete_all_check.values() and "B" in manual_delete_all_check.values():
                        update_couch_db = True
                        cdb_batch_distribution = constants.REFRESH_BATCH_DISTRIBUTION
                        force_delete = True
                    logger.info(" In update_ext_pack_status: technician_fill_status_dict {}".format(technician_fill_status_dict))
                    for display_id, pack_data in pack_dict.items():
                        distinct_ext_pack_status.append(pack_data["pack_status"])

                        if not change_rx:
                            ext_hold_flag_exists = db_check_ext_pack_status_on_hold_dao([display_id])
                            # if ext_hold_flag:
                            #     technician_fill_status = db_get_ext_status_by_pack_status(pack_data)
                            # else:
                            #     technician_fill_status = constants.EXT_PACK_STATUS_CODE_DELETED

                        technician_fill_status = technician_fill_status_dict[display_id]
                        if force_delete:
                            technician_fill_status = constants.EXT_PACK_STATUS_CODE_DELETED

                        ext_dict = {}
                        if not ext_hold_flag_exists and pack_data["pack_status"] != settings.DELETED_PACK_STATUS:
                            ext_dict = {"pack_id": pack_data["id"],
                                        "template_id": None,
                                        "status_id": pack_data["pack_status"],
                                        "ext_pack_display_id": display_id,
                                        "ext_status_id": technician_fill_status,
                                        "ext_comment": reason if technician_fill_status == constants.
                                            EXT_PACK_STATUS_CODE_DELETED else constants.HOLD_REASON_EXT_CHANGE_RX,
                                        "ext_company_id": company_id,
                                        "ext_user_id": user_id,
                                        "packs_delivered": str(delivered_packs) if delivered_packs else None,
                                        "pharmacy_pack_status_id": pharmacy_pack_status_id if pharmacy_pack_status_id else None,
                                        "ext_created_date": get_current_date_time(),
                                        "packs_delivery_status": constants.PACK_DELIVERY_STATUS_INSIDE_PHARMACY_ID}

                            if change_rx:
                                ext_dict.update({"ext_change_rx_id": ext_change_rx_id})

                        # if pack_data["batch_id"] and pack_data["pack_status"] != settings.DELETED_PACK_STATUS:
                        #     batch_dict[pack_data["batch_id"]].append(pack_data["id"])

                        if technician_fill_status == constants.EXT_PACK_STATUS_CODE_DELETED:
                            pack_ids.append(pack_data["id"])
                            if not ext_hold_flag_exists and ext_dict:
                                ext_pack_list.append(ext_dict)
                            else:
                                if pack_data["pack_status"] != settings.DELETED_PACK_STATUS:
                                    hold_to_delete_pack_ids.append(pack_data["id"])
                        else:
                            if not ext_hold_flag_exists:
                                logger.debug("Insert new Hold data for Pack Display ID: {}".format(display_id))
                                hold_pack_ids.append(pack_data["id"])
                                ext_hold_pack_list.append(ext_dict)
                            else:
                                logger.debug("Pack Display ID: {} is already on Hold for ext_pack_status".
                                             format(display_id))

                    # if change_rx:
                    logger.debug("Pack List: {} and Distinct Pack Status Display ID: {}, Batch: {}"
                                 .format(pack_ids, distinct_ext_pack_status, batch_dict))
                    distinct_ext_pack_status = list(set(distinct_ext_pack_status))
                    if distinct_ext_pack_status:
                        if len(distinct_ext_pack_status) == 1 and distinct_ext_pack_status[0] == \
                                settings.PENDING_PACK_STATUS:
                            logger.debug("For all packs in pending stage, we shall retain ext pack status as Hold..")
                            # # TODO: pack split cannot be checked because new template is not yet received
                            # for batch_id, batch_pack_ids in batch_dict.items():
                            #     batch_status = get_batch_status(batch_id)
                            #     logger.debug("Batch ID: {}, Status: {}".format(batch_id, batch_status))
                            #
                            #     if batch_status in [settings.BATCH_DELETED, settings.BATCH_PENDING]:
                            #         pack_ids, hold_pack_ids, ext_hold_pack_list, ext_pack_list = \
                            #             update_ext_packs_delete_status(pack_ids, hold_pack_ids, batch_pack_ids,
                            #                                            ext_hold_pack_list, ext_pack_list)
                            #
                            #     else:
                            #         logger.debug("Recommendation has been executed. Verify if MFD recommendation "
                            #                      "exists..")
                            #         mfd_check = db_check_mfd_analysis_by_batch_dao(batch_id)
                            #         if not mfd_check:
                            #             pack_ids, hold_pack_ids, ext_hold_pack_list, ext_pack_list = \
                            #                 update_ext_packs_delete_status(pack_ids, hold_pack_ids, batch_pack_ids,
                            #                                                ext_hold_pack_list, ext_pack_list)

                    if not ext_hold_flag_exists and not change_rx:
                        pack_ids, hold_pack_ids, ext_hold_pack_list, ext_pack_list = \
                            update_ext_packs_delete_status(pack_ids, hold_pack_ids, hold_pack_ids, ext_hold_pack_list,
                                                           ext_pack_list)

                    if hold_pack_ids and ext_hold_pack_list:
                        logger.debug("Hold update_ext_pack_status: saving data in ext_pack_details for Hold")
                        for ext_pack in ext_hold_pack_list:
                            if ext_pack["pack_id"] in hold_pack_ids:
                                hold_pack_display_ids.append(ext_pack["ext_pack_display_id"])

                        ext_data_update_flag = save_ext_pack_data(data_list=ext_hold_pack_list)

                    if pack_ids:
                        logger.debug("update_ext_pack_status: pack_dict data added in ext_pack_list")

                        # Send the details for Delete Reason which can be further utilized to communicate with IPS
                        args = {"company_id": company_id, "user_id": user_id, "status": settings.DELETED_PACK_STATUS,
                                "pack_id": pack_ids, "status_changed_from_ips": True, "reason": reason,
                                "change_rx": change_rx}

                        logger.debug("161: update_ext_pack_status: found pack_dict so calling set_status api with args - {}"
                                     .format(args))
                        rts_flag = bool(int(get_company_setting_by_company_id(company_id).get("USE_RTS_FLOW", 0)))

                        if rts_flag:
                            reuse_pack_drug_insert_response, ext_update_dict = insert_record_in_reuse_pack_drug(pack_ids, company_id)
                            logger.info(
                                "In update_ext_pack_status: response of insert_record_in_reuse_pack_drug: {}, ext_update_dict: {}"
                                .format(reuse_pack_drug_insert_response, ext_update_dict))
                        response = json.loads(set_status(args))
                        logger.debug("161: update_ext_pack_status: response of set_status: {}".format(response))

                        if response["status"] == settings.SUCCESS_RESPONSE:

                            # save data in ext_pack_details
                            if ext_pack_list:
                                logger.debug("update_ext_pack_status: saving data in ext_pack_details")
                                ext_data_update_flag = save_ext_pack_data(data_list=ext_pack_list)
                                logger.debug("update_ext_pack_status: data saved in ext_pack_details with status - {}"
                                             .format(ext_data_update_flag))

                                if ext_update_dict:
                                    ext_update_status = db_update_ext_packs_delivery_status_dao(ext_update_dict)
                                    logger.debug(
                                        "update_ext_pack_status: ext_update_status - {}".format(ext_update_status))

                            if hold_to_delete_pack_ids:
                                logger.debug("update_ext_pack_status: update data in ext_pack_details from Hold to "
                                             "Delete for Pack IDs: {}".format(hold_to_delete_pack_ids))
                                ext_data_update_flag = update_ext_pack_data(hold_to_delete_pack_ids=
                                                                            hold_to_delete_pack_ids,
                                                                            force_delete=force_delete)
                                logger.debug("update_ext_pack_status: update status: {}".format(ext_data_update_flag))

                            ext_pack_display_ids: List[int] = response.get("delete_pack_display_ids", None)
                        else:
                            logger.error("update_ext_pack_status: Error in updating pack status - {}"
                                         .format(response["description"]))
                            pack_display_ids_with_error.extend(pack_dict.keys())

                    if ext_pack_display_ids is None:
                        ext_pack_display_ids = []
                    pack_display_ids = ext_pack_display_ids + hold_pack_display_ids

                    # send notification for deleted packs if exists
                    if pack_display_ids:
                        pfw_deleted_pack_ids, dp_deleted_pack_ids, all_flows_deleted_packs_ids = \
                            get_packs_based_on_flow(
                                pack_display_ids=pack_display_ids,
                                company_id=company_id)

                        change_rx_hold_pack_ids = []
                        if pfw_deleted_pack_ids:
                            if not change_rx:
                                change_rx_hold_pack_ids = db_get_pack_display_ids_on_hold_dao(pack_display_ids=
                                                                                              pfw_deleted_pack_ids)
                                if change_rx_hold_pack_ids:
                                    pfw_deleted_pack_ids = change_rx_hold_pack_ids
                                # else:
                                #     message = 'Pack ID(s) {} has been deleted in Pharmacy Software' \
                                #         .format(','.join(str(pack) for pack in
                                #                          pfw_deleted_pack_ids))

                            more_info = {"pack_ids": pfw_deleted_pack_ids, "ips_username": ips_username}

                            if change_rx or change_rx_hold_pack_ids:
                                template_data = db_get_template_info_by_pack_display_id(pfw_deleted_pack_ids,
                                                                                        company_id)
                                message = constants.NOTIFICATION_EXT_CHANGE_RX_GENERAL
                                more_info.update({"change_rx": True, "old_template_id": template_data["template_id"],
                                                  "mvs_only": True, "user_full_name": user_lastname_firstname})
                                flow_document = "dp"
                                send_notification_in_thread(user_id, message, flow_document, more_info, False)
                                # asrs_data = db_get_storage_by_pack_display_id(dp_deleted_pack_ids, company_id)
                                # if asrs_data:
                                #     more_info.update({"asrs": asrs_data})
                            # else:
                            #     flow_document = "pfw"
                                logger.info(
                                    "change_rx_logger_debug_string: updating couchdb in : update_ext_pack_status: more_info = {}: flow = {}".format(
                                        more_info, flow_document))
                            else:
                                template_data = db_get_template_info_by_pack_display_id(pfw_deleted_pack_ids,
                                                                                        company_id)
                                message = 'Templates ID(s) {} has been deleted in Pharmacy Software'.format(template_data['template_id'])
                                more_info.update({"change_rx": False, "old_template_id": template_data["template_id"],
                                                  "mvs_only": True, "user_full_name": user_lastname_firstname})
                                flow_document = "dp"
                                send_notification_in_thread(user_id, message, flow_document, more_info, False)
                                logger.info(
                                    "change_rx_logger_debug_string: updating couchdb in : update_ext_pack_status: more_info = {}: flow = {}".format(
                                        more_info, flow_document))

                            exception_list = []
                            # send_notification_in_thread(user_id, message, flow_document, more_info, False)
                            # t = ExcThread(exception_list, name="send_notification_for_change_rx",
                            #               target=send_notification_in_thread,
                            #               args=[user_id, message, flow_document, more_info, False])
                            # t.start()

                            # Notifications(user_id=user_id, call_from_client=True).send_with_username(user_id=0,
                            #                                                                          message=message,
                            #                                                                          flow=flow_document,
                            #                                                                          more_info=more_info,
                            #                                                                          add_current_user=False)

                        change_rx_hold_pack_ids = []
                        if dp_deleted_pack_ids:
                            if not change_rx:
                                change_rx_hold_pack_ids = db_get_pack_display_ids_on_hold_dao(pack_display_ids=
                                                                                              dp_deleted_pack_ids)
                                if change_rx_hold_pack_ids:
                                    dp_deleted_pack_ids = change_rx_hold_pack_ids
                                # else:
                                #     message = 'Pack ID(s) {} has been deleted in Pharmacy Software' \
                                #         .format(','.join(str(pack) for pack in dp_deleted_pack_ids))

                            more_info = {"pack_ids": dp_deleted_pack_ids, "ips_username": ips_username}

                            if change_rx or change_rx_hold_pack_ids:
                                template_data = db_get_template_info_by_pack_display_id(dp_deleted_pack_ids,
                                                                                        company_id)
                                message = constants.NOTIFICATION_EXT_CHANGE_RX_GENERAL
                                more_info.update({"change_rx": True, "old_template_id": template_data["template_id"],
                                                  "mvs_only": True, "user_full_name": user_lastname_firstname})
                                send_notification_in_thread(user_id, message, 'dp', more_info, False)
                                # asrs_data = db_get_storage_by_pack_display_id(dp_deleted_pack_ids, company_id)
                                # if asrs_data:
                                #     more_info.update({"asrs": asrs_data})

                            exception_list = []
                            # send_notification_in_thread(user_id, message, 'dp', more_info, False)
                            # t = ExcThread(exception_list, name="send_notification_for_change_rx",
                            #               target=send_notification_in_thread,
                            #               args=[user_id, message, 'dp', more_info, False])
                            # t.start()

                        #     Notifications(user_id=user_id, call_from_client=True).send_with_username(user_id=0,
                        #                                                                              message=message,
                        #                                                                              flow='dp',
                        #                                                                              more_info=more_info,
                        #                                                                              add_current_user=False)
                        # change_rx_hold_pack_ids = []
                        if all_flows_deleted_packs_ids:
                            if not change_rx:
                                change_rx_hold_pack_ids = \
                                    db_get_pack_display_ids_on_hold_dao(pack_display_ids=all_flows_deleted_packs_ids)
                                if change_rx_hold_pack_ids:
                                    all_flows_deleted_packs_ids = change_rx_hold_pack_ids
                                # else:
                                #     message = 'Pack ID(s) {} has been deleted in Pharmacy Software' \
                                #         .format(','.join(str(pack) for pack in
                                #                          all_flows_deleted_packs_ids))

                            more_info = {"pack_ids": all_flows_deleted_packs_ids, "ips_username": ips_username}

                            if change_rx or change_rx_hold_pack_ids:
                                template_data = db_get_template_info_by_pack_display_id(all_flows_deleted_packs_ids,
                                                                                        company_id)
                                message = constants.NOTIFICATION_EXT_CHANGE_RX_GENERAL
                                more_info.update({"change_rx": True, "old_template_id": template_data["template_id"],
                                                  "mvs_only": True, "user_full_name": user_lastname_firstname})
                                flow_document = "dp"
                                send_notification_in_thread(user_id, message, flow_document, more_info, False)
                                # asrs_data = db_get_storage_by_pack_display_id(dp_deleted_pack_ids, company_id)
                                # if asrs_data:
                                #     more_info.update({"asrs": asrs_data})
                            # else:
                            #     flow_document = "general"

                            exception_list = []
                            # send_notification_in_thread(user_id, message, flow_document, more_info, False)
                            # t = ExcThread(exception_list, name="send_notification_for_change_rx",
                            #               target=send_notification_in_thread,
                            #               args=[user_id, message, flow_document, more_info, False])
                            # t.start()

                            # Notifications(user_id=user_id, call_from_client=True).send_with_username(user_id=0,
                            #                                                                          message=message,
                            #                                                                          flow=flow_document,
                            #                                                                          more_info=more_info,
                            #                                                                          add_current_user=False)

                    remaining_pack_display_ids = list(
                        set(remaining_pack_display_ids).difference(set(pack_dict.keys())))
                    logger.debug(
                        "update_ext_pack_status: pack_dict found so modified remaining_pack_display_ids: {}"
                            .format(remaining_pack_display_ids))

                    # Updating couchdb in some cases:
                    if update_couch_db:
                        update_couch_db_batch_distribution_status(company_id=company_id,
                                                                  refresh_screen=constants.REFRESH_BATCH_DISTRIBUTION)
                        if not cdb_batch_distribution:
                            system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                                           device_type_id=settings.DEVICE_TYPES[
                                                                               "ROBOT"])
                            args = {"system_id": system_id, "change_rx": True}
                            update_timestamp_couch_db_pre_processing_wizard(args)
                else:
                    logger.debug("update_ext_pack_status: No packs found that are not deleted from "
                                 "remaining_pack_display_ids: {}".format(remaining_pack_display_ids))
                    remaining_pack_display_ids = []

            pack_display_ids_with_error.extend(remaining_pack_display_ids)

            if pack_display_ids_with_error:
                return error(5007, ": " + str(pack_display_ids_with_error))

        elif technician_fill_status == constants.EXT_PACK_STATUS_CODE_DONE:
            if not reason:
                reason = 'Filled from Pharmacy Software'

            if not all_pack_display_ids:
                logger.error("empty pack_display_ids")
                return error(5008)

            # fetch userid based on ips_username
            user_info = get_userid_by_ext_username(ips_username, company_id)
            if user_info and "id" in user_info:
                user_id = user_info["id"]
            else:
                logger.error("Error while fetching user_info for technician_user_name {}".format(ips_username))
                return error(5006)
            logger.info("userinfo: {} for ips_username: {}".format(user_info, ips_username))

            if all_pack_display_ids:
                logger.debug("update_ext_pack_status: fetching pack_dict for remaining_pack_display_ids - {}"
                             .format(all_pack_display_ids))
                pack_dict = db_get_pack_data_by_pack_display_id(pack_display_ids=all_pack_display_ids,
                                                                company_id=company_id)

                if pack_dict:
                    for display_id, pack_data in pack_dict.items():
                        if pack_data["pack_status"] not in [settings.PARTIALLY_FILLED_BY_ROBOT, settings.FILLED_PARTIALLY_STATUS]:
                            not_partially_filled_status_packs[display_id] = pack_data["pack_status"]
                        else:
                            partially_filled_packs[display_id] = pack_data

                if not_partially_filled_status_packs:
                    return error(5020, ": " + str(not_partially_filled_status_packs.keys()))
                if pack_dict:
                    for display_id, pack_data in partially_filled_packs.items():
                        ext_dict = {"pack_id": pack_data["id"],
                                    "template_id": None,
                                    "status_id": pack_data["pack_status"],
                                    "ext_pack_display_id": display_id,
                                    "ext_status_id": technician_fill_status,
                                    "ext_comment": reason,
                                    "ext_company_id": company_id,
                                    "ext_user_id": user_id,
                                    "ext_created_date": get_current_date_time(),
                                    "packs_delivery_status": constants.PACK_DELIVERY_STATUS_INSIDE_PHARMACY_ID}
                        ext_pack_list.append(ext_dict)
                        pack_ids.append(pack_data["id"])
                    logger.debug("update_ext_pack_status: pack_dict data added in ext_pack_list")

                    # Send the details for Delete Reason which can be further utilized to communicate with IPS
                    args = {"company_id": company_id, "user_id": user_id, "status": settings.DONE_PACK_STATUS,
                            "pack_id": pack_ids, "status_changed_from_ips": True, "reason": reason,
                            "filled_at": settings.FILLED_AT_PHARMACY_SOFTWARE}
                    logger.debug("233: update_ext_pack_status: found pack_dict so calling set_status api with args - {}"
                                 .format(args))
                    rts_flag = bool(int(get_company_setting_by_company_id(company_id).get("USE_RTS_FLOW", 0)))

                    if rts_flag:
                        reuse_pack_drug_insert_response, ext_update_dict = insert_record_in_reuse_pack_drug(pack_ids, company_id)
                        logger.info(
                            "In update_ext_pack_status: response of insert_record_in_reuse_pack_drug: {}, ext_update_dict: {}"
                            .format(reuse_pack_drug_insert_response, ext_update_dict))
                    response = json.loads(set_status(args))
                    logger.debug("233: update_ext_pack_status: response of set_status: {}".format(response))

                    if response["status"] == settings.SUCCESS_RESPONSE:
                        # save data in ext_pack_details
                        logger.debug("update_ext_pack_status: saving data in ext_pack_details")
                        ext_data_update_flag = save_ext_pack_data(data_list=ext_pack_list)
                        logger.debug("update_ext_pack_status: data saved in ext_pack_details with status - {}"
                                     .format(ext_data_update_flag))

                        if ext_update_dict:
                            ext_update_status = db_update_ext_packs_delivery_status_dao(ext_update_dict)
                            logger.debug(
                                "update_ext_pack_status: ext_update_status - {}".format(ext_update_status))

                        pack_display_ids: List[int] = response.get("delete_pack_display_ids", None)

                    else:
                        logger.error("update_ext_pack_status: Error in updating pack status - {}"
                                     .format(response["description"]))
                        pack_display_ids_with_error.extend(partially_filled_packs.keys())

            #
            #
            if pack_display_ids_with_error:
                return error(5020, ": " + str(pack_display_ids_with_error))

        elif technician_fill_status == constants.IPS_PACK_ERROR_CODE:
            logger.info("Marking pack_display_id {} as Error in Filling from IPS")
            if not technician_fill_error_comment:
                technician_fill_error_comment = 'Marked as ,Error in Filling from IPS'

            if not all_pack_display_ids:
                logger.error("empty pack_display_ids")
                return error(5008)

            # fetch userid based on ips_username
            user_info = get_userid_by_ext_username(ips_username, company_id)
            if user_info and "id" in user_info:
                user_id = user_info["id"]
            else:
                logger.error("Error while fetching user_info for technician_user_name {}".format(ips_username))
                return error(5006)
            logger.info("userinfo: {} for ips_username: {}".format(user_info, ips_username))

            if all_pack_display_ids:
                logger.debug("update_ext_pack_status: fetching pack_dict for remaining_pack_display_ids - {}"
                             .format(all_pack_display_ids))
                pack_dict = db_get_pack_data_by_pack_display_id(pack_display_ids=all_pack_display_ids,
                                                                company_id=company_id)
                error_list = []
                if pack_dict:
                    for display_id, pack_data in pack_dict.items():
                        error_data = {
                                'pack_id': pack_data['id'],
                                'comments': technician_fill_error_comment,
                                'created_by': user_id,
                                'created_date': get_current_date_time()
                        }
                        error_list.append(error_data)
            # Adding error in database
                if error_list:
                    status = save_pack_error_from_ips(error_list)

                    if not status:
                        return error(5006)

        elif technician_fill_status == constants.EXT_PACK_STATUS_CODE_DELETED_RETURN_IN_PHARMACY_ID:
            if not return_from_the_delivery_packs:
                return error(1001, "Missing Parameter(s): return_from_the_delivery_packs.")

            # fetch userid based on ips_username
            user_info = get_userid_by_ext_username(ips_username, company_id)
            logger.info(
                "In update_ext_pack_status: User Id fetched ={}".format(user_info)) if user_info else logger.info(
                "In update_ext_pack_status: No user found for ips_user_name")

            if user_info and "id" in user_info:
                user_id = user_info["id"]
                user_lastname_firstname = user_info["last_name"] + ", " + user_info["first_name"]
            else:
                logger.error("Error while fetching user_info for technician_user_name {}".format(ips_username))
                return error(5006)
            logger.info("userinfo: {} for ips_username: {}".format(user_info, ips_username))
            logger.debug("User LastName, Firstname: {}".format(user_lastname_firstname))

            pack_display_ids = []
            for pack_display_id in return_from_the_delivery_packs:
                pack_display_ids.append(pack_display_id)

            pack_data_dict = db_get_pack_data_by_pack_display_id(pack_display_ids=pack_display_ids,
                                                                 company_id=company_id)

            pack_ids = list()
            if pack_data_dict:
                for pack_display_id, pack_data in pack_data_dict.items():
                    ext_dict = {"pack_id": pack_data["id"],
                                "template_id": None,
                                "status_id": pack_data["pack_status"],
                                "ext_pack_display_id": pack_display_id,
                                "ext_status_id": technician_fill_status,
                                "ext_comment": reason,
                                "ext_company_id": company_id,
                                "ext_user_id": user_id,
                                "packs_delivered": None,
                                "pharmacy_pack_status_id": pharmacy_pack_status_id if pharmacy_pack_status_id else None,
                                "ext_created_date": get_current_date_time(),
                                "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_PENDING_ID,
                                "packs_delivery_status": constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID
                                }

                    pack_ids.append(pack_data["id"])
                    ext_pack_list.append(ext_dict)

                ext_insert_status = db_insert_many_records_in_ext_pack_details_dao(ext_pack_list)
                logger.info("In update_ext_pack_status: ext_insert_status: {}".format(ext_insert_status))

                status, ext_update_dict = insert_record_in_reuse_pack_drug(pack_ids=pack_ids, company_id=company_id,
                                                                           return_from_the_delivery_packs_status=True,
                                                                           return_from_the_delivery_packs=return_from_the_delivery_packs)

                if ext_update_dict:
                    ext_update_status = db_update_ext_packs_delivery_status_dao(ext_update_dict)
                    logger.debug(
                        "update_ext_pack_status: ext_update_status - {}".format(ext_update_status))

                logger.info("In update_ext_pack_status: insert_record_in_reuse_pack_drug_status: {}, ext_update_dict: {}"
                            .format(status, ext_update_dict))

        else:
            return error(1035, 'technician_fill_status.')

        return ips_response(200, 'ok')
    except (IntegrityError, DoesNotExist, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error - " + str(e))


@log_args_and_response
def send_notification_in_thread(user_id, message, flow_document, more_info, add_current_user):
    try:
        for i in range(3):
            try:
                Notifications(user_id=user_id, call_from_client=True).send_with_username(user_id=0,
                                                                                         message=message,
                                                                                         flow=flow_document,
                                                                                         more_info=more_info,
                                                                                         add_current_user=add_current_user)
            except (IntegrityError, DoesNotExist, InternalError, DataError, RealTimeDBException) as e:
                logger.warning("In send_notification_in_thread: Cannot update couchDB")
                continue
            except Exception as e:
                logger.warning("In send_notification_in_thread: Cannot update couchDB")
                continue

            break

    except (IntegrityError, DoesNotExist, InternalError, DataError, Exception) as e:
        logger.error("Exception in send_notification_in_thread".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Exception in send_notification_in_thread".format(e), exc_info=True)
        raise e


@log_args_and_response
def ext_update_pharmacy_pack_status(pack_ids, pharmacy_pack_status):

    try:
        with db.transaction():
            for packs in pack_ids:

                pass
                # 1. Check if pack exist in ext pack details
                ext_pack_data = get_ext_pack_data_by_pack_display_id(packs)
                update_dict = {
                    "pharmacy_pack_status_id": pharmacy_pack_status
                }
                status = db_update_ext_pharmacy_pack_status(update_dict, ext_pack_data.id)

    except (IntegrityError, DoesNotExist, InternalError, DataError, Exception) as e:
        logger.error("Exception in ext_update_pharmacy_pack_status".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Exception in ext_update_pharmacy_pack_status".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_reusable_packs(dict_pack_info):

    logger.info("In get_reusable_packs {}".format(dict_pack_info))

    try:
        company_id = dict_pack_info["company_id"]
        paginate = dict_pack_info.get('paginate', None)
        sort_fields = dict_pack_info.get('sort_fields', None)
        filter_fields = dict_pack_info.get('filter_fields', None)

        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        pack_data = get_reusable_pack_dao(paginate=paginate,
                                          company_id=company_id,
                                          sort_fields=sort_fields,
                                          filter_fields=filter_fields,
                                          )

        return pack_data
    except Exception as e:
        logger.error(f"Error in get_pack_user_map: {e}")
        raise e
