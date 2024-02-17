import json

import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.manual_packing import getPatients, getPatientsList, getpacks, getFacilities, getFacilitiesList
from src.service.pack import get_pack_count_for_canister_skip, get_unscheduled_packs, \
    get_manual_packs_with_optimised_manual_fill, get_packs, get_packs_of_facility, get_incomplete_packs, \
    get_pack_details, get_pack_details_v2, set_status, get_pending_packs_with_past_delivery_date, \
    validate_robot_partially_filled_pack, get_pack_count_for_auto_pilot, get_pack_history_data, get_manual_packs, \
    get_similar_manual_packs, transfer_manual_packs, get_pack_drugs, unassign_packs, get_similar_packs_manual_assign, \
    create_overloadedpack_data, set_fill_time, partially_filled_pack, max_order, generate_test_packs, \
    get_all_unassociated_packs, map_user_pack, get_pack_user_map, get_user_pack_stats, get_manual_count_stats, \
    get_slot_details_for_vision_system, get_slots_for_user_station, get_slots_for_label_printing, prepare_label_data, \
    populate_slot_transaction, get_pack_data, get_user_assigned_packs, get_user_assigned_pack_count, \
    getUserWiesPacksCount, get_pack_grid_data, get_new_packs_change_rx, get_drugs_of_reuse_pack, verify_pack, \
    stop_pack_filling, get_packs_info, reuse_pack, recommend_reuse_pack, discard_pack_drug, \
    get_reuse_in_progress_pack, get_reuse_pack_drug_data, reseal_pack, rts_of_pack, get_vial_label, \
    epbm_general_api, get_vial_list, master_search, person_master_search
from src.service.test_pack import populate_pack_generator
from src.service.verification import get_all_unassociated_packs


class GetPackCountForSkipCanister(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, canister_id=None, device_id=None, system_id=None, **kwargs):
        try:
            if company_id is None or canister_id is None or device_id is None or system_id is None:
                return error(1001, "Missing Parameter(s): company_id or canister_id or device_id.")
            response = get_pack_count_for_canister_skip(company_id=company_id, system_id=system_id, canister_id=canister_id, device_id=device_id, batch_id=batch_id)
            return create_response(response)

        except Exception as e:
            print("Error in GetPackCountForSkipCanister {}".format(e))
            return error(0, e)


class GetUnscheduledPacks(object):
    """ Returns different mini batches"""
    exposed = True

    # Note: GET is now moved to POST request as pack_list can be very long and may truncate in url
    # POST should be used, Remove GET when POST is in use.
    # TODO Remove GET implementation

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_unscheduled_packs
            )
        else:
            return error(1001)
        return response


class ManualPacksWithOptimisedManualFill(object):
    """ Returns manual packs and canister packs based on
    canister drug percentage against given threshold """
    exposed = True

    # Note: GET is now moved to POST request as pack_list can be very long and may truncate in url
    # POST should be used, Remove GET when POST is in use.
    # TODO Remove GET implementation
    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_manual_packs_with_optimised_manual_fill
            )
        else:
            return error(1001)

        return response


class GetPacks(object):
    """
    @class: GetPacks
    @type: class
    @param: object
    @desc: It returns all the packs generated.
           The packs can also be filtered based on
           the start date and the end date and also
           the different status of the packs.

    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, date_from=None, date_to=None,
            status=None, system_id=None, filters=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if date_from is None:
            date_from = settings.DEFAULT_START_DATE
        if date_to is None:
            date_to = settings.DEFAULT_TO_DATE
        if status is None:
            status = settings.DEFAULT_PACK_STATUS

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "pack_status": status,
            "company_id": company_id,
            "system_id": system_id
        }
        try:
            if filters:
                args["filter_fields"] = json.loads(filters)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        if "all_flag" in kwargs and int(kwargs['all_flag']):
            args['all_flag'] = True
        else:
            args['all_flag'] = False
        if 'schedule_start_date' in kwargs and 'schedule_end_date' in kwargs:
            args['schedule_start_date'] = kwargs['schedule_start_date']
            args['schedule_end_date'] = kwargs['schedule_end_date']
        response = get_packs(args)

        return response


class GetPacksForFacility(object):
    """
    @class: GetPacksForFacility
    @type: class
    @param: object
    @desc: It returns pending packs of a facility.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, date_from=None, date_to=None,
            status=None, system_id=None, filters=None, facility_id=None, all_flag=None, **kwargs):
        if company_id is None or facility_id is None:
            return error(1001, "Missing Parameter(s): company_id or facility_id.")

        if date_from is None:
            date_from = settings.DEFAULT_START_DATE
        if date_to is None:
            date_to = settings.DEFAULT_TO_DATE
        if status is None:
            status = settings.PACK_STATUS["Pending"]

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "pack_status": status,
            "company_id": company_id,
            "system_id": system_id,
            "facility_id": facility_id
        }
        try:
            if filters:
                args["filter_fields"] = json.loads(filters)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        if all_flag is not None and int(all_flag):
            args['all_flag'] = True
        else:
            args['all_flag'] = False
        response = get_packs_of_facility(args)

        return response


