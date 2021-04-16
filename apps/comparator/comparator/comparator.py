#  This file is part of CEOsys Recommendation Checker.
#
#  Copyright (c) 2021 CEOsys project team <https://covid-evidenz.de>.
#
#  CEOsys Recommendation Checker is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  CEOsys Recommendation Checker is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with CEOsys Recommendation Checker.  If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import pint
from jsonpath_ng.ext import parse
from . import ureg, mapping_table
from .quantity import Quantity, Medication


def findall_resources(bundle: Dict, resource_type: str, identifier: str = None) -> Dict:
    """
    Find all resources of a given type in bundle

    Args:
        bundle: JSON structure (dict) of the bundle
        resource_type: resource type to search for
        identifier: value of the identifier of the resource (to locate specific resources)

    Returns: One resource of given type at a time

    """
    for entry in bundle["entry"]:
        if entry["resource"]["resourceType"] == resource_type:
            if (
                identifier is None
                or entry["resource"]["identifier"][0]["value"] == identifier
            ):
                yield entry["resource"]


def find_resource(bundle, resource_name, identifier=None):
    try:
        res = next(findall_resources(bundle, resource_name, identifier))
    except StopIteration:
        if identifier is not None:
            msg = f'No resource "{resource_name}" with identifier "{identifier}" found'
        else:
            msg = f'No resource "{resource_name}" found'
        raise KeyError(msg) from None
    return res


def get_mapping(coding: Dict) -> Dict:
    """
    Get mapping from guideline coding to specific variables from mapping table

    Args:
        coding: Coding from guideline

    Returns: Mapping information from mapping table

    """
    system = coding["system"].rstrip("/").strip()  # noqa
    code = coding["code"].strip()  # noqa
    res = mapping_table.query("(code==@code) & (system==@system)")
    if len(res) == 0:
        raise ValueError(f"Could not find mapping for code {coding}")
    return res.to_dict(orient="records")


def get_mappings(codeableConcept: Dict) -> List[Dict]:
    """
    Get mappings from guideline codeableConcept to specific variables from mapping table

    Args:
        codeableConcept: CodeableConcept from guideline

    Returns: List of mapping information

    """
    mappings = []

    for code in codeableConcept["coding"]:
        mappings += get_mapping(code)

    return mappings


def nonify(v: float) -> Optional[float]:
    """
    Converts nan values to None

    Args:
        v: float

    Returns: None if input value is NaN, else input value

    """
    if pd.isna(v):
        return None
    return v


def get_unique_mapping(codeableConcept: Dict) -> Dict:
    """
    Retrieve unique mapping for codeable concept.

    If multiple codings are specified for a codeableConcept, this function makes
    sure that all codings map to the same item.

    Args:
        codeableConcept: codeableConcept from guideline

    Returns: unique mapping, if available

    """
    mappings = get_mappings(codeableConcept)

    cols = ["variable_name", "type", "value", "value_low", "value_high"]
    n_unique_concepts = (
        pd.DataFrame(mappings).fillna("")[cols].drop_duplicates().shape[0]
    )
    assert (
        n_unique_concepts == 1
    ), f"Expected exactly one unique concept, found {n_unique_concepts}"

    return mappings[0]


def create_quantity_from_mapping(mapping):
    datatypes = {"str": str, "float": float, "int": int, "bool": bool}

    if mapping["type"] not in datatypes:
        raise ValueError(f'Invalid data type {mapping["type"]}')

    datatype = datatypes[mapping["type"]]

    value = nonify(mapping["value"])

    if value is not None:
        value = datatype(value)

    q = Quantity(
        datatype=datatype,
        variable_name=nonify(mapping["variable_name"]),
        value=value,
        value_low=nonify(mapping["value_low"]),
        value_high=nonify(mapping["value_high"]),
        unit=nonify(mapping["unit"]),
    )

    return q


def get_unit(quantity: Dict) -> pint.Quantity:
    if "unit" in quantity:
        if not quantity["system"] == "https://unitsofmeasure.org":
            raise ValueError(
                f'Can only use "https://unitsofmeasure.org" as unit system, '
                f'got {quantity["system"]} instead'
            )
        unit = quantity["code"]
    else:
        unit = None

    return ureg(unit)


