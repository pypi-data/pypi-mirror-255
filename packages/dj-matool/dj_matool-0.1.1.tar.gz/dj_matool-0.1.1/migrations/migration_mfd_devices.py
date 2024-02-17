import logging

from src import constants
from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.service.zone import prepare_data_for_device_locations_trolley, prepare_data_for_device_locations, \
    prepare_data_for_robot_mfd_locations
from src.model.model_container_master import ContainerMaster

from string import ascii_uppercase

logger = logging.getLogger("root")


class GroupMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=20, unique=True)
    device_code = CharField(max_length=10)
    container_code = CharField(max_length=10)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=20)
    serial_number = CharField(max_length=20, unique=True)
    device_type_id = ForeignKeyField(DeviceTypeMaster)
    system_id = IntegerField(null=True)
    version = CharField(null=True)
    active = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    associated_device = ForeignKeyField('self', null=True)
    ip_address = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


# class ContainerMaster(BaseModel):
#     id = PrimaryKeyField()
#     device_id = ForeignKeyField(DeviceMaster)
#     drawer_name = CharField(max_length=20)
#     ip_address = CharField(max_length=20, null=True)
#     secondary_ip_address = CharField(max_length=20, null=True)
#     mac_address = CharField(max_length=50, null=True)
#     secondary_mac_address = CharField(max_length=50, null=True)
#     drawer_level = IntegerField(null=True)
#     created_by = IntegerField(null=True)
#     modified_by = IntegerField(null=True)
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     drawer_type = ForeignKeyField(CodeMaster, default=77, related_name="drawer_type")
#     drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")
#     shelf = IntegerField(null=True)
#     serial_number = CharField(max_length=20, null=True)
#     lock_status = BooleanField(default=False)  # True-open and False-close
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "container_master"
#
#         indexes = (
#             (('device_id', 'drawer_number', 'ip_address'), True),
#         )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster, related_name='location_container_id')
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class UnitMaster(BaseModel):
    """
    Class to store the unit details.
    """
    id = PrimaryKeyField()
    name = CharField()
    type = CharField()
    symbol = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unit_master"


class ZoneMaster(BaseModel):
    """
        @desc: Class to store the zone details of company.
    """
    id = PrimaryKeyField()
    name = CharField(max_length=25)
    floor = IntegerField(null=True)
    length = DecimalField(decimal_places=2, null=True)
    height = DecimalField(decimal_places=2, null=True)
    width = DecimalField(decimal_places=2, null=True)
    company_id = IntegerField()  # Foreign key field of company table of dp auth
    x_coordinate = DecimalField(decimal_places=2, null=True)
    y_coordinate = DecimalField(decimal_places=2, null=True)
    dimensions_unit_id = ForeignKeyField(UnitMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "zone_master"
        indexes = (
            (('company_id', 'name'), True),
        )


class DeviceLayoutDetails(BaseModel):
    """
    Class to store the inventory layout related details of various devices.
    """
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, null=True, unique=True, related_name='device_layout_device_id')
    zone_id = ForeignKeyField(ZoneMaster, null=True, related_name='device_zone_id')
    x_coordinate = DecimalField(decimal_places=2, null=True)
    y_coordinate = DecimalField(decimal_places=2, null=True)
    marked_for_transfer = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_layout_details"


