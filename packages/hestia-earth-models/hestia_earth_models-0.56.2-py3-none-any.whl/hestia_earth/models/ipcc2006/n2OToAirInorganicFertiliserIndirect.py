from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.cycle import get_inorganic_fertiliser_N_total
from hestia_earth.models.utils.emission import _new_emission
from .utils import get_nh3_no3_nox_to_n, COEFF_NH3NOX_N2O, COEFF_NO3_N2O
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [{
            "@type": "Input",
            "value": "",
            "term.termType": "inorganicFertiliser",
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            }
        }],
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "no3ToGroundwaterInorganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "nh3ToAirInorganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "noxToAirInorganicFertiliser"}
        ]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2OToAirInorganicFertiliserIndirect'
TIER = EmissionMethodTier.TIER_1.value
NO3_TERM_ID = 'no3ToGroundwaterInorganicFertiliser'
NH3_TERM_ID = 'nh3ToAirInorganicFertiliser'
NOX_TERM_ID = 'noxToAirInorganicFertiliser'


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, N_total: float):
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)
    debugValues(cycle, model=MODEL, term=TERM_ID,
                no3_n=no3_n,
                nh3_n=nh3_n,
                nox_n=nox_n)
    value = COEFF_NH3NOX_N2O * (
        N_total * 0.1 if nox_n == 0 or nh3_n == 0 else nh3_n + nox_n
    ) + COEFF_NO3_N2O * (
        N_total * 0.3 if no3_n == 0 else no3_n
    )
    return [_emission(value * get_atomic_conversion(Units.KG_N2O, Units.TO_N))]


def _should_run(cycle: dict):
    N_total = get_inorganic_fertiliser_N_total(cycle)
    term_type_complete = _is_term_type_complete(cycle, {'termType': 'fertiliser'})

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_total=N_total,
                    term_type_fertiliser_complete=term_type_complete)

    should_run = any([N_total, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_total


def run(cycle: dict):
    should_run, N_total = _should_run(cycle)
    return _run(cycle, N_total) if should_run else []
