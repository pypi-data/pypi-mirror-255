from datetime import datetime
import pytest
from unittest.mock import patch

from hestia_earth.schema import SiteSiteType

from hestia_earth.models.utils.blank_node import (
    _calc_datetime_range_intersection_duration,
    _gapfill_datestr,
    _get_datestr_format,
    _run_required,
    _run_model_required,
    _should_run_array_treatment,
    ArrayTreatment,
    cumulative_nodes_match,
    DatestrFormat,
    DatestrGapfillMode,
    DatetimeRange,
    get_node_value,
    group_nodes_by_year
)


class_path = "hestia_earth.models.utils.blank_node"


def test_run_required():
    term = {
        '@id': 'ch4ToAirAquacultureSystems',
        'termType': 'emission'
    }
    assert not _run_required('model', term, {
        'site': {'siteType': SiteSiteType.CROPLAND.value}
    })
    assert _run_required('model', term, {
        'site': {'siteType': SiteSiteType.POND.value}
    }) is True

    term = {
        '@id': 'landTransformationFromCropland20YearAverageDuringCycle',
        'termType': 'resourceUse'
    }
    assert not _run_required('hyde32', term, {
        'site': {'siteType': SiteSiteType.CROPLAND.value}
    })


def test_run_model_required():
    term = {
        '@id': 'netPrimaryProduction',
        'termType': 'measurement'
    }
    assert _run_model_required('pooreNemecek2018', term, {
        'site': {'siteType': SiteSiteType.POND.value}
    }) is True
    assert not _run_model_required('pooreNemecek2018', term, {
        'site': {'siteType': SiteSiteType.CROPLAND.value}
    })


# --- test should_run_array_treatment ---


def test_should_run_array_treatment_true():
    VALUE = [24, 87, 34, 12]
    assert _should_run_array_treatment(VALUE) is True


def test_should_run_array_treatment_false_empty_list():
    VALUE = []
    assert _should_run_array_treatment(VALUE) is False


def test_should_run_array_treatment_false_not_iterable():
    VALUE = 1
    assert _should_run_array_treatment(VALUE) is False


# --- test get_node_value ---


FULL_TILLAGE_AS_PRACTICE = {
    "@type": "Practice",
    "term": {
        "@type": "Term",
        "@id": "fullTillage"
    },
    "value": [50, 50, 60, 70]
}

FULL_TILLAGE_AS_MANAGEMENT = {
    "@type": "Management",
    "term": {
        "@type": "Term",
        "@id": "fullTillage"
    },
    "value": 100
}

