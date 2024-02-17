from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    company_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField()  # number of canisters that robot can hold
    big_drawers = IntegerField(default=4)  # number of big drawers that robot holds
    small_drawers = IntegerField(default=12)  # number of small drawers that robot holds
    # controller used 'AR' for ardiuno and 'BB' for beagle bone 'BBB' for beagle bone black
    controller = CharField(max_length=10, default="AR")
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    serial_number = CharField(unique=True)
    # device_type_id = ForeignKeyField(DeviceTypeMaster)
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
    drawer_number = IntegerField()
    display_location = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


class DrugMaster(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50)
    strength_value = CharField(max_length=16)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    canister_number = SmallIntegerField(default=0, null=True)
    canister_type = CharField(max_length=20)
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    label_print_time = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class IntermediateNdcBlacklist(BaseModel):
    id = PrimaryKeyField()
    ndc = CharField(max_length=14)
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()
    note = CharField(max_length=100)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ndc_blacklist"


class IntermediateNdcBlacklistAudit(BaseModel):
    id = PrimaryKeyField()
    ndc_blacklist_id = ForeignKeyField(IntermediateNdcBlacklist)
    ndc = CharField(max_length=14)
    note = CharField(max_length=100)
    deleted_date = DateTimeField(default=get_current_date_time)
    deleted_by = IntegerField()
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ndc_blacklist_audit"


