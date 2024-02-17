"""
 Controller for canister transfers
"""
import json
import os

import settings
from scripts.canister_transfer_as_per_canister_recommendation import canister_transfer_as_per_canister_recommendation
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from scripts.canister_transfer_from_robot_to_csr import canister_transfer_from_robot_to_csr
from scripts.canister_transfer_from_shelf_to_csr import canister_transfer_from_shelf_to_csr
from scripts.canister_transfer_to_all_empty_robot_location import canister_transfer_to_all_empty_robot_location
from src.service.canister import canister_transferred_manually, canister_transfer, \
    get_disabled_location_canister_transfers, transfer_canisters
from src.service.canister_transfers import update_transfer_status, get_update_trolley_canister_transfers, \
    get_cart_data_to_device_transfer, get_drawer_data_to_device_transfer, get_canister_data_to_device_transfer, \
    get_cart_data_from_device_transfer, get_drawer_data_from_device_transfer, get_canister_data_from_device_transfer, \
    skip_canister_transfers, canister_transfer_skip, canister_transfer_later, get_pending_canister_transfer_list


class UpdateTransferStatus(object):
    """
    Controller to update the canister transfer status
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_transfer_status
            )
        else:
            return error(1001, "args keyword not found in the input parameters.")

        return response


class UpdateTransferStatusMobileApp(object):
    """
    Controller to update the canister transfer status
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **data):

        try:

            print("UpdateTransferStatusMobileApp: ", data, type(data))
            if "company_id" in data and "device_id" in data and "system_id" in data and "batch_id" in data\
                    and "transfer_cycle_id" in data:
                args = {
                    "device_id": data["device_id"],
                    "company_id": data["company_id"],
                    "system_id": data["system_id"],
                    "batch_id": data["batch_id"],
                    "transfer_cycle_id": data["transfer_cycle_id"],
                    "from_app": json.loads(data["from_app"]) if "from_app" in data else None,
                    "status": int(data["status"]) if "status" in data else None
                }

            else:
                return error(1001, "args keyword not found in the input parameters.")

            response = update_transfer_status(args=args)

        except Exception as e:
            print("error in UpdateTransferStatusMobileApp {}".format(e))
            return error(1001)

        return response


class RecommendCanisterTransfer(object):
    """
    Controller to run recommendation for canister transfer before batch import
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            print("IS_RUNNING_RECOMMENDCANISTERTRANSFER_API 1 {}".format(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"]))
            if int(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"])  != 0:
                return error(1000, "Recommendation is already in running state for canister transfer")
            os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"]  = str(int(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"]) + 1)
            print("IS_RUNNING_RECOMMENDCANISTERTRANSFER_API 2 {}".format(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"]))
            response = validate_request_args(kwargs["args"], get_update_trolley_canister_transfers)
            return response
        else:
            return error(1001)


class CartDataToDeviceTransfer(object):
    """
    Controller to get canister transfer to trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, transfer_cycle_id=None,
            from_app=None, **kwargs):
        if device_id is None or company_id is None or transfer_cycle_id is None \
                or system_id is None or batch_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "transfer_cycle_id": transfer_cycle_id,
            "from_app": from_app
        }

        return get_cart_data_to_device_transfer(args)


class DrawerDataToDeviceTransfer(object):
    """
    Controller to get canister transfer to trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, transfer_cycle_id=None,
            trolley_serial_number=None, **kwargs):
        if device_id is None or company_id is None or transfer_cycle_id is None \
                or system_id is None or batch_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "transfer_cycle_id": transfer_cycle_id,
            "trolley_serial_number": trolley_serial_number
        }

        return get_drawer_data_to_device_transfer(args)


class CanisterDataToDeviceTransfer(object):
    """
    Controller to get canister transfer to trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, transfer_cycle_id=None,
            trolley_serial_number=None, drawer_serial_number=None, from_app=None, **kwargs):
        if device_id is None or company_id is None or transfer_cycle_id is None \
                or system_id is None or batch_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "transfer_cycle_id": transfer_cycle_id,
            "trolley_serial_number": trolley_serial_number,
            "drawer_serial_number": drawer_serial_number,
            "from_app": from_app
        }

        return get_canister_data_to_device_transfer(args)


