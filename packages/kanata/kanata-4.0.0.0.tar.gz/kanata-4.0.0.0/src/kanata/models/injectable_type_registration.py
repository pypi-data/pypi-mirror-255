from dataclasses import dataclass

from .injectable_registration import InjectableRegistration
from .injectable_scope_type import InjectableScopeType

@dataclass(kw_only=True)
class InjectableTypeRegistration(InjectableRegistration):
    """Holds information about the registration of an injectable type."""

    injectable_type: type
    """Gets or sets the type of the injectable object."""

    is_generic: bool = False
    """Gets or sets whether the injectable should be constructed
    by passing the generic type arguments of the contract
    as generic type parameters to the injectable.

    This behavior will result in a runtime error if the specified type
    is not a generic type or there is a signature mismatch between
    the injectable type and the contract type.
    """

    scope: InjectableScopeType = InjectableScopeType.TRANSIENT
    """Gets or sets the lifetime scope type of the created instances."""
