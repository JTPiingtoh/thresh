d = {}



class Foo:
    def __init__(self):
        self.cat = 1
        self.dog = 2
    def save(self):
        d["state"] = self


if __name__ == "__main__":

    foo_instance_1 = Foo()

    for key, value in foo_instance_1.__dict__.items():
        print(key,value)
    foo_instance_1.save()

