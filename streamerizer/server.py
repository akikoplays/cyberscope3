#!/usr/bin/env python

# Server requirements
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import threading
from threading import Lock
import sys
from config import cfg
sys.path.insert(0, '../python-aux')
import cli
import Queue

# proc = None
player_thr = None
# q = Queue.Queue()

import time
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

# def stop_player_thread():
#     global player_thr
#     player_thr.join()
#     player_thr = None


class S(BaseHTTPRequestHandler):
    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _print(self, s):
        self.wfile.write('%s</br>' % s)
        logging.debug('%s' % s)

    def stop_stream(self):
        global player_thr
        if player_thr is not None:
            # First join thread if necessary
            try:
                if player_thr.isAlive():
                    player_thr.stop_stream()
                    player_thr.join()
                    self._print('gst thread joined')
                else:
                    self._print('gst thread was not alive, nothing to join')
            except:
                self._print('gst thread not initialized')
                pass

            # Now, kill the gst process
            if player_thr.get_gst_process() is not None:

                try:
                    cli.kill_process(player_thr.get_gst_process())
                    self._print('gst process killed')
                except OSError as e:
                    print "-- OSError > ", e.errno
                    print "-- OSError > ", e.strerror
                    print "-- OSError > ", e.filename
            else:
                self._print('gst process was not found, nothing to kill')

    def do_GET(self):
        # global proc
        global player_thr
        # global q

        code = 200
        qs = {}
        path = self.path
        params = {}
        print path
        if '?' in path:
            path, tmp = path.split('?', 1)
            params = urlparse.parse_qsl(tmp)
        print path, qs

        # for easier manipulation, convert to dictionary
        d = dict(params)

        # main command parser
        s = 'n/a'

        self._set_headers(code)
        self.wfile.write('<html><body>')

        if 'act' in d:
            s = d['act']
            self.wfile.write('Command received: %s<br/>' % s)
            print 'Command received: ', s
            if s == 'play':
                # Kill stream if running
                if (player_thr is not None) and player_thr.isAlive():
                    self.stop_stream()
                # Start new stream
                player_thr = VideoThread(kwargs={'cmd': cfg['stream_cmd']})
                player_thr.start()
            elif s == 'stop':
                self._print('Stopping stream')
                self.stop_stream()
            elif s == 'hello':
                print 'Hello world :) !'
                self.wfile.write('Hello World :)<br/>')
            elif s == 'convert':
                input = d['input'] if 'input' in d else 'animgifs'
                output = d['output'] if 'output' in d else 'avis'
                print 'Convert animgifs to avis'
                self.wfile.write('Converting anim gifs to avis.. please wait this may take a while<br/>')
                self.wfile.write('Input: %s<br/>' % input)
                self.wfile.write('Output: %s<br/>' % output)
                cli.run_cli_async('%s -c all -i %s -o %s' % (cfg['stream_cmd'], input, output))
                self.wfile.write('Done :)<br/>')
            elif s == 'reboot':
                self.wfile.write('Rebooting')
                cli.run_cli_async('sudo shutdown -r 0')
            elif s == 'shutdown':
                self.wfile.write('Shutting down')
                cli.run_cli_async('sudo shutdown 0')
            else:
                print 'Unknown action: %s' % (s)
                self.wfile.write('Unknown action requested :/ <br/>')
                code = 404
        # self.wfile.write("<html><body><h1>Command: %s, Error code: %s</h1></body></html>" % (s, code))

        self.wfile.write('</body></html>')


    def do_head(self):
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S, port=cfg['port']):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
