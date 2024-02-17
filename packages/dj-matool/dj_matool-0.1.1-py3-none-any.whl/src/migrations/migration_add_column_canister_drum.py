import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import *
from model.model_volumetric_analysis import BigCanisterStick, SmallCanisterStick
from src.model.model_canister_drum import CanisterDrum


class CanisterStick(BaseModel):
    """
    It contains the data related to small and big stick combination
    """
    id = PrimaryKeyField()
    big_canister_stick_id = ForeignKeyField(BigCanisterStick, related_name='big_canister_stick_id', null=True)
    small_canister_stick_id = ForeignKeyField(SmallCanisterStick, related_name='small_canister_stick_id', null=True)
    canister_drum_id = ForeignKeyField(CanisterDrum, related_name='canister_drum_id', null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_stick'


def add_columns_canister_drum():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(CanisterStick._meta.db_table,
                                CanisterStick.canister_drum_id.db_column,
                                CanisterStick.canister_drum_id),
            migrator.drop_not_null(CanisterStick._meta.db_table,
                                   CanisterStick.big_canister_stick_id.db_column),
            migrator.drop_not_null(CanisterStick._meta.db_table,
                                   CanisterStick.small_canister_stick_id.db_column)
        )
        print("Added column canister_drum_id CanisterStick and dropped not null from big and small stick")
    except Exception as e:
        settings.logger.error("Error while adding columns in CanisterStick: ", str(e))

