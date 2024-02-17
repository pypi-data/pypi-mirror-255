"""
The IPCC model for estimating soil organic carbon stock changes in the 0 - 30cm depth interval due to management
changes. This model combines the Tier 1 & Tier 2 methodologies. It first tries to run Tier 2 (only on croplands
remaining croplands). If Tier 2 cannot run, it will try to run Tier 1 (for croplands remaining croplands and for
grasslands remaining grasslands). Source:
[IPCC 2019, Vol. 4, Chapter 10](https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch05_Cropland.pdf).

Currently, the Tier 2 implementation does not take into account the irrigation of cycles when estimating soil organic
carbon stock changes.
"""
from collections.abc import Iterable
from enum import Enum
from functools import reduce
from numpy import exp
from pydash.objects import merge
from statistics import mean
from typing import (
    Any,
    NamedTuple,
    Optional,
    Union
)
from hestia_earth.schema import (
    MeasurementMethodClassification,
    SiteSiteType,
    TermTermType
)
from hestia_earth.utils.date import diff_in_years
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list, safe_parse_date

from hestia_earth.models.log import logShouldRun, log_as_table
from hestia_earth.models.utils.blank_node import (
    cumulative_nodes_match,
    cumulative_nodes_lookup_match,
    cumulative_nodes_term_match,
    get_node_value,
    group_nodes_by_year,
    node_lookup_match,
    node_term_match
)
from hestia_earth.models.utils.cycle import check_cycle_site_ids_identical
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from hestia_earth.models.utils.measurement import (
    _new_measurement,
    group_measurement_values_by_year,
    most_relevant_measurement_value_by_depth_and_date
)
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.term import (
    get_cover_crop_property_terms,
    get_crop_residue_incorporated_or_left_on_field_terms,
    get_irrigated_terms,
    get_residue_removed_or_burnt_terms,
    get_rice_plant_upland_terms
)

from . import MODEL

REQUIREMENTS = {
    "Site": {
        "siteType": ["cropland", "permanent pasture", "forest", "other natural vegetation"],
        "measurements": [
            {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
        ],
        "optional": {
            "measurements": [
                {"@type": "Measurement", "value": "", "term.termType": ["soilType", "usdaSoilType"]}
            ],
            "management": [
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "cropResidueManagement",
                    "name": ["burnt", "removed"]
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.termType": "landCover"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "landUseManagement"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.termType": "tillage"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "waterRegime",
                    "name": ["irrigated", "deep water"]
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "animalManureUsed"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "inorganicNitrogenFertiliserUsed"
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "shortBareFallow"}
            ]
        }
    }
}
LOOKUPS = {
    "ecoClimateZone": [
        "IPCC_2019_SOC_REF_KG_C_HECTARE_SAN",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_WET",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_VOL",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_POD",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_HAC",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_LAC",
        "IPCC_2019_LANDUSE_FACTOR_GRASSLAND",
        "IPCC_2019_LANDUSE_FACTOR_PERENNIAL_CROPS",
        "IPCC_2019_LANDUSE_FACTOR_PADDY_RICE_CULTIVATION",
        "IPCC_2019_LANDUSE_FACTOR_ANNUAL_CROPS_WET",
        "IPCC_2019_LANDUSE_FACTOR_ANNUAL_CROPS",
        "IPCC_2019_LANDUSE_FACTOR_SET_ASIDE",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_SEVERELY_DEGRADED",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_IMPROVED_GRASSLAND",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_HIGH_INTENSITY_GRAZING",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_NOMINALLY_MANAGED",
        "IPCC_2019_TILLAGE_MANAGEMENT_FACTOR_FULL_TILLAGE",
        "IPCC_2019_TILLAGE_MANAGEMENT_FACTOR_REDUCED_TILLAGE",
        "IPCC_2019_TILLAGE_MANAGEMENT_FACTOR_NO_TILLAGE",
        "IPCC_2019_GRASSLAND_CARBON_INPUT_FACTOR_HIGH",
        "IPCC_2019_GRASSLAND_CARBON_INPUT_FACTOR_MEDIUM",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_HIGH_WITH_MANURE",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_HIGH_WITHOUT_MANURE",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_MEDIUM",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_LOW"
    ],
    "landCover": [
        "IPCC_LAND_USE_CATEGORY",
        "LOW_RESIDUE_PRODUCING_CROP",
        "N_FIXING_CROP"
    ],
    "landUseManagement": "PRACTICE_INCREASING_C_INPUT",
    "soilType": "IPCC_SOIL_CATEGORY",
    "tillage": "IPCC_TILLAGE_MANAGEMENT_CATEGORY",
    "usdaSoilType": "IPCC_SOIL_CATEGORY"
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "dates": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": ""
    }]
}

TERM_ID = 'organicCarbonPerHa'

# --- SHARED TIER 1 & TIER 2 CONSTANTS ---

MIN_AREA_THRESHOLD = 30  # 30% as per IPCC guidelines
SUPER_MAJORITY_AREA_THRESHOLD = 100 - MIN_AREA_THRESHOLD
DEPTH_UPPER = 0
DEPTH_LOWER = 30

# --- TIER 2 CONSTANTS ---

NUMBER_OF_TILLAGES_TERM_ID = "numberOfTillages"
TEMPERATURE_MONTHLY_TERM_ID = "temperatureMonthly"
PRECIPITATION_MONTHLY_TERM_ID = "precipitationMonthly"
PET_MONTHLY_TERM_ID = "potentialEvapotranspirationMonthly"
SAND_CONTENT_TERM_ID = "sandContent"
CARBON_CONTENT_TERM_ID = "carbonContent"
NITROGEN_CONTENT_TERM_ID = "nitrogenContent"
LIGNIN_CONTENT_TERM_ID = "ligninContent"

CROP_RESIDUE_PROPERTY_TERM_IDS = [
    CARBON_CONTENT_TERM_ID,
    NITROGEN_CONTENT_TERM_ID,
    LIGNIN_CONTENT_TERM_ID
]

CARBON_SOURCE_TERM_TYPES = [
    TermTermType.ORGANICFERTILISER.value,
    TermTermType.SOILAMENDMENT.value,
    TermTermType.SEED.value
]

MIN_RUN_IN_PERIOD = 5

DEFAULT_PARAMS = {
    "active_decay_factor": 7.4,
    "slow_decay_factor": 0.209,
    "passive_decay_factor": 0.00689,
    "f_1": 0.378,
    "f_2_full_tillage": 0.455,
    "f_2_reduced_tillage": 0.477,
    "f_2_no_tillage": 0.5,
    "f_2_unknown_tillage": 0.368,
    "f_3": 0.455,
    "f_5": 0.0855,
    "f_6": 0.0504,
    "f_7": 0.42,
    "f_8": 0.45,
    "tillage_factor_full_tillage": 3.036,
    "tillage_factor_reduced_tillage": 2.075,
    "tillage_factor_no_tillage": 1,
    "maximum_temperature": 45,
    "optimum_temperature": 33.69,
    "water_factor_slope": 1.331,
    "default_carbon_content": 0.42,
    "default_nitrogen_content": 0.0085,
    "default_lignin_content": 0.073
}

# --- TIER 1 CONSTANTS ---

CLAY_CONTENT_TERM_ID = "clayContent"
LONG_FALLOW_CROP_TERM_ID = "longFallowCrop"
IMPROVED_PASTURE_TERM_ID = "improvedPasture"
SHORT_BARE_FALLOW_TERM_ID = "shortBareFallow"
ANIMAL_MANURE_USED_TERM_ID = "animalManureUsed"
INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID = "inorganicNitrogenFertiliserUsed"
ORGANIC_FERTILISER_USED_TERM_ID = "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed"

DEFAULT_NODE_VALUE = 100

CLAY_CONTENT_MAX = 8
SAND_CONTENT_MIN = 70

EQUILIBRIUM_TRANSITION_PERIOD = 20
"""
The number of years required for soil organic carbon to reach equilibrium after
a change in land use, management regime or carbon input regime.
"""

# --- SHARED TIER 1 & TIER 2 FORMAT MEASUREMENT OUTPUT ---


def _measurement(year: int, value: float, method_classification: str) -> dict:
    """
    Build a Hestia `Measurement` node to contain a value calculated by the models.

    Parameters
    ----------
    year : int
        The year that the value is associated with.
    value : float
        The value calculated by either the Tier 1 or Tier 2 model.
    method_classification :str
        The method tier used to calculate the value, either `tier 1 model` or `tier 2 model`.

    Returns
    -------
    dict
        A valid Hestia `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    """
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement["value"] = [value]
    measurement["dates"] = [f"{year}-12-31"]
    measurement["depthUpper"] = DEPTH_UPPER
    measurement["depthLower"] = DEPTH_LOWER
    measurement["methodClassification"] = method_classification
    return measurement


# --- SHARED TIER 1 & TIER 2 ENUMS ---


IpccManagementCategory = Enum("IpccManagementCategory", [
    "SEVERELY_DEGRADED",
    "IMPROVED_GRASSLAND",
    "HIGH_INTENSITY_GRAZING",
    "NOMINALLY_MANAGED",
    "FULL_TILLAGE",
    "REDUCED_TILLAGE",
    "NO_TILLAGE",
    "OTHER"
])
"""
Enum representing IPCC Management Categories for grasslands and annual
croplands.

See [IPCC (2019) Vol. 4, Ch. 5 and 6](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.
"""


# --- TIER 2 ENUMS ---


_InnerKey = Enum(
    "_InnerKey",
    [
        "TEMPERATURES",
        "PRECIPITATIONS",
        "PETS",
        "IS_IRRIGATEDS",
        "CARBON_SOURCES",
        "TILLAGE_CATEGORY"
    ],
)


INNER_KEYS_RUN_WITH_IRRIGATION = [
    _InnerKey.TEMPERATURES,
    _InnerKey.PRECIPITATIONS,
    _InnerKey.PETS,
    _InnerKey.IS_IRRIGATEDS,
    _InnerKey.CARBON_SOURCES,
    _InnerKey.TILLAGE_CATEGORY,
]

INNER_KEYS_RUN_WITHOUT_IRRIGATION = [
    _InnerKey.TEMPERATURES,
    _InnerKey.PRECIPITATIONS,
    _InnerKey.PETS,
    _InnerKey.CARBON_SOURCES,
    _InnerKey.TILLAGE_CATEGORY,
]


# --- TIER 1 ENUMS ---


IpccSoilCategory = Enum("IpccSoilCategory", [
    "ORGANIC_SOILS",
    "SANDY_SOILS",
    "WETLAND_SOILS",
    "VOLCANIC_SOILS",
    "SPODIC_SOILS",
    "HIGH_ACTIVITY_CLAY_SOILS",
    "LOW_ACTIVITY_CLAY_SOILS",
])
"""
Enum representing IPCC Soil Categories.

See [IPCC (2019) Vol 4, Ch. 2 and 3](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.
"""


IpccLandUseCategory = Enum("IpccLandUseCategory", [
    "GRASSLAND",
    "PERENNIAL_CROPS",
    "PADDY_RICE_CULTIVATION",
    "ANNUAL_CROPS_WET",
    "ANNUAL_CROPS",
    "SET_ASIDE",
    "FOREST",
    "NATIVE",
    "OTHER"
])
"""
Enum representing IPCC Land Use Categories.

See [IPCC (2019) Vol 4](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.
"""


IpccCarbonInputCategory = Enum("IpccCarbonInputCategory", [
    "GRASSLAND_HIGH",
    "GRASSLAND_MEDIUM",
    "CROPLAND_HIGH_WITH_MANURE",
    "CROPLAND_HIGH_WITHOUT_MANURE",
    "CROPLAND_MEDIUM",
    "CROPLAND_LOW",
    "OTHER"
])
"""
Enum representing IPCC Carbon Input Categories for improved grasslands
and annual croplands.

See [IPCC (2019) Vol. 4, Ch. 4, 5 and 6](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html)
for more information.
"""


# --- TIER 2 NAMED TUPLES FOR CARBON SOURCES AND MODEL RESULTS ---


CarbonSource = NamedTuple(
    "CarbonSource",
    [
        ("mass", float),
        ("carbon_content", float),
        ("nitrogen_content", float),
        ("lignin_content", float),
    ]
)
"""
A single carbon source (e.g. crop residues or organic amendment).

Attributes
-----------
mass : float
    The dry-matter mass of the carbon source, kg ha-1
carbon_content : float
    The carbon content of the carbon source, decimal proportion, kg C (kg d.m.)-1.
nitrogen_content : float
    The nitrogen content of the carbon source, decimal_proportion, kg N (kg d.m.)-1.
lignin_content : float
    The lignin content of the carbon source, decimal_proportion, kg lignin (kg d.m.)-1.
"""


TemperatureFactorResult = NamedTuple(
    "TemperatureFactorResult",
    [
        ("timestamps", list[float]),
        ("annual_temperature_factors", list[float])
    ]
)
"""
A named tuple to hold the result of `_run_annual_temperature_factors`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
annual_temperature_factors : list[float]
    A list of annual temperature factors for each year in the inventory, dimensionless, between `0` and `1`.
"""


WaterFactorResult = NamedTuple(
    "WaterFactorResult",
    [
        ("timestamps", list[float]),
        ("annual_water_factors", list[float])
    ]
)
"""
A named tuple to hold the result of `_run_annual_water_factors`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
annual_water_factors : list[float]
    A list of annual water factors for each year in the inventory, dimensionless, between `0.31935` and `2.25`.
"""


CarbonInputResult = NamedTuple(
    "CarbonInputResult",
    [
        ("timestamps", list[float]),
        ("organic_carbon_inputs", list[float]),
        ("average_nitrogen_contents", list[float]),
        ("average_lignin_contents", list[float]),
    ]
)
"""
A named tuple to hold the result of `_run_annual_organic_carbon_inputs`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
organic_carbon_inputs : list[float]
    A list of organic carbon inputs to the soil for each year in the inventory, kg C ha-1.
average_nitrogen_contents : list[float]
    A list of the average nitrogen contents of the carbon sources for each year in the inventory, decimal_proportion,
    kg N (kg d.m.)-1.
average_lignin_contents : list[float]
    A list of the average lignin contents of the carbon sources for each year in the inventory, decimal_proportion,
    kg lignin (kg d.m.)-1.
"""


Tier2SocResult = NamedTuple(
    "Tier2SocResult",
    [
        ("timestamps", list[float]),
        ("active_pool_soc_stocks", list[float]),
        ("slow_pool_soc_stocks", list[float]),
        ("passive_pool_soc_stocks", list[float]),
    ]
)
"""
A named tuple to hold the result of `_run_soc_stocks`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
active_pool_soc_stocks : list[float]
    The active sub-pool SOC stock for each year in the inventory, kg C ha-1.
slow_pool_soc_stocks : list[float]
    The slow sub-pool SOC stock for each year in the inventory, kg C ha-1.
passive_pool_soc_stocks : list[float]
    The passive sub-pool SOC stock for each year in the inventory, kg C ha-1.
"""


# --- TIER 1 NAMED TUPLES FOR STOCK CHANGE FACTORS AND MODEL RESULTS ---


StockChangeFactors = NamedTuple("StockChangeFactors", [
    ("land_use_factor", float),
    ("management_factor", float),
    ("carbon_input_factor", float)
])
"""
A named tuple to hold the 3 stock change factors retrieved by the model for each year in the inventory.

Attributes
----------
land_use_factor : float
    The stock change factor for mineral soil organic C land-use systems or sub-systems for a particular land-use,
    dimensionless.
management_factor : float
    The stock change factor for mineral soil organic C for management regime, dimensionless.
carbon_input_factor : float
    The stock change factor for mineral soil organic C for the input of organic amendments, dimensionless.
"""

