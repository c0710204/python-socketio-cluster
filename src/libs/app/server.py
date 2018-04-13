import client as cli
import multiprocessing
import socketio
class app_server(socketio.Namespace):
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)
        self.max_task_node=2
        self.tasking=multiprocessing.Semaphore(self.max_task_node)
    def on_connect(self, sid, environ):
        for i in range(self.max_task_node):
            self.emit("ask_init",room=sid)
    def event(self,noti,sid):
        if noti=='free':
            pkg=self.get_task()
            if pkg!=None:
                self.tasking.acquire()
                self.emit('task',pkg,room=sid)
    def on_client_free(self,sid,data):
        pass
        self.event('free',data)
    def on_result(self,sid,data):
        #print(data)
        if data['status']>0:
            self.process_result(data['arg'])
        else:
            self.handle_error(data['err'],data['arg'])
        self.tasking.release()
        self.event('free',sid)
    def handle_error(self,args):
        raise NotImplementedError()
    def process_result(self,err,args):
        raise NotImplementedError()
    def get_task(self):
        raise NotImplementedError()