class CartDataFromDeviceTransfer(object):
    """
    Controller to get canister transfer from trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, transfer_cycle_id=None,
             from_app=None, **kwargs):
        if device_id is None or company_id is None or transfer_cycle_id is None \
                or system_id is None or batch_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "transfer_cycle_id": transfer_cycle_id,
            "from_app": from_app
        }

        return get_cart_data_from_device_transfer(args)


class DrawerDataFromDeviceTransfer(object):
    """
    Controller to get canister transfer from trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, transfer_cycle_id=None,
            trolley_serial_number=None, **kwargs):
        if device_id is None or company_id is None or transfer_cycle_id is None \
                or system_id is None or batch_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "transfer_cycle_id": transfer_cycle_id,
            "trolley_serial_number": trolley_serial_number
        }

        return get_drawer_data_from_device_transfer(args)


class CanisterDataFromDeviceTransfer(object):
    """
    Controller to get canister transfer from trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, transfer_cycle_id=None,
            trolley_serial_number=None, drawer_serial_number=None, from_app=None, **kwargs):
        if device_id is None or company_id is None or transfer_cycle_id is None \
                or system_id is None or batch_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "transfer_cycle_id": transfer_cycle_id,
            "trolley_serial_number": trolley_serial_number,
            "drawer_serial_number": drawer_serial_number,
            "from_app": from_app
        }

        return get_canister_data_from_device_transfer(args)


class SkipCanisterTransfers(object):
    """
    This class contains methods which, when canister transfers are skipped post canister recommendation,
    CSR location gets assigned to them.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], skip_canister_transfers)
        else:
            return error(1001)

        return response


class CanisterTransferSkip(object):
    """
    This class contains methods which, when canister transfers are skipped post canister recommendation,
    CSR location gets assigned to them.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer_skip)
        else:
            return error(1001)

        return response


class CanisterTransferLater(object):
    """
    This class contains methods which, when canister transfers are skipped post canister recommendation,
    CSR location gets assigned to them.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer_later)
        else:
            return error(1001)

        return response


class GetPendingCanisterTransferList(object):
    """
    Controller to get canister transfer from trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, batch_id=None, module_id=None,
            call_from_portal=False, user_id=None, transfer_cycle_id=None, **kwargs):
        if device_id is None or company_id is None or module_id is None or transfer_cycle_id is None\
                or system_id is None or batch_id is None or user_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "batch_id": batch_id,
            "module_id": module_id,
            "call_from_portal": call_from_portal,
            "transfer_cycle_id": transfer_cycle_id,
            "user_id": user_id
        }

        return get_pending_canister_transfer_list(args)


class CanisterTransferToAllEmptyRobotLocation(object):
    """
    Controller to change pending status of mfd canisters and place them to empty location of lower drawer of home cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer_to_all_empty_robot_location)
        else:
            return error(1001)
        return response


class DisabledLocationsCanisterTransfer(object):
    """
        @class: UpdateCanisterDrawer
        @type: class
        @param: object
        @desc:  updates canister drawer
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], get_disabled_location_canister_transfers)
        else:
            return error(1001)
        return response


class CanisterTransferredManually(object):
    """
    This class contains methods which, when canister transfers are skipped post canister recommendation,
    CSR location gets assigned to them.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transferred_manually)
        else:
            return error(1001)

        return response


class CanisterTransfer(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer)
            return response
        else:
            return error(1001)


class SwapCanister(object):
    """
          @class: SwapCanister
          @type: class
          @param: object
          @desc:  swaps robot id and canister number of two canister.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], transfer_canisters
            )
        else:
            return error(1001)

        return response


class CanisterTransferFromShelfToCSR(object):
    """
    Controller to change pending status of mfd canisters and place them to empty location of lower drawer of home cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer_from_shelf_to_csr)
        else:
            return error(1001)
        return response


class CanisterTransferFromRobotToCSR(object):
    """
    Controller to change pending status of mfd canisters and place them to empty location of lower drawer of home cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer_from_robot_to_csr)
        else:
            return error(1001)
        return response


class CanisterTransferAsPerCanisterRecommendation(object):
    """
    Controller to change pending status of mfd canisters and place them to empty location of lower drawer of home cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], canister_transfer_as_per_canister_recommendation)
        else:
            return error(1001)
        return response