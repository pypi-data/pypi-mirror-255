import json
import logging
import sys
import os
from datetime import timedelta, datetime

from typing import List, Dict, Any, Tuple

from peewee import IntegrityError, DataError, InternalError, DoesNotExist

import settings
from dosepack.error_handling.error_handler import error, ips_response, create_response, remove_sql_injectors
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src import constants
from src.constants import IPS_STATUS_CODE_OK
from src.dao.device_manager_dao import get_system_id_based_on_device_type
from src.dao.ext_change_rx_dao import db_get_templates_by_template_info, db_get_patient_details_dao, \
    db_check_and_map_mfd_drug_for_new_pack, insert_new_rx_based_on_old_one, get_temp_slot_info_data, \
    update_temp_slot_info, get_slot_details_ids, changes_in_pack_rx_link_and_slot_details
from src.dao.ext_file_dao import update_couch_db_pending_template_count, insert_ext_hold_rx_data_dao
from src.dao.pack_ext_dao import db_get_templates_by_pharmacy_fill_ids
from src.dao.parser_dao import db_doctor_master_update_or_create
from src.dao.template_dao import get_template_id_from_display_id
from src.exceptions import FileParsingException, RedisConnectionException, TokenMissingException, \
    InvalidUserTokenException
from src.service.misc import get_token, get_current_user
from src.service.ext_file import format_prescription_dict, validate_prescription
from src.service.parser import Parser, db_check_split_old_and_new_template

logger = logging.getLogger("root")


def get_company_user_id_from_token() -> Tuple[int, int, str]:
    """
    Returns a Company ID based on the token received during API call from IPS

    Returns: tuple(bool, int) --> boolean value returns False for any error with Error ID.
            Else it returns True with Company ID
    """
    try:
        # fetch company_id based on token
        token = get_token()
        if not token:
            logger.debug("process_rx: token not found")
            raise TokenMissingException

        logger.debug("process_rx- Fetched token: " + str(token) + ", Now fetching user_details")
        current_user = get_current_user(token)
        logger.debug("process_rx: user_info- {} for token - {}".format(current_user, token))
        if not current_user:
            logger.debug("process_rx: no user found for token - {}".format(token))
            raise InvalidUserTokenException

        return current_user["company_id"], current_user["id"], current_user["ips_user_name"]
    except TokenMissingException as e:
        logger.error(e, exc_info=True)
        raise TokenMissingException
    except InvalidUserTokenException as e:
        logger.error(e, exc_info=True)
        raise InvalidUserTokenException
    except Exception as e:
        logger.error(e, exc_info=True)
        raise Exception


