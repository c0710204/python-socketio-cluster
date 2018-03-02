import apps.streetdownloader.pkg.streetview as streetview
import apps.streetdownloader.client as mdl_cli
import csv
import socketio
class app_server(socketio.Namespace):
    def __init__(self,*args):
        socketio.Namespace.__init__(self,*args)
    def on_connect(self, sid, environ):
        self.emit("ask_init")
    def event(self,noti,sid):
        if noti=='free':
            pkg=self.get_task()
            self.emit('task',pkg)
    def on_free(self,sid,data):
        pass
        #self.event('free',data)
    def on_result(self,sid,data):
        #print(data)
        if data['status']>0:
            self.process_result(data['arg'])
        else:
            self.handle_error(data['err'],data['arg'])
        self.event('free',sid)



class stv_app_server(app_server):
    def __init__(self,*args):
        app_server.__init__(self,*args)
        self.fin=open("Pulseplace_unique_locations.csv",'r+')
        self.fincsv=csv.DictReader(self.fin, delimiter=',')
        self.ferr=open("err.log",'a+')
        self.fout=open("ret.csv",'a+')
        self.processed=0;
        fieldnames = ['id','panoid', 'lat','lon','month','year']
        self.foutcsv=csv.DictWriter(self.fout,fieldnames=fieldnames)
    def handle_error(self,err,arg):
        s="{0},|{1}|\n".format(arg['id'],err)
        print(s)
        self.ferr.write(s)
    def get_task(self):
        """
        :param args all needed data from server
        """
        #read from list
        ret=self.fincsv.next()
        self.processed+=1
        if (self.processed%1000)==0:
            print("processed: {0}".format(self.processed))
        #return request
        return ret
    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        #print(ret)
        for line in ret:
            self.foutcsv.writerow(line)
        return ret
def handler():
    return stv_app_server
def main():
    #dummy
    srv=stv_app_server()

    client = mdl_cli.stv_app_client()
    print(srv.process_result(client.run(srv.get_task())))
if __name__ == '__main__':
    main()
