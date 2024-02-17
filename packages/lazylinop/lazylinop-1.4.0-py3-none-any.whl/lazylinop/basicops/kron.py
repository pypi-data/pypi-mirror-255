from lazylinop import LazyLinearOp, binary_dtype
import numpy as np


def kron(A, B):
    """
    Returns the LazyLinearOp(Kron) for the Kronecker product A x B.

    Note: this specialization is particularly optimized for multiplying the
    operator by a vector.

    Args:
        A: LinearOperator
            scaling factor,
        B: LinearOperator
            block factor.

    Returns:
        The Kronecker product LazyLinearOp.

    Example:
        >>> from lazylinop import kron as lkron
        >>> import numpy as np
        >>> from pyfaust import rand
        >>> A = np.random.rand(100, 100)
        >>> B = np.random.rand(100, 100)
        >>> AxB = np.kron(A,B)
        >>> lAxB = lkron(A, B)
        >>> x = np.random.rand(AxB.shape[1], 1)
        >>> print(np.allclose(AxB@x, lAxB@x))
        True
        >>> from timeit import timeit
        >>> timeit(lambda: AxB @ x, number=10) # doctest:+ELLIPSIS
        0...
        >>> # example: 0.4692082800902426
        >>> timeit(lambda: lAxB @ x, number=10) # doctest:+ELLIPSIS
        0...
        >>> # example 0.03464869409799576

    See also
    numpy.kron_,
    scipy.sparse.kron_,
    pylops.Kronecker_

.. _numpy.kron:
    https://numpy.org/doc/stable/reference/generated/numpy.kron.html
.. _scipy.sparse.kron:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.kron.html
.. _pylops.Kronecker:
    https://pylops.readthedocs.io/en/stable/api/generated/pylops.Kronecker.html
    """
    def _kron(A, B, shape, op):
        if isinstance(op, np.ndarray):
            op = np.asfortranarray(op)

        # LazyLinearOp._sanitize_matmul(op) # TODO

        if (hasattr(op, 'reshape') and
           hasattr(op, '__matmul__') and hasattr(op, '__getitem__')):

            if len(op.shape) == 1:
                op = op.reshape((op.size, 1))
                one_dim = True
            else:
                one_dim = False
            dtype = binary_dtype(binary_dtype(A.dtype, B.dtype), op.dtype)
            res = np.empty((shape[0], op.shape[1]), dtype=dtype)

            def out_col(j, ncols):
                for j in range(j, min(j + ncols, op.shape[1])):
                    op_mat = op[:, j].reshape((A.shape[1], B.shape[1]))
                    # Do we multiply from left to right or from right to left ?
                    m, k = A.shape
                    k, n = op_mat.shape
                    n, p = B.T.shape
                    ltor = m * k * n + m * n * p
                    rtol = m * k * p + k * n * p
                    if ltor < rtol:
                        res[:, j] = ((A @ op_mat) @ B.T).reshape(shape[0])
                    else:
                        res[:, j] = (A @ (op_mat @ B.T)).reshape(shape[0])

            ncols = op.shape[1]
            out_col(0, ncols)
            if one_dim:
                res = res.ravel()
        else:
            raise TypeError('op must possess reshape, __matmul__ and'
                            ' __getitem__ attributes to be multiplied by a'
                            ' Kronecker LazyLinearOp (use toarray on the'
                            ' latter to multiply by the former)')
        return res
    shape = (A.shape[0] * B.shape[0], A.shape[1] * B.shape[1])
    return LazyLinearOp(shape,
                        matmat=lambda x: _kron(A, B, shape, x),
                        rmatmat=lambda x: _kron(A.T.conj(), B.T.conj(),
                                                (shape[1], shape[0]), x),
                        dtype=binary_dtype(A.dtype, B.dtype))
