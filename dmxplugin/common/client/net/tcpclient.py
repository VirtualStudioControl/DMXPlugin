from threading import Thread, Lock
import socket
from typing import Optional, Callable

from dmxplugin.common.client.net.clientprotocol import createHello, handleMessage
from virtualstudio.common.logging import logengine
from virtualstudio.common.tools.bytetools import getInt


class TCPClient(Thread):

    def __init__(self, address="127.0.0.1", port=4300, username="", password="", onAuthenticated =None):
        super().__init__()
        self.isConnected = False
        self.address = address
        self.port = port

        self.username: str = username
        self.password: str = password

        self.sock: socket.socket = None
        self.timeout: Optional[float] = None
        self.running = False

        self.onAuth: Optional[Callable[[], None]] = onAuthenticated

        self.sendLock = Lock()

        self.logger = logengine.getLogger()

    def __str__(self):
        return "TCP Client connected to {}@{}:{}".format(self.username, self.address, str(self.port))

    def setTimeout(self, timeout: Optional[float]):
        self.timeout = timeout
        if self.sock is not None:
            self.sock.settimeout(timeout)

    def requestStop(self):
        self.running = False

    def run(self) -> None:
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.logger.debug("Connectiong to {}:{}".format(self.address, self.port))
        try:
            self.sock.connect((self.address, self.port))
            self.sendMessage(createHello(self.username))
            while self.running:
                try:
                    length = self.sock.recv(4)
                    while len(length) < 4:
                        length += self.sock.recv(4 - len(length))  # 16 kb buffer
                    pkglen = getInt(length, start=0)
                    data = bytearray()
                    while len(data) < pkglen:
                        data += self.sock.recv(pkglen - len(data))

                    self.logger.debug("Message Recieved: {:08X} {}".format(getInt(length, start=0), str(data)))
                    self.onMessageRecv(data)
                except:
                    pass

        except ConnectionAbortedError:
            pass # Socket closed by another thread
        except Exception as ex:
            self.logger.error(ex)
        finally:
            self.isConnected = False
            self.running = False
            self.sock.close()
            self.sock = None

    def onAuthenticated(self):
        self.isConnected = True
        if self.onAuth is not None:
            self.onAuth()

    def onMessageRecv(self, message: bytes):
        handleMessage(self, message)

    def sendMessage(self, message: bytes):
        if self.sock is not None:
            self.sendLock.acquire()
            try:
                self.logger.debug("Sending Message")
                self.sock.sendall(message)
            finally:
                self.sendLock.release()

    def closeConnection(self):
        self.isConnected = False
        self.sock.close()
