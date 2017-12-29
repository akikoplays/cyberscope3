    author: boris posavec
        

# What is this

Because sz2 was very belated, i had to resort to all kinds of tricks in order to prepare some basic functionality for the upcoming product. At some point we decided to use gstreamer for the realtime video feed from the device. I checked and iOS had supporting framework for that. gstreamer1 seems to be a lot better than gstreamer-0.1 which was used in Jasmine (MYS02) back in the days.

This project is about setting up CHIP to stream video test signal over the network to a recipient (another gstreamer listening on a specific port).
It covers how to prepare CHIP for gstreamer as well as how to develop python script for that, and on recipient' side how to enable video player for the incoming signal.

Note:
as much as this was initially intended for CHIP, you can use it with RPI or MacOS or Linux desktops. The only thing you need are python2.7+gstreamer-1.0.


# How to read this

This documentation, sadly, tries to encompass both system setup and application development. Some segments are only meant for firmware developers, that is how to setup software on the emulating device. Some segments are important for application developers because they explain how to communicate with the emulator, which commands are supported by it, what is the response format, etc.


# Update: CHIP or ... ?

Initially I started this emulator intending it for CHIP, because I had a piece lying somewhere, and I knew that CHIP had both wifi and ble combined, plus a decent, very fast booting linux distribution with apt.
But after a while I started using MacOS and RPI for the same task, so you don't really need CHIP, you can set it up on another linux machine, or mac. You just need gst-1.0 invokable from shell, and python 2.7.9+ and that's it.


# What you need in order to set up the emulating device

CHIP already comes with python2.7.9 preinstalled, so you just need to add gstreamer1:

    apt install gstreamer-1.0 
    apt install gstreamer1.0-plugins-base
    apt install gstreamer1.0-plugins-good
    apt gstreamer1.0-plugins-bad
    apt install gstreamer1.0-plugins-ugly
    apt install python-gst-1.0


# MacOS gstreamer-1.0 DIY compile 

In case you are setting this up on an MacOS, get Cerberos.
https://github.com/GStreamer/cerbero

managed to build gst-launch / inspect the basic package
now building good, bad, and ugly plugins.


## Instructions

1. cerbero-uninstalled bootstrap
2. cerber-uninstalled package gstreamer-1.0
3. install by doubleclicking the needed .pkg files that were created in step 2
4. install gstreamer-1.0-devel-1.13.0.1-x86_64.pkg needed for headers and libs
5. edit .bash_profile, add:


    # add gstreamer to exe path 
    export PATH=$PATH:/Library/Frameworks/GStreamer.framework/Versions/1.0/bin/
    export PKG_CONFIG_PATH=/Library/Frameworks/GStreamer.framework/Versions/1.0/lib/pkgconfig/

.. and then when compiling use pkg-config --cflags --libs gstreamer-1.0

takes eternity to build, but it WORKS :)


## Building hello example

    # https://gstreamer.freedesktop.org/documentation/tutorials/basic/hello-world.html
    gcc hello-gst.c -o hello-gst `pkg-config --cflags --libs gstreamer-1.0`


# Python GST Test script - how to use

On OSX side, you want to receive the signal using gstreamer:

    gst-launch-1.0 udpsrc port=5000 caps="application/x-rtp, encoding-name=JPEG, payload=26" ! rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink 

On CHIP side you just fire the script:

    python gst-test.py


# Main firmware script

Main firmware script is called server.py.  It is a HTTP(s in future) server listening to incoming requests and executing them, returning JSON response to the sender. JSON response is usually formatted like this:

    {"code": 200, "log": "Stopping stream\n"}

Where code is same as HTTP Header code, and log contains some debug info, that may or may not be present depending on server configuration. E.g. production version most probably won't include log messages, whereas developer version will be abundant in logging.

Note that the firmware script is also capable of logging data in a file. This file may then be either automatically uploaded to some remote server, or per GET request to the client.


# How to launch

Start server.py. It launches a http server listening on port 8001 (by default, but you can change the port in the config.py file). You may use curl to send get requests to server:

    curl localhost:8001/?act=hello
    

# Supported Commands

* hello - simply hails back, with code 200, use to see if server is up 
* listssids - lists all visible SSIDs, returns them in json log field.
* listconnections - lists all known wifi connections, that are already remembered by device, and that the wifi handler will try to resort to
* play - starts video stream of resolution set by setresolution action 
* stop - stops video stream
* setresolution&res=640x400 - set resolution to a x b, note that depending on imaging device, there might be some resolution constraints, ie: 2560x1920 or 640x480 or 1024x720 or similar. Yet to be determined and documented.
* scan?filename=filename - acquires a single image, filename string, which is the name of the file on disk (or non volatile memory)
* getimage?filename=filename - download the image by its filename from disk (see scan command)

# Response 

The response from the emulator is in most cases a JSON string. Only in case of requesting an image (see below) the response will be the binary data, respectively encoded.

JSON response is usually formatted like this:

    {"code": 200, "log": "Stopping stream\n"}

where _code_ is same as HTTP Header code, and log contains some debug info, that may or may not be present depending on server configuration. E.g. production version most probably won't include log messages, whereas developer version will be abundant in logging. The _log_ is there only as an aid to the client side developer.


## Compatibility notes

Commands such as addssid, listssids and listconnections are tightly coupled with the underlying OS. E.g. on CHIP linux is configured to use _nmcli_ tool to set up and control SSIDs. On RPI it's probably _iw_. On SZ2 it's going to be .... still don't know, but some wpa-supplicant like command set. Current application does not support anything other than CHIP's _nmcli_   


## Shell / Curl based communication examples

First, make sure server.py (sz2 firmware) is running on the emulator, e.g. NTC CHIP with hostname _chip.local_ connected to the same SSID the computer you are using.

Let's hail sz2 emulator:

    curl chip.local:8001?act=hello
    {"code": 200, "log": "Hello World :) !\n"}    

Lets run a video stream, and receive it with gstreamer command line tool:

    # run a listener first
    gst-launch-1.0 udpsrc port=5000 caps="application/x-rtp, encoding-name=JPEG, payload=26" ! rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink 
    
    # in a new terminal tab, tell emulator to start streaming:
    curl chip.local:8001?act=play
    
    # after that you can stop emulator stream 
    curl chip.local:8001?act=stop
    
*Attention: make sure you always stop a video stream before doing anything that affects camera resolution, or other settings (yet TBD).*

To set a resolution, call this before starting video stream.

    # set VGA resolution
    curl "chip.local:8001?act=setresolution=640x400"
    curl chip.local:8001?act=play
    # .. after a while
    curl chip.local:8001?act=stop
    
Once you set resolution, until you reboot the emulator, the resolution will be used for image acquisition, be it stream or snapshot.

Next, you want to acquire a set of images (the so called _Scan Session_):
    
    # set HD resolution
    curl "chip.local:8001?act=setresolution=2560x1920"
    curl "chip.local:8001?act=scan&filename=white.jpg"
    # todo: configure next LED
    curl "chip.local:8001?act=scan&filename=uv.jpg"
    # todo: configure next LED
    curl "chip.local:8001?act=scan&filename=green.jpg"
    

Finally, you want to download the image. Current implementation is pretty much HTTP standard approach, the image data is uploaded as Content image/jpeg (note: future implementations may support different file types, such as PNG or RAW).

    # Request file from emulator:
    curl "chip.local:8001?act=getimage&filename=white.jpg"
    
To see the image you can use any browser, and type this in the URL bar:

    chip.local:8001?act=getimage&filename=white.jpg

    
    