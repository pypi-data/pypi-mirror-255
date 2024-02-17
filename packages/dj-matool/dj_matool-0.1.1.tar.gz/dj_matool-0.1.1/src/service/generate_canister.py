# -*- coding: utf-8 -*-
"""
    src.generate_canister
    ~~~~~~~~~~~~~~~~
    This module provides function to provide data of generate canister
    Todo:
    :copyright: (c) 2015 by Dose-pack LLC.

"""

import json
import os
import sys

import settings
from src import constants
from typing import Dict, Any
from dosepack.base_model.base_model import db
from dosepack.validation.validate import validate
from peewee import InternalError, IntegrityError, DataError
from dosepack.utilities.utils import get_current_date_time, log_args_and_response, get_canister_volume, \
    get_max_possible_drug_quantities_in_canister, log_args
from dosepack.error_handling.error_handler import error, create_response
from src.dao.drug_inventory_dao import get_drug_info_based_on_ndc_dao
from src.dao.drug_dao import db_get_drug_info_by_canister
from src.exceptions import InventoryBadRequestException, InventoryDataNotFoundException, \
    InventoryBadStatusCode, InventoryConnectionException, InvalidResponseFromInventory
from src.service.canister_testing import add_canister_testing_data
from src.service.volumetric_analysis import get_drug_canister_recommendation_by_ndc_dimension, \
    get_drug_dimension_by_drug
from src.dao.generate_canister_dao import get_available_drug_canister, \
    get_drug_info_for_requested_canister, get_requested_canister_stick_data_from_stick_id, \
    get_request_canister_status_info, \
    get_same_stick_canister_list, get_recommended_stick_canister_data, \
    delete_recom_temp_stick_canister_data, check_existence_record, get_same_stick_canister_info, \
    update_stick_canister_status, update_odoo_requested_canister_status, \
    get_recom_stick_canister_data, get_canister_info_by_canister_id, get_drug_dimension_info_by_unique_drug_id, \
    insert_stick_canister_data, update_order_no_canister_list, get_drug_requested_canister_count, \
    insert_requested_canister_data

logger = settings.logger


