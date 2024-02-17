"""
A module to implement lazy linear operators.
Available operations are: +, @ (matrix product), * (scalar multiplication), slicing and indexing
and others (for a nicer introduction you might
look at `this notebook <notebooks/lazylinop.html>`_).
"""

import numpy as np
from scipy.sparse.linalg import LinearOperator
HANDLED_FUNCTIONS = {'ndim'}

class LazyLinearOp(LinearOperator):
    """
    This class implements a lazy linear operator. A LazyLinearOp is a
    specialization of a `scipy.linalg.LinearOperator <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.LinearOperator.html>`_.

    The evaluation of any defined operation is delayed until a multiplication
    by a matrix/vector, a call of :py:func:`LazyLinearOp.toarray`.
    A call to :py:func:`LazyLinearOp.toarray` corresponds to a multiplication by the
    identity matrix.

    To instantiate a LazyLinearOp look at
    :py:func:`lazylinop.aslazylinearoperator` or
    :py:func:`lazylinop.LazyLinearOp` to instantiate from matmat/matvec
    functions.

    **Note**: repeated "inplace" modifications of a :py:class:`LazyLinearOp`
    through any operation like a concatenation (``op = vstack((op, anything))``)
    are subject to a :py:class:`RecursionError` if the number of recursive
    calls exceeds the :py:func:`sys.getrecursionlimit`. You might change this
    limit if needed using :py:func:`sys.setrecursionlimit`.

    **Note: This code is in a beta status.**
    """

    def __init__(self, shape, **kwargs):
        """
        Returns a LazyLinearOp defined by shape and at least
        a matvec and a rmatvec (or a matmat and a rmatmat) functions.

        Args:
            shape: (tuple)
                 dimensions (M, N).
            matvec: (callable)
                 returns A * v (A of shape (M, N) and v a vector of size N).
                 the output vector size is M.
            rmatvec: (callable)
                 returns A^H * v (A of shape (M, N) and v a vector of size M).
                 the output vector size is N.
            matmat: (callable)
                 returns A * V (V a matrix of dimensions (N, K)).
                 the output matrix shape is (M, K).
            rmatmat: (callable)
                 returns A^H * V (V a matrix of dimensions (M, K)).
                 the output matrix shape is (N, K).
            dtype:
                 data type of the matrix (can be None).

        Return:
            LazyLinearOp

        Example:
            >>> # In this example we create a LazyLinearOp for the DFT using the fft from scipy
            >>> import numpy as np
            >>> from scipy.fft import fft, ifft
            >>> from lazylinop import LazyLinearOp
            >>> F = LazyLinearOp((8, 8), matmat=lambda x: fft(x, axis=0), rmatmat=lambda x: 8 * ifft(x, axis=0))
            >>> x = np.random.rand(8)
            >>> np.allclose(F * x, fft(x))
            True

        Reference:
            See also `SciPy linear Operator <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.LinearOperator.html>`_.
        """
        if 'internal_call' in kwargs and kwargs['internal_call']:
            self.shape = shape
            if 'dtype' in kwargs:
                self.dtype = kwargs['dtype']
            else:
                self.dtype = None
                super(LazyLinearOp, self).__init__(self.dtype, self.shape)
            return
        matvec, rmatvec, matmat, rmatmat = [None for i in range(4)]
        def callable_err(k):
            return TypeError(k+' in kwargs must be a callable/function')

        for k in kwargs.keys():
            if k != 'dtype' and not callable(kwargs[k]):
                raise callable_err(k)
        if 'matvec' in kwargs.keys():
            matvec = kwargs['matvec']
        if 'rmatvec' in kwargs.keys():
            rmatvec = kwargs['rmatvec']
        if 'matmat' in kwargs.keys():
            matmat = kwargs['matmat']
        if 'rmatmat' in kwargs.keys():
            rmatmat = kwargs['rmatmat']
        if 'dtype' in kwargs.keys():
            dtype = kwargs['dtype']
        else:
            dtype = None

        if matvec is None and matmat is None:
            raise ValueError('At least a matvec or a matmat function must be'
                             ' passed in kwargs.')

        def _matmat(M, _matvec, shape):
            nonlocal dtype
            if len(M.shape) == 1:
                return _matvec(M)
            first_col = _matvec(M[:, 0])
            dtype = first_col.dtype
            out = np.empty((shape[0], M.shape[1]), dtype=dtype)
            out[:, 0] = first_col
            for i in range(1, M.shape[1]):
                out[:, i] = _matvec(M[:,i])
            return out

        if matmat is None:
            matmat = lambda M: _matmat(M, matvec, shape)

        if rmatmat is None and rmatvec is not None:
            rmatmat = lambda M: _matmat(M, rmatvec, (shape[1], shape[0]))

        #MX = lambda X: matmat(np.eye(shape[1])) @ X
        MX = lambda X: matmat(X)
        #MTX = lambda X: rmatmat(X.T).T
        MHX = lambda X: rmatmat(X)

        def MTX(X):
            # computes L.T @ X # L LazyLinearOp, X anything compatible
            L_possibly_cplx = 'complex' in str(dtype) or dtype is None
            X_possibly_cplx = 'complex' in str(X.dtype) or X.dtype is None
            if L_possibly_cplx:
                if X_possibly_cplx:
                    return rmatmat(X.real).conj() - rmatmat(1j * X.imag).conj()
                else:
                    # X is real
                    return rmatmat(X).conj()
            else: # L is real
                return rmatmat(X)

        def MCX(X):
            # computes L.conj() @ X # L LazyLinearOp, X anything compatible
            L_possibly_cplx = 'complex' in str(dtype) or dtype is None
            X_possibly_cplx = 'complex' in str(X.dtype) or X.dtype is None
            if L_possibly_cplx:
                if X_possibly_cplx:
                    return matmat(X.real).conj() + matmat(1j * X.imag)
                else:
                    # X is real
                    return matmat(X).conj()
            else: # L is real
                return MX(X)

        lambdas = {'@': MX}
        lambdasT = {'@': MTX}
        lambdasH = {'@': MHX}
        lambdasC = {'@': MCX}
        # set lambdas temporarily to None (to satisfy the ctor)
        # they'll be initialized later
        for l in [lambdas, lambdasT, lambdasH, lambdasC]:
            l['T'] = None
            l['H'] = None
            l['slice'] = None

        lop = LazyLinearOp._create_LazyLinOp(lambdas, shape, dtype=dtype,
                                             self=self)
        super(LazyLinearOp, lop).__init__(lop.dtype, lop.shape)
        lopT = LazyLinearOp._create_LazyLinOp(lambdasT, (shape[1], shape[0]), dtype=dtype)
        super(LazyLinearOp, lopT).__init__(lopT.dtype, lopT.shape)
        lopH = LazyLinearOp._create_LazyLinOp(lambdasH, (shape[1], shape[0]), dtype=dtype)
        super(LazyLinearOp, lopH).__init__(lopH.dtype, lopH.shape)
        lopC = LazyLinearOp._create_LazyLinOp(lambdasC, shape, dtype=dtype)
        super(LazyLinearOp, lopC).__init__(lopC.dtype, lopC.shape)

        lambdas['T'] = lambda: lopT
        lambdas['H'] = lambda: lopH
        lambdas['slice'] = lambda indices: LazyLinearOp._index_lambda(lop,
                                                                       indices)()
        lambdasT['T'] = lambda: lop
        lambdasT['H'] = lambda: lopC
        lambdasT['slice'] = lambda indices: LazyLinearOp._index_lambda(lopT,
                                                                        indices)()
        lambdasH['T'] = lambda: lopC
        lambdasH['H'] = lambda: lop
        lambdasH['slice'] = lambda indices: LazyLinearOp._index_lambda(lopH,
                                                                        indices)()
        lambdasC['T'] = lambda: lopH
        lambdasC['H'] = lambda: lopT
        lambdasC['slice'] = lambda indices: LazyLinearOp._index_lambda(lopC,
                                                                        indices)()
        self = lop


    @staticmethod
    def _create_LazyLinOp(lambdas, shape, root_obj=None, dtype=None, self=None):
        """
        Low-level constructor. Not meant to be used directly.

        Args:
            lambdas: starting operations.
            shape: the initial shape of the operator.
            root_obj: the initial object the operator is based on.

        <b>See also:</b> :py:func:`lazylinop.aslazylinearoperator`.
        """
        if root_obj is not None:
            if not hasattr(root_obj, 'shape'):
                raise TypeError('The starting object to initialize a'
                                ' LazyLinearOp must possess a shape'
                                ' attribute.')
            if len(root_obj.shape) != 2:
                raise ValueError('The starting object to initialize a LazyLinearOp '
                                 'must have two dimensions, not: '+str(len(root_obj.shape)))

        if self is None:
            self = LazyLinearOp(shape, dtype=dtype, internal_call=True)
        else:
            self.shape = shape
            self.dtype = dtype
        self.lambdas = lambdas
        self._check_lambdas()
        self._root_obj = root_obj
        return self

    def _check_lambdas(self):
        if not isinstance(self.lambdas, dict):
            raise TypeError('lambdas must be a dict')
        keys = self.lambdas.keys()
        for k in ['@', 'H', 'T', 'slice']:
            if k not in keys:
                raise ValueError(k+' is a mandatory lambda, it must be set in'
                                 ' self.lambdas')

    @staticmethod
    def create_from_op(obj, shape=None):
        """
        Alias of :py:func:`lazylinop.aslazylinearoperator`.
        """
        if shape is None:
            oshape = obj.shape
        else:
            oshape = shape
        lambdas = {'@': lambda op: obj @ op}
        lambdasT = {'@': lambda op: obj.T @ op}
        lambdasH = {'@': lambda op: obj.T.conj() @ op}
        lambdasC = {'@': lambda op:
                    obj.conj() @ op if 'complex' in
                    str(obj.dtype) or obj.dtype is None
                    else obj @ op}
        # set lambdas temporarily to None (to satisfy the ctor)
        # they'll be initialized later
        for l in [lambdas, lambdasT, lambdasH, lambdasC]:
            l['T'] = None
            l['H'] = None
            l['slice'] = None #TODO: rename slice to index
        lop = LazyLinearOp._create_LazyLinOp(lambdas, oshape, obj, dtype=obj.dtype)
        lopT = LazyLinearOp._create_LazyLinOp(lambdasT, (oshape[1], oshape[0]), obj, dtype=obj.dtype)
        lopH = LazyLinearOp._create_LazyLinOp(lambdasH, (oshape[1], oshape[0]), obj, dtype=obj.dtype)
        lopC = LazyLinearOp._create_LazyLinOp(lambdasC, oshape, obj, dtype=obj.dtype)

        # TODO: refactor with create_from_funcs (in ctor)
        lambdas['T'] = lambda: lopT
        lambdas['H'] = lambda: lopH
        lambdas['slice'] = lambda indices: LazyLinearOp._index_lambda(lop,
                                                                       indices)()
        lambdasT['T'] = lambda: lop
        lambdasT['H'] = lambda: lopC
        lambdasT['slice'] = lambda indices: LazyLinearOp._index_lambda(lopT,
                                                                        indices)()
        lambdasH['T'] = lambda: lopC
        lambdasH['H'] = lambda: lop
        lambdasH['slice'] = lambda indices: LazyLinearOp._index_lambda(lopH,
                                                                        indices)()
        lambdasC['T'] = lambda: lopH
        lambdasC['H'] = lambda: lopT
        lambdasC['slice'] = lambda indices: LazyLinearOp._index_lambda(lopC,
                                                                        indices)()

        return lop

    #TODO: function not used anywhere, delete it?
    @staticmethod
    def create_from_scalar(s, shape=None):
        """
        Returns a LazyLinearOp L created from the scalar s, such as each L[i, i] == s.
        """
        if shape is None:
            shape = (1, 1)
        a = np.ones(shape) * s
        return create_from_op(a)

    @staticmethod
    def create_from_funcs(matmat, rmatmat, shape, dtype=None):
        """
        Alias of ctor lazylinop.LazyLinearOp.
        """
        pass

    def _checkattr(self, attr):
        if self._root_obj is not None and not hasattr(self._root_obj, attr):
            raise TypeError(attr+' is not supported by the root object of this'
                            ' LazyLinearOp')

    def _index_lambda(lop, indices):
        from scipy.sparse import eye as seye
        s = lambda: \
                LazyLinearOp.create_from_op(seye(lop.shape[0],
                                                  format='csr')[indices[0]]) \
                @ lop @ LazyLinearOp.create_from_op(seye(lop.shape[1], format='csr')[:, indices[1]])
        return s

    @property
    def ndim(self):
        """
        Returns the number of dimensions of the LazyLinearOp (it is always 2).
        """
        return 2

    def transpose(self):
        """
        Returns the LazyLinearOp transpose.
        """
        self._checkattr('transpose')
        return self.lambdas['T']()

    @property
    def T(self):
        """
        Returns the LazyLinearOp transpose.
        """
        return self.transpose()

    def conj(self):
        """
        Returns the LazyLinearOp conjugate.
        """
        self._checkattr('conj')
        return self.H.T

    def conjugate(self):
        """
        Returns the LazyLinearOp conjugate.
        """
        return self.conj()

    def getH(self):
        """
        Returns the LazyLinearOp adjoint/transconjugate.
        """
        #self._checkattr('getH')
        return self.lambdas['H']()

    @property
    def H(self):
        """
        The LazyLinearOp adjoint/transconjugate.
        """
        return self.getH()

    def _adjoint(self):
        """
        Returns the LazyLinearOp adjoint/transconjugate.
        """
        return self.H

    def _slice(self, indices):
        return self.lambdas['slice'](indices)

    def __add__(self, op):
        """
        Returns the LazyLinearOp for self + op.

        Args:
            op: an object compatible with self for this binary operation.

        """
        self._checkattr('__add__')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        if op.shape != self.shape:
            raise ValueError('Dimensions must agree')
        lambdas = {'@': lambda o: self @ o + op @ o,
                   'H': lambda: self.H + op.H,
                   'T': lambda: self.T + op.T,
                   'slice': lambda indices: self._slice(indices) + op._slice(indices)
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=tuple(self.shape),
                              root_obj=None)
        return new_op

    def __radd__(self, op):
        """
        Returns the LazyLinearOp for op + self.

        Args:
            op: an object compatible with self for this binary operation.

        """
        return self.__add__(op)

    def __iadd__(self, op):
        """
        Not Implemented self += op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__iadd__")
# can't do as follows, it recurses indefinitely because of self.eval
#        self._checkattr('__iadd__')
#        self = LazyLinearOp._create_LazyLinOp(init_lambda=lambda:
#                              (self.eval()).\
#                              __iadd__(LazyLinearOp._eval_if_lazy(op)),
#                              shape=(tuple(self.shape)),
#                              root_obj=self._root_obj)
#        return self


    def __sub__(self, op):
        """
        Returns the LazyLinearOp for self - op.

        Args:
            op: an object compatible with self for this binary operation.

        """
        self._checkattr('__sub__')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: self @ o - op @ o,
                   'H': lambda: self.H - op.H,
                   'T': lambda: self.T - op.T,
                   'slice': lambda indices: self._slice(indices) - op._slice(indices)
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=tuple(self.shape),
                              root_obj=None)
        return new_op


    def __rsub__(self, op):
        """
        Returns the LazyLinearOp for op - self.

        Args:
            op: an object compatible with self for this binary operation.

        """
        self._checkattr('__rsub__')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: op @ o - self @ o,
                   'H': lambda: op.H - self.H,
                   'T': lambda: op.T - self.T,
                   'slice': lambda indices: op._slice(indices) - self._slice(indices)
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=self.shape,
                              root_obj=None)
        return new_op

    def __isub__(self, op):
        """
        Not implemented self -= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__isub__")
