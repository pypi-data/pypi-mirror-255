"""
module for handling a `nxtransformations <https://manual.nexusformat.org/classes/base_classes/nxtransformations.html#nxtransformations>`_
"""

import typing
import logging
import h5py

from copy import deepcopy

from silx.utils.proxy import docstring
from silx.io.dictdump import nxtodict

from nxtomo.nxobject.nxobject import NXobject
from nxtomo.io import HDF5File
from nxtomo.utils.transformation import (
    Transformation,
    GravityTransformation,
    get_lr_flip as _get_lr_flip,
    get_ud_flip as _get_ud_flip,
)
from nxtomo.paths.nxtomo import get_paths as get_nexus_paths

_logger = logging.getLogger(__name__)


class NXtransformations(NXobject):
    def __init__(self, node_name: str = "transformations", parent=None) -> None:
        """
        Collection of axis-based translations and rotations to describe a geometry

        For tomotools the first usage would be to allow users to provide more metadata to tag acquisition (like 'detector has been rotate' of 90 degree...)

        :param str node_name: name of the detector in the hierarchy
        :param Optional[NXObject] parent: parent in the nexus hierarchy
        """
        super().__init__(node_name, parent)
        self._set_freeze(False)
        self._transformations = dict()
        # dict with axis_name as value and Transforamtion as value. Simplify handling compared to a tuple / list / set and ensure the axis_name is unique
        self._set_freeze(True)

    @property
    def transformations(self) -> tuple:
        """
        return dict with str as key and Transformation as value
        """
        return tuple(self._transformations.values())

    @transformations.setter
    def transformations(self, transformations: tuple):
        """
        :param dict transformations: dict as [str, Transformation]
        """
        # check type
        if not isinstance(transformations, (tuple, list)):
            raise TypeError(
                f"transformations is expected to be a dict. {type(transformations)} provided instead"
            )
        for transformation in transformations:
            if not isinstance(transformation, Transformation):
                raise TypeError(
                    f"element are expected to be instances of {Transformation}. {type(transformation)} provided instead"
                )
        # convert it to a dict for conveniance
        self._transformations = {
            transformation.axis_name: transformation
            for transformation in transformations
        }

    def addTransformation(self, *args, **kwargs):
        _logger.warning("addTransformation is deprecated. Please us add_transformation")
        self.add_transformation(*args, **kwargs)

    def add_transformation(
        self, transformation: Transformation, overwrite=False, skip_if_exists=False
    ):
        """
        add a transformation to the existing one.

        :param Transformation transformation: transformation to be added
        :param bool overwrite: if a transformation with the same axis_name already exists then overwrite it
        :param bool skip_if_exists: if a transformation with the same axis_name already exists then keep the existing one
        :raises: KeyError, if a transforamtion with the same axis_name already registered
        """
        if skip_if_exists is overwrite is True:
            raise ValueError(
                "both 'skip_if_exists' and 'overwrite' set to True. Undefined behavior"
            )
        if transformation.axis_name in self._transformations:
            if overwrite:
                _logger.info(
                    "A transformation over {transformation.axis_name} is already registered. Will overwrite it"
                )
            elif skip_if_exists:
                _logger.info(
                    "A transformation over {transformation.axis_name} is already registered. Skip add"
                )
                return
            else:
                raise KeyError(
                    f"A transformation over {transformation.axis_name} is already registered. axis_name must be unique"
                )

        self._transformations[transformation.axis_name] = transformation

    def rmTransformation(self, *args, **kwargs):
        _logger.warning("rmTransformation is deprecated. Please us rm_transformation")
        self.rm_transformation(*args, **kwargs)

    def rm_transformation(self, transformation: Transformation):
        """
        remove the provided transformation to the list of existing transformation

        :param Transformation transformation: transformation to be added
        """
        self._transformations.pop(transformation.axis_name, None)

    @docstring(NXobject)
    def to_nx_dict(
        self,
        nexus_path_version: typing.Optional[float] = None,
        data_path: typing.Optional[str] = None,
        solve_empty_dependency: bool = False,
    ) -> dict:
        """
        :param bool append_gravity: If True all transformation without dependancy will be depending on a "gravity" Transformation which represent the gravity
        """
        if len(self._transformations) == 0:
            # if no transformation, avoid creating the group
            return {}
        nexus_paths = get_nexus_paths(nexus_path_version)
        transformations_nexus_paths = nexus_paths.nx_transformations_paths
        if transformations_nexus_paths is None:
            _logger.info(
                f"no TRANSFORMATIONS provided for version {nexus_path_version}"
            )
            return {}

        transformations = deepcopy(self._transformations)
        # preprocessing for gravity
        if solve_empty_dependency:
            transformations_needing_gravity = dict(
                filter(
                    lambda pair: pair[1].depends_on in (None, ""),
                    transformations.items(),
                )
            )
            if len(transformations_needing_gravity) > 0:
                gravity = GravityTransformation()
                gravity_name = gravity.axis_name
                if gravity_name in transformations.keys():
                    _logger.warning(
                        f"transformations already contains a transformation named '{gravity.axis_name}'. Unable to expend transformation chain (cannot append twice gravity)"
                    )
                else:
                    transformations[gravity_name] = gravity
                # update transformations needing gravity
                for transformation in transformations_needing_gravity.values():
                    transformation.depends_on = gravity_name

        # dump Transformation
        nx_dict = {}
        for transformation in transformations.values():
            if not isinstance(transformation, Transformation):
                raise TypeError(
                    f"transformations are expected to be instances of {Transformation}. {type(transformation)} provided instead."
                )
            nx_dict.update(
                transformation.to_nx_dict(
                    transformations_nexus_paths=transformations_nexus_paths,
                    data_path=self.path,
                )
            )
        nx_dict[f"{self.path}@NX_class"] = "NX_transformations"
        nx_dict[f"{self.path}@units"] = "NX_TRANSFORMATION"
        return nx_dict

    @staticmethod
    def load_from_file(
        file_path: str, data_path: str, nexus_version: typing.Optional[float]
    ):
        """
        create an instance of :class:`~nxtomo.nxobject.nxtransformations,NXtransformations` and load it value from
        the given file and data path
        """
        result = NXtransformations()
        return result._load(
            file_path=file_path, data_path=data_path, nexus_version=nexus_version
        )

    def _load(
        self, file_path: str, data_path: str, nexus_version: typing.Optional[float]
    ) -> NXobject:
        """
        Create and load an NXmonitor from data on disk
        """
        nexus_paths = get_nexus_paths(nexus_version)
        transformations_nexus_paths = nexus_paths.nx_transformations_paths

        with HDF5File(file_path, mode="r", swmr=True) as h5f:
            if data_path == "":
                pass
            elif data_path not in h5f:
                _logger.error(
                    f"No NXtransformations found in {file_path} under {data_path} location."
                )
                return

        transformations_as_nx_dict = nxtodict(file_path, path=data_path)
        # filter attributes from the dict (as a convention dict contain '@' char)
        transformations_keys = dict(
            filter(
                lambda a: "@" not in a[0],
                transformations_as_nx_dict.items(),
            )
        )
        for key in transformations_keys:
            transformation = Transformation.from_nx_dict(
                axis_name=key,
                dict_=transformations_as_nx_dict,
                transformations_nexus_paths=transformations_nexus_paths,
            )
            if transformation is None:
                # if failed to load transformation (old version of nexus ?)
                continue
            else:
                self.add_transformation(transformation=transformation)
        return self

    @staticmethod
    @docstring(NXobject)
    def concatenate(nx_objects: tuple, node_name="transformations"):
        res = NXtransformations(node_name=node_name)
        for nx_transformations in nx_objects:
            if not isinstance(nx_transformations, NXtransformations):
                raise TypeError
            for transformation in nx_transformations.transformations:
                res.add_transformation(transformation, skip_if_exists=True)
        return res

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, NXtransformations):
            return False
        else:
            # to check equality we filter gravity as it can be provided at the end and as the reference
            def is_gravity(transformation):
                return transformation == GravityTransformation()

            return list(filter(is_gravity, self.transformations)) == list(
                filter(is_gravity, __value.transformations)
            )

    @staticmethod
    def is_a_valid_group(group: h5py.Group) -> bool:
        """
        check if the group fix an NXtransformations.
        For now the only condition is to be a group and to get NXtransformations as attr
        """
        if not isinstance(group, h5py.Group):
            return False
        return group.attrs.get("NX_class", None) in (
            "NX_transformations",
            "NX_TRANSFORMATIONS",
        )

    def __len__(self):
        return len(self.transformations)


def get_lr_flip(transformations: typing.Union[tuple, NXtransformations]) -> tuple:
    """
    check along all transformations if find Transformation matching 'LRTransformation'

    return a tuple with all matching keys
    """
    if isinstance(transformations, NXtransformations):
        transformations = transformations.transformations
    return _get_lr_flip(transformations)


def get_ud_flip(transformations: typing.Union[tuple, NXtransformations]) -> tuple:
    """
    check along all transformations if find Transformation matching 'UDTransformation'

    return a tuple with all matching keys
    """
    if isinstance(transformations, NXtransformations):
        transformations = transformations.transformations
    return _get_ud_flip(transformations)
