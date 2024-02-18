from datetime import datetime
from .models_definition import DefinitionProperty, DefinitionVariable
from .models_query import FilterBinary, FilterBetween, FilterList, FilterGroup, FilterImpossible, LoadOptions


class FilterDatatypeVisitor:
    def __init__(self, options: LoadOptions):
        super().__init__()
        self.options = options

    def visit_binary(self, f: FilterBinary) -> any:
        if self.__is_datetime(f.key):
            f.value = self.__get_datetime(f.value)

    def visit_between(self, f: FilterBetween) -> any:
        if self.__is_datetime(f.key):
            f.value1 = self.__get_datetime(f.value1)
            f.value2 = self.__get_datetime(f.value2)

    def visit_list(self, f: FilterList) -> any:
        if self.__is_datetime(f.key):
            f.values = list(map(lambda x: self.__get_datetime(x), f.values))

    def visit_group(self, f: FilterGroup) -> any:
        for f in f.filters:
            f.visit(self)

    def visit_impossible(self, f: FilterImpossible) -> any:
        pass

    def __is_datetime(self, key: str) -> bool:
        p: DefinitionProperty | None = next(filter(lambda x: x.key == key, self.options.definition.properties), None)
        if p:
            if p.type == "datetime":
                return True
            return False

        v: DefinitionVariable | None = next(filter(lambda x: x.key == key, self.options.definition.variables), None)
        if v:
            if v.type == "datetime":
                return True
            return False

        return False

    def __get_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value).replace(tzinfo=None)
