import logging
from typing import List, Dict, Union, Callable

from dmxplugin.common.tools.mapping_tools import rgb_to_rgbw, rgbw_to_rgb, byte_to_dimmer_range, dimmer_range_to_byte
from virtualstudio.common.logging import logengine

CHANNEL_TYPE_UNKNOWN = "UNKNOWN"

CHANNEL_TYPE_RED = "RED"
CHANNEL_TYPE_GREEN = "GREEN"
CHANNEL_TYPE_BLUE = "BLUE"
CHANNEL_TYPE_WHITE = "WHITE"
CHANNEL_TYPE_AMBER = "AMBER"
CHANNEL_TYPE_UV = "UV"

CHANNEL_TYPE_PAN = "PAN"
CHANNEL_TYPE_PAN_FINE = "PAN_FINE"
CHANNEL_TYPE_TILT = "TILT"
CHANNEL_TYPE_TILT_FINE = "TILT_FINE"

CHANNEL_TYPE_XYSPEED = "XYSPEED"
CHANNEL_TYPE_DIMMER = "DIMMER"
CHANNEL_TYPE_COLOR_MODE = "COLOR_MODE"
CHANNEL_TYPE_COLOR_JUMP_SPEED = "COLOR_SPEED"
CHANNEL_TYPE_STROBO = "STROBO"
CHANNEL_TYPE_CUSTOM = "CUSTOM"
CHANNEL_TYPE_RESET = "RESET"

logger = logengine.getLogger()

