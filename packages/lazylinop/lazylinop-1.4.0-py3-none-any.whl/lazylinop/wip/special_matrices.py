"""
Module for special matrices related LazyLinearOps.
"""
from warnings import warn
try:
    import dask
    from dask.distributed import Client, LocalCluster, wait
except ImportError:
    warn("Dask ImportError") # warn better than a print (ignored by doctest)
from lazylinop import *
try:
    import numba as nb
    from numba import njit, prange, set_num_threads, threading_layer
    nb.config.THREADING_LAYER = 'omp'
    _T = nb.config.NUMBA_NUM_THREADS
except ImportError:
    print('Did not find Numba.')
import numpy as np
import scipy as sp
import warnings
warnings.simplefilter(action='always')


@njit(parallel=False, cache=True)
def mm(A: np.ndarray, B: np.ndarray, M: int, K: int, N: int, swap_kn: bool=False):
    C = np.full(M * N, 0 * (A[0] * B[0]))
    if swap_kn:
        for m in range(M):
            for k in range(K):
                for n in range(N):
                    C[m * N + n] += A[m * K + k] * B[k * N + n]
    else:
        for m in range(M):
            for n in range(N):
                tmp = 0.0
                for k in range(K):
                    tmp += A[m * K + k] * B[k * N + n]
                C[m * N + n] = tmp
    return C


def alternant(x, f: list, use_numba: bool=False):
    r"""Constructs alternant matrix as a lazy linear operator A.
    The shape of the alternant lazy linear operator is (x.shape[0], len(f)).

    .. math::
        A = \begin{pmatrix}
        f_0(x_0) & f_1(x_0) & ... & f_n(x_0)\\
        f_0(x_1) & f_1(x_1) & ... & f_n(x_1)\\
        f_0(x_2) & f_1(x_2) & ... & f_n(x_2)\\
            .    &    .     &     &    .    \\
            .    &    .     &     &    .    \\
            .    &    .     &     &    .    \\
            .    &    .     &     &    .    \\
        f_0(x_m) & f_1(x_m) & ... & f_n(x_m)\\
        \end{pmatrix}

    Args:
        x: 1d array
            Array of points
        f: list
            A list of lambda functions.
        use_numba: bool, optional
            If True, use prange from Numba (default is False)
            to compute batch in parallel.
            It is useful only and only if the batch size and
            the length of a are big enough.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            f expects at least one element.
        ValueError
            x expects 1d-array.

    Examples:
        >>> import numpy as np
        >>> import scipy as sp
        >>> from lazylinop.wip.special_matrices import alternant
        >>> M = 5
        >>> N = 6
        >>> x = np.random.rand(M)
        >>> f = [lambda x, n=n: np.power(x, n) for n in range(N)]
        >>> X = np.random.rand(N, 3)
        >>> np.allclose(alternant(x, f) @ X, np.vander(x, N=N, increasing=True) @ X)
        True

    References:
        See also `Alternant matrix <https://en.wikipedia.org/wiki/Alternant_matrix>`_.
    """
    if len(f) < 1:
        raise ValueError("f expects at least one element.")

    if x.ndim != 1:
        raise ValueError("x expects 1d-array.")

    M, N = x.shape[0], len(f)

    def _matmat(x, f, X, adjoint):

        def _1d(x, f, X, adjoint):
            if X.ndim != 1:
                raise Exception("batch size must be equal to 1.")            
            y = np.empty(
                N if adjoint else M,
                dtype=np.complex_ if x.dtype.kind == 'c' or X.dtype.kind == 'c' else (x[0] * X[0]).dtype
            )
            if adjoint:
                # conjugate and transpose
                for i in range(N):
                    y[i] = np.array([f[i](x[j]) for j in range(M)]) @ X
            else:
                for i in range(M):
                    y[i] = np.array([f[j](x[i]) for j in range(N)]) @ X
            return y

        nb.config.DISABLE_JIT = 0 if use_numba else 1
        @njit(parallel=True, cache=True)
        def _2d(x, f, X, adjoint):
            if X.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = X.shape[1]
            y = np.empty(
                (N if adjoint else M, batch_size),
                dtype=np.complex_ if x.dtype.kind == 'c' or X.dtype.kind == 'c' else (x[0] * X[0, 0]).dtype
            )
            if adjoint:
                # conjugate and transpose
                for b in prange(batch_size):
                    for i in range(N):
                        y[i, b] = np.array([f[i](x[j]) for j in range(M)]) @ X[:, b]
            else:
                for b in prange(batch_size):
                    for i in range(M):
                        y[i, b] = np.array([f[j](x[i]) for j in range(N)]) @ X[:, b]
            return y

        return _1d(x, f, X, adjoint) if X.ndim == 1 else _2d(x, f, X, adjoint)

    return LazyLinearOp(
        shape=(M, N),
        matmat=lambda X: _matmat(x, f, X, False),
        rmatmat=lambda X: _matmat(x, f, X, True)
    )


def companion(a):
    """Constructs a companion matrix as a lazy linear operator C.

    Args:
        a: np.ndarray
        1d array of polynomial coefficients (N, ).

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            a expects a 1d array.
        ValueError
            # of coefficients must be at least >= 2.
        ValueError
            The first coefficient a[0] must be != 0.0.

    References:
        See also `scipy.linalg.companion <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.companion.html>`_.
        See also `Companion matrix <https://en.wikipedia.org/wiki/Companion_matrix>`_.
    """
    if a.ndim != 1:
        raise ValueError("a expects a 1d array.")
    if a.shape[0] < 2:
        raise ValueError("# of coefficients must be at least >= 2.")
    if a[0] == 0.0:
        raise ValueError("The first coefficient a[0] must be != 0.")

    def _matmat(a, x, H):
        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            batch_size = 1
            is_1d = True
        else:
            batch_size = x.shape[1]
            is_1d = False
        N = a.shape[0]
        if 'complex' in a.dtype.str:
            y = np.empty((N - 1, batch_size), dtype=np.complex_)
        else:
            y = np.empty((N - 1, batch_size), dtype=(a[0] * x[0]).dtype)
        if H:
            # conjugate and transpose
            for b in range(batch_size):
                y[:, b] = np.divide(np.multiply(a[1: ], x[0, b]), -a[0])
                np.add(y[:(N - 2), b], x[1:(N - 1), b], out=y[:(N - 2), b])
        else:
            for b in range(batch_size):
                y[0, b] = np.divide(a[1:], -a[0]) @ x[:, b]
                y[1:(N - 1), b] = x[:(N - 2), b]
        return y.ravel() if is_1d else y

    return LazyLinearOp(
        shape=(a.shape[0] - 1, a.shape[0] - 1),
        matmat=lambda x: _matmat(a, x, False),
        rmatmat=lambda x: _matmat(a, x, True)
    )


