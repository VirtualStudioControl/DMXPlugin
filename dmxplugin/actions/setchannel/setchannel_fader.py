from dmxplugin.actions.setchannel.setchannel import ADDITIONAL_CONTROLS, ACCOUNT_COMBO, UNIVERSE_SPIN, buildChannels
from dmxplugin.common.connection_manager import connection_manager
from dmxplugin.common.uitools import ensureAccountComboBox, setAccountComboBox
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.structs.action.fader_action import FaderAction


class FaderSetChannelAction(FaderAction):

    #region handlers

    def onLoad(self):
        self.uuid_map = []
        self.value = 0
        self.account_id = ""


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

    def onTouchStart(self):
        pass

    def onTouchEnd(self):
        pass

    def onMove(self, value):
        if self.account_id == "":
            return

        defaultUniverse = self.getGUIParameter(UNIVERSE_SPIN, "value")
        channels = buildChannels(self)

        for channel in channels:
            connection_manager.setChannelSilent(self.account_id, defaultUniverse, channel, value*2)
        connection_manager.sendFrameToServer(self.account_id, defaultUniverse)

    # endregion
