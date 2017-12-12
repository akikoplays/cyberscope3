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
        'output' : ' jpegenc ! rtpjpegpay ! udpsink host=192.168.1.63 port=5000 ',#'autovideosink'
        'screen' : [656,512],
        'decoder' : 'avdec_mpeg4'
        }