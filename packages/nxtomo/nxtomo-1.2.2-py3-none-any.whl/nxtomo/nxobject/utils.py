"""
utils for NXobject
"""

from typing import Iterable
from nxtomo.nxobject.nxobject import NXobject


def concatenate(nx_objects: Iterable, **kwargs) -> NXobject:
    """
    concatenate a list of NXobjects

    :param Iterable nx_objects: objects to be concatenated. They are expected to be of the same type.
    :param kwargs: extra parameters
    :return: concatenated object. Of the same type of 'nx_objects'
    :rtype: :class:`~nxtomo.nxobject.nxobject.NXobject`
    """
    if len(nx_objects) == 0:
        return None
    else:
        if not isinstance(nx_objects[0], NXobject):
            raise TypeError("nx_objects are expected to be instances of NXobject")
        return type(nx_objects[0]).concatenate(nx_objects=nx_objects, **kwargs)
