import datetime
import functools
import operator
from collections import defaultdict

import pandas as pd
from peewee import InternalError, IntegrityError, DoesNotExist, fn, JOIN_LEFT_OUTER, SQL

from src import constants
import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, log_args
from dosepack.validation.validate import validate
from src.dao.device_manager_dao import db_get_robots_by_systems_dao, get_disabled_locations_of_devices
from src.dao.pack_analysis_dao import db_delete_pack_analysis, db_save_analysis
from src.model.model_batch_hash import BatchHash
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_unique_drug import UniqueDrug
from src.model.model_zone_master import ZoneMaster
from src.multisystem_dosepacker_preprocessing import MultiSystemCanisterRecommender


logger = settings.logger


@log_args_and_response
def transfer_canister_recommendation(cr_res, canister_data, robot_dict):
    """
    Returns list of recommendations for canister transfers

    :param cr_res (dict): {canister id: (source_robot_id, dest_robot_id) }
    :param canister_data (dict): {canister_id: {...}}
    :param robot_dict:
    :return: list
    """
    robot_dict.setdefault(None, {})
    robot_dict[None]["name"] = None
    recommendations = list()  # stores recommended canister destination
    pending_transfers = list()
    reserved_canister = set()
    remove_locations = defaultdict(list)
    for canister_id, robots in cr_res.items():
        canister = canister_data[canister_id]
        canister["dest_device_id"] = robots[1]
        canister["source_device_id"] = robots[0]
        canister['dest_quadrant'] = robots[4] if len(robots) > 4 else None
        canister["dest_device_name"] = robot_dict[robots[1]]["name"]
        canister["source_device_name"] = robot_dict[robots[1]]["name"]
        # '''
        # Temporary implementation for CSR.
        # '''
        # if robots[1] in settings.AVAILABLE_CSR:
        #     canister["dest_robot_name"] = robots[1]
        # else:
        #     canister["dest_robot_name"] = robot_dict[robots[1]]["name"]
        # if robots[0] in settings.AVAILABLE_CSR:
        #     canister["source_robot_name"] = robots[0]
        # else:
        #     canister["source_robot_name"] = robot_dict[robots[0]]["name"]

        if robots[1] != robots[0]:
            # dest robot is not same as source robot, transfer action pending
            pending_transfers.append(canister)
        recommendations.append(canister)
        if robots[1] is None:
            remove_locations[robots[0]].append(canister['canister_number'])
        else:
            reserved_canister.add(canister_id)
    logger.info("In transfer_canister_recommendation, recommendations: {}".format(recommendations))
    logger.info("In transfer_canister_recommendation, remove_locations: {}".format(remove_locations))
    logger.info("In transfer_canister_recommendation, pending_transfers: {}".format(pending_transfers))
    logger.info("In transfer_canister_recommendation, reserved_canister: {}".format(reserved_canister))
    return recommendations, remove_locations, pending_transfers, reserved_canister


@log_args_and_response
def save_transfers(recommendations, batch_id):
    """
    Stores transfer recommendations into `CanisterTransfers`

    :param recommendations: transfer recommendations
    :param batch_id: batch ID for which transfer recommendations are saved
    :return:
    """
    transfers = list()
    for item in recommendations:
        transfers.append({
            'batch_id': batch_id,
            'canister_id': item['id'],
            'dest_device_id': item['dest_device_id'],
            'dest_quadrant' : item['dest_quadrant']
        })
    logger.debug('Canister Transfer Data: {}'.format(transfers))
    if transfers:
        BaseModel.db_create_multi_record(transfers, CanisterTransfers)


@log_args_and_response
def save_analysis(analysis, pack_manual, canister_data, drug_data, batch_id,
                  batch_list, re_run, user_id, full_manual_pack_drug):
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
    pack_list = list()
    analysis_data = list()
    print('here')
    canister_data[None] = {"drug_id": None, "canister_number": None} # default response for None canister id
    robot_id = None
    for pack, drugs in analysis.items():
        # create analysis data to store in db
        pack_data = dict()
        pack_list.append(pack)
        pack_data["pack_id"] = pack
        pack_data["manual_fill_required"] = pack_manual[pack]
        pack_data.setdefault('ndc_list', [])
        for item in drugs:
            drug = {}
            if (pack, item[0]) in full_manual_pack_drug:
                # do not assign canister as all qty are 0.5
                canister_id = item[1]
                drug["canister_id"] = None
                drug["device_id"] = None
                drug["drug_id"] = drug_data[item[0]]["drug_id"]
                drug["slot_id"] = item[4]
                drug["location_number"] = None
                drug["quadrant"] = None
                drug["drop_number"] = None
                drug["config_id"] = None
            else:  # assign canister as suggested by recommendation algo.
                canister_id = item[1]
                drug["canister_id"] = canister_id
                drug["device_id"] = item[2]
                drug["drug_id"] = drug_data[item[0]]["drug_id"]
                drug["location_number"] = None
                drug["quadrant"] = item[3]
                drug["slot_id"] = item[4]
                drug["drop_number"] = item[5]
                drug["config_id"] = item[6]

            pack_data['ndc_list'].append(drug)
        analysis_data.append(pack_data)
    logger.debug('pack list from analysis data: len - {} - {} '.format(len(pack_list), pack_list))
    _hash = BatchHash.generate_batch_hash(batch_list)

    with db.transaction():
        try:
            # commenting as batch id is already generated using /packbatch
            # batch_id = PackDetails.db_update_batch_id(pack_list, system_id)
            if re_run:
                db_delete_pack_analysis(batch_id)
                CanisterTransfers.delete().where(CanisterTransfers.batch_id == batch_id).execute()
            BatchMaster.db_set_status(batch_id, settings.BATCH_CANISTER_TRANSFER_RECOMMENDED, user_id)
            batch_hash = {
                'batch_id': batch_id,
                'batch_hash': _hash
            }
            record, created = BaseModel.db_create_record(batch_hash, BatchHash)
            logger.debug('BatchHash Data: {}'.format(batch_hash))
        except InternalError:
            raise
        logger.info('final_analysis_data:{}'.format(analysis_data))
        logger.info("analysis data while saving final pack analysis details {}".format(analysis_data))
        db_save_analysis(analysis_data, batch_id)
    return batch_id, analysis_data


