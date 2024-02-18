import numpy
import pytest

from nxtomo.nxobject.nxsample import NXsample


def test_nx_sample():
    """test creation and saving of an nxsource"""
    nx_sample = NXsample()
    # check name
    with pytest.raises(TypeError):
        nx_sample.name = 12
    nx_sample.name = "my sample"

    # check rotation angle
    with pytest.raises(TypeError):
        nx_sample.rotation_angle = 56
    nx_sample.rotation_angle = numpy.linspace(0, 180, 180, endpoint=False)

    # check x translation
    with pytest.raises(TypeError):
        nx_sample.x_translation = 56
    nx_sample.x_translation = numpy.linspace(0, 180, 180, endpoint=False)

    # check y translation
    with pytest.raises(TypeError):
        nx_sample.y_translation = 56
    nx_sample.y_translation = [0.0] * 180

    # check z translation
    with pytest.raises(TypeError):
        nx_sample.x_translation = 56
    nx_sample.z_translation = None

    assert isinstance(nx_sample.to_nx_dict(), dict)

    # check we can't set undefined attributes
    with pytest.raises(AttributeError):
        nx_sample.test = 12

    # test concatenation
    nx_sample_concat = NXsample.concatenate([nx_sample, nx_sample])
    assert nx_sample_concat.name == "my sample"
    numpy.testing.assert_array_equal(
        nx_sample_concat.rotation_angle,
        numpy.concatenate(
            [
                numpy.linspace(0, 180, 180, endpoint=False),
                numpy.linspace(0, 180, 180, endpoint=False),
            ]
        ),
    )

    numpy.testing.assert_array_equal(
        nx_sample_concat.x_translation.value,
        numpy.concatenate(
            [
                numpy.linspace(0, 180, 180, endpoint=False),
                numpy.linspace(0, 180, 180, endpoint=False),
            ]
        ),
    )

    numpy.testing.assert_array_equal(
        nx_sample_concat.y_translation.value,
        numpy.concatenate(
            [
                numpy.asarray([0.0] * 180),
                numpy.asarray([0.0] * 180),
            ]
        ),
    )

    assert nx_sample_concat.z_translation.value is None
