import gevent
import socketio
import os
import sys
import time
import pymysql
from src.libs.conf.conf import conf
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
#from pymongo import MongoClient
sio = socketio.Server(async_mode='gevent')
app = socketio.Middleware(sio)
db={}
enable_mysql=True
def conn_db():
    confloader=conf()
    confloader.load('service')
    #print("[{1}]connecting db...".format(0,time.asctime( time.localtime(time.time()) )))
    sys.stdout.flush()
    mysqldb=pymysql.connect(host="127.0.0.1",port=confloader.service['services']['mysql']['port'], user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
    #print("[{1}]db connection ok".format(0,time.asctime( time.localtime(time.time()) )))
    return mysqldb
@sio.on('connect')
def connect(sid, environ):
    print('logserv - connect ', sid)
    pass


@sio.on('update')
def update(sid, data):
    global db
    #global mysqldb
    #print(data)
    if enable_mysql:
        try:
            mysqldb=conn_db()
            with mysqldb.cursor() as cur:
                sql2='INSERT INTO psplog(panid,phase,val,max)VALUES("{0}","{1}","{2}","{3}");'.format(
                    data['id'],
                    data['phase'],
                    data['val'],
                    data['max']
                )
                cur.execute(sql2)
                mysqldb.commit()
                sql="select * from psplog where time in (SELECT max(time) FROM gsv_file_list.psplog group by panid) order by time"

                cur.execute(sql)
                mysqldb.commit()
                lines=cur.fetchall()
                lines=[{'id':l[2],'phase':l[3],'val':l[4],'max':l[5]} for l in lines]

                sio.emit('progress_upgrade_server',data=lines)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        finally:
            if mysqldb:
                mysqldb.close()
                del mysqldb

    else:
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
    confloader=conf()
    confloader.load('service')
    port = confloader.service['services']['log']['port']
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    print("creating remote port forward...")


    print("starting at local port {0}...".format(port))

    pywsgi.WSGIServer(('', port), app,handler_class=WebSocketHandler).serve_forever()
    #eventlet.wsgi.server(eventlet.listen(('', port)), app)
