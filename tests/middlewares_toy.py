import time

def send_request(input):
    # model how a valid response depends on a valid input
    print("sending request")
    response = input
    return response


def handle_error_middleware(input, next): 
    response = next(input)
    # fail fast
    if response != 0:
        raise RuntimeError("Bad response")

    return response


def retry_middleware(input, next):   
    
    for i in range(1,4):
        response = next(input)
        if response == 0:
            print("Got ok response")
            return response        
    return response



def ratelimit_middleware(input, next):   
    time.sleep(0.5)
    print("slept")
    response = next(input)
    return response


def wrap(middleware, handler):
    
    def new_handler(input):
        response = middleware(input, handler)
        return response
    return new_handler


def execute_middlewares(middlewares: list, input):

    middlewares.reverse()
    handler = send_request

    # Wrap handler with middleware in reverse order
    for middleware in middlewares:
        # wrap handler with middleware
        handler = wrap(middleware, handler)

    return handler(input)

# Not using input for now
input = 1
middlewares = [
    retry_middleware, 
    handle_error_middleware, 
    ratelimit_middleware
]

try:
    final_response = execute_middlewares(middlewares, input)
    print(f"final response: {final_response}")

except RuntimeError as e:
    print(e)