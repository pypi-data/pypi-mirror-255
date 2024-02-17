from copy import deepcopy
from unittest.mock import patch
import json
from numpy.testing import assert_almost_equal
import random
from typing import (
    NamedTuple,
    Optional,
    Union
)
from hestia_earth.schema import (
    SiteSiteType,
    TermTermType
)

from tests.utils import (
    fixtures_path,
    fake_new_measurement,
    PROPERTY,
    MANAGEMENT,
    MEASUREMENT,
)
from hestia_earth.models.ipcc2019.organicCarbonPerHa import (
    _assign_ipcc_carbon_input_category,
    _assign_ipcc_land_use_category,
    _assign_ipcc_management_category,
    _assign_ipcc_soil_category,
    _calc_temperature_factor,
    _calc_tier_1_soc_stocks,
    _calc_water_factor,
    _check_cropland_high_with_manure_category,
    _check_cropland_high_without_manure_category,
    _check_cropland_low_category,
    _check_cropland_medium_category,
    _make_carbon_input_args,
    _run_annual_organic_carbon_inputs,
    CarbonSource,
    CLAY_CONTENT_MAX,
    CLAY_CONTENT_TERM_ID,
    IpccCarbonInputCategory,
    IpccLandUseCategory,
    IpccManagementCategory,
    IpccSoilCategory,
    MODEL,
    run,
    SAND_CONTENT_MIN,
    SAND_CONTENT_TERM_ID,
    TERM_ID
)


TIER_2_SUBFOLDERS = [
    'Tier2/with-generalised-monthly-measurements',  # Closes issue 600
    'Tier2/with-incomplete-climate-data',  # Closes issue 599
    'Tier2/with-initial-soc',
    'Tier2/with-multi-year-cycles',
    'Tier2/without-any-measurements',  # Closes issue 594
    'Tier2/without-initial-soc'
]

TIER_1_SUBFOLDERS = [
    'Tier1/cropland-with-measured-soc',
    'Tier1/cropland-without-measured-soc',
    'Tier1/permanent-pasture',
    'Tier1/should-not-run',
    'Tier1/without-management-with-measured-soc',
    'Tier1/cropland-depth-as-float'
]

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

COVER_CROP_PROPERTY_TERM_IDS = [
    "catchCrop",
    "coverCrop",
    "groundCover",
    "longFallowCrop",
    "shortFallowCrop"
]

CROP_RESIDUE_INCORP_TERM_IDS = [
    "aboveGroundCropResidueIncorporated",
    "aboveGroundCropResidueLeftOnField",
    "belowGroundCropResidue",
    "discardedCropIncorporated",
    "discardedCropLeftOnField"
]

IRRIGATED_TERM_IDS = [
    "deepWater",
    "deepWaterWaterDepth100Cm",
    "deepWaterWaterDepth50100Cm",
    "irrigated",
    "irrigatedCenterPivotIrrigation",
    "irrigatedContinuouslyFlooded",
    "irrigatedDripIrrigation",
    "irrigatedFurrowIrrigation",
    "irrigatedLateralMoveIrrigation",
    "irrigatedLocalizedIrrigation",
    "irrigatedManualIrrigation",
    "irrigatedMultipleDrainagePeriods",
    "irrigatedSingleDrainagePeriod",
    "irrigatedSprinklerIrrigation",
    "irrigatedSubIrrigation",
    "irrigatedSurfaceIrrigation"
]

RESIDUE_REMOVED_OR_BURNT_TERM_IDS = [
    "residueBurnt",
    "residueBurntBeforeAllowingForCombustionFactor",
    "residueRemoved"
]

RICE_PLANT_UPLAND_TERM_IDS = [
    "ricePlantUpland"
]

# --- TIER 2 TEST UTILS ---


def _load_cycles(path):
    with open(path, encoding='utf-8') as f:
        cycles = json.load(f)
    return cycles


# --- TIER 1 TEST UTILS ---


def fake_measurement(
    term_id: str,
    value: list,
    term_type: TermTermType,
    properties: Optional[list[dict]] = None
):
    node = deepcopy(MEASUREMENT)
    node['term']['@id'] = term_id
    node['term']['termType'] = term_type.value
    node['value'] = (
        value if isinstance(value, list) else [value]
    )
    if properties:
        node['properties'] = (
            properties if isinstance(properties, list) else [properties]
        )
    return node


