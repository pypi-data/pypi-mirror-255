import csv
import logging
from peewee import *
from dosepack.base_model.base_model import db
from model.model_canister import CanisterMaster
from src.model.model_generate_canister import GenerateCanister
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_history import CanisterHistory
from src.model.model_group_master import GroupMaster
from src.model.model_action_master import ActionMaster
from src.model.model_reason_master import ReasonMaster
from src.model.model_code_master import CodeMaster
from model.model_drug import ImportedDrug
from src.model.model_dosage_type import DosageType
from src.model.model_drug_sync_log import DrugSyncLog
from src.model.model_drug_sync_history import DrugSyncHistory
from src.model.model_imported_drug_image import ImportedDrugImage
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from model.model_misc import CompanySetting, FileDownloadTracker, SystemSetting
from src.model.model_print_queue import PrintQueue
from src.model.model_printers import Printers
from src.model.model_pack_grid import PackGrid
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster
from model.model_volumetric_analysis import BigCanisterStick, CanisterParameters, SmallCanisterStick, CanisterStick
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_zone_master import ZoneMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pvs_dimension import PVSDimension

# get the logger for the pack from global configuration file logging.json
from dosepack.utilities.utils import get_current_date_time, get_current_date, get_current_time
from model.model_init import init_db

logger = logging.getLogger("root")


def add_data_in_tables():
    # group_master
    grp_dict = list(csv.DictReader(open("path_to_csv/group_master.csv", "r")))
    for data in grp_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # action_master
    act_dict = list(csv.DictReader(open("path_to_csv/action_master.csv", "r")))
    for data in act_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # big_canister_stick
    bcs_dict = list(csv.DictReader(open("path_to_csv/big_canister_stick.csv", "r")))
    for data in bcs_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # code_master
    cm_dict = list(csv.DictReader(open("path_to_csv/code_master.csv", "r")))
    for data in cm_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # company_setting
    cs_dict = list(csv.DictReader(open("path_to_csv/company_setting.csv", "r")))
    for data in cs_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # custom_drug_shape
    cds_dict = list(csv.DictReader(open("path_to_csv/custom_drug_shape.csv", "r")))
    for data in cds_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # device_type_master
    dtm_dict = list(csv.DictReader(open("path_to_csv/device_type_master.csv", "r")))
    for data in dtm_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # device_master
    dm_dict = list(csv.DictReader(open("path_to_csv/device_master.csv", "r")))
    for data in dm_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None
    # container_master
    container_dict = list(csv.DictReader(open("path_to_csv/container_master.csv", "r")))
    for data in container_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # unit_master
    um_dict = list(csv.DictReader(open("path_to_csv/unit_master.csv", "r")))
    for data in um_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # zone_master
    zm_dict = list(csv.DictReader(open("path_to_csv/zone_master.csv", "r")))
    for data in zm_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # device_layout_details
    dld_dict = list(csv.DictReader(open("path_to_csv/device_layout_details.csv", "r")))
    for data in dld_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # system_setting
    ss_dict = list(csv.DictReader(open("path_to_csv/system_setting.csv", "r")))
    for data in ss_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # pvs_dimension
    pd_dict = list(csv.DictReader(open("path_to_csv/pvs_dimension.csv", "r")))
    for data in pd_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # printers
    pr_dict = list(csv.DictReader(open("path_to_csv/printers.csv", "r")))
    for data in pr_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # location_master
    loc_dict = list(csv.DictReader(open("path_to_csv/location_master.csv", "r")))
    for data in loc_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # drug_master
    drug_dict = list(csv.DictReader(open("path_to_csv/drug_master.csv", "r")))
    # for data in drug_dict:
    #     for k, v in data.items():
    #         if v == 'NULL':
    #             data[k] = None

    # unique_drug
    ud_dict = list(csv.DictReader(open("path_to_csv/unique_drug.csv", "r")))
    for data in ud_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # canister_master
    can_dict = list(csv.DictReader(open("path_to_csv/canister_master.csv", "r")))
    for data in can_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None

    # pack_grid_dict
    grid_dict = list(csv.DictReader(open("path_to_csv/pack_grid.csv", "r")))
    for data in grid_dict:
        for k, v in data.items():
            if v == 'NULL':
                data[k] = None
    try:
        with db.transaction():
            GroupMaster.insert_many(grp_dict).execute()
            print("Data Added in GroupMaster")
            ActionMaster.insert_many(act_dict).execute()
            print("Data Added in ActionMaster")
            BigCanisterStick.insert_many(bcs_dict).execute()
            print("Data Added in BigCanisterStick")
            CodeMaster.insert_many(cm_dict).execute()
            print("Data Added in CodeMaster")
            CompanySetting.insert_many(cs_dict).execute()
            print("Data Added in CompanySetting")
            CustomDrugShape.insert_many(cds_dict).execute()
            print("Data Added in CustomDrugShape")
            DeviceTypeMaster.insert_many(dtm_dict).execute()
            print("Data Added in DeviceTypeMaster")
            DeviceMaster.insert_many(dm_dict).execute()
            print("Data Added in DeviceMaster")
            ContainerMaster.insert_many(container_dict).execute()
            print("Data Added in ContainerMaster")
            UnitMaster.insert_many(um_dict).execute()
            print("Data Added in UnitMaster")
            ZoneMaster.insert_many(zm_dict).execute()
            print("Data Added in ZoneMaster")
            DeviceLayoutDetails.insert_many(dld_dict).execute()
            print("Data Added in DeviceLayoutDetails")
            SystemSetting.insert_many(ss_dict).execute()
            print("Data Added in SystemSetting")
            PVSDimension.insert_many(pd_dict).execute()
            print("Data Added in PVSDimension")
            Printers.insert_many(pr_dict).execute()
            print("Data Added in Printers")
            LocationMaster.insert_many(loc_dict).execute()
            print("Data Added in LocationMaster")
            DrugMaster.insert_many(drug_dict).execute()
            print("Data Added in DrugMaster")
            UniqueDrug.insert_many(ud_dict).execute()
            print("Data Added in UniqueDrug")
            CanisterMaster.insert_many(can_dict).execute()
            print("Data Added in CanisterMaster")
            PackGrid.insert_many(grid_dict).execute()
            print("Data Added in PackGrid")

    except (IntegrityError, InternalError) as e:
        raise e


def migration_action_data():
    init_db(db, 'database_migration')
    add_data_in_tables()
