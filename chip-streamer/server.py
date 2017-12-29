#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import sys
import threading
from threading import Lock
import time
import json
from config import cfg
from device_config import dev
from scan import Scan

# akiko's helper fns
sys.path.insert(0, '../python-aux')
import cli

import logging
logging.basicConfig(filename=None, level=logging.DEBUG)


# Global vars
gst_thr = None  # gstreamer thread


def get_gst_thread():
    """
    Returns pointer to gstreamer thread that is stored globally
    """
    global gst_thr
    return gst_thr


def set_gst_thread(thr):
    global gst_thr
    gst_thr = thr


class VideoThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(VideoThread, self).__init__(group=group, target=target,
                                       name=name, verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        self.proc = None
        self.stopFlag = False
        self.mutex = Lock()
        self.playing = False

        return

    def run(self):
        logging.debug('vt: running with %s and %s', self.args, self.kwargs)
        logging.debug('vt: starting cli %s', self.kwargs['cmd'])

        self.proc = cli.run_cli_async(self.kwargs['cmd'])
        # marked as playing
        self.mutex.acquire()
        self.playing = True
        self.mutex.release()
        while self.proc.poll() is None:
            self.mutex.acquire()
            try:
                if self.stopFlag is True:
                    break
            finally:
                self.mutex.release()

            time.sleep(0.01)

        # mark as stopped
        self.mutex.acquire()
        self.playing = False
        self.mutex.release()
        logging.debug('vt: cli finished: %s ', self.kwargs['cmd'])
        pass

    def stop_stream(self):
        self.stopFlag=True

    def get_gst_process(self):
        return self.proc

    @property
    def is_playing(self):
        try:
            self.mutex.acquire()
            ret = self.playing
        except:
            return None
        finally:
            self.mutex.release()
        return ret


class S(BaseHTTPRequestHandler):

    def _print(self, s, append_log = None):
        # self.wfile.write('%s</br>' % s)
        logging.debug('%s' % s)
        if append_log is not None:
            append_log[0] = append_log[0] + s + '\n'

    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def get_param(self, params_dict, name):
        if not name in params_dict:
            return None
        return params_dict[name]

    def send_json_response(self, _code=200, _log=''):
        d = {'code': _code, 'log': _log}
        s = json.dumps(d)

        self.send_response(_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write('%s' % s)

    def stop_video_stream(self, log):
        if get_gst_thread() is None:
            self._print('warning: can\'t stop stream. Thread is uninitialized', log)
            return False

        try:
            if get_gst_thread().isAlive():
                get_gst_thread().stop_stream()
                get_gst_thread().join()
                self._print('gst thread joined', log)
        except:
            self._print('error: thread stop failed, unknown exception', log)
        finally:
            # kill the gst process
            if get_gst_thread().get_gst_process() is not None:

                try:
                    cli.kill_process(get_gst_thread().get_gst_process())
                    self._print('gst process killed', log)
                except OSError as e:
                    self._print("-- OSError > %s " % e.errno, log)
                    self._print("-- OSError > %s " % e.strerror, log)
                    self._print("-- OSError > %s " % e.filename, log)
            else:
                self._print('gst process was not found, nothing to kill', log)

    def do_GET(self):

        code = 200
        qs = {}
        path = self.path
        params = {}
        logging.debug(path)
        if '?' in path:
            path, tmp = path.split('?', 1)
            params = urlparse.parse_qsl(tmp)
        logging.debug('%s, %s' % (path, qs))

        # for easier manipulation, convert to dictionary
        d = dict(params)

        # self._set_headers(code)
        # self._print("<html><body>")

        # main command parser
        s = 'n/a'
        log = ['']

        if 'act' in d:
            s = d['act']
            logging.debug('action: %s', s)
            if s == 'play':

                # if video already playing, stop it
                if get_gst_thread() is not None and get_gst_thread().is_playing:
                    self._print('Stopping previously playing stream', log)
                    self.stop_video_stream(log)

                self._print('Stream testvideo to recipient', log)
                set_gst_thread(VideoThread(kwargs={'cmd': cfg['stream_cmd']}))
                get_gst_thread().start()
            elif s == 'stop':
                self._print('Stop stream', log)
                self.stop_video_stream(log)
            elif s == 'hello':
                self._print('Hello World :) !', log)
            elif s == 'listconnections':
                ret = cli.run_cli_sync('nmcli c')
                for line in ret:
                    self._print('%s' % line, log)
            elif s == 'listssids':
                ret = cli.run_cli_sync('nmcli device wifi list')
                for line in ret:
                    self._print('%s' % line, log)
            elif s == 'setresolution':
                resolution = self.get_param(d, 'res')
                if (resolution is None):
                    code = 400 # bad request
                else:
                    dims = resolution.split('x')
                    if len(dims) != 2:
                        code = 400
                        self._print('Invalid resolution: %s' % resolution, log)
                    else:
                        dev.camera.set_resolution(int(dims[0]), int(dims[1]))
                        self._print('Resolution set to %s x %s' % (dev.camera.get_resolution().width,
                                                                   dev.camera.get_resolution().height), log)
            elif s == 'scan':
                filename = self.get_param(d, 'filename')
                if filename is None:
                    code = 400
                    self._print('Bad request, missing parameter: \'filename\'. Must tell sz how to name file on disk, e.g. white-rnd.jpg')
                else:
                    self.do_capture(filename)
                # todo: error check
            elif s == 'getimage':
                filename = self.get_param(d, 'filename')
                if filename is None:
                    code = 400
                    self._print('Bad request, missing parameter: \'filename\'')
                else:
                    try:
                        img = self.load(cfg['image_store_path'] + filename)
                        self.send_response(200)
                        self.send_header('Content-type', 'image/jpeg')
                        self.end_headers()

                        self.wfile.write(img)
                        return
                    except:
                        code = 404
                        self._print('Error reading image %s' % filename)
            elif s == 'addssid':
                self._print('Adding SSID to the auto-connect list')
                ssid = self.get_param(d, 'ssid')
                psk = self.get_param(d, 'psk')
                self._print('SSID: %s' % (ssid, psk), log)
                self._print('PSK: %s' % (ssid, psk), log)
                ret = cli.run_cli_sync('nmcli device wifi connect \'%s\' password \'%s\' ifname wlan0' % (ssid, psk))
                for line in ret:
                    self._print('%s' % line, log)
            else:
                self._print('Unknown act: %s' % (s), log)

        self.send_json_response(code, log[0])

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
            # Doesn't do anything with posted data
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            self._set_headers()
            self.wfile.write("<html><body><h1>POST!</h1><pre>" + post_data + "</pre></body></html>")

    def load(self, filename):
        try:
            fp = open(filename, 'rb')
        except IOError:
            self._print('Could not open file: ', filename)

        try:
            content = fp.read()
        except IOError:
            self._print('Could not read from file: ', filename)
            return None

        s = str(content)
        b = bytes(s)
        return b

    def encode(self, file):
        # buffer = bytes(file, 'UTF-8')
        import base64
        str = base64.b64encode(file)
        return buffer

    # todo: support for different file extensions / image compression
    def do_capture(self, filename='snap.jpg'):
        # note:
        # this call is automated, sz makes a series of images in a specific order
        # autofocus first

        # todo: implement series of sync gst-launch shots for single hires images
        # best way to implement is to keep it in a separate python module, so that it can be easily
        # updated depending on device target group
        # cli.run_cli_sync(cfg['capture_cmd'].replace('#path', cfg['image_store_path'] + filename).replace('#width', str(dev.camera.get_resolution().width)).replace('#height', str(dev.camera.get_resolution().height)))
        # todo: error check!

        # todo:
        # testing modular approach
        scan = Scan()
        scan.scan(filename)
        pass


def run(server_class=HTTPServer, handler_class=S, port=cfg['port']):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd on port %s' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()