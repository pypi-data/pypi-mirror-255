
from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_unique_drug import UniqueDrug
from model.model_canister import CanisterMaster
from model.model_device_manager import RobotMaster
from src.model.model_pack_grid import PackGrid
import settings


class PackFillErrorV2(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='unique_drug_id')
    pack_id = ForeignKeyField(PackDetails, related_name='pack_id')
    note = CharField(null=True, max_length=1000)  # note provided by user for any filling error
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('unique_drug_id', 'pack_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_fill_error_v2"


class SlotFillErrorV2(BaseModel):
    id = PrimaryKeyField()
    pack_fill_error_id = ForeignKeyField(PackFillErrorV2)
    pack_grid_id = ForeignKeyField(PackGrid, related_name='pack_grid_id')
    error_qty = DecimalField(decimal_places=2, max_digits=4)
    broken = BooleanField()
    out_of_class_reported = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)

    class Meta:
        indexes = (
            (('pack_fill_error_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_v2"


class PVSDrugCount(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, related_name='pvs_drugcount_pack_id')
    unique_drug_id = ForeignKeyField(UniqueDrug, null=True, related_name='pvs_drugcount_unique_drug_id')
    pack_grid_id = ForeignKeyField(PackGrid, related_name='pvs_drugcount_pack_grid_id')
    expected_qty = DecimalField(default=None, null=True)
    predicted_qty = DecimalField(default=None, null=True)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'unique_drug_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_drug_count"


class ErrorDetails(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, related_name='pack_detail_id')
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='used_unique_drug_id')
    pack_grid_id = ForeignKeyField(PackGrid, related_name='associated_pack_grid_id')
    error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    pvs_error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    missing = DecimalField(decimal_places=2, max_digits=4, null=True)
    extra = DecimalField(decimal_places=2, max_digits=4, null=True)
    mpse = DecimalField(decimal_places=2, max_digits=4, null=True)
    broken = BooleanField(default=False)
    out_of_class_reported = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'unique_drug_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "error_details"


class PackCanisterUsage(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, related_name='processed_pack_id')
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='filled_unique_drug_id')
    robot_id = ForeignKeyField(RobotMaster, related_name='robot_id')
    canister_id = ForeignKeyField(CanisterMaster, related_name='canister_id')
    canister_number = SmallIntegerField()
    pack_grid_id = ForeignKeyField(PackGrid, related_name='used_pack_grid_id')
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'unique_drug_id', 'pack_grid_id', 'canister_number'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = 'pack_canister_usage'


def migrate_49():
    init_db(db, 'database_migration')
    db.create_tables([PVSDrugCount, SlotFillErrorV2, PackFillErrorV2, ErrorDetails, PackCanisterUsage], safe=True)  # Only create tables if they do not exist
    print("Tables Created: PVSDrugCount, SlotFillErrorV2, PackFillErrorV2, ErrorDetails, PackCanisterUsage")
