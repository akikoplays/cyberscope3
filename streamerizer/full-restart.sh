#!/bin/bash

echo "Stopping streamerizer..."
sudo pkill -9 python
curl "http://raspberrypi.local:8010/?act=stop"
sleep 4
echo "Done."
echo "Restarting stream-server..."
sudo systemctl restart stream-server
echo "Starting streamerizer..."
sleep 3
curl "http://raspberrypi.local:8010/?act=play&input=/home/pi/cyberscope3/streamerizer/avis"

