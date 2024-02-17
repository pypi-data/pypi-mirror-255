"""
Module for polynomial related LazyLinearOps.
"""
import numpy as np
from numpy.polynomial import Polynomial as P
from numpy.polynomial import Chebyshev as T
import scipy as sp
from lazylinop import *
import warnings
warnings.simplefilter(action='always')
from warnings import warn


try:
    import dask
    from dask.distributed import Client, LocalCluster, wait
except ImportError:
    warn("Dask ImportError")


class poly():#P, T):#np.polynomial.Polynomial, np.polynomial.Chebyshev):
    """This class implements a tuple (numpy.polynomial, LazyLinearOp).
    You can add, subtract, multiply and divide two instances p1 and p2.
    Thanks to Python `__call__` you can add two instances p1 and p2 and
    use the syntax `(p1+p2)(Op) @ x` to compute polynomial of LazyLinearOp Op
    applied to a vector x. To compute n-th power of LazyLinearOp applied to
    vector x simply use `p1(Op, n=n) @ x`.
    We rely on NumPy polynomial package to manipulate polynomials.
    To compute `(p1+p2)(Op) @ x` we use Horner's method.
    """

    def __init__(self, p, op=None):
        """Init instance of poly.

        Args:
            p: numpy.polynomial.Polynomial
            op: LazyLinearOp

        References:
            See `numpy.polynomial package <https://numpy.org/doc/stable/reference/routines.polynomials.html>`_ for more details.
        """
        self.__p = p
        self.__op = op

    def _val(self, op=None, basis: str='monomial'):
        """
        Call polyval or chebval according to the basis.
        """
        if self.__op is not None or op is not None:
            print('here', self.__p)
            if isinstance(self.__p, np.polynomial.polynomial.Polynomial):
                return polyval(self.__op if op is None else op, self.__p.coef)
            elif isinstance(self.__p, np.polynomial.Chebyshev):
                return chebval(self.__op if op is None else op, self.__p.coef)
            else:
                pass
        else:
            raise Exception('LazyLinearOp is None.')

    def __call__(self, op=None, basis: str='monomial', n: int=1):
        """
        Thanks to Python __call__ instance behaves like function.
        """
        print('test', self.__p)
        if n is not None and n > 1:
            # Compute n-th powers of self.__L
            return power(n, self.__op if op is None else op, use_numba=True)
        else:
            # Compute polynomial of LazyLinearOp
            return poly._val(self, op, basis)

    @property
    def op(self):
        return self.__op

    @op.setter
    def op(self, val):
        """Change LazyLinearOp of self instance.

        Args:
            val: LazyLinearOp
        """
        self.__op = val

    @property
    def p(self):
        return self.__p

    @p.setter
    def p(self, val):
        """Change basis of self instance.

        Args:
            val: numpy.polynomial
        """
        self.__p = val

    def __add__(self, p):
        """Add two poly instances and return poly instance.

        Args:
            p: poly instance

        Examples:
            >>> from numpy.polynomial import Polynomial as P
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.poly(op=None, p=P([1.0, 1.0]))
            >>> p2 = p1 + p1
        """
        return poly(op=None, p=self.__p + p.p)

    def __sub__(self, p):
        """Subtract two poly instances and return poly instance.

        Args:
            p: poly instance

        Examples:
            >>> from numpy.polynomial import Polynomial as P
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.poly(op=None, coeffs=P([1.0, 1.0]))
            >>> p2 = p1 - p1
        """
        return poly(op=None, p=self.__p - p.p)

    def __mul__(self, p):
        """Multiply two poly instances and return poly instance.

        Args:
            p: poly instance

        Examples:
            >>> from numpy.polynomial import Polynomial as P
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.poly(op=None, coeffs=P([1.0, 1.0]))
            >>> p2 = p1 * p1
        """
        return poly(op=None, p=self.__p * p.p)

    def __divmod__(self, p):
        """Divide two poly instances and return two poly instances
        corresponding to quotient and remainder.

        Args:
            p: poly instance

        Examples:
            >>> from numpy.polynomial import Polynomial as P
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.poly(op=None, coeffs=P([3.0, 1.0]))
            >>> p2 = p.poly(op=None, coeffs=P([1.0, 2.0]))
            >>> p, q = p1 / p2
        """
        ps = divmod(self.__p, p.p)
        return poly(op=None, p=ps[0]), poly(op=None, p=ps[1])

    def __floordiv__(self, p):
        """Divide (floor) two poly instances and return poly instance.

        Args:
            p: poly instance

        Examples:
            >>> from numpy.polynomial import Polynomial as P
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.poly(op=None, coeffs=P([1.0, 1.0]))
            >>> p2 = p1 // p1
        """
        return poly(op=None, p=self.__p // p.p)

    def __mod__(self, p):
        """Divide (modulo) two poly instances and return poly instance.

        Args:
            p: poly instance

        Examples:
            >>> from numpy.polynomial import Polynomial as P
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.poly(op=None, coeffs=P([1.0, 1.0]))
            >>> p2 = p1 % p1
        """
        return poly(op=None, p=self.__p % p.p)


class lpoly():
    """This class implements a polynomial that is described
    by coefficients, roots and basis representation (monomial or Chebyshev).
    If coefficients are not given, compute from roots.
    If roots are not given, compute from coefficients.
    Therefore, coefficients and roots from a poly instance are always not None.
    It is also possible to assign a LazyLinearOp. You can add, subtract
    and multiply two instances p1 and p2. Thanks to Python `__call__`
    you can add two instances p1 and p2 and use the syntax `(p1+p2)(Op) @ x`
    to compute polynomial of LazyLinearOp Op applied to a vector x.
    To compute n-th power of LazyLinearOp applied to vector x simply use `p1(Op, n=n) @ x`.
    Thanks to Numpy/SciPy functions you can switch between monomial and
    Chebyshev basis.
    WARNING: :py:class:`polynomial.poly` is deprecated, please have a
    look to :py:class:`polynomial.poly`.
    """

    def __init__(self, L=None, coeffs=None, roots=None, basis: str='monomial'):
        """Init instance of poly.

        Args:
            L: LazyLinearOp
            coeffs: 1d or 2d array
            roots: 1d or 2d array
            basis: str, optional
        """
        # lazy linear operator
        self.__L = L
        # basis
        if basis != 'monomial' and basis != 'chebyshev':
            raise ValueError('basis must be either monomial or chebyshev.')
        else:
            self.__basis = basis
        # Polynomial coefficients and roots from a poly
        # instance are always not None.
        if coeffs is not None and roots is None:
            self.coeffs = coeffs
            if basis == 'monomial':
                self.roots = np.polynomial.polynomial.polyroots(coeffs)
            elif basis == 'chebyshev':
                self.roots = np.polynomial.chebyshev.chebroots(coeffs)
        elif coeffs is not None and roots is not None:
            self.coeffs = coeffs
            self.roots = roots
        elif coeffs is None and roots is not None:
            if basis == 'monomial':
                self.coeffs = np.polynomial.polynomial.polyfromroots(roots)
            elif basis == 'chebyshev':
                self.coeffs = np.polynomial.chebyshev.chebfromroots(roots)
            self.roots = roots
        else:
            raise Exception('Expect coeffs or roots to be different from None.')

    def print(self):
        """Print polynomial details.
        """
        print('coefficients:')
        print(self.coeffs)
        print('roots:')
        print(self.roots)
        print('basis:')
        print(self.__basis)
        print('LazyLinearOp:')
        print(self.__L)

    @property
    def L(self):
        return self.__L

    @L.setter
    def L(self, op):
        """Change LazyLinearOp of self instance.

        Args:
            op: LazyLinearOp
        """
        self.__L = op

    def get_coeffs(self):
        return self.coeffs

    def set_coeffs(self, coeffs, basis):
        """Change coefficients of self instance.

        Args:
            roots: 1d or 2d array
        """
        self.coeffs = coeffs
        # Polynomial coefficients and roots from a poly
        # instance are always not None.
        if basis == 'monomial':
            self.roots = np.polynomial.polynomial.polyroots(coeffs)
        else:
            self.roots = np.polynomial.chebyshev.chebroots(coeffs)

    # @property
    # def coeffs(self):
    #     return self.coeffs

    # @coeffs.setter
    # def coeffs(self, coeffs, basis):
    #     """Change coefficients of self instance.

    #     Args:
    #         roots: 1d or 2d array
    #     """
    #     self.coeffs = coeffs
    #     if basis == 'monomial':
    #         self.roots = np.polynomial.polynomial.polyroots(coeffs)
    #     else:
    #         self.roots = np.polynomial.chebyshev.chebroots(coeffs)

    def get_roots(self):
        return self.roots

    def set_roots(self, roots):
        """Change roots of self instance.

        Args:
            roots: 1d or 2d array
        """
        self.roots = roots
        # Polynomial coefficients and roots from a poly
        # instance are always not None.
        if basis == 'monomial':
            self.coeffs = np.polynomial.polynomial.polyfromroots(roots)
        else:
            self.coeffs = np.polynomial.chebyshev.chebfromroots(roots)

    # @property
    # def roots(self):
    #     return self.roots

    # @roots.setter
    # def roots(self, roots):
    #     """Change roots of self instance.

    #     Args:
    #         roots: 1d or 2d array
    #     """
    #     self.roots = roots
    #     if basis == 'monomial':
    #         self.coeffs = np.polynomial.polynomial.polyfromroots(roots)
    #     else:
    #         self.coeffs = np.polynomial.chebyshev.chebfromroots(roots)

    @property
    def basis(self):
        return self.__basis

    @basis.setter
    def basis(self, basis):
        """Change basis of self instance.

        Args:
            basis: str
        """
        if self.__basis != basis:
            if self.__basis == 'monomial' and basis == 'chebyshev':
                self.coeffs = np.polynomial.chebyshev.poly2cheb(self.coeffs)
                self.roots = np.polynomial.chebyshev.chebroots(self.coeffs)
            if self.__basis == 'chebyshev' and basis == 'monomial':
                self.coeffs = np.polynomial.chebyshev.cheb2poly(self.coeffs)
                self.roots = np.polynomial.polynomial.polyroots(self.coeffs)
            self.__basis = basis

    # Evaluation of a (Chebyshev) polynomial from coefficients
    def _val(self, L=None, basis: str='monomial'):
        # Check if coeffs is not None
        if self.coeffs is None:
            if self.__basis == 'monomial':
                self.coeffs = np.polynomial.polynomial.polyfromroots(self.roots)
            elif self.__basis == 'chebyshev':
                self.coeffs = np.polynomial.chebyshev.chebfromroots(self.roots)
            else:
                pass
        # Call polyval according to the basis
        if basis == 'monomial':
            if self.__L is not None or L is not None:
                if self.__basis == 'monomial':
                    return polyval(self.__L if L is None else L, self.coeffs)
                else:
                    return polyval(self.__L if L is None else L,
                                   np.polynomial.chebyshev.cheb2poly(self.coeffs))
            else:
                raise Exception('LazyLinearOp is None.')
        elif basis == 'chebyshev':
            if self.__L is not None or L is not None:
                if self.__basis == 'monomial':
                    return chebval(
                        self.__L if L is None else L,
                        np.polynomial.chebyshev.poly2cheb(self.coeffs)
                    )
                else:
                    return chebval(self.__L if L is None else L, self.coeffs)
            else:
                raise Exception('LazyLinearOp is None.')
        else:
            pass

    # Thanks to Python __call__ instance behaves like function
    def __call__(self, L=None, basis: str='monomial', n: int=1):
        if n is not None and n > 1:
            # Compute n-th powers of self.__L
            return power(n, self.__L if L is None else L, use_numba=True)
        else:
            # Compute polynomial of LazyLinearOp
            return lpoly._val(self, L, basis)

    def __add__(self, p):
        """Add two poly instances and return poly instance
        with monomial basis.

        Args:
            p: poly instance

        Examples:
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.lpoly(L=None, coeffs=[1.0, 1.0], basis='monomial')
            >>> p2 = p1 + p1
        """
        coeffs1 = self.coeffs
        coeffs2 = p.coeffs
        if self.__basis == 'chebyshev':
            coeffs1 = np.polynomial.chebyshev.cheb2poly(coeffs1)
        if p.basis == 'chebyshev':
            coeffs2 = np.polynomial.chebyshev.cheb2poly(coeffs2)
        coeffs = np.polynomial.polynomial.polyadd(coeffs1, coeffs2)
        return lpoly(L=None, coeffs=coeffs, roots=None, basis='monomial')

    def polyadd(self, c):
        """Add coefficients c to `self.coeffs`.

        Args:
            c: 1d or 2d array
        """
        if self.__basis == 'monomial':
            self.coeffs = np.polynomial.polynomial.polyadd(self.coeffs, c)
            self.roots = np.polynomial.polynomial.polyroots(self.coeffs)
        elif self.__basis == 'chebyshev':
            self.coeffs = np.polynomial.chebyshev.chebadd(self.coeffs, c)
            self.roots = np.polynomial.chebyshev.chebroots(self.coeffs)

    def __sub__(self, p):
        """Subtract two poly instances and return poly instance
        with monomial basis.

        Args:
            p: poly instance

        Examples:
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.lpoly(L=None, coeffs=[1.0, 1.0], basis='monomial')
            >>> p2 = p1 - p1
        """
        coeffs1 = self.coeffs
        coeffs2 = p.coeffs
        if self.__basis == 'chebyshev':
            coeffs1 = np.polynomial.chebyshev.cheb2poly(coeffs1)
        if p.basis == 'chebyshev':
            coeffs2 = np.polynomial.chebyshev.cheb2poly(coeffs2)
        coeffs = np.polynomial.polynomial.polysub(coeffs1, coeffs2)
        return lpoly(L=None, coeffs=coeffs, roots=None, basis='monomial')

    def polysub(self, c):
        """Subtract coefficients c to `self.coeffs`.

        Args:
            c: 1d or 2d array
        """
        if self.__basis == 'monomial':
            self.coeffs = np.polynomial.polynomial.polysub(self.coeffs, c)
            self.roots = np.polynomial.polynomial.polyroots(self.coeffs)
        elif self.__basis == 'chebyshev':
            self.coeffs = np.polynomial.chebyshev.chebsub(self.coeffs, c)
            self.roots = np.polynomial.chebyshev.chebroots(self.coeffs)

    def __mul__(self, p):
        """Multiply two poly instances.

        Args:
            p: poly instance

        Examples:
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.lpoly(L=None, coeffs=[1.0, 1.0], basis='monomial')
            >>> p2 = p1 * p1
        """
        coeffs1 = self.coeffs
        coeffs2 = p.coeffs
        if self.__basis == 'chebyshev':
            coeffs1 = np.polynomial.chebyshev.cheb2poly(coeffs1)
        if p.basis == 'chebyshev':
            coeffs2 = np.polynomial.chebyshev.cheb2poly(coeffs2)
        coeffs = np.polynomial.polynomial.polymul(coeffs1, coeffs2)
        return lpoly(L=None, coeffs=coeffs, roots=None, basis='monomial')

    def polymul(self, c):
        """Multiply coefficients c by and to `self.coeffs`.

        Args:
            c: 1d or 2d array
        """
        self.coeffs = np.polynomial.polynomial.polymul(self.coeffs, c)
        self.roots = np.polynomial.polynomial.polyroots(self.coeffs)

    def __floordiv__(self, p):
        """Divide (floor division) two poly instances.

        Args:
            p: poly instance

        Examples:
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.lpoly(L=None, coeffs=[1.0, 1.0], basis='monomial')
            >>> p2 = p1 // p1
        """
        coeffs1 = self.coeffs
        coeffs2 = p.coeffs
        if self.__basis == 'chebyshev':
            coeffs1 = np.polynomial.chebyshev.cheb2poly(coeffs1)
        if p.basis == 'chebyshev':
            coeffs2 = np.polynomial.chebyshev.cheb2poly(coeffs2)
        coeffs = np.polynomial.polynomial.polydiv(coeffs1, coeffs2)
        return lpoly(L=None, coeffs=coeffs[0], roots=None, basis='monomial')

    def __truediv__(self, p):
        """Divide (true division) two poly instances.

        Args:
            p: poly instance

        Examples:
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.lpoly(L=None, coeffs=[1.0, 1.0], basis='monomial')
            >>> p2 = p1 / p1
        """
        coeffs1 = self.coeffs
        coeffs2 = p.coeffs
        if self.__basis == 'chebyshev':
            coeffs1 = np.polynomial.chebyshev.cheb2poly(coeffs1)
        if p.basis == 'chebyshev':
            coeffs2 = np.polynomial.chebyshev.cheb2poly(coeffs2)
        coeffs = np.polynomial.polynomial.polydiv(coeffs1, coeffs2)
        return lpoly(L=None, coeffs=coeffs, roots=None, basis='monomial')

    def polydiv(self, c, div: str='true'):
        """Divide coefficients c by and to `self.coeffs`.

        Args:
            c: 1d or 2d array
            div: str, optional default is 'true'
            div must be either 'true', 'floor' or 'modulo'.
        """
        if self.__basis == 'monomial':
            if div == 'true':
                # TODO
                self.coeffs = np.polynomial.polynomial.polydiv(self.coeffs, c)
            elif div == 'floor':
                self.coeffs = np.polynomial.polynomial.polydiv(self.coeffs, c)[0]
            elif div == 'modulo':
                self.coeffs = np.polynomial.polynomial.polydiv(self.coeffs, c)[1]
            self.roots = np.polynomial.polynomial.polyroots(self.coeffs)
        elif self.__basis == 'chebyshev':
            if div == 'true':
                # TODO
                self.coeffs = np.polynomial.chebyshev.chebdiv(self.coeffs, c)
            elif div == 'floor':
                self.coeffs = np.polynomial.chebyshev.chebdiv(self.coeffs, c)[0]
            elif div == 'modulo':
                self.coeffs = np.polynomial.chebyshev.chebdiv(self.coeffs, c)[1]
            self.roots = np.polynomial.chebyshev.chebroots(self.coeffs)

    def __mod__(self, p):
        """Divide two poly instances and keep the modulo.

        Args:
            p: poly instance

        Examples:
            >>> import lazylinop.wip.polynomial as p
            >>> p1 = p.lpoly(L=None, coeffs=[1.0, 1.0], basis='monomial')
            >>> p2 = p.lpoly(L=None, coeffs=[1.0, 1.0, 2.0], basis='monomial')
            >>> p3 = p1 % p2
        """
        coeffs1 = self.coeffs
        coeffs2 = p.coeffs
        if self.__basis == 'monomial':
            if p.basis == 'chebyshev':
                coeffs2 = np.polynomial.chebyshev.cheb2poly(coeffs2)
            coeffs = np.polynomial.polynomial.polydiv(coeffs1, coeffs2)[1]
            return lpoly(L=None, coeffs=coeffs, roots=None, basis='monomial')
        elif self.__basis == 'chebyshev':
            if p.basis == 'monomial':
                coeffs2 = np.polynomial.polynomial.poly2cheb(coeffs2)
            coeffs = np.polynomial.chebyshev.chebdiv(coeffs1, coeffs2)[1]
            return lpoly(L=None, coeffs=coeffs, roots=None, basis='chebyshev')
        else:
            return None

    def __eq__(self, p):
        """Check if two polynomial are equal.
        """
        return self.__basis == p.basis and np.allclose(self.coeffs, p.get_coeffs())

    def polyder(self, m: int=1, scl: float=1.0):
        """Constructs the m-th derivative of the polynomial c.
        
           References:
           See `NumPy, SciPy polyint <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyder.html>`_ for more details.
        """
        if self.__basis == 'monomial':
            self.coeffs = np.polynomial.polynomial.polyder(c, m, scl)
            self.roots = np.polynomial.polynomial.polyroots(self.coeffs)
        elif self.__basis == 'chebyshev':
            self.coeffs = np.polynomial.chebyshev.chebder(c, m, scl)
            self.roots = np.polynomial.chebyshev.chebroots(self.coeffs)
        else:
            pass

    def polyint(self, m: int=1, k: list=[], lbnd: float=0.0, scl: float=1.0):
        """Constructs the m-th integral of the polynomial c.

           References:
           See `NumPy, SciPy polyint <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyint.html>`_ for more details.
        """
        if self.__basis == 'monomial':
            self.coeff = np.polynomial.polynomial.polyint(c, m, k, lbnd, scl)
            self.roots = np.polynomial.polynomial.polyroots(self.coeffs)
        elif self.__basis == 'chebyshev':
            self.coeff = np.polynomial.chebyshev.chebint(c, m, k, lbnd, scl)
            self.roots = np.polynomial.chebyshev.chebroots(self.coeffs)
        else:
            pass


def chebval(L, c):
    r"""Constructs a Chebyshev polynomial of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the batch size.
    The k-th Chebyshev polynomial can be computed by recurrence:
    T_0(X)     = 1
    T_1(X)     = X
    T_{k+1}(X) = 2*X*T_k(X) - T_{k-1}(X)

    Args:
        L: 2d array
            Linear operator.
        c: 1d array
            List of Chebyshev polynomial(s) coefficients.
            If the size of the 1d array is n + 1 then the largest power of the polynomial is n.
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1]).
            :math:`P(L)` is equal to :math:`c_0 * Id + c_1 * T_1(L) + \cdots + c_n * T_n(L)`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.
        ValueError
            c must be a 1d array, c.shape=(D, ).

    Examples:

    References:
        See also `Wikipedia <https://en.wikipedia.org/wiki/Chebyshev_polynomials>`_.
        See also `Polynomial magic web page <https://francisbach.com/chebyshev-polynomials/>`_.
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebval.html>`_.
    """

    if type(c) is list:
        c = np.asarray(c)

    if c.ndim != 1:
        raise ValueError('c must be a 1d array, c.shape=(D, ).')
    D = c.shape[0]

    def _matmat(L, x, c):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is not equal to the # of rows of x.")
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        output = np.empty((L.shape[0], batch_size), dtype=x.dtype)
        T1x = np.empty(L.shape[0], dtype=x.dtype)
        T2x = np.empty(L.shape[0], dtype=x.dtype)
        # loop over the batch size
        for b in range(batch_size):
            T0x = np.multiply(c[0], x[:, b])
            np.copyto(output[:, b], T0x)
            if D > 1:
                # loop over the coefficients
                for i in range(1, D):
                    if i == 1:
                        np.copyto(T1x, L @ x[:, b])
                        if c[i] == 0.0:
                            continue
                        else:
                            np.add(output[:, b], np.multiply(c[i], T1x), out=output[:, b])
                    else:
                        np.copyto(T2x, np.subtract(np.multiply(2.0, L @ T1x), T0x))
                        # Recurrence
                        np.copyto(T0x, T1x)
                        np.copyto(T1x, T2x)
                        if c[i] == 0.0:
                            continue
                        else:
                            np.add(output[:, b], np.multiply(c[i], T2x), out=output[:, b])
        return output.ravel() if is_1d else output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(L, x, c),
        rmatmat=lambda x: _matmat(L.T.conj(), x, c)
    )


