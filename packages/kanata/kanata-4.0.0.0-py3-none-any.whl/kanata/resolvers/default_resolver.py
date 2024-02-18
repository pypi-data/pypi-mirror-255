from typing import Any, TypeVar

import structlog

from kanata.constants import LOGGER_NAME
from kanata.exceptions import DependencyResolutionException
from kanata.models import (
    InjectableInstanceRegistration, InjectableRegistration, InjectableScopeType,
    InjectableTypeRegistration
)
from .default_resolver_options import DefaultResolverOptions
from .resolver_base import ResolverBase
from .resolver_context import ResolverContext

TInjectable = TypeVar("TInjectable")

class DefaultResolver(ResolverBase):
    """Default implementation of a resolver."""

    def __init__(
        self,
        options: DefaultResolverOptions | None = None
    ) -> None:
        super().__init__()
        self.__options = options or DefaultResolverOptions()
        self.__log = structlog.get_logger(logger_name=LOGGER_NAME)

    def resolve(
        self,
        context: ResolverContext,
        registration: InjectableRegistration,
        injectable_type: type
    ) -> Any:
        if isinstance(registration, InjectableInstanceRegistration):
            return registration.injectable_instance
        if not isinstance(registration, InjectableTypeRegistration):
            raise DependencyResolutionException(
                type(registration),
                "Unsupported type of injectable registration."
            )

        # For singleton and scoped injectables, we know that there exists one and only one
        # instance for all of the associated contracts, therefore we can find and return
        # that specific one if it is created already.
        if (
            registration.scope in (InjectableScopeType.SINGLETON, InjectableScopeType.SCOPED)
            and (matching_instances := context.instances.get_instances_by_injectable(
                injectable_type,
                registration.scope
            ))
            and (instance := next(iter(matching_instances), None))
        ):
            return instance

        return injectable_type(
            *self._get_dependencies(
                context,
                injectable_type,
                registration.scope
            )
        )

    def _on_captive_dependency_detected(
        self,
        injectable: type,
        contract: type
    ) -> None:
        # Unless turned off, issue a warning, because a captive dependency
        # may be the result of a coding error, as it's generally undesirable.
        error_message = (
            "Detected captive dependency."
            f" Singleton '{injectable}' depends on transient '{contract}'."
        )
        if not self.__options.suppress_captive_dependency_warnings:
            self.__log.warn(error_message)
        if self.__options.raise_on_captive_dependency:
            raise DependencyResolutionException(injectable, error_message)
