from typing import List, Callable

from dmxplugin.common.device.dmxdevice import DMXDevice, fromDict as dictToDMXDevice


class DeviceManager:

    def __init__(self, connectionHandler):
        self.DMX_DEVICES: List[DMXDevice] = []
        self.handler = connectionHandler

        self.callbacks = []

    def addCallback(self, cb: Callable[[], None]):
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def removeCallback(self, cb: Callable[[], None]):
        if cb in self.callbacks:
            self.callbacks.remove(cb)

    def execCallbacks(self):
        for cb in self.callbacks:
            cb()

    def addDMXDevice(self, device: DMXDevice, silent=False):
        if device in self.DMX_DEVICES:
            return

        self.DMX_DEVICES.append(device)

        for child in device.children:
            self.addDMXDevice(child)

        if not silent:
            self.execCallbacks()

    def clearDMXDevices(self):
        self.DMX_DEVICES.clear()

    def getDMXDevices(self):
        return self.DMX_DEVICES

    def updateDMXDevices(self):
        for dev in self.DMX_DEVICES:
            dev.updateDevice()

    def toDict(self):
        devices = []
        for dev in self.DMX_DEVICES:
            if not dev.hasParent():
                devices.append(dev.toDict())

        return {
            "dmxdevices": devices
        }

    def fromDict(self, values):
        for device in values["dmxdevices"]:
            self.addDMXDevice(dictToDMXDevice(device, device_manager=self), silent=True)
        self.execCallbacks()
