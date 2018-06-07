import multiprocessing
import sys
from os.path import splitext, join, isfile, basename
from os import environ
from math import ceil
import subprocess
import logging
import json
import time
from src.libs.app.client import app_client
from src.libs.app.terminfo import terminfo
import time
import tqdm
import uuid
try: 
    from tasks.pre import pre
    from tasks.deeplearning import deeplearning
    from tasks.image_combine import image_combine
except Exception as e:
    print(__file__,e)
    from .tasks.pre import pre
    from .tasks.deeplearning import deeplearning
    from .tasks.image_combine import image_combine

# config
config_p1_folder = '/dev/shm/guxi/p1'
config_p2_folder = '/dev/shm/guxi/p2'
config_p3_folder = '/dev/shm/guxi/p3'

# init remote link
data = {
    "proxy": {
        "host": "star.eecs.oregonstate.edu",
        "username": "guxi",
        "password": "cft6&UJM",
        "port": 22,
    },
}


def ftunnel(*args):
    client = args[-1]
    if type(client) == dict:
        client = namedtuple('Struct', client.keys())(*client.values())
    cmd = "ssh -NR {0}:{1}:{2} {3}@{4} -p {5} >/dev/null".format(
        args[0], args[1], args[2], client.username, client.host, client.port)
    logging.info(cmd)
    ret = subprocess.call(cmd, shell=True)


def scp_download(port, user, host, path):
    
    cmd = "scp -P {0} {1}@{2}:{3} ./ > /dev/null".format(port, user, host, path)
    # print(cmd)
    logging.info(cmd)
    ret = subprocess.call(cmd, shell=True)


def scp_upload(port, user, host, path, file):
    
    cmd = "scp -P {0} ./{4} {1}@{2}:{3}/{4} > /dev/null".format(port, user, host, path, file)
    # print(cmd)
    logging.info(cmd)
    ret = subprocess.call(cmd, shell=True)


mutex_ssh = multiprocessing.Lock()


def sshdownload(data):
    global mutex_ssh
    mutex_ssh.acquire()

    # print("downloading ...".format())
    sys.stdout.flush()
    scp_download(data['ssh']['port'], data['ssh']['username'], data['ssh']['host'],
                 data['input_path'])
    # p.terminate()
    mutex_ssh.release()


def sshupload(data, path):
    import os
    if not os.path.exists(path):
        raise IOError
    global mutex_ssh
    mutex_ssh.acquire()
    # print("uploading {0}...".format(path))
    sys.stdout.flush()
    scp_upload(data['ssh']['port'], data['ssh']['username'], data['ssh']['host'],
               data["output_path"], path)
    # p.terminate()
    mutex_ssh.release()


def task_process(args,pspnet_pre_in,pspnet_dl_in,pspnet_img_combine_in,log,tid):
    # print("got request")
    data = args[0]
    filename, ext = splitext(data['input_path'])
    panid = basename(filename)
    # download file from upper server
    log.put("[{0}]download... {1}".format(tid,panid))
    sys.stdout.flush()
    sshdownload(data)
    args_d = {}
    args_d['panid'] = panid
    args_d['filename'] = filename
    args_d['ext'] = ext

    args_d['model'] = "pspnet50_ade20k"

    args_d['sliding'] = True
    args_d['flip'] = True
    args_d['multi_scale'] = True

    log.put("[{0}]phase 1...".format(tid,panid))
    sys.stdout.flush()
    args_d['input_path'] = "./{0}{1}".format(panid, ext)
    args_d['output_path'] = "{2}/{0}{1}".format(panid, ext, config_p1_folder)

    result_pre=pspnet_pre_in.ask_and_wait(args_d=args_d)
    log.put("[{0}]phase 2...".format(tid,panid))
    sys.stdout.flush()
    # args_d['sess']=sess
    # args_d['model_ok']=pspnet
    args_d['input']=result_pre
    args_d['input_path'] = config_p1_folder + '/'
    args_d['input_path_filter'] = panid
    args_d['output_path'] = config_p2_folder + '/'
    result_dl=pspnet_dl_in.ask_and_wait(args_d)

    log.put("[{0}]phase 3...".format(tid,panid))
    sys.stdout.flush()
    args_d['input']=result_dl
    args_d['input_path'] = "./{0}{1}".format(panid, ext)
    args_d['input_path2'] = "{2}/{0}{1}".format(panid, ext, config_p2_folder)
    args_d['output_path'] = "{2}/{0}{1}".format(panid, ext, config_p3_folder)
    pspnet_img_combine_in.ask_and_wait(args_d)

    log.put("[{0}]upload...".format(tid,panid))
    sys.stdout.flush()
    import numpy as np
    import os
    sshupload(data, "{0}.npy".format(panid))
    l=np.load("{0}_classify.npy".format(panid)).tolist()
    log.put("garbage cleaning")
    os.remove("{0}.npy".format(panid))
    os.remove("{0}_classify.npy".format(panid))
    os.remove("{0}.jpg".format(panid))
    sys.stdout.flush()
    import json
    return {'panid':panid,"percent":json.dumps(l),'id':data['taskid']};

