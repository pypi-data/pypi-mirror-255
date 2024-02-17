import functools
import logging
import operator
from collections import defaultdict
import datetime
from typing import List, Optional, Any, Dict

from peewee import fn, InternalError, IntegrityError, JOIN_LEFT_OUTER, SQL, DataError, DoesNotExist

import settings
from dosepack.utilities.utils import get_current_date, log_args_and_response
from src import constants
from src.dao.template_dao import decode_celery_result, db_get_template_change_rx_info

from src.model.model_celery_task_meta import CeleryTaskmeta
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_ext_change_rx_details import ExtChangeRxDetails
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_facility_master import FacilityMaster
from src.model.model_file_header import FileHeader
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_patient_master import PatientMaster
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_template_details import TemplateDetails
from src.model.model_template_master import TemplateMaster

logger = logging.getLogger("root")


@log_args_and_response
def db_get_templates(status, company_id):
    """ Gets all the template meta data based on the given status

        Args:
            status (int): The status on which the template is to be fetched
            company_id (int): company id for which templates need to be fetched

        Returns:
            List : List of all the template meta data for the given status.

        Examples:
            >>> TemplateMaster.get_all_templates(1, 2)
            >>> []

    """
    try:
        TemplateMasterAlias = TemplateMaster.alias()
        pending_template_status = settings.PENDING_PROGRESS_TEMPLATE_LIST
        linked_packs_list: List[int] = []
        change_rx_comment_list: List[str] = []

        # slot_data = TemplateMaster.select(TemplateMaster.id.alias('template_id'),
        #                                   fn.GROUP_CONCAT(
        #                                       Clause(SQL('DISTINCT'), TempSlotInfo.hoa_date, SQL('ORDER BY'),
        #                                              TempSlotInfo.hoa_date)).alias('admin_date_list')) \
        #     .join(TempSlotInfo, on=((TempSlotInfo.file_id == TemplateMaster.file_id) &
        #                             (TempSlotInfo.patient_id == TemplateMaster.patient_id))) \
        #     .group_by(TempSlotInfo.file_id, TempSlotInfo.patient_id) \
        #     .where(TemplateMaster.company_id == company_id,
        #            TemplateMaster.status << (
        #                settings.PENDING_TEMPLATE_STATUS, settings.PROGRESS_TEMPLATE_STATUS)).alias('slot_data')

        current_date = get_current_date()
        previous_date = datetime.datetime.strptime(current_date, '%Y-%m-%d') - datetime.timedelta(days=60)
        # if optimization is needed in sub_q 3 filter based on admin dates by adding
        # packdetails.consumption_start_date > previous date

        template_data = TemplateMaster.select(TemplateMaster.patient_id,
                                              TemplateMaster.file_id).dicts() \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << pending_template_status)

        file_patient_list = list()
        patient_ids = list()

        # fetching patient_file info to filter temp_slot_info and patinet_ids to filter packs info
        for record in template_data:
            file_patient_list.append('{}#{}'.format(record['patient_id'], record['file_id']))
            patient_ids.append(record['patient_id'])

        if not patient_ids:
            return {}
        packs_query = PackHeader.select(PackHeader.patient_id.alias('patient_id'),
                                        PackDetails.pack_display_id.alias('pack_display_id'),
                                        PackDetails.consumption_start_date.alias('consumption_start_date'),
                                        PackDetails.consumption_end_date.alias('consumption_end_date'),
                                        PackHeader.file_id.alias('file_id')) \
            .join(PackDetails,
                  on=((PackDetails.pack_header_id == PackHeader.id) &
                      (PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS])))) \
            .where(PackDetails.company_id == company_id,
                   PackDetails.consumption_start_date > previous_date,
                   PackHeader.patient_id << patient_ids).alias('packs_query')

        sub_q_2 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(TemplateMasterAlias.id)).coerce(False)
                                        .alias('duplicate_template_ids')) \
            .join(TemplateMasterAlias, on=((TemplateMaster.patient_id == TemplateMasterAlias.patient_id) &
                                           (TemplateMasterAlias.id != TemplateMaster.id))) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMasterAlias.status << settings.PENDING_PROGRESS_TEMPLATE_LIST,
                   TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST) \
            .group_by(TemplateMaster.id).alias('sub_q_2')

        temp_slot_data = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                             TempSlotInfo.hoa_date.alias('hoa_date'),
                                             TempSlotInfo.file_id.alias('file_id')) \
            .where(fn.CONCAT(TempSlotInfo.patient_id, '#', TempSlotInfo.file_id) << file_patient_list).alias(
            'temp_slot_data')

        # query to get packs having overlapping or similar admin period for each template
        sub_q_3 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(packs_query.c.pack_display_id)).coerce(False)
                                        .alias('duplicate_pack_ids'),
                                        ) \
            .join(temp_slot_data, on=((temp_slot_data.c.file_id == TemplateMaster.file_id) &
                                      (temp_slot_data.c.patient_id == TemplateMaster.patient_id))) \
            .join(packs_query,
                  on=(
                          (TemplateMaster.patient_id == packs_query.c.patient_id) &
                          (temp_slot_data.c.hoa_date.between(packs_query.c.consumption_start_date,
                                                             packs_query.c.consumption_end_date)
                           ))) \
            .group_by(temp_slot_data.c.file_id, temp_slot_data.c.patient_id) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST).alias('sub_q_3')

        # sub_q_ext_change_rx, sub_q_ext_change_rx_pack, sub_q_ext_change_rx_details = \
        #     db_get_linked_change_rx_details(company_id=company_id, template_status=settings.
        #                                     PENDING_PROGRESS_TEMPLATE_LIST)

        sub_ext_change_rx, sub_q_4 = db_get_template_change_rx_info(company_id=company_id, file_id=0, patient_id=0)

        query = TemplateMaster.select(TemplateMaster.status,
                                      TemplateMaster.file_id,
                                      TemplateMaster.patient_id,
                                      TemplateMaster.is_modified.alias('is_template_modified'),
                                      TemplateMaster.created_date,
                                      TemplateMaster.id.alias('template_id'),
                                      TemplateMaster.delivery_datetime,
                                      TemplateMaster.system_id,
                                      PatientMaster.last_name, PatientMaster.first_name,
                                      fn.IF(sub_q_2.c.duplicate_template_ids, 1, 0)
                                      .alias('duplicate_template_present'),
                                      fn.IF(sub_q_3.c.duplicate_pack_ids, 1, 0)
                                      .alias('duplicate_packs_present'),
                                      sub_q_2.c.duplicate_template_ids,
                                      sub_q_3.c.duplicate_pack_ids,
                                      PatientMaster.pharmacy_patient_id, PatientMaster.patient_no,
                                      FacilityMaster.facility_name,
                                      sub_q_4.c.linked_packs.alias("linked_packs"),
                                      sub_ext_change_rx.c.change_rx_comment.alias("change_rx_comment")) \
            .join(PatientMaster, on=PatientMaster.id == TemplateMaster.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(FileHeader, on=TemplateMaster.file_id == FileHeader.id) \
            .join(sub_q_3, JOIN_LEFT_OUTER, on=sub_q_3.c.temp_id == TemplateMaster.id) \
            .join(sub_q_2, JOIN_LEFT_OUTER, on=sub_q_2.c.temp_id == TemplateMaster.id) \
            .join(sub_q_4, JOIN_LEFT_OUTER, on=TemplateMaster.id == sub_q_4.c.template_id) \
            .join(sub_ext_change_rx, JOIN_LEFT_OUTER, on=TemplateMaster.id == sub_ext_change_rx.c.template_id) \
            .join(TemplateDetails, JOIN_LEFT_OUTER, on=TemplateDetails.patient_id == TemplateMaster.patient_id) \
            .group_by(TemplateMaster.file_id, TemplateMaster.patient_id) \
            .where(FileHeader.company_id == company_id, TemplateMaster.status << status) \
            .order_by(SQL('duplicate_packs_present').desc(),
                      SQL('duplicate_template_present').desc(), SQL('FIELD(is_template_modified, 1,2,0)'),
                      TemplateMaster.id)

        for record in query.dicts():
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["admin_date_list"] = list()
            temp_slot_data_2 = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                                   TempSlotInfo.hoa_date.alias('hoa_date'),
                                                   TempSlotInfo.file_id.alias('file_id')) \
                .where(TempSlotInfo.patient_id == record['patient_id'], TempSlotInfo.file_id == record['file_id']) \
                .order_by(TempSlotInfo.hoa_date).alias('temp_slot_data_2')
            for temp in list(temp_slot_data_2):
                if temp.patient_id_id == record["patient_id"] and temp.file_id_id == record["file_id"]:
                    hoa_date = temp.hoa_date.strftime('%m-%d-%y')
                    if hoa_date not in record["admin_date_list"]:
                        record["admin_date_list"].append(hoa_date)

            if not record.get("admin_date_list", None):
                continue
            record["admin_period"] = str(
                record["admin_date_list"][0] + "  to  " + record["admin_date_list"][
                    len(record["admin_date_list"]) - 1])
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None

            # Reset the list so that it does not carry forward data from previous record
            linked_packs_list = []
            change_rx_comment_list = []

            # Prepare the list of Linked Packs and Change Rx Comments to link data for Change Rx Templates
            if record["linked_packs"] is not None:
                linked_packs_list = list(map(lambda x: int(x), record["linked_packs"].split(',')))

            if record["change_rx_comment"] is not None:
                change_rx_comment_list = list(map(lambda x: str(x), record["change_rx_comment"].split(',')))

            record["linked_packs"] = linked_packs_list
            record["change_rx_comment"] = change_rx_comment_list

            yield record

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error(e)
        raise Exception


