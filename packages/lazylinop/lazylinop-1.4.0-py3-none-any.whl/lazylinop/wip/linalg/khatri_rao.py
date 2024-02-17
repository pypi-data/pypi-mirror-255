from lazylinop import isLazyLinearOp, LazyLinearOp
import numpy as np
import scipy as sp

def khatri_rao(A, B, column: bool=True, method: str='lazylinop'):
    """Constructs a Khatri-Rao product lazy linear operator K.
    Khatri-Rao product is a column-wise Kronecker product we denote c*
    while the row-wise product is r*.
    If A and B are two matrices then (A c* B)^T = A^T r* B^T.
    Therefore, we easily get the adjoint of the row-wize Kronecker product.
    If matrix A in R^{m x n} and B in R^{p x n}, the Khatri-Rao product
    matrix is in R^{(m * p) x n}. The function does not explicitly compute
    the matrix. It uses the trick (A c* B) @ x = vec(B @ diag(x) @ A.T)
    where x is a vector of length n and diag(x) a diagonal matrix of size n * n.
    Therefore, we save m * p * n - n * n of memory if m * p > n.

    Args:
        A:
        First matrix, it can be LazyLinearOp or NumPy array
        B:
        Second matrix, it can be LazyLinearOp or NumPy array
        column: bool, optional
        Compute Khatri-Rao product column-wize (True is default)
        If False, compute row-wize product
        method: str, optional
        If 'scipy' uses SciPy Khatri-Rao product

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            number of rows differs.
        ValueError
            number of columns differs.

    Examples:
        >>> import numpy as np
        >>> import scipy as sp
        >>> from lazylinop.wip.special_matrices import khatri_rao
        >>> M1 = np.full((2, 2), 1)
        >>> M2 = np.eye(3, M=2, k=0)
        >>> x = np.random.rand(2)
        >>> K = khatri_rao(M1, M2)
        >>> S = sp.linalg.khatri_rao(M1, M2)
        >>> np.allclose(K @ x, S @ x)
        True

    References:
        See also `scipy.linalg.khatri_rao <https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.khatri_rao.html>`_.
    """

    Ma, Na = A.shape[0], A.shape[1]
    Mb, Nb = B.shape[0], B.shape[1]

    if not column and Ma != Mb:
        raise ValueError("number of rows differs.")

    if column and Na != Nb:
        raise ValueError("number of columns differs.")

    shape = (Ma * Mb, Na) if column else (Ma, Na * Nb)

    # Compute number of operations for lazylinop (B @ diag(x) @ A.T)
    # and for SciPy and return the best method
    def _nops(A, B, x):
        m, k = B.shape
        k, n = x.shape[0], x.shape[0]
        n, p = A.T.shape
        batch_size = 1 if x.ndim == 1 else x.shape[1]
        # # Left to right or right to left multiplication ?
        # ltor = (m * k * n + m * n * p + k + m * p) * batch_size + k ** 2
        # rtol = (m * k * p + k * n * p + k + m * p) * batch_size + k ** 2
        # # SciPy computes the Khatri-Rao matrix K and then computes K @ X
        # nops = A.shape[0] * B.shape[0] * A.shape[1] * (1 + batch_size)
        # print(nops / max(ltor, rtol), 'lazylinop' if nops >  max(ltor, rtol) else 'scipy')
        # return 'lazylinop' if nops > min(ltor, rtol) else 'scipy'
        # Memory: lazylinop creates batch size diagonal matrix (k, k)
        # while SciPy creates Khatri-Rao product matrix (A.shape[0] * B.shape[0], A.shape[1])
        # print('batch size={0:d} {1:s}'.format(batch_size, 'lazylinop' if (A.shape[0] * B.shape[0] * A.shape[1]) > ((k ** 2 + m * p) * batch_size) else 'scipy'))
        return 'lazylinop' if (A.shape[0] * B.shape[0] * A.shape[1]) > ((k ** 2 + m * p) * batch_size) else 'scipy'

    # Because NumPy/SciPy uses parallel computation of the @
    # there is no reasons to define a matvec and run batch of
    # matvec in parallel as matmat.
    def _matmat(A, B, x, column):
        Ma, Na = A.shape[0], A.shape[1]
        Mb, Nb = B.shape[0], B.shape[1]
        if isLazyLinearOp(x):
            x = np.eye(x.shape[0], M=x.shape[0], k=0) @ x
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        Y = np.full((Ma * Mb if column else Ma, batch_size), 0.0 * (A[0, 0] * B[0, 0] * x[0, 0]))
        if column:
            # We use (A c* B) @ x = vec(B @ diag(x) @ A^T)
            # and a ravel with order='F' (does not work with Numba)
            for i in range(batch_size):
                m, k = B.shape
                k, n = x.shape[0], x.shape[0]
                n, p = A.T.shape
                ltor = m * k * n + m * n * p
                rtol = m * k * p + k * n * p
                # Save diagonal matrix creation
                if i == 0:
                    D = np.diag(x[:, i])
                else:
                    np.fill_diagonal(D, val=x[:, i])
                # Minimize the number of operations
                if ltor < rtol:
                    Y[:, i] = ((B @ D) @ A.T).ravel(order='F')
                else:
                    Y[:, i] = (B @ (D @ A.T)).ravel(order='F')
        else:
            for i in range(batch_size):
                for r in range(Ma):
                    Y[r, i] = A[r, :] @ (B[r, :] @ x[:, i].reshape(A.shape[1], B.shape[1]).T).T
        return Y.ravel() if is_1d else Y
        
    # We use (A c* B)^T = A^T r* B^T to compute the adjoint.
    return LazyLinearOp(
        shape=shape,
        matmat=lambda x: sp.linalg.khatri_rao(
            np.eye(A.shape[0], M=A.shape[0], k=0) @ A if isLazyLinearOp(A) else A,
            np.eye(B.shape[0], M=B.shape[0], k=0) @ B if isLazyLinearOp(B) else B
        ) @ x if column and (_nops(A, B, x) == 'scipy' or method == 'scipy') else _matmat(A, B, x, column),
        rmatmat=lambda x : _matmat(A.T.conj(), B.T.conj(), x, not column)
    )
