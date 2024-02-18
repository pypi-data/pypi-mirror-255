from collections.abc import Generator
from typing import Any, Protocol

from .injectable_scope_type import InjectableScopeType

class IInstanceCollection(Protocol):
    """Interface for a resolved instance collection."""

    def get_instances_by_injectable(
        self,
        injectable_type: type,
        scope_type: InjectableScopeType | None = None
    ) -> Generator[Any, None, None]:
        """Gets all the resolved instances associated to the specified contract.

        :param injectable_type: The injectable type for which to get the instances.
        :type injectable_type: type
        :param scope_type: An optional scope for which to get the instances, defaults to None
        :type scope_type: InjectableScopeType | None, optional
        :yield: Resolved instances associated to the contract.
        :rtype: Generator[Any, None, None]
        """
        ...
