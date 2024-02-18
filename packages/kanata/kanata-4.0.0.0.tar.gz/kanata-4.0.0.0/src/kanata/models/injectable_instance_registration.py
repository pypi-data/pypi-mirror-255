from dataclasses import dataclass
from typing import Any

from .injectable_registration import InjectableRegistration

@dataclass(kw_only=True)
class InjectableInstanceRegistration(InjectableRegistration):
    """Holds information about the registration of an injectable instance."""

    injectable_instance: Any
    """Gets or sets the injectable instance."""
