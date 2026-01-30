#########################################

# Server with fixed window rate limiter # 

#########################################

# TODO: replicate riot api rate limits in more detail

from __future__ import annotations 

from flask import Flask, Response
from flask_limiter import Limiter, HeaderNames
from flask_limiter.util import get_remote_address

slow_requests = 100
slow_per_second = 120

fast_requests = 20
fast_per_second = 1

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[
      f"{slow_requests} per {slow_per_second} seconds",
      f"{fast_requests} per {fast_per_second} seconds"
    ],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,
    header_name_mapping={
    HeaderNames.LIMIT : "X-My-Limit",
    HeaderNames.RESET : "X-My-Reset",
    HeaderNames.REMAINING: "X-My-Remaining"
  }

)



response = Response()
response.headers["X-App-Rate-Limit"] = f"{slow_requests}:{slow_per_second}, {fast_requests}:{fast_per_second}"
  

@app.route("/")
def index():

  return "index"


