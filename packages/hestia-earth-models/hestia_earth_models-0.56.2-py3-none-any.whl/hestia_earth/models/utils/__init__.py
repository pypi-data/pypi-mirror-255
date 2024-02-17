from os.path import dirname, abspath
import sys
from functools import reduce
import operator
from typing import Any
from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node

from .constant import Units

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
CACHE_KEY = '_cache'


def cached_value(node: dict, key: str = None, default=None):
    cache = node.get(CACHE_KEY, {})
    return cache.get(key, default) if key else cache


def _term_id(term): return term.get('@id') if isinstance(term, dict) else term


def _omit(values: dict, keys: list): return {k: v for k, v in values.items() if k not in keys}


def _include_model(node: dict, term_id: str):
    term = download_hestia(term_id) or {}
    return {**node, **({} if term.get('@id') is None else {'model': linked_node(term)})}


def _include_method(node: dict, term_id: str):
    term = download_hestia(term_id) or {}
    return {**node, **({} if term.get('@id') is None else {'method': linked_node(term)})}


def _include_methodModel(node: dict, term_id: str):
    term = download_hestia(term_id) or {}
    return {**node, **({} if term.get('@id') is None else {'methodModel': linked_node(term)})}


def _run_in_serie(data: dict, models: list): return reduce(lambda prev, model: model(prev), models, data)


def _load_calculated_node(node, type: SchemaType, data_state='recalculated'):
    # return original value if recalculated is not available
    return download_hestia(node.get('@id'), type, data_state=data_state) or download_hestia(node.get('@id'), type)


def _unit_str(unit) -> str: return unit if isinstance(unit, str) else unit.value


def _filter_list_term_unit(values: list, unit: Any):
    units = list(map(_unit_str, unit)) if isinstance(unit, list) else [_unit_str(unit)]
    return list(filter(lambda i: i.get('term', {}).get('units') in units, values))


def is_from_model(node: dict) -> bool:
    """
    Check if the Blank Node came from one of the Hestia Models.

    Parameters
    ----------
    node : dict
        The Blank Node containing `added` and `updated`.

    Returns
    -------
    bool
        `True` if the value came from a model, `False` otherwise.
    """
    return 'value' in node.get('added', []) or 'value' in node.get('updated', [])


def sum_values(values: list):
    """
    Sum up the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return sum(filtered_values) if len(filtered_values) > 0 else None


def multiply_values(values: list):
    """
    Multiply the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return reduce(operator.mul, filtered_values, 1) if len(filtered_values) > 1 else None


def term_id_prefix(term_id: str): return term_id.split('Kg')[0]


def get_kg_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgMass"


def get_kg_N_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgN"


def get_kg_P2O5_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgP2O5"


def get_kg_K2O_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgK2O"


def get_kg_VS_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgVs"


def get_kg_term_units(term_id: str, units: str):
    return {
        Units.KG.value: get_kg_term_id,
        Units.KG_N.value: get_kg_N_term_id,
        Units.KG_P2O5.value: get_kg_P2O5_term_id,
        Units.KG_K2O.value: get_kg_K2O_term_id,
        Units.KG_VS.value: get_kg_VS_term_id
    }.get(units, lambda x: None)(term_id)


def _get_by_key(x, y):
    return x if x is None else (
        x.get(y) if isinstance(x, dict) else list(map(lambda v: get_dict_key(v, y), x))
    )


def get_dict_key(value: dict, key: str): return reduce(lambda x, y: _get_by_key(x, y), key.split('.'), value)
