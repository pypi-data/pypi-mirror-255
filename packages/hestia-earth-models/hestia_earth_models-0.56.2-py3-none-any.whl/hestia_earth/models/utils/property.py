from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import find_term_match, linked_node
from hestia_earth.utils.lookup import download_lookup, extract_grouped_data, get_table_value, column_name
from hestia_earth.utils.tools import list_sum, safe_parse_float

from ..log import debugMissingLookup
from . import _term_id, _include_methodModel
from .term import get_lookup_value


def _new_property(term, model=None):
    node = {'@type': SchemaType.PROPERTY.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def merge_properties(properties: list, new_properties: list):
    return properties + [
        p for p in new_properties if not find_term_match(properties, p.get('term', {}).get('@id'))
    ]


def get_property_lookup_value(model: str, term_id: str, column: str):
    term = {'@id': term_id, 'termType': TermTermType.PROPERTY.value}
    return get_lookup_value(term, column, model=model, term=term_id)


def find_term_property(term, property: str, default=None) -> dict:
    """
    Get the property by `@id` linked to the `Term` in the glossary.

    Parameters
    ----------
    term
        The `Term` either as a `str` (`@id` field) or as a `dict` (containing `@id` as a key).
    property : str
        The `term.@id` of the property. Example: `nitrogenContent`.
    default : Any
        The default value if the property is not found. Defaults to `None`.

    Returns
    -------
    dict
        The property if found, `default` otherwise.
    """
    props = term.get('defaultProperties', []) if isinstance(term, dict) else []
    term_id = _term_id(term)
    props = (download_hestia(term_id) or {}).get('defaultProperties', []) if len(props) == 0 and term_id else props
    return find_term_match(props, property, default)


def get_node_property(node: dict, property: str, find_default_property: bool = True):
    """
    Get the property by `@id` linked to the Blank Node in the glossary.

    It will search for the `Property` in the following order:
    1. Search in the `properties` of the Blank Node if any was provided
    2. Search in the `defaultProperties` of the `term` by default.

    Parameters
    ----------
    node : dict
        The Blank Node, e.g. an `Input`, `Product`, `Measurement`, etc.
    property : str
        The `term.@id` of the property. Example: `nitrogenContent`.
    find_default_property : bool
        Default to fetching the property from the `defaultProperties` of the `Term`.

    Returns
    -------
    dict
        The property if found, `None` otherwise.
    """
    prop = find_term_match(node.get('properties', []), property, None)
    return find_term_property(node.get('term', {}), property, {}) if all([
        find_default_property,
        prop is None
    ]) else (prop or {})


def node_has_no_property(term_id: str):
    return lambda product: find_term_match(product.get('properties', []), term_id, None) is None


def node_has_property(term_id: str):
    return lambda product: find_term_match(product.get('properties', []), term_id, None) is not None


def _node_property_value(model: str, term: dict, prop_name: str):
    # as the lookup table might not exist, we are making sure we return `0` in thise case
    try:
        lookup_name = f"{term.get('termType')}-property.csv"
        lookup = download_lookup(lookup_name)
        term_id = term.get('@id')
        value = extract_grouped_data(get_table_value(lookup, 'termid', term_id, column_name(prop_name)), 'Avg')
        debugMissingLookup(lookup_name, 'termid', term_id, prop_name, value, model=model, term=term_id)
        return safe_parse_float(value)
    except Exception:
        return 0


def get_node_property_value(model: str, node: dict, prop_name: str):
    prop = get_node_property(node, prop_name)
    return prop.get('value', 0) if prop else _node_property_value(model, node.get('term', {}), prop_name)


def get_node_property_value_converted(model: str, node: dict, prop_name: str):
    return list_sum(node.get('value', [])) * get_node_property_value(model, node, prop_name)


def _get_nitrogen_content(node: dict):
    return safe_parse_float(
        get_node_property(node, 'nitrogenContent').get('value', 0)) if node else 0


def _get_nitrogen_tan_content(node: dict):
    return safe_parse_float(
        get_node_property(node, 'totalAmmoniacalNitrogenContentAsN').get('value', 0)) if node else 0
