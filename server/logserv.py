import eventlet
import socketio
import os
import sys
import time
sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)
db = {}


@sio.on('connect')
def connect(sid, environ):
    print('logserv - connect ', sid)
    pass


@sio.on('update')
def update(sid, data):
    global db
    print(data)
    if data['id'] in db:
        if (data['max']):
            db[data['id']]['max'] = data['max']

        if (data['val']):
            db[data['id']]['val'] = data['val']

        if (data['phase']):
            db[data['id']]['phase'] = data['phase']
    else:
        db[data['id']]=data
    sio.emit('progress_upgrade_server',data=db.values())
    pass

@sio.on('disconnect')
def disconnect(sid):
    print('logserv - disconnect ', sid)


if __name__ == '__main__':
    port = 30001
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    print("creating remote port forward...")


    print("starting at local port {0}...".format(port))

    eventlet.wsgi.server(eventlet.listen(('', port)), app)
