import json
from unittest.mock import patch
from tests.utils import fixtures_path

from hestia_earth.models.faostat2018.product.price import MODEL, MODEL_KEY, run, _should_run, _lookup_data

class_path = f"hestia_earth.models.{MODEL}.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/product/{MODEL_KEY}"


def test_should_run():
    cycle = {'endDate': '2020-01'}
    should_run, *_ = _should_run(cycle)
    assert not should_run

    cycle['site'] = {'country': {'@id': 'GADM-GBR'}}
    should_run, *_ = _should_run(cycle)
    assert should_run is True


def test_lookup_data():
    assert _lookup_data('cocoaSeedDehulled', 'Cocoa beans', 'GADM-GHA', 2000, term_type='crop') == 412.9
    # average price per tonne as year value is missing
    assert _lookup_data('cocoaSeedDehulled', 'Cocoa beans', 'GADM-GHA', 2012, term_type='crop') == 843.5571428571428


@patch(f"{class_path}.download_hestia", return_value={})
def test_run_crop(*args):
    with open(f"{fixtures_folder}/crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/crop/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.download_hestia", return_value={})
def test_run_animalProduct(*args):
    with open(f"{fixtures_folder}/animalProduct/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/animalProduct/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.download_hestia")
def test_run_liveAnimal_chicken(mock_download_hestia):
    with open(f"{fixtures_folder}/liveAnimal/chicken/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/liveAnimal/chicken/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    mock_download_hestia.return_value = {
        "@id": "meatChickenReadyToCookWeight",
        "@type": "Term",
        "units": "kg ready-to-cook weight",
        "termType": "animalProduct",
        "defaultProperties": [
            {
                "term": {
                    "@type": "Term",
                    "name": "Processing conversion, cold carcass weight to ready-to-cook weight",
                    "termType": "property",
                    "@id": "processingConversionColdCarcassWeightToReadyToCookWeight",
                    "units": "%"
                },
                "value": 72.45065789473684,
                "sd": 3.605314180391945,
                "@type": "Property"
            }
        ]
    }
    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.download_hestia")
def test_run_liveAnimal_pig(mock_download_hestia):
    with open(f"{fixtures_folder}/liveAnimal/pig/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/liveAnimal/pig/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    mock_download_hestia.return_value = {
        "@id": "meatPigColdDressedCarcassWeight",
        "@type": "Term",
        "units": "kg cold dressed carcass weight",
        "termType": "animalProduct",
        "defaultProperties": [
            {
                "term": {
                    "@type": "Term",
                    "name": "Processing conversion, liveweight to cold carcass weight",
                    "termType": "property",
                    "@id": "processingConversionLiveweightToColdCarcassWeight",
                    "units": "%"
                },
                "value": 75.22666597366735,
                "sd": 2.9377280394802323,
                "@type": "Property"
            }
        ]
    }
    value = run(cycle)
    assert value == expected
