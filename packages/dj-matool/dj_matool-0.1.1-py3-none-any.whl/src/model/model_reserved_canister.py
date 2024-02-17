from typing import List, Any

from peewee import ForeignKeyField, PrimaryKeyField, InternalError, IntegrityError
from sqlalchemy import case

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_batch_master import BatchMaster

from src.model.model_canister_master import CanisterMaster
logger = settings.logger


class ReservedCanister(BaseModel):
    """
        Stores canisters used in batch.
        - This Model should be used to determine if canister is available
        for canister_recommendation module.
        - Delete to free canister for other batch.
    """
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, null=True)
    canister_id = ForeignKeyField(CanisterMaster, related_name="canister_id")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "reserved_canister"

    @classmethod
    def db_validate_canisters(cls, canisters) -> bool:
        """
        Validates canisters, should not be reserved.
        If any canister is reserved then False, True otherwise
        :param canisters:
        :return:
        """
        try:
            canisters = list(set(canisters))
            if canisters:
                query = cls.select(cls.id) \
                    .where(cls.canister_id << canisters)
                if query.count() == 0:
                    return True
                else:
                    return False
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_save(cls, batch_canisters):
        """
        Takes dict containing key as batch_id and values as canisters ids. Stores this records in database,
        :param batch_canisters: dict
        :return:
        """
        try:
            record_list = list()
            # flatten and create list of dict to insert
            for batch_id, canisters in batch_canisters.items():
                for canister in canisters:
                    record_list.append({
                        'batch_id': batch_id,
                        'canister_id': canister
                    })
            if record_list:
                ReservedCanister.insert_many(record_list).execute()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_remove_reserved_canister(cls, canister_ids: list, batch_id: int = None) -> bool:
        """
        Removes unwanted canisters from reserved canisters
        :param batch_id:
        :param canister_ids:
        :return:
        """
        try:
            if batch_id:
                status = ReservedCanister.delete() \
                    .where(ReservedCanister.canister_id << canister_ids,
                           ReservedCanister.batch_id == batch_id).execute()
            else:
                status = ReservedCanister.delete().where(ReservedCanister.canister_id.in_(canister_ids)).execute()
            logger.info(
                'db_remove_reserved_canisters_with_status {} for canister_ids {}: '.format(status, canister_ids))
            return status

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_replace_canister_list(cls, batch_id, canister_list=None, alt_canister_list=None, case_sequence=None) -> bool:
        """
        Replaces canister_list to it's respective alt_canister_list
        :param batch_id:
        :param canister_list:
        :param alt_canister_list:
        :param case_sequence:
        :return:
        """
        try:
            if not case_sequence:
                if len(canister_list) != len(alt_canister_list):
                    raise ValueError('Length of canister_list and alt_canister_list should be same ')
                new_seq_tuple = list(tuple(zip(canister_list, alt_canister_list)))
                case_sequence = case(ReservedCanister.canister_id, new_seq_tuple)

            status = ReservedCanister.update(canister_id=case_sequence) \
                .where(ReservedCanister.batch_id == batch_id,
                       ReservedCanister.canister_id << canister_list).execute()
            print('replace_result', status)
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_replace_canister(cls, canister_id: int or None, alt_canister_id: int, canister_ids: list = None) -> bool:
        """
            Replace Canister for given batch_id.
            alt_canister_id will be replaced for canister_id
            :param batch_id:
            :param canister_id:
            :param alt_canister_id:
            :param canister_ids:
            :return:
        """
        try:
            clauses = []
            if canister_ids:
                clauses.append((ReservedCanister.canister_id << canister_ids))
            else:
                clauses.append((ReservedCanister.canister_id == canister_id))

            query = ReservedCanister.update(canister_id=alt_canister_id) \
                .where(*clauses)
            status = query.execute()
            return status
            # logger.info('Replace Reserved Canister Update Status: {} for canister_id: {} '
            #             'and alt_canister_id: {}'.format(
            #     status, canister_id, alt_canister_id
            # ))
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_reserved_canister(cls, company_id, batch_id=None, skip_canisters=None):
        """ Returns query to get reserved canister ids """

        clauses = [CanisterMaster.company_id == company_id,
                   ]
        try:
            logger.info("In db_get_reserved_canister: company_id: {}, batch_id: {}, skip_canister: {}".format(company_id, batch_id, skip_canisters))
            if batch_id:
                clauses.append((ReservedCanister.batch_id == batch_id))
            if skip_canisters:
                clauses.append(ReservedCanister.canister_id.not_in(skip_canisters))
            query = cls.select(cls.canister_id).dicts() \
                .join(CanisterMaster, on=CanisterMaster.id == ReservedCanister.canister_id) \
                .where(*clauses)
            canister_list = [record['canister_id'] for record in query]
            logger.info("In db_get_reserved_canister: canister_list: {}".format(canister_list))
            return canister_list
        except (InternalError, IntegrityError) as e:
            logger.error("Error in db_get_reserved_canister {}".format(e))
            raise e

    @classmethod
    def db_get_reserved_canister_query(cls, company_id, skip_canisters=None) -> List[Any]:
        """ Returns query to get reserved canister ids """
        clauses = [CanisterMaster.company_id == company_id,
                   ]
        if skip_canisters:
            clauses.append(ReservedCanister.canister_id.not_in(skip_canisters))
        query = cls.select(cls.canister_id) \
            .join(CanisterMaster, on=CanisterMaster.id == ReservedCanister.canister_id) \
            .where(*clauses)
        return query
