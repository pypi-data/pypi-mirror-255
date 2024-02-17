from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_migration_details import MigrationDetails


def migration_create_table_migration_details():
    init_db(db, 'database_migration')
    if not MigrationDetails.table_exists():
        db.create_tables([MigrationDetails], safe=True)
        print('Table(s) created: MigrationDetails')


if __name__ == "__main__":
    migration_create_table_migration_details()
