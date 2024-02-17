from hestia_earth.schema import InputStatsDefinition
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": "crop",
            "value": "> 0"
        }],
        "completeness.other": "False"
    }
}
LOOKUPS = {
    "crop": ["seedPerKgYield", "seedPerKgYield-sd"]
}
RETURNS = {
    "Input": [{
        "value": "",
        "sd": "",
        "statsDefinition": "regions"
    }]
}
TERM_ID = 'seed'


def _input(value: float, sd: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    if sd > 0:
        input['sd'] = [sd]
        input['statsDefinition'] = InputStatsDefinition.REGIONS.value
    return input


def _run_product(product: dict):
    term = product.get('term', {})
    product_value = list_sum(product.get('value', []))
    value = safe_parse_float(get_lookup_value(term, LOOKUPS['crop'][0], model=MODEL, term=TERM_ID)) * product_value
    sd = safe_parse_float(get_lookup_value(term, LOOKUPS['crop'][1], model=MODEL, term=TERM_ID))
    return value, sd


def _run(products: list):
    values = list(map(_run_product, products))
    total_value = list_sum([value for value, _ in values])
    # TODO: we only fill-in sd for single values as the total value is complicated to calculate
    total_sd = values[0][1] if len(values) == 1 else 0
    return [_input(total_value, total_sd)] if total_value > 0 else []


def _should_run_product(product: dict):
    term = product.get('term', {})
    product_value = list_sum(product.get('value', []))
    has_all_lookups = all([get_lookup_value(term, col, model=MODEL, term=TERM_ID) for col in LOOKUPS['crop']])
    return all([has_all_lookups, product_value > 0])


def _should_run(cycle: dict):
    products = list(filter(_should_run_product, cycle.get('products', [])))
    has_products = len(products) > 0
    product_ids = ';'.join([p.get('term', {}).get('@id') for p in products])
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_seed_incomplete=term_type_incomplete,
                    has_products=has_products,
                    product_ids=product_ids)

    should_run = all([term_type_incomplete, has_products])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
