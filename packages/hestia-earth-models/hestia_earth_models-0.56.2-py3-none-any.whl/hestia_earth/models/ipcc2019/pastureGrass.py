"""
Full Grass Consumption

This model estimates the energetic requirements of ruminants and can be used to estimate the amount of grass they graze.
Source:
[IPCC 2019, Vol.4, Chapter 10](https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch10_Livestock.pdf).
"""
from hestia_earth.schema import TermTermType, AnimalReferencePeriod
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.input import _new_input, get_feed_inputs
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.term import get_lookup_value, get_wool_terms
from hestia_earth.models.utils.property import get_node_property, get_node_property_value, _node_property_value
from .utils import get_milkYield_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "False",
        "site": {
            "@type": "Site",
            "siteType": "permanent pasture"
        },
        "practices": [{
            "@type": "Practice",
            "value": "",
            "term.@id": "pastureGrass",
            "key": {
                "@type": "Term",
                "term.termType": ["crop", "landCover"]
            }
        }],
        "animals": [{
            "@type": "Animal",
            "value": "> 0",
            "term.termType": "liveAnimal",
            "referencePeriod": "average",
            "properties": [{
                "@type": "Property",
                "value": "",
                "term.@id": [
                    "liveweightPerHead",
                    "weightAtMaturity"
                ]
            }],
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": [
                        "hoursWorkedPerDay",
                        "pregnancyRateTotal",
                        "animalsPerBirth"
                    ]
                }],
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
                }],
                "practices": [{
                    "@type": "Practice",
                    "value": "",
                    "term.termType": "animalManagement",
                    "properties": [{
                        "@type": "Property",
                        "value": "",
                        "term.@id": "fatContent"
                    }]
                }]
            }
        }],
        "optional": {
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
            }],
            "products": [{
                "@type": "Product",
                "value": "",
                "term.@id": "animalProduct"
            }]
        }
    }
}
LOOKUPS = {
    "animalManagement": [
        "mjKgEvMilkIpcc2019"
    ],
    "animalProduct": "mjKgEVwoolNetEnergyWoolIpcc019",
    "liveAnimal": [
        "ipcc2019AnimalTypeGrouping",
        "mjDayKgCfiNetEnergyMaintenanceIpcc2019",
        "ratioCPregnancyNetEnergyPregnancyIpcc2019",
        "ratioCNetEnergyGrowthCattleBuffaloIpcc2019",
        "MjKgABNetEnergyGrowthSheepGoatsIpcc2019"
    ],
    "system-liveAnimal-activityCoefficient-ipcc2019": "using animal term @id",
    "crop-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"],
    "crop": "grazedPastureGrassInputId",
    "forage-property": ["energyDigestibilityRuminants", "energyContentHigherHeatingValue"],
    "landCover": "grazedPastureGrassInputId"
}
RETURNS = {
    "Input": [{
        "term.termType": ["crop", "forage"],
        "value": ""
    }]
}
MODEL_KEY = 'pastureGrass'
KEY_TERM_TYPES = [
    TermTermType.CROP.value,
    TermTermType.LANDCOVER.value
]


def _input(term_id: str, value: float):
    node = _new_input(term_id, MODEL)
    node['value'] = [value]
    return node


def _practice_input_id(practice: dict): return get_lookup_value(practice.get('key', {}), 'grazedPastureGrassInputId')


def _get_grouping(animal: dict):
    term = animal.get('term', {})
    return get_lookup_value(term, 'ipcc2019AnimalTypeGrouping')


