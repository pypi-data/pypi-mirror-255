import json
import base64
from dosepack.base_model.base_model import db, BaseModel
from src.model.model_drug_master import DrugMaster
from model.model_device_manager import RobotMaster
# from model.model_canister import CanisterMaster
from playhouse.migrate import *
import settings


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class CanisterHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    robot_id = ForeignKeyField(RobotMaster)
    drug_id = ForeignKeyField(DrugMaster)
    canister_number = SmallIntegerField(default=0)
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"


class CanisterTracker(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    refill_type = SmallIntegerField(null=True)
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    # expiration_date = DateField(null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField()
    created_time = TimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


def migrate_7():
    json_file = open('config.json', "r")
    data = json.load(json_file)
    json_file.close()

    # Here database_migration is the key for the db engine present in
    # config.json file

    try:
        database = data["database_migration"]["db"]
        username = base64.b64decode(data["database_migration"]["user"])
        password = base64.b64decode(data["database_migration"]["passwd"])
        host = data["database_migration"]["host"]
        port = 3306
    except Exception as ex:
        raise Exception("Incorrect Value for db engine")

    db.init(database, user=username, password=password, host=host, port=port)

    migrator = MySQLMigrator(db)
    with db.transaction():
        migrate(migrator.drop_not_null(CanisterHistory._meta.db_table, CanisterHistory.robot_id.db_column))
        migrate(migrator.drop_not_null(CanisterTracker._meta.db_table, CanisterTracker.robot_id.db_column))
        CanisterHistory.update(**{'action': 'DELETE'}).where(CanisterHistory.action == 'REMOVE').execute()
        print('Table(s) Modified: CanisterHistory, CanisterTracker')