from playhouse.migrate import *

from dosepack.base_model.base_model import db
from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs
from model.model_init import init_db


def add_null_constraint_in_batch_id_column_in_FrequentMfdDrugs():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if FrequentMfdDrugs.table_exists():
            # add not null constraint
            migrate(migrator.drop_not_null(FrequentMfdDrugs._meta.db_table,
                                          FrequentMfdDrugs.batch_id.db_column))
            print("Add null constraint for batch_id column in FrequentMfdDrugs")


    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    add_null_constraint_in_batch_id_column_in_FrequentMfdDrugs()
