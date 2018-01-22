from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
import threading
from threading import Lock
from config import cfg
from device_config import dev
from device_config import Led
import subprocess

# akiko's helper fns
sys.path.insert(0, '../python-aux')
import cli

import logging


class Scan():

    """
    Configure for this device.
    Rest camera setting assumes only one LED type for the test signal. Real sz20 application will feature 3-4 different LED types.
    """
    scans = {
        '_testx':
                    {
                        'leds':  Led(10, 20, 0),
                        'resolution': [2560, 1920],
                        'shutter': 50,
                        'end': True
                    },
        '_testy':
            {
                'leds': Led(10, 20, 0),
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
        """
        Simple, single shot scan. Uses params from Device.Camera configuration. The LED is explicitly to be set by the application. I.e. what ever is being torched - that will be the illumination during scan. This action will not affect illum.
        :param base_filename: filename + file type extension that will be automatically appended to it
        :return: error code from the CLI procedure
        """

        logging.debug('Scan single image begins')
        # images are stored as base_filename_id.[jpg|png] where x id is taken from scan image identification list
        ext = '.jpg' # currently only jpg is supported
        filename = base_filename + ext
        logging.debug('scanning image %s' % filename)

        proc, output = cli.run_cli_sync(cfg['capture_cmd'].replace('#path', cfg['image_store_path'] + filename).replace('#width', str(dev.camera.get_resolution().width)).replace('#height', str(dev.camera.get_resolution().height)))
        logging.debug('finished execution, result code: %s' % str(proc.returncode))
        return proc.returncode

    def scan_seq(self, base_filename):
        """
        :param base_filename: base filename + scan type + file type extension. There are multiple images output by this function. See the scans dictionary of the Scan class.
        :return:
        """
        logging.debug('Scan sequence begins')
        # todo:
        # take n images, configuring different LED settings for each
        # images are stored as base_filename_id.[jpg|png] where x id is taken from scan image identification list
        packer_cmd = 'zip -j %s ' % (cfg['image_store_path'] + base_filename+'.zip')
        for k, v in self.scans.iteritems():
            filename = base_filename + k # extension will be added in scan()

            #todo:
            # set up LED for this iteration - not supported in emulator
            # set up camera for this iteration - not supported in emulator
            # invoke scan cli command to take the image and store it in file
            err = self.scan(filename)
            if err != 0:
                return err

            packer_cmd = packer_cmd + ' ' + cfg['image_store_path'] + filename + '.jpg'
            logging.debug('Zipping : ' + packer_cmd)

        proc, output = cli.run_cli_sync(packer_cmd)
        if proc.returncode != 0:
            logging.debug('Error zipping files, code: ' + str(proc.returncode))
            return proc.returncode

        logging.debug('Scan sequence zip created, code: ' + str(proc.returncode))
        return 0