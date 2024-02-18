#  Copyright (c) 2023 Roboto Technologies, Inc.

from typing import Optional

from .conditions import (
    Comparator,
    Condition,
    ConditionGroup,
    ConditionOperator,
    ConditionType,
)


def __pathspec_to_like_value(pattern: str) -> str:
    return pattern.replace("**/*", "%").replace("**", "%").replace("*", "%")


def git_paths_to_condition_group(
    include_patterns: Optional[list[str]],
    exclude_patterns: Optional[list[str]],
    path_field_name: str,
) -> ConditionGroup:
    conditions: list[ConditionType] = []

    if include_patterns:
        include_pattern_conditions = list(
            map(
                lambda pattern: Condition(
                    field=path_field_name,
                    comparator=Comparator.Like,
                    value=__pathspec_to_like_value(pattern),
                ),
                include_patterns,
            )
        )

        conditions.append(
            ConditionGroup(
                conditions=include_pattern_conditions, operator=ConditionOperator.Or
            )
        )

    if exclude_patterns:
        exclude_pattern_conditions = list(
            map(
                lambda pattern: Condition(
                    field=path_field_name,
                    comparator=Comparator.NotLike,
                    value=__pathspec_to_like_value(pattern),
                ),
                exclude_patterns,
            )
        )

        conditions.append(
            ConditionGroup(
                conditions=exclude_pattern_conditions, operator=ConditionOperator.And
            )
        )

    return ConditionGroup(conditions=conditions, operator=ConditionOperator.And)
