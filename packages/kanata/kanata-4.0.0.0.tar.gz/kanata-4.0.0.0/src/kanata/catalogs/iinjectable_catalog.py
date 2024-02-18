from typing import Protocol, TypeVar

from kanata.models import InjectableRegistration

T = TypeVar("T")

class IInjectableCatalog(Protocol):
    """Interface for a catalog of injectable registrations."""

    def get_registrations(self) -> tuple[InjectableRegistration, ...]:
        """Gets all the registrations available in the catalog.

        :return: The available registrations.
        :rtype: tuple[InjectableRegistration, ...]
        """
        ...

    def get_registrations_by_contract(
        self,
        contract: type) -> tuple[InjectableRegistration, ...]:
        """Gets the registrations associated to the specified contract.

        :param contract: The contract for which to get the registrations.
        :type contract: type
        :return: The registrations associated to the contract.
        :rtype: tuple[InjectableRegistration, ...]
        """
        ...

    def get_registration_by_injectable(
        self,
        injectable: type) -> InjectableRegistration | None:
        """Gets the registration associated to the specified injectable.

        :param injectable: The injectable for which to get the registration.
        :type injectable: type
        :return: If exists, the registration associated to the injectable.
        :rtype: InjectableRegistration | None
        """
        ...
