from concurrent import futures
import time
import math
import numpy as np
import grpc
import servers_pb2
import servers_pb2_grpc
#server
data_storage={"/example":np.zeros((473,473,1,150))}
data_storage['/example'].tofile("test3")
exit()
def server_handler():
    class servicer(servers_pb2_grpc.pspnet_serverServicer):
        def __init__(self):
            pass

        def get_server_memory(self, request, context):
        # missing associated documentation comment in .proto file
            path=request.url
            print("reading {0}".format(path))
            if path in data_storage:
                arr = servers_pb2.NDArray()
                arr.array.extend(data_storage[path].flatten().astype(int))
                arr.shape.extend(list(data_storage[path].shape))
                arr.dtype = data_storage[path].dtype.name
                print("sending...")
                return arr
            return servers_pb2.NDArray()



    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servers_pb2_grpc.add_pspnet_serverServicer_to_server(servicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
          time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)
server_handler()
#client
