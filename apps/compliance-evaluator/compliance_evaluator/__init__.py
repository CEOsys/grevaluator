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

import os
from pathlib import Path
import pint
import pandas as pd


def init_unit_registry() -> pint.UnitRegistry:
    """
    Initializes the unit registry once for the module (prevents the need for multiple initializations).

    Returns: Initialized unit registry

    """
    ureg = pint.UnitRegistry(
        preprocessors=[
            lambda s: s.replace("%%", " permille "),
            lambda s: s.replace("%", " percent "),
        ]
    )
    ureg.define(
        pint.unit.UnitDefinition(
            "permille",
            "%%",
            (),
            pint.converters.ScaleConverter(0.001),
        )
    )
    ureg.define(
        pint.unit.UnitDefinition(
            "percent",
            "%",
            (),
            pint.converters.ScaleConverter(0.01),
        )
    )
    ureg.define(
        pint.unit.UnitDefinition(
            "breaths",
            "breaths",
            (),
            pint.converters.ScaleConverter(1),
        )
    )

    return ureg


def init_mapping_table() -> pd.DataFrame:
    """
    Initializes the mapping table for concepts to specific variable names / values once for the module.

    Returns: Mapping table

    """
    path = Path(os.getenv("CEOSYS_BASE_PATH", ".")) / "res" / "concept-mappings.xlsx"
    df_mapping = pd.read_excel(path, engine="openpyxl")
    df_mapping["system"] = df_mapping["system"].str.rstrip("/")
    return df_mapping


ureg = init_unit_registry()
mapping_table = init_mapping_table()