@log_args_and_response
def db_get_ext_change_rx_by_template(template_id: int):
    try:
        return ExtChangeRx.db_get(template_id=template_id)
    except (IntegrityError, DataError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pending_templates_data(company_id):
    """ Gets all the pending template meta data based on the given company

        Args:
            company_id (int): company_id for which templates need to be fetched

        Returns:
            List : List of all the template meta data for the given company_id.

        Examples:
            >>> TemplateMaster.db_get_pending_templates_data(3)
            >>> []

    """
    try:
        TemplateMasterAlias = TemplateMaster.alias()
        pending_template_status = settings.PENDING_PROGRESS_TEMPLATE_LIST
        pending_template_data = []
        hoa_date_list = defaultdict(set)
        linked_packs_list: List[int] = []
        change_rx_comment_list: List[str] = []

        current_date = get_current_date()
        previous_date = datetime.datetime.strptime(current_date, '%Y-%m-%d') - datetime.timedelta(days=60)
        # if optimization is needed in sub_q 3 filter based on admin dates by adding
        # packdetails.consumption_start_date > previous date

        template_data = TemplateMaster.select(TemplateMaster.patient_id,
                                              TemplateMaster.file_id).dicts() \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << pending_template_status)

        file_patient_list = list()
        patient_ids = list()

        # fetching patient_file info to filter temp_slot_info and patinet_ids to filter packs info
        for record in template_data:
            file_patient_list.append('{}#{}'.format(record['patient_id'], record['file_id']))
            patient_ids.append(record['patient_id'])

        if not patient_ids:
            return pending_template_data
        packs_query = PackHeader.select(PackHeader.patient_id.alias('patient_id'),
                                        PackDetails.pack_display_id.alias('pack_display_id'),
                                        PackDetails.consumption_start_date.alias('consumption_start_date'),
                                        PackDetails.consumption_end_date.alias('consumption_end_date'),
                                        PackHeader.file_id.alias('file_id')) \
            .join(PackDetails,
                  on=((PackDetails.pack_header_id == PackHeader.id) &
                      (PackDetails.consumption_start_date > previous_date) &
                      (PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS])))) \
            .where(PackDetails.company_id == company_id,
                   PackHeader.patient_id << patient_ids).alias('packs_query')

        print(file_patient_list)
        sub_q_2 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(TemplateMasterAlias.id)).coerce(False)
                                        .alias('duplicate_template_ids')) \
            .join(TemplateMasterAlias, on=((TemplateMaster.patient_id == TemplateMasterAlias.patient_id) &
                                           (TemplateMasterAlias.id != TemplateMaster.id))) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMasterAlias.status << pending_template_status,
                   TemplateMaster.status << pending_template_status) \
            .group_by(TemplateMaster.id).alias('sub_q_2')

        temp_slot_data = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                             TempSlotInfo.hoa_date.alias('hoa_date'),
                                             TempSlotInfo.file_id.alias('file_id')) \
            .where(fn.CONCAT(TempSlotInfo.patient_id, '#', TempSlotInfo.file_id) << file_patient_list).alias(
            'temp_slot_data') \
            .order_by(TempSlotInfo.hoa_date)

        # query to get packs having overlapping or similar admin period for each template
        sub_q_3 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(packs_query.c.pack_display_id)).coerce(False)
                                        .alias('duplicate_pack_ids'),
                                        ) \
            .join(temp_slot_data, on=((temp_slot_data.c.file_id == TemplateMaster.file_id) &
                                      (temp_slot_data.c.patient_id == TemplateMaster.patient_id))) \
            .join(packs_query,
                  on=(
                          (TemplateMaster.patient_id == packs_query.c.patient_id) &
                          (temp_slot_data.c.hoa_date.between(packs_query.c.consumption_start_date,
                                                             packs_query.c.consumption_end_date)
                           ))) \
            .group_by(temp_slot_data.c.file_id, temp_slot_data.c.patient_id) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << pending_template_status).alias('sub_q_3')

        # query to get last ChangeRx received for any Template.
        # sub_q_ext_change_rx, sub_q_ext_change_rx_pack, sub_q_ext_change_rx_details = \
        #     db_get_linked_change_rx_details(company_id=company_id, template_status=pending_template_status)

        sub_ext_change_rx, sub_q_4 = db_get_template_change_rx_info(company_id=company_id, file_id=0, patient_id=0)

        logger.info('main_start' + str(datetime.datetime.now()))
        query = TemplateMaster.select(TemplateMaster.status,
                                      TemplateMaster.file_id,
                                      TemplateMaster.patient_id,
                                      TemplateMaster.is_modified.alias('is_template_modified'),
                                      TemplateMaster.created_date,
                                      TemplateMaster.id.alias('template_id'),
                                      TemplateMaster.delivery_datetime,
                                      TemplateMaster.system_id,
                                      TemplateMaster.id.alias('template_id'),
                                      PatientMaster.last_name, PatientMaster.first_name,
                                      fn.IF(sub_q_2.c.duplicate_template_ids, 1, 0)
                                      .alias('duplicate_template_present'),
                                      fn.IF(sub_q_3.c.duplicate_pack_ids, 1, 0)
                                      .alias('duplicate_packs_present'),
                                      sub_q_2.c.duplicate_template_ids,
                                      sub_q_3.c.duplicate_pack_ids,
                                      PatientMaster.pharmacy_patient_id, PatientMaster.patient_no,
                                      FacilityMaster.facility_name,
                                      fn.IF(TemplateMaster.task_id.is_null(False), True, False).alias('is_error'),
                                      CeleryTaskmeta.result.alias("template_result_message"),
                                      sub_q_4.c.linked_packs.alias("linked_packs"),
                                      sub_ext_change_rx.c.change_rx_comment.alias("change_rx_comment")) \
            .join(PatientMaster, on=PatientMaster.id == TemplateMaster.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(sub_q_3, JOIN_LEFT_OUTER, on=sub_q_3.c.temp_id == TemplateMaster.id) \
            .join(sub_q_2, JOIN_LEFT_OUTER, on=sub_q_2.c.temp_id == TemplateMaster.id) \
            .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=TemplateMaster.task_id == CeleryTaskmeta.task_id) \
            .join(sub_q_4, JOIN_LEFT_OUTER, on=TemplateMaster.id == sub_q_4.c.template_id) \
            .join(sub_ext_change_rx, JOIN_LEFT_OUTER, on=TemplateMaster.id == sub_ext_change_rx.c.template_id) \
            .group_by(TemplateMaster.id) \
            .order_by(SQL('duplicate_packs_present').desc(),
                      SQL('duplicate_template_present').desc(), SQL('is_error').desc(),
                      SQL('FIELD(is_template_modified, 1,2,0)'), TemplateMaster.id) \
            .where((TemplateMaster.company_id == company_id) &
                   ((TemplateMaster.status << settings.PENDING_TEMPLATE_LIST) |
                    ((TemplateMaster.status == settings.PROGRESS_TEMPLATE_STATUS) & (
                            CeleryTaskmeta.status != settings.PENDING_TEMPLATE_TASK_IN_TASK_QUEUE))))
        for record in query.dicts():
            record["template_result_message"] = decode_celery_result(record["template_result_message"]) if record[
                "is_error"] else None
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["admin_date_list"] = list()
            temp_slot_data_2 = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                                   TempSlotInfo.hoa_date.alias('hoa_date'),
                                                   TempSlotInfo.file_id.alias('file_id')) \
                .where(TempSlotInfo.patient_id == record['patient_id'], TempSlotInfo.file_id == record['file_id']) \
                .order_by(TempSlotInfo.hoa_date).alias('temp_slot_data_2')
            for temp in list(temp_slot_data_2):
                if temp.patient_id_id == record["patient_id"] and temp.file_id_id == record["file_id"]:
                    hoa_date = temp.hoa_date.strftime('%m-%d-%y')
                    if hoa_date not in record["admin_date_list"]:
                        record["admin_date_list"].append(hoa_date)

            if not record.get("admin_date_list", None):
                continue
            record["admin_period"] = str(
                record["admin_date_list"][0] + "  to  " + record["admin_date_list"][
                    len(record["admin_date_list"]) - 1])
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            record["admin_start_date"] = record["admin_date_list"][0]
            record["admin_end_date"] = record["admin_date_list"][len(record["admin_date_list"]) - 1]

            # Reset the list so that it does not carry forward data from previous record
            linked_packs_list = []
            change_rx_comment_list = []

            # Prepare the list of Linked Packs and Change Rx Comments to link data for Change Rx Templates
            if record["linked_packs"] is not None:
                linked_packs_list = list(map(lambda x: int(x), record["linked_packs"].split(',')))

            if record["change_rx_comment"] is not None:
                change_rx_comment_list = list(map(lambda x: str(x), record["change_rx_comment"].split(',')))

            record["linked_packs"] = linked_packs_list
            record["change_rx_comment"] = change_rx_comment_list
            pending_template_data.append(record)
        logger.info('main_end' + str(datetime.datetime.now()))
        return pending_template_data
    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error(e)
        raise Exception


