import collections.abc
import enum
import typing

import pydantic
from pydantic import ConfigDict


class ExecutorContainer(enum.Enum):
    LogRouter = "firelens_log_router"
    Monitor = "monitor"
    Setup = "setup"
    Action = "action"
    OutputHandler = "output_handler"


class ComputeRequirements(pydantic.BaseModel):
    """
    Compute requirements for an action invocation.

    .. _Relevant AWS Fargate documentation:
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html#fargate-tasks-size
    """

    vCPU: int = 512  # 256, 512, 1024, 2048, 4096, 8192, 16384
    memory: int = 1024  # 512, 1024, 2024, ... (120 * 1024) in MiB
    gpu: typing.Literal[False] = False  # Not yet supported
    storage: int = pydantic.Field(default=21, ge=21, le=200)  # in GiB (min 21, max 200)

    @pydantic.model_validator(mode="after")
    def validate_vcpu_mem_combination(self):
        allowed_vpcu = (256, 512, 1024, 2048, 4096, 8192, 16384)
        if self.vCPU not in allowed_vpcu:
            raise ValueError(f"Unsupported vCPU value. Allowed options: {allowed_vpcu}")

        memory = self.memory
        allowed_memory: collections.abc.Sequence = list()
        if self.vCPU == 256:
            allowed_memory = [512, 1024, 2048]
        elif self.vCPU == 512:
            allowed_memory = range(1024, 5 * 1024, 1024)
        elif self.vCPU == 1024:
            allowed_memory = range(2 * 1024, 9 * 1024, 1024)
        elif self.vCPU == 2048:
            allowed_memory = range(4 * 1024, 17 * 1024, 1024)
        elif self.vCPU == 4096:
            allowed_memory = range(8 * 1024, 31 * 1024, 1024)
        elif self.vCPU == 8192:
            allowed_memory = range(16 * 1024, 61 * 1024, 4 * 1024)
        elif self.vCPU == 16384:
            allowed_memory = range(32 * 1024, 121 * 1024, 8 * 1024)
        else:
            raise ValueError(f"Unknown vCPU value {self.vCPU}")

        if memory not in allowed_memory:
            raise ValueError(
                f"Unsupported memory/vCPU combination, allowed memory for {self.vCPU} vCPU: {list(allowed_memory)}"
            )

        return self

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, ComputeRequirements):
            return NotImplemented

        return (
            self.vCPU == other.vCPU
            and self.memory == other.memory
            and self.gpu == other.gpu
            and self.storage == other.storage
        )

    model_config = ConfigDict(extra="forbid")


class ContainerParameters(pydantic.BaseModel):
    command: typing.Optional[list[str]] = None
    entry_point: typing.Optional[list[str]] = None
    env_vars: typing.Optional[dict[str, str]] = None
    workdir: typing.Optional[str] = None

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, ContainerParameters):
            return NotImplemented

        return (
            self.command == other.command
            and self.entry_point == other.entry_point
            and self.env_vars == other.env_vars
            and self.workdir == other.workdir
        )

    model_config = ConfigDict(extra="forbid")
