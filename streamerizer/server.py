#!/usr/bin/env python

# Server requirements
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import threading
import subprocess
from config import cfg


proc = None
player_thr = None

def run_cli(cmdstr, sync):
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
    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global proc
        global player_thr

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
        if 'act' in d:
            s = d['act']
            print 'ACT: ', s
            if s == 'play':
                print 'Start playing avis'
                player_thr = threading.Thread(target=run_cli, args=(cfg['stream_cmd'], None))
                player_thr.start()
            elif s == 'stop':
                if player_thr != None:
                    kill_proc(proc)
                    player_thr.join()
                    player_thr = None
            elif s == 'hello':
                print 'Hello world :) !'
            elif s == 'convert':
                print 'Convert animgifs to avis'
            else:
                print 'Unknown act: %s' % (s)
                code = 404

        self._set_headers(code)
        self.wfile.write("<html><body><h1>Command: %s, Error code: %s</h1></body></html>" % (s, code))

    def do_HEAD(self):
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
