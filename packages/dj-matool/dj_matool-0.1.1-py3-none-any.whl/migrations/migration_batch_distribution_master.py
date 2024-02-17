from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings

class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    status_id = IntegerField()


    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"

def migrate_facility_distribution_master():
    init_db(db, 'database_t1')

    migrator = MySQLMigrator(db)
    db.create_tables([FacilityDistributionMaster], safe=True)
    print("Tables created: FacilityDistributionMaster")


if __name__ == "__main__":
    migrate_facility_distribution_master()