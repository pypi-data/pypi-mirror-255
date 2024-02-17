from diagrams import Cluster as OGCluster
from diagrams import setcluster
import logging


class Cluster:
    __cluster_list: dict[str, 'Cluster'] = {}

    def __init__(self, name: str):
        self.__name = name
        self._display_name = name.split('/')[-1]
        self.__cluster_obj: OGCluster = None
        self.__cluster_list.setdefault(self.__name, self)
        self.__children: list['Node'] = []
        self.__depth = name.count('/')

    def add_child(self, child: 'Node'):
        self.__children.append(child)

    @classmethod
    def fetchClusterByName(self, name: str) -> 'Cluster':
        # Fetch cluster if already created, otherwise create a new instnace.
        return Cluster.__cluster_list.get(name, Cluster.createTreeRec(name, name.split('/')))

    @classmethod
    def createTreeRec(self, own_name: str, path: list[str]):
        # If parent cluster already exists, create a new cluster.
        # If parent does not exist, create parent recursively until root cluster.
        own_name = '/'.join(path)
        parent_cluster = '/'.join(path[:-1])
        if len(path) > 1 and not parent_cluster in Cluster.__cluster_list:
            Cluster.createTreeRec(parent_cluster, path[:-1])
        if not own_name in Cluster.__cluster_list:
            ret = Cluster(own_name)
            Cluster.__cluster_list.setdefault(own_name, ret)
            return ret

    def clusterDepthToColor(self, iteration) -> str:
        return f'#{str((iteration%4)+1)*6}'

    def enterCluster(self):
        setcluster(self.__cluster_obj)
        logging.debug(f'-> {self.__name}')

    def leaveCluster(self):
        if self.__cluster_obj._parent:
            self.__cluster_obj._parent.subgraph(self.__cluster_obj.dot)
        else:
            self.__cluster_obj._diagram.subgraph(self.__cluster_obj.dot)
        setcluster(self.__cluster_obj._parent)
        logging.debug(f'<- {self.__name}')

    def draw(self) -> OGCluster:
        logging.debug(f'[+] cluster: {self.__name} Depth: {self.__depth}')
        attrs = {
            "bgcolor": self.clusterDepthToColor(self.__depth),
            "fontsize": "22",
            "fontcolor": "white",
            "style": "solid",
            "tooltip": self.__name
        }
        self.__cluster_obj = OGCluster(label=self._display_name, graph_attr=attrs)

    @classmethod
    def clusterize(self):
        open_clusters_stack: list[Cluster] = []

        for name, cluster in sorted(Cluster.__cluster_list.items()):
            cluster: Cluster
            while len(open_clusters_stack) > 0 and not name.startswith(open_clusters_stack[-1].__name + '/'):
                open_clusters_stack.pop(-1).leaveCluster()
            cluster.draw()
            cluster.enterCluster()
            open_clusters_stack.append(cluster)
            for node in cluster.__children:
                if node.obj is None:
                    node.initObj()
        while len(open_clusters_stack) > 0:
            open_clusters_stack.pop(-1).leaveCluster()
