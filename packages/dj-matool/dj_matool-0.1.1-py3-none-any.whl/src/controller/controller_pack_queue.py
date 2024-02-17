import json
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.utils import convert_dob_date_to_sql_date, is_date
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src import constants
from src.service.pack_queue import get_dashlet_data


class GetDashletData(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, **kwargs):
        args = {
            "system_id": system_id,
            "company_id": company_id
        }
        response = get_dashlet_data(args)
        return response