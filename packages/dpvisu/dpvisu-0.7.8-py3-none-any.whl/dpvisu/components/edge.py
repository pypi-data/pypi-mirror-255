from diagrams import Edge as OGEdge
from random import random
from colorsys import hsv_to_rgb


class Edge:
    @classmethod
    def __makeEdge(self, tooltip=None) -> OGEdge:
        return OGEdge(color=Edge.__getRandomColor(), penwidth="3", tooltip=tooltip)

    @classmethod
    def __getRandomColor(self) -> str:
        r, g, b = [hex(int(255 * i))[-2:] for i in hsv_to_rgb(random(), 0.5, 1.0)]
        return f'#{r}{g}{b}'

    @classmethod
    def connect(self, node1: 'Node', node2: 'Node'):
        node1.obj >> Edge.__makeEdge(f'{node1.getMCName()} -> {node2.getMCName()}') >> node2.obj
