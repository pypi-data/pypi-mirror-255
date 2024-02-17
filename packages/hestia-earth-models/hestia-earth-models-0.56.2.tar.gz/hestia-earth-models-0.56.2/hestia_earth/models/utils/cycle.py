from hestia_earth.schema import CycleFunctionalUnit, SiteSiteType, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match, find_primary_product
from hestia_earth.utils.tools import list_sum, safe_parse_float, safe_parse_date

from ..log import logRequirements, debugValues
from .lookup import factor_value
from .term import get_lookup_value
from .property import get_node_property
from .product import (
    abg_residue_on_field_nitrogen_content, blg_residue_nitrogen, discarded_residue_on_field_nitrogen_content
)
from .completeness import _is_term_type_complete
from .blank_node import get_N_total, get_P2O5_total, get_total_value_converted
from .measurement import most_relevant_measurement_value
from .site import valid_site_type as site_valid_site_type
from .crop import is_plantation
from .currency import DEFAULT_CURRENCY


def unique_currencies(cycle: dict) -> list:
    """
    Get the list of different currencies used in the Cycle.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    list
        The list of currencies as string.
    """
    products = cycle.get('products', [])
    return list(set([p.get('currency') for p in products if p.get('currency') is not None]))


def default_currency(cycle: dict) -> str:
    """
    Get the default currency for the Cycle.
    If multiple curriencies are used, will default to `USD`.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    str
        The default currency.
    """
    currencies = unique_currencies(cycle)
    return currencies[0] if len(currencies) == 1 else DEFAULT_CURRENCY


def get_crop_residue_on_field_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content from the `cropResidue` left on the field.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    products = cycle.get('products', [])
    total = sum([
        abg_residue_on_field_nitrogen_content(products),
        blg_residue_nitrogen(products),
        discarded_residue_on_field_nitrogen_content(products)
    ])
    return total if _is_term_type_complete(cycle, {'termType': TermTermType.CROPRESIDUE.value}) else 0


CROP_RESIDUE_DECOMPOSITION_PRODUCT_IDS = [
    'discardedCropLeftOnField',
    'discardedCropIncorporated',
    'aboveGroundCropResidueLeftOnField',
    'aboveGroundCropResidueIncorporated',
    'belowGroundCropResidue'
]


def get_crop_residue_decomposition_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of `cropResidue` decomposed.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    products = [
        p for p in cycle.get('products', []) if p.get('term', {}).get('@id') in CROP_RESIDUE_DECOMPOSITION_PRODUCT_IDS
    ]
    return list_sum(get_total_value_converted(products, 'nitrogenContent'))


def get_excreta_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of excreta used in the Cycle.

    The result is the sum of every excreta specified in `kg N` as an `Input` or a `Product`.

    Note: in the event where `completeness.product` is set to `True` and there are no excreta inputs or products,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.EXCRETA)
    products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    values = get_N_total(inputs) + get_N_total(products)
    return 0 if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'product'}) else list_sum(values)


def get_organic_fertiliser_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of organic fertilisers used in the Cycle.

    The result contains the values of the following `Input`s:
    1. Every organic fertiliser specified in `kg N` will be used.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `nitrogenContent` of that fertiliser.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no organic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.ORGANICFERTILISER)
    values = get_N_total(inputs)
    return 0 if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'fertiliser'}) else list_sum(values)


def get_organic_fertiliser_P_total(cycle: dict) -> float:
    """
    Get the total phosphate content of organic fertilisers used in the Cycle.

    The result contains the values of the following `Input`s:
    1. Every organic fertiliser specified in `kg P2O5` will be used.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `nitrogenContent` of that fertiliser.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no organic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.ORGANICFERTILISER)
    values = get_P2O5_total(inputs)
    return 0 if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'fertiliser'}) else list_sum(values)


def get_inorganic_fertiliser_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of inorganic fertilisers used in the Cycle.

    The result is the sum of every inorganic fertiliser specified in `kg N` as an `Input`.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no inorganic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.INORGANICFERTILISER)
    values = get_N_total(inputs)
    return 0 if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'fertiliser'}) else list_sum(values)


def get_inorganic_fertiliser_P_total(cycle: dict) -> float:
    """
    Get the total Phosphate content of inorganic fertilisers used in the Cycle.

    The result is the sum of every inorganic fertiliser specified in `kg P2O5` as an `Input`.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no inorganic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.INORGANICFERTILISER)
    values = get_P2O5_total(inputs)
    return 0 if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'fertiliser'}) else list_sum(values)


