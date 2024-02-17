from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_unique_drug import UniqueDrug


def add_col_in_unique_drug_for_drug_canister_usage():

    try:

        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():

            if UniqueDrug.table_exists():
                # add column:

                migrate(migrator.add_column(UniqueDrug._meta.db_table,
                                            UniqueDrug.min_canister.db_column,
                                            UniqueDrug.min_canister))
                print("Add 'min_canister' in UniqueDrug")
                migrate(migrator.add_column(UniqueDrug._meta.db_table,
                                            UniqueDrug.max_canister.db_column,
                                            UniqueDrug.max_canister))
                print("Add 'max_canister' in UniqueDrug")

            UniqueDrug.update(min_canister=2).execute()
            UniqueDrug.update(max_canister=2).execute()
            print("min_canister updated.")

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    add_col_in_unique_drug_for_drug_canister_usage()
