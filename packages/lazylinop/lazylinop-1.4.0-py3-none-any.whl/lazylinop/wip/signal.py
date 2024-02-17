"""
Module for signal processing related LazyLinearOps.
"""
import numpy as np
import scipy as sp
from lazylinop import *
import pywt
import sys
sys.setrecursionlimit(100000)
from lazylinop import mpad, mpad2


try:
    import numba as nb
    from numba import njit, prange, set_num_threads, threading_layer
    from numba.core import types
    from numba.typed import Dict
    _T = nb.config.NUMBA_NUM_THREADS
    nb.config.THREADING_LAYER = 'omp'
    nb.config.DISABLE_JIT = 0
except ImportError:
    print("Did not find Numba.")


def fft(N, backend='scipy', itype='complex', **kwargs):
    """
    Returns a LazyLinearOp for the DFT of size N.

    Args:
        N: int
            Size of the input (N > 0).
        backend:
            'scipy' (default) or 'pyfaust' for the underlying computation of the DFT.
        itype: str, optional
            Type of the input signal.
            If 'real' (default) use scipy.fft.rfft and scipy.fft.irfft.
        kwargs:
            any key-value pair arguments to pass to the scipy or pyfaust dft backend
            (https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html,
            https://faustgrp.gitlabpages.inria.fr/faust/last-doc/html/namespacepyfaust.html#a2695e35f9c270e8cb6b28b9b40458600).

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            itype expects either 'complex' or 'real'.

    Example:
        >>> from lazylinop.wip.signal import fft
        >>> import numpy as np
        >>> F1 = fft(32, norm='ortho')
        >>> F2 = fft(32, backend='pyfaust')
        >>> x = np.random.rand(32)
        >>> np.allclose(F1 @ x, F2 @ x)
        True
        >>> y = F1 @ x
        >>> np.allclose(F1.H @ y, x)
        True
        >>> np.allclose(F2.H @ y, x)
        True

    """

    if itype == 'complex':
        sp_fft = sp.fft.fft
        sp_ifft = sp.fft.ifft
    elif itype == 'real':
        sp_fft = sp.fft.rfft
        sp_ifft = sp.fft.irfft
    else:
        raise ValueError("itype expects either 'complex' or 'real'.")

    if backend == 'scipy':
        def scipy_scaling(kwargs):
            if 'norm' in kwargs:
                if kwargs['norm'] == 'ortho':
                    return 1
                elif kwargs['norm'] == 'forward':
                    return 1 / N
                elif kwargs['norm'] == 'backward':
                    return N
                else:
                    raise ValueError('Invalid norm value for scipy backend')
            else: # default is backward
                return N
        if itype == 'real':
            if 'n' in kwargs.keys():
                L = (kwargs['n'] // 2) + 1 if (kwargs['n'] % 2) == 0 else (kwargs['n'] + 1) // 2
            else:
                L = N
        else:
            L = N

        def _matmat(x):
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            # use Dask ?
            y = np.empty((L, batch_size), dtype=np.complex_)
            for b in range(batch_size):
                y[:, b] = sp_fft(x[:, b], axis=0, **kwargs)
            return y.ravel() if is_1d else y

        def _rmatmat(x):
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            # use Dask ?
            y = np.empty((L, batch_size), dtype=np.complex_)
            for b in range(batch_size):
                y[:, b] = sp_ifft(x[:, b], axis=0, **kwargs) * scipy_scaling(kwargs)
            return y.ravel() if is_1d else y

        F = LazyLinearOp(
            shape=(L, N),
            matmat=lambda x: _matmat(x),
            rmatmat=lambda x: _rmatmat(x),
            dtype='complex'
        )

        # lfft = LazyLinearOp(
        #     shape=(L, N),
        #     matmat=lambda x: (
        #         sp_fft(x, axis=0, **kwargs)
        #         # sp_fft(x, s=[kwargs['n']] if 'n' in kwargs.keys() else None, axes=[0])
        #     ),
        #     rmatmat=lambda x: (
        #         sp_ifft(x, axis=0, **kwargs) * scipy_scaling(kwargs)
        #         # sp_ifft(x, s=[kwargs['n']] if 'n' in kwargs.keys() else None, axes=[0]) * scipy_scaling(kwargs)
        #     )
        # )
    elif backend == 'pyfaust':
        from pyfaust import dft
        F = aslazylinearoperator(dft(N, **kwargs))
    else:
        raise ValueError('backend '+str(backend)+' is unknown')
    return F


def cfft(N, kernel, backend='scipy', itype='real', **kwargs):
    """
    Returns a LazyLinearOp for the IDFT{DFT(kernel) * DFT(input)} of size N.

    Args:
        N: int
            Size of the input (N > 0).
        kernel: 1d array
            Kernel to convolve with the input of size N.
        backend:
            'scipy' (default) or 'pyfaust' for the underlying computation of the DFT.
        itype: str, optional
            Type of the input signal.
            If 'real' (default) use scipy.fft.rfft and scipy.fft.irfft.
        kwargs:
            any key-value pair arguments to pass to the scipy or pyfaust dft backend
            (https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html,
            https://faustgrp.gitlabpages.inria.fr/faust/last-doc/html/namespacepyfaust.html#a2695e35f9c270e8cb6b28b9b40458600).

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            itype expects either 'complex' or 'real'.

    Example:
        >>> from lazylinop.wip.signal import cfft
        >>> import numpy as np
        >>> F1 = fft(32, norm='ortho')
        >>> F2 = fft(32, backend='pyfaust')
        >>> x = np.random.rand(32)
        >>> np.allclose(F1 @ x, F2 @ x)
        True
        >>> y = F1 @ x
        >>> np.allclose(F1.H @ y, x)
        True
        >>> np.allclose(F2.H @ y, x)
        True
    """

    if itype == 'complex':
        sp_fft = sp.fft.fftn
        sp_ifft = sp.fft.ifftn
    elif itype == 'real':
        sp_fft = sp.fft.rfftn
        sp_ifft = sp.fft.irfftn
    else:
        raise ValueError("itype expects either 'complex' or 'real'.")

    if True or backend == 'scipy':
        def scipy_scaling(kwargs):
            if 'norm' in kwargs:
                if kwargs['norm'] == 'ortho':
                    return 1
                elif kwargs['norm'] == 'forward':
                    return 1 / N
                elif kwargs['norm'] == 'backward':
                    return N
                else:
                    raise ValueError('Invalid norm value for scipy backend')
            else: # default is backward
                return N
        if itype == 'real':
            if 'n' in kwargs.keys():
                L = (kwargs['n'] // 2) + 1 if (kwargs['n'] % 2) == 0 else (kwargs['n'] + 1) // 2
                L = kwargs['n']
            else:
                L = N
        else:
            L = N
        F = LazyLinearOp(
            shape=(L, N),
            matmat=lambda x: (
                sp_ifft(
                    sp_fft(kernel, s=[kwargs['n']], axes=[0]) * sp_fft(x, s=[kwargs['n']], axes=[0]), s=[kwargs['n']], axes=[0]) * scipy_scaling(kwargs)
            ),
            rmatmat=lambda x: (
                sp_ifft(
                    sp_fft(kernel, s=[kwargs['n']], axes=[0]) * sp_fft(x, s=[kwargs['n']], axes=[0]), s=[kwargs['n']], axes=[0]) * scipy_scaling(kwargs)
            )
        )
    elif backend == 'pyfaust':
        # TODO
        # from pyfaust import dft
        # F = aslazylinearoperator(dft(N, **kwargs))
        pass
    else:
        raise ValueError('backend '+str(backend)+' is unknown')
    return F


def fft2(shape, backend='scipy', **kwargs):
    """Returns a LazyLinearOp for the 2D DFT of size n.

    Args:
        shape:
            the signal shape to apply the fft2.
        backend:
            'scipy' (default) or 'pyfaust' for the underlying computation of the 2D DFT.
        kwargs:
            any key-value pair arguments to pass to the `SciPy <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft2.html>`_
            or `pyfaust <https://faustgrp.gitlabpages.inria.fr/faust/last-doc/html/namespacepyfaust.html#a2695e35f9c270e8cb6b28b9b40458600>`_
            dft backend.

    Example:
        >>> from lazylinop.wip.signal import fft2
        >>> import numpy as np
        >>> F_scipy = fft2((32, 32), norm='ortho')
        >>> F_pyfaust = fft2((32, 32), backend='pyfaust')
        >>> x = np.random.rand(32, 32)
        >>> np.allclose(F_scipy @ x.ravel(), F_pyfaust @ x.ravel())
        True
        >>> y = F_scipy @ x.ravel()
        >>> np.allclose(F_scipy.H @ y, x.ravel())
        True
        >>> np.allclose(F_pyfaust.H @ y, x.ravel())
        True
    """
    s = shape[0] * shape[1]
    if backend == 'scipy':
        from scipy.fft import fft2, ifft2
        return LazyLinearOp(
            (s, s),
            matvec=lambda x: fft2(x.reshape(shape), **kwargs).ravel(),
            rmatvec=lambda x: ifft2(x.reshape(shape), **kwargs).ravel()
        )
    elif backend == 'pyfaust':
        from pyfaust import dft
        K = kron(dft(shape[0], **kwargs), dft(shape[1], **kwargs))
        return LazyLinearOp((s, s), matvec=lambda x: K @ x,
                                  rmatvec=lambda x: K.H @ x)
    else:
        raise ValueError('backend '+str(backend)+' is unknown')

def _is_power_of_two(n: int) -> bool:
    """return True if integer 'n' is a power of two.

    Args:
        n: int

    Returns:
        bool
    """
    return ((n & (n - 1)) == 0) and n > 0


def flip(shape: tuple, start: int = 0, end: int = None, axis: int = 0):
    """Constructs a flip lazy linear operator.

    Args:
        shape: tuple
        shape of the input
        start: int, optional
        flip from start (default is 0)
        end: int, optional
        stop flip (not included, default is None)
        axis: int, optional
        if axis=0 (default) flip per column, if axis=1 flip per row
        it does not apply if shape[1] is None.

    Returns:
        The flip LazyLinearOp

    Raises:
        ValueError
            start is < 0.
        ValueError
            start is > number of elements along axis.
        ValueError
            end is < 1.
        ValueError
            end is > number of elements along axis.
        ValueError
            end is <= start.
        ValueError
            axis is either 0 or 1.
    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.signal import flip
        >>> x = np.arange(6)
        >>> x
        array([0, 1, 2, 3, 4, 5])
        >>> y = flip(x.shape, 0, 5) @ x
        >>> y
        array([4, 3, 2, 1, 0, 5])
        >>> z = flip(x.shape, 2, 4) @ x
        >>> z
        array([0, 1, 3, 2, 4, 5])
        >>> X = np.eye(5, M=5, k=0)
        >>> X
        array([[1., 0., 0., 0., 0.],
               [0., 1., 0., 0., 0.],
               [0., 0., 1., 0., 0.],
               [0., 0., 0., 1., 0.],
               [0., 0., 0., 0., 1.]])
        >>> flip(X.shape, 1, 4) @ X
        array([[1., 0., 0., 0., 0.],
               [0., 0., 0., 1., 0.],
               [0., 0., 1., 0., 0.],
               [0., 1., 0., 0., 0.],
               [0., 0., 0., 0., 1.]])
    """
    N = shape[0]
    A = N
    if len(shape) == 2:
        M = shape[1]
        if axis == 1:
            A = M

    if start < 0:
        raise ValueError("start is < 0.")
    if start > A:
        raise ValueError("start is > number of elements along axis.")
    if not end is None and end < 1:
        raise ValueError("end is < 1.")
    if not end is None and end > A:
        raise ValueError("end is > number of elements along axis.")
    if not end is None and end <= start:
        raise ValueError("end is <= start.")
    if axis != 0 and axis != 1:
        raise ValueError("axis is either 0 or 1.")

    def _matmat(x, start, end, axis):
        if x.ndim == 1:
            y = np.copy(x.reshape(x.shape[0], 1))
            x_is_1d = True
            y[start:end, 0] = x[end - 1 - (np.arange(start, end, 1) - start)]
            return y.ravel()
        else:
            y = np.copy(x)
            x_is_1d = False
            if axis == 0:
                y[start:end, :] = x[end - 1 - (np.arange(start, end, 1) - start), :]
            else:
                y[:, start:end] = x[:, end - 1 - (np.arange(start, end, 1) - start)]
            return y

    return LazyLinearOp(
        shape=(N, N),
        matmat=lambda x: _matmat(x, start, N if end is None else end, axis),
        rmatmat=lambda x: _matmat(x, start, N if end is None else end, axis)
    )


def decimate(shape: tuple, start: int = 0, end: int = None, every: int = 2):
    """Constructs a decimation lazy linear operator.
    If the shape of the input array is (N, M) the operator
    has a shape = (ceil(D / every), N) where D = end - start.

    Args:
        shape: tuple
        Shape of the input
        start: int, optional
        First element to keep, default is 0
        end: int, optional
        Stop decimation (not included), default is None
        every: int, optional
        Keep element every this number, default is 2

    Returns:
        The decimation LazyLinearOp

    Raises:
        ValueError
            every is < 1.
        ValueError
            start is < 0.
        ValueError
            end is <= start.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.signal import decimate
        >>> x = np.arange(10)
        >>> x
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        >>> decimate(x.shape, 0, 10, every=2) @ x
        array([0, 2, 4, 6, 8])
        >>> X = np.arange(30).reshape((10, 3))
        >>> X
        array([[ 0,  1,  2],
               [ 3,  4,  5],
               [ 6,  7,  8],
               [ 9, 10, 11],
               [12, 13, 14],
               [15, 16, 17],
               [18, 19, 20],
               [21, 22, 23],
               [24, 25, 26],
               [27, 28, 29]])
        >>> decimate(X.shape, 0, 10, every=2) @ X
        array([[ 0,  1,  2],
               [ 6,  7,  8],
               [12, 13, 14],
               [18, 19, 20],
               [24, 25, 26]])
    """
    if every < 1:
        raise ValueError("every is < 1.")
    N = shape[0]
    if start < 0:
        raise ValueError("start is < 0.")
    M = 1 if len(shape) == 1 else shape[1]
    if start > N:
        raise ValueError("start is > number of elements along axis.")
    if not end is None:
        if end > N:
            raise ValueError("end is > number of elements along axis.")
    if not end is None and end <= start:
        raise ValueError("end is <= start.")

    def _matmat(x, start, end, every):
        D = end - start
        L = int(np.ceil(D / every))
        indices = np.arange(L)
        if x.ndim == 1:
            y = x[start + indices * every]
            return y
        else:
            y = x[start + indices * every, :]
            return y

    def _rmatmat(x, start, end, every):
        if x.ndim == 1:
            y = np.zeros(end, dtype=x.dtype)
            indices = np.arange(x.shape[0])
            y[start + indices * every] = x[indices]
            return y
        else:
            D = end - start
            y = np.zeros((end, x.shape[1]), dtype=x.dtype)
            indices = np.arange(x.shape[0])
            y[start + indices * every, :] = x[indices, :]
            return y

    last = N if end is None else end
    D = last - start
    L = int(np.ceil(D / every))
    return LazyLinearOp(
        shape=(L, N),
        matmat=lambda x: _matmat(x, start, last, every),
        rmatmat=lambda x: _rmatmat(x, start, last, every)
    )


def mslices(shape: tuple, start: list = np.ndarray, end: np.ndarray = None):
    """Constructs a multiple slices lazy linear operator.
    Element start[i] must be lesser than element end[i].
    Element end[i] must be greater or equal than element start[i - 1].
    If start[i] = end[i], extract only one element.
    If start or end is None, keep everything.

    Args:
        shape: tuple
        Shape of the input
        start: list, optional
        List of first element to keep, default is None
        end: list, optional
        List of last element to keep, default is None

    Returns:
        The multiple slices LazyLinearOp

    Raises:
        Exception
            start and end do not have the same length.
        ValueError
            start must be positive.
        ValueError
            end must be strictly positive.
        Exception
            end must be >= start.
        Exception
            end must be < shape[0].
        Exception
            last end must be > current start.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.signal import mslices
        >>> x = np.arange(10)
        >>> x
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        >>> mslices(x.shape, [0, 5], [2, 8]) @ x
        array([0, 1, 2, 5, 6, 7, 8])
    """
    if start is None or end is None:
        return eye(shape[0], n=shape[0], k=0)

    S = len(start)
    E = len(end)
    if S != E:
        raise Exception("start and end do not have the same length.")

    L = 0
    for s in range(S):
        if start[s] < 0:
            raise ValueError("start must be positive.")
        if end[s] < 0:
            raise ValueError("end must be strictly positive.")
        if end[s] < start[s]:
            raise Exception("end must be >= start.")
        if end[s] >= shape[0]:
            raise Exception("end must be < shape[0].")
        if s > 0:
            if end[s - 1] == start[s]:
                raise Exception("last end must be > current start.")
        L += end[s] - start[s] + 1

    def _matmat(x, start, end):
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        y = np.empty((L, batch_size), dtype=x.dtype)
        offset = 0
        for s in range(S):
            y[offset:(offset + end[s] - start[s] + 1), :] = x[start[s]:(end[s] + 1), :]
            offset += end[s] - start[s] + 1
        return y.ravel() if is_1d else y

    def _rmatmat(x, start, end):
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        y = np.zeros((shape[0], batch_size), dtype=x.dtype)
        offset = 0
        for s in range(S):
            y[start[s]:(end[s] + 1), :] = x[offset:(offset + end[s] - start[s] + 1), :]
            offset += end[s] - start[s] + 1
        return y.ravel() if is_1d else y

    return LazyLinearOp(
        shape=(L, shape[0]),
        matmat=lambda x: _matmat(x, start, end),
        rmatmat=lambda x: _rmatmat(x, start, end)
    )


def _fft_2radix(N: int, **kwargs):
    """Constructs a FFT lazy linear operator using radix-2 FFT algorithm.

    Args:
        N: int
        signal length (N = 2 ** k)
        kwargs:
            use_numba: bool
            if yes, use Numba decorator

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            signal length is not a power of 2.
    """
    if not _is_power_of_two(N):
        raise ValueError("signal length is not a power of 2.")

    use_numba = kwargs['use_numba'] if 'use_numba' in kwargs.keys() else False

    if N == 1:
        return LazyLinearOp(
            shape=(1, 1),
            matvec=lambda x: x,
            rmatvec=lambda x: x
        )
    else:
        # TODO: no Numba version
        # recursively compute FFT
        @njit(parallel=True, cache=True)
        def _matvec(x, N):
            omegaN = np.exp(-2j * np.pi / N)
            omega = 1.0
            if len(x.shape) == 1:
                x_is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                x_is_1d = False
            # decimate
            x_even = fft_2radix(x.shape[0] // 2) @ decimate(x.shape, 0, None, 2) @ x
            x_odd = fft_2radix(x.shape[0] // 2) @ decimate(x.shape, 1, None, 2) @ x
            # TODO: if len(x.shape) == 2
            output = np.full((N, x.shape[1]), 0j)
            NperT = int(np.ceil(N / _T))
            if NperT > 1000:
                for t in prange(_T):
                    for n in range(t * NperT, (t + 1) * NperT, 1):
                        if n >= N:
                            continue
                        nn = n % (N // 2)
                        output[n, :] = x_even[nn, :] + np.exp(-2j * np.pi * n / N) * x_odd[nn, :]
            else:
                # seq = np.arange(N)
                # mseq = np.mod(seq, N // 2)
                # output[seq, :] = np.add(x_even[mseq, :], np.exp(-2j * np.pi * seq / N).T @ x_odd[mseq, :])
                for n in range(0, N, 2):
                    nn = n % (N // 2)
                    output[n, :] = x_even[nn, :] + omega * x_odd[nn, :]
                    omega *= omegaN
                    nn = (n + 1) % (N // 2)
                    output[n + 1, :] = x_even[nn, :] + omega * x_odd[nn, :]
                    omega *= omegaN
            if x_is_1d:
                return output.ravel()
            else:
                return output
        @njit(parallel=True, cache=True)
        def _rmatvec(x, N):
            omegaN = np.exp(2j * np.pi / N)
            omega = 1.0
            if len(x.shape) == 1:
                x_is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                x_is_1d = False
            # decimate
            x_even = fft_2radix(x.shape[0] // 2).T.conj() @ decimate(x.shape, 0, None, 2) @ x
            x_odd = fft_2radix(x.shape[0] // 2).T.conj() @ decimate(x.shape, 1, None, 2) @ x
            # TODO: if len(x.shape) == 2
            output = np.full((N, x.shape[1]), 0j)
            NperT = int(np.ceil(N / _T))
            if NperT > 1000:
                for t in prange(_T):
                    for n in range(t * NperT, (t + 1) * NperT, 1):
                        if n >= N:
                            continue
                        nn = n % (N // 2)
                        output[n, :] = x_even[nn, :] + np.exp(2j * np.pi * n / N) * x_odd[nn, :]
            else:
                # seq = np.arange(N)
                # mseq = np.mod(seq, N // 2)
                # output[seq, :] = np.add(x_even[mseq, :], np.exp(2j * np.pi * seq / N).T @ x_odd[mseq, :])
                for n in range(0, N, 2):
                    nn = n % (N // 2)
                    output[n, :] = x_even[nn, :] + omega * x_odd[nn, :]
                    omega *= omegaN
                    nn = (n + 1) % (N // 2)
                    output[n + 1, :] = x_even[nn, :] + omega * x_odd[nn, :]
                    omega *= omegaN
            if x_is_1d:
                return output.ravel()
            else:
                return output
        return LazyLinearOp(
            shape=(N, N),
            matvec=lambda x: _matvec(x, N),
            rmatvec=lambda x: _rmatvec(x, N)
        )


def scatter_and_gather_windows(shape: tuple, window: int, nhop: int):
    """Constructs a scatter and gather windows lazy linear operator.
    For a given signal, window size (window) and number of
    elements (nhop) between two consecutive windows the
    lazy linear operator concatenates the windows into a
    signal that is larger than the original one. The number
    of windows is given by 1 + (signal length - window) // nhop.
    Therefore, the length of the output signal is nwindows * window.

    Args:
        shape: tuple
        Shape of the input array.
        window: int
        size of the window.
        nhop: int
        number of elements between two windows.

    Return:
        LazyLinearOp

    Raises:
        ValueError
            window argument expects a value > 0 and <= signal length.
        ValueError
            nhop argument expects a value > 0 and <= window.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.signal import scatter_window
        >>> x = np.arange(10)
        >>> x
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        >>> scatter_window(x.shape, 5, 2) @ x
        array([0, 1, 2, 3, 4, 2, 3, 4, 5, 6, 4, 5, 6, 7, 8])
        >>> X = np.arange(10).reshape(5, 2)
        >>> X
        array([[0, 1],
               [2, 3],
               [4, 5],
               [6, 7],
               [8, 9]])
        >>> scatter_window(X.shape, 3, 2) @ X
        array([[0, 1],
               [2, 3],
               [4, 5],
               [4, 5],
               [6, 7],
               [8, 9]])
    """
    if len(shape) == 1:
        N, batch_size = shape[0], 1
    else:
        N, batch_size = shape[0], shape[1]

    if window <= 0 or window > N:
        raise ValueError("window argument expects a value > 0 and <= signal length.")
    if nhop <= 0 or nhop > window:
        raise ValueError("nhop argument expects a value > 0 and <= window.")

    # number of windows in the original signal
    nwindows = 1 + (N - window) // nhop

    def _matmat(window, nhop, x):
        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            is_1d = True
        else:
            is_1d = False
        if True or nwindows <= 10:
            Op = eye(window, n=N, k=0)
            for i in range(1, nwindows, 1):
                Op = vstack((Op, eye(window, n=N, k=i * nhop)))
        else:
            Ops = [eye(window, n=N, k=0), eye(window, n=N, k=(nwindows // 2) * nhop)]
            for i in range(1, nwindows // 2):
                Ops[0] = vstack((Ops[0], eye(window, n=N, k=i * nhop)))
                Ops[1] = vstack((Ops[1], eye(window, n=N, k=(nwindows // 2 + i) * nhop)))
            if (nwindows % 2) == 1:
                Ops[1] = vstack((Ops[1], eye(window, n=N, k=(nwindows - 1) * nhop)))
            Op = vstack((Ops[0], Ops[1]))
        return (Op @ x).ravel() if is_1d else Op @ x

    def _rmatmat(window, nhop, x):
        if x.ndim == 1:
            x = x.reshape(x.shape[0], 1)
            is_1d = True
        else:
            is_1d = False
        Op = eye(N, n=window, k=0)
        for i in range(1, nwindows, 1):
            Op = hstack((Op, eye(N, n=window, k=-i * nhop)))
        return (Op @ x).ravel() if is_1d else Op @ x

    return LazyLinearOp(
        shape=(nwindows * window, N),
        matmat=lambda x: _matmat(window, nhop, x),
        rmatmat=lambda x : _rmatmat(window, nhop, x)
    )


def stft(shape: tuple, fs: float=1.0, window: str='hann', nperseg: int=256, noverlap: int=None, boundary: str='zeros', padded: bool=True, scaling: str='spectrum'):
    """Constructs a Short-Time-Fourier-Transform lazy linear operator.

    Args:
        shape: tuple
        Shape of the input array.
        fs: int, optional
        Sampling frequency (1 is default).
        window: str, optional
        Window name to use to avoid discontinuity if the
        segment was looped indefinitly ('hann' is default).
        See `scipy.signal.get_window <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window>`_
        for a list of available windows.
        nperseg: int, optional
        Number of samples in a frame (256 is default).
        noverlap: int, optional
        Number of samples to overlap between two consecutive
        segments (None is default correspoding to nperseg // 2).
        boundary: str or None, optional
        How to extend signal at both ends ('zeros' is default).
        padded: bool, optional
        Zero-pad the signal such that new length fits exactly
        into an integer number of window segments (True is default).
        scaling: str, optional
        Scaling mode ('spectrum' is default) follows scipy.signal.stft
        function, other possible choice is 'psd'.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            window argument expects 'hann'.
        ValueError
            scaling argument expects 'spectrum' or 'psd'.
        ValueError
            noverlap expects value less than nperseg.
        ValueError
            nperseg expects value greater than 0.

    Examples:

    References:
        See also `scipy.signal.stft <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html>`_.
    """
    if nperseg < 1:
        raise ValueError("nperseg expects value greater than 0.")

    if noverlap is None:
        noverlap = nperseg // 2
    if noverlap >= nperseg:
        raise ValueError("noverlap expects value less than nperseg.")

    if len(shape) == 1:
        N, batch_size = shape[0], 1
    else:
        N, batch_size = shape[0], shape[1]

    warray = sp.signal.windows.get_window(window, nperseg, fftbins=True)

    # number of zeros to add to both ends (boundary)
    bzeros = 1

    # number of samples between two frames > 0
    nhop = nperseg - noverlap
    # number of segments
    nseg = N // nperseg if nhop == 0 else 1 + (N - nperseg) // nhop
    # print("nseg={0:d}".format(nseg))
    # print(N, nperseg, nhop)
    # print("number of frames={0:d}".format(1 + (N + 2 * bzeros - nperseg) // nhop))

    def _lazy_rfft(N: int):
        nfreq = N // 2 + 1 if (N % 2) == 0 else (N + 1) // 2
        F = LazyLinearOp(
            shape=(N, N),
            matvec=lambda x: sp.fft.fft(x),
            rmatvec=lambda x: np.multiply(N, sp.fft.ifft(x)),
            dtype='complex128'
        )
        return F[:nfreq, :]

    def _1d(N, nperseg):
        # keep only positive-frequency terms
        nfreq = nperseg // 2 + 1 if (nperseg % 2) == 0 else (nperseg + 1) // 2
        # lazy linear operator for the FFT
        # from pyfaust import dft
        # F = dft(nperseg, normed=False)[:nfreq, :]
        F = _lazy_rfft(nperseg)
        # lazy linear operator "scatter and gather the windows"
        G = scatter_and_gather_windows((N, ), nperseg, nhop)#x.shape, nperseg, nhop)
        # lazy linear operator "one operation" per segment
        E = eye(nseg, n=nseg, k=0, dtype='complex128')
        # lazy linear operator to apply window
        W = kron(E, diag(warray, k=0))
        # lazy linear operator to apply STFT per segment
        S = kron(E, F)
        # lazy linear operator to scale the output
        if scaling == 'psd':
            sqscale = 1.0 / (fs * np.sum(np.square(warray)))
        elif scaling == 'spectrum':
            sqscale = 1.0 / np.sum(warray) ** 2
        else:
            raise ValueError("scaling argument expects 'spectrum' or 'psd'.")
        D = diag(np.full(nseg * nfreq, np.sqrt(sqscale)), k=0)
        # print(D, S, W, x.shape, D @ S @ W, x.astype(np.complex128).shape)
        # return complete operator
        return D @ S @ W @ G# @ x.astype(np.complex128)

    def _2d(N, batch_size, nperseg):
        Op = _1d(N, nperseg)
        for b in range(1, batch_size):
            Op = vstack((Op, _1d(N, nperseg)))
        return Op

    return _1d(N, nperseg) if batch_size == 1 else _2d(N, batch_size, nperseg)


def fwht(shape: tuple, normalize: bool = False, backend: str = 'lazylinop.direct'):
    """Constructs a Fast-Walsh-Hadamard-Transform lazy linear operator.
    The size of the signal has to be a power of two greater than 1.

    Args:
        shape: tuple
        Shape of the input array (M, N)
        normalize: tuple, optional
        Normalize at each stage of the FWHT (default is False)
        backend: str, optional
        It can be 'lazylinop' (default), 'pytorch' (wip) or 'scipy'.
        'lazylinop.kronecker' uses kron to compute FWHT (it can be very slow).
        'lazylinop.direct' uses kind of brute force to compute FWHT.
        It uses Numba prange for parallel computation.
        'pytorch' does not work yet.
        'scipy' uses scipy.linalg.hadamard.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            The size of the signal must be a power of two, greater or equal to two.
        ValueError
            backend argument expects either 'kronecker', 'lazylinop', 'pytorch' or 'scipy'.

    Examples:
    >>> import numpy as np
    >>> import scipy as sp
    >>> from lazylinop.wip.signal import fwht
    >>> x = np.random.rand(16)
    >>> y = fwht(x.shape) @ x
    >>> np.allclose(y, sp.linalg.hadamard(x.shape[0]) @ X)
    >>> X = np.random.rand(8, 4)
    >>> Y = fwht(X.shape) @ X
    >>> np.allclose(Y, sp.linalg.hadamard(X.shape[0]) @ X)

    References:
        See also `Wikipedia <https://en.wikipedia.org/wiki/Hadamard_transform>`_.
        See also `SciPy <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hadamard.html>`_.
    """

    if not _is_power_of_two(shape[0]) or shape[0] < 2:
        raise ValueError("The size of the signal must be a power of two, greater or equal to two.")

    if backend == 'scipy':
        return LazyLinearOp(
            shape=(shape[0], shape[0]),
            matvec=lambda x: sp.linalg.hadamard(shape[0]) @ x,
            rmatvec=lambda x: sp.linalg.hadamard(shape[0]) @ x,
            dtype='float'
        )
    elif backend == 'pytorch':
        raise Exception('PyTorch backend is Work-in-Progress.')
        from math import log2, sqrt
        import torch
        def _matmat(x):
            output = torch.Tensor(x)
            xshape = x.shape
            if len(xshape) == 1:
                output = output.unsqueeze(0)
            batch_dim, L = output.shape
            D = int(log2(L))
            H, F = 2, 1
            for d in range(D):
                output = output.view(batch_dim, L // H, H)
                h1, h2 = output[:, :, :F], output[:, :, F:]
                output = torch.cat((h1 + h2, h1 - h2), dim=-1)
                H *= 2
                F = H // 2
            if normalize:
                return (output / pow(2.0, D / 2.0)).view(*xshape)
            else:
                return output.view(*xshape)

        return LazyLinearOp(
            shape=(shape[0], shape[0]),
            matvec=lambda x: _matmat(x),
            rmatvec=lambda x: _matmat(x),
            dtype='float'
        )
    elif backend == 'lazylinop.kronecker':
        H1 = (1.0 / np.sqrt(2.0) if normalize else 1.0) * np.array([[1.0, 1.0], [1.0, -1.0]])
        D = int(np.log2(shape[0]))
        if D == 1:
            return aslazylinearoperator(H1)
        elif D == 2:
            return kron(H1, H1)
        else:
            Hd = kron(H1, H1)
            for d in range(1, D - 1):
                Hd = kron(H1, Hd)
            return Hd
    elif backend == 'lazylinop.direct':

        def _matmat(x):

            @njit(parallel=False, cache=True)
            def _1d(x):
                M = x.shape[0]
                H = 1
                D = int(np.floor(np.log2(M)))
                output = np.empty(M, dtype=x.dtype)
                tmp1, tmp2 = 0.0, 0.0
                for i in range(M):
                    output[i] = x[i]
                for d in range(D):
                    for i in range(0, M, 2 * H):
                        for j in range(i, i + H):
                            tmp1 = output[j]
                            tmp2 = output[j + H]
                            output[j] = tmp1 + tmp2
                            output[j + H] = tmp1 - tmp2
                    H *= 2
                # normalization
                if normalize:
                    norm = 1.0 / np.power(2.0, D / 2)
                    for i in range(M):
                        output[i] *= norm
                return output

            @njit(parallel=True, cache=True)
            def _2d(x):
                M = x.shape[0]
                batch_size = x.shape[1]
                Hs = np.full(batch_size, 1)
                D = int(np.floor(np.log2(M)))
                output = np.empty((M, batch_size), dtype=x.dtype)
                NperT = int(np.ceil(batch_size / _T))
                tmp1 = np.full(batch_size, 0.0 * x[0, 0])
                tmp2 = np.full(batch_size, 0.0 * x[0, 0])
                for t in prange(_T):
                    for n in range(t * NperT, min(batch_size, (t + 1) * NperT), 1):
                        for i in range(M):
                            output[i, n] = x[i, n]
                        for d in range(D):
                            for i in range(0, M, 2 * Hs[n]):
                                for j in range(i, i + Hs[n]):
                                    tmp1[n] = output[j, n]
                                    tmp2[n] = output[j + Hs[n], n]
                                    output[j, n] = tmp1[n] + tmp2[n]
                                    output[j + Hs[n], n] = tmp1[n] - tmp2[n]
                            Hs[n] *= 2
                # normalization
                if normalize:
                    norm = 1.0 / np.power(2.0, D / 2)
                    for i in range(M):
                        output[i, n] *= norm
                return output

            return _1d(x) if x.ndim == 1 else _2d(x)

        return LazyLinearOp(
            shape=(shape[0], shape[0]),
            matmat=lambda x: _matmat(x),
            rmatmat=lambda x: _matmat(x),
            dtype='float'
        )
    else:
        raise ValueError("backend argument expects either 'lazylinop.direct', 'lazylinop.kronecker', 'pytorch' or 'scipy'.")


def convolve(in1, in2: np.ndarray, mode: str = 'full', method: str = 'lazylinop.scipy.signal.convolve'):
    """If shape of the signal has been passed return a lazy linear operator
    that corresponds to the convolution with the kernel. If signal has been
    passed return the convolution result. If signal is a 2d array (S, batch),
    return convolution per column.

    Args:
        in1: tuple or np.ndarray
        Shape or array of the input.
        in2: np.ndarray
        1d kernel to convolve with the signal, shape is (K, ).
        mode: str, optional
        'full' computes convolution (input + padding)
        'valid' computes 'full' mode and extract centered output that does not depend on the padding. 
        'same' computes 'full' mode and extract centered output that has the same shape that the input.
        'circ' computes circular convolution
        method: str, optional
        'auto' use lazy encapsulation of scipy.signal.convolve (optimization and benchmark in progress)
        'direct' direct computation using nested for loops (Numba implementation)
        'lazylinop.scipy.signal.convolve' (default) to use lazy encapsulation of Scipy.signal convolve function
        'scipy.linalg.toeplitz' to use lazy encapsulation of Scipy implementation of Toeplitz matrix
        'pyfaust.toeplitz' to use pyfaust implementation of Toeplitz matrix
        'oa' to use lazylinop implementation of overlap-add method
        'scipy.linalg.circulant' use Scipy implementation of circulant matrix (works with mode='circ')
        'scipy.fft.fft' use Scipy implementation of FFT to compute circular convolution (works with mode='circ')
        'pyfaust.circ' use pyfaust implementation of circulant matrix (works with mode='circ')
        'pyfaust.dft' use pyfaust implementation of DFT (works with mode='circ')

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        ValueError
        Number of dimensions of the signal and/or the kernel is greater than one.
        ValueError
        mode is either 'full' (default), 'valid', 'same' or 'circ'
        ValueError
        Shape or input_array are expected
        ValueError
        Size of the kernel is greater than the size of signal and mode is valid.
        ValueError
        method is not in:
        'auto',
        'direct',
        'lazylinop.scipy.signal.convolve',
        'scipy.linalg.toeplitz',
        'pyfaust.toeplitz',
        'oa',
        'scipy.linalg.circulant',
        'scipy.fft.fft',
        'pyfaust.circ',
        'pyfaust.dft'
        Exception
        in1 expects tuple or np.ndarray.
        ValueError
        method='scipy.linalg.circulant', 'pyfaust.circ', 'scipy.fft.fft' or 'pyfaust.dft' works only with mode='circ'.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.signal import convolve
        >>> import scipy as sp
        >>> signal = np.random.rand(1024)
        >>> kernel = np.random.rand(32)
        >>> c1 = convolve(signal.shape, kernel, mode='same', method='direct') @ signal
        >>> c2 = convolve(signal.shape, kernel, mode='same', method='pyfaust.toeplitz') @ signal
        >>> c3 = sp.signal.convolve(signal, kernel, mode='same', method='auto')
        >>> np.allclose(c1, c3)
        True
        >>> np.allclose(c2, c3)
        True
        >>> signal = np.random.rand(32768)
        >>> kernel = np.random.rand(48)
        >>> c1 = convolve(signal.shape, kernel, mode='circ', method='scipy.fft.fft') @ signal
        >>> c2 = convolve(signal.shape, kernel, mode='circ', method='pyfaust.dft') @ signal
        >>> c3 = convolve(signal, kernel, mode='same', method='scipy.fft.fft')
        >>> c4 = convolve(signal, kernel, mode='same', method='pyfaust.dft')
        >>> np.allclose(c1, c2)
        True
        >>> np.allclose(c1, c3)
        True
        >>> np.allclose(c1, c4)
        True

    References:
        See also `SciPy convolve function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve.html>`_.
        See also `SciPy correlate function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html>`_.
    """
    if not mode in ['full', 'valid', 'same', 'circ']:
        raise ValueError("mode is either 'full' (default), 'valid', 'same' or 'circ'.")

    methods = [
        'auto',
        'direct',
        'lazylinop.scipy.signal.convolve',
        'scipy.linalg.toeplitz',
        'pyfaust.toeplitz',
        'oa',
        'scipy.linalg.circulant',
        'scipy.fft.fft',
        'pyfaust.circ',
        'pyfaust.dft'
    ]

    circmethods = [
        'auto',
        'direct',
        'scipy.linalg.circulant',
        'scipy.fft.fft',
        'pyfaust.circ',
        'pyfaust.dft'
    ]

    if mode == 'circ' and not method in circmethods:
        raise ValueError("mode 'circ' expects method to be in " + str(circmethods))

    if mode != 'circ' and (method == 'scipy.linalg.circulant' or method == 'pyfaust.circ' or method == 'scipy.fft.fft' or method == 'pyfaust.dft'):
        raise ValueError("method='scipy.linalg.circulant', 'pyfaust.circ', 'scipy.fft.fft' or 'pyfaust.dft' works only with mode='circ'.")

    # Check if signal has been passed to the function
    # Check if shape of the signal has been passed to the function
    if type(in1) is tuple:
        return_lazylinop = True
        shape = in1
    elif type(in1) is np.ndarray:
        return_lazylinop = False
        shape = in1.shape
    else:
        raise Exception("in1 expects tuple or np.ndarray.")

    if shape[0] <= 0 or in2.ndim != 1:
        raise ValueError("Number of dimensions of the signal and/or the kernel is not equal to 1.")

    K = in2.shape[0]
    S = shape[0]
    if K > S and mode == 'valid':
        raise ValueError("Size of the kernel is greater than the size of the signal and mode is valid.")

    if mode == 'circ':
        if method == 'auto':
            compute = 'circ.scipy.fft.fft'
        else:
            compute = 'circ.' + method
    else:
        if method == 'auto':
            if K < np.log(S):
                compute = 'direct'
            else:
                compute = 'lazylinop.scipy.signal.convolve'
        else:
            compute = method

    # Length of the output as a function of convolution mode
    dim = {}
    dim['full'] = S + K - 1
    dim['valid'] = S - K + 1
    dim['same'] = S
    dim['circ'] = S
    start = (dim['full'] - dim[mode]) // 2
    rmode = {}
    rmode['full'] = 'valid'
    rmode['valid'] = 'full'
    rmode['same'] = 'same'
    rmode['circ'] = 'circ'
    rstart = (dim['full'] - dim[rmode[mode]]) // 2

    dims = np.array([S + K - 1, S - K + 1, S, S], dtype=np.int_)
    imode = 0 * int(mode == 'full') + 1 * int(mode == 'valid') + 2 * int(mode == 'same') + 3 * int(mode == 'circ')

    # Check which method is asked for
    if compute == 'direct':
        dim = Dict.empty(
            key_type=types.unicode_type,
            value_type=types.int64
        )
        dim['full'] = S + K - 1
        dim['valid'] = S - K + 1
        dim['same'] = S
        dim['circ'] = S

        def _matmat(signal, kernel):
            # Because of Numba split 1d and 2d
            @njit(parallel=True, cache=True)
            def _1d(signal, kernel):
                K = kernel.shape[0]
                S = signal.shape[0]
                O = S + K - 1
                y = np.full(dims[imode], 0.0 * (kernel[0] * signal[0]))
                # y[n] = sum(h[k] * s[n - k], k, 0, K - 1)
                # n - k > 0 and n - k < len(s)
                OperT = int(np.ceil(O / _T))
                if (OperT * K) > 100000:
                    for t in prange(_T):
                        # i - j >= 0
                        # i - j < S
                        for i in range(t * OperT, min(O, (t + 1) * OperT), 1):
                            if i >= start and i < (start + dims[imode]):
                                for j in range(
                                        min(max(0, i - S + 1), min(K, i + 1)),
                                        min(K, i + 1),
                                        1
                                ):
                                    y[i - start] += kernel[j] * signal[i - j]
                else:
                    for i in range(start, start + dims[imode], 1):
                        maxj = min(K, i + 1)
                        minj = min(max(0, i - S + 1), maxj)
                        for j in range(minj, maxj, 1):
                            y[i - start] += kernel[j] * signal[i - j]
                return y

            @njit(parallel=True, cache=True)
            def _2d(signal, kernel):
                K = kernel.shape[0]
                S, batch_size = signal.shape
                O = S + K - 1
                y = np.full((dims[imode], batch_size), 0.0 * (kernel[0] * signal[0, 0]))
                # y[n] = sum(h[k] * s[n - k], k, 0, K - 1)
                # n - k > 0 and n - k < len(s)
                OperT = int(np.ceil(O / _T))
                if (OperT * K * batch_size) > 100000:
                    for t in prange(_T):
                        # i - j >= 0
                        # i - j < S
                        for b in range(batch_size):
                            for i in range(t * OperT, min(O, (t + 1) * OperT), 1):
                                if i >= start and i < (start + dims[imode]):
                                    for j in range(
                                            min(max(0, i - S + 1), min(K, i + 1)),
                                            min(K, i + 1),
                                            1
                                    ):
                                        y[i - start, b] += kernel[j] * signal[i - j, b]
                else:
                    for b in range(batch_size):
                        for i in range(start, start + dims[imode], 1):
                            maxj = min(K, i + 1)
                            minj = min(max(0, i - S + 1), maxj)
                            for j in range(minj, maxj, 1):
                                y[i - start, b] += kernel[j] * signal[i - j, b]
                return y

            return _1d(signal, kernel) if signal.ndim == 1 else _2d(signal, kernel)

        def _rmatmat(signal, kernel):
            # Because of Numba split 1d and 2d
            @njit(parallel=True, cache=True)
            def _1d(signal, kernel):
                K = kernel.shape[0]
                S = signal.shape[0]
                O = S + K - 1
                y = np.full(dims[2], 0.0 * (kernel[0] * signal[0]))
                # y[n] = sum(h[k] * s[k + n], k, 0, K - 1)
                # k + n < len(s)
                OperT = int(np.ceil(O / _T))
                if (OperT * K) > 100000:
                    for t in prange(_T):
                        for i in range(t * OperT, min(O, (t + 1) * OperT), 1):
                            if i >= rstart and i < (rstart + dims[2]):
                                for j in range(K):
                                    if (j - i + S - 1) >= 0 and (j - i + S - 1) < S:
                                        y[dims[2] - 1 - (i - rstart)] += kernel[j] * np.conjugate(signal[j - i + S - 1])
                else:
                    for i in range(rstart, rstart + dims[2]):
                        for j in range(K):
                            if (j - i + S - 1) >= 0 and (j - i + S - 1) < S:
                                y[dims[2] - 1 - (i - rstart)] += kernel[j] * np.conjugate(signal[j - i + S - 1])
                return y

            @njit(parallel=True, cache=True)
            def _2d(signal, kernel):
                K = kernel.shape[0]
                S, batch_size = signal.shape
                O = S + K - 1
                y = np.full((dims[2], batch_size), 0.0 * (kernel[0] * signal[0, 0]))
                # y[n] = sum(h[k] * s[k + n], k, 0, K - 1)
                # k + n < len(s)
                OperT = int(np.ceil(O / _T))
                if (OperT * K * batch_size) > 100000:
                    for t in prange(_T):
                        for b in range(batch_size):
                            for i in range(t * OperT, min(O, (t + 1) * OperT), 1):
                                if i >= rstart and i < (rstart + dims[2]):
                                    for j in range(K):
                                        if (j - i + S - 1) >= 0 and (j - i + S - 1) < S:
                                            y[dims[2] - 1 - (i - rstart), b] += kernel[j] * np.conjugate(signal[j - i + S - 1, b])
                else:
                    for b in range(batch_size):
                        for i in range(rstart, rstart + dims[2]):
                            for j in range(K):
                                if (j - i + S - 1) >= 0 and (j - i + S - 1) < S:
                                    y[dims[2] - 1 - (i - rstart), b] += kernel[j] * np.conjugate(signal[j - i + S - 1, b])
                return y

            return _1d(signal, kernel) if signal.ndim == 1 else _2d(signal, kernel)

        C = LazyLinearOp(
            shape=(dim[mode], dim['same']),
            matmat=lambda x: _matmat(x, in2),
            # rmatvec=lambda x: np.flip(_matvec(np.conjugate(np.flip(x)), in2))
            rmatmat=lambda x: _rmatmat(x, in2)
        )
    elif compute == 'lazylinop.scipy.signal.convolve':
        def _matmat(x):
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            y = np.empty((dim[mode], batch_size), dtype=(x[0, 0] * in2[0]).dtype)
            # Use Dask ?
            for b in range(batch_size):
                y[:, b] = sp.signal.convolve(x[:, b], in2, mode=mode, method='auto')
            return y.ravel() if is_1d else y
        def _rmatmat(x):
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            y = np.empty((dim['same'], batch_size), dtype=(x[0, 0] * in2[0]).dtype)
            # Use Dask ?
            for b in range(batch_size):
                y[:, b] = np.flip(sp.signal.convolve(np.flip(x[:, b]), in2, mode=rmode[mode], method='auto'))
            return y.ravel() if is_1d else y
        C = LazyLinearOp(
            shape=(dim[mode], dim['same']),
            matmat=lambda x: _matmat(x),
            rmatmat=lambda x: _rmatmat(x),
            dtype=in2.dtype
        )
    elif compute == 'scipy.linalg.toeplitz':
        C = LazyLinearOp(
            shape=(dim[mode], dim['same']),
            matmat=lambda x: sp.linalg.toeplitz(
                np.pad(in2, (0, S - 1)),
                np.pad([in2[0]], (0, S - 1))
            )[start:(start + dim[mode]), :] @ x,
            rmatmat=lambda x: (
                sp.linalg.toeplitz(
                    np.pad(in2, (0, S - 1)),
                    np.pad([in2[0]], (0, S - 1))
                )[start:(start + dim[mode]), :].T.conj() @ x if 'complex' in [str(x.dtype), str(in2.dtype)]
                else np.real(sp.linalg.toeplitz(
                        np.pad(in2, (0, S - 1)),
                        np.pad([in2[0]], (0, S - 1))
                )[start:(start + dim[mode]), :].T.conj() @ x)
            )
        )
    elif compute == 'pyfaust.toeplitz':
        from pyfaust import toeplitz
        iscomplex = 'complex' in str(in2.dtype)
        def _scalar2array(x):
            if x.shape == ():
                return x.reshape(1, )
            else:
                return x
        C = LazyLinearOp(
            shape=(dim[mode], dim['same']),
            matmat=lambda x: _scalar2array(toeplitz(
                np.pad(in2, (0, S - 1)),
                np.pad([in2[0]], (0, S - 1)),
                diag_opt=False
            )[start:(start + dim[mode]), :] @ x) if iscomplex or 'complex' in str(x.dtype)
            else np.real(_scalar2array(toeplitz(
                    np.pad(in2, (0, S - 1)),
                    np.pad([in2[0]], (0, S - 1)),
                    diag_opt=False
            )[start:(start + dim[mode]), :] @ x)),
            rmatmat=lambda x: (
                _scalar2array(toeplitz(
                    np.pad(in2, (0, S - 1)),
                    np.pad([in2[0]], (0, S - 1)),
                    diag_opt=False
                )[start:(start + dim[mode]), :].T.conj() @ x) if iscomplex or 'complex' in str(x.dtype)
                else np.real(_scalar2array(toeplitz(
                        np.pad(in2, (0, S - 1)),
                        np.pad([in2[0]], (0, S - 1)),
                        diag_opt=False
                )[start:(start + dim[mode]), :].T.conj() @ x))
            )
        )
    elif compute == 'oa':
        C = _oaconvolve(in1 if type(in1) is tuple else in1.shape, in2, mode=mode, fft_backend='scipy')
    elif 'circ.' in compute:
        tmp_method = method.replace('circ.', '')
        C = _circconvolve(in1 if type(in1) is tuple else in1.shape, in2, tmp_method)
    else:
        raise ValueError("method is not in " + str(methods))

    Op = LazyLinearOp(
        shape=C.shape,
        matmat=lambda x: (
            C @ x if 'complex' in [str(x.dtype), str(in2.dtype)]
            else np.real(C @ x)
        ),
        rmatmat=lambda x: (
            C.H @ x if 'complex' in [str(x.dtype), str(in2.dtype)]
            else np.real(C.H @ x)
        ),
        dtype=in2.dtype
    )
    return Op if return_lazylinop else Op @ in1


def dsconvolve(in1, in2: np.ndarray, mode: str = 'full', offset: int=0, every: int=2):
    """Creates convolution plus down-sampling lazy linear operator.
    If shape of the signal has been passed return a lazy linear operator
    that corresponds to the convolution with the kernel.
    If signal has been passed return the convolution result.
    If signal is a 2d array (S, batch), return convolution per column.
    offset argument determines the first element to keep while every argument
    determines distance between two elements to keep (it can be 1 or 2).

    Args:
        in1: tuple or np.ndarray
        Shape or array of the input.
        in2: np.ndarray
        1d kernel to convolve with the signal, shape is (K, ).
        mode: str, optional
            'full' computes convolution (input + padding).
            'valid' computes 'full' mode and extract centered output that does not depend on the padding.
            'same' computes 'full' mode and extract centered output that has the same shape that the input.
        offset: int, optional
        First element to keep (default is 0).
        every: int, optional
        Keep element every this number (default is 2).

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        ValueError
            Number of dimensions of the signal and/or the kernel is greater than one.
        ValueError
            mode is either 'full' (default), 'valid' or 'same'
        ValueError
            Shape or input_array are expected
        ValueError
            Size of the kernel is greater than the size of signal and mode is valid.
        Exception
            in1 expects tuple or np.ndarray.
        ValueError
            offset must be either 0 or 1.
        ValueError
            every must be either 1 or 2.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.signal import dsconvolve
        >>> import scipy as sp
        >>> signal = np.random.rand(1024)
        >>> kernel = np.random.rand(32)
        >>> Op = dsconvolve(signal.shape, kernel, mode='same', offset=0, every=2)
        >>> c1 = Op @ signal
        >>> c2 = sp.signal.convolve(signal, kernel, mode='same', method='auto')
        >>> np.allclose(c1, c2[0::2])
        True

    References:
        See also `SciPy convolve function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve.html>`_.
        See also `SciPy correlate function <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html>`_.
    """
    if not mode in ['full', 'valid', 'same']:
        raise ValueError("mode is either 'full' (default), 'valid' or 'same'.")

    # check if signal or shape of the signal has been passed to the function
    if type(in1) is tuple:
        return_lazylinop = True
        shape = in1
    elif type(in1) is np.ndarray:
        return_lazylinop = False
        shape = in1.shape
    else:
        raise Exception("in1 expects tuple or np.ndarray.")

    if shape[0] <= 0 or in2.ndim != 1:
        raise ValueError("Number of dimensions of the signal and/or the kernel is not equal to 1.")

    K = in2.shape[0]
    S = shape[0]
    if K > S and mode == 'valid':
        raise ValueError("Size of the kernel is greater than the size of the signal and mode is valid.")
    if offset != 0 and offset != 1:
        raise ValueError('offset must be either 0 or 1.')
    if every != 1 and every != 2:
        raise ValueError('every must be either 1 or 2.')

    # Length of the output as a function of convolution mode
    dims = np.array([S + K - 1, S - K + 1, S, S], dtype=np.int_)
    imode = 0 * int(mode == 'full') + 1 * int(mode == 'valid') + 2 * int(mode == 'same')
    start = (dims[0] - dims[imode]) // 2 + offset
    L = int(np.ceil((dims[imode] - offset) / every))

    OperT = int(np.ceil(dims[0] / _T))
    assert (OperT * _T) >= dims[0]

    def _matmat(signal, kernel):
        batch_size = 1 if signal.ndim == 1 else signal.shape[1]
        use_parallel = bool((OperT * K) > 100000 and batch_size == 1)
        use_bparallel = bool((OperT * K) > 100000 and batch_size > 1)
        # Because of Numba split 1d and 2d
        @njit(parallel=use_parallel, cache=True)
        def _1d(signal, kernel, use_prange):
            y = np.full(L, 0.0 * (kernel[0] * signal[0]))
            # y[n] = sum(h[k] * s[n - k], k, 0, K - 1)
            # n - k > 0 and n - k < len(s)
            if use_prange:
                tmp_acc = np.full(_T, 0.0 * (kernel[0] * signal[0]))
                for t in prange(_T):
                    for i in range(start + t * OperT, start + (t + 1) * OperT):
                        if i >= start and i < (start + dims[imode]) and ((i - start) % every) == 0:
                            tmp_acc[t] = 0.0
                            for j in range(min(K, i + 1)):
                                if (i - j) < S:
                                    tmp_acc[t] += kernel[j] * signal[i - j]
                            y[(i - start) // every] = tmp_acc[t]
            else:
                for i in range(dims[0]):
                    if i >= start and i < (start + dims[imode]) and ((i - start) % every) == 0:
                        tmp_acc = 0.0
                        for j in range(min(K, i + 1)):
                            if (i - j) < S:
                                tmp_acc += kernel[j] * signal[i - j]
                        # print(signal.shape, shape, (i - start) // every, L, i - start, dims[imode], offset)
                        y[(i - start) // every] = tmp_acc
            return y

        @njit(parallel=use_bparallel, cache=True)
        def _2d(signal, kernel):
            batch_size = signal.shape[1]
            BperT = int(np.ceil(batch_size / min(batch_size, _T)))
            y = np.full((L, batch_size), 0.0 * (kernel[0] * signal[0, 0]))
            for t in prange(min(batch_size, _T)):
                for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                    y[:, b] = _1d(signal[:, b], kernel, not use_bparallel)
            return y

        return _1d(signal, kernel, False) if signal.ndim == 1 else _2d(signal, kernel)

    def _rmatmat(signal, kernel):
        batch_size = 1 if signal.ndim == 1 else signal.shape[1]
        use_parallel = bool((OperT * K) > 100000 and batch_size == 1)
        use_bparallel = bool((OperT * K) > 100000 and batch_size > 1)
        # Because of Numba split 1d and 2d
        @njit(parallel=use_parallel, cache=True)
        def _1d(signal, kernel, use_prange):
            x = 0 if imode == 0 and offset == 0 else 1
            y = np.full(dims[2], 0.0 * (kernel[0] * signal[0]))
            for i in range(dims[2]):
                tmp_acc = 0.0
                if every == 2:
                    jstart = (i - x * start) - (i - x * start) // every
                elif every == 1:
                    jstart = i - x * start
                else:
                    pass
                for j in range(L):
                    if j < jstart:
                        continue
                    if every == 2:
                        k = (i - x * start) % 2 + (j - jstart) * every
                    elif every == 1:
                        k = j - jstart
                    else:
                        pass
                    if k < K:
                        tmp_acc += kernel[k] * signal[j]
                y[i] = tmp_acc
            return y

        @njit(parallel=use_bparallel, cache=True)
        def _2d(signal, kernel):
            batch_size = signal.shape[1]
            BperT = int(np.ceil(batch_size / min(batch_size, _T)))
            y = np.full((dims[2], batch_size), 0.0 * (kernel[0] * signal[0, 0]))
            for t in prange(min(batch_size, _T)):
                for b in range(t * BperT, min(batch_size, (t + 1) * BperT)):
                    y[:, b] = _1d(signal[:, b], kernel, not use_bparallel)
            return y

        return _1d(signal, kernel, True) if signal.ndim == 1 else _2d(signal, kernel)

    Op = LazyLinearOp(
        shape=(L, dims[2]),
        matmat=lambda x: (
            _matmat(x, in2) if 'complex' in str(x.dtype) or 'complex' in str(in2.dtype)
            else np.real(_matmat(x, in2))
        ),
        rmatmat=lambda x: (
            _rmatmat(x, in2) if 'complex' in str(x.dtype) or 'complex' in str(in2.dtype)
            else np.real(_rmatmat(x, in2))
        ),
        dtype=in2.dtype
    )
    return Op if return_lazylinop else Op @ in1


def _circconvolve(in1, in2: np.ndarray, method: str='auto'):
    """This function returns circular convolution.
    Length of the signal S and length of the kernel K must be the same.
    If not, pad the signal (resp. the kernel) if S > K (resp. K < S).
    If shape of the signal has been passed return Lazy Linear Operator
    that corresponds to the convolution with the kernel.
    If signal has been passed return the convolution result.
    The function only considers the first dimension of both kernel and signal.

    Args:
        in1: tuple or np.ndarray
        shape or array of the input
        in2: np.ndarray
        kernel to use for the convolution
        method: str, optional
            'auto' use lazy encapsulation of scipy.fft fft and ifft functions (optimization and benchmark in progress)
            'direct' direct computation using nested for loops (Numba implementation is work-in-progress)
            'scipy.linalg.circulant' use Scipy implementation of the circulant matrix
            'scipy.fft.fft' use Scipy implementation of the FFT
            'pyfaust.circ' use pyfaust implementation of circulant matrix
            'pyfaust.dft' use pyfaust implementation of DFT (pad the signal such that the length is a power of 2)

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        Exception
        Kernel number of dimensions < 1.
        ValueError
        Shape or input array are expected.
        ValueError
        method is not in ['auto', 'direct', 'scipy.linalg.circulant', 'scipy.fft.fft', 'pyfaust.circ', 'pyfaust.dft'].
    """
    if not type(in1) is tuple and not type(in1) is np.ndarray:
        raise ValueError("Shape or input array are expected")

    # check if signal has been passed to the function
    # check if shape of the signal has been passed to the function
    return_lazylinop, B = True if type(in1) is tuple else False, 2
    shape = in1 if type(in1) is tuple else in1.shape

    # keep only the first dimension of the kernel
    if in2.ndim == 1:
        kernel = np.copy(in2)
    elif in2.ndim > 1:
        kernel = np.copy(in2[:1])
    else:
        raise Exception("Kernel number of dimensions < 1.")

    ckernel = 'complex' in str(in2.dtype)

    # size of the kernel
    K = kernel.size
    # size of the signal
    S = shape[0]
    # size of the output
    O = max(S, K)
    # pad the kernel
    P = O
    if method == 'pyfaust.dft' and not _is_power_of_two(P):
        print("Length of the signal is not a power of two, switch method 'pyfaust.dft' to 'auto'.")
        method = 'auto'
        # P = np.power(2, int(np.floor(np.log2(O))) + 1)
    if P > K:
        pkernel = np.pad(kernel, (0, P - K), mode='constant', constant_values=0.0)
    else:
        pkernel = np.copy(kernel)

    if method == 'direct':
        if _disable_numba:
            def _matvec(kernel, signal):
                K = kernel.shape[0]
                S = signal.shape[0]
                output = np.full(S, 0.0)
                # y[n] = sum(h[k] * s[n - k mod N], k, 0, K - 1)
                for i in range(S):
                    output[i] = np.dot(kernel, signal[np.mod(np.subtract(i, np.arange(K)), S)])
                return output
            def _rmatvec(kernel, signal):
                K = kernel.shape[0]
                S = signal.shape[0]
                output = np.full(S, 0.0)
                # y[n] = sum(h[k] * s[n - k mod N], k, 0, K - 1)
                for i in range(S):
                    output[i] = np.dot(kernel, signal[np.mod(np.add(i, np.arange(K)), S)])
                return output
        else:
            @njit(parallel=True, cache=True)
            def _matvec(kernel, signal):
                K = kernel.shape[0]
                S = signal.shape[0]
                output = np.full(S, 0.0)
                # y[n] = sum(h[k] * s[n - k mod N], k, 0, K - 1)
                OperT = int(np.ceil(S / _T))
                if (OperT * K) > 1000:
                    for t in prange(_T):
                        for i in range(t * OperT, min(S, (t + 1) * OperT), 1):
                            for j in range(K):
                                output[i] += kernel[j] * signal[np.mod(i - j, S)]
                else:
                    for i in range(S):
                        for j in range(K):
                            output[i] += kernel[j] * signal[np.mod(i - j, S)]
                return output
            @njit(parallel=True, cache=True)
            def _rmatvec(kernel, signal):
                K = kernel.shape[0]
                S = signal.shape[0]
                output = np.full(S, 0.0)
                # y[n] = sum(h[k] * s[k + n mod N], k, 0, K - 1)
                OperT = int(np.ceil(S / _T))
                if (OperT * K) > 10000:
                    for t in prange(_T):
                        for i in range(t * OperT, min(S, (t + 1) * OperT), 1):
                            for j in range(K):
                                output[i] += kernel[j] * signal[np.mod(i + j, S)]
                else:
                    for i in range(S):
                        for j in range(K):
                            output[i] += kernel[j] * signal[np.mod(i + j, S)]
                return output
        C = LazyLinearOp(
            shape=(P, P),
            matvec=lambda x: _matvec(pkernel, x),
            rmatvec=lambda x: _rmatvec(pkernel, x)
        )
    elif method == 'scipy.linalg.circulant':
        C = LazyLinearOp(
            shape=(P, P),
            matvec=lambda x: sp.linalg.circulant(pkernel) @ x,
            rmatvec=lambda x: sp.linalg.circulant(pkernel).T.conj() @ x
        )
    elif method == 'scipy.fft.fft' or method == 'auto':
        # Op = FFT^-1 @ diag(FFT(kernel)) @ FFT
        fft_kernel = fft(P, backend='scipy', itype='complex') @ pkernel
        F = fft(P, backend='scipy', norm='forward', itype='complex').H @ diag(fft_kernel, k=0) @ fft(P, backend='scipy', itype='complex')
        C = LazyLinearOp(
            shape=(P, P),
            matvec=lambda x: (
                F @ x if 'complex' in [str(kernel.dtype), str(x.dtype)]
                else np.real(F @ x)
            ),
            rmatvec=lambda x: (
                F.H @ x if 'complex' in [str(kernel.dtype), str(x.dtype)]
                else np.real(F.H @ x)
            )
        )
    elif method == 'pyfaust.circ':
        from pyfaust import circ
        C = LazyLinearOp(
            shape=(P, P),
            matvec=lambda x: (
                circ(pkernel) @ x if 'complex' in [str(pkernel.dtype), str(x.dtype)]
                else np.real(circ(pkernel) @ x)
            ),
            rmatvec=lambda x: (
                circ(pkernel).H @ x if 'complex' in [str(pkernel.dtype), str(x.dtype)]
                else np.real(circ(pkernel).H @ x)
            )
        )
    elif method == 'pyfaust.dft':
        from pyfaust import dft
        F = aslazylinearoperator(dft(P, normed=False))
        fft_kernel = F @ pkernel
        A = F.H @ diag(fft_kernel, k=0) @ F
        AH = F.H @ diag(fft_kernel.conj(), k=0) @ F
        C = LazyLinearOp(
            shape=(P, P),
            matvec=lambda x: (
                np.multiply(1.0 / P, A @ x) if 'complex' in [str(pkernel.dtype), str(x.dtype)]
                else np.multiply(1.0 / P, np.real(A @ x))
            ),
            rmatvec=lambda x: (
                np.multiply(1.0 / P, AH @ x) if 'complex' in [str(pkernel.dtype), str(x.dtype)]
                else np.multiply(1.0 / P, np.real(AH @ x))
            )
        )
    else:
        raise ValueError("method is not in ['auto', 'direct', 'scipy.linalg.circulant', 'scipy.fft.fft', 'pyfaust.circ', 'pyfaust.dft']")

    # extract output of length S
    if return_lazylinop:
        # return lazy linear operator
        if P > S:
            return (C @ eye(P, n=S, k=0))[:S, :]
        else:
            return C[:S, :]
    else:
        # return result of the circular convolution
        if P > S:
            return (C @ eye(P, n=S, k=0) @ signal)[:S]
        else:
            return (C @ signal)[:S]


def _oaconvolve(in1, in2: np.ndarray, mode: str = 'full', **kwargs):
    """This function implements overlap-add method for convolution.
    If shape of the signal has been passed return Lazy Linear Operator
    that corresponds to the convolution with the kernel.
    If signal has been passed return the convolution result.
    The function only considers the first dimension of the kernel.

    Args:
        in1: tuple or np.ndarray
        Shape or array of the input
        in2: np.ndarray
        Kernel to use for the convolution
        mode: str, optional
            'full' computes convolution (input + padding)
            'valid' computes 'full' mode and extract centered output that does not depend on the padding
            'same' computes 'full' mode and extract centered output that has the same shape that the input
            refer to Scipy documentation of scipy.signal.convolve function for more details
        kwargs:
            block_size (int) size of the block unit (a power of two)
            fft_backend (str) see :py:func:`fft` for more details

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        Exception
        kernel number of dimensions < 1.
        ValueError
        mode is either 'full' (default), 'valid' or 'same'
        ValueError
        shape or input_array are expected
        ValueError
        block_size argument expects a value that is a power of two.
        ValueError
        block_size must be greater than the kernel size.
        ValueError
        size of the kernel is greater than the size of the signal.
    """
    if not mode in ['full', 'valid', 'same']:
        raise ValueError("mode is either 'full' (default), 'valid' or 'same'")
    if not type(in1) is tuple and not type(in1) is np.ndarray:
        raise ValueError("'shape' or 'input_array' are expected.")

    # check if signal has been passed to the function
    # check if shape of the signal has been passed to the function
    return_lazylinop, B = True if type(in1) is tuple else False, 2
    shape = in1 if type(in1) is tuple else in1.shape
    backend = 'scipy'
    for key, value in kwargs.items():
        if key == 'block_size':
            B = value
            if B <= 0 or not _is_power_of_two(B):
                raise ValueError("block_size argument expects a value that is a power of two.")
        elif key == 'fft_backend':
            fft_backend = value
        else:
            pass

    # keep only the first dimension of the kernel
    if in2.ndim == 1:
        kernel = np.copy(in2)
    elif in2.ndim > 1:
        kernel = np.copy(in2[:1])
    else:
        raise Exception("kernel number of dimensions < 1.")

    # size of the kernel
    K = kernel.size
    # size of the signal
    S = shape[0]
    if K > S:
        raise ValueError("size of the kernel is greater than the size of the signal.")
    # size of the output (full mode)
    O = S + K - 1

    # block size B, number of blocks X = S / B
    if not "block_size" in kwargs.keys():
        # no input for the block size: compute a value
        B = K
        while B < min(S, 2 * K) or not _is_power_of_two(B):
            B += 1
    else:
        if B < K:
            raise ValueError("block_size must be greater or equal to the kernel size.")
    # number of blocks
    step = B
    B *= 2
    R = S % step
    X = S // step + 1 if R > 0 else S // step

    # create linear operator Op that will be applied to all the blocks
    # Op = ifft(np.diag(fft(kernel)) @ fft(signal))
    # use Kronecker product between identity matrix and Op to apply to all the blocks
    # we can also use block_diag operator
    # use mpad to pad each block
    if S > (2 * K):
        # if the signal size is greater than twice
        # the size of the kernel use overlap-based convolution
        # fft_kernel = sp.fft.fft(np.pad(kernel, (0, B - K)))
        fft_kernel = fft(B, backend=fft_backend, itype='complex') @ eye(B, n=K, k=0) @ kernel
        F = fft(B, backend=fft_backend, norm='forward', itype='complex').H @ diag(fft_kernel, k=0) @ fft(B, backend=fft_backend, itype='complex')
        # is block_diag faster than kron ?
        # Op = oa(B, X, overlap=B - step) @ kron(eye(X, n=X, k=0), F) @ mpad2(step, X, n=B - step)
        Op = oa(B, X, overlap=B - step) @ block_diag(*[F] * X) @ mpad2(step, X, n=B - step)
        if (X * step) > S:
            Op = Op @ eye(X * step, n=S, k=0)
    else:
        # if the signal size is not greater than twice
        # the size of the kernel use FFT-based convolution
        fft_kernel = fft(O, backend=fft_backend) @ eye(O, n=K, k=0) @ kernel
        Op = fft(O, backend=fft_backend, norm='forward', itype='complex').H @ diag(fft_kernel, k=0) @ fft(O, backend=fft_backend, itype='complex') @ eye(O, n=S, k=0)

    # convolution mode
    if mode == 'valid':
        # compute full mode, valid mode returns
        # elements that do not depend on the padding
        extract = S - K + 1
        start = (O - extract) // 2
    elif mode == 'same':
        # keep the middle of full mode (centered)
        # and returns the same size that the signal size
        extract = S
        start = (O - extract) // 2
    else:
        # compute full mode
        extract = O
        start = 0
    indices = np.arange(start, start + extract, 1)
    # use eye operator to extract
    Op = eye(extract, n=Op.shape[0], k=start) @ Op

    iscomplex = 'complex' in str(in2.dtype)

    def _batch(op, x):
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        y = np.empty((op.shape[0], batch_size), dtype=binary_dtype(op.dtype, x.dtype))
        # print(op.dtype, x.dtype, y.dtype)
        # use Dask ?
        for b in range(batch_size):
            y[:, b] = op @ x[:, b]
        return y.ravel() if is_1d else y

    if return_lazylinop:
        # return LazyLinearOp
        return LazyLinearOp(
            shape=(Op.shape[0], S),
            matmat=lambda x: _batch(Op, x) if iscomplex or 'complex' in str(x.dtype)
            else np.real(_batch(Op, x)),
            rmatmat=lambda x: _batch(Op.H, x) if iscomplex or 'complex' in str(x.dtype)
            else np.real(_batch(Op.H, x))
        )
    else:
        # return result of the convolution
        return (
            Op @ in1 if iscomplex
            else np.real(Op @ in1)
        )

def oa(L: int, X: int, overlap: int=1):
    """return overlap-add linear operator.
    The overlap-add linear operator adds last overlap of block i > 0
    with first overlap of block i + 1.
    Of note, block i = 0 (of size L - overlap) does not change.

    Args:
        L: int
        Block size.
        X: int
        Number of blocks.
        overlap: int
        Size of the overlap < L (strictly positive).

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        ValueError
            L is strictly positive.
        ValueError
            X is strictly positive.
        ValueError
            overlap must be > 0 and <= L

    Examples:
        >>> from lazylinop.wip.signal import oa
        >>> import numpy as np
        >>> signal = np.full(5, 1.0)
        >>> oa(1, 5, overlap=1) @ signal
        array([5.])
        >>> signal = np.full(10, 1.0)
        >>> oa(2, 5, overlap=1) @ signal
        array([1., 2., 2., 2., 2., 1.])
    """
    if L <= 0:
        raise ValueError("L is strictly positive.")
    if X <= 0:
        raise ValueError("X is strictly positive.")
    if overlap < 0 or overlap > L:
        raise ValueError("overlap must be > 0 and <= L.")
    M = L * X - (X - 1) * overlap
    def _matmat(x):
        if x.ndim == 1:
            x_is_1d = True
            x = np.reshape(x, newshape=(x.size, 1))
        else:
            x_is_1d = False
        y = np.full((M, x.shape[1]), 0.0 * x[0, 0], dtype=x.dtype)
        y[:L, :] = x[:L, :]
        offset = L - overlap
        for i in range(X - 1):
            y[offset:(offset + L), :] += x[((i + 1) * L):((i + 2) * L), :]
            offset += L - overlap
        return y.ravel() if x_is_1d else y
    def _rmatmat(x):
        if x.ndim == 1:
            x_is_1d = True
            x = np.reshape(x, newshape=(x.size, 1))
        else:
            x_is_1d = False
        y = np.full((X * L, x.shape[1]), 0.0 * x[0, 0], dtype=x.dtype)
        for i in range(X):
            y[(i * L):((i + 1) * L), :] = x[(i * (L - overlap)):(i * (L - overlap) + L), :]
        return y.ravel() if x_is_1d else y
    return LazyLinearOp(
        (M, X * L),
        matmat=lambda x: _matmat(x),
        rmatmat=lambda x: _rmatmat(x)
    )


def fft2(shape, backend='scipy', **kwargs):
    """Returns a LazyLinearOp for the 2D DFT of size n.

    Args:
        shape:
             the signal shape to apply the fft2 to.
        backend:
             'scipy' (default) or 'pyfaust' for the underlying computation of the 2D DFT.
        kwargs:
             any key-value pair arguments to pass to the scipy or pyfaust dft backend
                (https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft2.html,
                https://faustgrp.gitlabpages.inria.fr/faust/last-doc/html/namespacepyfaust.html#a2695e35f9c270e8cb6b28b9b40458600).

    Example:

        >>> from lazylinop.wip.signal import fft2
        >>> import numpy as np
        >>> F_scipy = fft2((32, 32), norm='ortho')
        >>> F_pyfaust = fft2((32, 32), backend='pyfaust')
        >>> x = np.random.rand(32, 32)
        >>> np.allclose(F_scipy @ x.ravel(), F_pyfaust @ x.ravel())
        True
        >>> y = F_scipy @ x.ravel()
        >>> np.allclose(F_scipy.H @ y, x.ravel())
        True
        >>> np.allclose(F_pyfaust.H @ y, x.ravel())
        True
    """
    s = shape[0] * shape[1]
    if backend == 'scipy':
        from scipy.fft import fft2, ifft2
        return LazyLinearOp(
            shape=(s, s),
            matvec=lambda x: fft2(x.reshape(shape), **kwargs).ravel(),
            rmatvec=lambda x: ifft2(x.reshape(shape), **kwargs).ravel()
        )
    elif backend == 'pyfaust':
        from pyfaust import dft
        K = kron(dft(shape[0], **kwargs), dft(shape[1], **kwargs))
        return LazyLinearOp(
            shape=(s, s),
            matvec=lambda x: K @ x,
            rmatvec=lambda x: K.H @ x
        )
    else:
        raise ValueError('backend '+str(backend)+' is unknown')


def _is_power_of_two(n: int) -> bool:
    """return True if integer 'n' is a power of two.

    Args:
        n: int

    Returns:
        bool
    """
    return ((n & (n - 1)) == 0) and n > 0


def anti_identity(n: int, dtype='float'):
    """Constructs anti identity as lazy linear operator.

    Args:
        n: int
        Size of the matrix
        dtype: 'str' or numpy dtype
            Defaulty float.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n has to be >= 2.

    Examples:
        >>> from lazylinop.wip.signal import anti_identity
        >>> import numpy as np
        >>> x = np.arange(3)
        >>> x
        array([0, 1, 2])
        >>> Op = anti_identity(3)
        >>> np.allclose(Op @ x, np.flipud(x))
        True
    """
    if n < 2:
        raise ValueError("n has to be >= 2.")

    def _matmat(x):
        out_dtype = binary_dtype(dtype, x.dtype)
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        y = x[::-1, :]
        y = y.astype(out_dtype)
        # batch_size = x.shape[1]
        # y = np.empty((n, batch_size), dtype=x.dtype)
        # for b in range(batch_size):
        #     y[:n, b] = x[::-1, b]
        return y.ravel() if is_1d else y

    return LazyLinearOp(
        shape=(n, n),
        matmat=lambda x: _matmat(x),
        rmatmat=lambda x: _matmat(x),
        dtype=dtype
    )


def bc(L: int, n: int=1, bn: int=0, an: int=0, boundary: str='periodic'):
    """Constructs a periodic or symmetric boundary condition lazy linear operator.
    If you apply the operator to a 2d array, it will work
    on each column and returns a 2d array.
    Symmetric boundary condition is something like:
    xN, ..., x2, x1 | x1, x2, ..., xN | xN, ..., x2, x1
    while a periodic boundary condition is something like:
    x1, x2, ..., xN | x1, x2, ..., xN | x1, x2, ..., xN

    Args:
        L: int
        Size of the input
        n: int, optional
        Duplicate signal this number of times on both side
        bn: int, optional
        Add this number of elements before
        an: int, optional
        Add this number of elements after
        boundary: str, optional
        wrap/periodic (default) or symm/symmetric boundary condition

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n must be >= 0.
        ValueError
            an must be <= L.
        ValueError
            bn must be <= L.
        ValueError
            boundary excepts 'wrap', 'periodic', 'symm' or 'symmetric'.

    Examples:
        >>> from lazylinop.wip.signal import bc
        >>> import numpy as np
        >>> x = np.arange(3)
        >>> x
        array([0, 1, 2])
        >>> Op = bc(x.shape[0], n=1, bn=0, an=0, boundary='periodic')
        >>> Op @ x
        array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        >>> Op = bc(x.shape[0], n=1, bn=0, an=0, boundary='symmetric')
        >>> Op @ x
        array([2, 1, 0, 0, 1, 2, 2, 1, 0])
        >>> X = np.array([[0, 0], [1, 1], [2, 2]])
        array([[0, 0],
               [1, 1],
               [2, 2]])
        >>> Op @ X
        array([[2, 2],
               [1, 1],
               [0, 0],
               [0, 0],
               [1, 1],
               [2, 2],
               [2, 2],
               [1, 1],
               [0, 0]])
    """
    if n < 0:
        raise ValueError("n must be >= 0.")
    if bn > L:
        raise ValueError("bn must be <= L.")
    if an > L:
        raise ValueError("an must be <= L.")

    if boundary == 'symmetric' or boundary == 'symm':
        if (n % 2) == 0:
            Op = eye(L, n=L, k=0)
            flip = True
        else:
            Op = anti_identity(L) @ eye(L, n=L, k=0)
            flip = False
        for i in range(1, n + 1 + n):
            if flip:
                Op = vstack((Op, anti_identity(L) @ eye(L, n=L, k=0)))
                flip = False
            else:
                Op = vstack((Op, eye(L, n=L, k=0)))
                flip = True
        if bn > 0:
            if (n % 2) == 0:
                # flip
                Op = vstack((eye(bn, n=L, k=L - bn) @ anti_identity(L), Op))
            else:
                # do not flip
                Op = vstack((eye(bn, n=L, k=L - bn), Op))
        if an > 0:
            if (n % 2) == 0:
                # flip
                Op = vstack((Op, eye(an, n=L, k=0) @ anti_identity(L)))
            else:
                # do not flip
                Op = vstack((Op, eye(an, n=L, k=0)))
        return Op
    elif boundary == 'periodic' or boundary == 'wrap':
        Op = eye(L, n=L, k=0)
        for i in range(n + n):
            Op = vstack((Op, eye(L, n=L, k=0)))
        if bn > 0:
            Op = vstack((eye(bn, n=L, k=L - bn), Op))
        if an > 0:
            Op = vstack((Op, eye(an, n=L, k=0)))
        return Op
    else:
        raise ValueError("boundary is either 'periodic' ('wrap') or 'symmetric' (symm).")


def bc2d(shape: tuple, x: int=1, y: int=1, ax: int=0, ay: int=0, boundary: str='periodic'):
    """Constructs a periodic or symmetric boundary condition lazy linear operator.
    It will be applied to a flattened image.
    It basically add image on bottom, left, top and right side.
    Symmetric boundary condition is something like (on both axis):
    xN, ..., x2, x1 | x1, x2, ..., xN | xN, ..., x2, x1
    while a periodic boundary condition is something like (on both axis):
    x1, x2, ..., xN | x1, x2, ..., xN | x1, x2, ..., xN

    Args:
        shape: tuple
        Shape of the image
        x: int, optional
        2 * x + 1 signals along the first axis
        y: int, optional
        2 * y + 1 signals along the second axis
        ax: int, optional
        Add ax lines after.
        ay: int, optional
        Add ay lines after.
        boundary: str, optional
        wrap/periodic (default) or symm/symmetric boundary condition

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            x and y must be >= 0.
        ValueError
            shape expects tuple (R, C).
        ValueError
            ax (resp. ay) must be < shape[0] (resp. shape[1]).
        ValueError
            boundary excepts 'wrap', 'periodic', 'symm' or 'symmetric'.

    Examples:
        >>> from lazylinop.wip.signal import fbc2d
        >>> import numpy as np
        >>> X = np.arange(4).reshape(2, 2)
        >>> X
        array([[0, 1],
               [2, 3]])
        >>> Op = fbc2d(X.shape, x=1, y=1, ax=1, ay=1, boundary='periodic')
        >>> (Op @ X.ravel()).reshape(2 * 2 + 1, 2 * 2 + 1)
        array([[0, 1, 0, 1, 0],
               [2, 3, 2, 3, 2],
               [0, 1, 0, 1, 0],
               [2, 3, 2, 3, 2],
               [0, 1, 0, 1, 0]])
        >>> X = np.arange(6).reshape(3, 2)
        >>> X
        array([[0, 1],
               [2, 3],
               [4, 5]])
        >>> Op = fbc2d(X.shape, x=1, y=0, ax=2, ay=1, boundary='symmetric')
        >>> (Op @ X.ravel()).reshape(2 * 3 + 2, 2 + 1)
        array([[0, 1, 1],
              [2, 3, 3],
              [4, 5, 5],
              [4, 5, 5],
              [2, 3, 3],
              [0, 1, 1],
              [0, 1, 1],
              [2, 3, 3]])
    """
    if x < 0 or y < 0:
        raise ValueError("x and y must be >= 0.")
    if ax >= shape[0] or ay >= shape[1]:
        raise ValueError("ax (resp. ay) must be < shape[0] (resp. shape[1]).")
    if len(shape) != 2:
        raise ValueError("shape expects tuple (R, C).")

    # Use bc and kron lazy linear operators to write bc2d
    # Kronecker product trick: A @ X @ B^T = kron(A, B) @ vec(X)
    Op = kron(bc(shape[0], n=x, bn=ax, an=ax, boundary=boundary),
              bc(shape[1], n=y, bn=ay, an=ay, boundary=boundary))
    return Op


def dwt1d(N: int, wavelet: pywt.Wavelet=pywt.Wavelet("haar"), mode: str='zero', level: int=None, **kwargs):
    """Constructs a Discrete Wavelet Transform (DWT) lazy linear operator.
    For the first level of decomposition Op @ 1d array returns the array [cA, cD].
    For the nth level of decomposition Op @ 1d array returns the array [cAn, cDn, cDn-1, ..., cD2, cD1].
    The 1d array of coefficients corresponds to the concatenation of the list of arrays Pywavelets returns.
    Of note, the function follows the format returned by Pywavelets module.

    Args:
        N: int
        Size of the input array
        wavelet: pywt.Wavelet
        Wavelet from Pywavelets module, see `pywt.wavelist() <https://pywavelets.readthedocs.io/en/latest/regression/wavelet.html>`_ for more details.
        mode: str, optional
        'periodic', signal is treated as periodic signal
        'symmetric', use mirroring to pad the signal
        'zero', signal is padded with zeros (default)
        See `Pywavelets documentation <https://pywavelets.readthedocs.io/en/latest/ref/signal-extension-modes.html>`_ for more details
        level: int, optional
        Decomposition level, by default (None) return all
        kwargs:
        lfilter: np.ndarray
        Quadrature mirror low-pass filter.
        The function uses `scipy.signal.qmf <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.qmf.html>`_ to build high-pass filter.

    Returns:
        The DWT LazyLinearOp.

    Raises:
        ValueError
            Decomposition level must be greater or equal to 1.
        ValueError
            mode is either 'periodic', 'symmetric' or 'zero'.
        ValueError
            level is greater than the maximum decomposition level.

    Examples:
        >>> from lazylinop.wip.signal import dwt1d
        >>> import numpy as np
        >>> import pywt
        >>> x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        >>> Op = dwt1d(x.shape[0], wavelet=pywt.Wavelet('haar'), mode='periodic', level=1)
        >>> Op @ x
        array([ 2.12132034,  4.94974747,  7.77817459, 10.60660172, -0.70710678,
                -0.70710678, -0.70710678, -0.70710678])
        >>> pywt.wavedec(x, wavelet='haar', mode='periodic', level=1)
        [array([ 2.12132034,  4.94974747,  7.77817459, 10.60660172]), array([-0.70710678, -0.70710678, -0.70710678, -0.70710678])]        
        >>> np.concatenate(pywt.wavedec(x, wavelet='haar', mode='periodic', level=1))
        array([ 2.12132034,  4.94974747,  7.77817459, 10.60660172, -0.70710678,
                -0.70710678, -0.70710678, -0.70710678])

    References:
        See also `Pywavelets module <https://pywavelets.readthedocs.io/en/latest/index.html>`_
    """
    if level is not None and level < 1:
        raise ValueError("Decomposition level must be greater or equal to 1.")
    if not mode in ['zero', 'symmetric', 'periodic']:
        raise ValueError("mode is either 'periodic', 'symmetric' or 'zero'.")

    # Build high-pass filter using scipy.signal.qmf
    if 'lfilter' in kwargs.keys():
        lfilter = kwargs['lfilter']
        hfilter = sp.signal.qmf(lfilter)
        wavelet_name = 'unknown'
    else:
        lfilter = np.asarray(wavelet.dec_lo)
        hfilter = np.asarray(wavelet.dec_hi)
        wavelet_name = wavelet.name
    W = hfilter.shape[0]
    if W > N:
        # Nothing to decompose, return identity matrix
        return eye(N, n=N, k=0)

    boffset = bool(wavelet_name == 'bior3.1' or
                   wavelet_name == 'bior3.3' or
                   wavelet_name == 'bior3.5' or
                   wavelet_name == 'bior3.7' or
                   wavelet_name == 'bior3.9' or
                   wavelet_name == 'bior5.5' or
                   wavelet_name == 'coif2' or
                   wavelet_name == 'coif4' or
                   wavelet_name == 'coif6' or
                   wavelet_name == 'coif8' or
                   wavelet_name == 'coif10' or
                   wavelet_name == 'coif12' or
                   wavelet_name == 'coif14' or
                   wavelet_name == 'coif16' or
                   wavelet_name == 'db2' or
                   wavelet_name == 'db4' or
                   wavelet_name == 'db6' or
                   wavelet_name == 'db8' or
                   wavelet_name == 'db10' or
                   wavelet_name == 'db12' or
                   wavelet_name == 'db14' or
                   wavelet_name == 'db16' or
                   wavelet_name == 'db18' or
                   wavelet_name == 'db20' or
                   wavelet_name == 'db22' or
                   wavelet_name == 'db24' or
                   wavelet_name == 'db26' or
                   wavelet_name == 'db28' or
                   wavelet_name == 'db30' or
                   wavelet_name == 'db32' or
                   wavelet_name == 'db34' or
                   wavelet_name == 'db36' or
                   wavelet_name == 'db38' or
                   wavelet_name == 'rbio3.1' or
                   wavelet_name == 'rbio3.3' or
                   wavelet_name == 'rbio3.5' or
                   wavelet_name == 'rbio3.7' or
                   wavelet_name == 'rbio3.9' or
                   wavelet_name == 'rbio5.5' or
                   wavelet_name == 'sym2' or
                   wavelet_name == 'sym4' or
                   wavelet_name == 'sym6' or
                   wavelet_name == 'sym8' or
                   wavelet_name == 'sym10' or
                   wavelet_name == 'sym12' or
                   wavelet_name == 'sym14' or
                   wavelet_name == 'sym16' or
                   wavelet_name == 'sym18' or
                   wavelet_name == 'sym20')

    # Maximum decomposition level: stop decomposition when
    # the signal becomes shorter than the filter length
    K = int(np.log2(N / (W - 1)))
    if level is not None and level > K:
        raise ValueError("level is greater than the maximum decomposition level.")
    D = K if level is None else level

    if D == 0:
        # Nothing to decompose, return identity matrix
        return eye(N, n=N, k=0)

    # Loop over the decomposition level
    for i in range(D):
        # Low and high-pass filters + decimation
        npd = W - 2
        if i == 0:
            # Boundary conditions
            O = N + 2 * npd
            if mode == 'zero':
                O += O % 2
                B = eye(O, n=N, k=-npd)
            else:
                mx = O % 2
                bn = npd
                an = npd + mx
                O += mx
                B = bc(N, n=0, bn=bn, an=an, boundary=mode)
        else:
            # Boundary conditions
            O = cx + 2 * npd
            if mode == 'zero':
                O += O % 2
                B = eye(O, n=cx, k=-npd)
            else:
                mx = O % 2
                bn = npd
                an = npd + mx
                O += mx
                B = bc(cx, n=0, bn=bn, an=an, boundary=mode)
        G = convolve((O, ), lfilter, mode='same', method='lazylinop.scipy.signal.convolve') @ B
        H = convolve((O, ), hfilter, mode='same', method='lazylinop.scipy.signal.convolve') @ B
        offset_d = int((npd % 2) == 0) if mode == 'zero' else int((bn % 2) == 0)
        if boffset:
            offset_d = 0
        DG = decimate(G.shape, offset_d, None, 2)
        DH = decimate(H.shape, offset_d, None, 2)
        # Vertical stack
        GH = vstack((DG @ G, DH @ H))
        # Extract approximation and details coefficients cA, cD
        cx = ((N if i == 0 else cx) + W - 1) // 2
        offset = (O // 2 - cx) // 2
        if boffset:
            offset += 1
        # Slices to extract cA
        cA = mslices(GH.shape, [offset], [offset + cx - 1])
        # Slices to extract cD
        cD = mslices(GH.shape, [offset + O // 2], [offset + O // 2 + cx - 1])
        V = vstack((cA, cD))
        if i == 0:
            # First level of decomposition
            Op = V @ GH
        else:
            # Apply low and high-pass filters + decimation only to cA
            # Because of lazy linear operator V, cA always comes first
            tmpV = V @ GH
            tmp_eye = eye(Op.shape[0] - tmpV.shape[1], n=Op.shape[0] - tmpV.shape[1], k=0)
            Op = block_diag(*[tmpV, tmp_eye]) @ Op
    # return LazyLinearOp(
    #     shape=Op.shape,
    #     matvec=lambda x: Op @ x,
    #     rmatvec=lambda x: Op.H @ x
    # )
    return Op


def dwt2d(shape: tuple, wavelet: pywt.Wavelet=pywt.Wavelet("haar"), mode: str='zero', level: int=None, **kwargs):
    """Constructs a multiple levels 2d DWT lazy linear operator.
    If the lazy linear operator is applied to a 1d array it returns the array [cA, cH, cV, cD]
    for the first decomposition level. For the nth level of decomposition it returns
    the array [cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1]. The 1d array of coefficients corresponds
    to the concatenation of the list of arrays Pywavelets returns.

    Args:
        shape: tuple
        Shape of the input array (X, Y)
        wavelet: pywt.Wavelet
        Wavelet from Pywavelets module, see `pywt.wavelist() <https://pywavelets.readthedocs.io/en/latest/regression/wavelet.html>`_ for more details.
        mode: str, optional
        'periodic', image is treated as periodic image
        'symmetric', use mirroring to pad the signal
        'zero', signal is padded with zeros (default)
        See `Pywavelets documentation <https://pywavelets.readthedocs.io/en/latest/ref/signal-extension-modes.html>`_ for more details
        level: int, optional
        If level is None compute full decomposition (default)
        kwargs:
        lfilter: np.ndarray
        Quadrature mirror low-pass filter.
        The function uses `scipy.signal.qmf <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.qmf.html>`_ to build high-pass filter.

    Returns:
        LazyLinearOp

    Raises:
        Exception
            Shape expects tuple.
        ValueError
            Decomposition level must greater or equal to 1.
        ValueError
            Decomposition level is greater than the maximum decomposition level.
        ValueError
            mode is either 'zero', 'periodic' or 'symmetric'.

    Examples:
        >>> from lazylinop.wip.signal import dwt2d
        >>> import numpy as np
        >>> import pywt
        >>> X = np.arange(1, 5).reshape(2, 2)
        >>> Op = dwt2d(X.shape, wavelet=pywt.Wavelet('haar'), mode='periodic', level=1)
        >>> Op @ X
        array([ 5, -2, -1,  0])        
        >>> cA, (cH, cV, cD) = pywt.wavedec2(X, wavelet='haar', mode='periodic', level=1)
        >>> np.concatenate([cA, cH, cV, cD], axis=1)
        array([[ 5., -2., -1.,  0.]])

    References:
        See also `Pywavelets module <https://pywavelets.readthedocs.io/en/latest/ref/2d-dwt-and-idwt.html#ref-dwt2>`_
    """
    if not type(shape) is tuple:
        raise ValueError("Shape expects tuple.")
    if not level is None and level < 1:
        raise ValueError("Decomposition level must be greater or equal to 1.")

    # Image has been flattened (with img.flatten(order='C'))
    # The result is vec = (row1, row2, ..., rowR) with size = X * Y
    X, Y = shape[0], shape[1]

    # Build high-pass filter using scipy.signal.qmf
    if 'lfilter' in kwargs.keys():
        lfilter = kwargs['lfilter']
        hfilter = sp.signal.qmf(lfilter)
        wavelet_name = 'unknown'
    else:
        lfilter = np.asarray(wavelet.dec_lo)
        hfilter = np.asarray(wavelet.dec_hi)
        wavelet_name = wavelet.name
    W = hfilter.shape[0]

    if W > X or W > Y:
        # Nothing to decompose, return identity matrix
        return eye(X * Y, n=X * Y, k=0)

    boffset = bool(wavelet_name == 'bior3.1' or
                   wavelet_name == 'bior3.3' or
                   wavelet_name == 'bior3.5' or
                   wavelet_name == 'bior3.7' or
                   wavelet_name == 'bior3.9' or
                   wavelet_name == 'bior5.5' or
                   wavelet_name == 'coif2' or
                   wavelet_name == 'coif4' or
                   wavelet_name == 'coif6' or
                   wavelet_name == 'coif8' or
                   wavelet_name == 'coif10' or
                   wavelet_name == 'coif12' or
                   wavelet_name == 'coif14' or
                   wavelet_name == 'coif16' or
                   wavelet_name == 'db2' or
                   wavelet_name == 'db4' or
                   wavelet_name == 'db6' or
                   wavelet_name == 'db8' or
                   wavelet_name == 'db10' or
                   wavelet_name == 'db12' or
                   wavelet_name == 'db14' or
                   wavelet_name == 'db16' or
                   wavelet_name == 'db18' or
                   wavelet_name == 'db20' or
                   wavelet_name == 'db22' or
                   wavelet_name == 'db24' or
                   wavelet_name == 'db26' or
                   wavelet_name == 'db28' or
                   wavelet_name == 'db30' or
                   wavelet_name == 'db32' or
                   wavelet_name == 'db34' or
                   wavelet_name == 'db36' or
                   wavelet_name == 'db38' or
                   wavelet_name == 'rbio3.1' or
                   wavelet_name == 'rbio3.3' or
                   wavelet_name == 'rbio3.5' or
                   wavelet_name == 'rbio3.7' or
                   wavelet_name == 'rbio3.9' or
                   wavelet_name == 'rbio5.5' or
                   wavelet_name == 'sym2' or
                   wavelet_name == 'sym4' or
                   wavelet_name == 'sym6' or
                   wavelet_name == 'sym8' or
                   wavelet_name == 'sym10' or
                   wavelet_name == 'sym12' or
                   wavelet_name == 'sym14' or
                   wavelet_name == 'sym16' or
                   wavelet_name == 'sym18' or
                   wavelet_name == 'sym20')

    # Stop decomposition when the signal becomes
    # shorter than the filter length
    K = min(int(np.log2(X / (W - 1))), int(np.log2(Y / (W - 1))))
    if level is not None and level > K:
        raise ValueError("Decomposition level is greater than the maximum decomposition level.")
    D = K if level is None else min(K, level)
    if D == 0:
        # Nothing to decompose, return identity matrix
        return eye(X * Y, n=X * Y, k=0)

    # Loop over the decomposition level
    for i in range(D):
        # Low and high-pass filters + decimation
        # Boundary conditions
        npd = W - 2
        tmp_x = X if i == 0 else cx
        tmp_y = Y if i == 0 else cy
        Fx = tmp_x + 2 * npd
        Fy = tmp_y + 2 * npd
        if mode == 'zero':
            Fx += Fx % 2
            Fy += Fy % 2
            Ax = eye(Fx, n=tmp_x, k=-npd)
            Ay = eye(Fy, n=tmp_y, k=-npd)
        else:
            mx = Fx % 2
            bx = npd
            ax = npd + mx
            Fx += mx
            my = Fy % 2
            by = npd
            ay = npd + my
            Fy += my
            Ax = bc(tmp_x, n=0, bn=bx, an=ax, boundary=mode)
            Ay = bc(tmp_y, n=0, bn=by, an=ay, boundary=mode)
        # First work on the row ...
        # ... and then work on the column (use Kronecker product vec trick)
        # Convolution
        method = 'lazylinop.scipy.signal.convolve'
        GX = convolve((Fx, ), lfilter, mode='same', method=method) @ Ax
        GY = convolve((Fy, ), lfilter, mode='same', method=method) @ Ay
        HX = convolve((Fx, ), hfilter, mode='same', method=method) @ Ax
        HY = convolve((Fy, ), hfilter, mode='same', method=method) @ Ay
        offset_x = int((npd % 2) == 0) if mode == 'zero' else int((bx % 2) == 0)
        offset_y = int((npd % 2) == 0) if mode == 'zero' else int((by % 2) == 0)
        if boffset:
            offset_x, offset_y = 0, 0
        if 0:
            # Down-sampling, convolution and vertical stack
            GX = dsconvolve((Fx, ), lfilter, mode='same', offset=offset_x, every=2) @ Ax
            GY = dsconvolve((Fy, ), lfilter, mode='same', offset=offset_y, every=2) @ Ay
            HX = dsconvolve((Fx, ), hfilter, mode='same', offset=offset_x, every=2) @ Ax
            HY = dsconvolve((Fy, ), hfilter, mode='same', offset=offset_y, every=2) @ Ay
            VX = vstack((GX, HX))
            VY = vstack((GY, HY))
        else:
            # Down-sampling
            DX = decimate(GX.shape, offset_x, None, 2)
            DY = decimate(GY.shape, offset_y, None, 2)
            # Vertical stack
            VX = vstack((DX @ GX, DX @ HX))
            VY = vstack((DY @ GY, DY @ HY))
        # Because we work on the rows and then on the columns,
        # we can write a Kronecker product that will be applied to the flatten image
        KGH = kron(VX, VY)
        # Extract four sub-images (use mslices operator)
        # ---------------------
        # | LL (cA) | LH (cH) |
        # ---------------------
        # | HL (cV) | HH (cD) |
        # ---------------------
        cx = ((X if i == 0 else cx) + W - 1) // 2
        cy = ((Y if i == 0 else cy) + W - 1) // 2
        # Slices to extract detail, vertical and horizontal coefficients and
        # fill the following list of coefficients [cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1]
        offset_x = (Fx // 2 - cx) // 2
        offset_y = (Fy // 2 - cy) // 2
        if boffset:
            offset_x += 1
            offset_y += 1
        # Slices to extract sub-image LL
        seq = np.arange(offset_x, offset_x + cx)
        start = seq * Fy + offset_y
        # for j in range(offset_x, offset_x + cx):
        #     start[j - offset_x] = j * Fy + offset_y
        end = np.add(start, cy - 1)
        LL = mslices(KGH.shape, start, end)
        # Slices to extract sub-image LH
        LH = mslices(KGH.shape, np.add(start, Fy // 2), np.add(end, Fy // 2))
        # Slices to extract sub-image HL
        seq = np.arange(Fx // 2 + offset_x, Fx // 2 + offset_x + cx, 1)
        start = seq * Fy + offset_y
        # for j in range(Fx // 2 + offset_x, Fx // 2 + offset_x + cx):
        #     start[j - (Fx // 2 + offset_x)] = j * Fy + offset_y
        end = np.add(start, cy - 1)
        HL = mslices(KGH.shape, start, end)
        # Slices to extract sub-image HH
        HH = mslices(KGH.shape, np.add(start, Fy // 2), np.add(end, Fy // 2))
        # Vertical stack where LL is the first lazy linear operator
        # ----
        # |LL|
        # ----
        # |LH|
        # ----
        # |HL|
        # ----
        # |HH|
        # ----
        V = vstack((vstack((LL, HL)), vstack((LH, HH))))
        if i == 0:
            # First level of decomposition
            A = V @ KGH
        else:
            # Apply low and high-pass filters + decimation only to LL
            # Because of lazy linear operator V, LL always comes first
            tmpA = V @ KGH
            tmp_eye = eye(A.shape[0] - tmpA.shape[1], n=A.shape[0] - tmpA.shape[1], k=0)
            A = block_diag(*[tmpA, tmp_eye]) @ A
    # return LazyLinearOp(
    #     shape=A.shape,
    #     matvec=lambda x: A @ x,
    #     rmatvec=lambda x: A.H @ x,
    #     matmat=lambda X: A @ X,
    #     rmatmat=lambda X: A.H @ X
    # )
    return A


def convolve2d(in1, in2: np.ndarray, mode: str = 'full', boundary: str = 'fill', method: str = 'auto', **kwargs):
    """Constructs a 2d convolution lazy linear operator.
    If shape of the image has been passed return Lazy Linear Operator.
    If image has been passed return the convolution result.
    Toeplitz based method use the fact that convolution of a kernel with an image
    can be written as a sum of Kronecker product between eye and Toeplitz matrices.

    Args:
        in1: tuple or np.ndarray,
        Shape (tuple) of the signal or input array (np.ndarray)
        to convolve with kernel. Shape is (X, Y).
        in2: np.ndarray
        Kernel to use for the convolution, shape is (K, L)
        mode: str, optional
        'full' computes convolution (input + padding)
        'valid' computes 'full' mode and extract centered output that does not depend on the padding. 
        'same' computes 'full' mode and extract centered output that has the same shape that the input.
        See also Scipy documentation of scipy.signal.convolve function for more details
        boundary: str, optional
        'fill' pads input array with zeros (default)
        'wrap' periodic boundary conditions
        'symm' symmetrical boundary conditions
        See also Scipy documentation of scipy.signal.convolve2d function
        method: str, optional
        'auto' to use the best method according to the kernel and input array dimensions
        'direct' to use nested loops (brute force). It works with Numba decorators and prange.
        Therefore, it is useful only for large input.
        'lazy.scipy' use scipy.signal.convolve2d as a lazy linear operator
        'scipy.linalg.toeplitz' to use lazy encapsulation of Scipy implementation of Toeplitz matrix
        'pyfaust.toeplitz' to use pyfaust implementation of Toeplitz matrix
        'fft.scipy' to use Fast-Fourier-Transform to compute convolution

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        ValueError
            mode is either 'full' (default), 'valid' or 'same'.
        ValueError
            boundary is either 'fill' (default), 'wrap' or 'symm'
        ValueError
            Size of the kernel is greater than the size of signal.
        ValueError
            Unknown method.
        Exception
            in1 expects tuple as (X, Y).
        Exception
            in1 expects array with shape (X, Y).
        ValueError
            Negative dimension value is not allowed.

    Examples:
        >>> from lazylinop.wip.signal import convolve2d
        >>> import scipy as sp
        >>> image = np.random.rand(6, 6)
        >>> kernel = np.random.rand(3, 3)
        >>> c1 = convolve2d(image, kernel, mode='same', boundary='fill', method='scipy.linalg.toeplitz')
        >>> c2 = convolve2d(image, kernel, mode='same', boundary='fill', method='pyfaust.toeplitz')
        >>> c3 = convolve2d(image.shape, kernel, mode='same', boundary='fill', method='direct') @ image.flatten()
        >>> c4 = sp.signal.convolve2d(image, kernel, mode='same', boundary='fill')
        >>> np.allclose(c1, c2)
        True
        >>> np.allclose(c2, c3)
        True
        >>> np.allclose(c3, c4)
        True

    References:
        See also `scipy.signal.convolve2d <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve2d.html>`_
    """
    if not boundary in ['fill', 'wrap', 'symm']:
        raise ValueError("boundary is either 'fill' (default), 'wrap' or 'symm'")

    # check if image has been passed to the function
    # check if shape of the image has been passed to the function
    return_lazylinop = type(in1) is tuple

    if type(in1) is tuple:
        return_laylinop = True
        if len(in1) != 2:
            raise Exception("in1 expects tuple (X, Y).")
        X, Y = in1[0], in1[1]
    else:
        return_lazylinop = False
        if len(in1.shape) != 2:
            raise Exception("in1 expects array with shape (X, Y).")
        X, Y = in1.shape

    if X <= 0 or Y <= 0:
        raise ValueError("zero or negative dimension is not allowed.")
    K, L = in2.shape
    if K > X or L > Y:
        raise ValueError("Size of the kernel is greater than the size of the image.")
    if X <= 0 or Y <= 0 or K <= 0 or L <= 0:
        raise ValueError("Negative dimension value is not allowed.")

    if method == 'auto' and max(K, L) > 32:
        compute = 'fft.scipy'
    elif method == 'auto' and max(K, L) <= 32:
        compute = 'fft.scipy'#'direct'
    else:
        compute = method

    # if compute == 'direct' and (boundary == 'wrap' or boundary == 'symm'):
    #     raise Exception("direct method has no implemention of wrap and symm boundaries.")
    if compute == 'lazy.scipy' and (boundary == 'wrap' or boundary == 'symm'):
        raise Exception("lazy.scipy method has no implementation of wrap and symm boundaries.")

    # boundary conditions
    if boundary == 'fill' or compute == 'lazy.scipy':# or compute == 'direct':
        # if compute is lazy.scipy use boundary argument of SciPy function
        # if compute is direct use boundary conditions for the indices
        B = 1
    else:
        # add one input on both side of each axis
        B = 3

    # shape of the output image (full mode)
    # it takes into account the boundary conditions
    P, Q = B * X + K - 1, B * Y + L - 1

    # length of the output as a function of convolution mode
    xdim = {}
    xdim['full'] = B * X + K - 1
    xdim['valid'] = B * X - K + 1
    xdim['same'] = B * X
    ydim = {}
    ydim['full'] = B * Y + L - 1
    ydim['valid'] = B * Y - L + 1
    ydim['same'] = B * Y
    xdims = np.array([B * X + K - 1, B * X - K + 1, B * X, B * X], dtype=np.int_)
    ydims = np.array([B * Y + L - 1, B * Y - L + 1, B * Y, B * Y], dtype=np.int_)
    imode = 0 * int(mode == 'full') + 1 * int(mode == 'valid') + 2 * int(mode == 'same') + 3 * int(mode == 'circ')
    rmode = {}
    rmode['full'] = 'valid'
    rmode['valid'] = 'full'
    rmode['same'] = 'same'
    xy = {}
    xy['full'] = (X + K - 1) * (Y + L - 1)
    xy['valid'] = (X - K + 1) * (Y - L + 1)
    xy['same'] = X * Y

    if mode == 'full':
        i1 = (P - (X + K - 1)) // 2
        s1 = i1 + X + K - 1
        i2 = (Q - (Y + L - 1)) // 2
        s2 = i2 + Y + L - 1
    elif mode == 'valid':
        # compute full mode and extract what we need
        # number of rows to extract is X - K + 1 (centered)
        # number of columns to extract is Y - L + 1 (centered)
        # if boundary conditions extract image from the center
        i1 = (P - (X - K + 1)) // 2
        s1 = i1 + X - K + 1
        i2 = (Q - (Y - L + 1)) // 2
        s2 = i2 + Y - L + 1
    elif mode == 'same':
        # keep middle of the full mode
        # number of rows to extract is M (centered)
        # number of columns to extract is N (centered)
        # if boundary conditions extract image from the center
        i1 = (P - X) // 2
        s1 = i1 + X
        i2 = (Q - Y) // 2
        s2 = i2 + Y
    else:
        raise ValueError("mode is either 'full' (default), 'valid' or 'same'.")

    if compute == 'lazy.scipy':
        # correlate2d is the adjoint operator of convolve2d
        def _matmat(x):
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            # use Dask ?
            y = np.empty((xdim[mode] * ydim[mode], batch_size), dtype=(x[0, 0] * in2[0, 0]).dtype)
            for b in range(batch_size):
                y[:, b] = sp.signal.convolve2d(
                    x[:, b].reshape(xdim['same'], ydim['same']), in2, mode=mode, boundary=boundary).ravel()
            return y.ravel() if is_1d else y
        def _rmatmat(x):
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            # use Dask ?
            y = np.empty((xdim['same'] * ydim['same'], batch_size), dtype=(x[0, 0] * in2[0, 0]).dtype)
            for b in range(batch_size):
                y[:, b] = sp.signal.correlate2d(
                    x[:, b].reshape(xdim[mode], ydim[mode]), in2, mode=rmode[mode], boundary=boundary).ravel()
            return y.ravel() if is_1d else y
        C = LazyLinearOp(
            shape=(xdim[mode] * ydim[mode], xdim['same'] * ydim['same']),
            matmat=lambda x: _matmat(x),
            rmatmat=lambda x: _rmatmat(x)
        )
    elif compute == 'fft.scipy':
        if compute == 'dft.pyfaust':
            from lazylinop.wip.signal import fft2
            F = fft2((P, Q), backend='pyfaust', normed=True, diag_opt=True)
        elif compute == 'fft.scipy':
            from lazylinop.wip.signal import fft2
            F = fft2((P, Q), backend='scipy', norm='ortho')
        else:
            raise ValueError('Unknown backend')

        # operator to pad both flattened kernel and input according to convolution mode
        # scipy.signal.convolve2d adds 0 only on one side along both axis
        # input
        x1 = 0
        x2 = xdim['full'] - xdim['same'] - x1
        y1 = 0
        y2 = ydim['full'] - ydim['same'] - y1
        P1 = pad((xdim['same'], ydim['same']), ((x1, x2), (y1, y2)))
        # kernel
        x1 = 0
        x2 = xdim['full'] - K - x1
        y1 = 0
        y2 = ydim['full'] - L - y1
        P2 = pad((K, L), ((x1, x2), (y1, y2)))

        Fin2 = np.multiply(np.sqrt(P * Q), F @ P2 @ in2.flatten())
        C = F.H @ (diag(Fin2, k=0) @ F) @ P1
        if boundary == 'wrap' or boundary == 'symm':
            C = C @ bc2d((X, Y), x=1, y=1, boundary=boundary)
        # extract center of the output
        indices = ((np.arange(P * Q).reshape(P, Q))[i1:s1, i2:s2]).ravel()
        C = C[indices, :]
    elif compute == 'direct':
        # Write 2d convolution as a sum of Kronecker products:
        # input * kernel = sum(kron(E_i, T_i), i, 1, M)
        # E_i is an eye matrix eye(P, n=X, k=-i).
        # T_i is a Toeplitz matrix build from the kernel.
        # First column is the i-th row of the kernel while first row is 0.
        # Because of Numba cache=True id it better to call
        # convolve function many times ?
        Ops = [None] * K
        for i in range(K):
            Ops[i] = kron(
                eye(xdim['full'], n=xdim['same'], k=-i),
                convolve((B * Y, ), in2[i, :], method='direct', mode='full')
            )
        C = sum(*Ops, af=False)
        # Add boundary conditions
        if boundary == 'wrap' or boundary == 'symm':
            C = C @ bc2d((X, Y), x=1, y=1, boundary=boundary)
        # Extract center of the output
        C = C[((np.arange(xdim['full'] * ydim['full']).reshape(xdim['full'], ydim['full']))[i1:s1, i2:s2]).ravel(), :]

        # use_parallel=bool((X * Y * K * L / _T) >= 1000)

        # def _matmat(shape, xx, hh, adjoint=False):
        #     # Because of Numba split 1d and 2d functions
        #     @nb.jit(nopython=True, parallel=use_parallel, cache=True)
        #     def _1d(shape, xx, hh):
        #         X, Y = shape[0], shape[1]
        #         R, S = X + K - 1, Y + L - 1
        #         dim0, dim1 = X, Y
        #         if adjoint:
        #             # compute shape of the input
        #             if xx.shape[0] == ((X + K - 1) * (Y + L - 1)):
        #                 dim0, dim1 = X + K - 1, Y + L - 1
        #             elif xx.shape[0] == ((X - K + 1) * (Y - L + 1)):
        #                 dim0, dim1 = X - K + 1, Y - L + 1
        #             else:
        #                 dim0, dim1 = X, Y
        #             if mode == 'full':
        #                 R, S = dim0 + K - 1, dim1 + L - 1
        #             elif mode == 'valid':
        #                 R, S = dim0 + K - 1, dim1 + L - 1
        #             else:
        #                 R, S = 2*dim0 + K - 1, 2*dim1 + L - 1
        #         out = np.full(R * S, 0.0 * (xx[0] * hh[0, 0]))
        #         # brute force costs ~ X * Y * K * L operations
        #         for x in prange(R):
        #             for y in range(S):
        #                 for k in range(K):
        #                     dx = x - k
        #                     if (dx < 0 or dx >= dim0) and boundary == 'fill':
        #                         continue
        #                     for l in range(L):
        #                         dy = y - l
        #                         if (dy < 0 or dy >= dim1) and boundary == 'fill':
        #                             continue
        #                         if boundary == 'wrap':
        #                             dx += dim0 * (int(dx < 0) - int(dx >= dim0))
        #                             dy += dim1 * (int(dy < 0) - int(dy >= dim1))
        #                         elif boundary == 'symm':
        #                             dx += (-2 * dx - 1) * int(dx < 0) - (dx - (dim0 - 1)) * int(dx >= dim0)
        #                             dy += (-2 * dy - 1) * int(dy < 0) - (dy - (dim1 - 1)) * int(dy >= dim1)
        #                         else:
        #                             pass
        #                         out[x * S + y] += hh[k, l] * xx[dx * dim1 + dy]
        #         ix, sx = i1, s1
        #         iy, sy = i2, s2
        #         if adjoint:
        #             ix = (R - X) // 2
        #             iy = (S - Y) // 2
        #             sx = ix + X
        #             sy = iy + Y
        #         return out[((np.arange(R * S).reshape(R, S))[ix:sx, iy:sy]).ravel()]

        #     @nb.jit(nopython=True, parallel=use_parallel, cache=True)
        #     def _2d(shape, xx, hh):
        #         batch_size = xx.shape[1]
        #         X, Y = shape[0], shape[1]
        #         R, S = X + K - 1, Y + L - 1
        #         dim0, dim1 = X, Y
        #         if adjoint:
        #             # compute shape of the input
        #             if xx.shape[0] == ((X + K - 1) * (Y + L - 1)):
        #                 dim0, dim1 = X + K - 1, Y + L - 1
        #             elif xx.shape[0] == ((X - K + 1) * (Y - L + 1)):
        #                 dim0, dim1 = X - K + 1, Y - L + 1
        #             else:
        #                 dim0, dim1 = X, Y
        #             if mode == 'full':
        #                 R, S = dim0 + K - 1, dim1 + L - 1
        #             elif mode == 'valid':
        #                 R, S = dim0 + K - 1, dim1 + L - 1
        #             else:
        #                 R, S = 2*dim0 + K - 1, 2*dim1 + L - 1
        #         out = np.full((R * S, batch_size), 0.0 * (xx[0, 0] * hh[0, 0]))
        #         # brute force costs ~ X * Y * K * L operations
        #         for x in prange(R):
        #             for b in range(batch_size):
        #                 for y in range(S):
        #                     for k in range(K):
        #                         dx = x - k
        #                         if (dx < 0 or dx >= dim0) and boundary == 'fill':
        #                             continue
        #                         for l in range(L):
        #                             dy = y - l
        #                             if (dy < 0 or dy >= dim1) and boundary == 'fill':
        #                                 continue
        #                             if boundary == 'wrap':
        #                                 dx += dim0 * (int(dx < 0) - int(dx >= dim0))
        #                                 dy += dim1 * (int(dy < 0) - int(dy >= dim1))
        #                             elif boundary == 'symm':
        #                                 dx += (-2 * dx - 1) * int(dx < 0) - (dx - (dim0 - 1)) * int(dx >= dim0)
        #                                 dy += (-2 * dy - 1) * int(dy < 0) - (dy - (dim1 - 1)) * int(dy >= dim1)
        #                             else:
        #                                 pass
        #                             out[x * S + y, b] += hh[k, l] * xx[dx * dim1 + dy, b]
        #         ix, sx = i1, s1
        #         iy, sy = i2, s2
        #         if adjoint:
        #             ix = (R - X) // 2
        #             iy = (S - Y) // 2
        #             sx = ix + X
        #             sy = iy + Y
        #         return out[((np.arange(R * S).reshape(R, S))[ix:sx, iy:sy]).ravel(), :]

        #     return _1d(shape, xx, hh) if xx.ndim == 1 else _2d(shape, xx, hh)

        # C = LazyLinearOp(
        #     shape=(xdim[mode] * ydim[mode], xy['same']),
        #     matmat=lambda x: _matmat((X, Y), x, in2, False),
        #     rmatmat=lambda x: _matmat((X, Y), x, np.conjugate(in2)[::-1, ::-1], True)
        # )
    elif compute == 'pyfaust.toeplitz' or compute == 'scipy.linalg.toeplitz':
        # write 2d convolution as a sum of Kronecker products:
        # input * kernel = sum(kron(E_i, T_i), i, 1, M)
        # E_i is an eye matrix eye(P, n=X, k=-i).
        # T_i is a Toeplitz matrix build from the kernel.
        # first column is the i-th row of the kernel.
        # first row is 0
        if compute == 'pyfaust.toeplitz':
            from pyfaust import toeplitz
        Ops = [None] * K
        for i in range(K):
            if method == 'pyfaust.toeplitz':
                Ops[i] = kron(
                    eye(xdim['full'], n=xdim['full'], k=-i),
                    toeplitz(np.pad(in2[i, :], (0, ydim['same'] - 1)), np.pad([in2[i, 0]], (0, ydim['full'] - 1)), diag_opt=True)
                )
            else:
                # Default
                Ops[i] = kron(
                    eye(xdim['full'], n=xdim['full'], k=-i),
                    sp.linalg.toeplitz(np.pad(in2[i, :], (0, ydim['same'] - 1)), np.full(ydim['full'], 0.0))
                )
        # Operator to pad the flattened image
        # scipy.signal.convolve2d adds 0 only on one side along both axis
        C = sum(*Ops, af=False) @ pad((xdim['same'], ydim['same']), ((0, xdim['full'] - xdim['same']), (0, ydim['full'] - ydim['same'])))
        # Add boundary conditions
        if boundary == 'wrap' or boundary == 'symm':
            C = C @ bc2d((X, Y), x=1, y=1, boundary=boundary)
        # Extract center of the output
        C = C[((np.arange(xdim['full'] * ydim['full']).reshape(xdim['full'], ydim['full']))[i1:s1, i2:s2]).ravel(), :]
    else:
        raise ValueError('Unknown method.')

    if return_lazylinop:
        # return lazy linear operator
        # pyfaust.toeplitz returns 'complex' even if argument is 'real'
        ckernel = 'complex' in str(in2.dtype)
        return LazyLinearOp(
            shape=C.shape,
            matmat=lambda x: (
                C @ x if ckernel or 'complex' in str(x.dtype)
                else np.real(C @ x)
            ),
            rmatmat=lambda x: (
                C.H @ x if ckernel or 'complex' in str(x.dtype)
                else np.real(C.H @ x)
            )
        )
    else:
        # return result of the 2D convolution
        # pyfaust.toeplitz returns 'complex' even if argument is 'real'
        if 'complex' in str(in1.dtype) or 'complex' in str(in2.dtype):
            return (C @ in1.flatten())#.reshape(xdim[mode], ydim[mode])
        else:
            return np.real((C @ in1.flatten()))#.reshape(xdim[mode], ydim[mode])


# def tconvolve(in1, in2: np.ndarray):
#     """Constructs twisted convolution lazy linear operator.

#     Args:
#         in1: tuple,
#              Shape (tuple (X, Y)) of the signal to convolve with kernel.
#         in2: np.ndarray
#             kernel to use for the convolution, shape is (K = X, L = Y)

#     Returns:
#         LazyLinearOp or np.ndarray

#     Raises:
#         Exception
#             in1 expects tuple as (X, Y).
#         ValueError
#             Negative dimension value is not allowed.
#         ValueError
#             in1 and in2 must have the same dimensions.

#     Examples:
#         >>> import numpy as np
#         >>> from lazylinop.wip.signal import tconvolve
#         >>> image = np.random.rand(4, 4)
#         >>> kernel = np.random.rand(4, 4)
#         >>> c1 = tconvolve(image.shape, kernel) @ image.flatten()
#         >>> c2 = tconvolve(image, kernel)
#         >>> np.allclose(c1, c2)
#         True

#     References:
#         See also `LTFAT twisted convolution documentation <https://ltfat.org/doc/gabor/tconv.html>`_.
#     """
#     # check if matrix has been passed to the function
#     # check if shape of the image has been passed to the function
#     return_lazylinop = type(in1) is tuple

#     if type(in1) is tuple:
#         return_laylinop = True
#         if len(in1) != 2:
#             raise Exception("in1 expects tuple (X, Y).")
#         X, Y = in1[0], in1[1]
#     else:
#         raise Exception("in1 expects tuple (X, Y).")

#     if X <= 0 or Y <= 0:
#         raise ValueError("zero or negative dimension is not allowed.")
#     K, L = in2.shape
#     if X <= 0 or Y <= 0 or K <= 0 or L <= 0:
#         raise ValueError("Negative dimension value is not allowed.")
#     if X != Y or X != K or K != L:
#         raise ValueError("in1 and in2 must have the same dimensions.")
#     DIM = X

#     def _matmat(shape, xx, hh, adjoint=False):

#         sv = 1 if adjoint else -1
#         coeff = sv * 2.0 * np.pi * 1.0j / DIM
#         coeffH = -2.0 * np.pi * 1.0j / DIM

#         if xx.ndim == 1:
#             use_parallel=bool((X * Y * K * L / _T) >= 100000)
#         else:
#             use_parallel=bool((xx.shape[1] * X * Y * K * L / _T) >= 100000)

#         # Because of Numba split 1d and 2d functions
#         @nb.jit(nopython=True, parallel=use_parallel, cache=True)
#         def _1d(shape, xx, hh):
#             X, Y = shape[0], shape[1]
#             out = np.zeros(DIM ** 2, dtype=np.complex_)
#             # brute force costs ~ X * Y * K * L operations
#             for m in prange(DIM):
#                 for n in range(DIM):
#                     for x in range(DIM):
#                         for y in range(DIM):
#                             # print(np.exp(1+1j), np.exp(1-1j), np.conjugate(np.exp(1+1j)))
#                             # print(m, n, x, y, np.exp(coeff * ((m + sv * x) % DIM) * y))
#                             if adjoint:
#                                 out[m * DIM + n] += xx[x * DIM + y] * hh[(m + sv * x) % DIM, (n + sv * y) % DIM] * np.conjugate(np.exp(coeffH * ((m + sv * x) % DIM) * y))
#                                 # out[m * DIM + n] +=(
#                                 #     xx[(DIM - 1 - x) * DIM + (DIM - 1 - y)] * hh[(m - x) % DIM, (n - y) % DIM] *
#                                 #     np.exp(coeffH * ((m - x) % DIM) * y)
#                                 # )
#                             else:
#                                 out[m * DIM + n] += xx[x * DIM + y] * hh[(m + sv * x) % DIM, (n + sv * y) % DIM] * np.exp(coeff * ((m + sv * x) % DIM) * y)
#                             # out[m * DIM + n] += xx[x * DIM + y] * hh[(m + sv * x) % DIM, (n + sv * y) % DIM] * np.exp(coeff * ((m - sv * x) % DIM) * y)
#                             # if adjoint:
#                             #     out[m * DIM + n] += xx[((m - x) % DIM) * DIM + (n - y) % DIM] * hh[DIM - 1 - x, DIM - 1 - y] * np.exp(coeffH * ((m - x) % DIM) * (DIM - 1 - y))
#                             # else:
#                             #     out[m * DIM + n] += xx[((m - x) % DIM) * DIM + (n - y) % DIM] * hh[x, y] * np.exp(coeffH * ((m - x) % DIM) * y)
#                             # out[m * DIM + n] += xx[x * DIM + y] * hh[(m + sv * x) % DIM, (n + sv * y) % DIM] * np.exp(coeff * ((n + sv * y) % DIM) * x)
#             return out

#         @nb.jit(nopython=True, parallel=use_parallel, cache=True)
#         def _2d(shape, xx, hh):
#             batch_size = xx.shape[1]
#             out = np.zeros((DIM ** 2, batch_size), dtype=np.complex_)
#             # brute force costs ~ X * Y * K * L operations
#             for b in prange(batch_size):
#                 for m in range(DIM):
#                     for n in range(DIM):
#                         for x in range(DIM):
#                             for y in range(DIM):
#                                 out[m * DIM + n, b] += xx[x * DIM + y, b] * hh[(m + sv * x) % DIM, (n + sv * y) % DIM] * np.exp(coeff * ((m + sv * x) % DIM) * y)
#                                 # if adjoint:
#                                 #     out[m * DIM + n, b] += xx[((m - x) % DIM) * DIM + (n - y) % DIM, b] * hh[DIM - 1 - x, DIM - 1 - y] * np.exp(coeffH * ((m - x) % DIM) * (DIM - 1 - y))
#                                 # else:
#                                 #     out[m * DIM + n, b] += xx[((m - x) % DIM) * DIM + (n - y) % DIM, b] * hh[x, y] * np.exp(coeffH * ((m - x) % DIM) * y)
#                                 # out[m * DIM + n, b] += xx[x * DIM + y, b] * hh[(m + sv * x) % DIM, (n + sv * y) % DIM] * np.exp(coeff * ((n + sv * y) % DIM) * x)
#             return out

#         return _1d(shape, xx, hh) if xx.ndim == 1 else _2d(shape, xx, hh)

#     return LazyLinearOp(
#         shape=(DIM ** 2, DIM ** 2),
#         matmat=lambda x: _matmat((X, Y), x, in2, False),
#         rmatmat=lambda x: _matmat((X, Y), x, in2, True)
#     )


def pad(shape: tuple, pad_width: tuple):
    """
    Deprecated alias for :py:func:`lazylinop.pad` (using the
    :py:func:`lazylinop.kron` backend).
    This function might be removed in a next version.
    """
    from lazylinop.basicops.pad import kron_pad
    from warnings import warn
    warn("DEPRECATED lazylinop.wip.signal.pad, please use lazylinop.pad. This"
         " function might be removed in a next version.")
    return kron_pad(shape, pad_width)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
