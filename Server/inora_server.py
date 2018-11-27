#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Inora Server execution main script'''

import ssl
import ConfigParser
import os.path
from inspect import getsourcefile
from BaseHTTPServer import HTTPServer
from lib.inorahttprequesthandler import inoraHTTPRequestHandler
from lib.inoralogger import InoraLogger
from lib.rsspopulater import RSSPopulater

class MyHTTPServer(HTTPServer):
    """this HTTPServer sub-class is necessary to allow passing custom request
       handler into the RequestHandlerClass"""
    def __init__(self, server_address, RequestHandlerClass, rsspopulater):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.rss_populater = rsspopulater


##############################################################################
#                             INIT LOGGER                                    #
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
#                             Let's Start!                                   #
##############################################################################

def main():
    """Launch the Inora Server"""
    server_port = get_conf_value('general_conf', 'port')
    web_root = get_conf_value('general_conf', 'web_root')
    rss_key = get_conf_value('general_conf', 'rss_key')
    get_conf_value('certs_conf', 'enable_truth')
    cert_path = get_conf_value('certs_conf', 'server_cert_path', isfile=True)
    key_path = get_conf_value('certs_conf', 'private_key_path', isfile=True)
    get_conf_value('handler_file', 'log_file_path', isfile=True)
    get_conf_value('handler_file', 'max_bytes')
    get_conf_value('handler_file', 'backup_count')
    get_conf_value('handler_file', 'args')
    LOGGING.info('Starting Server on port:%s', server_port)
    rsspopulater = RSSPopulater(web_root + '/' + rss_key)

    # Create a web server and define the handler to manage the incoming request
    # NOTE : We don't use server_ip_address as first parameter but leave it blank or won't handle requests
    server = MyHTTPServer(('', int(server_port)), inoraHTTPRequestHandler, rsspopulater)
    server.socket = ssl.wrap_socket(server.socket, keyfile=key_path, certfile=cert_path, server_side=True)
    LOGGING.info('Started httpserver on port %s', server_port)
    # Wait forever for incoming http requests
    server.serve_forever()

if __name__ == '__main__':
    main()
