from file_obj import fobj
class file_local(fobj):
    path=""
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
        self.update_ready()
        if self.ready:
            return True
        else:
            raise NotImplementedError

    