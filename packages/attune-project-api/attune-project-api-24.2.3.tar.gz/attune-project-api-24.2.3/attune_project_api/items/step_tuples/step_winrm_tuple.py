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

from attune_project_api.items import NotZeroLenStr
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from . import addStepDeclarative
from . import extractTextPlaceholders
from .step_tuple import StepFieldNeedingSubstitution
from .step_tuple import StepTupleTypeEnum
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField

STEP_WIN_CMD_INTERPRETERS = {}


class StepWinCmdInterpreter:
    def __init__(self, _id: int, name: str, editorLanguage: str):
        self.id, self.name = _id, name
        self.editorLanguage = editorLanguage
        STEP_WIN_CMD_INTERPRETERS[self.id] = self


# ID=1, hard coded in 8ba86d3c39b_added_support_to_for_shell_interpreters.py
# due to upgrade import issues
winCmdIntBatchScript = StepWinCmdInterpreter(1, "Batch Script", "bat")
winCmdIntPowershellScript = StepWinCmdInterpreter(
    2, "Powershell Script", "powershell"
)
winCmdIntCustom = StepWinCmdInterpreter(3, "Custom", "guess")


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Windows Script")
@addTupleType
class StepWinRmTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.WINRM.value

    script: NotZeroLenStr = TupleField()
    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    interpreter: int = TupleField(defaultValue=winCmdIntPowershellScript.id)
    interpreterCommand: Optional[str] = TupleField()
    interpreterScriptExt: Optional[str] = TupleField()
    interpreterScriptSyntax: Optional[str] = TupleField()
    successExitCode: int = TupleField(defaultValue=0)
    timeout: Optional[int] = TupleField()

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )

    @property
    def interpreterWinCmd(self):
        return STEP_WIN_CMD_INTERPRETERS[self.interpreter]

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        textPh = extractTextPlaceholders(self.script)
        if self.interpreterCommand:
            textPh += extractTextPlaceholders(self.interpreterCommand)
        return textPh

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        return [
            StepFieldNeedingSubstitution(
                fieldName="server",
                displayName="Target WinRM Node",
                value=self.server,
                isScriptOrCode=False,
                order=0,
            ),
            StepFieldNeedingSubstitution(
                fieldName="osCred",
                displayName="WinRM Credential",
                value=self.osCred,
                isScriptOrCode=False,
                order=1,
            ),
            StepFieldNeedingSubstitution(
                fieldName="script",
                displayName="Script",
                value=self.script,
                isScriptOrCode=True,
                order=2,
            ),
        ]