def fake_management(
    term_id: str,
    value: Union[float, bool],
    term_type: TermTermType,
    properties: Optional[list[dict]] = None
):
    node = deepcopy(MANAGEMENT)
    node['term']['@id'] = term_id
    node['term']['termType'] = term_type.value
    node['value'] = (
        value[0] if isinstance(value, list) else value
    )
    if properties:
        node['properties'] = (
            properties if isinstance(properties, list) else [properties]
        )
    return node


def fake_property(
    term_id: str,
    value: Union[float, bool],
):
    node = deepcopy(PROPERTY)
    node['term']['@id'] = term_id
    node['term']['termType'] = TermTermType.PROPERTY.value
    node['value'] = (
        value[0] if isinstance(value, list) else value
    )
    return node


Tier1SocStockFixtures = NamedTuple('Tier1SocStockFixtures', [
    ('timestamps', list[int]),
    ('soc_equilibriums', list[float]),
    ('expected', list[float])
])


# --- TIER 1 & TIER 2 TESTS ---


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_empty_site_and_cycles(*args):
    SITE = {}
    EXPECTED = []
    result = run(SITE)
    assert result == EXPECTED


# --- TIER 2 TESTS: SUB-MODELS ---


def test_calc_temperature_factor():
    NUM_RANDOM = 9999
    MIN_T, MAX_T = -60, 60
    MIN_FAC, MAX_FAC = 0, 1

    temperatures = [random.uniform(MIN_T, MAX_T) for _ in range(0, NUM_RANDOM)]
    results = [
        _calc_temperature_factor(t) for t in temperatures
    ]

    assert all(MIN_FAC <= result <= MAX_FAC for result in results)


def test_calc_water_factor():
    NUM_RANDOM = 9999
    MIN, MAX = 0, 9999
    MIN_FAC, MAX_FAC = 0.2129, 1.5
    IRR_FAC = 0.775

    precipitations = [random.uniform(MIN, MAX) for _ in range(0, NUM_RANDOM)]
    pets = [random.uniform(MIN, MAX) for _ in range(0, NUM_RANDOM)]

    results = [
        _calc_water_factor(pre, pet) for pre, pet in zip(precipitations, pets)
    ]
    irr_results = [
        _calc_water_factor(pre, pet, is_irrigated=True) for pre, pet in zip(precipitations, pets)
    ]

    assert all(MIN_FAC <= result <= MAX_FAC for result in results)
    assert all(result == IRR_FAC for result in irr_results)
    assert _calc_water_factor(1, 1) == _calc_water_factor(1000, 1000)


def test_run_annual_organic_carbon_inputs():
    """
    Test the _run_annual_organic_carbon_inputs model:

    As the IPCC don't provide any test data, we can generate some random inputs and test that the results
    fall within the minimum and maximum bounds.
    """
    NUM_YEARS = 9999
    MIN_SOURCES, MAX_SOURCES = 0, 99
    MIN_MASS, MAX_MASS = 0, 9999
    MIN_C, MAX_C = 0.1, 0.5
    MIN_N, MAX_N = 0.001, 0.01
    MIN_LIG, MAX_LIG = 0.01, 0.1

    min_c_input = MIN_MASS * MIN_C * MIN_SOURCES
    max_c_input = MAX_MASS * MAX_C * MAX_SOURCES

    def generate_random_carbon_sources():
        return [
            CarbonSource(
                mass=random.uniform(MIN_MASS, MAX_MASS),
                carbon_content=random.uniform(MIN_C, MAX_C),
                nitrogen_content=random.uniform(MIN_N, MAX_N),
                lignin_content=random.uniform(MIN_LIG, MAX_LIG)
            ) for _ in range(0, random.randint(MIN_SOURCES, MAX_SOURCES))
        ]

    timestamps = list(range(0, NUM_YEARS))
    annual_carbon_sources = [
        generate_random_carbon_sources() for _ in timestamps
    ]

    result = _run_annual_organic_carbon_inputs(
        timestamps,
        annual_carbon_sources
    )

    for i in range(0, NUM_YEARS):
        assert result.timestamps[i] == timestamps[i]
        assert min_c_input <= result.organic_carbon_inputs[i] <= max_c_input
        assert MIN_N <= result.average_nitrogen_contents[i] <= MAX_N
        assert MIN_LIG <= result.average_lignin_contents[i] <= MAX_LIG


