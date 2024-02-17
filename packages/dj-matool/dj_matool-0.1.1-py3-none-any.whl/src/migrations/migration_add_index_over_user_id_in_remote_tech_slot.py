from playhouse.migrate import MySQLMigrator, migrate
import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_remote_tech_slot import RemoteTechSlot


def migration_add_index_over_user_id_in_remote_tech_slot():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        migrate(
            migrator.add_index(RemoteTechSlot._meta.db_table,
                               (RemoteTechSlot.remote_tech_id.db_column, ))
        )

        print("Migration completed.")
    except Exception as e:
        settings.logger.error("Error while adding index ", str(e))


if __name__ == "__main__":
    migration_add_index_over_user_id_in_remote_tech_slot()
