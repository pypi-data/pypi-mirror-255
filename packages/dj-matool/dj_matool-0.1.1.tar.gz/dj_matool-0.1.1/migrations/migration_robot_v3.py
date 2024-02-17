from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.service.zone import prepare_data_for_csr_locations, prepare_data_for_robot_locations


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField( max_length=20, unique=True)

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
    max_canisters = IntegerField(null=True)
    big_drawers = IntegerField(null=True)
    small_drawers = IntegerField(null=True)
    controller = CharField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_number = CharField()
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


CURRENT_DATE = get_current_date_time()

def insert_device_master_data(DEVICE_MASTER_DATA):
    try:
        DeviceMaster.insert_many(DEVICE_MASTER_DATA).execute()
    except Exception as e:
        print('Exception came in inserting device_master data: ', e)
        raise e


def insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:
        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            data_list = []
            if device_type == settings.DEVICE_TYPES['CSR']:
                locations_data = prepare_data_for_csr_locations(total_drawers=device['total_drawers'],
                                                                locations_per_drawer=device.get('locations_per_drawer',
                                                                                                12),
                                                                device_id=device['device_id'],
                                                                drawer_initials='decimal',
                                                                csr_name=device['shelf_name'])
            else:
                locations_data = prepare_data_for_robot_locations(total_drawers=device['total_drawers'],
                                                                  locations_per_drawer=device.get(
                                                                      'locations_per_drawer', 12),
                                                                  device_id=device['device_id'],
                                                                  drawer_per_row=10)

            data_list.extend(locations_data)
            print('**********************************************************************')
            print(data_list)
            LocationMaster.insert_many(data_list).execute()
    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def migrate_robot_v3():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    device_query = DeviceMaster.select().dicts().order_by(DeviceMaster.id.desc()).get()
    last_device_id = device_query['id']

    last_device_id +=1
    robot_id1 = last_device_id
    robot_id2 = last_device_id +1
    DEVICE_MASTER_DATA = [
        {'id': robot_id1, 'company_id': 3, 'name': 'Robot-1-v3', 'serial_number': 'RBTV301',
         'device_type_id': settings.DEVICE_TYPES["ROBOT"],
         'system_id': None, 'version': '2', 'max_canisters': 480, 'big_drawers': 80, 'small_drawers': 400,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id2, 'company_id': 3, 'name': 'Robot-2-v3', 'serial_number': 'RBTV302',
         'device_type_id': settings.DEVICE_TYPES["ROBOT"],
         'system_id': None, 'version': '2', 'max_canisters': 480, 'big_drawers': 80, 'small_drawers': 400,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE}

    ]

    DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST_ROBOT = [
        {"device_id": robot_id1, "total_drawers": 60, "locations_per_drawer": 8},
        {"device_id": robot_id2, "total_drawers": 60, "locations_per_drawer": 8},

    ]

    insert_device_master_data(DEVICE_MASTER_DATA)
    insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST_ROBOT, settings.DEVICE_TYPES['ROBOT'])


if __name__ == "__main__":
    migrate_robot_v3()
