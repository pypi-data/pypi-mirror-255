import json

import cherrypy

import settings
from dosepack.error_handling.error_handler import create_response
from dosepack.utilities.validate_auth_token import authenticate
from src.publisher import notify


class SendRefilDeviceData(object):
    """
          @class: SendRefilDeviceData
          @createdBy: Govind Savara
          @createdDate: 08/24/2017
          @lastModifiedBy: Govind Savara
          @lastModifiedDate: 08/24/2017
          @param: object
          @desc:
            1. Get the data from Mock refill device.
            2. send the data through websocket to front-end
    """
    exposed = True

    @authenticate(settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            data = json.loads(kwargs['args'])
            print('refill device data:', data)
            # send websocket data to user
            notify('refilldevice', json.dumps(data))

        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return create_response("success")