# we want a series of functions that will call eachother
# the last functions will actually send the request
# this is in effect just layers of function decorators.


import time

def retry(func):    
    def inner():
        response: int
        for i in range(3):
            print(f"retry {i}")
            response = func()
            if response == 0:
                break


        return response
    return inner


def error_handler(func):    
    def inner():
        response = func()
        if response != 0:
            print("bad response!")
        else:
            print("good reponse!")
        return response
    return inner


def rate_limiter(func):    
    def inner():
        time.sleep(0.5)
        print("limited!")
        response = func()
        return response
    return inner
    
@retry
@error_handler
@rate_limiter
def final1():
    response = 0
    return response

middlewares = [rate_limiter, error_handler, retry]

def final2():
    response = 0
    return response

for mw in middlewares:
    final2 = mw(final2)

response = final1()
print(f"final response 1: {response}")
print()
response = final2()
print(f"final response 2: {response}")