# --- TIER 2 TESTS: SOC MODEL ---


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run_tier_2_with_generalised_monthly_measurements(mock_related_cycles, *args):
    """
    Test for sites with monthly climate measurements (e.g., `precipitationMonthly`) with dates in the format `--MM`.

    Tier 2 model should not run, as monthly climate measurements must be associated with a year and a month in the
    format `YYYY-MM`. Therefore, `run` function is expected to return an empty list `[]`.
    """

    SUBFOLDER = TIER_2_SUBFOLDERS[0]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    mock_related_cycles.return_value = _load_cycles(f"{folder}/cycles.jsonld")

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = run(site)
    assert result == []


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run_tier_2_with_incomplete_climate_data(mock_related_cycles, *args):

    SUBFOLDER = TIER_2_SUBFOLDERS[1]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    mock_related_cycles.return_value = _load_cycles(f"{folder}/cycles.jsonld")

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = run(site)
    assert result == []


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run_tier_2_with_initial_soc(mock_related_cycles, *args):

    SUBFOLDER = TIER_2_SUBFOLDERS[2]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    mock_related_cycles.return_value = _load_cycles(f"{folder}/cycles.jsonld")

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run_tier_2_with_multi_year_cycles(mock_related_cycles, *args):

    SUBFOLDER = TIER_2_SUBFOLDERS[3]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    mock_related_cycles.return_value = _load_cycles(f"{folder}/cycles.jsonld")

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run_tier_2_without_any_measurements(mock_related_cycles, *args):

    SUBFOLDER = TIER_2_SUBFOLDERS[4]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    mock_related_cycles.return_value = _load_cycles(f"{folder}/cycles.jsonld")

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = run(site)
    assert result == []


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run_tier_2_without_initial_soc(mock_related_cycles, *args):

    SUBFOLDER = TIER_2_SUBFOLDERS[5]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    mock_related_cycles.return_value = _load_cycles(f"{folder}/cycles.jsonld")

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


# --- IPCC SOIL CATEGORY TESTS ---


EXPECTED_IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_TERM_IDS = {
    IpccSoilCategory.ORGANIC_SOILS: 'histosol',
    IpccSoilCategory.SANDY_SOILS: 'arenosols',
    IpccSoilCategory.WETLAND_SOILS: 'gleysols',
    IpccSoilCategory.VOLCANIC_SOILS: 'andosols',
    IpccSoilCategory.SPODIC_SOILS: 'podzols',
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: 'alisols',
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: 'cryosols'
}

EXPECTED_IPCC_SOIL_CATEGORY_TO_USDA_SOIL_TYPE_TERM_IDS = {
    IpccSoilCategory.ORGANIC_SOILS: 'histosols',
    IpccSoilCategory.SANDY_SOILS: 'psamments',
    IpccSoilCategory.WETLAND_SOILS: 'aquicCalcixerepts',
    IpccSoilCategory.VOLCANIC_SOILS: 'andisols',
    IpccSoilCategory.SPODIC_SOILS: 'spodosols',
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: 'vertisols',
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: 'alfisols'
}


def test_assign_ipcc_soil_category_standard_cases():

    # soilType
    for expected, term_id in EXPECTED_IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_TERM_IDS.items():
        measurements = [
            fake_measurement(term_id, [100], TermTermType.SOILTYPE)
        ]
        result = _assign_ipcc_soil_category(measurements)

        assert result == expected

    # usdaSoilType
    for expected, term_id in EXPECTED_IPCC_SOIL_CATEGORY_TO_USDA_SOIL_TYPE_TERM_IDS.items():
        measurements = [
            fake_measurement(term_id, [100], TermTermType.USDASOILTYPE)
        ]
        result = _assign_ipcc_soil_category(measurements)

        assert result == expected


def test_assign_ipcc_soil_category_fractional_case():

    EXPECTED = IpccSoilCategory.WETLAND_SOILS
    USDA_SOIL_CATEGORY_TERM_IDS = [
        'aquicCalcixerepts',    # WET
        'aquicXeropsamments',   # WET
        'aquicFraglossudalfs',  # WET
        'vertisols'             # HAC
    ]

    measurements = [
        fake_measurement(term_id, [100/len(USDA_SOIL_CATEGORY_TERM_IDS)], TermTermType.USDASOILTYPE)
        for term_id in USDA_SOIL_CATEGORY_TERM_IDS
    ]
    result = _assign_ipcc_soil_category(measurements)

    assert result == EXPECTED


