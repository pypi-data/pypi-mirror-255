from collections.abc import Iterable
from typing import get_origin

from kanata.exceptions import InjectableRegistrationException
from kanata.models import (
    InjectableInstanceRegistration, InjectableRegistration, InjectableTypeRegistration
)
from kanata.utils import get_generic_type_parameters, get_or_add
from .iinjectable_catalog import IInjectableCatalog

class InjectableCatalog(IInjectableCatalog):
    """Provides access to information about the known injectables."""

    def __init__(self, registrations: Iterable[InjectableRegistration]) -> None:
        self.__registrations_by_contract: dict[type, list[InjectableRegistration]] = {}
        self.__registrations_by_injectable: dict[type, InjectableRegistration] = {}
        self.__build_registration_maps(registrations)

    def get_registrations(self) -> tuple[InjectableRegistration, ...]:
        return tuple(self.__registrations_by_injectable.values())

    def get_registrations_by_contract(
        self,
        contract: type
    ) -> tuple[InjectableRegistration, ...]:
        registrations = [*self.__registrations_by_contract.get(contract, ())]

        if (origin := get_origin(contract)) and get_generic_type_parameters(origin):
            registrations.extend(
                self.__registrations_by_contract.get(origin, ())
            )

        return tuple(registrations)

    def get_registration_by_injectable(
        self,
        injectable: type
    ) -> InjectableRegistration | None:
        return self.__registrations_by_injectable.get(injectable, None)

    def __build_registration_maps(self, registrations: Iterable[InjectableRegistration]) -> None:
        for registration in registrations:
            for contract_type in registration.contract_types:
                by_injectables: list[InjectableRegistration] = get_or_add(
                    self.__registrations_by_contract,
                    contract_type,
                    lambda _: [])
                by_injectables.append(registration)

            match registration:
                case InjectableTypeRegistration():
                    key = registration.injectable_type
                case InjectableInstanceRegistration():
                    key = type(registration.injectable_instance)
                case _:
                    raise InjectableRegistrationException(
                        type(registration),
                        "Unsupported type of injectable registration."
                    )

            self.__registrations_by_injectable[key] = registration
