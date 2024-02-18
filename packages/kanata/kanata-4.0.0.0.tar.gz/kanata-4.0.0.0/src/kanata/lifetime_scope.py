import types
from collections.abc import Iterable
from typing import Any, get_args

import structlog

from kanata.catalogs import IInjectableCatalog
from kanata.utils import get_dependent_contracts
from .constants import LOGGER_NAME
from .exceptions import DependencyResolutionException
from .graphs import BidirectedGraph
from .graphs.sorting import topological_sort
from .ilifetime_scope import ILifetimeScope, TInjectable
from .models import (
    ClosedGenericTypeId, ClosedGenericTypeInfo, InjectableInstanceRegistration,
    InjectableRegistration, InjectableScopeType, InjectableTypeRegistration, InstanceCollection
)
from .resolvers import DefaultResolver, IResolver, ResolverContext

class LifetimeScope(ILifetimeScope):
    """An injectable lifetime scope
    that manages the lifetimes of injectables
    and provides access to them."""

    def __init__(
        self,
        catalog: IInjectableCatalog,
        resolvers: tuple[IResolver, ...] | None = None,
        _parent: ILifetimeScope | None = None
    ) -> None:
        self.__catalog = catalog
        self.__resolvers: tuple[IResolver, ...] = resolvers or (DefaultResolver(),)
        self.__parent = _parent
        self.__log = structlog.get_logger(logger_name=LOGGER_NAME)
        self.__instances = InstanceCollection()
        # The below dictionaries are used for tracking
        # the dynamically created closed generic types.
        self.__closed_generic_type_infos_by_id = dict[ClosedGenericTypeId, ClosedGenericTypeInfo]()
        self.__closed_generic_type_infos_by_type = dict[type, ClosedGenericTypeInfo]()

    def resolve(self, injectable: type[TInjectable]) -> TInjectable:
        if self.__parent and self.__should_resolve_via_parent(injectable):
            return self.__parent.resolve(injectable)

        dependency_graph = self.__build_dependency_graph_for(injectable)
        resolver_context = ResolverContext(
            catalog=self.__catalog,
            closed_generic_types=self.__closed_generic_type_infos_by_id,
            instances=self.__instances
        )
        instance = None
        for current_injectable in topological_sort(dependency_graph, injectable):
            self.__log.debug("Resolving injectable", type=current_injectable)
            instance = self.__resolve_injectable(resolver_context, current_injectable)
            self.__log.debug("Resolved injectable", type=current_injectable)

        if not isinstance(instance, injectable):
            raise DependencyResolutionException(
                type(instance),
                (
                    "Got an unexpected type during dependency resolution."
                    " This is likely an error in the algorithm."
                )
            )

        return instance

    def create_child_scope(self) -> ILifetimeScope:
        return LifetimeScope(self.__catalog, self.__resolvers, _parent=self)

    @staticmethod
    def __get_injectable_scope_type(registration: InjectableRegistration) -> InjectableScopeType:
        match registration:
            case InjectableTypeRegistration():
                return registration.scope
            case InjectableInstanceRegistration():
                return InjectableScopeType.SINGLETON
            case _:
                raise DependencyResolutionException(
                    type(registration),
                    "Unsupported type of injectable registration."
                )

    def __build_dependency_graph_for(self, injectable: type) -> BidirectedGraph[type]:
        graph: BidirectedGraph[type] = BidirectedGraph()
        injectables_to_resolve: list[type] = [injectable]
        while injectables_to_resolve:
            dependee_injectable = injectables_to_resolve.pop()
            if not graph.try_add_node(dependee_injectable):
                # This type's dependency chain has already been mapped.
                continue

            self.__log.debug("Gathering dependent contracts", dependee=dependee_injectable)
            dependent_contracts = get_dependent_contracts(dependee_injectable)
            for dependent_contract, is_multi in dependent_contracts:
                self.__log.debug(
                    "Found dependent contract",
                    dependee=dependee_injectable,
                    dependent=dependent_contract,
                    is_multi=is_multi
                )
                dependent_registrations = self.__catalog.get_registrations_by_contract(
                    dependent_contract
                )
                if len(dependent_registrations) == 0 and not is_multi:
                    raise DependencyResolutionException(
                        dependee_injectable,
                        "Cannot satisfy the dependency"
                        f" of {dependee_injectable} on {dependent_contract}."
                    )

                injectables_to_resolve.extend(
                    self.__mark_dependent_types(
                        graph,
                        dependee_injectable,
                        dependent_contract,
                        dependent_registrations
                    )
                )

        return graph

    def __resolve_injectable(
        self,
        resolver_context: ResolverContext,
        injectable: type
    ) -> Any:
        if closed_generic_type_info := self.__closed_generic_type_infos_by_type.get(injectable):
            registration = closed_generic_type_info.origin_registration
        else:
            registration = self.__catalog.get_registration_by_injectable(injectable)
            if not registration:
                raise DependencyResolutionException(
                    injectable,
                    f"Cannot find the registration for injectable '{injectable}'."
                    " It is possible that this type is not an injectable."
                )

        for resolver in self.__resolvers:
            if not (instance := resolver.resolve(resolver_context, registration, injectable)):
                continue

            self.__log.debug("Instantiated injectable", injectable=injectable)
            scope = LifetimeScope.__get_injectable_scope_type(registration)
            self.__instances.add_instance(scope, injectable, instance)

            return instance

        raise DependencyResolutionException(
            injectable,
            "None of the resolvers could resolve an instance of the specified type."
        )

    def __should_resolve_via_parent(
        self,
        injectable: type
    ) -> bool:
        registration = self.__catalog.get_registration_by_injectable(injectable)
        match registration:
            case InjectableTypeRegistration(scope=InjectableScopeType.SINGLETON): return True
            case InjectableInstanceRegistration(): return True
            case _: return False

    def __mark_dependent_types(
        self,
        graph: BidirectedGraph[type],
        dependee_injectable: type,
        dependent_contract: type,
        dependent_registrations: Iterable[InjectableRegistration]
    ) -> Iterable[type]:
        # Mark each implementation as a dependency. At this point,
        # it is possible only one of them will be needed by
        # this specific type. But we'll make sure all are initialized
        # as they may be needed later.
        dependent_types = []
        for dependent_registration in dependent_registrations:
            injectable_type = self.__get_injectable_type(
                dependent_contract,
                dependent_registration
            )

            graph.try_add_node(dependee_injectable)
            graph.try_add_edge(dependee_injectable, injectable_type)
            dependent_types.append(injectable_type)
            self.__log.debug(
                "Identified dependent injectable",
                dependee=dependee_injectable,
                dependent=injectable_type
            )

        return dependent_types

    def __get_injectable_type(
        self,
        dependent_contract: type,
        dependent_registration: InjectableRegistration
    ) -> type:
        match dependent_registration:
            case InjectableTypeRegistration():
                generic_type = self.__get_or_create_generic_type(
                    dependent_registration,
                    dependent_contract
                )
                return (
                    generic_type.closed_generic_type if generic_type
                    else dependent_registration.injectable_type
                )
            case InjectableInstanceRegistration():
                return type(dependent_registration.injectable_instance)
            case _:
                raise DependencyResolutionException(
                    type(dependent_registration),
                    "Unsupported type of injectable registration."
                )

    def __get_or_create_generic_type(
        self,
        registration: InjectableTypeRegistration,
        contract: type
    ) -> ClosedGenericTypeInfo | None:
        if not registration.is_generic:
            return None

        type_arguments = get_args(contract)
        if len(type_arguments) != 1:
            raise DependencyResolutionException(
                contract,
                "The generic contract must have one single generic type argument."
            )

        type_argument = type_arguments[0]
        generic_type_id = ClosedGenericTypeId(registration.injectable_type, type_argument)

        # Avoid creating the same type multiple times.
        if existing_type := self.__closed_generic_type_infos_by_id.get(generic_type_id):
            return existing_type

        closed_generic_type = types.new_class(
            f"{registration.injectable_type.__name__}Of{type_argument.__name__}",
            # Ignoring the type here, because the linter isn't aware this type is a Generic[T].
            (registration.injectable_type[type_argument],), # type: ignore
            None,
            lambda ns: ns.update({
                "generic_type_argument": property(lambda _: type_argument)
            })
        )
        generic_type_info = ClosedGenericTypeInfo(
            closed_generic_type=closed_generic_type,
            generic_type_argument=type_argument,
            origin_registration=registration
        )

        # Save the newly created type to avoid recreating it if it's needed later.
        self.__closed_generic_type_infos_by_id[generic_type_id] = generic_type_info
        self.__closed_generic_type_infos_by_type[closed_generic_type] = generic_type_info

        return generic_type_info
