/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _DEFINITIONS_C_GET_CONFIG_H_
#define _DEFINITIONS_C_GET_CONFIG_H_


// =======
// Headers
// =======

#include "./types.h"  // FlagType


// ============
// Declarations
// ============

FlagType is_use_symmetry();
FlagType is_use_openmp();
FlagType is_count_perf();
FlagType is_chunk_tasks();


#endif  // _DEFINITIONS_C_GET_CONFIG_H_
