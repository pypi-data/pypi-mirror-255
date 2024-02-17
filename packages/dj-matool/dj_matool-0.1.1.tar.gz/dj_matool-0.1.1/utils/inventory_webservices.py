import json
import logging

import requests

import settings
from dosepack.utilities.utils import construct_webservice_url, retry, log_args_and_response
from src import constants
from src.exceptions import InventoryBadRequestException, InventoryDataNotFoundException, \
    InventoryBadStatusCode, InventoryConnectionException, InvalidResponseFromInventory

logger = logging.getLogger("root")


@log_args_and_response
def inventory_api_call(api_name: str, data: dict = None, json_data=None, request_type="POST") -> dict:
    """

    @param json_data:
    @param request_type:
    @param api_name:
    @param data:
    @return:
    """
    try:
        token_request_data = {
            'username': settings.INVENTORY_USERNAME,
            'password': settings.INVENTORY_PASSWORD,
            'db': settings.INVENTORY_DATABASE_NAME
        }
        logger.debug("fetching access token from odoo")
        status, response = inventory_call_webservice(api_name=settings.GET_ACCESS_TOKEN, parameters=token_request_data,
                                                     headers={"Connection": "close"})
        if not status:
            raise InventoryConnectionException(response)

        if "access_token" not in response:
            raise InvalidResponseFromInventory(response)

        access_token = response["access_token"]
        logger.debug("Fetched access_token: " + str(access_token))
        logger.debug("calling api: " + str(api_name) + " data: " + str(data))

        if json_data:
            status, response = inventory_call_webservice(api_name=api_name, json_data=json_data, request_type=request_type,
                                                         headers={"Authorization": access_token, "Connection": "close"})
        elif data:
            status, response = inventory_call_webservice(api_name=api_name, parameters=data, request_type=request_type,
                                                         headers={"Authorization": access_token, "Connection": "close"})
        else:
            status, response = inventory_call_webservice(api_name=api_name, request_type=request_type,
                                                         headers={"Authorization": access_token, "Connection": "close"})
        if not status:
            raise InventoryConnectionException(response)
        return response

    except (InventoryBadRequestException, InventoryDataNotFoundException, InventoryBadStatusCode,
            InventoryConnectionException, InvalidResponseFromInventory) as e:
        logger.error("Error in Inventory Webservice Call {}".format(e))
        raise e


@retry(3)
@log_args_and_response
def inventory_call_webservice(api_name, parameters=None, base_url=settings.BASE_URL_INVENTORY, headers=None, timeout=None,
                              request_type="POST", use_ssl=settings.ODOO_SSL, call_electronics_api=False, json_data=None):
    """

    @param json_data:
    @param api_name: api name
    @param base_url: server url
    @param parameters: parameters to pass
    @param headers:
    @param request_type: GET or POST
    @param use_ssl: True / False
    @param timeout:
    @param call_electronics_api:
    @return: status, data
    """
    if request_type == "GET":
        url = construct_webservice_url(base_url, api_name, parameters, use_ssl=use_ssl)
    else:
        url = base_url + api_name
    logger.debug("calling inventory url: " + str(url))
    if use_ssl:
        connection_adapter = 'https://'
    else:
        connection_adapter = 'http://'

    # Connect to the inventory web service
    try:
        if request_type == "GET":
            data = requests.get(url, headers=headers, timeout=timeout, verify=False)
        else:
            url = connection_adapter + base_url + api_name
            if json_data:
                data = requests.post(url=url, json=json_data, timeout=timeout, headers=headers, verify=False)
            elif parameters:
                data = requests.post(url=url, data=parameters, timeout=timeout, headers=headers, verify=False)
            else:
                data = requests.post(url=url, timeout=timeout, headers=headers, verify=False)
        logger.debug("data fetched for url: " + str(url))
        response_status_code = data.status_code
        if call_electronics_api:
            response_data = data.content.decode('utf8').replace("'", '"')
        else:
            response_data = json.loads(str(data.content, 'utf-8'))

        logger.debug(
            "response data for url {}: status_code: {}, response: {}".format(url, response_status_code, response_data))

        if response_status_code == constants.INVENTORY_STATUS_CODE_OK:
            logger.debug("Success response from inventory-db")
            return True, response_data
        elif response_status_code == constants.INVENTORY_STATUS_CODE_BAD_REQUEST:
            logger.error("Inventory error: Invalid args in request url")
            raise InventoryBadRequestException(response_data)
        elif response_status_code == constants.INVENTORY_STATUS_CODE_DATA_NOT_FOUND:
            logger.error("Inventory error: Data not found for given parameters")
            raise InventoryDataNotFoundException(response_data)
        else:
            logger.error("Inventory error: Unexpected status code from Inventory")
            raise InventoryBadStatusCode(response_data)

    except requests.exceptions.Timeout as e:
        print('Timeout exception for url {}: {}'.format(url, e))
        return False, e

    except requests.ConnectionError as e:
        print('ConnectionError for url {}: {}'.format(url, e))
        return False, e

    except requests.HTTPError as e:
        print('HTTPError for url {}: {}'.format(url, e))
        return False, e

    except InventoryBadRequestException as e:
        raise InventoryBadRequestException(e)

    except InventoryDataNotFoundException as e:
        raise InventoryDataNotFoundException(e)

    except InventoryBadStatusCode as e:
        raise InventoryBadStatusCode(e)