def fiedler(a: np.ndarray, use_numba: bool=False):
    """Constructs a symmetric Fiedler matrix as a lazy linear operator F.
    A symmetric Fiedler matrix has entry F[i, j] = np.absolute(a[i] - a[j]).

    Args:
        a: np.ndarray
            Sequence of numbers (shape is (n, )).
        use_numba: bool, optional
            If True, use prange from Numba (default is False)
            to compute batch in parallel.
            It is useful only and only if the batch size and
            the length of a are big enough.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            a is empty.

    References:
        See also `scipy.linalg.fiedler <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.fiedler.html>`_.
        See also `Wikipedia <https://en.wikipedia.org/wiki/Algebraic_connectivity>`_.
    """
    if a.shape[0] == 0:
        raise ValueError("a is empty.")

    def _matmat(a, x):

        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            is_1d = True
        else:
            is_1d = False
        batch_size = x.shape[1]

        @njit(parallel=not is_1d, cache=True)
        def _bf(a, x):
            N = a.shape[0]
            __T = max(2, _T // 2)
            tmp_acc = np.full(__T, 0.0 * (a[0] * x[0, 0]))
            ai = np.full(__T, 0.0 * a[0])
            y = np.full((N, batch_size), 0.0 * (a[0] * x[0, 0]))
            BperT = int(np.ceil(batch_size / __T))
            # Run in parallel thanks to Numba prange
            for t in prange(__T):
                for b in range(t * BperT, min(batch_size, (t + 1) * BperT), 1):
                    for i in range(N):
                        tmp_acc[t] = 0.0
                        ai[t] = a[i]
                        # (L + D + U) @ x where U = L^T
                        # L is a lower triangular matrix such that L[i, i] = 0
                        # and D is a diagonal matrix such that D[i, i] = 0.
                        # L @ x + (x^T @ L)^T
                        for j in range(N):
                            tmp_acc[t] += np.absolute(ai[t] - a[j]) * x[j, b]
                        y[i, b] = tmp_acc[t]
            return y.ravel() if is_1d else y

        def _no_bf(a, x):
            N = a.shape[0]
            y = np.full((N, batch_size), 0 * (a[0] * x[0, 0]))
            for i in range(N):
                # (L + D + U) @ x where U = L^T
                # L is a lower triangular matrix such that L[i, i] = 0
                # and D is a diagonal matrix such that D[i, i] = 0.
                # L @ x + (x^T @ L)^T
                if i < (N - 1):
                    y[i, :] += np.absolute(np.subtract(a[i], a[(i + 1):])) @ x[(i + 1):, :]
                if i > 0:
                    y[i, :] += np.absolute(np.subtract(a[i], a[:i])) @ x[:i, :]
            return y.ravel() if is_1d else y

        return _bf(a, x) if use_numba else _no_bf(a, x)

    return LazyLinearOp(
        shape=(a.shape[0], a.shape[0]),
        matmat=lambda x: _matmat(a, x),
        rmatmat=lambda x: _matmat(a, x)
    )


def helmert(n: int, full: bool=False, use_numba: bool=False):
    r"""Constructs a Helmert matrix n x n as a lazy linear operator H.

    .. math::
        \begin{pmatrix}
        1/\sqrt{n} & 1/\sqrt{n} & 1/\sqrt{n} & ... & 1/\sqrt{n}\\
        1/\sqrt{2} & -1/\sqrt{2} & 0 & ... & 0\\
        1/\sqrt{6} & 1/\sqrt{6} & 2/\sqrt{6} & ... & 0\\
        . & . & . & ... & 0\\
        1/\sqrt{n(n-1)} & 1/\sqrt{n(n-1)} & 1/\sqrt{n(n-1)} & ... & -(n-1)/\sqrt{n(n-1)}\\
        \end{pmatrix}
    
    Args:
        n: int
            The size of the matrix (n, n).
        full: bool, optional
            If False (default) do not return the first row H[1:, :] @ x.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n must be >= 2.

    Examples:
        >>> from lazylinop.wip.special_matrices import helmert
        >>> import numpy as np
        >>> import scipy as sp
        >>> N = 100
        >>> X = np.random.rand(N, 10)
        >>> H = helmert(N)
        >>> np.allclose(H @ X, sp.linalg.helmert(N) @ X)
        True

    References:
        See also `scipy.linalg.helmert <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.helmert.html>`_.
        See also `R-project Helmert matrix <https://search.r-project.org/CRAN/refmans/fastmatrix/html/helmert.html>`_.
    """
    if n < 2:
        raise ValueError("n must be >= 2.")

    nb.config.DISABLE_JIT = 0 if use_numba else 1

    def _matmat(n, full, x, H):
        def _1d(n, full, x, H):
            if x.ndim != 1:
                raise Exception("batch size must be equal to 1.")
            offset = 0 if full else 1
            invsqrtn = 1.0 / np.sqrt(n)
            if H:
                # transpose and conjugate
                # if full skip the first row
                if full:
                    y = np.multiply(np.full(n, invsqrtn), x[0])
                else:
                    y = np.zeros(n, dtype=x.dtype)    
                for i in range(1, n):
                    invsqrt = 1.0 / np.sqrt((i + 1) * i)
                    y[:i] += np.multiply(np.full(i, invsqrt), x[i - offset])
                    y[i] -= x[i - offset] * (i * invsqrt)
            else:
                y = np.empty((n - offset), dtype=x.dtype)
                # if full skip the first row
                if full:
                    y[0] = np.full(n, invsqrtn) @ x
                for i in range(1, n):
                    invsqrt = 1.0 / np.sqrt((i + 1) * i)
                    y[i - offset] = np.sum(invsqrt * x[:i], axis=0) - x[i] * (i * invsqrt)
            return y

        def _2d(n, full, x, H):
            if x.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = x.shape[1]
            offset = 0 if full else 1
            invsqrtn = 1.0 / np.sqrt(n)

            def _no_bf(n, full, x, H):
                if H:
                    # transpose and conjugate
                    y = np.zeros((n, batch_size), dtype=x.dtype)
                    # if full skip the first row
                    if full:
                        y[:, :] = np.multiply(invsqrtn, x[0, :])
                    for i in range(1, n):
                        invsqrt = 1.0 / np.sqrt((i + 1) * i)
                        y[:i, :] += np.multiply(invsqrt, x[i - offset, :])
                        y[i, :] -= x[i - offset, :] * (i * invsqrt)
                else:
                    y = np.empty((n - offset, batch_size), dtype=x.dtype)
                    # if full skip the first row
                    if full:
                        y[0, :] = np.full(n, invsqrtn) @ x
                    for i in range(1, n):
                        invsqrt = 1.0 / np.sqrt(i ** 2 + i)
                        y[i - offset, :] = invsqrt * np.sum(x[:i, :], axis=0) - x[i, :] * (i * invsqrt)
                return y

            @njit(parallel=True, cache=True)
            def _bf(n, full, x, H):
                if H:
                    # transpose and conjugate
                    y = np.zeros((n, batch_size), dtype=x.dtype)
                    BperT = int(np.ceil(batch_size / _T))
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT), 1):
                            # if full skip the first row
                            if full:
                                for i in range(n):
                                    y[i, b] = invsqrtn * x[0, b]
                            for i in range(1, n):
                                invsqrt = 1.0 / np.sqrt((i + 1) * i)
                                for j in range(i):
                                    y[j, b] += invsqrt * x[i - offset, b]
                                y[i, b] -= x[i - offset, b] * (i * invsqrt)
                else:
                    y = np.empty((n - offset, batch_size), dtype=x.dtype)
                    __T = _T // 4
                    BperT = int(np.ceil(batch_size / __T))
                    #print(BperT, __T)
                    tmp_acc = np.full(__T, 0.0 * invsqrtn * x[0, 0])
                    for t in prange(__T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT), 1):
                            # if full skip the first row
                            if full:
                                y[0, b] = 0.0
                                for i in range(n):
                                    y[0, b] += invsqrtn * x[i, b]
                            for i in range(1, n):
                                invsqrt = 1.0 / np.sqrt(i ** 2 + i)
                                # y[i - offset, b] = -i * invsqrt * x[i, b]
                                tmp_acc[t] = -x[i, b] * i
                                for j in range(i):
                                    tmp_acc[t] += x[j, b]
                                    # y[i - offset, b] += invsqrt * x[j, b]
                                y[i - offset, b] = tmp_acc[t] * invsqrt
                return y

            return _bf(n, full, x, H) if use_numba else _no_bf(n, full, x, H)

        return _1d(n, full, x, H) if x.ndim == 1 else _2d(n, full, x, H)

    return LazyLinearOp(
        shape=(n - 1 + int(full), n),
        matmat=lambda x: _matmat(n, full, x, False),
        rmatmat=lambda x: _matmat(n, full, x, True)
    )


