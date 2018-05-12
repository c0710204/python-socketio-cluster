'''
work: register self to remote so remote can auto set SDN
'''
import importlib
import time
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from src.libs.network.async_socketIO import async_socketIO
import argparse
def main():

    parser = argparse.ArgumentParser(description='distrube client')
    parser.add_argument('--server','-s', type=str,help='manage server')
    args=parser.parse_args()
    cli=importlib.import_module("apps.{0}.client".format(args.app))
    cli_handle=cli.handler()
    asio = async_socketIO(SocketIO('localhost', 30041))
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