def _mchebval(L, c):
    r"""Constructs a Chebyshev polynomial of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P_j(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the n-th polynomial.
    The k-th Chebyshev polynomial can be computed by recurrence:
    T_0(X)     = 1
    T_1(X)     = X
    T_{k+1}(X) = 2*X*T_k(X) - T_{k-1}(X)

    Args:
        L: 2d array
            Linear operator.
        c: 1d or 2d array
            List of Chebyshev polynomial(s) coefficients.
            If the size of the 1d array is n + 1 then the largest power of the polynomial is n.
            If the array is 2d (shape (n + 1, m + 1)), the function considers one polynomial
            per column (m + 1 polynomials in total).
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1], m + 1).
            :math:`P_j(L)` is equal to :math:`c_{0,j} * Id + c_{1,j} * T_1(L) + \cdots + c_{n,j} * T_n(L)` with :math:`j\in\left[0,m\right]`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `Wikipedia <https://en.wikipedia.org/wiki/Chebyshev_polynomials>`_.
        See also `Polynomial magic web page <https://francisbach.com/chebyshev-polynomials/>`_.
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebval.html>`_.
    """

    if type(c) is list:
        c = np.asarray(c)

    if c.ndim == 1:
        # only one polynomial
        c = c.reshape(c.shape[0], 1)
    D, C = c.shape

    def _matmat(L, x, c):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is not equal to the # of rows of x.")
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        output = np.empty((L.shape[0], batch_size, C), dtype=x.dtype)
        T1x = np.empty(L.shape[0], dtype=x.dtype)
        T2x = np.empty(L.shape[0], dtype=x.dtype)
        # loop over the batch size
        for b in range(batch_size):
            # loop over the polynomials
            for p in range(C):
                T0x = np.multiply(c[0, p], x[:, b])
                np.copyto(output[:, b, p], T0x)
                if D > 1:
                    # loop over the coefficients
                    for i in range(1, D):
                        if i == 1:
                            np.copyto(T1x, L @ x[:, b])
                            if c[i, p] == 0.0:
                                continue
                            else:
                                np.add(output[:, b, p], np.multiply(c[i, p], T1x), out=output[:, b, p])
                        else:
                            np.copyto(T2x, np.subtract(np.multiply(2.0, L @ T1x), T0x))
                            # Recurrence
                            np.copyto(T0x, T1x)
                            np.copyto(T1x, T2x)
                            if c[i, p] == 0.0:
                                continue
                            else:
                                np.add(output[:, b, p], np.multiply(c[i, p], T2x), out=output[:, b, p])
        if C == 1:
            return output[:, 0, 0] if is_1d else output[:, :, 0]
        else:
            return output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(L, x, c),
        rmatmat=lambda x: _matmat(L.T.conj(), x, c)
    )


