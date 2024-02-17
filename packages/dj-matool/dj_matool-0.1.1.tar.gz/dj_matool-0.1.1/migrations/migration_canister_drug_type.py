from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
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


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    available_quantity = SmallIntegerField()
    # canister_number = SmallIntegerField(default=0, null=True)
    canister_type = ForeignKeyField(CodeMaster, default=settings.C, related_name='canister_type')
    canister_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Medium Fast Moving"],
                                     related_name='canister_usage')
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
    product_id = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


group_master_data = [dict(id=17, name="CanisterSize"),
                     dict(id=18, name="DrugUsage"),
                     ]

code_master_data = [dict(id=settings.CANISTER_TYPE['BIG'], group_id=17,
                         key=settings.CANISTER_TYPE['BIG'], value="BIG"),
                    dict(id=settings.CANISTER_TYPE['SMALL'], group_id=17,
                         key=settings.CANISTER_TYPE['SMALL'], value="Small"),
                    dict(id=72, group_id=18, key=72, value="Fast Moving"),
                    dict(id=73, group_id=18, key=73, value="Medium Fast Moving"),
                    dict(id=74, group_id=18, key=74, value="Medium Slow Moving"),
                    dict(id=75, group_id=18, key=75, value="Slow Moving"),
                    ]


def migrate_canister_drug_type():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    for each_data in group_master_data:
        GroupMaster.create(**each_data)
    print("data inserted in group master")

    for data in code_master_data:
        CodeMaster.create(**data)
    print("data inserted in code master")



    migrate(
        migrator.drop_column(
            CanisterMaster._meta.db_table,
            CanisterMaster.canister_type.db_column,
        ),
        migrator.add_column(
            CanisterMaster._meta.db_table,
            CanisterMaster.canister_type.db_column
        ),
        migrator.add_column(
            CanisterMaster._meta.db_table,
            CanisterMaster.canister_usage.db_column,
            CanisterMaster.canister_usage
        )
    )

    print('Table updated: CanisterMaster')

    # update_big_canisters = CanisterMaster.update(canister_size=72) \
    #     .where(CanisterMaster.canister_type == settings.CANISTER_SIZE['BIG']).execute()
    #
    # print('updated_big_canister:', update_big_canisters)
    #


if __name__ == '__main__':
    migrate_canister_drug_type()
