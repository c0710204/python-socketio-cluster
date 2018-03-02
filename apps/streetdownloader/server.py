import apps.streetdownloader.pkg.streetview as streetview
import apps.streetdownloader.client as mdl_cli
import csv
class app_server():
    def __init__(self):
        pass
    pass
class stv_app_server(app_server):
    def __init__(self):
        app_server.__init__(self)
        self.fin=open("Pulseplace_unique_locations.csv",'r+')
        self.fincsv=csv.reader(self.fin, delimiter=',')
        self.fout=open("ret.csv",'w+')
        self.foutcsv=csv.writer(self.fout)
    def get_task(self):
        """
        :param args all needed data from server
        """
        #read from list
        self.fincsv.read
        #return request
        return {"lat":-37.83314,"long": 144.919085}
    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        self.foutcsv.writerow(ret.values())
        return ret

def main():
    #dummy
    srv=stv_app_server()

    client = mdl_cli.stv_app_client()
    print(srv.process_result(client.run(srv.get_task())))
if __name__ == '__main__':
    main()
