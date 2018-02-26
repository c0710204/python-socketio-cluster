#!/bin/env python
import subprocess
import lxml.etree
from config import servers
import grpc
#config

def remote_exec(a,cmd,display=False):
    p=subprocess.Popen(['ssh',a['ip'],cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    Tout=""
    Terr=""
    print('********************')
    while 1:
        Lout=p.stdout.readline()
        Lerr=p.stderr.readline()
        if Lout != '':
            if display:
                print(Lout.rstrip())
            Tout+=Lout.rstrip()
            Terr+=Lerr.rstrip()
        else:
            break

    return Tout
def remote_exec_async(a,cmd):
    p=subprocess.Popen(['ssh',a['ip'],cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while p.poll() is None:
        yield p.communicate()
    yield p.communicate()
def remote_stats_cpu(server):
    opt=remote_exec(server,"top -bn1")
    opt_lines=opt.split("\n")
    pos=opt_lines[0].find("load average:")+len("load average:")
    return (map(float,opt_lines[0][pos:].split(',')))
def remote_stats_gpu_mem(server):
    opt=remote_exec(server,'nvidia-smi -q -x')
    GPU_info_xml=lxml.etree.HTML(opt)
    result=GPU_info_xml.xpath('//gpu/utilization/memory_util')
    return [r.text for r in result]
def remote_deploy(server1,server2):
    #mkdir
    print(remote_exec(server2,"mkdir -p {0}".format(server2['path']),display=True))
    #copyfile
    remote_exec(server1,"scp -v -r {0}/* {1}:{2}/".format(server1['path'],server2['ip'],server2['path']),display=True)

            
    
def deploy(server,type,id):
    pass
#load meta data
#run pre-process
#run gpu
#run reduce

#remote_deploy(servers[0],servers[1])
#exit()
#test
while(1):
    for a in servers:
        print("{0} {1} {2}".format(a['ip'],'0',remote_stats_gpu_mem(a)))
