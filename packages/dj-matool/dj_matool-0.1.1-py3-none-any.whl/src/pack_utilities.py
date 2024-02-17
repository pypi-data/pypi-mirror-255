# -*- coding: utf-8 -*-
"""
    src.pack_utilities
    ~~~~~~~~~~~~~~~~

    This module covers all the helper functions which are required by the core pack
    module.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""
import settings
from dosepack.utilities.utils import get_current_date, log_args_and_response
from src import constants
from src.dao.pill_vision_system_dao import pvs_drug_count_slots

logger = settings.logger


@log_args_and_response
def create_slot(dict_drug_info):
    """ Takes a drug dict and creates a slot dict from it.

        Args:
            dict_drug_info (dict): The drug dict to be mapped to slot.

        Returns:
            dict : The slot dict

        Examples:
            >>> create_slot({"drug_name": "Atrovastatin", "ndc": "123456789"})
            7
    """
    pvs_qty = None
    pvs_identified_quantity = pvs_drug_count_slots(dict_drug_info["slot_header_id"], dict_drug_info["unique_drug_id"])
    if pvs_identified_quantity:
        pvs_qty = pvs_identified_quantity[0]['predicted_qty']
    logger.info("pvs_identified_quantity : {}".format(pvs_identified_quantity))
    response = {"drug_name": dict_drug_info["drug_name"],
                "drug_full_name": dict_drug_info["drug_full_name"],
                "ndc": dict_drug_info["ndc"],
                "strength": dict_drug_info["strength"],
                "strength_value": dict_drug_info["strength_value"],
                "imprint": dict_drug_info["imprint"],
                "shape": dict_drug_info["shape"],
                "color": dict_drug_info["color"],
                "pharmacy_rx_no": dict_drug_info["pharmacy_rx_no"],
                "quantity": dict_drug_info["quantity"],
                "filled_quantity": dict_drug_info["filled_quantity"],
                "pvs_identified_quantity": pvs_qty,
                "sensor_detected_quantity": dict_drug_info["dropped_qty"],
                "is_manual": dict_drug_info["is_manual"],
                "formatted_ndc": dict_drug_info.get("formatted_ndc", None),
                "txr": dict_drug_info.get("txr", None),
                "canister_id": dict_drug_info.get("canister_id", None),
                "expiry_status": dict_drug_info.get("expiry_status", None),
                'display_location': dict_drug_info.get('display_location', None),
                'device_name': dict_drug_info.get('device_name', None),
                "rfid": dict_drug_info.get("rfid", None),
                "short_drug_name_v1": dict_drug_info.get("short_drug_name_v1", None),
                "short_drug_name_v2": dict_drug_info.get("short_drug_name_v2", None),
                "display_drug_name": dict_drug_info.get("display_drug_name"),
                "is_mfd_drug": dict_drug_info.get("is_mfd_drug"),
                "is_robot_drug": dict_drug_info["is_robot_drug"],
                "is_robot_to_manual": dict_drug_info["is_robot_to_manual"],
                "unique_drug_id": dict_drug_info.get("unique_drug_id"),
                "drug_id": dict_drug_info.get("drug_id"),
                "is_in_stock": dict_drug_info["is_in_stock"],
                "last_seen_on": dict_drug_info["last_seen_on"],
                "last_seen_by": dict_drug_info["last_seen_by"],
                'is_mfd_to_manual': dict_drug_info.get('is_mfd_to_manual', None),
                'mfd_skipped_quantity': dict_drug_info.get('mfd_skipped_quantity', None),
                'mfd_dropped_quantity': dict_drug_info.get('mfd_dropped_quantity', None),
                'mfd_manual_filled_quantity': dict_drug_info.get('mfd_manual_filled_quantity', None),
                'mfd_canister_id': dict_drug_info.get('mfd_canister_id', None),
                'missing_drug': dict_drug_info.get('missing_drug', False),
                'is_filled': dict_drug_info.get('is_filled'),
                'expire_soon': dict_drug_info.get('expire_soon'),
                'expire_soon_drug': dict_drug_info.get('expire_soon_drug'),
                'expiry_date': dict_drug_info.get('expiry_date'),
                "case_id": dict_drug_info.get('case_id'),
                "is_broken_pill": dict_drug_info.get("is_broken_pill", False),
                }
    if dict_drug_info.get("filled_quantity") is not None:
        response["reported_error"] = True if dict_drug_info["filled_quantity"] < dict_drug_info["quantity"] else False
    return response


def create_base_pack(patient_id, file_id, pharmacy_fill_id, total_packs, delivery_date, user_id, change_rx_flag):
    """ Creates a base pack dict.

        Args:
            patient_id (int): The id of the patient
            file_id (int): The id of the file processed.
            pharmacy_fill_id (int): The pharmacy id assigned to the fill.
            scheduled_type (str): The type of schedule or delivery.
            total_packs (int): The total number of packs for the given patient
            delivery_date (str | None): Delivery Date of pack.
            user_id (int): The id of the user who created the pack.
            change_rx_flag (bool): True, if Pack Generation is due to Change Rx else False

        Returns:
            dict : The base pack dict

        Examples:
            >>> create_base_pack()
    """
    return {"patient_id": patient_id, "file_id": file_id, "pharmacy_fill_id": pharmacy_fill_id,
            "total_packs": total_packs, "created_by": user_id, "modified_by": user_id, "start_day": 0,
            "delivery_datetime": delivery_date, "change_rx_flag": change_rx_flag}


def create_child_pack(base_pack_id, pharmacy_pack_id, pack_no, status, filled_by,
                      filled_days, fill_start_date, delivery_schedule,
                      user_id, pack_plate_location, order_no,
                      consumption_start_date, consumption_end_date,
                      company_id, system_id, is_takeaway, filled_date, filled_at, is_bubble=False,
                      pack_type=constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4):
    """ Creates a child pack dict.

        Args:
            base_pack_id (int): The base id of the pack generated for the patient.
            pharmacy_pack_id (int): The id assigned to the pack by the pharmacy software.
            pack_no (int): The order no of the generated pack.
            status (int): The status of the pack generated. The default status will be pending.
            filled_by (str): The user who created the file for the pack.
            filled_days (int): The number of days for which the pack is to be filled
            fill_start_date (datetime): The start date for the pack filling.
            delivery_schedule (datetime): The date at which the pack is supposed to be delivered to the patient.
            user_id (int): The id of the user
            consumption_start_date (date): Start date of the pack for consuming.
            consumption_end_date (date): Last date of the pack for consuming.
            company_id (int): The company_id for which pack is being generated
            system_id (int): The system id for which pack is being generated
            is_takeaway (bool): Flag to indicate takeaway pack
            filled_date (str | None): If marked manual then date of filling otherwise None
            filled_at (int): Indicates where was the pack filled

        Returns:
            dict : The child pack dict

        Examples:
            >>> create_child_pack()
    """
    if pack_type == constants.UNIT_DOSE_PER_PACK:
        if is_bubble:
            packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_8X4
        else:
            packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_7X4
    else:
        if is_bubble:
            packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_8X4
        else:
            packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4
    return {
        "pack_header_id": base_pack_id,
        "pack_display_id": pharmacy_pack_id,
        "pack_no": pack_no,
        "pack_status": status,
        "filled_by": filled_by,
        "filled_days": filled_days,
        "fill_start_date": fill_start_date,
        "delivery_schedule": delivery_schedule,
        "created_by": user_id,
        "modified_by": user_id,
        "created_date": get_current_date(),
        "pack_plate_location": pack_plate_location,
        "order_no": order_no,
        "consumption_start_date": consumption_start_date,
        "consumption_end_date": consumption_end_date,
        "company_id": company_id,
        "system_id": system_id,
        "is_takeaway": is_takeaway,
        "filled_date": filled_date,
        "filled_at": filled_at,
        "grid_type": constants.PACK_GRID_ROW_7x4 if not is_bubble else constants.PACK_GRID_ROW_8x4,
        "packaging_type": packaging_type
    }
