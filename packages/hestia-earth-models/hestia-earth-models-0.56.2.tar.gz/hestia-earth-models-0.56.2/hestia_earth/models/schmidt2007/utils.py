from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.lookup import factor_value


def get_waste_values(term_id: str, cycle: dict, lookup_col: str):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.WASTE)
    values = non_empty_list(map(factor_value(None, term_id, f"{TermTermType.WASTE.value}.csv", lookup_col), products))
    return [0] if all([
        len(values) == 0,
        _is_term_type_complete(cycle, {'termType': TermTermType.WASTE.value}),
        cycle.get('@type', cycle.get('type')) == NodeType.CYCLE.value  # ignore adding 0 value for Transformation
    ]) else values
