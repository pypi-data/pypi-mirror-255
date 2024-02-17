import os
import sys

from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, \
    InternalError, IntegrityError, DataError, fn, DoesNotExist
import settings
from dosepack.base_model.base_model import BaseModel
from src import constants
from src.model.model_pack_details import PackDetails
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


class PackFillErrorV2(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, null=True)
    pack_id = ForeignKeyField(PackDetails)
    note = CharField(null=True, max_length=1000)  # note provided by user for any filling error
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('unique_drug_id', 'pack_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_fill_error_v2"

    @classmethod
    def db_update_or_create(cls, unique_drug_id, pack_id, data):
        """
        Updates error for pack_rx_id if present otherwise creates entry with given data
        @param unique_drug_id:
        @param pack_id:
        @param data:
        @return: PackFillError, bool
        """
        try:
            record, created = PackFillErrorV2.get_or_create(unique_drug_id=unique_drug_id, pack_id=pack_id,
                                                            defaults=data)
            if not created:
                data.pop('created_by', None)
                data.pop('created_date', None)
                PackFillErrorV2.update(**data).where(PackFillErrorV2.id == record.id).execute()

        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)
        return record, created

    @classmethod
    def db_delete_pack_fill_errors_data(cls, delete_pack_fill_error_ids) -> bool:
        """
        delete pack fill errors data by id
        @param delete_pack_fill_error_ids:
        """
        try:
            status = PackFillErrorV2.delete().where(PackFillErrorV2.id << delete_pack_fill_error_ids).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_get_pack_fill_error_data(cls, id: int):
        """
        delete pack fill errors data by id
        @param id:
        """
        try:
            data = PackFillErrorV2.get(id=id)
            return data
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_error_pack_count_by_date(cls, from_date, to_date, offset):
        """
            get error pack count by date
        """
        error_pack_count_unit = dict()
        error_pack_count_multi = dict()
        try:
            created_date = fn.DATE(fn.CONVERT_TZ(PackFillErrorV2.created_date, settings.TZ_UTC, offset))

            error_unit_pack_count_query = PackFillErrorV2.select(
                fn.COUNT(PackFillErrorV2.pack_id).alias('pack_count'), created_date.alias('created_date')).dicts() \
                .join(PackDetails, on=PackDetails.id == PackFillErrorV2.pack_id) \
                .where(created_date.between(from_date, to_date),
                       ((PackDetails.pack_type == constants.WEEKLY_UNITDOSE_PACK) |
                       (PackDetails.dosage_type == settings.DOSAGE_TYPE_UNIT))) \
                .group_by(created_date)

            print("In db_get_error_pack_count_by_date: error_unit_pack_count_query", str(error_unit_pack_count_query))
            for record in error_unit_pack_count_query:
                error_pack_count_unit[record['created_date']] = record['pack_count']

            error_multi_pack_count_query = PackFillErrorV2.select(
                fn.COUNT(PackFillErrorV2.pack_id).alias('pack_count'),
                created_date.alias('created_date')).dicts() \
                .join(PackDetails, on=PackDetails.id == PackFillErrorV2.pack_id) \
                .where(created_date.between(from_date, to_date),
                       PackDetails.pack_type != constants.WEEKLY_UNITDOSE_PACK,
                       PackDetails.dosage_type == settings.DOSAGE_TYPE_MULTI) \
                .group_by(created_date)
            print("In db_get_error_pack_count_by_date: error_multi_pack_count_query", str(error_multi_pack_count_query))

            for record in error_multi_pack_count_query:
                error_pack_count_multi[record['created_date']] = record['pack_count']

            return error_pack_count_unit, error_pack_count_multi

        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error("error in db_get_filled_pack_count_by_date {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in db_get_filled_pack_count_by_date: exc_type - {exc_type}, filename - {filename}, line - "
                f"{exc_tb.tb_lineno}")
            raise e
        except DoesNotExist:
            logger.info('No packs filled on ' + str(from_date))
            return error_pack_count_unit, error_pack_count_multi
