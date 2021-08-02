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

from typing import Dict, List

import pandas as pd

from . import mapping_table


def codeable_concepts_to_clinical_variable(codeable_concept: Dict) -> List[Dict]:
    """
    Get mappings from guideline codeableConcept to specific variables from mapping table

    Args:
        codeable_concept: CodeableConcept from guideline

    Returns: List of mapping information

    """

    def get_mapping(coding: Dict) -> List[Dict]:
        """
        Get mapping from guideline codeable concept code to specific variables from mapping table

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

    mappings: List[Dict] = []

    for code in codeable_concept["coding"]:
        mappings += get_mapping(code)

    return mappings


def unique_codeable_concept_mapping(codeable_concept: Dict) -> Dict:
    """
    Retrieve unique mapping for codeable concept.

    If multiple codings are specified for a codeableConcept, this function makes
    sure that all codings map to the same item.

    Args:
        codeable_concept: codeableConcept from guideline

    Returns: unique mapping, if available

    """
    mappings = codeable_concepts_to_clinical_variable(codeable_concept)

    cols = ["variable_name", "type", "value", "value_low", "value_high"]
    n_unique_concepts = (
        pd.DataFrame(mappings).fillna("")[cols].drop_duplicates().shape[0]
    )
    assert (
        n_unique_concepts == 1
    ), f"Expected exactly one unique concept, found {n_unique_concepts}"

    return mappings[0]
