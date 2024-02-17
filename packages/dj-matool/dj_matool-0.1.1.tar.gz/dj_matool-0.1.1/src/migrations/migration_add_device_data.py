import logging

from src import constants
from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.service.zone import prepare_data_for_device_locations_trolley, prepare_data_for_device_locations, \
    prepare_data_for_robot_locations, prepare_data_for_robot_mfd_locations

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


class ContainerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_name = CharField(max_length=20)
    ip_address = CharField(max_length=20, null=True)
    secondary_ip_address = CharField(max_length=20, null=True)
    mac_address = CharField(max_length=50, null=True)
    secondary_mac_address = CharField(max_length=50, null=True)
    drawer_level = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_type = ForeignKeyField(CodeMaster, default=77, related_name="drawer_type")
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")
    shelf = IntegerField(null=True)
    serial_number = CharField(max_length=20, null=True)
    lock_status = BooleanField(default=False)  # True-open and False-close

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


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


def add_zone(zone_dict: dict) -> int:
    """
    To add zone in zone_master
    @param zone_dict: dict - {name:value, floor:None, length:None, height:None, width:None,
                                    company_id:None, x_coordinate:None, y_coordinate:None, dimensions_unit_id:None}
    @return: zone_id
    """
    try:
        logger.debug("Adding zone data")
        zone_data = ZoneMaster.get_or_create(**zone_dict)
        zone_id = zone_data.id
        logger.debug("Added zone data with id: " + str(zone_id))
        return zone_id
    except Exception as e:
        logger.error("Exception while adding zone data: " + str(e))


def add_containers_locations_for_csr(last_device_id):
    rows = 'ABCDEFGHIJ'
    container_dict = {}
    container_list = []
    location_list = []
    location_dict = {}
    location_number = 0
    serial_number = 'CRD00'
    # device_query = DeviceMaster.select().dicts().order_by(DeviceMaster.id.desc()).get()
    # last_device_id = device_query['id']
    location_query = ContainerMaster.select().dicts().order_by(ContainerMaster.id.desc()).get()
    last_container_id = location_query['id']
    for r in rows:
        if r == 'A' or r == 'B':
            for c in range(1, 27):
                if 9 <= c <= 18:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_BIG
                    container_dict['drawer_usage'] = constants.USAGE_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
                else:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_BIG
                    container_dict['drawer_usage'] = constants.USAGE_MEDIUM_FAST_MOVING
                    container_list.append(container_dict.copy())

                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())

        if r == 'C' or r == 'D' or r == 'E':
            for c in range(1, 27):
                if 9 <= c <= 18:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
                else:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_MEDIUM_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())

        if r == 'F':
            for c in range(1, 27):
                if 9 <= c <= 18:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
                else:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_MEDIUM_SLOW_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
        if r == 'G':
            for c in range(1, 27):
                container_dict['drawer_name'] = r + '-' + str(c)
                container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                container_dict['drawer_usage'] = constants.USAGE_MEDIUM_SLOW_MOVING
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_list.append(location_dict.copy())
        if r == 'H' or r == 'I' or r == 'J':
            for c in range(1, 27):
                if r == 'I':
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_BIG
                else:
                    container_dict['drawer_type']=constants.SIZE_OR_TYPE_SMALL
                container_dict['drawer_name'] = r + '-' + str(c)
                container_dict['drawer_usage'] = constants.USAGE_SLOW_MOVING
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_list.append(location_dict.copy())

    # To add corresponding serial_numbers to drawers
    li_serial = []
    li_url = []
    for i in range(1, 261):
        # li_url.append('dose_'+str(81)+'_'+str(i*2-1)+','+str(i*2)+'.'+'127.0.0.1')
        if len(str(i)) == 1:
            li_serial.append(serial_number + '00' + str(i))
        if len(str(i)) == 2:
            li_serial.append(serial_number + '0' + str(i))
        if len(str(i)) == 3:
            li_serial.append(serial_number + str(i))
    # To add corresponding shelf to drawers
    li_shelf = []
    for each_data in range(10):
        for i in range(1, 27):
            li_shelf.append(i)
    li_level = []
    for i in range(1, 11):
        for j in range(26):
            li_level.append(i)

    for each_data in container_list:
        # each_data['url'] = li_url.pop(0)
        each_data['serial_number'] = li_serial.pop(0)
        each_data['shelf'] = li_shelf.pop(0)
        each_data['drawer_level'] = li_level.pop(0)
        each_data['device_id'] = last_device_id
        each_data['created_by'] = 1
        each_data['modified_by'] = 1
        each_data['created_date'] = get_current_date_time()
        each_data['modified_date'] = get_current_date_time()

    # To add corresponding container_ids to locations
    container_id = last_container_id
    li_containers = []
    for i in range(260):
        container_id = container_id + 1
        for j in range(20):
            li_containers.append(container_id)
    for each_data in location_list:
        each_data['container_id'] = li_containers.pop(0)
        each_data['device_id'] = last_device_id
    try:
        with db.transaction():
            logger.info(container_list, location_list)
            ContainerMaster.insert_many(container_list).execute()
            LocationMaster.insert_many(location_list).execute()
            print("Data Added in ContainerMaster and LocationMaster")
    except (IntegrityError, InternalError) as e:
        logger.error(e)
        raise e


