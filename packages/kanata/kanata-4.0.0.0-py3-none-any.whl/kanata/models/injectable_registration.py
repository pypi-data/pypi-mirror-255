from dataclasses import dataclass, field
from typing import ClassVar

@dataclass(kw_only=True)
class InjectableRegistration:
    """Holds information about the registration of an injectable."""

    PROPERTY_NAME: ClassVar[str] = "kanata_injectable_registrations"
    """The name of the property used to hold the list
    of registration objects attached to an injectable."""

    contract_types: set[type] = field(default_factory=set)
    """Gets or sets the types of the contracts by which an instance of the object is injectable."""
