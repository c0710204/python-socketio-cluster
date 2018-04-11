import eventlet
import socketio
import os
import sys
import time
#from pymongo import MongoClient
#client = MongoClient('mongodb://root:dHtFkI6g@ds012578.mlab.com:12578/pspnet')
sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)

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
        data['label']=data['id']
        db[data['id']]=data
    try:
        collection.insert_one(data)
    except Exception as e:
        pass
    sio.emit('progress_upgrade_server',data=db.values())
    pass

@sio.on('disconnect')
def disconnect(sid):
    print('logserv - disconnect ', sid)


if __name__ == '__main__':
    port = 30011
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    print("creating remote port forward...")


    print("starting at local port {0}...".format(port))

    eventlet.wsgi.server(eventlet.listen(('', port)), app)
