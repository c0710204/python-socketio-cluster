
import gevent
import socketio
import os
import sys
import sshtunnel
import time
import argparse
import importlib
from gevent import pywsgi
sio = socketio.Server(async_mode='gevent')
app = socketio.Middleware(sio)

#temp

parser = argparse.ArgumentParser(description='distrube server')
parser.add_argument('--app','-a', type=str,help='an integer for the accumulator')
args=parser.parse_args()
srv=importlib.import_module("apps.{0}.server".format(args.app))
srv_handle=srv.handler()

node_thread_number =4

if __name__ == '__main__':
    port = 30021
    print("starting at local port {0}...".format(port))
    sio.register_namespace(srv_handle('/task'))
    pywsgi.WSGIServer(('', port), app).serve_forever()
