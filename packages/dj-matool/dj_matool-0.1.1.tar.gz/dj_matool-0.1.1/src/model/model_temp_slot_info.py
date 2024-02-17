from datetime import date
from typing import List, Dict, Any

from peewee import IntegerField, ForeignKeyField, DateField, \
    TimeField, PrimaryKeyField, InternalError, DoesNotExist, \
    DecimalField, FixedCharField, IntegrityError, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_patient_master import PatientMaster
from src.model.model_file_header import FileHeader
from src.model.model_patient_rx import PatientRx

logger = settings.logger


class TempSlotInfo(BaseModel):
    id = PrimaryKeyField()
    file_id = ForeignKeyField(FileHeader)
    patient_id = ForeignKeyField(PatientMaster)
    patient_rx_id = ForeignKeyField(PatientRx)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    hoa_date = DateField()
    hoa_time = TimeField()
    filled_by = FixedCharField(max_length=64)
    fill_start_date = DateField()
    fill_end_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    pharmacy_fill_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "temp_slot_info"

    @classmethod
    def db_get(cls, patient_id, file_id):
        try:
            for record in TempSlotInfo.select().dicts().where(TempSlotInfo.patient_id == patient_id,
                                                              TempSlotInfo.file_id == file_id):
                yield record
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            yield None
        except InternalError as e:
            logger.error(e)
            yield None

    @classmethod
    def db_delete_by_patient_file_ids(cls, patient_id, file_ids):
        try:
            return TempSlotInfo.delete().where(TempSlotInfo.patient_id == patient_id,
                                               TempSlotInfo.file_id << file_ids).execute()
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_file_id_by_pharmacy_fill(cls, pharmacy_fill_id_set):
        try:
            return TempSlotInfo.select(
                TempSlotInfo.pharmacy_fill_id,
                TempSlotInfo.file_id) \
                .where(TempSlotInfo.pharmacy_fill_id << list(pharmacy_fill_id_set))
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_admin_duration(cls, patient_id: int, file_id: int) -> List[Dict[str, Any]]:
        temp_slot_data_list: List[Dict[str, Any]] = []
        try:
            temp_data = TempSlotInfo.select(TempSlotInfo.fill_start_date, TempSlotInfo.fill_end_date).dicts() \
                .where(TempSlotInfo.patient_id == patient_id, TempSlotInfo.file_id == file_id) \
                .group_by(TempSlotInfo.patient_id, TempSlotInfo.file_id)

            for record in temp_data:
                temp_slot_data_list.append(record)
            return temp_slot_data_list

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return []
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_delete_rx_info(cls, patient_id: int, file_ids: List[int], patient_rx_id: int, start_date: date,
                          end_date: date) -> None:
        """
        Deletes the template records from the template_details table for the given patient_id, file_id and
        patient_rx_id and also for the given admin duration specified with start and end date.
        """
        try:
            TempSlotInfo.delete() \
                .where(TempSlotInfo.patient_id == patient_id,
                       TempSlotInfo.file_id << file_ids,
                       TempSlotInfo.patient_rx_id == patient_rx_id,
                       TempSlotInfo.hoa_date >= start_date,
                       TempSlotInfo.hoa_date <= end_date).execute()

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
