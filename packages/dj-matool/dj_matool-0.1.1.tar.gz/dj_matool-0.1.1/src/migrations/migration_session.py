from peewee import *

import settings
from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class SessionModuleMaster(BaseModel):
    id = PrimaryKeyField()
    session_module_type_id = ForeignKeyField(GroupMaster)
    screen_sequence = IntegerField()
    screen_name = CharField(max_length=100)
    screen_interaction = BooleanField()
    max_idle_time = IntegerField()
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session_module_master"


class SessionModuleMeta(BaseModel):
    id = PrimaryKeyField()
    session_module_id = ForeignKeyField(SessionModuleMaster)
    task_name = CharField(max_length=100)
    time_per_unit = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session_module_meta"


class Session(BaseModel):
    id = PrimaryKeyField()
    session_module_id = ForeignKeyField(SessionModuleMaster)
    identifier_key = ForeignKeyField(CodeMaster)
    identifier_value = IntegerField(null=True)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    active_time = IntegerField(default=0)
    created_datetime = DateTimeField()
    modified_datetime = DateTimeField()
    user_id = IntegerField()
    system_id = IntegerField(null=True)
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session"


class SessionMeta(BaseModel):
    id = PrimaryKeyField()
    session_id = ForeignKeyField(Session)
    session_module_meta_id = ForeignKeyField(SessionModuleMeta)
    value = CharField(max_length=100)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session_meta"


def create_session_tables():
    db.create_tables([SessionModuleMaster, SessionModuleMeta, SessionMeta, Session], safe=True)


def insert_data_in_session_tables(company_id: int):
    Company_id = company_id
    if SessionModuleMaster.table_exists():
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_DDT_SCREEN,
                                   session_module_type_id=constants.DRUG_DISPENSING_TEMPLATES_MODULE, screen_sequence=1,
                                   screen_name='DDT Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_SELECT_FACILITY_SCREEN,
                                   session_module_type_id=constants.BATCH_SCHEDULING_MODULE,
                                   screen_sequence=1, screen_name='Select Facility '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_SELECT_SYSTEMS_SCREEN,
                                   session_module_type_id=constants.BATCH_SCHEDULING_MODULE,
                                   screen_sequence=2, screen_name='Select Systems '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_ALTERNATE_DRUG_SCREEN,
                                   session_module_type_id=constants.BATCH_SCHEDULING_MODULE,
                                   screen_sequence=3, screen_name='Alternate Drug '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_OVERLOAD_PACK_SCREEN,
                                   session_module_type_id=constants.BATCH_SCHEDULING_MODULE,
                                   screen_sequence=4, screen_name='Overload Packs '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_RECOMMEND_DISTRIBUTION_SCREEN,
                                   session_module_type_id=constants.BATCH_SCHEDULING_MODULE,
                                   screen_sequence=5, screen_name='Recommend '
                                                                  'Distribution '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_SCHEDULED_BATCH_SCREEN,
                                   session_module_type_id=constants.PACK_PRE_PROCESSING_MODULE,
                                   screen_sequence=1, screen_name='Scheduled Batch '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_RECOMMEND_ALTERNATE_DRUG_SCREEN,
                                   session_module_type_id=constants.PACK_PRE_PROCESSING_MODULE,
                                   screen_sequence=2, screen_name='Recommend '
                                                                  'Alternate Drug '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_CANISTER_RECOMMENDATION_SCREEN,
                                   session_module_type_id=constants.PACK_PRE_PROCESSING_MODULE,
                                   screen_sequence=3, screen_name='Canister '
                                                                  'Recommendation '
                                                                  'Screen',
                                   screen_interaction=False, max_idle_time=20, company_id=Company_id).execute()
        SessionModuleMaster.insert(id=constants.MODULE_TYPE_IMPORT_BATCH_SCREEN,
                                   session_module_type_id=constants.PACK_PRE_PROCESSING_MODULE,
                                   screen_sequence=4, screen_name='Import Batch '
                                                                  'Screen',
                                   screen_interaction=True, max_idle_time=20, company_id=Company_id).execute()
    if SessionModuleMeta.table_exists():
        SessionModuleMeta.insert(id=constants.MODULE_META_SYSTEM_SELECTION,
                                 session_module_id=constants.MODULE_TYPE_SELECT_SYSTEMS_SCREEN,
                                 task_name='System Selection', time_per_unit=1).execute()
        SessionModuleMeta.insert(id=constants.MODULE_META_ALTERNATE_DRUG_SELECTION_AND_DESELECTION,
                                 session_module_id=constants.MODULE_TYPE_ALTERNATE_DRUG_SCREEN,
                                 task_name='Alternate Drug Selection/Deselection',
                                 time_per_unit=5).execute()
        SessionModuleMeta.insert(id=constants.MODULE_META_USER_SELECTION_AND_SYSTEM_SELECTION,
                                 session_module_id=constants.MODULE_TYPE_OVERLOAD_PACK_SCREEN,
                                 task_name='User Selection & System Selection',
                                 time_per_unit=10).execute()
        SessionModuleMeta.insert(id=constants.MODULE_META_ALTERNATE_DRUG_MODIFICATION,
                                 session_module_id=constants.MODULE_TYPE_RECOMMEND_ALTERNATE_DRUG_SCREEN,
                                 task_name='Alternate Drug Modification',
                                 time_per_unit=5).execute()
        SessionModuleMeta.insert(id=constants.MODULE_META_CANISTER_TRANSFERS,
                                 session_module_id=constants.MODULE_TYPE_CANISTER_RECOMMENDATION_SCREEN,
                                 task_name='Canister Transfers',
                                 time_per_unit=60).execute()
        SessionModuleMeta.insert(id=constants.MODULE_META_USER_SELECTION_FULLY_MANUAL_PACKS,
                                 session_module_id=constants.MODULE_TYPE_IMPORT_BATCH_SCREEN,
                                 task_name='User Selection for Fully Manual Packs',
                                 time_per_unit=2).execute()
        SessionModuleMeta.insert(id=constants.MODULE_META_CANISTER_TRANSFER_MISPLACED_CANISTER,
                                 session_module_id=constants.MODULE_TYPE_IMPORT_BATCH_SCREEN,
                                 task_name='Canister Transfer of Misplaced Canisters',
                                 time_per_unit=60).execute()
        print("Insertion in SessionModuleMaster and SessionModuleMeta completed.")

    print('Table(s) Created: SessionModuleMaster, SessionModuleMeta, Session, SessionMeta')


def migrate_session(company_id):
    init_db(db, "database_migration")
    create_session_tables()
    insert_data_in_session_tables(company_id=company_id)


if __name__=='__main__':
    migrate_session(company_id=3)