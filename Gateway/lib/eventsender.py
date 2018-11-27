#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lib for handling message sending to the Inora server"""
import time
import requests
import lib.inoralogger
LOGGING = lib.inoralogger.InoraLogger.get_logger()

class EventSender(object):
    """Class to send messages over IP"""

    def __init__(self, ip_address, port):
        self.__ip_address = ip_address
        self.__port = port

    def send_https_message(self, message):
        """sending a message over https"""
        url = 'https://' + self.__ip_address + ':' + str(self.__port)
        headers = {'Content-Length': str(len(message))}
        # tweak in case of Connection exception
        while True:
            try:
                LOGGING.debug(" Sending poll result over Https. dst_IP:%s port:%s", self.__ip_address, self.__port)
                requests.post(url, data=message, headers=headers, verify=False, timeout=30)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exception:
                LOGGING.error(exception)
                LOGGING.info("Retrying to connect...")
                time.sleep(3)
                continue
            break
