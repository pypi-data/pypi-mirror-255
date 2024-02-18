#  Copyright (c) 2023 Roboto Technologies, Inc.
import enum
import typing
from typing import Any, Optional, Union

import pydantic
from pydantic import ConfigDict
from pydantic_core.core_schema import (
    ValidationInfo,
)

from roboto.sentinels import NotSet, NotSetType

from ...pydantic import (
    validate_nonzero_gitpath_specs,
)
from ...query import ConditionType
from ..actions import (
    ComputeRequirements,
    ContainerParameters,
)
from .trigger_record import (
    TriggerForEachPrimitive,
)


class CreateTriggerRequest(pydantic.BaseModel):
    # Required
    name: str = pydantic.Field(pattern=r"[\w\-]+", max_length=256)
    action_name: str
    action_owner_id: Optional[str] = None
    action_digest: Optional[str] = None
    required_inputs: list[str]
    for_each: TriggerForEachPrimitive
    service_user_id: Optional[str] = None
    compute_requirement_overrides: Optional[ComputeRequirements] = None
    container_parameter_overrides: Optional[ContainerParameters] = None
    condition: Optional[ConditionType] = None
    additional_inputs: Optional[list[str]] = None
    parameter_values: Optional[dict[str, Any]] = None
    timeout: Optional[int] = None

    @pydantic.field_validator("required_inputs")
    def validate_required_inputs(cls, value: list[str]) -> list[str]:
        return validate_nonzero_gitpath_specs(value)

    @pydantic.field_validator("additional_inputs")
    def validate_additional_inputs(
        cls, value: Optional[list[str]]
    ) -> Optional[list[str]]:
        return None if value is None else validate_nonzero_gitpath_specs(value)


class QueryTriggersRequest(pydantic.BaseModel):
    filters: dict[str, Any] = pydantic.Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class UpdateTriggerRequest(pydantic.BaseModel):
    action_name: Union[str, NotSetType] = NotSet
    action_owner_id: Union[str, NotSetType] = NotSet
    action_digest: Optional[Union[str, NotSetType]] = NotSet
    required_inputs: Union[list[str], NotSetType] = NotSet
    for_each: Union[TriggerForEachPrimitive, NotSetType] = NotSet
    enabled: Union[bool, NotSetType] = NotSet
    additional_inputs: Optional[Union[list[str], NotSetType]] = NotSet
    compute_requirement_overrides: Optional[
        Union[ComputeRequirements, NotSetType]
    ] = NotSet
    container_parameter_overrides: Optional[
        Union[ContainerParameters, NotSetType]
    ] = NotSet
    condition: Optional[Union[ConditionType, NotSetType]] = NotSet
    parameter_values: Optional[Union[dict[str, Any], NotSetType]] = NotSet
    model_config = ConfigDict(
        extra="forbid", json_schema_extra=NotSetType.openapi_schema_modifier
    )
    timeout: Optional[Union[int, NotSetType]] = NotSet


class EvaluateTriggerPrincipalType(str, enum.Enum):
    Dataset = "dataset"
    File = "file"


class EvaluateTriggerScope(str, enum.Enum):
    Dataset = "dataset"
    DatasetFiles = "dataset_files"
    File = "file"


class EvaluateTriggersRequest(pydantic.BaseModel):
    principal_id: str
    principal_type: EvaluateTriggerPrincipalType
    evaluation_scope: EvaluateTriggerScope

    @staticmethod
    def is_valid_combination(
        principal_type: EvaluateTriggerPrincipalType,
        evaluation_scope: EvaluateTriggerScope,
    ) -> bool:
        return (principal_type, evaluation_scope) in [
            (EvaluateTriggerPrincipalType.File, EvaluateTriggerScope.File),
            (EvaluateTriggerPrincipalType.Dataset, EvaluateTriggerScope.Dataset),
            (EvaluateTriggerPrincipalType.Dataset, EvaluateTriggerScope.DatasetFiles),
        ]

    @pydantic.field_validator("evaluation_scope")
    def validate_evaluation_scope(
        cls, evaluation_scope: EvaluateTriggerScope, info: ValidationInfo
    ) -> EvaluateTriggerScope:
        principal_type = typing.cast(
            EvaluateTriggerPrincipalType, info.data.get("principal_type")
        )
        if not cls.is_valid_combination(principal_type, evaluation_scope):
            raise ValueError(
                f"'{principal_type}', '{evaluation_scope}' is not a valid tuple of "
                + "principal_type, evaluation_scope"
            )

        return evaluation_scope
