"""
    tasks.dpws_single_worker_tasks
    ~~~~~~~~~~~~~~~~

This module defines tasks which can be invoked by dpws server as asynchronous task.
This module should contain tasks which should be executed only one at a time
(i.e. Only single worker will work on these tasks)
Note: Periodic Tasks should not be defined in this module.

"""
import os
import logging

from peewee import IntegrityError, InternalError, DataError, MySQLDatabase, OperationalError
from peewee import OperationalError as peewee_operational

from sqlalchemy.exc import OperationalError as sql_operaional

from src.service.pack import update_drug_inventory_and_reorder_drugs
from .celery import celery_app
from celery.signals import task_postrun

from dosepack.utilities.manage_db_connection import use_database, before_request_handler, after_request_handler, \
    use_database_celery
from dosepack.base_model.base_model import db as dpws_db, db
from dosepack.local.lang_us_en import err
from src.model.model_file_header import FileHeader
from src.service.parser import Parser
from src.cloud_storage import download_blob, rx_file_blob_dir
from src.exceptions import FileParsingException
from src.service.misc import real_time_db_timestamp_trigger
from dosepack.error_handling.error_handler import error

import settings
import time

logger = logging.getLogger("root")

# Constants
DEFAULT_MAX_RETRY_COUNT = 3


def create_dir(path_list):
    """
    Creates directory required for app to run
    :param path_list:
    :return:
    """
    dir_path = os.path.join(*path_list)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


@celery_app.task
def test_task(name):
    logger.info(name)
    print('single worker', name)
    return 'Hello single worker {}'.format(name)


@celery_app.task()
def fetch_and_parse_rx_file(file_id, fill_manual, system_id, company_id):
    """
    Task to parse rx file,
    :param file_id:
    :param fill_manual:
    :param system_id:
    :return:
    """
    try:
        logger.info("in task fetch_and_parse_rx_file")
        logger.debug('FILE ID: {} to parse, fill_manual: {}'
                     ', system_id: {}'.format(file_id, fill_manual, system_id))
        if not isinstance(dpws_db, MySQLDatabase):
            logger.info("Invalid database instance")
            return error(1013)

        logger.info("Opening DB Connection from celery for: " + str(fetch_and_parse_rx_file))
        try:
            dpws_db.connect()
        except (Exception, OperationalError, sql_operaional, peewee_operational) as e:
            print("in_exception: ", str(e))
            logger.info("in_exception: " + str(e))
            logger.error("error in opening database connection: " + str(e))
            return error(1003)
        record = FileHeader.get(id=file_id)
        file_dir_as_list = [settings.PENDING_FILE_PATH, str(record.company_id)]
        create_dir(file_dir_as_list)
        file_path_as_list = file_dir_as_list + [record.filename]
        file_name = os.path.join(*file_path_as_list)
        logger.debug("downloading file: {}".format(file_name))
        with open(file_name, 'wb') as f:
            download_blob('{}/{}'.format(record.company_id, record.filename), f, rx_file_blob_dir)
        logger.debug('downloading done for file: {}'.format(file_name))
        rx_file_parser = Parser(record.created_by, record.filename, record.company_id,
                                record.manual_upload, system_id=system_id,
                                fill_manual=fill_manual, upload_file_to_gcs=False)
        logger.debug("download completed")
        rx_file_parser.file_id = record.id
        rx_file_parser.duplicate_file_check()
        logger.debug("duplicate file check completed")
        rx_file_parser.start_processing()
        logger.debug("returning value")
        return {'parsed': True,
                'file_name': record.filename}
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        try:
            file_name = record.filename
        except Exception:
            file_name = None
        # re-raising exception to store it in db, this will help in monitoring failed task
        raise FileParsingException('DB Exception while parsing file_name: {}, '
                                   'EXC: {}'.format(file_name, e)) from e  # chaining last exception
    finally:
        logger.info("Closing DB Connection from celery for: " + str(fetch_and_parse_rx_file))
        after_request_handler(dpws_db)


@task_postrun.connect()
def task_execute_after(signal=None, sender=None, task_id=None, task=None, args=None, retval=None, **kwargs ):
    if task.name == "tasks.dpws_single_worker_tasks.fetch_and_parse_rx_file":
        logger.info(args)
        logger.info(kwargs)
        logger.info('retval: ' + str(retval))
        company_id = args[3]
        logger.info(settings.CONST_COUCHDB_SERVER_URL)
        real_time_db_timestamp_trigger(settings.CONST_TEMPLATE_MASTER_DOC_ID, company_id=company_id)
        real_time_db_timestamp_trigger(settings.CONST_PRESCRIPTION_FILE_DOC_ID, company_id=company_id)


@celery_app.task()
@use_database_celery(db, settings.logger)
def update_drug_inventory_task(*args):
    """
    Task to call Elite API,
    :return:
    """
    try:
        param = dict(args)
        logger.info("inside update_drug_inventory_task")
        return update_drug_inventory_and_reorder_drugs(param)
    except Exception as e:
        logger.error(f"error in update_drug_inventory_task is {e}")