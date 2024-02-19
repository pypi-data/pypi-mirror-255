from warnings import warn
from scipy.sparse import issparse, random
import numpy as np


def check_op(L, silent=True):
    """
    Asserts that ``L`` is valid (as a :py:class:`LazyLinearOp`).

    This function helps to verify that a :py:class:`LazyLinearOp` defined using
    the class constructor is valid.

    For ``L`` to be valid it must:

        1. be a :py:class:`LazyLinearOp`,
        2. the result of products ``P = L @ X, L.T @ X or L.H @ X`` must
        consist with ``L``, ``X`` and a well defined matrix-product.
        ``P`` must have a consistent ``type(P)``, ``P.dtype``, ``P.shape`` and
        ``P`` value.
        ``X`` can be a 1d and 2d numpy array (and optionally a scipy matrix).

    For more details about the validity of a :py:class:`LazyLinearOp` see the
    `specification <./check_op_spec.html>`_.

    Args:
        L: (LazyLinearOp)
            The operator to test. It might have been defined by the
            :py:func:`LazyLinearOp.__init__` constructor, using
            :py:func:`lazylinop.aslazylinearoperator` or extending the
            :py:class:`LazyLinearOp` class.
        silent: (bool)
            if True (default) all informative messages are silenced otherwise
            they are printed.
            If you need to filter warnings too use
            ``warnings.filterwarnings('ignore', 'check_op')``.

    Raises:
        ``AssertionError``: if ``L`` is not valid.

    Returns:
        None

    Example:
        >>> from numpy.random import rand
        >>> from lazylinop import aslazylinearoperator, check_op
        >>> M = rand(12, 14)
        >>> check_op(aslazylinearoperator(M))

    """
    from lazylinop import binary_dtype, LazyLinearOp
    silent or print("Testing your LazyLinearOp L...")
    # (A1) type of L:
    assert LazyLinearOp.isLazyLinearOp(L)
    overridden_funcs = []
    verified_meths = ['__init__', '_create_LazyLinOp', '_check_lambdas',
                      'create_from_op', 'create_from_scalar',
                      'create_from_funcs', '_checkattr', '_index_lambda',
                      'ndim', 'transpose', 'T', 'conj', 'conjugate', 'getH',
                      'H', '_adjoint', '_slice', '__add__', '__radd__',
                      '__iadd__', '__sub__', '__rsub__', '__isub__',
                      '__truediv__', '__itruediv__', '_sanitize_matmul',
                      '__matmul__', 'dot', 'matvec', '_rmatvec', '_matmat',
                      '_rmatmat', '__imatmul__', '__rmatmul__', '__mul__',
                      '__rmul__', '__imul__', 'toarray', '__getitem__',
                      '_newshape_getitem', 'concatenate', '_vstack_slice',
                      '_vstack_mul_lambda', 'vstack', '_hstack_slice',
                      '_hstack_mul_lambda', 'hstack', 'real', 'imag',
                      'isLazyLinearOp', '__array_ufunc__', '__array__',
                      '__array_function__']
    for attr_name in verified_meths:  # dir(LazyLinearOp):
        attr = L.__getattribute__(attr_name)
        if (('method' in str(type(attr)) or 'function' in str(type(attr))) and
           'LazyLinearOp.'+attr_name not in str(attr)):
            overridden_funcs += [attr_name]
    if len(overridden_funcs) > 0:
        warn("Override detected in LazyLinearOp object for function(s): "
             + str(overridden_funcs)+", it might"
             " break something (at your own risk)")
    tested_Ls = [(L, 'L')]
    try:
        L.T.toarray()
    except TypeError as te:
        if str(te) in "'NoneType' object is not callable":
            # rmatmat or rmatvec was not provided by user
            warn("L wasn't defined with a rmatvec/rmatmat function, that's not"
                 " advised as L.T and L.H or left-hand mul Y @ L won't be"
                 " available.")
    else:
        # rmatmat/vec is defined
        tested_Ls += [(L.T, 'L.T'), (L.H, 'L.H')]
    for L_, L_exp in tested_Ls:
        # different to detect erroneous P shape
        X_ncols = 2 if L_.shape[1] != 2 else 3
        silent or print("Testing L_ =", L_exp, "through P = L_ @ X")
        for X, L_must_handle_X in [(np.random.rand(L_.shape[1], X_ncols),
                                    True),
                                   (random(L_.shape[1], X_ncols),
                                    False),
                                   (np.random.rand(L_.shape[1]), True)]:
            silent or print("type(X):", type(X))
            try:
                P = L_ @ X
            except Exception as e:
                if L_must_handle_X:
                    silent or print("L_ @ X raised this exception:", str(e))
                    raise Exception("L_ is defective about the type of X (in"
                                    " L_ @ X). L_ must handle X either it is"
                                    " a 2d or 1d np.ndarray (in the case the"
                                    " dimensions match).")
                else:
                    warn("L_ doesn't handle X of -- not mandatory -- type: " +
                         str(type(X)))
                    continue
            # (A2) type of P = L_ @ X:
            assert (issparse(X) and (issparse(P) or isinstance(P, np.ndarray))
                    or isinstance(X, np.ndarray) and isinstance(P, np.ndarray))
            # (A2) is True,
            # then attributes shape, ndim and dtype are available for P
            # (A3) Shape of P:
            assert P.ndim == X.ndim
            assert P.shape[0] == L_.shape[0]
            assert P.ndim == 1 or P.shape[1] == X.shape[1]
            # (A4) dtype of P:
            if L_.dtype is None:
                warn("L_ is of undefined dtype, this is not advised.")
            else:
                ref_dtype = binary_dtype(L_.dtype, X.dtype)
                assert P.dtype is ref_dtype
            # (A5) equality:
            if issparse(P):
                P = P.toarray()
            # (A5.1)
            assert np.allclose(P, L_.toarray() @ X)
            # (A5.2)
            if issparse(X):
                X_ = X.toarray()
            else:
                X_ = X
            assert (X_.ndim == 1 or
                    np.all([np.allclose(P[:, j], L_ @ X_[:, j]) for j in
                            range(X_.shape[1])])
                    and
                    np.all([np.allclose(P[i, :], L_[i, :] @ X_) for i in
                            range(L_.shape[0])]))
        silent or print("_L =", L_exp, "passed all tests")
    silent or print("L passed all tests")