CarbonInputArgs = NamedTuple("CarbonInputArgs", [
    ("num_grassland_improvements", int),
    ("has_irrigation", bool),
    ("has_residue_removed_or_burnt", bool),
    ("has_low_residue_producing_crops", bool),
    ("has_bare_fallow", bool),
    ("has_n_fixing_crop_or_inorganic_n_fertiliser_used", bool),
    ("has_practice_increasing_c_input", bool),
    ("has_cover_crop", bool),
    ("has_organic_fertiliser_or_soil_amendment_used", bool),
    ("has_animal_manure_used", bool)
])
"""
Named tuple representing the arguments for the functions assigning `IpccCarbonInputCategories` to inventory years.

Attributes
----------
num_grassland_improvements : int
    The number of grassland improvements.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
"""


# --- SHARED TIER 1 & TIER 2 MAPPING DICTS ---


IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE = {
    IpccManagementCategory.FULL_TILLAGE: "Full tillage",
    IpccManagementCategory.REDUCED_TILLAGE: "Reduced tillage",
    IpccManagementCategory.NO_TILLAGE: "No tillage"
}
"""
A dictionary mapping IPCC management categories to corresponding tillage lookup values in the
`"IPCC_TILLAGE_MANAGEMENT_CATEGORY" column`.
"""


# --- TIER 1 MAPPING DICTS ---


IPCC_CATEGORY_TO_ECO_CLIMATE_ZONE_LOOKUP_COLUMN = {
    # IpccSoilCategory
    IpccSoilCategory.SANDY_SOILS: LOOKUPS["ecoClimateZone"][0],
    IpccSoilCategory.WETLAND_SOILS: LOOKUPS["ecoClimateZone"][1],
    IpccSoilCategory.VOLCANIC_SOILS: LOOKUPS["ecoClimateZone"][2],
    IpccSoilCategory.SPODIC_SOILS: LOOKUPS["ecoClimateZone"][3],
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: LOOKUPS["ecoClimateZone"][4],
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: LOOKUPS["ecoClimateZone"][5],
    # IpccLandUseCategory
    IpccLandUseCategory.GRASSLAND: LOOKUPS["ecoClimateZone"][6],
    IpccLandUseCategory.PERENNIAL_CROPS: LOOKUPS["ecoClimateZone"][7],
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: LOOKUPS["ecoClimateZone"][8],
    IpccLandUseCategory.ANNUAL_CROPS_WET: LOOKUPS["ecoClimateZone"][9],
    IpccLandUseCategory.ANNUAL_CROPS: LOOKUPS["ecoClimateZone"][10],
    IpccLandUseCategory.SET_ASIDE: LOOKUPS["ecoClimateZone"][11],
    # IpccManagementCategory
    IpccManagementCategory.SEVERELY_DEGRADED: LOOKUPS["ecoClimateZone"][12],
    IpccManagementCategory.IMPROVED_GRASSLAND: LOOKUPS["ecoClimateZone"][13],
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: LOOKUPS["ecoClimateZone"][14],
    IpccManagementCategory.NOMINALLY_MANAGED: LOOKUPS["ecoClimateZone"][15],
    IpccManagementCategory.FULL_TILLAGE: LOOKUPS["ecoClimateZone"][16],
    IpccManagementCategory.REDUCED_TILLAGE: LOOKUPS["ecoClimateZone"][17],
    IpccManagementCategory.NO_TILLAGE: LOOKUPS["ecoClimateZone"][18],
    # IpccCarbonInputCategory
    IpccCarbonInputCategory.GRASSLAND_HIGH: LOOKUPS["ecoClimateZone"][19],
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: LOOKUPS["ecoClimateZone"][20],
    IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE: LOOKUPS["ecoClimateZone"][21],
    IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE: LOOKUPS["ecoClimateZone"][22],
    IpccCarbonInputCategory.CROPLAND_MEDIUM: LOOKUPS["ecoClimateZone"][23],
    IpccCarbonInputCategory.CROPLAND_LOW: LOOKUPS["ecoClimateZone"][24]
}
"""
A dictionary mapping IPCC category enums to their corresponding eco-climate zone lookup columns.
"""


def _get_eco_climate_zone_lookup_column(
    ipcc_category: Union[
        IpccSoilCategory,
        IpccLandUseCategory,
        IpccManagementCategory,
        IpccCarbonInputCategory
    ]
) -> Optional[str]:
    """
    Retrieve the corresponding eco-climate zone lookup column for the given IPCC category.

    Parameters
    ----------
    ipcc_category : IpccSoilCategory | IpccLandUseCategory | IpccManagementCategory | IpccCarbonInputCategory
        The IPCC category for which the eco-climate zone lookup column is needed.

    Returns
    -------
    str | None
        The eco-climate zone lookup column associated with the provided
        IPCC category, or None if no mapping is found.
    """
    return IPCC_CATEGORY_TO_ECO_CLIMATE_ZONE_LOOKUP_COLUMN.get(ipcc_category, None)


IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE = {
    IpccSoilCategory.ORGANIC_SOILS: "Organic soils",
    IpccSoilCategory.SANDY_SOILS: "Sandy soils",
    IpccSoilCategory.WETLAND_SOILS: "Wetland soils",
    IpccSoilCategory.VOLCANIC_SOILS: "Volcanic soils",
    IpccSoilCategory.SPODIC_SOILS: "Spodic soils",
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: "High-activity clay soils",
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: "Low-activity clay soils",
}
"""
A dictionary mapping IPCC soil categories to corresponding soil type and USDA soil type lookup values
in the `"IPCC_SOIL_CATEGORY"` column.
"""

IPCC_LAND_USE_CATEGORY_TO_SITE_TYPE = {
    IpccLandUseCategory.GRASSLAND: SiteSiteType.PERMANENT_PASTURE.value,
    IpccLandUseCategory.PERENNIAL_CROPS: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.ANNUAL_CROPS_WET: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.ANNUAL_CROPS: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.SET_ASIDE: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.FOREST: SiteSiteType.FOREST.value,
    IpccLandUseCategory.NATIVE: SiteSiteType.OTHER_NATURAL_VEGETATION.value
}
"""
A dictionary mapping IPCC land use categories to corresponding site types.
"""

IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE = {
    IpccLandUseCategory.PERENNIAL_CROPS: "Perennial crops",
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: "Paddy rice cultivation",
    IpccLandUseCategory.ANNUAL_CROPS_WET: "Annual crops",
    IpccLandUseCategory.ANNUAL_CROPS: "Annual crops"
}
"""
A dictionary mapping IPCC land use categories to corresponding land cover lookup values
in the `"IPCC_LAND_USE_CATEGORY"` column.
"""

IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID = {
    IpccManagementCategory.SEVERELY_DEGRADED: "severelyDegradedPasture",
    IpccManagementCategory.IMPROVED_GRASSLAND: "improvedPasture",
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: "highIntensityGrazingPasture",
    IpccManagementCategory.NOMINALLY_MANAGED: "nominallyManagedPasture",
    IpccManagementCategory.OTHER: "nativePasture"
}
"""
A dictionary mapping IPCC management categories to corresponding grassland management term IDs from the
land cover glossary.
"""


# --- TIER 2 FUNCTIONS: ASSIGN TILLAGE CATEGORY TO CYCLES ---


def _check_zero_tillages(practices: list[dict]) -> bool:
    """
    Checks whether a list of `Practice`s nodes describe 0 total tillages, or not.

    Parameters
    ----------
    practices : list[dict]
        A list of Hestia `Practice` nodes, see: https://www.hestia.earth/schema/Practice.

    Returns
    -------
    bool
        Whether or not 0 tillages counted.
    """
    practice = find_term_match(practices, NUMBER_OF_TILLAGES_TERM_ID)
    nTillages = list_sum(practice.get("value", []))
    return nTillages <= 0


def _check_cycle_tillage_management_category(
    cycle: dict,
    key: IpccManagementCategory
) -> bool:
    """
    Checks whether a Hesita `Cycle` node meets the requirements of a specific tillage `IpccManagementCategory`.

    Parameters
    ----------
    cycle : dict
        A Hestia `Cycle` node, see: https://www.hestia.earth/schema/Cycle.
    key : IpccManagementCategory
        The `IpccManagementCategory` to match.

    Returns
    -------
    bool
        Whether or not the cycle meets the requirements for the category.
    """
    LOOKUP = LOOKUPS["tillage"]
    target_lookup_values = IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE.get(key, None)

    practices = cycle.get("practices", [])
    tillage_nodes = filter_list_term_type(
        practices, [TermTermType.TILLAGE]
    )

    return cumulative_nodes_lookup_match(
        tillage_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    ) and (
        key is not IpccManagementCategory.NO_TILLAGE
        or _check_zero_tillages(tillage_nodes)
    )


TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.FULL_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    ),
    IpccManagementCategory.REDUCED_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    ),
    IpccManagementCategory.NO_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    )
}


def _assign_tier_2_ipcc_tillage_management_category(
    cycles: list[dict],
    default: IpccManagementCategory = IpccManagementCategory.OTHER
) -> IpccManagementCategory:
    """
    Assigns a tillage `IpccManagementCategory` to a list of Hestia `Cycle`s.

    Parameters
    ----------
    cycles : list[dict])
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
        IpccManagementCategory: The assigned tillage `IpccManagementCategory`.
    """
    return next(
        (
            key for key in TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE
            if TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE[key](cycles, key)
        ),
        default
    ) if len(cycles) > 0 else default


# --- TIER 2 FUNCTIONS: ANNUAL TEMPERATURE FACTOR FROM MONTHLY TEMPERATURE DATA ---


def _calc_temperature_factor(
    average_temperature: float,
    maximum_temperature: float = 45.0,
    optimum_temperature: float = 33.69,
) -> float:
    """
    Equation 5.0E, part 2. Calculate the temperature effect on decomposition in mineral soils for a single month using
    the Steady-State Method.

    If `average_temperature >= maximum_temperature` the function should always return 0.

    Parameters
    ----------
    average_temperature : float
        The average air temperature of a given month, degrees C.
    maximum_temperature : float
        The maximum air temperature for decomposition, degrees C, default value: `45.0`.
    optimum_temperature : float
        The optimum air temperature for decomposition, degrees C, default value: `33.69`.

    Returns
    -------
    float
        The air temperature effect on decomposition for a given month, dimensionless, between `0` and `1`.
    """
    prelim = (maximum_temperature - average_temperature) / (
        maximum_temperature - optimum_temperature
    )
    return 0 if average_temperature >= maximum_temperature else (
        pow(prelim, 0.2) * exp((0.2 / 2.63) * (1 - pow(prelim, 2.63)))
    )


def _calc_annual_temperature_factor(
    average_temperature_monthly: list[float],
    maximum_temperature: float = 45.0,
    optimum_temperature: float = 33.69,
) -> Union[float, None]:
    """
    Equation 5.0E, part 1. Calculate the average annual temperature effect on decomposition in mineral soils using the
    Steady-State Method.

    Parameters
    ----------
    average_temperature_monthly : list[float]
        A list of monthly average air temperatures in degrees C, must have a length of 12.

    Returns
    -------
    float | None
        Average annual temperature factor, dimensionless, between `0` and `1`, or `None` if the input list is empty.
    """
    return mean(
        list(
            _calc_temperature_factor(t, maximum_temperature, optimum_temperature)
            for t in average_temperature_monthly
        )
    ) if average_temperature_monthly else None


# --- TIER 2 FUNCTIONS: ANNUAL WATER FACTOR FROM MONTHLY PRECIPITATION, PET AND IRRIGATION DATA ---


def _calc_water_factor(
    precipitation: float,
    pet: float,
    is_irrigated: bool = False,
    water_factor_slope: float = 1.331,
) -> float:
    """
    Equation 5.0F, part 2. Calculate the water effect on decomposition in mineral soils for a single month using the
    Steady-State Method.

    If `is_irrigated == True` the function should always return `0.775`.

    Parameters
    ----------
    precipitation : float
        The sum total precipitation of a given month, mm.
    pet : float
        The sum total potential evapotranspiration in a given month, mm.
    is_irrigated : bool
        Whether or not irrigation has been used in a given month.
    water_factor_slope : float
        The slope for mappet term to estimate water factor, dimensionless, default value: `1.331`.

    Returns
    -------
    float
        The water effect on decomposition for a given month, dimensionless, between `0.2129` and `1.5`.
    """
    mappet = min(1.25, precipitation / pet)
    return 0.775 if is_irrigated else 0.2129 + (water_factor_slope * (mappet)) - (0.2413 * pow(mappet, 2))


def _calc_annual_water_factor(
    precipitation_monthly: list[float],
    pet_monthly: list[float],
    is_irrigated_monthly: Union[list[bool], None] = None,
    water_factor_slope: float = 1.331,
) -> Union[float, None]:
    """
    Equation 5.0F, part 1. Calculate the average annual water effect on decomposition in mineral soils using the
    Steady-State Method multiplied by a coefficient of `1.5`.

    Parameters
    ----------
    precipitation_monthly : list[float]
        A list of monthly sum total precipitation values in mm, must have a length of 12.
    pet_monthly : list[float])
        A list of monthly sum total potential evapotranspiration values in mm, must have a length of 12.
    is_irrigated_monthly : list[boolean] | None)
        A list of true/false values that describe whether irrigation has been used in each calendar month, must have a
        length of 12. If `None` is provided, a list of 12 `False` values is used.
    water_factor_slope : float
        The slope for mappet term to estimate water factor, dimensionless, default value: `1.331`.

    Returns
    -------
    float | None
        Average annual water factor multiplied by `1.5`, dimensionless, between `0.31935` and `2.25`,
        or `None` if any of the input lists are empty.
    """
    is_irrigated_monthly = (
        [False] * 12 if is_irrigated_monthly is None else is_irrigated_monthly
    )
    zipped = zip(precipitation_monthly, pet_monthly, is_irrigated_monthly)
    return 1.5 * mean(list(
        _calc_water_factor(precipitation, pet, is_irrigated, water_factor_slope)
        for precipitation, pet, is_irrigated in zipped
    )) if all([precipitation_monthly, pet_monthly]) else None


# --- TIER 2 FUNCTIONS: ANNUAL TOTAL ORGANIC C INPUT TO SOIL, N CONTENT AND LIGNIN CONTENT FROM CARBON SOURCES ---


def _calc_total_organic_carbon_input(
    carbon_sources: list[CarbonSource], default_carbon_content=0.42
) -> float:
    """
    Equation 5.0H part 1. Calculate the total organic carbon to a site from all carbon sources (above-ground and
    below-ground crop residues, organic amendments, etc.).

    Parameters
    ----------
    carbon_sources : list[CarbonSource])
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`.
    default_carbon_content : float
        The default carbon content of a carbon source, decimal proportion, kg C (kg d.m.)-1.

    Returns
    -------
    float
        The total mass of organic carbon inputted into the site, kg C ha-1.
    """
    return sum(c.mass * (c.carbon_content if c.carbon_content else default_carbon_content) for c in carbon_sources)


def _calc_average_nitrogen_content_of_organic_carbon_sources(
    carbon_sources: list[CarbonSource], default_nitrogen_content=0.0085
) -> float:
    """
    Calculate the average nitrogen content of the carbon inputs through a weighted mean.

    Parameters
    ----------
    carbon_sources : list[CarbonSource]
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`
    default_nitrogen_content : float
        The default nitrogen content of a carbon source, decimal proportion, kg N (kg d.m.)-1.

    Returns
    -------
    float
        The average nitrogen content of the carbon sources, decimal_proportion, kg N (kg d.m.)-1.
    """
    total_weight = sum(c.mass for c in carbon_sources)
    weighted_values = [
        c.mass * (c.nitrogen_content if c.nitrogen_content else default_nitrogen_content) for c in carbon_sources
    ]
    return sum(weighted_values) / total_weight if total_weight > 0 else default_nitrogen_content


