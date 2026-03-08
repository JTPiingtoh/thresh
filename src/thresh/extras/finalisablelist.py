from typing import Iterable

class FinalisableList(list):
    
    def __init__(self, object: Iterable):
        super().__init__(object)
        super().__setattr__("_finalised", False)
    
    def finalise(self):
        super().__setattr__("_finalised", True)

    def __setattr__(self, name, value):

        if name == "_finalised":
            raise RuntimeError("You cannot directly assign _finalised. Use finalise() instead.")
        super().__setattr__(name, value)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        finalised = super().__getattribute__("_finalised")
        if finalised:
            raise RuntimeError("List is finalised.")
        return attr
    
if __name__ == "__main__":

    flist = FinalisableList([1,2,3])
    flist.append(1)
    flist.finalise()
      