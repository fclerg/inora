'''http server to handle incoming requests'''
import json
from BaseHTTPServer import BaseHTTPRequestHandler

import lib.inoralogger

LOGGING = lib.inoralogger.InoraLogger.get_logger()


class inoraHTTPRequestHandler(BaseHTTPRequestHandler):

    """Handle incoming HTTP(S) messages.
    """
    def do_POST(self):
        """process http POST requests"""
        LOGGING.debug('incoming POST request. IP-address:%s', self.client_address[0])
        content_len = int(self.headers.getheader('Content-Length', 0))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        # print post_body
        self.server.rss_populater.notif_decider(json.loads(post_body))
