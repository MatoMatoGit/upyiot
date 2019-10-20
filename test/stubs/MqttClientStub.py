

class MQTTClient:

    SubscribedTopics = set()
    PublishedMessages = {}

    def __init__(self):
        self.CbMessageReceived = None
        self.Connected = False
        self.FailCount = 0
        return

# #### Test API #####

    def connect_fail_count(self, count):
        self.FailCount = count

    def is_connected(self):
        return self.Connected

    def has_callback(self):
        return self.CbMessageReceived is not None

    def has_subscription(self, topic):
        return topic in self.SubscribedTopics

# #### MQTTClient API #####

    def set_callback(self, callback):
        self.CbMessageReceived = callback
        return

    def connect(self):
        if self.FailCount is 0:
            print("[MQTTClient] Connected")
            self.Connected = True
        else:
            print("[MQTTClient] Connect failure")
            self.FailCount = self.FailCount - 1
            raise OSError

    def subscribe(self, topic):
        if self.Connected is False:
            print("[MQTTClient] Not connected; cannot subscribe to topic {}".format(topic))
            return -1
        if topic not in MQTTClient.SubscribedTopics:
            MQTTClient.SubscribedTopics.add(topic)
            print("[MQTTClient] Subscribing to topic {}".format(topic))
        else:
            print("[MQTTClient] Already subscribed to topic {}".format(topic))
        return 0

    def publish(self, topic, message):
        if self.Connected is False:
            print("[MQTTClient] Not connected; cannot publish on topic {}".format(topic))
            return -1
        MQTTClient.PublishedMessages[topic] = message
        print("[MQTTClient] Published message on topic {}".format(topic))
        return 0

    def check_msg(self):
        for topic in MQTTClient.PublishedMessages.keys():
            print("[MQTTClient] Checking topic {}".format(topic))
            if topic in MQTTClient.SubscribedTopics:
                print("[MQTTClient] Subscription: Yes")
                self.CbMessageReceived(topic, MQTTClient.PublishedMessages[topic])
            else:
                print("[MQTTClient] Subscription: No")
        MQTTClient.PublishedMessages.clear()
        print("[MQTTClient] Clearing messages")
        return
