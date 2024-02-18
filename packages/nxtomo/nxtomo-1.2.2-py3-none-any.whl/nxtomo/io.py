"""
some io utils to handle `nexus <https://manual.nexusformat.org/index.html>`_ and `hdf5 <https://www.hdfgroup.org/solutions/hdf5/>`_ with `h5py <https://www.h5py.org/>`_
"""

import logging
import os
from contextlib import contextmanager
import h5py._hl.selections as selection
from silx.io.url import DataUrl
from silx.io.h5py_utils import File as HDF5File

import h5py

_logger = logging.getLogger(__name__)


def check_virtual_sources_exist(fname, data_path):
    """
    Check that a virtual dataset points to actual data.

    :param str fname: HDF5 file path
    :param str data_path: Path within the HDF5 file

    :return bool res: Whether the virtual dataset points to actual data.
    """
    with HDF5File(fname, "r", swmr=True) as f:
        if data_path not in f:
            _logger.error(f"No dataset {data_path} in file {fname}")
            return False
        dptr = f[data_path]
        if not dptr.is_virtual:
            return True
        for vsource in dptr.virtual_sources():
            vsource_fname = os.path.join(
                os.path.dirname(dptr.file.filename), vsource.file_name
            )
            if not os.path.isfile(vsource_fname):
                _logger.error(f"No such file: {vsource_fname}")
                return False
            elif not check_virtual_sources_exist(vsource_fname, vsource.dset_name):
                _logger.error(f"Error with virtual source {vsource_fname}")
                return False
    return True


def from_data_url_to_virtual_source(url: DataUrl) -> tuple:
    """
    convert a DataUrl to a set (as tuple) of h5py.VirtualSource

    :param DataUrl url: url to be converted to a virtual source. It must target a 2D detector
    :return: (h5py.VirtualSource, tuple(shape of the virtual source), numpy.drype: type of the dataset associated with the virtual source)
    :rtype: tuple
    """
    if not isinstance(url, DataUrl):
        raise TypeError(
            f"url is expected to be an instance of DataUrl and not {type(url)}"
        )

    with HDF5File(url.file_path(), mode="r", swmr=True) as o_h5s:
        original_data_shape = o_h5s[url.data_path()].shape
        data_type = o_h5s[url.data_path()].dtype
        if len(original_data_shape) == 2:
            original_data_shape = (
                1,
                original_data_shape[0],
                original_data_shape[1],
            )

        vs_shape = original_data_shape
        if url.data_slice() is not None:
            vs_shape = (
                url.data_slice().stop - url.data_slice().start,
                original_data_shape[-2],
                original_data_shape[-1],
            )

    vs = h5py.VirtualSource(
        url.file_path(), url.data_path(), shape=vs_shape, dtype=data_type
    )

    if url.data_slice() is not None:
        vs.sel = selection.select(original_data_shape, url.data_slice())
    return vs, vs_shape, data_type


def from_virtual_source_to_data_url(vs: h5py.VirtualSource) -> DataUrl:
    """
    convert a h5py.VirtualSource to a DataUrl

    :param h5py.VirtualSource vs: virtual source to be converted to a DataUrl
    :return: url
    :rtype: DataUrl
    """
    if not isinstance(vs, h5py.VirtualSource):
        raise TypeError(
            f"vs is expected to be an instance of h5py.VirtualSorce and not {type(vs)}"
        )
    url = DataUrl(file_path=vs.path, data_path=vs.name, scheme="silx")
    return url


@contextmanager
def cwd_context(new_cwd=None):
    """
    create a context with 'new_cwd'.

    on entry update current working directory to 'new_cwd' and reset previous 'working_directory' at exit
    :param Optional[str] new_cwd: current working directory to use in the context
    """
    try:
        curdir = os.getcwd()
    except Exception as e:
        _logger.error(e)
        curdir = None
    try:
        if new_cwd is not None and os.path.isfile(new_cwd):
            new_cwd = os.path.dirname(new_cwd)
        if new_cwd not in (None, ""):
            os.chdir(new_cwd)
        yield
    finally:
        if curdir is not None:
            os.chdir(curdir)


def to_target_rel_path(file_path: str, target_path: str) -> str:
    """
    cast file_path to a relative path according to target_path.
    This is used to deduce h5py.VirtualSource path

    :param str file_path: file path to be moved to relative
    :param str target_path: target used as 'reference' to get relative path
    :return: relative path of file_path compared to target_path
    :rtype: str
    """
    file_path = os.path.abspath(file_path)
    target_path = os.path.abspath(target_path)
    path = os.path.relpath(file_path, os.path.dirname(target_path))
    if not path.startswith("./"):
        path = "./" + path
    return path
