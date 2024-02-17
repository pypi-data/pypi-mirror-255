import threading

from json2html import json2html

from dosepack.error_handling.error_handler import create_response


class Ping(object):
    """
          @class: Ping
          @type: class
          @param: object
          @desc:  If server is alive, then it'll send the response to the user,
                  when user pings the server
    """
    exposed = True

    def GET(self):
        response = {"result": "ok"}
        response = create_response(response)
        return response


class GetThreadStatus(object):
    """
          @class: GetThreadStatus
          @createdBy: Abhishek Nagar
          @createdDate: 24/11/2021
          @type: class
          @param: object
          @desc: to get list of a thread with status.
    """
    exposed = True

    def GET(self):
        current_threads = threading.enumerate()

        thread_data = []

        for item in current_threads:
            try:
                print(str(item.target))
            except AttributeError:
                print("item", str(item))
            thread_data.append({"thread_name": item.getName(), "status": int(item.is_alive()), "id": item.ident})

        response_data = json2html.convert(json={"thread_data": thread_data})
        return create_response(data=response_data)
