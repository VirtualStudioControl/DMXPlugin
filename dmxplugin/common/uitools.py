from typing import List

from dmxplugin.common.pluginloader import ACCOUNT_TYPES
from virtualstudio.common.account_manager import account_manager
from virtualstudio.common.structs.action.abstract_action import AbstractAction


def ensureAccountComboBox(action: AbstractAction, comboBoxName: str) -> List[str]:
    accounts = account_manager.getAccountListOfTypes(*ACCOUNT_TYPES)
    accountNames = [account.accountTitle for account in accounts]
    accountUUIDs: List[str] = [account.uuid for account in accounts]

    action.ensureGUIParameter(comboBoxName, "itemTexts", accountNames)

    return accountUUIDs


def setAccountComboBox(action: AbstractAction, comboBoxName: str) -> List[str]:
    accounts = account_manager.getAccountListOfTypes(*ACCOUNT_TYPES)
    accountNames = [account.accountTitle for account in accounts]
    accountUUIDs: List[str] = [account.uuid for account in accounts]

    action.setGUIParameter(comboBoxName, "itemTexts", accountNames)

    return accountUUIDs