def add_mfd_drawers(device_ids):
    try:
        all_drawer_data = list()
        drawer_per_row = 10
        location_per_drawer = 8
        mfd_initial = 'M'
        # device_query = DeviceMaster.select().dicts() \
        #     .where(DeviceMaster.version == settings.ROBOT_SYSTEM_VERSIONS['v3'],
        #            DeviceMaster.id == 15,
        #            DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']) \
        #     .order_by(DeviceMaster.id.desc())

        for device in device_ids:
            print(device)
            try:
                max_location_number = LocationMaster.select(fn.MAX(LocationMaster.location_number).alias('max_loc_id')
                                                            ).dicts() \
                    .where(LocationMaster.device_id == device).get()
                max_location_number = max_location_number['max_loc_id']
                print(max_location_number)
            except DoesNotExist as e:
                max_location_number = 0
            for i in range(1, drawer_per_row + 1):
                drawer_data = {'device_id': device,
                               'drawer_name': '{}-{}'.format(mfd_initial, i),
                               'drawer_type': settings.SIZE_OR_TYPE['MFD']}
                print(drawer_data)
                drawer_record = BaseModel.db_create_record(drawer_data, ContainerMaster, get_or_create=False)

                location_drawer_initial = '{}{}'.format(mfd_initial, i)
                mfd_derawer_data = prepare_data_for_robot_mfd_locations(location_per_drawer,
                                                                        device,
                                                                        drawer_record.id,
                                                                        max_location_number,
                                                                        original_drawer_number=i,
                                                                        drawer_initial_name=location_drawer_initial,
                                                                        drawer_per_row=10,
                                                                        quadrant_avialable=True)
                all_drawer_data.extend(mfd_derawer_data)
                max_location_number = max_location_number + location_per_drawer
            print(all_drawer_data)
            if all_drawer_data:
                LocationMaster.insert_many(all_drawer_data).execute()

    except Exception as e:
        logger.error(e)


