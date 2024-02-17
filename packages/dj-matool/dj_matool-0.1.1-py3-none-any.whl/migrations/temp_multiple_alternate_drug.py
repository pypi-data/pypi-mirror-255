from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import get_current_date_time


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    status_id = ForeignKeyField(CodeMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    # drug_id = ForeignKeyField(DrugMaster)

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class AlternateDrugOption(BaseModel):
    id = PrimaryKeyField()
    facility_dis_id = ForeignKeyField(FacilityDistributionMaster)
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='unique_drug_id')
    alternate_unique_drug_id = ForeignKeyField(UniqueDrug, related_name='alternate_unique_drug_id')
    active = BooleanField(default=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "alternate_drug_option"


def migrate_batch_distribution_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if AlternateDrugOption.table_exists():
        migrate(
            migrator.add_column(AlternateDrugOption._meta.db_table,
                                AlternateDrugOption.active.db_column,
                                AlternateDrugOption.active)
        )

    print('Table(s) Created: AlternateDrugOption')


if __name__ == "__main__":
    migrate_batch_distribution_master()

