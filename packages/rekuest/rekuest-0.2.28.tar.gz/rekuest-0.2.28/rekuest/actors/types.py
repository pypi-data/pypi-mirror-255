from typing import Protocol, runtime_checkable, Callable, Awaitable, Any
from rekuest.structures.registry import StructureRegistry
from rekuest.messages import Provision
from rekuest.rath import RekuestRath
from rekuest.api.schema import TemplateFragment, PortGroupInput, AssignationStatus
from rekuest.definition.define import DefinitionInput
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field
import uuid


class Passport(BaseModel):
    instance_id: str
    provision: str
    parent: Optional[str]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class Assignment(BaseModel):
    assignation: Optional[str]
    parent: Optional[str]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    args: List[Any] = Field(default_factory=list)
    user: Optional[str]
    reference: Optional[str]


class AssignmentUpdate(BaseModel):
    assignment: str
    status: AssignationStatus
    message: Optional[str]
    parent: Optional[str]
    progress: Optional[int]
    returns: Optional[List[Any]]


class Unassignment(BaseModel):
    assignation: str
    id: str


@runtime_checkable
class ActorBuilder(Protocol):
    def __call__(
        self,
        passport: Passport,
        transport: Any,
        collector: Any,
        definition_registry: Any,
    ) -> Any:
        ...


@runtime_checkable
class Actifier(Protocol):
    """An actifier is a function that takes a callable and a structure registry
    as well as optional arguments

    """

    def __call__(
        self,
        function: Callable,
        structure_registry: StructureRegistry,
        port_groups: Optional[List[PortGroupInput]] = None,
        groups: Optional[Dict[str, List[str]]] = None,
        is_test_for: Optional[List[str]] = None,
        **kwargs
    ) -> Tuple[DefinitionInput, ActorBuilder]:
        ...


@runtime_checkable
class OnProvide(Protocol):
    """An on_provide is a function that takes a provision and a transport and returns
    an awaitable

    """

    def __call__(
        self,
        passport: Passport,
    ) -> Awaitable[Any]:
        ...


@runtime_checkable
class OnUnprovide(Protocol):
    """An on_provide is a function that takes a provision and a transport and returns
    an awaitable

    """

    def __call__(self) -> Awaitable[Any]:
        ...
