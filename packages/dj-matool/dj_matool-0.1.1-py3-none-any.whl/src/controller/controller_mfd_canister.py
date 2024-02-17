import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import (use_database)
from dosepack.utilities.validate_auth_token import (authenticate)
from dosepack.validation.validate import (validate_request_args)
from src.service.mfd_canister import (get_canister_transfer, get_mfd_trolley_data, get_mfd_canister_details,
                                      add_mfd_canister, get_rts_canister_data, mark_canister_rts_done,
                                      get_unique_mfd_rts_canister_filters, get_mfd_empty_canister_data,
                                      get_unique_mfd_canister_master_filters, get_rts_drug_data,
                                      get_mfd_misplaced_canisters, get_mfd_empty_canister_cart, get_mfd_empty_canister_drawer,
                                      get_cart_rts_canister_data, get_cart_rts_drug_data, get_mfd_mvs_canister_details,
                                      activate_mfd_canister, mark_canister_found, update_mfd_canister_to_misplaced)


class AddMFDCanister(object):
    """
    @class: AddDataInMFDCanisterMaster
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_mfd_canister)
        else:
            return error(1001)

        return response


class MFDCartDataToDeviceTransfer(object):
    """
    @class: MFDCartDataToDeviceTransfer
    @desc: To get mfd canister transfer information for transfer to robot flow(cart level info)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id, system_id, device_id, batch_id, trolley_id=None, drawer_id=None, on_start=False,
            user_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'batch_id': batch_id,
                'trolley_id': trolley_id,
                'drawer_id': drawer_id,
                'user_id': user_id,
                'on_start': on_start}

        response = get_mfd_trolley_data(args)

        return response


class MFDDrawerDataToDeviceTransfer(object):
    """
    @class: MFDDrawerDataToDeviceTransfer
    @desc: To get mfd canister transfer information for transfer to robot flow(drawer level info)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id, system_id, device_id, batch_id, trolley_serial_number=None, drawer_serial_number=None,
            on_start=False, user_id=None, scanned_drawer_serial_number=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'batch_id': batch_id,
                'drawer_serial_number': drawer_serial_number,
                'user_id': user_id,
                'trolley_serial_number': trolley_serial_number,
                'scanned_drawer_serial_number': scanned_drawer_serial_number,
                'on_start': on_start}

        response = get_mfd_trolley_data(args)

        return response


class MFDCanisterDataToDeviceTransfer(object):
    """
    @class: MFDCanisterDataToDeviceTransfer
    @desc: To get mfd canister transfer information for transfer to robot flow(canister level info)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id, system_id, device_id, batch_id, trolley_id=None, drawer_id=None, on_start=False,
            user_id=None, trolley_serial_number=None, drawer_serial_number=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'batch_id': batch_id,
                'trolley_id': trolley_id,
                'drawer_id': drawer_id,
                'user_id': user_id,
                'trolley_serial_number': trolley_serial_number,
                'drawer_serial_number': drawer_serial_number,
                'on_start': on_start}

        response = get_mfd_trolley_data(args)

        return response


class GetMFDCanisterDetails(object):
    """
    @class: GetMFDCanisterDetails
    @desc: Get mfd canister data from mfd canister id
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, mfd_canister_id=None, pack_id=None, mvs_filling=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id,
                'mfd_canister_id': mfd_canister_id,
                'pack_id': pack_id,
                'mvs_filling': mvs_filling}

        response = get_mfd_canister_details(args)

        return response


class GetMFDCanisters(object):
    """
    @class: GetMFDCanisters
    @desc: Get the mfd canister's data for main screen(mfd canister master)
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filter_fields=None, sort_fields=None, paginate=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if paginate:
            paginate = json.loads(paginate)

        if sort_fields:
            sort_fields = json.loads(sort_fields)

        if filter_fields:
            filter_fields = json.loads(filter_fields)

        args = {'company_id': company_id,
                'filter_fields': filter_fields,
                'sort_fields': sort_fields,
                'paginate': paginate}

        response = get_canister_transfer(args)

        return response


class MFDRTSCanister(object):
    """
    controller to get rts canister and mark rts canister done(GET API is currently not in use as it's merged in mfd
    canister master screen)
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, filter_fields=None, sort_fields=None, paginate=None, robot_filters=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        try:

            if paginate is not None:
                paginate = json.loads(paginate)
            if filter_fields:
                filter_fields = json.loads(filter_fields)
            if sort_fields:
                sort_fields = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        if robot_filters:
            filter_fields = eval(robot_filters)

        args = {'company_id': company_id,
                'filter_fields': filter_fields,
                'sort_fields': sort_fields,
                'paginate': paginate}

        response = get_rts_canister_data(args)

        return response

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mark_canister_rts_done)
        else:
            return error(1001)

        return response


class MFDRTSFilters(object):
    """
    controller to get filters for rts canister
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id}

        response = get_unique_mfd_rts_canister_filters(args)

        return response


class MFDCanisterMasterFilters(object):
    """
    controller to get filters for rts canister
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id}

        response = get_unique_mfd_canister_master_filters(args)

        return response


class MFDEmptyCanisterData(object):
    """
    @class: MFDEmptyCanisterData
    @desc: To get mfd canister transfer information for from robot to trolley(canister level info)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, device_id=None, batch_id=None, user_id=None, current_module=None,
            on_start=False, trolley_serial_number=None, drawer_serial_number=None, drawer_scanned=None, **kwargs):
        if company_id is None or system_id is None or device_id is None or batch_id is None or user_id is None or \
                current_module is None:
            return error(1001, "Missing Parameter(s): company_id or system_id or device_id or batch_id or user_id or "
                               "current_module.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'batch_id': batch_id,
                'user_id': user_id,
                'on_start': on_start,
                'trolley_serial_number': trolley_serial_number,
                'drawer_serial_number': drawer_serial_number,
                'drawer_scanned': drawer_scanned,
                'current_module': current_module}

        response = get_mfd_empty_canister_data(args)

        return response


