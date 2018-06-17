import multiprocessing
import sys
from os.path import splitext, join, isfile, basename
from os import environ
from math import ceil
import subprocess
import logging
import json
import time
from src.libs.app.client import app_client,appOUT
from src.libs.app.terminfo import terminfo
import time
import tqdm
import uuid
import os
from collections import deque
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
        class ac_cmd(npyscreen.ActionControllerSimple):
            def create(self):
                self.add_action('^reboot mp', self.rebooter_mp, False)
                self.add_action('^reboot task', self.rebooter, False)
                self.add_action('^mode', self.c_mode, False)
            def c_mode(self, command_line, widget_proxy, live):
                self.parent.mode=1-self.parent.mode
                self.parent.while_waiting()
            def rebooter(self, command_line, widget_proxy, live):
                sys.stdout=appOUT(master_obj.log)        
                sys.stderr=appOUT(master_obj.log_err)              
                print("REBOOTING tasks.....")
                #killall tasks
                if master_obj.p_list:
                    for p in master_obj.p_list:
                        p.terminate()
                        p.join()
                #restart them
                master_obj.boot_mp(10)
                sys.stdout=sys.__stdout__
                sys.stderr=sys.__stderr__
                pass
            def rebooter_mp(self, command_line, widget_proxy, live):
                sys.stdout=appOUT(master_obj.log)         
                sys.stderr=appOUT(master_obj.log_err)                
                print("REBOOTING tasks.....")                
                pass
                

            def set_search(self, command_line, widget_proxy, live):
                self.parent.value.set_filter(command_line[1:])
                self.parent.wMain.values = self.parent.value.get()
                self.parent.wMain.display()

        class MainForm(npyscreen.FormMuttActiveWithMenus):
            COMMAND_WIDGET_CLASS = npyscreen.TextCommandBox
            MAIN_WIDGET_CLASS = npyscreen.BufferPager   
            ACTION_CONTROLLER = ac_cmd    
            def while_waiting(self):
                # if master_obj.p_mainthread:
                #     maint_status=master_obj.p_mainthread.is_alive()
                # else:
                #     maint_status="Wait for Start"
                self.wStatus2.value="[mode {8}] Server Time: {3}   Tasks in model: Pre:{0}({5:.3})| Deep Learning:{1}({6:.3}) | Image Combine:{2}({7:.3})            Main-thread: {4}".format(
                        master_obj.tasks[0].uptime(),
                        master_obj.tasks[1].uptime(),
                        master_obj.tasks[2].uptime(), 
                        time.asctime( time.localtime(time.time()) ),
                        master_obj.GPU_time.value,
                        master_obj.tasks[0].avgtime(),
                        master_obj.tasks[1].avgtime(),
                        master_obj.tasks[2].avgtime(),
                        self.mode                         
                        )
                for i in range(len(self.log_source)):
                    try:
                        self.wMain.values=self.buff[i]
                        while True:
                            obj=self.log_source[i].get_nowait()
                            #self.wMain.values.popleft()
                            self.wMain.buffer([obj,],scroll_if_editing =True)
                    except Exception as e:
                        #raise e
                        pass
                self.wMain.values=self.buff[self.mode]
                self.display()             
            def afterEditing(self):
                self.parentApp.setNextForm(None)
        class MyTestApp(npyscreen.NPSAppManaged):
            def onStart(self):
                form=MainForm()
                form.mode=0
                form.buff=[deque([],2048),deque([],2048)]
                form.log_source=[master_obj.log,master_obj.log_err]
                form.keypress_timeout=10
                self.registerForm("MAIN",form ) 
        TA = MyTestApp()
        TA.run()      
    def mainthread(self):
        """
        mainthread only
        """    
 
        
        sys.stdout=appOUT(self.log)        
        sys.stderr=appOUT(self.log_err)
        #fetch info from process name
        info_pkg=multiprocessing.current_process().name.split('_')
        GPU_ID=int(info_pkg[1])
        Local_ID=int(info_pkg[2])

        os.environ['CUDA_VISIBLE_DEVICES']="{0}".format(GPU_ID)


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
            self.GPU_time.value =t/self.p_mainthread_count
    thread_count=8    
    COL_MAX=4        
    def prepare(self):
        self.p_list=None
        self.p_mainthread_count=2
        self.p_mainthread_gpu_count=2
        self.is_ready=multiprocessing.Semaphore(self.p_mainthread_count*self.p_mainthread_gpu_count)
        manager=multiprocessing.Manager()
        for i in range(self.p_mainthread_count*self.p_mainthread_gpu_count):
            self.is_ready.acquire()
        # local process safe stuff
        self.GPU_time=manager.Value('i',0)
        # start monitor
        
        #init ops
        self.tasks=[pre(),deeplearning(),image_combine()]
        for task in self.tasks:
            task.prepare()
        
        self.p_mainthread=[None for i in range(self.p_mainthread_count*self.p_mainthread_gpu_count)]
        for i_gpu in range(self.p_mainthread_gpu_count):
            for i in range(self.p_mainthread_count):
                self.p_mainthread[i]=multiprocessing.Process(target=self.mainthread,name="Mainthread_{0}_{1}".format(i_gpu,i))
                # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
                self.p_mainthread[i].start()

        
        
        
        self.is_ready.acquire()
        print("\nclient ready, booting pthread_loop..")
        self.boot_mp(10)
        self.run_ready.release()


    def thread_loop(self,id,stdout=sys.__stdout__,stderr=sys.__stderr__):
        
        sys.stdout=stdout
        sys.stderr=stderr
        print("redirect stdout...")
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

def handler():
    return pspnet_app_client
def main():
    pass
if __name__ == '__main__':
    main()
