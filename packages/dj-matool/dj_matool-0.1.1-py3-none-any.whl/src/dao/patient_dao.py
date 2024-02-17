import functools
import logging
import operator
from datetime import datetime
from peewee import JOIN_LEFT_OUTER, InternalError, IntegrityError, fn
import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response
from src.api_utility import get_filters, get_results
from src.model.model_code_master import CodeMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_facility_schedule import FacilitySchedule
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_note import PatientNote
from src.model.model_patient_rx import PatientRx
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_slot_details import SlotDetails
from src.model.model_drug_master import DrugMaster

logger = settings.logger

schedule_logger = logging.getLogger("schedule")


@log_args_and_response
def get_next_schedules(company_id, active=True, filter_fields=None, schedule_facility_ids=None,
                       ips_delivery_dict=None, scheduled_delivery_dict=None, patient_schedule_ids=None):
    """
    Returns schedule data for given schedule_facility_ids or schedule_date
    for given company_id
    :param company_id: int
    :param active: bool if True, consider active patients only, otherwise all patients
    :return: dict
    @param patient_schedule_ids:
    @param active:
    @param company_id:
    @param scheduled_delivery_dict:
    @param ips_delivery_dict:
    @param schedule_facility_ids:
    @param filter_fields:
    """
    schedule_data = dict()
    schedule_facility_data = dict()
    logger.debug("Inside get_next_schedules")

    try:

        clauses = [
            (FacilityMaster.company_id == company_id), ]

        if active:
            clauses.append((PatientSchedule.active == 1))

        # if schedule_facility_ids:
        #     clauses.append((fn.CONCAT(
        #         PatientSchedule.schedule_id, ':',
        #         PatientSchedule.facility_id) << schedule_facility_ids))

        membership_search_list = ['facility_ids']
        fields_dict = {
            "facility_ids": PatientSchedule.facility_id, }

        clauses = get_filters(clauses, fields_dict, filter_fields,
                              membership_search_fields=membership_search_list)

        query = PatientSchedule.select(
                                        PatientSchedule.schedule_id,
                                        PatientSchedule.patient_id,
                                        PatientSchedule.facility_id,
                                        PatientSchedule.delivery_date_offset,
                                        PatientSchedule.last_import_date,
                                        FacilitySchedule.fill_cycle,
                                        CodeMaster.value,
                                        FacilitySchedule.start_date,
                                        FacilitySchedule.days,
                                        PatientSchedule.id.alias('scheduled_patient_id'),
                                        FacilityMaster.facility_name) \
                                .join(FacilityMaster, on=FacilityMaster.id == PatientSchedule.facility_id) \
                                .join(PatientMaster, on=((PatientSchedule.patient_id == PatientMaster.id)
                                                         & (PatientSchedule.facility_id == PatientMaster.facility_id))) \
                                .join(FacilitySchedule, JOIN_LEFT_OUTER, on=FacilitySchedule.id == PatientSchedule.schedule_id) \
                                .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == FacilitySchedule.fill_cycle) \
                                .where(*clauses)

        logger.info("In get_next_schedules, query: {}".format(query.dicts()))

        for record in query.dicts():

            logger.info("In get_next_schedules, record: {}".format(record))

            schedule_id = record['schedule_id']
            facility_id = record['facility_id']
            patient_id = record.pop('patient_id')
            scheduled_patient_id = record.pop('scheduled_patient_id')
            last_import_date = record['last_import_date']
            if ips_delivery_dict and facility_id in ips_delivery_dict:
                record['ips_delivery_date'] = ips_delivery_dict[facility_id]
            else:
                record['ips_delivery_date'] = ""
            # if not schedule_id:
            #     continue
            schedule_facility_id = '{}:{}'.format(schedule_id, facility_id)
            record['schedule_facility_id'] = schedule_facility_id

            if schedule_facility_id not in schedule_facility_data:
                record['patient_ids'] = set()
                record['scheduled_patient_ids'] = set()
                schedule_facility_data[schedule_facility_id] = record
            elif last_import_date > schedule_facility_data[schedule_facility_id]['last_import_date']:
                schedule_facility_data[schedule_facility_id]['last_import_date'] = last_import_date
            schedule_facility_data[schedule_facility_id]['patient_ids'].add(patient_id)
            schedule_facility_data[schedule_facility_id]['scheduled_patient_ids'].add(scheduled_patient_id)

        logger.info("In get_next_schedules, schedule_facility_data: {}".format(schedule_facility_data))

        for record in schedule_facility_data.values():

            logger.info("In get_next_schedules, record: {}".format(record))

            schedule_logger.info('=====' * 14)
            schedule_facility_id = record['schedule_facility_id']

            if not record['schedule_id']:
                schedule_data[schedule_facility_id] = record
                _date_format = '%m-%d-%y'
                record['last_import_date'] = record['last_import_date'].date().strftime(_date_format)
                continue

            schedule_data[schedule_facility_id] = PatientSchedule.get_next_schedule_from_last_import(record)

            if scheduled_delivery_dict:
                if record['facility_id'] in scheduled_delivery_dict:
                    _date_format = '%m-%d-%y'

                    delivery_date = scheduled_delivery_dict[record['facility_id']]
                    if delivery_date and delivery_date != '':
                        delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d %H:%M:%S')
                        delivery_date = delivery_date.strftime(_date_format)

                    else:
                        delivery_date = None

                    schedule_data[schedule_facility_id].update({'delivery_date': delivery_date})
                    print('updated for', schedule_data[schedule_facility_id])

                else:
                    delivery_date = None
                    schedule_data[schedule_facility_id].update({'delivery_date': delivery_date})
                    print('updated for', schedule_data[schedule_facility_id])

        return schedule_data
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_patient_name_from_patient_id_dao(patient_delivery_date_dict):
    try:
        return PatientMaster.db_get_patient_name_from_patient_id(list(patient_delivery_date_dict.keys()))
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


