import logging
from typing import List

from peewee import InternalError, IntegrityError, DataError, DoesNotExist

import settings
from com.pharmacy_software import send_data
from dosepack.utilities.utils import log_args_and_response
from src.model.model_company_setting import CompanySetting
from src.model.model_pack_details import PackDetails
from src.exceptions import PharmacySoftwareResponseException, PharmacySoftwareCommunicationException


logger = logging.getLogger("root")


@log_args_and_response
def db_verify_packlist_by_company(pack_id: int, company_id: int) -> bool:
    try:
        return PackDetails.db_verify_packlist([pack_id], company_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_verify_packlist_by_company {}".format(e))
        raise


@log_args_and_response
def db_verify_packlist_by_system(pack_ids: List[int], system_id: int) -> bool:
    try:
        return PackDetails.db_verify_packlist_by_system_id(pack_ids, system_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_verify_packlist_by_system {}".format(e))
        raise


@log_args_and_response
def db_get_pack_display_by_pack_id(pack_id: int) -> List[str]:
    try:
        return PackDetails.db_get_pack_display_ids([pack_id])
    except (InternalError, IntegrityError, DoesNotExist, DataError, Exception) as e:
        logger.error("error in db_get_pack_display_by_pack_id {}".format(e))
        raise


@log_args_and_response
def db_get_pack_display_by_pack_ids(pack_ids: List[int]) -> List[int]:
    try:
        return PackDetails.db_get_pack_display_ids(pack_ids)
    except (InternalError, IntegrityError, DoesNotExist, DataError, Exception) as e:
        logger.error("error in db_get_pack_display_by_pack_id {}".format(e))
        raise


@log_args_and_response
def rph_init_call_ips(pack_id: int, company_id: int, ips_username: str):
    # pack_display_ids: List[str] = []
    try:
        pack_display_ids = db_get_pack_display_by_pack_id(pack_id)
        ips_comm_settings = CompanySetting.db_get_ips_communication_settings(company_id)
        logger.info("Initiate RPh call...")

        alerts_data = send_data(
            ips_comm_settings['BASE_URL_IPS'],
            settings.RPH_INIT,
            {
                "batchid": pack_display_ids[0],
                "username": ips_username,
                "token": ips_comm_settings["IPS_COMM_TOKEN"]
            },
            0,
            token=ips_comm_settings["IPS_COMM_TOKEN"]
        )

        logger.info("Response from IPS: {}".format(alerts_data))

    except PharmacySoftwareCommunicationException as e:
        logger.error("error in rph_init_call_ips {}".format(e))
        raise
    except PharmacySoftwareResponseException as e:
        logger.error("error in rph_init_call_ips {}".format(e))
        raise
    except Exception as e:
        logger.error("error in rph_init_call_ips {}".format(e))
        raise


@log_args_and_response
def rph_get_alert_from_ips(pack_id: int, company_id: int, ips_username: str) -> bool:
    # pack_display_ids: List[str] = []
    # bill_dict: Dict[str, Any] = dict()
    # auth_dict: Dict[str, Any] = dict()
    # dur_dict: Dict[str, Any] = dict()
    # notes_dict: Dict[int, Any] = dict()
    try:
        pack_display_ids = db_get_pack_display_by_pack_id(pack_id)
        ips_comm_settings = CompanySetting.db_get_ips_communication_settings(company_id)
        logger.info("Get Alerts Update for RPh from IPS...")

        alerts_data = send_data(
            ips_comm_settings['BASE_URL_IPS'],
            settings.RPH_ALERT_CHECK,
            {
                "batchid": pack_display_ids[0],
                "username": ips_username,
                "token": ips_comm_settings["IPS_COMM_TOKEN"]
            },
            0,
            token=ips_comm_settings["IPS_COMM_TOKEN"]
        )
        logger.info("Response from IPS: {}".format(alerts_data))
        data = alerts_data["response"]["data"]
        logger.info("Data obtained from IPS: {}".format(data))

        if data:
            bill_dict = data.get("bill_check", {})
            auth_dict = data.get("auth_check", {})
            dur_dict = data.get("dur_check", {})
            notes_dict = data.get("notes", {})
            logger.info("Bill: {}\nAuth: {}\nDUR: {}\nNotes: {}".format(bill_dict, auth_dict, dur_dict, notes_dict))
        return True

    except PharmacySoftwareCommunicationException as e:
        logger.error("error in rph_get_alert_from_ips {}".format(e))
        raise
    except PharmacySoftwareResponseException as e:
        logger.error("error in rph_get_alert_from_ips {}".format(e))
        return False
    except Exception as e:
        logger.error("error in rph_get_alert_from_ips {}".format(e))
        raise


@log_args_and_response
def mark_rph_status_in_ips(pack_id: int, company_id: int, rph_action: int, ips_username: str, reason: str = ""):
    # pack_display_ids: List[str] = []
    try:
        pack_display_ids = db_get_pack_display_by_pack_id(pack_id)

        ips_comm_settings = CompanySetting.db_get_ips_communication_settings(company_id)
        logger.info("Update RPh Status in IPS...")

        alerts_data = send_data(
            ips_comm_settings['BASE_URL_IPS'],
            settings.RPH_UPDATE_IPS,
            {
                "batchid": pack_display_ids[0],
                "status": str(rph_action),
                "note": reason,
                "username": ips_username,
                "token": ips_comm_settings["IPS_COMM_TOKEN"]
            },
            0,
            token=ips_comm_settings["IPS_COMM_TOKEN"]
        )
        logger.info("Response from IPS: {}".format(alerts_data))

    except PharmacySoftwareCommunicationException as e:
        logger.error("error in mark_rph_status_in_ips {}".format(e))
        raise
    except PharmacySoftwareResponseException as e:
        logger.error("error in mark_rph_status_in_ips {}".format(e))
        raise
    except Exception as e:
        logger.error("error in mark_rph_status_in_ips {}".format(e))
        raise


@log_args_and_response
def get_notes_from_ips_dao(pack_id: int, company_id: int, note_type: int):
    # pack_display_ids: List[str] = []
    # notes_dict: Dict[str, Any] = dict()
    try:
        pack_display_ids = db_get_pack_display_by_pack_id(pack_id)
        ips_comm_settings = CompanySetting.db_get_ips_communication_settings(company_id)
        logger.info("Update RPh Status in IPS...")

        alerts_data = send_data(
            ips_comm_settings['BASE_URL_IPS'],
            settings.NOTES_IPS,
            {
                "batchid": pack_display_ids[0],
                "status": str(note_type),
                "token": ips_comm_settings["IPS_COMM_TOKEN"]
            },
            0,
            token=ips_comm_settings["IPS_COMM_TOKEN"]
        )
        logger.info("Response from IPS: {}".format(alerts_data))
        data = alerts_data["response"]["data"]
        logger.info("Data obtained from IPS: {}".format(data))

        if data:
            notes_dict = data.get("notes", {})
            logger.info("Notes: {}".format(notes_dict))

    except PharmacySoftwareCommunicationException as e:
        logger.error("error in get_notes_from_ips_dao {}".format(e))
        raise
    except PharmacySoftwareResponseException as e:
        logger.error("error in get_notes_from_ips_dao {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_notes_from_ips_dao {}".format(e))
        raise
