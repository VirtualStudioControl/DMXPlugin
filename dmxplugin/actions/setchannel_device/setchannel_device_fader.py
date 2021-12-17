from dmxplugin.actions.setchannel_device.setchannel_device import ADDITIONAL_CONTROLS, ACCOUNT_COMBO, DEVICE_COMBO, \
    CHANNEL_COMBO
from dmxplugin.common.connection_manager import connection_manager
from dmxplugin.common.device.dmxdevice import DMXDevice
from dmxplugin.common.uitools import ensureAccountComboBox, setAccountComboBox
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.structs.action.fader_action import FaderAction


class FaderSetChannelDeviceAction(FaderAction):

    #region handlers

    def onLoad(self):
        self.uuid_map = []
        self.value = 0
        self.account_id = ""

        self.deviceList = []


    def onAppear(self):
        self.setGUIParameter(ADDITIONAL_CONTROLS, "currentIndex", 0)
        account_manager.registerAccountChangeCallback(self.accountChangedCB)
        self.uuid_map = ensureAccountComboBox(self, ACCOUNT_COMBO)

        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None:
            self.account_id = self.uuid_map[index]
            self.initAccount()

    def initAccount(self):
        connection_manager.updateDMXFrameBuffer(self.account_id)
        connection_manager.getDMXDeviceManager(self.account_id).addCallback(self.updateDMXDeviceList)
        self.updateDMXDeviceList()

    def deinitAccount(self):
        connection_manager.getDMXDeviceManager(self.account_id).removeCallback(self.updateDMXDeviceList)

    def updateDMXDeviceList(self):
        self.deviceList = connection_manager.getDMXDeviceManager(self.account_id).getDMXDevices()

        devNames = []
        for dev in self.deviceList:
            devNames.append("{} [Universe {}, Channel {}]".format(dev.name, dev.universe, dev.baseChannel+1))

        self.setGUIParameter(DEVICE_COMBO, "itemTexts", devNames)
        devn = self.getGUIParameter(DEVICE_COMBO, "currentText")
        if devn in devNames:
            self.setGUIParameter(DEVICE_COMBO, "currentIndex", devNames.index(devn))
        else:
            if len(devNames) > 0:
                self.setGUIParameter(DEVICE_COMBO, "currentText", devNames[0])
            self.setGUIParameter(DEVICE_COMBO, "currentIndex", 0)

        self.setChannelBox(self.getGUIParameter(DEVICE_COMBO, "currentIndex"))

    def setChannelBox(self, index: int):
        if len(self.deviceList) <= 0:
            return

        dev = self.deviceList[index]

        self.setGUIParameter(CHANNEL_COMBO, "itemTexts", dev.channelTypes)

        chann = self.getGUIParameter(CHANNEL_COMBO, "currentText")
        if chann in dev.channelTypes:
            self.setGUIParameter(CHANNEL_COMBO, "currentIndex", dev.channelTypes.index(chann))
        else:
            self.setGUIParameter(CHANNEL_COMBO, "currentText", dev.channelTypes[0])
            self.setGUIParameter(CHANNEL_COMBO, "currentIndex", 0)

    def onDisappear(self):
        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None:
            self.account_id = self.uuid_map[index]
            self.deinitAccount()

    def onSettingsGUIAppear(self):
        pass

    def onSettingsGUIDisappear(self):
        pass

    def onParamsChanged(self, parameters: dict):
        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None:
            self.account_id = self.uuid_map[index]
            connection_manager.updateDMXFrameBuffer(self.account_id)

        devIdx = self.getGUIParameter(DEVICE_COMBO, "currentIndex")
        if devIdx is not None:
            self.setChannelBox(devIdx)

    #endregion

    #region Action Management

    def accountChangedCB(self, uuid):
        if self.account_id is not None:
            self.deinitAccount()
            self.uuid_map = setAccountComboBox(self, "account_combo")
        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None and index != uuid:
            self.account_id = self.uuid_map[index]
            self.initAccount()

    def getDevice(self) -> DMXDevice:
        devIdx = self.getGUIParameter(DEVICE_COMBO, "currentIndex")
        if devIdx is not None and len(self.deviceList) > 0:
            return self.deviceList[devIdx]

    #endregion

    # region Hardware Event Handlers

    def onTouchStart(self):
        pass

    def onTouchEnd(self):
        pass

    def onMove(self, value):

        device = self.getDevice()
        channel = self.getGUIParameter(CHANNEL_COMBO, "currentText")

        device.setChannel(channel, value*2)
        device.updateFrame()
        #for channel in channels:
        #    connection_manager.setChannelSilent(self.account_id, defaultUniverse, channel, value*2)
        #connection_manager.sendFrameToServer(self.account_id, defaultUniverse)

    # endregion
