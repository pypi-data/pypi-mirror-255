"""
Module for polynomial related :py:class:`.LazyLinearOp`-s.

It provides "polynomial as :py:class:`.LazyLinearOp`" functions for which
the polynomial variable is itself a linear operator (especially a
:py:class:`.LazyLinearOp`). Below are the provided functions:

    - :py:func:`.polyval` for evaluating general polynomials.
    - :py:func:`.chebval` which is specialized for Chebyshev polynomials.
    - :py:func:`.polyvalfromroots` and :py:func:`.chebvalfromroots` do the same
      but defining the polynomial from its roots.
    - :py:func:`.power` for the n-th power of any linear operator.

Besides, the two classes :py:class:`.poly` and :py:class:`.cheb` allow
to make computations with respectively general polynomials or in particular
with Chebyshev's. With ``p1`` and ``p2`` two polynomial instances, one can:

    - add/substract: ``(p1 + p2)(Op)``, ``(p1 - p2)(Op)`` with ``Op`` the
      polynomial variable (a :py:class:`.LazyLinearOp`, :py:class:`.poly` or
      :py:class:`.cheb`). Evaluating and applying the polynomials on the
      fly is also possible: ``(p1 + p2)(Op) @ x``.
    - The same is possible to multiply (``@``), divide (``//``) and modulo
      (``%``) two polynomials (``(p1 @ p2)(Op)``, ``(p1 // p2)(Op)``,
      ``(p1 % p2)(Op)``.
    - And compose two polynomials: ``(p1(p2))(Op)`` .

.. admonition:: More details about implementation and features

   The classes :py:class:`.poly` and :py:class:`cheb` extend
   :py:class:`numpy.polynomial.Polynomial` and
   :py:class:`numpy.polynomial.Chebyshev`.
   They override the method :py:meth:`__call__` to implement the polynomial
   evaluation and calculate on the fly the available operations.
   Under the hood :py:func:`polyval` or :py:func:`chebval` are called depending
   on the polynomial form.
   It is possible to use :code:`evaluate` to choose evaluation method
   of the operation (e.g. :code:`(p1+p2)(Op, evaluate='polyval') @ x`).
.. You can also use :py:func:`chebvalfromroots` that consider polynomial
   in monomial form before to convert into Chebyshev form.
   To compute n-th power of a LazyLinearOp use :py:func:`power` or
   create :py:class:`poly` instance such that only n-th coefficient
   is equal to one while the others are equal to zero.

"""

import numpy as np
from numpy.polynomial import Polynomial as P
from numpy.polynomial import Chebyshev as T
from lazylinop import binary_dtype, isLazyLinearOp, LazyLinearOp
import warnings
from warnings import warn
warnings.simplefilter(action='always')



