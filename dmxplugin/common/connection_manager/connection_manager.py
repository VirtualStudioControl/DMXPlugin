from typing import Dict, Any

from dmxplugin.common.connection_manager.connection_handler import ConnectionHandler
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.account_manager.account_info import AccountInfo
from virtualstudio.common.logging import logengine

CONNECTIONS: Dict[str, ConnectionHandler] = {}

logger = logengine.getLogger()


def initialise():
    account_manager.registerAccountChangeCallback(reconnectClient)


def createClient(account: AccountInfo):
    logger.debug("Creating new Client")
    connectionHandler = ConnectionHandler(account)
    CONNECTIONS[account.uuid] = connectionHandler
    connectionHandler.connect()


def reconnectClient(uuid: str):
    logger.debug("Trying to reconnect")
    if uuid in CONNECTIONS:
        CONNECTIONS[uuid].requestClose()
        del CONNECTIONS[uuid]
        logger.debug("Connection Deleted")


def sendMessage(account_uuid, message: bytes):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)

    CONNECTIONS[account_uuid].sendMessage(message)

#region DMX


def updateDMXFrameBuffer(account_uuid):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)
    CONNECTIONS[account_uuid].updateDMXFrameBuffer()


def setChannel(account_uuid, universe, channel, data):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)
    CONNECTIONS[account_uuid].setChannel(universe, channel, data)


def setChannelSilent(account_uuid, universe, channel, data):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)
    CONNECTIONS[account_uuid].setChannelSilent(universe, channel, data)


def getChannel(account_uuid, universe, channel):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)
    return CONNECTIONS[account_uuid].getChannel(universe, channel)


def sendFrameToServer(account_uuid, universe):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)
    CONNECTIONS[account_uuid].sendFrameToServer(universe)


def setFrame(account_uuid, universe, data):
    if account_uuid not in CONNECTIONS:
        account = account_manager.getAccountByUUID(account_uuid)
        createClient(account)
    CONNECTIONS[account_uuid].setFrame(universe, data)

#endregion