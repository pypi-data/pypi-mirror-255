from typing import Dict, List

import sqlalchemy as sa
from sqlalchemy.sql.elements import BooleanClauseList, ColumnElement
from sqlalchemy.sql.expression import Select

from approck_sqlalchemy_query_builder.types import Condition, Operator, Query, QueryRule


def build_rule_condition(map_columns: Dict[str, sa.Column], rule: QueryRule) -> ColumnElement[sa.Boolean]:
    column = map_columns.get(rule.id)

    if column is None:
        raise ValueError(f"Column for '{rule.id}' is not found")

    if rule.operator == Operator.OP_EQUAL:
        return column == rule.value
    elif rule.operator == Operator.OP_GREATER_THAN:
        return column > rule.value
    elif rule.operator == Operator.OP_LESS_THAN:
        return column < rule.value
    elif rule.operator == Operator.OP_GREATER_THAN_OR_EQUAL:
        return column >= rule.value
    elif rule.operator == Operator.OP_LESS_THAN_OR_EQUAL:
        return column <= rule.value
    elif rule.operator == Operator.OP_NOT_EQUAL:
        return column != rule.value
    elif rule.operator == Operator.OP_IN:
        return column.in_(rule.value)
    elif rule.operator == Operator.OP_NOT_IN:
        return column.not_in(rule.value)

    raise ValueError(f"Operator '{rule.operator}' is not supported")


def build_condition(
    map_columns: Dict[str, sa.Column], query: Query
) -> BooleanClauseList[ColumnElement[sa.Boolean]] | None:
    clauses: List[BooleanClauseList[ColumnElement[sa.Boolean]] | ColumnElement[sa.Boolean]] = []

    for rule in query.rules:
        if isinstance(rule, Query):
            condition = build_condition(map_columns=map_columns, query=rule)

            if condition is not None:
                clauses.append(condition)
        elif isinstance(rule, QueryRule):
            clauses.append(build_rule_condition(map_columns=map_columns, rule=rule))

    if clauses:
        if query.condition == Condition.OR:
            return sa.or_(*clauses)
        elif query.condition == Condition.AND:
            return sa.and_(*clauses)

    return None


def query_filter(statement: Select, map_columns: Dict[str, sa.Column], query: Query) -> Select:
    condition = build_condition(map_columns=map_columns, query=query)

    if condition is not None:
        statement = statement.where(condition)

    return statement
