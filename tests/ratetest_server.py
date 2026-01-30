#########################################

# Server with fixed window rate limiter # 

#########################################

# TODO: replicate riot api rate limits in more detail

from __future__ import annotations 

from flask import Flask, Response
from flask_limiter import Limiter, HeaderNames
from flask_limiter.util import get_remote_address

slow_requests = 10
slow_per_second = 12

fast_requests = 10
fast_per_second = 1

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{slow_requests} per {slow_per_second} seconds", "20 per 1 seconds"],
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

def add_app_ratelimit_headers(response: Response):
  response.headers["X-App-Rate-Limit"] = f"{slow_requests}:{slow_per_second},{fast_requests}:{fast_per_second}"
  return response


def add_method_ratelimit_headers(response: Response):
  ...  

@app.route("/")
def index():

  # response = add_app_ratelimit_headers(Response())
  # response.response = "Index"
  return "Index"


