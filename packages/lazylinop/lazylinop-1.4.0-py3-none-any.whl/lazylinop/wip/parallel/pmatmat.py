"""
This module provides parallelized matmat (pmatmat) implementations.
"""
from lazylinop import isLazyLinearOp
from lazylinop.wip.parallel import pmatmat_multithread
from lazylinop.wip.parallel import pmatmat_multiprocess
from lazylinop.wip.parallel import pmatmat_mpi
from os import environ
from warnings import warn


def pmatmat(L, method='thread', nworkers=None, use_matvec=False, **kwargs):
    """
    Frontend function to build a :py:class:`.LazyLinearOp` parallelized version
    of ``L``. Precisely, ``L.matmat``/``__matmul__`` is parallelized according
    to the specified method.

    This function implements the parallelization of the product ``L @ A``
    proceeding alternatively as follows:

        1. (``use_matvec=False``) Assign evenly blocks of columns of ``A`` to
        workers in order to compute the product by blocks in parallel using
        ``L`` pre-defined ``matmat``.

        2. (``use_matvec=True``) Define a parallelized ``matmat`` using ``L``'s
        pre-defined ``matvec``.
        Each worker makes a series of sequential calls to ``matvec`` in
        parallel to other workers. The ``matvec`` calls are made on ``A``
        columns assigned to the worker as in 1.

    .. Warning:: Using the method 1 or 2 does not go without consequence on the
        computing performance. In most cases method 1 should be more efficient.
        This is the default method (``use_matvec=False``).

    Args:
        L: (:py:class:`.LazyLinearOp`)
            The operator to parallelize.
        method: (str)
            - 'thread': see :py:func:`.pmatmat_multithread`
            - 'process': see :py:func:`.pmatmat_multiprocess`
            - 'mpi': see :py:func:`.pmatmat_mpi`
        nworkers: (int)
            The number of workers used for parallelization.
            Defaulty, the number of CPUs available on the system.
            This parameter is ignored for 'mpi' method (it is fixed externally
            by the ``mpiexec``/``mpirun`` command).
        use_matvec: (bool)
            If ``True`` the ``matvec`` function of ``L`` is used for
            parallelization otherwise only ``matmat`` is used.
        **kwargs: (unpacked dict)
            Specialized arguments corresponding to the method used.

    .. Warning:: For using ``pmatmat`` efficiently (i.e. without
        oversubscribing), the multithreading of underlying libraries
        should be disabled. Setting for example ``OMP_NUM_THREADS``,
        ``MKL_NUM_THREADS`` or ``OPENBLAS_NUM_THREADS`` environment
        variables to '1' (it must notably be done before importing
        numpy or other underlying library in start of your script). The
        variables to set depend on the :py:class:`.LazyLinearOp`
        ``matmat``/``matvec`` being parallelized. In any doubt, all
        variables can be set to '1'. An alternative to environment variables
        is to use the `threadpoolctl
        <https://pypi.org/project/threadpoolctl/>`_ library.

    Returns:
        A specialized :py:class:`.LazyLinearOp` that is able to compute the
        product ``L @ A`` in parallel according to the chosen method.


    Example:
        >>> # disable OpenMP before all things
        >>> from os import environ
        >>> environ['OMP_NUM_THREADS'] = '1'
        >>> environ['MKL_NUM_THREADS'] = '1'
        >>> environ['OPENBLAS_NUM_THREADS'] = '1'
        >>> from lazylinop import aslazylinearoperator
        >>> from lazylinop.wip.parallel import pmatmat
        >>> shape = (15, 20)
        >>> import numpy as np
        >>> M = np.random.rand(*shape)
        >>> A = np.random.rand(shape[1], 32)
        >>> L = aslazylinearoperator(M)
        >>> pL = pmatmat(L)
        >>> # pL matmat is parallelized using default thread method
        >>> LA = L @ A # seqential mul
        >>> pLA = pL @ A # parallel mul
        >>> np.allclose(pLA, LA)
        True
        >>> np.allclose(pLA, M @ A)
        True

    """
    if ('MKL_NUM_THREADS' not in environ or
            'OPENBLAS_NUM_THREADS' not in environ or
            'OMP_NUM_THREADS' not in environ):
        warn('You should disable numpy multithreading when using pmatmat; use'
             ' environment variables MKL_NUM_THREADS, OPENBLAS_NUM_THREADS and'
             ' maybe OPENM_NUM_THREADS. Set their values to 1.')
    if not isLazyLinearOp(L):
        raise TypeError('L must be a LazyLinearOp')
    method = method.lower()
    if method == 'thread':
        pL = pmatmat_multithread(L, nworkers=nworkers, use_matvec=use_matvec,
                                 **kwargs)
    elif method == 'process':
        pL = pmatmat_multiprocess(L, nworkers=nworkers, use_matvec=use_matvec,
                                  **kwargs)
    elif method == 'mpi':
        # nworkers is set externally with MPI command
        pL = pmatmat_mpi(L, use_matvec=use_matvec, **kwargs)
    else:
        raise ValueError('Unsupported method')
    return pL
