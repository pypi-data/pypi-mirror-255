from typing import Callable, Dict, List, Optional, Tuple, Union

from pydantic import Field
from rekuest.actors.base import Actor
from rekuest.actors.types import ActorBuilder, Passport
from rekuest.agents.errors import ProvisionException
from rekuest.api.schema import (
    TemplateFragment,
    acreate_template,
    AssignationStatus,
    ProvisionStatus,
)
from rekuest.definition.registry import (
    DefinitionRegistry,
    get_current_definition_registry,
)
from rekuest.definition.registry import get_default_definition_registry
from rekuest.rath import RekuestRath
from rekuest.definition.validate import auto_validate
import asyncio
from rekuest.agents.transport.base import AgentTransport
from rekuest.messages import Assignation, Unassignation, Unprovision, Provision, Inquiry
from koil import unkoil
from koil.composition import KoiledModel
import logging
from rekuest.collection.collector import Collector
import uuid
from rekuest.agents.errors import AgentException
from rekuest.actors.transport.local_transport import (
    AgentActorTransport,
    ProxyActorTransport,
)
from rekuest.actors.transport.types import ActorTransport
from rekuest.actors.types import Assignment, Unassignment
from .transport.errors import DefiniteConnectionFail, CorrectableConnectionFail
from rekuest.api.schema import aget_template
from rekuest.agents.extension import AgentExtension
from rekuest.agents.hooks import HooksRegistry, get_default_hook_registry
from typing import Any


logger = logging.getLogger(__name__)


