from file_obj import fobj

class file_remote(fobj):
    path=""
    local_path=""
    remote_info={}
    ready=False
    def get_path(self):    
        raise NotImplementedError
    def update_ready(self):
        import os
        import sys
        if os.path.exists(self.path):
            self.ready=True
        else:
            self.ready=False
    def force_ready(self):
        import subprocess
        cmd = "scp -P {0} {1}@{2}:{3} {4}".format(
            self.remote_info['port'], 
            self.remote_info['username'], 
            self.remote_info['host'], 
            self.remote_info['path'],
            self.path)
        print(cmd)
        ret = subprocess.call(cmd, shell=True)
        return True
    

    