class GetIncompletePacks(object):
    """
    @type: class
    @param: object
    @desc: Retrieves all the incomplete packs for a
           given system between date range.

    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, date_from=None, date_to=None, system_id=None, **kwargs):
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")
        if date_from is None:
            date_from = settings.DEFAULT_START_DATE
        if date_to is None:
            date_to = settings.DEFAULT_TO_DATE

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "system_id": system_id
        }
        response = get_incomplete_packs(args)

        return response


class GetPackDetails(object):
    """
    @class: GetPackDetails
    @type: class
    @param: object
    @desc: Get the pack details for the given pack id and system id.

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, device_id=None, non_fractional=None,
            company_id=None, mft_slots=None, print_status=None, user_id=None, module_id=None, **kwargs):
        # check if pack id is present

        if pack_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): pack_id or company_id.")
        if device_id:
            device_id = int(device_id)
        if non_fractional is None:
            non_fractional = 0
        if module_id:
            module_id = int(module_id)
        non_fractional = bool(int(non_fractional))
        if mft_slots is None:
            mft_slots = 0
        mft_slots = bool(int(mft_slots))  # expected values 0,1
        print_status = bool(int(print_status or 0))
        args = {
            "pack_id": pack_id,
            "device_id": device_id,
            "non_fractional": non_fractional,
            "company_id": company_id,
            "mft_slots": mft_slots,
            "print_status": print_status,
            "user_id": user_id,
            "module_id": module_id
        }
        response = get_pack_details(args)

        return response


class GetPackDetailsV2(object):
    """
    @class: GetPackDetails
    @type: class
    @param: object
    @desc: Get the pack details for the given pack id and system id.

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, device_id=None, non_fractional=None,
            company_id=None, mft_slots=None, print_status=None, exclude_pack_ids=None, **kwargs):
        # check if pack id is present

        if pack_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): pack_id or company_id.")
        if device_id:
            device_id = int(device_id)
        if non_fractional is None:
            non_fractional = 0
        non_fractional = bool(int(non_fractional))
        if mft_slots is None:
            mft_slots = 0
        mft_slots = bool(int(mft_slots))  # expected values 0,1
        print_status = bool(int(print_status or 0))
        if exclude_pack_ids:
            exclude_pack_ids = eval(exclude_pack_ids)
            # exclude_pack_ids = json.loads(exclude_pack_ids)
        args = {
            "pack_id": pack_id,
            "device_id": device_id,
            "non_fractional": non_fractional,
            "company_id": company_id,
            "mft_slots": mft_slots,
            "print_status": print_status,
            "exclude_pack_ids": exclude_pack_ids,
        }
        response = get_pack_details_v2(args)

        return response


class SetPackCrmStatus(object):
    """
    @class: SetPackCrmStatus
    @type: class
    @param: object
    @desc: sets the status of the given pack id according to system id.

    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_id=None, status=None, system_id=None,
            company_id=None, user_id=None, **kwargs):
        # check if pack id, status, systemid is present
        if pack_id is None or status is None or user_id is None:
            return error(1001, "Missing Parameter(s): pack_id or status or user_id.")

        args = {
            "pack_id": pack_id,
            "status": status,
            "user_id": int(user_id),
            "system_id": system_id,
            "company_id": company_id
        }
        response = set_status(args)

        return response


