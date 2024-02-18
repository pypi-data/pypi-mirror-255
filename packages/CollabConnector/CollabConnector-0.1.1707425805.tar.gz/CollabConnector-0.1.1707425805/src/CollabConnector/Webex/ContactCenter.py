import sys

import requests
import json
from .OutputStyle import TextStyle
import time
import urllib

requests.packages.urllib3.disable_warnings()


class Connect:
    access_token = None
    org_id = None

    # store token then fetch users orgId and save
    def __init__(self, access_token: str = None, org_id: str = None):
        if not access_token:
            TextStyle.error("Must pass API token for Admin API")
        else:
            self.access_token = access_token
            if org_id:
                self.org_id = org_id
            else:
                try:
                    self.org_id = self.get("/v1/subscriptions")['meta']['orgId']
                except Exception as err:
                    raise Exception(f"Error with Token or getting Org")

    # get next page for large requests
    @staticmethod
    def find_next_page(call_response):
        return True

    # basic REST GET
    def get(self, uri, data={}, page_size=50, page=0):
        if uri.find("organization//") > -1:  # add org ID for ease of use
            uri = uri.replace("//", f"/{self.org_id}/")
        elif uri.find("/v1/") > -1 and self.org_id is not None:
            data['orgId'] = self.org_id

        if uri.find("{orgid}") > -1: # remove {orgid} syntax from documentation to make it easy
            uri = uri.replace("/{orgid}/", f"/{self.org_id}/")

        if len(data) > 0:
            data = f"&{urllib.parse.urlencode(data)}"
        else:
            data = ""

        headers = {"Accept": "application/json",
                   "Authorization": f"Bearer {self.access_token}"}

        return_data = {'data': [], 'meta': {}}
        api_url = f"https://api.wxcc-us1.cisco.com/{uri.strip('/')}?pageSize={page_size}&page={page}{data}"
        while True:  # loop for throttling
            try:
                response = requests.get(f"https://api.wxcc-us1.cisco.com/{uri.strip('/')}?pageSize={page_size}&page={page}{data}",
                                        headers=headers,
                                        verify=False)

            except Exception as err:
                raise Exception(f"Error sending Webex CC REST GET - {uri} {err}")

            else:
                if response.status_code == 200 and response.json():
                    try:
                        response_data = json.loads(response.text)
                    except Exception as err:
                        TextStyle.error(f"Return Data not in correct format - {response.text}")
                        return False

                    else:
                        if isinstance(return_data, str):
                            TextStyle.error(f"Return Data not in correct format - {response.text}")
                            return False

                        if isinstance(response_data, list):  # reformat v2 API to match v1 cor consistent return
                            response_data = {'data': response_data,
                                             'meta': {'orgId': self.org_id,
                                                      'urlexpiration': None,
                                                      'library_added': True}
                                             }
                        else:
                            return_data['meta']['library_added'] = False

                        if isinstance(response_data, dict):
                            if 'meta' not in response_data.keys():
                                return { "data": [response_data],
                                               'meta': {
                                                           'orgId': self.org_id,
                                                            'urlexpiration': None,
                                                            'library_added': True
                                                       }
                                         }
                            if  "links" not in response_data['meta'].keys() or response_data['meta']['page'] == response_data['meta']['totalPages']:
                                return_data = {'data': return_data['data'] if return_data else response_data['data'],
                                               'meta': {
                                                           'orgId': response_data['meta']['orgId'] if "orgId" in response_data['meta'].keys() else self.org_id,
                                                            'urlexpiration': None,
                                                            'library_added': True
                                                       }
                                               }
                                return return_data
                            else:
                                page += 1
                                return_data['data'].extend( response_data['data'] if 'data' in response_data.keys() else response_data )

                elif response.status_code >= 200 and response.status_code < 300:
                    return True
                elif response.status_code == 429 or response.status_code == 429:  # handle throttling Wait and don't return to continue loop
                    TextStyle.warning(f"{uri}{data} - API Request throttled: {response.headers['Retry-After']}")
                    time.sleep(int(response.headers['Retry-After']) + 1)

                elif response.status_code == 401:
                    TextStyle.error("Webex Admin token invalid.  Generate new token.")
                    return False

                else:
                    TextStyle.error(f"Error sending CC GET to Webex - {uri}{data} {response}{response.text}")
                    return False

    def delete(self, uri):
        if uri.find("organization//") > -1:  # add org ID for ease of use
            uri = uri.replace("//", f"/{self.org_id}/")

        headers = {"Accept": "application/json",
                   "Authorization": f"Bearer {self.access_token}"}

        while True:  # loop for throttling
            try:
                response = requests.delete(f"https://api.wxcc-us1.cisco.com/{uri.strip('/')}",
                                           headers=headers,
                                           verify=False)

            except Exception as err:
                raise Exception(f"Error sending Webex CC REST DELETE - {uri} {err}")

            else:
                if response.status_code == 429:  # handle throttling
                    time.sleep(int(response.headers['Retry-After']) + 1)
                elif response.status_code == 200 and response.json():
                    return json.loads(response.text)
                elif 200 < response.status_code < 300:
                    return True
                else:
                    TextStyle.error(f"Error sending CC DELETE to Webex - {uri} {response}{response.text}")
                    return False

    def post(self, uri, data):
        if uri.find("organization//") > -1:  # add org ID for ease of use
            uri = uri.replace("//", f"/{self.org_id}/")

        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {self.access_token}"}

        while True:  # loop for throttling
            try:
                response = requests.post(f"https://api.wxcc-us1.cisco.com/{uri.strip('/')}",
                                         headers=headers,
                                         data=json.dumps(data),
                                         verify=False)

            except Exception as err:
                raise Exception(f"Error sending Webex CC REST POST - {uri} {err}")

            else:
                if response.status_code == 429:  # handle throttling
                    time.sleep(int(response.headers['Retry-After']) + 1)
                elif response.status_code == 200 and response.json():
                    return json.loads(response.text)
                elif 200 < response.status_code < 300:
                    return True
                else:
                    TextStyle.error(f"Error sending POST to Webex - {uri} {response}{response.text}")
                    return False

    def put(self, uri, data):
        if uri.find("organization//") > -1:  # add org ID for ease of use
            uri = uri.replace("//", f"/{self.org_id}/")

        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {self.access_token}"}

        while True:  # loop for throttling
            try:
                response = requests.put(f"https://api.wxcc-us1.cisco.com/{uri.strip('/')}",
                                        headers=headers,
                                        data=json.dumps(data),
                                        verify=False)

            except Exception as err:
                raise Exception(f"Error sending Webex CC REST PUT - {uri} {err}")

            else:
                if response.status_code == 429:  # handle throttling
                    time.sleep(int(response.headers['Retry-After']) + 1)
                elif response.status_code == 200 and response.json():
                    return json.loads(response.text)
                elif 200 < response.status_code < 300:
                    return True
                else:
                    TextStyle.error(f"Error sending PUT to Webex - {uri} {response}{response.text}")
                    return False

    def patch(self, uri, data):
        if uri.find("organization//") > -1:  # add org ID for ease of use
            uri = uri.replace("//", f"/{self.org_id}/")

        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {self.access_token}"}

        while True:  # loop for throttling
            try:
                response = requests.patch(f"https://api.wxcc-us1.cisco.com/{uri.strip('/')}",
                                          headers=headers,
                                          data=json.dumps(data),
                                          verify=False)

            except Exception as err:
                raise Exception(f"Error sending Webex CC REST PATCH - {uri} {err}")

            else:
                if response.status_code == 429:  # handle throttling
                    time.sleep(int(response.headers['Retry-After']) + 1)
                elif response.status_code == 200 and response.json():
                    return json.loads(response.text)
                elif 200 < response.status_code < 300:
                    return True
                else:
                    TextStyle.error(f"Error sending PATCH to Webex - {uri} {response}{response.text}")
                    return False
