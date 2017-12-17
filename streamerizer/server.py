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


def stop_player_thread():
    global proc
    global player_thr
    kill_proc(proc)
    player_thr.join()
    player_thr = None


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

        self._set_headers(code)
        self.wfile.write('<html><body>')

        if 'act' in d:
            s = d['act']
            self.wfile.write('Command received: %s<br/>' % s)
            print 'Command received: ', s
            if s == 'play':
                if player_thr != None:
                    stop_player_thread()

                print 'Start playing avis'
                self.wfile.write('Start playing avis <br/>')
                input = d['input'] if 'input' in d else 'avis'
                cmd = cfg['stream_cmd'] + ' -i ' + input
                player_thr = threading.Thread(target=run_cli, args=(cmd, None))
                player_thr.start()
            elif s == 'stop':
                if player_thr != None:
                    self.wfile.write('Stopping player thread<br/>')
                    stop_player_thread()
                else:
                    self.wfile.write('Nothing to stop<br/>')
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
                run_cli('%s -c all -i %s -o %s' % (cfg['stream_cmd'], input, output), None)
                self.wfile.write('Done :)<br/>')
            else:
                print 'Unknown act: %s' % (s)
                self.wfile.write('Unknown action requested :/ <br/>')
                code = 404
        # self.wfile.write("<html><body><h1>Command: %s, Error code: %s</h1></body></html>" % (s, code))

        self.wfile.write('</body></html>')


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