class SetStatus(object):
    """
    @class: SetStatus
    @type: class
    @param: object
    @desc: Set the status for the given pack id.

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], set_status
            )
        else:
            return error(1001)
        return response


class StopPackFilling(object):

    exposed = True

    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], stop_pack_filling
            )
        else:
            return error(1001)
        return response


class PendingPacksWithPastDeliveryDates(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, time_zone=None):
        if company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): company_id or time_zone.")
        return get_pending_packs_with_past_delivery_date(company_id=company_id, time_zone=time_zone)


class ValidateRobotFillPack(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, pack_ids=None, user_id=None, **kwargs):
        if company_id is None or pack_ids is None and user_id is None:
            return error(1001, "Missing Parameter(s): company_id or pack_ids or user_id.")

        args = {
            "company_id": company_id,
            "pack_display_ids": pack_ids,
            "user_id": user_id
        }
        response = validate_robot_partially_filled_pack(args)

        return response


class PackCountForAutoPilot(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, **kwargs):

        # check if input argument kwargs is present
        if system_id is None or company_id is None:
            return error(1001, "Missing Parameter(s)")

        dict_batch_info = {"system_id": system_id, "company_id": company_id}
        response = get_pack_count_for_auto_pilot(dict_batch_info=dict_batch_info)

        return response


class GetPackHistory(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, **kwargs):
        # check if input argument kwargs is present
        if pack_id is None:
            return error(1001, "Missing Parameter(s): pack_id.")

        dict_patient_info = {"pack_id": pack_id}
        response = get_pack_history_data(dict_patient_info)

        return response


class GetManualPacks(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filter_fields=None, paginate=None, sort_fields=None, **kwargs):

        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        filter_fields = json.loads(filter_fields)
        if sort_fields:
            sort_fields = json.loads(sort_fields)
        if paginate:
            paginate = json.loads(paginate)

        response = get_manual_packs(int(company_id), filter_fields, paginate, sort_fields)

        return response


class GetNewPacksChangeRx(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, template_id=None, company_id=None, assigned_to=None, **kwargs):

        if company_id is None or template_id is None or assigned_to is None:
            return error(1001, "Either of the parameters are missing: template_id or company_id or assigned_to.")

        response = get_new_packs_change_rx(template_id, company_id, assigned_to)

        return response


class SamePatientPacks(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, date_from=None, date_to=None, company_id=None, date_type=True, patient_id=None, user_id=None,
            assigned_user_id=None, pack_master=False,pack_header_id = None,  **kwargs):
        # check if input argument kwargs is present
        # if patient_id is None :
        #     return error(1001, "Missing Parameter(s): patient_id .")

        dict_patient_info = {"date_from": date_from, "date_to": date_to, "company_id": company_id,
                             "date_type": date_type, "patient_id": patient_id, "user_id": user_id,
                             "assigned_user_id": assigned_user_id, "pack_master": pack_master,
                             "pack_header_id": pack_header_id}
        response = get_similar_manual_packs(dict_patient_info)

        return response


class TransferManualPacks(object):
    """ controller for transfer manual packs"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            print(kwargs["args"])
            response = validate_request_args(kwargs["args"], transfer_manual_packs)
            return response
        else:
            return error(1001)


class PackDrug(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, pack_ids=None, batch_id=None, **kwargs):
        if company_id is None or (pack_ids is None and batch_id is None):
            return error(1001, "Missing Parameter(s): company_id or (pack_ids and batch_id).")

        args = {
            "company_id": company_id,
            "pack_id_list": pack_ids,
            "batch_id": batch_id
        }
        response = get_pack_drugs(args)

        return response


