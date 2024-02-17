from typing import Optional

from peewee import (ForeignKeyField, PrimaryKeyField, CharField, DecimalField, BooleanField)
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src.constants import MANUAL_USER_COUNT, NUMBER_OF_DAYS_TO_ORDER
from src.model.model_adhoc_drug_request import AdhocDrugRequest
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_batch_pack_data import BatchPackData
from src.model.model_company_setting import CompanySetting
from src.model.model_facility_distribution_master import FacilityDistributionMaster


class CurrentInventoryMapping(BaseModel):
    id = PrimaryKeyField()
    facility_dist_id = ForeignKeyField(FacilityDistributionMaster)
    batch_drug_id = ForeignKeyField(BatchDrugData)
    reserve_ndc = CharField(max_length=14)
    reserve_txr = CharField(max_length=8, null=True)
    reserve_qty = DecimalField(decimal_places=2)
    is_active = BooleanField(default=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "current_inventory_mapping"


def migration_drug_req_check(company_id: Optional[int] = None, user_id: Optional[int] = None):
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    print("Starting migration_drug_req_check.")
    populate_company_setting(company_id=company_id if company_id else 3, user_id=user_id if user_id else 2)
    create_tables()
    update_table(migrator)
    print("migration_drug_req_check ran successfully.")


def populate_company_setting(company_id, user_id):
    try:
        row_data = [
            {"company_id": company_id, "name": MANUAL_USER_COUNT, "value": 3, "created_by": user_id,
             "modified_by": user_id},
            {"company_id": company_id, "name": NUMBER_OF_DAYS_TO_ORDER, "value": 4, "created_by": user_id,
             "modified_by": user_id}
        ]
        CompanySetting.insert_many(row_data).execute()
        print("Data Inserted in CompanySetting table.")

    except Exception as e:
        print(e)


def create_tables():
    db.create_tables([AdhocDrugRequest], safe=True)
    print("Table created: AdhocDrugRequest")
    db.create_tables([BatchPackData], safe=True)
    print("Table created: BatchPackData")


def update_table(migrator):
    try:
        if CurrentInventoryMapping.table_exists():
            db.execute_sql("ALTER TABLE current_inventory_mapping ADD COLUMN reserve_txr VARCHAR(8) AFTER reserve_ndc")
            print("Column added: CurrentInventoryMapping.reserve_txr")

            db.execute_sql("UPDATE current_inventory_mapping cim INNER JOIN batch_drug_data bdd "
                           "ON bdd.id = cim.batch_drug_id_id SET cim.reserve_txr = bdd.txr")
            print("Values added to the column reserve_txr column of the table CurrentInventoryMapping.")

            migrate(migrator.add_not_null(CurrentInventoryMapping._meta.db_table,
                                          CurrentInventoryMapping.reserve_txr.db_column))
            print("Not null constraint added to the reserve_txr column of the table CurrentInventoryMapping.")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_drug_req_check()