class PackDistributorV3(object):
    """
    TODO Add docstrings
    """

    def __init__(self, company_id, batch_packs=None, split_function_id=None, dry_run=False, system_id=None):
        self.pack_delivery_date = None
        self.drug_canister_usage = None
        self.batch_packs = batch_packs
        self.company_id = company_id
        self.dry_run = dry_run
        self.split_function_id = split_function_id
        self.system_id = system_id
        # initially empty parameters, should be set through their data fetchers and generators
        self.batch_names = dict()
        self.system_packs = dict()
        self.batch_ids = dict()
        self.system_id_list = list()
        self.pack_ids_set = None
        self.drug_ids_set = None
        self.pack_mapping = None
        self.cache_drug_data = None
        self.pack_manual = None
        self.pack_drug_manual = None
        self.facility_packs = None
        self.fully_manual_pack_drug = None
        self.canister_location = None
        self.canister_expiry_status_dict = None
        self.drug_canisters = None
        self.canister_data = None
        self.robot_ids, self.robots_data, self.robot_capacity, self.system_robots = None, None, None, None
        self.robot_max_canisters = None
        self.robot_dict = None
        self.robot_empty_locations = None
        self.system_df = dict()

    def get_recommendation(self):
        self.initialize_data()
        self.get_pack_data()
        self.get_robot_canister_data()
        self.create_system_df()
        self.get_pack_slotwise_drugs()
        '''
        This class run canister recommendation for multiple system
        '''
        recommender = MultiSystemCanisterRecommender(
            None, None, self.system_df, self.pack_drug_manual, self.robot_capacity,
            self.drug_canisters, self.canister_location, self.canister_expiry_status_dict,
            self.robot_empty_locations, self.facility_packs, self.system_robots,
            system_division_info_dict=self.system_packs, split_function_id=self.split_function_id,
            pack_slot_drug_dict=self.pack_slot_drug_dict, pack_slot_detail_drug_dict=self.pack_slot_detail_drug_dict,
            pack_drug_slot_number_slot_id_dict=self.pack_drug_slot_number_slot_id_dict,
            pack_drug_half_pill_slots_dict=self.pack_drug_half_pill_slots_dict,
            drug_quantity_dict=self.drug_quantity_dict, canister_qty_dict=self.canister_qty_dict,
            drug_canister_usage=self.drug_canister_usage, pack_delivery_date=self.pack_delivery_date,
            robot_quadrant_enable_locations=self.robot_quadrant_enable_locations
        )
        recommendations = recommender.multi_robot_recommend_canister_distribution_across_systems_v3(self.system_packs)
        return recommendations


    def get_pack_slotwise_drugs(self):
        try:
            pack_id_list = self.batch_packs[self.system_id]['pack_list']
            self.pack_slot_drug_dict = dict()
            self.pack_slot_detail_drug_dict = dict()
            self.pack_drug_half_pill_slots_dict = dict()
            self.drug_quantity_dict = dict()

            query = PackDetails.select(PackDetails.id,
                                       DrugMaster.concated_fndc_txr_field(sep='##').alias('drug_id'),
                                       PackGrid.slot_number, SlotDetails.id.alias('slot_id'),
                                       SlotDetails.quantity) \
                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .where(PackDetails.id << pack_id_list)

            for record in query.dicts():
                if record['id'] not in self.pack_slot_drug_dict.keys():
                    self.pack_slot_drug_dict[record['id']] = {}
                    self.pack_slot_detail_drug_dict[record['id']] = {}
                    self.pack_drug_half_pill_slots_dict[record['id']] = {}
                if record['slot_number'] not in self.pack_slot_drug_dict[record['id']].keys():
                    self.pack_slot_drug_dict[record['id']][record['slot_number']] = set()
                    self.pack_slot_detail_drug_dict[record['id']][record['slot_number']] = record['slot_id']
                if record['drug_id'] is not None:
                    self.pack_slot_drug_dict[record['id']][record['slot_number']].add(record['drug_id'])
                if record['drug_id'] not in self.pack_drug_half_pill_slots_dict[record['id']].keys():
                    self.pack_drug_half_pill_slots_dict[record['id']][record['drug_id']] = list()
                if record['slot_number'] not in self.pack_drug_half_pill_slots_dict[record['id']][record['drug_id']] \
                        and record['quantity'] in settings.DECIMAL_QTY_LIST:
                        # and not float(record['quantity']).is_integer():
                    self.pack_drug_half_pill_slots_dict[record['id']][record['drug_id']].append(record['slot_number'])

                if record['drug_id'] not in self.drug_quantity_dict.keys():
                    self.drug_quantity_dict[record['drug_id']] = 0
                self.drug_quantity_dict[record['drug_id']] += record['quantity']

            logger.info(self.pack_slot_drug_dict, self.pack_slot_detail_drug_dict)
        except Exception as e:
            logger.info(e)
            return e

    def get_recommendation_multi_split(self):
        self.dry_run = True
        self.initialize_data()
        self.get_pack_data()
        self.get_robot_canister_data()
        self.create_system_df()

        recommender = MultiSystemCanisterRecommender(
            None, None, self.system_df, self.pack_drug_manual, self.robot_capacity,
            self.drug_canisters, self.canister_location,
            self.robot_empty_locations, self.facility_packs, self.system_robots,
            system_division_info_dict=self.system_packs
        )
        system_remaining_packs = self.pack_ids_set
        recommendations = recommender.multi_robot_recommend_canister_distribution_across_systems_multi_split(
            system_remaining_packs)
        return recommendations

    def initialize_data(self):
        for system, batch_data in self.batch_packs.items():
            system = int(system)
            self.batch_names[system] = batch_data['batch_name']
            self.system_packs[system] = batch_data['pack_list']
            self.batch_ids[system] = batch_data.get('batch_id', None)
            self.system_id_list.append(system)

    def get_pack_data(self):
        self.pack_ids_set, self.drug_ids_set, \
        self.pack_mapping, self.cache_drug_data, \
        self.pack_manual, self.pack_drug_manual, \
        self.facility_packs, self.fully_manual_pack_drug, self.pack_delivery_date = get_system_wise_pack_data(self.system_packs, self.dry_run)

        pack_list = list(self.pack_ids_set.values())[0]
        self.pack_drug_slot_id_dict = get_pack_drug_slot_data(pack_list)
        self.pack_drug_slot_number_slot_id_dict = get_pack_drug_slot_details(pack_list)

    def get_robot_canister_data(self):
        try:
            system_zone_mapping, self.zone_list = self.get_system_zone_mapping(self.system_id_list)

            self.robot_ids, self.robots_data, self.robot_capacity, \
            self.system_robots = get_robot_data(self.system_id_list)

            # self.drug_canister_per_robot = SystemSetting.db_get_system_value_by_name(system_list=self.system_id_list,
            #                                                                         name=[settings.DRUG_CANISTER_PER_ROBOT])
            self.canister_location, self.drug_canisters, \
            self.canister_data, self.canister_expiry_status_dict = get_canister_data(self.company_id, zone_list=self.zone_list,
                                                   ignore_reserved=self.dry_run, system_id=self.system_id)
            '''
            For Nx Canister Recommendation, we have fetched canister usage from unique drug table in below function
            '''
            self.drug_canister_usage = get_drug_canister_usage()
            """
            For nx canister recommendation we fetch robot wise all the enabled location excluding mfd locations
            """
            self.robot_quadrant_enable_locations = get_robot_quadrant_enable_locations()

            self.canister_qty_dict = get_canister_qty(self.company_id, zone_list=self.zone_list,
                                                   ignore_reserved=self.dry_run, system_id=self.system_id)
            self.robot_max_canisters = {robot['id']: robot['max_canisters'] for system, robots in
                                        self.robots_data.items()
                                        for robot in robots}
            self.robot_dict = {item["id"]: item for system, robots in self.robots_data.items()
                               for item in robots}
            self.robot_empty_locations = LocationMaster.db_get_empty_locationsV3(self.robot_max_canisters)
        except Exception as e:
            logger.info(e)
            return e

    def get_system_zone_mapping(self, system_list):

        try:
            system_zone_mapping = {}
            zone_list = set()
            query = DeviceMaster.select(ZoneMaster.id, DeviceMaster.system_id) \
                .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(ZoneMaster, on=ZoneMaster.id == DeviceLayoutDetails.zone_id).where(
                DeviceMaster.system_id << system_list)

            for record in query.dicts():
                system_zone_mapping[record['system_id']] = record['id']
                zone_list.add(record['id'])
            zone_list = list(zone_list)
            return system_zone_mapping, zone_list
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    def create_system_df(self):
        for system in self.system_id_list:  # create df for distributed packs
            df, column_list = create_dataset(
                self.pack_ids_set[system],
                self.drug_ids_set[system],
                self.pack_mapping[system]
            )
            self.system_df[system] = df

    def create_batch_packs_from_batches(self, batches):
        """
        This function is convenience function for testing purpose or dry run purpose.

        :param batches: list
        :return:
        """
        batch_packs = dict()
        if batches:
            query = PackDetails.select(
                PackDetails.batch_id,
                PackDetails.id.alias('pack_id'),
                BatchMaster.system_id
            ).join(BatchMaster).where(PackDetails.batch_id << batches)

            for item in query.dicts():
                system = item['system_id']
                batch_packs.setdefault(system, {})
                batch_packs[system]['batch_name'] = str(item['batch_id'])  # dummy # same as batch_id
                batch_packs[system].setdefault('pack_list', [])
                batch_packs[system]['pack_list'].append(item['pack_id'])
        self.batch_packs = batch_packs


