from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField( max_length=20, unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    # group_id = ForeignKeyField(GroupMaster)
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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"



class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    # pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
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
    car_id = IntegerField(null = True)
    unloading_time = DateTimeField(null=True)


    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


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


class PatientRx(BaseModel):
    id = PrimaryKeyField()
    # patient_id = ForeignKeyField(PatientMaster)
    drug_id = ForeignKeyField(DrugMaster)
    # doctor_id = ForeignKeyField(DoctorMaster)
    pharmacy_rx_no = FixedCharField(max_length=20)
    sig = CharField(max_length=1000)
    morning = FloatField(null=True)
    noon = FloatField(null=True)
    evening = FloatField(null=True)
    bed = FloatField(null=True)
    caution1 = CharField(null=True, max_length=300)
    caution2 = CharField(null=True, max_length=300)
    remaining_refill = DecimalField(decimal_places=2, max_digits=5)
    is_tapered = BooleanField(null=True)
    daw_code = SmallIntegerField(default=0)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_rx"

class PackRxLink(BaseModel):
    id = PrimaryKeyField()
    patient_rx_id = ForeignKeyField(PatientRx)
    pack_id = ForeignKeyField(PackDetails)

    # If original_drug_id is null while alternatendcupdate function
    # then store current drug id as original drug id in pack rx link
    # this is required so we can send the flag of ndc change while printing label
    original_drug_id = ForeignKeyField(DrugMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_rx_link"


class SlotDetails(BaseModel):
    id = PrimaryKeyField()
    # slot_id = ForeignKeyField(SlotHeader)
    pack_rx_id = ForeignKeyField(PackRxLink)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    is_manual = BooleanField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_details"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    # canister_number = SmallIntegerField(default=0, null=True)
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
    # location_id = ForeignKeyField(LocationMaster, null=True, unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"



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

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,1),(2,2),(3,3),(4,4)}", device_version="3.0"),
            dict(id=2, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,2),(4,3)}", device_version="3.0"),
            dict(id=3, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,4),(2,3)}", device_version="3.0"),
            dict(id=4, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(2,1),(3,4)}", device_version="3.0"),
            dict(id=5, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(3,1),(4,2)}", device_version="3.0"),
            dict(id=6, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,3)}", device_version="3.0"),
            dict(id=7, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(2,4)}", device_version="3.0"),
            dict(id=8, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(3,1)}", device_version="3.0"),
            dict(id=9, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(4,2)}}", device_version="3.0")
        ]


class SlotTransaction(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    slot_id = ForeignKeyField(SlotDetails)
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster, related_name="SlotTransaction_drug_id")
    canister_id = ForeignKeyField(CanisterMaster, related_name="SlotTransaction_canister_id", null=True)
    # canister_number = SmallIntegerField(null=True)
    # alternate_drug_id = ForeignKeyField(DrugMaster, null=True, related_name="SlotTransaction_alt_drug_id")
    alternate_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="SlotTransaction_alt_canister_id")
    dropped_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    mft_drug = BooleanField(default=False)
    IPS_update_alt_drug = BooleanField(null=True)
    IPS_update_alt_drug_error = CharField(null=True, max_length=150)
    # location_id = ForeignKeyField(LocationMaster)
    config_id = ForeignKeyField(ConfigurationMaster, null=True)
    created_by = IntegerField()
    created_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_transaction"


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


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_device_id = ForeignKeyField(DeviceMaster, null=True)
    dest_location_number = SmallIntegerField(null=True)
    dest_quadrant = SmallIntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


class PackAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    pack_id = ForeignKeyField(PackDetails)
    manual_fill_required = BooleanField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_analysis"


