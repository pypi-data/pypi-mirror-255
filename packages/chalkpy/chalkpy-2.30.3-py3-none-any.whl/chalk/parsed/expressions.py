from typing import Literal

Operation = Literal[
    "and", "or", "not", "==", "!=", "<", ">", "<=", ">", ">=", "in", "not in", "is_near_l2", "is_near_ip", "is_near_cos"
]


def is_valid_operation(operation: str) -> bool:
    return operation in (
        "and",
        "or",
        "not",
        "==",
        "!=",
        "in",
        "not in",
        ">=",
        "<=",
        ">",
        "<",
        "is_near_l2",
        "is_near_ip",
        "is_near_cos",
    )
