from peewee import PrimaryKeyField, IntegerField, CharField, FixedCharField, DateTimeField, DoesNotExist, InternalError
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class PharmacyMaster(BaseModel):
    """
        @class: pharmacy_master.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc:  Get all the pharmacy details which belongs to the
                particular pharmacy_id
        @input - 1
        @output - {"pharmacy_name": "Vibrant Care", "store_phone": "510-381-3344",
            "store_website": "www.rxnsend.com" .. }
    """
    id = PrimaryKeyField()
    system_id = IntegerField(unique=True)
    store_name = CharField(max_length=100)
    store_address = CharField()
    store_phone = FixedCharField(max_length=14)
    store_fax = FixedCharField(max_length=14, null=True)
    store_website = CharField(max_length=50, null=True)
    opening_hours = CharField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pharmacy_master"


    @classmethod
    def db_get(cls, system_id):
        # initialize empty dictionary to store pharmacy details
        # return True if query executes successfully along with the dict of pharmacy details
        try:
            for record in PharmacyMaster.select().dicts().where(PharmacyMaster.system_id == system_id):
                yield record
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            yield None
        except InternalError as e:
            logger.error(e)
            yield None

    @classmethod
    def db_get_pharmacy_data(cls):
        # initialize empty dictionary to store pharmacy details
        # return True if query executes successfully along with the dict of pharmacy details
        try:
            for record in PharmacyMaster.select().dicts():
                yield record
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            yield None
        except InternalError as e:
            logger.error(e)
            yield None
