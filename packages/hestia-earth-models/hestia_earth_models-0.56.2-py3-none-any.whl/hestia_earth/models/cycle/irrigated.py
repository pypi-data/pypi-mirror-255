from hestia_earth.schema import TermTermType, CycleFunctionalUnit
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.input import get_total_irrigation_m3
from hestia_earth.models.utils.completeness import _is_term_type_complete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.water": "",
        "functionalUnit": "1 ha",
        "none": {
            "practices": [{"@type": "Practice", "units": ["%", "% area"], "term.termType": "waterRegime"}]
        },
        "optional": {
            "inputs": [{"@type": "Input", "term.termType": "water", "value": ""}]
        }
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'irrigated'
MIN_IRRIGATION_M3 = 250


def _practice(value: float):
    practice = _new_practice(TERM_ID)
    practice['value'] = [value]
    return practice


def _run(irrigation_m3: float):
    value = 100 if irrigation_m3 > MIN_IRRIGATION_M3 else 0
    return [_practice(value)]


def _should_run(cycle: dict):
    functional_unit = cycle.get('functionalUnit')
    water_complete = _is_term_type_complete(cycle, {'termType': TermTermType.WATER.value})
    irrigation_value_m3 = get_total_irrigation_m3(cycle)

    water_regime = filter_list_term_type(cycle.get('practices', []), TermTermType.WATERREGIME)
    no_irrigation_practice = not any(map(_is_irrigation_practice, water_regime))

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    no_irrigation_practice=no_irrigation_practice,
                    term_type_water_complete=water_complete,
                    irrigation_value_m3=irrigation_value_m3)

    should_run = all([
        no_irrigation_practice,
        functional_unit == CycleFunctionalUnit._1_HA.value,
        any([water_complete, irrigation_value_m3 > MIN_IRRIGATION_M3])
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, irrigation_value_m3


def _is_irrigation_practice(practice: dict): return practice.get('term', {}).get('units', '') in ['%', '% area']


def run(cycle: dict):
    should_run, irrigation_m3 = _should_run(cycle)
    return _run(irrigation_m3) if should_run else []
