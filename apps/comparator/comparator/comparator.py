from typing import Dict, List
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


def get_mapping(coding):
    system = coding["system"].rstrip("/").strip()  # noqa
    code = coding["code"].strip()  # noqa
    res = mapping_table.query("(code==@code) & (system==@system)")
    if len(res) == 0:
        raise ValueError(f"Could not find mapping for code {coding}")
    elif len(res) > 1:
        raise ValueError(f"Multiple mappings found for code {coding}")
    return res.iloc[0].to_dict()


def nonify(v):
    if pd.isna(v):
        return None
    return v


def get_unique_mapping(codeableConcept):
    mappings = []
    for code in codeableConcept["coding"]:
        mappings.append(get_mapping(code))

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
        if not quantity["system"] == "http://unitsofmeasure.org":
            raise ValueError(
                f'Can only use "http://unitsofmeasure.org" as unit system, got {quantity["system"]} instead'
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
            resource, system="http://data.cochrane.org/ontologies/core/", code="Drug"
        )
        is not None
    )


def parse_characteristics(resource):
    characteristics = parse("$.characteristic[*]").find(resource)

    if len(characteristics) == 1:
        characteristic = characteristics[0]
        mapping = get_unique_mapping(characteristic.value["code"])
        q = get_quantity(
            characteristic.value, variable_name=nonify(mapping["variable_name"])
        )
    elif is_drug_group(resource):
        q = parse_drug_group(resource)
    else:
        group_name = resource["identifier"][0]["value"]
        raise ValueError(
            f"Unknown combination of multiple characteristics in group {group_name}"
        )

    return q


def parse_drug_group(resource):
    duration = find_characteristic(
        resource, system="http://data.cochrane.org/ontologies/pico/", code="Duration"
    )
    schedule = find_characteristic(
        resource, system="http://data.cochrane.org/ontologies/pico/", code="Schedule"
    )
    dose = find_characteristic(
        resource, system="http://data.cochrane.org/ontologies/pico/", code="Dose"
    )
    drug = find_characteristic(
        resource, system="http://data.cochrane.org/ontologies/core/", code="Drug"
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


def get_population_exposure(content):
    evidence = find_resource(content, "Evidence")
    res = []
    for var in evidence["variableDefinition"]:
        res.append(
            (
                var["variableRole"]["coding"][0]["code"],
                var["observed"]["identifier"]["value"],
            )
        )

    assert (
        sum(r[0] == "population" for r in res) == 1
    ), "Expected exactly one population entry in Evidence resource"
    assert (
        sum(r[0] == "exposure" for r in res) == 1
    ), "Expected exactly one exposure entry in Evidence resource"

    return dict(res)


def get_group_names(content, evidence, key):
    if key == "population":
        resource_name = "Group"
        attribute = "valueReference"
    elif key == "exposure":
        resource_name = "EvidenceVariable"
        attribute = "definitionReference"
    else:
        raise ValueError(f'Invalid key {key}. Expected "population" or "exposure"')

    entity = find_resource(content, resource_name, identifier=evidence[key])

    group_names = [
        m.value
        for m in parse(
            f'$.characteristic[?@.{attribute}.type=="Group"].{attribute}.identifier.value'
        ).find(entity)
    ]
    return group_names


def get_quantities(content: Dict, evidence: Dict, key: str) -> List[Quantity]:

    group_names = get_group_names(content, evidence, key)

    quantities = []

    for group_name in group_names:
        resource = find_resource(content, "Group", group_name)
        q = parse_characteristics(resource)
        quantities.append(q)

    return quantities


def process_guideline(content):
    evidence = get_population_exposure(content)
    q_population = get_quantities(content, evidence, "population")
    q_exposure = get_quantities(content, evidence, "exposure")

    variables = [q.variable_name for q in q_population + q_exposure]

    return variables, q_population, q_exposure
