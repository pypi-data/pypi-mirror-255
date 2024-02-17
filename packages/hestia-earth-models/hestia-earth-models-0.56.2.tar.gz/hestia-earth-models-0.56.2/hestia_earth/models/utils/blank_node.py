from calendar import monthrange
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime
from dateutil.relativedelta import relativedelta
from enum import Enum
from functools import reduce
from statistics import mode, mean
from typing import (
    Any,
    Callable,
    NamedTuple,
    Optional,
    Union
)
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.tools import (
    flatten,
    list_sum,
    safe_parse_date,
    safe_parse_float,
    non_empty_list
)

from ..log import debugValues
from . import _filter_list_term_unit
from .constant import Units
from .property import get_node_property, get_node_property_value
from .lookup import (
    is_model_siteType_allowed,
    is_siteType_allowed,
    is_product_id_allowed, is_product_termType_allowed,
    is_input_id_allowed, is_input_termType_allowed
)
from .term import get_lookup_value


def group_by_keys(group_keys: list = ['term']):
    def run(group: dict, input: dict):
        group_key = '-'.join(non_empty_list(map(lambda v: input.get(v, {}).get('@id'), group_keys)))
        group[group_key] = group.get(group_key, []) + [input]
        return group
    return run


def _module_term_id(term_id: str, module): return getattr(module, 'TERM_ID', term_id).split(',')[0]


def _run_model_required(model: str, term: dict, data: dict):
    siteType_allowed = is_model_siteType_allowed(model, term, data)

    run_required = all([siteType_allowed])
    debugValues(data, model=model, term=term.get('@id'),
                run_required=run_required,
                siteType_allowed=siteType_allowed)
    return run_required


def _run_required(model: str, term: dict, data: dict):
    siteType_allowed = is_siteType_allowed(data, term)
    product_id_allowed = is_product_id_allowed(data, term)
    product_termType_allowed = is_product_termType_allowed(data, term)
    input_id_allowed = is_input_id_allowed(data, term)
    input_termType_allowed = is_input_termType_allowed(data, term)

    run_required = all([
        siteType_allowed, product_id_allowed, product_termType_allowed, input_id_allowed, input_termType_allowed
    ])
    # model is only used for logs here, skip logs if model not provided
    if model:
        debugValues(data, model=model, term=term.get('@id'),
                    siteType_allowed=siteType_allowed,
                    product_id_allowed=product_id_allowed,
                    product_termType_allowed=product_termType_allowed,
                    input_id_allowed=input_id_allowed,
                    input_termType_allowed=input_termType_allowed)
        # logging this for the model would cause issues parsing statuses
        if model != 'emissionNotRelevant':
            debugValues(data, model=model, term=term.get('@id'), run_required=run_required)
    return run_required


def is_run_required(model: str, term_id: str, node: dict):
    """
    Determines whether the term for the model should run or not, based on lookup values.

    Parameters
    ----------
    model : str
        The `@id` of the model. Example: `pooreNemecek2018`.
    term_id : str
        The `@id` of the `Term` or the full JSON-LD of the Term. Example: `sandContent`.
    node : dict
        The node on which the model is applied. Logging purpose ony.

    Returns
    -------
    bool
        True if the model is required to run.
    """
    term = download_hestia(term_id)
    return (
        (_run_model_required(model, term, node) if model else True) and _run_required(model, term, node)
    ) if term else True