class poly(P):
    """This class implements a polynomial class derived from
    :py:class:`numpy.polynomial.Polynomial` and so relies on NumPy polynomial
    package to manipulate polynomials.

    See :py:mod:`lazylinop.wip.polynomial` for an introduction to implemented
    operations and their basic use.
    """

    def __init__(self, coef, domain=[-1.0, 1.0], window=[-1.0, 1.0],
                 symbol='x'):
        """Init instance of poly.

        Args:
            coef: list
                List of coefficients
            domain: list, optional
                see :py:class:`numpy.polynomial.Polynomial`
            window: list, optional
                see :py:class:`numpy.polynomial.Polynomial`
            symbol: str, optional
                see :py:class:`numpy.polynomial.Polynomial`

        Examples:
            >>> from lazylinop.wip.polynomial import poly
            >>> p = poly([1.0, 2.0, 3.0])

        .. seealso::
            `numpy.polynomial package
            <https://numpy.org/doc/stable/reference/routines.polynomials.html>`_.
        """
        P.__init__(self, coef, domain, window, symbol)
        # super().__init__(self, coef, domain, window, symbol)

    @staticmethod
    def fromroots(roots):
        """Return poly instance init from roots.

        Args:
            roots: list or np.ndarray
            List of roots.

        Returns:
            poly instance.

        Examples:
            >>> import numpy as np
            >>> from lazylinop.wip.polynomial import poly
            >>> p1 = poly([1.0, -2.0, 1.0])
            >>> p2 = poly.fromroots([1.0, 1.0])
            >>> np.allclose(p1.coef, p2.coef)
            True
        """
        tmp = P.fromroots(roots)
        return poly(tmp.coef, domain=tmp.domain, window=tmp.window,
                    symbol=tmp.symbol)

    def __call__(self, op, evaluate: str = 'polyval'):
        """
        Thanks to Python :py:meth:`__call__` instance behaves like function.
        If op is a LazyLinearOp, return polynomial of op applied to a 1d or
        2d array.
        If op is a P or T instance, return a poly instance.

        Args:
            op: LazyLinearOp, P or T
            evaluate: str, optional
            There is three methods to evaluate P(op) @ X.
            Default is 'polyval'.
            'polyvalfromroots' computes roots from coefficients and then
            call :py:func:`polyvalfromroots` function.
            'chebval' computes coefficients in Chebyshev form and then
            call :py:func:`chebval` function.

        Raises:
            ValueError
                evaluate must be either 'polyval', 'polyvalfromroots' or
                'chebval'.

        Examples:
            >>> from lazylinop import eye, isLazyLinearOp
            >>> from lazylinop.wip.polynomial import poly
            >>> p = poly([1.0, 2.0, 3.0])
            >>> Op = eye(3, n=3, k=0)
            >>> isLazyLinearOp(p(Op))
            True
            >>> x = np.random.randn(3)
            >>> np.allclose(6.0 * x, p(Op) @ x)
            True
        """
        if isLazyLinearOp(op):
            if evaluate == 'polyval':
                return polyval(op, self.coef)
            elif evaluate == 'polyvalfromroots':
                # Because of (Op - r_0 * Id) @ ... @ (Op - r_n * Id)
                # coeff c_n of the highest power c_n * Op ^ n is always 1.
                if self.coef[-1] != 1.0:
                    warn("Highest power coefficient c_n must be 1.")
                return polyvalfromroots(op,
                                        np.polynomial.polynomial.polyroots(
                                            self.coef))
            elif evaluate == 'chebval':
                tmp = self.convert(kind=T)
                return chebval(op, tmp.coef)
            else:
                raise ValueError("evaluate must be either 'polyval',"
                                 " 'polyvalfromroots' or 'chebval'.")
        elif isinstance(op, P):
            tmp = super(P, self).__call__(op)
            return poly(tmp.coef, domain=tmp.domain, window=tmp.window)
        elif isinstance(op, T):
            tmp = super(P, self).__call__(op)
            return cheb(tmp.coef, domain=tmp.domain, window=tmp.window)
        else:
            raise TypeError('Unexpected op.')


class cheb(T):
    """This class implements a Chebyshev polynomial class derived from
    :py:class:`numpy.polynomial.Chebyshev` and so relies on NumPy polynomial
    package to manipulate polynomials.

    See :py:mod:`lazylinop.wip.polynomial` for an introduction to implemented
    operations and their basic use.
    """

    def __init__(self, coef, domain=[-1.0, 1.0], window=[-1.0, 1.0],
                 symbol='x'):
        """Init instance of cheb.

        Args:
            coef: list
                List of coefficients
            domain: list, optional
                see :py:class:`numpy.polynomial.Chebyshev`
            window: list, optional
                see :py:class:`numpy.polynomial.Chebyshev`
            symbol: str, optional
                see :py:class:`numpy.polynomial.Chebyshev`

        Examples:
            >>> from lazylinop.wip.polynomial import cheb
            >>> t = cheb([1.0, 2.0, 3.0])

        .. seealso::
            `numpy.polynomial package
            <https://numpy.org/doc/stable/reference/routines.polynomials.html>`_.
        """
        T.__init__(self, coef, domain, window, symbol)

    @staticmethod
    def fromroots(roots):
        """Return cheb instance init from roots.

        Args:
            roots: list or np.ndarray
            List of roots.

        Returns:
            cheb instance.

        Examples:
            >>> import numpy as np
            >>> from numpy.polynomial import Chebyshev as T
            >>> from lazylinop.wip.polynomial import cheb, poly
            >>> p1 = poly([1.0, -2.0, 1.0]).convert(kind=T)
            >>> p2 = cheb.fromroots([1.0, 1.0])
            >>> np.allclose(p1.coef, p2.coef)
            True

        .. seealso::
            `numpy.polynomial package https://numpy.org/doc/stable/reference/
            generated/numpy.polynomial.chebyshev.chebfromroots.html`_
        """
        tmp = T.fromroots(roots)
        return cheb(tmp.coef, domain=tmp.domain, window=tmp.window,
                    symbol=tmp.symbol)

    def __call__(self, op, evaluate: str = 'chebval'):
        """
        Thanks to Python :py:meth:`__call__` instance behaves like function.
        If op is a LazyLinearOp, return polynomial of op applied to a 1d or
        2d array.
        If op is a P or T instance, return a poly instance.

        Args:
            op: LazyLinearOp, P or T
            evaluate: str, optional
            There is two methods to evaluate P(op) @ X.
            Default is 'chebval'.
            'polyval' computes coefficients in polynomial form and
            then call :py:func:`polyval` function.

        Raises:
            ValueError
                evaluate must be either 'chebval' or 'polyval'.

        Examples:
            >>> from lazylinop import eye, isLazyLinearOp
            >>> from lazylinop.wip.polynomial import cheb
            >>> t = poly([1.0, 2.0, 3.0])
            >>> Op = eye(3, n=3, k=0)
            >>> isLazyLinearOp(t(Op))
            True
        """
        if isLazyLinearOp(op):
            if evaluate == 'chebval':
                return chebval(op, self.coef)
            elif evaluate == 'polyval':
                tmp = self.convert(kind=P)
                return polyval(op, tmp.coef)
            else:
                raise ValueError("evaluate must be either 'chebval' or"
                                 " 'polyval'.")
        elif isinstance(op, P):
            tmp = super(T, self).__call__(op)
            return poly(tmp.coef, domain=tmp.domain, window=tmp.window)
        elif isinstance(op, T):
            tmp = super(T, self).__call__(op)
            return cheb(tmp.coef, domain=tmp.domain, window=tmp.window)
        else:
            raise TypeError('Unexpected op.')


