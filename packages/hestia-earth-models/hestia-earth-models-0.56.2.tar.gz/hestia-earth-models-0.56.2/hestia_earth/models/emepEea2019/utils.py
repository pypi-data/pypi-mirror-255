from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.lookup import extract_grouped_data
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL


def _get_fuel_input_value(term_id: str, lookup_col: str):
    def get_value(input: dict):
        input_term = input.get('term', {})
        input_term_id = input_term.get('@id')
        operation_term = input.get('operation', {})
        input_value = list_sum(input.get('value', []))

        operation_factor = extract_grouped_data(
            get_lookup_value(operation_term, lookup_col, model=MODEL, term=term_id), input_term_id
        ) if operation_term else None
        input_factor = operation_factor or get_lookup_value(input_term, lookup_col, model=MODEL, term=term_id)

        return input_value * safe_parse_float(input_factor)
    return get_value


def get_fuel_values(term_id: str, cycle: dict, lookup_col: str):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.FUEL)
    values = list(map(_get_fuel_input_value(term_id, lookup_col), inputs))

    return [0] if all([
        len(values) == 0,
        _is_term_type_complete(cycle, {'termType': 'electricityFuel'}),
        cycle.get('@type', cycle.get('type')) == NodeType.CYCLE.value  # ignore adding 0 value for Transformation
    ]) else values
