import logging

from playhouse.migrate import *

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_drug_tracker import DrugTracker

logger = logging.getLogger("root")


def add_column_scan_type_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugTracker._meta.db_table,
                                DrugTracker.scan_type.db_column,
                                DrugTracker.scan_type)
        )
        print("Added column scan_type in DrugTracker")
    except Exception as e:
        logger.error("Error while adding column in DrugTracker: ", str(e))


if __name__ == "__main__":
    add_column_scan_type_in_drug_tracker()