EXPECTED_EMPTY_LIST = 0


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_reduce_default(*args):
    """
    Should return the reduced value of the value list using the array treatment specified in the term lookup
    (or ArrayTreatment.FIRST if no lookup value available).

    The lookup array treatment for `fullTillage` is `first`, therefore a return value of `50` is expected.
    """
    EXPECTED = 50
    result = get_node_value(FULL_TILLAGE_AS_PRACTICE)
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_reduce_mean(*args):
    """
    Should return the mean value of the value list.

    `statistics.mean` function is used here.
    """
    EXPECTED = 57.5
    result = get_node_value(
        FULL_TILLAGE_AS_PRACTICE, array_treatment=ArrayTreatment.MEAN
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_reduce_mode(*args):
    """
    Should return the mode value of the value list.

    `statistics.mode` function is used here.
    """
    EXPECTED = 50
    result = get_node_value(
        FULL_TILLAGE_AS_PRACTICE, array_treatment=ArrayTreatment.MODE
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_reduce_sum(*args):
    """
    Should return the sum value of the value list.
    """
    EXPECTED = 230
    result = get_node_value(
        FULL_TILLAGE_AS_PRACTICE, array_treatment=ArrayTreatment.SUM
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_reduce_first(*args):
    """
    Should return the first value of the value list.
    """
    EXPECTED = 50
    result = get_node_value(
        FULL_TILLAGE_AS_PRACTICE, array_treatment=ArrayTreatment.FIRST
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_reduce_last(*args):
    """
    Should return the last value of the value list.
    """
    EXPECTED = 70
    result = get_node_value(
        FULL_TILLAGE_AS_PRACTICE, array_treatment=ArrayTreatment.LAST
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_bools_reduce_mean(*args):
    """
    If value is list of bools, the `satistics.mean` interprets them as integers (0 or 1),
    therefore number is returned.
    """
    EXPECTED = 1/3
    NODE = {"value": [False, False, True]}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.MEAN
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_bools_reduce_mode(*args):
    """
    If value is list of bools, the `satistics.mode` interprets them as bools and returns the most
    common bool value as expected.
    """
    EXPECTED = False
    NODE = {"value": [False, False, True]}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.MODE
    )
    assert result == EXPECTED
    assert isinstance(result, bool)


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_list_bools_reduce_sum(*args):
    """
    If value is list of bools, the built-in `sum` interprets them as integers (0 or 1),
    therefore number is returned.
    """
    EXPECTED = 1
    NODE = {"value": [False, False, True]}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.SUM
    )
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_empty_list_reduce_default(*args):
    """
    Empty list return as 0 if keyword arg `reduce_value_list` = `True`.
    """
    NODE = {"value": []}
    result = get_node_value(NODE)
    assert result == EXPECTED_EMPTY_LIST


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_empty_list_reduce_mean(*args):
    """
    Empty list return as 0 if keyword arg `reduce_value_list` = `True`.
    """
    NODE = {"value": []}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.MEAN
    )
    assert result == EXPECTED_EMPTY_LIST


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_empty_list_reduce_mode(*args):
    """
    Empty list return as 0 if keyword arg `reduce_value_list` = `True`.
    """
    NODE = {"value": []}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.MODE
    )
    assert result == EXPECTED_EMPTY_LIST


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_empty_list_reduce_sum(*args):
    """
    Empty list return as 0 if keyword arg `reduce_value_list` = `True`.
    """
    NODE = {"value": []}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.SUM
    )
    assert result == EXPECTED_EMPTY_LIST


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_empty_list_reduce_first(*args):
    """
    Empty list return as 0 if keyword arg `reduce_value_list` = `True`.
    """
    NODE = {"value": []}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.FIRST
    )
    assert result == EXPECTED_EMPTY_LIST


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_empty_list_reduce_last(*args):
    """
    Empty list return as 0 if keyword arg `reduce_value_list` = `True`.
    """
    NODE = {"value": []}
    result = get_node_value(
        NODE, array_treatment=ArrayTreatment.LAST
    )
    assert result == EXPECTED_EMPTY_LIST


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_float(*args):
    """
    Non-list values are returned directly, even if if keyword arg `reduce_value_list` = `True`.
    """
    EXPECTED = 100
    result = get_node_value(FULL_TILLAGE_AS_MANAGEMENT)
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_bool_true(*args):
    """
    Non-list values are returned directly, even if if keyword arg `reduce_value_list` = `True`.
    """
    EXPECTED = True
    NODE = {"value": True}
    result = get_node_value(NODE)
    assert result == EXPECTED


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_bool_false(*args):
    """
    Non-list values are returned directly, even if if keyword arg `reduce_value_list` = `True`.
    """
    EXPECTED = False
    NODE = {"value": False}
    result = get_node_value(NODE)
    assert result == EXPECTED
    assert isinstance(result, bool)


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.FIRST)
def test_get_node_value_no_value(*args):
    """
    Missing values are returned as 0.
    """
    EXPECTED = 0
    NODE = {}
    result = get_node_value(NODE)
    assert result == EXPECTED


# --- test cumulative_nodes_match ---


CROP_RESIDUE_NODES = [
    {
        "@type": "Product",
        "term": {
            "@type": "Term",
            "@id": "aboveGroundCropResidueBurnt"
        },
        "value": [20, 25, 30]
    },
    {
        "@type": "Product",
        "term": {
            "@type": "Term",
            "@id": "aboveGroundCropResidueRemoved"
        },
        "value": [10, 15, 20]
    },
    {
        "@type": "Product",
        "term": {
            "@type": "Term",
            "@id": "aboveGroundCropResidueLeftOnField"
        },
        "value": [50]
    },
]


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.MEAN)
def test_cumulative_nodes_match_true(*args):
    result = cumulative_nodes_match(
        lambda node: node.get("term", {}).get("@id") in [
            "aboveGroundCropResidueBurnt", "aboveGroundCropResidueRemoved"
        ],
        CROP_RESIDUE_NODES,
        cumulative_threshold=35
    )
    assert result is True


@patch(f"{class_path}._retrieve_array_treatment", return_value=ArrayTreatment.MEAN)
def test_cumulative_nodes_match_false(*args):
    result = cumulative_nodes_match(
        lambda node: node.get("term", {}).get("@id") in ["aboveGroundCropResidueLeftOnField"],
        CROP_RESIDUE_NODES,
        cumulative_threshold=100
    )
    assert result is False


