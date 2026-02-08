#########################################

# Server with fixed window rate limiter # 

#########################################

# TODO: replicate riot app limits etc
# TODO: add random throttling to rate limit, and add in headers

from __future__ import annotations 

from flask import Flask, Response, make_response
from flask_limiter import Limiter, HeaderNames, RequestLimit
from flask_limiter.util import get_remote_address

SLOW_REQUESTS = 100
SLOW_PER_SECONDS = 120

FAST_REQUESTS = 20
FAST_PER_SECONDS = 1

DEFAULT_LIMITS = [
  f"{SLOW_REQUESTS} per {SLOW_PER_SECONDS} seconds",
  f"{FAST_REQUESTS} per {FAST_PER_SECONDS} seconds"
]

# half rate
THROTTLED_LIMITS = [
  f"{int(SLOW_REQUESTS / 4)} per {SLOW_PER_SECONDS} seconds",
  f"{int(FAST_REQUESTS / 4)} per {FAST_PER_SECONDS} seconds"

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

def add_app_ratelimit_headers(response: Response, cur_limits: list[RequestLimit]):

  # TODO: add app rate limit
  
  # sort limits by rate (largest window first)
  sorted_cur_limits = sorted(cur_limits, key = lambda l: l.limit.get_expiry(), reverse=True)
  rate_limits = []
  limit_counts = []

  for request_limit in sorted_cur_limits:
    requests = request_limit.limit.amount 
    per_seconds = request_limit.limit.get_expiry()
    requests_remaining = request_limit.remaining 

    rate_limits.append(f"{requests}:{per_seconds}")    
    limit_counts.append(f"{requests - requests_remaining}:{per_seconds}")    
    
  response.headers["X-App-Rate-Limit"] = ",".join(rate_limits)  
  response.headers["X-App-Rate-Limit-Count"] = ",".join(limit_counts)

  return response



throttle_start = 0
throttling = False 

def random_limit():

  '''
  Randomly throttles rate limit. Motivation is to test the client's ability to handle throttling during 
  concurrent requests. 
  
  :param response: Description
  :type response: Response
  '''  

  import time 
  import random


  def is_throttled():
    global throttle_start
    global throttling
    now = time.time()

    if not throttling and random.randint(0,5) == 0:
      throttling = True
      throttle_start = now
      
    if throttling and now - throttle_start > 10:
      throttling = False

    return throttling
  
  if is_throttled():
    print(THROTTLED_LIMITS)
    return THROTTLED_LIMITS
  
  return None


def add_method_ratelimit_headers(response: Response):
  ...



@app.route("/")
@limiter.limit(limit_value=random_limit)
def index():

  response = make_response()
  return add_app_ratelimit_headers(response=response, cur_limits=limiter.current_limits)