def test_assign_ipcc_soil_category_sandy_override_case():

    EXPECTED = IpccSoilCategory.SANDY_SOILS
    LAC_SOIL_TYPE_TERM_ID = (
        EXPECTED_IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_TERM_IDS[IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS]
    )

    # `soilType` and/or `usdaSoilType` overridden by sand and clay content
    measurements = [
            fake_measurement(LAC_SOIL_TYPE_TERM_ID, [100], TermTermType.SOILTYPE),
            fake_measurement(CLAY_CONTENT_TERM_ID, [CLAY_CONTENT_MAX-1], TermTermType.MEASUREMENT),
            fake_measurement(SAND_CONTENT_TERM_ID, [SAND_CONTENT_MIN+1], TermTermType.MEASUREMENT)
    ]
    result = _assign_ipcc_soil_category(measurements)

    assert result == EXPECTED


def test_assign_ipcc_soil_category_no_measurements_case():

    EXPECTED = IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS

    measurements = []
    result = _assign_ipcc_soil_category(measurements)

    assert result == EXPECTED


# --- IPCC LAND USE CATEGORY TESTS ---


EXPECTED_IPCC_LAND_USE_CATEGORY_TO_SITE_TYPE = {
    IpccLandUseCategory.GRASSLAND: SiteSiteType.PERMANENT_PASTURE.value,
    IpccLandUseCategory.FOREST: SiteSiteType.FOREST.value,
    IpccLandUseCategory.SET_ASIDE: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.NATIVE: SiteSiteType.OTHER_NATURAL_VEGETATION.value,
    IpccLandUseCategory.OTHER: SiteSiteType.AGRI_FOOD_PROCESSOR,
}

EXPECTED_IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_TERM_ID = {
    IpccLandUseCategory.PERENNIAL_CROPS: 'grapesVine',
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: 'ricePlantFlooded',
    IpccLandUseCategory.ANNUAL_CROPS: 'kalePlant',
}

SITE_TYPE_CROPLAND = SiteSiteType.CROPLAND.value
IPCC_SOIL_CATEGORY_LAC = IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS


@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
def test_assign_ipcc_land_use_category_standard_cases(*args):
    # site type only
    for expected, site_type in EXPECTED_IPCC_LAND_USE_CATEGORY_TO_SITE_TYPE.items():

        management_nodes = []
        result = _assign_ipcc_land_use_category(
            site_type,
            management_nodes,
            IPCC_SOIL_CATEGORY_LAC
        )

        assert result == expected

    # site type `cropland` and land cover
    for expected, term_id in EXPECTED_IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_TERM_ID.items():

        management_nodes = [
            fake_management(
                term_id,
                100,
                TermTermType.LANDCOVER
            )
        ]
        result = _assign_ipcc_land_use_category(
            SITE_TYPE_CROPLAND,
            management_nodes,
            IPCC_SOIL_CATEGORY_LAC
        )

        assert result == expected


@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
def test_assign_ipcc_land_use_category_fractional_case(*args):
    EXPECTED = IpccLandUseCategory.PERENNIAL_CROPS
    LAND_COVER_TERM_IDS = [
        'appleTree',        # PERENNIAL_CROPS
        'apricotTree',      # PERENNIAL_CROPS
        'wheatPlant',       # ANNUAL_CROPS
        'barleyPlant'       # ANNUAL_CROPS
    ]

    management_nodes = [
        fake_management(
            term_id, 100/len(LAND_COVER_TERM_IDS), TermTermType.LANDCOVER
        ) for term_id in LAND_COVER_TERM_IDS
    ]
    result = _assign_ipcc_land_use_category(
        SITE_TYPE_CROPLAND,
        management_nodes,
        IPCC_SOIL_CATEGORY_LAC
    )

    assert result == EXPECTED


@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
def test_assign_ipcc_land_use_category_annual_crops_wet_case(*args):
    EXPECTED = IpccLandUseCategory.ANNUAL_CROPS_WET
    IPCC_SOIL_CATEGORY_WET = IpccSoilCategory.WETLAND_SOILS

    management_nodes = [
        fake_management(
            EXPECTED_IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_TERM_ID[IpccLandUseCategory.ANNUAL_CROPS],
            100,
            TermTermType.LANDCOVER
        )
    ]

    result = _assign_ipcc_land_use_category(
        SITE_TYPE_CROPLAND,
        management_nodes,
        IPCC_SOIL_CATEGORY_WET
    )
    assert result == EXPECTED


