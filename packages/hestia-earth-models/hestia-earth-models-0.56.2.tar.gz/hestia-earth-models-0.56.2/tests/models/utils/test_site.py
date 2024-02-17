from unittest.mock import patch
from hestia_earth.schema import SiteSiteType

from hestia_earth.models.utils.site import region_level_1_id, related_cycles, valid_site_type

class_path = 'hestia_earth.models.utils.site'
CYCLE = {'@id': 'id'}


def test_region_level_1_id():
    assert region_level_1_id('GADM-ITA') == 'GADM-ITA'
    assert region_level_1_id('GADM-ITA.16_1') == 'GADM-ITA.16_1'
    assert region_level_1_id('GADM-ITA.16.10_1') == 'GADM-ITA.16_1'
    assert region_level_1_id('GADM-ITA.16.10.3_1') == 'GADM-ITA.16_1'
    assert region_level_1_id('GADM-RWA.5.3.10.4_1') == 'GADM-RWA.5_1'
    assert region_level_1_id('GADM-RWA.5.3.10.4.3_1') == 'GADM-RWA.5_1'

    assert not region_level_1_id('region-world')


@patch(f"{class_path}.find_related", return_value=[CYCLE])
@patch(f"{class_path}.download_hestia", return_value=CYCLE)
def test_related_cycles(*args):
    assert related_cycles('id') == [CYCLE]


def test_valid_site_type():
    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert valid_site_type(site) is True

    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert not valid_site_type(site, [SiteSiteType.OTHER_NATURAL_VEGETATION.value])
