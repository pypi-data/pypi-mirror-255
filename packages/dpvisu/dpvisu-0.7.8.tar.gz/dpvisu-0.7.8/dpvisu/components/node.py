from .abstract_node import AbstractNode
from .cluster import Cluster
import re
import os
from diagrams import Node as OGNode
from abc import abstractmethod


class Node(AbstractNode):
    """
        Diagrams-Node wrapper
        Needed because data must be stored before diagrams-Node instance is created, as the context must be set to the correct cluster before init, but that cluster isn't known in advance.
        The actual diagrams-Node creation happens in initObj()
    """

    def __init__(self, raw_file_path: str, data_folder_path: str):
        super().__init__(raw_file_path, data_folder_path)

        self.obj = None  # Node Obj must be created when the appropriate cluster is open
        self._is_root_node = None

        self.parent_cluster_path = '/'.join(self._call_name.replace(':', '/').split('/')[:-1])
        Cluster.fetchClusterByName(self.parent_cluster_path).add_child(self)

    @staticmethod
    def _getRelativePath(file: str, data_folder: str) -> str:
        return os.path.relpath(file, data_folder).replace(os.sep, '/')

    def _getTooltip(self) -> str:
        return self.getMCName() + f"\n\nRoot Node: {self._is_root_node}"

    @abstractmethod
    def initObj(self):
        raise "Call to abstract base function."

    def _initObj(self, colors: list[str]):
        attrs = {
            "width": str(len(self._display_name) / 10.0 + 0.5),
            "height": "0.5",
            "shape": "box",
            "style": "filled",
            "tooltip": self._getTooltip()
        }
        ln = len(colors)
        if ln == 1:
            attrs["fillcolor"] = colors[0]
        if ln == 2:
            # graphviz only allows for 2 colors when using diagonal stripes (╯°□°）╯︵ ┻━┻
            attrs["fillcolor"] = f';{0.5}:'.join(colors)
            attrs["gradientangle"] = "60"
        else:
            weight = 1.0 / (ln * 2)
            attrs["fillcolor"] = f';{weight}:'.join(colors)
            attrs["style"] = "striped"
            attrs["gradientangle"] = "0"
        self.obj = OGNode(label=self._display_name, **attrs)

    @abstractmethod
    def createEdges(self):
        raise "Call to abstract base function."
