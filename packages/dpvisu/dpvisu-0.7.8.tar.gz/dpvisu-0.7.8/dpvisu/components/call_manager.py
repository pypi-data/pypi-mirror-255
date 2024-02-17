from .abstract_node import AbstractNode

class CallManager:

    # Map all callees to all their callers through a manager
    __function_mappings: dict[str, 'CallManager'] = dict()
    __advancement_mappings: dict[str, 'CallManager'] = dict()
    __function_tag_mappings: dict[str, 'CallManager'] = dict()

    def __init__(self):
        # Calls on a per-instance basis
        self.__callers: set['AbstractNode'] = set()

    @staticmethod
    def start_new_diagram():
        CallManager.__function_mappings = dict()
        CallManager.__advancement_mappings = dict()
        CallManager.__function_tag_mappings = dict()

    @staticmethod
    def registerCallToFunction(callee: str, caller: AbstractNode):
        CallManager.__function_mappings.setdefault(callee, CallManager())
        CallManager.__function_mappings[callee].__callers.add(caller)

    @staticmethod
    def registerCallToAdvancement(callee: str, caller: AbstractNode):
        CallManager.__advancement_mappings.setdefault(callee, CallManager())
        CallManager.__advancement_mappings[callee].__callers.add(caller)

    @staticmethod
    def registerCallToFunctionTag(callee: str, caller: AbstractNode):
        CallManager.__function_tag_mappings.setdefault(callee, CallManager())
        CallManager.__function_tag_mappings[callee].__callers.add(caller)

    @staticmethod
    def getCallManagerOfFunction(subject: str):
        return CallManager.__function_mappings.get(subject, CallManager())

    @staticmethod
    def getCallManagerOfAdvancement(subject: str):
        return CallManager.__advancement_mappings.get(subject, CallManager())

    @staticmethod
    def getCallManagerOfFunctionTag(subject: str):
        return CallManager.__function_tag_mappings.get(subject, CallManager())


    @property
    def hasCalls(self):
        return len(self.__callers) > 0

    @property
    def registeredFunctions(self):
        from .function import Function
        for call in self.__callers:
            if isinstance(call, Function):
                yield call

    @property
    def registeredAdvancements(self) -> 'Advancement':
        from .advancement import Advancement
        for call in self.__callers:
            if isinstance(call, Advancement):
                yield call

    @property
    def registeredFunctionTags(self) -> 'FunctionTag':
        from .function_tag import FunctionTag
        for call in self.__callers:
            if isinstance(call, FunctionTag):
                yield call

    @property
    def registeredNodes(self) -> 'Node':
        from .node import Node
        for call in self.__callers:
            if isinstance(call, Node):
                yield call
