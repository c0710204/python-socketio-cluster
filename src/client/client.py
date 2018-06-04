from __future__ import absolute_import
import importlib
import time
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
import sys
sys.path.append('.')
from src.libs.network.async_socketIO import async_socketIO
import argparse
import os

from src.libs.conf.conf import conf
def ping(hostname):
    response = os.system("ping -c 1 " + hostname)
    return response == 0

def check_direct_access(service):
    confloader = conf()
    confloader.load("sdn")
    confloader.load("service")
    config = confloader.sdn
    config_s = confloader.service
    #get server from client list base on service
    clitype=[x for x in config['proxy']['service'] if (service in [x2['type'] for x2 in config['proxy']['service'][x]])]
    if len(clitype)<=0:
        #not found
        return {"host":"localhost","port":config_s['services'][service]['port']}
    cli_type=clitype[0]
    target_cli=config['client_type'][cli_type][0]
    target_host=config['client']
    if ping(target_host):
        print("Using direct comm to task server....\n")
        return {"host":target_host,"port":config_s['services'][service]['port']}
    else:
        return {"host":"localhost","port":config_s['services'][service]['port']}
    
    #check server avaliable
    #return
def main():

    parser = argparse.ArgumentParser(description='distrube client')
    parser.add_argument('--app','-app', type=str,help='an integer for the accumulator')
    args=parser.parse_args()
    cli=importlib.import_module("apps.{0}.client".format(args.app))
    cli_handle=cli.handler()
    #try get dns from remote
    
#    h=check_direct_access('app_comm')
#    asio = async_socketIO(SocketIO(h.host,h.port))
    asio = async_socketIO(SocketIO('star.eecs.oregonstate.edu', 30041))
    sio_pspent_info = asio.socketIO.define(cli_handle, '/task')
    print("ready to receive order")
    asio.background()

    while (1):
        time.sleep(1)
    #mutex2.put("success",block=True)
    #except:
    #   pass
if __name__ == "__main__":
    main() 
