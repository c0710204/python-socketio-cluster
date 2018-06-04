class file_obj(object):
    path=""
    ready=False
    def get_path(self):    
        raise NotImplementedError
    def update_ready(self):
        raise NotImplementedError
    def force_ready(self):
        raise NotImplementedError

    