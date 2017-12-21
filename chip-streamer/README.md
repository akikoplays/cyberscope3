author: boris posavec


# What is this

Because sz2 was very belated, i had to resort to all kinds of tricks in order to prepare some basic functionality for the upcoming product. At some point we decided to use gstreamer for the realtime video feed from the device. I checked and iOS had supporting framework for that. gstreamer1 seems to be a lot better than gstreamer-0.1 which was used in Jasmine (MYS02) back in the days.

This project is about setting up CHIP to stream video test signal over the network to a recipient (another gstreamer listening on a specific port).
It covers how to prepare CHIP for gstreamer as well as how to develop python script for that, and on recipient' side how to enable video player for the incoming signal.


# What you need to set up

CHIP already comes with python2.7.9 preinstalled, so you just need to add gstreamer1:
apt install gstreamer-1.0 
apt install gstreamer1.0-plugins-base
apt install gstreamer1.0-plugins-good
apt gstreamer1.0-plugins-bad
apt install gstreamer1.0-plugins-ugly
apt install python-gst-1.0


# How to use

On OSX side, you want to receive the signal using gstreamer:
gst-launch-1.0 udpsrc port=5000 caps="application/x-rtp, encoding-name=JPEG, payload=26" ! rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink 

On CHIP side you just fire the script:
python gst-test.py

