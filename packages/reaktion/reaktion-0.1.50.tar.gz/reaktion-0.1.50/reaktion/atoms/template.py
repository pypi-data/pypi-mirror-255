from typing import Any, List, Optional
from rekuest.api.schema import AssignationLogLevel
from rekuest.messages import Assignation
from rekuest.postmans.utils import ReservationContract
from fluss.api.schema import ArkitektNodeFragment
from reaktion.atoms.generic import MapAtom
from reaktion.events import Returns


class TemplateMapAtom(MapAtom):
    node: ArkitektNodeFragment
    contract: ReservationContract

    async def map(self, args: Returns) -> Optional[List[Any]]:
        defaults = self.node.defaults or {}
        returns = await self.contract.aassign(
            *args,
            **defaults,
            alog=self.alog_arkitekt,
            parent=self.assignment.assignation
        )
        return returns
        # return await self.contract.aassign(*args)

    async def alog_arkitekt(
        self, assignation: Assignation, level: AssignationLogLevel, message: str
    ):
        if self.alog:
            await self.alog(self.node.id, level, message)
