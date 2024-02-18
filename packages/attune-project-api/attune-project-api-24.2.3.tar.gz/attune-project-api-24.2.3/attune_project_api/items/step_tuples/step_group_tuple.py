"""
*
 *  Copyright ServerTribe HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  ServerTribe HQ Pty Ltd
 *
"""
from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from . import addStepDeclarative
from .step_tuple import StepFieldNeedingSubstitution
from .step_tuple import StepTuple
from .step_tuple import StepTupleTypeEnum
from .. import NotZeroLenStr
from ... import ParameterTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField
from ...StorageTuple import StorageMemberTuple


@addTupleType
class StepGroupSubStepLinkTuple(StorageMemberTuple):
    __tupleType__ = "com.servertribe.attune.tuples.StepGroupSubStepLinkTuple"

    stepKey: NotZeroLenStr = TupleField()

    step = RelationField(
        ForeignClass=StepTuple,
        referenceKeyFieldName="stepKey",
        cascadeOnUpdate=False,
    )


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Group Step")
@addTupleType
class StepGroupTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.GROUP.value

    concurrency: int = TupleField(defaultValue=1)
    isBlueprint: bool = TupleField(defaultValue=False)
    links: list[StepGroupSubStepLinkTuple] = TupleField(defaultValue=[])
    childSteps: list[StepTuple] = RelationField(
        ForeignClass=StepTuple,
        referenceKeyFieldName="links",
        isList=True,
        cascadeOnDelete=True,
        memberReferenceKeyFieldName="stepKey",
    )

    @classmethod
    def niceName(cls) -> str:
        return "Group StepTuple"

    def stepForLink(
        self, link: StepGroupSubStepLinkTuple
    ) -> Optional[StepTuple]:
        return self.storageContext.getItem(self.storageGroup, link.stepKey)

    def parameters(self) -> list["ParameterTuple"]:
        return []

    def scriptReferences(self) -> list[str]:
        return []

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        return []

    def removeStepLink(self, index: int):
        self.links.pop(index)

    def insertStepLink(self, index: int, stepKey: str):
        link = StepGroupSubStepLinkTuple(stepKey=stepKey)
        self.links.insert(index, link)

    @property
    def hasErrors(self) -> bool:
        return bool(self.invalidChildStepKeys)

    @property
    def invalidChildStepKeys(self) -> list[str]:
        # noinspection PyTypeChecker
        return [link.stepKey for link in self.links if not link.step]
