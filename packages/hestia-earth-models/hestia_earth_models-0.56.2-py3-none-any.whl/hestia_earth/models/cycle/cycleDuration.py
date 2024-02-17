"""
Cycle duration

This model calculates the cycle duration using the cropping intensity for a single year.
"""
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "365",
        "endDate": "",
        "practices": [{"@type": "Practice", "value": "", "term.@id": "croppingIntensity"}],
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        }
    }
}
RETURNS = {
    "a `number` or `None` if requirements are not met": ""
}
MODEL_KEY = 'cycleDuration'
DEFAULT_DURATION = 365


def _run(croppingIntensity: float): return croppingIntensity * DEFAULT_DURATION


def _should_run(cycle: dict):
    croppingIntensity = find_term_match(cycle.get('practices', []), 'croppingIntensity').get('value', [None])[0]
    cycleDuration = cycle.get('cycleDuration')
    site_type_valid = valid_site_type(cycle)

    logRequirements(cycle, model=MODEL, key=MODEL_KEY,
                    cycleDuration=cycleDuration,
                    croppingIntensity=croppingIntensity,
                    site_type_valid=site_type_valid)

    should_run = all([site_type_valid, cycleDuration == 365, croppingIntensity])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run, croppingIntensity


def run(cycle: dict):
    should_run, croppingIntensity = _should_run(cycle)
    return _run(croppingIntensity) if should_run else None
