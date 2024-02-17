import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.ext_change_rx import ext_process_change_rx, get_ext_split, get_ext_mfd, add_rx


class ProcessChangeRx(object):
    """
    Controller to process Change Rx flow for any prescription of a patient
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], ext_process_change_rx
            )
        else:
            return error(1001, "Missing Parameter(s): args")

        return response


class ExtSplit(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, old_template=None, new_template=None, **kwargs):
        if old_template is None:
            return error(1001, 'Missing Parameter(s): old_template.')

        if new_template is None:
            return error(1001, 'Missing Parameter(s): new_template.')

        args = {"old_template": old_template,
                "new_template": new_template}
        response = get_ext_split(args)
        return response


class ExtMFD(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, old_template=None, new_template=None, **kwargs):
        if old_template is None:
            return error(1001, 'Missing Parameter(s): old_template.')

        if new_template is None:
            return error(1001, 'Missing Parameter(s): new_template.')

        args = {"old_template": old_template,
                "new_template": new_template}
        response = get_ext_mfd(args)
        return response


class AddRx(object):
    """
        Controller to process NFO flow for any prescription of a patient
        """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_rx
            )
        else:
            return error(1001, "Missing Parameter(s): args")

        return response