class IntermediateVisionDrugPrediction (BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    # slot_header_id = ForeignKeyField(SlotHeader)
    image_filename = CharField(null=True) # Image name generated with UUID # image generated for a slot
    image_uploaded = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "vision_drug_prediction"



class IntermediatePackAnalysisDetails(BaseModel):
    id = PrimaryKeyField()
    # analysis_id = ForeignKeyField(PackAnalysis)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    canister_id = ForeignKeyField(CanisterMaster, null=True)
    canister_number = SmallIntegerField(null=True)
    drug_id = ForeignKeyField(DrugMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_analysis_details"


class IntermediatePackCanisterUsage(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    # unique_drug_id = ForeignKeyField(UniqueDrug)
    robot_id = ForeignKeyField(RobotMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    canister_number = SmallIntegerField()
    # pack_grid_id = ForeignKeyField(PackGrid)
    location_id = ForeignKeyField(LocationMaster, default=None, null=True)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'unique_drug_id', 'pack_grid_id', 'canister_number'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = 'pack_canister_usage'


class IntermediateCanisterTracker(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    refill_type = SmallIntegerField(null=True)
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    # expiration_date = DateField(null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()
    voice_notification_uuid = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


class IntermediatePVSPack(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    mft_status = BooleanField()
    user_station_status = BooleanField()
    deleted = BooleanField()
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_pack'


class IntermediateSlotTransaction(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    # slot_id = ForeignKeyField(SlotDetails)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster, related_name="SlotTransaction_drug_id")
    canister_id = ForeignKeyField(CanisterMaster, related_name="SlotTransaction_canister_id", null=True)
    canister_number = SmallIntegerField(null=True)
    alternate_drug_id = ForeignKeyField(DrugMaster, null=True, related_name="SlotTransaction_alt_drug_id")
    alternate_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="SlotTransaction_alt_canister_id")
    dropped_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    mft_drug = BooleanField(default=False)
    IPS_update_alt_drug = BooleanField(null=True)
    IPS_update_alt_drug_error = CharField(null=True, max_length=150)
    location_id = ForeignKeyField(LocationMaster, null=True)
    created_by = IntegerField()
    created_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_transaction"


class IntermediatePackProcessingOrder(BaseModel):
    id = PrimaryKeyField()
    # batch_id = ForeignKeyField(BatchMaster)
    # pack_id = ForeignKeyField(PackDetails)
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    pack_order = SmallIntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_processing_order"


class IntermediateReplenishAnalysis(BaseModel):
    id = PrimaryKeyField()
    # batch_id = ForeignKeyField(BatchMaster)
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    quantity = SmallIntegerField()
    # process_order_id = ForeignKeyField(PackProcessingOrder)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "replenish_analysis"



def effiecient_migrate_location_id(migrator, model_class, remove_null=True):
    """
    migration function to replaces robot_id, canister_number combination with location_id
    :param migrator:
    :param model_class:
    :param remove_null:
    :return:
    """
    if model_class.table_exists():
        migrate(
            migrator.add_column(
                model_class._meta.db_table,
                model_class.location_id.db_column,
                model_class.location_id
            )
        )
        print("column added: " + str(model_class))

        query = model_class.select(LocationMaster.id.alias('location_id'),
                                   fn.GROUP_CONCAT(model_class.id).coerce(False).alias('table_id')).dicts() \
            .join(LocationMaster,
                  on=((model_class.robot_id == LocationMaster.device_id) &
                      (model_class.canister_number == LocationMaster.location_number)))\
            .group_by(LocationMaster.id)

        update_dict = dict()
        for record in query:
            update_dict[int(record['location_id'])] = list(map(int, record['table_id'].split(',')))


        for key, value in update_dict.items():
            model_class.update(location_id=key).where(model_class.id << value).execute()

        print("Column values updated " + str(model_class))

        if remove_null:
            try:
                migrate(migrator.add_not_null(model_class._meta.db_table, model_class.location_id.db_column))
            except Exception as e:
                print(e)
                print('Could not add not_null constraint to {}'.format(model_class))

        migrate(
            migrator.drop_column(
                model_class._meta.db_table,
                model_class.robot_id.db_column,
            ),
            migrator.drop_column(
                model_class._meta.db_table,
                model_class.canister_number.db_column,
            )
        )
        print("Column dropped " + str(model_class))


def migrate_device_id(migrator, model_class, remove_null=True):
    """
    migration function to replaces robot_id with device_id
    :param migrator:
    :param model_class:
    :param remove_null:
    :return:
    """
    if model_class.table_exists():
        migrate(
            migrator.add_column(
                model_class._meta.db_table,
                model_class.device_id.db_column,
                model_class.device_id
            )
        )
        print("column added: " + str(model_class))

        query = model_class.select(model_class.robot_id.alias('robot_id'),
                                       model_class.id.alias('table_id')).dicts()

        update_dict = defaultdict(list)
        for record in query:
            if record['robot_id']:
                update_dict[int(record['robot_id'])].append(record['table_id'])

        print("Column values being updated")

        for key, value in update_dict.items():
            model_class.update(device_id=key).where(model_class.id << value).execute()

        print("Column values updated " + str(model_class))


        migrate(
            migrator.drop_column(
                model_class._meta.db_table,
                model_class.robot_id.db_column,
            )
        )
        print("Column dropped " + str(model_class))

        if remove_null:
            try:
                migrate(
                    migrator.drop_foreign_key_constraint(model_class._meta.db_table, model_class.device_id.db_column),
                    migrator.add_not_null(model_class._meta.db_table, model_class.device_id.db_column),
                    migrator.add_foreign_key_constraint(model_class._meta.db_table, model_class.device_id.db_column,
                                                    DeviceMaster._meta.db_table, DeviceMaster.id.db_column)
                )
            except Exception as e:
                print(e)
                print('Could not add not_null constraint to {}'.format(model_class))


def migrate_location_id(migrator, model_class, remove_null=True):
    """
    migration function to replaces robot_id, canister_number combination with location_id
    :param migrator:
    :param model_class:
    :param remove_null:
    :return:
    """
    # This function is used only when group_concat truncates the data else use 'effiecient_migrate_location_id' method
    if model_class.table_exists():
        migrate(
            migrator.add_column(
                model_class._meta.db_table,
                model_class.location_id.db_column,
                model_class.location_id
            )
        )
        print("column added: " + str(model_class))

        query = model_class.select(LocationMaster.id.alias('location_id'),
                                   model_class.id.alias('table_id')).dicts() \
            .join(LocationMaster,
                  on=((model_class.robot_id == LocationMaster.device_id) &
                      (model_class.canister_number == LocationMaster.location_number))) \

        update_dict = defaultdict(list)
        for record in query:
            update_dict[int(record['location_id'])].append(record['table_id'])


        print("Column values being updated")

        for key, value in update_dict.items():
            model_class.update(location_id=key).where(model_class.id << value).execute()

        print("Column values updated " + str(model_class))

        if remove_null:
            try:
                migrate(
                    migrator.drop_foreign_key_constraint(model_class._meta.db_table, model_class.location_id.db_column),
                    migrator.add_not_null(model_class._meta.db_table, model_class.location_id.db_column),
                    migrator.add_foreign_key_constraint(model_class._meta.db_table, model_class.location_id.db_column,
                                                        LocationMaster._meta.db_table, LocationMaster.id.db_column)
                )
            except Exception as e:
                print(e)
                print('Could not add not_null constraint to {}'.format(model_class))

        migrate(
            migrator.drop_column(
                model_class._meta.db_table,
                model_class.robot_id.db_column, migrator,
            ),
            migrator.drop_column(
                model_class._meta.db_table,
                model_class.canister_number.db_column,
            )
        )
        print("Column dropped " + str(model_class))


def migrate_68():
    init_db(db, "database_migration")

    migrator = MySQLMigrator(db)
    try:
        with db.transaction():
            migrate_device_id(migrator, IntermediateNdcBlacklist)
            migrate_device_id(migrator, IntermediateNdcBlacklistAudit)
            migrate_device_id(migrator, IntermediateReplenishAnalysis)
            migrate_device_id(migrator, IntermediatePVSPack)
            migrate_device_id(migrator, IntermediatePackProcessingOrder)
            migrate_device_id(migrator, IntermediateCanisterTracker, remove_null=False)
            migrate_device_id(migrator, IntermediatePackAnalysisDetails, remove_null=False)
            migrate_device_id(migrator, IntermediateVisionDrugPrediction)

            migrate(
                migrator.rename_column(
                    IntermediatePackAnalysisDetails._meta.db_table,
                    IntermediatePackAnalysisDetails.canister_number.db_column,
                    'location_number'
                )
            )

            migrate_location_id(migrator, IntermediateSlotTransaction, remove_null=False) # removed as some null found in production

            migrate_location_id(migrator, IntermediatePackCanisterUsage, remove_null=True)
    except (InternalError, IntegrityError) as e:
        print(e)
        print('Error occured')


if __name__ == "__main__":
    migrate_68()