class pspnet_app_client(app_client):
    
    def gui(self):
        import npyscreen
        master_obj=self
        class MainForm(npyscreen.FormMutt):
            MAIN_WIDGET_CLASS = npyscreen.BufferPager
            def while_waiting(self):
                self.wStatus2.value="{0}|{1}|{2}".format(
                        master_obj.tasks[0].uptime(),
                        master_obj.tasks[1].uptime(),
                        master_obj.tasks[2].uptime(), 
                        time.asctime( time.localtime(time.time()) )
                        )
                try:   
                    while True:
                        obj=master_obj.log.get_nowait()
                        self.wMain.buffer([obj,])
                except Exception as e:
                    #raise e
                    pass

                self.display()             
            def afterEditing(self):
                self.parentApp.setNextForm(None)
        class MyTestApp(npyscreen.NPSAppManaged):
            def onStart(self):
                form=MainForm()
                form.keypress_timeout=10
                self.registerForm("MAIN",form ) 
        TA = MyTestApp()
        TA.run()       
    
    def mainthread(self):
        """
        mainthread only
        """    
        print("\npspnet.app.client mainthread start...")
        sys.stdout.flush()
        for task in self.tasks:
            if task.mainthread:
                task.prepare_mainthread()
        print("\npspnet.app.client mainthread started...")
        sys.stdout.flush()
        self.is_ready.release()
        while (1):
            
            t=time.time()
            for task in self.tasks:
                if task.mainthread:
                    task.run()
            t=time.time()-t
            self.GPU_time=t
    thread_count=8    
    COL_MAX=4        
    def prepare(self):
        manager=multiprocessing.Manager()
        
        self.log=manager.Queue()
        self.requestQueue = manager.Queue()
        self.responseQueue = manager.Queue()
        self.log=manager.Queue()
        self.is_ready=multiprocessing.Lock()
        self.is_ready.acquire()
        # local process safe stuff
        self.GPU_time=manager.Value('i',0)
        # start monitor
        
        #init ops
        self.tasks=[pre(),deeplearning(),image_combine()]
        for task in self.tasks:
            task.prepare()
        p=multiprocessing.Process(target=self.mainthread)
        # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
        p.start()

        
        
        
        self.is_ready.acquire()
        print("\nclient ready, booting thread_loop..")
        self.boot_mp()
        self.run_ready.release()

    def boot_mp(self,thread_num=4):
        class appOUT(object):
            def __init__(self,log_queue):
                self.logger=log_queue
            def flush(self):
                pass
            def write(self, s):
                self.logger.put(s)
                #sys.__stdout__.write(s)

        self.p_list=[None for i in range(thread_num)]
        self.p_list_pipe=[None for i in range(thread_num)]
        for i in range(thread_num):
            self.p_list[i]=multiprocessing.Process(target=self.thread_loop ,args=(i, appOUT(self.log)))
            self.p_list[i].start()

    def thread_loop(self,id,stdout=sys.__stdout__):
        print("redirect stdout...")
        sys.stdout=stdout
        print("booting thread - {0}".format(id))
        while True:
            # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
            #assert(multiprocessing.current_process().name=="Process-1")
            if self.requestQueue.empty():
                print("[thread-{0}]waiting for task".format(id))
                time.sleep(1)
                continue
            pkg = self.requestQueue.get()
            args=pkg['args']
            err=None
            ret=None
            try:
                ret=task_process([args],self.tasks[0],self.tasks[1],self.tasks[2],self.log,id)
            except Exception as e:
                err=e
            
            
            self.responseQueue.put({'id':pkg['local_id'],'tensor':ret,'err':err})
            time.sleep(1)
        
    def run(self,args):
        """
        :param args all needed data from server
        """
        local_id = "{0}".format(uuid.uuid4())
        pkg={"args":args,'local_id':local_id}
        
        self.requestQueue.put(pkg)
        p={}
        while (1):
            p = self.responseQueue.get()
            if p['id'] == local_id:
                break
            self.responseQueue.put(p)
        if p['err']:
            raise p['err']
        return p['tensor']


def handler():
    return pspnet_app_client
def main():
    pass
if __name__ == '__main__':
    main()
