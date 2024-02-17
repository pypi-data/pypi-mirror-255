from playhouse.migrate import *
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class SlotFillErrorV2(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    # unique_drug_id = ForeignKeyField(UniqueDrug)  # TODO: remove
    # pack_fill_error_id = ForeignKeyField(PackFillErrorV2)
    # pack_grid_id = ForeignKeyField(PackGrid)
    error_qty = DecimalField(decimal_places=2, max_digits=4)
    actual_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    counted_error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    broken = BooleanField()
    out_of_class_reported = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)

    class Meta:
        indexes = (
            (('pack_fill_error_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_v2"

def migrate_66():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)

    migrate(
        migrator.drop_column(
            SlotFillErrorV2._meta.db_table,
            SlotFillErrorV2.actual_qty.db_column,
        ),
        migrator.drop_column(
            SlotFillErrorV2._meta.db_table,
            SlotFillErrorV2.counted_error_qty.db_column,
        )
    )
    print("Columns dropped in SlotFillErrorV2")


if __name__ == '__main__':
    migrate_66()
