from hestia_earth.utils.tools import non_empty_list, list_average

from hestia_earth.models.log import logShouldRun, logRequirements, log_as_table
from . import MODEL


def run_products_average(cycle: dict, term_id: str, get_value_func):
    products = cycle.get('products', [])

    values_by_product = [
        (p.get('term', {}).get('@id'), get_value_func(p)) for p in products
    ]
    values = non_empty_list([
        value for term_id, value in values_by_product
    ])
    has_values = len(values) > 0

    logRequirements(cycle, model=MODEL, term=term_id,
                    has_values=has_values,
                    details=log_as_table([
                        {'id': term_id, 'value': value} for term_id, value in values_by_product
                    ]))

    should_run = all([has_values])
    logShouldRun(cycle, MODEL, term_id, should_run)
    return list_average(values) if should_run else None
