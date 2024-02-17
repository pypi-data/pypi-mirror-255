from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from playhouse.migrate import *
import settings


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class ZoneMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "zone_master"
        indexes = (
            (('company_id', 'name'), True),
        )


class DeviceLayoutDetails(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, null=True, unique=True)
    zone_id = ForeignKeyField(ZoneMaster, null=True)
    x_coordinate = DecimalField(decimal_places=2, null=True)
    y_coordinate = DecimalField(decimal_places=2, null=True)
    marked_for_transfer = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_layout_details"


def migrate_add_data():
    init_db(db, 'database_migration')

    with db.transaction():
        if DeviceLayoutDetails.table_exists():
            data_list = [{"device_id": 1, "zone_id": 1, "x_coordinate": 11.30, "y_coordinate": 11.30,
                          "marked_for_transfer": False},
                         {"device_id": 2, "zone_id": 2, "x_coordinate": 12.30, "y_coordinate": 12.30,
                          "marked_for_transfer": True},
                         {"device_id": 3, "zone_id": 3, "x_coordinate": 11.30, "y_coordinate": 11.30,
                          "marked_for_transfer": False},
                         {"device_id": 4, "zone_id": 1, "x_coordinate": 12.30, "y_coordinate": 12.30,
                          "marked_for_transfer": False},
                         {"device_id": 5, "zone_id": 1, "x_coordinate": 13.30, "y_coordinate": 13.30,
                          "marked_for_transfer": True},
                         {"device_id": 6, "zone_id": 1, "x_coordinate": 14.30, "y_coordinate": 14.30,
                          "marked_for_transfer": True},
                         {"device_id": 7, "zone_id": 2, "x_coordinate": 13.30, "y_coordinate": 12.30,
                          "marked_for_transfer": True},
                         {"device_id": 8, "zone_id": 2, "x_coordinate": 14.30, "y_coordinate": 14.30,
                          "marked_for_transfer": False},
                         ]
            DeviceLayoutDetails.insert_many(data_list).execute()
            print("Dummy records inserted in table zone_master")


if __name__ == "__main__":
    migrate_add_data()
