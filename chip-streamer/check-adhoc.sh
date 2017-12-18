#!/bin/bash
#4.4.13-ntc-mlc
sh -c 'echo 1020 > /sys/class/gpio/export'
#4.4.13-ntc-mlc - prints 'in'
cat /sys/class/gpio/gpio1020/direction
#4.4.13-ntc-mlc '0' if jumper present, '1' if open
state=$(cat /sys/class/gpio/gpio1020/value)
if [ "$state" == "0" ];
then 
	echo "Ad-hoc jumper set"
	echo "Starting Ad-hoc network"
	ifconfig wlan1 up 192.168.2.2
	iwconfig wlan1 mode ad-hoc channel 1 essid chip

else 
	echo "Ad-hoc jumper not set"
	echo "Continuing with infrastructure mode"
fi