def insert_mfd_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:

        drawer_ids_list = [(1, [1, 2]), (2, [3, 4]), (3, [5, 6]), (4, [7, 8]), (5, [9, 10]),
                           (6, [11, 12]), (7, [13, 14]), (8, [15, 16])]

        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            index = DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST.index(device)
            data_list = []
            drawer_list = []
            drawer_id = ContainerMaster.get_max_drawer_id()
            if device_type == "Manual Canister Cart":
                loc_num = 0
                locations_data, drawer_data, drawer_id, latest_num = prepare_data_for_device_locations_trolley(
                    total_drawers=device['total_drawers'],
                    locations_per_drawer=20,
                    device_id=device['device_id'],
                    drawer_per_row=16,
                mfd=True)
                # for each_drawer_data in drawer_ids_list:
                #     drawer_level, ed = each_drawer_data
                #     locations_data, drawer_data, drawer_id_updated, loc_num_updated = prepare_data_for_device_locations(
                #         total_drawers=1,
                #         locations_per_drawer=20,
                #         device_id=device['device_id'],
                #         drawer_per_row=2, quadrant_avialable=False,
                #         drawer_id_list=ed,
                #         drawer_id=drawer_id,
                #         loc_num=loc_num,
                #         drawer_level=drawer_level)
                #

                drawer_id = drawer_id
                drawer_list.extend(drawer_data)
                data_list.extend(locations_data)
            else:
                logger.error("not valid device type")
            # data_list.update(locations_data)
            print(drawer_list)
            print('**********************************************************************')
            print(data_list)
            ContainerMaster.insert_many(drawer_list).execute()
            LocationMaster.insert_many(data_list).execute()
    except DoesNotExist as ex:
        print(ex)
        raise DoesNotExist
    except InternalError as e:
        print(e)
        raise InternalError

    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def insert_trolley_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:
        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            data_list = []
            drawer_list = []
            if device_type == "Canister Transfer Cart":
                locations_data, drawer_data, drawer_id, latest_num = prepare_data_for_device_locations_trolley(
                    total_drawers=device['total_drawers'],
                    locations_per_drawer=20,
                    device_id=device['device_id'],
                    drawer_per_row=2)

            else:
                locations_data, drawer_data, drawer_id, latest_num = prepare_data_for_device_locations_trolley(
                    total_drawers=6,
                    locations_per_drawer=device.get(
                        'locations_per_drawer', 20),
                    device_id=device['device_id'],
                    drawer_per_row=4,
                    quadrant_avialable=False)

            data_list.extend(locations_data)
            drawer_list.extend(drawer_data)
            print('**********************************************************************')
            print(data_list)
            ContainerMaster.insert_many(drawer_list).execute()
            LocationMaster.insert_many(data_list).execute()
    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def add_devices(company_id: int, device_dict: dict, device_type_list: list = None, zone_id: int = None):
    """
    To add device data in device_type_master, device_master, container_master, location_master
    @param zone_id: int
    @param company_id: int
    @param device_dict: {"device_type_name":[{"device_name":value, "system_id"}]}
    @param device_type_list: [{"device_type_name":value,"device_code":value, "container_code":value}]
    @return:
    """
    try:
        # Adding device type if any new device type is added and fetch device_type_id of device_type
        device_type_name_id_dict = dict()
        for device_type in device_type_list:
            device_type_record, created = DeviceTypeMaster.get_or_create(**device_type)
            if created:
                logger.debug("Added device_type: {} with id - {}".format(device_type, device_type_record.id))
            device_type_name_id_dict[device_type_record.device_type_name] = device_type_record.id

        # Add device data in device_master
        for device_type, device_list in device_dict.items():
            logger.info("Data addition initiated")
            CURRENT_DATE = get_current_date_time()

            if device_type == "Manual Canister Cart":
                logger.info("adding manual canister cart")
                mfd_trolley_devices = list()
                for device in device_list:
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Manual Canister Cart"]
                    device["version"] = 2.0
                    device.update(data_dict)

                    #  add data in device master
                    new_device_id, created = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id, created = DeviceLayoutDetails.get_or_create(**device_layout_dict)
                    logger.info(device_layout_id)

                    location_data = {"device_id": new_device_id.id, "total_drawers": 16, "locations_per_drawer": 20}
                    mfd_trolley_devices.append(location_data)

                insert_mfd_location_data(mfd_trolley_devices, "Manual Canister Cart")
                print("data inserted in location master regular trolley")
                logger.info("manual canister cart added")

            if device_type == "Manual Filling Device":
                logger.info("adding MFD")
                total_drawers = 2
                drawer_per_row = 1
                location_per_drawer = 8
                all_drawer_data = list()
                for device in device_list:
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Manual Filling Device"]
                    device["version"] = 2.0
                    device.update(data_dict)

                    #  add data in device master
                    new_device_id, created = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id, created = DeviceLayoutDetails.get_or_create(**device_layout_dict)

                    try:
                        max_location_number = LocationMaster.select(
                            fn.MAX(LocationMaster.location_number).alias('max_loc_id')
                        ).dicts() \
                            .where(LocationMaster.device_id == new_device_id.id).get()
                        max_location_number = max_location_number['max_loc_id']
                        if max_location_number is None:
                            max_location_number = 0
                        print(max_location_number)
                    except DoesNotExist as e:
                        max_location_number = 0
                    for i in range(0, total_drawers):
                        drawer_initial = str(ascii_uppercase[i])

                        for i in range(1, drawer_per_row + 1):
                            drawer_data = {'device_id': new_device_id.id,
                                           'drawer_name': '{}-{}'.format(drawer_initial, i),
                                           'drawer_type': settings.SIZE_OR_TYPE["MFD"]}
                            print(drawer_data)
                            drawer_record = BaseModel.db_create_record(drawer_data, ContainerMaster,
                                                                       get_or_create=False)

                            location_drawer_initial = '{}{}'.format(drawer_initial, i)
                            drawer_data = prepare_data_for_robot_mfd_locations(location_per_drawer,
                                                                               new_device_id.id,
                                                                               drawer_record.id,
                                                                               max_location_number,
                                                                               original_drawer_number=i,
                                                                               drawer_initial_name=location_drawer_initial,
                                                                               drawer_per_row=10,
                                                                               quadrant_avialable=False)
                            all_drawer_data.extend(drawer_data)
                            max_location_number = max_location_number + location_per_drawer
                        print(all_drawer_data)
                if all_drawer_data:
                    LocationMaster.insert_many(all_drawer_data).execute()

                logger.info("MFD added")

    except Exception as e:
        logger.error("Exception while adding device data: " + str(e))
        raise


