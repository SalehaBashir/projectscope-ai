import os
from redis import Redis
from rq import Queue

redis_conn = Redis.from_url(os.getenv("REDIS_URL"))
task_queue = Queue("projectscope-jobs", connection=redis_conn)