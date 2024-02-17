import datetime

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time, get_current_date, get_current_time
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_parameters import CanisterParameters
from src.model.model_canister_stick import CanisterStick
from src.model.model_drug_dimension import DrugDimension
from src.model.model_file_header import FileHeader
from src.model.model_location_master import LocationMaster
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
from src.model.model_pack_details import PackDetails
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_pharmacy_master import PharmacyMaster
from src.model.model_pvs_slot import PVSSlot
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_reason_master import ReasonMaster
from src.model.model_batch_master import BatchMaster

# ------------ STATUS OF CodeMaster DURING MIGRATION EXECUTION ------------
# class CodeMaster(BaseModel):
#     id = PrimaryKeyField()
#     group_id = ForeignKeyField(GroupMaster)
#     value = CharField(max_length=50)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "code_master"


class PackPlateMaster(BaseModel):
    id = PrimaryKeyField()
    pack_plate_type = ForeignKeyField(CodeMaster)
    reverse = BooleanField()
    rfid_based = BooleanField()
    created_date = DateTimeField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())
    modified_by = IntegerField()


# ------------ STATUS OF DeviceTypeMaster DURING MIGRATION EXECUTION ------------
# class DeviceTypeMaster(BaseModel):
#     id = PrimaryKeyField()
#     device_type_name = CharField(max_length=50, unique=True)
#     device_code = CharField(max_length=10, null=True, unique=True)
#     container_code = CharField(max_length=10, null=True, unique=True)
#     station_type_id = IntegerField(unique=True, null=True)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "device_type_master"


# ------------ STATUS OF DeviceMaster DURING MIGRATION EXECUTION ------------
# class DeviceMaster(BaseModel):
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     name = CharField(max_length=50)
#     serial_number = CharField(max_length=20, unique=True)
#     device_type_id = ForeignKeyField(DeviceTypeMaster)
#     system_id = IntegerField(null=True)
#     version = CharField(null=True)
#     active = IntegerField(null=True)
#     created_by = IntegerField(null=True)
#     modified_by = IntegerField(null=True)
#     created_date = DateTimeField()
#     modified_date = DateTimeField()
#     associated_device = ForeignKeyField('self', null=True)
#     ip_address = CharField(null=True)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "device_master"
#
#         indexes = (
#             (('name', 'company_id'), True),
#         )


# ------------ STATUS OF UnitMaster DURING MIGRATION EXECUTION ------------
# class UnitMaster(BaseModel):
#     """
#     Class to store the unit details.
#     """
#     id = PrimaryKeyField()
#     name = CharField()
#     type = CharField()
#     symbol = CharField()
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "unit_master"


# ------------ STATUS OF ZoneMaster DURING MIGRATION EXECUTION ------------
# class ZoneMaster(BaseModel):
#     """
#         @desc: Class to store the zone details of company.
#     """
#     id = PrimaryKeyField()
#     name = CharField(max_length=25)
#     floor = IntegerField(null=True)
#     length = DecimalField(decimal_places=2,null=True)
#     height = DecimalField(decimal_places=2,null=True)
#     width = DecimalField(decimal_places=2,null=True)
#     company_id = IntegerField()  # Foreign key field of company table of dp auth
#     x_coordinate = DecimalField(decimal_places=2,null=True)
#     y_coordinate = DecimalField(decimal_places=2,null=True)
#     dimensions_unit_id = ForeignKeyField(UnitMaster,null=True)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "zone_master"
#         indexes = (
#             (('company_id', 'name'), True),
#         )


# ------------ STATUS OF DeviceLayoutDetails DURING MIGRATION EXECUTION ------------
# class DeviceLayoutDetails(BaseModel):
#     """
#     Class to store the inventory layout related details of various devices.
#     """
#     id = PrimaryKeyField()
#     device_id = ForeignKeyField(DeviceMaster, null=True, unique=True, related_name='device_layout_device_id')
#     zone_id = ForeignKeyField(ZoneMaster, null=True, related_name='device_zone_id')
#     x_coordinate = DecimalField(decimal_places=2, null=True)
#     y_coordinate = DecimalField(decimal_places=2, null=True)
#     marked_for_transfer = BooleanField(default=False)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "device_layout_details"


class StackedDevices(BaseModel):
    """
    Class to store the stacking details (i.e which device is stacked on which device)
    of the device present in the inventory layout.
    """
    id = PrimaryKeyField()
    device_layout_id = ForeignKeyField(DeviceLayoutDetails, unique=True, related_name='device')
    stacked_on_device_id = ForeignKeyField(DeviceLayoutDetails, null=True, related_name='stacked_on_device')

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "stacked_devices"


class CanisterUsageStatistics(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField()
    ndc = CharField(unique=True)
    usage_quantity = DecimalField(decimal_places=2)
    drawer_type = CharField()


class ClientMaster(BaseModel):
    """
        @class: client_master.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table auth_user
    """
    id = PrimaryKeyField()
    client_code = CharField()

    class Meta:
        not_in_use = True


# ------------ STATUS OF PharmacyMaster DURING MIGRATION EXECUTION ------------
# class PharmacyMaster(BaseModel):
#     """
#         @class: pharmacy_master.py
#         @createdBy: Manish Agarwal
#         @createdDate: 04/19/2016
#         @lastModifiedBy: Manish Agarwal
#         @lastModifiedDate: 04/19/2016
#         @type: file
#         @desc:  Get all the pharmacy details which belongs to the
#                 particular pharmacy_id
#         @input - 1
#         @output - {"pharmacy_name": "Vibrant Care", "store_phone": "510-381-3344",
#             "store_website": "www.rxnsend.com" .. }
#     """
#     id = PrimaryKeyField()
#     system_id = IntegerField(unique=True)
#     store_name = CharField(max_length=100)
#     store_address = CharField()
#     store_phone = FixedCharField(max_length=14)
#     store_fax = FixedCharField(max_length=14, null=True)
#     store_website = CharField(max_length=50, null=True)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "pharmacy_master"


class DeviceGroupHeader(BaseModel):
    id = PrimaryKeyField()
    client_id = ForeignKeyField(ClientMaster)
    pharmacy_id = ForeignKeyField(PharmacyMaster)
    code = ForeignKeyField(CodeMaster)
    name = CharField(max_length=50)
    created_date = DateField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())
    modified_by = IntegerField()

    class Meta:
        not_in_use = True


