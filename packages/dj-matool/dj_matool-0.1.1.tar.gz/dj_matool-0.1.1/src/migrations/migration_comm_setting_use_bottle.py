from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src.model.model_company_setting import CompanySetting


def migration_add_code_use_bottle_inventory_in_company_settings():

    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "USE_BOTTLE_INVENTORY",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            }
            ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added USE_BOTTLE_INVENTORY")
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    migration_add_code_use_bottle_inventory_in_company_settings()
