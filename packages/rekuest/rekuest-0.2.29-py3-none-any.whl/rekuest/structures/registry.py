import contextvars
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    OrderedDict,
    Dict,
    Optional,
    Type,
    List,
    TypeVar,
    Protocol,
    runtime_checkable,
)

from rekuest.api.schema import (
    ChoiceInput,
    ReturnWidgetInput,
    WidgetInput,
    WidgetInput,
    ReturnWidgetInput,
    AnnotationInput,
    Scope,
    PortInput,
    EffectInput,
    ChildPortInput,
    PortKindInput,
)
from pydantic import BaseModel, Field
import inspect
from .errors import (
    StructureDefinitionError,
    StructureOverwriteError,
    StructureRegistryError,
)
from .types import PortBuilder, FullFilledStructure
from .hooks.types import RegistryHook
from .hooks.default import get_default_hooks
from .hooks.errors import HookError

current_structure_registry = contextvars.ContextVar("current_structure_registry")


T = TypeVar("T")

Identifier = str
""" A unique identifier of this structure on the arkitekt platform"""
GroupMap = Dict[str, List[str]]
WidgetMap = Dict[str, List[WidgetInput]]
ReturnWidgetMap = Dict[str, List[ReturnWidgetInput]]
EffectsMap = Dict[str, List[EffectInput]]


def cls_to_identifier(cls: Type) -> Identifier:
    return f"{cls.__module__.lower()}.{cls.__name__.lower()}"


