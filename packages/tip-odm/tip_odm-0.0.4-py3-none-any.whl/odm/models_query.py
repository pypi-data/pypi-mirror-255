from csv import excel
from pydantic import BaseModel, Field
from datetime import datetime
from typing import ForwardRef
from .enums import (
    PropertyAggregateType,
    FilterBinaryOperator,
    FilterBetweenOperator,
    FilterGroupOperator,
    FilterListOperator)
from .models_definition import Definition, DefinitionProperty

type RawValues = datetime | str | int | float | bool

# ForwardRef um zirkuläre Abhängigkeiten zu verhindern
FilterImpossibleT = ForwardRef("FilterImpossible")
FilterBinaryT = ForwardRef("FilterBinary")
FilterBetweenT = ForwardRef("FilterBetween")
FilterListT = ForwardRef("FilterList")
FilterGroupT = ForwardRef("FilterGroup")

type Filters = FilterBinaryT | FilterBetweenT | FilterListT | FilterGroupT | FilterImpossibleT

type Visitor = ForwardRef("odm_filter_visitor.Visitor")


class FilterBase(BaseModel):
    def visit(self, visitor: Visitor) -> any:
        pass


class FilterImpossible(FilterBase):
    impossible: bool

    def visit(self, visitor: Visitor) -> any:
        return visitor.visit_impossible(self)


class FilterBinary(FilterBase):
    key: str
    operator: FilterBinaryOperator
    value: RawValues

    def visit(self, visitor: Visitor) -> any:
        return visitor.visit_binary(self)


class FilterBetween(FilterBase):
    key: str
    operator: FilterBetweenOperator
    value1: RawValues
    value2: RawValues

    def visit(self, visitor: Visitor) -> any:
        return visitor.visit_between(self)


class FilterList(FilterBase):
    key: str
    operator: FilterListOperator
    values: list[RawValues]

    def visit(self, visitor: Visitor) -> any:
        return visitor.visit_list(self)


class FilterGroup(FilterBase):
    operator: FilterGroupOperator
    filters: list[Filters]

    def visit(self, visitor: Visitor) -> any:
        return visitor.visit_group(self)


class LoadProperty(BaseModel):
    key: str
    field_name: str = Field(serialization_alias="fieldName", validation_alias="fieldName")
    alias: str | None = Field(None, exclude=True)

    aggregate_type: PropertyAggregateType = Field(
        PropertyAggregateType.no,
        serialization_alias="aggregateType",
        validation_alias="aggregateType")


class LoadOptions(BaseModel):
    definition: Definition | None = Field(default=None, exclude=True)
    identity_key: str = Field(serialization_alias="identityKey", validation_alias="identityKey")

    key: str

    properties: list[LoadProperty]
    filter_blocks: list[str] = Field(serialization_alias="filterBlocks", validation_alias="filterBlocks")
    variables: list[Filters]

    filter: Filters | None
    relation_filter: Filters | None = Field(
        None,
        serialization_alias="relationFilter",
        validation_alias="relationFilter")
    max_rows: int | None = Field(None, serialization_alias="maxRows", validation_alias="maxRows")

    def get_definition_property(self, key: str) -> DefinitionProperty:
        return next(filter(lambda x: x.key == key, self.definition.properties), None)

    def get_variable_value(self, alias: str) -> FilterBase | None:
        v = next(filter(lambda x: x.alias == alias, self.definition.variables), None)
        if not v:
            return None

        return next(filter(lambda x: x.key == v.key, self.variables), None)

    def has_filter_block_by_alias(self, alias: str) -> bool:
        f = next(filter(lambda x: x.alias == alias, self.definition.filter_blocks), None)

        if f is None:
            return False

        return f.key in self.filter_blocks
