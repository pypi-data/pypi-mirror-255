from dosepack.base_model.base_model import db
from playhouse.migrate import *
from src.model.model_generate_canister import GenerateCanister

from model.model_init import init_db


def migration_add_column_fulfilled_requested_canister_count():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if GenerateCanister.table_exists():
            # Add column fulfilled_requested_canister_count to track number of canister request is fufilled

            migrate(
                migrator.add_column(GenerateCanister._meta.db_table,
                                    GenerateCanister.fulfilled_requested_canister_count.db_column,
                                    GenerateCanister.fulfilled_requested_canister_count))

    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    migration_add_column_fulfilled_requested_canister_count()
