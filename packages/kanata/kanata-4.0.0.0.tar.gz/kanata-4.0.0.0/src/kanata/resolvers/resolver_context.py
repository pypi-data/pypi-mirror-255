from dataclasses import dataclass

from kanata.catalogs import IInjectableCatalog
from kanata.models import ClosedGenericTypeId, ClosedGenericTypeInfo, IInstanceCollection

@dataclass(frozen=True, kw_only=True)
class ResolverContext:
    """Holds contextual information for resolvers."""

    catalog: IInjectableCatalog
    """The catalog of injectables."""

    closed_generic_types: dict[ClosedGenericTypeId, ClosedGenericTypeInfo]
    """A map of closed generic types available for injection."""

    instances: IInstanceCollection
    """The already resolved instances of injectables."""
