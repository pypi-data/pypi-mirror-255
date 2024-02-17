from unittest.mock import patch
import json

from tests.utils import fixtures_path, fake_new_emission
from hestia_earth.models.cycle.input.ecoinventV3 import MODEL, run

class_path = f"hestia_earth.models.cycle.input.{MODEL}"
fixtures_folder = f"{fixtures_path}/cycle/input/{MODEL}"


TERM_BY_ID = {
    '24EpibrassinolideTgai': {
        "defaultProperties": [{
            "@type": "Property",
            "term": {
                "@id": "activeIngredient",
                "@type": "Term"
            },
            "value": 20,
            "key": {
                "@id": "CAS-78821-43-9",
                "@type": "Term",
                "termType": "pesticideAI"
            }
        }, {
            "@type": "Property",
            "term": {
                "@id": "activeIngredient",
                "@type": "Term"
            },
            "value": 30,
            "key": {
                "@id": "CAS-78821-42-8",
                "@type": "Term",
                "termType": "pesticideAI"
            }
        }]
    }
}


@patch('hestia_earth.models.utils.pesticideAI.download_hestia', side_effect=lambda id, *args: TERM_BY_ID[id])
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
