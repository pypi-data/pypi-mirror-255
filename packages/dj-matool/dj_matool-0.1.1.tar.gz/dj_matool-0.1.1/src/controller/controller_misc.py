import cgi
import os
import shutil
import tempfile

from peewee import InternalError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.utils import get_the_content_type_of_the_uploaded_file
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.dao.canister_dao import get_replenish_mini_batch_wise
from src.dao.device_manager_dao import db_get_robot_details_dao
from src.dao.file_dao import db_get_files_by_filename_dao
from src.service.pack import get_scheduled_till_date
from src.service.batch import get_system_status
from src.dao.couch_db_dao import reset_couch_db_document
from src.service.parser import Parser
from src.service.reason_codes import get_reasons
from src.service.misc import set_logged_in_user_in_couch_db_of_system, get_pre_processing_wizard_sequence_module, \
    update_pre_processing_wizard_sequence, validate_ips_username, get_printer_overhead_status, \
    create_update_system_setting, get_system_info, get_company_setting, add_company_setting, save_data, \
    update_company_setting, set_print_queue_status, get_token, get_current_user

import cherrypy


def noBodyProcess():
    cherrypy.request.process_request_body = False


cherrypy.tools.noBodyProcess = cherrypy.Tool(
    'before_request_body', noBodyProcess)


class UpdateLoggedInUser(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], set_logged_in_user_in_couch_db_of_system
            )
        else:
            return error(1001)

        return response


class PreProcessingWizardMapping(object):
    """
        Controller for `GetSequenceModule` Model
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None):
        if company_id is None or system_id is None:
            return error("Missing parameter: system_id")
        args = {"company_id": company_id, "system_id": system_id}
        response = get_pre_processing_wizard_sequence_module(data=args)
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_pre_processing_wizard_sequence)
        else:
            return error(1001)

        return response


class UploadFile(object):
    """
          @class: UploadFile
          @type: class
          @param: object
          @desc:  uploads the file in the server
    """
    exposed = True
    file_path = " "  # Variable to store the path of file uploaded manually

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    @cherrypy.tools.noBodyProcess()
    def POST(self, company_id=None, user_id=None, manual=None, system_id=None,
             fill_manual=0, **kwargs):
        if company_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or user_id.")
        # the file transfer can take a long time; by default cherrypy
        # limits responses to 300s; we increase it to 1h
        # cherrypy.response.timeout = 3600

        # convert the header keys to lower case
        lcHDRS = {}
        for key, val in cherrypy.request.headers.items():
            lcHDRS[key.lower()] = val

        # at this point we could limit the upload on content-length...
        # incomingBytes = int(lcHDRS['content-length'])
        # create our version of cgi.FieldStorage to parse the MIME encoded
        # form data where the file is contained
        formFields = myFieldStorage(fp=cherrypy.request.rfile,
                                    headers=lcHDRS,
                                    environ={'REQUEST_METHOD': 'POST'},
                                    keep_blank_values=True)

        # we now create a 2nd link to the file,  using the submitted
        # filename; if we renamed,  there would be a failure because
        # the NamedTemporaryFile,  used by our version of cgi.FieldStorage,
        # explicitly deletes the original filename

        # get the filename
        theFile = formFields['theFile']
        user_id_arg = int(user_id)
        token = get_token()
        # getting user id using session token instead of getting from front end directly
        user_details = get_current_user(token)
        user_id_token = user_details["id"]
        if user_id_arg != user_id_token:
            settings.logger.error(21010,
                                  f"user_id {user_id_arg} received from args do not match with session token user_id {user_id_token}")
            return error(21010)
        settings.logger.info("user_id received from args is validated with session token user_id")
        user_id = user_id_arg
        company_id = int(company_id)  # get it from client/front-end
        # convert the filename
        # theFile.filename = str(dt) + theFile.filename
        # we allow user to upload a file only when filename is different or previous file uploaded is un_generated
        try:
            print("upload_file: filename: "+str(theFile.filename))
            filename_without_extension = ('.').join(str(theFile.filename).split('.')[:-1])
            print("upload_file: filename_without_extension: "+str(filename_without_extension))
            filelist = db_get_files_by_filename_dao(filename_without_extension, company_id)
            for file in filelist:
                if file["status"] != settings.UNGENERATE_FILE_STATUS:
                    return error(3002)
        except InternalError as ex:
            return error(1003)

        # validate file type
        file_extension = str(theFile.filename).split('.')[-1]
        if file_extension != "txt":
            return error(5022)
        else:
            # check content type of uploaded file
            # someone can upload file with .txt, so we need to check content type also.
            file_type = get_the_content_type_of_the_uploaded_file(theFile)
            if file_type not in ["text/plain", "application/csv", "text/csv"]:
                print(f"file_type: {file_type}")
                return error(5022)

        # write the file contents in the file and store the file in appropriate
        # location
        file_path = os.path.join(settings.PENDING_FILE_PATH, str(company_id), theFile.filename)

        # creating the file and storing its content from 'the file.file'
        dir_path = os.path.join(settings.PENDING_FILE_PATH, str(company_id))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(file_path, 'wb') as f:
            shutil.copyfileobj(theFile.file, f)

        # Checking the file size available at path stored in "file_path" --> if size is not zero then we will parse else
        # return message --> file size is zero
        if os.path.getsize(file_path):
            if manual and int(manual):
                manual = True
            else:
                manual = False
            process_pharmacy_file = Parser(user_id, theFile.filename, company_id,
                                           manual, system_id=system_id, fill_manual=fill_manual)
            response = process_pharmacy_file.enqueue_task()
            return response

        else:
            return error(1001, "File has no size.")


class GetRobotInfoByRobotId(object):
    """ Controller for getting robot data by robot id """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, system_id=None, **kwargs):
        if system_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): system_id or device_id.")

        device_id = int(device_id)
        system_id = int(system_id)

        # if robot_id == 0:
        response = db_get_robot_details_dao(device_id, system_id)

        return response


class Reasons(object):
    """
    Controller for reason resource
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, reason_group=None, **kwargs):
        if reason_group is None:
            return error(1001, "Missing Parameter(s): reason_group.")

        response = get_reasons(reason_group)

        return response


