from dmxplugin.actions.setchannel_device.setchannel_device_fader import FaderSetChannelDeviceAction
from dmxplugin.common.pluginloader import ROOT_DIRECTORY

from virtualstudio.common.action_manager.actionmanager import registerCategoryIcon
from virtualstudio.common.io import filewriter
from virtualstudio.common.structs.action.action_launcher import *
from virtualstudio.common.tools import icontools
from virtualstudio.common.tools.icontools import readPNGIcon

from pathlib import Path

class SetChannelDeviceLauncher(ActionLauncher):

    def __init__(self):
        super(SetChannelDeviceLauncher, self).__init__()
        registerCategoryIcon(["DMX"], ROOT_DIRECTORY + "/assets/icons/category/dmx.png")

        self.ACTIONS = {
            #CONTROL_TYPE_BUTTON: ButtonTransitionAction,
            CONTROL_TYPE_FADER: FaderSetChannelDeviceAction,
            #CONTROL_TYPE_IMAGE_BUTTON: ImagebuttonSetChannelAction,
            #CONTROL_TYPE_ROTARY_ENCODER: RotarySetChannelAction
        }

    #region Metadata

    def getName(self):
        return "Set Channel (Device)"

    def getIcon(self):
        return readPNGIcon(ROOT_DIRECTORY + "/assets/icons/actions/faders2.png")

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
                   filewriter.readFileBinary(ROOT_DIRECTORY + "/assets/ui/actions/setchannel_device.ui"))
    #endregion