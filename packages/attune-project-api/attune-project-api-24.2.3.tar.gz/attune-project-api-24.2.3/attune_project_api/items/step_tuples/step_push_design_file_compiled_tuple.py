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
import logging

from attune_project_api import ObjectStorageContext
from attune_project_api.items.file_archive_tuples.file_archive_tuple import (
    FileArchiveTuple,
)
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from . import addStepDeclarative
from . import extractTextPlaceholders
from .step_tuple import StepFieldNeedingSubstitution
from .step_tuple import StepTuple
from .step_tuple import StepTupleTypeEnum
from .. import NotZeroLenStr
from ..parameter_tuple import ParameterTuple
from ...RelationField import RelationField
from ...StorageTuple import StorageMemberTuple

logger = logging.getLogger(__name__)


@addTupleType
class StepPushDesignFileCompiledParamTuple(StorageMemberTuple):
    __tupleType__ = (
        "com.servertribe.attune.tuples.StepPushDesignFileCompiledParamTuple"
    )

    # None means this is target text param
    name: NotZeroLenStr = TupleField()
    parameterType: str = TupleField()
    parameterKey: NotZeroLenStr = TupleField()
    parameter: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="parameterKey",
        cascadeOnUpdate=False,
        cascadeOnDelete=False,
    )


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Push Compiled Files")
@addTupleType
class StepPushDesignFileCompiledTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.PUSH_DESIGN_FILE_COMPILED.value
    __storageTuple__ = __tupleType__

    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    deployPath: NotZeroLenStr = TupleField()
    archiveKey: NotZeroLenStr = TupleField()

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )
    archive: FileArchiveTuple = RelationField(
        ForeignClass=FileArchiveTuple,
        referenceKeyFieldName="archiveKey",
    )

    # A list of file names in the archive that are the root templates.
    # These will be the ones we feed into Mako
    makoFileNames: list[str] = TupleField([])

    makoParameters: list[StepPushDesignFileCompiledParamTuple] = TupleField([])
    storageParameters: list[StepTuple] = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="makoParameters",
        isList=True,
        cascadeOnDelete=True,
        cascadeOnUpdate=True,
        memberReferenceKeyFieldName="parameterKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred] + [
            param.parameter for param in self.makoParameters
        ]

    def scriptReferences(self) -> list[str]:
        return extractTextPlaceholders(self.deployPath)

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        results = [
            StepFieldNeedingSubstitution(
                fieldName="server",
                displayName="Target Node",
                value=self.server,
                isScriptOrCode=False,
                order=0,
            ),
            StepFieldNeedingSubstitution(
                fieldName="osCred",
                displayName="Target Node Credential",
                value=self.osCred,
                isScriptOrCode=False,
                order=1,
            ),
            StepFieldNeedingSubstitution(
                fieldName="deployPath",
                displayName="Remote Deployment Path",
                value=self.deployPath,
                isScriptOrCode=False,
                order=2,
            ),
        ]

        for param in self.makoParameters:
            results.append(
                StepFieldNeedingSubstitution(
                    fieldName="makoParameters[%s]" % param.name,
                    displayName="Mako Parameter: %s" % param.name,
                    value=param.parameter,
                    isScriptOrCode=False,
                    order=10 + len(results),
                )
            )

        return results

    @property
    def hasErrors(self) -> bool:
        return bool(self.invalidParameterKeys)

    @property
    def invalidParameterKeys(self) -> list[str]:  # noinspection PyTypeChecker
        return [
            param.parameterKey
            for param in self.makoParameters
            if not param.parameter
        ]
