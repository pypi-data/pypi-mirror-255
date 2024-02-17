"""
Input Hestia Aggregated Data

This model adds `impactAssessment` to `Input` based on data which has been aggregated into country level averages.
Note: to get more accurate impacts, we recommend setting the
[input.impactAssessment](https://hestia.earth/schema/Input#impactAssessment)
instead of the region-level averages using this model.
"""
import math
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import search
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.model import find_primary_product, find_term_match, linked_node
from hestia_earth.utils.tools import safe_parse_date, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import is_organic, valid_site_type
from hestia_earth.models.utils.term import get_generic_crop

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "value": "",
            "none": {
                "impactAssessment": "",
                "fromCycle": "True"
            },
            "optional": {
                "country": {"@type": "Term", "termType": "region"},
                "region": {"@type": "Term", "termType": "region"}
            }
        }],
        "optional": {
            "site": {
                "@type": "Site",
                "siteType": ["cropland", "pasture"],
                "country": {"@type": "Term", "termType": "region"}
            },
            "inputs": [{
                "@type": "Input",
                "term.@id": "seed",
                "value": "",
                "none": {
                    "impactAssessment": ""
                }
            }],
            "products": [{"@type": "Product", "value": "", "primary": "True"}]
        }
    }
}
RETURNS = {
    "Input": [{
        "impactAssessment": "added from Hestia",
        "impactAssessmentIsProxy": "True"
    }]
}
MODEL_ID = 'hestiaAggregatedData'
MODEL_KEY = 'impactAssessment'
SEED_TERM_ID = 'seed'
MATCH_WORLD_QUERY = {'match': {'country.name.keyword': {'query': 'World', 'boost': 1}}}


def _end_date(end_date: str):
    year = safe_parse_date(end_date).year
    return round(math.floor(year / 10) * 10) + 9


def _match_region_country(region: dict, country: dict):
    region_name = region.get('name') if region else None
    country_name = country.get('name') if country else None
    return {
        'bool': {
            # either get with exact country, or default to global
            'should': non_empty_list([
                (
                    {'match': {'region.name.keyword': {'query': region_name, 'boost': 1000}}} if region_name else
                    {'match': {'country.name.keyword': {'query': country_name, 'boost': 1000}}} if country_name else
                    None
                ),
                MATCH_WORLD_QUERY
            ]),
            'minimum_should_match': 1
        }
    }


def _find_closest_impact(cycle: dict, end_date: str, input: dict, region: dict, country: dict, must_queries=[]):
    term = input.get('term', {})
    query = {
        'bool': {
            'must': non_empty_list([
                {'match': {'@type': SchemaType.IMPACTASSESSMENT.value}},
                {'match': {'aggregated': 'true'}},
                {
                    'bool': {
                        # handle old ImpactAssessment data
                        'should': [
                            {'match': {'product.term.name.keyword': term.get('name')}},
                            {'match': {'product.name.keyword': term.get('name')}}
                        ],
                        'minimum_should_match': 1
                    }
                } if term else None,
                _match_region_country(region, country)
            ]) + must_queries,
            'should': [
                # if the Cycle is organic, we can try to match organic aggregate first
                {'match': {'name': {'query': 'Organic' if is_organic(cycle) else 'Conventional', 'boost': 1000}}},
                {'match': {'endDate': {'query': end_date, 'boost': 1000}}}
            ]
        }
    }
    results = search(query, fields=['@type', '@id', 'name', 'endDate']) if term else []
    # sort by distance to date and score and take min
    results = sorted(
        results,
        key=lambda v: abs(int(end_date) - int(v.get('endDate', '0'))) * v.get('_score', 0),
    )
    return results[0] if len(results) > 0 else None


