from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.crop import is_plantation
from .utils import get_region_factor
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "primary": "True",
            "term.termType": "crop"
        }],
        "site": {
            "@type": "Site",
            "or": [
                {"region": {"@type": "Term"}},
                {"country": {"@type": "Term"}}
            ]
        }
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
LOOKUPS = {
    "crop": "isPlantation",
    "region-landUseManagement": "croppingIntensity"
}
TERM_ID = 'croppingIntensity'


def _practice(value: float):
    practice = _new_practice(TERM_ID)
    practice['value'] = [round(value, 7)]
    return practice


def _run(cycle: dict):
    site = cycle.get('site')
    region_factor = get_region_factor(TERM_ID, site, TermTermType.LANDUSEMANAGEMENT)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    region_factor=region_factor)

    should_run = all([region_factor])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return [_practice(region_factor)] if should_run else []


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    not_plantation = not is_plantation(MODEL, TERM_ID, product.get('term', {}).get('@id'))

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    not_plantation=not_plantation)

    should_run = all([not_plantation])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
