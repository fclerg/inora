#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Device filtering tools"""

import ConfigParser
import json
import re

import lib.inoralogger

LOGGING = lib.inoralogger.InoraLogger.get_logger()


class ArbitraryDict(dict):
    """A dictionary that applies an arbitrary key-altering function
       before accessing the keys (see class MacDict)."""

    def __keytransform__(self, key):
        return key

    def __getitem__(self, key):
        return dict.__getitem__(self, self.__keytransform__(key))

    def __setitem__(self, key, value):
        return dict.__setitem__(self, self.__keytransform__(key), value)

    def __delitem__(self, key):
        return dict.__delitem__(self, self.__keytransform__(key))

    def __contains__(self, key):
        return dict.__contains__(self, self.__keytransform__(key))


class MacDict(ArbitraryDict):
    """Initiate a type to store mac:devicesname dictionary"""

    def __keytransform__(self, key):
        """Take a mac address and replace separators with hyphens"""
        match = re.match(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})(!)?', key)
        if not match:
            raise ValueError("The key must be a valid MAC address format with possible '!' at the end.")
        return key.replace(':', '-').lower()

class DeviceFilter(object):
    """Filter for dictionaries of device"""
    def __init__(self, configfile):
        self.__config_file = configfile

    @staticmethod
    def byteify(var):
        """To get rid of the encoding character when dumping a loaded Json string"""
        if isinstance(var, dict):
            return {DeviceFilter.byteify(key): DeviceFilter.byteify(value) for key, value in var.iteritems()}
        elif isinstance(var, list):
            return [DeviceFilter.byteify(element) for element in var]
        elif isinstance(var, unicode):
            return var.encode('utf-8')
        return var

    @staticmethod
    def jsonloads_hook(x):
        """json loads hook"""
        if x.get('_class') is not None:
            LOGGING.error('LA CLASS %s', x.get('_class'))

        if isinstance(x, MacDict):
            return {k: v for k, v in x.items()}
        return x

    @staticmethod
    def __convert_dict_to_macdict(dict1):
        dictconv = MacDict()
        for k, v in dict1.iteritems():
            dictconv[k] = v
        return dictconv

    def filter(self, devices):
        """Edit the given list of devices based on the filter config file"""
        config = ConfigParser.SafeConfigParser()
        config.read(self.__config_file)

        # Don't know how to get directly a MacDict from json.loads :(
        devices_dict = DeviceFilter.__convert_dict_to_macdict(DeviceFilter.byteify(json.loads(devices)))
        try:
            filtlist = MacDict(config.items('filters'))
        except ValueError:
            LOGGING.error('Invalid file format: %s. Verify MAC Addresses format in filters section.', self.__config_file)
            exit(1)

        for mac, name in filtlist.iteritems():
            match = re.match(r'\s*(([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2}))(!)?\s*', mac)
            # if MAC address format is correct
            if match:
                if match.group(1) in devices_dict:
                    # match.group(4) is the possible '!' after the mac address
                    if match.group(4):
                        LOGGING.debug('Removing from the dict. Mac:%s Name:"%s".', match.group(1), name)
                        del devices_dict[match.group(1)]
                    else:
                        LOGGING.debug('Updating the dict.' + ' Mac:%s. Renaming from "%s" to "%s"', mac, devices_dict[match.group(1)], name)
                        devices_dict[match.group(1)] = name
            else:
                LOGGING.error('Unknown Error in filter function')
        return devices_dict
