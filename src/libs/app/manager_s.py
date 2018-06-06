import client as cli
from collections import defaultdict
import multiprocessing
import socketio
import logging
class manager_server(socketio.Namespace):
    max_task_node=4
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)
    def cron_task(self):
        #check all ndoe info
        #trigger node work
        pass
    def on_client_init(self,sid,data):
        #registe client to the server
        #registe task thread to server
        #init task thread
        pass

    def on_connect(self, sid, environ):
        print(sid,"connect")
        info_pkg={"max_thread":max_task_node,"port":30041,"host":"star.eecs.oregonstate.edu","path":"/task"}
        self.emit("ask_init",info_pkg,room=sid)

