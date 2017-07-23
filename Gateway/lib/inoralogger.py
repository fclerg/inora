"""inora logging module """

import logging.config
import os.path
from inspect import getsourcefile


class InoraLogger(object):
    '''inora logging tools'''
    @staticmethod
    def get_logger():
        '''returned the logger configured with the parameters set up in inora conf file'''
        logging.config.fileConfig(os.path.dirname(getsourcefile(lambda: None)) + '/../inora.conf')
        return logging.getLogger('inora_logger')
