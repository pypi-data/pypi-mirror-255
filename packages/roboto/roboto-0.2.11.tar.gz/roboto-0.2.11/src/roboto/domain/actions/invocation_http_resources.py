from typing import Any, Optional

import pydantic

from .action_container_resources import (
    ComputeRequirements,
    ContainerParameters,
)
from .invocation_record import (
    InvocationDataSourceType,
    InvocationSource,
    InvocationStatus,
)


class CreateInvocationRequest(pydantic.BaseModel):
    parameter_values: Optional[dict[str, Any]] = None
    input_data: list[str]
    compute_requirement_overrides: Optional[ComputeRequirements] = None
    container_parameter_overrides: Optional[ContainerParameters] = None
    data_source_id: str
    data_source_type: InvocationDataSourceType
    invocation_source: InvocationSource
    invocation_source_id: Optional[str] = None
    idempotency_id: Optional[str] = None
    timeout: Optional[int] = None


class UpdateInvocationStatus(pydantic.BaseModel):
    status: InvocationStatus
    detail: str
