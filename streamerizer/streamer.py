#!/usr/bin/env python

import os
import os.path
import subprocess
import argparse
import config as cfg
import sys
sys.path.insert(0, '../python-aux')
import cli


'''
Streamerizer

What does it do?
===================
Streamer scans given folder for all .gif files, jumps randomly through them, taking each gif and unwrapping it into a 
sequence of frames (frame-1.png, frame-2.png, etc.) storing them in unwrapped/ folder.
Then it invokes gstreamer with multifilesrc directive and streams the animation sequence to the recipient (fbdevsink, 
another udp listener, autovideosink, or output file).

What are cmd line args?
========================
-i --input folder (e.g. python streamer.py -i ./downloaded_anims/
-o --output sink (e.g. python streamer.py -i ./downloaded_anims/ -o fbdevsink
-c --convert source animgifs to avis (e.g. ./streamer.py -c -i ./animgifs -o ./avis 
-p --play as "avi" 


What does it use?
==================
To unwrap anim gif into a sequence of images it will invoke ffmpeg -i srcfile -o frame-%d.png.
To stream it will use gstreamer.


'''


def get_screen_resolution():
    return cfg.gst['screen'][0], cfg.gst['screen'][1]


def run_avi_shuffler(args):

    print "Starting avi shuffle player"
    print "-- reading avi files from: %s" % args.input

    avis = cli.collect_files_of_type(args.input, "avi")
    scrw, scrh = get_screen_resolution()

    print "-- streaming them to : %s" % args.output

    while True:
        for avi in avis:

            # determine video resolution using ffprobe
            cmdstr = "ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 \"%s/%s\"" % (args.input, avi)
            proc, out = cli.run_cli_sync(cmdstr)
            if (proc.returncode!= 0):
                print 'Error caught from ffprobe, skipping file %s' % avi
                continue

            dims = out[0].split('=')
            w = int(dims[1].strip())
            dims = out[1].split('=')
            h = int(dims[1].strip())
            print 'Video resolution : %s x %s ' % (w, h)

            # figure out aspect ratio / fit to screen!
            # hint: https://stackoverflow.com/a/6565988
            rs = scrw / scrh
            ri = w/h
            if rs > ri :
                fitw = w * scrw/h # imgw * screenh/imgh
                fith = scrh
            else:
                fitw = scrw
                fith = h * scrw/w # imgh * screenw/imgw

#            cmdstr = "gst-launch-1.0 filesrc location=\"%s/%s\" ! %s" % (args.input, avi, args.output)
#             args.output = " avidemux ! mpeg4videoparse ! avdec_mpeg4 ! videoscale method=0 add-borders=false ! video/x-raw,width=%s,height=%s ! autovideoconvert ! autovideosink" % (fitw, fith)
#             args.output = " avidemux ! mpeg4videoparse ! avdec_mpeg4 ! videoscale method=0 add-borders=false ! video/x-raw,width=%s,height=%s ! openh264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.63 port=5000" % (fitw, fith)
#             args.output = " avidemux ! mpeg4videoparse ! avdec_mpeg4 ! videoscale method=0 add-borders=false ! video/x-raw,width=%s,height=%s ! videobox autocrop=true ! \"video/x-raw, width=%s, height=%s\" ! jpegenc ! rtpjpegpay ! udpsink host=192.168.1.63 port=5000" % (fitw, fith, scrw, scrh)
            output = " avidemux ! mpeg4videoparse ! %s ! videoscale method=0 add-borders=false ! video/x-raw,width=%s,height=%s !\
             videobox autocrop=true ! \"video/x-raw, width=%s, height=%s\" ! %s" \
                     % (cfg.gst['decoder'], fitw, fith, scrw, scrh, args.output)
            cmdstr = "gst-launch-1.0 filesrc location=\"%s/%s\" ! %s" % (args.input, avi, output)
            proc, out = cli.run_cli_sync(cmdstr)
            if (proc.returncode != 0):
                print ('-- error caught, gst-launch returned error code: %s, %s, skipping file %s' % (code, out, avi))

    return


def run_converter(args):

    print "Starting gif to avi batch converter"
    print "-- reading animgifs from: %s" % args.input
    print "-- converting them to avis to be stored in: %s" % args.output
    gifs = cli.collect_files_of_type(args.input, "gif")

    cli.run_cli_sync('mkdir %s' % args.output)
    for gif in gifs:
        cmd = "ffmpeg -y -i %s/%s %s/%s.avi" % (args.input, gif, args.output, gif)
        cli.run_cli_sync(cmd)

    return


def main():

    # default values come from config file

    parser = argparse.ArgumentParser(description='Akikos automated anim gif streamer.')
    parser.add_argument('-c', '--convert', help='take all animgifs from -i and create avis in -o folder; uses ffmpeg')
    parser.add_argument('-i', '--input', type=str, default=cfg.gst['input'], help='source folder to scan for *.gif files')
    parser.add_argument('-o', '--output', type=str, default=cfg.gst['output'], help='in case of --play avi this parameter is used as the gstreamer pipe sink, e.g. autovideosink')
    parser.add_argument('-p', '--play', type=str, default='', help='at the moment only "avi" is supported, i.e. anims from --input param will be played using avi (mp4) shuffler')
    args = parser.parse_args()

    print args

    if args.convert is not None:
        print "Convert set!"

    if args.play == 'avi':
            run_avi_shuffler(args)
    elif args.convert:
        run_converter(args)
    else:
        run_avi_shuffler(args)


if __name__ == "__main__":
    main()