def test_cumulative_nodes_match_additional_args():
    with pytest.raises(TypeError):
        cumulative_nodes_match(
            lambda node: node.get("term", {}).get("@id") in ["aboveGroundCropResidueBurnt"],
            CROP_RESIDUE_NODES,
            {"random": True},
            cumulative_threshold=10
        )


# --- test _get_datestr_format ---

DATESTR_YEAR = "2000"
DATESTR_YEAR_MONTH = "2000-01"
DATESTR_YEAR_MONTH_DAY = "2000-01-01"
DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = "2000-01-01T00:00:00"
DATESTR_MONTH = "--01"
DATESTR_MONTH_DAY = "--01-01"


def test_get_date_year():
    """
    Test datestr format `YYYY`.
    """
    assert _get_datestr_format(DATESTR_YEAR) == DatestrFormat.YEAR


def test_get_date_year_month():
    """
    Test datestr format `YYYY-MM`.
    """
    assert _get_datestr_format(DATESTR_YEAR_MONTH) == DatestrFormat.YEAR_MONTH


def test_get_date_year_month_day():
    """
    Test datestr format `YYYY-MM-DD`.
    """
    assert _get_datestr_format(DATESTR_YEAR_MONTH_DAY) == DatestrFormat.YEAR_MONTH_DAY


def test_get_date_year_month_day_hour_minute_second():
    """
    Test datestr format `YYYY-MM-DDTHH:mm:ss`.
    """
    assert (
        _get_datestr_format(DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND) ==
        DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
    )


def test_get_date_month():
    """
    Test datestr format `--MM`.

    Should only be found in blank node `dates` field. (Format not permitted in `startDate` or `endDate` fields.)
    """
    assert _get_datestr_format(DATESTR_MONTH), DatestrFormat.MONTH


def test_get_date_month_day():
    """
    Test datestr format `--MM-DD`.

    Should only be found in blank node `dates` field. (Format not permitted in `startDate` or `endDate` fields.)
    """
    assert _get_datestr_format(DATESTR_MONTH_DAY), DatestrFormat.MONTH_DAY


# --- test _gapfill_datestr ---


def test_complete_datestr_year():
    assert _gapfill_datestr(DATESTR_YEAR), "2000-01-01T00:00:00"
    assert _gapfill_datestr(DATESTR_YEAR, DatestrGapfillMode.END), "2000-12-31T23:59:59"


def test_complete_datestr_year_month():
    assert _gapfill_datestr(DATESTR_YEAR_MONTH), "2000-01-01T00:00:00"
    assert _gapfill_datestr(DATESTR_YEAR_MONTH, DatestrGapfillMode.END) == "2000-01-31T23:59:59"


def test_complete_datestr_year_month_day():
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY), "2000-01-01T00:00:00"
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY, DatestrGapfillMode.END) == "2000-01-01T23:59:59"


def test_gapfill_datestr_feburary():
    """
    Gapfilling February datestrings should take into account leap years
    """
    # Non-leap year
    assert _gapfill_datestr("1981-02") == "1981-02-01T00:00:00"
    assert _gapfill_datestr("1981-02", DatestrGapfillMode.END) == "1981-02-28T23:59:59"

    # Leap year
    assert _gapfill_datestr("2024-02", DatestrGapfillMode.END) == "2024-02-29T23:59:59"


def test_complete_datestr_should_not_run():
    """
    Completion should not run, therefore the function should return the datestr without
    modification.
    """
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND) == DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
    assert _gapfill_datestr(DATESTR_MONTH) == DATESTR_MONTH
    assert _gapfill_datestr(DATESTR_MONTH_DAY) == DATESTR_MONTH_DAY
    assert _gapfill_datestr("") == ""


# --- test _calc_datetime_range_intersection_duration ---


def test_calc_datetime_range_intersection_duration():
    r1 = DatetimeRange(
        start=datetime(2000, 1, 1),
        end=datetime(2002, 1, 1)
    )
    r2 = DatetimeRange(
        start=datetime(2001, 1, 1),
        end=datetime(2003, 1, 1)
    )

    result = _calc_datetime_range_intersection_duration(r1, r2)
    assert result == 31536000


def test_calc_datetime_range_intersection_duration_no_intersection():
    r1 = DatetimeRange(
        start=datetime(2000, 1, 1),
        end=datetime(2000, 12, 31)
    )
    r2 = DatetimeRange(
        start=datetime(2001, 1, 1),
        end=datetime(2001, 12, 31)
    )

    result = _calc_datetime_range_intersection_duration(r1, r2)
    assert result == 0


# --- test group_nodes_by_year ---


