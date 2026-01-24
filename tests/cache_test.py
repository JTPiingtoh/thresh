from functools import cached_property
from time import time

import pickle

cache = {}

class foo():

    def __enter__(self):
        try:
            with open('test_class_info.pkl', "wrb") as file:
                self.__setattr__() = pickle.load(file)
        except FileNotFoundError:
            self.state = 0 

    def set_state(self, n):
        self.state = n
        cache["state"] = n

    def __exit__(self):

        with open('test_class_info.pkl', "wb") as file:

            pickle.dump(f_instance, file)

    


f_instance = foo()
f_instance.set_state(3)