@log_args_and_response
@validate(required_fields=["company_id"])
def get_canister_request_list(data: dict) -> dict:
    """
    return list of drug info for which canister is requested
    @param data:
    @return:
    """
    company_id = data.get('company_id')
    filter_fields = data.get('filter_fields', None)
    sort_fields = data.get('sort_fields', None)
    paginate = data.get('paginate', None)

    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, ' Missing key(s) in paginate.')
    try:
        # get data of drug info(requested canister drug info) and number of drug for which canister is requested
        results, count = get_drug_info_for_requested_canister(company_id=company_id,
                                                              filter_fields=filter_fields,
                                                              sort_fields=sort_fields, paginate=paginate)
        for record in results:
            # get count of available canister for drug
            available_canister = get_available_drug_canister(company_id=company_id,
                                                             fndc=record['formatted_ndc'],
                                                             txr=record['txr'])
            logger.info("In get_canister_request_list : available_canister_count: {} ,for formatted_ndc: {}, txr: {}"
                        .format(len(available_canister), record['formatted_ndc'], record['txr']))
            record['available_canister_count'] = len(available_canister)
        response_data = {"drug_data": results,
                         "number_of_drugs": count}

        return create_response(response_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_request_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_canister_request_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_request_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_canister_request_list: " + str(e))


@log_args_and_response
@validate(required_fields=["company_id", "ndc"])
def get_request_canister_status_data(canister_request_data: dict) -> dict:
    """
    return requested canister status in canister request status screen
    @param canister_request_data:
    @return:
    """
    ndc = canister_request_data.get('ndc')
    try:
        # get fndc txr by ndc
        drug_info: Dict[str, Any] = get_drug_info_based_on_ndc_dao(ndc_list=[ndc])
        logger.info("In get_request_canister_status_data: given ndc: {} and drug_info: {}".format(ndc, drug_info))

        # get requested canister status information from generate canister table
        requested_canister_status_info = get_request_canister_status_info(canister_request_data=canister_request_data,
                                                                          fndc=drug_info[ndc]['formatted_ndc'],
                                                                          txr=drug_info[ndc]['txr'])
        response_data = {"requested_canister_status_info": requested_canister_status_info}

        return create_response(response_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_request_canister_status_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_request_canister_status_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_request_canister_status_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_request_canister_status_data: " + str(e))


@log_args_and_response
@validate(required_fields=['unique_drug_id', 'canister_id'])
def get_replenish_test_data(data: dict) -> dict:
    """
    return max canister capacity for replenish drug
    @param data:
    @return:
    """
    canister_id = data.get('canister_id')
    unique_drug_id = data.get('unique_drug_id')
    try:

        # get canister type from canister id
        canister_info = get_canister_info_by_canister_id(canister_id=int(canister_id))

        # find canister volume based on canister type
        canister_usable_volume = get_canister_volume(canister_type=canister_info['canister_type'])
        logger.info("In get_replenish_test_data: canister_usable_volume: {}".format(canister_usable_volume))

        # get drug_approx_volume from drug dimension master table
        drug_dimension_data = get_drug_dimension_info_by_unique_drug_id(unique_drug_id=int(unique_drug_id))

        # find max possible drug quantity in canister(canister_capacity)
        canister_capacity = get_max_possible_drug_quantities_in_canister(canister_volume=canister_usable_volume,
                                                                         unit_drug_volume=float(
                                                                             drug_dimension_data['approx_volume']))
        logger.info("In get_replenish_test_data: canister_capacity : {}".format(canister_capacity))
        response_data = {"canister_capacity": canister_capacity,
                         "fill_quantity": settings.MINIMUM_FILL_QUANTITY_REPLENISH_TEST}

        return create_response(response_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_replenish_test_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_replenish_test_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_replenish_test_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_replenish_test_data: " + str(e))


@log_args_and_response
@validate(required_fields=["ndc", "company_id", "user_id"])
def store_recommend_stick_canister(drug_canister_data: dict) -> dict:
    """
    store recommended stick canister data in TempRecommendedStickCanisterData table
    1. 1st check if available canister count is more than required canister count no need to generate other canister
    2. get recommended stick for given ndc
    3. get canister for recommended stick
    4. store recommended stick canister data in specific formate
    :return:
    """
    try:

        user_id = drug_canister_data.get("user_id")
        ndc = drug_canister_data.get("ndc")
        company_id = drug_canister_data.get("company_id")
        max_canister: int = 0
        order_no: int = 1
        stick_sequence, canister_sequence = 0, 0
        list_canister: list = list()
        recomm_canister_list: list = list()
        final_canister_list: list = list()
        canister_with_stick_dict: dict = dict()
        stick_id_list: list = list()
        generate_canister_flag: int = 0  # by default, it is 0 but, it is 1 if generate request for canister
        temp_data_inserted_status: bool = False
        response_code: int = 0  # {response_code 1 : available_canister_count >= required_canister_count ,
        # response_code 2: available_canister_count + requested_canister_count >= required_canister_count,
        # response_code  3: stick is not recommended for given ndc ,
        # response_code  4: stick is recommended but de-active canister is not
        #                   available for recommended stick,
        # response_code 5: stick is recommended ,de-active canister is available but when we test canister it is tested,
        #                   testing status is not pass

        # 1. check if available canister count is more than required canister count then return error
        # get fndc txr by ndc
        drug_info: Dict[str, Any] = get_drug_info_based_on_ndc_dao(ndc_list=[ndc])
        logger.info("In store_recommend_stick_canister: given ndc: {} and drug_info: {}".format(ndc, drug_info))

        # get available canister count for drug
        available_canister = get_available_drug_canister(company_id=company_id,
                                                         fndc=drug_info[ndc]['formatted_ndc'],
                                                         txr=drug_info[ndc]['txr'])
        logger.info("In store_recommend_stick_canister: available canister count:{} ".format(len(available_canister)))

        # if available_canister > REQUIRED_CANISTER_COUNT then response code = 1 and no need to generate request
        # for canister then generate_canister_flag = 0
        if len(available_canister) >= settings.REQUIRED_CANISTER_COUNT:
            return create_response({'recom_stick_id_list': stick_id_list,
                                    'canister_with_stick': 0,
                                    'temp_data_inserted_status': temp_data_inserted_status,
                                    'generate_canister_flag': generate_canister_flag,
                                    'response_code': 1})

        # get requested canister count from generate canister table (requested status in [approved, in progress, pending, Done])
        requested_canister_count = get_drug_requested_canister_count(company_id=company_id,
                                                                     fndc=drug_info[ndc]['formatted_ndc'],
                                                                     txr=drug_info[ndc]['txr'])
        logger.info("In store_recommend_stick_canister: requested canister count:{} ".format(requested_canister_count))

        # if available canister count + requested canister count is greater than required canister count
        # then no need to generate new canister response_code = 2
        if len(available_canister) + requested_canister_count >= settings.REQUIRED_CANISTER_COUNT:
            return create_response({'recom_stick_id_list': stick_id_list,
                                    'canister_with_stick': 0,
                                    'temp_data_inserted_status': temp_data_inserted_status,
                                    'generate_canister_flag': generate_canister_flag,
                                    'response_code': 2})

        # 2. get recommended stick for given ndc
        stick_data = get_drug_canister_recommendation_by_ndc_dimension(dict_drug_info=drug_canister_data)
        stick_id_list = json.loads(stick_data)["data"]["canister_stick_id_list"]
        logger.info("In store_recommend_stick_canister: recommended stick id list:{} ".format(stick_id_list))

        drug_canister_data["stick_id_list"] = stick_id_list

        # if no stick is recommended response code = 3
        if not stick_id_list:
            return create_response({'recom_stick_id_list': stick_id_list, 'canister_with_stick': 0,
                                    'temp_data_inserted_status': temp_data_inserted_status, 'generate_canister_flag': 1,
                                    'response_code': 3})

        # 3. get other canister of recommended
        # stick same_stick_canister_dict = {s1: [{'canister_id': c1},{'canister_id': c2},{'canister_id': c3},{'canister_id': c4}],
        #                                   s2: [{'canister_id': c5}]
        #                                   }
        same_stick_canister_dict = get_same_stick_canister_list(drug_canister_data=drug_canister_data)

        # find max number of stick for which canister is available
        total_stick = len(same_stick_canister_dict.keys())
        logger.info("In store_recommend_stick_canister: Total number of stick for which canister is available:{}"
                     .format(total_stick))

        # canister is not available for recommended stick response_code = 4
        if not same_stick_canister_dict:
            return create_response({'recom_stick_id_list': stick_id_list, 'canister_with_stick': 0,
                                    'temp_data_inserted_status': temp_data_inserted_status,
                                    'generate_canister_flag': 1, 'response_code': 4})

        # check any record exist in table for given user_id then delete record and insert new record in table
        existence = check_existence_record(user_id=user_id)

        if existence:
            status = delete_recom_temp_stick_canister_data(user_id=user_id)
            logger.info("In store_recommend_stick_canister: record exist in table for given user id then"
                        "delete record from temp table:{}".format(status))

        #  create link_canister = [(c1,c2,c3,c4),(c5,c6,c7),(c8,c9),(c10)] from same_stick_canister_dict
        for stick, canister_list in same_stick_canister_dict.items():
            canister_id_list: list = list()
            # find max number of canister available for recommended stick
            if max_canister < len(canister_list):
                max_canister = len(canister_list)
            for data in canister_list:
                # create dict of canister_id with stick
                canister_with_stick_dict[data['canister_id']] = stick
                canister_id_list.append(data['canister_id'])
            list_canister.append(tuple(canister_id_list))

        logger.info("In store_recommend_stick_canister: list_canister:{}".format(list_canister))
        # 3.  create list to store data in table TempRecommendedStickCanisterData()
        #     - 1st canister of 1st stick  then 1st canister of 2nd stick  for all stick then repeat
        #     - 2nd canister of 1st stick  then 2nd canister of 2nd stick 2nd canister so on....
        # final_canister_list = [c1,c5,c8,c10,c2,c6,c9,c3,c7,c4]
        while stick_sequence + 1 <= total_stick and canister_sequence + 1 <= max_canister:
            if list_canister[stick_sequence]:
                if canister_sequence < len(list_canister[stick_sequence]):
                    if list_canister[stick_sequence][canister_sequence]:
                        final_canister_list.append(list_canister[stick_sequence][canister_sequence])
                        stick_sequence += 1
                else:
                    stick_sequence += 1
                if stick_sequence == total_stick:
                    stick_sequence = 0
                    canister_sequence += 1

        # insert recommended stick canister data in TempRecommendedStickCanisterData table with pending status
        for canister_id in final_canister_list:
            temp_recommend_canister_test_data = {"canister_id": canister_id,
                                                 "canister_stick_id": canister_with_stick_dict[canister_id],
                                                 "status": constants.CANISTER_TESTING_PENDING, "order_no": order_no,
                                                 "user_id": user_id, "recommended_stick": True}
            order_no += 1
            recomm_canister_list.append(temp_recommend_canister_test_data)

        temp_data_inserted_status = insert_stick_canister_data(canister_list=recomm_canister_list)
        response = {'recom_stick_id_list': stick_id_list,
                    'canister_with_stick': total_stick,
                    'temp_data_inserted_status': temp_data_inserted_status,
                    'generate_canister_flag': generate_canister_flag,
                    'response_code': response_code}
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in store_recommend_stick_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in store_recommend_stick_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in store_recommend_stick_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in store_recommend_stick_canister: " + str(e))


@log_args_and_response
@validate(required_fields=["ndc", "company_id", "user_id"])
def get_recommended_stick_canister(dict_drug_canister_info: dict) -> Dict:
    """
    function to get next canister data for generate canister screen from TempRecommendedStickCanisterData table
    @param dict_drug_canister_info:
    @return:
    """
    user_id = dict_drug_canister_info.get("user_id")
    company_id = dict_drug_canister_info.get("company_id")
    ndc = dict_drug_canister_info.get("ndc")
    canister_data: dict = dict()
    canister_info: list = list()
    requested_canister_count: int = 0
    generate_canister_flag: int = 0
    response_code: int = 0  # {response_code 1 : available_canister_count >= required_canister_count ,
    # response_code 2: available_canister_count + requested_canister_count >= required_canister_count,
    # response_code 3: stick is not recommended for given ndc , 4: stick is recommended but de-active canister is not available
    #                   for recommended stick,
    # response_code 5: stick is recommended ,de-active canister is available but when we test canister it is tested,
    #                    testing status is not pass

    try:

        # get fndc txr by ndc
        drug_info: Dict[str, Any] = get_drug_info_based_on_ndc_dao(ndc_list=[ndc])
        logger.info("In get_recommended_stick_canister: given ndc: {} and drug_info: {}".format(ndc, drug_info))

        # get available canister count for drug
        available_canister = get_available_drug_canister(company_id=company_id,
                                                         fndc=drug_info[ndc]['formatted_ndc'],
                                                         txr=drug_info[ndc]['txr'])
        logger.info("In get_recommended_stick_canister: available canister count:{} ".format(len(available_canister)))

        # if available canister count is more than required canister count then return error message
        if len(available_canister) >= settings.REQUIRED_CANISTER_COUNT:
            return create_response({"canister_data": canister_info,
                                    "available_canister_count": len(available_canister),
                                    "required_canister_count": settings.REQUIRED_CANISTER_COUNT,
                                    "requested_canister_count": requested_canister_count,
                                    "generate_canister_flag": generate_canister_flag, 'response_code': 1})

        # get requested canister count from generate canister table (requested status in [approved, in progress, pending, Done])
        requested_canister_count = get_drug_requested_canister_count(company_id=company_id,
                                                                     fndc=drug_info[ndc]['formatted_ndc'],
                                                                     txr=drug_info[ndc]['txr'])
        logger.info("IN get_recommended_stick_canister: requested canister count: {}".format(requested_canister_count))

        # if available canister count + requested canister count is greater than required canister count
        # then no need to generate new canister
        if len(available_canister) + requested_canister_count >= settings.REQUIRED_CANISTER_COUNT:
            return create_response({"canister_data": canister_info, "available_canister_count": len(available_canister),
                                    "required_canister_count": settings.REQUIRED_CANISTER_COUNT,
                                    "requested_canister_count": requested_canister_count,
                                    "generate_canister_flag": generate_canister_flag, 'response_code': 2})

        # get recommended canister data
        canister_info = get_recommended_stick_canister_data(company_id=company_id, user_id=user_id)
        logger.info("In get_recommended_stick_canister: recommended canister for drug: {}".format(canister_info))

        # recommended stick canister is not available and available + requested canister count < required
        # then generate request for new canister
        if not canister_info:
            return create_response({"canister_data": canister_info, "available_canister_count": len(available_canister),
                                    "required_canister_count": settings.REQUIRED_CANISTER_COUNT,
                                    "requested_canister_count": requested_canister_count,
                                    "generate_canister_flag": 1, 'response_code': 5})

        canister_data["canister_data"] = canister_info
        canister_data["available_canister_count"] = len(available_canister)
        canister_data["required_canister_count"] = settings.REQUIRED_CANISTER_COUNT
        canister_data["requested_canister_count"] = requested_canister_count
        canister_data["response_code"] = response_code
        return create_response(canister_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommended_stick_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_recommended_stick_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommended_stick_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_recommended_stick_canister: " + str(e))


@log_args_and_response
@validate(
    required_fields=["canister_id", "ndc", "status_id", "user_id", "company_id", "device_id", "is_recommended_stick",
                     "same_stick_combination"])
def update_tested_stick_canister_status(drug_canister_data: dict) -> dict:
    """
    updates requested canister status
    1. if status is pass and tested canister stick is not recommended stick then insert record of
        same stick canister in TempRecommendedStickCanisterData
    2. Update in tested canister status in TempRecommendedStickCanisterData
         (But - if pass then update status of same stick canister as pass)
    3. If status is defective and same_stick_combination(next display same stick canister record) == True
        then change order_no of pending status
    4. update or create record in canister_testing_status for pass/ fail canister
    @param drug_canister_data:
    :return:
    """
    try:
        tested_canister_status = drug_canister_data.get('status_id')
        test_canister_id = int(drug_canister_data.get('canister_id'))
        ndc = drug_canister_data.get('ndc')
        user_id = drug_canister_data.get('user_id')
        is_recommended_stick = drug_canister_data.get('is_recommended_stick')
        same_stick_combination = drug_canister_data.get('same_stick_combination')
        other_same_stick_canister_list: list = list()
        same_stick_canister_dict: dict = dict()
        pending_canister_list: list = list()
        current_canister_status: int = 0
        defective_stick_id: int = 0
        same_stick_canister_list: list = list()
        seq_tuples: list = list()
        order_no: int = 1
        temp_status: bool = False

        input_args = {'canister_id': test_canister_id,
                      'ndc': ndc,
                      'status_id': tested_canister_status,
                      'user_id': user_id,
                      'company_id': drug_canister_data['company_id'],
                      'device_id': drug_canister_data['device_id'],
                      'deactivate_canister': 0
                      }

        with db.transaction():
            # get stick of scan canister(test with other canister)
            canister_data = db_get_drug_info_by_canister(canister_id=test_canister_id)
            drug_canister_data['stick_id_list'] = [canister_data["canister_stick_id"]]
            logger.info("In update_tested_stick_canister_status: stick of scan canister: {}".format(
                canister_data["canister_stick_id"]))

            # 1. get other canister of same stick - only for not recommended_stick - test with other canister case
            # (when canister is tested with other canister)
            # (because to store data in TempRecommendedStickCanisterData if tested canister status = pass )
            if not is_recommended_stick:
                order_no = 0
                if tested_canister_status == constants.CANISTER_TESTING_PASS:
                    if canister_data["canister_stick_id"]:
                        same_stick_canister_dict = get_same_stick_canister_list(drug_canister_data=drug_canister_data)

                    # store other canister data in TempRecommendedStickCanisterData table with order_no = 0
                    for stick, canister_list in same_stick_canister_dict.items():
                        for data in canister_list:
                            temp_other_canister_test_data = {"canister_id": data['canister_id'],
                                                             "canister_stick_id": data['canister_stick_id'],
                                                             "status": tested_canister_status, "order_no": order_no,
                                                             "user_id": user_id, "recommended_stick": False}

                        other_same_stick_canister_list.append(temp_other_canister_test_data)
                        status = insert_stick_canister_data(canister_list=other_same_stick_canister_list)
                        logger.info("In update_tested_stick_canister_status: record inserted in"
                                    "TempRecommendedStickCanisterData for not recommended stick and pass status: {}"
                                     .format(status))
                elif tested_canister_status == constants.CANISTER_TESTING_FAIL:
                    tested_canister_data = [{"canister_id": test_canister_id,
                                            "canister_stick_id": canister_data['canister_stick_id'],
                                             "status": tested_canister_status, "order_no": order_no,
                                             "user_id": user_id, "recommended_stick": False}]

                    status = insert_stick_canister_data(canister_list=tested_canister_data)
                    logger.info("In update_tested_stick_canister_status: record inserted in"
                                "TempRecommendedStickCanisterData for not recommended stick and for fail status: {}"
                                 .format(status))
                else:
                    pass
            else:
                # 2. update recommended canister status in TempRecommendedStickCanisterData table
                temp_status = update_stick_canister_status(canister_data=drug_canister_data)
                logger.info("In update_tested_stick_canister_status: recommended stick canister testing status"
                            "updated in TempRecommendedStickCanisterData: {}".format(temp_status))

                if tested_canister_status == constants.CANISTER_DEFECTIVE_ID and same_stick_combination:
                    # get recommended  canister data from TempRecommendedStickCanisterData table
                    # pending_canister_data = [c1,c5,c8,c10,c2,c6,c9,c3,c7,c4] -
                    # here [(c1,c2,c3,c4) are of stick s1,(c5,c6,c7) are  of stick s2 ,(c8,c9) are of stick s3 ,(c10) are of stick s4]
                    # status of (c1,c2,c3,c4) = pass
                    pending_canister_data = get_recom_stick_canister_data()

                    for record in pending_canister_data.dicts():
                        # create list of pending canister pending_canister_list =[c8,c10,c6,c9,c7]
                        if record['status'] == constants.CANISTER_TESTING_PENDING:
                            pending_canister_list.append(record['canister_id'])

                        # if current tested canister is defective then store tested canister stick and status test_canister_id = c5 ,c5- it is defective
                        if record['status'] == constants.CANISTER_DEFECTIVE_ID and  \
                             record['canister_id'] == test_canister_id:
                            defective_stick_id = record['canister_stick_id']  # defective_stick_id = s2 (c5)
                            current_canister_status = record['status']  # current_canister_status = defective


                        # create list if any other canister which stick is same as defective canister stick in temp table
                        #  (stick = same stick of defective canister and status = pending) - same stick canister of s2 => same_stick_canister_list = [c6,c7]
                        if record['canister_stick_id'] == defective_stick_id and  \
                             record['status'] == constants.CANISTER_TESTING_PENDING:
                            same_stick_canister_list.append(record['canister_id'])

                # 3. current tested canister(c5) status == defective then change order of pending packs
                #    (next display same stick canister with pending status if available)
                if current_canister_status == constants.CANISTER_DEFECTIVE_ID and same_stick_combination:
                    # if same stick  (same as defective(S2) canister stick) is available
                    # then remove canister from pending list and set its order 1st
                    if same_stick_canister_list:
                        # same_stick_canister_list[0] = c6 remove this from pending list
                        pending_canister_list.remove(same_stick_canister_list[0])
                        # pending_canister_list = [c8,c10,c9,c7]
                        final_list = [same_stick_canister_list[0]] + pending_canister_list
                        #  final_list =    [c6] + [c8,c10,c9,c7]
                    else:
                        final_list = pending_canister_list
                    for canister_id in final_list:
                        seq_tuples.append((canister_id, order_no))
                        order_no += 1

                    if seq_tuples:
                        # update order number in table
                        # order number = [c6-0,c8-1,c10-2,c9-3,c7-4]
                        order_no_status = update_order_no_canister_list(seq_tuples=seq_tuples, canister_list=final_list)
                        logger.info("In update_tested_stick_canister_status: if defective status with"
                                    "same_stick_combination then order_no is updated in temptable: {}"
                                     .format(order_no_status))

            # 4. if tested canister status is pass -> call add_canister_testing_data
            if tested_canister_status in [constants.CANISTER_TESTING_PASS]:
                status = add_canister_testing_data(input_args)
                loaded_response = json.loads(status)
                logger.info("In update_tested_stick_canister_status: add_canister_testing_data response: {} "
                             .format(loaded_response))

            return create_response({'status': temp_status})
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_tested_stick_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_tested_stick_canister_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_tested_stick_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_tested_stick_canister_status: " + str(e))


@log_args_and_response
@validate(required_fields=['canister_id', 'company_id'])
def get_same_stick_canister_data(data: dict) -> dict:
    """
    to get other canister of same stick which is same as given canister's stick
    @param data:
    :return:
    """
    try:
        canister_list: dict = dict()
        canister_id = data.get('canister_id')
        # get same stick canister data from TempRecommendedStickCanisterData
        canister_data = get_same_stick_canister_info(canister_id=canister_id)
        logger.info("In get_same_stick_canister_data: same stick canister data:{}".format(canister_data))
        canister_list["canister_list"] = canister_data
        return create_response(canister_list)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_same_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_same_stick_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_same_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_same_stick_canister_data: " + str(e))


@log_args_and_response
@validate(required_fields=["ndc", "company_id", "system_id", "user_id"])
def generate_canister_request(data: dict) -> dict:
    """
    generate canister request to odoo
    @param data:
    @return:
    """
    ndc = data.get('ndc')
    company_id = data.get('company_id')
    system_id = data.get('system_id')
    user_id = data.get('user_id')
    canister_stick_data: list = list()
    response_data: dict = dict()
    requested_canister_count: int = 0
    response_code: int = 0  # {response_code 1 : available_canister_count >= required_canister_count ,
    # response_code 2: available_canister_count + requested_canister_count >= required_canister_count,
    # response_code 3: stick is not recommended for given ndc , 4: stick is recommended but de-active canister is not available
    #                  for recommended stick,
    # response_code 5: stick is recommended ,de-active canister is available but when we test canister it is tested,
    #                  testing status is not pass
    try:
        with db.transaction():
            # get fndc txr by ndc
            drug_info: Dict[str, Any] = get_drug_info_based_on_ndc_dao(ndc_list=[ndc])
            logger.info("In generate_canister_request: drug id for ndc: {}".format(drug_info[ndc]['id']))

            # get available canister count for given drug
            available_canister = get_available_drug_canister(company_id=company_id,
                                                             fndc=drug_info[ndc]['formatted_ndc'],
                                                             txr=drug_info[ndc]['txr'])
            logger.info("In generate_canister_request: available canister count:{} ".format(len(available_canister)))

            # get requested canister count from generate canister table for status
            # (requested status in [approved, in progress, pending, Done])
            existing_requested_canister_count = get_drug_requested_canister_count(company_id=company_id,
                                                                                  fndc=drug_info[ndc]['formatted_ndc'],
                                                                                  txr=drug_info[ndc]['txr'])
            logger.info("IN generate_canister_request: requested canister count for drug: {}"
                         .format(existing_requested_canister_count))

            # if available canister count is more than required canister count then return error message
            if len(available_canister) >= settings.REQUIRED_CANISTER_COUNT:
                return create_response({"requested_canister_count": requested_canister_count,
                                        "odoo_request_id": 0,
                                        "response_code": 1})

            # if available canister count + requested canister count is greater than required canister count
            # then no need to generate new canister
            elif len(available_canister) + existing_requested_canister_count >= settings.REQUIRED_CANISTER_COUNT:
                return create_response({"requested_canister_count": existing_requested_canister_count,
                                        "odoo_request_id": 0,  "response_code": 2})
            else:
                # find requested canister_count
                requested_canister_count = settings.REQUIRED_CANISTER_COUNT - \
                                           (len(available_canister) + existing_requested_canister_count)

            # get recommended stick for given ndc
            stick_id_list = get_drug_canister_recommendation_by_ndc_dimension(dict_drug_info=data)
            stick_id_list = json.loads(stick_id_list)["data"]["canister_stick_id_list"]
            logger.info("In generate_canister_request: recommended stick id list:{} ".format(stick_id_list))

            # get requested canister information for ndc (big canister serial number, small stick serial number and
            # drum serial number)
            if stick_id_list:
                canister_stick_data = get_requested_canister_stick_data_from_stick_id(stick_id_list=stick_id_list)

            # get drug dimension information for given drug
            ndc_data = {"drug": ndc}
            drug_data = json.loads(get_drug_dimension_by_drug(ndc_data))["data"]
            if not canister_stick_data and not drug_data:
                raise Exception("generate_canister_request: Either canister data or drug data is not available for"
                                "ndc : {}".format(ndc))
            else:
                requested_data = {"canister_stick_data": canister_stick_data,
                                  "drug_data": drug_data,
                                  "requested_canister_count": requested_canister_count}
                logger.info("In generate_canister_request: odoo requested canister data and drug_data : {}"
                             .format(requested_data))

            # //TODO: call odoo api
            # send requested canister info  and drug info to the odoo
            # if requested_canister_count != 0:
            # odoo_response = inventory_api_call(api_name=settings.CREATE_CANISTER_PACKAGES, data=requested_data)
            # odoo_response = {"odoo_request_id": odoo_response["odoo_request_id"]}
            odoo_response = {"odoo_request_id": 1}
            logger.info("In generate_canister_request: odoo response" + str(odoo_response))

            if odoo_response and odoo_response["odoo_request_id"]:
                # insert requested canister data in generate canister table
                requested_canister_data = [{
                    'company_id': company_id,
                    'system_id': system_id,
                    'created_date': get_current_date_time(),
                    'modified_date': get_current_date_time(),
                    'drug_id': drug_info[ndc]['id'],
                    'requested_canister_count': int(requested_canister_count),
                    'created_by': user_id,
                    'odoo_request_id': odoo_response["odoo_request_id"],
                    'status': constants.PENDING_ID,
                    'canister_stick_id': 1
                }]
                record_id = insert_requested_canister_data(canister_data=requested_canister_data)
                logger.info("In generate_canister_request: GenerateCanister id of requested canister " + str(record_id))
                response_data = {"requested_canister_count": requested_canister_count,
                                 "odoo_request_id": odoo_response["odoo_request_id"], "response_code": response_code}
            else:
                error(4004)
            return create_response(response_data)

    except (InternalError, IntegrityError, DataError, ValueError) as e:
        logger.error("Error in get_request_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in generate_canister_request: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise

    except InventoryBadRequestException as e:
        return error(4001, "- Error: {}.".format(e))

    except InventoryDataNotFoundException as e:
        return error(4002, "- Error: {}.".format(e))

    except InventoryBadStatusCode as e:
        return error(4004, "- Error: {}.".format(e))

    except InventoryConnectionException as e:
        return error(4003, "- Error: {}.".format(e))

    except InvalidResponseFromInventory as e:
        return error(4005, "- Error: {}.".format(e))

    except Exception as e:
        logger.error("Error in generate_canister_request {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in generate_canister_request: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in generate_canister_request: " + str(e))


@log_args_and_response
@validate(required_fields=['odoo_req_id', 'status'])
def update_requested_canister_status(canister_data: dict) -> dict:
    """
    updates requested canister status
    @param canister_data:
    :return:
    """
    try:
        # update requested canister status in Generate canister table
        status = update_odoo_requested_canister_status(canister_data=canister_data)

        return create_response({'status': status})

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_requested_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_requested_canister_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_requested_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_requested_canister_status: " + str(e))