class PackDistributor(object):
    """
    TODO Add docstrings
    """

    def __init__(self, company_id, batch_packs=None, split_function_id=None, dry_run=False):
        self.pack_delivery_date = None
        self.batch_packs = batch_packs
        self.company_id = company_id
        self.dry_run = dry_run
        self.split_function_id = split_function_id

        # initially empty parameters, should be set through their data fetchers and generators
        self.batch_names = dict()
        self.system_packs = dict()
        self.batch_ids = dict()
        self.system_id_list = list()
        self.pack_ids_set = None
        self.drug_ids_set = None
        self.pack_mapping = None
        self.cache_drug_data = None
        self.pack_manual = None
        self.pack_drug_manual = None
        self.facility_packs = None
        self.fully_manual_pack_drug = None
        self.canister_location = None
        self.canister_expiry_status_dict = None
        self.drug_canisters = None
        self.canister_data = None
        self.robot_ids, self.robots_data, self.robot_capacity, self.system_robots = None, None, None, None
        self.robot_max_canisters = None
        self.robot_dict = None
        self.robot_empty_locations = None
        self.system_df = dict()

    def get_recommendation(self):
        self.initialize_data()
        self.get_pack_data()
        self.get_robot_canister_data()
        self.create_system_df()
        recommender = MultiSystemCanisterRecommender(
            None, None, self.system_df, self.pack_drug_manual, self.robot_capacity,
            self.drug_canisters, self.canister_location,
            self.robot_empty_locations, self.facility_packs, self.system_robots,
            system_division_info_dict=self.system_packs, split_function_id=self.split_function_id,
            pack_drug_slot_id_dict=self.pack_drug_slot_id_dict
        )
        recommendations = recommender.multi_robot_recommend_canister_distribution_across_systems(self.system_packs)
        return recommendations

    def get_recommendation_multi_split(self):
        self.dry_run = True
        self.initialize_data()
        self.get_pack_data()
        self.get_robot_canister_data()
        self.create_system_df()

        if len(self.system_robots[self.system_id_list[0]]) == 1:
            recommendations = "Currently, this system is running single drug dispenser. This functionality is not applicable to single drug dispenser system."
        else:
            recommender = MultiSystemCanisterRecommender(
                None, None, self.system_df, self.pack_drug_manual, self.robot_capacity,
                self.drug_canisters, self.canister_location,
                self.robot_empty_locations, self.facility_packs, self.system_robots,
                system_division_info_dict=self.system_packs
            )

            system_remaining_packs = self.pack_ids_set
            recommendations = recommender.multi_robot_recommend_canister_distribution_across_systems_multi_split(
                system_remaining_packs)

        return recommendations

    def initialize_data(self):
        for system, batch_data in self.batch_packs.items():
            system = int(system)
            self.batch_names[system] = batch_data['batch_name']
            self.system_packs[system] = batch_data['pack_list']
            self.batch_ids[system] = batch_data.get('batch_id', None)
            self.system_id_list.append(system)

    def get_pack_data(self):
        self.pack_ids_set, self.drug_ids_set, \
        self.pack_mapping, self.cache_drug_data, \
        self.pack_manual, self.pack_drug_manual, \
        self.facility_packs, self.fully_manual_pack_drug, self.pack_delivery_date = get_system_wise_pack_data(self.system_packs, self.dry_run)

        pack_list = list(self.pack_ids_set.values())[0]
        self.pack_drug_slot_id_dict = get_pack_drug_slot_data(pack_list)

    def get_robot_canister_data(self):
        # system_id_list = self.get_system_from_company_id(self.company_id)
        system_zone_mapping, self.zone_list = self.get_system_zone_mapping(self.system_id_list)

        self.canister_location, self.drug_canisters, \
        self.canister_data, self.canister_expiry_status_dict = get_canister_data(self.company_id, zone_list=self.zone_list, ignore_reserved=self.dry_run)

        self.robot_ids, self.robots_data, self.robot_capacity, \
        self.system_robots = get_robot_data(self.system_id_list)
        self.robot_max_canisters = {robot['id']: robot['max_canisters'] for system, robots in self.robots_data.items()
                                    for robot in robots}
        self.robot_dict = {item["id"]: item for system, robots in self.robots_data.items()
                           for item in robots}
        self.robot_empty_locations = db_get_empty_locations(self.robot_max_canisters,
                                                                           packdistribution=True)

    def create_system_df(self):
        for system in self.system_id_list:  # create df for distributed packs
            df, column_list = create_dataset(
                self.pack_ids_set[system],
                self.drug_ids_set[system],
                self.pack_mapping[system]
            )
            self.system_df[system] = df

    def get_system_from_company_id(self, company_id):
        try:
            system_id_list = []
            query = DeviceMaster.select(DeviceMaster.system_id).where(DeviceMaster.company_id == company_id)
            for record in query.dicts():
                system_id_list.append(record['system_id'])
            return system_id_list
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    def get_system_zone_mapping(self, system_list):

        try:
            system_zone_mapping = {}
            zone_list = set()
            query = DeviceMaster.select(ZoneMaster.id, DeviceMaster.system_id) \
                .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(ZoneMaster, on=ZoneMaster.id == DeviceLayoutDetails.zone_id).where(
                DeviceMaster.system_id << system_list)

            for record in query.dicts():
                system_zone_mapping[record['system_id']] = record['id']
                zone_list.add(record['id'])
            zone_list = list(zone_list)
            return system_zone_mapping, zone_list
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    def create_batch_packs_from_batches(self, batches):
        """
        This function is convenience function for testing purpose or dry run purpose.

        :param batches: list
        :return:
        """
        batch_packs = dict()
        if batches:
            query = PackDetails.select(
                PackDetails.batch_id,
                PackDetails.id.alias('pack_id'),
                BatchMaster.system_id
            ).join(BatchMaster).where(PackDetails.batch_id << batches)

            for item in query.dicts():
                system = item['system_id']
                batch_packs.setdefault(system, {})
                batch_packs[system]['batch_name'] = str(item['batch_id'])  # dummy # same as batch_id
                batch_packs[system].setdefault('pack_list', [])
                batch_packs[system]['pack_list'].append(item['pack_id'])
        self.batch_packs = batch_packs


