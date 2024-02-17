from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input

from hestia_earth.models.ipcc2019.pastureGrass import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"
MILK_YIELD_TERMS = ['milkYieldPerCowRaw', 'milkYieldPerSheepRaw']
WOOL_TERMS = ['woolSheepGreasy']


def fake_download_hestia(term_id: str, *args): return {'@id': term_id, 'termType': 'forage'}


@patch(f"{class_path}.download_hestia", side_effect=fake_download_hestia)
@patch(f"{class_path}.get_wool_terms", return_value=WOOL_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=MILK_YIELD_TERMS)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.download_hestia", side_effect=fake_download_hestia)
@patch(f"{class_path}.get_wool_terms", return_value=WOOL_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=MILK_YIELD_TERMS)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run_with_feed(*args):
    with open(f"{fixtures_folder}/with-feed/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-feed/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.download_hestia", side_effect=fake_download_hestia)
@patch(f"{class_path}.get_wool_terms", return_value=WOOL_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=MILK_YIELD_TERMS)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run_with_goats(*args):
    with open(f"{fixtures_folder}/with-goats/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-goats/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
