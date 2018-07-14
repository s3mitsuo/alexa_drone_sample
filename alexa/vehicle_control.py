# coding: utf-8
#!/usr/bin/env python
import time

from dronekit import connect, VehicleMode
from pymavlink import mavutil

import websocket

def connect_state():
    if vehicle is not None and vehicle.is_armable:
        return True
    else:
        return False

def cmd_arm():
    print("Arm vehicle")
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        return False

    print("Arming motors")
    vehicle.armed = True

    cnt = 1
    while not vehicle.armed:
        if cnt <= 0:
            break
        print(" Waiting for arming...")
        time.sleep(1)
        cnt -= 1
    return vehicle.armed

def cmd_disarm():
    print("Disarm vehicle")
    vehicle.armed = False
    cnt = 1
    while vehicle.armed:
        if cnt <= 0:
            break
        print(" Waiting for arming...")
        time.sleep(1)
        cnt -= 1
    return not vehicle.armed

def arm_and_takeoff(aTargetAltitude):
    arm()

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def ChangeMode(vehicle, mode):
	# change mode to given mode
	while vehicle.mode != VehicleMode(mode):
		vehicle.mode = VehicleMode(mode);
		time.sleep(0.5)
	
	return True;
	


##################
# web socket client
##################
def on_message(ws, message):
    print message
    message = message.split(",")
    if message[0] != "vehicle":
        ws.send("Non-Cmd")
        return
    message = message[1]
    if(message == 'connect_state'):
        state = connect_state()
        res = "待機状態です。" if state else "接続されていません。"
        ws.send(res)
    if(message == 'state'):
        if vehicle is None:
            ws.send("機体に接続していません。")
        else:
            arm = "アーム" if vehicle.armed else "ディスアーム"
            say = "機体は{}モードで{}状態です".format(vehicle.mode.name, arm)
            ws.send("接続中です。%s" % say)
    if(message == 'arm'):
        state = cmd_arm()
        res = "アームしました。" if state else "アームできません。"
        ws.send(res)
    if(message == 'disarm'):
        state = cmd_disarm()
        res = "ディスアームしました。" if state else "ディスアームできません。"
        ws.send(res)
    if(message == 'arm_and_takeoff'):
        arm_and_takeoff(10);
	time.sleep(3)
	ChangeMode(vehicle, "RTL")

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"


vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://127.0.0.1:3000/ws",
                          on_message = on_message,
                          on_error = on_error,
                          on_close = on_close)
ws.run_forever()
