import logging
from itertools import cycle
from typing import Dict, Any

from peewee import MySQLDatabase
from peewee import IntegrityError, InternalError, DoesNotExist, OperationalError
from sqlalchemy.exc import OperationalError as sql_operaional
from sys import getsizeof
from peewee import OperationalError as peewee_operational

from src.dao.ext_file_dao import update_couch_db_pending_template_count, get_template_ext_data
from src.dao.ext_change_rx_couchdb_dao import update_notifications_couch_db_green_status
from src.dao.misc_dao import get_company_setting_by_company_id
from src.model.model_template_master import TemplateMaster
from src.dao.pack_dao import db_max_assign_order_no_manual_packs, db_update_slot_details_drug_with_old_packs
from src.redis_controller import update_pending_template_data_in_redisdb
from .celery import celery_app
from celery.signals import task_postrun
import ast
import settings
from dosepack.utilities.manage_db_connection import after_request_handler

from src.model.model_canister_master import CanisterMaster


from src.service.generate_packs import GeneratePack, set_unit_dosage_flag, bulk_pack_ids, \
    db_process_new_packs_change_rx
from src.service.pack import db_update_rx_changed_packs_manual_count
from src.exceptions import PackGenerationException, PharmacyRxFileGenerationException, \
    PharmacySlotFileGenerationException, PharmacySoftwareResponseException, PharmacySoftwareCommunicationException, \
    RedisConnectionException
from src.service.facility_schedule import update_delivery_date
from src.service.misc import update_queue_count
from dosepack.base_model.base_model import db as dpws_db
from dosepack.local.lang_us_en import err


logger = logging.getLogger("root")

DEFAULT_MAX_RETRY_COUNT = 3


@celery_app.task
def test_task_1(name):
    return 'Hello {}'.format(name)


def error_response_pack_generation(file_id, patient_id, msg, company_id, template_id):
    display_list = list()
    template_dict: Dict[str, Any] = {}
    logger.info("error_response_pack_generation" + str(msg))
    logger.info("sizeOf " + str(getsizeof(msg)))
    try:
        template_dict = get_template_ext_data(template_id=template_id)
        if template_dict:
            update_dict = {"status": template_dict["status"]}
        else:
            update_dict = {"status": settings.PENDING_TEMPLATE_STATUS}

        TemplateMaster.db_update_status_with_id(template_id, update_dict)
    except (InternalError, IntegrityError, OperationalError, sql_operaional, peewee_operational) as e:
        logger.info("known_execption in error_response_pack_generation" + str(e))
        logger.info(e)
        return '{} ##True'.format(err[2001])
    except Exception as e:
        logger.info("execption in error_response_pack_generation" + str(e))
        return '{} ##True'.format(str(e))
    return '{} ##True'.format(msg)


# def update_couch_db_status(msg, company_id):
#     try:
#         status, _ = update_queue_count(settings.CONST_TEMPLATE_MASTER_DOC_ID, 1, None, company_id,
#                            settings.TASK_OPERATION['Remove'], update_timestamp=True, raise_exc=True)
#     except Exception as e:
#         data = update_couch_db_status(str(e), company_id)
#         logger.error(e)
#         return data
#     logger.info(status)
#     return msg


def change_response_format(message):
    return '{} ##True'.format(message)


