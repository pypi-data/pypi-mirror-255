from hestia_earth.schema import TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten, non_empty_list, list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from .impact_assessment import convert_value_from_cycle, get_product
from .cycle import impact_lookup_value as cycle_lookup_value


def _get_input_from_properties(input: dict):
    input_value = list_sum(input.get('value', []))
    properties = input.get('properties') or download_hestia(input.get('term', {}).get('@id')).get('defaultProperties')
    return non_empty_list([
        {'term': p.get('key'), 'value': [p.get('value') / 100 * input_value]} for p in (properties or []) if all([
            p.get('key'), p.get('value')
        ])
    ]) if input_value > 0 else []


def get_from_inputs(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.PESTICIDEBRANDNAME)
    return flatten([
        _get_input_from_properties(i) for i in inputs
    ])


def impact_lookup_value(model: str, term_id: str, impact_assessment: dict, lookup_col: str):
    cycle = impact_assessment.get('cycle', {})
    is_complete = cycle.get('completeness', {}).get('pesticideVeterinaryDrug', False)
    product = get_product(impact_assessment)
    pesticides = filter_list_term_type(cycle.get('inputs', []), TermTermType.PESTICIDEAI) + get_from_inputs(cycle)
    has_pesticides_inputs = len(pesticides) > 0
    pesticides_value = convert_value_from_cycle(
        product, cycle_lookup_value(model, term_id, pesticides, lookup_col, False), model=model, term_id=term_id
    )
    logRequirements(impact_assessment, model=model, term=term_id,
                    term_type_pesticideVeterinaryDrug_complete=is_complete,
                    has_pesticides_inputs=has_pesticides_inputs)

    should_run = any([
        is_complete and not has_pesticides_inputs,
        is_complete and pesticides_value is not None
    ])
    logShouldRun(impact_assessment, model, term_id, should_run)

    return (pesticides_value or 0) if should_run else None
