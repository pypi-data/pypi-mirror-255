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

from .._definitions.types cimport FlagType


# =======
# Externs
# =======

cdef extern from "c_get_config.h":

    cdef FlagType is_use_symmetry() nogil
    cdef FlagType is_use_openmp() nogil
    cdef FlagType is_count_perf() nogil
    cdef FlagType is_chunk_tasks() nogil
