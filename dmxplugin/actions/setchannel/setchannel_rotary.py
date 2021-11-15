from dmxplugin.actions.setchannel.setchannel import ADDITIONAL_CONTROLS, ACCOUNT_COMBO, UNIVERSE_SPIN, buildChannels
from dmxplugin.common.connection_manager import connection_manager
from dmxplugin.common.uitools import ensureAccountComboBox, setAccountComboBox
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.structs.action.rotary_encoder_action import RotaryEncoderAction


class RotarySetChannelAction(RotaryEncoderAction):

    #region handlers

    def onLoad(self):
        self.uuid_map = []
        self.value = 0
        self.displayValue = 0
        self.account_id = ""


    def onAppear(self):
        self.setGUIParameter(ADDITIONAL_CONTROLS, "currentIndex", 0)
        account_manager.registerAccountChangeCallback(self.accountChangedCB)
        self.uuid_map = ensureAccountComboBox(self, ACCOUNT_COMBO)

        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None:
            self.account_id = self.uuid_map[index]
            self.initAccount()

        self.setLEDRingValue(self.displayValue)

    def initAccount(self):
        connection_manager.updateDMXFrameBuffer(self.account_id)

    def onDisappear(self):
        pass

    def onSettingsGUIAppear(self):
        pass

    def onSettingsGUIDisappear(self):
        pass

    def onParamsChanged(self, parameters: dict):
        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None:
            self.account_id = self.uuid_map[index]
            connection_manager.updateDMXFrameBuffer(self.account_id)

    #endregion

    #region Action Management

    def accountChangedCB(self, uuid):
        if self.account_id is not None:
            self.uuid_map = setAccountComboBox(self, "account_combo")
            index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
            if index is not None and index != uuid:
                self.account_id = self.uuid_map[index]
                self.initAccount()

    #endregion

    # region Hardware Event Handlers

    def onKeyDown(self):
        pass

    def onKeyUp(self):
        pass

    def onRotate(self, value: int):
        self.value += (value - self.displayValue)
        self.value = min(0xff, max(self.value, 0))
        self.displayValue = (self.value // 2) + 1
        self.setLEDRingValue(self.displayValue)
        if self.account_id == "":
            return

        defaultUniverse = self.getGUIParameter(UNIVERSE_SPIN, "value")
        channels = buildChannels(self)

        for channel in channels:
            connection_manager.setChannelSilent(self.account_id, defaultUniverse, channel, self.value)
        connection_manager.sendFrameToServer(self.account_id, defaultUniverse)

    # endregion