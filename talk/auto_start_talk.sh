#!/bin/bash

sleep 15

screen -dm -S MavProxy mavproxy.py --master=udp:127.0.0.1:14550 --out=udp:172.20.10.3:14550 --out=udp:127.0.0.1:20001

# start websocket bridge
screen -dm -S Bridge node /home/pi/alexa_drone_sample/alexa/node_bridge.js > /dev/null 2>&1
sleep 5
# start front end
screen -dm -S Frontend python /home/pi/alexa_drone_sample/alexa/alexa_entry.py > /dev/null 2>&1
# start drone talk
screen -dm -S DroneTalk python /home/pi/alexa_drone_sample/talk/drone_talk.py > /dev/null 2>&1
