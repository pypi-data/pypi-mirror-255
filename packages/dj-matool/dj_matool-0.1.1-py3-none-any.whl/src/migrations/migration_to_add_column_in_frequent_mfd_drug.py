import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db

from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs


def add_column_in_frequent_mfd_drug():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if FrequentMfdDrugs.table_exists():
                migrate(
                    migrator.add_column(FrequentMfdDrugs._meta.db_table,
                                        FrequentMfdDrugs.modified_date.db_column,
                                        FrequentMfdDrugs.modified_date)
                )
                print("Added modified_date column in FrequentMfdDrugs")

                migrate(
                    migrator.add_column(FrequentMfdDrugs._meta.db_table,
                                        FrequentMfdDrugs.current_pack_queue.db_column,
                                        FrequentMfdDrugs.current_pack_queue)
                )
                print("Added current_pack_queue column in FrequentMfdDrugs")

    except Exception as e:
        settings.logger.error("Error while adding columns in PVSSlot: ", str(e))


if __name__ == "__main__":
    add_column_in_frequent_mfd_drug()