def _calc_average_lignin_content_of_organic_carbon_sources(
    carbon_sources: list[dict[str, float]], default_lignin_content=0.073
) -> float:
    """
    Calculate the average lignin content of the carbon inputs through a weighted mean.

    Parameters
    ----------
    carbon_sources : list[CarbonSource]
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`
    default_lignin_content : float
        The default lignin content of a carbon source, decimal proportion, kg lignin (kg d.m.)-1.

    Returns
    -------
    float
        The average lignin content of the carbon sources, decimal_proportion, kg lignin (kg d.m.)-1.
    """
    total_weight = sum(c.mass for c in carbon_sources)
    weighted_values = [
        c.mass * (c.lignin_content if c.lignin_content else default_lignin_content) for c in carbon_sources
    ]
    return sum(weighted_values) / total_weight if total_weight > 0 else default_lignin_content


# --- TIER 2 FUNCTIONS: ACTIVE SUB-POOL SOC STOCK ---


def _calc_beta(
    carbon_input: float,
    lignin_content: float = 0.073,
    nitrogen_content: float = 0.0083,
) -> float:
    """
    Equation 5.0G, part 2. Calculate the C input to the metabolic dead organic matter C component, kg C ha-1.

    See table 5.5b for default values for lignin content and nitrogen content.

    Parameters
    ----------
    carbon_input : float
        Total carbon input to the soil during an inventory year, kg C ha-1.
    lignin_content : float
        The average lignin content of carbon input sources, decimal proportion, default value: `0.073`.
    nitrogen_content : float
        The average nitrogen content of carbon sources, decimal proportion, default value: `0.0083`.

    Returns
    -------
    float
        The C input to the metabolic dead organic matter C component, kg C ha-1.
    """
    return carbon_input * (0.85 - 0.018 * (lignin_content / nitrogen_content))


def _get_f_2(
    tillage_management_category: IpccManagementCategory = IpccManagementCategory.OTHER,
    f_2_full_tillage: float = 0.455,
    f_2_reduced_tillage: float = 0.477,
    f_2_no_tillage: float = 0.5,
    f_2_unknown_tillage: float = 0.368,
) -> float:
    """
    Get the value of `f_2` (the stabilisation efficiencies for structural decay products entering the active pool)
    based on the tillage `IpccManagementCategory`.

    If tillage regime is unknown, `IpccManagementCategory.OTHER` should be assumed.

    Parameters
    ----------
    tillage_management_category : (IpccManagementCategory)
        The tillage category of the inventory year, default value: `IpccManagementCategory.OTHER`.
    f_2_full_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool under full tillage,
        decimal proportion, default value: `0.455`.
    f_2_reduced_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool under reduced tillage,
        decimal proportion, default value: `0.477`.
    f_2_no_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool under no tillage,
        decimal proportion, default value: `0.5`.
    f_2_unknown_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool if tillage is not known,
        decimal proportion, default value: `0.368`.

    Returns
    -------
        float: The stabilisation efficiencies for structural decay products entering the active pool,
        decimal proportion.
    """
    ipcc_tillage_management_category_to_f_2s = {
        IpccManagementCategory.FULL_TILLAGE: f_2_full_tillage,
        IpccManagementCategory.REDUCED_TILLAGE: f_2_reduced_tillage,
        IpccManagementCategory.NO_TILLAGE: f_2_no_tillage,
        IpccManagementCategory.OTHER: f_2_unknown_tillage
    }
    default = f_2_unknown_tillage

    return ipcc_tillage_management_category_to_f_2s.get(tillage_management_category, default)


def _calc_f_4(sand_content: float = 0.33, f_5: float = 0.0855) -> float:
    """
    Equation 5.0C, part 4. Calculate the value of the stabilisation efficiencies for active pool decay products
    entering the slow pool based on the sand content of the soil.

    Parameters
    ----------
    sand_content : float)
        The sand content of the soil, decimal proportion, default value: `0.33`.
    f_5 : float
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal_proportion,
        default value: `0.0855`.

    Returns
    -------
    float
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    """
    return 1 - f_5 - (0.17 + 0.68 * sand_content)


def _calc_alpha(
    carbon_input: float,
    f_2: float,
    f_4: float,
    lignin_content: float = 0.073,
    nitrogen_content: float = 0.0083,
    f_1: float = 0.378,
    f_3: float = 0.455,
    f_5: float = 0.0855,
    f_6: float = 0.0504,
    f_7: float = 0.42,
    f_8: float = 0.45,
) -> float:
    """
    Equation 5.0G, part 1. Calculate the C input to the active soil carbon sub-pool, kg C ha-1.

    See table 5.5b for default values for lignin content and nitrogen content.

    Parameters
    ----------
    carbon_input : float
        Total carbon input to the soil during an inventory year, kg C ha-1.
    f_2 : float
        The stabilisation efficiencies for structural decay products entering the active pool, decimal proportion.
    f_4 : float
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    lignin_content : float
        The average lignin content of carbon input sources, decimal proportion, default value: `0.073`.
    nitrogen_content : float
        The average nitrogen content of carbon input sources, decimal proportion, default value: `0.0083`.
    sand_content : float
        The sand content of the soil, decimal proportion, default value: `0.33`.
    f_1 : float
        The stabilisation efficiencies for metabolic decay products entering the active pool, decimal proportion,
        default value: `0.378`.
    f_3 : float
        The stabilisation efficiencies for structural decay products entering the slow pool, decimal proportion,
        default value: `0.455`.
    f_5 : float
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal proportion,
        default value: `0.0855`.
    f_6 : float
        The stabilisation efficiencies for slow pool decay products entering the passive pool, decimal proportion,
        default value: `0.0504`.
    f_7 : float
        The stabilisation efficiencies for slow pool decay products entering the active pool, decimal proportion,
        default value: `0.42`.
    f_8 : float
        The stabilisation efficiencies for passive pool decay products entering the active pool, decimal proportion,
        default value: `0.45`.

    Returns
    -------
    float
        The C input to the active soil carbon sub-pool, kg C ha-1.
    """
    beta = _calc_beta(
        carbon_input, lignin_content=lignin_content, nitrogen_content=nitrogen_content
    )

    x = beta * f_1
    y = (carbon_input * (1 - lignin_content) - beta) * f_2
    z = (carbon_input * lignin_content) * f_3 * (f_7 + (f_6 * f_8))
    d = 1 - (f_4 * f_7) - (f_5 * f_8) - (f_4 * f_6 * f_8)
    return (x + y + z) / d


def _get_tillage_factor(
    tillage_management_category: IpccManagementCategory = IpccManagementCategory.FULL_TILLAGE,
    tillage_factor_full_tillage: float = 3.036,
    tillage_factor_reduced_tillage: float = 2.075,
    tillage_factor_no_tillage: float = 1,
) -> float:
    """
    Calculate the tillage disturbance modifier on decay rate for active and slow sub-pools based on the tillage
    `IpccManagementCategory`.

    If tillage regime is unknown, `FULL_TILLAGE` should be assumed.

    Parameters
    ----------
    tillage_factor_full_tillage : float)
        The tillage disturbance modifier for decay rates under full tillage, dimensionless, default value: `3.036`.
    tillage_factor_reduced_tillage : float
        Tillage disturbance modifier for decay rates under reduced tillage, dimensionless, default value: `2.075`.
    tillage_factor_no_tillage : float
        Tillage disturbance modifier for decay rates under no tillage, dimensionless, default value: `1`.

    Returns
    -------
    float
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    """
    ipcc_tillage_management_category_to_tillage_factors = {
        IpccManagementCategory.FULL_TILLAGE: tillage_factor_full_tillage,
        IpccManagementCategory.REDUCED_TILLAGE: tillage_factor_reduced_tillage,
        IpccManagementCategory.NO_TILLAGE: tillage_factor_no_tillage,
    }
    default = tillage_factor_full_tillage

    return ipcc_tillage_management_category_to_tillage_factors.get(
        tillage_management_category, default
    )


def _calc_active_pool_decay_rate(
    annual_temperature_factor: float,
    annual_water_factor: float,
    tillage_factor: float,
    sand_content: float = 0.33,
    active_decay_factor: float = 7.4,
) -> float:
    """
    Equation 5.0B, part 3. Calculate the decay rate for the active SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    annual_temperature_factor : float
        Average annual temperature factor, dimensionless, between `0` and `1`.
    annual_water_factor : float
        Average annual water factor, dimensionless, between `0.31935` and `2.25`.
    tillage_factor : float
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    sand_content : float
        sand_content (float): The sand content of the soil, decimal proportion, default value: `0.33`.
    active_decay_factor : float
        decay rate constant under optimal conditions for decomposition of the active SOC subpool, year-1, default value:
        `7.4`.

    Returns
    -------
    float
        The decay rate for active SOC sub-pool, year-1.
    """
    sand_factor = 0.25 + (0.75 * sand_content)
    return (
        annual_temperature_factor
        * annual_water_factor
        * tillage_factor
        * sand_factor
        * active_decay_factor
    )


def _calc_active_pool_steady_state(
    alpha: float, active_pool_decay_rate: float
) -> float:
    """
    Equation 5.0B part 2. Calculate the steady state active sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    alpha : float
        The C input to the active soil carbon sub-pool, kg C ha-1.
    active_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.

    Returns
    -------
    float
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1
    """
    return alpha / active_pool_decay_rate


# --- TIER 2 FUNCTIONS: SLOW SUB-POOL SOC STOCK ---


def _calc_slow_pool_decay_rate(
    annual_temperature_factor: float,
    annual_water_factor: float,
    tillage_factor: float,
    slow_decay_factor: float = 0.209,
) -> float:
    """
    Equation 5.0C, part 3. Calculate the decay rate for the slow SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    annual_temperature_factor : float
        Average annual temperature factor, dimensionless, between `0` and `1`.
    annual_water_factor : float
        Average annual water factor, dimensionless, between `0.31935` and `2.25`.
    tillage_factor : float
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    slow_decay_factor : float)
        The decay rate constant under optimal conditions for decomposition of the slow SOC subpool, year-1,
        default value: `0.209`.

    Returns
    -------
    float
        The decay rate for slow SOC sub-pool, year-1.
    """
    return (
        annual_temperature_factor
        * annual_water_factor
        * tillage_factor
        * slow_decay_factor
    )


def _calc_slow_pool_steady_state(
    carbon_input: float,
    f_4: float,
    active_pool_steady_state: float,
    active_pool_decay_rate: float,
    slow_pool_decay_rate: float,
    lignin_content: float = 0.073,
    f_3: float = 0.455,
) -> float:
    """
    Equation 5.0C, part 2. Calculate the steady state slow sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    carbon_input : float
        Total carbon input to the soil during an inventory year, kg C ha-1.
    f_4 : float
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    active_pool_steady_state : float
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1
    active_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.
    slow_pool_decay_rate : float
        Decay rate for slow SOC sub-pool, year-1.
    lignin_content : float
        The average lignin content of carbon input sources, decimal proportion, default value: `0.073`.
    f_3 : float
        The stabilisation efficiencies for structural decay products entering the slow pool, decimal proportion,
        default value: `0.455`.

    Returns
    -------
    float
        The steady state slow sub-pool SOC stock given conditions in year y, kg C ha-1
    """
    x = carbon_input * lignin_content * f_3
    y = active_pool_steady_state * active_pool_decay_rate * f_4
    return (x + y) / slow_pool_decay_rate


# --- TIER 2 FUNCTIONS: PASSIVE SUB-POOL SOC STOCK ---


def _calc_passive_pool_decay_rate(
    annual_temperature_factor: float,
    annual_water_factor: float,
    passive_decay_factor: float = 0.00689,
) -> float:
    """
    Equation 5.0D, part 3. Calculate the decay rate for the passive SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    annual_temperature_factor : float
        Average annual temperature factor, dimensionless, between `0` and `1`.
    annual_water_factor : float
        Average annual water factor, dimensionless, between `0.31935` and `2.25`.
    passive_decay_factor : float
        decay rate constant under optimal conditions for decomposition of the passive SOC subpool, year-1,
        default value: `0.00689`.

    Returns
    -------
    float
        The decay rate for passive SOC sub-pool, year-1.
    """
    return annual_temperature_factor * annual_water_factor * passive_decay_factor


def _calc_passive_pool_steady_state(
    active_pool_steady_state: float,
    slow_pool_steady_state: float,
    active_pool_decay_rate: float,
    slow_pool_decay_rate: float,
    passive_pool_decay_rate: float,
    f_5: float = 0.0855,
    f_6: float = 0.0504,
) -> float:
    """
    Equation 5.0D, part 2. Calculate the steady state passive sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    active_pool_steady_state : float
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1.
    slow_pool_steady_state : float
        The steady state slow sub-pool SOC stock given conditions in year y, kg C ha-1.
    active_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.
    slow_pool_decay_rate : float
        Decay rate for slow SOC sub-pool, year-1.
    passive_pool_decay_rate : float
        Decay rate for passive SOC sub-pool, year-1.
    f_5 : float
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal proportion,
        default value: `0.0855`.
    f_6 : float
        The stabilisation efficiencies for slow pool decay products entering the passive pool, decimal proportion,
        default value: `0.0504`.

    Returns
    -------
    float
        The steady state passive sub-pool SOC stock given conditions in year y, kg C ha-1.
    """
    x = active_pool_steady_state * active_pool_decay_rate * f_5
    y = slow_pool_steady_state * slow_pool_decay_rate * f_6
    return (x + y) / passive_pool_decay_rate


# --- TIER 2 FUNCTIONS:  GENERIC SUB-POOL SOC STOCK ---


def _calc_sub_pool_soc_stock(
    sub_pool_steady_state: (float),
    previous_sub_pool_soc_stock: (float),
    sub_pool_decay_rate: (float),
    timestep: int = 1,
) -> float:
    """
    Generalised from equations 5.0B, 5.0C and 5.0D, part 1. Calculate the sub-pool SOC stock in year y, kg C ha-1.

    If `sub_pool_decay_rate > 1` then set its value to `1` for this calculation.

    Parameters
    ----------
    sub_pool_steady_state : float
        The steady state sub-pool SOC stock given conditions in year y, kg C ha-1.
    previous_sub_pool_soc_stock : float
        The sub-pool SOC stock in year y-timestep (by default one year ago), kg C ha-1.
    sub_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.
    timestep : int
        The number of years between current and previous inventory year.

    Returns
    -------
    float
        The sub-pool SOC stock in year y, kg C ha-1.
    """
    sub_pool_decay_rate = min(1, sub_pool_decay_rate)
    return (
        previous_sub_pool_soc_stock
        + (sub_pool_steady_state - previous_sub_pool_soc_stock)
        * timestep
        * sub_pool_decay_rate
    )


# --- TIER 2 FUNCTIONS: SOC STOCK CHANGE ---


def _calc_tier_2_soc_stock(
    active_pool_soc_stock: float,
    slow_pool_soc_stock: float,
    passive_pool_soc_stock: float,
) -> float:
    """
    Equation 5.0A, part 3. Calculate the total SOC stock for a site by summing its active, slow and passive SOC stock
    sub-pools. This is the value we need for our `organicCarbonPerHa` measurement.

    Parameters
    ----------
    actve_pool_soc_stock : float
        The active sub-pool SOC stock in year y, kg C ha-1.
    slow_pool_soc_stock : float
        The slow sub-pool SOC stock in year y, kg C ha-1.
    passive_pool_soc_stock : float
        The passive sub-pool SOC stock in year y, kg C ha-1.

    Returns
    -------
    float
        The SOC stock of a site in year y, kg C ha-1.
    """
    return active_pool_soc_stock + slow_pool_soc_stock + passive_pool_soc_stock


# --- TIER 2 SUB-MODEL: RUN ACTIVE, SLOW AND PASSIVE SOC STOCKS ---


def timeseries_to_inventory(timeseries_data: list[float], run_in_period: int):
    """
    Convert annual data to inventory data by averaging the values for the run-in period.

    Parameters
    ----------
    timeseries_data : list[float]
        The timeseries data to be reformatted.
    run_in_period : int
        The length of the run-in in years.

    Returns
    -------
    list[float]
        The inventory formatted data, where value 0 is the average of the run-in values.
    """
    return [mean(timeseries_data[0:run_in_period])] + timeseries_data[run_in_period:]