@celery_app.task()
def generate_pack(file_id, patient_id, user_id, company_id, version, time_zone, transfer_to_manual_fill_system,
                  assigned_to, system_id, template_id, token, autoprocess_template, old_packs_dict, ext_change_rx_data,
                  ips_user_name):
    try:
        logger.info('In')
        if not isinstance(dpws_db, MySQLDatabase):
            logger.info("Invalid database instance")
            update_couch_db_pending_template_count(company_id=company_id)
            return change_response_format(err[1013])

        logger.info("Opening DB Connection from celery for: " + str(generate_pack))
        # commenting below db connection to resolve celery db connection issue
        # if not before_request_handler(dpws_db, logger):
        #     return change_response_format(err[1003])

        # Adding db connection code to open connection
        try:
            dpws_db.connect()
        except (Exception, OperationalError, sql_operaional, peewee_operational) as e:
            print("in_exception: ", str(e))
            logger.info("in_exception: " + str(e))
            logger.error("error in opening database connection: " + str(e))
            update_couch_db_pending_template_count(company_id=company_id)
            return change_response_format(err[1003])

        logger.info("Connection successful")
        order_no, pack_plate_location = None, None
        if not settings.USE_CONVEYOR:

            # commenting as the function is not getting used because it requires system id and not company id
            # order_no = PackDetails.db_max_order_no(company_id)

            order_no = 0
            pack_plate_location = cycle(settings.PACK_PLATE_LOCATION)

        # checking database connection
        logger.info("Is Database connection closed: {}".format(dpws_db.is_closed()))
        logger.info("getting canister master drug ids")
        canister_drug_id_set = CanisterMaster.db_get_drug_ids(company_id)
        logger.info("canister master db_get_drug_ids done")

        try:
            logger.info("fetching company settings")
            company_settings = get_company_setting_by_company_id(company_id=company_id)
            required_settings = settings.PACK_GENERATION_REQUIRED_SETTINGS
            settings_present = all([key in company_settings for key in required_settings])
            if not settings_present:
                # return error(6001)
                update_couch_db_pending_template_count(company_id=company_id)
                return change_response_format(err[6001])
        except InternalError:
            # return error(2001)
            update_couch_db_pending_template_count(company_id=company_id)
            return change_response_format(err[2001])
        logger.info("generating packs")
        gen_pack = GeneratePack(
            file_id, patient_id, user_id, order_no, pack_plate_location,
            canister_drug_id_set, company_id, company_settings,
            2, version, time_zone=time_zone,
            transfer_to_manual_fill_system=transfer_to_manual_fill_system, assigned_to=assigned_to,
            system_id=system_id, template_id=template_id, token=token, autoprocess_template=autoprocess_template
        )
        gen_pack.initialize_auto_process_template_parameters(old_packs_dict=old_packs_dict,
                                                             ext_change_rx_data=ext_change_rx_data,
                                                             ips_user_name=ips_user_name)
        try:
            logger.info("in prepare data")
            gen_pack.prepare_data()
        except PackGenerationException as e:
            logger.info("PackGenerationException:" + str(e))
            print(str(e))
            data = error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
            logger.error(data)
            update_couch_db_pending_template_count(company_id=company_id)
            return data
        except Exception as e:
            logger.info("prepare data exception:" + str(e))
            data = error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
            logger.error(e)
            update_couch_db_pending_template_count(company_id=company_id)
            return data

        try:
            bulk_pack_ids([gen_pack], company_settings)
        except PharmacySoftwareResponseException as e:
            update_couch_db_pending_template_count(company_id=company_id)
            return error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
        except Exception as e:
            logger.error(e, exc_info=True)
            data = error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
            update_couch_db_pending_template_count(company_id=company_id)
            return data
        pack_ids_dict = dict()
        try:
            gen_pack.start_pack_generation(pack_ids_dict)
        except (PackGenerationException,
                PharmacyRxFileGenerationException,
                IOError,
                PharmacySoftwareResponseException,
                PharmacySoftwareCommunicationException,
                PharmacySlotFileGenerationException) as e:
            logger.error(e)
            update_couch_db_pending_template_count(company_id=company_id)
            return error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)

        try:
            delivery_date_set = update_delivery_date({'update_existing': False, 'patient_ids': [patient_id]})
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            logger.info('Could not set delivery date')
            data = error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
            logger.error(e)
            update_couch_db_pending_template_count(company_id=company_id)
            return data

        pack_ids_list = [pack_id for pack_ids in list(pack_ids_dict.values()) for pack_id in pack_ids]

        status = set_unit_dosage_flag(company_id=company_id,pack_list=pack_ids_list)
        print(pack_ids_list)
        if transfer_to_manual_fill_system and pack_ids_list:
            db_max_assign_order_no_manual_packs(company_id, pack_ids_list)

        update_couch_db_pending_template_count(company_id=company_id)

        try:
            if old_packs_dict and ext_change_rx_data:
                logger.debug("Check if there is any change in drug information as compared to old packs..")
                update_slot_drug_status = \
                    db_update_slot_details_drug_with_old_packs(update_drug_dict=old_packs_dict["slot_drug_update"],
                                                               ext_change_rx_data=ext_change_rx_data,
                                                               user_id=user_id)
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            logger.info('Could not process the check and update for Slot Drugs.')

        try:
            if old_packs_dict and ext_change_rx_data:
                db_process_new_packs_change_rx(old_packs_dict=old_packs_dict, ext_change_rx_data=ext_change_rx_data,
                                               company_id=company_id, user_id=user_id,
                                               transfer_to_manual_fill_system=transfer_to_manual_fill_system,
                                               token=token)
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            logger.info('Could not process the new packs linked due to Change Rx.')

        if transfer_to_manual_fill_system:
            db_update_rx_changed_packs_manual_count(company_id)

        update_notifications_couch_db_green_status(file_id=file_id, patient_id=patient_id,
                                                   company_id=company_id)

        return '{} ##{}'.format(pack_ids_list, False)
    except Exception as e:
        logger.info("generate_pack main exception:")
        logger.info(e)
        data = error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
        update_couch_db_pending_template_count(company_id=company_id)
        return data
    except (OperationalError, sql_operaional, peewee_operational) as e:
        logger.info("Connection error:" + str(e))
        logger.info(e)
        data = error_response_pack_generation(file_id, patient_id, str(e), company_id, template_id)
        update_couch_db_pending_template_count(company_id=company_id)
        return data
    finally:
        logger.info("Closing DB Connection from celery for: " + str(generate_pack))
        after_request_handler(dpws_db)


