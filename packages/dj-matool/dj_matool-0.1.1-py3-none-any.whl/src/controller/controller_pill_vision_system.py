import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.pill_vision_system import create_slot_data, get_drug_training, update_drug_training


class PVSSlot(object):
    """
          @class: PVSSlot
          @type: class
          @param: object
          @desc: Controller for Pill Vision slot data
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], create_slot_data
            )
        else:
            return error(1001)

        return response

    # @authenticate(settings.logger)


class DrugTraining(object):
    """
    Controller for DrugTraining
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_drug_training
            )
        else:
            return error(1001)

        return response


class UpdateDrugTraining(object):
    """
    Controller for updating training status for drug
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_drug_training
            )
        else:
            return error(1001)

        return response