def _run_soc_stocks(
    timestamps: list[int],
    annual_temperature_factors: list[float],
    annual_water_factors: list[float],
    annual_organic_carbon_inputs: list[float],
    annual_average_nitrogen_contents_of_organic_carbon_sources: list[float],
    annual_average_lignin_contents_of_organic_carbon_sources: list[float],
    annual_tillage_categories: Union[list[IpccManagementCategory], None] = None,
    sand_content: float = 0.33,
    run_in_period: int = 5,
    initial_soc_stock: Union[float, None] = None,
    params: Union[dict[str, float], None] = None,
) -> Tier2SocResult:
    """
    Run the IPCC Tier 2 SOC model with precomputed `annual_temperature_factors`, `annual_water_factors`,
    `annual_organic_carbon_inputs`, `annual_average_nitrogen_contents_of_organic_carbon_sources`,
    `annual_average_lignin_contents_of_organic_carbon_sources`.

    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
    annual_temperature_factors : list[float]
        A list of temperature factors for each year in the inventory, dimensionless (see Equation 5.0E).
    annual_water_factors : list[float]
        A list of water factors for each year in the inventory, dimensionless (see Equation 5.0F).
    annual_organic_carbon_inputs : list[float]
        A list of organic carbon inputs to the soil for each year in the inventory, kg C ha-1 year-1
        (see Equation 5.0H).
    annual_average_nitrogen_contents_of_organic_carbon_sources : list[float]
        A list of the average nitrogen contents of the organic carbon sources for each year in the inventory,
        decimal proportion.
    annual_average_lignin_contents_of_organic_carbon_sources : list[float]
        A list of the average lignin contents of the organic carbon sources for each year in the inventory,
        decimal proportion.
    annual_tillage_categories : list[IpccManagementCategory] | None
        A list of the site"s `IpccManagementCategory`s for each year in the inventory.
    sand_content : float
        The sand content of the site, decimal proportion, default value: `0.33`.
    run_in_period : int
        The length of the run-in period in years, must be greater than or equal to 1, default value: `5`.
    initial_soc_stock : float | None
        The measured or pre-computed initial SOC stock at the end of the run-in period, kg C ha-1.
    params : dict[str: float] | None
        Overrides for the model parameters. If `None` only default parameters will be used.

    Returns
    -------
    Tier2SocResult
        Returns an annual inventory of organicCarbonPerHa data in the format
        `(timestamps: list[int], organicCarbonPerHa_values: list[float], active_pool_soc_stocks: list[float],
        slow_pool_soc_stocks: list[float], passive_pool_soc_stocks: list[float])`
    """

    # --- MERGE ANY USER-SET PARAMETERS WITH THE IPCC DEFAULTS ---

    params = DEFAULT_PARAMS | (params or {})

    # --- GET F4 ---

    f_4 = _calc_f_4(sand_content, f_5=params.get("f_5"))

    # --- GET ANNUAL DATA ---

    annual_f_2s = [
        _get_f_2(
            till,
            f_2_full_tillage=params.get("f_2_full_tillage"),
            f_2_reduced_tillage=params.get("f_2_reduced_tillage"),
            f_2_no_tillage=params.get("f_2_no_tillage"),
            f_2_unknown_tillage=params.get("f_2_unknown_tillage"),
        )
        for till in annual_tillage_categories
    ]

    annual_tillage_factors = [
        _get_tillage_factor(
            till,
            tillage_factor_full_tillage=params.get("tillage_factor_full_tillage"),
            tillage_factor_reduced_tillage=params.get("tillage_factor_reduced_tillage"),
            tillage_factor_no_tillage=params.get("tillage_factor_no_tillage"),
        )
        for till in annual_tillage_categories
    ]

    # --- SPLIT ANNUAL DATA INTO RUN-IN AND INVENTORY PERIODS ---

    inventory_temperature_factors = timeseries_to_inventory(
        annual_temperature_factors, run_in_period
    )
    inventory_water_factors = timeseries_to_inventory(
        annual_water_factors, run_in_period
    )
    inventory_carbon_inputs = timeseries_to_inventory(
        annual_organic_carbon_inputs, run_in_period
    )
    inventory_nitrogen_contents = timeseries_to_inventory(
        annual_average_nitrogen_contents_of_organic_carbon_sources, run_in_period
    )
    inventory_lignin_contents = timeseries_to_inventory(
        annual_average_lignin_contents_of_organic_carbon_sources, run_in_period
    )
    inventory_f_2s = timeseries_to_inventory(annual_f_2s, run_in_period)
    inventory_tillage_factors = timeseries_to_inventory(
        annual_tillage_factors, run_in_period
    )

    inventory_timestamps = timestamps[
        run_in_period - 1:
    ]  # The last year of the run-in should be the first year of the inventory

    # --- CALCULATE THE ACTIVE ACTIVE POOL STEADY STATES ---

    inventory_alphas = [
        _calc_alpha(
            carbon_input,
            f_2,
            f_4,
            lignin_content,
            nitrogen_content,
            f_1=params.get("f_1"),
            f_3=params.get("f_3"),
            f_5=params.get("f_5"),
            f_6=params.get("f_6"),
            f_7=params.get("f_7"),
            f_8=params.get("f_8"),
        )
        for carbon_input, f_2, lignin_content, nitrogen_content in zip(
            inventory_carbon_inputs,
            inventory_f_2s,
            inventory_lignin_contents,
            inventory_nitrogen_contents,
        )
    ]

    inventory_active_pool_decay_rates = [
        _calc_active_pool_decay_rate(
            temp_fac,
            water_fac,
            till_fac,
            sand_content,
            active_decay_factor=params.get("active_decay_factor"),
        )
        for temp_fac, water_fac, till_fac in zip(
            inventory_temperature_factors,
            inventory_water_factors,
            inventory_tillage_factors,
        )
    ]

    inventory_active_pool_steady_states = [
        _calc_active_pool_steady_state(alpha, active_decay_rate)
        for alpha, active_decay_rate in zip(
            inventory_alphas, inventory_active_pool_decay_rates
        )
    ]

    # --- CALCULATE THE SLOW POOL STEADY STATES ---

    inventory_slow_pool_decay_rates = [
        _calc_slow_pool_decay_rate(
            temp_fac, water_fac, till_fac, slow_decay_factor=params.get("slow_decay_factor")
        )
        for temp_fac, water_fac, till_fac in zip(
            inventory_temperature_factors,
            inventory_water_factors,
            inventory_tillage_factors,
        )
    ]

    inventory_slow_pool_steady_states = [
        _calc_slow_pool_steady_state(
            carbon_input,
            f_4,
            active_steady_state,
            active_decay_rate,
            slow_decay_rate,
            lignin_content,
            f_3=params.get("f_3"),
        )
        for carbon_input, active_steady_state, active_decay_rate, slow_decay_rate, lignin_content in zip(
            inventory_carbon_inputs,
            inventory_active_pool_steady_states,
            inventory_active_pool_decay_rates,
            inventory_slow_pool_decay_rates,
            inventory_lignin_contents,
        )
    ]

    # --- CALCULATE THE PASSIVE POOL STEADY STATES ---

    inventory_passive_pool_decay_rates = [
        _calc_passive_pool_decay_rate(
            temp_fac, water_fac, passive_decay_factor=params.get("passive_decay_factor")
        )
        for temp_fac, water_fac in zip(
            inventory_temperature_factors, inventory_water_factors
        )
    ]

    inventory_passive_pool_steady_states = [
        _calc_passive_pool_steady_state(
            active_steady_state,
            slow_steady_state,
            active_decay_rate,
            slow_decay_rate,
            passive_decay_rate,
            f_5=params.get("f_5"),
            f_6=params.get("f_6"),
        )
        for active_steady_state, slow_steady_state, active_decay_rate, slow_decay_rate, passive_decay_rate in zip(
            inventory_active_pool_steady_states,
            inventory_slow_pool_steady_states,
            inventory_active_pool_decay_rates,
            inventory_slow_pool_decay_rates,
            inventory_passive_pool_decay_rates,
        )
    ]

    # --- CALCULATE THE ACTIVE, SLOW AND PASSIVE SOC STOCKS ---

    init_total_steady_state = (
        inventory_active_pool_steady_states[0] +
        inventory_slow_pool_steady_states[0] + inventory_passive_pool_steady_states[0]
    )

    init_active_frac = inventory_active_pool_steady_states[0]/init_total_steady_state
    init_slow_frac = inventory_slow_pool_steady_states[0]/init_total_steady_state
    init_passive_frac = 1 - (init_active_frac + init_slow_frac)

    inventory_active_pool_soc_stocks = []
    inventory_slow_pool_soc_stocks = []
    inventory_passive_pool_soc_stocks = []

    should_calc_run_in = initial_soc_stock is None

    inventory_active_pool_soc_stocks.insert(
        0,
        inventory_active_pool_steady_states[0]
        if should_calc_run_in
        else init_active_frac * initial_soc_stock,
    )
    inventory_slow_pool_soc_stocks.insert(
        0,
        inventory_slow_pool_steady_states[0]
        if should_calc_run_in
        else init_slow_frac * initial_soc_stock,
    )
    inventory_passive_pool_soc_stocks.insert(
        0,
        inventory_passive_pool_steady_states[0]
        if should_calc_run_in
        else init_passive_frac * initial_soc_stock,
    )

    for index in range(1, len(inventory_timestamps), 1):
        inventory_active_pool_soc_stocks.insert(
            index,
            _calc_sub_pool_soc_stock(
                inventory_active_pool_steady_states[index],
                inventory_active_pool_soc_stocks[index - 1],
                inventory_active_pool_decay_rates[index],
            ),
        )
        inventory_slow_pool_soc_stocks.insert(
            index,
            _calc_sub_pool_soc_stock(
                inventory_slow_pool_steady_states[index],
                inventory_slow_pool_soc_stocks[index - 1],
                inventory_slow_pool_decay_rates[index],
            ),
        )
        inventory_passive_pool_soc_stocks.insert(
            index,
            _calc_sub_pool_soc_stock(
                inventory_passive_pool_steady_states[index],
                inventory_passive_pool_soc_stocks[index - 1],
                inventory_passive_pool_decay_rates[index],
            ),
        )

    # --- RETURN THE RESULT ---

    return Tier2SocResult(
        timestamps=inventory_timestamps,
        active_pool_soc_stocks=inventory_active_pool_soc_stocks,
        slow_pool_soc_stocks=inventory_slow_pool_soc_stocks,
        passive_pool_soc_stocks=inventory_passive_pool_soc_stocks,
    )


# --- TIER 2 SUB-MODEL: ANNUAL TEMPERATURE FACTORS ---


def _check_consecutive(ints: list[int]) -> bool:
    """
    Checks whether a list of integers are consecutive.

    Used to determine whether annualised data is complete from every year from beggining to end.

    Parameters
    ----------
    ints : list[int]
        A list of integer values.

    Returns
    -------
    bool
        Whether or not the list of integers is consecutive.
    """
    range_list = list(range(min(ints), max(ints)+1)) if ints else []
    return all(a == b for a, b in zip(ints, range_list))


def _check_12_months(inner_dict: dict, keys: set[Any]):
    """
    Checks whether an inner dict has 12 months of data for each of the required inner keys.

    Parameters
    ----------
    inner_dict : dict
        A dictionary representing one year in a timeseries for the Tier 2 model.
    keys : set[Any]
        The required inner keys.

    Returns
    -------
    bool
        Whether or not the inner dict satisfies the conditions.
    """
    return all(
        len(inner_dict.get(key, [])) == 12 for key in keys
    )


# --- SUB-MODEL ANNUAL TEMPERATURE FACTORS ---


def _should_run_annual_temperature_factors(
    site: dict
) -> tuple[bool, dict]:
    """
    Extracts, formats and checks data from the site node to determine whether or not to run the annual temperature
    factors model on a specific Hestia `Site`.

    Parameters
    ----------
    site : dict
        A Hestia `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    tuple[bool, dict]
        `(should_run, grouped_data)`.
    """
    measurements = site.get("measurements", [])
    temperature_monthly = find_term_match(measurements, TEMPERATURE_MONTHLY_TERM_ID, {})

    grouped_data = group_measurement_values_by_year(
        temperature_monthly,
        inner_key=_InnerKey.TEMPERATURES,
        complete_years_only=True
    )

    should_run = all([
        all(
            _check_12_months(inner, {_InnerKey.TEMPERATURES})
            for inner in grouped_data.values()
        ),
        len(grouped_data.keys()) >= MIN_RUN_IN_PERIOD,
        _check_consecutive(grouped_data.keys())
    ])

    logShouldRun(site, MODEL, TERM_ID, should_run, sub_model="_run_annual_temperature_factors")
    return should_run, grouped_data


def _run_annual_temperature_factors(
    timestamps: list[int],
    temperatures: list[list[float]],
    maximum_temperature: float = 45.0,
    optimum_temperature: float = 33.69,
):
    """
    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
    temperatures : list[list[float]])
        A list of monthly average temperatures for each year in the inventory
        (e.g. `[[10,10,10,20,25,15,15,10,10,10,5,5]]`).
    maximum_temperature : float
        The maximum air temperature for decomposition, degrees C, default value: `45.0`.
    optimum_temperature : float
        The optimum air temperature for decomposition, degrees C, default value: `33.69`.

    Returns
    -------
    TemperatureFactorResult
        An inventory of annual temperature factor data as a named tuple with the format
        `(timestamps: list[int], annual_temperature_factors: list[float])`.
    """
    return TemperatureFactorResult(
        timestamps=timestamps,
        annual_temperature_factors=[
            _calc_annual_temperature_factor(
                monthly_temperatures, maximum_temperature, optimum_temperature
            )
            for monthly_temperatures in temperatures
        ],
    )


# --- TIER 2 SUB-MODEL: ANNUAL WATER FACTORS ---


def _should_run_annual_water_factors(
    site: dict,
    cycles: list[dict]
) -> tuple[bool, bool, dict]:
    """
    Extracts, formats and checks data from the site and cycle nodes to determine determine whether or not to run the
    annual water factors model on a specific Hestia `Site` and `Cycle`s.

    TODO: Implement checks for monthly is_irrigateds from cycles.

    Parameters
    ----------
    site : dict
        A Hestia `Site` node, see: https://www.hestia.earth/schema/Site.
    cycles : list[dict]
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    tuple[bool, bool, dict]
        `(should_run, run_with_irrigation, grouped_data)`.
    """
    measurements = site.get("measurements", [])
    precipitation_monthly = find_term_match(measurements, PRECIPITATION_MONTHLY_TERM_ID, {})
    potential_evapotranspiration_monthly = find_term_match(measurements, PET_MONTHLY_TERM_ID, {})

    grouped_precipitations = group_measurement_values_by_year(
        precipitation_monthly,
        inner_key=_InnerKey.PRECIPITATIONS,
        complete_years_only=True
    )
    grouped_pets = group_measurement_values_by_year(
        potential_evapotranspiration_monthly,
        inner_key=_InnerKey.PETS,
        complete_years_only=True
    )

    is_irrigateds = None  # TODO: Implement is_irrigateds check.
    run_with_irrigation = bool(is_irrigateds)

    grouped_data = (
        merge(grouped_precipitations, grouped_pets) if is_irrigateds is None else reduce(
            merge, [grouped_precipitations, grouped_pets, is_irrigateds]
        )
    )

    should_run = all([
        all(
            _check_12_months(inner, {_InnerKey.PRECIPITATIONS, _InnerKey.PETS})
            for inner in grouped_data.values()
        ),
        not run_with_irrigation or all(
            _check_12_months(inner, {_InnerKey.IS_IRRIGATEDS})
            for inner in grouped_data.values()
        ),
        len(grouped_data.keys()) >= MIN_RUN_IN_PERIOD,
        _check_consecutive(grouped_data.keys()),
        check_cycle_site_ids_identical(cycles)
    ])

    logShouldRun(
        site,
        MODEL,
        TERM_ID,
        should_run,
        sub_model="_run_annual_water_factors",
        run_with_irrigation=run_with_irrigation
    )
    return should_run, run_with_irrigation, grouped_data


