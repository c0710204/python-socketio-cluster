import apps.streetdownloader.pkg.streetview as streetview
import logging
import subprocess
class app_client():
    def scp_download(self,port, user, host, path):
        cmd = "scp -P {0} {1}@{2}:{3} ./".format(port, user, host, path)
        logging.info(cmd)
        ret = subprocess.call(cmd, shell=True)
    def scp_upload(self,port, user, host, path, file):
        cmd = "scp -P {0} ./{4} {1}@{2}:{3} ".format(port, user, host, path, file)
        logging.info(cmd)
        ret = subprocess.call(cmd, shell=True)
    def sshdownload(self,data):
        print("downloading {0}...".format(data['input_path']))
        scp_download(data['ssh']['port'], data['ssh']['username'], "127.0.0.1",
                     data['input_path'])
    def sshupload(self,data, path):
        print("uploading {0}...".format(data['input_path']))
        scp_upload(data['ssh']['port'], data['ssh']['username'], "127.0.0.1",
                   data["output_path"], path)
    def __init__(self):
        pass
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

def main():
    loc_test=stv_app_client()
    ret=loc_test.run({"id":-1,"lat":-37.83314,"long": 144.919085})
    print(ret)
if __name__ == '__main__':
    main()