def chebval(L, c):
    r"""Constructs a :py:class:`.LazyLinearOp` Chebysev polynomial ``P(L)`` of
    linear operator ``L``.

    ``P(L)`` is equal to :math:`c_0Id + c_1T_1(L) + \cdots + c_nT_n(L)`.

    The k-th Chebyshev polynomial can be computed by recurrence:

    .. math::

        \begin{eqnarray}
        T_0(L) &=& 1\\
        T_1(L) &=& L\\
        T_{k+1}(L) &=& 2LT_k(L) - T_{k-1}(L)
        \end{eqnarray}

    The Clenshaw's method is used to compute ``P(L) @ X``.

    ``Y = P(L) @ X`` shape is ``(L.shape[0], X.shape[1])``.


    Args:
        L: 2d array
            Linear operator.
        c: 1d array
            List of Chebyshev polynomial(s) coefficients.
            If the size of the 1d array is n + 1 then the largest power of the
            polynomial is n.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the
            # of rows of x.
        ValueError
            List of coefficients has zero size.

    Examples:
        >>> import numpy as np
        >>> from lazylinop import eye
        >>> from lazylinop.wip.polynomial import chebval
        >>> x = np.random.randn(3)
        >>> Op = eye(3, n=3, k=0)
        >>> y = chebval(Op, [1.0, 2.0, 3.0]) @ x
        >>> np.allclose(6.0 * x, y)
        True

    .. seealso::
        - `Wikipedia <https://en.wikipedia.org/wiki/Chebyshev_polynomials>`_,
        - `Polynomial magic web page
          <https://francisbach.com/chebyshev-polynomials/>`_,
        - `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/
          reference/generated/numpy.polynomial.chebyshev.chebval.html>`_.
    """

    if type(c) is list:
        c = np.asarray(c)

    if c.ndim == 2:
        # Only one polynomial
        c = np.copy(c[:, 0].flatten())
    D = c.shape[0]
    if D == 0:
        raise ValueError("List of coefficients has zero size.")

    def _matmat(L, x, c):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is"
                             " not equal to the # of rows of x.")
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        batch_size = x.shape[1]
        output = np.empty((L.shape[0], batch_size),
                          dtype=binary_dtype(c.dtype, x.dtype))
        T0x = np.empty((L.shape[0], batch_size),
                       dtype=binary_dtype(c.dtype, x.dtype))
        T1x = np.empty((L.shape[0], batch_size),
                       dtype=binary_dtype(c.dtype, x.dtype))
        T2x = np.empty((L.shape[0], batch_size),
                       dtype=binary_dtype(c.dtype, x.dtype))
        np.copyto(T0x, x)
        np.copyto(output[:, :], np.multiply(c[0], T0x))
        if D > 1:
            # loop over the coefficients
            for i in range(1, D):
                if i == 1:
                    np.copyto(T1x, L @ x)
                    if c[i] == 0.0:
                        continue
                    else:
                        np.add(output, np.multiply(c[i], T1x), out=output)
                else:
                    np.copyto(T2x, np.subtract(np.multiply(2.0, L @ T1x), T0x))
                    # Recurrence
                    np.copyto(T0x, T1x)
                    np.copyto(T1x, T2x)
                    if c[i] == 0.0:
                        continue
                    else:
                        np.add(output, np.multiply(c[i], T2x), out=output)
        return output.ravel() if is_1d else output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(L, x, c),
        rmatmat=lambda x: _matmat(L.T.conj(), x, c)
    )


