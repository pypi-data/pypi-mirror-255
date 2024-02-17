import math
import os
import sys
from collections import OrderedDict
from copy import deepcopy

from peewee import InternalError, IntegrityError, DataError

import settings
import src.constants
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src import constants
from src.dao.batch_dao import get_system_id_from_batch_id, db_update_mfd_status
from src.dao.canister_recommendation_configuration_dao import get_configuration_for_recommendation
from src.dao.device_manager_dao import db_get_system_zone_mapping
from src.dao.mfd_dao import get_batch_data, check_mfd_recommendation_executed, get_half_pill_drug_pack_data, \
    get_pack_slotwise_canister_drugs, get_quadrant_drugs, get_manual_drug_pack_info, add_mfd_analysis_data, \
    add_mfd_analysis_details_data, populate_data_in_frequent_mfd_drugs_table
from src.dao.misc_dao import update_sequence_no_for_pre_processing_wizard
from src.dao.pack_analysis_dao import db_delete_pack_analysis_by_packs, db_save_analysis, \
    db_delete_pack_analysis_details_slots
from src.service.misc import update_timestamp_couch_db_pre_processing_wizard
from src.service.mfd_drops import RecommendDrops

logger = settings.logger


@log_args_and_response
@validate(required_fields=['user_id', 'system_id', 'batch_id', 'company_id'])
def save_mfd_recommendation(batch_info):
    """
    Function to get slots filled by mfd and populate data in mfd tables
    @param batch_info:
    @return:
    """
    batch_id = batch_info['batch_id']
    user_id = batch_info['user_id']
    try:
        with db.transaction():
            batch_data = get_batch_data(batch_id)
            if batch_data.sequence_no == constants.PPP_SEQUENCE_IN_PROGRESS:
                return error(2000)
            else:
                previous_sequence = batch_data.sequence_no
                logger.info(
                    "In save_mfd_recommendation: previous sequence: {} for batch_id:{}".format(previous_sequence,
                                                                                               batch_id))

                # update sequence_no to PPP_SEQUENCE_IN_PROGRESS(1) in batch master
                seq_status = update_sequence_no_for_pre_processing_wizard(
                    sequence_no=constants.PPP_SEQUENCE_IN_PROGRESS,
                    batch_id=batch_id)
                logger.info(
                    "In save_mfd_recommendation: save_mfd_recommendation execution started: {} , changed sequence to "
                    "{} for batch_id: {} "
                        .format(seq_status, constants.PPP_SEQUENCE_IN_PROGRESS, batch_id))
                if seq_status:
                    # update couch db timestamp for pack_pre processing wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                    logger.info(
                        "In save_mfd_recommendation : time stamp updated for pre processing wizard for in_progress "
                        "API: {} for batch_id: {}".format(
                            couch_db_status, batch_id))

        # check if mfd recommendation already executed
        status = check_mfd_recommendation_executed(batch_id=batch_id)
        if status:
            seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                      batch_id=batch_id)
            if seq_status:
                # update couch db timestamp for pack_pre processing wizard change
                couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                logger.info(
                    "In save_mfd_recommendation :Error in MFD recommendation, already executed ,time stamp updated "
                    "for pre processing wizard: {} change sequence to : {} for batch_id: {}".format(
                        couch_db_status, previous_sequence, batch_id))
            logger.error("Error in MFD recommendation, already executed {}".format(status))
            return error(1020, "Error in MFD recommendation, already executed")

        # get required data from db and created dicts
        patient_pack_column_drop_slot_quad_dict, device_ordered_patients_dict, pack_slot_drug_qty_dict, \
        patient_pack_slot_quad_config_dict, patient_pack_column_manual_slots_dict, pack_slot_drug_dict, \
        pack_drug_slot_number_slot_id_dict, device_ordered_packs_dict, robot_quadrant_drug_data, \
        robot_quadrant_drug_canister_dict, robot_drugs_dict, pack_slot_drug_dict_global, pack_list, robot_half_pill_drug_pack_dict = get_require_data_for_mfd(
            batch_id)
        logger.info("save_mfd_recommendation get_require_data_for_mfd")

        if len(device_ordered_patients_dict):
            # if there are packs which required mfd to be filled
            pack_column_quad_slots_dict, pack_slot_total_quantity_dict, pack_slot_multi_quadrant_dict = prepare_needed_data_structures(
                patient_pack_column_drop_slot_quad_dict, patient_pack_slot_quad_config_dict, pack_slot_drug_qty_dict)
            logger.info("save_mfd_recommendation prepare_needed_data_structures")

            mfdr = MFDRecommendation(batch_id, patient_pack_column_drop_slot_quad_dict, device_ordered_patients_dict,
                                     pack_slot_drug_qty_dict, pack_column_quad_slots_dict,
                                     pack_slot_total_quantity_dict,
                                     patient_pack_column_manual_slots_dict, pack_slot_drug_dict,
                                     pack_drug_slot_number_slot_id_dict, device_ordered_packs_dict,
                                     robot_quadrant_drug_data, robot_quadrant_drug_canister_dict, robot_drugs_dict,
                                     patient_pack_slot_quad_config_dict, pack_slot_drug_dict_global,
                                     pack_slot_multi_quadrant_dict, robot_half_pill_drug_pack_dict)
            recommendation_response, auto_packs_response, auto_packs_list, mfd_slots = mfdr.get_mfd_recommendation()
            logger.info("save_mfd_recommendation mfd recommendation done")

            save_recommendation_analysis(recommendation_response, auto_packs_response, auto_packs_list, batch_id,
                                         mfd_slots, user_id)
            logger.info("save_mfd_recommendation data saved in db")
            # return create_response(True)

        # update sequence_no to PPP_SEQUENCE_MFD_RECOMMENDATION_DONE(it means mfd recommendation api run successfully)
        seq_status = update_sequence_no_for_pre_processing_wizard(
            sequence_no=constants.PPP_SEQUENCE_MFD_RECOMMENDATION_DONE,
            batch_id=batch_id)
        logger.info(
            "In save_mfd_recommendation: save_mfd_recommendation run successfully: {} , changed sequence to {} for "
            "batch_id: {} "
                .format(seq_status, constants.PPP_SEQUENCE_MFD_RECOMMENDATION_DONE, batch_id))
        if seq_status:
            # update couch db timestamp for pack_pre processing wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
            logger.info(
                "In save_mfd_recommendation time stamp updated for pre processing wizard: {} for batch_id: {}".format(
                    couch_db_status, batch_id))
        return create_response(True)

    except (InternalError, IntegrityError, DataError) as e:
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                  batch_id=batch_id)
        if seq_status:
            # update couch db timestamp for pack_pre processing wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
            logger.info(
                "In save_mfd_recommendation : Failure in save_mfd_recommendation time stamp updated for pre "
                "processing wizard: {}, change sequence to: {} for batch_id: {}".format(
                    couch_db_status, previous_sequence, batch_id))
        logger.error("Error in MFD recommendation {}".format(e))
        return error(0, str(e))

    except Exception as e:
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                  batch_id=batch_id)
        if seq_status:
            # update couch db timestamp for pack_pre processing wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
            logger.info(
                "In save_mfd_recommendation : Failure in save_mfd_recommendation time stamp updated for pre "
                "processing wizard: {}, change sequence to: {} for batch_id: {}".format(
                    couch_db_status, previous_sequence, batch_id))

        # logger.error("Error in MFD recommendation {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in save_mfd_recommendation: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        return error(0, str(e))


