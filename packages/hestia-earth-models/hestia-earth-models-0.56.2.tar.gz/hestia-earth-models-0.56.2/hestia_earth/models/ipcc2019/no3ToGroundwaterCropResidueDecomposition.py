from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_crop_residue_decomposition_N_total, get_ecoClimateZone
from .utils import get_FracLEACH_H
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "completeness.water": "True",
        "products": [
            {
                "@type": "Product",
                "value": "",
                "term.@id": "aboveGroundCropResidueLeftOnField",
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            },
            {
                "@type": "Product",
                "value": "",
                "term.@id": "aboveGroundCropResidueIncorporated",
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            },
            {
                "@type": "Product",
                "value": "",
                "term.@id": "belowGroundCropResidue",
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            }
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
TERM_ID = 'no3ToGroundwaterCropResidueDecomposition'
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
    N_total = get_crop_residue_decomposition_N_total(cycle)
    value, min, max, sd = get_FracLEACH_H(cycle, TERM_ID)
    converted_N_total = N_total * get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    return [_emission(
        converted_N_total * value,
        converted_N_total * sd,
        converted_N_total * min,
        converted_N_total * max
    )]


def _should_run(cycle: dict):
    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    ecoClimateZone = get_ecoClimateZone(cycle)
    crop_residue_complete = _is_term_type_complete(cycle, {'termType': TermTermType.CROPRESIDUE.value})
    water_complete = _is_term_type_complete(cycle, {'termType': TermTermType.WATER.value})

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_crop_residue=N_crop_residue,
                    ecoClimateZone=ecoClimateZone,
                    term_type_cropResidue_complete=crop_residue_complete,
                    term_type_water_complete=water_complete)

    should_run = all([N_crop_residue >= 0, ecoClimateZone, crop_residue_complete, water_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
