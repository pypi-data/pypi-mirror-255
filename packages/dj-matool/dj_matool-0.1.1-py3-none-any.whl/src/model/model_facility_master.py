import functools
import operator

from peewee import PrimaryKeyField, IntegerField, CharField, FixedCharField, BooleanField, DateTimeField, DataError, \
    IntegrityError, InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time


logger = settings.logger


class FacilityMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    pharmacy_facility_id = IntegerField()
    facility_name = CharField(max_length=40)
    address1 = CharField(null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pharmacy_facility_id', 'company_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_master"

    @classmethod
    def db_update_or_create(cls, data, pharmacy_facility_id, company_id, add_fields=None, remove_fields=None,
                            fn_transform=None, fn_validate=None, default_data_dict=None):
        """Takes data from the file and updates the data if exists else creates new record.

                Args:
                    data (dict): The record dict to be inserted in table.
                    pharmacy_facility_id: Value against which record will be identified uniquely.
                    company_id: The id of the Company
                    add_fields (optional argument) (dict): The additional data to be added to record dict.
                    remove_fields (optional argument) (dict): The data to be removed from record dict.
                    fn_transform (optional argument) (dict): The transformation rules if any for the record.
                    fn_validate (optional argument) (dict): The validation rules if any for the record dict.
                    default_data_dict (optional argument) (boolean): The default data to be added along the record.

                Returns:
                   Model.Record : Returns the record containing data.

                Raises:
                    IntegrityError: If the record with the provided primary key already exists
                    InternalError: If the record to be inserted does not have have valid fields.

                Examples:
                    >>> create_record([], [])
                    [0, 1, 2, 3]

        """
        if default_data_dict:
            data.update(default_data_dict)

        # List of fields to be removed from data dictionary
        if remove_fields:
            for item in remove_fields:
                data.pop(item, 0)

        # List of additional fields to be added to data dictionary
        if add_fields:
            data.update(add_fields)

        try:
            record, created = FacilityMaster.get_or_create(
                pharmacy_facility_id=pharmacy_facility_id,
                company_id=company_id,
                defaults=data
            )
            if not created:
                FacilityMaster.update(**data). \
                    where(FacilityMaster.pharmacy_facility_id == pharmacy_facility_id,
                          FacilityMaster.company_id == company_id).execute()

        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)
        return record