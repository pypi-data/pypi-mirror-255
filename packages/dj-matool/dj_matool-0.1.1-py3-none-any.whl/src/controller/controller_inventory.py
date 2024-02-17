import cherrypy
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.inventory import insert_drug_lot_data, get_lot_information, update_drug_lot_data, \
    get_drug_bottle_label, update_lot_recall_status, update_pills_quantity_in_bottle_by_id, \
    check_details_for_lot_number_and_drug_existence, delete_drug_bottle, find_similar_configuration_canister_by_drug_id


class DrugLotData(object):
    """
        @class: DrugLotData
        @type: class
        @param: object
        @desc: Get drug lot data
       """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], insert_drug_lot_data)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, drug_id=None, lot_number=None, **kwargs):

        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        required_dict = {"company_id": company_id, "lot_number": lot_number, "drug_id": drug_id}

        response = get_lot_information(required_dict)
        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class UpdateDrugLotData(object):
    """
        @class: UpdateDrugLotData
        @type: class
        @param: object
        @desc:  update drug lot data
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_drug_lot_data)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class DrugBottleLabel(object):
    """
        @class: DrugBottleLabel
        @type: class
        @param: object
        @desc: Generates drug bottle label file and returns file name
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], get_drug_bottle_label)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response


class DrugLotRecall(object):
    """
        @class: DrugLotRecall
        @type: class
        @param: object
        @desc: POST: Update the recall status of a given lot id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_lot_recall_status)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response


class UpdateDrugBottleQuantityById(object):
    """
        @class: UpdateDrugBottleQuantityById
        @type: class
        @param: object
        @desc: POST: Update drug bottle quantity by id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_pills_quantity_in_bottle_by_id)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response


class SearchDrugLotSerialData(object):
    """

    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, lot_number=None, ndc=None, serial_number=None):
        if lot_number is None or ndc is None:
            return error(1001, "Missing Parameter(s): lot_number or ndc.")
        else:
            required_dict = {"lot_number": lot_number, "ndc": ndc, "serial_number": serial_number}

            response = check_details_for_lot_number_and_drug_existence(required_dict)

        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class DeleteDrugBottle(object):
    """

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], delete_drug_bottle)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response


class FindSuitableDrugs(object):
    """

    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, drug_id=None, company_id=None):
        if drug_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): drug_id or company_id.")

        required_dict = {"drug_id": drug_id, "company_id": company_id}

        response = find_similar_configuration_canister_by_drug_id(required_dict)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response