@log_args_and_response
def get_system_wise_pack_data(system_packs, dry_run):
    pack_ids_set = defaultdict(set)
    drug_ids_set = defaultdict(set)
    facility_packs = defaultdict(set)
    pack_mapping = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    full_manual_pack_drug = set()  # drug which have 0.5 qty in all slots
    pack_manual = defaultdict(bool)
    pack_system = dict()
    pack_drug_manual = defaultdict(dict)  # if drug is only fractional and less than 1, mark manual
    cache_drug_data = dict()
    pack_ids_list = list()
    pack_delivery_date = dict()

    if dry_run:
        pack_status_list = [
            settings.PENDING_PACK_STATUS
        ]
    else:
        pack_status_list = [
            settings.PENDING_PACK_STATUS,
            settings.PROGRESS_PACK_STATUS,
            settings.DONE_PACK_STATUS]
    # create reverse map for pack to system and pack list
    for system, pack_list in system_packs.items():
        for pack in pack_list:
            pack_system[pack] = system
            pack_ids_list.append(pack)

    if not pack_ids_list:
        return pack_ids_set, drug_ids_set, pack_mapping, cache_drug_data, \
               pack_manual, pack_drug_manual, facility_packs, full_manual_pack_drug, pack_delivery_date

    query = get_pack_data_query(pack_ids_list, pack_status_list)

    try:
        for record in query.dicts():
            system_id = pack_system[record["pack_id"]]
            # list of unique qty for a drug in pack
            quanty = list()
            floor_quantity_temp = list(str(record['quantities']).split(","))
            for each_quantity in floor_quantity_temp:
                if float(each_quantity) in settings.DECIMAL_QTY_LIST:
                    quanty = list()
                    break
                else:
                    quanty.append(float(each_quantity))
            quantities = list(set([float(item) % 1 for item in record["quantities"].split(',')]))
            if 0 in quantities:  # keeping only fractional qty in list
                quantities.remove(0)
            if not pack_manual[record["pack_id"]] and len(quantities) > 0:
                # manual based on fractional qty
                pack_manual[record["pack_id"]] = True

            quantity = float(record["quantity"])
            floor_quantity = sum(quanty)
            # floor_quantity = float(record["floor_quantity"])
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"] if record["txr"] is not None else ''
            )
            if floor_quantity == 0:  # all qty are 0.5, mark them for special handling later
                full_manual_pack_drug.add((record["pack_id"], fndc_txr))

            robot_drug_quantities = {float(item) for item in record["quantities"].split(",")
                                     if float(item) not in settings.DECIMAL_QTY_LIST}
            # if no quantities are robot quantities, it is fully manual
            pack_drug_manual[record["pack_id"]][fndc_txr] = not bool(robot_drug_quantities)

            pack_mapping[system_id][record["pack_id"]][fndc_txr] += quantity
            pack_ids_set[system_id].add(record["pack_id"])
            drug_ids_set[system_id].add(fndc_txr)
            facility_packs[record["facility_id"]].add(record["pack_id"])
            pack_delivery_date[record["pack_id"]] = record["delivery_date"]

            if fndc_txr not in cache_drug_data:
                cache_drug_data[fndc_txr] = {
                    "drug_name": record["drug_name"],
                    "ndc": record["ndc"],
                    "strength": record["strength"],
                    "formatted_ndc": record["formatted_ndc"],
                    "txr": record["txr"],
                    "strength_value": record["strength_value"],
                    "image_name": record["image_name"],
                    "required_quantity": quantity,
                    "imprint": record["imprint"],
                    "shape": record["shape"],
                    "color": record["color"],
                    "drug_id": record["drug_id"]
                }
            else:
                cache_drug_data[fndc_txr]["required_quantity"] += quantity

    except (DoesNotExist, InternalError, IntegrityError) as e:
        logger.error(e)
        raise

    return pack_ids_set, drug_ids_set, pack_mapping, cache_drug_data, \
           pack_manual, pack_drug_manual, facility_packs, full_manual_pack_drug, pack_delivery_date


@log_args_and_response
def get_pack_drug_slot_data(pack_list):
    try:
        pack_list = list(pack_list)
        pack_drug_slot_id_dict = {}
        query = SlotDetails.select(PackDetails.id.alias('pack_id'),
                                   fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')).alias(
                                       'drug'), SlotDetails.id.alias('slot_id')) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list)

        for record in query.dicts():
            if record['pack_id'] not in pack_drug_slot_id_dict:
                pack_drug_slot_id_dict[record['pack_id']] = {}
            if record['drug'] not in pack_drug_slot_id_dict[record['pack_id']]:
                pack_drug_slot_id_dict[record['pack_id']][record['drug']] = []
            pack_drug_slot_id_dict[record['pack_id']][record['drug']].append(record['slot_id'])
        return pack_drug_slot_id_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_pack_drug_slot_details(pack_list):
    try:
        pack_list = list(pack_list)
        pack_drug_slot_number_slot_id_dict = {}
        query = SlotDetails.select(PackDetails.id.alias('pack_id'),
                                   DrugMaster.concated_fndc_txr_field(sep='##').alias('drug'),
                                   SlotDetails.id.alias('slot_id'), PackGrid.slot_number) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .where(PackDetails.id << pack_list)

        for record in query.dicts():
            if record['pack_id'] not in pack_drug_slot_number_slot_id_dict:
                pack_drug_slot_number_slot_id_dict[record['pack_id']] = {}
            if record['drug'] not in pack_drug_slot_number_slot_id_dict[record['pack_id']]:
                pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']] = {}
            if record['slot_number'] not in pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']]:
                pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']][record['slot_number']] = 0
            pack_drug_slot_number_slot_id_dict[record['pack_id']][record['drug']][record['slot_number']] = record[
                'slot_id']
        return pack_drug_slot_number_slot_id_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_robot_data(system_id_list):
    '''
    This function fetches data of all devices including Robots and CSRs
    :param system_id_list:
    :return:
    '''
    robot_capacity = dict()
    robots_data = dict()
    system_id_list = list(map(int, system_id_list))
    robots_data = db_get_robots_by_systems_dao(system_id_list=system_id_list)
    # for item in robot_list:
    #     robots_data.setdefault(item["system_id"], list()).append(item)
    robot_ids = [item["id"] for robots in robots_data.values()
                 for item in robots
                 if item["system_id"] in system_id_list]
    disabled_locations = defaultdict(set)
    system_robots = defaultdict(list)
    for record in get_disabled_locations_of_devices(device_ids=robot_ids):
        disabled_locations[record["device_id"]].add(record["location_number"])
    for system, robots in robots_data.items():
        if system in system_id_list:
            for robot in robots:
                system_robots[system].append(robot["id"])
                robot_capacity[robot["id"]] = robot["max_canisters"] - len(disabled_locations[robot["id"]])

    return robot_ids, robots_data, robot_capacity, system_robots


