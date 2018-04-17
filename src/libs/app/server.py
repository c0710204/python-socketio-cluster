import client as cli
from collections import defaultdict
import multiprocessing
import socketio
class app_server(socketio.Namespace):
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)
        self.max_task_node=2
        self.tasking=defaultdict(lambda :multiprocessing.Semaphore(self.max_task_node))

    def on_connect(self, sid, environ):
        for i in range(self.max_task_node):
            self.emit("ask_init",room=sid)
    def event(self,noti,sid):
        if noti=='free':
            pkg=self.get_task()
            if pkg!=None:
                print(sid,"acquire")
                self.tasking[sid].acquire()
                self.emit('task',pkg,room=sid)
    def on_client_free(self,sid,data):
        pass
        self.event('free',sid)
    def on_result(self,sid,data):
        print(sid,"release")
        self.tasking[sid].release()
        if data['status']>0:
            self.process_result(data['arg'])
        else:
            self.handle_error(data['err'],data['arg'])

        self.event('free',sid)
    def handle_error(self,args):
        raise NotImplementedError()
    def process_result(self,err,args):
        raise NotImplementedError()
    def get_task(self):
        raise NotImplementedError()
