from lazylinop import LazyLinearOp


def sum(*lops, af=False):
    """
    Sums (lazily) all linear operators in lops.

    Args:
        lops: (LinearOperator, including :py:class:`LazyLinearOp`)
             the objects to add up as a list of LazyLinearOp-s or other
             compatible linear operator.
        af:
             this argument defines how to compute L @ M = sum(lops) @ M,
             with M a numpy array. If True, the function adds the lops[i]
             into s before computing s @ M. Otherwise, by default, each
             lops[i] @ M are computed and then summed.

    Returns:
        The LazyLinearOp for the sum of lops.

    Example:
        >>> import numpy as np
        >>> from lazylinop import sum, aslazylinearoperator
        >>> from pyfaust import dft, Faust
        >>> from scipy.sparse import diags
        >>> nt = 10
        >>> d = 64
        >>> v = np.random.rand(d)
        >>> terms = [dft(d) @ Faust(diags(v, format='csr')) @ dft(d) \
                     for _ in range(nt)]
        >>> ls = sum(*terms) # ls is the LazyLinearOp sum of terms
    """

    def lAx(A, x):
        return A @ x

    def lAHx(A, x):
        return A.T.conj() @ x
    for op in lops[1:]:
        if op.shape != lops[0].shape:
            raise ValueError('Dimensions must agree')

    def matmat(x, lmul):
        if af:
            S = lops[0]
            for T in lops[1:]:
                S = S + T
            return S @ x
        Ps = [None for _ in range(len(lops))]
        n = len(lops)
        for i, A in enumerate(lops):
            Ps[i] = lmul(A, x)
        S = Ps[-1]
        for i in range(n-2, -1, -1):
            S = S + Ps[i]
        return S

    return LazyLinearOp(lops[0].shape, matmat=lambda x: matmat(x, lAx),
                        rmatmat=lambda x: matmat(x, lAHx))