def get_max_rooting_depth(cycle: dict) -> float:
    properties = list(map(lambda p: get_node_property(p, 'rootingDepth'), cycle.get('products', [])))
    values = [safe_parse_float(p.get('value')) for p in properties if p.get('value') is not None]
    return max(values) if len(values) > 0 else None


def _land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 365)
    longFallowRatio = find_term_match(cycle.get('practices', []), 'longFallowRatio')
    longFallowRatio = longFallowRatio.get('value', [None])[0]
    value = cycleDuration / 365 * longFallowRatio if longFallowRatio is not None else None

    logRequirements(cycle, model=model, term=term_id,
                    cycleDuration=cycleDuration,
                    longFallowRatio=longFallowRatio,
                    value_per_ha=value)

    return value


def _plantation_land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    practices = cycle.get('practices', [])
    nurseryDuration = list_sum(find_term_match(practices, 'nurseryDuration').get('value', []), None)
    plantationProductiveLifespan = list_sum(
        find_term_match(practices, 'plantationProductiveLifespan').get('value', []), None)
    plantationDensity = list_sum(find_term_match(practices, 'plantationDensity').get('value', []), None)
    plantationLifespan = list_sum(find_term_match(practices, 'plantationLifespan').get('value', []), None)
    rotationDuration = list_sum(find_term_match(practices, 'rotationDuration').get('value', []), None)
    nurseryDensity = list_sum(find_term_match(practices, 'nurseryDensity').get('value', []), None)

    logRequirements(cycle, model=model, term=term_id,
                    nurseryDuration=nurseryDuration,
                    nurseryDensity=nurseryDensity,
                    plantationDensity=plantationDensity,
                    plantationLifespan=plantationLifespan,
                    plantationProductiveLifespan=plantationProductiveLifespan,
                    rotationDuration=rotationDuration)

    should_run = all([
        nurseryDuration, nurseryDensity,
        plantationDensity, plantationLifespan, plantationProductiveLifespan,
        rotationDuration
    ])
    return (plantationLifespan/plantationProductiveLifespan) * (
        1 + (nurseryDuration/365)/nurseryDensity * plantationDensity/(plantationLifespan/365)  # nursery
    ) * rotationDuration/plantationLifespan if should_run else None


def land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    """
    Get the land occupation of the cycle per hectare in hectare.

    Parameters
    ----------
    model : str
        The name of the model running this function. For debugging purpose only.
    term_id : str
        The name of the term running this function. For debugging purpose only.
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The land occupation in hectare.
    """
    product = find_primary_product(cycle) or {}
    plantation = is_plantation(model, term_id, product.get('term', {}).get('@id'))
    return _plantation_land_occupation_per_ha(model, term_id, cycle) if plantation \
        else _land_occupation_per_ha(model, term_id, cycle)


def _land_occupation_per_kg(model: str, term_id: str, cycle: dict, product: dict, land_occupation_per_ha: float):
    functionalUnit = cycle.get('functionalUnit')
    product_value = list_sum(product.get('value', [0]))
    economicValueShare = product.get('economicValueShare', 0)

    value = land_occupation_per_ha * 10000 * (economicValueShare / 100)
    value = value / product_value if all([product_value > 0, economicValueShare > 0]) else None
    value = value if functionalUnit == CycleFunctionalUnit._1_HA.value else None

    logRequirements(cycle, model=model, term=term_id,
                    functionalUnit=functionalUnit,
                    product_yield=product_value,
                    economicValueShare=economicValueShare,
                    value_per_kg_per_m2=value)

    return value


