from collections.abc import Callable
from typing import TypeVar

from kanata.models import InjectableTypeRegistration
from kanata.utils import get_generic_type_parameters, get_or_add_attribute

T = TypeVar("T")

def injectable(contract_type: type) -> Callable[[type[T]], type[T]]:
    """Marks a class as an injectable.

    :param contract_type: The type of the contract by which an instance of the object is injectable.
    :type contract_type: type
    :return: A decorator that returns the same class that it decorates.
    :rtype: Callable[[type[T]], type[T]]
    """

    def decorator(wrapped_class: type[T]) -> type[T]:
        registration = get_or_add_attribute(
            wrapped_class,
            InjectableTypeRegistration.PROPERTY_NAME,
            lambda injectable_type=wrapped_class: __create_registration(injectable_type)
        )
        registration.contract_types.add(contract_type)
        return wrapped_class

    return decorator

def __create_registration(
    injectable_type: type
) -> InjectableTypeRegistration:
    # TODO https://github.com/PyCQA/pylint/issues/6550
    return InjectableTypeRegistration( # pylint: disable=unexpected-keyword-arg
        injectable_type=injectable_type,
        is_generic=bool(get_generic_type_parameters(injectable_type))
    )
