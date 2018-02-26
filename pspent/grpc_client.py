from concurrent import futures
import time
import math
import numpy as np
import grpc
import servers_pb2
import servers_pb2_grpc




#client
grpc.max_receive_message_length=99999999999999999999
channel = grpc.insecure_channel('localhost:50051')
grpc.channel_ready_future(channel).result()
stub = servers_pb2_grpc.pspnet_serverStub(channel)
msg=stub.get_server_memory(servers_pb2.path(url="/example"))
buff=""
for a in msg.array:
  buff+=a
print(buff)
a=np.frombuffer(buff,msg.dtype)
print (msg.shape)
a=a.reshape(list(msg.shape))
print(a)