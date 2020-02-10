import sys
sys.path.append('../')

from upyiot.comm.Messaging.MessageSpecification import MessageSpecification
from umqtt.simple import MQTTClient

try:
    import utime as time
except:
    import time

try:
    import uos as os
except:
    import os

import ujson as json


MessageSpecs = set()
MsgCount = 0
_MsgListFile = None
_MsgList = {}
_BaseDir = "./"


def ComposePath(base, type, subtype):
    return base + "/" + str(type) + "." + str(subtype)


def SplitTopic(topic):
    return topic.split('/')


def MqttMsgRecvCallback(topic, message):
    global MsgCount
    global _BaseDir

    topic = topic.decode('utf-8')
    topic_lvls = SplitTopic(topic)

    print("[MsgClient] Received message {} on topic {}".format(message, topic))
    for spec in MessageSpecs:
        spec_topic_lvls = SplitTopic(spec.Url)
        print(spec_topic_lvls)
        if spec_topic_lvls[2] == topic_lvls[2]:
            file_path = ComposePath(_BaseDir, spec.Type, spec.Subtype) + "/" + \
                        topic_lvls[1] + "_" + str(MsgCount) + ".json"
            print("[MsgClient] Writing message to file {}".format(file_path))
            f = open(file_path, "w")
            f.write(message)
            f.close()
            MsgCount += 1
            return
    print("[MsgClient] Topic {} not supported.".format(topic))


def main(argv):
    ID = 'server_node'
    BROKER = '192.168.0.103'
    PORT = 1883

    global _MsgListFile
    global _MsgList
    global _BaseDir

    _MsgListFile = argv[0]
    print(_MsgListFile)

    _BaseDir = argv[1]
    print(_BaseDir)

    msg_file = open(_MsgListFile, 'r')
    msg_file_str = msg_file.read()
    print(msg_file_str)
    msg_file.close()

    _MsgList = json.loads(msg_file_str)

    for msg_entry in _MsgList.keys():
        print(msg_entry)
        msg_spec = MessageSpecification.CreateFromFile(_MsgList[msg_entry]["spec"])
        print(msg_spec)
        MessageSpecs.add(msg_spec)

        output_dir = ComposePath(_BaseDir, msg_spec.Type, msg_spec.Subtype)
        print("Creating folder: {}".format(output_dir))
        try:
            os.mkdir(output_dir)
        except OSError:
            print("Could not create folder")

    mqtt_client = MQTTClient(ID, BROKER, PORT)
    mqtt_client.set_callback(MqttMsgRecvCallback)
    mqtt_client.connect()

    for spec in MessageSpecs:
        print("Subscribing to: {}".format(spec.Url))
        mqtt_client.subscribe(spec.Url)

    while True:
        while mqtt_client.check_msg() is None:
            time.sleep(3)


if __name__ == '__main__':
    main(sys.argv[1:])
