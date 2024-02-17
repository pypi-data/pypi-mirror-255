"""
Some utility functions
"""

from __future__ import annotations
from importlib import import_module
from types import ModuleType

import numpy as np

from .probe import Probe


def import_safely(module: str) -> ModuleType:
    """
    Safely import a module with importlib and return the imported module object.

    Parameters
    ----------
    module : str
        The name of the module to import.

    Returns
    -------
    module_obj : module
        The imported module object.

    Raises
    ------
    ImportError
        If the specified module cannot be imported.

    Examples
    --------
    >>> import math
    >>> math_module = import_safely("math")
    >>> math_module.sqrt(4)
    2.0

    >>> import_safely("non_existent_module")
    ImportError: No module named 'non_existent_module'
    """

    try:
        module_obj = import_module(module)
    except ImportError as error:
        raise ImportError(f"{repr(error)}")

    return module_obj


def combine_probes(probes: list[Probe], connect_shape: bool = True) -> Probe:
    """
    Combine several Probe objects into a unique
    multi-shank Probe object.
    This works only when ndim=2

    This will have strange behavior if:
      * probes have been rotated
      * one of the probes has NOT been moved from its original location
        (results in probes overlapping in space )


    Parameters
    ----------
    probes : list
        List of Probe objects
    connect_shape : bool, default: True
        Connect all shapes together.
        Be careful, as this can lead to strange probe shape....

    Return
    ----------
    multi_shank : a multi-shank Probe object

    """

    # check ndim
    assert all(probes[0].ndim == p.ndim for p in probes), "all probes must have the same ndim"
    assert probes[0].ndim == 2, "All probes should be 2d"

    kwargs = {}
    for k in ("contact_positions", "contact_plane_axes", "contact_shapes", "contact_shape_params"):
        v = np.concatenate([getattr(p, k) for p in probes], axis=0)
        kwargs[k.replace("contact_", "")] = v

    shank_ids = np.concatenate([np.ones(p.get_contact_count(), dtype="int64") * i for i, p in enumerate(probes)])
    kwargs["shank_ids"] = shank_ids

    # TODO deal with contact_ids/device_channel_indices

    multi_shank = Probe(ndim=probes[0].ndim, si_units=probes[0].si_units)
    multi_shank.set_contacts(**kwargs)

    # global shape
    have_shape = all(p.probe_planar_contour is not None for p in probes)

    if have_shape and connect_shape:
        verts = np.concatenate([p.probe_planar_contour for p in probes], axis=0)
        verts = np.concatenate([verts[0:1] + [0, 40], verts, verts[-1:] + [0, 40]], axis=0)

        multi_shank.set_planar_contour(verts)

    return multi_shank


def generate_unique_ids(min: int, max: int, n: int, trials: int = 20) -> np.array:
    """
    Create n unique identifiers.
    Creates `n` unique integer identifiers between `min` and `max` within a
    maximum number of `trials` attempts.

    Parameters
    ----------
    min : int
        Minimun value permitted for an identifier
    max : int
        Maximum value permitted for an identifier
    n : int
        Number of identifiers to create
    trials : int, default: 20
        Maximal number of attempts for generating
        the set of identifiers

    Returns
    -------
    ids : A numpy array of `n` unique integer identifiers

    """

    ids = np.random.randint(min, max, n)
    i = 0

    while len(np.unique(ids)) != len(ids) and i < trials:
        ids = np.random.randint(min, max, n)

    if len(np.unique(ids)) != len(ids):
        raise ValueError(f"Can not generate {n} unique ids between {min} " f"and {max} in {trials} trials")
    return ids