@log_args_and_response
def db_get_linked_change_rx_details_customize(file_id, patient_id, company_id):
    linked_packs: List[int] = []
    change_rx_comment: List[str] = []

    try:
        template_data: Dict[str, Any] = TemplateMaster.db_get_template_id(file_id=file_id, patient_id=patient_id)

        # query to get last ChangeRx received for any Template.
        sub_q_ext_change_rx, sub_q_ext_change_rx_pack, sub_q_ext_change_rx_details = \
            db_get_linked_change_rx_details(company_id=company_id, template_status=settings.
                                            PENDING_PROGRESS_TEMPLATE_LIST, template_id=template_data["id"])

        query = TemplateMaster.select(TemplateMaster.id, sub_q_ext_change_rx_pack.c.linked_packs.alias("linked_packs"),
                                      sub_q_ext_change_rx_details.c.change_rx_comment.alias("change_rx_comment")) \
            .join(sub_q_ext_change_rx_pack, JOIN_LEFT_OUTER, on=TemplateMaster.id == sub_q_ext_change_rx_pack.c.
                  template_id) \
            .join(sub_q_ext_change_rx_details, JOIN_LEFT_OUTER, on=TemplateMaster.id == sub_q_ext_change_rx_details.c.
                  template_id) \
            .group_by(TemplateMaster.id) \
            .where(TemplateMaster.id == template_data["id"])

        for template in query.dicts():
            linked_packs = template["linked_packs"]
            change_rx_comment = template["change_rx_comment"]

        return linked_packs, change_rx_comment
    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error(e)
        raise Exception


