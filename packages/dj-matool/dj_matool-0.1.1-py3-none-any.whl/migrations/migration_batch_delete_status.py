from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from playhouse.migrate import *
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"

def migrate_batch_delete_status():

    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    with db.transaction():
        CodeMaster.create(**{'id': 59, 'key': 59, 'value': 'Batch Deleted', 'group_id': 7})
        # CodeMaster.create(**{'id': 57, 'key': 57, 'value': 'Batch Distribution Done', 'group_id': facility_distribution_group.id})

        print('Tables Modified: CodeMaster')

if __name__ == "__main__":
    migrate_batch_delete_status()