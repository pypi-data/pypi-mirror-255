from .node import Node
from .edge import Edge
from .call_manager import CallManager


class Function(Node):
    function_search_string = r'(?:function )(\S+)'
    advancement_search_string = r'(?:advancement grant .+ (?:only|until|through|from) )(\S+)(?:[$\s])?'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.called_by_tags = []

    @staticmethod
    def getAssociatedGlob() -> str:
        return r'*/functions/**/*.mcfunction'

    @staticmethod
    def handleFile(file: str, base_pack: str):
        return Function(raw_file_path=file, data_folder_path=base_pack)

    def generateCallList(self, file: str):
        # search for function calls
        calls = Node._extractCallListFromFile(file, search_string=Function.function_search_string)
        self._is_recursive = self.getMCName() in calls
        if self._is_recursive:
            calls.remove(self.getMCName())
        for callee in calls:
            CallManager.registerCallToFunction(callee, self)

        # search for advancement grantings
        for call in Node._extractCallListFromFile(file, search_string=Function.advancement_search_string):
            CallManager.registerCallToAdvancement(call, self)

    def initObj(self):
        colors = []
        cm = CallManager.getCallManagerOfFunction(self.getMCName())
        callers = CallManager.getCallManagerOfFunction(self.getMCName())
        if not cm.hasCalls:
            self._is_root_node = True
            colors.append("darkorange2")
        else:
            for caller in cm.registeredFunctionTags:
                self.called_by_tags.append(caller.getMCName())
            if len(self.called_by_tags) > 0:
                # Called by a tag
                colors.append("purple")
        # Single iteration or recursive
        colors.append("firebrick" if self._is_recursive else "royalblue4")
        super()._initObj(colors)

    def createEdges(self):
        cm = CallManager.getCallManagerOfFunction(self.getMCName())
        for caller in cm.registeredNodes:
            Edge.connect(caller, self)

    def _getTooltip(self):
        return super()._getTooltip() + f"\nRecursive: {self._is_recursive}\nCalled by Tags:\n{', '.join(self.called_by_tags)}"
