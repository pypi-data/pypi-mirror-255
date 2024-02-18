"""
Common enums.
"""

from spotlight.core.common.base_enum import BaseEnum


class Order(BaseEnum):
    ASC = "ASC"
    DESC = "DESC"


class ComparisonOperator(BaseEnum):
    NOT_IN = "NOT_IN"
    IN = "IN"
    NOT_EQUAL = "NOT_EQUAL"
    EQUAL = "EQUAL"
    LIKE = "LIKE"
    NOT_LIKE = "NOT_LIKE"
    GTE = "GTE"
    GT = "GT"
    LTE = "LTE"
    LT = "LT"


class LogicalOperator(BaseEnum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class FieldType(BaseEnum):
    BOOLEAN = "BOOLEAN"
    DOUBLE = "DOUBLE"
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    TIMESTAMP = "TIMESTAMP"
    DATETIME = "DATETIME"


class UpdateRequestAction(BaseEnum):
    UPDATE = "UPDATE"
    COPY = "COPY"