def migrate_add_all_devices(zone_id = 1, company_id = 4, system_id = 11,
                            mfd_system_id_1=16,
                            mfd_system_id_2=17,
                            mfd_system_id_3=18,
                            mfd_system_id_4=19):
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    robot_system_id = system_id
    mfd_system_id_1 = mfd_system_id_1
    mfd_system_id_2 = mfd_system_id_2
    mfd_system_id_3 = mfd_system_id_3
    mfd_system_id_4 = mfd_system_id_4

    # with db.transaction():
    if company_id:

        # add and map device data
        device_type_list = [

            {"device_type_name": "Manual Filling Device", "device_code": "MFD", "container_code": "MDD"},
            {"device_type_name": "Manual Canister Cart", "device_code": "MCC", "container_code": "MCD"},

        ]
        device_dict = {

            "Manual Filling Device": [
                {"name": "Manual Filling Device - 01", "system_id": mfd_system_id_1, "serial_number": "MFD00001"},
                {"name": "Manual Filling Device - 02", "system_id": mfd_system_id_2, "serial_number": "MFD00002"},
                {"name": "Manual Filling Device - 03", "system_id": mfd_system_id_3, "serial_number": "MFD00003"},
                {"name": "Manual Filling Device - 04", "system_id": mfd_system_id_4, "serial_number": "MFD00004"},
            ],

            "Manual Canister Cart": [
                {"name": "Manual Canister Cart - 01", "system_id": robot_system_id, "serial_number": "MCC00001"},
                {"name": "Manual Canister Cart - 02", "system_id": robot_system_id, "serial_number": "MCC00002"},
                {"name": "Manual Canister Cart - 03", "system_id": robot_system_id, "serial_number": "MCC00003"},
                {"name": "Manual Canister Cart - 04", "system_id": robot_system_id, "serial_number": "MCC00004"},
                {"name": "Manual Canister Cart - 05", "system_id": robot_system_id, "serial_number": "MCC00005"},
                {"name": "Manual Canister Cart - 06", "system_id": robot_system_id, "serial_number": "MCC00006"},
                {"name": "Manual Canister Cart - 07", "system_id": robot_system_id, "serial_number": "MCC00007"},
                {"name": "Manual Canister Cart - 08", "system_id": robot_system_id, "serial_number": "MCC00008"},
                {"name": "Manual Canister Cart - 09", "system_id": robot_system_id, "serial_number": "MCC00009"},
                {"name": "Manual Canister Cart - 10", "system_id": robot_system_id, "serial_number": "MCC00010"},
            ]
        }

        try:
            add_devices(company_id=company_id, device_dict=device_dict, device_type_list=device_type_list,
                        zone_id=zone_id)

        except Exception as e:
            logger.error(e)
            raise


if __name__ == "__main__":
    migrate_add_all_devices(zone_id = 1,
                            company_id = 5,
                            system_id = 13,
                            mfd_system_id_1=16,
                            mfd_system_id_2=17,
                            mfd_system_id_3=18,
                            mfd_system_id_4=19
                            )