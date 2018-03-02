import apps.streetdownloader.client as cli
import time
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from pspnet.async_socketIO import async_socketIO
cli_handle=cli.handler()
def main():


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