class UserAssignedPacks(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], get_user_assigned_packs)
        else:
            return error(1001)
        return create_response(response)

    @use_database(db, settings.logger)
    def GET(self, company_id=None, users=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id.")
        else:
            pack_map_dict = {
                'company_id': company_id,
                'users': users
            }
            response = get_user_assigned_pack_count(pack_map_dict)
            return response


class UnAssignPacks(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, users=None, **kwargs):
        if not company_id or not users:
            return error(1001, "Missing Parameter(s): company_id.")
        else:
            user_dict = {
                'company_id': company_id,
                'users': users
            }
            response = unassign_packs(user_dict)
            return response


class SimilarManualPacks(object):
    """
        @class: SimilarPacks
        @type: class
        @param: object
        @desc: Gets similar packs based on similar
               drugs and same pack header ID.
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, date_from=None, date_to=None, date_type=None, batch_distribution=None ,**kwargs):
        # check if input argument kwargs is present
        if pack_id is None:
            return error(1001, "Missing Parameter(s): pack_id.")

        if date_type and (not date_to or not date_from):
            return error(1001, "Missing Parameter(s): date_to or date_from.")

        pack_id = json.loads(pack_id)
        dict_pack_info = {"pack_id": pack_id,
                          "date_type": date_type,
                          "date_to": date_to,
                          "date_from": date_from,
                          "batch_distribution": batch_distribution}
        response = get_similar_packs_manual_assign(dict_pack_info)

        return response


@cherrypy.tools.json_out()
class UserWiseCounts(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        return getUserWiesPacksCount(company_id)


class StoreExtraHours(object):
    """ saves the time for overloaded packs in db table overloaded pack timings"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            print(kwargs["args"])
            response = validate_request_args(kwargs["args"], create_overloadedpack_data)
        else:
            return error(1001)

        return response


class SetFillTime(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], set_fill_time)
        else:
            return error(1001)
        return response


class FillPartially(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], partially_filled_pack)
        else:
            return error(1001)
        return response


class MaxOrderNo(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, **kwargs):
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")

        response = max_order(int(system_id))

        return response


class CreateDummyPacks(object):
    """
          @class: CreateDummyPacks
          @param: object
          @desc: creates a dummy pack
          @args: rx_ids and system_id

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, rx_ids=None, system_id=None, **kwargs):
        # check if pack id is present
        if rx_ids is None or system_id is None:
            return error(1001, "Missing Parameter(s): rx_ids or system_id.")

        args = {"rx_ids": rx_ids, "system_id": int(system_id)}
        response = populate_pack_generator(args)

        return response


class TestPacks(object):
    """
          @class: TestPacks
          @type: class
          @param: object
          @desc: creates test packs

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], generate_test_packs
            )
        else:
            return error(1001, "Missing Parameters.")

        return response


class GetAllUnassociatedPacks(object):
    """
          @type: class
          @param: object
          @desc:  get all packs whose rfid is null
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, robotid, from_date, to_date):
        # check if input argument kwargs is present
        if robotid is None or from_date is None or to_date is None:
            return error(1001, "Missing Parameter(s): robot id or from_date or to_date.")
        else:
            try:
                dict_rfid_info = {
                    "device_id": robotid,
                    "from_date": from_date,
                    "to_date": to_date
                }
                response = get_all_unassociated_packs(dict_rfid_info)
            except Exception as ex:
                return error(1001, "Missing Parameters.")

        return response


@cherrypy.tools.json_out()
class ManualPacking(object):
    exposed = True

    @cherrypy.tools.allow(methods=['POST', 'OPTIONS'])
    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def packs(self):
        return getpacks(cherrypy.request, json)


@cherrypy.tools.json_out()
class PatientsController(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, available_olny=True, **kwargs):
        return getPatients(company_id, available_olny)

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self):
        return getPatientsList(cherrypy.request, json)


@cherrypy.tools.json_out()
class FacilityController(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, available_olny=True, **kwargs):
        return getFacilities(company_id, available_olny)

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self):
        return getFacilitiesList(cherrypy.request, json)


class PackUserMap(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], map_user_pack)
        else:
            return error(1001)
        return create_response(response)

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
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
            response = create_response(get_pack_user_map(args))
            return response
        except Exception as ex:
            print(ex)
            return error(1001, "No record found for the given parameters.")

        # return response


class GetUserPackStats(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, date_from=None, date_to=None,
            status=None, system_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "pack_status": status,
            "company_id": company_id,
            "system_id": system_id
        }
        response = get_user_pack_stats(args)

        return response


class ManualCountStats(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, date_from=None, date_to=None, company_id=None, date_type=True, status=None, assigned_to=None,
            user_stats=None, **kwargs):

        # check if input argument kwargs is present
        if date_type is None or company_id is None or assigned_to is None or status is None:
            return error(1001, "Missing Parameter(s): data_type or company_id or assigned_to or status.")

        dict_patient_info = {"date_from": date_from, "date_to": date_to, "company_id": company_id,
                             "date_type": date_type, "status": json.loads(status) if status else status,
                             "assigned_to": assigned_to}

        if user_stats is not None:
            dict_patient_info["user_stats"] = json.loads(user_stats)
        if not dict_patient_info["status"]:
            return error(1000, "status is empty")
        response = get_manual_count_stats(dict_patient_info)

        return response


class SlotDetailsForVisionSystem(object):
    """
        @class: SlotDetailsForVisionSystem
        @type: class
        @param: object
        @desc: get the refill canister information notification
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, device_id=None, **kwargs):
        if pack_id is None or system_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): pack_id or system_id or device_id.")

        try:
            dict_pack_info = {
                "pack_id": pack_id,
                "system_id": system_id,
                "device_id": device_id
            }
            response = get_slot_details_for_vision_system(dict_pack_info)
        except Exception as ex:
            return error(1001, ex)

        return response


