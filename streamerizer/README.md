# About this project

    Project: Raspberry Pi Streamer
    Author Boris Posavec, blamemusic@gmail.com

The goal of this project is to create a stand alone and cross platform compatible video streamer with following features:

* gstreamer 1.0 based
* controllable via web server (python SimpleHTTPServer)
* tool to batch process anim gifs to avis (mp4)
* requires ffmpeg (ffmpeg and ffprobe)
* systemd services that bring up server and listener on boot-up


Lets simply describe how it works:

* stream-server.service and stream-listener.service are systemd services that are started on boot-up
* from another or same machine start avi player using http://machineip:8010/?act=play&input=/home/pi/cyberscope3/streamerizer/avis
* to stop the player, call http://machineip:8010/?act=stop
* you can provide another absolute path to the play action if you want to switch playlists


# Supported HTTP commands

* ?play&input=absolutepath : starts playback of avi files from the given path
* ?stop : stops playback
* ?hello : hails back and lists available commands
* ?reboot : reboots raspberry pi
* ?shutdown : shuts down raspberry pi
* ?convert&input=absolutepath&output=absolutepath


# How to install

First git clone the cyberscope3 repo from akiko's github:

    cd /home/pi/
    git clone https://github.com/akikoplays/cyberscope3.git
    
Next make a copy of config.py.in:

    $ cp config.py.in config.py
    
Edit the config.py file to match your platform. For example, on RPI with a 656x512 TFT screen,  the config file will look something like this:

    gst = { 'input' : './avis',
            # RPI version when streaming from localhost to localhost (i know, sounds stupid, but occasional gst lockups happen when gst plays direct from avi to fb)
            'output' : ' videoconvert ! video/x-raw,format=I420 ! jpegenc ! rtpjpegpay ! udpsink host=127.0.0.1 port=5000 ',
            # RPI: show on tft framebuffer
            'screen' : [656,512],
            'decoder' : 'omxmpeg4videodec'
        }
    
    
    cfg = {
            'stream_cmd' : '/usr/bin/python /home/pi/cyberscope3/streamerizer/streamer.py ',
            # Server listenes at this port
            'port' : 8010,
            'end' : True
          }

## How to start streamerizer when system boots up 

Raspbian as well as NextThing CHIP OS both rely on systemd. So, you will need to set up two services in systemd, if you want the streamer to come up online with the system.

Important: 

beacuse both server.py and streamer.py rely on cyberscope3/python-aux/cli.py module, you will have to make this module visible to python when invoked from systemd service manager. For that you need to make a symbolic link:

    # in case python modules search path is located in usr/lib/ :
    sudo ln -s /home/pi/cyberscope3/python-aux/cli.py /usr/lib/python2.7/
    
    # if not, you need to find it, by invoking e.g.
    find / -iname urlparse.py


First service:

    # /etc/systemd/system/stream-listener.service 
    
    [Unit]
    # By default 'simple' is used, see also https://www.freedesktop.org/software/systemd/man/systemd.service.html#Type=
    #Type=simple|forking|oneshot|dbus|notify|idle
    Description=Run Streamerizer on sys startup. This service invokes a script that runs gstreamer listener, server.py and sends a HTTP GET request to server.py to start playing avis.
    ## make sure we only start the service after network is up
    #After=network.target
    
    [Service]
    Type=simple
    ## here we can set custom environment variables
    Environment=AUTOSSH_GATETIME=0
    #Environment=AUTOSSH_PORT=0
    ExecStart=/usr/bin/gst-launch-1.0  -v udpsrc port=5000 caps="application/x-rtp, encoding-name=JPEG, payload=26" ! rtpjpegdepay ! jpegdec ! videoconvert ! fbdevsink
    ExecStop=/usr/bin/pkill -9 gst-launch-1.0
    # don't use 'nobody' if your script needs to access user files
    # (if User is not set the service will run as root)
    #User=nobody
    
    # Useful during debugging; remove it once the service is working
    StandardOutput=syslog
    
    [Install]
    WantedBy=multi-user.target
    

Second service:

    #/etc/systemd/system/stream-server.service        
    [Unit]
    # By default 'simple' is used, see also https://www.freedesktop.org/software/systemd/man/systemd.service.html#Type=
    #Type=simple|forking|oneshot|dbus|notify|idle
    Description=Run Streamerizer on sys startup. This service invokes a script that runs gstreamer listener, server.py and sends a HTTP GET request to server.py to start playing avis.
    ## make sure we only start the service after network is up
    #After=network.target
    
    [Service]
    Type=simple
    ## here we can set custom environment variables
    Environment=AUTOSSH_GATETIME=0
    #Environment=AUTOSSH_PORT=0
    ExecStart=/usr/bin/python /home/pi/cyberscope3/streamerizer/server.py
    ExecStop=/usr/bin/pkill -9 python
    # don't use 'nobody' if your script needs to access user files
    # (if User is not set the service will run as root)
    #User=nobody
    
    # Useful during debugging; remove it once the service is working
    StandardOutput=syslog
    
    [Install]
    WantedBy=multi-user.target
    
To enable the services:

    sudo systemctl enable stream-listener.service
    sudo systemctl enable stream-server.service
    sudo systemctl start stream-listener.service
    sudo systemctl start stream-server.service
    
    
# How to use

You can make as many folders with avi files as you please. Then using the web interface you can start playback in any of the folders, but remember that you need to provide the absolute path in the GET request, because stream server is started via systemd service and is pretty much agnostic of relative paths. 


## How to convert anim gifs to avi files

AVI format that is supported by streamerizer is MP4 as created with ffmpeg. In order to batch convert a whole folder with gifs to a folder with avis, use 

    http://machineip:8010/?act=convert&input=absolutepath&output=absolutepath

You can also do this manually, by logging in the RPI box, and then:

    cd /home/pi/cyberscope3/streamerizer/
    ./streamer.py -c 1 -input ./animgif-cyberpunk -output ./avi-cyberpunk
    
If the avi-cyberpunk folder doesn't exist, it will be created prior to the batch conversion process.


## What did I learn from this project

First thing, i wasn't able to get python gst to function. gst 1.0 bindings for python seem to be missing even after installing them on rpi via apt. 

Next, I learned how to control processes from python, and how to launch them in a separate thread, plus how to control them via http server, also in python. The idea of being able to control the streamer application via browser was really sweet.

Next, i managed to understand the intricacies of launching scripts via systemd services.. those absolute paths which were absolutely necessary when providing input params, as well as how to understand why a service has failed.

Then, I figured out the differences between rpi and say OSX gst pipelines. E.g. when repacking avi to jpeg stream, on rpi it was necessary to explicitly give the format of the jpeg during videoconvert: videoconvert ! video/x-raw,format=I420 ! jpegenc ... on OSX this wasn't the case.

Biggest issue I had, that made me switch to omxplayer on rpi, was that omxmpeg4videodec was causing dubious pipeline lock up. The next element in the pipe was unable to conitnue, as if nothing was fed to it. 