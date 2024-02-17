import os
import sys
from typing import List, Any, Dict, Optional

from peewee import IntegrityError, DataError, InternalError, JOIN_LEFT_OUTER, DoesNotExist, fn

import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response

from model.model_device_manager import DeviceMaster
from src import constants
from src.constants import EXT_PACK_USAGE_STATUS_PENDING_ID, EXT_PACK_STATUS_CODE_DELETED
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_user_map import PackUserMap
from src.model.model_container_master import ContainerMaster
from src.model.model_ext_pack_details import ExtPackDetails

from src.model.model_patient_master import PatientMaster
from src.model.model_slot_details import SlotDetails
from src.model.model_template_master import TemplateMaster
from src.model.model_temp_slot_info import TempSlotInfo
from src.service.misc import update_notifications_couch_db_status

logger = settings.logger


@log_args_and_response
def save_ext_pack_data(data_list: list) -> bool:
    """
    Method to save ext pack data in table ext_pack_details
    @param data_list:
    @return:
    """
    try:
        logger.debug("Assign Pack Usage status based on the pack status and Hold/Delete option.")
        logger.debug("For Ext Status as Deleted: If Pack status is In Progress or Done --> Pack Usage is Pending, "
                     "If Pack Status is Pending --> Pack Usage is default value i.e. Not Required.")
        for ext_pack in data_list:
            if ext_pack["ext_status_id"] == EXT_PACK_STATUS_CODE_DELETED and \
                    ext_pack["status_id"] in settings.PACK_PROGRESS_DONE_STATUS_LIST:
                ext_pack["pack_usage_status_id"] = EXT_PACK_USAGE_STATUS_PENDING_ID
        ExtPackDetails.insert_many(data_list).execute()
        return True
    except (IntegrityError, DataError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_ext_pack_data(hold_to_delete_pack_ids: List[int],
                         pack_display_id_status_dict: Optional[Dict[int, Dict[str, Any]]] = None,
                         force_delete: Optional[bool] = False):
    try:
        return ExtPackDetails.db_update_ext_status(hold_to_delete_pack_ids, pack_display_id_status_dict, force_delete)
    except (IntegrityError, DataError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_ext_pack_usage_status(pack_ids: List[int], new_pack_ids: List[int]):
    update_status: bool = False
    same_template_packs_list: List[int] = []
    packs_not_done: int = 0
    pack_usage_done: bool = False
    old_template_list: List[int] = []
    try:
        update_status = ExtPackDetails.db_update_ext_pack_usage_status(pack_ids)

        logger.debug("Check whether all packs are marked done and Pack Usage Status also Pending, then we need to "
                     "remove the Notification from notifications_dp_all document.")
        PackHeaderAlias = PackHeader.alias()
        PackDetailsAlias = PackDetails.alias()
        PackDetailsAlias_ext = PackDetails.alias()

        company_id = PackDetails.get_company_id_for_pack(pack_ids)
        if company_id:

            pack_query = PackDetails.select(fn.GROUP_CONCAT(fn.DISTINCT(PackDetailsAlias.id)).coerce(False)
                                            .alias("same_template_packs")).dicts()\
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
                .join(PackHeaderAlias, on=((PackHeader.patient_id == PackHeaderAlias.patient_id) &
                                           (PackHeader.file_id == PackHeaderAlias.file_id)))\
                .join(PackDetailsAlias, on=PackHeaderAlias.id == PackDetailsAlias.pack_header_id)\
                .where(PackDetails.id << new_pack_ids)\
                .group_by(PackHeaderAlias.patient_id, PackHeaderAlias.file_id)
            logger.debug("Pack Query: {}".format(pack_query))

            for pack in pack_query:
                same_template_packs_list = []
                packs_not_done = 0
                pack_usage_done = False
                old_template_list = []

                if pack["same_template_packs"] is not None:
                    same_template_packs_list = list(map(lambda x: int(x), pack["same_template_packs"].split(',')))
                    logger.debug("Same Template Packs: {}".format(same_template_packs_list))

                    packs_not_done = PackDetails.select().dicts()\
                        .where(PackDetails.id << same_template_packs_list,
                               PackDetails.pack_status.not_in(settings.FILLED_PACK_STATUS)).count()

                    logger.debug("Packs Not Done: {}".format(packs_not_done))
                    if packs_not_done:
                        logger.debug("Still have packs that are not done. We cannot remove the CouchDB notifications "
                                     "from notifications_dp_all document.")
                    else:
                        ext_query = ExtPackDetails.select(ExtPackDetails.pack_id, ExtPackDetails.ext_pack_display_id,
                                                          ExtPackDetails.pack_usage_status_id,
                                                          ExtChangeRx.current_template).dicts()\
                            .join(ExtChangeRx, on=ExtPackDetails.ext_change_rx_id == ExtChangeRx.id)\
                            .join(PackDetailsAlias_ext, on=ExtPackDetails.pack_id == PackDetailsAlias_ext.id)\
                            .join(TemplateMaster, on=ExtChangeRx.new_template == TemplateMaster.id)\
                            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                                  (TemplateMaster.file_id == PackHeader.file_id)))\
                            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
                            .where(PackDetails.id << same_template_packs_list,
                                   TemplateMaster.fill_start_date <= PackDetailsAlias_ext.consumption_start_date,
                                   TemplateMaster.fill_end_date >= PackDetailsAlias_ext.consumption_end_date)
                        logger.debug("Packs Done, Get ExtPack Query: {}".format(ext_query))

                        pack_usage_done = \
                            all([ext_pack["pack_usage_status_id"] in [constants.EXT_PACK_USAGE_STATUS_NA_ID,
                                                                      constants.EXT_PACK_USAGE_STATUS_DONE_ID]
                                 for ext_pack in ext_query])

                        logger.debug("Pack Usage Status: {}".format(pack_usage_done))
                        if pack_usage_done:
                            old_template_list = list(set([ext_pack["current_template"] for ext_pack in ext_query]))
                            logger.debug("Old Template List: {}".format(old_template_list))

                            for old_template_id in old_template_list:
                                update_notifications_couch_db_status(old_pharmacy_fill_id=[],
                                                                     company_id=company_id, file_id=0,
                                                                     old_template_id=old_template_id,
                                                                     new_template_id=0, autoprocess_template_flag=False,
                                                                     new_pack_ids=[], remove_action=True)
        return update_status

    except (IntegrityError, DataError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_pack_user_map_data_dao(pack_id: int):
    try:
        return PackUserMap.db_check_pack_user_map_data(pack_id=pack_id)
    except (IntegrityError, DataError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_templates_by_pharmacy_fill_ids(pharmacy_fill_ids: list, company_id: int, status_list: list = None) -> dict:
    """
    Returns templates data based on given pharmacy_fill_ids and status list
    @param company_id:
    @param status_list:
    @param pharmacy_fill_ids:
    :return: list of templates
    """
    try:
        template_dict = dict()
        query = TemplateMaster.select(TemplateMaster, TemplateMaster.pharmacy_fill_id).dicts() \
            .where(TemplateMaster.pharmacy_fill_id << pharmacy_fill_ids,
                   TemplateMaster.company_id == company_id) \
            .group_by(TemplateMaster.id)

        if status_list:
            query = query.where(TemplateMaster.status << status_list)

        for record in query:
            template_dict[record["pharmacy_fill_id"]] = record

        return template_dict

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_data_by_pack_display_id(pack_display_ids: list, company_id: int):
    """
    Method to get pack data by pack display ids
    --> Get only those packs that are not deleted
    @param pack_display_ids:
    @param company_id:
    @return:
    """
    try:
        pack_dict = dict()

        query = PackDetails.select(PackDetails).dicts() \
            .where(PackDetails.pack_display_id << pack_display_ids,
                   PackDetails.company_id == company_id,
                   PackDetails.pack_status != settings.DELETED_PACK_STATUS)

        for record in query:
            pack_dict[record['pack_display_id']] = record

        return pack_dict
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_storage_by_pack_display_id(pack_display_ids: List[int], company_id: int) -> Dict[str, Any]:
    asrs_dict: Dict[str, Any] = dict()
    pack_id_list: List[int] = []

    try:
        query = PackDetails.select(DeviceMaster.name.alias("device_name"),
                                   fn.GROUP_CONCAT(PackDetails.pack_display_id).coerce(False).alias("pack_ids")
                                   ).dicts() \
            .join(ContainerMaster, on=PackDetails.container_id == ContainerMaster.id) \
            .join(DeviceMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
            .where(PackDetails.pack_display_id << pack_display_ids,
                   PackDetails.company_id == company_id,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES["ASRS"]) \
            .group_by(DeviceMaster.id)

        for asrs in query:
            if asrs["pack_ids"] is not None:
                pack_id_list = list(map(lambda x: int(x), asrs["pack_ids"].split(',')))
                asrs_dict.update({asrs["device_name"]: pack_id_list})
        return asrs_dict

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_info_by_pack_display_id(pack_display_ids: List[int], company_id: int) -> Dict[str, Any]:
    template_dict: Dict[str, Any] = dict()

    try:
        query = PackDetails.select(TemplateMaster.id.alias("template_id")).dicts() \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(TemplateMaster, on=((PackHeader.patient_id == TemplateMaster.patient_id) &
                                      (PackHeader.file_id == TemplateMaster.file_id))) \
            .where(PackDetails.pack_display_id << pack_display_ids,
                   PackDetails.company_id == company_id) \
            .group_by(TemplateMaster.id)

        for template in query:
            template_dict = {"template_id": template["template_id"]}

        return template_dict
    except (IntegrityError, DoesNotExist, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_packs_based_on_flow(pack_display_ids: list, company_id: int) -> tuple:
    """
    Method to differentiate packs based on flow
    @param pack_display_ids:
    @param company_id:
    @return:
    """
    try:
        manual_pack_display_ids = list()
        packs_with_batch = list()
        packs_without_batch = list()

        query = PackDetails.select(PackDetails.pack_display_id, PackDetails.batch_id,
                                   PackUserMap.id.alias('pack_user_map_id')).dicts() \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .where(PackDetails.pack_display_id << pack_display_ids,
                   PackDetails.company_id == company_id)

        for record in query:
            if record["pack_user_map_id"] is not None:
                manual_pack_display_ids.append(record["pack_display_id"])
            elif record["batch_id"] is not None:
                packs_with_batch.append(record["pack_display_id"])
            else:
                packs_without_batch.append(record["pack_display_id"])

        return manual_pack_display_ids, packs_with_batch, packs_without_batch

    except InternalError as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def check_other_packs_of_that_patients(pack_header_id, technician_fill):
    try:

        """
        case when this function will helpful
        8 packs of patient 1 >> 5 packs manual (due to updatemfdanalysis API>> similar packs) + 3 packs (at pack queue)
        now if change rx happen >> new packs will go for the manual , 5 packs (old) gets deleted but remaining 3 old packs not get deleted 
        because of pending status but it should also get deleted.
        """


        logger.info("In check_other_packs_of_that_patients")
        logger.info(f"In check_other_packs_of_that_patients, pack_header_id:{pack_header_id}, technician_fill:{technician_fill}")

        query = PackDetails.select(PackUserMap.pack_id).dicts() \
                .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
                .where(PackDetails.pack_header_id == pack_header_id)

        for data in query:
            # loop will execute only one time
            #if data exist means status of other packs of that patient are manual.

            #check mfd filling >> if mfd drug status pending >> delete that packs.
            mfd_filling_query = PackDetails.select(fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.status_id))
                                          .coerce(False).alias('mfd_status')).dicts() \
                                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                                .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
                                .where(PackDetails.pack_header_id == pack_header_id)

            for status in mfd_filling_query:
                # loop will execute only one time
                mfd_status = list(map(int, (status["mfd_status"]).split(",")))

                logger.info(f"In check_other_packs_of_that_patients, mfd_status: {mfd_status}")

                if set(mfd_status).difference({constants.MFD_DRUG_PENDING_STATUS, constants.MFD_DRUG_SKIPPED_STATUS}):
                    # some mfds are filled >> don't delete that pack
                    return technician_fill

                #if all mfd of that patients are pending >> skip that canister and drug.

                update_mfd_status_query = MfdAnalysisDetails.select(MfdAnalysis.id).dicts() \
                                            .join(MfdAnalysis, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                                            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                                            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                                            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                                            .where(PackDetails.pack_header_id == pack_header_id,
                                                   MfdAnalysisDetails.status_id == constants.MFD_DRUG_PENDING_STATUS) \
                                            .group_by(MfdAnalysis.id)

                mfd_analysis_ids = []
                for data in update_mfd_status_query:
                    mfd_analysis_ids.append(data["id"])

                logger.info(f"In check_other_packs_of_that_patients, mfd_analysis_ids: {mfd_analysis_ids}")
                if mfd_analysis_ids:
                    with db.transaction():
                        logger.info(f"In check_other_packs_of_that_patients, updating MfdAnalysisDetails")
                        status = MfdAnalysisDetails.update(status_id=constants.MFD_DRUG_SKIPPED_STATUS)\
                                            .where(MfdAnalysisDetails.analysis_id << mfd_analysis_ids) \
                                            .execute()
                        logger.info(f"In check_other_packs_of_that_patients, updated MfdAnalysisDetails: {status}")

                        status = MfdAnalysis.update(status_id=constants.MFD_CANISTER_SKIPPED_STATUS)\
                                            .where(MfdAnalysis.id << mfd_analysis_ids)\
                                            .execute()
                        logger.info(f"In check_other_packs_of_that_patients, updated MfdAnalysis: {status}")

            return constants.EXT_PACK_STATUS_CODE_DELETED

        logger.info(f"In check_other_packs_of_that_patients, technician_fill: {technician_fill}")

        return technician_fill

    except Exception as e:
        logger.error("Error in check_other_packs_of_that_patients {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_other_packs_of_that_patients: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return technician_fill


@log_args_and_response
def get_ext_pack_data_by_pack_display_id(pack_id):
    try:
        query = ExtPackDetails.select().where(ExtPackDetails.ext_pack_display_id == pack_id).get()
        return query

    except Exception as e:
        logger.error("Error in get_ext_pack_data_by_pack_display_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_ext_pack_data_by_pack_display_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def db_update_ext_pharmacy_pack_status(update_dict, ext_id):
    try:
        query = ExtPackDetails.update(**update_dict).where(ExtPackDetails.id == ext_id).execute()
        return query

    except Exception as e:
        logger.error("Error in db_update_ext_pharmacy_pack_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in db_update_ext_pharmacy_pack_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def db_update_ext_pack_details_by_pack_id_dao(pack_ids, update_dict):
    try:
        query = ExtPackDetails.db_update_ext_pack_details_by_pack_id(pack_ids, update_dict)
        return query

    except Exception as e:
        logger.error("Error in db_update_ext_pack_status_by_pack_id_dao: {}".format(e))
        raise e


@log_args_and_response
def db_insert_many_records_in_ext_pack_details_dao(data_list):
    try:
        status = ExtPackDetails.db_insert_many_records_in_ext_pack_details(data_list=data_list)
        return status

    except Exception as e:
        logger.error("Error in db_insert_many_records_in_ext_pack_details_dao: {}".format(e))
        raise e


@log_args_and_response
def db_get_ext_pack_data_by_pack_ids_dao(pack_ids):
    try:
        status = ExtPackDetails.db_get_ext_pack_data_by_pack_ids(pack_ids=pack_ids)
        return status

    except Exception as e:
        logger.error("Error in db_get_ext_pack_data_by_pack_ids_dao: {}".format(e))
        raise e


@log_args_and_response
def db_update_ext_packs_delivery_status_dao(ext_update_dict):
    try:
        status = None
        for ext_pack_id, update_data in ext_update_dict.items():
            update_dict = {"packs_delivery_status": update_data}
            status = ExtPackDetails.db_update_ext_pack_details_by_pack_id([ext_pack_id], update_dict)

        return status

    except Exception as e:
        logger.error("Error in db_update_ext_packs_delivery_status_dao: {}".format(e))
        raise e
