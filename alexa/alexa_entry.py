# coding: utf-8
from flask import Flask
from flask_ask import Ask, question, session, statement, convert_errors
import logging
import websocket
from websocket import create_connection

app = Flask(__name__)
ask = Ask(app, '/')

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

repmsg = "命令をどうぞ"

@ask.launch
def launch():
    return question("ドローンハブではドローンを音声で制御できます。命令をどうぞ。").reprompt(repmsg)

@ask.intent('DroneConnectStateIntent')
def connect_state():
    print("connect_state called")
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,connect_state')
    while True:
        res = ws.recv()
        print("recv {}".format(res))
        if "vehicle" in res:
            continue
        ws.close()
        break
    return statement(res)

@ask.intent('DroneStateIntent')
def state():
    print("state called")
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,state')
    while True:
        res = ws.recv()
        print("recv {}".format(res))
        if "vehicle" in res:
            continue
        ws.close() 
        break
    return statement(res)

@ask.intent('DroneArmIntent')
def arm_control():
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,arm')
    while True:
        res = ws.recv()
        if "vehicle" in res:
            continue
        ws.close() 
        break
    return statement(res)

@ask.intent('DroneDisarmIntent')
def disarm_control():
    print("arm_control called")
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,disarm')
    while True:
        res = ws.recv()
        print("recv {}".format(res))
        if "vehicle" in res:
            continue
        ws.close() 
        return statement(res)

@ask.intent('DroneModeStateIntent')
def mode_state():
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,mode_state')
    while True:
        res = ws.recv()
        if "vehicle" in res:
            continue
        ws.close() 
        break
    return statement(res)

@ask.intent('DroneMissionIntent')
def mission():
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,mission_start')
    while True:
        res = ws.recv()
        if "vehicle" in res:
            continue
        ws.close() 
        break
    return statement(res)

@ask.intent('DroneGreetingIntent')
def mission():
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:3000/ws")
    ws.send('vehicle,greeting')
    while True:
        res = ws.recv()
        if "vehicle" in res:
            continue
        ws.close() 
        break
    return statement(res)

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = '接続状態、機体の状態、起動制御ができます。命令をどうぞ。'
    return question(speech_text).reprompt(speech_text)

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == "__main__":
    app.run(debug=True)
