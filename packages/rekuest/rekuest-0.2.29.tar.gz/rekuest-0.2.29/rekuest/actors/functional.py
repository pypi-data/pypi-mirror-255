import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable
from koil.helpers import iterate_spawned, run_spawned, iterate_processed, run_processed
from pydantic import BaseModel, Field
from rekuest.actors.base import SerializingActor
from rekuest.messages import Assignation, Provision
from rekuest.api.schema import AssignationStatus, ProvisionFragment
from rekuest.structures.serialization.actor import expand_inputs, shrink_outputs
from rekuest.actors.contexts import AssignationContext
from rekuest.actors.types import OnProvide, OnUnprovide, Assignment, Unassignment
from rekuest.collection.collector import Collector
from rekuest.actors.transport.types import AssignTransport
from rekuest.structures.parse_collectables import parse_collectable
from rekuest.structures.errors import SerializationError

logger = logging.getLogger(__name__)


async def async_none_provide(prov: Provision):
    """Do nothing on provide"""
    return None


async def async_none_unprovide():
    """Do nothing on unprovide"""
    return None


class FunctionalActor(BaseModel):
    assign: Callable[..., Any]
    on_provide: OnProvide = Field(default=async_none_provide)
    on_unprovide: OnUnprovide = Field(default=async_none_unprovide)

    class Config:
        arbitrary_types_allowed = True


class AsyncFuncActor(SerializingActor):
    async def on_assign(
        self,
        assignment: Assignment,
        collector: Collector,
        transport: AssignTransport,
    ):
        try:
            params = await expand_inputs(
                self.definition,
                assignment.args,
                structure_registry=self.structure_registry,
                skip_expanding=not self.expand_inputs,
            )

            await transport.change(
                status=AssignationStatus.ASSIGNED,
            )

            async with AssignationContext(
                assignment=assignment, transport=transport, passport=self.passport
            ):
                returns = await self.assign(**params)

            returns = await shrink_outputs(
                self.definition,
                returns,
                structure_registry=self.structure_registry,
                skip_shrinking=not self.shrink_outputs,
            )

            collector.register(assignment, parse_collectable(self.definition, returns))

            await transport.change(
                status=AssignationStatus.RETURNED,
                returns=returns,
            )

        except SerializationError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except AssertionError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except Exception as e:
            logger.error("Assignation error", exc_info=True)
            await transport.change(
                status=AssignationStatus.ERROR,
                message=repr(e),
            )


