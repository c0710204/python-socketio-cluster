import apps.streetdownloader.client as cli
import importlib
import time
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from src.libs.network.async_socketIO import async_socketIO

def main():

    parser = argparse.ArgumentParser(description='distrube client')
    parser.add_argument('client','c', type=str,help='an integer for the accumulator')
    args=parser.parse_args()
    cli=importlib.import_module("app.{0}.client".format(args.client))
    cli_handle=cli.handler()
    asio = async_socketIO(SocketIO('localhost', 30021))
    sio_pspent_info = asio.socketIO.define(cli_handle, '/task')
    asio.background()
    while (1):
        time.sleep(1)
    #mutex2.put("success",block=True)
    #except:
    #   pass
if __name__ == "__main__":
    main()
