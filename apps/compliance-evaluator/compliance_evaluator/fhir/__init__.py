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
from typing import Dict, Optional, Iterator

from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse


def findall_resources(
    bundle: Dict, resource_type: str, identifier: str = None
) -> Iterator[Dict]:
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


def find_resource(bundle: Dict, resource_type: str, identifier: str = None) -> Dict:
    """
    Finds first resource of a given type in a bundle.

    Args:
        bundle: JSON structure (dict) of the bundle
        resource_type: resource type to search for
        identifier: value of the identifier of the resource (to locate specific resources)

    Returns: First resource of given type

    """
    try:
        res = next(findall_resources(bundle, resource_type, identifier))
    except StopIteration:
        if identifier is not None:
            msg = f'No resource "{resource_type}" with identifier "{identifier}" found'
        else:
            msg = f'No resource "{resource_type}" found'
        raise KeyError(msg) from None
    return res


def find_characteristic(
    resource: Dict, system: str, code: str
) -> Optional[jsonpath.DatumInContext]:
    """
    Finds a single characteristic (Coding defined by system and code) in a FHIR resource.

    For reference to the FHIR Coding datatype see https://www.hl7.org/fhir/datatypes.html#Coding.

    Args:
        resource: FHIR resource
        system: Identity of the terminology system
        code: Symbol in syntax defined by the system

    Returns: A single characteristic if found as specified, or None

    """
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
