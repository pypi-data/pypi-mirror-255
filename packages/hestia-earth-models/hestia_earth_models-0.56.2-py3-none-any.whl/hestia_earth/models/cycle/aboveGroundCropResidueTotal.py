"""
This model gap-fills the amount of above ground crop residue total if any matching management practice
and crop residue products are provided. Examples:
- if `residueLeftOnField` = `50%` and `aboveGroundCropResidueLeftOnField` = `1000kg`, the total is `2000kg`;
- if `residueLeftOnField` = `100%` and `aboveGroundCropResidueLeftOnField` = `1000kg`, the total is `1000kg`.
"""
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.product import _new_product
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "practices": [{"@type": "Practice", "value": "", "term.termType": "cropResidue"}],
        "products": [{"@type": "Product", "value": "", "term.termType": "cropResidueManagement"}]
    }
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
TERM_ID = 'aboveGroundCropResidueTotal'


def _product(value: float):
    product = _new_product(TERM_ID, value)
    return product


def _run(practice: dict, product: dict):
    practice_value = list_sum(practice.get('value', []))
    product_value = list_sum(product.get('value', []))
    value = 0 if any([practice_value == 0 or product_value == 0]) else product_value / (practice_value / 100)
    return [_product(value)]


def _should_run(cycle: dict):
    # run if any practice equals 100% with a product value
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROPRESIDUE)

    def _matching_product(practice: dict):
        term_id = practice.get('term', {}).get('@id')
        product = next((
            p for p in products if all([
                p.get('value', []),
                p.get('term', {}).get('@id').lower().endswith(term_id.lower())
            ])
        ), None)
        return (practice, product) if product else None

    matching_practices = non_empty_list(map(_matching_product, practices))
    practice, matching_product = (matching_practices or [(None, None)])[0]

    practice_id = (practice or {}).get('term', {}).get('@id')
    product_id = (matching_product or {}).get('term', {}).get('@id')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    practice_id=practice_id,
                    product_id=product_id)

    should_run = all([practice_id, product_id])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, practice, matching_product


def run(cycle: dict):
    should_run, practice, matching_product = _should_run(cycle)
    return _run(practice, matching_product) if should_run else []
