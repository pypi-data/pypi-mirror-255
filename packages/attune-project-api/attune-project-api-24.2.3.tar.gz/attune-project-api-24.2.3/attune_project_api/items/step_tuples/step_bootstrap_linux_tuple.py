from attune_project_api import ObjectStorageContext
from attune_project_api import ParameterTuple
from attune_project_api.RelationField import RelationField
from attune_project_api.items import NotZeroLenStr
from attune_project_api.items.step_tuples import addStepDeclarative
from attune_project_api.items.step_tuples.step_tuple import (
    StepFieldNeedingSubstitution,
)
from attune_project_api.items.step_tuples.step_tuple import StepTuple
from attune_project_api.items.step_tuples.step_tuple import StepTupleTypeEnum
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Setup Linux SSH Keys")
@addTupleType
class StepBootstrapLinuxTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.BOOTSTRAP_LINUX.value

    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        return []

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        return [
            StepFieldNeedingSubstitution(
                fieldName="server",
                displayName="Target SSH Node",
                value=self.server,
                isScriptOrCode=False,
                order=0,
            ),
            StepFieldNeedingSubstitution(
                fieldName="osCred",
                displayName="SSH Credential",
                value=self.osCred,
                isScriptOrCode=False,
                order=1,
            ),
        ]
