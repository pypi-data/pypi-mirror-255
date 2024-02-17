from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from .utils import get_fuel_values
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "inputs": [
                {"@type": "Input", "value": "", "term.termType": "fuel", "optional": {
                    "operation": ""
                }}
            ],
            "completeness.electricityFuel": "True"
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "fuel": "so2ToAirFuelCombustionEmepEea2019",
    "operation": "so2ToAirFuelCombustionEmepEea2019"
}
TERM_ID = 'so2ToAirFuelCombustion'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(fuel_values: list):
    value = list_sum(fuel_values)
    return [_emission(value)]


def _should_run(cycle: dict):
    fuel_values = get_fuel_values(TERM_ID, cycle, LOOKUPS['fuel'])
    has_fuel = len(fuel_values) > 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_fuel=has_fuel)

    should_run = any([has_fuel])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, fuel_values


def run(cycle: dict):
    should_run, fuel_values = _should_run(cycle)
    return _run(fuel_values) if should_run else []
