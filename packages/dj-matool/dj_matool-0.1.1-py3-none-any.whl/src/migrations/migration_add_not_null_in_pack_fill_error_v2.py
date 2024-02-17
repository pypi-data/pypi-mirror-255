from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug
from model.model_init import init_db
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2

# class PackFillErrorV2(BaseModel):
#     id = PrimaryKeyField()
#     unique_drug_id = ForeignKeyField(UniqueDrug)
#     pack_id = ForeignKeyField(PackDetails)
#     note = CharField(null=True, max_length=1000)  # note provided by user for any filling error
#     created_by = IntegerField()
#     modified_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#
#     class Meta:
#         indexes = (
#             (('unique_drug_id', 'pack_id'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "pack_fill_error_v2"
#
#
# class SlotFillErrorV2(BaseModel):
#     id = PrimaryKeyField()
#     # pack_id = ForeignKeyField(PackDetails)
#     # unique_drug_id = ForeignKeyField(UniqueDrug)  # TODO: remove
#     pack_fill_error_id = ForeignKeyField(PackFillErrorV2)
#     pack_grid_id = ForeignKeyField(PackGrid)
#     error_qty = DecimalField(decimal_places=2,
#                              max_digits=4)  # kept to support previously reported error and stable flow
#     actual_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
#     counted_error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
#     broken = BooleanField()
#     out_of_class_reported = BooleanField(default=False)
#     created_date = DateTimeField(default=get_current_date_time)
#     created_by = IntegerField(default=1)
#
#     class Meta:
#         indexes = (
#             (('pack_fill_error_id', 'pack_grid_id'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "slot_fill_error_v2"


def add_not_null_constraint_in_fillerrorv2():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if PackFillErrorV2.table_exists():
            # add not null constraint
            migrate(migrator.drop_not_null(PackFillErrorV2._meta.db_table,
                                          PackFillErrorV2.unique_drug_id.db_column))
            print("Add null constraint for unique_drug_id column in PackFillErrorV2")

        if SlotFillErrorV2.table_exists():
            # add not null constraint
            migrate(migrator.drop_not_null(SlotFillErrorV2._meta.db_table,
                                          SlotFillErrorV2.error_qty.db_column))
            print("Add null constraint for error_qty column in SlotFillErrorV2")

        if SlotFillErrorV2.table_exists():
            # add not null constraint
            migrate(migrator.drop_not_null(SlotFillErrorV2._meta.db_table,
                                          SlotFillErrorV2.broken.db_column))
            print("Add null constraint for broken column in SlotFillErrorV2")

    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    add_not_null_constraint_in_fillerrorv2()
