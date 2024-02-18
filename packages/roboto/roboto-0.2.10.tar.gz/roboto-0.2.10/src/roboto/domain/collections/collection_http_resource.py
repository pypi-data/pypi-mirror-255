#  Copyright (c) 2023 Roboto Technologies, Inc.
from typing import Optional, Union

import pydantic
from pydantic import ConfigDict

from roboto.sentinels import NotSet, NotSetType

from .collection_record import (
    CollectionResourceRef,
)


class CreateCollectionRequest(pydantic.BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resources: Optional[list[CollectionResourceRef]] = None
    tags: Optional[list[str]] = None


class UpdateCollectionRequest(pydantic.BaseModel):
    name: Optional[Union[NotSetType, str]] = NotSet
    description: Optional[Union[NotSetType, str]] = NotSet
    add_resources: Union[list[CollectionResourceRef], NotSetType] = NotSet
    remove_resources: Union[list[CollectionResourceRef], NotSetType] = NotSet
    add_tags: Union[list[str], NotSetType] = NotSet
    remove_tags: Union[list[str], NotSetType] = NotSet
    model_config = ConfigDict(json_schema_extra=NotSetType.openapi_schema_modifier)
