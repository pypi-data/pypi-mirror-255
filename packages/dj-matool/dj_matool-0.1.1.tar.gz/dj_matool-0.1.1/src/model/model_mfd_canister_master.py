from peewee import *
from playhouse.shortcuts import case
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_code_master import CodeMaster
from src.model.model_location_master import LocationMaster
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class MfdCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True, related_name='mfd_loc_id')
    canister_type = ForeignKeyField(CodeMaster, default=settings.SIZE_OR_TYPE["MFD"])
    state_status = SmallIntegerField()
    label_print_time = DateTimeField(null=True, default=None)
    erp_product_id = IntegerField(null=True, unique=True)
    company_id = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    home_cart_id = ForeignKeyField(DeviceMaster, null=True)
    fork_detected = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_master"

    @classmethod
    def db_update_canister_id(cls, canister_ids: list, location_ids: list) -> int:
        """
        updates current location of canisters
        :param canister_ids: list
        :param location_ids: list
        :return: int
        """
        try:
            new_seq_tuple = list(tuple(zip(map(str, canister_ids), location_ids)))
            case_sequence = case(MfdCanisterMaster.id, new_seq_tuple)
            logger.info(case_sequence)
            resp = MfdCanisterMaster.update(location_id=case_sequence) \
                .where(MfdCanisterMaster.id.in_(canister_ids)).execute()
            logger.info("mfd_can_id_location_updated_with: " + str(resp) + ' status for canister_ids: ' +
                        str(canister_ids) + ' and location_ids: ' + str(location_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_by_id(cls, canister_id: int, raise_exc: bool = True) -> object:
        """
        returns canister data for given canister id
        :param canister_id: int
        :param raise_exc: bool
        :return: dict
        """
        try:
            return cls.get(cls.id == canister_id)
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            if raise_exc:
                raise
            return None
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def get_home_cart_for_given_locations(cls, location_id_list: list) -> list:
        """
        returns home_cart_id for canisters with their current locations
        :param location_id_list: list
        :return: list
        """
        try:
            trolley_id_list = []
            query = cls.select(cls.home_cart_id).dicts().where(cls.location_id << location_id_list)
            for record in query:
                trolley_id_list.append(record["home_cart_id"])
            return trolley_id_list
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_canister_location_and_fork(cls, canister_ids: list, location_ids: list, fork_detections: list) -> int:
        """
        updates current location of canisters
        :param canister_ids: list
        :param location_ids: list
        :param fork_detections: list
        :return: int
        """
        try:
            new_seq_tuple = list(tuple(zip(map(str, canister_ids), location_ids)))
            fork_new_seq_tuple = list(tuple(zip(map(str, canister_ids), fork_detections)))
            case_sequence = case(MfdCanisterMaster.id, new_seq_tuple)
            fork_case_sequence = case(MfdCanisterMaster.id, fork_new_seq_tuple)
            logger.info(case_sequence)
            resp = MfdCanisterMaster.update(location_id=case_sequence, fork_detected=fork_case_sequence) \
                .where(MfdCanisterMaster.id.in_(canister_ids)).execute()
            logger.info("mfd_can_id_location_updated_with: " + str(resp) + ' status for canister_ids: ' +
                        str(canister_ids) + ' and location_ids: ' + str(location_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_verify_mfd_canister_ids(cls, mfd_canister_ids: list, company_id: int) -> bool:
        """
        Verifies weather the mfd_canister_ids belongs to the given company or not
        :param mfd_canister_ids: list
        :param company_id: int
        :return:
        """
        if not mfd_canister_ids:
            return False
        try:
            canister_count = MfdCanisterMaster.select() \
                .where(MfdCanisterMaster.id << mfd_canister_ids,
                       MfdCanisterMaster.company_id == company_id).count()
            if len(mfd_canister_ids) == canister_count:
                return True
            return False
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_data_by_mfd_canister_id(cls, mfd_canister_ids: list, update_dict: dict) -> bool:
        """
        updates data in mfd_canister_master for given mfd_canister_ids based on update dict
        :param mfd_canister_ids:
        :param update_dict:
        :return:
        """
        try:
            update_status = MfdCanisterMaster.update(**update_dict) \
                .where(MfdCanisterMaster.id << mfd_canister_ids).execute()
            logger.debug('Updated mfd_canister_id: {} with data {} and update_status: {}'
                         .format(mfd_canister_ids, update_dict, update_status))
            return update_status
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_mfd_canister_location_by_mfd_canister_id(cls, mfd_canister_id_list,
                                                                           mfd_canister_location_list) -> bool:
        try:
            new_seq_tuple = list(tuple(zip(map(str, mfd_canister_id_list), map(str, mfd_canister_location_list))))
            case_sequence = case(MfdCanisterMaster.id, new_seq_tuple)
            status = 0
            if mfd_canister_id_list:
                status = cls.update(location_id=case_sequence).where(MfdCanisterMaster.id.in_(mfd_canister_id_list)).execute()
            return status
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
