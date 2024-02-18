"""
module for handling a `nxmonitor <https://manual.nexusformat.org/classes/base_classes/NXmonitor.html>`_
"""

from functools import partial
from operator import is_not
from typing import Optional, Union
import numpy

from silx.utils.proxy import docstring

from nxtomo.paths.nxtomo import get_paths as get_nexus_paths
from nxtomo.nxobject.nxobject import ElementWithUnit, NXobject
from nxtomo.utils import get_data_and_unit

from pyunitsystem import ElectricCurrentSystem


class NXmonitor(NXobject):
    def __init__(self, node_name="control", parent: Optional[NXobject] = None) -> None:
        """
        representation of `nexus NXmonitor <https://manual.nexusformat.org/classes/base_classes/NXmonitor.html>`_.
        A monitor of incident beam data.

        :param str node_name: name of the detector in the hierarchy
        :param Optional[NXObject] parent: parent in the nexus hierarchy
        """
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._data = ElementWithUnit(default_unit=ElectricCurrentSystem.AMPERE)
        self._set_freeze(True)

    @property
    def data(self) -> Optional[numpy.ndarray]:
        """
        monitor data.
        In the case of NXtomo it expects to contains machine electric current for each frame
        """
        return self._data

    @data.setter
    def data(self, data: Optional[Union[numpy.ndarray, list, tuple]]):
        if isinstance(data, (tuple, list)):
            if len(data) == 0:
                data = None
            else:
                data = numpy.asarray(data)

        if isinstance(data, numpy.ndarray):
            if not data.ndim == 1:
                raise ValueError(f"data is expected to be 1D and not {data.ndim}d")
        elif not isinstance(data, type(None)):
            raise TypeError(
                f"data is expected to be None or a numpy array. Not {type(data)}"
            )
        self._data.value = data

    @docstring(NXobject)
    def to_nx_dict(
        self,
        nexus_path_version: Optional[float] = None,
        data_path: Optional[str] = None,
    ) -> dict:
        nexus_paths = get_nexus_paths(nexus_path_version)
        monitor_nexus_paths = nexus_paths.nx_monitor_paths

        nx_dict = {}
        if self.data.value is not None:
            if monitor_nexus_paths.DATA_PATH is not None:
                data_path = f"{self.path}/{monitor_nexus_paths.DATA_PATH}"
                nx_dict[data_path] = self.data.value
                nx_dict["@".join([data_path, "units"])] = str(self.data.unit)

        if nx_dict != {}:
            nx_dict[f"{self.path}@NX_class"] = "NXmonitor"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        """
        Create and load an NXmonitor from data on disk
        """
        nexus_paths = get_nexus_paths(nexus_version)
        monitor_nexus_paths = nexus_paths.nx_monitor_paths
        if monitor_nexus_paths.DATA_PATH is not None:
            self.data, self.data.unit = get_data_and_unit(
                file_path=file_path,
                data_path="/".join([data_path, monitor_nexus_paths.DATA_PATH]),
                default_unit="Ampere",
            )

    @staticmethod
    @docstring(NXobject)
    def concatenate(nx_objects: tuple, node_name: str = "control"):
        # filter None obj
        nx_objects = tuple(filter(partial(is_not, None), nx_objects))
        if len(nx_objects) == 0:
            return None
        nx_monitor = NXmonitor(node_name=node_name)
        data = [
            nx_obj.data.value * nx_obj.data.unit.value
            for nx_obj in nx_objects
            if nx_obj.data.value is not None
        ]
        if len(data) > 0:
            nx_monitor.data = numpy.concatenate(data)
        return nx_monitor
