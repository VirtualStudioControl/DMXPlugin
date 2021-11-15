from dmxplugin.actions.setchannel.setchannel import ADDITIONAL_CONTROLS, ACCOUNT_COMBO, UNIVERSE_SPIN, buildChannels, \
    MODE_COMBO, SET_STACK, SET_SPINBOX
from dmxplugin.common.connection_manager import connection_manager
from dmxplugin.common.uitools import ensureAccountComboBox, setAccountComboBox
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.logging import logengine
from virtualstudio.common.structs.action.imagebutton_action import ImageButtonAction

logger = logengine.getLogger()

class ImagebuttonSetChannelAction(ImageButtonAction):

    #region handlers

    def onLoad(self):
        self.uuid_map = []
        self.value = 0
        self.account_id = ""


    def onAppear(self):
        self.setGUIParameter(ADDITIONAL_CONTROLS, "currentIndex", 1)
        account_manager.registerAccountChangeCallback(self.accountChangedCB)
        self.uuid_map = ensureAccountComboBox(self, ACCOUNT_COMBO)

        modeCombo = self.getGUIParameter(MODE_COMBO, "currentIndex")

        if modeCombo == 0:
            self.setGUIParameter(SET_STACK, "currentIndex", 1)
        else:
            self.setGUIParameter(SET_STACK, "currentIndex", 0)


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
        modeCombo = self.getGUIParameter(MODE_COMBO, "currentIndex")
        if modeCombo is None:
            modeCombo = 0

        if modeCombo == 0:
            self.setGUIParameter(SET_STACK, "currentIndex", 1)
        else:
            self.setGUIParameter(SET_STACK, "currentIndex", 0)

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
        self.nextState()

    def onKeyUp(self):
        if self.account_id == "":
            return

        defaultUniverse = self.getGUIParameter(UNIVERSE_SPIN, "value")
        channels = buildChannels(self)

        modeCombo = self.getGUIParameter(MODE_COMBO, "currentIndex")
        if modeCombo is None:
            modeCombo = 0

        for channel in channels:
            value = connection_manager.getChannel(self.account_id, defaultUniverse, channel)
            logger.info(value)
            if modeCombo == 0:
                val = self.getGUIParameter(SET_SPINBOX, "value")

                if val is None:
                    val = 0
                value = val
            elif modeCombo == 1:
                value += 1
            else:
                value -= 1

            value = min(0xff, max(value, 0))

            connection_manager.setChannelSilent(self.account_id, defaultUniverse, channel, value)

        connection_manager.sendFrameToServer(self.account_id, defaultUniverse)

    # endregion
