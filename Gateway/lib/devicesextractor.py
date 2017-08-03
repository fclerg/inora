# pylint: disable=line-too-long
"""This lib contains classes for scraping and extracting connected devices from router web interface"""
import os
import re
import time
import json
from abc import ABCMeta, abstractmethod
import requests

import lib.inoralogger as inoralogger

os.environ['TZ'] = 'Europe/London'
LOGGING = inoralogger.InoraLogger.get_logger()
#requests.packages.urllib3.disable_warnings()


class ExtractorFactory(object):
    """
    Factory to create some devices extractors
    """
    @staticmethod
    def factory(rtype, router_ip, poll_period):
        """returns an extractor instance depending on the router type"
        rtype passed in parameter"""
        if rtype == "Livebox2":
            return LiveboxConnectedDevicesExtractor(router_ip, poll_period)
        elif rtype == "BboxFast3504":
            return BboxConnectedDevicesExtractor(router_ip, poll_period)
        else:
            LOGGING.error('Invalid router name in configuration file: %s', rtype)
            exit(1)

class AbstractDevicesExtractor:
    """
    Generic type for the scrapping engine that extract the connected devices list
    """
    __metaclass__ = ABCMeta

    def __init__(self, router_ip, poll_period):
        self.__poll_period = poll_period
        self.__router_ip = router_ip

    @abstractmethod
    def get_devices_dict(self):
        """return devices dict out of the scrapping"""
        pass

    def get_poll_period(self):
        """return the poll period (time between each scrapping calls)"""
        return self.__poll_period

    def get_router_ip(self):
        """return the router IP address"""
        return self.__router_ip


