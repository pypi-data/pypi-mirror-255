from __future__ import annotations

from typing import Protocol, TypeVar

TInjectable = TypeVar("TInjectable")

class ILifetimeScope(Protocol):
    """Interface for an injectable lifetime scope
    that manages the lifetimes of injectables
    and provides access to them.
    """

    def resolve(self, injectable: type[TInjectable]) -> TInjectable:
        """Resolves an instance of an injectable associated to the specified interface.

        :param injectable: The injectable for which to get a resolved instance.
        :type injectable: type[TInjectable]
        :raises DependencyResolutionException: Raised when dependency resolution fails.
        :return: An instance of the appropriate injectable.
        :rtype: TInjectable
        """
        ...

    def create_child_scope(self) -> ILifetimeScope:
        """Creates a lifetime scoped attached to the current one.
        This child will have access to the same injectable catalog,
        as well as singleton instances. Scoped instances will die
        along with this child.

        :return: A lifetime scope attached to the current lifetime scope.
        :rtype: ILifetimeScope
        """
        ...