def chebvalfromroots(L, r):
    r"""Constructs a Chebyshev polynomial (from roots) of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a 1d or 2d array. The first dimension is the result of P(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the batch size.
    The k-th Chebyshev polynomial can be computed by recurrence:
    T_0(X)     = 1
    T_1(X)     = X
    T_{k+1}(X) = 2*X*T_k(X) - T_{k-1}(X)

    Args:
        L: 2d array
            Linear operator.
        r: 1d array
            List of Chebyshev polynomial roots.
            If the size of the list is n + 1 then the largest power of the polynomial is n.
            :math:`P(L)` is equal to :math:`(L - r_0 * Id) * (L - r_1 * Id) * ... * (L - r_n * Id)`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            r must be a 1d array, c.shape=(D, ).

    Examples:

    References:
        See also `Wikipedia <https://en.wikipedia.org/wiki/Chebyshev_polynomials>`_.
        See also `Polynomial magic web page <https://francisbach.com/chebyshev-polynomials/>`_.
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebval.html>`_.
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebfromroots.html>`_.
        See also :py:func:`chebval`.
    """
    if type(r) is list:
        r = np.asarray(r)
    if r.ndim != 1:
        raise ValueError('r must be a 1d array, c.shape=(D, ).')
    return chebval(L, np.polynomial.chebyshev.chebfromroots(r))


