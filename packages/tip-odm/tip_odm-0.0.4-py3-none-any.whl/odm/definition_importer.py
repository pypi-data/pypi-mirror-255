import importlib
import os
import polars as pl
import pathlib
import yaml
from .query import add_query
from .query_utils import filter_aggregate_convert
from .enums import DataType
from .models_definition import Definition, DefinitionProperty
from .models_query import LoadOptions
from .caching import data_cache, get_cached_data


def auto_import_path(path: str):
    __auto_import_py(path)
    __auto_import_yaml(path)


def __auto_import_py(path: str):
    p = pathlib.Path.cwd() / path
    files = p.glob("*.py")

    for file in files:
        r = str(file.relative_to(pathlib.Path.cwd())).replace("/", ".").replace("\\", ".")[:-3]
        module = importlib.import_module(str(r))

        if "add" in module.__dict__ and callable(module.__dict__["add"]):
            module.add()


def __auto_import_yaml(path: str):
    p = pathlib.Path.cwd() / path
    files = list(p.glob("*.yml")) + list(p.glob("*.yaml"))

    for file in files:
        add_yaml(str(file.relative_to(pathlib.Path.cwd())))


def add_yaml(file: str):
    file = pathlib.Path.cwd() / file

    with open(file, "r", encoding="utf-8") as f:
        dict_def: dict[str, any] = yaml.safe_load(f)

    dict_properties: dict[str, any] = dict_def["properties"]
    dict_cache: dict[str, any] | None = dict_def.get("cache", None)

    conn: str | None = dict_def["conn"]
    sql: str | None = dict_def["sql"]

    properties: list[DefinitionProperty] = []
    for key, value in dict_properties.items():
        t = value.get("type", "string")

        properties.append(DefinitionProperty(
            alias=key,
            name=value.get("name", key),
            type=__convert_str_to_data_type(t),
            description=value.get("description", None),
            format_string=value.get("formatString", None),
            regex=value.get("regex", None),
            can_aggregate=value.get("canAggregate", False)
        ))

    d = Definition(
        key=dict_def["key"],
        name=dict_def["name"],
        description=dict_def.get("description", None),

        properties=properties
    )

    uri = os.getenv(conn)
    cache_key: str | None = dict_cache.get("key", None) if dict_cache is not None else None

    def get_data():
        return pl.read_database(sql, uri)

    def f(options: LoadOptions):
        df = get_data() if cache_key is None else get_cached_data(cache_key)
        return filter_aggregate_convert(options, df)

    if cache_key is not None:
        cache_name: str | None = dict_cache.get("name", cache_key)
        cache_timer = dict_cache.get("refreshTime", ["02:00"])
        cache_recreate = dict_cache.get("recreate", True)
        cache_lazy = dict_cache.get("lazy", True)

        if isinstance(cache_timer, str):
            cache_timer = [cache_timer]

        # Cache für die Definition aktivieren
        data_cache(cache_key, cache_name, cache_timer, cache_recreate, cache_lazy)(get_data)

    add_query(d, f)


def __convert_str_to_data_type(string: str) -> DataType:
    match string:
        case "string":
            return DataType.string
        case "int":
            return DataType.int
        case "decimal":
            return DataType.decimal
        case "datetime":
            return DataType.datetime
        case "bytes":
            return DataType.bytes
