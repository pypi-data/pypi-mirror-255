/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


// =======
// Headers
// =======

#include "./c_get_config.h"


// ===============
// is use symmetry 
// ===============

/// \brief Returns USE_SYMMETRY.
///

FlagType is_use_symmetry()
{
    if (USE_SYMMETRY == 1)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}


// =============
// is use openmp
// =============

/// \brief Returns USE_OPENMP.
///

FlagType is_use_openmp()
{
    if (USE_OPENMP == 1)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}


// =============
// is count perf
// =============

/// \brief Returns COUNT_PERF.
///

FlagType is_count_perf()
{
    if (COUNT_PERF == 1)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}


// ==============
// is chunk tasks
// ==============

/// \brief Returns CHUNK_TASKS.
///

FlagType is_chunk_tasks()
{
    if (CHUNK_TASKS == 1)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}
