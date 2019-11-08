import sys
sys.path.append('../')

from upyiot.module.Messaging.MessageSpecification import MessageSpecification
from umqtt.simple import MQTTClient

try:
    import utime as time
except:
    import time

try:
    import uos as os
except:
    import os

MessageSpecs = set()
OUTPUT_DIR = "./"
MsgCount = 0


def ComposePath(base, type, subtype):
    return base + "/" + str(type) + "." + str(subtype)


def MqttMsgRecvCallback(topic, message):
    global MsgCount

    topic = topic.decode('utf-8')

    print("[MsgClient] Received message {} on topic {}".format(message, topic))
    for spec in MessageSpecs:
        if spec.Url == topic:
            file_path = ComposePath(OUTPUT_DIR, spec.Type, spec.Subtype) + "/3f7e12c9_" + str(MsgCount)
            print("[MsgClient] Writing message to file {}".format(file_path))
            f = open(file_path, "w")
            f.write(message)
            f.close()
            MsgCount += 1
            return
    print("[MsgClient] Topic {} not supported.".format(topic))


def main(msg_spec_file):
    ID = 'server_node'
    BROKER = '192.168.0.103'
    PORT = 1883

    msg_spec = MessageSpecification.CreateFromFile(msg_spec_file)
    print(msg_spec)
    MessageSpecs.add(msg_spec)

    mqtt_client = MQTTClient(ID, BROKER, PORT)
    mqtt_client.set_callback(MqttMsgRecvCallback)
    mqtt_client.connect()

    for spec in MessageSpecs:
        mqtt_client.subscribe(spec.Url)

        output_dir = ComposePath(OUTPUT_DIR, spec.Type, spec.Subtype)
        try:
            os.mkdir(output_dir)
        except OSError:
            print("Could not create folder")

    while True:
        mqtt_client.check_msg()
        time.sleep(5)


if __name__ == '__main__':
    main("./ExampleMessage.json")