def _get_activityCoefficient(cycle: dict, animal: dict, system: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')
    system_id = system.get('term', {}).get('@id')
    lookup = download_lookup('system-liveAnimal-activityCoefficient-ipcc2019.csv')
    activityCoefficient = safe_parse_float(get_table_value(lookup, 'termid', system_id, column_name(term_id)), 0)

    debugValues(cycle, model=MODEL, term=term_id,
                activityCoefficient=activityCoefficient)

    return activityCoefficient


def _calculate_NEm(cycle: dict, animal: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')

    mjDayKgCfiNetEnergyMaintenance = safe_parse_float(
        get_lookup_value(term, 'mjDayKgCfiNetEnergyMaintenanceIpcc2019'), 0
    )
    liveweightPerHead = get_node_property(animal, 'liveweightPerHead', False).get('value', 0)
    animal_value = animal.get('value', 0)
    cycleDuration = cycle.get('cycleDuration', 365)
    NEm = mjDayKgCfiNetEnergyMaintenance * pow(liveweightPerHead, 0.75) * animal_value * cycleDuration

    debugValues(cycle, model=MODEL, term=term_id,
                mjDayKgCfiNetEnergyMaintenance=mjDayKgCfiNetEnergyMaintenance,
                liveweightPerHead=liveweightPerHead,
                NEm=NEm)

    return NEm


def _calculate_NEa_cattleAndBuffalo(cycle: dict, animal: dict, system: dict, NEm: float):
    term = animal.get('term', {})
    term_id = term.get('@id')

    activityCoefficient = _get_activityCoefficient(cycle, animal, system)

    NEa = activityCoefficient * NEm

    debugValues(cycle, model=MODEL, term=term_id,
                NEa=NEa)

    return term_id, NEa


def _calculate_NEa_sheepAndGoat(cycle: dict, animal: dict, system: dict, _NEm: float):
    term = animal.get('term', {})
    term_id = term.get('@id')

    activityCoefficient = _get_activityCoefficient(cycle, animal, system)

    liveweightPerHead = get_node_property(animal, 'liveweightPerHead', False).get('value', 0)
    animal_value = animal.get('value', 0)
    cycleDuration = cycle.get('cycleDuration', 365)
    NEa = activityCoefficient * liveweightPerHead * animal_value * cycleDuration

    debugValues(cycle, model=MODEL, term=term_id,
                liveweightPerHead=liveweightPerHead,
                NEa=NEa)

    return term_id, NEa


_NEa_BY_GROUPING = {
    'cattleAndBuffalo': _calculate_NEa_cattleAndBuffalo,
    'sheepAndGoat': _calculate_NEa_sheepAndGoat
}


def _calculate_NEa(cycle: dict, animal: dict, system: dict, NEm: float):
    grouping = _get_grouping(animal)
    return _NEa_BY_GROUPING.get(grouping, lambda *args: None)(cycle, animal, system, NEm)


def _calculate_NEl_cattleAndBuffalo(cycle: dict, animal: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')

    milkYieldPractice = get_milkYield_practice(animal)
    milkYield = list_sum(milkYieldPractice.get('value', []))
    fatContent = get_node_property(milkYieldPractice, 'fatContent').get('value', 0)
    animal_value = animal.get('value', 0)
    cycleDuration = cycle.get('cycleDuration', 365)
    NEl = milkYield * (1.47 + (0.4 * fatContent)) * animal_value * cycleDuration

    debugValues(cycle, model=MODEL, term=term_id,
                milkYield=milkYield,
                fatContent=fatContent,
                NEl=NEl)

    return term_id, NEl


def _calculate_NEl_sheepAndGoat(cycle: dict, animal: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')

    milkYieldPractice = get_milkYield_practice(animal)
    milkYield = list_sum(milkYieldPractice.get('value', []))
    EV_milk = safe_parse_float(get_lookup_value(milkYieldPractice.get('term', {}), 'mjKgEvMilkIpcc2019'), 0)
    fatContent = get_node_property(milkYieldPractice, 'fatContent').get('value', 0)
    animal_value = animal.get('value', 0)
    cycleDuration = cycle.get('cycleDuration', 365)
    NEl = milkYield * (EV_milk * fatContent/7) * animal_value * cycleDuration

    debugValues(cycle, model=MODEL, term=term_id,
                milkYield=milkYield,
                EV_milk=EV_milk,
                NEl=NEl)

    return term_id, NEl


_NEl_BY_GROUPING = {
    'cattleAndBuffalo': _calculate_NEl_cattleAndBuffalo,
    'sheepAndGoat': _calculate_NEl_sheepAndGoat
}


def _calculate_NEl(cycle: dict, animal: dict):
    grouping = _get_grouping(animal)
    return _NEl_BY_GROUPING.get(grouping, lambda *args: None)(cycle, animal)


def _calculate_NEwork(cycle: dict, animal: dict, NEm: float):
    term = animal.get('term', {})
    term_id = term.get('@id')

    hoursWorkedPerDay = get_node_property(animal, 'hoursWorkedPerDay').get('value', 0)
    NEwork = 0.1 * NEm * hoursWorkedPerDay

    debugValues(cycle, model=MODEL, term=term_id,
                hoursWorkedPerDay=hoursWorkedPerDay,
                NEwork=NEwork)

    return term_id, NEwork


def _get_pregnancy_ratio_per_birth(animal: dict, value: str):
    animalsPerBirth = get_node_property(animal, 'animalsPerBirth').get('value', 3)
    single = safe_parse_float(extract_grouped_data(value, 'singleBirth'), 0)
    double = safe_parse_float(extract_grouped_data(value, 'doubleBirth'), 0)
    tripple = safe_parse_float(extract_grouped_data(value, 'tripleBirthOrMore'))
    return (
        single if animalsPerBirth <= 1 else
        ((animalsPerBirth-1)/2)*single * (1-((animalsPerBirth-1)/2)*double) if 1 < animalsPerBirth < 2 else
        double if animalsPerBirth == 2 else
        ((animalsPerBirth-2)/3)*double * (1-((animalsPerBirth-2)/3)*tripple) if 2 < animalsPerBirth < 3 else
        tripple
    )


def _get_pregnancy_ratio(animal: dict):
    term = animal.get('term', {})
    value = get_lookup_value(term, 'ratioCPregnancyNetEnergyPregnancyIpcc2019')
    return _get_pregnancy_ratio_per_birth(animal, value) if ';' in value else safe_parse_float(value, 0)


def _calculate_NEp(cycle: dict, animal: dict, NEm: float):
    term = animal.get('term', {})
    term_id = term.get('@id')

    ratioCPregnancyNetEnergyPregnancy = _get_pregnancy_ratio(animal)
    pregnancyRateTotal = get_node_property(animal, 'pregnancyRateTotal').get('value', 0)
    NEp = ratioCPregnancyNetEnergyPregnancy * pregnancyRateTotal/100 * NEm

    debugValues(cycle, model=MODEL, term=term_id,
                ratioCPregnancyNetEnergyPregnancy=ratioCPregnancyNetEnergyPregnancy,
                pregnancyRateTotal=pregnancyRateTotal,
                NEp=NEp)

    return term_id, NEp


def _calculate_NEg_cattleAndBuffalo(cycle: dict, animal: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')

    ratioCNetEnergyGrowthCattleBuffalo = safe_parse_float(
        get_lookup_value(term, 'ratioCNetEnergyGrowthCattleBuffaloIpcc2019'), 0
    )
    liveweightPerHead = get_node_property(animal, 'liveweightPerHead').get('value', 0)
    weightAtMaturity = get_node_property(animal, 'weightAtMaturity').get('value', 0)
    liveweightGain = get_node_property(animal, 'liveweightGain').get('value', 0)
    animal_value = animal.get('value', 0)
    cycleDuration = cycle.get('cycleDuration', 365)
    NEg = 22.02 * \
        pow(liveweightPerHead / (ratioCNetEnergyGrowthCattleBuffalo * weightAtMaturity), 0.75) * \
        pow(liveweightGain, 1.097) * \
        animal_value * cycleDuration if all([
            ratioCNetEnergyGrowthCattleBuffalo * weightAtMaturity > 0
        ]) else 0

    debugValues(cycle, model=MODEL, term=term_id,
                ratioCNetEnergyGrowthCattleBuffalo=ratioCNetEnergyGrowthCattleBuffalo,
                liveweightPerHead=liveweightPerHead,
                weightAtMaturity=weightAtMaturity,
                liveweightGain=liveweightGain,
                NEg=NEg)

    return term_id, NEg


def _calculate_NEg_sheepAndGoat(cycle: dict, animal: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')

    MjKgABNetEnergyGrowthSheepGoats = get_lookup_value(term, 'MjKgABNetEnergyGrowthSheepGoatsIpcc2019')
    MjKg_a = safe_parse_float(extract_grouped_data(MjKgABNetEnergyGrowthSheepGoats, 'a'), 0)
    MjKg_b = safe_parse_float(extract_grouped_data(MjKgABNetEnergyGrowthSheepGoats, 'b'), 0)
    BWi = get_node_property(animal, 'weightAtWeaning').get('value', 0)
    BWf = get_node_property(animal, 'weightAtOneYear').get('value', 0) or \
        get_node_property(animal, 'weightAtSlaughter').get('value', 0)
    animal_value = animal.get('value', 0)
    cycleDuration = cycle.get('cycleDuration', 365)
    NEg = (BWf - BWi) * (MjKg_a + 0.5 * MjKg_b * (BWi + BWf)) / 365 * animal_value * cycleDuration

    debugValues(cycle, model=MODEL, term=term_id,
                MjKg_a=MjKg_a,
                MjKg_b=MjKg_b,
                BWi=BWi,
                BWf=BWf,
                NEg=NEg)

    return term_id, NEg


_NEg_BY_GROUPING = {
    'cattleAndBuffalo': _calculate_NEg_cattleAndBuffalo,
    'sheepAndGoat': _calculate_NEg_sheepAndGoat
}


def _calculate_NEg(cycle: dict, animal: dict):
    grouping = _get_grouping(animal)
    return _NEg_BY_GROUPING.get(grouping, lambda *args: None)(cycle, animal)


def _calculate_NEwool(cycle: dict):
    terms = get_wool_terms()
    products = [p for p in cycle.get('products', []) if p.get('term', {}).get('@id') in terms]
    product_values = [
        (
            list_sum(p.get('value', [])),
            safe_parse_float(get_lookup_value(p.get('term', {}), LOOKUPS['animalProduct']), 24)
        ) for p in products
    ]

    return sum([value * lookup_value for (value, lookup_value) in product_values])


def _pastureGrass_key_property_value(practice: dict, column: dict):
    term_id = _practice_input_id(practice)
    term = download_hestia(term_id)
    term_type = term.get('termType')
    value = list_sum(practice.get('value', [0]))
    lookup_value = _node_property_value(MODEL, {'@id': term_id, 'termType': term_type}, column)
    return (lookup_value, value)


def _calculate_meanDE(practices: list):
    values = list(map(lambda p: _pastureGrass_key_property_value(p, 'energyDigestibilityRuminants'), practices))
    total_weight = sum([weight/100 for _value, weight in values])
    meanDE = sum([
        value * weight/100 for value, weight in values
    ]) / total_weight if total_weight > 0 else 0

    return meanDE


def _calculate_REM(meanDE: float):
    return 1.123 - (4.092/1000 * meanDE) + (1.126/100000 * pow(meanDE, 2)) - (25.4/meanDE) if meanDE > 0 else 0


def _calculate_REG(meanDE: float):
    return 1.164 - (5.16/1000 * meanDE) + (1.308/100000 * pow(meanDE, 2)) - (37.4/meanDE) if meanDE > 0 else 0


def _calculate_feed_meanDE(cycle: dict, input: dict):
    term_id = input.get('term', {}).get('@id')

    energyContent = get_node_property_value(MODEL, input, 'energyContentHigherHeatingValue')
    energyDigestibility = get_node_property_value(MODEL, input, 'energyDigestibilityRuminants')
    meanDE = energyContent * (energyDigestibility/100)

    debugValues(cycle, model=MODEL, term=term_id,
                energyContent=energyContent,
                energyDigestibility=energyDigestibility,
                meanDE=meanDE)

    return meanDE


def _calculate_NEfeed_m(cycle: dict, input: dict, meanDE: float):
    term_id = input.get('term', {}).get('@id')

    energyDigestibility = get_node_property_value(MODEL, input, 'energyDigestibilityRuminants')
    REm = _calculate_REM(energyDigestibility)

    debugValues(cycle, model=MODEL, term=term_id,
                REm=REm)

    input_value = list_sum(input.get('value'))
    return meanDE * REm * input_value


def _calculate_NEfeed_g(cycle: dict, input: dict, meanDE: float):
    term_id = input.get('term', {}).get('@id')

    energyDigestibility = get_node_property_value(MODEL, input, 'energyDigestibilityRuminants')
    REg = _calculate_REG(energyDigestibility)

    debugValues(cycle, model=MODEL, term=term_id,
                REg=REg)

    input_value = list_sum(input.get('value'))
    return meanDE * REg * input_value


def _calculate_NEfeed(cycle: dict):
    inputs = get_feed_inputs(cycle)
    # calculate meanDE for each input first
    inputs = [(input, _calculate_feed_meanDE(cycle, input)) for input in inputs]
    NEfeed_m = sum([
        _calculate_NEfeed_m(cycle, input, meanDE) for (input, meanDE) in inputs
    ]) if len(inputs) > 0 else 0
    NEfeed_g = sum([
        _calculate_NEfeed_g(cycle, input, meanDE) for (input, meanDE) in inputs
    ]) if len(inputs) > 0 else 0

    return (NEfeed_m, NEfeed_g)


def _group_logs(values: list): return ';'.join([f"id:{term_id}_value:{value}" for term_id, value in values if term_id])


def _sum_values(values): return sum([value for term_id, value in values])


def _calculate_GE(cycle: dict, meanDE: float, system: dict):
    animals = [
        a for a in cycle.get('animals', []) if all([
            a.get('value') and a.get('referencePeriod') == AnimalReferencePeriod.AVERAGE.value
        ])
    ]

    # calculate NEm first and re-use in other places
    animals = [(animal, _calculate_NEm(cycle, animal)) for animal in animals]

    NEm = sum(non_empty_list([NEm for (animal, NEm) in animals]))

    NEa = non_empty_list([_calculate_NEa(cycle, animal, system, NEm) for (animal, NEm) in animals])
    NEl = non_empty_list([_calculate_NEl(cycle, animal) for (animal, _NEm) in animals])
    NEwork = non_empty_list([_calculate_NEwork(cycle, animal, NEm) for (animal, NEm) in animals])
    NEp = non_empty_list([_calculate_NEp(cycle, animal, NEm) for (animal, NEm) in animals])
    NEg = non_empty_list([_calculate_NEg(cycle, animal) for (animal, _NEm) in animals])

    NEwool = _calculate_NEwool(cycle)
    REM = _calculate_REM(meanDE) if meanDE > 0 else None
    REG = _calculate_REG(meanDE) if meanDE > 0 else None

    NEfeed_m, NEfeed_g = _calculate_NEfeed(cycle)

    logRequirements(cycle, model=MODEL, term=MODEL_KEY,
                    NEm=_group_logs([(animal.get('term', {}).get('@id'), NEm) for (animal, NEm) in animals]),
                    NEa=_group_logs(NEa),
                    NEl=_group_logs(NEl),
                    NEwork=_group_logs(NEwork),
                    NEp=_group_logs(NEp),
                    NEg=_group_logs(NEg),
                    NEwool=NEwool,
                    REM=REM,
                    REG=REG,
                    NEfeed_m=NEfeed_m,
                    NEfeed_g=NEfeed_g)

    return (
        (NEm + _sum_values(NEa) + _sum_values(NEl) + _sum_values(NEwork) + _sum_values(NEp) - NEfeed_m)/REM +
        (_sum_values(NEg) + NEwool - NEfeed_g)/REG
    ) / (meanDE/100) if all([REM, REG]) else 0


def _calculate_meanECHHV(practices: list):
    values = list(map(lambda p: _pastureGrass_key_property_value(p, 'energyContentHigherHeatingValue'), practices))
    total_weight = sum([weight/100 for _value, weight in values])
    return sum([
        value * weight/100 for value, weight in values
    ]) / total_weight if total_weight > 0 else 0


def _run_practice(cycle: dict, GE: float, meanECHHV: float):
    def run(practice: dict):
        key = practice.get('key', {})
        key_id = key.get('@id')
        input_term_id = _practice_input_id(practice)
        value = (GE / meanECHHV) * (list_sum(practice.get('value', [0])) / 100)

        logRequirements(cycle, model=MODEL, term=input_term_id,
                        GE=GE,
                        meanECHHV=meanECHHV,
                        key_id=key_id)

        logShouldRun(cycle, MODEL, input_term_id, True)

        return _input(input_term_id, value)

    return run


def _should_run_practice(cycle: dict):
    def should_run(practice: dict):
        term_id = practice.get('term', {}).get('@id')
        key_term_type = practice.get('key', {}).get('termType')
        value = practice.get('value', [])

        logRequirements(cycle, model=MODEL, term=term_id,
                        practice_value=list_sum(value),
                        practice_key_term_type=key_term_type)

        should_run = all([len(value) > 0, term_id == MODEL_KEY, key_term_type in KEY_TERM_TYPES])
        logShouldRun(cycle, MODEL, term_id, should_run)
        return should_run

    return should_run


def _should_run(cycle: dict, practices: dict):
    systems = filter_list_term_type(cycle.get('practices', []), TermTermType.SYSTEM)
    animalFeed_incomplete = _is_term_type_incomplete(cycle, {'termType': 'animalFeed'})
    all_animals_have_value = all([a.get('value', 0) > 0 for a in cycle.get('animals', [])])

    meanDE = _calculate_meanDE(practices)
    meanECHHV = _calculate_meanECHHV(practices)
    GE = _calculate_GE(cycle, meanDE, systems[0]) if all([meanDE > 0, len(systems) > 0]) else 0

    should_run = all([
        animalFeed_incomplete, all_animals_have_value, len(systems) > 0, len(practices) > 0, GE > 0, meanECHHV > 0
    ])

    for term_id in [MODEL_KEY] + [_practice_input_id(p) for p in practices]:
        logRequirements(cycle, model=MODEL, term=term_id,
                        term_type_animalFeed_incomplete=animalFeed_incomplete,
                        all_animals_have_value=all_animals_have_value,
                        meanDE=meanDE,
                        meanECHHV=meanECHHV,
                        GE=GE)

        logShouldRun(cycle, MODEL, term_id, should_run)

    return should_run, GE, meanECHHV


def run(cycle: dict):
    practices = list(filter(_should_run_practice(cycle), cycle.get('practices', [])))
    should_run, GE, meanECHHV = _should_run(cycle, practices)
    return list(map(_run_practice(cycle, GE, meanECHHV), practices)) if should_run else []