def land_occupation_per_kg(model: str, term_id: str, cycle: dict, site: dict, primary_product: dict):
    """
    Get the land occupation of the cycle per kg in meter square.

    Parameters
    ----------
    model : str
        The name of the model running this function. For debugging purpose only.
    term_id : str
        The name of the term running this function. For debugging purpose only.
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.
    site : dict
        The `Site` as defined in the Hestia Schema.
    primary_product : dict
        The primary `Product` of the `Cycle`.

    Returns
    -------
    float
        The land occupation in m2.
    """
    site_type = site.get('siteType')
    value = land_occupation_per_ha(model, term_id, cycle)
    return 0 if site_type in [
        # assume the land occupation is 0 for these sites
        SiteSiteType.AGRI_FOOD_PROCESSOR.value,
        SiteSiteType.ANIMAL_HOUSING.value,
        SiteSiteType.FOOD_RETAILER.value,
        SiteSiteType.LAKE.value,
        SiteSiteType.POND.value,
        SiteSiteType.RIVER_OR_STREAM.value,
        SiteSiteType.SEA_OR_OCEAN.value
    ] else (
        _land_occupation_per_kg(model, term_id, cycle, primary_product, value) if value is not None else None
    )


def valid_site_type(cycle: dict, include_permanent_pasture=False):
    """
    Check if the `site.siteType` of the cycle is `cropland`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.
    include_permanent_pasture : bool
        If set to `True`, `permanent pasture` is also allowed. Defaults to `False`.

    Returns
    -------
    bool
        `True` if `siteType` matches the allowed values, `False` otherwise.
    """
    site_types = [SiteSiteType.CROPLAND.value] + (
        [SiteSiteType.PERMANENT_PASTURE.value] if include_permanent_pasture else []
    )
    return site_valid_site_type(cycle.get('site', {}), site_types)


def is_organic(cycle: dict):
    """
    Check if the `Cycle` is organic, i.e. if it contains an organic standard label `Practice`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    bool
        `True` if the `Cycle` is organic, `False` otherwise.
    """
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.STANDARDSLABELS)
    return any([get_lookup_value(p.get('term', {}), 'isOrganic') == 'organic' for p in practices])


def is_irrigated(cycle: dict):
    """
    Check if the `Cycle` is irrigated, i.e. if it contains an irrigated `Practice`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    bool
        `True` if the `Cycle` is irrigated, `False` otherwise.
    """
    return list_sum(find_term_match(cycle.get('practices', []), 'irrigated').get('value', [])) > 0


def cycle_end_year(cycle: dict):
    """
    End year of the `Cycle`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    number
        The year in which the `Cycle` ends.
    """
    date = safe_parse_date(cycle.get('endDate'))
    return date.year if date else None


def impact_lookup_value(
    model: str, term_id: str, blank_nodes: list, lookup_col: str, allow_missing: bool = True
) -> float:
    """
    Calculate the value of the impact based on lookup factors and cycle values.

    Parameters
    ----------
    term_id : str
        The term to display in the logs only.
    blank_nodes : list
        The list of blank nodes from the Cycle.
    lookup_col : str
        The lookup column to fetch the factors from.
    allow_missing : bool
        Allow missing factors. Default to `False` (will return `None` if one factor is missing).

    Returns
    -------
    int
        The impact total value.
    """
    term_type = blank_nodes[0].get('term', {}).get('termType') if len(blank_nodes) > 0 else None
    get_factor_value = factor_value(model, term_id, f"{term_type}.csv", lookup_col)
    factors = [(node.get('term', {}).get('@id'), get_factor_value(node)) for node in blank_nodes]
    values = [value for (_term, value) in factors if value is not None]
    missing_values = set([term for (term, value) in factors if value is None])
    all_nodes_have_value = len(values) == len(factors)
    debugValues({'type': 'Cycle'}, model=model, term=term_id,
                missing_lookup_factor=';'.join(missing_values),
                **{f"all_{term_type}_have_lookup_value": all_nodes_have_value})
    return list_sum(values) if len(values) > 0 and (allow_missing or all_nodes_have_value) else None


def get_ecoClimateZone(cycle: dict) -> int:
    """
    Get the `ecoClimateZone` value from the Site Measurements (if present).

    Parameters
    ----------
    cycle : dict
        The full Cycle containing the Site.

    Returns
    -------
    int
        The ecoClimateZone value from 1 to 12.
    """
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    return most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)


def check_cycle_site_ids_identical(cycles: list[dict]) -> bool:
    """
    Checks whether the sites of a list of cycles are the same.

    Parameters
    ----------
    cycles : list[dict]
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    bool
        Whether or not all of the cycles associated site ids are identical.
    """
    return len(set(cycle.get('site', {}).get('@id', None) for cycle in cycles)) <= 1