# can't do as follows, it recurses indefinitely because of self.eval
#        self._checkattr('__isub__')
#        self = LazyLinearOp._create_LazyLinOp(init_lambda=lambda:
#                              (self.eval()).\
#                              __isub__(LazyLinearOp._eval_if_lazy(op)),
#                              shape=(tuple(self.shape)),
#                              root_obj=self._root_obj)
#        return self


    def __truediv__(self, s):
        """
        Returns the LazyLinearOp for self / s.

        Args:
            s: a scalar.

        """
        new_op = self * 1/s
        return new_op

    def __itruediv__(self, op):
        """
        Not implemented self /= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__itruediv__")
# can't do as follows, it recurses indefinitely because of self.eval
#
#        self._checkattr('__itruediv__')
#        self = LazyLinearOp._create_LazyLinOp(init_lambda=lambda:
#                              (self.eval()).\
#                              __itruediv__(LazyLinearOp._eval_if_lazy(op)),
#                              shape=(tuple(self.shape)),
#                              root_obj=self._root_obj)
#        return self

    def _sanitize_matmul(self, op, swap=False):
        self._checkattr('__matmul__')
        if not hasattr(op, 'shape'):
            raise TypeError('op must have a shape attribute')
        dim_err = ValueError('dimensions must agree')
        if (hasattr(self, 'ravel_op') and self.ravel_op == True and
            len(op.shape) >= 2):
            # array flattening is authorized for self LazyLinearOp
            if (not swap and self.shape[1] != op.shape[-2] and np.prod(op.shape) != self.shape[1] or
                swap and self.shape[0] != op.shape[-2] and np.prod(op.shape) != self.shape[0]):
                raise dim_err
            return # flattened op is compatible to self
        if (len(op.shape) == 1 and
            self.shape[(int(swap)+1)%2] != op.shape[-1]
            or
            len(op.shape) >= 2 and
            (swap and op.shape[-1] != self.shape[0] or
             not swap and self.shape[1] != op.shape[-2])):
            raise dim_err

    def __matmul__(self, op):
        """
        Computes self @ op as a sparse matrix / dense array or as a LazyLinearOp depending on the type of op.

        Args:
            op: an object compatible with self for this binary operation.

        Returns:
            If op is an numpy array or a scipy matrix the function returns (self @
            op) as a numpy array or a scipy matrix. Otherwise it returns the
            LazyLinearOp for the multiplication self @ op.

        """
        from scipy.sparse import issparse
        self._sanitize_matmul(op)
        if isinstance(op, np.ndarray) or issparse(op):
            if op.ndim == 1 and self._root_obj is not None:
                res = self.lambdas['@'](op.reshape(op.size, 1)).ravel()
            elif op.ndim > 2:
                from itertools import product
                # op.ndim > 2
                dtype = _binary_dtype(self.dtype, op.dtype)
                res = np.empty((*op.shape[:-2], self.shape[0], op.shape[-1]),
                               dtype=dtype)
                idl = [ list(range(op.shape[i])) for i in range(op.ndim-2) ]
                for t in product(*idl):
                    tr = (*t, slice(0, res.shape[-2]), slice(0, res.shape[-1]))
                    to = (*t, slice(0, op.shape[-2]), slice(0, op.shape[-1]))
                    R = self.lambdas['@'](op.__getitem__(to))
                    res.__setitem__(tr, R)
                # TODO: try to parallelize
            else:
                res = self.lambdas['@'](op)
        else:
            if not LazyLinearOp.isLazyLinearOp(op):
                op = LazyLinearOp.create_from_op(op)
            lambdas = {'@': lambda o: self @ (op @ o),
                       'H': lambda: op.H @ self.H,
                       'T': lambda: op.T @ self.T,
                       'slice': lambda indices: self._slice((indices[0],
                                                            slice(0,
                                                                  self.shape[1])))\
                       @ op._slice((slice(0, op.shape[0]), indices[1]))
                      }
            res = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                                                 shape=(self.shape[0], op.shape[1]),
                                                 root_obj=None,
                                                 dtype=binary_dtype(self.dtype, op.dtype))
#            res = LazyLinearOp.create_from_op(super(LazyLinearOp,
#                                                     self).__matmul__(op))
        return res

    def dot(self, op):
        """
        Alias of LazyLinearOp.__matmul__.
        """
        return self.__matmul__(op)

    def matvec(self, op):
        """
        This function is an alias of self @ op, where the multiplication might
        be specialized for op a vector (depending on how self has been defined
        ; upon on a operator object or through a matvec/matmat function).


        <b>See also:</b> lazylinop.LazyLinearOp.
        """
        if not hasattr(op, 'shape') or not hasattr(op, 'ndim'):
            raise TypeError('op must have shape and ndim attributes')
        if op.ndim > 2 or op.ndim == 0:
            raise ValueError('op.ndim must be 1 or 2')
        if op.ndim != 1 and op.shape[0] != 1 and op.shape[1] != 1:
            raise ValueError('op must be a vector -- attribute ndim to 1 or'
                             ' shape[0] or shape[1] to 1')
        return self.__matmul__(op)

    def _rmatvec(self, op):
        """
        Returns self^H @ op, where self^H is the conjugate transpose of A.

        Returns:
            It might be a LazyLinearOp or an array depending on the op type
            (cf. lazylinop.LazyLinearOp.__matmul__).
        """
        # LinearOperator need.
        return self.T.conj() @ op

    def _matmat(self, op):
        """
        Alias of LazyLinearOp.__matmul__.
        """
        # LinearOperator need.
        if not hasattr(op, 'shape') or not hasattr(op, 'ndim'):
            raise TypeError('op must have shape and ndim attributes')
        if op.ndim > 2 or op.ndim == 0:
            raise ValueError('op.ndim must be 1 or 2')
        return self.__matmul__(op)

    def _rmatmat(self, op):
        """
        Returns self^H @ op, where self^H is the conjugate transpose of A.

        Returns:
            It might be a LazyLinearOp or an array depending on the op type
            (cf. lazylinop.LazyLinearOp.__matmul__).
        """
        # LinearOperator need.
        return self.T.conj() @ op

    def __imatmul__(self, op):
        """
        Not implemented self @= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__imatmul__")

    def __rmatmul__(self, op):
        """
        Returns op @ self which can be a LazyLinearOp or an array depending on op type.

        Args:
            op: an object compatible with self for this binary operation.

        <b>See also:</b> lazylinop.LazyLinearOp.__matmul__)
        """
        self._checkattr('__rmatmul__')
        from scipy.sparse import issparse
        self._sanitize_matmul(op, swap=True)
        if isinstance(op, np.ndarray) or issparse(op):
            res = (self.H @ op.T.conj()).T.conj()
        else:
            if not LazyLinearOp.isLazyLinearOp(op):
                op = LazyLinearOp.create_from_op(op)
            lambdas = {'@': lambda o: (op @ self) @ o,
                       'H': lambda: self.H @ op.H,
                       'T': lambda: self.T @ op.T,
                       'slice': lambda indices: (op @ self)._slice(indices)
                      }
            res = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                               shape=(op.shape[0], self.shape[1]),
                               root_obj=None)
        return res

    def __mul__(self, other):
        """
        Returns the LazyLinearOp for self * other if other is a scalar
        otherwise returns self @ other.

        Args:
            other: a scalar or a vector/array.

        <b>See also:</b> lazylinop.LazyLinearOp.__matmul__)
        """
        self._checkattr('__mul__')
        if np.isscalar(other):
            Dshape = (self.shape[1], self.shape[1])
            matmat = lambda M: M * other
            D = LazyLinearOp(Dshape, matmat=matmat, rmatmat=matmat)
            new_op = self @ D
        else:
            new_op = self @ other
        return new_op

    def __rmul__(self, other):
        """
        Returns other * self.

        Args:
            other: a scalar or a vector/array.

        """
        if np.isscalar(other):
            return self * other
        else:
            return other @ self


    def __imul__(self, op):
        """
        Not implemented self *= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__imul__")

    def toarray(self):
        """
        Returns self as a numpy array.
        """
        #from scipy.sparse import eye
        #return self @ eye(self.shape[1], self.shape[1], format='csr')
        # don't use csr because of function based LazyLinearOp
        # (e.g. scipy fft receives only numpy array)
        return self @ np.eye(self.shape[1], order='F', dtype=self.dtype)

    def __getitem__(self, indices):
        """
        Returns the LazyLinearOp for slicing/indexing.

        Args:
            indices: array of length 1 or 2 which elements must be slice, integer or
            Ellipsis (...). Note that using Ellipsis for more than two indices
            is normally forbidden.

        """
        self._checkattr('__getitem__')
        if isinstance(indices, int):
            indices = (indices, slice(0, self.shape[1]))
        if isinstance(indices, tuple) and len(indices) == 2 and isinstance(indices[0], int) and isinstance(indices[1], int):
            return self.toarray().__getitem__(indices)
        elif isinstance(indices, slice) or isinstance(indices[0], slice) and \
                isinstance(indices[0], slice):
            return self._slice(indices)
        else:
            return self._slice(indices)

    def _newshape_getitem(self, indices):
        empty_lop_except = Exception("Cannot create an empty LazyLinearOp.")
        if isinstance(indices, (np.ndarray, list)):
            return (len(indices), self.shape[1])
        elif indices == Ellipsis:
            return self.shape
        elif isinstance(indices,int):
            # self[i] is a row
            return (1, self.shape[1])
        elif isinstance(indices, slice):
            #self[i:j] a group of contiguous rows
            start, stop, step = indices.start, indices.stop, indices.step
            if stop is None:
                stop = self.shape[0]
            if start is None:
                start = 0
            if step is None:
                step = 1
            return ((stop - start) // step, self.shape[1])
        elif isinstance(indices, tuple):
            if len(indices) == 1:
                return self._newshape_getitem(indices[0])
            elif len(indices) == 2:
                if(isinstance(indices[0], int) and isinstance(indices[1],int)):
                    # item
                    return (1, 1)
            else:
                raise IndexError('Too many indices.')

            if indices[0] == Ellipsis:
                if indices[1] == Ellipsis:
                    raise IndexError('an index can only have a single ellipsis '
                                     '(\'...\')')
                else:
                    # all rows
                    new_shape = self.shape
            elif isinstance(indices[0], int):
                # line F[i]
                new_shape = (1, self.shape[1])
            elif isinstance(indices[0], slice):
                start, stop, step = indices[0].start, indices[0].stop, indices[0].step
                if stop is None:
                    stop = self.shape[0]
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                new_shape = ((stop - start) // step, self.shape[1])
            elif isinstance(indices[0], (list, np.ndarray)):
                if len(indices[0]) == 0: raise empty_lop_except
                new_shape = (len(indices[0]), self.shape[1])
            else:
                 raise idx_error_exception

            if indices[1] == Ellipsis:
                # all columns
                new_shape = self.shape
            elif isinstance(indices[1], int):
                # col F[:, i]
                new_shape = (new_shape[0], 1)
            elif isinstance(indices[1], slice):
                start, stop, step = indices[1].start, indices[1].stop, indices[1].step
                if stop is None:
                    stop = self.shape[1]
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                new_shape = (new_shape[0], (stop - start) // step)
            elif isinstance(indices[1], (list, np.ndarray)):
                if len(indices[1]) == 0: raise empty_lop_except
                new_shape = (new_shape[0], len(indices[1]))
            else:
                 raise idx_error_exception
            return new_shape

    def concatenate(self, *ops, axis=0):
        """
        Returns the LazyLinearOp for the concatenation of self and op.

        Args:
            axis: axis of concatenation (0 for rows, 1 for columns).
        """
        from pyfaust import concatenate as cat
        nrows = self.shape[0]
        ncols = self.shape[1]
        out = self
        for op in ops:
            if axis == 0:
                out = out.vstack(op)
            elif axis == 1:
                out = out.hstack(op)
            else:
                raise ValueError('axis must be 0 or 1')
        return out

    def _vstack_slice(self, op, indices):
        rslice = indices[0]
        if isinstance(rslice, int):
            rslice = slice(rslice, rslice+1, 1)
        if rslice.step is not None and rslice.step != 1:
            raise ValueError('Can\'t handle non-contiguous slice -- step > 1')
        if rslice.start == None:
            rslice = slice(0, rslice.stop, rslice.step)
        if rslice.stop == None:
            rslice = slice(rslice.start, self.shape[0] + op.shape[0], rslice.step)
        if rslice.stop > self.shape[0] + op.shape[0]:
            raise ValueError('Slice overflows the row dimension')
        if rslice.start >= 0 and rslice.stop <= self.shape[0]:
            # the slice is completly in self
            return lambda: self._slice(indices)
        elif rslice.start >= self.shape[0]:
            # the slice is completly in op
            return lambda: op._slice((slice(rslice.start - self.shape[0],
                                            rslice.stop - self.shape[0]) ,indices[1]))
        else:
            # the slice is overlapping self and op
            self_slice = self._slice((slice(rslice.start, self.shape[0]), indices[1]))
            op_slice = self._slice((slice(0, rslice.stop - self.shape[0]), indices[1]))
            return lambda: self_slice.vstack(op_slice)

    def _vstack_mul_lambda(self, op, o):
        from scipy.sparse import issparse
        mul_mat = lambda o: np.vstack((self @ o, op @ o))
        mul_vec = lambda o: mul_mat(o.reshape(self.shape[1], 1)).ravel()
        mul_mat_vec = lambda : mul_vec(o) if len(o.shape) == 1 else mul_mat(o)
        mul = lambda: mul_mat_vec() if isinstance(o, np.ndarray) \
                or issparse(o) else self.vstack(op) @ o
        return mul


    def vstack(self, op):
        """
        See lazylinop.vstack.
        """
        if self.shape[1] != op.shape[1]:
            raise ValueError('self and op numbers of columns must be the'
                             ' same')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: self._vstack_mul_lambda(op, o)(),
                   'H': lambda: self.H.hstack(op.H),
                   'T': lambda: self.T.hstack(op.T),
                   'slice': lambda indices: self._vstack_slice(op, indices)()
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                                                shape=(self.shape[0] + op.shape[0], self.shape[1]),
                                                root_obj=None,
                                                dtype=binary_dtype(self.dtype, op.dtype))
        return new_op

    def _hstack_slice(self, op, indices):
        cslice = indices[1]
        if isinstance(cslice, int):
            cslice = slice(cslice, cslice+1, 1)
        if cslice.step is not None and cslice.step != 1:
            raise ValueError('Can\'t handle non-contiguous slice -- step > 1')
        if cslice.stop > self.shape[1] + op.shape[1]:
            raise ValueError('Slice overflows the row dimension')
        if cslice.start >= 0 and cslice.stop <= self.shape[1]:
            # the slice is completly in self
            return lambda: self._slice(indices)
        elif cslice.start >= self.shape[1]:
            # the slice is completly in op
            return lambda: op._slice((indices[0], slice(cslice.start - self.shape[1],
                                            cslice.stop - self.shape[1])))
        else:
            # the slice is overlapping self and op
            self_slice = self._slice((indices[0], slice(cslice.start, self.shape[1])))
            op_slice = self._slice((indices[0], slice(0, cslice.stop - self.shape[1])))
            return lambda: self_slice.vstack(op_slice)

    def _hstack_mul_lambda(self, op, o):
        from scipy.sparse import issparse
        if isinstance(o, np.ndarray) or issparse(o):
            if len(o.shape) == 1:
                return lambda: self @ o[:self.shape[1]] + op @ o[self.shape[1]:]
            else:
                return lambda: self @ o[:self.shape[1],:] + op @ o[self.shape[1]:, :]
        else:
            return lambda: \
                self @ o._slice((slice(0, self.shape[1]), slice(0,
                                                                o.shape[1]))) \
                    + op @ o._slice((slice(self.shape[1], o.shape[0]), slice(0, o.shape[1])))

    def hstack(self, op):
        """
        See lazylinop.hstack.
        """
        if self.shape[0] != op.shape[0]:
            raise ValueError('self and op numbers of rows must be the'
                             ' same')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: self._hstack_mul_lambda(op, o)(),
               'H': lambda: self.H.vstack(op.H),
               'T': lambda: self.T.vstack(op.T),
                   'slice': lambda indices: self._hstack_slice(op, indices)()
              }
        new_op = LazyLinearOp._create_LazyLinOp(
            lambdas=lambdas,
            shape=(self.shape[0], self.shape[1] + op.shape[1]),
            root_obj=None,
            dtype=binary_dtype(self.dtype, op.dtype))
        return new_op

    @property
    def real(self):
        """
        Returns the LazyLinearOp for real.
        """
        from scipy.sparse import issparse
        lambdas = {'@': lambda o: (self @ o.real).real + \
                   (self @ o.imag * 1j).real if isinstance(o, np.ndarray) \
                   or issparse(o) else real(self @ o),
                   'H': lambda: self.T.real,
                   'T': lambda: self.T.real,
                   'slice': lambda indices: self._slice(indices).real
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                           shape=tuple(self.shape),
                           root_obj=None)
        return new_op

    @property
    def imag(self):
        """
        Returns the imaginary part of the LazyLinearOp.
        """
        from scipy.sparse import issparse
        lambdas = {'@': lambda o: (self @ o.real).imag + \
                   (self @ (1j * o.imag)).imag if isinstance(o, np.ndarray) \
                   or issparse(o) else imag(self @ o),
                   'H': lambda: self.T.imag,
                   'T': lambda: self.T.imag,
                   'slice': lambda indices: self._slice(indices).imag
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                           shape=tuple(self.shape),
                           root_obj=None)
        return new_op


    @staticmethod
    def isLazyLinearOp(obj):
        """
        Returns True if obj is a LazyLinearOp, False otherwise.
        """
        return isinstance(obj, LazyLinearOp)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method == '__call__':
            if str(ufunc) == "<ufunc 'matmul'>" and len(inputs) >= 2 and \
               LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__rmatmul__(inputs[0])
            elif str(ufunc) == "<ufunc 'multiply'>" and len(inputs) >= 2 and \
               LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__rmul__(inputs[0])
            elif str(ufunc) == "<ufunc 'add'>" and len(inputs) >= 2 and \
                    LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__radd__(inputs[0])
            elif str(ufunc) == "<ufunc 'subtract'>" and len(inputs) >= 2 and \
                    LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__rsub__(inputs[0])
        elif method == 'reduce':
#            # not necessary numpy calls Faust.sum
#            if ufunc == "<ufunc 'add'>":
#                if len(inputs) == 1 and pyfaust.isLazyLinearOp(inputs[0]):
#                    #return inputs[0].sum(*inputs[1:], **kwargs)
#                else:
            return NotImplemented

    def __array__(self, *args, **kwargs):
        return self

    def __array_function__(self, func, types, args, kwargs):
        # Note: this allows subclasses that don't override
        # __array_function__ to handle self.__class__ objects
        if not all(issubclass(t, LazyLinearOp) for t in types):
            return NotImplemented
        if func.__name__ == 'ndim':
            return self.ndim
        return NotImplemented

def binary_dtype(A_dtype, B_dtype):
    if isinstance(A_dtype, str):
        A_dtype = np.dtype(A_dtype)
    if isinstance(B_dtype, str):
        B_dtype = np.dtype(B_dtype)
    if A_dtype is None and B_dtype is None:
        return None
    # ('complex', None) always gives 'complex'
    # because whatever None is hiding
    # the binary op result will be complex
    # but (real, None) gives None
    # because a None might or might not hide
    # a complex type
    if A_dtype is None:
        if 'complex' in str(B_dtype):
            return B_dtype
        return None
    if B_dtype is None:
        if 'complex' in str(A_dtype):
            return A_dtype
        return None
    kinds = [A_dtype.kind, B_dtype.kind]
    if A_dtype.kind == B_dtype.kind:
        dtype = A_dtype if A_dtype.itemsize > B_dtype.itemsize else B_dtype
    elif 'c' in [A_dtype.kind, B_dtype.kind]:
        dtype = 'complex'
    elif 'f' in kinds:
        dtype = 'double'
    else:
        dtype = A_dtype
    return dtype

_binary_dtype = binary_dtype # temporary private alias for retro-compat.

def sanitize_op(op, op_name='op'):
    if not hasattr(op, 'shape') or not hasattr(op, 'ndim'):
        raise TypeError(op_name+' must have shape and ndim attributes')

_sanitize_op = sanitize_op # temporary private alias for retro-compat.

def old_check_op(op):
    """
    Verifies validity assertions on any LazyLinearOp.

    Let op a LazyLinearOp, u a vector of size op.shape[1], v a vector of size
    op.shape[0], X an array such that X.shape[0] == op.shape[1],
    Y an array such that Y.shape[0] == op.shape[0],
    the function verifies that:

        - (op @ u).size == op.shape[0],
        - (op.H @ v).size == op.shape[1],
        - (op @ u).conj().T @ v == u.conj().T @ op.H @ v,
        - op @ X is equal to the horizontal concatenation of all op @ X[:, j] for j in {0, ..., X.shape[1]-1}.
        - op.H @ Y is equal to the horizontal concatenation of all op.H @ Y[:, j] for j in {0, ..., X.shape[1]-1}.
        - op @ X @ Y.H == (Y @ (X.H @ op.H)).H

    **Note**: this function has a computational cost (at least similar to the
    cost of op@x), it shouldn't be used into an efficient implementation but
    only to test a LazyLinearOp works properly.

    Example:
        >>> from numpy.random import rand
        >>> from lazylinop import aslazylinearoperator, check_op
        >>> M = rand(12, 14)
        >>> check_op(aslazylinearoperator(M))

    """
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
    # if not np.allclose(op @ X, np.hstack([(op @ X[:, i]).reshape(-1, 1) for i in range(X.shape[1])])):
    #     raise Exception("Wrong operator matrix product")
    # Dot test to check forward - adjoint consistency
    if not np.allclose((op @ u).conj().T @ v, u.conj().T @ (op.H @ v)):
        raise Exception("Operator and its adjoint do not match")
    # if (op.T @ Y).shape[0] != op.shape[1]:
    #     raise Exception("Wrong operator transpose dimension (when multiplying"
    #                     " an array)")
    AY = op.H @ Y
    if AY.shape[0] != op.shape[1]:
        raise Exception("Wrong operator transpose dimension (when multiplying"
                        " an array)")
    for i in range(X.shape[1]):
        if not np.allclose(AY[:, i], op.H @ Y[:, i]):
            raise Exception("Wrong operator adjoint on matrix product")
    del AY
    # if not np.allclose(op.H @ Y, np.hstack([(op.H @ Y[:, i]).reshape(-1, 1) for i in range(X.shape[1])])):
    #     raise Exception("Wrong operator adjoint on matrix product")
    if not np.allclose(AX @ Y.T.conj(), (Y @ AX.T.conj()).T.conj()):
        raise Exception("Wrong operator on (Y @ X.H @ op.H).H")
    # if not np.allclose(op.dot(X) @ Y.T.conj(), (Y @ (X.T.conj() @ op.H)).T.conj()):
    #     raise Exception("Wrong operator on (Y @ X.H @ op.H).H")

def check_op(op):
    """
    Verifies validity assertions on any LazyLinearOp.

    Let op a LazyLinearOp, u a vector of size op.shape[1], v a vector of size
    op.shape[0], X an array such that X.shape[0] == op.shape[1],
    Y an array such that Y.shape[0] == op.shape[0],
    the function verifies that:

        - (op @ u).size == op.shape[0],
        - (op.H @ v).size == op.shape[1],
        - (op @ u).conj().T @ v == u.conj().T @ op.H @ v,
        - op @ X is equal to the horizontal concatenation of all op @ X[:, j] for j in {0, ..., X.shape[1]-1}.
        - op.H @ Y is equal to the horizontal concatenation of all op.H @ Y[:, j] for j in {0, ..., X.shape[1]-1}.
        - op @ X @ Y.H == (Y @ (X.H @ op.H)).H

    **Note**: this function has a computational cost (at least similar to the
    cost of op@x), it shouldn't be used into an efficient implementation but
    only to test a LazyLinearOp works properly.

    Example:
        >>> from numpy.random import rand
        >>> from lazylinop import aslazylinearoperator, check_op
        >>> M = rand(12, 14)
        >>> check_op(aslazylinearoperator(M))

    """
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
    # Dot test to check forward - adjoint consistency
    if not np.allclose((op @ u).conj().T @ v, u.conj().T @ (op.H @ v)):
        raise Exception("Operator and its adjoint do not match")
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

def isLazyLinearOp(obj):
    """
    Returns True if obj is a LazyLinearOp, False otherwise.
    """
    return LazyLinearOp.isLazyLinearOp(obj)

def aslazylinearoperator(obj, shape=None) -> LazyLinearOp:
    """
    Creates a LazyLinearOp based on the object obj which must be of a linear operator compatible type.

    **Note**: obj must support operations and attributes defined in the
    LazyLinearOp class.
    Any operation not supported would raise an exception at evaluation time.

    Args:
        obj:
            the root object on which the LazyLinearOp is based
            (it could be a numpy array, a scipy matrix, a pyfaust.Faust object or
            almost any object that supports the same kind of functions).
        shape:
            defines the shape of the resulting LazyLinearOp. In most cases
            this argument shouldn't be used because we can rely on obj.shape but
            if for any reason obj.shape is not well defined the user can explicitly
            define the shape of the LazyLinearOp (cf. below, the example of
            pylops.Symmetrize defective shape).


    Returns: LazyLinearOp
        a LazyLinearOp instance based on obj.

    Example:
        >>> from lazylinop import aslazylinearoperator
        >>> import numpy as np
        >>> M = np.random.rand(10, 12)
        >>> lM = aslazylinearoperator(M)
        >>> twolM = lM + lM
        >>> twolM
        <10x12 LazyLinearOp with unspecified dtype>
        >>> import pyfaust as pf
        >>> F = pf.rand(10, 12)
        >>> lF = aslazylinearoperator(F)
        >>> twolF = lF + lF
        >>> twolF
        <10x12 LazyLinearOp with unspecified dtype>

		>>> # To illustrate the use of the optional “shape” parameter, let us consider implementing a lazylinearoperator associated with the pylops.Symmetrize linear operator,
		>>> # https://pylops.readthedocs.io/en/latest/api/generated/pylops.Symmetrize.html
		>>> # (version 2.1.0 is used here)
		>>> # which is designed to symmetrize a vector, or a matrix, along some coordinate axis
		>>> from pylops import Symmetrize
		>>> M = np.random.rand(22, 2)
		>>> # Here the matrix M is of shape(22, 2) and we want to symmetrize it vertically (axis == 0), so we build the corresponding symmetrizing operator Sop
		>>> Sop = Symmetrize(M.shape, axis=0)
		>>> # Applying the operator to M works, and the symmetrized matrix has 43 = 2*22-1 rows, and 2 columns (as many as M) as expected
		>>> (Sop @ M).shape
		(43, 2)
		>>> # Since it maps matrices with 22 rows to matrices with 43 rows, the “shape” of Sop should be (43,22) however, the “shape” as provided by pylops is inconsistent

        >>> Sop.shape
        (86, 44)

		>>> # To exploit Sop as a LazyLinearOp we cannot rely on the “shape” given by pylops (otherwise the LazyLinearOp-matrix product wouldn't be properly defined, and would fail on a "dimensions must agree" exception)
		>>> # Thanks to the optional “shape” parameter of aslazylinearoperator, this can be fixed
		>>> lSop = aslazylinearoperator(Sop, shape=(43, 22))
		>>> # now lSop.shape is consistent
		>>> lSop.shape
		(43, 22)
		>>> (lSop @ M).shape
		(43, 2)
		>>> # Besides, Sop @ M is equal to lSop @ M, so all is fine !
		>>> np.allclose(lSop @ M, Sop @ M)
		True


    **See also:** pyfaust.rand, pylops.Symmetrize
    (https://pylops.readthedocs.io/en/latest/api/generated/pylops.Symmetrize.html)

    """
    if isLazyLinearOp(obj):
        return obj
    return LazyLinearOp.create_from_op(obj, shape)
