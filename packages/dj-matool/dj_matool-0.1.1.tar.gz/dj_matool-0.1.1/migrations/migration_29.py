from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from playhouse.migrate import *
import settings


class RobotMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    robot_id = ForeignKeyField(RobotMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class OldCanisterHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    canister_number = SmallIntegerField(default=0)
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"


class CanisterHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    current_robot_id = ForeignKeyField(RobotMaster, null=True, related_name='current_robot_id')
    previous_robot_id = ForeignKeyField(RobotMaster, null=True, related_name='previous_robot_id')
    # drug_id = ForeignKeyField(DrugMaster)
    current_canister_number = SmallIntegerField(null=True)
    previous_canister_number = SmallIntegerField(null=True)
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"


def migrate_29():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if OldCanisterHistory.table_exists():
        migrate(
            migrator.rename_column(
                OldCanisterHistory._meta.db_table,
                OldCanisterHistory.canister_number.db_column,
                CanisterHistory.current_canister_number.db_column
            ),
            migrator.rename_column(
                OldCanisterHistory._meta.db_table,
                OldCanisterHistory.robot_id.db_column,
                CanisterHistory.current_robot_id.db_column
            ),
            migrator.add_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_robot_id.db_column,
                CanisterHistory.previous_robot_id
            ),
            migrator.add_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_canister_number.db_column,
                CanisterHistory.previous_canister_number
            )
        )
        print("Table Modified: CanisterHistory")

if __name__ == "__main__":
    migrate_29()


