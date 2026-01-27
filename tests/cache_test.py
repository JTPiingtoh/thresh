class foo:

    def __enter__(self):
        try:
            raise RuntimeError("")
        except RuntimeError:
            pass


    def __exit__(self, *_):
        print("foo.__exit__() called")
    
    


with foo() as _:
    pass

