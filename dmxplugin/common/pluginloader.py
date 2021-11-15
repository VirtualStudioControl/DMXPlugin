from pathlib import Path
from typing import List

from virtualstudio.common.account_manager.account_manager import registerAccountType
from virtualstudio.common.logging import logengine

ROOT_DIRECTORY = str(Path(__file__).resolve().parents[2])

ACCOUNT_TYPE_DMX_RELAY: str = "DMX Relay"

ACCOUNT_TYPES: List[str] = [ACCOUNT_TYPE_DMX_RELAY]


def initializePlugin():
    registerAccountType(ACCOUNT_TYPE_DMX_RELAY, ROOT_DIRECTORY + "/assets/icons/category/account.png")

initializePlugin()