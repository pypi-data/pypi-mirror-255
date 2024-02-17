from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from playhouse.migrate import *
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


def migrate_17():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(BatchMaster._meta.db_table,
                            BatchMaster.name.db_column,
                            BatchMaster.name)
    )

    migrate(
        migrator.add_column(BatchMaster._meta.db_table,
                            BatchMaster.status.db_column,
                            BatchMaster.status)
    )
    migrate(
        migrator.add_column(BatchMaster._meta.db_table,
                            BatchMaster.modified_date.db_column,
                            BatchMaster.modified_date)
    )
    migrate(
        migrator.add_column(BatchMaster._meta.db_table,
                            BatchMaster.modified_by.db_column,
                            BatchMaster.modified_by)
    )
    print('Table Modified: BatchMaster')
    with db.transaction():
        batch_group = GroupMaster.create(**{'id': 7, 'name': 'BatchStatus'})
        CodeMaster.create(**{'id': 34, 'key': 34, 'value': 'Pending', 'group_id': batch_group.id})
        CodeMaster.create(**{'id': 35, 'key': 35, 'value': 'Canister Transfer Recommended', 'group_id': batch_group.id})
        CodeMaster.create(**{'id': 36, 'key': 36, 'value': 'Canister Transfer Done', 'group_id': batch_group.id})
        CodeMaster.create(**{'id': 37, 'key': 37, 'value': 'Imported', 'group_id': batch_group.id})
        print('Tables Modified: GroupMaster, CodeMaster')


def rollback_17():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    with db.transaction():
        try:
            from model.model_code import CodeMaster
            CodeMaster.delete().where(CodeMaster.id << [34, 35, 36, 37]).execute()
            batch_group = GroupMaster.delete().where(GroupMaster.id == 7).execute()
            print('Tables Modified: GroupMaster, CodeMaster')
        except (InternalError, IntegrityError) as e:
            print(e)

    try:
        migrate(
            # CanisterMaster._meta.db_table, CanisterMaster.canister_drawer_id.db_column
            migrator.drop_column(BatchMaster._meta.db_table,
                                BatchMaster.name.db_column)
        )

        migrate(
            migrator.drop_column(BatchMaster._meta.db_table,
                                BatchMaster.status.db_column)
        )
        migrate(
            migrator.drop_column(BatchMaster._meta.db_table,
                                BatchMaster.modified_date.db_column)
        )
        migrate(
            migrator.drop_column(BatchMaster._meta.db_table,
                                BatchMaster.modified_by.db_column)
        )
    except (IntegrityError, InternalError) as e:
        print(e)

    print("Table Modified: BatchMaster")