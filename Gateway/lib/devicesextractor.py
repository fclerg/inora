"""This lib contains classes for scraping and extracting connected devices from router web interface"""
import os
import time

import lib.inoralogger as inoralogger

os.environ['TZ'] = 'Europe/London'
LOGGING = inoralogger.InoraLogger.get_logger()
#	ts.packages.urllib3.disable_warnings()

class AbstractDevicesExtractor(object):
    """
    Generic type for the scrapping engine that extract the connected devices list
    """
    def __init__(self, router_ip, poll_period, credentials):
        self.__poll_period = poll_period
        self.__router_ip = router_ip
        self.__router_credentials = credentials

    def get_devices_dict(self):
        """Implementation must return a dictionary 'MAC Address->device name' out of the scrapping"""
        raise NotImplementedError("This method must be implemented")

    def poll_devices_dict(self):
        """Template method to get the devices dictionary"""
        LOGGING.debug("Waiting. PollPeriod:%s seconds", str(self.__poll_period))
        time.sleep(float(self.__poll_period))
        # Tweak to get the router type in the log line
        LOGGING.debug("Query to %s. IP:%s", self.__class__.__name__.replace("ConnectedDevicesExtractor", ""), self.__router_ip)
        return self.get_devices_dict()

    def get_router_ip(self):
        """return the router IP address"""
        return self.__router_ip

    def get_credentials(self):
        """returns a dictionary with the router authenticaton info"""
        return self.__router_credentials