def get_patient_wise_delivery_date(patient_list):
    patient_dd_dict = {}
    try:
        query = PackHeader.select(PackHeader.patient_id,
                                  fn.MAX(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date')) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PatientRx, on=PatientRx.patient_id == PatientMaster.id) \
            .join(PackRxLink, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackHeader.scheduled_delivery_date.is_null(False), PatientMaster.id << patient_list) \
            .group_by(PatientMaster.id)  # PackHeader.scheduled_delivery_date.is_null(True)

        for record in query.dicts():
            patient_dd_dict[record['patient_id']] = record["scheduled_delivery_date"]
        return patient_dd_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def get_patient_rx_data(pack_ids: list):
    """
        get patient rx data by dae
        @param pack_ids:
        @return:

    """
    try:
        clauses: list = list()
        clauses.append((PackRxLink.pack_id << pack_ids))
        clauses.append((PatientRx.daw_code == 0))
        # if pack_rx_ids:
        #     clauses.append((PackRxLink.id.not_in(pack_rx_ids)))
        query = PackRxLink.select(PackRxLink.patient_rx_id,
                                  PackRxLink.id,
                                  PackRxLink.original_drug_id,
                                  SlotDetails.drug_id,
                                  PackRxLink.pack_id,
                                  PackDetails.pack_display_id
                                  ).dicts() \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(functools.reduce(operator.and_, clauses))
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_patient_rx_data {}".format(e))
        raise e


@log_args_and_response
def get_patient_facility_id_data(patient_list):
    try:
        patient_facility_dict = {}
        query = PatientMaster.select(PatientMaster.id, PatientMaster.facility_id).where(
            PatientMaster.id << patient_list)

        for record in query.dicts():
            patient_facility_dict[record['id']] = record['facility_id']
        return patient_facility_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        print(e)
        raise


@log_args_and_response
def db_get_patient_info_by_patient_id_dao(patient_id):
    try:
        return PatientMaster.db_get_patient_info_by_patient_id(patient_id=patient_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_patient_name_patient_no_from_patient_id_dao(patient_id):
    try:
        return PatientMaster.db_get_patient_name_patient_no_from_patient_id(patient_id=patient_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_patient_master_update_or_create_dao(dict_patient_master_data, pharmacy_patient_id, company_id,
                                           default_data_dict, facility_id, remove_fields_list):
    try:
        return PatientMaster.db_update_or_create(
            dict_patient_master_data, pharmacy_patient_id,
            company_id=company_id,
            default_data_dict=default_data_dict,
            add_fields={
                'facility_id': facility_id
            },
            remove_fields=remove_fields_list
        )
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_patient_data_dao(patient_id: int):
    try:
        return PatientNote.db_get(patient_id=patient_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_patient_data_dao {}".format(e))
        raise e


@log_args_and_response
def patient_note_update_or_create_dao(patient_id: int, patient_note, user_id):
    try:
        return PatientNote.db_update_or_create(patient_id=patient_id,
                                               note=patient_note,
                                               user_id=user_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in patient_note_update_or_create_dao {}".format(e))
        raise e


def get_patients_dao(company_id, filter_fields, paginate, sort_fields):
    """
    get patient data
    @param company_id:
    @param filter_fields:
    @param paginate:
    @param sort_fields:
    @return:
    """
    try:
        clauses: list = list()
        between_search_list: list = list()
        exact_search_list: list = list()
        clauses.append((PatientMaster.company_id == company_id))
        order_list: list = list()
        if sort_fields:
            order_list.extend(sort_fields)
        fields_dict = {  # do not give alias here, instead give it in select_fields,
            # as this can be reused in where clause
            "patient_id": PatientMaster.id,
            "patient_no": PatientMaster.patient_no,
            "first_name": PatientMaster.first_name,
            "last_name": PatientMaster.last_name,
            "patient_name": PatientMaster.concated_patient_name_field(),
        }
        select_fields = [fields_dict["patient_id"].alias('patient_id'),
                         fields_dict["patient_no"].alias('patient_no'),
                         fields_dict["first_name"].alias('first_name'),
                         fields_dict["last_name"].alias('last_name'),
                         fields_dict["patient_name"].alias('patient_name')]

        query = PatientMaster.select(*select_fields)
        like_search_list = ['patient_no']
        membership_search_list = ['patient_id']
        results, count = get_results(query.dicts(), fields_dict, clauses=clauses,
                                     filter_fields=filter_fields,
                                     sort_fields=order_list,
                                     paginate=paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     between_search_list=between_search_list,
                                     membership_search_list=membership_search_list,
                                     last_order_field=[fields_dict['patient_id']])
        return count, results
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_patients_dao {}".format(e))
        raise e

@log_args_and_response
def get_patient_rx_id_based_on_pack_id_and_drug_id(args):

    try:
        response = dict()
        for pack_id, drug_ids in args.items():

            txr_list = DrugMaster.db_get_multiple_txr_by_drug_id(drug_ids)
            logger.info("In get_patient_rx_id_based_on_pack_id_and_drug_id: txr_list {}".format(txr_list))
            select_fields = [PatientRx.id.alias("patient_rx_id")]

            query = PatientRx.select(*select_fields).dicts()\
                .join(PackRxLink, on=PatientRx.id == PackRxLink.patient_rx_id)\
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
                .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id)\
                .where((PackDetails.id == pack_id) & (DrugMaster.txr << txr_list))

            patient_rx_id = list()
            for records in query:
                if records["patient_rx_id"] not in patient_rx_id:
                    patient_rx_id.append(records["patient_rx_id"])

            response[pack_id] = patient_rx_id

        return response
    except Exception as e:
        logger.error("error in get_patient_rx_id_based_on_pack_id_and_drug_id {}".format(e))
        raise e

@log_args_and_response
def db_update_patient_rx_for_manual_pack_filling(drug_data, patient_rx_update_data) -> bool:
    """
    update patient rx data by patient rx id
    :return:
    """
    try:
        patient_rx_status = None
        with db.transaction():
            for txr, ndc in drug_data.items():
                if ndc in patient_rx_update_data:
                    update_dict = patient_rx_update_data[ndc]["update_dicts"]
                    patient_rx_id = patient_rx_update_data[ndc]["patient_rx_id"]

                    patient_rx_status = PatientRx.db_update_multiple_patient_rx_data(update_dict,
                                                                                     patient_rx_id
                                                                                     )

                    logger.info("In db_update_patient_rx_for_manual_pack_filling: patient_rx_status: {}".format(
                        patient_rx_status
                    ))

        return patient_rx_status
    except Exception as e:
        logger.error("Error in db_update_patient_rx_for_manual_pack_filling {}".format(e))
        raise e

@log_args_and_response
def db_update_patient_rx_data_in_dao(update_dict: dict, patient_rx_id: int):
    try:
        status = PatientRx.db_update_patient_rx_data(update_dict=update_dict,
                                                     patient_rx_id=patient_rx_id
                                                     )
        return status
    except Exception as e:
        logger.error("Error in db_update_patient_rx_data_in_dao: {}".format(e))
        raise e