def hilbert(n: int, use_numba: bool=False, bf: bool=False):
    """Constructs Hilbert matrix n x n as a lazy linear operator H (H[i, j] = 1 / (i + j + 1)).
    Of note Hilbert matrix is positive definite and symmetric H = L + D + L^T where L is a lower
    triangular matrix such that L[i, i] = 0.
    
    Args:
        n: int
            The size of the matrix (n, n).
        use_numba: bool, optional
            If True, use Numba (default is False).
        bf: bool, optional
            If True, use brute force (default is False) and not NumPy.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n must be >= 2.

    References:
        See also `scipy.linalg.hilbert <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hilbert.html>`_.
        See also `Hilbert matrix <https://en.wikipedia.org/wiki/Hilbert_matrix>`_.
    """
    if n < 2:
        raise ValueError("n must be >= 2.")

    def _matmat(n, x):
        nb.config.DISABLE_JIT = 0 if use_numba else 1

        @njit(parallel=False, cache=True)
        def _1d(n, x):
            if x.ndim != 1:
                raise Exception("batch size must be equal to 1.")
            y = np.empty(n, dtype=x.dtype)
            for i in range(n):
                # (L + D + U) @ x where U = L^T
                # L is a lower triangular matrix such that L[i, i] = 0.
                # L @ x + D @ x + (x^T @ L)^T
                y[i] = np.divide(1.0, i + np.arange(n) + 1) @ x
            return y

        @njit(parallel=False, cache=True)
        def _bf1d(n, x):
            if x.ndim != 1:
                raise Exception("batch size must be equal to 1.")
            y = np.zeros(n, dtype=x.dtype)
            for i in range(n):
                # (L + D + U) @ x where U = L^T
                # L is a lower triangular matrix such that L[i, i] = 0.
                # L @ x + D @ x + (x^T @ L)^T
                for j in range(x.shape[0]):
                    y[i] += x[j] / (i + j + 1)
            return y

        @njit(parallel=True, cache=True)
        def _2d(n, x):
            if x.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = x.shape[1]
            y = np.empty((n, batch_size), dtype=x.dtype)
            for b in prange(batch_size):
                for i in range(n):
                    # (L + D + U) @ x where U = L^T
                    # L is a lower triangular matrix such that L[i, i] = 0.
                    # L @ x + D @ x + (x^T @ L)^T
                    y[i, b] = np.divide(1.0, i + np.arange(n) + 1) @ x[:, b]
            return y

        @njit(parallel=True, cache=True)
        def _bf2d(n, x):
            if x.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = x.shape[1]
            y = np.zeros((n, batch_size), dtype=x.dtype)
            BperT = int(np.ceil(batch_size / _T))
            for t in prange(_T):
                for b in range(t * BperT, min(batch_size, (t + 1) * BperT), 1):
                    for i in range(n):
                        # (L + D + U) @ x where U = L^T
                        # L is a lower triangular matrix such that L[i, i] = 0.
                        y[i, b] += x[i, b] / (i + i + 1)
                        for j in range(i + 1, x.shape[0]):
                            norm = 1 / (i + j + 1)
                            y[i, b] += x[j, b] * norm
                            y[j, b] += x[i, b] * norm
            return y

        if bf:
            return _bf1d(n, x) if x.ndim == 1 else _bf2d(n, x)
        else:
            return _1d(n, x) if x.ndim == 1 else _2d(n, x)

    return LazyLinearOp(
        shape=(n, n),
        matmat=lambda x: _matmat(n, x),
        rmatmat=lambda x: _matmat(n, x)
    )


def householder_matrix(v):
    """Constructs an Householder matrix lazy linear operator H
    from a non-zero unit column vector v.

    Args:
        v: 1d array
           non-zero vector (unit column vector)

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            The norm of vector v is zero.

    Examples:

    References:
        See also `Householder transformation <https://en.wikipedia.org/wiki/Householder_transformation>`_.
    """

    norm = np.sqrt(np.dot(v, v))
    if norm == 0.0:
        raise ValueError("The norm of vector v is zero.")

    def _matmat(v, x):
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        L = x.shape[0]
        batch_size = x.shape[1]
        y = np.empty(x.shape, dtype=x.dtype)
        for i in range(batch_size):
            y[:, i] = np.subtract(v[:, i], np.multiply(2.0, v @ (v.T.conj() @ x[:, i])))
        if is_1d:
            return y.ravel()
        else:
            return y

    return LazyLinearOp(
        shape=(v.shape[0], v.shape[0]),
        matmat=lambda x: _matmat(np.multiply(1.0 / norm, v), x),
        rmatmat=lambda x: _matmat(np.multiply(1.0 / norm, v), x)
    )


