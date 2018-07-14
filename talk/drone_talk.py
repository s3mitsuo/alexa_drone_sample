# -*- coding: utf-8 -*-

import os
import random
from dronekit import connect, VehicleMode
from multiprocessing import Process, Queue
import websocket


# talk
def talk(text):
    p = '/home/pi/alexa_drone_sample/talk/aquestalkpi/AquesTalkPi "' + text + '"| aplay'
    print(p)
    os.system(p)


# モード変換
def mode_conv(mode):
    mode = mode.upper()
    msg = mode
    if mode == "STABILIZE":
        msg = "スタビライズモード"
    elif mode == "ALT_HOLD":
        msg = "オルトホールドモード"
    elif mode == "LOITER":
        msg = "ロイターモード"
    elif mode == "GUIDED":
        msg = "ガイデッドモード"
    elif mode == "AUTO":
        msg = "オートモード"
    elif mode == "LAND":
        msg = "ランドモード"
    elif mode == "RTL":
        msg = "アールティーエルモード"
    return msg


def init(host, q, res_q):
    # connect to vehicle
    vehicle = connect(host, wait_ready=True)
    talk(str(int(vehicle.parameters["SYSID_THISMAV"])) + "号機接続完了")

    @vehicle.on_message("STATUSTEXT")
    def listener(self, name, message):
        if "PreArm" in message.text:
            talk("プレアームチェック")
            if "Need 3D Fix" in message.text:
                talk("GPSがロックできません。")
            elif "GPS" in message.text and "error" in message.text:
                talk("GPSに異常です。")
            elif "mag" in message.text and "field" in message.text:
                talk("コンパスエラーです。")
            elif "Battery" in message.text:
                talk("バッテリーを確認してください。")
            else:
                talk(message.text)
        elif "Crash" in message:
            talk("クラッシュしました。")
        else:
            talk(message.text)

    @vehicle.on_attribute("armed")
    def armed(self, name, message):
        if message:
            talk("離陸できます。")
        else:
            talk("待機します。")

    @vehicle.on_attribute("battery.level")
    def battery(self, name, message):
        talk("バッテリー残り" + str(message) + "パーセント")

    @vehicle.on_attribute("mode")
    def mode(self, name, message):
        mode = message.name.upper()
        print("mode="+mode)
        mode_str = mode_conv(mode)
        talk(mode_str)

    try:
        permit_arm = 2
        while True:
            cmd = q.get()
            print("cmd = " + cmd)
            # 受信した命令を処理
            if cmd == "connect_state" or cmd == "state":
                if vehicle is not None and vehicle.is_armable:
                    res = str(int(vehicle.parameters["SYSID_THISMAV"])) + "号機接続中です。"
                else:
                    res = "接続している機体はありません。"
                res_q.put_nowait(res)
            elif cmd == "battery_level":
                res = "バッテリー残量は" + str(int(vehicle.battery.level)) + "パーセントです。"
                res_q.put_nowait(res)
            elif cmd == "arm":
                permit_arm -= 1
                if permit_arm > 0:
                    res = "動きたくないよう。"
                else:
                    if vehicle.is_armable:
                        res = "しょーーーがないなー"
                        vehicle.armed = True
                    else:
                        res = "無理、アームできないみたい"
                    permit_arm = random.randrange(1, 3, 1)
                res_q.put_nowait(res)
            elif cmd == "disarm":
                res = "ディスアームしましたよ。"
                res_q.put_nowait(res)
            elif cmd == "mode_state":
                res = mode_conv(vehicle.mode.name) + "だよ、覚えとけよ"
                res_q.put_nowait(res)
            elif cmd == "mission_start":
                res = "室内だろ、あぶねーよ。やめとけ。"
                res_q.put_nowait(res)
            elif cmd == "greeting":
                res = "ごきげんよう、ご主人様"
                res_q.put_nowait(res)
            else:
                res = "何言ってんのかわかんない。"
                res_q.put_nowait(res)
    except KeyboardInterrupt:
        q.close()
        res_q.close()


# Connect to websocket server
def connect_ws(q, res_q):

    # メッセージ受信
    def on_message(ws, message):
        print(message)
        msg = message.split(",")
        # 機体制御コマンドではない
        if msg[0] != "vehicle":
            ws.send("Non-Cmd")
            return
        # 制御コマンドをキューに送信
        q.put_nowait(msg[1])
        # 2秒返事待ち（ブロック）
        try:
            res = res_q.get(True, 2)
            if res is not None and len(res) > 0:
                ws.send("命令は送っておきました。")
            else:
                ws.send("ごめんなさい、命令が送れたかどうか自信ありません。")
            talk(res)
        except Queue.Empty:
            ws.send("反応がありません。")

    # エラー処理
    def on_error(ws, error):
        pass

    # クローズ処理
    def on_close(ws):
        pass

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:3000/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
    print("WebSocket connected")


if __name__ == '__main__':
    queue = Queue()
    res_queue = Queue()
    #proc = Process(target=init, args=('/dev/ttyAMA0', queue,))
    proc = Process(target=init, args=('127.0.0.1:20001', queue, res_queue, ))
    proc.start()
    # Connect to WS
    connect_ws(queue, res_queue)
    proc.join()
