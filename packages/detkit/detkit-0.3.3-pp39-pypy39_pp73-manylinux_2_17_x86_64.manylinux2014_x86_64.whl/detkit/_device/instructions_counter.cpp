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

#include "./instructions_counter.h"
#include <string.h>
#include <iostream>

#if __linux__
    #include <asm/unistd.h>
    #include <sys/ioctl.h>
    #include <unistd.h>
    #include <inttypes.h>
    #include <sys/types.h>
#endif


// ===============
// perf event open
// ===============

#if __linux__
    static long perf_event_open(
            struct perf_event_attr* hw_event,
            pid_t pid,
            int cpu,
            int group_fd,
            unsigned long flags)
    {
        int ret;
        ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd,
                      flags);
        return ret;
    }
#endif


// ===========
// Constructor
// ===========

InstructionsCounter::InstructionsCounter():
    fd(-1),
    count(0)
{
    #if __linux__
        memset(&this->pe, 0, sizeof(struct perf_event_attr));
        this->pe.type = PERF_TYPE_HARDWARE;
        this->pe.size = sizeof(struct perf_event_attr);
        this->pe.config = PERF_COUNT_HW_INSTRUCTIONS;
        this->pe.disabled = 1;
        this->pe.exclude_kernel = 1;
        this->pe.exclude_hv = 1;  // Don't count hypervisor events.

        this->fd = perf_event_open(&this->pe, 0, -1, -1, 0);
        if (this->fd == -1)
        {
            // Error, cannot open the leader.
            this->count = -1;
        }
    #endif
}


// ==========
// Destructor
// ==========

InstructionsCounter::~InstructionsCounter()
{
    #if __linux__
        if (this->fd != -1)
        {
            close(this->fd);
        }
    #endif
}


// =====
// Start
// =====

void InstructionsCounter::start()
{
    #if __linux__
        if (this->fd != -1)
        {
            ioctl(this->fd, PERF_EVENT_IOC_RESET, 0);
            ioctl(this->fd, PERF_EVENT_IOC_ENABLE, 0);
        }
    #endif
}


// ====
// Stop
// ====

void InstructionsCounter::stop()
{
    #if __linux__
        if (this->fd != -1)
        {
            ioctl(this->fd, PERF_EVENT_IOC_DISABLE, 0);
            read(this->fd, &this->count, sizeof(long long));
        }
    #endif
}


// =========
// get count
// =========

long long InstructionsCounter::get_count()
{
    return this->count;
}