def get_quantity(char, variable_name=None):
    if "valueRange" in char:

        has_low = "low" in char["valueRange"]
        has_high = "high" in char["valueRange"]

        unit_low = get_unit(char["valueRange"]["low"]) if has_low else None
        unit_high = get_unit(char["valueRange"]["high"]) if has_high else None

        if has_low and has_high:
            assert (
                unit_low.dimensionality == unit_high.dimensionality
            ), "Got different units for low and high end of range"
            unit = unit_low
        elif has_low:
            unit = unit_low
        else:
            unit = unit_high

        q = Quantity(
            float,
            value_low=char["valueRange"]["low"]["value"] if has_low else None,
            value_high=char["valueRange"]["high"]["value"] if has_high else None,
            unit=unit,
        )
    elif "valueBoolean" in char:
        q = Quantity(bool, value=char["valueBoolean"])
    elif "valueQuantity" in char:
        value = char["valueQuantity"]["value"]
        unit = get_unit(char["valueQuantity"])
        q = Quantity(type(value), value=value, unit=unit)
    elif "valueCodeableConcept" in char:
        mapping = get_unique_mapping(char["valueCodeableConcept"])
        q = create_quantity_from_mapping(mapping)
    else:
        raise ValueError("No value found in characteristic")

    q.variable_name = variable_name

    return q


def find_characteristic(resource, system, code):
    res = parse(
        f'$.characteristic[*].code.coding[?(system=="{system}") & (code=="{code}")]'
    ).find(resource)
    if len(res) > 1:
        raise ValueError(
            f'Multiple characteristics with system "{system}" / code "{code}" found'
        )
    elif len(res) == 1:
        return res[0]
    else:
        return None


def is_drug_group(resource):
    return (
        find_characteristic(
            resource, system="https://data.cochrane.org/ontologies/core/", code="Drug"
        )
        is not None
    )


def parse_characteristics(resource):
    characteristics = parse("$.characteristic[*]").find(resource)
    quantities = []

    if len(characteristics) == 1:
        characteristic = characteristics[0]
        for mapping in get_mappings(characteristic.value["code"]):
            q = get_quantity(
                characteristic.value, variable_name=nonify(mapping["variable_name"])
            )
            # only add quantity to list if not already contained (e.g. if multiple
            # concepts from different vocabularies (SNOMED CT, Cochrane) point to the
            # same mapping
            if q not in quantities:
                quantities.append(q)
    elif is_drug_group(resource):
        q = parse_drug_group(resource)
        quantities.append(q)
    else:
        group_name = resource["identifier"][0]["value"]
        raise ValueError(
            f"Unknown combination of multiple characteristics in group {group_name}"
        )

    return quantities


def parse_drug_group(resource):
    duration = find_characteristic(
        resource, system="https://data.cochrane.org/ontologies/pico/", code="Duration"
    )
    schedule = find_characteristic(
        resource, system="https://data.cochrane.org/ontologies/pico/", code="Schedule"
    )
    dose = find_characteristic(
        resource, system="https://data.cochrane.org/ontologies/pico/", code="Dose"
    )
    drug = find_characteristic(
        resource, system="https://data.cochrane.org/ontologies/core/", code="Drug"
    )

    dose = get_quantity(dose.context.context.context.value)

    if duration is not None:
        duration = get_quantity(duration.context.context.context.value)

    if schedule is not None:
        schedule = get_quantity(schedule.context.context.context.value)

    drug = get_unique_mapping(
        drug.context.context.context.value["valueCodeableConcept"]
    )
    drug["value"] = dose.value
    drug["unit"] = dose.unit
    drug["value_low"] = dose.value_low
    drug["value_high"] = dose.value_high
    drug = create_quantity_from_mapping(drug)

    q = Medication(drug=drug, dose=dose, schedule=schedule, duration=duration)

    return q