def _run_annual_water_factors(
    timestamps: list[int],
    precipitations: list[list[float]],
    pets: list[list[float]],
    is_irrigateds: Union[list[list[bool]], None] = None,
    water_factor_slope: float = 1.331,
):
    """
    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996...]`) for each year in the inventory.
    precipitations : list[list[float]]
        A list of monthly sum precipitations for each year in the inventory
        (e.g. `[[10,10,10,20,25,15,15,10,10,10,5,5]]`).
    pets list[list[float]]
        A list of monthly sum potential evapotransiprations for each year in the inventory.
    is_irrigateds list[list[bool]] | None
        A list of monthly booleans that describe whether irrigation is used in a particular calendar month for each
        year in the inventory.
    water_factor_slope : float
        The slope for mappet term to estimate water factor, dimensionless, default value: `1.331`.

    Returns
    -------
    WaterFactorResult
        An inventory of annual water factor data as a named tuple with the format
        `(timestamps: list[int], annual_water_factors: list[float])`.
    """
    is_irrigateds = [None] * len(timestamps) if is_irrigateds is None else is_irrigateds
    return WaterFactorResult(
        timestamps=timestamps,
        annual_water_factors=[
            _calc_annual_water_factor(
                monthly_precipitations,
                monthly_pets,
                monthly_is_irrigateds,
                water_factor_slope,
            )
            for monthly_precipitations, monthly_pets, monthly_is_irrigateds in zip(
                precipitations, pets, is_irrigateds
            )
        ],
    )


# --- TIER 2 SUB-MODEL: ANNUAL ORGANIC CARBON INPUTS ---


def _iterate_carbon_source(node: dict) -> Union[CarbonSource, None]:
    """
    Validates whether a node is a valid carbon source and returns
    a `CarbonSource` named tuple if yes.

    Parameters
    ----------
    node : dict
        A Hestia `Product` or `Input` node, see: https://www.hestia.earth/schema/Product
        or https://www.hestia.earth/schema/Input.

    Returns
    -------
    CarbonSource | None
        A `CarbonSource` named tuple if the node is a carbon source with the required properties, else `None`.
    """
    term = node.get("term", {})
    mass = list_sum(node.get("value", []))
    carbon_content, nitrogen_content, lignin_content = (
        get_node_property(node, term_id, False).get("value", 0)/100 for term_id in CROP_RESIDUE_PROPERTY_TERM_IDS
    )

    should_run = all([
        any([
            term.get("@id", None) in get_crop_residue_incorporated_or_left_on_field_terms(),
            term.get("termType") in CARBON_SOURCE_TERM_TYPES
        ]),
        mass > 0,
        0 < carbon_content <= 1,
        0 < nitrogen_content <= 1,
        0 < lignin_content <= 1
    ])

    return (
        CarbonSource(
            mass, carbon_content, nitrogen_content, lignin_content
        ) if should_run else None
    )


def _get_carbon_sources_from_cycles(cycles: dict) -> list[CarbonSource]:
    """
    Retrieves and formats all of the valid carbon sources from a list of cycles.

    Carbon sources can be either a Hestia `Product` node (e.g. crop residue) or `Input` node (e.g. organic amendment).

    Parameters
    ----------
    cycles : list[dict]
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    list[CarbonSource]
        A formatted list of `CarbonSource`s for the inputted `Cycle`s.
    """
    inputs_and_products = non_empty_list(flatten(
        [cycle.get("inputs", []) + cycle.get("products", []) for cycle in cycles]
    ))

    return non_empty_list([_iterate_carbon_source(node) for node in inputs_and_products])


def _should_run_annual_organic_carbon_inputs(
    site: dict,
    cycles: list[dict]
) -> tuple[bool, dict]:
    """
    Extracts, formats and checks data from the site node to determine whether or not to run the annual organic carbon
    inputs model on a specific set of Hestia `Cycle`s.

    Parameters
    ----------
    cycles : list[dict]
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    tuple[bool, dict]
        `(should_run, grouped_data)`.
    """
    grouped_cycles = group_nodes_by_year(cycles)

    grouped_data = {
        year: {
            _InnerKey.CARBON_SOURCES: _get_carbon_sources_from_cycles(_cycles)
        } for year, _cycles in grouped_cycles.items()
    }

    should_run = all([
        len(grouped_data.keys()) >= MIN_RUN_IN_PERIOD,
        _check_consecutive(grouped_data.keys()),
        check_cycle_site_ids_identical(cycles)
    ])

    logShouldRun(site, MODEL, TERM_ID, should_run, sub_model="_run_annual_organic_carbon_inputs")
    return should_run, grouped_data


def _run_annual_organic_carbon_inputs(
    timestamps: list[int],
    annual_carbon_sources: list[list[CarbonSource]],
    default_carbon_content: float = 0.42,
    default_nitrogen_content: float = 0.0085,
    default_lignin_content: float = 0.073,
):
    """
    Calculate the organic carbon input, average nitrogen content of carbon sources and average lignin content of carbon
    sources for each year of the inventory.

    `timestamps` and `annual_carbon_sources` must have the same length.

    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
    annual_carbon_sources : list[list[CarbonSource]]
        A list of carbon sources for each year of the inventory, where each carbon source is a named tupled with the
        format `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`
    default_carbon_content : float
        The default carbon content of a carbon source, decimal proportion, kg C (kg d.m.)-1, default value: `0.42`.
    default_nitrogen_content : float
        The default nitrogen content of a carbon source, decimal proportion, kg N (kg d.m.)-1, default value: `0.0085`.
    default_lignin_content : float)
        The default lignin content of a carbon source, decimal proportion, kg lignin (kg d.m.)-1,
        default value: `0.073`.

    Returns
    -------
    CarbonInputResult
        An inventory of annual carbon input data as a named tuple with the format
        `(timestamps: list[int], organic_carbon_inputs: list[float], average_nitrogen_contents: list[float],
        average_lignin_contents: list[float])`
    """
    return CarbonInputResult(
        timestamps=timestamps,
        organic_carbon_inputs=[
            _calc_total_organic_carbon_input(sources, default_carbon_content=default_carbon_content)
            for sources in annual_carbon_sources
        ],
        average_nitrogen_contents=[
            _calc_average_nitrogen_content_of_organic_carbon_sources(
                sources, default_nitrogen_content=default_nitrogen_content)
            for sources in annual_carbon_sources
        ],
        average_lignin_contents=[
            _calc_average_lignin_content_of_organic_carbon_sources(
                sources, default_lignin_content=default_lignin_content)
            for sources in annual_carbon_sources
        ],
    )


# --- TIER 2 SOC MODEL ---


def _should_run_tier_2(
    site: dict
) -> tuple:
    """
    Extracts, formats and checks data from the site and cycle nodes to determine
    determine whether or not to run the Tier 2 SOC model.

    Parameters
    ----------
    site : dict
        A Hestia `Site` node, see: https://www.hestia.earth/schema/Site.
    cycles : list[dict]
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    tuple
        `(should_run, timestamps, temperatures, precipitations, pets, carbon_sources, tillage_categories, sand_content,
        is_irrigateds, run_in_period, initial_soc_stock)`
    """
    cycles = related_cycles(site.get("@id"))

    should_run_t, grouped_temperature_data = _should_run_annual_temperature_factors(site)
    should_run_w, run_with_irrigation, grouped_water_data = _should_run_annual_water_factors(site, cycles)
    should_run_c, grouped_carbon_sources_data = _should_run_annual_organic_carbon_inputs(site, cycles)

    grouped_cycles = group_nodes_by_year(cycles)

    grouped_tillage_categories = {
        year: {
            _InnerKey.TILLAGE_CATEGORY: _assign_tier_2_ipcc_tillage_management_category(_cycles)
        } for year, _cycles in grouped_cycles.items()
    }

    # Combine all the grouped data into one dictionary
    grouped_data = reduce(merge, [grouped_temperature_data, grouped_water_data,
                          grouped_carbon_sources_data, grouped_tillage_categories])

    # Select the correct keys for data completeness based on `run_with_irrigation`
    keys = INNER_KEYS_RUN_WITH_IRRIGATION if run_with_irrigation else INNER_KEYS_RUN_WITHOUT_IRRIGATION

    # Filter out any incomplete years
    complete_data = dict(filter(
        lambda item: all([key in item[1].keys() for key in keys]),
        grouped_data.items()
    ))

    timestamps = list(complete_data)
    start_year = timestamps[0] if timestamps else 0
    end_year = timestamps[-1] if timestamps else 0

    measurements = site.get("measurements", [])

    sand_content_value, _ = most_relevant_measurement_value_by_depth_and_date(
        measurements,
        SAND_CONTENT_TERM_ID,
        f"{start_year}-12-31",
        DEPTH_UPPER,
        DEPTH_LOWER,
        depth_strict=False
    ) if timestamps else (None, None)
    sand_content = sand_content_value/100 if sand_content_value else None

    initial_soc_stock_value, initial_soc_stock_date = most_relevant_measurement_value_by_depth_and_date(
        measurements,
        TERM_ID,
        f"{end_year}-12-31",
        DEPTH_UPPER,
        DEPTH_LOWER,
        depth_strict=True
    ) if timestamps else (None, None)

    run_with_initial_soc_stock = bool(initial_soc_stock_value and initial_soc_stock_date)

    run_in_period = (
        int(abs(diff_in_years(f"{start_year}-12-31", initial_soc_stock_date)) + 1)
        if run_with_initial_soc_stock else MIN_RUN_IN_PERIOD
    ) if timestamps else 0

    timestamps = list(complete_data.keys())
    temperatures = [complete_data[year][_InnerKey.TEMPERATURES] for year in timestamps]
    precipitations = [complete_data[year][_InnerKey.PRECIPITATIONS] for year in timestamps]
    pets = [complete_data[year][_InnerKey.PETS] for year in timestamps]
    annual_carbon_sources = [complete_data[year][_InnerKey.CARBON_SOURCES] for year in timestamps]
    annual_tillage_categories = [complete_data[year][_InnerKey.TILLAGE_CATEGORY] for year in timestamps]
    is_irrigateds = (
        [complete_data[year][_InnerKey.IS_IRRIGATEDS] for year in timestamps] if run_with_irrigation else None
    )

    should_run = all([
        should_run_t,
        should_run_w,
        should_run_c,
        sand_content is not None and 0 < sand_content <= 1,
        run_in_period >= MIN_RUN_IN_PERIOD,
        len(timestamps) >= run_in_period,
        check_cycle_site_ids_identical(cycles),
        _check_consecutive(timestamps)
    ])

    logShouldRun(
        site,
        MODEL,
        TERM_ID,
        should_run,
        sub_model="_run_tier_2",
        run_with_irrigation=run_with_irrigation,
        run_with_initial_soc_stock=run_with_initial_soc_stock,
        run_in_period=run_in_period
    )

    return (
        should_run,
        timestamps,
        temperatures,
        precipitations,
        pets,
        annual_carbon_sources,
        annual_tillage_categories,
        sand_content,
        is_irrigateds,
        run_in_period,
        initial_soc_stock_value
    )


def _run_tier_2(
    timestamps: list[int],
    temperatures: list[list[float]],
    precipitations: list[list[float]],
    pets: list[list[float]],
    annual_carbon_sources: list[list[CarbonSource]],
    annual_tillage_categories: list[IpccManagementCategory],
    sand_content: float = 0.33,
    is_irrigateds: Union[list[list[bool]], None] = None,
    run_in_period: int = 5,
    initial_soc_stock: Union[float, None] = None,
    params: Union[dict[str, float], None] = None,
) -> list[dict]:
    """
    Run the IPCC Tier 2 SOC model on a time series of annual data about a site and the mangagement activities taking
    place on it. `timestamps` and `annual_`... lists must be the same length.

    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. [1995, 1996...]) for each year in the inventory.
    temperatures : list[list[float]]
        A list of monthly average temperatures for each year in the inventory.
    precipitations : list[list[float]]
        A list of monthly sum precipitations for each year in the inventory.
    pets : list[list[float]]
        A list of monthly sum potential evapotransiprations for each year in the inventory.
    annual_carbon_sources : list[list[CarbonSource]]
        A list of carbon sources for each year of the inventory, where each carbon source is a named tupled with the
        format `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`
    annual_tillage_categories : list[IpccManagementCategory)
        A list of the site"s IpccManagementCategory for each year in the inventory.
    sand_content : float
        The sand content of the site, decimal proportion, default value: `0.33`.
    is_irrigateds : list[list[bool]] | None
        A list of monthly booleans that describe whether irrigation is used in a particular calendar month for each
        year in the inventory.
    run_in_period : int
        The length of the run-in period in years, must be greater than or equal to 1, default value: `5`.
    initial_soc_stock : float | None]
        The measured or pre-computed initial SOC stock at the end of the run-in period, kg C ha-1.
    params : dict | None
        Overrides for the model parameters. If `None` only default parameters will be used.

    Returns
    -------
    list[dict]
        A list of Hestia `Measurement` nodes containing the calculated SOC stocks and additional relevant data.
    """

    # --- MERGE ANY USER-SET PARAMETERS WITH THE IPCC DEFAULTS ---

    params = DEFAULT_PARAMS | (params or {})

    # --- COMPUTE FACTORS AND CARBON INPUTS ---

    _, annual_temperature_factors = _run_annual_temperature_factors(
        timestamps,
        temperatures,
        maximum_temperature=params.get("maximum_temperature"),
        optimum_temperature=params.get("optimum_temperature")
    )

    _, annual_water_factors = _run_annual_water_factors(
        timestamps,
        precipitations,
        pets,
        is_irrigateds,
        water_factor_slope=params.get("water_factor_slope")
    )

    (
        _,
        annual_organic_carbon_inputs,
        annual_nitrogen_contents,
        annual_lignin_contents
    ) = _run_annual_organic_carbon_inputs(
        timestamps,
        annual_carbon_sources,
        default_carbon_content=params.get("default_carbon_content"),
        default_nitrogen_content=params.get("default_nitrogen_content"),
        default_lignin_content=params.get("default_lignin_content")
    )

    # --- RUN THE MODEL ---

    result = _run_soc_stocks(
        timestamps=timestamps,
        annual_temperature_factors=annual_temperature_factors,
        annual_water_factors=annual_water_factors,
        annual_organic_carbon_inputs=annual_organic_carbon_inputs,
        annual_average_nitrogen_contents_of_organic_carbon_sources=annual_nitrogen_contents,
        annual_average_lignin_contents_of_organic_carbon_sources=annual_lignin_contents,
        annual_tillage_categories=annual_tillage_categories,
        sand_content=sand_content,
        run_in_period=run_in_period,
        initial_soc_stock=initial_soc_stock,
        params=params
    )

    values = [
        _calc_tier_2_soc_stock(
            active,
            slow,
            passive
        ) for active, slow, passive in zip(
            result.active_pool_soc_stocks,
            result.slow_pool_soc_stocks,
            result.passive_pool_soc_stocks
        )
    ]

    # --- RETURN MEASUREMENT NODES ---

    return [
        _measurement(
            year,
            value,
            MeasurementMethodClassification.TIER_2_MODEL.value
        ) for year, value in zip(
            result.timestamps,
            values
        )
    ]


# --- TIER 1 FUNCTIONS ---


def _find_closest_value_index(
    lst: Iterable[Union[int, float]], target_value: Union[int, float]
) -> Optional[int]:
    """
    Find the index of the closest value in a list.

    Parameters
    ----------
    lst : iterable[int | float]
        The list of integers.
    target : int | float
        The target value.

    Returns
    -------
    int
        The index of the closest value.
    """
    should_run = all([
        lst,
        all(isinstance(element, (int, float)) for element in lst),
        isinstance(target_value, (int, float))
    ])
    return min(range(len(lst)), key=lambda i: abs(lst[i] - target_value)) if should_run else None


