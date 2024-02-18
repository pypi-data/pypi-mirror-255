.. _dependencies:

Runtime Dependencies
====================

The followings are dependencies used during the runtime of |project|. Note that, among these dependencies, `OpenMP` is **required**, while the rest of the dependencies are optional.

.. _dependencies_openmp:

OpenMP (`Required`)
-------------------

|project| requires OpenMP, which is typically included with most C++ compilers.

.. glossary::

    For **Linux** users:

        By installing a C++ compiler such as GCC, Clang, or Intel, you also obtain OpenMP as well. You may alternatively install ``libgomp`` (see below) without the need to install a full compiler.

    For **macOS** users:

        It's crucial to note that OpenMP is not part of the default Apple Xcode's LLVM compiler. Even if you have Apple Xcode LLVM compiler readily installed on macOS, you will still need to install OpenMP separately via ``libomp`` Homebrew package (see below) or as part of the *open source* `LLVM compiler <https://llvm.org/>`__, via ``llvm`` Homebrew package.

    For **Windows** users:

        OpenMP support depends on the compiler you choose; Microsoft Visual C++ supports OpenMP, but you may need to enable it explicitly.

Below are the specific installation for each operating system:

.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt install libgomp1 -y

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum install libgomp -y

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf install libgomp -y

    .. tab-item:: macOS
        :sync: osx

        .. prompt:: bash

            sudo brew install libomp

.. note::

    In *macOS*, for ``libomp`` versions ``15`` and above, Homebrew installs OpenMP as *keg-only*. To utilize the OpenMP installation, you should establish the following symbolic links:

    .. prompt:: bash

        libomp_dir=$(brew --prefix libomp)
        ln -sf ${libomp_dir}/include/omp-tools.h  /usr/local/include/omp-tools.h
        ln -sf ${libomp_dir}/include/omp.h        /usr/local/include/omp.h
        ln -sf ${libomp_dir}/include/ompt.h       /usr/local/include/ompt.h
        ln -sf ${libomp_dir}/lib/libomp.a         /usr/local/lib/libomp.a
        ln -sf ${libomp_dir}/lib/libomp.dylib     /usr/local/lib/libomp.dylib

Perf Tool (`Optional`)
----------------------

|project| can count the FLOPs of the computations, if the argument ``flops=True`` is used in the functions (see :ref:`API Reference <api>`). To this end, the `Linux Performance Counter tool <https://perf.wiki.kernel.org/index.php/Main_Page>`_, known as ``perf`` should be installed.

.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt-get install linux-tools-common linux-tools-generic linux-tools-`uname -r`

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum group install perf

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf group install perf

.. attention::

    The ``perf`` tool is not available in macOS and Windows.

Grant permissions to the user to be able to run the perf tool:

.. prompt:: bash

    sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
    
Test if the `perf` tool works by

.. prompt::

    perf stat -e instructions:u dd if=/dev/zero of=/dev/null count=100000

Alternatively, you may also test `perf` tool with |project| by

.. code-block:: python

    >>> import detkit
    >>> detkit..get_instructions_per_task()

If the installed `perf` tool is configured properly, the output of either of the above commands should not be empty.
