from functools import reduce
from dateutil import parser
from statistics import mode, mean
from typing import Any, Union

from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_list, flatten, safe_parse_float
from hestia_earth.utils.date import diff_in_days

from . import _term_id, _include_method
from .term import get_lookup_value

# from hestia_earth.models.site.utils import _has_all_months

# TODO: verify those values
MAX_DEPTH = 1000
OLDEST_DATE = '1800'

MEASUREMENT_REDUCE = {
    'mean': lambda value: mean(value),
    'mode': lambda value: mode(value),
    'sum': lambda value: sum(value)
}


def _new_measurement(term, model=None):
    node = {'@type': SchemaType.MEASUREMENT.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_method(node, model)


def measurement_value(measurement: dict, is_larger_unit: bool = False) -> float:
    term = measurement.get('term', {})
    reducer = get_lookup_value(term, 'arrayTreatmentLargerUnitOfTime' if is_larger_unit else 'arrayTreatment') or 'mean'
    value = measurement.get('value', [])
    is_value_valid = value is not None and isinstance(value, list) and len(value) > 0
    return MEASUREMENT_REDUCE.get(reducer, lambda v: v[0])(value) if is_value_valid else 0


def _measurement_date(measurement: dict): return parser.isoparse(measurement.get('endDate', OLDEST_DATE))


def _distance(measurement: dict, date): return abs((_measurement_date(measurement) - date).days)


def _most_recent_measurements(measurements: list, date: str) -> list:
    closest_date = parser.isoparse(date)
    min_distance = min([_distance(m, closest_date) for m in measurements])
    return list(filter(lambda m: _distance(m, closest_date) == min_distance, measurements))


def _shallowest_measurement(measurements: list) -> dict:
    min_depth = min([m.get('depthUpper', MAX_DEPTH) for m in measurements])
    return next((m for m in measurements if m.get('depthUpper', MAX_DEPTH) == min_depth), {})


def most_relevant_measurement(measurements: list, term_id: str, date: str):
    filtered_measurements = [m for m in measurements if m.get('term', {}).get('@id') == term_id]
    return {} if len(filtered_measurements) == 0 \
        else _shallowest_measurement(_most_recent_measurements(filtered_measurements, date)) \
        if date and len(filtered_measurements) > 1 else filtered_measurements[0]


def most_relevant_measurement_value(measurements: list, term_id: str, date: str, default=None):
    measurement = most_relevant_measurement(measurements, term_id, date)
    return measurement_value(measurement) if measurement else default


def _group_measurement_key(measurement: dict, include_dates: bool = True):
    keys = non_empty_list([
        str(measurement.get('depthUpper', '')),
        str(measurement.get('depthLower', '')),
        measurement.get('startDate') if include_dates else None,
        measurement.get('endDate') if include_dates else None
    ])
    return '_to_'.join(keys) if len(keys) > 0 else 'no-depths'


def group_measurements_by_depth(measurements: list, include_dates: bool = True):
    def group_by(group: dict, measurement: dict):
        key = _group_measurement_key(measurement, include_dates)
        return group | {key: group.get(key, []) + [measurement]}

    return reduce(group_by, measurements, {})


def has_all_months(dates: list):
    try:
        months = [int(d[5:7]) for d in dates]
        return all(m in months for m in range(1, 13))
    except Exception:
        return False


def group_measurement_values_by_year(
    measurement: dict,
    inner_key: Union[Any, None] = None,
    complete_years_only: bool = False,
) -> Union[dict, None]:
    """
    Groups the values of a monthly measurement by year.

    Only complete years (i.e. where all 12 months have a value) are returned and values are
    not transformed in any way (i.e. they are not averaged).

    Parameters
    ----------
    measurement : dict
        A Hestia `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    inner_key: Any | None
        An optional inner dictionary key for the outputted annualised groups (can be used to merge annualised
        dictionaries together), default value: `None`.
    complete_years_only : bool
        Keep only years where there is a measurement value for each calendar month, default value: `False`.

    Returns
    -------
    dict | None
        The annualised dictionary of measurement values by year.
    """
    dates = measurement.get('dates', [])
    values = measurement.get('value', [])

    def group_values(groups: dict, index: int) -> dict:
        """
        Reducer function used to group the `Measurement` dates and values into years.
        """
        try:
            date = dates[index]
            value = values[index]
            year = int(date[0:4])  # Get the year from a date in the format `YYYY-MM-DD`
            groups[year] = groups.get(year, []) + [(date, value)]
        except (IndexError, ValueError):
            pass
        return groups

    grouped = reduce(group_values, range(0, len(dates)), dict())

    iterated = {
        key: {inner_key: [v for _d, v in values]} if inner_key else [v for _d, v in values]
        for key, values in grouped.items()
        if has_all_months([d for d, _v in values]) or not complete_years_only
    }

    return iterated


def most_relevant_measurement_value_by_depth_and_date(
    measurements: list[dict],
    term_id: str,
    date: str,
    depth_upper: int,
    depth_lower: int,
    depth_strict: bool = True,
    default: Union[Any, None] = None
) -> Union[tuple[float, str], tuple[Any, None]]:
    """
    Returns the measurement value with the closest data, depth upper and depth lower.

    Parameters
    ----------
    measurements list[dict]
        A list of Hestia `Measurement` nodes, see: https://www.hestia.earth/schema/Measurement.
    term_id : str
        The `@id` of a Hestia `Term`. Example: `"sandContent"`
    date : str
        The target date in ISO 8601 string format (`"YYYY-MM-DD"`), see: https://en.wikipedia.org/wiki/ISO_8601.
    depth_upper : int
        The target `depthUpper` of the `Measurement`.
    depth_lower : int
        The target `depthLower` of the `Measurement`.
    depth_strict : bool
        Whether or not the depth requirement is strict, default value: `True`.
    default : Any | None
        The returned value if no match was found, default value: `None`.

    Returns
    -------
    tuple[float, str] | tuple[Any, None]:
        If a nearest measurement is found, return `(nearest_value, nearest_date)` else return `(default, None)`
    """
    filtered_measurements = [m for m in measurements if m.get('term', {}).get('@id') == term_id]

    if len(filtered_measurements) == 0:
        return default, None

    grouped_measurements = group_measurements_by_depth(filtered_measurements, False)

    def depth_distance(depth_string):
        split = depth_string.split('_')
        upper, lower = safe_parse_float(split[0]), safe_parse_float(split[2])  # "a_to_b"
        return abs(upper - depth_upper) + abs(lower - depth_lower)

    nearest_key = min(grouped_measurements.keys(), key=depth_distance)
    closest_depth_measurements = (
        grouped_measurements.get(nearest_key, []) if depth_distance(nearest_key) <= 0 or not depth_strict else []
    )

    dates = flatten([measurement.get('dates', []) for measurement in closest_depth_measurements])
    values = flatten([measurement.get('value', []) for measurement in closest_depth_measurements])

    def date_distance(_date):
        return abs(diff_in_days(_date if _date else OLDEST_DATE, date))

    nearest_value, nearest_date = min(zip(values, dates), key=lambda i: date_distance(i[1]), default=(default, None))

    return nearest_value, nearest_date
