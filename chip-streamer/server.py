#!/usr/bin/env python
"""
Very simple HTTP server in python.

Usage::
    ./dummy-web-server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import urlparse
import os
import os.path
import sys
import subprocess
import argparse
import threading
from config import cfg 

proc = None
gst_thr = None

def run_cli(cmdstr):
    global proc
    print "Running CLI: ", cmdstr
    ret = []
    proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
    for line in proc.stdout:
        print line
        ret.append(line)

    print 'Waiting for proc to finish'
    proc.wait()
    if proc.returncode != 0:
        print "Error: processor failed, ret code = ", proc.returncode
        exit(1)

    print 'Returning from CLI'
    return proc.returncode, ret


def kill_proc(p):
    print 'Killing process ', p
    if p:
        p.terminate()


class S(BaseHTTPRequestHandler):

    def _print(self, s):
        self.wfile.write('%s</br>' % s)
        print '%s' % s


    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def get_param(self, params_dict, name):
        if not name in params_dict:
            return None
        return params_dict[name]


    def do_GET(self):
        global proc
        global gst_thr

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

        self._set_headers(code)
        self._print("<html><body>")

        # main command parser
        s = 'n/a'
        if 'act' in d:
            s = d['act']
            print 'ACT: ', s
            if s == 'play':
                self._print('Stream test video stream to localhost')
                # run_cli(cfg['stream_cmd'])
                gst_thr = threading.Thread(target=run_cli, args=(cfg['stream_cmd']))
                gst_thr.start()
            elif s == 'stop':
                self._print('Stopping stream')
                gst_thr.join
                kill_proc(proc)
            elif s == 'hello':
                self._print('Hello World :) !')
            elif s == 'listconnections':
                ret = run_cli('nmcli c')
                for line in ret:
                    self._print('%s' % line)
            elif s == 'listssids':
                ret = run_cli('nmcli device wifi list')
                for line in ret:
                    self._print('%s' % line)
            elif s == 'addssid':
                self._print('Adding SSID to the auto-connect list')
                ssid = self.get_param(d, 'ssid')
                psk = self.get_param(d, 'psk')
                self._print('SSID: %s' % (ssid, psk))
                self._print('PSK: %s' % (ssid, psk))
                ret = run_cli('nmcli device wifi connect \'%s\' password \'%s\' ifname wlan0' % (ssid, psk))
                for line in ret:
                    self._print('%s' % line)
            else:
                self._print('Unknown act: %s' % (s))
                code = 404

        # self.wfile.write("<html><body><h1>Command: %s, Error code: %s</h1></body></html>" % (s, code))
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
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()