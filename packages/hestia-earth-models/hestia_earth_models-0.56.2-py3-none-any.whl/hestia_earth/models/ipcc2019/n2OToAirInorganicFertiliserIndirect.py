from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.cycle import get_inorganic_fertiliser_N_total, get_ecoClimateZone
from hestia_earth.models.utils.emission import _new_emission
from .utils import get_nh3_no3_nox_to_n, COEFF_NO3_N2O, COEFF_N_NH3NOX_inorganic, get_FracNH3NOx_N2O, get_FracLEACH_H
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "completeness.water": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "inorganicFertiliser",
                "term.units": "kg N"
            }
        ],
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "no3ToGroundwaterInorganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "nh3ToAirInorganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "noxToAirInorganicFertiliser"}
        ],
        "site": {
            "@type": "Site",
            "measurements": [{"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}]
        },
        "optional": {
            "practices": [{"@type": "Practice", "value": "", "term.termType": "waterRegime"}]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}

TERM_ID = 'n2OToAirInorganicFertiliserIndirect'
NO3_TERM_ID = 'no3ToGroundwaterInorganicFertiliser'
NH3_TERM_ID = 'nh3ToAirInorganicFertiliser'
NOX_TERM_ID = 'noxToAirInorganicFertiliser'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, sd: float, min: float, max: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['sd'] = [sd]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict):
    N_total = get_inorganic_fertiliser_N_total(cycle)
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)
    debugValues(cycle, model=MODEL, term=TERM_ID,
                no3_n=no3_n,
                nh3_n=nh3_n,
                nox_n=nox_n)
    value, min_val, max_val, std = [
        get_FracNH3NOx_N2O(cycle, TERM_ID)[x] * (
            N_total * COEFF_N_NH3NOX_inorganic[x] if nox_n == 0 or nh3_n == 0 else nh3_n + nox_n
        ) +
        COEFF_NO3_N2O[x] * (
            N_total * get_FracLEACH_H(cycle, TERM_ID)[x] if no3_n == 0 else no3_n
        ) for x in range(4)
    ]
    return [_emission(
        value * get_atomic_conversion(Units.KG_N2O, Units.TO_N),
        std * get_atomic_conversion(Units.KG_N2O, Units.TO_N),
        min_val * get_atomic_conversion(Units.KG_N2O, Units.TO_N),
        max_val * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    )]


def _should_run(cycle: dict):
    N_inorganic_fertiliser = get_inorganic_fertiliser_N_total(cycle)
    ecoClimateZone = get_ecoClimateZone(cycle)
    fertiliser_complete = _is_term_type_complete(cycle, {'termType': 'fertiliser'})
    water_complete = _is_term_type_complete(cycle, {'termType': TermTermType.WATER.value})

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_inorganic_fertiliser=N_inorganic_fertiliser,
                    ecoClimateZone=ecoClimateZone,
                    term_type_fertiliser_complete=fertiliser_complete,
                    term_type_water_complete=water_complete)

    should_run = all([N_inorganic_fertiliser >= 0, ecoClimateZone, fertiliser_complete, water_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
