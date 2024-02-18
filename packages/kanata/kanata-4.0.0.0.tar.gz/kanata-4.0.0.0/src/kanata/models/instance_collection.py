from collections.abc import Generator
from typing import Any

from .iinstance_collection import IInstanceCollection
from .injectable_scope_type import InjectableScopeType

class InstanceCollection(IInstanceCollection):
    """A container for resolved instances."""

    def __init__(self) -> None:
        self.__instances = dict[InjectableScopeType, dict[type, set]]()

    def get_instances_by_injectable(
        self,
        injectable_type: type,
        scope_type: InjectableScopeType | None = None
    ) -> Generator[Any, None, None]:
        if scope_type is None:
            for injectables_by_contract in self.__instances.values():
                yield from injectables_by_contract.get(injectable_type, ())
            return

        if not (injectables_by_contract := self.__instances.get(scope_type)):
            return

        yield from injectables_by_contract.get(injectable_type, ())

    def add_instance(
        self,
        scope_type: InjectableScopeType,
        injectable_type: type,
        instance: Any
    ) -> None:
        """Adds the specified instance to the collection associated to
        the specified injectable type and scope.

        :param scope_type: The scope of the injectable.
        :type scope_type: InjectableScopeType
        :param injectable_type: The type of the injectable.
        :type injectable_type: type
        :param instance: The injectable instance to be added.
        :type instance: Any
        """

        if not (instances_by_scope := self.__instances.get(scope_type)):
            self.__instances[scope_type] = instances_by_scope = {}
        if not (instances := instances_by_scope.get(injectable_type)):
            instances_by_scope[injectable_type] = instances = set()
        instances.add(instance)