class Manufacturer(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=100)
    mfg_date = DateField()
    exp_date = DateField()
    maintenance_time = FixedCharField(max_length=10)
    mfg_by = CharField(max_length=50)
    patent_no = FixedCharField(max_length=100)
    created_date = DateField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())
    modified_by = IntegerField()


class DeviceManager(BaseModel):
    id = PrimaryKeyField()
    client_id = ForeignKeyField(ClientMaster)
    pharmacy_id = ForeignKeyField(PharmacyMaster)
    mfg_id = ForeignKeyField(Manufacturer)
    code = ForeignKeyField(CodeMaster)
    version = FixedCharField(max_length=4)
    name = CharField(max_length=150)
    base_url = CharField(max_length=20)
    ip = CharField(max_length=40)
    port = FixedCharField(max_length=8)
    active = BooleanField(default=True)
    created_date = DateTimeField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())
    modified_by = IntegerField()

    class Meta:
        not_in_use = True


class TaskManager(BaseModel):
    """
        @class: task_manager.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table task_manager
    """
    id = PrimaryKeyField()
    client_id = ForeignKeyField(ClientMaster, null=True)
    device_id = ForeignKeyField(DeviceManager)
    task_type = ForeignKeyField(CodeMaster)
    task_id = IntegerField()
    created_by = IntegerField()
    DateTimeField(default=datetime.datetime.now())

    class Meta:
        not_in_use = True


class DeviceGroupDetails(BaseModel):
    id = PrimaryKeyField()
    client_id = ForeignKeyField(ClientMaster)
    pharmacy_id = ForeignKeyField(PharmacyMaster)
    device_group_id = ForeignKeyField(DeviceGroupHeader)
    device_id = ForeignKeyField(DeviceManager)
    created_date = DateField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())
    modified_by = IntegerField()

    class Meta:
        not_in_use = True


class RobotUnitMaster(BaseModel):
    id = PrimaryKeyField()
    client_id = ForeignKeyField(ClientMaster)
    pharmacy_id = ForeignKeyField(PharmacyMaster)
    device_group_id = ForeignKeyField(DeviceGroupHeader)
    created_date = DateField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())
    modified_by = IntegerField()

    class Meta:
        not_in_use = True


