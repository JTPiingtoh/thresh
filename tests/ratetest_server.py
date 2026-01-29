#########################################

# Server with fixed window rate limiter # 

#########################################

# TODO: replicate riot api rate limits in more detail

from __future__ import annotations 

from flask import Flask, Response
from flask_limiter import Limiter, HeaderNames
from flask_limiter.util import get_remote_address

requests = 100
per_second = 120

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{requests} per {per_second} seconds"],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,
    header_name_mapping={
    HeaderNames.LIMIT : "X-My-Limit",
    HeaderNames.RESET : "X-My-Reset",
    HeaderNames.REMAINING: "X-My-Remaining"
  }

)


@app.route("/")
def index():

  response = Response()
  response.headers["X-App-Rate-Limit"] = f"{requests}:{per_second}"
  
  return "hello"


