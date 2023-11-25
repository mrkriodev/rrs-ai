import multiprocessing
import socket
import os
import numpy
import base64
import time
from datetime import datetime
import os
import pickle
import numpy as np
import paho.mqtt.publish as publish
from docopt import docopt
import paho.mqtt.client as paho
from ultralytics import YOLO
from ftplib import FTP
import ast

help = """Server (Cameras reciever).

Usage:
  frame_server.py [--host=<hs>] [--port=<ps>] [--ftp-host=<fs>] [--remote_host=<rh>]
  frame_server.py (-h | --help)
  frame_server.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  --host=<hs>           Host for server                            [default: 127.0.0.1].
  --port=<ps>           Port for server                            [default: 9090]. 
  --ftp-host=<fs>       FTP HOST                                   [default: 127.0.0.1].
  --remote_host=<rh>    MQTT broker host                           [default: 127.0.0.1].
"""

'''TO DO 
Вынести в окружение
'''
fcc_code = {"bricks": "8 12 201 01 20 5",
            "grunt": "8 11 100 00 00 0",
            "beton": "8 22 211 11 20 4",
            "wood": "8 12 101 01 72 4",
            "empty": "-1"}


def predict(video, model=None, distance_threshold=0.5):
    if model is None:
        raise Exception(
            "Must supply YOLOv8")

    model = YOLO(model)

    results = model.predict(
        source=video,
        conf=0.75
    )

    class_probabilities = {}
    for r in results:
        for c in r.boxes.cls:
            for p in r.boxes.conf.tolist():
                if model.names[int(c)] in class_probabilities:
                    class_probabilities[model.names[int(c)]].append(p)
                else:
                    class_probabilities[model.names[int(c)]] = [p]

    max_prob_class = max(class_probabilities, key=lambda k: max(
        class_probabilities[k], default=0.0))
    max_probability = max(class_probabilities[max_prob_class], default=0.0)

    return (max_prob_class, fcc_code[max_prob_class], max_probability)


def handle(topic, payload):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(f"process - {payload}")

    ftp = FTP(Server.FTP_USER_HOST)
    ftp.login(Server.FTP_USER_USERNAME, Server.FTP_USER_PASSWORD)

    try:
        decode = payload.decode('UTF-8')
        logger.debug("data %r at %r", topic, decode)

        dict_req = ast.literal_eval(decode)
        file = dict_req['file_path']
        id = dict_req['id']

        with open(file, 'wb') as f:
            ftp.retrbinary('RETR ' + file, f.write)

        res = predict(file, model='./best.pt')

        ans = "{ \"id\":" + str(id) + "," + "\"file_path\":" + "\"" + str(file) + "\"" + "," + \
            "\"class\":" + "\"" + str(res[0]) + "\"" + "," + "\"cat_code\":" + "\"" + str(res[1]) + "\"" + "," + \
            "\"prob\":" + str(res[2]) + "}"

        publish.single(topic='/detect/output', payload=str(ans),
                       hostname=Server.MQTT_HOST)

        os.remove(file)

    except:
        logger.exception("Problem handling request")
        ftp.close()
    finally:
        logger.debug("Exit")
        ftp.close()


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))


def on_message(client, userdata, msg):
    process = multiprocessing.Process(
        target=handle, args=(msg.topic, msg.payload))
    process.daemon = True
    process.start()


class Server(object):
    '''TO DO 
    Вынести в окружение
    '''
    FTP_USER_USERNAME = "ftpuser2"
    FTP_USER_PASSWORD = "cQCY+14q,NLCXS"
    FTP_USER_HOST = "127.0.0.1"
    MQTT_HOST = "127.0.0.1"

    def __init__(self, arguments):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = arguments['--host']
        self.port = int(arguments['--port'])
        self.mqtt_host = arguments['--remote_host']
        self.ftp_host = arguments['--ftp-host']

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        self.client = paho.Client()
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message
        self.client.connect(self.mqtt_host, 1883)
        self.client.subscribe('/detect/input', qos=1)
        self.client.loop_forever()


if __name__ == "__main__":
    arguments = docopt(help, version='Server (Predictor)')
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server(arguments)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
