#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class for making API calls to extract connected devices from a Virgin Super Hub router"""
import time
import re
import requests
from lib.devicesextractor import AbstractDevicesExtractor
import lib.inoralogger
LOGGING = lib.inoralogger.InoraLogger.get_logger()

class SuperHubConnectedDevicesExtractor(AbstractDevicesExtractor):
    """Extractor class for the Virgin Super Hub router"""

    def __init__(self, router_ip, poll_period, credentials):
        super(SuperHubConnectedDevicesExtractor, self).__init__(router_ip, poll_period, credentials)
        self.session = requests.Session()

    def __get_data(self):
        url = 'http://' + super(SuperHubConnectedDevicesExtractor, self).get_router_ip() + '/VmLogin.html'
        # tweak in case of Connection exception
        while True:
            try:
                req = self.session.get(url)
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break

        LOGGING.debug("Scrapping login page. url:%s", url)
        return req.text

    def __get_name_field(self, html):
        namefield = ""
        for line in html.splitlines():
            match = re.match(r'.*inactive" name="([^ ]*)" id="password".*', line)
            if match:
                namefield = match.group(1)
        return namefield

    def __authent_https_POST_request(self):
        url = 'http://' + super(SuperHubConnectedDevicesExtractor, self).get_router_ip() + '/VmLogin.html'
        postdata = self.__get_name_field(self.__get_data()) + "=" \
                                + super(SuperHubConnectedDevicesExtractor, self).get_credentials()["router_password"]  \
                                + "&VmWpsPin=" \
                                + super(SuperHubConnectedDevicesExtractor, self).get_credentials()["router_login"]
        headers = {'Host': super(SuperHubConnectedDevicesExtractor, self).get_router_ip(),
                   'Content-Type': 'application/x-www-form-urlencoded'
                  }
        LOGGING.debug("Authenticating. Router-IP:%s", super(SuperHubConnectedDevicesExtractor, self).get_router_ip())
        # tweak in case of Connection exception
        while True:
            try:
                self.session.post(url, data=postdata, headers=headers)
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break

    def __get_devices_html_page(self):
        self.__authent_https_POST_request()
        url = 'http://' + super(SuperHubConnectedDevicesExtractor, self).get_router_ip() + '/device_connection_status.html'
        LOGGING.debug("Retrieving connected devices page. Router-IP:%s", super(SuperHubConnectedDevicesExtractor, self).get_router_ip())
        # tweak in case of Connection exception
        while True:
            try:
                req = self.session.get(url)
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break

        found = False
        for line in req.text.splitlines():
            match = re.match(r'.*var WifiDevicesList = \'([^;]*);.*', line)
            if match:
                found = True

        # If this is not the page wanted, redo (auth, etc...)
        if found is False:
            time.sleep(1)
            self.__get_devices_html_page()
        self.__logout()
        return req.text

    def __parse_devices(self, jsvar_string):
        dictm = {}
        for line in jsvar_string.split(','):
            match = re.match(r'.*(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))}-{[^}]*}-{([^}]*)}-.*', line)
            if match:
                dictm[match.group(1)] = match.group(4)
            else:
                LOGGING.debug("Field extraction failed for %s", line)
        LOGGING.debug("js var line parsed. Returning dict of devices.")
        return dictm

    def __extract_devices_jsvar(self, html):
        LOGGING.debug("Parsing javascript content")
        found = ""
        for line in html.splitlines():
            match = re.match(r'.*var WifiDevicesList = \'([^;]*);.*', line)
            if match:
                found = match.group(1)
        return found

    def __logout(self):
        url = 'http://' + super(SuperHubConnectedDevicesExtractor, self).get_router_ip() + '/VmLogout2.html'
        headers = {'Host': super(SuperHubConnectedDevicesExtractor, self).get_router_ip(),
                   'Content-Type': 'application/x-www-form-urlencoded'
                  }
        LOGGING.debug("Logging Out. Router-IP:%s", super(SuperHubConnectedDevicesExtractor, self).get_router_ip())
        # tweak in case of Connection exception
        while True:
            try:
                requests.post(url, headers=headers)
            except requests.exceptions.ConnectionError as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break

    def get_devices_dict(self):
        return self.__parse_devices(self.__extract_devices_jsvar(self.__get_devices_html_page()))
