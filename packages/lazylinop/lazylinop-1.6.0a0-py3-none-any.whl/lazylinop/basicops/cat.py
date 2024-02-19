from lazylinop import isLazyLinearOp

def hstack(tup):
    """
    Concatenates a tuple of lazy linear operators, compatible objects horizontally.

    Args:
        tup:
            a tuple whose first argument is a LazyLinearOp and other must
            be compatible objects (numpy array, matrix, LazyLinearOp).

    Return:
        A LazyLinearOp resulting of the concatenation.

    """
    lop = tup[0]
    if isLazyLinearOp(lop):
        return lop.concatenate(*tup[1:], axis=1)
    else:
        raise TypeError('lop must be a LazyLinearOp')

def vstack(tup):
    """
    Concatenates a tuple of lazy linear operators, compatible objects vertically.

    Args:
        tup:
            a tuple whose first argument is a LazyLinearOp and other must be
            compatible objects (numpy array, matrix, LazyLinearOp).

    Return:
        A LazyLinearOp resulting of the concatenation.

    """
    lop = tup[0]
    if isLazyLinearOp(lop):
        return lop.concatenate(*tup[1:], axis=0)
    else:
        raise TypeError('lop must be a LazyLinearOp')


