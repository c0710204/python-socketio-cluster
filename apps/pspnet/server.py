from src.libs.app.server import app_server
import time
import sys
import pymysql
import os
from src.libs.conf.conf import conf
def package(input_path, output_pathg,id):
    return {
        "ssh": {
            "host": "127.0.0.1",
            "username": "guxi",
            "password": "cft6&UJM",
            "port": 50022,
        },
        "input_path": input_path,
        "output_path": output_path,
        "taskid":id
    }


class pspnet_app_server(app_server):
    def __init__(self,*args):
        confloader=conf()
        confloader.load('service')
        self.db=pymysql.connect(host="127.0.0.1",port=confloader.service['services']['mysql']['port'], user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
        app_server.__init__(self,*args)
        self.max_task_node=2
    def handle_error(self,err,arg):
        print(err)
    def get_task(self):
        """
        :param args all needed data from server
        """
        cursor = self.db.cursor()
        rnd=os.getpid()
        print("[{1}]getting info from db".format(info['pid'],time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()
        sql1='update tasks set status="loaded" , locker="{0}" where status="wait" limit 1'.format(rnd)
        sql2='select tasks.id as id pid,path,resultpath from files,tasks where tasks.loader="{0}" tasks.pid=files.pid  and tasks.status="loaded" limit 1'.format(rnd)
        cursor.execute(sql1);
        cursor.execute(sql2);
        self.db.commit()
        try:
            info = cursor.fetchone()
            img_local=info['path']
            print("[{1}]sending request : {0} image".format(info['pid'],time.asctime( time.localtime(time.time()) )))
            sys.stdout.flush()
        except Exception as e:
            print(e)
            return None
        return package(img_local, info['resultpath'],info['id'])

    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        cursor = self.db.cursor()
        sql1='update tasks set status="done"  where id="{0}"'.format(ret['id'])
        cursor.execute(sql1)
        self.db.commit()
        sql2='INSERT INTO result_percent(panid,info)VALUES("{0}","{1}");'.format(
            ret['panid'],
            ret['info']
        )
        cursor.execute(sql2)
        self.db.commit()
        pass

def handler():
    return pspnet_app_server
def main():
    #dummy
    pass
    #srv=pspnet_app_server()

    #client = mdl_cli.pspnet_app_client()
    #print(srv.process_result(client.run(srv.get_task())))
if __name__ == '__main__':
    main()
