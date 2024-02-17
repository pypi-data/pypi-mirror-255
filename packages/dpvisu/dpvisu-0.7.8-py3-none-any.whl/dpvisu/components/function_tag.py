from .abstract_node import AbstractNode
from .node import Node
from .call_manager import CallManager
import re
import os

class FunctionTag(AbstractNode):
    function_search_string = r'(?:")(\S+:\S+)(?:")'

    def __init__(self, file: str, data_folder: str, *args, **kwargs):
        super().__init__(raw_file_path=file, data_folder_path=data_folder)

    @staticmethod
    def getAssociatedGlob() -> str:
        return r'*/tags/functions/**/*.json'

    @staticmethod
    def handleFile(file: str, base_pack: str):
        FunctionTag(file, base_pack).generateCallList(file)
        return None

    def generateCallList(self, file: str):
        #search for function calls
        calls = AbstractNode._extractCallListFromFile(file, search_string=FunctionTag.function_search_string)
        for callee in calls:
            CallManager.registerCallToFunction(callee, self)

    @staticmethod
    def _generateCallName(relative_path: str) -> str:
        # Remove Extension
        path = os.path.normpath(relative_path)
        path = os.path.splitext(path)[0]

        # Remove 2nd & 3rd level of folder structure ("tags/function")
        path = path.replace(os.sep, '/')
        return "#" + re.sub('(/[A-z0-9_]+/[A-z0-9_]+/)', ':', path, count=1)