def insert_robot_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:
        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            data_list = []
            container_list = []
            device_id = device['device_id']
            if device_type == settings.DEVICE_TYPES['Robot']:
                locations_data, drawer_data = prepare_data_for_robot_locations(total_drawers=50,
                                                                  locations_per_drawer=device.get(
                                                                      'locations_per_drawer', 12),
                                                                  device_id=device['device_id'],
                                                                  drawer_per_row=10,
                                                                   drawer_type="SMALL")

                data_list.extend(locations_data)
                container_list.extend(drawer_data)

                locations_data,drawer_data = prepare_data_for_robot_locations(total_drawers=20,
                                                                  locations_per_drawer=device.get(
                                                                      'locations_per_drawer', 12),
                                                                  device_id=device['device_id'],
                                                                  drawer_per_row=10,
                                                                  drawer_type="BIG")

                data_list.extend(locations_data)
                container_list.extend(drawer_data)

            print('**********************************************************************')
            print(data_list)
            print(container_list)
            ContainerMaster.insert_many(container_list).execute()
            LocationMaster.insert_many(data_list).execute()

            add_mfd_drawers([device_id])

    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def insert_mfd_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:

        drawer_ids_list = [(1, [1, 2]), (2, [3, 4]), (3, [5, 6]), (4, [7, 8]), (5, [9, 10]),
                           (6, [11, 12]), (7, [13, 14]), (8, [15, 16])]

        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            index = DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST.index(device)
            data_list = []
            drawer_list = []
            drawer_id = ContainerMaster.get_max_drawer_id()
            if device_type == settings.DEVICE_TYPES['MFD_TROLLEY']:
                loc_num = 0
                for each_drawer_data in drawer_ids_list:
                    drawer_level, ed = each_drawer_data
                    locations_data, drawer_data, drawer_id_updated, loc_num_updated = prepare_data_for_device_locations(
                        total_drawers=1,
                        locations_per_drawer=20,
                        device_id=device['device_id'],
                        drawer_per_row=2, quadrant_avialable=False,
                        drawer_id_list=ed,
                        drawer_id=drawer_id,
                        loc_num=loc_num,
                        drawer_level = drawer_level)

                    loc_num = loc_num_updated
                    drawer_id = drawer_id_updated
                    drawer_list.extend(drawer_data)
                    data_list.extend(locations_data)
            else:
                locations_data, drawer_data = prepare_data_for_device_locations(total_drawers=device['total_drawers'],
                                                                                locations_per_drawer=device.get(
                                                                                    'locations_per_drawer', 20),
                                                                                device_id=device['device_id'],
                                                                                drawer_per_row=8,
                                                                                quadrant_avialable=False)

            # data_list.extend(locations_data)
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
                    total_drawers=device['total_drawers'],
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


