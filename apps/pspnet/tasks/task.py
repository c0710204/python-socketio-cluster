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

    def prepare(self):
        """
        using to init before running code
        """
        self.remote_uuid = "{0}{1}".format(uuid.uuid4(), "_deeplearning")
        self.socketIO = SocketIO('localhost', 30001, LoggingNamespace)
