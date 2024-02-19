from lazylinop import LazyLinearOp, binary_dtype
from multiprocessing import cpu_count, Process, Queue
from .pmatmat_thread import _share_work
import numpy as np


def pmatmat_multiprocess(L, nworkers=None, use_matvec=False,
                         procs_created_once=False):
    """
    Implements :py:func:`.pmatmat` using Python `multiprocessing
    <https://docs.python.org/3/library/multiprocessing.html>`_.

    Args:
        L:
            see :py:func:`.pmatmat`
        nworkers:
            see :py:func:`.pmatmat`
        use_matvec:
            see :py:func:`.pmatmat`
        procs_created_once: (bool)
            If ``True`` processes are created beforehand and then
            consume/compute multiplications on the fly.
            Otherwise (``False``) processes are created each time a
            multiplication is calculated.  ``procs_created_once=True``
            hardly outperforms ``False`` case because it needs to make
            IPC (Inter-Process Communication) to send slices of ``A``
            (if we compute ``L @ A``) to processes created
            beforehand. In case of ``procs_created_once=False`` ``A`` is
            auto-shared by process forking (without any copy) but the resulting
            slices of multiplication still imply a need for IPC.
    """
    if procs_created_once:
        return PMCreatedOnceProcessLazyLinearOp(L, nworkers,
                                                use_matvec=use_matvec)
    else:
        return PMProcessLazyLinearOp(L, nworkers, use_matvec=use_matvec)


class PMProcessLazyLinearOp(LazyLinearOp):
    """
    TODO
    """

    def __init__(self, L, nworkers=None, use_matvec=False):
        """
            It can parallelize proceeding alternatively as follows:
                1. Parallelize a pre-defined matmat per blocks of columns.
                2. Define a parallelized matmat using a pre-defined matvec.

            .. Warning:: Using the method 1 or 2 does not go without
            consequence on the computing performance. In most cases
            method 1 should be more efficient.

            Python Process-es (multiprocessing package) are used for
            parallelization.

        """
        self.L = L
        super().__init__(L.shape,
                         matmat=lambda X:
                         pmatmat_process(L, X, nworkers,
                                         use_matvec=use_matvec),
                         dtype=L.dtype)

    def terminate(self):
        # just for compatibility with PMCreatedOnceProcessLazyLinearOp
        # (TODO: it should be made by class inheritance).
        pass


def matmat_block(L, A, q, offset):
    out = np.empty((L.shape[0], A.shape[1]), dtype=binary_dtype(L.dtype,
                                                                A.dtype))
    for j in range(A.shape[1]):
        out[:, j] = L @ A[:, j]
    q.put([out, offset])


def matmat_matvec(L, A, q, offset):
    out = L @ A
    q.put([out, offset])


def select_matmat_func(use_matvec=False):
    if use_matvec:
        return matmat_matvec
    else:
        return matmat_block


def pmatmat_process(L, A, nprocs=None, use_matvec=False):
    matmat = select_matmat_func(use_matvec=use_matvec)
    if nprocs is None:
        nprocs = cpu_count()
    nprocs = min(nprocs, cpu_count())
    out = np.empty((L.shape[0], A.shape[1]), dtype=binary_dtype(L.dtype,
                                                                A.dtype))
    w_offsets, w_njobs = _share_work(nprocs, A.shape[1])
    procs = [0 for _ in range(nprocs)]
    q = Queue()
    for i in range(nprocs):
        start = w_offsets[i]
        end = start + w_njobs[i]
        procs[i] = Process(target=matmat, args=(L, A[:, start:end], q, start))
        procs[i].start()
    for i in range(nprocs):
        LA_slice = q.get()
        offset = LA_slice[1]
        slice_len = LA_slice[0].shape[1]
        out[:, offset:offset+slice_len] = LA_slice[0]
    return out


class PMCreatedOnceProcessLazyLinearOp(LazyLinearOp):
    """
    Same as PMProcessLazyLinearOp but processes created once and for all
    (waiting for new multiplications to compute).
    It follows then model Producer-consumer on each matmat request.
    """

    def __init__(self, L, nworkers=None, use_matvec=False):
        self.L = L
        if nworkers is None:
            nworkers = cpu_count()
        nworkers = min(nworkers, cpu_count())
        procs = [0 for _ in range(nworkers)]
        q_in = Queue()
        q_out = Queue()
        self.procs = procs
        self.q_in = q_in
        self.q_out = q_out
        for i in range(nworkers):
            procs[i] = Process(target=process_consume, args=(L, q_in, q_out,
                                                             use_matvec))
            procs[i].start()
        super().__init__(L.shape,
                         matmat=lambda X:
                         process_producer(L, X, procs, q_in, q_out),
                         dtype=L.dtype)

    def __del__(self):
        self.terminate()

    def terminate(self):
        for p in self.procs:
            p.terminate()


def process_producer(L, A, procs, q_in, q_out):
    nprocs = len(procs)
    out = np.empty((L.shape[0], A.shape[1]), dtype=binary_dtype(L.dtype,
                                                                A.dtype))
    w_offsets, w_njobs = _share_work(nprocs, A.shape[1])
    for i in range(nprocs):
        start = w_offsets[i]
        end = start + w_njobs[i]
        q_in.put([A[:, start:end], start])
    for i in range(nprocs):
        LA_slice = q_out.get()
        offset = LA_slice[1]
        slice_len = LA_slice[0].shape[1]
        out[:, offset:offset+slice_len] = LA_slice[0]
    return out


def process_consume(L, q_in, q_out, use_matvec):
    matmat = select_matmat_func(use_matvec=use_matvec)
    while mm_info := q_in.get():
        A, offset = mm_info
        matmat(L, A, q_out, offset)
