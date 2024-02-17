from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.api import find_node, search

from ..log import debugMissingLookup
from .constant import Units

LIMIT = 1000


def get_lookup_value(lookup_term: dict, column: str, skip_debug: bool = False, **kwargs):
    table_name = f"{lookup_term.get('termType')}.csv" if lookup_term else None
    value = get_table_value(
        download_lookup(table_name), 'termid', lookup_term.get('@id'), column_name(column)
    ) if table_name else None
    debugMissingLookup(
        table_name, 'termid', lookup_term.get('@id'), column, value, **kwargs
    ) if lookup_term and not skip_debug else None
    return value


def get_liquid_fuel_terms():
    """
    Find all "liquid" `fuel` terms from the Glossary:
    - https://hestia.earth/glossary?termType=fuel&query=gasoline
    - https://hestia.earth/glossary?termType=fuel&query=petrol
    - https://hestia.earth/glossary?termType=fuel&query=diesel

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.FUEL.value
                    }
                }
            ],
            "should": [
                {
                    "regexp": {
                        "name": "gasoline*"
                    }
                },
                {
                    "regexp": {
                        "name": "petrol*"
                    }
                },
                {
                    "regexp": {
                        "name": "diesel*"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_wood_fuel_terms():
    """
    Find all "wood" `fuel` terms from the Glossary that have a `Energy content (lower heating value)` property:
    - https://hestia.earth/glossary?termType=fuel&query=wood

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.FUEL.value
                    }
                },
                {
                    "nested": {
                        "path": "defaultProperties",
                        "query": {
                            "match": {
                                "defaultProperties.term.name.keyword": "Energy content (lower heating value)"
                            }
                        }
                    }
                }
            ],
            "should": [
                {
                    "regexp": {
                        "name": "wood*"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_irrigation_terms():
    """
    Find all `water` terms from the Glossary:
    https://hestia.earth/glossary?termType=water

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.WATER.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_urea_terms():
    """
    Find all `inorganicFertiliser` urea terms from the Glossary:
    https://hestia.earth/glossary?termType=inorganicFertiliser&query=urea

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.INORGANICFERTILISER.value,
        'name': 'urea'
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_excreta_N_terms():
    """
    Find all `excreta` terms in `kg N` from the Glossary:
    https://hestia.earth/glossary?termType=excreta

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.EXCRETA.value,
        'units.keyword': Units.KG_N.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_excreta_VS_terms():
    """
    Find all `excreta` terms in `kg Vs` from the Glossary:
    https://hestia.earth/glossary?termType=excreta

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.EXCRETA.value,
        'units.keyword': Units.KG_VS.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_tillage_terms():
    """
    Find all `landUseManagement` terms of "tillage" from the Glossary:
    https://hestia.earth/glossary?termType=tillage&query=tillage

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.TILLAGE.value,
        'name': 'tillage'
    }, limit=LIMIT)
    return [n['@id'] for n in terms if 'depth' not in n['@id'].lower()]


def get_generic_crop():
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.CROP.value,
        'name': 'Generic crop seed'
    }, limit=1)
    return terms[0] if len(terms) > 0 else None


def get_rice_paddy_terms():
    """
    Find all `crop` terms of "rice paddy" from the Glossary:
    https://hestia.earth/glossary?termType=crop&query=rice%20paddy

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType": TermTermType.CROP.value
                    }
                },
                {
                    "regexp": {
                        "name": "rice*"
                    }
                },
                {
                    "regexp": {
                        "name": "flooded*"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return [n['@id'] for n in terms if 'depth' not in n['@id'].lower()]


def get_crop_residue_terms():
    terms = find_node(SchemaType.TERM, {'termType.keyword': TermTermType.CROPRESIDUE.value}, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_digestible_energy_terms():
    """
    Find all "digestible energy" `property` terms from the Glossary:
    https://hestia.earth/glossary?termType=property&query=digestible%20energy

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.PROPERTY.value
                    }
                }
            ],
            "should": [
                {
                    "match_phrase_prefix": {
                        "name": "Digestible energy"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_energy_digestibility_terms():
    """
    Find all "energy digestibility" `property` terms from the Glossary:
    https://hestia.earth/glossary?termType=property&query=energy%digestibility

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.PROPERTY.value
                    }
                }
            ],
            "should": [
                {
                    "match_phrase_prefix": {
                        "name": "Energy digestibility"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_crop_residue_management_terms():
    """
    Find all `cropResidueManagement` terms from the Glossary:
    https://hestia.earth/glossary?termType=cropResidueManagement

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.CROPRESIDUEMANAGEMENT.value
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_all_emission_terms():
    """
    Find all `emission` terms from the Glossary:
    https://hestia.earth/glossary?termType=emission

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.EMISSION.value
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_milkYield_terms():
    """
    Find all "milk yield" `animalManagement` terms from the Glossary:
    https://hestia.earth/glossary?query=milk%20yield&termType=animalManagement

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.ANIMALMANAGEMENT.value
                    }
                }
            ],
            "should": [
                {
                    "match_phrase_prefix": {
                        "name": "Milk yield"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_wool_terms():
    """
    Find all "wool" `animalProduct` terms from the Glossary:
    https://hestia.earth/glossary?query=wool&termType=animalProduct

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.ANIMALPRODUCT.value
                    }
                }
            ],
            "should": [
                {
                    "match_phrase_prefix": {
                        "name": "Wool"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_cover_crop_property_terms():
    """
    Find all property terms related to cover crops from the Glossary:
    - https://www.hestia.earth/glossary?query=cover%20crop&termType=property
    - https://www.hestia.earth/glossary?query=catch%20crop&termType=property
    - https://www.hestia.earth/glossary?query=fallow%20crop&termType=property

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.PROPERTY.value}}
            ],
            "should": [
                {"match_phrase": {"name": "cover crop"}},
                {"match_phrase": {"name": "catch crop"}},
                {"match_phrase": {"name": "fallow crop"}},
                {"match_phrase": {"synonyms": "cover crop"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_crop_residue_incorporated_or_left_on_field_terms():
    """
    Find all `cropResidue` terms for residues incorporated or left on field.
    - https://www.hestia.earth/glossary?query=incorporated&termType=cropResidue
    - https://www.hestia.earth/glossary?query=left%20on%20field&termType=cropResidue
    - https://www.hestia.earth/glossary?query=below%20ground&termType=cropResidue

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type.keyword": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.CROPRESIDUE.value}}
            ],
            "should": [
                {"match": {"name": "incorporated"}},
                {"match_phrase": {"name": "left on field"}},
                {"match_phrase": {"name": "below ground"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_irrigated_terms():
    """
    Find all `waterRegime` management/practice terms with names containing "irrigated" and "deep water"
    from the Glossary:
    - https://hestia.earth/glossary?termType=waterRegime&query=irrigated
    - https://hestia.earth/glossary?termType=waterRegime&query=deep%20water

    n.b., this function differs from `get_irrigation_terms` which returns all `water` input terms.

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.WATERREGIME.value}}
            ],
            "should": [
                {"match_phrase_prefix": {"name": "irrigated"}},
                {"match_phrase_prefix": {"name": "deep water"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_residue_removed_or_burnt_terms():
    """
    Find all `cropResidueManagement` terms where residues are removed or burnt from the Glossary

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.CROPRESIDUEMANAGEMENT.value}}
            ],
            "should": [
                {"match": {"name": "removed"}},
                {"match": {"name": "burnt"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_rice_plant_upland_terms():
    """
    Find all `landCover` terms related to upland rice the Glossary

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.LANDCOVER.value}},
                {"match_phrase": {"name": "rice plant"}},
                {"match": {"name": "upland"}}
            ],
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_pasture_system_terms():
    """
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.SYSTEM.value}},
                {"match": {"name": "pasture"}}
            ],
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))
