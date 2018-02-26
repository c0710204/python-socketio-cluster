from multiprocessing import Process, Queue
class async_socketIO():
    def __init__(self,socketIO):
        self.socketIO=socketIO
        self.result=[]
    def emit(self,msg,data):
        self.socketIO.emit(msg,data,self.receiver)
        self.socketIO.wait_for_callbacks(seconds=1)
        while 1:
            if len(self.result)>0:
                return self.result
    def run(self,msg,data):
        self.socketIO.emit(msg,data,self.receiver)
        self.socketIO.wait_for_callbacks(seconds=1)
        while 1:
            if len(self.result)>0:
                return self.result
    def receiver(*args):
        #print(args)
        args[0].result=args[1:]
    def background(self):
        t=Process(target=self.socketIO.wait)
        #t.setDaemon(True)
        t.start()