class DMXDevice:

    def __init__(self, universe: int, baseChannel: int, channelCount: int, name: str = "", devtype: str = "", channelTypes=None,
                 constantChannels: Dict[Union[str, int], int]=None, dimmerRange=None, device_manager=None):
        super(DMXDevice, self).__init__()
        if dimmerRange is None:
            dimmerRange = [0, 1, 254, 255]
        if constantChannels is None:
            constantChannels = {}
        if channelTypes is None:
            channelTypes = []

        self.device_manager = device_manager

        self.universe = universe
        self.baseChannel = baseChannel
        self.channelCount = channelCount
        self.name = name
        self.deviceType = devtype

        self.channelTypes = [CHANNEL_TYPE_UNKNOWN] * self.channelCount

        for i in range(len(channelTypes)):
            if i >= self.channelCount:
                break
            if channelTypes[i] is not None:
                self.channelTypes[i] = channelTypes[i]

        self.constantChannels = constantChannels

        self.dimmerRange = dimmerRange

        self.parent = None
        self.children = []

        self.updateFunctions: List[Callable[[], None]] = []

        self.updateTimer = None

    #region Update System

    def addUpdateFunction(self, func: Callable[[], None]):
        self.updateFunctions.append(func)

    def removeUpdateFuction(self, func):
        self.updateFunctions.remove(func)

    def clearUpdateFunctions(self):
        self.updateFunctions.clear()

    def updateDevice(self):
        for update in self.updateFunctions:
            try:
                update()
            except Exception as ex:
                logger.error("An Error occured during calling frame update functions")
                logger.exception(ex)

    #endregion

    #region Parent / Child

    def setParent(self, parent):
        if self.parent is not None:
            self.parent.removeChild(self)

        self.parent = parent

        if self.parent is not None:
            self.parent.addChild(self)

    def hasParent(self):
        return self.parent is not None

    def hasChildren(self):
        return len(self.children) > 0

    def addChild(self, child):
        if child not in self.children:
            self.children.append(child)

    def removeChild(self, child):
        if child in self.children:
            self.children.remove(child)

    #endregion

    #region LowLevel

    def __setValue(self, channel, value):
        for child in self.children:
            child.__setValue(channel, value)

        if self.universe < 0:
            return

        if self.baseChannel < 0:
            return

        if type(channel) == str:
            channel = self.getChannelIDByType(channel)

        if channel < 0:
            return

        if self.baseChannel + channel >= 512:
            return

        if value < 0:
            value = 0
        elif value > 255:
            value = 255

        self.device_manager.handler.setChannelSilent(self.universe, channel + self.baseChannel, value)

    def __getValue(self, channel) -> int:
        val = -1
        if self.hasChildren():
            val = self.children[0].__getValue(channel)

        if self.universe < 0:
            return val

        if type(channel) == str:
            channel = self.getChannelIDByType(channel)

        if channel < 0:
            return val

        return self.device_manager.handler.getChannel(self.universe, channel + self.baseChannel)

    def __enforceConstantChannels(self):
        for child in self.children:
            child.__enforceConstantChannels()

        if self.universe < 0:
            return

        for channel in self.constantChannels:
            self.__setValue(channel, self.constantChannels[channel])

    def __updateFrame(self, setFrame=True):
        for child in self.children:
            child.__updateFrame(setFrame=False)

        if self.universe >= 0:
            self.__enforceConstantChannels()

        if setFrame:
            logger.info("UPDATING DMX DEVICE FRAMES, SET FRAME: {}".format(setFrame))
            return self.device_manager.handler.setAllUniverses()
        return None

    def getChannelIDByType(self, channelType: str):
        if self.hasChannelType(channelType):
            return self.channelTypes.index(channelType)

        try:
            return int(channelType.strip())
        except:
            return -1

    def hasChannelType(self, channelType):
        return channelType in self.channelTypes

    def setChannel(self, channel, value) -> bool:
        """
        Sets the value of the given Channel

        :param channel: index of the given channel
        :param value: new value for the given channel
        :return: True if successfull, False otherwise
        """
        self.__setValue(channel, value)
        return True

    def getChannel(self, channel) -> int:
        """
        Gets the value of the given channel

        :param channel: index of the channel to query
        :return: the value of the given channel
        """

        return self.__getValue(channel)

    def setInt16(self, channel_rough, channel_fine, value) -> bool:
        """
        Puts a 16-bit value into the devices data block

        :param channel_rough: channel for the upper 8 bits
        :param channel_fine: channel for the lower 8 bit
        :param value: 16-bit value to put into the device data block
        :return: True if success, False otherwise
        """

        if value < 0:
            value = 0
        elif value > 2 ** 16:
            value = 2 ** 16
        self.__setValue(channel_rough, (value >> 8) & 0xff)
        self.__setValue(channel_fine, (value >> 0) & 0xff)
        return True

    def getInt16(self, channel_rough, channel_fine):
        """
        Returns the 16-bit value of the device
        :param channel_rough: channel of the upper 8 bit
        :param channel_fine: channel of the lower 8 bit
        :return: a 16 bit Value
        """
        return (self.__getValue(channel_rough) << 8) | (self.__getValue(channel_fine))

    def updateFrame(self):

        self.__updateFrame()

    #endregion

    #region HighLevel

    def hasColor(self):
        return self.hasChannelType(CHANNEL_TYPE_RED)

    def hasUV(self):
        return self.hasChannelType(CHANNEL_TYPE_UV)

    def hasDimmer(self):
        return self.hasChannelType(CHANNEL_TYPE_DIMMER)

    def hasPan(self):
        return self.hasChannelType(CHANNEL_TYPE_PAN)

    def hasTilt(self):
        return self.hasChannelType(CHANNEL_TYPE_TILT)

    def hasSpeed(self):
        return self.hasChannelType(CHANNEL_TYPE_XYSPEED)

    def setColorRGB(self, red, green, blue):
        if self.universe < 0:
            for child in self.children:
                child.setColorRGB(red, green, blue)
            return

        if self.hasChannelType(CHANNEL_TYPE_WHITE):
            red, green, blue, white = rgb_to_rgbw(red, green, blue)
            self.setChannel(CHANNEL_TYPE_WHITE, white)

        self.setChannel(CHANNEL_TYPE_RED, red)
        self.setChannel(CHANNEL_TYPE_GREEN, green)
        self.setChannel(CHANNEL_TYPE_BLUE, blue)

        self.__updateFrame()

    def getColor(self):
        if self.universe < 0:
            if self.hasChildren():
                return self.children[0].getColor()

        white = 0

        if self.hasChannelType(CHANNEL_TYPE_WHITE):
            white = self.getChannel(CHANNEL_TYPE_WHITE)

        return rgbw_to_rgb(self.getChannel(CHANNEL_TYPE_RED),
                           self.getChannel(CHANNEL_TYPE_GREEN),
                           self.getChannel(CHANNEL_TYPE_BLUE),
                           white)

    def setUV(self, value):
        if self.universe < 0:
            for child in self.children:
                child.setUV(value)
            return

        if self.hasChannelType(CHANNEL_TYPE_UV):
            self.setChannel(CHANNEL_TYPE_UV, value)
            self.__updateFrame()

    def getUV(self):
        if self.universe < 0:
            if self.hasChildren():
                return self.children[0].getUV()
        return self.getChannel(CHANNEL_TYPE_UV)

    def setDimmer(self, value):
        if self.universe < 0:
            for child in self.children:
                child.setDimmer(value)
            return

        if self.hasChannelType(CHANNEL_TYPE_DIMMER):
            self.setChannel(CHANNEL_TYPE_DIMMER, byte_to_dimmer_range(value, self.dimmerRange))
            self.__updateFrame()

    def getDimmer(self):
        if self.universe < 0:
            if self.hasChildren():
                return self.children[0].getDimmer()
        return dimmer_range_to_byte(self.getChannel(CHANNEL_TYPE_DIMMER), self.dimmerRange)

    def setPanTiltSpeed(self, value):
        if self.universe < 0:
            for child in self.children:
                child.setPanTiltSpeed(value)
            return

        if self.hasChannelType(CHANNEL_TYPE_XYSPEED):
            self.setChannel(CHANNEL_TYPE_XYSPEED, value)
            self.__updateFrame()

    def getPanTiltSpeed(self):
        if self.universe < 0:
            if self.hasChildren():
                return self.children[0].getPanTiltSpeed()
        return self.getChannel(CHANNEL_TYPE_XYSPEED)

    def setPan(self, value):
        if self.universe < 0:
            for child in self.children:
                child.setPan(value)
            return
        if self.hasChannelType(CHANNEL_TYPE_PAN):
            if self.hasChannelType(CHANNEL_TYPE_PAN_FINE):
                self.setInt16(CHANNEL_TYPE_PAN, CHANNEL_TYPE_PAN_FINE, value)
                self.__updateFrame()
                return
            self.setChannel(CHANNEL_TYPE_PAN, (value >> 8) & 0xff)
            self.__updateFrame()

    def getPan(self):
        if self.universe < 0:
            if self.hasChildren():
                return self.children[0].getPan()

        if self.hasChannelType(CHANNEL_TYPE_PAN_FINE):
            return self.getInt16(CHANNEL_TYPE_PAN, CHANNEL_TYPE_PAN_FINE)
        return self.getChannel(CHANNEL_TYPE_PAN) << 8

    def setTilt(self, value):
        if self.universe < 0:
            for child in self.children:
                child.setTilt(value)
            return
        if self.hasChannelType(CHANNEL_TYPE_TILT):
            if self.hasChannelType(CHANNEL_TYPE_TILT_FINE):
                self.setInt16(CHANNEL_TYPE_TILT, CHANNEL_TYPE_TILT_FINE, value)
                self.__updateFrame()
                return
            self.setChannel(CHANNEL_TYPE_TILT, (value >> 8) & 0xff)
            self.__updateFrame()

    def getTilt(self):
        if self.universe < 0:
            if self.hasChildren():
                return self.children[0].getTilt()

        if self.hasChannelType(CHANNEL_TYPE_TILT_FINE):
            return self.getInt16(CHANNEL_TYPE_TILT, CHANNEL_TYPE_TILT_FINE)
        return self.getChannel(CHANNEL_TYPE_TILT) << 8


    #endregion

    def toDict(self):

        cds = []
        for child in self.children:
            cds.append(child.toDict())

        return {
            "name": self.name,
            "deviceType": self.deviceType,
            "universe": self.universe,
            "baseChannel": self.baseChannel,
            "channelCount": self.channelCount,
            "channelTypes": self.channelTypes,
            "constantChannels": self.constantChannels,
            "dimmerRange": self.dimmerRange,
            "childs": cds
        }

def fromDict(values, parent=None, device_manager=None):
    dev = DMXDevice(universe=values["universe"], baseChannel=values["baseChannel"], channelCount=values["channelCount"],
                    name=values["name"], devtype=values["deviceType"], channelTypes=values["channelTypes"],
                    constantChannels=values["constantChannels"], dimmerRange=values["dimmerRange"],
                    device_manager=device_manager)

    if parent is not None:
        dev.setParent(parent)

    for child in values["childs"]:
        fromDict(child, dev, device_manager=device_manager)

    return dev
