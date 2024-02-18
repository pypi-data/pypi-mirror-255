from enum import Flag, Enum


class FilterOperator(Flag):
    no = 0
    equals = 1
    not_equals = 2
    greater_than = 4
    greater_than_or_equals = 8
    less_than = 16
    less_than_or_equals = 32
    value_in = 64
    value_not_in = 128
    like = 256
    not_like = 512
    between = 1024
    not_between = 2048
    group_and = 4096
    group_or = 8192
    binary_filter = (equals
                     | not_equals
                     | greater_than
                     | greater_than_or_equals
                     | less_than
                     | less_than_or_equals
                     | like
                     | not_like)
    between_filter = between | not_between
    list_filter = value_in | value_not_in
    group_filter = group_and | group_or


class FilterBinaryOperator(int, Enum):
    equals = 0,
    not_equals = 1
    like = 2
    not_like = 3
    greater_than = 4
    greater_than_or_equals = 5
    less_than = 6
    less_than_or_equals = 7


class FilterBetweenOperator(int, Enum):
    between = 0
    not_between = 1


class FilterListOperator(int, Enum):
    value_in = 0
    value_not_in = 1


class FilterGroupOperator(int, Enum):
    group_and = 0
    group_or = 1


class DataType(str, Enum):
    string = "string"
    int = "int"
    decimal = "decimal"
    datetime = "datetime"
    bytes = "bytes"


class PropertyAggregateType(int, Enum):
    no = 0
    sum = 1
    max = 2
    min = 3
    avg = 4
    count = 5
    stdev = 6
