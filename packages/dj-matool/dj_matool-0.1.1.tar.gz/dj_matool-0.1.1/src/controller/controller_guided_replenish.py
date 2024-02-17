import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from scripts.guided_transfer_to_cart import guided_canister_transfer_to_cart
from scripts.guided_transfer_to_csr import guided_canister_transfer_to_csr
from scripts.guided_transfer_to_dd import guided_canister_transfer_to_dd
from src.service.guided_replenish import guided_cart_data_from_device_transfer, guided_drawer_data_from_device_transfer, \
    guided_canister_data_from_device_transfer, guided_cart_data_to_device_transfer, \
    guided_drawer_data_to_device_transfer, guided_canister_data_to_device_transfer, recommendguidedtx, \
    get_batch_guided_tx_drugs, skip_guided_tx_canister, update_guided_cycle_status, guided_transfer_skip, \
    get_guided_transfer_pending_canisters, guided_transfer_later


class GuidedTxDrugs(object):
    """
        This class contains methods to Get transfer data from CanisterTransferTracker Table.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, filter_fields=None, guided_tx_cycle_id=None, system_id=None, company_id=None, sort_fields=None,
            **kwargs):

        if guided_tx_cycle_id is None or system_id is None or company_id is None:
            return error(1001, "Missing Parameters.")
        dict_batch_info = {"guided_tx_cycle_id": guided_tx_cycle_id,
                           "system_id": system_id,
                           "company_id": company_id}
        if sort_fields:
            dict_batch_info["sort_fields"] = json.loads(sort_fields)
        if filter_fields:
            dict_batch_info["filter_fields"] = json.loads(filter_fields)

        response = get_batch_guided_tx_drugs(dict_batch_info)

        return response


class RecommendGuidedTx(object):
    """
        Controller to recommend guided transfers
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], recommendguidedtx)
        else:
            return error(1001)
        return response


class GuidedTxReplenishSkip(object):
    """
    Controller to skip the canister in Guided TX flow
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], skip_guided_tx_canister
            )
        else:
            return error(1001, "args keyword not found in the input parameters.")

        return response


class UpdateGuidedTxStatus(object):
    """
    Controller to update the cycle status is meta in Guided TX flow
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_guided_cycle_status
            )
        else:
            return error(1001, "args keyword not found in the input parameters.")

        return response


class UpdateGuidedTxStatusMobileApp(object):
    """
    Controller to update the cycle status is meta in Guided TX flow
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self,  **kwargs):

        try:
            if "module_id" in kwargs and "company_id" in kwargs:
                args = {
                    "module_id": int(kwargs["module_id"]),
                    "company_id": kwargs["company_id"],
                    "batch_id": int(kwargs["batch_id"]),
                    "guided_tx_cycle_id": int(kwargs["guided_tx_cycle_id"]),
                    "user_id": kwargs["user_id"] if "user_id" in kwargs else None,
                    "from_app": json.loads(kwargs["from_app"]) if "from_app" in kwargs else None,
                    "status": json.loads(kwargs["status"]) if "status" in kwargs else None,
                    "transfer_done_from_portal": json.loads(
                        kwargs["transfer_done_from_portal"]) if "transfer_done_from_portal" in kwargs else None
                }
            else:
                return error(1001, "args keyword not found in the input parameters.")

            response = update_guided_cycle_status(args=args)

        except Exception as e:
            print("Error in UpdateGuidedTxStatusMobileApp {}".format(e))
            return error(1001, e)

        return response


class GuidedCartDataFromDeviceTransfer(object):
    """
    Controller to get cart data for guided transfer from the given device.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, guided_tx_cycle_id=None, user_id=None,
            from_app=None, **kwargs):
        if device_id is None or company_id is None or guided_tx_cycle_id is None \
                or system_id is None:
            return error(1001, "Missing parameters.: device_id or system_id or guided_tx_cycle_id or "
                               "company_id")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "guided_tx_cycle_id": guided_tx_cycle_id,
            "user_id": user_id,
            "from_app": from_app
        }

        return guided_cart_data_from_device_transfer(args)