@log_args_and_response
def get_canister_data(company_id, zone_list=[], ignore_reserved=False, system_id=None):
    drug_canisters = defaultdict(set)
    canister_location = dict()
    canister_data = dict()
    canister_expiry_status_dict = dict()
    drug_canisters_single = dict()
    query = CanisterMaster.select(
        CanisterMaster.id,
        LocationMaster.location_number,
        fn.IF(
            CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
            constants.EXPIRED_CANISTER,
            fn.IF(
                CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
        LocationMaster.quadrant,
        DeviceMaster.id.alias("device_id"),
        CanisterMaster.location_id,
        CanisterMaster.drug_id,
        DrugMaster.formatted_ndc,
        DrugMaster.txr,
        DrugMaster.ndc,
        DrugMaster.drug_name,
        DrugMaster.strength_value,
        DrugMaster.strength,
        DrugMaster.imprint,
        DrugMaster.shape,
        DrugMaster.color,
        DeviceMaster.name.alias('device_name'),
        LocationMaster.location_number,
        LocationMaster.is_disabled,
    ) \
        .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
        .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
        .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
        .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)

    if ignore_reserved:
        query = query.where(
            CanisterMaster.company_id == company_id,
            CanisterMaster.active == settings.is_canister_active,
            # CanisterZoneMapping.zone_id << self.zone_list
        )
    else:
        reserved_canister = ReservedCanister.select(ReservedCanister.canister_id) \
            .join(BatchMaster, on=BatchMaster.id == ReservedCanister.batch_id) \
            .join(CanisterMaster, on=CanisterMaster.id == ReservedCanister.canister_id) \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .where(CanisterMaster.company_id == company_id)

        """
        commented the below code:
        reason: due to the below check all the canisters which are reserved for the current progress batch
                are not consider as reserved in the recommendation of next upcoming batch and because of that 
                some of the reserved canisters also counted in the recommendation.
                To avoid this situation we commented the below check of system_id
        """
        # to consider canisters which are used in batch of given system in case when other batch of same
        # system is in progress
        if system_id:
            reserved_canister = reserved_canister.where(
                BatchMaster.system_id.not_in([system_id])
            )

        query = query.where(
            CanisterMaster.company_id == company_id,
            CanisterMaster.active == settings.is_canister_active,
            CanisterZoneMapping.zone_id << zone_list,
            CanisterMaster.id.not_in(reserved_canister))  # do not consider canister which are in use
    try:
        for record in query.dicts():
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"] if record["txr"] is not None else ''
            )
            if record["device_id"] is not None:
                canister_location[record["id"]] = (record["device_id"], record["location_number"], record['quadrant'],
                                                   record["is_disabled"])
            else:
                canister_location[record["id"]] = (record["device_name"], record["location_number"], record['quadrant'],
                                                   record["is_disabled"])
            canister_data[record["id"]] = record
            canister_expiry_status_dict[record["id"]] = record["expiry_status"]

            # todo change dynamic for 2x and 4x currently done for 1x
            # if fndc_txr not in drug_canisters_single.keys():
            drug_canisters[fndc_txr].add(record["id"])
            # if len(drug_canisters[fndc_txr]) <= 1:

    except Exception as e:
        logger.info(e)
        return e

    return canister_location, drug_canisters, canister_data, canister_expiry_status_dict


@log_args_and_response
def get_drug_canister_usage():
    drug_canister_usgae = dict()
    try:
        query = UniqueDrug.select().dicts().group_by(UniqueDrug.formatted_ndc, UniqueDrug.txr)
        for record in query:
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"] if record["txr"] is not None else ''
            )
            drug_canister_usgae[fndc_txr] = {"min": int(record["min_canister"]),
                                             "max": int(record['max_canister'])}

    except Exception as e:
        logger.info(e)
        raise e

    return drug_canister_usgae


@log_args_and_response
def get_robot_quadrant_enable_locations():
    robot_quadrant_enable_location: dict = dict()
    try:
        query = LocationMaster.select(LocationMaster).dicts()\
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id)\
            .where((LocationMaster.is_disabled == 0) &
                   (DeviceMaster.device_type_id == settings.DEVICE_TYPES["ROBOT"]) &
                   (~(LocationMaster.display_location % "M%")))

        for record in query:
            if record["device_id"] not in robot_quadrant_enable_location:
                robot_quadrant_enable_location[record["device_id"]] = dict()

            if record["quadrant"] not in robot_quadrant_enable_location[record["device_id"]]:
                robot_quadrant_enable_location[record["device_id"]][record["quadrant"]] = 0

            robot_quadrant_enable_location[record["device_id"]][record["quadrant"]] += 1
    except Exception as e:
        logger.error("Error in get_robot_quadrant_enable_locations: {}".format(e))
        raise e

    return robot_quadrant_enable_location

@log_args_and_response
def get_canister_qty(company_id, zone_list=[], ignore_reserved=False, system_id=None):
    drug_canisters = defaultdict(set)
    canister_location = dict()
    canister_data = dict()
    drug_canisters_single = dict()
    query = CanisterMaster.select(
        CanisterMaster.id,
        CanisterMaster.available_quantity,
    ) \
        .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \

    if ignore_reserved:
        query = query.where(
            CanisterMaster.company_id == company_id,
            CanisterMaster.active == settings.is_canister_active,
            # CanisterZoneMapping.zone_id << self.zone_list
        )
    else:
        reserved_canister = ReservedCanister.select(ReservedCanister.canister_id) \
            .join(BatchMaster, on=BatchMaster.id == ReservedCanister.batch_id) \
            .join(CanisterMaster, on=CanisterMaster.id == ReservedCanister.canister_id) \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .where(CanisterMaster.company_id == company_id)

        # to consider canisters which are used in batch of given system in case when other batch of same
        # system is in progress
        if system_id:
            reserved_canister = reserved_canister.where(
                BatchMaster.system_id.not_in([system_id])
            )

        query = query.where(
            CanisterMaster.company_id == company_id,
            CanisterMaster.active == settings.is_canister_active,
            CanisterZoneMapping.zone_id << zone_list,
            CanisterMaster.id.not_in(reserved_canister))  # do not consider canister which are in use
    try:
        canister_qty_dict = {}
        for record in query.dicts():
           canister_qty_dict[record['id']] = record['available_quantity']

    except Exception as e:
        logger.info(e)
        return e

    return canister_qty_dict


@log_args_and_response
def create_dataset(pack_set, drug_ids_set, pack_mapping):
    """ Takes the drug id and the pack id list and creates a dataframe for drug and pack mapping.

    Args:
        pack_set (set): The distinct set of the pack ids
        drug_ids_set (set): The distinct set of the drug ids
        pack_mapping (dict): The dict containing the mapping of pack ids and the drug ids

    Returns:
        pandas.dataframe

    Examples:
        >>> create_dataset([])
        pandas.DataFrame, []
    """
    try:
        df = pd.DataFrame(index=pack_set, columns=drug_ids_set)

        for key, value in pack_mapping.items():
            for item in value:
                df.ix[key][item] = value[item]
        df = df.fillna(0)

        return df, df.columns.tolist()

    except Exception as e:
        logger.error("Error in create_frame: ",str(e))


@log_args_and_response
def get_pack_data_query(pack_ids_list, pack_status_list):
    """
    Returns query for pack data required for pack distribution and distribution analysis
    :param pack_ids_list: list Pack List
    :param pack_status_list: list Status List
    :return: peewee.SelectQuery
    """
    return (
        PackRxLink.select(
            SlotDetails.drug_id,
            PackRxLink.pack_id,
            PackHeader.patient_id,
            PackHeader.scheduled_delivery_date.alias("delivery_date"),
            PatientMaster.facility_id,
            PackDetails.id.alias("pack_id"),
            fn.sum(fn.floor(fn.MOD(SlotDetails.quantity,1))).alias("floor_quantity"),
            fn.sum(SlotDetails.quantity).alias("quantity"),
            fn.group_concat(fn.distinct(SlotDetails.quantity)).alias('quantities'),
            DrugMaster.drug_name,
            DrugMaster.ndc,
            DrugMaster.strength,
            DrugMaster.txr,
            DrugMaster.strength_value,
            DrugMaster.image_name,
            DrugMaster.formatted_ndc,
            DrugMaster.imprint,
            DrugMaster.shape,
            DrugMaster.color,
            DrugMaster.id.alias('drug_id')
        )
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id)
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id)
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id)
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
            .where(PackDetails.id << pack_ids_list,
                   PackDetails.company_id,
                   PackDetails.pack_status << pack_status_list)
            .group_by(PackRxLink.pack_id, SlotDetails.drug_id))


