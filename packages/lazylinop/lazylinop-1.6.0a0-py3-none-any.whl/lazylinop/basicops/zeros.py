from lazylinop import LazyLinearOp, sanitize_op, binary_dtype
import numpy as np

def zeros(shape, dtype=None):
    """
    Returns a zero LazyLinearOp.

    Args:
        shape:
             the shape of the operator.

    Example:
        >>> from lazylinop import zeros
        >>> import numpy as np
        >>> Lz = zeros((10, 12))
        >>> x = np.random.rand(12)
        >>> Lz @ x
        array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])

    References:
        See also `numpy.zeros <https://numpy.org/doc/stable/reference/generated/numpy.zeros.html>`.
    """
    if dtype is None:
        dtype = 'float'
    def _matmat(op, shape):
        nonlocal dtype
        dtype = binary_dtype(dtype, op.dtype)
        sanitize_op(op)
        op_m = op.shape[0] if op.ndim == 1 else op.shape[-2]
        if op_m != shape[1]:
            raise ValueError('Dimensions must agree')
        if LazyLinearOp.isLazyLinearOp(op):
            return zeros((shape[0], op.shape[1]))
        # TODO: another output type than numpy array?
        elif op.ndim == 2:
            return np.zeros((shape[0], op.shape[1]), dtype=dtype)
        elif op.ndim > 2:
            return np.zeros((*op.shape[:-2], shape[0], op.shape[-1]),
                            dtype=dtype)
        else:
            # op.ndim == 1
            return np.zeros((shape[0],))
    return LazyLinearOp(shape, matmat=lambda x:
                              _matmat(x, shape),
                              rmatmat=lambda x: _matmat(x, (shape[1],
                                                             shape[0])),
                        dtype=dtype)


