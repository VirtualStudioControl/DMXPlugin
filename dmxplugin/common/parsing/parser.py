from typing import List

DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

class Parser:

    def __init__(self):
        self.position = 0
        self.text = ""

    def loadText(self, text: str):
        self.position = 0
        self.text = text

    def available(self) -> bool:
        return self.position < len(self.text)

    def peek(self) -> str:
        return self.text[self.position]

    def consume(self):
        self.position += 1

    def isDigit(self, char):
        return char in DIGITS

    def toDigit(self, char) -> int:
        if char in DIGITS:
            return DIGITS.index(char)

    def parseInt(self):
        result = 0
        while self.available():
            if not self.isDigit(self.peek()):
                return result
            result = result * 10 + self.toDigit(self.peek())
            self.consume()
        return result

    def parseIntegerList(self) -> List[int]:
        result = []

        while self.available():
            if self.isDigit(self.peek()):
                result.append(self.parseInt())
            else:
                self.consume()

        return result