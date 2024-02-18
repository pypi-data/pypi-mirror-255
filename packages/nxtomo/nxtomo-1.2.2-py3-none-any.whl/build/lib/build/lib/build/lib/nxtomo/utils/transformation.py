"""module to provide helper classes to define transformations contained in NXtransformations"""

import typing
import logging
import numpy

from pyunitsystem.metricsystem import MetricSystem

from silx.utils.enum import Enum as _Enum


_logger = logging.getLogger(__name__)


class TransformationType(_Enum):
    """
    possible NXtransformations types
    """

    TRANSLATION = "translation"
    ROTATION = "rotation"


class TransformationAxis:
    """
    Some predefined axis for tomography acquisition done at esrf.
    Warning those are stored as (X, Y, Z) and not under the usual numpy reference (Z, Y, X)

    space is defined here: https://tomo.gitlab-pages.esrf.fr/ebs-tomo/master/modelization.html
    """

    AXIS_X = (1, 0, 0)
    AXIS_Y = (0, 1, 0)
    AXIS_Z = (0, 0, 1)


class Transformation:
    """
    Define a Transformation done on an axis

    :param str axis_name: name of the transformation.
    :param TransformationType transformation_type: type of the formation. As unit depends on the type of transformation this is not possible to modify it once created
    :param vector: vector of the transformation. Expected as a tuple of three values that define the axis for this transformation. Can also be an instance of TransformationAxis predefining some default axis
    :param Optional[str] depends_on: used to determine transformation chain. If depends on no other transformation then should be considered as if it is depending on "gravity" only.
    :warning: when convert a rotation which as 'radian' as units it will be cast to degree
    """

    __isfrozen = False
    # to ease API and avoid setting wrong attributes we 'freeze' the attributes
    # see https://stackoverflow.com/questions/3603502/prevent-creating-new-attributes-outside-init

    def __init__(
        self,
        axis_name: str,
        value,
        transformation_type: TransformationType,
        vector: typing.Union[typing.Tuple[float, float, float], TransformationAxis],
        depends_on: typing.Optional[str] = None,
    ) -> None:
        self._axis_name = axis_name
        self._transformation_values = None
        self.transformation_values = value
        self._transformation_type = TransformationType.from_value(transformation_type)
        self._units = (
            MetricSystem.METER
            if self._transformation_type is TransformationType.TRANSLATION
            else "degree"
        )
        if isinstance(vector, TransformationAxis):
            self._vector = vector.value()
        elif not isinstance(vector, (tuple, list, numpy.ndarray)) or len(vector) != 3:
            raise TypeError(
                f"vector should be a tuple of three elements. {vector} provided"
            )
        else:
            self._vector = tuple(vector)
            assert len(self._vector) == 3, ""
        self._offset = (0, 0, 0)
        self._depends_on = None
        self.depends_on = depends_on
        self._equipment_component = None
        self._set_freeze()

    def _set_freeze(self, freeze=True):
        self.__isfrozen = freeze

    @property
    def axis_name(self) -> str:
        return self._axis_name

    @axis_name.setter
    def axis_name(self, axis_name: str):
        self._axis_name = axis_name

    @property
    def transformation_values(self):
        return self._transformation_values

    @transformation_values.setter
    def transformation_values(self, values):
        if values is not None and not numpy.isscalar(values):
            self._transformation_values = numpy.array(values)
        else:
            self._transformation_values = values

    @property
    def transformation_type(self) -> TransformationType:
        return self._transformation_type

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, units: typing.Union[str, MetricSystem]):
        """
        :raises ValueError: if units is invalid (depends on the transformation type).
        """
        if units == "m/s2":
            # corner cases of the gravity
            self._units = units
        elif self._transformation_type is TransformationType.TRANSLATION:
            self._units = MetricSystem.from_value(units)
        elif units in ("rad", "radian", "radians"):
            self._units = "rad"
        elif units in ("degree", "degrees"):
            self._units = "degree"
        else:
            raise ValueError(f"Unrecognized unit {units}")

    @property
    def vector(self) -> typing.Tuple[float, float, float]:
        return self._vector

    @property
    def offset(self) -> tuple:
        return self._offset

    @offset.setter
    def offset(self, offset: typing.Union[tuple, list, numpy.ndarray]):
        if not isinstance(offset, (tuple, list, numpy.ndarray)):
            raise TypeError(
                f"offset is expected to be a vector of three elements. {type(offset)} provided"
            )
        elif not len(offset) == 3:
            raise TypeError(
                f"offset is expected to be a vector of three elements. {offset} provided"
            )
        self._offset = tuple(offset)

    @property
    def depends_on(self):
        return self._depends_on

    @depends_on.setter
    def depends_on(self, depends_on):
        """
        :param Optional[Transformation] depends_on:
        """
        if not (depends_on is None or isinstance(depends_on, str)):
            raise TypeError(
                f"offset is expected to be None or str. {type(depends_on)} provided"
            )
        self._depends_on = depends_on

    @property
    def equipment_component(self) -> typing.Optional[str]:
        return self._equipment_component

    @equipment_component.setter
    def equipment_component(self, equipment_component: typing.Optional[str]):
        if not (equipment_component is None or isinstance(equipment_component, str)):
            raise TypeError(
                f"equipment_component is expect to ne None or a str. {type(equipment_component)} provided"
            )
        self._equipment_component = equipment_component

    def get_transformation_values_in_common_unit(self):
        transformation_values = self.transformation_values
        units = self.units
        if units in ("radian", "rad", "rads", "radians"):
            if transformation_values is None:
                return None, "degree"
            else:
                transformation_values = numpy.rad2deg(transformation_values)
                return transformation_values % 360, "degree"
        elif units in ("degree", "degrees"):
            if transformation_values is None:
                return None, "degree"
            else:
                return transformation_values % 360, "degree"
        elif units == "m/s2":
            return transformation_values, "m/s2"
        else:
            converted_values = (
                transformation_values * MetricSystem.from_str(str(units)).value
            )
            return converted_values, MetricSystem.METER

    def to_nx_dict(self, transformations_nexus_paths, data_path: str):
        def join(my_list):
            # filter empty strings
            my_list = tuple(
                filter(
                    lambda a: bool(
                        a
                    ),  # return False if a is an empty string else True,
                    my_list,
                )
            )
            if len(my_list) == 0:
                return ""
            else:
                return "/".join(my_list)

        transformation_values = self.transformation_values
        if transformation_values is None:
            _logger.error(f"no values defined for {self.axis_name}")
        elif numpy.isscalar(transformation_values):
            pass
        else:
            transformation_values = numpy.array(transformation_values)
        units = self.units
        if units == "radian":
            if transformation_values is not None:
                transformation_values = numpy.rad2deg(transformation_values)
            units = "degree"
        elif isinstance(units, MetricSystem):
            units = str(units)

        res = {
            join((data_path, self.axis_name)): self.transformation_values,
            join(
                (
                    data_path,
                    self.axis_name + transformations_nexus_paths.TRANSFORMATION_TYPE,
                )
            ): self.transformation_type.value,
            join((data_path, f"{self.axis_name}@units")): units,
        }

        # vector is mandatory
        res[
            join((data_path, f"{self.axis_name}{transformations_nexus_paths.VECTOR}"))
        ] = self.vector
        if self.offset is not None:
            res[
                join(
                    (data_path, f"{self.axis_name}{transformations_nexus_paths.OFFSET}")
                )
            ] = self.offset
        if self.depends_on:
            res[
                join(
                    (
                        data_path,
                        f"{self.axis_name}{transformations_nexus_paths.DEPENDS_ON}",
                    )
                )
            ] = self.depends_on
        if self.equipment_component:
            res[
                join(
                    (
                        data_path,
                        f"{self.axis_name}{transformations_nexus_paths.EQUIPMENT_COMPONENT}",
                    )
                )
            ] = self.equipment_component
        return res

    @staticmethod
    def from_nx_dict(axis_name: str, dict_: dict, transformations_nexus_paths):
        if transformations_nexus_paths is None:
            _logger.warning(
                "no transformations_nexus_paths (not implemented on this version of nexus - too old)"
            )
            return None
        value = dict_.get(axis_name, None)
        # if this is a scalar store as an array move it back to an array
        if isinstance(value, numpy.ndarray) and value.ndim == 0:
            value = value[()]
        vector = dict_.get(f"{axis_name}{transformations_nexus_paths.VECTOR}", None)
        transformation_type = dict_.get(
            f"{axis_name}{transformations_nexus_paths.TRANSFORMATION_TYPE}", None
        )
        if vector is None or transformation_type is None:
            raise ValueError(
                "Unable to find mandatory vector and/or transformation_type"
            )

        transformation = Transformation(
            axis_name=axis_name,
            value=value,
            transformation_type=transformation_type,
            vector=vector,
        )

        units = dict_.get(f"{axis_name}@units", None) or dict_.get(
            "{axis_name}@unit", None
        )
        if units is not None:
            transformation.units = units

        offset = dict_.get(f"{axis_name}{transformations_nexus_paths.OFFSET}", None)
        if offset is not None:
            transformation.offset = offset

        depends_on = dict_.get(
            f"{axis_name}{transformations_nexus_paths.DEPENDS_ON}", None
        )
        if depends_on is not None:
            transformation.depends_on = depends_on

        equipment_component = dict_.get(
            f"{axis_name}{transformations_nexus_paths.EQUIPMENT_COMPONENT}", None
        )
        if equipment_component is not None:
            transformation.equipment_component = equipment_component

        return transformation

    def __setattr__(self, __name, __value):
        if self.__isfrozen and not hasattr(self, __name):
            raise AttributeError("can't set attribute", __name)
        else:
            super().__setattr__(__name, __value)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Transformation):
            return False
        else:
            if not (
                self.vector == __value.vector
                and self.transformation_type == __value.transformation_type
                and self.offset == __value.offset
                and self.depends_on == __value.depends_on
                and self.equipment_component == __value.equipment_component
            ):
                return False
            else:
                values_a, units_a = self.get_transformation_values_in_common_unit()
                values_b, units_b = __value.get_transformation_values_in_common_unit()
                if values_a is None or values_b is None:
                    return (values_a is values_b) and (units_a == units_b)
                elif units_a != units_b:
                    return False
                if isinstance(values_a, numpy.ndarray) and isinstance(
                    values_b, numpy.ndarray
                ):
                    return numpy.array_equal(values_a, values_b)
                else:
                    return values_a == values_b

    def as_matrix(self):
        # handle the transformation in detector space
        if self.transformation_values is None:
            raise ValueError(f"missing transformation values for {self}")
        elif numpy.isscalar(self.transformation_values):
            if self.transformation_type is TransformationType.ROTATION:
                if self.units in ("rad", "rads", "radian", "radians"):
                    theta = self.transformation_values
                elif self.units in ("deg", "degree", "degs", "degrees"):
                    theta = numpy.deg2rad(self.transformation_values)
                else:
                    raise ValueError(f"unknow unit: {self.units}")

                if self.offset != (0, 0, 0):
                    raise ValueError("offset not handled")

                if self.vector == (1, 0, 0):
                    return numpy.array(
                        [
                            [
                                1,
                                0,
                                0,
                            ],
                            [0, numpy.cos(theta), -numpy.sin(theta)],
                            [0, numpy.sin(theta), -numpy.cos(theta)],
                        ],
                        dtype=numpy.float32,
                    )
                elif self.vector == (0, 1, 0):
                    return numpy.array(
                        [
                            [numpy.cos(theta), 0, numpy.sin(theta)],
                            [0, 1, 0],
                            [-numpy.sin(theta), 0, numpy.cos(theta)],
                        ],
                        dtype=numpy.float32,
                    )
                elif self.vector == (0, 0, 1):
                    return numpy.array(
                        [
                            [numpy.cos(theta), -numpy.sin(theta), 0],
                            [numpy.sin(theta), numpy.cos(theta), 0],
                            [0, 0, 1],
                        ],
                        dtype=numpy.float32,
                    )
                else:
                    raise ValueError(f"vector {self.vector} not handled")
            elif self.transformation_type is TransformationType.TRANSLATION:
                if self.vector == (1, 0, 0):
                    return numpy.array(
                        [
                            [
                                self.transformation_values,
                                0,
                                0,
                            ],
                            [0, 1, 0],
                            [0, 0, 1],
                        ],
                        dtype=numpy.float32,
                    )
                elif self.vector == (0, 1, 0):
                    return numpy.array(
                        [
                            [1, 0, 0],
                            [0, self.transformation_values, 0],
                            [0, 0, 1],
                        ],
                        dtype=numpy.float32,
                    )
                elif self.vector == (0, 0, 1):
                    return numpy.array(
                        [
                            [1, 0, 0],
                            [0, 1, 0],
                            [0, 0, self.transformation_values],
                        ],
                        dtype=numpy.float32,
                    )
            else:
                raise RuntimeError(
                    f"unknow transformation type: {self.transformation_type}"
                )
        else:
            raise ValueError(
                f"transformations as a list of values is not handled for now ({self})"
            )

    def __str__(self):
        return f"transformation: {self.axis_name} -" + ", ".join(
            [
                f"type: {self.transformation_type.value}",
                f"value: {self.transformation_values}",
                f"vector: {self.vector}",
                f"offset: {self.offset}",
                f"depends_on: {self.depends_on}",
                f"equipment_component: {self.equipment_component}",
            ]
        )


