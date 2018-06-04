import client as cli
from collections import defaultdict
import multiprocessing
import socketio
import logging
logging.setLevel(DEBUG)
class app_server(socketio.Namespace):
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)

        self.max_task_node=4
        self.tasking=defaultdict(lambda :multiprocessing.Semaphore(self.max_task_node))
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

        for i in range(self.max_task_node):
            info_pkg={'sid':sid,'thread_id':i}
            self.emit("ask_init",info_pkg,room=sid)
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
            logging.info("[{0}][{1}] arrive success".format(data['metadata']['sid'],data['metadata']['thread_id']))
            self.process_result(data['arg'])
        else:
            logging.info("[{0}][{1}] arrive err".format(data['metadata']['sid'],data['metadata']['thread_id']))
            self.handle_error(data['err'],data['arg'])
        self.event('free',sid)
    def handle_error(self,args):
        raise NotImplementedError()
    def process_result(self,err,args):
        raise NotImplementedError()
    def get_task(self):
        raise NotImplementedError()