def _mchebvalfromroots(L, r):
    r"""Constructs a Chebyshev polynomial (from roots) of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P_j(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the n-th polynomial.
    The k-th Chebyshev polynomial can be computed by recurrence:
    T_0(X)     = 1
    T_1(X)     = X
    T_{k+1}(X) = 2*X*T_k(X) - T_{k-1}(X)

    Args:
        L: 2d array
            Linear operator.
        r: 1d or 2d array
            List of Chebyshev polynomial(s) roots.
            If the size of the list is n + 1 then the largest power of the polynomial is n.
            If the array is 2d (shape (m + 1, n + 1)), the function considers one polynomial
            per column (m + 1 polynomials in total).
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1], m + 1).
            :math:`P_j(L)` is equal to :math:`(L - r_{0,j} * Id) * (L - r_{1,j} * Id) * ... * (L - r_{n,j} * Id)` with :math:`j\in\left[0,m\right]`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `Wikipedia <https://en.wikipedia.org/wiki/Chebyshev_polynomials>`_.
        See also `Polynomial magic web page <https://francisbach.com/chebyshev-polynomials/>`_.
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebval.html>`_.
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebfromroots.html>`_.
        See also :py:func:`chebval`.
    """
    if type(r) is list:
        r = np.asarray(r)
    if r.ndim == 1:
        coeffs = np.polynomial.chebyshev.chebfromroots(r)
    else:
        x, y = r.shape
        coeffs = np.empty((x + 1, y), dtype=r.dtype)
        for i in range(y):
            coeffs[:, i] = np.polynomial.chebyshev.chebfromroots(r[:, i])
    return chebval(L, coeffs)