@log_args_and_response
@validate(required_fields=["error_code", "error_desc", "data"])
def ext_process_change_rx(data_ips_dict: Dict[str, Any]) -> str:

    logger.debug("In Process ChangeRx...")

    # FUTURE: Need to handle this for re-triggering of API call
    error_code = data_ips_dict.get("error_code")
    error_desc = data_ips_dict.get("error_desc")

    logger.debug("Get the Actual data that needs to be processed for ChangeRx")
    data_dict = data_ips_dict.get("data")

    company_id: int
    pharmacy_display_ids: List[int] = data_dict["pack_display_id"]

    token_user_id: int
    token_user_name: str
    user_id: int
    file_id: int
    system_id: int
    change_rx_constant: str = "Change Rx"
    change_rx: bool = True
    pharmacy_patient_id: int
    template_master_data: List[Dict[str, Any]] = list()
    patient_id: int = 0
    autoprocess_template: int = 0

    try:
        # -------------- Fetch Company ID based on Token --------------
        company_id, token_user_id, token_user_name = get_company_user_id_from_token()
        data_dict["company_id"] = company_id

        logger.debug("Get the Template details to fetch their status...")
        template_dict = db_get_templates_by_pharmacy_fill_ids(pharmacy_fill_ids=pharmacy_display_ids,
                                                              company_id=company_id)

        if error_code:
            if error_code in [constants.ERROR_CODE_CONNECTION_ISSUE_AFTER_FILE_SAVED]:
                logger.debug("{}: API retriggered, with error code: {}, error_desc: {} and Pharmacy Display IDs: {}."
                             .format(change_rx_constant, error_code, error_desc, pharmacy_display_ids))
            elif error_code == constants.ERROR_CODE_DEFAULT:
                logger.debug("Inside the method to process Change Rx...")
            else:
                logger.debug("API triggered with invalid error codes...")
                return error(21002, "Error Code: {}".format(error_code))

        if not template_dict:
            logger.debug("No Templates are present to proceed further with Change Rx...")
            return error(constants.ERROR_CODE_NO_TEMPLATES_FOUND)

        logger.debug("Template Master Info: {}...".format(template_dict))
        template_master_data = db_get_templates_by_template_info(template_dict)

        logger.debug("Change Rx -- Fetch the Patient from Template")
        for template in template_master_data:
            patient_id = template["patient_id"]
            file_id = template["file_id"]

        logger.debug("Change Rx -- Set the Patient Details that will help in storing data for File Validation "
                     "errors...")
        patient_details = db_get_patient_details_dao(patient_id)

        if not patient_details:
            raise Exception

        logger.debug("Change Rx -- Setup the dictionary with Patient Name, Patient No and Pharmacy Fill ID.")
        data_dict["patient_name"] = patient_details["patient_name"]
        data_dict["patient_no"] = patient_details["patient_no"]
        data_dict["pharmacy_fill_id"] = pharmacy_display_ids[0]
        ext_change_rx_dict: Dict[str, Any] = data_dict.copy()

        # ----------------- validate file with required keys and values -----------------
        validation_error_message = validate_prescription(data_dict, change_rx=change_rx)

        if validation_error_message:
            logger.error("{}: error found while validating prescription data format - {}"
                         .format(change_rx_constant, validation_error_message))
            return error(5012, validation_error_message)
        logger.debug("{}: prescription validated.".format(change_rx_constant))

        # ----------------- get the robot system_id from the given company_id as of now. -----------------
        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])

        # process_pharmacy_file.file_id = file_id
        daycare_program = data_dict.pop("daycare_program", 0)
        if not daycare_program:
            autoprocess_template = 1
        logger.debug("Auto-Process Template: {}".format(autoprocess_template))

        # autoprocess_template = data_dict.pop("autoprocess_template", 0)
        # logger.debug("Auto-Process Template: {}".format(autoprocess_template))

        # ----------------- format the data dict to create same data frame as per old format -----------------
        logger.debug("{}: formatting prescription data".format(change_rx_constant))
        processed_data, stop_data, hold_rx_dict = format_prescription_dict(data=data_dict, change_rx=change_rx, template_master_data=template_master_data)
        logger.debug("{}: prescription data formatted".format(change_rx_constant))

        # ----------------- process the file -----------------
        logger.debug("{}: Initiating Parser".format(change_rx_constant))
        process_pharmacy_file = Parser(user_id=token_user_id, filename="NA", company_id=company_id,
                                       system_id=system_id, from_dict=True, data=processed_data,
                                       upload_file_to_gcs=False)
        logger.debug("{}: parser initiated".format(change_rx_constant))

        if autoprocess_template:
            process_pharmacy_file.autoprocess_template = autoprocess_template
        process_pharmacy_file.ips_user_name = token_user_name

        logger.debug("{}: Parser initiated, now calling start_processing".format(change_rx_constant))
        response = process_pharmacy_file.start_processing(update_prescription_v1=True, change_rx=change_rx,stop_data= stop_data,
                                                          template_master_data=template_master_data,
                                                          data_dict=ext_change_rx_dict)
        logger.debug("{}: start_processing done with response - {}".format(change_rx_constant, response))

        if hold_rx_dict:
            status = insert_ext_hold_rx_data_dao(hold_rx_dict, file_id)

        parsed_response = json.loads(response)
        if parsed_response["status"] == settings.FAILURE_RESPONSE:
            return error(5016, parsed_response["description"])

        if not autoprocess_template:
            update_couch_db_pending_template_count(company_id=company_id)

        return ips_response(IPS_STATUS_CODE_OK)

    except (IntegrityError, DoesNotExist, InternalError, DataError, FileParsingException) as e:
        logger.error(e, exc_info=True)
        return error(5015, e)
    except TokenMissingException as e:
        logger.error(e, exc_info=True)
        return error(5018, e)
    except InvalidUserTokenException as e:
        logger.error(e, exc_info=True)
        return error(5019, e)
    except RedisConnectionException as e:
        logger.info(e)
        pass
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(constants.ERROR_CODE_INTERNAL_CHANGE_RX, str(e))