def chebvalfromroots(L, r):
    r"""Constructs a :py:class:`.LazyLinearOp` Chebyshev polynomial
    ``P(L)`` of linear operator ``L`` from the polynomial roots.

    ``P(L)`` is equal to :math:`(L - r_0Id)(L - r_1Id)\cdots (L - r_nId)`.

    ``Y = P(L) @ X`` shape is ``(L.shape[0], X.shape[1])``.

    Args:
        L: 2d array
            Linear operator.
        r: 1d array
            List of Chebyshev polynomial roots.
            If the size of the list is n + 1 then the largest power of the
            polynomial is n.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            List of coefficients has zero size.

    Examples:
        >>> import numpy as np
        >>> from lazylinop import eye
        >>> from lazylinop.wip.polynomial import chebvalfromroots
        >>> x = np.random.randn(3)
        >>> Op = eye(3, n=3, k=0)
        >>> y = chebvalfromroots(Op, [1.0, 1.0]) @ x
        >>> np.allclose(0.0 * x, y)
        True

    .. seealso::
        - `Wikipedia <https://en.wikipedia.org/wiki/Chebyshev_polynomials>`_,
        - `Polynomial magic web page
          <https://francisbach.com/chebyshev-polynomials/>`_,
        - `NumPy polynomial cheval
          <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebval.html>`_,
        - `NumPy polynomial chebfromroots
          <https://docs.scipy.org/doc//numpy-1.9.3/reference/generated/numpy.polynomial.chebyshev.chebfromroots.html>`_,
        - :py:func:`chebval`.
    """
    if type(r) is list:
        r = np.asarray(r)
    if r.ndim == 2:
        # Only one polynomial
        r = np.copy(r[:, 0].flatten())
    if r.shape[0] == 0:
        raise ValueError("List of roots has zero size.")
    return chebval(L, np.polynomial.chebyshev.chebfromroots(r))


def polyval(L, c):
    r"""Constructs a :py:class:`.LazyLinearOp` polynomial ``P(L)`` of linear
    operator ``L``.

    ``P(L)`` is equal to :math:`c_0Id + c_1L^1 + \cdots + c_nL^n`.

    ``Y = P(L) @ X`` shape is ``(L.shape[0], X.shape[1])``.

    Args:
        L: 2d array
            Linear operator.
        c: 1d array
            List of polynomial coefficients.
            If the size of the 1d array is n + 1 then the largest power of the
            polynomial is n.
            If the array is 2d consider only the first column/polynomial.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the
            # of rows of x.
        ValueError
            List of coefficients has zero size.

    Examples:
        >>> import numpy as np
        >>> from lazylinop import eye
        >>> from lazylinop.wip.polynomial import polyval
        >>> x = np.random.randn(3)
        >>> Op = eye(3, n=3, k=0)
        >>> y = polyval(Op, [1.0, 2.0, 3.0]) @ x
        >>> np.allclose(6.0 * x, y)
        True

    .. seealso::
        - `NumPy polynomial class <https://docs.scipy.org/doc//numpy-1.9.3/
          reference/generated/numpy.polynomial.polynomial.polyval.html>`_.
        - :py:func:`polyvalfromroots`.
    """

    if type(c) is list:
        c = np.asarray(c)

    if c.ndim == 2:
        # Only one polynomial
        c = np.copy(c[:, 0].flatten())
    D = c.shape[0]
    if D == 0:
        raise ValueError("List of coefficients has zero size.")

    def _matmat(L, x, c):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is"
                             " not equal to the # of rows of x.")
        # x can't be a LazyLinearOp here because it's handle before in
        # LazyLinearOp.__matmul__
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        output = np.empty((L.shape[0], x.shape[1]),
                          dtype=binary_dtype(c.dtype, x.dtype))
        Lx = np.empty((L.shape[0], x.shape[1]), dtype=binary_dtype(c.dtype,
                                                                   x.dtype))
        output[:, :] = np.multiply(c[0], x)
        if D > 1:
            # Loop over the coefficients
            for i in range(1, D):
                if i == 1:
                    np.copyto(Lx, L @ x)
                else:
                    np.copyto(Lx, L @ Lx)
                if c[i] == 0.0:
                    continue
                else:
                    np.add(output[:, :], np.multiply(c[i], Lx), out=output)
        return output.ravel() if is_1d else output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(L, x, c),
        rmatmat=lambda x: _matmat(L.T.conj(), x, c)
    )