class PackAnalysisDetails(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(PackAnalysis)
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    canister_id = ForeignKeyField(CanisterMaster, null=True)
    # canister_number = SmallIntegerField(null=True)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    location_number = SmallIntegerField(null=True)
    drug_id = ForeignKeyField(DrugMaster)
    slot_id = ForeignKeyField(SlotDetails, null=True)  # combination of drug and slot
    quadrant = SmallIntegerField(null=True)
    drop_number = SmallIntegerField(null=True)
    config_id = ForeignKeyField(ConfigurationMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_analysis_details"


def migrate_74():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    # db.create_tables([ConfigurationMaster], safe=True)
    print('Table created: ConfigurationMaster')

    ConfigurationMaster.insert_many(ConfigurationMaster.get_initial_data()).execute()
    print('Data added: ConfigurationMaster')

    migrate(
        migrator.add_column(
            SlotTransaction._meta.db_table,
            SlotTransaction.config_id.db_column,
            SlotTransaction.config_id
        ),
        migrator.add_column(
            CanisterTransfers._meta.db_table,
            CanisterTransfers.dest_quadrant.db_column,
            CanisterTransfers.dest_quadrant
        ),
        migrator.add_column(
            LocationMaster._meta.db_table,
            LocationMaster.quadrant.db_column,
            LocationMaster.quadrant
        ),
        migrator.add_column(
            PackAnalysisDetails._meta.db_table,
            PackAnalysisDetails.slot_id.db_column,
            PackAnalysisDetails.slot_id
        ),
        migrator.add_column(
            PackAnalysisDetails._meta.db_table,
            PackAnalysisDetails.quadrant.db_column,
            PackAnalysisDetails.quadrant
        ),
        migrator.add_column(
            PackAnalysisDetails._meta.db_table,
            PackAnalysisDetails.drop_number.db_column,
            PackAnalysisDetails.drop_number
        ),
        migrator.add_column(
            PackAnalysisDetails._meta.db_table,
            PackAnalysisDetails.config_id.db_column,
            PackAnalysisDetails.config_id
        )
    )
    print('Table modified: SlotTransaction, CanisterTransfers, PackAnalysisDetails, LocationMaster')

    pack_analysis_details_list = list()

    batch_query = BatchMaster.select(fn.DISTINCT(BatchMaster.id).alias('id')).dicts()\
        .join(PackDetails, on=PackDetails.batch_id == BatchMaster.id)\
        .where(BatchMaster.status.not_in([settings.BATCH_PROCESSING_COMPLETE]))\
        .order_by(BatchMaster.id.desc())\
        .limit(20)

    batch_ids = [batch['id'] for batch in batch_query]

    print(batch_ids)

    DrugMasterAlias = DrugMaster.alias()

    query = PackAnalysisDetails.select(PackAnalysisDetails.analysis_id,
                                       PackAnalysisDetails.drug_id,
                                       fn.IF(SlotDetails.quantity >= 1, PackAnalysisDetails.canister_id, None)
                                       .alias('canister_id'),
                                       fn.IF(SlotDetails.quantity >= 1, PackAnalysisDetails.device_id, None)
                                       .alias('device_id'),
                                       fn.IF(SlotDetails.quantity >= 1, PackAnalysisDetails.location_number, None)
                                       .alias('location_number'),
                                       SlotDetails.id.alias('slot_id'),
                                       ).dicts()\
        .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
        .join(DrugMaster, on=DrugMaster.id == PackAnalysisDetails.drug_id) \
        .join(PackDetails, on=((PackDetails.id == PackAnalysis.pack_id) &
                               (PackAnalysis.batch_id == PackDetails.batch_id)))\
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
        .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        .join(DrugMasterAlias, on=((DrugMasterAlias.id == PatientRx.drug_id) &
                                   (DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) &
                                   (DrugMaster.txr == DrugMasterAlias.txr)))\
        .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id)\
        .where(PackAnalysis.batch_id << batch_ids)

    for record in query:
        analysis_details_dict = {
            'analysis_id': record['analysis_id'],
            'slot_id': record['slot_id'],
            'canister_id': record['canister_id'],
            'location_number': record['location_number'],
            'device_id': record['device_id'],
            'drug_id': record['drug_id']
        }
        pack_analysis_details_list.append(analysis_details_dict)
    print(len(pack_analysis_details_list))

    with db.atomic():
        for idx in range(0, len(pack_analysis_details_list), 900):
            # Insert 900 rows at a time.
            rows = pack_analysis_details_list[idx:idx + 900]
            PackAnalysisDetails.insert_many(rows).execute()
            print('Updated', idx)
    # PackAnalysisDetails.insert_many(pack_analysis_details_list).execute()

    PackAnalysisDetails.delete().where(PackAnalysisDetails.slot_id.is_null(True)).execute()

    migrate(
        migrator.drop_not_null(
            PackAnalysisDetails._meta.db_table,
            PackAnalysisDetails.slot_id.db_column
        ),
        migrator.drop_column(
            PackAnalysisDetails._meta.db_table,
            PackAnalysisDetails.drug_id.db_column
        )
    )

    print("Column dropped: PackAnalysisDetails")


if __name__ == "__main__":
    migrate_74()
