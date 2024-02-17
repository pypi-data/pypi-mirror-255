from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import logShouldRun
from .property import _new_property

DRY_MATTER_TERM_ID = 'dryMatter'
DM_PROP_MAPPING = {
    'value': 'Avg',
    'sd': 'SD',
    'min': 'Min',
    'max': 'Max'
}


def get_feedipedia_properties():
    lookup = download_lookup('property.csv')
    term_ids = list(lookup.termid)
    term_ids = [
        term_id for term_id in term_ids if get_table_value(lookup, 'termid', term_id, column_name('feedipediaName'))
    ]
    return term_ids


def _dm_property(term_id: str, property_values: dict, dm_property_values: dict, dry_matter_property: dict):
    blank_node = _new_property(term_id)
    blank_node_data = {}
    for hestia_key, lookup_key in DM_PROP_MAPPING.items():
        new_dm_value = safe_parse_float(dry_matter_property.get(hestia_key))
        old_dm_value = safe_parse_float(dm_property_values.get(lookup_key))
        old_property_value = safe_parse_float(property_values.get(lookup_key))
        if all([new_dm_value, old_dm_value, old_property_value]):
            blank_node_data[hestia_key] = round(old_property_value / old_dm_value * new_dm_value, 2)
    return (blank_node | blank_node_data) if blank_node_data else None


def _parse_properties(value: str):
    values = value.split(';')
    return {value.split(':')[0]: value.split(':')[1] for value in values}


def rescale_properties_from_dryMatter(model: str, node: dict, blank_nodes: list):
    properties = get_feedipedia_properties()

    def exec_property(input: dict, property_id: str, dry_matter_property: dict):
        term_id = input.get('term', {}).get('@id')
        term_type = input.get('term', {}).get('termType')
        lookup = download_lookup(f"{term_type}-property.csv")

        dm_property_value = get_table_value(lookup, 'termid', term_id, column_name(DRY_MATTER_TERM_ID))
        property_value = get_table_value(lookup, 'termid', term_id, column_name(property_id))

        return _dm_property(
            property_id, _parse_properties(property_value), _parse_properties(dm_property_value), dry_matter_property
        ) if all([property_id, property_value, dm_property_value]) else None

    def exec(blank_node: dict):
        term_id = blank_node.get('term', {}).get('@id')
        all_properties = blank_node.get('properties', [])
        dry_matter_property = find_term_match(all_properties, DRY_MATTER_TERM_ID)
        # get all values for this term that have a special property
        new_properties = non_empty_list([
            exec_property(blank_node, p, dry_matter_property) for p in properties if all([
                not find_term_match(all_properties, p),
                p != DRY_MATTER_TERM_ID
            ])
        ])
        for prop in new_properties:
            logShouldRun(node, model, term_id, True, property=prop.get('term', {}).get('@id'))
        return {**blank_node, 'properties': all_properties + new_properties} if new_properties else blank_node

    return list(map(exec, blank_nodes))