def chebadd(c1, c2, L):
    """Constructs a Chebyshev polynomial c1 + c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the addition of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] + c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy polyadd function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebadd.html>`_ for more details.
        See also :py:func:`chebval`.
    """
    c = np.polynomial.chebyshev.chebadd(c1, c2)
    return chebval(L, c)


def chebsub(c1, c2, L):
    """Constructs a Chebyshev polynomial c1 - c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the subtraction of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] - c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy chebsub function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebsub.html>`_ for more details.
        See also :py:func:`chebval`.
    """
    c = np.polynomial.chebyshev.chebsub(c1, c2)
    return chebval(L, c)


def chebmul(c1, c2, L):
    """Constructs a Chebyshev polynomial c1 * c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the multiplication of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] * c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy chebmul function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebmul.html>`_ for more details.
        See also :py:func:`chebval`.
    """
    c = np.polynomial.chebyshev.chebmul(c1, c2)
    return chebval(L, c)


def chebdiv(c1, c2, L):
    """Constructs a Chebysehv polynomial c1 / c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[n] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the multiplication of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] / c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy chebdiv function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebdiv.html>`_ for more details.
        See also :py:func:`chebval`.
    """
    c = np.polynomial.chebyshev.chebdiv(c1, c2)
    return chebval(L, c)


