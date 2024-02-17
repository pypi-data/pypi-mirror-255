from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.other": "False",
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}],
        "site": {"@type": "Site", "siteType": ["cropland", "permanent pasture"]}
    }
}
LOOKUPS = {
    "crop": "Saplings_required"
}
RETURNS = {
    "Input": [{
        "value": ""
    }]
}
TERM_ID = 'saplings'


def _input(value: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    return input


def _get_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop']), None)


def _run(cycle: dict):
    def run_product(product):
        value = _get_value(product)
        return None if value is None else _input(value)

    return non_empty_list(map(run_product, cycle.get('products', [])))


def _should_run(cycle: dict):
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_seed_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