@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
def test_assign_ipcc_land_use_category_set_aside_case(*args):
    EXPECTED = IpccLandUseCategory.SET_ASIDE
    WHITE_CLOVER_PLANT_TERM_ID = 'whiteCloverPlant'
    LONG_FALLOW_CROP_TERM_ID = 'longFallowCrop'

    management_nodes = [
        fake_management(
            WHITE_CLOVER_PLANT_TERM_ID,
            100,
            TermTermType.LANDCOVER,
            properties=[
                fake_property(
                    LONG_FALLOW_CROP_TERM_ID,
                    True
                )
            ]
        )
    ]

    result = _assign_ipcc_land_use_category(
        SITE_TYPE_CROPLAND,
        management_nodes,
        IPCC_SOIL_CATEGORY_LAC
    )

    assert result == EXPECTED


@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
def test_assign_ipcc_land_use_category_upland_rice_cases(*args):
    EXPECTED_IRRIGATED = IpccLandUseCategory.PADDY_RICE_CULTIVATION
    EXPECTED_NOT_IRRIGATED = IpccLandUseCategory.ANNUAL_CROPS

    RICE_PLANT_UPLAND_TERM_ID = 'ricePlantUpland'
    IRRIGATED_TERM_ID = 'irrigated'

    # Irrigated upland rice
    management_nodes_irrigated = [
        fake_management(
            RICE_PLANT_UPLAND_TERM_ID, 100, TermTermType.LANDCOVER
        ),
        fake_management(
            IRRIGATED_TERM_ID, 100, TermTermType.WATERREGIME
        )
    ]
    result_irrigated = _assign_ipcc_land_use_category(
        SITE_TYPE_CROPLAND,
        management_nodes_irrigated,
        IPCC_SOIL_CATEGORY_LAC
    )

    assert result_irrigated == EXPECTED_IRRIGATED

    # Not irrigated upland rice
    management_nodes_not_irrigated = [
        fake_management(
            RICE_PLANT_UPLAND_TERM_ID, 100, TermTermType.LANDCOVER
        )
    ]
    result_not_irrigated = _assign_ipcc_land_use_category(
        SITE_TYPE_CROPLAND,
        management_nodes_not_irrigated,
        IPCC_SOIL_CATEGORY_LAC
    )

    assert result_not_irrigated == EXPECTED_NOT_IRRIGATED


@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
def test_assign_ipcc_land_use_category_no_site_type_case(*args):
    EXPECTED = IpccLandUseCategory.OTHER
    SITE_TYPE = None
    MANAGEMENT_NODES = []

    result = _assign_ipcc_land_use_category(
        SITE_TYPE, MANAGEMENT_NODES, IPCC_SOIL_CATEGORY_LAC
    )

    assert result == EXPECTED


# --- IPCC MANAGEMENT CATEGORY TESTS ---


EXPECTED_IPCC_MANAGEMENT_CATEGORY_TO_LAND_COVER_TERM_ID = {
    IpccManagementCategory.SEVERELY_DEGRADED: 'severelyDegradedPasture',
    IpccManagementCategory.IMPROVED_GRASSLAND: 'improvedPasture',
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: 'highIntensityGrazingPasture',
    IpccManagementCategory.NOMINALLY_MANAGED: 'nominallyManagedPasture',
    IpccManagementCategory.OTHER: 'nativePasture'
}

EXPECTED_IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_TERM_ID = {
    IpccManagementCategory.FULL_TILLAGE: 'fullTillage',
    IpccManagementCategory.REDUCED_TILLAGE: 'minimumTillage',
    IpccManagementCategory.NO_TILLAGE: 'noTillage'
}