def polyval(L, c):
    r"""Constructs a polynomial of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a 2d array. The first dimension is the result of P(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the
    batch size. Computation of P(L) @ X uses Horner method.

    Args:
        L: 2d array
            Linear operator.
        c: 1d array
            List of polynomial coefficients.
            If the size of the 1d array is n + 1 then the largest power of the polynomial is n.
            If the array is 2d consider only the first column/polynomial.
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1]).
            :math:`P(L)` is equal to :math:`c_0 * Id + c_1 * L^1 + \cdots + c_n * L^n` with.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also :py:func:`polyvalfromroots`.
    """

    if type(c) is list:
        c = np.asarray(c)

    if c.ndim == 2:
        # Only one polynomial
        c = np.copy(c[:, 0].flatten())
    D = c.shape[0]

    def _matmat(L, x, c):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is not equal to the # of rows of x.")
        if isLazyLinearOp(x):
            # Handle the case x is a LazyLinearOp
            Lx = L @ x
            Op = c[0] * (eye(L.shape[0], n=L.shape[1], k=0) @ x)
            if D > 1:
                # Loop over the coefficients
                for i in range(1, D):
                    Lx = L @ x if i == 1 else L @ Lx
                    if c[i] == 0.0:
                        continue
                    else:
                        Op = Op + c[i] * Lx
            return Op
        else:
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            output = np.empty((L.shape[0], batch_size), dtype=x.dtype)
            Lx = np.empty(L.shape[0], dtype=x.dtype)
            # Loop over the batch size
            for b in range(batch_size):
                output[:, b] = np.multiply(c[0], x[:, b])
                if D > 1:
                    # Loop over the coefficients
                    for i in range(1, D):
                        if i == 1:
                            np.copyto(Lx, L @ x[:, b])
                        else:
                            np.copyto(Lx, L @ Lx)
                        if c[i] == 0.0:
                            continue
                        else:
                            np.add(output[:, b], np.multiply(c[i], Lx), out=output[:, b])
            return output.ravel() if is_1d else output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(L, x, c),
        rmatmat=lambda x: _matmat(L.T.conj(), x, c)
    )


