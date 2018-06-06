import logging
import subprocess
import multiprocessing
import sys

from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
class manager_client(BaseNamespace):
    def __init__(self,*args):
        BaseNamespace.__init__(self,*args)
        self.thread_list
    def prepare(self):
        """
        run on the start and init all
        """
        self.metadata={}
        self.run_ready.release()
        pass
    def on_ask_init(self,*args):
        info_pack=args[0]
        self.manager=multiprocessing.Manager()
        self.log=self.manager.Queue()
        self.metadata=info_pack
        self.asio_list=[]
        # start processes
        for i in range(self.metadata['max_thread']):
            asio = async_socketIO(SocketIO(self.metadata['host'], self.metadata['port']))
            sio_pspent_info = asio.socketIO.define(cli_handle, self.metadata['path'])
            asio.handler(self.metadata['path']).thread_id=i
            asio.handler(self.metadata['path']).log=self.log
            asio.handler(self.metadata['path']).prepare()
            print("ready to receive order")
            asio.background()
            self.asio_list.append(asio)
    