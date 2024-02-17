from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, DateTimeField, IntegerField, CharField
from playhouse.migrate import MySQLMigrator, migrate
from playhouse.shortcuts import case

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_code_master import CodeMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_dimention_history import DrugDimensionHistory
from src.model.model_unique_drug import UniqueDrug
from utils.drug_inventory_webservices import get_current_inventory_data

init_db(db, 'database_migration')
migrator = MySQLMigrator(db)


class DrugDimension(BaseModel):
    """
    It contains the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True, related_name='unique_drug_id_id')
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=6, max_digits=10)  # in mm^3
    # approx_volume must be calculated using length*width*depth on every insert and update
    accurate_volume = DecimalField(decimal_places=6, max_digits=10, null=True)  # in mm^3  # provided by user
    shape = ForeignKeyField(CustomDrugShape, null=True, related_name='shape')
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    verification_status_id = ForeignKeyField(CodeMaster, default=settings.DRUG_VERIFICATION_STATUS['pending'], related_name='verification_status')
    verified_by = IntegerField(default=None, null=True)  # verification needs to be done by second pharmacy tech.
    verified_date = DateTimeField(default=None, null=True)
    rejection_note = CharField(default=None, null=True, max_length=1000)
    unit_weight = DecimalField(null=True)
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class DrugDimensionHistory(BaseModel):
    """
    It contains the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    drug_dimension_id = ForeignKeyField(DrugDimension)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=6, max_digits=10)  # in mm^3
    accurate_volume = DecimalField(decimal_places=6, max_digits=10, null=True)  # in mm^3  # provided by user
    shape = ForeignKeyField(CustomDrugShape, null=True, related_name='shape_id')
    created_by = IntegerField(default=1)
    is_manual = IntegerField(default=1)
    unit_weight = DecimalField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    image_name = CharField(null=True, max_length=255)
    verification_status_id = ForeignKeyField(CodeMaster, default=settings.DRUG_VERIFICATION_STATUS['pending'], related_name="verification_status_id_id")
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension_history'


def add_column_unit_weight_in_unique_drug_table():
    try:
        with db.transaction():
            if UniqueDrug.table_exists():
                migrate(migrator.add_column(UniqueDrug._meta.db_table,
                                            UniqueDrug.unit_weight.db_column,
                                            UniqueDrug.unit_weight))
            print("In add_column_unit_weight_in_uniq_drug_table, new column unit_weight added")
    except Exception as e:
        print(e)
        raise e


def add_values_of_unit_weight_from_drug_dimension_to_unique_drug():
    try:
        unique_drug_list = list()
        unit_weight_list = list()
        query = DrugDimension.select(UniqueDrug.id, DrugDimension.unit_weight).dicts() \
                             .join(UniqueDrug, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
                             .where(DrugDimension.unit_weight.is_null(False))
        for drug in query:
            unique_drug_list.append(drug['id'])
            unit_weight_list.append(drug['unit_weight'])

        new_seq_tuple = list(tuple(zip(map(str, unique_drug_list), map(str, unit_weight_list))))
        case_sequence = case(UniqueDrug.id, new_seq_tuple)
        status = UniqueDrug.update(unit_weight=case_sequence).where(UniqueDrug.id.in_(unique_drug_list)).execute()
        print("Added values of unit_weight from drug_dimension to drug_dimension_history.")
        print("status", status)
        return status

    except Exception as e:
        print(e)
        raise e


def drop_column_unit_weight_from_drug_dimension_and_drug_dimension_history():
    try:
        if DrugDimension.table_exists():
            migrate(migrator.drop_column(DrugDimension._meta.db_table,
                                         DrugDimension.unit_weight.db_column))

        if DrugDimensionHistory.table_exists():
            migrate(migrator.drop_column(DrugDimensionHistory._meta.db_table,
                                         DrugDimensionHistory.unit_weight.db_column))

        print("Dropped tables drug_dimension and drug_dimension_history.")
    except Exception as e:
        print(e)
        raise e


def migration_for_adding_unique_weight_column_in_unique_drug_and_removing_from_drug_dimension():
    add_column_unit_weight_in_unique_drug_table()
    add_values_of_unit_weight_from_drug_dimension_to_unique_drug()
    drop_column_unit_weight_from_drug_dimension_and_drug_dimension_history()


if __name__ == "__main__":
    migration_for_adding_unique_weight_column_in_unique_drug_and_removing_from_drug_dimension()
