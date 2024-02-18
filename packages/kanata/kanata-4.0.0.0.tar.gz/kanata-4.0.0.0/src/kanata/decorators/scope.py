from collections.abc import Callable
from typing import TypeVar

from kanata.models import InjectableScopeType, InjectableTypeRegistration
from kanata.utils import get_or_add_attribute

T = TypeVar("T")

def scope(scope_type: InjectableScopeType) -> Callable[[type[T]], type[T]]:
    """Specifies the scope type of an injectable class.

    :param scope_type: The lifetime scope of the created instances.
    :type scope_type: InjectableScopeType, optional
    :return: A decorator that returns the same class that it decorates.
    :rtype: Callable[[type[T]], type[T]]
    """
    def decorator(wrapped_class: type[T]) -> type[T]:
        registration = get_or_add_attribute(
            wrapped_class,
            InjectableTypeRegistration.PROPERTY_NAME,
            # TODO https://github.com/PyCQA/pylint/issues/6550
            lambda: InjectableTypeRegistration(injectable_type=wrapped_class) # pylint: disable=unexpected-keyword-arg
        )
        registration.scope = scope_type
        return wrapped_class

    return decorator