def lehmer(n: int, use_numba: bool=False, bf: bool=False):
    """Constructs Lehmer matrix n x n as a lazy linear operator L (L[i, j] = min(i, j) / max(i, j)).
    Of note Lehmer matrix is symmetric.
    
    Args:
        n: int
            The size of the matrix (n, n).
        use_numba: bool, optional
            If True, use Numba (default is False).
        bf: bool, optional
            If True, use brute force nested loops (default is False)

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n must be >= 2.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.special_matrices import lehmer
        >>> N = 2
        >>> x = np.random.rand(N)
        >>> np.allclose(lehmer(N) @ X, np.array([[1, 1 / 2], [1 / 2, 1]]) @ X)
        True

    References:
        See also `Lehmer matrix <https://en.wikipedia.org/wiki/Lehmer_matrix>`_.
    """
    if n < 2:
        raise ValueError("n must be >= 2.")

    def _matmat(n, x):
        nb.config.DISABLE_JIT = 0 if use_numba else 1

        # (L + D + U) @ x where U = L^T and D = Id
        # L is a lower triangular matrix such that L[i, i] = 0.
        # L @ x + x + (x^T @ L)^T

        @njit(parallel=False, cache=True)
        def _1d(n, x):
            if x.ndim != 1:
                raise Exception("batch size must be equal to 1.")
            y = np.copy(x)
            for i in range(n):
                # seq = np.divide(min(i, i:n), max(i, i:n))
                seq = np.divide(i + 1, np.arange(i + 1, n + 1, 1))
                seq[0] = 0.0
                if i == 0:
                    y[i] += seq @ x[i:]
                else:
                    # y[i] += np.add(seq @ x[i:], x[:i] @ np.divide(min(i, 0:i) / max(i, 0:i))))
                    y[i] += np.add(seq @ x[i:], np.divide(np.arange(1, i + 1), i + 1) @ x[:i])
            return y

        @njit(parallel=False, cache=True)
        def _bf1d(n, x):
            if x.ndim != 1:
                raise Exception("batch size must be equal to 1.")
            y = np.zeros(n, dtype=x.dtype)
            for i in range(n):
                for j in range(x.shape[0]):
                    y[i] += x[j] * min(i, j) / max(i, j)
            return y

        @njit(parallel=True, cache=True)
        def _2d(n, x):
            if x.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = x.shape[1]
            y = np.empty((n, batch_size), dtype=x.dtype)
            for b in prange(batch_size):
                seq = np.divide(1, np.arange(1, n + 1))
                y[0, b] = seq @ x[:, b]
                for i in range(1, n - 1):
                    seq = np.divide(
                        np.append(np.arange(1, i + 1), np.full(n - i, i + 1)),
                        np.append(np.full(i, i + 1), np.arange(i + 1, n + 1))
                    )
                    y[i, b] = seq @ x[:, b]
                seq = np.divide(np.arange(1, n + 1), n)
                y[n - 1, b] = seq @ x[:, b]
            return y

        @njit(parallel=True, cache=True)
        def _bf2d(n, x):
            if x.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = x.shape[1]
            y = np.zeros((n, batch_size), dtype=x.dtype)
            for b in prange(batch_size):
                for i in range(n):
                    y[i, b] += x[i, b]
                    for j in range(i + 1, x.shape[0]):
                        norm = min(i, j) / max(i, j)
                        y[i, b] += x[j, b] * norm
                        y[j, b] += x[i, b] * norm
            return y

        if bf:
            return _bf1d(n, x) if x.ndim == 1 else _bf2d(n, x)
        else:
            return _1d(n, x) if x.ndim == 1 else _2d(n, x)

    return LazyLinearOp(
        shape=(n, n),
        matmat=lambda x: _matmat(n, x),
        rmatmat=lambda x: _matmat(n, x)
    )


def leslie(f: np.ndarray, s: np.ndarray, use_numba: bool=False):
    """Constructs a Leslie matrix as a lazy linear operator L.

    Args:
        f: np.ndarray
            The fecundity coefficients (N, ).
        s: np.ndarray
            The survival coefficients (N - 1, ).

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            # of fecundity coefficients must be N and # of survival coefficients must be N - 1.

    References:
        See also `scipy.linalg.leslie <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.leslie.html>`_.
        See also `Leslie matrix <https://en.wikipedia.org/wiki/Leslie_matrix>`_.
    """
    N = f.shape[0]
    if (N - 1) != s.shape[0]:
        raise ValueError("# of fecundity coefficients must be N and # of survival coefficients must be N - 1.")

    def _matmat(f, s, x, H):
        def _1d(f, s, x, H):
            if x.ndim != 1:
                raise Exception("batch size must be equal to 1.")
            if H:
                # conjugate and transpose
                y = np.multiply(f, x[0])
                np.add(y[:(N - 1)], np.multiply(s, x[1:N]), out=y[:(N - 1)])
            else:
                y = np.empty(N, dtype=((f[0] + s[0]) * x[0]).dtype)
                y[0] = f @ x
                y[1:N] = np.multiply(s, x[:(N - 1)])
            return y

        def _2d(f, s, x, H):

            @njit(parallel=True, cache=True)
            def _bf(f, s, x, H):
                if x.ndim == 1:
                    raise Exception("batch size must be > 1.")
                batch_size = x.shape[1]
                BperT = int(np.ceil(batch_size / _T))
                y = np.empty((N, batch_size), dtype=np.float_)
                if H:
                    # conjugate and transpose
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT), 1):
                            for i in range(N - 1):
                                y[i, b] = f[i] * x[0, b] + s[i] * x[i + 1, b]
                            y[N - 1, b] = f[N - 1] * x[0, b]
                else:
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT), 1):
                            y[0, b] = f[0] * x[0, b]
                            for i in range(1, N):
                                y[0, b] += f[i] * x[i, b]
                                y[i, b] = s[i - 1] * x[i - 1, b]
                return y

            def _no_bf(f, s, x, H):
                if x.ndim == 1:
                    raise Exception("batch size must be > 1.")
                batch_size = x.shape[1]
                fT = f.reshape(f.shape[0], 1)
                sT = s.reshape(s.shape[0], 1)
                if H:
                    # conjugate and transpose
                    y = np.multiply(fT, x[0, :])
                    y[:(N - 1), :] += np.multiply(sT, x[1:, :])
                else:
                    y = np.empty((N, batch_size), dtype=((f[0] + s[0]) * x[0, 0]).dtype)
                    y[0, :] = f @ x
                    y[1:, :] = np.multiply(sT, x[:(N - 1), :])
                return y

            return _bf(f, s, x, H) if use_numba else _no_bf(f, s, x, H)

        return _1d(f, s, x, H) if x.ndim == 1 else _2d(f, s, x, H)

    return LazyLinearOp(
        shape=(f.shape[0], f.shape[0]),
        matmat=lambda x: _matmat(f, s, x, False),
        rmatmat=lambda x: _matmat(f, s, x, True)
    )