class MFDRecommendation:
    def __init__(self, batch_id, patient_pack_column_drop_slot_quad_dict, device_ordered_patients_dict,
                 pack_slot_drug_qty_dict, pack_column_quad_slots_dict, pack_slot_total_quantity_dict,
                 patient_pack_column_manual_slots_dict, pack_slot_drug_dict, pack_drug_slot_number_slot_id_dict,
                 device_ordered_packs_dict, robot_quadrant_drug_data, robot_quadrant_drug_canister_dict,
                 robot_drugs_dict, patient_pack_slot_quad_config_dict, pack_slot_drug_dict_global,
                 pack_slot_multi_quadrant_dict, robot_half_pill_drug_pack_dict):
        """
        This Class is of MFD Recommendation Algorithm. This takes all the input data which is fetched from database with particular batch_id.
        """
        self.batch_id = batch_id
        self.patient_pack_column_drop_slot_quad_dict = patient_pack_column_drop_slot_quad_dict
        self.device_ordered_patients_dict = device_ordered_patients_dict
        self.pack_slot_drug_qty_dict = pack_slot_drug_qty_dict
        self.pack_column_quad_slots_dict = pack_column_quad_slots_dict
        self.patient_pack_column_manual_slots_dict = patient_pack_column_manual_slots_dict
        self.pack_slot_total_quantity_dict = pack_slot_total_quantity_dict
        self.pack_slot_drug_dict = pack_slot_drug_dict
        self.pack_drug_slot_number_slot_id_dict = pack_drug_slot_number_slot_id_dict
        self.device_ordered_packs_dict = device_ordered_packs_dict
        self.robot_quadrant_drug_data = robot_quadrant_drug_data
        self.robot_quadrant_drug_canister_dict = robot_quadrant_drug_canister_dict
        self.robot_drugs_dict = robot_drugs_dict
        self.patient_pack_slot_quad_config_dict = patient_pack_slot_quad_config_dict
        self.patient_pack_slot_quad_config_dict_final = deepcopy(patient_pack_slot_quad_config_dict)
        self.pack_slot_drug_dict_global = pack_slot_drug_dict_global
        self.pack_slot_multi_quadrant_dict = pack_slot_multi_quadrant_dict
        self.robot_half_pill_drug_pack_dict = robot_half_pill_drug_pack_dict
        # self.valid_slot_quadrant = {1: {2, 3}, 2: {2, 3}, 3: {2, 3}, 4: {2, 3}, 5: {2, 3}, 6: {2, 3}, 7: {3},
        #                             8: {1, 2, 3, 4}, 9: {1, 2, 3, 4}, 10: {1, 2, 3, 4}, 11: {1, 2, 3, 4},
        #                             12: {1, 2, 3, 4}, 13: {1, 2, 3, 4}, 14: {3, 4}, 15: {1, 2, 3, 4}, 16: {1, 2, 3, 4},
        #                             17: {1, 2, 3, 4}, 18: {1, 2, 3, 4}, 19: {1, 2, 3, 4}, 20: {1, 2, 3, 4}, 21: {3, 4},
        #                             22: {1, 4}, 23: {1, 4}, 24: {1, 4}, 25: {1, 4}, 26: {1, 4}, 27: {1, 4}, 28: {4}}
        # self.valid_slot_quadrant = {1: {2}, 2: {2, 3}, 3: {2, 3}, 4: {2, 3}, 5: {2, 3}, 6: {2, 3}, 7: {2, 3}, 8: {3},
        #                             9: {1, 2}, 10: {1, 2, 3, 4}, 11: {1, 2, 3, 4}, 12: {1, 2, 3, 4}, 13: {1, 2, 3, 4},
        #                             14: {1, 2, 3, 4}, 15: {1, 2, 3, 4}, 16: {3, 4}, 17: {1, 2}, 18: {1, 2, 3, 4},
        #                             19: {1, 2, 3, 4}, 20: {1, 2, 3, 4}, 21: {1, 2, 3, 4}, 22: {1, 2, 3, 4},
        #                             23: {1, 2, 3, 4}, 24: {3, 4}, 25: {1}, 26: {1, 4}, 27: {1, 4}, 28: {1, 4},
        #                             29: {1, 4}, 30: {1, 4}, 31: {1, 4}, 32: {4}}

        # TODO: self.valid_slot_quadrant can get from database
        self.valid_slot_quadrant = get_configuration_for_recommendation(valid_slot_quadrant=True)
        # self.valid_slot_quadrant = {}
        # query = EdgeSlotMapping.select().dicts()
        # for data in query:
        #     for slot in data["slots"]:
        #         self.valid_slot_quadrant[slot] = data["quadrant"]
        # max_slot = PackGrid.select(fn.MAX(PackGrid.slot_number)).sclar()
        # for slot in range(1,max_slot+1):
        #     if slot not in self.valid_slot_quadrant:
        #         self.valid_slot_quadrant[slot] = {1,2,3,4}

        self.independent_canister_flag = 1
        self.canister_id_count = 1
        self.canister_slot_data_dict = {}
        self.canister_dest_data_dict = {}
        self.pack_canister_data = {}
        self.canister_slot_details = {}
        self.canister_dest_details = {}
        self.patient_canister_data = {}
        self.quad_capacity_count = {1: 0, 2: 0, 3: 0, 4: 0}
        self.patient_canister_len = OrderedDict()
        self.analysis_data = {}
        self.auto_packs_analysis_data = []
        self.auto_packs_list = []
        pass

    @log_args_and_response
    def get_mfd_recommendation(self):
        """
        This function recommends the mfd canisters and their details according to pack_sequence and single canister can't be share between two patients.
        :return:
        """
        self.mfd_slots = set()
        try:
            for device, patients in self.device_ordered_patients_dict.items():   # patients : list()
                self.get_recommendation_data_for_device(device, patients)
                self.internal_slot_count = 1
                # break

            self.distribute_canisters_between_users()
            self.analysis_data = self.save_analysis_mfd()
            return self.analysis_data, self.auto_packs_analysis_data, self.auto_packs_list, self.mfd_slots

        except Exception as e:
            logger.info("error in get_mfd_recom {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.info(
                f"Error in get_mfd_recommendation: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
            raise e

    def distribute_canisters_between_users(self):
        """
        This function will distribute the canisters between user with consideration that same patient canisters will be distributed to same user.
        Every time we assign canister to the user which have min no. of canisters.
        :return:
        """
        try:
            logger.info("distribute_canisters_between_users")

            user_canister_list = {}
            total_canister_len = 0
            user_canister_count = {}
            user_list = [1, 2, 3, 4]
            for user in user_list:
                user_canister_list[user] = {}
                user_canister_count[user] = 0
            for canisters in self.patient_canister_data.values():
                total_canister_len += len(canisters)
            split = math.ceil(total_canister_len / len(user_list))
            self.patient_canister_len = OrderedDict(
                sorted(self.patient_canister_len.items(), key=lambda k: k[1], reverse=True))
            user = user_list[0]
            while not len(self.patient_canister_len.keys()) == 0:
                patient = list(self.patient_canister_len)[0]
                del self.patient_canister_len[patient]
                if len(self.patient_canister_data[patient]) <= (split - len(user_canister_list[user])):
                    user_canister_list[user].update(self.patient_canister_data[patient])
                    user_canister_count[user] += len(self.patient_canister_data[patient])
                    for canister in self.patient_canister_data[patient].keys():
                        self.canister_dest_details[canister]['assigned_user_id'] = user
                    user_canister_count = OrderedDict(sorted(user_canister_count.items(), key=lambda k: k[1]))
                    user_list = list(user_canister_count.keys())
                    user = user_list[0]
                    del self.patient_canister_data[patient]

                if patient in self.patient_canister_data:
                    user_canister_list[user].update(self.patient_canister_data[patient])
                    user_canister_count[user] += len(self.patient_canister_data[patient])
                    user_canister_count = OrderedDict(sorted(user_canister_count.items(), key=lambda k: k[1]))
                    user_list = list(user_canister_count.keys())
                    user = user_list[0]
                    for canister in self.patient_canister_data[patient].keys():
                        self.canister_dest_details[canister]['assigned_user_id'] = user
                    del self.patient_canister_data[patient]

        except Exception as e:
            logger.info(e)
            raise

    @log_args_and_response
    def get_recommendation_data_for_device(self, device, patients):
        """
        This function Makes the recommendation data for the patients of particular device.
        :param device:
        :param patients:
        :return:
        """

        try:
            for patient in patients:  # take one by one patients
                logger.info("get_recommendation_data_for_device patient {}".format(patient))
                canister_slot_details = {}
                canister_slot_data_dict = {}

                # We are keeping this because if any quad capacity limit exceed above 20 then we can use this.
                self.quad_capacity_count_copy = deepcopy(self.quad_capacity_count)
                self.quad_capacity_count_base = deepcopy(self.quad_capacity_count)
                canister_dest_data_dict = {}

                # We are checking if this patient has fully manual slots!.
                if patient in self.patient_pack_column_manual_slots_dict:  # patient_pack_column_manual_slots_dict : patient --> pack --> column --> set () : slot_numbers
                    allocated_pack_slot_quadrant = {}
                    self.temp_canister_id_count = deepcopy(self.canister_id_count)
                    for pack, column_slots in self.patient_pack_column_manual_slots_dict[patient].items():
                        # we are checking this condition because if packs of same patient distributed between robots.
                        if pack not in self.device_ordered_packs_dict[device]:
                            continue
                        self.auto_packs_list.append(pack)
                        allocated_pack_slot_quadrant[pack] = {}
                        for column, slots in column_slots.items():
                            # Here we are finalizing quadrants for fully manual slots
                            allocated_pack_slot_quadrant[pack].update(self.allocate_quadrants(column, slots))

                    logger.info("pack_list")
                    pack_list = list(allocated_pack_slot_quadrant.keys())
                    # Make pack_slot_drug_dict for only this pack list
                    pack_slot_drug_dict = {pack: self.pack_slot_drug_dict_global[pack] for pack in pack_list}
                    pack_quadrant_data = {"quadrant_drugs": self.robot_quadrant_drug_data[device],
                                          "pack_slot_drug_dict": self.pack_slot_drug_dict,
                                          "pack_slot_drug_dict_global": pack_slot_drug_dict,
                                          "pack_slot_quad": allocated_pack_slot_quadrant}
                    md = RecommendDrops(pack_quadrant_data)
                    # Recommend new drops with manual slot quad consideration and separating out dicts.
                    self.pack_slot_drop_info_dict, self.pack_slot_drug_config_id_dict, self.pack_slot_drug_quad_id_dict, self.unique_matrix_list, self.unique_matrix_data_list, self.pack_data, self.pack_slot_drop_info_dict_manual = md.get_pack_fill_analysis()
                    # Modify required dicts with changed data.
                    self.modify_dictionaries(patient=patient)
                    # make auto data and delete the data of this packs from analysis details and save new.
                    pack_drug_canister_robot_dict_auto = self.fill_data_for_auto_slot_packs(device)
                    # Makes auto data for updating in pack_analysis and pack_analysis_details

                    self.auto_packs_analysis_data.extend(self.save_analysis(pack_drug_canister_robot_dict_auto))

                self.independent_canister_flag = 1
                self.column_quad_slot_drug_list_with_qty, self.column_independent_flag_dict = self.get_recommendation_data_for_patient(
                    device, patient)

                previous_slot = []
                logger.info("column_quad_slot_drug_list_with_qty for patient {}, {}".format(
                    self.column_quad_slot_drug_list_with_qty,
                    patient))
                for column, quad_info in self.column_quad_slot_drug_list_with_qty.items():
                    total_column_slot_drug_list = []
                    for each_quad, slot_drug_list_with_qty in quad_info.items():
                        add_slot = True
                        if type(each_quad) == int:
                            loop_quad = (each_quad,)
                        else:
                            loop_quad = each_quad
                        for quad in loop_quad:
                            if self.column_independent_flag_dict[column][each_quad]:
                                new_slot_drug_list_with_qty = []
                                slot_drug_list_with_qty_copy = []
                                while len(slot_drug_list_with_qty):
                                    if (slot_drug_list_with_qty[0][0], slot_drug_list_with_qty[0][1]) in previous_slot:
                                        previous_slot = []
                                        previous_slot.append(
                                            (slot_drug_list_with_qty[0][0], slot_drug_list_with_qty[0][1]))
                                        slot_drug_list_with_qty_copy.append(slot_drug_list_with_qty[0])
                                        slot_drug_list_with_qty.remove(slot_drug_list_with_qty[0])
                                        continue
                                    previous_slot = []
                                    new_slot_drug_list_with_qty.append(slot_drug_list_with_qty[0])
                                    previous_slot.append((slot_drug_list_with_qty[0][0], slot_drug_list_with_qty[0][1]))
                                    slot_drug_list_with_qty.remove(slot_drug_list_with_qty[0])
                                new_slot_drug_list_with_qty.extend(slot_drug_list_with_qty_copy)
                                new_slot_drug_list_with_qty.sort(key=lambda x: (x[0], x[3], x[1]))
                                slot_drug_list_with_qty = deepcopy(new_slot_drug_list_with_qty)
                            self.internal_slot_count = 1
                            catered_slot_ids = []
                            logger.info("slot_data")
                            for slot_data in slot_drug_list_with_qty:
                                if slot_data[1] in catered_slot_ids:
                                    if len(catered_slot_ids) > 2:
                                        catered_slot_ids = []
                                        self.internal_slot_count = 1
                                        if self.canister_id_count in canister_slot_data_dict:
                                            self.canister_id_count += 1
                                            if type(quad) == tuple:
                                                for each_quad in quad:
                                                    self.quad_capacity_count[each_quad] += 1
                                                    self.validate_quad_capacity_count(each_quad)
                                            else:
                                                self.quad_capacity_count[quad] += 1
                                                self.validate_quad_capacity_count(quad)
                                    else:
                                        add_slot = False
                                if add_slot:
                                    catered_slot_ids.append(slot_data[1])
                                if self.canister_id_count not in canister_slot_data_dict:
                                    canister_slot_data_dict[self.canister_id_count] = {}
                                if self.internal_slot_count not in canister_slot_data_dict[self.canister_id_count]:
                                    canister_slot_data_dict[self.canister_id_count][self.internal_slot_count] = {}
                                canister_slot_data_dict[self.canister_id_count][self.internal_slot_count]['pack_id'] = \
                                    slot_data[0]
                                canister_slot_data_dict[self.canister_id_count][self.internal_slot_count][
                                    'slot_number'] = slot_data[1]
                                canister_slot_data_dict[self.canister_id_count][self.internal_slot_count][
                                    'drug_info'] = dict(slot_data[2])
                                canister_slot_data_dict[self.canister_id_count][self.internal_slot_count][
                                    'drop_number'] = slot_data[3]
                                if self.canister_id_count not in canister_dest_data_dict:
                                    canister_dest_data_dict[self.canister_id_count] = {'device_id': device,
                                                                                       'quadrant': quad}
                                if self.internal_slot_count == 4:
                                    self.internal_slot_count = 1
                                    self.canister_id_count += 1
                                    if type(quad) == tuple:
                                        for each_quad in quad:
                                            self.quad_capacity_count[each_quad] += 1
                                            self.validate_quad_capacity_count(each_quad)
                                    else:
                                        self.quad_capacity_count[quad] += 1
                                        self.validate_quad_capacity_count(quad)
                                else:
                                    self.internal_slot_count += 1
                            if self.canister_id_count in canister_slot_data_dict:
                                self.canister_id_count += 1
                                if type(quad) == tuple:
                                    for each_quad in quad:
                                        self.quad_capacity_count[each_quad] += 1
                                        self.validate_quad_capacity_count(each_quad)
                                else:
                                    self.quad_capacity_count[quad] += 1
                                    self.validate_quad_capacity_count(quad)

                    logger.info("validate")
                self.canister_slot_data_dict.update(canister_slot_data_dict)
                self.canister_dest_data_dict.update(canister_dest_data_dict)
                # This below loop will make data for saving into database.
                for canister, slot_data in canister_slot_data_dict.items():
                    canister_slot_data_list = []
                    # ask change to meet
                    quad = canister_dest_data_dict[canister]['quadrant']
                    for internal_slot, drug_details in slot_data.items():
                        for drug, qty in drug_details["drug_info"].items():
                            # if type(quad) == tuple:
                            #     for each_quad in quad:
                            #         slot_id = self.pack_drug_slot_number_slot_id_dict[drug_details["pack_id"]][drug][drug_details["slot_number"]]
                            #         canister_slot_data_list.append((internal_slot,slot_id,drug_details["drop_number"],self.patient_pack_slot_quad_config_dict[patient][drug_details["pack_id"]][drug_details["slot_number"]][each_quad],qty))
                            # else:
                            slot_id = self.pack_drug_slot_number_slot_id_dict[drug_details["pack_id"]][drug][
                                drug_details["slot_number"]]
                            self.mfd_slots.add(slot_id)
                            quad_config = list(self.patient_pack_slot_quad_config_dict[patient][
                                                   drug_details["pack_id"]][
                                                   drug_details["slot_number"]].keys())[0]

                            if type(quad) == tuple:
                                for each_quad in quad:
                                    if type(quad_config) == tuple and each_quad in quad_config:
                                        quad_config_value = self.patient_pack_slot_quad_config_dict[patient][
                                            drug_details["pack_id"]][
                                            drug_details["slot_number"]][quad_config]
                                    else:
                                        quad_config_value = self.patient_pack_slot_quad_config_dict[patient][
                                            drug_details["pack_id"]][
                                            drug_details["slot_number"]][each_quad]
                                    canister_slot_data_list.append((internal_slot, slot_id, drug_details["drop_number"],
                                                                    quad_config_value, qty))
                            else:
                                if type(quad_config) == tuple and quad in quad_config:
                                    quad_config_value = self.patient_pack_slot_quad_config_dict[patient][
                                        drug_details["pack_id"]][
                                        drug_details["slot_number"]][quad_config]
                                else:
                                    quad_config_value = self.patient_pack_slot_quad_config_dict[patient][
                                        drug_details["pack_id"]][
                                        drug_details["slot_number"]][quad]

                                canister_slot_data_list.append((internal_slot, slot_id, drug_details["drop_number"],
                                                                quad_config_value, qty))

                    canister_slot_details[canister] = canister_slot_data_list
                    self.canister_dest_details[canister] = self.canister_dest_data_dict[canister]
                self.patient_canister_data[patient] = canister_slot_details
                self.canister_slot_details.update(canister_slot_details)
                self.patient_canister_len[patient] = len(canister_slot_details)

        except Exception as e:
            logger.error("error in get_recommendation_data_for_device {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(
                f"Error in get_recommendation_data_for_device: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
            raise e

    def validate_quad_capacity_count(self, quad):
        """
        This function reset all quad capacity to initial capacity at the starting of patient iteration.
        :param quad:
        :return:
        """
        if self.quad_capacity_count[quad] > 20:
            for i in range(1, 5):
                self.quad_capacity_count[i] = self.quad_capacity_count[i] - self.quad_capacity_count_base[i]

    def modify_dictionaries(self, patient):
        """
        This function modifies dictionaries with modified data.
        :param patient:
        :return:
        """
        try:

            if patient not in self.patient_pack_column_drop_slot_quad_dict:
                self.patient_pack_column_drop_slot_quad_dict[patient] = OrderedDict()
            if patient not in self.patient_pack_slot_quad_config_dict:
                self.patient_pack_slot_quad_config_dict[patient] = OrderedDict()
            for pack, slot_drop_info in self.pack_slot_drop_info_dict.items():
                self.patient_pack_column_drop_slot_quad_dict[patient][pack] = OrderedDict()
                self.patient_pack_slot_quad_config_dict[patient][pack] = OrderedDict()
                for slot, drop_info in slot_drop_info.items():
                    column = settings.SLOT_COLUMN_ID[slot]
                    if slot not in self.patient_pack_slot_quad_config_dict[patient][pack]:
                        self.patient_pack_slot_quad_config_dict[patient][pack][slot] = OrderedDict()
                    if column not in self.patient_pack_column_drop_slot_quad_dict[patient][pack]:
                        self.patient_pack_column_drop_slot_quad_dict[patient][pack][column] = OrderedDict()
                    if drop_info['drop_number'] not in self.patient_pack_column_drop_slot_quad_dict[patient][pack][
                        column]:
                        self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                            drop_info['drop_number']] = OrderedDict()
                    if slot not in self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                        drop_info['drop_number']]:
                        self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                            drop_info['drop_number']][slot] = set()
                    self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                        drop_info['drop_number']][slot] = drop_info['quadrant']
                    config_id = deepcopy(drop_info['configuration_id'])
                    if type(drop_info['quadrant']) == tuple:
                        if pack not in self.pack_slot_multi_quadrant_dict.keys():
                            self.pack_slot_multi_quadrant_dict[pack] = dict()
                        self.pack_slot_multi_quadrant_dict[pack][slot] = set(drop_info['quadrant'])
                    else:
                        if pack in self.pack_slot_multi_quadrant_dict.keys():
                            if slot in self.pack_slot_multi_quadrant_dict[pack]:
                                self.pack_slot_multi_quadrant_dict[pack][slot] = {drop_info['quadrant']}
                    self.patient_pack_slot_quad_config_dict[patient][pack][slot][
                        drop_info['quadrant']] = config_id.pop() if type(config_id) == set else config_id

            for pack, slot_drop_info in self.pack_slot_drop_info_dict_manual.items():
                if pack not in self.patient_pack_column_drop_slot_quad_dict[patient]:
                    self.patient_pack_column_drop_slot_quad_dict[patient][pack] = OrderedDict()
                if pack not in self.patient_pack_slot_quad_config_dict[patient]:
                    self.patient_pack_slot_quad_config_dict[patient][pack] = OrderedDict()
                for slot, drop_info in slot_drop_info.items():
                    column = settings.SLOT_COLUMN_ID[slot]
                    if slot not in self.patient_pack_slot_quad_config_dict[patient][pack]:
                        self.patient_pack_slot_quad_config_dict[patient][pack][slot] = OrderedDict()
                    if column not in self.patient_pack_column_drop_slot_quad_dict[patient][pack]:
                        self.patient_pack_column_drop_slot_quad_dict[patient][pack][column] = OrderedDict()
                    if drop_info['drop_number'] not in self.patient_pack_column_drop_slot_quad_dict[patient][pack][
                        column]:
                        self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                            drop_info['drop_number']] = OrderedDict()
                    if slot not in self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                        drop_info['drop_number']]:
                        self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                            drop_info['drop_number']][slot] = set()
                    self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                        drop_info['drop_number']][slot] = drop_info['quadrant']
                    if type(drop_info['quadrant']) == tuple:
                        if pack not in self.pack_slot_multi_quadrant_dict.keys():
                            self.pack_slot_multi_quadrant_dict[pack] = dict()
                        self.pack_slot_multi_quadrant_dict[pack][slot] = set(drop_info['quadrant'])
                    else:
                        if pack in self.pack_slot_multi_quadrant_dict.keys():
                            if slot in self.pack_slot_multi_quadrant_dict[pack]:
                                self.pack_slot_multi_quadrant_dict[pack][slot] = {drop_info['quadrant']}
                    self.patient_pack_slot_quad_config_dict[patient][pack][slot][drop_info['quadrant']] = drop_info[
                        'configuration_id']

            for pack, column_drop_slot_quads in self.patient_pack_column_drop_slot_quad_dict[patient].items():
                # for pack, column_drop_slot_quads in pack_details.items():
                self.pack_column_quad_slots_dict[pack] = {}
                for column, drop_slot_quads in column_drop_slot_quads.items():
                    quad_slots = {}
                    self.pack_column_quad_slots_dict[pack][column] = {}
                    drop_slot_quads = OrderedDict(sorted(drop_slot_quads.items()))
                    for drop, slot_quads in drop_slot_quads.items():
                        for slot, quads in slot_quads.items():
                            if quads == None:
                                if quads not in quad_slots:
                                    quad_slots[quads] = []
                            elif type(quads) == tuple:
                                quads = sorted(quads)
                                quads = tuple(quads)
                                if quads not in quad_slots:
                                    quad_slots[quads] = []
                            else:
                                if quads not in quad_slots:
                                    quad_slots[quads] = []
                            quad_slots[quads].append((slot, drop))
                    self.pack_column_quad_slots_dict[pack][column] = quad_slots

            # for pack, slot_drug_qty in self.pack_slot_drug_qty_dict.items():
            #     if pack not in self.patient_pack_column_drop_slot_quad_dict[patient]:
            #         continue
            #     pack_slot_total_quantity_dict[pack] = {}
            #     for slot, drug_qty in slot_drug_qty.items():
            #         pack_slot_total_quantity_dict[pack][slot] = 0
            #         for qty in drug_qty.values():
            #             pack_slot_total_quantity_dict[pack][slot] += qty

        except Exception as e:
            logger.error("Exception in modify_dictionaries {}".format(e))

    def modify_dictionary_multi_quad(self, patient, pack, slot_quad_dict, slot_quad_config_dict):
        """

        @param patient:
        @param pack:
        @param slot_quad_dict:
        @param slot_quad_config_dict:
        """
        # if patient not in self.patient_pack_column_drop_slot_quad_dict:
        #     self.patient_pack_column_drop_slot_quad_dict[patient] = OrderedDict()
        # if patient not in  self.patient_pack_slot_quad_config_dict:
        #     self.patient_pack_slot_quad_config_dict[patient] = OrderedDict()
        # for pack, slot_drop_info in self.pack_slot_drop_info_dict_manual.items():
        #     if pack not in self.patient_pack_column_drop_slot_quad_dict[patient]:
        #         self.patient_pack_column_drop_slot_quad_dict[patient][pack] = OrderedDict()
        #     if pack not in self.patient_pack_slot_quad_config_dict[patient]:
        #         self.patient_pack_slot_quad_config_dict[patient][pack] = OrderedDict()
        try:
            for patient1, pack_slot_data in self.patient_pack_column_drop_slot_quad_dict.items():
                if patient1 != patient:
                    continue
                for pack1, column_drop_slot in pack_slot_data.items():
                    if pack1 != pack:
                        continue
                    for column, drop_slot in column_drop_slot.items():
                        for drop, slots in drop_slot.items():
                            for slot1 in slots:
                                if slot1 not in slot_quad_dict:
                                    continue
                                self.patient_pack_column_drop_slot_quad_dict[patient][pack][column][
                                    drop][slot1] = slot_quad_dict[slot1]
                                quads = slot_quad_dict[slot1]
                                # ask meet for changes
                                # for quad in quads:
                                self.patient_pack_slot_quad_config_dict[patient][pack1][slot1][quads] = \
                                    slot_quad_config_dict[slot1][quads]

            for pack, column_drop_slot_quads in self.patient_pack_column_drop_slot_quad_dict[patient].items():
                # for pack, column_drop_slot_quads in pack_details.items():
                self.pack_column_quad_slots_dict[pack] = {}
                for column, drop_slot_quads in column_drop_slot_quads.items():
                    quad_slots = {}
                    self.pack_column_quad_slots_dict[pack][column] = {}
                    drop_slot_quads = OrderedDict(sorted(drop_slot_quads.items()))
                    for drop, slot_quads in drop_slot_quads.items():
                        for slot, quads in slot_quads.items():
                            if quads == None:
                                if quads not in quad_slots:
                                    quad_slots[quads] = []
                            # condition for set added temp
                            elif type(quads) == tuple or type(quads) == set:
                                quads = sorted(quads)
                                quads = tuple(quads)
                                if quads not in quad_slots:
                                    quad_slots[quads] = []
                            else:
                                if quads not in quad_slots:
                                    quad_slots[quads] = []
                            quad_slots[quads].append((slot, drop))
                    self.pack_column_quad_slots_dict[pack][column] = quad_slots

        except Exception as e:
            logger.error("error in modify_dictionary_multi_quad {}".format(e))
            raise e

    def get_recommendation_data_for_patient(self, device, patient):
        """
        This function is for making the mfd slot wise data based on slot drug qty for all the packs of current patient.
        For each column, we make data of each mfd column that mfd slot can have which drug and how much qty and if slot qty is more than 4 pill then distribute it.
        :param device:
        :param patient:
        :return:
        """

        base_drug_list_with_qty = []
        column_quad_slot_drug_list_with_qty = OrderedDict()
        column_independent_flag_dict = {}

        try:
            for pack, drop_slot_info in self.patient_pack_column_drop_slot_quad_dict[patient].items():
                if pack not in self.device_ordered_packs_dict[device]:
                    continue

                if pack in self.pack_slot_multi_quadrant_dict:
                    # If any pack have slot can be filled from multiple quadrant then fix the quad for mfd.
                    self.temp_canister_id_count = deepcopy(self.canister_id_count)
                    slot_quad_dict, slot_quad_config_dict = self.allocate_multi_quad(patient, pack,
                                                                                     self.pack_slot_multi_quadrant_dict[
                                                                                         pack])
                    self.modify_dictionary_multi_quad(patient, pack, slot_quad_dict, slot_quad_config_dict)
                for column, quad_info in self.pack_column_quad_slots_dict[pack].items():
                    if column not in column_quad_slot_drug_list_with_qty:
                        column_quad_slot_drug_list_with_qty[column] = {}
                    for quad, slot_list in quad_info.items():
                        slot_drug_list_with_qty = []
                        if quad not in column_quad_slot_drug_list_with_qty[column]:
                            column_quad_slot_drug_list_with_qty[column][quad] = []
                        for slot_drop in slot_list:
                            used_drugs = []
                            # This below code find total qty and split if qty more than 4.
                            if slot_drop[0] in self.pack_slot_total_quantity_dict[pack]:
                                total_slot_qty = self.pack_slot_total_quantity_dict[pack][slot_drop[0]]
                                req_no_of_canister_slots = math.ceil(total_slot_qty / settings.MFD_CANISTER_SLOTS)
                                ideal_qty_per_slot = math.ceil(total_slot_qty / req_no_of_canister_slots)
                                total_filled_qty = 0
                                for i in range(req_no_of_canister_slots):
                                    filled_qty = 0
                                    drug_qty_list = []
                                    for drug, qty in self.pack_slot_drug_qty_dict[pack][slot_drop[0]].items():
                                        if drug in used_drugs:
                                            continue
                                        if qty + filled_qty <= ideal_qty_per_slot:
                                            drug_tuple = (drug, qty)
                                            self.pack_slot_drug_qty_dict[pack][slot_drop[0]][drug] -= qty
                                            filled_qty += qty
                                            total_filled_qty += qty
                                            used_drugs.append(drug)
                                            drug_qty_list.append(drug_tuple)
                                        else:
                                            qty_to_fill = ideal_qty_per_slot - filled_qty
                                            # qty_to_fill = qty
                                            drug_tuple = (drug, qty_to_fill)
                                            self.pack_slot_drug_qty_dict[pack][slot_drop[0]][drug] -= qty_to_fill
                                            filled_qty += qty_to_fill
                                            total_filled_qty += qty_to_fill
                                            drug_qty_list.append(drug_tuple)
                                        if filled_qty >= ideal_qty_per_slot or total_filled_qty == total_slot_qty:
                                            slot_drug_list_with_qty.append(
                                                (pack, slot_drop[0], drug_qty_list, slot_drop[1]))
                                            base_drug_list_with_qty.append(slot_drug_list_with_qty)
                                            break
                        column_quad_slot_drug_list_with_qty[column][quad].extend(slot_drug_list_with_qty)
                column_quad_slot_drug_list_with_qty_copy = deepcopy(column_quad_slot_drug_list_with_qty)
                # column_quad_slot_drug_list_with_qty[column][quad].extend(slot_drug_list_with_qty)

            column_quad_slot_drug_list_with_qty = column_quad_slot_drug_list_with_qty_copy
            for column, quad_info in column_quad_slot_drug_list_with_qty.items():
                column_independent_flag_dict[column] = {}
                # This dict is for decision making if we can fill splited slots in single canister or make separate
                # canister.
                for quad, slot_drug_list_with_qty in quad_info.items():
                    column_independent_flag_dict[column][quad] = True
                    # This below condition checks that if we separate out canisters then it will have 1 filled slot
                    # and 3 empty slots if this type of case happened then we will not allow to make separate
                    # canister so make flag false. (pack1,slot1),(pack1,slot1),(pack2,slot2),(pack2,slot2) we will
                    # not make separate canister for this. It should have only one canister
                    if len(slot_drug_list_with_qty) / len(
                            self.patient_pack_column_drop_slot_quad_dict[patient]) == 2 and len(
                        self.patient_pack_column_drop_slot_quad_dict[patient]) == 2:
                        column_independent_flag_dict[column][quad] = False
            return column_quad_slot_drug_list_with_qty, column_independent_flag_dict

        except Exception as e:
            logger.info("error in  get_recommendation_data_for_patient {}".format(e))
            logger.info("patient: ", patient)
            raise e

    @log_args_and_response
    def fill_data_for_auto_slot_packs(self, robot):
        """
        This function makes data for saving auto slots pack.
        :param df:
        :param robot_cluster_drug_dict:
        :param drug_canister_info_dict:
        :return:
        """
        self.used_canisters = set()
        pack_drug_canister_robot_dict = {}
        try:

            for pack, slot_details in self.pack_slot_drug_dict_global.items():
                logger.info("fill_data_for_auto_slot_packs data {}, {}".format(pack, slot_details))
                if pack not in self.pack_slot_drop_info_dict:
                    continue
                pack_drug_canister_robot_dict[pack] = []
                for slot, drugs in slot_details.items():
                    # slot_id = self.pack_slot_detail_drug_dict[pack][slot]
                    # drug_used = False
                    # for robot in robot_quadrant_drug_distribution_dict:
                    for drug in drugs:
                        """
                        Manual drug condition
                        """
                        if drug in self.robot_half_pill_drug_pack_dict[robot]:
                            if pack in self.robot_half_pill_drug_pack_dict[robot][drug]:
                                continue
                        slot_id = self.pack_drug_slot_number_slot_id_dict[pack][drug][slot]
                        if drug not in self.robot_drugs_dict[robot]:
                            pack_drug_canister_robot_dict[pack].append([drug, None, None, None, slot_id, None, None])
                            continue

                        if slot not in self.pack_slot_drop_info_dict[pack].keys():
                            pack_drug_canister_robot_dict[pack].append([drug, None, None, None, slot_id, None, None])
                            continue

                        quadrant_details = self.pack_slot_drop_info_dict[pack][slot]
                        drug_used = False
                        if type(quadrant_details['quadrant']) == tuple:
                            quadrants = list(quadrant_details['quadrant'])
                        else:
                            quadrants = list(map(int, list(str(quadrant_details['quadrant']))))

                        if len(quadrant_details['configuration_id']) > 1:
                            quad = self.pack_slot_drug_quad_id_dict[pack][slot][drug]
                            conf_id = self.pack_slot_drug_config_id_dict[pack][slot][drug]
                            if drug in self.robot_quadrant_drug_data[robot][quad]['drugs']:
                                if (drug_used is True):
                                    break
                                if drug in self.robot_quadrant_drug_canister_dict[robot][quad]:
                                    canister_id = next(iter(self.robot_quadrant_drug_canister_dict[robot][quad][drug]))
                                    pack_drug_canister_robot_dict[pack].append(
                                        [drug, canister_id, robot, quad, slot_id, quadrant_details['drop_number'],
                                         {conf_id}])
                                    # self.used_canisters.add(canister_id)
                                else:
                                    pack_drug_canister_robot_dict[pack].append(
                                        [drug, None, None, None, slot_id, None, None])
                                drug_used = True
                            else:
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                                drug_used = True
                            continue

                        for quad in quadrants:
                            if drug in self.robot_quadrant_drug_data[robot][quad]['drugs']:
                                if (drug_used is True):
                                    break

                                if drug in self.robot_quadrant_drug_canister_dict[robot][quad]:
                                    canister_id = next(iter(self.robot_quadrant_drug_canister_dict[robot][quad][drug]))
                                    pack_drug_canister_robot_dict[pack].append(
                                        [drug, canister_id, robot, quad, slot_id, quadrant_details['drop_number'],
                                         quadrant_details['configuration_id']])
                                    # self.used_canisters.add(canister_id)
                                else:
                                    pack_drug_canister_robot_dict[pack].append(
                                        [drug, None, None, None, slot_id, None, None])
                                drug_used = True

            return pack_drug_canister_robot_dict

        except Exception as e:
            logger.error("Exception in fill_data_for_auto_slot_packs {}".format(e))
            raise e

    def allocate_quadrants(self, column, slots):
        """
        This function allocates quadrants to fully manual slots according to quadrant canister capacity.
        :param column:
        :param slots:
        :return:
        """
        slots = sorted(slots, reverse=True)
        quad_capacity_count_copy = deepcopy(self.quad_capacity_count_copy)
        base_quad_capacity_count = deepcopy(self.quad_capacity_count_copy)
        canister_id_count = deepcopy(self.temp_canister_id_count)
        base_canister_count = deepcopy(self.canister_id_count)
        slot_quad_dict = OrderedDict()
        slot_count = 0
        current_quad = 0

        # Sort quad capacity.
        sorted_quad_cap_count = OrderedDict(sorted(quad_capacity_count_copy.items(), key=lambda kv: kv[1]))

        for count, slot in enumerate(slots):
            if slot_count >= 1 and slot_count < 4:
                slot_quad_dict[slot] = current_quad
                slot_count += 1
                if slot_count == 4 or count == (len(slots) - 1):
                    # Canister count increases if slot_count reaches to 4 or slots are finished.
                    slot_count = 0
                    canister_id_count += 1
                    sorted_quad_cap_count[current_quad] += 1
                    sorted_quad_cap_count = OrderedDict(sorted(sorted_quad_cap_count.items(), key=lambda kv: kv[1]))
                    if sorted_quad_cap_count[current_quad] > 20:
                        # This condition checks if capacity exceeds 20 and if yes then reset all quad capacity
                        for quad, cnt in sorted_quad_cap_count.items():
                            sorted_quad_cap_count[quad] -= self.quad_capacity_count_base[quad]
                continue
            if len(self.valid_slot_quadrant[slot]) < 4:
                # This condition is for if we have hardware limitations on slot_quad then we will select only from those quadrants.
                possible_set = self.valid_slot_quadrant[slot]
                quad_list = list(possible_set)
                if len(quad_list) > 1:
                    if sorted_quad_cap_count[quad_list[0]] <= sorted_quad_cap_count[quad_list[1]] and \
                            sorted_quad_cap_count[quad_list[0]] < 20:
                        current_quad = quad_list[0]
                        slot_quad_dict[slot] = current_quad
                        slot_count += 1
                    # elif sorted_quad_cap_count[quad_list[1]] < 20:
                    else:
                        current_quad = quad_list[1]
                        slot_quad_dict[slot] = current_quad
                        slot_count += 1
                else:
                    current_quad = quad_list[0]
                    slot_quad_dict[slot] = current_quad
                    slot_count += 1
            else:
                # Pick min capacity quadrant for normal slots(no hardware limitations)
                current_quad = list(sorted_quad_cap_count.items())[0][0]
                slot_quad_dict[slot] = current_quad
                slot_count += 1
        self.temp_canister_id_count = deepcopy(canister_id_count)
        self.quad_capacity_count_copy = deepcopy(dict(sorted_quad_cap_count))
        return slot_quad_dict

    def allocate_multi_quad(self, patient, pack, slot_multi_quad):
        """

        @param patient:
        @param pack:
        @param slot_multi_quad:
        @return:
        """
        try:
            slots = sorted(list(slot_multi_quad.keys()), reverse=True)
            quad_capacity_count_copy = deepcopy(self.quad_capacity_count)
            base_quad_capacity_count = deepcopy(self.quad_capacity_count)
            canister_id_count = deepcopy(self.temp_canister_id_count)
            base_canister_count = deepcopy(self.canister_id_count)
            slot_quad_dict = OrderedDict()
            slot_quad_config_dict = OrderedDict()
            slot_count = 0
            current_quad = 0

            sorted_quad_cap_count = OrderedDict(sorted(quad_capacity_count_copy.items(), key=lambda kv: kv[1]))
            for count, slot in enumerate(slots):
                slot_quad_config_dict[slot] = {}
                if slot_count >= 1 and slot_count < 4:
                    for quad in sorted_quad_cap_count.keys():
                        if quad in slot_multi_quad[slot]:
                            # current_quad = list(sorted_quad_cap_count.items())[0][0]
                            quadrant = list(self.patient_pack_slot_quad_config_dict[patient][pack][slot].keys())
                            for each_quad in quadrant:
                                if type(each_quad) == tuple and quad in each_quad:
                                    quadrant_1 = each_quad
                                else:
                                    quadrant_1 = quad
                            slot_quad_dict[slot] = quad
                            del self.patient_pack_slot_quad_config_dict[patient][pack][slot][quadrant_1]
                            self.patient_pack_slot_quad_config_dict[patient][pack][slot][quad] = \
                                settings.SLOT_QUAD_CONFIG_DICT[slot][quad]
                            slot_quad_config_dict[slot][quad] = \
                                settings.SLOT_QUAD_CONFIG_DICT[slot][quad]
                            slot_count += 1
                            current_quad = quad
                            break
                    slot_quad_dict[slot] = current_quad
                    quadrant = list(self.patient_pack_slot_quad_config_dict[patient][pack][slot].keys())
                    slot_quad_config_dict[slot][current_quad] = \
                        settings.SLOT_QUAD_CONFIG_DICT[slot][current_quad]
                    del self.patient_pack_slot_quad_config_dict[patient][pack][slot][quadrant[0]]
                    self.patient_pack_slot_quad_config_dict[patient][pack][slot][current_quad] = \
                        settings.SLOT_QUAD_CONFIG_DICT[slot][current_quad]
                    slot_count += 1
                    if slot_count == 4 or count == (len(slots) - 1):
                        slot_count = 0
                        canister_id_count += 1
                        sorted_quad_cap_count[current_quad] += 1
                        sorted_quad_cap_count = OrderedDict(sorted(sorted_quad_cap_count.items(), key=lambda kv: kv[1]))
                        if sorted_quad_cap_count[current_quad] > 20:
                            for quad, cnt in sorted_quad_cap_count.items():
                                sorted_quad_cap_count[quad] -= base_quad_capacity_count[quad]
                    continue
                # if len(slot_quadrant[slot]) < 4:
                #     possible_set = self.valid_slot_quadrant[slot]
                #     quad_list = list(possible_set)
                #     if len(quad_list) > 1:
                #         if sorted_quad_cap_count[quad_list[0]] < sorted_quad_cap_count[quad_list[1]] and \
                #                 sorted_quad_cap_count[quad_list[0]] < 20:
                #             current_quad = quad_list[0]
                #             slot_quad_dict[slot] = current_quad
                #             slot_count += 1
                #         elif sorted_quad_cap_count[quad_list[1]] < 20:
                #             current_quad = quad_list[1]
                #             slot_quad_dict[slot] = current_quad
                #             slot_count += 1
                #     else:
                #         current_quad = quad_list[0]
                #         slot_quad_dict[slot] = current_quad
                #         slot_count += 1
                # else:
                for quad in sorted_quad_cap_count.keys():
                    if quad in slot_multi_quad[slot]:
                        # current_quad = list(sorted_quad_cap_count.items())[0][0]
                        slot_quad_dict[slot] = quad
                        quadrant = list(self.patient_pack_slot_quad_config_dict[patient][pack][slot].keys())
                        for each_quad in quadrant:
                            if type(each_quad) == tuple and quad in each_quad:
                                quadrant_1 = each_quad
                            else:
                                quadrant_1 = quad
                        del self.patient_pack_slot_quad_config_dict[patient][pack][slot][quadrant_1]
                        self.patient_pack_slot_quad_config_dict[patient][pack][slot][quad] = \
                            settings.SLOT_QUAD_CONFIG_DICT[slot][quad]

                        slot_quad_config_dict[slot][quad] = \
                            settings.SLOT_QUAD_CONFIG_DICT[slot][quad]
                        slot_count += 1
                        current_quad = quad
                        break
            self.temp_canister_id_count = deepcopy(canister_id_count)
            self.quad_capacity_count = deepcopy(dict(sorted_quad_cap_count))
            return slot_quad_dict, slot_quad_config_dict

        except Exception as e:
            logger.error("error in allocate_multi_quad: ", e)
            logger.error("patient: ", patient, ", pack: ", pack)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.info(
                f"Error in add_canister_testing_data: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
            raise e

    def save_analysis(self, analysis):
        """
        Store pack-drug and canister-robot allocation in database
        Returns batch id and analysis data

        :param analysis (dict): {pack_id: (fndc_txr, canister_id, robot_id),}
        :param pack_manual (dict): whether pack is manual due to half pills {pack_id: bool,}
        :param canister_data (dict): {canister_id: {...},}
        :param drug_data:
        :param batch_id:
        :param batch_list: list of packs in a batch
        :param re_run: bool flag to indicate re_run, removes older analysis
        :param user_id: User ID
        :param full_manual_pack_drug: (pack, drug) which have only 0.5 qty in all slots
        :return: int, list
        """
        try:
            pack_list = list()
            analysis_data = list()
            logger.info('here')
            # canister_data[None] = {"drug_id": None, "canister_number": None}  # default response for None canister id
            robot_id = None
            for pack, drugs in analysis.items():
                # create analysis data to store in db
                pack_data = dict()
                pack_list.append(pack)
                pack_data["pack_id"] = pack
                pack_data["manual_fill_required"] = 1
                pack_data.setdefault('ndc_list', [])
                for item in drugs:
                    drug = {}
                    canister_id = item[1]
                    drug["canister_id"] = canister_id
                    drug["device_id"] = item[2]
                    drug["location_number"] = None
                    drug["quadrant"] = item[3]
                    drug["slot_id"] = item[4]
                    drug["drop_number"] = item[5]
                    drug["config_id"] = item[6]

                    pack_data['ndc_list'].append(drug)
                analysis_data.append(pack_data)

            return analysis_data

        except (InternalError, IntegrityError) as e:
            logger.error("Error in save analysis {}".format(e))
            raise

    def save_analysis_mfd(self):
        """
        This function makes data for saving in database.
        :return:
        """
        analysis_data = []
        canister_data = {}
        canister_analysis = {}

        for canister, canister_slot_data_list in self.canister_slot_details.items():
            canister_analysis['canister'] = canister
            canister_analysis['desired_device_id'] = self.canister_dest_details[canister]['device_id']
            canister_analysis['desired_quadrant'] = self.canister_dest_details[canister]['quadrant']
            # canister_analysis['assigned_user_id'] = self.canister_dest_details[canister]['assigned_user_id']
            canister_analysis['order_no'] = canister
            canister_analysis['batch_id'] = self.batch_id
            canister_analysis['status'] = src.constants.MFD_CANISTER_PENDING_STATUS
            canister_analysis['canister_slot_data'] = []
            for item in canister_slot_data_list:
                canister_data['mfd_can_slot_number'] = item[0]
                canister_data['drop_number'] = item[2]
                canister_data['config_id'] = item[3]
                canister_data['slot_id'] = item[1]
                canister_data['quantity'] = item[4]
                canister_data['status_id'] = src.constants.MFD_DRUG_PENDING_STATUS
                canister_analysis['canister_slot_data'].append(deepcopy(canister_data))
            analysis_data.append(deepcopy(canister_analysis))
        return analysis_data


@log_args_and_response
def save_recommendation_analysis(recom_analysis, auto_packs_response, auto_packs_list, batch_id, mfd_slots, user_id):
    """
    This function saves MFD Recommendation data to MFD_analysis and MFD_analysis_details.
    @param recom_analysis:
    @param mfd_slots:
    @param batch_id:
    @param user_id:
    @param auto_packs_list:
    @param auto_packs_response:
    """
    try:
        logger.debug("save_recommendation_analysis")
        with db.transaction():
            if len(auto_packs_list) != 0:
                db_delete_pack_analysis_by_packs(auto_packs_list)
                db_save_analysis(auto_packs_response, batch_id, mfd_slots)
            db_delete_pack_analysis_details_slots(list(mfd_slots))

            detailed_list = list()
            canister_analysis = dict()
            canister_data = dict()
            logger.info("mfd analysis data {}, {}".format(recom_analysis, batch_id))
            for analysis in recom_analysis:
                if type(analysis['desired_quadrant']) == tuple:
                    for each_quad in analysis['desired_quadrant']:
                        canister_analysis['dest_device_id'] = analysis['desired_device_id']
                        canister_analysis['dest_quadrant'] = each_quad
                        canister_analysis['batch_id'] = analysis['batch_id']
                        canister_analysis['status_id'] = analysis['status']
                        canister_analysis['created_by'] = user_id
                        canister_analysis['modified_by'] = user_id
                        analysis_record = add_mfd_analysis_data(data_dict=canister_analysis)
                        for canister_details in analysis['canister_slot_data']:
                            canister_data['analysis_id'] = analysis_record.id
                            canister_data['mfd_can_slot_no'] = canister_details['mfd_can_slot_number']
                            canister_data['drop_number'] = canister_details['drop_number']
                            canister_data['config_id'] = canister_details['config_id']
                            canister_data['slot_id'] = canister_details['slot_id']
                            canister_data['quantity'] = canister_details['quantity']
                            canister_data['status_id'] = canister_details['status_id']
                            canister_data['created_by'] = user_id
                            canister_data['modified_by'] = user_id
                            detailed_list.append(deepcopy(canister_data))
                else:
                    canister_analysis['dest_device_id'] = analysis['desired_device_id']
                    canister_analysis['dest_quadrant'] = analysis['desired_quadrant']
                    canister_analysis['batch_id'] = analysis['batch_id']
                    canister_analysis['status_id'] = analysis['status']
                    canister_analysis['created_by'] = user_id
                    canister_analysis['modified_by'] = user_id
                    analysis_record = add_mfd_analysis_data(data_dict=canister_analysis)
                    for canister_details in analysis['canister_slot_data']:
                        canister_data['analysis_id'] = analysis_record.id
                        canister_data['mfd_can_slot_no'] = canister_details['mfd_can_slot_number']
                        canister_data['drop_number'] = canister_details['drop_number']
                        canister_data['config_id'] = canister_details['config_id']
                        canister_data['slot_id'] = canister_details['slot_id']
                        canister_data['quantity'] = canister_details['quantity']
                        canister_data['status_id'] = canister_details['status_id']
                        canister_data['created_by'] = user_id
                        canister_data['modified_by'] = user_id
                        detailed_list.append(deepcopy(canister_data))

            if detailed_list:
                status = db_update_mfd_status(batch=batch_id, mfd_status=src.constants.MFD_BATCH_PENDING,
                                              user_id=1)
                analysis_details_record = add_mfd_analysis_details_data(data_dict=detailed_list)

                populate_data_in_frequent_mfd_drugs_table(batch_id=batch_id)
        logger.info(f"In save_recommendation_analysis, data populated in frequent_mfd_drugs table")

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in save_recommendation_analysis {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in save_recommendation_analysis: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def prepare_needed_data_structures(patient_pack_column_drop_slot_quad_dict, patient_pack_slot_quad_config_dict,
                                   pack_slot_drug_qty_dict=None):
    """
    This function is for making required data structure according to algorithm from base data structure for ease of use.
    :param patient_pack_column_drop_slot_quad_dict:
    :param patient_pack_slot_quad_config_dict:
    :param pack_slot_drug_qty_dict:
    :return:
    """
    if pack_slot_drug_qty_dict is None:
        pack_slot_drug_qty_dict = {}
    logger.debug("In prepare_needed_data_structures")
    pack_column_quad_slots_dict = {}
    pack_slot_total_quantity_dict = {}
    pack_slot_multi_quadrant_dict = {}
    alloted = False
    for pack_details in patient_pack_column_drop_slot_quad_dict.values():
        for pack, column_drop_slot_quads in pack_details.items():
            pack_column_quad_slots_dict[pack] = {}
            for column, drop_slot_quads in column_drop_slot_quads.items():
                quad_slots = {}
                pack_column_quad_slots_dict[pack][column] = {}
                drop_slot_quads = OrderedDict(sorted(drop_slot_quads.items()))
                for drop, slot_quads in drop_slot_quads.items():
                    for slot, quads in slot_quads.items():
                        if quads == None:
                            if quads not in quad_slots:
                                quad_slots[quads] = []
                        elif type(quads) == tuple:
                            quads = sorted(quads)
                            quads = tuple(quads)
                            if quads not in quad_slots:
                                quad_slots[quads] = []
                        else:
                            if quads not in quad_slots:
                                quad_slots[quads] = []
                        quad_slots[quads].append((slot, drop))
                pack_column_quad_slots_dict[pack][column] = quad_slots

    for pack, slot_drug_qty in pack_slot_drug_qty_dict.items():
        pack_slot_total_quantity_dict[pack] = {}
        for slot, drug_qty in slot_drug_qty.items():
            pack_slot_total_quantity_dict[pack][slot] = 0
            for qty in drug_qty.values():
                pack_slot_total_quantity_dict[pack][slot] += qty

    for patient, pack_slot_data in patient_pack_slot_quad_config_dict.items():
        for pack, slot_data in pack_slot_data.items():
            pack_slot_multi_quadrant_dict[pack] = {}
            for slot, quad_config in slot_data.items():
                pack_slot_multi_quadrant_dict[pack][slot] = set()
                if len(patient_pack_slot_quad_config_dict[patient][pack][slot]) > 1:
                    pack_slot_multi_quadrant_dict[pack][slot] = set(quad_config.keys())
                    alloted = True
            if not alloted:
                del pack_slot_multi_quadrant_dict[pack]

    return pack_column_quad_slots_dict, pack_slot_total_quantity_dict, pack_slot_multi_quadrant_dict


@log_args_and_response
def get_require_data_for_mfd(batch_id):
    """
    This function is for getting all required data from database for mfd recommendation algorithm for batch_id given in argument.
    :param batch_id:
    :return:
    """
    try:
        patient_pack_column_drop_slot_quad_dict, device_ordered_patients_dict, pack_slot_drug_qty_dict, \
        patient_pack_slot_quad_config_dict, patient_pack_column_manual_slots_dict, pack_list, \
        device_ordered_packs_dict = get_manual_drug_pack_info(
            batch_id)
        logger.info("Patient dicts created")
        # get zone id from batch
        system_id = get_system_id_from_batch_id(batch_id=batch_id)
        system_zone_mapping, zone_list = db_get_system_zone_mapping([system_id])
        zone_id = system_zone_mapping[system_id]

        robot_half_pill_drug_pack_dict = get_half_pill_drug_pack_data(batch_id=batch_id,
                                                                      device_ordered_packs_dict=device_ordered_packs_dict)

        pack_slot_drug_dict, pack_drug_slot_number_slot_id_dict, pack_slot_drug_dict_global = get_pack_slotwise_canister_drugs(
            pack_list, zone_id)
        logger.info("Packs and zone dicts created")
        robot_quadrant_drug_data, robot_quadrant_drug_canister_dict, robot_drug_dict = get_quadrant_drugs(batch_id)
        logger.info("robot data dicts created")
        return patient_pack_column_drop_slot_quad_dict, device_ordered_patients_dict, pack_slot_drug_qty_dict, \
               patient_pack_slot_quad_config_dict, patient_pack_column_manual_slots_dict, pack_slot_drug_dict, \
               pack_drug_slot_number_slot_id_dict, device_ordered_packs_dict, robot_quadrant_drug_data, \
               robot_quadrant_drug_canister_dict, robot_drug_dict, pack_slot_drug_dict_global, pack_list, \
               robot_half_pill_drug_pack_dict

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("Error in MFD recommendation get require data {}".format(e))
        raise
