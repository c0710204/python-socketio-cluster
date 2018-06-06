import uuid
import multiprocessing
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
class task(object):
    """
    mainthread:

        True    : need to maintain the run() in the main thread to provide service
        False   : auto create process to provide service

    handler_type:

        "file"  : using file as status and args transfer tool
        "queue" : build-in queue transfer



    """
    mainthread = False
    handler_type = 'None'
    def __init__(self):
        self.upcount=0
    def uptime(self):
        raise NotImplemented
    def sio_auto(self,sio,a,b):
        if sio is None:
            return
        try:
            sio.emit(a,b)
            #sio.wait(seconds=1)
        except Exception as e:
            print(e)
    def ask_and_wait(self,args_d):
        raise NotImplemented
    def prepare(self):
        """
        using to init before running code
        """
        
        self.mg=multiprocessing.Manager()
        self.remote_uuid = "{0}{1}".format(uuid.uuid4(), "_deeplearning")
        try:
            self.socketIO = SocketIO('star.eecs.oregonstate.edu', 30091, LoggingNamespace,wait_for_connection=False)
        except Exception as e:
            self.socketIO=None