def _mpolyval(L, c):
    r"""Constructs a polynomial of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the j-th polynomial.
    Computation of P(L) @ X uses Horner method.

    Args:
        L: 2d array
            Linear operator.
        c: 1d or 2d array
            List of polynomial(s) coefficients.
            If the size of the 1d array is n + 1 then the largest power of the polynomial is n.
            If the array is 2d (shape (n + 1, m + 1)), the function considers one polynomial
            per column (m + 1 polynomials in total).
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1], m + 1).
            :math:`P_j(L)` is equal to :math:`c_{0,j} * Id + c_{1,j} * L^1 + \cdots + c_{n,j} * L^n` with :math:`j\in\left[0,m\right]`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also :py:func:`polyvalfromroots`.
    """

    if type(c) is list:
        c = np.asarray(c)

    if c.ndim == 1:
        # Only one polynomial
        c = c.reshape(c.shape[0], 1)
    D, C = c.shape

    def _matmat(L, x, c):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is not equal to the # of rows of x.")
        if isLazyLinearOp(x):
            # Handle the case x is a LazyLinearOp
            Lx = L @ x
            Ops = [c[0, p] * (eye(L.shape[0], n=L.shape[1], k=0) @ x) for p in range(C)]
            if D > 1:
                # Loop over the polynomials
                for p in range(C):
                    # Loop over the coefficients
                    for i in range(1, D):
                        Lx = L @ x if i == 1 else L @ Lx
                        if c[i, p] == 0.0:
                            continue
                        else:
                            Ops[p] = Ops[p] + c[i, p] * Lx
            return Ops
        else:
            if x.ndim == 1:
                is_1d = True
                x = x.reshape(x.shape[0], 1)
            else:
                is_1d = False
            batch_size = x.shape[1]
            output = np.empty((L.shape[0], batch_size, C), dtype=x.dtype)
            Lx = np.empty(L.shape[0], dtype=x.dtype)
            # Loop over the batch size
            for b in range(batch_size):
                # Loop over the polynomials
                for p in range(C):
                    output[:, b, p] = np.multiply(c[0, p], x[:, b])
                    if D > 1:
                        # Loop over the coefficients
                        for i in range(1, D):
                            if i == 1:
                                np.copyto(Lx, L @ x[:, b])
                            else:
                                np.copyto(Lx, L @ Lx)
                            if c[i, p] == 0.0:
                                continue
                            else:
                                np.add(output[:, b, p], np.multiply(c[i, p], Lx), out=output[:, b, p])
            if C == 1:
                return output[:, 0, 0] if is_1d else output[:, :, 0]
            else:
                return output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(L, x, c),
        rmatmat=lambda x: _matmat(L.T.conj(), x, c)
    )


def polyvalfromroots(L, r):
    r"""Constructs a polynomial (from roots) of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a 2d array. The first dimension is the result of P(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the batch size.

    Args:
        L: 2d array
            Linear operator.
        r: 1d array
            List of polynomial roots.
            If the size of the 1d array is n + 1 then the largest power of the polynomial is n.
            If the array is 2d, the function considers only the first column/polynomial.
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1]).
            :math:`P(L)` is equal to :math:`(L - r_0 * Id) * (L - r_1 * Id) * \cdots * (L - r_n * Id)`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also :py:func:`polyval`.
    """

    if r.ndim == 2:
        # only one polynomial
        r = np.copy(r[:, 0])
    R = r.shape[0]

    def _matmat(r, L, x):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is not equal to the # of rows of x.")
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        output = np.empty((L.shape[0], batch_size), dtype=x.dtype)
        Lx = np.empty(L.shape[0], dtype=x.dtype)
        # loop over the batch size (Dask ?)
        for b in range(batch_size):
            # loop over the roots
            if r[R - 1] == 0.0:
                np.copyto(Lx, L @ x[:, b])
            else:
                np.copyto(Lx, np.subtract(L @ x[:, b], np.multiply(r[R - 1], x[:, b])))
            if R > 1:
                for i in range(1, R):
                    if r[R - 1 - i] == 0.0:
                        np.copyto(Lx, L @ Lx)
                    else:
                        np.copyto(Lx, np.subtract(L @ Lx, np.multiply(r[R - 1 - i], Lx)))
            np.copyto(output[:, b], Lx)
        return output.ravel() if is_1d else output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(r, L, x),
        rmatmat=lambda x: _matmat(r, L.T.conj(), x)
    )


def _mpolyvalfromroots(L, r):
    r"""Constructs a polynomial (from roots) of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P_j(L) @ X[:, b]
    where b is the b-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the j-th polynomial.

    Args:
        L: 2d array
            Linear operator.
        r: 1d or 2d array
            List of polynomial(s) roots.
            If the size of the 1d array is n + 1 then the largest power of the polynomial is n.
            If the array is 2d (shape (n + 1, m + 1)), the function considers one polynomial
            per column (m + 1 polynomials in total).
            The shape of the output P(L) @ X is (L.shape[0], X.shape[1], m + 1).
            :math:`P_j(L)` is equal to :math:`(L - r_{0,0} * Id) * (L - r_{1,j} * Id) * \cdots * (L - r_{n,1} * Id)` with :math:`j\in\left[0,m\right]`.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also :py:func:`polyval`.
    """

    if r.ndim == 1:
        # only one polynomial
        r = r.reshape(r.shape[0], 1)
    R, P = r.shape

    def _matmat(r, L, x):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is not equal to the # of rows of x.")
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        output = np.empty((L.shape[0], batch_size, P), dtype=x.dtype)
        Lx = np.empty(L.shape[0], dtype=x.dtype)
        # loop over the batch size (Dask ?)
        for b in range(batch_size):
            # loop over the polynomials
            for p in range(P):
                # loop over the roots
                if r[R - 1, p] == 0.0:
                    np.copyto(Lx, L @ x[:, b])
                else:
                    np.copyto(Lx, np.subtract(L @ x[:, b], np.multiply(r[R - 1, p], x[:, b])))
                if R > 1:
                    for i in range(1, R):
                        if r[R - 1 - i, p] == 0.0:
                            np.copyto(Lx, L @ Lx)
                        else:
                            np.copyto(Lx, np.subtract(L @ Lx, np.multiply(r[R - 1 - i, p], Lx)))
                np.copyto(output[:, b, p], Lx)
        if P == 1:
            return output[:, 0, 0] if is_1d else output[:, :, 0]
        else:
            return output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(r, L, x),
        rmatmat=lambda x: _matmat(r, L.T.conj(), x)
    )


