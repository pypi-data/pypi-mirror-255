from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value, extract_grouped_data
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugMissingLookup, debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.input import get_feed_inputs, get_feed_content
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.property import get_node_property_value_converted
from hestia_earth.models.utils.liveAnimal import get_default_digestibility
from .utils import get_milkYield_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.grazedForage": "True",
        "or": [
            {
                "animals": [{
                    "@type": "Animal",
                    "inputs": [{
                        "@type": "Input",
                        "term.units": "kg",
                        "value": "> 0",
                        "optional": {
                            "properties": [{
                                "@type": "Property",
                                "value": "",
                                "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                            }]
                        }
                    }]
                }]
            },
            {
                "inputs": [{
                    "@type": "Input",
                    "term.units": "kg",
                    "value": "> 0",
                    "isAnimalFeed": "True",
                    "optional": {
                        "properties": [{
                            "@type": "Property",
                            "value": "",
                            "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                        }]
                    }
                }]
            }
        ]
    }
}
LOOKUPS = {
    "animalProduct": [
        "digestibility",
        "percentageYmMethaneConversionFactorEntericFermentationIPCC2019",
        "percentageYmMethaneConversionFactorEntericFermentationIPCC2019-sd"
    ],
    "liveAnimal": [
        "digestibility",
        "percentageYmMethaneConversionFactorEntericFermentationIPCC2019",
        "percentageYmMethaneConversionFactorEntericFermentationIPCC2019-sd"
    ],
    "crop-property": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "methodTier": "tier 2",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'ch4ToAirEntericFermentation'
TIER = EmissionMethodTier.TIER_2.value
METHANE_EC = 55.65  # MJ/kg CH4
DEFAULT_YM = {
    'value': 6.125,
    'min': 5.7,
    'max': 6.5,
    'description': 'Average Ym factor of 6.125% used as data missing to differentiate Ym.'
}


def _emission(value: float, sd: float = None, min: float = None, max: float = None, default: bool = False):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    if sd is not None:
        emission['sd'] = [sd]
        emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    if default:
        emission['min'] = [min]
        emission['max'] = [max]
        emission['description'] = DEFAULT_YM.get('description')
        emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['methodTier'] = TIER
    return emission


def _run(feed: float, enteric_factor: float, enteric_sd: float):
    value = feed * ((enteric_factor or DEFAULT_YM.get('value')) / 100) / METHANE_EC
    min = feed * (DEFAULT_YM.get('min') / 100) / METHANE_EC
    max = feed * (DEFAULT_YM.get('max') / 100) / METHANE_EC
    return [
        _emission(value, sd=enteric_sd, default=False) if enteric_factor
        else _emission(value, min=min, max=max, default=True)
    ]


DE_NDF_MAPPING = {
    'high_DE_low_NDF': lambda DE, NDF: DE >= 70 and NDF < 35,
    'high_DE_high_NDF': lambda DE, NDF: DE >= 70 and NDF >= 35,
    'medium_DE_high_NDF': lambda DE, NDF: 63 <= DE < 70 and NDF > 37,
    'low_DE_high_NDF': lambda DE, NDF: DE < 62 and NDF >= 38
}
MILK_YIELD_MAPPING = {
    'high_DE_low_NDF': lambda milk_yield: milk_yield > 8500,
    'high_DE_high_NDF': lambda milk_yield: milk_yield > 8500,
    'medium_DE_high_NDF': lambda milk_yield: 5000 <= milk_yield <= 8500,
    'low_DE_high_NDF': lambda milk_yield: 0 < milk_yield < 5000
}

DE_MAPPING = {
    'high_medium_DE': lambda DE, _: DE > 63,
    'medium_DE': lambda DE, _: DE > 62 and DE < 72,
    'low_DE': lambda DE, _: DE <= 62,
    'high_DE': lambda DE, _: DE >= 72,
    'high_DE_ionophore': lambda DE, ionophore: DE > 75 and ionophore
}


def _get_grouped_data_key(keys: list, DE: float, NDF: float, ionophore: bool, milk_yield: float):
    # test conditions one by one and return the key associated for the first one that passes
    return (
        next(
            (key for key in keys if key in DE_NDF_MAPPING and DE_NDF_MAPPING[key](DE, NDF)),
            None
        ) or next(
            (key for key in keys if key in DE_MAPPING and DE_MAPPING[key](DE, ionophore)),
            None
        ) if DE else None
    ) or (
        next(
            (key for key in keys if key in MILK_YIELD_MAPPING and MILK_YIELD_MAPPING[key](milk_yield)),
            None
        ) if milk_yield else None
    )


def _extract_groupped_data(value: str, DE: float, NDF: float, ionophore: bool, milk_yield: float):
    value_keys = [val.split(':')[0] for val in value.split(';')]
    value_key = _get_grouped_data_key(value_keys, DE, NDF, ionophore, milk_yield)
    return safe_parse_float(extract_grouped_data(value, value_key))


def _get_lookup_value(lookup, term: dict, lookup_col: str, DE: float, NDF: float, ionophore: bool, milk_yield: float):
    term_id = term.get('@id')
    value = get_table_value(lookup, 'termid', term_id, column_name(lookup_col)) if term_id else None
    debugMissingLookup(f"{term.get('termType')}.csv", 'termid', term_id, lookup_col, value, model=MODEL, term=TERM_ID)
    return value if value is None or ':' not in value else _extract_groupped_data(value, DE, NDF, ionophore, milk_yield)


def _get_crop_property_average(cycle: dict, inputs: list, property_id: str):
    values = [get_node_property_value_converted(MODEL, input, property_id) for input in inputs]
    property_value = list_sum(values)
    ratio_inputs_with_props = len(values) / len(inputs) if len(inputs) and len(values) else 0
    total_value = list_sum([list_sum(i.get('value', [])) for i in inputs])

    logRequirements(cycle, model=MODEL, term=TERM_ID, property_id=property_id,
                    nb_inputs=len(inputs),
                    nb_inputs_with_prop=len(values),
                    ratio_inputs_with_props=ratio_inputs_with_props,
                    min_ratio=0.8)

    return (property_value / total_value) if total_value > 0 and ratio_inputs_with_props > 0.8 else 0


def _get_milk_yield(cycle: dict):
    value = list_sum(get_milkYield_practice(cycle).get('value', []), 0)
    return value * 365 if value > 0 else None


def _get_DE_type(lookup, term_id: str, term_type: str):
    lookup_col = LOOKUPS.get(term_type, [None])[0]
    value = get_table_value(lookup, 'termid', term_id, column_name(lookup_col)) if lookup_col else None
    debugMissingLookup(f"{term_type}.csv", 'termid', term_id, lookup_col, value, model=MODEL, term=TERM_ID)
    return value


def _is_ionophore(cycle: dict, total_feed: float):
    inputs = cycle.get('inputs', [])
    has_input = find_term_match(inputs, 'ionophores', None) is not None
    maize_input = find_term_match(inputs, 'maizeSteamFlaked', {'value': 0})
    maize_feed = get_feed_content(MODEL, inputs=[maize_input])
    return has_input and maize_feed / total_feed >= 0.9


def _should_run(cycle: dict):
    is_animalFeed_complete = cycle.get('completeness', {}).get('animalFeed', False) is True
    is_grazedForage_complete = cycle.get('completeness', {}).get('grazedForage', False) is True

    primary_product = find_primary_product(cycle) or {}
    term = primary_product.get('term', {})
    term_id = term.get('@id')
    term_type = term.get('termType')
    lookup_name = f"{term_type}.csv"
    lookup = download_lookup(lookup_name)

    DE_type = _get_DE_type(lookup, term_id, term_type) if term_id else None

    feed_inputs = get_feed_inputs(cycle)

    total_feed = get_feed_content(MODEL, inputs=feed_inputs)
    ionophore = _is_ionophore(cycle, total_feed) if total_feed > 0 else False
    milk_yield = _get_milk_yield(cycle)

    # only keep inputs that have a positive value
    inputs = list(filter(lambda i: list_sum(i.get('value', [])) > 0, feed_inputs))
    DE = (
        _get_crop_property_average(cycle, inputs, DE_type) if DE_type and isinstance(DE_type, str) else None
    ) or get_default_digestibility(MODEL, TERM_ID, cycle)
    NDF = _get_crop_property_average(cycle, inputs, 'neutralDetergentFibreContent')

    enteric_factor = safe_parse_float(_get_lookup_value(
        lookup, term, LOOKUPS['liveAnimal'][1], DE, NDF, ionophore, milk_yield
    ), None)
    enteric_sd = safe_parse_float(_get_lookup_value(
        lookup, term, LOOKUPS['liveAnimal'][2], DE, NDF, ionophore, milk_yield
    ), None)

    debugValues(cycle, model=MODEL, term=TERM_ID,
                DE_type=DE_type,
                digestibility=DE,
                ndf=NDF,
                ionophore=ionophore,
                milk_yield=milk_yield,
                enteric_factor=enteric_factor,
                enteric_sd=enteric_sd)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_animalFeed_complete=is_animalFeed_complete,
                    term_type_grazedForage_complete=is_grazedForage_complete,
                    total_feed=total_feed)

    should_run = all([is_animalFeed_complete, is_grazedForage_complete, total_feed])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, total_feed, enteric_factor, enteric_sd


def run(cycle: dict):
    should_run, feed, enteric_factor, enteric_sd = _should_run(cycle)
    return _run(feed, enteric_factor, enteric_sd) if should_run else []
