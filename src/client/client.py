import importlib
import time
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from src.libs.network.async_socketIO import async_socketIO
import argparse
def main():

    parser = argparse.ArgumentParser(description='distrube client')
    parser.add_argument('--app','-app', type=str,help='an integer for the accumulator')
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
