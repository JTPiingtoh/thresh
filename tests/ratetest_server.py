#########################################

# Server with fixed window rate limiter # 

#########################################

from __future__ import annotations 

from flask import Flask
from flask_limiter import Limiter, HeaderNames
from flask_limiter.util import get_remote_address

import flask_limiter



app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per 1 seconds"],
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


  return "Awesome league data!"