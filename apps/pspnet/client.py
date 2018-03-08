import apps.streetdownloader.pkg.streetview as streetview
from src.libs.app.client import app_client

class pspnet_app_client(app_client):
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
    return pspnet_app_client
def main():
    loc_test=pspnet_app_client()
    ret=loc_test.run({"id":-1,"lat":-37.83314,"long": 144.919085})
    print(ret)
if __name__ == '__main__':
    main()
