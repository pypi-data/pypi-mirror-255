"""
Excreta (kg)

This model calculates the amount of excreta in `kg` based on the amount of excreta in `kg N` or `kg Vs`.
"""
from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import non_empty_list, list_sum

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import get_kg_term_id, get_kg_N_term_id, get_kg_VS_term_id
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.product import _new_product, convert_product_to_unit
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [
            {
                "@type": "Product",
                "term.termType": "excreta",
                "term.units": ["kg N", "kg VS"]
            }
        ]
    }
}
RETURNS = {
    "Product": [{
        "term.termType": "excreta",
        "term.units": "kg",
        "value": ""
    }]
}
MODEL_KEY = 'excretaKgMass'
MODEL_LOG = '/'.join([MODEL, MODEL_KEY])

UNITS = [
    Units.KG_N.value,
    Units.KG_VS.value
]


def _product(value: float, term_id: str):
    product = _new_product(term_id, value)
    return product


def _get_existing_product(cycle: dict, term_id: str):
    term_ids = [
        get_kg_term_id(term_id),  # set `kg` as first item because it usually contains the conversion ratios
        get_kg_N_term_id(term_id),
        get_kg_VS_term_id(term_id)
    ]
    products = non_empty_list([find_term_match(cycle.get('products', []), id, None) for id in term_ids])
    return products[0]


def _run_product(cycle: dict, term_id: str):
    existing_product = _get_existing_product(cycle, term_id)

    term = download_hestia(term_id)
    product = {
        'term': term,
        'value': [1]
    }
    # get the factor from converting 1 kg in the current product units and apply to product value
    conversion_to_kg_ratio = convert_product_to_unit(product, existing_product.get('term', {}).get('units'))
    value = list_sum(existing_product.get('value', [])) / conversion_to_kg_ratio if conversion_to_kg_ratio else None

    debugValues(cycle, model=MODEL_LOG, term=term_id,
                using_excreta_product=(existing_product or {}).get('term', {}).get('@id'),
                conversion_to_kg_ratio=conversion_to_kg_ratio,
                value=value)

    return _product(value, term_id) if value else None


def _should_run(cycle: dict):
    node_type = cycle.get('type', cycle.get('@type'))
    excreta_products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    kg_term_ids = list(set([
        get_kg_term_id(p.get('term', {}).get('@id')) for p in excreta_products
        if p.get('term', {}).get('units') in UNITS
    ]))
    missing_term_ids = [
        term_id for term_id in kg_term_ids if not find_term_match(excreta_products, term_id, None)
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
