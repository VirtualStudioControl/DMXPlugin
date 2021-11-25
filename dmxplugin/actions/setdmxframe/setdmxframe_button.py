import base64
from typing import List, Tuple, Union

from dmxplugin.actions.setdmxframe.setdmxframe import ACCOUNT_COMBO, FILE_SELECTOR
from dmxplugin.common.connection_manager import connection_manager
from dmxplugin.common.io.dmxframe_io import readDMXFrame
from dmxplugin.common.uitools import ensureAccountComboBox, setAccountComboBox
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.logging import logengine
from virtualstudio.common.structs.action.button_action import ButtonAction

logger = logengine.getLogger()

class ButtonSetDMXFrameAction(ButtonAction):

    #region handlers

    def onLoad(self):
        self.uuid_map = []
        self.account_id = ""

        self.filename = ""
        self.dmxData: List[Tuple[int, Union[bytes, bytearray, List[int]]]] = []

    def onAppear(self):
        account_manager.registerAccountChangeCallback(self.accountChangedCB)
        self.uuid_map = ensureAccountComboBox(self, ACCOUNT_COMBO)

        self.filename = self.getGUIParameter(FILE_SELECTOR, "currentFile")
        self.dmxData = self.decodeDMXData(self.getGUIParameter(FILE_SELECTOR, "fileContent"))

        self.setGUIParameter(FILE_SELECTOR, "fileFilter", "DMXFrame (*.dmxframe)")

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
        filename = self.getGUIParameter(FILE_SELECTOR, "currentFile")
        if self.filename != filename:
            self.filename = filename
            self.dmxData = self.decodeDMXData(self.getGUIParameter(FILE_SELECTOR, "fileContent"))
            logger.info()

        index = self.getGUIParameter(ACCOUNT_COMBO, "currentIndex")
        if index is not None:
            self.account_id = self.uuid_map[index]
            connection_manager.updateDMXFrameBuffer(self.account_id)

    #endregion

    #region DMXFrame

    def decodeDMXData(self, base64data: str):
        if base64data is None:
            return None
        bindata = base64.b64decode(base64data.encode("utf-8"))
        return readDMXFrame(bindata)


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

        if self.dmxData is not None:
            for frame in self.dmxData:
                logger.info("UPDATING UNIVERSE: {}".format(frame[0]))
                connection_manager.setFrame(self.account_id, frame[0], frame[1])
                connection_manager.sendFrameToServer(self.account_id, frame[0])
        else:
            logger.info("DMXData is None !")

    # endregion
