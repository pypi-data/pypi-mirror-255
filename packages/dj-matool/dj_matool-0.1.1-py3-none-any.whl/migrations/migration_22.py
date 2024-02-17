from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField() # number of canisters that robot can hold
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


class CanisterDrawers(BaseModel):
    id = PrimaryKeyField()
    robot_id = ForeignKeyField(RobotMaster)
    drawer_number = SmallIntegerField()
    drawer_id = SmallIntegerField()
    ip_address = CharField()
    drawer_size = CharField(default="REGULAR", max_length=20)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawers"


class CanisterDrawerMaster(BaseModel):
    id = PrimaryKeyField()
    robot_id = ForeignKeyField(RobotMaster)
    canister_drawer_number = SmallIntegerField()
    security_code = CharField(default='0000', max_length=8)
    created_by = IntegerField() # todo check if user creates this data
    modified_by = IntegerField() # todo check if user creates this data
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawer_master"
        indexes = (
            (('robot_id', 'canister_drawer_number'), True), # keep trailing comma as suggested by peewee doc
        )


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    robot_id = ForeignKeyField(RobotMaster, null=True)
    canister_drawer_id = ForeignKeyField(CanisterDrawerMaster, null=True)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    canister_number = SmallIntegerField(default=0, null=True)
    canister_type = CharField(max_length=20)
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


def migrate_22():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    db.create_tables([CanisterDrawers], safe=True)
    print("Tables created: CanisterDrawers")

    if CanisterMaster.table_exists():
        migrate(
            migrator.drop_column(CanisterMaster._meta.db_table, CanisterMaster.canister_drawer_id.db_column)
        )
        print("Tables modified: CanisterMaster")

    if RobotMaster.table_exists():
        migrate(
            migrator.add_column(RobotMaster._meta.db_table,
                                RobotMaster.big_drawers.db_column,
                                RobotMaster.big_drawers)
        )

        migrate(
            migrator.add_column(RobotMaster._meta.db_table,
                                RobotMaster.small_drawers.db_column,
                                RobotMaster.small_drawers)
        )
        migrate(
            migrator.add_column(RobotMaster._meta.db_table,
                                RobotMaster.controller.db_column,
                                RobotMaster.controller)
        )
        print("Tables modified: RobotMaster")

    # commenting to keep it available for migration rollback
    # if CanisterDrawerMaster.table_exists():
    #     db.drop_table(CanisterDrawerMaster)
    #     print("Tables dropped: CanisterDrawerMaster")


def rollback_22():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    if CanisterMaster.table_exists():
        # migrate(
        #     migrator.add_column(CanisterMaster._meta.db_table,
        #                         CanisterMaster.canister_drawer_id.db_column,
        #                         CanisterMaster.canister_drawer_id)
        # )

        # Above code is trying to create fk constraint identifier but it is longer than 60 char
        # so It throws MySQL error (1059). SO using raw command below.
        db.execute_sql("ALTER TABLE canister_master ADD canister_drawer_id_id INTEGER, ADD CONSTRAINT FOREIGN KEY "
                       "(canister_drawer_id_id) REFERENCES canister_drawer_master(id)")

        print("Tables modified: CanisterMaster")
        if RobotMaster.table_exists():
            migrate(
                migrator.drop_column(RobotMaster._meta.db_table,
                                    RobotMaster.big_drawers.db_column)
            )

            migrate(
                migrator.drop_column(RobotMaster._meta.db_table,
                                    RobotMaster.small_drawers.db_column)
            )
            migrate(
                migrator.drop_column(RobotMaster._meta.db_table,
                                    RobotMaster.controller.db_column)
            )
            print("Tables modified: RobotMaster")