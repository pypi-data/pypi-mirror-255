from typing import Union
from scipy.sparse import issparse, vstack as svstack
from numpy import vstack
from lazylinop import isLazyLinearOp, LazyLinearOp, sanitize_op, binary_dtype
from lazylinop.basicops import vstack as lvstack
import numpy as np


def ones(shape: tuple[int, int],
         dtype: Union[str, None] = None,
         **kwargs):
    """
    Return a :class:`LazyLinearOp` given shape and type, filled with ones.

    Args:

        shape: (int or tuple/pair of ints)
            Shape of the new array, e.g., (2, 3) or 2.

        dtype: (data-type str)
            numpy compliant data-type str (e.g. 'float64').


    Examples:
        >>> from lazylinop import ones
        >>> O = ones((6, 5), dtype='float')
        >>> import numpy as np
        >>> v = np.arange(5)
        >>> O @ v
        array([10., 10., 10., 10., 10., 10.])
        >>> Oa = np.ones((6, 5))
        >>> Oa @ v
        array([10., 10., 10., 10., 10., 10.])
        >>> M = np.arange(5*4).reshape(5, 4)
        >>> O @ M
        array([[40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.]])
        >>> Oa @ M
        array([[40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.],
               [40., 45., 50., 55.]])

    """
    # TODO: using MPI or Dask should be considered as complementary methods
    # (equiv. to parallel_proc in one CPU scenoario)
    # meth: str = None,
    # slice_size: Union[None, int] = None)
    # meth: (str)
    # Determines the method used to compute the matrix multiplication of the
    # ones :class:`LazyLinearOp`. Defaultly (if None), 'seq' method is used.
    # - 'seq': computes sequentially after a toarray (it does not disable the
    # numpy array parallelization of the matrix mul. but does not add any
    # parallelization upon it).
    # - 'seq_per_slice': computes sequentially but slice per slice.
    # - 'parallel_thread': computes in parallel using threads.
    # - 'parallel_proc': computes in parallel using processes.
    # slice_size: the slice size in columns used to compute in methods
    # 'seq_per_slice' and 'parallel_thread' or 'parallel_proc'. Defaultly
    # (None) it is 1 for 'seq_per_slice' and `multiprocessing.cpu_count()`
    #        for 'parallel*'.
    if 'meth' in kwargs:
        meth = kwargs['meth']
    else:
        meth = None
#    if 'slice_size' in kwargs:
#        slice_size = kwargs['slice_size']
#    else:
#        slice_size = None
    if not isinstance(shape, tuple):
        raise TypeError('shape is not a tuple')
    if len(shape) != 2:
        raise ValueError('shape must be of length 2')
    m, n = shape
    valid_meths = ['seq', 'seq_per_slice', 'parallel_thread', 'parallel_proc']
    if meth is None:
        meth = 'seq'
    elif meth not in valid_meths:
        raise ValueError('Unknown method '+str(valid_meths))
    if dtype is None:
        dtype = 'int'

    def mul(nrows, ncols, op):
        sanitize_op(op)
        out_dtype = binary_dtype(dtype, op.dtype)
        if meth == 'seq':
            if isinstance(op, np.ndarray):
                s = np.sum(op, axis=0)
                ret = vstack([s for _ in range(nrows)]).astype(out_dtype)
            elif issparse(op):
                s = op.sum(axis=0)
                ret = svstack([s for _ in range(nrows)]).astype(out_dtype)
            elif isLazyLinearOp(op):
                for i in range(op.shape[0]):
                    if i == 0:
                        s = op[0, :]
                    else:
                        s = s + op[i, :]
                return lvstack([s for _ in range(nrows)])
            else:
                raise TypeError('Unknown type of object: '+str(op))
        else:
            raise NotImplementedError("ones method "+str(meth))
        if op.ndim == 1:
            return ret.ravel()
        else:
            return ret
    return LazyLinearOp((m, n), matmat=lambda x: mul(m, n, x),
                        rmatmat=lambda x: mul(n, m, x),
                        dtype=dtype)
