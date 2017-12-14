#!/usr/bin/env python

import os
import os.path
import sys
import subprocess
import argparse
# from PIL import Image
import config as cfg


'''
Streamer

What does it do?
===================
Streamer scans given folder for all .gif files, jumps randomly through them, taking each gif and unwrapping it into a 
sequence of frames (frame-1.png, frame-2.png, etc.) storing them in unwrapped/ folder.
Then it invokes gstreamer with multifilesrc directive and streams the animation sequence to the recipient (fbdevsink, 
another udp listener, autovideosink, or output file).

What are cmd line args?
========================
-i input folder (e.g. python streamer.py -i ./downloaded_anims/
-o output sink (e.g. python streamer.py -i ./downloaded_anims/ -o fbdevsink
-c convert source animgifs to avis (e.g. ./streamer.py -c -i ./animgifs -o ./avis 
-p play as a) "slideshow or b) "avi"; slideshow is the old way, convert to frames, multifilesrc frames


What does it use?
==================
To unwrap anim gif into a sequence of images it will invoke ffmpeg -i srcfile -o frame-%d.png.
To stream it will use gstreamer.


'''


def get_screen_resolution():
    return cfg.gst['screen'][0], cfg.gst['screen'][1]


def collect_files_of_type(root, extension):

    print "-- collecting files with extension: %s" % (extension)
    list = []
    for item in os.listdir(root):
        if os.path.isfile(os.path.join(root, item)):
            if item.endswith(extension):
                list.append(item)
                print ".... %s" % (item)
    return list


def run_cli(cmdstr):
    print "Running CLI: ", cmdstr
    ret = []
    proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
    for line in proc.stdout:
        print line
        ret.append(line)
    proc.wait()
    if proc.returncode != 0:
        print "Error: processor failed, ret code = ", proc.returncode
        exit(1)
    return proc.returncode, ret


def run_slide_show(args):

    temp_folder = "./unwrapped"

    print "Starting slide show player"
    print "-- reading animgifs from: %s" % args.input
    print "-- gst-sink them to: %s" % args.output
    print "-- temp folder is: %s" % temp_folder
    gifs = collect_files_of_type(args.input, "gif")

    idx = 0
    while True:
        for src in gifs:
            # or use new format method "Day old bread, 50% sale {0}".format("today")
            print "processing gif #%s %s" % (idx, src)
            cmdstr = "ffmpeg -i %s/%s %s/frame-%%d.png" % (args.input, src, temp_folder)
            print "running cmdline: " + cmdstr
            proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
            for line in proc.stdout:
                print line
            proc.wait()
            if proc.returncode != 0:
                print "Error: processor failed, ret code = ", proc.returncode
                exit(1)

            print "Launching gstreamer ..."
            # cmdstr = "gst-launch-1.0 multifilesrc location=\"%s/frame-%%d.png\" loop=false index=1 caps=\"image/png,framerate=\(fraction\)12/1\" ! pngdec ! videobox ! videoconvert ! videoscale method=0 add-borders=false ! video/x-raw,width=640,height=360 ! x264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=127.0.0.1 port=5000" % (temp_folder)
            # cmdstr = "gst-launch-1.0 multifilesrc location=\"%s/frame-%%d.png\" loop=false index=1 caps=\"image/png,framerate=\(fraction\)12/1\" ! pngdec ! videoconvert ! x264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.64 port=5000" % (temp_folder)
            # cmdstr = "gst-launch-1.0 multifilesrc location=\"%s/frame-%%d.png\" loop=false index=1 caps=\"image/png,framerate=\(fraction\)12/1\" ! pngdec ! videoconvert ! videoscale method=0 add-borders=false ! video/x-raw,width=640,height=360 ! jpegenc ! rtpjpegpay ! udpsink host=192.168.1.64 port=5000" % (temp_folder)

            # RPI version
            # cmdstr = "gst-launch-1.0 multifilesrc location=\"%s/frame-%%d.png\" loop=false start-index=1 caps=\"image/png,framerate=\(fraction\)12/1\" ! pngdec ! videoconvert ! fbdevsink" % (temp_folder)

            cmdstr = "gst-launch-1.0 multifilesrc location=\"%s/frame-%%d.png\" loop=false start-index=1 caps=\"image/png,framerate=\(fraction\)12/1\" ! pngdec ! videoconvert ! %s" % (temp_folder, args.output)
            run_cli(cmdstr)

            print "Deleting temp png sequence ..."
            cmdstr = "rm %s/*.png" % (temp_folder)
            run_cli(cmdstr)

    print "looping"

    return


def run_avi_shuffler(args):

    print "Starting avi shuffle player"
    print "-- reading animgifs from: %s" % args.input
    print "-- converting them to avis to be stored in: %s" % args.output

    avis = collect_files_of_type(args.input, "avi")
    scrw, scrh = get_screen_resolution()

    while True:
        for avi in avis:

            # determine video resolution using ffprobe
            cmdstr = "ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 \"%s/%s\"" % (args.input, avi)
            err, output = run_cli(cmdstr)
            dims = output[0].split('=')
            w = int(dims[1].strip())
            dims = output[1].split('=')
            h = int(dims[1].strip())
            print 'Video resolution : %s x %s ' % (w, h)

            # todo: figure out aspect ratio / fit to screen!
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
            run_cli(cmdstr)

    return


def run_converter(args):

    print "Starting gif to avi batch converter"
    print "-- reading animgifs from: %s" % args.input
    print "-- converting them to avis to be stored in: %s" % args.output
    gifs = collect_files_of_type(args.input, "gif")

    for gif in gifs:
        cmd = "ffmpeg -i %s/%s %s/%s.avi" % (args.input, gif, args.output, gif)
        run_cli(cmd)

    return


def main():

    # default values come from config file

    parser = argparse.ArgumentParser(description='Akikos automated anim gif streamer.')
    parser.add_argument('-c', '--convert', action="store_true", help='take all animgifs from -i and create avis in -o folder; uses ffmpeg')
    parser.add_argument('-i', '--input', type=str, default=cfg.gst['input'], help='source folder to scan for *.gif files')
    parser.add_argument('-o', '--output', type=str, default=cfg.gst['output'], help='in case of --play avi this will be the gstreamer pipe sink, e.g. autovideosink')
    parser.add_argument('-p', '--play', type=str, default='', help='if set to slideshow: convert each gif to frames, then show frames as slideshow, then delete frames; else if avi play them using avi (mp4) shuffler')
    args = parser.parse_args()

    print args

    if args.play == 'slideshow':
        run_slide_show(args)
    elif args.play == 'avi':
            run_avi_shuffler(args)
    elif args.convert:
        run_converter(args)
    else:
        run_avi_shuffler(args)


if __name__ == "__main__":
    main()
