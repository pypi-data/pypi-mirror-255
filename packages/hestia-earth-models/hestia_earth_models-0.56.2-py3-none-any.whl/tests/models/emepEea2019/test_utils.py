from unittest.mock import patch

from hestia_earth.models.emepEea2019.utils import get_fuel_values

class_path = 'hestia_earth.models.emepEea2019.utils'
TERMS = [
    'diesel',
    'petrol'
]


@patch(f"{class_path}._is_term_type_complete", return_value=True)
def test_get_fuel_values_no_inputs_complete(*args):
    cycle = {'@type': 'Cycle', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == [0]

    cycle = {'@type': 'Transformation', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == []


@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_get_fuel_values_no_inputs_incomplete(*args):
    cycle = {'@type': 'Cycle', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == []

    cycle = {'@type': 'Transformation', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == []


def test_get_fuel_values(*args):
    cycle = {
        '@type': 'Cycle',
        'inputs': [
            {
                'term': {'@id': 'diesel', 'termType': 'fuel'},
                'value': [100]
            },
            {

                'term': {'@id': 'diesel', 'termType': 'fuel'},
                'operation': {'@id': 'crushingWoodMachineUnspecified', 'termType': 'operation'},
                'value': [200]
            },
            {

                'term': {'@id': 'diesel', 'termType': 'fuel'},
                'operation': {'@id': 'helicopterUseOperationUnspecified', 'termType': 'operation'},
                'value': [150]
            },
            {
                'term': {'@id': 'marineGasOil', 'termType': 'fuel'},
                'operation': {'@id': 'crushingWoodMachineUnspecified', 'termType': 'operation'},
                'value': [50]
            }
        ]
    }
    result = get_fuel_values('co2ToAirFuelCombustion', cycle, 'co2ToAirFuelCombustionEmepEea2019')
    assert result == [317.0, 632.0, 475.5, 158.5]
