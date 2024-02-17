
from playhouse.migrate import *
from collections import defaultdict
from string import ascii_uppercase
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.service.zone import prepare_data_for_csr_locations, prepare_data_for_robot_locations, \
    prepare_data_for_robot_mfd_locations
from src.model.model_container_master import ContainerMaster


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=20, unique=True)

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


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    # group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class DrawerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_number = CharField(max_length=20)
    drawer_id = SmallIntegerField(null=True)
    ip_address = CharField(max_length=20, null=True)
    mac_address = CharField(max_length=50, null=True)
    drawer_status = BooleanField(default=True)
    security_code = CharField(default='0000', max_length=8)
    drawer_type = CharField(default="ROBOT")
    drawer_level = IntegerField(null=True)
    max_canisters = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_size = ForeignKeyField(CodeMaster, default=77, related_name="drawer_size")
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster, related_name="container_id_id")
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )

DEVICE_TYPES = [
{'id': 11, 'device_type_name': "Manual Fill Station"},
]

number_of_mfs = 4

# for i in range()


def migrate_mfs():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    all_drawer_data = list()
    device_count = 4
    system_id = [23, 24, 25, 26]
    company_id = 25
    serial_number = list()
    device_name = list()
    device_type = settings.DEVICE_TYPES['Manual Filling Device']
    DEVICE_MASTER_DATA = list()
    device_prefix = 'MFS'
    max_canisters = 16
    big_drawer = 0
    small_drawer = 2
    CURRENT_DATE = get_current_date_time()

    with db.transaction():
        drawer_per_row = 1
        location_per_drawer = 8
        total_drawers = 2
        device_type_id = DeviceTypeMaster.insert_many(DEVICE_TYPES).execute()
        device_query = DeviceMaster.select().dicts().order_by(DeviceMaster.id.desc()).get()
        last_device_id = device_query['id']
        device_ids = list()
        for i in range(1, device_count+1):
            device_ids.append(last_device_id+i)
            device_name.append('{}-{}'.format(device_prefix, i))
            serial_number.append('{}-{}'.format(device_prefix, i))

        for i in range(0, device_count):
            print(DEVICE_MASTER_DATA)
            DEVICE_MASTER_DATA.append(
                {'id': device_ids[i], 'company_id': company_id, 'name': device_name[i], 'serial_number': serial_number[i],
                 'device_type_id': device_type,
                 'system_id': system_id[i], 'version': '2.0',
                 'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                 'modified_date': CURRENT_DATE})

        DeviceMaster.insert_many(DEVICE_MASTER_DATA).execute()
        for device_id in device_ids:
            try:
                max_location_number = LocationMaster.select(fn.MAX(LocationMaster.location_number).alias('max_loc_id')
                                                            ).dicts() \
                    .where(LocationMaster.device_id == device_id).get()
                max_location_number = max_location_number['max_loc_id']
                if max_location_number is None:
                    max_location_number = 0
                print(max_location_number)
            except DoesNotExist as e:
                max_location_number = 0
            for i in range(0, total_drawers):
                drawer_initial = str(ascii_uppercase[i])


                for i in range(1, drawer_per_row + 1):
                    drawer_data = {'device_id': device_id,
                                   'drawer_name': '{}-{}'.format(drawer_initial, i),
                                   'drawer_type': settings.SIZE_OR_TYPE["MFD"]}
                    print(drawer_data)
                    drawer_record = BaseModel.db_create_record(drawer_data, ContainerMaster, get_or_create=False)

                    location_drawer_initial = '{}{}'.format(drawer_initial, i)
                    drawer_data = prepare_data_for_robot_mfd_locations(location_per_drawer,
                                                                            device_id,
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


if __name__ == "__main__":
    migrate_mfs()


