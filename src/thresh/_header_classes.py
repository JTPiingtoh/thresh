d = {}



class Foo:
    def __init__(self):
        self.cat = 1
        self.dog = 2
    def save(self):
        d["state"] = self


if __name__ == "__main__":

    foo_instance_1 = Foo()

    foo_instance_1.cat = 3
    print(foo_instance_1.cat)

