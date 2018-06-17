import logging
import subprocess
import multiprocessing
import sys

from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
class app_client(BaseNamespace):
    def __init__(self,*args):
        BaseNamespace.__init__(self,*args)
        
        self.run_ready=multiprocessing.Lock()
        self.run_ready.acquire()
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
        self.emit("client_free", None)
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
        try:
            ret={'metadata':arg['metadata'],"status":1,"arg":self.run(arg)}
        except Exception as e:
            ret['err']="{0}".format(sys.exc_info())
            #raise e
        self.emit('result',ret)
    def run(self,args):
        raise NotImplementedError()
