from .node import Node
from .edge import Edge
from .call_manager import CallManager


class Advancement(Node):
    function_search_string = r'(?:"function"\s*:\s*")([^\s"]+)'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def getAssociatedGlob() -> str:
        return r'*/advancements/**/*.json'

    @staticmethod
    def handleFile(file: str, base_pack: str):
        return Advancement(raw_file_path=file, data_folder_path=base_pack)

    def initObj(self):
        super()._initObj(colors = ["limegreen"])

    def generateCallList(self, file: str):
        calls = Node._extractCallListFromFile(file, search_string=Advancement.function_search_string)
        for call in calls:
            CallManager.registerCallToFunction(call, self)

    def createEdges(self):
        cm = CallManager.getCallManagerOfAdvancement(self.getMCName())
        for caller in cm.registeredFunctions:
            Edge.connect(caller, self)
        self._is_root_node = not cm.hasCalls
