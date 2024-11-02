# gunicorn.conf.py

bind = "0.0.0.0:9000"
loglevel = "info"
proc_name = "sirius"
timeout = 200
workers = 1
worker_class = "eventlet"
keepalive = 10