def update_couch_db_queue(company_id, update_timestamp):
    try:
        logger.info(settings.CONST_COUCHDB_SERVER_URL)
        status, _ = update_queue_count(settings.CONST_TEMPLATE_MASTER_DOC_ID, 1, None, company_id,
                                       settings.TASK_OPERATION['Remove'], update_timestamp=update_timestamp,
                                       raise_exc=True)
        logger.info("couch_db_updated_with_status:" + str(status))
        return status
    except Exception as e:
        logger.info('Caught exception while couch db update, retrying')
        logger.info(e)
        status = update_couch_db_queue(company_id, update_timestamp)
        logger.info('Retried couch db update')
        return status


@task_postrun.connect()
def task_execute_after(signal=None, sender=None, task_id=None, task=None, args=None, retval=None, **kwargs ):
    if task.name == "tasks.dpws_multi_worker_tasks.generate_pack":
        logger.info(args)
        logger.info(kwargs)
        logger.info('retval: ' + str(retval))
        company_id = args[3]
        update_couch_db_count = retval.__contains__('##')
        logger.info("update_couch_db_count: "+str(update_couch_db_count))
        data = retval.split('##')
        update_timestamp = ast.literal_eval(data[-1])
        if update_timestamp:
            try:
                update_pending_template_data_in_redisdb(company_id)
            except (RedisConnectionException, Exception) as e:
                logger.info(e)
        if update_couch_db_count:
            try:
                logger.info('Reducing count in template doc for task_id: ' + str(task_id))
                status = update_couch_db_queue(company_id, update_timestamp)
                if status:
                    logger.info("couch db updated: "+str(company_id))
                else:
                    logger.info("Error while updating template counter in couch db")
            except Exception as e:
                logger.info(e)
