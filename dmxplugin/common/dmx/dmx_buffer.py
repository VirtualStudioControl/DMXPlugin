from typing import Dict

from virtualstudio.common.tools.bytetools import getInt


class DMXBuffer:

    def __init__(self):
        super(DMXBuffer, self).__init__()
        self.buffers: Dict[int, bytearray] = {}

    def loadData(self, content: bytes):
        universeCount = getInt(content, 0)

        position = 4
        for i in range(universeCount):
            universe = getInt(content, position)
            position += 4
            universeLength = getInt(content, position)
            position += 4
            data = content[position: position + universeLength]
            position += universeLength
            self.buffers[universe] = bytearray(data)

    def setChannel(self, universe, channel, value):
        if universe not in self.buffers:
            self.buffers[universe] = bytearray(512)
        value = min(0xff, max(value, 0))
        self.buffers[universe][channel] = value & 0xff

    def getChannel(self, universe, channel):
        if universe not in self.buffers:
            return 0
        return self.buffers[universe][channel]

    def setFrame(self, universe, data):
        self.buffers[universe] = data

    def getFrame(self, universe):
        if universe not in self.buffers:
            self.buffers[universe] = bytearray(512)
        return self.buffers[universe]