class AsyncGenActor(SerializingActor):
    async def on_assign(
        self,
        assignment: Assignation,
        collector: Collector,
        transport: AssignTransport,
    ):
        try:
            params = await expand_inputs(
                self.definition,
                assignment.args,
                structure_registry=self.structure_registry,
                skip_expanding=not self.expand_inputs,
            )

            await transport.change(
                status=AssignationStatus.ASSIGNED,
            )

            async with AssignationContext(
                assignment=assignment, transport=transport, passport=self.passport
            ):
                async for returns in self.assign(**params):
                    returns = await shrink_outputs(
                        self.definition,
                        returns,
                        structure_registry=self.structure_registry,
                        skip_shrinking=not self.shrink_outputs,
                    )

                    collector.register(
                        assignment, parse_collectable(self.definition, returns)
                    )

                    await transport.change(
                        status=AssignationStatus.YIELD,
                        returns=returns,
                    )

            await transport.change(status=AssignationStatus.DONE)

        except SerializationError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except AssertionError as ex:
            await transport.change(
                status=AssignationStatus.ERROR,
                message=str(ex),
            )

        except Exception as ex:
            logger.error("Error in actor", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

            raise ex


class FunctionalFuncActor(FunctionalActor, AsyncFuncActor):
    async def progress(self, value, percentage):
        await self._progress(value, percentage)

    class Config:
        arbitrary_types_allowed = True


class FunctionalGenActor(FunctionalActor, AsyncGenActor):
    async def progress(self, value, percentage):
        await self._progress(value, percentage)

    class Config:
        arbitrary_types_allowed = True


class ThreadedFuncActor(SerializingActor):
    executor: ThreadPoolExecutor = Field(default_factory=lambda: ThreadPoolExecutor(1))

    async def on_assign(
        self,
        assignment: Assignment,
        collector: Collector,
        transport: AssignTransport,
    ):
        try:
            logger.info("Assigning Number two")
            params = await expand_inputs(
                self.definition,
                assignment.args,
                structure_registry=self.structure_registry,
                skip_expanding=not self.expand_inputs,
            )

            await transport.change(
                status=AssignationStatus.ASSIGNED,
            )

            async with AssignationContext(
                assignment=assignment, transport=transport, passport=self.passport
            ):
                returns = await run_spawned(
                    self.assign, **params, executor=self.executor, pass_context=True
                )

            returns = await shrink_outputs(
                self.definition,
                returns,
                structure_registry=self.structure_registry,
                skip_shrinking=not self.shrink_outputs,
            )

            collector.register(assignment, parse_collectable(self.definition, returns))

            await transport.change(
                status=AssignationStatus.RETURNED,
                returns=returns,
            )

        except SerializationError as ex:
            logger.error("Serializing Error in actor", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except AssertionError as ex:
            logger.error("AssertionError in actor", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except Exception as e:
            logger.error("Error in actor", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(e),
            )


class ThreadedGenActor(SerializingActor):
    executor: ThreadPoolExecutor = Field(default_factory=lambda: ThreadPoolExecutor(4))

    async def on_assign(
        self,
        assignment: Assignation,
        collector: Collector,
        transport: AssignTransport,
    ):
        try:
            params = await expand_inputs(
                self.definition,
                assignment.args,
                structure_registry=self.structure_registry,
                skip_expanding=not self.expand_inputs,
            )
            await transport.change(
                status=AssignationStatus.ASSIGNED,
            )

            async with AssignationContext(
                assignment=assignment, transport=transport, passport=self.passport
            ):
                async for returns in iterate_spawned(
                    self.assign, **params, executor=self.executor, pass_context=True
                ):
                    returns = await shrink_outputs(
                        self.definition,
                        returns,
                        structure_registry=self.structure_registry,
                        skip_shrinking=not self.shrink_outputs,
                    )

                    collector.register(
                        assignment, parse_collectable(self.definition, returns)
                    )

                    await transport.change(
                        status=AssignationStatus.YIELD,
                        returns=returns,
                    )

            await transport.change(status=AssignationStatus.DONE)

        except AssertionError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except SerializationError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except Exception as e:
            logging.critical(f"Assignation Error {assignment} {e}", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(e),
            )

            raise e


class ProcessedGenActor(SerializingActor):
    async def on_assign(
        self,
        assignment: Assignation,
        collector: Collector,
        transport: AssignTransport,
    ):
        try:
            params = await expand_inputs(
                self.definition,
                assignment.args,
                structure_registry=self.structure_registry,
                skip_expanding=not self.expand_inputs,
            )
            await transport.change(
                status=AssignationStatus.ASSIGNED,
            )

            async with AssignationContext(
                assignment=assignment, transport=transport, passport=self.passport
            ):
                async for returns in iterate_processed(self.assign, **params):
                    returns = await shrink_outputs(
                        self.definition,
                        returns,
                        structure_registry=self.structure_registry,
                        skip_shrinking=not self.shrink_outputs,
                    )

                    collector.register(
                        assignment, parse_collectable(self.definition, returns)
                    )

                    await self.transport.change(
                        status=AssignationStatus.YIELD,
                        returns=returns,
                    )

            await transport.change(status=AssignationStatus.DONE)

        except AssertionError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except SerializationError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except Exception as e:
            logging.critical(f"Assignation Error {assignment} {e}", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(e),
            )

            raise e


class ProcessedFuncActor(SerializingActor):
    async def on_assign(
        self,
        assignment: Assignment,
        collector: Collector,
        transport: AssignTransport,
    ):
        try:
            logger.info("Assigning Number two")
            params = await expand_inputs(
                self.definition,
                assignment.args,
                structure_registry=self.structure_registry,
                skip_expanding=not self.expand_inputs,
            )

            await transport.change(
                status=AssignationStatus.ASSIGNED,
            )

            async with AssignationContext(
                assignment=assignment, transport=transport, passport=self.passport
            ):
                returns = await run_processed(
                    self.assign,
                    **params,
                )

            returns = await shrink_outputs(
                self.definition,
                returns,
                structure_registry=self.structure_registry,
                skip_shrinking=not self.shrink_outputs,
            )

            collector.register(assignment, parse_collectable(self.definition, returns))

            await transport.change(
                status=AssignationStatus.RETURNED,
                returns=returns,
            )

        except SerializationError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except AssertionError as ex:
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(ex),
            )

        except Exception as e:
            logger.error("Error in actor", exc_info=True)
            await transport.change(
                status=AssignationStatus.CRITICAL,
                message=str(e),
            )


class FunctionalThreadedFuncActor(FunctionalActor, ThreadedFuncActor):
    async def progress(self, value, percentage):
        await self._progress(value, percentage)

    class Config:
        arbitrary_types_allowed = True


class FunctionalThreadedGenActor(FunctionalActor, ThreadedGenActor):
    async def progress(self, value, percentage):
        await self._progress(value, percentage)

    class Config:
        arbitrary_types_allowed = True


class FunctionalProcessedFuncActor(FunctionalActor, ProcessedFuncActor):
    async def progress(self, value, percentage):
        await self._progress(value, percentage)

    class Config:
        arbitrary_types_allowed = True


class FunctionalProcessedGenActor(FunctionalActor, ProcessedGenActor):
    async def progress(self, value, percentage):
        await self._progress(value, percentage)

    class Config:
        arbitrary_types_allowed = True