class SlotsForUserStation(object):
    """
          @class: SlotsForUserStation
          @type: class
          @param: object
          @desc: slot details and incorrect drug data for a
                 pack to show on user station
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, **kwargs):
        if pack_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): pack_id or system_id.")
        args = {"pack_id": pack_id, "system_id": system_id}
        response = get_slots_for_user_station(args)

        return response


class GetSlotDetails(object):
    """
    @class: GetSlotDetails
    @type: class
    @param: object
    @desc: Get the slot details for the given pack id and system id.

    """
    exposed = True

    # @authenticate(settings.logger) # to support print utility
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, pvs_data_required=None, rts_data_required=None, user_id=None,
            call_from_mvs=None, max_pack_consumption_end_date=None, cyclic_pack=True, module_id=None, **kwargs):
        # check if packid is present
        if system_id is None or pack_id is None:
            return error(1001, "Missing Parameter(s): system_id or pack_id.")

        if pvs_data_required:
            pvs_data_required = bool(int(pvs_data_required))  # expected values 0,1
        else:
            pvs_data_required = False

        if call_from_mvs:
            call_from_mvs = bool(int(call_from_mvs))  # expected values 0,1
        else:
            call_from_mvs = False
        # pvs_data_required = True
        if user_id:
            try:
                user_id = int(user_id)
            except:
                user_id = None
        if cyclic_pack:
            cyclic_pack = bool(int(cyclic_pack))
        args = {
            "pack_id": int(pack_id),
            "system_id": int(system_id),
            "pvs_data_required": pvs_data_required,
            "user_id": user_id,
            "call_from_mvs": call_from_mvs,
            "max_pack_consumption_end_date": max_pack_consumption_end_date,
            "cyclic_flag": cyclic_pack,
            "module_id": module_id
        }
        response = get_slots_for_label_printing(args)

        return response


class GetDrugsOfReusePack(object):
    """
        @class: GetDrugsOfReusePack
        @type: class
        @param: object
        @desc: Get the drug details of reuse pack

        """
    exposed = True

    # @authenticate(settings.logger) # to support print utility
    @use_database(db, settings.logger)
    def GET(self, pack_display_id=None, company_id=None, similar_pack_ids=None, is_change_rx_pack=None, **kwargs):
        # check if packid is present
        if pack_display_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): pack_dispaly_id or company_id.")

        if type(similar_pack_ids) is str:
            similar_pack_ids = eval(similar_pack_ids)

        if type(is_change_rx_pack) is str:
            is_change_rx_pack = is_change_rx_pack.capitalize()
            is_change_rx_pack = eval(is_change_rx_pack)

        response = get_drugs_of_reuse_pack(pack_display_id=pack_display_id,
                                           company_id=company_id,
                                           similar_pack_ids=similar_pack_ids,
                                           is_change_rx_pack=is_change_rx_pack)

        return response

class GetLabelInfo(object):
    """
    @class: GetLabelInfo
    @type: class
    @param: object
    @desc: Get the label info for which the pack label is to be printed.

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, **kwargs):
        # check if pack id is present
        if system_id is None or pack_id is None:
            return error(1001, "Missing Parameter(s): system_id or pack_id.")

        args = {"pack_id": pack_id, "system_id": system_id}
        args.update(**kwargs)
        response = prepare_label_data(args)

        return response


