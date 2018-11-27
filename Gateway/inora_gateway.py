#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inora Gateway execution main script"""

import ConfigParser
import json
import os.path
from inspect import getsourcefile
from lib.inoralogger import InoraLogger
from lib.eventsender import EventSender
from lib.devicefilter import DeviceFilter
from lib.routers.liveboxconnecteddevicesextractor import LiveboxConnectedDevicesExtractor
from lib.routers.bboxconnecteddevicesextractor import BboxConnectedDevicesExtractor
from lib.routers.superhubconnecteddevicesextractor import SuperHubConnectedDevicesExtractor

##############################################################################
#                             LOGGER INIT                                    #
##############################################################################

LOGGING = InoraLogger.get_logger()

##############################################################################
#                             CONF HANDLING                                  #
##############################################################################

def get_conf_value(sectionval, optionval, isfile=False):
    """parse the config file and return the value of the given variable"""
    wconfig = ConfigParser.SafeConfigParser()
    # Tweak to retrieve the path
    conf_path = wconfig.read(os.path.dirname(getsourcefile(lambda: None)) + '/inora.conf')
    if not wconfig.has_option(sectionval, optionval):
        LOGGING.error('in %s: section:%s or option:%s missing', str(conf_path), sectionval, optionval)
        exit(1)
    if isfile:
        if not os.path.isfile(wconfig.get(sectionval, optionval)):  # Check if file exists
            LOGGING.error('%s NOT FOUND!', wconfig.get(sectionval, optionval))
            exit(1)
    LOGGING.debug('in %s: section:%s and option:%s Validated', str(conf_path), sectionval, optionval)
    return str(wconfig.get(sectionval, optionval))


##############################################################################
#                             Let's get started                              #
##############################################################################

def device_extractor_factory(rtype, router_ip, poll_period, credentials):
    """returns an extractor instance depending on the router type"
    rtype passed in parameter"""
    if rtype == "Livebox2":
        return LiveboxConnectedDevicesExtractor(router_ip, poll_period, credentials)
    if rtype == "BboxFast3504":
        return BboxConnectedDevicesExtractor(router_ip, poll_period, credentials)
    if rtype == "VirginSuperHub":
        return SuperHubConnectedDevicesExtractor(router_ip, poll_period, credentials)
    LOGGING.error('Invalid router name in configuration file: %s', rtype)
    return exit(1)


def main():
    """Launch the Inora Gateway"""
    credentials = {}
    router_ip_address = get_conf_value('general_conf', 'router_ip')
    server_ip_address = get_conf_value('general_conf', 'server_ip')
    server_port = get_conf_value('general_conf', 'server_port')
    poll_period = get_conf_value('general_conf', 'poll_period')
    router_type = get_conf_value('general_conf', 'router_type')
    credentials["router_login"] = get_conf_value('general_conf', 'router_login')
    credentials["router_password"] = get_conf_value('general_conf', 'router_password')
    get_conf_value('certs_conf', 'enable_truth')
    get_conf_value('certs_conf', 'server_cert_path', isfile=True)
    get_conf_value('certs_conf', 'private_key_path', isfile=True)
    get_conf_value('handler_file', 'log_file_path', isfile=True)
    get_conf_value('handler_file', 'max_bytes')
    get_conf_value('handler_file', 'backup_count')
    get_conf_value('handler_file', 'args')

    LOGGING.info('Starting...')
    dictdevices = device_extractor_factory(router_type, router_ip_address, poll_period, credentials)
    wfilter = DeviceFilter(os.path.dirname(getsourcefile(lambda: None)) + '/devices.filters')
    while True:
        sender = EventSender(server_ip_address, server_port)
        sender.send_https_message(json.dumps(wfilter.filter(json.dumps(dictdevices.poll_devices_dict(), indent=2)), indent=2))

if __name__ == '__main__':
    main()