def test_group_nodes_by_year_empty_list():
    CYCLES = []
    EXPECTED = {}
    result = group_nodes_by_year(CYCLES)
    assert result == EXPECTED


GROUP_NODES_BY_YEAR_SCENARIO_A_CYCLES = [
    {"@id": "cycle-1a", "endDate": "2002"},
    {"@id": "cycle-2a", "endDate": "2003"},
    {"@id": "cycle-3a", "endDate": "2006", "startDate": "2004"}
]


def test_group_nodes_scenario_a():
    """
    Datestr in format `YYYY`. Some nodes missing `startDate` field. One multi-year cycle.

    Incomplete datestrs are gapfilled by default; with `endDate` datestrs snapping to the end
    of the calendar year, and `startDate` datestrs snapping to the beginning of the calendar
    year.
    """

    EXPECTED = {
        2002: [{
            "@id": "cycle-1a",
            "endDate": "2002",
            "fraction_of_year": 1.0,
            "fraction_of_node_duration": 1.0
        }],
        2003: [{
            "@id": "cycle-2a",
            "endDate": "2003",
            "fraction_of_year": 1.0,
            "fraction_of_node_duration": 1.0
        }],
        2004: [{
            "@id": "cycle-3a",
            "endDate": "2006",
            "startDate": "2004",
            "fraction_of_year": 1.0,
            "fraction_of_node_duration": 0.33394160583941607
        }],
        2005: [{
            "@id": "cycle-3a",
            "endDate": "2006",
            "startDate": "2004",
            "fraction_of_year": 1.0,
            "fraction_of_node_duration": 0.333029197080292
        }],
        2006: [{
            "@id": "cycle-3a",
            "endDate": "2006",
            "startDate": "2004",
            "fraction_of_year": 1.0,
            "fraction_of_node_duration": 0.333029197080292
        }]
    }

    result = group_nodes_by_year(GROUP_NODES_BY_YEAR_SCENARIO_A_CYCLES)
    assert result == EXPECTED


