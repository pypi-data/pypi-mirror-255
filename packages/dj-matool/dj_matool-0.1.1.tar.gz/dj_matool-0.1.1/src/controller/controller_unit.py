import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.unit import insert_unit_data, get_units_by_type, insert_conversion_data, get_conversion_ratio


class Unit(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], insert_unit_data)
        else:
            return error(1001)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, unit_type):

        if unit_type is None:
            return error(1001, "Missing Parameter(s): unit_type.")

        args_dict = {"unit_type": unit_type}

        response = get_units_by_type(args_dict)
        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class UnitConversion(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], insert_conversion_data)
        else:
            return error(1001)

            # we have to add 'Access-Control-Allow-Origin' to the response header
            # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    @use_database(db, settings.logger)
    def GET(self, convert_from=None, convert_into=None):

        if convert_from is None or convert_into is None:
            return error(1001, "Missing Parameter(s): convert_from or convert_into.")

        args_dict = {"convert_from": convert_from, "convert_into": convert_into}

        response = get_conversion_ratio(args_dict)

        cherrypy.response.headers['Access-Control_Allow-Origin'] = "*"
        return response
