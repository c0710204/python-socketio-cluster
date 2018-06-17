from src.libs.app.server import app_server
import time
from time import sleep
import sys
import pymysql
import os
import random
from src.libs.conf.conf import conf
def package(input_path, output_path,id):
  #replacer
    input_path=input_path.replace('/scratch/guxi/googlestreeview_download/temp/DownloadedImages/','/home/ibm/guxi/images/')
    output_path='/home/ibm/guxi/result/'
    return {
        "ssh": {
            "host": "openpower.cgrb.oregonstate.edu",
            "username": "guxi",
            "password": "cft6&UJM",
            "port": 822,
        },
        "input_path": input_path,
        "output_path": output_path,
        "taskid":id
    }


class pspnet_app_server(app_server):




    def __init__(self,*args):
        confloader=conf()
        confloader.load('service')
        print("[{1}]connecting db...".format(0,time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()
        print("starting conn pool")
        self.fetcher_count=1
        self.dbpool=[None for  i in range(self.fetcher_count)]
        for i in range(self.fetcher_count):
            self.dbpool[i]=pymysql.connect(
                port=33061,autocommit=False,host="localhost", 
                user="guxi",passwd="dHtFkI6g",db="gsv_file_list",
                read_timeout=60,write_timeout=60)
        print("[{1}]db connection ok".format(0,time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()
        app_server.__init__(self,*args)
        self.max_task_node=10
    def handle_error(self,err,arg):
        print(err)
    def get_task(self,tid):
        """
        :param args all needed data from server
        """
        import random
        print("[{1}]getting info from db".format(0,time.asctime( time.localtime(time.time()) )))
        sys.stdout.flush()
        random.seed(time.time())
        rnd=random.randint(0,65000000)
        # 16 item each time
        max_pull=16
        sql1='update tasks set status="loaded" , locker="{0}" where status="wait" limit {1}'.format(rnd,max_pull)
        sql2='select tasks.id as id, tasks.pid,path,resultpath from files,tasks where tasks.locker="{0}" and tasks.pid=files.pid  and tasks.`status`="loaded" limit {1}'.format(rnd,max_pull)
        try:
            db=self.dbpool[tid]
            db.ping()
            cursor = db.cursor()
            cursor.execute(sql1);
            #db.commit()
            cursor.execute(sql2);
            db.commit()
            infos = cursor.fetchall()
            ret=[]
            for info in infos:
                img_local=info[2].rstrip()
                cursor.close()
                #db.close()
                print("[{1}]sending request : {0} image".format(info[1],time.asctime( time.localtime(time.time()) )))
                sys.stdout.flush()
                ret.append( package(img_local, info[3],info[0]))
            return ret
        except pymysql.err.OperationalError as e:
            #lose connect
            print(e)
            #db.rollback()
            #db.close()
            return []
        except Exception as e:
            print(e)
            #cursor.close()
            #db.close()
            
            return []

        

    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        success=False
        
        sql1='update tasks set status="done"  where id="{0}"'.format(ret['id'])
        sql2='insert into psplog(`panid`,`phase`,`val`,`max`) values("{0}","3","1","1") '.format(ret['panid'])
        sql3='INSERT INTO result_percent(panid,info)VALUES("{0}","{1}");'.format(
            ret['panid'],
            ret['percent']
        )
        try:
            db=self.dbpool[0]
            db.ping()
            cursor = db.cursor()
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.execute(sql3)
            db.commit()
            cursor.close()
            #db.close()
        except pymysql.err.OperationalError as e:
            
            #lose connect
            db.rollback()
            cursor.close()
            #db.close()
            raise e
                

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