def test_group_nodes_scenario_b():
    """
    Datestr in format `YYYY-MM-DD`. Two concurrent cycles (`cycle-3b` & `cycle-4b`).
    """

    CYCLES = [
        {"@id": "cycle-1b", "endDate": "2000-12-31", "startDate": "2000-01-01"},
        {"@id": "cycle-2b", "endDate": "2001-12-31", "startDate": "2001-01-01"},
        {"@id": "cycle-3b", "endDate": "2002-12-31", "startDate": "2002-01-01"},
        {"@id": "cycle-4b", "endDate": "2002-12-31", "startDate": "2002-01-01"}
    ]

    EXPECTED = {
        2000: [
            {
                "@id": "cycle-1b",
                "endDate": "2000-12-31",
                "startDate": "2000-01-01",
                "fraction_of_year": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ],
        2001: [
            {
                "@id": "cycle-2b",
                "endDate": "2001-12-31",
                "startDate": "2001-01-01",
                "fraction_of_year": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ],
        2002: [
            {
                "@id": "cycle-3b",
                "endDate": "2002-12-31",
                "startDate": "2002-01-01",
                "fraction_of_year": 1.0,
                "fraction_of_node_duration": 1.0
            },
            {
                "@id": "cycle-4b",
                "endDate": "2002-12-31",
                "startDate": "2002-01-01",
                "fraction_of_year": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ]
    }

    result = group_nodes_by_year(CYCLES)
    assert result == EXPECTED


def test_group_nodes_scenario_c():
    """
    Multiple overlapping 6 month and 12 month cycles.
    """

    CYCLES = [
        {"@id": "cycle-1c", "endDate": "2000-06", "startDate": "2000-01"},
        {"@id": "cycle-2c", "endDate": "2001-12", "startDate": "2000-07"},
        {"@id": "cycle-3c", "endDate": "2001-06", "startDate": "2001-01"},
        {"@id": "cycle-4c", "endDate": "2002-06", "startDate": "2001-07"},
        {"@id": "cycle-5c", "endDate": "2002-12", "startDate": "2002-01"}
    ]

    EXPECTED = {
        2000: [
            {
                "@id": "cycle-1c",
                "endDate": "2000-06",
                "startDate": "2000-01",
                "fraction_of_year": 0.4972677595628415,
                "fraction_of_node_duration": 1.0
            },
            {
                "@id": "cycle-2c",
                "endDate": "2001-12",
                "startDate": "2000-07",
                "fraction_of_year": 0.5027322404371585,
                "fraction_of_node_duration": 0.33515482695810567
            }
        ],
        2001: [
            {
                "@id": "cycle-2c",
                "endDate": "2001-12",
                "startDate": "2000-07",
                "fraction_of_year": 1.0,
                "fraction_of_node_duration": 0.6648451730418944
            },
            {
                "@id": "cycle-3c",
                "endDate": "2001-06",
                "startDate": "2001-01",
                "fraction_of_year": 0.4958904109589041,
                "fraction_of_node_duration": 1.0
            },
            {
                "@id": "cycle-4c",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "fraction_of_year": 0.5041095890410959,
                "fraction_of_node_duration": 0.5041095890410959
            }
        ],
        2002: [
            {
                "@id": "cycle-4c",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "fraction_of_year": 0.4958904109589041,
                "fraction_of_node_duration": 0.4958904109589041
            },
            {
                "@id": "cycle-5c",
                "endDate": "2002-12",
                "startDate": "2002-01",
                "fraction_of_year": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ]
    }

    result = group_nodes_by_year(CYCLES)
    assert result == EXPECTED


def test_group_nodes_scenario_d():
    """
    Cases where nodes only overlap with year groups by a small amount.
    Overlaps of less than 30% of a year should be not be included in a
    year group, unless that majority (<50%) of their duration takes place
    within that year.
    """

    MANAGEMENT = [
        {
            "term.@id": "fullTillage",
            "endDate": "2000-11",
            "value": 100
        },
        {
            "term.@id": "fullTillage",
            "endDate": "2001-07",
            "startDate": "2000-12",
            "value": 50
        },
        {
            "term.@id": "noTillage",
            "endDate": "2001-07",
            "startDate": "2000-12",
            "value": 50
        },
        {
            "term.@id": "noTillage",
            "endDate": "2002-01",
            "startDate": "2001-08",
            "value": 100
        },
        {
            "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed",
            "endDate": "2000-11",
            "startDate": "2000-09",
            "value": True
        },
        {
            "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed",
            "endDate": "2002-06",
            "startDate": "2001-07",
            "value": True
        }
    ]

    EXPECTED = {
        2000: [
            {
                "term.@id": "fullTillage",
                "endDate": "2000-11",
                "value": 100,
                "fraction_of_year": 0.9153005464480874,
                "fraction_of_node_duration": 0.9153005464480874
            },
            {
                "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed",
                "endDate": "2000-11",
                "startDate": "2000-09",
                "value": True,
                "fraction_of_year": 0.24863387978142076,
                "fraction_of_node_duration": 1.0
            }
        ],
        2001: [
            {
                "term.@id": "fullTillage",
                "endDate": "2001-07",
                "startDate": "2000-12",
                "value": 50,
                "fraction_of_year": 0.5808219178082191,
                "fraction_of_node_duration": 0.8724279835390947
            },
            {
                "term.@id": "noTillage",
                "endDate": "2001-07",
                "startDate": "2000-12",
                "value": 50,
                "fraction_of_year": 0.5808219178082191,
                "fraction_of_node_duration": 0.8724279835390947
            },
            {
                "term.@id": "noTillage",
                "endDate": "2002-01",
                "startDate": "2001-08",
                "value": 100,
                "fraction_of_year": 0.4191780821917808,
                "fraction_of_node_duration": 0.8315217391304348
            },
            {
                "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "value": True,
                "fraction_of_year": 0.5041095890410959,
                "fraction_of_node_duration": 0.5041095890410959
            }
        ],
        2002: [
            {
                "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "value": True,
                "fraction_of_year": 0.4958904109589041,
                "fraction_of_node_duration": 0.4958904109589041
            }
        ]
    }

    result = group_nodes_by_year(MANAGEMENT)
    assert result == EXPECTED


def test_group_nodes_scenario_e():
    """
    Edge case where nodes with short durations are equally split between two
    year groups. In this case, they should be categorised as the later of the
    two potential groups.
    """

    MANAGEMENT = [
        {
            "term.@id": "fullTillage",
            "endDate": "2001-01",
            "startDate": "2000-12",
            "value": 100
        }
    ]

    EXPECTED = {
        2001: [
            {
                "term.@id": "fullTillage",
                "endDate": "2001-01",
                "startDate": "2000-12",
                "value": 100,
                "fraction_of_year": 0.08493150684931507,
                "fraction_of_node_duration": 0.50
            }
        ]
    }

    result = group_nodes_by_year(
        MANAGEMENT,
        # gapfill_incomplete_datestrs=False
    )
    assert result == EXPECTED
