"""
Excreta (kg VS)

This model calculates the amount of excreta in `kg VS` based on the amount of excreta in `kg`.
"""
from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit, get_kg_term_id, get_kg_VS_term_id
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.product import _new_product, convert_product_to_unit
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [
            {
                "@type": "Product",
                "term.termType": "excreta",
                "term.units": ["kg"]
            }
        ]
    }
}
RETURNS = {
    "Product": [{
        "term.termType": "excreta",
        "term.units": "kg VS",
        "value": ""
    }]
}
MODEL_KEY = 'excretaKgVs'
MODEL_LOG = '/'.join([MODEL, MODEL_KEY])


def _product(value: float, term_id: str):
    product = _new_product(term_id, value)
    return product


def _run_product(cycle: dict, term_id: str):
    existing_product = find_term_match(cycle.get('products', []), get_kg_term_id(term_id))
    value = convert_product_to_unit(existing_product, Units.KG_VS)

    debugValues(cycle, model=MODEL_LOG, term=term_id,
                using_excreta_product=(existing_product or {}).get('term', {}).get('@id'),
                value=value)

    return _product(value, term_id)


def _should_run(cycle: dict):
    node_type = cycle.get('type', cycle.get('@type'))
    excreta_products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    excreta_products_kg = _filter_list_term_unit(excreta_products, Units.KG)
    kg_N_term_ids = list(set([
        get_kg_VS_term_id(p.get('term', {}).get('@id')) for p in excreta_products_kg
    ]))
    missing_term_ids = [
        term_id for term_id in kg_N_term_ids if not find_term_match(excreta_products, term_id, None)
    ]
    has_missing_term_ids = len(missing_term_ids) > 0

    logRequirements(cycle, model=MODEL_LOG,
                    node_type=node_type,
                    has_missing_term_ids=has_missing_term_ids,
                    missing_term_ids=';'.join(missing_term_ids))

    should_run = all([node_type == NodeType.CYCLE.value, has_missing_term_ids])
    for term_id in missing_term_ids:
        logShouldRun(cycle, MODEL_LOG, term_id, should_run)
    logShouldRun(cycle, MODEL_LOG, None, should_run)
    return should_run, missing_term_ids


def run(cycle: dict):
    should_run, missing_term_ids = _should_run(cycle)
    return non_empty_list([_run_product(cycle, term_id) for term_id in missing_term_ids]) if should_run else []