@log_args_and_response
def get_ext_split(args):
    try:
        old_template = args["old_template"]
        new_template = args["new_template"]
        check_split = db_check_split_old_and_new_template(old_template, new_template)
        if check_split:
            return create_response(True)
        else:
            return create_response(False)
    except (IntegrityError, DoesNotExist, InternalError, DataError, FileParsingException) as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(5015, e)
    except Exception as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_INTERNAL_CHANGE_RX, str(e))


@log_args_and_response
def get_ext_mfd(args):
    try:
        old_template = args["old_template"]
        new_template = args["new_template"]
        mfd_mapping = db_check_and_map_mfd_drug_for_new_pack(old_template, new_template)

        return create_response(mfd_mapping)

    except (IntegrityError, DoesNotExist, InternalError, DataError, FileParsingException) as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(5015, e)
    except Exception as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_INTERNAL_CHANGE_RX, str(e))


@log_args_and_response
def add_rx(args):
    try:
        logger.info("In add_nfo_rx")
        # template_id = args['template_id']
        pack_display_ids = args['pack_display_ids']
        nfo_details = args['nfo_details']
        fill_start_date = datetime.strptime(args["fill_start_date"], "%Y%m%d").date()
        fill_end_date = datetime.strptime(args["fill_end_date"], "%Y%m%d").date()
        new_rx_details = []
        old_new_rx_dict = dict()
        new_old_rx_dict = dict()
        doctor_details_dict = dict()
        final_slot_details = dict()
        update_temp_slot_info_dict = dict()
        remaining_refill_dict = dict()


        logger.debug("add_rx: fetching token")
        token = get_token()
        if not token:
            logger.debug("add_rx: token not found")
            return error(5018)
        logger.debug("add_rx- Fetched token: " + str(token) + ", Now fetching user_details")
        current_user = get_current_user(token)
        logger.debug("add_rx: user_info- {} for token - {}".format(current_user, token))
        if not current_user:
            logger.debug("add_rx: no user found for token - {}".format(token))
            return error(5019)
        company_id = current_user["company_id"]
        user_id = current_user["id"]

        #validation on template id
        template_id = get_template_id_from_display_id(pack_display_id=pack_display_ids)
        if not template_id:
            logger.info(f"In add_rx, Invaid template id")
            return error(5021)

        for nfo in nfo_details:

            new_rx_details = nfo['new_rx_details']

            old_new_rx_dict[str(nfo["old_rx_details"]["pharmacy_rx_no"])] = str(new_rx_details["pharmacy_rx_no"])
            new_old_rx_dict[str(new_rx_details["pharmacy_rx_no"])] = str(nfo["old_rx_details"]["pharmacy_rx_no"])
            remaining_refill_dict[str(new_rx_details["pharmacy_rx_no"])] = new_rx_details["remaining_refill"]

            if not doctor_details_dict.get(new_rx_details['pharmacy_doctor_id']):

                dict_doctor_master_data = {}
                dict_doctor_master_data["pharmacy_doctor_id"] = new_rx_details['pharmacy_doctor_id']
                dict_doctor_master_data["doctor_name"] = new_rx_details['doctor_name']
                dict_doctor_master_data["doctor_phone"] = new_rx_details['doctor_phone']
                dict_doctor_master_data["workphone"] = new_rx_details['doctor_phone']
                name = new_rx_details['doctor_name'].split(",", 1)
                dict_doctor_master_data["last_name"] = name[0]
                dict_doctor_master_data["first_name"] = name[1] if len(name) > 1 else ""
                dict_doctor_master_data = {k: (v.strip() if type(v) is str else v) for k, v in
                                           dict_doctor_master_data.items()}


                doctor_details_dict[new_rx_details['pharmacy_doctor_id']] = dict_doctor_master_data

        logger.info(f'In add_rx, doctor_details_dict: {doctor_details_dict}')
        # -----------update doctor_master if needed---------------------
        for pharmacy_doctor_id, dict_doctor_master_data in doctor_details_dict.items():
            doctor_data = db_doctor_master_update_or_create(dict_doctor_master_data=dict_doctor_master_data,
                                                            pharmacy_doctor_id=pharmacy_doctor_id,
                                                            company_id=company_id,
                                                            default_data_dict={'created_by': user_id,
                                                                               'modified_by': user_id},
                                                            remove_fields=['doctor_phone', 'doctor_name'])
            logger.info(f"In add_rx, pharmacy_doctor_id: {pharmacy_doctor_id}, doctor_data: {doctor_data.id}")

        # ------------insert new rx in patient_rx if needed---------------------
        new_patient_rx_ids, old_patient_rx_ids = insert_new_rx_based_on_old_one(old_new_rx_dict, template_id, user_id, remaining_refill_dict)
        # new_patient_rx_ids : {new_rx: patient_rx_id}
        # old_patient_rx_ids : {old_rx: patient_rx_id}

        # ---------------get temp_slot_info data----------------------
        temp_slot_info_data = get_temp_slot_info_data(template_id, old_new_rx_dict)

        # ------------------get pack_rx_link and slot_details data: if exists---------------------------------
        slot_details_hoa_rx_wise, slot_pack_dict, current_pack_rx_link = get_slot_details_ids(old_new_rx_dict, pack_display_ids)
        # pack_rx_data = get_pack_rx_data(template_id, old_new_rx_dict)

        for nfo in nfo_details:
            old_rx = str(nfo["old_rx_details"]['pharmacy_rx_no'])
            new_rx = str(nfo["new_rx_details"]['pharmacy_rx_no'])
            new_patient_rx_id = new_patient_rx_ids[new_rx]
            new_fill_details = nfo['new_rx_details']['fill_details']

            logger.info(f"In In add_rx, old_rx: {old_rx}, new_rx: {new_rx}, new_patient_rx_id: {new_patient_rx_id}")

            for fill in new_fill_details:
                quantity_list = fill["quantity"]
                hoa_time = fill['hoa_time']
                hoa_time = datetime.strptime(hoa_time, "%H%M").time()
                hoa_date = fill_start_date
                slot_id_dict = dict()
                if slot_details_hoa_rx_wise:
                    slot_id_dict = slot_details_hoa_rx_wise[hoa_time][old_rx]
                for qty in quantity_list:
                    # check for hoa_date: it must be between fill_start_date and fill_end_date including both
                    if hoa_date > fill_end_date:
                        logger.debug(
                            "add_rx: hoa_date > fill_end_date for pack_display_ids- {}".format(pack_display_ids))
                        break
                    if float(qty):
                        if not update_temp_slot_info_dict.get(new_patient_rx_id):
                            update_temp_slot_info_dict[new_patient_rx_id] = []
                        temp_slot_info_id = temp_slot_info_data[old_rx][hoa_time][hoa_date]
                        update_temp_slot_info_dict[new_patient_rx_id].append(temp_slot_info_id)
                        if slot_id_dict:
                            # slot_id_list = slot_details_hoa_rx_wise[hoa_time][old_rx]
                            if not final_slot_details.get(hoa_time):
                                final_slot_details[hoa_time] = dict()
                            if not final_slot_details[hoa_time].get(new_rx):
                                final_slot_details[hoa_time][new_rx] = list()
                            final_slot_details[hoa_time][new_rx].extend(slot_id_dict.get(hoa_date, []))
                    else:
                        if slot_id_dict:
                            if not final_slot_details.get(hoa_time):
                                final_slot_details[hoa_time] = dict()
                            if not final_slot_details[hoa_time].get(old_rx):
                                final_slot_details[hoa_time][old_rx] = list()
                            # slot_id_list = slot_details_hoa_rx_wise[hoa_time][old_rx]
                            final_slot_details[hoa_time][old_rx].extend(slot_id_dict.get(hoa_date, []))

                    hoa_date = hoa_date + timedelta(days=1)

        # ---------------------update temp_slot_info---------------------------
        if update_temp_slot_info:
            status = update_temp_slot_info(update_temp_slot_info_dict)
            logger.info(f'In ad, update temp_slot_info status: {status}')

        # -------------------update/insert pack_rx_link and slot_details--------------------------------
        logger.info(f'In add_rx, final_slot_details: {final_slot_details}')
        if final_slot_details:
            status = changes_in_pack_rx_link_and_slot_details(final_slot_details, template_id, old_new_rx_dict, new_patient_rx_ids, old_patient_rx_ids, slot_pack_dict, new_old_rx_dict, current_pack_rx_link)
            logger.info(f'In add_rx, update pack_rx_link_and_slot_details status: {status}')

        return create_response(True)
    except Exception as e:
        logger.error("error in merge_batch_dao {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in merge_batch_dao: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
