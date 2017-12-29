from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
import threading
from threading import Lock
from config import cfg
from device_config import dev
from device_config import Led

# akiko's helper fns
sys.path.insert(0, '../python-aux')
import cli

import logging


class Scan():

    """
    Configure for this device.
    Rest camera setting assumes only one LED type for the test signal. Real sz20 application will feature 3-4 different LED types.
    """
    scans = {'test':
                    {
                        'leds':  Led(10, 20, 0),
                        'resolution': [2560, 1920],
                        'shutter': 50,
                        'end': True
                    }
    }

    def __init__(self):
        logging.debug('Initializing Scan Object')

        # todo:
        # configure device_config module for this device
        # - set LED settings for #n leds
        # - set resolution
        # - set camera shutter

    def scan(self, base_filename):
        logging.debug('Scan starts')
        # todo:
        # take n images, configuring different LED settings for each
        # images are stored as base_filename_id.[jpg|png] where x id is taken from scan image identification list
        ext = '.jpg' # currently only jpg is supported
        for k, v in self.scans.iteritems():
            filename = base_filename + k + ext

            #todo:
            # set up LED for this iteration - not supported in emulator
            # set up camera for this iteration - not supported in emulator
            # invoke scan cli command to take the image and store it in file
            cli.run_cli_sync(cfg['capture_cmd'].replace('#path', cfg['image_store_path'] + filename).replace('#width', str(dev.camera.get_resolution().width)).replace('#height', str(dev.camera.get_resolution().height)))

