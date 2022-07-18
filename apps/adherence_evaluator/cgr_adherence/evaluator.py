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

from typing import Dict, List, Set, Tuple
from jsonpath_ng.ext import parse
from .fhir import find_resource
from .parser import parse_characteristics
from .quantity import Quantity


class AdherenceEvaluator:
    """
    Adherence Evaluator Module

    Args:
        rec: Clinical guideline recommendation (json)
    """

    def __init__(self, rec: Dict):
        self.content = rec

    def _get_group_names(
        self, evidence_identifier: str, evidence_type: str
    ) -> List[str]:
        """
        Get characteristics group names from guideline recommendation for population or exposure

        Args:
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

        entity = find_resource(
            self.content, resource_name, identifier=evidence_identifier
        )

        group_names = [
            m.value
            for m in parse(
                f'$.characteristic[?@.{attribute}.type=="Group"].{attribute}.identifier.value'
            ).find(entity)
        ]
        return group_names

    def _get_quantities(
        self, evidence_identifier: str, evidence_type: str
    ) -> List[Quantity]:
        """
        Parses guideline recommendation into quantities (to test dataset)

        Args:
            evidence_identifier: Identifier of the population or exposure resource
            evidence_type: "population" or "exposure"

        Returns: Quantities belonging to the evidence identifier resource

        """

        group_names = self._get_group_names(evidence_identifier, evidence_type)

        quantities = []

        for group_name in group_names:
            resource = find_resource(self.content, "Group", group_name)
            quantities += parse_characteristics(resource)

        return quantities

    def _get_clinical_variable_names(
        self, quantities: Dict[str, List[Quantity]]
    ) -> Set[str]:
        """
        Get unique variable names from dict of list of quantities.

        Args:
            quantities: Quantities

        Returns: unique variable names

        """
        variables: List[str] = []
        for q_name in quantities:
            variables += [qi.variable_name for qi in quantities[q_name]]

        return set(variables)

    def get_population_exposure(self) -> Dict[str, List[str]]:
        """
        Extract names of the population and exposure groups from the full guideline recommendation.

        Returns: name of population and exposure groups

        """
        evidence = find_resource(self.content, "Evidence")
        res = []
        for var in evidence["variableDefinition"]:
            res.append(
                (
                    var["variableRole"]["coding"][0]["code"],
                    var["observed"]["identifier"]["value"],
                )
            )

        return {
            key: [v[1] for v in res if v[0] == key]
            for key in ["population", "exposure"]
        }

    def get_population_quantities(
        self, populations: List[str]
    ) -> Dict[str, List[Quantity]]:
        """
        Get all quantities from populations.

        Returns a Dict of list of Quantity objects, where the first level specifies
        OR relationships and the second AND relationships.

        Args:
            populations: Name of population resource names

        Returns: List of Dict of quantity objects

        """
        q_population = {}

        for population in populations:
            q_population[population] = self._get_quantities(population, "population")

        return q_population

    def get_exposures_quantities(
        self, exposures: List[str]
    ) -> Dict[str, List[Quantity]]:
        """
        Get all quantities from exposures.

        Returns a Dict of list of Quantity objects, where the first level specifies
        OR relationships and the second AND relationships.

        Args:
            exposures: Name of exposure resource names

        Returns: Dict of list of quantity objects

        """
        q_exposure = {}

        for exposure in exposures:
            q_exposure[exposure] = self._get_quantities(exposure, "exposure")

        return q_exposure

    def process_guideline_recommendation(
        self,
    ) -> Tuple[
        Dict[str, Set[str]], Dict[str, List[Quantity]], Dict[str, List[Quantity]]
    ]:
        """
        Convert guideline recommendation to Quantity objects for population and exposure

        Returns: variable names and quantities for population and exposure

        """
        evidence = self.get_population_exposure()
        q_population = self.get_population_quantities(evidence["population"])
        q_exposure = self.get_exposures_quantities(evidence["exposure"])

        variable_names = {
            "population": self._get_clinical_variable_names(q_population),
            "exposure": self._get_clinical_variable_names(q_exposure),
        }

        return variable_names, q_population, q_exposure
