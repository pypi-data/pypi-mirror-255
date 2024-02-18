from typing import Callable
from .filter_datatype_visitor import FilterDatatypeVisitor
from .models_definition import Definition, DefinitionCompact
from .models_query import LoadOptions
from .logger import log_error, log_exception
from .utils import create_uuid_from_string, timer

type DefinitionCallback = Callable[[], Definition] | Definition
type LoadCallback = Callable[[LoadOptions], any]

queries: list[tuple[DefinitionCallback, LoadCallback]] = []


def add_query(d: DefinitionCallback, f: LoadCallback):
    """
    Fügt ein Query in das Query-Repository ein
    :param d: Definition oder Funktion, die eine Definition zurückgibt (falls diese dynamisch ist)
    :param f: Funktion die aufgerufen wird, wenn die Daten ermittelt werden
    :return: None
    """

    if d is None:
        msg = "add_query: Definition darf nicht None sein"
        log_error(msg)
        raise Exception(msg)
    if f is None:
        msg = "add_query: Funktion darf nicht None sein"
        log_error(msg)
        raise Exception(msg)

    if isinstance(d, Definition):
        d = __validate_definition(d)

    queries.append((d, f))


def get_queries():
    """
    Gibt alle Queries (in kompakter Form) zurück
    :return: DefinitionCompact[]
    """

    d = map(lambda q: __get_definition(q[0]), queries)

    return map(lambda d: DefinitionCompact(
        key=d.key,
        name=d.name,
        description=d.description
    ), d)


def get_query(key):
    """
    Gibt eine Query zurück
    :param key: Key der Definition
    :return: Definition | None
    """

    d = next(filter(lambda d: d.key == key, map(lambda q: q[0], queries)), None)
    if d is None:
        log_error(f"get_query: Definition mit Key {key} nicht gefunden")
        return None

    d = __get_definition(d)
    return d


def get_query_result(options: LoadOptions) -> str:
    """
    Ermittelt die Daten für eine Query
    :param options: LoadOptions
    :return: JSON-String mit den Ergebnissen
    """

    q = next(filter(lambda x: x[0].key == options.key, queries))
    if not q:
        log_error(f"[{options.identity_key}]  get_query_result: Query mit Key {options.key} nicht gefunden")
        return "[]"

    options.definition = __get_definition(q[0])
    __validate_load_options(options)

    try:
        text = f"[{options.identity_key}]  Query {options.definition.name}"
        return timer(text, lambda: q[1](options))
    except Exception:
        log_exception(f"[{options.identity_key}]  Fehler bei Query {options.definition.name}")
        return "[]"


def __get_definition(d: DefinitionCallback) -> Definition:
    if isinstance(d, Definition):
        return d
    else:
        return __validate_definition(d())


def __validate_definition(d: Definition):
    for p in d.properties:
        if p.key is None:
            p.key = create_uuid_from_string(f"{d.key}_{p.alias}")

    if d.variables:
        for v in d.variables:
            if v.key is None:
                v.key = create_uuid_from_string(f"{d.key}_var_{v.alias}")

    if d.filter_blocks:
        for fb in d.filter_blocks:
            if fb.key is None:
                fb.key = create_uuid_from_string(f"{d.key}_fb_{fb.alias}")

    return d


def __validate_load_options(options: LoadOptions):
    d: Definition = options.definition

    alias_dict = {p.key: p.alias for p in d.properties}

    for p in options.properties:
        p.alias = alias_dict[p.key]

    visitor = FilterDatatypeVisitor(options)

    if options.filter:
        options.filter.visit(visitor)

    if options.relation_filter:
        options.relation_filter.visit(visitor)

    for v in options.variables:
        v.visit(visitor)
