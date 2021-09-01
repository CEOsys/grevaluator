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

from typing import Dict, List, Any, Optional

import pint
from jsonpath_ng.ext import parse

from . import ureg
from .fhir import find_characteristic
from .mapping import (
    unique_codeable_concept_mapping,
    codeable_concepts_to_clinical_variable,
)
from .quantity import Quantity, Medication
from .utils import nonify


def is_drug_group(resource: Dict) -> bool:
    """
    Determines whether a FHIR Group resource specifies a drug application.

    Args:
        resource: FHIR Group resource

    Returns: True if the Group resource specifies a drug application

    """
    return (
        find_characteristic(
            resource, system="https://data.cochrane.org/ontologies/core/", code="Drug"
        )
        is not None
    )


def parse_characteristics(resource: Dict) -> List[Quantity]:
    """
    Parse FHIR Group resource characteristics to Quantity objects.

    Converts all quantities that are specified in a FHIR Group resource as characteristics to Quantity objects, which
    can be applied directly on clinical data to check whether these data fulfill the specified quantity or not.

    Args:
        resource: FHIR Group resource

    Returns: List of Quantity objects.

    """
    characteristics = parse("$.characteristic[*]").find(resource)
    quantities = []

    if len(characteristics) == 1:
        characteristic = characteristics[0]
        for mapping in codeable_concepts_to_clinical_variable(
            characteristic.value["code"]
        ):
            q = characteristic_to_quantity(
                characteristic.value, variable_name=nonify(mapping["variable_name"])
            )
            # only add quantity to list if not already contained (e.g. if multiple
            # concepts from different vocabularies (SNOMED CT, Cochrane) point to the
            # same mapping
            if q not in quantities:
                quantities.append(q)
    elif is_drug_group(resource):
        q = parse_drug_application_group(resource)
        quantities.append(q)
    else:
        group_name = resource["identifier"][0]["value"]
        raise ValueError(
            f"Unknown combination of multiple characteristics in group {group_name}"
        )

    return quantities


def parse_drug_application_group(resource: Dict) -> Medication:
    """
    Parses a drug application group into a Medication (Quantity) object.

    Args:
        resource: Group resource describing a drug application.

    Returns: Medication (Quantity)

    """
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

    if dose is None:
        raise ValueError("Required 'Dose' characteristic not found")
    if drug is None:
        raise ValueError("Required 'Drug' characteristic not found")

    dose = characteristic_to_quantity(dose.context.context.context.value)

    if duration is not None:
        duration = characteristic_to_quantity(duration.context.context.context.value)

    if schedule is not None:
        schedule = characteristic_to_quantity(schedule.context.context.context.value)

    drug = unique_codeable_concept_mapping(
        drug.context.context.context.value["valueCodeableConcept"]
    )
    drug["value"] = dose.value
    drug["unit"] = dose.unit
    drug["value_low"] = dose.value_low
    drug["value_high"] = dose.value_high
    drug = mapping_to_quantity(drug)

    q = Medication(drug=drug, dose=dose, schedule=schedule, duration=duration)

    return q


def mapping_to_quantity(mapping: Dict[str, Any]) -> Quantity:
    """
    Creates a Quantity object from a mapping table entry.

    Args:
        mapping: Mapping table entry

    Returns: Quantity describing the quantity coded by the mapping table entry.

    """
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


def characteristic_to_quantity(
    char: Dict, variable_name: Optional[str] = None
) -> Quantity:
    """
    Creates a Quantity object from a Group.characteristic field
    (https://build.fhir.org/group-definitions.html#Group.characteristic).

    Args:
        char: FHIR Group resource characteristic field
        variable_name: Clinical variable name

    Returns: Quantity object describing the quantity coded by the Group.characteristic field

    """

    def get_unit(quantity: Dict) -> pint.Quantity:
        """
        Converts a unit CodeableConcept.coding to a pint.Quantity unit representation.

        Args:
            quantity: CodeableConcept.coding of a unit (system must be "https://unitsofmeasure.org")

        Returns: pint unit representation

        """
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
        mapping = unique_codeable_concept_mapping(char["valueCodeableConcept"])
        q = mapping_to_quantity(mapping)
    else:
        raise ValueError("No value found in characteristic")

    q.variable_name = variable_name

    return q
