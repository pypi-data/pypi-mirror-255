from attune_project_api import ObjectStorageContext
from attune_project_api import ParameterTuple
from attune_project_api.items import NotZeroLenStr
from attune_project_api.items.step_tuples import addStepDeclarative
from attune_project_api.items.step_tuples import extractTextPlaceholders
from attune_project_api.items.step_tuples.step_ssh_tuple import StepSshTuple
from attune_project_api.items.step_tuples.step_tuple import (
    StepFieldNeedingSubstitution,
)
from attune_project_api.items.step_tuples.step_tuple import StepTupleTypeEnum
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Linux Script With Responses")
@addTupleType
class StepSshPromptedTuple(StepSshTuple):
    __tupleType__ = StepTupleTypeEnum.SSH_PROMPTED.value

    promptResponses: NotZeroLenStr = TupleField()

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        return extractTextPlaceholders(self.script + self.promptResponses)

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        results = StepSshTuple.fieldsNeedingSubstitutions(self)
        results.append(
            StepFieldNeedingSubstitution(
                fieldName="promptResponses",
                displayName="Prompt Responses",
                value=self.promptResponses,
                isScriptOrCode=False,
                order=len(results),
            )
        )
        return results
