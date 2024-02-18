from warnings import warn

from navel import _messages

NAVEL_MOTION_SOCKET = "/run/bodyd/motion.sock"
NAVEL_PERCEPTION_SOCKET = "/run/bodyd/vision.sock"
NAVEL_SPEECH_SOCKET = "/run/bodyd/speech.sock"


class Motion(_messages.MotionMessenger):
    """Send messages to motion socket.

    This class is able to send protobuf messages via a unix
    domain socket (UDS). As soon as the object is created it will
    attempt to connect to the socket. If socket connection is successful,
    methods can be used to send messages. Each message is  converted
    to a protobuf format before being sent to the motion socket.

    Args:
        socket_name (str): Name of motion socket to connect too.
    """

    def __init__(self, socket_name=NAVEL_MOTION_SOCKET):
        super().__init__(socket_name)


class Speech(_messages.SpeechMessenger):
    """Send and receive messages via speech socket

    This class is able to transceive protobuf messages via a unix
    domain socket (UDS). As soon as the object is created it will
    attempt to connect to the socket. If socket connection is successful,
    methods can be used to send messages. Each message is converted
    into a protobuf format before being sent to the speech socket.

    It also provides a mechanism for registerig bookmarks in the text.
    This is run asynchronously as messages could arrive at any point in
    time. Read messages are accessed using callback functions.
    If there are no relevent callback functions then messages will be thrown
    away to keep buffer clear. See valid keys to see what callbacks are
    supported.

    If the object where data is stored by callback functions is to be accessed
    by any other threads, steps must be taken to make it threadsafe.

    Args:
        socket_name (str, optional): Name of the socket to connect to.
            Defaults to NAVEL_SPEECH_SOCKET
    """

    def __init__(self, socket_name=NAVEL_SPEECH_SOCKET):
        super().__init__(socket_name)


class Perception(_messages.PerceptionMessenger):
    """Receive messages from perception socket

    This class is able to receive protobuf messages via a unix
    domain socket (UDS). As soon as the object is created it will
    attempt to connect to the socket. If socket connection is successful,
    methods can be used to receive messages. Each message is converted
    from a protobuf format and into a navel data struct.

    Args:
        socket_name (str, optional): Name of the socket to connect to.
            Defaults to NAVEL_PERCEPTION_SOCKET
    """

    def __init__(self, socket_name=NAVEL_PERCEPTION_SOCKET):
        super().__init__(socket_name)


class Robot(Motion, Perception, Speech):
    """Send commands and receive data from robot.

    This class can be used to send motion or speech commands, register
    callbacks for bookmarks, fetch the latest perception data, and set
    robot configuration values. It should always be used as a context
    manager (inside a ``with`` block).
    """

    def __init__(self):
        Motion.__init__(self, None)
        Perception.__init__(self, None)
        Speech.__init__(self, None)
        self._sockets = {}
        self._active = False

    def __enter__(self):
        self._active = True

        return self

    def __exit__(self, *args):
        self._active = False
        for socket in self._sockets.values():
            socket.disconnect()

        self._sockets = {}

    @property
    def _motion_sock(self):
        return self._get_or_init_prop(NAVEL_MOTION_SOCKET)

    @property
    def _perc_sock(self):
        return self._get_or_init_prop(NAVEL_PERCEPTION_SOCKET)

    @property
    def _speech_sock(self):
        return self._get_or_init_prop(NAVEL_SPEECH_SOCKET)

    def _get_or_init_prop(self, name):
        if not self._active:
            raise RuntimeError(
                'Robot communication should only be done inside "with" block'
            )
        if name not in self._sockets:
            self._sockets[name] = _messages.ProtobufSocket(name)
        return self._sockets[name]


def run(app):
    """Run a coroutine with a robot connection as the only parameter.

    This is used to start navel "apps". This function is only provided
    as a shorthand for the most common use-case, calling the run
    method on any of the connection classes accomplishes the same goal.
    """

    with Robot() as robot:
        warn(
            "Function .run() is deprecated and will be removed in a future version. Please check the getting started guide for the recommended way to start coroutines.",
            DeprecationWarning,
            stacklevel=2,
        )
        return robot.run(app)
