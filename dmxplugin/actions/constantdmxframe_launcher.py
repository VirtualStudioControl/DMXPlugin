from dmxplugin.actions.setdmxframe.setdmxframe_button import ButtonSetDMXFrameAction
from dmxplugin.actions.setdmxframe.setdmxframe_imagebutton import ImagebuttonSetDMXFrameAction
from dmxplugin.common.pluginloader import ROOT_DIRECTORY

from virtualstudio.common.action_manager.actionmanager import registerCategoryIcon
from virtualstudio.common.io import filewriter
from virtualstudio.common.structs.action.action_launcher import *
from virtualstudio.common.tools import icontools
from virtualstudio.common.tools.icontools import readPNGIcon

from pathlib import Path

class SetConstantFrameLauncher(ActionLauncher):

    def __init__(self):
        super(SetConstantFrameLauncher, self).__init__()
        registerCategoryIcon(["DMX"], ROOT_DIRECTORY + "/assets/icons/category/dmx.png")

        self.ACTIONS = {
            CONTROL_TYPE_BUTTON: ButtonSetDMXFrameAction,
            #CONTROL_TYPE_FADER: FaderDebugAction,
            CONTROL_TYPE_IMAGE_BUTTON: ImagebuttonSetDMXFrameAction,
            #CONTROL_TYPE_ROTARY_ENCODER: RotaryEncoderDebugAction
        }

    #region Metadata

    def getName(self):
        return "Set DMXFrame"

    def getIcon(self):
        return readPNGIcon(ROOT_DIRECTORY + "/assets/icons/actions/lightbulbs.png")

    def getCategory(self):
        return ["DMX"]

    def getAuthor(self):
        return "eric"

    def getVersion(self):
        return (0,0,1)

    def getActionStateCount(self, controlType: str) -> int:
        return 1

    def getActionUI(self, controlType: str) -> Tuple[str, str]:
        return UI_TYPE_QTUI, \
               icontools.encodeIconData(
                   filewriter.readFileBinary(ROOT_DIRECTORY + "/assets/ui/actions/setdmxframe.ui"))
    #endregion