def _retrieve_soc_ref(
    eco_climate_zone: int,
    ipcc_soil_category: IpccSoilCategory
) -> float:
    """
    Retrieve the soil organic carbon (SOC) reference value for a given combination of eco-climate zone
    and IPCC soil category.

    See [IPCC (2019) Vol. 4, Ch. 2, Table 2.3](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html)
    for more information.

    Parameters
    ----------
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    ipcc_soil_category : IpccSoilCategory
        The IPCC soil category of the site.

    Returns
    -------
    float
        The reference condition soil organic carbon (SOC) stock in the 0-30cm depth interval, kg C ha-1.
    """
    col_name = _get_eco_climate_zone_lookup_column(ipcc_soil_category)
    return get_ecoClimateZone_lookup_value(eco_climate_zone, col_name)


def _retrieve_soc_stock_factors(
    eco_climate_zone: int,
    ipcc_land_use_category: IpccLandUseCategory,
    ipcc_management_category: IpccManagementCategory,
    ipcc_carbon_input_category: IpccCarbonInputCategory
) -> StockChangeFactors:
    """
    Retrieve the stock change factors for soil organic carbon (SOC)
    based on a given combination of land use, management and carbon
    input.

    Parameters
    ----------
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    ipcc_land_use_category : IpccLandUseCategory
        The IPCC land use category for the inventory year.
    ipcc_management_category : IpccManagementCategory
        The IPCC land use category for the inventory year.
    ipcc_carbon_input_category : IpccCarbonInputCategory
        The IPCC land use category for the inventory year.

    Returns
    -------
    StockChangeFactors
        A named tuple containing the retrieved stock change factors for SOC.
    """
    DEFAULT_FACTOR = 1

    EXCLUDED_LAND_USE_CATEGORIES = {
        IpccLandUseCategory.FOREST,
        IpccLandUseCategory.NATIVE,
        IpccLandUseCategory.OTHER
    }

    EXCLUDED_MANAGEMENT_CATEGORIES = {
        IpccManagementCategory.OTHER
    }

    EXCLUDED_CARBON_INPUT_CATEGORIES = {
        IpccCarbonInputCategory.OTHER
    }

    def get_factor(category, exclude_set):
        return (
            DEFAULT_FACTOR if category in exclude_set
            else get_ecoClimateZone_lookup_value(
                eco_climate_zone, _get_eco_climate_zone_lookup_column(category)
            )
        )

    land_use_factor = get_factor(ipcc_land_use_category, EXCLUDED_LAND_USE_CATEGORIES)
    management_factor = get_factor(ipcc_management_category, EXCLUDED_MANAGEMENT_CATEGORIES)
    carbon_input_factor = get_factor(ipcc_carbon_input_category, EXCLUDED_CARBON_INPUT_CATEGORIES)

    return StockChangeFactors(land_use_factor, management_factor, carbon_input_factor)


def _calc_soc_equilibrium(
    soc_ref: float,
    land_use_factor: float,
    management_factor: float,
    carbon_input_factor: float
) -> float:
    """
    Calculate the soil organic carbon (SOC) equilibrium based on reference SOC and factors.

    In the tier 1 model, SOC equilibriums are considered to be reached after 20 years of
    consistant land use, management and carbon input.

    Parameters
    ----------
    soc_ref : float
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.
    land_use_factor : float
        The stock change factor for mineral soil organic C land-use systems or sub-systems
        for a particular land-use, dimensionless.
    management_factor : float
        The stock change factor for mineral soil organic C for management regime, dimensionless.
    carbon_input_factor : float
        The stock change factor for mineral soil organic C for the input of organic amendments, dimensionless.

    Returns
    -------
    float
        The calculated SOC equilibrium, kg C ha-1.
    """
    return soc_ref * land_use_factor * management_factor * carbon_input_factor


def _calc_regime_start_index(
    current_index: int, soc_equilibriums: list[float], default: Optional[int] = None
) -> Optional[int]:
    """
    Calculate the start index of the SOC regime based on the current index and equilibriums.

    Parameters
    ----------
    current_index : int
        The current index in the SOC equilibriums list.
    soc_equilibriums : list[float]
        List of SOC equilibriums.
    default : Any | None
        Default value to return if no suitable start index is found, by default `None`.

    Returns
    -------
    int | None
        The calculated start index for the SOC regime.
    """

    def calc_forward_index(sliced_reverse_index: int) -> int:
        """
        Calculate the forward index based on a sliced reverse index.
        """
        return current_index - sliced_reverse_index - 1

    current_soc_equilibrium = soc_equilibriums[current_index]
    sliced_reversed_soc_equilibriums = reversed(soc_equilibriums[0:current_index])

    return next(
        (
            calc_forward_index(sliced_reverse_index) for sliced_reverse_index, prev_equilibrium
            in enumerate(sliced_reversed_soc_equilibriums)
            if not prev_equilibrium == current_soc_equilibrium
        ),
        default
    )


def _iterate_soc_equilibriums(
    timestamps: list[int], soc_equilibriums: list[float]
) -> tuple[list[int], list[float]]:
    """
    Iterate over SOC equilibriums, inserting timestamps and soc_equilibriums for any
    missing years where SOC would have reached equilibrium.

    Parameters
    ----------
    timestamps : list[int]
        List of timestamps for each year in the inventory.
    soc_equilibriums : list[float]
        List of SOC equilibriums for each year in the inventory.

    Returns
    -------
    tuple[list[int], list[float]]
        Updated `timestamps` and `soc_equilibriums`.
    """
    iterated_timestamps = list(timestamps)
    iterated_soc_equilibriums = list(soc_equilibriums)

    def calc_equilibrium_reached_timestamp(index: int) -> int:
        """
        Calculate the timestamp when SOC equilibrium is reached based on the current index.
        """
        regime_start_index = _calc_regime_start_index(index, soc_equilibriums)
        regime_start_timestamp = (
            timestamps[regime_start_index] if regime_start_index is not None
            else timestamps[0] - EQUILIBRIUM_TRANSITION_PERIOD
        )
        return regime_start_timestamp + EQUILIBRIUM_TRANSITION_PERIOD

    def is_missing_equilibrium_year(
        timestamp: int, equilibrium_reached_timestamp: int
    ) -> bool:
        """
        Check if the given timestamp is after equilibrium and the equilibrium year is missing.
        """
        return (
            timestamp > equilibrium_reached_timestamp
            and equilibrium_reached_timestamp not in iterated_timestamps
        )

    for index, (timestamp, soc_equilibrium) in enumerate(zip(timestamps, soc_equilibriums)):

        equilibrium_reached_timestamp = calc_equilibrium_reached_timestamp(index)

        if is_missing_equilibrium_year(timestamp, equilibrium_reached_timestamp):
            iterated_timestamps.insert(index, equilibrium_reached_timestamp)
            iterated_soc_equilibriums.insert(index, soc_equilibrium)

    return iterated_timestamps, iterated_soc_equilibriums


def _run_soc_equilibriums(
    timestamps: list[int],
    ipcc_land_use_categories: list[IpccLandUseCategory],
    ipcc_management_categories: list[IpccManagementCategory],
    ipcc_carbon_input_categories: list[IpccCarbonInputCategory],
    eco_climate_zone: int,
    soc_ref: float
) -> tuple[list[int], list[float]]:
    """
    Run the soil organic carbon (SOC) equilibriums calculation for each year in the inventory.

    Missing years where SOC equilibrium would be reached are inserted to allow for annual
    SOC change to be calculated correctly.

    Parameters
    ----------
    timestamps : list[int]
        A list of timestamps for each year in the inventory.
    ipcc_land_use_categories : list[IpccLandUseCategory]
        A list of IPCC land use categories for each year in the inventory.
    ipcc_management_categories : list[IpccManagementCategory]
        A list of IPCC management categories for each year in the inventory.
    ipcc_carbon_input_categories : list[IpccCarbonInputCategory]
        A list of IPCC carbon input categories for each year in the inventory.
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    soc_ref : float
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.

    Returns
    -------
    tuple[list[int], list[float]]
        `timestamps` and `soc_equilibriums` for each year in the inventory, including any
        missing years where SOC equilibrium would have been reached.
    """

    # Calculate SOC equilibriums for each year
    soc_equilibriums = [
        _calc_soc_equilibrium(
            soc_ref,
            *_retrieve_soc_stock_factors(
                eco_climate_zone,
                land_use_category,
                management_category,
                carbon_input_category
            )
        ) for land_use_category, management_category, carbon_input_category in zip(
            ipcc_land_use_categories,
            ipcc_management_categories,
            ipcc_carbon_input_categories
        )
    ]

    # Insert missing years where SOC equilibrium would have been reached
    iterated_timestamps, iterated_soc_equilibriums = (
        _iterate_soc_equilibriums(timestamps, soc_equilibriums)
    )

    return iterated_timestamps, iterated_soc_equilibriums


def _calc_tier_1_soc_stocks(
    timestamps: list[int],
    soc_equilibriums: list[float],
) -> list[float]:
    """
    Calculate soil organic carbon (SOC) stocks (kg C ha-1) in the 0-30cm depth interval for each year in
    the inventory.

    Parameters
    ----------
    timestamps : list[int]
        A list of timestamps for each year in the inventory.
    soc_equilibriums : list[float]
        A list of SOC equilibriums for each year in the inventory.

    Returns
    -------
    list[float]
        SOC stocks for each year in the inventory.
    """
    soc_stocks = [soc_equilibriums[0]]

    for index in range(1, len(soc_equilibriums)):

        timestamp = timestamps[index]
        soc_equilibrium = soc_equilibriums[index]

        regime_start_index = _calc_regime_start_index(index, soc_equilibriums)

        regime_start_timestamp = (
            timestamps[regime_start_index]
            if regime_start_index is not None
            else timestamps[0] - EQUILIBRIUM_TRANSITION_PERIOD
        )

        regime_start_soc_stock = soc_stocks[regime_start_index or 0]

        regime_duration = timestamp - regime_start_timestamp

        time_ratio = min(regime_duration / EQUILIBRIUM_TRANSITION_PERIOD, 1)
        soc_delta = (soc_equilibrium - regime_start_soc_stock) * time_ratio

        soc_stocks.append(regime_start_soc_stock + soc_delta)

    return soc_stocks


def _calc_measurement_scaling_factor(
    measured_soc: float, calculated_soc: float
) -> float:
    """
    Calculate the scaling factor soil organic carbon (SOC) values based
    on the ratio between measured and calculated values.

    Parameters
    ----------
    measured_soc : float
        The measured SOC value.
    calculated_soc : float
        The calculated SOC value.

    Returns
    -------
    float
        The scaling factor.
    """
    return measured_soc / calculated_soc


def _scale_soc_stocks(
    soc_stocks: list[float],
    soc_measurement_value: Union[float, None] = None,
    soc_measurement_index: Union[int, None] = None
) -> list[float]:
    """
    Scale soil organic carbon (SOC) stocks based on a measurement value and index.

    Parameters
    ----------
    soc_stocks : list[float]
        The list of SOC stocks to be scaled.
    soc_measurement_value : float | None, optional
        The measured SOC value for scaling. If None, no scaling is applied.
    soc_measurement_index : int | None, optional
        The index of the calculated SOC stock to compare against the SOC measurement.

    Returns
    -------
    list[float]
        The scaled SOC stocks.
    """

    measurement_scaling_factor = (
        _calc_measurement_scaling_factor(
            soc_measurement_value,
            soc_stocks[soc_measurement_index]
        ) if soc_measurement_value and soc_measurement_index is not None
        else 1
    )

    return [value * measurement_scaling_factor for value in soc_stocks]


# --- GET THE ECO-CLIMATE ZONE FROM THE MEASUREMENTS ---


def _get_eco_climate_zone(measurements: list[dict]) -> Optional[int]:
    """
    Get the eco-climate zone value from a list of measurements.

    Parameters
    ----------
    measurements : list[dict]
        A list of measurement nodes.

    Returns
    -------
    int | None
        The eco-climate zone value if found, otherwise None.
    """
    eco_climate_zone = find_term_match(measurements, "ecoClimateZone")
    # return measurement_value(eco_climate_zone) or None
    return get_node_value(eco_climate_zone) or None


# --- ASSIGN IPCC SOIL CATEGORY TO SITE ---