def get_population_exposure(content: Dict) -> Dict[str, List[str]]:
    """
    Extract names of the population and exposure groups from the full guideline.

    Args:
        content: Guideline (json)

    Returns: name of population and exposure groups

    """
    evidence = find_resource(content, "Evidence")
    res = []
    for var in evidence["variableDefinition"]:
        res.append(
            (
                var["variableRole"]["coding"][0]["code"],
                var["observed"]["identifier"]["value"],
            )
        )

    return {
        key: [v[1] for v in res if v[0] == key] for key in ["population", "exposure"]
    }


def get_group_names(
    content: Dict, evidence_identifier: str, evidence_type: str
) -> List[str]:
    """
    Get characteristics group names from guideline for population or exposure

    Args:
        content: Guideline
        evidence_identifier: Identifier of the population or exposure resource
        evidence_type: "population" or "exposure"

    Returns: all group names belonging to the evidence identifier resource

    """
    if evidence_type == "population":
        resource_name = "Group"
        attribute = "valueReference"
    elif evidence_type == "exposure":
        resource_name = "EvidenceVariable"
        attribute = "definitionReference"
    else:
        raise ValueError(
            f'Invalid key {evidence_type}. Expected "population" or "exposure"'
        )

    entity = find_resource(content, resource_name, identifier=evidence_identifier)

    group_names = [
        m.value
        for m in parse(
            f'$.characteristic[?@.{attribute}.type=="Group"].{attribute}.identifier.value'
        ).find(entity)
    ]
    return group_names


def get_quantities(
    content: Dict, evidence_identifier: str, evidence_type: str
) -> List[Quantity]:
    """
    Parses guideline into quantities (to test dataset)

    Args:
        content: Guideline
        evidence_identifier: Identifier of the population or exposure resource
        evidence_type: "population" or "exposure"

    Returns: Quantities belonging to the evidence identifier resource

    """

    group_names = get_group_names(content, evidence_identifier, evidence_type)

    quantities = []

    for group_name in group_names:
        resource = find_resource(content, "Group", group_name)
        quantities += parse_characteristics(resource)

    return quantities


def get_population_quantities(
    content: Dict, populations: List[str]
) -> Dict[str, List[Quantity]]:
    """
    Get all quantities from populations.

    Returns a Dict of list of Quantity objects, where the first level specifies
    OR relationships and the second AND relationships.

    Args:
        content: Guideline
        populations: Name of population resource names

    Returns: List of Dict of quantity objects

    """
    q_population = {}

    for population in populations:
        q_population[population] = get_quantities(content, population, "population")

    return q_population


def get_exposures_quantities(
    content: Dict, exposures: List[str]
) -> Dict[str, List[Quantity]]:
    """
    Get all quantities from exposures.

    Returns a Dict of list of Quantity objects, where the first level specifies
    OR relationships and the second AND relationships.

    Args:
        content: Guideline
        exposures: Name of exposure resource names

    Returns: Dict of list of quantity objects

    """
    q_exposure = {}

    for exposure in exposures:
        q_exposure[exposure] = get_quantities(content, exposure, "exposure")

    return q_exposure


def get_variable_names(quantities: Dict[str, List[Quantity]]) -> Set[str]:
    """
    Get unique variable names from dict of list of quantities.

    Args:
        quantities: Quantities

    Returns: unique variable names

    """
    variables = []
    for q_name in quantities:
        variables += [qi.variable_name for qi in quantities[q_name]]

    return set(variables)


def process_guideline(
    content: Dict,
) -> Tuple[Dict[str, List[str]], Dict[str, List[Quantity]], Dict[str, List[Quantity]]]:
    """
    Convert guideline to Quantity objects for population and exposure

    Args:
        content: Guideline

    Returns: variable names and quantities for population and exposure

    """
    evidence = get_population_exposure(content)
    q_population = get_population_quantities(content, evidence["population"])
    q_exposure = get_exposures_quantities(content, evidence["exposure"])

    variable_names = {
        "population": get_variable_names(q_population),
        "exposure": get_variable_names(q_exposure),
    }

    return variable_names, q_population, q_exposure
