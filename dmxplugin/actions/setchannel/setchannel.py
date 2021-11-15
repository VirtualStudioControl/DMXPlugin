from dmxplugin.common.parsing.parser import Parser
from dmxplugin.common.uitools import ensureAccountComboBox
from virtualstudio.common.account_manager import account_manager


ACCOUNT_COMBO = "account_combo"
UNIVERSE_SPIN = "universe_spin"
CHANNEL_ID_EDIT = "channel_id_edit"

ADDITIONAL_CONTROLS = "additional_controls"
SET_STACK = "set_stack"

MODE_COMBO = "mode_combo"
SET_SPINBOX = "set_spinbox"


parser = Parser()

def buildChannels(action):
    channelText = action.getGUIParameter(CHANNEL_ID_EDIT, "text")
    parser.loadText(channelText)
    return parser.parseIntegerList()