def pascal(n: int, kind: str='symmetric', exact: bool=True):
    """Constructs Pascal matrix as a lazy linear operator P.
    It uses the formula S = exp(A) @ exp(B) where B = A^T is
    a matrix with entries only on the first subdiagonal.
    The entries are the sequence arange(1, n) (NumPy notation).
    Of note, A and B are nilpotent matrices A^n = B^n = 0.
    To compute S @ X we use the Taylor expansion
    S @ X = sum(A^k / k!, k=0 to n) @ sum(B^k / k!, k=0 to n) @ X.
    Because of A and B are nilpotent matrices, we just have
    to compute the first n terms of the expansion.

    Args:
        n: int
            The size of the Pascal matrix (n, n).
        kind: str, optional
            If 'lower' constructs lower Pascal matrix L.
            If 'upper' constructs upper Pascal matrix U.
            If 'symmetric' (default) constructs L @ U.
        exact: bool, optional
            If exact is False the matrix coefficients are not
            the exact ones. If exact is True (default) the matrix
            coefficients will be integers.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            kind is either 'symmetric', 'lower' or 'upper'.

    Examples:
        >>> from lazylinop.wip.special_matrices import pascal
        >>> import numpy as np
        >>> import scipy as sp
        >>> N = 100
        >>> X = np.random.rand(N, 10)
        >>> P = pascal(N, kind='symmetric', exact=True)
        >>> np.allclose(P @ X, sp.linalg.pascal(N, kind='symmetric', exact=True) @ X)
        True

    References:
        See also `scipy.linalg.pascal <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.pascal.html>`_.
        See also `Pascal matrix <https://en.wikipedia.org/wiki/Pascal_matrix>`_.
    """
    if not kind in ['symmetric', 'lower', 'upper']:
        raise ValueError("kind is either 'symmetric', 'lower' or 'upper'.")

    def _matmat(n, x, kind):
        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            batch_size = 1
            is_1d = True
        else:
            batch_size = x.shape[1]
            is_1d = False
        # for large n entries of the Pascal matrix
        # become very big ! TODO something about it
        if n <= 160:
            y = np.empty((n, batch_size), dtype=x.dtype)
            Mx = np.empty(n, dtype=x.dtype)
        else:
            y = np.empty((n, batch_size), dtype=object)
            Mx = np.empty(n, dtype=object)
        if False and exact:
            # TODO
            pass
        else:
            scale = 1.0
            # L = exp(A)
            # U = exp(B)
            # S = L @ U
            # Of note, A and B=A^T matrices are nilpotents.
            # upper matrix U
            if kind == 'symmetric' or kind == 'upper':
                # it is better to use the seq trick for big value of n
                # instead of diag lazy linear operator ?
                # Du = diag(np.arange(1, n), k=1)
                seq = np.arange(1, n)
                for b in range(batch_size):
                    factor = 1.0
                    y[:, b] = x[:, b]
                    # np.copyto(Mx, Du @ x[:, b])
                    np.copyto(Mx, np.append(np.multiply(seq, x[1:, b]), [0.0]))
                    for i in range(1, n, 1):
                        factor /= i
                        np.add(y[:, b], np.multiply(factor, Mx), out=y[:, b])
                        # if b == 0:
                        #     print(i, y[0, b], factor, "*", Mx[0], "=", factor * Mx[0])
                        # np.copyto(Mx, Du @ Mx)
                        np.copyto(Mx, np.append(np.multiply(seq, Mx[1:]), [0.0]))
            # lower matrix L
            if kind == 'symmetric' or kind == 'lower':
                # it is better to use the seq trick for big value of n
                # instead of diag lazy linear operator ?
                # Dl = diag(np.arange(1, n), k=-1)
                seq = np.arange(1, n)
                for b in range(batch_size):
                    factor = 1.0
                    # if 'symmetric' is asked for, do not initialize
                    if kind == 'lower':
                        y[:, b] = x[:, b]
                        # np.copyto(Mx, Dl @ x[:, b])
                        np.copyto(Mx, np.append([0.0], np.multiply(seq, x[:(n - 1), b])))
                    else:
                        # np.copyto(Mx, Dl @ y[:, b])
                        np.copyto(Mx, np.append([0.0], np.multiply(seq, y[:(n - 1), b])))
                    for i in range(1, n, 1):
                        factor /= i
                        np.add(y[:, b], np.multiply(factor, Mx), out=y[:, b])
                        # np.copyto(Mx, Dl @ Mx)
                        np.copyto(Mx, np.append([0.0], np.multiply(seq, Mx[:(n - 1)])))
        return y.ravel() if is_1d else y

    if kind == 'lower':
        kindT = 'upper'
    elif kind == 'upper':
        kindT = 'lower'
    else:
        kindT = kind
        
    return LazyLinearOp(
        shape=(n, n),
        matmat=lambda x: _matmat(n, x, kind),
        rmatmat=lambda x: _matmat(n, x, kindT)
    )


def redheffer(n: int, use_numba: bool=False):
    r"""Constructs Redheffer matrix n x n as a lazy linear operator R.
    Redheffer matrix entry R[i, j] is 1 if i divides j, 0 otherwize.
    Redheffer matrix for n=5 looks like:

    .. math::
        R = \begin{pmatrix}
        1 & 1 & 1 & 1 & 1\\
        1 & 1 & 0 & 1 & 0\\
        1 & 0 & 1 & 0 & 0\\
        1 & 0 & 0 & 1 & 0\\
        1 & 0 & 0 & 0 & 1\\
        \end{pmatrix}

    and its transpose looks like:

    .. math::
        R^T = \begin{pmatrix}
        1 & 1 & 1 & 1 & 1\\
        1 & 1 & 0 & 0 & 0\\
        1 & 0 & 1 & 0 & 0\\
        1 & 1 & 0 & 1 & 0\\
        1 & 0 & 0 & 0 & 1\\
        \end{pmatrix}
    
    Args:
        n: int
            The size of the matrix (n, n).
        use_numba: bool, optional
            If True, use Numba (default is False).

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n must be >= 2.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.special_matrices import redheffer
        >>> N = 3
        >>> x = np.random.rand(N)
        >>> np.allclose(redheffer(N) @ x, np.array([[1, 1, 1], [1, 1, 0], [1, 0, 1]]) @ x)
        True

    References:
        See also `Redheffer matrix <https://en.wikipedia.org/wiki/Redheffer_matrix>`_.
    """
    if n < 2:
        raise ValueError("n must be >= 2.")

    def _matmat(n, x, adjoint):
        nb.config.DISABLE_JIT = 0 if use_numba else 1

        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            is_1d = True
        else:
            is_1d = False
        batch_size = x.shape[1]

        BperT = int(np.ceil(batch_size / _T))

        # diagonal of Redheffer matrix is 1
        # first column as-well-as first row is 1

        def _2d(n, x):
            if adjoint:
                y = np.zeros((n, batch_size), dtype=x.dtype)
                y[0, :] = np.sum(x, axis=0)
                y[1:, :] = x[0, :]
                for i in range(1, n):
                    y[np.arange(i, n, i + 1), :] += x[i, :]
            else:
                y = np.empty((n, batch_size), dtype=x.dtype)
                y[0, :] = np.sum(x, axis=0)
                for i in range(1, n):
                    y[i, :] = np.add(x[0, :], np.sum(x[np.arange(i, n, i + 1), :], axis=0))
            return y.ravel() if is_1d else y

        @njit(parallel=True, cache=True)
        def _bf2d(n, x):
            if x.ndim != 2:
                raise Exception("batch size must be greater than 1.")
            batch_size = x.shape[1]
            y = np.empty((n, batch_size), dtype=x.dtype)
            if adjoint:
                for t in prange(_T):
                    for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                        y[0, b] = x[0, b]
                        for i in range(1, n):
                            y[0, b] += x[i, b]
                            y[i, b] = x[0, b]
                        for i in range(1, n):
                            for j in range(i, n, i + 1):
                                y[j, b] += x[i, b]
            else:
                for t in prange(_T):
                    for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                        for i in range(n):
                            y[i, b] = x[0, b]
                            for j in range(i, n, i + 1):
                                y[i, b] += x[j, b]
                        y[0, b] -= x[0, b]
            return y.ravel() if is_1d else y

        return _bf2d(n, x) if use_numba else _2d(n, x)

    return LazyLinearOp(
        shape=(n, n),
        matmat=lambda x: _matmat(n, x, False),
        rmatmat=lambda x: _matmat(n, x, True)
    )


