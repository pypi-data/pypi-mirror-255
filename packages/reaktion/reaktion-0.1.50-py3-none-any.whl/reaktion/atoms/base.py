import asyncio
from typing import Awaitable, Callable, Optional
from pydantic import BaseModel, Field
from rekuest.api.schema import AssignationLogLevel
from rekuest.messages import Assignation
from fluss.api.schema import FlowNodeCommonsFragmentBase
from reaktion.atoms.errors import AtomQueueFull
from reaktion.events import EventType, InEvent, OutEvent
import logging
from rekuest.actors.types import Assignment
from reaktion.atoms.transport import AtomTransport
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Atom(BaseModel):
    node: FlowNodeCommonsFragmentBase
    transport: AtomTransport
    alog: Optional[Callable[[str, AssignationLogLevel, str], Awaitable[None]]] = Field(
        exclude=True
    )
    globals: Dict[str, Any] = Field(default_factory=dict)
    assignment: Assignment

    _private_queue: asyncio.Queue = None

    async def run(self):
        raise NotImplementedError("This needs to be implemented")

    async def get(self) -> InEvent:
        assert self._private_queue is not None, "Atom not started"
        return await self._private_queue.get()

    async def put(self, event: InEvent):
        assert self._private_queue is not None, "Atom not started"
        try:
            logger.info(f"Putting event {event}")
            await self._private_queue.put(event)  # TODO: Make put no wait?
        except asyncio.QueueFull as e:
            logger.error(f"{self.node.id} private queue is full")
            raise AtomQueueFull(f"{self.node.id} private queue is full") from e

    async def aenter(self):
        self._private_queue = asyncio.Queue()

    async def aexit(self):
        self._private_queue = None

    async def __aenter__(self):
        await self.aenter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aexit()

    async def start(self):
        try:
            await self.run()
        except Exception as e:
            logger.error(f"{self.node.id} FAILED", exc_info=True)
            await self.transport.put(
                OutEvent(
                    handle="return_0",
                    type=EventType.ERROR,
                    source=self.node.id,
                    value=e,
                    caused_by=[-1],
                )
            )

    @property
    def set_values(self) -> Dict[str, Any]:
        defaults = getattr(self.node, "defaults", {}) or {}
        my_globals = self.globals or {}
        return {**defaults, **my_globals}

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
