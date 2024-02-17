from hestia_earth.schema import SchemaType, SiteSiteType, TermTermType
from hestia_earth.utils.api import download_hestia, find_related
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import non_empty_list, safe_parse_date

from hestia_earth.models.log import debugMissingLookup
from . import cached_value

CACHE_YEARS_KEY = 'years'
WATER_TYPES = [
    SiteSiteType.POND.value,
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value,
    SiteSiteType.SEA_OR_OCEAN.value
]
FRESH_WATER_TYPES = [
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value
]


def region_level_1_id(term_id: str):
    """
    Get the level 1 `@id` of the region.

    Parameters
    ----------
    term_id : str
        The `@id` of the region Term

    Returns
    -------
    str
        The `@id` of the `region` with a maximum level of 1.
    """
    term_parts = term_id.split('.') if term_id else []
    return None if term_id is None or not term_id.startswith('GADM') else (
        term_id if len(term_id) == 8 else (
            f"{'.'.join(term_parts[0:2])}{('_' + term_id.split('_')[1]) if len(term_parts) > 2 else ''}"
        )
    )


def is_site(site: dict): return site.get('@type', site.get('type')) == SchemaType.SITE.value


def related_cycles(site_id: str):
    """
    Get the list of `Cycle` related to the `Site`.

    In Hestia, a `Cycle` must have a link to a `Site`, therefore a `Site` can be related to many `Cycle`s.

    Parameters
    ----------
    site_id : str
        The `@id` of the `Site`.

    Returns
    -------
    list[dict]
        The related `Cycle`s as `dict`.
    """
    nodes = find_related(SchemaType.SITE, site_id, SchemaType.CYCLE)
    return list(map(lambda node: download_hestia(node.get('@id'), SchemaType.CYCLE), nodes or []))


def _cycle_end_year(cycle: dict):
    date = safe_parse_date(cycle.get('endDate'))
    return date.year if date else None


def related_years(site: dict):
    return cached_value(site, CACHE_YEARS_KEY) or (
        non_empty_list(set(map(_cycle_end_year, related_cycles(site.get('@id')))))
    )


def valid_site_type(site: dict, site_types=[SiteSiteType.CROPLAND.value, SiteSiteType.PERMANENT_PASTURE.value]):
    """
    Check if the site `siteType` is allowed.

    Parameters
    ----------
    site : dict
        The `Site`.
    site_types : list[string]
        List of valid site types. Defaults to `['cropland', 'permanent pasture']`.
        Full list available on https://hestia.earth/schema/Site#siteType.

    Returns
    -------
    bool
        `True` if `siteType` matches the allowed values, `False` otherwise.
    """
    site_type = site.get('siteType') if site is not None else None
    return site_type in site_types


def region_factor(model: str, region_id: str, term_id: str, termType: TermTermType):
    lookup_name = f"region-{termType.value}.csv"
    value = get_table_value(download_lookup(lookup_name), 'termid', region_id, column_name(term_id))
    debugMissingLookup(lookup_name, 'termid', region_id, term_id, value, model=model, term=term_id)
    return value
