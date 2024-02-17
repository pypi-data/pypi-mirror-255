import re
import os
from abc import ABC, abstractmethod


class AbstractNode(ABC):
    """
        Abstract base class representing a file of a datapack.
        Cannot be drawn to a graph on its own, as not all files need graphical representation.
    """

    def __init__(self, raw_file_path: str, data_folder_path: str):
        self.relative_path = self._getRelativePath(raw_file_path, data_folder_path)
        self._call_name = self._generateCallName(self.relative_path)

        self._display_name = self._generateDisplayName()
        self.generateCallList(raw_file_path)

    @staticmethod
    @abstractmethod
    def handleFile(file: str, base_pack: str):
        raise "Call to abstract base function."

    @abstractmethod
    def generateCallList(self, file: str):
        raise "Call to abstract base function."

    @staticmethod
    @abstractmethod
    def getAssociatedGlob() -> str:
        raise "Call to abstract base function."

    @staticmethod
    def _getRelativePath(file: str, data_folder: str) -> str:
        return os.path.relpath(file, data_folder).replace(os.sep, '/')

    def getMCName(self):
        return self._call_name

    def __eq__(self, other: 'AbstractNode'):
        if not isinstance(other, AbstractNode):
            return NotImplemented
        return type(self) == type(other) and self.getMCName() == other.getMCName()

    def __hash__(self):
        return hash((self.getMCName(), type(self)))

    def _generateDisplayName(self) -> str:
        return self.getMCName().replace(':','/').split('/')[-1]

    @staticmethod
    def _generateCallName(relative_path: str) -> str:
        # Remove Extension
        path = os.path.normpath(relative_path)
        path = os.path.splitext(path)[0]

        # Remove 2nd level of folder structure ("function" or "advancement")
        path = path.replace(os.sep, '/')
        return re.sub('(/[A-z0-9_]+/)', ':', path, count=1)

    @staticmethod
    def _extractCallListFromFile(file: str, search_string: str) -> set[str]:
        calls = set()
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if not line.startswith("#"):
                    match = re.search(search_string, line)
                    if match is not None:
                        calls.add(match.group(1))
        return set(calls)  # Eliminate duplicates
