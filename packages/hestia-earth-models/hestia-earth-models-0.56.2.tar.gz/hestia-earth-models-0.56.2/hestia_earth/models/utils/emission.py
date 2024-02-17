from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name

from . import _term_id, _include_methodModel


def _new_emission(term, model=None):
    node = {'@type': SchemaType.EMISSION.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def is_in_system_boundary(term_id: str):
    lookup = download_lookup('emission.csv')
    value = get_table_value(lookup, 'termid', term_id, column_name('inHestiaDefaultSystemBoundary'))
    # handle numpy boolean
    return not (not value)
