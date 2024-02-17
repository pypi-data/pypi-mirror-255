from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from src.model.model_group_master import GroupMaster
from src.model.model_action_master import ActionMaster
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=50, unique=True)
    device_code = CharField(max_length=10, null=True)
    container_code = CharField(max_length=10, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=50)
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


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


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
    drawer_type = ForeignKeyField(CodeMaster, related_name="drawer_type", null=True)
    drawer_usage = ForeignKeyField(CodeMaster, related_name="drawer_usage", null=True)
    shelf = IntegerField(null=True)
    serial_number = CharField(max_length=20, null=True)
    lock_status = BooleanField(default=False)  # True-open and False-close

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class PackHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_header"


class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status_asrs")
    filled_by = FixedCharField(max_length=64)
    consumption_start_date = DateField()
    consumption_end_date = DateField()
    filled_days = SmallIntegerField()
    fill_start_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    association_status = BooleanField(null=True)
    rfid = FixedCharField(null=True, max_length=20, unique=True)
    pack_plate_location = FixedCharField(max_length=2, null=True)
    order_no = IntegerField(null=True)
    filled_date = DateTimeField(null=True)
    filled_at = SmallIntegerField(null=True)
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)
    facility_dis_id = ForeignKeyField(FacilityDistributionMaster, null=True)
    car_id = IntegerField(null=True)
    unloading_time = DateTimeField(null=True)
    pack_sequence = IntegerField(null=True)
    dosage_type = ForeignKeyField(CodeMaster, default=settings.DOSAGE_TYPE_MULTI)
    filling_status = ForeignKeyField(CodeMaster, null=True, related_name="packdetails_filling_status_asrs")
    container_id = ForeignKeyField(ContainerMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


def migrate_add_column_in_pack_details():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    if PackDetails.table_exists():
        migrate(
            migrator.add_column(
                PackDetails._meta.db_table,
                PackDetails.container_id.db_column,
                PackDetails.container_id
            ))
    print("Table Modified: PACK DETAILS")


def insert_device_types_device_container():
    init_db(db, "database_migration")
    try:
        device_type = dict()
        device_type["device_type_name"] = "ASRS Storage"
        device_type["device_code"] = "ASS"
        device_type, created = DeviceTypeMaster.get_or_create(**device_type)

        CURRENT_DATE = get_current_date_time()
        company_id = 4
        Asrs_System_Id = 11
        device_type_id_Asr = 4
        device_type_id_Ass = device_type.id

        # ADD ASRS device
        DeviceMaster.insert_many([
            {'company_id': company_id, 'version': 2.0, 'created_by': 2, 'modified_by': 2,
             'active': 1, 'device_type_id': device_type_id_Asr,
             'created_date': CURRENT_DATE, 'name': 'ASRS - 01', 'system_id': Asrs_System_Id,
             'serial_number': 'ASR00001',
             'modified_date': CURRENT_DATE},
            {'company_id': company_id, 'version': 2.0, 'created_by': 2, 'modified_by': 2,
             'active': 1, 'device_type_id': device_type_id_Asr,
             'created_date': CURRENT_DATE, 'name': 'ASRS - 02', 'system_id': Asrs_System_Id,
             'serial_number': 'ASR00002',
             'modified_date': CURRENT_DATE}]).execute()

        # Add asrs storage device
        asrs_storage_device = {'company_id': company_id, 'version': 2.0, 'created_by': 2, 'modified_by': 2,
                               'active': 1, 'device_type_id': device_type_id_Ass, 'created_date': CURRENT_DATE,
                               'name': 'ASRS Storage - 01',
                               'serial_number': 'ASS00001', 'modified_date': CURRENT_DATE}

        asrs_storage_device_id = DeviceMaster.create(**asrs_storage_device).id
        insert_data_container_master(device_id=asrs_storage_device_id)

    except Exception as e:
        print("Exception came in inserting device types data")
        raise e


def insert_data_container_master(device_id):
    init_db(db, "database_migration")
    try:
        ContainerMaster.insert_many([
            {'device_id': device_id, 'drawer_name': 'Pack Storage 1', "serial_number": "ASD00001"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 2', "serial_number": "ASD00002"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 3', "serial_number": "ASD00003"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 4', "serial_number": "ASD00004"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 5', "serial_number": "ASD00005"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 6', "serial_number": "ASD00006"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 7', "serial_number": "ASD00007"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 8', "serial_number": "ASD00008"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 9', "serial_number": "ASD00009"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 10', "serial_number": "ASD00010"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 11', "serial_number": "ASD00011"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 12', "serial_number": "ASD00012"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 13', "serial_number": "ASD00013"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 14', "serial_number": "ASD00014"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 15', "serial_number": "ASD00015"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 16', "serial_number": "ASD00016"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 17', "serial_number": "ASD00017"},
            {'device_id': device_id, 'drawer_name': 'Pack Storage 18', "serial_number": "ASD00018"}]).execute()

    except Exception as e:
        print("Exception while in inserting container data")
        raise e


def asrs_action_master_addition():
    """
   To create new action for ASRS
    @return: Success Message
    """
    init_db(db, "database_migration")
    try:
        if GroupMaster.table_exists():
            asrs_group = GroupMaster.create(name="ASRS")
            print("Data inserted in GroupMaster Table")

            if ActionMaster.table_exists():
                ActionMaster.create(group_id=asrs_group.id, key=22, value="Pack Removed from ASRS")
                print("Data inserted in the Action Master table.")
    except Exception as e:
        print("Exception adding action in action master")
        raise e


def migration_add_asrs():

    insert_device_types_device_container()
    asrs_action_master_addition()
