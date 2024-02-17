from peewee import *
from playhouse.migrate import *
import requests as r
import json
from model.model_init import init_db
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time, get_current_time, get_current_date
from dosepack.utilities.utils import call_webservice
import settings


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


class OldPackDetails(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()  # system_id from dpauth project System table
    # pack_header_id = ForeignKeyField(PackHeader)
    # batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    # pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
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
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class OldFileHeader(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True)  # added - Amisha
    message = CharField(null=True, max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField(default=get_current_date)
    created_time = TimeField(default=get_current_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class OldDoctorMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    pharmacy_doctor_id = IntegerField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
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
            db_table = "doctor_master"


class OldPatientMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # facility_id = ForeignKeyField(FacilityMaster)
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


class OldFacilityMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
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


class OldCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    # canister_drawer_id = ForeignKeyField(CanisterDrawerMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    canister_number = SmallIntegerField(default=0, null=True)
    canister_type = CharField(max_length=20)
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class OldRobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField()  # number of canisters that robot can hold
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class OldTemplateMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # patient_id = ForeignKeyField(PatientMaster)
    # file_id = ForeignKeyField(FileHeader)
    # status = ForeignKeyField(CodeMaster)
    is_modified = BooleanField()
    delivery_datetime = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


class OldNewFillDrug(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    formatted_ndc = CharField(max_length=12, null=True)
    txr = CharField(max_length=8, null=True)
    new = BooleanField(default=True)
    packs_filled = SmallIntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "new_fill_drug"


class OldTemplateDetails(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # patient_id = ForeignKeyField(PatientMaster)
    # patient_rx_id = ForeignKeyField(PatientRx)
    column_number = SmallIntegerField()
    hoa_time = TimeField()
    quantity = DecimalField(decimal_places=2, max_digits=4)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_details"


# New Models
class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField(null=True)
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=1)
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    # pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    # pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
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
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=-1)
    system_id = IntegerField(null=True)
    # status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True)  # added - Amisha
    message = CharField(null=True, max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField(default=get_current_date)
    created_time = TimeField(default=get_current_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class DoctorMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=-1)
    system_id = IntegerField(null=True)
    pharmacy_doctor_id = IntegerField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
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
            db_table = "doctor_master"


class PatientMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=-1)
    system_id = IntegerField(null=True)
    # facility_id = ForeignKeyField(FacilityMaster)
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


class FacilityMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=-1)
    system_id = IntegerField(null=True)
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


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    company_id = IntegerField(null=True)  # add not null later
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField()  # number of canisters that robot can hold
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField(default=-1)
    company_id = IntegerField(default=-1)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    # canister_drawer_id = ForeignKeyField(CanisterDrawerMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    canister_number = SmallIntegerField(default=0, null=True)
    canister_type = CharField(max_length=20)
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=-1)
    system_id = IntegerField(null=True)
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    # status = ForeignKeyField(CodeMaster)
    is_modified = BooleanField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


class SystemSetting(BaseModel):
    """
        @class: SystemSetting
        @createdBy: Dushyant Parmar
        @createdDate: 01/11/2018
        @lastModifiedBy: Dushyant Parmar
        @lastModifiedDate: 01/11/2018
        @type: class
        @desc: stores settings of system
    """
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "system_setting"
        indexes = (
            (('system_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per system
        )


class CompanySetting(BaseModel):
    """ stores setting for a company """
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )


class NewFillDrug(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField(default=-1)
    system_id = IntegerField(null=True)
    formatted_ndc = CharField(max_length=12, null=True)
    txr = CharField(max_length=8, null=True)
    new = BooleanField(default=True)
    packs_filled = SmallIntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "new_fill_drug"


class ReservedCanister(BaseModel):
    """
        Stores canisters used in batch.
        - This Model should be used to determine if canister is available
        for canister_recommendation module.
        - Delete to free canister for other batch.
    """
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "reserved_canister"


def migrate_32(env="dev"):
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    env_base_auth_url = {
        "dev": "d-auth.dosepack.com",
        "prod": "p-auth.dosepack.com",
        "qa": "q-auth.dosepack.com"
    }
    fill_manual_systems = {
        "dev": [],
        "qa": [215],
        "prod": [5, 6]
    }
    base_auth_url = env_base_auth_url[env]

    resp = r.get("https://{}/api/system_company_map".format(base_auth_url), verify=False)
    system_company_map = json.loads(resp.content)["data"]  # system_id: company_id

    def migrate_company_id(model_class, old_model_class=None, drop_system_id=True):
        """
        Adds company id using `model_class` and drops system_id if `drop_system_id` True
        Assumes Model has company_id field and old_model_class has system_id if drop_system_id is True
        """
        if model_class.table_exists():
            migrate(migrator.add_column(model_class._meta.db_table,
                                        model_class.company_id.db_column,
                                        model_class.company_id))
            print("Table Modified: " + str(model_class))
            for k, v in system_company_map.items():
                status = model_class.update(company_id=v).where(model_class.system_id == k).execute()
                print('{}: Rows updated {} for system_id {} and company_id {}'.format(model_class, status, k, v))
            if drop_system_id:
                migrate(migrator.drop_column(old_model_class._meta.db_table,
                                             old_model_class.system_id.db_column))

    migrate_company_id(PackDetails, OldPackDetails, drop_system_id=False)
    migrate(migrator.drop_not_null(PackDetails._meta.db_table, PackDetails.system_id.db_column))
    migrate_company_id(FileHeader, OldFileHeader, drop_system_id=True)
    migrate_company_id(DoctorMaster, OldDoctorMaster, drop_system_id=True)
    migrate_company_id(PatientMaster, OldPatientMaster, drop_system_id=True)
    migrate_company_id(FacilityMaster, OldFacilityMaster, drop_system_id=True)
    migrate_company_id(TemplateMaster, OldTemplateMaster, drop_system_id=False)
    migrate(migrator.drop_not_null(OldTemplateMaster._meta.db_table, OldTemplateMaster.system_id.db_column))
    migrate(migrator.add_column(TemplateMaster._meta.db_table, TemplateMaster.fill_manual.db_column,
                                TemplateMaster.fill_manual))
    migrate(migrator.drop_column(OldTemplateDetails._meta.db_table, OldTemplateDetails.system_id.db_column))
    migrate_company_id(CanisterMaster, OldCanisterMaster, drop_system_id=True)
    migrate_company_id(NewFillDrug, OldNewFillDrug, drop_system_id=False)
    migrate(migrator.drop_not_null(NewFillDrug._meta.db_table, NewFillDrug.system_id.db_column))
    migrate_company_id(RobotMaster, OldRobotMaster, drop_system_id=False)
    migrate(migrator.add_not_null(RobotMaster._meta.db_table, RobotMaster.company_id.db_column))
    db.create_tables([CompanySetting, ReservedCanister], safe=True)
    print('Table Created: CompanySetting, ReservedCanister')

    migrate(migrator.add_column(
        BatchMaster._meta.db_table, BatchMaster.system_id.db_column, BatchMaster.system_id
    ))
    print('Table Modified: BatchMaster')
    query = BatchMaster.select(BatchMaster.id,
                               fn.IFNULL(PackDetails.system_id, -1).alias('system_id')) \
        .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
        .group_by(BatchMaster.id)
    for record in query.dicts():
        BatchMaster.update(system_id=record["system_id"]) \
            .where(BatchMaster.id == record["id"]).execute()
    print('Table Updated: BatchMaster')
    migrate(
        migrator.add_not_null(BatchMaster._meta.db_table, BatchMaster.system_id.db_column)
    )
    print('Table Modified: BatchMaster')

    company_setting_list = list()
    unique_settings = list()
    for record in SystemSetting.select().dicts():
        record["company_id"] = system_company_map[str(record.pop('system_id'))]
        if (record["company_id"], record["name"]) not in unique_settings:
            company_setting_list.append(record)
            unique_settings.append((record["company_id"], record["name"]))
    CompanySetting.insert_many(company_setting_list).execute()
    print('Table Modified: CompanySetting')

    # marking template of manual filling system to fill_manual
    fill_manual_system_list = fill_manual_systems[env]
    if fill_manual_system_list:
        rows_updated = TemplateMaster.update(fill_manual=True) \
            .where(TemplateMaster.system_id << fill_manual_system_list).execute()
        print("TemplateMaster: {} rows updated for fill_manual(flag 0) column"
              .format(rows_updated))
    # removing association of template with system for dosepacker system
    query = TemplateMaster.update(system_id=None)
    if fill_manual_system_list:
        query = query. \
            where(TemplateMaster.system_id.not_in(fill_manual_system_list))
    rows_updated = query.execute()
    print("TemplateMaster: {} rows updated with system_id(NULL) column"
          .format(rows_updated))
    print('Table Modified: TemplateMaster')
    CodeMaster.create(**{'id': 38, 'key': 38, 'value': 'Processing Complete', 'group_id': 7})
    BatchMaster.update(  # considering every batch is completed before migrating
        status=settings.BATCH_PROCESSING_COMPLETE
    ).execute()
    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
    print('Status of all batch is updated to `Processing Complete`. \n'
          'Manually revert current batch status if batch processing is pending')
    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')


if __name__ == "__main__":
    import os

    os.environ.update({
        "MYSQL_DATABASE": 'dpwsdevlocal',
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "root",
        "MYSQL_PWD": "root"
    })
    migrate_32()