def test_assign_ipcc_management_category_standard_cases():

    # Grassland
    for expected, term_id in EXPECTED_IPCC_MANAGEMENT_CATEGORY_TO_LAND_COVER_TERM_ID.items():

        management_nodes = [
            fake_management(
                term_id,
                100,
                TermTermType.LANDCOVER
            )
        ]
        result = _assign_ipcc_management_category(
            management_nodes,
            IpccLandUseCategory.GRASSLAND
        )

        assert result == expected

    # Annual crops
    for expected, term_id in EXPECTED_IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_TERM_ID.items():

        management_nodes = [
            fake_management(term_id, 100, TermTermType.TILLAGE)
        ]
        result = _assign_ipcc_management_category(
            management_nodes,
            IpccLandUseCategory.ANNUAL_CROPS
        )

        assert result == expected

    # Annual crops wet
    for expected, term_id in EXPECTED_IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_TERM_ID.items():

        management_nodes = [
            fake_management(term_id, 100, TermTermType.TILLAGE)
        ]
        result = _assign_ipcc_management_category(
            management_nodes,
            IpccLandUseCategory.ANNUAL_CROPS_WET
        )

        assert result == expected


def test_assign_ipcc_management_fractional_cases():
    EXPECTED_GRASSLAND = IpccManagementCategory.IMPROVED_GRASSLAND
    LAND_COVER_TERM_IDS = [
        'severelyDegradedPasture',  # 25%
        'improvedPasture',          # 25%
        'improvedPasture',          # 25%
        'nativePasture'             # 25%
    ]

    EXPECTED_CROPLAND = IpccManagementCategory.REDUCED_TILLAGE
    TILLAGE_TERM_IDS = [
        'fullTillage',              # 25%
        'mulchTillage',             # 25%
        'stripTillage',             # 25%
        'noTillage'                 # 25%
    ]

    # Grassland
    management_nodes_grassland = [
        fake_management(
            term_id,
            100/len(LAND_COVER_TERM_IDS),
            TermTermType.LANDCOVER
            )
        for term_id in LAND_COVER_TERM_IDS
    ]
    result_grassland = _assign_ipcc_management_category(
        management_nodes_grassland,
        IpccLandUseCategory.GRASSLAND
    )

    assert result_grassland == EXPECTED_GRASSLAND

    # Annual crops
    management_nodes_cropland = [
        fake_management(
            term_id,
            100/len(TILLAGE_TERM_IDS),
            TermTermType.TILLAGE
            )
        for term_id in TILLAGE_TERM_IDS
    ]
    result_cropland = _assign_ipcc_management_category(
        management_nodes_cropland,
        IpccLandUseCategory.ANNUAL_CROPS
    )

    assert result_cropland == EXPECTED_CROPLAND


def test_assign_ipcc_management_category_no_management_cases():

    EXPECTED_GRASSLAND = IpccManagementCategory.NOMINALLY_MANAGED
    EXPECTED_CROPLAND = IpccManagementCategory.FULL_TILLAGE
    MANAGEMENT_NODES = []

    result_grassland = _assign_ipcc_management_category(
        MANAGEMENT_NODES, IpccLandUseCategory.GRASSLAND
    )

    assert result_grassland == EXPECTED_GRASSLAND

    result_cropland = _assign_ipcc_management_category(
        MANAGEMENT_NODES, IpccLandUseCategory.ANNUAL_CROPS
    )

    assert result_cropland == EXPECTED_CROPLAND


# --- IPCC CARBON INPUT CATEGORY TESTS ---

ANIMAL_MANURE_USED_NODE = fake_management(
    'animalManureUsed', True, TermTermType.LANDUSEMANAGEMENT
)

BROCCOLI_PLANT_NODE = fake_management(
    'broccoliPlant', 100, TermTermType.LANDCOVER
)

COMMON_BEAN_PLANT_NODE = fake_management(
    'commonBeanPlant', 100, TermTermType.LANDCOVER
)

CLOVER_PLANT_NODE = fake_management(
    'cloverPlant', 100, TermTermType.LANDCOVER
)

IRRIGATED_NODE = fake_management(
    'irrigated', 100, TermTermType.WATERREGIME
)

INORGANIC_NITROGEN_FERTILISER_USED_NODE = fake_management(
    'inorganicNitrogenFertiliserUsed', True, TermTermType.LANDUSEMANAGEMENT
)

MULCHING_NODE = fake_management(
    'mulching', 100, TermTermType.LANDUSEMANAGEMENT
)

ORGANIC_FERTILISER_USED_NODE = fake_management(
    'organicFertiliserOrSoilCarbonIncreasingAmendmentUsed',
    100,
    TermTermType.LANDUSEMANAGEMENT
)

RESIDUE_REMOVED_NODE = fake_management(
    'residueRemoved', 100, TermTermType.CROPRESIDUEMANAGEMENT
)

