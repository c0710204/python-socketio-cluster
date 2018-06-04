from src.libs.app.server import app_server
import time
from time import sleep
import sys
import pymysql
import os
from src.libs.conf.conf import conf
def package(input_path, output_path,id):
    return {
        "ssh": {
            "host": "star.eecs.oregonstate.edu",
            "username": "guxi",
            "password": "cft6&UJM",
            "port": 22,
        },
        "input_path": input_path,
        "output_path": output_path,
        "taskid":id
    }


class pspnet_app_server(app_server):
    def reconn_db(self):
        confloader=conf()
        confloader.load('service')
        while True:
            try:
                self.db=pymysql.connect(host="127.0.0.1",port=confloader.service['services']['mysql']['port'], user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
                break
            except Exception as e:
                print(e)
                sleep(10)



    def __init__(self,*args):
        confloader=conf()
        confloader.load('service')
        print("[{1}]connecting db...".format(0,time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()
        self.db=pymysql.connect(host="127.0.0.1",port=confloader.service['services']['mysql']['port'], user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
        print("[{1}]db connection ok".format(0,time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()
        app_server.__init__(self,*args)
        self.max_task_node=4
    def handle_error(self,err,arg):
        print(err)
    def get_task(self):
        """
        :param args all needed data from server
        """
        import random
        print("[{1}]getting info from db".format(0,time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()

        rnd=random.randint(0,65000)

        sql1='update tasks set status="loaded" , locker="{0}" where status="wait" limit 1'.format(rnd)
        sql2='select tasks.id as id, tasks.pid,path,resultpath from files,tasks where tasks.locker="{0}" and tasks.pid=files.pid  and tasks.`status`="loaded" limit 1'.format(rnd)
        while True:
            try:
                cursor = self.db.cursor()
                cursor.execute(sql1);
                cursor.execute(sql2);
                self.db.commit()
                info = cursor.fetchone()
                print(info)
                img_local=info[2].rstrip()
                print("[{1}]sending request : {0} image".format(info[1],time.asctime( time.localtime(time.time()) )))
                sys.stdout.flush()
                break
            except pymysql.err.OperationalError as e:
                #lose connect
                print(e)
                self.reconn_db()
            except Exception as e:
                print(e)
                sleep(10)

        return package(img_local, info[3],info[0])

    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        success=False

        sql1='update tasks set status="done"  where id="{0}"'.format(ret['id'])

        while True:
            try:
                cursor = self.db.cursor()
                cursor.execute(sql1)
                self.db.commit()
                break
            except pymysql.err.OperationalError as e:
                #lose connect
                self.reconn_db()


        sql2='INSERT INTO result_percent(panid,info)VALUES("{0}","{1}");'.format(
            ret['panid'],
            ret['percent']
        )
        while True:
            try:
                cursor.execute(sql2)
                self.db.commit()
                break
            except pymysql.err.OperationalError as e:
                #lose connect
                self.reconn_db()
            except Exception as e:
                break

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
