from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster
from src.model.model_remote_tech_slot_details import RemoteTechSlotDetails


def add_column_in_remote_tech_slot_details():

    try:

        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():

            if GroupMaster.table_exists():

                GroupMaster.insert(id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                                   name='SkippedAndMappedRtsDrugStatus').execute()
                print("SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID inserted in GroupMaster")

            if CodeMaster.table_exists():

                CodeMaster.insert(id=constants.SKIPPED_AND_FOREIGN_OBJECT_MAPPED,
                                  group_id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                                  value="Skipped And Foreign Object Mapped").execute()
                print("SKIPPED_AND_FOREIGN_OBJECT_MAPPED inserted in CodeMaster")

                CodeMaster.insert(id=constants.SKIPPED_AND_BROKEN_PILL_MAPPED,
                                  group_id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                                  value="Skipped And Broken Pill Mapped").execute()
                print("SKIPPED_AND_BROKEN_PILL_MAPPED inserted in CodeMaster")

                CodeMaster.insert(id=constants.SKIPPED_AND_MAPPED_BUT_USER_NOT_SURE,
                                  group_id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                                  value="Skipped And Mapped But User Not Sure").execute()
                print("SKIPPED_AND_MAPPED_BUT_USER_NOT_SURE inserted in CodeMaster")

                CodeMaster.insert(id=constants.SKIPPED_AND_SURE_MAPPED,
                                  group_id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                                  value="Skipped And Sure Mapped").execute()
                print("SKIPPED_AND_SURE_MAPPED inserted in CodeMaster")

                CodeMaster.insert(id=constants.SKIPPED_AND_MAPPED_BUT_REFERENCE_IMAGE_NOT_AVAILABLE,
                                  group_id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                                  value="Reference Image Not Available").execute()
                print("SKIPPED_AND_MAPPED_BUT_REFERENCE_IMAGE_NOT_AVAILABLE inserted in CodeMaster")

            if RemoteTechSlotDetails.table_exists():
                # add column:
                migrate(migrator.add_column(RemoteTechSlotDetails._meta.db_table,
                                            RemoteTechSlotDetails.mapped_status.db_column,
                                            RemoteTechSlotDetails.mapped_status))
                print("Add 'mapped_status' in RemoteTechSlotDetails")

                migrate(migrator.add_column(RemoteTechSlotDetails._meta.db_table,
                                            RemoteTechSlotDetails.linked_qty.db_column,
                                            RemoteTechSlotDetails.linked_qty))
                print("Add 'linked_qty' in RemoteTechSlotDetails")

            RemoteTechSlotDetails.update(mapped_status=constants.SKIPPED_AND_MAPPED_BUT_USER_NOT_SURE,
                                         linked_qty=0) \
                                    .where(RemoteTechSlotDetails.label_drug_id.is_null(True)) \
                                    .execute()
            print("status updated.")

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    add_column_in_remote_tech_slot_details()
