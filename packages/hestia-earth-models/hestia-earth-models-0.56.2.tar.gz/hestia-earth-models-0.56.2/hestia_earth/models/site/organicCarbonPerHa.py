from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.source import get_source
from hestia_earth.models.utils.measurement import (
    _new_measurement, group_measurements_by_depth, _group_measurement_key, measurement_value
)
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {
                "@type": "Measurement",
                "value": "",
                "term.@id": "soilBulkDensity",
                "depthUpper": "",
                "depthLower": ""
            },
            {
                "@type": "Measurement",
                "value": "",
                "term.@id": "organicCarbonPerKgSoil",
                "depthUpper": "",
                "depthLower": ""
            }
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "depthUpper": "",
        "depthLower": "",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'organicCarbonPerHa'
BIBLIO_TITLE = 'Soil organic carbon sequestration rates in vineyard agroecosystems under different soil management practices: A meta-analysis'  # noqa: E501


def _measurement(site: dict, value: float, depthUpper: int, depthLower: int):
    data = _new_measurement(TERM_ID)
    data['value'] = [value]
    data['depthUpper'] = depthUpper
    data['depthLower'] = depthLower
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    return data | get_source(site, BIBLIO_TITLE)


def _run(site: dict, measurements: list):
    soilBulkDensity = measurement_value(find_term_match(measurements, 'soilBulkDensity'))
    organicCarbonPerKgSoil = find_term_match(measurements, 'organicCarbonPerKgSoil')
    organicCarbonPerKgSoil_value = measurement_value(organicCarbonPerKgSoil)

    value = (
        organicCarbonPerKgSoil.get('depthLower') - organicCarbonPerKgSoil.get('depthUpper')
    ) * soilBulkDensity * (organicCarbonPerKgSoil_value/10) * 1000

    depthUpper = organicCarbonPerKgSoil.get('depthUpper')
    depthLower = organicCarbonPerKgSoil.get('depthLower')

    return _measurement(site, value, depthUpper, depthLower)


def _should_run_measurements(site: dict, measurements: list):
    soilBulkDensity = find_term_match(measurements, 'soilBulkDensity', None)
    has_soilBulkDensity_depthLower = (soilBulkDensity or {}).get('depthLower') is not None
    has_soilBulkDensity_depthUpper = (soilBulkDensity or {}).get('depthUpper') is not None
    organicCarbonPerKgSoil = find_term_match(measurements, 'organicCarbonPerKgSoil', None)
    has_organicCarbonPerKgSoil_depthLower = (organicCarbonPerKgSoil or {}).get('depthLower') is not None
    has_organicCarbonPerKgSoil_depthUpper = (organicCarbonPerKgSoil or {}).get('depthUpper') is not None

    depth_logs = {
        _group_measurement_key(measurements[0], include_dates=False): ';'.join([
            '_'.join([
                'id:soilBulkDensity',
                f"hasDepthLower:{has_soilBulkDensity_depthLower}",
                f"hasDepthUpper:{has_soilBulkDensity_depthUpper}"
            ]),
            '_'.join([
                'id:organicCarbonPerKgSoil',
                f"hasDepthLower:{has_organicCarbonPerKgSoil_depthLower}",
                f"hasDepthUpper:{has_organicCarbonPerKgSoil_depthUpper}"
            ])
        ])
    } if len(measurements) > 0 else {}

    logRequirements(site, model=MODEL, term=TERM_ID,
                    **depth_logs)

    should_run = all([
        has_soilBulkDensity_depthLower, has_soilBulkDensity_depthUpper,
        has_organicCarbonPerKgSoil_depthLower, has_organicCarbonPerKgSoil_depthUpper
    ])
    return should_run


def _should_run(site: dict):
    grouped_measurements = list(group_measurements_by_depth(site.get('measurements', [])).values())
    values = [(measurements, _should_run_measurements(site, measurements)) for measurements in grouped_measurements]
    should_run = any([_should_run for measurements, _should_run in values])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, [measurements for measurements, _should_run in values if _should_run]


def run(site: dict):
    should_run, values = _should_run(site)
    return [_run(site, value) for value in values] if should_run else []
