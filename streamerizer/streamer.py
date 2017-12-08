#!/usr/bin/env python

import os
import os.path
import sys
import subprocess
import argparse
from PIL import Image


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

What does it use?
==================
To unwrap anim gif into a sequence of images it will invoke ffmpeg -i srcfile -o frame-%d.png.
To stream it will use gstreamer.


'''

def collectFilesOfType(root, extension):
    print "-- collecting files with extension: %s" % (extension)
    list = []
    for item in os.listdir(root):
        if os.path.isfile(os.path.join(root, item)):
            if item.endswith(extension):
                list.append(item)
                print ".... %s" % (item)
    return list


def main():
    temp_folder = "./unwrapped"
    inputflags = "./"
    outputflags = "x264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.64 port=5000"
    parser = argparse.ArgumentParser(description='Akikos automated anim gif streamer.')
    parser.add_argument('-i', '--input', type=str, default=inputflags, help='source folder to scan for *.gif files to process')
    parser.add_argument('-o', '--output', type=str, default=outputflags, help='you can put fbdevsink or fakesink or filesink location="somepath"')
    args = parser.parse_args()

    print "-- setting input to %s" % (args.input)
    print "-- setting output to %s" % (args.output)

    gifs = collectFilesOfType(args.input, "gif")

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


            proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
            for line in proc.stdout:
                print line
            proc.wait()
            if proc.returncode != 0:
                print "Error: processor failed, ret code = ", proc.returncode
                exit(1)

            print "Deleting temp png sequence ..."
            cmdstr = "rm %s/*.png" % (temp_folder)
            proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
            for line in proc.stdout:
                print line
            proc.wait()
            if proc.returncode != 0:
                print "Error: processor failed, ret code = ", proc.returncode
                exit(1)

    print "looping"

if __name__ == "__main__":
    main()
