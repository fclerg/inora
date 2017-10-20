# pylint: disable=line-too-long
"""This lib contains classes for scraping and extracting connected devices from router web interface"""
import os
import time
from abc import ABCMeta, abstractmethod

import lib.inoralogger as inoralogger

os.environ['TZ'] = 'Europe/London'
LOGGING = inoralogger.InoraLogger.get_logger()
#	ts.packages.urllib3.disable_warnings()

class AbstractDevicesExtractor:
    """
    Generic type for the scrapping engine that extract the connected devices list
    """
    __metaclass__ = ABCMeta

    def __init__(self, router_ip, poll_period, credentials):
        self.__poll_period = poll_period
        self.__router_ip = router_ip
        self.__router_credentials = credentials

    @abstractmethod
    def get_devices_dict(self):
        """return devices dict out of the scrapping"""
        pass

    def poll_devices_dict(self):
        """Template method to get the devices dictionary"""
        LOGGING.debug("Waiting. PollPeriod:%s seconds", str(self.__poll_period))
        time.sleep(float(self.__poll_period))
        # Tweak to get the router type in the log line
        LOGGING.debug("query to %s. IP:%s", self.__class__.__name__.replace("ConnectedDevicesExtractor", ""), self.__router_ip)
        return self.get_devices_dict()

    def get_router_ip(self):
        """return the router IP address"""
        return self.__router_ip

    def get_credentials(self):
        """returns a dictionary with the router authenticaton info"""
        return self.__router_credentials