class BaseAgent(KoiledModel):
    """Agent

    Agents are the governing entities for every app. They are responsible for
    managing the lifecycle of the direct actors that are spawned from them through arkitekt.

    Agents are nothing else than actors in the classic distributed actor model, but they are
    always provided when the app starts and they do not provide functionality themselves but rather
    manage the lifecycle of the actors that are spawned from them.

    The actors that are spawned from them are called guardian actors and they are the ones that+
    provide the functionality of the app. These actors can then in turn spawn other actors that
    are not guardian actors. These actors are called non-guardian actors and their lifecycle is
    managed by the guardian actors that spawned them. This allows for a hierarchical structure
    of actors that can be spawned from the agents.


    """

    instance_id: str = "main"
    rath: RekuestRath
    transport: AgentTransport
    definition_registry: DefinitionRegistry = Field(
        default_factory=get_default_definition_registry
    )
    extensions: Dict[str, AgentExtension] = Field(default_factory=dict)
    collector: Collector = Field(default_factory=Collector)
    managed_actors: Dict[str, Actor] = Field(default_factory=dict)

    interface_template_map: Dict[str, TemplateFragment] = Field(
        default_factory=dict,
    )
    template_interface_map: Dict[str, str] = Field(default_factory=dict)
    provision_passport_map: Dict[str, Passport] = Field(default_factory=dict)
    managed_assignments: Dict[str, Assignment] = Field(default_factory=dict)
    hook_registry: HooksRegistry = Field(default_factory=get_default_hook_registry)

    running: bool = False
    _context: Dict[str, Any] = None

    def register_extension(self, name: str, extension: AgentExtension):
        self.extensions[name] = extension

    async def process(
        self, message: Union[Assignation, Provision, Unassignation, Unprovision]
    ):
        logger.info(f"Agent processes {message}")

        if isinstance(message, Assignation):
            if message.provision in self.provision_passport_map:
                passport = self.provision_passport_map[message.provision]
                actor = self.managed_actors[passport.id]

                # Converting assignation to Assignment
                message = Assignment(
                    assignation=message.assignation,
                    args=message.args,
                    user=message.user,
                )
                self.managed_assignments[message.assignation] = message
                await actor.apass(message)
            else:
                logger.warning(
                    "Received assignation for a provision that is not running"
                    f"Managed: {self.provision_passport_map} Received: {message.provision}"
                )
                await self.transport.change_assignation(
                    message.assignation,
                    status=AssignationStatus.CRITICAL,
                    message="Actor was no longer running or not managed",
                )

        elif isinstance(message, Inquiry):
            logger.info("Received Inquiry")
            for assignation in message.assignations:
                if assignation.assignation in self.managed_assignments:
                    logger.debug(
                        f"Received Inquiry for {assignation.assignation} and it was found. Ommiting setting Criticial"
                    )
                else:
                    logger.warning(
                        f"Did no find Inquiry for {assignation.assignation} and it was found. Setting Criticial"
                    )
                    await self.transport.change_assignation(
                        message.assignation,
                        status=AssignationStatus.CRITICAL,
                        message="Actor was no longer running or not managed",
                    )

        elif isinstance(message, Unassignation):
            if message.assignation in self.managed_assignments:
                passport = self.provision_passport_map[message.provision]
                actor = self.managed_actors[passport.id]
                assignment = self.managed_assignments[message.assignation]

                # Converting unassignation to unassignment
                unass = Unassignment(assignation=message.assignation, id=assignment.id)

                await actor.apass(unass)
            else:
                logger.warning(
                    "Received unassignation for a provision that is not running"
                    f"Managed: {self.provision_passport_map} Received: {message.provision}"
                )
                await self.transport.change_assignation(
                    message.assignation,
                    status=AssignationStatus.CRITICAL,
                    message="Actor was no longer running or not managed",
                )

        elif isinstance(message, Provision):
            # TODO: Check if the provision is already running
            try:
                status = await self.acheck_status_for_provision(message)
                await self.transport.change_provision(
                    message.provision,
                    status=status,
                    message="Actor was already running",
                )
            except KeyError as e:
                try:
                    await self.aspawn_actor_from_provision(message)
                except ProvisionException as e:
                    logger.error(
                        f"Error when spawing Actor for {message}", exc_info=True
                    )
                    await self.transport.change_provision(
                        message.provision, status=ProvisionStatus.DENIED, message=str(e)
                    )

        elif isinstance(message, Unprovision):
            if message.provision in self.provision_passport_map:
                passport = self.provision_passport_map[message.provision]
                actor = self.managed_actors[passport.id]
                await actor.acancel()
                await self.transport.change_provision(
                    message.provision,
                    status=ProvisionStatus.CANCELLED,
                    message=str("Actor was cancelled"),
                )
                del self.provision_passport_map[message.provision]
                del self.managed_actors[passport.id]
                logger.info("Actor stopped")

            else:
                await self.transport.change_provision(
                    message.provision,
                    status=ProvisionStatus.CANCELLED,
                    message=str(
                        "Actor was no longer active when we received this message"
                    ),
                )
                logger.warning(
                    f"Received Unprovision for never provisioned provision {message}"
                )

        else:
            raise AgentException(f"Unknown message type {type(message)}")

    async def aregister_definitions(self, instance_id: Optional[str] = None):
        """Registers the definitions that are defined in the definition registry

        This method is called by the agent when it starts and it is responsible for
        registering the definitions that are defined in the definition registry. This
        is done by sending the definitions to arkitekt and then storing the templates
        that are returned by arkitekt in the agent's internal data structures.

        You can implement this method in your agent subclass if you want define preregistration
        logic (like registering definitions in the definition registry).
        """
        for i in self.extensions.values():
            await i.aregister_definitions(
                self.definition_registry,
                instance_id=instance_id or self.instance_id,
            )  # Lets register all the extensions

        for (
            interface,
            definition,
        ) in self.definition_registry.definitions.items():
            # Defined Node are nodes that are not yet reflected on arkitekt (i.e they dont have an instance
            # id so we are trying to send them to arkitekt)
            try:
                arkitekt_template = await acreate_template(
                    definition=definition,
                    interface=interface,
                    instance_id=instance_id or self.instance_id,
                    rath=self.rath,
                )
            except Exception as e:
                logger.info(
                    f"Error Creating template for {definition} at interface {interface}"
                )
                raise e

            self.interface_template_map[interface] = arkitekt_template
            self.template_interface_map[arkitekt_template.id] = interface

    async def acheck_status_for_provision(
        self, provision: Provision
    ) -> ProvisionStatus:
        passport = self.provision_passport_map[provision.provision]
        actor = self.managed_actors[passport.id]
        return await actor.aget_status()

    async def abuild_actor_for_template(
        self, template: TemplateFragment, passport: Passport, transport: ActorTransport
    ) -> Actor:
        if not template.extensions:
            try:
                actor_builder = self.definition_registry.get_builder_for_interface(
                    template.interface
                )

            except KeyError as e:
                raise ProvisionException(
                    f"No Actor Builder found for template {template.interface} and no extensions specified"
                )

            actor = actor_builder(
                passport=passport,
                transport=transport,
                collector=self.collector,
                agent=self,
            )

        for i in template.extensions:
            if i in self.extensions:
                extension = self.extensions[i]
                try:
                    actor = await extension.aspawn_actor_from_template(
                        template, passport, transport, self
                    )
                except Exception as e:
                    raise ProvisionException(
                        "Error spawning actor from extension"
                    ) from e
                if actor:
                    # First extension that manages to spawn an actor wins
                    break

        if not actor:
            raise ProvisionException("No extensions managed to spawn an actor")

        return actor

    async def on_assign_change(self, assignment: Assignment, *args, **kwargs):
        await self.transport.change_assignation(assignment.assignation, *args, **kwargs)

    async def on_assign_log(self, assignment: Assignment, *args, **kwargs):
        await self.transport.log_to_assignation(assignment.assignation, *args, **kwargs)

    async def on_actor_change(self, passport: Passport, *args, **kwargs):
        await self.transport.change_provision(passport.provision, *args, **kwargs)

    async def on_actor_log(self, passport: Passport, *args, **kwargs):
        await self.transport.log_to_provision(passport.provision, *args, **kwargs)

    async def aspawn_actor_from_provision(self, provision: Provision) -> Actor:
        """Spawns an Actor from a Provision. This function closely mimics the
        spawining protocol within an actor. But maps template"""

        template = await aget_template(
            provision.template,
            rath=self.rath,
        )

        passport = Passport(provision=provision.provision, instance_id=self.instance_id)

        transport = ProxyActorTransport(
            passport=passport,
            on_assign_change=self.on_assign_change,
            on_assign_log=self.on_assign_log,
            on_actor_change=self.on_actor_change,
            on_actor_log=self.on_actor_log,
        )

        actor = await self.abuild_actor_for_template(template, passport, transport)

        await actor.arun()  # TODO: Maybe move this outside?
        self.managed_actors[actor.passport.id] = actor
        self.provision_passport_map[provision.provision] = actor.passport

        return actor

    async def astep(self):
        await self.process(await self.transport.aget_message())

    async def astart(self, instance_id: Optional[str] = None):
        # TODO: Maybe we should check if we are already running
        await self.aregister_definitions(instance_id=instance_id)

        self._context = await self.hook_registry.arun_startup()
        await self.hook_registry.arun_background(self._context)

        await self.transport.aconnect(instance_id or self.instance_id)

    async def aget_context(self):
        if not self._context:
            raise AgentException(
                "Context not initialized. Because agent is not running"
            )
        return self._context

    async def astop(self):
        # Cancel all the tasks
        cancelations = [actor.acancel() for actor in self.managed_actors.values()]
        # just stopping the actor, not cancelling the provision..

        for c in cancelations:
            try:
                await c
            except asyncio.CancelledError:
                pass

        await self.hook_registry.astop_background()

        self.managed_actors = {}
        self.provision_passport_map = {}  # Clearing the managed actors

        await self.transport.adisconnect()
        self.running = False

    def step(self, *args, **kwargs):
        return unkoil(self.astep, *args, **kwargs)

    def start(self, *args, **kwargs):
        return unkoil(self.astart, *args, **kwargs)

    def provide(self, *args, **kwargs):
        return unkoil(self.aprovide, *args, **kwargs)

    async def aprovide(self, instance_id: Optional[str] = None):
        logger.info(f"Launching provisioning task. We are running {instance_id}")
        try:
            await self.astart(instance_id=instance_id)
            while True:
                self.running = True
                await self.astep()
        except asyncio.CancelledError:
            await self.astop()
            logger.info("Provisioning task cancelled. We are running")

    async def __aenter__(self):
        await self.transport.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.astop()
        await self.transport.__aexit__(exc_type, exc_val, exc_tb)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
