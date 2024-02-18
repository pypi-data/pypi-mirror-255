import os
from tempfile import TemporaryDirectory
from typing import Optional

import numpy
import pytest
import pyunitsystem as unitsystem

from nxtomo.nxobject.nxobject import ElementWithUnit, NXobject


class test_nx_object:
    """Tets API of the nx object"""

    with pytest.raises(TypeError):
        NXobject(node_name=12)
    with pytest.raises(TypeError):
        NXobject(node_name="test", parent=12)

    nx_object = NXobject(node_name="NXobject")
    with pytest.raises(NotImplementedError):
        nx_object.to_nx_dict(nexus_path_version=1.0)
    assert nx_object.is_root is True

    with pytest.raises(TypeError):
        nx_object.node_name = 12

    with pytest.raises(AttributeError):
        nx_object.test = 12

    class MyNXObject(NXobject):
        def to_nx_dict(
            self,
            nexus_path_version: Optional[float] = None,
            data_path: Optional[str] = None,
        ) -> dict:
            return {
                f"{self.path}/test": "toto",
            }

    my_nx_object = MyNXObject(node_name="NxObject2")

    with TemporaryDirectory() as folder:
        file_path = os.path.join(folder, "my_nexus.nx")
        assert not os.path.exists(file_path)
        my_nx_object.save(
            file_path=file_path, data_path="/object", nexus_path_version=1.0
        )
        assert os.path.exists(file_path)

        with pytest.raises(KeyError):
            my_nx_object.save(
                file_path=file_path,
                data_path="/object",
                nexus_path_version=1.0,
                overwrite=False,
            )

        my_nx_object.save(
            file_path=file_path,
            data_path="/object",
            nexus_path_version=1.0,
            overwrite=True,
        )


def test_ElementWithUnit():
    """test the ElementWithUnit class"""
    elmt = ElementWithUnit(default_unit=unitsystem.MetricSystem.METER)
    elmt.value = 12.3
    assert elmt.si_value == 12.3
    elmt.unit = "cm"
    assert numpy.isclose(elmt.si_value, 0.123)

    with pytest.raises(TypeError):
        ElementWithUnit(default_unit=None)

    elmt = ElementWithUnit(default_unit=unitsystem.EnergySI.KILOELECTRONVOLT)
    elmt.value = 12.3
    assert elmt.si_value == 12.3 * unitsystem.EnergySI.KILOELECTRONVOLT.value
    elmt.unit = "J"
    assert elmt.si_value == 12.3
    str(elmt)
    assert str(elmt) == "12.3 J"

    elmt = ElementWithUnit(default_unit=unitsystem.TimeSystem.SECOND)
    elmt.value = 8.0
    assert elmt.si_value == 8.0
    elmt.unit = "minute"
    elmt.si_value == 8.0 / 60.0
    str(elmt)

    with pytest.raises(ValueError):
        elmt.unit = "not minute"
    with pytest.raises(TypeError):
        elmt.unit = 123
