
import eventlet
import socketio
import os
import sys
import sshtunnel
import time
sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)

#temp
import apps.streetdownloader.server as srv
srv_handle=srv.handler()

node_thread_number =4

if __name__ == '__main__':
    port = 30021
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])g


    print("starting at local port {0}...".format(port))
    sio.register_namespace(srv_handle('/task'))
    eventlet.wsgi.server(eventlet.listen(('', port)), app)
