from pydantic import BaseModel, Field
from typing import Callable, ForwardRef
import polars as pl
from .enums import FilterOperator, DataType

type LoadOptionsInt = ForwardRef("LoadOptions", "odm_models_query")
type LoadPropertyInt = ForwardRef("LoadProperty", "odm_models_query")


class DefinitionProperty(BaseModel):
    alias: str = Field(exlcude=True)
    name: str = Field(serialization_alias="name")

    type: DataType = Field(serialization_alias="type")

    key: str | None = Field(None, serialization_alias="key")
    description: str | None = Field(None, serialization_alias="description")
    format_string: str | None = Field(None, serialization_alias="formatString")
    regex: str | None = Field(None, serialization_alias="regex")

    can_aggregate: bool | None = Field(None, serialization_alias="canAggregate")

    """
    Diese Eigenschaften können nicht direkt gefilter werden, da diese erst im Nachhinein berechnet werden.
    Falls doch ein Filter kommt, werden diese mit True bestätigt. Filterung muss, wenn notwendig  mit Hilfe
    von Variablen erfolgen.
    # TODO Filter (siehe Beschreibung)
    """
    agg_expr: Callable[[LoadOptionsInt, LoadPropertyInt, bool], pl.Expr] | None = Field(None, exclude=True)
    final_expr: Callable[[LoadOptionsInt], pl.Expr] | None = Field(None, exclude=True)


class DefinitionVariable(BaseModel):
    alias: str = Field(exlcude=True)
    name: str = Field(serialization_alias="name")

    type: DataType = Field(serialization_alias="type")

    supported_filter_operators: FilterOperator = Field(serialization_alias="supportedFilterOperators")

    key: str | None = Field(None, serialization_alias="key")
    description: str | None = Field(None, serialization_alias="description")
    format_string: str | None = Field(None, serialization_alias="formatString")
    regex: str | None = Field(None, serialization_alias="regex")

    is_required: bool | None = Field(None, serialization_alias="isRequired")


class DefinitionFilterBlock(BaseModel):
    alias: str = Field(exlcude=True)
    name: str = Field(alias="name")

    key: str | None = Field(None, serialization_alias="key")
    description: str | None = Field(None, serialization_alias="description")


class Definition(BaseModel):
    key: str = Field(serialization_alias="key")
    name: str = Field(serialization_alias="name")
    description: str | None = Field(None, serialization_alias="description")

    properties: list[DefinitionProperty] = Field(serialization_alias="properties")

    variables: list[DefinitionVariable] | None = Field(None, serialization_alias="variables")
    filter_blocks: list[DefinitionFilterBlock] | None = Field(None, serialization_alias="filterBlocks")


class DefinitionCompact(BaseModel):
    key: str = Field(serialization_alias="key")
    name: str = Field(serialization_alias="name")
    description: str | None = Field(None, serialization_alias="description")