class UDDetTransformation(Transformation):
    """
    convenient class to define a detector up-down flip if we consider the center of the detector to be at (0, 0)
    """

    def __init__(
        self,
        axis_name="ry",
        depends_on=None,
    ) -> None:
        super().__init__(
            axis_name=axis_name,
            value=180,
            transformation_type=TransformationType.ROTATION,
            vector=TransformationAxis.AXIS_Y,
            depends_on=depends_on,
        )


class LRDetTransformation(Transformation):
    """
    convenient class to define a detector left-right flip if we consider the center of the detector to be at (0, 0)
    """

    def __init__(
        self,
        axis_name="rz",
        depends_on=None,
    ) -> None:
        super().__init__(
            axis_name=axis_name,
            value=180,
            transformation_type=TransformationType.ROTATION,
            vector=TransformationAxis.AXIS_Z,
            depends_on=depends_on,
        )


class GravityTransformation(Transformation):
    """
    Gravity is used to solve transformation chain (as chain 'endpoint')
    """

    def __init__(self) -> None:
        super().__init__(
            axis_name="gravity",
            value=numpy.nan,
            transformation_type=TransformationType.TRANSLATION,
            vector=(0, 0, -1),
        )
        self.units = "m/s2"


def get_lr_flip(transformations: tuple) -> tuple:
    """
    check along all transformations if find Transformation matching 'LRTransformation'

    return a tuple with all matching keys
    """
    if not isinstance(transformations, (tuple, list)):
        raise TypeError(
            f"transformations is expected to be a tuple. {type(transformations)} provided"
        )
    res = []
    for transformation in transformations:
        if transformation == LRDetTransformation():
            res.append(transformation)
    return tuple(res)


