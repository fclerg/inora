#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class for scrapping the bbox web interface to extract connected devices"""
import time
import requests
from lib.devicesextractor import AbstractDevicesExtractor
import lib.inoralogger
LOGGING = lib.inoralogger.InoraLogger.get_logger()

class BboxConnectedDevicesExtractor(AbstractDevicesExtractor):
    """Extractor class for Bbox F@st3504"""

    def __init__(self, router_ip, poll_period, credentials):
        super(BboxConnectedDevicesExtractor, self).__init__(router_ip, poll_period, credentials)
        self.session = requests.Session()

    def __auth(self):
        # tweak in case of Connection exception
        while True:
            try:
                req = self.session.get("http://" + super(BboxConnectedDevicesExtractor, self).get_router_ip() + '/login.html', timeout=20)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exception:
                LOGGING.error(exception)
                print "Retrying to get logging page..."
                time.sleep(3)
                continue
            if req.status_code != 200:
                LOGGING.error(
                    'Error getting Logging page. BboxIP:%s. Response:%s', \
                    super(BboxConnectedDevicesExtractor, self).get_router_ip(), \
                    req.status_code
                )
                time.sleep(3)
                continue
            LOGGING.debug('Session initialized. BboxIP:%s. Response:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip(), req.status_code)
            break

        while True:
            credentials = {'password': super(BboxConnectedDevicesExtractor, self).get_credentials()["router_password"], 'remember': 0}
            LOGGING.debug('Authentication Bbox with BboxIP:%s', super(BboxConnectedDevicesExtractor, self).get_router_ip())
            try:
                req = self.session.post(
                    "http://" + super(BboxConnectedDevicesExtractor, self).get_router_ip() + '/api/v1/login', params=credentials, timeout=20
                )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exception:
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
                req = self.session.get(
                    "http://" + super(BboxConnectedDevicesExtractor, self).get_router_ip() + '/api/v1/hosts?_=' + str(millis), timeout=20
                )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exception:
                LOGGING.error(exception)
                print "Retrying to get logging page..."
                time.sleep(3)
                continue
            if req.status_code != 200:
                LOGGING.error(
                    "Getting bbox json failed. BBOX_ID:%s. BboxIP:%s. Response:%s", \
                     self.session.cookies.get('BBOX_ID'), \
                     super(BboxConnectedDevicesExtractor, self).get_router_ip(), req.status_code
                )
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
        return self.__get_wifi_devices()
