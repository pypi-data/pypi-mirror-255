"""
Linked Impact Assessment

A model which takes recalculated data from an Impact Assessment linked to an Input in a Cycle.
"""
from functools import reduce
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import load_impacts
from hestia_earth.models.utils.blank_node import group_by_keys

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "value": "> 0",
            "impactAssessment": ""
        }]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "background",
        "inputs": "",
        "operation": ""
    }]
}
MODEL = 'linkedImpactAssessment'
MODEL_AGGREGATED = 'hestiaAggregatedData'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(cycle: dict, term_id: str, value: float, input: dict, model: str):
    # log run on each emission so we know it did run
    input_term_id = input.get('term', {}).get('@id')
    operation_term_id = input.get('operation', {}).get('term', {}).get('@id')
    logShouldRun(cycle, model, term_id, True, methodTier=TIER, input=input_term_id, operation=operation_term_id)
    emission = _new_emission(term_id, model)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['inputs'] = [input.get('term')]
    if input.get('operation'):
        emission['operation'] = input.get('operation')
    return emission


def _emission_group(term_id: str):
    lookup = download_lookup('emission.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('inputProductionGroupId'))


def _group_emissions(impact: dict):
    def _group_by(prev: dict, emission: dict):
        term_id = emission.get('term', {}).get('@id')
        grouping = _emission_group(term_id)
        if grouping:
            prev[grouping] = prev.get(grouping, 0) + (emission.get('value', 0) or 0)
        return prev

    emissions = impact.get('emissionsResourceUse', [])
    return reduce(_group_by, emissions, {})


def _run_input(cycle: dict):
    def run(inputs: list):
        input = inputs[0]
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        term_id = input.get('term', {}).get('@id')
        impact = input.get('impactAssessment')
        model = MODEL_AGGREGATED if impact.get('aggregated', False) else MODEL
        emissions = _group_emissions(impact)
        logRequirements(cycle, model=model, term=term_id,
                        impact_assessment_id=input.get('impactAssessment', {}).get('@id'))
        logShouldRun(cycle, model, term_id, True, methodTier=TIER)
        return [
            _emission(cycle, id, input_value * value, input, model) for id, value in emissions.items()
        ]
    return run


def run(_, cycle: dict):
    inputs = load_impacts(cycle.get('inputs', []))
    inputs = [i for i in inputs if list_sum(i.get('value', [])) > 0]
    logger.debug('model=%s, nb inputs=%s', MODEL, len(inputs))
    # group inputs with same id/operation to avoid adding emissions twice
    inputs = reduce(group_by_keys(['term', 'operation']), inputs, {})
    return flatten(map(_run_input(cycle), inputs.values()))
