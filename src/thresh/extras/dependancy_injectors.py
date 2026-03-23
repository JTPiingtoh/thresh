#############################################################################
# Functions for initiated classes from other objects that shares attributes # 
#############################################################################

import inspect
from typing import Any



def init_injector [C] (cls: type[C], instance: Any) -> C:
    '''
    Create an instance of class C with shared parameters from some other instance.
    Instance does not have to be of the type as cls.
    cls must be fully initiated from just shared parameters from instance.
    '''

    if not inspect.isclass(cls):
        raise TypeError("cls must be a class")
    new_vars = {}

    for i, member in enumerate(inspect.getmembers(instance)):
        if member[0].startswith("__"):
            continue
        elif inspect.ismethod(member[1]):
            continue

        if not member[0] in inspect.getfullargspec(cls.__init__)[0]:
            continue
        new_vars[member[0]] = member[1]

    try:
        new = cls(**new_vars)
        return new

    except TypeError as e:
        raise ValueError(f"Injecting {instance} into {cls} failed as {e}")

    return cls(**new_vars)
    

    
if __name__ == "__main__":


    class First():
        def __init__(self, b, c):
            self.b = b
            self.c = c

        def foo(self):
            pass


    class Second():
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def foo(self):
            pass


    first = First(2,3)

    second = init_injector(Second, first)
    assert first.b == second.b
    
