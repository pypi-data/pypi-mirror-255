import datetime
from collections import defaultdict
from datetime import timedelta

import pandas as pd
from peewee import InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import db

from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date, get_current_date_time, log_args_and_response, log_args, \
    convert_date_to_sql_date
from dosepack.validation.validate import validate
from src import constants
from src.dao.facility_dao import db_get_facility_info_dao, db_add_facility_schedule_dao, add_update_facility_dis_dao
from src.dao.patient_schedule_dao import update_patient_schedule_dao, get_schedule_details_dao, get_calender_info_dao, \
    delete_schedule_dao, get_patientwise_calender_schedule_dao
from src.dao.pack_dao import get_delivery_date_list_of_pending_packs, update_delivery_date_dao, db_get_facility_data_v3, \
    db_verify_packlist_by_company, update_schedule_id_null_dao, update_schedule_id_dao, \
    update_delivery_without_schedule_dao, db_update_delivery_date_and_delivery_status
from src.dao.template_dao import db_compare_min_admin_date_with_current_date, \
    db_setting_previous_facility_schedule_for_new_patient, db_update_patient_schedule
from src.service.misc import get_userid_by_ext_username

logger = settings.logger



@validate(required_fields=["company_id"])
def get_facility_info(dict_canister_info):
    company_id = dict_canister_info["company_id"]

    filter_fields = dict_canister_info.get('filter_fields', None)
    sort_fields = dict_canister_info.get('sort_fields', None)
    paginate = dict_canister_info.get('paginate', None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')


    try:
        response = None
        facility_list, count = db_get_facility_info_dao(
            company_id,
            filter_fields,
            sort_fields,
            paginate
        )
        return {"facility_data":facility_list,"number_of_records":count}

    except InternalError:
        return error(2001)


def add_schedule(schedule_data):
    """
    adds schedule for facility
    :param schedule_data: dict
    :return: json
    """
    try:
        current_date = schedule_data.get('current_date', get_current_date())
        schedule_details = schedule_data['schedule_list']
        with db.transaction():
            for schedule_detail in schedule_details:
                current_schedule = schedule_detail.get("current_schedule", False)
                if schedule_detail.get("module_id") in [constants.MODULE_DRUG_DISPENSING_TEMPLATES,
                                                        constants.MODULE_MANUAL_PACK_FILLING] and not current_schedule:
                    if schedule_detail.get("patient_id"):
                        start_date = db_compare_min_admin_date_with_current_date(
                            patient_id=schedule_detail["patient_id"],
                            file_id=schedule_detail["file_id"],
                            start_date=schedule_detail["start_date"])
                        schedule_info = {
                            'fill_cycle': schedule_detail["fill_cycle"],
                            'start_date': start_date,
                            'days': schedule_detail.get('days'),
                            'created_by': schedule_detail.get("user_id", 1),
                            'modified_by': schedule_detail.get("user_id", 1)}
                        record = db_add_facility_schedule_dao(schedule_info)
                        status = db_setting_previous_facility_schedule_for_new_patient(
                            patient_id=schedule_detail["patient_id"], facility_id=schedule_detail["facility_id"],
                            schedule_id=record.id, delivery_date_offset=schedule_detail["delivery_date_offset"])
                        return create_response({'schedule_info': schedule_details})
                    else:
                        status = db_update_patient_schedule(
                            patient_schedule_ids=schedule_detail['patient_schedule_ids'],
                            delivery_date_offset=schedule_detail['delivery_date_offset'],
                            fill_cycle=schedule_detail['fill_cycle'], user_id=schedule_detail['user_id'],
                            days=schedule_detail.get('days'), start_date=schedule_detail['start_date'])
                        # return create_response({'schedule_info': schedule_details})
                # week_day = schedule_detail.get("week_day", None)
                # delivery_week_day = schedule_detail.get("delivery_week_day", None)
                # if week_day and delivery_week_day:
                #     delivery_date_offset = delivery_week_day - week_day
                start_date = schedule_detail["start_date"]
                # delivery_date = schedule_detail.get("delivery_date", None)
                delivery_date_offset = schedule_detail["delivery_date_offset"]
                # if start_date and delivery_date:
                #     delivery_date_offset = (datetime.datetime.strptime(delivery_date, '%Y-%m-%d') -
                #                             datetime.datetime.strptime(start_date, '%Y-%m-%d')).days
                # if week_day in range(0,7):
                #     week_day = (week_day - 1) % 7  # angular to python weekday conversion
                schedule_info = {
                    'fill_cycle': schedule_detail["fill_cycle"],
                    'start_date': start_date,
                    'days': schedule_detail.get('days'),
                    'created_by': schedule_detail.get("user_id", 1),
                    'modified_by': schedule_detail.get("user_id", 1),
                    # 'week_day': week_day,
                }
                record = db_add_facility_schedule_dao(schedule_info)
                if not current_schedule:

                    update_dict = {"schedule_id": record.id,
                                   "delivery_date_offset": delivery_date_offset,
                                   "modified_date": get_current_date_time()}
                    update_patient_schedule_dao(update_dict, schedule_detail)

                update_delivery_date({'patient_schedule_ids': schedule_detail['patient_schedule_ids'],
                                      'update_existing': True,
                                      'current_date': current_date,
                                      'current_schedule': current_schedule,
                                      'start_date': start_date})
                schedule_detail['schedule_id'] = record.id

                # fetch min delivery date at facility level
                delivery_date_set = get_delivery_date_list_of_pending_packs(
                                                        patient_schedule_ids=schedule_detail['patient_schedule_ids'])
                if None in delivery_date_set:
                    schedule_detail["delivery_date"] = None
                else:
                    schedule_detail["delivery_date"] = str(min(delivery_date_set)) if delivery_date_set else None
            return create_response({'schedule_info': schedule_details})
    except KeyError as e:
        logger.error(e, exc_info=True)
        return error(1001)
    except (InternalError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def get_schedule_details(company_id, current_date, facility_list=None):
    """
    returns schedule for facility and patient for which no schedule is available
    :param company_id: company id
    :return: json
    """
    template_records = list()
    schedule_list = list()
    # schedule_list = defaultdict(dict)
    can_edit = True
    schedule_dict = dict()

    if current_date is None:
        current_date = get_current_date()
    try:

        # query = PatientSchedule.select(fn.COUNT(PatientSchedule.id).alias('total_patient'),
        #                                fn.GROUP_CONCAT(PatientSchedule.id).coerce(False).alias('patient_schedule_ids'),
        #                                fn.GROUP_CONCAT(PatientMaster.first_name, ' ', PatientMaster.last_name).coerce(
        #                                    False).alias('patient_names'),
        #                                fn.GROUP_CONCAT(PatientMaster.patient_no).alias('patient_nos'),
        #                                fn.SUM(PatientSchedule.total_packs).alias('total_packs'),
        #                                FacilitySchedule,
        #                                FacilityMaster,
        #                                PatientSchedule.modified_date,
        #                                FacilitySchedule.created_date,
        #                                FacilitySchedule.id.alias('facility_schedule_id')).dicts()\
        #     .join(FacilityMaster, on=PatientSchedule.facility_id == FacilityMaster.id)\
        #     .join(FacilitySchedule, JOIN_LEFT_OUTER, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
        #     .join(PatientMaster, on=PatientMaster.id == PatientSchedule.patient_id) \
        #     .where(FacilityMaster.company_id == company_id)\
        #     .group_by(PatientSchedule.facility_id, fn.date(PatientSchedule.modified_date), PatientSchedule.schedule_id)

        query = get_schedule_details_dao(company_id, facility_list)

        for record in query:
            # if record["week_day"] in range(0,7):
            #     record["week_day"] = (record["week_day"] + 1) % 7  # python to angular day conversion
            #     record['delivery_week_day'] = (record["week_day"] + timedelta(days=record['delivery_date_offset'])) % 7
            patient_data = {
                "patient_id": record['patient_id'],
                'total_packs': record['total_packs'],
                'first_name': record['first_name'],
                'last_name': record['last_name'],
                'patient_name': '{}, {}'.format(record['last_name'], record['first_name']),
                'patient_no': record['patient_no'],
                'last_import_date': record['last_import_date'],
                'patient_schedule_id': record['patient_schedule_id'],
                'days': record['days'],
                'fill_cycle': record['fill_cycle'],
                'delivery_date_offset': record['delivery_date_offset']
            }
            delivery_offset = record.get('delivery_date_offset', None)
            if delivery_offset is not None:
                schedule_info = get_expected_schedule(current_date=str(current_date),
                                                      start_date=str(record['start_date'].date()),
                                                      delivery_date_offset=record['delivery_date_offset'],
                                                      fill_cycle=record['fill_cycle'],
                                                      no_of_days=record['days'])
                patient_data['next_delivery_date'] = schedule_info['next_delivery_date']
                patient_data['next_schedule_date'] = schedule_info['next_schedule_date']
            if record['facility_id'] in schedule_dict:
                schedule_dict[record['facility_id']]['patient_info'].append(patient_data)
                if patient_data['last_import_date'] > schedule_dict[record['facility_id']]['last_import_date']:
                    schedule_dict[record['facility_id']]['last_import_date'] = patient_data['last_import_date']
            else:
                patient_info = list()
                patient_info.append(patient_data)
                schedule_dict[record['facility_id']] = {
                    'facility_id': record['facility_id'],
                    'schedule_id': record['schedule_id'],
                    'fill_cycle': record['fill_cycle'],
                    'days': record['days'],
                    'start_date': record['start_date'],
                    'company_id': record['company_id'],
                    "facility_name": record['facility_name'],
                    "patient_info": patient_info,
                    'last_import_date': record['last_import_date'],
                    'delivery_date_offset': record['delivery_date_offset']
                }
            schedule_list.append(record)
        for record in schedule_dict.values():
            delivery_offset = record.get('delivery_date_offset', None)
            if delivery_offset is not None:
                schedule_info = get_expected_schedule(current_date=str(current_date),
                                                      start_date=str(record['start_date'].date()),
                                                      delivery_date_offset=record['delivery_date_offset'],
                                                      fill_cycle=record['fill_cycle'],
                                                      no_of_days=record['days'])
                record['next_delivery_date'] = schedule_info['next_delivery_date']
                record['next_schedule_date'] = schedule_info['next_schedule_date']
                record['start_date'] = str(record['start_date'])
            record['last_import_date'] = str(record['last_import_date'])
        response = {
            'can_edit': can_edit,
            'schedule_info': list(schedule_dict.values())
        }
        return create_response(response)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def next_weekday(date, weekday):
    """
    returns specified weekday from given date
    :param date:
    :param weekday:
    :return:
    """
    day_gap = weekday - date.weekday()
    if day_gap < 0:
        day_gap += 7
    return date + timedelta(days=day_gap)


def get_calender_info(company_id, start_date, end_date, facility_list=None):
    """
    returns schedule data for given company_id in specified date range
    :param start_date:
    :param end_date:
    :param company_id:
    :return:
    """
    schedule_start_date = datetime.datetime.strptime((start_date), "%Y-%m-%d")
    end_date = datetime.datetime.strptime((end_date), "%Y-%m-%d")

    query = get_calender_info_dao(company_id, facility_list = None)


    freq_dict = {46: '7D', 47: '14D', 48: '28D'}
    facility_schedule = defaultdict(list)
    logger.info(query.sql())
    for record in query:
        try:
            frequency = freq_dict[record['fill_cycle']]
        except KeyError as e:
            frequency = "{}D".format(record['days'])
        # if not record.get('start_date', None):
        #     start_date = next_weekday(record['created_date'], record['week_day'])
        # else:
        #     start_date = record.get('start_date', start_date)
        start_date = record['start_date']
        schd = pd.date_range(start_date.date(), end_date, freq=frequency)
        for i in schd:
            if (i.date() >= schedule_start_date.date()):
                # if (record['week']):
                #     if week_of_month(i.date(), record['week']):
                #         facility_schedule[str(i.date())].append({'facility_name': record['facility_name'],
                #                                                  'total_patient': record['total_patient'],
                #                                                  'patient_schedule_ids': record['patient_schedule_ids'],
                #                                                  'patient_names': record['patient_names'],
                #                                                  'total_packs': record['total_packs']})
                # else:
                if record['delivery_date_offset'] is not None:
                    delivery_date = (i.date() + timedelta(days=record['delivery_date_offset']))
                else:
                    delivery_date = None
                facility_schedule[str(i.date())].append({
                    'facility_name': record['facility_name'],
                    'total_patient': record['total_patient'],
                    'patient_schedule_ids': record['patient_schedule_ids'],
                    'patient_names': record['patient_names'],
                    'total_packs': record['total_packs'],
                    'patient_nos': record['patient_nos'],
                    'delivery_date': delivery_date
                })
    return create_response(facility_schedule)


def delete_schedule(schedule_details):
    """
    deletes schedule for patients of facility
    :param schedule_details: list
    :return:
    """
    try:
        with db.transaction():
            patient_schedule_id_list = list()
            if not schedule_details:
                return error(1020, 'Empty data')
            for schedule_detail in schedule_details:
                current_date = schedule_detail.get('current_date', get_current_date())
                patient_schedule_id_list.extend(schedule_detail['patient_schedule_ids'])
            if patient_schedule_id_list:
                update_dict = {"schedule_id": None,
                               "delivery_date_offset": None,
                               "modified_date": get_current_date_time(),
                               "active" : False}
                delete_schedule_dao(update_dict, patient_schedule_id_list)

                delivery_date_set = update_delivery_date({'patient_schedule_ids': patient_schedule_id_list,
                                      'update_existing': True,
                                      'current_date': current_date})

            # FacilitySchedule.delete()\
            #     .where(FacilitySchedule.id.not_in(
            #     PatientSchedule.select(PatientSchedule.schedule_id)
            #         .where(PatientSchedule.active == True, PatientSchedule.schedule_id.is_null(False)))
            # ).execute()
            return create_response(True)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def remove_schedule(schedule_details):
    """
    removes schedule of facility
    :param schedule_details: list
    :return:
    """
    try:
        patient_schedule_id_list = list()
        for schedule_detail in schedule_details:
            current_date = schedule_detail.get('current_date', get_current_date())
            patient_schedule_id_list.extend(schedule_detail['patient_schedule_ids'])
        if patient_schedule_id_list:
            update_dict = {"schedule_id": None,
                           "delivery_date_offset": None,
                           "modified_date": get_current_date_time()}
            schedule_detail = {'patient_schedule_ids':patient_schedule_id_list}
            update_patient_schedule_dao(update_dict, schedule_detail)
            delivery_date_set = update_delivery_date({'patient_schedule_ids': patient_schedule_id_list,
                                  'update_existing': True,
                                  'current_date': current_date})
        return create_response(True)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def get_expected_schedule(current_date, start_date, delivery_date_offset, fill_cycle, no_of_days):
    """
    returns expected schedule for given data
    :param current_date:
    :param start_date:
    :param delivery_date_offset:
    :param fill_cycle:
    :param no_of_days:
    :return: dict
    """
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    current_date = datetime.datetime.strptime(current_date, "%Y-%m-%d")
    start_date = start_date.date()
    current_date = current_date.date()
    # current_date = datetime.datetime.now().date()
    delivery_date_offset = int(delivery_date_offset)
    if no_of_days is not None:
        no_of_days = int(no_of_days)
    response = {}
    freq_dict = {46: '7D', 47: '14D', 48: '28D'}
    days = {46: 7, 47: 14, 48: 28}
    fill_cycle = int(fill_cycle)
    try:
        frequency = freq_dict[fill_cycle]
        day = days[fill_cycle]
    except KeyError as e:
        frequency = "{}D".format(no_of_days)
        day = no_of_days
    # current_date = current_date.date()
    end_date = current_date + timedelta(days=day)
    schd = pd.date_range(start_date, end_date, freq=frequency)
    sch_date_list = list()
    for i in schd:
        sch_date_list.append(i.date())
    if current_date <= start_date:
        response['next_schedule_date'] = start_date
    elif current_date in sch_date_list:
        response["next_schedule_date"] = current_date
    else:
        last_schedule_date = sch_date_list[-2]
        last_schedule_date = datetime.datetime.combine(last_schedule_date, datetime.datetime.min.time())
        delivery_date = last_schedule_date + timedelta(days=delivery_date_offset)
        delivery_date = delivery_date.date()
        # import_date = datetime.datetime.combine(import_date, datetime.datetime.min.time())
        if current_date <= delivery_date:
            response['next_schedule_date'] = last_schedule_date
        else:
            last_schedule_date = sch_date_list[-1]
            response['next_schedule_date'] = last_schedule_date
    response['next_schedule_date'] = datetime.datetime.combine(response['next_schedule_date'],
                                                               datetime.datetime.min.time())
    response['next_delivery_date'] = response['next_schedule_date'] + timedelta(days=delivery_date_offset)
    response['next_delivery_date'] = str(response['next_delivery_date'])
    response['next_schedule_date'] = str(response['next_schedule_date'])

    return response


@log_args_and_response
def update_delivery_date(update_dict):
    logger.info('____called with {}'.format(update_dict))
    try:
        # if update_dict.get("current_schedule"):
        #     delivery_date_set = update_delivery_without_schedule_dao(update_dict)
        # else:
        delivery_date_set = update_delivery_date_dao(update_dict)
        return list(delivery_date_set)
    except (IntegrityError, InternalError, Exception) as e:
        logger.info(e)
        raise


@validate(required_fields=['company_id', 'user_id'])
def add_batch_distribution(batch_info):
    """
    Adds batch id i.e schedule id in pack details for given pack ids
    - creates data in batch formation
    :param batch_info:
    :return:
    """
    logger.debug(batch_info)
    pack_list = batch_info.get('pack_list', [])
    user_id = batch_info['user_id']
    status = batch_info['status_id']
    company_id = batch_info['company_id']
    facility_dis_id = batch_info.get('facility_distribution_id', None)
    response = {}
    try:
        if status != "Pending":
            return error(1020, "Batch already in process.")
        else:
            with db.transaction():
                status_id = settings.FACILITY_DISTRIBUTION_PENDING_STATUS

                valid_pack_list = db_verify_packlist_by_company(pack_list=pack_list, company_id=company_id)
                if not valid_pack_list:
                    return error(1026)

                if facility_dis_id is None:
                    facility_dis_id = add_update_facility_dis_dao(user_id=user_id, status_id=status_id, company_id=company_id)
                    print(facility_dis_id)
                    response['status'] = update_schedule_id_dao(pack_list=pack_list, facility_dis_id=facility_dis_id)
                    response['facility_dis_id'] = facility_dis_id

                else:
                    response['status'] = update_schedule_id_null_dao(pack_list, facility_dis_id, update=False)
                    response['facility_dis_id'] = None

                return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


@log_args
@validate(required_fields=["date_from", "date_to", "company_id"],
          validate_dates=['date_from', 'date_to'])
def get_facility_data_of_pending_packs(search_filters):
    """ Take the search filters which includes the date_from, to_date and retrieves all the
        facilities which satisfies the search criteria.

        Args:
            search_filters (dict): The keys in it are date_from(Date), date_to(Date),
                                   pack_status(str), system_id(int), company_id(int)

        Returns
           list: List of all the facilities which falls in the search criteria.

        Examples:
            >>> get_facility_data_of_pending_packs({"from_date": '01-01=01', "to_date": '01-12-16', \
                            "pack_status": '1', 'system_id': 2})
    """
    logger.debug("args for get_facility_data_of_pending_packs: " + str(search_filters))
    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    company_id = search_filters["company_id"]
    # system_id = search_filters.get("system_id", None)
    all_flag = search_filters.get('all_flag', False)
    status = [int(item) for item in str(search_filters["pack_status"]).split(',')]
    system_ids = [int(item) for item in str(search_filters["system_id"]).split(',')]
    filter_fields = search_filters.get('filter_fields', None)
    try:
        facility_list, facility_ids = db_get_facility_data_v3(
            date_from, date_to, status, filter_fields, company_id,
            system_ids=system_ids,
            all_flag=all_flag,
        )
        logger.debug("Pending packs Facility data retrieved")
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    response = {"facility_list": facility_list,
                "facility_ids": facility_ids}
    return create_response(response)


@log_args_and_response
def pharmacy_delivery_sync(list_args):
    try:
        for args in list_args:
            pack_display_id = args.get("pack_id")
            delivery_date = args.get("delivery_datetime")
            ips_username = args.get("username")
            delivery_status = args.get("delivery_status")
            company_id = args.get("company_id")
            user_info = get_userid_by_ext_username(ips_username, company_id)
            status = db_update_delivery_date_and_delivery_status(pack_display_id=pack_display_id,
                                                                 delivery_status=delivery_status,
                                                                 delivery_date=delivery_date, user_id=user_info["id"])
        return create_response(settings.SUCCESS_RESPONSE)
    except (IntegrityError, InternalError, Exception) as e:
        logger.info(e)
        raise


@log_args_and_response
def get_patientwise_calender_schedule(company_id, start_date, end_date, facility_list=None):
    """
    returns schedule data for given company_id in specified date range
    :param start_date:
    :param end_date:
    :param company_id:
    :return:
    """
    try:
        schedule_start_date = datetime.datetime.strptime((start_date), "%Y-%m-%d")
        end_date = datetime.datetime.strptime((end_date), "%Y-%m-%d")
        query = get_patientwise_calender_schedule_dao(company_id, facility_list = None)

        freq_dict = {46: '7D', 47: '14D', 48: '28D'}
        facility_schedule = defaultdict()
        logger.info(query.sql())

        for record in query:
            try:
                frequency = freq_dict[record['fill_cycle']]
            except KeyError as e:
                frequency = "{}D".format(record['days'])
            start_date = record['start_date']
            schd = pd.date_range(start_date.date(), end_date, freq=frequency)
            for i in schd:
                if i.date() >= schedule_start_date.date():
                    if record['delivery_date_offset'] is not None:
                        delivery_date = (i.date() + timedelta(days=record['delivery_date_offset']))
                    else:
                        delivery_date = None

                    if str(i.date()) not in facility_schedule:
                        facility_schedule[str(i.date())] = dict()
                        facility_schedule[str(i.date())][record["facility_id"]] = {
                            "facility_name": record["facility_name"],
                            "total_patients": 0,
                            "patient_info": list(),
                            "delivery_date": delivery_date,
                            "total_packs": 0
                        }
                    if record["facility_id"] not in facility_schedule[str(i.date())]:
                        facility_schedule[str(i.date())][record["facility_id"]] = {
                            "facility_name": record["facility_name"],
                            "total_patients": 0,
                            "patient_info": list(),
                            "delivery_date": delivery_date,
                            "total_packs": 0
                        }
                    facility_schedule[str(i.date())][record["facility_id"]]["patient_info"].append({
                        "patient_schedule_id": record["patient_schedule_id"],
                        "patient_name":  record["patient_name"],
                        "patient_no": record["patient_no"],
                        "packs": record["packs"]
                    })
                    facility_schedule[str(i.date())][record["facility_id"]]["total_patients"] += 1
                    facility_schedule[str(i.date())][record["facility_id"]]["total_packs"] += record["packs"]

        return create_response(facility_schedule)
    except (IntegrityError, InternalError, Exception) as e:
        logger.info(e)
        raise e