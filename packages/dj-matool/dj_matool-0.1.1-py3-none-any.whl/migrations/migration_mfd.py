import src.constants
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


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


class ZoneMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=25)
    floor = IntegerField(null=True)
    length = DecimalField(decimal_places=2,null=True)
    height = DecimalField(decimal_places=2,null=True)
    width = DecimalField(decimal_places=2,null=True)
    company_id = IntegerField()  # Foreign key field of company table of dp auth
    x_coordinate = DecimalField(decimal_places=2,null=True)
    y_coordinate = DecimalField(decimal_places=2,null=True)
    # dimensions_unit_id = ForeignKeyField(UnitMaster,null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "zone_master"
        indexes = (
            (('company_id', 'name'), True),
        )


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    split_function_id = IntegerField(null=True)
    scheduled_start_time = DateTimeField(default=get_current_date_time(), null=True)
    estimated_processing_time = FloatField(null=True)
    imported_date = DateTimeField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class ConfigurationMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    device_type_id = ForeignKeyField(DeviceTypeMaster)
    device_version = CharField(null=True)
    configuration_name = CharField(max_length=50)
    configuration_value = TextField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "configuration_master"


class SlotDetails(BaseModel):
    id = PrimaryKeyField()
    # slot_id = ForeignKeyField(SlotHeader)
    # pack_rx_id = ForeignKeyField(PackRxLink)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    is_manual = BooleanField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_details"


class MfdCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
    canister_type = CharField(max_length=36)
    active = BooleanField()
    label_print_time = DateTimeField(null=True, default=None)
    erp_product_id = IntegerField(null=True, unique=True)
    company_id = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    home_cart_id = ForeignKeyField(DeviceMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_master"


class MfdCanisterTransferHistory(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    current_location_id = ForeignKeyField(LocationMaster, null=True, related_name='mfd_current_location_id')
    previous_location_id = ForeignKeyField(LocationMaster, null=True, related_name='mfd_previous_location_id')
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_transfer_history"


class MfdCanisterStatusHistory(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_status_history"


class MfdCanisterZoneMapping(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    zone_id = ForeignKeyField(ZoneMaster)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_zone_mapping"

        indexes = (
            (('mfd_canister_id', 'zone_id'), True),
        )


class MfdAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, related_name='batch_id')
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster, null=True, related_name='mfd_can_id')
    order_no = IntegerField()
    assigned_to = IntegerField(null=True)
    status_id = ForeignKeyField(CodeMaster, related_name='can_status')
    dest_device_id = ForeignKeyField(DeviceMaster, related_name='robot_id')
    mfs_device_id = ForeignKeyField(DeviceMaster, null=True, related_name='manual_fill_station')
    mfs_location_number = IntegerField(null=True)
    dest_quadrant = IntegerField()
    trolley_location_id = ForeignKeyField(LocationMaster, related_name='trolley_loc_id', null=True)
    dropped_location_id = ForeignKeyField(LocationMaster, null=True, related_name='dropped_loc_id')
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis"


class MfdAnalysisDetails(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(MfdAnalysis)
    mfd_can_slot_no = IntegerField()
    drop_number = IntegerField()
    config_id = ForeignKeyField(ConfigurationMaster)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    status_id = ForeignKeyField(CodeMaster)
    slot_id = ForeignKeyField(SlotDetails)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis_details"


class MfdCanisterAnalysisMapping(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster, unique=True)
    analysis_id = ForeignKeyField(MfdAnalysis, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_analysis_mapping"


def migrate_mfd():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    db.create_tables([MfdCanisterMaster, MfdCanisterStatusHistory, MfdCanisterTransferHistory, MfdCanisterZoneMapping,
                      MfdAnalysis, MfdAnalysisDetails, MfdCanisterAnalysisMapping], safe=True)

    GROUP_MASTER_DATA = [
            dict(id=src.constants.GROUP_MASTER_MFD_CANISTER, name='Mfd Canister'),
            dict(id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG, name='Mfd Drug')
    ]

    CODE_MASTER_DATA = [
            dict(id=src.constants.MFD_CANISTER_PENDING_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_PENDING_STATUS, value="Pending"),
            dict(id=src.constants.MFD_CANISTER_IN_PROGRESS_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_IN_PROGRESS_STATUS, value="In Progress"),
            dict(id=src.constants.MFD_CANISTER_FILLED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_FILLED_STATUS, value="Filled"),
            dict(id=src.constants.MFD_CANISTER_DROPPED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_DROPPED_STATUS, value="Dropped"),
            dict(id=src.constants.MFD_DRUG_FILLED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                 key=src.constants.MFD_DRUG_FILLED_STATUS, value="Filled"),
            dict(id=src.constants.MFD_DRUG_SKIPPED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                 key=src.constants.MFD_DRUG_SKIPPED_STATUS, value="Skipped"),
            dict(id=src.constants.MFD_DRUG_PENDING_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                 key=src.constants.MFD_DRUG_PENDING_STATUS, value="Pending"),
            dict(id=src.constants.MFD_CANISTER_SKIPPED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_SKIPPED_STATUS, value="Skipped"),
            dict(id=src.constants.MFD_DRUG_DROPPED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                 key=src.constants.MFD_DRUG_DROPPED_STATUS, value="Dropped"),
            dict(id=src.constants.MFD_DRUG_RTS_REQUIRED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                 key=src.constants.MFD_DRUG_RTS_REQUIRED_STATUS, value="RTS Required"),
            dict(id=src.constants.MFD_DRUG_RTS_DONE, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                 key=src.constants.MFD_DRUG_RTS_DONE, value="RTS Done"),
            dict(id=src.constants.MFD_CANISTER_VERIFIED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_VERIFIED_STATUS, value="Verified"),
            dict(id=src.constants.MFD_CANISTER_RTS_REQUIRED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
             key=src.constants.MFD_CANISTER_RTS_REQUIRED_STATUS, value="RTS Required"),
            dict(id=src.constants.MFD_CANISTER_RTS_DONE_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 key=src.constants.MFD_CANISTER_RTS_DONE_STATUS, value="RTS Done")
        ]

    print("Table(s) Created: MfdCanisterMaster, MfdCanisterHistory, MfdCanisterZoneMapping, "
          "MfdAnalysis, MfdAnalysisDetails")


    GroupMaster.insert_many(GROUP_MASTER_DATA).execute()

    CodeMaster.insert_many(CODE_MASTER_DATA).execute()

    print("Table modified: GroupMaster, CodeMaster")


if __name__ == "__main__":
    migrate_mfd()
