import client as cli
from collections import defaultdict
import multiprocessing
import socketio
import logging
import time
class app_server(socketio.Namespace):
    #def __del__(self):
    #    for p in self.fetcher:
    #        p.terminate()
    #        p.join()
         
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)

        self.max_task_node=10
        self.tasking=defaultdict(lambda :multiprocessing.Semaphore(self.max_task_node))

        # starting fetching process
        manager=multiprocessing.Manager()
        self.task_queue=manager.Queue(64)
        if not self.fetcher_count:
            self.fetcher_count=4
        #todo: add for
        self.fetcher=[None for i in range(self.fetcher_count)]
        for i in range(self.fetcher_count):
            self.fetcher[i]=multiprocessing.Process(target=self.get_task_queue,args=(self.task_queue,i))
            self.fetcher[i].start()

    def get_task_queue(self,queue_out,id):
        while True:
            if queue_out.full():
                print("queue full")
                time.sleep(1)
                continue
            rets=self.get_task(id)

            for ret in rets:
                queue_out.put(ret)
            time.sleep(1)
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
    def event(self,noti,sid,thread_id=0):
        if noti=='free':
            pkg=self.task_queue.get()
            
            if pkg!=None:
                pkg['metadata']={'sid':sid,'thread_id':thread_id}
                print(sid,thread_id,"acquire")
                self.tasking[sid].acquire()
                self.emit('task',pkg,room=sid)
    def on_client_free(self,sid,data):
        pass
        self.event('free',sid,data['thread_id'])
    def on_result(self,sid,data):
        print(sid,"release")
        self.tasking[sid].release()
        if data['status']>0:
            print("[{0}][{1}] arrive success".format(data['metadata']['sid'],data['metadata']['thread_id']))
            p=multiprocessing.Process(target=self.process_result,args=(data['arg'],))
            p.start()
        else:
            print("[{0}][{1}] arrive err".format(data['metadata']['sid'],data['metadata']['thread_id']))
            self.handle_error(data['err'],data['arg'])
        self.event('free',sid,data['metadata']['thread_id'])
    def handle_error(self,args):
        raise NotImplementedError()
    def process_result(self,err,args):
        raise NotImplementedError()
    def get_task(self):
        raise NotImplementedError()