def power(n, L, use_numba: bool=False):
    """Constructs power L^n of linear operator L as a lazy linear operator P(L).

    Args:
        n: int
            Raise the linear operator to degree n.
        L: 2d array
            Linear operator.
        use_numba: bool, optional
            If True, use prange from Numba (default is False)
            to compute batch in parallel.
            It is useful only and only if the batch size and
            the length of a are big enough.

    Returns:
        LazyLinearOp

    Raises:

    Examples:
        >>> from lazylinop.wip.polynomial import power
        >>> Op = power(3, eye(3, n=3, k=0))
        >>> x = np.full(3, 1.0)
        >>> np.allclose(Op @ x, x)
        True
        >>> Op = power(3, eye(3, n=3, k=1))
        >>> x = np.full(3, 1.0)
        >>> np.allclose(Op @ x, np.zeros(3, dtype=np.float_))
        True

    References:
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
    """

    def _matmat(n, L, x):

        import numba as nb
        from numba import prange, set_num_threads, threading_layer
        nb.config.DISABLE_JIT = int(not use_numba)
        nb.config.THREADING_LAYER = 'omp'
        if not use_numba:
            nb.config.DISABLE_JIT = 1

        def _1d(n, L, x):
            output = L @ x
            if n > 1:
                for n in range(1, n):
                    output[:] = L @ output[:]
            return output

        def _2d_no_numba(n, L, x):
            output = L @ x
            if n > 1:
                for n in range(1, n):
                    output[:, :] = L @ output[:, :]
            return output

        @nb.jit(nopython=True, parallel=True, cache=True)
        def _2d(n, L, x):
            batch_size = x.shape[1]
            output = np.empty((L.shape[0], batch_size), dtype=x.dtype)
            # loop over the batch size
            for b in prange(batch_size):
                output[:, b] = L @ x[: ,b]
                if n > 1:
                    for n in range(1, n):
                        output[:, b] = L @ output[:, b]
            return output

        if use_numba:
            return _1d(n, L, x) if x.ndim == 1 else _2d(n, L, x)
        else:
            return _1d(n, L, x) if x.ndim == 1 else _2d_no_numba(n, L, x)
    

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(n, L, x),
        rmatmat=lambda x: _matmat(n, L.T.conj(), x)
    )


def polyadd(c1, c2, L):
    """Constructs a polynomial c1 + c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the addition of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] + c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also `NumPy, SciPy polyadd function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyadd.html>`_ for more details.
        See also :py:func:`polyval`.
    """
    c = np.polynomial.polynomial.polyadd(c1, c2)
    return polyval(L, c)


def polysub(c1, c2, L):
    """Constructs a polynomial c1 - c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the subtraction of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] - c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy polyadd function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polysub.html>`_ for more details.
        See also :py:func:`polyval`.
    """
    c = np.polynomial.polynomial.polysub(c1, c2)
    return polyval(L, c)


def polymul(c1, c2, L):
    """Constructs a polynomial c1 * c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the multiplication of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] * c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy, SciPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also `NumPy, SciPy polymul function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polymul.html>`_ for more details.
        See also :py:func:`polyval`.
    """
    c = np.polynomial.polynomial.polymul(c1, c2)
    return polyval(L, c)


def polydiv(c1, c2, L):
    """Constructs a polynomial c1 / c2 of linear operator L as a lazy linear operator P(L).
    Y = P(L) @ X returns a tensor. The first dimension is the result of P(L)[k] @ X[:, j]
    where j is the j-th column of X, the second dimension corresponds to the
    batch size while the third dimension corresponds to the k-th polynomial.

    Args:
        c1: 1d or 2d array
            List of coefficients of the first polynomial.
            If shape of c1 is (M1, N1) we have M1 polynomials
            and largest power is N1 - 1.
        c2: 1d or 2d array
            List of coefficients of the second polynomial.
            If shape of c2 is (M2, N2) we have M2 polynomials
            and largest power is N2 - 1.
            The coefficients corresponding to the multiplication of the two polynomials is
            c1[:min(M1, M2), :min(N1, N2)] / c2[:min(M1, M2), :min(N1, N2)].
        L: 2d array
            Linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the # of rows of x.

    Examples:

    References:
        See also `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        See also `NumPy, SciPy polydiv function <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polydiv.html>`_ for more details.
        See also :py:func:`polyval`.
    """
    c = np.polynomial.polynomial.polydiv(c1, c2)
    return polyval(L, c)


def polyder(c, m: int=1, scl: float=1.0, L=None):
    """Constructs the m-th derivative of the polynomial c
    as a lazy linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L is None

    References:
        See `NumPy, SciPy polyder <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyder.html>`_ for more details.
    """
    if L is None:
        raise ValueError("L is None.")
    return polyval(L, np.polynomial.polynomial.polyder(c, m, scl))


def polyint(c, m: int=1, k: list=[], lbnd: float=0.0, scl: float=1.0, L=None):
    """Constructs the m-th integral of the polynomial c
    as a lazy linear operator.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L is None

    References:
        See `NumPy, SciPy polyint <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.polyint.html>`_ for more details.
    """
    if L is None:
        raise ValueError("L is None.")
    return polyval(L, np.polynomial.polynomial.polyint(c, m, k, lbnd, scl))
