import eventlet
import socketio
import os
import sys
import sshtunnel
from async_socketIO import async_socketIO

sio = socketio.Server(async_mode='eventlet')
app = socketio.Middleware(sio)
img_list = [
    "/home/guxi/put/allComposites/allComposites/pdq1V_ELoWZKwMqmYGhlJ3A.jpg",
    "/home/guxi/put/allComposites/allComposites/pDroglglZkhzRHy8Ro7469A.jpg",
    "/home/guxi/put/allComposites/allComposites/pe4aqz15bqGBJC7NFfvffUw.jpg",
    "/home/guxi/put/allComposites/allComposites/peKrEIjt-ejZPzxPb8k8YTg.jpg",
    "/home/guxi/put/allComposites/allComposites/pe-NNi3o_IBygE3pHUaFVkA.jpg",
    "/home/guxi/put/allComposites/allComposites/pEoQ4MpQStvkaX2XRuAandA.jpg",
    "/home/guxi/put/allComposites/allComposites/pGARaFX8fku2M7YL5p3Q3nw.jpg",
    "/home/guxi/put/allComposites/allComposites/pGLJkBvFkwJKBPxRlYiw8IA.jpg",
    "/home/guxi/put/allComposites/allComposites/pgpN2LrjihhgOF1nJt5enPQ.jpg",
    "/home/guxi/put/allComposites/allComposites/pHB9QHNJ7BlEskE_aI__Etw.jpg",
    "/home/guxi/put/allComposites/allComposites/phdfSVpKonsOj6YsIh94F1Q.jpg",
    "/home/guxi/put/allComposites/allComposites/pHvFX4hWJDBnX0he_uoi-Xg.jpg",
    "/home/guxi/put/allComposites/allComposites/p-IrT50a5IdPs_3lWhjgU_w.jpg",
    "/home/guxi/put/allComposites/allComposites/piXskIgLHk0Mz50jZ5j3Ojw.jpg",
    "/home/guxi/put/allComposites/allComposites/pj0cnmNnqcZoREN7AmVHS1w.jpg",
    "/home/guxi/put/allComposites/allComposites/pjDaPrxSetgB6YPqJ1DA4bw.jpg",
    "/home/guxi/put/allComposites/allComposites/pjlBEv_5UMPTYW08b_FiU9A.jpg",
    "/home/guxi/put/allComposites/allComposites/pJTZ6nR9HhEtr9QeNN9iRng.jpg",
    "/home/guxi/put/allComposites/allComposites/pk29iBtSIAExFD6F9BSh1LQ.jpg",
    "/home/guxi/put/allComposites/allComposites/pMVVN47PalYrJJal6QVVRxg.jpg",
    "/home/guxi/put/allComposites/allComposites/pnnGnDY8gMbbIJ67IhL_egA.jpg",
    "/home/guxi/put/allComposites/allComposites/pnvMO9L6NhlCDv4Jexn7kug.jpg",
    "/home/guxi/put/allComposites/allComposites/pp7folxTLUX66BM5BlUewDQ.jpg",
    "/home/guxi/put/allComposites/allComposites/pQrrHyXgEpvD_ZBDHN0uS9w.jpg",
]


def package(input_path, output_path):
    return {
        "proxy": {
            "host": "star.eecs.oregonstate.edu",
            "username": "guxi",
            "password": "cft6&UJM",
            "port": 22,
        },
        "ssh": {
            "host": "127.0.0.1",
            "username": "guxi",
            "password": "dHtFkI6g",
            "port": 50022,
        },
        "input_path": input_path,
        "output_path": output_path
    }


node_thread_number = 4


@sio.on('connect', namespace='/pspnet')
def connect(sid, environ):
    print("connect", sid)
    #global img_list
    #img_local=img_list[-1]
    #del img_list[-1]
    #print("sending request : {0} image left".format(len(img_list)))
    #sio.emit("request",package(img_local,"/home/guxi/tree2/output/"),namespace="/pspnet")
    for i in range(node_thread_number):
        sio.emit("asknext", namespace="/pspnet")


@sio.on('next', namespace='/pspnet')
def next(sid):
    global img_list
    if len(img_list) > 0:
        img_local = img_list[-1]
        del img_list[-1]
        print("sending request : {0} image left".format(len(img_list)))
        sio.emit(
            "request",
            package(img_local, "/home/guxi/tree2/output/"),
            namespace="/pspnet")


@sio.on(
    'disconnect', )
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    port = 30021
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    print("creating remote port forward...")
    data = package("", "")

    print("starting at local port {0}...".format(port))

    eventlet.wsgi.server(eventlet.listen(('', port)), app)