class PackStencil(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    seq_no = CharField(max_length=15)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_stencil"


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField()  # number of canisters that robot can hold
    big_drawers = IntegerField(default=4)
    small_drawers = IntegerField(default=12)
    controller = CharField(max_length=10, default="AR")
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class DeviceProperties(BaseModel):
    """
    Class to store the device properties related to inventory layout. Right now we store following properties :
    1. number_of_drawers
    2. rotate
    3. drawers_initial_pattern
    4. initials_for_each_column ( For SSR only)
    5. number_of_columns ( For SSR only)
    """
    id = PrimaryKeyField()
    device_layout_id = ForeignKeyField(DeviceLayoutDetails)
    property_name = CharField()
    property_value = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_properties"


class FileDownloadTracker(BaseModel):
    """
        @class: print_queue.py
        @createdBy: Jitendra Saxena
        @createdDate: 01/03/2018
        @lastModifiedBy:
        @lastModifiedDate:
        @type: file
        @desc: stores the history of downloaded file
    """
    id = PrimaryKeyField()
    system_id = IntegerField()
    filename = CharField(max_length=30)
    user_id = IntegerField()
    ip_address = CharField()
    downloaded_date = DateField(default=get_current_date)
    downloaded_time = TimeField(default=get_current_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_download_tracker"


# ------------ STATUS OF FacilityDistributionMaster DURING MIGRATION EXECUTION ------------
# class FacilityDistributionMaster(BaseModel):
#     id = PrimaryKeyField()
#     company_id = SmallIntegerField()
#     created_by = IntegerField()
#     modified_by = IntegerField(null=True)
#     created_date = DateTimeField(default=get_current_date_time, null=True)
#     modified_date = DateTimeField(default=get_current_date_time, null=True)
#     status_id = ForeignKeyField(CodeMaster)
#     req_dept_list = CharField(null=True, default=None)
#     ack_dept_list = CharField(null=True, default=None)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "facility_distribution_master"


# ------------ STATUS OF BatchMaster DURING MIGRATION EXECUTION ------------
# class BatchMaster(BaseModel):
#     id = PrimaryKeyField()
#     system_id = IntegerField()
#     name = CharField(null=True)
#     status = ForeignKeyField(CodeMaster, null=True)
#     created_date = DateTimeField(default=get_current_date_time, null=True)
#     modified_date = DateTimeField(default=get_current_date_time, null=True)
#     created_by = IntegerField()
#     modified_by = IntegerField(null=True)
#     split_function_id = IntegerField(null=True)
#     scheduled_start_time = DateTimeField(default=get_current_date_time(), null=True)
#     estimated_processing_time = FloatField(null=True)
#     imported_date = DateTimeField(null=True)
#     mfd_status = ForeignKeyField(CodeMaster, null=True, related_name='mfd_status_id')
#     sequence_no = IntegerField(default=0)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "batch_master"


# ------------ STATUS OF FacilityMaster DURING MIGRATION EXECUTION ------------
# class FacilityMaster(BaseModel):
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     pharmacy_facility_id = IntegerField()
#     facility_name = CharField(max_length=40)
#     address1 = CharField(null=True)
#     address2 = CharField(null=True)
#     cellphone = FixedCharField(max_length=14, null=True)
#     workphone = FixedCharField(max_length=14, null=True)
#     fax = FixedCharField(max_length=14, null=True)
#     email = CharField(max_length=320, null=True)
#     website = CharField(null=True, max_length=50)
#     active = BooleanField(null=True)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         indexes = (
#             (('pharmacy_facility_id', 'company_id'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "facility_master"


# ------------ STATUS OF PatientMaster DURING MIGRATION EXECUTION ------------
# class PatientMaster(BaseModel):
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     facility_id = ForeignKeyField(FacilityMaster)
#     pharmacy_patient_id = IntegerField()
#     first_name = CharField(max_length=50)
#     last_name = CharField(max_length=50)
#     patient_picture = CharField(null=True)
#     address1 = CharField()
#     zip_code = CharField(max_length=9)
#     city = CharField(max_length=50, null=True)
#     state = CharField(max_length=50, null=True)
#     address2 = CharField(null=True)
#     cellphone = FixedCharField(max_length=14, null=True)
#     workphone = FixedCharField(max_length=14, null=True)
#     fax = FixedCharField(max_length=14, null=True)
#     email = CharField(max_length=320, null=True)
#     website = CharField(null=True, max_length=50)
#     active = BooleanField(null=True)
#     dob = DateField(null=True)
#     allergy = CharField(null=True, max_length=500)
#     patient_no = FixedCharField(null=True, max_length=35)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         indexes = (
#             (('pharmacy_patient_id', 'company_id'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "patient_master"


# ------------ STATUS OF FileHeader DURING MIGRATION EXECUTION ------------
# class FileHeader(BaseModel):
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     status = ForeignKeyField(CodeMaster)
#     filename = CharField(max_length=150)
#     filepath = CharField(null=True, max_length=200)
#     manual_upload = BooleanField(null=True)  # added - Amisha
#     message = CharField(null=True, max_length=500)
#     task_id = CharField(max_length=155, null=True)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateField(default=get_current_date)
#     created_time = TimeField(default=get_current_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "file_header"


# ------------ STATUS OF PackHeader DURING MIGRATION EXECUTION ------------
# class PackHeader(BaseModel):
#     id = PrimaryKeyField()
#     patient_id = ForeignKeyField(PatientMaster)
#     file_id = ForeignKeyField(FileHeader)
#     total_packs = SmallIntegerField()
#     start_day = SmallIntegerField()
#     pharmacy_fill_id = IntegerField()
#     delivery_datetime = DateTimeField(null=True, default=None)
#     scheduled_delivery_date = DateTimeField(null=True, default=None)  # delivery_date from the facility schedule
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "pack_header"


# ------------ STATUS OF ContainerMaster DURING MIGRATION EXECUTION ------------
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
#     drawer_type = ForeignKeyField(CodeMaster, related_name="drawer_type", null=True)
#     drawer_usage = ForeignKeyField(CodeMaster, related_name="drawer_usage", null=True)
#     shelf = IntegerField(null=True)
#     serial_number = CharField(max_length=20, null=True, unique=True)
#     lock_status = BooleanField(default=False) # True-open and False-close
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "container_master"
#
#         indexes = (
#             (('device_id', 'drawer_name', 'ip_address'), True),
#         )


# ------------ STATUS OF PackDetails DURING MIGRATION EXECUTION ------------
# class PackDetails(BaseModel):
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     system_id = IntegerField(null=True)  # system_id from dpauth project System table
#     pack_header_id = ForeignKeyField(PackHeader)
#     batch_id = ForeignKeyField(BatchMaster, null=True)
#     pack_display_id = IntegerField()
#     pack_no = SmallIntegerField()
#     is_takeaway = BooleanField(default=False)
#     pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
#     filled_by = FixedCharField(max_length=64)
#     consumption_start_date = DateField()
#     consumption_end_date = DateField()
#     filled_days = SmallIntegerField()
#     fill_start_date = DateField()
#     delivery_schedule = FixedCharField(max_length=50)
#     association_status = BooleanField(null=True)
#     rfid = FixedCharField(null=True, max_length=20, unique=True)
#     pack_plate_location = FixedCharField(max_length=2, null=True)
#     order_no = IntegerField(null=True)
#     filled_date = DateTimeField(null=True)
#     filled_at = SmallIntegerField(null=True)
#     # marked filled at which step
#     # Any manual goes in 0-10, If filled by system should be > 10
#     #  0 - Template(Auto marked manual for manual system),
#     #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
#     #  11 - DosePacker
#     fill_time = IntegerField(null=True, default=None)  # in seconds
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateField()
#     modified_date = DateTimeField(default=get_current_date_time)
#     facility_dis_id = ForeignKeyField(FacilityDistributionMaster, null=True)
#     # facility_dis_id_id = IntegerField()
#     car_id = IntegerField(null=True)
#     unloading_time = DateTimeField(null=True)
#     # facility_distribution_id_id = IntegerField()
#     pack_sequence = IntegerField(null=True)
#     dosage_type = ForeignKeyField(CodeMaster, default=settings.DOSAGE_TYPE_MULTI)
#     filling_status = ForeignKeyField(CodeMaster, null=True, related_name="packdetails_filling_status")
#     container_id = ForeignKeyField(ContainerMaster, null=True)
#
#     FILLED_AT_MAP = {
#         0: 'Auto',
#         1: 'Pre-Batch Allocation',
#         2: 'Post-Import',
#         3: 'Manual Verification Station',
#         4: 'Pre-Import',
#         11: 'DosePacker'
#     }
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "pack_details"


class FillProductivity(BaseModel):
    id = PrimaryKeyField()
    session_id = IntegerField()
    system_id = IntegerField()
    total_time = IntegerField(null=True)  # in seconds
    user_station_time = IntegerField(null=True)  # in seconds
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "fill_productivity"


class FilledPack(BaseModel):
    id = PrimaryKeyField()
    productivity_id = ForeignKeyField(FillProductivity)
    pack_id = ForeignKeyField(PackDetails)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "filled_pack"


class NdcBlacklist(BaseModel):
    """
        @class: ndc_blacklist.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table ndc_blacklist
    """
    id = PrimaryKeyField()
    ndc = CharField(max_length=14)
    device_id = ForeignKeyField(DeviceMaster)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()
    note = CharField(max_length=100)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ndc_blacklist"


class NdcBlacklistAudit(BaseModel):
    """
        @class: ndc_blacklist_audit.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table ndc_blacklist_audit
    """
    id = PrimaryKeyField()
    ndc_blacklist_id = ForeignKeyField(NdcBlacklist)
    ndc = CharField(max_length=14)
    note = CharField(max_length=100)
    deleted_date = DateTimeField(default=get_current_date_time)
    deleted_by = IntegerField()
    device_id = ForeignKeyField(DeviceMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ndc_blacklist_audit"


class UpdatedDrugMaster(BaseModel):
    """
        This class will be responsible for storing the drug updated value if any pharmtechs updates during inventory
        management
    """
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster)
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
    verification_status = IntegerField(default=0)
    created_by = IntegerField(null=True)
    created_time = DateTimeField(default=get_current_date_time)
    verified_by = IntegerField(null=True)
    verified_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "updated_drug_master"


class PackProcessingOrder(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    pack_id = ForeignKeyField(PackDetails)
    device_id = ForeignKeyField(DeviceMaster)
    pack_order = SmallIntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_processing_order"


# ------------ STATUS OF CanisterDrum DURING MIGRATION EXECUTION ------------
# class CanisterDrum(BaseModel):
#     id = PrimaryKeyField()
#     serial_number = CharField(unique=True, max_length=10, null=False)
#     width = DecimalField(decimal_places=3, max_digits=6, null=False)
#     depth = DecimalField(decimal_places=3, max_digits=6, null=False)
#     length = DecimalField(decimal_places=3, max_digits=6, null=False)
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     created_by = IntegerField(null=False)
#     modified_by = IntegerField(null=False)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "canister_drum"


# ------------ STATUS OF SmallCanisterStick DURING MIGRATION EXECUTION ------------
# class SmallCanisterStick(BaseModel):
#     """
#     It contain the data related to small canister sticks.
#     """
#     id = PrimaryKeyField()
#     length = DecimalField(decimal_places=3, max_digits=6)
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     created_by = IntegerField(default=1)
#     modified_by = IntegerField(default=1)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == '_':
#             db_table = 'small_canister_stick'


# ------------ STATUS OF BigCanisterStick DURING MIGRATION EXECUTION ------------
# class BigCanisterStick(BaseModel):
#     """
#     It contain the data related to big canister sticks.
#     """
#     id = PrimaryKeyField()
#     width = DecimalField(decimal_places=3, max_digits=6)
#     depth = DecimalField(decimal_places=3, max_digits=6)
#     serial_number = CharField(unique=True, max_length=10)
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     created_by = IntegerField(default=1)
#     modified_by = IntegerField(default=1)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == '_':
#             db_table = 'big_canister_stick'


# ------------ STATUS OF CanisterStick DURING MIGRATION EXECUTION ------------
# class CanisterStick(BaseModel):
#     """
#     It contains the data related to small and big stick combination
#     """
#     id = PrimaryKeyField()
#     big_canister_stick_id = ForeignKeyField(BigCanisterStick, related_name='big_canister_stick', null=True)
#     small_canister_stick_id = ForeignKeyField(SmallCanisterStick, related_name='small_canister_stick', null=True)
#     canister_drum_id = ForeignKeyField(CanisterDrum, related_name='canister_drum', null=True)
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     created_by = IntegerField(default=1)
#     modified_by = IntegerField(default=1)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == '_':
#             db_table = 'canister_stick'


# ------------ STATUS OF LocationMaster DURING MIGRATION EXECUTION ------------
# class LocationMaster(BaseModel):
#     id = PrimaryKeyField()
#     device_id = ForeignKeyField(DeviceMaster, related_name="lm_device_id_id")
#     location_number = IntegerField()
#     container_id = ForeignKeyField(ContainerMaster, related_name='location_container_id')
#     display_location = CharField()
#     quadrant = SmallIntegerField(null=True)
#     is_disabled = BooleanField(default=False)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "location_master"


# ------------ STATUS OF CanisterMaster DURING MIGRATION EXECUTION ------------
# class CanisterMaster(BaseModel):
#     """
#         @class: canister_master.py
#         @createdBy: Manish Agarwal
#         @createdDate: 04/19/2016
#         @lastModifiedBy: Manish Agarwal
#         @lastModifiedDate: 04/19/2016
#         @type: file
#         @desc: logical class for table canister_master
#     """
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     # robot_id = ForeignKeyField(RobotMaster, null=True)
#     drug_id = ForeignKeyField(DrugMaster)
#     rfid = FixedCharField(null=True, unique=True, max_length=32)
#     available_quantity = SmallIntegerField()
#     # canister_number = SmallIntegerField(default=0, null=True)F
#     active = BooleanField()
#     reorder_quantity = SmallIntegerField()
#     barcode = CharField(max_length=15)
#     canister_code = CharField(max_length=25, unique=True, null=True)
#     label_print_time = DateTimeField(null=True, default=None)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
#     product_id = IntegerField(null=True)
#     canister_type = ForeignKeyField(CodeMaster, default=71, related_name='canister_type')  # 70-big, 71-small
#     canister_stick_id = ForeignKeyField(CanisterStick, related_name="canister_stick_id", null= True)
#     # canister_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Medium Fast Moving"])
#     requested_id = IntegerField(null=True)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "canister_master"


class ReplenishAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    device_id = ForeignKeyField(DeviceMaster)
    drug_id = ForeignKeyField(DrugMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    quantity = SmallIntegerField()
    process_order_id = ForeignKeyField(PackProcessingOrder)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "replenish_analysis"


# ------------ STATUS OF PackGrid DURING MIGRATION EXECUTION ------------
# class PackGrid(BaseModel):
#     id = PrimaryKeyField()
#     slot_row = SmallIntegerField()
#     slot_column = SmallIntegerField()
#     slot_number = SmallIntegerField()
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "pack_grid"


# ------------ STATUS OF DoctorMaster DURING MIGRATION EXECUTION ------------
# class DoctorMaster(BaseModel):
#     id = PrimaryKeyField()
#     company_id = IntegerField()
#     pharmacy_doctor_id = IntegerField()
#     first_name = CharField(max_length=50)
#     last_name = CharField(max_length=50)
#     address1 = CharField(null=True)
#     address2 = CharField(null=True)
#     cellphone = FixedCharField(max_length=14, null=True)
#     workphone = FixedCharField(max_length=14, null=True)
#     fax = FixedCharField(max_length=14, null=True)
#     email = CharField(max_length=320, null=True)
#     website = CharField(null=True, max_length=50)
#     active = BooleanField(null=True)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         indexes = (
#             (('pharmacy_doctor_id', 'company_id'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "doctor_master"


# ------------ STATUS OF PatientRx DURING MIGRATION EXECUTION ------------
# class PatientRx(BaseModel):
#     id = PrimaryKeyField()
#     patient_id = ForeignKeyField(PatientMaster)
#     drug_id = ForeignKeyField(DrugMaster)
#     doctor_id = ForeignKeyField(DoctorMaster)
#     pharmacy_rx_no = FixedCharField(max_length=20)
#     sig = CharField(max_length=1000)
#     morning = FloatField(null=True)
#     noon = FloatField(null=True)
#     evening = FloatField(null=True)
#     bed = FloatField(null=True)
#     caution1 = CharField(null=True, max_length=300)
#     caution2 = CharField(null=True, max_length=300)
#     remaining_refill = DecimalField(decimal_places=2, max_digits=5)
#     is_tapered = BooleanField(null=True)
#     daw_code = SmallIntegerField(default=0)
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         indexes = (
#             (('patient_id', 'pharmacy_rx_no'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "patient_rx"


# ------------ STATUS OF PackRxLink DURING MIGRATION EXECUTION ------------
# class PackRxLink(BaseModel):
#     id = PrimaryKeyField()
#     patient_rx_id = ForeignKeyField(PatientRx)
#     pack_id = ForeignKeyField(PackDetails)
#
#     # If original_drug_id is null while alternatendcupdate function
#     # then store current drug id as original drug id in pack rx link
#     # this is required so we can send the flag of ndc change while printing label
#     original_drug_id = ForeignKeyField(DrugMaster, null=True)
#     bs_drug_id = ForeignKeyField(DrugMaster, null=True,
#                                  related_name='bs_drug_id')  # drug_id selected from batch scheduling logic.
#     fill_manually = BooleanField(default=False)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "pack_rx_link"


class PackFillError(BaseModel):
    id = PrimaryKeyField()
    pack_rx_id = ForeignKeyField(PackRxLink)
    note = CharField(null=True, max_length=1000)  # note provided by user for any filling error
    pill_misplaced = BooleanField(default=False)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_fill_error"


# ------------ STATUS OF GroupMaster DURING MIGRATION EXECUTION ------------
# class GroupMaster(BaseModel):
#     id = PrimaryKeyField()
#     name = CharField(max_length=50)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "group_master"


# ------------ STATUS OF ReasonMaster DURING MIGRATION EXECUTION ------------
# class ReasonMaster(BaseModel):
#     id = PrimaryKeyField()
#     reason_group = ForeignKeyField(GroupMaster)
#     reason = CharField()
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "reason_master"


class PackFillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    fill_error_id = ForeignKeyField(PackFillError)
    reason_id = ForeignKeyField(ReasonMaster)  # predefined reason, selected by user
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_fill_error_details"


class SlotFillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    pack_fill_error_details_id = ForeignKeyField(PackFillErrorDetails)
    pack_grid_id = ForeignKeyField(PackGrid)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_details"


class SlotFillError(BaseModel):
    id = PrimaryKeyField()
    pack_fill_error_id = ForeignKeyField(PackFillError)
    broken = BooleanField()  # flag to indicate broken pills
    error_quantity = DecimalField(decimal_places=2, max_digits=4)
    pack_grid_id = ForeignKeyField(PackGrid)

    # `error_quantity` is relative to dropped quantity

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error"


class ErrorMaster(BaseModel):
    """
        @class: error_master.py
        @createdBy: Manish Agarwal
        @createdDate: 04/17/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/17/2016
        @type: file
        @desc: logical class for table error_master
    """
    error_id = PrimaryKeyField()
    error_no = SmallIntegerField(unique=True)
    error_code = CharField(max_length=50)
    error_description = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=datetime.datetime.now())
    modified_date = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "error_master"


class ParameterHeader(BaseModel):

    id = PrimaryKeyField()
    parameter_code = CharField(max_length=50)
    name = CharField(max_length=50)
    type = ForeignKeyField(CodeMaster)
    help_note = CharField(max_length=150)
    seq_no = SmallIntegerField()
    created_date = DateTimeField(default=datetime.datetime.now())
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "parameter_header"


class ParameterDetails(BaseModel):

    id = PrimaryKeyField()
    client_id = ForeignKeyField(ClientMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    user_id = IntegerField()
    code = ForeignKeyField(ParameterHeader)
    char_value = CharField(null=True)
    numeric_value = IntegerField(null=True)
    date_value = DateField(null=True)
    note = CharField(max_length=150)
    created_date = DateTimeField(default=datetime.datetime.now())
    created_by = IntegerField()
    modified_by = IntegerField()
    modified_date = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "parameter_details"


class User(BaseModel):

    id = PrimaryKeyField()
    user_name = CharField(unique=True, max_length=64)
    password = CharField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = CharField(max_length=320)
    is_admin = BooleanField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=datetime.datetime.now())
    modified_date = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "user"


class JobMaster(BaseModel):
    id = PrimaryKeyField()
    type = IntegerField()  # describes the type of job whether scheduling reporting email others
    description = CharField()
    active = BooleanField()
    request_url = CharField()  # webservice url pointing to that job
    request_type = IntegerField()  # type of webservice url (GET or POST or PUT or other)
    created_by = IntegerField()
    created_date_time = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "job_master"


class JobDetails(BaseModel):

    id = PrimaryKeyField()
    job_id = ForeignKeyField(JobMaster)
    client_id = ForeignKeyField(ClientMaster)
    argument1 = CharField()  # first argument to the webservice
    argument2 = CharField()
    argument3 = CharField()
    argument4 = CharField()
    argument5 = CharField()
    argument6 = CharField()
    created_by = IntegerField()
    created_date_time = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "job_details"


class JobScheduling(BaseModel):

    id = PrimaryKeyField()
    job_details_id = ForeignKeyField(JobDetails)
    client_id = ForeignKeyField(ClientMaster)
    device_id = ForeignKeyField(RobotMaster)
    user_id = ForeignKeyField(User)
    job_scheduled_id = CharField(null=True)
    cron_string = CharField(max_length=20)
    active = BooleanField()
    status = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date_time = DateTimeField(default=datetime.datetime.now())
    modified_date_time = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "job_scheduling"


class EmailRecipients(BaseModel):

    id = PrimaryKeyField()
    job_schedule_id = ForeignKeyField(JobScheduling)
    as_attachment = BooleanField()
    user_id = ForeignKeyField(User)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date_time = DateTimeField(default=datetime.datetime.now())
    modified_date_time = DateTimeField(default=datetime.datetime.now())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "email_recipients"


class JobSchedulingHistory(BaseModel):

    id = PrimaryKeyField()
    job_scheduled_id = ForeignKeyField(JobScheduling)
    status = IntegerField()
    count = IntegerField()
    created_by = IntegerField()
    created_date_time = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "job_scheduling_history"


class UserHistory(BaseModel):

    id = PrimaryKeyField()
    user_id = ForeignKeyField(User)
    username = CharField()
    action = BooleanField()
    token = CharField()
    ip = CharField(max_length=40)
    created_date = DateTimeField(default=datetime.datetime.now())
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "user_history"


class PVSPack(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    device_id = ForeignKeyField(DeviceMaster)
    mft_status = BooleanField()  # TODO check if needed in slots also
    user_station_status = BooleanField(default=False)  # update on every slot @DushyantP
    deleted = BooleanField(default=False)  # TODO delete if previous pack present
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_pack'


class PVSBatchDrugs(BaseModel):  # stores drug split in batch created by pvs
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot)
    drug_id = ForeignKeyField(UniqueDrug)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_batch_drugs'


class TechnicianPack(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    technician_id = IntegerField()
    pvs_pack_id = ForeignKeyField(PVSPack)
    verified_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    total_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    verification_status = BooleanField(null=True, default=None)
    start_time = DateTimeField(null=True)  # time for technician
    end_time = DateTimeField(null=True)
    verification_time = SmallIntegerField(null=True)  # total time for verification in seconds
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_pack'


class TechnicianSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_sh_id = ForeignKeyField(PVSSlot)
    technician_id = IntegerField()
    verified = SmallIntegerField()  # 0 Reject, 1 Verified, 2 Not sure 3 reset
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_slot_header'


class TechnicianSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_sd_id = ForeignKeyField(PVSSlotDetails)
    technician_id = IntegerField()
    technician_ndc = CharField()
    original_ndc_match = BooleanField()  # original ndc == technician ndc
    pvs_ndc_match = BooleanField()  # PVSSlotDetails.predicted_ndc == technician ndc
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_slot_details'


class PackLifeCycle(BaseModel):
    id = PrimaryKeyField()
    pack_header_id = ForeignKeyField(PackHeader)
    IPS_rx_file_comm = BooleanField(null=True)
    IPS_slot_file_comm = BooleanField(null=True)
    IPS_finalize_pack_comm = BooleanField(null=True)
    IPS_rx_file_comm_error = CharField(null=True, max_length=150)
    IPS_slot_file_comm_error = CharField(null=True, max_length=150)
    IPS_finalize_pack_comm_error = CharField(null=True, max_length=150)
    pack_generation_status = SmallIntegerField(default=0, null=True)
    created_by = IntegerField()
    created_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_life_cycle"


class SlotHeaderTransaction(BaseModel):
    id = PrimaryKeyField()
    slot_header_id = ForeignKeyField(SlotHeader)
    manual_fill_required = BooleanField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_header_transaction"


class SkipUSPack(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "skip_us_pack"


class FileLifeCycle(BaseModel):
    id = PrimaryKeyField()
    file_id = ForeignKeyField(FileHeader)

    class Meta:
        not_in_use = True


class CanisterRegister(BaseModel):  # To store register canister recommendation
    id = PrimaryKeyField()
    system_id = IntegerField()
    drug_id = ForeignKeyField(DrugMaster)
    canister_quantity = SmallIntegerField(default=1)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_register"


class CanisterStickParameters(BaseModel):
    """
    Currently not in use. Created for future use
    """
    id = PrimaryKeyField()
    canister_stick_id = ForeignKeyField(CanisterStick)
    canister_parameter_id = ForeignKeyField(CanisterParameters)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_stick_parameters'


class LocationMapping(BaseModel):
    id = PrimaryKeyField()
    location_id = ForeignKeyField(LocationMaster, unique=True)
    ndc = CharField(max_length=14, unique=True)

    # todo: Ask whether to link the locations with ndc of formatted ndc.

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_mapping"


class MftDrugSlotDetails(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotDetails, unique=True)
    qty = DecimalField(decimal_places=2, max_digits=4)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mft_drug_slot_details"


class ModuleTypeMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=255)
    record_screen_interaction = BooleanField(null=True)
    idle_time_seconds = IntegerField(null=True, default=None)
    expected_seconds_per_unit = IntegerField(null=True, default=None)
    module_category_id = IntegerField()  # 1 = Pre Processing, 2 = Post Init

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "module_type_master"


class UserSession(BaseModel):
    id = PrimaryKeyField()
    module_type_id = ForeignKeyField(ModuleTypeMaster)
    module_url = CharField(max_length=255)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    system_id = IntegerField()
    company_id = IntegerField()
    user_id = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "user_session"


class UserSessionMeta(BaseModel):
    id = PrimaryKeyField()
    user_session_id = ForeignKeyField(UserSession)
    name = CharField(max_length=255)
    value = CharField(max_length=255, null=True)

    class Meta:
        indexes = (
            # create a unique composite key on user_session_id/name/
            (('user_session_id', 'name'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "user_session_meta"


class UserSessionInteractionTracker(BaseModel):
    id = PrimaryKeyField()
    user_session_id = ForeignKeyField(UserSession)
    idle = BooleanField()
    start_time = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "user_session_interaction_tracker"


class SkipStickRecommendation(BaseModel):
    """
    Stores the recommendation if it was over written by the dosepack admin
    """
    id = PrimaryKeyField()
    drug_dimension_id = ForeignKeyField(DrugDimension)
    recommended_small_stick_id = ForeignKeyField(SmallCanisterStick)
    used_small_stick_id = ForeignKeyField(SmallCanisterStick, related_name="used_small_stick")
    recommended_big_stick_id = ForeignKeyField(BigCanisterStick)
    used_big_stick_id = ForeignKeyField(BigCanisterStick, related_name="used_big_stick")
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'skip_stick_recommendation'


def db_cleaner_v3():
    init_db(db, 'database_migration')

    if PackPlateMaster.table_exists():
        db.drop_tables([PackPlateMaster])
        print("Table dropped: PackPlateMaster")

    if StackedDevices.table_exists():
        db.drop_tables([StackedDevices])
        print("Table dropped: StackedDevices")

    if CanisterUsageStatistics.table_exists():
        db.drop_tables([CanisterUsageStatistics])
        print("Table dropped: CanisterUsageStatistics")

    if DeviceGroupDetails.table_exists():
        db.drop_tables([DeviceGroupDetails])
        print("Table dropped: DeviceGroupDetails")

    if TaskManager.table_exists():
        db.drop_tables([TaskManager])
        print("Table dropped: TaskManager")

    if DeviceManager.table_exists():
        db.drop_tables([DeviceManager])
        print("Table dropped: DeviceGroupDetails")

    if Manufacturer.table_exists():
        db.drop_tables([Manufacturer])
        print("Table dropped: Manufacturer")

    if RobotUnitMaster.table_exists():
        db.drop_tables([RobotUnitMaster])
        print("Table dropped: RobotUnitMaster")

    if DeviceGroupHeader.table_exists():
        db.drop_tables([DeviceGroupHeader])
        print("Table dropped: DeviceGroupHeader")

    if PackStencil.table_exists():
        db.drop_tables([PackStencil])
        print("Table dropped: PackStencil")

    if RobotMaster.table_exists():
        db.drop_tables([RobotMaster])
        print("Table dropped: RobotMaster")

    if DeviceProperties.table_exists():
        db.drop_tables([DeviceProperties])
        print("Table dropped: DeviceProperties")

    if FileDownloadTracker.table_exists():
        db.drop_tables([FileDownloadTracker])
        print("Table dropped: FileDownloadTracker")

    if FilledPack.table_exists():
        db.drop_tables([FilledPack])
        print("Table dropped: FilledPack")

    if FillProductivity.table_exists():
        db.drop_tables([FillProductivity])
        print("Table dropped: FillProductivity")

    if NdcBlacklist.table_exists():
        db.drop_tables([NdcBlacklist])
        print("Table dropped: NdcBlacklist")

    if NdcBlacklistAudit.table_exists():
        db.drop_tables([NdcBlacklistAudit])
        print("Table dropped: NdcBlacklistAudit")

    if UpdatedDrugMaster.table_exists():
        db.drop_tables([UpdatedDrugMaster])
        print("Table dropped: UpdatedDrugMaster")

    if ReplenishAnalysis.table_exists():
        db.drop_tables([ReplenishAnalysis])
        print("Table dropped: ReplenishAnalysis")

    if PackProcessingOrder.table_exists():
        db.drop_tables([PackProcessingOrder])
        print("Table dropped: PackProcessingOrder")

    if SlotFillErrorDetails.table_exists():
        db.drop_tables([SlotFillErrorDetails])
        print("Table dropped: SlotFillErrorDetails")

    if SlotFillError.table_exists():
        db.drop_tables([SlotFillError])
        print("Table dropped: SlotFillError")

    if PackFillErrorDetails.table_exists():
        db.drop_tables([PackFillErrorDetails])
        print("Table dropped: PackFillErrorDetails")

    if PackFillError.table_exists():
        db.drop_tables([PackFillError])
        print("Table dropped: PackFillError")

    if ErrorMaster.table_exists():
        db.drop_tables([ErrorMaster])
        print("Table dropped: ErrorMaster")

    if ParameterDetails.table_exists():
        db.drop_tables([ParameterDetails])
        print("Table dropped: ParameterDetails")

    if ParameterHeader.table_exists():
        db.drop_tables([ParameterHeader])
        print("Table dropped: ParameterHeader")

    if JobSchedulingHistory.table_exists():
        db.drop_tables([JobSchedulingHistory])
        print("Table dropped: JobSchedulingHistory")

    if EmailRecipients.table_exists():
        db.drop_tables([EmailRecipients])
        print("Table dropped: EmailRecipients")

    if JobScheduling.table_exists():
        db.drop_tables([JobScheduling])
        print("Table dropped: JobScheduling")

    if JobDetails.table_exists():
        db.drop_tables([JobDetails])
        print("Table dropped: JobDetails")

    if JobMaster.table_exists():
        db.drop_tables([JobMaster])
        print("Table dropped: JobMaster")

    if UserHistory.table_exists():
        db.drop_tables([UserHistory])
        print("Table dropped: UserHistory")

    if User.table_exists():
        db.drop_tables([User])
        print("Table dropped: User")

    if ClientMaster.table_exists():
        db.drop_tables([ClientMaster])
        print("Table dropped: ClientMaster")

    if TechnicianSlot.table_exists():
        db.drop_tables([TechnicianSlot])
        print("Table dropped: TechnicianSlot")

    if TechnicianSlotDetails.table_exists():
        db.drop_tables([TechnicianSlotDetails])
        print("Table dropped: TechnicianSlotDetails")

    if TechnicianPack.table_exists():
        db.drop_tables([TechnicianPack])
        print("Table dropped: TechnicianPack")

    if PVSPack.table_exists():
        db.drop_tables([PVSPack])
        print("Table dropped: PVSPack")

    if PVSBatchDrugs.table_exists():
        db.drop_tables([PVSBatchDrugs])
        print("Table dropped: PVSBatchDrugs")

    if PackLifeCycle.table_exists():
        db.drop_tables([PackLifeCycle])
        print("Table dropped: PackLifeCycle")

    if SlotHeaderTransaction.table_exists():
        db.drop_tables([SlotHeaderTransaction])
        print("Table dropped: SlotHeaderTransaction")

    if SkipUSPack.table_exists():
        db.drop_tables([SkipUSPack])
        print("Table dropped: SkipUSPack")

    if FileLifeCycle.table_exists():
        db.drop_tables([FileLifeCycle])
        print("Table dropped: FileLifeCycle")

    if CanisterRegister.table_exists():
        db.drop_tables([CanisterRegister])
        print("Table dropped: CanisterRegister")

    if CanisterStickParameters.table_exists():
        db.drop_tables([CanisterStickParameters])
        print("Table dropped: CanisterStickParameters")

    if LocationMapping.table_exists():
        db.drop_tables([LocationMapping])
        print("Table dropped: LocationMapping")

    if MftDrugSlotDetails.table_exists():
        db.drop_tables([MftDrugSlotDetails])
        print("Table dropped: MftDrugSlotDetails")

    if UserSessionInteractionTracker.table_exists():
        db.drop_tables([UserSessionInteractionTracker])
        print("Table dropped: UserSessionInteractionTracker")

    if UserSessionMeta.table_exists():
        db.drop_tables([UserSessionMeta])
        print("Table dropped: UserSessionMeta")

    if UserSession.table_exists():
        db.drop_tables([UserSession])
        print("Table dropped: UserSession")

    if ModuleTypeMaster.table_exists():
        db.drop_tables([ModuleTypeMaster])
        print("Table dropped: ModuleTypeMaster")

    if SkipStickRecommendation.table_exists():
        db.drop_tables([SkipStickRecommendation])
        print("Table dropped: SkipStickRecommendation")




if __name__ == "__main__":
    db_cleaner_v3()