@log_args_and_response
@validate(required_fields=['company_id'])
def recommend_canister_to_register(params):
    company_id = params['company_id']
    batch_id = params.get('batch_id', None)
    pharmacy_cycle = 14  # in days  # TODO load variable dynamically
    pack_ids_set = defaultdict(set)
    drug_ids_set = defaultdict(set)
    drug_canister = defaultdict(set)
    system_robots = dict()
    batch_system = dict()
    batch_pack_drug_qty = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    system_dfs = dict()
    canister_data = dict()
    system_drugs = defaultdict(set)
    response = list()

    try:
        if not batch_id:  # if not performing for a batch, then find last import date
            q = BatchMaster.select(BatchMaster.created_date) \
                .join(PackDetails, on=BatchMaster.id == PackDetails.batch_id) \
                .where(PackDetails.company_id == company_id,
                       PackDetails.pack_status != settings.DELETED_PACK_STATUS) \
                .order_by(BatchMaster.created_date.desc()) \
                .limit(1)
            try:
                last_imported_pack_date = q.get().created_date.date()
            except DoesNotExist as e:
                logger.info('last pack import date: NOT FOUND')
                # if no pack data found, consider current date
                last_imported_pack_date = datetime.utcnow().date()
            date_range = (str((last_imported_pack_date - datetime.timedelta(days=pharmacy_cycle))),
                          str(last_imported_pack_date))

        query = SlotDetails.select(
            fn.sum(fn.floor(SlotDetails.quantity)).alias("quantity"),
            PackRxLink.pack_id,
            SlotDetails.drug_id,
            PackDetails.batch_id, BatchMaster.system_id,
            DrugMaster
        ) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id)
        if not batch_id:
            query = query.where(PackDetails.company_id == company_id,
                                fn.DATE(BatchMaster.created_date).between(*date_range)
                                ) \
                .group_by(PackRxLink.pack_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                .having(SQL('quantity') > 0)
        else:
            query = query.where(PackDetails.company_id == company_id,
                                PackDetails.batch_id == batch_id
                                ) \
                .group_by(PackRxLink.pack_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                .having(SQL('quantity') > 0)
        for record in query.dicts():
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"]
            )
            batch_pack_drug_qty[record["batch_id"]][record["pack_id"]][fndc_txr] = record["quantity"]
            pack_ids_set[record['batch_id']].add(record['pack_id'])
            drug_ids_set[record['batch_id']].add(fndc_txr)
            batch_system[record['batch_id']] = record['system_id']
            canister_data[fndc_txr] = {
                'drug_id': record['drug_id'],
                'drug_name': record['drug_name'],
                'strength_value': record['strength_value'],
                'strength': record['strength'],
                'ndc': record['ndc'],
                'formatted_ndc': record['formatted_ndc'],
                'txr': record['txr'],
                'image_name': record['image_name'],
                'shape': record['shape'],
                'color': record['color'],
                'imprint': record['imprint'],
            }
            system_drugs[fndc_txr].add(record['system_id'])
        for batch, pack_data in batch_pack_drug_qty.items():
            df, _ = create_dataset(
                pack_ids_set[batch], drug_ids_set[batch], pack_data
            )
            system_dfs.setdefault(batch_system[batch], []).append(df)

        canister_query = CanisterMaster.select(
            CanisterMaster.id,
            DrugMaster.formatted_ndc, DrugMaster.txr
        ) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.active == settings.is_canister_active,
                   CanisterMaster.company_id == company_id)
        for record in canister_query.dicts():
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"]
            )
            drug_canister[fndc_txr].add(record['id'])
        for record in DeviceMaster.select() \
                .where(DeviceMaster.company_id == company_id,
                       DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']).dicts():
            system_robots.setdefault(record['system_id'], []).append(record['id'])

        recommender = MultiSystemCanisterRecommender(drug_canister_info_dict=drug_canister,
                                                     system_batchwise_df=system_dfs,
                                                     system_robot_info_dict=system_robots)
        recommendations, priority_drug_dict = recommender.multi_robot_recommend_canister_to_add_batchwise()

        for fndc_txr, qty in recommendations:
            if priority_drug_dict[fndc_txr] == 1:
                canister_data[fndc_txr]['canister_quantity'] = qty

        for fndc_txr, priority_flag in priority_drug_dict.items():
            canister_data[fndc_txr]['priority_flag'] = priority_drug_dict[fndc_txr]
            response.append(canister_data[fndc_txr])
        return create_response(response)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=['company_id', 'batch_id'])