SHORT_BARE_FALLOW_NODE = fake_management(
    'shortBareFallow', 100, TermTermType.LANDUSEMANAGEMENT
)

RYEGRASS_PLANT_AS_COVER_CROP_NODE = fake_management(
    'ryegrassPlant', 100, TermTermType.LANDCOVER,
    properties=[
        fake_property(
            'coverCrop',
            True
        )
    ]
)

WHEAT_PLANT_NODE = fake_management(
    'wheatPlant', 100, TermTermType.LANDCOVER
)


@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_check_cropland_high_with_manure_category(*args):
    IPCC_CARBON_INPUT_CATEGORY = IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE
    EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES = {
        1: [
            COMMON_BEAN_PLANT_NODE,  # N-fixing crop
            ANIMAL_MANURE_USED_NODE
        ]
    }

    for expected, management_nodes in EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES.items():
        carbon_input_args = _make_carbon_input_args(management_nodes)
        result = _check_cropland_high_with_manure_category(
            carbon_input_args,
            key=IPCC_CARBON_INPUT_CATEGORY
        )

        assert result == expected
    pass


@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_check_cropland_high_without_manure_category(*args):
    IPCC_CARBON_INPUT_CATEGORY = IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE
    EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES = {
        1: [
            WHEAT_PLANT_NODE,  # Non-N-fixing & high-residue-producing crop
            INORGANIC_NITROGEN_FERTILISER_USED_NODE,
            ORGANIC_FERTILISER_USED_NODE
        ]
    }

    for expected, management_nodes in EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES.items():
        carbon_input_args = _make_carbon_input_args(management_nodes)
        result = _check_cropland_high_without_manure_category(
            carbon_input_args,
            key=IPCC_CARBON_INPUT_CATEGORY
        )

        assert result == expected


@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_check_cropland_medium_category(*args):
    IPCC_CARBON_INPUT_CATEGORY = IpccCarbonInputCategory.CROPLAND_MEDIUM
    EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES = {
        1: [
            WHEAT_PLANT_NODE,  # Non-N-fixing & high-residue-producing crop
            RESIDUE_REMOVED_NODE,
            ANIMAL_MANURE_USED_NODE
        ],
        2: [
            BROCCOLI_PLANT_NODE,  # Low-residue-producing crop
            IRRIGATED_NODE
        ],
        3: [
            WHEAT_PLANT_NODE,  # Non-N-fixing & high-residue-producing crop
            RYEGRASS_PLANT_AS_COVER_CROP_NODE  # Practice increasing C input
        ],
        4: [
            COMMON_BEAN_PLANT_NODE  # N-fixing crop
        ]
    }

    for expected, management_nodes in EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES.items():
        carbon_input_args = _make_carbon_input_args(management_nodes)
        result = _check_cropland_medium_category(
            carbon_input_args,
            key=IPCC_CARBON_INPUT_CATEGORY
        )

        assert result == expected


@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_check_cropland_low_category(*args):
    IPCC_CARBON_INPUT_CATEGORY = IpccCarbonInputCategory.CROPLAND_LOW
    EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES = {
        1: [
            WHEAT_PLANT_NODE,  # Non-N-fixing & high-residue-producing crop
            RESIDUE_REMOVED_NODE
        ],
        2: [
            WHEAT_PLANT_NODE,  # Low-residue-producing crop
            SHORT_BARE_FALLOW_NODE
        ],
        3: [],
    }

    for expected, management_nodes in EXPECTED_CONDITION_KEY_TO_MANAGEMENT_NODES.items():
        carbon_input_args = _make_carbon_input_args(management_nodes)
        result = _check_cropland_low_category(
            carbon_input_args,
            key=IPCC_CARBON_INPUT_CATEGORY
        )
        assert result == expected


@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_assign_ipcc_carbon_input_category_grassland_cases(*args):
    GRASSLAND_CARBON_INPUT_CATEGORY_MANAGEMENT_FIXTURES_GROUPED = {
        IpccCarbonInputCategory.GRASSLAND_HIGH: [
            [
                IRRIGATED_NODE,
                INORGANIC_NITROGEN_FERTILISER_USED_NODE
            ],
            [
                MULCHING_NODE,
                CLOVER_PLANT_NODE
            ]
        ],
        IpccCarbonInputCategory.GRASSLAND_MEDIUM: [
            [
                ORGANIC_FERTILISER_USED_NODE
            ],
            [
                CLOVER_PLANT_NODE
            ]
        ]
    }

    for expected, management_node_groups in GRASSLAND_CARBON_INPUT_CATEGORY_MANAGEMENT_FIXTURES_GROUPED.items():
        for management_nodes in management_node_groups:

            result = _assign_ipcc_carbon_input_category(
                management_nodes,
                IpccManagementCategory.IMPROVED_GRASSLAND
            )

            assert result == expected


