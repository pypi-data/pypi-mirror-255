#  Copyright (c) 2024 Roboto Technologies, Inc.


import pydantic


class AuthZTupleRecord(pydantic.BaseModel):
    """
    Fully qualified record of (user has relation to obj)
    """

    user: str
    relation: str
    obj: str


class EditAccessRequest(pydantic.BaseModel):
    add: list[AuthZTupleRecord] = pydantic.Field(default_factory=list)
    remove: list[AuthZTupleRecord] = pydantic.Field(default_factory=list)


class GetAccessResponse(pydantic.BaseModel):
    relations: list[AuthZTupleRecord]
    group_permissions: dict[str, list[str]] = pydantic.Field(default_factory=dict)
