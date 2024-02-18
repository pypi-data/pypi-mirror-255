from typing import Any, Protocol

from kanata.models import InjectableRegistration
from .resolver_context import ResolverContext

class IResolver(Protocol):
    """Interface for a service that can resolve instances of injectables."""

    def resolve(
        self,
        context: ResolverContext,
        registration: InjectableRegistration,
        injectable_type: type
    ) -> Any:
        """Resolves an instance of a specific injectable.

        :param context: Contextual information for the resolver.
        :type context: ResolverContext
        :param injectable_type: The injectable that needs to be resolved. For generic injectables, this is the closed generic type.
        :type injectable_type: type
        :return: The resolved injectable instance.
        :rtype: TInjectable
        """
        ...
