class Foo:
    x = 2
    def p(self):
        print(self.x)

f = Foo()
f2 = Foo()
Foo.x = 1
print(Foo.x)
f2.p()