def recommend_canister_to_register_optimised(params):
    company_id = params['company_id']
    number_of_drugs_needed = params.get('number_of_drugs_needed', None)
    drugs_to_register = params.get('drugs_to_register', None)
    batch_id = params.get('batch_id', None)
    pharmacy_cycle = 14  # in days  # TODO load variable dynamically
    pack_ids_set = defaultdict(set)
    drug_ids_set = defaultdict(set)
    drug_canister = defaultdict(set)
    system_robots = dict()
    batch_system = dict()
    batch_pack_drug_qty = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    system_dfs = dict()
    canister_data = dict()
    system_drugs = defaultdict(set)
    drugs_to_register_response = []
    response = {}
    drugid_fndc_txr_dict = dict()
    required_drug_list = list()

    try:
        if drugs_to_register is not None:
            drugs_to_register = list(map(int, drugs_to_register.split(',')))

        if not batch_id:  # if not performing for a batch, then find last import date
            q = BatchMaster.select(BatchMaster.created_date) \
                .join(PackDetails, on=BatchMaster.id == PackDetails.batch_id) \
                .where(PackDetails.company_id == company_id,
                       PackDetails.pack_status != settings.DELETED_PACK_STATUS) \
                .order_by(BatchMaster.created_date.desc()) \
                .limit(1)
            try:
                last_imported_pack_date = q.get().created_date.date()
            except DoesNotExist as e:
                logger.info('last pack import date: NOT FOUND')
                # if no pack data found, consider current date
                last_imported_pack_date = datetime.utcnow().date()
            date_range = (str((last_imported_pack_date - datetime.timedelta(days=pharmacy_cycle))),
                          str(last_imported_pack_date))

        query = SlotDetails.select(
            fn.sum(fn.floor(SlotDetails.quantity)).alias("quantity"),
            PackRxLink.pack_id,
            SlotDetails.drug_id,
            PackDetails.batch_id, BatchMaster.system_id,
            DrugMaster
        ) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id)
        if not batch_id:
            query = query.where(PackDetails.company_id == company_id,
                                fn.DATE(BatchMaster.created_date).between(*date_range)
                                ) \
                .group_by(PackRxLink.pack_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                .having(SQL('quantity') > 0)
        else:
            query = query.where(PackDetails.company_id == company_id,
                                PackDetails.batch_id == batch_id,
                                # PackDetails.pack_status == 2
                                ) \
                .group_by(PackRxLink.pack_id, DrugMaster.formatted_ndc, DrugMaster.txr) \
                .having(SQL('quantity') > 0)
        for record in query.dicts():
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"]
            )
            batch_pack_drug_qty[record["batch_id"]][record["pack_id"]][fndc_txr] = record["quantity"]
            pack_ids_set[record['batch_id']].add(record['pack_id'])
            drug_ids_set[record['batch_id']].add(fndc_txr)
            batch_system[record['batch_id']] = record['system_id']
            canister_data[fndc_txr] = {
                'drug_id': record['drug_id'],
                'drug_name': record['drug_name'],
                'strength_value': record['strength_value'],
                'strength': record['strength'],
                'ndc': record['ndc'],
                'formatted_ndc': record['formatted_ndc'],
                'txr': record['txr'],
                'image_name': record['image_name'],
                'shape': record['shape'],
                'color': record['color'],
                'imprint': record['imprint'],
            }
            drugid_fndc_txr_dict[canister_data[fndc_txr]['drug_id']] = fndc_txr
            if drugs_to_register is not None:
                for drug_id in drugs_to_register:
                    for drug, fndc_txr in drugid_fndc_txr_dict.items():
                        if drug == drug_id:
                            required_drug_list.append(fndc_txr)
            system_drugs[fndc_txr].add(record['system_id'])
        required_drug_list = list(set(required_drug_list))
        for batch, pack_data in batch_pack_drug_qty.items():
            df, _ = create_dataset(
                pack_ids_set[batch], drug_ids_set[batch], pack_data
            )
            system_dfs.setdefault(batch_system[batch], []).append(df)

        canister_query = CanisterMaster.select(
            CanisterMaster.id,
            DrugMaster.formatted_ndc, DrugMaster.txr
        ) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.active == settings.is_canister_active,
                   CanisterMaster.company_id == company_id)
        for record in canister_query.dicts():
            fndc_txr = "{}{}{}".format(
                record["formatted_ndc"], settings.SEPARATOR, record["txr"]
            )
            drug_canister[fndc_txr].add(record['id'])
        for record in DeviceMaster.select() \
                .where(DeviceMaster.company_id == company_id,
                       DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']).dicts():
            system_robots.setdefault(record['system_id'], []).append(record['id'])

        recommender = MultiSystemCanisterRecommender(drug_canister_info_dict=drug_canister,
                                                     system_batchwise_df=system_dfs,
                                                     system_robot_info_dict=system_robots)
        default_split, drug_split_info = recommender.multi_robot_recommend_canister_to_add_batchwise_optimised(
            number_of_drugs_needed, required_drug_list)

        # if 'default_split' in drug_split_info:
        #     response.append(default_split['default_split'])
        split_info = {}

        if 'new_split' not in drug_split_info:
            for drug, split_info in drug_split_info.items():
                canister_data[drug]['split_info'] = {}
                canister_data[drug]['split_info']['Robot-1 pack_length'] = split_info['Robot-1 Pack_length']
                canister_data[drug]['split_info']['Robot-2 pack_length'] = split_info['Robot-2 pack_length']
                canister_data[drug]['split_info']['Common packs'] = split_info['Common packs']
                canister_data[drug]['canister_quantity'] = split_info['qty']
                drugs_to_register_response.append(canister_data[drug])
            # drugs_to_register_response.append(default_split)
            response["default_split"] = default_split['default_split']
            response["drugs_to_register"] = drugs_to_register_response
            return create_response(response)
        else:
            response["new_split"] = drug_split_info['new_split']
            response["default_split"] = default_split['default_split']
            # response = set(response)
            return create_response(response)

        # for fndc_txr, qty in recommendations:
        #     for i in range(qty):
        #         canister_data[fndc_txr]['canister_quantity'] = qty
        #         if fndc_txr in drug_split_info.keys():
        #             response.append(canister_data[fndc_txr])
        # return create_response(response,default_split)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_empty_locations(device_ids, packdistribution=False):
    """
        Returns empty locations for given robot ids

    @param device_ids:
    @param packdistribution:
    @return:
    """
    try:
        if packdistribution:
            empty_locations = {x: set([i for i in range(1, device_ids[x] + 1)]) for x in device_ids}
        else:
            empty_locations = LocationMaster.get_display_locations_from_device_ids(device_ids)
        # filling with all locations first
        locations = {x: set() for x in device_ids}
        device_id_list = list(device_ids.keys())

        if device_ids:
            for record in CanisterMaster.select(LocationMaster.device_id, LocationMaster.display_location,
                                                LocationMaster.location_number).dicts() \
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                    .where((CanisterMaster.location_id > 0 | LocationMaster.is_disabled == settings.is_location_active),
                           LocationMaster.device_id << device_id_list,
                           CanisterMaster.active == settings.is_canister_active):
                if packdistribution:
                    locations[record['device_id']].add(record['location_number'])
                else:
                    locations[record['device_id']].add((record["display_location"], record["location_number"]))
            for k, v in locations.items():
                empty_locations[k] -= locations[k]
        return empty_locations
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args
def cr_analysis_fetch_data(batch_id):
    try:
        robot_2_count = 0
        robot_3_count = 0
        analysis_dict = defaultdict()
        canister_2_data1 = 0
        canister_2_data2 = 0
        canister_2_data3 = 0
        canister_2_data4 = 0
        canister_3_data1 = 0
        canister_3_data2 = 0
        canister_3_data3 = 0
        canister_3_data4 = 0
        drug_wise_canister_count = defaultdict()
        batch_manual_drug = []
        query = PackAnalysis.select(PackAnalysisDetails.device_id,
                                    PackAnalysis.pack_id,
                                    fn.MAX(PackAnalysisDetails.drop_number).alias('drop_number')).dicts()\
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id==PackAnalysis.id)\
            .where(PackAnalysis.batch_id == batch_id)\
            .group_by(PackAnalysisDetails.device_id, PackAnalysis.pack_id)

        for record in query:
            if record['device_id']:
                # if record['device_id'] not in analysis_dict.keys():
                #     analysis_dict[record['device_id']] = {}
                #     analysis_dict[record['device_id']][record['pack_id']] = record['drop_number']
                # else:
                #     analysis_dict[record['device_id']][record['pack_id']] = record['drop_number']
                #
                # # analysis_dict[record['device_id']] += record['drop_number']
                if record['device_id'] in [2, '2']:
                    robot_2_count += record['drop_number'] if record['drop_number'] else 0
                if record['device_id'] in [3, '3']:
                    robot_3_count += record['drop_number'] if record['drop_number'] else 0
                # analysis_dict[record['device_id']]['drop_count'] = drop_count

        DrugMasterAlias = DrugMaster.alias()
        manual_drug = PackAnalysis.select(SlotDetails.drug_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .where(PackAnalysis.batch_id == batch_id, PackAnalysisDetails.canister_id.is_null(True),
                   PackAnalysisDetails.config_id.is_null(True)).group_by(SlotDetails.drug_id)
            # .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            # .join(DrugMasterAlias, on=(
            #         DrugMasterAlias.formatted_ndc == DrugMaster.formatted_ndc and DrugMasterAlias.txr == DrugMaster.txr)) \
            # .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMasterAlias.id) \


        query = PackAnalysis.select(PackAnalysisDetails.device_id, PackAnalysisDetails.quadrant,
                                    fn.COUNT(fn.DISTINCT(PackAnalysisDetails.canister_id)).alias("canister_count")).dicts() \
                    .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                    .where(PackAnalysis.batch_id == batch_id) \
                    .group_by(PackAnalysisDetails.device_id, PackAnalysisDetails.quadrant)
        for record in query:
            if record['device_id'] in [2, '2']:
                if record['quadrant'] ==1:
                    canister_2_data1 = record['canister_count']
                if record['quadrant'] ==2:
                    canister_2_data2 = record['canister_count']
                if record['quadrant'] ==3:
                    canister_2_data3 = record['canister_count']
                if record['quadrant'] ==4:
                    canister_2_data4 = record['canister_count']

            if record['device_id'] in [3, '3']:
                if record['quadrant'] ==1:
                    canister_3_data1 = record['canister_count']
                if record['quadrant'] ==2:
                    canister_3_data2 = record['canister_count']
                if record['quadrant'] ==3:
                    canister_3_data3 = record['canister_count']
                if record['quadrant'] ==4:
                    canister_3_data4 = record['canister_count']

        drug_wise_canister_count = PackAnalysis.select(DrugMaster.concated_fndc_txr_field().alias('drug'), fn.COUNT(fn.DISTINCT(CanisterMaster.id)).alias('canister_count')).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(PackAnalysis.batch_id == batch_id).group_by(DrugMaster.concated_fndc_txr_field())

        total_packs = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.batch_id == batch_id,
                                                                         PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        return robot_2_count, robot_3_count, canister_2_data1,canister_2_data2,canister_2_data3,canister_2_data4,canister_3_data1,canister_3_data2,canister_3_data3,canister_3_data4, manual_drug.scalar(), total_packs.scalar()
    except Exception as e:
        raise


@log_args_and_response
def get_packs_to_be_filled_by_canister(device_id, canister_ids):
    try:
        batch_id = None
        packs_to_reconfigure = []
        packs_of_canister = PackDetails.select(PackDetails.id,
                                               PackDetails.batch_id
                                               ).dicts()\
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
            .where(PackAnalysisDetails.canister_id << canister_ids, PackAnalysisDetails.device_id == device_id,
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS).group_by(PackDetails.id)

        for record in packs_of_canister:
            packs_to_reconfigure.append(record['id'])

            if not batch_id:
                batch_id = record["batch_id"]

        return packs_to_reconfigure, batch_id
    except Exception as e:
        logger.error("Error in get_packs_to_be_filled_by_canister {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_affected_pack_list_for_canisters(canister_list):
    try:
        CanisterMasterAlias = CanisterMaster.alias()
        device_wise_canisters = {2:set(),
                                 3: set()}
        drug_canisters = []
        fndc_txr_query = (CanisterMaster.select(DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr"),
                                                CanisterMaster.id.alias("canister_id"),
                                                LocationMaster.device_id)
                          .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)
                          .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id)
                          .where(CanisterMaster.id << canister_list))
        for record in fndc_txr_query.dicts():
            fndc_txr = record['fndc_txr']
        device_id = None
        affected_pack_list = []
        device_wise_packs = {}
        query = (PackDetails.select(PackDetails.id,
                                    SlotDetails.drug_id,
                                    PackAnalysisDetails.device_id.alias("dest_device_id"),
                                    PackAnalysisDetails.canister_id.alias("canister_id"),
                                    )
                 .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id)
                 .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id)
                 .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id)
                 .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                 .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id)
                 .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id)
                 .where(DrugMaster.concated_fndc_txr_field(sep="##") == fndc_txr,
                        PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                        BatchMaster.status == settings.BATCH_IMPORTED,
                        CanisterMaster.active == settings.is_canister_active
                        )
                 )
        for record in query.dicts():
            device_wise_canisters.setdefault(record['dest_device_id'], set())
            device_wise_canisters[record['dest_device_id']].add(record['canister_id'])

            device_wise_packs.setdefault(record['dest_device_id'], set())
            device_wise_packs[record['dest_device_id']].add(record['id'])

        for device_id, canisters in device_wise_canisters.items():
            if len(canisters) == len(drug_canisters):
                for dest_device_id, packs in device_wise_packs.items():
                    if len(packs) > len(affected_pack_list):
                        affected_pack_list = packs
                        device_id = dest_device_id
            elif len(canisters) < len(drug_canisters):
                drug_canisters = canisters
                device_id = device_id
                affected_pack_list = device_wise_packs[device_id]
        # for dest_device_id, packs in device_wise_packs.items():
        #     if len(packs) > len(affected_pack_list):
        #         affected_pack_list = packs
        #         device_id = dest_device_id

        return list(affected_pack_list), device_id

    except Exception as e:
        raise e