# def H(shape: tuple, F_to_C: bool = False):
#     """Constructs a lazy linear operator Op such that Op @ x
#     is F order flattened from C order flattened x array.
#     C and F order definition comes from Numpy flatten function.
#     If F order to C order is True swap shape[0] and shape[1].

#     Args:
#         shape: tuple, shape of the image
#         C_to_F: bool, optional
#         if True F order to C order, if False (default) C order to F order.
#         if C order to F order swap shape[0] and shape[1].

#     Returns:
#         LazyLinearOperator

#     Raises:
#         Exception
#             shape expects a tuple (X, Y).

#     Examples:
#         >>> from lazylinop.wip.special_matrices import H
#         >>> import numpy as np
#         >>> img = np.reshape(np.arange(16), newshape=(4, 4))
#         >>> Op = H(img.shape)
#         >>> np.allclose(Op @ img.flatten(order='C'), img.flatten(order='F'))
#         True
#         >>> img = np.reshape(np.arange(12), newshape=(3, 4))
#         >>> Op = H(img.shape)
#         >>> np.allclose(Op @ img.flatten(order='C'), img.flatten(order='F'))
#         True
#         >>> img = np.reshape(np.arange(12), newshape=(4, 3))
#         >>> Op = H(img.shape)
#         >>> np.allclose(Op @ img.flatten(order='C'), img.flatten(order='F'))
#         True
#     """
#     if shape[0] is None or shape[1] is None:
#         raise Exception("shape expects a tuple (X, Y).")
#     if F_to_C:
#         newshape = (shape[1], shape[0])
#     else:
#         newshape = (shape[0], shape[1])
#     def _matvec(x, shape):
#         X, Y = shape[0], shape[1]
#         mv = np.empty(X * Y, dtype=x.dtype)
#         # get column c=0
#         # P[r, r * Y] = 1 where r = 0 to X - 1
#         # get column c=1
#         # P[c * X + r, c + r * Y] = 1 where r = 0 to X - 1
#         # ...
#         for c in range(Y):
#             mv[c * X + np.arange(X)] = x[np.arange(X) * Y + c].conj()
#         return mv
#     def _rmatvec(x, shape):
#         Y, X = shape[0], shape[1]
#         mv = np.empty(X * Y, dtype=x.dtype)
#         for c in range(Y):
#             mv[c * X + np.arange(X)] = x[np.arange(X) * Y + c].conj()
#         return mv
#     return LazyLinearOp(
#         shape=(shape[0] * shape[1], shape[0] * shape[1]),
#         matvec=lambda x: _matvec(x, newshape),
#         rmatvec=lambda x: _rmatvec(x, newshape)
#     )


def h_multiply(a):
    """Constructs a Hessenberg decomposition as a lazy linear operator H.
    It can be used to compute the product between Hessenberg matrix and a vector x.
    Hessenberg decomposition writes a = Q @ H @ Q^H.

    Args:
        a: np.ndarray or LazyLinearOp
        Compute Hessenberg decomposition of the matrix a of shape (M, N).

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            Argument a expects a 2d array.
        ValueError
            # of rows and # of columns are differents.

    References:
        See also `scipy.linalg.hessenberg <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hessenberg.html>`_.
        See also `Hessenberg decomposition <https://en.wikipedia.org/wiki/Hessenberg_matrix>`_.
    """
    if a.ndim != 2:
        raise ValueError("Argument a expects 2d array.")
    if a.shape[0] != a.shape[1]:
        return ValueError("# of rows and # of columns are differents.")

    def _matmat(a, x, adjoint):

        if isLazyLinearOp(x):
            # TODO: do better than that
            H = sp.linalg.hessenberg(np.eye(x.shape[0], M=x.shape[0], k=0) @ a)[what[mode]]
        else:
            H = sp.linalg.hessenberg(a, calc_q=False)

        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
            batch_size = 1
        else:
            is_1d = False
            batch_size = x.shape[1]

        y = np.empty((a.shape[0], batch_size), dtype=(a[0, 0] * x[0]).dtype)

        # Hessenberg matrix first sub-diagonal has non-zero entries
        if adjoint:
            for b in range(batch_size):
                y[0, b] = H[:2, 0] @ x[:2, b]
                if a.shape[0] >= 2:
                    y[1, b] = H[:3, 1] @ x[:3, b]
                if a.shape[0] > 2:
                    for i in range(2, a.shape[0]):
                        y[i, b] = H[:min(a.shape[0], i + 2), i] @ x[:min(a.shape[0], i + 2), b]
        else:
            for b in range(batch_size):
                y[0, b] = H[0, :] @ x[:, b]
                if a.shape[0] >= 2:
                    y[1, b] = H[1, :] @ x[:, b]
                if a.shape[0] > 2:
                    for i in range(2, a.shape[0]):
                        y[i, b] = H[i, (i - 1):] @ x[(i - 1):, b]
        return y.ravel() if is_1d else y

    return LazyLinearOp(
        shape=(a.shape[0], a.shape[0]),
        matmat=lambda x: _matmat(a, x, False),
        # rmatmat=lambda x: _matmat(a.T.conj(), x, False)
        rmatmat=lambda x: _matmat(a, x, True)
    )


