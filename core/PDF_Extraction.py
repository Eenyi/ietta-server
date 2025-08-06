import json
import os

from tika import parser


class pdfParser:
    def __init__(self, fileName=None, storageLocation=None) -> None:
        self.fileName = fileName
        self.parsed = None
        self.__storingLocation = storageLocation
        self.__OpenFile()
        self.fileName = self.fileName[: len(self.fileName) - 4]

    def __OpenFile(self) -> None:
        try:
            if self.fileName:
                self.parsed = parser.from_file(self.__storingLocation + self.fileName)
        except Exception as e:
            print(e)

    def ParseContent(self) -> str:
        try:
            if self.parsed:
                return self.parsed["content"]
        except Exception as e:
            print(e)

    def ParseMetaData(self) -> str:
        try:
            if self.parsed:
                return self.parsed["metadata"]
        except Exception as e:
            print(e)

    def convertToText(self):
        try:
            with open(
                self.__storingLocation + self.fileName + ".txt", "w", encoding="utf-8"
            ) as file:
                file.write(self.ParseContent().lstrip())
            os.remove(self.__storingLocation + self.fileName + ".pdf")
            return True
        except Exception as e:
            print(e)
            return False

    def countLines(self, reader):
        b = reader(1024 * 1024)
        while b:
            yield b
            b = reader(1024 * 1024)

    def createAnnotationFile(self, filePath) -> bool:
        try:
            with open(filePath, "r", encoding="utf-8") as textFile:
                for singleLine in textFile:
                    count = self.getWordCount(singleLine)
                    if not self.writeMetaData(count, filePath):
                        return False
            return True
        except Exception as e:
            print(e)
            return False

    def writeMetaData(self, count, filePath) -> bool:
        try:
            with open(filePath[: len(filePath) - 3] + "ietta", "a") as metaFile:
                for i in range(count):
                    metaFile.write("O ")
                metaFile.write("\n")
            return True
        except Exception as e:
            print(e)
            return False

    def getWordCount(self, line) -> int:
        words = line.split()
        return len(words)
