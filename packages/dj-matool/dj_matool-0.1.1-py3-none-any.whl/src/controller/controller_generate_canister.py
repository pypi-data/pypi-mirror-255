"""

    @file: controller_generate_canister.py
    @type: file
    @desc: Provides Controller for Generate Canister
"""
import json
from dosepack.utilities.manage_db_connection import use_database
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.validation.validate import validate_request_args
from dosepack.utilities.validate_auth_token import authenticate
from src.service.generate_canister import get_canister_request_list, update_requested_canister_status, \
    get_request_canister_status_data, get_replenish_test_data, \
    store_recommend_stick_canister, get_recommended_stick_canister, \
    update_tested_stick_canister_status, get_same_stick_canister_data, generate_canister_request
import settings


class CanisterRequestList(object):
    """Controller for `CanisterRequestList` Model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id")
        args = {"company_id": company_id}
        try:
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_canister_request_list(args)
        except Exception as ex:
            response = json.dumps({"error": str(ex), "status": settings.FAILURE})
        return response


class CanisterRequestStatusData(object):
    """Controller for `CanisterRequestStatusData` Model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, ndc=None, filters=None, **kwargs):
        if company_id is None or ndc is None:
            return error(1001, "Missing Parameter(s): company_id or ndc.")
        canister_request_data = {"company_id": company_id, "ndc": ndc}
        try:
            if filters:
                canister_request_data["filter_fields"] = json.loads(filters)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_request_canister_status_data(canister_request_data)
        except Exception as ex:
            response = json.dumps({"error": str(ex), "status": settings.FAILURE})
        return response


class GetReplenishTestData(object):
    """Controller for `GetReplenishTestData` Model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, unique_drug_id=None, canister_id=None, **kwargs):
        if unique_drug_id is None or canister_id is None:
            return error(1001, "Missing Parameter(s): unique_drug_id or canister_id")

        args = {"unique_drug_id": unique_drug_id, "canister_id": canister_id}

        response = get_replenish_test_data(args)

        return response


class RecommendStickCanister(object):
    """Controller for `RecommendStickCanister` Model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, user_id=None, ndc=None, **kwargs):
        if company_id is None or user_id is None or ndc is None:
            return error(1001, "Missing Parameter(s): company_id or user_id or ndc or txr.")
        try:
            args = {"company_id": company_id, "user_id": user_id,
                    "ndc": ndc}

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_recommended_stick_canister(args)
        except Exception as ex:
            response = json.dumps({"error": str(ex), "status": settings.FAILURE})
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], store_recommend_stick_canister)
            print("response of store_recommend_stick_canister ", response)
            return response

        else:
            return error(1001)


class UpdateTestedStickCanisterStatus(object):
    """Controller for 'UpdateTestedStickCanisterStatus' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_tested_stick_canister_status)
            return response
        else:
            return error(1001)


class GetSameStickCanister(object):
    """Controller for 'GetSameStickCanister' model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, canister_id=None, **kwargs):
        if company_id is None or canister_id is None:
            return error(1001, "Missing Parameter(s):company_id or canister_id ")
        args = {"company_id": company_id, "canister_id": canister_id}
        try:
            response = get_same_stick_canister_data(args)
        except Exception as ex:
            response = json.dumps({"error": str(ex), "status": settings.FAILURE})
        return response


class GenerateCanisterRequest(object):
    """Controller for `GenerateCanisterRequest` Model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], generate_canister_request)
            return response
        else:
            return error(1001)


class UpdateRequestedCanisterStatus(object):
    """Controller for 'UpdateRequestedCanisterStatus' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_requested_canister_status)
            return response
        else:
            return error(1001)
