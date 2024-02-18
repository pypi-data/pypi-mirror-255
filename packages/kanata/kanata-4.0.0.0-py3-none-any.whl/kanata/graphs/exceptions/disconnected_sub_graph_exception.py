from typing import Any

class DisconnectedSubGraphException(Exception):
    """Raised when a disconnected sub-graph is detected in a graph that doesn't allow it."""

    def __init__(self, nodes: tuple[Any, ...], *args: object) -> None:
        """Initializes a new instance.

        :param nodes: The list of nodes that form the disconnected sub-graph.
        :type nodes: tuple[Any, ...]
        """

        super().__init__(*args)
        self.__nodes: tuple[Any, ...] = nodes

    @property
    def nodes(self) -> tuple[Any, ...]:
        """Gets the list of nodes that form the disconnected sub-graph.

        :return: The list of nodes that form the disconnected sub-graph.
        :rtype: tuple[Any, ...]
        """

        return self.__nodes
