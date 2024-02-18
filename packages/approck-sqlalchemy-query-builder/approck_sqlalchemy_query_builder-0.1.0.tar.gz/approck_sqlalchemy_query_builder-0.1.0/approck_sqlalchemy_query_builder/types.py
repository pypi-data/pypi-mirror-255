import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class Condition(str, Enum):
    AND = "AND"
    OR = "OR"


class Operator(str, Enum):
    OP_EQUAL = "="
    OP_GREATER_THAN = ">"
    OP_LESS_THAN = "<"
    OP_GREATER_THAN_OR_EQUAL = ">="
    OP_LESS_THAN_OR_EQUAL = "<="
    OP_NOT_EQUAL = "!="
    OP_IN = "in"
    OP_NOT_IN = "="


BaseValue = int | float | str | datetime.datetime | None


class QueryRule(BaseModel):
    id: str
    operator: Operator
    value: BaseValue | List[BaseValue]


class Query(BaseModel):
    condition: Condition
    rules: "List[Query | QueryRule]"
