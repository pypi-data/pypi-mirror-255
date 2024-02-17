"""
Pre Checks Cache Geospatial Database

This model caches results from Geospatial Database.
"""
from functools import reduce
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils import CACHE_KEY, cached_value
from hestia_earth.models.utils.site import CACHE_YEARS_KEY
from hestia_earth.models.geospatialDatabase.utils import (
    MAX_AREA_SIZE, CACHE_VALUE, CACHE_AREA_SIZE,
    has_geospatial_data, has_coordinates, get_area_size, geospatial_data, _run_query, _collection_name
)
from hestia_earth.models.geospatialDatabase import list_ee_params

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ]
    }
}
RETURNS = {
    "Site": {}
}


def cache_site_results(results: list, collections: list, area_size: int = None):
    def _combine_result(group: dict, index: int):
        collection = collections[index]
        name = collection.get('name')
        value = results[index]
        data = (group.get(name, {}) | {collection.get('year'): value}) if 'year' in collection else value
        return group | {name: data}

    return reduce(_combine_result, range(0, len(results)), {}) | (
        {CACHE_AREA_SIZE: area_size} if area_size is not None else {}
    )


def _extend_collection(name: str, collection: dict, years: list = []):
    data = collection | {'name': name, 'collection': _collection_name(collection.get('collection'))}
    return [
        data | {
            'year': str(year)
        } for year in years
    ] if 'reducer_annual' in collection and 'reducer_period' not in collection else [data]


def _extend_collections(values: list, years: list = []):
    return flatten([
        _extend_collection(value.get('name'), value.get('params'), years) for value in values
    ])


def list_collections(years: list, include_region: bool = False):
    ee_params = list_ee_params()
    # only cache `raster` results as can be combined in a single query
    rasters = [value for value in ee_params if value.get('params').get('ee_type') == 'raster']

    vectors = [
        value for value in ee_params if all([
            value.get('params').get('ee_type') == 'vector',
            include_region or not value.get('params').get('collection', '').startswith('gadm36')
        ])
    ]

    return (_extend_collections(rasters, years), _extend_collections(vectors))


def _cache_results(site: dict, area_size: float):
    # to fetch data related to the year
    years = cached_value(site, key=CACHE_YEARS_KEY, default=[])
    include_region = all([has_coordinates(site), not site.get('region')])
    rasters, vectors = list_collections(years, include_region=include_region)

    raster_results = _run_query({
        'ee_type': 'raster',
        'collections': rasters,
        **geospatial_data(site)
    })

    vector_results = _run_query({
        'ee_type': 'vector',
        'collections': vectors,
        **geospatial_data(site)
    })

    return cache_site_results(raster_results + vector_results, rasters + vectors, area_size)


def _should_run(site: dict, area_size: float = None):
    area_size = area_size or get_area_size(site)
    contains_geospatial_data = has_geospatial_data(site)
    contains_coordinates = has_coordinates(site)
    has_cache = cached_value(site, CACHE_VALUE) is not None

    debugValues(site,
                area_size=area_size,
                MAX_AREA_SIZE=MAX_AREA_SIZE,
                contains_geospatial_data=contains_geospatial_data,
                has_cache=has_cache)

    should_run = all([
        not has_cache,
        contains_coordinates or (area_size is not None and area_size <= MAX_AREA_SIZE),
        contains_geospatial_data
    ])
    return should_run, area_size


def run(site: dict):
    should_run, area_size = _should_run(site)
    return {
        **site,
        CACHE_KEY: {**cached_value(site), CACHE_VALUE: _cache_results(site, area_size)}
    } if should_run else site
