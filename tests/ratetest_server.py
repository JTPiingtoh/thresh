#########################################

# Server with fixed window rate limiter # 

#########################################

# TODO: replicate riot api rate limits in more detail

from __future__ import annotations 

from flask import Flask, Response, make_response
from flask_limiter import Limiter, HeaderNames, RequestLimit
from flask_limiter.util import get_remote_address

import time
import random

slow_requests = 100
slow_per_seconds = 12

fast_requests = 20
fast_per_seconds = 1

DEFAULT_LIMITS = [
    f"{slow_requests} per {slow_per_seconds} seconds",
    f"{fast_requests} per {fast_per_seconds} seconds",
]

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=DEFAULT_LIMITS,
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,
    header_name_mapping={
    HeaderNames.LIMIT : "X-My-Limit",
    HeaderNames.RESET : "X-My-Reset",
    HeaderNames.REMAINING: "X-My-Remaining"
  }
)

# TODO: add application limit
# https://flask-limiter.readthedocs.io/en/stable/api.html#flask_limiter.ApplicationLimit

last_slowed = 0

def random_limit():
    global last_slowed
    now = time.time()

    

    if now - last_slowed <= 10:
        return "5 per 120 seconds, 40 per 120 seconds"

    if random.randrange(5) == 0:
        last_slowed = now
        return "5 per 120 seconds, 40 per 120 seconds"

    return DEFAULT_LIMITS


def add_app_ratelimit_headers(response: Response, cur_limits: list[RequestLimit]):

    limits = {str(l.limit): l for l in cur_limits}

    slow_key = "5 per 120 seconds"
    fast_key = "40 per 120 seconds"

    if slow_key not in limits or fast_key not in limits:
        return response

    slow_limit = limits[slow_key]
    fast_limit = limits[fast_key]

    response.headers["X-App-Rate-Limit"] = "5:120,40:120"

    slow_used = 5 - slow_limit.remaining
    fast_used = 40 - fast_limit.remaining

    response.headers["X-App-Rate-Limit-Count"] = f"{slow_used}:120,{fast_used}:120"

    return response


@app.route("/")
@limiter.limit(random_limit)
def index():
    response = make_response("Index")
    return add_app_ratelimit_headers(response, limiter.current_limits)


