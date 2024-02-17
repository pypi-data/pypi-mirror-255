import functools
import operator

from peewee import InternalError, IntegrityError, DataError

import settings
from src.api_utility import get_filters, get_orders, apply_paginate
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_facility_schedule import FacilitySchedule

logger = settings.logger



def db_get_facility_info_dao(
            company_id,
            filter_fields,
            sort_fields,
            paginate
        ):
    try:
        facility_list, count = db_get_facility_info(
            company_id,
            filter_fields,
            sort_fields,
            paginate
        )
        return facility_list, count

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_max_canister_count {}".format(e))
        raise e


def db_add_facility_schedule_dao(schedule_info):
    try:
        return FacilitySchedule.db_add_facility_schedule(schedule_info)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_max_canister_count {}".format(e))
        raise e


def add_update_facility_dis_dao(user_id, status_id, company_id):
    try:
        return FacilityDistributionMaster.db_update_or_create_bdm(user_id=user_id, status_id=status_id, company_id=company_id)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in add_update_facility_dis_dao {}".format(e))
        raise e


def db_get_facility_info(company_id, filter_fields, sort_fields, paginate):
    canister_list = list()
    fields_dict = {

    }
    non_exact_search_list = ['name']
    membership_search_list = ['facility_id']

    clauses = list()
    clauses.append((FacilityMaster.company_id == company_id))

    order_list = list()
    clauses = get_filters(clauses, fields_dict, filter_fields,
                          like_search_fields=non_exact_search_list,
                          membership_search_fields=membership_search_list)
    order_list = get_orders(order_list, fields_dict, sort_fields)
    order_list.append(FacilityMaster.id)  # To provide same order for grouped data

    try:
        query = FacilityMaster.select(FacilityMaster.id.alias('facility_id'),
                                      FacilityMaster.facility_name).dicts()

        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        if order_list:
            query = query.order_by(*order_list)
        count = query.count()
        if paginate:
            query = apply_paginate(query, paginate)
        for record in query:
            canister_list.append(record)

        return (canister_list, count)

    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError

