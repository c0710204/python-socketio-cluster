import apps.streetdownloader.pkg.streetview as streetview
import logging
import subprocess

import multiprocessing

from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
class app_client(BaseNamespace):
    def on_ask_init(self,*args):
        self.emit("free", None)
    def on_connect(self, *args):
        self.emit("client_free", None)
        pass
    def on_task(self, *args):
        p = multiprocessing.Process(target=self.run_mp, args=(args[0],))
        p.start()
        return


    def run_mp(self,arg):
        ret={"status":-1,"arg":arg,"err":""}
        try:
            ret={"status":1,"arg":self.run(arg)}
        except Exception as e:
            ret['err']="{0}".format(e)

        self.emit('result',ret)


class stv_app_client(app_client):
    def run(self,args):
        """
        :param args all needed data from server
        """
        panoids = streetview.panoids(lat= args['lat'], lon= args['long'])
        panoids_ret=[]
        for line in panoids:
            line['id']=args['id']
            panoids_ret.append(line)
        return panoids_ret

def handler():
    return stv_app_client
def main():
    loc_test=stv_app_client()
    ret=loc_test.run({"id":-1,"lat":-37.83314,"long": 144.919085})
    print(ret)
if __name__ == '__main__':
    main()