def get_ud_flip(transformations: tuple) -> tuple:
    """
    check along all transformations if find Transformation matching 'UDTransformation'

    return a tuple with all matching keys
    """
    if not isinstance(transformations, (tuple, list)):
        raise TypeError(
            f"transformations is expected to be a tuple. {type(transformations)} provided"
        )
    res = []
    for transformation in transformations:
        if transformation == UDDetTransformation():
            res.append(transformation)
    return tuple(res)


def build_matrix(transformations: set):
    """
    build a matrice from a set of Transformation
    """
    transformations = {
        transformation.axis_name: transformation for transformation in transformations
    }
    already_applied_transformations = set(["gravity"])

    def handle_transformation(transformation: Transformation, matrix):
        if not isinstance(transformation, Transformation):
            raise TypeError(
                f"transformation is expected to be an instance of {Transformation}. {type(transformation)} provided"
            )

        # handle dependancies
        if transformation.axis_name in already_applied_transformations:
            # case already applied
            return matrix
        elif transformation.transformation_values is None:
            # case of the gravity matrix
            if transformation.axis_name.lower() == "gravity":
                return numpy.identity(3, dtype=numpy.float32)
            else:
                _logger.error(
                    f"transformation value not provided for {transformation.axis_name}. Ignore the transformation"
                )
                return matrix
        elif (
            transformation.depends_on is not None
            and transformation.depends_on not in already_applied_transformations
        ):
            if transformation.depends_on not in transformations:
                raise ValueError(
                    f"Unable to find transformation {transformation.depends_on}. Unable to build matrix. reason is: broken dependancy chain"
                )
            else:
                matrix = handle_transformation(
                    transformations[transformation.depends_on], matrix
                )
        matrix = numpy.matmul(matrix, transformation.as_matrix())
        already_applied_transformations.add(transformation.axis_name)
        return matrix

    matrix = numpy.identity(3, dtype=numpy.float32)
    for transformation in transformations.values():
        matrix = handle_transformation(transformation, matrix)

    return matrix
