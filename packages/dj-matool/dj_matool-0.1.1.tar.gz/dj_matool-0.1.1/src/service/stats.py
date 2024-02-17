"""
      @file: stats.py
      @createdBy: Manish Agarwal
      @createdDate: 09/08/2015
      @lastModifiedBy: Manish Agarwal
      @lastModifiedDate: 02/17/2015
      @type: file
      @desc: List of web services for Dashboard.

"""
import json
from datetime import timedelta, date

from peewee import DoesNotExist, fn

import settings
from pymysql import InternalError
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_verification import PackVerification
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails

logger = settings.logger

__module__ = 'stats'


def get_last_n_days(n):
    """
        @function: get_last_n_days
        @createdBy: Manish Agarwal
        @createdDate: 09/08/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/08/2015
        @type: function
        @param: int
        @purpose - Get the last nth dates starting from today.
        @input -
            type: (int)
                n = 5
        @output -
            ['09-08-15','09-07-15','09-06-15','09-05-15','09-04-15',]
    """

    # Get the current date
    current_date = date.today()
    # Manish Agarwal 4/13/16 BugID: 64753
    # Changing date format to MySQL time format
    # Iterate over n and subtract n days from date
    date_list = [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, n)]
    return date_list


def get_pack_ids_for_given_date(date_list, status=[4]):
    """
        @function: get_pack_ids_for_given_date
        @createdBy: Manish Agarwal
        @createdDate: 09/08/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 02/17/2016
        @type: function
        @param: str
        @purpose - Get all the processed pack ids for the given date
        @input -
            type: (str)
                date = '09-08-15'
        @output -
            [1,2.3,4,5]
    """
    # Get the processed status from settings
    pack_id_list = []

    # Get the done pack ids from PackStatusTracker table
    for record in PackStatusTracker.select(PackStatusTracker.pack_id).dicts().\
            join(PackDetails).where(PackDetails.created_date << date_list,
                                    PackDetails.pack_status << status):
        pack_id_list.append(record["pack_id"])
    return pack_id_list


def get_count_for_pack_verification(packlist):
    """
        @function: get_count_for_pack_verification
        @createdBy: Manish Agarwal
        @createdDate: 09/12/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/12/2015
        @type: function
        @param: str
        @purpose - Get all the processed packids for the given date
        @input -
            type: (list)
                packlist = [1,2,3,4,5...]
        @output -
            verified_with_success = 2
            verified_with_failure = 3
    """
    verified_with_success = 0
    verified_with_failure = 0

    # use IN in SQL Query instead of filtering records one by one on packids
    if not packlist:
        return verified_with_success, verified_with_failure

    try:
        verified_with_success = PackVerification.select(PackVerification.pack_id).\
            where(PackVerification.pack_fill_status == settings.SUCCESS,
                  PackVerification.pack_id << packlist).wrapped_count()
        verified_with_failure = PackVerification.select(PackVerification.pack_id).\
            where(PackVerification.pack_fill_status == settings.FAILURE,
                  PackVerification.pack_id << packlist).wrapped_count()
    except Exception as ex:
        logger.error(str(ex))
        return verified_with_success, verified_with_failure

    return verified_with_success, verified_with_failure


def accumulate_pack_id(n):
    """
        @function: accumulate_pack_id
        @createdBy: Manish Agarwal
        @createdDate: 09/08/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/08/2015
        @type: function
        @param: int
        @purpose - Append the processed packids for the given date
        @input -
            type: (int)
                n = 4
        @output -
            {'09-08-15':[1,2,3,4,5],'09-07-15':[],......}
    """
    date_list = get_last_n_days(n)

    total_packs_list = get_pack_ids_for_given_date(date_list)
    return date_list, total_packs_list


def get_pending_packs(_date):
    """
        @function: get_pending_packs
        @createdBy: Manish Agarwal
        @createdDate: 10/11/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 02/17/2016
        @type: function
        @param: date
        @purpose - Get the number of pending packs for the given date
        @input -
            type: (int)
                n = '10-11-15'
        @output -
            22
    """

    # modified the function to pass robot_id as a argument to it.
    try:
        pack_list = PackDetails.select(PackDetails.id).where(PackDetails.pack_status == 2,
                                                                  PackDetails.created_date << _date).wrapped_count()
        return pack_list
    except Exception as ex:
        logger.error(ex, exc_info=True)
        return settings.NULL