@log_args_and_response
def db_get_canister_reverted_packs(device_id, canister_id):
    try:
        packs_to_reconfigure = []
        canister_quad = int()
        packs_of_canister = PackDetails.select(PackDetails.id, ReplenishSkippedCanister.quadrant).dicts().join(PackAnalysis,
                                                                            on=PackAnalysis.pack_id == PackDetails.id) \
            .join(ReplenishSkippedCanister, on=ReplenishSkippedCanister.pack_id == PackDetails.id) \
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
            .where(ReplenishSkippedCanister.canister_id << canister_id, ReplenishSkippedCanister.device_id == device_id,
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS).group_by(PackDetails.id)

        for record in packs_of_canister:
            packs_to_reconfigure.append(record['id'])
            canister_quad = record['quadrant']
        return packs_to_reconfigure, canister_quad
    except Exception as e:
        logger.error("Error in get_packs_to_be_filled_by_canister {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_multi_canister_drug_data_by_canister(canister_list, device_id, batch_id=None, pack_queue=False):
    fndc_txr_canister_dict = defaultdict(list)
    multi_canister_fndc_txr = dict()
    try:
        # txr = CanisterMaster.select(DrugMaster.txr).join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id).where(
        #     CanisterMaster.id << canister_list).group_by(DrugMaster.txr)

        fndc_txr = CanisterMaster.select(DrugMaster.concated_fndc_txr_field(sep="##"))\
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            .where(CanisterMaster.id << canister_list).group_by(DrugMaster.concated_fndc_txr_field(sep="##"))

        query = PackAnalysis.select(PackAnalysisDetails.device_id, PackAnalysisDetails.canister_id,
                                    PackAnalysisDetails.quadrant,
                                    DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr")).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)
        if pack_queue:
            query = query.join(PackQueue, on=PackQueue.pack_id == PackAnalysis.pack_id)
        elif batch_id:
            query = query.where(PackAnalysis.batch_id == batch_id)

        # query = query.where(DrugMaster.txr << txr, PackAnalysisDetails.device_id == device_id, PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        query = query.where(DrugMaster.concated_fndc_txr_field(sep="##") << fndc_txr,
                            PackAnalysisDetails.device_id == device_id,
                            PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        logger.info(f"in get_multi_canister_drug_data_by_canister - query is {query}")
        for record in query:
            if record['canister_id'] not in fndc_txr_canister_dict[record['fndc_txr']]:
                fndc_txr_canister_dict[record['fndc_txr']].append(record['canister_id'])

        # multi_canister_fndc_txr = {key: value for key, value in fndc_txr_canister_dict.items() if len(value) > 1}

        for key, value in fndc_txr_canister_dict.items():
            if len(value) > 1:
                all_can_skip = True
                for can in value:
                    if can not in canister_list:
                        all_can_skip = False
                        break
                if not all_can_skip:
                    multi_canister_fndc_txr[key] = value

        all_can = [can for value in multi_canister_fndc_txr.values() for can in value]

        return multi_canister_fndc_txr, all_can

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_affected_pack_list(can_list, device_id, batch_id):
    affected_pack_list = list()
    try:
        query = PackDetails.select(PackDetails.id.alias("pack_id")).dicts()\
            .join(PackAnalysis, on=PackDetails.id == PackAnalysis.pack_id)\
            .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
            .where((PackAnalysisDetails.canister_id << can_list) &
                   (PackAnalysisDetails.device_id == device_id) &
                   (PackDetails.pack_status == settings.PENDING_PACK_STATUS) &
                   (PackDetails.batch_id == batch_id)
                   )\
            .group_by(PackDetails.id)

        for record in query:
            affected_pack_list.append(record["pack_id"])

        return affected_pack_list
    except Exception as e:
        logger.error("Error in db_get_affected_pack_list: {}".format(e))
        raise e


@log_args_and_response
def db_get_pending_pack_list(pack_list):
    packs = list()
    try:
        query = PackDetails.select(PackDetails.id.alias("pack_id"),
                                   PackDetails.pack_status
                                   ).dicts()\
            .where(PackDetails.id << pack_list)

        for record in query:
            if record["pack_status"] == settings.PENDING_PACK_STATUS:
                if record["pack_id"] not in packs:
                    packs.append(record["pack_id"])

        return packs
    except Exception as e:
        logger.error("Error in db_get_pending_pack_list: {}".format(e))
        raise e
