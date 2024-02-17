from lazylinop import LazyLinearOp, isLazyLinearOp, binary_dtype
import numpy as np

def eye(m, n=None, k=0, dtype='float'):
    """
    Returns the LazyLinearOp for eye (identity matrix and variants).

    Args:
        m: (int)
             Number of rows of the LazyLinearOp.
        n: (int)
             Number of columns. Default is m.
        k: (int)
             Diagonal to place ones on. Default is 0 (main diagonal). Negative integer for a diagonal below the main diagonal, strictly positive integer for a diagonal above.
        dtype: (str)
             data type of the LazyLinearOp.

    Example:
        >>> from lazylinop import eye
        >>> le1 = eye(5)
        >>> le1
        <5x5 LazyLinearOp with dtype=float64>
        >>> le1.toarray()
        array([[1., 0., 0., 0., 0.],
               [0., 1., 0., 0., 0.],
               [0., 0., 1., 0., 0.],
               [0., 0., 0., 1., 0.],
               [0., 0., 0., 0., 1.]])
        >>> le2 = eye(5, 2)
        >>> le2
        <5x2 LazyLinearOp with dtype=float64>
        >>> le2.toarray()
        array([[1., 0.],
               [0., 1.],
               [0., 0.],
               [0., 0.],
               [0., 0.]])
        >>> le3 = eye(5, 3, 1)
        >>> le3
        <5x3 LazyLinearOp with dtype=float64>
        >>> le3.toarray()
        array([[0., 1., 0.],
               [0., 0., 1.],
               [0., 0., 0.],
               [0., 0., 0.],
               [0., 0., 0.]])
        >>> le4 = eye(5, 3, -1)
        >>> le4
        <5x3 LazyLinearOp with dtype=float64>
        >>> le4.toarray()
        array([[0., 0., 0.],
               [1., 0., 0.],
               [0., 1., 0.],
               [0., 0., 1.],
               [0., 0., 0.]])

    References:
        **See also:** `scipy.sparse.eye <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.eye.html>`_, `numpy.eye <https://numpy.org/devdocs/reference/generated/numpy.eye.html>`_.
    """
    def matmat(x, m, n, k):
        nonlocal dtype # TODO: take dtype into account
        out_dtype = binary_dtype(dtype, x.dtype)
        if n != x.shape[0]:
            raise ValueError('Dimensions must agree')
        if len(x.shape) == 1:
             x = x.reshape(x.size, 1)
             x_1dim = True
        else:
             x_1dim = False
        minmn = min(m, n)
        x_islop = isLazyLinearOp(x)
        if k < 0:
            neg_k = True
            nz = np.zeros((abs(k), x.shape[1]), dtype=out_dtype)
            if x_islop:
                nz = aslazylinearoperator(nz)
            limk = min(minmn, m - abs(k))
            k = 0
        else:
            limk = min(minmn, n - k)
            neg_k = False
        mul = x[k: k + limk, :]
        if neg_k:
            if x_islop:
                mul = vstack((nz, mul))
            else:
                mul = np.vstack((nz, mul))
        if mul.shape[0] < m:
            z = np.zeros((m -
                      mul.shape[0],
                      mul.shape[1]), dtype=out_dtype)
            if x_islop:
                    z = aslazylinearoperator(z)
            t = (mul, z)
            if x_islop:
                mul = vstack(t)
            else:
                mul = np.vstack(t)
        if x_1dim:
            mul = mul.reshape(-1)
        return mul.astype(out_dtype)
    n = n if n is not None else m
    return LazyLinearOp((m, n), matmat=lambda x: matmat(x, m, n, k),
                              rmatmat=lambda x: matmat(x, n, m, -k),
                              dtype=dtype)
