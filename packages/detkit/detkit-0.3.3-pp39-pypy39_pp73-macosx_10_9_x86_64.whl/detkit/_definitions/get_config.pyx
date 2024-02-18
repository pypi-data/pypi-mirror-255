# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

from .c_get_config cimport is_use_symmetry, is_use_openmp, is_count_perf, \
        is_chunk_tasks


# ==========
# get config
# ==========

def get_config():
    """
    Returns the definitions used in the compile-time of the package.

    Returns
    -------

    config : dict
        A dictionary of the definitions used in the compile-time with the
        following fields:

        * ``'use_symmetry'``: boolean, determines whether the Gramian
          matrices are computed using symmetric matrix multiplication (when
          `True`), or using the full matrix multiplication (when `False`).
        * ``'use_openmp'``: boolean, determines whether to use OpenMP
          parallelism.
        * ``'count_perf'``: boolean, determines whether to count hardware
          instructions during the runtime.
        * ``'chunk_tasks'``: boolean, chunks the multiply-add (MA) operations,
          similar to a technique used for instance in BLAS library. When
          `True`, every five MA operations are computed in the same chunk.

    See Also
    --------

    detkit.get_instructions_per_task

    Notes
    -----

    To configure the compile-time definitions, modify the
    ``/detkit/_definitions/definitions.h`` file and recompile the package.

    Examples
    --------

    .. code-block:: python

        >>> import detkit
        >>> detkit.get_config()
        {
            'use_symmetry': True,
            'use_openmp': False,
            'count_perf': True,
            'chunk_tasks': True
        }

    The above configuration shows the package was compiled where the symmetric
    matrix multiplication for Gram matrices is enabled, the package supports
    parallelism on shared memory with OpenMP, it can count hardware
    instructions at the runtime, and chunks multiply-add operations to
    improve performance.
    """

    config = {
        'use_symmetry': bool(is_use_symmetry()),
        'use_openmp': bool(is_use_openmp()),
        'count_perf': bool(is_count_perf()),
        'chunk_tasks': bool(is_chunk_tasks()),
    }

    return config
