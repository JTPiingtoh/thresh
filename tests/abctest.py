# what is an interface?
    # defines the inputs and outputs of something 

# abstract classes
    # define the interface, and could provide an implementation
    # cannot be instantiated by themselves, must be inherited

# abstract classes 

from abc import ABC


class Animal(ABC):

    def __init__(self, name):
        self.name = name

    def walk(self):
        print(f"{self.name} is walking")

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Animal:
            if any("walk" in B.__dict__ for B in subclass.__mro__):
                return True
        return NotImplemented


class Dog():
    def __init__(self, name):
        self.name = name

    def walk(self):
        print(f"{self.name} is walking")




if __name__ == "__main__":
    pluto = Dog("pluto")
    assert issubclass(Dog, Animal)