import settings
from playhouse.migrate import *

from model.model_init import init_db
from dosepack.base_model.base_model import db


from src.model.model_canister_tracker import CanisterTracker


def add_modified_date_column_in_canister_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if CanisterTracker.table_exists():
                migrate(
                    migrator.add_column(CanisterTracker._meta.db_table,
                                        CanisterTracker.modified_date.db_column,
                                        CanisterTracker.modified_date)
                )
                print("Added modified_date column in CanisterTracker")
    except Exception as e:
        settings.logger.error("Error while adding column: modified_date in CanisterTracker. e:  ", str(e))


if __name__ == "__main__":
    add_modified_date_column_in_canister_tracker()