def add_devices(company_id: int, device_dict: dict, device_type_list: list = None, zone_id:int = None):
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
            device_type_name_id_dict[device_type_record.name] = device_type_record.id

        # Add device data in device_master
        for device_type, device_list in device_dict:
            logger.info("Data addition initiated")
            CURRENT_DATE = get_current_date_time()
            if device_type == "CSR":
                logger.info("Adding CSR")
                for device in device_list:
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                     'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["CSR"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)
                    logger.info(device_layout_id)

                    # to add locations and containers for CSR
                    add_containers_locations_for_csr(new_device_id.id)
                    logger.info("CSR added")

            if device_type == "Robot":
                logger.info("Adding robot")
                device_ids = list()
                for device in device_list:
                    data_dict = {
                        'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                        'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Robot"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)

                    device_ids.append(new_device_id.id)

                DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST_ROBOT = [
                    {"device_id": device_ids[0], "total_drawers": 60, "locations_per_drawer": 8},
                    {"device_id": device_ids[1], "total_drawers": 60, "locations_per_drawer": 8}]

                insert_robot_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST_ROBOT, 2)
                logger.info("Robot added")

            if device_type == "Manual Canister Cart":
                logger.info("adding manual canister cart")
                mfd_trolley_devices = list()
                for device in device_list:
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                     'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Manual Canister Cart"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id":new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)
                    logger.info(device_layout_id)

                    location_data = {"device_id": new_device_id.id, "total_drawers": 16, "locations_per_drawer": 20}
                    mfd_trolley_devices.append(location_data)

                    insert_mfd_location_data(mfd_trolley_devices, "Manual Canister Cart")
                    print("data inserted in location master regular trolley")
                    logger.info("manual canister cart added")

            if device_type == "Refilling Device":
                logger.info("adding refilling device")
                container_data_list = list()
                for i, device in enumerate(device_list):
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Refilling Device"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)



                    # to add containers for Refill device data
                    container_dict = {"device_id": new_device_id, "drawer_name": "A-1",
                                      "created_date": CURRENT_DATE, "modified_date": CURRENT_DATE,
                                      "serial_number": "RDD0000"+str(i)}
                container_data_list.append(container_dict)
                container_data = ContainerMaster.insert_many(container_data_list)
                logger.info("Added refill device data")

            if device_type == "Drug Dispenser Trolley":
                logger.info("Adding drug dispenser trolley")
                container_data_list = list()
                for i, device in enumerate(device_list):
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Drug Dispenser Trolley"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)

                    # to add containers for Drug Dispenser Trolley
                    container_dict = {"device_id": new_device_id, "drawer_name": "A-1",
                                      "created_date": get_current_date_time, "modified_date": get_current_date_time,
                                      "serial_number": "DTD0000"+str(i)}
                container_data_list.append(container_dict)
                container_data = ContainerMaster.insert_many(container_data_list)
                logger.info("Added Drug Dispenser Trolley")

            if device_type == "Dimension Measuring Equipment":
                logger.info("Dimension measuring equipment")
                container_data_list = list()
                for i, device in enumerate(device_list):
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Dimension Measuring Equipment"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)

                    # to add containers for Drug Dispenser Trolley
                    container_dict = {"device_id": new_device_id, "drawer_name": "A-1",
                                      "created_date": get_current_date_time, "modified_date": get_current_date_time,
                                      "serial_number": "DMD0000"+str(i)}
                container_data_list.append(container_dict)
                container_data = ContainerMaster.insert_many(container_data_list)
                logger.info("Added Dimension Measuring Equipment")

            if device_type == "Canister Transfer Cart":
                logger.info("canister transfer cart")
                device_ids = list()
                for device in device_list:
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Canister Transfer Cart"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}
                    device_ids.append(new_device_id.id)
                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)

                # to add containers and locations for Canister Transfer Cart
                DEVICE_ID_TO_MAX_LOCATION_MAPPING_REGULAR_TROLLEY = [
                    {"device_id": device_ids.pop(), "total_drawers": 16, "locations_per_drawer": 20},
                    {"device_id": device_ids.pop(), "total_drawers": 16, "locations_per_drawer": 20},
                    {"device_id": device_ids.pop(), "total_drawers": 16, "locations_per_drawer": 20}
                ]
                logger.debug("Adding location and container data for canister transfer cart")
                insert_trolley_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_REGULAR_TROLLEY,
                                           "Canister Transfer Cart")
                logger.info("data inserted in location master for regular trolley")

            if device_type == "Canister Cart w/ Elevator":
                logger.info("adding canister cart with elevator")
                device_ids = list()
                for device in device_list:
                    data_dict = {'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                                 'modified_date': CURRENT_DATE}
                    device["company_id"] = company_id
                    device["device_type_id"] = device_type_name_id_dict["Canister Cart w/ Elevator"]
                    device["version"] = 2.0
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}
                    device_ids.append(new_device_id.id)
                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)

                    # to add containers and locations for Canister Transfer Cart
                DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIFT_TROLLEY = [
                    {"device_id": device_ids.pop(), "total_drawers": 8, "locations_per_drawer": 20},
                ]
                logger.debug("Adding location and container data for canister transfer cart")
                insert_trolley_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIFT_TROLLEY,
                                           device_type_name_id_dict["Canister Cart w/ Elevator"])
                logger.info("data inserted in location master for lift trolley")

            if device_type == "MFD":
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
                    device.extend(data_dict)

                    #  add data in device master
                    new_device_id = DeviceMaster.get_or_create(**device)
                    device_layout_dict = {"device_id": new_device_id.id, "zone_id": zone_id}

                    # to add data in device layout details
                    device_layout_id = DeviceLayoutDetails.get_or_create(**device_layout_dict)

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
                            drawer_record = BaseModel.db_create_record(drawer_data, ContainerMaster, get_or_create=False)

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