def _check_soil_category(
    soil_types: list[dict],
    usda_soil_types: list[dict],
    *,
    key: IpccSoilCategory,
    **_
) -> bool:
    """
    Check if the soil category matches the given key.

    Parameters
    ----------
    soil_types : list[dict]
        List of soil type measurement nodes.
    usda_soil_types : list[dict]
        List of USDA soil type measurement nodes
    key : IpccSoilCategory
        The IPCC soil category to check.

    Returns
    -------
    bool
        `True` if the soil category matches, `False` otherwise.
    """
    SOIL_TYPE_LOOKUP = LOOKUPS["soilType"]
    USDA_SOIL_TYPE_LOOKUP = LOOKUPS["usdaSoilType"]

    target_lookup_values = IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE.get(key, None)

    is_soil_type_match = cumulative_nodes_lookup_match(
        soil_types,
        lookup=SOIL_TYPE_LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    is_usda_soil_type_match = cumulative_nodes_lookup_match(
        usda_soil_types,
        lookup=USDA_SOIL_TYPE_LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    return is_soil_type_match or is_usda_soil_type_match


def _check_sandy_soils(
    soil_types: list[dict],
    usda_soil_types: list[dict],
    *,
    is_sandy: bool,
    **_
) -> bool:
    """
    Check if the soils are sandy.

    This function is special case of `_check_soil_category`.

    Parameters
    ----------
    soil_types : list[dict]
        List of soil type measurement nodes.
    usda_soil_types : list[dict]
        List of USDA soil type measurement nodes
    is_sandy : bool
        True if the soils are sandy, False otherwise.

    Returns
    -------
    bool
        `True` if the soil category matches, `False` otherwise.
    """
    KEY = IpccSoilCategory.SANDY_SOILS
    return _check_soil_category(soil_types, usda_soil_types, key=KEY) or is_sandy


SOIL_CATEGORY_DECISION_TREE = {
    IpccSoilCategory.ORGANIC_SOILS: _check_soil_category,
    IpccSoilCategory.SANDY_SOILS: _check_sandy_soils,
    IpccSoilCategory.WETLAND_SOILS: _check_soil_category,
    IpccSoilCategory.VOLCANIC_SOILS: _check_soil_category,
    IpccSoilCategory.SPODIC_SOILS: _check_soil_category,
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: _check_soil_category,
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: _check_soil_category
}
"""
A decision tree mapping IPCC soil categories to corresponding check functions.

Key: IpccSoilCategory
Value: Corresponding function for checking the match of the given soil category based on soil types.
"""


def _assign_ipcc_soil_category(
    measurements: list[dict],
    default: IpccSoilCategory = IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS
) -> IpccSoilCategory:
    """
    Assign an IPCC soil category based on a site"s measurement nodes.

    Parameters
    ----------
    measurements : list[dict]
        List of measurement nodes.
    default : IpccSoilCategory, optional
        The default soil category if none matches, by default IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS.

    Returns
    -------
    IpccSoilCategory
        The assigned IPCC soil category.
    """
    soil_types = filter_list_term_type(measurements, TermTermType.SOILTYPE)
    usda_soil_types = filter_list_term_type(measurements, TermTermType.USDASOILTYPE)

    clay_content = get_node_value(find_term_match(measurements, CLAY_CONTENT_TERM_ID))
    sand_content = get_node_value(find_term_match(measurements, SAND_CONTENT_TERM_ID))
    # clay_content = measurement_value(find_term_match(measurements, CLAY_CONTENT_TERM_ID))
    # sand_content = measurement_value(find_term_match(measurements, SAND_CONTENT_TERM_ID))

    is_sandy = clay_content < CLAY_CONTENT_MAX and sand_content > SAND_CONTENT_MIN

    return next(
        (
            key for key in SOIL_CATEGORY_DECISION_TREE
            if SOIL_CATEGORY_DECISION_TREE[key](
                soil_types,
                usda_soil_types,
                key=key,
                is_sandy=is_sandy
            )
        ),
        default
    ) if len(soil_types) > 0 or len(usda_soil_types) > 0 else default


# --- ASSIGN IPCC LAND USE CATEGORY ---


def _has_irrigation(water_regime_nodes: list[dict]) -> bool:
    """
    Check if irrigation is present in the water regime nodes.

    Parameters
    ----------
    water_regime_nodes : List[dict]
        List of water regime nodes to be checked.

    Returns
    -------
    bool
        `True` if irrigation is present, `False` otherwise.
    """
    return cumulative_nodes_term_match(
        water_regime_nodes,
        target_term_ids=get_irrigated_terms(),
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )


def _check_ipcc_land_use_category(
    site_type: str,
    *,
    key: IpccLandUseCategory,
    **_
):
    """
    Check if the site type matches the target site type for the given key.

    Parameters
    ----------
    site_type : str
        The site type to check.
    key : IpccLandUseCategory
        The IPCC land use category to check.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.

    """
    target_site_type = IPCC_LAND_USE_CATEGORY_TO_SITE_TYPE.get(key, None)

    return site_type == target_site_type


def _check_cropland_land_use_category(
    site_type: str,
    *,
    key: IpccLandUseCategory,
    land_cover_nodes: list[dict],
    **_
) -> bool:
    """
    Check if the site type and land cover nodes match the target conditions for a cropland IpccLandUseCategory.

    This function is special case of `_check_cropland_land_use_category`.

    Parameters
    ----------
    site_type : str
        The site type to check.
    key : IpccLandUseCategory
        The IPCC land use category to check.
    land_cover_nodes : list[dict]
        List of land cover nodes.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    LOOKUP = LOOKUPS["landCover"][0]
    target_lookup_values = IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE.get(key, None)

    return _check_ipcc_land_use_category(site_type, key=key) and cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )


def _check_paddy_rice_cultivation_category(
    site_type: str,
    *,
    land_cover_nodes: list[dict],
    is_irrigated_upland_rice: bool,
    **_
) -> bool:
    """
    Check if the site type and land cover nodes match the target conditions for paddy rice cultivation.

    This function is special case of `_check_cropland_land_use_category`.

    Parameters
    ----------
    site_type : str
        The site type to check.
    land_cover_nodes : list[dict]
        List of land cover nodes.
    is_irrigated_upland_rice : bool
        Flag indicating if the land cover irrigated upland rice.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    KEY = IpccLandUseCategory.PADDY_RICE_CULTIVATION
    return _check_cropland_land_use_category(
        site_type, key=KEY, land_cover_nodes=land_cover_nodes
    ) or is_irrigated_upland_rice


def _check_annual_crops_category(
    site_type: str,
    *,
    land_cover_nodes: list[dict],
    has_long_fallow: bool,
    **_
) -> bool:
    """
    Check if the site type and land cover nodes match the target conditions for annual crops.

    This function is special case of `_check_cropland_land_use_category`.

    Parameters
    ----------
    site_type : str
        The site type to check.
    land_cover_nodes : list[dict]
        List of land cover nodes.
    has_long_fallow : bool
        Flag indicating if there is long fallow.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    KEY = IpccLandUseCategory.ANNUAL_CROPS
    return _check_cropland_land_use_category(
        site_type, key=KEY, land_cover_nodes=land_cover_nodes
    ) and not has_long_fallow


def _check_annual_crops_wet_category(
    site_type: str,
    *,
    land_cover_nodes: list[dict],
    has_wetland_soils: bool,
    has_long_fallow: bool,
    **_
):
    """
    Check if the site type and land cover nodes match the target conditions for annual crops on wetland soils.

    This function is special case of `_check_cropland_land_use_category`.

    Parameters
    ----------
    site_type : str
        The site type to check.
    land_cover_nodes : list[dict]
        List of land cover nodes.
    has_wetland_soils : bool
        Flag indicating if the site is classified as `IpccSoilCategory.WETLAND_SOILS`
    has_long_fallow : bool
        Flag indicating if there is long fallow.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    KEY = IpccLandUseCategory.ANNUAL_CROPS_WET
    return _check_cropland_land_use_category(
        site_type, key=KEY, land_cover_nodes=land_cover_nodes
    ) and has_wetland_soils and not has_long_fallow


LAND_USE_CATEGORY_DECISION_TREE = {
    IpccLandUseCategory.GRASSLAND: _check_ipcc_land_use_category,
    IpccLandUseCategory.PERENNIAL_CROPS: _check_cropland_land_use_category,
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: _check_paddy_rice_cultivation_category,
    IpccLandUseCategory.ANNUAL_CROPS_WET: _check_annual_crops_wet_category,
    IpccLandUseCategory.ANNUAL_CROPS: _check_annual_crops_category,
    IpccLandUseCategory.SET_ASIDE: _check_ipcc_land_use_category,
    IpccLandUseCategory.FOREST: _check_ipcc_land_use_category,
    IpccLandUseCategory.NATIVE: _check_ipcc_land_use_category,
    IpccLandUseCategory.OTHER: _check_ipcc_land_use_category
}
"""
A decision tree mapping IPCC soil categories to corresponding check functions.

Key: IpccLandUseCategory
Value: Corresponding function for checking the match of the given land use category based on site type
and land cover nodes.
"""


def _assign_ipcc_land_use_category(
    site_type: str,
    management_nodes: list[dict],
    ipcc_soil_category: IpccSoilCategory
) -> IpccLandUseCategory:
    """
    Assigns IPCC land use category based on site type, management nodes, and soil category.

    Parameters
    ----------
    site_type : str
        The type of the site.
    management_nodes : list[dict]
        List of management nodes.
    ipcc_soil_category : IpccSoilCategory
        The site"s assigned IPCC soil category.

    Returns
    -------
    IpccLandUseCategory
        Assigned IPCC land use category.
    """
    DECISION_TREE = LAND_USE_CATEGORY_DECISION_TREE
    DEFAULT = IpccLandUseCategory.OTHER

    land_cover_nodes = filter_list_term_type(
        management_nodes, [TermTermType.LANDCOVER]
    )

    water_regime_nodes = filter_list_term_type(
        management_nodes, [TermTermType.WATERREGIME]
    )

    has_irrigation = _has_irrigation(water_regime_nodes)

    is_upland_rice = cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=get_rice_plant_upland_terms(),
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    is_irrigated_upland_rice = is_upland_rice and has_irrigation

    # SUPER_MAJORITY_AREA_THRESHOLD
    has_long_fallow = cumulative_nodes_match(
        lambda node: get_node_property(node, LONG_FALLOW_CROP_TERM_ID, False).get("value", 0),
        land_cover_nodes,
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    has_wetland_soils = ipcc_soil_category is IpccSoilCategory.WETLAND_SOILS

    should_run = bool(site_type)

    return next(
        (
            key for key in DECISION_TREE
            if DECISION_TREE[key](
                site_type,
                key=key,
                land_cover_nodes=land_cover_nodes,
                is_irrigated_upland_rice=is_irrigated_upland_rice,
                has_long_fallow=has_long_fallow,
                has_wetland_soils=has_wetland_soils
            )
        ),
        DEFAULT
    ) if should_run else DEFAULT


# --- ASSIGN IPCC MANAGEMENT CATEGORY ---


def _check_grassland_ipcc_management_category(
    *,
    land_cover_nodes: list[dict],
    key: IpccManagementCategory,
    **_
) -> bool:
    """
    Check if the land cover nodes match the target conditions for a grassland IpccManagementCategory.

    Parameters
    ----------
    land_cover_nodes : List[dict]
        List of land cover nodes to be checked.
    key : IpccManagementCategory
        The IPCC management category to check.

    Returns
    -------
    bool
        `True` if the conditions match the specified management category, `False` otherwise.
    """
    target_term_id = IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID.get(key, None)

    return cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=target_term_id,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )


def _check_tillage_ipcc_management_category(*, tillage_nodes: list[dict], key: IpccManagementCategory, **_) -> bool:
    """
    Check if the tillage nodes match the target conditions for a tillage IpccManagementCategory.

    Parameters
    ----------
    tillage_nodes : List[dict]
        List of tillage nodes to be checked.
    key : IpccManagementCategory
        The IPCC management category to check.

    Returns
    -------
    bool
        `True` if the conditions match the specified management category, `False` otherwise.
    """
    LOOKUP = LOOKUPS["tillage"]
    target_lookup_values = IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE.get(key, None)

    return cumulative_nodes_lookup_match(
        tillage_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )


GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.SEVERELY_DEGRADED: _check_grassland_ipcc_management_category,
    IpccManagementCategory.IMPROVED_GRASSLAND: _check_grassland_ipcc_management_category,
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: _check_grassland_ipcc_management_category,
    IpccManagementCategory.NOMINALLY_MANAGED: _check_grassland_ipcc_management_category,
    IpccManagementCategory.OTHER: _check_grassland_ipcc_management_category
}
"""
Decision tree mapping IPCC management categories to corresponding check functions for grassland.

Key: IpccManagementCategory
Value: Corresponding function for checking the match of the given management category based on land cover nodes.
"""

TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.FULL_TILLAGE: _check_tillage_ipcc_management_category,
    IpccManagementCategory.REDUCED_TILLAGE: _check_tillage_ipcc_management_category,
    IpccManagementCategory.NO_TILLAGE: _check_tillage_ipcc_management_category
}
"""
Decision tree mapping IPCC management categories to corresponding check functions for tillage.

Key: IpccManagementCategory
Value: Corresponding function for checking the match of the given management category based on tillage nodes.
"""

IPCC_LAND_USE_CATEGORY_TO_DECISION_TREE = {
    IpccLandUseCategory.GRASSLAND: GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE,
    IpccLandUseCategory.ANNUAL_CROPS_WET: TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE,
    IpccLandUseCategory.ANNUAL_CROPS: TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE
}
"""
Decision tree mapping IPCC land use categories to corresponding decision trees for management categories.

Key: IpccLandUseCategory
Value: Corresponding decision tree for IPCC management categories based on land use categories.
"""

IPCC_LAND_USE_CATEGORY_TO_DEFAULT_IPCC_MANAGEMENT_CATEGORY = {
    IpccLandUseCategory.GRASSLAND: IpccManagementCategory.NOMINALLY_MANAGED,
    IpccLandUseCategory.ANNUAL_CROPS_WET: IpccManagementCategory.FULL_TILLAGE,
    IpccLandUseCategory.ANNUAL_CROPS: IpccManagementCategory.FULL_TILLAGE
}
"""
Mapping of default IPCC management categories for each IPCC land use category.

Key: IpccLandUseCategory
Value: Default IPCC management category for the given land use category.
"""


def _assign_ipcc_management_category(
    management_nodes: list[dict],
    ipcc_land_use_category: IpccLandUseCategory
) -> IpccManagementCategory:
    """
    Assign an IPCC Management Category based on the given management nodes and IPCC Land Use Category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes.
    ipcc_land_use_category : IpccLandUseCategory
        The IPCC Land Use Category.

    Returns
    -------
    IpccManagementCategory
        The assigned IPCC Management Category.
    """
    decision_tree = IPCC_LAND_USE_CATEGORY_TO_DECISION_TREE.get(
        ipcc_land_use_category, {}
    )
    default = IPCC_LAND_USE_CATEGORY_TO_DEFAULT_IPCC_MANAGEMENT_CATEGORY.get(
        ipcc_land_use_category, IpccManagementCategory.OTHER
    )

    land_cover_nodes = filter_list_term_type(
        management_nodes, [TermTermType.LANDCOVER]
    )
    tillage_nodes = filter_list_term_type(
        management_nodes, [TermTermType.TILLAGE]
    )

    should_run = (
        len(land_cover_nodes) > 0 if decision_tree == GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE
        else len(tillage_nodes) > 0
    )

    return next(
        (
            key for key in decision_tree
            if decision_tree[key](
                land_cover_nodes=land_cover_nodes,
                tillage_nodes=tillage_nodes,
                key=key
            )
        ),
        default
    ) if should_run else default


# --- ASSIGN IPCC CARBON INPUT CATEGORY ---


GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_TO_MIN_NUM_IMPROVEMENTS = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: 2,
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: 1
}
"""
A mapping from IPCC Grassland Carbon Input Categories to the minimum number of improvements required.

Key: IpccCarbonInputCategory
Value: Minimum number of improvements required for the corresponding Grassland Carbon Input Category.
"""


def _check_grassland_ipcc_carbon_input_category(
    carbon_input_args: CarbonInputArgs,
    *,
    key: IpccCarbonInputCategory
) -> bool:
    """
    Checks if the given carbon input arguments satisfy the conditions for a specific
    Grassland IPCC Carbon Input Category.

    Parameters
    ----------
    carbon_input_args : CarbonInputArgs
        The carbon input arguments.
    key : IpccCarbonInputCategory
        The grassland IPCC Carbon Input Category to check.

    Returns
    -------
    bool
        `True` if the conditions for the specified category are met; otherwise, `False`.
    """
    min_improvements = (
        GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_TO_MIN_NUM_IMPROVEMENTS[key]
    )
    return carbon_input_args.num_grassland_improvements >= min_improvements


