from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_canister_orders import CanisterOrders


def migration_create_table_canister_orders():
    init_db(db, 'database_migration')
    if not CanisterOrders.table_exists():
        db.create_tables([CanisterOrders], safe=True)
        print('Table(s) created: CanisterOrders')


if __name__ == "__main__":
    migration_create_table_canister_orders()
