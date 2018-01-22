#!/usr/bin/env python

import urllib
import sys
import argparse

# akiko's helper fns
sys.path.insert(0, '../python-aux')
import cli

import logging
logging.basicConfig(filename=None, level=logging.DEBUG)

def get_file_list_from_url(url):
    cmd = 'curl %s | awk \'{for (i = 1; i < 9; i++) $i = ""; sub(/^ */, ""); print}\'' % (url)
    print 'Fetching results from cmd: ', cmd
    proc, output = cli.run_cli_sync(cmd)

    ret = []
    for name in output:
        ret.append(name.rstrip())

    return ret


def download_files_from_url(url, folder):
    list = get_file_list_from_url(url)
    for file in list:
        print 'downloading file ', file
        cmd = 'wget -q "%s%s" -P %s -o /dev/null' % (url, file, folder)
        proc, out = cli.run_cli_sync(cmd)


def run(url, folder):
    # sock = urllib.urlopen(url)
    # html = sock.read()
    # sock.close()
    # print html
    download_files_from_url(url, folder)


if __name__ == "__main__":
    from sys import argv

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default='./', help='Location to store downloaded files')
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('-i', '--input', required=True, help='URL from which to download files')

    args = parser.parse_args()

    # url = 'ftp://ftp.modland.com/pub/modules/Protracker/Supernao/'
    # folder = './downloads/'
    run(args.input, args.output)
