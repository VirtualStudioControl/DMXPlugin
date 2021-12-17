import asyncio
import json
from threading import Lock
from time import sleep
from typing import Optional

from dmxplugin.common import datatools
from dmxplugin.common.client.net import clientprotocol
from dmxplugin.common.client.net.constants import GET_CURRENT_DMX_FRAME, GET_CURRENT_DMX_SCENE
from dmxplugin.common.client.net.tcpclient import TCPClient
from dmxplugin.common.device.device_manager import DeviceManager
from dmxplugin.common.dmx.dmx_buffer import DMXBuffer
from dmxplugin.common.interfaces.IFrameProvider import IFrameProvider
from virtualstudio.common.account_manager.account_info import AccountInfo

from aiohttp.client_exceptions import ClientConnectorError, ClientError

from virtualstudio.common.logging import logengine


class ConnectionHandler:
    def __init__(self, accountData: AccountInfo):
        super(ConnectionHandler, self).__init__()
        self.accountData: AccountInfo = accountData
        self.client: Optional[TCPClient] = None
        self.clientLock = Lock()

        self.sendQueue = []
        self.logger = logengine.getLogger()

        self.dmx_buffer = DMXBuffer()
        self.device_manager = DeviceManager(self)

    def isConnected(self) -> bool:
        return self.client is not None and self.client.isConnected

    def connect(self):
        with self.clientLock:
            self.client = TCPClient(address=self.accountData.server, port=self.accountData.port,
                                    username=self.accountData.username, password=self.accountData.password,
                                    onAuthenticated=self.onAuthenticated)

            self.client.start()
            sleep(.5)
            for message in self.sendQueue:
                self.client.sendMessage(message=message)
            self.sendQueue.clear()

    def onAuthenticated(self):
        self.sendMessage(clientprotocol.createGet(datatools.messageID(), GET_CURRENT_DMX_FRAME, self.setBufferData))
        self.sendMessage(clientprotocol.createGet(datatools.messageID(), GET_CURRENT_DMX_SCENE, self.parseDMXScene))

    def parseDMXScene(self, client, value):
        self.logger.info(value)
        dmxscene = json.loads(value)
        self.logger.info(value)
        self.device_manager.fromDict(dmxscene)

    def setBufferData(self, client, data):
        self.dmx_buffer.loadData(data)

    def requestClose(self):
        self.client.requestStop()

    def sendMessage(self, data: bytes):
        if not self.isConnected():
            self.sendQueue.append(data)
            return
        self._sendMsgInternal(data)

    def _sendMsgInternal(self, data: bytes):
        if not self.isConnected():
            self.connect()

        try:
            with self.clientLock:
                self.client.sendMessage(data)
        except Exception as ex:
            self.logger.error(ex)
            self.logger.info("Attempting Reconnect")
            self.connect()
    #region DMX Specific functions

    def updateDMXFrameBuffer(self):
        self.sendMessage(clientprotocol.createGet(datatools.messageID(), GET_CURRENT_DMX_FRAME, self.setBufferData))

    def setChannel(self, universe, channel, data):
        self.dmx_buffer.setChannel(universe, channel, data)
        self.sendMessage(clientprotocol.createDMXMessage(False, universe, self.dmx_buffer.getFrame(universe)))

    def setChannelSilent(self, universe, channel, data):
        self.dmx_buffer.setChannel(universe, channel, data)

    def getChannel(self, universe, channel):
        return self.dmx_buffer.getChannel(universe, channel)

    def sendFrameToServer(self, universe):
        self.sendMessage(clientprotocol.createDMXMessage(False, universe, self.dmx_buffer.getFrame(universe)))

    def setFrameSilent(self, universe, data):
        self.dmx_buffer.setFrame(universe, data)

    def setFrame(self, universe, data):
        self.setFrameSilent(universe, data)
        self.sendFrameToServer(universe)

    def setAllUniverses(self):
        for universe in self.dmx_buffer.listUniverses():
            self.sendFrameToServer(universe)

    #endregion