def run_if_required(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if is_run_required(model, _module_term_id(term_id, module), data) else []


def find_terms_value(nodes: list, term_id: str):
    """
    Returns the sum of all blank nodes in the list which match the `Term` with the given `@id`.

    Parameters
    ----------
    values : list
        The list in which to search for. Example: `cycle['nodes']`.
    term_id : str
        The `@id` of the `Term`. Example: `sandContent`

    Returns
    -------
    float
        The total `value` as a number.
    """
    return list_sum(get_total_value(filter(lambda node: node.get('term', {}).get('@id') == term_id, nodes)))


def get_total_value(nodes: list):
    """
    Get the total `value` of a list of Blank Nodes.
    This method does not take into account the `units` and possible conversions.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    return list(map(lambda node: list_sum(node.get('value', [])), nodes))


def _value_as(term_id: str, convert_to_property=True):
    def get_value(node: dict):
        property = get_node_property(node, term_id)
        # ignore node value if property is not found
        factor = safe_parse_float(property.get('value', 0))
        value = list_sum(node.get('value', []))
        ratio = factor / 100 if property.get('term', {}).get('units', '') == '%' else factor
        return 0 if ratio == 0 else (value * ratio if convert_to_property else value / ratio)
    return get_value


def get_total_value_converted(nodes: list, conversion_property, convert_to_property=True):
    """
    Get the total `value` of a list of Blank Nodes converted using a property of each Blank Node.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.
    conversion_property : str|List[str]
        Property (or multiple properties) used for the conversion. Example: `nitrogenContent`.
        See https://hestia.earth/glossary?termType=property for a list of `Property`.
    convert_to_property : bool
        By default, property is multiplied on value to get result. Set `False` to divide instead.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    def convert_multiple(node: dict):
        value = 0
        for prop in conversion_property:
            value = _value_as(prop, convert_to_property)(node)
            node['value'] = [value]
        return value

    return [
        _value_as(conversion_property, convert_to_property)(node) if isinstance(conversion_property, str) else
        convert_multiple(node) for node in nodes
    ]


def get_N_total(nodes: list) -> list:
    """
    Get the total nitrogen content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg N` will be used.
    2. Every blank node specified in `kg` will be multiplied by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_N_nodes) + get_total_value_converted(kg_nodes, 'nitrogenContent')


def get_KG_total(nodes: list) -> list:
    """
    Get the total kg mass of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg` will be used.
    2. Every blank node specified in `kg N` will be divided by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_nodes) + get_total_value_converted(kg_N_nodes, 'nitrogenContent', False)


def get_P2O5_total(nodes: list) -> list:
    """
    Get the total phosphate content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every organic fertiliser specified in `kg P2O5` will be used.
    1. Every organic fertiliser specified in `kg N` will be multiplied by the `phosphateContentAsP2O5` property.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `phosphateContentAsP2O5` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The phosphate values as a list of numbers.
    """
    kg_P_nodes = _filter_list_term_unit(nodes, Units.KG_P2O5)
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_P_nodes) + get_total_value_converted(kg_N_nodes + kg_nodes, 'phosphateContentAsP2O5')


def convert_to_nitrogen(node: dict, model: str, term_id: str, blank_nodes: list):
    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'nitrogenContent')
        return value / 100 if value > 0 else get_node_property_value(model, input, 'crudeProteinContent') / 625

    values = [(i, prop_value(i)) for i in blank_nodes]
    missing_nitrogen_property = [i.get('term', {}).get('@id') for i, p_value in values if not p_value]

    debugValues(node, model=model, term=term_id,
                missing_nitrogen_property=';'.join(set(missing_nitrogen_property)))

    return list_sum([
        list_sum(i.get('value', [])) * p_value for i, p_value in values
    ]) if len(missing_nitrogen_property) == 0 else None


def convert_to_carbon(node: dict, model: str, term_id: str, blank_nodes: list):
    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'carbonContent')
        return value / 100 if value > 0 else \
            get_node_property_value(model, input, 'energyContentHigherHeatingValue') * 0.021

    values = [(i, prop_value(i)) for i in blank_nodes]
    missing_carbon_property = [i.get('term', {}).get('@id') for i, p_value in values if not p_value]

    debugValues(node, model=model, term=term_id,
                missing_carbon_property=';'.join(missing_carbon_property))

    return list_sum([
        list_sum(i.get('value', [])) * p_value for i, p_value in values
    ]) if len(missing_carbon_property) == 0 else None


class ArrayTreatment(Enum):
    """
    Enum representing different treatments for arrays of values.
    """
    MEAN = 'mean'
    MODE = 'mode'
    SUM = 'sum'
    FIRST = 'first'
    LAST = 'last'


def _should_run_array_treatment(value):
    return isinstance(value, Iterable) and len(value) > 0


DEFAULT_ARRAY_TREATMENT = ArrayTreatment.MEAN
ARRAY_TREATMENT_TO_REDUCER = {
    ArrayTreatment.MEAN: lambda value: mean(value) if _should_run_array_treatment(value) else 0,
    ArrayTreatment.MODE: lambda value: mode(value) if _should_run_array_treatment(value) else 0,
    ArrayTreatment.SUM: lambda value: sum(value) if _should_run_array_treatment(value) else 0,
    ArrayTreatment.FIRST: lambda value: value[0] if _should_run_array_treatment(value) else 0,
    ArrayTreatment.LAST: lambda value: value[-1] if _should_run_array_treatment(value) else 0
}
"""
A dictionary mapping ArrayTreatment enums to corresponding reducer functions.
"""


def _retrieve_array_treatment(
    node: dict,
    is_larger_unit: bool = False,
    default: ArrayTreatment = ArrayTreatment.FIRST
) -> ArrayTreatment:
    """
    Retrieves the array treatment for a given node.

    Array treatments are used to reduce an array's list of values into
    a single value. The array treatment is retrieved from a lookup on
    the node's term.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    is_larger_unit : bool, optional
        Flag indicating whether to use the larger unit lookup, by default `False`.
    default : ArrayTreatment, optional
        Default value to return if the lookup fails, by default `ArrayTreatment.FIRST`.

    Returns
    -------
    ArrayTreatment
        The retrieved array treatment.

    """
    ARRAY_TREATMENT_LOOKUPS = [
        'arrayTreatmentLargerUnitOfTime',
        'arrayTreatment'
    ]
    lookup = ARRAY_TREATMENT_LOOKUPS[0] if is_larger_unit else ARRAY_TREATMENT_LOOKUPS[1]

    term = node.get('term', {})
    lookup_value = get_lookup_value(term, lookup, skip_debug=True)

    return next(
        (treatment for treatment in ArrayTreatment if treatment.value == lookup_value),
        default
    )


def get_node_value(
    node: dict,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None
) -> Union[float, bool]:
    """
    Get the value from the dictionary representing the node,
    applying optional array treatment if the value is a list.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    is_larger_unit : bool, optional
        A flag indicating whether the unit of time is larger, by default `False`.
    array_treatment : ArrayTreatment, optional
        An optional override for the treatment to be applied to an array value, if `None` the array treatment in the
        node's term's lookup is used (which defaults to `FIRST` if no array treatment is specified), by default `None`.

    Returns
    -------
    float | bool
        The extracted value from the node.

    """
    value = node.get("value", 0)

    reducer = ARRAY_TREATMENT_TO_REDUCER[(
        array_treatment or _retrieve_array_treatment(node, is_larger_unit=is_larger_unit)
    )] if isinstance(value, list) and len(value) > 0 else None

    return reducer(value) if reducer else value if isinstance(value, bool) else value or 0


def _convert_to_set(
    variable: Union[Iterable[Any], Any]
) -> set:
    """
    Description of function

    Parameters
    ----------
    variable : Iterable[Any] | Any
        The input variable, which can be either an iterable or a single element.

    Returns
    -------
    set
        A set containing the elements of the input variable.
    """
    is_iterable = isinstance(variable, Iterable) and not isinstance(variable, (str, bytes))
    return set(variable) if is_iterable else {variable}


def node_term_match(
    node: dict,
    target_term_ids: Union[str, set[str]]
) -> bool:
    """
    Check if the term ID of the given node matches any of the target term IDs.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    target_term_ids : str | set[str]
        A single term ID or an set of term IDs to check against.

    Returns
    -------
    bool
        `True` if the term ID of the node matches any of the target
        term IDs, `False` otherwise.

    """
    target_term_ids = _convert_to_set(target_term_ids)
    return node.get('term', {}).get('@id', None) in target_term_ids


def node_lookup_match(
    node: dict,
    lookup: str,
    target_lookup_values: Union[str, set[str]]
) -> bool:
    """
    Check if the lookup value in the node's term matches any of the
    target lookup values.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    lookup : str
        The lookup key.
    target_lookup_values : str | set[str]
        A single target lookup value or a set of target lookup values
        to check against.

    Returns
    -------
    bool
        `True` if there is a match, `False` otherwise.
    """
    target_lookup_values = _convert_to_set(target_lookup_values)
    return get_lookup_value(node.get('term', {}), lookup) in target_lookup_values


def cumulative_nodes_match(
    function: Callable[[dict], bool],
    nodes: list[dict],
    *,
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes that satisfy the provided
    function exceed the threshold.

    Parameters
    ----------
    function : Callable[[dict], bool]
        A function to determine whether a node should be included in
        the calculation.
    nodes : list[dict]
        The list of nodes to be considered.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the
        function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by
        default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit
        of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False`
        otherwise.

    """
    values = [
        get_node_value(
            node, is_larger_unit, array_treatment
        ) or default_node_value for node in nodes if function(node)
    ]

    return list_sum(non_empty_list(flatten(values))) > cumulative_threshold


def cumulative_nodes_term_match(
    nodes: list[dict],
    *,
    target_term_ids: Union[str, set[str]],
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes with matching term IDs
    exceed the threshold.

    Parameters
    ----------
    nodes : list[dict]
        The list of nodes to be considered.
    target_term_ids : str | set[str]
        The term ID or a set of term IDs to match.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False` otherwise.
    """
    target_term_ids = _convert_to_set(target_term_ids)

    def match_function(node: dict) -> bool:
        return node_term_match(node, target_term_ids)

    return cumulative_nodes_match(
        match_function,
        nodes,
        cumulative_threshold=cumulative_threshold,
        default_node_value=default_node_value,
        is_larger_unit=is_larger_unit,
        array_treatment=array_treatment
    )


def cumulative_nodes_lookup_match(
    nodes: list[dict],
    *,
    lookup: str,
    target_lookup_values: Union[str, set[str]],
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes with matching lookup values exceed the threshold.

    Parameters
    ----------
    nodes : list[dict]
        The list of nodes to be considered.
    lookup : str
        The lookup key to match against in the nodes.
    target_lookup_values : str | set[str]
        The lookup value or a set of lookup values to match.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the
        function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by
        default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit
        of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False`
        otherwise.
    """
    target_lookup_values = _convert_to_set(target_lookup_values)

    def match_function(node: dict) -> bool:
        return node_lookup_match(node, lookup, target_lookup_values)

    return cumulative_nodes_match(
        match_function,
        nodes,
        cumulative_threshold=cumulative_threshold,
        default_node_value=default_node_value,
        is_larger_unit=is_larger_unit,
        array_treatment=array_treatment
    )


# --- Group nodes by year ---


class DatestrFormat(Enum):
    """
    Enum representing ISO date formats permitted by Hestia.

    See: https://en.wikipedia.org/wiki/ISO_8601
    """
    YEAR = r"%Y"
    YEAR_MONTH = r"%Y-%m"
    YEAR_MONTH_DAY = r"%Y-%m-%d"
    YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = r"%Y-%m-%dT%H:%M:%S"
    MONTH = r"--%m"
    MONTH_DAY = r"--%m-%d"


DatestrGapfillMode = Enum("DatestrGapfillMode", [
    "START",
    "END"
])
"""
Enum representing modes of gapfilling incomplete datestrings.
"""


DatetimeRange = NamedTuple(
    "DatetimeRange",
    [
        ("start", datetime),
        ("end", datetime)
    ]
)
"""
A named tuple for storing a datetime range.

Attributes
----------
start : datetime
    The start of the datetime range.
end : datetime
    The end of the datetime range.
"""


def _check_datestr_format(datestr: str, format: Union[DatestrFormat, str]) -> bool:
    """
    Use `datetime.strptime` to determine if a datestr is in a particular ISO format.
    """
    try:
        date_format_str = (
            format.value if isinstance(format, DatestrFormat)
            else str(format)
        )
        return bool(datetime.strptime(str(datestr), date_format_str))
    except ValueError:
        return False


def _get_datestr_format(datestr: str, default: Optional[Any] = None) -> Union[DatestrFormat, Any, None]:
    """
    Check a datestr against each ISO format permitted by the Hestia schema and
    return the matching format.
    """
    return next(
        (date_format for date_format in DatestrFormat if _check_datestr_format(str(datestr), date_format)),
        default
    )


def _gapfill_datestr_start(datestr: str, *_) -> str:
    """
    Gapfill an incomplete datestr with the earliest possible date and time.

    Datestr will snap to the start of the year/month/day as appropriate.
    """
    return datestr + "YYYY-01-01T00:00:00"[len(datestr):]


def _gapfill_datestr_end(datestr: str, format: DatestrFormat) -> str:
    """
    Gapfill an incomplete datestr with the latest possible date and time.

    Datestr will snap to the end of the year/month/day as appropriate.
    """
    datetime = safe_parse_date(datestr)
    num_days_in_month = (
        monthrange(datetime.year, datetime.month)[1]
        if datetime and format == DatestrFormat.YEAR_MONTH
        else 31
    )
    completion_str = f"YYYY-12-{num_days_in_month}T23:59:59"
    return datestr + completion_str[len(datestr):]


DATESTR_GAPFILL_MODE_TO_GAPFILL_FUNCTION = {
    DatestrGapfillMode.START: _gapfill_datestr_start,
    DatestrGapfillMode.END: _gapfill_datestr_end
}


def _gapfill_datestr(datestr: str, mode: DatestrGapfillMode = DatestrGapfillMode.START) -> str:
    """
    Gapfill incomplete datestrs and returns them in the format `YYYY-MM-DDTHH:MM_SS`.
    """
    VALID_DATE_FORMATS = {
        DatestrFormat.YEAR, DatestrFormat.YEAR_MONTH, DatestrFormat.YEAR_MONTH_DAY
    }
    _datestr = str(datestr)
    format = _get_datestr_format(_datestr)
    should_run = format in VALID_DATE_FORMATS
    return DATESTR_GAPFILL_MODE_TO_GAPFILL_FUNCTION[mode](_datestr, format) if should_run else _datestr


def _datetime_within_range(datetime: datetime, range: DatetimeRange) -> bool:
    """
    Determine whether or not a `datetime` falls within a `DatetimeRange`.
    """
    return range.start < datetime < range.end


def _datetime_range_duration(range: DatetimeRange) -> float:
    """
    Determine the length of a `DatetimeRange` in seconds.
    """
    return (range.end - range.start).total_seconds()


def _calc_datetime_range_intersection_duration(
    range_a: DatetimeRange, range_b: DatetimeRange
) -> float:
    """
    Determine the length of a `DatetimeRange` in seconds.
    """
    latest_start = max(range_a.start, range_b.start)
    earliest_end = min(range_a.end, range_b.end)

    intersection_range = DatetimeRange(
        start=latest_start,
        end=earliest_end
    )

    # if less than 0 the ranges do not intersect, so return 0.
    return max(0, _datetime_range_duration(intersection_range))


def _validate_intersection_threshold(
    fraction_of_year: float,
    fraction_of_node_duration: float,
    is_final_year: bool
) -> bool:
    """
    Return `True` if the the node intersections with a year group by
    more than 30% OR the year group represents more than 50% of a node's
    duration. Return `False` otherwise.

    This is to prevent cycles/managements being categorised into a year group
    when due to overlapping by just a few days. In these cases, nodes will only
    be counted in the year group if the majority of that node takes place in
    that year.
    """
    FRACTION_OF_YEAR_THRESHOLD = 0.3
    FRACTION_OF_NODE_DURATION_THRESHOLD = 0.5

    return (
        fraction_of_year > FRACTION_OF_YEAR_THRESHOLD
        or fraction_of_node_duration > FRACTION_OF_NODE_DURATION_THRESHOLD
        or (is_final_year and fraction_of_node_duration == FRACTION_OF_NODE_DURATION_THRESHOLD)
    )


def group_nodes_by_year(
    nodes: list[dict],
    default_node_duration: int = 1,
    sort_result: bool = True
) -> dict[int, list[dict]]:
    """
    Group nodes by year based on their start and end dates. Incomplete date strings are gap-filled automatically
    using `_gapfill_datestr` function.

    Parameters
    ----------
    nodes : list[dict]
        A list of nodes with start and end date information.
    default_node_duration : int, optional
        Default duration of a node years if start date is not available, by default 1.
    sort_result : bool, optional
        Flag to sort the result by year, by default True.

    Returns
    -------
    dict[int, list[dict]]
        A dictionary where keys are years and values are lists of nodes.
    """
    def group_node(groups: dict, index: int):
        node = nodes[index]

        end_datestr = _gapfill_datestr(node.get("endDate"), DatestrGapfillMode.END)
        start_datestr = _gapfill_datestr(node.get("startDate"), DatestrGapfillMode.START)

        end = safe_parse_date(end_datestr)
        start = (
            safe_parse_date(start_datestr)
            or end - relativedelta(years=default_node_duration, seconds=-1)
            if bool(end) else None
        )

        node_datetime_range = DatetimeRange(
            start=start,
            end=end
        )

        range_end = end.year + 1 if end else 0
        range_start = start.year if start else 0

        for year in range(range_start, range_end):

            group_datetime_range = DatetimeRange(
                start=safe_parse_date(_gapfill_datestr(year, DatestrGapfillMode.START)),
                end=safe_parse_date(_gapfill_datestr(year, DatestrGapfillMode.END))
            )

            is_final_year = _datetime_within_range(node_datetime_range.end, group_datetime_range)

            # add 1 to durations if datestrs gap filled (to account for 1 second between 23:59:59 and 00:00:00)
            year_duration = _datetime_range_duration(group_datetime_range) + 1
            node_duration = _datetime_range_duration(node_datetime_range) + 1
            intersection_duration = (
                _calc_datetime_range_intersection_duration(node_datetime_range, group_datetime_range) + 1
            )

            fraction_of_year = intersection_duration / year_duration
            fraction_of_node_duration = intersection_duration / node_duration

            time_fraction_dict = {
                "fraction_of_year": fraction_of_year,
                "fraction_of_node_duration": fraction_of_node_duration
            }

            _node = node | time_fraction_dict

            should_run = _validate_intersection_threshold(
                fraction_of_year,
                fraction_of_node_duration,
                is_final_year
            )

            should_run and groups[year].append(_node)

        return groups

    grouped = reduce(group_node, range(len(nodes)), defaultdict(list))
    return dict(sorted(grouped.items())) if sort_result else grouped
