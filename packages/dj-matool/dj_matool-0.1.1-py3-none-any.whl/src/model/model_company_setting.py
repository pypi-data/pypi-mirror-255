from typing import Optional

from peewee import (PrimaryKeyField, IntegerField, CharField, DateTimeField, InternalError,
                    IntegrityError, DataError)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants

logger = settings.logger


class CompanySetting(BaseModel):
    """ stores setting for a company """
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    # Constant for template_settings
    SLOT_VOLUME_THRESHOLD_MARK = 'SLOT_VOLUME_THRESHOLD_MARK'
    SPLIT_STORE_SEPARATE = 'SPLIT_STORE_SEPARATE'
    VOLUME_BASED_TEMPLATE_SPLIT = 'VOLUME_BASED_TEMPLATE_SPLIT'
    COUNT_BASED_TEMPLATE_SPLIT = 'COUNT_BASED_TEMPLATE_SPLIT'
    TEMPLATE_SPLIT_COUNT_THRESHOLD = 'TEMPLATE_SPLIT_COUNT_THRESHOLD'
    TEMPLATE_SPLIT_COUNT_THRESHOLD_UNIT = 'TEMPLATE_SPLIT_COUNT_THRESHOLD_UNIT'
    SLOT_COUNT_THRESHOLD = 'SLOT_COUNT_THRESHOLD'
    TEMPLATE_AUTO_SAVE = 'TEMPLATE_AUTO_SAVE'
    MAX_SLOT_VOLUME_THRESHOLD_MARK = 'MAX_SLOT_VOLUME_THRESHOLD_MARK'
    MANUAL_PER_DAY_HOURS = "MANUAL_PER_DAY_HOURS"
    MANUAL_PER_HOUR = "MANUAL_PER_HOUR"
    MANUAL_SUNDAY_HOURS = "MANUAL_SUNDAY_HOURS"
    MANUAL_SATURDAY_HOURS = "MANUAL_SATURDAY_HOURS"
    MANUAL_USER_COUNT = "MANUAL_USER_COUNT"

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )

    @classmethod
    def db_get_by_company_id(cls, company_id):
        """
        To obtain data from company_settings table
        @param company_id:int
        @return: dict
        """
        company_settings: dict = dict()
        try:
            for record in CompanySetting.select(CompanySetting.name, CompanySetting.value).dicts() \
                    .where(CompanySetting.company_id == company_id):
                company_settings[record["name"]] = record["value"]
            return company_settings

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_ips_communication_settings(cls, company_id):
        """
        Returns required settings for ips communication
        :param company_id:
        :return: dict
        """
        setting_names = settings.IPS_COMMUNICATION_SETTINGS
        ips_communication_settings = {}
        try:
            query = CompanySetting.select(
                CompanySetting.name,
                CompanySetting.value
            ).where(CompanySetting.company_id == company_id,
                    CompanySetting.name << setting_names)
            for record in query.dicts():
                ips_communication_settings[record["name"]] = record["value"]
            return ips_communication_settings

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_split_settings(cls, company_id, max_count_threshold: Optional[int] = None):
        """
        Returns template settings unless there is no default setting to use
        :param company_id: int
        :param max_count_threshold: int
        :return: dict
        """
        template_settings = {}
        try:
            template_setting_converter_and_default = {
                # dict to maintain type and default of template settings
                cls.SLOT_VOLUME_THRESHOLD_MARK: (float, 0.58),
                cls.SPLIT_STORE_SEPARATE: (int, 1),
                cls.VOLUME_BASED_TEMPLATE_SPLIT: (int, 1),
                cls.COUNT_BASED_TEMPLATE_SPLIT: (int, 0),
                cls.TEMPLATE_SPLIT_COUNT_THRESHOLD: (int, constants.TEMPLATE_SPLIT_COUNT_THRESHOLD),
                cls.TEMPLATE_SPLIT_COUNT_THRESHOLD_UNIT: (int, constants.TEMPLATE_SPLIT_COUNT_THRESHOLD_UNIT),
                cls.SLOT_COUNT_THRESHOLD: (int, constants.TEMPLATE_SPLIT_COUNT_THRESHOLD),
                cls.TEMPLATE_AUTO_SAVE: (int, 1),
                cls.MAX_SLOT_VOLUME_THRESHOLD_MARK: (float, 0.72)
            }
            query = cls.select(cls.name, cls.value) \
                .where(cls.company_id == company_id,
                       cls.name << list(template_setting_converter_and_default.keys()))
            for record in query.dicts():
                template_settings[record["name"]] = record["value"]
            for name, val in template_setting_converter_and_default.items():
                if template_settings.get(name, None) is None:
                    if val[1] is not None:
                        template_settings[name] = template_setting_converter_and_default[name][1]
                else:
                    # convert to python data types if setting is required
                    template_settings[name] = val[0](template_settings[name])

            if max_count_threshold:
                template_settings[cls.TEMPLATE_SPLIT_COUNT_THRESHOLD] = constants.MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD
                template_settings[cls.SLOT_COUNT_THRESHOLD] = constants.MAX_SLOT_COUNT_THRESHOLD

            return template_settings
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_company_setting_data_by_company_id(cls, company_id):
        """
        To obtain data from company_settings table by company_id
        @param company_id:int
        @return: dict
        """
        try:
            query = CompanySetting.select(
                CompanySetting.id,
                CompanySetting.company_id,
                CompanySetting.name,
                CompanySetting.value,
            ).where(CompanySetting.company_id == company_id)
            return query

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_company_setting_by_company_id(cls, update_dict, company_id, name) -> bool:
        """
        update system setting by company_id in table
        """
        try:
            status = cls.update(**update_dict).where(cls.company_id == company_id, cls.name == name).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
