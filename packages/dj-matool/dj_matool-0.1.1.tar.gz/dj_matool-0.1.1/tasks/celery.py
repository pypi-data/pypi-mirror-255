"""
This module creates task queue app using celery.
This app will be used to define tasks using decorator @celery_app.task,
which can be invoked using `celery_app.send_task` or `celery_app.apply_async` or `celery_app.delay`
This tasks needs worker to execute tasks asynchronously.
To create workers for windows while testing RUN ``` celery -A tasks worker --pool=solo -l INFO ```.
To create workers for unix RUN ``` celery -A tasks worker -l INFO ```.
(WARNING: Above commands will pull tasks from all queues, we want to create workers for specific queues)


Deployment Instructions
~~~~~~~~~~~~~~~~~~~~~~~

For Queue `dpws_single_worker_tasks` we will use only single worker.
To achieve create worker using RUN ``` celery -A tasks worker -c 1 -Q dpws_single_worker_tasks  -l INFO ```
In above command,
-c (--concurrency) is 1, will create 1 worker.
-Q is queue name dpws_single_worker_tasks.

For Queue `dpws_multi_worker_tasks` we will use four workers.
To achieve create workers using RUN ``` celery -A tasks worker -c 4 -Q dpws_multi_worker_tasks  -l INFO ```
In above command,
-c (--concurrency) is 4, will create 4 workers.
-Q is queue name dpws_multi_worker_tasks (We can pass multiple queue name (comma separated)).

To schedule periodic tasks we need to run scheduler, which can be done by celery beat.
Celery beat can be invoked by running ``` celery -A tasks beat -l INFO ```
celery beat will put tasks into task queue and worker needs be online to execute these tasks.

"""

import os
import sys
import logging
from celery import Celery

import settings
from tasks.settings import TaskConstant, TaskQueue
from model.model_init import get_connection_dict as get_dpws_connection_dict, init_db
from dosepack.base_model.base_model import db as dpws_db


# set up logger
logger = logging.getLogger("root")
sh = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
sh.setFormatter(formatter)
logger.addHandler(sh)

dpws_db_config_key = os.environ.get('CELERY_RESULTS_DB_KEY', TaskConstant.CELERY_RESULTS_DB_KEY)

dpws_db_dict = get_dpws_connection_dict(dpws_db_config_key)


celery_broker = os.environ.get('DP_CELERY_BROKER', TaskConstant.DP_CELERY_BROKER)
logger.info("celery_broker", str(celery_broker))

celery_app = Celery(
    'tasks',
    broker=celery_broker,
    backend='db+{}'.format(dpws_db_dict['connection_string']),
    include=[
        # task files to include for this celery app
        'tasks.dpws_single_worker_tasks',
        'tasks.dpws_multi_worker_tasks'
    ]
)
print(celery_app.conf)
# celery_app = Celery(
#     'tasks',
#     broker='amqp://localhost',
#     backend='db+{}'.format(dpws_db_dict['connection_string']),
#     include=[
#         # task files to include for this celery app
#         'tasks.dpws_single_worker_tasks',
#         'tasks.dpws_multi_worker_tasks'
#     ]
# )

# Optional configuration, see the application user guide.
celery_app.conf.update(
    result_expires=TaskConstant.CELERY_RESULT_EXPIRES
)

celery_app.conf.beat_schedule = {
    # my_task is for test purpose only
    'my_task': {
        'task': 'tasks.dpws_single_worker_tasks.test_task',
        'schedule': 5,
        'args': ('Unknown',),
        'options': {'queue': TaskQueue.SINGLE_WORKER}
    }
}

celery_app.conf.task_routes = {
    # making sure single worker tasks routes to `dpws_single_worker_tasks` queue
    # we will make sure there is only single worker running for queue `dpws_single_worker_tasks`
    'tasks.dpws_single_worker_tasks.*': {'queue': TaskQueue.SINGLE_WORKER},
    'tasks.dpws_multi_worker_tasks.*': {'queue': TaskQueue.MULTI_WORKER},
}

celery_app.conf.broker_transport_options = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.4,
}


def setup_custom_ca_bundle():
    cafile_path = os.path.join(
        settings.CUSTOM_CA_BUNDLE_PATH,
        settings.CUSTOM_CA_BUNDLE_FILE
    )
    os.environ['SSL_CERT_FILE'] = cafile_path
    os.environ["REQUESTS_CA_BUNDLE"] = cafile_path


setup_custom_ca_bundle()
init_db(dpws_db, dpws_db_config_key)


def run_celery_app():
    if celery_app is None:
        return False
    celery_app.start()
    return True


if __name__ == '__main__':
    run_celery_app()

    # INFO: RUN WORKER ON WINDOWS
    # celery -A tasks worker --pool=solo -l INFO
