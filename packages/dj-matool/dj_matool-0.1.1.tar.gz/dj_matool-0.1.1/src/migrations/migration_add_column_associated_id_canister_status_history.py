from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time, get_current_date, get_current_time
from model.model_init import init_db
from playhouse.migrate import *
import settings
from src.model.model_canister_status_history import CanisterStatusHistory


def add_column_associated_canister_status_history_id():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            CanisterStatusHistory._meta.db_table,
            CanisterStatusHistory.associated_canister.db_column,
            CanisterStatusHistory.associated_canister
        )
    )
    print("associated_canister column added in canister_status_history table")


if __name__ == "__main__":
    # add associated_canister(canister_status_history id)in canister status history table
    add_column_associated_canister_status_history_id()
