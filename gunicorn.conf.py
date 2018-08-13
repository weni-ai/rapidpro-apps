import os
import multiprocessing

current_path = os.path.dirname(os.path.abspath(__file__))
bind = '0.0.0.0:8080'
workers = multiprocessing.cpu_count() * 2 + 1
threads = workers
name = 'rapidpro'
env = 'DJANGO_SETTINGS_MODULE=temba.settings'
proc_name = 'rapidpro'
default_proc_name = proc_name
chdir = current_path
loglevel = 'info'
accesslog = '/dev/stdout'
errorlog = '/dev/stderr'
timeout = 120
