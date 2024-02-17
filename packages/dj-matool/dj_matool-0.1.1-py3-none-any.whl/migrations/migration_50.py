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


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class ActionMaster(BaseModel):
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class BatchChangeTracker(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    action_id = ForeignKeyField(ActionMaster)
    input_params = TextField(null=True)  # parameters that are applied on batch
    # e.g. {"canister_id": 1, "alt_canister_id": 10}
    packs_affected = TextField(null=True)  # if partial packs are affected, then store it
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_change_tracker"


def migrate_50():
    init_db(db, "database_migration")
    db.create_tables([BatchChangeTracker], safe=True)
    print('Table(s) Created: BatchChangeTracker')
    group_record, _ = GroupMaster.get_or_create(id=11, name='BatchChange')
    print('Table(s) Updated: GroupMaster')
    action_start_id = 3
    actions = [
        'Update Alternate Canister',
        'Update Alternate Drug Canister',
        'Update Alternate Drug',
        'Skip for Batch',
    ]
    for action in actions:
        ActionMaster.get_or_create(
            id=action_start_id,
            group_id=group_record,
            key=action_start_id,
            value=action
        )
        action_start_id += 1
    print('Table(s) Updated: ActionMaster')


if __name__ == '__main__':
    migrate_50()
