'''this lib contain the factory class to create some devices extractors'''
import lib.inoralogger as inoralogger
from lib.routers.liveboxconnecteddevicesextractor import LiveboxConnectedDevicesExtractor
from lib.routers.bboxconnecteddevicesextractor import BboxConnectedDevicesExtractor
LOGGING = inoralogger.InoraLogger.get_logger()

class DevicesExtractorFactory(object):
    """
    Factory to create some devices extractors
    """
    @staticmethod
    def factory(rtype, router_ip, poll_period, credentials):
        """returns an extractor instance depending on the router type"
        rtype passed in parameter"""
        if rtype == "Livebox2":
            return LiveboxConnectedDevicesExtractor(router_ip, poll_period, credentials)
        elif rtype == "BboxFast3504":
            return BboxConnectedDevicesExtractor(router_ip, poll_period, credentials)
        else:
            LOGGING.error('Invalid router name in configuration file: %s', rtype)
            exit(1)
