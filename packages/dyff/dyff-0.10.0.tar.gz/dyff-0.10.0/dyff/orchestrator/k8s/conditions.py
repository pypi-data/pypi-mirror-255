# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0
from typing import NamedTuple, Optional, cast

from ...api import timestamp

Condition = dict[str, Optional[str]]


class _ConditionStatus(NamedTuple):
    true: str = "True"
    false: str = "False"
    unknown: str = "Unknown"


ConditionStatus = _ConditionStatus()


def set(
    conditions: list[Condition],
    type_: str,
    *,
    status: str,
    reason: Optional[str] = None,
    message: Optional[str] = None,
):
    if status not in [
        ConditionStatus.true,
        ConditionStatus.false,
        ConditionStatus.unknown,
    ]:
        raise ValueError(f"status={status}")
    new_condition = {
        "type": type_,
        "status": status,
        "reason": reason,
        "message": message,
    }
    for condition in conditions:
        if condition["type"] == type_:
            new_condition["lastTransitionTime"] = timestamp.now_str()
            condition.update(new_condition)
            break
    else:
        new_condition["lastTransitionTime"] = timestamp.now_str()
        # mypy can't figure out that Optional[str] satisfies Union[str, None, ...]
        conditions.append(new_condition)


def get(conditions: list[Condition], type_: str) -> Optional[Condition]:
    for condition in conditions:
        if condition["type"] == type_:
            return condition
    else:
        return None


def get_status(conditions: list[Condition], type_: str) -> str:
    condition = get(conditions, type_)
    if condition is not None:
        return cast(str, condition["status"])
    else:
        return ConditionStatus.unknown


class ConditionsList:
    def __init__(self, conditions_list: Optional[list[Condition]] = None):
        self.conditions_list = conditions_list or []

    def set(
        self,
        type_: str,
        *,
        status: str,
        reason: Optional[str] = None,
        message: Optional[str] = None,
    ):
        return set(
            self.conditions_list, type_, status=status, reason=reason, message=message
        )

    def get(self, type_: str):
        return get(self.conditions_list, type_)

    def get_status(self, type_: str):
        return get_status(self.conditions_list, type_)