def _run_seed(cycle: dict, primary_product: dict, seed_input: dict, end_date: str):
    region = seed_input.get('region')
    country = seed_input.get('country')
    # to avoid double counting seed => aggregated impact => seed, we need to get the impact of the previous decade
    # if the data does not exist, use the aggregated impact of generic crop instead
    date = _end_date(end_date)
    impact = _find_closest_impact(cycle, date, primary_product, region, country, [
        {'match': {'endDate': date - 10}}
    ]) or _find_closest_impact(cycle, date, {'term': get_generic_crop()}, region, country)

    debugValues(cycle, model=MODEL_ID, term=SEED_TERM_ID, key=MODEL_KEY,
                input_region=(region or {}).get('@id'),
                input_country=(country or {}).get('@id'),
                date=date,
                impact=(impact or {}).get('@id'))

    return [{**seed_input, MODEL_KEY: linked_node(impact), 'impactAssessmentIsProxy': True}] if impact else []


def _should_run_seed(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    product_id = primary_product.get('term', {}).get('@id')
    term_type = primary_product.get('term', {}).get('termType')
    is_crop_product = term_type == TermTermType.CROP.value
    input = find_term_match(cycle.get('inputs', []), SEED_TERM_ID, None)
    has_input = input is not None
    site_type_valid = valid_site_type(cycle, True)

    should_run = all([site_type_valid, is_crop_product, has_input])

    # ignore logs if seed is not present
    if has_input:
        debugValues(cycle, model=MODEL_ID, term=SEED_TERM_ID, key=MODEL_KEY,
                    primary_product_id=product_id,
                    primary_product_term_type=term_type)

        logRequirements(cycle, model=MODEL_ID, term=SEED_TERM_ID, key=MODEL_KEY,
                        site_type_valid=site_type_valid,
                        is_crop_product=is_crop_product,
                        has_input=has_input)

        logShouldRun(cycle, MODEL_ID, SEED_TERM_ID, should_run)
        logShouldRun(cycle, MODEL_ID, SEED_TERM_ID, should_run, key=MODEL_KEY)  # show specifically under Input

    return should_run, primary_product, input


def _run_input(cycle: dict, date: int):
    def run(input: dict):
        term_id = input.get('term', {}).get('@id')
        region = input.get('region')
        country = input.get('country')
        impact = _find_closest_impact(cycle, date, input, region, country)

        debugValues(cycle, model=MODEL_ID, term=term_id, key=MODEL_KEY,
                    input_region=(region or {}).get('@id'),
                    input_country=(country or {}).get('@id'),
                    impact=(impact or {}).get('@id'))

        should_run = all([impact is not None])
        logShouldRun(cycle, MODEL_ID, term_id, should_run)
        logShouldRun(cycle, MODEL_ID, term_id, should_run, key=MODEL_KEY)  # show specifically under Input

        return {**input, MODEL_KEY: linked_node(impact), 'impactAssessmentIsProxy': True} if impact else None
    return run


def _run(cycle: dict, inputs: list, end_date: str):
    date = _end_date(end_date)
    return non_empty_list(map(_run_input(cycle, date), inputs))


def _should_aggregate_input(term: dict):
    lookup = download_lookup(f"{term.get('termType')}.csv", True)
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('skipAggregation'))
    return True if value is None or value == '' else not value


def _should_run_input(products: list):
    def should_run(input: dict):
        term = input.get('term', {})
        return all([
            not input.get(MODEL_KEY),
            _should_aggregate_input(term),
            # make sure Input is not a Product as well or we might double-count emissions
            find_term_match(products, term.get('@id'), None) is None,
            # ignore inputs which are flagged as Product of the Cycle
            not input.get('fromCycle', False)
        ])
    return should_run


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    inputs = list(filter(_should_run_input(cycle.get('products', [])), cycle.get('inputs', [])))

    logRequirements(cycle, model=MODEL_ID, key=MODEL_KEY,
                    end_date=end_date,
                    nb_inputs=len(inputs))

    should_run = all([end_date, len(inputs) > 0])
    logShouldRun(cycle, MODEL_ID, None, should_run, key=MODEL_KEY)
    return should_run, inputs, end_date


def run(cycle: dict):
    should_run, inputs, end_date = _should_run(cycle)
    should_run_seed, primary_product, seed_input = _should_run_seed(cycle)
    return (
        _run(cycle, inputs, end_date) if should_run else []
    ) + (
        _run_seed(cycle, primary_product, seed_input, end_date) if should_run_seed else []
    )
