"""populate the rss server with incoming inora events"""
# pylint: disable=line-too-long
import datetime
import os
import time
import random

import lib.inoralogger

os.environ['TZ'] = 'Europe/London'

LOGGING = lib.inoralogger.InoraLogger.get_logger()


class RSSPopulater(object):
    '''tools to pricess the incoming requests'''
    def __init__(self, filepath):
        self.memo_device_array = {}
        self.__filepath = filepath

    def notif_decider(self, device_array):
        """Update the XML RSS file if an event has been triggered in the supervised network (connection or deconnection of device).
        Args:
        device_array: the device dictionary to compare inorah the last received (memo_device_array), looking for possible new events.
        """
        # Algorithm of comparison :
        # if device_array is not empty
        if len(device_array) != 0:
            for mac, devicename in device_array.items():
                if mac in self.memo_device_array:
                    self.memo_device_array.pop(mac, None)
                else:
                    # write in the XML file
                    self.write_entry("Connexion : " + devicename)
                    LOGGING.info("Notification Connexion. mac:" + str(self.memo_device_array.get(mac)) + " device-ame:" + devicename)
        for mac in self.memo_device_array:
            # write in the XML file
            self.write_entry("Deconnexion : " + self.memo_device_array.get(mac))
            LOGGING.info("Notification Deconnexion. device-name: " + self.memo_device_array.get(mac))

        # memo_device_array is now device_array
        self.memo_device_array = device_array

    def write_entry(self, eventstring):
        """Write message in the RSS XML file in the RSS-matching format.
        Args:
            String of the event to write.
        """
        naive_dt = datetime.datetime.now()
        ts = time.time()
        lines = ""
        if not os.path.isfile(self.__filepath):
            with open(self.__filepath, "w+") as f:
                f.write('''<rss version="2.0"><channel>\n<title>Inora</title>\n<link>https://github.com/fclerg</link>\n<description>Inora rss feed</description>\n</channel></rss>\n''')

        # Messy way to insert lines right before the RSS closing HTML tags '</channel></rss>'
        # Read all the file inorahout the last line ('</channel></rss>') then writes it all again in an empty file
        # then writes the new entry and add the closing HTML tag again.
        with open(self.__filepath, "r") as f:
            lines = f.readlines()
            lines = lines[:-1]
        with open(self.__filepath, "w+") as f:
            f.write(''.join(lines))
        with open(self.__filepath, "a") as f:
            f.write('<item>\n')
            f.write('<title>' + eventstring + '</title>\n')
            f.write('<link>https://github.com/fclerg</link>\n')
            # 'guid' must be randomized in addition to the timestamp to avoid side effects
            f.write('<guid>' + str(ts) + str(random.randint(0, 100)) + '</guid>\n')
            f.write('<pubDate>' + naive_dt.strftime("%a, %d %b %Y %H:%M:%S") + '</pubDate>\n')
            f.write('<description>' + eventstring + '</description>\n')
            f.write('</item>\n')
            f.write('</channel></rss>')
        LOGGING.debug("Entry added to RSS feed file. file: " + self.__filepath + " content: " + eventstring)
