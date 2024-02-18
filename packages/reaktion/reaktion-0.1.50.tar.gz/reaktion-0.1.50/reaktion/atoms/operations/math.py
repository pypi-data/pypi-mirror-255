import asyncio
from typing import List
from reaktion.atoms.operations.base import OperationAtom
from reaktion.events import EventType, OutEvent
from fluss.api.schema import ReactiveImplementationModelInput
import logging
import operator


logger = logging.getLogger(__name__)


operation_map = {
    ReactiveImplementationModelInput.ADD: operator.add,
    ReactiveImplementationModelInput.SUBTRACT: operator.sub,
    ReactiveImplementationModelInput.MULTIPLY: operator.mul,
    ReactiveImplementationModelInput.DIVIDE: operator.truediv,
    ReactiveImplementationModelInput.MODULO: operator.mod,
    ReactiveImplementationModelInput.POWER: operator.pow,
}


class MathAtom(OperationAtom):
    complete: List[bool] = [False, False]

    async def run(self):
        operation = operation_map.get(self.node.implementation)
        number = self.set_values.get("number", 1)

        try:
            while True:
                event = await self.get()

                if event.type == EventType.ERROR:
                    await self.transport.put(
                        OutEvent(
                            handle="return_0",
                            type=EventType.ERROR,
                            value=event.value,
                            source=self.node.id,
                            caused_by=[event.current_t],
                        )
                    )
                    break

                if event.type == EventType.NEXT:
                    await self.transport.put(
                        OutEvent(
                            handle="return_0",
                            type=EventType.NEXT,
                            value=[operation(value, number) for value in event.value],
                            source=self.node.id,
                            caused_by=[event.current_t],
                        )
                    )

                if event.type == EventType.COMPLETE:
                    await self.transport.put(
                        OutEvent(
                            handle="return_0",
                            type=EventType.COMPLETE,
                            value=[],
                            source=self.node.id,
                            caused_by=[event.current_t],
                        )
                    )
                    break

        except asyncio.CancelledError as e:
            logger.warning(f"Atom {self.node} is getting cancelled")
            raise e

        except Exception as e:
            logger.exception(f"Atom {self.node} excepted")
            raise e