def _check_op(op):
    """
    Verifies validity assertions on any LazyLinearOp.

    Let op a LazyLinearOp, u a vector of size op.shape[1], v a vector of size
    op.shape[0], X an array such that X.shape[0] == op.shape[1],
    Y an array such that Y.shape[0] == op.shape[0],
    the function verifies that:

        - (op @ u).size == op.shape[0],
        - (op.H @ v).size == op.shape[1],
        - (op @ u).conj().T @ v == u.conj().T @ op.H @ v,
        - op @ X is equal to the horizontal concatenation of all op @ X[:, j]
          for j in {0, ..., X.shape[1]-1}.
        - op.H @ Y is equal to the horizontal concatenation of all
          op.H @ Y[:, j] for j in {0, ..., X.shape[1]-1}.
        - op @ X @ Y.H == (Y @ (X.H @ op.H)).H

    **Note**: this function has a computational cost (at least similar to the
    cost of op@x), it shouldn't be used into an efficient implementation but
    only to test a LazyLinearOp works properly.

    Example:
        >>> from numpy.random import rand
        >>> from lazylinop import aslazylinearoperator
        >>> from lazylinop.check_op import _check_op
        >>> M = rand(12, 14)
        >>> _check_op(aslazylinearoperator(M))

    """
    warn("Deprecated _check_op, please use check_op. The former will deleted"
         " soon.")
    u = np.random.randn(op.shape[1])
    v = np.random.randn(op.shape[0])
    X = np.random.randn(op.shape[1], 3)
    Y = np.random.randn(op.shape[0], 3)
    # Check operator - vector product dimension
    if (op @ u).shape != (op.shape[0],):
        raise Exception("Wrong operator dimension")
    # Check operator adjoint - vector product dimension
    if (op.H @ v).shape != (op.shape[1],):
        raise Exception("Wrong operator adjoint dimension")
    # Check operator - matrix product consistency
    AX = op @ X
    for i in range(X.shape[1]):
        if not np.allclose(AX[:, i], op @ X[:, i]):
            raise Exception("Wrong operator matrix product")
#    if not np.allclose(op @ X, np.hstack([(op @ X[:, i]).reshape(-1, 1)
#                                          for i in range(X.shape[1])])):
#         raise Exception("Wrong operator matrix product")
#    if not np.allclose(op.H @ Y, np.hstack([(op.H @ Y[:, i]).reshape(-1, 1)
#                                            for i in range(X.shape[1])])):
#         raise Exception("Wrong operator adjoint on matrix product")
    # Dot test to check forward - adjoint consistency
    if not np.allclose((op @ u).conj().T @ v, u.conj().T @ (op.H @ v)):
        raise Exception("Operator and its adjoint do not match")
    if (op.T @ Y).shape[0] != op.shape[1]:
        raise Exception("Wrong operator transpose dimension (when multiplying"
                        " an array)")
    if not np.allclose(AX @ Y.T.conj(), (Y @ AX.T.conj()).T.conj()):
        raise Exception("Wrong operator on (Y @ X.H @ op.H).H")
    del AX
    # Check operator transpose dimension
    AY = op.H @ Y
    if AY.shape[0] != op.shape[1]:
        raise Exception("Wrong operator transpose dimension (when multiplying"
                        " an array)")
    # Check operator adjoint on matrix product
    for i in range(X.shape[1]):
        if not np.allclose(AY[:, i], op.H @ Y[:, i]):
            raise Exception("Wrong operator adjoint on matrix product")
    del AY
