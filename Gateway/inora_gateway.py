"""
   Inora Gateway execution main script
"""

# pylint: disable=line-too-long
import ConfigParser
import json
import os.path
from inspect import getsourcefile
import lib.devicesextractor as devicesextractor
from lib.inoralogger import InoraLogger
from lib.eventsender import EventSender
from lib.devicefilter import DeviceFilter



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
        LOGGING.error('in ' + str(conf_path) + ': section:' + sectionval + ' or option:' + optionval + ' missing')
        exit(1)
    if isfile:
        if not os.path.isfile(wconfig.get(sectionval, optionval)):  # Check if file exists
            LOGGING.error(" " + wconfig.get(sectionval, optionval) + " NOT FOUND!")
            exit(1)
    LOGGING.debug('in ' + str(conf_path) + ': section:' + sectionval + ' and option:' + optionval + ' Validated')
    return str(wconfig.get(sectionval, optionval))


##############################################################################
#                             Let's get started                              #
##############################################################################



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
    dictdevices = devicesextractor.ExtractorFactory.factory(router_type, router_ip_address, poll_period, credentials)
    wfilter = DeviceFilter(os.path.dirname(getsourcefile(lambda: None)) + '/devices.filters')
    while True:
        sender = EventSender(server_ip_address, server_port)
        sender.send_https_message(json.dumps(wfilter.filter(json.dumps(dictdevices.get_devices_dict(), indent=2)), indent=2))

if __name__ == '__main__':
    main()
