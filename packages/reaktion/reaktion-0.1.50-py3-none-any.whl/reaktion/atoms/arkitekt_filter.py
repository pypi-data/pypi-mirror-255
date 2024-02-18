import asyncio

from typing import Any, List, Optional
from rekuest.postmans.utils import RPCContract
from reaktion.atoms.helpers import node_to_reference

from fluss.api.schema import ArkitektNodeFragment, ArkitektFilterNodeFragment

from reaktion.atoms.generic import (
    MapAtom,
    MergeMapAtom,
    AsCompletedAtom,
    OrderedAtom,
    FilterAtom,
)
from reaktion.events import InEvent
import logging

logger = logging.getLogger(__name__)


class ArkitektFilterAtom(FilterAtom):
    node: ArkitektFilterNodeFragment
    contract: RPCContract

    async def filter(self, event: InEvent) -> Optional[bool]:
        kwargs = self.set_values

        stream_one = self.node.instream[0]
        for arg, item in zip(event.value, stream_one):
            kwargs[item.key] = arg

        returns = await self.contract.aassign_retry(
            kwargs=kwargs,
            parent=self.assignment,
            reference=node_to_reference(self.node, event),
        )
        return all([r for r in returns.values()])
