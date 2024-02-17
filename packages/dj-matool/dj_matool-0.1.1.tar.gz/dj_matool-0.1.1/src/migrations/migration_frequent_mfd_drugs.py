from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs
from src.model.model_group_master import GroupMaster


def migration_create_frequent_mfd_drugs_table():
    try:

        init_db(db, 'database_migration')

        if FrequentMfdDrugs.table_exists():
            db.drop_table(FrequentMfdDrugs)
            print('Table(s) dropped: FrequentMfdDrugs')

        if not FrequentMfdDrugs.table_exists():
            db.create_tables([FrequentMfdDrugs], safe=True)
            print('Table(s) created: FrequentMfdDrugs')

        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.FREQUENT_MFD_DRUGS_STATUS_GROUP_ID,
                               name='FrequentMfdDrugsStatus').execute()
            print("FREQUENT_MFD_DRUGS_STATUS_GROUP_ID inserted in GroupMaster")

        if CodeMaster.table_exists():

            CodeMaster.insert(id=constants.PENDING_MFD_DRUD_DIMENSION_FLOW,
                              group_id=constants.FREQUENT_MFD_DRUGS_STATUS_GROUP_ID,
                              value="Pending").execute()
            print("PENDING_MFD_DRUD_DIMENSION_FLOW inserted in CodeMaster")

            CodeMaster.insert(id=constants.SKIPPED_MFD_DRUG_DIMENSION_FLOW,
                              group_id=constants.FREQUENT_MFD_DRUGS_STATUS_GROUP_ID,
                              value="Skipped").execute()
            print("SKIPPED_MFD_DRUG_DIMENSION_FLOW inserted in CodeMaster")

            CodeMaster.insert(id=constants.DONE_MFD_DRUG_DIMENSION_FLOW,
                              group_id=constants.FREQUENT_MFD_DRUGS_STATUS_GROUP_ID,
                              value="Done").execute()
            print("DONE_MFD_DRUG_DIMENSION_FLOW inserted in CodeMaster")

    except Exception as e:
        print(e)
        raise


if __name__ == "__main__":
    migration_create_frequent_mfd_drugs_table()