class LiveboxConnectedDevicesExtractor(AbstractDevicesExtractor):
    """Extractor class for Livebox API"""
    USERNAME = 'admin'
    PASSWORD = '*********'

    def __init__(self, router_ip, poll_period):
        super(LiveboxConnectedDevicesExtractor, self).__init__(router_ip, poll_period)
        self.session = requests.Session()

    def __auth(self):
        context_id = ""
        # tweak in case of Connection exception
        while True:
            credentials = {'username': LiveboxConnectedDevicesExtractor.USERNAME, 'password': LiveboxConnectedDevicesExtractor.PASSWORD}
            LOGGING.debug('Authentication Livebox with User:%s LiveboxIP:%s', LiveboxConnectedDevicesExtractor.USERNAME, super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
            try:
                req = self.session.post("http://" + super(LiveboxConnectedDevicesExtractor, self).get_router_ip() + '/authenticate', params=credentials)
                context_id = req.json()['data']['contextID']
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                print "Retrying to connect..."
                time.sleep(3)
                continue
            if not 'contextID' in req.json()['data']:
                LOGGING.error('Authentication error. User:%s LiveboxIP:%s. Response:%s', LiveboxConnectedDevicesExtractor.USERNAME, super(LiveboxConnectedDevicesExtractor, self).get_router_ip(), str(req.text))
                print "Retrying to Authent"
                LOGGING.debug("Retrying to Authent...")
                time.sleep(3)
                continue
            break
        LOGGING.debug("Authentication Successful. User:%s context-id:%s", LiveboxConnectedDevicesExtractor.USERNAME, context_id)
        return context_id
        # print "Response2 : " + pprint.pprint(r.json())

    def __logout(self):
        LOGGING.debug("Loging out. IP : %s", super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
        while True:
            try:
                self.session.post("http://" + super(LiveboxConnectedDevicesExtractor, self).get_router_ip() + '/logout')
            except requests.exceptions.ConnectionError as exception:
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
                req = self.session.post("http://" + super(LiveboxConnectedDevicesExtractor, self).get_router_ip() + '/sysbus/Hosts:getDevices', headers=sah_headers, data='{"parameters":{}}')
            except requests.exceptions.ConnectionError as exception:
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
        LOGGING.debug("Waiting. PollPeriod:%s seconds", str(super(LiveboxConnectedDevicesExtractor, self).get_poll_period()))
        time.sleep(float(super(LiveboxConnectedDevicesExtractor, self).get_poll_period()))
        # Since responses from the Livebox are not always consistents, we run few query against it and consider a device
        # is connected if seen in, at least, one of the responses.
        number_of_tries = 4
        devices_dict = {}
        for i in range(number_of_tries):
            LOGGING.debug('%d/%d query to Livebox. IP:%s', i+1, number_of_tries, super(LiveboxConnectedDevicesExtractor, self).get_router_ip())
            devices_dict.update(self.__wifi_devices_dict(self.__get_all_devices(self.__auth())))
            time.sleep(3)
        return devices_dict

class BboxConnectedDevicesExtractor(AbstractDevicesExtractor):
    """Extractor class for Bbox F@st3504"""
    USERNAME = 'admin'
    PASSWORD = '*********'

    def __init__(self, router_ip, poll_period):
        super(BboxConnectedDevicesExtractor, self).__init__(router_ip, poll_period)
        self.session = requests.Session()

    def __auth(self):
        # tweak in case of Connection exception
        while True:
            try:
                req = self.session.get("http://" + super(BboxConnectedDevicesExtractor, self).get_router_ip() + '/login.html')
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                print "Retrying to get logging page..."
                time.sleep(3)
                continue
            if req.status_code != 200:
                LOGGING.error('Error getting Logging page. BboxIP:%s. Response:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip(), req.status_code)
                time.sleep(3)
                continue
            LOGGING.debug('Session initialized. BboxIP:%s. Response:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip(), req.status_code)
            break

        while True:
            credentials = {'password': BboxConnectedDevicesExtractor.PASSWORD, 'remember': 0}
            LOGGING.debug('Authentication Bbox with BboxIP:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip())
            try:
                req = self.session.post("http://" + super(BboxConnectedDevicesExtractor, self).get_router_ip() + '/api/v1/login', params=credentials)
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                print "Retrying to connect..."
                time.sleep(3)
                continue
            if not 'BBOX_ID' in req.cookies:
                LOGGING.error('Authentication error.  BboxIP:%s. Response:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip(), req.status_code)
                print "Retrying to Authent"
                LOGGING.debug("Retrying to Authent...")
                time.sleep(3)
                continue
            break
        LOGGING.debug("Authentication Successful. BBOX_ID:%s", req.cookies.get('BBOX_ID'))
        # print "Response2 : " + pprint.pprint(r.json())

    def __get_full_json(self):
        self.__auth()
        millis = 0
        while True:
            try:
                millis = int(round(time.time() * 1000))
                req = self.session.get("http://" + super(BboxConnectedDevicesExtractor, self).get_router_ip() + '/api/v1/hosts?_=' + str(millis))
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                print "Retrying to get logging page..."
                time.sleep(3)
                continue
            if req.status_code != 200:
                LOGGING.error("Getting bbox json failed. BBOX_ID:%s. BboxIP:%s. Response:%s", self.session.cookies.get('BBOX_ID'), super(BboxConnectedDevicesExtractor, self).get_router_ip(), req.status_code)
                print "Retrying to get bbox json..."
                time.sleep(3)
                continue
            return req.json()

    def __get_wifi_devices(self):
        # tweak in case of Connection exception
        wdict = {}
        bbox_json_content = self.__get_full_json()
        print "ici" + str(type(bbox_json_content))
        for device in bbox_json_content[0]['hosts']['list']:
            if str(device['active']) == '1' and str(device['link']).startswith("Wifi"):
                LOGGING.debug('Active device. mac:%s hostname:%s', device['macaddress'], device['hostname'])
                wdict[device['macaddress']] = device['hostname']
        LOGGING.debug("Retrieved all connected wifi devices from Bbox %s", super(BboxConnectedDevicesExtractor, self).get_router_ip())
        return wdict


    def get_devices_dict(self):
        LOGGING.debug("Waiting. PollPeriod:%s seconds", str(super(BboxConnectedDevicesExtractor, self).get_poll_period()))
        time.sleep(float(super(BboxConnectedDevicesExtractor, self).get_poll_period()))
        LOGGING.debug('query to Bbox. IP:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip())
        return self.__get_wifi_devices()
