#############################################################################
# Functions for initiated classes from other objects that shares attributes # 
#############################################################################

import inspect
from typing import Any



def inject_from [C] (cls: type[C], instance: Any) -> C:
    """
    Instantiate a class by injecting compatible attributes from an existing object.

    This utility inspects the provided ``instance`` and extracts its non-dunder,
    non-method attributes. It then filters those attributes to retain only the
    ones that match the parameter names of ``cls.__init__``. The filtered values
    are passed as keyword arguments to construct a new instance of ``cls``.

    This enables lightweight structural "mapping" between unrelated types, as long
    as the target class can be fully initialized using attributes present on the
    source instance.

    Parameters
    ----------
    cls : type[C]
        The target class to instantiate. Must be a valid class object whose
        constructor parameters can be satisfied by attributes on ``instance``.
    instance : Any
        Source object from which attribute values are extracted. It does not
        need to be an instance of ``cls``.

    Returns
    -------
    C
        A new instance of ``cls`` initialized with matching attributes from
        ``instance``.

    Raises
    ------
    TypeError
        If ``cls`` is not a class.
    ValueError
        If instantiation of ``cls`` fails due to missing or incompatible
        arguments.

    Notes
    -----
    - Only attributes whose names match parameters in ``cls.__init__`` are used.
    - Dunder attributes (``__*__``) and bound methods are ignored.
    - This function assumes that ``cls`` can be fully initialized from the
      subset of attributes found on ``instance``; otherwise, a ``ValueError``
      is raised.

    Examples
    --------
    >>> class A:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    >>> class B:
    ...     def __init__(self, x, y, z=0):
    ...         self.x = x
    ...         self.y = y
    ...         self.z = z
    ...
    >>> a = A(1, 2)
    >>> b = inject_from(B, a)
    >>> (b.x, b.y, b.z)
    (1, 2, 0)

    This docstring was generated using a LLM, and has been reviewed by me (Joe). No LLM was used to write this function. 
    """

    if not inspect.isclass(cls):
        raise TypeError("cls must be a class")

    try:
        # new = cls(**new_vars)
        new = cls(**instance.__dict__)
        return new

    except TypeError as e:
        raise ValueError(f"Injecting {instance} into {cls} failed as {e}")

    


    
if __name__ == "__main__":


    class A:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    class B:
        def __init__(self, x, y, z=0):
            self.x = x
            self.y = y
            self.z = z

        def __call__(self, *args, **kwds):
            pass

