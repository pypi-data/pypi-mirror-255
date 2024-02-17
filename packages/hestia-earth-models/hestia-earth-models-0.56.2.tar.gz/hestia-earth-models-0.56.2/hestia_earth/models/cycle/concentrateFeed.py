"""
Concentrate feed Properties

This model calculates all of the nutrient content values and dry matter values for a feed blend
if we know the crops that went into the blend by taking a weighted average.
"""
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum, non_empty_list, flatten

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.property import _new_property, get_node_property_value, get_property_lookup_value
from hestia_earth.models.utils.term import get_digestible_energy_terms, get_energy_digestibility_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{"@type": "Practice", "value": "", "term.termType": ["crop", "animalProduct"]}],
        "products": [
            {
                "@type": "Product",
                "primary": "True",
                "term.@id": ["concentrateFeedUnspecified", "concentrateFeedBlend", "feedMix"]
            }
        ]
    }
}
RETURNS = {
    "Product": [{
        "properties": [{
            "@type": "Property"
        }]
    }]
}
LOOKUPS = {
    "crop-property": "crudeProteinContent",
    "property": "commonToSupplementInAnimalFeed"
}
TERM_ID = 'concentrateFeedBlend,concentrateFeedUnspecified,feedMix'
INPUT_TERM_TYPES = [TermTermType.CROP.value, TermTermType.ANIMALPRODUCT.value]


def _property(term_id: str, value: float):
    prop = _new_property(term_id)
    prop['value'] = value
    return prop


def _min_ratio(term_id: str):
    value = get_property_lookup_value(MODEL, term_id, LOOKUPS['property'])
    # value is a Numpy bool so use negation
    return 1 if not value else 0.8


def _weighted_value(values: list):
    total_weight = sum(weight for _v, weight in values)
    weighted_values = [value * weight for value, weight in values]
    return sum(weighted_values) / (total_weight if total_weight != 0 else 1)


def _calculate_value(cycle: dict, product: dict, inputs: list, property_id: str, values: list):
    values = [(prop_value, value) for id, prop_value, value in values if value and prop_value]
    ratio_inputs_with_props = len(inputs) / len(values) if len(inputs) and len(values) else 0
    min_ratio = _min_ratio(property_id)

    term_id = product.get('term', {}).get('@id')
    logRequirements(cycle, model=MODEL, term=term_id, property=property_id,
                    nb_inputs=len(inputs),
                    nb_inputs_with_prop=len(values),
                    ratio_inputs_with_props=ratio_inputs_with_props,
                    min_ratio=min_ratio)

    should_run = all([ratio_inputs_with_props >= min_ratio])
    logShouldRun(cycle, MODEL, term_id, should_run, property=property_id)

    return [(property_id, _weighted_value(values))] if should_run else []


def _calculate_default_value(cycle: dict, product: dict, inputs: list, property_id: str):
    values = [(
        i.get('term', {}).get('@id'),
        get_node_property_value(MODEL, i, property_id),
        list_sum(i.get('value', []))
    ) for i in inputs]
    return _calculate_value(cycle, product, inputs, property_id, values)


def _calculate_N_value(cycle: dict, product: dict, inputs: list, property_id: str):
    values = [(
        i.get('term', {}).get('@id'),
        get_node_property_value(MODEL, i, property_id) or
        get_node_property_value(MODEL, i, 'crudeProteinContent') * 0.16,
        list_sum(i.get('value', []))
    ) for i in inputs]
    return _calculate_value(cycle, product, inputs, property_id, values)


def _calculate_digestibleEnergy(cycle: dict, product: dict, inputs: list, *args):
    property_ids = get_digestible_energy_terms()
    return flatten([_calculate_default_value(cycle, product, inputs, id) for id in property_ids])


def _calculate_energyDigestibility(cycle: dict, product: dict, inputs: list, *args):
    property_ids = get_energy_digestibility_terms()
    return flatten([_calculate_default_value(cycle, product, inputs, id) for id in property_ids])


PROPERTY_TO_VALUE = {
    'crudeProteinContent': _calculate_default_value,
    'digestibleEnergy': _calculate_digestibleEnergy,
    'dryMatter': _calculate_default_value,
    'energyContentHigherHeatingValue': _calculate_default_value,
    'energyDigestibility': _calculate_energyDigestibility,
    'neutralDetergentFibreContent': _calculate_default_value,
    'nitrogenContent': _calculate_N_value,
    'phosphorusContentAsP': _calculate_default_value
}


def _run_property(cycle: dict, product: dict, inputs: list):
    def exec(values: tuple):
        term_id, func = values
        values = func(cycle, product, inputs, term_id)
        return [_property(id, value) for id, value in values if value]
    return exec


def _run(cycle: dict, product: dict, inputs: list):
    properties = non_empty_list(flatten(map(_run_property(cycle, product, inputs), PROPERTY_TO_VALUE.items())))
    return [{**product, 'properties': product.get('properties', []) + properties}] if len(properties) > 0 else []


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    term_ids = TERM_ID.split(',')
    has_product = product.get('term', {}).get('@id') in term_ids

    inputs = [i for i in cycle.get('inputs', []) if i.get('term', {}).get('termType') in INPUT_TERM_TYPES]
    has_inputs = len(inputs) > 0

    should_run = all([has_product, has_inputs])
    return should_run, product, inputs


def run(cycle: dict):
    should_run, product, inputs = _should_run(cycle)
    return _run(cycle, product, inputs) if should_run else []
