from typing import Optional, List, Tuple, Dict, Any

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import DataError, DoesNotExist, SmallIntegerField, \
    IntegerField, CharField
from src.model.model_code_master import CodeMaster
from peewee import ForeignKeyField, DateTimeField, PrimaryKeyField, InternalError, IntegrityError

logger = settings.logger


class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    status_id = ForeignKeyField(CodeMaster)
    req_dept_list = CharField(null=True, default=None)
    ack_dept_list = CharField(null=True, default=None)
    ordering_bypass = IntegerField(null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"

    @classmethod
    def db_update_or_create_bdm(cls, user_id, status_id, company_id):
        """
        If record exists then updates it or creates new record
        @param user_id:
        @param status_id:
        @param company_id:
        @return:
        """
        try:
            update_dict = {"modified_by": user_id, "modified_date": get_current_date_time(), "created_by": user_id}
            record, created = FacilityDistributionMaster.get_or_create(defaults=update_dict, status_id=status_id,
                                                                       company_id=company_id)
            print("rec, cre", record.id)
            if not created:
                update_dict["created_by"] = record.created_by
                FacilityDistributionMaster.update(**update_dict).where(
                    FacilityDistributionMaster.id == record.id).execute()

            return record.id
        except InternalError as e:
            raise InternalError(e)

    @classmethod
    def db_validate_company_bach_distribution_id(cls, company_id: int, facility_dist_id: int):
        company_id = int(company_id)
        try:
            batch_distribution = FacilityDistributionMaster.get(id=facility_dist_id)
            if company_id == batch_distribution.company_id:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_update_facility_distribution_status(cls, company_id, facility_distribution_id):
        company_id = int(company_id)
        try:
            for each_id in facility_distribution_id:
                FacilityDistributionMaster.update(status_id=settings.BATCH_DISTRIBUTION_DONE) \
                    .where(FacilityDistributionMaster.id == each_id,
                           FacilityDistributionMaster.company_id == company_id).execute()
            return True
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_get_facility_distribution_status(cls, company_id: int, facility_dist_id: int) -> int:
        try:
            for data in cls.select().dicts().where(cls.id == facility_dist_id, cls.company_id == company_id):
                return data["status_id"]
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            return 0

    @classmethod
    def db_get_dept_data_by_id(cls, facility_dist_id: int) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """
        Fetch the record by the facility_dist_id and company_id.
        """
        try:
            for data in cls.select().dicts().where(cls.id == facility_dist_id):
                req_dept_list: Optional[List[str]] = data["req_dept_list"].split(",") if data["req_dept_list"] else None
                ack_dept_list: Optional[List[str]] = data["ack_dept_list"].split(",") if data["ack_dept_list"] else None

                return req_dept_list, ack_dept_list

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_by_id(cls, update_dict: Dict[str, Any], facility_dist_id: int) -> bool:
        """
        Updates the db for the given facility_dist_id.
        """
        try:
            cls.update(**update_dict).where(cls.id == facility_dist_id).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
