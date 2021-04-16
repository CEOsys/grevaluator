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

import pytest
from comparator.quantity import Quantity


def test_quantity_str():
    q = Quantity(str, "hallo")
    assert not q.valid("ssdf")
    assert q.valid("hallo")
    assert not q.valid(101)
    assert not q.valid(101.0)
    assert not q.valid(True)


def test_quantity_bool():
    q = Quantity(bool, True)
    assert not q.valid("ssdf")
    assert not q.valid(101)
    assert not q.valid(101.0)
    assert q.valid(True)


def test_quantity_int_value():
    q = Quantity(int, 101)
    assert not q.valid("ssdf")
    assert q.valid(101)
    assert q.valid(101.0)
    assert not q.valid(True)


def test_quantity_int_value_low():
    q = Quantity(int, value_low=101)
    assert not q.valid("ssdf")
    assert q.valid(101)
    assert q.valid(101.0)
    assert q.valid(110)
    assert not q.valid(100.99999)
    assert not q.valid(True)


def test_quantity_int_value_high():
    q = Quantity(int, value_high=101)
    assert not q.valid("ssdf")
    assert q.valid(101)
    assert q.valid(101.0)
    assert not q.valid(110)
    assert q.valid(100.99999)
    assert q.valid(True)


def test_quantity_int_value_low_high():
    q = Quantity(int, value_low=100, value_high=101)
    assert not q.valid("ssdf")
    assert q.valid(101)
    assert q.valid(101.0)
    assert q.valid(100)
    assert q.valid(100.0)
    assert not q.valid(101.1)
    assert not q.valid(99.99999)
    assert q.valid(100.1)
    assert not q.valid(True)


def test_quantity_construct():
    with pytest.raises(ValueError, match="must be of type"):
        Quantity(str, 1)
    with pytest.raises(ValueError, match="must be of type"):
        Quantity(str, True)
    with pytest.raises(ValueError, match="value must be set for"):
        Quantity(str, value_low="a")
    with pytest.raises(ValueError, match="value must be set for"):
        Quantity(str, value_high="a")

    with pytest.raises(ValueError, match="must be of type"):
        Quantity(bool, 1)
    with pytest.raises(ValueError, match="must be of type"):
        Quantity(bool, "True")
    with pytest.raises(ValueError, match="value must be set for"):
        Quantity(bool, value_low="a")
    with pytest.raises(ValueError, match="value must be set for"):
        Quantity(bool, value_high="a")

    for datatype in [int, float]:
        with pytest.raises(ValueError, match="value must be a numeric type"):
            Quantity(datatype, value="str")
        with pytest.raises(ValueError, match="value_low must not be set for datatype"):
            Quantity(datatype, value=1.0, value_low=1.0)
        with pytest.raises(ValueError, match="value_high must not be set for datatype"):
            Quantity(datatype, value=1.0, value_high=1.0)
        with pytest.raises(
            ValueError, match="value_low and/or value_high must be set for datatype"
        ):
            Quantity(datatype)


test_quantity_str()
test_quantity_bool()
test_quantity_int_value()
test_quantity_int_value_low()
test_quantity_int_value_high()
test_quantity_int_value_low_high()
test_quantity_construct()
