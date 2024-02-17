from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants


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


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class PRSDrugDetails(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    status = ForeignKeyField(CodeMaster)
    done_by = IntegerField(null=True)
    verified_by = IntegerField(null=True)
    registered_by = IntegerField(null=True)
    comments = CharField(null=True)
    face1 = TextField(null=True)
    face2 = TextField(null=True)
    side_face = TextField(null=True)
    predicted_qty = IntegerField(default=0)
    expected_qty = IntegerField(default=0)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'prs_drug_details'


def migration_add_column():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            PRSDrugDetails._meta.db_table,
            PRSDrugDetails.pvs_crop_image_qty.db_column,
            PRSDrugDetails.pvs_crop_image_qty
        )
    )
    migrate(
        migrator.add_column(
            PRSDrugDetails._meta.db_table,
            PRSDrugDetails.expected_count.db_column,
            PRSDrugDetails.expected_count
        )
    )
    print("column added: pvs_crop_image_qty and expected_count")


if __name__ == "__main__":
    migration_add_column()
