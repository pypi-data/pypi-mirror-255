import asyncio

from typing import Any, List, Optional
from rekuest.postmans.utils import RPCContract
from reaktion.atoms.helpers import node_to_reference

from fluss.api.schema import ArkitektNodeFragment

from reaktion.atoms.generic import MapAtom, MergeMapAtom, AsCompletedAtom, OrderedAtom
from reaktion.events import InEvent
import logging

logger = logging.getLogger(__name__)


class ArkitektMapAtom(MapAtom):
    node: ArkitektNodeFragment
    contract: RPCContract

    async def map(self, event: InEvent) -> Optional[List[Any]]:
        kwargs = self.set_values

        stream_one = self.node.instream[0]
        for arg, item in zip(event.value, stream_one):
            kwargs[item.key] = arg

        returns = await self.contract.aassign_retry(
            kwargs=kwargs,
            parent=self.assignment,
            reference=node_to_reference(self.node, event),
        )

        out = []
        stream_one = self.node.outstream[0]
        for arg in stream_one:
            out.append(returns[arg.key])

        return out
        # return await self.contract.aassign(*args)


class ArkitektMergeMapAtom(MergeMapAtom):
    node: ArkitektNodeFragment
    contract: RPCContract

    async def merge_map(self, event: InEvent) -> Optional[List[Any]]:
        kwargs = self.set_values

        stream_one = self.node.instream[0]
        for arg, item in zip(event.value, stream_one):
            kwargs[item.key] = arg

        async for r in self.contract.astream_retry(
            kwargs=kwargs,
            parent=self.assignment,
            reference=node_to_reference(self.node, event),
        ):
            out = []
            stream_one = self.node.outstream[0]
            for arg in stream_one:
                out.append(r[arg.key])

            yield out


class ArkitektAsCompletedAtom(AsCompletedAtom):
    node: ArkitektNodeFragment
    contract: RPCContract

    async def map(self, event: InEvent) -> Optional[List[Any]]:
        kwargs = self.set_values

        stream_one = self.node.instream[0]
        for arg, item in zip(event.value, stream_one):
            kwargs[item.key] = arg

        returns = await self.contract.aassign_retry(
            kwargs=kwargs,
            parent=self.assignment,
            reference=node_to_reference(self.node, event),
        )

        out = []
        stream_one = self.node.outstream[0]
        for arg in stream_one:
            out.append(returns[arg.key])

        return out


class ArkitektOrderedAtom(OrderedAtom):
    node: ArkitektNodeFragment
    contract: RPCContract

    async def map(self, event: InEvent) -> Optional[List[Any]]:
        kwargs = self.set_values

        stream_one = self.node.instream[0]
        for arg, item in zip(event.value, stream_one):
            kwargs[item.key] = arg

        returns = await self.contract.aassign_retry(
            kwargs=kwargs,
            parent=self.assignment,
            reference=node_to_reference(self.node, event),
        )

        out = []
        stream_one = self.node.outstream[0]
        for arg in stream_one:
            out.append(returns[arg.key])

        return out