def sylvester(cp, cq):
    r"""Constructs Sylvester matrix as a lazy linear operator S_p,q.
    If p has a degree m=2 and q has a degree n=3 Sylvester matrix looks like:

    .. math::
        S = \begin{pmatrix}
        p_2 & p_1 & p_0 & 0 & 0\\
        0 & p_2 & p_1 & p_0 & 0\\
        0 & 0 & p_2 & p_1 & p_0\\
        q_3 & q_2 & q_1 & q_0 & 0\\
        0 & q_3 & q_2 & q_1 & q_0\\
        \end{pmatrix}

    Args:
        cp: list
            List of coefficients (m + 1) of the first polynomial p.
        cq: list
            List of coefficients (n + 1) of the second polynomial q.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            List of coefficients should have at least one element.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.special_matrices import sylvester
        >>> Op = sylvester(np.random.rand(3), np.random.rand(2))
        >>> check_op(Op)
        True

    References:
        See `Sylvester matrix <https://en.wikipedia.org/wiki/Sylvester_matrix>`_.
    """
    M = cp.shape[0]
    N = cq.shape[0]
    # Keep only the first dimension of the list of coefficients
    if cp.ndim > 1:
        cp = np.copy(cp[:1])
    if cq.ndim > 1:
        cq = np.copy(cq[:1])
    Md = M - 1
    Nd = N - 1
    if M == 0 or N == 0:
        raise ValueError("List of coefficients should have at least one element.")

    def _matmat(cp, cq, x):
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        y = np.empty((Md + Nd, batch_size), dtype=x.dtype)
        for b in range(batch_size):
            for n in range(Nd):
                y[n, b] = cp[::-1] @ x[n:(n + Md + 1), b]
            for m in range(Md):
                y[Nd + m, b] = cq[::-1] @ x[m:(m + Nd + 1), b]
        return y.ravel() if is_1d else y

    def _rmatmat(cp, cq, x):
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        y = np.zeros((Md + Nd, batch_size), dtype=x.dtype)
        for b in range(batch_size):
            for n in range(Nd):
                y[n:(n + Md + 1), b] += np.multiply(cp[::-1], x[n, b])
            for m in range(Md):
                y[m:(m + Nd + 1), b] += np.multiply(cq[::-1], x[Nd + m, b])
        return y.ravel() if is_1d else y

    return LazyLinearOp(
        shape=(Md + Nd, Md + Nd),
        matmat=lambda x: _matmat(cp, cq, x),
        rmatmat=lambda x: _rmatmat(cp, cq, x)
    )


def tri(a, factor: str='lower', use_numba: bool=False):
    """Constructs a lower (resp. upper) triangular matrix L (resp. U) from
    matrix a as a lazy linear operator Op.

    Args:
        a: np.ndarray or LazyLinearOp
        Shape of the input is (M, M).
        factor: str, optional
        If 'lower' (default) consider a as lower triangular matrix.
        If 'upper' consider a as upper triangular matrix.
        use_numba: str, optional
        If True, use prange from Numba (default is False)
        to compute batch in parallel.
        It is useful only and only if the batch size and
        the size of a are big enough.

    Returns:
        LazyLinearOp
        
    Raises:

    Examples:

    References:
    """

    def _matmat(a, x, factor, H):

        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            is_1d = True
        else:
            is_1d = False
        batch_size = x.shape[1]
        BperT = int(np.ceil(batch_size / _T))

        if isLazyLinearOp(a):
            a = np.eye(a.shape[0], M=a.shape[0], k=0) @ a

        M, N = a.shape

        def _no_bf(a, x, factor, H):
            if H:
                # conjugate transpose
                y = np.full((M, batch_size),  0 * (a[0, 0] * x[0, 0]))
                if factor == 'lower':
                    for i in range(M):
                        y[i, :] = a[i:M, i].conj() @ x[i:M, :]
                else:
                    for i in range(N):
                        y[i, :] = a[:(i + 1), i].conj() @ x[:(i + 1), :]
            else:
                y = np.full((M, batch_size),  0 * (a[0, 0] * x[0, 0]))
                if factor == 'lower':
                    for i in range(M):
                        y[i, :] = a[i, :(i + 1)] @ x[:(i + 1), :]
                else:
                    for i in range(M):
                        y[i, :] = a[i, i:N] @ x[i:N, :]
            return y.ravel() if is_1d else y

        @njit(parallel=True, cache=True)
        def _bf(a, x, factor, H):
            tmp = np.full(_T, 0 * (a[0, 0] * x[0, 0]))
            y = np.full((M, batch_size), 0 * (a[0, 0] * x[0, 0]))
            if H:
                # conjugate transpose
                if factor == 'lower':
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                            for i in range(M):
                                tmp[t] = 0 * (a[0, 0] * x[0, 0])
                                for j in range(i, M, 1):
                                    tmp[t] += np.conjugate(a[j, i]) * x[j, b]
                                y[i, b] = tmp[t]
                else:
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                            for i in range(N):
                                tmp[t] = 0 * (a[0, 0] * x[0, 0])
                                for j in range(i + 1):
                                    tmp[t] += np.conjugate(a[j, i]) * x[j, b]
                                y[i, b] = tmp[t]
            else:
                if factor == 'lower':
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                            for i in range(M):
                                tmp[t] = 0 * (a[0, 0] * x[0, 0])
                                for j in range(i + 1):
                                    tmp[t] += a[i, j] * x[j, b]
                                y[i, b] = tmp[t]
                else:
                    for t in prange(_T):
                        for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                            for i in range(M):
                                tmp[t] = 0 * (a[0, 0] * x[0, 0])
                                for j in range(i, N, 1):
                                    tmp[t] += a[i, j] * x[j, b]
                                y[i, b] = tmp[t]
            return y.ravel() if is_1d else y

        return _bf(a, x, factor, H) if use_numba else _no_bf(a, x, factor, H)

    return LazyLinearOp(
        shape=a.shape,
        matmat=lambda x: _matmat(a, x, factor, False),
        rmatmat=lambda x: _matmat(a, x, factor, True)
    )


def vander(x, N: int=None):
    r"""Constructs Vandermonde matrix as a lazy linear operator V.
    The shape of the Vandermonde lazy linear operator is (x.shape[0], deg + 1).

    .. math::
        V = \begin{pmatrix}
        1 & x[0] & x[0]^2 & ... & x[0]^{deg}\\
        1 & x[1] & x[1]^2 & ... & x[1]^{deg}\\
        1 & x[2] & x[2]^2 & ... & x[2]^{deg}\\
        . & .    & .      & ... &   .       \\
        . & .    & .      & ... &   .       \\
        . & .    & .      & ... &   .       \\
        1 & x[n] & x[n]^2 & ... & x[n]^{deg}
        \end{pmatrix}

    Args:
        x: 1d array
        Array of points
        N: int, optional
        Number of columns in the output.
        Maximum degree is N - 1.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            x must be a 1d-array.
        ValueError
            N expects an integer value >= 1.

    Examples:

    References:
        See also `NumPy polyvander <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyvander.html>`_.
        See also `NumPy vander function <https://numpy.org/doc/stable/reference/generated/numpy.vander.html>`_.
        See also `Vandermonde matrix <https://en.wikipedia.org/wiki/Vandermonde_matrix>`_.
    """
    if x.ndim != 1:
        raise ValueError("x must be a 1d-array.")
    if N is None:
        N = len(x)
    if N != int(N) or N < 1:
        raise ValueError("N expects an integer value >= 1.")

    def _matmat(x, X, H):
        if X.ndim == 1:
            X = X.reshape(X.shape[0], 1)
            is_1d = True
        else:
            is_1d = False
        batch_size = X.shape[1]

        y = np.empty(
            (N if H else x.shape[0], batch_size),
            dtype=np.complex_ if x.dtype.kind == 'c' or X.dtype.kind == 'c' else (x[0] * X[0, 0]).dtype
        )
        if H:
            # conjugate and transpose
            for i in range(N):
                y[i, :] = np.power(x, np.full(x.shape[0], i)) @ X
        else:
            for i in range(x.shape[0]):
                y[i, :] = np.power(np.full(N, x[i]), np.arange(0, N)) @ X
        return y.ravel() if is_1d else y

    return LazyLinearOp(
        shape=(x.shape[0], N),
        matmat=lambda X: _matmat(x, X, False),
        rmatmat=lambda X: _matmat(x, X, True)
    )


