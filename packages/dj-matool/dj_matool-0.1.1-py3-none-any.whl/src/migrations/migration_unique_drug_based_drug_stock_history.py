from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *
from dosepack.utilities.utils import get_current_date_time
from src.service.pack import op_null_equal
import settings
from model.model_init import init_db
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster


class DrugStockHistory(BaseModel):
    id = PrimaryKeyField()
    drug_master_id = ForeignKeyField(DrugMaster)
    unique_drug_id = ForeignKeyField(UniqueDrug, null=True, related_name='drug_stock_history_unique_drug_id')
    is_in_stock = SmallIntegerField(null=True)
    is_active = BooleanField(default=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_stock_history"


def add_column_unique_drug_in_drug_stock_history():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if DrugStockHistory.table_exists():
            # Add column unique_drug_id
            migrate(
                migrator.add_column(DrugStockHistory._meta.db_table,
                                    DrugStockHistory.unique_drug_id.db_column,
                                    DrugStockHistory.unique_drug_id)
            )
            print("unique_drug_id added in drug_stock_history")

            # sync drugmaster table with unique_drug table
            add_data_unique_drug()
            print("data inserted in unique_drug")

            # update data in drug stock history
            update_data()
            print("data updated in drug stock history")

            migrate(migrator.drop_column(DrugStockHistory._meta.db_table,
                                         DrugStockHistory.drug_master_id.db_column))
            print("dropped column drug_master_id from table drug stock history")

            migrate(migrator.add_not_null(DrugStockHistory._meta.db_table,
                                          DrugStockHistory.unique_drug_id.db_column))
            print("Add not null constraint for unique_drug_id column in drug stock history")
    except Exception as e:
        print(e)
        raise


def add_data_unique_drug():
    final_list = []
    try:
        """
            Fetch drug id based on formatted_ndc & txt and is not available in unique_drug table
        """
        query = DrugMaster.select(fn.MIN(DrugMaster.id).alias('drug_master_id'),
                                  DrugMaster.formatted_ndc, DrugMaster.txr) \
            .join(UniqueDrug, JOIN_LEFT_OUTER,
                  on=((fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr))
                      & (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc))) \
            .where(UniqueDrug.id.is_null(True)).group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        print(query)
        for record in query.dicts():
            print(record["drug_master_id"])
            data = {"drug_id": record["drug_master_id"], "formatted_ndc": record["formatted_ndc"], "txr": record["txr"]}
            final_list.append(data)
        """
            insert record of drug_id in unique_drug
        """
        if final_list:
            status = UniqueDrug.insert_many(final_list).execute()
            print(status)

    except Exception as e:
        print(e)
        raise


def update_data():
    try:
        """
            Fetch Unique_drud_id for Drug_master_id Based on formatted_ndc & txt
        """
        query = DrugStockHistory.select(UniqueDrug.id.alias('unique_drug_id'),
                                        UniqueDrug.formatted_ndc,
                                        UniqueDrug.txr,
                                        DrugMaster.id) \
            .join(DrugMaster, on=DrugStockHistory.drug_master_id == DrugMaster.id) \
            .join(UniqueDrug, on=((fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) == fn.IF(
            UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                  (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)))
        """
            Update Unique_drug_id for Drug_master_id
        """
        for record in query.dicts():
            DrugStockHistory.update(unique_drug_id=record["unique_drug_id"]).where(
                DrugStockHistory.drug_master_id == record["id"]).execute()

        sub_query = DrugStockHistory.select(DrugStockHistory.unique_drug_id.alias('unique_drug_id'),
                                            fn.Count(DrugStockHistory.id).alias('count'),
                                            fn.MAX(DrugStockHistory.created_date).alias('created_date')). \
            where(DrugStockHistory.is_active == 1) \
            .group_by(DrugStockHistory.unique_drug_id). \
            having((fn.Count(DrugStockHistory.id)) > 1).alias('sub_query')

        query = DrugStockHistory.select(DrugStockHistory.id, DrugStockHistory.unique_drug_id.alias('unique_drug_id')).dicts()\
            .join(sub_query, on=(sub_query.c.unique_drug_id == DrugStockHistory.unique_drug_id))\
            .where(sub_query.c.created_date == DrugStockHistory.created_date)
        for record in query:
            print(record)
            print(record["id"], record["unique_drug_id"])
            DrugStockHistory.update(is_active=0) \
                .where(DrugStockHistory.id != record['id'],
                       DrugStockHistory.unique_drug_id == record["unique_drug_id"]).execute()
    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    add_column_unique_drug_in_drug_stock_history()
