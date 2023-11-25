import paho.mqtt.client as paho
import ast
import requests

def set_class_pred(video_id: int, pred: dict):
    st = pred['class']
    res_st = 2 if  st != "empty" else -1
    pred['status'] = res_st

    params = {'video_id': pred['id']}
    del pred['id']

    print(pred)

    r = requests.post("http://127.0.0.1/api/update_video", data=pred, params=params)
    print(r.status_code, r.reason)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload)) 
    decode = msg.payload.decode('UTF-8')
    dict_req = ast.literal_eval(decode)
    res = set_class_pred(dict_req['id'], dict_req)
    print(res)

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect('127.0.0.1', 1883)
client.subscribe('/detect/output', qos=1)
client.loop_forever()
