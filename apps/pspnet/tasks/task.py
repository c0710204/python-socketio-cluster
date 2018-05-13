import uuid
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
class task():
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
    def sio_auto(self,sio,a,b):
        if sio is None:
            return
        try:
            sio.emit(a,b)
            #sio.wait(seconds=1)
        except Exception as e:
            print(e)
    def prepare(self):
        """
        using to init before running code
        """
        self.remote_uuid = "{0}{1}".format(uuid.uuid4(), "_deeplearning")
        try:
            self.socketIO = SocketIO('localhost', 30091, LoggingNamespace)
        except Exception as e:
            self.socketIO=None
