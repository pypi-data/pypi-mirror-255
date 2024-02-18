"""general utils"""

from typing import Iterable
import h5py
import numpy
from silx.io.utils import h5py_read_dataset

from nxtomo.io import HDF5File


def cast_and_check_array_1D(array, array_name: str):
    """
    cast provided array to 1D

    :param array: array to be cast to 1D
    :param str array_name: name of the array - used for log only
    """
    if not isinstance(array, (type(None), numpy.ndarray, Iterable)):
        raise TypeError(
            f"{array_name} is expected to be None, or an Iterable. Not {type(array)}"
        )
    if array is not None and not isinstance(array, numpy.ndarray):
        array = numpy.asarray(array)
    if array is not None and array.ndim > 1:
        raise ValueError(f"{array_name} is expected to be 0 or 1d not {array.ndim}")
    return array


def get_data_and_unit(file_path: str, data_path: str, default_unit):
    """
    return for an HDF5 dataset his value and his unit. If unit cannot be found then fallback on the 'default_unit'

    :param str file_path: file path location of the HDF5Dataset to read
    :param str data_path: data_path location of the HDF5Dataset to read
    :param default_unit: default unit to fall back if the dataset has no 'unit' or 'units' attribute
    """
    with HDF5File(file_path, mode="r", swmr=True) as h5f:
        if data_path in h5f and isinstance(h5f[data_path], h5py.Dataset):
            dataset = h5f[data_path]
            unit = None
            if "unit" in dataset.attrs:
                unit = dataset.attrs["unit"]
            elif "units" in dataset.attrs:
                unit = dataset.attrs["units"]
            else:
                unit = default_unit
            if hasattr(unit, "decode"):
                # handle Diamond dataset
                unit = unit.decode()
            return h5py_read_dataset(dataset), unit
        else:
            return None, default_unit


def get_data(file_path: str, data_path: str):
    """
    proxy to h5py_read_dataset, handling use case 'data_path' not present in the file.
    In this case return None

    :param str file_path: file path location of the HDF5Dataset to read
    :param str data_path: data_path location of the HDF5Dataset to read
    """
    with HDF5File(file_path, mode="r", swmr=True) as h5f:
        if data_path in h5f:
            return h5py_read_dataset(h5f[data_path])
        else:
            return None
