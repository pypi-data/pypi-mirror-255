from playhouse.migrate import *
import settings
from collections import defaultdict
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
import itertools


class PackGrid(BaseModel):
    id = PrimaryKeyField()
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    slot_number = SmallIntegerField()

    class Meta:
        index = ()
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_grid"

class OldSlotHeader(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    hoa_date = DateField()
    hoa_time = TimeField()
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_header"


class NewSlotHeader(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    hoa_date = DateField()
    hoa_time = TimeField()
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    pack_grid_id = ForeignKeyField(PackGrid, null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_header"

class FinalSlotHeader(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    hoa_date = DateField()
    hoa_time = TimeField()
    pack_grid_id = ForeignKeyField(PackGrid)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_header"


class OldSlotFillError(BaseModel):
    id = PrimaryKeyField()
    # pack_fill_error_id = ForeignKeyField(PackFillError)
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    broken = BooleanField()  # flag to indicate broken pills
    error_quantity = DecimalField(decimal_places=2, max_digits=4)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error"


class NewSlotFillError(BaseModel):
    id = PrimaryKeyField()
    # pack_fill_error_id = ForeignKeyField(PackFillError)
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    broken = BooleanField()  # flag to indicate broken pills
    error_quantity = DecimalField(decimal_places=2, max_digits=4)
    pack_grid_id = ForeignKeyField(PackGrid, null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error"


class FinalSlotFillError(BaseModel):
    id = PrimaryKeyField()
    # pack_fill_error_id = ForeignKeyField(PackFillError)
    broken = BooleanField()  # flag to indicate broken pills
    error_quantity = DecimalField(decimal_places=2, max_digits=4)
    pack_grid_id = ForeignKeyField(PackGrid)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error"


class OldSlotFillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    # pack_fill_error_details_id = ForeignKeyField(PackFillErrorDetails)
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_details"


class NewSlotFillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    # pack_fill_error_details_id = ForeignKeyField(PackFillErrorDetails)
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    pack_grid_id = ForeignKeyField(PackGrid, null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_details"


class FinalSlotFillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    # pack_fill_error_details_id = ForeignKeyField(PackFillErrorDetails)
    pack_grid_id = ForeignKeyField(PackGrid)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_details"


def migrate_48():
    init_db(db, 'database_migration')

    db.create_tables([PackGrid], safe=True)
    print('table created: PackGrid')

    migrator = MySQLMigrator(db)

    pack_grid_data = list()
    for row, col in itertools.product(range(7), range(4)):
        if col % 2 == 0:
            pack_grid_detail = {
                "slot_row": row,
                "slot_column": col,
                "slot_number": (col*7) + (row+1)
            }
        else:
            pack_grid_detail = {
                "slot_row": row,
                "slot_column": col,
                "slot_number": (col*7) + (7-row)
            }
        pack_grid_data.append(pack_grid_detail)
    print(pack_grid_data)
    PackGrid.insert_many(pack_grid_data).execute()

    migrate(
        migrator.add_column(
            NewSlotHeader._meta.db_table,
            NewSlotHeader.pack_grid_id.db_column,
            NewSlotHeader.pack_grid_id
        ),
        migrator.add_column(
            NewSlotFillError._meta.db_table,
            NewSlotFillError.pack_grid_id.db_column,
            NewSlotFillError.pack_grid_id
        ),
        migrator.add_column(
            NewSlotFillErrorDetails._meta.db_table,
            NewSlotFillErrorDetails.pack_grid_id.db_column,
            NewSlotFillErrorDetails.pack_grid_id
        )
    )

    slot_update_data = defaultdict(int)

    query = PackGrid.select().dicts()
    for record in query:
        slot_update_data[(record['slot_row'], record['slot_column'])] = record['id']

    print('Tables being updated: SlotHeader, SlotFillError')
    for slot_data, pack_grid_id in slot_update_data.items():
        update_slot_header = NewSlotHeader.update({NewSlotHeader.pack_grid_id : pack_grid_id})\
            .where(NewSlotHeader.slot_row == slot_data[0], NewSlotHeader.slot_column==slot_data[1]).execute()
        update_slot_fill_error = NewSlotFillError.update({NewSlotFillError.pack_grid_id : pack_grid_id})\
            .where(NewSlotFillError.slot_row == slot_data[0], NewSlotFillError.slot_column==slot_data[1]).execute()
        update_slot_fill_error_detail = NewSlotFillErrorDetails.update({NewSlotFillErrorDetails.pack_grid_id : pack_grid_id})\
            .where(NewSlotFillErrorDetails.slot_row == slot_data[0], NewSlotFillErrorDetails.slot_column==slot_data[1]).execute()


    migrate(
        migrator.drop_column(
            OldSlotHeader._meta.db_table,
            OldSlotHeader.slot_row.db_column,
        ),
        migrator.drop_column(
            OldSlotHeader._meta.db_table,
            OldSlotHeader.slot_column.db_column
        ),
        migrator.add_not_null(
            NewSlotHeader._meta.db_table,
            NewSlotHeader.pack_grid_id.db_column
        ),
        migrator.drop_column(
            OldSlotFillError._meta.db_table,
            OldSlotFillError.slot_row.db_column,
        ),
        migrator.drop_column(
            OldSlotFillError._meta.db_table,
            OldSlotFillError.slot_column.db_column
        ),
        migrator.add_not_null(
            NewSlotFillError._meta.db_table,
            NewSlotFillError.pack_grid_id.db_column
        ),
        migrator.drop_column(
            OldSlotFillErrorDetails._meta.db_table,
            OldSlotFillErrorDetails.slot_row.db_column,
        ),
        migrator.drop_column(
            OldSlotFillErrorDetails._meta.db_table,
            OldSlotFillErrorDetails.slot_column.db_column
        ),
        migrator.add_not_null(
            NewSlotFillErrorDetails._meta.db_table,
            NewSlotFillErrorDetails.pack_grid_id.db_column
        )
    )

    print('Tables modified: SlotHeader, SlotFillError, SlotFillErrorDetails')
