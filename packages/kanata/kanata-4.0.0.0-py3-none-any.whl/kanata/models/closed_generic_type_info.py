from dataclasses import dataclass, field

from .closed_generic_type_id import ClosedGenericTypeId
from .injectable_type_registration import InjectableTypeRegistration

@dataclass(kw_only=True)
class ClosedGenericTypeInfo:
    """Information about a dynamically created closed generic type."""

    closed_generic_type: type
    """The dynamically created closed generic type."""

    generic_type_argument: type
    """The generic type argument of the closed generic type."""

    origin_registration: InjectableTypeRegistration
    """The registration for which the closed generic type was created."""

    identifier: ClosedGenericTypeId = field(init=False)
    """The identifier of the closed generic type."""

    def __post_init__(self) -> None:
        self.identifier = ClosedGenericTypeId(
            self.origin_registration.injectable_type,
            self.generic_type_argument
        )
