import logging
import subprocess
import multiprocessing
import sys
import uuid
import time
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
class appOUT(object):
        def __init__(self,log_queue=None):
            self.logger=log_queue
        def flush(self):
            pass
        def write(self, s):
            self.logger.put("[syslog][{2}][{1}]{0}".format(s,time.asctime( time.localtime(time.time()) ),multiprocessing.current_process().name))
            #sys.__stdout__.write(s)    
class app_client(BaseNamespace):
    def __init__(self,*args):
        BaseNamespace.__init__(self,*args)
        
        self.run_ready=multiprocessing.Lock()
        self.run_ready.acquire()
        #self init

        
        manager=multiprocessing.Manager()
        self.log=manager.Queue()
        self.log_err=manager.Queue()
        self.requestQueue = manager.Queue()
        self.responseQueue = manager.Queue()
                
        self.prepare()
    def prepare(self):
        """
        run on the start and init all
        """
        self.metadata={}
        self.run_ready.release()
        pass
    def on_ask_init(self,*args):
        info_pack=args[0]
        self.metadata=info_pack
        # print("\n\n\ninfo:\nsid:{0}\nthread:{1}\n\n".format(self.metadata['sid'],self.metadata['thread_id']))
        self.emit("client_free", info_pack)
    def on_connect(self, *args):
        #self.emit("client_free", None)
        pass
    def on_task(self, *args):
        p = multiprocessing.Process(target=self.run_mp, args=(args[0],))
        p.start()
        return
    def run_mp(self,arg):
        #arg['metadata']=self.metadata
        ret={'metadata':arg['metadata'],"status":-1,"arg":arg,"err":""}
        pkg=self.run(arg)
        if pkg['err']:
            raise pkg['err']
            ret['err']="{0}".format(pkg['err'])
        else:
            ret={'metadata':arg['metadata'],"status":1,"arg":pkg['ret']}
        self.emit('result',ret)
        
    def thread_loop(self,id,stdout=sys.__stdout__):
        raise NotImplementedError()

    def boot_mp(self,thread_num=4):
        class appOUT(object):
            def __init__(self,log_queue):
                self.logger=log_queue
            def flush(self):
                pass
            def write(self, s):
                self.logger.put(s)
                #sys.__stdout__.write(s)

        self.p_list=[None for i in range(thread_num)]
        self.p_list_pipe=[None for i in range(thread_num)]
        for i in range(thread_num):
            self.p_list[i]=multiprocessing.Process(target=self.thread_loop ,args=(i, appOUT(self.log), appOUT(self.log_err)),name="Task_thread_{0}".format(i))
            self.p_list[i].start()
        
    def run(self,args):
        """
        :param args all needed data from server
        """
        local_id = "{0}".format(uuid.uuid4())
        pkg={"args":args,'local_id':local_id}
        
        self.requestQueue.put(pkg)
        p={}
        while (1):
            p = self.responseQueue.get()
            if p['id'] == local_id:
                break
            self.responseQueue.put(p)
        return {'ret':p['tensor'],'err':p['err']}