def migrate_add_all_devices():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    company_id = 60
    refill_system_id = 61
    robot_system_id = 62
    mfd_system_id_1 = 63
    mfd_system_id_2 = 64
    mfd_system_id_3 = 65
    mfd_system_id_4 = 66

    with db.transaction():
        # add zone if not available
        zone_dict = {"name": "Zone-A", "floor": 1, "length": 1500.00, "height": 1309.00,
                     "width": 1500.00, "company_id": company_id, "x_coordinate": 12.30,
                     "y_coordinate": 12.30, "dimensions_unit_id": 5}
        zone_id = add_zone(zone_dict)

        # add and map device data
        device_type_list = [
            {"device_type_name": "CSR", "device_code": "CSR", "container_code": "CRD"},
            {"device_type_name": "Robot", "device_code": "DDR", "container_code": "DDD"},
            {"device_type_name": "Manual Filling Device", "device_code": "MFD", "container_code": "MDD"},
            {"device_type_name": "ASRS", "device_code": "ASR", "container_code": "ASD"},
            {"device_type_name": "Refilling Device", "device_code": "RFD", "container_code": "RDD"},
            {"device_type_name": "Drug Dispenser Trolley", "device_code": "DDT", "container_code": "DTD"},
            {"device_type_name": "Dimension Measuring Equipment", "device_code": "DME", "container_code": "DMD"},
            {"device_type_name": "Manual Canister Cart", "device_code": "MCC", "container_code": "MCD"},
            {"device_type_name": "Canister Transfer Cart", "device_code": "CTC", "container_code": "CCD"},
            {"device_type_name": "Canister Cart w/ Elevator", "device_code": "CCE", "container_code": "CED"},
        ]
        device_dict = {
            "CSR": [
                {"name": "CSR - 01", "system_id": refill_system_id, "serial_number": "CSR00001"}
            ],
            "Robot": [
                {"name": "Robot - 01", "system_id": robot_system_id, "serial_number": "DDR00001"},
                {"name": "Robot - 02", "system_id": robot_system_id, "serial_number": "DDR00002"},
            ],
            "Manual Filling Device": [
                {"name": "Manual Filling Device - 01", "system_id": mfd_system_id_1, "serial_number": "MFD00001"},
                {"name": "Manual Filling Device - 02", "system_id": mfd_system_id_2, "serial_number": "MFD00002"},
                {"name": "Manual Filling Device - 03", "system_id": mfd_system_id_3, "serial_number": "MFD00003"},
                {"name": "Manual Filling Device - 04", "system_id": mfd_system_id_4, "serial_number": "MFD00004"},
            ],
            "Refilling Device": [
                {"name": "Refill Device - 01", "system_id": refill_system_id, "serial_number": "RFD00001"},
            ],
            "Dimension Measuring Equipment": [
                {"name": "Dimension Measuring Equipment - 01", "system_id": refill_system_id, "serial_number": "DME00001"}
            ],
            "Drug Dispenser Trolley": [
                {"name": "Drug Dispenser Trolley - 01", "system_id": robot_system_id, "serial_number": "DDT00001"},
                {"name": "Drug Dispenser Trolley - 02", "system_id": robot_system_id, "serial_number": "DDT00002"},
                {"name": "Drug Dispenser Trolley - 03", "system_id": robot_system_id, "serial_number": "DDT00003"},
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
            ],
            "Canister Transfer Cart": [
                {"name": "Canister Transfer Cart - 01", "system_id": robot_system_id, "serial_number": "CTC00001"},
                {"name": "Canister Transfer Cart - 02", "system_id": robot_system_id, "serial_number": "CTC00002"},
                {"name": "Canister Transfer Cart - 03", "system_id": robot_system_id, "serial_number": "CTC00003"},
            ],
            "Canister Cart w/ Elevator": [
                {"name": "Canister Cart w/ Elevator - 01", "system_id": robot_system_id, "serial_number": "CCE00001"},
            ]
        }

        try:
            add_devices(company_id=company_id, device_dict=device_dict, device_type_list=device_type_list, zone_id = zone_id)

        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    migrate_add_all_devices()