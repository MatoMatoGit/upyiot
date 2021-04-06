from upyiot.comm.Messaging.MessageSpecification import MessageSpecification
from upyiot.comm.Messaging.Message import Message
from upyiot.comm.Messaging.MessageTemplate import MessageTemplate
from upyiot.comm.Messaging.MessageBuffer import MessageBuffer
from upyiot.middleware.SubjectObserver.SubjectObserver import Subject
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from upyiot.system.ExtLogging import ExtLogging

from micropython import const
import utime

RECEIVE_MESSAGES_ENABLED = 0


class MessageExchangeExceptionMessageSize(Exception):
    """Raised when MessageExchange is initialized with a max message size
    that exceeds the MTU defined by the used protocol. """
    def __init__(self, msg_size, mtu):
        self.MsgSize = msg_size
        self.Mtu = mtu
        msg = (" MessageExchange is initialized with a max message size {} "
               "that exceeds the MTU {} defined by the used protocol.".format(self.MsgSize, self.Mtu))
        super().__init__(msg)


class MessageExchangeService(Service):
    MSG_EX_SERVICE_MODE = Service.MODE_RUN_PERIODIC

    def __init__(self):
        self.DefaultInterval = 100
        super().__init__("MsgEx", self.MSG_EX_SERVICE_MODE, {})

    def DefaultIntervalSet(self, default_interval_sec):
        self.DefaultInterval = default_interval_sec


class MessageExchange(MessageExchangeService):

    CONNECT_RETRY_INTERVAL_SEC  = const(1)

    # Buffer sizes (number of messages).
    SEND_BUFFER_SIZE = const(1000)
    RECV_BUFFER_SIZE = const(100)

    MSG_MAP_TYPE        = const(0)
    MSG_MAP_SUBTYPE     = const(1)
    MSG_MAP_ROUTING     = const(2)
    MSG_MAP_RECV_BUFFER = const(3)
    MSG_MAP_SUBSCRIBED  = const(4)

    _Instance = None

    def __init__(self, directory, proto_obj, send_retries, msg_size_max, msg_send_limit=5):
        if msg_size_max > proto_obj.Mtu:
            raise MessageExchangeExceptionMessageSize(msg_size_max, proto_obj.Mtu)

        # Initialize the MessageExchangeService class.
        super().__init__()

        # Configure the max size of a single message. Determines buffer sizes.
        MessageTemplate.Configure(msg_size_max)

        # Configure the MessageBuffer and Message classes.
        MessageBuffer.Configure(directory)

        # Create a generic send buffer for all outgoing messages.
        self.SendMessageBuffer = MessageBuffer('send', -1, -1,
                                               MessageExchange.SEND_BUFFER_SIZE)
        self.MessageMappings = set()
        self.Protocol = proto_obj
        self.SendRetries = send_retries
        self.SendLimit = msg_send_limit
        self.ConnectionState = Subject()
        self.ConnectionState.State = False
        self.ServiceInit = False
        self.NewMessage = False  # Set to True by the receive callback on a received message.
        self.Log = ExtLogging.Create("MsgEx")

        MessageExchange._Instance = self

    @staticmethod
    def InstanceGet():
        return MessageExchange._Instance

# #### Service API ####

    def SvcInit(self):
        self._ProtocolSetup()

    def SvcRun(self):
        # Get the amount of messages queued for transmission.
        msg_count = self.SendMessageBuffer.MessageCount() \
            if self.SendMessageBuffer.MessageCount() < self.SendLimit else self.SendLimit

        self.Log.info("Messages in send-buffer: {}".format(self.SendMessageBuffer.MessageCount()))

        # Iterate through all queued messages once.
        self.Log.info("Sending {} messages".format(msg_count))
        for i in range(0, msg_count):
            self._SendMessage()

        if RECEIVE_MESSAGES_ENABLED is 1:
            self._ReceiveMessage()

        # If not all messages could be send in a single cycle due to a send limit,
        # AND a custom send interval has been defined (not default),
        # set the send interval for this cycle. The scheduler will schedule this
        # service again after the send interval.
        if self.SendMessageBuffer.MessageCount() \
                and self.Protocol.SendInterval is not self.Protocol.SEND_INTERVAL_DEFAULT:
            self.Log.info("Setting send interval: {}".format(self.Protocol.SendInterval))
            self.SvcIntervalSet(self.Protocol.SendInterval)
        else:
            self.SvcIntervalSet(self.DefaultInterval)

