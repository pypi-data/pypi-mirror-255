import json
from src.independentclusters import RecommendCanisterToAdd, RecommendCanistersToRemove, RecommendCanistersToTransfer,RecommendCanisterDistributionInQuadrants, RecommendPackDistributionAcrossSystems, RecommendCanisterDistributionAcrossSystems
from copy import deepcopy
import pandas as pd
import time
import logging
from src.dosepacker_preprocessing import CanisterRecommender
logger = logging.getLogger("cr")

def date_handler(obj):
    """
        @function: date_handler
        @createdBy: Manish Agarwal
        @createdDate: 7/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: date
        @purpose - Parse the date object to isoformat so that it
                    can be handled by json
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    else:
        return str(obj)

def append_dictionary_to_json_file(dict, dict_name, save_json, json_name):
    """
    This method will save(append) passed dictionary to json
    :return:
    """
    if save_json:
        dict_to_store = {dict_name: deepcopy(dict)}
        print ("dict to store", dict_to_store)
        # a = json.dumps(dict_to_store, default=date_handler)
        with open(json_name, 'a+') as fp:
            json.dump(dict_to_store, fp, default=date_handler)
    pass


class MultiSystemCanisterRecommender:
    """
    This class will provide given utilities.
    1) It will recommend canisters to add(register) for given data frame.
    2) It will recommend canisters to remove from the dosepacker.
    3) It will recommend canisters to transfer for achieving optimal distribution of packs to the robot.

    Glossary:-
    ------------
    1) Dataframe:-- Pandas data frame containing the list of drugs as columns and the list of packs as rows of a 2d
    Matrix.
    :::--- Instead of data frame we will want dataframe_info_dict for multi-system canister recommendation. Key of dictionary
    will be system_id and value will be dataframe.
    2) Robot_capacity_info_dict:-- Dictionary containing robot id as key and the maximum number of canisters it can
    accommodate as the value.
    3) Drug_canister_info_dict:-- Drug id as key, list of canister ids as value.
    4) canister_location_info_dict:-- canister id as key, tuple containing (robot_id, location_id) as value.
    If the canister is placed outside the robot, robot id will be None.
    5) list_of_canisters_to_add:-- The list of tuples, every tuple contains canister id as the first element and
    quantity(number of canisters to add for that drug) as the second element.
    6) canister_transfer_info_dict:--Dictionary, canister id as key, tuple of (src_robot_id,
    destination_robot_id) as value.
    7) Pack_robot_drug_info_dict:-- Dictionary, key = pack_id, value = {[(drug_id, canister_id, robot_id)]}
    8) Robot_free_location_info_dict:-- Dictionary, key = Robot_id, value = [free location id list]
    9) facility_pack_info_dict:-- facility id as key, pack ids as value
    10) system_robot_info_dict:-- system_id as key, robot id list as value
    11) system_division_info_dict:-- system_id as key, list of packs as value.
    """

    def __init__(self, file_name=None, df=None, dataframe_info_dict=None, pack_drug_manual_dict=None,
                 robot_capacity_info_dict=None, drug_canister_info_dict=None,
                 canister_location_info_dict=None, canister_expiry_status_dict=None, robot_free_location_info_dict=None,
                 facility_pack_info_dict=None,
                 system_robot_info_dict=None, system_division_info_dict=None, system_batchwise_df=None,
                 split_function_id=None, pack_slot_drug_dict=None,
                 multiple_canisters_drugs=None, drug_canister_count_dict=None, pack_slot_detail_drug_dict=None,
                 pack_drug_slot_id_dict=None, pack_drug_slot_number_slot_id_dict=None,
                 pack_drug_half_pill_slots_dict=None,
                 drug_quantity_dict=None, canister_qty_dict=None, drug_canister_usage=None, pack_delivery_date=None,
                 robot_quadrant_enable_locations=None):

        # Defining Variables
        self.file_name = file_name
        """
        The main df: 
        1. first we divide this dataframe according to number of systems(PackDistribution Class).
        2. Then It will be divided according to the main Independent Cluster Algorithm recursively.
        """
        self.df = df

        self.pack_slot_drug_dict = pack_slot_drug_dict
        self.multiple_canisters_drugs = multiple_canisters_drugs
        self.drug_canister_count_dict = drug_canister_count_dict
        self.pack_slot_detail_drug_dict = pack_slot_detail_drug_dict
        self.pack_drug_slot_number_slot_id_dict = pack_drug_slot_number_slot_id_dict
        self.pack_drug_half_pill_slots_dict = pack_drug_half_pill_slots_dict
        self.drug_quantity_dict = drug_quantity_dict
        self.canister_qty_dict = canister_qty_dict
        self.pack_delivery_date = pack_delivery_date
        '''
        dataframe_info_dict:
        It is derived from pack distribution across systems(N-systems --> N-distributions of packs)
        - each system_id: df
        - It is mainly used in canister transfer process for multiple systems, where the canister transfer is not limited to be transfered between same system.
        - Canisters can be transfered by any system, we just want to know the destination robot to put canister, because it doesn't matter where the canister is currently being processed.
        - We set aside canisters that are need to be processed in the next batch
        '''
        self.dataframe_info_dict = dataframe_info_dict

        # Capacity of each robot of containing max no of canister
        self.robot_capacity_info_dict = robot_capacity_info_dict
        '''
        drug_canister_info_dict:
        dict {drug_id: set of registered canisters} - canisters that are not in process right now, and available to be assigned to new robots
        i.e. If there are total 8 canisters registered for drug d, but 5 of the canisters are already in processing, then the drug canister will show 3 canisters that are free for that drug
        '''
        self.drug_canister_info_dict = drug_canister_info_dict
        self.drug_canister_usage = drug_canister_usage
        self.robot_quadrant_enable_locations = robot_quadrant_enable_locations

        '''
        canister_location_info_dict:
        dict {canister_id: tuple(robot_id, location_id)}: To see currently where our canister is placed(Either in one of the robots, or on the shelf)
        '''
        self.canister_location_info_dict = canister_location_info_dict
        self.canister_expiry_status_dict = canister_expiry_status_dict
        self.save_data_frame = False

        '''
        robot_free_location_info_dict:
        dict {robot_id: set(canister_id's)}: To see unused locations of canisters for each robot(which can be utilized for canister transfer from shelf to any robot)
        '''
        self.robot_free_location_info_dict = robot_free_location_info_dict

        '''
        Consider a facility as one hospital, we want to deliver set of packs to particular facility(assume all facilities are at different location), therefore we would like to process it by facilities
        rather than just by balancing packs on the robots.
        
        '''
        self.facility_pack_info_dict = facility_pack_info_dict
        self.system_robot_info_dict = system_robot_info_dict

        '''
        system_division_info_dict:
        canister transfer info, analysis for each system
        canister transfer: canister_id --> (source robot, destination robot) information; source can be 'None' if taken from shelf
        analysis: pack --> (drug id, canister id, robot id) info; 
        '''
        self.system_division_info_dict = system_division_info_dict

        '''
        pack_drug_manual_dict:
        List of drugs which are used in 1/2 quantity across all packs(that drug column in df is 0 for all packs, because we round it by integer)
        '''
        self.pack_drug_manual_dict = pack_drug_manual_dict

        self.split_function_id = split_function_id

        self.pack_drug_slot_id_dict = pack_drug_slot_id_dict

        '''
        system_batchwise_df:
        We used to follow a procedure before, in that we used to give the list of drugs canisters to register on daily basis. The reason to give this list of canister is to reduce the latency, because 
        the list of canisters(of drugs) to register will try to normalize the distribution between robots. 
        - One canister registration almost takes 30 mins. So user always tend to skip the procedure and proceed for further packing. In that case, we were not able to get higher throughput. Therefore, 
        we decided to give recommendation of registering canisters after 15 days(a cycle). For that, we are providing 15-dfs for each systems, i.e. total 30 dfs if there are 2 systems
        '''
        self.system_batchwise_df = system_batchwise_df
        if self.save_data_frame:
            # self.writer = pd.ExcelWriter('output.xlsx')
            self.df.to_csv('output.csv')
            # self.writer.save()
        pass

    def recommend_canister_to_add_batchwise(self):
        """
        It will recommend to register canister at end of every 15 days cycle
        :return:
        """

        self.system_priority_druglist_info_dict = {}
        self.batch_system_drug_info_dict = {}
        '''
        - Retrieve every seperate df from system_batchwise_df(i.e., total 30 df's for 2 systems, 15 df's for each system as per 15 days(one batch))
        - Store all priority drug-list for each 30 dfs into one dict: system_priority_druglist_info_dict(system-0: 15 lists, system-1: 15 lists)
        '''
        for system_id, list_df in self.system_batchwise_df.items():
            self.system_priority_druglist_info_dict[system_id] = []
            for i in range(len(list_df)):
                each_df = self.system_batchwise_df[system_id][i]

                self.rca = RecommendCanisterToAdd(file_name=self.file_name, df=each_df,
                                                  drug_canister_info_dict=self.drug_canister_info_dict)

                priority_drug_list, _ = self.rca.get_recommendation_to_add_canisters_truncated()
                self.system_priority_druglist_info_dict[system_id].append(priority_drug_list)

        # if all systems are not empty
        if not (all(len(priority_drug_list) is 0 for (system_id, priority_drug_list) in self.system_priority_druglist_info_dict.items())):

            # batchwise (system, set of drugs) dictionary
            self.batch_system_drug_info_dict = self.rca.fill_batch_system_drug_info_dict(self.system_batchwise_df)

            # 1. all drugs of the batch, 2. (drug, list of systems where the drug is used) dictionary
            self.batch_all_drugs, self.drug_system_info_dict = self.rca.fill_drug_system_info_dict(self.batch_system_drug_info_dict)

            # gives list of(prioritywise) drug tuple which contains (drug, required no. of canisters) as a tuple
            self.drug_required_canister_list = self.rca.process_system_priority_druglist_info_dict(self.system_priority_druglist_info_dict, self.batch_system_drug_info_dict)

            # with information of required canisters and available canister for that drug, suggests no. of canisters that are needed to be registered for drugs(priority-wise)
            self.batchwise_drug_list_of_tuple = self.rca.generate_drug_list_of_tuple_multisystem(self.drug_required_canister_list, self.drug_canister_info_dict)
        else:
            self.batchwise_drug_list_of_tuple = []

        return self.batchwise_drug_list_of_tuple

    def multi_robot_recommend_canister_to_add_batchwise(self):
        """
        It will recommend to register canister at end of every 15 days cycle
        :return:
        """

        self.system_priority_druglist_info_dict = {}
        self.batch_system_drug_info_dict = {}
        '''
        - Retrieve every seperate df from system_batchwise_df(i.e., total 30 df's for 2 systems, 15 df's for each system as per 15 days(one batch))
        - Store all priority drug-list for each 30 dfs into one dict: system_priority_druglist_info_dict(system-0: 15 lists, system-1: 15 lists)
        '''
        for system_id, list_df in self.system_batchwise_df.items():
            self.system_priority_druglist_info_dict[system_id] = []
            for i in range(len(list_df)):
                each_df = self.system_batchwise_df[system_id][i]
                systemwise_robot = self.system_robot_info_dict[system_id]
                self.rca = RecommendCanisterToAdd(file_name=self.file_name, df=each_df,
                                                  drug_canister_info_dict=self.drug_canister_info_dict, robot_list=systemwise_robot)

                priority_drug_list,priority_drug_dict, _ = self.rca.get_recommendation_to_add_canisters_truncated()
                self.system_priority_druglist_info_dict[system_id].append(priority_drug_list)

        # if all systems are not empty
        if not (all(len(priority_drug_list) is 0 for (system_id, priority_drug_list) in self.system_priority_druglist_info_dict.items())):

            # batchwise (system, set of drugs) dictionary
            self.batch_system_drug_info_dict = self.rca.fill_batch_system_drug_info_dict(self.system_batchwise_df)

            # 1. all drugs of the batch, 2. (drug, list of systems where the drug is used) dictionary
            self.batch_all_drugs, self.drug_system_info_dict = self.rca.fill_drug_system_info_dict(self.batch_system_drug_info_dict)

            # gives list of(prioritywise) drug tuple which contains (drug, required no. of canisters) as a tuple
            self.drug_required_canister_list = self.rca.process_system_priority_druglist_info_dict(self.system_priority_druglist_info_dict, self.batch_system_drug_info_dict)

            # with information of required canisters and available canister for that drug, suggests no. of canisters that are needed to be registered for drugs(priority-wise)
            self.batchwise_drug_list_of_tuple = self.rca.generate_drug_list_of_tuple_multisystem(self.drug_required_canister_list, self.drug_canister_info_dict)
        else:
            self.batchwise_drug_list_of_tuple = []

        return self.batchwise_drug_list_of_tuple,priority_drug_dict



    def multi_robot_recommend_canister_to_add_batchwise_with_priority(self):
        """
        It will recommend to register canister at end of every 15 days cycle
        :return:
        """

        self.system_priority_druglist_info_dict = {}
        self.batch_system_drug_info_dict = {}
        '''
        - Retrieve every seperate df from system_batchwise_df(i.e., total 30 df's for 2 systems, 15 df's for each system as per 15 days(one batch))
        - Store all priority drug-list for each 30 dfs into one dict: system_priority_druglist_info_dict(system-0: 15 lists, system-1: 15 lists)
        '''
        for system_id, list_df in self.system_batchwise_df.items():
            self.system_priority_druglist_info_dict[system_id] = []
            for i in range(len(list_df)):
                each_df = self.system_batchwise_df[system_id][i]
                systemwise_robot = self.system_robot_info_dict[system_id]
                self.rca = RecommendCanisterToAdd(file_name=self.file_name, df=each_df,
                                                  drug_canister_info_dict=self.drug_canister_info_dict, robot_list=systemwise_robot)

                priority_drug_list,priority_drug_dict, _ = self.rca.get_recommendation_to_add_canisters_truncated_with_priority()
                self.system_priority_druglist_info_dict[system_id].append(priority_drug_list)

        # if all systems are not empty
        if not (all(len(priority_drug_list) is 0 for (system_id, priority_drug_list) in self.system_priority_druglist_info_dict.items())):

            # batchwise (system, set of drugs) dictionary
            self.batch_system_drug_info_dict = self.rca.fill_batch_system_drug_info_dict(self.system_batchwise_df)

            # 1. all drugs of the batch, 2. (drug, list of systems where the drug is used) dictionary
            self.batch_all_drugs, self.drug_system_info_dict = self.rca.fill_drug_system_info_dict(self.batch_system_drug_info_dict)

            # gives list of(prioritywise) drug tuple which contains (drug, required no. of canisters) as a tuple
            self.drug_required_canister_list = self.rca.process_system_priority_druglist_info_dict(self.system_priority_druglist_info_dict, self.batch_system_drug_info_dict)

            # with information of required canisters and available canister for that drug, suggests no. of canisters that are needed to be registered for drugs(priority-wise)
            self.batchwise_drug_list_of_tuple = self.rca.generate_drug_list_of_tuple_multisystem(self.drug_required_canister_list, self.drug_canister_info_dict)
        else:
            self.batchwise_drug_list_of_tuple = []

        return self.batchwise_drug_list_of_tuple,priority_drug_dict


    def multi_robot_recommend_canister_to_add_batchwise_optimised(self,number_of_drugs_needed,drugs_to_register):
        """
        It will recommend to register canister at end of every 15 days cycle
        :return:
        """

        self.system_priority_druglist_info_dict = {}
        self.batch_system_drug_info_dict = {}
        '''
        - Retrieve every seperate df from system_batchwise_df(i.e., total 30 df's for 2 systems, 15 df's for each system as per 15 days(one batch))
        - Store all priority drug-list for each 30 dfs into one dict: system_priority_druglist_info_dict(system-0: 15 lists, system-1: 15 lists)
        '''
        priority_drug_dict = {}
        for system_id, list_df in self.system_batchwise_df.items():
            self.system_priority_druglist_info_dict[system_id] = []
            for i in range(len(list_df)):
                each_df = self.system_batchwise_df[system_id][i]
                systemwise_robot = self.system_robot_info_dict[system_id]
                self.rca = RecommendCanisterToAdd(file_name=self.file_name, df=each_df,
                                                  drug_canister_info_dict=self.drug_canister_info_dict, robot_list=systemwise_robot)

                default_split,priority_drug_dict,priority_drug_list = self.rca.get_recommendation_to_add_canisters_truncated_optimised(number_of_drugs_needed,drugs_to_register)
                self.system_priority_druglist_info_dict[system_id].append(priority_drug_list)

        # if all systems are not empty
        if not (all(len(priority_drug_list) is 0 for (system_id, priority_drug_list) in self.system_priority_druglist_info_dict.items())):

            # batchwise (system, set of drugs) dictionary
            self.batch_system_drug_info_dict = self.rca.fill_batch_system_drug_info_dict(self.system_batchwise_df)

            # 1. all drugs of the batch, 2. (drug, list of systems where the drug is used) dictionary
            self.batch_all_drugs, self.drug_system_info_dict = self.rca.fill_drug_system_info_dict(self.batch_system_drug_info_dict)

            # gives list of(prioritywise) drug tuple which contains (drug, required no. of canisters) as a tuple
            self.drug_required_canister_list = self.rca.process_system_priority_druglist_info_dict(self.system_priority_druglist_info_dict, self.batch_system_drug_info_dict)

            # with information of required canisters and available canister for that drug, suggests no. of canisters that are needed to be registered for drugs(priority-wise)
            self.batchwise_drug_list_of_tuple = self.rca.generate_drug_list_of_tuple_multisystem(self.drug_required_canister_list, self.drug_canister_info_dict)

            if 'new_split' not in priority_drug_dict:
                for tpl in self.batchwise_drug_list_of_tuple:
                    if tpl[0] in priority_drug_dict.keys():
                        priority_drug_dict[tpl[0]]['qty'] = tpl[1]
        else:
            self.batchwise_drug_list_of_tuple = []

        return default_split,priority_drug_dict

    def recommend_canister_distribution_across_systems(self):
        """
        When optimum split facilities given to each system, this method will recommend optimal canister transfer operations across the available systems
        :return:
        """

        self.cd = RecommendCanisterDistributionAcrossSystems(system_df_info_dict=self.dataframe_info_dict,
                                                             drug_canister_info_dict=self.drug_canister_info_dict,
                                                             system_robot_info_dict=self.system_robot_info_dict,
                                                             robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                             pack_drug_manual_dict=self.pack_drug_manual_dict,
                                                             canister_location_info_dict=self.canister_location_info_dict)

        self.system_list, self.system_drug_canister_info_dict, self.system_robot_capacity_info_dict, self.system_manual_drug_dict = self.cd.recommend_canister_distribution()
        self.systemwise_distribution = {}
        self.systemwise_canister_to_add = {}
        for system_id in self.system_list:

            self.systemwise_manual_drugs = self.system_manual_drug_dict[system_id]
            self.systemwise_df = self.dataframe_info_dict[system_id]
            self.systemwise_drug_canister_info_dict = self.system_drug_canister_info_dict[system_id]
            self.systemwise_robot_capacity_info_dict = self.system_robot_capacity_info_dict[system_id]

            self.dpp = CanisterRecommender(file_name=self.file_name, df=self.systemwise_df, robot_capacity_info_dict=self.systemwise_robot_capacity_info_dict,
                                           drug_canister_info_dict=self.systemwise_drug_canister_info_dict, canister_location_info_dict=self.canister_location_info_dict, canister_expiry_status_dict = self.canister_expiry_status_dict,
                                           robot_free_location_info_dict=self.robot_free_location_info_dict, external_manual_drug_list=self.systemwise_manual_drugs)

            self.canister_transfer_info_dict, self.analysis = self.dpp.recommend_canisters_to_transfer_hybrid()

            self.systemwise_distribution[system_id] = {
                                                       "canister_transfer_info_dict": self.canister_transfer_info_dict,
                                                       "analysis": self.analysis
                                                       }

        return self.systemwise_distribution

    def recommend_distribution_across_systems(self):
        """
        When list of facilities are imported in the system, this method will recommend optimal distribution(groups)
        across the available systems.
        :return:
        """
        self.pd = RecommendPackDistributionAcrossSystems(df=self.df,
                                                         robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                         drug_canister_info_dict=self.drug_canister_info_dict,
                                                         canister_location_info_dict=self.canister_location_info_dict,
                                                         robot_free_location_info_dict=self.robot_free_location_info_dict,
                                                         facility_pack_info_dict=self.facility_pack_info_dict,
                                                         system_robot_info_dict=self.system_robot_info_dict)
        self.system_division_info_dict = self.pd.recommend_distribution()
        return self.system_division_info_dict


    def recommend_canisters_to_add(self, truncated = True):
        """
        This method will recommmend canisters to add in the form of list of tuple.
        :return: recommended_canister_list_of_tuple
        """
        self.rca = RecommendCanisterToAdd(file_name=self.file_name, df=self.df, drug_canister_info_dict=self.drug_canister_info_dict)
        if truncated:
            _, recommended_canister_list_of_tuple = self.rca.get_recommendation_to_add_canisters_truncated()
            return recommended_canister_list_of_tuple
        else:
            _, recommended_canister_list_of_tuple = self.rca.get_recommendation_to_add_canisters()
            return recommended_canister_list_of_tuple

    def recommend_canisters_to_remove(self):
        """

        :return:
        """
        self.rcr = RecommendCanistersToRemove(file_name=self.file_name, df=self.df, robot_capacity_info_dict=self.robot_capacity_info_dict,
                                              drug_canister_info_dict=self.drug_canister_info_dict, canister_location_info_dict=self.canister_location_info_dict)
        canisters_to_remove_list = self.rcr.recommend_canisters_to_remove()
        return canisters_to_remove_list

    def recommend_canisters_to_transfer(self):
        self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.df, robot_capacity_info_dict=self.robot_capacity_info_dict,
                                              drug_canister_info_dict=self.drug_canister_info_dict, canister_location_info_dict=self.canister_location_info_dict, robot_free_location_info_dict=self.robot_free_location_info_dict)
        canister_transfer_info_dict = self.rct.recommend_canisters_to_transfer()
        return canister_transfer_info_dict

    def recommend_canisters_to_transfer_hybrid(self):
        """
        This method is called when we want to get recommendation of remove and transfer altogether,
        - In this method we will get recommendation for removing canister in the form of dictionary with value tuple.
        - We will append both recommendation.
        :return:
        """
        self.rcr = RecommendCanistersToRemove(file_name=self.file_name, df=self.df,
                                              robot_capacity_info_dict=self.robot_capacity_info_dict,drug_canister_info_dict=self.drug_canister_info_dict,
                                              canister_location_info_dict=self.canister_location_info_dict)
        insufficient_space_canister_remove_dict = self.rcr.recommend_canisters_to_remove(hybrid_method=True)
        """
        converting insufficient_space_canister_remove_dict into format of canister transfer info dict.
        """
        canister_transfer_info_dict_for_remove = {}
        for robot_id in insufficient_space_canister_remove_dict.keys():
            for canister_id in insufficient_space_canister_remove_dict[robot_id]:
                canister_transfer_info_dict_for_remove[canister_id] = (robot_id, None)
        self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.df,
                                                robot_capacity_info_dict=self.robot_capacity_info_dict,drug_canister_info_dict=self.drug_canister_info_dict,
                                                canister_location_info_dict=self.canister_location_info_dict,
                                                robot_free_location_info_dict=self.robot_free_location_info_dict
                                                )
        canister_transfer_info_dict, analysis = self.rct.recommend_canisters_to_transfer()
        canister_transfer_info_dict.update(canister_transfer_info_dict_for_remove)
        append_dictionary_to_json_file(canister_transfer_info_dict, "canister_transfer_info_dict_hybrid", True, "transfer.json")
        return canister_transfer_info_dict, analysis


    # TODO: Check the correntness for N-robots
    # this function doesn't depend on number of robots, It only depends on the total facilities and their packs
    def multi_robot_recommend_distribution_across_systems(self):
        """
        When list of facilities are imported in the system, this method will recommend optimal distribution(groups)
        across the available systems.
        :return:
        """
        self.pd = RecommendPackDistributionAcrossSystems(df=self.df,
                                                         robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                         drug_canister_info_dict=self.drug_canister_info_dict,
                                                         canister_location_info_dict=self.canister_location_info_dict,
                                                         robot_free_location_info_dict=self.robot_free_location_info_dict,
                                                         facility_pack_info_dict=self.facility_pack_info_dict,
                                                         system_robot_info_dict=self.system_robot_info_dict)
        self.system_division_info_dict = self.pd.recommend_distribution()
        return self.system_division_info_dict

    def multi_robot_recommend_canister_distribution_across_systems_multi_split(self,total_packs):
        """
        When optimum split facilities given to each system, this method will recommend optimal canister transfer operations across the available systems
        :return:
        """
        self.systemwise_distribution_get_multisplit = {}
        self.cd = RecommendCanisterDistributionAcrossSystems(system_df_info_dict=self.dataframe_info_dict,
                                                             drug_canister_info_dict=self.drug_canister_info_dict,
                                                             system_robot_info_dict=self.system_robot_info_dict,
                                                             robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                             pack_drug_manual_dict=self.pack_drug_manual_dict,
                                                             canister_location_info_dict=self.canister_location_info_dict)

        # system_manual_drug_dict is for external manual drugs
        self.system_list, self.system_drug_canister_info_dict, self.system_robot_capacity_info_dict, self.system_pack_drug_manual_dict, self.system_pack_half_pill_drug_dict = self.cd.recommend_canister_distribution()
        self.systemwise_distribution = {}
        self.systemwise_canister_to_add = {}
        for system_id in self.system_list:

            # self.systemwise_manual_drugs = self.system_manual_drug_dict[system_id]
            self.systemwise_pack_drug_manual_dict = self.system_pack_drug_manual_dict[system_id]
            self.systemwise_pack_half_pill_drug_dict = self.system_pack_half_pill_drug_dict[system_id]
            self.systemwise_df = self.dataframe_info_dict[system_id]
            self.systemwise_drug_canister_info_dict = self.system_drug_canister_info_dict[system_id]
            self.systemwise_robot_capacity_info_dict = self.system_robot_capacity_info_dict[system_id]
            self.systemwise_robots = self.system_robot_info_dict[int(system_id)]

            self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.systemwise_df,
                                                    robot_capacity_info_dict=self.systemwise_robot_capacity_info_dict,
                                                    drug_canister_info_dict=self.systemwise_drug_canister_info_dict,
                                                    canister_location_info_dict=self.canister_location_info_dict,
                                                    robot_free_location_info_dict=self.robot_free_location_info_dict,
                                                    robot_list=self.systemwise_robots,
                                                    pack_drug_manual_dict=self.systemwise_pack_drug_manual_dict,
                                                    pack_half_pill_drug_dict=self.systemwise_pack_half_pill_drug_dict,total_packs=total_packs[system_id])

            split_list = []
            self.multi_split_info = self.rct.recommend_multiple_split()
            for k,v in self.multi_split_info.items():
                self.multi_split_info[k][self.systemwise_robots[0]] = self.multi_split_info[k]["Robot-1"]
                self.multi_split_info[k][self.systemwise_robots[1]] = self.multi_split_info[k]["Robot-2"]
                del self.multi_split_info[k]["Robot-1"]
                del self.multi_split_info[k]["Robot-2"]
            for f_id,result in self.multi_split_info.items():
                result["id"] = f_id
                split_list.append(result)
            # split_list.append({'total_packs':len(total_packs[system_id])})

            self.systemwise_distribution_get_multisplit[system_id] = {'total_packs':len(total_packs[system_id]),'split':split_list}

        return self.systemwise_distribution_get_multisplit

    # TODO: Check the correntness for N-robots
    def multi_robot_recommend_canister_distribution_across_systems(self,total_packs):
        """
        When optimum split facilities given to each system, this method will recommend optimal canister transfer operations across the available systems
        :return:
        """

        self.cd = RecommendCanisterDistributionAcrossSystems(system_df_info_dict=self.dataframe_info_dict,
                                                             drug_canister_info_dict=self.drug_canister_info_dict,
                                                             system_robot_info_dict=self.system_robot_info_dict,
                                                             robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                             pack_drug_manual_dict=self.pack_drug_manual_dict,
                                                             canister_location_info_dict=self.canister_location_info_dict)

        # system_manual_drug_dict is for external manual drugs
        self.system_list, self.system_drug_canister_info_dict, self.system_robot_capacity_info_dict, self.system_pack_drug_manual_dict, self.system_pack_half_pill_drug_dict = self.cd.recommend_canister_distribution()
        self.systemwise_distribution = {}
        self.systemwise_canister_to_add = {}
        for system_id in self.system_list:

            # self.systemwise_manual_drugs = self.system_manual_drug_dict[system_id]
            self.systemwise_pack_drug_manual_dict = self.system_pack_drug_manual_dict[system_id]
            self.systemwise_pack_half_pill_drug_dict = self.system_pack_half_pill_drug_dict[system_id]
            self.systemwise_df = self.dataframe_info_dict[system_id]
            self.systemwise_drug_canister_info_dict = self.system_drug_canister_info_dict[system_id]
            self.systemwise_robot_capacity_info_dict = self.system_robot_capacity_info_dict[system_id]
            self.systemwise_robots = self.system_robot_info_dict[int(system_id)]

            self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.systemwise_df,
                                                    robot_capacity_info_dict=self.systemwise_robot_capacity_info_dict,
                                                    drug_canister_info_dict=self.systemwise_drug_canister_info_dict,
                                                    canister_location_info_dict=self.canister_location_info_dict,
                                                    robot_free_location_info_dict=self.robot_free_location_info_dict,
                                                    robot_list=self.systemwise_robots,
                                                    pack_drug_manual_dict=self.systemwise_pack_drug_manual_dict,
                                                    pack_half_pill_drug_dict=self.systemwise_pack_half_pill_drug_dict,
                                                    split_function_id = self.split_function_id,total_packs=total_packs[system_id],pack_drug_slot_id_dict=self.pack_drug_slot_id_dict,total_robots=len(self.systemwise_robots))

            self.canister_transfer_info_dict, self.analysis = self.rct.recommend_canisters_to_transfer()

            self.systemwise_distribution[system_id] = {
                                                       "canister_transfer_info_dict": self.canister_transfer_info_dict,
                                                       "analysis": self.analysis
                                                       }

        return self.systemwise_distribution

    def multi_robot_recommend_canister_distribution_across_systems_v3(self,total_packs):
        """
        When optimum split facilities given to each system, this method will recommend optimal canister transfer operations across the available systems
        :return:
        """
        '''
        Below class distributes packs among systems. This depends on system capacity. 
        Once packs are distributed among system, we distribute packs among robots.
        Inside this class, logic for 1x and Nx is written.
        '''
        self.cd = RecommendCanisterDistributionAcrossSystems(system_df_info_dict=self.dataframe_info_dict,
                                                             drug_canister_info_dict=self.drug_canister_info_dict,
                                                             system_robot_info_dict=self.system_robot_info_dict,
                                                             robot_capacity_info_dict=self.robot_capacity_info_dict,
                                                             pack_drug_manual_dict=self.pack_drug_manual_dict,
                                                             canister_location_info_dict=self.canister_location_info_dict,canister_qty_dict=self.canister_qty_dict)

        # system_manual_drug_dict is for external manual drugs
        self.system_list, self.system_drug_canister_info_dict, self.system_robot_capacity_info_dict, self.system_pack_drug_manual_dict, self.system_pack_half_pill_drug_dict = self.cd.recommend_canister_distribution()
        self.systemwise_distribution = {}
        self.systemwise_canister_to_add = {}
        for system_id in self.system_list:

            # self.systemwise_manual_drugs = self.system_manual_drug_dict[system_id]
            self.systemwise_pack_drug_manual_dict = self.system_pack_drug_manual_dict[system_id]

            self.systemwise_pack_half_pill_drug_dict = self.system_pack_half_pill_drug_dict[system_id]

            self.systemwise_df = self.dataframe_info_dict[system_id]

            self.systemwise_drug_canister_info_dict = self.system_drug_canister_info_dict[system_id]

            self.systemwise_robot_capacity_info_dict = self.system_robot_capacity_info_dict[system_id]

            self.systemwise_robots = self.system_robot_info_dict[int(system_id)]

            '''
            For each system, we distribute packs among the robots and after that, distribute drugs among quadrants.
            Below class gives quadrant distribution per robot with optimized drops and config_ids.
            '''
            self.rct = RecommendCanistersToTransfer(file_name=self.file_name, df=self.systemwise_df,
                                                    robot_capacity_info_dict=self.systemwise_robot_capacity_info_dict,
                                                    drug_canister_info_dict=self.systemwise_drug_canister_info_dict,
                                                    canister_location_info_dict=self.canister_location_info_dict,
                                                    canister_expiry_status_dict=self.canister_expiry_status_dict,
                                                    robot_free_location_info_dict=self.robot_free_location_info_dict,
                                                    robot_list=self.systemwise_robots,
                                                    pack_drug_manual_dict=self.systemwise_pack_drug_manual_dict,
                                                    pack_half_pill_drug_dict=self.systemwise_pack_half_pill_drug_dict,
                                                    split_function_id=self.split_function_id,
                                                    total_packs=total_packs[system_id],
                                                    pack_slot_drug_dict=self.pack_slot_drug_dict,
                                                    pack_slot_detail_drug_dict=self.pack_slot_detail_drug_dict,
                                                    pack_drug_slot_number_slot_id_dict=self.pack_drug_slot_number_slot_id_dict,
                                                    total_robots=len(self.systemwise_robots),
                                                    pack_drug_half_pill_slots_dict=self.pack_drug_half_pill_slots_dict,
                                                    drug_quantity_dict=self.drug_quantity_dict,
                                                    canister_qty_dict=self.canister_qty_dict,
                                                    drug_canister_usage=self.drug_canister_usage,
                                                    pack_delivery_date=self.pack_delivery_date,
                                                    robot_quadrant_enable_locations=self.robot_quadrant_enable_locations)

            self.canister_transfer_info_dict, self.analysis = self.rct.recommend_canisters_to_transfer_v3()


            self.systemwise_distribution[system_id] = {
                                                       "canister_transfer_info_dict": self.canister_transfer_info_dict,
                                                       "analysis": self.analysis
                                                       }

        return self.systemwise_distribution


    def canister_recommendation_for_quadrants(self):

        self.rcdiq = RecommendCanisterDistributionInQuadrants(
                                                              pack_slot_drug_dict=self.pack_slot_drug_dict,
                                                              multiple_canisters_drugs=self.multiple_canisters_drugs,
                                                              drug_canister_count_dict =  self.drug_canister_count_dict)

        self.response, self.updated_pack_slot_drug_dict = self.rcdiq.run_algo(num_of_quadrants = 4,combinations_to_remove = None)

        return self.response, self.updated_pack_slot_drug_dict

