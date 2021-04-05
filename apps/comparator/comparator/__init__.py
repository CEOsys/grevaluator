import os
from pathlib import Path
import pint
import pandas as pd


def init_unit_registry() -> pint.UnitRegistry:
    """
    Initializes the unit registry once for the module.

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

    return ureg


def init_mapping_table() -> pd.DataFrame:
    """
    Initializes the mapping table for concepts to specific variable names / values once for the module.

    Returns: Mapping table

    """
    path = Path(os.getenv("CEOSYS_BASE_PATH", ".")) / "res" / "concept-mappings.xlsx"
    df_mapping = pd.read_excel(path)
    df_mapping["system"] = df_mapping["system"].str.rstrip("/")
    return df_mapping


ureg = init_unit_registry()
mapping_table = init_mapping_table()
