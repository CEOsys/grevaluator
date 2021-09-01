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

from typing import Union, Optional, Type, Any
import numbers
import pint
from . import ureg


class Quantity:
    """
    Specification of a value or value range of a quantity.

    This class is used to check if a given value is compliant with (i.e. matches) the value or value range of the
    specified Quantity.

    Examples:
        # String quantity (matches a specific string only)
        q = Quantity(str, "hallo")
        q.valid("ssdf") # False
        q.valid("hallo") # True
        q.valid(101) # False

        # Boolean quantity (matches either True or False)
        q = Quantity(bool, True)
        q.valid(True) # True

        # Integer quantity (matches a numeric value)
        q = Quantity(int, 101)
        q.valid(101) # True
        q.valid(101.0) # True

        # Integer range quantity (matches a range of numbers)
        q = Quantity(int, value_low=100, value_high=101)
        q.valid(101) # True

        # Integer range quantity (matches a range of numbers with no maximal number)
        q = Quantity(int, value_low=101)
        q.valid(110) # True
        q.valid(100.99999) # False

    Args:
        datatype: Type of the quantity (str, float, int or bool)
        value: Value of the quantity (must be None if describing a value range
        value_low: Minimal acceptable value of the quantity (must be None if quantity has a single specific value;
            can be None to indicate a quantity that only has a maximal but not minimal value)
        value_high: Maximal acceptable value of the quantity (must be None if quantity has a single specific value;
            can be None to indicate a quantity that only has a minimal but not maximal value)
        unit: Unit of the quantity value or value range
        variable_name: Variable name of the quantity in the clinical dataset
    """

    datatype: Type
    value: Optional[Union[str, float, int, bool]]
    value_low: Optional[Union[float, int]]
    value_high: Optional[Union[float, int]]
    _unit: Optional[pint.Quantity]
    variable_name: Optional[str]

    def __init__(
        self,
        datatype: Type,
        value: Optional[Union[str, float, int, bool]] = None,
        value_low: Optional[Union[float, int]] = None,
        value_high: Optional[Union[float, int]] = None,
        unit: Optional[Union[str, pint.Quantity]] = None,
        variable_name: Optional[str] = None,
    ) -> None:
        def typename(dt: Any) -> str:
            """
            Returns the string representation of a type or object's type
            Args:
                dt: Type or Object

            Returns: String representation of the type

            """

            if type(dt) != type:
                dt = type(dt)
            return dt.__name__

        if datatype in [str, bool]:
            if value is None:
                raise ValueError(f"value must be set for datatype {typename(datatype)}")
            if value_low is not None:
                raise ValueError(
                    f"value_low must not be set for datatype {typename(datatype)}"
                )
            if value_high is not None:
                raise ValueError(
                    f"value_high must not be set for datatype {typename(datatype)}"
                )
            if type(value) != datatype:
                raise ValueError(
                    f"value must be of type {typename(datatype)} (was {typename(value)})"
                )
        elif datatype in [float, int]:
            if value is not None:
                if not isinstance(value, numbers.Number):
                    raise ValueError(
                        f"value must be a numeric type (was {typename(value)})"
                    )
                if value_low is not None:
                    raise ValueError(
                        f"value_low must not be set for datatype {typename(datatype)} and given value"
                    )
                if value_high is not None:
                    raise ValueError(
                        f"value_high must not be set for datatype {typename(datatype)} and given value"
                    )
            else:
                if value_low is None and value_high is None:
                    raise ValueError(
                        f"value_low and/or value_high must be set for datatype {typename(datatype)} and no given value"
                    )
                if value_low is not None and not isinstance(value_low, numbers.Number):
                    raise ValueError(
                        f"value_low must be a numeric type (was {typename(value_low)})"
                    )
                if value_high is not None and not isinstance(
                    value_high, numbers.Number
                ):
                    raise ValueError(
                        f"value_high must be a numeric type (was {typename(value_high)})"
                    )

        else:
            raise ValueError(f"Invalid datatype {datatype}")

        self.datatype = datatype
        self.value = value
        self.value_low = value_low
        self.value_high = value_high
        self._unit = unit if isinstance(unit, pint.Quantity) else ureg(unit)
        self.variable_name = variable_name

    def _str_validator(self, value: str) -> bool:
        if not type(value) == str:
            return False
        return value == self.value

    def _bool_validator(self, value: bool) -> bool:
        if not type(value) == bool:
            return False
        return value == self.value

    def _numeric_validator(self, value: Union[float, int]) -> bool:
        if not isinstance(value, numbers.Number):
            return False

        if self.value is not None:
            return value == self.value

        valid = True
        if self.value_low is not None:
            valid &= value >= self.value_low  # type: ignore

        if self.value_high is not None:
            valid &= value <= self.value_high  # type: ignore

        return valid

    @property
    def unit(self) -> Optional[pint.Quantity]:
        """
        Get quantity's unit

        Returns: Unit of the quantity

        """
        return self._unit

    @unit.setter
    def unit(self, unit: Union[str, pint.Unit]) -> None:
        self._unit = ureg(unit)

    def valid(self, value: Any) -> bool:
        """
        Determines if a given value is compliant with (i.e. matches) the value or value range of the quantity
        specification.

        Args:
            value: Value to compare

        Returns: True if value is compliant with quantity specification, False otherwise

        """
        validators = {
            bool: self._bool_validator,
            str: self._str_validator,
            int: self._numeric_validator,
            float: self._numeric_validator,
        }

        return validators[self.datatype](value)  # type: ignore

    def __repr__(self) -> str:
        """
        Get string representation of defined quantity.

        Returns: string representation of defined quantity

        """
        s = f"Quantity(datatype={str(self.datatype.__name__)}"
        for var in ["variable_name", "value", "value_low", "value_high", "unit"]:
            if getattr(self, var) is not None:
                s += f", {var}={getattr(self, var)}"
        s += ")"
        return s

    def __eq__(self, other: object) -> bool:
        """
        Compares quantity with another object.

        Args:
            other: Other object

        Returns: True if both objects describe the equal quantity, False otherwise

        """
        if not isinstance(other, Quantity):
            raise NotImplementedError

        return str(self) == str(other)


class Medication(Quantity):
    """
    Specification of a Medication.

    This class is used to check if a given drug application is compliant with (i.e. matches) the specified
    medication.

    Args:
        drug: Name of the drug.
        dose: Dosage of the drug application
        schedule: Schedule of the drug application
        duration: Duration of the drug application
    """

    drug: Quantity
    dose: Quantity
    schedule: Optional[Quantity]
    duration: Optional[Quantity]

    def __init__(
        self,
        drug: Quantity,
        dose: Quantity,
        schedule: Optional[Quantity] = None,
        duration: Optional[Quantity] = None,
    ):
        self.drug = drug
        self.dose = dose
        self.schedule = schedule
        self.duration = duration

        self.variable_name = drug.variable_name

    def valid(self, value: Any) -> bool:
        """
        Determines if a given value is compliant with (i.e. matches) the specified medication.

        Args:
            value: Value to compare

        Returns: True if value is compliant with quantity specification, False otherwise

        """
        # TODO implement proper check
        return value > 0

    def __repr__(self) -> str:
        """
        Get string representation of defined medication.

        Returns: string representation of defined medication

        """
        vals = []
        for var in ["drug", "dose", "schedule", "duration"]:

            if getattr(self, var) is not None:
                vals.append(f"{var}={getattr(self, var)}")

        s = f'Medication({", ".join(vals)})'

        return s
