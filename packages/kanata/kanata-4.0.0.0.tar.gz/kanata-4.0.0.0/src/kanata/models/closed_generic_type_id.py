from typing import NamedTuple

class ClosedGenericTypeId(NamedTuple):
    """A named tuple used to identify a dynamically created closed generic type."""

    origin_type: type
    """The type of the origin injectable from which the closed generic type was created."""

    generic_type_argument: type
    """The generic type argument of the closed generic type."""