class ValidateIPSUser(object):
    """
        Controller for getting all valid ips_username

    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, user_name=None, password=None, **kwargs):
        if company_id is None or user_name is None or password is None:
            return error(1001, "Missing Parameters.")

        response = validate_ips_username(company_id, user_name, password)
        print('response')
        return response


class CheckPrintCount(object):
    """
        Check  Print_count of a printer and return flag value based on print_count
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, printer_unique_code=None, system_id=None):
        if printer_unique_code is None:
            return error("Missing parameter: printer_unique_code")
        if system_id is None:
            return error("Missing parameter: system_id")

        response = get_printer_overhead_status(printer_unique_code, system_id)
        return response


class ResetCouchDBDocument(object):
    """
        To reset couch db document
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], reset_couch_db_document)
        else:
            return error(1001)

        return response


class CreateUpdateSystemSetting(object):
    """
    class to insert row in system setting table
    and if created than update respective row
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            print(kwargs["args"])
            response = validate_request_args(kwargs["args"], create_update_system_setting)
            return response

        else:
            return error(1001)


class GetAllSystemInfo(object):
    """
    class to get row in system setting table
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        response = get_system_info(company_id)
        return response


class CompanySetting(object):
    """
      @class: CompanySetting
      @type: class
      @param: object
      @desc:  gets all the settings of company
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        response = get_company_setting(company_id)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_company_setting)
        else:
            return error(1001)

        return response


class StoreExtraHours(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], save_data
            )
        else:
            return error(1001)

        return response


class UpdateCompanySetting(object):
    """
      @class: UpdateCompanySetting
      @type: class
      @param: object
      @desc: creates a record in company_setting table for given setting name and value
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_company_setting)
        else:
            return error(1001)

        return response


class SetPrintStatus(object):
    """
          @class: SetPrintStatus
          @type: class
          @param: object
          @desc:  sets given print status for given pack id
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_id=None, record_id=None, status=None,
            system_id=None, company_id=None, unique_code=None, reset_printer_count=None, dry_run=None, **kwargs):
        if pack_id is None or record_id is None or status is None or system_id is None or unique_code is None:
            return error(1001, "Missing Parameter(s): pack_id or record_id or status or system_id or unique_code.")
        response = set_print_queue_status(
            pack_id,
            record_id,
            status,
            system_id,
            company_id=company_id,
            printer_unique_code=unique_code,
            reset_printer_count=reset_printer_count
        )

        return response


class myFieldStorage(cgi.FieldStorage):
    """
          @class: myFieldStorage
          @type: function
          @param: none
          @desc:    It uses a named temporary file instead of the default
                    non-named file; keeping it visible (named),  allows us to create a
                    2nd link after the upload is done,  thus avoiding the overhead of
                    making a copy to the destination filename.
    """

    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile()


class SystemStatus(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id_list):
        if system_id_list is None and system_id_list:
            return error(1001, "Missing Parameter(s): system_id_list.")
        system_id_list = system_id_list.split(',')
        response = get_system_status(system_id_list)

        return response


class ReplenishV2(object):
    """
    Controller for replenish mini batch wise
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, device_id=None, **kwargs):
        if system_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): system_id or batch_id or device_id or batch_name.")
        data_dict = {
            'system_id': system_id,
            'device_id': device_id,
        }
        response = get_replenish_mini_batch_wise(data_dict)

        return create_response(response)


class GetScheduledTillDate(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        # check if input argument kwargs is present
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        dict_batch_info = {"company_id": company_id}
        response = get_scheduled_till_date(dict_batch_info)

        return create_response(response)