# def eigvals(a):
#     """Constructs a diagonal matrix from the eigen values of
#     matrix a as a lazy linear operator E.

#     Args:
#         a: np.ndarray or LazyLinearOp
#         Matrix to diagonalize.

#     Returns:
#         LazyLinearOp
        
#     Raises:

#     Examples:

#     References:
#         See also `scipy.linalg.eigvals function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigvals.html>`_.
#     """
#     def _matmat(a, x):
#         if x.ndim == 1:
#             x = x.reshape(x.shape[0], 1)
#             batch_size = 1
#             is_1d = True
#         else:
#             batch_size = x.shape[1]
#             is_1d = False
#         if 'complex' in a.dtype.str:
#             y = np.empty((a.shape[0], batch_size), dtype=np.complex_)
#         else:
#             y = np.empty((a.shape[0], batch_size), dtype=x.dtype)
#         if isLazyLinearOp(a):
#             # TODO: do better than that
#             D = diag(sp.linalg.eigvals(np.eye(a.shape[0], M=a.shape[0], k=0) @ a), k=0)
#         else:
#             D = diag(sp.linalg.eigvals(a), k=0)
#         # TODO: parallel computation
#         for b in range(batch_size):
#             y[:, b] = D @ x[:, b]
#         return y.ravel() if is_1d else y

#     return LazyLinearOp(
#         shape=a.shape,
#         matmat=lambda x: _matmat(a, x),
#         rmatmat=lambda x: _matmat(a, x)
#     )


# def inv(a: np.ndarray):
#     """Constructs inverse of a matrix as a lazy linear operator P.

#     Args:
#         a: np.ndarray
#         Matrix to invert

#     Returns:
#         LazyLinearOp
        
#     Raises:

#     Examples:

#     References:
#         See also `scipy.linalg.inv function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.inv.html>`_.
#     """

#     def _matmat(a, x):
#         if x.ndim == 1:
#             x = x.reshape(x.shape[0], 1)
#             batch_size = 1
#             is_1d = True
#         else:
#             batch_size = x.shape[1]
#             is_1d = False
#         if 'complex' in a.dtype.str:
#             y = np.empty((x.shape[0], batch_size), dtype='complex128')
#         else:
#             y = np.empty((x.shape[0], batch_size), dtype=x.dtype)
#         if isLazyLinearOp(a):
#             # TODO: do better than that
#             P = aslazylinearoperator(
#                 sp.linalg.inv(np.eye(a.shape[0], M=a.shape[1], k=0) @ a)
#             )
#         else:
#             P = aslazylinearoperator(sp.linalg.inv(a))
#         # TODO: parallel computation
#         for b in range(batch_size):
#             y[:, b] = P @ x[:, b]
#         return y.ravel() if is_1d else y

#     return LazyLinearOp(
#         shape=a.shape,
#         matmat=lambda x: _matmat(a, x),
#         rmatmat=lambda x: _matmat(a.T.conj(), x)
#     )


# def pinv(a: np.ndarray, atol: float=0.0, rtol: float=None):
#     """Constructs pseudo-inverse of a matrix as a lazy linear operator P.

#     Args:
#         a: np.ndarray
#         Matrix to pseudo-invert
#         atol: float, optional
#         Absolute threshold term (default is 0.0).
#         rtol: float, optional
#         Relative threshold term (default is 0.0).
#         See `scipy.linalg.pinv function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.pinv.html>`_ for more details.

#     Returns:
#         LazyLinearOp
        
#     Raises:

#     Examples:

#     References:
#         See also `scipy.linalg.pinv function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.pinv.html>`_.
#         See also `Moore-Penrose pseudo-inverse <https://en.wikipedia.org/wiki/Moore%E2%80%93Penrose_inverse>`_.
#     """

#     def _matmat(a, x):
#         if x.ndim == 1:
#             x = x.reshape(x.shape[0], 1)
#             batch_size = 1
#             is_1d = True
#         else:
#             batch_size = x.shape[1]
#             is_1d = False
#         y = np.empty(
#             (a.shape[1], batch_size),
#             dtype=np.complex_ if 'complex' in a.dtype.str else x.dtype
#         )
#         if isLazyLinearOp(a):
#             # TODO: do better than that
#             P = aslazylinearoperator(
#                 sp.linalg.pinv(
#                     np.eye(a.shape[0], M=a.shape[1], k=0) @ a,
#                     atol, rtol
#                 )
#             )
#         else:
#             P = aslazylinearoperator(sp.linalg.pinv(a, atol, rtol))
#         # TODO: parallel computation
#         for b in range(batch_size):
#             y[:, b] = P @ x[:, b]
#         return y.ravel() if is_1d else y

#     # complex conjugation and transposition commute
#     # with Moore-Penrose pseudo-inverse
#     return LazyLinearOp(
#         shape=(a.shape[1], a.shape[0]),
#         matmat=lambda x: _matmat(a, x),
#         rmatmat=lambda x: _matmat(a.T.conj(), x)
#     )


# def svd(a: np.ndarray):
#     """Constructs a diagonal matrix from the singular values of
#     matrix a as a lazy linear operator S.

#     Args:
#         a: np.ndarray or LazyLinearOp
#         Matrix to compute SVD.

#     Returns:
#         LazyLinearOp
        
#     Raises:

#     Examples:

#     References:
#         See also `scipy.linalg.svd function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.svd.html>`_.
#     """

#     def _matmat(a, x):
#         if x.ndim == 1:
#             x = x.reshape(x.shape[0], 1)
#             batch_size = 1
#             is_1d = True
#         else:
#             batch_size = x.shape[1]
#             is_1d = False
#         L = min(a.shape[0], a.shape[1])
#         if 'complex' in a.dtype.str:
#             y = np.empty((L, batch_size), dtype=np.complex_)
#         else:
#             y = np.empty((L, batch_size), dtype=x.dtype)
#         if isLazyLinearOp(a):
#             # TODO: do better than that
#             D = diag(
#                 sp.linalg.svd(
#                     np.eye(a.shape[0], M=a.shape[0], k=0) @ a,
#                     full_matrices=True, compute_uv=False
#                 ), k=0
#             )
#         else:
#             D = diag(sp.linalg.svd(a, full_matrices=True, compute_uv=False), k=0)
#         # TODO: parallel computation
#         for b in range(batch_size):
#             y[:, b] = D @ x[:, b]
#         return y.ravel() if is_1d else y

#     L = min(a.shape[0], a.shape[1])
#     return LazyLinearOp(
#         shape=(L, L),
#         matmat=lambda x: _matmat(a, x),
#         rmatmat=lambda x: _matmat(a, x)
#     )