@log_args_and_response
def db_get_linked_change_rx_details(company_id: int, template_status: List[int], template_id: Optional[int] = None):
    PackHeaderAlias = PackHeader.alias()
    PackDetailsAlias = PackDetails.alias()
    try:
        clauses = list()
        clauses.append(TemplateMaster.company_id == company_id)
        clauses.append(TemplateMaster.status << template_status)

        if template_id:
            clauses.append(TemplateMaster.id == template_id)

        # query to get last ChangeRx received for any Template.
        sub_q_ext_change_rx = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
                                                    fn.max(ExtChangeRx.id).alias("ext_change_rx_id")) \
            .join(ExtChangeRx, on=ExtChangeRx.new_template == TemplateMaster.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(TemplateMaster.id).alias("sub_q_ext_change_rx")

        # Link last ChangeRx with affected Packs for providing reference to user
        clauses.append(ExtPackDetails.status_id << settings.PACK_PROGRESS_DONE_STATUS_LIST)
        clauses.append(ExtPackDetails.pack_usage_status_id << constants.EXT_PACK_USAGE_STATUS_PENDING_ID)

        sub_q_ext_change_rx_pack = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
                                                         fn.GROUP_CONCAT(ExtPackDetails.ext_pack_display_id)
                                                         .coerce(False).alias("linked_packs")) \
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id))) \
            .join(PackHeaderAlias, on=PackHeader.patient_id == PackHeaderAlias.patient_id) \
            .join(PackDetailsAlias, on=PackDetailsAlias.pack_header_id == PackHeaderAlias.id) \
            .join(ExtPackDetails, on=PackDetailsAlias.id == ExtPackDetails.pack_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(TemplateMaster.id).alias("sub_q_ext_change_rx_pack").alias("sub_q_ext_change_rx_pack")

        # Link last ChangeRx with affected Rxs for providing reference of ChangeRx comments to user
        sub_q_ext_change_rx_details = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
                                                            fn.GROUP_CONCAT(fn.DISTINCT(ExtChangeRxDetails.
                                                                                        ext_comment)).
                                                            alias("change_rx_comment")) \
            .join(sub_q_ext_change_rx, on=TemplateMaster.id == sub_q_ext_change_rx.c.template_id) \
            .join(ExtChangeRxDetails, on=sub_q_ext_change_rx.c.ext_change_rx_id == ExtChangeRxDetails.
                  ext_change_rx_id) \
            .group_by(TemplateMaster.id).alias("sub_q_ext_change_rx_details")

        return sub_q_ext_change_rx, sub_q_ext_change_rx_pack, sub_q_ext_change_rx_details
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