def _check_cropland_high_with_manure_category(
    carbon_input_args: CarbonInputArgs,
    **_
) -> Optional[int]:
    """
    Checks the Cropland High with Manure IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    carbon_input_args : CarbonInputArgs
        The carbon input arguments.

    Returns
    -------
    int | none
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            not carbon_input_args.has_low_residue_producing_crops,
            not carbon_input_args.has_bare_fallow,
            carbon_input_args.has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            carbon_input_args.has_animal_manure_used
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_high_without_manure_category(
    carbon_input_args: CarbonInputArgs, **_
) -> Optional[int]:
    """
    Checks the Cropland High without Manure IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    carbon_input_args : CarbonInputArgs
        The carbon input arguments.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            not carbon_input_args.has_low_residue_producing_crops,
            not carbon_input_args.has_bare_fallow,
            carbon_input_args.has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            any([
                carbon_input_args.has_irrigation,
                carbon_input_args.has_practice_increasing_c_input,
                carbon_input_args.has_cover_crop,
                carbon_input_args.has_organic_fertiliser_or_soil_amendment_used
            ]),
            not carbon_input_args.has_animal_manure_used
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_medium_category(
    carbon_input_args: CarbonInputArgs,
    **_
) -> Optional[int]:
    """
    Checks the Cropland Medium IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    carbon_input_args : CarbonInputArgs
        The carbon input arguments.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            carbon_input_args.has_residue_removed_or_burnt,
            carbon_input_args.has_animal_manure_used
        ]),
        2: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            any([
                carbon_input_args.has_low_residue_producing_crops,
                carbon_input_args.has_bare_fallow
            ]),
            any([
                carbon_input_args.has_irrigation,
                carbon_input_args.has_practice_increasing_c_input,
                carbon_input_args.has_cover_crop,
                carbon_input_args.has_organic_fertiliser_or_soil_amendment_used,
            ])
        ]),
        3: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            not carbon_input_args.has_low_residue_producing_crops,
            not carbon_input_args.has_bare_fallow,
            not carbon_input_args.has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            any([
                carbon_input_args.has_irrigation,
                carbon_input_args.has_practice_increasing_c_input,
                carbon_input_args.has_cover_crop,
                carbon_input_args.has_organic_fertiliser_or_soil_amendment_used
            ])
        ]),
        4: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            not carbon_input_args.has_low_residue_producing_crops,
            not carbon_input_args.has_bare_fallow,
            carbon_input_args.has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            not carbon_input_args.has_irrigation,
            not carbon_input_args.has_organic_fertiliser_or_soil_amendment_used,
            not carbon_input_args.has_practice_increasing_c_input,
            not carbon_input_args.has_cover_crop
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_low_category(
    carbon_input_args: CarbonInputArgs,
    **_
) -> Optional[int]:
    """
    Checks the Cropland Low IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    carbon_input_args : CarbonInputArgs
        The carbon input arguments.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            carbon_input_args.has_residue_removed_or_burnt,
            not carbon_input_args.has_animal_manure_used
        ]),
        2: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            any([
                carbon_input_args.has_low_residue_producing_crops,
                carbon_input_args.has_bare_fallow
            ]),
            not carbon_input_args.has_irrigation,
            not carbon_input_args.has_practice_increasing_c_input,
            not carbon_input_args.has_cover_crop,
            not carbon_input_args.has_organic_fertiliser_or_soil_amendment_used
        ]),
        3: all([
            not carbon_input_args.has_residue_removed_or_burnt,
            not carbon_input_args.has_low_residue_producing_crops,
            not carbon_input_args.has_bare_fallow,
            not carbon_input_args.has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            not carbon_input_args.has_irrigation,
            not carbon_input_args.has_organic_fertiliser_or_soil_amendment_used,
            not carbon_input_args.has_practice_increasing_c_input,
            not carbon_input_args.has_cover_crop
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _make_carbon_input_args(
    management_nodes: list[dict]
) -> CarbonInputArgs:
    """
    Creates CarbonInputArgs based on the provided list of management nodes.

    Parameters
    ----------
    management_nodes : list[dict]
        The list of management nodes.

    Returns
    -------
    CarbonInputArgs
        The carbon input arguments.
    """

    PRACTICE_INCREASING_C_INPUT_LOOKUP = LOOKUPS["landUseManagement"]
    LOW_RESIDUE_PRODUCING_CROP_LOOKUP = LOOKUPS["landCover"][1]
    N_FIXING_CROP_LOOKUP = LOOKUPS["landCover"][2]

    # To prevent double counting already explicitly checked practices.
    EXCLUDED_PRACTICE_TERM_IDS = {
        IMPROVED_PASTURE_TERM_ID,
        ANIMAL_MANURE_USED_TERM_ID,
        INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID,
        ORGANIC_FERTILISER_USED_TERM_ID
    }

    crop_residue_management_nodes = filter_list_term_type(
        management_nodes, [TermTermType.CROPRESIDUEMANAGEMENT]
    )

    land_cover_nodes = filter_list_term_type(
        management_nodes, [TermTermType.LANDCOVER]
    )

    land_use_management_nodes = filter_list_term_type(
        management_nodes, [TermTermType.LANDUSEMANAGEMENT]
    )

    water_regime_nodes = filter_list_term_type(
        management_nodes, [TermTermType.WATERREGIME]
    )

    has_irrigation = _has_irrigation(water_regime_nodes)

    has_residue_removed_or_burnt = cumulative_nodes_term_match(
        crop_residue_management_nodes,
        target_term_ids=get_residue_removed_or_burnt_terms(),
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    # SUPER_MAJORITY_AREA_THRESHOLD
    has_low_residue_producing_crops = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=LOW_RESIDUE_PRODUCING_CROP_LOOKUP,
        target_lookup_values=True,
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    has_bare_fallow = cumulative_nodes_term_match(
        land_use_management_nodes,
        target_term_ids=SHORT_BARE_FALLOW_TERM_ID,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    has_n_fixing_crop = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=N_FIXING_CROP_LOOKUP,
        target_lookup_values=True,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    has_inorganic_n_fertiliser_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID)
    )

    has_n_fixing_crop_or_inorganic_n_fertiliser_used = (
        has_n_fixing_crop or has_inorganic_n_fertiliser_used
    )

    has_practice_increasing_c_input = cumulative_nodes_match(
        lambda node: (
            node_lookup_match(node, PRACTICE_INCREASING_C_INPUT_LOOKUP, True)
            and not node_term_match(node, EXCLUDED_PRACTICE_TERM_IDS)
        ),
        land_use_management_nodes,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    has_cover_crop = cumulative_nodes_match(
        lambda node: any(
            get_node_property(node, term_id, False).get("value", False) for term_id in get_cover_crop_property_terms()
        ),
        land_cover_nodes,
        cumulative_threshold=MIN_AREA_THRESHOLD,
        default_node_value=DEFAULT_NODE_VALUE
    )

    has_organic_fertiliser_or_soil_amendment_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, ORGANIC_FERTILISER_USED_TERM_ID)
    )

    has_animal_manure_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, ANIMAL_MANURE_USED_TERM_ID)
    )

    num_grassland_improvements = [
        has_irrigation,
        has_practice_increasing_c_input,
        has_n_fixing_crop_or_inorganic_n_fertiliser_used,
        has_organic_fertiliser_or_soil_amendment_used
    ].count(True)

    return CarbonInputArgs(
        num_grassland_improvements=num_grassland_improvements,
        has_irrigation=has_irrigation,
        has_residue_removed_or_burnt=has_residue_removed_or_burnt,
        has_low_residue_producing_crops=has_low_residue_producing_crops,
        has_bare_fallow=has_bare_fallow,
        has_n_fixing_crop_or_inorganic_n_fertiliser_used=has_n_fixing_crop_or_inorganic_n_fertiliser_used,
        has_practice_increasing_c_input=has_practice_increasing_c_input,
        has_cover_crop=has_cover_crop,
        has_organic_fertiliser_or_soil_amendment_used=has_organic_fertiliser_or_soil_amendment_used,
        has_animal_manure_used=has_animal_manure_used
    )


GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: _check_grassland_ipcc_carbon_input_category,
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: _check_grassland_ipcc_carbon_input_category
}
"""
A decision tree for assigning IPCC Carbon Input Categories to Grassland based on the number of improvements.

Key: IpccCarbonInputCategory
Value: Corresponding function to check if the given conditions are met for the category.
"""

CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE = {
    IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE: _check_cropland_high_with_manure_category,
    IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE: _check_cropland_high_without_manure_category,
    IpccCarbonInputCategory.CROPLAND_MEDIUM: _check_cropland_medium_category,
    IpccCarbonInputCategory.CROPLAND_LOW: _check_cropland_low_category
}
"""
A decision tree for assigning IPCC Carbon Input Categories to Cropland based on specific conditions.

Key: IpccCarbonInputCategory
Value: Corresponding function to check if the given conditions are met for the category.
"""

DECISION_TREE_FROM_IPCC_MANAGEMENT_CATEGORY = {
    IpccManagementCategory.IMPROVED_GRASSLAND: GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.FULL_TILLAGE: CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.REDUCED_TILLAGE: CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.NO_TILLAGE: CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE
}
"""
A decision tree mapping IPCC Management Categories to respective Carbon Input Category decision trees.

Key: IpccManagementCategory
Value: Decision tree for Carbon Input Categories corresponding to the management category.
"""

DEFAULT_CARBON_INPUT_CATEGORY = {
    IpccManagementCategory.IMPROVED_GRASSLAND: IpccCarbonInputCategory.GRASSLAND_MEDIUM,
    IpccManagementCategory.FULL_TILLAGE: IpccCarbonInputCategory.CROPLAND_LOW,
    IpccManagementCategory.REDUCED_TILLAGE: IpccCarbonInputCategory.CROPLAND_LOW,
    IpccManagementCategory.NO_TILLAGE: IpccCarbonInputCategory.CROPLAND_LOW
}
"""
A mapping from IPCC Management Categories to default Carbon Input Categories.

Key: IpccManagementCategory
Value: Default Carbon Input Category for the corresponding Management Category.
"""


def _assign_ipcc_carbon_input_category(
    management_nodes: list[dict],
    ipcc_management_category: IpccManagementCategory
) -> IpccCarbonInputCategory:
    """
    Assigns an IPCC Carbon Input Category based on the provided management nodes and IPCC Management Category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes containing information about land management practices.
    ipcc_management_category : IpccManagementCategory
        IPCC Management Category for which the Carbon Input Category needs to be assigned.

    Returns
    -------
    IpccCarbonInputCategory
        Assigned IPCC Carbon Input Category.
    """
    decision_tree = DECISION_TREE_FROM_IPCC_MANAGEMENT_CATEGORY.get(ipcc_management_category, {})
    default = DEFAULT_CARBON_INPUT_CATEGORY.get(ipcc_management_category, IpccCarbonInputCategory.OTHER)

    carbon_input_args = _make_carbon_input_args(management_nodes)

    should_run = len(management_nodes) > 0

    return next(
        (key for key in decision_tree if decision_tree[key](
            carbon_input_args,
            key=key,
        )),
        default
    ) if should_run else default


# --- TIER 1 SOC MODEL ---


def _should_run_inventory_year(inner_dict: dict) -> bool:
    """
    Check if the given inventory year meets the required conditions for further processing.

    Check if the land use category is not "OTHER" and all required keys are present.

    Parameters
    ----------
    inner_dict : dict
        Dictionary containing information for a specific inventory year.

    Returns
    -------
    bool
        True if the inventory year should be considered, False otherwise.
    """
    REQUIRED_KEYS = {IpccLandUseCategory, IpccManagementCategory, IpccCarbonInputCategory}
    return (
        inner_dict[IpccLandUseCategory] != IpccLandUseCategory.OTHER
        and all(key in REQUIRED_KEYS for key in inner_dict)
    )


def _should_run_tier_1(site: dict) -> tuple:
    """
    Determines whether Tier 1 of the IPCC SOC model should run for a given site.

    Parameters
    ----------
    site : dict
        A Hestia `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    tuple
        A tuple containing information to determine if Tier 1 should run, including timestamps,
        IPCC land use categories, management categories, carbon input categories, eco-climate zone,
        SOC reference, and initial SOC stock.
    """

    site_type = site.get("siteType", "")
    management_nodes = site.get("management", [])
    measurement_nodes = site.get("measurements", [])

    eco_climate_zone = _get_eco_climate_zone(measurement_nodes)
    ipcc_soil_category = _assign_ipcc_soil_category(measurement_nodes)
    soc_ref = _retrieve_soc_ref(eco_climate_zone, ipcc_soil_category)

    grouped_management = group_nodes_by_year(management_nodes)

    grouped_land_use_categories = {
        year: {
            IpccLandUseCategory: _assign_ipcc_land_use_category(
                site_type,
                nodes,
                ipcc_soil_category
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_management_categories = {
        year: {
            IpccManagementCategory: _assign_ipcc_management_category(
                nodes,
                grouped_land_use_categories[year][IpccLandUseCategory]
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_carbon_input_categories = {
        year: {
            IpccCarbonInputCategory: _assign_ipcc_carbon_input_category(
                nodes,
                grouped_management_categories[year][IpccManagementCategory]
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_data = reduce(merge, [
        grouped_land_use_categories,
        grouped_management_categories,
        grouped_carbon_input_categories
    ])

    complete_data = {
        year: inner_dict for year, inner_dict in grouped_data.items()
        if _should_run_inventory_year(inner_dict)
    }

    timestamps = list(complete_data)
    start_year = timestamps[0] if timestamps else None
    end_year = timestamps[-1] if timestamps else None

    soc_measurement_value, soc_measurement_date = most_relevant_measurement_value_by_depth_and_date(
        measurement_nodes,
        TERM_ID,
        f"{end_year}-12-31",  # Last year in inventory
        DEPTH_UPPER,
        DEPTH_LOWER,
        depth_strict=True
    ) if end_year else (None, None)

    soc_measurement_datetime = safe_parse_date(soc_measurement_date)
    soc_measurement_year = (
        soc_measurement_datetime.year if soc_measurement_datetime else None
    )

    ipcc_land_use_categories = [complete_data[year][IpccLandUseCategory] for year in timestamps]
    ipcc_management_categories = [complete_data[year][IpccManagementCategory] for year in timestamps]
    ipcc_carbon_input_categories = [complete_data[year][IpccCarbonInputCategory] for year in timestamps]

    should_run = all([
        soc_ref > 0,
        isinstance(eco_climate_zone, int) and eco_climate_zone > 0,
        len(timestamps) > 0,
        (
            start_year <= soc_measurement_year < end_year
        ) if soc_measurement_value and soc_measurement_year else True
    ])

    logShouldRun(
        site, MODEL, TERM_ID, should_run,
        timestamps=log_as_table(set(timestamps)),
        ipcc_land_use_categories=log_as_table(set(ipcc_land_use_categories)),
        ipcc_management_categories=log_as_table(set(ipcc_management_categories)),
        ipcc_carbon_input_categories=log_as_table(set(ipcc_carbon_input_categories)),
        eco_climate_zone=eco_climate_zone,
        soc_ref=soc_ref,
        run_with_soc_measurement=(soc_measurement_value and soc_measurement_year),
        soc_measurement_value=soc_measurement_value,
        soc_measurement_year=soc_measurement_year
    )

    return (
        should_run,
        timestamps,
        ipcc_land_use_categories,
        ipcc_management_categories,
        ipcc_carbon_input_categories,
        eco_climate_zone,
        soc_ref,
        soc_measurement_value,
        soc_measurement_year
    )


def _run_tier_1(
    timestamps: list[int],
    ipcc_land_use_categories: list[IpccLandUseCategory],
    ipcc_management_categories: list[IpccManagementCategory],
    ipcc_carbon_input_categories: list[IpccCarbonInputCategory],
    eco_climate_zone: int,
    soc_ref: float,
    soc_measurement_value: Optional[float] = None,
    soc_measurement_year: Optional[int] = None
) -> list[dict]:
    """
    Run the IPCC (2019) Tier 1 methodology for calculating SOC stocks (in kg C ha-1) for each year in the inventory
    and wrap each of the calculated values in Hestia measurement nodes.

    See [IPCC (2019) Vol. 4, Ch. 2](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.

    Parameters
    ----------
    timestamps : list[int]
        A list of timestamps for each year in the inventory.
    ipcc_land_use_categories : list[IpccLandUseCategory]
        A list of IPCC land use categories for each year in the inventory.
    ipcc_management_categories : list[IpccManagementCategory]
        A list of IPCC management categories for each year in the inventory.
    ipcc_carbon_input_categories : list[IpccCarbonInputCategory]
        A list of IPCC carbon input categories for each year in the inventory.
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    ipcc_soil_category : IpccSoilCategory
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.
    soc_measurement_value : float | None, optional
        Measured SOC stock, if provided.
    soc_measurement_year : int | None, optional
        The year the SOC measurement took place, if provided.

    Returns
    -------
    tuple
    """

    iterated_timestamps, iterated_soc_equilibriums = _run_soc_equilibriums(
        timestamps,
        ipcc_land_use_categories,
        ipcc_management_categories,
        ipcc_carbon_input_categories,
        eco_climate_zone,
        soc_ref
    )

    soc_stocks = _calc_tier_1_soc_stocks(iterated_timestamps, iterated_soc_equilibriums)

    soc_measurement_index = _find_closest_value_index(iterated_timestamps, soc_measurement_year)

    scaled_soc_stocks = _scale_soc_stocks(
        soc_stocks, soc_measurement_value, soc_measurement_index
    )

    slice_index = soc_measurement_index or 0
    result_timestamps = iterated_timestamps[slice_index:]
    result_soc_stocks = scaled_soc_stocks[slice_index:]

    return [
        _measurement(
            year,
            soc_stock,
            MeasurementMethodClassification.TIER_1_MODEL.value
        ) for year, soc_stock in zip(
            result_timestamps,
            result_soc_stocks
        )
    ]


# --- SHARED TIER 1 & TIER 2 RUN FUNCTION ---


def run(site: dict) -> list[dict]:
    """
    Check which Tier of IPCC SOC model to run, run it and return the formatted output.

    Parameters
    ----------
    site : dict
        A Hestia `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    list[dict]
        A list of Hestia `Measurement` nodes containing the calculated SOC stocks and additional relevant data.
    """
    should_run_tier_2, *tier_2_args = _should_run_tier_2(site)
    should_run_tier_1, *tier_1_args = (
        _should_run_tier_1(site) if not should_run_tier_2
        else (False, None)
    )
    return (
        _run_tier_2(*tier_2_args) if should_run_tier_2
        else _run_tier_1(*tier_1_args) if should_run_tier_1
        else []
    )
