import json
import base64
import os

import redis

from settings import logger
from src.exceptions import RedisConnectionException


def get_connection_dict(db_config_name):
    try:
        json_file = open('config.json', "r")
    except FileNotFoundError:
        # for devs, as sometime only migration file can be run by main in migration file
        try:
            json_file = open('../config.json', "r")
        except FileNotFoundError:
            json_file = open('../../config.json', "r")

    data = json.load(json_file)
    json_file.close()

    # Here db_config_name is the key for the db engine present in
    # config.json file
    database = os.environ.get('MYSQL_DATABASE', data[db_config_name]["db"])
    username = os.environ.get('MYSQL_USER', base64.b64decode(data[db_config_name]["user"]))
    password = base64.b64decode(os.environ.get('MYSQL_PWD', data[db_config_name]["passwd"]))
    host = os.environ.get('MYSQL_HOST', data[db_config_name]["host"])
    connection_string = 'mysql+pymysql://{}:{}@{}/{}'.format(
        username.decode('utf-8') if hasattr(username, 'decode') else username,
        password.decode('utf-8') if hasattr(password, 'decode') else password,
        host,
        database
    )
    return {
        'database': database,
        'username': username,
        'password': password,
        'host': host,
        'connection_string': connection_string
    }


def init_db(db_instance, db_config_name):

    try:
        connection_dict = get_connection_dict(db_config_name)
        # print ("mysql database", database, password, type(password))

        # port = 3306
    except Exception as ex:
        raise Exception("Incorrect Value for db engine", ex)
    database = connection_dict['database']
    username = connection_dict['username']
    password = connection_dict['password']
    host = connection_dict['host']
    connection_string = connection_dict['connection_string']
    os.environ["SQLALCHEMY_DATABASE_URI"] = connection_string
    if db_instance.database is None:  # if not already initialized, init db
        db_instance.init(database, user=username, password=password, host=host)
        print('DB initialized with parameters - database: {}, host: {}'.format(database, host))


def test_db_connection(_db):
    """
    Opens connection on given db and closes it.
    :param _db: peewee.Database instance
    :return:
    """
    _db.connect()
    _db.close()


def init_redisdb(redis_db_config):
    try:
        json_file = open('config.json', "r")
    except FileNotFoundError:
        json_file = open('../config.json', "r")
    data = json.load(json_file)
    json_file.close()

    try:
        redis_host = os.environ.get('REDIS_HOST', data[redis_db_config]['host'])
        redis_password=os.environ.get('REDIS_PASSWORD', data[redis_db_config]['password'])
        redis_port = int(os.environ.get('REDIS_PORT',data[redis_db_config]['port']))
        redis_db = int(os.environ.get('REDIS_DB',data[redis_db_config]['db']))

        redisdb = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password, decode_responses=True)
        redisdb.ping()
        print('init_redisdb: Redis DB initialized with parameters - database: {0}, host: {1}, port: {2}'.format(redis_db, redis_host,redis_port))
        return redisdb
    except redis.exceptions.ConnectionError:
        logger.info("redisdb_connection_error: redis_host - {0}, redis_port - {1}, redis_password: - {2}, redis_db - {3}"
                    .format(redis_host,redis_port,redis_password,redis_db))
        raise RedisConnectionException("redisdb connection error")
    except Exception as e:
        raise Exception(e)