class MFDRTSDrug(object):
    """
    controller to get rts drug
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id}

        response = get_rts_drug_data(args)

        return response


class MFDMisplacedCanisters(object):
    """
    @class: MFDMisplacedCanisters
    @desc: To get misplaced mfd canister data based on module(transfer to or from robot)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id, system_id, device_id, batch_id, module_id, trolley_serial_number=None,
            drawer_serial_number=None, misplaced_canister_count=None, **kwargs):
        if company_id is None or system_id is None or device_id is None or batch_id is None or module_id is None:
            return error(1001, "Missing Parameter(s): company_id or system_id or device_id or batch_id or module_id.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'batch_id': batch_id,
                'module_id': module_id,
                'trolley_serial_number': trolley_serial_number,
                'drawer_serial_number': drawer_serial_number,
                'misplaced_canister_count': misplaced_canister_count,
                }

        response = get_mfd_misplaced_canisters(args)

        return response


class MFDEmptyCanisterCart(object):
    """
    @class: MFDEmptyCanisterData
    @desc: To get mfd canister transfer information for from robot to trolley(cart level info)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, device_id=None, user_id=None, batch_id=None, on_start=False,
            **kwargs):
        if company_id is None or system_id is None or device_id is None or user_id is None or batch_id is None:
            return error(1001, "Missing Parameter(s): company_id or system_id or device_id or user_id or")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'user_id': user_id,
                'batch_id': batch_id,
                'on_start': on_start, }

        response = get_mfd_empty_canister_cart(args)

        return response


class MFDEmptyCanisterDrawer(object):
    """
    @class: MFDEmptyCanisterData
    @desc: To get mfd canister transfer information for from robot to trolley(drawer level info)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, device_id=None, batch_id=None, user_id=None, current_module=None,
            trolley_serial_number=None, **kwargs):
        if company_id is None or system_id is None or device_id is None or batch_id is None or user_id is None or \
                current_module is None or trolley_serial_number is None:
            return error(1001, "Missing Parameter(s): company_id or system_id or device_id or batch_id or user_id or "
                               "current_module or trolley_serial_number.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'device_id': device_id,
                'batch_id': batch_id,
                'user_id': user_id,
                'trolley_serial_number': trolley_serial_number,
                'current_module': current_module}

        response = get_mfd_empty_canister_drawer(args)

        return response


class MFDCartRTSCanister(object):
    """
    controller to get rts canister for particular cart
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, cart_serial_number=None, batch_id=None, filter_fields=None,
            sort_fields=None, paginate=None, **kwargs):
        if company_id is None or system_id is None or cart_serial_number is None or batch_id is None:
            return error(1001, "Missing Parameter(s): company_id, system_id or cart_serial_number or batch_id.")

        if paginate:
            paginate = json.loads(paginate)

        if sort_fields:
            sort_fields = json.loads(sort_fields)

        if filter_fields:
            filter_fields = json.loads(filter_fields)

        args = {'company_id': company_id,
                'system_id': system_id,
                'cart_serial_number': cart_serial_number,
                'batch_id': batch_id,
                'filter_fields': filter_fields,
                'sort_fields': sort_fields,
                'paginate': paginate}

        response = get_cart_rts_canister_data(args)

        return response


class MFDCartRTSDrug(object):
    """
    controller to get rts drug data for particular cart
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, cart_serial_number=None, batch_id=None, **kwargs):
        if company_id is None or system_id is None or cart_serial_number is None or batch_id is None:
            return error(1001, "Missing Parameter(s): company_id, system_id or cart_serial_number or batch_id.")

        args = {'company_id': company_id,
                'system_id': system_id,
                'cart_serial_number': cart_serial_number,
                'batch_id': batch_id,
                }

        response = get_cart_rts_drug_data(args)

        return response


class MFDMVSCanisterDetails(object):
    """
    @class:
    @desc: Get mfd canister data from mfd canister id for mvs/pfw use
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, mfd_canister_id=None, pack_id=None, mvs_filling=None, **kwargs):
        if company_id is None or mfd_canister_id is None or pack_id is None:
            return error(1001, "Missing Parameter(s): company_id, mfd_canister_id or pack_id.")

        args = {'company_id': company_id,
                'mfd_canister_id': mfd_canister_id,
                'pack_id': pack_id,
                'mvs_filling': mvs_filling}

        response = get_mfd_mvs_canister_details(args)

        return response


class ActivateMFDCanister(object):
    """
    @class: ActivateMFDCanister
    @desc: To activate mfd canister
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], activate_mfd_canister)
        else:
            return error(1001)

        return response


class MfdCanisterFound(object):
    """
    @class: ActivateMFDCanister
    @desc: To mark misplaced mfd canister as found
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mark_canister_found)
        else:
            return error(1001)

        return response


class MfdCanisterMisplaced(object):
    """
    @class: ActivateMFDCanister
    @desc: To mark the mfd canister misplaced
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_mfd_canister_to_misplaced)
        else:
            return error(1001)

        return response
