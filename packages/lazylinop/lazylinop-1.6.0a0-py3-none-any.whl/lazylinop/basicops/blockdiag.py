from lazylinop import (binary_dtype, LazyLinearOp, aslazylinearoperator,
                       isLazyLinearOp)
import numpy as np


def block_diag(*lops):
    """
    Returns the block diagonal LazyLinearOp formed of operators in lops.

    Args:
        lops:
             the objects defining the diagonal blocks as a list of
             LazyLinearOp-s or other compatible linear operator.

    Returns:
        The diagonal block LazyLinearOp.

    Example:
        >>> import numpy as np
        >>> from lazylinop import block_diag, aslazylinearoperator
        >>> import scipy
        >>> nt = 10
        >>> d = 64
        >>> v = np.random.rand(d)
        >>> terms = [np.random.rand(64, 64) for _ in range(10)]
        >>> ls = block_diag(*terms) # ls is the block diagonal LazyLinearOp
        >>> np.allclose(scipy.linalg.block_diag(*terms), ls.toarray())
        True


    **See also:** `scipy.linalg.block_diag <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.block_diag.html>`_.
    """
    from lazylinop import vstack
    def lAx(A, x):
        return A @ x

    def lAHx(A, x):
        return A.T.conj() @ x
    roffsets = [0]
    coffsets = [0]  # needed for transpose case
    for i in range(len(lops)):
        roffsets += [roffsets[i] + lops[i].shape[1]]
        coffsets += [coffsets[i] + lops[i].shape[0]]
        if i == 0:
            dtype = lops[0].dtype
        else:
            dtype = binary_dtype(dtype, lops[i].dtype)

    def matmat(x, lmul, offsets):
        if len(x.shape) == 1:
            x_is_1d = True
            x = x.reshape(x.size, 1)
        else:
            x_is_1d = False
        Ps = [None for _ in range(len(lops))]
        n = len(lops)
        for i, A in enumerate(lops):
            Ps[i] = lmul(A, x[offsets[i]:offsets[i+1]])
        S = Ps[0]
        conv_to_lop = isLazyLinearOp(S)
        vcat = vstack if conv_to_lop else np.vstack
        for i in range(1, n):
            if conv_to_lop:
                Ps[i] = aslazylinearoperator(Ps[i])
            elif isLazyLinearOp(Ps[i]):
                S = aslazylinearoperator(S)
                conv_to_lop = True
                vcat = vstack
            S = vcat((S, Ps[i]))
        if x_is_1d:
            S = S.ravel()
        return S
    return LazyLinearOp((coffsets[-1], roffsets[-1]), matmat=lambda x:
                        matmat(x, lAx, roffsets),
                        rmatmat=lambda x: matmat(x, lAHx, coffsets),
                        dtype=dtype)
