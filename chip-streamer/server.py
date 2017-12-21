#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import sys
import threading
from threading import Lock
import time
from config import cfg

# akiko's helper fns
sys.path.insert(0, '../python-aux')
import cli

import logging
logging.basicConfig(filename=None, level=logging.DEBUG)


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
        return

    def run(self):
        logging.debug('vt: running with %s and %s', self.args, self.kwargs)
        logging.debug('vt: starting cli %s', self.kwargs['cmd'])

        self.proc = cli.run_cli_async(self.kwargs['cmd'])
        while self.proc.poll() is None:
            self.mutex.acquire()
            try:
                if self.stopFlag is True:
                    break
            finally:
                self.mutex.release()

            time.sleep(0.01)

        logging.debug('vt: cli finished: %s ', self.kwargs['cmd'])
        pass

    def stop_stream(self):
        self.stopFlag=True
    def get_gst_process(self):
        return self.proc


# Global vars
gst_thr = None  # gstreamer thread


class S(BaseHTTPRequestHandler):

    def _print(self, s):
        self.wfile.write('%s</br>' % s)
        logging.debug('%s' % s)


    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def get_param(self, params_dict, name):
        if not name in params_dict:
            return None
        return params_dict[name]


    def do_GET(self):
        global gst_thr
        global q

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

        self._set_headers(code)
        self._print("<html><body>")

        # main command parser
        s = 'n/a'
        if 'act' in d:
            s = d['act']
            logging.debug('action: %s', s)
            if s == 'play':

                # todo:
                # don't play video if video already playing, return error instead

                self._print('Stream test video stream to localhost')
                gst_thr = VideoThread(kwargs={'cmd':cfg['stream_cmd']})
                gst_thr.start()
            elif s == 'stop':
                self._print('Stopping stream')

                if gst_thr is not None:
                    # First join thread if necessary
                    try:
                        if gst_thr.isAlive():
                            gst_thr.stop_stream()
                            gst_thr.join()
                            self._print('gst thread joined')
                        else:
                            self._print('gst thread was not alive, nothing to join')
                    except:
                        self._print('gst thread not initialized')
                        pass

                    # Now, kill the gst process
                    if gst_thr.get_gst_process() is not None:

                        try:
                            cli.kill_process(gst_thr.get_gst_process())
                            self._print('gst process killed')
                        except OSError as e:
                            print "-- OSError > ", e.errno
                            print "-- OSError > ", e.strerror
                            print "-- OSError > ", e.filename
                    else:
                        self._print('gst process was not found, nothing to kill')
            elif s == 'hello':
                self._print('Hello World :) !')
            elif s == 'listconnections':
                ret = cli.run_cli_sync('nmcli c')
                for line in ret:
                    self._print('%s' % line)
            elif s == 'listssids':
                ret = cli.run_cli_sync('nmcli device wifi list')
                for line in ret:
                    self._print('%s' % line)
            elif s == 'addssid':
                self._print('Adding SSID to the auto-connect list')
                ssid = self.get_param(d, 'ssid')
                psk = self.get_param(d, 'psk')
                self._print('SSID: %s' % (ssid, psk))
                self._print('PSK: %s' % (ssid, psk))
                ret = cli.run_cli_sync('nmcli device wifi connect \'%s\' password \'%s\' ifname wlan0' % (ssid, psk))
                for line in ret:
                    self._print('%s' % line)
            else:
                self._print('Unknown act: %s' % (s))

        self.wfile.write("</body></html>")


    def do_HEAD(self):
        self._set_headers()

        
    def do_POST(self):
            # Doesn't do anything with posted data
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            self._set_headers()
            self.wfile.write("<html><body><h1>POST!</h1><pre>" + post_data + "</pre></body></html>")
        

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