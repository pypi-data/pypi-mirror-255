from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, InternalError, IntegrityError, fn,
                    DoesNotExist)
from playhouse.shortcuts import case
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from pymysql import DataError
from src.model.model_code_master import CodeMaster
from src.model.model_location_master import LocationMaster
from src.model.model_batch_master import BatchMaster
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class MfdAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, related_name='batch_id')
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster, null=True, related_name='mfd_can_id')
    order_no = IntegerField()
    assigned_to = IntegerField(null=True)
    status_id = ForeignKeyField(CodeMaster, related_name='can_status')
    dest_device_id = ForeignKeyField(DeviceMaster, related_name='robot_id')
    mfs_device_id = ForeignKeyField(DeviceMaster, null=True, related_name='manual_fill_station')
    mfs_location_number = IntegerField(null=True)
    dest_quadrant = IntegerField()
    trolley_location_id = ForeignKeyField(LocationMaster, related_name='trolley_loc_id', null=True)
    dropped_location_id = ForeignKeyField(LocationMaster, null=True, related_name='dropped_loc_id')
    transferred_location_id = ForeignKeyField(LocationMaster, null=True, related_name='transferred_loc_id')
    trolley_seq = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis"

    @classmethod
    def db_update_canister_status(cls, analysis_ids: list, status: int) -> int:
        """
        updates mfd canister status for given analysis_ids
        :param analysis_ids: list
        :param status: int
        :return: int
        """
        try:
            update_status = MfdAnalysis.update(status_id=status,
                                               modified_date=get_current_date_time()) \
                .where(MfdAnalysis.id << analysis_ids).execute()
            logger.info("mfd_can_status_changed_to: " + str(status) + ' for analysis_ids: ' + str(analysis_ids))
            return update_status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_mfs_location(cls, analysis_ids: list, location_ids: list) -> int:
        """
        updates mfs_location number to associate analysis_id with location where canister should be placed and mapped
        to the given analysis id for rfid callback
        :param analysis_ids: list
        :param location_ids: list
        :return: int
        """
        try:
            new_seq_tuple = list(tuple(zip(map(str, analysis_ids), map(str, location_ids))))
            case_sequence = case(MfdAnalysis.id, new_seq_tuple)
            logger.info(case_sequence)
            resp = MfdAnalysis.update(mfs_location_number=case_sequence) \
                .where(MfdAnalysis.id.in_(analysis_ids)).execute()
            logger.info("mfd_can_updated_with: " + str(resp) + ' mfs location for analysis_id: ' + str(analysis_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_canister_id(cls, analysis_ids: list, canister_ids: list) -> int:
        """
        associates canister id to analysis id
        :param analysis_ids: list
        :param canister_ids: list
        :return: int
        """
        try:
            new_seq_tuple = list(tuple(zip(map(str, analysis_ids), canister_ids)))
            case_sequence = case(MfdAnalysis.id, new_seq_tuple)
            logger.info(case_sequence)
            resp = MfdAnalysis.update(mfd_canister_id=case_sequence) \
                .where(MfdAnalysis.id.in_(analysis_ids)).execute()
            logger.info("mfd_can_id_associated_with: " + str(resp) + ' mfs location for analysis_id: ' +
                        str(analysis_ids) + ' canister_ids: ' + str(canister_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_order_number_from_analysis_id(cls, analysis_ids: list) -> dict:
        """
        to obtain analysis data for given analysis_id
        :param analysis_ids: list
        :return:
        """
        try:
            query = cls.select(cls).where(cls.id << analysis_ids).order_by(cls.order_no.desc()).limit(1)

            return query.dicts()

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_dest_location(cls, analysis_ids: list, location_ids: list) -> int:
        """
        updates trolley_location to change the dest location of canister in trolley
        :param analysis_ids: list
        :param location_ids: list
        :return: int
        """
        try:
            new_seq_tuple = list(tuple(zip(map(str, analysis_ids), map(str, location_ids))))
            case_sequence = case(MfdAnalysis.id, new_seq_tuple)
            logger.info(case_sequence)
            resp = MfdAnalysis.update(trolley_location_id=case_sequence) \
                .where(MfdAnalysis.id.in_(analysis_ids)).execute()
            logger.info(
                "mfd_can_updated_with: " + str(resp) + ' trolley location for analysis_id: ' + str(analysis_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_assigned_to(cls, analysis_ids: list, assigned_to: int) -> int:
        """
        updates user assignment to the given analysis ids
        :param analysis_ids: list
        :param assigned_to: int
        :return: int
        """
        try:
            resp = MfdAnalysis.update(assigned_to=assigned_to,
                                      modified_date=get_current_date_time()) \
                .where(MfdAnalysis.id.in_(analysis_ids)).execute()
            logger.info(
                "mfd_can_updated_with: " + str(resp) + ' assigned to for analysis_id: ' + str(analysis_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_transferred_location(cls, analysis_ids: list, location_ids: list) -> int:
        """
        updates robot's location after the trolley canisters transfer to robot is done
        :param analysis_ids: list
        :param location_ids: list
        :return: int
        """
        try:
            new_seq_tuple = list(tuple(zip(map(str, analysis_ids), map(str, location_ids))))
            case_sequence = case(MfdAnalysis.id, new_seq_tuple)
            logger.info(case_sequence)
            resp = MfdAnalysis.update(transferred_location_id=case_sequence) \
                .where(MfdAnalysis.id.in_(analysis_ids)).execute()
            logger.info("mfd_can_updated_with: " + str(resp) + ' transferred_location_id for analysis_id: ' +
                        str(analysis_ids))
            return resp
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_max_order_number(cls) -> int:
        """
        To get max order number from mfd analysis
        @return: int
        """
        try:
            order_no = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no)).scalar()
            return order_no
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_min_analysis_id(cls, batch_id: int, trolley_seq: int) -> int:
        """
        To get max order number from mfd analysis
        @return: int
        """
        min_order_no = None
        try:
            order_no_query = MfdAnalysis.select(MfdAnalysis.order_no).dicts() \
                .where(MfdAnalysis.batch_id == batch_id,
                       MfdAnalysis.trolley_seq == trolley_seq) \
                .order_by(MfdAnalysis.order_no) \
                .limit(1)
            for record in order_no_query:
                min_order_no = record['order_no']
            return min_order_no
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_analysis_data_from_analysis_ids(cls, analysis_ids: list) -> dict:
        """
        to obtain analysis data for given analysis_id
        :param analysis_ids: list
        :return:
        """
        try:
            query = cls.select(cls).where(cls.id << analysis_ids)

            return query.dicts()

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_check_mfd_analysis_by_batch(cls, batch_id: int) -> bool:
        try:
            mfd_query = MfdAnalysis.select().dicts().where(MfdAnalysis.batch_id == batch_id)
            if mfd_query.count() > 0:
                return True
            return False
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_total_mfd_canister_to_be_used_by_batch(cls, batch_id: int) -> bool:
        try:
            mfd_query = MfdAnalysis.select().dicts().where(MfdAnalysis.batch_id == batch_id)
            return mfd_query.count()
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_mfd_analysis_by_status(cls, mfd_analysis_pending_status_ids,
                                                                           mfd_analysis_complete_status_ids,batch_id):
        try:
            new_seq_tuple = list(tuple(zip(map(str, mfd_analysis_pending_status_ids), map(str, mfd_analysis_complete_status_ids))))
            case_sequence = case(MfdAnalysis.status_id, new_seq_tuple)

            mfd_analysis_updated_status = list()
            mfd_analysis_id_list = list()

            subquery = cls.select(cls.id.alias("mfd_analysis_id"),cls.status_id.alias("mfd_analysis_old_status")).dicts()\
                .where(MfdAnalysis.status_id.in_(mfd_analysis_pending_status_ids),
                       MfdAnalysis.batch_id.not_in(batch_id)).order_by(cls.id)

            for record in subquery:
                mfd_analysis_updated_status.append(record)
                mfd_analysis_id_list.append(record["mfd_analysis_id"])

            query = cls.update(status_id=case_sequence).where(MfdAnalysis.status_id.in_(mfd_analysis_pending_status_ids))

            if batch_id:
                query = query.where(MfdAnalysis.batch_id.not_in(batch_id))

            status = query.execute()

            if len(subquery) != 0:
                select_query = cls.select(cls.id.alias("mfd_analysis_id"), cls.status_id.alias("mfd_analysis_new_status")).dicts()\
                .where(MfdAnalysis.id.in_(mfd_analysis_id_list)).order_by(cls.id)

                if select_query:
                    for record,i in zip(select_query, mfd_analysis_updated_status):
                        i["mfd_analysis_new_status"] = record["mfd_analysis_new_status"]

            return status, mfd_analysis_updated_status
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_get_last_order_no_trolley_seq_no_of_given_batch(cls, batch_id: int):
        """
        get query to get last order no. of imported batch
        @param batch_id:
        """
        try:
            mfd_analysis_data = list()
            query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias("last_order_no"),
                                       fn.MAX(MfdAnalysis.trolley_seq).alias("last_trolley_seq")).dicts() \
                .where(MfdAnalysis.batch_id == batch_id)
            for record in query:
                mfd_analysis_data.append(record)

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_first_order_no_trolley_seq_no_of_given_batch(cls, batch_id: int):
        """
        get query to get last order no. of imported batch
        @param batch_id:
        """
        try:
            mfd_analysis_data = list()
            query = MfdAnalysis.select(fn.MIN(MfdAnalysis.order_no).alias("first_order_no"),
                                       fn.MIN(MfdAnalysis.trolley_seq).alias("first_trolley_seq")).dicts() \
                .where(MfdAnalysis.batch_id == batch_id)
            for record in query:
                mfd_analysis_data.append(record)

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_trolley_seq_by_analysis_id(cls, analysis_id, new_trolley_seq):
        try:
            query = cls.update(trolley_seq = new_trolley_seq).where(cls.id << analysis_id).execute()
            return query
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_change_mfd_order_no(cls, case_sequence, mfd_analysis_ids, user_id):
        """
        update order no
        :return:
        """
        try:
            status = cls.update(order_no=case_sequence, modified_date=get_current_date_time(), modified_by=user_id).where(
                cls.id.in_(mfd_analysis_ids)).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_change_trolley_seq(cls, case_sequence, mfd_analysis_ids, user_id):
        """
        update order no
        :return:
        """
        try:
            status = cls.update(trolley_seq=case_sequence, modified_date=get_current_date_time(),
                                modified_by=user_id).where(
                cls.id.in_(mfd_analysis_ids)).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_last_order_no_given_trolley_seq(cls, batch_id, trolley_seq):
        """
        To get max order number and trolley_seq from mfd analysis
        @param batch_id:
        @param trolley_seq:
        @return: list
        """
        in_progress_trolley_seq_order_no_detail = list()
        try:
            order_no_query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias("order_no"),
                                                MfdAnalysis.trolley_seq).dicts() \
                .where(MfdAnalysis.trolley_seq == trolley_seq, MfdAnalysis.batch_id == batch_id)

            for record in order_no_query:
                in_progress_trolley_seq_order_no_detail.append(record)
            return in_progress_trolley_seq_order_no_detail
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_first_order_no_given_trolley_seq(cls, batch_id, trolley_seq):
        """
        To get first order number of given trolley sequence
        @param batch_id:
        @param trolley_seq:
        @return: list
        """
        trolley_seq_order_no_detail = list()
        try:
            order_no_query = MfdAnalysis.select(fn.MIN(MfdAnalysis.order_no).alias("order_no"),
                                                MfdAnalysis.trolley_seq).dicts() \
                .where(MfdAnalysis.trolley_seq == trolley_seq, MfdAnalysis.batch_id == batch_id)

            for record in order_no_query:
                trolley_seq_order_no_detail.append(record)
            return trolley_seq_order_no_detail
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