def get_active_canister_list(device_id):
    """
        @function: gather_active_canister_list
        @createdBy: Manish Agarwal
        @createdDate: 09/13/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/13/2015
        @type: function
        @param: str
        @purpose - Get the canister number for the given ndc
        @input -
            type: (int)
                robot_id = 4
        @output -
            1,2,3,......
    """
    active_canister_count = 0
    try:
        active_canister_count = CanisterMaster.select(LocationMaster.location_number).dicts()\
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id)\
            .where(LocationMaster.device_id == device_id, CanisterMaster.active == settings.is_canister_active)\
            .wrapped_count()
    except Exception as ex:
        logger.error(ex, exc_info=True)
        return active_canister_count

    return active_canister_count


def get_current_module_name():
        """
        @purpose - Get the name of the file from which function is executed
        @input - None
        @output - stats.py
        """
        # caller_frame = stack()[1]
        # return caller_frame[0].f_globals.get('__file__', None)
        return "stats.py"


def gather_stats(dict_info):
    """
        @function: gather_stats
        @createdBy: Manish Agarwal
        @createdDate: 09/08/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/08/2015
        @type: function
        @param: int
        @purpose - Gather drug statistics for the given no of days.
        @input -
            type: (dict)
                dict_info["n"] = 5
        @output -
            {
                "08-31-15": {
                    "total_tray_drugs": 291,
                    "drug_list_robot": [],
                    "drug_list_manual": [
                        {
                            "NDC": "537460466",
                            "Quantity": 112,
                            "DrugName": null
                        },
                        {
                            "NDC": "537460466",
                            "Quantity": 112,
                            "DrugName": null
                        },
                        {
                            "NDC": "537460466",
                            "Quantity": 112,
                            "DrugName": null
                        },
                    ],
                    "total_robot_drugs": 0
                },
                 .
                 .
            }
    """
    n = dict_info["n"]
    device_id = dict_info["device_id"]

    return calculate_stats(n, device_id)


def get_manual_drug_percentage(pack_ids):
    slot_data = []
    try:
        for record in SlotDetails.select(DrugMaster.drug_name, DrugMaster.ndc,
                                         fn.sum(SlotDetails.quantity).alias("total_quantity"),
                                         SlotDetails.is_manual) \
                .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
                .join(DrugMaster, on=PatientRx.drug_id == DrugMaster.id) \
                .where(PackDetails.id << pack_ids) \
                .group_by(SlotDetails.is_manual):

            print("record", record)
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
            print(record["quantity"])
            slot_data.append(record)

        return slot_data
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        print(ex)
        return None
    except InternalError as e:
        logger.error(e, exc_info=True)
        print(e)
        return None
    except Exception as e:
        print(e)


def calculate_stats(n, device_id):
        """
        @function: gather_stats
        @createdBy: Manish Agarwal
        @createdDate: 09/08/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/08/2015
        @type: function
        @param: int
        @purpose - Gather drug statistics for the given no of days.
        @input - 5, 6
        @output -
            {
                "08-31-15": {
                    "total_tray_drugs": 291,
                    "drug_list_robot": [],
                    "drug_list_manual": [
                        {
                            "NDC": "537460466",
                            "Quantity": 112,
                            "DrugName": null
                        },
                        {
                            "NDC": "537460466",
                            "Quantity": 112,
                            "DrugName": null
                        },
                        {
                            "NDC": "537460466",
                            "Quantity": 112,
                            "DrugName": null
                        },
                    ],
                    "total_robot_drugs": 0
                },
                 .
                 .
            }
        """
        stat_data = {}

        try:
            # get the list of pack ids for the given number of days
            date_list, processed_packs = accumulate_pack_id(n)
        except Exception as ex:
            print(ex)
            logger.error(ex, exc_info=True)

        active_canister_count = get_active_canister_list(device_id)
        total_processed_packs = len(processed_packs)

        stat_data["active_canisters"] = active_canister_count
        stat_data["processed_packs"] = total_processed_packs
        stat_data["total_canisters"] = settings.MAX_LOCATION

        print(active_canister_count, total_processed_packs)

        slot_data = get_manual_drug_percentage([23000, 23001, 23004, 24000])

        return json.dumps({"data": stat_data, "status": "success", "error": "none"}, indent=4)


# print(gather_stats({"n": 5, "robot_id": 6}))
# gather the drug stats of the date and return the response to populate the table.
# 54.67.35.135

