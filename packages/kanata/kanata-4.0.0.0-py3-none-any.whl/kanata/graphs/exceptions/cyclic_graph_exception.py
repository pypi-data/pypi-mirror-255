from typing import Any

class CyclicGraphException(Exception):
    """Raised when a cycle is detected in a graph which doesn't allow one."""

    def __init__(self, nodes: set[Any], *args: object) -> None:
        """Initializes a new instance.

        :param nodes: The list of nodes that form the cycle.
        :type nodes: set[Any]
        """

        super().__init__(*args)
        self.__nodes: set[Any] = nodes

    @property
    def nodes(self) -> set[Any]:
        """Gets the list of nodes that form the cycle.

        :return: The list of nodes that form the cycle.
        :rtype: set[Any]
        """

        return self.__nodes
