from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from playhouse.migrate import *
import settings
from dosepack.utilities.utils import get_current_date_time
import logging

logger = logging.getLogger("root")


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class CanisterDrawerMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawer_master"
        indexes = (
            (('robot_id', 'canister_drawer_number'), True),  # keep trailing comma as suggested by peewee doc
        )


class CanisterDrawers(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawers"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class DrawerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_number = CharField(max_length=20)
    drawer_id = SmallIntegerField(null=True)
    ip_address = CharField(max_length=20, null=True)
    drawer_size = CharField(default="REGULAR", max_length=20)
    mac_address = CharField(max_length=50, null=True)
    drawer_status = BooleanField(default=True)
    security_code = CharField(default='0000', max_length=8)
    drawer_type = CharField(default="ROBOT")
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_number = CharField()
    drawer_id = ForeignKeyField(DrawerMaster, null=True)
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


def rename_canister_drawer(migrator):
    # rename_canister_drawer()
    try:
        migrate(
            migrator.rename_table(CanisterDrawers._meta.db_table, DrawerMaster._meta.db_table)
        )
        print("table canister_drawers renamed to drawer_master")

    except Exception as e:
        logger.error("Error while renaming table canister_drawer", str(e))


def alter_table_drawer_master(migrator):
    # add column security_code and drawer_type in drawer_master
    try:
        if DrawerMaster.table_exists():
            migrate(
                migrator.add_column(
                    DrawerMaster._meta.db_table,
                    DrawerMaster.security_code.db_column,
                    DrawerMaster.security_code
                ),
                migrator.add_column(
                    DrawerMaster._meta.db_table,
                    DrawerMaster.drawer_type.db_column,
                    DrawerMaster.drawer_type
                ),
                migrator.drop_not_null(DrawerMaster._meta.db_table, DrawerMaster.drawer_id.db_column),
                migrator.drop_not_null(DrawerMaster._meta.db_table, DrawerMaster.created_by.db_column),
                migrator.drop_not_null(DrawerMaster._meta.db_table, DrawerMaster.modified_by.db_column),
                migrator.drop_not_null(DrawerMaster._meta.db_table, DrawerMaster.ip_address.db_column),
            )
        print("columns security_code and drawer_type added in drawer_master")
    except Exception as e:
        logger.error("Error while modifying table drawer_master", str(e))


def drop_table_canister_drawer_master():
    # drop CanisterDrawerMaster table
    try:
        if CanisterDrawerMaster.table_exists():
            db.drop_table(CanisterDrawerMaster)
        print("Dropped table canister_drawer_master")
    except Exception as e:
        logger.error("Error while dropping table canister_drawer_master", str(e))


def add_drawer_data_in_drawer_master_from_location_master(migrator):
    try:
        # add drawer data in drawer_master
        drawer_data = list()
        drawer_records = LocationMaster.select(LocationMaster.device_id,
                                               fn.GROUP_CONCAT(fn.DISTINCT(LocationMaster.drawer_number)).alias("drawer_list"))\
                                        .dicts().group_by(LocationMaster.device_id)

        for record in drawer_records:
            for drawer in record["drawer_list"].split(','):
                drawer_data.append({"device_id": record["device_id"], "drawer_number": drawer})

        if DrawerMaster.table_exists():
            DrawerMaster.insert_many(drawer_data).execute()
            print("Drawer data inserted in drawer_master")

    except Exception as e:
        logger.error("Error while updating drawer data in drawer_master", str(e))


def add_and_update_drawer_id_location_master(migrator):
    try:
        # add column container_id
        migrate(
            migrator.add_column(
            LocationMaster._meta.db_table,
            LocationMaster.drawer_id.db_column,
            LocationMaster.drawer_id
            )
        )
        print("column container_id added in location_master")

        # update container_id in location_master
        drawer_master_records = DrawerMaster.select(
                DrawerMaster.id,
                DrawerMaster.device_id,
                DrawerMaster.drawer_number
        ).dicts()

        print("drawer_master_records: ", str(drawer_master_records))

        for record in drawer_master_records:
            LocationMaster.update(drawer_id=record["id"]).where(
                LocationMaster.device_id == record["device_id"],
                LocationMaster.drawer_number == record["drawer_number"]
            ).execute()
        print("container_id updated in location_master")

    except Exception as e:
        logger.error("Error while adding and updating column container_id in location_master", str(e))


def drop_column_drawer_number_from_location_master(migrator):
    # drop column drawer_number
    try:
        migrate(
            migrator.drop_column(
                LocationMaster._meta.db_table,
                LocationMaster.drawer_number.db_column,
                LocationMaster.drawer_number
            )
        )
        print("column drawer_number dropped from location_master")
    except Exception as e:
        logger.error("Error while droping column drawer_number from drawer_master", str(e))


def migrate_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    rename_canister_drawer(migrator)
    alter_table_drawer_master(migrator)
    drop_table_canister_drawer_master()

    add_drawer_data_in_drawer_master_from_location_master(migrator)
    add_and_update_drawer_id_location_master(migrator)

    drop_column_drawer_number_from_location_master(migrator)


if __name__ == '__main__':
    migrate_changes()