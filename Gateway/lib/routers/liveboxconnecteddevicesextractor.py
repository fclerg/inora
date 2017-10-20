# pylint: disable=line-too-long
"""Class for making API calls to extract connected devices from a Livebox v2"""
import time
import json
import requests
from lib.devicesextractor import AbstractDevicesExtractor
import lib.inoralogger
LOGGING = lib.inoralogger.InoraLogger.get_logger()

class LiveboxConnectedDevicesExtractor(AbstractDevicesExtractor):
    """Extractor class for Livebox API"""

    def __init__(self, router_ip, poll_period, credentials):
        super(LiveboxConnectedDevicesExtractor, self).__init__(router_ip, poll_period, credentials)
        self.session = requests.Session()

    def __auth(self):
        context_id = ""
        # tweak in case of Connection exception
        while True:
            credentials = {'username': super(LiveboxConnectedDevicesExtractor, self).get_credentials()["router_login"], 'password': super(LiveboxConnectedDevicesExtractor, self).get_credentials()["router_password"]}
            LOGGING.debug('Authentication Livebox with User:%s LiveboxIP:%s', credentials["username"], super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
            try:
                req = self.session.post("http://" + super(LiveboxConnectedDevicesExtractor, self).get_router_ip() + '/authenticate', params=credentials, timeout=20)
                context_id = req.json()['data']['contextID']
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exception:
                LOGGING.error(exception)
                print "Retrying to connect..."
                time.sleep(3)
                continue
            if not 'contextID' in req.json()['data']:
                LOGGING.error('Authentication error. User:%s LiveboxIP:%s. Response:%s', credentials["username"], super(LiveboxConnectedDevicesExtractor, self).get_router_ip(), str(req.text))
                print "Retrying to Authent"
                LOGGING.debug("Retrying to Authent...")
                time.sleep(3)
                continue
            break
        LOGGING.debug("Authentication Successful. User:%s context-id:%s", credentials["username"], context_id)
        return context_id
        # print "Response2 : " + pprint.pprint(r.json())

    def __logout(self):
        LOGGING.debug("Loging out. IP : %s", super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
        while True:
            try:
                self.session.post("http://" + super(LiveboxConnectedDevicesExtractor, self).get_router_ip() + '/logout', timeout=20)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break

    def __get_all_devices(self, context_id):
        sah_headers = {'X-Context':context_id,
                       'X-Prototype-Version':'1.7',
                       'Content-Type':'application/x-sah-ws-1-call+json; charset=UTF-8',
                       'Accept':'text/javascript'
                      }
        # tweak in case of Connection exception
        while True:
            try:
                req = self.session.post("http://" + super(LiveboxConnectedDevicesExtractor, self).get_router_ip() + '/sysbus/Hosts:getDevices', headers=sah_headers, data='{"parameters":{}}', timeout=20)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break
        LOGGING.debug("Retrieved all known devices from Livebox %s", super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
        return json.loads(req.text)

    def __wifi_devices_dict(self, all_devices_dict):
        wdict = {}
        LOGGING.debug('Extracting wifi devices subset')
        for device in all_devices_dict['result']['status']:
            if str(device['active']).strip() is 'True' and str(device['interfaceType']).strip() == '802.11':
                LOGGING.debug('Active device. mac:%s hostname:%s', device['physAddress'], device['hostName'])
                wdict[device['physAddress']] = device['hostName']
        self.__logout()
        return wdict

    def get_devices_dict(self):
        # Since responses from the Livebox are not always consistents, we run few query against it and consider a device
        # is connected if seen in, at least, one of the responses.
        number_of_tries = 4
        devices_dict = {}
        for i in range(number_of_tries):
            LOGGING.debug('%d/%d query to Livebox2. IP:%s', i+1, number_of_tries, super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
            devices_dict.update(self.__wifi_devices_dict(self.__get_all_devices(self.__auth())))
            time.sleep(3)
        return devices_dict
