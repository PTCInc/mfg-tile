#!/bin/sh
# launcher.sh
#navigate home, then here, launch the python script for the pi

sleep 30
cd /
cd /home/pi/mfg-tile
sudo python modbusSigmaTile.py
