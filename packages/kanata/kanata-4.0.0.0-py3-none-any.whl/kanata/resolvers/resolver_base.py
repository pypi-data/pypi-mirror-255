from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, get_args

from kanata.exceptions import DependencyResolutionException
from kanata.models import (
    ClosedGenericTypeId, ClosedGenericTypeInfo, IInstanceCollection, InjectableInstanceRegistration,
    InjectableRegistration, InjectableScopeType, InjectableTypeRegistration
)
from kanata.utils import get_dependent_contracts
from .iresolver import IResolver
from .resolver_context import ResolverContext

_SCOPE_TYPE_RANKS: dict[InjectableScopeType, int] = {
    InjectableScopeType.TRANSIENT: 0,
    InjectableScopeType.SCOPED: 1,
    InjectableScopeType.SINGLETON: 2
}

class ResolverBase(ABC, IResolver):
    """Abstract base class for a resolver."""

    @abstractmethod
    def resolve(
        self,
        context: ResolverContext,
        registration: InjectableRegistration,
        injectable_type: type
    ) -> Any:
        ...

    @staticmethod
    def _is_captive_dependency(
        dependee_scope: InjectableScopeType,
        dependent_scope: InjectableScopeType
    ) -> bool:
        """Determines if the dependee and dependent scopes
        result in a captive dependency.

        :param dependee_scope: The scope of the dependee.
        :type dependee_scope: InjectableScopeType
        :param dependent_scope: The scope of the dependent.
        :type dependent_scope: InjectableScopeType
        :return: True, if a captive dependency is detected.
        :rtype: bool
        """

        ranked_scopes = sorted(
            (dependee_scope, dependent_scope),
            key=lambda i: _SCOPE_TYPE_RANKS[i]
        )
        return ranked_scopes[0] != dependee_scope

    def _on_captive_dependency_detected(
        self,
        injectable: type,
        contract: type
    ) -> None:
        """Invoked when a captive dependency is detected
        so that the resolver can handle the situation.

        This method should be overridden by subclasses
        and it does nothing by default.

        :param injectable: The type of the causing injectable.
        :type injectable: type
        :param contract: The type of the dependent contract.
        :type contract: type
        """

    def _get_dependencies(
        self,
        context: ResolverContext,
        injectable: type,
        dependee_scope: InjectableScopeType
    ) -> list[Any]:
        """Gets the dependencies of the specified injectable.

        :param context: Contextual information for the resolver.
        :type context: ResolverContext
        :param injectable: The type of the injectable for which to get the dependencies.
        :type injectable: type
        :param dependee_scope: The scope of the dependee.
        :type dependee_scope: InjectableScopeType
        :raises DependencyResolutionException: Raised when a dependency cannot be satisfied.
        :return: The list of dependencies.
        :rtype: list[Any]
        """

        dependent_contracts = get_dependent_contracts(injectable)
        dependent_injectables = list[Any]()
        for dependent_contract, is_multi in dependent_contracts:
            candidate_instances = self.__get_candidate_dependent_instances(
                context,
                injectable,
                dependee_scope,
                dependent_contract
            )

            if is_multi:
                dependent_injectables.append(tuple(candidate_instances))
            elif len(candidate_instances) > 0:
                dependent_injectables.append(candidate_instances[0])
            else:
                raise DependencyResolutionException(
                    injectable,
                    (
                        "Cannot satisfy the dependency"
                        f" of '{injectable}' on '{dependent_contract}'."
                    )
                )

        return dependent_injectables

    @staticmethod
    def __get_candidates_by_type_registration(
        closed_generic_types: dict[ClosedGenericTypeId, ClosedGenericTypeInfo],
        instances: IInstanceCollection,
        registration: InjectableTypeRegistration,
        dependent_contract: type
    ) -> Iterable[Any]:
        return (
            ResolverBase.__get_closed_generic_instances(
                closed_generic_types,
                instances,
                registration,
                dependent_contract
            )
            if registration.is_generic
            else instances.get_instances_by_injectable(
                registration.injectable_type,
                registration.scope
            )
        )

    @staticmethod
    def __get_closed_generic_instances(
        closed_generic_types: dict[ClosedGenericTypeId, ClosedGenericTypeInfo],
        instances: IInstanceCollection,
        origin_registration: InjectableTypeRegistration,
        contract_type: type
    ) -> Iterable[Any]:
        type_argument = get_args(contract_type)[0]
        generic_type_id = ClosedGenericTypeId(origin_registration.injectable_type, type_argument)
        if not (closed_generic_type_info := closed_generic_types.get(generic_type_id)):
            return ()

        return instances.get_instances_by_injectable(
            closed_generic_type_info.closed_generic_type,
            origin_registration.scope
        )

    def __get_candidate_dependent_instances(
        self,
        context: ResolverContext,
        injectable: type,
        dependee_scope: InjectableScopeType,
        dependent_contract: type
    ) -> list[Any]:
        registrations = context.catalog.get_registrations_by_contract(dependent_contract)
        candidate_instances = []
        for registration in registrations:
            if isinstance(registration, InjectableTypeRegistration):
                if ResolverBase._is_captive_dependency(dependee_scope, registration.scope):
                    self._on_captive_dependency_detected(injectable, dependent_contract)

                candidate_instances.extend(
                    ResolverBase.__get_candidates_by_type_registration(
                        context.closed_generic_types,
                        context.instances,
                        registration,
                        dependent_contract
                    )
                )
            elif isinstance(registration, InjectableInstanceRegistration):
                candidate_instances.append(registration.injectable_instance)
            else: raise DependencyResolutionException(
                type(registration),
                "Unsupported type of injectable registration."
            )

        return candidate_instances
