from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class GuidedTracker(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_tracker"


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class GuidedTransferCycleHistory(BaseModel):
    id = PrimaryKeyField()
    guided_tracker_id = ForeignKeyField(GuidedTracker)
    canister_id = ForeignKeyField(CanisterMaster)
    action_id = ForeignKeyField(ActionMaster)
    current_status_id = ForeignKeyField(CodeMaster, related_name='current_status')
    previous_status_id = ForeignKeyField(CodeMaster, related_name='previous_state')
    action_taken_by = IntegerField(null=False)
    action_datetime = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_transfer_cycle_history"


class GuidedTransferHistoryComment(BaseModel):
    id = PrimaryKeyField()
    guided_transfer_history_id = ForeignKeyField(GuidedTransferCycleHistory)
    comment = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_transfer_history_comment"


def migration_add_guided_tx_history_tables():
    init_db(db, 'database_migration')
    db.create_tables([GuidedTransferCycleHistory], safe=True)
    print('Table(s) created: GuidedTransferCycleHistory')
    db.create_tables([GuidedTransferHistoryComment], safe=True)
    print('Table(s) created: GuidedTransferHistoryComment')


