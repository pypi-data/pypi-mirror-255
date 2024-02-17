import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_details import SlotDetails
from src.model.model_pack_details import PackDetails
from dosepack.base_model.base_model import db, BaseModel
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_tracker import DrugTracker as DT
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_tracker import CanisterTracker

class DrugTracker(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotDetails)
    canister_id = ForeignKeyField(CanisterMaster)
    drug_id = ForeignKeyField(DrugMaster)
    drug_quantity = IntegerField(default=0)
    canister_tracker_id = ForeignKeyField(CanisterTracker)
    comp_canister_tracker_id = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    is_deleted = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_tracker"

def add_and_update_columns_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if DT.table_exists():
                migrate(migrator.add_column(DT._meta.db_table,
                                            DT.drug_lot_master_id.db_column,
                                            DT.drug_lot_master_id
                                            )

                        )
                print("Added drug_lot_master_id column in drug_tracker")

            if DT.table_exists():
                migrate(migrator.add_column(DT._meta.db_table,
                                            DT.filled_at.db_column,
                                            DT.filled_at
                                            )
                        )
                print("Added filled_at column in drug_tracker")

            if DT.table_exists():
                migrate(migrator.add_column(DT._meta.db_table,
                                            DT.created_by.db_column,
                                            DT.created_by
                                            )
                        )
                print("Added created_by column in drug_tracker")

            if DT.table_exists():
                migrate(migrator.add_column(DT._meta.db_table,
                                            DT.pack_id.db_column,
                                            DT.pack_id
                                            )
                        )
                print("Added pack_id column in drug_tracker")

            if DT.table_exists():
                migrate(migrator.add_column(DT._meta.db_table,
                                            DT.is_overwrite.db_column,
                                            DT.is_overwrite
                                            )
                        )
                print("Added is_overwrite column in drug_tracker")

            if DT.table_exists():
                migrate(migrator.drop_not_null(DT._meta.db_table,
                                               DT.canister_id.db_column
                                               )
                        )
                print("Add null constraint for canister_id column in drug_tracker")

            if DT.table_exists():
                migrate(migrator.drop_not_null(DT._meta.db_table,
                                               DT.canister_tracker_id.db_column
                                               )
                        )
                print("Add null constraint for canister_tracker_id column in drug_tracker")

            if DrugTracker.table_exists():
                migrate(migrator.drop_column(DrugTracker._meta.db_table,
                                             DrugTracker.is_deleted.db_column
                                             )
                        )
                print("is_deleted column is dropped")

            if DT.table_exists():
                sql = 'ALTER TABLE drug_tracker MODIFY drug_quantity decimal(4,2) NOT NULL default 0;'
                db.execute_sql(sql)
                print("Datatype of the drug_quantity column is updated")

    except Exception as e:
        settings.logger.error("Error while adding or updating columns in drug_tracker: ", str(e))


if __name__ == "__main__":
    add_and_update_columns_in_drug_tracker()
