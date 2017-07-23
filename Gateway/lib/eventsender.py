"""Lib for handling message sending to the Inora server"""
# pylint: disable=line-too-long
import requests
import lib.inoralogger
LOGGING = lib.inoralogger.InoraLogger.get_logger()

class EventSender:
    """Class to send messages over IP"""

    def __init__(self, ip_address, port):
        self.__ip_address = ip_address
        self.__port = port

    def send_https_message(self, message):
        """sending a message over https"""
        url = 'https://' + self.__ip_address + ':' + str(self.__port)
        headers = {'Content-Length': str(len(message))}
        try:
            LOGGING.debug(" Sending poll result over Https. dst_IP:" + self.__ip_address + " port:" + str(self.__port))
            requests.post(url, data=message, headers=headers, verify=False)
        except requests.exceptions.ConnectionError as e:
            LOGGING.error(e)
