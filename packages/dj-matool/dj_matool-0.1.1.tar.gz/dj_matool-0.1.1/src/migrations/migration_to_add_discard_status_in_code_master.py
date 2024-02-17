from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster

def migration_add_discard_status_in_code_master():

    try:

        init_db(db, 'database_migration')

        if CodeMaster.table_exists():

            CodeMaster.insert(id=constants.USAGE_CONSIDERATION_DISCARD,
                              group_id=constants.CANISTER_TRACKER_USAGE_CONSIDERATION_GROUP_ID,
                              value="Usage Discard").execute()
            print("USAGE_CONSIDERATION_DISCARD inserted in CodeMaster")

            CodeMaster.insert(id=constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD,
                              group_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_GROUP_ID,
                              value="Discard").execute()
            print("CANISTER_QUANTITY_UPDATE_TYPE_DISCARD inserted in CodeMaster")

    except Exception as e:
        print(e)
        raise

if __name__ == "__main__":
    migration_add_discard_status_in_code_master()

