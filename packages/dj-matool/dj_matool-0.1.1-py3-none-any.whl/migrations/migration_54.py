from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
from src.api_utility import get_expected_delivery_date


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


class FacilityMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    pharmacy_facility_id = IntegerField()
    facility_name = CharField(max_length=40)
    address1 = CharField(null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_master"


class PatientMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    facility_id = ForeignKeyField(FacilityMaster)
    pharmacy_patient_id = IntegerField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    patient_picture = CharField(null=True)
    address1 = CharField()
    zip_code = CharField(max_length=9)
    city = CharField(max_length=50, null=True)
    state = CharField(max_length=50, null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    dob = DateField(null=True)
    allergy = CharField(null=True, max_length=500)
    patient_no = FixedCharField(null=True, max_length=35)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"


class FacilitySchedule(BaseModel):
    id = PrimaryKeyField()
    fill_cycle = ForeignKeyField(CodeMaster)  # 46=Weekly, 47=Bi-weekly, 48=monthly(28 days) and 49=other
    # week_day = IntegerField(null=True)  # 0=Monday, 1=Tuesday, .. 5=Saturday, 6=Sunday
    days = IntegerField(null=True)  # scheduled after every n days
    start_date = DateTimeField(null=True)  # start date for schedule
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    # Constants
    SCHEDULE_TYPE_WEEKLY = 46
    SCHEDULE_TYPE_BI_WEEKLY = 47
    SCHEDULE_TYPE_MONTHLY = 48
    SCHEDULE_TYPE_OTHER = 49
    FREQUENCY_IN_DAYS_DICT = {SCHEDULE_TYPE_WEEKLY: 7, SCHEDULE_TYPE_BI_WEEKLY: 14, SCHEDULE_TYPE_MONTHLY: 28}
    FREQUENCY_DICT = {k: '{}D'.format(v) for k, v in FREQUENCY_IN_DAYS_DICT.items()}

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'facility_schedule'


class PatientRx(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    # drug_id = ForeignKeyField(DrugMaster)
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


class PatientSchedule(BaseModel):
    id = PrimaryKeyField()
    facility_id = ForeignKeyField(FacilityMaster)
    patient_id = ForeignKeyField(PatientMaster)
    schedule_id = ForeignKeyField(FacilitySchedule, null=True)
    total_packs = IntegerField()
    delivery_date_offset = SmallIntegerField(null=True, default=None)
    active = BooleanField(default=True)
    last_import_date = DateTimeField(default=get_current_date_time)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('facility_id', 'patient_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'patient_schedule'


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True) # added - Amisha
    message = CharField(null=True, max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    # created_date = DateField(default=get_current_date)
    # created_time = TimeField(default=get_current_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class PackHeader(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    total_packs = SmallIntegerField()
    start_day = SmallIntegerField()
    pharmacy_fill_id = IntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    scheduled_delivery_date = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_header"


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    # batch_id = ForeignKeyField(BatchMaster, null=True)
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
    # marked filled at which step
    # Any manual goes in 0-10, If filled by system should be > 10
    #  0 - Template(Auto marked manual for manual system),
    #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
    #  11 - DosePacker
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class PackRxLink(BaseModel):
    id = PrimaryKeyField()
    patient_rx_id = ForeignKeyField(PatientRx)
    pack_id = ForeignKeyField(PackDetails)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_rx_link"
import datetime

def migrate_54():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            PackHeader._meta.db_table,
            PackHeader.scheduled_delivery_date.db_column,
            PackHeader.scheduled_delivery_date
        )
    )
    print('Table(s) Updated: PackHeader')
    print('Updating delivery_date')

    PackDetailsAlias = PackDetails.alias()

    query = PackDetails.select(PatientSchedule,
                               FacilitySchedule,
                               PackDetails,
                               fn.MIN(PackDetails.consumption_start_date).alias('consumption_start_date'),
                               PackRxLink.pack_id,
                               PackHeader.id.alias('pack_header_id'),
                               fn.CONCAT(PackDetails.pack_status).alias('statuses'),
                               fn.CONCAT(PackHeader.id).alias('pack_ids')).dicts()\
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id)\
        .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)\
        .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id)\
        .join(PatientSchedule, on=((PatientSchedule.patient_id == PatientMaster.id) & (PatientSchedule.facility_id == PatientMaster.facility_id)))\
        .join(FacilitySchedule, on=PatientSchedule.schedule_id == FacilitySchedule.id)\
        .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id)\
        .join(PackDetailsAlias, on=PackDetailsAlias.pack_header_id == PackHeader.id)\
        .group_by(PackHeader.id)\
        .where((PackDetailsAlias.pack_status << [settings.PENDING_PACK_STATUS]) |
               (PackDetails.created_date.between(datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now())))

    print(query)
    count = 0
    for record in query:
        delivery_data = get_expected_delivery_date(record['consumption_start_date'], record['start_date'],
                                                   record['delivery_date_offset'], record['fill_cycle'],
                                                   record['days'])
        print("consumption start date: {}, scheduled date: {}".format(record['consumption_start_date'], delivery_data['next_delivery_date']))
        print("pack ids {} and status {}".format(record['pack_ids'], record['statuses']))
        PackHeader.update(scheduled_delivery_date=delivery_data['next_delivery_date'])\
            .where(PackHeader.id == record['pack_header_id']).execute()
        count = count + 1

    print('Delivery_date updated', count)


if __name__ == '__main__':
    migrate_54()