# ########

    def AttachConnectionStateObserver(self, observer):
        """
        Attach a connection state observer to this service. The observer is updated
        when the connection state changes. The state update argument represents the
        connection state; true = connected, false = not connected.
        :param observer: Observer to attach
        :type observer: <Observer>
        """
        self.ConnectionState.Attach(observer)

    def DetachConnectionStateObserver(self, observer):
        self.ConnectionState.Detach(observer)

    def RegisterMessageType(self, msg_spec_obj):
        # If this message can be received
        if msg_spec_obj.Direction is not MessageSpecification.MSG_DIRECTION_SEND:
            # Create receive buffer for the messages of this type.
            recv_buffer = MessageBuffer('recv', msg_spec_obj.Type, msg_spec_obj.Subtype,
                                        MessageExchange.RECV_BUFFER_SIZE)
        else:
            recv_buffer = None
        self.Log.debug("Registering message specification: {}".format(msg_spec_obj))
        # Add the new mapping to the set of mappings.
        self.MessageMappings.add((msg_spec_obj.Type, msg_spec_obj.Subtype,
                                  msg_spec_obj.Url, recv_buffer))

    def Reset(self):
        self.SendMessageBuffer.Delete()
        for msg_map in self.MessageMappings:
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_buf.Delete()

    def MessagePut(self, msg_data: dict, msg_type: int,
                   msg_subtype: int, msg_meta: dict = None) -> int:
        """
        Put a single message in the send queue (FIFO) of the Message Exchange service.
        :param msg_data: Message data
        :type msg_data: dict
        :param msg_type: Message type
        :type msg_type: int
        :param msg_subtype: Message subtype
        :type msg_subtype: int
        :param msg_meta: Message metadata (optional)
        :type msg_meta: dict
        :return:
        :rtype:
        :except
        """
        # Get the current date-time.
        self.Log.debug("Serializing message: {}".format(msg_data))
        # Serialize the message.
        Message.Serialize(msg_data, msg_meta)
        self.Log.debug("Serialized length: {}".format(len(Message.Stream().getvalue())))

        # Put the message in the send buffer, return the result value.
        return self.SendMessageBuffer.MessagePutWithType(msg_type, msg_subtype,
                                                         Message.Stream().getvalue())

    def MessageGet(self, msg_type: int, msg_subtype: int) -> dict:
        """
        Returns a received message that matches the specified type and subtype.
        :param msg_type: Message type
        :type msg_type: int
        :param msg_subtype: Message subtype
        :type msg_subtype: int
        :return: Message or {"error": <code>}.
        -3 if no message is available.
        -2 if the message spec is of type SEND.
        -1 if no message mapping exists.
        :rtype: dict
        """
        # Get the message map for the requested type.
        msg_map = self.MessageMapFromType(msg_type, msg_subtype)
        self.Log.debug("Found message map: {}".format(msg_map))
        if msg_map is not None:
            # Check if the requested type has a receive buffer.
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                # Get the message from the receive buffer.
                msg_tup = msg_buf.MessageGet()
                if msg_tup is not None:
                    # Deserialize the message data and return it to the user.
                    msg_len = msg_tup[MessageBuffer.MSG_STRUCT_LEN]
                    return Message.Deserialize(msg_tup[MessageBuffer.MSG_STRUCT_DATA][:msg_len])
                else:
                    self.Log.info("No message of type %d.%d received." % (msg_type, msg_subtype))
                    return {"error": -3}
            else:
                self.Log.error("Message type %d.%d is specified as SEND." % (msg_type, msg_subtype))
                return {"error": -2}
        else:
            self.Log.error("No message mapping for message type %d.%d" % (msg_type, msg_subtype))
        return {"error": -1}

    def MessageMapFromType(self, msg_type, msg_subtype):
        for msg_map in self.MessageMappings:
            if msg_map[MessageExchange.MSG_MAP_TYPE] is msg_type \
                    and msg_map[MessageExchange.MSG_MAP_SUBTYPE] is msg_subtype:
                return msg_map
        return None

    def MessageMapFromRoute(self, route):
        for msg_map in self.MessageMappings:
            if msg_map[MessageExchange.MSG_MAP_ROUTING] == route:
                return msg_map
        return None

# #### Private methods ####

    @staticmethod
    def _MsgRecvCallback(route, msg):
        route = route.decode('utf-8')
        data_ex = MessageExchange.InstanceGet()
        data_ex.NewMessage = True

        data_ex.Log.info("Message received with route %s" % route)
        # Get the message mapping from the route
        msg_map = data_ex.MessageMapFromRoute(route)
        if msg_map is not None:
            # Put the message string in the corresponding receive buffer.
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_buf.MessagePut(msg)
        else:
            data_ex.Log.warning("No message mapping defined for route %s" % route)

    def _ProtocolSetup(self):
        self.Log.info("Connecting to server.")
        connected = False
        retries = 0

        self.Protocol.Setup(MessageExchange._MsgRecvCallback, self.MessageMappings)

        # Try to connect to the server, if it fails retry after the specified
        # amount of retries an exception is raised.
        while connected is False and retries < self.SendRetries:
            try:
                self.Protocol.Connect()
                connected = True
                self.Log.info("Connected.")
            except OSError:
                retries += 1
                self.Log.info("Failed to connect to server. Retries left %d"
                      % (self.SendRetries - retries))
                utime.sleep(MessageExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue
        
        # Update the Connection state subject
        self.ConnectionState.State = connected
        
        if connected is False:
            self.Log.warning("Failed to connect after retries.")
            # TODO: Raise ServiceException
            return

    def _SendMessage(self):

        # Get the message tuple, and extract the mapping.
        msg_tup = self.SendMessageBuffer.MessageGet()
        msg_map = self.MessageMapFromType(msg_tup[MessageBuffer.MSG_STRUCT_TYPE],
                                          msg_tup[MessageBuffer.MSG_STRUCT_SUBTYPE])

        # If a valid mapping was found, transmit the message.
        if msg_map is not None:

            # Get the message length and call the protocol send function.
            self.Log.debug("Found message map: {}".format(msg_map))
            msg_len = msg_tup[MessageBuffer.MSG_STRUCT_LEN]

            self.Log.info("Sending message of length {}".format(msg_len))
            self.Protocol.Send(msg_map, msg_tup[MessageBuffer.MSG_STRUCT_DATA][:msg_len], msg_len)

        else:
            # TODO: Raise an exception here. This should not happen.
            self.Log.error("No map defined for message type %d.%d" %
                             (msg_tup[MessageBuffer.MSG_STRUCT_TYPE],
                              msg_tup[MessageBuffer.MSG_STRUCT_SUBTYPE]))

    def _ReceiveMessage(self):
        self.Log.info("Checking for received messages.")
        while True:
            # Check for any received messages. The 'message received'-callback is called if a message
            # was received.
            self.Protocol.Receive()
            if self.NewMessage is False:
                break
            self.NewMessage = False
