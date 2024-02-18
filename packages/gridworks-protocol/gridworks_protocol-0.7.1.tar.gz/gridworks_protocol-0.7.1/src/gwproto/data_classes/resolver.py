from abc import ABC
from abc import abstractmethod

from gwproto.data_classes.component import Component
from gwproto.data_classes.sh_node import ShNode


class ComponentResolver(ABC):
    @abstractmethod
    def resolve(
        self,
        node_name: str,
        nodes: dict[str, ShNode],
        components: dict[str, Component],
    ):
        raise NotImplementedError
