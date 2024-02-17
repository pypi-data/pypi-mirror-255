from dosepack.base_model.base_model import db
from playhouse.migrate import *
from src.model.model_canister_master import CanisterMaster

from model.model_init import init_db


def migration_add_column_requested_id_canister_master():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if CanisterMaster.table_exists():
            # Add column requested_id to find for which requested id canister is generated

            migrate(
                migrator.add_column(CanisterMaster._meta.db_table,
                                    CanisterMaster.requested_id.db_column,
                                    CanisterMaster.requested_id))

    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    migration_add_column_requested_id_canister_master()
