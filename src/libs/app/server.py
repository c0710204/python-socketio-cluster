import src.libs.app.client as cli
import multiprocessing
import socketio
class app_server(socketio.Namespace):
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)
        self.max_task_node=100
    def on_connect(self, sid, environ):
        for i in range(self.max_task_node):
            self.emit("ask_init",room=sid)
    def event(self,noti,sid):
        if noti=='free':
            pkg=self.get_task()
            if pkg!=None:
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
        self.event('free',sid)
