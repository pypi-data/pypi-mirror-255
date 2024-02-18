#  Copyright (c) 2023 Roboto Technologies, Inc.
import decimal
import typing

from roboto.types import UserMetadata


def field_serializer_user_metadata(value: dict[str, typing.Any]) -> UserMetadata:
    for k, v in value.items():
        if type(v) in [bool, int, float, str]:
            continue
        elif type(v) is decimal.Decimal:
            value[k] = float(v)
        else:
            raise ValueError(
                f"Illegal metadata element with key '{k}',  type {type(v)}"
            )

    return value
