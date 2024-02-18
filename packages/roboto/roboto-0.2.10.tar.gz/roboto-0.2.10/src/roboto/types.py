#  Copyright (c) 2023 Roboto Technologies, Inc.

import typing

# DO NOT EVER TAKE DEPENDENCIES ON ANY OTHER FILE IN ROBOTO

JsonablePrimitive = typing.Union[int, str, float, bool]
UserMetadata = dict[str, JsonablePrimitive]
