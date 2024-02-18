from .models_query import FilterBinary, FilterBetween, FilterList, FilterGroup, FilterImpossible


class FilterVisitor:
    def visit_binary(self, f: FilterBinary) -> any:
        pass

    def visit_between(self, f: FilterBetween) -> any:
        pass

    def visit_list(self, f: FilterList) -> any:
        pass

    def visit_group(self, f: FilterGroup) -> any:
        pass

    def visit_impossible(self, f: FilterImpossible) -> any:
        pass
