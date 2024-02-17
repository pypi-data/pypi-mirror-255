import cherrypy
from dosepack.utilities.utils import call_webservice
import settings
from datetime import timedelta, datetime
from functools import wraps
from cachetools import LRUCache

# token_cache = LRUCache(maxsize=500)
token_cache = {}
BASE_URL = ''
VALIDATE_ACCESS_TOKEN_URL = ''


def init_url(base_url_param, access_token_url_param):
    """
    initializes variables for url to validate access token
    :param base_url_param:
    :param access_token_url_param:
    :return:
    """
    global BASE_URL, VALIDATE_ACCESS_TOKEN_URL
    BASE_URL = base_url_param
    VALIDATE_ACCESS_TOKEN_URL = access_token_url_param


def authenticate(logger):
    """
    this decorator is used for oauth user token validation
    :param logger:
    :return:
    """
    def decorator(function):

        @wraps(function)
        def validator(*args, **kwargs):
            if not settings.AUTHENTICATE:  # adding to toggle authentication
                response = function(*args, **kwargs)
                return response

            authorization = cherrypy.request.headers.get("Authorization")
            # checks if access_token present in request headers or not
            if authorization:
                access_token = authorization.split()[1]
                settings.ACCESS_TOKEN = access_token

                if access_token in token_cache:
                    logger.info(f"In authenticate, {access_token} token in token_cache")
                    # checks if access_token is present in token_cache dictionary and it is not expired yet
                    if datetime.utcnow() < token_cache[access_token]:
                        response = function(*args, **kwargs)
                        return response
                    else:
                        # removes access_token from token_cache if token is expired
                        token_cache.pop(access_token)
                        logger.info("Access token is expired.")
                        raise cherrypy.HTTPError(401)
                else:
                    logger.info(f"In authenticate, {access_token} token not in token_cache")
                    # webservice call to validate access_token if it is not present in dictionary
                    status, data = call_webservice(BASE_URL, VALIDATE_ACCESS_TOKEN_URL, {"access_token": access_token},
                                                   use_ssl=settings.AUTH_SSL)
                    if not status or data["status"] == "failure":
                        logger.error("Error in validating access token, Access-token: " + access_token)
                        raise cherrypy.HTTPError(401)

                    if "expires_in" in data["data"]:
                        token_info = data["data"]
                        # converting seconds into datetime object
                        expires_at = datetime.utcnow() + timedelta(seconds=int(token_info["expires_in"]))
                        # token_cache[access_token] = expires_at
                        response = function(*args, **kwargs)
                        return response
                    else:
                        logger.info("Access token is expired.")
                        raise cherrypy.HTTPError(401)

            else:
                logger.info("Access token not present in request headers.")
                raise cherrypy.HTTPError(401)
        return validator
    return decorator
