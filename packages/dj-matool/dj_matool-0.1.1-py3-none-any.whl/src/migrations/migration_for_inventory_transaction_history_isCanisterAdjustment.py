from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_tracker import DrugTracker
from src.model.model_inventroy_transaction_history import InventoryTransactionHistory


def add_column_is_canister_adjustment_in_inventory_transaction_history():
    init_db(db, "database_migration")
    # migrator = SchemaMigrator(db)
    migrator = MySQLMigrator(db)

    print("Migration start : Adding isCanisterAdjustment column to inventory transaction history ")

    try:
        with db.transaction():


            migrate(
                migrator.add_column(InventoryTransactionHistory._meta.db_table,
                                    InventoryTransactionHistory.isCanisterAdjustment.db_column,
                                    InventoryTransactionHistory.isCanisterAdjustment)
            )
    except Exception as e:
        print("error", e)


if __name__ == "__main__":
    add_column_is_canister_adjustment_in_inventory_transaction_history()
    print("column isCanisterAdjustment is added")
