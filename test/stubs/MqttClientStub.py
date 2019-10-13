

class MQTTClient:

    SubscribedTopics = set()
    PublishedMessages = {}

    def __init__(self):
        self.CbMessageReceived = None
        self.Connected = False
        return

    def set_callback(self, callback):
        self.CbMessageReceived = callback
        return

    def connect(self):
        self.Connected = True
        return

    def subscribe(self, topic):
        if self.Connected is False:
            return -1
        if topic not in MQTTClient.SubscribedTopics:
            MQTTClient.SubscribedTopics.add(topic)
        return 0

    def publish(self, topic, message):
        if self.Connected is False:
            return -1
        MQTTClient.PublishedMessages[topic] = message
        return 0

    def check_msg(self):
        for topic in MQTTClient.PublishedMessages.keys():
            if topic in MQTTClient.SubscribedTopics:
                self.CbMessageReceived(topic, MQTTClient.PublishedMessages[topic])
        MQTTClient.PublishedMessages.clear()
        return
