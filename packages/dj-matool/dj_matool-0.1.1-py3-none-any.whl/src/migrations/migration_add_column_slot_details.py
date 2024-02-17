import settings
from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *

from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_header import SlotHeader


class SlotDetails(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotHeader, related_name="slot_id_id")
    pack_rx_id = ForeignKeyField(PackRxLink, related_name="pack_rx_id_id")
    quantity = DecimalField(decimal_places=2, max_digits=4)
    is_manual = BooleanField()
    drug_id = ForeignKeyField(DrugMaster, related_name="drug_id_id", null=True)
    original_drug_id = ForeignKeyField(DrugMaster, related_name="slot_details_original_drug_id_id", null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_details"


def add_column_in_slot_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        #  add column drug id in slot details
        if SlotDetails.table_exists():
            migrate(
                migrator.add_column(
                    SlotDetails._meta.db_table,
                    SlotDetails.original_drug_id.db_column,
                    SlotDetails.original_drug_id),
            )
            migrate(
                migrator.add_column(
                    SlotDetails._meta.db_table,
                    SlotDetails.drug_id.db_column,
                    SlotDetails.drug_id
                )
            )
            print("Added column in SlotDetails Table")
    except Exception as e:
        print("Error while adding columns in SlotDetails: ", str(e))
        return e


if __name__ == "__main__":
    add_column_in_slot_details()
