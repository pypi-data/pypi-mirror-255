from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun
from .impact_assessment import convert_value_from_cycle, get_product
from .cycle import impact_lookup_value as cycle_lookup_value


def impact_lookup_value(model: str, term_id: str, impact_assessment: dict, lookup_col: str):
    cycle = impact_assessment.get('cycle', {})
    fuel_complete = cycle.get('completeness', {}).get('electricityFuel', False)
    product = get_product(impact_assessment)
    fuels = filter_list_term_type(cycle.get('inputs', []), TermTermType.FUEL)
    has_fuels = len(fuels) > 0
    fuels_value = convert_value_from_cycle(
        product, cycle_lookup_value(model, term_id, fuels, lookup_col), model=model, term_id=term_id
    )
    logRequirements(impact_assessment, model=model, term=term_id,
                    term_type_electricityFuel_complete=fuel_complete,
                    has_fuels=has_fuels,
                    fuels_value=fuels_value)

    should_run = any([
        fuel_complete and not has_fuels,
        fuel_complete and fuels_value is not None
    ])
    logShouldRun(impact_assessment, model, term_id, should_run)

    return (fuels_value or 0) if should_run else None