class GuidedDrawerDataFromDeviceTransfer(object):
    """
    Controller to get drawer data for guided transfer from the given device.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, guided_tx_cycle_id=None,
            trolley_serial_number=None, user_id=None, **kwargs):
        if device_id is None or company_id is None or guided_tx_cycle_id is None \
                or system_id is None or trolley_serial_number is None:
            return error(1001, "Missing parameters.: device_id or system_id or guided_tx_cycle_id or "
                               "company_id or trolley_serial_number")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "guided_tx_cycle_id": guided_tx_cycle_id,
            "trolley_serial_number": trolley_serial_number,
            "user_id": user_id
        }

        return guided_drawer_data_from_device_transfer(args)


class GuidedCanisterDataFromDeviceTransfer(object):
    """
    Controller to get cart data for guided transfer from the given device.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, guided_tx_cycle_id=None,
            trolley_serial_number=None, drawer_serial_number=None, user_id=None, from_app=None, **kwargs):
        if device_id is None or company_id is None or guided_tx_cycle_id is None or system_id is None \
                or drawer_serial_number is None:
            return error(1001, "Missing parameters.: device_id or system_id or guided_tx_cycle_id or "
                               "company_id or trolley_serial_number or drawer_serial_number")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "guided_tx_cycle_id": guided_tx_cycle_id,
            "trolley_serial_number": trolley_serial_number,
            "drawer_serial_number": drawer_serial_number,
            "user_id": user_id,
            "from_app": from_app
        }

        return guided_canister_data_from_device_transfer(args)


class GuidedCartDataToDeviceTransfer(object):
    """
    Controller to get cart data for guided transfer to the given device.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, guided_tx_cycle_id=None, system_id=None,
            device_type=None, user_id=None, from_app=None, **kwargs):
        if device_id is None or company_id is None or guided_tx_cycle_id is None:
            return error(1001, "Missing parameters.: device_id or guided_tx_cycle_id or company_id")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "guided_tx_cycle_id": guided_tx_cycle_id,
            "device_type": device_type,
            "user_id": user_id,
            "from_app": from_app
        }

        return guided_cart_data_to_device_transfer(args)


class GuidedDrawerDataToDeviceTransfer(object):
    """
    Controller to get drawer data for guided transfer to the given device.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, guided_tx_cycle_id=None, trolley_serial_number=None,
            system_id=None, device_type=None, user_id=None, **kwargs):
        if device_id is None or company_id is None or guided_tx_cycle_id is None or trolley_serial_number is None:
            return error(1001,
                         "Missing parameters.: device_id or guided_tx_cycle_id or company_id or trolley_serial_number")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "guided_tx_cycle_id": guided_tx_cycle_id,
            "trolley_serial_number": trolley_serial_number,
            "device_type": device_type,
            "user_id": user_id
        }

        return guided_drawer_data_to_device_transfer(args)


class GuidedCanisterDataToDeviceTransfer(object):
    """
    Controller to get canister data for guided transfer to the given device.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, guided_tx_cycle_id=None, trolley_serial_number=None,
            drawer_serial_number=None, system_id=None, device_type=None, user_id=None,
            from_app=None, **kwargs):
        if device_id is None or company_id is None or guided_tx_cycle_id is None \
                or drawer_serial_number is None:
            return error(1001, "Missing parameters.: device_id or guided_tx_cycle_id or "
                               "company_id or drawer_serial_number")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "guided_tx_cycle_id": guided_tx_cycle_id,
            "trolley_serial_number": trolley_serial_number,
            "drawer_serial_number": drawer_serial_number,
            "device_type": device_type,
            "user_id": user_id,
            "from_app": from_app
        }

        return guided_canister_data_to_device_transfer(args)


class GuidedTransferSkip(object):
    """
    This class contains methods which, when canister transfers are skipped post canister recommendation,
    CSR location gets assigned to them.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], guided_transfer_skip)
        else:
            return error(1001)

        return response


class GetGuidedTransferPendingCanisters(object):
    """
    Controller to get canister transfer from trolley data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, system_id=None, module_id=None,
            call_from_portal=False, user_id=None, guided_meta_id=None, **kwargs):
        if device_id is None or company_id is None or module_id is None or guided_meta_id is None\
                or system_id is None or user_id is None:
            return error(1001, "Missing parameters.")

        args = {
            "device_id": device_id,
            "company_id": company_id,
            "system_id": system_id,
            "module_id": module_id,
            "call_from_portal": call_from_portal,
            "guided_meta_id": guided_meta_id,
            "user_id": user_id
        }

        return get_guided_transfer_pending_canisters(args)


class GuidedTransferToDD(object):
    """
    Controller to transfer mfd canister from cart to robot
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], guided_canister_transfer_to_dd)
        else:
            return error(1001)
        return response


class GuidedTransferToCSR(object):
    """
    Controller to transfer mfd canister from cart to robot
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], guided_canister_transfer_to_csr)
        else:
            return error(1001)
        return response


class GuidedTransferToCart(object):
    """
    Controller to transfer mfd canister from cart to robot
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], guided_canister_transfer_to_cart)
        else:
            return error(1001)
        return response


class GuidedTransferLater(object):
    """
    This class contains methods which, when canister transfers are skipped post canister recommendation,
    CSR location gets assigned to them.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], guided_transfer_later)
        else:
            return error(1001)

        return response