# --- TIER 1 TESTS ---


def test_run_tier_1_soc_stocks():
    IPCC_TIMESTAMPS = [1990, 1995, 2000, 2005, 2010, 2015, 2020]

    IPCC_TIER_1_SOC_STOCK_FIXTURES = [
        # Land unit 1
        Tier1SocStockFixtures(
            timestamps=IPCC_TIMESTAMPS,
            soc_equilibriums=[
                77.000, 70.840, 70.840, 70.840, 70.840, 70.840, 70.840
            ],
            expected=[
                77.000, 75.460, 73.920, 72.380, 70.840, 70.840, 70.840
            ]
        ),
        # Land unit 2
        Tier1SocStockFixtures(
            timestamps=IPCC_TIMESTAMPS,
            soc_equilibriums=[
                77.000, 70.840, 70.840, 70.840, 80.850, 80.850, 80.850
            ],
            expected=[
                77.000, 75.460, 73.920, 72.380, 74.498, 76.615, 78.733
            ]
        ),
        # Land unit 3
        Tier1SocStockFixtures(
            timestamps=IPCC_TIMESTAMPS,
            soc_equilibriums=[
                80.850, 70.840, 70.840, 70.840, 70.840, 80.850, 80.850
            ],
            expected=[
                80.850, 78.348, 75.845, 73.343, 70.840, 73.343, 75.845
            ]
        ),
        # Land unit 4
        Tier1SocStockFixtures(
            timestamps=IPCC_TIMESTAMPS,
            soc_equilibriums=[
                80.850, 80.850, 77.000, 77.000, 77.000, 77.000, 77.000
            ],
            expected=[
                80.850, 80.850, 79.888, 78.925, 77.963, 77.000, 77.000
            ]
        ),
        # Land unit 5
        Tier1SocStockFixtures(
            timestamps=IPCC_TIMESTAMPS,
            soc_equilibriums=[
                70.840, 70.840, 70.840, 70.840, 80.850, 80.850, 80.850
            ],
            expected=[
                70.840, 70.840, 70.840, 70.840, 73.343, 75.845, 78.348
            ]
        ),
        # Land unit 6
        Tier1SocStockFixtures(
            timestamps=IPCC_TIMESTAMPS,
            soc_equilibriums=[
                70.840, 70.840, 80.850, 80.850, 80.850, 70.840, 80.850
            ],
            expected=[
                70.840, 70.840, 73.343, 75.845, 78.348, 76.471, 77.565
            ]
        )
    ]

    for fixture in IPCC_TIER_1_SOC_STOCK_FIXTURES:
        result = _calc_tier_1_soc_stocks(
            fixture.timestamps, fixture.soc_equilibriums
        )
        assert_almost_equal(result, fixture.expected, decimal=3)


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_tier_1_cropland_with_measured_soc(*args):
    SUBFOLDER = TIER_1_SUBFOLDERS[0]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_tier_1_cropland_without_measured_soc(*args):

    SUBFOLDER = TIER_1_SUBFOLDERS[1]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_tier_1_permanent_pasture(*args):

    SUBFOLDER = TIER_1_SUBFOLDERS[2]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_tier_1_should_not_run(*args):

    SUBFOLDER = TIER_1_SUBFOLDERS[3]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = run(site)
    assert result == []


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_tier_1_without_management_with_measured_soc(*args):
    """
    This is to test for Sites with measured SOC stock values but no management nodes.
    The model should not run but should not raise errors either.
    """

    SUBFOLDER = TIER_1_SUBFOLDERS[4]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = run(site)
    assert result == []


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_rice_plant_upland_terms", return_value=RICE_PLANT_UPLAND_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_tier_1_cropland_depth_as_float(*args):
    SUBFOLDER = TIER_1_SUBFOLDERS[5]
    folder = f"{fixtures_folder}/{SUBFOLDER}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    print(json.dumps(result, indent=2))
    assert result == expected