class StructureRegistry(BaseModel):
    copy_from_default: bool = False
    allow_overwrites: bool = True
    allow_auto_register: bool = True
    cls_to_identifier: Callable[[Type], Identifier] = cls_to_identifier

    identifier_structure_map: Dict[str, Type] = Field(
        default_factory=dict, exclude=True
    )
    identifier_scope_map: Dict[str, Scope] = Field(default_factory=dict, exclude=True)
    _identifier_expander_map: Dict[str, Callable[[str], Awaitable[Any]]] = {}
    _identifier_shrinker_map: Dict[str, Callable[[Any], Awaitable[str]]] = {}
    _identifier_collecter_map: Dict[str, Callable[[Any], Awaitable[None]]] = {}
    _identifier_predicate_map: Dict[str, Callable[[Any], bool]] = {}
    _identifier_builder_map: Dict[str, PortBuilder] = {}

    _structure_convert_default_map: Dict[str, Callable[[Any], str]] = {}
    _structure_identifier_map: Dict[Type, str] = {}
    _structure_default_widget_map: Dict[Type, WidgetInput] = {}
    _structure_default_returnwidget_map: Dict[Type, ReturnWidgetInput] = {}
    _structure_annotation_map: Dict[Type, Type] = {}

    registry_hooks: OrderedDict[str, RegistryHook] = Field(
        default_factory=get_default_hooks
    )
    _fullfilled_structures_map: Dict[Type, FullFilledStructure] = {}

    _token: contextvars.Token = None

    def get_expander_for_identifier(self, key):
        try:
            return self._identifier_expander_map[key]
        except KeyError as e:
            raise StructureRegistryError(f"Expander for {key} is not registered") from e

    def get_collector_for_identifier(self, key):
        try:
            return self._identifier_collecter_map[key]
        except KeyError as e:
            raise StructureRegistryError(
                f"Collector for {key} is not registered"
            ) from e

    def get_shrinker_for_identifier(self, key):
        try:
            return self._identifier_shrinker_map[key]
        except KeyError as e:
            raise StructureRegistryError(f"Shrinker for {key} is not registered") from e

    def register_expander(self, key, expander):
        self._identifier_expander_map[key] = expander

    def get_widget_input(self, cls) -> Optional[WidgetInput]:
        return self._structure_default_widget_map.get(cls, None)

    def get_returnwidget_input(self, cls) -> Optional[ReturnWidgetInput]:
        return self._structure_default_returnwidget_map.get(cls, None)

    def get_predicator_for_identifier(
        self, identifier: str
    ) -> Optional[Callable[[Any], bool]]:
        return self._identifier_predicate_map[identifier]

    def get_identifier_for_structure(self, cls):
        try:
            return self._structure_identifier_map[cls]
        except KeyError as e:
            if self.allow_auto_register:
                try:
                    self.register_as_structure(cls)
                    return self._structure_identifier_map[cls]
                except StructureDefinitionError as e:
                    raise StructureDefinitionError(
                        f"{cls} was not registered and could not be registered"
                        " automatically"
                    ) from e
            else:
                raise StructureRegistryError(
                    f"{cls} is not registered and allow_auto_register is set to False."
                    " Please make sure to register this type beforehand or set"
                    " allow_auto_register to True"
                ) from e

    def get_scope_for_identifier(self, identifier: str):
        return self.identifier_scope_map[identifier]

    def get_default_converter_for_structure(self, cls):
        try:
            return self._structure_convert_default_map[cls]
        except KeyError as e:
            if self.allow_auto_register:
                try:
                    self.register_as_structure(cls)
                    return self._structure_convert_default_map[cls]
                except StructureDefinitionError as e:
                    raise StructureDefinitionError(
                        f"{cls} was not registered and not be no default converter"
                        " could be registered automatically."
                    ) from e
            else:
                raise StructureRegistryError(
                    f"{cls} is not registered and allow_auto_register is set to False."
                    " Please register a 'conver_default' function for this type"
                    " beforehand or set allow_auto_register to True. Otherwise you"
                    " cant use this type with a default"
                ) from e

    def register_as_structure(
        self,
        cls: Type,
        identifier: str = None,
        scope: Scope = Scope.LOCAL,
        aexpand: Callable[
            [
                str,
            ],
            Awaitable[Any],
        ] = None,
        ashrink: Callable[
            [
                any,
            ],
            Awaitable[str],
        ] = None,
        acollect: Callable[
            [
                str,
            ],
            Awaitable[Any],
        ] = None,
        predicate: Callable[[Any], bool] = None,
        convert_default: Callable[[Any], str] = None,
        default_widget: Optional[WidgetInput] = None,
        default_returnwidget: Optional[ReturnWidgetInput] = None,
    ):
        fullfilled_structure = None
        for key, hook in self.registry_hooks.items():
            try:
                if hook.is_applicable(cls):
                    try:
                        fullfilled_structure = hook.apply(
                            cls,
                            identifier=identifier,
                            scope=scope,
                            aexpand=aexpand,
                            ashrink=ashrink,
                            acollect=acollect,
                            predicate=predicate,
                            convert_default=convert_default,
                            default_widget=default_widget,
                            default_returnwidget=default_returnwidget,
                        )
                        break  # we found a hook that applies
                    except HookError as e:
                        raise StructureDefinitionError(
                            f"Hook {key} failed to apply to {cls}"
                        ) from e
            except Exception as e:
                raise StructureDefinitionError(
                    f"Hook {key} does not correctly implement its interface. Please contact the developer of this hook."
                ) from e

        if fullfilled_structure is None:
            raise StructureDefinitionError(
                f"No hook was able to apply to {cls}. Please check your hooks {self.registry_hooks}"
            )

        self.fullfill_registration(fullfilled_structure)

    def get_fullfilled_structure_for_cls(self, cls: Type) -> FullFilledStructure:
        try:
            return self._fullfilled_structures_map[cls]
        except KeyError as e:
            if self.allow_auto_register:
                try:
                    self.register_as_structure(cls)
                    return self._fullfilled_structures_map[cls]
                except StructureDefinitionError as e:
                    raise StructureDefinitionError(
                        f"{cls} was not registered and could not be registered"
                        " automatically"
                    ) from e
            else:
                raise StructureRegistryError(
                    f"{cls} is not registered and allow_auto_register is set to False."
                    " Please make sure to register this type beforehand or set"
                    " allow_auto_register to True"
                ) from e

    def fullfill_registration(
        self,
        fullfilled_structure: FullFilledStructure,
    ):
        if (
            fullfilled_structure.identifier in self.identifier_structure_map
            and not self.allow_overwrites
        ):
            raise StructureOverwriteError(
                f"{fullfilled_structure.identifier} is already registered. Previously registered"
                f" {self.identifier_structure_map[fullfilled_structure.identifier]}"
            )

        self._identifier_expander_map[
            fullfilled_structure.identifier
        ] = fullfilled_structure.aexpand
        self._identifier_collecter_map[
            fullfilled_structure.identifier
        ] = fullfilled_structure.acollect
        self._identifier_shrinker_map[
            fullfilled_structure.identifier
        ] = fullfilled_structure.ashrink
        self._identifier_predicate_map[
            fullfilled_structure.identifier
        ] = fullfilled_structure.predicate

        self.identifier_structure_map[
            fullfilled_structure.identifier
        ] = fullfilled_structure.cls
        self.identifier_scope_map[
            fullfilled_structure.identifier
        ] = fullfilled_structure.scope
        self._structure_identifier_map[
            fullfilled_structure.cls
        ] = fullfilled_structure.identifier
        self._structure_default_widget_map[
            fullfilled_structure.cls
        ] = fullfilled_structure.default_widget
        self._structure_default_returnwidget_map[
            fullfilled_structure.cls
        ] = fullfilled_structure.default_returnwidget
        self._structure_convert_default_map[
            fullfilled_structure.cls
        ] = fullfilled_structure.convert_default

        self._fullfilled_structures_map[fullfilled_structure.cls] = fullfilled_structure

    def get_converter_for_annotation(self, annotation):
        try:
            return self._structure_annotation_map[annotation]
        except KeyError as e:
            raise StructureRegistryError(f"{annotation} is not registered") from e

    def get_port_for_cls(
        self,
        cls: Type,
        key: str,
        nullable: bool = False,
        description: Optional[str] = None,
        groups: List[str] = None,
        effects: Optional[EffectsMap] = None,
        label: Optional[str] = None,
        default: Any = None,
        assign_widget: Optional[WidgetInput] = None,
        return_widget: Optional[ReturnWidgetInput] = None,
    ) -> PortInput:
        structure = self.get_fullfilled_structure_for_cls(cls)

        identifier = structure.identifier
        scope = structure.scope
        default_converter = structure.convert_default
        assign_widget = assign_widget or structure.default_widget
        return_widget = return_widget or structure.default_returnwidget

        try:
            return PortInput(
                kind=PortKindInput.STRUCTURE,
                identifier=identifier,
                assignWidget=assign_widget,
                scope=scope,
                returnWidget=return_widget,
                key=key,
                label=label,
                default=default_converter(default) if default else None,
                nullable=nullable,
                effects=effects,
                description=description,
                groups=groups,
            )
        except Exception as e:
            raise StructureRegistryError(
                f"Could not create port for {cls} with fullfilled structure {structure}"
            ) from e

    def get_child_port_and_default_converter_for_cls(
        self,
        cls: Type,
        nullable: bool = False,
        assign_widget: Optional[WidgetInput] = None,
        return_widget: Optional[ReturnWidgetInput] = None,
    ) -> PortInput:
        identifier = self.get_identifier_for_structure(cls)
        scope = self.get_scope_for_identifier(identifier)
        identifier = self.get_identifier_for_structure(cls)
        default_converter = self.get_default_converter_for_structure(cls)
        assign_widget = assign_widget or self.get_widget_input(cls)
        return_widget = return_widget or self.get_returnwidget_input(cls)

        return (
            ChildPortInput(
                kind=PortKindInput.STRUCTURE,
                identifier=identifier,
                scope=scope,
                nullable=nullable,
                assignWidget=assign_widget,
                returnWidget=return_widget,
            ),
            default_converter,
        )

    def register_annotation_converter(
        self,
        annotation: T,
        converter: Callable[[Type[T]], AnnotationInput],
        overwrite=False,
    ):
        if annotation in self._structure_annotation_map and not overwrite:
            raise StructureRegistryError(
                f"{annotation} is already registered: Specify overwrite=True to"
                " overwrite"
            )

        self._structure_annotation_map[annotation] = converter

    async def __aenter__(self):
        current_structure_registry.set(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        current_structure_registry.set(None)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


DEFAULT_STRUCTURE_REGISTRY = None


def get_current_structure_registry(allow_default=True):
    return current_structure_registry.get()