def polyvalfromroots(L, r):
    r"""Constructs a :py:class:`.LazyLinearOp` polynomial
    ``P(L)`` of linear operator ``L`` from the polynomial roots.

    ``P(L)`` is equal to :math:`(L - r_0Id)(L - r_1)\cdots (L - r_nId)`.

    ``Y = P(L) @ X`` shape is ``(L.shape[0], X.shape[1])``.

    Args:
        L: 2d array
            Linear operator.
        r: 1d array
            List of polynomial roots.
            If the size of the 1d array is n + 1 then the largest power of the
            polynomial is n.
            If the array is 2d, the function considers only the first
            column/polynomial.

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            L @ x does not work because # of columns of L is not equal to the #
            of rows of x.
        ValueError
            List of roots has zero size.

    Examples:
        >>> import numpy as np
        >>> from lazylinop import eye
        >>> from lazylinop.wip.polynomial import polyvalfromroots
        >>> x = np.random.randn(3)
        >>> Op = eye(3, n=3, k=0)
        >>> y = polyvalfromroots(Op, [1.0, 1.0]) @ x
        >>> np.allclose(0.0 * x, y)
        True

    .. seealso::
        - `NumPy polynomial class <https://docs.scipy.org/doc/
          numpy-1.9.3/reference/generated/numpy.polynomial.polynomial.
          polyval.html>`_.
        - :py:func:`polyval`.
    """

    if type(r) is list:
        r = np.asarray(r)

    if r.ndim == 2:
        # Only one polynomial
        r = np.copy(r[:, 0].flatten())
    R = r.shape[0]
    if R == 0:
        raise ValueError("List of roots has zero size.")

    def _matmat(r, L, x):
        if L.shape[1] != x.shape[0]:
            raise ValueError("L @ x does not work because # of columns of L is"
                             " not equal to the # of rows of x.")
        if x.ndim == 1:
            is_1d = True
            x = x.reshape(x.shape[0], 1)
        else:
            is_1d = False
        output = np.empty((L.shape[0], x.shape[1]),
                          dtype=binary_dtype(r.dtype,
                                             x.dtype))
        Lx = np.empty((L.shape[0], x.shape[1]), dtype=binary_dtype(r.dtype,
                                                                   x.dtype))
        if r[R - 1] == 0.0:
            np.copyto(Lx, L @ x)
        else:
            np.copyto(Lx, np.subtract(L @ x, np.multiply(r[R - 1], x)))
        if R > 1:
            for i in range(1, R):
                if r[R - 1 - i] == 0.0:
                    np.copyto(Lx, L @ Lx)
                else:
                    np.copyto(Lx, np.subtract(L @ Lx, np.multiply(r[R - 1 - i],
                                                                  Lx)))
        np.copyto(output[:, :], Lx)
        return output.ravel() if is_1d else output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(r, L, x),
        rmatmat=lambda x: _matmat(r, L.T.conj(), x)
    )


def power(n, L):
    r"""Constructs the n-th power :math:`L^n` of linear operator ``L``.

    .. note::
        It is equivalent to create a :py:class:`poly` instance such that
        only n-th coefficient is equal to one while the others are equal
        to zero.

    Args:
        n: int
            Raise the linear operator to degree n.
        L: 2d array
            Linear operator (e.g. a :py:class:`.LazyLinearOp`).

    Returns:
        LazyLinearOp :math:`L^n`.

    Raises:

    Examples:
        >>> import numpy as np
        >>> from lazylinop import eye
        >>> from lazylinop.wip.polynomial import power
        >>> Op = power(3, eye(3, n=3, k=0))
        >>> x = np.full(3, 1.0)
        >>> np.allclose(Op @ x, x)
        True
        >>> Op = power(3, eye(3, n=3, k=1))
        >>> # Note that Op is in fact zero
        >>> x = np.full(3, 1.0)
        >>> np.allclose(Op @ x, np.zeros(3, dtype=np.float_))
        True

    .. seealso::
        `NumPy power function
        <https://numpy.org/doc/stable/reference/generated/numpy.power.html>`_.
    """

    def _matmat(n, L, x):

        output = L @ x
        if n > 1:
            for n in range(1, n):
                if x.ndim == 1:
                    output[:] = L @ output[:]
                else:
                    output[:, :] = L @ output[:, :]

        return output

    return LazyLinearOp(
        shape=L.shape,
        matmat=lambda x: _matmat(n, L, x),
        rmatmat=lambda x: _matmat(n, L.T.conj(), x)
    )


if __name__ == '__main__':
    import doctest
    doctest.testmod()
