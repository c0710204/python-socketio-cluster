import apps.streetdownloader.pkg.streetview as streetview
import apps.streetdownloader.client as mdl_cli
from src.libs.app.client import app_server


class pspnet_app_server(app_server):
    def __init__(self,*args):
        app_server.__init__(self,*args)
    def handle_error(self,err,arg):
        pass
    def get_task(self):
        """
        :param args all needed data from server
        """
        pass
    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        pass

def handler():
    return pspnet_app_server
def main():
    #dummy
    srv=pspnet_app_server()

    client = mdl_cli.pspnet_app_client()
    print(srv.process_result(client.run(srv.get_task())))
if __name__ == '__main__':
    main()
