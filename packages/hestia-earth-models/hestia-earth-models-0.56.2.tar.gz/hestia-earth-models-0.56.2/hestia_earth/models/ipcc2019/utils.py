from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils.input import get_total_irrigation_m3
from hestia_earth.models.utils.cycle import get_ecoClimateZone
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.blank_node import find_terms_value
from hestia_earth.models.utils.term import get_lookup_value, get_milkYield_terms
from . import MODEL

# From IPCC2019 Indirect N2O emission factor, in N [avg, min, max, std]
COEFF_NO3_N2O = [0.011, 0.00, 0.02, 0.005]
# Volatilized Nitrogen as NH3-N and NOx-N per kg N applied organic fertilisers and animal dung and urine
COEFF_N_NH3NOX_organic_animal = [0.21, 0.00, 0.31, 0.0775]
# Volatilized Nitrogen as NH3-N and NOx-N per kg N applied inorganic fertilisers
COEFF_N_NH3NOX_inorganic = [0.11, 0.02, 0.33, 0.0775]


def get_nh3_no3_nox_to_n(cycle: dict, nh3_term_id: str, no3_term_id: str, nox_term_id: str):
    nh3 = find_terms_value(cycle.get('emissions', []), nh3_term_id)
    nh3 = nh3 / get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    no3 = find_terms_value(cycle.get('emissions', []), no3_term_id)
    no3 = no3 / get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    nox = find_terms_value(cycle.get('emissions', []), nox_term_id)
    nox = nox / get_atomic_conversion(Units.KG_NOX, Units.TO_N)
    return nh3, no3, nox


def get_FracLEACH_H(cycle: dict, term_id: str):
    eco_climate_zone = get_ecoClimateZone(cycle)
    is_eco_climate_zone_dry = eco_climate_zone % 2 == 0
    irrigation_value_m3 = get_total_irrigation_m3(cycle)
    is_drip_irrigated = find_term_match(cycle.get('practices', []), 'irrigatedDripIrrigation', None) is not None

    debugValues(cycle, model=MODEL, term=term_id,
                is_eco_climate_zone_dry=is_eco_climate_zone_dry,
                irrigation_value_m3=irrigation_value_m3,
                is_drip_irrigated=is_drip_irrigated)

    return (0, 0, 0, 0) if all([
        is_eco_climate_zone_dry,
        any([irrigation_value_m3 <= 250, is_drip_irrigated])
    ]) else (0.24, 0.01, 0.73, 0.18)  # value, min, max, sd


# Indirect N2O emissions from volatilized NH3 and NOx
def get_FracNH3NOx_N2O(cycle: dict, term_id: str):
    eco_climate_zone = get_ecoClimateZone(cycle)
    is_eco_climate_zone_dry = eco_climate_zone % 2 == 0
    irrigation_value_m3 = get_total_irrigation_m3(cycle)
    is_drip_irrigated = find_term_match(cycle.get('practices', []), 'irrigatedDripIrrigation', None) is not None

    debugValues(cycle, model=MODEL, term=term_id,
                is_eco_climate_zone_dry=is_eco_climate_zone_dry,
                irrigation_value_m3=irrigation_value_m3,
                is_drip_irrigated=is_drip_irrigated)

    return (0.005, 0, 0.011, 0.00275) if all([
        is_eco_climate_zone_dry,
        any([irrigation_value_m3 <= 250, is_drip_irrigated])
    ]) else (0.014, 0.011, 0.017, 0.0015)  # value, min, max, sd


def get_yield_dm(term_id: str, term: dict):
    return safe_parse_float(get_lookup_value(term, 'IPCC_2019_Ratio_AGRes_YieldDM', model=MODEL, term=term_id), None)


def get_milkYield_practice(node: dict):
    terms = get_milkYield_terms()
    return next((p for p in node.get('practices', []) if p.get('term', {}).get('@id') in terms), {})
