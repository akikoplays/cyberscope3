#!/usr/bin/env python

'''
streamer includes this file in order to determin gst sinks and other params.
e.g.

On rpi:
gst = { 'input' : './avis',
        'output' : 'fbdevsink',
        'screen' : [656,512]
        'decoder' : 'omxmpeg4videodec'
        }

On OSX:
gst = { 'input' : './avis',
        'output' : 'autovideosink',
        'screen' : [656,512]
        'decoder' : 'avdec_mpeg4'
        }

If you want to stream the decoded video as mpeg to a udp recipient set output to:
" jpegenc ! rtpjpegpay ! udpsink host=192.168.1.63 port=5000" (change IP to match your environment)

'''


gst = { 'input' : './avis',
# RPI version when streaming from localhost to localhost (i know, sounds stupid, but occasional gst lockups happen when gst plays direct from avi to fb)
        'output' : ' videoconvert ! video/x-raw,format=I420 ! jpegenc ! rtpjpegpay ! udpsink host=127.0.0.1 port=5000 ',
# OSX: show on screen
#'autovideosink',
# RPI: show on tft framebuffer, no localhost loopback streaming
#'fbdevsink',
        'screen' : [656,512],
        'decoder' : 'omxmpeg4videodec'
        }