class PersistSlotTransaction(object):
    """
          @class: GetCanisterInfo
          @type: class
          @param: object
          @desc:  get the canister information for the given robotid
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], populate_slot_transaction
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class PackStatus(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, pack_ids=None, **kwargs):
        if company_id is None or pack_ids is None:
            return error(1001, "Missing Parameter(s): company_id or pack_ids.")

        response = get_pack_data(company_id, pack_ids)

        return response


class GetPackGrid(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self,pack_id=None,grid_type=None, **kwargs):
        response = get_pack_grid_data(pack_id, grid_type)
        return response


class VerifyPackId(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_id):
        if pack_id is None:
            return error(1001, "Missing Parameter(s): pack_id.")
        args = {
            'pack_id': pack_id
        }
        response = verify_pack(args)
        return response


class GetPacksInfo(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, filters=None, sort_fields=None, paginate=None,
            company_id=None, time_zone=None,
            user_id=None, **kwargs):
        if company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): company_id or time_zone.")
        try:
            args = {
                "company_id": company_id,
                "time_zone": time_zone,  # expected values 0,1
                "user_id": user_id
            }
            if 'system_id' in kwargs and kwargs['system_id']:
                args['system_id'] = kwargs['system_id']
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        response = get_packs_info(args)

        return response


class ReusePack(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], reuse_pack
                )

                return response
        except Exception as e:
            raise e


class RecommendReusePack(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], recommend_reuse_pack
                )

                return response
        except Exception as e:
            raise e


class DiscardPackDrug(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], discard_pack_drug
                )

                return response

        except Exception as e:
            raise e


class ResealPack(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], reseal_pack
                )

                return response
        except Exception as e:
            raise e


class GetReuseInProgressPack(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, current_pack_ids=None):

        try:
            if current_pack_ids is None:
                return error(1001, "Missing Parameter(s): current_pack_ids.")

            response = get_reuse_in_progress_pack(current_pack_ids)

            return response

        except Exception as e:
            raise e


class GetReusePackDrugData(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_ids=None, company_id=None):
        try:
            if pack_ids is None:
                return error(1001, "Missing Parameter(s): pack_ids.")

            if company_id is None:
                return error(1001, "Missing Parameter(s): company_id.")

            if type(pack_ids) == str:
                pack_ids = eval(pack_ids)

            response = get_reuse_pack_drug_data(pack_ids, company_id)

            return response

        except Exception as e:
            raise e


class RTSOfPack(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], rts_of_pack
                )

                return response
        except Exception as e:
            raise e


class GetVialLabel(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], get_vial_label
                )

                return create_response(response)
        except Exception as e:
            raise e


class EPBMGeneralAPI(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, query_string_parameter=None, api_name=None, api_type=None, **kwargs):
        try:
            response = None
            if company_id is None:
                return error(1001, "Missing Parameter(s): company_id.")

            if api_name is None:
                return error(1001, "Missing Parameter(s): api_name.")

            if api_type is None:
                return error(1001, "Missing Parameter(s): api_type.")

            if query_string_parameter and type(query_string_parameter) == str:
                query_string_parameter = eval(query_string_parameter)

            if "args" in kwargs and kwargs['args']:
                if type(kwargs["args"]) == str:
                    temp = kwargs['args']
                    temp = json.loads(temp)
                    kwargs['args'] = temp
                response = epbm_general_api(kwargs['args'], query_string_parameter, api_name, api_type)

            return response
        except Exception as e:
            return error(2001)


class GetVialList(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        try:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], get_vial_list
                )

                return response
        except Exception as e:
            raise e


class SearchPatient(object):
    """
    To search the patient
    """
    exposed = True

    def GET(self, company_id=None, filter_fields=None, paginate=None, sort_fields=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id")
        try:
            if filter_fields:
                filter_fields = json.loads(filter_fields)
            if paginate:
                paginate = json.loads(paginate)
            if sort_fields:
                sort_fields = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as e:
            return error(1020, str(e))

        try:
            response = master_search(company_id, filter_fields, sort_fields, paginate)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as e:
            return error((1020, str(e)))


class SearchContact(object):
    """
    Api to search doctor or patient or facility and there contact
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, search=None, paginate=None, sort_fields=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id")
        try:
            if paginate:
                paginate = json.loads(paginate)
            if sort_fields:
                sort_fields = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as e:
            return error(1020, str(e))

        try:
            response = person_master_search(company_id, search, sort_fields, paginate)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as e:
            return error((1020, str(e)))
